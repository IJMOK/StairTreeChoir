import pytest

pytest.importorskip("shapely")

from tools import gen_controller as gc  # noqa: E402
from tools import gen_pcb as gp  # noqa: E402


def pcb_lookup():
    """(part, pin) as gen_controller names them -> the PCB pads' nets."""
    out = {}
    for p in gp.pads():
        part, pin = p.ref.split()[0].split(".", 1)
        if part in ("J2", "J3", "U1"):
            pin = int(pin)
        elif part == "M":
            pin = pin.rstrip("ab")
        out.setdefault((part, pin), []).append(p.net)
    return out


def test_esp32_u1_and_mini560_in_the_protoboard_holes():
    # These set the box's fit (tall parts, the Mini560 standing at the column A edge); R1, R2, C1, C2
    # and JD are placed for the 1mm isolation rules.
    pcb = {p.ref.split()[0]: (round(p.x, 3), round(p.y, 3)) for p in gp.pads()}
    for header, names in (("J2", gc.J2), ("J3", gc.J3)):
        for i in range(1, len(names) + 1):
            assert pcb[f"{header}.{i}"] == tuple(round(v, 3) for v in gp.gxy(*gc.esp_hole(header, i)))
    for p in gc.U1_PINS:
        assert pcb[f"U1.{p}"] == tuple(round(v, 3) for v in gp.gxy(*gc.u1_hole(p)))
    for ref, row in (("M.OUT+a", 3), ("M.OUT+b", 4), ("M.OUT-a", 7), ("M.OUT-b", 8)):
        assert pcb[ref] == tuple(round(v, 3) for v in gp.gxy(2, row))


def test_same_circuit_as_the_protoboard():
    look = pcb_lookup()
    seen = {}
    for net, members in gc.NETS.items():
        pcb_nets = {n for m in members for n in look[m]}
        assert len(pcb_nets) == 1, (net, pcb_nets)
        seen[net] = pcb_nets.pop()
    assert len(set(seen.values())) == len(seen)       # different nets stay apart


def test_fixings_match_the_box():
    assert (gp.BOARD_W, gp.BOARD_H, gp.HOLE_IN) == (70.0, 50.0, 2.0)  # tree-box params pb_w, pb_h, pb_hole_in


def test_one_tool_only():
    job = gp.gcode_all()
    assert "M06" not in job and "M6 " not in job
    assert gp.CLEAR == gp.EM_D == 1.0


def test_milled_copper_matches_the_netlist():
    cu = gp.copper()
    report, fails = gp.checks(cu, gp.gcode_all())
    assert not fails, "\n".join(report)
