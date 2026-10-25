import json

import pytest

from tools import arrange_song as ars
from tools import fx
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


def outline(effects, tree):
    return sorted((e for e in effects if e.target == f"StairTree{tree}/Outline"), key=lambda e: e.start)


def test_outline_dims_only_while_others_sing():
    beats = [1.0, 2.0, 3.0, 4.0, 4.5]
    _, effects, _ = ars.plan_song(ARR, LINES, beats, 6000)
    by_start = {e.start: (e.colours[0], e.settings["Eff_On_Start"]) for e in outline(effects, 1)}
    assert by_start[0][1] == 100  # nobody sings yet
    assert by_start[1000] == ("#00FF00", 100)  # tree 1 sings, colours alternate per beat
    assert by_start[3000][1] == int(100 * ars.REST_SCALE)  # B sings line 2, tree 1 rests
    assert all(e.start < e.end for e in outline(effects, 1))


def test_ripple_lights_one_tree_per_beat():
    arr = {**ARR, "sections": [{"until": 999, "outline": "ripple", "colours": ["#0000FF"]}]}
    beats = [5.0 + 0.5 * k for k in range(12)]
    _, effects, _ = ars.plan_song(arr, LINES, beats, 11500)
    for k in range(1, 12):
        start = 5000 + 500 * (k - 1)
        bright = [t for t in range(1, 7)
                  if any(e.start == start and e.settings["Eff_On_Start"] == 100 for e in outline(effects, t))]
        assert len(bright) == 1


def test_eye_moves_switch_the_faces_eyes_off():
    arr = {**ARR, "sections": [{"until": 999, "look": "chase", "palette": "rainbow", "eyes": "follow"}]}
    faces, effects, sing = ars.plan_song(arr, LINES, [1.0, 2.0, 3.0, 4.0], 6000)
    eyes4 = [e for e in effects if e.target == "StairTree4/Eyes"]
    assert eyes4 and all(not ars.inside(e.start, sing[4]) for e in eyes4)   # watches only while resting
    assert eyes4[0].settings["Skips_StartPos"] == fx.EYE_POS["left"]       # A (trees 1-3) sings line 1
    for a, b, s in faces[4]:
        off = any(e.start <= a < e.end for e in eyes4)
        assert ("Faces_Eyes=(off)" in s) == off


def test_gaze_points_at_the_singers():
    sing = {t: [] for t in range(1, 7)}
    sing[6] = [(0, 1000)]
    assert ars.gaze_pieces(0, 1000, 2, sing) == [(0, 1000, "right")]
    assert ars.gaze_pieces(0, 1000, 6, sing) == []


def test_guest_gazes_override_follow():
    arr = {"gazes": [{"from": 1.0, "until": 2.0, "look": "up"}, {"from": 3.0, "until": 4.0, "look": 1}]}
    assert ars.guest_gazes(arr, 0, 5000, 3) == [(1000, 2000, "up"), (3000, 4000, "left")]
    assert ars.guest_gazes(arr, 0, 5000, 1)[1] == (3000, 4000, "down")     # the phone tree looks at its phone
    follow = [(500, 1500, "right"), (1500, 2500, "left")]
    assert ars.merge_gazes(follow, ars.guest_gazes(arr, 0, 2500, 3)) == [
        (500, 1000, "right"), (1000, 2000, "up"), (2000, 2500, "left")]


def test_glances_look_at_one_tree_then_the_pavement():
    # first glance: tree 3 looks up, the others turn towards it; the third: everyone looks down
    first = {t: ars.glance_pieces(0, 25000, t)[0] for t in range(1, 7)}
    assert {t: d for t, (_, _, d) in first.items()} == {1: "right", 2: "right", 3: "up", 4: "left", 5: "left", 6: "left"}
    assert all(ars.glance_pieces(0, 25000, t)[2][2] == "down" for t in range(1, 7))
    # pieces stay inside the window and don't overlap; the turn carries on from k0
    g = ars.glance_pieces(0, 25000, 6)
    assert g[-1][1] <= 25000 and all(x[1] <= y[0] for x, y in zip(g, g[1:]))
    assert ars.glance_pieces(0, 25000, 6, 1)[0] == (2000, 4500, "up")


@pytest.mark.parametrize("song", ["rockin-around", "dominick", "feliz-navidad", "drummer-boy", "goodnight", "we-wish-you", "o-come-all-ye-faithful", "virgin-mary", "twelve-days"])
def test_real_arrangement_is_consistent(song):
    arr = json.loads((ROOT / f"data/songs/{song}.json").read_text(encoding="utf-8"))
    assert sorted(int(k) for k in arr["lines"]) == list(range(1, len(arr["lines"]) + 1))
    assert all(g in arr["groups"] for g in arr["lines"].values())
    assert all(set(m) <= set(range(1, 7)) for m in arr["groups"].values())
    untils = [s["until"] for s in arr["sections"]]
    assert untils == sorted(untils)
    # every look, palette, accent and eye move builds valid settings
    beats = [10000 + 500 * k for k in range(8)]
    for sec in arr["sections"]:
        look = sec.get("look") or sec["outline"]
        spec = sec.get("palette", sec.get("colours", "xmas"))
        if look.startswith("choir_"):
            out = fx.look_choir(look, 10000, 14000, beats, fx.colours_for(spec), sec.get("params", {}))
        elif look in ("pulse", "ripple", "hold"):
            out = ars.beat_pulses(look, 10000, 14000, beats, 1, fx.colours_for(spec), [], [], 0)
        else:
            out = fx.look_per_tree(look, "StairTree1/Outline", 10000, 14000, beats, 1, fx.colours_for(spec, 1), 35,
                                   sec.get("params", {}))
        if sec.get("accent"):
            out += fx.accents(sec["accent"], "Outlines", 10000, 14000, beats, fx.colours_for(spec))
        if sec.get("eyes", "blink") not in ("blink", "follow", "glance"):
            out += fx.eyes(sec["eyes"], 1, 10000, 14000, beats, fx.colours_for(spec))
        assert out
        for e in out:
            e.settings_string()
            assert e.start < e.end


def test_no_lines_is_an_animation_loop():
    arr = {"lyrics_track": "Loop", "groups": {}, "lines": {},
           "sections": [{"until": 3.0, "look": "choir_butterfly"},
                        {"until": 999, "look": "twinkle", "palette": "rainbow", "eyes": "roll"}]}
    faces, effects, sing = ars.plan_song(arr, [], [0.5 * k for k in range(12)], 6000)
    assert all(w == [] for w in sing.values())
    for t in range(1, 7):
        assert all("Phoneme=rest" in s for _, _, s in faces[t])
        assert faces[t][0][0] == 0 and faces[t][-1][1] == 6000
    assert any(e.target == "Outlines" for e in effects) and any(e.target == "StairTree1/Eyes" for e in effects)


def test_end_at_leaves_the_last_frames_black():
    arr = {**ARR, "end_at": 4.2, "end_fade": 0.5,
           "sections": [{"until": 999, "look": "chase", "palette": "rainbow", "eyes": "roll"}]}
    faces, effects, _ = ars.plan_song(arr, LINES, [1.0, 2.0, 3.0, 4.0, 5.0], 6000)
    assert max(b for t in faces for _, b, _ in faces[t]) == 4200
    assert max(e.end for e in effects) == 4200 and all(e.start < e.end for e in effects)
    assert all("T_TEXTCTRL_Fadeout=" in s for t in faces for _, b, s in faces[t] if b == 4200)
    ending = [e for e in effects if e.end == 4200]
    assert ending and all(e.settings.get("fadeout") for e in ending)
    for e in ending:
        assert "T_TEXTCTRL_Fadeout=" in e.settings_string()


def test_moves_override_mouth_eyes_and_outline():
    arr = {"lyrics_track": "Loop", "groups": {}, "lines": {},
           "sections": [{"until": 999, "look": "chase", "palette": "rainbow", "eyes": "roll"}],
           "moves": [{"tree": 2, "from": 1.0, "until": 3.0, "mouth": "O", "eyes": "closed",
                      "outline": {"look": "glow", "palette": ["#FF0000"]}},
                     {"tree": [2, 3], "from": 2.0, "until": 2.5, "eyes": 1},
                     {"tree": 4, "from": 1.0, "until": 4.0, "mouth": "yawn"}]}
    faces, effects, _ = ars.plan_song(arr, [], [0.5 * k for k in range(12)], 6000)

    def at(t, ms):
        return next(s for a, b, s in faces[t] if a <= ms < b)
    assert "Phoneme=O" in at(2, 1500) and "Faces_Eyes=Closed" in at(2, 1500)
    assert "Faces_Eyes=(off)" in at(2, 2200)                 # the later move (look at Holly) wins
    assert all("Phoneme=rest" in s for a, b, s in faces[2] if b <= 1000 or a >= 3000)
    out2 = outline(effects, 2)
    assert [e for e in out2 if e.start == 1000 and e.end == 3000 and e.colours == ["#FF0000"]]
    assert not [e for e in out2 if e.start < 3000 and e.end > 1000 and e.colours != ["#FF0000"]]   # carved out
    eyes3 = [e for e in effects if e.target == "StairTree3/Eyes" and e.start == 2000]
    assert eyes3 and eyes3[0].settings["Skips_StartPos"] == fx.EYE_POS["left"]
    yawn = [s.split("Phoneme=")[1].split(",")[0] for a, b, s in faces[4] if 1000 <= a < 4000]
    assert yawn == ["MBP", "O", "AI", "O", "MBP"]


def test_mouth_patterns_cover_the_move():
    for name in ars.MOUTH_PATTERNS:
        p = ars.mouth_pieces(name, 1000, 7000)
        assert p[0][0] == 1000 and p[-1][1] == 7000 and all(a[1] == b[0] for a, b in zip(p, p[1:]))
        assert {x for _, _, x in p} <= set(ars.PHONEMES)
    with pytest.raises(KeyError):
        ars.mouth_pieces("sneeze", 0, 1000)


def test_brightness_and_tree_end():
    arr = {"lyrics_track": "Loop", "groups": {}, "lines": {}, "brightness": 40, "end_fade": 1.0,
           "tree_end": {"3": 2.0},
           "sections": [{"until": 999, "look": "glow", "palette": "rainbow", "eyes": "heavy"}],
           "asleep": [{"tree": 5, "from": None, "until": None}]}
    faces, effects, _ = ars.plan_song(arr, [], [], 6000)
    assert all("C_SLIDER_Brightness=40" in s for t in faces for _, _, s in faces[t])
    glow1 = outline(effects, 1)
    assert glow1 and all(e.settings["brightness"] == 40 for e in glow1)
    assert all("brightness" not in e.settings for e in outline(effects, 5))     # a sleeper's breath isn't dimmed
    assert max(b for _, b, _ in faces[3]) == 2000
    assert max(e.end for e in effects if e.target.startswith("StairTree3")) == 2000
    assert all(e.settings.get("fadeout") for e in effects if e.target.startswith("StairTree3") and e.end == 2000)
    assert max(b for _, b, _ in faces[1]) == 6000
