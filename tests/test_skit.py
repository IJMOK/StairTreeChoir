"""Skit scripts and their generated arrangements stay consistent with the cast."""

import json

from tools.tree_layout import ROOT

CAST = json.loads((ROOT / "data" / "voices.json").read_text(encoding="utf-8"))["characters"]
SCRIPTS = sorted((ROOT / "data" / "skits").glob("*.json"))


def test_scripts_exist():
    assert SCRIPTS


def test_scripts_use_known_characters():
    for p in SCRIPTS:
        script = json.loads(p.read_text(encoding="utf-8"))
        assert script["name"] == p.stem
        assert script["lines"], p
        for line in script["lines"]:
            assert line["who"] in CAST, f"{p.name}: {line['who']}"
            assert line["say"].strip(), p.name


def test_arrangements_match_scripts():
    for p in SCRIPTS:
        script = json.loads(p.read_text(encoding="utf-8"))
        arr_path = ROOT / "data" / "songs" / f"skit-{p.stem}.json"
        assert arr_path.exists(), f"missing {arr_path.name}"
        arr = json.loads(arr_path.read_text(encoding="utf-8"))
        n = len(script["lines"])
        assert list(arr["lines"]) == [str(i) for i in range(1, n + 1)], p.name
        assert [arr["lines"][str(i)] for i in range(1, n + 1)] == [l["who"] for l in script["lines"]]
        whos = {l["who"] for l in script["lines"]}
        assert set(arr["groups"]) == whos, p.name
        for who, slots in arr["groups"].items():
            assert slots == [CAST[who]["slot"]], f"{p.name}: {who}"
