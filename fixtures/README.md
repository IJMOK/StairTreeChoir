# CNC fixtures

`step-clamp.scad`: printed hold-down clamp for the bed's channel-strut rails, M6 bolt into a strut channel nut. Print 4 clamps and 4 washers in PETG; the clamp prints on its side (as exported), 4 walls, 40% infill.

```
openscad -o step-clamp.stl step-clamp.scad
openscad -o step-clamp-washer.stl -D 'part="washer"' step-clamp.scad
```

The heel stands on the MDF topper; the tread sits on a sacrificial sheet (`spoil_t`, default 6mm: set yours before printing). The strut is ~4mm below the topper; the console echo gives the M6 bolt length (64mm for a 6mm sheet: use M6 × 65). The nose grips 12mm of the edge; the pixel holes start 16mm in. How the clamps are used: docs/cnc-cutting.md.
