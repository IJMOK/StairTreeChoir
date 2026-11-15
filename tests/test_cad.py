"""The CAD: the committed exports, and geometry checks run in FreeCAD (tests/fc_checks.py)
when freecadcmd is installed."""

import json
import re
import struct
import subprocess

import pytest

from tools import cad
from tools.tree_layout import ROOT

PRINT = sorted((ROOT / "print").glob("*.stl"))


def test_print_files_exist():
    names = {p.stem for p in PRINT}
    for n in ("tree-box-base", "tree-box-cover", "tree-socket", "tree-ski", "tree-tower", "psu-hood",
              "pixel-disk", "step-clamp", "pod-buck-base", "pod-buck-lid"):
        assert n in names


@pytest.mark.parametrize("path", PRINT, ids=[p.name for p in PRINT])
def test_stls_are_binary_and_whole(path):
    data = path.read_bytes()
    assert len(data) == 84 + 50 * struct.unpack("<I", data[80:84])[0]


@pytest.mark.parametrize("path", PRINT, ids=[p.name for p in PRINT])
def test_every_print_file_has_a_step_or_preview(path):
    assert (ROOT / "cad" / "previews" / f"{path.stem}.png").exists()


def test_print_readme_lists_every_file():
    text = (ROOT / "print" / "README.md").read_text(encoding="utf-8")
    for p in PRINT:
        assert f"]({p.name})" in text


def test_no_openscad_or_cadquery_left():
    """Single source of truth: every live part is a FreeCAD master (Rob, 15 Nov 2026)."""
    live = [p for p in ROOT.rglob("*.scad") if "archive" not in p.parts and ".venv" not in p.parts]
    assert not live
    for py in (ROOT / "tools").glob("*.py"):
        assert "import cadquery" not in py.read_text(encoding="utf-8"), py


def test_cad_checks_all_pass():
    text = (ROOT / "docs" / "cad-checks.md").read_text(encoding="utf-8")
    assert "**" not in text, "a check in docs/cad-checks.md failed"


def test_mount_sizes_hang_together():
    mp = json.loads((ROOT / "cad" / "parts" / "tree-mounts-params.json").read_text(encoding="utf-8"))
    assert mp["ten_l"] + 0.5 < mp["ski_h"]                    # the ski's pocket has a floor
    assert mp["base_t"] + mp["ten_l"] + 0.5 < mp["bore_yc"] - (mp["spig_d"] / 2 + mp["spig_clr"])  # pocket and bore don't meet
    assert mp["sock_w"] <= 56                                # fits the flat at the tree's top
    assert mp["spig_w"] + 2 * mp["spig_clr"] < mp["col_w"]   # the recess has walls
    assert 16 - mp["wall"] < mp["tree_t"] - 15               # the screws stop well short of the front


@pytest.fixture(scope="module")
def fc():
    exe = cad.freecadcmd()
    if not exe:
        pytest.skip("freecadcmd not installed")
    run = subprocess.run([exe, "-c", "exec(open('tests/fc_checks.py').read())"], cwd=ROOT,
                         capture_output=True, text=True, errors="replace", timeout=900)
    found = re.search(r"RESULT:(\{.*\})", run.stdout)     # FreeCAD's progress counter can share the line
    assert found, run.stdout[-3000:] + run.stderr[-3000:]
    return json.loads(found[1])


EXPECTED = [
    "tree is one valid solid", "tree spans the thickness", "tree symmetric",
    "tree volume = slab - pixel holes - old holes", "one counterbore floor per pixel", "tree sits in the plate pocket",
    "tree box base: one solid with real surfaces", "tree box cover: one solid with real surfaces",
    "tree box sizes follow the spreadsheet", "tree box base and cover don't clash",
    "cover screw clears the cover wall and the boss bore", "shelf reaches the cover's side walls",
    "ski and tower take the socket's tenon", "towers stack without clashing", "tower bore runs right through",
    "spigot sits in the recess above", "ski is hollow either side, solid at the pocket", "socket is one valid solid", "ski is one valid solid", "tower is one valid solid",
    "socket channel takes the tread", "hood is one valid solid", "hood clears the PSU",
    "hood M4 screws reach 5mm max into the case", "hood has a closed floor under the chamber",
    "hood partition between mains and 12V",
    *[f"master {n} recomputes" for n in ("tree-box", "player-pods", "psu-cover", "tree-mounts", "pixel-disk", "step-clamp")],
]


@pytest.mark.parametrize("name", EXPECTED)
def test_freecad_geometry(fc, name):
    ok, detail = fc[name]
    assert ok, detail
