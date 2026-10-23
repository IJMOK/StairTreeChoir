# Enclosures (M3)

## Tree controller box

`tree-box.scad`, one per tree, sitting on the tower of the control boot (`feet/`). Sizes shared with the boot are in `tree-box-params.scad`; change them there, then re-export the box and the left boot together.

```
openscad -o tree-box-box.stl    -D 'part="box"'    tree-box.scad   # PETG, front face on the bed, no supports
openscad -o tree-box-lid.stl    -D 'part="lid"'    tree-box.scad   # PETG, flat
openscad -o tree-box-gasket.stl -D 'part="gasket"' tree-box.scad   # TPU, flat
```

Outside 81 × 99 × 38mm (101mm wide with the ears); inside 76 × 92 × 30mm.

- **Front wall** (towards the tree): four standoffs for the 5×7cm controller board, M2 self-tapping screws. The board sits at the top, components facing the lid.
- **Below the board**: the Mini560 and the two Wago 221-413s (foam tape), and the gland nuts.
- **Floor**: PG9 (12V flex in) and PG7 (pixel lead tail out), both pointing down into the boot tower, and a 3mm drip hole.
- **Roof**: RP-SMA bulkhead for the antenna, so the dipole stands up behind the tree.
- **Lid** on the back: six M3 screws into heat-set inserts in the rim, a printed TPU gasket under it, and a rain skirt that hangs over the gasket line.
- **Ears**: four M3 screws down into inserts in the boot tower's posts.

No fuse in the box: each tree's 12V is fused at the site box, where the run starts (CLAUDE.md §4).

**Unverified until the parts arrive:** the board's hole positions (`pb_*`, assumed 2.5mm in from the corners), that the ESP32 on its headers clears 30mm, the PG9/PG7 thread sizes, the RP-SMA bulkhead thread, and the M3 insert hole size (4.0mm).

## Site box

Not started: Pi, USB sound card, PAM8610, 5V buck for the Pi, fuse block for the tree runs, router if wanted. The Mean Well PSU (IP67) sits outside it; mains never enters a printed box.
