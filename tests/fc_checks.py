"""Geometry checks run inside FreeCAD by tests/test_cad.py (freecadcmd). Prints one JSON line
starting with RESULT: a name -> [passed, detail] map. Checks the committed exports and
the masters as saved."""

import json
import math
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

V = App.Vector
R = {}


def check(name, ok, detail=""):
    R[name] = [bool(ok), str(detail)]


def solid(path):
    return Part.read(str(ROOT / path))


# --- the tread (cad_tree.py): one solid, the right volume, a counterbore floor per pixel
layout = json.loads((ROOT / "data" / "tree-layout.json").read_text(encoding="utf-8"))
b, p = layout["blank"], layout["params"]
tree = solid("cad/tree/stair-tree.step")
check("tree is one valid solid", tree.isValid() and len(tree.Solids) == 1)
bb = tree.BoundBox
check("tree spans the thickness", abs(bb.ZMin + b["thickness"]) < 0.01 and abs(bb.ZMax) < 0.01, bb)
check("tree symmetric", abs(bb.XMin + bb.XMax - b["width"]) < 0.01, bb)
import cad_tree  # noqa: E402
slab = cad_tree.outline(layout, 0, b["thickness"]).Volume
r_cb, r_cl, d_cb = p["front_counterbore_dia"] / 2, p["clearance_dia"] / 2, p["front_counterbore_depth"]
pixels = len(layout["nodes"]) * math.pi * (r_cb ** 2 * d_cb + r_cl ** 2 * (b["thickness"] - d_cb))
old = sum(math.pi * (h["dia"] / 2) ** 2 * h["depth"] for h in b["existing_holes"])
check("tree volume = slab - pixel holes - old holes", abs(tree.Volume / (slab - pixels - old) - 1) < 1e-3, tree.Volume)
floors = [f for f in tree.Faces if f.Surface.TypeId == "Part::GeomPlane" and abs(f.CenterOfMass.z + d_cb) < 1e-6]
check("one counterbore floor per pixel", len(floors) == len(layout["nodes"]), len(floors))
plate = solid("cad/tree/fixture-plate.step")
check("tree sits in the plate pocket", tree.common(plate).Volume < 1e-3)

# --- the tree box (as exported from cad/parts/tree-box.FCStd)
bp = json.loads((ROOT / "cad" / "parts" / "tree-box-params.json").read_text(encoding="utf-8"))
base, cover = solid("cad/printed/tree-box-base.step"), solid("cad/printed/tree-box-cover.step")
for n, s in (("base", base), ("cover", cover)):
    check(f"tree box {n}: one solid with real surfaces", s.isValid() and len(s.Solids) == 1 and len(s.Faces) < 500, len(s.Faces))
bb, cb = base.BoundBox, cover.BoundBox
check("tree box sizes follow the spreadsheet",
      abs(bb.XMin + bp["ear_w"]) < 0.01 and abs(bb.XMax - bp["box_w"] - bp["ear_w"]) < 0.01
      and abs(bb.ZMax - bp["plate_top"]) < 0.01 and abs(cb.XLength - bp["box_w"] - 2 * bp["wrap"]) < 0.01
      and abs(cb.YMax - bp["cover_y1"]) < 0.01)
check("tree box base and cover don't clash", base.common(cover).Volume < 1)
s2 = bp["s2"]
at = lambda t, x=0.0: V(bp["boss_x"] + x, bp["screw_y"] - t * s2, bp["screw_z"] + t * s2)  # noqa: E731
check("cover screw clears the cover wall and the boss bore",
      not cover.isInside(at(-bp["bevel_t"] / 2), 1e-6, False) and all(not base.isInside(at(t), 1e-6, False) for t in (1, 5, 9, 11))
      and base.isInside(at(5, bp["m3_insert_d"] / 2 + 1), 1e-6, False))
z = bp["lip_t"] + bp["floor_t"] / 2
check("shelf reaches the cover's side walls",
      base.isInside(V(0.1, 20, z), 1e-6, True) and base.isInside(V(bp["box_w"] - 0.1, 20, z), 1e-6, True)
      and cover.isInside(V(bp["ix0"] - 1, 20, z), 1e-6, True))

# --- tree mounts: the socket takes the tongue, the stack interlocks, the tower is hollow
mp = json.loads((ROOT / "cad" / "parts" / "tree-mounts-params.json").read_text(encoding="utf-8"))
sock, ski, tower = (solid(f"cad/printed/tree-{n}.step") for n in ("socket", "ski", "tower"))
check("ski and tower take the socket's tenon", sock.common(ski).Volume < 1e-3 and sock.common(tower).Volume < 1e-3)
ski_hi = ski.copy()
ski_hi.translate(V(0, mp["col_d"], 0))
check("ski clips onto the tower's outer tenon (show riser)", tower.common(ski_hi).Volume < 1e-3)
pw = mp["ten_w"] / 2 + mp["clr"]
hy = mp["base_t"] + mp["notch_y"] + 0.2 + mp["hook_d"]
zt = -mp["tree_t"] / 2 + 6
check("latch hooks sit in the socket's notches",
      all(part.isInside(V(sg * (pw - 0.5), hy, zt), 1e-6, True) for part in (ski, tower) for sg in (-1, 1))
      and all(not sock.isInside(V(sg * (mp["ten_w"] / 2 - 0.4), hy, zt), 1e-6, True) for sg in (-1, 1)))
up = tower.copy()
up.translate(V(0, 0, mp["pitch"]))
check("towers stack without clashing", tower.common(up).Volume < 1e-3)
yc = mp["bore_yc"]
z0 = -(mp["tree_t"] + mp["below"])
check("tower bore runs right through", all(not tower.isInside(V(0, yc, z), 1e-6, True)
                                           for z in (z0 + 1, z0 + mp["pitch"] / 2, z0 + mp["pitch"] + mp["spig_h"] - 1)))
spig_in_recess = up.common(tower).Volume
check("spigot sits in the recess above", spig_in_recess < 1e-3 and up.BoundBox.ZMin < tower.BoundBox.ZMax)
sole = mp["base_t"] + mp["ski_h"]
mid_cav = (mp["hol_gap"] + mp["hol_end"]) / 2
check("ski is hollow either side, solid at the pocket",
      all(not ski.isInside(V(0, sole - 5, -mp["tree_t"] / 2 + sg * mid_cav), 1e-6, True) for sg in (-1, 1))
      and ski.isInside(V(0, sole - 5, -mp["tree_t"] / 2), 1e-6, True))
for n, s in (("socket", sock), ("ski", ski), ("tower", tower)):
    check(f"{n} is one valid solid", s.isValid() and len(s.Solids) == 1)
ch = mp["tree_t"] + mp["fit"]
check("socket channel takes the tread", not sock.isInside(V(0, -mp["leg_h"] / 2, -mp["tree_t"] / 2), 1e-6, True)
      and sock.isInside(V(0, -mp["leg_h"] / 2, mp["fit"] / 2 + mp["wall"] / 2), 1e-6, True), ch)

# --- PSU hood
hp = json.loads((ROOT / "cad" / "parts" / "psu-cover-params.json").read_text(encoding="utf-8"))
hood = solid("cad/printed/psu-hood.step")
psu = Part.makeBox(215, hp["psu_w"], hp["psu_h"])
check("hood is one valid solid", hood.isValid() and len(hood.Solids) == 1)
check("hood clears the PSU", hood.common(psu).Volume < 1e-3)
check("hood M4 screws reach 5mm max into the case", hp["wall"] + 3 <= 6 + 0.01, "M4 x 6 through a 3mm wall")
check("hood has a closed floor under the chamber", hood.isInside(V(-hp["cham_l"] / 2, 60, hp["wall"] / 2), 1e-6, True))
check("hood partition between mains and 12V", hood.isInside(V(-10, hp["rib_y"], 30), 1e-6, True))

# --- masters recompute cleanly
for name in ("tree-box", "player-pods", "psu-cover", "tree-mounts", "pixel-disk", "step-clamp"):
    doc = App.openDocument(str(ROOT / "cad" / "parts" / f"{name}.FCStd"))
    doc.recompute()
    bad = [o.Name for o in doc.Objects if not o.isValid()]
    check(f"master {name} recomputes", not bad, bad)
    App.closeDocument(doc.Name)

# --- the complete tree: every link resolves and it holds the whole tree
doc = App.openDocument(str(ROOT / "cad" / "stair-tree-complete.FCStd"))
doc.recompute()
links = [o for o in doc.Objects if o.TypeId == "App::Link"]
broken = [o.Name for o in links if o.getLinkedObject() is None or o.getLinkedObject() == o]
names = {o.Name for o in doc.Objects}
needed = {"StairTree", "TreeUnit", "Tree", "TreeBox", "BoxBase", "BoxCover", "Socket0", "Socket1", "Socket2", "Ski0", "Ski1",
          "Box_esp32", "Box_sp16", "Disk01", "Disk92", "Pixels"}
check("complete tree assembly opens with every link resolved", not broken and needed <= names and len(links) > 100,
      f"broken {broken}, missing {needed - names}, {len(links)} links")
for d in list(App.listDocuments().values()):
    App.closeDocument(d.Name)

print("RESULT:" + json.dumps(R))
