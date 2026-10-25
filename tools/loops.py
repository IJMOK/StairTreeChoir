"""The silent loops, scene by scene: the Waiting loop between shows, the Night loop after the
Goodnight, and the Lights Out that ends them.

    python -m tools.loops                 # write data/loops/*.json
    python -m tools.loops --xlights       # also create, arrange and render every sequence in xLights
    python -m tools.loops --xlights --only night-03

Each loop is a run of short sequences ("Waiting 1" ... "Waiting 10", "Night 1" ... "Night 8"),
one scene each, which an FPP playlist plays in order and repeats. Short pieces because FPP's
graceful stop (Home Assistant's "lights out", the 23:30 backstop) waits for the piece that's
playing to end before it plays the playlist's lead-out (Lights Out): a minute at most.

No audio anywhere. The six characters muck about with eyes, outlines and mouth shapes, through
arrange_song "moves" over a background look per scene. Slots: 1 Holly (conductor), 2 Ivy
(sidekick), 3 Noel (show-off), 4 Jingle (over-excited), 5 Bramble (sleepy), 6 Pip (joker);
docs/backstory.md. Nothing strobes: the quickest thing on a whole tree is Jingle's bounce.

The arrangements in data/loops/ are generated: change the scenes here and re-run. The asleep
variants are generated from the same scenes, so they can't drift: "Waiting Asleep" is the
Waiting loop with Bramble asleep throughout (his own moves dropped; the others still look at
him and nudge him, and he sleeps on), "Night Christmas Eve" is everyone asleep.

The Morning loop isn't scheduled: Home Assistant starts it with Rob's alarm and stops it
gracefully at the morning lights out. As a backstop its playlist (tools/gen_site_config.py)
lists the Morning pieces over and over for MORNING_HOURS with repeat off, so it ends by itself
through its lead-out (Morning Lights Off) if the stop never comes.
"""

from __future__ import annotations

import argparse
import json
import time

from tools.tree_layout import ROOT

LOOPS_DIR = ROOT / "data" / "loops"
HOLLY, IVY, NOEL, JINGLE, BRAMBLE, PIP = range(1, 7)
ALL = list(range(1, 7))
COL = {HOLLY: "#FF2020", IVY: "#20D060", NOEL: "#FFC000", JINGLE: "#FF7A00", BRAMBLE: "#3050C0", PIP: "#FF40C0"}
GOLD, WARM, ICE_WHITE = "#FFD040", "#FF9040", "#C0E8FF"
NIGHT_BRIGHTNESS = 45            # % for the Night loop and Lights Out: late, and there are neighbours
NIGHT_BG = {"lo": 30, "hi": 75, "period": 5.0, "stagger": 0.8}   # the settled, breathing state
WAITING_S, NIGHT_S, XMAS_EVE_S, MORNING_S = 60, 50, 40, 45
LIGHTS_OUT_S, LIGHTS_OUT_ASLEEP_S, MORNING_OFF_S = 20, 12, 15

# Sequence names (FPP plays "<name>.fseq")
WAITING, WAITING_ASLEEP, NIGHT, NIGHT_XMAS_EVE = "Waiting", "Waiting Asleep", "Night", "Night Christmas Eve"
LIGHTS_OUT, LIGHTS_OUT_ASLEEP = "Lights Out", "Lights Out Asleep"
MORNING, MORNING_OFF = "Morning", "Morning Lights Off"


class Scene:
    """One sequence: a background (arrange_song sections) and the characters' moves on top.
    Later moves win over earlier ones where they overlap."""

    def __init__(self, title: str, seconds: float, sections: list[dict]):
        self.title, self.seconds, self.sections, self.moves = title, seconds, sections, []

    def move(self, tree, a: float, b: float, **kw) -> None:
        b = min(b, self.seconds)
        if b - a >= 0.1:
            self.moves.append({"tree": tree, "from": round(a, 2), "until": round(b, 2), **kw})

    # -- little bits of business ----------------------------------------------------------
    def look_at(self, a, b, target, who=None):
        for t in who or [t for t in ALL if t != target]:
            self.move(t, a, b, eyes=target)

    def wave(self, a, order, colours, step=0.5, dur=1.4, mouth="O"):
        """A Mexican wave: each tree in turn swells, looks up and goes "oh"."""
        for k, t in enumerate(order):
            c = colours[t] if isinstance(colours, dict) else colours
            x = a + k * step
            self.move(t, x, x + dur, outline={"look": "swell", "palette": [c], "params": {"lo": 50}}, eyes="up")
            if mouth:
                self.move(t, x + 0.1, x + dur * 0.6, mouth=mouth)

    def ball(self, a, path, hop=1.0, colour=GOLD, catch=True):
        """A ball of light passed along: the holder spins it round its outline and everyone
        else watches it; a tree it flies over looks up. Returns the time it lands."""
        for i, t in enumerate(path):
            x, y = a + i * hop, a + (i + 1) * hop
            self.move(t, x, y, outline={"look": "ball", "palette": [colour], "params": {"size": 8, "speed": 25}},
                      eyes="open")
            for o in ALL:
                if o != t:
                    self.move(o, x, y, eyes=t)
            if catch:
                self.move(t, x, x + min(0.45, hop * 0.6), mouth="O")
            if i + 1 < len(path):
                nxt = path[i + 1]
                for over in range(min(t, nxt) + 1, max(t, nxt)):
                    self.move(over, y - hop * 0.3, y + hop * 0.2, eyes="up")
        return a + len(path) * hop

    def yawn(self, t, a, dur=2.6):
        self.move(t, a, a + dur, mouth="yawn")
        self.move(t, a + dur * 0.25, a + dur * 0.8, eyes="closed")

    def doze(self, t, a, b, colour=COL[BRAMBLE], snore=True):
        """Eyes droop, close, slow dim breath, snoring."""
        self.move(t, a, min(b, a + 2.0), eyes="heavy")
        self.move(t, a + 2.0, b, eyes="closed",
                  outline={"look": "breathe", "palette": [colour], "params": {"lo": 12, "hi": 50, "period": 4.0}})
        if snore:
            self.move(t, a + 2.5, b, mouth="snore")

    def shush(self, a, target, by=HOLLY, dur=2.2):
        self.move(by, a, a + dur, mouth="shush", eyes=target,
                  outline={"look": "swell", "palette": [COL[by]], "params": {"lo": 40}})

    def giggle(self, t, a, dur=1.6, sparkle=True):
        self.move(t, a, a + dur, mouth="giggle")
        if sparkle:
            self.move(t, a, a + dur, outline={"look": "sparkle", "palette": [COL[t], "#FFFFFF"]})

    def bounce(self, t, a, b, period=0.5, lo=35, hi=100):
        self.move(t, a, b, outline={"look": "bounce", "palette": [COL[t]],
                                    "params": {"period": period, "lo": lo, "hi": hi}})

    def roll(self, trees, a, b):
        for t in trees:
            self.move(t, a, b, eyes="roll")

    def passer_by(self, a, right_to_left=True, step=0.3, each=1.8):
        """Someone walks past: the trees nearest them notice first; eyes follow them across."""
        order = list(reversed(ALL)) if right_to_left else ALL
        first, last = ("right", "left") if right_to_left else ("left", "right")
        for k, t in enumerate(order):
            x = a + k * step
            self.move(t, x, x + each, eyes=first)
            self.move(t, x + each, x + 2 * each, eyes="down")
            self.move(t, x + 2 * each, x + 3 * each, eyes=last)

    def hum(self, trees, a, b, stagger=0.35):
        for k, t in enumerate(trees):
            self.move(t, a + k * stagger, b, mouth="hum")

    def arrangement(self, sequence: str, asleep: list[int] = (), brightness: int = 100, extra: dict | None = None,
                    sleepers_act: bool = False) -> dict:
        """The arrangement for one sequence. Trees in asleep sleep throughout and their moves are
        dropped, unless sleepers_act (the moves are then their stirring in their sleep)."""
        moves = []
        for m in self.moves:
            trees = m["tree"] if isinstance(m["tree"], list) else [m["tree"]]
            awake = trees if sleepers_act else [t for t in trees if t not in asleep]
            if awake:
                moves.append({**m, "tree": awake if len(awake) > 1 else awake[0]})
        arr = {
            "sequence": sequence, "audio": None,
            "lyrics_timing": "Audio/Loops/Waiting.timing.json", "lyrics_track": "Waiting",
            "beats": "Audio/Loops/Waiting.beats.json", "seconds": self.seconds,
            "groups": {}, "lines": {}, "sections": self.sections,
        }
        if brightness != 100:
            arr["brightness"] = brightness
        if asleep:
            arr["asleep"] = [{"tree": t, "from": None, "until": None} for t in asleep]
        arr["moves"] = moves
        arr.update(extra or {})
        arr["notes"] = f"{self.title}. Generated by tools/loops.py; don't edit, change the scene there."
        return arr


def sec(until, look, eyes="blink", **kw) -> dict:
    return {"name": look, "until": until, "look": look, "eyes": eyes, **kw}


# ------------------------------------------------------------------------- Waiting (10 min) ----

def waiting_scenes() -> list[Scene]:
    S = WAITING_S
    out = []

    s = Scene("Mexican wave: down the line, back in everyone's own colour, then faster; Bramble is late",
              S, [sec(999, "rainbow_wash", "glance", palette="rainbow")])
    s.move(HOLLY, 1.5, 4.0, eyes="right", mouth="MBP")
    s.wave(4.5, ALL, GOLD)
    s.giggle(JINGLE, 8.5, 1.6)
    s.bounce(JINGLE, 8.5, 11.0)
    s.wave(11.5, list(reversed(ALL)), COL)
    s.giggle(PIP, 15.5)
    s.wave(19.0, [t for t in ALL if t != BRAMBLE], ICE_WHITE, step=0.35, dur=1.2)
    s.move(BRAMBLE, 23.0, 24.6, outline={"look": "swell", "palette": [ICE_WHITE]}, eyes="up", mouth="O")
    s.look_at(23.2, 26.5, BRAMBLE)
    s.roll([HOLLY], 24.8, 26.8)
    s.giggle(PIP, 25.0, 1.4, sparkle=False)
    s.bounce(JINGLE, 40, 44)
    s.move(IVY, 50, 53, eyes=HOLLY)
    out.append(s)

    s = Scene("Noel shows off with a rainbow shimmer; the others roll their eyes; Holly stops him; he tries again",
              S, [sec(999, "choir_butterfly", params={"speed": 5})])
    s.look_at(4, 14, NOEL)
    s.doze(BRAMBLE, 4, 15, snore=False)
    s.roll([HOLLY, IVY], 8, 11.5)
    s.move(NOEL, 3, 14, outline={"look": "chase", "palette": "rainbow", "params": {"colors": "Rainbow", "per_bar": 1.5}},
           eyes="rainbow")
    s.move(NOEL, 3, 4, mouth="MBP")
    s.move(NOEL, 4, 12, mouth="O")
    s.move(NOEL, 12, 14, mouth="AI")
    s.shush(14, NOEL)
    s.move(NOEL, 16.5, 20, eyes="down", outline={"look": "glow", "palette": [COL[NOEL]], "bright": 40})
    s.move(NOEL, 24, 32, outline={"look": "sparkle", "palette": [COL[NOEL], "#FF0000", "#FFE600", "#00E05A", "#0090FF", "#7A00FF"],
                                  "params": {"base": 60}}, eyes="up", mouth="O")
    s.roll([HOLLY, IVY, JINGLE, PIP], 25, 31)
    s.move(BRAMBLE, 25, 31, eyes="heavy")
    s.move(IVY, 32, 35, eyes=HOLLY, mouth="whisper")
    s.move(HOLLY, 32, 35, eyes=IVY)
    s.giggle(PIP, 36, 1.8)
    s.giggle(JINGLE, 36.4, 1.6)
    s.move(NOEL, 46, 52, eyes="rainbow")
    s.move(HOLLY, 48, 52, eyes=NOEL)
    out.append(s)

    s = Scene("Pass the ball: Pip and Jingle throw a ball of light over Bramble, up to Holly, who throws it back; Pip drops it",
              S, [sec(999, "breathe", palette="rainbow", params={"lo": 25, "hi": 60, "period": 4.0, "stagger": 0.6})])
    t = s.ball(2.0, [PIP, JINGLE, PIP, JINGLE, NOEL, IVY, HOLLY], hop=1.1)
    s.move(HOLLY, t, t + 2.4, outline={"look": "glow", "palette": [GOLD]}, eyes=PIP)
    s.look_at(t, t + 2.4, HOLLY)
    t = s.ball(t + 2.4, [HOLLY, IVY, NOEL, JINGLE, BRAMBLE, PIP], hop=0.35, colour="#FFFFFF", catch=False)
    s.move(PIP, t, t + 1.0, outline={"look": "swell", "palette": ["#FFFFFF"]}, mouth="O", eyes="open")
    for o in ALL:
        s.move(o, t + 0.6, t + 2.6, eyes="down")
    s.giggle(PIP, t + 2.6, 1.8)
    s.roll([HOLLY], t + 2.8, t + 4.6)
    s.bounce(JINGLE, 33, 37)
    s.move(JINGLE, 33, 37, eyes=PIP)
    t = s.ball(37.5, [PIP, JINGLE], hop=1.2, colour=COL[PIP])
    s.move(JINGLE, t, t + 4, outline={"look": "ball", "palette": [COL[PIP]], "params": {"size": 8, "speed": 30}},
           mouth="giggle", eyes="up")
    s.roll([HOLLY], t + 0.5, t + 3)
    out.append(s)

    s = Scene("Bramble nods off; Ivy tells Holly; Holly's nudge runs down the line and he wakes with a start",
              S, [sec(999, "spiral", palette="xmas", params={"rotation": 1.5, "movement": 1.0})])
    s.move(BRAMBLE, 2, 8, eyes="heavy")
    s.yawn(BRAMBLE, 4, 3.0)
    s.doze(BRAMBLE, 8, 22.5)
    s.move(IVY, 12, 15, eyes=BRAMBLE)
    s.move(IVY, 15, 18, eyes=HOLLY, mouth="whisper")
    s.move(HOLLY, 15, 18, eyes=IVY)
    s.move(HOLLY, 18, 21, eyes=BRAMBLE)
    s.move(HOLLY, 19, 20.5, outline={"look": "swell", "palette": [COL[HOLLY]]})
    for k, t in enumerate((IVY, NOEL, JINGLE)):
        s.move(t, 20.4 + 0.45 * k, 21.2 + 0.45 * k, outline={"look": "sparkle", "palette": [COL[HOLLY], "#FFFFFF"]},
               eyes=BRAMBLE)
    s.move(BRAMBLE, 22.5, 24.5, eyes="open", mouth="O", outline={"look": "swell", "palette": [GOLD], "params": {"lo": 30}})
    s.look_at(22.5, 26, BRAMBLE)
    s.giggle(PIP, 23.2)
    s.giggle(JINGLE, 23.5)
    s.move(BRAMBLE, 24.5, 34, eyes="heavy")
    s.yawn(BRAMBLE, 34, 3.0)
    s.move(BRAMBLE, 37, 60, eyes="heavy")
    s.passer_by(45)
    out.append(s)

    s = Scene("Ivy copies everything Holly does, a beat behind; Holly notices; Pip joins in",
              S, [sec(999, "marquee", palette="xmas", params={"speed": 3})])
    copy = [(3.0, 1.5, {"eyes": "up"}), (6.0, 1.5, {"eyes": "right"}),
            (9.0, 1.2, {"outline": "swell", "mouth": "O"}), (12.0, 1.6, {"eyes": "roll"}),
            (15.0, 1.5, {"mouth": "MBP", "eyes": "down"}), (23.0, 0.7, {"eyes": "left"}),
            (23.7, 0.7, {"eyes": "right"}), (26.0, 1.5, {"outline": "sparkle"})]
    for a, d, mv in copy:
        for t, lag in ((HOLLY, 0.0), (IVY, 0.8)) + (((PIP, 1.6),) if a >= 23 else ()):
            kw = dict(mv)
            if "outline" in kw:
                kw["outline"] = {"look": kw["outline"], "palette": [COL[t], "#FFFFFF"] if kw["outline"] == "sparkle" else [COL[t]]}
            s.move(t, a + lag, a + lag + d, **kw)
    s.move(HOLLY, 19.0, 21.5, eyes=IVY)
    s.move(IVY, 19.5, 22.0, eyes="up", mouth="hum")
    s.move(HOLLY, 30.0, 32.5, eyes=PIP, outline={"look": "glow", "palette": [COL[HOLLY]]})
    s.move(IVY, 30.8, 33.0, eyes=PIP)
    s.move(PIP, 30.5, 33.0, eyes="down")
    s.roll([NOEL], 33, 35.5)
    s.giggle(JINGLE, 34, 1.8)
    s.passer_by(46, right_to_left=False)
    out.append(s)

    s = Scene("Jingle can't keep still: bouncing, eyes rolling, chattering; Holly shushes him; Pip joins in",
              S, [sec(999, "plasma", palette="xmas", params={"speed": 8})])
    s.bounce(JINGLE, 2, 14)
    s.move(JINGLE, 2, 14, eyes="roll")
    s.move(JINGLE, 4, 12, mouth="chatter")
    s.look_at(5, 14, JINGLE, [NOEL, BRAMBLE])
    s.shush(14, JINGLE, dur=2.5)
    s.move(JINGLE, 16.5, 22, eyes="open", mouth="MBP", outline={"look": "glow", "palette": [COL[JINGLE]], "bright": 60})
    s.move(JINGLE, 22, 23, eyes="left")
    s.move(JINGLE, 23, 24, eyes="right")
    s.bounce(JINGLE, 25, 36)
    s.bounce(PIP, 27, 36, period=0.6)
    s.move(PIP, 27, 30, eyes=JINGLE)
    s.giggle(JINGLE, 30, 4, sparkle=False)
    s.giggle(PIP, 30.3, 3.7, sparkle=False)
    s.roll([HOLLY], 31, 33)
    s.shush(36, BRAMBLE)
    for t in (JINGLE, PIP):
        s.move(t, 38, 44, eyes="down", outline={"look": "glow", "palette": [COL[t]], "bright": 50})
    s.bounce(JINGLE, 52, 54)
    out.append(s)

    s = Scene("Passers-by: the trees watch someone walk past, show off to them, pose; a silent hum to finish",
              S, [sec(40, "choir_rainbow"), sec(999, "breathe", palette="rainbow",
                                                params={"lo": 30, "hi": 85, "period": 4.0, "stagger": 0.5})])
    s.passer_by(4)
    for k, t in enumerate(ALL):
        s.move(t, 10 + 0.2 * k, 14, eyes="down", outline={"look": "swell", "palette": [COL[t]], "params": {"lo": 50}})
    s.bounce(JINGLE, 10, 15)
    s.move(NOEL, 11, 15, eyes="rainbow")
    s.giggle(PIP, 12, 1.2, sparkle=False)
    s.move(HOLLY, 15, 17, eyes="right", mouth="O")
    for t in ALL:
        s.move(t, 17, 20, eyes="open", mouth="MBP")
    s.passer_by(24, right_to_left=False)
    s.move(BRAMBLE, 33, 35, eyes="right")
    s.giggle(PIP, 34, 1.5)
    s.hum(ALL, 41, 58)
    for t in ALL:
        s.move(t, 41, 58, eyes="heavy")
    s.move(HOLLY, 41, 58, eyes="up")
    out.append(s)

    s = Scene("The silent hum: Holly conducts, Noel holds the last note far too long, Holly stops him, he bows",
              S, [sec(999, "breathe", palette="rainbow", params={"lo": 30, "hi": 90, "period": 4.0, "stagger": 0.6})])
    s.hum([IVY, NOEL, JINGLE, BRAMBLE, PIP], 2, 20)
    s.move(HOLLY, 2, 20, eyes="up", outline={"look": "bounce", "palette": [COL[HOLLY]], "params": {"period": 1.2, "lo": 40}})
    s.move(NOEL, 12, 26, mouth="O")
    s.move(NOEL, 14, 26, eyes="closed")
    s.move(NOEL, 12, 18, outline={"look": "glow", "palette": [COL[NOEL]]})
    s.move(NOEL, 18, 26, outline={"look": "sparkle", "palette": [COL[NOEL], "#FFFFFF"]})
    s.look_at(20, 26, NOEL)
    s.roll([IVY, PIP], 22, 25)
    s.shush(26, NOEL)
    s.move(NOEL, 28, 28.5, mouth="AI")
    s.move(NOEL, 28, 30, eyes="open")
    s.move(NOEL, 30, 32, eyes="down", outline={"look": "swell", "palette": [GOLD]})
    s.move(JINGLE, 32, 35, outline={"look": "sparkle", "palette": [COL[JINGLE], "#FFFFFF"]}, mouth="O")
    s.giggle(PIP, 32.5)
    s.move(BRAMBLE, 44, 52, eyes="heavy")
    s.yawn(BRAMBLE, 45, 3.0)
    out.append(s)

    s = Scene("Colour relay: every tree passes its colour to its neighbour; Pip muddles it; then the ball goes round everyone",
              S, [sec(40, "glow", palette="rainbow"), sec(999, "spiral", "glance", palette="ice",
                                                         params={"rotation": 2.0, "movement": 1.0})])
    for r in range(1, 6):
        for t in ALL:
            a = 2 + (r - 1) * 3 + (t - 1) * 0.25
            c = ["#FF0000", "#FF7A00", "#FFE600", "#00E05A", "#0090FF", "#7A00FF"][(t - 1 - r) % 6]
            s.move(t, a, 20, outline={"look": "glow", "palette": [c]})
            s.move(t, a, a + 0.8, eyes="left" if t > 1 else "right")
    s.move(PIP, 20, 23, outline={"look": "sparkle", "palette": "rainbow"}, mouth="O")
    s.look_at(20.3, 23.5, PIP)
    s.shush(23.5, PIP)
    s.move(PIP, 25.5, 28, eyes="down")
    for t in ALL:
        s.move(t, 28, 39, outline={"look": "ball", "palette": ["#FFFFFF"], "params": {"size": 6, "speed": 20}}, eyes="roll")
    s.giggle(JINGLE, 37, 2.0, sparkle=False)
    out.append(s)

    s = Scene("Snow: everyone looks up in wonder; Jingle's delighted; Pip catches a snowflake; then cosy by the fire",
              S, [sec(30, "spiral", palette="ice", params={"rotation": 2.0, "movement": 1.0}),
                  sec(999, "fire", "glance", params={"height": 70})])
    for k, t in enumerate(ALL):
        s.move(t, 3 + 0.4 * k, 12, eyes="up")
        s.move(t, 4 + 0.4 * k, 6.5 + 0.4 * k, mouth="O")
        s.move(t, 5 + 0.6 * k, 5.6 + 0.6 * k, outline={"look": "sparkle", "palette": [ICE_WHITE, "#FFFFFF"]})
    s.bounce(JINGLE, 12, 16)
    s.giggle(JINGLE, 12.5, 2.0, sparkle=False)
    s.yawn(BRAMBLE, 16, 3.0)
    s.move(BRAMBLE, 19, 22, eyes="heavy")
    s.move(PIP, 20, 22, eyes="up")
    s.move(PIP, 22, 23.2, outline={"look": "sparkle", "palette": ["#FFFFFF"]}, mouth="O", eyes="open")
    s.giggle(PIP, 23.2, 1.6, sparkle=False)
    s.roll([NOEL], 23.5, 25.5)
    for t in ALL:
        s.move(t, 32, 40, eyes="heavy")
    s.hum(ALL, 34, 40)
    s.move(HOLLY, 45, 50, eyes="right")
    for t in ALL:
        s.move(t, 50, 52.5, eyes="open")
    out.append(s)
    return out


# ------------------------------------------------------------------------- Night (~7 min) ----

def night_bg(colour=WARM, **params) -> list[dict]:
    return [sec(999, "breathe", palette=[colour], params={**NIGHT_BG, **params})]


def night_scenes() -> list[Scene]:
    S = NIGHT_S
    out = []

    s = Scene("Settling down: yawns go round, Bramble's already snoring, Jingle's wide awake until Holly shushes him",
              S, night_bg())
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, PIP):
        s.move(t, 0, S, eyes="heavy")
    s.move(JINGLE, 0, 30, eyes="open")
    s.yawn(HOLLY, 6, 2.8)
    s.yawn(IVY, 8.5, 2.8)
    s.yawn(NOEL, 12, 4.0)
    s.yawn(PIP, 17, 2.2)
    for k in range(5):
        s.move(JINGLE, 10 + 4 * k, 12 + 4 * k, eyes="left" if k % 2 == 0 else "right")
    s.shush(30, JINGLE)
    s.move(JINGLE, 32.2, S, eyes="closed")
    s.move(PIP, 40, S, eyes="closed")
    s.move(NOEL, 42, S, eyes="closed")
    out.append(s)

    s = Scene("Can't sleep: Jingle peeks, whispers to Pip, Pip whispers back; Holly shushes; Jingle peeks again",
              S, night_bg("#3060FF", period=6.0, stagger=0.6))
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(JINGLE, 5, 8, eyes="wink")
    s.move(JINGLE, 8, 11, eyes="left")
    s.move(JINGLE, 11, 14, eyes="right")
    s.move(JINGLE, 14, 18, eyes=PIP, mouth="whisper")
    s.bounce(JINGLE, 14, 18, period=1.0, lo=15, hi=45)
    s.move(PIP, 16, 18, eyes=JINGLE)
    s.move(PIP, 18, 21, eyes=JINGLE, mouth="whisper")
    s.shush(21, BRAMBLE, dur=2.8)
    s.move(JINGLE, 36, 39, eyes="wink")
    s.move(HOLLY, 39.5, 42, eyes=JINGLE)
    s.move(HOLLY, 39.5, 42, eyes="heavy")
    s.move(HOLLY, 40.5, 42, eyes=JINGLE)
    out.append(s)

    s = Scene("Doze and poke: Noel nods off, Jingle pokes him and pretends to be asleep; later Pip does it too",
              S, [sec(999, "fire", params={"height": 25})])
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, JINGLE, PIP):
        s.move(t, 0, S, eyes="heavy")
    s.doze(NOEL, 4, 14.5, colour=COL[NOEL], snore=True)
    s.move(JINGLE, 12, 14, eyes=NOEL)
    s.move(JINGLE, 14, 15, outline={"look": "swell", "palette": [COL[JINGLE]]})
    s.move(NOEL, 14.5, 16.5, eyes="open", mouth="O", outline={"look": "swell", "palette": [COL[NOEL]], "params": {"lo": 30}})
    s.move(JINGLE, 15, 21, eyes="closed")
    s.move(NOEL, 16.5, 21, eyes=JINGLE)
    s.doze(NOEL, 21, 33.5, colour=COL[NOEL])
    s.move(PIP, 30, 32, eyes=NOEL)
    s.giggle(PIP, 32, 1.2)
    s.move(NOEL, 33.5, 35, eyes="open", outline={"look": "swell", "palette": [COL[NOEL]], "params": {"lo": 30}})
    s.move(NOEL, 35, 38, eyes=PIP)
    s.move(PIP, 33.5, 40, eyes="closed")
    for t in (IVY, NOEL, JINGLE, PIP):
        s.move(t, 40, S, eyes="closed")
    out.append(s)

    s = Scene("Snore glow: Bramble snores, his glow swelling with every snore; Ivy rolls her eyes; Holly's nudge travels down the line",
              S, night_bg("#9050FF", stagger=0.9))
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(BRAMBLE, 0, S, eyes="closed")
    s.move(BRAMBLE, 0, 26.5, mouth="snore",
           outline={"look": "breathe", "palette": [COL[BRAMBLE]], "params": {"lo": 10, "hi": 100, "period": 3.5}})
    s.move(IVY, 8, 12, eyes=BRAMBLE)
    s.roll([IVY], 12, 15)
    s.move(IVY, 15, 18, eyes=HOLLY, mouth="whisper")
    s.move(HOLLY, 16, 19, eyes=IVY)
    s.move(HOLLY, 19, 25, eyes=BRAMBLE)
    s.move(HOLLY, 21, 23, mouth="O")
    s.move(HOLLY, 23, 24.5, outline={"look": "swell", "palette": [COL[HOLLY]]})
    for k, t in enumerate((IVY, NOEL, JINGLE)):
        s.move(t, 24.5 + 0.5 * k, 25.5 + 0.5 * k, outline={"look": "swell", "palette": [COL[HOLLY]], "params": {"lo": 10}})
    s.move(BRAMBLE, 26.5, 38, outline={"look": "breathe", "palette": [COL[BRAMBLE]], "params": {"lo": 15, "hi": 45, "period": 5.0}})
    s.move(BRAMBLE, 38, S, mouth="snore",
           outline={"look": "breathe", "palette": [COL[BRAMBLE]], "params": {"lo": 8, "hi": 50, "period": 4.0}})
    s.roll([HOLLY], 40, 42.5)
    out.append(s)

    s = Scene("Giggles: Pip and Jingle set each other off, a sparkle passing between them over sleeping Bramble; Holly shushes",
              S, night_bg("#20C0C0"))
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(PIP, 5, 16, eyes=JINGLE)
    s.move(JINGLE, 6.5, 16, eyes=PIP)
    for k, t in enumerate((PIP, JINGLE, PIP, JINGLE)):
        s.giggle(t, 8 + 2 * k, 1.8)
        s.move(BRAMBLE, 9.6 + 2 * k, 10.2 + 2 * k, outline={"look": "sparkle", "palette": ["#FFFFFF"], "params": {"count": 20, "base": 0}})
    s.shush(16, BRAMBLE, dur=2.6)
    s.giggle(PIP, 26, 0.8)
    s.move(HOLLY, 27, 30, eyes=PIP)
    out.append(s)

    s = Scene("Peekaboo: they take turns to peek; Pip and Holly peek at each other at the same moment; Bramble talks in his sleep",
              S, night_bg("#4060FF", stagger=1.2))
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(IVY, 6, 8, eyes="left")
    s.move(IVY, 8, 10, eyes="right")
    s.move(PIP, 12, 16, eyes=HOLLY)
    s.move(HOLLY, 14, 16, eyes=PIP)
    s.move(NOEL, 20, 22, eyes="wink")
    s.move(NOEL, 22, 24, eyes="rainbow", eyes_bright=50)
    s.move(JINGLE, 28, 32, eyes="up", mouth="O")
    s.move(BRAMBLE, 33, 36, mouth="whisper")
    s.look_at(34, 38, BRAMBLE, [HOLLY, IVY, NOEL, JINGLE, PIP])
    out.append(s)

    s = Scene("Noel's dream: asleep, he glitters gold and silently sings his solo; Holly rolls her eyes",
              S, [sec(999, "spiral", palette="ice", params={"rotation": 0.8, "movement": 0.5})])
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(NOEL, 6, 30, outline={"look": "sparkle", "palette": [COL[NOEL], "#FFFFFF"], "params": {"count": 30, "base": 15}})
    s.move(NOEL, 8, 24, mouth="hum")
    s.move(NOEL, 24, 28, mouth="O")
    s.move(HOLLY, 14, 18, eyes=NOEL)
    s.roll([HOLLY], 18, 21)
    s.move(IVY, 28, 31, eyes=NOEL, mouth="whisper")
    out.append(s)

    s = Scene("Deep sleep: slow breaths roll down the line, soft snores; Holly checks everyone's asleep",
              S, night_bg("#3060FF", period=7.0, stagger=1.5, lo=20, hi=60))
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, JINGLE, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(NOEL, 20, 40, mouth="snore")
    s.move(HOLLY, 40, 43, eyes="heavy")
    s.move(HOLLY, 43, 47, eyes="right", eyes_bright=60)
    s.move(HOLLY, 47, S, eyes="heavy")
    for t in (IVY, NOEL, JINGLE, PIP):
        s.move(t, 46, S, eyes="heavy")
    out.append(s)
    return out


def xmas_eve_scenes() -> list[Scene]:
    """Christmas Eve: all asleep for Santa; only the gentlest stirring."""
    S = XMAS_EVE_S
    bg = [sec(999, "breathe", palette=["#2040A0"], params={"lo": 6, "hi": 30, "period": 4.0})]   # under the sleepers
    a = Scene("Asleep for Santa: Pip peeks to see if he's been; Jingle giggles in a dream; Bramble snores", S, bg)
    a.move(PIP, 10, 13, eyes="wink")
    a.move(JINGLE, 20, 22, mouth="giggle")
    a.move(BRAMBLE, 26, 34, mouth="snore")
    b = Scene("Asleep for Santa: Bramble snores, Ivy hums in her sleep, Noel dreams in gold", S, bg)
    b.move(BRAMBLE, 6, 14, mouth="snore")
    b.move(IVY, 18, 22, mouth="hum")
    b.move(NOEL, 25, 30, outline={"look": "sparkle", "palette": [COL[NOEL]], "params": {"count": 20, "base": 10}})
    c = Scene("Asleep for Santa: Holly checks everyone's asleep; Jingle looks up for the sleigh", S, bg)
    c.move(HOLLY, 5, 8, eyes="wink")
    c.move(BRAMBLE, 15, 21, mouth="snore")
    c.move(JINGLE, 30, 32, eyes="up")
    return [a, b, c]


def lights_out() -> Scene:
    """The lead-out of the Waiting and Night playlists: everyone settles, a last yawn, Holly
    shushes, eyes close, and the trees go dark one by one. Ends black (FPP holds the last frame)."""
    s = Scene("Lights out: yawns, Jingle's last look round, Holly shushes, eyes close, the trees go dark one by one",
              LIGHTS_OUT_S, night_bg())
    s.doze(BRAMBLE, 0, LIGHTS_OUT_S)
    for t in (HOLLY, IVY, NOEL, PIP, JINGLE):
        s.move(t, 0, LIGHTS_OUT_S, eyes="heavy")
    s.yawn(HOLLY, 1, 2.8)
    s.yawn(IVY, 2.5, 2.8)
    s.yawn(NOEL, 4, 3.4)
    s.yawn(PIP, 6, 2.6)
    s.move(JINGLE, 6.5, 8.5, eyes="left")
    s.move(JINGLE, 8.5, 10, eyes="right")
    s.shush(10, JINGLE, dur=2.2)
    for t in ALL:
        s.move(t, 12.5, LIGHTS_OUT_S, eyes="closed")
    return s


LIGHTS_OUT_ORDER = {JINGLE: 13.5, PIP: 14.5, NOEL: 15.5, IVY: 16.5, BRAMBLE: 17.5, HOLLY: 18.5}   # Holly last


def lights_out_asleep() -> Scene:
    return Scene("Lights out on Christmas Eve: the sleeping trees fade out one by one", LIGHTS_OUT_ASLEEP_S,
                 [sec(999, "breathe", palette=["#2040A0"], params={"lo": 6, "hi": 30, "period": 4.0})])


# ----------------------------------------------------------------------- Morning (~4.5 min) ----

SUNRISE = ["#FF6080", "#FFA040", "#FFD070"]         # pink, orange, gold
DAYLIGHT = ["#FFF0D0", "#C0E8FF", "#FFFFFF"]


def morning_scenes() -> list[Scene]:
    """Started by Home Assistant with Rob's alarm, stopped at the morning lights out (or by
    itself after about three hours: see MORNING_HOURS)."""
    S = MORNING_S
    out = []

    s = Scene("Waking up: Jingle's been awake for ages; eyes open one by one with yawns and stretches; Bramble snores on",
              S, [sec(999, "breathe", palette=[SUNRISE[0]], params={"lo": 15, "hi": 60, "period": 5.0, "stagger": 0.7})])
    s.doze(BRAMBLE, 0, S)
    for t in (HOLLY, IVY, NOEL, PIP):
        s.move(t, 0, S, eyes="closed")
    s.move(JINGLE, 0, S, eyes="open")
    s.bounce(JINGLE, 0, 8, period=0.6)
    for k, (t, a) in enumerate(((HOLLY, 3), (IVY, 6), (PIP, 9), (NOEL, 12))):
        s.move(t, a, a + 2.5, eyes="heavy")
        s.yawn(t, a + 0.5, 3.6 if t == NOEL else 2.6)
        s.move(t, a + 3.5, a + 5.5, outline={"look": "swell", "palette": [SUNRISE[2]], "params": {"lo": 30}}, eyes="up")
        s.move(t, a + 5.5, S, eyes="heavy" if a + 5.5 < 25 else "open")
    s.move(JINGLE, 20, 30, eyes="roll")
    s.bounce(JINGLE, 20, 30, period=0.5)
    for t in (HOLLY, IVY, NOEL, PIP):
        s.move(t, 30, S, eyes="open")
    s.look_at(31, 36, BRAMBLE, [IVY, NOEL, JINGLE, PIP])
    out.append(s)

    s = Scene("Holly's roll call: she looks at each tree in turn and they answer with a blink and a colour pop; "
              "Jingle answers too early, Noel shows off, Bramble doesn't answer at all",
              S, [sec(999, "breathe", palette=[SUNRISE[2]], params={"lo": 40, "hi": 75, "period": 4.0, "stagger": 0.5})])
    s.doze(BRAMBLE, 0, S, snore=True)
    t0 = 3.0
    for k, t in enumerate((IVY, NOEL, JINGLE, BRAMBLE, PIP)):
        a = t0 + 3.5 * k
        s.move(HOLLY, a, a + 3.5, eyes=t)
        if t == BRAMBLE:
            s.move(HOLLY, a + 1.5, a + 3.5, outline={"look": "swell", "palette": [COL[HOLLY]]})
            s.move(IVY, a + 1.0, a + 3.5, eyes=BRAMBLE)
            continue
        s.move(t, a + 0.6, a + 0.95, eyes="closed")
        s.move(t, a + 0.95, a + 2.6, outline={"look": "swell", "palette": [COL[t]], "params": {"lo": 40}}, mouth="O")
        if t == NOEL:
            s.move(NOEL, a + 0.95, a + 3.4, eyes="rainbow", mouth="AI")
            s.move(JINGLE, a + 1.5, a + 3.0, mouth="O", outline={"look": "swell", "palette": [COL[JINGLE]]})
            s.roll([IVY], a + 2.5, a + 4.5)
    s.move(HOLLY, 21, 25, eyes=BRAMBLE, outline={"look": "glow", "palette": [COL[HOLLY]]})
    s.look_at(21.5, 25, BRAMBLE, [IVY, NOEL, JINGLE, PIP])
    s.giggle(PIP, 26, 1.8)
    s.roll([HOLLY], 28, 30.5)
    out.append(s)

    s = Scene("Bramble won't wake: Holly and Ivy nudge him, then Pip and Jingle from the other side; he opens one eye, and shuts it again",
              S, [sec(999, "spiral", palette=SUNRISE, params={"rotation": 1.0, "movement": 0.8})])
    s.doze(BRAMBLE, 0, 30)
    for k, a in enumerate((4.0, 10.0)):
        for j, t in enumerate((HOLLY, IVY, NOEL, JINGLE)):
            s.move(t, a + 0.4 * j, a + 0.4 * j + 0.9, outline={"look": "swell", "palette": [COL[HOLLY]]}, eyes=BRAMBLE)
        s.move(BRAMBLE, a + 1.7, a + 2.4, outline={"look": "swell", "palette": [COL[BRAMBLE]], "params": {"lo": 10}})
    s.look_at(16, 30, BRAMBLE)
    s.giggle(PIP, 18, 1.6)
    s.giggle(JINGLE, 18.4, 1.6)
    s.move(BRAMBLE, 20, 21, outline={"look": "sparkle", "palette": [COL[PIP], "#FFFFFF"]})
    s.move(BRAMBLE, 30, 34, eyes="wink")
    s.move(BRAMBLE, 34, 38, eyes="closed", mouth="snore",
           outline={"look": "breathe", "palette": [COL[BRAMBLE]], "params": {"lo": 6, "hi": 35, "period": 4.0}})
    s.roll([HOLLY, IVY], 34.5, 37)
    s.move(BRAMBLE, 38, S, eyes="heavy")
    s.yawn(BRAMBLE, 39, 3.2)
    out.append(s)

    s = Scene("Pip's sunrise: a sparkle on Pip spreads up the line in gold and everyone looks up; then Noel warms up, silently",
              S, [sec(999, "rainbow_wash", palette="rainbow")])
    s.move(BRAMBLE, 0, S, eyes="heavy")
    s.move(PIP, 2, 5, outline={"look": "sparkle", "palette": SUNRISE}, eyes="up", mouth="O")
    s.wave(5.0, list(reversed(ALL)), SUNRISE[2], step=0.6, dur=1.8)
    for t in ALL:
        s.move(t, 9, 13, eyes="up")
    s.move(NOEL, 16, 30, outline={"look": "chase", "palette": "rainbow", "params": {"colors": "Rainbow", "per_bar": 1.5}},
           eyes="rainbow")
    for k in range(6):
        s.move(NOEL, 16 + 1.2 * k, 16.6 + 1.2 * k, mouth="AI")
        s.move(NOEL, 16.6 + 1.2 * k, 17.2 + 1.2 * k, mouth="O")
    s.move(NOEL, 23.2, 30, mouth="AI")
    s.look_at(17, 30, NOEL, [HOLLY, IVY, JINGLE, PIP])
    s.roll([HOLLY, IVY], 24, 27)
    s.bounce(JINGLE, 26, 30)
    s.shush(30, NOEL)
    s.move(NOEL, 32.5, 36, eyes="down")
    out.append(s)

    s = Scene("Off to work and school: the trees watch people go past, Jingle bounces at them, everyone stretches up in daylight",
              S, [sec(999, "marquee", palette=DAYLIGHT, params={"speed": 3})])
    s.move(BRAMBLE, 0, S, eyes="heavy")
    s.passer_by(3)
    s.bounce(JINGLE, 8, 13)
    s.move(JINGLE, 8, 13, eyes="down", mouth="O")
    s.passer_by(16, right_to_left=False)
    s.giggle(PIP, 22, 1.6)
    s.wave(26.0, ALL, DAYLIGHT[2], step=0.4, dur=1.6, mouth="AI")
    s.move(HOLLY, 32, 35, eyes="right", mouth="MBP")
    s.passer_by(36)
    out.append(s)

    s = Scene("Ready for the day: everyone hums; Bramble finally wakes properly and the others cheer with a gold wave",
              S, [sec(999, "breathe", palette="rainbow", params={"lo": 35, "hi": 85, "period": 4.0, "stagger": 0.5})])
    s.move(BRAMBLE, 0, 18, eyes="heavy")
    s.hum([HOLLY, IVY, NOEL, JINGLE, PIP], 2, 16)
    s.move(HOLLY, 2, 16, eyes="up")
    s.yawn(BRAMBLE, 16, 3.0)
    s.move(BRAMBLE, 19, 23, eyes="open", outline={"look": "swell", "palette": [SUNRISE[2]], "params": {"lo": 30}}, mouth="O")
    s.look_at(19.5, 23, BRAMBLE)
    s.wave(23.5, [HOLLY, IVY, NOEL, JINGLE, PIP], SUNRISE[2], step=0.4, dur=1.6)
    s.giggle(JINGLE, 27, 1.8)
    s.move(BRAMBLE, 27, S, eyes="open")
    s.passer_by(32, right_to_left=False)
    out.append(s)
    return out


def morning_lights_off() -> Scene:
    """The Morning playlist's lead-out: goodbye waves and winks ("see you tonight"), then the
    trees go out one by one, Holly last. Ends black."""
    s = Scene("Morning lights off: a goodbye wave down the line, a wink each, then off one by one",
              MORNING_OFF_S, [sec(999, "breathe", palette=[SUNRISE[2]], params={"lo": 40, "hi": 75, "period": 4.0})])
    s.wave(0.5, ALL, DAYLIGHT[2], step=0.5, dur=1.6, mouth="etc")
    for k, t in enumerate(ALL):
        s.move(t, 4.5 + 0.3 * k, 6.5 + 0.3 * k, eyes="down")
        s.move(t, 6.5 + 0.3 * k, 7.5 + 0.3 * k, eyes="wink")
    s.yawn(BRAMBLE, 8, 2.0)
    return s


MORNING_OFF_ORDER = {BRAMBLE: 9.5, JINGLE: 10.3, PIP: 11.1, NOEL: 11.9, IVY: 12.7, HOLLY: 13.5}
MORNING_HOURS = 3                # the Morning playlist ends by itself after this, if nobody stops it
MORNING_BRIGHTNESS = 85          # dawn, people walking past: gentler than the evening, brighter than the night


# ------------------------------------------------------------------------------- output ----

def pieces() -> dict[str, dict]:
    """File stem -> arrangement, for every loop sequence."""
    out = {}
    for k, s in enumerate(waiting_scenes(), 1):
        out[f"waiting-{k:02d}"] = s.arrangement(f"{WAITING} {k}")
        out[f"waiting-asleep-{k:02d}"] = s.arrangement(f"{WAITING_ASLEEP} {k}", asleep=[BRAMBLE])
    for k, s in enumerate(night_scenes(), 1):
        out[f"night-{k:02d}"] = s.arrangement(f"{NIGHT} {k}", brightness=NIGHT_BRIGHTNESS)
    for k, s in enumerate(xmas_eve_scenes(), 1):
        out[f"night-christmas-eve-{k:02d}"] = s.arrangement(f"{NIGHT_XMAS_EVE} {k}", asleep=ALL, sleepers_act=True)
    out["lights-out"] = lights_out().arrangement(
        LIGHTS_OUT, brightness=NIGHT_BRIGHTNESS,
        extra={"tree_end": {str(t): v for t, v in LIGHTS_OUT_ORDER.items()}, "end_fade": 1.0})
    for k, s in enumerate(morning_scenes(), 1):
        out[f"morning-{k:02d}"] = s.arrangement(f"{MORNING} {k}", brightness=MORNING_BRIGHTNESS)
    out["morning-lights-off"] = morning_lights_off().arrangement(
        MORNING_OFF, brightness=MORNING_BRIGHTNESS,
        extra={"tree_end": {str(t): v for t, v in MORNING_OFF_ORDER.items()}, "end_fade": 0.8})
    out["lights-out-asleep"] = lights_out_asleep().arrangement(
        LIGHTS_OUT_ASLEEP, asleep=ALL,
        extra={"tree_end": {str(t): 4.0 + k for k, t in enumerate((JINGLE, PIP, NOEL, IVY, BRAMBLE, HOLLY))},
               "end_fade": 1.5})
    return out


def loop_sequences(name: str) -> list[str]:
    """The sequences of one loop playlist, in order (e.g. "Night" -> Night 1 ... Night 8)."""
    count = {WAITING: len(waiting_scenes()), WAITING_ASLEEP: len(waiting_scenes()),
             NIGHT: len(night_scenes()), NIGHT_XMAS_EVE: len(xmas_eve_scenes()), MORNING: len(morning_scenes())}[name]
    return [f"{name} {k}" for k in range(1, count + 1)]


def all_sequences() -> set[str]:
    return {a["sequence"] for a in pieces().values()}


def write() -> dict[str, dict]:
    LOOPS_DIR.mkdir(exist_ok=True)
    arrs = pieces()
    for old in LOOPS_DIR.glob("*.json"):
        if old.stem not in arrs:
            old.unlink()
    for stem, arr in arrs.items():
        (LOOPS_DIR / f"{stem}.json").write_text(json.dumps(arr, indent=2) + "\n", encoding="utf-8", newline="\n")
    return arrs


# ------------------------------------------------------------------------------ xLights ----

def build_in_xlights(arrs: dict[str, dict], only: list[str] | None = None, template: str = "Waiting") -> None:
    """Create each sequence (an animation cloned from the template) if it's missing, open it,
    arrange it and render it. xLights must be running with its API on."""
    from tools import arrange_song, xsq
    show = arrange_song.SHOW_FOLDER
    for stem, arr in arrs.items():
        if only and stem not in only:
            continue
        seq = arr["sequence"]
        path = show / f"{seq}.xsq"
        if not path.exists():
            xsq.clone_animation(show / f"{template}.xsq", path, arr["seconds"])
        r = arrange_song.call({"cmd": "openSequence", "seq": str(path).replace("\\", "/"), "force": "true"})
        if r.get("seq") != seq:
            raise SystemExit(f"opening {seq} gave {r}")
        if int(r["len"]) != int(arr["seconds"] * 1000):
            raise SystemExit(f"{seq} is {r['len']} ms long, the scene is {arr['seconds']} s: delete the .xsq and re-run")
        t0 = time.time()
        arrange_song.main([str(LOOPS_DIR / f"{stem}.json")])
        arrange_song.call({"cmd": "closeSequence", "force": "true"})
        print(f"{seq}: done in {time.time() - t0:.0f}s")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--xlights", action="store_true", help="create, arrange and render the sequences in xLights")
    ap.add_argument("--only", nargs="+", help="with --xlights: just these (file stems, e.g. night-03)")
    args = ap.parse_args(argv)
    arrs = write()
    print(f"wrote {len(arrs)} loop arrangements to {LOOPS_DIR.relative_to(ROOT)}")
    if args.xlights:
        build_in_xlights(arrs, args.only)


if __name__ == "__main__":
    main()
