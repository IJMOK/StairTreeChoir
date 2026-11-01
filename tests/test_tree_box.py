"""The tree box as exported from its FreeCAD master (tools/tree_box_export.py), checked on
the committed files."""

import json
import struct

import pytest

cq = pytest.importorskip("cadquery")

from tools.gen_components import PARAMS_FILE  # noqa: E402
from tools.gen_printed import PRINTED_DIR  # noqa: E402
from tools.tree_layout import ROOT  # noqa: E402


@pytest.fixture(scope="module")
def p():
    return json.loads(PARAMS_FILE.read_text(encoding="utf-8"))


def solid(name):
    return cq.importers.importStep(str(PRINTED_DIR / f"tree-box-{name}.step")).val()


@pytest.mark.parametrize("name", ["base", "cover"])
def test_one_valid_solid_with_real_surfaces(name):
    shape = solid(name)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert len(shape.Faces()) < 500           # a mesh-made solid has thousands


def test_base_and_cover_sizes_follow_the_spreadsheet(p):
    base, cover = solid("base").BoundingBox(), solid("cover").BoundingBox()
    assert base.xmin == pytest.approx(-p["ear_w"], abs=0.01)
    assert base.xmax == pytest.approx(p["box_w"] + p["ear_w"], abs=0.01)
    assert base.zmax == pytest.approx(p["plate_top"], abs=0.01)
    assert cover.xlen == pytest.approx(p["box_w"] + 2 * p["wrap"], abs=0.01)
    assert cover.ymax == pytest.approx(p["cover_y1"], abs=0.01)
    assert cover.ymin == pytest.approx(-p["hook_fit"] - p["hook_back"], abs=0.01)


def test_base_and_cover_do_not_clash():
    assert solid("base").intersect(solid("cover")).Volume() < 1


def test_screw_lines_up_through_cover_and_boss(p):
    """The screw's axis clears the cover's wall and the insert's hole, right through the boss."""
    s = p["s2"]
    at = lambda t, x=0.0: cq.Vector(p["boss_x"] + x, p["screw_y"] - t * s, p["screw_z"] + t * s)
    assert not solid("cover").isInside(at(-p["bevel_t"] / 2))
    base = solid("base")
    assert all(not base.isInside(at(t)) for t in (1, 5, 9, 11))
    assert base.isInside(at(5, p["m3_insert_d"] / 2 + 1))         # the boss's wall round it


def test_shelf_reaches_the_covers_side_walls(p):
    """No slot at the shelf's ends: only the cover's fit between them and its walls."""
    base = solid("base")
    z = p["lip_t"] + p["floor_t"] / 2
    assert base.isInside(cq.Vector(0.1, 20, z))
    assert base.isInside(cq.Vector(p["box_w"] - 0.1, 20, z))
    assert solid("cover").isInside(cq.Vector(p["ix0"] - 1, 20, z))


@pytest.mark.parametrize("name", ["base", "cover", "spacer", "coupon", "seal-test"])
def test_stls_are_binary_and_whole(name):
    data = (ROOT / "enclosure" / f"tree-box-{name}.stl").read_bytes()
    assert len(data) == 84 + 50 * struct.unpack("<I", data[80:84])[0]
