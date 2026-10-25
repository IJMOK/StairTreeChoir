"""Check a rendered sequence against its arrangement: python -m tools.check_render data/songs/<song>.json

Reads the sequence's .fseq (FSEQ v2, zstd or uncompressed) from the show folder and,
for every lyric line, lists which trees sing during it (mouth changes shape, or
shows anything but the closed-lip rest). Those must
be exactly the trees the arrangement gives the line (less a sleeping tree on a shared
line). While a tree is "asleep" its eyes must be shut: the upper half of each eye dark (except
where a loop's move opens them). Silent loops (tools/loops.py) get their own check: check_moves.
Also reports each tree's mouth shape counts. Needs zstandard (requirements-lyrics.txt).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

from tools.arrange_song import SHOW_FOLDER, TREES, asleep_spans, sings_line
from tools.tree_layout import LAYOUT_FILE, ROOT

TREE_CHANNELS = 276
MOUTH = ("mouth_wide", "mouth_small", "lip")
REST = (0, 0, 1)  # lip line only


def read_fseq(path: Path) -> tuple[bytes, int, int, int]:
    """(frame data, channels per frame, frame count, step ms)."""
    b = path.read_bytes()
    if b[:4] != b"PSEQ" or b[7] != 2:
        raise SystemExit(f"{path} is not an FSEQ v2 file")
    data_off = struct.unpack_from("<H", b, 4)[0]
    channels, frames = struct.unpack_from("<II", b, 10)
    step, compression = b[18], b[20] & 0x0F
    blocks = b[21] | ((b[20] >> 4) << 8)
    if compression == 0:
        return b[data_off:data_off + channels * frames], channels, frames, step
    if compression != 1:
        raise SystemExit("only zstd or uncompressed FSEQ is supported")
    import zstandard

    out, pos, d = bytearray(), data_off, zstandard.ZstdDecompressor()
    for i in range(blocks):
        _, size = struct.unpack_from("<II", b, 32 + 8 * i)
        if size:
            out += d.decompress(b[pos:pos + size], max_output_size=channels * frames)
            pos += size
    return bytes(out), channels, frames, step


DARK_LIMIT_S = 2.0      # longest an outline may stay fully dark in a loop, unless the arrangement turns it off


def check_moves(arr: dict, raw: bytes, channels: int, frames: int, step: int, groups: dict, shape) -> list:
    """Silent loops: a mouth leaves the rest shape only inside a move's mouth span (one frame of
    slack) or goes dark with its tree, and no tree's outline stays dark longer than DARK_LIMIT_S
    except where it's meant to (tree_end, an "off" outline move)."""
    from tools.arrange_song import expand_moves
    song_ms = frames * step
    mouth = {t: [] for t in TREES}
    off = {t: [] for t in TREES}
    for t, a, b, mv in expand_moves(arr, song_ms):
        if "mouth" in mv:
            mouth[t].append((a - step, b + step))
        if mv.get("outline") == "off":
            off[t].append((a, b))
    for k, v in arr.get("tree_end", {}).items():
        off[int(k)].append((int(v * 1000) - int(arr.get("end_fade", 0) * 1000) - step, song_ms))
    out = []
    for t in TREES:
        stray = [f for f in range(frames) if shape(f, t) != REST and not any(a <= f * step < b for a, b in mouth[t])
                 and not (shape(f, t) == (0, 0, 0) and any(a <= f * step < b for a, b in off[t]))]   # gone dark on purpose
        dark, run, worst = 0, 0, 0
        for f in range(frames):
            base = f * channels + (t - 1) * TREE_CHANNELS
            lit = any(raw[base + (k - 1) * 3: base + k * 3] != b"\0\0\0" for k in groups["outline"])
            meant = any(a <= f * step < b for a, b in off[t])
            run = 0 if lit or meant else run + 1
            worst = max(worst, run)
            dark += 0 if lit else 1
        print(f"StairTree{t}: mouth open outside its moves in {len(stray)} frames; "
              f"outline dark in {dark} frames, longest unplanned {worst * step / 1000:.1f}s")
        if stray:
            out.append((f"tree {t}", f"mouth open at {stray[0] * step / 1000:.2f}s", "rest"))
        if worst * step / 1000 > DARK_LIMIT_S:
            out.append((f"tree {t}", f"outline dark for {worst * step / 1000:.1f}s", "lit"))
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arrangement", type=Path)
    args = ap.parse_args(argv)
    arr = json.loads((ROOT / args.arrangement).read_text(encoding="utf-8"))
    raw, channels, frames, step = read_fseq(SHOW_FOLDER / f"{arr['sequence']}.fseq")
    timing = json.loads((SHOW_FOLDER / arr["lyrics_timing"]).read_text(encoding="utf-8"))
    groups: dict[str, list[int]] = {}
    for n in json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))["nodes"]:
        groups.setdefault(n["group"], []).append(n["n"])

    def shape(frame: int, tree: int) -> tuple[int, ...]:
        base = frame * channels + (tree - 1) * TREE_CHANNELS
        return tuple(int(any(raw[base + (k - 1) * 3:base + k * 3] != b"\0\0\0" for k in groups[g]))
                     for g in MOUTH)

    bad = []
    for i, seg in enumerate(timing["segments"], 1):
        # Inside the line only: one frame of slack at each end for snapping to frames.
        f0, f1 = int(seg["start_time"] * 1000 / step) + 1, int(seg["end_time"] * 1000 / step) - 1
        if arr.get("end_at") is not None:   # after end_at everything is dark by design (a closer)
            f1 = min(f1, int(arr["end_at"] * 1000 / step) - 1)
        # Singing: the mouth changes, or shows anything but the closed-lip rest
        # (a short line can hold one open shape).
        shapes = {t: {shape(f, t) for f in range(f0, min(f1, frames))} for t in TREES}
        moving = [t for t in TREES if len(shapes[t]) > 1 or shapes[t] - {REST}]
        group = arr["groups"][arr["lines"][str(i)]]
        want = [t for t in group if sings_line(arr, t, group, seg["start_time"])]
        if moving != want:
            bad.append((i, moving, want))
    # Shut eyes: the eye hexagons' upper nodes (top, upper-right, upper-left) stay dark.
    upper = [first + o for first in (groups["eye_right"][0], groups["eye_left"][0]) for o in (0, 1, 5)]
    from tools.arrange_song import expand_moves
    peeks = {t: [] for t in TREES}      # a loop's sleeper may open an eye on purpose (an eye move)
    for t, a, b, mv in expand_moves(arr, frames * step):
        if "eyes" in mv and mv["eyes"] != "closed":
            peeks[t].append((a - step, b + step))
    for t, spans in asleep_spans(arr, frames * step).items():
        for a, b in spans:
            lit = sum(any(raw[f * channels + (t - 1) * TREE_CHANNELS + (k - 1) * 3:
                              f * channels + (t - 1) * TREE_CHANNELS + k * 3] != b"\0\0\0" for k in upper)
                      for f in range(a // step + 1, min(b // step - 1, frames))
                      if not any(p0 <= f * step < p1 for p0, p1 in peeks[t]))
            print(f"StairTree{t} asleep {a / 1000:.1f}-{b / 1000:.1f}s: eyes open in {lit} frames")
            if lit:
                bad.append((f"asleep {t}", "eyes open", "shut"))
    if arr.get("moves") is not None and not arr["lines"]:     # a silent loop (tools/loops.py)
        bad += check_moves(arr, raw, channels, frames, step, groups, shape)
    for t in TREES:
        counts = Counter(shape(f, t) for f in range(frames))
        print(f"StairTree{t} (wide, small, lip) frames: {dict(sorted(counts.items()))}")
    for i, moving, want in bad:
        print(f"line {i}: mouths moving on {moving}, arranged for {want}")
    print(f"{len(timing['segments']) - len(bad)}/{len(timing['segments'])} lines match the arrangement")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
