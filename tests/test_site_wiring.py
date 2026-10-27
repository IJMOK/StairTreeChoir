import json

import pytest

from tools import gen_site_wiring as sw


def test_sites_file_is_valid_and_covers_14_trees():
    data = sw.load_sites()
    trees = sorted(t["tree"] for s in data["sites"] for t in s["trees"])
    assert trees == list(range(1, 15))


def test_one_psu_per_site_within_its_margin():
    for site in sw.load_sites()["sites"]:
        p = sw.plan(site)
        assert p["psu"]["amps"] <= p["psu"]["rating"] * sw.PSU_MAX_LOAD
        assert len(p["runs"]) == len(site["trees"])


def test_psu_picks_the_smallest_that_fits():
    assert sw.psu_for(6 * sw.TREE_A + sw.PLAYER_A + sw.ROUTER_A)[0] == "LRS-200-12"
    a = sw.plan({"id": "a", "router": "indoors", "trees": [{"slot": 1, "tree": 1, "run_m": 5}]})
    assert not a["router_on_psu"] and a["psu"]["amps"] == pytest.approx(sw.TREE_A + sw.PLAYER_A)
    assert sw.psu_for(2 * sw.TREE_A + sw.PLAYER_A)[0] == "LRS-100-12"
    with pytest.raises(ValueError):
        sw.psu_for(20)


def test_flex_size_keeps_the_drop_in_limit():
    assert sw.flex_for(5) == 0.75
    assert sw.drop(5, 0.75) == pytest.approx(0.49, abs=0.01)
    assert sw.flex_for(12) == 1.5
    with pytest.raises(ValueError):
        sw.flex_for(200)


def test_bad_slots_rejected(tmp_path):
    bad = {"sites": [{"id": "x", "name": "X", "player": "Pi", "trees": [{"slot": 2, "tree": 1, "run_m": 5}]}]}
    f = tmp_path / "sites.json"
    f.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        sw.load_sites(f)
