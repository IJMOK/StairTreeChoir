"""docs/index.html is generated from docs/*.md (tools/gen_docs_site.py) and stays in step."""

import re

from tools import gen_docs_site as site
from tools.tree_layout import ROOT


def test_index_is_in_step_with_the_docs():
    assert site.OUT_FILE.read_text(encoding="utf-8") == site.render(), "re-run python -m tools.gen_docs_site"


def test_every_doc_is_in_the_sidebar_and_on_the_page():
    page = site.render()
    for path in (ROOT / "docs").glob("*.md"):
        assert f'<li data-doc="{path.stem}">' in page
        assert f'<article data-doc="{path.stem}"' in page


def test_every_link_inside_the_page_lands_somewhere():
    page = site.render()
    ids = set(re.findall(r'\s(?:id|data-doc)="([^"]+)"', page))
    targets = set(re.findall(r'href="#([^"]+)"', page))
    assert targets
    assert not targets - ids


def test_links_between_docs_stay_inside_the_page_and_others_leave_it():
    _, body, _ = site.render_doc(
        "[a](bom.md) [b](bom.md#extras) [c](#local) [d](../electronics/README.md) [e](https://example.com)\n", "webcam")
    assert 'href="#bom"' in body and 'href="#bom/extras"' in body and 'href="#webcam/local"' in body
    assert '<a href="../electronics/README.md" target="_blank"' in body
    assert '<a href="https://example.com" target="_blank"' in body


def test_headings_get_github_anchors_unique_to_the_doc():
    title, body, sections = site.render_doc("# Top\n\n## Who's on?\n\n## Who's on?\n\n### Small\n\n# Next\n", "bom")
    assert title == "Top"
    assert 'id="bom/whos-on"' in body and 'id="bom/whos-on-1"' in body
    assert sections == [("bom/whos-on", "Who's on?"), ("bom/whos-on-1", "Who's on?"), ("bom/next", "Next")]


def test_markdown_features_the_docs_use():
    _, body, _ = site.render_doc("| a |\n|---|\n| 1 |\n\n- [ ] open\n- [x] done\n\n> **A:** one\n> **B:** two\n", "x")
    assert "<table>" in body
    assert '<input type="checkbox" disabled> open' in body and '<input type="checkbox" disabled checked> done' in body
    assert "one<br" in body  # a script's speakers stay on their own lines


def test_a_new_doc_lands_under_other():
    assert site.doc_order(["bom", "new-notes"])["Other"] == ["new-notes"]
    assert "Other" not in site.doc_order(["bom"])
