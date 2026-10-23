// Tree controller box (M3). PETG box + flat lid sealed with 2.7mm rubber cord (seal.scad).
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
// the lid screw bosses have 45 degree undersides. Lid flat, groove up.
//
// UNVERIFIED until the parts arrive: board hole positions (pb_*), the gland and
// bulkhead thread sizes, and that the ESP32 on its headers clears box_in_d.
// Sizes shared with the boot are in tree-box-params.scad.

include <tree-box-params.scad>
include <seal.scad>

part = "assembly";       // "box", "lid" or "assembly"

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
boss_d        = 7;       // flush with the outer wall at lid_screw_in
boss_len      = 10;      // screw bosses run this far in from the rim face
skirt_t       = 1.6;     // rain skirt round the lid, over the gasket line
skirt_gap     = 0.4;
skirt_len     = box_gasket_t + 2.5;

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

ledge = box_rim - box_wall;                     // rim ledge inside the walls
ledge_t = 4;

module along_y(d, l) {                          // cylinder along +y from y = 0
    rotate([-90, 0, 0]) cylinder(d = d, h = l);
}

module cavity() {
    x0 = box_wall; z0 = box_floor_t;
    y0 = box_front_t; y_ledge = box_body_d - ledge_t;
    translate([x0, y0, z0]) cube([box_in_w, y_ledge - ledge - y0, box_in_h]);
    hull() {                                    // 45 degree underside of the rim ledge
        translate([x0, y_ledge - ledge - 0.01, z0]) cube([box_in_w, 0.01, box_in_h]);
        translate([x0 + ledge, y_ledge, z0 + ledge]) cube([box_in_w - 2 * ledge, 0.01, box_in_h - 2 * ledge]);
    }
    translate([x0 + ledge, y_ledge, z0 + ledge]) cube([box_in_w - 2 * ledge, ledge_t + 1, box_in_h - 2 * ledge]);
}

module box() {
    difference() {
        union() {
            difference() {
                cube([box_w, box_body_d, box_h]);
                cavity();
            }
            // lid screw bosses, cone underneath so they print
            for (s = lid_screws) translate([s[0], box_body_d - boss_len, s[1]]) {
                along_y(boss_d, boss_len);
                translate([0, -boss_d / 2, 0]) rotate([-90, 0, 0]) cylinder(d1 = 0.1, d2 = boss_d, h = boss_d / 2);
            }
            // board standoffs on the front wall
            for (p = board_holes) translate([p[0], box_front_t - 0.01, p[1]]) along_y(standoff_d, standoff_h);
            // mounting ears either side of the floor, stopping short of the lid skirt
            for (x = [-box_ear_w, box_w]) translate([x, 0, 0]) cube([box_ear_w, box_body_d - skirt_len - 1, box_ear_t]);
        }
        for (s = lid_screws) translate([s[0], box_body_d - m3_insert_len, s[1]]) along_y(m3_insert_d, m3_insert_len + 1);
        for (p = board_holes) translate([p[0], box_front_t - 1, p[1]]) along_y(standoff_hole, standoff_h + 1);
        for (h = box_ear_holes) translate([h[0], h[1], -1]) cylinder(d = m3_clear, h = box_ear_t + 2);
        // floor: glands and drip hole; roof: antenna bulkhead
        translate([pg9_x, gland_y, -1]) cylinder(d = pg9_d, h = box_floor_t + 2);
        translate([pg7_x, gland_y, -1]) cylinder(d = pg7_d, h = box_floor_t + 2);
        translate([box_w / 2, box_front_t + 4, -1]) cylinder(d = drip_d, h = box_floor_t + 2);
        translate([ant_x, gland_y, box_h - box_floor_t - 1]) cylinder(d = ant_d, h = box_floor_t + 2);
    }
}

module lid_screw_holes(h) {
    for (s = lid_screws) translate([s[0], s[1], -1]) cylinder(d = m3_clear, h = h + 2);
}

// Lid, flat on the bed: x across, y = box z (up as fitted), outer face down.
module lid() {
    o = skirt_gap + skirt_t;
    difference() {
        union() {
            cube([box_w, box_h, box_lid_t]);
            difference() {                      // rain skirt over the gasket line
                translate([-o, -o, 0]) cube([box_w + 2 * o, box_h + 2 * o, box_lid_t + skirt_len]);
                translate([-skirt_gap, -skirt_gap, box_lid_t]) cube([box_w + 2 * skirt_gap, box_h + 2 * skirt_gap, skirt_len + 1]);
            }
        }
        lid_screw_holes(box_lid_t);
        translate([0, 0, box_lid_t - groove_d]) cord_groove(box_w, box_h, groove_in);
    }
}

// Everything in box coordinates, as fitted.
module tree_box_assembly() {
    color("SteelBlue") box();
    color("LightSteelBlue") translate([0, box_d, 0]) rotate([90, 0, 0]) lid();   // skirt towards the front
}

if (part == "box") rotate([90, 0, 0]) box();   // front face on the bed, open side up
else if (part == "lid") lid();
else if (part == "assembly") tree_box_assembly();
