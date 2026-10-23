# CNC fixtures

`step-clamp.scad`: printed hold-down clamp for the bed's channel-strut rails, M6 bolt into a strut channel nut. Print 4 clamps and 4 washers in PETG; the clamp prints on its side (as exported), 4 walls, 40% infill.

```
openscad -o step-clamp.stl step-clamp.scad
openscad -o step-clamp-washer.stl -D 'part="washer"' step-clamp.scad
```

The heel stands on the MDF topper; the tread sits on a sacrificial sheet (`spoil_t`, default 6mm: set yours before printing). The strut (41×21 lipped steel, Unistrut type) is ~4mm below the topper and takes M6 spring channel nuts; the console echo gives the bolt length (69mm for a 6mm sheet: use M6 × 70; up to ~10mm longer is fine, the channel has room below the nut). The nose grips 12mm of the edge; the pixel holes start 16mm in. How the clamps are used: docs/cnc-cutting.md.
