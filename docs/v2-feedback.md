# Tree mounts: v2 feedback

Rob's notes from printing and fitting the v1 mounts (c06ad23 / bbc6ba1), 17 Nov 2026.
Everything here lives in `cad/parts/tree-mounts.FCStd`, built by `tools/cad_parts.py`
(`tree_mounts()`), placed by `tools/cad_assembly.py`.

**Built as v2 on 17 Nov 2026** (items 1–6 below, plus a drilling jig, `print/tree-drill-jig.stl`). Not printed yet: start with the coupon, one socket, the jig and one cap.

Before v2 is built, print **one fit-test coupon** that settles the three tolerances below
(dovetail, pole bore, peg hole) in a few grams, instead of finding out from full parts again.

---

## Feet and stands

### 1. Sockets are loose on the tree
**Seen:** the U over the edge rattles on the tread.

**Why:** `fit = 0.8` is total slack across the channel, on purpose: the plan was that the
screws through both legs would pull them tight. In practice they don't.

**v2 (Rob, 17 Nov 2026):** a **solid socket** (not cored: Rob, later 17 Nov) **that fits the tree well**, fixed by screws **up
through its base into the tree's edge** (into the 30mm thickness), with no screws through
the faces.
- Snug on the tread: the channel takes up the slack itself instead of relying on the screws.
  `fit` goes from 0.8 to about 0.2. Better, use **crush ribs** on the inside faces, as the pixel
  disks do, so it grips the oiled oak whatever its real thickness. Tape-check the thickness of a
  few finished treads first (30 nominal).
- The legs become short, stiff locators that grip the faces. They no longer carry screws, so
  they can be shorter than `leg_h` = 10 and stay clear of the counterbores (12.5mm in).
- Screw positions are critical: they must miss the pixel holes. The base row is 12 pixels every
  30mm (x = 25.9 … 356.1), 22mm up from the bottom edge, and each has a Ø15 clearance hole
  through the full 30mm.
  - **The bottom sockets sit directly under a pixel**: `SOCKET_BOTTOM_X = (55.9, 326.1)` are
    pixel positions. The comment in `cad_assembly.py` that says "midway between" is wrong. A screw
    at the socket's centre would run straight into that pixel's hole.
  - So either put the two edge screws at **±15** (midway between pixels: 40.9 / 70.9 and
    311.1 / 341.1), which leaves about 5mm of oak each side of a 5mm screw as it passes the holes,
    or move the sockets so the pixel sits between the screws. The ±15 pair also spreads the hold.
  - Add a check to `cad_assembly.checks()` for the oak left between each edge screw (full length)
    and the nearest pixel hole, the same way the face screws are checked now.
- The top socket (x = 191, on the top edge) needs the same check against the top pixels.
- **End grain (decided, Rob, 17 Nov 2026):** the tree's bottom and top edges are end grain
  (the grain runs along the tread). v1 put nothing there, and this reverses that rule in the
  brief (§3). Rob's answer: **pre-drill and use larger screws**.
  - Built (17 Nov): 5 × 45 in the bottom sockets, 5 × 35 in the top one (50s would run into the old stair pilot holes, which are 23mm deep from the back); stainless, pilot sized for oak, countersunk into the socket's
    base.
  - Long screws are what give end grain its hold, but a 50mm screw passes level with the base
    row (22mm up), so it has to go between the holes (±15, above). A 6mm screw leaves only about
    4.5mm of oak each side, so 5mm is the safer size.
  - The drilling jig (item 2) sets the pilot positions and angle.

### 2. Socket position drives stacking, and nothing sets it
**Seen:** where the sockets go on each tree decides whether the towers line up in the stack,
and v1 leaves that to eye and tape measure.

**Why:** the CAD places sockets exactly (`SOCKET_BOTTOM_X`, top at the edge's midpoint), but
there's nothing to carry that position onto the real oak.

**v2:** a printed **drilling jig** for each socket position. It registers off something fixed
on every tree (the tread's corners or ends and/or locating pins into neighbouring pixel holes),
and it drills the pilot holes so every tree gets its sockets in the same place. Make the jig
from the same numbers as the assembly so the CAD and the trees can't drift apart. Worth
checking that all trees really are the same blank (`layout["blank"]`). If any differ, the jig
must register off the edge that matters for stacking.

### 3. Pole holes are loose on the poles
**Seen:** the poles measure **exactly 11.0mm**. The holes are sloppy, and they should be a slide fit.

**Why:** `pole_d = 11.6` (0.3 a side, allowing for a ferrule that isn't there). Horizontal
teardrop holes print close to size, so they come out loose.

The **caps** (the feet) are especially loose. Their bore is a teardrop (`CapBoreRoof`, so it
prints without supports), and the pole only sits in the round lower part, with nothing
holding it down from above.

**v2 (Rob, 17 Nov 2026: tighter in the feet):** split `pole_d` in two.
- `pole_d` (stand tube) about **11.2**: slide fit.
- New `cap_bore_d`, about **11.0–11.1**: a firm push fit. Add **crush ribs** in the bore (3–4,
  including one in the teardrop's peak) so the pole is gripped all round, not only in the lower
  half, and printing variation is taken up the same way the pixel disks' ribs do.
- Settle both on the coupon (stand: 11.1 / 11.2 / 11.3; cap: plain against ribbed).

### 4. Peg holes should be angled 45° back toward the tree
**Seen:** the 9mm peg holes are vertical. As with good tent pitching, the peg should go in at
45°: head leaning out, tip under the tree, so a pull from the tree drives it deeper rather than
levering it out.

**Why:** `CapPeg` is a vertical cylinder through the 6mm pad (`pad_t`) at `peg_at`.

**v2:** tilt the peg hole 45° in the front-to-back plane, its bottom toward the tree on both
the front and the back cap (the back cap is the front one turned round, so one master does
both). Notes:
- A 45° hole through a 6mm pad is a 13mm-long oval and guides the peg poorly. Give it a **boss**
  (a sloped block, roughly 10–12mm along the peg's axis) so the peg is held at the angle.
- The peg's head then bears on a sloped face. Keep a flat landing square to the hole, or the
  existing countersink, for the head.
- Recheck `peg_at` and the pad's length: the peg's entry point moves outward, and its tip must
  not meet the pole's end.
- A 45° hole prints without supports.
- Keep the `stake_d >= 9` rule (9.4 now), and confirm it on the coupon at the new angle.

---

## Stacking and storage

### 5. Storage towers failed to print
**Seen:** knocked off the bed mid-print. Too narrow for their height. Rob suggests widening
by about 10mm.

**Why:** a tower is 115 tall (`pitch`, which must not change), and it prints standing on its
**slim** end: below the rail's stop it's trimmed to just the pocket and its walls
(`spig_w + 2·spig_clr + 2·stalk_wall` ≈ 35 wide, only about 10.5 deep). That's roughly an 11:1
height to depth ratio on the bed, so the nozzle knocks it over.

**v2:**
- Widen by about 10mm **in depth** (away from the tree), since depth is the narrow direction.
  Either grow `col_d`, or add the 10mm as a solid back spine. Width along the edge (`col_w = 54`)
  is already fine at the top.
- Stop slimming the bottom to the pocket, or slim it much less (`stalk_wall` up from 2), so the
  footprint on the bed is the full section.
- Belt and braces: a brim, or mouse ears, on `print/tower-plate.3mf`, and space the six towers
  further apart on the plate.
- Re-slice (`make slice`) and quote grams. The plate was 225g / 5h36 for six.

### 6. Dovetails are loose: make them a slide fit with a light latch
**Seen:** around **1mm of play**. They should slide on snugly and click home.

**Why:** `clr = 0.3` a side, plus the slot floor is cut `clr` past the rail (`dt_h + clr`), so
with 15° flanks the rail sits about 0.6–0.8mm loose across once it's seated, before any print
error. The same `slot()` cuts the towers and the stands, so both are loose.

**v2:**
- `clr` about **0.1–0.15** a side, settled on the coupon. The flanks are 15° undercuts, so tighter
  clearance pulls the rail down onto the floor as well.
- A **latch** (built): a tongue in the slot's floor, cut free on three sides, with a 0.8mm bump
  (r 3, so it ramps both ways) that drops into a 0.9mm groove across the rail's tip, 5.2mm in
  from the rail's back end, when the rail is home on the stop. The bump only rides the rail for
  the last few mm.
  - **Stand:** the tree slides in from the front; the tongue (3mm, the floor wall) flexes out
    underneath.
  - **Tower** (Rob, 17 Nov 2026: "the towers don't latch in either"): the rail's back end sits
    on the tower's stop just as on the stand, so the same groove serves both. The column is
    solid behind the floor, so the tongue is 2.4mm with a 1.2mm relief behind it.
- The socket is **solid** (Rob, 17 Nov 2026), the rail no longer cored, which helps the fit too.

---

## Still open
- Cross pin through stand and rail: deferred by Rob. A latch (item 6) may make it unnecessary.
