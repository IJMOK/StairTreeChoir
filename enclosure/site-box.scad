// Site box (M3): the show player and the 12V distribution for one site.
// An upright wall box: lid on the front, every cable through the floor, so it sheds
// rain. Screw it to a post or fence (lugs top and bottom), under some cover if you can.
//
// Inside, on the back wall: the Pi (standoffs on the Raspberry Pi 58 x 49mm M2.5
// pattern, Pi 3 and Pi 5 alike), and a grid of zip-tie anchors for everything whose
// size isn't confirmed yet: GL.iNet router, 12V->5V buck, PAM8610, USB sound card,
// and per PSU a pair of Wago 221-413s and its inline blade fuse holders.
//
// Wiring (electronics/site-wiring.md): the Mean Well PSUs stand OUTSIDE, one per pair
// of trees; mains never enters this box. Each PSU's 12V comes in on its own gland
// and feeds only its own fuses (never parallel two PSUs). PSU 1 also feeds the
// player through a 3A fuse. One gland out per tree, one for the speaker.
//
// Floor glands, left to right: PSU inputs, tree runs, speaker (PG7). Unused tree
// holes for smaller sites: export with trees = 4 or 2.
//
// Printing (P1S, 255mm bed): box on its back, open side up, no supports; lid flat,
// groove up. Outside 236 x 196mm. Lid sealed with 2.7mm rubber cord (seal.scad).
//
// UNVERIFIED: PG9/PG7 thread sizes, M3 insert hole, that everything fits the
// 64mm depth with the router on its side. Lay the real parts out on the back wall
// before printing.

include <seal.scad>

part   = "assembly";     // "box", "lid", "assembly"
trees  = 6;              // glands for this many tree runs (6, 4 or 2)
psus   = ceil(trees / 2);

in_w     = 230;          // inside, across
in_h     = 190;          // inside, up
in_d     = 64;           // inside, back wall to rim
wall     = 3;
rim      = 12;           // rim width at the lid face: lid screws, then the cord groove
gasket_t = 0;            // cord in the lid groove; lid lands on the rim
lid_t    = 4;
groove_in = 8;           // cord groove centreline from the outer edges

pg9_d    = 15.6;
pg7_d    = 12.9;
gland_pitch = 25;        // PG9 locknut is ~22mm across corners
drip_d   = 3;

pi_holes = [[0, 0], [58, 0], [0, 49], [58, 49]];   // Raspberry Pi mounting holes, M2.5
pi_at    = [12, in_h - 12 - 49 - 3.5];              // first hole, from the inside bottom-left
standoff_h = 6;

anchor_pitch = 30;       // zip-tie anchors on the back wall
anchor_slot  = [5, 2.2]; // tie width x thickness it takes

m3_clear = 3.4;
m3_insert_d = 4.0;
m3_insert_len = 6;
screw_in = 3.5;          // lid screw centres from the outer edges
boss_d   = 7;
boss_len = 12;
skirt_t  = 1.6;
skirt_gap = 0.4;
skirt_len = gasket_t + 3;
lug_w    = 30;
lug_t    = 5;
lug_hole = 5;            // for a 4.5mm screw into the post

$fn = 40;

W = in_w + 2 * wall;
H = in_h + 2 * wall;
D = wall + in_d;          // back face to rim face
lid_screws = [for (x = [screw_in, W / 2, W - screw_in]) for (z = [screw_in, H - screw_in]) [x, z]];
side_screws = [for (x = [screw_in, W - screw_in]) [x, H / 2]];
all_screws = concat(lid_screws, side_screws);

// Box coordinates: x across, z up (as fitted), y from the back face (0) to the rim (D).
module along_y(d, l) { rotate([-90, 0, 0]) cylinder(d = d, h = l); }

module cavity() {
    ledge = rim - wall;
    yl = D - 4;
    translate([wall, wall, wall]) cube([in_w, yl - ledge - wall, in_h]);
    hull() {
        translate([wall, yl - ledge - 0.01, wall]) cube([in_w, 0.01, in_h]);
        translate([wall + ledge, yl, wall + ledge]) cube([in_w - 2 * ledge, 0.01, in_h - 2 * ledge]);
    }
    translate([wall + ledge, yl, wall + ledge]) cube([in_w - 2 * ledge, 5, in_h - 2 * ledge]);
}

module zip_anchor() {        // a bridge on the back wall a cable tie threads under
    difference() {
        translate([-(anchor_slot[0] + 4) / 2, 0, -3]) cube([anchor_slot[0] + 4, anchor_slot[1] + 2, 6]);
        translate([-anchor_slot[0] / 2, -1, -4]) cube([anchor_slot[0], anchor_slot[1] + 1, 8]);
    }
}

function in_pi(x, z) = x > wall + pi_at[0] - 12 && x < wall + pi_at[0] + 58 + 12
                    && z > wall + pi_at[1] - 12 && z < wall + pi_at[1] + 49 + 12;

gland_list = concat([for (i = [0 : psus - 1]) pg9_d], [for (i = [0 : trees - 1]) pg9_d], [pg7_d]);
gland_rows = len(gland_list) * gland_pitch > in_w - 10 ? 2 : 1;

module box() {
    difference() {
        union() {
            difference() { cube([W, D, H]); cavity(); }
            for (s = all_screws) translate([s[0], D - boss_len, s[1]]) {
                along_y(boss_d, boss_len);
                translate([0, -boss_d / 2, 0]) rotate([-90, 0, 0]) cylinder(d1 = 0.1, d2 = boss_d, h = boss_d / 2);
            }
            for (h = pi_holes) translate([wall + pi_at[0] + h[0], wall - 0.01, wall + pi_at[1] + h[1]]) along_y(6, standoff_h);
            for (x = [wall + 15 : anchor_pitch : W - wall - 10]) for (z = [wall + 40 : anchor_pitch : H - wall - 10])
                if (!in_pi(x, z)) translate([x, wall - 0.01, z]) zip_anchor();
            // wall-mounting lugs on the back, top and bottom
            for (z = [-lug_w * 0.6, H]) translate([W / 2 - lug_w / 2, 0, z]) cube([lug_w, lug_t, lug_w * 0.6]);
        }
        for (s = all_screws) translate([s[0], D - m3_insert_len, s[1]]) along_y(m3_insert_d, m3_insert_len + 1);
        for (h = pi_holes) translate([wall + pi_at[0] + h[0], wall - 1, wall + pi_at[1] + h[1]]) along_y(2.2, standoff_h + 1);
        for (z = [-lug_w * 0.3, H + lug_w * 0.3]) translate([W / 2, -1, z]) along_y(lug_hole, lug_t + 2);
        // floor glands, in one or two rows
        for (i = [0 : len(gland_list) - 1]) {
            per_row = ceil(len(gland_list) / gland_rows);
            r = floor(i / per_row); c = i % per_row;
            x = W / 2 + (c - (per_row - 1) / 2) * gland_pitch;
            y = wall + (gland_rows == 1 ? in_d / 2 : (r == 0 ? in_d * 0.3 : in_d * 0.72));
            translate([x, y, -1]) cylinder(d = gland_list[i], h = wall + 2);
        }
        translate([wall + 6, wall + in_d / 2, -1]) cylinder(d = drip_d, h = wall + 2);
    }
}

module lid() {               // flat on the bed, outer face down; x across, y = box z
    o = skirt_gap + skirt_t;
    difference() {
        union() {
            cube([W, H, lid_t]);
            difference() {
                translate([-o, -o, 0]) cube([W + 2 * o, H + 2 * o, lid_t + skirt_len]);
                translate([-skirt_gap, -skirt_gap, lid_t]) cube([W + 2 * skirt_gap, H + 2 * skirt_gap, skirt_len + 1]);
            }
        }
        for (s = all_screws) translate([s[0], s[1], -1]) cylinder(d = m3_clear, h = lid_t + 2);
        translate([0, 0, lid_t - groove_d]) cord_groove(W, H, groove_in);
    }
}

if (part == "box") rotate([90, 0, 0]) box();   // back face on the bed, open side up
else if (part == "lid") lid();
else {
    color("SteelBlue") box();
    color("LightSteelBlue", 0.5) translate([0, D + gasket_t + lid_t, 0]) rotate([90, 0, 0]) lid();
}
