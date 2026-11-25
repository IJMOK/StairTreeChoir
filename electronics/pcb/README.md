# Milled tree controller PCB (6-up, PrintNC, one 1mm end mill)

The protoboard circuit on single-sided 1.2mm FR4 for the last five trees, plus one spare. The whole job is one 1.0mm flat end mill and one file: one isolation pass round every copper area, then the holes, then the cut-out.

**What stays the same as the protoboard:**
- the 70 × 50 outline;
- the four fixing holes (Ø2.2, 2mm in from each edge, so the box's M2 standoffs fit);
- the ESP32, U1 and Mini560 in exactly the same holes, so the tree box and its fit checks don't change.

**What changes:**
- **Pads.** A 1mm cutter needs 1mm between nets, so pads on 2.54 pitch are 1.5mm wide ovals.
- **Small parts move.** R1, R2, C1, C2 and JD sit where the tracks fit (see the assembly drawing).
- **Thinner board.** It's 0.4mm thinner than the protoboard, so everything sits 0.4mm further from the cover.

Everything in this folder comes from `tools/gen_pcb.py` (`make all`, or `python -m tools.gen_pcb`). Change the generator, not the files.

> **Single-sided clad only.** The holes aren't plated and the parts sit on the plain side. If the sheet has copper on both sides, that copper joins every pin together. Remove it first, or use single-sided board.

## Files

| File | What |
|---|---|
| **`cam/tree-pcb-6up-1mm.nc`** | **The whole job:** isolation and label (all 6 boards), then holes, then cut-out (~70 min) |
| `cam/0_air_frame.nc` | Spindle off. Traces the job's footprint (146 × 160) 5mm above the sheet, so you can check it sits on the copper clad |
| `cam/1_isolation_1mm.nc`, `2_drill_1mm.nc`, `3_outline_1mm.nc` | The same job in three parts, to re-run one step (~25, ~30 and ~15 min) |
| `board-component-side.svg` | **Assembly drawing:** where every part goes (component side, antenna end left) |
| `board-copper-side.svg` | The copper as milled, with the cutter's centre lines |
| `panel.svg` | The panel as it sits on the machine, with X0 Y0 marked |
| `gerber/` | Bottom copper, outline and Excellon drill (component view), for a Gerber viewer |
| `checks.md` | Design rules, plus the G-code re-read and checked against the netlist |

## What you need

- Single-sided FR4, 1.2mm, at least **150 × 165**. The panel is 144 × 158 (2 across, 3 up, 4mm between boards); the cut-out reaches 1mm past it.
- Double-sided tape under the whole sheet, or at least under every board. The boards are cut free with no tabs.
- A 1.0mm flat 2-flute carbide end mill. A sharp one: a worn cutter tears the copper instead of cutting it.
- Dust extraction and a mask. FR4 dust is glass fibre.

## On the PrintNC

1. Tape the sheet down square to X and Y, copper up, and roll it flat.
2. **X0 Y0** = the bottom-left corner of the panel. Put it about 2mm in from the sheet's bottom-left corner. **Z0** = the top of the copper. The copper conducts, so a probe clip on the sheet works.
3. Run `0_air_frame.nc` and watch that the frame stays on the sheet.
4. Run `tree-pcb-6up-1mm.nc`. It does board A's isolation first, at the bottom left. **Feed-hold after board A** and check:
   - every groove is cut through to dull FR4 all the way round;
   - with a meter, neighbouring ESP32 pads aren't joined, and 5V (the track round the edge) isn't joined to the GND pour.
5. Lift the boards off the tape. Deburr, then clean the copper with a Scotch-Brite pad and IPA. Flux or tin it straight away.

**Depth.** The isolation cuts 0.2 deep. A flat cutter cuts the same width at any depth, so a sheet up to about 0.15 lower than Z0 still gets cut through. The design also holds with a 0.95 or 1.05 cutter (checked, below).

**G-code:** the same plain subset as your NX tread job, which ran on this machine: `%` wrapper, G21 G90 G17, G0/G1, G2 with I/J for the helical holes, M3 S18000/M5, M30. There's no M6, G43, G28 or canned cycles. `G04 P3` waits for the spindle: 3 seconds on LinuxCNC and grbl, but on Mach3 that P may mean milliseconds.

| Step | Spindle | Feed | Plunge | Depth |
|---|---|---|---|---|
| Isolation and label | 18,000 | 350 | 60 | 0.2, one pass |
| Holes | 18,000 | 150 (helix) | 60 (pecks of 0.75) | 1.5 (1.2 board + 0.3 into the tape) |
| Cut-out | 18,000 | 300 | 60 | 0.5 per pass, 3 passes to 1.5 |

The cut-out is in three depths because a single 1.5 deep pass is three times the cutter's diameter, and that's how 1mm cutters snap. For one pass, set `EM_STEPDOWN = 1.5` in `tools/gen_pcb.py`, rerun, and slow `EM_FEED`. Every feed is a constant at the top of that file.

## The board

- Copper only on the underside. Parts go in from the plain side and are soldered on the copper, as on the protoboard. **No wires underneath**: every join is a track.
- **5V** (0.8 wide) goes up from the Mini560, along the top edge, down the USB end to J2.19, then along the bottom past C1 and C2 to U1.14.
- **IO16** (0.6) runs under the ESP32, round its antenna end past R2, along under the J2 row and down into U1.2.
- **U1.3** runs between U1's two rows of pins, out past U1.1 to R1, then on to JD.
- **GND** is all the copper that's left: one pour. GND pads sit straight in it with no thermal spokes, because a 1mm cutter can't cut them. Give those joints a little longer with the iron.
- **Unused pads** (most ESP32 pins, U1's 2Y, 3Y and 4Y) are islands of their own, so every ESP32 pin can be soldered for strength. Two more ESP32 GND pins (J3.7, J2.14) join GND, which is harmless.
- **Rings are thin.** The header and U1 pads are 1.5 × 2.3 ovals on 1.0 holes. The copper ring is 0.25 across the row and on the outer side, more inwards. Don't overheat a pad, or it lifts.
- **The ESP32 also fits turned 180°, which puts 5V on the wrong pins.** Antenna end left, seen from the component side. A groove in the copper reads "ANT →" from the copper side, pointing to that end.
- Signal copper keeps 2.5mm from the fixing hole centres, so the standoffs' brass inserts only ever touch GND.

## Building one

Use **board-component-side.svg** for where the parts go; R1, R2, C1, C2 and JD have moved from the protoboard drawing. Otherwise follow [../README.md](../README.md) "Building and testing one board", skipping the underside joins.
- **U1**: notch right. **ESP32**: antenna end left. **Mini560**: on its 90° header in the same four holes as before (OUT+ C4/C5 at the top, OUT− C8/C9).
- **R2** stands, either way round. **R1** lies flat.
- **C1** (100µF) has + at the bottom, on the 5V track.
- **C2** (0.1µF) has its leads 7.62 apart. Bend them, and lean the body right, away from U1.
- **JD**: fit it with the wire entries facing the board's bottom edge.
- Before fitting anything, meter 5V to GND (C1's two pads). They must be open. Then check the 5V rail on the bench supply before the ESP32 and U1 go in, as before.

## Checks (checks.md)

`tools/gen_pcb.py` checks the drawn copper:
- 1.0 between nets;
- signal copper 2.5 from the fixing holes and 0.5 from the edge;
- the rings;
- one GND pour.

Then it **re-reads the whole-job G-code**. It sweeps the 1mm cutter along every move, works out the copper and holes actually left on board A, and confirms:
- every net is one piece;
- no piece joins two nets;
- no floating scraps;
- the cutter never touches a pad or track;
- every hole is the right size;
- the board cuts out at 70.00 × 50.00 with the fixing holes 2.0 in.

The same G-code checked as if cut by a 0.95 or a 1.05 cutter keeps every net and adds no shorts. `tests/test_pcb.py` checks that the circuit is the protoboard's, that the ESP32, U1 and Mini560 are in their protoboard holes, and that the job uses one tool.

## Still to check on the real parts

- **The fixing hole inset (2.0)** is the tree box's `pb_hole_in`. Nobody has measured it. Check one protoboard's hole centres (66 × 46 apart) before cutting.
- **JD's pins** in a 1.4 hole, and header pins in the 1.0 holes. Drill a scrap first if unsure.
- **C1's can** (assumed 6.3 dia, 2.5 lead pitch) clears R1. **R2** standing (10mm or so) clears the Mini560's lower end: the Mini560's exact footprint above the board isn't measured.
