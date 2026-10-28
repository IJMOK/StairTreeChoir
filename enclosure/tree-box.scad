// Tree controller box (M3). PETG, on the shared sealed-box shell (sealed-box.scad):
// rounded corners, lid sealed with 2.7mm rubber cord, hollow roof sloping away from
// the tree with a hood and drip lip over the lid joint.
// Holds the 5x7cm controller board (electronics/), the Mini560, two Wago 221-413
// and the ends of the 12V flex and pixel lead. Sits on the tower of the control
// boot (feet/), behind the tree, with a gap to the oak; four M3 screws through its
// ears into heat-set inserts in the tower.
//
// As fitted: in the floor, the SP16 panel socket for the 12V run (rear nut, firing
// down; Rob, 28 Oct 2026, replacing the PG9 gland and pigtail) and the PG7 gland
// for the pixel lead, both pointing down into the boot tower; RP-SMA antenna bulkhead in the outer side wall
// (x = 0, away from the tree's centre) above the board, dipole hinged up (28 Oct 2026:
// the roof was 11mm thick there, the bulkhead clamps 3.2mm at most); lid on the back, facing away
// from the tree. Drip hole in the floor.
//
// Printing: box on its front face (open side up), no supports: the rim ledge and
// the lid screw bosses have 45 degree undersides. Lid flat, outer face down.
//
// UNVERIFIED until the parts arrive: board hole positions (pb_*), the SP16 hole and
// its nut clearance, the gland and bulkhead thread sizes, and that the ESP32 on its headers clears box_in_d.
// Sizes shared with the boot are in tree-box-params.scad.

include <tree-box-params.scad>
include <sealed-box.scad>

part = "assembly";       // "box", "lid", "coupon" or "assembly"; "box-fitted", "lid-fitted": as fitted (STEP export)

// Board: 5x7cm prototype board, M2 screws into the standoffs
pb_w          = 70;
pb_h          = 50;
pb_hole_in    = 2.5;     // hole centres from the board edges
pb_top_gap    = 12;      // board top edge below the roof: clear of the rim ledge
standoff_h    = 5;       // room for the underside joins
standoff_d    = 6;
standoff_hole = 1.8;     // M2 self-tapping

// Entries
sp16_d        = 16.7;    // SP16 panel socket, M16x1.5: listing hole 16.5 ...
sp16_flat     = 15.4;    // ... with one flat, 15.3 from the far side (stops it turning)
sp16_x        = 22;      // from the box's outer left
pg7_d         = 12.9;    // PG7 thread 12.5
pg7_x         = 59;
floor_y       = box_front_t + 13;   // floor parts' centre: their nuts (up to ~25 across corners) stay
                                    // on flat floor, in front of the rim ledge's slope
drip_d        = 3;
ant_d         = 6.6;     // RP-SMA bulkhead (1/4"-36)
ant_y         = box_front_t + 9;    // in the side wall: clear of the rim ledge (nut 8 AF)
ant_z         = box_h - box_floor_t - 6;   // above the board, below the roof

// Lid
lid_screw_in  = 3.5;     // lid screw centres from the outer edges; the cord runs inside them
groove_in     = 8;       // cord groove centreline from the outer edges
lid_panel_t   = 2;       // lid panel inside the thick frame
boss_d        = 7;
boss_len      = 10;      // screw bosses run this far in from the rim face
corner_r      = 4;       // outline corner radius

$fn = 48;

assert(floor_y + 12.7 <= box_body_d - 4 - (box_rim - box_wall),
       "floor sockets' nuts reach the rim ledge: deepen the box or move floor_y");

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

module along_y(d, l) {                          // cylinder along +y from y = 0
    rotate([-90, 0, 0]) cylinder(d = d, h = l);
}

module sp16_hole(h) {                           // D hole along z; the flat towards the lid (+y): the top when printed
    intersection() {
        cylinder(d = sp16_d, h = h);
        translate([-sp16_d / 2, -sp16_d / 2, 0]) cube([sp16_d, sp16_flat, h]);
    }
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
        }
        for (s = lid_screws) translate([s[0], box_body_d - m3_insert_len, s[1]]) along_y(m3_insert_d, m3_insert_len + 1);
        for (p = board_holes) translate([p[0], box_front_t - 1, p[1]]) along_y(standoff_hole, standoff_h + 1);
        for (h = box_ear_holes) translate([h[0], h[1], -1]) cylinder(d = m3_clear, h = box_ear_t + 2);
        // floor: SP16 socket, gland and drip hole; outer side wall: antenna bulkhead
        translate([sp16_x, floor_y, -1]) sp16_hole(box_floor_t + 2);
        translate([pg7_x, floor_y, -1]) cylinder(d = pg7_d, h = box_floor_t + 2);
        translate([box_w / 2, box_front_t + 4, -1]) cylinder(d = drip_d, h = box_floor_t + 2);
        translate([-1, ant_y, ant_z]) rotate([0, 90, 0]) cylinder(d = ant_d, h = box_wall + 2);
    }
}

// Fit coupon (28 Oct 2026): the box's holes in a 15-minute print, to try the real parts
// before printing a box. Floor plate (box_floor_t) with the SP16 D hole, the PG7 hole
// and the drip hole; a side-wall fin (box_wall) with the RP-SMA hole; a lid screw boss
// with its M3 insert hole; a board standoff. Prints flat as it lies, no supports.
module coupon() {
    l = 76; w = 30; fin_h = 18;
    difference() {
        union() {
            translate([0, 0, 0]) cube([l, w, box_floor_t]);
            translate([0, w - box_wall, 0]) cube([30, box_wall, fin_h]);                 // side-wall fin
            translate([44, w - boss_d / 2 - 1, 0]) cylinder(d = boss_d, h = boss_len);    // lid screw boss
            translate([66, w - standoff_d / 2 - 2, 0]) cylinder(d = standoff_d, h = box_floor_t + standoff_h);
        }
        translate([14, 13, -1]) sp16_hole(box_floor_t + 2);
        translate([38, 11, -1]) cylinder(d = pg7_d, h = box_floor_t + 2);
        translate([56, 8, -1]) cylinder(d = drip_d, h = box_floor_t + 2);
        translate([15, w - box_wall - 1, box_floor_t + 7]) rotate([-90, 0, 0]) cylinder(d = ant_d, h = box_wall + 2);
        translate([44, w - boss_d / 2 - 1, boss_len - m3_insert_len]) cylinder(d = m3_insert_d, h = m3_insert_len + 1);
        translate([66, w - standoff_d / 2 - 2, box_floor_t]) cylinder(d = standoff_hole, h = standoff_h + 1);
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
else if (part == "coupon") coupon();
