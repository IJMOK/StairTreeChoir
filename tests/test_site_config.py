import json
import re

import pytest

from tools import gen_site_config as sc
from tools import wled_apply
from tools.gen_site_wiring import load_sites


def sites():
    return load_sites()["sites"]


def test_slot_start_channels():
    assert [sc.slot_start(s) for s in range(1, 7)] == [1, 277, 553, 829, 1105, 1381]


def test_every_site_outputs_cover_its_trees_in_slot_order():
    for site in sites():
        outs = sc.fpp_outputs(site)["channelOutputs"][0]["universes"]
        assert len(outs) == len(site["trees"])
        for out, t in zip(outs, site["trees"]):
            assert out["address"] == f"192.168.8.{100 + t['tree']}"
            assert out["startChannel"] == (t["slot"] - 1) * 276 + 1
            assert out["channelCount"] == 276
            assert out["type"] == 5            # DDP - One Based: WLED wants DDP offset 0
            assert out["active"] == 1
        # outputs tile the channel space without a gap or overlap
        edge = 1
        for out in outs:
            assert out["startChannel"] == edge
            edge += out["channelCount"]


def test_ips_and_hostnames_unique_across_all_sites():
    ips = [u["address"] for s in sites() for u in sc.fpp_outputs(s)["channelOutputs"][0]["universes"]]
    assert len(ips) == 14 == len(set(ips))
    cfgs = [sc.wled_config(t["tree"]) for s in sites() for t in s["trees"]]
    assert len({tuple(c["nw"]["ins"][0]["ip"]) for c in cfgs}) == 14
    assert len({c["id"]["mdns"] for c in cfgs}) == 14


def test_wled_config_content():
    c = sc.wled_config(7)
    assert c["id"]["mdns"] == "stairtree-07"
    w = c["nw"]["ins"][0]
    assert w["ip"] == [192, 168, 8, 107] and w["gw"] == [192, 168, 8, 1] and w["sn"] == [255, 255, 255, 0]
    led = c["hw"]["led"]["ins"][0]
    assert (led["start"], led["len"], led["pin"], led["type"]) == (0, 92, [16], 22)
    assert c["hw"]["led"]["total"] == 92
    assert c["if"]["live"]["en"] is True


def test_wled_apply_adds_credentials_only_in_memory():
    cfg = wled_apply.build(5, "HomeNet", "s3cret")
    assert cfg["nw"]["ins"][0]["psk"] == "s3cret" and cfg["nw"]["ins"][0]["ssid"] == "HomeNet"
    assert sc.wled_config(5)["nw"]["ins"][0]["ssid"] == sc.SSID_PLACEHOLDER


def test_playlists_reference_only_known_sequences():
    known = sc.known_sequences()
    pls = sc.playlists()
    for name, pl in pls.items():
        assert re.fullmatch(r"[-a-zA-Z0-9_ ]+", name)       # FPP playlist name rule
        used = sc.sequences_used(pl)
        assert used, name
        assert set(used) <= known, (name, set(used) - known)
        assert pl["playlistInfo"]["total_items"] == len(pl["mainPlaylist"])
    assert "Frosty the Snowman" in sc.sequences_used(pls["Show B"])


def test_show_sets_follow_show_night():
    pls = sc.playlists()
    seqs = {k: sc.sequences_used(pls[f"Show {k}"]) for k in "ABC"}
    for k in "ABC":
        assert seqs[k][0] == "Skit tuning-up" and seqs[k][-1] == "Skit thank-you"
        songs = [s for s in seqs[k] if s in sc.SONGS]
        assert len(songs) == 4 and len(set(songs)) == 4
    assert [s for s in seqs["B"] if s in sc.SONGS][1] == sc.FROSTY
    # Bramble's story, in every playlist: sleepy songs (one or more in a row) only right after he
    # nods off, and he's woken right after them
    for name, pl in pls.items():
        s = sc.sequences_used(pl)
        i = 0
        while i < len(s):
            if s[i] in sc.SLEEPY_SONGS:
                j = i
                while j < len(s) and s[j] in sc.SLEEPY_SONGS:
                    j += 1
                assert s[i - 1] == "Skit bramble-sleeps" and s[j].startswith("Skit bramble-wakes"), name
                i = j
            i += 1
        assert s.count("Skit bramble-sleeps") == sum(x.startswith("Skit bramble-wakes") for x in s), name
    # songs and skits carry audio, the waiting loop does not
    for e in pls["Show A"]["mainPlaylist"]:
        if e["type"] != "pause":
            assert e["type"] == "both" and e["mediaName"]
    assert pls["Waiting"]["mainPlaylist"][0]["type"] == "sequence"


def _span(e):
    return e["start"], e["end"]


def _on(dates, day=None):
    return [e for e in sc.schedule_plan() if e["dates"] == dates and (day is None or e["day"] == day)]


DECEMBER = (sc.SEASON_START, "2026-12-26")


def test_schedule_matches_the_running_order():
    for dates, suffix, day in ((DECEMBER, " SAT week", sc.DOW_SUN_TO_FRI), (("2026-12-27", "2026-12-30"), " NYE week", 7)):
        plan = _on(dates, day)
        shows = [e for e in plan if e["cls"] == "show"]
        assert [(e["start"] // 60, e["playlist"]) for e in shows] == [
            (17, f"Show A{suffix}"), (18, f"Show B{suffix}"), (19, f"Show C{suffix}"), (20, f"Show A{suffix}")]
        ann = [e["start"] for e in plan if e["cls"] == "announcement"]
        assert ann == [h * 60 + m for h in range(16, 20) for m in (15, 30, 45)]   # none after the 20:00 show
        gn = [e for e in plan if e["cls"] == "goodnight"]
        assert len(gn) == 1 and gn[0]["start"] == 21 * 60
        w = [e for e in plan if e["cls"] == "waiting"]
        assert len(w) == 1 and (w[0]["start"], w[0]["end"]) == (16 * 60, 21 * 60) and w[0]["repeat"] == 1
    assert {e["playlist"] for e in sc.schedule_plan()} <= set(sc.playlists())


def test_every_night_of_the_season_is_covered_once():
    import datetime
    days = {}
    for e in sc.schedule_plan():
        a, b = (datetime.date.fromisoformat(x) for x in e["dates"])
        for k in range((b - a).days + 1):
            d = a + datetime.timedelta(days=k)
            if (d.weekday() + 1) % 7 in sc.weekdays(e["day"]):   # FPP counts from Sunday = 0
                days.setdefault(d, set()).add((e["dates"], e["day"]))
    first, last = (datetime.date.fromisoformat(x) for x in (sc.SEASON_START, sc.SEASON_END))
    assert sorted(days) == [first + datetime.timedelta(days=k) for k in range((last - first).days + 1)]
    assert all(len(v) == 1 for v in days.values())   # one kind of night per date


def test_fpp_day_codes():
    assert sc.weekdays(sc.DOW_SUN_TO_FRI) == {0, 1, 2, 3, 4, 5}
    assert sc.weekdays(sc.DOW_SATURDAY) == {6}
    assert sc.DOW_SUN_TO_FRI == 0x17E00


def test_saturday_special():
    plan = _on(DECEMBER, sc.DOW_SATURDAY)
    shows = {sc._hms(e["start"])[:5]: e["playlist"] for e in plan if e["cls"] == "show"}
    assert shows == {"17:00": sc.SAT_TEASER, "18:00": sc.SAT_SPECIAL, "19:00": "Show C", "20:00": "Show A"}
    ann = {sc._hms(e["start"])[:5]: e["playlist"] for e in plan if e["cls"] == "announcement"}
    assert ann["16:15"] == "Announce 17 Saturday" and ann["17:45"] == "Announce Special"
    assert "18:15" not in ann and "18:30" not in ann and ann["18:45"] == "Announce 19"
    pls = sc.playlists()
    special = [s for s in sc.sequences_used(pls[sc.SAT_SPECIAL]) if s in sc.SONGS]
    assert sorted(special) == sorted(sc.SONGS[:9])                     # every Christmas song, once
    teaser = [s for s in sc.sequences_used(pls[sc.SAT_TEASER]) if s in sc.SONGS]
    assert len(teaser) == 2 and sc.sequences_used(pls[sc.SAT_TEASER])[-1] == "Skit save-your-voices"
    weekday_shows = {e["playlist"] for e in _on(DECEMBER, sc.DOW_SUN_TO_FRI) if e["cls"] == "show"}
    assert all(sc.sequences_used(pls[p])[-1] == "Skit thank-you-week" for p in weekday_shows)


def test_new_years_eve():
    plan = _on((sc.NYE, sc.NYE))
    cd = [e for e in plan if e["cls"] == "countdown"]
    assert len(cd) == 1 and sc.schedule_plan().index(cd[0]) == 0           # beats everything
    assert sc._hms(cd[0]["start"]) == "23:59:20" and cd[0]["stop"] == sc.STOP_AFTER_LOOP
    assert sc._hms(cd[0]["end"], last_second=True) == "23:59:59"           # no entry crosses midnight
    assert not [e for e in plan if e["playlist"] == sc.GOODNIGHT]          # no 21:00 goodnight tonight
    assert [sc._hms(e["start"])[:5] for e in plan if e["cls"] == "show"] == ["17:00", "18:00", "19:00", "20:00", "22:00", "23:15"]
    assert all(e["playlist"].endswith(" NYE") or e["playlist"] == sc.NYE_LATE for e in plan if e["cls"] == "show")
    asleep = [e for e in plan if e["cls"] == "waiting_asleep"]
    assert len(asleep) == 1 and asleep[0]["end"] == cd[0]["start"]
    assert sc.sequences_used(sc.playlists()[sc.COUNTDOWN])[:2] == ["Skit countdown", "Auld Lang Syne"]


def test_new_years_day():
    plan = _on((sc.NYD, sc.NYD))
    assert [e["start"] // 60 for e in plan if e["cls"] == "show"] == [15, 16, 17, 18, 19]
    assert {e["playlist"] for e in plan if e["cls"] == "show"} == {sc.NYD_SHOW}
    gn = [e for e in plan if e["cls"] == "goodnight"]
    assert len(gn) == 1 and gn[0]["playlist"] == sc.NYD_GOODNIGHT
    christmas = set(sc.SONGS[:9])
    assert not christmas & set(sc.sequences_used(sc.playlists()[sc.NYD_SHOW]))


def test_schedule_priority_and_overlaps():
    """FPP gives the entry earlier in the file priority. Entries of the same kind never overlap;
    an overlap between kinds is only allowed where the higher-priority kind is earlier.
    Entries on different dates never meet."""
    plan = sc.schedule_plan()
    for i, a in enumerate(plan):
        for j, b in enumerate(plan):
            if j <= i or not (a["dates"][0] <= b["dates"][1] and b["dates"][0] <= a["dates"][1]):
                continue
            if not sc.weekdays(a["day"]) & sc.weekdays(b["day"]):
                continue
            overlap = a["start"] < b["end"] and b["start"] < a["end"]
            if a["cls"] == b["cls"] and a["cls"] != "waiting":
                assert not overlap, (a, b)
            if overlap:
                assert sc.CLASS_RANK[a["cls"]] < sc.CLASS_RANK[b["cls"]], (a, b)
    assert plan[-1]["cls"] == "waiting"      # the background loop is the lowest priority


def test_schedule_json_shape():
    for e in sc.schedule():
        assert set(e) == {"enabled", "playlist", "day", "startTime", "endTime", "repeat",
                          "startDate", "endDate", "stopType"}
        assert re.fullmatch(r"\d\d:\d\d:\d\d", e["startTime"]) and re.fullmatch(r"\d\d:\d\d:\d\d", e["endTime"])
        assert e["startTime"] < e["endTime"] and e["day"] in (7, sc.DOW_SATURDAY, sc.DOW_SUN_TO_FRI) and e["stopType"] in (0, 1, 2)


def test_generated_files_are_current_and_secret_free(tmp_path):
    sc.main()
    files = sorted(sc.WLED_DIR.glob("stairtree-*.json")) + sorted(sc.FPP_DIR.glob("site-*/**/*.json"))
    assert len(files) >= 14 + 4 * 11
    for f in files:
        text = f.read_text(encoding="utf-8")
        json.loads(text)
        assert not re.search(r'"(psk|pass|password|apsk|key|token)"', text, re.I), f
    for tree in range(1, 15):
        c = json.loads((sc.WLED_DIR / f"stairtree-{tree:02d}.json").read_text(encoding="utf-8"))
        assert c == sc.wled_config(tree)
        assert "psk" not in c["nw"]["ins"][0]
    # every site got the same playlists and schedule
    for site in sites():
        base = sc.FPP_DIR / site["id"]
        assert json.loads((base / "schedule.json").read_text(encoding="utf-8")) == sc.schedule()
        assert {p.stem for p in (base / "playlists").glob("*.json")} == set(sc.playlists())


def test_playlist_media_are_the_arranged_audio_files():
    """Every song/skit in a playlist plays its arrangement's real audio file (data/songs/*.json)."""
    media = sc.arranged_media()
    missing = sorted({s for pl in sc.playlists().values() for s in sc.sequences_used(pl)} - set(media) - {sc.WAITING, sc.WAITING_ASLEEP})
    for pl in sc.playlists().values():
        for e in pl["mainPlaylist"]:
            seq = e.get("sequenceName", "").removesuffix(".fseq")
            if "mediaName" in e and seq in media:
                assert e["mediaName"] == media[seq]
    assert not missing, f"not arranged yet: {missing}"
