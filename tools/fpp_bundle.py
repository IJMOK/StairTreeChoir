"""Gather one site's whole FPP show into a folder laid out like FPP's media directory.

    python -m tools.fpp_bundle site-a                        # -> <show>/FPP/site-a/
    python -m tools.fpp_bundle --all                         # every site in data/sites.json
    python -m tools.fpp_bundle site-a --deploy 192.168.8.20  # bundle, then upload it to that player

The bundle is everything a site's player needs, from the generated config (fpp/<site>/,
tools/gen_site_config.py) and the xLights render output (show folder):
  config/co-universes.json, config/schedule.json   ->  /home/fpp/media/config/
  playlists/<name>.json                             ->  /home/fpp/media/playlists/
  sequences/<name>.fseq                             ->  /home/fpp/media/sequences/
  music/<audio>                                     ->  /home/fpp/media/music/
  show-plan.md                                      the night with real running times
The show plan is also written to docs/show-plan.md, and the public version of it (tools/whats_on.py)
to docs/whats-on.md.
so it can be copied onto the Pi as it is (Samba/SFTP into /home/fpp/media, then restart
FPPD) or uploaded with --deploy, which uses the API calls in fpp/README.md. It stops with
a list if anything a playlist names is missing or a sequence is older than its .xsq
(saved but not rendered).

--deploy worked against Rob's bench Pi 3 (FPP 10.3, 24 Oct 2026): every file, playlist, the
schedule and the outputs arrived and validated. If the player has a UI password, set it in the
FPP_PASSWORD environment variable (sent as HTTP basic auth, user "admin").
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import urllib.parse
import urllib.request
from pathlib import Path

from tools import gen_site_config as cfg
from tools import whats_on
from tools.arrange_song import SHOW_FOLDER
from tools.gen_site_wiring import load_sites
from tools.tree_layout import ROOT

BUNDLE_DIR = SHOW_FOLDER / "FPP"
AUDIO_DIRS = ("Audio/Songs", "Audio/Skits")
PLAN_FILE = ROOT / "docs" / "show-plan.md"
WHATS_ON_FILE = whats_on.OUT_FILE


def fseq_seconds(path: Path) -> float:
    """Length of an FSEQ v2 file from its header (frame count x step ms)."""
    head = path.read_bytes()[:32]
    if head[:4] != b"PSEQ":
        raise SystemExit(f"{path.name} is not an FSEQ file")
    frames = struct.unpack_from("<I", head, 14)[0]
    return frames * head[18] / 1000


def find_audio(name: str) -> Path | None:
    for d in AUDIO_DIRS:
        if (SHOW_FOLDER / d / name).exists():
            return SHOW_FOLDER / d / name
    return None


def site_files(site_id: str) -> tuple[dict[str, dict], list[dict], Path]:
    base = cfg.FPP_DIR / site_id
    if not base.exists():
        raise SystemExit(f"no fpp/{site_id}/: run python -m tools.build first")
    pls = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((base / "playlists").glob("*.json"))}
    return pls, json.loads((base / "schedule.json").read_text(encoding="utf-8")), base


def check(pls: dict[str, dict]) -> tuple[dict[str, Path], dict[str, Path], list[str]]:
    """(sequence files, audio files, problems) for everything the playlists name."""
    seqs, audio, problems = {}, {}, []
    for name, pl in pls.items():
        for e in cfg.entries(pl):
            if e["type"] == "pause":
                continue
            f = SHOW_FOLDER / e["sequenceName"]
            xsq = f.with_suffix(".xsq")
            if not f.exists():
                problems.append(f"{name}: no {e['sequenceName']} (render it in xLights)")
            elif xsq.exists() and xsq.stat().st_mtime > f.stat().st_mtime + 2:
                problems.append(f"{name}: {f.name} is older than its .xsq (render it again)")
            else:
                seqs[e["sequenceName"]] = f
            if e.get("mediaName"):
                a = find_audio(e["mediaName"])
                if a is None:
                    problems.append(f"{name}: no audio {e['mediaName']} in {' or '.join(AUDIO_DIRS)}")
                else:
                    audio[e["mediaName"]] = a
    return seqs, audio, problems


def playlist_seconds(pl: dict, seqs: dict[str, Path], section: str = "mainPlaylist") -> float:
    return sum(e["duration"] if e["type"] == "pause" else fseq_seconds(seqs[e["sequenceName"]])
               for e in pl[section])


def _hmmss(s: float) -> str:
    return f"{int(s // 3600)}:{int(s // 60 % 60):02d}:{int(round(s % 60)):02d}" if s >= 3600 else _mmss(s)


def _mmss(s: float) -> str:
    return f"{int(s // 60)}:{int(round(s % 60)):02d}"


def show_plan(pls: dict[str, dict], schedule: list[dict], seqs: dict[str, Path]) -> str:
    nights: dict[tuple[str, str, int], list[dict]] = {}
    for e in schedule:
        nights.setdefault((e["startDate"], e["endDate"], e["day"]), []).append(e)
    first = min(d[0] for d in nights)
    last = max(d[1] for d in nights)
    day_names = {cfg.DOW_EVERY_DAY: "", cfg.DOW_SATURDAY: ", Saturdays", cfg.DOW_SUN_TO_FRI: ", Sunday to Friday"}
    lines = ["# Show plan", "",
             "Generated by `python -m tools.fpp_bundle` from the FPP playlists and schedule "
             "(tools/gen_site_config.py) and the rendered sequences; don't edit, change those and re-run. "
             "Every site plays the same nights; only its trees differ.", "",
             f"Season: {first} to {last}. Priority when two overlap (fpp/README.md): the countdown, "
             "then goodnights, shows, announcements, the Night loop, and the waiting loop, which comes back by itself "
             "after each. The Night loop runs from the Goodnight until Home Assistant's lights out, or the end of its "
             "window at the latest; either way it stops gracefully: the piece playing ends, then Lights Out. "
             "The Morning loop isn't scheduled: Home Assistant starts it.", ""]
    for (a, b, day), entries in sorted(nights.items()):
        lines += [f"## {a}" + ("" if a == b else f" to {b}") + day_names[day], "",
                  "| Time | Playlist | Runs | Window |", "|---|---|---|---|"]
        for e in sorted(entries, key=lambda e: e["startTime"]):
            run = "loops" if e["repeat"] else _mmss(playlist_seconds(pls[e["playlist"]], seqs))
            lines.append(f"| {e['startTime']} | {e['playlist']} | {run} | to {e['endTime']} |")
        lines.append("")
    lines += ["# Playlists", ""]
    loops_ = {n: pl for n, pl in pls.items() if pl["leadOut"]}
    for name in sorted(pls, key=lambda n: (not n.startswith("Show"), n)):
        pl = pls[name]
        if len(pl["mainPlaylist"]) < 2 or name in loops_:
            continue
        lines += [f"## {name} ({_mmss(playlist_seconds(pl, seqs))})", "", "| Starts | Piece | Length |", "|---|---|---|"]
        t = 0.0
        for e in pl["mainPlaylist"]:
            if e["type"] == "pause":
                t += e["duration"]
                continue
            n = fseq_seconds(seqs[e["sequenceName"]])
            lines.append(f"| {_mmss(t)} | {e['sequenceName'].removesuffix('.fseq')} | {_mmss(n)} |")
            t += n
        lines.append(f"\n{cfg.BETWEEN_PAUSE_S} s pause between pieces.\n")
    lines += ["# Silent loops", "",
              "Short pieces played in order and repeated; a graceful stop lets the piece playing finish, "
              "then plays the lead-out (tools/loops.py).", "",
              "| Playlist | Pieces | One pass | Lead-out | Ends by itself |", "|---|---|---|---|---|"]
    for name, pl in sorted(loops_.items()):
        names = [e["sequenceName"].removesuffix(".fseq") for e in pl["mainPlaylist"]]
        one = list(dict.fromkeys(names))
        passes = len(names) // len(one)
        one_s = sum(fseq_seconds(seqs[f"{n}.fseq"]) for n in one)
        lo = pl["leadOut"][0]["sequenceName"].removesuffix(".fseq")
        ends = (f"after {passes} passes ({_hmmss(playlist_seconds(pl, seqs))}), then {lo}" if passes > 1
                else "no: it loops while its schedule window is open")
        lines.append(f"| {name} | {one[0]} ... {one[-1]} ({len(one)}) | {_mmss(one_s)} | {lo} "
                     f"({_mmss(playlist_seconds(pl, seqs, 'leadOut'))}) | {ends} |")
    lines.append("")
    singles = [(n, pl) for n, pl in pls.items() if len(pl["mainPlaylist"]) == 1 and not pl["leadOut"]]
    lines += ["## Single-piece playlists", "", "| Playlist | Sequence | Length |", "|---|---|---|"]
    for n, pl in sorted(singles):
        e = pl["mainPlaylist"][0]
        lines.append(f"| {n} | {e['sequenceName'].removesuffix('.fseq')} | {_mmss(fseq_seconds(seqs[e['sequenceName']]))} |")
    return "\n".join(lines) + "\n"


def bundle(site_id: str) -> Path:
    pls, schedule, base = site_files(site_id)
    seqs, audio, problems = check(pls)
    if problems:
        raise SystemExit("not bundled:\n  " + "\n  ".join(problems))
    out = BUNDLE_DIR / site_id
    if out.exists():
        shutil.rmtree(out)
    for sub, files in (("config", {"co-universes.json": base / "co-universes.json", "schedule.json": base / "schedule.json"}),
                       ("playlists", {f"{n}.json": base / "playlists" / f"{n}.json" for n in pls}),
                       ("sequences", {n: p for n, p in seqs.items()}),
                       ("music", {n: p for n, p in audio.items()})):
        (out / sub).mkdir(parents=True, exist_ok=True)
        for name, src in files.items():
            shutil.copy2(src, out / sub / name)
    plan = show_plan(pls, schedule, seqs)
    (out / "show-plan.md").write_text(plan, encoding="utf-8")
    PLAN_FILE.write_text(plan, encoding="utf-8", newline="\n")
    scheduled = {e["playlist"] for e in schedule if not e["repeat"]}
    WHATS_ON_FILE.write_text(whats_on.render({n: playlist_seconds(pls[n], seqs) for n in scheduled}),
                             encoding="utf-8", newline="\n")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) / 1e6
    print(f"{site_id}: {len(pls)} playlists, {len(seqs)} sequences, {len(audio)} audio files, {size:.0f} MB -> {out}")
    return out


def _user_env(name: str) -> str | None:
    """A user environment variable; on Windows also read from HKCU when this process predates it."""
    import os
    value = os.environ.get(name)
    if not value and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                value = winreg.QueryValueEx(k, name)[0]
        except OSError:
            pass
    return value


def _auth() -> dict[str, str]:
    """HTTP basic auth for a player with a UI password (FPP's user is "admin"). The password comes
    from the FPP_PASSWORD environment variable (a user variable on Windows), never from git."""
    import base64
    pw = _user_env("FPP_PASSWORD")
    return {"Authorization": "Basic " + base64.b64encode(f"admin:{pw}".encode()).decode()} if pw else {}


def _post(url: str, data: bytes, ctype: str, method: str = "POST") -> str:
    req = urllib.request.Request(url, data, {"Content-Type": ctype, **_auth()}, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read().decode(errors="replace")[:200]


# Home Assistant (M7) at the sites that have one: Site A is at Rob's home. FPP connects out to HA's
# Mosquitto broker (works from behind the site router's NAT) as the HA user stair-tree-choir; the
# password is the FPP_MQTT_PASSWORD user environment variable, never in git. Topics are
# falcon/player/<HostName>/...; the HA side is packages/stair_tree_choir.yaml in Rob's HA repo.
HA_SITES = {"site-a": "192.168.0.100"}
MQTT_USER = "stair-tree-choir"


def mqtt_settings(api: str, broker: str) -> None:
    """Point the player's MQTT client at Home Assistant (applied by the fppd restart that follows)."""
    pw = _user_env("FPP_MQTT_PASSWORD")
    if not pw:
        print("MQTT not set: no FPP_MQTT_PASSWORD (Home Assistant won't see this player)")
        return
    for name, value in (("MQTTHost", broker), ("MQTTPort", "1883"), ("MQTTUsername", MQTT_USER),
                        ("MQTTPassword", pw)):
        _post(f"{api}/settings/{name}", value.encode(), "text/plain", method="PUT")
    print(f"MQTT -> {broker} as {MQTT_USER}")


def deploy(out: Path, host: str, site_id: str = "") -> None:
    """Upload a bundle with the FPP API (fpp/README.md, step 4 and 5)."""
    api = f"http://{host}/api"
    q = urllib.parse.quote
    for f in sorted((out / "sequences").iterdir()):
        _post(f"{api}/file/Sequences/{q(f.name)}", f.read_bytes(), "application/octet-stream")
    for f in sorted((out / "music").iterdir()):
        _post(f"{api}/file/Music/{q(f.name)}", f.read_bytes(), "application/octet-stream")
    _post(f"{api}/channel/output/universeOutputs", (out / "config" / "co-universes.json").read_bytes(), "application/json")
    for f in sorted((out / "playlists").iterdir()):
        _post(f"{api}/playlist/{q(f.stem)}", f.read_bytes(), "application/json")
    _post(f"{api}/schedule", (out / "config" / "schedule.json").read_bytes(), "application/json")
    _post(f"{api}/schedule/reload", b"", "application/json")
    if site_id in HA_SITES:
        mqtt_settings(api, HA_SITES[site_id])
    _post(f"{api}/system/fppd/restart", b"", "application/json")
    print(f"deployed to {host}; check Playlists for warnings (GET {api}/playlists/validate)")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("site", nargs="?", help="site id from data/sites.json, e.g. site-a")
    ap.add_argument("--all", action="store_true", help="bundle every site")
    ap.add_argument("--deploy", metavar="HOST", help="upload the bundle to this FPP player (IP or hostname)")
    args = ap.parse_args(argv)
    sites = [s["id"] for s in load_sites()["sites"]] if args.all else [args.site]
    if not sites[0] or (args.deploy and len(sites) != 1):
        ap.error("give one site (or --all without --deploy)")
    for site in sites:
        out = bundle(site)
        if args.deploy:
            deploy(out, args.deploy, site)


if __name__ == "__main__":
    main()
