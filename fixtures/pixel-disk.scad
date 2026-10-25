// Printed retaining disk for the 12mm bullet pixels (Ray Wu: body 12, front flange 13.6,
// dome 8, 30mm body behind the flange, side clips that grip a 2mm-thick panel).
// Each tree hole is cut from the front only: a 19 x 2mm counterbore, then a 15mm
// clearance hole through the 30mm oak. This disk sits flush in the counterbore (hot glue,
// or CA/epoxy); the bullet pushes in from the front, its flange rests on the disk and the
// clips snap behind it into the clearance hole. The disk's bore sets the fit.
//
// Prints flat, front face on the bed (smooth face under the flange), no supports.
// The 0.4mm chamfer is on the back edge of the bore (the top as printed), to lead the clips.
// PETG, 100% infill (or 4+ walls: it's only 2mm thick). A tree needs 92.
//
// Print the test strip first (bores 11.8 to 12.2, labelled on snap-off tabs); put the
// chosen bore in tools/tree_layout.py Params.hole_dia and in `bore` below.

part = "disk";           // "disk", "plate" (5 x 4 = 20) or "test" (5 bores, labelled)

disk_od   = 18.5;        // in a 19mm counterbore: 0.25mm glue gap all round
disk_t    = 2.0;         // = the clip gap; must match the counterbore depth
bore      = 12.0;        // pixel body 12: set from the test strip
chamfer   = 0.4;         // back edge of the bore, leads the clips through
notches   = 3;           // glue notches on the OD (0 for none)
notch_w   = 1.0;
notch_d   = 0.5;

plate_nx  = 5;
plate_ny  = 4;
gap       = 2;           // between disks on the plate

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

module disk(b = bore) {
    difference() {
        cylinder(d = disk_od, h = disk_t);
        translate([0, 0, -1]) cylinder(d = b, h = disk_t + 2);
        // back-edge chamfer (top as printed)
        translate([0, 0, disk_t - chamfer]) cylinder(d1 = b, d2 = b + 2 * chamfer + 0.02, h = chamfer + 0.01);
        // glue notches through the full thickness
        for (i = [0 : notches - 1]) if (notches > 0)
            rotate(i * 360 / notches + 90)
                translate([disk_od / 2 - notch_d, -notch_w / 2, -1]) cube([notch_d + 1, notch_w, disk_t + 2]);
    }
}

module plate() {
    p = disk_od + gap;
    for (i = [0 : plate_nx - 1], j = [0 : plate_ny - 1])
        translate([i * p, j * p, 0]) disk();
}

module test_strip() {
    n = len(test_bores);
    p = disk_od + test_gap;
    for (i = [0 : n - 1]) translate([i * p, 0, 0]) {
        disk(test_bores[i]);
        // label tab below the disk, on a thin snap-off neck
        translate([-bridge_w / 2, -disk_od / 2 - neck_l - 0.3, 0]) cube([bridge_w, neck_l + 0.6, bridge_t]);
        translate([-tab_l / 2, -disk_od / 2 - neck_l - tab_w, 0]) {
            cube([tab_l, tab_w, tab_t]);
            translate([tab_l / 2, tab_w / 2, tab_t - 0.01])
                linear_extrude(text_h + 0.01)
                    text(str(test_bores[i]), size = text_size, font = font, halign = "center", valign = "center");
        }
    }
    // snap-off bridges between neighbouring disks (on the centreline, clear of the notches)
    for (i = [0 : n - 2])
        translate([i * p + disk_od / 2 - 0.3, -bridge_w / 2, 0]) cube([test_gap + 0.6, bridge_w, bridge_t]);
}

if (part == "plate") plate();
else if (part == "test") test_strip();
else disk();
