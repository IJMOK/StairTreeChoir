# Stair Tree Choir

Fourteen lip-syncing pixel Christmas trees cut from old spiral-stair oak treads, driven by seven identical Pi + FPP pair kits.

The project brief, decisions and milestones are in [CLAUDE.md](CLAUDE.md). The parts list is in [docs/bom.md](docs/bom.md).

## Quick start

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m tools.build     # regenerate data/ and cad/
.venv/Scripts/python -m pytest -q
```

Edit `data/blank.json` (the tread outline) or the parameters in `tools/tree_layout.py`, then rebuild. Never edit generated files by hand.
