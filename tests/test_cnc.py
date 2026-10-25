import math
import re

import ezdxf

from tools import gen_cnc
from tools.tree_layout import build_layout, load_blank


def generate(tmp_path):
    g = gen_cnc.geometry(build_layout(load_blank()))
    svg, dxf = tmp_path / "t.svg", tmp_path / "t.dxf"
    gen_cnc.write_svg(g, svg)
    gen_cnc.write_dxf(g, dxf)
    return g, svg, dxf


def test_svg_viewbox_is_blank_size(tmp_path):
    g, svg, _ = generate(tmp_path)
    text = svg.read_text()
    w, h = gen_cnc.fmt(g["width"]), gen_cnc.fmt(g["height"])
    assert f'viewBox="0 0 {w} {h}"' in text
    assert f'width="{w}mm" height="{h}mm"' in text
    for layer in ("FRONT_HOLES", "FRONT_COUNTERBORE"):
        assert len(re.findall(rf'<g id="{layer}".*?</g>', text, re.S)[0].split("<circle")) - 1 == 92


def test_front_only(tmp_path):
    _, svg, dxf = generate(tmp_path)
    assert "BACK_" not in svg.read_text() and "mirrored" not in svg.read_text()
    assert not [layer.dxf.name for layer in ezdxf.readfile(dxf).layers if layer.dxf.name.startswith("BACK_")]


def test_wood_between_counterbores(tmp_path):
    g, _, _ = generate(tmp_path)
    pts = g["holes"]
    closest = min(math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:])
    assert closest - g["counterbore_dia"] >= 4.0


def test_dxf_layers_and_units(tmp_path):
    _, _, dxf = generate(tmp_path)
    doc = ezdxf.readfile(dxf)
    assert doc.units == ezdxf.units.MM
    msp = doc.modelspace()
    assert len(msp.query('CIRCLE[layer=="FRONT_HOLES"]')) == 92
    assert len(msp.query('CIRCLE[layer=="FRONT_COUNTERBORE"]')) == 92


def test_outputs_deterministic(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    _, svg1, dxf1 = generate(tmp_path / "a")
    _, svg2, dxf2 = generate(tmp_path / "b")
    assert svg1.read_bytes() == svg2.read_bytes()
    assert dxf1.read_bytes() == dxf2.read_bytes()
