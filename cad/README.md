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
                              and the 14-tree storage stack                  (generated)
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
| [stair-tree-complete.FCStd](stair-tree-complete.FCStd) | **One complete tree**, on its display stands and tent poles: the tree, its 92 disks and pixels, the tree box with every bought part, the three sockets, two stands, two poles and four pole caps. Every part is an App::Link to its master, so it always shows the masters as saved | generated (`tools/cad_assembly.py`) |
| [stair-tree-choir.FCStd](stair-tree-choir.FCStd) | **The whole setup**: Site A's 6 trees on their stands and poles and the site box, and the 14-tree storage stack, all linking the complete tree above | generated |
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
| [tree-mounts.FCStd](parts/tree-mounts.FCStd) | v2 (17 Nov 2026): Socket (3 per tree: solid, crush ribs, screwed up into the edge, a dovetail rail), Stand (show, 2 per tree, latches, a tent pole through it), PoleCap (4 per tree, ribbed bore, peg at 45°), Tower (storage, 3 per tree, prints on its back, latches), DovetailCoupon, DrillJig | `tree-socket.stl`, `tree-stand.stl`, `tree-pole-cap.stl`, `tree-tower.stl`, `tower-plate.3mf`, `tree-dovetail-coupon.stl`, `tree-drill-jig.stl` |
| [psu-cover.FCStd](parts/psu-cover.FCStd) | Hood over Site A's S-400-12 terminals, with the IEC inlet; RefPsu and the inlet as reference solids | `psu-hood.stl` |
| [psu-cover-lrs.FCStd](parts/psu-cover-lrs.FCStd) | The same for the LRS-350-12 (ordered again 17 Nov 2026): the inlet over the lid, a short chamber | `psu-hood-lrs.stl` |
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
- **Socket frame** (tree-mounts): x along the tree's edge (0 at the socket's centre), y out of the edge (0 at the edge), z = the tree's Z. The tower, the stand and the front pole cap are drawn in it as fitted (the cap on the front end of a `pole_l` pole centred on the tree's centre plane); the back cap is the front one turned round a vertical through that plane.
- **Tree box** (tree-box): x across the plate, y back from the plate's tree face, z up from the cover's bottom edge.
- **PSU** (psu-cover, psu-cover-lrs): x along the case from its terminal end, y across from the L (pin 1) side, z up from its base.
- **Assembly world**: Z up with the ground at 0; the show faces −Y (FreeCAD's front view).

## Part notes

### Tree mounts: socket, display stand, tent-pole feet, storage tower (Rob, 16 Nov 2026)

**v2, 17 Nov 2026**, from Rob's notes on printing and fitting v1 ([docs/v2-feedback.md](../docs/v2-feedback.md)). **One joint: a dovetail rail running front to back** (16 tall, 46 wide at its tip, 15° undercut, 58 long) on the sockets; the stands and towers carry the slot, now **0.1 a side** (v1's 0.3 gave about 1mm of play), and both **latch**. Sliced (P1S, PETG, 3 walls, 15% infill): one tree's show set (3 sockets, 2 stands, 4 caps) **210g, 6h13**; six towers **143g, 3h31**.

- **Socket** (3 per tree): **solid** (Rob). A snug U over the edge, 0.3 a side with three **crush ribs** up each leg biting 0.2 into the oak, and a full-height cove buttressing each leg. No face screws: two **5mm countersunk stainless screws go up through the rail into the tree's edge** (5 × 45 in the bottom sockets, 5 × 35 in the top one, clear of the old stair pilot holes) (end grain, pre-drilled: Rob), on the centre plane, ±14mm either side of the pixel straight above the socket, heads in counterbores below the rail's tip, 37mm and 27mm in the oak (3mm+ of oak to the pixel holes, [docs/cad-checks.md](../docs/cad-checks.md)). A 0.9mm groove across the rail's tip, 5.2mm in from its back end, takes the latch. Two on the bottom edge (straight under the base row's 2nd and 11th pixels, 270mm apart), one on the top edge (under the apex pixel).
- **Drilling jig** (1): drops over the edge, snug, with a hole that sits over the dome of the pixel straight above the socket (22mm in: CNC'd, so the same on every tree) and two guides for the 3.5mm pilots. Every tree gets its sockets in the same place, which is what makes the stack line up.
- **Display stand** (2 per tree): as v1 (100mm lift, A-frame, diamond windows), with the pole hole a **slide fit (11.2)** on the 11.0 pole, and a **latch**: a tongue in the slot's floor, cut free on three sides, with a 0.8mm bump that clicks into the rail's groove when the tree is home. The tongue's free end is cut at 45°, so it prints back end down with no supports.
- **Pole cap** (4 per tree): the bore is a teardrop (11.6) with **three crush ribs** gripping to 10.8 (Rob: tighter in the feet). The **peg goes in at 45°**, its tip under the tree (good tent pitching), through a boss that holds it at the angle; its axis meets the grass 11mm past the pole's end.
- **Storage tower** (3 per tree): **prints on its back** (Rob: v1 fell over printing upright), so the bed sees 54 × 127. The tab on top sits flush with the back face and is a 15° dovetail, narrowest at the back, so it slides down into a matching notch under the tower above (open at the back) and is held both ways. It latches like the stand; the column is solid behind the tongue, so there's a **window right through to the back face**: the tongue flexes into it, and its small support (on the build plate only, up through the window) snaps out through it. 115mm pitch as before.
- **Plates:** `print/tree-plate.3mf` (one tree's show set, nine objects, clear of the P1S's cutter corner) and `print/tower-plate.3mf` (six towers on their backs: four along the back, two across the front), both sliced by `make slice`; the tower plate is sliced with support on the build plate only and bridges unsupported. Sizes and weights in [print/README.md](../print/README.md).
- **Test first:** print the **dovetail coupon** (the back 30mm of a stand: its stop and latch, 11g), one **socket** and the **jig** (14g). The coupon should slide onto the rail by hand with no rock and click home; tune `clr` and `latch_h` in the sheet. Push a pole into a cap (`cap_rib_id`) and through a stand (`pole_d`). Try the socket's grip on a real tread (`rib_in`) and the jig on a pixel (`jig_dome_d`).
- The fillet and chamfer sizes are set in [tools/cad_parts.py](../tools/cad_parts.py) when the part is built, not in the sheet; the sizes they round follow the sheet.

### PSU hood with IEC inlet (Rob, 15 Nov 2026; S-400-12, inlet on top, 16 Nov 2026)

For Site A's **S-400-12**. The LRS-350-12 it was drawn for on 15 Nov arrived as an LRS-350-24, so the S-400 carries the show (Rob, 16 Nov 2026; the LRS version is in git at edd7308). Case 217 × 114 × 50 (Rob's size); the rest read off his photos of 16 Nov against a ruler: the terminals sit in an open recess at the end, the lid stopping about 20mm in (`lid_x`) and its top vents starting at about 29; facing the terminals, left to right, ADJ, +V × 3, −V × 3, earth, N, L (earth about 38mm from the L side, the first −V about 47); threaded M4 side holes 32mm in and 38mm up on both sides. The fan is at the far end and the 115/230V switch about 150mm along the ADJ side, both clear of the hood.

- A box over the terminal end, 54mm tall (just over the case), with a wiring chamber beyond the case and a partition between earth and −V (`rib_y` 42.5), so the mains side and the 12V side are separate. The partition runs floor to roof in the chamber and hangs on 10mm into the terminal recess, down to 25mm above the base (`rib_z`), over the terminal block.
- The fused, switched **IEC C14 inlet** (the 3-in-1 module: cut-out **48.5 × 28**, Rob 17 Nov 2026, off the printed hood (the drawing's 47.3 × 27.4 was too small); two M3 holes 40 apart across it, flange 54.4 × 49.2 from the drawing). The bigger cut-out still fits the 56mm chamber, so the hood is no longer. A hood printed before 17 Nov can be filed out: 0.6mm off each end, 0.3mm off each side sits **in the roof** over the chamber's mains side (Rob, 16 Nov 2026), its long side along the hood; the C13 plug goes in from above. The chamber's mains side is closed: floor, L side wall, end wall, partition, roof. Mains arrives on a C13 lead; nothing is wired to a loose mains cable.
- **12V leads go straight onto the PSU's terminals** (Rob, 16 Nov 2026) and run out along the box floor: the chamber has no floor on its 12V side and a 50 × 22mm notch in the end wall, open at the bottom, so the hood drops on over leads that are already wired.
- Over the case the roof and full sides stop at 26mm (`roof_l`), past the lid's edge and short of its vents; past that only **side tabs** go on (z 8–44, to 42mm) to reach the side holes, staying under the lid's side vents. The holes in the tabs are short **slots** (±2.5mm along, ±0.75mm up and down, since the positions come from photos). Two **M4 × 6 with washers** (about 2mm into the case; never longer).
- Vent slots in the 12V side wall over the case's own side vents by the terminals (the mains side wall is left closed, so the case's vents on that side are covered). A slot in the roof over the ADJ pot.
- Prints standing on its end wall with no supports. PETG, 4 walls, 40% infill. About 80cm³.
- **This puts mains inside a printed part** (the brief's old rule said never; Rob chose the inlet, 15 Nov 2026). See the safety notes in [docs/site-box-wiring.html](../docs/site-box-wiring.html): earth from the inlet to FG, insulated crimps on every mains tab, set the PSU's 115/230V switch to 230V before fitting the hood.
- **Check before printing** (all in the sheet): the terminal positions (the partition, `rib_y`, must fall between earth and the first −V, and the terminal block must stay under `rib_z`), where the lid stops (`lid_x`), the side holes (`side_x`, `side_z`), the ADJ pot (`adj_x`, `adj_y`), and the inlet's body depth behind the panel and its tabs (about 17 + 8mm from the drawing: it has to clear the chamber floor, 54 − 25 = 29mm up). Leave room above the hood for the C13 plug under the DRiBOX lid (an angled C13 helps).

### PSU hood for the LRS-350-12 (Rob, 17 Nov 2026)

Rob ordered the LRS-350-12 again, so it has its own hood, [psu-cover-lrs.FCStd](parts/psu-cover-lrs.FCStd), with the same inlet (48.5 × 28 cut-out), built to stick out as little as possible past the PSU's end. Sizes from the Mean Well drawing (case 207A, Rob sent it 17 Nov): 215 × 115 × 30, terminals 1–9 on the end at 9.5 pitch (L, N, FG, −V × 3, +V × 3), the LED and ADJ beside pin 9, M4 side holes 32.5 in and 12.5 up (5mm max into the case), the fan on the lid at the far end blowing in, the air leaving by side slots, two pairs of them near the terminals. Measure the real one.

- The 30mm case is too low for the inlet to hang in a chamber beside it: on its side wall or in the roof over a chamber, the inlet's flange and the room the leads need in front of the terminals made the chamber 50–65mm long. So the inlet sits in the roof **over the lid** (`iec_x` 25.5: its body runs 1–50mm along the case), its tabs 8mm above the lid (`spade_h`: use **90° flag spades** there), and the chamber (`cham_l` 12: 15 past the PSU's end, Rob 17 Nov) only holds the leads off the terminals, which go in on **bootlace ferrules** (forks need more room): the mains ones go up to the inlet, the 12V ones run straight out through the open floor on the 12V side and a 52 × 25 notch in the end wall, as on the S-400 hood.
- Slimmed down (Rob, 17 Nov: "the LRS hood is HUGE"): only the mains side is tall, a **turret** 60 wide and 66 tall over the inlet; the 12V side is a **low cap** 33.5 tall, 0.5 over the lid, reaching 46 along the case. A shelf at the low roof's height, from the partition to the turret's wall, shuts the chamber's 12V side off from the turret. The side walls have **windows over the case's vent slots** (the tall pair by the terminals and the small slots either side of the M4 hole), so the hood doesn't choke the fan's airflow.
- 74 long × 122 wide × 66 tall at the turret; **15mm past the PSU's end** (the S-400 hood: 59). In the DRiBOX the PSU and hood take 230mm of the 290 floor, with about 74mm over the turret for the C13 plug.
- Partition between FG and −V (`rib_y` 36.25) in the chamber; the inlet's tabs over the lid sit across that line, so take the L, N and earth leads over the lid to the chamber's mains side. Plain M4 holes (datasheet positions), M4 × 6. A slot over the ADJ pot and LED.
- **Check before printing**: the case, terminal and vent positions, and the inlet's flange (`iec_fl_l`, `iec_fl_w`: still the drawing's) and its depth behind the panel (`iec_depth` 25). The turret's height follows from `spade_h` + `iec_depth`. PETG, end wall on the bed, no supports.

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
