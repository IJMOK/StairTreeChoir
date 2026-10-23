// Tree controller box: sizes shared by the box (enclosure/tree-box.scad) and the
// control boot it sits on (feet/stair-tree-foot.scad). Change them here only.
//
// Box coordinates: x across (0 = outer left), y from the front wall (towards the
// tree, y = 0) to the lid at the back, z up as fitted (0 = underside of the floor).

box_in_w      = 76;      // inside width: 70mm prototype board + 3mm each side
box_in_h      = 92;      // inside height: board (50) at the top, Wagos/Mini560/gland nuts below
box_in_d      = 30;      // inside depth, front wall to rim: ESP32 on headers stands ~22mm proud of the board
box_wall      = 2.5;     // side walls
box_floor_t   = 3.5;     // floor and roof (they carry the glands and the antenna bulkhead)
box_front_t   = 3;       // wall towards the tree, carries the board standoffs
box_rim       = 8;       // rim width at the lid face: gasket land + lid screws
box_gasket_t  = 1.5;     // printed TPU gasket
box_lid_t     = 3;
box_ear_w     = 10;      // mounting ears either side of the floor
box_ear_t     = 5;
box_ear_front = 6;       // ear screw centres from the box front ...
box_ear_back  = 8;       // ... and from the rim face

m3_clear      = 3.4;
m3_insert_d   = 4.0;     // M3 heat-set insert hole (BOM inserts; check their spec)
m3_insert_len = 6;

box_w      = box_in_w + 2 * box_wall;
box_h      = box_in_h + 2 * box_floor_t;
box_body_d = box_front_t + box_in_d;            // front face to rim face
box_d      = box_body_d + box_gasket_t + box_lid_t;
box_span   = box_w + 2 * box_ear_w;             // ears included

// Ear screw centres, box coordinates (z = 0 plane)
box_ear_holes = [
    for (x = [-box_ear_w / 2, box_w + box_ear_w / 2])
        for (y = [box_ear_front, box_body_d - box_ear_back]) [x, y]
];
