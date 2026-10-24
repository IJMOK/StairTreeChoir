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
    assert "Frosty the Snowman" not in {s for pl in pls.values() for s in sc.sequences_used(pl)}


def test_show_sets_follow_show_night():
    pls = sc.playlists()
    seqs = {k: sc.sequences_used(pls[f"Show {k}"]) for k in "ABC"}
    for k in "ABC":
        assert seqs[k][0] == "Skit tuning-up" and seqs[k][-1] == "Skit thank-you"
        songs = [s for s in seqs[k] if s in sc.SONGS]
        assert len(songs) == 4 and len(set(songs)) == 4
    assert [s for s in seqs["B"] if s in sc.SONGS][1] == sc.FROSTY_SUBSTITUTE
    # songs and skits carry audio, the waiting loop does not
    for e in pls["Show A"]["mainPlaylist"]:
        if e["type"] != "pause":
            assert e["type"] == "both" and e["mediaName"]
    assert pls["Waiting"]["mainPlaylist"][0]["type"] == "sequence"


def _span(e):
    return e["start"], e["end"]


def test_schedule_matches_the_running_order():
    plan = sc.schedule_plan()
    shows = [e for e in plan if e["cls"] == "show"]
    assert [(e["start"] // 60, e["playlist"]) for e in shows] == [
        (17, "Show A"), (18, "Show B"), (19, "Show C"), (20, "Show A")]
    ann = [e["start"] for e in plan if e["cls"] == "announcement"]
    assert ann == [h * 60 + m for h in range(16, 21) for m in (15, 30, 45)]
    gn = [e for e in plan if e["cls"] == "goodnight"]
    assert len(gn) == 1 and gn[0]["start"] == 21 * 60
    w = [e for e in plan if e["cls"] == "waiting"]
    assert len(w) == 1 and (w[0]["start"], w[0]["end"]) == (16 * 60, 21 * 60) and w[0]["repeat"] == 1
    assert {e["playlist"] for e in plan} <= set(sc.playlists())


def test_schedule_priority_and_overlaps():
    """FPP gives the entry earlier in the file priority. Entries of the same kind never overlap;
    an overlap between kinds is only allowed where the higher-priority kind is earlier."""
    plan = sc.schedule_plan()
    for i, a in enumerate(plan):
        for j, b in enumerate(plan):
            if j <= i:
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
        assert e["startTime"] < e["endTime"] and e["day"] == 7 and e["stopType"] in (0, 1, 2)


def test_generated_files_are_current_and_secret_free(tmp_path):
    sc.main()
    files = sorted(sc.WLED_DIR.glob("stairtree-*.json")) + sorted(sc.FPP_DIR.glob("site-*/**/*.json"))
    assert len(files) >= 14 + 4 * 12
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
