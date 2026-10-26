"""The printed parts as STEP (tools/gen_printed.py), checked on the committed files."""

import pytest

cq = pytest.importorskip("cadquery")

from tools import gen_printed  # noqa: E402
from tools.gen_step import tree_solid  # noqa: E402
from tools.tree_layout import build_layout, load_blank  # noqa: E402

if not gen_printed.KIT_FILE.exists():
    pytest.skip("run python -m tools.gen_printed first", allow_module_level=True)


@pytest.fixture(scope="module")
def layout():
    return build_layout(load_blank())


@pytest.fixture(scope="module")
def tree(layout):
    return tree_solid(layout).val()


def placed(layout, name):
    side = "right" if name.endswith("right") else "left"
    shape = cq.importers.importStep(str(gen_printed.PRINTED_DIR / f"{name}.step")).val()
    return shape.moved(gen_printed.boot_to_tree(layout, f"fixing_bottom_{side}"))


def test_every_part_is_a_closed_solid():
    for p in gen_printed.STEPS:
        shape = cq.importers.importStep(str(gen_printed.PRINTED_DIR / f"{p.out}.step")).val()
        assert shape.isValid(), p.out
        assert shape.Volume() > 0, p.out


@pytest.mark.parametrize("name", ["boot-left", "boot-right", "peg-left", "peg-right",
                                  "tree-box-box-on-boot", "tree-box-lid-on-boot"])
def test_fitted_parts_clear_the_tree(layout, tree, name):
    # Facets cut a hair inside curved holes, so allow a sliver.
    assert tree.intersect(placed(layout, name)).Volume() < 5


def test_pegs_go_into_the_old_fixing_holes(layout):
    holes = {h["name"]: h for h in layout["blank"]["existing_holes"]}
    for side in ("left", "right"):
        bb = placed(layout, f"peg-{side}").BoundingBox()
        h = holes[f"fixing_bottom_{side}"]
        assert bb.xmin < h["x"] < bb.xmax
        assert bb.zmin < -layout["blank"]["thickness"] < bb.zmax  # shaft into the back face, head behind it


def test_control_boot_is_at_node_1(layout):
    # Node 1 (data in) is at the base-left seen from the front; the box sits behind the tree on that side.
    node1 = layout["nodes"][0]
    box = placed(layout, "tree-box-box-on-boot").BoundingBox()
    assert node1["x"] < layout["blank"]["width"] / 2
    assert box.xmax < layout["blank"]["width"] / 2
    assert box.zmax < -layout["blank"]["thickness"]


def test_boots_stand_on_the_ground(layout):
    shelf = gen_printed.foot_param("clearance")
    for side in ("left", "right"):
        assert placed(layout, f"boot-{side}").BoundingBox().ymin == pytest.approx(-shelf, abs=0.01)
