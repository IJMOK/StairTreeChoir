"""Skit scripts and their generated arrangements stay consistent with the cast."""

import json

import numpy as np
import pytest

from tools import skit
from tools.tree_layout import ROOT

VOICES = json.loads((ROOT / "data" / "voices.json").read_text(encoding="utf-8"))
CAST, GUESTS = VOICES["characters"], VOICES.get("guests", {})
SCRIPTS = sorted((ROOT / "data" / "skits").glob("*.json"))


def test_scripts_exist():
    assert SCRIPTS


def test_scripts_use_known_characters():
    for p in SCRIPTS:
        script = json.loads(p.read_text(encoding="utf-8"))
        assert script["name"] == p.stem
        assert script["lines"], p
        for line in script["lines"]:
            assert skit.speakers(line["who"], CAST, p.name, GUESTS), f"{p.name}: {line['who']}"
            assert line["say"].strip(), p.name


def test_timed_lines_are_in_order():
    for p in SCRIPTS:
        ats = [l["at"] for l in json.loads(p.read_text(encoding="utf-8"))["lines"] if "at" in l]
        assert ats == sorted(ats), p.name


def test_arrangements_match_scripts():
    for p in SCRIPTS:
        script = json.loads(p.read_text(encoding="utf-8"))
        arr_path = ROOT / "data" / "songs" / f"skit-{p.stem}.json"
        assert arr_path.exists(), f"missing {arr_path.name}"
        arr = json.loads(arr_path.read_text(encoding="utf-8"))
        n = len(script["lines"])
        assert list(arr["lines"]) == [str(i) for i in range(1, n + 1)], p.name
        assert [arr["lines"][str(i)] for i in range(1, n + 1)] == [skit.group_name(l["who"]) for l in script["lines"]]
        for line in script["lines"]:
            slots = sorted(CAST[c]["slot"] for c in skit.speakers(line["who"], CAST, p.name, GUESTS) if c in CAST)
            assert arr["groups"][skit.group_name(line["who"])] == slots, f"{p.name}: {line['who']}"
        guest_lines = sum(all(c in GUESTS for c in skit.speakers(l["who"], CAST, p.name, GUESTS)) for l in script["lines"])
        assert len(arr.get("gazes", [])) == guest_lines, p.name     # the trees look at every guest


def test_guests_look_somewhere():
    for name, g in GUESTS.items():
        assert g["look"] in ("up", "down") or g["look"] in CAST, name
        assert name not in CAST
    assert skit.speakers("Everyone", CAST, guests=GUESTS) == list(CAST)   # "Everyone" is the choir only


def test_everyone_is_the_whole_cast():
    assert skit.speakers("Everyone", CAST) == list(CAST)
    assert skit.speakers(["Holly", "Pip"], CAST) == ["Holly", "Pip"]
    assert skit.group_name(["Holly", "Pip"]) == "Holly+Pip"
    with pytest.raises(SystemExit):
        skit.speakers("Rudolph", CAST)


def test_at_starts_a_line_exactly(monkeypatch, tmp_path):
    monkeypatch.setattr(skit, "SKIT_DIR", tmp_path)
    monkeypatch.setattr(skit, "speak", lambda text, ch, cache, engine: np.ones(skit.RATE // 10, dtype=np.float32) * 0.5)
    script = {"name": "t", "lines": [{"who": "Holly", "say": "a"}, {"who": "Everyone", "say": "b", "at": 3.0}]}
    wav = skit.build(script, audio_only=True)
    import wave
    with wave.open(str(wav)) as w:
        y = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    first_loud_after_2s = np.flatnonzero(np.abs(y[2 * skit.RATE:]) > 1000)[0] + 2 * skit.RATE
    assert first_loud_after_2s == 3 * skit.RATE
