Stair Tree Choir

Fourteen lip-syncing pixel Christmas trees, cut from the oak treads of a removed spiral staircase. Every tree is self-contained: its own ESP32 pixel controller on the back, fed with 12V. Each site has one show player (a Pi running FPP) that plays the audio and streams the frames to its trees over Wi-Fi. Any site can run any number of trees.

This file is the project brief for Claude Code. It records what has been decided, what has been bought, and what still needs building. Before changing a decision, raise it with Rob. Everything marked unverified has to be checked against a primary source (FPP, WLED or xLights source code, a datasheet, or Rob measuring the real part) before you rely on it.

Original build pack (claude.ai artifact): https://claude.ai/artifact/X9tCyDmTd4q82MWGGNtpmc. It describes the earlier "pair kit" design (a Pi in every box driving two trees from GPIO); that was replaced on 20 Oct 2026 (§2).

1. Goals
14 trees, all identical, each with an outline, two eyes and a multi-shape mouth that lip-syncs to music. A 15th tread turned up in the loft (Rob, 24 Oct 2026), so there may be 15 (stairtree-15, 192.168.8.115 fits the scheme; measure the tread first).

Scope for December 2026 (Rob, 24 Oct 2026): 6 trees working at one site, at Rob's home (Site A); the other sites and trees follow later. Prioritise what those 6 need; don't hold anything up for sites B to D.
Sites: four, one with 4 or 6 trees, one with 4 trees and two with 2 trees each.
Every site plays the same sequences. A song is sequenced once, for a 6-tree layout.
Target: running by early December 2026.
Rob builds the hardware himself. He has a CNC router, a 3D printer (Bambu P1S; PETG/TPU), soldering kit and a bench supply.

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
Audio: USB sound card → PAM8610 amp → speaker, at the player.

Addressing
Tree IDs 1–14 are physical: hostname stairtree-NN, fixed IP 192.168.8.(100+NN) (set as the site router's LAN, with the router at 192.168.8.1). Same on every site router.
Sequence slots 1–6 are the 6 trees in the xLights sequence. Each site's config maps slots to tree IDs (data/sites.json, M5); a 2-tree site uses slots 1–2, a 4-tree site slots 1–4.

Channel map (6-tree sequence)
    Value
Pixels per tree    92 (RGB, so 276 channels)
Slot s (1 to 6) start channel    (s-1) × 276 + 1
Whole sequence    1,656 channels
FPP output per tree    DDP to the tree's IP, start channel of its slot, 276 channels

3. The tree
Blank: the existing treads are symmetric tapered boards (not triangles): about 92mm across the narrow end, 382mm across the wide end, 894mm long, 30mm thick, corners rounded ~15–20mm. Measured from photos on 20 Oct 2026 (§9); Rob to confirm with a tape. The narrow end is the top of the tree. The shape lives in data/blank.json, not in code.
Existing holes: each tread has four old stair-fixing holes in the BACK face, 17mm diameter × 23mm deep (7mm of oak left in front), two about 33mm from the narrow end (±37mm from the centreline) and two about 44mm from the wide end (±170mm), plus small screw pilot holes beside them. Decision (Rob, 20 Oct 2026): pixels keep at least a 5mm wall from them (Params.hole_wall), measured from the clearance hole: the 6mm counterbore never reaches the old holes, which stop 7mm short of the front (1mm of oak between them). The wide-end holes carry the printed boots.
CNC (decided by Rob, 25 Oct 2026): one op per tree, front face up, no flip. Nothing is cut from the back, so no registration. The blank drops into a 4mm pocket of its own shape in an MDF plate (op 0, cut once and never moved) and is held with workshop clamps. Rob does the CAM in Siemens NX from the STEP files (below); docs/cnc-cutting.md.
Pixels (decided by Rob, 25 Oct 2026): 12mm bullet pixels (Ray Wu: Ø13.6 flange, 30mm body, clips that grip a 2mm panel, too thin to rely on oak). Each hole is a front counterbore Ø19 × 6mm (Params.front_counterbore_dia/depth; deepened from 2mm by Rob after the first-off CAM run, 26 Oct 2026) holding a printed PETG disk (fixtures/pixel-disk.scad: OD 18.5, 6mm, a 2mm front lip with bore Params.hole_dia, default 12.0, and a Ø15 relief behind it) glued in with hot glue (or CA/epoxy), then a Ø15 clearance hole through the oak (Params.clearance_dia, TBC: must clear the clip barbs). The bullet pushes in from the front: the flange rests on the disk, ~1mm proud, and the clips snap behind the lip. The body ends level with the back face. Rob must test-fit one (disk test strip, bores 11.8–12.2, plus one counterbore and clearance hole in an offcut) before cutting all 14.
Layout: 92 nodes, minimum centre spacing 24.4mm, outline inset 22mm from the edge. Face option C (Rob, 20 Oct 2026): eyes centred 450mm and lip line 645mm below the top; the mouth can't go higher at its current width.
Back face: nothing routed (Rob, 25 Oct 2026). The pixel leads come out of the back and loop across the back face in data order; node 1 (data in) is at the base-left.
Tree controller box (decided by Rob, 23 Oct 2026): sits on a hollow tower on the tree's left boot (the control boot, behind node 1), behind the tree and inside its outline: ESP32, level shifter, 5V buck, two Wagos; no fuse. Glands point down into the tower. The pixel lead runs down the tree's back face, through the boot's shelf and into the tower. enclosure/tree-box.scad, feet/.
Mounting: two 3D-printed PETG boots per tree (feet/; cartoon boots the tree stands in, hollow to save material across 28): a plain right boot and the left control boot. The tree drops into the slot between lip and shaft from above; a separate printed peg goes through the shaft into the old 17mm fixing hole, and the wood screw into the old pilot hole goes through the peg's tab (Rob, 23 Oct 2026: a moulded spigot blocked assembly). Holds the bottom edge 50mm off the grass; pegged with two 8mm × 200mm nails.
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

cad/stair-tree.step (the finished tread: rounded 18mm corners, counterbores, clearance holes and the old back fixing holes), cad/fixture-plate.step (MDF plate, 18mm default, blank bounding box + 50mm margin, 4mm pocket drawn at zero clearance; Rob sets the offset in CAM) and cad/stair-tree-assembly.step are generated by tools/gen_step.py. Every printed part is also a STEP solid in cad/printed/ (as fitted, from OpenSCAD meshes: planes merged, curves faceted) and cad/stair-tree-kit.step is one tree with boots, pegs, tree box and 92 pixel disks in the tree's frame, all by tools/gen_printed.py (OpenSCAD + CadQuery; rerun after any .scad change, it also re-exports the print STLs). Tree axes: mm, Z up, front face at Z = 0 (part from Z = −30 to 0), X right, Y up (tree top is +Y), origin bottom-left of the blank's bounding box. cad/stair-tree-cnc-layout.svg and .dxf (tools/gen_cnc.py) stay as 2D reference. Layers: BLANK, FRONT_COUNTERBORE, FRONT_HOLES (clearance, through), EXISTING (reference only, not mirrored). Don't edit them by hand.

4. Hardware (decided unless marked TBC)
Part    Decision
Tree controller    ESP32 running WLED, one per tree (14). Decided by Rob, 21 Oct 2026: DIY. ESP32-DevKitC-32U (38-pin) with a U.FL to RP-SMA antenna, plugged into female headers on a 5×7cm prototype board with the level shifter and Mini560 (electronics/, M4). 16 ordered (2 spare).
ESP32 data pin    GPIO16 (not a strapping pin; proven in the M0 prototype with WLED 16.0.1). GPIO 5/18/19/23 kept free for an optional SD breakout (ESPixelStick fallback).
Level shifter    74AHCT125N (DIP-14, in a socket), one channel used per tree, 33Ω series resistor on the data line, 10k pull-down on its input, 100µF across 5V, 0.1µF at the chip.
Tree logic power    Mini560 fixed 5V buck (12V in) for the ESP32 and level shifter.
Pixel power    12V to each tree on its own run from the site box, fused 3A at the site box (5A decided 23 Oct 2026; 3A by Rob, 26 Oct 2026: a tree can't draw more than 2.3A, well under the SP17 connector's 10A). Each tree's WLED brightness limiter holds its pixels to 2A (gen_site_config.py; 2.3A would be full white), so a tree draws 2.1A (26 Oct 2026).
Mains PSU    One enclosed, fanless Mean Well LRS per site, inside the site box (Rob, 26 Oct 2026: no outdoor PSUs, replacing the LPV-100-12 per pair): the smallest that carries the site at ≤ 90% with every tree at its cap (A LRS-200-12 at 15.1A of 17A, B LRS-150-12, C/D LRS-100-12; Site A 14.1A of 17A with its router indoors); a spare LRS-200-12 later (none for December, Rob 26 Oct 2026). It also runs the player (3A fuse) and, where the router isn't indoors, the router (2A fuse; Rob, 26 Oct 2026). electronics/site-wiring.md (generated from data/sites.json) has every run, fuse and load. Mains comes in on a plug lead (3A fuse) to the PSU's terminals, which sit under a printed cover; it never enters a printed enclosure and is never on an open terminal; RCD-protected outdoor socket. 0.75mm² flex up to ~7m, 1.5mm² beyond.
12V leads    2-core 0.75mm² rubber flex (Pro Power H05RR-F, 50m bought 27 Oct 2026). Each run ends in an SP16/SP17 2-pin screw-terminal aviation connector (solderless, IP68 mated, SP17 10A, cable 6–10mm; bought 27 Oct 2026, replacing the PY07 Z108 bayonets): female on the run (powered side), male pins on a short pigtail out of the tree box's PG9 gland; red to +. The site end goes straight to its fuse in the site box's blade fuse box. xConnect pigtails for the pixel string.
Show player    One Raspberry Pi per site running FPP (4 sites): Rob's Pi 3 and Pi 5, plus 2 to buy (Pi 3 A+ is fine). Outdoors in the site box (decided 23 Oct 2026) with the PSU, the amp, a Mini560 5V buck, the blade fuse box and the router. Site A's player is the Pi 3 (the bench FPP, already set up; Rob, 26 Oct 2026), on a Mini560 from the bought stock; the Pi 5 is kept for Site B or the webcam relay.
Site network    One Cudy WR3000 per site on vanilla OpenWrt (~£30–40, decided 24 Oct 2026 over the GL.iNet Mango). It is dual-band with external antennas and doubles as a home mesh node off-season. Same SSID, password and subnet everywhere; the show uses 2.4 GHz.
Audio    USB sound card → PAM8610 2×15W (12V) → a stereo pair of outdoor 8Ω speakers per site (Site A: PD BGO40 4" IP56 pair, Rob, 26 Oct 2026; bought 27 Oct 2026 on eBay for £15.88), each on its own 2-core run.

Pixel power: about 0.3W per pixel at full white → about 28W (2.3A) per tree. Voltage drop over 5m of 0.75mm² at 2.3A is about 0.6V, fine at 12V.

5. Bought
See docs/bom.md (kept current). Ordered from AliExpress 18 Oct 2026, £277.80, due 25–31 Oct. With the ESP32-per-tree design some of it is spare (amps, sound cards, OTG cables, pin headers).

6. Repo layout
CLAUDE.md
data/blank.json                # hand-edited input: measured tread outline
data/tree-layout.json          # canonical, generated
data/sites.json                # hand-edited input: sites, slot → tree ID, 12V run lengths (defaults until Rob confirms)
tools/gen_site_wiring.py       # -> electronics/site-wiring.md, electronics/<site>.svg
tools/tree_layout.py           # layout generator (source of truth)
tools/gen_cnc.py               # -> cad/*.svg, cad/*.dxf (2D reference)
tools/gen_step.py              # -> cad/*.step for CAM in NX (needs requirements-cad.txt)
tools/gen_printed.py           # OpenSCAD -> print STLs, cad/printed/*.step (as fitted), cad/stair-tree-kit.step
tools/gen_xmodel.py            # -> xlights/StairTree.xmodel (M2)
tools/gen_site_config.py       # -> fpp/<site>/ outputs, wled/stairtree-NN.json (M5)
tools/build.py                 # python -m tools.build regenerates everything
cad/                           # CNC outputs (STEP, SVG, DXF); cad/printed/ = every printed part as STEP
fixtures/                      # OpenSCAD: CNC step clamps, pixel disks + test strip
requirements-cad.txt           # optional: CadQuery for tools/gen_step.py
docs/research.md               # what already exists (FPP, xLights, ESP32/WLED, HA integrations)
enclosure/                     # OpenSCAD: tree controller box, site box
feet/                          # OpenSCAD tree boots + exported STLs
electronics/                   # tree controller stripboard layout, wiring diagram, pin table
fpp/                           # per-site player config, provisioning notes
wled/                          # per-tree WLED config
xlights/                       # model files, layout notes
docs/                          # build guide, BOM, test checklist
tests/                         # pytest for generators
photos/                        # measurement photos (§9)

Milestones (in order)

M0. Prototype the architecture (first half done 21 Oct 2026: WLED 16.0.1 on Rob's spare ESP32-WROOM-32 mini at 192.168.0.72, 92 LEDs on GPIO16, receiving DDP from xLights on the PC as controller StairTree1; see wled/README.md. Waiting on the pixels for the rest)
Flash WLED onto a spare ESP32; FPP on Rob's Pi 3 (or xLights on the PC) sends DDP to it. When the pixels arrive, drive one 92-pixel string through a 74AHCT125 and check frame timing with a fast mouth sequence over Wi-Fi. This decides WLED streaming vs ESPixelStick FPP Remote before 14 boards are bought.

M1. Layout and CNC files (done for the measured blank; redone 25 Oct 2026 for one front-only op; waiting on the disk and clearance test)
Keep tools/tree_layout.py as the single source of truth. Front counterbores and clearance holes, existing-hole reference layer, fixture plate with the blank pocket. STEP (CadQuery) for CAM in NX; SVG (mm) and DXF (ezdxf) as reference. Tests: 92 nodes; spacing ≥ 24mm; holes ≥ 16mm from the edge; clear of the old holes; SVG viewBox = blank size; deterministic output.

M2. xLights model (generator done 20 Oct 2026: tools/gen_xmodel.py → xlights/StairTree.xmodel, format checked against xLights source 75c3e11; imported into xLights 2026.18 by Rob on 20 Oct 2026 as StairTree1-6 at start channels 1, 277, 553, 829, 1105, 1381; all 92 node positions, the face definition and sub-models verified from the saved layout)
Generate a Custom Model .xmodel from the layout JSON. Scale it to a grid (for example 1 cell = 10mm) with node numbers in wiring order.
Include a face definition mapping the phonemes in §3 to node ranges, plus eyes-open/closed if useful.
Unverified: the exact .xmodel XML schema and the face-definition attribute names. Confirm them from the xLights source on GitHub, or ask Rob to export a sample custom model with a face from his xLights install (xLights 2026.18 installed 20 Oct 2026). Don't guess the format.
Add a short doc: import the model, copy it to 6 trees (slots), set start channels per §2, and set up each tree as a DDP/WLED controller for testing from the PC.

M3. Enclosures (OpenSCAD, parametric)
Tree controller box (14): first version done 23 Oct 2026 (enclosure/tree-box.scad, sits on the control boot's tower). PETG, lid sealed with 2.7mm rubber cord in a groove (enclosure/seal.scad), M3 heat-set inserts, drip hole, PG9/PG7 in the floor, RP-SMA in the roof, standoffs for the 5×7 board. Board hole positions and ESP32 height still to be measured.
Site box: a bought DRiBOX Large (Rob, 26 Oct 2026; internal 330 × 230 × 140mm at the top, tapering with ribs, so plan on ~290 × 190 at the floor; IP55; cables pass through its lid seals, no glands), replacing the printed box of 23 Oct (enclosure/site-box.scad, now superseded). Inside: a printed plate carrying the LRS PSU with a cover over its mains terminals, a 10-way blade fuse box with a negative bus (the 0V common; Rob, 26 Oct 2026, over DIN 10×38 holders), the Pi, buck, amp and sound card, and the router if it fits. Plate still to design; measure the box when it arrives.
Every dimension a named parameter at the top of the file. Export STLs.

M3b. Tree boots (rough-in done)
feet/stair-tree-foot.scad, left and right STLs. Printed upright on the P1S, no supports, ~145–175g each. Next: Rob test-fits one pair on a tread, then tune spigot fit, shelf height and wing length.

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
docs/build-guide.md: tree cutting → finishing → pixel fitting → controller box → boots → site setup.
docs/bom.md: kept current.
docs/test-checklist.md: every Mini560 reads 5.0V before the ESP32 is connected; each 74AHCT125 in a socket; first-light test pattern; node order matches the xLights model; full-white current per tree; Wi-Fi frame timing with all 6 trees streaming; rain/soak test of one printed enclosure.

M7. Home Assistant link (later)
Rob's Home Assistant config lives in a separate repo (C:\Users\User\Documents\HA\Homeassistant, Node-RED flows there too). Plan: start/stop the show and pick playlists from HA/Node-RED (e.g. at sunset, only when someone is home), and show what's playing on the hall board. Use the existing koolsb/ha-fpp HACS integration (FPP as a media player) rather than writing one; see docs/research.md. WLED trees also appear in HA natively, which helps for testing.
Decided by Rob, 25 Oct 2026: after the 21:00 Goodnight the trees doze in the silent Night loop until "lights out", which HA sends (a graceful playlist stop when the living room lights go off); FPP keeps a 23:30 backstop. HA also starts the silent Morning loop with Rob's alarm and stops it at sunrise + 90 min; the Morning playlist ends by itself after 3 hours as a backstop. The loops are short pieces with a lead-out (tools/loops.py, docs/show-night.md "The silent loops").

7. Constraints and conventions
Python 3.11+, with dependencies in requirements.txt (ezdxf, pytest); optional CadQuery in requirements-cad.txt (STEP files; tools/build.py skips them without it). OpenSCAD for enclosures and boots. Local venv in .venv (not committed).
Generators are deterministic. Generated files are committed so Rob can use them without running code, and are rebuilt by a single make all (or python -m tools.build).
Units are mm everywhere. Coordinates are viewed from the front of the tree unless a file says it is mirrored.
Never hand-edit generated files. Change the generator and regenerate.
Mains safety: no design in this repo may put mains voltage inside a printed enclosure.
No Wi-Fi passwords or other secrets in git.
You can't test the hardware. Say plainly what Rob needs to verify on the bench, and ask before deciding anything marked TBC in §4.

8. Open questions for Rob
Tape-check the photo measurements: narrow end ~92mm, wide end ~382mm, length ~894mm.
Tree controller board: DIY ESP32-32U on stripboard, or a ready-made WLED board? (Decide after M0.)
WLED streaming (DDP) or ESPixelStick FPP Remote? (Decide after M0.)
Site router: Site A's is indoors at the front window, about 5ft from the trees, antennas upright, on its own adapter, with Ethernet to the Pi (Rob, 26 Oct 2026; inside the DRiBOX its antennas would lie flat over the PSU at ground level). Other sites: in a small covered box mounted high, 12V from the site PSU on a 2A fuse (data/sites.json "router").
Boots: test-fit the first printed pair and pegs (peg fit, tread thickness in the slot, pilot hole diameter and screw size, xConnect plug through the 16mm shelf hole, 50mm clearance enough?).
The clip barb flare diameter on a real pixel. It sets Params.clearance_dia (15mm assumed).
The disk bore, from the test strip (11.8–12.2; Params.hole_dia, 12.0 assumed), and that the flange doesn't crack the disk.
Measured sizes: chosen ESP32 board, Mini560, PAM8610, PG7/PG9 glands, outer diameter of the outdoor flex, the DRiBOX's inside at the floor, the LRS PSU.
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
