"""Tree controller perfboard: electronics/tree-controller-board.svg and electronics/connections.md.

One board per tree on a 5x7cm pad-per-hole prototype board (24 x 18 holes, 2.54mm).
Parts and nets are defined here; the wiring list is the shortest set of joins that
connects each net (a minimum spanning tree over its holes), so it can't miss a pin.

Pin order of the ESP32 headers from Espressif's ESP32-DevKitC V4 user guide
(J2 and J3, pin 1 at the antenna end). The header row spacing differs between
clones: ESP_ROW_GAP is a guess until Rob measures the boards.
"""

from __future__ import annotations

import math
from pathlib import Path

from tools.tree_layout import ROOT

SVG_FILE = ROOT / "electronics" / "tree-controller-board.svg"
TABLE_FILE = ROOT / "electronics" / "connections.md"

PITCH = 2.54
COLS, ROWS = 24, 18
ESP_ROW_GAP = 10  # holes between J2 and J3 (25.4mm); measure the real board
ESP_J2_ROW = 2
ESP_PIN1_COL = 5  # pin 19 lands on the last column, so the USB end overhangs the edge

J2 = ["3V3", "EN", "VP", "VN", "IO34", "IO35", "IO32", "IO33", "IO25", "IO26",
      "IO27", "IO14", "IO12", "GND", "IO13", "D2", "D3", "CMD", "5V"]
J3 = ["GND", "IO23", "IO22", "TX", "RX", "IO21", "GND", "IO19", "IO18", "IO5",
      "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "D1", "D0", "CLK"]

# 74AHCT125 DIP-14, fitted notch-right: pin 1 top right, pins 1-7 run left along
# the top row, pins 8-14 run right along the bottom row.
U1_PINS = {1: "1OE", 2: "1A", 3: "1Y", 4: "2OE", 5: "2A", 6: "2Y", 7: "GND",
           8: "3Y", 9: "3A", 10: "3OE", 11: "4Y", 12: "4A", 13: "4OE", 14: "VCC"}
U1_TOP_ROW, U1_BOTTOM_ROW, U1_RIGHT_COL = 14, 17, 12


def u1_hole(pin: int) -> tuple[int, int]:
    if pin <= 7:
        return U1_RIGHT_COL - (pin - 1), U1_TOP_ROW
    return U1_RIGHT_COL - 6 + (pin - 8), U1_BOTTOM_ROW


def esp_hole(header: str, pin: int) -> tuple[int, int]:
    row = ESP_J2_ROW if header == "J2" else ESP_J2_ROW + ESP_ROW_GAP
    return ESP_PIN1_COL + pin - 1, row


# Two-lead parts and wire pads: name -> (description, [(pin label, (col, row)), ...]).
SMALL_PARTS = {
    "R1": ("33Ω data resistor, lying flat", [("1", (14, 16)), ("2", (18, 16))]),
    "R2": ("10kΩ pull-down, standing", [("1", (11, 13)), ("2", (12, 13))]),
    "C1": ("100µF 16V+ electrolytic, standing", [("+", (3, 16)), ("-", (4, 16))]),
    "C2": ("0.1µF ceramic, standing", [("GND", (13, 15)), ("5V", (13, 17))]),
    "JP": ("12V in, 2-way 5.08mm screw terminal", [("12V", (0, 13)), ("GND", (0, 15))]),
    "JD": ("Pixel data out, 2-way 5.08mm screw terminal", [("DATA", (20, 16)), ("GND", (22, 16))]),
    "M": ("Mini560 5V buck, off the board on short leads",
          [("IN+", (0, 4)), ("IN-", (0, 6)), ("OUT-", (0, 8)), ("OUT+", (0, 10))]),
}

# Net -> list of (part, pin). U1's spare channels have inputs and enables tied to
# GND, so their outputs sit low; outputs 2Y/3Y/4Y and unused ESP pins stay open.
NETS = {
    "12V": [("JP", "12V"), ("M", "IN+")],
    "5V": [("M", "OUT+"), ("C1", "+"), ("J2", 19), ("U1", 14), ("C2", "5V")],
    "GND": [("JP", "GND"), ("M", "IN-"), ("M", "OUT-"), ("C1", "-"), ("J3", 1),
            ("U1", 1), ("U1", 4), ("U1", 5), ("U1", 7), ("U1", 9), ("U1", 10),
            ("U1", 12), ("U1", 13), ("R2", "2"), ("C2", "GND"), ("JD", "GND")],
    "DATA 3.3V": [("J3", 12), ("U1", 2), ("R2", "1")],
    "DATA 5V": [("U1", 3), ("R1", "1")],
    "DATA OUT": [("R1", "2"), ("JD", "DATA")],
}

NET_COLOURS = {"12V": "#d62728", "5V": "#ff7f0e", "GND": "#333333",
               "DATA 3.3V": "#1f77b4", "DATA 5V": "#2ca02c", "DATA OUT": "#9467bd"}


def hole(part: str, pin) -> tuple[int, int]:
    if part in ("J2", "J3"):
        return esp_hole(part, pin)
    if part == "U1":
        return u1_hole(pin)
    return dict(SMALL_PARTS[part][1])[pin]


def pin_label(part: str, pin) -> str:
    if part == "J2":
        return f"ESP32 J2.{pin} {J2[pin - 1]}"
    if part == "J3":
        return f"ESP32 J3.{pin} {J3[pin - 1]}"
    if part == "U1":
        return f"U1.{pin} {U1_PINS[pin]}"
    return f"{part} {pin}"


def hole_name(col: int, row: int) -> str:
    """Column letter A-X, row number 1-18, as seen from the component side."""
    return f"{chr(ord('A') + col)}{row + 1}"


def all_holes() -> dict[tuple[int, int], str]:
    """Every hole a part uses -> its label."""
    used = {}
    for header, names in (("J2", J2), ("J3", J3)):
        for i in range(1, len(names) + 1):
            used[esp_hole(header, i)] = pin_label(header, i)
    for p in U1_PINS:
        used[u1_hole(p)] = pin_label("U1", p)
    for part, (_, pins) in SMALL_PARTS.items():
        for label, h in pins:
            used[h] = pin_label(part, label)
    return used


def joins(net: str) -> list[tuple[tuple, tuple]]:
    """Minimum spanning tree over the net's holes (Prim), ties broken by order."""
    members = NETS[net]
    done = [members[0]]
    todo = list(members[1:])
    out = []
    while todo:
        best = None
        for a in done:
            for b in todo:
                d = math.dist(hole(*a), hole(*b))
                if best is None or d < best[0]:
                    best = (d, a, b)
        _, a, b = best
        out.append((a, b))
        done.append(b)
        todo.remove(b)
    return out


def is_bridge(a: tuple, b: tuple) -> bool:
    """Neighbouring holes in a row or column: a solder bridge is enough."""
    (c1, r1), (c2, r2) = hole(*a), hole(*b)
    return abs(c1 - c2) + abs(r1 - r2) == 1


def table() -> str:
    lines = [
        "# Tree controller connections",
        "",
        "Generated by tools/gen_controller.py; don't edit. Holes are named column letter "
        "(A-X, left to right) and row (1-18, top to bottom) **seen from the component side**. "
        "On the underside the columns run right to left.",
        "",
        "Bridge = neighbouring holes, join with a solder blob or a bent lead. "
        "Wire = insulated wire on the underside (it may pass over other pads).",
        "",
        "## Parts",
        "",
        "| Part | What | Holes |",
        "|---|---|---|",
        f"| J2/J3 | ESP32 dev board in two 1×19 female headers | J2 {hole_name(*esp_hole('J2', 1))}–"
        f"{hole_name(*esp_hole('J2', 19))}, J3 {hole_name(*esp_hole('J3', 1))}–"
        f"{hole_name(*esp_hole('J3', 19))} (pin 1 at the antenna end) |",
        f"| U1 | 74AHCT125N in a DIP-14 socket, notch to the right | pin 1 {hole_name(*u1_hole(1))}, "
        f"pin 7 {hole_name(*u1_hole(7))}, pin 8 {hole_name(*u1_hole(8))}, pin 14 {hole_name(*u1_hole(14))} |",
    ]
    for part, (desc, pins) in SMALL_PARTS.items():
        holes = ", ".join(f"{label} {hole_name(*h)}" for label, h in pins)
        lines.append(f"| {part} | {desc} | {holes} |")
    lines += ["", "## Joins", "", "| Net | From | To | Type |", "|---|---|---|---|"]
    for net in NETS:
        for a, b in joins(net):
            kind = "bridge" if is_bridge(a, b) else "wire"
            lines.append(f"| {net} | {pin_label(*a)} ({hole_name(*hole(*a))}) | "
                         f"{pin_label(*b)} ({hole_name(*hole(*b))}) | {kind} |")
    lines.append("")
    return "\n".join(lines)


def _xy(col: int, row: int, mirror: bool, ox: float) -> tuple[float, float]:
    c = COLS - 1 - col if mirror else col
    return ox + 5 + c * PITCH, 12 + row * PITCH


def _panel(ox: float, mirror: bool) -> list[str]:
    w, h = (COLS - 1) * PITCH + 10, (ROWS - 1) * PITCH + 10
    title = "Underside (as you solder): joins" if mirror else "Component side: parts"
    out = [f'<rect x="{ox}" y="7" width="{w:.2f}" height="{h:.2f}" rx="1" fill="#e9d8a6" stroke="#8a7a50" stroke-width="0.3"/>',
           f'<text x="{ox}" y="4" font-size="3">{title}</text>']
    used = all_holes()
    for col in range(COLS):
        for row in range(ROWS):
            x, y = _xy(col, row, mirror, ox)
            fill = "#b87333" if (col, row) in used else "#c9b98a"
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.55" fill="{fill}"/>')
    for col in range(COLS):
        x, _ = _xy(col, 0, mirror, ox)
        out.append(f'<text x="{x:.2f}" y="{7 + h + 3:.2f}" font-size="1.6" text-anchor="middle">{chr(65 + col)}</text>')
    for row in range(ROWS):
        x, y = _xy(0, row, mirror, ox)
        tx = x + (3 if mirror else -3)
        out.append(f'<text x="{tx:.2f}" y="{y + 0.6:.2f}" font-size="1.6" text-anchor="middle">{row + 1}</text>')
    if mirror:
        for net in NETS:
            colour = NET_COLOURS[net]
            for a, b in joins(net):
                (x1, y1), (x2, y2) = _xy(*hole(*a), True, ox), _xy(*hole(*b), True, ox)
                width = 0.9 if is_bridge(a, b) else 0.45
                out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                           f'stroke="{colour}" stroke-width="{width}" stroke-linecap="round" opacity="0.85"/>')
        for i, net in enumerate(NETS):
            lx, ly = ox + (i % 3) * 23, 7 + h + 7 + (i // 3) * 3.5
            out.append(f'<rect x="{lx:.2f}" y="{ly - 1.8:.2f}" width="3" height="2" fill="{NET_COLOURS[net]}"/>'
                       f'<text x="{lx + 4:.2f}" y="{ly:.2f}" font-size="2">{net}</text>')
        return out
    # Component side outlines.
    for header in ("J2", "J3"):
        (x1, y1), (x2, _) = _xy(*esp_hole(header, 1), False, ox), _xy(*esp_hole(header, 19), False, ox)
        out.append(f'<rect x="{x1 - 1.27:.2f}" y="{y1 - 1.27:.2f}" width="{x2 - x1 + 2.54:.2f}" height="2.54" '
                   f'fill="none" stroke="#222" stroke-width="0.3"/>'
                   f'<text x="{x1 - 2:.2f}" y="{y1 + 0.7:.2f}" font-size="1.8" text-anchor="end">{header}</text>')
    (ax, ay), (bx, by) = _xy(*esp_hole("J2", 1), False, ox), _xy(*esp_hole("J3", 19), False, ox)
    out.append(f'<rect x="{ax - 1.27:.2f}" y="{ay - 1.27:.2f}" width="{bx - ax + 2.54:.2f}" height="{by - ay + 2.54:.2f}" '
               f'fill="#3a6ea5" fill-opacity="0.12" stroke="#3a6ea5" stroke-width="0.3" stroke-dasharray="1 0.6"/>'
               f'<text x="{(ax + bx) / 2:.2f}" y="{(ay + by) / 2:.2f}" font-size="2.5" text-anchor="middle" fill="#3a6ea5">'
               f'ESP32 dev board (antenna end left, USB right)</text>')
    for p, label in ((12, "IO16"), (1, "GND")):
        x, y = _xy(*esp_hole("J3", p), False, ox)
        out.append(f'<text x="{x:.2f}" y="{y - 1.8:.2f}" font-size="1.4" text-anchor="middle">{label}</text>')
    x, y = _xy(*esp_hole("J2", 19), False, ox)
    out.append(f'<text x="{x:.2f}" y="{y - 1.8:.2f}" font-size="1.4" text-anchor="middle">5V</text>')
    (x1, y1), (x2, y2) = _xy(*u1_hole(7), False, ox), _xy(*u1_hole(14), False, ox)
    out.append(f'<rect x="{x1 - 1.5:.2f}" y="{y1 - 1.5:.2f}" width="{x2 - x1 + 3:.2f}" height="{y2 - y1 + 3:.2f}" '
               f'fill="#222" fill-opacity="0.15" stroke="#222" stroke-width="0.3"/>'
               f'<circle cx="{x2 + 1.5:.2f}" cy="{(y1 + y2) / 2:.2f}" r="0.8" fill="#fff" stroke="#222" stroke-width="0.2" '
               f'clip-path="inset(0 50% 0 0)"/>'
               f'<text x="{(x1 + x2) / 2:.2f}" y="{(y1 + y2) / 2 + 0.8:.2f}" font-size="2" text-anchor="middle">U1 74AHCT125</text>')
    x, y = _xy(*u1_hole(1), False, ox)
    out.append(f'<text x="{x:.2f}" y="{y - 1.8:.2f}" font-size="1.4" text-anchor="middle">1</text>')
    for part, (_, pins) in SMALL_PARTS.items():
        pts = [_xy(*h, False, ox) for _, h in pins]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out.append(f'<rect x="{min(xs) - 1.3:.2f}" y="{min(ys) - 1.3:.2f}" width="{max(xs) - min(xs) + 2.6:.2f}" '
                   f'height="{max(ys) - min(ys) + 2.6:.2f}" rx="0.8" fill="none" stroke="#a33" stroke-width="0.3"/>')
        tx = max(xs) + 5 if part in ("JP", "M") else (min(xs) + max(xs)) / 2
        anchor = "start" if part in ("JP", "M") else "middle"
        ty = (min(ys) + max(ys)) / 2 + 0.7 if part in ("JP", "M") else min(ys) - 1.8
        out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-size="1.8" text-anchor="{anchor}" fill="#a33">{part}</text>')
        for label, h in pins:
            hx, hy = _xy(*h, False, ox)
            if part in ("JP", "M"):
                out.append(f'<text x="{hx + 1.6:.2f}" y="{hy + 0.45:.2f}" font-size="1.2" fill="#a33">{label}</text>')
            elif part in ("C1", "JD"):
                out.append(f'<text x="{hx:.2f}" y="{hy + 2.6:.2f}" font-size="1.2" text-anchor="middle" fill="#a33">{label}</text>')
    return out


def svg() -> str:
    panel_w = (COLS - 1) * PITCH + 10
    width, height = 2 * panel_w + 12, (ROWS - 1) * PITCH + 33
    body = _panel(0, False) + _panel(panel_w + 12, True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * 6:.0f}" height="{height * 6:.0f}" '
            f'viewBox="-2 -2 {width + 4:.2f} {height + 2:.2f}" font-family="sans-serif">\n'
            f'<rect x="-2" y="-2" width="{width + 4:.2f}" height="{height + 2:.2f}" fill="#fff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def write(svg_path: Path = SVG_FILE, table_path: Path = TABLE_FILE) -> None:
    svg_path.write_text(svg(), encoding="utf-8", newline="\n")
    table_path.write_text(table(), encoding="utf-8", newline="\n")


def main() -> None:
    write()


if __name__ == "__main__":
    main()
