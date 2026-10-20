# Tree boots (rough-in)

![boot](boot-preview.png)

`stair-tree-foot.scad` is parametric (every dimension at the top). The STLs are exported from it:
`openscad -o stair-tree-foot-right.stl -D 'hand="right"' stair-tree-foot.scad` (and `left`).

Two boots per tree, one at each old 17mm fixing hole in the wide end; 28 in all. Each boot:
- plugs a 16.6mm spigot into the old hole and takes a 4mm wood screw into the old pilot hole beside it (screwdriver goes in through the tunnel in the heel)
- carries the tree's bottom edge on a shelf 50mm above the ground, with a low front lip (8mm, below the bottom pixel row)
- is pegged with two 8mm × 200mm nails, one through the toe cap and one through the heel spur

## Printing (Bambu P1S)

Upright on the sole, no supports, PETG, 3 walls, 15% infill. It's hollow and open underneath (2.4mm walls, sloped roofs), with solid tubes round the nails.

Rough mass: 145–175g each, so about 4–5kg of PETG for 28 (the first solid version was ~6kg). Bambu Studio will give the exact figure. Leaner settings if needed: `clearance=40`, `wall=2`, `toe_len=56` save roughly another 10–15%.

Print one pair and test-fit it before printing all 28. Check on a real tread: hole diameter and depth, hole height above the bottom edge (44mm from the photo), pilot offset (26.5mm) and screw size.
