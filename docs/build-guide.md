# Build guide

How to build the Stair Tree Choir, in order: 14 trees, 4 sites. It is written from the other documents in this repo, which stay the source of truth for dimensions and decisions ([CLAUDE.md](../CLAUDE.md)). Where something is not decided or not yet measured, it says **TBC (Rob)**. The tick-box tests are in [test-checklist.md](test-checklist.md); each stage below says which section to run.

Two safety rules cover the whole project:
- Mains voltage never goes inside a printed box. The Mean Well PSUs stand outside, beside the site box, each on its own mains lead to an RCD-protected outdoor socket.
- Never join the +12V of two PSUs.

## 0. Overview

| Stage | What | Details |
|---|---|---|
| 1 | Buy and print | [bom.md](bom.md), [feet/](../feet/README.md), [enclosure/](../enclosure/README.md) |
| 2 | Prepare and check the treads | `data/blank.json` |
| 3 | CNC | [cnc-cutting.md](cnc-cutting.md) |
| 4 | Finish the wood | exterior oil |
| 5 | Fit the pixels | `data/tree-layout.json` |
| 6 | Build the controller board | [electronics/README.md](../electronics/README.md) |
| 7 | Boots and pegs | [feet/README.md](../feet/README.md) |
| 8 | Tree box | [enclosure/README.md](../enclosure/README.md) |
| 9 | Site box and power | [electronics/site-wiring.md](../electronics/site-wiring.md) |
| 10 | Network | router, fixed IPs |
| 11 | Provisioning | [wled/README.md](../wled/README.md), [fpp/README.md](../fpp/README.md) |
| 12 | First light and testing | [test-checklist.md](test-checklist.md) |
| 13 | On-site setup, take-down, storage | |

## 1. Buy and print first

1. Order from [bom.md](bom.md). The AliExpress order (18 Oct 2026) is due 25 to 31 Oct 2026. The "Still to buy" list has the rest: the Mean Well PSUs (7 plus 1 spare), the ESP32-DevKitC-32U boards with antennas, the Pis for two sites, the routers, flex and fasteners. The BOM says to buy 15 or more extra PG9 glands, since the 20 bought are not enough.
2. Measure the parts the design only assumes. The READMEs list these as unverified, and they may change files before you print or cut 14 of anything:
   - ESP32 board header row spacing (assumed 25.4mm), Mini560 size and pad positions, and that the 5×7cm board is 24×18 holes ([electronics/README.md](../electronics/README.md)).
   - Board hole positions and ESP32 height in the box, PG9 and PG7 thread sizes, RP-SMA bulkhead thread, and the M3 insert hole size (4.0mm) ([enclosure/README.md](../enclosure/README.md)).
   - The outer diameter of the outdoor flex (under 8mm for the glands).
3. Print **one control boot, one plain boot, two pegs, one tree box and lid** before printing the rest. PETG, 3 walls, 15% infill. Boots stand upright on the sole with no supports; pegs print head down. The export commands are in [feet/README.md](../feet/README.md) and [enclosure/README.md](../enclosure/README.md), and the STLs are committed.
4. Print 4 step clamps and 4 washers for the CNC bed ([fixtures/README.md](../fixtures/README.md)): PETG, 4 walls, 40% infill.
5. The full print run, once the test fit passes (stage 7): 14 plain boots, 14 control boots, 28 pegs, 14 tree boxes with lids, and the site boxes (the 6, 4 and 2-tree versions) with lids.

## 2. Tread preparation

You need 14 treads. Each is a tapered oak board with four old 17mm fixing holes in its back face.

1. **Tape-check** each tread against `data/blank.json`: length about 894mm, wide end about 382mm, narrow end about 92mm, thickness 30mm. These came from photos and are good to about 2 to 3mm. If one is out by more than about 3mm, fix the JSON and run `python -m tools.build` before cutting. **TBC (Rob):** the tape check has not been done.
2. Note each tread's thickness. The boot slot is 30mm plus 1.5mm.
3. Mark the front and back faces. Find the old holes in the back: two about 33mm from the narrow end and two about 44mm from the wide end, 17mm across and 23mm deep. Check them against the `EXISTING` layer of the CNC file.
4. The treads may not be identical, so measure each one rather than trusting the first.

## 3. CNC

The procedure, layers and feeds are in [cnc-cutting.md](cnc-cutting.md). In outline:

1. **Offcut test first.** Cut 11.8, 12.0, 12.2 and 12.5mm holes in an oak offcut, plus 20mm of channel at 15mm and 18mm wide. Push a pixel into each hole with its lead in the channel. Set `hole_dia` (and a counterbore if one is needed) in `tools/tree_layout.py` and run `make all`. **TBC (Rob):** hole size, counterbore, and the lead length between pixels. These wait on the pixels arriving.
2. Screw a sacrificial MDF sheet to the bed, and clamp the tread with the printed step clamps.
3. Cut a **pilot tree first**. Op 1: the 92 front holes (face up, helical bore, clear the chips every 6 to 8mm). Op 2: flip left to right, locate from the centres of the node 36 and node 64 holes, then cut the channel, the node 1 pocket and the exit slot. Watch the first tree all the way through.
4. Fit a pixel string and a boot to the pilot tree before cutting the other 13.
5. **TBC (Rob):** how front and back are registered. The current method is the two finished holes, with no dowels.

Safety: eye and ear protection, dust extraction for oak dust, hands clear of the bit. Packed chips are what snap a 4mm bit.

## 4. Finishing

1. Sand the front lightly. Do not round the hole edges.
2. Oil with an exterior oil (for example Osmo UV), 2 to 3 coats, including the end grain.
3. **Keep the push fit.** Oil can close up the holes. After the last coat, test a pixel in several holes; a tight one may need a quick hand pass with a 12mm drill bit. **TBC (Rob):** the product and cure time.

## 5. Pixel fitting

Each tree takes one string of 92 pixels. The strings have 100: cut off the surplus 8 and keep them as repair spares.

1. Identify the data end of the string and the xConnect wires. **TBC (Rob):** which wire colour is data. Check against the arrows on the string and with a meter before connecting anything.
2. Fit the pixels in **wiring order**, which is the node order in `data/tree-layout.json`:

   | Group | Nodes |
   |---|---|
   | outline | 1 to 59: from node 1 at the base-left corner, along the base, up the right edge, over the apex, down the left edge |
   | mouth_wide | 60 to 68, left to right |
   | mouth_small | 69 to 73, right to left |
   | lip | 74 to 80, left to right |
   | eye_right | 81 to 86, viewer's right, top node first, clockwise |
   | eye_left | 87 to 92, viewer's left, top node first, clockwise |

3. Push each pixel in from the front. Lay its lead in the back channel (15mm wide, 12mm deep) following the same order, and coil spare lead between closely spaced pixels.
4. Node 1 is at the base-left, at the 25mm data-in pocket. The string's input lead goes out through the exit slot in the bottom edge and hangs down into the control boot's shelf hole, with its xConnect plug at the end and a loop of slack.
5. Cut the string after node 92 and seal the cut end.
6. Test the string (checklist section B) before the channel is closed up or the tree goes into its boots.
7. **TBC (Rob):** how the leads are held in the channel. The repo does not say; use something rated for outdoor use.

## 6. Controller board (14, plus 2 spare)

Follow "Building and testing one board" in [electronics/README.md](../electronics/README.md). Every join is in [connections.md](../electronics/connections.md) and the layout is in [tree-controller-board.svg](../electronics/tree-controller-board.svg). Both are generated by `tools/gen_controller.py`: change the generator, not the files.

1. Solder the headers, DIP socket, screw terminals and passives. Leave out the ESP32, U1 and the Mini560.
2. Make the underside joins from connections.md and tick them off.
3. Check that 12V, 5V and GND are not shorted to each other.
4. Wire in the Mini560. Feed 12V from the bench supply with a 200mA limit. **Check 5.0V (plus or minus 0.1V) at J2.19 and U1.14 before the ESP32 goes in.**
5. Power off. Fit U1 (notch to the right) and the ESP32 (antenna end left). Current should stay under 150mA at 12V and WLED should join Wi-Fi.
6. Never power the ESP32 from USB and the Mini560 together. Update WLED over Wi-Fi, or unplug the 12V first.

Run checklist section A for each board.

## 7. Boots and pegs

Two boots per tree: a plain boot on the right and the **control boot** on the left (a tower for the box, behind node 1). Details are in [feet/README.md](../feet/README.md).

1. **Test-fit the first pair and two pegs on a real tread** before printing 28. Check the tread thickness in the slot, the old hole's diameter and depth (peg 16.6mm, 20mm deep), the hole height above the bottom edge (44mm from the photo), the pilot offset (26.5mm), the pilot hole diameter (the design assumes a 4 × 30 countersunk screw), and that the xConnect plug passes the 16mm shelf hole. **TBC (Rob):** all of these, and whether 50mm clearance off the ground is enough.
2. Push the M3 heat-set inserts into the tops of the control boot's four tower posts.
3. Stand both boots on blocks, so the pixel lead can hang down through the control boot. Lower the tree into them from above, feeding the pixel lead and its plug down through the shelf hole.
4. From behind, push a peg through each boot's shaft into the old fixing hole. Drive a 4mm wood screw through the peg's tab into the old pilot hole.
5. Stand the tree where it lives. Nail the toes and heels (8mm × 200mm nails). In the control boot the heel nail is inside the tower, so hammer it before the box goes on.
6. Thread the pixel lead through the arch into the tower. Bring the 12V flex in through the arch at the bottom of the tower's back wall.

The peg is separate because the tree has to drop into the slot from above; do not glue or screw a peg in before the tree is in.

## 8. Tree box

Box details are in [enclosure/README.md](../enclosure/README.md).

1. Push 6 M3 heat-set inserts into the lid side (near the rim's outer edge) of the box. The 4 tower inserts are done in stage 7.
2. Fit the PG9 (12V flex in) and PG7 (pixel lead tail out) glands in the floor, both pointing down into the tower, and the RP-SMA bulkhead in the roof. Leave the 3mm drip hole open.
3. Screw the controller board onto the four standoffs on the front wall (M2 self-tapping), components facing the lid. Foam-tape the Mini560 and the two Wago 221-413 below the board.
4. Wire to the schematic in [electronics/README.md](../electronics/README.md). The pixel current (about 2.3A at full white) goes through the Wagos on 18AWG wire, never through the board. The pixel lead's data wire goes to JD DATA. The optional TVS diode goes across JD (data to GND). There is no fuse in the box: the 5A fuse is at the site box.
5. Connect the antenna: U.FL to RP-SMA pigtail, then the dipole on the outside of the roof, pointing up. Where you can, put the box on the side of the tree that faces the router.
6. **Cord seal.** Lay the 2.7mm rubber cord in the lid groove (3.8 × 2.05mm, about 25% squeeze), cut it to length and superglue the butt joint. Fit the lid with six M3 screws, tightening evenly.
7. Fit the box on the tower with four M3 screws through its ears. Plug the pixel lead's xConnect into the PG7 tail.

Run checklist section C (including the soak test of at least one box).

## 9. Site box and power

Each site's PSUs, fuses and runs are in [electronics/site-wiring.md](../electronics/site-wiring.md), generated from `data/sites.json`. **TBC (Rob):** the tree counts per site and every run length are defaults, not confirmed. Edit `data/sites.json` and run `make all` when they are. Current defaults: Site A 6 trees (Pi 5), Site B 4 trees (Pi 3), Sites C and D 2 trees each (Pi still to buy).

**Mains.** Each PSU has its own mains lead to an RCD-protected outdoor socket (or a weatherproof multi-way box on one). Mains never enters a printed box. The repo does not specify the socket, the lead or who inspects the mains side. **TBC (Rob):** have the mains side checked by a competent electrician.

1. Print the box for the site's tree count (`trees=6`, `4` or `2`). Fit 8 M3 heat-set inserts for the lid.
2. Fit PG9 glands in the floor: one per PSU input and one per tree run. Fit a PG7 for the speaker (two rows for a 6-tree site). Leave the drip hole open.
3. Lay the parts on the back wall before tying anything down: Pi on its standoffs (58 × 49mm M2.5 pattern, top left), router, 12V to 5V buck, PAM8610, USB sound card, Wagos and fuse holders on the zip-tie anchors. **TBC (Rob):** these sizes are not confirmed, nor that they fit the 64mm depth.
4. Wire each PSU's 12V input to **its own** pair of Wagos (+ and −), and from there through its own 5A blade fuses to its two tree runs. **Never join two PSUs' +12V.** The negatives may be joined.
5. PSU 1 also feeds the player: a 3A fuse, then the buck to the Pi (a Pi 5 needs a 5V 5A buck, a Pi 3 is happy with 2.5A). The PAM8610 runs straight off 12V.
6. Fuse each run at the site box, where it starts, so the fuse protects the flex. Use 3-core 0.75mm² outdoor flex (good for about 6A) up to about 7m, and 1.5mm² beyond.
7. Run each flex to its tree and through the back arch of the control boot to the PG9 gland. Label both ends with the tree number.
8. Stand the PSUs outside, beside the site box. Screw the box to a post or fence through its lugs (5 × 40 exterior screws).

## 10. Network

1. One travel router per site (GL.iNet Mango, about £27), set up identically: same SSID, password and subnet at every site. **No Wi-Fi password goes in git.** **TBC (Rob):** dedicated router or the Pi as hotspot. The router is the working assumption and the hotspot is the fallback.
2. Subnet: the GL.iNet default, 192.168.8.x. **TBC (Rob):** confirm on the real router.
3. Fixed addresses: tree NN is `stairtree-NN` at `192.168.8.(100+NN)`, the same at every site. Tree 7 is `stairtree-07` at 192.168.8.107. Reserve each IP in the router as well as setting it in WLED.
4. The router can sit in the site box or beside it. Keep each tree's antenna in view of it where possible: 30mm of wet oak costs signal.
5. Connect the Pi to the router by Ethernet.

## 11. Provisioning

Do this on the bench, before anything goes outside.

### Trees (WLED)

For each ESP32, follow "Setting up a tree controller by hand" in [wled/README.md](../wled/README.md):

1. Flash the plain ESP32 build of WLED (16.0.1 was tested) from install.wled.me.
2. LED preferences: length 92, data GPIO 16, WS281x, colour order GRB (**TBC at first light**), brightness limiter on. The limiter assumes 5V pixels, so recheck it for the 12V strings.
3. Sync interfaces: tick Receive UDP realtime (DDP).
4. Set the hostname `stairtree-NN`, the static IP 192.168.8.(100+NN) and the site Wi-Fi.
5. Label the ESP32 and its box with the tree number.

**What M5 will generate.** `tools/gen_site_config.py` (milestone M5, not written yet) is to produce, per tree, a WLED config (hostname, static IP, 92 LEDs, GPIO 16, colour order, realtime on, no Wi-Fi credentials) and, per site, an FPP config (one DDP output per tree, a playlist, and a nightly schedule that stops the show cleanly). Until it exists, do these by hand. The WLED and FPP config schemas are unverified: prefer WLED's `/json/cfg` backup and restore and FPP's settings backup over writing files.

### Players (FPP)

[fpp/README.md](../fpp/README.md) is a placeholder until M5, so this is **TBC (Rob)**. From the brief: FPP 10.x on a 64-bit Pi image, a high-endurance microSD, the USB sound card as the audio output, and one DDP output per tree to its IP. Each tree's slot decides its start channel and each carries 276 channels:

| Slot | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Start channel | 1 | 277 | 553 | 829 | 1105 | 1381 |

A 2-tree site uses slots 1 and 2, a 4-tree site slots 1 to 4. The slot-to-tree mapping will be in `data/sites.json` (M5). Upload the `.fseq` and audio, then build the playlist and schedule from [show-night.md](show-night.md) (the times there are a proposal).

## 12. First light and testing

Run [test-checklist.md](test-checklist.md) in order; its sections match the stages above. Write the readings in the blanks and keep the sheets. At first light settle:
- Colour order (solid red, green, blue); update WLED if it is not GRB.
- That node 1 and the wiring order match the xLights model (a test chase).
- Whether DDP over Wi-Fi is smooth enough for lip-sync with all of a site's trees streaming. If it jitters, the fallback is ESPixelStick in FPP Remote mode, which needs SD-equipped ESP32s, so decide before building all 14 boards.

## 13. On-site setup, take-down and storage

**TBC (Rob):** the repo has nothing on this yet, so this is a proposed order, to revise after the first real set-up.

Setting up:
1. Fix the site box to its post and stand the PSUs beside it.
2. Stand each tree and nail its boots, with the control boot on the left.
3. Run each 12V flex to its tree and connect the box.
4. Mains last: plug the PSUs into the RCD socket and test the RCD. Then power the router, the player, and the trees.
5. Run checklist sections D and E.

Taking down:
1. Switch off at the mains and unplug before touching any 12V connection.
2. Take the boxes off the towers. Pull the nails to free the boots.
3. Dry everything before packing it.

Storage: dry, trees flat with the pixel leads supported, lids off the boxes with the cord left in its groove, and each tree's flex and box labelled with its number.
