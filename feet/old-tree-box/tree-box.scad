// FROZEN 1 Nov 2026: the tree box moved to FreeCAD (enclosure/tree-box.FCStd). This is here only so
// the parked boot still builds. Don't change the box here.
//
// Tree controller box (M3), L base + wrap-round cover (Rob, 31 Oct 2026). PETG.
//
// Base: an L. A back plate on 10mm spacers off the tree, with a blended ear at each
// corner (a slot each), and a shelf along its bottom. It carries everything, so it is
// all built and wired on the bench: the controller board on four standoffs on the
// plate, the Mini560 standing on the board, the Wagos on the plate, and firing down
// through the shelf the SP16 panel socket (12V run), the PG7 gland (pixel lead) and the
// RP-SMA bulkhead (antenna). Nothing unplugs when the cover comes off.
//
// Cover: back, sides and a roof sloping 8 degrees away from the tree, wrapping round the
// plate's top and side edges, notched round the ears. A hook under the roof catches the
// plate's top edge from behind: hold the cover tilted with its bottom out, lift it over
// the edge, drop it and swing it in, then one M3 goes in at the bottom. The hook is at
// the very top so that everything lies below the pivot and swings clear of the plate.
// Nothing of the cover goes under the shelf: a swing about the top lifts anything under
// there into it. The side skirts only guide and shed rain; 5mm is too short to flex as a
// snap. The screw is at 45 degrees, through the bevel on the cover's lower back corner
// into an insert in a boss on the shelf: it pulls the cover in against the cord and up
// until the roof meets the plate's top edge, and a straight-up screw wouldn't.
//
// Seal: the 2.7mm cord lies in a groove in the plate's back face, over the top and down
// both sides, held by pinch points, and the cover's rim lands on it. The cover swings
// onto it, so nothing slides along the cord. The bottom is open on purpose: rain doesn't
// fall upwards, and anything that gets in drains out.
//
// Made for the printer (PETG, 0.4 nozzle, no supports):
// - Base with the tree face on the bed; cover with its back on the bed. Both grow along
//   y, so outlines in x-z can take any radius, and every face that looks down on the
//   way up is 45 degrees or better.
// - The cover's back edge is a radius that stops at 45 degrees and runs out in a chamfer
//   at the bed, so it needs no support and hides elephant's foot. The inside follows it,
//   which keeps the walls even.
// - The rim ramps out of the walls at 45 degrees instead of bridging.
// - Holes along z in the shelf are teardrops (or D-shaped) pointing up the print.
// - The hook pulls across the layers: that is why it is one long block, not two tabs.
//
// UNVERIFIED until measured: board hole positions (pb_*), the SP16 nut and thread
// length, the gland and bulkhead sizes; the squeeze along the sides from one screw and
// two hooks (print seal-test).
// Shared sizes are in tree-box-params.scad; tools/gen_components.py checks the parts fit.

include <tree-box-params.scad>
include <seal.scad>

part = "assembly";       // "base", "cover", "coupon", "seal-test", "spacer", "assembly";
                         // "base-fitted", "cover-fitted": as fitted (STEP export)

// Board: 5x7cm prototype board on the plate, M2 screws into heat-set inserts in the standoffs
pb_w          = 70;
pb_h          = 50;
pb_hole_in    = 2.0;     // hole centres from the board edges: from Rob's photo (30 Oct 2026), measure it
board_z0      = 34.5;    // above the Wagos
standoff_h    = 5;       // room for the underside joins
standoff_d    = 6;
standoff_foot = 0.8;      // cone at the root, standing off the plate
standoff_hole = 3.2;     // M2 heat-set insert (Rob, 31 Oct 2026): check against the real insert on the coupon

// Shelf entries, firing down
sp16_d        = 16.7;    // SP16 panel socket, M16x1.5: drawing hole 16.5 ...
sp16_flat     = 15.4;    // ... with one flat, 15.3 from the far side (stops it turning)
pg7_d         = 12.9;    // PG7 thread 12.5
ant_d         = 6.6;     // RP-SMA, 1/4"-36
ant_panel     = 3;       // shelf left at the bulkhead: it takes 3.2 at most
ant_recess_d  = 14;      // room for its nut
floor_y       = plate_t + 14;      // their centres: nuts (up to ~25 across corners) clear of the plate
ant_x         = 10;      // outer side, away from the tree's centre
sp16_x        = 29;
pg7_x         = 72;

// Cover's rim: lands on the plate
rim_w         = 6.5;
rim_top       = 10;      // below box_h
rim_d         = 3;       // rim depth, before it ramps back to the walls
rim_z0        = floor_z + 0.3;     // the rim stops above the shelf
open_r        = 5;

// Cord: a U, centred on the side rims and across the top. Its ends stop above the shelf
cord_x        = rim_w / 2;
cord_top      = box_h - rim_top + rim_w / 2;
cord_end      = rim_z0 + 6;
pinch_gap     = 2.4;     // pinch points narrow the 3.8 groove to this, to hold the 2.7 cord
pinch_l       = 1.6;
pinch_every   = 22;

// Top hook: a block under the roof, behind the plate. Its 45 degree face hangs on a
// chamfer along the plate's top edge at the tree face, so the cover's own weight seats it
hook_x0       = 18;
hook_w        = box_w - 2 * hook_x0;
hook_c        = 2;       // the chamfer: the lift needed to get over the edge
hook_back     = 2.8;     // block thickness behind the chamfer
hook_fit      = 0.2;     // hook face to the chamfer, along y
top_gap       = 0.2;     // plate's top edge to the roof's underside: the screw closes it

// Skirts: round the plate's edges, stopping short of the ears. The top of each notch
// leaves room for the lift over the hook
skirt_end     = 1.5;     // skirt to the ears' fillets, below the notch
skirt_lift    = 2.5;     // ... and above it

// Bottom screw: M3 x 10 at 45 degrees through the cover's bevel into the shelf's boss
bevel         = 13;      // cut off the cover's lower back corner
bevel_t       = 3.6;     // wall there, square to the bevel: the screw head sits in it
head_cb_d     = 7;       // the head's counterbore
head_cb_h     = 1.4;
boss_x        = 50;      // between the SP16 and the PG7
boss_d        = 11;
boss_l        = 9;       // into the shelf, square to the bevel
boss_along    = 8;       // the screw's centre along the bevel from the shelf's underside
rib_t         = 4;       // from the boss to the plate, under the Wagos
rib_h         = 6.5;
shelf_fillet  = 2;       // shelf to plate

// Mounting on the back of the tree
ear_w         = 15;      // beyond each side of the plate: the head and washer clear the cover's wall
ear_h         = 26;
ear_r         = 6;       // corners
ear_fillet    = 3;       // where they leave the plate
mount_slot_d  = 4.6;     // 4mm stainless wood screws (4 x 40 pan head + washer)
mount_slot_l  = 6;       // slot travel, up and down
mount_z       = [18, 80];
spacer_d      = 10;
spacer_l      = 10;      // rain gap between the oak and the box

// Outline
roof_slope    = 8;       // degrees, down away from the tree
roof_back     = 1;       // roof thickness above box_h at the back edge
blend_r       = 8;       // back edge of the cover
foot_r        = 3;       // the cover's bottom corners
edge_ch       = 0.5;     // the cover's rim, against the plate

$fn = 64;

board_x0 = (box_w - pb_w) / 2;
shelf_x0 = cover_wall + cover_fit;
shelf_w  = box_w - 2 * shelf_x0;
in_back  = plate_t + box_in_d;                // cover's back wall, inside face
wrap     = cover_wall + cover_fit;            // the cover past the plate's edges
cx0      = -wrap;                             // cover's outside ...
cx1      = box_w + wrap;
ix0      = -cover_fit;                        // ... and inside faces
ix1      = box_w + cover_fit;
plate_top = roof_z(plate_t) - cover_wall - top_gap;
s2       = sqrt(0.5);
// The bevel: outside face z = y - bevel_o, inside face z = y + bevel_c
bevel_o  = cover_y1 - bevel;
bevel_c  = bevel_t / s2 - bevel_o;
board_holes = [
    for (x = [pb_hole_in, pb_w - pb_hole_in])
        for (z = [pb_hole_in, pb_h - pb_hole_in]) [board_x0 + x, board_z0 + z]
];
screw_mid = [lip_t - bevel_c + boss_along * s2, lip_t + boss_along * s2];   // (y, z) on the bevel's inside face

function roof_z(y) = box_h + roof_back + (cover_y1 - y) * tan(roof_slope);
function bevel_z(y) = max(0, y - bevel_o);
function shelf_y(z) = z - bevel_c - 0.3;      // the shelf stops just short of the bevel
// How far a blended edge is in at t from the bed: radius r, down to 45 degrees, then a chamfer
function blend(t, r) = let (ts = r * (1 - s2))
    t >= r ? 0 : t < ts ? 2 * ts - t : r - sqrt(r * r - (r - t) * (r - t));

assert(floor_y + 12.7 <= shelf_y(lip_t), "floor nuts reach the bevel: move floor_y or deepen the box");
assert(board_z0 + pb_h + 2 <= box_h - rim_top, "board too high for the cover's opening");
assert(board_z0 > floor_z + 20, "board too low: the SP16 body stands ~19mm off the shelf");
assert(plate_top - hook_c > cord_top + groove_w / 2 + 1, "hook chamfer reaches the cord groove");
assert(floor_z + rib_h < floor_z + 7, "rib reaches the Wagos");

// ---- shapes ------------------------------------------------------------------------

// Rounded profile in x-z (u = x, v = z): radius rt at the top, rb at the bottom
module prof(x0, z0, x1, z1, rt, rb) {
    hull() {
        translate([x0 + rt, z1 - rt]) circle(r = rt);
        translate([x1 - rt, z1 - rt]) circle(r = rt);
        translate([x0 + rb, z0 + rb]) circle(r = rb);
        translate([x1 - rb, z0 + rb]) circle(r = rb);
    }
}

// That profile as a thin slice at y, inset by i, radii following
module slice(y, x0, z0, x1, z1, rt, rb, i = 0) {
    translate([0, y + 0.01, 0]) rotate([90, 0, 0]) linear_extrude(0.01)
        prof(x0 + i, z0 + i, x1 - i, z1 - i, max(rt - i, 0.4), max(rb - i, 0.4));
}

// A y-z polygon extruded across x
module yz_prism(x0, w, pts) {
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(w) polygon(pts);
}

module along_y(d, l) { rotate([-90, 0, 0]) cylinder(d = d, h = l); }

// Hole along z, pointing up the print (+y) so it needs no support
module teardrop(d, h) {
    linear_extrude(h) hull() {
        circle(d = d);
        translate([0, d / 2 / s2 - 0.05]) square(0.1, center = true);
    }
}

module sp16_hole(h) {     // D hole along z; the flat towards the back (+y): the top when the base prints
    intersection() {
        cylinder(d = sp16_d, h = h);
        translate([-sp16_d / 2, -sp16_d / 2, 0]) cube([sp16_d, sp16_flat, h]);
    }
}

// Move to the screw's position on the bevel's inside face, +z pointing into the boss
module at_screw() {
    translate([boss_x, screw_mid[0], screw_mid[1]]) rotate([45, 0, 0]) children();
}

// ---- base ----------------------------------------------------------------------------

module plate_2d() {
    offset(r = ear_r) offset(delta = -ear_r)              // the ears' corners
    offset(r = -ear_fillet) offset(delta = ear_fillet)    // the fillets where they leave the plate
    union() {
        prof(0, lip_t, box_w, plate_top, corner_r, 0.4);
        for (x = [-ear_w, box_w], z = mount_z)
            translate([x - 1 * (x > 0 ? 1 : 0), z - ear_h / 2]) square([ear_w + 1, ear_h]);
    }
}

module plate() {
    module layer(y0, y1, i) {
        translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) offset(delta = -i) plate_2d();
    }
    for (s = [[0, 0.2, 0.5], [0.2, 0.4, 0.3], [0.4, 0.6, 0.1]]) layer(s[0], s[1], s[2]);    // chamfer at the bed
    layer(0.6, plate_t - 0.4, 0);
    for (s = [[plate_t - 0.4, plate_t - 0.2, 0.1], [plate_t - 0.2, plate_t, 0.3]]) layer(s[0], s[1], s[2]);
}

module mount_slots() {
    for (x = [-ear_w / 2, box_w + ear_w / 2]) for (z = mount_z)
        hull() for (dz = [-mount_slot_l / 2, mount_slot_l / 2])
            translate([x, -1, z + dz]) along_y(mount_slot_d, plate_t + 2);
}

// Shelf, its back cut parallel to the cover's bevel, the fillet to the plate, the boss
// on a foot and the rib that ties it back to the plate
module shelf() {
    yz_prism(shelf_x0, shelf_w, [[plate_t - 0.01, lip_t], [shelf_y(lip_t), lip_t], [shelf_y(floor_z), floor_z],
                                 [plate_t - 0.01, floor_z]]);
    yz_prism(rim_w + open_r + 0.5, box_w - 2 * (rim_w + open_r + 0.5),    // the fillet, clear of the rim's corners
             [[plate_t - 0.01, floor_z - 0.01], [plate_t + shelf_fillet, floor_z - 0.01], [plate_t - 0.01, floor_z + shelf_fillet]]);
    hull() {
        at_screw() translate([0, 0, 0.3]) cylinder(d = boss_d, h = boss_l);
        translate([boss_x - boss_d / 2, shelf_y(lip_t) - 14, lip_t]) cube([boss_d, 13, floor_t]);
    }
    yz_prism(boss_x - rib_t / 2, rib_t, [[plate_t - 0.01, floor_z - 0.01], [plate_t - 0.01, floor_z + rib_h],
                                         [shelf_y(lip_t) - 8, floor_z + rib_h], [shelf_y(lip_t) - 2, floor_z - 0.01]]);
}

// The U the cord follows, width w, in x-z
module cord_path(w) {
    x0 = cord_x; x1 = box_w - cord_x; z1 = cord_top; r = groove_r;
    translate([x0 - w / 2, cord_end]) square([w, z1 - cord_end - r]);
    translate([x1 - w / 2, cord_end]) square([w, z1 - cord_end - r]);
    translate([x0, cord_end]) circle(d = w);                  // round ends
    translate([x1, cord_end]) circle(d = w);
    translate([x0 + r, z1 - w / 2]) square([x1 - x0 - 2 * r, w]);
    for (c = [[x0 + r, z1 - r, 90], [x1 - r, z1 - r, 0]])
        translate([c[0], c[1]]) rotate(c[2]) intersection() {
            difference() { circle(r = r + w / 2); circle(r = r - w / 2); }
            square(r + w);
        }
}

// Pinch points: tabs left in both walls of the groove
module cord_pinches() {
    c = pinch_gap / 2;
    for (z = [cord_end + 6 : pinch_every : cord_top - groove_r - 2], x = [cord_x, box_w - cord_x])
        difference() {
            translate([x - groove_w, z - pinch_l / 2]) square([2 * groove_w, pinch_l]);
            translate([x - c, z - pinch_l]) square([2 * c, 2 * pinch_l]);
        }
    for (x = [cord_x + groove_r + 4 : pinch_every : box_w - cord_x - groove_r - 2])
        difference() {
            translate([x - pinch_l / 2, cord_top - groove_w]) square([pinch_l, 2 * groove_w]);
            translate([x - pinch_l, cord_top - c]) square([2 * pinch_l, 2 * c]);
        }
}

module groove() {
    translate([0, plate_t + 1, 0]) rotate([90, 0, 0]) linear_extrude(groove_d + 1)
        difference() { cord_path(groove_w); cord_pinches(); }
}

module base() {
    difference() {
        union() {
            plate();
            shelf();
            for (p = board_holes) translate([p[0], plate_t - 0.01, p[1]]) {
                along_y(standoff_d, standoff_h);
                rotate([-90, 0, 0]) cylinder(d1 = standoff_d + 2 * standoff_foot, d2 = standoff_d, h = standoff_foot);
            }
        }
        groove();
        mount_slots();
        for (p = board_holes) translate([p[0], plate_t - 1, p[1]]) along_y(standoff_hole, standoff_h + 2);
        translate([sp16_x, floor_y, lip_t - 1]) sp16_hole(floor_t + 2);
        translate([pg7_x, floor_y, lip_t - 1]) teardrop(pg7_d, floor_t + 2);
        translate([ant_x, floor_y, lip_t - 1]) teardrop(ant_d, floor_t + 2);
        translate([ant_x, floor_y, lip_t + ant_panel]) teardrop(ant_recess_d, floor_t);
        yz_prism(hook_x0 - 1, hook_w + 2, [[-1, plate_top - hook_c - 1], [hook_c + 1, plate_top + 1], [-1, plate_top + 1]]);
        at_screw() cylinder(d = m3_insert_d, h = m3_insert_len + 0.5);
    }
}

// ---- cover ---------------------------------------------------------------------------

// The outside: one form with the roof, the bevel, the corners and the back edge in it
module cover_outer() {
    module s(y, i = 0) { slice(y, cx0, bevel_z(y), cx1, roof_z(y), corner_r + wrap, foot_r, i); }
    hull() {
        s(0, edge_ch);
        s(edge_ch);
        s(bevel_o);
        for (t = [0 : 0.4 : blend_r]) s(cover_y1 - t, blend(t, blend_r));
    }
}

// The inside: the same form a wall thick, then the rim's opening, ramped so it prints.
// The sides ramp out straight behind the rim, which leaves the fittings the room
module cover_inner() {
    ri = blend_r - cover_wall;
    open_top = box_h - rim_top;
    y_rim = plate_t + rim_d;
    y_side = y_rim + rim_w + cover_fit;
    y_ramp = y_rim + (roof_z(plate_t) - cover_wall - open_top);
    ro = corner_r + wrap - cover_wall;
    module s(y, i = 0) {
        slice(y, ix0, max(lip_t, y + bevel_c), ix1, roof_z(y) - cover_wall, ro, 0.4, i);
    }
    module opening(y) { slice(y, rim_w, rim_z0, box_w - rim_w, open_top, open_r, open_r); }
    module sides() { slice(y_side, ix0, lip_t, ix1, open_top + y_side - y_rim, ro, 0.4); }
    hull() {
        s(y_ramp);
        s(lip_t - bevel_c);                       // where the bevel starts
        for (t = [0 : 0.4 : ri]) s(in_back - t, blend(t, ri));
    }
    hull() { sides(); s(y_ramp); }
    hull() { opening(y_rim); sides(); }
    hull() { opening(plate_t - 1); opening(y_rim); }   // through the rim
    yz_prism(ix0, ix1 - ix0,                      // round the shelf, below the rim, and down the bevel
             [[plate_t - 1, -1], [-1 - bevel_c, -1], [rim_z0 - bevel_c, rim_z0], [plate_t - 1, rim_z0]]);
}

// Behind the rim, all that is left is the skirt round the plate, notched for the ears
module skirt_cut() {
    z0 = mount_z[0] + ear_h / 2 + ear_fillet + skirt_end;           // below this there is none
    n0 = mount_z[1] - ear_h / 2 - ear_fillet - skirt_lift;
    n1 = mount_z[1] + ear_h / 2 + ear_fillet + skirt_end;
    translate([0, plate_t, 0]) rotate([90, 0, 0]) linear_extrude(plate_t + 5)
        offset(r = -1.5) offset(delta = 1.5) union() {              // the skirts' tips rounded
            prof(ix0, -5, ix1, plate_top + top_gap, corner_r + cover_fit, 0.4);
            translate([-30, -5]) square([box_w + 60, z0 + 5]);
            for (x = [-30, box_w]) translate([x, n0]) square([30, n1 - n0]);
        }
}

// The hook: hangs on the plate's chamfer, blended into the roof
module hook() {
    y1 = -hook_fit - hook_back;
    yz_prism(hook_x0, hook_w, [
        [hook_c - hook_fit + top_gap, plate_top + top_gap], [-hook_fit, plate_top - hook_c], [y1, plate_top - hook_c],
        [y1, roof_z(y1) - 1], [y1 + 1, roof_z(y1 + 1)], [edge_ch, roof_z(edge_ch)], [hook_c + 1, roof_z(hook_c + 1) - 1]]);
}

module cover() {
    difference() {
        union() {
            difference() { cover_outer(); cover_inner(); skirt_cut(); }
            hook();
        }
        at_screw() translate([0, 0, -bevel_t - 1]) cylinder(d = m3_clear, h = bevel_t + 2);
        at_screw() translate([0, 0, -bevel_t - 1]) cylinder(d = head_cb_d, h = head_cb_h + 1);
    }
}

// ---- small prints ----------------------------------------------------------------------

module spacer() {                                  // printed rain-gap spacer, 4 per tree
    ch = 0.6;
    difference() {
        union() {
            cylinder(d1 = spacer_d - 2 * ch, d2 = spacer_d, h = ch);
            translate([0, 0, ch]) cylinder(d = spacer_d, h = spacer_l - 2 * ch);
            translate([0, 0, spacer_l - ch]) cylinder(d1 = spacer_d, d2 = spacer_d - 2 * ch, h = ch);
        }
        translate([0, 0, -1]) cylinder(d = mount_slot_d, h = spacer_l + 2);
    }
}

// Fit coupon: the holes in a short flat print. A shelf strip with the SP16 D hole, the
// PG7 hole and the RP-SMA hole in its thinned recess; an 8mm block with an M3 insert
// hole; a board standoff.
module coupon() {
    l = 76; w = 30;
    difference() {
        union() {
            cube([l, w, floor_t]);
            translate([50, w - 8, 0]) cube([12, 8, 12]);
            translate([68, 8, 0]) cylinder(d = standoff_d, h = floor_t + standoff_h);
        }
        translate([14, 13, -1]) sp16_hole(floor_t + 2);
        translate([38, 13, -1]) cylinder(d = pg7_d, h = floor_t + 2);
        translate([56, 11, -1]) cylinder(d = ant_d, h = floor_t + 2);
        translate([56, 11, ant_panel]) cylinder(d = ant_recess_d, h = floor_t);
        translate([56, w + 0.01, 7]) rotate([90, 0, 0]) cylinder(d = m3_insert_d, h = m3_insert_len);
        translate([68, 8, floor_t]) cylinder(d = standoff_hole, h = standoff_h + 1);
    }
}

// Seal test: a strip of plate with the groove, its pinch points and the hook's chamfer,
// and a bar of cover rim with its wall and hook. Hook it on, swing it in and pull the far
// end down with one M3 into an insert, 90mm from the hook like the real cover. Slide
// paper into the joint along the bar: it should drag all the way. If the middle gaps, the
// cover's rim needs stiffening before printing a whole one.
st_l = 100; st_w = 24; st_bar = cover_wall + 6;
module seal_test() {
    c = pinch_gap / 2;
    difference() {
        cube([st_l, st_w, plate_t]);
        translate([0, 0, plate_t - groove_d]) linear_extrude(groove_d + 1) difference() {
            translate([14, st_w / 2 - groove_w / 2]) square([st_l - 26, groove_w]);
            for (x = [20 : pinch_every : st_l - 16]) difference() {
                translate([x - pinch_l / 2, 0]) square([pinch_l, st_w]);
                translate([x - pinch_l, st_w / 2 - c]) square([2 * pinch_l, 2 * c]);
            }
        }
        translate([0, st_w + 1, 0]) rotate([90, 0, 0]) linear_extrude(st_w + 2)
            polygon([[-1, -1], [hook_c + 1, -1], [-1, hook_c + 1]]);
        translate([st_l - 6, st_w / 2, plate_t + 0.01 - m3_insert_len]) cylinder(d = m3_insert_d, h = m3_insert_len);
    }
    translate([0, st_w + 10, 0]) difference() {
        union() {
            translate([-top_gap, 0, 0]) cube([st_l + top_gap, st_w, st_bar]);      // as stiff as the cover's wall and rim
            top = st_bar + plate_t;                                // the strip's tree face, once hooked on
            translate([0, st_w, 0]) rotate([90, 0, 0]) linear_extrude(st_w)
                polygon([[-top_gap - cover_wall, 0], [-top_gap, 0], [-top_gap, top - hook_c + hook_fit - top_gap],
                         [hook_c, top + hook_fit], [hook_c, top + hook_fit + hook_back],
                         [-top_gap - cover_wall, top + hook_fit + hook_back]]);
        }
        translate([st_l - 6, st_w / 2, -1]) cylinder(d = m3_clear, h = st_bar + 2);
    }
}

// ---- output ------------------------------------------------------------------------------

module tree_box_assembly() {
    color("SteelBlue") base();
    color("LightSteelBlue", 0.6) cover();
}

// Old module names, for the parked boot (feet/)
module box() { cover(); }
module lid() { base(); }

if (part == "base") rotate([90, 0, 0]) base();                                  // tree face on the bed
else if (part == "cover") translate([0, 0, cover_y1]) rotate([-90, 0, 0]) cover(); // back on the bed
else if (part == "base-fitted") base();
else if (part == "cover-fitted") cover();
else if (part == "coupon") coupon();
else if (part == "seal-test") seal_test();
else if (part == "spacer") spacer();
else if (part == "assembly") tree_box_assembly();
