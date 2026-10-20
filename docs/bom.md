# Bill of materials

Kept current from CLAUDE.md §4. 14 trees, each with its own ESP32 controller; one show player per site (4 sites). Updated 20 Oct 2026 for the ESP32-per-tree design.

## Bought (AliExpress, ordered 18 Oct 2026, £277.80, due 25–31 Oct)

| Qty | Item | Notes |
|---|---|---|
| 14 | Ray Wu 12V WS2811 12mm bullet strings, 100 pixels, resistor type, black 18AWG, xConnect ends | One per tree. Cut the surplus 8 off each and keep as repair spares. Lead spacing not yet confirmed (probably 3–4 inch). |
| 2 lots (20 pairs) | Ray Wu xConnect 3-core 18AWG flat pigtails, 20cm | |
| 10 | PAM8610 amp boards | 4 needed (one per site); 6 spare |
| 10 | 74AHCT125N DIP-14 | One per tree; 4 more needed |
| – | Prototype boards, 5×7cm | |
| 7 | USB sound cards | 4 needed (one per site player); 3 spare |
| 15 | Micro-USB OTG cables | Spares |
| 10 | 2×20 pin headers | Spares |
| 10 | Mini560 5V buck | One per tree controller; 4 more needed |
| 20 + 20 | PG7 and PG9 cable glands | PG9: 12V flex into each tree box (14) + site boxes. PG7: pixel lead out of each tree box (14, via a short round tail, since the flat xConnect pigtail won't seal) + speaker cables (4). Enough. |

## Rob already has

DIP sockets, inline blade fuse holders and 5A fuses, M3 heat-set inserts and stainless screws, 33Ω resistors, 100µF capacitors.

## Still to buy

Decide the tree controller board after the M0 prototype before buying the ESP32s.

| Qty | Item | Notes |
|---|---|---|
| 14 | ESP32 tree controllers | DIY: ESP32-WROOM-32U dev board + external antenna, ~£5–6 each. Or ready-made 12V WLED boards with level shifting (QuinLED Dig-Uno, GledOpto), ~£15–30 each. TBC after M0. |
| 4 | 74AHCT125N DIP-14 | Only if DIY boards (10 already bought) |
| 4 | Mini560 5V buck | Only if DIY boards (10 already bought) |
| 2 | Raspberry Pi 3 Model A+ (or any Pi) | Show players for two sites; Rob's Pi 3 and Pi 5 are the other two. The Pi Hut, about £24. |
| 4 | High-endurance microSD | One per player. UK retailer, not AliExpress |
| 4 | Travel router (GL.iNet Mango, ~£27) | One per site, optional (Pi hotspot fallback) |
| 7 | Mean Well LPV-100-12 | One per two trees, genuine, UK distributor. TBC vs 14 × LPV-60-12 |
| ~60m | 3-core 0.75mm² outdoor flex | 12V runs to the trees; outer diameter < 8mm for the glands |
| – | Adhesive-lined heatshrink | |
| – | PETG, plus TPU or 3mm silicone cord | Enclosures, boots and gaskets |
| 4 | Speakers | One per site |
| – | 0.1µF capacitors | Level-shifter decoupling (M4) |
| 14 | Small TVS diodes (optional) | Data line protection at each tree controller |
| 56 | 8mm × 200mm nails | Two per boot, 28 boots (feet/) |
| 28 | 4mm stainless wood screws, ~25mm | Boot into the old pilot hole; length TBC on test-fit |
| – | Exterior oil (e.g. Osmo UV) | |
