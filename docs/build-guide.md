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
| 5 | Glue the disks, fit the pixels | `data/tree-layout.json` |
| 6 | Build the controller board | [electronics/README.md](../electronics/README.md) |
| 7 | Boots and pegs | [feet/README.md](../feet/README.md) |
| 8 | Tree box | [enclosure/README.md](../enclosure/README.md) |
| 9 | Site box and power | [electronics/site-wiring.md](../electronics/site-wiring.md) |
| 10 | Network | router, fixed IPs |
| 11 | Provisioning | [wled/README.md](../wled/README.md), [fpp/README.md](../fpp/README.md) |
| 12 | First light and testing | [test-checklist.md](test-checklist.md) |
| 13 | On-site setup, take-down, storage | |

## 1. Buy and print first

1. Order from [bom.md](bom.md). The AliExpress order (18 Oct 2026) is due 25 to 31 Oct 2026. The "Still to buy" list has the rest: the Mean Well PSU (one LRS per site), the ESP32-DevKitC-32U boards with antennas, the Pis for two sites, the routers, flex and fasteners. The BOM says to buy 15 or more extra PG9 glands, since the 20 bought are not enough.
2. Measure the parts the design only assumes. The READMEs list these as unverified, and they may change files before you print or cut 14 of anything:
   - ESP32 board header row spacing (assumed 25.4mm), Mini560 size and pad positions, and that the 5×7cm board is 24×18 holes ([electronics/README.md](../electronics/README.md)).
   - Board hole positions and ESP32 height in the box, the SP16 socket's hole and nut clearance, the PG7 thread size, RP-SMA bulkhead thread, and the M3 insert hole size (4.0mm) ([enclosure/README.md](../enclosure/README.md)).
   - The outer diameter of the outdoor flex (under 8mm for the glands).
3. Print **one control boot, one plain boot, two pegs, one tree box and lid** before printing the rest. PETG, 3 walls, 15% infill. Boots stand upright on the sole with no supports; pegs print head down. The export commands are in [feet/README.md](../feet/README.md) and [enclosure/README.md](../enclosure/README.md), and the STLs are committed.
4. Print 4 step clamps and 4 washers for the CNC bed, and the pixel disk test strip ([fixtures/README.md](../fixtures/README.md)): PETG, 4 walls, 40% infill for the clamps.
5. The full print run, once the test fit passes (stage 7): 14 plain boots, 14 control boots, 28 pegs, 14 tree boxes with lids, 92 pixel disks per tree (bore from the test strip, stage 3), and the site boxes (the 6, 4 and 2-tree versions) with lids.

## 2. Tread preparation

You need 14 treads. Each is a tapered oak board with four old 17mm fixing holes in its back face.

1. **Tape-check** each tread against `data/blank.json`: length about 894mm, wide end about 382mm, narrow end about 92mm, thickness 30mm. These came from photos and are good to about 2 to 3mm. If one is out by more than about 3mm, fix the JSON and run `python -m tools.build` before cutting. **TBC (Rob):** the tape check has not been done.
2. Note each tread's thickness. The boot slot is 30mm plus 1.5mm.
3. Mark the front and back faces. Find the old holes in the back: two about 33mm from the narrow end and two about 44mm from the wide end, 17mm across and 23mm deep. Check them against the `EXISTING` layer of the CNC file.
4. The treads may not be identical, so measure each one rather than trusting the first.

## 3. CNC

The procedure, layers and feeds are in [cnc-cutting.md](cnc-cutting.md). In outline:

Each tree is cut in one op, front face up, with no flip and nothing cut from the back (Rob, 25 Oct 2026). Rob does the CAM in NX from the STEP files in `cad/` (`tools/gen_step.py`).

1. **Offcut test first.** Print the disk test strip (`fixtures/pixel-disk.scad`, bores 11.8 to 12.2mm). Cut one Ø19 × 6mm counterbore and a Ø15 clearance hole in an oak offcut and glue a disk in. Check a pixel snaps in and its clips clear the hole. Set `hole_dia` (the disk bore) and `clearance_dia` in `tools/tree_layout.py` and run `make all`. **TBC (Rob):** the disk bore and the clip barb flare. These wait on the pixels arriving.
2. **Op 0, once:** screw an MDF sheet to the bed and pocket it 4mm deep to the blank's shape. Don't move it again.
3. Cut a **pilot tree first**. Op 1: drop the tread into the pocket, face up, and clamp it with the clamps clear of the counterbores. Cut the 92 counterbores, then the clearance holes through into the MDF (helical bore, clear the chips every 6 to 8mm). Watch the first tree all the way through.
4. Fit a pixel string and a boot to the pilot tree before cutting the other 13.

Safety: eye and ear protection, dust extraction for oak dust, hands clear of the bit. Packed chips are what snap a 4mm bit.

## 4. Finishing

1. Sand the front lightly. Do not round the counterbore edges.
2. Oil with an exterior oil (for example Osmo UV), 2 to 3 coats, including the end grain.
3. **Oil before the disks go in.** The pixel fit is in the printed disk, not the wood, so the oil can't close it up; let it cure before gluing. **TBC (Rob):** the product and cure time.

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

3. **Glue in the disks** first: one printed PETG disk (Ø18.5 × 6mm) in each front counterbore, flush with the face, with hot glue (or CA or epoxy). Keep glue out of the bore.
4. Push each pixel in from the front, through the disk, until its clips snap behind it. The flange rests on the disk, about 1mm proud. The 30mm body ends level with the back face, so the leads come straight out of the back.
5. Loop each lead across the back face to the next pixel in the same order.
6. Node 1 is at the base-left. The string's input lead runs down the back face into the control boot's shelf hole, with its xConnect plug at the end and a loop of slack.
7. Cut the string after node 92 and seal the cut end.
8. Test the string (checklist section B) before the tree goes into its boots.
9. **TBC (Rob):** how the leads are held on the back face, and that the flange doesn't crack the disk when a pixel is pushed in. Use something rated for outdoor use for the leads.

## 6. Controller board (14, plus 2 spare)

Follow "Building and testing one board" in [electronics/README.md](../electronics/README.md). Every join is in [connections.md](../electronics/connections.md) and the layout is in [tree-controller-board.svg](../electronics/tree-controller-board.svg). Both are generated by `tools/gen_controller.py`: change the generator, not the files.

1. Solder the screw terminals and passives. Leave out the ESP32, U1 and the Mini560 (no sockets: they are soldered in once the 5V rail checks out).
2. Make the underside joins from connections.md and tick them off.
3. Check that 12V, 5V and GND are not shorted to each other.
4. Wire in the Mini560. Feed 12V from the bench supply with a 200mA limit. **Check 5.0V (plus or minus 0.1V) at the J2.19 and U1.14 holes before the ESP32 and U1 go in.**
5. Power off. Solder in U1 (notch to the right) and the ESP32 (antenna end left). Current should stay under 150mA at 12V and WLED should join Wi-Fi.
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

Base + cover; details in [enclosure/README.md](../enclosure/README.md). Print the coupon and the seal test before the first box.

1. **Base, on the bench.** Push 4 M3 heat-set inserts into the plug's sides (two each side). Fit the SP16 panel socket (rear nut; the D flat stops it turning) and the PG7 gland in the shelf floor, both pointing down. Leave the 3mm drip hole open.
2. Screw the controller board onto the plate's four standoffs (M2 self-tapping), components facing the back. Fit the two Wago 221-413 on the plate below the board.
3. Wire to the schematic in [electronics/README.md](../electronics/README.md): SP16 to the Wagos, Wagos to JP and the pixel lead. The pixel current (about 2.3A at full white) goes through the Wagos on 18AWG wire, never through the board. The pixel lead's data wire goes to JD DATA. There is no fuse in the box: the 3A fuse is at the site box.
4. **Cover.** Fit the RP-SMA bulkhead in its outer side wall and the dipole outside, hinged to point up. Plug the U.FL pigtail onto the ESP32, leaving enough slack to set the cover down beside the base.
5. **Cord seal.** Lay the 2.7mm rubber cord in the plug's groove all the way round, cut it to length and superglue the butt joint (at the back, not in the bends). Slide the cover on from behind, square, over the cord, and fit its four M3 × 10 screws.
6. **On the tree.** Four 4 × 40 stainless pan-head wood screws with washers through the flange slots and the 10mm spacers into the back of the tree, the shelf level. Plug the run's SP17 plug onto the SP16 underneath and the pixel lead's xConnect onto its tail.

## 9. Site box and power

Each site's PSUs, fuses and runs are in [electronics/site-wiring.md](../electronics/site-wiring.md), generated from `data/sites.json`. **TBC (Rob):** the tree counts per site and every run length are defaults, not confirmed. Edit `data/sites.json` and run `make all` when they are. Current defaults: Site A 6 trees (Pi 5), Site B 4 trees (Pi 3), Sites C and D 2 trees each (Pi still to buy).

**Mains.** One plug lead (3-core 1.0mm² H05RN-F, 13A plug with a 3A fuse) per site, from an RCD-protected outdoor socket into the site box, clamped to the plate and wired to the PSU's input terminals under their printed cover. Mains goes nowhere else in the box. The repo does not specify the socket or who inspects the mains side. **TBC (Rob):** have the mains side checked by a competent electrician.

The site box is a DRiBOX Large (Rob, 26 Oct 2026). Cables pass through the seals in its lid, so it needs no glands. Its inside tapers towards the floor, with ribs: measure it before printing the plate. **The plate is still to design** (CLAUDE.md §5); the steps below are the plan.

1. Fit the PSU (Site A: LRS-200-12) at the top of the plate with air round it, then the terminal cover over its mains side.
2. Fit the 10-way blade fuse box below it: the PSU's +12V to its input, 0V to its negative bus. One way per tree run (3A), one for the player (3A), one for the router (2A); every negative to the bus.
3. Fit the Pi and its Mini560 5V buck (Site A: the Pi 3, which needs 2.5A; keep the 5V leads short. A Pi 5 would need 5A, and `PSU_MAX_CURRENT=5000` set with `rpi-eeprom-config --edit` because a plain buck can't do its USB-PD handshake), the PAM8610 (straight off 12V after the player fuse) and the USB sound card. Each speaker gets its own 2-core run from the amp.
4. Make up each run: 2-core 0.75mm² outdoor flex (good for about 6A) up to about 7m, 1.5mm² beyond, with the SP17 cable plug of an SP16/SP17 2-pin aviation connector on the tree end (screw terminals, no solder; tighten its gland nut on the sheath). Red to +, the same pin every time. Label both ends with the tree number.
5. Wire each tree box's SP16 socket to its two Wagos with short 0.75mm² tails, red to +, the same pin as the plugs.
6. Wire each run to its fuse at the site box, lay the cables through the DRiBOX lid seals with the cable guides, and clamp the lid.
7. Plug each run into its tree. Keep the joints off the ground where water pools (IP67 only when mated).
8. Stand the box upright with the seals facing down, or screw it to a post or fence.

## 10. Network

1. One router per site: a Cudy WR3000 (about £30–40) flashed with vanilla OpenWrt. Set every site up identically, with the same SSID, password and subnet. **No Wi-Fi password goes in git.**
2. The show runs on 2.4 GHz only, because the ESP32s are 2.4 GHz. Give it a fixed channel (1, 6 or 11, 20 MHz wide), picking whichever is quietest at the site. The 5 GHz radio isn't used for the show.
3. Subnet: 192.168.8.x, with the router at 192.168.8.1. OpenWrt starts at 192.168.1.1, so change the LAN address at first set-up.
4. Fixed addresses: tree NN is `stairtree-NN` at `192.168.8.(100+NN)`, the same at every site. Tree 7 is `stairtree-07` at 192.168.8.107. Reserve each IP in the router as well as setting it in WLED.
5. Each router keeps two configs. "Show" is the setup above. "Home" makes it an 802.11s mesh node of Rob's home OpenWrt network for the rest of the year (5 GHz backhaul, home SSID on 2.4 GHz). Save both as `sysupgrade -b` backups outside git, because they hold the Wi-Fi passwords. Restore "show" before each season.
6. Not in the site box: inside the DRiBOX the router's 175mm antennas would lie flat over the PSU at ground level. Put it up high with its antennas upright (Site A: indoors at the front window, about 5ft from the trees). Keep each tree's antenna in view of it where possible: 30mm of wet oak costs signal.
7. Site A: the router stands indoors at the front window, about 5ft from the trees, with its antennas upright, on its own mains adapter. Other sites: in a small covered box mounted high, on the site PSU through its own 2A fuse (the WR3000 takes 12V 1A, the WR3000H 1.5A; check the label and the barrel's polarity). Set `"router"` in `data/sites.json` to match.
8. Connect the Pi to the router by Ethernet: at Site A, outdoor Cat6 from the site box (through its lid seal) to the window.

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
