"""Printed parts from the OpenSCAD sources (Rob, 26 Oct 2026): python -m tools.gen_printed

  <dir>/*.stl                  print files, laid out for the bed (as the READMEs list them)
  cad/printed/*.step           every printed part as a STEP solid, the way it is fitted
  cad/stair-tree-kit.step      one tree with everything on it, as a STEP assembly

The STEP solids are made from OpenSCAD meshes: flat faces come out as planes, curved
ones stay faceted. Good for placing parts and checking clearances in NX; for editing,
change the .scad and rerun this.

Frames (mm, Z up unless said):
  boots, pegs          boot coordinates (feet/stair-tree-foot.scad): origin on the old
                       fixing hole's axis at the tree's front face, ground z = 0, toe at
                       -y, +x towards the tree centre (mirrored on the right boot)
  tree-box-base/-cover box coordinates (enclosure/tree-box.scad), as fitted
  site-box-*           box coordinates (enclosure/site-box.scad), lid on the front
  step-clamp           the right way up, heel on the bed at z = 0
  pixel-disk           front face (under the pixel flange) at z = 0, back at +z
  stair-tree-kit       the frame of cad/stair-tree.step: X right as seen from the front,
                       Y up from the tree's bottom edge, the front face at Z = 0

Needs OpenSCAD and CadQuery (requirements-cad.txt).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
from OCP.ShapeFix import ShapeFix_Solid
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.StlAPI import StlAPI_Reader
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Shape

from tools.gen_step import CAD_DIR, scrub, tree_solid
from tools.tree_layout import LAYOUT_FILE, ROOT

PRINTED_DIR = CAD_DIR / "printed"
KIT_FILE = CAD_DIR / "stair-tree-kit.step"


@dataclass(frozen=True)
class Part:
    out: str                      # path from the repo root (.stl) or a name in cad/printed/ (.step)
    scad: str
    defines: dict = field(default_factory=dict)


FOOT, TREE_BOX, SITE_BOX = "feet/stair-tree-foot.scad", "enclosure/tree-box.scad", "enclosure/site-box.scad"
CLAMP, DISK = "fixtures/step-clamp.scad", "fixtures/pixel-disk.scad"

STLS = [
    Part("feet/stair-tree-foot-right.stl", FOOT, {"hand": "right"}),
    Part("feet/stair-tree-foot-left.stl", FOOT, {"hand": "left"}),
    Part("feet/stair-tree-peg.stl", FOOT, {"part": "peg"}),
    Part("enclosure/tree-box-base.stl", TREE_BOX, {"part": "base"}),
    Part("enclosure/tree-box-cover.stl", TREE_BOX, {"part": "cover"}),
    Part("enclosure/tree-box-coupon.stl", TREE_BOX, {"part": "coupon"}),
    Part("enclosure/tree-box-seal-test.stl", TREE_BOX, {"part": "seal-test"}),
    Part("enclosure/tree-box-spacer.stl", TREE_BOX, {"part": "spacer"}),
    *[Part(f"enclosure/site-box-{n}-trees.stl", SITE_BOX, {"part": "box", "trees": n}) for n in (6, 4, 2)],
    Part("enclosure/site-box-lid.stl", SITE_BOX, {"part": "lid"}),
    Part("fixtures/step-clamp.stl", CLAMP),
    Part("fixtures/step-clamp-washer.stl", CLAMP, {"part": "washer"}),
    Part("fixtures/pixel-disk.stl", DISK),
    Part("fixtures/pixel-disk-test.stl", DISK, {"part": "test"}),
]

STEPS = [
    Part("boot-left", FOOT, {"hand": "left"}),
    Part("boot-right", FOOT, {"hand": "right"}),
    Part("peg-left", FOOT, {"hand": "left", "part": "peg-fitted"}),
    Part("peg-right", FOOT, {"hand": "right", "part": "peg-fitted"}),
    Part("tree-box-base", TREE_BOX, {"part": "base-fitted"}),
    Part("tree-box-cover", TREE_BOX, {"part": "cover-fitted"}),
    *[Part(f"site-box-{n}-trees", SITE_BOX, {"part": "box-fitted", "trees": n}) for n in (6, 4, 2)],
    Part("site-box-lid", SITE_BOX, {"part": "lid-fitted"}),
    Part("step-clamp", CLAMP, {"part": "clamp-fitted"}),
    Part("step-clamp-washer", CLAMP, {"part": "washer"}),
    Part("pixel-disk", DISK),
]

# The kit leaves out the site box and the CNC fixtures.
KIT_COLOURS = {"boot": cq.Color(0.80, 0.52, 0.25), "peg": cq.Color(1.0, 0.55, 0.0),
               "tree-box-base": cq.Color(0.27, 0.51, 0.71), "tree-box-cover": cq.Color(0.69, 0.77, 0.87),
               "tree": cq.Color(0.72, 0.53, 0.30), "pixel-disk": cq.Color(0.15, 0.15, 0.15)}


def openscad() -> str:
    exe = shutil.which("openscad") or r"C:\Program Files\OpenSCAD\openscad.com"
    if not Path(exe).exists() and not shutil.which(exe):
        raise SystemExit("OpenSCAD not found: install it or put openscad on the PATH")
    return exe


def render(part: Part, stl: Path) -> None:
    args = [openscad(), "-o", str(stl)]
    for k, v in part.defines.items():
        args += ["-D", f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"]
    args.append(str(ROOT / part.scad))
    run = subprocess.run(args, capture_output=True, text=True)
    if run.returncode or not stl.exists():
        raise RuntimeError(f"OpenSCAD failed on {part.out}:\n{run.stderr}")


def mesh_solid(stl: Path) -> cq.Shape:
    """An OpenSCAD STL as STEP-ready solids: sewn shells closed into solids, with the
    triangles of each flat face merged into one planar face."""
    mesh = TopoDS_Shape()
    if not StlAPI_Reader().Read(mesh, str(stl)):
        raise RuntimeError(f"could not read {stl}")
    sewing = BRepBuilderAPI_Sewing(1e-4)
    sewing.Add(mesh)
    sewing.Perform()
    solids = []
    shells = TopExp_Explorer(sewing.SewedShape(), TopAbs_SHELL)
    while shells.More():
        fix = ShapeFix_Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(shells.Current())).Solid())
        fix.Perform()
        solids.append(fix.Solid())
        shells.Next()
    if not solids:
        raise RuntimeError(f"no closed shells in {stl}")
    shape = solids[0] if len(solids) == 1 else cq.Compound.makeCompound([cq.Shape.cast(s) for s in solids]).wrapped
    # Merging can break a solid (the left boot did, 26 Oct 2026): then merge faces only,
    # and failing that keep the triangles.
    for edges in (True, False):
        unify = ShapeUpgrade_UnifySameDomain(shape, True, edges, True)
        unify.Build()
        merged = cq.Shape.cast(unify.Shape())
        if merged.isValid():
            return merged
    return cq.Shape.cast(shape)


def write_step(shape, path: Path) -> None:
    if isinstance(shape, cq.Assembly):
        shape.export(str(path), exportType="STEP")
    else:
        cq.exporters.export(shape, str(path), exportType="STEP")
    scrub(path)


def boot_to_tree(layout: dict, hole: str) -> cq.Location:
    """Boot coordinates to the tree's: the boot's y (front to back) becomes -Z, its z
    (up, ground 0) becomes Y from the bottom edge, its origin the fixing hole's axis."""
    b = layout["blank"]
    h = next(h for h in b["existing_holes"] if h["name"] == hole)
    shelf = foot_param("clearance")
    return cq.Location(cq.Vector(h["x"], -shelf, 0)) * cq.Location(cq.Vector(), cq.Vector(1, 0, 0), -90)


def foot_param(name: str) -> float:
    for line in (ROOT / FOOT).read_text(encoding="utf-8").splitlines():
        if line.split("=")[0].strip() == name:
            return float(line.split("=")[1].split(";")[0])
    raise KeyError(name)


def kit(layout: dict, solids: dict[str, cq.Shape]) -> cq.Assembly:
    height = layout["blank"]["height"]
    kit = cq.Assembly(name="stair-tree-kit")
    kit.add(tree_solid(layout), name="tree", color=KIT_COLOURS["tree"])
    for side, hole in (("left", "fixing_bottom_left"), ("right", "fixing_bottom_right")):
        loc = boot_to_tree(layout, hole)
        names = [f"boot-{side}", f"peg-{side}"]   # the tree box now screws to the tree's back (not placed yet)
        for name in names:
            colour = KIT_COLOURS[name.removesuffix("-on-boot").removesuffix(f"-{side}")]
            kit.add(solids[name], name=name, loc=loc, color=colour)
    # One disk in every counterbore, front face flush with the tree's (flipped: its back goes in first).
    flip = cq.Location(cq.Vector(), cq.Vector(1, 0, 0), 180)
    for n in layout["nodes"]:
        kit.add(solids["pixel-disk"], name=f"pixel-disk-{n['n']:02d}",
                loc=cq.Location(cq.Vector(n["x"], height - n["y"], 0)) * flip, color=KIT_COLOURS["pixel-disk"])
    return kit


def main(stls: bool = True) -> None:
    PRINTED_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        jobs = [(p, tmp / f"{p.out}.stl") for p in STEPS]
        if stls:
            jobs += [(p, ROOT / p.out) for p in STLS]
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            list(pool.map(lambda job: render(*job), jobs))
        solids = {p.out: mesh_solid(tmp / f"{p.out}.stl") for p in STEPS}
    for name, shape in solids.items():
        write_step(shape, PRINTED_DIR / f"{name}.step")
    layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    write_step(kit(layout, solids), KIT_FILE)
    done = len(STEPS) + 1 + (len(STLS) if stls else 0)
    print(f"wrote {done} files: cad/printed/*.step, {KIT_FILE.relative_to(ROOT)}"
          + (", the print STLs" if stls else ""))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-stl", action="store_true", help="only the STEP files, leave the print STLs alone")
    main(stls=not ap.parse_args().no_stl)
