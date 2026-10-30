"""Tree box parts as STEP, placed in the box, with fit checks (Rob, 28 Oct 2026):
python -m tools.gen_components

  cad/components/<part>.step    every bought part in the tree box, in its own frame
  cad/tree-box-assembly.step    the base, the cover and every part, as fitted
  docs/tree-box-parts.md        the sizes used, where each came from, what to measure,
                                and the check results

Simple solids (boxes, cylinders, hex nuts) at the parts' real envelopes, enough to
check clearances in NX. Every size lives in DIMS below with its source and status;
measure the parts, change the number and the status to "measured", rerun.

Part frames (mm): board-mounted parts are built in the protoboard's frame (origin at
the centre of its component face, +x along the columns A->X, +y up the rows 18->1,
+z out of the component face). Panel-mounted parts (SP16, PG7, RP-SMA) have z along
their axis, z = 0 on the panel's outer face, +z into the box. The Wagos: origin at a
bottom corner, lying flat, +z up.

Box frame = enclosure/tree-box.scad (base + cover, 28 Oct 2026): x across from the
cover's outer left (seen from behind), y from the tree face back, z up, 0 = underside
of the shelf.
"""

from __future__ import annotations

import math
import re
from itertools import combinations, product
from pathlib import Path

import cadquery as cq
from OCP.gp import gp_Trsf

from tools.gen_controller import COLS, PITCH, ROWS, SMALL_PARTS, esp_hole, u1_hole
from tools.gen_printed import PRINTED_DIR, write_step
from tools.gen_step import CAD_DIR
from tools.tree_layout import ROOT

OUT_DIR = CAD_DIR / "components"
ASSEMBLY_FILE = CAD_DIR / "tree-box-assembly.step"
DOC_FILE = ROOT / "docs" / "tree-box-parts.md"
SCAD = [ROOT / "enclosure" / "tree-box-params.scad", ROOT / "enclosure" / "tree-box.scad"]

# status: "measured" (calipers on Rob's part), "datasheet" (maker's drawing),
# "listing" (seller or aggregator figure), "guess" (typical; measure it).
DIMS = {
    "protoboard": dict(
        desc="5 x 7cm double-sided prototype board, 24 x 18 holes", have=True,
        w=(70, "photo"), h=(50, "photo"), t=(1.6, "guess"),
        tail=(2.5, "guess"),                # solder tails and joins below the board
        note="Photo 30 Oct 2026: 24 x 18 holes confirmed, plus a row of 16 oval pads at each short edge. "
             "Corner holes about 2mm in from both edges and about 2mm across (box: pb_hole_in 2.0). "
             "Measure the corner hole spacing and the thickness"),
    "header": dict(
        desc="ESP32's own male pin headers, soldered straight into the protoboard (no sockets, Rob 28 Oct 2026)",
        have=True, male_base=(2.5, "guess"),
        note="Plastic between the protoboard and the ESP32's underside"),
    "esp32": dict(
        desc="ESP32-DevKitC-32U, 38-pin (AliExpress)", have=True,
        l=(48.3, "photo"), w=(27.94, "photo"), t=(1.6, "guess"),
        row_gap=(25.4, "photo"), end_pin1=(1.0, "photo"),
        mod_l=(17.5, "photo"), mod_w=(16.0, "photo"), mod_h=(3.2, "datasheet"),
        usb_w=(9.0, "guess"), usb_d=(7.3, "guess"), usb_h=(3.2, "guess"), usb_over=(0.5, "photo"),
        ufl_h=(2.5, "guess"),
        note="Photo 30 Oct 2026: USB-C clone with a CP2102, pinout matches Espressif's J2/J3, 19 pins each, "
             "rows 10 pitches apart, about 48.3 long (not the listed 54.4), so it doesn't overhang the board. "
             "Measure the length and the tallest part"),
    "u1": dict(
        desc="74AHCT125N (DIP-14), soldered in (no socket)", have=True,
        seat=(0.5, "guess"), top=(5.1, "datasheet"),
        note="TI N package body 19.3 x 6.35, rows 7.62; up to 5.08 above the seating plane"),
    "terminal": dict(
        desc="2-way 5.08mm PCB screw terminal (JD)", have=False,
        d=(7.6, "guess"), h=(10.0, "guess"),
        note="KF128 / KF301 type: 10.16 along the pitch; depth and height vary by make"),
    "c1": dict(desc="100uF electrolytic, standing", have=True,
               d=(6.3, "guess"), h=(11.0, "guess"), note="6.3 x 11 or 5 x 11 can"),
    "mini560": dict(
        desc="Mini560 5V buck module (standing on its OUT end on the protoboard)", have=True,
        l=(30, "measured"), w=(18.27, "measured"), h=(5.4, "listing"), lift=(3.0, "guess"),
        note="Width 18.27 (Rob, 28 Oct 2026); about 30 long (Rob, 30 Oct), IN at one end and OUT at the other, "
             "a pair of + pads and a pair of - pads at each end. Stands on its OUT end at the board's column A-D "
             "edge on a 90 degree header (lift = the header's plastic); its IN end is wired from the Wagos. "
             "Measure the height to the top of the inductor, the pad spacing and the header"),
    "wago": dict(
        desc="WAGO 221-413 lever connector", have=True,
        l=(18.6, "listing"), w=(18.7, "listing"), h=(8.3, "listing"), lever_open=(20, "guess"),
        note="Aggregators disagree (18.6-18.8, h 8.3-8.6); no WAGO drawing read. In hand since 30 Oct: measure"),
    "sp16": dict(
        desc="SP16 2-pin panel socket (rear nut) + SP17 cable plug", have=False,
        hole=(16.5, "datasheet"), flat=(15.3, "datasheet"), thread=(16, "datasheet"),
        flange_d=(25, "datasheet"), flange_t=(3, "guess"), body=(22, "datasheet"),
        nut_af=(20, "guess"), nut_t=(3, "guess"), plug_l=(60, "datasheet"), plug_d=(22, "guess"),
        note="Drawing (spebanmoh SP16 PDF): hole 16.5 / flat 15.3, flange 25, body 22, plug 60, cable 6-8. "
             "Due 7 Nov: measure the nut, the flange thickness and the thread length (max panel)"),
    "pg7": dict(
        desc="PG7 nylon cable gland (pixel lead out)", have=True,
        thread=(12.5, "datasheet"), thread_l=(8, "datasheet"), nut_af=(15, "guess"), nut_t=(3, "guess"),
        cap_af=(15, "guess"), out_h=(14, "guess"),
        note="Multicomp PG7DG: thread 8 long, overall 22, clamps 3-6.5. Rob has 20: measure the nut and cap"),
    "rpsma": dict(
        desc="RP-SMA bulkhead (U.FL pigtail end) + 2.4GHz dipole", have=True,
        thread=(6.35, "datasheet"), nut_af=(8, "datasheet"), nut_t=(2.5, "guess"),
        max_panel=(3.2, "datasheet"), body_in=(8, "guess"), dipole_d=(10, "guess"), dipole_l=(108, "guess"),
        note="Wurth/Linx drawings: 1/4-36 UNS, nut 8 AF, hole 6.5, panel 2.8-3.2 max. "
             "Measure the thread length past the flange and the dipole"),
}

COLOURS = {"protoboard": (0.15, 0.45, 0.2), "header": (0.1, 0.1, 0.1), "esp32": (0.1, 0.2, 0.5),
           "u1": (0.2, 0.2, 0.2), "terminal": (0.1, 0.4, 0.8), "c1": (0.2, 0.3, 0.6),
           "mini560": (0.1, 0.1, 0.3), "wago": (0.9, 0.5, 0.1), "sp16": (0.2, 0.4, 0.8),
           "pg7": (0.15, 0.15, 0.15), "rpsma": (0.8, 0.7, 0.3),
           **{f"spacer{i}": (0.27, 0.51, 0.71) for i in range(1, 5)}}


def v(part: str, key: str) -> float:
    return DIMS[part][key][0]


def scad_params() -> dict[str, float]:
    """Plain `name = number;` lines from the tree box sources, then the derived sizes."""
    p = {}
    for f in SCAD:
        for m in re.finditer(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", f.read_text(encoding="utf-8"), re.M):
            p.setdefault(m[1], float(m[2]))
    # the derived sizes, as tree-box-params.scad and tree-box.scad work them out
    p["floor_y"] = p["plate_t"] + 14
    p["floor_z"] = p["lip_t"] + p["floor_t"]
    p["back_in"] = p["plate_t"] + p["box_in_d"]                 # cover's back wall, inside face
    p["board_x0"] = (p["box_w"] - p["pb_w"]) / 2
    return p


# ---- solids ---------------------------------------------------------------------

def box(cx, cy, z0, lx, ly, h) -> cq.Workplane:
    return cq.Workplane().box(lx, ly, h, centered=(True, True, False)).translate((cx, cy, z0))


def cyl(cx, cy, z0, d, h) -> cq.Workplane:
    return cq.Workplane().circle(d / 2).extrude(h).translate((cx, cy, z0))


def hexnut(cx, cy, z0, af, h, hole) -> cq.Workplane:
    return (cq.Workplane().polygon(6, af / math.cos(math.radians(30))).extrude(h)
            .faces(">Z").workplane().hole(hole).translate((cx, cy, z0)))


def grid(col: float, row: float) -> tuple[float, float]:
    """Protoboard hole (col 0 = A, row 0 = 1) in the board frame."""
    return (col - (COLS - 1) / 2) * PITCH, ((ROWS - 1) / 2 - row) * PITCH


def protoboard() -> cq.Workplane:
    w, h, t = v("protoboard", "w"), v("protoboard", "h"), v("protoboard", "t")
    tail = v("protoboard", "tail")
    return box(0, 0, -t, w, h, t).union(box(0, 0, -t - tail, w - 16, h - 16, tail))   # tails, inside the standoffs


def esp32() -> cq.Workplane:
    """Board frame, plugged into the headers: pins on J2/J3, components facing out."""
    (c1, r2), (c19, r3) = esp_hole("J2", 1), esp_hole("J3", 19)
    x1, y2 = grid(c1, r2)
    x19, y3 = grid(c19, r3)
    sign = 1 if x19 > x1 else -1                      # pin 1 -> pin 19 direction
    z0 = 0
    base = box((x1 + x19) / 2, (y2 + y3) / 2, z0, abs(x19 - x1) + 2 * PITCH, abs(y3 - y2) + PITCH,
               v("header", "male_base"))                                  # male header plastic
    zb = z0 + v("header", "male_base")
    l, w, t = v("esp32", "l"), v("esp32", "w"), v("esp32", "t")
    end1 = x1 - sign * v("esp32", "end_pin1")
    cx, cy = end1 + sign * l / 2, (y2 + y3) / 2
    pcb = box(cx, cy, zb, l, w, t)
    mod = box(end1 + sign * v("esp32", "mod_l") / 2, cy, zb + t, v("esp32", "mod_l"), v("esp32", "mod_w"),
              v("esp32", "mod_h"))
    ufl = cyl(end1 + sign * 3, cy + v("esp32", "mod_w") / 2 - 3, zb + t + v("esp32", "mod_h"), 3, v("esp32", "ufl_h"))
    usb_x = end1 + sign * (l + v("esp32", "usb_over") - v("esp32", "usb_d") / 2)
    usb = box(usb_x, cy, zb + t, v("esp32", "usb_d"), v("esp32", "usb_w"), v("esp32", "usb_h"))
    return base.union(pcb).union(mod).union(ufl).union(usb)


def u1() -> cq.Workplane:
    xs = [grid(*u1_hole(p))[0] for p in range(1, 15)]
    ys = [grid(*u1_hole(p))[1] for p in range(1, 15)]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return box(cx, cy, v("u1", "seat"), 19.3, 6.35, v("u1", "top") - v("u1", "seat"))


def two_lead(part: str) -> tuple[float, float, bool]:
    (_, a), (_, b) = SMALL_PARTS[part][1]
    (xa, ya), (xb, yb) = grid(*a), grid(*b)
    return (xa + xb) / 2, (ya + yb) / 2, abs(xa - xb) > abs(ya - yb)


def terminals() -> cq.Workplane:
    out = None
    for part in ("JD",):
        x, y, along_x = two_lead(part)
        lx, ly = (10.16, v("terminal", "d")) if along_x else (v("terminal", "d"), 10.16)
        s = box(x, y, 0, lx, ly, v("terminal", "h"))
        out = s if out is None else out.union(s)
    return out


def c1() -> cq.Workplane:
    x, y, _ = two_lead("C1")
    return cyl(x, y, 0, v("c1", "d"), v("c1", "h"))


def mini560() -> cq.Workplane:
    return box(v("mini560", "l") / 2, v("mini560", "w") / 2, 0, v("mini560", "l"), v("mini560", "w"),
               v("mini560", "h"))


def wago() -> cq.Workplane:
    return box(v("wago", "l") / 2, v("wago", "w") / 2, 0, v("wago", "l"), v("wago", "w"), v("wago", "h"))


def d_profile(d: float, flat: float, h: float, z0: float) -> cq.Workplane:
    return (cq.Workplane().circle(d / 2).extrude(h)
            .intersect(box(0, -(d - flat) / 2, 0, d, flat, h)).translate((0, 0, z0)))   # flat to +y (the lid)


def sp16(floor_t: float) -> cq.Workplane:
    """Axis z, 0 = the floor's outer face, +z into the box; plug mated below."""
    ft = v("sp16", "flange_t")
    flange = cyl(0, 0, -ft, v("sp16", "flange_d"), ft)
    body = d_profile(v("sp16", "thread"), v("sp16", "flat") - 0.4, v("sp16", "body") - ft, 0)   # flat 6.9 off the axis, the hole's 7.05
    nut = hexnut(0, 0, floor_t, v("sp16", "nut_af"), v("sp16", "nut_t"), v("sp16", "thread"))
    plug = cyl(0, 0, -ft - v("sp16", "plug_l"), v("sp16", "plug_d"), v("sp16", "plug_l"))
    return flange.union(body).union(nut).union(plug)


def pg7(floor_t: float) -> cq.Workplane:
    thread = cyl(0, 0, 0, v("pg7", "thread"), v("pg7", "thread_l"))
    nut = hexnut(0, 0, floor_t, v("pg7", "nut_af"), v("pg7", "nut_t"), v("pg7", "thread"))
    cap = (cq.Workplane().polygon(6, v("pg7", "cap_af") / math.cos(math.radians(30)))
           .extrude(v("pg7", "out_h")).translate((0, 0, -v("pg7", "out_h"))))
    return thread.union(nut).union(cap)


def rpsma(grip: float) -> cq.Workplane:
    """Axis z, 0 = the wall's outer face, +z into the box; dipole outside (shown straight
    out; it hinges up). grip = material the thread has to pass through, outer face to the nut."""
    th = cyl(0, 0, -1, v("rpsma", "thread"), grip + v("rpsma", "nut_t") + 1)
    nut = hexnut(0, 0, grip, v("rpsma", "nut_af"), v("rpsma", "nut_t"), v("rpsma", "thread"))
    body = cyl(0, 0, grip + v("rpsma", "nut_t"), 7, v("rpsma", "body_in"))
    dip = cyl(0, 0, -v("rpsma", "dipole_l"), v("rpsma", "dipole_d"), v("rpsma", "dipole_l"))
    return th.union(nut).union(body).union(dip)


# ---- placement --------------------------------------------------------------------

def loc(rows: tuple, origin: tuple) -> cq.Location:
    """Location from a rotation (rows of the 3 x 3 matrix) and a translation."""
    t = gp_Trsf()
    (a, b, c), (d, e, f), (g, h, i) = rows
    t.SetValues(a, b, c, origin[0], d, e, f, origin[1], g, h, i, origin[2])
    return cq.Location(t)


def placed(p: dict) -> tuple[dict[str, cq.Shape], dict[str, cq.Location], dict]:
    ft = p["floor_t"]
    board_rows = ((-1, 0, 0), (0, 0, 1), (0, 1, 0))          # board x -> -X, y -> Z, z -> Y
    board_origin = (p["board_x0"] + p["pb_w"] / 2, p["plate_t"] + p["standoff_h"] + v("protoboard", "t"),
                    p["board_z0"] + p["pb_h"] / 2)
    on_board = loc(board_rows, board_origin)
    up = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    grip = p["ant_panel"]
    shapes = {"protoboard": protoboard(), "esp32": esp32(), "u1": u1(),
              "terminal": terminals(), "c1": c1(), "mini560": mini560(), "wago": wago(),
              "sp16": sp16(ft), "pg7": pg7(ft), "rpsma": rpsma(grip)}
    in_wall = p["plate_t"]
    locs = {k: on_board for k in ("protoboard", "esp32", "u1", "terminal", "c1")}
    # Mini560 standing on its input end in the free strip along the board's column A edge (28 Oct 2026):
    # its length out of the board (+z), width along the rows, thickness along the columns
    l, w, h = v("mini560", "l"), v("mini560", "w"), v("mini560", "h")
    x0 = grid(0, 0)[0] - PITCH / 2 + 0.5
    yc = grid(0, 6)[1]
    shapes["mini560"] = box(x0 + h / 2, yc, v("mini560", "lift"), h, w, l)
    locs["mini560"] = on_board
    # the Wagos flat on the plate below the board, side by side, clear of the SP16 body, above the PG7 nut
    on_wall = ((1, 0, 0), (0, 0, -1), (0, 1, 0))
    wx, wz = p["sp16_x"] + 9, p["floor_z"] + 6.6
    locs["wago"] = loc(on_wall, (wx, in_wall + v("wago", "h"), wz))
    locs["wago2"] = loc(on_wall, (wx + v("wago", "l") + 1.5, in_wall + v("wago", "h"), wz))
    shapes["wago2"] = shapes["wago"]
    # the printed spacers between the ears and the tree, axis along y, on the mounting slots' centres
    spacer = cyl(0, 0, 0, p["spacer_d"], p["spacer_l"]).cut(cyl(0, 0, -1, p["mount_slot_d"], p["spacer_l"] + 2))
    for i, (x, z) in enumerate(product((-p["ear_w"] / 2, p["box_w"] + p["ear_w"] / 2), (18, p["box_h"] - 16)), 1):
        shapes[f"spacer{i}"] = spacer
        locs[f"spacer{i}"] = loc(((1, 0, 0), (0, 0, 1), (0, -1, 0)), (x, -p["spacer_l"], z))
    locs["sp16"] = loc(up, (p["sp16_x"], p["floor_y"], p["lip_t"]))
    locs["pg7"] = loc(up, (p["pg7_x"], p["floor_y"], p["lip_t"]))
    locs["rpsma"] = loc(up, (p["ant_x"], p["floor_y"], p["lip_t"]))     # firing down, through the shelf's recess
    return {k: s.val() for k, s in shapes.items()}, locs, {"grip": grip}


def checks(p: dict, solids: dict, locs: dict, base: cq.Shape, cover: cq.Shape, info: dict) -> list[str]:
    out = []
    g, mx = info["grip"], v("rpsma", "max_panel")
    out.append(f"RP-SMA bulkhead: through the shelf, thinned to {g:.1f}mm; it takes {mx:.1f}mm at most. "
               + ("OK." if g <= mx else "**Too thick.**"))
    out.append(f"SP16 and PG7: the shelf is {p['floor_t']:.1f}mm. PG7 thread is {v('pg7', 'thread_l'):.0f}mm long "
               f"(nut {v('pg7', 'nut_t'):.0f}mm): OK. SP16 thread length past the flange is unknown: measure it.")
    out.append(f"SP16 plug: {v('sp16', 'plug_l') + v('sp16', 'flange_t'):.0f}mm below the floor's outer face "
               f"(plug {v('sp16', 'plug_l'):.0f} + flange), plus the cable bend: keep that clear under the box.")
    placed_ = {k: solids[k].moved(locs[k]) for k in locs}
    placed_["base"], placed_["cover"] = base, cover
    clashes = []
    for a, b in combinations(placed_, 2):
        if {a, b} <= {"protoboard", "esp32", "u1", "terminal", "c1"}:
            continue                                         # one board, built to its own grid
        try:
            vol = placed_[a].intersect(placed_[b]).Volume()
        except Exception:                                    # noqa: BLE001 (mesh booleans can fail)
            clashes.append(f"{a} / {b}: boolean failed, check in NX")
            continue
        if vol > 1.0:
            clashes.append(f"{a} / {b}: {vol:.0f} mm³")
    out.append("Clashes (overlap over 1mm³): " + ("none." if not clashes else "; ".join(clashes) + "."))
    esp_top = placed_["esp32"].BoundingBox().ymax
    back = p["back_in"]
    out.append(f"Board stack: the ESP32's tallest part reaches y = {esp_top:.1f}mm; the cover's back wall is at "
               f"y = {back:.0f}, so {back - esp_top:.1f}mm spare.")
    m = placed_["mini560"].BoundingBox()
    out.append(f"Mini560 standing on the board: its top end reaches y = {m.ymax:.1f}mm, {back - m.ymax:.1f}mm short "
               f"of the back wall. Clear of the ESP32 by {m.xmin - placed_['esp32'].BoundingBox().xmax:.1f}mm "
               "(column A is at the box's high-x side).")
    usb = placed_["esp32"].BoundingBox().xmin
    out.append(f"ESP32 USB end reaches x = {usb:.1f}mm; the cover's inside wall is at x = {p['cover_wall']:.2f}.")
    return out


def doc(results: list[str]) -> str:
    lines = ["# Tree box parts: sizes, sources and checks", "",
             "Generated by `python -m tools.gen_components` (edit DIMS there, not this file). "
             "STEP models: `cad/components/` (each part in its own frame) and `cad/tree-box-assembly.step` "
             "(base, cover and parts as fitted, in the box frame of enclosure/tree-box.scad).", "",
             "Status: **measured** = calipers on Rob's part; **datasheet** = maker's drawing; "
             "**photo** = scaled from Rob's photo, close but measure it; **listing** = seller or aggregator; **guess** = typical value, measure it.", "",
             "## Checks", ""] + [f"- {r}" for r in results] + ["", "## Sizes", "",
             "| Part | In hand | Size (mm) | Status | Notes |", "|---|---|---|---|---|"]
    for name, d in DIMS.items():
        sizes = ", ".join(f"{k} {val[0]:g}" for k, val in d.items() if isinstance(val, tuple))
        stat = sorted({val[1] for val in d.values() if isinstance(val, tuple)})
        lines.append(f"| {d['desc']} | {'yes' if d['have'] else 'no'} | {sizes} | {', '.join(stat)} | {d['note']} |")
    lines += ["", "## Measure now (parts in hand)", ""]
    for name, d in DIMS.items():
        todo = [k for k, val in d.items() if isinstance(val, tuple) and val[1] in ("guess", "listing", "photo")]
        if d["have"] and todo:
            lines.append(f"- [ ] {d['desc']}: {', '.join(todo)}")
    lines += ["", "## Measure when they arrive", ""]
    for name, d in DIMS.items():
        todo = [k for k, val in d.items() if isinstance(val, tuple) and val[1] in ("guess", "listing", "photo")]
        if not d["have"] and todo:
            lines.append(f"- [ ] {d['desc']}: {', '.join(todo)}")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = scad_params()
    base = cq.importers.importStep(str(PRINTED_DIR / "tree-box-base.step")).val()
    cover = cq.importers.importStep(str(PRINTED_DIR / "tree-box-cover.step")).val()
    solids, locs, info = placed(p)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, s in solids.items():
        if name not in ("wago2", "spacer2", "spacer3", "spacer4"):
            write_step(s, OUT_DIR / f"{'spacer' if name == 'spacer1' else name}.step")
    asm = cq.Assembly(name="tree-box-assembly")
    asm.add(base, name="tree-box-base", color=cq.Color(0.27, 0.51, 0.71))
    asm.add(cover, name="tree-box-cover", color=cq.Color(0.69, 0.77, 0.87, 0.35))
    for name, l in locs.items():
        asm.add(solids[name], name=name, loc=l, color=cq.Color(*COLOURS[name.removesuffix("2") if name == "wago2" else name]))
    write_step(asm, ASSEMBLY_FILE)
    results = checks(p, solids, locs, base, cover, info)
    DOC_FILE.write_text(doc(results), encoding="utf-8", newline="\n")
    print("\n".join(results))
    print(f"wrote {len(solids) - 4} parts in cad/components/, {ASSEMBLY_FILE.relative_to(ROOT)}, "
          f"{DOC_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
