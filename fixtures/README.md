# CNC fixtures

`step-clamp.scad`: printed hold-down clamp for the bed's channel-strut rails, M6 bolt into a strut channel nut. Print 4 clamps and 4 washers in PETG; the clamp prints on its side (as exported), 4 walls, 40% infill.

```
openscad -o step-clamp.stl step-clamp.scad
openscad -o step-clamp-washer.stl -D 'part="washer"' step-clamp.scad
```

The heel stands on the MDF topper; the tread sits on a sacrificial sheet (`spoil_t`, default 6mm: set yours before printing). The strut (41×21 lipped steel, Unistrut type) is ~4mm below the topper and takes M6 spring channel nuts; the console echo gives the bolt length (69mm for a 6mm sheet: use M6 × 70; up to ~10mm longer is fine, the channel has room below the nut). On the MDF fixture plate (Rob, 25 Oct 2026) set `spoil_t` to the plate less its 4mm pocket: 14mm for 18mm MDF (bolt 77mm: M6 × 80). The nose grips 12mm of the edge; the pixel counterbores start ~12.5mm in, so set the clamp so it overlaps no more than 10mm, between pixels where you can. How the clamps are used: docs/cnc-cutting.md.

`pixel-disk.scad`: printed retaining disk for the 12mm bullet pixels (OD 18.5, 6mm thick: a 2mm front lip with bore `bore`, default 12.0, then a Ø15 relief for the clips). It sits flush in each hole's Ø19 × 6mm front counterbore, glued with hot glue (or CA/epoxy) through the 3 notches on its edge (`notches = 0` for none); the bullet pushes in from the front, its flange rests on the disk and the clips snap behind the lip into the relief. The 0.4mm chamfer on the lip's back edge leads the clips through. A tree needs 92. Print in PETG, flat as exported (front face on the bed), no supports, 100% infill or 4+ walls.

```
openscad -o pixel-disk.stl pixel-disk.scad
openscad -o pixel-disk-test.stl -D 'part="test"' pixel-disk.scad
```

The `plate` part (20 disks, 5 × 4) isn't kept as an STL: export it when needed, or copy the disk in the slicer. The test strip is 5 disks with bores 11.8, 11.9, 12.0, 12.1 and 12.2, joined by snap-off bridges, each labelled on a snap-off tab. Print the test strip first; put the chosen bore in tools/tree_layout.py Params.hole_dia and in this file (`bore`), then re-export the disk.
