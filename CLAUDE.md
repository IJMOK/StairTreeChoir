Stair Tree Choir

Fourteen lip-syncing pixel Christmas trees, cut from the oak treads of a removed spiral staircase. Every tree is self-contained: its own ESP32 pixel controller on the back, fed with 12V. Each site has one show player (a Pi running FPP) that plays the audio and streams the frames to its trees over Wi-Fi. Any site can run any number of trees.

This file is the project brief for Claude Code. It records what has been decided, what has been bought, and what still needs building. Before changing a decision, raise it with Rob. Everything marked unverified has to be checked against a primary source (FPP, WLED or xLights source code, a datasheet, or Rob measuring the real part) before you rely on it.

Original build pack (claude.ai artifact): https://claude.ai/artifact/X9tCyDmTd4q82MWGGNtpmc, copied into archive/docs/build-pack-2026-10-17.html. The wiring pages on claude.ai are published from docs/ (tree-wiring.html → MSrFAPvADXk8sjWY8vGcvA, site-box-wiring.html → B8oeTvXTP7NtsEbwvLjcDn, wiring.html → D7S2aqDR7d8ZSA9qU48DHn): the repo copies are the masters; republish after changing them. It describes the earlier "pair kit" design (a Pi in every box driving two trees from GPIO); that was replaced on 20 Oct 2026 (§2).

1. Goals
14 trees, all identical, each with an outline, two eyes and a multi-shape mouth that lip-syncs to music. A 15th tread turned up in the loft (Rob, 24 Oct 2026), so there may be 15 (stairtree-15, 192.168.8.115 fits the scheme; measure the tread first).

Scope for December 2026 (Rob, 24 Oct 2026): 6 trees working at one site, at Rob's home (Site A); the other sites and trees follow later. Prioritise what those 6 need; don't hold anything up for sites B to D.
Sites: four, one with 4 or 6 trees, one with 4 trees and two with 2 trees each.
Every site plays the same sequences. A song is sequenced once, for a 6-tree layout.
Target: running by early December 2026.
Rob builds the hardware himself. He has a CNC router, a 3D printer (Bambu Lab P1S, 256 × 256 bed; PETG/TPU), soldering kit and a bench supply.

2. System architecture (decided by Rob, 20 Oct 2026: ESP32 per tree, one player per site)

xLights (Rob's PC) ── sequence once for 6 trees ──► .fseq + audio
                                                      │ upload
Site (e.g. lawn, 6 trees)                             ▼
  Show player: Pi + FPP, USB audio → amp → speaker
      │ DDP over the site's own Wi-Fi (frames only, ~90 kbit/s per tree)
      ▼
  Site router (dedicated, same SSID and addressing at every site)
      │
  Tree ESP32s (WLED): stairtree-01 … stairtree-14, one per tree

Show player: Falcon Player (FPP 10.x, 64-bit Pi image) on one Raspberry Pi per site. It plays the .fseq and audio and sends each tree's channels as DDP to that tree's IP. Rob's Pi 3 and Pi 5 are two of the four; any Pi works because no GPIO pixel output is used. Rob's PC can stand in during development (xLights output or xSchedule).
Tree controller: an ESP32 on each tree running WLED, receiving DDP (realtime mode) and driving the tree's 92 pixels through a 74AHCT125 level shifter. The data lead from ESP32 to first pixel is short (≈30cm), so no long outdoor data runs.
Network: each site has a dedicated router, a Cudy WR3000 on vanilla OpenWrt. They are configured identically everywhere, so trees never join a host's home Wi-Fi. Out of season the routers serve as mesh nodes on Rob's home OpenWrt network. Fallback: the Pi as its own hotspot. Traffic is tiny; the router is for reliability, a quiet channel and fixed addressing, not bandwidth.
Fallback if Wi-Fi streaming jitters in testing: ESPixelStick firmware in FPP Remote mode (sequence stored on the ESP's SD card, sync packets only). Needs SD-equipped ESP32s, so decide before buying boards.
Audio: USB sound card → XH-M541 amp (TPA3116D2) → speakers, at the player.

Addressing
Tree IDs 1–14 are physical: hostname stairtree-NN, fixed IP 192.168.8.(100+NN) (set as the site router's LAN, with the router at 192.168.8.1). Same on every site router, by default.
Site A exception (Rob, 11 Nov 2026): the Cudy extends Rob's home network and the player plugs into it, so Site A runs on 192.168.0.x: tree NN at 192.168.0.(220+NN), FPP at .220, gateway the Huawei B818 at .1. The trees stay on DHCP and get those addresses from reservations on the Zyxel OpenWrt (192.168.0.3), which hands out the home network's addresses (pool .6–.200). A site's addressing lives in data/sites.json ("network"); tools/gen_site_wiring.ip() is the one place it's computed.
Sequence slots 1–6 are the 6 trees in the xLights sequence. Each site's config maps slots to tree IDs (data/sites.json, M5); a 2-tree site uses slots 1–2, a 4-tree site slots 1–4.

Channel map (6-tree sequence)
    Value
Pixels per tree    92 (RGB, so 276 channels)
Slot s (1 to 6) start channel    (s-1) × 276 + 1
Whole sequence    1,656 channels
FPP output per tree    DDP to the tree's IP, start channel of its slot, 276 channels

3. The tree
Blank: the existing treads are symmetric tapered boards (not triangles): about 92mm across the narrow end, 382mm across the wide end, 894mm long, 30mm thick, corners rounded ~15–20mm. Measured from photos on 20 Oct 2026 (§9); Rob to confirm with a tape. The narrow end is the top of the tree. The shape lives in data/blank.json, not in code.
Existing holes: each tread has four old stair-fixing holes in the BACK face, 17mm diameter × 23mm deep (7mm of oak left in front), two about 33mm from the narrow end (±37mm from the centreline) and two about 44mm from the wide end (±170mm), plus small screw pilot holes beside them. Decision (Rob, 20 Oct 2026): pixels keep at least a 5mm wall from them (Params.hole_wall), measured from the clearance hole: the 6mm counterbore never reaches the old holes, which stop 7mm short of the front (1mm of oak between them). Nothing uses them now (the boots that did are archived).
CNC (decided by Rob, 25 Oct 2026): one op per tree, front face up, no flip. Nothing is cut from the back, so no registration. The blank drops into a 4mm pocket of its own shape in an MDF plate (op 0, cut once and never moved) and is held with workshop clamps. Rob does the CAM in Siemens NX from the STEP files (below); docs/cnc-cutting.md.
Pixels (decided by Rob, 25 Oct 2026): 12mm bullet pixels (Ray Wu: Ø13.6 flange, 30mm body, clips that grip a 2mm panel, too thin to rely on oak). Each hole is a front counterbore Ø19 × 6mm (Params.front_counterbore_dia/depth; deepened from 2mm by Rob after the first-off CAM run, 26 Oct 2026) holding a printed PETG disk (cad/parts/pixel-disk.FCStd: a 2mm front lip with bore Params.hole_dia, default 12.0, and a Ø15 relief behind it). Friction fit since 13 Nov 2026 (Rob): the varnished counterbores measure 18.3–18.6 × 4.9 deep (varnish pools in the bottom), so the disk is an Ø18.0 core with 8 crush ribs (rib_od 19.3 as drawn, a solid fit from the rib test strip; 18.8 was too loose; bore 12.0 fits the pixel), 4.8 thick, with a 0.7 chamfer on its back outer edge to clear the varnish fillet; no glue, then a Ø15 clearance hole through the oak (Params.clearance_dia, TBC: must clear the clip barbs). The bullet pushes in from the front: the flange rests on the disk, ~1mm proud, and the clips snap behind the lip. The body ends level with the back face. Rob must test-fit one (disk test strip, bores 11.8–12.2, plus one counterbore and clearance hole in an offcut) before cutting all 14.
Layout: 92 nodes, minimum centre spacing 24.4mm, outline inset 22mm from the edge. Face option C (Rob, 20 Oct 2026): eyes centred 450mm and lip line 645mm below the top; the mouth can't go higher at its current width.
Back face: nothing routed (Rob, 25 Oct 2026). The pixel leads come out of the back and loop across the back face in data order; node 1 (data in) is at the base-left.
Tree controller box (Rob, 31 Oct 2026): an L base + wrap-round cover on spacers on the back of the tree: ESP32, level shifter, 5V buck, two Wagos; no fuse. The SP16, the pixel gland and the antenna all fire down through the shelf. cad/parts/tree-box.FCStd.
Mounting and storage (Rob, 15 Nov 2026; replaces the boots, now in archive/boots/): one joint, a dovetail rail running front to back. Three printed sockets per tree (two on the bottom edge, one on the top), each a U over the edge screwed through both legs (2 × 4 × 16 countersunk stainless each side, 5mm in from the edge, the front pair offset from the back; nothing into the end grain) with a dovetail rail under it (16 tall, 46 wide, 15° undercut, 58 long) and a full-height cove buttressing each leg, the screws in counterbores. Show: two ski halves per bottom socket slide on from front and back and are staked (two 8mm pegs each), which locks them; ~380mm of ground cover, each half 190mm, slimmer towards its ends and a thin-walled shell (one tree's whole set, 3 sockets, 4 halves and 3 towers, prints on one P1S plate: print/tree-plate.gcode.3mf); the bottom edge stands 50mm off the grass, or 106mm with a tower slid on as a riser. Storage: the trees lie face up and drop onto three towers each (slots stopped at the bottom), 115mm pitch, 14 stack about 1.63m. cad/parts/tree-mounts.FCStd; clearances in docs/cad-checks.md.
Finish: exterior oil (e.g. Osmo UV), 2–3 coats, including the end grain.

Canonical layout data: data/tree-layout.json, generated by tools/tree_layout.py from data/blank.json (the only hand-edited input). The node order is the wiring order. Every downstream artefact (CNC files, xLights model, controller config) must be generated from this file, never hand-copied.

Group    Nodes    Notes
outline    1–59    Starts at the base-left corner, runs along the base, up the right edge, over the apex and down the left edge
mouth_wide    60–68    Left to right
mouth_small    69–73    Right to left
lip    74–80    Left to right
eye_right    81–86    Viewer's right, top node first, clockwise
eye_left    87–92    Viewer's left, top node first, clockwise

Phoneme mapping (the outline and both eyes stay lit). Every shape keeps a top lip (Rob, 24 Oct 2026: O/U/WQ used to drop it and read as two smiles):

Phoneme    Mouth nodes lit
rest    lip (74–80)
MBP    inner 5 of the lip (75–79): pressed lips
etc, E, L    lip + mouth_small
FV    lip + middle 3 of mouth_small (70–72): slight dip
AI    lip + mouth_wide
O    inner 5 of the lip + mouth_small (69–73, 75–79): closed round o
U, WQ    middle 3 of the lip + middle 3 of mouth_small (70–72, 76–78): small pucker

CAD (Rob, 15 Nov 2026: one source of truth, all in FreeCAD 1.1; cad/README.md is the index): every part's master is a FreeCAD file in cad/parts/ with a `params` spreadsheet; the tread is built in FreeCAD from data/tree-layout.json by tools/cad_tree.py (cad/tree/stair-tree.FCStd, and for CAM cad/tree/stair-tree.step: rounded 18mm corners, counterbores, clearance holes, the old back fixing holes; cad/tree/fixture-plate.step: 18mm MDF, blank bounding box + 50mm margin, 4mm pocket at zero clearance, Rob sets the offset in CAM; cad/tree/stair-tree-assembly.step). Rob's NX CAM set for the first-off is archived (archive/nx-cam/); redo CAM from cad/tree/*.step. `make cad` (python -m tools.cad) exports every print STL to print/, every part as fitted to cad/printed/*.step, the tree box's bought parts (cad/components/bought-parts.FCStd) and fit checks, previews, cad/stair-tree-complete.FCStd (one complete tree as it stands, every part linked to its master) and cad/stair-tree-choir.FCStd (Site A's 6 trees and site box, the raised option, the storage stack). Tree axes: mm, Z up, front face at Z = 0 (part from Z = −30 to 0), X right, Y up (tree top is +Y), origin bottom-left of the blank's bounding box. cad/tree/stair-tree-cnc-layout.svg (tools/gen_cnc.py) stays as 2D reference. Layers: BLANK, FRONT_COUNTERBORE, FRONT_HOLES (clearance, through), EXISTING (reference only, not mirrored). Don't edit generated files by hand.

4. Hardware (decided unless marked TBC)
Part    Decision
Tree controller    ESP32 running WLED, one per tree (14). Decided by Rob, 21 Oct 2026: DIY. ESP32-DevKitC-32U (38-pin) with a U.FL to RP-SMA antenna, plugged into female headers on a 5×7cm prototype board with the level shifter and Mini560 (electronics/, M4). 16 ordered (2 spare).
ESP32 data pin    GPIO16 (not a strapping pin; proven in the M0 prototype with WLED 16.0.1). GPIO 5/18/19/23 kept free for an optional SD breakout (ESPixelStick fallback).
Level shifter    74AHCT125N (DIP-14, soldered in: no sockets, Rob 28 Oct 2026), one channel used per tree, 33Ω series resistor on the data line, 10k pull-down on its input, 100µF across 5V, 0.1µF at the chip.
Tree logic power    Mini560 fixed 5V buck (12V in) for the ESP32 and level shifter.
Pixel power    12V to each tree on its own run from the site box, fused 3A at the site box (5A decided 23 Oct 2026; 3A by Rob, 26 Oct 2026: a tree can't draw more than 2.3A, well under the SP17 connector's 10A). Each tree's WLED brightness limiter holds its pixels to 2A (gen_site_config.py; 2.3A would be full white), so a tree draws 2.1A (26 Oct 2026).
Mains PSU    Site A: a Mean Well LRS-350-12 (Rob, 15 Nov 2026, replacing the S-400-12; 29A, enclosed, temperature-controlled fan), under a printed terminal hood that carries a fused, switched IEC C14 inlet (cad/parts/psu-cover.FCStd; mains arrives on a C13 lead). Other sites: one enclosed, fanless Mean Well LRS per site, inside the site box (Rob, 26 Oct 2026: no outdoor PSUs, replacing the LPV-100-12 per pair): the smallest that carries the site at ≤ 90% with every tree at its cap (B LRS-150-12, C/D LRS-100-12); a spare LRS-200-12 later (none for December, Rob 26 Oct 2026). It also runs the player (3A fuse) and, where the router isn't indoors, the router (2A fuse; Rob, 26 Oct 2026). electronics/site-wiring.md (generated from data/sites.json) has every run, fuse and load. Mains comes from an RCD-protected outdoor socket; it is never on an open terminal, and inside the site box it exists only within the PSU and its hood. 0.75mm² flex up to ~7m, 1.5mm² beyond.
12V leads    2-core 0.75mm² rubber flex (Pro Power H05RR-F, 50m bought 27 Oct 2026). Each run ends in the SP17 cable plug of an SP16/SP17 2-pin screw-terminal aviation connector (solderless, IP68 mated, 10A, cable 6–10mm; bought 27 Oct 2026, replacing the PY07 Z108 bayonets). It screws onto the SP16 panel socket, rear-nut mounted in the tree box floor and firing down (Rob, 28 Oct 2026; no pigtail, no PG9); the box sits high enough that the plug ends 20mm above the tree's bottom edge. Red to +. Check which half has the pins when they arrive (due 7 Nov): the powered run should carry the shrouded contacts. The site end goes straight to its fuse in the site box's blade fuse box. xConnect pigtails for the pixel string.
Show player    One Raspberry Pi per site running FPP (4 sites): Rob's Pi 3 and Pi 5, plus 2 to buy (Pi 3 A+ is fine). Outdoors in the site box (decided 23 Oct 2026) with the PSU, the amp, a Mini560 5V buck, the blade fuse box and the router. Site A's player is the Pi 3 (the bench FPP, already set up; Rob, 26 Oct 2026), on a Mini560 from the bought stock; the Pi 5 is kept for Site B or the webcam relay.
Site network    One Cudy WR3000 per site on vanilla OpenWrt (~£30–40, decided 24 Oct 2026 over the GL.iNet Mango). It is dual-band with external antennas and doubles as a home mesh node off-season. Same SSID, password and subnet everywhere; the show uses 2.4 GHz.
Audio    USB sound card → XH-M541 (TPA3116D2 stereo, 12–24V; Rob, 15 Nov 2026, replacing the PAM8610; on order, size to measure) on its own 3A fuse, the sound card's output into the amp's 3.5mm input on a lead (no soldering) → a stereo pair of outdoor 8Ω speakers per site (Site A: PD BGO40 4" IP56 pair, Rob, 26 Oct 2026; bought 27 Oct 2026 on eBay for £15.88), each on its own 2-core run.

Pixel power: about 0.3W per pixel at full white → about 28W (2.3A) per tree. Voltage drop over 5m of 0.75mm² at 2.3A is about 0.6V, fine at 12V.

5. Bought
See docs/bom.md (kept current). Ordered from AliExpress 18 Oct 2026, £277.80, due 25–31 Oct. With the ESP32-per-tree design some of it is spare (amps, sound cards, OTG cables, pin headers).

6. Repo layout
CLAUDE.md                      # this brief; README.md: quick start and a map of the repo
data/blank.json                # hand-edited input: measured tread outline
data/tree-layout.json          # canonical, generated
data/sites.json                # hand-edited input: sites, slot → tree ID, 12V run lengths, PSU in hand
cad/README.md                  # the CAD index: every master, what it exports, frames, part notes
cad/parts/*.FCStd              # FreeCAD masters (hand-edited): tree box, tree mounts, PSU hood, player pods, pixel disk, step clamp
cad/stair-tree-complete.FCStd  # one complete tree, linked to the masters (generated)
cad/stair-tree-choir.FCStd     # the whole setup: 6 trees, site box, raised option, storage stack (generated)
cad/                           # also tree/ (the tread and fixture plate for CAM), components/ (bought parts), printed/ STEPs, previews/
print/                         # every STL to print, laid out for the bed, with a table (generated)
tools/tree_layout.py           # layout generator (source of truth)
tools/cad.py                   # python -m tools.cad: runs tools/cad_export.py in freecadcmd (cad_tree, cad_components, cad_assembly)
tools/slice.py                 # python -m tools.slice: Bambu Studio CLI, P1S + PETG -> print/*.gcode.3mf
tools/gen_cnc.py               # -> cad/*.svg, cad/*.dxf (2D reference)
tools/gen_xmodel.py            # -> xlights/StairTree.xmodel (M2)
tools/gen_site_wiring.py       # -> electronics/site-wiring.md, electronics/<site>.svg
tools/gen_site_config.py       # -> fpp/<site>/ outputs, wled/stairtree-NN.json (M5)
tools/build.py                 # python -m tools.build (make all) regenerates everything but the printed parts (make cad)
docs/                          # build guide, BOM, test checklist, wiring pages; index.html browses them (generated, tools/gen_docs_site.py)
electronics/                   # tree controller stripboard layout, wiring diagram, pin table
fpp/                           # per-site player config, provisioning notes
wled/                          # per-tree WLED config
xlights/                       # model files, layout notes
tests/                         # pytest; tests/test_cad.py runs geometry checks in FreeCAD when it's installed
photos/                        # measurement photos (§9)
archive/                       # superseded work (boots, OpenSCAD, CadQuery generators, NX imports); see archive/README.md

Milestones (in order)

M0. Prototype the architecture (first half done 21 Oct 2026: WLED 16.0.1 on Rob's spare ESP32-WROOM-32 mini at 192.168.0.72, 92 LEDs on GPIO16, receiving DDP from xLights on the PC as controller StairTree1; see wled/README.md. Waiting on the pixels for the rest)
Flash WLED onto a spare ESP32; FPP on Rob's Pi 3 (or xLights on the PC) sends DDP to it. When the pixels arrive, drive one 92-pixel string through a 74AHCT125 and check frame timing with a fast mouth sequence over Wi-Fi. This decides WLED streaming vs ESPixelStick FPP Remote before 14 boards are bought.

M1. Layout and CNC files (done for the measured blank; redone 25 Oct 2026 for one front-only op; waiting on the disk and clearance test)
Keep tools/tree_layout.py as the single source of truth. Front counterbores and clearance holes, existing-hole reference layer, fixture plate with the blank pocket. STEP (FreeCAD, tools/cad_tree.py) for CAM in NX; SVG (mm) and DXF (ezdxf) as reference. Tests: 92 nodes; spacing ≥ 24mm; holes ≥ 16mm from the edge; clear of the old holes; SVG viewBox = blank size; deterministic output.

M2. xLights model (generator done 20 Oct 2026: tools/gen_xmodel.py → xlights/StairTree.xmodel, format checked against xLights source 75c3e11; imported into xLights 2026.18 by Rob on 20 Oct 2026 as StairTree1-6 at start channels 1, 277, 553, 829, 1105, 1381; all 92 node positions, the face definition and sub-models verified from the saved layout)
Generate a Custom Model .xmodel from the layout JSON. Scale it to a grid (for example 1 cell = 10mm) with node numbers in wiring order.
Include a face definition mapping the phonemes in §3 to node ranges, plus eyes-open/closed if useful.
Unverified: the exact .xmodel XML schema and the face-definition attribute names. Confirm them from the xLights source on GitHub, or ask Rob to export a sample custom model with a face from his xLights install (xLights 2026.18 installed 20 Oct 2026). Don't guess the format.
Add a short doc: import the model, copy it to 6 trees (slots), set start channels per §2, and set up each tree as a DDP/WLED controller for testing from the PC.

M3. Enclosures (FreeCAD, parametric: cad/parts/, cad/README.md)
Tree controller box (14): L base + wrap-round cover since 31 Oct 2026 (Rob: the sliding cover would drag the cord out of its groove). The base is a back plate on 10mm spacers with ears (4 × 40 wood screws) plus a shelf. It carries everything: the board on the plate, the Mini560 standing on the board, the Wagos, and the SP16, PG7 and RP-SMA firing down through the shelf, so nothing unplugs when the cover comes off. The cover (back, sides, roof sloping away from the tree, skirts wrapping the plate's top and side edges, notched round the ears) hooks over the plate's top edge and swings in; nothing of it goes under the shelf, because a swing about the top lifts anything there into it (the first print couldn't be assembled). One M3 × 10 goes through a 45° bevel at its lower back corner into an insert in a block on the shelf (45° so it pulls the cover against the cord). The 2.7mm cord is in a groove in the plate, over the top and down the sides only: the bottom is deliberately not sealed, because rain doesn't fall upwards (Rob). No sockets (Rob): the ESP32 and the 74AHCT125 are soldered in. cad/parts/tree-box.FCStd (FreeCAD since 1 Nov 2026; sizes in its `params` spreadsheet); bought parts and fit checks in tools/cad_components.py; print the coupon and the seal test first. Board hole positions and the SP16's nut and thread still to be measured.
Site box: a bought DRiBOX Large (Rob, 26 Oct 2026; internal 330 × 230 × 140mm at the top, tapering with ribs, so plan on ~290 × 190 at the floor; IP55; cables pass through its lid seals, no glands), replacing the printed box of 23 Oct (now in archive/printed-site-box/). Inside (Site A, 10 Nov 2026): parts stuck down on pads, no plate (docs/site-box-wiring.html): the LRS-350-12 under its IEC hood, a 10-way blade fuse box (Rob, 26 Oct 2026, over DIN 10×38 holders; Site A's PPFH-76ATO10 has no negative bus, so 0V joins on 2 × Wago 221-415), the Pi and its buck (in the printed buck pod), the XH-M541 and the sound card. The router is indoors at Site A. The assembly shows an indicative layout; measure the box when it arrives.
Every dimension a named parameter in the master's `params` sheet; `make cad` exports the STLs.

M3b. Tree mounts and storage (designed 15 Nov 2026, replacing the boots)
cad/parts/tree-mounts.FCStd: socket (3 per tree), ski (2), tower (3). Next: Rob prints one socket and the dovetail coupon, checks the channel on a real tread, the slide (`clr`) and the screw positions, then one pair of ski halves and two towers.

M4. Electronics documentation (done 21 Oct 2026: tools/gen_controller.py → electronics/tree-controller-board.svg + connections.md, electronics/README.md for the schematic, box wiring, bench test and site wiring. Unverified until parts arrive: header row spacing, Mini560 size, xConnect colours)
Tree controller stripboard layout (diagram plus connection table): ESP32 data pin → 74AHCT125 (powered at 5V, unused inputs tied to GND, /OE of the used channel tied low) → 33Ω → pixel data; 100µF across 5V; 0.1µF at the chip; Mini560 from 12V; pixel 12V fused 3A at the site box. Optional TVS diode on the data line at the box.
Site wiring diagram: PSU → fused splits → trees; player, amp, speaker.

M5. Site and tree configuration
data/sites.json lists the sites and maps sequence slots to tree IDs. tools/gen_site_config.py generates:
per tree: WLED config (hostname stairtree-NN, static IP, LED count 92, data pin, colour order TBC from first light, realtime/DDP receive enabled, site Wi-Fi credentials kept out of git)
per site: FPP channel outputs (one DDP output per tree: IP, start channel of its slot, 276 channels), playlist and a nightly schedule that stops the show cleanly
Unverified: WLED's config JSON schema and FPP's channel output JSON schema. Read them from the source or from a backup exported from a running device. Prefer WLED's /json/cfg backup/restore and FPP's settings backup or API over writing files into filesystems.
A provisioning checklist: flash ESP32 → apply config → join site router → test pattern; flash Pi → apply site config → audio test.

M6. Docs and test checklist
docs/build-guide.md: tree cutting → finishing → pixel fitting → controller box → mounts → site setup.
docs/bom.md: kept current.
docs/test-checklist.md: every Mini560 reads 5.0V before the ESP32 is connected; each 74AHCT125 soldered in after the 5V check; first-light test pattern; node order matches the xLights model; full-white current per tree; Wi-Fi frame timing with all 6 trees streaming; rain/soak test of one printed enclosure.

M7. Home Assistant link (later)
Rob's Home Assistant config lives in a separate repo (C:\Users\User\Documents\HA\Homeassistant, Node-RED flows there too). Plan: start/stop the show and pick playlists from HA/Node-RED (e.g. at sunset, only when someone is home), and show what's playing on the hall board. Use the existing koolsb/ha-fpp HACS integration (FPP as a media player) rather than writing one; see docs/research.md. WLED trees also appear in HA natively, which helps for testing.
Decided by Rob, 25 Oct 2026: after the 21:00 Goodnight the trees doze in the silent Night loop until "lights out", which HA sends (a graceful playlist stop when the living room lights go off); FPP keeps a 23:30 backstop. HA also starts the silent Morning loop with Rob's alarm and stops it at sunrise + 90 min; the Morning playlist ends by itself after 3 hours as a backstop. The loops are short pieces with a lead-out (tools/loops.py, docs/show-night.md "The silent loops").

7. Constraints and conventions
Python 3.11+, with dependencies in requirements.txt (ezdxf, pytest). FreeCAD 1.1 for all CAD (Rob, 15 Nov 2026: no OpenSCAD or CadQuery; freecadcmd runs the exports and the CAD tests skip without it). Local venv in .venv (not committed).
Generators are deterministic. Generated files are committed so Rob can use them without running code, and are rebuilt by a single make all (or python -m tools.build).
Units are mm everywhere. Coordinates are viewed from the front of the tree unless a file says it is mirrored.
Never hand-edit generated files. Change the generator and regenerate.
Mains safety (amended by Rob, 15 Nov 2026, for the IEC inlet): the only printed part that may carry mains is a PSU terminal hood: closed on every side, the inlet's earth to the PSU's FG, insulated crimps on every mains tab, a partition between the mains and 12V terminals, screws that can't reach into the PSU past its datasheet limit. No other printed part carries mains.
No Wi-Fi passwords or other secrets in git.
You can't test the hardware. Say plainly what Rob needs to verify on the bench, and ask before deciding anything marked TBC in §4.

8. Open questions for Rob
Tape-check the photo measurements: narrow end ~92mm, wide end ~382mm, length ~894mm.
Tree controller board: DIY ESP32-32U on stripboard, or a ready-made WLED board? (Decide after M0.)
WLED streaming (DDP) or ESPixelStick FPP Remote? (Decide after M0.)
Site router: Site A's is indoors at the front window, about 5ft from the trees, antennas upright, on its own adapter, with Ethernet to the Pi (Rob, 26 Oct 2026; inside the DRiBOX its antennas would lie flat over the PSU at ground level). Other sites: in a small covered box mounted high, 12V from the site PSU on a 2A fuse (data/sites.json "router").
Tree mounts: test-print one socket and the dovetail coupon (channel slack on a real tread, the dovetail slide, screw positions against your tree), then a pair of ski halves and towers. The XH-M541's size and mounting, the LRS-350-12 and the IEC inlet measured against the hood before printing it.
The clip barb flare diameter on a real pixel. It sets Params.clearance_dia (15mm assumed).
The disk bore, from the test strip (11.8–12.2; Params.hole_dia, 12.0 assumed), and that the flange doesn't crack the disk.
Measured sizes: chosen ESP32 board, Mini560, XH-M541, LRS-350-12, IEC inlet, PG7 gland and SP16 socket (hole and nut), outer diameter of the outdoor flex, the DRiBOX's inside at the floor.
The pixel colour order (RGB, GRB and so on), from the first-light test.
Which song to sequence first.

9. Measuring the tread from photos
Rob photographs a tread; Claude reads the photos and writes data/blank.json. Done for one tread on 20 Oct 2026 (photos/PXL_20261020_*.jpg): an OpenCV script segmented the wood and the A4 sheet, used the sheet's corners for a perspective transform, and fitted lines to the four edges. The front and back photos agreed within ~5mm.
- Lay the tread flat, front face up, in even light.
- Lay two rulers or tapes flat on the tread: one along the long edge, one across the widest end. Add an A4 sheet on the tread too (a known 210×297 rectangle for perspective correction).
- Shoot from directly above, from as far back as the zoom allows, tread filling most of the frame. Then a second photo square-on to the narrow end, and close-ups of any curve or notch with a ruler in shot.
- Tape-measure by hand: overall length, widest width, thickness. These cross-check the photo.
- Save the photos in photos/.
Claude fixes scale and perspective from the A4 corners or ruler marks, describes the outline as points in mm (curves as several points with corner=false), and gives the numbers back for Rob to check against the tape before regenerating. Expect about ±2–3mm from a photo: fine for the outline inset, not for hole fit (that comes from the offcut test). The generator only handles convex outlines so far; a notch at the narrow end would need it extending.

10. Long term ideas (not started)
Effects library (tools/fx.py, 23 Oct 2026): sections name looks, palettes, beat accents and eye moves (eyes follow the singers, roll, spin); whole-choir looks go on the Outlines group; tools/preview_render.py draws a render as a GIF. See xlights/README.md. Still to come: script writing for the songs/skits, animation beyond the phoneme faces, and voice generation for spoken parts (Rob, 23 Oct 2026: Piper, free local TTS, a voice per tree). Sequencing help: JohnBreault/xlights-mcp-server (docs/research.md), once the tree models are in the xLights show folder.
