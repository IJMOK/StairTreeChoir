"""docs/whats-on.md is generated with docs/show-plan.md (tools/fpp_bundle.py) and stays in step."""

from tools import whats_on
from tools.tree_layout import ROOT


def test_whats_on_is_in_step_with_the_show_plan():
    plan = (ROOT / "docs" / "show-plan.md").read_text(encoding="utf-8")
    page = (ROOT / "docs" / "whats-on.md").read_text(encoding="utf-8")
    assert page == whats_on.render(whats_on.lengths_from_plan(plan)), "re-run python -m tools.fpp_bundle site-a"


def test_whats_on_speaks_plainly():
    page = whats_on.render({"Show A": 735, "Show B": 675, "Show C": 820, "Saturday Special": 1681})
    for word in ("FPP", "Home Assistant", "playlist", "fseq", "MQTT"):
        assert word not in page
    assert "about 11-14 minutes" in page and "Lights out by 11:30pm" in page
    assert "5, 12, 19 and 26 December" in page and "midnight countdown" in page
    assert page.count("*(to confirm)*") == 1  # the season dates; the New Year songs are confirmed (Rob, 25 Oct)
    assert "The 5 and 8 o'clock show" in page
