"""Draw a rendered sequence as the six trees would show it: an animated GIF or a contact sheet.

    python -m tools.preview_render data/songs/rockin-around.json --start 30 --end 40
    python -m tools.preview_render data/songs/rockin-around.json --sheet 0:120:4

Reads the .fseq from the show folder (as check_render does) and places every pixel at its
node position from data/tree-layout.json, six trees side by side as in the sequence slots.
Output goes to previews/ (not committed). Needs Pillow and zstandard.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tools.arrange_song import SHOW_FOLDER, TREES
from tools.check_render import TREE_CHANNELS, read_fseq
from tools.tree_layout import LAYOUT_FILE, ROOT

OUT_DIR = ROOT / "previews"
SCALE = 0.25           # px per mm
GAP = 30               # px between trees
DOT = 4                # pixel radius in px
BG, WOOD = (8, 8, 14), (40, 30, 22)


def load_layout() -> tuple[list[dict], list[tuple[float, float]], float, float]:
    layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    blank = layout["blank"]
    return layout["nodes"], [tuple(p) for p in blank["polygon"]], blank["width"], blank["height"]


def draw_frame(raw: bytes, channels: int, frame: int, nodes, poly, bw, bh, label: str = "") -> Image.Image:
    tw, th = int(bw * SCALE), int(bh * SCALE)
    img = Image.new("RGB", (len(TREES) * (tw + GAP) + GAP, th + 2 * GAP), BG)
    d = ImageDraw.Draw(img)
    for i, tree in enumerate(TREES):
        ox, oy = GAP + i * (tw + GAP), GAP
        d.polygon([(ox + x * SCALE, oy + y * SCALE) for x, y in poly], fill=WOOD)
        base = frame * channels + (tree - 1) * TREE_CHANNELS
        for n in nodes:
            k = base + (n["n"] - 1) * 3
            r, g, b = raw[k:k + 3]
            if r or g or b:
                x, y = ox + n["x"] * SCALE, oy + n["y"] * SCALE
                # soft glow, then the bulb
                d.ellipse([x - DOT * 2, y - DOT * 2, x + DOT * 2, y + DOT * 2], fill=(r // 4, g // 4, b // 4))
                d.ellipse([x - DOT, y - DOT, x + DOT, y + DOT], fill=(r, g, b))
    if label:
        d.text((GAP, 6), label, fill=(200, 200, 200), font=ImageFont.load_default())
    return img


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arrangement", type=Path, help="data/songs/<song>.json (or a sequence name)")
    ap.add_argument("--start", type=float, default=0.0, help="seconds")
    ap.add_argument("--end", type=float, default=None, help="seconds (default start + 15)")
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--sheet", help="contact sheet instead of a GIF: start:end:every (seconds)")
    args = ap.parse_args(argv)

    p = ROOT / args.arrangement
    seq = json.loads(p.read_text(encoding="utf-8"))["sequence"] if p.suffix == ".json" else str(args.arrangement)
    raw, channels, frames, step = read_fseq(SHOW_FOLDER / f"{seq}.fseq")
    nodes, poly, bw, bh = load_layout()
    OUT_DIR.mkdir(exist_ok=True)
    stem = seq.replace(" ", "-").replace("'", "")

    if args.sheet:
        a, b, every = (float(x) for x in args.sheet.split(":"))
        times = [a + k * every for k in range(int((b - a) / every) + 1)]
        shots = [draw_frame(raw, channels, min(int(t * 1000 / step), frames - 1), nodes, poly, bw, bh, f"{t:.1f}s")
                 for t in times]
        cols = 2
        w, h = shots[0].size
        sheet = Image.new("RGB", (w * cols, h * ((len(shots) + cols - 1) // cols)), BG)
        for k, s in enumerate(shots):
            sheet.paste(s, ((k % cols) * w, (k // cols) * h))
        out = OUT_DIR / f"{stem}-{a:g}-{b:g}.png"
        sheet.save(out)
    else:
        end = args.end if args.end is not None else args.start + 15
        every = max(1, round(1000 / args.fps / step))
        f0, f1 = int(args.start * 1000 / step), min(int(end * 1000 / step), frames)
        imgs = [draw_frame(raw, channels, f, nodes, poly, bw, bh, f"{f * step / 1000:.1f}s")
                for f in range(f0, f1, every)]
        out = OUT_DIR / f"{stem}-{args.start:g}-{end:g}.gif"
        imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=every * step, loop=0)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
