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

# --- tree mounts: dovetail rails and slots, the stack interlocks, the tower is hollow
mp = json.loads((ROOT / "cad" / "parts" / "tree-mounts-params.json").read_text(encoding="utf-8"))
sock, half, tower = (solid(f"cad/printed/tree-{n}.step") for n in ("socket", "ski-half", "tower"))
zc = -mp["tree_t"] / 2
back = half.copy()
back.rotate(V(0, 0, zc), V(0, 1, 0), 180)
check("ski halves and tower slide on the socket's rail",
      sock.common(half).Volume < 1e-3 and sock.common(back).Volume < 1e-3 and sock.common(tower).Volume < 1e-3
      and half.common(back).Volume < 1e-3)
hi_f, hi_b = half.copy(), back.copy()
hi_f.translate(V(0, mp["y_out"], 0))
hi_b.translate(V(0, mp["y_out"], 0))
check("ski halves slide onto the tower's outer rail (show riser)",
      tower.common(hi_f).Volume < 1e-3 and tower.common(hi_b).Volume < 1e-3)
lip = mp["dt_root"] / 2 + mp["clr"] + 0.4          # just outside the rail's root, inside the slot's lip
check("dovetail captures the rail (the slot's lip overhangs the rail's flare)",
      half.isInside(V(lip, 0.5, zc + 10), 1e-6, True) and tower.isInside(V(lip, 0.8, zc + 10), 1e-6, True)
      and sock.isInside(V(lip, mp["dt_h"] - 2, zc + 10), 1e-6, True))
up = tower.copy()
up.translate(V(0, 0, mp["pitch"]))
check("towers stack without clashing", tower.common(up).Volume < 1e-3 and sock.common(up).Volume < 1e-3)
yc = mp["bore_yc"]
z0 = -(mp["tree_t"] + mp["below"])
check("tower bore runs right through", all(not tower.isInside(V(0, yc, z), 1e-6, True)
                                           for z in (z0 + 1, z0 + mp["pitch"] / 2, z0 + mp["pitch"] + mp["spig_h"] - 1)))
check("spigot sits in the recess above", up.common(tower).Volume < 1e-3 and up.BoundBox.ZMin < tower.BoundBox.ZMax)
check("tower slot is stopped at the bottom, open at the top",
      tower.isInside(V(0, 6, zc - mp["rail_half"] - 2), 1e-6, True) and not tower.isInside(V(0, 6, z0 + mp["pitch"] - 1), 1e-6, True))
dz = (mp["inner_l"] + 6 + mp["half_l"] - 12) / 2            # middle of the cavities, from the centre plane
w = mp["ski_w"] + (mp["ski_w_end"] - mp["ski_w"]) * (dz - mp["inner_l"]) / (mp["half_l"] - mp["inner_l"])
xcav = (mp["hol_wall"] / 2 + w / 2 - mp["hol_wall"]) / 2
check("ski half is hollow, solid round its slot",
      all(not half.isInside(V(sg * xcav, mp["ski_h"] - 2, zc + dz), 1e-6, True) for sg in (-1, 1))
      and half.isInside(V(0, mp["dt_h"] + 3, zc + 10), 1e-6, True))
for n, s in (("socket", sock), ("ski half", half), ("tower", tower)):
    check(f"{n} is one valid solid", s.isValid() and len(s.Solids) == 1)
check("socket channel takes the tread", not sock.isInside(V(0, -mp["leg_h"] / 2, zc), 1e-6, True)
      and sock.isInside(V(0, -mp["leg_h"] / 2, mp["fit"] / 2 + mp["wall"] / 2), 1e-6, True))

# --- PSU hood
hp = json.loads((ROOT / "cad" / "parts" / "psu-cover-params.json").read_text(encoding="utf-8"))
hood = solid("cad/printed/psu-hood.step")
# the S-400-12 with its open terminal recess (the partition hangs into it, above the terminals)
psu = Part.makeBox(hp["psu_l"], hp["psu_w"], hp["psu_h"]).cut(
    Part.makeBox(hp["lid_x"] + 1, hp["psu_w"] - 6, hp["psu_h"] - hp["rib_z"] + 1, V(-1, 3, hp["rib_z"])))
check("hood is one valid solid", hood.isValid() and len(hood.Solids) == 1)
check("hood clears the PSU", hood.common(psu).Volume < 1e-3)
check("hood M4 screws reach 3mm max into the S-400's case", 6 - hp["wall"] <= 3 + 0.01, "M4 x 6 through a 3mm wall")
check("hood has a closed floor under the chamber's mains side",
      hood.isInside(V(-hp["cham_l"] / 2, hp["rib_y"] / 2, hp["wall"] / 2), 1e-6, True))
check("hood is open under the chamber's 12V side, for the leads",
      not hood.isInside(V(-hp["cham_l"] / 2, hp["dc_y"], hp["wall"] / 2), 1e-6, True))
check("hood partition between mains and 12V", hood.isInside(V(-10, hp["rib_y"], 30), 1e-6, True)
      and hood.isInside(V(5, hp["rib_y"], hp["rib_z"] + 5), 1e-6, True))
check("hood inlet is in the roof over the mains side",
      not hood.isInside(V(hp["iec_x"], hp["iec_y"], hp["hood_h"] - hp["wall"] / 2), 1e-6, True)
      and hp["iec_y"] + hp["iec_cut_w"] / 2 < hp["rib_y"] - hp["rib_t"] / 2
      and hp["iec_x"] + hp["iec_cut_h"] / 2 < 0)

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
