# Build guide

How to build the Stair Tree Choir, in order: 14 trees, 4 sites. It is written from the other documents in this repo, which stay the source of truth for dimensions and decisions ([CLAUDE.md](../CLAUDE.md)). Where something is not decided or not yet measured, it says **TBC (Rob)**. The tick-box tests are in [test-checklist.md](test-checklist.md); each stage below says which section to run.

Two safety rules cover the whole project:
- Mains stays inside the PSU and its printed terminal hood, which is closed all round and carries a fused, switched IEC inlet (Rob, 15 Nov 2026). Mains comes from an RCD-protected outdoor socket on a C13 lead. No other printed part carries mains.
- Never join the +12V of two PSUs.

## 0. Overview

| Stage | What | Details |
|---|---|---|
| 1 | Buy and print | [bom.md](bom.md), [print/](../print/README.md), [cad/](../cad/README.md) |
| 2 | Prepare and check the treads | `data/blank.json` |
| 3 | CNC | [cnc-cutting.md](cnc-cutting.md) |
| 4 | Finish the wood | exterior oil |
| 5 | Glue the disks, fit the pixels | `data/tree-layout.json` |
| 6 | Build the controller board | [electronics/README.md](../electronics/README.md) |
| 7 | Mounts: sockets, display stands, tent-pole feet | [cad/README.md](../cad/README.md#tree-mounts-socket-display-stand-tent-pole-feet-storage-tower-rob-16-nov-2026) |
| 8 | Tree box | [cad/README.md](../cad/README.md#tree-controller-box) |
| 9 | Site box and power | [electronics/site-wiring.md](../electronics/site-wiring.md) |
| 10 | Network | router, fixed IPs |
| 11 | Provisioning | [wled/README.md](../wled/README.md), [fpp/README.md](../fpp/README.md) |
| 12 | First light and testing | [test-checklist.md](test-checklist.md) |
| 13 | On-site setup, take-down, storage | |

## 1. Buy and print first

1. Order from [bom.md](bom.md). The AliExpress order (18 Oct 2026) is due 25 to 31 Oct 2026. The "Still to buy" list has the rest: the Mean Well PSU (one LRS per site), the ESP32-DevKitC-32U boards with antennas, the Pis for two sites, the routers, flex and fasteners. The BOM says to buy 15 or more extra PG9 glands, since the 20 bought are not enough.
2. Measure the parts the design only assumes. The READMEs list these as unverified, and they may change files before you print or cut 14 of anything:
   - ESP32 board header row spacing (assumed 25.4mm), Mini560 size and pad positions, and that the 5×7cm board is 24×18 holes ([electronics/README.md](../electronics/README.md)).
   - Board hole positions and ESP32 height in the box, the SP16 socket's nut and thread, the PG7 and RP-SMA sizes, and the insert holes ([docs/tree-box-parts.md](tree-box-parts.md)).
   - Site A's S-400-12, the IEC inlet and the XH-M541 against the hood and the site box ([cad/README.md](../cad/README.md)).
   - The outer diameter of the outdoor flex (6–10mm for the SP17's gland).
3. Print the first-offs before the rest, from [print/](../print/README.md) (sizes, counts and settings in its table): one **tree box** with its coupon and seal test, the **dovetail coupon**, one **socket** and the **drilling jig**, then two **display stands** and four **pole caps**. PETG.
4. Print 4 step clamps and 4 washers for the CNC bed: PETG, 4 walls, 40% infill.
5. The full print run, once the test fits pass (stage 7): 14 tree boxes, 42 sockets, 28 display stands, 56 pole caps, 42 storage towers (before the season ends), 92 pixel disks per tree, Site A's PSU hood and buck pod.

## 2. Tread preparation

You need 14 treads. Each is a tapered oak board with four old 17mm fixing holes in its back face.

1. **Tape-check** each tread against `data/blank.json`: length about 894mm, wide end about 382mm, narrow end about 92mm, thickness 30mm. These came from photos and are good to about 2 to 3mm. If one is out by more than about 3mm, fix the JSON and run `python -m tools.build` before cutting. **TBC (Rob):** the tape check has not been done.
2. Note each tread's thickness. The sockets' channel is 30mm plus 0.8mm (`fit`); a thicker tread needs it changed.
3. Mark the front and back faces. Find the old holes in the back: two about 33mm from the narrow end and two about 44mm from the wide end, 17mm across and 23mm deep. Check them against the `EXISTING` layer of the CNC file.
4. The treads may not be identical, so measure each one rather than trusting the first.

## 3. CNC

The procedure, layers and feeds are in [cnc-cutting.md](cnc-cutting.md). In outline:

Each tree is cut in one op, front face up, with no flip and nothing cut from the back (Rob, 25 Oct 2026). Rob does the CAM in NX from the STEP files in `cad/` (`tools/cad_tree.py`, run by `make all`).

1. **Offcut test first.** Print a few pixel disks (`print/pixel-disk.stl`). Cut one Ø19 × 6mm counterbore and a Ø15 clearance hole in an oak offcut and press a disk in. Check a pixel snaps in and its clips clear the hole. Set `hole_dia` (the disk bore) and `clearance_dia` in `tools/tree_layout.py` and run `make all`. **TBC (Rob):** the disk bore and the clip barb flare. These wait on the pixels arriving.
2. **Op 0, once:** screw an MDF sheet to the bed and pocket it 4mm deep to the blank's shape. Don't move it again.
3. Cut a **pilot tree first**. Op 1: drop the tread into the pocket, face up, and clamp it with the clamps clear of the counterbores. Cut the 92 counterbores, then the clearance holes through into the MDF (helical bore, clear the chips every 6 to 8mm). Watch the first tree all the way through.
4. Fit a pixel string, the sockets, stands and poles to the pilot tree before cutting the other 13.

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

3. **Press in the disks** first: one printed PETG disk in each front counterbore, ribbed edge first (front face out), pushed in flush with the face. It's a friction fit on crush ribs (no glue): `rib_od` 19.3 and `bore` 12.0 fitted on 13 Nov 2026 (cad/parts/pixel-disk.FCStd).
4. Push each pixel in from the front, through the disk, until its clips snap behind it. The flange rests on the disk, about 1mm proud. The 30mm body ends level with the back face, so the leads come straight out of the back.
5. Loop each lead across the back face to the next pixel in the same order.
6. Node 1 is at the base-left. The string's input lead runs across the back face to the tree box's PG7 gland, with its xConnect plug at the end and a loop of slack.
7. Cut the string after node 92 and seal the cut end.
8. Test the string (checklist section B) before the mounts and the box go on.
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

## 7. Mounts: sockets, display stands, tent-pole feet

Three sockets per tree, screwed to the edge through both legs: two on the bottom edge, one on the top. In the show a display stand slides onto each bottom socket's dovetail rail, an 11mm fibreglass tent pole runs through it front to back, and a pegged cap goes on each end of the pole; in storage a slim storage tower drops onto every rail. Details and positions: [cad/README.md](../cad/README.md#tree-mounts-socket-display-stand-tent-pole-feet-storage-tower-rob-16-nov-2026); clearances: [cad-checks.md](cad-checks.md).

1. **Test-fit one socket and the dovetail coupon** before printing 42. The socket should slide over the edge with a little slack (0.8mm across); the coupon should slide onto the rail by hand without rocking, and a pole should slide through its hole. Too tight or loose: change `clr` (or `pole_d`) in cad/parts/tree-mounts.FCStd and `make cad`.
2. Mark the sockets: bottom ones centred 55.9mm in from each side of the bottom edge, the top one centred on the top edge. Each sits hard against the edge with its legs over both faces, the rail running front to back.
3. Pilot (2.5mm) and drive four 4 × 16 countersunk stainless wood screws per socket: two through the back leg, two through the front leg. Each goes 12.5mm into the oak; nothing goes into the end grain of the edge.
4. Cut the poles: two 400mm lengths of 11mm fibreglass tent pole per tree, no ferrules (tape round the cut, fine hacksaw, sand the ends, gloves).
5. With the tree lying on its back, slide a display stand onto each bottom rail from the front until it stops. Push a pole through each stand's tube, centred, and a cap onto each end.
6. Stand the tree where it lives, the caps' pads outwards, and drive a peg (up to 9mm) through each cap (four per tree). If a tree creeps along its poles in testing, a cable tie on the pole either side of each stand stops it.

## 8. Tree box

## 8. Tree box

L base + wrap-round cover; details in [cad/README.md](../cad/README.md#tree-controller-box). Print the coupon and the seal test before the first box.

1. **Base, on the bench.** Push the M3 heat-set insert into the block on the shelf and an M2 insert into each of the four standoffs. Fit the SP16 panel socket (rear nut; the D flat stops it turning), the PG7 gland and the RP-SMA bulkhead in the shelf, all firing down, with the dipole on the bulkhead.
2. Screw the controller board onto the plate's four standoffs with four M2 × 6 screws, components facing the back. Fit the two Wago 221-413 on the plate below the board.
3. Wire to the schematic in [electronics/README.md](../electronics/README.md): SP16 to the Wagos, Wagos to the Mini560's IN pads and the pixel lead. The pixel current (about 2.3A at full white) goes through the Wagos on 18AWG wire, never through the board. The pixel lead's data wire goes to JD DATA. Plug the U.FL pigtail onto the ESP32. There is no fuse in the box: the 3A fuse is at the site box.
4. **Cord seal.** Press the 2.7mm rubber cord into the plate's groove, under every pinch point, from one end over the top to the other. It doesn't need joining.
5. **On the tree.** Low on the node-1 side, high enough that the SP17 plug under the shelf ends at least 20mm above the tree's bottom edge (the assembly puts the plate's left edge 83mm in from the tree's left and the cover's bottom 126mm up: [cad-checks.md](cad-checks.md); check the ear screws miss the pixel leads on your tree). Four 4 × 40 stainless pan-head wood screws with washers through the ear slots and the 10mm spacers into the back of the tree, the shelf level. Plug the run's SP17 plug onto the SP16 underneath and the pixel lead's xConnect onto its tail.
6. **Cover.** Hold it with the bottom a few degrees out, lift it over the plate's top edge and drop it so the hook catches behind the plate. Swing the bottom in and fit the one M3 × 10 screw at the lower back corner, until the rim lands on the plate.

## 9. Site box and power

Each site's PSUs, fuses and runs are in [electronics/site-wiring.md](../electronics/site-wiring.md), generated from `data/sites.json`. **TBC (Rob):** the tree counts per site and every run length are defaults, not confirmed. Edit `data/sites.json` and run `make all` when they are. Current defaults: Site A 6 trees (Pi 5), Site B 4 trees (Pi 3), Sites C and D 2 trees each (Pi still to buy).

**Mains** (Site A, Rob, 15 Nov 2026). A C13 lead (13A plug, 5A fuse) from an RCD-protected outdoor socket, through a lid seal, into the IEC inlet on the PSU's printed hood. Inside the hood: the inlet's L (through its fuse and switch) and N to the S-400-12's L and N, its earth to FG, all on fully insulated crimps. Mains goes nowhere else in the box. Wiring and tests: [site-box-wiring.html](site-box-wiring.html). **TBC (Rob):** have the mains side checked by a competent electrician.

The site box is a DRiBOX Large (Rob, 26 Oct 2026). Cables pass through the seals in its lid, so it needs no glands. Its inside tapers towards the floor, with ribs: measure it. Parts are stuck down on pads, no plate (Rob, 10 Nov 2026); the assembly ([cad/stair-tree-choir.FCStd](../cad/stair-tree-choir.FCStd)) shows an indicative layout.

1. Set the S-400-12's input switch to **230V**. Wire the 12V leads straight onto +V and −V and the inlet (in the hood's roof) to L, N and earth, lower the hood on (two M4 × 6 with washers into the case's side holes, no longer) and stand the PSU along the back of the floor, fan side up and clear.
2. Fit the 10-way blade fuse box: the PSU's +12V to its input stud; the PSU's 0V to two linked Wago 221-415 beside it. One way per tree run (3A), one for the Pi's buck (3A), one for the amp (3A), one for the router where it's on the PSU (2A); every negative to the Wagos.
3. Fit the Pi with its 12V-to-USB buck in the printed buck pod, and the XH-M541 amp (12V off its own fuse; the USB sound card plugs into the Pi and a short 3.5mm lead goes to the amp's input). Each speaker gets its own 2-core run from the amp.
4. Make up each run: 2-core 0.75mm² outdoor flex (good for about 6A) up to about 7m, 1.5mm² beyond, with the SP17 cable plug of an SP16/SP17 2-pin aviation connector on the tree end (screw terminals, no solder; tighten its gland nut on the sheath). Red to +, the same pin every time. Label both ends with the tree number.
5. Wire each tree box's SP16 socket to its two Wagos with short 0.75mm² tails, red to +, the same pin as the plugs.
6. Wire each run to its fuse at the site box, lay the cables through the DRiBOX lid seals with the cable guides, and clamp the lid.
7. Plug each run into its tree. Keep the joints off the ground where water pools (IP67 only when mated).
8. Stand the box upright with the seals facing down, or screw it to a post or fence.

## 10. Network

1. One router per site: a Cudy WR3000 (about £30–40) flashed with vanilla OpenWrt. Set every site up identically, with the same SSID, password and subnet. **No Wi-Fi password goes in git.**
2. The show runs on 2.4 GHz only, because the ESP32s are 2.4 GHz. Give it a fixed channel (1, 6 or 11, 20 MHz wide), picking whichever is quietest at the site. The 5 GHz radio isn't used for the show.
3. Subnet: 192.168.8.x, with the router at 192.168.8.1. OpenWrt starts at 192.168.1.1, so change the LAN address at first set-up.
4. Fixed addresses: tree NN is `stairtree-NN` at `192.168.8.(100+NN)`, the same at every site. Tree 7 is `stairtree-07` at 192.168.8.107. Reserve each IP in the router as well as setting it in WLED. Site A is the exception: it runs on the home network, with tree NN reserved at `192.168.0.(220+NN)` on the Zyxel OpenWrt and WLED left on DHCP (data/sites.json).
5. Each router keeps two configs. "Show" is the setup above. "Home" makes it an 802.11s mesh node of Rob's home OpenWrt network for the rest of the year (5 GHz backhaul, home SSID on 2.4 GHz). Save both as `sysupgrade -b` backups outside git, because they hold the Wi-Fi passwords. Restore "show" before each season.
6. Not in the site box: inside the DRiBOX the router's 175mm antennas would lie flat over the PSU at ground level. Put it up high with its antennas upright (Site A: indoors at the front window, about 5ft from the trees). Keep each tree's antenna in view of it where possible: 30mm of wet oak costs signal.
7. Site A: the router stands indoors at the front window, about 5ft from the trees, with its antennas upright, on its own mains adapter. Other sites: in a small covered box mounted high, on the site PSU through its own 2A fuse (the WR3000 takes 12V 1A, the WR3000H 1.5A; check the label and the barrel's polarity). Set `"router"` in `data/sites.json` to match.
8. Connect the Pi to the router by Ethernet: at Site A, outdoor Cat6 from the site box (through its lid seal) to the window.

## 11. Provisioning

Do this on the bench, before anything goes outside.

### Trees (WLED)

For each ESP32, follow "Setting up a tree controller by hand" in [wled/README.md](../wled/README.md):

1. Flash the plain ESP32 build of WLED (16.0.1 was tested) from install.wled.me.
2. LED preferences: length 92, data GPIO 16, WS281x, colour order RGB (confirmed at first light on tree 1), brightness limiter on. The limiter assumes 5V pixels, so recheck it for the 12V strings.
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
- Colour order (solid red, green, blue); WLED is set to RGB (order 1); change it if a tree differs.
- That node 1 and the wiring order match the xLights model (a test chase).
- Whether DDP over Wi-Fi is smooth enough for lip-sync with all of a site's trees streaming. If it jitters, the fallback is ESPixelStick in FPP Remote mode, which needs SD-equipped ESP32s, so decide before building all 14 boards.

## 13. On-site setup, take-down and storage

**TBC (Rob):** the repo has nothing on this yet, so this is a proposed order, to revise after the first real set-up.

Setting up:
1. Put the site box in place.
2. With each tree on its back, slide a display stand onto each bottom rail from the front, push a pole through each and a cap onto each end, stand it and peg each cap (four pegs).
3. Run each 12V flex to its tree and screw its SP17 plug onto the box's SP16.
4. Mains last: plug the C13 lead into the inlet and the plug into the RCD socket, test the RCD, then switch on at the inlet. Then power the router, the player and the trees.
5. Run checklist sections D and E.

Taking down:
1. Switch off at the mains and unplug before touching any 12V connection.
2. Unscrew the SP17 plugs. Pull the pegs, take the caps and poles off and slide the stands off. For storage, slide a storage tower onto each of the three rails and stack the trees face up.
3. Dry everything before packing it.

Storage: dry, the trees face up in one stack on their towers (a tower dropped onto every socket's rail; each drops into the one below, 115mm pitch, about 1.63m for 14). Boxes stay on the trees, the cord left in its groove; label each tree's flex with its number.
