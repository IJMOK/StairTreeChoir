"""xLights custom model from data/tree-layout.json: xlights/StairTree.xmodel.

Format checked against the xLights source (xLightsSequencer/xLights 75c3e11,
20 Oct 2026):
  <custommodel> root with CustomWidth/CustomHeight/Depth and a CustomModel grid
  string: rows split by ';', cells by ',', empty cell = no node, top row first
  (XmlSerializeFunctions.cpp ParseCustomModel, LoadCustomModelFromXml).
  <faceInfo Type="NodeRange"> keys read by the Faces effect: Mouth-<phoneme>,
  Eyes-Open, Eyes-Closed, FaceOutline, CustomColors and <key>-Color
  (FacesEffect.cpp RenderFaces). Values are 1-based node ranges "a-b,c".
  <subModel type="ranges" line0="..."> for each node group (ParseSubModelNode).
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.tree_layout import LAYOUT_FILE, ROOT, phoneme_nodes

XMODEL_FILE = ROOT / "xlights" / "StairTree.xmodel"
MODEL_NAME = "StairTree"
CELL_MM = 10.0  # one grid cell = 10mm, so the model keeps the tree's real proportions

# Eye hexagons run top, upper-right, lower-right, bottom, lower-left, upper-left;
# a closed eye keeps the lower three (a lid line).
CLOSED_EYE_OFFSETS = (2, 3, 4)

COLOURS = {"mouth": "#FF0000", "eyes": "#FFFFFF", "outline": "#00FF00"}

SUBMODELS = [
    ("Outline", ["outline"]),
    ("Mouth", ["mouth_wide", "mouth_small", "lip"]),
    ("Mouth Wide", ["mouth_wide"]),
    ("Mouth Small", ["mouth_small"]),
    ("Lip", ["lip"]),
    ("Eyes", ["eye_right", "eye_left"]),
    ("Eye Right", ["eye_right"]),
    ("Eye Left", ["eye_left"]),
]


def ranges(nodes: list[int]) -> str:
    """Compress sorted node numbers into xLights range syntax: 1-5,7,9-10."""
    nodes = sorted(set(nodes))
    out, start = [], None
    for i, n in enumerate(nodes):
        if start is None:
            start = n
        if i + 1 == len(nodes) or nodes[i + 1] != n + 1:
            out.append(f"{start}" if start == n else f"{start}-{n}")
            start = None
    return ",".join(out)


def group_nodes(layout: dict, groups: list[str]) -> list[int]:
    nodes = []
    for g in groups:
        first, last = layout["groups"][g]
        nodes += range(first, last + 1)
    return nodes


def grid(layout: dict) -> list[list[int]]:
    width = round(layout["blank"]["width"] / CELL_MM) + 1
    height = round(layout["blank"]["height"] / CELL_MM) + 1
    cells = [[-1] * width for _ in range(height)]
    for n in layout["nodes"]:
        row, col = round(n["y"] / CELL_MM), round(n["x"] / CELL_MM)
        if cells[row][col] != -1:
            raise ValueError(f"nodes {cells[row][col]} and {n['n']} share grid cell {row},{col}; use a smaller CELL_MM")
        cells[row][col] = n["n"]
    return cells


def custom_model_string(cells: list[list[int]]) -> str:
    return ";".join(",".join("" if c < 0 else str(c) for c in row) for row in cells)


def face_info(layout: dict) -> dict[str, str]:
    eye_r, eye_l = layout["groups"]["eye_right"][0], layout["groups"]["eye_left"][0]
    attrs = {"Name": MODEL_NAME, "Type": "NodeRange", "CustomColors": "1"}
    # xLights phonemes (FacesEffect.cpp phonemeMap) -> layout["phonemes"] (CLAUDE.md §3).
    for phoneme, spec in sorted(layout["phonemes"].items()):
        attrs[f"Mouth-{phoneme}"] = ranges(phoneme_nodes(layout["groups"], spec))
        attrs[f"Mouth-{phoneme}-Color"] = COLOURS["mouth"]
    attrs["Eyes-Open"] = ranges(group_nodes(layout, ["eye_right", "eye_left"]))
    attrs["Eyes-Open-Color"] = COLOURS["eyes"]
    attrs["Eyes-Closed"] = ranges([first + o for first in (eye_r, eye_l) for o in CLOSED_EYE_OFFSETS])
    attrs["Eyes-Closed-Color"] = COLOURS["eyes"]
    attrs["FaceOutline"] = ranges(group_nodes(layout, ["outline"]))
    attrs["FaceOutline-Color"] = COLOURS["outline"]
    return attrs


def build(layout: dict) -> ET.Element:
    cells = grid(layout)
    root = ET.Element("custommodel", {
        "name": MODEL_NAME,
        "CustomWidth": str(len(cells[0])),
        "CustomHeight": str(len(cells)),
        "Depth": "1",
        "StringType": "RGB Nodes",
        "Transparency": "0",
        "PixelSize": "2",
        "Antialias": "1",
        "StrandNames": "",
        "NodeNames": "",
        "PixelCount": str(layout["node_count"]),
        "PixelType": "WS2811",
        "LayoutGroup": "Default",
        "CustomModel": custom_model_string(cells),
    })
    ET.SubElement(root, "faceInfo", face_info(layout))
    for name, groups in SUBMODELS:
        ET.SubElement(root, "subModel", {
            "name": name,
            "layout": "horizontal",
            "type": "ranges",
            "bufferstyle": "Default",
            "line0": ranges(group_nodes(layout, groups)),
        })
    return root


def write(root: ET.Element, path: Path = XMODEL_FILE) -> None:
    ET.indent(root)
    text = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    write(build(layout))
    print(f"wrote {XMODEL_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
