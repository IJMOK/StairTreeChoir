"""Word-level lyric timing for xLights, from the song audio and its lyrics, using Whisper on the PC.

    python -m tools.lyric_timing "C:/Users/User/Documents/xLights/Audio/song.mp3" \
        --artist "Brenda Lee" --title "Rockin' Around the Christmas Tree"

Writes <track>.json next to the audio (default track name "Choir"). In xLights:
File → Import → Import Timing Track, file type "Eleven Labs (*.json)". It becomes a
timing track named after the file with a phrase layer (one lyric line each) and a
word layer; right-click the track → Breakdown Words to add the phonemes.

The JSON shape is what xLights' ElevenLabs importer reads (SequenceFile::
ProcessElevenLabsTimingFiles in src-core/import_export/TimingImport.cpp, xLights
75c3e11): {"segments": [{"text", "start_time", "end_time", "words": [{"text",
"start_time", "end_time"}]}]}, times in seconds.

With --transcribe (no published lyrics, e.g. a carol recording of unknown origin)
Whisper first transcribes the song, one line per sung phrase, into <audio>.lyrics.txt;
check that file (carols get misheard), fix it if needed and run again without the flag.

Lyrics come from LRCLIB (lrclib.net) unless --lyrics is given, and are saved as
<audio>.lyrics.txt, one sung line per line, plus LRCLIB's line-synced <audio>.lrc.
Lines where the alignment fails (squashed, or >1.5s from the LRC start; e.g. donkey
brays) fall back to the LRC line timing with the words spread evenly. Fix that file and run again: an
existing .lyrics.txt is used instead of downloading. Lyrics stay in the show
folder, never in git.

stable-ts aligns the known text to the audio (forced alignment), which is far more
reliable on singing than transcribing. Run it on the vocal stem if the mix is busy.
Needs requirements-lyrics.txt (CPU PyTorch, stable-ts, PyAV).
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

XLIGHTS_DICTIONARIES = Path(r"C:\Program Files\xLights\dictionaries")
USER_AGENT = "StairTreeChoir lyric_timing (github.com/IJMOK/StairTreeChoir)"
SAMPLE_RATE = 16000
# Characters xLights strips before a dictionary lookup (PhonemeDictionary::BreakdownWord).
XL_STRIP = set("/#~@$%^*,!&-_+=[]{}\":;.<>?`")


def load_audio(path: Path):
    """Decode any audio file to mono 16kHz float32, as Whisper expects."""
    import av
    import numpy as np

    chunks = []
    with av.open(str(path)) as container:
        resampler = av.AudioResampler(format="flt", layout="mono", rate=SAMPLE_RATE)
        for frame in container.decode(audio=0):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
        for out in resampler.resample(None):
            chunks.append(out.to_ndarray().reshape(-1))
    return np.concatenate(chunks).astype("float32")


def lyric_lines(text: str) -> list[str]:
    """Sung lines: LRC timestamps, section tags like [Chorus] and blank lines removed."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\[[^\]]*\]", "", line).strip()
        if line:
            lines.append(line)
    return lines


def fetch_lyrics(artist: str, title: str, duration: float) -> dict:
    """LRCLIB record whose length is closest to the audio (plainLyrics, syncedLyrics)."""
    query = urllib.parse.urlencode({"artist_name": artist, "track_name": title})
    req = urllib.request.Request(f"https://lrclib.net/api/search?{query}",
                                 headers={"User-Agent": USER_AGENT})
    for attempt in range(4):  # LRCLIB sometimes answers 503 for a moment
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                results = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 3:
                raise
            time.sleep(5)
    results = [r for r in results if r.get("plainLyrics") or r.get("syncedLyrics")]
    if not results:
        raise SystemExit(f"LRCLIB has no lyrics for {artist} - {title}; pass --lyrics.")
    best = min(results, key=lambda r: abs((r.get("duration") or 0) - duration))
    print(f"LRCLIB: {best.get('artistName')} - {best.get('trackName')} "
          f"({best.get('duration')}s; audio {duration:.0f}s)")
    return best


def clean_word(word: str) -> str:
    """A word as exported. Brackets mark backing vocals in the line text, but xLights
    doesn't strip them before the dictionary lookup, so they come off the words."""
    return word.strip().replace("(", "").replace(")", "")


def xlights_word_key(word: str) -> str:
    return "".join(c for c in clean_word(word) if c not in XL_STRIP).upper()


def dictionary_words(search_dirs: list[Path]) -> set[str]:
    """Words xLights can break down. Like xLights (xLightsFrame::LoadPhonemeDictionaries),
    each dictionary file is taken from the first directory that has it, show folder first."""
    words = set()
    for name in ("standard_dictionary", "extended_dictionary", "user_dictionary"):
        path = next((d / name for d in search_dirs if (d / name).exists()), None)
        if path is None:
            continue
        for line in path.read_text(encoding="latin-1").splitlines():
            line = line.strip()
            if line and not line.startswith(("##", ";;")) and len(line.split()) > 1:
                words.add(line.split()[0])
    return words


def lrc_starts(synced: str) -> list[float]:
    """Line start times (s) from LRC text, for lines with words."""
    return [int(m) * 60 + float(sec) for m, sec in re.findall(r"^\[(\d+):(\d+(?:\.\d+)?)\]\s*\S", synced, re.M)]


def apply_lrc_fallback(data: dict, starts: list[float], song_end: float,
                       max_shift: float = 1.5, min_len: float = 0.3) -> list[int]:
    """Where alignment failed on a line (squashed, or far from LRCLIB's start), use the LRC
    line start and spread its words evenly. Returns the 1-based lines replaced."""
    segs = data["segments"]
    if len(starts) != len(segs):
        print(f"LRC has {len(starts)} lines, timing has {len(segs)}: no fallback")
        return []
    fixed = []
    for i, seg in enumerate(segs):
        start = starts[i]
        if abs(seg["start_time"] - start) <= max_shift and seg["end_time"] - seg["start_time"] >= min_len:
            continue
        nxt = starts[i + 1] if i + 1 < len(starts) else song_end
        end = min(nxt - 0.05, start + max(0.6, 0.4 * len(seg["words"])))
        step = (end - start) / len(seg["words"])
        for k, w in enumerate(seg["words"]):
            w["start_time"], w["end_time"] = round(start + k * step, 3), round(start + (k + 1) * step, 3)
        seg["start_time"], seg["end_time"] = round(start, 3), round(end, 3)
        fixed.append(i + 1)
    return fixed


def tidy(data: dict, min_word: float = 0.1) -> None:
    """Make the timing safe for xLights' word breakdown: lines don't overlap (a line that
    runs into the next is squeezed to end where it starts), and every word lasts at
    least min_word where its neighbours allow. A word shorter than a frame gets no
    phonemes, so the mouth would hold its last shape through it."""
    segs = data["segments"]
    for a, b in zip(segs, segs[1:]):
        if a["end_time"] > b["start_time"] > a["start_time"]:
            s0, old, new = a["start_time"], a["end_time"], b["start_time"]
            scale = (new - s0) / (old - s0)
            for w in a["words"]:
                w["start_time"] = round(s0 + (w["start_time"] - s0) * scale, 3)
                w["end_time"] = round(s0 + (w["end_time"] - s0) * scale, 3)
            a["end_time"] = new
    for seg in segs:
        words = seg["words"]
        for k, w in enumerate(words):
            if w["end_time"] - w["start_time"] >= min_word:
                continue
            limit = words[k + 1]["start_time"] if k + 1 < len(words) else seg["end_time"]
            w["end_time"] = round(min(w["start_time"] + min_word, max(limit, w["end_time"])), 3)
            if w["end_time"] - w["start_time"] < min_word and k + 1 < len(words):
                nxt = words[k + 1]  # borrow from the next word if it can spare it
                cut = round(w["start_time"] + min_word, 3)
                if nxt["end_time"] - cut >= min_word and nxt["start_time"] <= cut:
                    w["end_time"] = nxt["start_time"] = cut
            if w["end_time"] - w["start_time"] < min_word and k > 0:
                prev = words[k - 1]
                start = max(prev["start_time"] + min_word, w["end_time"] - min_word)
                if start < w["start_time"]:
                    w["start_time"] = round(start, 3)
                    prev["end_time"] = min(prev["end_time"], w["start_time"])
        seg["start_time"] = min(seg["start_time"], words[0]["start_time"])
        seg["end_time"] = max(seg["end_time"], words[-1]["end_time"])


def to_xlights(result) -> dict:
    """stable-ts WhisperResult -> xLights ElevenLabs-import JSON."""
    segments = []
    for seg in result.segments:
        words = [{"text": clean_word(w.word), "start_time": round(w.start, 3), "end_time": round(w.end, 3)}
                 for w in seg.words if clean_word(w.word)]
        if not words:
            continue
        segments.append({"text": seg.text.strip(), "start_time": round(seg.start, 3),
                         "end_time": round(seg.end, 3), "words": words})
    return {"segments": segments}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("audio", type=Path)
    ap.add_argument("--artist", help="for the LRCLIB lyrics search")
    ap.add_argument("--title", help="for the LRCLIB lyrics search")
    ap.add_argument("--lyrics", type=Path, help="lyrics text file, one sung line per line")
    ap.add_argument("--track", default="Choir", help="timing track name (the output file's name)")
    ap.add_argument("--model", default="medium.en", help="Whisper model (small.en is faster)")
    ap.add_argument("--transcribe", action="store_true",
                    help="no published lyrics: transcribe the song into <audio>.lyrics.txt first")
    args = ap.parse_args(argv)

    audio = load_audio(args.audio)
    duration = len(audio) / SAMPLE_RATE
    saved = args.audio.with_suffix(".lyrics.txt")
    lrc = args.audio.with_suffix(".lrc")
    record = None
    if not args.lyrics and (not saved.exists() or not lrc.exists()) and args.artist and args.title:
        record = fetch_lyrics(args.artist, args.title, duration)
        if record.get("syncedLyrics") and not lrc.exists():
            lrc.write_text(record["syncedLyrics"], encoding="utf-8")
    if args.transcribe and not saved.exists():
        import stable_whisper

        print(f"Transcribing {duration:.0f}s with {args.model} on the CPU (no published lyrics)...")
        heard = stable_whisper.load_model(args.model, device="cpu").transcribe(audio, language="en", vad=True)
        phrases = [seg.text.strip() for seg in heard.segments if seg.text.strip()]
        saved.write_text("\n".join(phrases) + "\n", encoding="utf-8")
        print(f"Wrote {saved} ({len(phrases)} lines): check it against the song")
    if args.lyrics:
        text = args.lyrics.read_text(encoding="utf-8-sig")
    elif saved.exists():
        print(f"Using {saved}")
        text = saved.read_text(encoding="utf-8-sig")
    else:
        if not (args.artist and args.title):
            raise SystemExit("Give --artist and --title, --lyrics, or --transcribe.")
        text = record.get("plainLyrics") or record["syncedLyrics"]
    lines = lyric_lines(text)
    saved.write_text("\n".join(lines) + "\n", encoding="utf-8")

    show_folder = args.audio.parent.parent if args.audio.parent.name.lower() == "audio" else args.audio.parent
    known = dictionary_words([show_folder, XLIGHTS_DICTIONARIES])
    unknown = sorted({xlights_word_key(w) for line in lines for w in line.split()} - known - {""})
    if known and unknown:
        print("Not in xLights' dictionaries (add them to user_dictionary in the show folder):",
              ", ".join(unknown))

    import stable_whisper

    print(f"Aligning {len(lines)} lines to {duration:.0f}s of audio with {args.model} on the CPU...")
    model = stable_whisper.load_model(args.model, device="cpu")
    result = model.align(audio, "\n".join(lines), language="en", original_split=True)
    if result is None:
        raise SystemExit("Alignment failed. Try the vocal stem, or check the lyrics match the recording.")

    out = args.audio.with_name(f"{args.track}.json")
    data = to_xlights(result)
    if lrc.exists() and not args.lyrics:
        fixed = apply_lrc_fallback(data, lrc_starts(lrc.read_text(encoding="utf-8")), duration)
        if fixed:
            print("Alignment looked wrong on lines", fixed, "- used LRCLIB's timing there")
    tidy(data)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    n_words = sum(len(s["words"]) for s in data["segments"])
    print(f"Wrote {out}: {len(data['segments'])} phrases, {n_words} words")


if __name__ == "__main__":
    main()
