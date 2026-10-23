// Shared shell for the tree box and the site box: a box with rounded corners, one
// open face sealed by a lid with 2.7mm rubber cord (seal.scad), and a hollow sloped
// roof that sheds rain away from the mounting face and overhangs the lid joint as
// a hood with a drip lip.
//
// Box coordinates: x across, z up as fitted, y from the mounting face (y = 0: the
// tree side of the tree box, the post side of the site box) to the rim (y = D).
// Printed on the mounting face, open side up: every face is vertical or leans in,
// so no supports. The roof wedge is hollow (closed void) and its ends close in a V.

include <seal.scad>

sb_bed_ch    = 0.6;     // chamfer on the bed edges (elephant's foot)
sb_edge_ch   = 0.8;     // chamfer on the rim and lid edges
sb_slope     = 8;       // roof slope, degrees
sb_skin      = 2.4;     // roof wedge skin
sb_hood_gap  = 0.6;     // hood clearance above the lid's top edge
sb_hood_over = 3;       // hood beyond the lid's outer face
sb_drip      = 2;       // drip lip below the hood
sb_frame     = 12;      // lid: full thickness this far in from the edges (screws + cord)

module rrect(w, h, r) {
    translate([r, r]) offset(r = r) square([w - 2 * r, h - 2 * r]);
}

// The x-z outline extruded along y, with chamfers at y = 0 and y = d.
module rprism(w, h, d, r, ch0, ch1) {
    rotate([-90, 0, 0]) mirror([0, 1, 0]) hull() {
        linear_extrude(0.01) offset(delta = -ch0) rrect(w, h, r);
        translate([0, 0, ch0]) linear_extrude(d - ch0 - ch1) rrect(w, h, r);
        translate([0, 0, d - 0.01]) linear_extrude(0.01) offset(delta = -ch1) rrect(w, h, r);
    }
}

function sb_rise(len) = len * tan(sb_slope);

// Roof wedge on top of a box of outer height H, depth D, lid lid_t: high at y = 0,
// running past the rim to overhang the lid.
module sb_roof(W, H, D, lid_t, r) {
    y_end = D + lid_t + sb_hood_over;
    top0 = H + sb_hood_gap + sb_skin + sb_rise(y_end);       // at y = 0
    top1 = H + sb_hood_gap + sb_skin;                        // at the hood tip
    outer = [[0, H - 1], [0, top0], [y_end, top1], [y_end, H - sb_drip],
             [y_end - 1.6, H - sb_drip], [y_end - 1.6, H + sb_hood_gap], [D, H + sb_hood_gap], [D, H - 1]];
    void = [[sb_skin, H + 0.01], [sb_skin, top0 - sb_skin - sb_rise(sb_skin)],
            [D - sb_skin, top1 + sb_rise(y_end - D + sb_skin) - sb_skin], [D - sb_skin, H + 0.01]];
    difference() {
        intersection() {
            rotate([90, 0, 90]) linear_extrude(W) polygon(outer);
            // round the roof's corners like the box
            translate([0, -1, 0]) rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(y_end + 2) rrect(W, top0 + 1, r);
        }
        translate([sb_skin, 0, 0]) rotate([90, 0, 90]) linear_extrude(W - 2 * sb_skin) polygon(void);
    }
}

// Shell: outer W x H (x, z), depth D to the rim, walls `wall`, mounting face `base_t`,
// floor and roof `ft`, rim land `rim` (lid screws then the cord), outline radius r.
module sb_shell(W, H, D, wall, base_t, ft, rim, r, lid_t) {
    ledge = rim - wall;
    yl = D - 4;
    difference() {
        union() {
            rprism(W, H, D, r, sb_bed_ch, 0.4);
            sb_roof(W, H, D, lid_t, r);
        }
        // cavity, with the rim ledge's 45 degree underside
        translate([wall, base_t, ft]) cube([W - 2 * wall, yl - ledge - base_t, H - 2 * ft]);
        hull() {
            translate([wall, yl - ledge - 0.01, ft]) cube([W - 2 * wall, 0.01, H - 2 * ft]);
            translate([wall + ledge, yl, ft + ledge]) cube([W - 2 * wall - 2 * ledge, 0.01, H - 2 * ft - 2 * ledge]);
        }
        translate([wall + ledge, yl, ft + ledge]) cube([W - 2 * wall - 2 * ledge, 5, H - 2 * ft - 2 * ledge]);
    }
}

// Lid, flat on the bed with its outer face down: x across, y = box z.
// Thick frame round the edge (screws, cord groove), thin panel inside.
module sb_lid(W, H, lid_t, panel_t, r, screws, groove_in) {
    difference() {
        hull() {
            linear_extrude(0.01) offset(delta = -sb_edge_ch) rrect(W, H, r);
            translate([0, 0, sb_edge_ch]) linear_extrude(lid_t - sb_edge_ch - 0.4) rrect(W, H, r);
            translate([0, 0, lid_t - 0.01]) linear_extrude(0.01) offset(delta = -0.4) rrect(W, H, r);
        }
        // thin the panel inside the frame (from the inner face)
        translate([sb_frame, sb_frame, panel_t]) linear_extrude(lid_t)
            offset(r = 3) offset(delta = -3) square([W - 2 * sb_frame, H - 2 * sb_frame]);
        for (s = screws) translate([s[0], s[1], -1]) cylinder(d = 3.4, h = lid_t + 2, $fn = 24);
        translate([0, 0, lid_t - groove_d]) cord_groove(W, H, groove_in);
    }
}
