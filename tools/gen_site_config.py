"""Tree and site configuration from data/sites.json (milestone M5).

Writes
  wled/stairtree-NN.json            one WLED config fragment per tree, POSTed to /json/cfg
  fpp/<site id>/co-universes.json   the site's FPP channel outputs, one DDP output per tree
  fpp/<site id>/playlists/*.json    FPP playlists (waiting loop, announcements, shows, goodnight)
  fpp/<site id>/schedule.json       FPP schedule implementing docs/show-night.md

Every key below was read from source on 24 Oct 2026, not guessed.

WLED v16.0.1 (tag v16.0.1, commit 29b389d), github.com/wled/WLED, wled00/:
  cfg.cpp deserializeConfig()  reads these keys (and serializeConfig() writes the same ones):
    id.mdns   -> cmDNS (mDNS name; getWLEDhostname() in util.cpp prefers it for the DHCP hostname)
    id.name   -> serverDescription
    nw.ins[]  -> multiWiFi[n]: ssid, psk, ip[4], gw[4], sn[4] (static IP is per Wi-Fi entry;
                 psk is read when present and is never written back: serializeConfig() only
                 writes its length as "pskl")
    hw.led.total, hw.led.ins[] -> start, len, pin[], order, rev, skip, type, ref
    if.live.en -> receiveDirect (the "Receive UDP realtime" box; DDP on UDP 4048 is switched on by
                 it, see udp.cpp and wled.cpp ddp.begin(false, DDP_DEFAULT_PORT))
  const.h  TYPE_WS2812_RGB = 22; COL_ORDER_GRB = 0, RGB = 1, BRG = 2, RBG = 3, BGR = 4, GBR = 5
  cfg.cpp  every field is read with CJSON(a, b) = "b | a": a key that is missing keeps the
           device's current value, so a fragment only changes what it names.
  cfg.cpp  end of deserializeConfig(): "rb": true sets doReboot when the config arrives over
           /json/cfg (needed for the static IP to take effect).
  wled_server.cpp  POST /json/cfg -> deserializeConfig(root); a bus change is applied and the
           config saved by the main loop (doInitBusses).
NOT written (left at the device's value): hw.led.maxpwr and per-bus ledma (WLED's brightness
limiter, see wled/README.md: to be rechecked for 12V strings), nw.dns, ap.*, timers, ntp.

FPP 10.3 (tag 10.3, commit da997bd), github.com/FalconChristmas/fpp:
  www/js/fpp.js postUniverseJSON()     the file the UI saves: {"channelOutputs":[{"type":"universes",
        "enabled","interface","threaded","pacingRate","startChannel","channelCount","universes":[...]}]}
        with per-universe active, description, id, startChannel, channelCount, type, universeCount,
        address, priority, syncUniverse, monitor, deDuplicate. Saved with
        POST /api/channel/output/universeOutputs (www/api/controllers/channel.php
        channel_save_output(); file is config/co-universes.json, www/config.php).
  src/channeloutput/UDPOutput.cpp UDPOutput::Init() and UDPOutputData ctor: reads enabled, universes[],
        type, startChannel, channelCount, address, active, description, monitor, deDuplicate.
        Types: 4 = "DDP - Raw Channel Numbers", 5 = "DDP - One Based" (www/js/fpp.js).
  src/channeloutput/DDP.cpp DDPOutputData ctor: the DDP offset of the first packet is
        startChannel-1 for type 4 and 0 for type 5; the data always comes from the sequence at
        startChannel. WLED's first LED is DDP offset 0, so the type is 5.
  Playlists: src/playlist/Playlist.cpp Playlist::Load() (name, desc, repeat, loopCount,
        globalPauseBetweenSequencesMS, playlistInfo, leadIn / mainPlaylist / leadOut);
        www/playlistEntryTypes.json (entry types "both": sequenceName, mediaName, videoOut;
        "sequence": sequenceName; "pause": duration in seconds, outputs keep their last values);
        www/js/fpp.js SavePlaylistAs() (version 4, repeat 0 "currently unused by player", empty,
        playlistInfo). Saved with POST /api/playlist/<name> and Content-Type application/json
        (www/api/controllers/playlist.php playlist_update(); www/api/lib/limonade.php only fills
        the body for application/json). Names: letters, numbers, spaces, hyphens, underscores
        (fpp.js PlaylistNameOK).
  Schedule: src/ScheduleEntry.cpp ScheduleEntry::LoadFromJson() (enabled, playlist, day,
        startTime, endTime, repeat, startDate, endDate, stopType); day 7 = every day
        (ScheduleEntry.h INX_EVERYDAY); repeat 1 = loop the playlist; stopType 0 graceful,
        1 hard, 2 graceful after loop. Saved with POST /api/schedule then POST /api/schedule/reload
        (www/api/controllers/schedule.php). src/Scheduler.cpp: an entry's priority is its index in
        the file (lower index = higher priority); a higher-priority entry starting pre-empts a
        running lower-priority one using the running entry's stop type, and the pre-empted entry
        is restarted afterwards if its window is still open; a lower-priority entry waits while a
        higher-priority one is running and starts when the player is idle if its window is open.
  Files: POST /api/file/Sequences/<name>.fseq and /api/file/Music/<name> (files.php PostFile(),
        config.php GetDirSetting()).

Unverified (no device to test on): see the lists in fpp/README.md and wled/README.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.gen_site_wiring import ip, load_sites
from tools.tree_layout import ROOT

WLED_DIR = ROOT / "wled"
FPP_DIR = ROOT / "fpp"
SKITS_DIR = ROOT / "data" / "skits"

# ---- tree (WLED) ----------------------------------------------------------------------------
PIXELS = 92
DATA_PIN = 16
LED_TYPE_WS281X = 22             # const.h TYPE_WS2812_RGB
COLOR_ORDER = 0                  # const.h COL_ORDER_GRB; TBC at first light (wled/README.md)
GATEWAY = (192, 168, 8, 1)
NETMASK = (255, 255, 255, 0)
SSID_PLACEHOLDER = "CHANGE-ME-SSID"   # tools/wled_apply.py swaps in the real one at provisioning

# ---- site (FPP) -----------------------------------------------------------------------------
CHANNELS_PER_TREE = PIXELS * 3   # 276
DDP_ONE_BASED = 5                # FPP output type "DDP - One Based"
DOW_EVERY_DAY = 7
STOP_GRACEFUL, STOP_HARD = 0, 1
SEASON_START = "2026-12-01"      # Rob to confirm
SEASON_END = "2026-12-31"
BETWEEN_PAUSE_S = 4              # "3-5 s of the waiting look" between pieces (show-night.md)
SONG_MEDIA_EXT = ".mp3"          # media file extensions are assumptions: lyrics/beat tools take MP3s,
SKIT_MEDIA_EXT = ".wav"          # tools/skit.py writes WAVs. Change here if the media differ.
GOODNIGHT_MEDIA = "Goodnight.wav"

# Sequence names ("<name>.fseq" in FPP). Songs as given by Rob on 24 Oct 2026.
SONGS = (
    "Rockin Around the Christmas Tree", "Dominick the Donkey", "Feliz Navidad",
    "Little Drummer Boy", "We Wish You a Merry Christmas", "O Come All Ye Faithful",
    "The Virgin Mary Had a Baby Boy", "Twelve Days of Christmas", "Frosty the Snowman",
)
WAITING, GOODNIGHT = "Waiting", "Goodnight"
FROSTY = "Frosty the Snowman"   # Set B's second song

# show-night.md "A show": (kind, name) with kind "skit" (data/skits/<name>.json) or "song".
# Bramble's story is whole in A and C (Rob, 24 Oct 2026): he nods off, sleeps through the next
# song (its arrangement has him "asleep": Little Drummer Boy, Twelve Days) and is woken after it.
# Those two songs must only ever follow bramble-sleeps.
_THANKS = ("skit", "thank-you")
_TUNING = ("skit", "tuning-up")
_SLEEPS, _WAKES = ("skit", "bramble-sleeps"), ("skit", "bramble-wakes")
SETS = {
    "A": [_TUNING, ("song", "Rockin Around the Christmas Tree"), ("skit", "whos-next"),
          ("song", "Dominick the Donkey"), _SLEEPS, ("song", "Little Drummer Boy"), _WAKES,
          ("song", "We Wish You a Merry Christmas"), _THANKS],
    "B": [_TUNING, ("song", "Feliz Navidad"), ("skit", "pips-joke"),
          ("song", FROSTY), ("skit", "whos-next"),
          ("song", "O Come All Ye Faithful"), ("song", "Rockin Around the Christmas Tree"), _THANKS],
    "C": [_TUNING, ("song", "We Wish You a Merry Christmas"), _SLEEPS,
          ("song", "Twelve Days of Christmas"), _WAKES,
          ("song", "The Virgin Mary Had a Baby Boy"), ("song", "Dominick the Donkey"), _THANKS],
}
SLEEPY_SONGS = ("Little Drummer Boy", "Twelve Days of Christmas")
SHOW_HOURS = (17, 18, 19, 20)
SHOW_SETS = ("A", "B", "C", "A")             # 17:00 A, 18:00 B, 19:00 C, 20:00 A
WAITING_FROM, WAITING_TO = 16 * 60, 21 * 60  # minutes after midnight
GOODNIGHT_AT, GOODNIGHT_WINDOW = 21 * 60, 5
SHOW_WINDOW = 30                             # a ~15 minute show is never cut off by its end time
ANNOUNCE_LABELS = ("17", "18", "19", "last")    # skits announce-<label>; "last" = the 20:00 show
ANNOUNCE_WINDOW = 10                         # latest late start of a quarter-hour announcement
CLASS_RANK = {"goodnight": 0, "show": 1, "announcement": 2, "waiting": 3}   # priority order


def skit_names() -> list[str]:
    return sorted(p.stem for p in SKITS_DIR.glob("*.json"))


def skit_sequence(name: str) -> str:
    return f"Skit {name}"


def known_sequences() -> set[str]:
    return set(SONGS) | {skit_sequence(n) for n in skit_names()} | {WAITING, GOODNIGHT}


# ---------------------------------------------------------------------------- tree configs ----

def wled_config(tree: int, ssid: str = SSID_PLACEHOLDER) -> dict:
    """The fragment POSTed to http://<device>/json/cfg. No Wi-Fi password: wled_apply adds it."""
    name = f"stairtree-{tree:02d}"
    return {
        "rb": True,
        "id": {"mdns": name, "name": name},
        "nw": {"ins": [{
            "ssid": ssid,
            "ip": list(map(int, ip(tree).split("."))),
            "gw": list(GATEWAY),
            "sn": list(NETMASK),
        }]},
        "hw": {"led": {
            "total": PIXELS,
            "ins": [{"start": 0, "len": PIXELS, "pin": [DATA_PIN], "order": COLOR_ORDER,
                     "rev": False, "skip": 0, "type": LED_TYPE_WS281X, "ref": False}],
        }},
        "if": {"live": {"en": True}},
    }


# ------------------------------------------------------------------------------ FPP outputs ----

def slot_start(slot: int) -> int:
    return (slot - 1) * CHANNELS_PER_TREE + 1


def fpp_outputs(site: dict) -> dict:
    universes = []
    for t in site["trees"]:
        universes.append({
            "active": 1,
            "description": f"stairtree-{t['tree']:02d} (slot {t['slot']})",
            "id": 1,
            "startChannel": slot_start(t["slot"]),
            "channelCount": CHANNELS_PER_TREE,
            "type": DDP_ONE_BASED,
            "universeCount": 1,
            "address": ip(t["tree"]),
            "priority": 0,
            "syncUniverse": 0,
            "monitor": 1,
            "deDuplicate": 0,
        })
    return {"channelOutputs": [{
        "type": "universes", "enabled": 1, "interface": "", "threaded": 1, "pacingRate": 90,
        "startChannel": 1, "channelCount": -1, "universes": universes,
    }]}


# ---------------------------------------------------------------------------------- playlists ----

def _entry(sequence: str, media: str | None) -> dict:
    e = {"type": "both" if media else "sequence", "enabled": 1, "playOnce": 0,
         "sequenceName": f"{sequence}.fseq"}
    if media:
        e["mediaName"] = media
        e["videoOut"] = "--Default--"
    return e


def arranged_media() -> dict[str, str]:
    """Sequence name -> its audio file name, from the arrangements (data/songs/*.json).

    FPP plays the media by file name, so it must be the real file (e.g. the song's MP3 as
    downloaded), uploaded to FPP's music folder under that name."""
    out = {}
    for p in sorted((ROOT / "data" / "songs").glob("*.json")):
        arr = json.loads(p.read_text(encoding="utf-8"))
        if arr.get("sequence") and arr.get("audio"):
            out[arr["sequence"]] = Path(arr["audio"]).name
    return out


def media_for(seq: str, fallback: str) -> str:
    """The arranged audio file, else a placeholder (tests flag placeholders as unfinished)."""
    return arranged_media().get(seq, fallback)


def _piece(kind: str, name: str) -> tuple[str, dict]:
    """(sequence name, playlist entry) for one song or skit."""
    if kind == "song":
        return name, _entry(name, media_for(name, name + SONG_MEDIA_EXT))
    seq = skit_sequence(name)
    return seq, _entry(seq, media_for(seq, seq + SKIT_MEDIA_EXT))


def _playlist(name: str, desc: str, main: list[dict], repeat: int = 0) -> dict:
    return {
        "name": name, "version": 4, "repeat": repeat, "loopCount": 0, "desc": desc, "random": 0,
        "globalPauseBetweenSequencesMS": 0, "empty": False,
        "leadIn": [], "mainPlaylist": main, "leadOut": [],
        "playlistInfo": {
            "total_duration": 0, "total_items": len(main),
            "leadIn_duration": 0, "leadIn_items": 0,
            "mainPlaylist_duration": 0, "mainPlaylist_items": len(main),
            "leadOut_duration": 0, "leadOut_items": 0,
        },
    }


def announce_playlist_name(label: str) -> str:
    return f"Announce {label}"


def playlists() -> dict[str, dict]:
    """Playlist name -> FPP playlist JSON. The same at every site."""
    out: dict[str, dict] = {}
    out[WAITING] = _playlist(WAITING, "Waiting loop: rainbow, blinking, glancing. No audio.",
                             [_entry(WAITING, None)])
    for label in ANNOUNCE_LABELS:
        seq, entry = _piece("skit", f"announce-{label}")
        n = announce_playlist_name(label)
        out[n] = _playlist(n, "Quarter-hour announcement of the next show.", [entry])
    for letter, pieces in SETS.items():
        main: list[dict] = []
        for kind, name in pieces:
            if main:
                main.append({"type": "pause", "enabled": 1, "playOnce": 0, "duration": BETWEEN_PAUSE_S})
            main.append(_piece(kind, name)[1])
        n = f"Show {letter}"
        out[n] = _playlist(n, f"Set {letter}, about 15 minutes.", main)
    out[GOODNIGHT] = _playlist(GOODNIGHT, "Goodnight skit; the lights go out.",
                               [_entry(GOODNIGHT, media_for(GOODNIGHT, GOODNIGHT_MEDIA))])
    return out


def sequences_used(playlist: dict) -> list[str]:
    return [e["sequenceName"].removesuffix(".fseq") for sec in ("leadIn", "mainPlaylist", "leadOut")
            for e in playlist[sec] if "sequenceName" in e]


# ------------------------------------------------------------------------------------ schedule ----

def schedule_plan() -> list[dict]:
    """Entries in priority order (the file order is the priority, see the module docstring).

    start/end are minutes after midnight; end is the latest the entry may still be running or
    start late. cls ranks who wins an overlap (CLASS_RANK).
    """
    plan = [{"playlist": GOODNIGHT, "cls": "goodnight", "start": GOODNIGHT_AT,
             "end": GOODNIGHT_AT + GOODNIGHT_WINDOW, "stop": STOP_GRACEFUL, "repeat": 0}]
    for hour, letter in zip(SHOW_HOURS, SHOW_SETS):
        plan.append({"playlist": f"Show {letter}", "cls": "show", "start": hour * 60,
                     "end": hour * 60 + SHOW_WINDOW, "stop": STOP_GRACEFUL, "repeat": 0})
    # Each hour announces the next show; the 19:xx ones announce the last show (20:00). No
    # announcements after the last show has started.
    for hour, label in zip(range(SHOW_HOURS[0] - 1, SHOW_HOURS[-1]), ANNOUNCE_LABELS):
        for minute in (15, 30, 45):
            plan.append({"playlist": announce_playlist_name(label), "cls": "announcement",
                         "start": hour * 60 + minute, "end": hour * 60 + minute + ANNOUNCE_WINDOW,
                         "stop": STOP_GRACEFUL, "repeat": 0})
    # The waiting loop is the background: lowest priority, loops, and a hard stop so a show or
    # announcement that pre-empts it starts at once instead of after the current loop.
    plan.append({"playlist": WAITING, "cls": "waiting", "start": WAITING_FROM, "end": WAITING_TO,
                 "stop": STOP_HARD, "repeat": 1})
    return plan


def _hms(minutes: int, last_second: bool = False) -> str:
    if last_second:
        minutes -= 1
        return f"{minutes // 60:02d}:{minutes % 60:02d}:59"
    return f"{minutes // 60:02d}:{minutes % 60:02d}:00"


def schedule() -> list[dict]:
    """FPP schedule.json. End times are the last second of the window (e.g. 17:29:59)."""
    return [{
        "enabled": 1, "playlist": e["playlist"], "day": DOW_EVERY_DAY,
        "startTime": _hms(e["start"]), "endTime": _hms(e["end"], last_second=True),
        "repeat": e["repeat"], "startDate": SEASON_START, "endDate": SEASON_END,
        "stopType": e["stop"],
    } for e in schedule_plan()]


# --------------------------------------------------------------------------------------- main ----

def _dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    sites = load_sites()["sites"]
    trees = sorted(t["tree"] for s in sites for t in s["trees"])
    for tree in trees:
        _dump(WLED_DIR / f"stairtree-{tree:02d}.json", wled_config(tree))
    pls = playlists()
    for site in sites:
        base = FPP_DIR / site["id"]
        _dump(base / "co-universes.json", fpp_outputs(site))
        for old in (base / "playlists").glob("*.json"):     # playlists no longer generated
            if old.stem not in pls:
                old.unlink()
        for name, pl in pls.items():
            _dump(base / "playlists" / f"{name}.json", pl)
        _dump(base / "schedule.json", schedule())
    print(f"wrote {len(trees)} WLED configs and {len(sites)} FPP site configs")


if __name__ == "__main__":
    main()
