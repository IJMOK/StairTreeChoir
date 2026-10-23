// Lid seal shared by the tree box and the site box: Rob's 2.7mm rubber cord
// (23 Oct 2026) in a groove in the lid's inner face, pressed onto the flat rim
// of the box. Face-seal proportions: depth ~75% of the cord (about 25% squeeze),
// width ~1.4x the cord, corners radius >= 3x the cord so it doesn't kink.
// Cut the cord to length and butt-join it with a drop of superglue.

cord_d     = 2.7;
groove_w   = 3.8;
groove_d   = 2.05;
groove_r   = 8;       // corner radius of the groove's centreline

// Groove as a solid to subtract: centreline is a rounded rectangle inset `inset`
// from the edges of a w x h lid, from z = 0 up; place it groove_d below the face.
module cord_groove(w, h, inset) {
    linear_extrude(groove_d + 1) difference() {   // +1: runs out through the face
        offset(r = groove_r + groove_w / 2) offset(delta = -groove_r)
            translate([inset, inset]) square([w - 2 * inset, h - 2 * inset]);
        offset(r = groove_r - groove_w / 2) offset(delta = -groove_r)
            translate([inset, inset]) square([w - 2 * inset, h - 2 * inset]);
    }
}
