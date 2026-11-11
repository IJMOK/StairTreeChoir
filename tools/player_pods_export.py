"""Exports the site box's player pods from enclosure/player-pods.FCStd (Rob, 10 Nov 2026).
Run from the repo root with FreeCAD's own Python, after saving the model:

  freecadcmd -c "import sys; sys.path.insert(0, 'tools'); import player_pods_export; player_pods_export.main()"

  enclosure/pod-buck-base.stl, pod-buck-lid.stl     the Pi's USB buck
  enclosure/pod-audio-base.stl, pod-audio-lid.stl   PAM8610 + USB sound card
  cad/printed/pod-*.step                            as fitted

Bases print floor down; lids are turned over so the plate is on the bed. No supports.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import FreeCAD as App
import MeshPart

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "enclosure" / "player-pods.FCStd"
LINEAR, ANGULAR = 0.01, math.radians(3)
PARTS = {"buck-base": "BuckBase", "buck-lid": "BuckLid", "audio-base": "AudioBase", "audio-lid": "AudioLid"}


def on_bed(shape, flip: bool):
    s = shape.copy()
    if flip:
        s.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
    return s


def main():
    doc = App.openDocument(str(SOURCE))
    doc.recompute()
    for name, obj in PARTS.items():
        shape = doc.getObject(obj).Shape
        if not shape.isValid() or len(shape.Solids) != 1:
            raise RuntimeError(f"{obj}: not one valid solid")
        mesh = MeshPart.meshFromShape(Shape=on_bed(shape, name.endswith("lid")), LinearDeflection=LINEAR,
                                      AngularDeflection=ANGULAR, Relative=False)
        if not mesh.isSolid() or mesh.hasNonManifolds():
            raise RuntimeError(f"{name}: the mesh isn't a closed solid")
        mesh.write(str(ROOT / "enclosure" / f"pod-{name}.stl"))
        path = ROOT / "cad" / "printed" / f"pod-{name}.step"
        shape.exportStep(str(path))
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"FILE_NAME\('[^']*','[^']*'", f"FILE_NAME('{path.name}','2026-01-01T00:00:00'", text, count=1)
        text = re.sub(r"Open CASCADE STEP translator [\d.]+ \d+", path.stem, text)
        path.write_text(text, encoding="utf-8", newline="\n")
        bb = shape.BoundBox
        print(f"pod-{name}: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm, {shape.Volume / 1000:.1f} cm3")


if __name__ == "__main__":
    main()
