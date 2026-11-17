"""Slice print files for Rob's Bambu Lab P1S with Bambu Studio's command line: python -m tools.slice

  python -m tools.slice                       print/tree-plate.3mf -> print/tree-plate.gcode.3mf
  python -m tools.slice print/psu-hood.stl    any print file(s)

Profiles: the printer "Bambu Lab P1S 0.4 nozzle" and the filament "Bambu PETG Basic @BBL X1C" from Bambu Studio's own system presets, and the process print/bambu/
stair-tree-mounts.json (0.20mm Standard with 3 walls and 15% infill, no skirt or brim). The
command line doesn't resolve a preset's "inherits" chain (it quietly falls back to generic
defaults: a 200mm bed, 60mm/s walls, no filament density), so each preset is merged here first. The .gcode.3mf holds the
sliced plate (Textured PEI Plate): open it in Bambu Studio and send it (Print plate), or slice again after changing
anything. The print time and weight go into print/README.md (between the "sliced" markers).

Bambu Studio is found at BAMBU_STUDIO, or in Program Files. Its presets in %APPDATA%\\BambuStudio.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRINT = ROOT / "print"
PROCESS = PRINT / "bambu" / "stair-tree-mounts.json"
MACHINE = "Bambu Lab P1S 0.4 nozzle"
FILAMENT = "Bambu PETG Basic @BBL X1C"          # the X1C presets are the P1S's too
README = PRINT / "README.md"
START, END = "<!-- sliced -->", "<!-- /sliced -->"


def studio() -> Path | None:
    for c in (os.environ.get("BAMBU_STUDIO"), r"C:\Program Files\Bambu Studio\bambu-studio.exe"):
        if c and Path(c).exists():
            return Path(c)
    return None


def presets() -> Path:
    return Path(os.environ.get("APPDATA", "")) / "BambuStudio" / "system" / "BBL"


def flattened(kind: str, name: str) -> dict:
    """A Bambu system preset with its whole "inherits" chain merged in. The command line doesn't
    resolve a printer preset's parents (it fell back to generic defaults: a 200mm bed, slow
    accelerations, no printer model), so the slicer is given the complete preset."""
    path = presets() / kind / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"missing Bambu preset: {path}")
    child = json.loads(path.read_text(encoding="utf-8"))
    parent = flattened(kind, child["inherits"]) if child.get("inherits") else {}
    merged = {**parent, **child}
    merged.pop("inherits", None)
    return merged


def complete(kind: str, name: str, overrides: dict | None = None) -> dict:
    """The system preset, flattened, with overrides on top, marked as a system preset so the
    command line uses it as given."""
    p = flattened(kind, name)
    p.update({k: v for k, v in (overrides or {}).items() if k not in ("inherits", "from", "type")})
    p.update({"from": "system", "instantiation": "true"})
    p.setdefault("name", name)
    return p


def slice_one(exe: Path, stl: Path) -> dict:
    if not PROCESS.exists():
        raise SystemExit(f"missing profile: {PROCESS}")
    ours = json.loads(PROCESS.read_text(encoding="utf-8"))
    if stl.name.startswith("tower"):
        # v2 towers print on their backs (Rob, 17 Nov 2026) with a little support under the latch
        # tongue, from the plate up through the window behind it; bridges (the notch's roof) aren't
        ours = {**ours, "enable_support": "1", "support_type": "normal(auto)", "support_on_build_plate_only": "1",
                "bridge_no_support": "1", "support_threshold_angle": "30"}
    out = stl.with_name(stl.name.split(".")[0] + ".gcode.3mf")
    with tempfile.TemporaryDirectory() as tmp:
        files = {}
        for key, data in (("machine", complete("machine", MACHINE, {"name": MACHINE})),
                          ("process", complete("process", ours["inherits"], ours)),
                          ("filament", complete("filament", FILAMENT, {"name": FILAMENT}))):
            files[key] = Path(tmp) / f"{key}.json"
            files[key].write_text(json.dumps(data, indent=1), encoding="utf-8")
        run = subprocess.run([str(exe), "--slice", "0", "--load-settings", f"{files['machine']};{files['process']}",
                              "--load-filaments", str(files["filament"]), "--export-3mf", "out.3mf", "--outputdir", tmp,
                              str(stl)], capture_output=True, text=True, errors="replace", timeout=900)
        result = json.loads((Path(tmp) / "result.json").read_text(encoding="utf-8")) \
            if (Path(tmp) / "result.json").exists() else {}
        if run.returncode or result.get("return_code"):
            raise SystemExit(f"{stl.name}: {result.get('error_string', run.stderr[-2000:])}")
        gcode = (Path(tmp) / "plate_1.gcode").read_text(encoding="utf-8", errors="replace")
        shutil.move(str(Path(tmp) / "out.3mf"), out)
    when = re.search(r"total estimated time: ([^\n]+)", gcode)
    grams = re.search(r"total filament weight \[g\] : ([\d.]+)", gcode)
    length = re.search(r"total filament length \[mm\] : ([\d.]+)", gcode)
    info = {"file": out.name, "from": stl.name, "time": when[1].strip() if when else "?",
            "grams": round(float(grams[1])) if grams else None,
            "metres": round(float(length[1]) / 1000, 1) if length else None}
    print(f"{out}: {info['time']}, about {info['grams']}g of PETG ({info['metres']}m)")
    return info


def write_readme(infos: list[dict]) -> None:
    lines = [START, "", "## Sliced for the P1S", "",
             f"`python -m tools.slice` (Bambu Studio's command line): printer {MACHINE}, filament {FILAMENT}, "
             "process [bambu/stair-tree-mounts.json](bambu/stair-tree-mounts.json) (0.20mm Standard, 3 walls, 15% infill). "
             "Open the `.gcode.3mf` in Bambu Studio and send it; it's already sliced.", "",
             "| Ready to print | From | Time | PETG |", "|---|---|---|---|"]
    lines += [f"| [{i['file']}]({i['file']}) | {i['from']} | {i['time']} | about {i['grams']}g ({i['metres']}m) |"
              for i in infos]
    lines += ["", END]
    text = README.read_text(encoding="utf-8") if README.exists() else ""
    block = "\n".join(lines)
    if START in text and END in text:
        text = text[:text.index(START)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    README.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    exe = studio()
    if not exe:
        raise SystemExit("Bambu Studio not found: install it or set BAMBU_STUDIO")
    stls = [Path(a).resolve() for a in sys.argv[1:]] or [PRINT / "tree-plate.3mf"]
    write_readme([slice_one(exe, s) for s in stls])


if __name__ == "__main__":
    main()
