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
| [tree-mounts.FCStd](parts/tree-mounts.FCStd) | Socket (3 per tree: screwed both sides, a dovetail rail), Stand (show, 2 per tree, a tent pole through it), PoleCap (4 per tree, pegged), Tower (storage, 3 per tree), DovetailCoupon | `tree-socket.stl`, `tree-stand.stl`, `tree-pole-cap.stl`, `tree-tower.stl`, `tower-plate.3mf`, `tree-dovetail-coupon.stl` |
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

Replaced the boots (15 Nov 2026). **One joint: a dovetail rail running front to back**, on the sockets; the stands and towers carry the slot. On 16 Nov 2026 Rob dropped the ski halves and then split the chunky towers (a colossal amount of material and print time for what they were) into two parts, each with one job: a **display stand** for the show, standing the tree on **11mm fibreglass tent poles**, and a slim **storage tower**. Weighed in the slicer (P1S, PETG, 3 walls, 15% infill), one tree's show set is about **200g** (3 sockets 16g each, 2 stands 54g, 4 caps 11g) and its storage towers about **115g** (3 × 38g), against about 745g for the sockets, ski halves and towers of the morning.

- **Socket** (3 per tree, 16g): a U over the edge with a **full-height cove** buttressing each leg from the rail to its top, screwed through both legs (two 4 × 16 countersunk stainless each side, the front pair offset 8mm along the edge from the back pair; each goes 12.5mm into the 30mm oak, so they can't meet). The screws sit in **counterbores** through the coves, heads flush on the leg faces, 5mm in from the edge, clear of the pixel holes and the leads ([docs/cad-checks.md](../docs/cad-checks.md)). Under the edge a **dovetail rail** 16mm tall, 46mm wide at its tip with a 15° undercut, 58mm front to back (14mm past each face), cored from its tip face. It can't pull off downwards or sideways, only slide along. Two on the bottom edge (centres 55.9mm in from each side, 270mm apart), one on the top edge. Unchanged on 16 Nov.
- **Display stand** (2 per tree, on the bottom sockets, 54g, 1h53m): slides onto the rail from the front to a stop at the back. The tree's bottom edge stands **100mm** off the grass (`lift`; Rob: at least 50, ideally 100; 75 would only save 5g). Across, it's an A-frame: the slot block on top (54 wide, 62.5 long), two 2.4mm legs slanting in to the **pole tube** along the grass (the pole's axis 9.8mm up, on a flat foot), so the tree can't rack sideways. The legs have a lattice of 45° diamond windows (`win_h`, `win_s`). The pole tube runs on 20mm past the front (`tube_ext`) for a longer grip on the pole: 82.5mm in all. Prints upright, back end down, with no supports: every face is vertical or a 45° diamond. The window lattice is laid out when the builder runs, so after changing `lift` or the window sizes rerun it ([tools/cad_parts.py](../tools/cad_parts.py)).
- **Tent poles** (bought, 2 per tree): 11mm fibreglass, 400mm each (`pole_l`; any length works, and longer gives a wider stance), front to back through each stand's tube with a **pole cap** on each end. One peg through each cap (4 per tree) holds the poles down, and the poles hold the stands down. The pegs are 429mm apart front to back and a foot covers 469mm (the skis covered 380). The holes are `pole_d` 11.6, so a **ferrule won't go through**: use plain lengths, ferrules cut off. Fibreglass splinters when cut: tape round the cut, use a fine hacksaw, sand the ends, wear gloves.
- **Pole cap** (4 per tree, 11g): a 20mm-wide body the pole pushes 25mm into, with a 3mm end wall, standing on a **pad** 40mm wide and 6mm thick (Rob, 16 Nov 2026: bigger, for stability) that runs 4mm past the body's inner end and on past the peg, its end a half round centred on the peg. The **peg hole** is drawn Ø9.4 so it prints at least 9mm, with a 1mm countersink, 7mm clear of the end wall so a peg's head sits flat on the pad. The pole sits at the stand's height, so it runs level (it's lower than the pad's top, so the bore runs on through the pad's lead as a channel). Rounded all over except the sole: 3mm on the body, a 2mm fillet where it stands on the pad, 2.5mm round the pad's top edge. The bore has a teardrop roof (it prints lying down) and a lead-in; so do both ends of the stand's pole tube.
- **Unproven:** nothing but friction holds a stand on its pole or the rail in its stand front to back (the skis' stakes used to lock the rail). A gust tips the tree, which binds both joints across their lengths, so it should stay put; if a tree creeps in testing, a cable tie on the pole either side of each stand stops it on the pole, and a cross pin through the stand and rail is the next change (Rob: not yet).
- **Storage tower** (3 per tree, every socket, 38g, 2h16m): storage only, so it's slim: 54 wide, **26mm deep** (from 56–67), and still the stack's **115mm pitch** long (Rob: the stack stays as it was). The trees lie face up; each tower's slot is open at the top and stopped at the bottom, so a tree drops onto its three towers and rests on the stops. A **tab** on top (30 × 6, 12 tall, tapered), behind the slot (the tree's rail fills the slot to the top in storage), drops into a **pocket** under the tower above. Below the rail's stop the tower slims to the pocket and its 2mm walls, flaring out to the full section at 45°. Prints upright, tab up, no supports (the pocket's roof bridges 7mm). The tree box under each tree clears the pixels below by 16mm. 14 trees stand about 1.62m.
- **Plates:** `print/tree-plate.3mf` is one tree's show set (3 sockets across the front, clear of the 18 × 28mm corner the P1S keeps for its filament cutter; the 2 stands upright behind them; the 4 caps beside the stands) as nine separate objects, and `print/tree-plate.gcode.3mf` is it sliced for the P1S in PETG (`make slice`): open it in Bambu Studio and send it. `print/tower-plate.3mf` is six storage towers (two trees), sliced the same way; print those any time before the season ends. Sizes, times and weights are in [print/README.md](../print/README.md).
- Printing (all PETG, no supports): sockets rail down, legs up; stands upright, back end down; caps sole down; towers upright, tab up.
- **Test first:** print one socket and the **dovetail coupon** (`tree-dovetail-coupon.stl`, the front 20mm of a stand's slot block). It should slide onto the rail by hand with no rock; tune `clr` (0.3 a side) in the sheet. Push a pole into a cap (tune `pole_d`). Check the channel on a real tread (`fit`, 0.8 total) and the screw positions against your tree.
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

Rob ordered the LRS-350-12 again, so it has its own hood, [psu-cover-lrs.FCStd](parts/psu-cover-lrs.FCStd), with the same inlet (48.5 × 28 cut-out), built to stick out as little as possible past the PSU's end. Sizes from the Mean Well datasheet (215 × 115 × 30, terminals 1–9 on the end at 9.5 pitch: L, N, FG, −V × 3, +V × 3; M4 side holes 32.5 in, 12.5 up): measure the real one.

- The 30mm case is too low for the inlet to hang in a chamber beside it: on its side wall or in the roof over a chamber, the inlet's flange and the room the leads need in front of the terminals made the chamber 50–65mm long. So the inlet sits **in the roof over the lid** (`iec_x` 25.5: its body runs 1–50mm along the case), its tabs 14mm above the lid (`spade_h`) for insulated spades, and the chamber (`cham_l` 24) only holds the leads off the terminals: the mains ones bend up to the inlet, and the 12V ones run straight out through the open floor on the 12V side and a 52 × 30 notch in the end wall, as on the S-400 hood.
- 87 long × 122 × 72 tall; **27mm past the PSU's end** (the S-400 hood: 59; the 15 Nov LRS hood with the inlet on its side: 53). In the DRiBOX, the PSU and hood take 242mm of the 290 floor and leave about 68mm over the hood for the C13 plug.
- Partition between FG and −V (`rib_y` 36.25) in the chamber; the inlet's tabs over the lid sit across that line, so take the L, N and earth leads over the lid to the chamber's mains side. Plain M4 holes (datasheet positions), M4 × 6. Vents over the case's side vents on the 12V side, a slot over the ADJ pot.
- **Check before printing**: the case and terminal positions, and the inlet's flange (`iec_fl_l`, `iec_fl_w`: still the drawing's) and its depth behind the panel (`iec_depth` 25). The hood's height follows from `spade_h` + `iec_depth`. About 84cm³, PETG, end wall on the bed, no supports.

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
