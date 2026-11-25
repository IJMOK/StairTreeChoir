"""Milled tree controller PCB (Rob, 25 Nov 2026): the protoboard circuit on single-sided 1.2mm FR4,
cut 6-up on the PrintNC from copper clad held down with double-sided tape, ALL WITH ONE 1.0mm FLAT
END MILL (Rob: "going to have to do it all with a 1mm bit in one pass").

  python -m tools.gen_pcb          (make all runs it too)

writes electronics/pcb/:
  cam/tree-pcb-6up-1mm.nc     the whole job in one file: isolation, label, holes, cut-out, 6 boards
  cam/0_air_frame.nc          spindle off, traces the job's footprint 5mm above the sheet (placement check)
  cam/1_isolation_1mm.nc      the same job in parts, to re-run one step: one pass round every copper area
  cam/2_drill_1mm.nc          every hole (pecked; JD and the fixing holes bored helically)
  cam/3_outline_1mm.nc        cuts the 6 boards out, no tabs (the tape holds them)
  gerber/                     the board as Gerber + Excellon, for a viewer or other CAM
  board-*.svg, panel.svg      drawings; checks.md: the design and the G-code checked against the netlist

Isolation is one pass of the 1mm cutter round every signal track, every pad and every unused pad,
0.5mm out, so nets are exactly 1.0mm apart; all the copper that's left is one GND pour. That rule
sets the pads: 1.5mm wide where pins are 2.54 apart (oval, longer the other way), so the board is
re-routed, not the protoboard's wiring.

Kept from the 5 x 7cm protoboard: the 70 x 50 outline, the 4 fixing holes (2.0 in from each edge, the
tree box's pb_hole_in) and the holes of the ESP32, U1 and the Mini560, so the box and its fit checks
don't change. R1, R2, C1, C2 and JD sit wherever the 1mm rules let the tracks through.

Frames: "component view" = the protoboard drawing (component side, antenna end left, x right, y up,
origin at the board's bottom-left corner). The copper is milled face up, so the CNC sees it mirrored:
x_cnc = BOARD_W - x. G-code zero: X0 Y0 = the panel's bottom-left corner (board A's corner),
Z0 = the top of the copper.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from tools.gen_controller import COLS, J2, J3, PITCH, ROWS, U1_PINS, esp_hole, u1_hole
from tools.tree_layout import ROOT

OUT = ROOT / "electronics" / "pcb"

# ---- board (identical to the protoboard and to the box's params: pb_w, pb_h, pb_hole_in) ----
BOARD_W, BOARD_H = 70.0, 50.0
HOLE_IN = 2.0            # fixing hole centres in from both edges (tree-box params pb_hole_in)
FIX_HOLE_D = 2.2         # M2 x 6 into the standoffs' heat-set inserts; 2.2 clears an M2
INSERT_KEEP = 2.5        # no signal copper this close to a fixing hole's centre (brass insert, screw)
THICK = 1.2              # FR4 sheet
GRID_X0 = (BOARD_W - (COLS - 1) * PITCH) / 2    # the hole grid is centred, as in tools/cad_components.grid()
GRID_Y0 = (BOARD_H - (ROWS - 1) * PITCH) / 2

# ---- the one tool and how it cuts (PrintNC, 18,000 rpm like the tread job) ----
EM_D = 1.0                         # flat 2-flute carbide end mill: isolation, label, holes, cut-out
R = EM_D / 2
CLEAR = EM_D                       # copper to copper between nets = one pass of the cutter
SLIVER = 0.5                       # pour narrower than this gets its own pass (no loose fingers of copper)
ISO_DEPTH = 0.20                   # through 35um copper; a flat cutter's width doesn't change with depth
ISO_FEED, ISO_PLUNGE = 350, 60
EM_DEPTH = THICK + 0.3             # holes and cut-out: through the board, into the tape
EM_PECK = 0.75
EM_PLUNGE, EM_HELIX_FEED, EM_FEED = 60, 150, 300
EM_STEPDOWN = 0.5                  # cut-out passes (3 to 1.5)
RPM = 18000
Z_SAFE, Z_CLEAR = 3.0, 15.0
Z_HOP, HOP_MAX = 1.0, 20.0         # short hops between isolation loops stay 1mm up
Z_APPROACH = 0.3                   # rapids stop this far above the copper

# ---- panel: 2 across x 3 up, 4mm between boards (the cut-out paths leave a 2mm web) ----
PANEL_COLS, PANEL_ROWS, PANEL_GAP = 2, 3, 4.0

W_5V, W_SIG = 0.8, 0.6   # track widths


def cut_width() -> float:
    return EM_D


# ------------------------------------------------------------------ geometry in the component view
def gxy(col: float, row: float) -> tuple[float, float]:
    """Protoboard grid (col 0 = A, row 0 = 1) -> component-view mm."""
    return GRID_X0 + col * PITCH, BOARD_H - (GRID_Y0 + row * PITCH)


@dataclass
class Pad:
    ref: str            # e.g. "U1.14 VCC"
    net: str
    x: float            # hole centre, component view
    y: float
    w: float = 2.0      # copper across (x) and along (y); equal = round, else a stadium
    h: float = 2.0
    dy: float = 0.0     # copper centre offset from the hole (ovals reach inwards, away from the next row)
    hole: float = 1.0

    @property
    def xy(self) -> tuple[float, float]:
        return self.x, self.y

    def shape(self) -> Polygon:
        cx, cy = self.x, self.y + self.dy
        if abs(self.w - self.h) < 1e-9:
            return Point(cx, cy).buffer(self.w / 2, quad_segs=16)
        r = min(self.w, self.h) / 2
        if self.h > self.w:
            seg = LineString([(cx, cy - self.h / 2 + r), (cx, cy + self.h / 2 - r)])
        else:
            seg = LineString([(cx - self.w / 2 + r, cy), (cx + self.w / 2 - r, cy)])
        return seg.buffer(r, quad_segs=16)

    def ring(self) -> float:
        """Thinnest copper between the hole and the pad's edge."""
        sx, sy = self.w / 2, self.h / 2
        return min(sx, sy - abs(self.dy)) - self.hole / 2


PIN_W, PIN_L, PIN_IN = 1.5, 2.3, 0.4    # 2.54-pitch pins: 1.5 wide, 2.3 long, reaching 0.4 inwards

# Where the parts the 1mm rules moved now sit (component view, mm). The ESP32, U1 and Mini560 are on
# the protoboard grid (tools/gen_controller.py).
POS = {
    "R1.1": (44.5, 10.5), "R1.2": (54.66, 10.5),        # 33R lying, 10.16 pitch
    "R2.1": (16.2, 20.5), "R2.2": (13.66, 20.5),        # 10k standing, 2.54 pitch, below the Mini560's end
    "C1.+": (49.0, 3.81), "C1.-": (49.0, 6.35),         # 100uF, 2.54 pitch, on the 5V run (6.3 can clears R1)
    "C2.5V": (41.5, 3.81), "C2.GND": (41.5, 11.43),     # 0.1uF, 7.62 pitch (bend the leads), clear of U1's body
    "JD.DATA": (58.5, 10.5), "JD.GND": (63.58, 10.5),   # 5.08 screw terminal, wire entries to the bottom edge
}


def pads() -> list[Pad]:
    out = []
    for header, names in (("J3", J3), ("J2", J2)):
        for i, name in enumerate(names, 1):
            if name == "GND":
                net = "GND"
            elif (header, i) == ("J3", 12):
                net = "DATA3"
            elif (header, i) == ("J2", 19):
                net = "5V"
            else:
                net = f"nc:{header}.{i}"
            x, y = gxy(*esp_hole(header, i))
            out.append(Pad(f"{header}.{i} {name}", net, x, y, PIN_W, PIN_L, -PIN_IN if header == "J3" else PIN_IN))
    u1_net = {1: "GND", 2: "DATA3", 3: "DATA5", 4: "GND", 5: "GND", 7: "GND", 9: "GND", 10: "GND",
              12: "GND", 13: "GND", 14: "5V"}
    for p, name in U1_PINS.items():
        x, y = gxy(*u1_hole(p))
        out.append(Pad(f"U1.{p} {name}", u1_net.get(p, f"nc:U1.{p}"), x, y, PIN_W, PIN_L, -PIN_IN if p <= 7 else PIN_IN))
    # Mini560 on its 90 degree header, both pins of each pair (electronics/README.md: C4+C5, C8+C9)
    for ref, net, row in (("M.OUT+a", "5V", 3), ("M.OUT+b", "5V", 4), ("M.OUT-a", "GND", 7), ("M.OUT-b", "GND", 8)):
        out.append(Pad(ref, net, *gxy(2, row)))
    nets = {"R1.1": "DATA5", "R1.2": "DATAOUT", "R2.1": "DATA3", "R2.2": "GND", "C1.+": "5V", "C1.-": "GND",
            "C2.5V": "5V", "C2.GND": "GND", "JD.DATA": "DATAOUT", "JD.GND": "GND"}
    for ref, (x, y) in POS.items():
        if ref.startswith("R2"):
            out.append(Pad(ref, nets[ref], x, y, PIN_W, PIN_L))          # pair along x: narrow in x
        elif ref.startswith("C1"):
            out.append(Pad(ref, nets[ref], x, y, PIN_L, PIN_W))          # pair along y: narrow in y
        elif ref.startswith("JD"):
            out.append(Pad(ref, nets[ref], x, y, 2.6, 2.6, hole=1.4))
        else:
            out.append(Pad(ref, nets[ref], x, y))
    return out


def pad(ref: str) -> Pad:
    return next(p for p in pads() if p.ref.split()[0] == ref)


def pc(ref: str) -> tuple[float, float]:
    """A pad's copper centre (where a track should end)."""
    p = pad(ref)
    return p.x, p.y + p.dy


# net -> [(width, [(x, y), ...]), ...], component view mm
TRACKS = {
    "5V": [(W_5V, [pc("M.OUT+a"), pc("M.OUT+b")]),
           # up from the Mini560, along the top edge, down the USB end to J2.19, then along the bottom to U1.14
           (W_5V, [pc("M.OUT+a"), (10.87, 45.5), (66.4, 45.5), (66.4, 6.5), (64.5, 3.81), pc("U1.14")]),
           (W_5V, [(66.4, pc("J2.19")[1]), pc("J2.19")])],
    # IO16: down under the ESP32, round its antenna end (past R2), along under J2 and down into U1.2 (1A)
    "DATA3": [(W_SIG, [pc("J3.12"), (pc("J3.12")[0], 34.5), (16.2, 34.5), (16.2, 13.57),
                       (pc("U1.2")[0], 13.57), pc("U1.2")])],
    # U1.3 (1Y) down between U1's rows and out past U1.1/U1.14 to R1
    "DATA5": [(W_SIG, [pc("U1.3"), (pc("U1.3")[0], 8.1), (pc("R1.1")[0], 8.1), pc("R1.1")])],
    "DATAOUT": [(W_SIG, [pc("R1.2"), pc("JD.DATA")])],
}

# Grooved into the pour, reading the right way from the copper side (CNC view), 1mm strokes, no
# closed shapes (they'd leave floating copper): "ANT ---->" pointing at the ESP32's antenna end.
LABEL_STROKES = [
    [(12, 23), (14, 28), (16, 23)],                       # A (no bar)
    [(18.5, 23), (18.5, 28), (22.5, 23), (22.5, 28)],     # N
    [(25, 28), (29.5, 28)], [(27.25, 28), (27.25, 23)],   # T
    [(33, 25.5), (47, 25.5)], [(44, 28), (47, 25.5), (44, 23)],   # arrow
]


def fix_holes() -> list[tuple[float, float]]:
    i = HOLE_IN
    return [(i, i), (BOARD_W - i, i), (i, BOARD_H - i), (BOARD_W - i, BOARD_H - i)]


def track_shapes(net: str):
    return unary_union([LineString(pts).buffer(w / 2, quad_segs=16) for w, pts in TRACKS.get(net, [])])


def nets_copper() -> dict:
    """Every net's pads + tracks, before the pour. Unused pads are nets of their own."""
    by_net: dict[str, list] = {}
    for p in pads():
        by_net.setdefault(p.net, []).append(p.shape())
    return {net: unary_union(shapes + [track_shapes(net)]) for net, shapes in by_net.items()}


def board_outline() -> Polygon:
    return box(0, 0, BOARD_W, BOARD_H)


def mirror(g):
    """Component view <-> CNC view of one board (copper face up). Its own inverse."""
    return affinity.scale(g, xfact=-1, yfact=1, origin=(BOARD_W / 2, 0))


def label_paths_cnc() -> list[list[tuple[float, float]]]:
    return [list(s) for s in LABEL_STROKES]


def design() -> tuple[dict, list]:
    """(final copper per net in the component view, sliver pieces that get a pass of their own)."""
    nets = nets_copper()
    keepout = unary_union([g.buffer(CLEAR, quad_segs=16) for n, g in nets.items() if n != "GND"])
    raw = board_outline().difference(keepout)
    raw = raw.difference(mirror(unary_union([LineString(s).buffer(R, quad_segs=8) for s in label_paths_cnc()])))
    opened = raw.buffer(-SLIVER / 2, quad_segs=16).buffer(SLIVER / 2, quad_segs=16).intersection(raw)
    # thin bits of pour get a pass of their own, kept a cutter's radius off the GND pads and tracks
    protect = nets["GND"].buffer(R + 0.02, quad_segs=16)
    edge = board_outline().exterior
    slivers = [g for g in components(raw.difference(opened).difference(protect))
               if g.area > 0.002 and g.distance(edge) > 0.01]        # board corners: GND, harmless
    pour = raw.difference(unary_union([g.exterior.buffer(R, quad_segs=8) for g in slivers])) if slivers else raw
    gnd = unary_union([pour, nets["GND"]])
    gnd_pads = [p.shape() for p in pads() if p.net == "GND"]
    nets["GND"] = unary_union([g for g in components(gnd) if any(g.intersects(s) for s in gnd_pads)])
    return nets, slivers


def copper() -> dict:
    return design()[0]


# ------------------------------------------------------------------ toolpaths (CNC frame of one board)
def ring_coords(g) -> list[list[tuple[float, float]]]:
    out = []
    for p in components(g):
        out.append(list(p.exterior.coords))
        out += [list(r.coords) for r in p.interiors]
    return out


def isolation_loops() -> list[list[tuple[float, float]]]:
    """One pass 0.5 out round every piece of signal copper (each net, each unused pad), plus a pass
    round any sliver of pour too thin to keep; CNC view of one board."""
    nets, slivers = design()
    loops = []
    for net, g in nets_copper().items():
        if net == "GND":
            continue
        for piece in components(g):
            loops += ring_coords(mirror(piece.buffer(R, quad_segs=16)).simplify(0.003))
    for s in slivers:
        loops += ring_coords(mirror(s).simplify(0.003))
    return loops


def drill_list() -> list[tuple[float, float, float]]:
    """(x, y, diameter) in the CNC view of one board."""
    out = [(BOARD_W - p.x, p.y, p.hole) for p in pads()]
    out += [(BOARD_W - x, y, FIX_HOLE_D) for x, y in fix_holes()]
    return out


def panel_offsets() -> list[tuple[str, float, float]]:
    out = []
    for r in range(PANEL_ROWS):
        for c in range(PANEL_COLS):
            out.append((chr(ord("A") + r * PANEL_COLS + c), c * (BOARD_W + PANEL_GAP), r * (BOARD_H + PANEL_GAP)))
    return out


def panel_size() -> tuple[float, float]:
    return (PANEL_COLS * BOARD_W + (PANEL_COLS - 1) * PANEL_GAP,
            PANEL_ROWS * BOARD_H + (PANEL_ROWS - 1) * PANEL_GAP)


# ------------------------------------------------------------------ G-code
def f(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


TOOL = f"{EM_D:g}MM FLAT 2-FLUTE CARBIDE END MILL"


class G:
    def __init__(self, title: str, notes: list[str], spindle: bool = True):
        self.lines = ["%", f"({title})", f"(TOOL: {TOOL})"] + [f"({n})" for n in notes] + [
            "(ZERO: X0 Y0 = PANEL BOTTOM-LEFT CORNER, Z0 = TOP OF THE COPPER)",
            "G21 G90 G17 G40 G94 G54",
            f"G00 Z{f(Z_CLEAR)}"]
        if spindle:
            self.lines += [f"S{RPM} M03", "G04 P3"]
        self.x = self.y = None
        self.z = Z_CLEAR

    def rapid_to(self, x: float, y: float, hop: float = Z_SAFE) -> None:
        """Up to `hop` (Z_HOP for a short move over the flat taped sheet, else Z_SAFE), then across."""
        if self.x is not None and math.dist((self.x, self.y), (x, y)) > HOP_MAX:
            hop = Z_SAFE
        if self.z < hop:
            self.lines.append(f"G00 Z{f(hop)}")
            self.z = hop
        self.lines.append(f"G00 X{f(x)} Y{f(y)}")
        self.x, self.y = x, y

    def plunge(self, z: float, feed: float) -> None:
        if z < 0 < self.z and self.z > Z_APPROACH:
            self.lines.append(f"G00 Z{f(Z_APPROACH)}")     # rapid to just above the copper, then feed
        self.lines.append(f"G01 Z{f(z)} F{f(feed)}")
        self.z = z

    def lift(self, z: float = Z_SAFE) -> None:
        self.lines.append(f"G00 Z{f(z)}")
        self.z = z

    def line_to(self, x: float, y: float, feed: float | None = None) -> None:
        self.lines.append(f"G01 X{f(x)} Y{f(y)}" + (f" F{f(feed)}" if feed else ""))
        self.x, self.y = x, y

    def end(self) -> str:
        self.lines += [f"G00 Z{f(Z_CLEAR)}", "M05", "G00 X0 Y0", "M30", "%"]
        return "\n".join(self.lines) + "\n"


def order_paths(paths, start=(0.0, 0.0)):
    """Nearest-neighbour order. Closed loops start at their vertex nearest the last point; open paths
    run from whichever end is nearer."""
    todo = [list(p) for p in paths]
    out, cur = [], start
    while todo:
        def cost(p):
            if p[0] == p[-1]:
                return min(math.dist(cur, q) for q in p[::max(1, len(p) // 24)])
            return min(math.dist(cur, p[0]), math.dist(cur, p[-1]))
        p = todo.pop(min(range(len(todo)), key=lambda i: cost(todo[i])))
        if p[0] == p[-1]:
            ring = p[:-1]
            k = min(range(len(ring)), key=lambda i: math.dist(cur, ring[i]))
            p = ring[k:] + ring[:k] + [ring[k]]
        elif math.dist(cur, p[-1]) < math.dist(cur, p[0]):
            p = p[::-1]
        out.append(p)
        cur = p[-1]
    return out


def cut_paths(g: G, paths, depth: float, feed: float, plunge: float) -> None:
    for path in order_paths(paths, (g.x or 0.0, g.y or 0.0)):
        g.rapid_to(*path[0], hop=Z_HOP)
        g.plunge(-depth, plunge)
        first = True
        for x, y in path[1:]:
            g.line_to(x, y, feed if first else None)
            first = False
        g.lift(Z_HOP)


def isolation_moves(g: G) -> None:
    loops, label = isolation_loops(), label_paths_cnc()
    for name, ox, oy in panel_offsets():
        g.lines.append(f"(BOARD {name}: ISOLATION + LABEL, Z-{f(ISO_DEPTH)})")
        cut_paths(g, [[(x + ox, y + oy) for x, y in l] for l in loops + label], ISO_DEPTH, ISO_FEED, ISO_PLUNGE)
    g.lift()


def helix(g: G, x: float, y: float, hole_d: float) -> None:
    """Helical bore: G02 full circles stepping down, then a flat circle at depth."""
    r = (hole_d - EM_D) / 2
    g.rapid_to(x + r, y)
    g.plunge(0.2, EM_PLUNGE * 2)
    z, step = 0.2, 0.3
    while z > -EM_DEPTH:
        z = max(z - step, -EM_DEPTH)
        g.lines.append(f"G02 X{f(x + r)} Y{f(y)} Z{f(z)} I{f(-r)} J0 F{f(EM_HELIX_FEED)}")
    g.lines.append(f"G02 X{f(x + r)} Y{f(y)} I{f(-r)} J0")
    g.lines.append(f"G01 X{f(x)} Y{f(y)}")
    g.z = z
    g.lift()


def drill_moves(g: G) -> None:
    for name, ox, oy in panel_offsets():
        g.lines.append(f"(BOARD {name}: HOLES)")
        holes = [(x + ox, y + oy, d) for x, y, d in drill_list()]
        cur = (g.x if g.x is not None else ox, g.y if g.y is not None else oy)
        while holes:
            i = min(range(len(holes)), key=lambda k: math.dist(cur, holes[k][:2]))
            x, y, d = holes.pop(i)
            if d <= EM_D + 0.05:
                g.rapid_to(x, y)
                g.plunge(0.2, EM_PLUNGE * 4)
                depth = 0.0
                while depth > -EM_DEPTH:
                    depth = max(depth - EM_PECK, -EM_DEPTH)
                    g.plunge(depth, EM_PLUNGE)
                    if depth > -EM_DEPTH:
                        g.lift(0.3)
                g.lift(1.0)
            else:
                helix(g, x, y, d)
            cur = (x, y)
    g.lift()


def outline_loop(ox: float, oy: float) -> list[tuple[float, float]]:
    """The cutter's centre round one board: outside the edge by its radius, corners stay square."""
    p = box(ox, oy, ox + BOARD_W, oy + BOARD_H).buffer(R, quad_segs=4)
    pts = list(p.exterior.coords)[:-1]
    # clockwise round the outside (board on the cutter's right: a climb cut with M03)
    if p.exterior.is_ccw:
        pts = pts[::-1]
    k = min(range(len(pts)), key=lambda i: math.dist(pts[i], (ox + BOARD_W / 2, oy - R)))
    pts = pts[k:] + pts[:k]
    return pts + [pts[0]]


def outline_moves(g: G) -> None:
    for name, ox, oy in panel_offsets():
        g.lines.append(f"(BOARD {name}: CUT OUT)")
        loop = outline_loop(ox, oy)
        g.rapid_to(*loop[0])
        g.plunge(0.2, EM_PLUNGE * 4)
        z = 0.0
        while z > -EM_DEPTH:
            z = max(z - EM_STEPDOWN, -EM_DEPTH)
            g.plunge(z, EM_PLUNGE)
            first = True
            for x, y in loop[1:]:
                g.line_to(x, y, EM_FEED if first else None)
                first = False
        g.lift()


NOTE_ISO = f"ISOLATION: ONE PASS ROUND EVERY COPPER AREA, Z-{f(ISO_DEPTH)}, F{ISO_FEED}"
NOTE_DRILL = f"HOLES TO Z-{f(EM_DEPTH)}: 1.0 PECKED, JD 1.4 AND FIXING {f(FIX_HOLE_D)} HELICAL"
NOTE_CUT = f"CUT-OUT: OUTSIDE EACH 70 X 50 BOARD, {f(EM_STEPDOWN)} PER PASS TO Z-{f(EM_DEPTH)}, NO TABS"


def gcode_all() -> str:
    g = G("STAIR TREE CONTROLLER PCB - WHOLE JOB, 6 BOARDS, ONE TOOL", [NOTE_ISO, NOTE_DRILL, NOTE_CUT,
                                                                       "TOUCH OFF Z ON THE COPPER"])
    isolation_moves(g)
    drill_moves(g)
    outline_moves(g)
    return g.end()


def gcode_isolation() -> str:
    g = G("STAIR TREE CONTROLLER PCB - 1 ISOLATION + LABEL, 6 BOARDS", [NOTE_ISO, "TOUCH OFF Z ON THE COPPER"])
    isolation_moves(g)
    return g.end()


def gcode_drill() -> str:
    g = G("STAIR TREE CONTROLLER PCB - 2 HOLES, 6 BOARDS", [NOTE_DRILL])
    drill_moves(g)
    return g.end()


def gcode_outline() -> str:
    g = G("STAIR TREE CONTROLLER PCB - 3 CUT OUT, 6 BOARDS", [NOTE_CUT])
    outline_moves(g)
    return g.end()


def gcode_frame() -> str:
    w, h = panel_size()
    m = EM_D  # the cut-out reaches 1mm past the panel
    g = G("STAIR TREE CONTROLLER PCB - 0 AIR FRAME (SPINDLE OFF)", [
        f"TRACES THE AREA THE JOB CUTS ({f(w + 2 * m)} X {f(h + 2 * m)}) 5MM ABOVE THE SHEET",
        "CHECK IT STAYS ON THE COPPER CLAD AND CLEAR OF THE TAPE EDGES"], spindle=False)
    g.rapid_to(-m, -m)
    g.lines.append("G00 Z5")
    g.z = 5
    for x, y in ((w + m, -m), (w + m, h + m), (-m, h + m), (-m, -m)):
        g.line_to(x, y, 2000)
    return g.end()


# ------------------------------------------------------------------ checks: simulate the G-code
MOVE = re.compile(r"([GXYZIJF])(-?\d+(?:\.\d+)?)")


def simulate(text: str, width: float, zmax: float = 0.0, zmin: float = -99.0):
    """Area cut by moves with the tool tip between zmin and zmax (below 0 = cutting), lines and arcs."""
    x = y = 0.0
    z = Z_CLEAR
    mode = 0
    paths = []
    cur: list[tuple[float, float]] = []

    def cutting(zz):
        return zmin <= zz < zmax

    for raw in text.splitlines():
        line = raw.split("(")[0].strip()
        if not line or line == "%":
            continue
        words = {}
        for k, v in MOVE.findall(line):
            if k == "G" and v in ("0", "00", "1", "01", "2", "02", "3", "03"):
                mode = int(v)
            elif k != "G":
                words[k] = float(v)
        nx, ny, nz = words.get("X", x), words.get("Y", y), words.get("Z", z)
        if mode in (2, 3) and ("I" in words or "J" in words):
            cx, cy = x + words.get("I", 0), y + words.get("J", 0)
            r = math.hypot(x - cx, y - cy)
            a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
            if mode == 2:
                while a1 >= a0:
                    a1 -= 2 * math.pi
            else:
                while a1 <= a0:
                    a1 += 2 * math.pi
            n = max(8, int(abs(a1 - a0) / (math.pi / 32)))
            pts = [(cx + r * math.cos(a0 + (a1 - a0) * t / n), cy + r * math.sin(a0 + (a1 - a0) * t / n),
                    z + (nz - z) * t / n) for t in range(1, n + 1)]
        else:
            pts = [(nx, ny, nz)]
        for px, py, pz in pts:
            if cutting(pz) and cutting(z) and mode != 0:
                if not cur:
                    cur = [(x, y)]
                cur.append((px, py))
            else:
                if len(cur) > 1:
                    paths.append(cur)
                cur = []
                if cutting(pz) and mode != 0:          # plunge: a hole as big as the tool
                    paths.append([(px, py)])
            x, y, z = px, py, pz
    if len(cur) > 1:
        paths.append(cur)
    geoms = [LineString(p).buffer(width / 2, quad_segs=8) if len(p) > 1 else Point(p[0]).buffer(width / 2, quad_segs=8)
             for p in paths]
    return unary_union(geoms)


def components(g) -> list[Polygon]:
    """The polygons in any shapely result (Polygon, MultiPolygon or a mixed collection)."""
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if not hasattr(g, "geoms"):
        return []                      # lines and points left by an intersection
    return [p for part in g.geoms for p in components(part)]


def checks(cu: dict, job: str, width: float = EM_D, iso_job: str | None = None) -> tuple[list[str], list[str]]:
    """Design rules on the drawn copper, then the copper the G-code actually leaves on board A."""
    out, fails = [], []

    def check(ok: bool, text: str) -> None:
        out.append(f"- {'PASS' if ok else '**FAIL**'}: {text}")
        if not ok:
            fails.append(text)

    pad_list = pads()
    raw = nets_copper()
    names = sorted(raw)
    worst = min((raw[a].distance(raw[b]), a, b) for i, a in enumerate(names) for b in names[i + 1:] if "GND" not in (a, b))
    check(worst[0] >= CLEAR - 0.005, f"drawn clearance between signal nets and unused pads {worst[0]:.3f}mm "
                                     f"(min {CLEAR}; closest {worst[1]} / {worst[2]})")
    gnd_gap = min(raw["GND"].distance(g) for n, g in raw.items() if n != "GND")
    check(gnd_gap >= CLEAR - 0.005, f"GND pads {gnd_gap:.3f}mm from any other net (min {CLEAR})")
    sig = unary_union([g for n, g in raw.items() if n != "GND"])
    keep = min(Point(*h).distance(sig) for h in fix_holes())
    check(keep >= INSERT_KEEP - 0.005, f"signal copper {keep:.2f}mm from the fixing hole centres "
                                       f"(min {INSERT_KEEP}: the brass inserts touch the copper side)")
    inside = all(board_outline().buffer(-0.5).contains(g) for n, g in raw.items() if n != "GND")
    check(inside, "signal copper at least 0.5mm in from the board edge")
    ring = min(p.ring() for p in pad_list)
    check(ring >= 0.24, f"smallest annular ring {ring:.2f}mm")
    gnd_parts = components(cu["GND"])
    check(len(gnd_parts) == 1, f"GND pour is {len(gnd_parts)} piece(s), reaching all {sum(p.net == 'GND' for p in pad_list)} GND pads")

    ox, oy = panel_offsets()[0][1:]
    board_a = box(ox, oy, ox + BOARD_W, oy + BOARD_H)
    # the isolation part of the job (the helical bores pass through the same depths on their way down)
    iso_part = iso_job if iso_job is not None else job.split("HOLES)")[0]
    iso = simulate(iso_part, width, zmin=-ISO_DEPTH - 0.01)
    holes = simulate(job, width, zmax=-ISO_DEPTH - 0.01)        # moves deeper: holes and the cut-out
    left = mirror(board_a.difference(iso).difference(holes))
    pieces = components(left)
    piece_nets: dict[int, set] = {}
    for p in pad_list:
        hit = [i for i, g in enumerate(pieces) if g.intersects(p.shape().buffer(-0.05))]
        for i in hit:
            piece_nets.setdefault(i, set()).add(p.net)
        if len(hit) != 1:
            check(False, f"{p.ref}: its pad is in {len(hit)} copper pieces after milling")
    shorts = [nets for nets in piece_nets.values() if len(nets) > 1]
    check(not shorts, "milled copper: no piece joins two nets" + (f" (shorts: {shorts})" if shorts else ""))
    for net in sorted({p.net for p in pad_list if not p.net.startswith("nc:")}):
        n = sum(1 for nets in piece_nets.values() if net in nets)
        check(n == 1, f"milled copper: {net} is {'one piece' if n == 1 else f'{n} pieces'} "
                      f"({sum(p.net == net for p in pad_list)} pads)")
    floating = [round(g.area, 2) for i, g in enumerate(pieces) if i not in piece_nets and g.area > 0.05]
    check(not floating, f"milled copper: {len(floating)} floating scraps over 0.05mm2 {floating if floating else ''}")
    nicked = mirror(iso).intersection(unary_union([g.buffer(-0.02) for n, g in raw.items()])).area
    check(nicked < 0.01, f"the isolation pass never cuts drawn pads or tracks ({nicked:.4f}mm2 overlap)")
    keep_ring = min(left.intersection(p.shape()).area / (p.shape().area - math.pi * (p.hole / 2) ** 2) for p in pad_list)
    check(keep_ring > 0.97, f"every pad keeps {keep_ring:.0%} or more of its copper after drilling")
    drilled = mirror(holes.intersection(board_a.buffer(-0.01)))
    bad = []
    for p in pad_list:
        hole = drilled.intersection(Point(*p.xy).buffer(p.hole / 2 + 0.3))
        dia = 2 * math.sqrt(hole.area / math.pi) if not hole.is_empty else 0
        if abs(dia - p.hole) > 0.06:
            bad.append(f"{p.ref} {dia:.2f}")
    check(not bad, f"every part hole drilled to size ({len(pad_list)} holes)" + (f": {bad}" if bad else ""))
    fixes = [2 * math.sqrt(drilled.intersection(Point(*h).buffer(FIX_HOLE_D)).area / math.pi) for h in fix_holes()]
    check(all(abs(d - FIX_HOLE_D) < 0.06 for d in fixes), f"fixing holes drilled at {', '.join(f'{d:.2f}' for d in fixes)} "
                                                          f"(want {FIX_HOLE_D}), centres {HOLE_IN} in from both edges")
    slot = holes.intersection(box(ox - 3, oy - 3, ox + BOARD_W + 3, oy + BOARD_H + 3))
    outer = [g for g in components(slot) if g.interiors]
    if outer:
        inner = Polygon(max(outer, key=lambda g: g.area).interiors[0]).bounds
        check(abs(inner[2] - inner[0] - BOARD_W) < 0.05 and abs(inner[3] - inner[1] - BOARD_H) < 0.05,
              f"board A cuts out at {inner[2] - inner[0]:.2f} x {inner[3] - inner[1]:.2f} (want {BOARD_W:g} x {BOARD_H:g})")
    else:
        check(False, "board A's cut-out isn't a closed loop")
    check(len(re.findall(r"\(BOARD [A-F]: CUT OUT\)", job)) == PANEL_COLS * PANEL_ROWS, f"{PANEL_COLS * PANEL_ROWS} boards in the job")
    return out, fails


# ------------------------------------------------------------------ drawings
def svg_path(g, **attrs) -> str:
    d = []
    for p in components(g):
        for ring in [p.exterior] + list(p.interiors):
            d.append("M" + " L".join(f"{x:.3f},{-y:.3f}" for x, y in ring.coords) + " Z")
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{" ".join(d)}" fill-rule="evenodd" {a}/>'


def board_svg(cu: dict, component_side: bool, loops=None) -> str:
    pad_list = pads()
    m = 4
    parts = []
    if component_side:
        title = "Component side: parts go in here (copper faint, seen through the board)"
        tf = lambda g: g  # noqa: E731
    else:
        title = "Copper side, as milled (mirror image); blue = the 1mm cutter's centre line"
        tf = mirror
    parts.append(svg_path(board_outline(), fill="#2f5d3a" if not component_side else "#d9c99a", stroke="#222", stroke_width=0.2))
    for net, g in cu.items():
        parts.append(svg_path(tf(g), fill="#c8803a", opacity=0.35 if component_side else 1))
    if loops and not component_side:
        for l in loops:
            parts.append('<polyline points="' + " ".join(f"{x:.3f},{-y:.3f}" for x, y in l)
                         + '" fill="none" stroke="#0af" stroke-width="0.08"/>')
    for p in pad_list:
        x = p.x if component_side else BOARD_W - p.x
        parts.append(f'<circle cx="{x:.3f}" cy="{-p.y:.3f}" r="{p.hole / 2}" fill="#111"/>')
    for hx, hy in fix_holes():
        x = hx if component_side else BOARD_W - hx
        parts.append(f'<circle cx="{x:.3f}" cy="{-hy:.3f}" r="{FIX_HOLE_D / 2}" fill="#fff" stroke="#222" stroke-width="0.15"/>')
    if component_side:
        def rect(a, b, label, colour="#a33", pad_=1.5, where="above"):
            (x1, y1), (x2, y2) = a, b
            parts.append(f'<rect x="{min(x1, x2) - pad_:.2f}" y="{-max(y1, y2) - pad_:.2f}" width="{abs(x2 - x1) + 2 * pad_:.2f}" '
                         f'height="{abs(y2 - y1) + 2 * pad_:.2f}" rx="0.6" fill="none" stroke="{colour}" stroke-width="0.25"/>')
            tx, ty, anchor = (x1 + x2) / 2, -max(y1, y2) - pad_ - 0.6, "middle"
            if where == "right":
                tx, ty, anchor = max(x1, x2) + pad_ + 0.5, -(y1 + y2) / 2 + 0.6, "start"
            elif where == "left":
                tx, ty, anchor = min(x1, x2) - pad_ - 0.5, -(y1 + y2) / 2 + 0.6, "end"
            elif where == "inside":
                ty = -(y1 + y2) / 2 + 0.6
            elif where == "below":
                ty = -min(y1, y2) + pad_ + 1.8
            parts.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-size="1.7" text-anchor="{anchor}" fill="{colour}">{label}</text>')
        (ax, ay), (bx, by) = pad("J2.1").xy, pad("J3.19").xy
        parts.append(f'<rect x="{ax - 1:.2f}" y="{-by - 1.3:.2f}" width="48.3" height="27.94" fill="#3a6ea5" fill-opacity="0.10" '
                     f'stroke="#3a6ea5" stroke-width="0.25" stroke-dasharray="1 0.6"/>')
        parts.append(f'<text x="{(ax + bx) / 2:.2f}" y="{-(ay + by) / 2 - 3:.2f}" font-size="2.4" text-anchor="middle" fill="#3a6ea5">'
                     f'ESP32-DevKitC-32U: antenna end left, USB right</text>')
        rect(pad("U1.7").xy, pad("U1.14").xy, "U1 74AHCT125, notch right", "#222", 1.4, "inside")
        rect(pad("R1.1").xy, pad("R1.2").xy, "R1 33Ω")
        rect(pad("R2.2").xy, pad("R2.1").xy, "R2 10k", where="below")
        rect(pad("C1.-").xy, pad("C1.+").xy, "C1 100µF, + down", where="right")
        rect(pad("C2.5V").xy, pad("C2.GND").xy, "C2 0.1µF", pad_=1.2, where="below")
        rect(pad("JD.DATA").xy, pad("JD.GND").xy, "JD: DATA | GND", pad_=1.6)
        rect(pad("M.OUT+a").xy, pad("M.OUT-b").xy, "", pad_=1.3)
        x, y = pad("M.OUT+b").x, (pad("M.OUT+b").y + pad("M.OUT-a").y) / 2
        parts.append(f'<text x="{x - 2.2:.2f}" y="{-y:.2f}" font-size="1.6" fill="#a33" text-anchor="middle" '
                     f'transform="rotate(-90 {x - 2.2:.2f} {-y:.2f})">Mini560 OUT − | +</text>')
    w, h = BOARD_W + 2 * m, BOARD_H + 2 * m + 6
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * 10:.0f}" height="{h * 10:.0f}" '
            f'viewBox="{-m} {-BOARD_H - m - 6} {w} {h}" font-family="sans-serif">'
            f'<rect x="{-m}" y="{-BOARD_H - m - 6}" width="{w}" height="{h}" fill="#fff"/>'
            f'<text x="0" y="{-BOARD_H - 2.5}" font-size="2.2">{title}</text>' + "".join(parts) + "</svg>\n")


def panel_svg(cu: dict) -> str:
    w, h = panel_size()
    m = 6
    cnc_cu = mirror(unary_union(list(cu.values())))
    parts = []
    for name, ox, oy in panel_offsets():
        parts.append(svg_path(affinity.translate(board_outline(), ox, oy), fill="#2f5d3a"))
        parts.append(svg_path(affinity.translate(cnc_cu, ox, oy), fill="#c8803a"))
        for x, y, d in drill_list():
            parts.append(f'<circle cx="{x + ox:.2f}" cy="{-(y + oy):.2f}" r="{d / 2}" fill="#111"/>')
        parts.append(f'<text x="{ox + BOARD_W / 2:.1f}" y="{-(oy + 12):.1f}" font-size="9" text-anchor="middle" '
                     f'fill="#fff" fill-opacity="0.6">{name}</text>')
    parts.append(f'<circle cx="0" cy="0" r="1.6" fill="none" stroke="#e00" stroke-width="0.5"/>'
                 f'<text x="2" y="4.5" font-size="3.5" fill="#e00">X0 Y0</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{(w + 2 * m) * 4:.0f}" height="{(h + 2 * m + 8) * 4:.0f}" '
            f'viewBox="{-m} {-h - m} {w + 2 * m} {h + 2 * m + 8}" font-family="sans-serif">'
            f'<rect x="{-m}" y="{-h - m}" width="{w + 2 * m}" height="{h + 2 * m + 8}" fill="#fff"/>'
            + "".join(parts) +
            f'<text x="0" y="{m + 3}" font-size="3.5">Panel as it sits on the PrintNC, copper up: {w:g} x {h:g}mm '
            f'(cut-out reaches 1mm further all round)</text></svg>\n')


# ------------------------------------------------------------------ Gerber / Excellon (component view = top view)
def gerber(geom, layer: str) -> str:
    def c(v):
        return f"{round(v * 1e6):d}"
    lines = ["%FSLAX46Y46*%", "%MOMM*%", f"G04 Stair Tree controller, {layer}, tools/gen_pcb.py*", "%LPD*%", "G01*"]
    for p in sorted(components(geom), key=lambda q: -q.area):   # containers first: LPC holes must not clear islands
        for i, ring in enumerate([p.exterior] + list(p.interiors)):
            lines.append("%LPD*%" if i == 0 else "%LPC*%")
            pts = list(ring.coords)
            lines += ["G36*", f"X{c(pts[0][0])}Y{c(pts[0][1])}D02*"] + [f"X{c(x)}Y{c(y)}D01*" for x, y in pts[1:]] + ["G37*"]
        lines.append("%LPD*%")
    lines.append("M02*")
    return "\n".join(lines) + "\n"


def gerber_outline() -> str:
    lines = ["%FSLAX46Y46*%", "%MOMM*%", "%ADD10C,0.100*%", "D10*", "G01*", "X0Y0D02*",
             f"X{int(BOARD_W * 1e6)}Y0D01*", f"X{int(BOARD_W * 1e6)}Y{int(BOARD_H * 1e6)}D01*",
             f"X0Y{int(BOARD_H * 1e6)}D01*", "X0Y0D01*", "M02*"]
    return "\n".join(lines) + "\n"


def excellon() -> str:
    holes = [(p.xy, p.hole) for p in pads()] + [(h, FIX_HOLE_D) for h in fix_holes()]
    sizes = sorted({d for _, d in holes})
    lines = ["M48", "METRIC,TZ"] + [f"T{i + 1}C{d:.3f}" for i, d in enumerate(sizes)] + ["%", "G05"]
    for i, d in enumerate(sizes):
        lines.append(f"T{i + 1}")
        lines += [f"X{x:.3f}Y{y:.3f}" for (x, y), dd in holes if dd == d]
    lines.append("M30")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ main
def stats(text: str) -> tuple[float, float]:
    """(cutting length mm, rough minutes) from the G-code."""
    x = y = z = 0.0
    feed, length, minutes = 1000.0, 0.0, 0.0
    for raw in text.splitlines():
        line = raw.split("(")[0]
        w = dict(MOVE.findall(line))
        if "F" in w:
            feed = float(w["F"])
        nx, ny, nz = float(w.get("X", x)), float(w.get("Y", y)), float(w.get("Z", z))
        d = math.dist((x, y, z), (nx, ny, nz))
        if re.search(r"\bG0?[23]\b", line):
            d = max(d, 2 * math.pi * math.hypot(float(w.get("I", 0)), float(w.get("J", 0))))
        if re.search(r"\bG0?0\b", line):
            minutes += d / 5000
        elif d:
            length += d
            minutes += d / feed
        x, y, z = nx, ny, nz
    return length, minutes


def write() -> tuple[list[str], list[str]]:
    cu = copper()
    files = {"cam/tree-pcb-6up-1mm.nc": gcode_all(), "cam/0_air_frame.nc": gcode_frame(),
             "cam/1_isolation_1mm.nc": gcode_isolation(), "cam/2_drill_1mm.nc": gcode_drill(),
             "cam/3_outline_1mm.nc": gcode_outline()}
    report, fails = checks(cu, files["cam/tree-pcb-6up-1mm.nc"])
    robust = []
    for wd in (0.95, 1.05):
        _, f2 = checks(cu, files["cam/tree-pcb-6up-1mm.nc"], wd)
        f2 = [x for x in f2 if x.startswith(("milled copper", "U1.", "J", "R", "C", "M.", "GND pour"))]   # nets only
        robust.append(f"- {'PASS' if not f2 else '**FAIL**'}: the same G-code with a {wd}mm cutter: "
                      + ("same nets, no shorts, no breaks" if not f2 else "; ".join(f2)))
        fails += f2
    files["gerber/tree-controller-B_Cu.gbr"] = gerber(unary_union(list(cu.values())), "bottom copper, seen from the top")
    files["gerber/tree-controller-Edge_Cuts.gbr"] = gerber_outline()
    files["gerber/tree-controller.drl"] = excellon()
    files["board-component-side.svg"] = board_svg(cu, True)
    files["board-copper-side.svg"] = board_svg(cu, False, isolation_loops() + label_paths_cnc())
    files["panel.svg"] = panel_svg(cu)
    times = []
    for name in ("cam/1_isolation_1mm.nc", "cam/2_drill_1mm.nc", "cam/3_outline_1mm.nc", "cam/tree-pcb-6up-1mm.nc"):
        length, minutes = stats(files[name])
        times.append(f"| {name.split('/')[-1]} | {length / 1000:.1f} m | ~{minutes:.0f} min |")
    pw, ph = panel_size()
    files["checks.md"] = "\n".join([
        "# Tree controller PCB: checks", "",
        "Generated by tools/gen_pcb.py; don't edit. The first block checks the drawn copper; the rest re-reads "
        "cam/tree-pcb-6up-1mm.nc, works out the copper and holes it actually leaves on board A, and compares that "
        "with the netlist.", "", f"One {EM_D:g}mm flat end mill for everything; isolation one pass, {ISO_DEPTH}mm deep.", ""]
        + report + robust + ["", f"Panel {pw:g} x {ph:g}mm ({PANEL_COLS} x {PANEL_ROWS} boards, {PANEL_GAP:g}mm apart); "
                             f"the cut-out reaches {EM_D:g}mm past it all round.", "",
                             "| File | Cutting | Time (feeds only, rough) |", "|---|---|---|"] + times + [""])
    for stale in (OUT / "cam").glob("*.nc"):
        if f"cam/{stale.name}" not in files:
            stale.unlink()
    for name, text in files.items():
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return report + robust, fails


def main() -> None:
    report, fails = write()
    print("\n".join(report))
    if fails:
        raise SystemExit(f"gen_pcb: {len(fails)} check(s) failed")


if __name__ == "__main__":
    main()
