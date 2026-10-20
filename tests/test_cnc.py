import math
import re

import ezdxf

from tools import gen_cnc
from tools.tree_layout import build_layout, load_blank


def generate(tmp_path):
    cp = gen_cnc.CncParams()
    g = gen_cnc.geometry(build_layout(load_blank()), cp)
    svg, dxf = tmp_path / "t.svg", tmp_path / "t.dxf"
    gen_cnc.write_svg(g, cp, svg)
    gen_cnc.write_dxf(g, cp, dxf)
    return g, svg, dxf


def test_svg_viewbox_is_blank_size(tmp_path):
    g, svg, _ = generate(tmp_path)
    text = svg.read_text()
    w, h = gen_cnc.fmt(g["width"]), gen_cnc.fmt(g["height"])
    assert f'viewBox="0 0 {w} {h}"' in text
    assert f'width="{w}mm" height="{h}mm"' in text
    assert len(re.findall(r'<g id="FRONT_HOLES".*?</g>', text, re.S)[0].split("<circle")) - 1 == 92


def test_back_channel_visits_every_hole_mirrored_in_order(tmp_path):
    g, _, _ = generate(tmp_path)
    remaining = iter(g["channel"])
    for hx, hy in g["holes"]:
        assert any(abs(hx + cx - g["width"]) < 1e-9 and hy == cy for cx, cy in remaining)


def test_channel_clear_of_existing_holes(tmp_path):
    g, _, _ = generate(tmp_path)
    cp = gen_cnc.CncParams()
    for (c, dia) in g["existing"]:
        if dia < cp.channel_avoid_min_dia:
            continue
        for a, b in zip(g["channel"], g["channel"][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            t = max(0.0, min(1.0, ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / (dx * dx + dy * dy)))
            d = math.dist(c, (a[0] + dx * t, a[1] + dy * t))
            # Channel ends at a node; only the far side of a node's own hole can come close.
            assert d - dia / 2 - cp.channel_width / 2 >= cp.channel_hole_wall - 0.1 or t in (0.0, 1.0), (c, a, b)


def test_dxf_layers_and_units(tmp_path):
    _, _, dxf = generate(tmp_path)
    doc = ezdxf.readfile(dxf)
    assert doc.units == ezdxf.units.MM
    msp = doc.modelspace()
    assert len(msp.query('CIRCLE[layer=="FRONT_HOLES"]')) == 92
    assert len(msp.query('LWPOLYLINE[layer=="BACK_CHANNEL"]')) == 1


def test_outputs_deterministic(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    _, svg1, dxf1 = generate(tmp_path / "a")
    _, svg2, dxf2 = generate(tmp_path / "b")
    assert svg1.read_bytes() == svg2.read_bytes()
    assert dxf1.read_bytes() == dxf2.read_bytes()
