// Stair Tree foot: rough-in, first pass. PETG.
// Two per tree, at the wide (bottom) end. Each foot plugs into one of the old
// 17mm stair-fixing holes in the back face with a spigot, takes a wood screw
// into the old pilot hole beside it, carries the tree's bottom edge on a shelf
// held off the grass, and is pegged down through its sole with 8mm nails.
//
// Foot coordinates: x along the tree's width (+x = towards the tree centre),
// y through the tree (front face y = 0, back face y = tree_t), z up, ground z = 0.
// Built as the RIGHT foot seen from the front; the left one is mirrored.
//
// Print lying on its flat outer side (the x = x0 face, nearest the tree's edge),
// so the layers run along the plate-to-shelf bend and the spigot.
// 5+ perimeters, 40%+ infill: that corner takes the wind load.
//
// UNVERIFIED: hole positions come from photos (data/blank.json); Rob to measure
// spigot hole depth/diameter and pilot offset on a real tread before printing 28.

hand = "right";          // "right" or "left"

// Tree (from data/blank.json)
tree_t        = 30;      // tread thickness
hole_z        = 44.1;    // old fixing hole centre above the bottom edge
hole_d        = 17;      // old fixing hole diameter
hole_depth    = 23;
pilot_dx      = 26.5;    // old pilot hole, inboard of the fixing hole centre
hole_to_side  = 13.3;    // fixing hole centre to the sloping side, at hole height

// Foot
clearance     = 50;      // tree bottom edge above the ground
sole_t        = 12;
wing_front    = 70;      // sole beyond the front face
wing_back     = 70;      // sole beyond the back plate
plate_t       = 10;      // back plate thickness
plate_above   = 28;      // back plate above the hole centre
lip_t         = 6;       // front lip thickness
lip_h         = 8;       // front lip height above the shelf (bottom pixels start ~16mm up)
side_margin   = 2;       // keep the foot inside the tree's side edge
inboard       = 14;      // foot beyond the pilot hole, towards the centre

spigot_d      = 16.6;    // 0.4 clearance in the 17mm hole
spigot_len    = 20;      // hole is 23 deep
spigot_chamfer = 1.5;
screw_d       = 4.5;     // clearance for a 4mm wood screw into the old pilot
screw_head_d  = 9;
nail_d        = 8.8;     // 8mm x 200mm nails
gusset_t      = 8;
nail_from_end = 14;      // nail centre from the end of each wing, clear of the gussets

$fn = 64;

x0 = -(hole_to_side - side_margin);
x1 = pilot_dx + inboard;
w  = x1 - x0;
zs = clearance;                     // shelf top = tree bottom edge
zh = clearance + hole_z;            // hole centre height
y_back = tree_t + plate_t;

module foot() {
    difference() {
        union() {
            // sole with front and back wings
            translate([x0, -lip_t - wing_front, 0]) cube([w, lip_t + wing_front + y_back + wing_back, sole_t]);
            // riser under the tree, up to the shelf
            translate([x0, -lip_t, 0]) cube([w, lip_t + y_back, zs]);
            // front lip
            translate([x0, -lip_t, 0]) cube([w, lip_t, zs + lip_h]);
            // back plate
            translate([x0, tree_t, 0]) cube([w, plate_t, zh + plate_above]);
            // spigot into the old hole
            translate([0, tree_t, zh]) rotate([90, 0, 0]) spigot();
            // gussets: back plate to back wing, front lip to front wing
            for (gx = [x0, x1 - gusset_t]) {
                translate([gx, y_back, sole_t]) gusset(wing_back - 2 * nail_from_end, zh + plate_above - sole_t - 10);
                translate([gx + gusset_t, -lip_t, sole_t]) rotate([0, 0, 180]) gusset(wing_front - 2 * nail_from_end, zs - sole_t);
            }
        }
        // screw into the old pilot hole, head countersunk on the back
        translate([pilot_dx, tree_t - 1, zh]) rotate([-90, 0, 0]) {
            cylinder(d = screw_d, h = plate_t + 2);
            translate([0, 0, plate_t + 1 - 4]) cylinder(d1 = screw_d, d2 = screw_head_d, h = 4.01);
        }
        // nail holes through the wings
        for (ny = [-lip_t - wing_front + nail_from_end, y_back + wing_back - nail_from_end])
            translate([(x0 + x1) / 2, ny, -1]) cylinder(d = nail_d, h = sole_t + 2);
        // drain: no pocket under the tree's end grain
        translate([(x0 + x1) / 2, tree_t / 2, zs - 3]) rotate([0, 90, 0]) cylinder(d = 4, h = w + 2, center = true);
    }
}

module spigot() {
    cylinder(d = spigot_d, h = spigot_len - spigot_chamfer);
    translate([0, 0, spigot_len - spigot_chamfer])
        cylinder(d1 = spigot_d, d2 = spigot_d - 2 * spigot_chamfer, h = spigot_chamfer);
}

// Right-angle triangle rib in the y-z plane, thickness gusset_t along x.
module gusset(len, height) {
    rotate([90, 0, 90]) linear_extrude(gusset_t)
        polygon([[0, 0], [len, 0], [0, height]]);
}

if (hand == "left") mirror([1, 0, 0]) foot(); else foot();
