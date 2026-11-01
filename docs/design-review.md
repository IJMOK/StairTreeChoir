# Design review, 1 Nov 2026

A review of the tree design from the source, the data and the WLED and FPP code. Nothing here has been changed in the design: every item is Rob's to decide. Nothing was tested on hardware, and the OpenSCAD solids weren't rendered, so the sizes are worked out from the parameters. Figures marked "estimate" are engineering estimates.

Scope is December 2026: 6 trees at Site A.

## Fix before the first show

### Nothing to stand the trees on

The boots are parked and nothing replaces them. A finished tree is about 5kg (estimate) with its centre of area 356mm above the base, and on its own base it tips at about 3 m/s of wind. A gust of 20–30 m/s gives about 26–87 Nm at the base (estimate), which weight alone can't resist. It needs a staked post or similar, designed for about 130 Nm. Standoffs on the back have to miss pixels 64, 71 and 77 at x = 191. The bottom edge also needs keeping off the grass.

This sits at the top because it holds up other items: the build guide's stage 7 and final assembly steps, the bottom-edge height, and possibly the box position.

### Tree box has no position

Nothing fixes where the box goes (`gen_printed.py` says "not placed yet"; `wiring.html` says "low down"). With 6mm of margin for the leads there are two windows:

- **Between the eyes and the lip (recommended):** the plate's x = 0 edge at tree x 113–182, centred at about 147, cover bottom at y 600–640 from the top. Screws clear pixels by 36mm or more, no pixel leads cross it, and it is hidden from the front. The pixel lead to node 1 is about 310mm.
- **Low band:** x 73–222, cover bottom at y ≈ 858, with only about 3mm of vertical play, and the antenna tip reaches 88mm below the tree.

### WLED config (`tools/gen_site_config.py:262`)

Both come from the WLED 16.0.1 source and the generated config; neither has been seen on a real tree. Trees 1–9 were flashed with this config, so they need it applied again.

1. **Idle trees go orange.** The config doesn't set `def.on`, so WLED boots on, orange, at brightness 128. WLED leaves realtime 2.5 s after the last frame, and FPP stops sending once nothing is playing unless `alwaysTransmit` is set (the repo never sets it; its default wasn't checked). So expect an orange flash in the 4 s pauses, and orange trees after Lights Out, at about 0.6A each. Fix: add `"def": {"on": false}` and set `alwaysTransmit`, then bench it.
2. **The show runs at about half brightness.** `if.live.maxbri` isn't set, so DDP frames are scaled by brightness 128. It also hides the problem below, because the current tests read low. Fix: `"if": {"live": {"en": true, "maxbri": true}}`, and do the current tests at 255.

### Pixel current is unmeasured

The 0.3W (25mA) per pixel figure has no source in the repo, and the limiter, fuses and voltage drop all rest on it. Forum reports for Ray Wu 12V 12mm pixels range from 30mA to 60mA. At 50mA full white is 4.6A, and because the limiter believes 25mA it would allow about 3.9A, over the 3A fuse. At brightness 128 that same tree reads about 2.3A, exactly what the test expects. Fix: measure one pixel at 255 with the limiter off, then set `LED_MA` and recheck the cap and the fuse. If 25mA holds, the arithmetic is fine: the limit lands at about 1.93A.

### Mains

- The test checklist has no check before first mains for the S-400-12's 230V switch, plug earth to case continuity, or L and N. They appear only in the build guide and `wiring.html`. The switch is a one-shot PSU killer.
- The BOM has no cord grip, and no forks or ferrules for the PSU's screw terminals, and the grip in `wiring.html` is on a plate that isn't designed. A pulled lead could put live on the 12V wiring. Add an anchored lead with crimped ends and the earth longest.
- CLAUDE.md §7 bans mains in a printed enclosure, while §4 puts the terminals under a printed hood that is open underneath with unverified sizes. Either state the exception or use a bought shroud.

## Fix on the next tree box print

| Item | Evidence | Fix |
|---|---|---|
| Mounting slots run the wrong way | `tree-box.scad:233` slots are vertical, along the grain, which barely moves. Oak moves across the grain, about 1–3mm over the 102mm screw span (estimate), against ±0.3 of play | Horizontal slots on one column |
| M3 × 10 bottoms out | The tip reaches 7.8mm and the hole ends at 6.5mm. The cover stops about 0.9mm short, so the lower seal gets no squeeze | M3 × 8 (`bom.md:114`) |
| Ears barely clear washers | `ear_w` predates the wrap: a Ø9 washer clears the cover by 0.35mm | Widen the ears 3mm |
| Coupon doesn't match the base | The coupon prints the holes vertical, the base prints them horizontal | Print the coupon on edge |
| No home for the Wagos | No retention feature. The modelled ports sit 1mm from the SP16 and 1.5mm from each other | Stack or turn them, with 20mm of wire room |
| No strain relief on the SP17 | 100N at 65mm is 6.5 Nm into a 3.5mm shelf with the layers across the load | Clip the flex to the post |

## Check when the parts are in hand

- **Pixel leads:** the 59→60 and 80→81 jumps are 195mm and 224mm, and the leads are probably 76–102mm. Plan two splices. About 4.7m of slack has no way of being held.
- **Pixel disk chamfer:** `pixel-disk.scad:52` chamfers the lip's back edge, where the clips grip. The test strip should show whether the clips still seat, or whether it needs removing to keep the full 2mm land.
- **Glue:** `cnc-cutting.md:66` has hot glue on oiled wood, and the hole grows 0.2–0.6mm across the grain. Exterior PU or MS in bare counterbores, before oiling, is safer.
- **Old finish:** the photos look lacquered, with residue bands at both ends, so oil may not soak in. Confirm the species and strip first. Seal the end grain harder than oil, especially by the 12 bottom holes and node 36, 12.5mm from it.
- **Cover screw:** the cord force is about 200–480N through one M3 (estimate), so expect creep in the PETG under the head. Leave the seal test loaded for a few days.
- **First controller board:** the checklist catches the 5V move but not a leftover GND wire on F13 (now 3V3) or data on Q13 (now IO14). Meter F13, X3 and Q13 before fitting the ESP32.
- **Board shorts:** L14–L15 (data) sits beside M14–M15 (GND), so meter it. README step 2 also fills the U1 and ESP32 holes with solder before the parts go in.
- **Player fuse:** the Pi (about 1.2A) plus the amp at clipping (about 1.7A, estimate) nears the 3A fuse, and a blown fuse stops the show. Give the amp its own way.
- **Site box:** heat looks fine in December (about 20K rise, estimate). Condensation on the IP20 mesh PSU at ground level is the bigger worry, so mount it high. Check the DRiBOX seals take all 10 cables.
- **Mini560 EN pad:** reports conflict on whether it may float. **S-400-12 inrush** against the 3A plug fuse: no datasheet found. Bench both.
- **RP-SMA:** the model has the nut inside, but many pigtails take it outside. It sets the recess.
- **Clip flare:** a clearance above about Ø16 leaves too little disk wall.
- **Pilot holes** for the 4 × 40 screws aren't documented: 2.5–3mm × 22mm.

## Looks fine

- **Schematic:** the 74AHCT125 pins, /OE, spare ties, R1, R2, C1, C2 and GPIO16. Netlist, drawing and `connections.md` agree, and regenerating gives byte-identical files.
- **Power:** S-400-12 capacity, 11.5V at the tree, 0.75mm² on a 3A fuse if 25mA holds, the Wago 0V split, and the data ground. The limiter does apply to DDP.
- **Oak:** 5.4mm minimum web between counterbores (9.4mm between holes), and 4.9mm from clearance holes to the old holes. Nothing loads them, and 45% holes at the lip row is still only about 1.4 MPa at 30 m/s.
- **Wood screws:** 24mm of bite and 6mm of front skin.
- **Tree box:** the roof and drip path, tool access for the rear nuts and the 45° screw, and the 2.4mm Mini560 clearance (the swing moves away from it). Params, scad and DIMS agree on the fittings. Pixel holes drain out of the back.

## NX

`cad/` held three old imports of the tree box and none of them was current, including the set that commit 0707947 calls wrap-round: it's the clip-on cover from 30 Oct. All three are now in [archive/](../archive/README.md). Import `cad/tree-box-assembly.step` to see the real design; with the old names gone, NX should keep the plain part names.

## Docs still out of date

These describe dead designs. They aren't fixed yet, mostly because they depend on the stand decision above. Generated files are fixed in their generator, then rerun.

| Where | What's wrong |
|---|---|
| `docs/build-guide.md` | Lines 6, 29, 193–194: PSUs beside the box, PG9 glands. Lines 19, 56, 85–87, 103–114, 201, 204: boots, towers. Lines 34, 36: box and lid, printed site boxes. Line 90: 14 + 2 boards. Line 129: Site A Pi 5 (it's the Pi 3). Line 133: wrong § reference. Line 153: outdoor Cat6 (flat patch lead). Line 163: flash from `tools/wled_flash.py`. Lines 169, 173: M5 "not written yet" |
| `docs/test-checklist.md` | Lines 11, 23: DIP socket. Lines 54: O shape. Lines 66–67, 70, 73, 76, 78: lid, drip hole, boots, glands. Line 71: antenna fires down, not up |
| `docs/bom.md` | Lines 14–22, 85–91: 16 boards (10 bought, none spare). Lines 107, 119–120: lid-era fasteners and boot-only screws and nails. Line 128: spare ESP32 |
| `docs/webcam.md` | Lines 21–22, 26, 38, 99, 138: router outdoors, Site A Pi 5, spare boards, Cudy not in place |
| `docs/wiring.html` | Line 99: clip-on, and the tree box drawing shows the old box. Line 314: negative bus. Line 451: outdoor Cat6. It is a hand-made copy of the artifact |
| `docs/research.md` | Line 33: ha-fpp. Lines 5–17, 41–49: the pair-kit design |
| `docs/folders.md` | Line 42: Piper voices (ElevenLabs now) |
| `electronics/README.md` | Lines 80, 87: Site A router fuse, LRS-200 (it's the S-400-12, 14.1A of 33A) |
| `feet/README.md` | Banner is fine, but the text under it describes the tower |
| `wled/README.md` | Lines 34–38: pixels "due 25–31 Oct". Lines 38, 56, 93: limiter "not set" and "assumes 5V". `def`/`maxbri` when they are fixed |
| `xlights/README.md` | Lines 12–15: old mouth shapes (use the table in CLAUDE.md §3) |
| `CLAUDE.md` | Lines 49, 55, 79, 89, 145, 182: boots. Line 83: sockets, 16 boards. Line 88: Site A LRS. Line 90: router in the box. Line 148: header spacing is confirmed. Line 165: ha-fpp (MQTT is live). Line 179: DIY is decided. Line 199: Piper. §6 and `docs/folders.md` also omit most of `tools/` |
| `feet/stair-tree-foot.scad` | No parked banner, describes the tower |
| `tools/gen_controller.py:58` | C1 is 10V, not "16V+" |
| `tools/gen_site_wiring.py` | "LRS PSU" for Site A; SP16 "in the floor" (it's the shelf) |
| `tools/gen_components.py` | The terminal is marked not in hand (Rob found KF2EDG). Comments at 19–21 and 275 |
| `tools/gen_printed.py` | The kit doesn't place the tree box |
