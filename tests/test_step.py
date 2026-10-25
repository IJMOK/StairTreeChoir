import math

import pytest

cq = pytest.importorskip("cadquery")

from tools import gen_step  # noqa: E402
from tools.tree_layout import build_layout, load_blank  # noqa: E402


@pytest.fixture(scope="module")
def layout():
    return build_layout(load_blank())


@pytest.fixture(scope="module")
def tree_file(layout, tmp_path_factory):
    path = tmp_path_factory.mktemp("step") / "tree.step"
    gen_step.write(gen_step.tree_solid(layout), path)
    return path


def test_tree_bounding_box(layout, tree_file):
    bb = cq.importers.importStep(str(tree_file)).val().BoundingBox()
    b = layout["blank"]
    assert (bb.zmin, bb.zmax) == pytest.approx((-b["thickness"], 0), abs=0.01)
    # The rounded corners pull the extents in from the sharp polygon, by less than the radius.
    r = b["corner_radius"]
    assert -0.01 < bb.xmin < r and -0.01 < bb.ymin < r
    assert b["width"] - r < bb.xmax < b["width"] + 0.01 and b["height"] - r < bb.ymax < b["height"] + 0.01
    assert bb.xmin + bb.xmax == pytest.approx(b["width"], abs=0.01)  # still symmetric


def test_one_counterbore_floor_per_pixel(layout, tree_file):
    depth = layout["params"]["front_counterbore_depth"]
    planes = cq.importers.importStep(str(tree_file)).faces("%PLANE").vals()
    floors = [f for f in planes if abs(f.Center().z + depth) < 1e-6]
    assert len(floors) == 92


def test_volume_removed(layout, tree_file):
    b, p = layout["blank"], layout["params"]
    slab = gen_step.outline(layout, 0, b["thickness"]).val().Volume()
    r_cb, r_cl, d_cb = p["front_counterbore_dia"] / 2, p["clearance_dia"] / 2, p["front_counterbore_depth"]
    pixels = 92 * math.pi * (r_cb ** 2 * d_cb + r_cl ** 2 * (b["thickness"] - d_cb))
    old = sum(math.pi * (h["dia"] / 2) ** 2 * h["depth"] for h in b["existing_holes"])
    assert cq.importers.importStep(str(tree_file)).val().Volume() == pytest.approx(slab - pixels - old, rel=1e-3)


def test_tree_sits_in_plate_pocket(layout):
    tree, plate = gen_step.tree_solid(layout).val(), gen_step.plate_solid(layout).val()
    assert tree.intersect(plate).Volume() == pytest.approx(0, abs=1e-3)
    fp = gen_step.FixtureParams()
    assert plate.BoundingBox().zmax == pytest.approx(-layout["blank"]["thickness"] + fp.pocket_depth)


def test_deterministic(layout, tree_file, tmp_path):
    again = tmp_path / "tree.step"
    gen_step.write(gen_step.tree_solid(layout), again)
    assert again.read_bytes() == tree_file.read_bytes()
