"""Beat times for a song: python -m tools.beats "<mp3>" -> <mp3 stem>.beats.json (seconds).

librosa's beat tracker on the decoded audio (needs requirements-lyrics.txt). The
arrangement file's "beats" entry points at the output. Prints the tempo and the
spread of beat intervals; a steady recording should have them all close.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.lyric_timing import SAMPLE_RATE, load_audio


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audio", type=Path)
    args = ap.parse_args(argv)

    import librosa
    import numpy as np

    y = load_audio(args.audio)
    tempo, beats = librosa.beat.beat_track(y=y, sr=SAMPLE_RATE, units="time", tightness=400)
    beats = [round(float(b), 3) for b in beats]
    gaps = np.diff(beats)
    out = args.audio.with_name(args.audio.stem + ".beats.json")
    out.write_text(json.dumps(beats), encoding="utf-8")
    print(f"{float(np.atleast_1d(tempo)[0]):.1f} BPM, {len(beats)} beats "
          f"({beats[0]:.2f}s to {beats[-1]:.2f}s), gaps {gaps.min():.3f}-{gaps.max():.3f}s -> {out}")


if __name__ == "__main__":
    main()
