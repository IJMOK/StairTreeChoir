"""Run the FreeCAD exports from the project's Python: python -m tools.cad

Finds freecadcmd (FREECADCMD, then %LOCALAPPDATA%\\Programs\\FreeCAD 1.1\\bin, then the PATH)
and runs tools/cad_export.py in it, which writes every CAD output (cad/README.md lists them).
Takes a few minutes. Pick steps with --only, e.g. python -m tools.cad --only parts,assembly
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = ("tree", "parts", "components", "assembly")
NOISE = re.compile(r"^\s*$|\*{3}|Step File Name|Transfer|WorkSession|Recompute|Importing project|^\s*\(\d+ %\)|\.\.\.\.")


def freecadcmd() -> str | None:
    candidates = [os.environ.get("FREECADCMD"),
                  str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "FreeCAD 1.1" / "bin" / "freecadcmd.exe"),
                  shutil.which("freecadcmd"), shutil.which("FreeCADCmd")]
    return next((c for c in candidates if c and Path(c).exists()), None)


def run(steps=STEPS) -> int:
    exe = freecadcmd()
    if not exe:
        print("freecadcmd not found: install FreeCAD 1.1 or set FREECADCMD", file=sys.stderr)
        return 1
    flags = ", ".join(f"{s}={s in steps}" for s in STEPS)
    code = f"import sys; sys.path[:0] = ['.', 'tools']; import cad_export; cad_export.main({flags})"
    proc = subprocess.Popen([exe, "-c", code], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace")
    failed = False
    for line in proc.stdout:
        for part in line.replace("\r", "\n").split("\n"):
            if not NOISE.search(part):
                print(part)
            failed |= "Traceback" in part
    return proc.wait() or int(failed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help=f"comma-separated steps from {', '.join(STEPS)}")
    a = ap.parse_args()
    steps = tuple(a.only.split(",")) if a.only else STEPS
    sys.exit(run(steps))


if __name__ == "__main__":
    main()
