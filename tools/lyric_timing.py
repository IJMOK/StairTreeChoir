"""Word-level lyric timing for xLights, from the song audio and its lyrics, using Whisper on the PC.

    python -m tools.lyric_timing "C:/Users/User/Documents/xLights/Audio/song.mp3" \
        --artist "Brenda Lee" --title "Rockin' Around the Christmas Tree"

Writes <track>.json next to the audio (default track name "Choir"). In xLights:
File → Import → Import Timing Track, file type "Eleven Labs (*.json)". It becomes a
timing track named after the file with a phrase layer (one lyric line each) and a
word layer; right-click the track → Breakdown Words to add the phonemes.

The JSON shape is what xLights' ElevenLabs importer reads (SequenceFile::
ProcessElevenLabsTimingFiles in src-core/import_export/TimingImport.cpp, xLights
75c3e11): {"segments": [{"text", "start_time", "end_time", "words": [{"text",
"start_time", "end_time"}]}]}, times in seconds.

Lyrics come from LRCLIB (lrclib.net) unless --lyrics is given, and are saved as
<audio>.lyrics.txt, one sung line per line. Fix that file and run again: an
existing .lyrics.txt is used instead of downloading. Lyrics stay in the show
folder, never in git.

stable-ts aligns the known text to the audio (forced alignment), which is far more
reliable on singing than transcribing. Run it on the vocal stem if the mix is busy.
Needs requirements-lyrics.txt (CPU PyTorch, stable-ts, PyAV).
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

XLIGHTS_DICTIONARIES = Path(r"C:\Program Files\xLights\dictionaries")
USER_AGENT = "StairTreeChoir lyric_timing (github.com/IJMOK/StairTreeChoir)"
SAMPLE_RATE = 16000
# Characters xLights strips before a dictionary lookup (PhonemeDictionary::BreakdownWord).
XL_STRIP = set("/#~@$%^*,!&-_+=[]{}\":;.<>?`")


def load_audio(path: Path):
    """Decode any audio file to mono 16kHz float32, as Whisper expects."""
    import av
    import numpy as np

    chunks = []
    with av.open(str(path)) as container:
        resampler = av.AudioResampler(format="flt", layout="mono", rate=SAMPLE_RATE)
        for frame in container.decode(audio=0):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
        for out in resampler.resample(None):
            chunks.append(out.to_ndarray().reshape(-1))
    return np.concatenate(chunks).astype("float32")


def lyric_lines(text: str) -> list[str]:
    """Sung lines: LRC timestamps, section tags like [Chorus] and blank lines removed."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\[[^\]]*\]", "", line).strip()
        if line:
            lines.append(line)
    return lines


def fetch_lyrics(artist: str, title: str, duration: float) -> str:
    """Plain lyrics from LRCLIB; picks the result whose length is closest to the audio."""
    query = urllib.parse.urlencode({"artist_name": artist, "track_name": title})
    req = urllib.request.Request(f"https://lrclib.net/api/search?{query}",
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        results = json.load(resp)
    results = [r for r in results if r.get("plainLyrics") or r.get("syncedLyrics")]
    if not results:
        raise SystemExit(f"LRCLIB has no lyrics for {artist} - {title}; pass --lyrics.")
    best = min(results, key=lambda r: abs((r.get("duration") or 0) - duration))
    print(f"LRCLIB: {best.get('artistName')} - {best.get('trackName')} "
          f"({best.get('duration')}s; audio {duration:.0f}s)")
    return best.get("plainLyrics") or best["syncedLyrics"]


def xlights_word_key(word: str) -> str:
    return "".join(c for c in word if c not in XL_STRIP).upper()


def dictionary_words(search_dirs: list[Path]) -> set[str]:
    """Words xLights can break down. Like xLights (xLightsFrame::LoadPhonemeDictionaries),
    each dictionary file is taken from the first directory that has it, show folder first."""
    words = set()
    for name in ("standard_dictionary", "extended_dictionary", "user_dictionary"):
        path = next((d / name for d in search_dirs if (d / name).exists()), None)
        if path is None:
            continue
        for line in path.read_text(encoding="latin-1").splitlines():
            line = line.strip()
            if line and not line.startswith(("##", ";;")) and len(line.split()) > 1:
                words.add(line.split()[0])
    return words


def to_xlights(result) -> dict:
    """stable-ts WhisperResult -> xLights ElevenLabs-import JSON."""
    segments = []
    for seg in result.segments:
        words = [{"text": w.word.strip(), "start_time": round(w.start, 3), "end_time": round(w.end, 3)}
                 for w in seg.words if w.word.strip()]
        if not words:
            continue
        segments.append({"text": seg.text.strip(), "start_time": round(seg.start, 3),
                         "end_time": round(seg.end, 3), "words": words})
    return {"segments": segments}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audio", type=Path)
    ap.add_argument("--artist", help="for the LRCLIB lyrics search")
    ap.add_argument("--title", help="for the LRCLIB lyrics search")
    ap.add_argument("--lyrics", type=Path, help="lyrics text file, one sung line per line")
    ap.add_argument("--track", default="Choir", help="timing track name (the output file's name)")
    ap.add_argument("--model", default="medium.en", help="Whisper model (small.en is faster)")
    args = ap.parse_args(argv)

    audio = load_audio(args.audio)
    duration = len(audio) / SAMPLE_RATE
    saved = args.audio.with_suffix(".lyrics.txt")
    if args.lyrics:
        text = args.lyrics.read_text(encoding="utf-8-sig")
    elif saved.exists():
        print(f"Using {saved}")
        text = saved.read_text(encoding="utf-8-sig")
    else:
        if not (args.artist and args.title):
            raise SystemExit("Give --artist and --title (or --lyrics).")
        text = fetch_lyrics(args.artist, args.title, duration)
    lines = lyric_lines(text)
    saved.write_text("\n".join(lines) + "\n", encoding="utf-8")

    show_folder = args.audio.parent.parent if args.audio.parent.name.lower() == "audio" else args.audio.parent
    known = dictionary_words([show_folder, XLIGHTS_DICTIONARIES])
    unknown = sorted({xlights_word_key(w) for line in lines for w in line.split()} - known - {""})
    if known and unknown:
        print("Not in xLights' dictionaries (add them to user_dictionary in the show folder):",
              ", ".join(unknown))

    import stable_whisper

    print(f"Aligning {len(lines)} lines to {duration:.0f}s of audio with {args.model} on the CPU...")
    model = stable_whisper.load_model(args.model, device="cpu")
    result = model.align(audio, "\n".join(lines), language="en", original_split=True)
    if result is None:
        raise SystemExit("Alignment failed. Try the vocal stem, or check the lyrics match the recording.")

    out = args.audio.with_name(f"{args.track}.json")
    data = to_xlights(result)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    n_words = sum(len(s["words"]) for s in data["segments"])
    print(f"Wrote {out}: {len(data['segments'])} phrases, {n_words} words")


if __name__ == "__main__":
    main()
