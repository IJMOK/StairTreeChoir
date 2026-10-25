"""tools/loops.py: the silent loops' scenes, their asleep variants and the files they write."""

import json

import pytest

from tools import arrange_song as ars
from tools import loops
from tools.tree_layout import ROOT

BEATS = [0.6 * k for k in range(1, 500)]


def trees_of(m):
    return m["tree"] if isinstance(m["tree"], list) else [m["tree"]]


@pytest.mark.parametrize("stem", sorted(loops.pieces()))
def test_every_piece_plans_and_fits(stem):
    arr = loops.pieces()[stem]
    ms = int(arr["seconds"] * 1000)
    assert arr["audio"] is None and not arr["lines"]
    untils = [s["until"] for s in arr["sections"]]
    assert untils == sorted(untils)
    for m in arr["moves"]:
        assert set(trees_of(m)) <= set(loops.ALL) and 0 <= m["from"] < m["until"] <= arr["seconds"], (stem, m)
    faces, effects, _ = ars.plan_song(arr, [], BEATS, ms)
    for e in effects:
        e.settings_string()
        assert 0 <= e.start < e.end <= ms
    for t in loops.ALL:
        plan = faces[t]
        assert all(a[1] == b[0] for a, b in zip(plan, plan[1:]))
        if "tree_end" not in arr:
            assert plan[0][0] == 0 and plan[-1][1] == ms


def test_lengths_suit_a_graceful_stop():
    """A graceful stop waits for the piece that's playing: none is longer than a minute."""
    for arr in loops.pieces().values():
        assert arr["seconds"] <= 60
    assert len(loops.waiting_scenes()) * loops.WAITING_S == 600      # ten minutes before the Waiting loop repeats


def test_every_character_plays_in_the_waiting_loop_and_scenes_differ():
    scenes = loops.waiting_scenes()
    looks = [tuple(s["look"] for s in sc.sections) for sc in scenes]
    assert len(set(looks)) >= 8                                       # (nearly) a different background every scene
    for sc in scenes:
        acting = {t for m in sc.moves for t in trees_of(m)}
        assert len(acting) >= 4, sc.title
    acted = {t for sc in scenes for m in sc.moves for t in trees_of(m) if "mouth" in m or "outline" in m}
    assert acted == set(loops.ALL)


def test_waiting_asleep_is_waiting_with_bramble_asleep():
    p = loops.pieces()
    for k in range(1, len(loops.waiting_scenes()) + 1):
        w, a = p[f"waiting-{k:02d}"], p[f"waiting-asleep-{k:02d}"]
        assert a["sequence"] == f"Waiting Asleep {k}" and a["asleep"] == [{"tree": 5, "from": None, "until": None}]
        assert a["sections"] == w["sections"]
        assert not [m for m in a["moves"] if loops.BRAMBLE in trees_of(m)]
        assert [m for m in w["moves"] if m["tree"] != loops.BRAMBLE and not isinstance(m["tree"], list)] == \
               [m for m in a["moves"] if not isinstance(m["tree"], list)]


def test_night_and_lights_out_are_dim_and_end_dark():
    p = loops.pieces()
    for stem, arr in p.items():
        if (stem.startswith("night-") and "christmas" not in stem) or stem == "lights-out":
            assert arr["brightness"] == loops.NIGHT_BRIGHTNESS <= 50
        if stem.startswith("night-christmas-eve"):
            assert len(arr["asleep"]) == 6 and arr["moves"]          # all asleep, with a little stirring
    for stem in ("lights-out", "lights-out-asleep", "morning-lights-off"):
        arr = p[stem]
        assert sorted(int(t) for t in arr["tree_end"]) == loops.ALL
        assert max(arr["tree_end"].values()) < arr["seconds"]          # the last frames are black
        faces, effects, _ = ars.plan_song(arr, [], BEATS, int(arr["seconds"] * 1000))
        end = int(max(arr["tree_end"].values()) * 1000)
        assert max(e.end for e in effects) <= end and max(b for t in faces for _, b, _ in faces[t]) <= end
    assert loops.LIGHTS_OUT_ORDER[loops.HOLLY] == max(loops.LIGHTS_OUT_ORDER.values())   # Holly goes last


def test_files_are_current():
    for stem, arr in loops.pieces().items():
        on_disk = json.loads((ROOT / "data" / "loops" / f"{stem}.json").read_text(encoding="utf-8"))
        assert on_disk == json.loads(json.dumps(arr)), f"run python -m tools.loops ({stem})"
    assert {p.stem for p in (ROOT / "data" / "loops").glob("*.json")} == set(loops.pieces())
