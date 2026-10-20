"""Tree layout generator: the single source of truth for pixel positions.

Reads the blank outline from data/blank.json, places the 92 nodes in wiring
order and writes data/tree-layout.json. Every other artefact (CNC, xLights,
FPP) is generated from that JSON.

Coordinates are mm, viewed from the front of the tree, x right, y down,
origin at the top-left of the blank's bounding box.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLANK_FILE = ROOT / "data" / "blank.json"
LAYOUT_FILE = ROOT / "data" / "tree-layout.json"


@dataclass(frozen=True)
class Params:
    hole_dia: float = 12.0          # pixel bullet hole; confirm with the offcut test
    # TODO(Rob): pixels will probably need a counterbore from the back; size TBC when they arrive. 0 = none.
    back_counterbore_dia: float = 0.0
    back_counterbore_depth: float = 0.0
    edge_inset: float = 22.0        # outline node centres from the blank edge
    min_spacing: float = 24.4       # minimum node centre spacing
    hole_wall: float = 5.0          # minimum wood between a pixel hole and an existing hole
    outline_nodes: int = 59
    # Face, relative to the blank's centreline (cx) and its top (y = 0).
    eye_y: float = 555.0
    eye_dx: float = 42.0            # each eye centre this far either side of cx
    eye_r: float = 26.0             # hexagon of 6 nodes
    mouth_y: float = 690.0          # lip line
    mouth_pitch: float = 26.0       # horizontal spacing of mouth nodes
    lip_nodes: int = 7
    mouth_wide_nodes: int = 9
    mouth_wide_depth: float = 92.0  # parabola depth below the lip line
    mouth_small_nodes: int = 5
    mouth_small_depth: float = 44.0
    mouth_small_half_width: float = 78.0


# Wiring order of the groups after the outline.
GROUP_ORDER = ("outline", "mouth_wide", "mouth_small", "lip", "eye_right", "eye_left")

# Mouth groups lit for each xLights phoneme; outline and eyes are always lit.
PHONEMES = {
    "rest": ["lip"], "MBP": ["lip"],
    "etc": ["lip", "mouth_small"], "FV": ["lip", "mouth_small"],
    "L": ["lip", "mouth_small"], "E": ["lip", "mouth_small"],
    "AI": ["lip", "mouth_wide"],
    "O": ["mouth_small", "mouth_wide"], "U": ["mouth_small", "mouth_wide"],
    "WQ": ["mouth_small", "mouth_wide"],
}

Point = tuple[float, float]


def load_blank(path: Path = BLANK_FILE) -> dict:
    blank = json.loads(path.read_text(encoding="utf-8"))
    pts = [(float(p["x"]), float(p["y"])) for p in blank["points"]]
    minx = min(x for x, _ in pts)
    miny = min(y for _, y in pts)
    blank["polygon"] = [(x - minx, y - miny) for x, y in pts]
    blank["corners"] = [p.get("corner", True) for p in blank["points"]]
    blank["holes"] = [{**h, "x": h["x"] - minx, "y": h["y"] - miny} for h in blank.get("existing_holes", [])]
    return blank


def signed_area(poly: list[Point]) -> float:
    return sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1]
               for i in range(len(poly))) / -2.0


def inset_convex(poly: list[Point], d: float) -> list[Point]:
    """Offset a convex polygon inwards by d; returns one point per vertex."""
    n = len(poly)
    sign = 1.0 if signed_area(poly) > 0 else -1.0
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        length = math.hypot(x1 - x0, y1 - y0)
        ex, ey = (x1 - x0) / length, (y1 - y0) / length
        nx, ny = -ey * sign, ex * sign  # inward normal
        lines.append(((x0 + nx * d, y0 + ny * d), (ex, ey)))
    out = []
    for i in range(n):
        (p, e), (q, f) = lines[i - 1], lines[i]
        den = e[0] * f[1] - e[1] * f[0]
        t = ((q[0] - p[0]) * f[1] - (q[1] - p[1]) * f[0]) / den
        out.append((p[0] + e[0] * t, p[1] + e[1] * t))
    return out


def check_convex(poly: list[Point]) -> None:
    n = len(poly)
    signs = set()
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(cross) > 1e-9:
            signs.add(cross > 0)
    if len(signs) > 1:
        raise ValueError("blank outline must be convex (concave shapes not supported yet)")


def interior_angle(a: Point, b: Point, c: Point) -> float:
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
    return math.acos(max(-1.0, min(1.0, cos)))


def point_along(path: list[Point], dist: float) -> Point:
    for a, b in zip(path, path[1:]):
        seg = math.dist(a, b)
        if dist <= seg or b is path[-1]:
            t = dist / seg
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        dist -= seg
    return path[-1]


def path_length(path: list[Point]) -> float:
    return sum(math.dist(a, b) for a, b in zip(path, path[1:]))


def forbidden_spans(path: list[Point], keepouts: list[tuple[Point, float]], step: float = 0.25) -> list[tuple[float, float]]:
    """Stretches of the path (as distances along it) where a node centre would
    come closer to an existing hole than its keep-out radius."""
    total = path_length(path)
    spans, start = [], None
    for k in range(int(total / step) + 2):
        s = min(k * step, total)
        q = point_along(path, s)
        bad = any(math.dist(q, c) < r for c, r in keepouts)
        if bad and start is None:
            start = s
        elif not bad and start is not None:
            spans.append((start, s))
            start = None
    if start is not None:
        spans.append((start, total))
    return spans


def outline_nodes(inset: list[Point], corners: list[bool], p: Params,
                  keepouts: list[tuple[Point, float]] = ()) -> list[Point]:
    """Nodes on every corner, the rest spread along the sides between corners.

    Near an acute corner the first node on each side is pushed back far enough
    that the two neighbours of the corner node are still min_spacing apart.
    Keep-outs (existing holes) split a side: no node inside one, and the nodes
    either side sit on its boundary. A corner inside a keep-out is dropped.
    """
    n = len(inset)
    if not corners[0]:
        raise ValueError("the first blank point (data-in) must be a corner")
    path = inset + [inset[0]]
    pos = [0.0]
    for a, b in zip(path, path[1:]):
        pos.append(pos[-1] + math.dist(a, b))
    total = pos[-1]
    spans = forbidden_spans(path, list(keepouts))

    def blocked(s: float) -> bool:
        return any(a <= s <= b for a, b in spans)

    if blocked(0.0):
        raise ValueError("the data-in corner is inside an existing hole's keep-out")

    # Events along the closed path: kept corners, and keep-out boundaries.
    events = []  # (distance, kind, clearance)
    for i in range(n):
        if corners[i] and not blocked(pos[i]):
            theta = interior_angle(inset[i - 1], inset[i], inset[(i + 1) % n])
            events.append((pos[i], "corner", max(p.min_spacing, p.min_spacing / (2 * math.sin(theta / 2)))))
    for a, b in spans:
        events += [(a, "enter", 0.0), (b, "leave", 0.0)]
    events.sort()
    events.append((total, *events[0][1:]))

    segments = [(e0, e1) for e0, e1 in zip(events, events[1:]) if e0[1] != "enter"]
    n_corners = sum(1 for e in events[:-1] if e[1] == "corner")

    # Share the non-corner nodes between segments by length (largest remainder).
    spare = p.outline_nodes - n_corners
    lengths = [e1[0] - e0[0] for e0, e1 in segments]
    raw = [spare * length / sum(lengths) for length in lengths]
    counts = [math.floor(r) for r in raw]
    order = sorted(range(len(segments)), key=lambda i: (-(raw[i] - counts[i]), i))
    for i in order[: spare - sum(counts)]:
        counts[i] += 1

    dists = []
    for ((s0, k0, c0), (s1, k1, c1)), m in zip(segments, counts):
        if k0 == "corner":
            dists.append(s0)
        if m == 0:
            continue
        length = s1 - s0
        at_start, at_end = k0 == "leave", k1 == "enter"  # nodes sit on keep-out boundaries
        gaps = m + 1 - at_start - at_end
        step = length / gaps if gaps else math.inf
        first = 0 if at_start else 1
        if not gaps:
            rel = [length / 2]
        elif step >= max(c0, c1):
            rel = [step * (first + k) for k in range(m)]
        else:
            lo, hi = c0, length - c1
            rel = [(lo + hi) / 2] if m == 1 else [lo + (hi - lo) * k / (m - 1) for k in range(m)]
        dists += [s0 + r for r in rel]
    return [point_along(path, d) for d in dists]


def face_nodes(cx: float, p: Params) -> dict[str, list[Point]]:
    def parabola(n: int, half: float, depth: float, reverse: bool) -> list[Point]:
        xs = [(k - (n - 1) / 2) * p.mouth_pitch for k in range(n)]
        if reverse:
            xs.reverse()
        return [(cx + dx, p.mouth_y + depth * (1 - (dx / half) ** 2)) for dx in xs]

    def hexagon(ex: float) -> list[Point]:
        # Top node first, then clockwise as seen from the front.
        return [(ex + p.eye_r * math.sin(math.radians(a)), p.eye_y - p.eye_r * math.cos(math.radians(a)))
                for a in range(0, 360, 60)]

    wide_half = (p.mouth_wide_nodes - 1) / 2 * p.mouth_pitch
    lip_xs = [(k - (p.lip_nodes - 1) / 2) * p.mouth_pitch for k in range(p.lip_nodes)]
    return {
        "mouth_wide": parabola(p.mouth_wide_nodes, wide_half, p.mouth_wide_depth, False),
        "mouth_small": parabola(p.mouth_small_nodes, p.mouth_small_half_width, p.mouth_small_depth, True),
        "lip": [(cx + dx, p.mouth_y) for dx in lip_xs],
        "eye_right": hexagon(cx + p.eye_dx),  # viewer's right, as seen from the front
        "eye_left": hexagon(cx - p.eye_dx),
    }


def build_layout(blank: dict, p: Params = Params()) -> dict:
    poly = blank["polygon"]
    check_convex(poly)
    inset = inset_convex(poly, p.edge_inset)
    xs = [x for x, _ in poly]
    width, height = max(xs), max(y for _, y in poly)
    cx = width / 2

    holes = blank.get("holes", [])
    pixel_r = max(p.hole_dia, p.back_counterbore_dia) / 2
    keepouts = [((h["x"], h["y"]), pixel_r + h["dia"] / 2 + p.hole_wall) for h in holes]
    groups = {"outline": outline_nodes(inset, blank["corners"], p, keepouts), **face_nodes(cx, p)}
    nodes, ranges, n = [], {}, 1
    for g in GROUP_ORDER:
        pts = groups[g]
        ranges[g] = [n, n + len(pts) - 1]
        for x, y in pts:
            nodes.append({"n": n, "group": g, "x": round(x, 1), "y": round(y, 1)})
            n += 1

    return {
        "generated_by": "tools/tree_layout.py",
        "units": "mm",
        "view": "front, x right, y down, origin top-left of blank bounding box",
        "blank": {
            "measured": blank.get("measured", False),
            "width": round(width, 1),
            "height": round(height, 1),
            "thickness": blank.get("thickness"),
            "corner_radius": blank.get("corner_radius", 0),
            "polygon": [[round(x, 1), round(y, 1)] for x, y in poly],
            "existing_holes": [{k: h[k] for k in ("name", "x", "y", "dia", "depth")} for h in holes],
        },
        "params": asdict(p),
        "node_count": len(nodes),
        "groups": ranges,
        "phonemes": PHONEMES,
        "nodes": nodes,
    }


def dumps(layout: dict) -> str:
    """JSON with one node per line, so diffs stay readable."""
    head = {k: v for k, v in layout.items() if k != "nodes"}
    head["blank"] = {**head["blank"], "polygon": "@POLY@", "existing_holes": "@HOLES@"}
    text = json.dumps(head, indent=2)[:-2]
    text = text.replace('"@POLY@"', json.dumps(layout["blank"]["polygon"]))
    holes = ",\n".join("      " + json.dumps(h) for h in layout["blank"]["existing_holes"])
    text = text.replace('"@HOLES@"', f"[\n{holes}\n    ]" if holes else "[]")
    rows = ",\n".join("    " + json.dumps(nd) for nd in layout["nodes"])
    return f'{text},\n  "nodes": [\n{rows}\n  ]\n}}\n'


def main() -> None:
    layout = build_layout(load_blank())
    LAYOUT_FILE.write_text(dumps(layout), encoding="utf-8", newline="\n")
    print(f"wrote {LAYOUT_FILE.relative_to(ROOT)} ({layout['node_count']} nodes)")


if __name__ == "__main__":
    main()
