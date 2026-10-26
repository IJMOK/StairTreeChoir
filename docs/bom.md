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
- 5A blade fuses (spares only: the runs are fused 3A in a blade fuse box, 26 Oct 2026)
- M3 heat-set inserts and stainless screws (count them against the fastener list below)
- 33Ω resistors, 100µF capacitors
- Lid sealing cord, RS 159-1490
- Cudy WR3000 router (bought by 26 Oct 2026): 12V 1A (the WR3000H is 1.5A); runs off the site PSU on a 2A fuse. Check the label and barrel polarity
- High-endurance microSD (bought; now in the Pi 3 bench player, FPP 10.3)

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

**The plan (Rob, 24 Oct 2026):** a minimum viable show of **6 trees at home (Site A) by 1 Dec 2026**. Buy the December list first; the later list is for sites B to D and trees 7 to 14 (or 15) and can wait. Building more than six is a bonus if parts and time allow.

### For December: Site A, 6 trees

Trimmed with Rob on 26 Oct 2026 to what he doesn't already have.

**Already covered** (bought or in hand): ESP32 boards and antennas (10), 74AHCT125s, Mini560s (10: 6 trees + the Pi 3 + 3 spare), prototype boards (10), the PAM8610, a USB sound card, PG9 and PG7 glands (20 each; Site A needs 6 of each), the Pi 3 player with its microSD, the Cudy WR3000, the RCD outdoor socket, a mains lead with a 13A plug, PETG, hot glue, heatshrink, lid cord, and 18mm sheet for the CNC fixture plate.

| Qty | Item | Notes | Approx. |
|---|---|---|---|
| 7 | 1×40 2.54mm female header strip | One per board: cut two 1×19 for the ESP32. 6 boards + 1 spare | £3 |
| 7 | DIP-14 socket | For the 74AHCT125 | £2 |
| 14 | 2-way 5.08mm PCB screw terminal | JP (12V in) and JD (data out), 2 per board | £3 |
| 7 + 7 | 10kΩ resistor, 0.1µF capacitor | R2 data pull-down; level-shifter decoupling. Rob has the 33Ω and 100µF | £2 |
| 1 | Mean Well LRS-200-12 (12V 17A, enclosed, fanless, 215 × 115 × 30mm) | Site A's PSU: 14.1A with the trees at WLED's 2A cap and the player (83%); the router is indoors on its own adapter. No spare for December (Rob, 26 Oct 2026); Site B's LRS-150-12 can stand in later. RS 106-5859, £30.56 ex VAT | £37 |
| 1 | DRiBOX Large (internal 330 × 230 × 140mm at the top, narrower at the floor; IP55) | The site box (PSU, fuses, Pi, amp; the router stays indoors). Amazon (Festive Lights), £19.99 | £20 |
| 1 | 10-way blade fuse box with a negative bus (marine type, screw or stud input) | Replaces the DIN fuse holders (Rob, 26 Oct 2026): 6 tree runs, the player, the router + 2 spare. Its negative bus is the 0V common, so the site box needs no Wagos | £8 |
| 10 | Blade fuses: 3A (standard ATO/ATC size, to suit the box) | Every tree run and the player. Rob's 5A blades are spares only | £3 |
| ~10m | Outdoor Cat6 (UV-rated), flat if it has to pass a window frame | Pi in the site box to the router indoors at the front window (Rob, 26 Oct 2026). Measure the route | £10 |
| 15 | Wago 221-413 (3-way) | 2 per tree box (12) + 3 spare | £10 |
| 10 sets | PY07 Z108 2P bayonet waterproof connectors (IP67 mated, cable 3–8mm, solder) | One per tree run + spares. Socket on the run (powered side), pins on the tree's pigtail; red to +. No Z108 rating found; the PY07 series is ~4A on its small contacts, so the runs are fused 3A. Check the price is per mated pair | £12 |
| ~35m | 2-core 0.75mm² outdoor flex (H05RN-F rubber if you can; 3-core is fine with the earth unused) | 6 runs at the default 5m (electronics/site-wiring.md) + the trees' pigtails. Rob has some flex but not enough (26 Oct 2026); buy the balance | £15–30 |
| 1 pair | PD BGO40 outdoor speakers (MPN 100.044): 4" + 3/4" dome, 8Ω, 30W RMS, 89dB 1W/1m, 100Hz–20kHz, IP56, 130 × 155 × 200mm, speaker cable included | Stereo off the PAM8610 (10W/ch into 8Ω). Chosen 26 Oct 2026 after UK eBay had no second-hand outdoor pairs. ElectroMarket | £51 |
| 6 | Small TVS diodes (optional) | Data line protection; skip for December | – |

Site A total: about **£185**, less whatever flex Rob already has. The pixel disks (552 + spares) are printed from `fixtures/pixel-disk.scad`; print the bore test strip first.

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
| 3 | Mini560 5V buck for the players (a Pi 3 / 3 A+ needs 2.5A; a Pi 5 needs 5A and `PSU_MAX_CURRENT=5000`) | One per site box; Site B's Pi 5 also needs its own microSD |
| 3 | Blade fuse boxes with a negative bus (+ 3A and 2A blades) | One per site box: the runs, the player and the router |
| 1 | Spare Mean Well LRS-200-12 | Covers any site; skipped for December |
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
