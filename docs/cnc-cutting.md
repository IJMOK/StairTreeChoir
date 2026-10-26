# Cutting a tree on the CNC

One tree per setup, in **one op, front face up, no flip** (Rob, 25 Oct 2026). Nothing is cut from the back: the pixel leads loop across the back face. Not a production run: take it gently and watch the first one all the way through.

Rob does the CAM in Siemens NX from the STEP files made by `tools/gen_step.py` (needs `requirements-cad.txt`; `python -m tools.build` skips it without CadQuery):

| File | What |
|---|---|
| `cad/stair-tree.step` | the finished tread: rounded 18mm corners, 92 counterbores and clearance holes, the old fixing holes in the back |
| `cad/fixture-plate.step` | MDF plate (18mm default), blank bounding box + 50mm all round, with a 4mm pocket the shape of the blank |
| `cad/stair-tree-assembly.step` | the two together, tree sitting in the pocket |

For assembling the rest in NX, `tools/gen_printed.py` (OpenSCAD + CadQuery) makes every printed part a STEP solid in `cad/printed/` (boots, pegs, tree box, site boxes, step clamp and washer, pixel disk), each as fitted, and `cad/stair-tree-kit.step`: the tree with both boots, pegs, the tree box and 92 pixel disks in place, in the same axes as `cad/stair-tree.step`. They are made from the OpenSCAD meshes, so flat faces are planes and curved ones are faceted. The frames are listed at the top of the tool.

Axes: mm, Z up, the tree's front face at Z = 0 (the part runs from Z = −30 to 0), X right, Y up (the tree's top is +Y), origin at the bottom-left of the blank's bounding box. The plate shares the origin, so its top is at Z = −26. The pocket is drawn at **zero clearance**: set the offset in CAM.

The 2D files stay as reference: `cad/stair-tree-cnc-layout.dxf` (or `.svg`), mm, front view. Layers:

| Layer | Op | What |
|---|---|---|
| `FRONT_COUNTERBORE` | 1 | 92 × Ø19 × 6mm, for the printed pixel disks |
| `FRONT_HOLES` | 1 | 92 × Ø15 clearance holes, right through |
| `EXISTING` | — | reference only: the old fixing holes in the back (not mirrored). Don't cut. |
| `BLANK` | — | the tread outline, for positioning only |

How the pixel sits: a printed PETG disk (`fixtures/pixel-disk.scad`, Ø18.5 × 6mm, a 2mm front lip with bore `hole_dia`) is glued into the counterbore; the bullet pushes in from the front, its Ø13.6 flange resting on the disk and its clips snapping behind the lip. The fit is set by the printed bore, not the oak.

## Before the first tree

1. **Offcut test** (pixels needed): print the disk test strip (bores 11.8 to 12.2), and cut one Ø19 × 6 counterbore and Ø15 clearance hole in an oak offcut. Glue a disk in, and check a pixel snaps in and its clips clear the hole. Set `hole_dia` (disk bore) and `clearance_dia` in `tools/tree_layout.py`, then `make all`. **TBC (Rob):** the clip barb flare, which sets `clearance_dia`.
2. **Tape-check the tread** against `data/blank.json`: length ~894, wide end ~382, narrow end ~92. If one is out by more than about 3mm, fix the JSON and regenerate before cutting.

## Op 0: fixture pocket (once)

- Screw an MDF sheet (18mm, or set `plate_thickness` in `tools/gen_step.py`) to the bed, at least the blank plus 50mm all round.
- Pocket it 4mm deep to the blank outline, with your clearance offset. Rob may use a bigger bit than the 4mm for this.
- Drop a tread in to check the fit before cutting any tree.
- **Never move the plate again.** XY zero stays where it is for every tree.

## Op 1: front face up, counterbores and holes

- Drop the tread into the pocket, front face up, narrow end towards +Y. Hold it down with workshop clamps (or the printed step clamps, `fixtures/`, with `spoil_t` set to the plate less the pocket: 14mm for 18mm MDF). The pocket locates it; the clamps only stop it lifting.
- **Clamp clearance:** the counterbore edge is ~12.5mm in from the blank edge, so grip no more than 10mm of the edge, between pixels where you can. Check every clamp against the toolpath before starting.
- Z zero on the tread's front face; touch off each tree, as the thickness varies.
- Counterbores: Ø19 × 6mm (Rob, after the first-off run, 26 Oct 2026), to the finished size (the disk is Ø18.5).
- Clearance holes: helical bore Ø15 through, to 0.5mm into the MDF. Holes through the pocket floor are fine; each tree reuses the same spots.
- Peck/clear: lift out of the hole every 6–8mm of depth and blow the chips out. Deep oak holes pack with chips, and packed chips are what snap a 4mm bit.

## Feeds for oak (starting point, 4mm 2-flute carbide)

4mm two-flute carbide end mill with enough reach for 30mm (Rob, 23 Oct 2026). Rob may choose other tools in NX.

| | Value |
|---|---|
| Spindle | 18,000 rpm |
| Feed | 800–1000 mm/min (≈0.025mm per tooth: gentle) |
| Plunge / helix | 300 mm/min, helix step 1mm per turn |
| Depth per pass | 1mm per helix turn in the holes; the counterbore in 1mm steps |
| Width per pass | ≤ 40% of the bit in the counterbore; or adaptive clearing |
| Finish | a 0.2mm finishing pass on the counterbore wall, so the disk drops in |

Listen and look at the chips: dust means the feed is too slow (heat dulls the bit); a screech or shower of splinters means it's too fast or too deep. Slow down in the narrow top end, where there's less wood to hold the board.

## After cutting

Sand the front lightly (don't round the counterbore edges), then oil per CLAUDE.md §3. Glue the disks in after the oil has cured (build-guide §5); the fit is in the disk, so the oil can't close it up.
