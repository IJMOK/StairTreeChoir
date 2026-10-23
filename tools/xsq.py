"""Small edits to xLights sequence files (.xsq) that the automation API can't make.

    python -m tools.xsq "<sequence name>"        # add any missing GROUPS to that sequence

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


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("sequence", help="sequence name, e.g. 'Rockin Around the Christmas Tree'")
    args = ap.parse_args(argv)
    added = add_groups(SHOW_FOLDER / f"{args.sequence}.xsq")
    print(f"added {', '.join(added)}" if added else "nothing to add")


if __name__ == "__main__":
    main()
