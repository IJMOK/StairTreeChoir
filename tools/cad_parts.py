"""First builds of the FreeCAD masters that replaced the OpenSCAD parts (15 Nov 2026).

Run once per part with FreeCAD's Python, from the repo root:

  freecadcmd -c "import sys; sys.path.insert(0, 'tools'); import cad_parts; cad_parts.main(['tree-mounts'])"

Each writes cad/parts/<name>.FCStd. From then on the .FCStd is the master: edit its
`params` sheet (or its features) in FreeCAD, save, and run tools/cad_export.py.
Rerunning a builder OVERWRITES the master and any hand edits in it, so it refuses to
unless you pass force=True. The builders stay here as a record of how each part is made.

Frames, as fitted (mm):
  tree-mounts   the socket frame: x along the tree's edge (0 = socket centre), y out of
                the edge (0 = the edge, + away from the tree), z through the tree with
                the front face at 0 and the back at -tree_t (the tree's own Z)
  psu-cover     the PSU's frame: x along its length from the terminal end (0) to 215,
                y across from the pin 1 side (0) to 115, z up from its base (0)
  pixel-disk    front face (under the pixel flange) at z = 0, back at +z
  step-clamp    the right way up, heel on the bed at z = 0, x along the bar from the nose
"""

from __future__ import annotations

import sys
from pathlib import Path

import FreeCAD as App

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fcad as F  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PARTS_DIR = ROOT / "cad" / "parts"


# --------------------------------------------------------------------------- tree mounts

def tree_mounts():
    """Socket, ski foot and storage tower (Rob, 15 Nov 2026; v3 the same day).

    One rule: sockets and towers carry tenons, skis and towers carry pockets, and anything
    with a pocket clips onto anything with a tenon. No bolts: a springy latch arm in each
    side wall of every pocket clicks its hook into a notch in the tenon (a firm pull takes
    it off again: the hook's back face is 60 deg). Every tenon has a 45 deg keel underneath
    (the tree's back side), so it prints without supports in any direction and the parts
    only go together one way.

      socket   on the tree (3 per tree): a slim U-clip over the edge and a tenon. Minimal.
      ski      show feet (2 per tree): a pocket, 250mm long to fit a P2S bed, hollow.
      tower    storage (3 per tree): pocket on the tree side, spigot and recess to stack,
               and a second tenon on its outer face, so in the show it can go between
               socket and ski as a riser, lifting the tree by col_d.

    Fillets and chamfers are fixed at build time; the sizes follow the sheet. The latch
    arms run along the print's Z in each part (the ski prints sole down, the tower upright),
    so neither needs supports.
    """
    doc = F.new_doc("tree_mounts")
    F.sheet(doc, [
        ("", None, "The tree"),
        ("tree_t", 30, "tread thickness"),
        ("fit", 0.8, "total slack across the channel: the screws pull the back leg tight"),
        ("", None, "Socket (3 per tree): a slim U-clip and a tenon, nothing more"),
        ("sock_w", 46, "along the edge: fits the 56mm flat at the tree's top between the corner radii"),
        ("base_t", 4, "under the edge: the rider's top face bears on it"),
        ("wall", 3.5, "legs"),
        ("leg_h", 10, "up the faces from the edge: outline pixel counterbores start 12.5mm in"),
        ("screw_x", 13, "back-leg screws at +-this from the centre"),
        ("screw_y", -5, "screw centre, mm in from the edge (negative = on the tree)"),
        ("screw_d", 4.5, "4 x 16 countersunk stainless wood screw: 12.5mm into the oak, 17.5mm left in front"),
        ("csk_d", 9.0, "countersink, 90 deg"),
        ("", None, "Tenon (socket, and the tower's outer face) and the pockets that take it"),
        ("ten_w", 24, "along the edge"),
        ("ten_t", 22, "through the tree's thickness, centred on it: flat sides on top, a 45 deg keel below"),
        ("ten_l", 20, "length beyond the face it stands on"),
        ("clr", 0.3, "pocket clearance a side round the tenon"),
        ("mouth_ch", 1.5, "lead-in chamfer at the pocket mouth"),
        ("", None, "Latch: an arm in each side wall of a pocket, its hook in a notch across the tenon's side"),
        ("notch_y", 3, "notch starts this far along the tenon from its root"),
        ("notch_w", 2.6, "notch width along the tenon"),
        ("notch_d", 0.9, "notch depth into the tenon"),
        ("hook_d", 1.0, "hook stands this far out of the pocket wall (0.7 into the notch)"),
        ("arm_t", 2.5, "arm thickness: the flex"),
        ("arm_w", 8, "arm width"),
        ("arm_l", 24, "arm length, root to free end"),
        ("arm_gap", 1.2, "slot round the arm: more than hook_d, so it can spring clear"),
        ("", None, "Ski foot (2 per tree, show)"),
        ("ski_w", 44, "across"),
        ("ski_h", 46, "height: the tree's bottom edge sits base_t + ski_h = 50mm off the ground"),
        ("ski_l", 259, "sole front to back before the ends are rounded: finished about 250, for a P2S bed (256)"),
        ("ski_taper", 40, "top shorter than the sole by this at each end"),
        ("stake_d", 8.8, "for 8mm peg stakes"),
        ("stake_off", 98, "stake holes at +-this from the tree's centre plane"),
        ("hol_wall", 4, "hollow ski: side walls"),
        ("hol_h", 24, "hollow ski: straight-sided part of each cavity, up from the sole"),
        ("hol_gap", 16, "cavities start this far either side of the centre: solid round the pocket and latches"),
        ("hol_end", 78, "and stop this far out: solid round the stake holes and under the sloped ends"),
        ("", None, "Storage tower (3 per tree); also the show riser"),
        ("col_w", 46, "along the edge"),
        ("col_d", 64, "away from the tree: the pocket, then the hollow bore. Also how much a riser lifts the tree"),
        ("below", 70, "column bottom below the tree's back face: the tree box stands 60 off it"),
        ("pitch", 115, "stack pitch: tree to tree. Pixels (~9 proud) clear the box above by ~16"),
        ("spig_h", 20, "spigot height: how far each tower drops into the one above"),
        ("spig_w", 38, "spigot base, along the edge"),
        ("spig_d", 30, "spigot base, the other way"),
        ("spig_taper", 2, "spigot narrower at its top by this a side"),
        ("spig_clr", 0.4, "recess clearance a side"),
        ("tube_t", 3, "wall of the hollow spigot: the bore runs right through, so no bridges"),
        ("bore_yc", "=base_t + col_d - 5 - (spig_d / 2 + spig_clr)", "worked out: bore and spigot centre, 5mm in from the column's outer face"),
    ])

    P = "params."
    zc = f"-{P}tree_t / 2"
    ch_lo = f"-({P}tree_t + {P}fit / 2)"
    keel = f"({P}ten_w / 2)"                                  # 45 deg: as deep as half the width
    z_keel = f"{zc} - {P}ten_t / 2 + {keel}"                  # where the flat sides end and the keel starts
    along = lambda v: abs(v.x) > 0.99    # noqa: E731
    upward = lambda v: abs(v.y) > 0.99   # noqa: E731
    through = lambda v: abs(v.z) > 0.99  # noqa: E731

    # --- a tenon standing on the face y = y0, with a notch across each side
    def tenon(prefix, y0):
        top = F.box(doc, f"{prefix}TenonTop", f"{P}ten_w", f"{P}ten_l + 0.01", f"{P}ten_t / 2 - ({z_keel} - {zc})",
                    f"-{P}ten_w / 2", f"{y0} - 0.01", z_keel)
        doc.recompute()
        top_r = F.fillet(doc, f"{prefix}TenonTopR", top, 2.0,
                         lambda e, s: upward(F.direction(e)) and F.mid(e).z > s.BoundBox.ZMax - 0.01)
        kl = F.wedge(doc, f"{prefix}TenonKeel", f"-{P}ten_w / 2", f"{P}ten_w / 2", 0, keel,
                     f"{y0} - 0.01", f"{y0} + {P}ten_l", -0.5, 0.5, f"{y0} - 0.01", f"{y0} + {P}ten_l",
                     0, 0, z_keel, F.X, -90)
        notches = [F.box(doc, f"{prefix}Notch{i}", f"{P}notch_d + 1", f"{P}notch_w", f"{P}ten_t + 2",
                         x, f"{y0} + {P}notch_y", f"{zc} - {P}ten_t / 2 - 1")
                   for i, x in enumerate((f"-{P}ten_w / 2 - 1", f"{P}ten_w / 2 - {P}notch_d"))]
        return F.fuse(doc, f"{prefix}TenonSolid", [top_r, kl]), notches

    # --- the pocket that takes a tenon standing on y0, cut into a rider; the latch arms are
    # added back after the cut. `arm_axis` is "y" (the arm runs along the tenon: the ski) or
    # "z" (the arm runs through the tree's thickness: the tower).
    def pocket(prefix, y0, arm_axis):
        pw = f"({P}ten_w + 2 * {P}clr)"
        g = f"{P}clr"
        top = F.box(doc, f"{prefix}PocketTop", pw, f"{P}ten_l + 0.5 + 1", f"{P}ten_t / 2 - ({z_keel} - {zc}) + {g}",
                    f"-{pw} / 2", f"{y0} - 1", z_keel)
        kl = F.wedge(doc, f"{prefix}PocketKeel", f"-{pw} / 2", f"{pw} / 2", 0, f"{keel} + {g}",
                     f"{y0} - 1", f"{y0} + {P}ten_l + 0.5", f"-0.5 - {g}", f"0.5 + {g}",
                     f"{y0} - 1", f"{y0} + {P}ten_l + 0.5", 0, 0, f"{z_keel} + 0.01", F.X, -90)
        mouth = F.wedge(doc, f"{prefix}Mouth", f"-{pw} / 2 - {P}mouth_ch", f"{pw} / 2 + {P}mouth_ch",
                        f"{y0} - 0.01", f"{y0} + {P}mouth_ch", f"{z_keel} - {zc} - {P}mouth_ch",
                        f"{P}ten_t / 2 + {g} + {P}mouth_ch", f"-{pw} / 2", f"{pw} / 2",
                        f"{z_keel} - {zc}", f"{P}ten_t / 2 + {g}", 0, 0, zc)
        cuts, arms = [top, kl, mouth], []
        hy = f"({y0} + {P}notch_y + 0.2 + {P}hook_d)"              # hook peak, along the tenon
        zmid = f"({z_keel} + {zc} + {P}ten_t / 2) / 2"             # middle of the tenon's flat sides
        for i, sgn in enumerate((1, -1)):
            xw = f"{sgn} * {pw} / 2"                               # the pocket wall
            x_lo = f"{pw} / 2" if sgn > 0 else f"-{pw} / 2 - {P}arm_t - {P}arm_gap"
            ax_lo = f"{pw} / 2" if sgn > 0 else f"-{pw} / 2 - {P}arm_t"
            if arm_axis == "y":   # ski: root deep in the wall, free end just under the ski's top
                slot = F.box(doc, f"{prefix}Slot{i}", f"{P}arm_t + {P}arm_gap", f"{P}arm_l + 1",
                             f"{P}arm_w + 2 * {P}arm_gap", x_lo, f"{y0} - 1", f"{zmid} - {P}arm_w / 2 - {P}arm_gap")
                arm = F.box(doc, f"{prefix}Arm{i}", f"{P}arm_t", f"{P}arm_l - 0.5 + 0.01", f"{P}arm_w",
                            ax_lo, f"{y0} + 0.5", f"{zmid} - {P}arm_w / 2")
                hz0, hz1 = f"{zmid} - {P}arm_w / 2", f"{zmid} + {P}arm_w / 2"
            else:                 # tower: root below the pocket, free end up by the tenon's top
                z_top = f"{zc} + {P}ten_t / 2 - 1"
                slot = F.box(doc, f"{prefix}Slot{i}", f"{P}arm_t + {P}arm_gap", f"{P}arm_w + {P}arm_gap + 1",
                             f"{P}arm_l + {P}arm_gap", x_lo, f"{y0} - 1", f"{z_top} - {P}arm_l")
                arm = F.box(doc, f"{prefix}Arm{i}", f"{P}arm_t", f"{P}arm_w", f"{P}arm_l + 0.01",
                            ax_lo, f"{y0} + 0.5", f"{z_top} - {P}arm_l - 0.01")
                hz0, hz1 = f"{z_keel} + 0.5", z_top
            # the hook: a triangular ridge, 45 deg lead-in towards the mouth, 60 deg back face
            hook = F.wedge(doc, f"{prefix}Hook{i}", f"{hy} - {P}hook_d", f"{hy} + {P}hook_d * 0.58", 0, f"{P}hook_d",
                           hz0, hz1, hy, hy, hz0, hz1,
                           xw, 0, 0, F.Z, 90 if sgn > 0 else -90)
            if sgn < 0:   # mirrored: the rotation flips the wedge's X, so flip its ranges back
                for prop, val in (("Xmin", f"-({hy} + {P}hook_d * 0.58)"), ("Xmax", f"-({hy} - {P}hook_d)"),
                                  ("X2min", f"-{hy}"), ("X2max", f"-{hy}")):
                    hook.setExpression(prop, val)
            cuts.append(slot)
            arms += [arm, hook]
        return cuts, arms

    # --- socket: base under the edge, two legs, the tenon
    base = F.box(doc, "SockBase", f"{P}sock_w", f"{P}base_t", f"{P}tree_t + {P}fit + 2 * {P}wall",
                 f"-{P}sock_w / 2", 0, f"{ch_lo} - {P}wall")
    front_leg = F.box(doc, "SockFrontLeg", f"{P}sock_w", f"{P}leg_h + 0.01", f"{P}wall",
                      f"-{P}sock_w / 2", f"-{P}leg_h", f"{P}fit / 2")
    back_leg = F.box(doc, "SockBackLeg", f"{P}sock_w", f"{P}leg_h + 0.01", f"{P}wall",
                     f"-{P}sock_w / 2", f"-{P}leg_h", f"{ch_lo} - {P}wall")
    doc.recompute()
    base_r = F.fillet(doc, "SockBaseR", base, 2.5, lambda e, s: along(F.direction(e)) and F.mid(e).y > 1)
    front_r = F.fillet(doc, "SockFrontLegR", front_leg, 1.5,
                       lambda e, s: along(F.direction(e)) and F.mid(e).y < -1 and F.mid(e).z > s.BoundBox.Center.z)
    back_r = F.fillet(doc, "SockBackLegR", back_leg, 1.5,
                      lambda e, s: along(F.direction(e)) and F.mid(e).y < -1 and F.mid(e).z < s.BoundBox.Center.z)
    ten, notches = tenon("Sock", f"{P}base_t")
    screws = []
    for i, sx in enumerate((f"-{P}screw_x", f"{P}screw_x")):
        screws.append(F.cyl(doc, f"SockScrew{i}", f"{P}screw_d / 2", f"{P}wall + 2",
                            sx, f"{P}screw_y", f"{ch_lo} - {P}wall - 1"))
        screws.append(F.cone(doc, f"SockCsk{i}", f"{P}csk_d / 2 + 0.01", f"{P}screw_d / 2",
                             f"({P}csk_d - {P}screw_d) / 2 + 0.01", sx, f"{P}screw_y", f"{ch_lo} - {P}wall - 0.01"))
    F.cut(doc, "Socket", F.fuse(doc, "SocketSolid", [base_r, front_r, back_r, ten]), [*notches, *screws])

    # --- ski foot
    bar = F.wedge(doc, "SkiBar",
                  f"-{P}ski_w / 2", f"{P}ski_w / 2", f"{P}base_t", f"{P}base_t + {P}ski_h",
                  f"-({P}ski_l / 2 - {P}ski_taper)", f"{P}ski_l / 2 - {P}ski_taper",
                  f"-{P}ski_w / 2", f"{P}ski_w / 2", f"-{P}ski_l / 2", f"{P}ski_l / 2",
                  0, 0, zc)
    doc.recompute()
    bar_r = F.fillet(doc, "SkiBarR", bar, 4.0, lambda e, s: True)
    stakes = [F.cyl(doc, f"SkiStake{i}", f"{P}stake_d / 2", f"{P}ski_h + 2", 0, f"{P}base_t - 1",
                    f"{zc} {sgn} {P}stake_off", F.X, -90) for i, sgn in enumerate("-+")]
    sole = f"{P}base_t + {P}ski_h"
    hw = f"({P}ski_w / 2 - {P}hol_wall)"
    hollows = []
    for i, (lo, hi) in enumerate(((f"{P}hol_gap", f"{P}hol_end"), (f"-{P}hol_end", f"-{P}hol_gap"))):
        hollows.append(F.box(doc, f"SkiHollow{i}", f"2 * {hw}", f"{P}hol_h + 1", f"{hi} - ({lo})",
                             f"-{hw}", f"{sole} - {P}hol_h", f"{zc} + {lo}"))
        hollows.append(F.wedge(doc, f"SkiHollowRoof{i}", -1, 1, f"{sole} - {P}hol_h - ({hw} - 1)",
                               f"{sole} - {P}hol_h + 0.01", lo, hi, f"-{hw}", hw, lo, hi, 0, 0, zc))
    cuts, arms = pocket("Ski", f"{P}base_t", "y")
    ski_cut = F.cut(doc, "SkiCut", bar_r, [*cuts, *stakes, *hollows])
    ski = F.fuse(doc, "Ski", [ski_cut, *arms])
    # Latch coupon: a short slice of the ski round its pocket, to try the click and the
    # pull-off on a printed socket before printing 28 skis (change arm_t / hook_d to tune).
    slab = F.box(doc, "CouponBox", f"{P}ski_w + 2", f"{P}ten_l + 10", 56,
                 f"-{P}ski_w / 2 - 1", f"{P}base_t - 1", f"{zc} - 28")
    F.common(doc, "LatchCoupon", ski, slab)

    # --- storage tower / show riser
    z0 = f"-({P}tree_t + {P}below)"
    col = F.box(doc, "TowerColumn", f"{P}col_w", f"{P}col_d", f"{P}pitch",
                f"-{P}col_w / 2", f"{P}base_t", z0)
    doc.recompute()
    col_r = F.fillet(doc, "TowerColumnR", col, 5.0, lambda e, s: through(F.direction(e)))
    doc.recompute()
    col_c = F.chamfer(doc, "TowerColumnC", col_r, 1.0,
                      lambda e, s: not through(F.direction(e)) and (F.mid(e).z < s.BoundBox.ZMin + 0.01
                                                                     or F.mid(e).z > s.BoundBox.ZMax - 0.01))
    yc = f"{P}bore_yc"

    def frustum(name, grow, h, z):
        g = f" + {grow}" if grow else ""
        return F.wedge(doc, name,
                       f"-({P}spig_w / 2{g})", f"{P}spig_w / 2{g}", 0, h,
                       f"-({P}spig_d / 2{g})", f"{P}spig_d / 2{g}",
                       f"-({P}spig_w / 2 - {P}spig_taper{g})", f"{P}spig_w / 2 - {P}spig_taper{g}",
                       f"-({P}spig_d / 2 - {P}spig_taper{g})", f"{P}spig_d / 2 - {P}spig_taper{g}",
                       0, yc, z, F.X, 90)

    spigot = frustum("TowerSpigot", "", f"{P}spig_h", f"{z0} + {P}pitch - 0.01")
    recess = frustum("TowerRecess", f"{P}spig_clr", f"{P}spig_h + 0.01", f"{z0} - 0.01")
    bw = f"({P}spig_w - 2 * {P}spig_taper + 2 * {P}spig_clr)"
    bd = f"({P}spig_d - 2 * {P}spig_taper + 2 * {P}spig_clr)"
    iw = f"({P}spig_w - 2 * {P}spig_taper - 2 * {P}tube_t)"
    idp = f"({P}spig_d - 2 * {P}spig_taper - 2 * {P}tube_t)"
    step = f"(({bw}) - ({iw})) / 2"
    bore = F.box(doc, "TowerBore", bw, bd, f"{P}pitch - {P}spig_h - {step} + 0.02",
                 f"-{bw} / 2", f"{yc} - {bd} / 2", f"{z0} + {P}spig_h")
    roof = F.wedge(doc, "TowerBoreStep", f"-{bw} / 2", f"{bw} / 2", 0, step, f"-{bd} / 2", f"{bd} / 2",
                   f"-{iw} / 2", f"{iw} / 2", f"-{idp} / 2", f"{idp} / 2",
                   0, yc, f"{z0} + {P}pitch - {step}", F.X, 90)
    hole = F.box(doc, "TowerSpigotBore", iw, idp, f"{P}spig_h + 2",
                 f"-{iw} / 2", f"{yc} - {idp} / 2", f"{z0} + {P}pitch - 1")
    out_ten, out_notches = tenon("TowerOut", f"{P}base_t + {P}col_d")
    cuts, arms = pocket("Tower", f"{P}base_t", "z")
    tower_cut = F.cut(doc, "TowerCut", F.fuse(doc, "TowerSolid", [col_c, spigot, out_ten]),
                      [*cuts, recess, bore, roof, hole, *out_notches])
    F.fuse(doc, "Tower", [tower_cut, *arms])

    F.check(doc, ["Socket", "Ski", "Tower", "LatchCoupon"])
    return doc


# --------------------------------------------------------------------------- PSU cover

def psu_cover():
    """Terminal hood for Site A's Mean Well LRS-350-12 with a fused, switched IEC C14
    inlet (Rob, 15 Nov 2026). PSU sizes from the Mean Well datasheet (LRS-350-SPEC,
    2025-09-12, case 207A): 215 x 115 x 30, terminals 1-9 along the end at 9.5 pitch
    (1 AC/L, 2 AC/N, 3 FG, 4-6 -V, 7-9 +V), M4 side holes 32.5 from the terminal end and
    12.5 up, max 5mm into the case. Inlet: the 3-in-1 module drawing Rob sent (panel cut-out
    47.3 x 27.4, two 3.5mm holes 40 apart, ~17mm behind the panel plus ~8mm tabs)."""
    doc = F.new_doc("psu_cover")
    F.sheet(doc, [
        ("", None, "LRS-350-12 (datasheet; measure the real one before printing)"),
        ("psu_w", 115, "across"),
        ("psu_h", 30, "height"),
        ("side_x", 32.5, "M4 side holes from the terminal end"),
        ("side_z", 12.5, "M4 side holes above the base"),
        ("adj_x", 6, "+V ADJ pot and LED: access slot over them (scaled off the drawing)"),
        ("adj_y", 98, ""),
        ("", None, "Hood: one height all through, so it prints standing on its end wall with no supports"),
        ("fit", 0.5, "gap a side round the case"),
        ("wall", 3, "M4 x 6 through the wall leaves 3mm in the case (5 max)"),
        ("over_l", 45, "hood length over the case: well clear of the fan"),
        ("cham_l", 50, "wiring chamber beyond the terminal end (inside); floored"),
        ("hood_h", 63, "outside height: the inlet's flange is 54.4 tall"),
        ("rib_y", 36.25, "partition between pins 3 (FG, y 29) and 4 (-V, y 38.5): mains side and 12V side"),
        ("rib_t", 2, ""),
        ("m4_d", 4.5, "M4 clearance"),
        ("vent_l", 14, "vent slots in the 12V side wall only, over the case's own side vents"),
        ("vent_h", 2.5, "4 slots, 5mm apart from z = 5"),
        ("", None, "IEC inlet, mains side wall (3-in-1 C14 + fuse + switch, Rob's drawing)"),
        ("iec_x", -25, "centre of the inlet along the hood (in the chamber, clear of the case)"),
        ("iec_cut_w", 27.4, "panel cut-out, along the hood"),
        ("iec_cut_h", 47.3, "panel cut-out, upright (switch at the bottom)"),
        ("iec_hole_d", 3.4, "M3 x 10 + nyloc"),
        ("iec_hole_pitch", 40, "the two holes, either side of the cut-out along the hood"),
        ("", None, "12V out: a window in the roof over the chamber's 12V side, cables go up"),
        ("dc_l", 22, "along the hood"),
        ("dc_w", 36, "across"),
        ("dc_y", 78, "window centre"),
        ("tie_w", 4.5, "cable-tie slot pairs either side of the window"),
    ])
    P = "params."
    yl = f"-({P}fit + {P}wall)"
    W = f"{P}psu_w + 2 * ({P}fit + {P}wall)"
    x0 = f"-({P}cham_l + {P}wall)"
    zin = f"{P}hood_h - {P}wall"
    outer = F.box(doc, "Outer", f"{P}cham_l + {P}wall + {P}over_l", W, f"{P}hood_h", x0, yl, 0)
    over_in = F.box(doc, "OverIn", f"{P}over_l + 1.01", f"{P}psu_w + 2 * {P}fit", f"{zin} + 1",
                    -0.01, f"-{P}fit", -1)
    cham_in = F.box(doc, "ChamberIn", f"{P}cham_l + 0.02", f"{P}psu_w + 2 * {P}fit", f"{zin} - {P}wall",
                    f"-{P}cham_l", f"-{P}fit", f"{P}wall")
    rib = F.box(doc, "Rib", f"{P}cham_l - 2 + 0.01", f"{P}rib_t", f"{zin} - {P}wall + 0.02",
                f"-{P}cham_l - 0.01", f"{P}rib_y - {P}rib_t / 2", f"{P}wall - 0.01")
    m4 = [F.cyl(doc, f"M4{i}", f"{P}m4_d / 2", f"{P}wall + 2", f"{P}side_x", y, f"{P}side_z", F.X, -90)
          for i, y in enumerate((f"{yl} - 1", f"{P}psu_w - 1"))]
    vents = [F.box(doc, f"Vent{i}", f"{P}vent_l", f"{P}wall + 2", f"{P}vent_h",
                   5, f"{P}psu_w + {P}fit - 1", f"5 + {i} * 5") for i in range(4)]
    adj = F.box(doc, "AdjSlot", 6, 16, f"{P}wall + 2", f"{P}adj_x - 3", f"{P}adj_y - 8", f"{zin} - 1")
    zc = f"{P}hood_h / 2"
    iec = F.box(doc, "IecCut", f"{P}iec_cut_w", f"{P}wall + 2", f"{P}iec_cut_h",
                f"{P}iec_x - {P}iec_cut_w / 2", f"{yl} - 1", f"{zc} - {P}iec_cut_h / 2")
    iec_holes = [F.cyl(doc, f"IecHole{i}", f"{P}iec_hole_d / 2", f"{P}wall + 2",
                       f"{P}iec_x {s} {P}iec_hole_pitch / 2", f"{yl} - 1", zc, F.X, -90) for i, s in enumerate("-+")]
    dcx = f"-{P}cham_l + 4"
    dc = F.box(doc, "DcWindow", f"{P}dc_l", f"{P}dc_w", f"{P}wall + 2", dcx, f"{P}dc_y - {P}dc_w / 2", f"{zin} - 1")
    ties = [F.box(doc, f"Tie{i}", 2.5, f"{P}tie_w", f"{P}wall + 2", f"{dcx} + {k}",
                  f"{P}dc_y {s} ({P}dc_w / 2 + 4) - {P}tie_w / 2", f"{zin} - 1")
            for i, (s, k) in enumerate((("-", 4), ("-", "params.dc_l - 6.5"), ("+", 4), ("+", "params.dc_l - 6.5")))]
    shell = F.cut(doc, "HoodShell", outer, [over_in, cham_in])
    ribbed = F.fuse(doc, "HoodRibbed", [shell, rib])
    F.cut(doc, "Hood", ribbed, [*m4, *vents, adj, iec, *iec_holes, dc, *ties])

    # reference solids (not printed): the PSU and the inlet (body behind the panel, flange)
    ref_psu = F.box(doc, "RefPsu", 215, f"{P}psu_w", f"{P}psu_h", 0, 0, 0)
    ref_iec = F.box(doc, "RefIec", f"{P}iec_cut_w", 25, f"{P}iec_cut_h",
                    f"{P}iec_x - {P}iec_cut_w / 2", f"-{P}fit", f"{zc} - {P}iec_cut_h / 2")
    ref_flange = F.box(doc, "RefIecFlange", 49.2, 4, 54.4, f"{P}iec_x - 24.6", f"{yl} - 4", f"{zc} - 27.2")
    F.group(doc, "Reference", [ref_psu, ref_iec, ref_flange])
    F.check(doc, ["Hood"])
    return doc


# --------------------------------------------------------------------------- pixel disk

def pixel_disk():
    """The printed retaining disk for the 12mm bullet pixels, from fixtures/pixel-disk.scad
    as of 13 Nov 2026 (crush-rib friction fit, Rob)."""
    doc = F.new_doc("pixel_disk")
    F.sheet(doc, [
        ("", None, "Friction fit in the varnished counterbore (18.3-18.6 x 4.9 deep)"),
        ("core_od", 18.0, "clears the smallest counterbore by 0.15 a side"),
        ("rib_od", 19.3, "over the rib tips, as drawn: a solid fit (rib test strip, 13 Nov 2026)"),
        ("ribs", 8, "fixed: the model has 8 rib features"),
        ("rib_w", 1.2, "at the root (on the core)"),
        ("rib_tip_w", 0.5, "flat on the tip: at least a nozzle width"),
        ("rib_lead", 1.2, "ribs taper away over this at the back (goes in first)"),
        ("disk_t", 4.8, "flush in the 4.9 counterbore"),
        ("back_ch", 0.7, "back outer edge: clears the varnish fillet"),
        ("", None, "The pixel"),
        ("lip_t", 2.0, "= the clip gap: the clips snap behind this"),
        ("relief_d", 15.0, "behind the lip, room for the clips (= clearance_dia)"),
        ("bore", 12.0, "pixel body 12: good fit (13 Nov 2026); also tools/tree_layout.py Params.hole_dia"),
        ("chamfer", 0.4, "back edge of the bore, leads the clips through"),
    ])
    P = "params."
    core = F.cyl(doc, "Core", f"{P}core_od / 2", f"{P}disk_t - {P}back_ch")
    corech = F.cone(doc, "CoreChamfer", f"{P}core_od / 2", f"{P}core_od / 2 - {P}back_ch", f"{P}back_ch",
                    0, 0, f"{P}disk_t - {P}back_ch - 0.001")
    # Rib: a Wedge with Y radial. Its width runs linearly from rib_w at the core surface to
    # rib_tip_w at rib_od, extended inwards to r_in so its root is buried under the core's
    # back chamfer; its outer edge falls from (rib_od, disk_t - rib_lead) to (r_in, disk_t).
    r_in, r0, rt = f"({P}core_od / 2 - {P}back_ch)", f"({P}core_od / 2 - 0.1)", f"({P}rib_od / 2)"
    w_in = f"({P}rib_w + ({P}rib_w - {P}rib_tip_w) * ({r0} - {r_in}) / ({rt} - {r0}))"
    ribs = []
    for i in range(8):
        ribs.append(F.wedge(doc, f"Rib{i}", f"-{w_in} / 2", f"{w_in} / 2", r_in, rt, 0, f"{P}disk_t",
                            f"-{P}rib_tip_w / 2", f"{P}rib_tip_w / 2", 0, f"{P}disk_t - {P}rib_lead",
                            0, 0, 0, F.Z, f"{i} * 360 / {P}ribs"))
    bore = F.cyl(doc, "Bore", f"{P}bore / 2", f"{P}disk_t + 2", 0, 0, -1)
    relief = F.cyl(doc, "Relief", f"{P}relief_d / 2", f"{P}disk_t", 0, 0, f"{P}lip_t")
    ch = F.cone(doc, "BoreChamfer", f"{P}bore / 2", f"{P}bore / 2 + {P}chamfer + 0.01", f"{P}chamfer + 0.01",
                0, 0, f"{P}lip_t - {P}chamfer")
    F.cut(doc, "Disk", F.fuse(doc, "DiskSolid", [core, corech, *ribs]), [bore, relief, ch])
    F.check(doc, ["Disk"])
    return doc


# --------------------------------------------------------------------------- step clamp

def step_clamp():
    """CNC hold-down clamp and its washer, from fixtures/step-clamp.scad (23 Oct 2026),
    without the cosmetic 1mm edge bevel."""
    doc = F.new_doc("step_clamp")
    F.sheet(doc, [
        ("", None, "Rob's bed: MDF topper, 41 x 21 strut rails, M6 into channel nuts"),
        ("bolt_d", 6.5, "M6 clearance"),
        ("tree_t", 30, "tread"),
        ("spoil_t", 6, "sacrificial sheet under the tread"),
        ("work_h", "=tree_t + spoil_t", "top of the tread above the topper"),
        ("bar_l", 110, ""),
        ("bar_w", 24, ""),
        ("bar_t", 16, "bar thickness above the work"),
        ("nose_l", 12, "grip on the work: counterbores start ~12.5mm in"),
        ("nose_pad", 1, "nose stands proud so the bar tilts onto the work"),
        ("heel_l", 18, ""),
        ("slot_from_nose", 30, "slot starts this far from the nose end"),
        ("slot_len", 34, "adjustment along the bar"),
        ("washer_od", 18, ""),
        ("washer_t", 4, ""),
        ("bolt_len", "=ceil(washer_t + bar_t + work_h + 4 + 2.5 + 6)", "M6 bolt: washer, bar, work, strut drop 4, lip 2.5, nut 6"),
    ])
    P = "params."
    bar = F.box(doc, "Bar", f"{P}bar_l", f"{P}bar_w", f"{P}bar_t", 0, 0, f"{P}work_h")
    nose = F.box(doc, "Nose", f"{P}nose_l", f"{P}bar_w", f"{P}nose_pad + 0.01", 0, 0, f"{P}work_h - {P}nose_pad")
    heel = F.wedge(doc, "Heel", f"{P}bar_l - {P}heel_l", f"{P}bar_l", 0, f"{P}work_h + 0.01", f"-{P}bar_w", 0,
                   f"{P}bar_l - {P}heel_l - 10", f"{P}bar_l", f"-{P}bar_w", 0, 0, 0, 0, F.X, 90)
    slot = F.box(doc, "Slot", f"{P}slot_len", f"{P}bolt_d", f"{P}bar_t + 2",
                 f"{P}slot_from_nose", f"{P}bar_w / 2 - {P}bolt_d / 2", f"{P}work_h - 1")
    ends = [F.cyl(doc, f"SlotEnd{i}", f"{P}bolt_d / 2", f"{P}bar_t + 2", x, f"{P}bar_w / 2", f"{P}work_h - 1")
            for i, x in enumerate((f"{P}slot_from_nose", f"{P}slot_from_nose + {P}slot_len"))]
    ridges = [F.box(doc, f"Ridge{i}", 1, f"{P}bar_w + 2", 1, 2 + 3 * i, -1,
                    f"{P}work_h - {P}nose_pad - 0.6", F.Y, 45) for i in range(3)]
    F.cut(doc, "Clamp", F.fuse(doc, "ClampSolid", [bar, nose, heel]), [slot, *ends, *ridges])
    wx = -30
    w_mid = F.cyl(doc, "WasherMid", f"{P}washer_od / 2", f"{P}washer_t - 1.6", wx, 0, 0.8)
    w_lo = F.cone(doc, "WasherLo", f"{P}washer_od / 2 - 0.8", f"{P}washer_od / 2", 0.8, wx, 0, 0)
    w_hi = F.cone(doc, "WasherHi", f"{P}washer_od / 2", f"{P}washer_od / 2 - 0.8", 0.8, wx, 0, f"{P}washer_t - 0.8")
    w_hole = F.cyl(doc, "WasherHole", f"{P}bolt_d / 2", f"{P}washer_t + 2", wx, 0, -1)
    F.cut(doc, "Washer", F.fuse(doc, "WasherSolid", [w_lo, w_mid, w_hi]), [w_hole])
    F.check(doc, ["Clamp", "Washer"])
    return doc


BUILDERS = {"tree-mounts": tree_mounts, "psu-cover": psu_cover, "pixel-disk": pixel_disk, "step-clamp": step_clamp}


def main(names=None, force=False):
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in names or BUILDERS:
        path = PARTS_DIR / f"{name}.FCStd"
        if path.exists() and not force:
            print(f"{path.name} exists: it is the master now; pass force=True to overwrite it")
            continue
        doc = BUILDERS[name]()
        doc.saveAs(str(path))
        App.closeDocument(doc.Name)
        print(f"wrote {path.relative_to(ROOT)}")
