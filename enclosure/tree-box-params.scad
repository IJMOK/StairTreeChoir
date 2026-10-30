// Tree controller box: sizes shared by the box (enclosure/tree-box.scad),
// tools/gen_components.py and the parked boot (feet/stair-tree-foot.scad). Change them here only.
//
// L base + clip-on cover (Rob, 30 Oct 2026): the base is an L, a back plate on spacers
// off the tree plus a shelf along its bottom. It carries everything, including the
// SP16, PG7 and RP-SMA firing down through the shelf, so nothing unplugs when the cover
// comes off. The cover hooks on at the top, swings in and takes one M3 at the bottom.
// The 2.7mm cord seals the top and sides on the plate; the bottom is left open on
// purpose: rain doesn't fall upwards.
//
// Box coordinates: x across from the cover's outer left (seen from behind; the
// antenna side, away from the tree's centre), y from the plate's tree face (y = 0) back,
// z up, 0 = underside of the cover's bottom lip.

box_w         = 87;      // cover's outer width: the 74 opening plus a 6.5 rim each side
box_h         = 102;     // cover's height at the back edge, below the roof's last 1mm
box_in_d      = 42;      // inside depth, plate to the cover's back wall (the Mini560 stands about 33 off the board)
plate_t       = 5;       // back plate and its ears: carries the cord groove
floor_t       = 3.5;     // shelf
lip_t         = 2.4;     // cover's bottom lip, under the shelf
cover_wall    = 2.4;
cover_back_t  = 3;
cover_fit     = 0.25;    // cover's walls to the shelf's sides, each side
corner_r      = 12;      // cover's outline radius, top corners

m3_clear      = 3.4;
m3_insert_d   = 4.0;     // M3 heat-set insert hole (CNC Kitchen / Ruthex M3 x 5.7: hole 4.0)
m3_insert_len = 6;

floor_z    = lip_t + floor_t;                                     // shelf's top face
cover_y1   = plate_t + box_in_d + cover_back_t;                   // cover's back face

// Old names, kept so the parked boot (feet/) still builds; it no longer carries the box.
box_wall = cover_wall; box_front_t = plate_t; box_floor_t = floor_t;
box_lid_t = 0; box_roof_h = 12; box_ear_w = 0; box_ear_t = 5; box_rim = 12; box_gasket_t = 0;
box_body_d = cover_y1; box_d = cover_y1; box_span = box_w;
box_ear_holes = [[8, 8], [box_w - 8, 8], [8, cover_y1 - 8], [box_w - 8, cover_y1 - 8]];
