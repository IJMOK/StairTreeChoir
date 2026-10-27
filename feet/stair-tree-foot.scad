// Stair Tree boot: a cartoon boot the tree stands in. PETG.
// Two per tree, at the wide (bottom) end: a plain boot on the right and the
// control boot on the left (as seen from the front). Each one carries the tree's
// bottom edge on a shelf held off the grass, is located by a peg through its
// shaft into one of the old 17mm stair-fixing holes, takes a wood screw into the
// old pilot hole beside it, and is pegged down with two 8mm nails (toe and heel).
//
// From the front you see a rounded toe and a low vamp, with the tree standing
// in it; the shaft sits behind the tree. Nothing rises in front of the tree above
// the low lip, so the bottom pixels stay clear.
//
// Assembly: stand the boots on blocks, lower the tree into them from above (the
// slot between lip and shaft is open at the top), then push a peg (part="peg")
// through each shaft into the old hole and drive the wood screw through the peg's
// tab into the old pilot hole: one screw holds both. The peg is separate because a
// fixed spigot would stop the tree dropping in.
//
// Control boot (left): node 1 (data in) is at the base-left, so this boot carries
// the tree controller box (enclosure/tree-box.scad) on a hollow tower behind the
// tree. The pixel lead leaves the tree through the exit slot in its bottom edge,
// drops through a hole in the shelf into the toe hollow, and runs back through an
// arch in the shaft into the tower, where it meets the box's PG7 tail. The 12V flex
// comes in at the back of the tower. Glands point down into the tower, so the box
// never faces rain with an entry. Order: tree, pegs and screws, nails, then the box.
//
// Hollow, like a real boot: open underneath, thin walls, solid tubes round the
// nails. 28 of them are needed, so material matters more than looks inside.
//
// Boot coordinates: x along the tree's width (+x = towards the tree centre),
// y through the tree (front face y = 0, back face y = tree_t, toe at -y),
// z up, ground z = 0. Built as the left (control) boot seen from the front, which
// puts +x to the right as you face it; the right (plain) boot is mirrored.
//
// Printing (Bambu P1S): upright on the sole, no supports. Cavity roofs are sloped
// and horizontal holes are teardrops. PETG, 3 walls, 15% infill. Peg: head down.
//
// UNVERIFIED: hole positions come from photos (data/blank.json); Rob to measure
// fixing hole depth/diameter, pilot offset and pilot diameter (screw size), and
// tread thickness, on a real tread before printing 28.

include <../enclosure/tree-box-params.scad>
use <../enclosure/tree-box.scad>

hand = "right";          // "right" (plain) or "left" (control boot)
part = "boot";           // "boot", "peg", or "preview" (boot + peg + box, not for printing)
                         // "peg-fitted", "box-fitted", "lid-fitted": as fitted, in boot coordinates (STEP export)
controller = hand == "left";

// Tree (from data/blank.json and data/tree-layout.json)
tree_t        = 30;      // tread thickness
hole_z        = 44.1;    // old fixing hole centre above the bottom edge
pilot_dx      = 26.5;    // old pilot hole, inboard of the fixing hole centre
hole_to_side  = 13.3;    // fixing hole centre to the sloping side, at hole height
hole_x_tree   = 20.5;    // left fixing hole from the tree's left bottom corner
node1_dx      = 5.4;     // node 1 (and the exit slot) inboard of the left fixing hole: 25.9 vs 20.5
side_slope    = 145 / 894;  // the sloping side moves inboard this much per mm up

// Boot
clearance     = 50;      // tree bottom edge above the ground (shelf height)
slot_clear    = 1.5;     // slot between lip and shaft wider than the tread
wall          = 2.4;     // shell walls
top_t         = 4;       // shelf thickness under the tree
sole_t        = 6;       // welt flange
welt          = 3;       // flange sticks out past the upper by this much
toe_len       = 64;      // toe in front of the front lip
toe_bulge     = 6;       // toe wider than the shaft, on the outer side
toe_h         = 32;      // toe cap height
lip_t         = 5;       // front lip (vamp top) thickness
lip_h         = 8;       // lip above the shelf (bottom pixels start ~16mm up)
plate_t       = 6;       // shaft wall behind the tree
plate_above   = 26;      // shaft above the hole centre
cuff_h        = 12;      // turned-down cuff band at the top of the shaft
cuff_out      = 3;
heel_back     = 24;      // shaft flares back into the heel over this length
heel_h        = 20;      // heel height at the back of the flare
spur          = 24;      // flat heel spur behind the flare, for the heel nail
side_margin   = 2;       // keep the boot inside the tree's side edge
edge_r        = 2.5;     // upright edges rounded
welt_ch       = 1.5;     // chamfer on the welt's top edge (and 0.6 on the bed edge)
cuff_fall     = 4;       // cuff top falls this much towards the back, shedding rain off the tree
inboard       = 12;      // boot beyond the pilot hole, towards the centre

// Peg (separate part): shaft through the boot's shaft wall into the old hole,
// head with a tab that the pilot-hole screw goes through
peg_d         = 16.6;    // 0.4 clearance in the 17mm hole
peg_hole_d    = 17.2;    // in the boot
peg_depth     = 20;      // into the tree; the old hole is 23 deep
peg_chamfer   = 1.5;
peg_head_d    = 19;
peg_tab_w     = 13;
peg_head_t    = 5;
screw_d       = 4.5;     // clearance for a 4 x 30 countersunk wood screw into the old pilot
screw_head_d  = 9;
nail_d        = 8.8;     // 8mm x 200mm nails
nail_boss     = 3;       // solid wall round each nail
nail_head_d   = 18;      // flat seat for the nail head

// Control boot
lead_hole_d   = 16;      // pixel lead and its xConnect plug, down through the shelf (UNVERIFIED plug size)
arch_w        = 24;      // through the shaft wall under the shelf: toe hollow to tower
arch_h        = 30;
tower_wall    = 2.4;
post          = 12;      // corner posts under the box ears (square)
post_h        = 14;
feed_w        = 14;      // 12V flex entry, bottom of the tower's back wall
feed_h        = 24;
box_margin    = 3;       // box kept this far inside the tree's sloping edge

$fn = 64;

x0 = -(hole_to_side - side_margin);
x1 = pilot_dx + inboard;
w  = x1 - x0;
xc = (x0 + x1) / 2;
zs = clearance;                     // shelf top = tree bottom edge
zh = clearance + hole_z;            // hole centre height
z_top = zh + plate_above;
y_back = tree_t + plate_t;
y_front = -slot_clear - lip_t;
y_toe = y_front - toe_len;
y_flare = y_back + heel_back;
y_end = y_flare + spur;
toe_r = (w + toe_bulge) / 2;
toe_cx = x1 - toe_r;                // flat on the inner side, bulging outwards
toe_cy = y_toe + toe_r;
toe_nail = [toe_cx, toe_cy - 4];

// Control boot: the box sits on a tower behind the shaft. Its top corner must stay
// inside the sloping edge of the tree so it can't be seen from the front.
zb = z_top;                                                  // tower top = box floor
box_x = max((zb + box_h + box_roof_h - zs) * side_slope + box_margin - hole_x_tree, x0 + box_ear_w);  // box outer left
tx0 = box_x - box_ear_w;                                     // tower outer left
tx1 = tx0 + box_span;
ty1 = y_back + box_body_d;
heel_nail = controller ? [tx0 + box_span * 0.75, ty1 - tower_wall - nail_d / 2 - nail_boss]
                       : [xc, y_flare + spur / 2];
x_max = controller ? tx1 : x1;

module footprint(grow = 0) {
    offset(r = grow) hull() {
        translate([toe_cx, toe_cy]) circle(r = toe_r);
        if (controller) translate([x0, y_back - 1]) square([w, 1]);
        else {
            translate([x0 + 6, y_end - 6]) circle(r = 6);
            translate([x1 - 6, y_end - 6]) circle(r = 6);
        }
        translate([x0, y_front]) square([w, 1]);
    }
    if (controller) offset(r = grow) translate([tx0, y_back - 1]) square([box_span, box_body_d + 1]);
}

module toe_dome(r) {
    translate([toe_cx, toe_cy, 0]) scale([1, 1.15, toe_h / toe_r]) sphere(r = r);
}

// 2D teardrop pointing at -y; along_y() turns that into a point at +z
module teardrop(d) {
    hull() {
        circle(d = d);
        translate([0, -d / 2 * sqrt(2)]) square(0.01, center = true);
    }
}

// 2D pointed arch standing on y = 0, pointing at -y (so +z after along_y)
module arch(aw, ah) {
    polygon([[0, 1], [aw, 1], [aw, -(ah - aw / 2)], [aw / 2, -ah], [0, -(ah - aw / 2)]]);
}

module along_y(y0, y1) {                     // extrude 2D children along +y; 2D -y becomes +z
    translate([0, y0, 0]) rotate([-90, 0, 0]) linear_extrude(y1 - y0) children();
}

// cube with its upright (z) edges rounded
module rcube(s, r = edge_r) {
    hull() for (x = [r, s[0] - r]) for (y = [r, s[1] - r]) translate([x, y, 0]) cylinder(r = r, h = s[2]);
}

module tower() {
    difference() {
        translate([tx0, y_back - 0.01, 0]) rcube([box_span, box_body_d + 0.01, zb], 3);
        translate([tx0 + tower_wall, y_back + tower_wall, -1]) cube([box_span - 2 * tower_wall, box_body_d - 2 * tower_wall, zb + 2]);
    }
    // posts under the ears, chamfered underneath
    for (h = box_ear_holes) {
        left = h[0] < 0;
        front = h[1] < box_body_d / 2;
        px = left ? tx0 : tx1 - post;
        py = front ? y_back : ty1 - post;
        hull() {
            translate([px, py, zb - post_h]) cube([post, post, post_h]);
            translate([left ? tx0 : tx1 - 0.01, front ? y_back : ty1 - 0.01, zb - post_h - post]) cube([0.01, 0.01, post]);
        }
    }
    // heel nail boss on the back wall
    translate([heel_nail[0], heel_nail[1], 0]) hull() {
        cylinder(d = nail_d + 2 * nail_boss, h = sole_t);
        translate([-(nail_d / 2 + nail_boss), 0, 0]) cube([nail_d + 2 * nail_boss, ty1 - heel_nail[1], sole_t]);
    }
}

module outer() {
    // toe cap and vamp: the toe dome hulled up to the shelf under the tree
    hull() {
        toe_dome(toe_r);
        translate([x0, y_front, 0]) rcube([w, y_back - y_front, zs]);
    }
    translate([x0, y_front, 0]) hull() {                              // front lip, rounded top
        rcube([w, lip_t, zs + lip_h - lip_t / 2], lip_t / 2);
        translate([lip_t / 2, lip_t / 2, zs + lip_h - lip_t / 2]) rotate([0, 90, 0]) cylinder(d = lip_t, h = w - lip_t);
    }
    if (controller) {
        translate([x0, tree_t, 0]) rcube([w, plate_t, z_top - cuff_h]);
        tower();
    } else hull() {                                                   // shaft flaring into the heel
        translate([x0, tree_t, 0]) rcube([w, plate_t, z_top - cuff_h]);
        translate([x0, y_flare - 2 * edge_r, 0]) rcube([w, 2 * edge_r, heel_h]);
    }
    translate([x0, tree_t, z_top - cuff_h]) hull() {                  // cuff, top falling away from the tree
        rcube([w, plate_t + cuff_out, cuff_h - cuff_fall]);
        rcube([w, 2 * edge_r, cuff_h]);
    }
    welt_flange();
}

// welt flange: 0.6 chamfer on the bed edge, welt_ch on the top edge
module welt_flange() {
    linear_extrude(0.6) footprint(welt - 0.6);
    translate([0, 0, 0.6]) linear_extrude(sole_t - 0.6 - welt_ch) footprint(welt);
    for (i = [1 : 3]) translate([0, 0, sole_t - welt_ch + (i - 1) * welt_ch / 3])
        linear_extrude(welt_ch / 3) footprint(welt - i * welt_ch / 3);
}

// Hollows, open to the ground. Roofs slope at ~45 degrees so they print upright.
module cavities() {
    roof = zs - top_t;
    span = tree_t - (y_front + wall);                                // under the shelf, in front of the shaft wall
    hull() {
        toe_dome(toe_r - wall);
        translate([x0 + wall, y_front + wall, -1]) cube([w - 2 * wall, span, roof - span / 2 + 1]);
        translate([x0 + wall, y_front + wall + span / 2 - 1, -1]) cube([w - 2 * wall, 2, roof + 1]);
    }
    if (controller)                                                   // welt flange inside the tower
        translate([tx0 + tower_wall, y_back + tower_wall, -1]) cube([box_span - 2 * tower_wall, box_body_d - 2 * tower_wall, sole_t + 2]);
    else hull() {                                                     // inside the heel flare
        translate([x0 + wall, y_back, -1]) cube([w - 2 * wall, 0.01, z_top - cuff_h - 30]);
        translate([x0 + wall, y_flare - wall - 0.01, -1]) cube([w - 2 * wall, 0.01, heel_h - wall - 4]);
    }
}

module peg_head_2d(grow = 0) {
    hull() {
        circle(d = peg_head_d + 2 * grow);
        translate([pilot_dx, 0]) circle(d = peg_tab_w + 2 * grow);
    }
}

// Peg as fitted: head against the back of the shaft wall, shaft into the tree.
module peg() {
    difference() {
        union() {
            translate([0, y_back, zh]) rotate([-90, 0, 0]) hull() {      // head, edges chamfered
                linear_extrude(0.01) peg_head_2d(-0.8);
                translate([0, 0, 0.8]) linear_extrude(peg_head_t - 1.6) peg_head_2d();
                translate([0, 0, peg_head_t - 0.01]) linear_extrude(0.01) peg_head_2d(-0.8);
            }
            translate([0, y_back + 0.01, zh]) rotate([90, 0, 0]) {
                cylinder(d = peg_d, h = plate_t + peg_depth - peg_chamfer + 0.01);
                translate([0, 0, plate_t + peg_depth - peg_chamfer])
                    cylinder(d1 = peg_d, d2 = peg_d - 2 * peg_chamfer, h = peg_chamfer);
            }
        }
        translate([pilot_dx, y_back - 1, zh]) rotate([-90, 0, 0]) {
            cylinder(d = screw_d, h = peg_head_t + 2);
            translate([0, 0, peg_head_t + 1 - 3]) cylinder(d1 = screw_d, d2 = screw_head_d, h = 3.01);
        }
    }
}

// Peg laid out for printing: head down, screw countersink on the bed side.
module peg_print() {
    rotate([-90, 0, 0]) translate([0, -(y_back + peg_head_t), -zh]) peg();
}

module boot() {
    difference() {
        intersection() {
            union() {
                difference() { outer(); cavities(); }
                // solid post round the toe nail, filling up to the toe roof so it joins the shell
                // (wider than the head seat, or the seat cuts it free)
                intersection() {
                    outer();
                    translate([toe_nail[0], toe_nail[1], 0]) cylinder(d = nail_head_d + 2 * nail_boss, h = toe_h + 10);
                }
                // heel nail goes through the solid spur
                if (!controller) translate([heel_nail[0], heel_nail[1], 0]) cylinder(d = nail_d + 2 * nail_boss, h = sole_t);
            }
            translate([-500, -500, 0]) cube([500 + x_max, 1000, 500]);  // flat inner side
        }
        // welt line: a small groove where the flange meets the upper
        translate([0, 0, sole_t - 1]) linear_extrude(1.2) difference() { footprint(welt + 1); footprint(0); }
        // peg and screw through the shaft wall; behind it, a tunnel the peg head fits through
        translate([0, 0, zh]) along_y(tree_t - 1, y_back + 1) teardrop(peg_hole_d);
        translate([pilot_dx, 0, zh]) along_y(tree_t - 1, y_back + 1) teardrop(screw_d);
        translate([0, 0, zh]) along_y(y_back, 300) hull() {
            teardrop(peg_head_d + 1);
            translate([pilot_dx, 0]) teardrop(peg_tab_w + 1);
        }
        // nails: through the toe cap (head seated 6mm down) and the heel spur / tower boss
        translate([toe_nail[0], toe_nail[1], -1]) {
            cylinder(d = nail_d, h = 300);
            translate([0, 0, toe_h - 6 + 1]) cylinder(d = nail_head_d, h = 300);
        }
        translate([heel_nail[0], heel_nail[1], -1]) cylinder(d = nail_d, h = 300);
        // drain from the shelf into the hollow
        translate([xc, tree_t / 2, zs - top_t - 1]) cylinder(d = 5, h = top_t + 2);
        if (controller) {
            // pixel lead: exit slot in the tree's bottom edge, through the shelf into the toe hollow
            translate([node1_dx, tree_t - 7, -1]) cylinder(d = lead_hole_d, h = zs + 2);
            // arch through the shaft wall: toe hollow to tower
            translate([max(tx0 + tower_wall, x0 + wall), 0, 0]) along_y(tree_t - 1, y_back + tower_wall + 1) arch(arch_w, arch_h);
            // 12V flex entry, bottom of the tower's back wall
            translate([tx0 + box_span * 0.4, 0, 0]) along_y(ty1 - tower_wall - 1, ty1 + 1) arch(feed_w, feed_h);
            // M3 heat-set inserts for the box ears
            for (h = box_ear_holes) translate([box_x + h[0], y_back + h[1], zb - m3_insert_len])
                cylinder(d = m3_insert_d, h = m3_insert_len + 1);
        }
    }
}

module hand() {
    if (hand == "right") mirror([1, 0, 0]) children(); else children();
}

if (part == "boot") hand() boot();
else if (part == "peg") peg_print();
else if (part == "peg-fitted") hand() peg();
else if (part == "box-fitted") hand() translate([box_x, y_back, zb]) box();
else if (part == "lid-fitted") hand() translate([box_x, y_back + box_body_d + box_lid_t, zb]) rotate([90, 0, 0]) lid();
else if (part == "preview") hand() {
    color("Peru") boot();
    color("DarkOrange") peg();
    if (controller) translate([box_x, y_back, zb]) tree_box_assembly();
    %translate([-hole_x_tree, 0, zs]) cube([160, tree_t, 220]);      // the bottom corner of the tread (ghost)
}
