// Printed hold-down clamp for the CNC bed's channel-strut rails (41mm strut, ~180mm
// centres; one tree per setup, two to four clamps). The bolt goes into a strut
// spring/channel nut.
// A bar with a nose that presses on the tread's edge and a heel that rests on the bed;
// the M6 bolt goes through the slot between them, nearer the nose so most of the force
// lands on the work. PETG, printed on its side (slot vertical) so the layers run along
// the bar and don't split under the bolt.
//
// Rob's bed (23 Oct 2026): MDF topper with the strut set in grooves, strut top ~4mm
// below the topper; M6 bolts into strut channel nuts. The tread sits on a sacrificial
// sheet (the holes go through), the heel stands on the topper beside it.
// Bolt length: printed with the clamp's console echo (M6 x that, or the next size up).

part = "clamp";          // "clamp" or "washer"

bolt_d     = 6.5;        // M6 clearance
tree_t     = 30;         // tread
spoil_t    = 6;          // sacrificial sheet under the tread (set to yours)
strut_drop = 4;          // strut top below the topper
nut_t      = 6;          // channel nut, plus a couple of threads past it
work_h     = tree_t + spoil_t;   // top of the tread above the topper
bar_l      = 110;
bar_w      = 24;
bar_t      = 16;         // bar thickness above the work
nose_l     = 12;         // grip on the work: keep <= 10-12mm, the holes start 16mm in
nose_pad   = 1;          // nose stands proud, so the bar tilts onto the work, not the heel
heel_l     = 18;
slot_from_nose = 30;     // slot starts this far from the nose end
slot_len   = 34;         // adjustment along the bar
washer_od  = 18;

$fn = 48;

echo(bolt_len = ceil(work_h + bar_t + 2 + strut_drop + nut_t));   // + 2 for the washer

module clamp() {
    difference() {
        union() {
            // bar
            translate([0, 0, work_h]) cube([bar_l, bar_w, bar_t]);
            // nose pad (on the work)
            translate([0, 0, work_h - nose_pad]) cube([nose_l, bar_w, nose_pad + 0.01]);
            // heel (on the bed), with a 45 degree inside face so it prints on its side
            hull() {
                translate([bar_l - heel_l, 0, 0]) cube([heel_l, bar_w, work_h + 0.01]);
                translate([bar_l - heel_l - 10, 0, work_h - 0.01]) cube([heel_l + 10, bar_w, 0.01]);
            }
        }
        // bolt slot
        hull() for (x = [slot_from_nose, slot_from_nose + slot_len])
            translate([x, bar_w / 2, work_h - 1]) cylinder(d = bolt_d, h = bar_t + 2);
        // grip ridges under the nose
        for (x = [2:3:nose_l - 2]) translate([x, -1, work_h - nose_pad - 0.6]) rotate([0, 45, 0]) cube([1, bar_w + 2, 1]);
    }
}

module washer() {
    difference() {
        cylinder(d = washer_od, h = 4);
        translate([0, 0, -1]) cylinder(d = bolt_d, h = 6);
    }
}

if (part == "clamp") rotate([-90, 0, 0]) translate([0, -bar_w, 0]) clamp();   // on its side
else washer();
