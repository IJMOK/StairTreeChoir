"""Apply a song arrangement (data/songs/<song>.json) to the open xLights sequence.

    python -m tools.arrange_song data/songs/rockin-around.json [--dry-run]

Who sings which lyric line, and the outline lighting per section, are data; this
turns them into effects through xLights' automation API (Preferences → Output →
API Port A, 127.0.0.1:49913). The sequence must be open in xLights.

Per tree, every existing effect on StairTreeN and StairTreeN/Outline is replaced:
- StairTreeN: Faces effects back to back. While the tree sings a line, mouths follow
  the lyric timing track; otherwise a fixed "rest" mouth. Eyes blink throughout.
  The Faces outline is off: the Outline sub-model owns those pixels.
- StairTreeN/Outline: one On effect per beat. "pulse" flashes every tree, full
  brightness for trees singing that beat and dim for the rest, cycling the
  section's colours beat by beat; "ripple" flashes one tree per beat across the
  choir; "hold" stays lit. Sub-model effects render over the parent model's, so
  these are what show on the outline.

Settings keys are from the xLights source (FacesEffect.cpp, OnEffect.cpp, 75c3e11).
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from tools.tree_layout import ROOT

SHOW_FOLDER = Path(r"C:\Users\User\Documents\xLights")
API = "http://127.0.0.1:49913/xlDoAutomation"
FRAME_MS = 50
TREES = range(1, 7)
LEAD_MS, TAIL_MS = 100, 150  # open the singing window a little around each line
MERGE_GAP_MS = 400  # rest gaps shorter than this stay singing (no mouth snapping shut)
PULSE_START, PULSE_END = 100, 25  # On effect brightness % across one beat
REST_SCALE = 0.35  # outline brightness for trees not singing that beat

FACES_COMMON = ("E_CHOICE_Faces_FaceDefinition=StairTree,E_CHOICE_Faces_Eyes=Auto,"
                "E_CHOICE_Faces_EyeBlinkFrequency=Normal,E_CHECKBOX_Faces_Outline=0")


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


def faces_plan(arr: dict, line_times, tree: int, song_ms: int) -> list[tuple[int, int, str]]:
    """Back-to-back Faces effects covering the whole song: (start, end, settings)."""
    sing = f"E_CHOICE_Faces_TimingTrack={arr['lyrics_track']},{FACES_COMMON}"
    rest = f"E_CHOICE_Faces_Phoneme=rest,{FACES_COMMON}"
    plan, t = [], 0
    for a, b in singing_windows(arr, line_times, tree):
        if a > t:
            plan.append((t, a, rest))
        plan.append((a, b, sing))
        t = b
    if t < song_ms:
        plan.append((t, song_ms, rest))
    return plan


def section_at(arr: dict, seconds: float) -> dict:
    return next(s for s in arr["sections"] if seconds < s["until"])


def outline_plan(arr: dict, beats: list[float], tree: int, song_ms: int,
                 windows: list[tuple[int, int]],
                 anyone: list[tuple[int, int]]) -> list[tuple[int, int, str, int, int]]:
    """On effects for the tree's Outline: (start, end, colour, start %, end %)."""
    edges = [0.0] + [b for b in beats if 0 < b < song_ms / 1000] + [song_ms / 1000]
    plan = []
    for k in range(len(edges) - 1):
        a, b = snap(edges[k] * 1000), snap(edges[k + 1] * 1000)
        if b <= a:
            continue
        sec = section_at(arr, edges[k])
        colour = sec["colours"][k % len(sec["colours"])]
        style = sec["outline"]
        if style == "hold":
            lo = hi = 100
        elif style == "ripple":
            hi = PULSE_START if k % len(TREES) == tree - 1 else int(PULSE_START * REST_SCALE)
            lo = int(hi * PULSE_END / 100)
        else:  # pulse
            # Dim this tree only while another tree is singing.
            singing = any(w0 <= a < w1 for w0, w1 in windows)
            others = any(w0 <= a < w1 for w0, w1 in anyone)
            scale = REST_SCALE if others and not singing else 1.0
            hi, lo = int(PULSE_START * scale), int(PULSE_END * scale)
        plan.append((a, b, colour, hi, lo))
    # Join consecutive identical beats ("hold") into one effect.
    joined = []
    for p in plan:
        if joined and p[2:] == joined[-1][2:] and p[3] == p[4]:
            joined[-1] = (joined[-1][0], p[1], *p[2:])
        else:
            joined.append(p)
    return joined


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


def add(model: str, effect: str, start: int, end: int, settings: str, palette: str) -> None:
    r = call({"cmd": "addEffect", "target": model, "effect": effect, "settings": settings,
              "palette": palette, "layer": "0", "startTime": str(start), "endTime": str(end)})
    if r.get("worked") != "true":
        raise SystemExit(f"addEffect {effect} on {model} {start}-{end} failed: {r}")


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

    anyone = [w for t in TREES for w in singing_windows(arr, line_times, t)]
    for tree in TREES:
        model, outline = f"StairTree{tree}", f"StairTree{tree}/Outline"
        windows = singing_windows(arr, line_times, tree)
        faces = faces_plan(arr, line_times, tree, song_ms)
        beats_plan = outline_plan(arr, beats, tree, song_ms, windows, anyone)
        sung = sum(b - a for a, b in windows) / 1000
        print(f"{model}: sings {sung:.0f}s in {len(windows)} windows; "
              f"{len(faces)} Faces, {len(beats_plan)} outline effects")
        if args.dry_run:
            continue
        clear(model)
        clear(outline)
        for a, b, settings in faces:
            add(model, "Faces", a, b, settings, "C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1")
        for a, b, colour, hi, lo in beats_plan:
            add(outline, "On", a, b, f"E_TEXTCTRL_Eff_On_Start={hi},E_TEXTCTRL_Eff_On_End={lo}",
                f"C_BUTTON_Palette1={colour},C_CHECKBOX_Palette1=1")
    if not args.dry_run:
        print(call({"cmd": "renderAll"}))
        urllib.request.urlopen("http://127.0.0.1:49913/saveSequence", timeout=60).read()
        print("Rendered and saved.")


if __name__ == "__main__":
    main()
