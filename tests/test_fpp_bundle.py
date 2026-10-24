"""tools/fpp_bundle.py against a fake show folder: what it copies, what it refuses, the plan."""

import struct

import pytest

from tools import fpp_bundle, gen_site_config as cfg


def fake_fseq(path, seconds, step_ms=50):
    head = bytearray(32)
    head[:4] = b"PSEQ"
    head[7] = 2
    struct.pack_into("<II", head, 10, 276, int(seconds * 1000 / step_ms))
    head[18] = step_ms
    path.write_bytes(bytes(head))


@pytest.fixture
def show(tmp_path, monkeypatch):
    monkeypatch.setattr(fpp_bundle, "SHOW_FOLDER", tmp_path)
    monkeypatch.setattr(fpp_bundle, "BUNDLE_DIR", tmp_path / "FPP")
    monkeypatch.setattr(fpp_bundle, "PLAN_FILE", tmp_path / "show-plan.md")
    for d in fpp_bundle.AUDIO_DIRS:
        (tmp_path / d).mkdir(parents=True)
    pls, _, _ = fpp_bundle.site_files("site-a")
    for pl in pls.values():
        for e in pl["mainPlaylist"]:
            if e["type"] != "pause":
                fake_fseq(tmp_path / e["sequenceName"], 60)
                if e.get("mediaName"):
                    (tmp_path / "Audio/Songs" / e["mediaName"]).write_bytes(b"x")
    return tmp_path


def test_bundle_lays_out_fpp_media(show):
    out = fpp_bundle.bundle("site-a")
    assert (out / "config" / "schedule.json").exists()
    assert (out / "config" / "co-universes.json").exists()
    assert (out / "playlists" / "Show A.json").exists()
    assert (out / "sequences" / "Waiting.fseq").exists()
    assert any((out / "music").iterdir())
    plan = (out / "show-plan.md").read_text(encoding="utf-8")
    assert "| 17:00:00 | Show A SAT week |" in plan and "| 16:00:00 | Waiting | loops |" in plan
    assert "Saturdays" in plan and "| 18:00:00 | Saturday Special |" in plan
    assert "## 2026-12-31" in plan and "| 23:59:20 | Countdown |" in plan


def test_show_length_counts_pauses(show):
    pls, _, _ = fpp_bundle.site_files("site-a")
    seqs, _, problems = fpp_bundle.check(pls)
    assert not problems
    pl = pls["Show A"]
    pieces = sum(e["type"] != "pause" for e in pl["mainPlaylist"])
    pauses = sum(e["type"] == "pause" for e in pl["mainPlaylist"])
    assert fpp_bundle.playlist_seconds(pl, seqs) == pytest.approx(60 * pieces + cfg.BETWEEN_PAUSE_S * pauses)


def test_missing_or_stale_render_refused(show):
    (show / "Waiting.fseq").unlink()
    (show / "Goodnight.xsq").write_text("x")
    import os
    os.utime(show / "Goodnight.fseq", (1, 1))
    with pytest.raises(SystemExit) as e:
        fpp_bundle.bundle("site-a")
    assert "no Waiting.fseq" in str(e.value) and "older than its .xsq" in str(e.value)
