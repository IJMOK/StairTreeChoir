"""The tread, generated from data/tree-layout.json in FreeCAD (replaces the CadQuery
tools/gen_step.py, 15 Nov 2026). Run with FreeCAD's Python from the repo root:

  freecadcmd -c "import sys; sys.path.insert(0, 'tools'); import cad_tree; cad_tree.main()"

  cad/stair-tree.FCStd          the tree and the fixture plate (generated: don't edit it,
                                change data/blank.json or tools/tree_layout.py and rerun)
  cad/stair-tree.step           the finished tread for CAM in NX: rounded outline, a disk
                                counterbore and a clearance hole per pixel, the old stair
                                fixing holes in the back
  cad/fixture-plate.step        MDF plate with a pocket the shape of the blank, zero
                                clearance (set the offset in CAM)
  cad/stair-tree-assembly.step  the two together

Tree axes: mm, Z up, front face at Z = 0 (the part runs down to -thickness), X right,
Y up (the top of the tree is +Y), origin at the bottom-left of the blank's bounding box.
The plate shares the origin, so the tree drops straight into its pocket.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parent.parent
LAYOUT_FILE = ROOT / "data" / "tree-layout.json"
CAD_DIR = ROOT / "cad"
FCSTD = CAD_DIR / "stair-tree.FCStd"
TREE_FILE = CAD_DIR / "stair-tree.step"
PLATE_FILE = CAD_DIR / "fixture-plate.step"
ASSEMBLY_FILE = CAD_DIR / "stair-tree-assembly.step"

PLATE_THICKNESS = 18.0   # MDF sheet
PLATE_MARGIN = 50.0      # beyond the blank's bounding box, all round
POCKET_DEPTH = 4.0       # Rob, 25 Oct 2026

Z = App.Vector(0, 0, 1)


def load_layout() -> dict:
    return json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))


def up(layout: dict, x: float, y: float) -> App.Vector:
    """Layout coordinates (y down from the top) to tree coordinates (Y up from the base)."""
    return App.Vector(x, layout["blank"]["height"] - y, 0)


def outline(layout: dict, z: float, depth: float) -> Part.Shape:
    """The blank with its rounded corners, from z down by depth."""
    b = layout["blank"]
    pts = [up(layout, x, y) + App.Vector(0, 0, z) for x, y in b["polygon"]]
    face = Part.Face(Part.makePolygon(pts + pts[:1]))
    if face.normalAt(0, 0).z < 0:
        face.reverse()
    solid = face.extrude(App.Vector(0, 0, -depth))
    if b["corner_radius"]:
        edges = [e for e in solid.Edges if abs(abs((e.Vertexes[1].Point - e.Vertexes[0].Point).normalize().z) - 1) < 1e-9]
        solid = solid.makeFillet(b["corner_radius"], edges)
    return solid


def tree_solid(layout: dict) -> Part.Shape:
    b, p = layout["blank"], layout["params"]
    t = b["thickness"]
    cuts = []
    for n in layout["nodes"]:
        c = up(layout, n["x"], n["y"])
        cuts.append(Part.makeCylinder(p["front_counterbore_dia"] / 2, p["front_counterbore_depth"] + 1,
                                      c + App.Vector(0, 0, -p["front_counterbore_depth"]), Z))
        cuts.append(Part.makeCylinder(p["clearance_dia"] / 2, t + 2, c + App.Vector(0, 0, -t - 1), Z))
    for h in b["existing_holes"]:
        c = up(layout, h["x"], h["y"])
        cuts.append(Part.makeCylinder(h["dia"] / 2, h["depth"] + 1, c + App.Vector(0, 0, -t - 1), Z))
    tree = outline(layout, 0, t).cut(Part.makeCompound(cuts))
    return tree.removeSplitter()


def plate_solid(layout: dict) -> Part.Shape:
    b = layout["blank"]
    top = -b["thickness"] + POCKET_DEPTH   # the tree's back face sits on the pocket floor
    w, h, m = b["width"], b["height"], PLATE_MARGIN
    plate = Part.makeBox(w + 2 * m, h + 2 * m, PLATE_THICKNESS, App.Vector(-m, -m, top - PLATE_THICKNESS))
    return plate.cut(outline(layout, top + 0.001, POCKET_DEPTH + 0.001)).removeSplitter()


def scrub(path: Path) -> None:
    """Fixed timestamp and names, so a rebuild only changes the file when the geometry does."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"FILE_NAME\('[^']*','[^']*'", f"FILE_NAME('{path.name}','2026-01-01T00:00:00'", text, count=1)
    text = re.sub(r"Open CASCADE STEP translator [\d.]+ \d+", path.stem, text)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_step(objs, path: Path) -> None:
    import Import
    Import.export(objs, str(path))
    scrub(path)


def main() -> None:
    layout = load_layout()
    tree, plate = tree_solid(layout), plate_solid(layout)
    for name, s in (("tree", tree), ("plate", plate)):
        if not s.isValid() or len(s.Solids) != 1:
            raise RuntimeError(f"{name}: not one valid solid")
    name = "stair_tree"
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    t = doc.addObject("Part::Feature", "Tree")
    t.Shape = tree
    t.Label = "Tree (generated from data/tree-layout.json)"
    pl = doc.addObject("Part::Feature", "FixturePlate")
    pl.Shape = plate
    doc.recompute()
    doc.saveAs(str(FCSTD))
    write_step([t], TREE_FILE)
    write_step([pl], PLATE_FILE)
    write_step([t, pl], ASSEMBLY_FILE)
    App.closeDocument(name)
    print(f"tree {tree.Volume / 1000:.1f} cm3, plate {plate.Volume / 1000:.1f} cm3; wrote "
          + ", ".join(str(f.relative_to(ROOT)) for f in (FCSTD, TREE_FILE, PLATE_FILE, ASSEMBLY_FILE)))
