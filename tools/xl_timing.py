"""Lyric timing tracks for xLights sequences, without the GUI.

    python -m tools.xl_timing verify "<sequence>" <track>     # compare with a track xLights made
    python -m tools.xl_timing add "<sequence>" "Audio/Songs/<sequence>.timing.json" [--name <track>]

Ports, line for line, what xLights 2026.18 does when you import an "Eleven Labs" JSON
(SequenceFile::ProcessElevenLabsTimingFiles, src-core/import_export/TimingImport.cpp)
and then right-click → Breakdown Words (RowHeading.cpp → BreakdownWord in
src-core/lyrics/LyricBreakdown.cpp and PhonemeDictionary.cpp): phrases on layer 0,
words on layer 1, mouth shapes on layer 2. Times go through 32-bit floats as in the
C++ ((int)(start * 1000.0F)) and are rounded to the frame the same way.

`verify` rebuilds an existing track from its JSON and compares it effect by effect with
what xLights saved, so the port is checked against the real thing (Rockin', Dominick).
`add` writes the track into a sequence file (closed in xLights), like the import.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from html import escape
from pathlib import Path

import numpy as np

from tools.arrange_song import SHOW_FOLDER

INSTALL_DICTS = Path(r"C:\Program Files\xLights\dictionaries")
FRAME_MS = 50
STRIP = set("/#~@$%^*,!&-_+=[]{}\":;.<>?`")


def round_to_period(number: int, frame_ms: int = FRAME_MS) -> int:
    """RoundToMultipleOfPeriod: (number + ms/2) / ms * ms in C++ integer maths."""
    q = number + frame_ms // 2
    periods = int(q / frame_ms)          # C++ division truncates towards zero
    return periods * frame_ms


def to_ms(seconds: float) -> int:
    """(int)(float_seconds * 1000.0F): float32 throughout, truncated."""
    return int(np.float32(seconds) * np.float32(1000.0))


def _find(name: str, show: Path) -> Path | None:
    for d in (show, INSTALL_DICTS):
        if (d / name).exists():
            return d / name
    return None


def load_dictionary(show: Path = SHOW_FOLDER) -> tuple[dict, dict]:
    words: dict[str, list[str]] = {}
    for name in ("standard_dictionary", "extended_dictionary", "user_dictionary"):
        p = _find(name, show)
        if p is None:
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("##") or line.startswith(";;"):
                continue
            parts = line.split()
            if len(parts) > 1:
                words[parts[0]] = parts
    mapping: dict[str, str] = {}
    for line in _find("phoneme_mapping", show).read_text(encoding="latin-1").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";;"):
            continue
        parts = line.split()
        if len(parts) > 1 and parts[0] != ".":
            mapping[parts[0]] = parts[1]
    return words, mapping


def ascii_upper(word: str) -> str:
    """wxString::Upper() as xLights runs it uppercases ASCII only (a non-ASCII letter such as
    ñ stays lower case), so user_dictionary keys keep those letters as sung."""
    return "".join(chr(ord(c) - 32) if "a" <= c <= "z" else c for c in word)


def word_phonemes(text: str, words: dict, mapping: dict) -> list[str]:
    word = "".join(" " if c == "\t" else c for c in text if c not in STRIP)
    pron = words.get(ascii_upper(word))
    out: list[str] = []
    if not pron or len(pron) <= 1:
        return out
    for p in pron[1:]:
        if not p:
            continue
        m = mapping.get(p)
        if m is not None:
            if m == "etc" and out and out[-1] == "etc":
                continue
            out.append(m)
        else:
            if out and out[-1] == "etc":
                continue
            out.append("")
    return out


def breakdown_word(start: int, end: int, text: str, words: dict, mapping: dict,
                   frame_ms: int = FRAME_MS) -> list[tuple[str, int, int]]:
    phonemes = word_phonemes(text, words, mapping)
    if not phonemes:
        return []
    count_short = sum(1 for p in phonemes if p in ("etc", "MBP"))
    min_period = int(1000.0 / (1000.0 / frame_ms))
    default_interval = (end - start) / float(len(phonemes))
    short_interval = 50.0
    if default_interval < 50:
        short_interval = float(min_period)
    adjusted = default_interval
    if len(phonemes) > 1 and len(phonemes) > count_short:
        adjusted = (end - start - count_short * short_interval) / (len(phonemes) - count_short)
    else:
        short_interval = default_interval
    out, t, shorts, longs = [], start, 0, 0
    for p in phonemes:
        if p in ("etc", "MBP"):
            shorts += 1
        else:
            longs += 1
        e = round_to_period(int(start + longs * adjusted + shorts * short_interval), frame_ms)
        e = min(e, end)
        if e > t:
            out.append((p, t, e))
        t = e
    return out


def track_layers(data: dict, words: dict, mapping: dict, frame_ms: int = FRAME_MS):
    """(phrases, words, phonemes): lists of (label, start ms, end ms)."""
    def span(a: float, b: float) -> tuple[int, int]:
        s, e = round_to_period(to_ms(a), frame_ms), round_to_period(to_ms(b), frame_ms)
        if s == e:
            e = round_to_period(s + 1000 // frame_ms, frame_ms)
        return s, e

    phrases, all_words = [], []
    for seg in data["segments"]:
        phrases.append((seg["text"], *span(seg["start_time"], seg["end_time"])))
        for w in seg["words"]:
            if not w["text"] or not w["text"].strip():
                continue
            all_words.append((w["text"], *span(w["start_time"], w["end_time"])))
    # Breakdown Words runs over every word effect, including ones that still end where
    # they start after rounding (xLights' "one more frame" fix adds 20 ms, which rounds
    # back to the same frame); those zero-length words are not saved in the file.
    # Verified against Rockin' and Dominick as xLights saved them.
    phon = [p for label, s, e in all_words for p in breakdown_word(s, e, label, words, mapping, frame_ms)]
    keep = lambda fx: [x for x in fx if x[2] > x[1]]
    return keep(phrases), keep(all_words), phon


# --- sequence files ---------------------------------------------------------

def _layer_xml(effects) -> str:
    if not effects:
        return "      <EffectLayer />\n"
    rows = "".join(f'        <Effect label="{escape(l, quote=True)}" startTime="{s}" endTime="{e}" />\n' for l, s, e in effects)
    return f"      <EffectLayer>\n{rows}      </EffectLayer>\n"


def read_track(xsq: Path, name: str) -> list[list[tuple[str, int, int]]]:
    import xml.etree.ElementTree as ET

    root = ET.parse(xsq).getroot()
    for el in root.find("ElementEffects"):
        if el.get("type") == "timing" and el.get("name") == name:
            return [[(e.get("label"), int(e.get("startTime")), int(e.get("endTime"))) for e in layer]
                    for layer in el.findall("EffectLayer")]
    raise SystemExit(f"no timing track {name!r} in {xsq.name}")


def add_track(xsq: Path, name: str, layers) -> None:
    s = xsq.read_text(encoding="utf-8")
    if re.search(rf'<Element [^>]*type="timing" name="{re.escape(name)}"', s):
        raise SystemExit(f"{xsq.name} already has a timing track {name!r}")
    display = f'    <Element collapsed="false" type="timing" name="{escape(name, quote=True)}" visible="true" views="" active="true" />\n'
    at = s.index("<DisplayElements>") + len("<DisplayElements>\n")
    s = s[:at] + display + s[at:]
    body = f'    <Element type="timing" name="{escape(name, quote=True)}">\n' + "".join(_layer_xml(l) for l in layers) + "    </Element>\n"
    at = s.index("<ElementEffects>") + len("<ElementEffects>\n")
    s = s[:at] + body + s[at:]
    shutil.copy2(xsq, xsq.with_suffix(".xsq.bak"))
    xsq.write_text(s, encoding="utf-8", newline="")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("sequence")
    v.add_argument("track")
    v.add_argument("json", type=Path)
    a = sub.add_parser("add")
    a.add_argument("sequence")
    a.add_argument("json", type=Path)
    a.add_argument("--name", help="track name (default: the JSON file's name without .timing.json)")
    args = ap.parse_args(argv)
    words, mapping = load_dictionary()
    data = json.loads((SHOW_FOLDER / args.json).read_text(encoding="utf-8"))
    built = track_layers(data, words, mapping)
    xsq = SHOW_FOLDER / f"{args.sequence}.xsq"
    if args.cmd == "verify":
        saved = read_track(xsq, args.track)
        for name, mine, theirs in zip(("phrases", "words", "phonemes"), built, saved):
            diff = [(i, m, t) for i, (m, t) in enumerate(zip(mine, theirs)) if m != t]
            print(f"{name}: {len(mine)} built, {len(theirs)} in xLights, {len(diff)} differ"
                  + (f"; first {diff[:3]}" if diff else ""))
    else:
        name = args.name or args.json.name.removesuffix(".json").removesuffix(".timing")
        add_track(xsq, name, built)
        print(f"added timing track {name!r} to {xsq.name}: "
              f"{len(built[0])} phrases, {len(built[1])} words, {len(built[2])} mouth shapes")


if __name__ == "__main__":
    main()
