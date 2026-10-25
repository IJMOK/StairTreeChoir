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
        playlistInfo). A graceful stop (Playlist::StopGracefully) lets the playing entry finish,
        then plays leadOut (SwitchToLeadOut) and goes idle; a hard stop (StopNow) skips leadOut.
        With repeat off, or once loopCount passes are done, the main section ends into leadOut.
        Saved with POST /api/playlist/<name> and Content-Type application/json
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
        A playlist stopped by hand (API, MQTT, a command: forceStop 1) is not restarted by the
        scheduler in the same window (doScheduledPlaylist "just force stopped"), so Home
        Assistant's lights out sticks. At the end of a window the entry's stop type applies
        (Player.cpp: graceful plays the lead-out).
  Files: POST /api/file/Sequences/<name>.fseq and /api/file/Music/<name> (files.php PostFile(),
        config.php GetDirSetting()).

Unverified (no device to test on): see the lists in fpp/README.md and wled/README.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import loops
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
DOW_SATURDAY = 6                         # ScheduleEntry.h INX_SAT
DOW_SUN_TO_FRI = 0x10000 | 0x07E00       # INX_DAY_MASK | every day's bit but INX_DAY_MASK_SATURDAY (0x00100)
STOP_GRACEFUL, STOP_HARD, STOP_AFTER_LOOP = 0, 1, 2
SEASON_START = "2026-12-01"      # Rob to confirm
SEASON_END = "2027-01-01"        # New Year's Day (docs/specials.md)
NYE_WEEK_START = "2026-12-27"    # thank-yous plug New Year's Eve from here
NYE, NYD = "2026-12-31", "2027-01-01"
VILLAGE_WEEK_START = "2026-12-20"   # Sun-Tue thank-yous plug Wednesday's Village Special
VILLAGE_NIGHT, XMAS_EVE, XMAS_DAY = "2026-12-23", "2026-12-24", "2026-12-25"
BETWEEN_PAUSE_S = 4              # "3-5 s of the waiting look" between pieces (show-night.md)
SONG_MEDIA_EXT = ".mp3"          # media file extensions are assumptions: lyrics/beat tools take MP3s,
SKIT_MEDIA_EXT = ".wav"          # tools/skit.py writes WAVs. Change here if the media differ.
GOODNIGHT_MEDIA = "Goodnight.wav"

# Sequence names ("<name>.fseq" in FPP). Songs as given by Rob on 24 Oct 2026.
SONGS = (
    "Rockin Around the Christmas Tree", "Dominick the Donkey", "Feliz Navidad",
    "Little Drummer Boy", "We Wish You a Merry Christmas", "O Come All Ye Faithful",
    "The Virgin Mary Had a Baby Boy", "Twelve Days of Christmas", "Frosty the Snowman",
    # New Year (Rob, 24 Oct 2026)
    "Auld Lang Syne", "Happy New Year", "Here Comes the Sun", "Walking on Sunshine", "What a Wonderful World",
)
GOODNIGHT = "Goodnight"
# The silent loops (tools/loops.py): each playlist plays its short pieces in order, then its lead-out
# when it's stopped gracefully. The playlist names are what Home Assistant stops and watches for.
WAITING = loops.WAITING                 # between shows
WAITING_ASLEEP = loops.WAITING_ASLEEP   # the waiting loop with Bramble asleep (New Year's Eve, before midnight)
NIGHT = loops.NIGHT                     # after the Goodnight until lights out (Home Assistant) or NIGHT_END
NIGHT_XMAS_EVE = loops.NIGHT_XMAS_EVE   # Christmas Eve: everyone asleep for Santa
MORNING = loops.MORNING                 # not scheduled: Home Assistant starts it with the alarm
LEAD_OUT = {WAITING: loops.LIGHTS_OUT, WAITING_ASLEEP: loops.LIGHTS_OUT, NIGHT: loops.LIGHTS_OUT,
            NIGHT_XMAS_EVE: loops.LIGHTS_OUT_ASLEEP, MORNING: loops.MORNING_OFF}
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
NIGHT_END = 23 * 60 + 30                     # backstop: lights out by 23:30 if Home Assistant hasn't
NYE_NIGHT_END = 30                           # New Year's Day 00:30, after the countdown
GOODNIGHT_AT, GOODNIGHT_WINDOW = 21 * 60, 5
SHOW_WINDOW = 30                             # a ~15 minute show is never cut off by its end time
ANNOUNCE_LABELS = ("17", "18", "19", "last")    # skits announce-<label>; "last" = the 20:00 show
ANNOUNCE_WINDOW = 10                         # latest late start of a quarter-hour announcement
# priority order (earlier in schedule.json wins)
CLASS_RANK = {"countdown": 0, "goodnight": 1, "show": 2, "announcement": 3, "waiting_asleep": 4, "night": 5,
              "waiting": 6}

# Thank-you variants by date (docs/specials.md): plain to 26 Dec, plugging New Year's Eve 27-30 Dec,
# "see you at midnight" on the night. Playlist names: letters, numbers, spaces only.
THANKS_VARIANTS = {"": "thank-you", " SAT week": "thank-you-week", " NYE week": "thank-you-nye-week",
                   " NYE": "thank-you-nye-night", " VIL week": "thank-you-vil-week"}

# Saturday Special (docs/specials.md): Saturdays to 26 Dec. 17:00 is a two-song teaser, 18:00 every song.
# Sun-Fri thank-yous plug "this Saturday at six" (" SAT week"); after the special the shows are as usual.
SAT_TEASER = "Show Saturday teaser"
SAT_TEASER_SET = [_TUNING, ("song", "Rockin Around the Christmas Tree"), ("song", "Feliz Navidad"),
                  ("skit", "save-your-voices")]
SAT_SPECIAL = "Saturday Special"
SAT_SPECIAL_SET = [("skit", "special-intro"), ("song", "Rockin Around the Christmas Tree"), ("song", "Feliz Navidad"),
                   ("song", "Dominick the Donkey"), ("song", FROSTY), _SLEEPS, ("song", "Little Drummer Boy"),
                   ("song", "Twelve Days of Christmas"), ("skit", "bramble-wakes-special"),
                   ("song", "O Come All Ye Faithful"), ("song", "The Virgin Mary Had a Baby Boy"),
                   ("song", "We Wish You a Merry Christmas"), ("skit", "thank-you-special")]
SAT_SPECIAL_WINDOW = 35                       # it runs about 29 minutes
SAT_ANNOUNCE = {16: ("Announce 17 Saturday", "announce-17-sat"), 17: ("Announce Special", "announce-special")}

# New Year's Eve (docs/specials.md)
NYE_SHOWS = ((17, "A"), (18, "B"), (19, "C"), (20, "A"), (22, "B"))
NYE_LATE = "Show NYE late"                   # 23:15: Bramble swears he'll stay up, sings, nods off
NYE_LATE_AT = 23 * 60 + 15
NYE_LATE_SET = [("skit", "bramble-staying-up"), ("song", "Rockin Around the Christmas Tree"),
                ("song", "Dominick the Donkey"), ("skit", "bramble-nods-off-nye")]
COUNTDOWN = "Countdown"
COUNTDOWN_AT = 23 * 60 + 59 + 20 / 60        # 23:59:20: the skit says "Ten!" at 30 s, so HAPPY NEW YEAR at 00:00:00
COUNTDOWN_SET = [("skit", "countdown"), ("song", "Auld Lang Syne"), ("skit", "goodnight-newyear")]
NYE_ANNOUNCE_HOURS = range(16, 23)           # :15 :30 :45 from 16:15 to 22:45
# New Year's Day
NYD_SHOW = "Show New Year"
NYD_HOURS = (15, 16, 17, 18, 19)
NYD_WAITING = (14 * 60 + 30, 19 * 60 + 30)
NYD_GOODNIGHT = "Goodnight Season"
NYD_GOODNIGHT_AT = 19 * 60 + 30
NYD_SET = [("skit", "newyear-intro"), ("song", "Happy New Year"), ("song", "Here Comes the Sun"),
           ("song", "Walking on Sunshine"), ("song", "What a Wonderful World"), ("song", "Auld Lang Syne"),
           ("skit", "thank-you-newyear")]


# Village Night (Wed 23 Dec, Rob 24 Oct): the busiest night, the village out before travelling to
# family. Auditions in the 17:00 and 19:00 shows (guest voices from the crowd), the Village Special
# at 18:00 (every song, opening with the phone-call roll-call), the roll-call again at 20:00.
VILLAGE_SPECIAL = "Village Special"
VILLAGE_SPECIAL_SET = ([("skit", "village-special")] + SAT_SPECIAL_SET[1:-1]
                       + [("skit", "thank-you-village-special")])
VILLAGE_ANNOUNCE = {16: ("Announce 17 Village", "announce-17-village"),
                    17: ("Announce Village Special", "announce-village-special")}
# Christmas Eve (Thu 24 Dec): Santa rings the sleigh radio in every show; at 21:00 the choir falls
# asleep one by one so he can come.
XMAS_EVE_GOODNIGHT = "Goodnight Christmas Eve"
SPECIALS = (SAT_SPECIAL, VILLAGE_SPECIAL)     # half-hour blocks: no announcements inside them


def show_variant(letter: str, extra: str | None = None, thanks: str = "thank-you") -> list[tuple[str, str]]:
    """A set with a skit after the tuning-up and its own thank-you."""
    out = []
    for p in SETS[letter]:
        out.append(("skit", thanks) if p == _THANKS else p)
        if p == _TUNING and extra:
            out.append(("skit", extra))
    return out


VILLAGE_SHOWS = {17: ("Show A village", show_variant("A", "auditions", "thank-you-vil-day")),
                 18: (VILLAGE_SPECIAL, VILLAGE_SPECIAL_SET),
                 19: ("Show C village", show_variant("C", "auditions", "thank-you-village")),
                 20: ("Show A village late", show_variant("A", "village-roll-call", "thank-you-village"))}
XMAS_EVE_SHOWS = {h: (f"Show {l} Christmas Eve" + (" last" if h == 20 else ""),
                      show_variant(l, "santa-nearly" if h == 20 else "santa-calls", "thank-you-xmas-eve"))
                  for h, l in zip(SHOW_HOURS, SHOW_SETS)}


def skit_names() -> list[str]:
    return sorted(p.stem for p in SKITS_DIR.glob("*.json"))


def skit_sequence(name: str) -> str:
    return f"Skit {name}"


def known_sequences() -> set[str]:
    return set(SONGS) | {skit_sequence(n) for n in skit_names()} | {GOODNIGHT} | loops.all_sequences()


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


def _playlist(name: str, desc: str, main: list[dict], repeat: int = 0, lead_out: list[dict] = (),
              loop_count: int = 0) -> dict:
    return {
        "name": name, "version": 4, "repeat": repeat, "loopCount": loop_count, "desc": desc, "random": 0,
        "globalPauseBetweenSequencesMS": 0, "empty": False,
        "leadIn": [], "mainPlaylist": main, "leadOut": list(lead_out),
        "playlistInfo": {
            "total_duration": 0, "total_items": len(main) + len(lead_out),
            "leadIn_duration": 0, "leadIn_items": 0,
            "mainPlaylist_duration": 0, "mainPlaylist_items": len(main),
            "leadOut_duration": 0, "leadOut_items": len(lead_out),
        },
    }


def loop_playlist(name: str, desc: str, passes: int = 1) -> dict:
    """A silent loop: its pieces in order (passes times over), then its lead-out on a graceful stop."""
    main = [_entry(seq, None) for _ in range(passes) for seq in loops.loop_sequences(name)]
    return _playlist(name, desc, main, lead_out=[_entry(LEAD_OUT[name], None)], loop_count=1 if passes > 1 else 0)


def morning_passes() -> int:
    """How often the Morning pieces are listed so the playlist runs loops.MORNING_HOURS by itself."""
    import math
    one = len(loops.morning_scenes()) * loops.MORNING_S
    return math.ceil(loops.MORNING_HOURS * 3600 / one)


def announce_playlist_name(label: str) -> str:
    return f"Announce {label}"


def playlists() -> dict[str, dict]:
    """Playlist name -> FPP playlist JSON. The same at every site."""
    out: dict[str, dict] = {}
    out[WAITING] = loop_playlist(WAITING, "Between shows: the choir mucking about. No audio. Lights Out when stopped gracefully.")
    out[NIGHT] = loop_playlist(NIGHT, "After the Goodnight: dozing, yawning, giggling, dim. No audio. "
                                      "Lights Out when stopped gracefully (Home Assistant or the 23:30 backstop).")
    out[NIGHT_XMAS_EVE] = loop_playlist(NIGHT_XMAS_EVE, "Christmas Eve after the Goodnight: all asleep for Santa. "
                                                        "No audio. Fades out when stopped gracefully.")
    # Home Assistant starts it at the alarm and stops it gracefully at the morning lights out. Repeat
    # is off and the pieces are listed for loops.MORNING_HOURS, so it ends by itself (through its lead-out)
    # if the stop never comes; loopCount 1 keeps it to one pass even if it's started with repeat on.
    out[MORNING] = loop_playlist(MORNING, f"Morning, started by Home Assistant: waking up. No audio. Ends by itself "
                                          f"after about {loops.MORNING_HOURS} hours; Morning Lights Off when stopped gracefully.",
                                 morning_passes())
    for label in ANNOUNCE_LABELS:
        seq, entry = _piece("skit", f"announce-{label}")
        n = announce_playlist_name(label)
        out[n] = _playlist(n, "Quarter-hour announcement of the next show.", [entry])
    for suffix, thanks in THANKS_VARIANTS.items():
        for letter, pieces in SETS.items():
            n = f"Show {letter}{suffix}"
            pieces = [("skit", thanks) if p == _THANKS else p for p in pieces]
            out[n] = _set_playlist(n, f"Set {letter}, about 15 minutes; closes with {thanks}.", pieces)
    out[GOODNIGHT] = _playlist(GOODNIGHT, "Goodnight skit; the lights go out.",
                               [_entry(GOODNIGHT, media_for(GOODNIGHT, GOODNIGHT_MEDIA))])
    # New Year's Eve and New Year's Day (docs/specials.md)
    out[WAITING_ASLEEP] = loop_playlist(WAITING_ASLEEP, "Waiting loop with Bramble asleep, until the countdown.")
    for n, skit in (("Announce NYE", "announce-nye"), ("Announce New Year", "announce-newyear")):
        out[n] = _playlist(n, "Quarter-hour announcement.", [_piece("skit", skit)[1]])
    out[NYE_LATE] = _set_playlist(NYE_LATE, "23:15: Bramble is staying up. He isn't.", NYE_LATE_SET)
    out[COUNTDOWN] = _set_playlist(COUNTDOWN, "Midnight: count down, Happy New Year, Auld Lang Syne, goodnight.",
                                   COUNTDOWN_SET, pause=1)
    out[NYD_SHOW] = _set_playlist(NYD_SHOW, "New Year's Day show: New Year songs, no Christmas.", NYD_SET)
    out[NYD_GOODNIGHT] = _set_playlist(NYD_GOODNIGHT, "End of the season; the lights go out.",
                                       [("skit", "goodnight-season")])
    # Saturday Special
    out[SAT_TEASER] = _set_playlist(SAT_TEASER, "Saturday 17:00: two songs, then save your voices for six.", SAT_TEASER_SET)
    out[SAT_SPECIAL] = _set_playlist(SAT_SPECIAL, "Saturday 18:00: every song, about 29 minutes.", SAT_SPECIAL_SET)
    for n, skit in SAT_ANNOUNCE.values():
        out[n] = _playlist(n, "Saturday quarter-hour announcement.", [_piece("skit", skit)[1]])
    # Village Night and Christmas Eve
    for hour, (n, pieces) in VILLAGE_SHOWS.items():
        desc = "23 Dec 18:00: every song for the whole village." if n == VILLAGE_SPECIAL else f"23 Dec {hour}:00."
        out[n] = _set_playlist(n, desc, pieces)
    for n, skit in VILLAGE_ANNOUNCE.values():
        out[n] = _playlist(n, "Village Night quarter-hour announcement.", [_piece("skit", skit)[1]])
    for hour, (n, pieces) in XMAS_EVE_SHOWS.items():
        out[n] = _set_playlist(n, f"Christmas Eve {hour}:00: Santa on the sleigh radio.", pieces)
    out[XMAS_EVE_GOODNIGHT] = _set_playlist(XMAS_EVE_GOODNIGHT, "Christmas Eve: the choir falls asleep for Santa.",
                                            [("skit", "goodnight-christmas-eve")])
    return out


def _set_playlist(name: str, desc: str, pieces, pause: int = BETWEEN_PAUSE_S) -> dict:
    main: list[dict] = []
    for kind, piece in pieces:
        if main:
            main.append({"type": "pause", "enabled": 1, "playOnce": 0, "duration": pause})
        main.append(_piece(kind, piece)[1])
    return _playlist(name, desc, main)


def entries(playlist: dict) -> list[dict]:
    """Every entry the playlist can play, lead-in to lead-out."""
    return [e for sec in ("leadIn", "mainPlaylist", "leadOut") for e in playlist[sec]]


def sequences_used(playlist: dict) -> list[str]:
    return [e["sequenceName"].removesuffix(".fseq") for sec in ("leadIn", "mainPlaylist", "leadOut")
            for e in playlist[sec] if "sequenceName" in e]


# ------------------------------------------------------------------------------------ schedule ----

def _day_before(date: str) -> str:
    import datetime
    return (datetime.date.fromisoformat(date) - datetime.timedelta(days=1)).isoformat()


def _e(playlist: str, cls: str, start: float, end: float, dates: tuple[str, str],
       stop: int = STOP_GRACEFUL, repeat: int = 0, day: int = DOW_EVERY_DAY) -> dict:
    return {"playlist": playlist, "cls": cls, "start": start, "end": end, "dates": dates, "stop": stop,
            "repeat": repeat, "day": day}


def weekdays(day: int) -> set[int]:
    """FPP day code -> the days it covers, 0 = Sunday (ScheduleEntry.h)."""
    if day == DOW_EVERY_DAY:
        return set(range(7))
    if day < 7:
        return {day}
    if day & 0x10000:   # INX_DAY_MASK: Sunday is 0x04000, then one bit lower per day to Saturday 0x00100
        return {d for d in range(7) if day & (0x04000 >> d)}
    raise ValueError(f"day code {day} not used here")


def normal_night(dates: tuple[str, str], suffix: str = "", day: int = DOW_EVERY_DAY,
                 shows: dict[int, str] | None = None, announce: dict[int, tuple[str, str]] | None = None,
                 goodnight: str = GOODNIGHT, night: str = NIGHT) -> list[dict]:
    """show-night.md's night; suffix picks the shows' thank-you variant (THANKS_VARIANTS). shows
    and announce replace the playlist at an hour (the Saturday teaser and special, Village Night)."""
    shows, announce = shows or {}, announce or {}
    plan = [_e(goodnight, "goodnight", GOODNIGHT_AT, GOODNIGHT_AT + GOODNIGHT_WINDOW, dates, day=day)]
    # After the Goodnight (higher priority, so it goes first) the trees doze until Home Assistant's
    # lights out stops this gracefully (Lights Out plays, then dark). Backstop: the window closes at
    # NIGHT_END with a graceful stop, so it's dark within a piece (<= 1 min) plus Lights Out (20 s).
    plan.append(_e(night, "night", GOODNIGHT_AT, NIGHT_END, dates, STOP_GRACEFUL, 1, day=day))
    for hour, letter in zip(SHOW_HOURS, SHOW_SETS):
        window = SAT_SPECIAL_WINDOW if shows.get(hour) in SPECIALS else SHOW_WINDOW
        plan.append(_e(shows.get(hour, f"Show {letter}{suffix}"), "show", hour * 60, hour * 60 + window, dates, day=day))
    # Each hour announces the next show; the 19:xx ones announce the last show (20:00). No
    # announcements after the last show has started.
    for hour, label in zip(range(SHOW_HOURS[0] - 1, SHOW_HOURS[-1]), ANNOUNCE_LABELS):
        name = announce[hour][0] if hour in announce else announce_playlist_name(label)
        for minute in (15, 30, 45):
            t = hour * 60 + minute
            if any(e["playlist"] in SPECIALS and e["start"] <= t < e["end"] for e in plan):
                continue   # during the half-hour special: it would only queue up behind it
            plan.append(_e(name, "announcement", t, t + ANNOUNCE_WINDOW, dates, day=day))
    # The waiting loop is the background: lowest priority, loops, and a hard stop so a show or
    # announcement that pre-empts it starts at once instead of after the current loop.
    plan.append(_e(WAITING, "waiting", WAITING_FROM, WAITING_TO, dates, STOP_HARD, 1, day=day))
    return plan


def nye_night() -> list[dict]:
    """New Year's Eve: shows to 22:00, Bramble's late show, the countdown at midnight."""
    d = (NYE, NYE)
    # The countdown's window closes at 23:59:59, before midnight; "stop after the loop" lets the
    # playlist (countdown, Auld Lang Syne, goodnight) play out past midnight.
    plan = [_e(COUNTDOWN, "countdown", COUNTDOWN_AT, 24 * 60, d, STOP_AFTER_LOOP)]
    for hour, letter in NYE_SHOWS:
        plan.append(_e(f"Show {letter} NYE", "show", hour * 60, hour * 60 + SHOW_WINDOW, d))
    plan.append(_e(NYE_LATE, "show", NYE_LATE_AT, NYE_LATE_AT + SHOW_WINDOW, d))
    for hour in NYE_ANNOUNCE_HOURS:
        for minute in (15, 30, 45):
            t = hour * 60 + minute
            plan.append(_e("Announce NYE", "announcement", t, t + ANNOUNCE_WINDOW, d))
    # After the late show Bramble stays asleep in the waiting loop until the countdown wakes him.
    plan.append(_e(WAITING_ASLEEP, "waiting_asleep", NYE_LATE_AT + 5, COUNTDOWN_AT, d, STOP_HARD, 1))
    plan.append(_e(WAITING, "waiting", WAITING_FROM, COUNTDOWN_AT, d, STOP_HARD, 1))
    return plan


def nyd_night() -> list[dict]:
    """New Year's Day: hourly New Year shows 15:00-19:00, then the season's goodbye."""
    d = (NYD, NYD)
    plan = [_e(NYD_GOODNIGHT, "goodnight", NYD_GOODNIGHT_AT, NYD_GOODNIGHT_AT + GOODNIGHT_WINDOW, d)]
    # Just after midnight, the end of New Year's Eve: once the countdown playlist (which plays on
    # past midnight, "stop after loop") has finished, the trees doze until 00:30. An entry of its own
    # on 1 January, so no entry crosses midnight. Nothing after the season's last Goodnight.
    plan.append(_e(NIGHT, "night", 0, NYE_NIGHT_END, d, STOP_GRACEFUL, 1))
    for hour in NYD_HOURS:
        plan.append(_e(NYD_SHOW, "show", hour * 60, hour * 60 + SHOW_WINDOW, d))
    for hour in NYD_HOURS[:-1]:
        for minute in (15, 30, 45):
            t = hour * 60 + minute
            plan.append(_e("Announce New Year", "announcement", t, t + ANNOUNCE_WINDOW, d))
    plan.append(_e(WAITING, "waiting", *NYD_WAITING, d, STOP_HARD, 1))
    return plan


def schedule_plan() -> list[dict]:
    """Entries in priority order (the file order is the priority, see the module docstring).

    start/end are minutes after midnight (fractions for seconds); end is the latest the entry may
    still be running or start late; dates is the (first, last) day it applies. cls ranks who wins
    an overlap (CLASS_RANK); entries on different dates never meet.
    """
    december = (SEASON_START, _day_before(NYE_WEEK_START))
    plan = (normal_night((SEASON_START, _day_before(VILLAGE_WEEK_START)), " SAT week", DOW_SUN_TO_FRI)
            + normal_night((VILLAGE_WEEK_START, _day_before(VILLAGE_NIGHT)), " VIL week", DOW_SUN_TO_FRI)
            + normal_night((VILLAGE_NIGHT, VILLAGE_NIGHT), shows={h: n for h, (n, _) in VILLAGE_SHOWS.items()},
                           announce=VILLAGE_ANNOUNCE)
            + normal_night((XMAS_EVE, XMAS_EVE), shows={h: n for h, (n, _) in XMAS_EVE_SHOWS.items()},
                           goodnight=XMAS_EVE_GOODNIGHT, night=NIGHT_XMAS_EVE)
            + normal_night((XMAS_DAY, _day_before(NYE_WEEK_START)), " SAT week",
                           DOW_SUN_TO_FRI)
            + normal_night(december, "", DOW_SATURDAY, shows={17: SAT_TEASER, 18: SAT_SPECIAL}, announce=SAT_ANNOUNCE)
            + normal_night((NYE_WEEK_START, _day_before(NYE)), " NYE week")
            + nye_night() + nyd_night())
    return sorted(plan, key=lambda e: CLASS_RANK[e["cls"]])   # stable: keeps time order within a class


def _hms(minutes: float, last_second: bool = False) -> str:
    s = round(minutes * 60) - (1 if last_second else 0)
    return f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}"


def schedule() -> list[dict]:
    """FPP schedule.json. End times are the last second of the window (e.g. 17:29:59)."""
    return [{
        "enabled": 1, "playlist": e["playlist"], "day": e["day"],
        "startTime": _hms(e["start"]), "endTime": _hms(e["end"], last_second=True),
        "repeat": e["repeat"], "startDate": e["dates"][0], "endDate": e["dates"][1],
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
