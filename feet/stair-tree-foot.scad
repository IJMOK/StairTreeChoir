// Stair Tree boot: a cartoon boot the tree stands in. Rough-in, PETG.
// Two per tree, at the wide (bottom) end. Each boot plugs into one of the old
// 17mm stair-fixing holes in the back face with a spigot, takes a wood screw
// into the old pilot hole beside it, carries the tree's bottom edge on a shelf
// held off the grass, and is pegged down with two 8mm nails (toe and heel).
//
// From the front you see a rounded toe and a low vamp, with the tree standing
// in it; the tall shaft and cuff sit behind the tree. Nothing rises in front of
// the tree above the low lip, so the bottom pixels stay clear.
//
// Hollow, like a real boot: open underneath, thin walls, solid tubes round the
// nails, a solid shaft wall behind the tree. 28 of them are needed, so material
// matters more than looks inside.
//
// Boot coordinates: x along the tree's width (+x = towards the tree centre),
// y through the tree (front face y = 0, back face y = tree_t, toe at -y),
// z up, ground z = 0. Built as the RIGHT boot seen from the front; left is mirrored.
//
// Printing (Bambu P1S): upright on the sole, no supports. The cavity roofs are
// sloped and the spigot is a short horizontal peg. PETG, 3 walls, 15% infill.
// Wind load on the shaft is about 1 MPa across the layers, far below PETG's
// layer strength, so upright is fine.
//
// UNVERIFIED: hole positions come from photos (data/blank.json); Rob to measure
// spigot hole depth/diameter and pilot offset on a real tread before printing 28.

hand = "right";          // "right" or "left"

// Tree (from data/blank.json)
tree_t        = 30;      // tread thickness
hole_z        = 44.1;    // old fixing hole centre above the bottom edge
pilot_dx      = 26.5;    // old pilot hole, inboard of the fixing hole centre
hole_to_side  = 13.3;    // fixing hole centre to the sloping side, at hole height

// Boot
clearance     = 50;      // tree bottom edge above the ground (shelf height)
wall          = 2.4;     // shell walls
top_t         = 4;       // shelf thickness under the tree
sole_t        = 6;       // welt flange
welt          = 3;       // flange sticks out past the upper by this much
toe_len       = 64;      // toe in front of the front lip
toe_bulge     = 6;       // toe wider than the shaft, on the outer side
toe_h         = 32;      // toe cap height
lip_t         = 5;       // front lip (vamp top) thickness
lip_h         = 8;       // lip above the shelf (bottom pixels start ~16mm up)
plate_t       = 8;       // shaft wall behind the tree
plate_above   = 26;      // shaft above the hole centre
cuff_h        = 12;      // turned-down cuff band at the top of the shaft
cuff_out      = 3;
heel_back     = 24;      // shaft flares back into the heel over this length
heel_h        = 20;      // heel height at the back of the flare
spur          = 24;      // flat heel spur behind the flare, for the heel nail
side_margin   = 2;       // keep the boot inside the tree's side edge
inboard       = 12;      // boot beyond the pilot hole, towards the centre

spigot_d      = 16.6;    // 0.4 clearance in the 17mm hole
spigot_len    = 20;      // hole is 23 deep
spigot_chamfer = 1.5;
screw_d       = 4.5;     // clearance for a 4mm wood screw into the old pilot
screw_head_d  = 9;
nail_d        = 8.8;     // 8mm x 200mm nails
nail_boss     = 3;       // solid wall round each nail
nail_head_d   = 18;      // flat seat for the nail head

$fn = 64;

x0 = -(hole_to_side - side_margin);
x1 = pilot_dx + inboard;
w  = x1 - x0;
xc = (x0 + x1) / 2;
zs = clearance;                     // shelf top = tree bottom edge
zh = clearance + hole_z;            // hole centre height
z_top = zh + plate_above;
y_back = tree_t + plate_t;
y_front = -lip_t;
y_toe = y_front - toe_len;
y_flare = y_back + heel_back;
y_end = y_flare + spur;
toe_r = (w + toe_bulge) / 2;
toe_cx = x1 - toe_r;                // flat on the inner side, bulging outwards
toe_cy = y_toe + toe_r;
toe_nail = [toe_cx, toe_cy - 4];
heel_nail = [xc, y_flare + spur / 2];

module footprint(grow = 0) {
    offset(r = grow) hull() {
        translate([toe_cx, toe_cy]) circle(r = toe_r);
        translate([x0 + 6, y_end - 6]) circle(r = 6);
        translate([x1 - 6, y_end - 6]) circle(r = 6);
        translate([x0, y_front]) square([w, 1]);
    }
}

module toe_dome(r) {
    translate([toe_cx, toe_cy, 0]) scale([1, 1.15, toe_h / toe_r]) sphere(r = r);
}

module outer() {
    // toe cap and vamp: the toe dome hulled up to the shelf under the tree
    hull() {
        toe_dome(toe_r);
        translate([x0, y_front, 0]) cube([w, y_back - y_front, zs]);
    }
    translate([x0, y_front, 0]) cube([w, lip_t, zs + lip_h]);      // front lip
    hull() {                                                          // shaft flaring into the heel
        translate([x0, tree_t, 0]) cube([w, plate_t, z_top - cuff_h]);
        translate([x0, y_flare - 1, 0]) cube([w, 1, heel_h]);
    }
    translate([x0, tree_t, z_top - cuff_h]) hull() {                  // cuff
        cube([w, plate_t + cuff_out, cuff_h - 3]);
        translate([0, 0, cuff_h - 3]) cube([w, plate_t + cuff_out - 3, 3]);
    }
    linear_extrude(sole_t) footprint(welt);                           // welt flange
}

// Hollows, open to the ground. Roofs slope at ~45 degrees so they print upright.
module cavities() {
    roof = zs - top_t;
    span = y_back - plate_t - (y_front + wall);                      // under the shelf, in front of the shaft wall
    hull() {
        toe_dome(toe_r - wall);
        translate([x0 + wall, y_front + wall, -1]) cube([w - 2 * wall, span, roof - span / 2 + 1]);
        translate([x0 + wall, y_front + wall + span / 2 - 1, -1]) cube([w - 2 * wall, 2, roof + 1]);
    }
    hull() {                                                          // inside the heel flare
        translate([x0 + wall, y_back, -1]) cube([w - 2 * wall, 0.01, z_top - cuff_h - 30]);
        translate([x0 + wall, y_flare - wall - 0.01, -1]) cube([w - 2 * wall, 0.01, heel_h - wall - 4]);
    }
}

module spigot() {
    cylinder(d = spigot_d, h = spigot_len - spigot_chamfer);
    translate([0, 0, spigot_len - spigot_chamfer])
        cylinder(d1 = spigot_d, d2 = spigot_d - 2 * spigot_chamfer, h = spigot_chamfer);
}

module boot() {
    difference() {
        intersection() {
            union() {
                difference() { outer(); cavities(); }
                // solid tubes round the nails, up to their seats
                translate([toe_nail[0], toe_nail[1], 0]) cylinder(d = nail_d + 2 * nail_boss, h = toe_h - 6);
                translate([heel_nail[0], heel_nail[1], 0]) cylinder(d = nail_d + 2 * nail_boss, h = sole_t);
                translate([0, tree_t, zh]) rotate([90, 0, 0]) spigot();
            }
            translate([-500, -500, 0]) cube([500 + x1, 1000, 500]);  // flat inner side
        }
        // welt line: a small groove where the flange meets the upper
        translate([0, 0, sole_t - 1]) linear_extrude(1.2) difference() { footprint(welt + 1); footprint(0); }
        // screw into the old pilot hole, countersunk, with a screwdriver tunnel through the heel
        translate([pilot_dx, tree_t - 1, zh]) rotate([-90, 0, 0]) {
            cylinder(d = screw_d, h = plate_t + 2);
            translate([0, 0, plate_t + 1 - 4]) cylinder(d1 = screw_d, d2 = screw_head_d, h = 4.01);
            translate([0, 0, plate_t + 1]) cylinder(d = screw_head_d + 1, h = 200);
        }
        // nails: through the toe cap (head seated 6mm down) and the heel spur
        translate([toe_nail[0], toe_nail[1], -1]) {
            cylinder(d = nail_d, h = 300);
            translate([0, 0, toe_h - 6 + 1]) cylinder(d = nail_head_d, h = 300);
        }
        translate([heel_nail[0], heel_nail[1], -1]) cylinder(d = nail_d, h = 300);
        // drain from the shelf into the hollow
        translate([xc, tree_t / 2, zs - top_t - 1]) cylinder(d = 5, h = top_t + 2);
    }
}

if (hand == "left") mirror([1, 0, 0]) boot(); else boot();
