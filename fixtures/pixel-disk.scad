// Printed retaining disk for the 12mm bullet pixels (Ray Wu: body 12, front flange 13.6,
// dome 8, 30mm body behind the flange, side clips that grip a 2mm-thick panel).
// Each tree hole is cut from the front only: a 19 x 6mm counterbore, then a 15mm
// clearance hole through the 30mm oak. This disk sits flush in the counterbore; the bullet
// pushes in from the front, its flange rests on the disk and the clips snap behind the 2mm
// front lip into the relief. The lip's bore sets the pixel fit.
//
// Friction fit (Rob, 13 Nov 2026): the varnished counterbores measure 18.3-18.6 across and
// 4.9 deep (varnish pools in the bottom). The disk is a core that clears the smallest hole
// with crush ribs that shave down on press-in, 4.8 thick, with a chamfer on its back
// outer edge to clear the varnish fillet in the corner and lead it in. The ribs taper over
// rib_lead at the back end so they start straight.
//
// Prints flat, front face on the bed (smooth face under the flange), no supports: the
// relief opens upwards from the lip. The 0.4mm chamfer is on the back edge of the bore
// (the lip's top as printed), to lead the clips.
// PETG, 100% infill (or 4+ walls). A tree needs 92.
//
// Test strips: part = "test" varies the rib diameter (fit in the counterbore, bore fixed),
// part = "bore-test" varies the bore (fit of the pixel, ribs fixed). Put the chosen values
// in rib_od / bore below, and the bore in tools/tree_layout.py Params.hole_dia.

part = "disk";           // "disk", "plate" (5 x 4 = 20), "test" (5 rib sizes) or "bore-test" (5 bores)

core_od   = 18.0;        // clears the smallest varnished counterbore (18.3) by 0.15 a side
rib_od    = 19.3;        // over the rib tips, as drawn: a solid fit from the rib test strip
                         // (Rob, 13 Nov 2026; 18.8 drawn printed 18.64 and was too loose)
ribs      = 8;
rib_w     = 1.2;         // at the root
rib_tip_w = 0.5;         // flat on the tip: at least a nozzle width, or the slicer rounds it off
rib_lead  = 1.2;         // ribs taper to nothing over this at the back (goes in first)
disk_t    = 4.8;         // varnished counterbore is 4.9 deep: flush, 0.1 to spare
back_ch   = 0.7;         // back outer edge: clears the varnish fillet in the corner
lip_t     = 2.0;         // = the clip gap: the clips snap behind this
relief_d  = 15.0;        // behind the lip, room for the clips to spring out (= clearance_dia)
bore      = 12.0;        // pixel body 12: good fit on the first print (Rob, 13 Nov 2026)
chamfer   = 0.4;         // back edge of the bore, leads the clips through

plate_nx  = 5;
plate_ny  = 4;
gap       = 2;           // between disks on the plate

test_ribs  = [18.9, 19.0, 19.1, 19.2, 19.3];
test_bores = [11.8, 11.9, 12.0, 12.1, 12.2];
test_gap  = 3;           // between disks on the test strip
bridge_w  = 1.2;         // snap-off bridges and tab necks
bridge_t  = 0.6;         //   (3 layers at 0.2: bend them and they break)
tab_l     = 11;          // label tab under each disk
tab_w     = 6;
tab_t     = 1.0;
neck_l    = 2;           // disk edge to tab
text_size = 3.2;
text_h    = 0.6;         // embossed on the tab
font      = "Liberation Sans:style=Bold";

$fn = 128;               // round bore: ~0.3mm facets on a 12mm hole

// one rib's cross-section, root buried 0.1 in the core, tip at radius r
module rib_profile(r) {
    r0 = core_od / 2 - 0.1;
    polygon([[r0, -rib_w / 2], [r, -rib_tip_w / 2], [r, rib_tip_w / 2], [r0, rib_w / 2]]);
}

module rib(r_tip) {
    hull() {
        linear_extrude(disk_t - rib_lead) rib_profile(r_tip);
        // at the back face the tip meets the chamfered core edge
        translate([0, 0, disk_t - 0.01]) linear_extrude(0.01) rib_profile(core_od / 2 - back_ch + 0.05);
    }
}

module disk(b = bore, r_od = rib_od) {
    difference() {
        union() {
            cylinder(d = core_od, h = disk_t - back_ch);
            translate([0, 0, disk_t - back_ch - 0.001])
                cylinder(d1 = core_od, d2 = core_od - 2 * back_ch, h = back_ch + 0.001);
            for (i = [0 : ribs - 1]) rotate(i * 360 / ribs) rib(r_od / 2);
        }
        translate([0, 0, -1]) cylinder(d = b, h = disk_t + 2);
        translate([0, 0, lip_t]) cylinder(d = relief_d, h = disk_t);
        // back-edge chamfer of the lip (top as printed)
        translate([0, 0, lip_t - chamfer]) cylinder(d1 = b, d2 = b + 2 * chamfer + 0.02, h = chamfer + 0.01);
    }
}

module plate() {
    p = rib_od + gap;
    for (i = [0 : plate_nx - 1], j = [0 : plate_ny - 1])
        translate([i * p, j * p, 0]) disk();
}

// a snap-off strip of test disks: disk i has bore bores[i], rib diameter rods[i], label labels[i]
module strip(labels, bores, rods) {
    n = len(labels);
    p = max(rods) + test_gap;
    for (i = [0 : n - 1]) translate([i * p, 0, 0]) {
        rotate(360 / ribs / 2) disk(bores[i], rods[i]);   // ribs off the bridge/tab line
        // label tab below the disk, on a thin snap-off neck
        translate([-bridge_w / 2, -core_od / 2 - neck_l - 0.3, 0]) cube([bridge_w, neck_l + 0.6, bridge_t]);
        translate([-tab_l / 2, -core_od / 2 - neck_l - tab_w, 0]) {
            cube([tab_l, tab_w, tab_t]);
            translate([tab_l / 2, tab_w / 2, tab_t - 0.01])
                linear_extrude(text_h + 0.01)
                    text(str(labels[i]), size = text_size, font = font, halign = "center", valign = "center");
        }
    }
    // snap-off bridges between neighbouring disks (on the centreline, between ribs)
    for (i = [0 : n - 2])
        translate([i * p + core_od / 2 - 0.3, -bridge_w / 2, 0]) cube([p - core_od + 0.6, bridge_w, bridge_t]);
}

if (part == "plate") plate();
else if (part == "test") strip(test_ribs, [for (r = test_ribs) bore], test_ribs);
else if (part == "bore-test") strip(test_bores, test_bores, [for (b = test_bores) rib_od]);
else disk();
