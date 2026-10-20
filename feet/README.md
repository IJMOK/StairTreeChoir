# Tree feet (rough-in)

`stair-tree-foot.scad` is parametric (every dimension at the top). The STLs are exported from it:
`openscad -o stair-tree-foot-right.stl -D 'hand="right"' stair-tree-foot.scad` (and `left`).

Two feet per tree, one at each old 17mm fixing hole in the wide end. Each foot:
- plugs a 16.6mm spigot into the old hole and takes a 4mm wood screw into the old pilot hole beside it
- carries the tree's bottom edge on a shelf 50mm above the ground, with a low front lip (8mm, below the bottom pixel row)
- has a sole with front and back wings, each with a hole for an 8mm × 200mm nail, clear of the gussets for the hammer

Print lying on the flat outer side, PETG, 5+ perimeters, 40%+ infill. Print one pair and test-fit before printing all 28.

To check on a real tread before printing: hole diameter and depth, hole height above the bottom edge (44mm from the photo), pilot offset (26.5mm) and pilot size.
