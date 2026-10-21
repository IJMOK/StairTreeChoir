"""Build a scrubbed copy of this repo for publishing: python -m tools.make_public [target]

Exports the committed tree at HEAD (not the working copy, not the history) into a
fresh git repo (default ../StairTreeChoir-public) as a single commit authored with
Rob's GitHub noreply address, so the private history and email stay private.

Checks before committing, and refuses on a hard failure:
- no image with GPS data in its EXIF (hard)
- Rob's email address nowhere in the files (hard)
- no lyrics, .lrc or audio files (hard; lyrics live in the xLights show folder)
- personal references (family, friends, home) are listed for review, not changed

Never pushes. Publishing is a separate, deliberate step: create the public GitHub
repo, then `git remote add origin ...` and `git push` in the target.
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

from tools.tree_layout import ROOT

MARKER = ".public-snapshot"  # only directories carrying this are ever wiped
AUTHOR = "IJMOK <1636330+IJMOK@users.noreply.github.com>"  # GitHub user id 1636330
FORBIDDEN = re.compile(r"(\.lrc|\.lyrics\.txt|\.mp3|\.wav|\.m4a)$", re.I)
# Words in prose, not code (".parents[1]", "parents=True").
PERSONAL = re.compile(r"(?<![.\w])(parents|friends?|front lawn|my house|home address)\b(?!\s*[=\[(])", re.I)
IMAGE = re.compile(r"\.(jpe?g|png|heic|tiff?)$", re.I)


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def export_head(target: Path) -> list[Path]:
    """Committed files at HEAD, written under target."""
    data = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=ROOT,
                          check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(target, filter="data")
        return [target / m.name for m in tar.getmembers() if m.isfile()]


def has_gps(path: Path) -> bool:
    from PIL import Image

    with Image.open(path) as im:
        return bool(im.getexif().get_ifd(0x8825))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", nargs="?", type=Path, default=ROOT.parent / "StairTreeChoir-public")
    args = ap.parse_args(argv)
    target = args.target.resolve()
    private_email = git("config", "user.email").strip()  # read here so it isn't in this file

    if git("status", "--porcelain").strip():
        print("Note: uncommitted changes are not included (only HEAD is exported).")
    if target.exists():
        if not (target / MARKER).exists():
            raise SystemExit(f"{target} exists and isn't a previous public snapshot; not touching it.")
        shutil.rmtree(target)
    target.mkdir(parents=True)

    files = export_head(target)
    rel = lambda p: p.relative_to(target).as_posix()
    hard, review = [], []
    for p in files:
        if FORBIDDEN.search(p.name):
            hard.append(f"{rel(p)}: lyrics/audio file")
        if IMAGE.search(p.name) and has_gps(p):
            hard.append(f"{rel(p)}: GPS in EXIF")
        if IMAGE.search(p.name):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if private_email and private_email in text:
            hard.append(f"{rel(p)}: contains the private email address")
        for n, line in enumerate(text.splitlines(), 1):
            if PERSONAL.search(line) and rel(p) != "tools/make_public.py":
                review.append(f"{rel(p)}:{n}: {line.strip()[:110]}")

    if hard:
        shutil.rmtree(target)
        raise SystemExit("Not built:\n  " + "\n  ".join(hard))

    (target / MARKER).write_text("Built by tools/make_public.py from the private repo; rebuilt on each run.\n",
                                 encoding="utf-8")
    head = git("rev-parse", "--short", "HEAD").strip()
    git("init", "-q", "-b", "main", cwd=target)
    git("add", "-A", cwd=target)
    name, email = AUTHOR[:-1].split(" <")
    git("-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-q",
        "-m", f"Stair Tree Choir (snapshot of private {head})", cwd=target)
    print(f"Built {target}: {len(files)} files, one commit by {AUTHOR}.")
    if review:
        print(f"Personal references to review before publishing ({len(review)}):")
        print("  " + "\n  ".join(review))
    print("Nothing was pushed.")


if __name__ == "__main__":
    main()
