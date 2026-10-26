// Tree controller box (M3). PETG, on the shared sealed-box shell (sealed-box.scad):
// rounded corners, lid sealed with 2.7mm rubber cord, hollow roof sloping away from
// the tree with a hood and drip lip over the lid joint.
// Holds the 5x7cm controller board (electronics/), the Mini560, two Wago 221-413
// and the ends of the 12V flex and pixel lead. Sits on the tower of the control
// boot (feet/), behind the tree, with a gap to the oak; four M3 screws through its
// ears into heat-set inserts in the tower.
//
// As fitted: glands in the floor (PG9 12V in, PG7 pixel lead), pointing down into
// the boot tower; RP-SMA antenna bulkhead in the roof; lid on the back, facing away
// from the tree. Drip hole in the floor.
//
// Printing: box on its front face (open side up), no supports: the rim ledge and
// the lid screw bosses have 45 degree undersides. Lid flat, outer face down.
//
// UNVERIFIED until the parts arrive: board hole positions (pb_*), the gland and
// bulkhead thread sizes, and that the ESP32 on its headers clears box_in_d.
// Sizes shared with the boot are in tree-box-params.scad.

include <tree-box-params.scad>
include <sealed-box.scad>

part = "assembly";       // "box", "lid" or "assembly"; "box-fitted", "lid-fitted": as fitted (STEP export)

// Board: 5x7cm prototype board, M2 screws into the standoffs
pb_w          = 70;
pb_h          = 50;
pb_hole_in    = 2.5;     // hole centres from the board edges
pb_top_gap    = 12;      // board top edge below the roof: clear of the rim ledge
standoff_h    = 5;       // room for the underside joins
standoff_d    = 6;
standoff_hole = 1.8;     // M2 self-tapping

// Entries
pg9_d         = 15.6;    // PG9 thread 15.2
pg7_d         = 12.9;    // PG7 thread 12.5
pg9_x         = 22;      // from the box's outer left
pg7_x         = 59;
gland_y       = box_front_t + box_in_d / 2;
drip_d        = 3;
ant_d         = 6.6;     // RP-SMA bulkhead (1/4"-36)
ant_x         = box_w - 18;

// Lid
lid_screw_in  = 3.5;     // lid screw centres from the outer edges; the cord runs inside them
groove_in     = 8;       // cord groove centreline from the outer edges
lid_panel_t   = 2;       // lid panel inside the thick frame
boss_d        = 7;
boss_len      = 10;      // screw bosses run this far in from the rim face
corner_r      = 4;       // outline corner radius
ant_boss_d    = 14;      // flat seat for the antenna nut on the sloped roof

$fn = 48;

lid_screws = [
    for (x = [lid_screw_in, box_w - lid_screw_in])
        for (z = [lid_screw_in, box_h / 2, box_h - lid_screw_in]) [x, z]
];

board_x0 = box_wall + (box_in_w - pb_w) / 2;
board_z0 = box_h - box_floor_t - pb_top_gap - pb_h;
board_holes = [
    for (x = [pb_hole_in, pb_w - pb_hole_in])
        for (z = [pb_hole_in, pb_h - pb_hole_in]) [board_x0 + x, board_z0 + z]
];

// roof surface height at depth y (sealed-box.scad's wedge)
function roof_z(y) = box_h + sb_hood_gap + sb_skin + sb_rise(box_body_d + box_lid_t + sb_hood_over) - sb_rise(y);

module along_y(d, l) {                          // cylinder along +y from y = 0
    rotate([-90, 0, 0]) cylinder(d = d, h = l);
}

module ear() {                                  // mounting ear, top edges chamfered
    l = box_body_d - 4;
    hull() {
        cube([box_ear_w, l, box_ear_t - 1]);
        translate([1, 1, 0]) cube([box_ear_w - 2, l - 2, box_ear_t]);
    }
}

module box() {
    difference() {
        union() {
            sb_shell(box_w, box_h, box_body_d, box_wall, box_front_t, box_floor_t, box_rim, corner_r, box_lid_t);
            // lid screw bosses, cone underneath so they print; trimmed to the outline
            intersection() {
                rprism(box_w, box_h, box_body_d, corner_r, 0, 0);
                for (s = lid_screws) translate([s[0], box_body_d - boss_len, s[1]]) {
                    along_y(boss_d, boss_len);
                    translate([0, -boss_d / 2, 0]) rotate([-90, 0, 0]) cylinder(d1 = 0.1, d2 = boss_d, h = boss_d / 2);
                }
            }
            // board standoffs on the front wall
            for (p = board_holes) translate([p[0], box_front_t - 0.01, p[1]]) along_y(standoff_d, standoff_h);
            // mounting ears either side of the floor
            translate([-box_ear_w + 0.5, 0, 0]) ear();
            translate([box_w - 0.5, 0, 0]) ear();
            // flat seat for the antenna bulkhead nut, on top of the sloped roof
            translate([ant_x, gland_y, box_h - 1]) cylinder(d = ant_boss_d, h = roof_z(gland_y - ant_boss_d / 2) - box_h + 1.5);
        }
        for (s = lid_screws) translate([s[0], box_body_d - m3_insert_len, s[1]]) along_y(m3_insert_d, m3_insert_len + 1);
        for (p = board_holes) translate([p[0], box_front_t - 1, p[1]]) along_y(standoff_hole, standoff_h + 1);
        for (h = box_ear_holes) translate([h[0], h[1], -1]) cylinder(d = m3_clear, h = box_ear_t + 2);
        // floor: glands and drip hole; roof: antenna bulkhead
        translate([pg9_x, gland_y, -1]) cylinder(d = pg9_d, h = box_floor_t + 2);
        translate([pg7_x, gland_y, -1]) cylinder(d = pg7_d, h = box_floor_t + 2);
        translate([box_w / 2, box_front_t + 4, -1]) cylinder(d = drip_d, h = box_floor_t + 2);
        translate([ant_x, gland_y, box_h - box_floor_t - 1]) cylinder(d = ant_d, h = 50);
    }
}

module lid() {                                  // flat on the bed: x across, y = box z, outer face down
    sb_lid(box_w, box_h, box_lid_t, lid_panel_t, corner_r, lid_screws, groove_in);
}

// Everything in box coordinates, as fitted.
module tree_box_assembly() {
    color("SteelBlue") box();
    color("LightSteelBlue") translate([0, box_body_d + box_lid_t, 0]) rotate([90, 0, 0]) lid();
}

if (part == "box") rotate([90, 0, 0]) box();   // front face on the bed, open side up
else if (part == "lid") lid();
else if (part == "box-fitted") box();
else if (part == "lid-fitted") translate([0, box_body_d + box_lid_t, 0]) rotate([90, 0, 0]) lid();
else if (part == "assembly") tree_box_assembly();
