# Enclosures (M3)

## Tree controller box

`tree-box.scad`, one per tree, a **base + cover** (Rob, 28 Oct 2026), screwed straight to the back of the tree. Shared sizes are in `tree-box-params.scad`; `python -m tools.gen_printed` exports everything and `python -m tools.gen_components` checks that the bought parts fit ([docs/tree-box-parts.md](../docs/tree-box-parts.md)).

```
openscad -o tree-box-base.stl      -D 'part="base"'      tree-box.scad   # PETG, tree face on the bed, no supports
openscad -o tree-box-cover.stl     -D 'part="cover"'     tree-box.scad   # PETG, back on the bed, no supports
openscad -o tree-box-spacer.stl    -D 'part="spacer"'    tree-box.scad   # 4 per tree
openscad -o tree-box-coupon.stl    -D 'part="coupon"'    tree-box.scad   # print first: SP16, PG7, RP-SMA, an M3 insert, an M2 screw
openscad -o tree-box-seal-test.stl -D 'part="seal-test"' tree-box.scad   # print first: the cord seal and the cover's fit
```

About 119 × 61 × 107mm overall with the flanges and the roof; inside 76 wide, 44 deep, about 86 high.

- **Base** (everything is built on it, on the bench): an L. The tree plate, with a flange down each side (two 4.6mm slots each, for 4 × 40 stainless pan-head wood screws), and a shelf along its bottom.
  - The controller board sits on four M2 standoffs on the plate, components facing the back. The Mini560 stands on the board. The two Wago 221-413s sit on the plate below the board.
  - The shelf's 3.5mm floor carries the SP16 panel socket (12V run in, firing down: D hole 16.5mm with a flat at 15.3mm, rear nut) and the PG7 gland (pixel lead out), plus a 3mm drip hole.
  - The **plug** is an 8mm-thick rim running 16mm back from the plate (top and sides) and up from the floor (sides and back), which the cover slides over. One continuous cord groove (`seal.scad`, 3.8 × 2.05mm) runs round its outside: across the top and down the sides 12mm behind the plate, then through an 8mm bend into the shelf's rim 12mm above the underside, and across the back.
- **Cover**: back, sides and a roof sloping 8° away from the tree, open at the front and the bottom, with a 1mm lead-in round its mouth. It slides on from behind; the 2.7mm cord squeezes radially between the plug and its walls (0.25mm fit each side), so the screws only hold it. Four M3 × 10 screws through its sides into heat-set inserts in the plug, in front of and below the seal line. The RP-SMA antenna bulkhead goes through its outer side wall (x = 0, away from the tree's centre), behind the plug: leave the U.FL pigtail long enough to lift the cover off and set it down beside the base.
- **Spacers**: 10mm printed tubes between the plate's flanges and the oak, so rain runs down between the tree and the box.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`, assumed 2.5mm in from the corners), the SP16 nut and thread length, the PG7 and RP-SMA sizes, the M3 insert hole (4.0mm), and the seal's squeeze. Print the coupon and the seal test first.

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
