// Tree controller box (M3), base + cover (Rob, 28 Oct 2026). PETG.
//
// Base: an L. The tree plate (y = 0 face against the spacers on the back of the tree)
// with a flange down each side, two slots each, and a shelf along its bottom. It
// carries everything, so it is all built and wired on the bench: the controller board
// on four standoffs on the plate, the Mini560 standing on the board, the Wagos on the
// shelf, and in the shelf floor the SP16 panel socket (12V run, firing down) and the
// PG7 gland (pixel lead). Round the plate and the shelf runs the plug, a rim 16mm deep
// that the cover slides over, with one continuous cord groove on its outside.
//
// Cover: back, sides and a roof sloping 8 degrees away from the tree, open at the
// front and the bottom. It slides on from behind; the 2.7mm cord in the plug's groove
// seals against its walls (radial squeeze, so the screws only hold it, they don't
// clamp the seal). Four M3 screws through its sides into heat-set inserts in the plug,
// on the outside of the seal. The RP-SMA antenna bulkhead is in its outer side wall
// (x = 0, away from the tree's centre): leave the U.FL pigtail long enough to lift
// the cover off.
//
// Printing, no supports: base with the tree face on the bed; cover with its back on
// the bed.
//
// UNVERIFIED until the parts arrive: board hole positions (pb_*), the SP16 nut and
// thread length, the gland and bulkhead sizes; the seal's squeeze (print seal-test).
// Shared sizes are in tree-box-params.scad; tools/gen_components.py checks the parts fit.

include <tree-box-params.scad>
include <seal.scad>

part = "assembly";       // "base", "cover", "coupon", "seal-test", "spacer", "assembly";
                         // "base-fitted", "cover-fitted": as fitted (STEP export)

// Board: 5x7cm prototype board on the plate, M2 screws into the standoffs
pb_w          = 70;
pb_h          = 50;
pb_hole_in    = 2.5;     // hole centres from the board edges
standoff_h    = 5;       // room for the underside joins
standoff_d    = 6;
standoff_hole = 1.8;     // M2 self-tapping

// Shelf floor entries
sp16_d        = 16.7;    // SP16 panel socket, M16x1.5: drawing hole 16.5 ...
sp16_flat     = 15.4;    // ... with one flat, 15.3 from the far side (stops it turning)
pg7_d         = 12.9;    // PG7 thread 12.5
floor_y       = plate_t + 14;      // their centres: nuts (up to ~25 across corners) clear of the plate and the shelf rim
sp16_x        = plug_x0 + plug_t + 14;
pg7_x         = plug_x0 + plug_t + box_in_w - 18;
drip_d        = 3;

// Cord groove round the plug: on the plate's rim this far back from the plate, on
// the shelf's rim this high above the underside; the two join down each side in an
// 8mm bend (>= 3 x the cord, so it doesn't kink)
groove_y      = plate_t + 12;
groove_z      = 12;
groove_bend   = 8;

// Cover screws (M3 x 10 button head): through the cover's sides into inserts in the
// plug, on the outside of the seal: one in the plate's rim, one in the shelf's rim
cover_screws  = [[plate_t + 5, plug_top - 20], [plug_back - 14, 5]];   // [y, z]
lead_in       = 1;       // chamfer inside the cover's mouth, so it slides over the cord

// Antenna: RP-SMA bulkhead in the cover's outer side wall, behind the plate's rim
ant_d         = 6.6;     // 1/4"-36
ant_y         = plate_t + plug_d + 10;
ant_z         = box_h - 22;

// Mounting on the back of the tree
flange_w      = 13;      // beyond each side of the cover
flange_r      = 6;
mount_slot_d  = 4.6;     // 4mm stainless wood screws (4 x 40 pan head + washer)
mount_slot_l  = 6;       // slot travel, up and down
mount_z       = [14, box_h - 16];
spacer_d      = 10;
spacer_l      = 10;      // rain gap between the oak and the box

// Roof
roof_slope    = 8;       // degrees, down away from the tree
roof_back     = 1;       // roof thickness above box_h at the back edge
bed_ch        = 0.6;     // chamfer on the bed edges (elephant's foot)
edge_ch       = 0.8;

$fn = 48;

board_x0 = plug_x0 + plug_t + (box_in_w - pb_w) / 2;
board_z0 = plug_top - plug_t - 2 - pb_h;
board_holes = [
    for (x = [pb_hole_in, pb_w - pb_hole_in])
        for (z = [pb_hole_in, pb_h - pb_hole_in]) [board_x0 + x, board_z0 + z]
];

assert(floor_y - 12.7 >= plate_t && floor_y + 12.7 <= plug_back - plug_t,
       "floor nuts reach the plate or the shelf rim: move floor_y or deepen the box");
assert(board_z0 > floor_t + 20, "board too low: the SP16 body stands ~19mm off the floor");

// ---- shapes ------------------------------------------------------------------------

// Rounded top corners in x-z (u = x, v = z), square bottom
module top_round(w, h, r) {
    hull() {
        square([w, h - r]);
        translate([r, h - r]) circle(r = r);
        translate([w - r, h - r]) circle(r = r);
    }
}

// Rounded back corners in x-y (u = x, v = y), square front
module back_round(w, d, r) { top_round(w, d, r); }

// x-z profile extruded along +y from y0 to y0 + d
module xz_box(x0, y0, w, h, d, r, z0 = 0) {
    translate([x0, y0 + d, z0]) rotate([90, 0, 0]) linear_extrude(d) top_round(w, h, r);
}

// x-y profile extruded along +z from z0 to z0 + h
module xy_box(x0, y0, w, d, h, r, z0 = 0) {
    translate([x0, y0, z0]) linear_extrude(h) back_round(w, d, r);
}

module along_y(d, l) { rotate([-90, 0, 0]) cylinder(d = d, h = l); }
module along_x(d, l) { rotate([0, 90, 0]) cylinder(d = d, h = l); }

module sp16_hole(h) {     // D hole along z; the flat towards the back (+y): the top when the base prints
    intersection() {
        cylinder(d = sp16_d, h = h);
        translate([-sp16_d / 2, -sp16_d / 2, 0]) cube([sp16_d, sp16_flat, h]);
    }
}

// ---- base ----------------------------------------------------------------------------

// The plug's outer envelope (solid), grown by g on its sealing faces (sides, top, back)
module plug_env(g = 0) {
    union() {
        xz_box(plug_x0 - g, plate_t - 0.01, plug_w + 2 * g, plug_top + g, plug_d + 0.01, plug_r + g);
        xy_box(plug_x0 - g, plate_t - 0.01, plug_w + 2 * g, plug_back + g - plate_t + 0.01, plug_d, plug_r + g);
    }
}

module plug() {
    difference() {
        plug_env();
        translate([plug_x0 + plug_t, plate_t - 1, floor_t])
            cube([box_in_w, plug_back - plug_t - plate_t + 1, plug_top - plug_t - floor_t]);
    }
}

// One continuous groove: the skin of the plug's sealing faces, where it crosses the path
module groove() {
    w = groove_w; c = [groove_y + groove_bend, groove_z + groove_bend];   // bend centre, (y, z)
    intersection() {
        difference() { plug_env(0.01); plug_env(-groove_d); }
        union() {
            translate([-50, groove_y - w / 2, c[1]]) cube([box_w + 100, w, 200]);       // plate rim
            translate([-50, c[0], groove_z - w / 2]) cube([box_w + 100, 200, w]);       // shelf rim
            translate([-50, c[0], c[1]]) rotate([0, 90, 0]) linear_extrude(box_w + 100)  // the bends
                intersection() {
                    difference() { circle(r = groove_bend + w / 2); circle(r = groove_bend - w / 2); }
                    translate([0, -groove_bend - w]) square(groove_bend + w);
                }
        }
    }
}

// Tree plate with its flanges, tree face on the bed, edge chamfered
module plate() {
    W = box_w + 2 * flange_w;
    translate([-flange_w, 0, 0]) hull() {
        translate([0, bed_ch, 0]) rotate([90, 0, 0]) linear_extrude(0.01)
            offset(delta = -bed_ch) offset(r = flange_r) offset(delta = -flange_r) square([W, box_h]);
        translate([0, plate_t, 0]) rotate([90, 0, 0]) linear_extrude(plate_t - bed_ch)
            offset(r = flange_r) offset(delta = -flange_r) square([W, box_h]);
    }
}

module mount_slots() {
    for (x = [-flange_w / 2, box_w + flange_w / 2]) for (z = mount_z)
        hull() for (dz = [-mount_slot_l / 2, mount_slot_l / 2])
            translate([x, -1, z + dz]) along_y(mount_slot_d, plate_t + 2);
}

module base() {
    difference() {
        union() {
            plate();
            plug();
            for (p = board_holes) translate([p[0], plate_t - 0.01, p[1]]) along_y(standoff_d, standoff_h);
        }
        groove();
        mount_slots();
        for (p = board_holes) translate([p[0], plate_t - 1, p[1]]) along_y(standoff_hole, standoff_h + 2);
        translate([sp16_x, floor_y, -1]) sp16_hole(floor_t + 2);
        translate([pg7_x, floor_y, -1]) cylinder(d = pg7_d, h = floor_t + 2);
        translate([box_w / 2, plug_back - plug_t - 3, -1]) cylinder(d = drip_d, h = floor_t + 2);
        for (s = cover_screws, side = [0, 1])                                  // inserts, from each side
            translate([side == 0 ? plug_x0 - 0.01 : plug_x0 + plug_w + 0.01, s[0], s[1]])
                rotate([0, side == 0 ? 90 : -90, 0]) cylinder(d = m3_insert_d, h = m3_insert_len);
    }
}

// ---- cover ---------------------------------------------------------------------------

module cover_outline(x0, y0, w, d, h, r, z0 = 0) {
    intersection() {
        xz_box(x0, y0, w, h, d, r, z0);
        xy_box(x0, y0, w, d, h + 100, r, z0);
    }
}

// Roof wedge, high at the tree: its sides run flush out of the walls and keep the
// corner radius all along the slope; rounded at the back corners like the cover
module roof() {
    d = cover_y1 - plate_t;
    top0 = box_h + roof_back + d * tan(roof_slope);
    top1 = box_h + roof_back;
    zb = box_h - corner_r;
    module slice(y, top, inset) {
        translate([0, y + 0.01, zb]) rotate([90, 0, 0]) linear_extrude(0.01)
            offset(delta = -inset) top_round(box_w, top - zb, corner_r);
    }
    intersection() {
        hull() {
            slice(plate_t, top0, 0);
            slice(cover_y1 - edge_ch, top1 + edge_ch * tan(roof_slope), 0);
            slice(cover_y1 - 0.01, top1, edge_ch);
        }
        xy_box(0, plate_t, box_w, d, 200, corner_r);
    }
}

module cover() {
    ci = cover_wall;
    cavity_d = cover_y1 - cover_back_t - plate_t;
    difference() {
        union() {
            cover_outline(0, plate_t, box_w, cover_y1 - plate_t, box_h, corner_r);
            roof();
        }
        // inside: the plug grown by the fit, open at the front and the bottom
        cover_outline(ci, plate_t - 1, box_w - 2 * ci, cavity_d + 1, box_h - ci + 1, corner_r - ci, -1);
        // lead-in chamfers round the mouth: front edge and bottom edge
        hull() {
            cover_outline(ci - lead_in, plate_t - 0.01, box_w - 2 * (ci - lead_in), 0.01,
                          box_h - ci + lead_in + 1, corner_r - ci + lead_in, -1);
            cover_outline(ci, plate_t + lead_in, box_w - 2 * ci, 0.01, box_h - ci + 1, corner_r - ci, -1);
        }
        hull() {
            translate([0, 0, -0.01]) linear_extrude(0.01)
                translate([ci - lead_in, plate_t - 1]) back_round(box_w - 2 * (ci - lead_in), cavity_d + 1 + lead_in, corner_r - ci + lead_in);
            translate([0, 0, lead_in]) linear_extrude(0.01)
                translate([ci, plate_t - 1]) back_round(box_w - 2 * ci, cavity_d + 1, corner_r - ci);
        }
        for (s = cover_screws) translate([-1, s[0], s[1]]) along_x(m3_clear, box_w + 2);
        translate([-1, ant_y, ant_z]) along_x(ant_d, ci + 2);
    }
}

// ---- small prints ----------------------------------------------------------------------

module spacer() {                                  // printed rain-gap spacer, 4 per tree
    difference() {
        cylinder(d = spacer_d, h = spacer_l);
        translate([0, 0, -1]) cylinder(d = mount_slot_d, h = spacer_l + 2);
    }
}

// Fit coupon: the holes in a short flat print. A 3.5mm floor strip with the SP16 D hole,
// the PG7 hole and the drip hole; a 2.4mm fin with the RP-SMA hole; an 8mm block with
// an M3 insert hole (as in the plug's walls); a board standoff.
module coupon() {
    l = 76; w = 30; fin_h = 18;
    difference() {
        union() {
            cube([l, w, floor_t]);
            translate([0, w - cover_wall, 0]) cube([30, cover_wall, fin_h]);
            translate([40, w - plug_t, 0]) cube([12, plug_t, 12]);
            translate([66, w - standoff_d / 2 - 2, 0]) cylinder(d = standoff_d, h = floor_t + standoff_h);
        }
        translate([14, 13, -1]) sp16_hole(floor_t + 2);
        translate([38 - 6, 11, -1]) cylinder(d = pg7_d, h = floor_t + 2);
        translate([58, 8, -1]) cylinder(d = drip_d, h = floor_t + 2);
        translate([15, w - cover_wall - 1, floor_t + 7]) along_y(ant_d, cover_wall + 2);
        translate([46, w + 0.01, 7]) rotate([90, 0, 0]) cylinder(d = m3_insert_d, h = m3_insert_len);
        translate([66, w - standoff_d / 2 - 2, floor_t]) cylinder(d = standoff_hole, h = standoff_h + 1);
    }
}

// Seal test: a short plug with the groove and the corner radius, and a sleeve of the
// cover's wall and fit, with its lead-in. Cord in, slide the sleeve on: it should go
// on firmly by hand and not rock. Both print standing on their flat ends.
st_w = 50; st_h = 30; st_d = 20;
module st_shape(w, h, r, l) { linear_extrude(l) offset(r = r) offset(delta = -r) square([w, h]); }
module seal_test() {
    difference() {                                          // plug with a floor
        st_shape(st_w, st_h, plug_r, st_d);
        translate([plug_t, plug_t, 3]) st_shape(st_w - 2 * plug_t, st_h - 2 * plug_t, 1, st_d);
        intersection() {
            difference() {
                translate([-0.01, -0.01, 0]) st_shape(st_w + 0.02, st_h + 0.02, plug_r, st_d + 1);
                translate([groove_d, groove_d, -1]) st_shape(st_w - 2 * groove_d, st_h - 2 * groove_d, plug_r - groove_d, st_d + 3);
            }
            translate([-10, -10, 12 - groove_w / 2]) cube([st_w + 20, st_h + 20, groove_w]);
        }
    }
    f = cover_fit; ci = cover_wall;
    translate([st_w + 15, 0, 0]) difference() {             // sleeve
        translate([-f - ci, -f - ci, 0]) st_shape(st_w + 2 * (f + ci), st_h + 2 * (f + ci), plug_r + f + ci, st_d);
        translate([-f, -f, -1]) st_shape(st_w + 2 * f, st_h + 2 * f, plug_r + f, st_d + 2);
        hull() {
            translate([-f - lead_in, -f - lead_in, -0.01]) st_shape(st_w + 2 * (f + lead_in), st_h + 2 * (f + lead_in), plug_r + f + lead_in, 0.01);
            translate([-f, -f, lead_in]) st_shape(st_w + 2 * f, st_h + 2 * f, plug_r + f, 0.01);
        }
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
