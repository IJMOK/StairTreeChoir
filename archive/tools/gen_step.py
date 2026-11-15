"""STEP solids for CAM in NX, from data/tree-layout.json (Rob, 25 Oct 2026).

  cad/stair-tree.step           the finished tread: rounded outline, a disk
                                counterbore and a clearance hole per pixel,
                                and the old stair fixing holes in the back
  cad/fixture-plate.step        MDF plate with a pocket the shape of the blank,
                                zero clearance (set the offset in CAM)
  cad/stair-tree-assembly.step  the two together

Axes: mm, Z up, the tree's front face at Z = 0 (the part runs down to
Z = -thickness), X right, Y up (the tree's top is +Y), origin at the
bottom-left of the blank's bounding box. The plate shares the origin, so the
tree drops straight into its pocket.

Needs CadQuery (requirements-cad.txt); tools/build.py skips this without it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

from tools.tree_layout import LAYOUT_FILE, ROOT

CAD_DIR = ROOT / "cad"
TREE_FILE = CAD_DIR / "stair-tree.step"
PLATE_FILE = CAD_DIR / "fixture-plate.step"
ASSEMBLY_FILE = CAD_DIR / "stair-tree-assembly.step"


@dataclass(frozen=True)
class FixtureParams:
    plate_thickness: float = 18.0   # MDF sheet
    margin: float = 50.0            # plate beyond the blank's bounding box, all round
    pocket_depth: float = 4.0       # Rob, 25 Oct 2026


def up(layout: dict, x: float, y: float) -> tuple[float, float]:
    """Layout coordinates (y down from the top) to STEP coordinates (Y up from the base)."""
    return (x, layout["blank"]["height"] - y)


def outline(layout: dict, z: float, depth: float) -> cq.Workplane:
    """The blank outline with its rounded corners, from z down by depth."""
    b = layout["blank"]
    pts = [up(layout, x, y) for x, y in b["polygon"]]
    solid = cq.Workplane("XY", origin=(0, 0, z)).polyline(pts).close().extrude(-depth)
    return solid.edges("|Z").fillet(b["corner_radius"]) if b["corner_radius"] else solid


def tree_solid(layout: dict) -> cq.Workplane:
    b, p = layout["blank"], layout["params"]
    t = b["thickness"]
    nodes = [up(layout, n["x"], n["y"]) for n in layout["nodes"]]
    tree = (outline(layout, 0, t).faces(">Z").workplane(origin=(0, 0, 0))
            .pushPoints(nodes)
            .cboreHole(p["clearance_dia"], p["front_counterbore_dia"], p["front_counterbore_depth"]))
    for h in b["existing_holes"]:
        hole = (cq.Workplane("XY", origin=(0, 0, -t)).center(*up(layout, h["x"], h["y"]))
                .circle(h["dia"] / 2).extrude(h["depth"]))
        tree = tree.cut(hole)
    return tree


def plate_solid(layout: dict, fp: FixtureParams = FixtureParams()) -> cq.Workplane:
    b = layout["blank"]
    top = -b["thickness"] + fp.pocket_depth  # the tree's back face sits on the pocket floor
    w, h, m = b["width"], b["height"], fp.margin
    plate = (cq.Workplane("XY", origin=(0, 0, top)).center(w / 2, h / 2)
             .rect(w + 2 * m, h + 2 * m).extrude(-fp.plate_thickness))
    return plate.cut(outline(layout, top, fp.pocket_depth))


def scrub(path: Path) -> None:
    """Fixed timestamp and names, so a rebuild only changes the file when the geometry does
    (OpenCascade otherwise numbers its products per process: 'translator 7.9 1', '... 2')."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"FILE_NAME\('[^']*','[^']*'", f"FILE_NAME('{path.name}','2026-01-01T00:00:00'", text, count=1)
    text = re.sub(r"Open CASCADE STEP translator [\d.]+ \d+", path.stem, text)
    path.write_text(text, encoding="utf-8", newline="\n")


def write(shape, path: Path) -> None:
    if isinstance(shape, cq.Assembly):
        shape.export(str(path), exportType="STEP")
    else:
        cq.exporters.export(shape, str(path), exportType="STEP")
    scrub(path)


def main() -> None:
    layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    tree, plate = tree_solid(layout), plate_solid(layout)
    CAD_DIR.mkdir(exist_ok=True)
    write(tree, TREE_FILE)
    write(plate, PLATE_FILE)
    assembly = (cq.Assembly(name="stair-tree-assembly")
                .add(tree, name="tree", color=cq.Color(0.72, 0.53, 0.30))
                .add(plate, name="fixture-plate", color=cq.Color(0.55, 0.45, 0.35, 0.6)))
    write(assembly, ASSEMBLY_FILE)
    print(f"wrote {', '.join(str(f.relative_to(ROOT)) for f in (TREE_FILE, PLATE_FILE, ASSEMBLY_FILE))}")


if __name__ == "__main__":
    main()
