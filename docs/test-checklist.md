# Test checklist

Tick-box checks for the build in [build-guide.md](build-guide.md). Print one sheet per tree, box and site, and write the readings in the blanks. If a check fails, stop and fix it before going on: most of these protect an ESP32 or a string of pixels.

Limits come from [electronics/README.md](../electronics/README.md), [electronics/site-wiring.md](../electronics/site-wiring.md) and [CLAUDE.md](../CLAUDE.md). Where no pass limit is decided it says **TBC (Rob)**.

## A. Per tree board (bench, before pixels)

Tree no. ____  Board no. ____  Date ____

- [ ] 74AHCT125 sits in a DIP-14 socket, notch to the right (towards R1)
- [ ] Mini560 is the fixed 5V version
- [ ] All joins in [connections.md](../electronics/connections.md) made and ticked off

With the ESP32, U1 and the Mini560 not yet plugged in or powered:
- [ ] 12V is not shorted to 5V or GND
- [ ] 5V is not shorted to GND
- [ ] 12V reaches only JP 12V and the Mini560 IN+ pad

Power-up on the bench supply, 12V, current limit 200mA, **ESP32 not yet fitted**:
- [ ] Mini560 output: ____ V (pass: 5.0V plus or minus 0.1V)
- [ ] At J2.19 (the ESP32's 5V pin): ____ V (same pass)
- [ ] At U1.14 (socket pin 14): ____ V (same pass)
- [ ] Every reading is in range, so the ESP32 may go in

With U1 and the ESP32 fitted (antenna end left):
- [ ] ESP32 LED lights
- [ ] Current at 12V: ____ mA (pass: under 150mA)
- [ ] WLED joins Wi-Fi: hostname `stairtree-____`, IP 192.168.8.____
- [ ] USB is not connected while the 12V is on
- [ ] Data line (JD DATA) stays low through a power-up, with no random flash on the pixels (R2 pull-down)

## B. Per tree after pixels

Tree no. ____

String and wiring:
- [ ] 92 disks glued in flush, bores clear of glue
- [ ] Pixels fitted in node order 1 to 92, clips snapped behind the disks, with the surplus 8 cut off and the end sealed
- [ ] xConnect wires identified with a meter: data is ____ (colour), +12V ____, GND ____
- [ ] Polarity checked before the string is connected through the Wagos and JD

First light (WLED solid colours):
- [ ] Solid red shows red, solid green shows green, solid blue shows blue
- [ ] Colour order that works: ____ (WLED is set to GRB, order 0, until first light says otherwise)
- [ ] All 92 pixels light; none dark or flickering
- [ ] WLED brightness limiter rechecked for 12V pixels: setting ____

Order (xLights test chase to this tree's IP, DDP, 276 channels):
- [ ] The chase starts at node 1, base-left
- [ ] It runs along the base, up the right edge, over the apex and down the left edge (nodes 1 to 59)
- [ ] Mouth: wide arc 60 to 68, small arc 69 to 73, lip 74 to 80
- [ ] Eyes: 81 to 86 on the viewer's right, 87 to 92 on the viewer's left
- [ ] Node order matches the xLights model (face rest: lip only; AI: lip plus wide arc; O: small plus wide arcs)

Power:
- [ ] Full white, all 92 pixels: ____ A at 12V (expected about 2.3A)
- [ ] Voltage at the tree box at full white: ____ V
- [ ] Wires and Wagos only slightly warm after 10 minutes at full white

## C. Per box (tree box and site box)

Box: tree ____ / site ____

- [ ] Heat-set inserts straight and tight; screws pull down without stripping
- [ ] Lid cord is seated in its groove, not twisted, and its butt joint is superglued
- [ ] Lid screws tightened evenly (6 on a tree box, 8 on a site box)
- [ ] Each gland is tight on the flex's outer sleeve (flex outer diameter under 8mm)
- [ ] All glands point down; nothing enters on a face that takes rain
- [ ] 3mm drip hole is open
- [ ] RP-SMA bulkhead is tight and the antenna points up (tree box)
- [ ] The box is screwed to the tower by four M3 screws (tree box); the tower is open underneath
- [ ] The heel nail in the control boot was hammered before the box went on

Rain and soak test of at least one box. **TBC (Rob):** the repo does not give a duration or method. A suggestion is an hour under a hose or watering can, from above and the sides.
- [ ] Box fully built with cables in its glands
- [ ] Test started ____, finished ____
- [ ] Inside dry afterwards: board, Wagos and the lid rim
- [ ] Water found at: ____
- [ ] Cord still seated after the test

## D. Per site

Site ____  Trees ____  Player ____

Mains and fuses:
- [ ] Mains never enters a printed box
- [ ] Each PSU has its own lead to an RCD-protected outdoor socket
- [ ] RCD test button trips it: ____
- [ ] PSU outputs with no load: ____ V, ____ V, ____ V (12V nominal)
- [ ] No two PSUs' +12V are joined: meter between the +12V of each pair of PSUs, with the mains off
- [ ] A 5A blade fuse sits at the site box on every tree run
- [ ] A 3A fuse sits on the player feed (PSU 1)
- [ ] The wiring matches this site's table in [site-wiring.md](../electronics/site-wiring.md)

PSU loads, all trees at full white with the player running (the PSU is 8.5A):

| PSU | Feeds | Expected | Measured |
|---|---|---|---|
| 1 | 2 trees plus the player | 6.1A | ____ A |
| 2 | 2 trees (sites A and B) | 4.6A | ____ A |
| 3 | 2 trees (site A only) | 4.6A | ____ A |

- [ ] No PSU is over 8.5A, and none gets hot

Voltage at the far tree (all trees white):

| Tree | Run (m) | Flex | Voltage at the tree | Expected |
|---|---|---|---|---|
| ____ | ____ | ____ mm² | ____ V | about 11.5V on 5m of 0.75mm² |
| ____ | ____ | ____ mm² | ____ V | |

- [ ] Far tree is above ____ V. **TBC (Rob):** the pass limit. The design expects about 11.5V and calls that fine for 12V pixels.
- [ ] Any run over about 7m uses 1.5mm² flex

Network:
- [ ] Router has the same SSID, password and subnet as the other sites; subnet ____ (expected 192.168.8.x)
- [ ] Every tree answers at 192.168.8.(100+NN) and keeps it after a power cycle
- [ ] Pi is on the router by Ethernet
- [ ] **Frame timing:** every tree of the site streaming a fast mouth sequence, each at its real distance from the router, for ____ minutes. Dropped or late frames seen: ____. **TBC (Rob):** how to measure it. The M0 plan is to watch for them, and WLED's Info page shows realtime mode and the sender's IP.
- [ ] Mouths stay in step with the audio
- [ ] If it jitters, note the tree and the distance, and decide about ESPixelStick FPP Remote (needs SD-equipped ESP32s)

Audio and player:
- [ ] Pi supply at its input: ____ V (Pi 5 needs a 5V 5A buck, Pi 3 2.5A or more)
- [ ] FPP has one DDP output per tree: right IP, start channel of its slot, 276 channels
- [ ] Slot-to-tree mapping matches `data/sites.json`
- [ ] USB sound card selected as the FPP audio output
- [ ] Audio test plays through the PAM8610 and speaker with no hum or crackle
- [ ] Volume set for the site: ____ (a quieter level after 20:00 is proposed in [show-night.md](show-night.md))
- [ ] PAM8610 is not hot after 10 minutes

## E. Show

- [ ] The sequence plays from FPP (not from the PC), with audio
- [ ] Every tree uses all four mouth shapes and rests on the lip in instrumentals
- [ ] Eyes blink
- [ ] Only the trees arranged to sing move their mouths
- [ ] The waiting loop and the goodnight fade play (these are still to be built, see [show-night.md](show-night.md))
- [ ] Schedule starts the show: set ____ (16:00 is proposed), started ____
- [ ] Schedule stops cleanly and lights go off: set ____ (21:00 after the goodnight is proposed), stopped ____
- [ ] After a power cut, the player and trees come back and the schedule carries on. **TBC (Rob):** nothing in the repo says whether FPP is set to resume.
- [ ] One whole evening runs without a dropout or anything overheating
- [ ] Spares are on site: fuses, an ESP32, a 74AHCT125, a Mini560, spare pixels

Signed off ____  Date ____
