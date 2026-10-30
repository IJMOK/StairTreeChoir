# Bill of materials

Kept current from CLAUDE.md §4. 14 trees (maybe 15), each with its own ESP32 controller; one show player per site (4 sites). First goal: 6 trees at Site A by 1 Dec 2026. Updated 24 Oct 2026 with deliveries; pixel disks and the fixture plate added 25 Oct 2026; the 27 Oct orders added 28 Oct 2026.

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
| 20 + 20 | PG7 and PG9 cable glands | Needed: PG7 14 = the tree boxes' pixel lead. PG9 no longer needed: the 12V run plugs into an SP16 panel socket in the tree box floor (28 Oct 2026), so the PG9s are spares. The site box is now a DRiBOX, whose lid seals clamp the cables, so it needs no glands (26 Oct 2026). Both are covered. | Arrived 24 Oct |
| 10 | ESP32-DevKitC-32U dev board, 38-pin | 16 needed; 6 more to buy | Arrived 30 Oct |
| 10 | 2.4GHz antenna: U.FL to RP-SMA bulkhead pigtail + RP-SMA dipole | 16 needed; 6 more to buy | Arrived 30 Oct |

Orders of 27 Oct 2026 (Site A wiring, speakers, router):

| Qty | Item | Notes | Status |
|---|---|---|---|
| 1 | Cudy WR3000 V1 (AX3000; listed as V2, but the unit reports `cudy,wr3000-v1`) | Site A router, indoors at the front of the house, on OpenWrt 25.12.6. eBay (lekafindslimited), £29.99, order 11-15340-22895 | Arrived 29 Oct |
| 1 pair | PD BGO40 outdoor speakers, black (MPN 100.044): 4" + 3/4" dome, 8Ω, 30W RMS, 89dB 1W/1m, 100Hz–20kHz, IP56, speaker cable included | Site A's stereo pair off the PAM8610. eBay listing called them "BC040" but the box says BGO40 (Rob, 28 Oct 2026); £15.88 against £51 at ElectroMarket. eBay (zahumble-0), order 09-15354-62517 | Arrived 28 Oct |
| 25 | Wago 221-413 (3-way) | 12 for Site A's tree boxes + 13 toward trees 7–14. CPC CN20136, order 21543768 | Arrived by 30 Oct |
| 50m | Pro Power H05RR-F 2-core 0.75mm² rubber cable, black | Site A's ~35m of runs + ~15m toward the later sites. H05RR-F is lighter duty than H05RN-F but fine laid on the ground for a season. CPC CB19470 (order 21543768 also lists SU00243, 1 off) | Arrived by 30 Oct |
| 15 sets | SP16/SP17 2-pin screw-terminal aviation connectors (solderless): SP16 panel socket (rear nut, M16 × 1.5, D hole 16.5mm with a flat at 15.3mm) + SP17 cable plug | Replace the PY07 Z108 bayonets: one per tree run, 14 trees + 1 spare. SP17 2-pin is rated 10A, IP68 mated, cable 6–10mm (SP16 is smaller: check the H05RR-F sheath fits the gland). The SP16 goes in the tree box floor, firing down (Rob, 28 Oct 2026); the SP17 goes on the tree end of the run. Red to +. Check which half has the pins when they arrive (due 7 Nov): the powered run should carry the shrouded contacts. AliExpress (Ti Socket Store), 10 + 5 sets, £32.06 | Shipped 28 Oct, due 7 Nov |

## Rob already has

- 5A blade fuses (spares only: the runs are fused 3A in a blade fuse box, 26 Oct 2026)
- M3 heat-set inserts and stainless screws (count them against the fastener list below)
- 33Ω resistors, 100µF capacitors
- Lid sealing cord, RS 159-1490
- High-endurance microSD (bought; now in the Pi 3 bench player, FPP 10.3)

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

**The plan (Rob, 24 Oct 2026):** a minimum viable show of **6 trees at home (Site A) by 1 Dec 2026**. Buy the December list first; the later list is for sites B to D and trees 7 to 14 (or 15) and can wait. Building more than six is a bonus if parts and time allow.

### For December: Site A, 6 trees

Trimmed with Rob on 26 Oct 2026 to what he doesn't already have.

**Already covered** (bought or in hand): ESP32 boards and antennas (10), 74AHCT125s, Mini560s (10: 6 trees + the Pi 3 + 3 spare), prototype boards (10), the PAM8610, a USB sound card, PG7 glands (20; Site A needs 6), the Pi 3 player with its microSD, the Cudy WR3000 V1, the 27 Oct orders (Wagos, 50m of flex, the aviation connectors, the BGO40 speakers), the RCD outdoor socket, a mains lead with a 13A plug, PETG, hot glue, heatshrink, lid cord, and 18mm sheet for the CNC fixture plate.

| Qty | Item | Notes | Approx. |
|---|---|---|---|
| 7 | 2-way 5.08mm PCB screw terminal | JD (data out), 1 per board; 12V no longer reaches the board | £2 |
| 7 + 7 | 10kΩ resistor, 0.1µF capacitor | R2 data pull-down; level-shifter decoupling. Rob has the 33Ω and 100µF | £2 |
| 1 | Mean Well LRS-200-12 (12V 17A, enclosed, fanless, 215 × 115 × 30mm) | **Not needed for December (30 Oct 2026):** Site A uses Rob's S-400-12 (12V 33A, 217 × 114 × 50mm, temperature-controlled fan) with `enclosure/psu-cover.scad`. Was Site A's PSU: 14.1A with the trees at WLED's 2A cap and the player (83%); the router is indoors on its own adapter. No spare for December (Rob, 26 Oct 2026); Site B's LRS-150-12 can stand in later. RS 106-5859, £30.56 ex VAT | £37 |
| 1 | DRiBOX Large (internal 330 × 230 × 140mm at the top, narrower at the floor; IP55) | The site box (PSU, fuses, Pi, amp; the router stays indoors). Amazon (Festive Lights), £19.99 | £20 |
| 1 | 10-way blade fuse box with a negative bus (marine type, screw or stud input) | Replaces the DIN fuse holders (Rob, 26 Oct 2026): 6 tree runs and the player + 3 spare (the router is indoors). Its negative bus is the 0V common, so the site box needs no Wagos | £8 |
| 10 | Blade fuses: 3A (standard ATO/ATC size, to suit the box) | Every tree run and the player. Rob's 5A blades are spares only | £3 |
| ~10m | Outdoor Cat6 (UV-rated), flat if it has to pass a window frame | Pi in the site box to the router indoors at the front window (Rob, 26 Oct 2026). Measure the route | £10 |
| 6 | Small TVS diodes (optional) | Data line protection; skip for December | – |

Still to buy for Site A: about **£90** (the 27 Oct orders covered the Wagos, flex, connectors and speakers, about £77 plus CPC). The pixel disks (552 + spares) are printed from `fixtures/pixel-disk.scad`; print the bore test strip first.

### Later: sites B to D, trees 7 to 14 (or 15)

| Qty | Item | Notes |
|---|---|---|
| 6 | ESP32-DevKitC-32U (or -32UE) dev board, 38-pin | 16 = 14 + 2 spare (one more for a 15th tree). Espressif DevKitC pin layout (IO16 on J3 pin 12). Any USB chip (CP2102 or CH340) |
| 6 | 2.4GHz antenna: U.FL (IPEX-1) to RP-SMA bulkhead pigtail, 10–15cm, + RP-SMA dipole | The WROOM-32U has no antenna of its own; check the listing includes both parts |
| 6 | 74AHCT125N DIP-14 | 16 boards |
| 6 | Mini560 5V buck (fixed 5V version) | 16 boards |
| 6 | 5×7cm prototype boards | 16 boards |
| 9 | 10kΩ, 0.1µF (each) | The rest of the 16 boards (no sockets or female headers: Rob solders the ESP32 and the 74AHCT125 in, 28 Oct 2026) |
| 9 | 2-way 5.08mm PCB screw terminal | The rest of the 16 boards |
| 0 | Wago 221-413 | 13 left over from the 27 Oct CPC order cover trees 7–14 (16) less 3; buy a 10-pack if the site boxes need any |
| 3 | Mean Well LRS-150-12 (site B) and 2 × LRS-100-12 (sites C, D) | electronics/site-wiring.md |
| 3 | DRiBOX (Large for B; C and D may fit a Medium) + mains leads | |
| 3 | Mini560 5V buck for the players (a Pi 3 / 3 A+ needs 2.5A; a Pi 5 needs 5A and `PSU_MAX_CURRENT=5000`) | One per site box; Site B's Pi 5 also needs its own microSD |
| 3 | Blade fuse boxes with a negative bus (+ 3A and 2A blades) | One per site box: the runs, the player and the router |
| 1 | Spare Mean Well LRS-200-12 | Covers any site; skipped for December |
| 0 | SP16/SP17 2-pin aviation connectors | The 15 sets bought 27 Oct cover all 14 runs + 1 spare; buy a few more spares |
| ~30m | 2-core 0.75mm² rubber flex | The other sites' runs, less the ~15m left from the 50m reel |
| 2 | Raspberry Pi 3 Model A+ (or any Pi) | Players for sites C and D; Rob's Pi 3 is Site B's. The Pi Hut, about £24 |
| 3 | High-endurance microSD | One per player |
| 3 | Cudy WR3000 router (check V1 or V2 on arrival: listings mix them up, and each needs its own OpenWrt image) | One per site; out of season they become home mesh nodes |
| 3 pairs | Outdoor 8Ω speakers | One stereo pair per site |
| 8 | Small TVS diodes (optional) | |
| 736 + spares | Printed pixel disks (PETG) | 92 per tree × 8 (trees 7–14) |

## Fasteners (23 Oct 2026 designs)

Lids and box mounts use M3 brass heat-set inserts, not captive nuts: the screws sit 3.5mm from the box edge, where an M3 nut (6.4mm across corners) would break through the wall, and inserts take repeated lid opening better than nuts or self-tapping into PETG. Quantities include about 15% spare. "December" is Site A's 6 trees and one site box.

| December | All | Item | Where |
|---|---|---|---|
| 30 | 70 | M3 brass heat-set inserts, for a 4.0mm hole (CNC Kitchen / Ruthex M3 × 5.7) | Tree box: 1 per tree, in the shelf's block for the cover screw (30 Oct 2026). Check the hole size against the ones Rob has (`m3_insert_d`) |
| 30 | 70 | M3 × 10 stainless button/pan head screws | The cover's bevel into the shelf's insert, 1 per tree |
| 28 | 64 | 4 × 40 stainless pan-head wood screws + washers | Tree box to the back of the tree, through the flange slots and 10mm printed spacers, 4 per tree |
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
