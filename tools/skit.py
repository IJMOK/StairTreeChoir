"""Turn a skit script into audio, lyric timing and an arrangement, like a song.

    python -m tools.skit data/skits/tuning-up.json [--audio-only]

The script (data/skits/<name>.json) lists who says what. Each line is spoken by that
character's voice (data/voices.json) and the lines are joined with short pauses into
<show>/Audio/Skits/<name>.wav. Two engines (voices.json "engine", or --engine):
- elevenlabs: the character's "elevenlabs" voice via the ElevenLabs API, key from the
  ELEVENLABS_API_KEY environment variable (never in git). Each clip is cached in
  Audio/Skits/cache/ by voice, settings and text, so re-runs cost no credits. With the
  eleven_v3 model a line may carry audio tags such as "[yawns]"; they are left out of
  the lyrics used for lip-sync.
- piper: local and free, the character's Piper model, pitch-shifted.
Then:
- tools.lyric_timing aligns the known text to that audio -> Audio/Skits/<name>.timing.json;
  add it to the sequence as timing track Skit_<name_with_underscores> (tools.xl_timing add
  --name, or import as an "Eleven Labs" timing track, rename it, Breakdown Words);
- data/songs/skit-<name>.json is written: every line goes to its character's tree, so
  tools.arrange_song moves the right mouth, and eyes "follow" makes everyone else look
  at whoever is talking.

Script keys: name, lines [{who, say}], optional look/palette for the outlines and
gap (seconds between lines, default 0.35). A line's "pause" adds silence before it.
A line's "who" may be a list of characters or "Everyone": their voices are mixed, all
their mouths move. A line's "at" (seconds from the start of the audio) starts its voice exactly
then instead of after a gap (the midnight countdown); it may overlap the line before. "sections" replaces the default
single outline section (same keys as a song's, see tools/arrange_song.py). "fade_out" (s)
makes the skit a closer: everything fades over that time and ends dark (end_at/end_fade).
"asleep": [{who, from_line}] sends a character to sleep from the start of that line (1-based)
to the end; [{who, until_line}] has them asleep from the start until just before that line
(arrange_song "asleep": eyes shut, outline breathing).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
import wave
from pathlib import Path

import numpy as np

from tools.arrange_song import SHOW_FOLDER
from tools.tree_layout import ROOT

VOICES_FILE = ROOT / "data" / "voices.json"
VOICE_DIR = SHOW_FOLDER / "Voices"
SKIT_DIR = SHOW_FOLDER / "Audio" / "Skits"
CACHE_DIR = SKIT_DIR / "cache"
RATE = 22050      # Piper medium voices; ElevenLabs is asked for pcm_22050 to match
ELEVEN_API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=pcm_22050"
ELEVEN_MODEL = "eleven_v3"
WAKE_LEAD_S = 0.3  # eyes open this long before a waking character's line
EVERYONE = "Everyone"  # a line the whole cast says together
TAG = re.compile(r"\s*\[[^\]]*\]\s*")


def spoken(text: str) -> str:
    """The words of a line without audio tags: what lip-sync aligns to."""
    return TAG.sub(" ", text).strip()


def speak_eleven(text: str, ch: dict) -> np.ndarray:
    el = ch["elevenlabs"]
    body = {"text": text, "model_id": el.get("model", ELEVEN_MODEL)}
    settings = {k: el[k] for k in ("stability", "similarity_boost", "style", "speed") if k in el}
    if settings:
        body["voice_settings"] = settings
    key = hashlib.sha1(json.dumps([el["voice"], body], sort_keys=True).encode()).hexdigest()[:16]
    clip = CACHE_DIR / f"{key}.pcm"
    if not clip.exists():
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key and os.name == "nt":  # set with setx: not in this process until a restart
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                    api_key = winreg.QueryValueEx(k, "ELEVENLABS_API_KEY")[0]
            except OSError:
                pass
        if not api_key:
            raise SystemExit("ELEVENLABS_API_KEY is not set")
        req = urllib.request.Request(ELEVEN_API.format(voice=el["voice"]), json.dumps(body).encode(),
                                     {"xi-api-key": api_key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            raise SystemExit(f"ElevenLabs {e.code}: {e.read().decode(errors='replace')[:300]}")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        clip.write_bytes(data)
    return np.frombuffer(clip.read_bytes(), dtype=np.int16).astype(np.float32) / 32768


def speak(text: str, ch: dict, cache: dict, engine: str = "piper") -> np.ndarray:
    if engine == "elevenlabs":
        return speak_eleven(text, ch)
    import io

    import librosa
    from piper import PiperVoice, SynthesisConfig

    model = ch["model"]
    if model not in cache:
        cache[model] = PiperVoice.load(str(VOICE_DIR / f"{model}.onnx"))
    voice = cache[model]
    speaker = voice.config.speaker_id_map.get(ch["speaker"]) if ch.get("speaker") else None
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice.synthesize_wav(spoken(text), w, syn_config=SynthesisConfig(speaker_id=speaker, length_scale=ch.get("length", 1.0)))
    buf.seek(0)
    with wave.open(buf, "rb") as w:
        sr = w.getframerate()
        y = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if sr != RATE:
        y = librosa.resample(y, orig_sr=sr, target_sr=RATE)
    if ch.get("pitch"):
        y = librosa.effects.pitch_shift(y, sr=RATE, n_steps=ch["pitch"])
    return y


def fit_to_spans(timing: Path, spans: list[tuple[float, float]], slack: float = 0.15) -> None:
    """Keep each line's words inside the stretch of audio that line really is.

    The skit is built line by line, so where each speaker talks is known exactly.
    Whisper sometimes smears one line over the next (a shout or a gasp, e.g. "Bramble!"
    swallowing "Present!"), or squeezes a line into a sliver of it; then that line's
    words are spread over its own span by length instead, so the right tree's mouth moves."""
    data = json.loads(timing.read_text(encoding="utf-8"))
    for seg, (a, b) in zip(data["segments"], spans):
        words = seg["words"]
        smeared = any(w["start_time"] < a - slack or w["end_time"] > b + slack for w in words)
        squeezed = words[-1]["end_time"] - words[0]["start_time"] < 0.5 * (b - a)  # e.g. a gasp, then one short word
        if smeared or squeezed:
            weights = [max(1, len(w["text"])) for w in words]
            t, per = a, (b - a) / sum(weights)
            for w, k in zip(words, weights):
                w["start_time"], w["end_time"] = round(t, 2), round(t + max(0.1, k * per), 2)
                t += k * per
        seg["start_time"], seg["end_time"] = words[0]["start_time"], words[-1]["end_time"]
    timing.write_text(json.dumps(data, indent=2), encoding="utf-8")


def speakers(who, cast: dict, skit: str = "") -> list[str]:
    """A line's characters: one name, a list of names, or "Everyone"."""
    names = list(cast) if who == EVERYONE else [who] if isinstance(who, str) else list(who)
    for n in names:
        if n not in cast:
            raise SystemExit(f"{skit}: unknown character {n!r}")
    return names


def group_name(who) -> str:
    return who if isinstance(who, str) else "+".join(who)


def build(script: dict, audio_only: bool = False, engine: str | None = None) -> Path:
    voices = json.loads(VOICES_FILE.read_text(encoding="utf-8"))
    cast = voices["characters"]
    engine = engine or voices.get("engine", "piper")
    name = script["name"]
    gap = script.get("gap", 0.35)
    SKIT_DIR.mkdir(parents=True, exist_ok=True)
    cache: dict = {}
    y = np.zeros(int(0.5 * RATE), dtype=np.float32)
    end = len(y)  # where the last line's clip ends; the next line follows a gap after it
    spans = []  # where each line's voice actually is, in seconds: alignment must stay inside it
    for line in script["lines"]:
        names = speakers(line["who"], cast, name)
        clips = [speak(line["say"], cast[n], cache, engine) for n in names]
        clip = np.zeros(max(len(c) for c in clips), dtype=np.float32)
        for c in clips:  # several voices at once ("Everyone"): mixed, levelled with the rest below
            clip[:len(c)] += c / np.sqrt(len(clips))
        loud = np.flatnonzero(np.abs(clip) > 0.02 * max(1e-6, float(np.abs(clip).max())))
        if "at" in line:  # an exact start (the midnight countdown): the voice itself lands on it,
            if len(loud):  # and may overlap the tail of the line before, like a crowd
                clip, loud = clip[loud[0]:], loud - loud[0]
            pos = int(line["at"] * RATE)
        else:
            pos = end + int((gap + line.get("pause", 0)) * RATE)
        if pos + len(clip) > len(y):
            y = np.concatenate([y, np.zeros(pos + len(clip) - len(y), dtype=np.float32)])
        y[pos:pos + len(clip)] += clip
        spans.append(((pos + (loud[0] if len(loud) else 0)) / RATE, (pos + (loud[-1] if len(loud) else len(clip))) / RATE))
        end = max(end, pos + len(clip))
    y = np.concatenate([y[:end], np.zeros(int(1.0 * RATE), dtype=np.float32)])
    y = y / max(1e-6, float(np.abs(y).max())) * 0.9
    wav = SKIT_DIR / f"{name}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(f"wrote {wav} ({len(y) / RATE:.1f}s, {engine})")
    if audio_only:
        return wav

    track = f"Skit_{name.replace('-', '_')}"
    lyrics = wav.with_suffix(".lyrics.txt")
    lyrics.write_text("\n".join(spoken(l["say"]) for l in script["lines"]) + "\n", encoding="utf-8")
    from tools import lyric_timing

    timing = SKIT_DIR / f"{name}.timing.json"
    lyric_timing.main([str(wav), "--lyrics", str(lyrics), "--out", str(timing), "--model", "small.en"])
    fit_to_spans(timing, spans)
    # a steady 120 bpm grid stands in for beats (accents and pulses need one)
    beats = SKIT_DIR / f"{name}.beats.json"
    beats.write_text(json.dumps([round(0.5 * k, 3) for k in range(int(len(y) / RATE * 2))]), encoding="utf-8")

    groups = {group_name(l["who"]): sorted(cast[n]["slot"] for n in speakers(l["who"], cast, name))
              for l in script["lines"]}
    arr = {
        "sequence": f"Skit {name}",
        "audio": f"Audio/Skits/{wav.name}",
        "lyrics_timing": f"Audio/Skits/{timing.name}",
        "lyrics_track": track,
        "beats": f"Audio/Skits/{beats.name}",
        "groups": groups,
        "lines": {str(i): group_name(l["who"]) for i, l in enumerate(script["lines"], 1)},
        "sections": script.get("sections") or [{"name": "skit", "until": 999, "look": script.get("look", "rainbow_wash"),
                                                "palette": script.get("palette", "rainbow"), "eyes": "follow"}],
        "notes": f"Generated by tools/skit.py from data/skits/{name}.json; don't edit, change the script.",
    }
    segs = json.loads(timing.read_text(encoding="utf-8"))["segments"]
    asleep = []
    for s in script.get("asleep", []):
        a = segs[s["from_line"] - 1]["start_time"] if "from_line" in s else None
        b = round(segs[s["until_line"] - 1]["start_time"] - WAKE_LEAD_S, 2) if "until_line" in s else None
        asleep.append({"tree": cast[s["who"]]["slot"], "from": a, "until": b})
    if asleep:
        arr["asleep"] = asleep
    if script.get("fade_out"):  # a closer: dark for the last second of silence, so FPP holds black
        arr["end_at"] = round(len(y) / RATE - 1.0, 1)
        arr["end_fade"] = script["fade_out"]
    out = ROOT / "data" / "songs" / f"skit-{name}.json"
    out.write_text(json.dumps(arr, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return wav


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scripts", type=Path, nargs="+")
    ap.add_argument("--audio-only", action="store_true", help="just the WAV, to listen to")
    ap.add_argument("--engine", choices=["elevenlabs", "piper"], help='override voices.json "engine"')
    args = ap.parse_args(argv)
    for p in args.scripts:
        build(json.loads((ROOT / p).read_text(encoding="utf-8")), args.audio_only, args.engine)


if __name__ == "__main__":
    main()
