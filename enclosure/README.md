# Enclosures (M3)

## Tree controller box

`tree-box.scad`, one per tree, sitting on the tower of the control boot (`feet/`). Sizes shared with the boot are in `tree-box-params.scad`; change them there, then re-export the box and the left boot together.

```
openscad -o tree-box-box.stl    -D 'part="box"'    tree-box.scad   # PETG, front face on the bed, no supports
openscad -o tree-box-lid.stl    -D 'part="lid"'    tree-box.scad   # PETG, flat
```

Outside 96 × 99 × 37mm (116mm wide with the ears); inside 91 × 92 × 30mm.

- **Front wall** (towards the tree): four standoffs for the 5×7cm controller board, M2 self-tapping screws. The board sits at the top, components facing the lid.
- **Below the board**: the Mini560 and the two Wago 221-413s (foam tape), and the gland nuts.
- **Floor**: PG9 (12V flex in) and PG7 (pixel lead tail out), both pointing down into the boot tower, and a 3mm drip hole.
- **Roof**: RP-SMA bulkhead for the antenna, so the dipole stands up behind the tree.
- **Lid** on the back: six M3 screws into heat-set inserts near the rim's outer edge; 2.7mm rubber cord in a groove in the lid (`seal.scad`: 3.8 × 2.05mm, ~25% squeeze, superglue the butt joint) presses on the flat rim inside the screws; a rain skirt hangs over the joint. The rim opening is 72 × 73mm, so the 70 × 50mm board goes in flat.
- **Ears**: four M3 screws down into inserts in the boot tower's posts.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`, assumed 2.5mm in from the corners), that the ESP32 on its headers clears 30mm, the PG9/PG7 thread sizes, the RP-SMA bulkhead thread, and the M3 insert hole size (4.0mm).

## Site box

`site-box.scad`, one per site: the show player and the 12V distribution. Wiring per site: [electronics/site-wiring.md](../electronics/site-wiring.md).

```
openscad -o site-box-6-trees.stl -D 'part="box"' -D 'trees=6' site-box.scad   # also 4 and 2: same box, fewer glands
openscad -o site-box-lid.stl     -D 'part="lid"'    site-box.scad
```

Outside 236 × 196 × 72mm (with lid); inside 230 × 190 × 64mm. Upright wall box: screw it to a post or fence through the lugs top and bottom, lid on the front, every cable through the floor.

- **Back wall**: Pi standoffs (Raspberry Pi 58 × 49mm M2.5 pattern, Pi 3 and Pi 5 alike) top left; a 30mm grid of zip-tie anchors for the router, 12V→5V buck, PAM8610, USB sound card, Wagos and inline fuse holders. Their sizes aren't confirmed, so lay the real parts out on the wall and tie them where they fit.
- **Floor**: PG9 per PSU input, PG9 per tree run, PG7 for the speaker (two rows for a 6-tree site), 3mm drip hole.
- **Lid**: eight M3 screws into heat-set inserts, 2.7mm rubber cord in the lid groove (`seal.scad`), rain skirt.
- **12V inside**: each PSU's input goes to its own Wago pair (+ and −) and from there through its own inline 5A blade fuses to its two tree runs. Never join two PSUs' +12V. PSU 1 also feeds the player through a 3A fuse (buck → Pi; PAM8610 straight off 12V). The negatives may be joined.
- The Mean Well PSUs stand outside, beside the box (IP67); mains never enters it.

**Unverified:** gland threads, M3 insert hole, and that the router, buck and amp fit the 64mm depth. A Pi 5 needs a 5V 5A buck.
