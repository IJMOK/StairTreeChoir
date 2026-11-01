# Enclosures (M3)

## Tree controller box

`tree-box.scad`, one per tree, an **L base + wrap-round cover** (Rob, 31 Oct 2026), on spacers on the back of the tree. Shared sizes are in `tree-box-params.scad`; `python -m tools.gen_printed` exports everything and `python -m tools.gen_components` checks that the bought parts fit ([docs/tree-box-parts.md](../docs/tree-box-parts.md)).

```
openscad -o tree-box-base.stl      -D 'part="base"'      tree-box.scad   # PETG, tree face on the bed, no supports
openscad -o tree-box-cover.stl     -D 'part="cover"'     tree-box.scad   # PETG, back on the bed, no supports
openscad -o tree-box-spacer.stl    -D 'part="spacer"'    tree-box.scad   # 4 per tree
openscad -o tree-box-coupon.stl    -D 'part="coupon"'    tree-box.scad   # print first: SP16, PG7, RP-SMA, an M3 insert, an M2 insert
openscad -o tree-box-seal-test.stl -D 'part="seal-test"' tree-box.scad   # print first: the cord squeeze from the hook and one screw
```

About 117 × 53 × 110mm overall with the ears, the hook and the roof, plus the 10mm spacers; the cover is 92 wide; inside 87 wide, 42 deep.

- **Base** (everything is built on it, on the bench): an L. A 5mm back plate on 10mm spacers off the tree, with four blended ears (a 4.6mm slot each, for 4 × 40 stainless pan-head wood screws), and a shelf along its bottom.
  - The controller board sits on four standoffs on the plate, each with an M2 heat-set insert (3.2mm hole), components facing the back. The Mini560 stands on the board. The two Wago 221-413s sit on the plate below the board.
  - The 3.5mm shelf carries three fittings, all firing down: the RP-SMA antenna bulkhead (outer side, in a recess that thins the shelf to 3mm), the SP16 panel socket (12V run in: D hole 16.5mm with a flat at 15.3mm, rear nut) and the PG7 gland (pixel lead out). Nothing unplugs when the cover comes off.
  - The 2.7mm cord sits in a groove in the plate's back face (`seal.scad`, 3.8 × 2.05mm), over the top and down both sides, held by pinch points. Its ends stop just above the shelf.
  - A 45° chamfer along the top edge of the plate, at the tree face, takes the cover's hook. A block on the shelf holds one M3 heat-set insert, at 45°.
- **Cover** (Rob, 31 Oct 2026): back, sides and a roof sloping 8° away from the tree, with a rim that lands on the plate and skirts that wrap the plate's top and side edges, notched round the ears. Hold it with the bottom a few degrees out, lift it 2mm over the plate's top edge, drop it so the hook catches behind the plate, swing it in, and fit one M3 × 10 screw through the bevel on its lower back corner. The hook is along the very top so everything lies below the pivot; the old slots, lower down, drove the rim above them into the plate. Nothing of the cover goes under the shelf, because a swing about the top lifts anything under there into it. The side skirts only guide and shed rain: a wrap round a 5mm plate is too short to flex as a snap. The screw is at 45° so that it pulls the cover in against the cord and up until the roof meets the plate's top edge; a straight-up screw wouldn't squeeze the cord at all.
- **Not sealed at the bottom, on purpose** (Rob, 30 Oct 2026): rain doesn't fall upwards, and anything that gets in drains out round the fittings.
- **Spacers**: 10mm printed tubes between the ears and the oak, so rain runs down between the tree and the box.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`: 2mm in from the corners, from a photo), the SP16 nut and thread length, the PG7 and RP-SMA sizes, the M3 and M2 insert holes (4.0 and 3.2mm), and the cord's squeeze along the sides. Print the coupon and the seal test first.

## PSU terminal cover

`psu-cover.scad`, one for Site A's S-400-12 (`psu-cover.stl`, PETG, end wall on the bed, no supports). A hood over the terminal end, held by two M4 × 6 screws in the case's threaded side holes, with a rib between the 12V and mains sides and a cable notch each. Don't use longer screws: past about 3mm they reach into the PSU. Its sizes are scaled from photos, so offer up the print before wiring.

## Site box

A bought DRiBOX Large (Rob, 26 Oct 2026) with the site's PSU inside on a printed plate, still to design: CLAUDE.md M3. Wiring per site: [electronics/site-wiring.md](../electronics/site-wiring.md). The earlier printed box is in [archive/printed-site-box/](../archive/printed-site-box/).
