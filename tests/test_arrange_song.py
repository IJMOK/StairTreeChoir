import json

import pytest

from tools import arrange_song as ars
from tools.tree_layout import ROOT

ARR = {
    "lyrics_track": "Choir_1",
    "groups": {"A": [1, 2, 3], "B": [4, 5, 6], "all": [1, 2, 3, 4, 5, 6]},
    "lines": {"1": "A", "2": "B", "3": "all"},
    "sections": [{"until": 5.0, "outline": "pulse", "colours": ["#FF0000", "#00FF00"]},
                 {"until": 999, "outline": "ripple", "colours": ["#0000FF"]}],
}
LINES = [(1.0, 2.0), (2.5, 3.5), (4.0, 4.5)]


def test_windows_follow_the_arrangement():
    assert ars.singing_windows(ARR, LINES, 1) == [(900, 2150), (3900, 4650)]
    assert ars.singing_windows(ARR, LINES, 4) == [(2400, 4650)]  # lines 2 and 3 merge (gap < 400ms)


def test_back_to_back_lines_dont_bleed():
    arr = {**ARR, "lines": {"1": "A", "2": "B", "3": "A"}}
    lines = [(1.0, 2.0), (2.0, 2.6), (2.6, 3.5)]  # no gaps, like Dominick's chorus
    a = ars.singing_windows(arr, lines, 1)
    b = ars.singing_windows(arr, lines, 4)
    assert a == [(900, 2000), (2600, 3650)]  # not merged across B's line
    assert b == [(2000, 2600)]


def test_faces_cover_the_song_back_to_back():
    plan = ars.faces_plan(ARR, LINES, 1, 6000)
    assert plan[0][0] == 0 and plan[-1][1] == 6000
    assert all(a[1] == b[0] for a, b in zip(plan, plan[1:]))
    assert all(a < b and a % ars.FRAME_MS == 0 and b % ars.FRAME_MS == 0 for a, b, _ in plan)
    assert ["Choir_1" in s for _, _, s in plan] == [False, True, False, True, False]
    assert all("Faces_Outline=0" in s for _, _, s in plan)


def test_outline_dims_only_while_others_sing():
    beats = [1.0, 2.0, 3.0, 4.0, 4.5]
    anyone = [w for t in range(1, 7) for w in ars.singing_windows(ARR, LINES, t)]
    p1 = ars.outline_plan(ARR, beats, 1, 6000, ars.singing_windows(ARR, LINES, 1), anyone)
    by_start = {a: (colour, hi) for a, _, colour, hi, _ in p1}
    assert by_start[0][1] == 100  # nobody sings yet
    assert by_start[1000] == ("#00FF00", 100)  # tree 1 sings, colours alternate per beat
    assert by_start[3000][1] == int(100 * ars.REST_SCALE)  # B sings line 2, tree 1 rests
    assert all(a < b for a, b, *_ in p1)


def test_ripple_lights_one_tree_per_beat():
    beats = [5.0 + 0.5 * k for k in range(12)]
    plans = [ars.outline_plan(ARR, beats, t, 11500, [], []) for t in range(1, 7)]
    for k in range(1, 12):  # beat k starts at edges[k]
        bright = [t for t, plan in enumerate(plans, 1)
                  if any(a == 5000 + 500 * (k - 1) and hi == 100 for a, _, _, hi, _ in plan)]
        assert len(bright) == 1


def test_real_arrangement_is_consistent():
    arr = json.loads((ROOT / "data/songs/rockin-around.json").read_text(encoding="utf-8"))
    assert sorted(int(k) for k in arr["lines"]) == list(range(1, len(arr["lines"]) + 1))
    assert all(g in arr["groups"] for g in arr["lines"].values())
    assert all(set(m) <= set(range(1, 7)) for m in arr["groups"].values())
    untils = [s["until"] for s in arr["sections"]]
    assert untils == sorted(untils)
    assert {s["outline"] for s in arr["sections"]} <= {"pulse", "ripple", "hold"}
