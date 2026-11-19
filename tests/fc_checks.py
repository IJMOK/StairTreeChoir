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

# --- tree mounts: dovetail rail and slot, tent-pole feet, the stack interlocks, the tower is hollow
mp = json.loads((ROOT / "cad" / "parts" / "tree-mounts-params.json").read_text(encoding="utf-8"))
sock, tower, stand, cap, jig = (solid(f"cad/printed/tree-{n}.step") for n in ("socket", "tower", "stand", "pole-cap", "drill-jig"))
zc = -mp["tree_t"] / 2
back = cap.copy()
back.rotate(V(0, 0, zc), V(0, 1, 0), 180)
check("tower and stand slide on the socket's rail", sock.common(tower).Volume < 1e-3 and sock.common(stand).Volume < 1e-3)
lip = mp["dt_root"] / 2 + mp["clr"] + 0.4          # just outside the rail's root, inside the slot's lip
check("dovetail captures the rail (the slot's lip overhangs the rail's flare)",
      tower.isInside(V(lip, 0.8, zc + 10), 1e-6, True) and stand.isInside(V(lip, 0.8, zc + 10), 1e-6, True)
      and sock.isInside(V(mp["dt_root"] / 2 + mp["clr"] + 1.5, mp["dt_h"] - 2, zc + 10), 1e-6, True))
pole = Part.makeCylinder(5.5, mp["pole_l"], V(0, mp["pole_y"], zc - mp["pole_l"] / 2))     # an 11mm pole
check("tent pole runs right through the stand, near its sole",
      stand.common(pole).Volume < 1e-3 and stand.isInside(V(0, mp["pole_y"] + 5.5 + 1, zc), 1e-6, True)
      and pole.BoundBox.ZMin < stand.BoundBox.ZMin and pole.BoundBox.ZMax > stand.BoundBox.ZMax)
check("stand lifts the tree at least 50mm", mp["lift"] >= 50 and abs(stand.BoundBox.YMax - mp["lift"]) < 0.01)
ze = zc + mp["pole_l"] / 2
zq = ze + mp["peg_at"]                       # v2: the peg's axis meets the grass here, at 45 deg
fits = Part.makeCylinder(mp["cap_rib_id"] / 2 - 0.05, mp["pole_l"], V(0, mp["pole_y"], zc - mp["pole_l"] / 2))
check("pole caps take the pole's ends (a pole just under the ribs slides in) and the ribs grip an 11mm one",
      cap.common(fits).Volume < 1e-3 and back.common(fits).Volume < 1e-3 and cap.common(pole).Volume > 0.5
      and cap.isInside(V(0, mp["pole_y"], ze + mp["cap_end"] / 2), 1e-6, True)
      # optimalBoundingBox: the plain BoundBox pads the round pad end and its fillets (43.3 for 40)
      and abs(cap.optimalBoundingBox().XLength - mp["pad_w"]) < 0.01)
check("peg hole runs at 45 deg, tip toward the tree, through the pad and its boss",
      all(not cap.isInside(V(0, mp["lift"] - h, zq + h), 1e-6, True)
          and not cap.isInside(V(mp["stake_d"] / 2 - 0.05, mp["lift"] - h, zq + h), 1e-6, True)
          and cap.isInside(V(mp["stake_d"] / 2 + 1, mp["lift"] - h, zq + h), 1e-6, True) for h in (1, 4, 8))
      and mp["peg_at"] - mp["stake_d"] / 2 * 2 ** 0.5 >= mp["cap_end"] + 1)
check("caps and stand stand on the same ground, clear of each other",
      abs(cap.optimalBoundingBox().YMax - stand.optimalBoundingBox().YMax) < 0.01 and cap.common(stand).Volume < 1e-3
      and back.common(stand).Volume < 1e-3)
up = tower.copy()
up.translate(V(0, 0, mp["pitch"]))
check("towers stack without clashing", tower.common(up).Volume < 1e-3 and sock.common(up).Volume < 1e-3)
z0 = -(mp["tree_t"] + mp["below"])
ty = mp["y_out"] - mp["spig_t"] / 2                          # the tab's centre line (v2: flush with the back)
check("tower tab sits in the pocket of the tower above",
      up.isInside(V(0, ty, z0 + mp["pitch"] + 5), 1e-6, True) is False and tower.isInside(V(0, ty, z0 + mp["pitch"] + 5), 1e-6, True)
      and not tower.isInside(V(0, ty, z0 + 5), 1e-6, True))
check("tower is slim under the rail's stop",
      not tower.isInside(V(0, 5, z0 + 5), 1e-6, True) and not tower.isInside(V(mp["col_w"] / 2 - 3, ty, z0 + 5), 1e-6, True)
      and tower.isInside(V(mp["col_w"] / 2 - 3, ty, zc), 1e-6, True))
check("spigot sits in the recess above", up.common(tower).Volume < 1e-3 and up.BoundBox.ZMin < tower.BoundBox.ZMax)
check("tower slot is stopped at the bottom, open at the top",
      tower.isInside(V(0, 6, zc - mp["rail_half"] - 2), 1e-6, True) and not tower.isInside(V(0, 6, z0 + mp["pitch"] - 1), 1e-6, True))
z1 = zc - mp["rail_half"]
fl = mp["dt_h"] + mp["clr"]
check("stand latch: a bump on a free tongue, just inside the rail's end wall when seated",
      stand.isInside(V(0, fl - mp["latch_h"] / 2, z1 + mp["latch_at"]), 1e-6, True)
      and not stand.isInside(V(mp["tongue_w"] / 2 + mp["tongue_gap"] / 2, fl + 1.5, z1 + 10), 1e-6, True)
      and mp["latch_at"] - mp["latch_r"] < mp["slot_wall"] + 1 and mp["latch_at"] - 2 > mp["slot_wall"] - 1)
check("socket: edge screw holes open through the rail, solid round them, no face screws",
      all(not sock.isInside(V(sx, y, zc), 1e-6, True) for sx in (-mp["edge_x"], mp["edge_x"]) for y in (0.5, 5, 12, mp["dt_h"] - 0.5))
      and all(sock.isInside(V(sx * (1 - 4 / mp["edge_x"]), 6, zc), 1e-6, True) for sx in (-mp["edge_x"], mp["edge_x"]))
      and sock.isInside(V(4, -5, mp["fit"] / 2 + mp["wall"] / 2), 1e-6, True))
check("socket is solid (v2), with the latch groove across its rail's tip",
      sock.isInside(V(0, mp["dt_h"] / 2, zc), 1e-6, True) and sock.isInside(V(0, mp["dt_h"] / 2, z1 + 5), 1e-6, True)
      and not sock.isInside(V(0, mp["dt_h"] - mp["latch_groove"] / 2, z1 + mp["latch_at"]), 1e-6, True)
      and sock.isInside(V(0, mp["dt_h"] - mp["latch_groove"] - 0.2, z1 + mp["latch_at"]), 1e-6, True))
check("tower latch: a bump on a free tongue, a window behind it out through the back",
      tower.isInside(V(0, fl - mp["latch_h"] / 2, z1 + mp["latch_at"]), 1e-6, True)
      and not tower.isInside(V(mp["tongue_w"] / 2 + mp["tongue_gap"] / 2, fl + 1.5, z1 + 10), 1e-6, True)
      and not tower.isInside(V(0, mp["y_out"] - 0.5, z1 + 10), 1e-6, True)
      and tower.isInside(V(0, fl + mp["tower_tongue_t"] / 2, z1 + 10), 1e-6, True))
plug = solid("cad/printed/tree-screw-plug.step")
core = Part.makeCylinder(mp["plug_d"] / 2 - 0.02, plug.BoundBox.YLength, V(mp["edge_x"], plug.BoundBox.YMin, zc), V(0, 1, 0))
check("screw plug (v3): in the +x counterbore, under the rail's tip, clear of the screw head, its ribs gripping the wall",
      plug.isValid() and len(plug.Solids) == 1
      and plug.BoundBox.YMax <= mp["dt_h"] - 0.2 and plug.BoundBox.YMin >= mp["edge_seat"] + 1
      and plug.common(sock).Volume > 0.1 and core.common(sock).Volume < 1e-3)   # the ribs overlap the hole as drawn (it prints small)
yb = fl + mp["slot_wall"]
zf = zc + mp["rail_half"] + 1
check("stand gusset (v3): on the centre plane past the front and down the front inside, the latch tongue still free to flex",
      stand.isInside(V(0, (yb + mp["pole_y"]) / 2, zf + 2), 1e-6, True)
      and stand.isInside(V(0, (yb + mp["pole_y"]) / 2, zf - 10), 1e-6, True)
      and not stand.isInside(V(mp["gus_t"] / 2 + 0.5, (yb + mp["pole_y"]) / 2, zf + 2), 1e-6, True)
      and not stand.isInside(V(0, yb + 1.5, z1 + 10), 1e-6, True))
check("tower tab is flush with the back face and a dovetail (narrower at the back)",
      tower.isInside(V(mp["spig_w"] / 2 - 0.5, mp["y_out"] - 0.3, -(mp["tree_t"] + mp["below"]) + mp["pitch"] + 5), 1e-6, True)
      and not tower.isInside(V(mp["spig_w"] / 2 + 0.5, mp["y_out"] - 0.3, -(mp["tree_t"] + mp["below"]) + mp["pitch"] + 5), 1e-6, True)
      and tower.isInside(V(mp["spig_w"] / 2 + 0.5, mp["y_out"] - mp["spig_t"] + 0.3, -(mp["tree_t"] + mp["below"]) + mp["pitch"] + 5), 1e-6, True))
check("socket crush ribs stand into the channel",
      sock.isInside(V(0, -4, mp["fit"] / 2 - mp["rib_in"] + 0.1), 1e-6, True)
      and not sock.isInside(V(6, -4, mp["fit"] / 2 - mp["rib_in"] + 0.1), 1e-6, True))
check("drilling jig: guides over the screw positions, a hole on the pixel above, snug over the edge",
      all(not jig.isInside(V(sx, mp["jig_base"] / 2, zc), 1e-6, True) for sx in (-mp["edge_x"], mp["edge_x"]))
      and not jig.isInside(V(0, -mp["jig_pixel_in"], mp["jig_fit"] / 2 + mp["jig_plate_t"] / 2), 1e-6, True)
      and jig.isInside(V(0, -mp["jig_pixel_in"] + mp["jig_flange_d"] / 2 + 1, mp["jig_fit"] / 2 + mp["jig_plate_t"] / 2), 1e-6, True)
      and not jig.isInside(V(0, -mp["leg_h"] / 2, zc), 1e-6, True))
for n, s in (("socket", sock), ("tower", tower), ("stand", stand), ("pole cap", cap), ("drill jig", jig)):
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

# --- LRS-350-12 hood: the inlet over the lid, the chamber only for the leads
lp = json.loads((ROOT / "cad" / "parts" / "psu-cover-lrs-params.json").read_text(encoding="utf-8"))
lhood = solid("cad/printed/psu-hood-lrs.step")
lpsu = Part.makeBox(lp["psu_l"], lp["psu_w"], lp["psu_h"])
lz = lp["hood_h"] - lp["wall"] - lp["iec_depth"]               # bottom of the inlet's tabs
lbody = Part.makeBox(lp["iec_cut_h"], lp["iec_cut_w"], lp["iec_depth"],
                     V(lp["iec_x"] - lp["iec_cut_h"] / 2, lp["iec_y"] - lp["iec_cut_w"] / 2, lz))
check("LRS hood is one valid solid", lhood.isValid() and len(lhood.Solids) == 1)
check("LRS hood clears the PSU", lhood.common(lpsu).Volume < 1e-3)
check("LRS hood M4 screws reach 5mm max into the case", 6 - lp["wall"] <= 5 + 0.01, "M4 x 6 through a 3mm wall")
check("LRS inlet sits over the lid, clear of the hood, spade room under it",
      lbody.common(lhood).Volume < 1e-3 and lbody.BoundBox.XMin > 0 and lz - lp["psu_h"] >= 8,
      f"tabs {lz - lp['psu_h']:.1f} over the lid")
check("LRS hood has a closed floor under the chamber's mains side",
      lhood.isInside(V(-lp["cham_l"] / 2, lp["rib_y"] / 2, lp["wall"] / 2), 1e-6, True))
check("LRS hood is open under the chamber's 12V side, for the leads",
      not lhood.isInside(V(-lp["cham_l"] / 2, lp["dc_y"], lp["wall"] / 2), 1e-6, True))
check("LRS hood partition between mains and 12V", lhood.isInside(V(-lp["cham_l"] / 2, lp["rib_y"], 20), 1e-6, True))
check("LRS hood is short past the PSU's end", -lhood.BoundBox.XMin <= 15.01, f"{-lhood.BoundBox.XMin:.1f}")
lyt = -(lp["fit"] + lp["wall"]) + lp["tur_w"] - lp["wall"]     # the turret's 12V-side wall, inside
check("LRS shelf shuts the chamber's 12V side off from the turret",
      lhood.isInside(V(-lp["cham_l"] / 2, (lp["rib_y"] + lyt) / 2, lp["low_h"] - lp["wall"] / 2), 1e-6, True))
check("LRS hood is low over the 12V side",
      lhood.common(Part.makeBox(300, 50, 100, V(-100, lyt + lp["wall"] + 1, lp["low_h"] + 0.01))).Volume < 1e-3)
check("LRS side walls open over the case's vent slots",
      not lhood.isInside(V((lp["vw_x0"] + lp["vw_x1"]) / 2, -lp["fit"] - lp["wall"] / 2, 15), 1e-6, True)
      and not lhood.isInside(V((lp["vw_x0"] + lp["vw_x1"]) / 2, lp["psu_w"] + lp["fit"] + lp["wall"] / 2, 15), 1e-6, True))

# --- masters recompute cleanly
for name in ("tree-box", "player-pods", "psu-cover", "psu-cover-lrs", "tree-mounts", "pixel-disk", "step-clamp"):
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
needed = {"StairTree", "TreeUnit", "Tree", "TreeBox", "BoxBase", "BoxCover", "Socket0", "Socket1", "Socket2", "Stand0", "Stand1",
          "Pole0", "Pole1", "Cap0", "CapBack1",
          "Box_esp32", "Box_sp16", "Disk01", "Disk92", "Pixels"}
check("complete tree assembly opens with every link resolved", not broken and needed <= names and len(links) > 100,
      f"broken {broken}, missing {needed - names}, {len(links)} links")
for d in list(App.listDocuments().values()):
    App.closeDocument(d.Name)

print("RESULT:" + json.dumps(R))
