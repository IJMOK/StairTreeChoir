# Bill of materials

Kept current from CLAUDE.md §4. 14 trees (maybe 15), each with its own ESP32 controller; one show player per site (4 sites). First goal: 6 trees at Site A by 1 Dec 2026. Updated 24 Oct 2026 with deliveries; pixel disks and the fixture plate added 25 Oct 2026.

## Bought

AliExpress order of 18 Oct 2026 (£277.80, due 25–31 Oct), plus the ESP32 order of 22 Oct.

| Qty | Item | Notes | Status |
|---|---|---|---|
| 14 | Ray Wu 12V WS2811 12mm bullet strings, 100 pixels, resistor type, black 18AWG, xConnect ends | One per tree. Cut the surplus 8 off each and keep as repair spares. Lead spacing not yet confirmed (probably 3–4 inch). | Due 25–31 Oct |
| 2 lots (20 pairs) | Ray Wu xConnect 3-core 18AWG flat pigtails, 20cm | | Due 25–31 Oct |
| 10 | PAM8610 amp boards | 4 needed (one per site); 6 spare | Arrived 24 Oct |
| 10 | 74AHCT125N DIP-14 | One per tree; 6 more for 16 boards | Arrived 24 Oct |
| 10 | Prototype boards, 5×7cm | Tree controller boards; 6 more for 16 boards | Arrived 24 Oct |
| 7 | USB sound cards | 4 needed (one per site player); 3 spare | Arrived 24 Oct |
| 15 | Micro-USB OTG cables | Spares | Arrived 24 Oct |
| 10 | 2×20 pin headers | Spares | Arrived 24 Oct |
| 10 | Mini560 5V buck | One per tree controller; 6 more for 16 boards | Arrived 24 Oct |
| 20 + 20 | PG7 and PG9 cable glands | Needed (23 Oct 2026 design): PG9 14 = the tree boxes' 12V lead; PG7 14 = the tree boxes. The site box is now a DRiBOX, whose lid seals clamp the cables, so it needs no glands (26 Oct 2026). Both are covered. | Arrived 24 Oct |
| 10 | ESP32-DevKitC-32U dev board, 38-pin | 16 needed; 6 more to buy | Ordered 22 Oct (AliExpress) |
| 10 | 2.4GHz antenna: U.FL to RP-SMA bulkhead pigtail + RP-SMA dipole | 16 needed; 6 more to buy | Ordered 22 Oct (AliExpress) |

## Rob already has

- DIP sockets
- 5A blade fuses (no longer used: the site box has DIN-rail 10×38 fuses, 26 Oct 2026)
- M3 heat-set inserts and stainless screws (count them against the fastener list below)
- 33Ω resistors, 100µF capacitors
- Lid sealing cord, RS 159-1490

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

**The plan (Rob, 24 Oct 2026):** a minimum viable show of **6 trees at home (Site A) by 1 Dec 2026**. Buy the December list first; the later list is for sites B to D and trees 7 to 14 (or 15) and can wait. Building more than six is a bonus if parts and time allow.

### For December: Site A, 6 trees

Already covered by what's bought: ESP32 boards and antennas (10 for 6 + spares), 74AHCT125s, Mini560s and prototype boards (10 each), the PAM8610, a USB sound card, PG9 glands (Site A needs 6, one per tree box; 20 bought) and PG7 glands (6; 20 bought), Rob's DIN rail. The player is Rob's Pi 5 (`data/sites.json`); his Pi 3 is the bench player meanwhile.

| Qty | Item | Notes |
|---|---|---|
| 7 | 1×40 2.54mm female header strip | One strip per board: cut two 1×19 for the ESP32. 6 boards + 1 spare |
| 7 | DIP-14 socket | Unless Rob has enough |
| 14 | 2-way 5.08mm PCB screw terminal | JP (12V in) and JD (data out), 2 per board |
| 7 | 10kΩ resistor | R2 data pull-down, unless Rob has them |
| 7 | 0.1µF capacitor | Level-shifter decoupling |
| 20 | Wago 221-413 (3-way) | 2 per tree box (12) + the 12V and 0V commons in the site box (on DIN-rail carriers) + spare |
| 2 | Wago 221 DIN-rail mounting carriers (221-500) | Site box |
| 2 | Mean Well LRS-200-12 (12V 17A, enclosed, fanless, 215 × 115 × 30mm) | Site A's PSU (15.1A: trees at WLED's 2A cap, player and router; 89%) + 1 spare that covers any site (Rob, 26 Oct 2026: no outdoor PSUs). RS 106-5859, £30.56 ex VAT each (26 Oct 2026) |
| 1 | DRiBOX Large (internal 330 × 230 × 140mm at the top, narrower at the floor; IP55) | The site box: PSU, DIN rail, Pi, amp, router on a printed plate. £19.99, Amazon (Festive Lights), 26 Oct 2026 |
| 1 | Mains lead: 3-core 1.0mm² H05RN-F + 13A plug, 3A fuse | To the PSU's input terminals (under a printed cover), clamped on the plate; plugs into the RCD-protected outdoor socket |
| 1 | 12V→5V 5A buck with a USB-C lead, for the Pi 5 | After the player's 3A fuse. A plain buck can't do the Pi 5's USB-PD handshake: set `PSU_MAX_CURRENT=5000` in the Pi's EEPROM (`rpi-eeprom-config --edit`) so it trusts it. A Pi 3 would manage on 2.5A |
| 10 | DIN-rail 10×38 fuse holders (generic RT18-32 is fine at 12V) | 6 tree runs, the player and the router, + 2 spare, on Rob's DIN rail |
| 10 + 5 | 10×38 fuses: 3A (+ spares), 2A | 3A on every tree run and the player, 2A on the router (Rob, 26 Oct 2026) |
| 10 sets | PY07 Z108 2P bayonet waterproof connectors (IP67 mated, cable 3–8mm, solder) | One per tree run + spares. Socket on the run cable (powered side), pins on the tree's pigtail; red to +. No Z108 rating found; the PY07 series is ~4A on its small contacts, so the runs are fused 3A |
| 50m | 2-core 0.75mm² outdoor flex (H05RN-F rubber if you can) | Site A: 6 runs at the default 5m (electronics/site-wiring.md) + the trees' pigtails + the two speaker runs; outer diameter 3–8mm for the connectors and glands |
| 1 | Cudy WR3000 router (AX3000, vanilla OpenWrt), ~£30–40 | 12V 1A (the WR3000H is 1.5A); runs off the site PSU on a 2A fuse, so keep or cut the adapter's barrel lead. Check the hardware version is on the OpenWrt Table of Hardware before buying |
| 1 | High-endurance microSD | For the Pi 5. UK retailer, not AliExpress |
| 1 pair | Outdoor 8Ω speakers: PD BGO40 4" pair, IP56 | Stereo off the PAM8610, each on its own 2-core run (Rob, 26 Oct 2026). ElectroMarket, £53.99 (26 Oct 2026) |
| – | RCD-protected outdoor socket | Rob has one where the site box goes (26 Oct 2026). **TBC (Rob):** have the mains side checked by a competent electrician |
| – | Adhesive-lined heatshrink; PETG | Boots (12), tree boxes (6), the site box plate, pixel disks. Lid cord: Rob has it (tree boxes) |
| 552 + spares | Printed pixel disks (PETG, fixtures/pixel-disk.scad) | 92 per tree × 6, glued into the front counterbores (Rob, 25 Oct 2026). Print the test strip first for the bore |
| 1 pack | Hot-glue sticks (outdoor-rated if you can) | Pixel disks into the counterbores; CA or epoxy also work |
| 1 | MDF sheet, 18mm, blank + 50mm all round (~1000 × 500) | CNC fixture plate with the blank pocket (cad/fixture-plate.step). Unless Rob has one |
| 6 | Small TVS diodes (optional) | Data line protection |
| – | Exterior oil (e.g. Osmo UV) | |

### Later: sites B to D, trees 7 to 14 (or 15)

| Qty | Item | Notes |
|---|---|---|
| 6 | ESP32-DevKitC-32U (or -32UE) dev board, 38-pin | 16 = 14 + 2 spare (one more for a 15th tree). Espressif DevKitC pin layout (IO16 on J3 pin 12). Any USB chip (CP2102 or CH340) |
| 6 | 2.4GHz antenna: U.FL (IPEX-1) to RP-SMA bulkhead pigtail, 10–15cm, + RP-SMA dipole | The WROOM-32U has no antenna of its own; check the listing includes both parts |
| 6 | 74AHCT125N DIP-14 | 16 boards |
| 6 | Mini560 5V buck (fixed 5V version) | 16 boards |
| 6 | 5×7cm prototype boards | 16 boards |
| 9 | 1×40 female header strip, DIP-14 sockets, 10kΩ, 0.1µF (each) | The rest of the 16 boards |
| 18 | 2-way 5.08mm PCB screw terminal | The rest of the 16 boards |
| 20 | Wago 221-413 | Trees 7–14 and the other site boxes |
| 3 | Mean Well LRS-150-12 (site B) and 2 × LRS-100-12 (sites C, D) | electronics/site-wiring.md |
| 3 | DRiBOX (Large for B; C and D may fit a Medium) + mains leads | |
| 3 | 12V→5V buck for the players (Pi 3 / Pi 3 A+: 2.5A is enough) | One per site box |
| 11 | DIN-rail 10×38 fuse holders (+ fuses) | 8 tree runs (sites B 4, C 2, D 2) + 3 players |
| 10 sets | PY07 Z108 2P bayonet connectors | Trees 7–14 + spares |
| ~45m | 2-core 0.75mm² outdoor flex | The other sites' runs |
| 2 | Raspberry Pi 3 Model A+ (or any Pi) | Players for sites C and D; Rob's Pi 3 is Site B's. The Pi Hut, about £24 |
| 3 | High-endurance microSD | One per player |
| 3 | Cudy WR3000 router | One per site; out of season they become home mesh nodes |
| 3 pairs | Outdoor 8Ω speakers | One stereo pair per site |
| 8 | Small TVS diodes (optional) | |
| 736 + spares | Printed pixel disks (PETG) | 92 per tree × 8 (trees 7–14) |

## Fasteners (23 Oct 2026 designs)

Lids and box mounts use M3 brass heat-set inserts, not captive nuts: the screws sit 3.5mm from the box edge, where an M3 nut (6.4mm across corners) would break through the wall, and inserts take repeated lid opening better than nuts or self-tapping into PETG. Quantities include about 15% spare. "December" is Site A's 6 trees and one site box.

| December | All | Item | Where |
|---|---|---|---|
| 80 | 200 | M3 brass heat-set inserts, for a 4.0mm hole (e.g. M3 × 5 × 4.2 OD) | Tree box lid 6 + control-boot tower 4 = 10 per tree. Check the hole size against the ones Rob has (`m3_insert_d`) |
| 80 | 200 | M3 × 10 stainless button/pan head screws | Same places: 4mm lid frame or 5mm box ear + 6mm in the insert |
| 30 | 70 | M2 × 6 self-tapping screws for plastic | Controller board into its standoffs, 4 per board |
| 4 | 20 | M2.5 × 6 self-tapping screws for plastic | Pi into the site box plate's standoffs, 4 per site |
| 14 | 32 | 4 × 30 stainless countersunk wood screws | Through each peg's tab and the boot shaft into the old pilot hole, 2 per tree. Pilot hole size still to measure |
| 24 | 56 | 8mm × 200mm nails | Two per boot, two boots per tree (feet/) |
| 2 | 10 | 5 × 40 stainless exterior screws + washers | The DRiBOX to a post or fence, if it isn't left standing |
| 4 + 4 | 4 + 4 | M6 × 70 bolts and M6 spring channel nuts (short spring, 41×21 strut) | CNC clamps (fixtures/); the washers are printed. On the 18mm fixture plate (`spoil_t` 14) the echo gives 77mm: use M6 × 80 |
| 1 pack | 1 pack | Cable ties, up to 4.8mm wide | Site box plate tie points (5mm slots) |
| – | – | Superglue | Butt joints in the lid cord |

## Webcam (separate project)

A battery-powered WiFi camera in the hedge across the road. It streams the Site A shows live and records them for clips, for about £145–210 (an ESP32 from the tree spares switches it per show). Not needed for 1 Dec. Design, BOM, the music-copyright plan and the checks to do before buying are in [webcam.md](webcam.md).
