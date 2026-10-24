import xml.etree.ElementTree as ET

import pytest

from tools import gen_xmodel
from tools.tree_layout import build_layout, load_blank


@pytest.fixture(scope="module")
def layout():
    return build_layout(load_blank())


@pytest.fixture(scope="module")
def model(layout, tmp_path_factory):
    path = tmp_path_factory.mktemp("x") / "t.xmodel"
    gen_xmodel.write(gen_xmodel.build(layout), path)
    return ET.parse(path).getroot()


def expand(r):
    out = []
    for part in r.split(","):
        a, _, b = part.partition("-")
        out += range(int(a), int(b or a) + 1)
    return out


def test_grid_holds_every_node_once(model):
    rows = model.get("CustomModel").split(";")
    assert len(rows) == int(model.get("CustomHeight"))
    cells = [c for row in rows for c in row.split(",")]
    assert all(len(row.split(",")) == int(model.get("CustomWidth")) for row in rows)
    nodes = sorted(int(c) for c in cells if c)
    assert nodes == list(range(1, 93))


def test_grid_matches_positions(model, layout):
    rows = [row.split(",") for row in model.get("CustomModel").split(";")]
    for n in layout["nodes"]:
        r, c = round(n["y"] / gen_xmodel.CELL_MM), round(n["x"] / gen_xmodel.CELL_MM)
        assert rows[r][c] == str(n["n"])


def test_face_definition(model):
    face = model.find("faceInfo").attrib
    assert face["Type"] == "NodeRange"
    for p in ("AI", "E", "FV", "L", "MBP", "O", "U", "WQ", "etc", "rest"):
        assert f"Mouth-{p}" in face
    assert expand(face["Mouth-rest"]) == list(range(74, 81))
    assert expand(face["Mouth-AI"]) == list(range(60, 69)) + list(range(74, 81))
    assert expand(face["Mouth-MBP"]) == list(range(75, 80))
    assert expand(face["Mouth-FV"]) == [70, 71, 72] + list(range(74, 81))
    assert expand(face["Mouth-O"]) == list(range(69, 74)) + list(range(75, 80))
    assert expand(face["Mouth-U"]) == expand(face["Mouth-WQ"]) == [70, 71, 72, 76, 77, 78]
    lip = set(range(74, 81))
    for p in ("AI", "E", "FV", "L", "MBP", "O", "U", "WQ", "etc", "rest"):
        assert lip & set(expand(face[f"Mouth-{p}"])), f"{p} has no top lip"
    assert expand(face["FaceOutline"]) == list(range(1, 60))
    assert expand(face["Eyes-Open"]) == list(range(81, 93))
    assert expand(face["Eyes-Closed"]) == [83, 84, 85, 89, 90, 91]


def test_submodels(model):
    subs = {s.get("name"): expand(s.get("line0")) for s in model.findall("subModel")}
    assert subs["Outline"] == list(range(1, 60))
    assert subs["Eyes"] == list(range(81, 93))


def test_ranges():
    assert gen_xmodel.ranges([1, 2, 3, 5, 7, 8]) == "1-3,5,7-8"
