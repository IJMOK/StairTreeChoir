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
    for n in ("tree-box-base", "tree-box-cover", "tree-socket", "tree-tower", "tree-stand", "tree-pole-cap", "tree-plate", "psu-hood",
              "pixel-disk", "step-clamp", "pod-buck-base", "pod-buck-lid"):
        assert n in names


@pytest.mark.parametrize("path", PRINT, ids=[p.name for p in PRINT])
def test_stls_are_binary_and_whole(path):
    data = path.read_bytes()
    assert len(data) == 84 + 50 * struct.unpack("<I", data[80:84])[0]


@pytest.mark.parametrize("path", PRINT, ids=[p.name for p in PRINT])
def test_every_print_file_has_a_step_or_preview(path):
    assert (ROOT / "cad" / "previews" / f"{path.stem}.png").exists()


def test_one_tree_fits_one_plate():
    """print/tree-plate.stl: one tree's show set (3 sockets, 2 stands, 4 pole caps) on one P1S plate."""
    data = (ROOT / "print" / "tree-plate.stl").read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    xs, ys = [], []
    for i in range(n):
        v = struct.unpack("<12f", data[84 + 50 * i: 84 + 50 * i + 48])
        xs += v[3::3]
        ys += v[4::3]
    w, d = max(xs) - min(xs), max(ys) - min(ys)
    assert w <= 255 and d <= 255
    # Bambu Studio centres it on the P1S's 256 bed: nothing in the front-left corner it keeps
    # clear for the filament cutter (bed_exclude_area 18 x 28)
    ox, oy = (256 - w) / 2 - min(xs), (256 - d) / 2 - min(ys)
    assert not any(x + ox < 18 and y + oy < 28 for x, y in zip(xs, ys))


def test_tree_plate_is_sliced_for_the_p1s():
    """print/tree-plate.gcode.3mf (python -m tools.slice): sliced, for the P1S, in PETG, on the textured plate."""
    import zipfile
    z = zipfile.ZipFile(ROOT / "print" / "tree-plate.gcode.3mf")
    head = z.read("Metadata/plate_1.gcode")[:400_000].decode("utf-8", "replace")
    tail = z.read("Metadata/plate_1.gcode")[-200_000:].decode("utf-8", "replace")
    text = head + tail
    assert "printer_model = Bambu Lab P1S" in text
    assert 'filament_settings_id = "Bambu PETG Basic @BBL X1C"' in text
    assert "curr_bed_type = Textured PEI Plate" in text
    assert "default_acceleration = 10000" in text    # the real Bambu process, not the CLI's defaults


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


def test_all_live_cad_is_freecad():
    """Only FreeCAD masters and files exported from them outside archive/ (Rob, 15 Nov 2026)."""
    foreign = {".prt", ".scad", ".f3d", ".sldprt", ".gcode", ".nc", ".3mf", ".dwg"}
    for path in ROOT.rglob("*"):
        if {"archive", ".venv", ".git"} & set(path.parts) or not path.is_file():
            continue
        if path.suffix.lower() == ".3mf" and path.parent == ROOT / "print":   # print files, not CAD
            continue
        assert path.suffix.lower() not in foreign, path


def test_complete_tree_file_exists():
    assert (ROOT / "cad" / "stair-tree-complete.FCStd").stat().st_size > 1000
    assert (ROOT / "cad" / "components" / "bought-parts.FCStd").exists()


def test_cad_checks_all_pass():
    text = (ROOT / "docs" / "cad-checks.md").read_text(encoding="utf-8")
    assert "**" not in text, "a check in docs/cad-checks.md failed"


def test_mount_sizes_hang_together():
    mp = json.loads((ROOT / "cad" / "parts" / "tree-mounts-params.json").read_text(encoding="utf-8"))
    assert 0 < mp["dt_root"] < mp["dt_tip"]                   # a dovetail: wider at the tip
    assert mp["dt_tip"] <= 56                                 # fits the flat at the tree's top
    assert mp["dt_tip"] + 2 * mp["clr"] + 2 * mp["slot_wall"] <= mp["col_w"]   # the tower's slot has walls
    assert mp["spig_w"] + 2 * mp["spig_clr"] + 2 * mp["stalk_wall"] < mp["col_w"]   # the pocket has walls
    assert mp["col_d"] <= 30                                  # Rob: the storage tower much slimmer
    assert mp["stake_d"] >= 9                                 # Rob: the peg hole at least 9mm
    assert mp["stake_d"] + 2 * 8 <= mp["pad_w"]               # 8mm of pad round each peg hole
    assert mp["peg_at"] - mp["stake_d"] / 2 >= mp["cap_end"] + 3   # the hole clears the end wall
    assert mp["lift"] >= 50                                   # Rob: at least 50mm of lift, ideally 100
    assert mp["pole_y"] - mp["pole_d"] / 2 >= mp["dt_h"] + mp["clr"] + mp["slot_wall"] + 3   # slot block to the pole hole
    assert 2 * (16 - mp["wall"]) < mp["tree_t"]               # front and back screws can't meet
    assert mp["front_x"] != mp["screw_x"]                     # and they're offset anyway
    assert -mp["tree_t"] / 2 + mp["rail_half"] < -(mp["tree_t"] + mp["below"]) + mp["pitch"]  # rail clears the tower above


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
    "tower and stand slide on the socket's rail", "dovetail captures the rail (the slot's lip overhangs the rail's flare)",
    "tent pole runs right through the stand, near its sole", "stand lifts the tree at least 50mm",
    "pole caps take the pole's ends and a peg each", "caps and stand stand on the same ground, clear of each other", "tower slot is stopped at the bottom, open at the top", "towers stack without clashing", "tower tab sits in the pocket of the tower above", "tower is slim under the rail's stop",
    "spigot sits in the recess above", "socket is one valid solid", "tower is one valid solid", "stand is one valid solid", "pole cap is one valid solid",
    "socket channel takes the tread", "hood is one valid solid", "hood clears the PSU",
    "hood M4 screws reach 3mm max into the S-400's case", "hood has a closed floor under the chamber's mains side",
    "hood is open under the chamber's 12V side, for the leads", "hood partition between mains and 12V", "hood inlet is in the roof over the mains side",
    "complete tree assembly opens with every link resolved",
    *[f"master {n} recomputes" for n in ("tree-box", "player-pods", "psu-cover", "tree-mounts", "pixel-disk", "step-clamp")],
]


@pytest.mark.parametrize("name", EXPECTED)
def test_freecad_geometry(fc, name):
    ok, detail = fc[name]
    assert ok, detail
