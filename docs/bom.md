# Bill of materials

Kept current from CLAUDE.md §4. 14 trees (maybe 15), each with its own ESP32 controller; one show player per site (4 sites). First goal: 6 trees at Site A by 1 Dec 2026. Updated 24 Oct 2026 with deliveries; pixel disks and the fixture plate added 25 Oct 2026; the 27 Oct orders added 28 Oct 2026; LRS-350-12, IEC inlet, XH-M541 and the tree mounts 15 Nov 2026; back to the S-400-12 16 Nov 2026.

## Bought

AliExpress order of 18 Oct 2026 (£277.80, due 25–31 Oct), plus the ESP32 order of 22 Oct.

| Qty | Item | Notes | Status |
|---|---|---|---|
| 14 | Ray Wu 12V WS2811 12mm bullet strings, 100 pixels, resistor type, black 18AWG, xConnect ends | One per tree. Cut the surplus 8 off each and keep as repair spares. Lead spacing not yet confirmed (probably 3–4 inch). | Due 25–31 Oct |
| 2 lots (20 pairs) | Ray Wu xConnect 3-core 18AWG flat pigtails, 20cm | | Due 25–31 Oct |
| 10 | PAM8610 amp boards | **Not used** (Rob, 15 Nov 2026: replaced by the XH-M541); all spare | Arrived 24 Oct |
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
| 1 pair | PD BGO40 outdoor speakers, black (MPN 100.044): 4" + 3/4" dome, 8Ω, 30W RMS, 89dB 1W/1m, 100Hz–20kHz, IP56, speaker cable included | Site A's stereo pair off the XH-M541. eBay listing called them "BC040" but the box says BGO40 (Rob, 28 Oct 2026); £15.88 against £51 at ElectroMarket. eBay (zahumble-0), order 09-15354-62517 | Arrived 28 Oct |
| 25 | Wago 221-413 (3-way) | 12 for Site A's tree boxes + 13 toward trees 7–14. CPC CN20136, order 21543768 | Arrived by 30 Oct |
| 50m | Pro Power H05RR-F 2-core 0.75mm² rubber cable, black | Site A's ~35m of runs + ~15m toward the later sites. H05RR-F is lighter duty than H05RN-F but fine laid on the ground for a season. CPC CB19470 (order 21543768 also lists SU00243, 1 off) | Arrived by 30 Oct |
| 15 sets | SP16/SP17 2-pin screw-terminal aviation connectors (solderless): SP16 panel socket (rear nut, M16 × 1.5, 17mm hole with two flats 15.5mm across, measured 4 Nov 2026) + SP17 cable plug | Replace the PY07 Z108 bayonets: one per tree run, 14 trees + 1 spare. SP17 2-pin is rated 10A, IP68 mated, cable 6–10mm (SP16 is smaller: check the H05RR-F sheath fits the gland). The SP16 goes in the tree box floor, firing down (Rob, 28 Oct 2026); the SP17 goes on the tree end of the run. Red to +. Check which half has the pins when they arrive (due 7 Nov): the powered run should carry the shrouded contacts. AliExpress (Ti Socket Store), 10 + 5 sets, £32.06 | Arrived 4 Nov |

Orders of 31 Oct 2026:

| Qty | Item | Notes | Status |
|---|---|---|---|
| 2 | DRiBOX DB-330-UK-B, black, 140 × 230 × 330mm | Site A's site box + 1 toward Site B. CPC EN82293 | Ordered 31 Oct (CPC, £75.38 ex VAT, £90.46 total) |
| 1 | Multicomp PPFH-76ATO10 fuse box: 10 × ATO, 30A per way, 100A in, 32V DC, 6.35mm Faston outs, 10-32 stud in, LED on a blown fuse | **No negative bus listed**, so 0V joins on two Wago 221-415 instead. CPC FF02310. Measure it against the 150 × 65 space, and see how the LEDs are wired, when it arrives | Same order |
| 20 | Littelfuse 0287003.PXCN ATO blade fuse, 3A | CPC FF02734 | Same order |
| 100 | 100µF 10V electrolytic, 5 × 11 (MCGPR10V107M5X11) | C1. 10V rather than 16V, fine on the 5V rail. CPC CA08547 | Same order |
| 20 | 0.1µF 100V X7R ceramic, 5.08mm (MCRR50104X7RK0100) | C2. Tight beside U1: lean it away from the chip. CPC CA05520 | Same order |
| 100 + 100 | 10kΩ and 33Ω, 0.25W | R2 and R1. CPC RE03815, RE03786 | Same order |
| 1 | Pro Signal Cat6 UTP flat patch lead, 10m | Pi to router. Not the outdoor UV-rated cable first listed: fine for a season, keep the plugs dry; measure the route. CPC CS38194 | Same order |
| 100 | 0.1µF 63V electrolytic (MCMR63V104M4X7) | **Do not fit as C2**: polarised, and too slow for decoupling. Ordered by mistake. CPC CA08189 | Same order |
| 1 + 1 | 100m 13 × 0.2mm figure-8 speaker cable, white; 2m HDMI lead | Not on the list. Speaker cable is too thin for the 12V runs. CPC CB17775, AV23428 | Same order |
| 30m | 18AWG silicone wire, 6 colours | Tree box tails. Not for the PSU feed to the fuse box (about 14A) | AliExpress, due 5–8 Nov |
| 120 | 24AWG tinned jumper wires, 8cm | Underside joins on the boards | AliExpress, due 5–8 Nov |
| 800 | Twill-knurled M2 + M3 heat-set inserts | Sizes not stated: try them on the coupon (`standoff_hole` 3.2, `m3_insert_d` 4.0) | AliExpress, due 5–8 Nov |

Orders of mid-November 2026 (Rob, 15 Nov 2026):

| Qty | Item | Notes | Status |
|---|---|---|---|
| 1 | S-400-12 (12V 33A, 217 × 114 × 50mm, fan, 115/230V switch) | Site A's PSU: 14.1A of 33A. The LRS-350-12 ordered for it arrived as an LRS-350-24 (16 Nov 2026), which is no use at 12V. Under the printed hood `print/psu-hood.stl` | Have |
| 1 | Mean Well LRS-350-12 (215 × 115 × 30) | Ordered again 17 Nov 2026 as Site A's other option; its own hood `print/psu-hood-lrs.stl` | Ordered |
| 1 | XH-M541 stereo amp board (TPA3116D2, DC 12–24V, 3.5mm input, screw speaker terminals) | Site A's amp, replacing the PAM8610. Listings disagree on power (50–60W a channel into 4Ω; far less into the 8Ω BGO40s at 12V, plenty). **Measure it** and its power input (likely a 5.5 × 2.1 barrel) when it arrives | On order |
| 1 | 3-in-1 IEC C14 inlet module: fused (5 × 20mm), switched, screw mounting (panel cut-out 47.3 × 27.4, holes 3.5mm, 40 apart) | In the PSU hood's mains side wall. Rob's drawing, 15 Nov 2026 | To buy if not in hand |

## Rob already has

- 5A blade fuses (spares only: the runs are fused 3A in a blade fuse box, 26 Oct 2026)
- M3 heat-set inserts and stainless screws (count them against the fastener list below)
- Lid sealing cord, RS 159-1490
- High-endurance microSD (bought; now in the Pi 3 bench player, FPP 10.3)

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

**The plan (Rob, 24 Oct 2026):** a minimum viable show of **6 trees at home (Site A) by 1 Dec 2026**. Buy the December list first; the later list is for sites B to D and trees 7 to 14 (or 15) and can wait. Building more than six is a bonus if parts and time allow.

### For December: Site A, 6 trees

Trimmed with Rob on 26 Oct 2026 to what he doesn't already have.

**Already covered** (bought or in hand): ESP32 boards and antennas (10, 1 of each now on the wreath), 74AHCT125s, Mini560s (10: wreath + 6 trees + the Pi 3 + 2 spare), prototype boards (10), a USB sound card, PG7 glands (20; Site A needs 6), the Pi 3 player with its microSD, the Cudy WR3000 V1, the 27 Oct orders (Wagos, 50m of flex, the aviation connectors, the BGO40 speakers), the 31 Oct orders (DRiBOX, fuse box, fuses, R1, R2, C1, C2, a Cat6 lead, heat-set inserts, wire), the RCD outdoor socket, a mains lead with a 13A plug, PETG, hot glue, heatshrink, lid cord, and 18mm sheet for the CNC fixture plate.

| Qty | Item | Notes | Approx. |
|---|---|---|---|
| 6 | 2-way 5.08mm PCB screw terminal | JD (data out), 1 per board. Rob found some KF2EDG-2P: count them first | £2 |
| 1 | IEC C13 mains lead, 13A plug with a **5A** fuse, 2m+ (or an angled C13) | Into the PSU hood's inlet, through a lid seal. 5A in the plug for the PSU's cold-start inrush (the S-400-12's isn't known: bench it); the inlet holds the T-fuse | £5 |
| 2 | 5 × 20mm time-lag fuses, T4A 250V (ceramic, H) | The IEC inlet: one fitted, one spare. Under 1A at 230V for Site A's load | £2 |
| 4 + 2 | M4 × 6 stainless pan head + M4 washer; M3 × 10 + M3 nyloc | Hood to the PSU's side holes (no longer than 6, with the washer: about 3mm max into the S-400's case); the inlet to the hood | £2 |
| 1 pack | Fully insulated 6.3mm female spade crimps (0.5–1.5mm²) and fork crimps for M3.5 terminals | Every mains tab on the inlet, and the PSU's terminals | £4 |
| 1 | 3.5mm stereo jack lead, 30cm | Sound card to the XH-M541's input | £2 |
| 1 | DC barrel lead (5.5 × 2.1, check the XH-M541) with bare ends | Amp power from its fuse and the 0V Wago | £2 |
| 2 | Wago 221-415 (5-way) | Site A's 0V join, since the fuse box has no negative bus: PSU − and a link wire + 3 returns in one, the link + 4 returns in the other | £2 |
| 8 | 6.3mm insulated female crimps, red (0.5–1.5mm²) | The fuse box's Faston outputs | £2 |
| 1 + ~1m | Ring terminal for the 10-32 stud (about M5) + about 2.5mm² wire | PSU +12V to the fuse box, up to about 14A | £3 |
| 6 | Small TVS diodes (optional) | Data line protection; skip for December | – |

Still to buy for Site A: about **£27** plus the fasteners below (and the inlet, if not in hand). Everything printed is in [print/](../print/README.md): pixel disks (552 + spares), 6 tree boxes, 18 sockets, 12 display stands and 24 pole caps, the PSU hood and the buck pod; 18 storage towers before the season ends. Plus 12 lengths of 11mm fibreglass tent pole, 400mm each (below).

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
| 3 | Mean Well LRS-150-12 (site B) and 2 × LRS-100-12 (sites C, D) | electronics/site-wiring.md. Each needs its own hood (a copy of psu-cover.FCStd sized to it) and inlet |
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
| 3 | XH-M541 amps (or similar, 12V) | One per site |
| 8 | Small TVS diodes (optional) | |
| 736 + spares | Printed pixel disks (PETG) | 92 per tree × 8 (trees 7–14) |
| 24 + 16 + 32 + 24 | Printed sockets, display stands, pole caps, storage towers (PETG) | Trees 7–14 |
| 16 × 400mm | 11mm fibreglass tent pole | Trees 7–14, two per tree |

## Fasteners

Lids and box mounts use brass heat-set inserts, not captive nuts: the screws sit 3.5mm from the box edge, where an M3 nut (6.4mm across corners) would break through the wall, and inserts take repeated lid opening better than nuts or self-tapping into PETG. Quantities include about 15% spare. "December" is Site A's 6 trees and one site box.

| December | All | Item | Where |
|---|---|---|---|
| 7 | 16 | M3 brass heat-set inserts, for a 4.0mm hole (CNC Kitchen / Ruthex M3 × 5.7) | Tree box: 1 per tree, in the shelf's block for the cover screw (30 Oct 2026). Check the hole size against the ones Rob has (`m3_insert_d`) |
| 7 | 16 | M3 × 10 stainless button/pan head screws | The cover's bevel into the shelf's insert, 1 per tree |
| 28 | 64 | 4 × 40 stainless pan-head wood screws + washers | Tree box to the back of the tree, through the flange slots and 10mm printed spacers, 4 per tree |
| 28 | 64 | M2 brass heat-set inserts, about 4mm long, for a 3.2mm hole | Controller board standoffs, 4 per board (Rob, 31 Oct 2026). Check the hole against the real inserts (`standoff_hole`) |
| 28 | 64 | M2 × 6 stainless pan-head machine screws | Controller board into the standoff inserts, 4 per board |
| 84 | 192 | 4 × 16 stainless countersunk wood screws | Sockets, 4 each (2 through the back leg, 2 through the front), 3 sockets per tree (15 Nov 2026). Not longer: two from opposite faces must not meet in 30mm of oak |
| 28 | 64 | 8mm peg stakes, about 200mm | One through each pole cap's pad, four per tree (Rob, 16 Nov 2026: tent-pole feet; the hole takes up to 9mm) |
| 12 × 400mm | 28 × 400mm | 11mm fibreglass tent pole (plain lengths: a ferrule won't go through the stand) | Feet: one through each display stand, front to back, 2 per tree. Cut with a fine hacksaw, tape round the cut, sand the ends |
| 2 | 10 | 5 × 40 stainless exterior screws + washers | The DRiBOX to a post or fence, if it isn't left standing |
| 4 + 4 | 4 + 4 | M6 × 70 bolts and M6 spring channel nuts (short spring, 41×21 strut) | CNC clamps (cad/parts/step-clamp.FCStd); the washers are printed. On the 18mm fixture plate (`spoil_t` 14) the echo gives 77mm: use M6 × 80 |
| 1 pack | 1 pack | Cable ties, up to 4.8mm wide | Buck pod and PSU hood tie slots |
| – | – | Superglue | Butt joints in the lid cord |

## Webcam (separate project)

A battery-powered WiFi camera in the hedge across the road. It streams the Site A shows live and records them for clips, for about £145–210 (an ESP32 from the tree spares switches it per show). Not needed for 1 Dec. Design, BOM, the music-copyright plan and the checks to do before buying are in [webcam.md](webcam.md).
