// Printed hold-down clamp for the CNC bed's channel-strut rails (41mm strut, ~180mm
// centres; one tree per setup, two to four clamps). The bolt goes into a strut
// spring/channel nut.
// A bar with a nose that presses on the tread's edge and a heel that rests on the bed;
// the M6 bolt goes through the slot between them, nearer the nose so most of the force
// lands on the work. PETG, printed on its side (slot vertical) so the layers run along
// the bar and don't split under the bolt.
//
// Bolts: M6 into strut channel nuts (Rob, 23 Oct 2026).
// work_h is the top of the tread above whatever the heel stands on: 30mm if the heel
// stands on the same MDF sheet as the tread; 30 + the MDF thickness if the heel
// stands on the strut and the tread on MDF laid between/over the struts.

part = "clamp";          // "clamp" or "washer"

bolt_d     = 6.5;        // M6 clearance
work_h     = 30;         // tread thickness above the heel's footing
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
