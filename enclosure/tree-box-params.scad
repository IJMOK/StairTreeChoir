// Tree controller box: sizes shared by the box (enclosure/tree-box.scad),
// tools/gen_components.py and the parked boot (feet/stair-tree-foot.scad). Change them here only.
//
// Base + cover (Rob, 28 Oct 2026): the base is an L, a plate screwed to the back of
// the tree plus a shelf along its bottom, and carries everything (board, Mini560,
// Wagos, the SP16 and PG7 in the shelf), so it is all built on the bench. The cover
// (back, sides, roof) slides on from behind over the base's "plug", the 16mm-deep
// rim round the plate and the shelf; a 2.7mm cord in a groove round the plug seals
// against the cover's walls (radial, like an O-ring on a piston).
//
// Box coordinates: x across from the cover's outer left (seen from behind; the
// antenna side, away from the tree's centre), y from the tree face (y = 0) back,
// z up, 0 = underside of the shelf and the cover's bottom edge.

box_in_w      = 76;      // inside width between the plug's side walls: the 70mm board plus 3 each side (the ESP32's USB end overhangs it)
box_in_d      = 44;      // inside depth, plate to the cover's back wall (the Mini560 stands 31 off the board)
box_h         = 100;     // cover's outer height to its top edge (the roof sits above)
plate_t       = 4;       // tree plate and its flanges
floor_t       = 3.5;     // shelf floor under the SP16 and PG7
plug_t        = 8;       // plug walls: carry the cord groove and the cover screws' inserts
plug_d        = 16;      // plug depth: the plate's rim back from the plate, the shelf's rim up from the floor
cover_wall    = 2.4;
cover_back_t  = 3;
cover_fit     = 0.25;    // cover to plug, each side; the cord takes up the gap
corner_r      = 10;      // cover's outline radius (top edges and back corners)

m3_clear      = 3.4;
m3_insert_d   = 4.0;     // M3 heat-set insert hole (CNC Kitchen / Ruthex M3 x 5.7: hole 4.0)
m3_insert_len = 6;

box_w      = box_in_w + 2 * (plug_t + cover_fit + cover_wall);   // cover's outer width
plug_x0    = cover_wall + cover_fit;                              // plug's outer left
plug_w     = box_in_w + 2 * plug_t;
plug_top   = box_h - cover_wall - cover_fit;                      // plate plug's top face
cover_y1   = plate_t + box_in_d + cover_back_t;                   // cover's back face
plug_back  = plate_t + box_in_d - cover_fit;                      // shelf plug's back face
plug_r     = corner_r - cover_wall - cover_fit;                   // plug's corner radius

// Old names, kept so the parked boot (feet/) still builds; it no longer carries the box.
box_wall = cover_wall; box_front_t = plate_t; box_floor_t = floor_t;
box_lid_t = 0; box_roof_h = 12; box_ear_w = 0; box_ear_t = 5; box_rim = 12; box_gasket_t = 0;
box_body_d = cover_y1; box_d = cover_y1; box_span = box_w;
box_ear_holes = [[8, 8], [box_w - 8, 8], [8, cover_y1 - 8], [box_w - 8, cover_y1 - 8]];
