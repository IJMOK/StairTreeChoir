"""Exports the tree box from its FreeCAD master, enclosure/tree-box.FCStd. Run from the
repo root with FreeCAD's own Python (save the model first: this reads the file on disk):

  freecadcmd -c "import sys; sys.path.insert(0, 'tools'); import tree_box_export; tree_box_export.main()"

  enclosure/tree-box-*.stl        print files, laid out for the bed (enclosure/README.md)
  cad/printed/tree-box-*.step     the base and cover as fitted, with real surfaces
  enclosure/tree-box-params.json  the spreadsheet's values, for tools/gen_components.py

Then python -m tools.gen_components for the fit checks and the STEP assembly.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "enclosure" / "tree-box.FCStd"
LINEAR, ANGULAR = 0.01, math.radians(3)     # finer than a 0.4 nozzle can show
X = App.Vector(1, 0, 0)


def params(doc) -> dict[str, float]:
    sheet = doc.getObject("params")
    aliases = [sheet.getAlias(f"B{row}") for row in range(2, 500)]
    return {a: sheet.get(a) for a in aliases if a}


def stl(doc, name, bodies, place=App.Placement()):
    shapes = [doc.getObject(b).Shape for b in bodies]
    shape = Part.makeCompound(shapes) if len(shapes) > 1 else shapes[0]
    mesh = MeshPart.meshFromShape(Shape=shape.transformGeometry(place.toMatrix()), LinearDeflection=LINEAR,
                                  AngularDeflection=ANGULAR, Relative=False)
    if not mesh.isSolid() or mesh.hasNonManifolds():
        raise RuntimeError(f"{name}: the mesh isn't a closed solid")
    mesh.write(str(ROOT / "enclosure" / f"tree-box-{name}.stl"))
    print(f"tree-box-{name}.stl: {mesh.CountFacets} facets, {mesh.Volume:.0f} mm3")


def step(doc, body, name):
    path = ROOT / "cad" / "printed" / f"tree-box-{name}.step"
    doc.getObject(body).Shape.exportStep(str(path))
    text = path.read_text(encoding="utf-8")
    # as tools.gen_step.scrub: a rebuild only changes the file when the geometry does
    text = re.sub(r"FILE_NAME\('[^']*','[^']*'", f"FILE_NAME('{path.name}','2026-01-01T00:00:00'", text, count=1)
    text = re.sub(r"Open CASCADE STEP translator [\d.]+ \d+", path.stem, text)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{path.name}: {path.stat().st_size // 1024} kB")


def main():
    doc = App.openDocument(str(SOURCE))
    doc.recompute()
    broken = [o.Name for o in doc.Objects if not o.isValid()]
    if broken:
        raise RuntimeError(f"the model has errors: {broken}")
    p = params(doc)
    stl(doc, "base", ["Base"], App.Placement(App.Vector(), App.Rotation(X, 90)))                        # tree face on the bed
    stl(doc, "cover", ["Cover"], App.Placement(App.Vector(0, 0, p["cover_y1"]), App.Rotation(X, -90)))  # back on the bed
    stl(doc, "spacer", ["Spacer"])
    stl(doc, "coupon", ["Coupon"])
    stl(doc, "seal-test", ["SealStrip", "SealBar"])
    step(doc, "Base", "base")
    step(doc, "Cover", "cover")
    (ROOT / "enclosure" / "tree-box-params.json").write_text(json.dumps(p, indent=1) + "\n", encoding="utf-8", newline="\n")
    App.closeDocument(doc.Name)
