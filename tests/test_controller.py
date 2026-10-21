from collections import Counter

from tools import gen_controller as gc


def test_holes_on_the_board_and_not_shared():
    holes = []
    for header, names in (("J2", gc.J2), ("J3", gc.J3)):
        holes += [gc.esp_hole(header, i) for i in range(1, len(names) + 1)]
    holes += [gc.u1_hole(p) for p in gc.U1_PINS]
    for _, pins in gc.SMALL_PARTS.values():
        holes += [h for _, h in pins]
    assert all(0 <= c < gc.COLS and 0 <= r < gc.ROWS for c, r in holes)
    assert not [h for h, n in Counter(holes).items() if n > 1]


def test_each_pin_in_at_most_one_net():
    pins = [m for members in gc.NETS.values() for m in members]
    assert len(pins) == len(set(pins))
    assert all(len(members) >= 2 for members in gc.NETS.values())


def test_joins_connect_every_net_member():
    for net, members in gc.NETS.items():
        joins = gc.joins(net)
        assert len(joins) == len(members) - 1
        reached = {members[0]}
        for a, b in joins:
            assert a in reached
            reached.add(b)
        assert reached == set(members)


def test_circuit():
    net_of = {m: net for net, members in gc.NETS.items() for m in members}
    assert gc.J3[12 - 1] == "IO16" and net_of[("J3", 12)] == "DATA 3.3V"
    assert gc.J2[19 - 1] == "5V" and net_of[("J2", 19)] == "5V"
    assert gc.J3[1 - 1] == "GND" and net_of[("J3", 1)] == "GND"
    assert net_of[("U1", 14)] == "5V" and net_of[("U1", 7)] == "GND"
    assert net_of[("U1", 1)] == "GND"  # channel 1 enabled
    for pin in (4, 5, 9, 10, 12, 13):  # spare channels tied off
        assert net_of[("U1", pin)] == "GND"
    for pin in (6, 8, 11):  # spare outputs open
        assert ("U1", pin) not in net_of
    # SD card fallback pins (VSPI) stay free.
    for name in ("IO5", "IO18", "IO19", "IO23"):
        assert ("J3", gc.J3.index(name) + 1) not in net_of
    # 12V only reaches the buck input.
    assert gc.NETS["12V"] == [("JP", "12V"), ("M", "IN+")]


def test_bridges_never_skip_a_pad():
    used = set(gc.all_holes())
    for net in gc.NETS:
        for a, b in gc.joins(net):
            if gc.is_bridge(a, b):
                assert gc.hole(*a) in used and gc.hole(*b) in used


def test_deterministic(tmp_path):
    gc.write(tmp_path / "a.svg", tmp_path / "a.md")
    gc.write(tmp_path / "b.svg", tmp_path / "b.md")
    assert (tmp_path / "a.svg").read_bytes() == (tmp_path / "b.svg").read_bytes()
    assert (tmp_path / "a.md").read_bytes() == (tmp_path / "b.md").read_bytes()
