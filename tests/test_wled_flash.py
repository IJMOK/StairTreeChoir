import json

import pytest

from tools import wled_apply, wled_flash as wf


def test_rpc_packet_matches_improv_cpp():
    p = wf.improv_packet(wf.RPC_INFO)
    assert p[:6] == b"IMPROV" and list(p[6:11]) == [1, 3, 2, 3, 0]
    assert p[-1] == sum(p[:-1]) & 0xFF


def test_wifi_payload_is_length_prefixed():
    assert wf.wifi_payload("ab", "xyz") == b"\x02ab\x03xyz"
    p = wf.improv_packet(wf.RPC_WIFI, wf.wifi_payload("ab", "xyz"))
    assert p[8] == 2 + 7 and p[9] == 1 and p[10] == 7 and p[11:18] == b"\x02ab\x03xyz"


def test_long_wifi_details_refused():
    with pytest.raises(ValueError):
        wf.wifi_payload("x" * 33, "p")
    with pytest.raises(ValueError):
        wf.wifi_payload("s", "x" * 65)


def frame(kind: int, data: bytes) -> bytes:
    p = b"IMPROV" + bytes([1, kind, len(data)]) + data
    return p + bytes([sum(p) & 0xFF]) + b"\n"


def test_frames_found_among_serial_noise_and_partial_reads():
    a, b = frame(wf.TYPE_STATE, b"\x04"), frame(wf.TYPE_RESULT, b"\x01\x12\x11http://192.168.0.9")
    frames, rest = wf.improv_frames(b"boot log\r\n" + a + b"{json}" + b[:6])
    assert frames == [(wf.TYPE_STATE, b"\x04")]
    frames, rest = wf.improv_frames(rest + b[6:])
    assert frames == [(wf.TYPE_RESULT, b"\x01\x12\x11http://192.168.0.9")]


def test_bad_checksum_dropped():
    bad = bytearray(frame(wf.TYPE_STATE, b"\x04"))
    bad[9] = 3
    assert wf.improv_frames(bytes(bad))[0] == []


def test_rpc_strings():
    assert wf.rpc_strings(b"\x03\x09\x04WLED\x03abc") == ["WLED", "abc"]


def test_bench_config_keeps_wifi_off_the_wire():
    cfg = wf.tree_config(3, False, "HomeNet", "s3cret")
    assert "nw" not in cfg and "s3cret" not in json.dumps(cfg)
    assert cfg["id"]["mdns"] == "stairtree-03" and cfg["hw"]["led"]["ins"][0]["pin"] == [16]


def test_site_config_carries_fixed_ip_and_wifi():
    wifi = wf.tree_config(3, True, "SiteNet", "s3cret")["nw"]["ins"][0]
    assert wifi["ssid"] == "SiteNet" and wifi["psk"] == "s3cret" and wifi["ip"] == [192, 168, 8, 103]


def test_log_keeps_one_row_per_tree_and_board(tmp_path):
    path = tmp_path / "log.csv"
    wf.log(2, "aaa", "bench", "http://1", path)
    wf.log(3, "bbb", "bench", "http://2", path)
    wf.log(9, "aaa", "bench", "http://1", path)     # board aaa renumbered
    wf.log(2, "ccc", "bench", "http://3", path)     # a new board takes tree 2
    rows = path.read_text(encoding="utf-8").splitlines()[1:]
    assert [r.split(",")[1:3] for r in rows] == [["2", "ccc"], ["3", "bbb"], ["9", "aaa"]]


def test_other_boards_protected():
    assert {"d48c49160a30", "98cdac30920f", "c4dee21939ec"} <= set(wf.PROTECTED)


def test_images_are_laid_out_as_the_installer_does():
    assert [i[0] for i in wf.IMAGES] == [0x1000, 0x8000, 0x10000]
    assert all(len(i[3]) == 64 for i in wf.IMAGES)


def test_credentials_from_file(tmp_path, monkeypatch):
    monkeypatch.delenv("STAIRTREE_WIFI_SSID", raising=False)
    monkeypatch.delenv("STAIRTREE_WIFI_PSK", raising=False)
    monkeypatch.setattr(wled_apply.Path, "home", lambda: tmp_path)
    (tmp_path / ".stairtree_wifi.json").write_text('{"ssid": "Net", "psk": "pw"}', encoding="utf-8")
    assert wled_apply.credentials() == ("Net", "pw")


def test_credentials_missing_stops(tmp_path, monkeypatch):
    monkeypatch.delenv("STAIRTREE_WIFI_SSID", raising=False)
    monkeypatch.delenv("STAIRTREE_WIFI_PSK", raising=False)
    monkeypatch.setattr(wled_apply.Path, "home", lambda: tmp_path)
    with pytest.raises(SystemExit):
        wled_apply.credentials()


def test_credentials_file_is_not_in_the_repo():
    assert not (wf.ROOT / ".stairtree_wifi.json").exists()
