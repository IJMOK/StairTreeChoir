"""Apply a song arrangement (data/songs/<song>.json) to the open xLights sequence.

    python -m tools.arrange_song data/songs/rockin-around.json [--dry-run]

Who sings which lyric line, and how each section looks, are data; this turns them into
effects through xLights' automation API (Preferences → Output → API Port A,
127.0.0.1:49913). The sequence must be open in xLights and list the Outlines group
(python -m tools.xsq "<sequence>" adds it, with the sequence closed).

Every run replaces all effects on StairTreeN, StairTreeN/Outline, StairTreeN/Eyes and
the Outlines group:
- StairTreeN: Faces effects back to back. While the tree sings a line the mouth follows
  the lyric timing track; otherwise a fixed "rest" mouth. Eyes blink, except where an eye
  move runs (then the Faces eyes are off). The Faces outline is off.
- Outline lighting per section (tools/fx.py): a per-tree look on StairTreeN/Outline,
  bright on the trees singing and dimmed on the rest, or a whole-choir look on the
  Outlines group; optional beat accents on the layer above.
- Eye moves per section on StairTreeN/Eyes: "follow" (trees not singing look at the
  ones that are), "glance" (no singing needed: every 7 s one tree looks up and the rest
  look at it, every third time all look down at the pavement), "roll", "rainbow",
  "sparkle"; "blink" (default) leaves them to Faces.

Section keys: name, until (s), look, palette (name or list; "colours" also accepted),
params, accent ("flash", "sparkle_hit", "colour_hit"), accent_every, eyes.

Optional arrangement keys: "gazes": [{"from", "until", "look"}] (s; look "up", "down" or a tree
slot) turns every tree's eyes that way, over "follow" (a guest voice speaking, tools/skit.py).
"asleep": [{"tree", "from", "until"}] (s; null = start/end) puts a
tree to sleep: eyes shut, mouth at rest, no eye moves, outline a slow dim blue breath, and it
sits out shared lines (a line that is only its own, a snore, still moves its mouth).
"end_at" (s) clips every effect, Faces included, to end there,
so the frames after it are black (FPP holds the last frame when a playlist ends);
"end_fade" (s) fades the effects that end at end_at out over that time.
"tree_end": {"<slot>": s} ends one tree early the same way (lights out one tree at a time).
"brightness" (%) scales every effect and the Faces (eyes, mouth) but not a sleeper's breath
(the late-night loops are dimmed this way).
"moves": [{"tree" (slot or list), "from", "until", and any of "mouth", "eyes", "outline"}] (s):
one character acting on its own over everything above (sections, glances, asleep), for the
silent loops (tools/loops.py). mouth: a phoneme (rest, MBP, etc, E, FV, L, AI, O, U, WQ) or a
pattern (MOUTH_PATTERNS: yawn, hum, giggle, chatter, whisper, snore, shush). eyes: "closed",
"open" (staring, no blink), a direction (up, down, left, right), a slot number (look at that
tree; its own number: up), or an fx eye mode (heavy, wink, roll, rainbow, sparkle; "eyes_bright" %
dims it). outline: a
per-tree look name or {"look", "palette", "params", "bright"} (fx.look_per_tree).
An arrangement may have no lines at all (groups {}, lines {}: an animation loop).
Faces/On settings keys are from the xLights source (data/xlights-effects.json).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from tools import fx
from tools.tree_layout import ROOT

SHOW_FOLDER = Path(r"C:\Users\User\Documents\xLights")
API = "http://127.0.0.1:49913/xlDoAutomation"
FRAME_MS = 50
TREES = range(1, 7)
LEAD_MS, TAIL_MS = 100, 150  # open the singing window a little around each line
MERGE_GAP_MS = 400  # rest gaps shorter than this stay singing (no mouth snapping shut)
PULSE_START, PULSE_END = 100, 25  # On effect brightness % across one beat
REST_SCALE = 0.35  # outline brightness for trees not singing while others do
SLEEP_BREATH_MS = 4000  # one slow breath on a sleeping tree's outline
SLEEP_BRIGHT = (6, 30)  # On brightness % at the bottom and top of a breath
SLEEP_COLOUR = "#3050C0"

FACES_COMMON = ("E_CHOICE_Faces_FaceDefinition=StairTree,E_CHOICE_Faces_EyeBlinkFrequency=Normal,"
                "E_CHECKBOX_Faces_Outline=0")


def snap(ms: float) -> int:
    return int(round(ms / FRAME_MS)) * FRAME_MS


def asleep_spans(arr: dict, song_ms: int = 10 ** 9) -> dict[int, list[tuple[int, int]]]:
    """[start, end) ms per tree from "asleep": [{"tree", "from", "until"}] (seconds; a missing
    or null end means the start or end of the sequence)."""
    out: dict[int, list[tuple[int, int]]] = {t: [] for t in TREES}
    for s in arr.get("asleep", []):
        a = snap(s["from"] * 1000) if s.get("from") is not None else 0
        b = snap(s["until"] * 1000) if s.get("until") is not None else song_ms
        out[s["tree"]].append((a, min(b, song_ms)))
    return out


def sings_line(arr: dict, tree: int, members: list[int], start_s: float) -> bool:
    """A sleeping tree sits out the lines it shares; a line that is only its own (a snore,
    talking in its sleep) still moves its mouth."""
    return tree in members and (len(members) == 1 or not inside(snap(start_s * 1000), asleep_spans(arr)[tree]))


def singing_windows(arr: dict, line_times: list[tuple[float, float]], tree: int) -> list[tuple[int, int]]:
    """Merged [start, end) ms windows in which this tree sings.

    Each line's window opens LEAD_MS early and closes TAIL_MS late, but never past the
    midpoint to the neighbouring line, so a tree doesn't mouth the next singer's first
    syllable. Windows merge only across silence (consecutive lines both sung by this
    tree), never across a line someone else sings."""
    n = len(line_times)
    windows = []
    for number, group in sorted(arr["lines"].items(), key=lambda kv: int(kv[0])):
        i = int(number) - 1
        start, end = line_times[i]
        if not sings_line(arr, tree, arr["groups"][group], start):
            continue
        lo, hi = start * 1000 - LEAD_MS, end * 1000 + TAIL_MS
        if i > 0:
            lo = max(lo, (line_times[i - 1][1] + start) * 500)
        if i < n - 1:
            hi = min(hi, (end + line_times[i + 1][0]) * 500)
        windows.append([snap(lo), snap(hi), i])
    merged = []
    for w in windows:
        if merged and w[2] == merged[-1][2] + 1 and w[0] - merged[-1][1] < MERGE_GAP_MS:
            merged[-1][1], merged[-1][2] = max(merged[-1][1], w[1]), w[2]
        else:
            merged.append(w)
    return [(max(0, a), b) for a, b, _ in merged]


def inside(t: int, windows) -> bool:
    return any(a <= t < b for a, b in windows)


def cut(a: int, b: int, edges) -> list[tuple[int, int]]:
    """[a, b) split at every edge inside it."""
    pts = sorted({a, b, *(e for e in edges if a < e < b)})
    return list(zip(pts, pts[1:]))


def faces_plan(arr: dict, line_times, tree: int, song_ms: int,
               eyes_off=(), asleep=(), mouths=(), eye_states=()) -> list[tuple[int, int, str]]:
    """Back-to-back Faces effects covering the whole song: (start, end, settings).
    Eyes blink (Auto), are off where an eye move runs, and are shut while asleep; a move's
    (start, end, phoneme) mouths and (start, end, Faces_Eyes value) eye states win over all that."""
    sing = f"E_CHOICE_Faces_TimingTrack={arr['lyrics_track']},{FACES_COMMON}"
    rest = f"E_CHOICE_Faces_Phoneme=rest,{FACES_COMMON}"
    pieces, t = [], 0
    for a, b in singing_windows(arr, line_times, tree):
        if a > t:
            pieces.append((t, a, rest))
        pieces.append((a, b, sing))
        t = b
    if t < song_ms:
        pieces.append((t, song_ms, rest))
    edges = [e for w in (*eyes_off, *asleep) for e in w] + [e for w in (*mouths, *eye_states) for e in w[:2]]
    bright = f",C_SLIDER_Brightness={arr['brightness']}" if arr.get("brightness", 100) != 100 else ""
    plan = []
    for a, b, s in pieces:
        for x, y in cut(a, b, edges):
            m = [p for p0, p1, p in mouths if p0 <= x < p1]
            s2 = f"E_CHOICE_Faces_Phoneme={m[-1]},{FACES_COMMON}" if m else s
            st = [v for p0, p1, v in eye_states if p0 <= x < p1]
            eyes = st[-1] if st else "Closed" if inside(x, asleep) else "(off)" if inside(x, eyes_off) else "Auto"
            plan.append((x, y, f"{s2},E_CHOICE_Faces_Eyes={eyes}{bright}"))
    return plan


def sections(arr: dict, song_ms: int) -> list[tuple[int, int, dict]]:
    out, a = [], 0
    for s in arr["sections"]:
        b = min(song_ms, snap(s["until"] * 1000))
        if b > a:
            out.append((a, b, s))
        a = b
    return out


def beat_pulses(style: str, a: int, b: int, beats_ms: list[int], tree: int, cols: list[str],
                windows, anyone, k0: int) -> list[fx.Fx]:
    """The original beat-synced On looks: pulse, ripple, hold."""
    target = f"StairTree{tree}/Outline"
    if style == "hold":
        return [fx.Fx(target, "On", a, b, {"Eff_On_Start": 100, "Eff_On_End": 100}, [cols[0]])]
    edges = [a] + [x for x in beats_ms if a < x < b] + [b]
    out = []
    for k in range(len(edges) - 1):
        x, y = edges[k], edges[k + 1]
        if y - x < FRAME_MS:
            continue
        colour = cols[(k0 + k) % len(cols)]
        if style == "ripple":
            hi = PULSE_START if (k0 + k) % len(TREES) == tree - 1 else int(PULSE_START * REST_SCALE)
            lo = int(hi * PULSE_END / 100)
        else:
            scale = REST_SCALE if inside(x, anyone) and not inside(x, windows) else 1.0
            hi, lo = int(PULSE_START * scale), int(PULSE_END * scale)
        out.append(fx.Fx(target, "On", x, y, {"Eff_On_Start": hi, "Eff_On_End": lo}, [colour]))
    return out


def gaze_pieces(a: int, b: int, tree: int, sing: dict) -> list[tuple[int, int, str]]:
    """While others sing and this tree doesn't, look towards them (slot 1 is on the left)."""
    edges = [e for t in TREES for w in sing[t] for e in w]
    out = []
    for x, y in cut(a, b, edges):
        singers = [t for t in TREES if inside(x, sing[t])]
        if not singers or tree in singers:
            continue
        d = "right" if sum(singers) / len(singers) > tree else "left"
        if out and out[-1][2] == d and out[-1][1] == x:
            out[-1] = (out[-1][0], y, d)
        else:
            out.append((x, y, d))
    return out


GLANCE_EVERY_MS, GLANCE_MS = 7000, 2500
GLANCE_FOCUS = [3, 6, 1, 4, 2, 5]       # who "heard something", in turn


def glance_pieces(a: int, b: int, tree: int, k0: int = 0) -> list[tuple[int, int, str]]:
    """Without singing: every 7 s one tree looks up and the others turn to look at it;
    every third glance the whole choir looks down at the people on the pavement."""
    out = []
    for k, x in enumerate(range(a + 2000, b - GLANCE_MS, GLANCE_EVERY_MS)):
        n = k0 + k
        if n % 3 == 2:
            d = "down"
        else:
            f = GLANCE_FOCUS[(n - n // 3) % len(GLANCE_FOCUS)]
            d = "up" if f == tree else "right" if f > tree else "left"
        out.append((x, x + GLANCE_MS, d))
    return out


def guest_gazes(arr: dict, a: int, b: int, tree: int) -> list[tuple[int, int, str]]:
    """Arrangement "gazes" (tools/skit.py guests) inside a..b: look "up", "down", or at a tree
    by slot (that tree itself looks down, at the phone)."""
    out = []
    for g in arr.get("gazes", []):
        x, y = max(a, snap(g["from"] * 1000)), min(b, snap(g["until"] * 1000))
        look = g["look"]
        if isinstance(look, int):
            look = "down" if look == tree else "right" if look > tree else "left"
        if y > x:
            out.append((x, y, look))
    return out


def merge_gazes(follow: list[tuple[int, int, str]], forced: list[tuple[int, int, str]]):
    """follow pieces with the forced ones laid over them."""
    out = []
    for x, y, d in follow:
        for p, q in cut(x, y, [e for f in forced for e in f[:2]]):
            if not any(f0 <= p < f1 for f0, f1, _ in forced):
                out.append((p, q, d))
    return sorted(out + forced)


def carve(effects: list[fx.Fx], targets: set[str], spans) -> list[fx.Fx]:
    """Cut the spans out of every effect on these targets (all layers)."""
    out = []
    for e in effects:
        if e.target not in targets:
            out.append(e)
            continue
        pieces = [(e.start, e.end)]
        for a, b in spans:
            pieces = [q for x, y in pieces for q in ((x, min(y, a)), (max(x, b), y)) if q[1] - q[0] >= FRAME_MS]
        out += [dataclasses.replace(e, start=x, end=y) for x, y in pieces]
    return out


def breathing(tree: int, a: int, b: int) -> list[fx.Fx]:
    """A sleeping tree's outline: dim blue, slowly swelling and fading like breath."""
    target, out, up = f"StairTree{tree}/Outline", [], True
    lo, hi = SLEEP_BRIGHT
    for x in range(a, b, SLEEP_BREATH_MS // 2):
        y = min(b, x + SLEEP_BREATH_MS // 2)
        out.append(fx.Fx(target, "On", x, y, {"Eff_On_Start": lo if up else hi, "Eff_On_End": hi if up else lo},
                         [SLEEP_COLOUR]))
        up = not up
    return out


def plan_song(arr: dict, line_times, beats_s: list[float], song_ms: int):
    """Everything to add: (Faces plan per tree, list of Fx, singing windows per tree)."""
    if arr.get("end_at") is not None:
        song_ms = min(song_ms, snap(arr["end_at"] * 1000))
    beats_ms = [snap(b * 1000) for b in beats_s]
    sing = {t: singing_windows(arr, line_times, t) for t in TREES}
    anyone = [w for t in TREES for w in sing[t]]
    sing_edges = [e for w in anyone for e in w]
    effects: list[fx.Fx] = []
    eyes_off = {t: [] for t in TREES}
    k0 = glances = 0
    for a, b, sec in sections(arr, song_ms):
        look = sec.get("look") or sec.get("outline", "pulse")
        spec = sec.get("palette", sec.get("colours", "xmas"))
        params = sec.get("params", {})
        in_beats = [x for x in beats_ms if a <= x < b]
        accent, every = sec.get("accent"), sec.get("accent_every", 1)
        layer = 1 if accent else 0
        if look.startswith("choir_"):
            new = fx.look_choir(look, a, b, in_beats, fx.colours_for(spec), params)
            for e in new:
                e.layer += layer
            effects += new
            if accent:
                effects += fx.accents(accent, "Outlines", a, b, in_beats, fx.colours_for(spec), every)
        else:
            for t in TREES:
                target = f"StairTree{t}/Outline"
                cols = fx.colours_for(spec, t if spec == "rainbow" else None)
                if look in ("pulse", "ripple", "hold"):
                    new = beat_pulses(look, a, b, beats_ms, t, cols, sing[t], anyone, k0)
                else:
                    new = []
                    for x, y in cut(a, b, sing_edges):
                        dim = inside(x, anyone) and not inside(x, sing[t])
                        new += fx.look_per_tree(look, target, x, y, [z for z in in_beats if x <= z < y], t, cols,
                                                int(100 * REST_SCALE) if dim else 100, params)
                for e in new:
                    e.layer += layer
                effects += new
                if accent:
                    effects += fx.accents(accent, target, a, b, in_beats, cols, every)
        k0 += len(in_beats)
        mode = sec.get("eyes", "blink")
        if mode == "blink":
            continue
        for t in TREES:
            if mode in ("follow", "glance"):
                gz = (merge_gazes(gaze_pieces(a, b, t, sing), guest_gazes(arr, a, b, t)) if mode == "follow"
                      else glance_pieces(a, b, t, glances))
                effects += fx.eyes("follow", t, a, b, in_beats, [], gz)
                eyes_off[t] += [(g0, g1) for g0, g1, _ in gz if g1 - g0 >= 100]
            else:
                effects += fx.eyes(mode, t, a, b, in_beats, fx.colours_for(spec, t))
                eyes_off[t].append((a, b))
        if mode == "glance":       # the turn of who looks up carries on into the next glance section
            glances += len(glance_pieces(a, b, 1))
    scale_brightness(effects, arr.get("brightness", 100))
    asleep = asleep_spans(arr, song_ms)
    for t in TREES:
        if asleep[t]:
            effects = carve(effects, {f"StairTree{t}/Outline", f"StairTree{t}/Eyes"}, asleep[t])
            effects += [e for a, b in asleep[t] for e in breathing(t, a, b)]
    effects, mouths, eye_states = apply_moves(arr, effects, beats_ms, song_ms)
    faces = {t: faces_plan(arr, line_times, t, song_ms, eyes_off[t], asleep[t], mouths[t], eye_states[t])
             for t in TREES}
    ends = {int(k): snap(v * 1000) for k, v in arr.get("tree_end", {}).items()}
    if arr.get("end_at") is not None or ends:
        faces, effects = clip_to_end(faces, effects, song_ms, arr.get("end_fade", 0), ends)
    return faces, effects, sing


PHONEMES = ("rest", "MBP", "etc", "E", "FV", "L", "AI", "O", "U", "WQ")
# Silent mouth patterns for the loops: (phonemes, seconds each), repeated over the move.
MOUTH_PATTERNS = {
    "hum": (("MBP", "U", "MBP", "O"), (0.7, 0.6, 0.7, 0.6)),       # lips barely moving
    "giggle": (("E", "rest", "AI", "rest"), (0.15, 0.1, 0.15, 0.15)),
    "chatter": (("etc", "O", "E", "MBP", "AI", "L", "rest", "U"), (0.2,) * 8),   # talking nineteen to the dozen
    "whisper": (("etc", "rest", "O", "rest", "E", "rest"), (0.25,) * 6),
    "snore": (("rest", "U", "O", "U"), (1.6, 0.5, 0.9, 0.5)),
    "shush": (("U",), (1.0,)),
}
YAWN = (("MBP", 0.1), ("O", 0.2), ("AI", 0.45), ("O", 0.15), ("MBP", 0.1))   # share of the move


def mouth_pieces(spec: str, a: int, b: int) -> list[tuple[int, int, str]]:
    """(start, end, phoneme) pieces for a move's mouth over [a, b)."""
    if spec in PHONEMES:
        return [(a, b, spec)]
    out, x = [], a
    if spec == "yawn":
        for k, (ph, share) in enumerate(YAWN):
            y = b if k == len(YAWN) - 1 else min(b, snap(x + (b - a) * share))
            if y > x:
                out.append((x, y, ph))
            x = y
        return out
    if spec not in MOUTH_PATTERNS:
        raise KeyError(f"unknown mouth {spec!r}")
    shapes, secs = MOUTH_PATTERNS[spec]
    k = 0
    while x < b:
        y = min(b, x + max(FRAME_MS, snap(secs[k % len(secs)] * 1000)))
        out.append((x, y, shapes[k % len(shapes)]))
        x, k = y, k + 1
    return out


def expand_moves(arr: dict, song_ms: int) -> list[tuple[int, int, int, dict]]:
    """(tree, start ms, end ms, move) for every tree a move names, in order, clipped to the song."""
    out = []
    for mv in arr.get("moves", []):
        a, b = snap(mv["from"] * 1000), min(song_ms, snap(mv["until"] * 1000))
        if b - a < FRAME_MS:
            continue
        for t in (mv["tree"] if isinstance(mv["tree"], list) else [mv["tree"]]):
            out.append((t, a, b, mv))
    return out


def apply_moves(arr: dict, effects: list[fx.Fx], beats_ms: list[int], song_ms: int):
    """Lay the arrangement's moves over the effects: (effects, mouths, eye states) per tree."""
    mouths, eye_states = {t: [] for t in TREES}, {t: [] for t in TREES}
    pct = arr.get("brightness", 100)
    for t, a, b, mv in expand_moves(arr, song_ms):
        in_beats = [x for x in beats_ms if a <= x < b]
        if "outline" in mv:
            spec = mv["outline"] if isinstance(mv["outline"], dict) else {"look": mv["outline"]}
            target = f"StairTree{t}/Outline"
            effects = carve(effects, {target}, [(a, b)])
            pal = spec.get("palette", "xmas")
            new = fx.look_per_tree(spec["look"], target, a, b, in_beats, t,
                                   fx.colours_for(pal, t if pal == "rainbow" else None), spec.get("bright", 100),
                                   spec.get("params", {}))
            scale_brightness(new, pct)
            effects += new
        if "eyes" in mv:
            target = f"StairTree{t}/Eyes"
            effects = carve(effects, {target}, [(a, b)])
            look = mv["eyes"]
            if isinstance(look, int):
                look = "up" if look == t else "right" if look > t else "left"
            if look in ("closed", "open"):
                eye_states[t].append((a, b, look.capitalize()))
            else:
                new = fx.eyes(look, t, a, b, in_beats, fx.colours_for(mv.get("eye_palette", "white"), t))
                scale_brightness(new, pct * mv.get("eyes_bright", 100) // 100)
                effects += new
                eye_states[t].append((a, b, "(off)"))
        if "mouth" in mv:
            mouths[t] += mouth_pieces(mv["mouth"], a, b)
    return effects, mouths, eye_states


def scale_brightness(effects: list[fx.Fx], percent: int) -> None:
    """Scale every effect's brightness (the shared Color panel setting) by percent."""
    if percent == 100:
        return
    for e in effects:
        e.settings = {**e.settings, "brightness": max(1, round(e.settings.get("brightness", 100) * percent / 100))}


def clip_to_end(faces: dict, effects: list, end_ms: int, fade_s: float = 0, tree_end: dict | None = None):
    """Cut everything at end_ms (a tree in tree_end at its own time); effects that now end there
    fade out over fade_s."""
    tree_end = tree_end or {}

    def end_of(target: str) -> int:
        t = target.split("/")[0].removeprefix("StairTree")
        return min(end_ms, tree_end.get(int(t), end_ms)) if t.isdigit() else end_ms

    def fade(a: int, b: int, end: int) -> float:
        return round(min(fade_s, (b - a) / 1000), 2) if fade_s and b == end else 0
    out_faces = {}
    for t, plan in faces.items():
        out_faces[t] = []
        end = end_of(f"StairTree{t}")
        for a, b, s in plan:
            if a >= end:
                continue
            b = min(b, end)
            f = fade(a, b, end)
            out_faces[t].append((a, b, s + (f",T_TEXTCTRL_Fadeout={f}" if f else "")))
    out = []
    for e in effects:
        end = end_of(e.target)
        if e.start >= end:
            continue
        e.end = min(e.end, end)
        f = fade(e.start, e.end, end)
        if f:
            e.settings = {**e.settings, "fadeout": f}
        out.append(e)
    return out_faces, out


def call(cmd: dict) -> dict:
    req = urllib.request.Request(API, data=json.dumps(cmd, separators=(",", ":")).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(10):  # xLights answers 503 while it's busy (rendering, saving)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            if e.code != 503 or attempt == 9:
                raise
            time.sleep(2)


def clear(model: str) -> None:
    ids = call({"cmd": "getEffectIDs", "model": model}).get("effects", [])
    for layer, layer_ids in enumerate(ids):
        for i in sorted((int(x) for x in layer_ids), reverse=True):
            call({"cmd": "deleteEffect", "model": model, "layer": str(layer), "id": str(i)})


def add(model: str, effect: str, start: int, end: int, settings: str, palette: str, layer: int = 0) -> None:
    r = call({"cmd": "addEffect", "target": model, "effect": effect, "settings": settings,
              "palette": palette, "layer": str(layer), "startTime": str(start), "endTime": str(end)})
    if r.get("worked") != "true":
        raise SystemExit(f"addEffect {effect} on {model} layer {layer} {start}-{end} failed: {r}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arrangement", type=Path)
    ap.add_argument("--dry-run", action="store_true", help="print the plan, don't touch xLights")
    args = ap.parse_args(argv)

    arr = json.loads((ROOT / args.arrangement if not args.arrangement.is_absolute() else args.arrangement)
                     .read_text(encoding="utf-8"))
    timing = json.loads((SHOW_FOLDER / arr["lyrics_timing"]).read_text(encoding="utf-8"))
    line_times = [(s["start_time"], s["end_time"]) for s in timing["segments"]]
    if len(line_times) != len(arr["lines"]):
        raise SystemExit(f"{len(arr['lines'])} lines arranged but the timing has {len(line_times)}")
    beats = json.loads((SHOW_FOLDER / arr["beats"]).read_text(encoding="utf-8"))

    if not args.dry_run:
        seq = call({"cmd": "getOpenSequence"})
        if seq.get("seq") != arr["sequence"]:
            raise SystemExit(f"Open '{arr['sequence']}' in xLights first (open: {seq})")
        song_ms = int(seq["len"])
    else:
        song_ms = snap(max([*beats[-1:], *(e for _, e in line_times[-1:])], default=0) * 1000 + 5000)

    faces, effects, sing = plan_song(arr, line_times, beats, song_ms)
    count: dict[str, int] = {}
    for e in effects:
        count[e.target] = count.get(e.target, 0) + 1
        e.settings_string()  # validate every setting before touching xLights
    for t in TREES:
        sung = sum(b - a for a, b in sing[t]) / 1000
        print(f"StairTree{t}: sings {sung:.0f}s in {len(sing[t])} windows; {len(faces[t])} Faces, "
              f"{count.get(f'StairTree{t}/Outline', 0)} outline, {count.get(f'StairTree{t}/Eyes', 0)} eye effects")
    print(f"Outlines (whole choir): {count.get('Outlines', 0)} effects")
    if args.dry_run:
        return
    for t in TREES:
        for m in (f"StairTree{t}", f"StairTree{t}/Outline", f"StairTree{t}/Eyes"):
            clear(m)
    clear("Outlines")
    clear("Choir")      # never used by the arrangements (see tools/fx.py); cleared in case of hand edits
    for t in TREES:
        for a, b, settings in faces[t]:
            add(f"StairTree{t}", "Faces", a, b, settings, "C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1")
    for e in sorted(effects, key=lambda e: e.layer):   # layer 0 first, so layer 1 exists when it's needed
        add(e.target, e.xl_name, e.start, e.end, e.settings_string(), e.palette_string(), e.layer)
    print(call({"cmd": "renderAll"}))
    urllib.request.urlopen("http://127.0.0.1:49913/saveSequence", timeout=60).read()
    print("Rendered and saved.")


if __name__ == "__main__":
    main()
