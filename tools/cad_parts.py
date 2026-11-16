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
  psu-cover     the PSU's frame: x along its length from the terminal end (0) to 217,
                y across from the L side (0) to 114, z up from its base (0)
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
    """Socket, two-piece ski and storage tower (Rob, 15 Nov 2026; v4: dovetails).

    One joint everywhere: a dovetail rail running front to back. Sockets and towers carry
    rails, ski halves and towers carry slots.

      socket     on the tree (3 per tree): a U over the edge, screwed through both legs
                 (two each side, the front pair offset from the back pair), with a dovetail
                 rail under the edge that sticks out past both faces. Prints rail-down.
      ski half   show feet (4 per tree, 2 per bottom socket): a slot running in from the inner
                 end; full size round the slot, slimmer and lower towards the outer end. One slides on from the front and one from the back until they butt
                 under the tree; staking each half down locks the joint. About 500mm of ground
                 cover front to back; one tree's whole set prints on one 256 bed.
      tower      storage (3 per tree): a slot on the tree side, open at the top and stopped at
                 the bottom, so a tree lying face up drops onto its towers; spigot and recess to
                 stack. A rail on its outer face, so in the show it slides onto a socket lying
                 front to back and the ski halves slide onto it: a riser.

    Fillets and chamfers are fixed at build time; the sizes follow the sheet.
    """
    doc = F.new_doc("tree_mounts")
    F.sheet(doc, [
        ("", None, "The tree"),
        ("tree_t", 30, "tread thickness"),
        ("fit", 0.8, "total slack across the channel: the screws pull the legs tight"),
        ("", None, "Socket (3 per tree): a U over the edge, screwed both sides, a dovetail rail under it"),
        ("leg_w", 37, "along the edge: within the rail's root, so nothing overhangs as it prints rail down"),
        ("wall", 3.5, "legs"),
        ("leg_h", 10, "up the faces from the edge: outline pixel counterbores start 12.5mm in"),
        ("screw_x", 12, "back-leg screws at +-this from the centre"),
        ("front_x", 4, "front-leg screws at +-this: offset from the back pair"),
        ("screw_y", -5, "screw centre, mm in from the edge (negative = on the tree)"),
        ("screw_d", 4.5, "4 x 16 countersunk stainless wood screws: 12.5mm into the oak from each side"),
        ("csk_d", 9.0, "countersink, 90 deg"),
        ("", None, "Dovetail rail (socket, and the tower's outer face) and the slots that take it"),
        ("dt_h", 16, "rail height, out from the face it stands on (Rob: bigger, 15 Nov 2026)"),
        ("dt_tip", 46, "rail width at its tip (the wide side): 46 so the skis are narrow enough for one plate"),
        ("dt_ang", 15, "undercut a side, deg"),
        ("dt_root", "=dt_tip - 2 * dt_h * tan(dt_ang)", "worked out: rail width at its root"),
        ("rail_half", 29, "rail runs this far either side of the tree's centre plane: 14mm past each face"),
        ("clr", 0.3, "slot clearance a side"),
        ("", None, "Ski half (4 per tree, show)"),
        ("ski_w", 54, "across, at the inner end round the slot (Rob: narrower, so a whole set fits one plate)"),
        ("ski_h", 50, "height at the inner end: the tree's bottom edge sits this far off the ground"),
        ("inner_l", 40, "full size for this far from the centre plane (the slot), then it tapers"),
        ("ski_w_end", 30, "width at the outer end (Rob: slimmer towards the ends)"),
        ("ski_h_end", 24, "height at the outer end: the sole stays flat, the top slopes down"),
        ("half_l", 190, "length from the tree's centre plane to the outer end: 4 halves + 3 sockets fit one 255 plate"),
        ("butt_gap", 0.2, "each half stops this short of the centre plane"),
        ("stake_d", 8.8, "for 8mm peg stakes"),
        ("stake_1", 55, "stake holes this far from the centre plane..."),
        ("stake_2", 160, "...and this far"),
        ("hol_wall", 1.6, "shell walls: 4 perimeters of a 0.4 nozzle (Rob: hollow, strong enough, not over-engineered)"),
        ("skin", 2, "top skin over the ski's cavities (flat roofs, bridged: under 31mm wide)"),
        ("slot_wall", 3, "wall round the dovetail slots and the rail's core"),
        ("", None, "Storage tower (3 per tree); also the show riser"),
        ("col_w", 54, "along the edge: the slot and a wall each side; 54 so a whole set fits one plate"),
        ("col_d", 56, "away from the tree: the slot, then the hollow bore. Also how much a riser lifts the tree"),
        ("below", 70, "column bottom below the tree's back face: the tree box stands 60 off it"),
        ("pitch", 115, "stack pitch: tree to tree. Pixels (~9 proud) clear the box above by ~16"),
        ("spig_h", 20, "spigot height: how far each tower drops into the one above"),
        ("spig_w", 38, "spigot base, along the edge"),
        ("spig_d", 30, "spigot base, the other way"),
        ("spig_taper", 2, "spigot narrower at its top by this a side"),
        ("spig_clr", 0.4, "recess clearance a side"),
        ("tube_t", 3, "wall of the hollow spigot: the bore runs right through, so no bridges"),
        ("bore_yc", "=0.3 + col_d - 5 - (spig_d / 2 + spig_clr)", "worked out: bore and spigot centre, 5mm in from the column's outer face"),
        ("y_out", "=0.3 + col_d", "worked out: the tower's outer face, where its rail stands"),
    ])

    P = "params."
    zc = f"-{P}tree_t / 2"
    ch_lo = f"-({P}tree_t + {P}fit / 2)"
    z1, z2 = f"{zc} - {P}rail_half", f"{zc} + {P}rail_half"
    along = lambda v: abs(v.x) > 0.99    # noqa: E731
    through = lambda v: abs(v.z) > 0.99  # noqa: E731

    def rail(prefix, y0):
        """A dovetail rail standing on the face y = y0, narrow at its root, wide at its tip."""
        r = F.wedge(doc, f"{prefix}Rail", f"-{P}dt_root / 2", f"{P}dt_root / 2", y0, f"{y0} + {P}dt_h", z1, z2,
                    f"-{P}dt_tip / 2", f"{P}dt_tip / 2", z1, z2)
        doc.recompute()
        return F.chamfer(doc, f"{prefix}RailC", r, 1.0,
                         lambda e, s: F.mid(e).y > s.BoundBox.YMax - 0.01 or not through(F.direction(e)))

    def slot(prefix, y0, zlo, zhi):
        """The slot that takes a rail standing on y0, from zlo to zhi."""
        lo = f"({P}dt_root / 2 + {P}clr - tan({P}dt_ang))"                       # at y0 - 1
        hi = f"({P}dt_root / 2 + {P}clr + ({P}dt_h + {P}clr) * tan({P}dt_ang))"  # at the slot's floor
        return F.wedge(doc, f"{prefix}Slot", f"-{lo}", lo, f"{y0} - 1", f"{y0} + {P}dt_h + {P}clr", zlo, zhi,
                       f"-{hi}", hi, zlo, zhi)

    # --- socket: legs over the edge, the rail under it
    front_leg = F.box(doc, "SockFrontLeg", f"{P}leg_w", f"{P}leg_h + 0.01", f"{P}wall",
                      f"-{P}leg_w / 2", f"-{P}leg_h", f"{P}fit / 2")
    back_leg = F.box(doc, "SockBackLeg", f"{P}leg_w", f"{P}leg_h + 0.01", f"{P}wall",
                     f"-{P}leg_w / 2", f"-{P}leg_h", f"{ch_lo} - {P}wall")
    web = F.box(doc, "SockWeb", f"{P}leg_w", 1, f"{P}tree_t + {P}fit + 2 * {P}wall",
                f"-{P}leg_w / 2", 0, f"{ch_lo} - {P}wall")       # starts exactly at the tree's edge
    doc.recompute()
    front_r = F.fillet(doc, "SockFrontLegR", front_leg, 1.5,
                       lambda e, s: along(F.direction(e)) and F.mid(e).y < -1 and F.mid(e).z > s.BoundBox.Center.z)
    back_r = F.fillet(doc, "SockBackLegR", back_leg, 1.5,
                      lambda e, s: along(F.direction(e)) and F.mid(e).y < -1 and F.mid(e).z < s.BoundBox.Center.z)
    sock_rail = rail("Sock", 0)
    screws = []
    for i, sx in enumerate((f"-{P}screw_x", f"{P}screw_x")):     # back leg, heads on the back
        screws.append(F.cyl(doc, f"SockScrew{i}", f"{P}screw_d / 2", f"{P}wall + 2",
                            sx, f"{P}screw_y", f"{ch_lo} - {P}wall - 1"))
        screws.append(F.cone(doc, f"SockCsk{i}", f"{P}csk_d / 2 + 0.01", f"{P}screw_d / 2",
                             f"({P}csk_d - {P}screw_d) / 2 + 0.01", sx, f"{P}screw_y", f"{ch_lo} - {P}wall - 0.01"))
    for i, sx in enumerate((f"-{P}front_x", f"{P}front_x")):     # front leg, heads on the front
        screws.append(F.cyl(doc, f"SockFrontScrew{i}", f"{P}screw_d / 2", f"{P}wall + 2",
                            sx, f"{P}screw_y", f"{P}fit / 2 - 1"))
        screws.append(F.cone(doc, f"SockFrontCsk{i}", f"{P}csk_d / 2 + 0.01", f"{P}screw_d / 2",
                             f"({P}csk_d - {P}screw_d) / 2 + 0.01", sx, f"{P}screw_y",
                             f"{P}fit / 2 + {P}wall + 0.01", F.X, 180))
    # core the rail from its tip face (the bed side as printed): its flanks, ends and a skin
    # under the legs stay slot_wall thick
    t15 = f"tan({P}dt_ang)"
    inset = f"({P}slot_wall / cos({P}dt_ang))"
    core = F.wedge(doc, "SockRailCore", f"-({P}dt_root / 2 + {P}slot_wall * {t15} - {inset})",
                   f"{P}dt_root / 2 + {P}slot_wall * {t15} - {inset}", f"{P}slot_wall", f"{P}dt_h + 1",
                   f"{z1} + {P}slot_wall", f"{z2} - {P}slot_wall",
                   f"-({P}dt_tip / 2 + {t15} - {inset})", f"{P}dt_tip / 2 + {t15} - {inset}",
                   f"{z1} + {P}slot_wall", f"{z2} - {P}slot_wall")
    # A cove the full height of each leg, outside the channel (Rob, 15 Nov 2026: stronger): a
    # leg_h square bar with a leg_h-radius quarter round taken out, so each leg is buttressed
    # from the rail to its top. Each screw gets a counterbore out through the cove, so its
    # countersunk head seats flush on the leg's face.
    R = f"{P}leg_h"
    coves = []
    for name, face, out in (("Front", f"{P}fit / 2 + {P}wall", 1), ("Back", f"{ch_lo} - {P}wall", -1)):
        z_bar = face if out > 0 else f"{face} - {R}"
        bar = F.box(doc, f"SockCoveBar{name}", f"{P}leg_w", R, R, f"-{P}leg_w / 2", f"-{R}", z_bar)
        round_ = F.cyl(doc, f"SockCoveRound{name}", R, f"{P}leg_w + 2", f"-{P}leg_w / 2 - 1", f"-{R}",
                       f"{face} + {R}" if out > 0 else f"{face} - {R}", F.Y, 90)
        coves.append(F.cut(doc, f"SockCove{name}", bar, [round_]))
    sock_f = F.fuse(doc, "SocketSolid", [front_r, back_r, web, sock_rail, *coves])
    for i, sx in enumerate((f"-{P}screw_x", f"{P}screw_x")):      # heads on the back
        screws.append(F.cyl(doc, f"SockCboreBack{i}", f"{P}csk_d / 2 + 0.2", f"{R} + 1", sx, f"{P}screw_y",
                            f"{ch_lo} - {P}wall - {R} - 1"))
    for i, sx in enumerate((f"-{P}front_x", f"{P}front_x")):      # heads on the front
        screws.append(F.cyl(doc, f"SockCboreFront{i}", f"{P}csk_d / 2 + 0.2", f"{R} + 1", sx, f"{P}screw_y",
                            f"{P}fit / 2 + {P}wall"))
    F.cut(doc, "Socket", sock_f, [*screws, core])

    # --- ski half (drawn as the front half: from the centre plane forwards, +z). Full size round
    # the slot for inner_l, then tapering in width and height to the outer end, sole flat.
    zb = f"{zc} + {P}butt_gap"
    zi = f"{zc} + {P}inner_l"
    zo = f"{zc} + {P}half_l"
    run = f"({P}half_l - {P}inner_l)"

    def width(z):          # z measured from the centre plane
        return f"({P}ski_w + ({P}ski_w_end - {P}ski_w) * (({z}) - {P}inner_l) / {run})"

    def top_y(z):          # the top surface's y (down from the tree's edge) at z
        return f"(0.3 + ({P}ski_h - 0.3 - {P}ski_h_end) * (({z}) - {P}inner_l) / {run})"

    # One ruled loft through three sections (the butt end, where the taper starts, the outer
    # end), so there's no seam for the rounds to trip on. Then 2.5mm rounds on the top and end
    # edges (~1.5mm of the 1.6mm shell is left at the corners); not on the shallow creases where
    # the taper starts, where a fillet bulges outwards instead of trimming. The sole's edges stay square: they're on the bed, and a round there would cut
    # into the walls.
    sections = []
    for i, (z, w, h) in enumerate(((zb, f"{P}ski_w", f"{P}ski_h - 0.3"), (zi, f"{P}ski_w", f"{P}ski_h - 0.3"),
                                   (zo, f"{P}ski_w_end", f"{P}ski_h_end"))):
        sec = doc.addObject("Part::Plane", f"SkiSection{i}")
        F._set(sec, "Length", w)
        F._set(sec, "Width", h)
        F._place(sec, f"-({w}) / 2", f"{P}ski_h - ({h})", z)
        sec.Visibility = False
        sections.append(sec)
    body_sq = doc.addObject("Part::Loft", "SkiBodySquare")
    body_sq.Sections = sections
    body_sq.Solid = True
    body_sq.Ruled = True
    doc.recompute()
    zi_val = doc.getObject("params").get("inner_l") - doc.getObject("params").get("tree_t") / 2

    def roundable(e, s):        # top and end edges; not the sole, the butt face or the taper's start
        m = F.mid(e)
        return m.y < s.BoundBox.YMax - 0.01 and m.z > s.BoundBox.ZMin + 0.01 and abs(m.z - zi_val) > 0.01

    body_r = F.fillet(doc, "SkiBody", body_sq, 2.5, roundable)
    ski_slot = slot("Ski", 0, f"{zb} - 1", f"{z2} + 0.5")
    stakes = [F.cyl(doc, f"SkiStake{i}", f"{P}stake_d / 2", f"{P}ski_h + 2", 0, -1, f"{zc} + {P}{k}", F.X, -90)
              for i, k in enumerate(("stake_1", "stake_2"))]
    # A shell (Rob, 15 Nov 2026: 750g a tree was too much): two cavities side by side, open to
    # the sole, with a web between them, under the slot and all along the taper. Walls hol_wall,
    # a skin over the cavities, slot_wall round the slot, a tube round each stake.
    ys = f"({P}dt_h + {P}clr + {P}slot_wall)"                  # under the slot's floor
    z_after = f"({P}rail_half + 0.5 + {P}slot_wall)"           # past the slot's closed end
    zz = f"{P}half_l - 6"
    hollows = []
    for i, sgn in enumerate((-1, 1)):
        def xs(w):                                            # the cavity's x range in a ski w wide
            lo, hi = f"{P}hol_wall / 2", f"{w} / 2 - {P}hol_wall"
            return (lo, hi) if sgn > 0 else (f"-({hi})", f"-{lo}")
        x0, x1 = xs(f"{P}ski_w")
        hollows.append(F.box(doc, f"SkiUnderSlot{i}", f"{x1} - ({x0})", f"{P}ski_h - {ys} + 1",
                             f"{P}inner_l - {P}butt_gap - {P}slot_wall + 0.5", x0, ys, f"{zb} + {P}slot_wall"))
        hollows.append(F.box(doc, f"SkiPastSlot{i}", f"{x1} - ({x0})", f"{ys} - 0.3 - {P}skin + 0.5",
                             f"{P}inner_l - {z_after} + 0.5", x0, f"0.3 + {P}skin", f"{zc} + {z_after}"))
        xa, xb = xs(width(P + "inner_l"))
        x2a, x2b = xs(width(zz))
        hollows.append(F.wedge(doc, f"SkiHollow{i}", xa, xb, zi, f"{zc} + {zz}",
                               f"-{P}ski_h - 1", f"-(0.3 + {P}skin)", x2a, x2b,
                               f"-{P}ski_h - 1", f"-({top_y(zz)} + {P}skin)", 0, 0, 0, F.X, 90))
    shell = F.cut(doc, "SkiShell", body_r, hollows)
    bosses = [F.cyl(doc, f"SkiBoss{i}", f"{P}stake_d / 2 + {P}hol_wall", f"{P}ski_h", 0, 0.3, f"{zc} + {P}{k}", F.X, -90)
              for i, k in enumerate(("stake_1", "stake_2"))]
    # the tubes are trimmed to the ski's outline (its top slopes down towards the outer end)
    tubes = F.common(doc, "SkiTubes", F.fuse(doc, "SkiTubesRaw", bosses), body_r)
    bossed_in = F.fuse(doc, "SkiBossed", [shell, tubes])
    F.cut(doc, "SkiHalf", bossed_in, [ski_slot, *stakes])

    # --- storage tower / show riser
    z0 = f"-({P}tree_t + {P}below)"
    col = F.box(doc, "TowerColumn", f"{P}col_w", f"{P}col_d", f"{P}pitch", f"-{P}col_w / 2", 0.3, z0)
    doc.recompute()
    col_r = F.fillet(doc, "TowerColumnR", col, 5.0, lambda e, s: through(F.direction(e)))
    doc.recompute()
    col_c = F.chamfer(doc, "TowerColumnC", col_r, 1.0,
                      lambda e, s: not through(F.direction(e)) and (F.mid(e).z < s.BoundBox.ZMin + 0.01
                                                                     or F.mid(e).z > s.BoundBox.ZMax - 0.01))
    tower_slot = slot("Tower", 0, f"{z1} - 0.5", f"{z0} + {P}pitch + 1")     # stopped at the bottom, open at the top
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
    roof_t = F.wedge(doc, "TowerBoreStep", f"-{bw} / 2", f"{bw} / 2", 0, step, f"-{bd} / 2", f"{bd} / 2",
                     f"-{iw} / 2", f"{iw} / 2", f"-{idp} / 2", f"{idp} / 2",
                     0, yc, f"{z0} + {P}pitch - {step}", F.X, 90)
    hole = F.box(doc, "TowerSpigotBore", iw, idp, f"{P}spig_h + 2",
                 f"-{iw} / 2", f"{yc} - {idp} / 2", f"{z0} + {P}pitch - 1")
    out_rail = rail("TowerOut", f"{P}y_out")
    # the outer rail's bottom end overhangs as the tower prints upright: cut it back at 45 deg
    under = F.box(doc, "TowerRailUnder", f"{P}col_w + 2", 40, 40,
                  f"-{P}col_w / 2 - 1", f"{P}y_out + 0.01 + 40 * cos(45)", f"{z1} - 40 * sin(45)", F.X, 45)
    tower_solid = F.fuse(doc, "TowerSolid", [col_c, spigot, out_rail])
    # lighter: two vertical cores beside the bore, right through (they print as plain holes),
    # and a core under the slot's stop, open at the bottom
    cores = []
    for i, sgn in enumerate((-1, 1)):
        lo, hi = f"{bw} / 2 + {P}slot_wall", f"{P}col_w / 2 - {P}slot_wall"
        x0 = lo if sgn > 0 else f"-({hi})"
        cores.append(F.box(doc, f"TowerCore{i}", f"{hi} - ({lo})", f"{P}y_out - {P}slot_wall - ({P}dt_h + {P}clr + {P}slot_wall)",
                           f"{P}pitch + 2", x0, f"{P}dt_h + {P}clr + {P}slot_wall", f"{z0} - 1"))
    cores.append(F.box(doc, "TowerUnderSlot", f"{P}dt_root", f"{P}dt_h + {P}clr - {P}slot_wall - 0.3",
                       f"({z1} - 0.5 - {P}slot_wall) - ({z0}) + 1", f"-{P}dt_root / 2", f"0.3 + {P}slot_wall", f"{z0} - 1"))
    F.cut(doc, "Tower", tower_solid, [tower_slot, recess, bore, roof_t, hole, under, *cores])

    # Dovetail coupon: the inner 60mm of a ski half, to try the slide on a printed socket
    slab = F.box(doc, "CouponBox", f"{P}ski_w + 2", f"{P}ski_h + 2", f"{P}inner_l", f"-{P}ski_w / 2 - 1", -1, f"{zc}")
    F.common(doc, "DovetailCoupon", doc.getObject("SkiHalf"), slab)

    F.check(doc, ["Socket", "SkiHalf", "Tower", "DovetailCoupon"])
    return doc



# --------------------------------------------------------------------------- PSU cover

def psu_cover():
    """Terminal hood for Site A's S-400-12 with a fused, switched IEC C14 inlet (Rob,
    16 Nov 2026: the LRS-350-12 arrived as a 350-24, so the S-400-12 carries the show).
    Case 217 x 114 x 50 (Rob); the rest read off his photos of 16 Nov 2026 against a
    ruler: the terminals sit in an open recess at the end, the lid stopping about 20mm in
    (its vents start at about 29); facing them, left to right, ADJ, +V x 3, -V x 3, earth,
    N, L, earth about 38 from the L side and the first -V about 47; threaded M4 side holes
    32 in and 38 up on both sides (screws no more than about 3mm in); the fan is at the far
    end and the 115/230V switch about 150 along the ADJ side, both clear of the hood.
    The inlet sits in the ROOF over the mains side (Rob, 16 Nov 2026), and the 12V leads
    run straight off the terminals and out through the chamber's open 12V side and a
    notch in the end wall, so the hood slides on over them. Inlet: the 3-in-1 module
    drawing Rob sent (panel cut-out 47.3 x 27.4, two 3.5mm holes 40 apart across the
    27.4, flange 54.4 x 49.2, ~17mm behind the panel plus ~8mm tabs). The 15 Nov
    LRS-350-12 version is in git (edd7308)."""
    doc = F.new_doc("psu_cover")
    F.sheet(doc, [
        ("", None, "S-400-12 (Rob's case size; the rest read off his photos: check before printing)"),
        ("psu_l", 217, "length"),
        ("psu_w", 114, "across"),
        ("psu_h", 50, "height"),
        ("lid_x", 20, "the lid stops this far in from the end: the terminals are in the open recess"),
        ("side_x", 32, "threaded M4 side holes from the end, both sides (photos: slotted)"),
        ("side_z", 38, "and above the base"),
        ("slot_t", 2.5, "slot travel each way along the case"),
        ("slot_v", 0.75, "and up and down"),
        ("adj_x", 16, "+V ADJ pot: access slot over it (photos)"),
        ("adj_y", 102, ""),
        ("", None, "Hood: one height all through, so it prints standing on its end wall with no supports"),
        ("fit", 0.5, "gap a side round the case"),
        ("wall", 3, "M4 x 6 + washer through the wall leaves about 2mm in the case (3 max)"),
        ("roof_l", 26, "roof and full sides over the case: past the lid's edge, short of its vents (29)"),
        ("tab_l", 42, "side tabs run on to here, past the side holes"),
        ("tab_z0", 8, "tabs' bottom"),
        ("tab_z1", 44, "tabs' top, under the lid's side vents (43.5 up, from 34 along)"),
        ("cham_l", 56, "wiring chamber beyond the end (inside); floored on the mains side, open under the 12V side"),
        ("hood_h", 54, "outside height: just over the case (50 + fit + wall)"),
        ("rib_y", 42.5, "partition between earth (~38) and -V (~47), photos: mains side and 12V side"),
        ("rib_t", 2, ""),
        ("rib_in", 10, "the partition hangs on into the recess, above the terminal block"),
        ("rib_z", 25, "its bottom there (above the screw heads)"),
        ("m4_d", 4.5, "M4 clearance"),
        ("vent_l", 15, "vent slots in the 12V side wall only, over the case's own side vents"),
        ("vent_h", 2.5, "5 slots, 5mm apart from z = 14, from 7 along"),
        ("", None, "IEC inlet in the roof over the chamber's mains side (3-in-1 C14 + fuse + switch, Rob's drawing)"),
        ("iec_x", -26.5, "centre along the hood: body in the chamber, flange on the flat of the roof"),
        ("iec_y", 26.5, "centre across: body on the mains side of the partition, flange clear of the edge round"),
        ("iec_cut_w", 27.4, "panel cut-out, across the hood"),
        ("iec_cut_h", 47.3, "panel cut-out, along the hood"),
        ("iec_hole_d", 3.4, "M3 x 10 + nyloc"),
        ("iec_hole_pitch", 40, "the two holes, either side of the cut-out across the hood"),
        ("", None, "12V out: the leads go straight onto the terminals and out through a notch in the end wall"),
        ("dc_w", 50, "notch width, on the 12V side, open at the bottom"),
        ("dc_y", 80, "notch centre"),
        ("dc_h", 22, "notch height"),
    ])
    P = "params."
    yl = f"-({P}fit + {P}wall)"
    W = f"{P}psu_w + 2 * ({P}fit + {P}wall)"
    x0 = f"-({P}cham_l + {P}wall)"
    zin = f"{P}hood_h - {P}wall"
    outer = F.box(doc, "Outer", f"{P}cham_l + {P}wall + {P}tab_l", W, f"{P}hood_h", x0, yl, 0)
    over_in = F.box(doc, "OverIn", f"{P}tab_l + 1.01", f"{P}psu_w + 2 * {P}fit", f"{zin} + 1",
                    -0.01, f"-{P}fit", -1)
    cham_in = F.box(doc, "ChamberIn", f"{P}cham_l + 0.02", f"{P}psu_w + 2 * {P}fit", f"{zin} - {P}wall",
                    f"-{P}cham_l", f"-{P}fit", f"{P}wall")
    # the tabs: past the roof only the side walls go on, from tab_z0 to tab_z1
    tab_top = F.box(doc, "TabTop", f"{P}tab_l - {P}roof_l + 1", f"{W} + 2", f"{P}hood_h", f"{P}roof_l",
                    f"{yl} - 1", f"{P}tab_z1")
    tab_low = F.box(doc, "TabLow", f"{P}tab_l - {P}roof_l + 1", f"{W} + 2", f"{P}tab_z0 + 1", f"{P}roof_l",
                    f"{yl} - 1", -1)
    rib = F.box(doc, "Rib", f"{P}cham_l - {P}fit + 0.01", f"{P}rib_t", f"{zin} - {P}wall + 0.02",
                f"-{P}cham_l - 0.01", f"{P}rib_y - {P}rib_t / 2", f"{P}wall - 0.01")
    rib_hang = F.box(doc, "RibHang", f"{P}rib_in + {P}fit + 1", f"{P}rib_t", f"{zin} - {P}rib_z + 0.01",
                     f"-{P}fit - 1", f"{P}rib_y - {P}rib_t / 2", f"{P}rib_z")
    # slotted M4 holes (the hole positions are estimates): a stadium either side
    sr = f"({P}m4_d / 2 + {P}slot_v)"
    slots = []
    for i, y in enumerate((f"{yl} - 1", f"{P}psu_w - 1")):
        slots += [F.cyl(doc, f"Slot{i}{j}", sr, f"{P}wall + 2", f"{P}side_x {s} {P}slot_t", y, f"{P}side_z", F.X, -90)
                  for j, s in enumerate("-+")]
        slots.append(F.box(doc, f"Slot{i}", f"2 * {P}slot_t", f"{P}wall + 2", f"2 * {sr}",
                           f"{P}side_x - {P}slot_t", y, f"{P}side_z - {sr}"))
    vents = [F.box(doc, f"Vent{i}", f"{P}vent_l", f"{P}wall + 2", f"{P}vent_h",
                   7, f"{P}psu_w + {P}fit - 1", f"14 + {i} * 5") for i in range(5)]
    adj = F.box(doc, "AdjSlot", 6, 16, f"{P}wall + 2", f"{P}adj_x - 3", f"{P}adj_y - 8", f"{zin} - 1")
    # the inlet, in the roof: cut-out 27.4 across, 47.3 along; holes across, either side
    iec = F.box(doc, "IecCut", f"{P}iec_cut_h", f"{P}iec_cut_w", f"{P}wall + 2",
                f"{P}iec_x - {P}iec_cut_h / 2", f"{P}iec_y - {P}iec_cut_w / 2", f"{zin} - 1")
    iec_holes = [F.cyl(doc, f"IecHole{i}", f"{P}iec_hole_d / 2", f"{P}wall + 2",
                       f"{P}iec_x", f"{P}iec_y {s} {P}iec_hole_pitch / 2", f"{zin} - 1") for i, s in enumerate("-+")]
    # 12V side: no floor under the chamber, and a notch in the end wall open at the bottom
    floor12 = F.box(doc, "Floor12V", f"{P}cham_l + 0.02", f"{P}psu_w + {P}fit - {P}rib_y - {P}rib_t / 2 + 0.01",
                    f"{P}wall + 2", f"-{P}cham_l - 0.01", f"{P}rib_y + {P}rib_t / 2", -1)
    dc = F.box(doc, "DcNotch", f"{P}wall + 2", f"{P}dc_w", f"{P}dc_h + 1", f"{x0} - 1", f"{P}dc_y - {P}dc_w / 2", -1)
    # Nice to handle (Rob, 15 Nov 2026): 5mm rounds on every outside edge but the floor's,
    # a 0.8mm chamfer round the floor, and a lead-in where the roof slides over the PSU.
    doc.recompute()
    outer_r = F.fillet(doc, "OuterR", outer, 5.0, lambda e, s: F.mid(e).z > 0.5)
    doc.recompute()
    outer_c = F.chamfer(doc, "OuterC", outer_r, 0.8, lambda e, s: F.mid(e).z < 0.01)
    lead = F.wedge(doc, "LeadIn", f"-({P}psu_w + {P}fit)", f"{P}fit", f"{P}roof_l - 1.5", f"{P}roof_l + 0.01",
                   -1, f"{zin}", f"-({P}psu_w + {P}fit) - 1.5", f"{P}fit + 1.5", -1, f"{zin} + 1.5",
                   0, 0, 0, F.Z, -90)
    shell = F.cut(doc, "HoodShell", outer_c, [over_in, cham_in, lead, tab_top, tab_low])
    ribbed = F.fuse(doc, "HoodRibbed", [shell, rib, rib_hang])
    F.cut(doc, "Hood", ribbed, [*slots, *vents, adj, iec, *iec_holes, floor12, dc])

    # reference solids (not printed): the PSU and the inlet (body behind the panel, flange)
    ref_psu = F.box(doc, "RefPsu", f"{P}psu_l", f"{P}psu_w", f"{P}psu_h", 0, 0, 0)
    ref_iec = F.box(doc, "RefIec", f"{P}iec_cut_h", f"{P}iec_cut_w", 25,
                    f"{P}iec_x - {P}iec_cut_h / 2", f"{P}iec_y - {P}iec_cut_w / 2", f"{P}hood_h - 25")
    ref_flange = F.box(doc, "RefIecFlange", 54.4, 49.2, 4, f"{P}iec_x - 27.2", f"{P}iec_y - 24.6", f"{P}hood_h")
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
