"""How enclosure/tree-box.FCStd was first built (1 Nov 2026), kept for reference. In FreeCAD's Python:

  freecadcmd -c "import sys; sys.path.insert(0, 'archive'); __import__('tree-box-build').main()"

One PartDesign body per printed part, with every size in the spreadsheet `params` under
the names the OpenSCAD source used, and each sketch bound to it by expressions. It is
the OpenSCAD model feature for feature, except that the stepped edges and hulls of thin
slices are now true chamfers and lofts. The .FCStd is the master from here on: edit that
and export with tools/tree_box_export.py. This script overwrites it, so don't rerun it
over edits.

Box coordinates as before: x across from the plate's left edge, y from the plate's tree
face back, z up, 0 = the cover's bottom edge.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import FreeCAD as App
import Part
import Sketcher

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "enclosure" / "tree-box.FCStd"
V = App.Vector

# name, value or formula, note. Inputs first, then what is worked out from them.
PARAMS = [
    ("# Box", None, None),
    ("box_w", 87, "plate's width: the 74 opening plus a 6.5 rim each side; the cover wraps it"),
    ("box_h", 102, "cover's height at the back edge, below the roof's last 1mm"),
    ("box_in_d", 42, "inside depth, plate to the cover's back wall"),
    ("plate_t", 5, "back plate and its ears: carries the cord groove"),
    ("floor_t", 3.5, "shelf"),
    ("lip_t", 2.4, "shelf's underside above the cover's bottom edge"),
    ("cover_wall", 2.4, ""),
    ("cover_back_t", 3, ""),
    ("cover_fit", 0.25, "cover's walls to the plate's edges, each side"),
    ("corner_r", 12, "plate's top corners; the cover's follow"),
    ("# Fasteners", None, None),
    ("m3_clear", 3.4, ""),
    ("m3_insert_d", 4.0, "M3 heat-set insert hole (CNC Kitchen / Ruthex M3 x 5.7): check on the coupon"),
    ("m3_insert_len", 6, ""),
    ("# Board: 5 x 7cm protoboard, M2 screws into heat-set inserts in the standoffs", None, None),
    ("pb_w", 70, ""),
    ("pb_h", 50, ""),
    ("pb_hole_in", 2.0, "hole centres from the board edges: from Rob's photo, measure it"),
    ("board_z0", 34.5, "above the Wagos"),
    ("standoff_h", 5, "room for the underside joins"),
    ("standoff_d", 6, ""),
    ("standoff_foot", 0.8, "cone at the root"),
    ("standoff_hole", 3.2, "M2 heat-set insert: check against the real insert on the coupon"),
    ("# Shelf entries, firing down", None, None),
    ("sp16_d", 16.7, "SP16 panel socket, M16 x 1.5: drawing hole 16.5 ..."),
    ("sp16_flat", 15.4, "... with one flat, 15.3 from the far side (stops it turning)"),
    ("pg7_d", 12.9, "PG7 thread 12.5"),
    ("ant_d", 6.6, "RP-SMA, 1/4-36"),
    ("ant_panel", 3, "shelf left at the bulkhead: it takes 3.2 at most"),
    ("ant_recess_d", 14, "room for its nut"),
    ("floor_inset", 14, "the fittings' centres from the plate: nuts clear of the plate"),
    ("ant_x", 10, "outer side, away from the tree's centre"),
    ("sp16_x", 29, ""),
    ("pg7_x", 72, ""),
    ("# Cover's rim: lands on the plate", None, None),
    ("rim_w", 6.5, ""),
    ("rim_top", 10, "below box_h"),
    ("rim_d", 3, "rim depth, before it ramps back to the walls"),
    ("open_r", 5, ""),
    ("rim_above", 0.3, "the rim stops this far above the shelf"),
    ("# Cord: 2.7mm rubber in a U-shaped groove in the plate's back face", None, None),
    ("groove_w", 3.8, "about 1.4 x the cord"),
    ("groove_d", 2.05, "about 75% of the cord"),
    ("groove_r", 8, "corner radius of the centreline"),
    ("cord_end_in", 6, "the groove's ends above the rim's bottom"),
    ("pinch_gap", 2.4, "pinch points narrow the groove to this, to hold the cord"),
    ("pinch_l", 1.6, ""),
    ("pinch_every", 22, ""),
    ("# Top hook", None, None),
    ("hook_x0", 18, ""),
    ("hook_c", 2, "the chamfer: the lift needed to get over the edge"),
    ("hook_back", 2.8, "block thickness behind the chamfer"),
    ("hook_fit", 0.2, "hook face to the chamfer, along y"),
    ("top_gap", 0.2, "plate's top edge to the roof's underside: the screw closes it"),
    ("# Skirts round the plate's edges, stopping short of the ears", None, None),
    ("skirt_end", 1.5, "skirt to the ears' fillets, below the notch"),
    ("skirt_lift", 2.5, "... and above it"),
    ("skirt_tip_r", 1.5, ""),
    ("# Bottom screw: M3 at 45 degrees through the cover's bevel into the shelf's boss", None, None),
    ("bevel", 13, "cut off the cover's lower back corner"),
    ("bevel_t", 3.6, "wall there, square to the bevel: the screw head sits in it"),
    ("head_cb_d", 7, "the head's counterbore"),
    ("head_cb_h", 1.4, ""),
    ("boss_x", 50, "between the SP16 and the PG7"),
    ("boss_d", 11, ""),
    ("boss_l", 9, "into the shelf, square to the bevel"),
    ("boss_along", 8, "the screw's centre along the bevel from the shelf's underside"),
    ("boss_gap", 0.3, "boss to the bevel's inside face"),
    ("boss_tail", 14, "how far the boss's root runs along the shelf"),
    ("rib_t", 4, "from the boss to the plate, under the Wagos"),
    ("rib_h", 6.5, ""),
    ("shelf_fillet", 2, "shelf to plate"),
    ("# Mounting on the back of the tree", None, None),
    ("ear_w", 15, "beyond each side of the plate"),
    ("ear_h", 26, ""),
    ("ear_r", 6, "corners"),
    ("ear_fillet", 3, "where they leave the plate"),
    ("mount_slot_d", 4.6, "4mm stainless wood screws (4 x 40 pan head + washer)"),
    ("mount_slot_l", 6, "slot travel, up and down"),
    ("mount_z0", 18, ""),
    ("mount_z1", 80, ""),
    ("spacer_d", 10, ""),
    ("spacer_l", 10, "rain gap between the oak and the box"),
    ("spacer_ch", 0.6, ""),
    ("# Outline", None, None),
    ("roof_slope", 8, "degrees, down away from the tree"),
    ("roof_back", 1, "roof thickness above box_h at the back edge"),
    ("blend_r", 8, "back edge of the cover"),
    ("foot_r", 3, "the cover's bottom corners"),
    ("edge_ch", 0.5, "the cover's rim, against the plate"),
    ("plate_ch_tree", 0.6, "plate's edge at the tree face, on the bed"),
    ("plate_ch_back", 0.4, "plate's edge at the back face"),
    ("min_r", 0.4, "smallest corner on the cover's sections"),
    ("# Coupon and seal test", None, None),
    ("cp_l", 76, ""),
    ("cp_w", 30, ""),
    ("st_l", 100, ""),
    ("st_w", 24, ""),
    ("st_gap", 10, "strip to bar on the bed"),
    ("st_groove_x", 14, ""),
    ("st_screw_in", 6, "the screw from the far end"),
    ("# Worked out: don't edit below here", None, None),
    ("s2", "=sqrt(0.5)", ""),
    ("tan_r", "=tan(roof_slope * 1 deg)", ""),
    ("floor_z", "=lip_t + floor_t", "shelf's top face"),
    ("floor_y", "=plate_t + floor_inset", ""),
    ("cover_y1", "=plate_t + box_in_d + cover_back_t", "cover's back face"),
    ("in_back", "=plate_t + box_in_d", "cover's back wall, inside face"),
    ("wrap", "=cover_wall + cover_fit", "the cover past the plate's edges"),
    ("cx0", "=-wrap", "cover's outside ..."),
    ("cx1", "=box_w + wrap", ""),
    ("ix0", "=-cover_fit", "... and inside faces"),
    ("ix1", "=box_w + cover_fit", ""),
    ("board_x0", "=(box_w - pb_w) / 2", ""),
    ("shelf_x0", "=cover_wall + cover_fit", ""),
    ("shelf_w", "=box_w - 2 * shelf_x0", ""),
    ("rim_z0", "=floor_z + rim_above", ""),
    ("cord_x", "=rim_w / 2", ""),
    ("cord_top", "=box_h - rim_top + rim_w / 2", ""),
    ("cord_end", "=rim_z0 + cord_end_in", ""),
    ("hook_w", "=box_w - 2 * hook_x0", ""),
    ("roof_p", "=box_h + roof_back + (cover_y1 - plate_t) * tan_r", "roof's top at the plate's back face"),
    ("plate_top", "=roof_p - cover_wall - top_gap", ""),
    ("bevel_o", "=cover_y1 - bevel", "the bevel: outside face z = y - bevel_o ..."),
    ("bevel_c", "=bevel_t / s2 - bevel_o", "... inside face z = y + bevel_c"),
    ("shelf_y0", "=lip_t - bevel_c - 0.3", "the shelf stops just short of the bevel"),
    ("shelf_y1", "=floor_z - bevel_c - 0.3", ""),
    ("screw_y", "=lip_t - bevel_c + boss_along * s2", "screw's centre on the bevel's inside face"),
    ("screw_z", "=lip_t + boss_along * s2", ""),
    ("open_top", "=box_h - rim_top", ""),
    ("y_rim", "=plate_t + rim_d", ""),
    ("y_side", "=y_rim + rim_w + cover_fit", ""),
    ("y_ramp", "=y_rim + plate_top + top_gap - open_top", ""),
    ("y_bev_in", "=lip_t - bevel_c", "where the inside's bevel starts"),
    ("ri", "=blend_r - cover_wall", "back edge's inside radius"),
    ("ro", "=corner_r + wrap - cover_wall", "top corners' inside radius"),
    ("ts", "=blend_r * (1 - s2)", "the back edge's radius stops at 45 degrees, this far from the bed"),
    ("tsi", "=ri * (1 - s2)", "... and inside"),
    ("skirt_z0", "=mount_z0 + ear_h / 2 + ear_fillet + skirt_end", "below this there is no skirt"),
    ("skirt_n0", "=mount_z1 - ear_h / 2 - ear_fillet - skirt_lift", "the notch round the upper ear"),
    ("skirt_n1", "=mount_z1 + ear_h / 2 + ear_fillet + skirt_end", ""),
    ("st_bar", "=cover_wall + 6", "as stiff as the cover's wall and rim"),
]

for k in range(5):      # sections through the back edge's radius, from where it starts
    PARAMS += [(f"o_t{k}", f"=blend_r - (blend_r - ts) * {k} / 4", ""),
               (f"o_i{k}", f"=blend_r - sqrt(blend_r ^ 2 - (blend_r - o_t{k}) ^ 2)", ""),
               (f"i_t{k}", f"=ri - (ri - tsi) * {k} / 4", ""),
               (f"i_i{k}", f"=ri - sqrt(ri ^ 2 - (ri - i_t{k}) ^ 2)", "")]

ALIASES = {p[0] for p in PARAMS if p[1] is not None}
_NAME = re.compile(r"(?<![\w.])([a-z_][a-z0-9_]*)\b")


def px(expr) -> str:
    """An expression in params names, as it must be written outside the spreadsheet."""
    return _NAME.sub(lambda m: f"params.{m[1]}" if m[1] in ALIASES else m[1], str(expr))


class Model:
    def __init__(self):
        self.doc = App.newDocument("tree_box")
        self.sheet = self.doc.addObject("Spreadsheet::Sheet", "params")
        self.sheet.set("A1", "Name")
        self.sheet.set("B1", "Value")
        self.sheet.set("C1", "Note")
        row = 2
        for name, value, note in PARAMS:
            if value is None:
                self.sheet.set(f"A{row}", name.lstrip("# "))
                self.sheet.setStyle(f"A{row}", "bold")
            else:
                self.sheet.set(f"A{row}", name)
                self.sheet.set(f"B{row}", str(value))
                self.sheet.setAlias(f"B{row}", name)
                if note:
                    self.sheet.set(f"C{row}", "'" + note)
            row += 1
        self.sheet.setColumnWidth("A", 130)
        self.sheet.setColumnWidth("C", 480)
        self.doc.recompute()
        self.body = None

    def ev(self, expr) -> float:
        v = self.sheet.evalExpression(str(expr))
        return float(getattr(v, "Value", v))

    def new_body(self, name, label=None):
        self.body = self.doc.addObject("PartDesign::Body", name)
        self.body.Label = label or name
        return self.body

    def plane(self, role):
        return next(f for f in self.body.Origin.OriginFeatures if f.Role == role)

    def axis(self, role):
        return self.plane(role)

    def sketch(self, name, plane="XZ_Plane", offset=None, angle=None):
        """offset = {x, y, z} expressions for the AttachmentOffset, in the plane's own
        frame. Sketch axes: XZ plane u = X, v = Z, normal -Y; YZ plane u = Y, v = Z, normal
        +X; XY plane u = X, v = Y, normal +Z."""
        sk = self.body.newObject("Sketcher::SketchObject", name)
        sk.AttachmentSupport = [(self.plane(plane), "")]
        sk.MapMode = "FlatFace"
        if angle is not None:
            sk.AttachmentOffset = App.Placement(V(), App.Rotation(V(1, 0, 0), angle))
        for k, expr in (offset or {}).items():
            sk.setExpression(f".AttachmentOffset.Base.{k}", px(expr))
        return sk

    def at_y(self, name, y):
        return self.sketch(name, "XZ_Plane", {"z": f"-({y})"})

    def at_x(self, name, x):
        return self.sketch(name, "YZ_Plane", {"z": x})

    def at_z(self, name, z):
        return self.sketch(name, "XY_Plane", {"z": z})

    def at_screw(self, name, local):
        """In the plane square to the cover screw, `local` along it from the bevel's inside
        face (+ into the boss). Sketch u = X, v up the bevel, normal into the boss."""
        return self.sketch(name, "XY_Plane", {"x": "boss_x", "y": f"screw_y - ({local}) * s2",
                                              "z": f"screw_z + ({local}) * s2"}, angle=45)

    def dim(self, sk, kind, a, b, value, expr=None):
        """A datum constraint between (geo, pos) points, bound to an expression."""
        name = f"d{sk.ConstraintCount}"
        i = sk.addConstraint(Sketcher.Constraint(kind, *a, *b, value))
        sk.renameConstraint(i, name)
        if expr is not None:
            sk.setExpression(f"Constraints.{name}", px(expr))

    def radius(self, sk, geo, value, expr):
        name = f"d{sk.ConstraintCount}"
        i = sk.addConstraint(Sketcher.Constraint("Radius", geo, value))
        sk.renameConstraint(i, name)
        if expr is not None:
            sk.setExpression(f"Constraints.{name}", px(expr))

    def diameter(self, sk, geo, value, expr):
        name = f"d{sk.ConstraintCount}"
        i = sk.addConstraint(Sketcher.Constraint("Diameter", geo, value))
        sk.renameConstraint(i, name)
        sk.setExpression(f"Constraints.{name}", px(expr))

    def point(self, sk, geo, pos, u, v):
        """Fix a point with expressions u, v measured from the sketch origin."""
        pu, pv = self.ev(u), self.ev(v)
        self.dim(sk, "DistanceX", (-1, 1), (geo, pos), pu, u)
        self.dim(sk, "DistanceY", (-1, 1), (geo, pos), pv, v)

    # ---- profiles -------------------------------------------------------------------

    def rounded(self, sk, x0, z0, x1, z1, rt, rb):
        """Rounded rectangle, the same 8 edges in the same order in every section."""
        a, b, c, d = self.ev(x0), self.ev(z0), self.ev(x1), self.ev(z1)
        t, r = self.ev(rt), self.ev(rb)
        C = lambda x, y, rad, a0, a1: Part.ArcOfCircle(Part.Circle(V(x, y, 0), V(0, 0, 1), rad),
                                                      math.radians(a0), math.radians(a1))
        L = lambda p, q: Part.LineSegment(V(*p, 0), V(*q, 0))
        sk.addGeometry([L((a + r, b), (c - r, b)), C(c - r, b + r, r, -90, 0),
                        L((c, b + r), (c, d - t)), C(c - t, d - t, t, 0, 90),
                        L((c - t, d), (a + t, d)), C(a + t, d - t, t, 90, 180),
                        L((a, d - t), (a, b + r)), C(a + r, b + r, r, 180, 270)], False)
        sk.addConstraint([Sketcher.Constraint("Tangent", i, 2, (i + 1) % 8, 1) for i in range(8)]
                         + [Sketcher.Constraint("Horizontal", 0), Sketcher.Constraint("Horizontal", 4),
                            Sketcher.Constraint("Vertical", 2), Sketcher.Constraint("Vertical", 6),
                            Sketcher.Constraint("Equal", 1, 7), Sketcher.Constraint("Equal", 3, 5)])
        self.dim(sk, "DistanceY", (-1, 1), (0, 1), b, z0)
        self.dim(sk, "DistanceY", (-1, 1), (4, 1), d, z1)
        self.dim(sk, "DistanceX", (-1, 1), (2, 1), c, x1)
        self.dim(sk, "DistanceX", (-1, 1), (6, 1), a, x0)
        self.radius(sk, 3, t, rt)
        self.radius(sk, 1, r, rb)

    def polygon(self, sk, pts):
        """Closed polygon: every corner fixed by expressions."""
        n = len(pts)
        p = [(self.ev(u), self.ev(v)) for u, v in pts]
        g = sk.GeometryCount
        sk.addGeometry([Part.LineSegment(V(*p[i], 0), V(*p[(i + 1) % n], 0)) for i in range(n)], False)
        sk.addConstraint([Sketcher.Constraint("Coincident", g + i, 2, g + (i + 1) % n, 1) for i in range(n)])
        for i, (u, v) in enumerate(pts):
            self.point(sk, g + i, 1, u, v)

    def rect(self, sk, x0, y0, x1, y1):
        self.polygon(sk, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

    def circle(self, sk, x, y, d):
        g = sk.GeometryCount
        sk.addGeometry(Part.Circle(V(self.ev(x), self.ev(y), 0), V(0, 0, 1), self.ev(d) / 2), False)
        self.point(sk, g, 3, x, y)
        self.diameter(sk, g, self.ev(d), d)

    def chain(self, sk, items):
        """Closed outline of horizontal lines ("h", v), vertical lines ("v", u) and arcs
        ("a", cu, cv, r, sense, {dims}), each tangent to the next where it can be.
        cu, cv and r are expressions; dims picks which of "u", "v", "r" get a dimension, for the
        ones that the neighbours don't already fix."""
        ev = self.ev
        n = len(items)

        def junction(a, b):
            if a[0] == "a" and b[0] == "a":
                c1, c2 = V(ev(a[1]), ev(a[2]), 0), V(ev(b[1]), ev(b[2]), 0)
                r = ev(a[3])
                d = (c2 - c1)
                d.normalize()
                return (c1 + d * r) if a[4] != b[4] else (c1 - d * r)
            if a[0] == "a" or b[0] == "a":
                arc, line = (a, b) if a[0] == "a" else (b, a)
                return V(ev(arc[1]), ev(line[1]), 0) if line[0] == "h" else V(ev(line[1]), ev(arc[2]), 0)
            h, v = (a, b) if a[0] == "h" else (b, a)
            return V(ev(v[1]), ev(h[1]), 0)

        ends = [(junction(items[i - 1], items[i]), junction(items[i], items[(i + 1) % n])) for i in range(n)]
        g0 = sk.GeometryCount
        pos = []             # (start pos, end pos) of each item as the chain runs
        for it, (p, q) in zip(items, ends):
            if it[0] == "a":
                c = V(ev(it[1]), ev(it[2]), 0)
                a0, a1 = math.atan2(p.y - c.y, p.x - c.x), math.atan2(q.y - c.y, q.x - c.x)
                if it[4] < 0:
                    a0, a1 = a1, a0
                if a1 <= a0:
                    a1 += 2 * math.pi
                sk.addGeometry(Part.ArcOfCircle(Part.Circle(c, V(0, 0, 1), ev(it[3])), a0, a1), False)
                pos.append((1, 2) if it[4] > 0 else (2, 1))
            else:
                sk.addGeometry(Part.LineSegment(p, q), False)
                pos.append((1, 2))
        for i, it in enumerate(items):
            j = (i + 1) % n
            kind = "Tangent" if "a" in (it[0], items[j][0]) else "Coincident"
            sk.addConstraint(Sketcher.Constraint(kind, g0 + i, pos[i][1], g0 + j, pos[j][0]))
        for i, it in enumerate(items):
            g = g0 + i
            if it[0] == "h":
                sk.addConstraint(Sketcher.Constraint("Horizontal", g))
                self.dim(sk, "DistanceY", (-1, 1), (g, 1), ev(it[1]), it[1])
            elif it[0] == "v":
                sk.addConstraint(Sketcher.Constraint("Vertical", g))
                self.dim(sk, "DistanceX", (-1, 1), (g, 1), ev(it[1]), it[1])
            else:
                dims = it[5] if len(it) > 5 else "r"
                if "r" in dims:
                    self.radius(sk, g, ev(it[3]), it[3])
                if "u" in dims:
                    self.dim(sk, "DistanceX", (-1, 1), (g, 3), ev(it[1]), it[1])
                if "v" in dims:
                    self.dim(sk, "DistanceY", (-1, 1), (g, 3), ev(it[2]), it[2])

    def slot(self, sk, x, z, d, l):
        """Stadium, its length along v."""
        self.chain(sk, [("v", f"{x} + {d} / 2"), ("a", x, f"{z} + {l} / 2", f"{d} / 2", 1, "v"),
                        ("v", f"{x} - {d} / 2"), ("a", x, f"{z} - {l} / 2", f"{d} / 2", 1, "v")])

    def teardrop(self, sk, x, y, d):
        """Hole pointing up the print (+y), so it needs no support."""
        cx, cy, r = self.ev(x), self.ev(y), self.ev(d) / 2
        g = sk.GeometryCount
        tip = V(cx, cy + r * math.sqrt(2), 0)
        s = r * math.sqrt(0.5)
        arc = Part.ArcOfCircle(Part.Circle(V(cx, cy, 0), V(0, 0, 1), r), math.radians(135), math.radians(405))
        sk.addGeometry([arc, Part.LineSegment(V(cx + s, cy + s, 0), tip), Part.LineSegment(tip, V(cx - s, cy + s, 0))], False)
        sk.addConstraint([Sketcher.Constraint("Tangent", g, 2, g + 1, 1), Sketcher.Constraint("Tangent", g + 2, 2, g, 1),
                          Sketcher.Constraint("Coincident", g + 1, 2, g + 2, 1),
                          Sketcher.Constraint("Vertical", g, 3, g + 1, 2)])
        self.point(sk, g, 3, x, y)
        self.radius(sk, g, r, f"{d} / 2")
        self.dim(sk, "DistanceY", (g, 3), (g + 1, 2), r * math.sqrt(2), f"{d} / 2 / s2")

    def d_hole(self, sk, x, y, d, flat):
        """Circle with a flat on the +y side, `flat` from the far side."""
        cx, cy, r = self.ev(x), self.ev(y), self.ev(d) / 2
        f = self.ev(flat) - r
        a = math.asin(f / r)
        g = sk.GeometryCount
        p = V(cx + r * math.cos(a), cy + f, 0)
        q = V(cx - r * math.cos(a), cy + f, 0)
        sk.addGeometry([Part.ArcOfCircle(Part.Circle(V(cx, cy, 0), V(0, 0, 1), r), math.pi - a, 2 * math.pi + a),
                        Part.LineSegment(p, q)], False)
        sk.addConstraint([Sketcher.Constraint("Coincident", g, 2, g + 1, 1), Sketcher.Constraint("Coincident", g + 1, 2, g, 1),
                          Sketcher.Constraint("Horizontal", g + 1)])
        self.point(sk, g, 3, x, y)
        self.radius(sk, g, r, f"{d} / 2")
        self.dim(sk, "DistanceY", (g, 3), (g + 1, 1), f, f"{flat} - {d} / 2")

    # ---- features -------------------------------------------------------------------

    def finish(self, f):
        f.Refine = True
        self.doc.recompute()
        if not f.isValid() or f.Shape.isNull() or not f.Shape.isValid():
            raise RuntimeError(f"{f.Name} failed: {f.getStatusString()}")
        return f

    def pad(self, name, sk, length, reversed_=False, midplane=False, taper=None):
        f = self.body.newObject("PartDesign::Pad", name)
        f.Profile = sk
        f.Reversed = reversed_
        f.SideType = "Symmetric" if midplane else "One side"
        f.setExpression("Length", px(length))
        if taper is not None:
            f.TaperAngle = taper
        return self.finish(f)

    def pocket(self, name, sk, length, reversed_=False, midplane=False):
        f = self.body.newObject("PartDesign::Pocket", name)
        f.Profile = sk
        f.Reversed = reversed_
        f.SideType = "Symmetric" if midplane else "One side"
        f.setExpression("Length", px(length))
        return self.finish(f)

    def loft(self, name, sketches, ruled=True, cut=False):
        f = self.body.newObject("PartDesign::SubtractiveLoft" if cut else "PartDesign::AdditiveLoft", name)
        f.Profile = sketches[0]
        f.Sections = sketches[1:]
        f.Ruled = ruled
        f.Closed = False
        return self.finish(f)

    def pattern(self, name, base, axis, length, count):
        f = self.body.newObject("PartDesign::LinearPattern", name)
        f.Originals = [base]
        f.Direction = (self.axis(axis), [""])
        f.setExpression("Length", px(length))
        f.setExpression("Occurrences", px(count))
        self.body.Tip = f
        return self.finish(f)


def plate_outline(m, i="0"):
    """The back plate with its four ears: the OpenSCAD outline's offsets, worked out as
    arcs. The right side is the left mirrored. Inset by i for the chamfered edges: the
    centres stay put, convex arcs shrink and concave ones grow."""
    z_low0, z_low1 = "mount_z0 - ear_h / 2", "mount_z0 + ear_h / 2"
    z_up0, z_up1 = "mount_z1 - ear_h / 2", "mount_z1 + ear_h / 2"
    # the concave arc under the lower ear runs straight into the arc at the plate's foot
    low_x, low_z = "-ear_fillet", f"{z_low0} - ear_fillet"
    foot_z = "lip_t + ear_r"
    foot_x = f"({low_x}) + sqrt((ear_fillet + ear_r) ^ 2 - (({foot_z}) - ({low_z})) ^ 2)"
    # ... and the one over the upper ear into the plate's top corner
    top_cz = "plate_top - corner_r"
    high_z = f"{z_up1} + ear_fillet"
    high_x = f"corner_r - sqrt((corner_r + ear_fillet) ^ 2 - (({high_z}) - ({top_cz})) ^ 2)"
    convex, concave = f"ear_r - {i}", f"ear_fillet + {i}"

    def side(flip):
        X = (lambda e: f"box_w - ({e})") if flip else (lambda e: e)
        s = -1          # the same either side: mirroring and running backwards cancel out
        return [
            ("a", X(foot_x), foot_z, convex, -s),
            ("a", X(low_x), low_z, concave, s, "ru"),
            ("h", f"{z_low0} + {i}"),
            ("a", X("ear_r - ear_w"), f"{z_low0} + ear_r", convex, -s),
            ("v", X(f"{i} - ear_w")),
            ("a", X("ear_r - ear_w"), f"{z_low1} - ear_r", convex, -s),
            ("h", f"{z_low1} - {i}"),
            ("a", X("-ear_fillet"), f"{z_low1} + ear_fillet", concave, s),
            ("v", X(i)),
            ("a", X("-ear_fillet"), f"{z_up0} - ear_fillet", concave, s),
            ("h", f"{z_up0} + {i}"),
            ("a", X("ear_r - ear_w"), f"{z_up0} + ear_r", convex, -s),
            ("v", X(f"{i} - ear_w")),
            ("a", X("ear_r - ear_w"), f"{z_up1} - ear_r", convex, -s),
            ("h", f"{z_up1} - {i}"),
            ("a", X(high_x), high_z, concave, s),
            ("a", X("corner_r"), top_cz, f"corner_r - {i}", -s, "ru"),
        ]

    # counter-clockwise from the plate's bottom edge: right side going up, the top, left going down
    return [("h", f"lip_t + {i}")] + side(True) + [("h", f"plate_top - {i}")] + mirrored(side(False))


def mirrored(items):
    """A chain run backwards, for the other side of a symmetric outline."""
    return list(reversed(items))


def cord_outline():
    """The U the cord follows, as the groove's outline."""
    hw = "groove_w / 2"
    x0, x1, r = "cord_x", "box_w - cord_x", "groove_r"
    return [("a", x1, "cord_end", hw, -1, "v"), ("v", f"{x1} - {hw}"),
            ("a", f"{x1} - {r}", f"cord_top - {r}", f"{r} - {hw}", 1),
            ("h", f"cord_top - {hw}"),
            ("a", f"{x0} + {r}", f"cord_top - {r}", f"{r} - {hw}", 1),
            ("v", f"{x0} + {hw}"), ("a", x0, "cord_end", hw, -1, "v"), ("v", f"{x0} - {hw}"),
            ("a", f"{x0} + {r}", f"cord_top - {r}", f"{r} + {hw}", -1),
            ("h", f"cord_top + {hw}"),
            ("a", f"{x1} - {r}", f"cord_top - {r}", f"{r} + {hw}", -1), ("v", f"{x1} + {hw}")]


def build_base(m):
    m.new_body("Base", "Base (L: plate + shelf)")

    def outline(name, y, i="0"):
        sk = m.at_y(name, y)
        m.chain(sk, plate_outline(m, i))
        return sk

    m.loft("PlateEdgeTree", [outline("PlateFace", "0", "plate_ch_tree"), outline("PlateFaceEnd", "plate_ch_tree")])
    m.pad("Plate", outline("PlateSketch", "plate_ch_tree"), "plate_t - plate_ch_tree - plate_ch_back", reversed_=True)
    m.loft("PlateEdgeBack", [outline("PlateBack", "plate_t - plate_ch_back"), outline("PlateBackEnd", "plate_t", "plate_ch_back")])

    sk = m.at_x("ShelfSketch", "box_w / 2")
    m.polygon(sk, [("plate_t - 1", "lip_t"), ("shelf_y0", "lip_t"), ("shelf_y1", "floor_z"), ("plate_t - 1", "floor_z")])
    m.pad("Shelf", sk, "shelf_w", midplane=True)

    sk = m.at_x("ShelfFilletSketch", "box_w / 2")
    m.polygon(sk, [("plate_t - 1", "floor_z - 1"), ("plate_t + shelf_fillet", "floor_z - 1"),
                   ("plate_t + shelf_fillet", "floor_z"), ("plate_t", "floor_z + shelf_fillet"),
                   ("plate_t - 1", "floor_z + shelf_fillet")])
    m.pad("ShelfFillet", sk, "box_w - 2 * (rim_w + open_r + 0.5)", midplane=True)

    # The boss: the flat sides, the cylinder and the blend up its top, which is what a hull of them gave
    sk = m.at_x("BossSideSketch", "boss_x")
    m.polygon(sk, [("shelf_y0 - boss_tail", "lip_t"), ("shelf_y0 - 1", "lip_t"),
                   ("screw_y - boss_gap * s2", "screw_z + boss_gap * s2"),
                   ("screw_y - (boss_gap + boss_l) * s2", "screw_z + (boss_gap + boss_l) * s2"),
                   ("shelf_y0 - boss_tail", "floor_z")])
    m.pad("BossSide", sk, "boss_d", midplane=True)
    sk = m.at_screw("BossSketch", "boss_gap")
    m.circle(sk, "0", "0", "boss_d")
    m.pad("Boss", sk, "boss_l")
    a = m.at_y("BossRootSketch", "shelf_y0 - boss_tail")
    m.rect(a, "boss_x - boss_d / 2", "lip_t", "boss_x + boss_d / 2", "floor_z")
    b = m.at_screw("BossTopSketch", "boss_gap + boss_l")
    m.circle(b, "0", "0", "boss_d")
    m.loft("BossBlend", [a, b])

    sk = m.at_x("RibSketch", "boss_x")
    m.polygon(sk, [("plate_t - 1", "floor_z - 0.4"), ("shelf_y0 - 2", "floor_z - 0.4"), ("shelf_y0 - 2", "floor_z"),
                   ("shelf_y0 - 8", "floor_z + rib_h"), ("plate_t - 1", "floor_z + rib_h")])
    m.pad("Rib", sk, "rib_t", midplane=True)

    # Standoffs: on the board's corner holes
    holes = [(f"board_x0 + {x}", f"board_z0 + {z}") for x in ("pb_hole_in", "pb_w - pb_hole_in")
             for z in ("pb_hole_in", "pb_h - pb_hole_in")]
    sk = m.at_y("StandoffSketch", "plate_t - 1")
    for x, z in holes:
        m.circle(sk, x, z, "standoff_d")
    m.pad("Standoffs", sk, "standoff_h + 1", reversed_=True)
    sk = m.at_y("StandoffFootSketch", "plate_t")
    for x, z in holes:
        m.circle(sk, x, z, "standoff_d + 2 * standoff_foot")
    m.pad("StandoffFeet", sk, "standoff_foot", reversed_=True, taper=-45)
    sk = m.at_y("StandoffHoleSketch", "plate_t + standoff_h")
    for x, z in holes:
        m.circle(sk, x, z, "standoff_hole")
    m.pocket("StandoffHoles", sk, "standoff_h + 1", reversed_=True)

    # Cord groove and its pinch points
    sk = m.at_y("GrooveSketch", "plate_t")
    m.chain(sk, cord_outline())
    m.pocket("Groove", sk, "groove_d", reversed_=True)
    gap, tab = "pinch_gap / 2", "(groove_w / 2 + 0.1)"
    sk = m.at_y("PinchSideSketch", "plate_t")
    z0, z1 = "cord_end + cord_end_in - pinch_l / 2", "cord_end + cord_end_in + pinch_l / 2"
    for x in ("cord_x", "box_w - cord_x"):
        m.rect(sk, f"{x} - {tab}", z0, f"{x} - {gap}", z1)
        m.rect(sk, f"{x} + {gap}", z0, f"{x} + {tab}", z1)
    pad = m.pad("PinchSide", sk, "groove_d + 0.05")
    n = "floor((cord_top - groove_r - 2 - cord_end - cord_end_in) / pinch_every)"
    m.pattern("PinchSides", pad, "Z_Axis", f"{n} * pinch_every", f"{n} + 1")
    sk = m.at_y("PinchTopSketch", "plate_t")
    x0, x1 = "cord_x + groove_r + 4 - pinch_l / 2", "cord_x + groove_r + 4 + pinch_l / 2"
    m.rect(sk, x0, f"cord_top - {tab}", x1, f"cord_top - {gap}")
    m.rect(sk, x0, f"cord_top + {gap}", x1, f"cord_top + {tab}")
    pad = m.pad("PinchTop", sk, "groove_d + 0.05")
    n = "floor((box_w - 2 * cord_x - 2 * groove_r - 6) / pinch_every)"
    m.pattern("PinchTops", pad, "X_Axis", f"{n} * pinch_every", f"{n} + 1")

    # Mounting slots
    sk = m.at_y("SlotSketch", "-1")
    for x in ("-ear_w / 2", "box_w + ear_w / 2"):
        for z in ("mount_z0", "mount_z1"):
            m.slot(sk, f"({x})", z, "mount_slot_d", "mount_slot_l")
    m.pocket("Slots", sk, "plate_t + 2")

    # The three entries through the shelf, from underneath
    sk = m.at_z("EntriesSketch", "lip_t - 1")
    m.d_hole(sk, "sp16_x", "floor_y", "sp16_d", "sp16_flat")
    m.teardrop(sk, "pg7_x", "floor_y", "pg7_d")
    m.teardrop(sk, "ant_x", "floor_y", "ant_d")
    m.pocket("Entries", sk, "floor_t + 2", reversed_=True)
    sk = m.at_z("AntennaRecessSketch", "lip_t + ant_panel")
    m.teardrop(sk, "ant_x", "floor_y", "ant_recess_d")
    m.pocket("AntennaRecess", sk, "floor_t", reversed_=True)

    # The chamfer the hook hangs on: along the plate's top edge at the tree face
    sk = m.at_x("HookChamferSketch", "box_w / 2")
    m.polygon(sk, [("-1", "plate_top - hook_c - 1"), ("hook_c + 1", "plate_top + 1"), ("-1", "plate_top + 1")])
    m.pocket("HookChamfer", sk, "hook_w + 2", midplane=True)

    sk = m.at_screw("InsertSketch", "0")
    m.circle(sk, "0", "0", "m3_insert_d")
    m.pocket("Insert", sk, "m3_insert_len + 0.5", reversed_=True)


def roof(y):
    return f"(box_h + roof_back + (cover_y1 - ({y})) * tan_r)"


def outer_section(m, name, y, i):
    """The cover's outside at y, inset by i as the edges blend away."""
    sk = m.at_y(name, y)
    m.rounded(sk, f"cx0 + {i}", f"max(0; ({y}) - bevel_o) + {i}", f"cx1 - {i}", f"{roof(y)} - {i}",
              f"max(corner_r + wrap - {i}; min_r)", f"max(foot_r - {i}; min_r)")
    return sk


def inner_section(m, name, y, i="0"):
    """The cover's inside at y: the same form a wall thick."""
    sk = m.at_y(name, y)
    m.rounded(sk, f"ix0 + {i}", f"max(lip_t; ({y}) + bevel_c) + {i}", f"ix1 - {i}",
              f"{roof(y)} - cover_wall - {i}", f"max(ro - {i}; min_r)", "min_r")
    return sk


def opening_section(m, name, y):
    sk = m.at_y(name, y)
    m.rounded(sk, "rim_w", "rim_z0", "box_w - rim_w", "open_top", "open_r", "open_r")
    return sk


def sides_section(m, name):
    sk = m.at_y(name, "y_side")
    m.rounded(sk, "ix0", "lip_t", "ix1", "open_top + y_side - y_rim", "ro", "min_r")
    return sk


def skirt_outline(m):
    """What comes off the cover in front of the rim: all but a skirt round the plate's
    edges, notched at the upper ear."""
    ev = m.ev
    far, tip, r, top = "30", "skirt_tip_r", "corner_r + cover_fit", "plate_top + top_gap"
    cz = f"{top} - ({r})"
    tip_z = f"skirt_n1 + {tip}"
    tip_x = f"(corner_r - sqrt(({r} + {tip}) ^ 2 - (({tip_z}) - ({cz})) ^ 2))"

    def side(flip):
        X = (lambda e: f"box_w - ({e})") if flip else (lambda e: e)
        s = -1
        return [("h", "skirt_z0"), ("a", X(f"ix0 - {tip}"), f"skirt_z0 + {tip}", tip, s), ("v", X("ix0")),
                ("a", X(f"ix0 - {tip}"), f"skirt_n0 - {tip}", tip, s), ("h", "skirt_n0"), ("v", X(f"-{far}")),
                ("h", "skirt_n1"), ("a", X(tip_x), tip_z, tip, s), ("a", X("corner_r"), cz, r, -s, "ru")]

    right = side(True)
    left = side(False)
    return [("h", "-5"), ("v", f"box_w + {far}")] + right + [("h", top)] + mirrored(left) + [("v", f"-{far}")]


def build_cover(m):
    m.new_body("Cover", "Cover (wrap-round)")

    # The outside: one form with the roof, the bevel, the corners and the back edge in it
    s0 = outer_section(m, "OuterRim", "0", "edge_ch")
    s1 = outer_section(m, "OuterRimEnd", "edge_ch", "0")
    m.loft("OuterEdge", [s0, s1])
    s2 = outer_section(m, "OuterBevelStart", "bevel_o", "0")
    m.loft("OuterMain", [outer_section(m, "OuterRimEnd2", "edge_ch", "0"), s2])
    s3 = outer_section(m, "OuterBlendStart", "cover_y1 - o_t0", "o_i0")
    m.loft("OuterBevel", [outer_section(m, "OuterBevelStart2", "bevel_o", "0"), s3])
    blend = [outer_section(m, f"OuterBlend{k}", f"cover_y1 - o_t{k}", f"o_i{k}") for k in range(5)]
    m.loft("OuterRadius", blend, ruled=False)
    m.loft("OuterChamfer", [outer_section(m, "OuterBlend4b", "cover_y1 - o_t4", "o_i4"),
                            outer_section(m, "OuterBack", "cover_y1", "2 * ts")])

    # The inside, from the rim's opening back
    m.loft("OpeningCut", [opening_section(m, "Opening0", "plate_t - 1"), opening_section(m, "Opening1", "y_rim")], cut=True)
    m.loft("RimRamp", [opening_section(m, "Opening2", "y_rim"), sides_section(m, "Sides0")], cut=True)
    m.loft("TopRamp", [sides_section(m, "Sides1"), inner_section(m, "Inner0", "y_ramp")], cut=True)
    m.loft("InnerMain", [inner_section(m, "Inner1", "y_ramp"), inner_section(m, "Inner2", "y_bev_in")], cut=True)
    m.loft("InnerBevel", [inner_section(m, "Inner3", "y_bev_in"),
                          inner_section(m, "Inner4", "in_back - i_t0", "i_i0")], cut=True)
    blend = [inner_section(m, f"InnerBlend{k}", f"in_back - i_t{k}", f"i_i{k}") for k in range(5)]
    m.loft("InnerRadius", blend, ruled=False, cut=True)
    m.loft("InnerChamfer", [inner_section(m, "InnerBlend4b", "in_back - i_t4", "i_i4"),
                            inner_section(m, "InnerBack", "in_back", "2 * tsi")], cut=True)

    # Round the shelf, below the rim, and down the bevel
    sk = m.at_x("UnderRimSketch", "box_w / 2")
    m.polygon(sk, [("plate_t - 1", "-1"), ("-1 - bevel_c", "-1"), ("rim_z0 - bevel_c", "rim_z0"), ("plate_t - 1", "rim_z0")])
    m.pocket("UnderRim", sk, "ix1 - ix0", midplane=True)

    # Behind the rim, all that is left is the skirt round the plate
    sk = m.at_y("SkirtSketch", "plate_t")
    m.chain(sk, skirt_outline(m))
    m.pocket("Skirts", sk, "plate_t + 5", reversed_=True)

    # The hook: hangs on the plate's chamfer, blended into the roof
    sk = m.at_x("HookSketch", "box_w / 2")
    y1 = "(-hook_fit - hook_back)"
    m.polygon(sk, [("hook_c - hook_fit + top_gap", "plate_top + top_gap"), ("-hook_fit", "plate_top - hook_c"),
                   (y1, "plate_top - hook_c"), (y1, f"{roof(y1)} - 1"),
                   (f"{y1} + 1", roof(f"{y1} + 1")), ("edge_ch", roof("edge_ch")),
                   ("hook_c + 1", f"{roof('hook_c + 1')} - 1")])
    m.pad("Hook", sk, "hook_w", midplane=True)

    sk = m.at_screw("ScrewHoleSketch", "-bevel_t - 1")
    m.circle(sk, "0", "0", "m3_clear")
    m.pocket("ScrewHole", sk, "bevel_t + 2", reversed_=True)
    sk = m.at_screw("CounterboreSketch", "-bevel_t - 1")
    m.circle(sk, "0", "0", "head_cb_d")
    m.pocket("Counterbore", sk, "head_cb_h + 1", reversed_=True)


def build_spacer(m):
    m.new_body("Spacer", "Spacer (4 per tree)")
    sk = m.at_y("SpacerSketch", "0")
    r, ch = "spacer_d / 2", "spacer_ch"
    m.polygon(sk, [("mount_slot_d / 2", "0"), (f"{r} - {ch}", "0"), (r, ch), (r, f"spacer_l - {ch}"),
                  (f"{r} - {ch}", "spacer_l"), ("mount_slot_d / 2", "spacer_l")])
    f = m.body.newObject("PartDesign::Revolution", "SpacerRevolve")
    f.Profile = sk
    f.ReferenceAxis = (m.axis("Z_Axis"), [""])
    f.Angle = 360
    m.finish(f)


def build_coupon(m):
    m.new_body("Coupon", "Coupon (fit test: print first)")
    sk = m.at_z("CouponStripSketch", "0")
    m.rect(sk, "0", "0", "cp_l", "cp_w")
    m.pad("CouponStrip", sk, "floor_t")
    sk = m.at_z("CouponBlockSketch", "0")
    m.rect(sk, "50", "cp_w - 8", "62", "cp_w")
    m.pad("CouponBlock", sk, "12")
    sk = m.at_z("CouponStandoffSketch", "0")
    m.circle(sk, "68", "8", "standoff_d")
    m.pad("CouponStandoff", sk, "floor_t + standoff_h")
    sk = m.at_z("CouponHolesSketch", "-1")
    m.d_hole(sk, "14", "13", "sp16_d", "sp16_flat")
    m.circle(sk, "38", "13", "pg7_d")
    m.circle(sk, "56", "11", "ant_d")
    m.pocket("CouponHoles", sk, "floor_t + 2", reversed_=True)
    sk = m.at_z("CouponRecessSketch", "ant_panel")
    m.circle(sk, "56", "11", "ant_recess_d")
    m.pocket("CouponRecess", sk, "floor_t", reversed_=True)
    sk = m.at_y("CouponInsertSketch", "cp_w")
    m.circle(sk, "56", "7", "m3_insert_d")
    m.pocket("CouponInsert", sk, "m3_insert_len", reversed_=True)
    sk = m.at_z("CouponM2Sketch", "floor_t + standoff_h")
    m.circle(sk, "68", "8", "standoff_hole")
    m.pocket("CouponM2", sk, "standoff_h")


def build_seal_test(m):
    m.new_body("SealStrip", "Seal test: plate strip")
    sk = m.at_z("StripSketch", "0")
    m.rect(sk, "0", "0", "st_l", "st_w")
    m.pad("Strip", sk, "plate_t")
    sk = m.at_z("StripGrooveSketch", "plate_t")
    m.rect(sk, "st_groove_x", "st_w / 2 - groove_w / 2", "st_l - 12", "st_w / 2 + groove_w / 2")
    m.pocket("StripGroove", sk, "groove_d")
    gap, tab = "pinch_gap / 2", "(groove_w / 2 + 0.1)"
    sk = m.at_z("StripPinchSketch", "plate_t")
    m.rect(sk, "20 - pinch_l / 2", f"st_w / 2 - {tab}", "20 + pinch_l / 2", f"st_w / 2 - {gap}")
    m.rect(sk, "20 - pinch_l / 2", f"st_w / 2 + {gap}", "20 + pinch_l / 2", f"st_w / 2 + {tab}")
    pad = m.pad("StripPinch", sk, "groove_d + 0.05", reversed_=True)
    n = "floor((st_l - 36) / pinch_every)"
    m.pattern("StripPinches", pad, "X_Axis", f"{n} * pinch_every", f"{n} + 1")
    sk = m.at_y("StripChamferSketch", "0")
    m.polygon(sk, [("-1", "-1"), ("hook_c + 1", "-1"), ("-1", "hook_c + 1")])
    m.pocket("StripChamfer", sk, "st_w")
    sk = m.at_z("StripInsertSketch", "-1")
    m.circle(sk, "st_l - st_screw_in", "st_w / 2", "m3_insert_d")
    m.pocket("StripInsert", sk, "plate_t + 2", reversed_=True)

    m.new_body("SealBar", "Seal test: cover bar")
    y0 = "st_w + st_gap"
    sk = m.at_y("BarSketch", y0)
    top = "(st_bar + plate_t)"
    m.polygon(sk, [("-top_gap - cover_wall", "0"), ("st_l", "0"), ("st_l", "st_bar"), ("-top_gap", "st_bar"),
                   ("-top_gap", f"{top} - hook_c + hook_fit - top_gap"), ("hook_c", f"{top} + hook_fit"),
                   ("hook_c", f"{top} + hook_fit + hook_back"), ("-top_gap - cover_wall", f"{top} + hook_fit + hook_back")])
    m.pad("Bar", sk, "st_w", reversed_=True)
    sk = m.at_z("BarHoleSketch", "-1")
    m.circle(sk, "st_l - st_screw_in", f"{y0} + st_w / 2", "m3_clear")
    m.pocket("BarHole", sk, "st_bar + 2", reversed_=True)


def report(m):
    for b in m.doc.findObjects("PartDesign::Body"):
        s = b.Shape
        bb = s.BoundBox
        print(f"{b.Name}: valid {s.isValid()}, solids {len(s.Solids)}, faces {len(s.Faces)}, volume {s.Volume:.1f}, "
              f"x {bb.XMin:.3f} {bb.XMax:.3f} y {bb.YMin:.3f} {bb.YMax:.3f} z {bb.ZMin:.3f} {bb.ZMax:.3f}")
    sketches = m.doc.findObjects("Sketcher::SketchObject")
    print(f"sketches {len(sketches)}, not solving {[s.Name for s in sketches if s.solve() != 0]}, "
          f"not fully constrained {[s.Name for s in sketches if not s.FullyConstrained]}")


def main(path=OUT):
    m = Model()
    build_base(m)
    build_cover(m)
    build_spacer(m)
    build_coupon(m)
    build_seal_test(m)
    m.doc.recompute()
    report(m)
    m.doc.saveAs(str(path))
    return m
