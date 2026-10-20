import math

import pytest

from tools.tree_layout import GROUP_ORDER, Params, build_layout, dumps, load_blank


@pytest.fixture(scope="module")
def layout():
    return build_layout(load_blank())


def dist_to_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.dist(p, (a[0] + dx * t, a[1] + dy * t))


def test_node_count(layout):
    assert layout["node_count"] == 92
    assert [n["n"] for n in layout["nodes"]] == list(range(1, 93))


def test_groups_match_brief(layout):
    assert layout["groups"] == {
        "outline": [1, 59], "mouth_wide": [60, 68], "mouth_small": [69, 73],
        "lip": [74, 80], "eye_right": [81, 86], "eye_left": [87, 92],
    }
    assert list(layout["groups"]) == list(GROUP_ORDER)


def test_min_spacing(layout):
    pts = [(n["x"], n["y"]) for n in layout["nodes"]]
    closest = min(math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:])
    assert closest >= 24.0


def test_edge_clearance(layout):
    poly = layout["blank"]["polygon"]
    for n in layout["nodes"]:
        d = min(dist_to_segment((n["x"], n["y"]), a, b) for a, b in zip(poly, poly[1:] + poly[:1]))
        assert d >= 16.0, n


def test_outline_starts_base_left(layout):
    first = layout["nodes"][0]
    assert (first["x"], first["y"]) == (27.4, 878.0)


def test_deterministic():
    assert dumps(build_layout(load_blank())) == dumps(build_layout(load_blank()))


def test_concave_blank_rejected():
    blank = {"polygon": [(0, 0), (100, 0), (50, 20), (100, 100), (0, 100)], "corners": [True] * 5}
    with pytest.raises(ValueError):
        build_layout(blank, Params())
