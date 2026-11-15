"""docs/tree-wiring.html: one tree's pixels in wiring order, where the box and the sockets sit,
and how the box connects. Generated from data/tree-layout.json and cad/placements.json
(written by tools/cad_assembly.py), so it follows the layout and the CAD. Replaces the
hand-made "Tree Wiring Diagram" page of 7 Nov 2026 (https://claude.ai/artifact/MSrFAPvADXk8sjWY8vGcvA).

  python -m tools.gen_tree_wiring      (also run by python -m tools.build)
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.tree_layout import LAYOUT_FILE, ROOT

OUT = ROOT / "docs" / "tree-wiring.html"
PLACEMENTS = ROOT / "cad" / "placements.json"
M = 60                                         # margin round the blank, mm = svg units
COLOURS = {"outline": "--c-out", "mouth_wide": "--c-mouth", "mouth_small": "--c-mouth", "lip": "--c-lip",
           "eye_right": "--c-eye", "eye_left": "--c-eye"}
LABELS = [2, 10, 20, 30, 40, 50, 59, 60, 68, 69, 73, 74, 80, 81, 86, 87, 92]


def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def tree_svg(layout: dict, place: dict | None) -> str:
    b = layout["blank"]
    w, h = b["width"], b["height"]
    X = lambda x: x + M                     # noqa: E731  layout x -> svg
    Yl = lambda y: y + M                    # noqa: E731  layout y (down from the top) -> svg
    Yt = lambda y: h - y + M                # noqa: E731  tree Y (up from the bottom) -> svg
    out = [f'<svg viewBox="0 0 {f(w + 2 * M)} {f(h + 2 * M)}" role="img" '
           'aria-label="Front view of the tree with all 92 pixels in wiring order, the controller box and the three sockets">']
    pts = " ".join(f"{f(X(x))},{f(Yl(y))}" for x, y in b["polygon"])
    out.append(f'<polygon points="{pts}" class="blank" stroke-linejoin="round"/>')
    nodes = layout["nodes"]
    for a, c in zip(nodes, nodes[1:]):
        cls = "wire" if a["group"] == c["group"] else "jump"
        out.append(f'<line x1="{f(X(a["x"]))}" y1="{f(Yl(a["y"]))}" x2="{f(X(c["x"]))}" y2="{f(Yl(c["y"]))}" class="{cls}"/>')
    if place:
        x0, y0, x1, y1 = place["tree_box"]["footprint"]
        out.append(f'<rect x="{f(X(x0))}" y="{f(Yt(y1))}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" rx="6" class="box"/>')
        cx, cy = X((x0 + x1) / 2), Yt((y0 + y1) / 2)
        out.append(f'<text x="{f(cx)}" y="{f(cy - 4)}" class="lbl" text-anchor="middle">BOX</text>')
        out.append(f'<text x="{f(cx)}" y="{f(cy + 12)}" class="sub" text-anchor="middle">on the back</text>')
        for sx, sy in place["tree_box"]["ear_screws"]:
            out.append(f'<circle cx="{f(X(sx))}" cy="{f(Yt(sy))}" r="3" class="screw"/>')
        for s in place["sockets"]:
            sw, leg = s["width"], s["leg_h"]
            body = s.get("depth", 12)
            if s["points"] == "down":
                y_top, y_bot = Yt(leg), Yt(-body)
            else:
                y_top, y_bot = Yt(h + body), Yt(h - leg)
            out.append(f'<rect x="{f(X(s["x"] - sw / 2))}" y="{f(y_top)}" width="{f(sw)}" height="{f(y_bot - y_top)}" rx="3" class="sock"/>')
            for qx, qy in s["screws"]:
                out.append(f'<circle cx="{f(X(qx))}" cy="{f(Yt(qy))}" r="2.5" class="screw"/>')
    for n in nodes:
        r, cls = (11, "px p1") if n["n"] == 1 else (7, "px")
        out.append(f'<circle cx="{f(X(n["x"]))}" cy="{f(Yl(n["y"]))}" r="{r}" fill="var({COLOURS[n["group"]]})" class="{cls}"/>')
    cxm = w / 2
    for n in nodes:
        if n["n"] not in LABELS:
            continue
        x, y = X(n["x"]), Yl(n["y"])
        if n["group"] == "outline" and n["n"] < 12:
            out.append(f'<text x="{f(x)}" y="{f(y - 14)}" class="nn" text-anchor="middle">{n["n"]}</text>')
        elif n["group"] == "outline":
            right = n["x"] > cxm
            out.append(f'<text x="{f(x + (16 if right else -16))}" y="{f(y + 4)}" class="nn" '
                       f'text-anchor="{"start" if right else "end"}">{n["n"]}</text>')
        else:
            out.append(f'<text x="{f(x)}" y="{f(y - 12)}" class="nn" text-anchor="middle">{n["n"]}</text>')
    p1 = nodes[0]
    out.append(f'<text x="{f(X(p1["x"]) - 8)}" y="{f(Yl(p1["y"]) + 44)}" class="big">PIXEL 1</text>')
    out.append(f'<text x="{f(X(p1["x"]) - 8)}" y="{f(Yl(p1["y"]) + 60)}" class="sub">data in, base-left corner</text>')
    out.append("</svg>")
    return "\n".join(out)


CONNECTIONS = """<svg viewBox="0 0 860 520" role="img" aria-label="Wiring from the site box through the controller box to the pixel lead"><rect x="10" y="20" width="120" height="54" rx="5" class="blk site"/><text x="70" y="42" class="bt" text-anchor="middle">Site box</text><text x="70" y="60" class="bs" text-anchor="middle">3A fuse, 12V</text><path d="M130,47 L175,47" class="p12"/><text x="152" y="39" class="bl" text-anchor="middle">12V</text><rect x="175" y="20" width="130" height="54" rx="5" class="blk"/><text x="240" y="42" class="bt" text-anchor="middle">SP16 socket</text><text x="240" y="60" class="bs" text-anchor="middle">SP17 plug screws on</text><path d="M305,47 L345,47" class="p12"/><rect x="345" y="20" width="130" height="54" rx="5" class="blk"/><text x="410" y="42" class="bt" text-anchor="middle">2 x Wago 221</text><text x="410" y="60" class="bs" text-anchor="middle">+12V / 0V split</text><path d="M475,36 L525,36" class="p12"/><text x="500" y="28" class="bl" text-anchor="middle">+12V</text><path d="M475,60 L525,60" class="g"/><text x="500" y="76" class="bl" text-anchor="middle">0V</text><rect x="525" y="20" width="140" height="66" rx="5" class="blk out"/><text x="595" y="42" class="bt" text-anchor="middle">Pixel lead</text><text x="595" y="60" class="bs" text-anchor="middle">xConnect plug</text><text x="595" y="110" class="bs" text-anchor="middle">12V and 0V go straight on,</text><text x="595" y="125" class="bs" text-anchor="middle">never through the board</text><path d="M410,74 L410,150" class="p12"/><text x="418" y="118" class="bl" text-anchor="start">12V to IN+ / IN-</text><rect x="330" y="150" width="160" height="54" rx="5" class="blk"/><text x="410" y="172" class="bt" text-anchor="middle">Mini560 buck</text><text x="410" y="190" class="bs" text-anchor="middle">12V in, 5V out</text><path d="M410,204 L410,250" class="p5"/><text x="418" y="232" class="bl" text-anchor="start">5V</text><rect x="330" y="250" width="160" height="58" rx="5" class="blk esp"/><text x="410" y="272" class="bt" text-anchor="middle">ESP32 DevKitC-32U</text><text x="410" y="290" class="bs" text-anchor="middle">WLED, antenna on shelf</text><path d="M490,279 L540,279" class="d"/><text x="515" y="270" class="bl" text-anchor="middle">GPIO16</text><text x="515" y="296" class="bl" text-anchor="middle">3.3V data</text><rect x="540" y="250" width="140" height="58" rx="5" class="blk"/><text x="610" y="272" class="bt" text-anchor="middle">74AHCT125</text><text x="610" y="290" class="bs" text-anchor="middle">powered from 5V</text><path d="M610,308 L610,350" class="d"/><rect x="540" y="350" width="140" height="44" rx="5" class="blk"/><text x="610" y="377" class="bt" text-anchor="middle">R1 33 ohm</text><path d="M610,394 L610,430" class="d"/><text x="618" y="418" class="bl" text-anchor="start">5V data</text><rect x="540" y="430" width="140" height="54" rx="5" class="blk jd"/><text x="610" y="452" class="bt" text-anchor="middle">JD terminal</text><text x="610" y="470" class="bs" text-anchor="middle">DATA and GND</text><path d="M680,457 L730,457 L730,53 L665,53" class="d"/><path d="M660,53 l10,-5 l0,10 z" class="dfill"/><text x="738" y="250" class="bl" text-anchor="start">data wire</text><text x="738" y="266" class="bl" text-anchor="start">to pixel 1</text><text x="10" y="508" class="bs">Amber 12V, blue 5V, green data, grey 0V</text></svg>"""

STYLE = """:root{--bg:#f3f1ec;--fg:#1d2220;--mut:#5d655f;--line:#c9c6bc;--wood:#e4d2b0;--woodln:#9a8560;
--c-out:#2f6f9f;--c-mouth:#c2410c;--c-lip:#b4236b;--c-eye:#2f8a4e;--p12:#b7791f;--p5:#2b6cb0;--dat:#1f8a4c;--gnd:#6b716d;--panel:#fbfaf7;--hi:#d9261c;--sock:#3b7dd8;
--disp:'Barlow Condensed',sans-serif;--body:'Barlow',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14181a;--fg:#e8e6df;--mut:#9aa39c;--line:#394043;--wood:#3a3226;--woodln:#8c7a58;--c-out:#6fb0e0;--c-mouth:#f08a4b;--c-lip:#f06aa8;--c-eye:#62d08a;--p12:#e8a93a;--p5:#6fb0f0;--dat:#4fd18a;--gnd:#98a09a;--panel:#1b2124;--hi:#ff5a4d;--sock:#6fa9ef;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#14181a;--fg:#e8e6df;--mut:#9aa39c;--line:#394043;--wood:#3a3226;--woodln:#8c7a58;--c-out:#6fb0e0;--c-mouth:#f08a4b;--c-lip:#f06aa8;--c-eye:#62d08a;--p12:#e8a93a;--p5:#6fb0f0;--dat:#4fd18a;--gnd:#98a09a;--panel:#1b2124;--hi:#ff5a4d;--sock:#6fa9ef;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);padding-block:24px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));margin:0}
main{max-width:1180px;margin:0 auto;display:grid;gap:24px}
h1{font:600 2.2rem/1 var(--disp);letter-spacing:.02em;margin:0;text-transform:uppercase;text-wrap:balance}
h2{font:600 1.15rem/1 var(--disp);letter-spacing:.08em;text-transform:uppercase;margin:0 0 10px;color:var(--mut)}
p{margin:6px 0 0;color:var(--mut);max-width:65ch}
.grid{display:grid;grid-template-columns:minmax(0,420px) minmax(0,1fr);gap:24px;align-items:start}
@media(max-width:820px){.grid{grid-template-columns:minmax(0,1fr)}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px;min-width:0}
svg{width:100%;height:auto;display:block}
.scroll{overflow-x:auto}.scroll svg{min-width:560px}
.blank{fill:var(--wood);stroke:var(--woodln);stroke-width:2}
.wire{stroke:var(--mut);stroke-width:1.5;opacity:.7}
.jump{stroke:var(--mut);stroke-width:1.2;stroke-dasharray:4 4;opacity:.6}
.px{stroke:var(--panel);stroke-width:1.5}
.p1{stroke:var(--hi);stroke-width:4}
.nn{font:500 11px var(--mono);fill:var(--fg)}
.big{font:700 24px var(--disp);fill:var(--hi);letter-spacing:.05em}
.sub{font:12px var(--body);fill:var(--mut)}
.lbl{font:600 15px var(--disp);letter-spacing:.1em;fill:var(--fg)}
.box{fill:var(--panel);fill-opacity:.55;stroke:var(--fg);stroke-width:2;stroke-dasharray:7 5}
.sock{fill:var(--sock);fill-opacity:.35;stroke:var(--sock);stroke-width:1.5}
.screw{fill:var(--fg)}
.blk{fill:var(--bg);stroke:var(--fg);stroke-width:1.5}
.blk.site{stroke:var(--p12)}.blk.out{stroke:var(--hi);stroke-width:2.5}.blk.esp{stroke:var(--p5)}.blk.jd{stroke:var(--dat)}
.bt{font:600 16px var(--disp);letter-spacing:.04em;fill:var(--fg)}
.bs{font:12px var(--body);fill:var(--mut)}.bl{font:11px var(--mono);fill:var(--mut)}
.p12{stroke:var(--p12);stroke-width:3;fill:none}.p5{stroke:var(--p5);stroke-width:3}.d{stroke:var(--dat);stroke-width:3;fill:none}.g{stroke:var(--gnd);stroke-width:3}.dfill{fill:var(--dat)}
.key{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.85rem;margin-top:10px}
.key i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
ul{margin:10px 0 0;padding-left:1.1em;color:var(--mut);line-height:1.5}li{max-width:70ch;margin-bottom:4px}"""


def page(layout: dict, place: dict | None) -> str:
    groups = layout["groups"]
    rng = lambda g: f"{groups[g][0]}-{groups[g][-1]}" if isinstance(groups[g], list) else str(groups[g])  # noqa: E731
    if place:
        tb = place["tree_box"]
        where = (f"The box (dashed, on the back face) sits with its plate {tb['plate_left_x']:g}mm in from the tree's "
                 f"left edge and its cover's bottom {tb['cover_bottom_y']:g}mm up, so the 12V plug under it ends above "
                 "the bottom edge; black dots are its four ear screws and the sockets' screws, all clear of the pixel holes. "
                 "The blue blocks are the three sockets (cad/parts/tree-mounts.FCStd).")
    else:
        where = "Run python -m tools.cad to place the box and the sockets."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by tools/gen_tree_wiring.py from data/tree-layout.json and cad/placements.json. Don't edit. -->
<title>Tree Wiring Diagram</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500&family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
{STYLE}
</style>
</head>
<body>
<main>
<header><h1>Stair Tree Choir tree wiring</h1><p>One tree, seen from the front, to scale. The string runs in wiring order from pixel 1 at the base-left corner. {where}</p></header>
<div class="grid">
<section class="card"><h2>Pixel layout, {len(layout["nodes"])} nodes</h2>{tree_svg(layout, place)}
<div class="key"><span><i style="background:var(--hi)"></i>Pixel 1 (data in)</span><span><i style="background:var(--c-out)"></i>Outline {rng("outline")}</span><span><i style="background:var(--c-mouth)"></i>Mouth {groups["mouth_wide"][0]}-{groups["mouth_small"][-1]}</span><span><i style="background:var(--c-lip)"></i>Lip {rng("lip")}</span><span><i style="background:var(--c-eye)"></i>Eyes {groups["eye_right"][0]}-{groups["eye_left"][-1]}</span></div></section>
<section class="card"><h2>Connections to the box</h2><div class="scroll">{CONNECTIONS}</div>
<ul>
<li>Outline: base-left, along the base, up the right edge, over the apex and down the left edge, ending at node {groups["outline"][-1]}.</li>
<li>Then mouth wide {rng("mouth_wide")} (left to right), mouth small {rng("mouth_small")} (right to left), lip {rng("lip")} (left to right), the viewer's right eye {rng("eye_right")}, the viewer's left eye {rng("eye_left")}. Dashed grey lines are leads that hop between groups on the back.</li>
<li>Pixel 1 takes the 5V data wire from the 74AHCT125 through R1 (33 ohm) and the JD terminal. The pixel lead leaves through the PG7 gland in the shelf and meets the tree's own lead at the xConnect plug.</li>
<li>Pixel power (about 2.1A per tree) goes from the Wagos straight to the string. 12V reaches the board only at the Mini560 input.</li>
<li>The sockets' screws go into the back face 5mm in from the edge, 12mm deep; the leads run between the pixel holes 22mm in, so keep the leads off the bottom 12mm of the back face.</li>
</ul></section>
</div>
<p>Check the xConnect wire colours with a meter before powering. Clearances: docs/cad-checks.md. The board itself: electronics/README.md.</p>
</main>
</body>
</html>
"""


def groups_as_ranges(layout: dict) -> dict:
    out = {}
    for n in layout["nodes"]:
        out.setdefault(n["group"], []).append(n["n"])
    return out


def main() -> None:
    layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    layout["groups"] = groups_as_ranges(layout)
    place = json.loads(PLACEMENTS.read_text(encoding="utf-8")) if PLACEMENTS.exists() else None
    OUT.write_text(page(layout, place), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
