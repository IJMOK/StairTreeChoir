# CNC fixtures

`step-clamp.scad`: printed hold-down clamp for the bed's channel-strut rails, M6 bolt into a strut channel nut. Print 4 clamps and 4 washers in PETG; the clamp prints on its side (as exported), 4 walls, 40% infill.

```
openscad -o step-clamp.stl step-clamp.scad
openscad -o step-clamp-washer.stl -D 'part="washer"' step-clamp.scad
```

The heel stands on the MDF topper; the tread sits on a sacrificial sheet (`spoil_t`, default 6mm: set yours before printing). The strut (41×21 lipped steel, Unistrut type) is ~4mm below the topper and takes M6 spring channel nuts; the console echo gives the bolt length (69mm for a 6mm sheet: use M6 × 70; up to ~10mm longer is fine, the channel has room below the nut). On the MDF fixture plate (Rob, 25 Oct 2026) set `spoil_t` to the plate less its 4mm pocket: 14mm for 18mm MDF (bolt 77mm: M6 × 80). The nose grips 12mm of the edge; the pixel counterbores start ~12.5mm in, so set the clamp so it overlaps no more than 10mm, between pixels where you can. How the clamps are used: docs/cnc-cutting.md.

`pixel-disk.scad`: printed retaining disk for the 12mm bullet pixels (4.8 thick: a 2mm front lip with bore `bore`, default 12.0, then a Ø15 relief for the clips). It's a friction fit in each hole's varnished front counterbore (measured 18.3–18.6 × 4.9, 13 Nov 2026): an Ø18.0 core with 8 crush ribs to `rib_od` (19.3, a solid fit from the rib test strip, 13 Nov 2026; 18.8 was too loose) that taper at the back so they start straight, and a 0.7 chamfer on the back outer edge to clear the varnish that pools in the corner; the bullet pushes in from the front, its flange rests on the disk and the clips snap behind the lip into the relief. The 0.4mm chamfer on the lip's back edge leads the clips through. A tree needs 92. Print in PETG, flat as exported (front face on the bed), no supports, 100% infill or 4+ walls.

```
openscad -o pixel-disk.stl pixel-disk.scad
openscad -o pixel-disk-test.stl -D 'part="test"' pixel-disk.scad
openscad -o pixel-disk-bore-test.stl -D 'part="bore-test"' pixel-disk.scad
```

The `plate` part (20 disks, 5 × 4) isn't kept as an STL: export it when needed, or copy the disk in the slicer. Two test strips, each 5 disks joined by snap-off bridges and labelled on snap-off tabs: `pixel-disk-test.stl` varies the rib diameter (18.9, 19.0, 19.1, 19.2, 19.3; bore 12.0) for the fit in the counterbore, and `pixel-disk-bore-test.stl` varies the bore (11.8 to 12.2; ribs at `rib_od`; 12.0 fitted the pixel on the first print, so it's only needed if that changes) for the fit of the pixel. Try the rib strip in the tightest and loosest holes: pick the one that presses in by thumb at 18.3 and won't turn or pull out with a pixel at 18.6. Put the choices in `rib_od` and `bore` (and the bore in tools/tree_layout.py Params.hole_dia), then re-export.
