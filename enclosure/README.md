# Enclosures (M3)

## Tree controller box

`tree-box.FCStd` (FreeCAD 1.1), one box per tree, an **L base + wrap-round cover** (Rob, 31 Oct 2026), on spacers on the back of the tree. It moved here from OpenSCAD on 1 Nov 2026, matching to within 0.03% by volume (the spacer 0.15%, faceting on the old round walls), with real curved surfaces. Two changes followed that same day (Rob): the shelf now runs the plate's full width, closing the 2.9mm slot at each end, and the insert's hole goes right through the boss. The base has to be reprinted for them; the cover hasn't changed.

**To change it:** edit a value in the `params` spreadsheet (sizes in mm, the same names the OpenSCAD used; leave the "worked out" rows alone) and recompute. Each sketch is fully constrained and bound to the spreadsheet. Anything needing a new shape goes in the body's feature tree. Save, then from the repo root:

```
freecadcmd -c "import sys; sys.path.insert(0, 'tools'); import tree_box_export; tree_box_export.main()"
python -m tools.gen_components     # fit checks, cad/tree-box-assembly.step, docs/tree-box-parts.md
```

`freecadcmd` is in `%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin`. A rebuild takes about a minute, the export under a minute and the fit checks about 20 seconds.

| Body | Print file | Print it |
|---|---|---|
| Base | `tree-box-base.stl` | PETG, tree face on the bed, no supports |
| Cover | `tree-box-cover.stl` | PETG, back on the bed, no supports |
| Spacer | `tree-box-spacer.stl` | 4 per tree |
| Coupon | `tree-box-coupon.stl` | Print first: SP16, PG7, RP-SMA, an M3 insert, an M2 insert |
| SealStrip, SealBar | `tree-box-seal-test.stl` | Print first: the cord squeeze from the hook and one screw |

The "Fitted parts" group in the model is a static import of `cad/tree-box-assembly.step` for reference: it doesn't follow the spreadsheet, and the export ignores it.

About 117 × 53 × 110mm overall with the ears, the hook and the roof, plus the 10mm spacers; the cover is 92 wide; inside 87 wide, 42 deep.

- **Base** (everything is built on it, on the bench): an L. A 5mm back plate on 10mm spacers off the tree, with four blended ears (a 4.6mm slot each, for 4 × 40 stainless pan-head wood screws), and a shelf along its bottom.
  - The controller board sits on four standoffs on the plate, each with an M2 heat-set insert (3.2mm hole), components facing the back. The Mini560 stands on the board. The two Wago 221-413s sit on the plate below the board.
  - The 3.5mm shelf runs the plate's full width, so its ends sit 0.25mm off the cover's walls and the box's bottom is closed apart from the fittings and that fit. It carries three fittings, all firing down: the RP-SMA antenna bulkhead (outer side, in a recess that thins the shelf to 3mm), the SP16 panel socket (12V run in: D hole 16.5mm with a flat at 15.3mm, rear nut) and the PG7 gland (pixel lead out). Nothing unplugs when the cover comes off.
  - The 2.7mm cord sits in a groove in the plate's back face (3.8 × 2.05mm), over the top and down both sides, held by pinch points. Its ends stop just above the shelf.
  - A 45° chamfer along the top edge of the plate, at the tree face, takes the cover's hook. A boss on the shelf holds one M3 heat-set insert, at 45°, in a 4.0mm hole right through the boss (Rob, 1 Nov 2026), so an M3 × 10 can't bottom out. There is no shoulder to stop the insert: push it in until it is flush with the boss's face.
- **Cover** (Rob, 31 Oct 2026): back, sides and a roof sloping 8° away from the tree, with a rim that lands on the plate and skirts that wrap the plate's top and side edges, notched round the ears. Hold it with the bottom a few degrees out, lift it 2mm over the plate's top edge, drop it so the hook catches behind the plate, swing it in, and fit one M3 × 10 screw through the bevel on its lower back corner. The hook is along the very top so everything lies below the pivot; the old slots, lower down, drove the rim above them into the plate. Nothing of the cover goes under the shelf, because a swing about the top lifts anything under there into it. The side skirts only guide and shed rain: a wrap round a 5mm plate is too short to flex as a snap. The screw is at 45° so that it pulls the cover in against the cord and up until the roof meets the plate's top edge; a straight-up screw wouldn't squeeze the cord at all.
- **Not sealed at the bottom, on purpose** (Rob, 30 Oct 2026): rain doesn't fall upwards, and anything that gets in drains out round the fittings and through the 0.25mm fit at the shelf's ends and back edge.
- **Spacers**: 10mm printed tubes between the ears and the oak, so rain runs down between the tree and the box.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`: 2mm in from the corners, from a photo), the SP16 nut and thread length, the PG7 and RP-SMA sizes, the M3 and M2 insert holes (4.0 and 3.2mm), and the cord's squeeze along the sides. Print the coupon and the seal test first.

## PSU terminal cover

`psu-cover.scad`, one for Site A's S-400-12 (`psu-cover.stl`, PETG, end wall on the bed, no supports). A hood over the terminal end, held by two M4 × 6 screws in the case's threaded side holes, with a rib between the 12V and mains sides and a cable notch each. Don't use longer screws: past about 3mm they reach into the PSU. Its sizes are scaled from photos, so offer up the print before wiring.

## Site box

A bought DRiBOX Large (Rob, 26 Oct 2026) with the site's PSU inside on a printed plate, still to design: CLAUDE.md M3. Wiring per site: [electronics/site-wiring.md](../electronics/site-wiring.md). The earlier printed box is in [archive/printed-site-box/](../archive/printed-site-box/).
