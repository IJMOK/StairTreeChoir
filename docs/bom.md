# Bill of materials

Kept current from CLAUDE.md §4. 14 trees, each with its own ESP32 controller; one show player per site (4 sites). Updated 20 Oct 2026 for the ESP32-per-tree design.

## Bought (AliExpress, ordered 18 Oct 2026, £277.80, due 25–31 Oct)

| Qty | Item | Notes |
|---|---|---|
| 14 | Ray Wu 12V WS2811 12mm bullet strings, 100 pixels, resistor type, black 18AWG, xConnect ends | One per tree. Cut the surplus 8 off each and keep as repair spares. Lead spacing not yet confirmed (probably 3–4 inch). |
| 2 lots (20 pairs) | Ray Wu xConnect 3-core 18AWG flat pigtails, 20cm | |
| 10 | PAM8610 amp boards | 4 needed (one per site); 6 spare |
| 10 | 74AHCT125N DIP-14 | One per tree; 6 more for 16 boards |
| – | Prototype boards, 5×7cm | Tree controller boards (count TBC on arrival) |
| 7 | USB sound cards | 4 needed (one per site player); 3 spare |
| 15 | Micro-USB OTG cables | Spares |
| 10 | 2×20 pin headers | Spares |
| 10 | Mini560 5V buck | One per tree controller; 6 more for 16 boards |
| 20 + 20 | PG7 and PG9 cable glands | PG9: 12V flex into each tree box (14) + site boxes. PG7: pixel lead out of each tree box (14, via a short round tail, since the flat xConnect pigtail won't seal) + speaker cables (4). Enough. |

## Rob already has

DIP sockets, 5A blade fuses (now in a fuse block in each site box, not inline at the trees), M3 heat-set inserts and stainless screws, 33Ω resistors, 100µF capacitors.

## Still to buy

Tree controller: DIY boards (Rob, 21 Oct 2026). See electronics/README.md.

| Qty | Item | Notes |
|---|---|---|
| 16 | ESP32-DevKitC-32U (or -32UE) dev board, 38-pin | 14 + 2 spare. Espressif DevKitC pin layout (IO16 on J3 pin 12). Any USB chip (CP2102 or CH340). |
| 16 | 2.4GHz antenna: U.FL (IPEX-1) to RP-SMA bulkhead pigtail, 10–15cm, + RP-SMA dipole | The WROOM-32U has no antenna of its own; check the listing includes both parts |
| 6 | 74AHCT125N DIP-14 | 10 already bought; 16 boards |
| 6 | Mini560 5V buck (fixed 5V version) | 10 already bought; 16 boards |
| 16 | 1×40 2.54mm female header strip | Cut two 1×19 per board for the ESP32 |
| 16 | DIP-14 socket | Unless Rob has enough |
| 32 | 2-way 5.08mm PCB screw terminal | JP (12V in) and JD (data out) |
| 16 | 10kΩ resistor | R2 data pull-down, unless Rob has them |
| 28 | Wago 221-413 (3-way) | 12V and GND split in each tree box |
| 16 | 5×7cm prototype boards | Unless the bought pack has enough |
| 2 | Raspberry Pi 3 Model A+ (or any Pi) | Show players for two sites; Rob's Pi 3 and Pi 5 are the other two. The Pi Hut, about £24. |
| 4 | High-endurance microSD | One per player. UK retailer, not AliExpress |
| 4 | Travel router (GL.iNet Mango, ~£27) | One per site, optional (Pi hotspot fallback) |
| 8 | Mean Well LPV-100-12 (12V 8.5A, IP67) | One per pair of trees, all at the site box; 7 + 1 spare. Genuine, UK distributor: ~£28 ex VAT, in stock at Future House Store (checked 23 Oct 2026) |
| ~60m | 3-core 0.75mm² outdoor flex | 12V runs to the trees; outer diameter < 8mm for the glands |
| – | Adhesive-lined heatshrink | |
| – | PETG, plus TPU or 3mm silicone cord | Enclosures, boots and gaskets |
| 4 | Speakers | One per site |
| – | 0.1µF capacitors | Level-shifter decoupling (M4) |
| 14 | Small TVS diodes (optional) | Data line protection at each tree controller |
| 56 | 8mm × 200mm nails | Two per boot, 28 boots (feet/) |
| 28 | 4mm stainless wood screws, ~25mm | Boot into the old pilot hole; length TBC on test-fit |
| – | Exterior oil (e.g. Osmo UV) | |
