# Enclosures (M3)

## Tree controller box

`tree-box.scad`, one per tree, an **L base + clip-on cover** (Rob, 30 Oct 2026), on spacers on the back of the tree. Shared sizes are in `tree-box-params.scad`; `python -m tools.gen_printed` exports everything and `python -m tools.gen_components` checks that the bought parts fit ([docs/tree-box-parts.md](../docs/tree-box-parts.md)).

```
openscad -o tree-box-base.stl      -D 'part="base"'      tree-box.scad   # PETG, tree face on the bed, no supports
openscad -o tree-box-cover.stl     -D 'part="cover"'     tree-box.scad   # PETG, back on the bed, no supports
openscad -o tree-box-spacer.stl    -D 'part="spacer"'    tree-box.scad   # 4 per tree
openscad -o tree-box-coupon.stl    -D 'part="coupon"'    tree-box.scad   # print first: SP16, PG7, RP-SMA, an M3 insert, an M2 screw
openscad -o tree-box-seal-test.stl -D 'part="seal-test"' tree-box.scad   # print first: the cord squeeze from one hook and one screw
```

About 113 × 50 × 109mm overall with the ears and the roof, plus the 10mm spacers; inside 82 wide, 42 deep.

- **Base** (everything is built on it, on the bench): an L. A 5mm back plate on 10mm spacers off the tree, with four blended ears (a 4.6mm slot each, for 4 × 40 stainless pan-head wood screws), and a shelf along its bottom.
  - The controller board sits on four M2 standoffs on the plate, components facing the back. The Mini560 stands on the board. The two Wago 221-413s sit on the plate below the board.
  - The 3.5mm shelf carries three fittings, all firing down: the RP-SMA antenna bulkhead (outer side, in a recess that thins the shelf to 3mm), the SP16 panel socket (12V run in: D hole 16.5mm with a flat at 15.3mm, rear nut) and the PG7 gland (pixel lead out). Nothing unplugs when the cover comes off.
  - The 2.7mm cord sits in a groove in the plate's back face (`seal.scad`, 3.8 × 2.05mm), over the top and down both sides, held by pinch points. Its ends stop just above the shelf.
  - Two slots near the top of the plate, above the cord, take the cover's hooks. A block on the shelf holds one M3 heat-set insert, at 45°.
- **Cover**: back, sides and a roof sloping 8° away from the tree, with a rim that lands on the plate, and a lip under the shelf with open U cutouts round the three fittings. Lift it, put its two hook tabs through the slots, drop it so the teeth catch behind the plate, swing it in, and fit one M3 × 10 screw through the bevel on its lower back corner. The screw is at 45° so that it pulls the cover in against the cord as well as up onto the shelf; a straight-up screw wouldn't squeeze the cord at all.
- **Not sealed at the bottom, on purpose** (Rob, 30 Oct 2026): rain doesn't fall upwards, and anything that gets in drains out round the fittings.
- **Spacers**: 10mm printed tubes between the ears and the oak, so rain runs down between the tree and the box.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`: 2mm in from the corners, from a photo), the SP16 nut and thread length, the PG7 and RP-SMA sizes, the M3 insert hole (4.0mm), and the cord's squeeze along the sides. Print the coupon and the seal test first.

## PSU terminal cover

`psu-cover.scad`, one for Site A's S-400-12 (`psu-cover.stl`, PETG, end wall on the bed, no supports). A hood over the terminal end, held by two M4 × 6 screws in the case's threaded side holes, with a rib between the 12V and mains sides and a cable notch each. Don't use longer screws: past about 3mm they reach into the PSU. Its sizes are scaled from photos, so offer up the print before wiring.

## Site box

`site-box.scad`, one per site: the show player and the 12V distribution. Wiring per site: [electronics/site-wiring.md](../electronics/site-wiring.md).

```
openscad -o site-box-6-trees.stl -D 'part="box"' -D 'trees=6' site-box.scad   # also 4 and 2: same box, fewer glands
openscad -o site-box-lid.stl     -D 'part="lid"'    site-box.scad
```

Outside 235 × 195mm plus the roof (prints 235 × 241mm with the lugs, inside the 255mm bed); inside 230 × 190 × 64mm. Upright wall box on the shared shell (`sealed-box.scad`): roof sloping away from the post with a hood over the lid, lid on the front, every cable through the floor. Screw it to a post or fence through the lugs below the floor and above the roof (5 × 40 exterior screws).

- **Back wall**: Pi standoffs (Raspberry Pi 58 × 49mm M2.5 pattern, Pi 3 and Pi 5 alike) top left; a 30mm grid of zip-tie anchors for the router, 12V→5V buck, PAM8610, USB sound card, Wagos and inline fuse holders. Their sizes aren't confirmed, so lay the real parts out on the wall and tie them where they fit.
- **Floor**: PG9 per PSU input, PG9 per tree run, PG7 for the speaker (two rows for a 6-tree site), 3mm drip hole.
- **Lid**: eight M3 screws into heat-set inserts, 2.7mm rubber cord in the lid groove (`seal.scad`), rain skirt.
- **12V inside**: each PSU's input goes to its own Wago pair (+ and −) and from there through its own inline 5A blade fuses to its two tree runs. Never join two PSUs' +12V. PSU 1 also feeds the player through a 3A fuse (buck → Pi; PAM8610 straight off 12V). The negatives may be joined.
- The Mean Well PSUs stand outside, beside the box (IP67); mains never enters it.

**Superseded 26 Oct 2026 (Rob):** the site box is now a bought DRiBOX Large with the site's one LRS PSU inside it, on a printed plate still to design (CLAUDE.md §4). This printed box and its notes above are kept for reference only.

**Unverified:** gland threads, M3 insert hole, and that the router, buck and amp fit the 64mm depth. A Pi 5 needs a 5V 5A buck.
