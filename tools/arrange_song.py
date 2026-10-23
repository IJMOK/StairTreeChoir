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
  ones that are), "roll", "rainbow", "sparkle"; "blink" (default) leaves them to Faces.

Section keys: name, until (s), look, palette (name or list; "colours" also accepted),
params, accent ("flash", "sparkle_hit", "colour_hit"), accent_every, eyes.
Faces/On settings keys are from the xLights source (data/xlights-effects.json).
"""

from __future__ import annotations

import argparse
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

FACES_COMMON = ("E_CHOICE_Faces_FaceDefinition=StairTree,E_CHOICE_Faces_EyeBlinkFrequency=Normal,"
                "E_CHECKBOX_Faces_Outline=0")


def snap(ms: float) -> int:
    return int(round(ms / FRAME_MS)) * FRAME_MS


def singing_windows(arr: dict, line_times: list[tuple[float, float]], tree: int) -> list[tuple[int, int]]:
    """Merged [start, end) ms windows in which this tree sings.

    Each line's window opens LEAD_MS early and closes TAIL_MS late, but never past the
    midpoint to the neighbouring line, so a tree doesn't mouth the next singer's first
    syllable. Windows merge only across silence (consecutive lines both sung by this
    tree), never across a line someone else sings."""
    n = len(line_times)
    windows = []
    for number, group in sorted(arr["lines"].items(), key=lambda kv: int(kv[0])):
        if tree not in arr["groups"][group]:
            continue
        i = int(number) - 1
        start, end = line_times[i]
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
               eyes_off=()) -> list[tuple[int, int, str]]:
    """Back-to-back Faces effects covering the whole song: (start, end, settings)."""
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
    edges = [e for w in eyes_off for e in w]
    plan = []
    for a, b, s in pieces:
        for x, y in cut(a, b, edges):
            eyes = "(off)" if inside(x, eyes_off) else "Auto"
            plan.append((x, y, f"{s},E_CHOICE_Faces_Eyes={eyes}"))
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


def plan_song(arr: dict, line_times, beats_s: list[float], song_ms: int):
    """Everything to add: (Faces plan per tree, list of Fx, singing windows per tree)."""
    beats_ms = [snap(b * 1000) for b in beats_s]
    sing = {t: singing_windows(arr, line_times, t) for t in TREES}
    anyone = [w for t in TREES for w in sing[t]]
    sing_edges = [e for w in anyone for e in w]
    effects: list[fx.Fx] = []
    eyes_off = {t: [] for t in TREES}
    k0 = 0
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
                e.layer = layer
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
                    e.layer = layer
                effects += new
                if accent:
                    effects += fx.accents(accent, target, a, b, in_beats, cols, every)
        k0 += len(in_beats)
        mode = sec.get("eyes", "blink")
        if mode == "blink":
            continue
        for t in TREES:
            if mode == "follow":
                gz = gaze_pieces(a, b, t, sing)
                effects += fx.eyes("follow", t, a, b, in_beats, [], gz)
                eyes_off[t] += [(g0, g1) for g0, g1, _ in gz if g1 - g0 >= 100]
            else:
                effects += fx.eyes(mode, t, a, b, in_beats, fx.colours_for(spec, t))
                eyes_off[t].append((a, b))
    faces = {t: faces_plan(arr, line_times, t, song_ms, eyes_off[t]) for t in TREES}
    return faces, effects, sing


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
        song_ms = snap(max(beats[-1], line_times[-1][1]) * 1000 + 5000)

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
