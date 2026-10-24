"""Small edits to xLights sequence files (.xsq) that the automation API can't make.

    python -m tools.xsq "<sequence name>"        # add any missing GROUPS to that sequence
    python -m tools.xsq "<sequence name>" --fit-audio   # also set its length to its audio's (re-voiced skits)
    python -m tools.xsq "<new name>" --clone "<template>" --media "Audio/Songs/<new name>.mp3" --track <Track>

--clone makes a new sequence from an existing one without the GUI (xLights' New Sequence
dialog needs clicks): the template's file with the new media, its length fitted, and the
template's lyric track renamed to --track (then `tools.xl_timing add ... --replace` fills it).
The template's effects stay until tools.arrange_song replaces them, which it does for every
element the arrangements use. Use a template of the same kind (a skit for a skit).

A sequence only accepts effects on elements it lists. Groups added to the layout
later (Outlines, 23 Oct 2026) must be added to each existing sequence: once under
<DisplayElements> (row order = render order: groups first, so the trees' own
effects land on top) and once, empty, under <ElementEffects>. The sequence must be
closed in xLights while this runs; it keeps a .bak copy.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from tools.arrange_song import SHOW_FOLDER

GROUPS = ["Choir", "Outlines"]


def add_groups(path: Path, groups: list[str] = GROUPS) -> list[str]:
    s = path.read_text(encoding="utf-8")
    added = []
    for g in groups:
        if re.search(rf'<Element [^>]*type="model" name="{re.escape(g)}"', s):
            continue
        display = f'    <Element collapsed="false" type="model" name="{g}" visible="true" />\n'
        effects = f'    <Element type="model" name="{g}">\n      <EffectLayer />\n    </Element>\n'
        # after the last group already listed, else before the first tree
        m = list(re.finditer(r'    <Element collapsed="false" type="model" name="(Choir|Outlines)" visible="true" />\n', s))
        at = m[-1].end() if m else s.index('    <Element collapsed="false" type="model" name="StairTree1"')
        s = s[:at] + display + s[at:]
        e = s.index("<ElementEffects>")
        first_model = s.index('    <Element type="model"', e)
        s = s[:first_model] + effects + s[first_model:]
        added.append(g)
    if added:
        shutil.copy2(path, path.with_suffix(".xsq.bak"))
        path.write_text(s, encoding="utf-8", newline="")
    return added


def media_seconds(media: str) -> float:
    if media.lower().endswith(".wav"):
        import wave
        with wave.open(media, "rb") as w:
            return round(w.getnframes() / w.getframerate(), 3)
    import librosa
    return round(librosa.get_duration(path=media), 3)


def clone(template: Path, path: Path, media: Path, track: str) -> None:
    """A new sequence from the template's file: new media, its length, the lyric track renamed."""
    if path.exists():
        raise SystemExit(f"{path.name} already exists")
    s = template.read_text(encoding="utf-8")
    old = [n for n in re.findall(r'<Element [^>]*type="timing" name="([^"]+)"', s) if n != "New Timing"]
    if len(set(old)) != 1:
        raise SystemExit(f"{template.name}: expected one lyric timing track, found {sorted(set(old))}")
    s = s.replace(f'type="timing" name="{old[0]}"', f'type="timing" name="{track}"')
    s = re.sub(r"<mediaFile>[^<]*</mediaFile>", lambda m: f"<mediaFile>{media}</mediaFile>", s, count=1)
    seconds = media_seconds(str(media))
    s = re.sub(r"<sequenceDuration>[^<]*</sequenceDuration>", lambda m: f"<sequenceDuration>{seconds}</sequenceDuration>", s, count=1)
    path.write_text(s, encoding="utf-8", newline="")


def fit_audio(path: Path) -> float:
    """Set <sequenceDuration> to the length of the sequence's <mediaFile>."""
    s = path.read_text(encoding="utf-8")
    media = re.search(r"<mediaFile>([^<]+)</mediaFile>", s).group(1)
    seconds = media_seconds(media)
    s2 = re.sub(r"<sequenceDuration>[^<]*</sequenceDuration>", f"<sequenceDuration>{seconds}</sequenceDuration>", s, count=1)
    if s2 != s:
        shutil.copy2(path, path.with_suffix(".xsq.bak"))
        path.write_text(s2, encoding="utf-8", newline="")
    return seconds


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sequence", help="sequence name, e.g. 'Rockin Around the Christmas Tree'")
    ap.add_argument("--fit-audio", action="store_true", help="set the sequence length to its audio's")
    ap.add_argument("--clone", metavar="TEMPLATE", help="create this sequence from the template sequence")
    ap.add_argument("--media", help="with --clone: the audio, relative to the show folder")
    ap.add_argument("--track", help="with --clone: the lyric timing track's name")
    args = ap.parse_args(argv)
    path = SHOW_FOLDER / f"{args.sequence}.xsq"
    if args.clone:
        if not (args.media and args.track):
            ap.error("--clone needs --media and --track")
        clone(SHOW_FOLDER / f"{args.clone}.xsq", path, SHOW_FOLDER / args.media, args.track)
        print(f"created {path.name} from {args.clone}")
    added = add_groups(path)
    print(f"added {', '.join(added)}" if added else "nothing to add")
    if args.fit_audio:
        print(f"length {fit_audio(path)}s")


if __name__ == "__main__":
    main()
