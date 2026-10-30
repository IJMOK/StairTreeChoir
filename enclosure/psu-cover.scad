// Terminal cover for the Site A S-400-12 PSU (Rob, 30 Oct 2026). PETG.
//
// A hood over the PSU's open terminal end: top, sides and end wall, open underneath. It
// slides on from the end and is held by two M4 × 6 screws into the case's threaded side
// holes, so it takes a tool to get it off. Don't use longer screws: past about 3mm they
// reach into the PSU. The slots allow for the hole positions being estimates.
//
// A rib between -V and earth keeps the mains side apart from the 12V side, and each side
// has its own cable notch in the end wall, open at the bottom so the hood fits over
// wired cables. Anchor the mains lead in the cord grip: this cover doesn't grip it.
//
// Facing the terminals, left to right (the PSU's own markings): ADJ, +V × 3, -V × 3,
// earth, N, L. The trim and the LED are under the hood: take it off to adjust.
//
// Printing, no supports: end wall on the bed.
//
// Frame: x across from the case's left side, facing the terminals; y outwards from the
// tips of the case's side lips; z up from the underside of the case.
//
// UNVERIFIED: every size here is scaled from Rob's photos, using his case size of
// 217 × 114 × 50. Offer up the print before wiring: check the side holes line up with
// the slots and that the case's side screws clear the tabs.

part = "print";          // "print", "fitted"

case_w      = 114;
case_h      = 50;
fit         = 0.4;       // each side, and over the top
wall        = 2.4;
end_t       = 2.4;
y_end       = 10;        // inside of the end wall, past the lip tips: room for the cables
y_lid       = -23;       // where the case's lid stops
y_skirt     = -26;       // the top and full sides stop here, just over the lid
y_tab       = -38;       // the tabs run on to the side holes
tab_z       = [8, 47];   // the tabs' height, leaving 5mm of tab above the slots
hole_y      = -32;       // the case's side holes, from the lip tips
hole_z      = 38;
slot_d      = 4.5;
slot_y      = 4;         // slot travel each way
slot_z      = 1.5;

divide_x    = 76.5;      // the rib, between -V and earth
rib_t       = 2.4;
rib_y       = -10;
rib_z       = 25;        // above the terminal block
mains_x     = 98;        // cable notches in the end wall
mains_w     = 11;
mains_h     = 13;
low_x       = 42;
low_w       = 18;
low_h       = 10;

corner_r    = 5;
$fn = 64;

W = case_w + 2 * (fit + wall);
H = case_h + fit + wall;
x0 = -fit - wall;
y1 = y_end + end_t;

// Rounded top corners, square bottom, in x-z, extruded along y
module xz_prof(x, w, h, r, y0, y1) {
    translate([x, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) hull() {
        translate([r, h - r]) circle(r = r);
        translate([w - r, h - r]) circle(r = r);
        translate([0, -1]) square([w, 1]);
    }
}

module notch(x, w, h) {            // U in the end wall, open at the bottom
    translate([x, y_end - 1, 0]) rotate([-90, 0, 0]) linear_extrude(end_t + 2) hull() {
        translate([0, -h + w / 2]) circle(d = w);
        translate([-w / 2, 1]) square([w, 1]);
    }
}

module cover() {
    difference() {
        union() {
            difference() {
                xz_prof(x0, W, H, corner_r, y_tab, y1);
                xz_prof(-fit, case_w + 2 * fit, case_h + fit, corner_r - wall, y_tab - 1, y_end);
                translate([x0 - 1, y_tab - 1, -2]) cube([W + 2, y_skirt - y_tab + 1, tab_z[0] + 2]);    // the tabs
                translate([x0 - 1, y_tab - 1, tab_z[1]]) cube([W + 2, y_skirt - y_tab + 1, H]);
            }
            translate([divide_x - rib_t / 2, rib_y, rib_z]) cube([rib_t, y_end - rib_y + 0.01, case_h + fit - rib_z + 0.5]);
        }
        notch(mains_x, mains_w, mains_h);
        notch(low_x, low_w, low_h);
        for (x = [x0 - 1, case_w + fit - 1]) translate([x, 0, 0]) hull()
            for (dy = [-slot_y, slot_y], dz = [-slot_z, slot_z])
                translate([0, hole_y + dy, hole_z + dz]) rotate([0, 90, 0]) cylinder(d = slot_d, h = wall + 2);
    }
}

if (part == "fitted") cover();
else translate([0, 0, y1]) rotate([-90, 0, 0]) cover();                         // end wall on the bed
