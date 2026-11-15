# CAD

**One place, one tool.** Every part is designed in FreeCAD 1.1, and its master is a file in [parts/](parts/) (Rob, 15 Nov 2026: OpenSCAD and CadQuery retired, their last versions in [archive/](../archive/README.md)). The tread is the exception that proves the rule: its shape is data ([data/blank.json](../data/blank.json) → [data/tree-layout.json](../data/tree-layout.json)), and FreeCAD builds it from that. Everything else in this folder, and every print file in [print/](../print/README.md), is exported from those sources by one command:

```
make cad            # = python -m tools.cad   (a few minutes; needs FreeCAD 1.1)
```

## What's where

```
cad/
  stair-tree-complete.FCStd   one complete tree, as it stands in the show      (generated)
  stair-tree-choir.FCStd      the whole setup: Site A's 6 trees and site box,
                              the raised option, the 14-tree storage stack    (generated)
  stair-tree-choir.step       one tree as it stands, plus the PSU and hood    (generated)
  parts/                      THE MASTERS: one FreeCAD file per part family   (hand, in FreeCAD)
  tree/                       the tread and the CNC fixture plate, built from data/tree-layout.json
  components/                 the tree box's bought parts, in FreeCAD and STEP (generated)
  printed/                    every printed part as a STEP solid, as fitted    (generated)
  previews/                   a picture of every part and assembly             (generated)
  placements.json             where the box and sockets sit on the tree        (generated)
```

| Path | What | Edited by |
|---|---|---|
| [stair-tree-complete.FCStd](stair-tree-complete.FCStd) | **One complete tree**, standing on its skis: the tree, its 92 disks and pixels, the tree box with every bought part, the three sockets and two skis. Every part is an App::Link to its master, so it always shows the masters as saved | generated (`tools/cad_assembly.py`) |
| [stair-tree-choir.FCStd](stair-tree-choir.FCStd) | **The whole setup**: Site A's 6 trees on skis and the site box, a raised tree on towers, and the 14-tree storage stack, all linking the complete tree above | generated |
| `parts/*.FCStd` | **The masters**, one per part family (table below). Sizes in each file's `params` spreadsheet. `*-params.json` beside them are copies of the sheets for the tools and tests | **hand, in FreeCAD** |
| `tree/stair-tree.FCStd`, `stair-tree.step`, `fixture-plate.step`, `stair-tree-assembly.step` | The tread and the MDF fixture plate: the STEPs are for CAM | generated (`tools/cad_tree.py`, also run by `make all`) |
| `tree/stair-tree-cnc-layout.svg` | 2D reference of one tree's holes | generated (`tools/gen_cnc.py`) |
| `components/bought-parts.FCStd`, `components/*.step`, `components/tree-box-assembly.step` | The tree box's bought parts (stand-ins at their real envelopes, each in its own frame) and the box with them fitted; sizes, sources and fit checks in [docs/tree-box-parts.md](../docs/tree-box-parts.md) | generated (`tools/cad_components.py`) |
| `printed/*.step` | Every printed part as a STEP solid, as fitted (not laid out for printing: that's [print/](../print/README.md)) | generated |
| `previews/*.png` | Pictures of every printed part (as printed) and of the assemblies | generated |

Nothing in `cad/` is in another CAD program's format any more (15 Nov 2026). Rob's NX CAM set for the first-off tree (`tree.prt`, `fixture-plate.prt`, `Clamp.prt`, the assembly and `stair-tree.gcode`) is in [archive/nx-cam/](../archive/nx-cam/); do the CAM again from `tree/*.step` (in NX, or FreeCAD's CAM workbench).

Clearances measured on the models (screws against pixel holes, the storage stack, clashes) are in [docs/cad-checks.md](../docs/cad-checks.md), rewritten by every `make cad`.

## The masters

| Master | Parts (bodies) | Print files |
|---|---|---|
| [tree-box.FCStd](parts/tree-box.FCStd) | Tree controller box: Base, Cover, Spacer; Coupon and SealStrip/SealBar test prints | `tree-box-*.stl` |
| [tree-mounts.FCStd](parts/tree-mounts.FCStd) | Socket (3 per tree: screwed both sides, a dovetail rail), SkiHalf (show feet, 4 per tree), Tower (storage and show riser, 3 per tree), DovetailCoupon | `tree-socket.stl`, `tree-ski-half.stl`, `tree-tower.stl`, `tree-dovetail-coupon.stl` |
| [psu-cover.FCStd](parts/psu-cover.FCStd) | Hood over Site A's LRS-350-12 terminals, with the IEC inlet; RefPsu and the inlet as reference solids | `psu-hood.stl` |
| [player-pods.FCStd](parts/player-pods.FCStd) | Buck pod (base, lid) for the Pi's 12V-to-USB buck. The audio pod in it was for the PAM8610 and isn't exported (below) | `pod-buck-*.stl` |
| [pixel-disk.FCStd](parts/pixel-disk.FCStd) | The crush-rib disk that holds each bullet pixel | `pixel-disk.stl` |
| [step-clamp.FCStd](parts/step-clamp.FCStd) | CNC hold-down clamp and its washer | `step-clamp*.stl` |

### Changing a part

1. Open the master in FreeCAD, change a value in its `params` spreadsheet (mm; a note beside each says what it is and where it came from) and recompute. Sizes, positions and holes are expressions on the sheet, so the part follows. Anything that needs a new shape goes in as a new feature; keep it bound to the sheet.
2. Save.
3. `make cad`. It recomputes each master, stops if a feature is broken or a part isn't one solid, and rewrites the STLs, STEPs, previews, the assembly and the checks.
4. `make test` (the CAD tests run the geometry checks in FreeCAD).

The four masters made on 15 Nov 2026 (tree mounts, PSU hood, pixel disk, step clamp) were first built by [tools/cad_parts.py](../tools/cad_parts.py). That is only a record now: rerunning it overwrites the master and your edits, so it refuses without `force=True`.

### Frames (mm)

- **Tree** (stair-tree.FCStd, and the TreeUnit in the assembly): Z up out of the front face (front at Z = 0, back at −30), X right seen from the front, Y up the tree, origin at the bottom-left of the blank's bounding box.
- **Socket frame** (tree-mounts): x along the tree's edge (0 at the socket's centre), y out of the edge (0 at the edge), z = the tree's Z. The front ski half and the tower are drawn in it as fitted; the back half is the front one turned round a vertical through the tree's centre plane.
- **Tree box** (tree-box): x across the plate, y back from the plate's tree face, z up from the cover's bottom edge.
- **PSU** (psu-cover): x along the case from its terminal end, y across from the pin 1 side, z up from its base.
- **Assembly world**: Z up with the ground at 0; the show faces −Y (FreeCAD's front view).

## Part notes

### Tree mounts: socket, ski halves, tower (Rob, 15 Nov 2026)

Replaces the boots. **One joint everywhere: a dovetail rail running front to back.** Sockets and towers carry rails; ski halves and towers carry slots. Nothing is bolted or clipped; every edge you handle is rounded or chamfered.

- **Socket** (3 per tree, about 18cm³: the rail is cored from its tip face, 3mm flanks and ends): a U over the edge, **screwed through both legs**: two 4 × 16 countersunk stainless screws in the back leg and two in the front leg, the front pair offset 8mm along the edge from the back pair. Each goes 12.5mm into the 30mm oak, so they can't meet; all 5mm in from the edge, clear of the pixel holes and the leads ([docs/cad-checks.md](../docs/cad-checks.md)). Under the edge, a **dovetail rail** 16mm tall, 52mm wide at its tip with a 15° undercut, running 58mm front to back (14mm past each face). It can't pull off downwards or sideways, only slide along. Two on the bottom edge (centres 55.9mm in from each side, 270mm apart), one on the top edge.
- **Show:** each bottom socket takes **two ski halves** (4 per tree), one slid on from the front and one from the back until they butt under the tree; stake each half (two 8mm pegs each) and they can't slide apart, which locks the joint. A foot covers about 380mm front to back. Each half is 190mm: full size (64 × 50) for the 40mm round its slot, then slimmer and lower towards the outer end (36 wide, 24 tall), sole flat. It's a **shell** (Rob, 15 Nov 2026: 750g a tree was too much): 1.6mm walls (4 perimeters), a 2mm top skin, a web down the middle, 3mm round the dovetail slot and tubes round the stake holes, about 73cm³. The loads are small (a 5kg tree, roughly 35 N·m of tipping moment in a strong gust), so that's plenty in PETG. The tree's bottom edge stands 50mm off the grass.
- **Show, raised:** a **tower** slides onto each bottom rail lying front to back, and the ski halves slide onto the rail on the tower's outer face. The bottom edge stands 106mm off the grass.
- **Storage:** the trees lie face up; each tower's slot is open at the top and stopped at the bottom, so a tree drops onto its three towers and rests on the stops; each tower's tapered spigot drops 20mm into the tower above. Pitch 115mm: the tree box under each tree clears the pixels below by 16mm. 14 trees stand about 1.63m.
- **One plate per tree:** `print/tree-plate.stl` (and, sliced for the P2S in PETG, `print/tree-plate.gcode.3mf`: `make slice`) is one tree's show set (4 ski halves nested head to tail, 3 sockets) laid out on 160 × 251mm of the 255 plate, about 350cm³ (≈ 440g at full density).
- Printing (all PETG, no supports): sockets rail down, legs up; ski halves sole down (the cavities' flat roofs bridge under 31mm); towers upright, spigot up (vertical cores beside the bore; the outer rail's bottom end is cut back at 45°). 42 sockets, 56 ski halves, 42 towers (about 200cm³ each).
- **Test first:** print one socket and the **dovetail coupon** (`tree-dovetail-coupon.stl`, the inner 40mm of a ski half). It should slide on by hand with no rock; tune `clr` (0.3 a side) in the sheet. Check the channel on a real tread (`fit`, 0.8 total) and the screw positions against your tree.
- The fillet and chamfer sizes are set in [tools/cad_parts.py](../tools/cad_parts.py) when the part is built, not in the sheet; the sizes they round follow the sheet.

### PSU hood with IEC inlet (Rob, 15 Nov 2026)

For Site A's Mean Well **LRS-350-12** (replacing the S-400-12 and its cover). Sizes from Mean Well's datasheet (LRS-350-SPEC, 2025-09-12, case 207A): 215 × 115 × 30, terminals 1–9 at 9.5 pitch along one end (1 AC/L, 2 AC/N, 3 FG, 4–6 −V, 7–9 +V), M4 side holes 32.5mm from that end and 12.5mm up, **5mm max** into the case; a temperature-controlled fan on top, well clear of the hood.

- A box over the terminal end, one height all through (63mm), with a closed wiring chamber beyond the case (floored) and a partition between pin 3 and pin 4, so the mains side and the 12V side are separate. Two **M4 × 6** screws through its side walls into the case's side holes (3mm into the case).
- The fused, switched **IEC C14 inlet** (the 3-in-1 module in Rob's drawing: cut-out 47.3 × 27.4, two M3 holes 40 apart) sits in the mains side wall over the chamber, switch at the bottom. Mains arrives on a C13 lead; nothing is wired to a loose mains cable.
- 12V leaves through a window in the roof over the chamber's 12V side, with cable-tie slots beside it. Vent slots on the 12V side only, over the case's own side vents. A slot in the roof reaches the +V ADJ pot.
- Prints standing on its end wall with no supports. PETG, 4 walls, 40% infill.
- **This puts mains inside a printed part** (the brief's old rule said never; Rob chose the inlet, 15 Nov 2026). See the safety notes in [docs/site-box-wiring.html](../docs/site-box-wiring.html): earth from the inlet to FG, insulated crimps on every mains tab, set the PSU's 115/230V switch to 230V before fitting the hood.
- **Measure before printing:** the PSU itself (±1mm on the drawing), the terminal positions (scaled off the drawing: the partition, `rib_y`, must fall between pins 3 and 4), the ADJ pot (`adj_x`, `adj_y`), and the inlet's body depth behind the panel and its tabs (about 17 + 8mm from the drawing).

### Tree controller box

An L base plus a wrap-round cover on 10mm spacers on the back of the tree (Rob, 31 Oct 2026), placed low on the node-1 side so the 12V run's SP17 plug, screwed on under the shelf, ends at least 20mm above the tree's bottom edge. The base carries the board on four M2 heat-set standoffs, the Mini560 standing on it, two Wago 221-413s, and the SP16 socket (17mm hole, two flats 15.7mm apart), PG7 gland and RP-SMA bulkhead firing down through the 3.5mm shelf, so nothing unplugs when the cover comes off. The cover hooks over the plate's top edge, swings in, and takes one M3 × 10 at 45° into an insert in a boss on the shelf (push the insert in flush; the hole goes right through). A 2.7mm cord in a groove seals the top and sides; the bottom is open on purpose (rain doesn't fall upwards). About 117 × 53 × 110 overall. Print the coupon and the seal test first. **Unverified:** the board's hole positions, the SP16 nut and thread length, the PG7 and RP-SMA sizes, the insert holes, the cord's squeeze ([docs/tree-box-parts.md](../docs/tree-box-parts.md)).

### Player pods

The **buck pod** holds the 12V-to-USB buck that powers the Pi: USB socket flush with one end wall, 12V pair in through a slot at the other, clip-on lid (four hooks; push them in through the side windows to open), cable-tie slots in the end flanges. The **audio pod** was for the PAM8610 and the bare sound card with soldered wires; with the **XH-M541** (15 Nov 2026) the sound card plugs into the Pi and a 3.5mm lead goes to the amp's own input jack, so the pod isn't needed and isn't exported. The amp gets screwed or stuck to the site box wall when it arrives and is measured. Every pod size is read off photos: caliper the boards first (`bk_*` in the sheet).

### Pixel disk

A friction fit in each varnished counterbore (18.3–18.6 × 4.9 deep, 13 Nov 2026): an Ø18.0 core with 8 crush ribs to Ø19.3 (a solid fit from the rib test strip), tapering at the back so they start straight, a 0.7 chamfer on the back edge for the varnish fillet, 4.8 thick. A 2mm front lip with a 12.0 bore (the pixel fits; also `Params.hole_dia` in tools/tree_layout.py), a Ø15 relief behind it for the clips, a 0.4 chamfer leading them through. Front face on the bed, 100% infill. 92 a tree. The rib and bore test strips are done and archived; to try another size, change `rib_od` or `bore` and print a few singles.

### Step clamp

Hold-down for the CNC bed's channel-strut rails, M6 into a strut channel nut. The heel stands on the topper; set `spoil_t` to what the tread sits on (14 for the 18mm MDF plate less its pocket); `bolt_len` in the sheet gives the bolt (M6 × 80 on the plate). The nose grips 12mm of the edge: keep it to 10mm, between pixels. Print 4 clamps and 4 washers. The OpenSCAD version's 1mm edge bevel didn't come across. How the clamps are used: [docs/cnc-cutting.md](../docs/cnc-cutting.md).

### Site box

A bought DRiBOX Large (inside about 330 × 230 × 140 at the top, about 290 × 190 at the floor). The assembly's layout is **indicative**: the PSU and hood fill the back of the floor, the fuse box and the Pi the front strip; the amp goes on the front wall and the buck pod on the hood's roof. Measure the box and the fuse box and amp before printing anything for it.
