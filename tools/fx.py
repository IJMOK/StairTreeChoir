"""Effects library for the arrangements: named looks turned into xLights effects.

Settings strings are built from data/xlights-effects.json (tools/xl_keys.py, from the
xLights 2026.18 source), so a misspelt setting fails here, not silently in xLights.

Where effects go (verified by experiment on Rockin', 23 Oct 2026):
- StairTreeN/Outline   per-tree looks. A sub-model's effects override any group effect.
                       Its default buffer is a 59-pixel strip in wiring order (chases run
                       round the tree); buffer="Per Preview" makes it 2D (fire climbs the sides).
- Outlines (group)     whole-choir looks, one picture across all six outlines. Only where no
                       tree has its own outline effect.
- StairTreeN/Eyes      eye moves: the right ring then the left ring, 6 pixels each, clockwise
                       from the top as seen from the front. The Faces effect's own eyes must
                       be off meanwhile, or they show through wherever the eye effect is black.
- Layers: 0 is the top layer. A look may use layers 0 and 1 itself; arrange_song shifts
  them down by one when a section has beat accents.
- Never on Choir (the whole trees): it shows through the Faces effect's black, opening the
  mouths and filling blinking eyes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache

from tools.tree_layout import ROOT

KEYS_FILE = ROOT / "data" / "xlights-effects.json"
RAINBOW = ["#FF0000", "#FF7A00", "#FFE600", "#00E05A", "#0090FF", "#7A00FF"]
CANDY = ["#FF0000", "#FFFFFF"]
XMAS = ["#FF0000", "#00C000", "#FFB000"]
ICE = ["#80E0FF", "#FFFFFF", "#2060FF"]
WHITE = ["#FFFFFF"]
NAMED_PALETTES = {"rainbow": RAINBOW, "candy": CANDY, "xmas": XMAS, "ice": ICE, "white": WHITE}

# xLights effect names as addEffect wants them
EFFECT_NAME = {"ColorWash": "Color Wash", "SingleStrand": "Single Strand"}
# Short names for the shared panels
SHARED = {"buffer": ("Buffer", "BufferStyle"), "brightness": ("Color", "Brightness"),
          "fadein": ("Blending", "Fadein"), "fadeout": ("Blending", "Fadeout"),
          "layer_method": ("Blending", "LayerMethod"), "sparkles": ("Color", "SparkleFrequency"),
          "hue": ("Color", "Color_HueAdjust")}

EYE_POS = {"up": 1, "right": 2, "down": 4, "left": 5}   # Skips start position (1-based) per gaze


@dataclass
class Fx:
    target: str
    effect: str          # library name, e.g. "ColorWash"
    start: int
    end: int
    settings: dict = field(default_factory=dict)
    colours: list = field(default_factory=lambda: list(WHITE))
    layer: int = 0

    def settings_string(self) -> str:
        return build_settings(self.effect, self.settings)

    def palette_string(self) -> str:
        return palette(self.colours)

    @property
    def xl_name(self) -> str:
        return EFFECT_NAME.get(self.effect, self.effect)


@lru_cache(maxsize=1)
def keys() -> dict:
    return json.loads(KEYS_FILE.read_text(encoding="utf-8"))


def _key(entry: dict, pid: str) -> str:
    # Decimal settings (with a divisor) are read back from the text box as a plain decimal.
    if entry.get("divisor") and entry.get("type") == "float":
        return f"E_TEXTCTRL_{pid}"
    return entry["key"]


def _fmt(v) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else f"{v:.1f}"
    return str(v)


def build_settings(effect: str, settings: dict) -> str:
    table = keys()
    eff = table["effects"][effect]
    parts = []
    for name, value in settings.items():
        if name in SHARED:
            panel, pid = SHARED[name]
            parts.append(f"{table['shared'][panel][pid]['key']}={_fmt(value)}")
        elif name.startswith(("E_", "B_", "C_", "T_")):
            parts.append(f"{name}={_fmt(value)}")       # raw key, e.g. E_NOTEBOOK_SSEFFECT_TYPE
        elif name in eff:
            entry = eff[name]
            opts = entry.get("options")
            if opts and value not in opts:
                raise ValueError(f"{effect}.{name}: {value!r} not in {opts}")
            lo, hi = entry.get("min"), entry.get("max")
            div = entry.get("divisor") or 1
            if lo is not None and isinstance(value, (int, float)) and not isinstance(value, bool):
                if not lo / div <= value <= hi / div:
                    raise ValueError(f"{effect}.{name}: {value} outside {lo / div}..{hi / div}")
            parts.append(f"{_key(entry, name)}={_fmt(value)}")
        else:
            raise KeyError(f"{effect} has no setting {name!r}")
    return ",".join(parts)


def palette(colours: list[str]) -> str:
    cols = colours[:8]
    return ",".join(f"C_BUTTON_Palette{i}={c},C_CHECKBOX_Palette{i}=1" for i, c in enumerate(cols, 1))


def colours_for(spec, tree: int | None = None) -> list[str]:
    """A palette by name or list; rainbow turns one step per tree, so hues run across the choir."""
    cols = list(NAMED_PALETTES.get(spec, spec)) if isinstance(spec, str) else list(spec)
    if tree and len(cols) > 1:
        k = (tree - 1) % len(cols)
        cols = cols[k:] + cols[:k]
    return cols


# ---------------------------------------------------------------------------
# Looks. Each takes the window (ms), the beats inside it (ms), the tree (1-6, or
# None on the Outlines group), the palette and the brightness, and returns Fx.

def _bars(beats: list[int]) -> float:
    return max(1.0, len(beats) / 4)


def look_per_tree(name: str, target: str, a: int, b: int, beats: list[int], tree: int,
                  cols: list[str], bright: int, p: dict) -> list[Fx]:
    s = {"brightness": bright} if bright != 100 else {}
    n_bars = _bars(beats)
    if name == "rainbow_wash":
        return [Fx(target, "ColorWash", a, b, {"ColorWash_Cycles": round(min(20.0, n_bars / 2), 1), **s},
                   colours_for("rainbow", tree))]
    if name == "chase":
        return [Fx(target, "SingleStrand", a, b,
                   {"E_NOTEBOOK_SSEFFECT_TYPE": "Chase", "SingleStrand_Colors": p.get("colors", "Rainbow"),
                    "Number_Chases": p.get("chases", 2), "Color_Mix1": p.get("mix", 30),
                    "Chase_Rotations": round(min(50.0, n_bars * p.get("per_bar", 1.0)), 1),
                    "Chase_Type1": p.get("type", "Left-Right"), "Fade_Type": "From Head", **s}, cols)]
    if name == "marquee":
        return [Fx(target, "Marquee", a, b, {"Marquee_Band_Size": p.get("band", 3), "Marquee_Skip_Size": p.get("skip", 2),
                                              "Marquee_Speed": p.get("speed", 6), **s}, cols)]
    if name == "candy":
        return look_per_tree("marquee", target, a, b, beats, tree, CANDY, bright, {"band": 3, "skip": 0, **p})
    if name == "twinkle":
        return [Fx(target, "Twinkle", a, b, {"Twinkle_Count": p.get("count", 80), "Twinkle_Steps": p.get("steps", 40), **s}, cols)]
    if name == "shimmer":
        return [Fx(target, "Shimmer", a, b, {"Shimmer_Duty_Factor": 50, "Shimmer_Cycles": round(min(600.0, len(beats) * 2.0), 1),
                                              "Shimmer_Use_All_Colors": True, **s}, cols)]
    if name == "fire":
        return [Fx(target, "Fire", a, b, {"buffer": "Per Preview", "Fire_Height": p.get("height", 60),
                                           "Fire_HueShift": p.get("hue", 0), **s})]
    if name == "meteors":       # streaks need area: on a thin outline they read as scattered dots
        return [Fx(target, "Meteors", a, b, {"buffer": "Per Preview", "Meteors_Effect": p.get("dir", "Down"),
                                              "Meteors_Type": p.get("type", "Palette"), "Meteors_Count": p.get("count", 12),
                                              "Meteors_Length": 30, "Meteors_Speed": p.get("speed", 20), **s}, cols)]
    if name == "spiral":
        return [Fx(target, "Spirals", a, b, {"buffer": "Per Preview", "Spirals_Count": p.get("count", 2),
                                              "Spirals_Rotation": round(p.get("rotation", 4.0), 1), "Spirals_Thickness": 60,
                                              "Spirals_Movement": round(p.get("movement", 2.0), 1), **s}, cols)]
    if name == "butterfly":
        return [Fx(target, "Butterfly", a, b, {"Butterfly_Colors": "Rainbow", "Butterfly_Style": p.get("style", 1),
                                                "Butterfly_Speed": p.get("speed", 20), **s})]
    if name == "plasma":
        return [Fx(target, "Plasma", a, b, {"buffer": "Per Preview", "Plasma_Color": p.get("color", "Preset Colors 1"),
                                             "Plasma_Speed": p.get("speed", 20), **s}, cols)]
    if name == "snow":
        return [Fx(target, "Snowflakes", a, b, {"buffer": "Per Preview", "Snowflakes_Count": p.get("count", 8),
                                                 "Snowflakes_Speed": p.get("speed", 10), "Falling": "Falling", **s}, colours_for("ice"))]
    if name == "strobe":
        return [Fx(target, "Strobe", a, b, {"Number_Strobes": p.get("count", 6), "Strobe_Duration": 4, **s}, cols)]
    # Character looks (25 Oct 2026): one tree acting on its own, for the loops' "moves".
    if name == "glow":         # a steady colour
        return [Fx(target, "On", a, b, {"Eff_On_Start": 100, "Eff_On_End": 100, **s}, [cols[0]])]
    if name == "off":          # black over whatever the choir look is doing (a tree sulking, lights out)
        return [Fx(target, "On", a, b, {"Eff_On_Start": 100, "Eff_On_End": 100}, ["#000000"])]
    if name in ("breathe", "bounce"):   # slow swell and fade / a quick fidgety bob
        period = int(p.get("period", 4.0 if name == "breathe" else 0.5) * 1000)
        lo, hi = p.get("lo", 15 if name == "breathe" else 35), p.get("hi", 80 if name == "breathe" else 100)
        offset = p.get("offset", 0) + p.get("stagger", 0) * ((tree or 1) - 1)    # stagger: a slow wave down the line
        out, up, x = [], p.get("start_up", True), a + int(offset * 1000) % max(1, period // 2)
        if x > a:
            out.append(Fx(target, "On", a, x, {"Eff_On_Start": hi if up else lo, "Eff_On_End": hi if up else lo, **s},
                          [cols[0]]))
        while x < b:
            y = min(b, x + period // 2)
            if y - x >= 50:
                out.append(Fx(target, "On", x, y, {"Eff_On_Start": lo if up else hi, "Eff_On_End": hi if up else lo, **s},
                              [cols[0]]))
            up, x = not up, y
        return out
    if name == "swell":        # one rise and fall over the window (a wave passing, a nudge landing)
        mid = min(b - 50, max(a + 50, a + (b - a) * p.get("peak", 40) // 100))
        lo = p.get("lo", 20)
        if mid <= a or mid >= b:
            return [Fx(target, "On", a, b, {"Eff_On_Start": 100, "Eff_On_End": lo, **s}, [cols[0]])]
        return [Fx(target, "On", a, mid, {"Eff_On_Start": lo, "Eff_On_End": 100, **s}, [cols[0]]),
                Fx(target, "On", mid, b, {"Eff_On_Start": 100, "Eff_On_End": lo, **s}, [cols[0]])]
    if name in ("sparkle", "ball"):
        # sparkle: glitter all over the tree (a giggle, a snowflake landing); ball: one bright band
        # running round the outline. Both over a dim glow of their first colour on the layer below
        # ("base" %, 0 for none): with Normal blending their black pixels are see-through, so the
        # tree isn't left dark between the twinkles or behind the ball. (Fill was tried for a
        # rising level: it doesn't move without a value curve.)
        if name == "sparkle":
            top = Fx(target, "Twinkle", a, b, {"Twinkle_Count": p.get("count", 45), "Twinkle_Steps": p.get("steps", 16), **s},
                     cols[1:] or cols)
        else:
            top = Fx(target, "Marquee", a, b, {"Marquee_Band_Size": p.get("size", 6), "Marquee_Skip_Size": 59 - p.get("size", 6),
                                                "Marquee_Speed": p.get("speed", 15), **s}, cols)
        base = p.get("base", 45)
        if not base:
            return [top]
        return [top, Fx(target, "On", a, b, {"Eff_On_Start": base, "Eff_On_End": base, **s}, [cols[0]], layer=1)]
    raise KeyError(f"unknown look {name!r}")


def look_choir(name: str, a: int, b: int, beats: list[int], cols: list[str], p: dict) -> list[Fx]:
    """Whole-choir looks on the Outlines group: one picture across all six trees."""
    t = "Outlines"
    pv = {"buffer": "Per Preview"}
    n_bars = _bars(beats)
    if name == "choir_rainbow":       # rainbow bands sweeping across the choir
        return [Fx(t, "Bars", a, b, {**pv, "Bars_BarCount": 2, "Bars_Direction": p.get("dir", "Left"),
                                     "Bars_Cycles": round(min(30.0, n_bars / 2), 1)}, colours_for("rainbow"))]
    if name == "choir_butterfly":
        return [Fx(t, "Butterfly", a, b, {**pv, "Butterfly_Colors": "Rainbow", "Butterfly_Style": p.get("style", 1),
                                          "Butterfly_Speed": p.get("speed", 15)})]
    if name == "choir_meteors":
        return [Fx(t, "Meteors", a, b, {**pv, "Meteors_Effect": p.get("dir", "Down"), "Meteors_Type": p.get("type", "Rainbow"),
                                        "Meteors_Count": 25, "Meteors_Length": 25, "Meteors_Speed": p.get("speed", 20)}, cols)]
    if name == "choir_fire":
        return [Fx(t, "Fire", a, b, {**pv, "Fire_Height": p.get("height", 50), "Fire_HueShift": p.get("hue", 0)})]
    if name == "choir_spiral":
        return [Fx(t, "Spirals", a, b, {**pv, "Spirals_Count": 3, "Spirals_Rotation": 6.0, "Spirals_Thickness": 50,
                                        "Spirals_Movement": 3.0}, cols)]
    if name == "choir_galaxy":
        return [Fx(t, "Galaxy", a, b, {**pv, "Galaxy_Revolutions": 2.0, "Galaxy_Start_Width": 20,
                                       "Galaxy_End_Width": 60, "Galaxy_Duration": 40}, cols)]
    if name == "choir_curtain":
        return [Fx(t, "Curtain", a, b, {**pv, "Curtain_Edge": "center", "Curtain_Effect": p.get("effect", "open"),
                                        "Curtain_Speed": 1.0, "Curtain_Swag": 3}, cols)]
    if name == "choir_snow":
        return [Fx(t, "Snowflakes", a, b, {**pv, "Snowflakes_Count": 25, "Snowflakes_Speed": 10,
                                           "Falling": "Falling"}, colours_for("ice"))]
    if name == "choir_shockwave":      # a ring bursting out from the middle of the choir on every beat
        out = []
        edges = [a] + [x for x in beats if a < x < b] + [b]
        for k in range(len(edges) - 1):
            out.append(Fx(t, "Shockwave", edges[k], edges[k + 1],
                          {**pv, "Shockwave_Start_Radius": 0, "Shockwave_End_Radius": 400, "Shockwave_Start_Width": 40,
                           "Shockwave_End_Width": 120, "Shockwave_Blend_Edges": True},
                          [cols[k % len(cols)]]))
        return out
    raise KeyError(f"unknown choir look {name!r}")


def accents(name: str, target: str, a: int, b: int, beats: list[int], cols: list[str], every: int = 1) -> list[Fx]:
    """Short hits on the beat, on the layer above a look (layer 0; looks go on layer 1)."""
    out = []
    hits = [x for x in beats if a <= x < b][::every]
    for k, x in enumerate(hits):
        end = min(b, x + 250)
        if end - x < 100:
            continue
        if name == "flash":
            out.append(Fx(target, "On", x, end, {"Eff_On_Start": 100, "Eff_On_End": 0, "layer_method": "Max"}, WHITE))
        elif name == "sparkle_hit":
            out.append(Fx(target, "Twinkle", x, end, {"Twinkle_Count": 60, "Twinkle_Steps": 6, "layer_method": "Max"}, WHITE))
        elif name == "colour_hit":
            out.append(Fx(target, "On", x, end, {"Eff_On_Start": 100, "Eff_On_End": 0, "layer_method": "Max"},
                          [cols[k % len(cols)]]))
        else:
            raise KeyError(f"unknown accent {name!r}")
    return out


def eyes(mode: str, tree: int, a: int, b: int, beats: list[int], cols: list[str],
         gaze: list[tuple[int, int, str]] | None = None) -> list[Fx]:
    """Eye moves on StairTreeN/Eyes. Faces must have its eyes off over the same window.

    gaze: (start, end, direction) pieces for "follow" (look at the singers)."""
    t = f"StairTree{tree}/Eyes"
    skips = {"E_NOTEBOOK_SSEFFECT_TYPE": "Skips", "Skips_SkipSize": 5, "Skips_Direction": "Right"}
    if mode == "roll":       # a pupil running round both eyes, one turn per beat
        turns = max(1, len([x for x in beats if a <= x < b]))
        return [Fx(t, "SingleStrand", a, b, {**skips, "Skips_BandSize": 1, "Skips_StartPos": 1,
                                              "Skips_Advance": min(100, turns * 6)}, WHITE)]
    if mode == "rainbow":    # spinning rainbow eyes
        return [Fx(t, "SingleStrand", a, b, {"E_NOTEBOOK_SSEFFECT_TYPE": "Chase", "SingleStrand_Colors": "Rainbow",
                                              "Number_Chases": 2, "Color_Mix1": 50, "Chase_Rotations": 8.0,
                                              "Chase_Group_All": False}, RAINBOW)]
    if mode == "sparkle":
        return [Fx(t, "Twinkle", a, b, {"Twinkle_Count": 50, "Twinkle_Steps": 8}, cols)]
    if mode == "heavy":      # heavy lids: every pixel but the top of each eye, dimmed
        return [Fx(t, "SingleStrand", a, b, {**skips, "Skips_BandSize": 5, "Skips_SkipSize": 1, "Skips_StartPos": 2,
                                              "Skips_Advance": 0, "brightness": 60}, WHITE)]
    if mode == "wink":       # right eye open, left eye shut (its lower half), on two layers
        return [Fx(t, "SingleStrand", a, b, {**skips, "Skips_BandSize": 6, "Skips_SkipSize": 6, "Skips_StartPos": 1,
                                              "Skips_Advance": 0}, WHITE),
                Fx(t, "SingleStrand", a, b, {**skips, "Skips_BandSize": 3, "Skips_SkipSize": 9, "Skips_StartPos": 9,
                                              "Skips_Advance": 0}, WHITE, layer=1)]
    if mode in EYE_POS:      # a plain look in one direction
        return eyes("follow", tree, a, b, beats, cols, [(a, b, mode)])
    if mode == "follow":
        out = []
        for g0, g1, d in gaze or []:
            if g1 - g0 >= 100:
                out.append(Fx(t, "SingleStrand", g0, g1, {**skips, "Skips_BandSize": 2 if d in ("left", "right") else 1,
                                                          "Skips_SkipSize": 4 if d in ("left", "right") else 5,
                                                          "Skips_StartPos": EYE_POS[d], "Skips_Advance": 0}, WHITE))
        return out
    raise KeyError(f"unknown eye mode {mode!r}")
