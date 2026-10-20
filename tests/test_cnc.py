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
    _, svg, _ = generate(tmp_path)
    text = svg.read_text()
    assert 'viewBox="0 0 400 900"' in text
    assert 'width="400mm" height="900mm"' in text
    assert len(re.findall(r'<g id="FRONT_HOLES".*?</g>', text, re.S)[0].split("<circle")) - 1 == 92


def test_back_is_mirrored(tmp_path):
    g, _, _ = generate(tmp_path)
    for (hx, hy), (cx, cy) in zip(g["holes"], g["channel"]):
        assert abs(hx + cx - g["width"]) < 1e-9 and hy == cy


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
