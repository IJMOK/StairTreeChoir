"""Build a test video of the trees singing and push it to YouTube Live, to see what Content ID flags.

    python -m tools.stream_test build                      # previews/stream-test.mp4 (Rockin', O Come, Auld Lang Syne)
    python -m tools.stream_test build rockin-around --seconds 20
    python -m tools.stream_test stream                     # push the built file in real time

The webcam plan (docs/webcam.md) needs to know which recordings YouTube matches before we rely on
the auto-mute list. Video is the rendered .fseq drawn as preview_render does it, so the test looks
like the real stream; the audio is the song's MP3 from the arrangement. The stream key comes from the
YT_STREAM_KEY environment variable (a user variable on Windows), never from git. Use an unlisted
broadcast. Needs PyAV, Pillow and zstandard.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image

from tools.arrange_song import SHOW_FOLDER
from tools.check_render import read_fseq
from tools.preview_render import BG, OUT_DIR, draw_frame, load_layout
from tools.tree_layout import ROOT

DEFAULT_SONGS = ["rockin-around", "o-come-all-ye-faithful", "auld-lang-syne"]  # high risk, carol, low risk
OUT = OUT_DIR / "stream-test.mp4"
W, H, FPS = 1280, 720, 20
GOP = 2 * FPS                  # YouTube wants a keyframe at least every 4 s
RATE = 44100
RTMP = "rtmp://a.rtmp.youtube.com/live2/"


def _stream_key() -> str | None:
    key = os.environ.get("YT_STREAM_KEY")
    if not key and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = winreg.QueryValueEx(k, "YT_STREAM_KEY")[0]
        except OSError:
            pass
    return key


def _fit(img: Image.Image) -> Image.Image:
    """Letterbox a preview frame into the W x H video frame."""
    s = min(W / img.width, H / img.height)
    img = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    out = Image.new("RGB", (W, H), BG)
    out.paste(img, ((W - img.width) // 2, (H - img.height) // 2))
    return out


def _audio_frames(mp3: Path, seconds: float | None):
    """The song's audio as 44.1 kHz stereo frames for the AAC encoder."""
    rs = av.AudioResampler(format="fltp", layout="stereo", rate=RATE, frame_size=1024)
    done = 0
    with av.open(str(mp3)) as src:
        for frame in src.decode(audio=0):
            for f in rs.resample(frame):
                if seconds is not None and done >= seconds * RATE:
                    return
                done += f.samples
                yield f
    yield from rs.resample(None)


def build(songs: list[str], out: Path, seconds: float | None = None) -> Path:
    """Render each song's trees and audio back to back into one interleaved MP4."""
    nodes, poly, bw, bh = load_layout()
    out.parent.mkdir(exist_ok=True)
    with av.open(str(out), "w") as dst:
        vs = dst.add_stream("libx264", rate=FPS)
        vs.width, vs.height, vs.pix_fmt = W, H, "yuv420p"
        vs.bit_rate = 2_500_000
        vs.options = {"preset": "veryfast", "g": str(GOP), "keyint_min": str(GOP), "sc_threshold": "0"}
        as_ = dst.add_stream("aac", rate=RATE)
        as_.layout, as_.bit_rate = "stereo", 128_000

        vpts = apts = 0                      # running totals in frames / samples across songs
        for name in songs:
            arr = json.loads((ROOT / "data" / "songs" / f"{name}.json").read_text(encoding="utf-8"))
            raw, channels, frames, step = read_fseq(SHOW_FOLDER / f"{arr['sequence']}.fseq")
            mp3 = SHOW_FOLDER / arr["audio"]
            length = frames * step / 1000 if seconds is None else min(seconds, frames * step / 1000)
            label = f"Stair Tree Choir - stream test - {arr['sequence']}"
            song_v0, song_a0 = vpts, apts
            audio = _audio_frames(mp3, length)
            for k in range(int(length * FPS)):
                f = min(int(k * 1000 / FPS / step), frames - 1)
                vf = av.VideoFrame.from_image(_fit(draw_frame(raw, channels, f, nodes, poly, bw, bh, label)))
                vf.pts, vf.time_base = vpts, Fraction(1, FPS)
                vpts += 1
                dst.mux(vs.encode(vf))
                # keep audio level with video so the file streams in order
                while (apts - song_a0) / RATE < (vpts - song_v0) / FPS:
                    af = next(audio, None)
                    if af is None:
                        break
                    af.pts, af.time_base = apts, Fraction(1, RATE)
                    apts += af.samples
                    dst.mux(as_.encode(af))
            for af in audio:                 # any audio left past the last frame
                af.pts, af.time_base = apts, Fraction(1, RATE)
                apts += af.samples
                dst.mux(as_.encode(af))
            # the next song starts on a common clock, after whichever stream ran longer
            apts = max(apts, vpts * RATE // FPS)
            vpts = -(-apts * FPS // RATE)
            print(f"  {arr['sequence']}: {length:.0f} s")
        dst.mux(vs.encode(None))
        dst.mux(as_.encode(None))
    print(f"wrote {out}")
    return out


def stream(src: Path, url: str) -> None:
    """Send the built file to an RTMP server at real-time pace (YouTube drops a stream sent faster)."""
    with av.open(str(src)) as inp, av.open(url, "w", format="flv") as dst:
        mapping = {s.index: dst.add_stream_from_template(s) for s in inp.streams}
        t0 = time.monotonic()
        for pkt in inp.demux():
            if pkt.dts is None:
                continue
            wait = float(pkt.dts * pkt.time_base) - (time.monotonic() - t0)
            if wait > 0:
                time.sleep(wait)
            pkt.stream = mapping[pkt.stream.index]
            dst.mux(pkt)
    print(f"streamed {src.name}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="render the test video")
    b.add_argument("songs", nargs="*", default=DEFAULT_SONGS, help="data/songs/<name>.json names")
    b.add_argument("--seconds", type=float, help="only the first N seconds of each song")
    b.add_argument("--out", type=Path, default=OUT)
    s = sub.add_parser("stream", help="push the built video to YouTube Live")
    s.add_argument("--file", type=Path, default=OUT)
    s.add_argument("--url", help="full RTMP URL instead of YouTube + YT_STREAM_KEY")
    args = ap.parse_args(argv)

    if args.cmd == "build":
        build(args.songs, args.out, args.seconds)
    else:
        url = args.url
        if not url:
            key = _stream_key()
            if not key:
                raise SystemExit("set YT_STREAM_KEY (YouTube Studio > Go live > Stream > Stream key)")
            url = RTMP + key
        stream(args.file, url)


if __name__ == "__main__":
    main()
