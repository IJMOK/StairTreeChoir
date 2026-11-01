"""docs/index.html: every docs/*.md in one page with a sidebar: python -m tools.gen_docs_site

A browser won't let a page opened by double-click read the .md files beside it, so they're
rendered here and embedded, and the page needs no server, no network and no copy of a
Markdown library. It's a snapshot: tools/build.py and tools/fpp_bundle.py rewrite it, and
tests/test_docs_site.py fails if a doc changed without a rebuild. Don't edit the file.
A new docs/*.md appears by itself, under "Other" until it's added to GROUPS.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from markdown_it import MarkdownIt

from tools.tree_layout import ROOT

DOCS = ROOT / "docs"
OUT_FILE = DOCS / "index.html"
SITE_TITLE = "Stair Tree Choir"
GROUPS = {
    "Build": ["build-guide", "bom", "tree-box-parts", "cnc-cutting", "test-checklist"],
    "Show": ["show-night", "show-plan", "whats-on", "specials", "backstory", "webcam"],
    "Reference": ["design-review", "research", "folders"],
}
# The sidebar uses the title up to any colon; these need something better.
NAV_TITLES = {"backstory": "Who they are"}
# Hand-made pages in docs/ that open on their own: group -> (file, sidebar title).
PAGES = {"Build": [("wiring.html", "Site A wiring diagrams")]}

TICK_BOX = re.compile(r"<li>(\s*(?:<p>)?)\[( |x|X)\] ")
SLUG_DROP = re.compile(r"[^\w\s-]")


def slug(text: str) -> str:
    """Heading text -> GitHub's anchor, so a link written for GitHub works here too."""
    return re.sub(r"\s", "-", SLUG_DROP.sub("", text.lower()).strip())


def local_href(href: str, doc: str) -> str | None:
    """A link's address inside the page, or None if it leaves the page."""
    if "://" in href or href.startswith("mailto:"):
        return None
    path, _, fragment = href.partition("#")
    if not path:
        return f"#{doc}/{fragment}"
    target = (DOCS / path).resolve()
    if target.suffix == ".md" and target.parent == DOCS.resolve():
        return f"#{target.stem}/{fragment}" if fragment else f"#{target.stem}"
    return None


def render_doc(text: str, doc: str) -> tuple[str, str, list[tuple[str, str]]]:
    """One Markdown file -> (title, body HTML, [(section anchor, section title)])."""
    # breaks: the skit scripts are one speaker per line. No doc wraps its paragraphs by hand.
    md = MarkdownIt("commonmark", {"breaks": True, "html": False}).enable(["table", "strikethrough"])
    tokens = md.parse(text)
    title, sections, seen = doc, [], {}
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            name = tokens[i + 1].content
            base = slug(name)
            seen[base] = seen.get(base, -1) + 1
            anchor = f"{doc}/{base}-{seen[base]}" if seen[base] else f"{doc}/{base}"
            token.attrSet("id", anchor)
            if token.tag == "h1" and title == doc:
                title = name
            elif token.tag in ("h1", "h2"):
                sections.append((anchor, name))
        for child in token.children or []:
            if child.type == "link_open":
                href = local_href(str(child.attrGet("href")), doc)
                if href:
                    child.attrSet("href", href)
                else:
                    child.attrSet("target", "_blank")
                    child.attrSet("rel", "noopener")
    body = md.renderer.render(tokens, md.options, {})
    body = TICK_BOX.sub(lambda m: f'<li class="tick">{m[1]}<input type="checkbox" disabled'
                                  f'{" checked" if m[2] != " " else ""}> ', body)
    return title, body, sections


def doc_order(names: list[str]) -> dict[str, list[str]]:
    """Sidebar groups, in order, holding only the docs that exist."""
    groups = {group: [n for n in docs if n in names] for group, docs in GROUPS.items()}
    placed = {n for docs in groups.values() for n in docs}
    others = sorted(set(names) - placed)
    return groups | {"Other": others} if others else groups


def render() -> str:
    rendered = {p.stem: render_doc(p.read_text(encoding="utf-8"), p.stem) for p in sorted(DOCS.glob("*.md"))}
    groups = doc_order(list(rendered))
    order = [n for docs in groups.values() for n in docs]

    nav = []
    for group, docs in groups.items():
        items = []
        for name in docs:
            title, _, sections = rendered[name]
            label = NAV_TITLES.get(name, title.split(":")[0])
            toc = "".join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in sections)
            toc = f'<ul class="toc">{toc}</ul>' if toc else ""
            items.append(f'<li data-doc="{name}"><a href="#{name}">{html.escape(label)}</a>{toc}</li>')
        for page, label in PAGES.get(group, []):
            if (DOCS / page).exists():
                items.append(f'<li><a href="{page}" target="_blank" rel="noopener">{html.escape(label)} ↗</a></li>')
        nav.append(f'<section><h2>{group}</h2><ul>{"".join(items)}</ul></section>')

    articles = []
    for i, name in enumerate(order):
        title, body, _ = rendered[name]
        hidden = " hidden" if i else ""
        pager = []
        if i:
            before = order[i - 1]
            pager.append(f'<a href="#{before}">← {html.escape(rendered[before][0])}</a>')
        if i < len(order) - 1:
            after = order[i + 1]
            pager.append(f'<a class="next" href="#{after}">{html.escape(rendered[after][0])} →</a>')
        articles.append(f'<article data-doc="{name}" data-title="{html.escape(title)}"{hidden}>\n{body}'
                        f'<footer class="pager">{"".join(pager)}</footer>\n</article>')

    return (PAGE.replace("{{SITE_TITLE}}", SITE_TITLE)
                .replace("{{NAV}}", "\n".join(nav))
                .replace("{{ARTICLES}}", "\n".join(articles)))


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by tools/gen_docs_site.py from docs/*.md. Don't edit this file: change the .md and rebuild. -->
<title>{{SITE_TITLE}}</title>
<style>
/* A workshop sheet, same colours as wiring.html. Everything is in this file, so it works offline. */
:root {
  --bg: #f4f5f1;
  --panel: #ffffff;
  --fg: #1c2326;
  --muted: #5a666b;
  --line: #c6ccc8;
  --hatch: #e6e9e4;
  --link: #2a68ad;
  --body: "Segoe UI", system-ui, -apple-system, sans-serif;
  --mono: ui-monospace, Consolas, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #12171a; --panel: #192024; --fg: #e3e8e6; --muted: #98a4a7; --line: #36423f; --hatch: #222b2e; --link: #6fa9ef; }
}
* { box-sizing: border-box; }
html { color-scheme: light dark; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.6 var(--body); }
.layout { display: grid; grid-template-columns: 290px minmax(0, 1fr); min-height: 100vh; }

nav { position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 20px 16px 32px; background: var(--panel); border-right: 1px solid var(--line); font-size: 15px; line-height: 1.35; }
nav .brand { display: block; margin-bottom: 14px; color: var(--fg); font-size: 18px; font-weight: 600; text-decoration: none; }
nav input { width: 100%; padding: 7px 10px; border: 1px solid var(--line); border-radius: 4px; background: var(--bg); color: var(--fg); font: inherit; }
nav .count { min-height: 1.4em; margin: 5px 0 0; color: var(--muted); font-size: 13px; }
nav h2 { margin: 16px 0 4px; color: var(--muted); font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
nav ul { margin: 0; padding: 0; list-style: none; }
nav a { display: block; padding: 5px 8px; border-radius: 4px; color: var(--fg); text-decoration: none; }
nav a:hover { background: var(--hatch); }
nav li.on > a { background: var(--hatch); color: var(--link); font-weight: 600; }
nav .toc { display: none; margin: 2px 0 6px 8px; padding-left: 4px; border-left: 2px solid var(--line); font-size: 14px; }
nav .toc a { color: var(--muted); }
nav li.on .toc { display: block; }
#menu { display: none; }

main { min-width: 0; padding: 32px 40px 48px; }
article { max-width: 980px; margin: 0 auto; }
h1, h2, h3, h4 { line-height: 1.25; scroll-margin-top: 16px; }
article h1 { margin: 0 0 16px; font-size: 32px; }
article h1:not(:first-child) { margin-top: 48px; padding-top: 24px; border-top: 2px solid var(--line); }
article h2 { margin: 36px 0 12px; font-size: 23px; }
article h3 { margin: 26px 0 8px; font-size: 18px; }
article a { color: var(--link); }
code { padding: 1px 4px; border-radius: 3px; background: var(--hatch); font: .88em var(--mono); }
pre { overflow-x: auto; padding: 12px 14px; border: 1px solid var(--line); border-radius: 4px; background: var(--panel); }
pre code { padding: 0; background: none; }
blockquote { margin: 16px 0; padding: 2px 16px; border-left: 3px solid var(--line); background: var(--panel); }
table { display: block; max-width: 100%; overflow-x: auto; margin: 16px 0; border-collapse: collapse; font-size: 15px; line-height: 1.45; }
th, td { padding: 6px 10px; border: 1px solid var(--line); background: var(--panel); text-align: left; vertical-align: top; }
th { background: var(--hatch); }
li.tick { list-style: none; margin-left: -1.3em; }
li.tick input { margin: 0 5px 0 0; }
hr { margin: 32px 0; border: 0; border-top: 1px solid var(--line); }
.pager { display: flex; justify-content: space-between; gap: 24px; margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); }
.pager .next { margin-left: auto; text-align: right; }

@media (max-width: 800px) {
  .layout { display: block; }
  nav { position: static; height: auto; padding: 12px 16px; border-right: 0; border-bottom: 1px solid var(--line); }
  nav .brand { display: inline-block; margin: 0; }
  #menu { display: block; float: right; padding: 4px 12px; border: 1px solid var(--line); border-radius: 4px; background: var(--bg); color: var(--fg); font: inherit; }
  nav .fold { display: none; margin-top: 12px; }
  nav.open .fold { display: block; }
  main { padding: 20px 16px 32px; }
  article h1 { font-size: 26px; }
}
@media print {
  body { background: #fff; color: #000; font-size: 11pt; }
  .layout { display: block; }
  nav, .pager { display: none; }
  main { padding: 0; }
  article { max-width: none; }
  table { display: table; }
  th, td { border-color: #888; background: none; }
  th { background: #eee; }
  blockquote, pre, code { background: none; }
  article a { color: inherit; }
  h1, h2, h3 { break-after: avoid; }
  tr, li.tick { break-inside: avoid; }
}
</style>
</head>
<body>
<div class="layout">
<nav aria-label="Documents">
<a class="brand" href="#">{{SITE_TITLE}}</a>
<button id="menu" type="button" aria-expanded="false">Contents</button>
<div class="fold">
<input id="search" type="search" placeholder="Search all the docs" aria-label="Search all the docs">
<p class="count" id="count"></p>
{{NAV}}
</div>
</nav>
<main>
{{ARTICLES}}
</main>
</div>
<script>
const articles = [...document.querySelectorAll("article")];
const items = [...document.querySelectorAll("nav li[data-doc]")];
const search = document.getElementById("search");
const count = document.getElementById("count");
const nav = document.querySelector("nav");
const menu = document.getElementById("menu");
const words = new Map(articles.map(a => [a.dataset.doc, a.textContent.toLowerCase()]));
let current = null;

function show() {
  const hash = decodeURIComponent(location.hash.slice(1));
  const name = hash.split("/")[0];
  const article = articles.find(a => a.dataset.doc === name) || articles[0];
  const changed = article !== current;
  current = article;
  articles.forEach(a => { a.hidden = a !== article; });
  items.forEach(li => li.classList.toggle("on", li.dataset.doc === article.dataset.doc));
  document.title = `${article.dataset.title} · {{SITE_TITLE}}`;
  const section = hash.includes("/") && document.getElementById(hash);
  if (section) section.scrollIntoView();
  else if (changed) scrollTo(0, 0);
  if (changed && !section && search.value && window.find) {
    getSelection().collapse(article, 0);  // find goes forward from here, past the sidebar
    window.find(search.value.trim());
  }
}

function filter() {
  const query = search.value.trim().toLowerCase();
  let hits = 0;
  items.forEach(li => {
    li.hidden = query && !words.get(li.dataset.doc).includes(query);
    hits += !li.hidden;
  });
  document.querySelectorAll("nav section").forEach(s => {
    s.hidden = query && !s.querySelector("li[data-doc]:not([hidden])");
  });
  count.textContent = query ? (hits ? `In ${hits} of ${items.length} docs. Pick one to jump to the first match.` : "No matches.") : "";
}

addEventListener("hashchange", show);
search.addEventListener("input", filter);
menu.addEventListener("click", () => {
  menu.setAttribute("aria-expanded", nav.classList.toggle("open"));
});
nav.addEventListener("click", e => {
  if (e.target.matches("a:not(.brand)")) {
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", false);
  }
});
show();
</script>
</body>
</html>
"""


def main() -> None:
    OUT_FILE.write_text(render(), encoding="utf-8", newline="\n")
    print(f"wrote {OUT_FILE.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
