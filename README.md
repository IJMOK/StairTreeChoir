# Stair Tree Choir

Fourteen lip-syncing pixel Christmas trees cut from old spiral-stair oak treads. Each tree has its own ESP32 (WLED); each site has one Pi running FPP that plays the audio and streams the frames over Wi-Fi.

To read the docs with a sidebar and search, open [docs/index.html](docs/index.html).

## Where to start

| I want to… | Go to |
|---|---|
| Know what's decided and why | [CLAUDE.md](CLAUDE.md), the project brief |
| Build it, stage by stage | [docs/build-guide.md](docs/build-guide.md), with [docs/test-checklist.md](docs/test-checklist.md) |
| Buy parts | [docs/bom.md](docs/bom.md) |
| Print something | [print/](print/README.md): every STL, with counts and settings; `tree-plate.gcode.3mf` is one tree's whole set of mounts, sliced for the P1S (16h, 640g) |
| Change a part's design | [cad/](cad/README.md): one FreeCAD master per part, and the whole setup in [cad/stair-tree-choir.FCStd](cad/stair-tree-choir.FCStd) |
| Cut a tree on the CNC | [docs/cnc-cutting.md](docs/cnc-cutting.md) |
| Wire a tree | [docs/tree-wiring.html](docs/tree-wiring.html) (pixel order and the box), [electronics/](electronics/README.md) (the controller board) |
| Wire a site box | [docs/site-box-wiring.html](docs/site-box-wiring.html) (Site A, every wire), [docs/wiring.html](docs/wiring.html) (how it all connects), [electronics/site-wiring.md](electronics/site-wiring.md) (runs and fuses per site) |
| Set up the controllers and players | [wled/](wled/README.md), [fpp/](fpp/README.md) |
| Sequence a song | [xlights/](xlights/README.md), [docs/show-plan.md](docs/show-plan.md) |
| Find a file | [docs/folders.md](docs/folders.md) |

## Quick start

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
make all     # = python -m tools.build: layout, CNC and CAM files, xLights model, configs, docs site
make cad     # = python -m tools.cad: every printed part, STEP and picture from the FreeCAD masters (FreeCAD 1.1, a few minutes)
make slice   # = python -m tools.slice: slice the one-tree plate for the P1S in Bambu Studio -> print/tree-plate.gcode.3mf
make test    # = python -m pytest -q
```

Edit `data/blank.json` (the tread outline), `data/sites.json` (the sites) or a master in `cad/parts/`, then rebuild. Never edit generated files by hand.
