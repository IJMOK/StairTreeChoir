# Bill of materials

Kept current from CLAUDE.md §4. 14 trees, each with its own ESP32 controller; one show player per site (4 sites). Updated 24 Oct 2026 with deliveries.

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
| 20 + 20 | PG7 and PG9 cable glands | Needed (23 Oct 2026 design): PG9 35 = 14 tree boxes + 7 PSU inputs and 14 tree runs at the site boxes; PG7 18 = 14 tree boxes + 4 speakers. PG7 is covered; PG9 is 15 short (see Still to buy). | Arrived 24 Oct |
| 10 | ESP32-DevKitC-32U dev board, 38-pin | 16 needed; 6 more to buy | Ordered 22 Oct (AliExpress) |
| 10 | 2.4GHz antenna: U.FL to RP-SMA bulkhead pigtail + RP-SMA dipole | 16 needed; 6 more to buy | Ordered 22 Oct (AliExpress) |

## Rob already has

- DIP sockets
- 5A blade fuses (now in a fuse block in each site box, not inline at the trees)
- M3 heat-set inserts and stainless screws (count them against the fastener list below)
- 33Ω resistors, 100µF capacitors
- Lid sealing cord, RS 159-1490

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

| Qty | Item | Notes |
|---|---|---|
| 6 | ESP32-DevKitC-32U (or -32UE) dev board, 38-pin | 10 ordered 22 Oct; 16 = 14 + 2 spare. Espressif DevKitC pin layout (IO16 on J3 pin 12). Any USB chip (CP2102 or CH340). |
| 6 | 2.4GHz antenna: U.FL (IPEX-1) to RP-SMA bulkhead pigtail, 10–15cm, + RP-SMA dipole | 10 ordered 22 Oct. The WROOM-32U has no antenna of its own; check the listing includes both parts |
| 15+ | PG9 cable glands | 20 bought, 35 needed; plus a few spare |
| 6 | 74AHCT125N DIP-14 | 10 already bought; 16 boards |
| 6 | Mini560 5V buck (fixed 5V version) | 10 already bought; 16 boards |
| 16 | 1×40 2.54mm female header strip | Cut two 1×19 per board for the ESP32 |
| 16 | DIP-14 socket | Unless Rob has enough |
| 32 | 2-way 5.08mm PCB screw terminal | JP (12V in) and JD (data out) |
| 16 | 10kΩ resistor | R2 data pull-down, unless Rob has them |
| 28 | Wago 221-413 (3-way) | 12V and GND split in each tree box |
| 6 | 5×7cm prototype boards | 10 bought; 16 boards |
| 2 | Raspberry Pi 3 Model A+ (or any Pi) | Show players for two sites; Rob's Pi 3 and Pi 5 are the other two. The Pi Hut, about £24. |
| 4 | High-endurance microSD | One per player. UK retailer, not AliExpress |
| 4 | Travel router (GL.iNet Mango, ~£27) | One per site, optional (Pi hotspot fallback) |
| 8 | Mean Well LPV-100-12 (12V 8.5A, IP67) | One per pair of trees, all at the site box; 7 + 1 spare. Genuine, UK distributor: ~£28 ex VAT, in stock at Future House Store (checked 23 Oct 2026) |
| ~80m | 3-core 0.75mm² outdoor flex | 12V runs to the trees (electronics/site-wiring.md: 77m at the default 5m runs); outer diameter < 8mm for the glands |
| – | Adhesive-lined heatshrink | |
| – | PETG; 2.7mm rubber cord (Rob has it, RS 159-1490) | Boots and enclosures; the cord seals the box lids (~0.35m per tree box, ~0.8m per site box: about 8m for everything) |
| 4 | Speakers | One per site |
| – | 0.1µF capacitors | Level-shifter decoupling (M4) |
| 14 | Small TVS diodes (optional) | Data line protection at each tree controller |
| – | Exterior oil (e.g. Osmo UV) | |

## Fasteners (23 Oct 2026 designs)

Lids and box mounts use M3 brass heat-set inserts, not captive nuts: the screws sit 3.5mm from the box edge, where an M3 nut (6.4mm across corners) would break through the wall, and inserts take repeated lid opening better than nuts or self-tapping into PETG. Quantities include about 15% spare.

| Qty | Item | Where |
|---|---|---|
| 200 | M3 brass heat-set inserts, for a 4.0mm hole (e.g. M3 × 5 × 4.2 OD) | Tree box lid 6 + control-boot tower 4 = 10 per tree (140); site box lid 8 per site (32). Check the hole size against the ones Rob has (`m3_insert_d`) |
| 200 | M3 × 10 stainless button/pan head screws | Same places: 4mm lid frame or 5mm box ear + 6mm in the insert |
| 70 | M2 × 6 self-tapping screws for plastic | Controller board into its standoffs, 4 per board (16 boards) |
| 20 | M2.5 × 6 self-tapping screws for plastic | Pi into the site box standoffs, 4 per site |
| 32 | 4 × 30 stainless countersunk wood screws | Through each peg's tab and the boot shaft into the old pilot hole, 2 per tree. Pilot hole size still to measure |
| 56 | 8mm × 200mm nails | Two per boot, 28 boots (feet/) |
| 10 | 5 × 40 stainless exterior screws + washers | Site box lugs to a post or fence, 2 per box |
| 4 + 4 | M6 × 70 bolts and M6 spring channel nuts (short spring, 41×21 strut) | CNC clamps (fixtures/); the washers are printed |
| 1 pack | Cable ties, up to 4.8mm wide | Site box zip-tie anchors (5mm slots) |
| – | Superglue | Butt joints in the lid cord |
