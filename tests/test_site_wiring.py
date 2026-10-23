import json

import pytest

from tools import gen_site_wiring as sw


def test_sites_file_is_valid_and_covers_14_trees():
    data = sw.load_sites()
    trees = sorted(t["tree"] for s in data["sites"] for t in s["trees"])
    assert trees == list(range(1, 15))


def test_no_psu_overloaded_and_every_tree_fused():
    for site in sw.load_sites()["sites"]:
        p = sw.plan(site)
        assert all(psu["amps"] <= sw.PSU[1] for psu in p["psus"])
        assert sum(len(psu["trees"]) for psu in p["psus"]) == len(site["trees"])
        assert sum(psu["player"] for psu in p["psus"]) == 1


def test_flex_size_keeps_the_drop_in_limit():
    assert sw.flex_for(5) == 0.75
    assert sw.drop(5, 0.75) == pytest.approx(0.54, abs=0.01)
    assert sw.flex_for(12) == 1.5
    with pytest.raises(ValueError):
        sw.flex_for(200)


def test_bad_slots_rejected(tmp_path):
    bad = {"sites": [{"id": "x", "name": "X", "player": "Pi", "trees": [{"slot": 2, "tree": 1, "run_m": 5}]}]}
    f = tmp_path / "sites.json"
    f.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        sw.load_sites(f)
