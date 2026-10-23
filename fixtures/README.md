# CNC fixtures

`step-clamp.scad`: printed hold-down clamp for the bed's channel-strut rails, M6 bolt into a strut channel nut. Print 4 clamps and 4 washers in PETG; the clamp prints on its side (as exported), 4 walls, 40% infill.

```
openscad -o step-clamp.stl step-clamp.scad
openscad -o step-clamp-washer.stl -D 'part="washer"' step-clamp.scad
```

`work_h` (30) is the top of the tread above whatever the heel stands on. If the heel stands on the strut and the tread sits on an MDF sheet, add the MDF thickness. The nose grips 12mm of the edge; the pixel holes start 16mm in. How the clamps are used: docs/cnc-cutting.md.
