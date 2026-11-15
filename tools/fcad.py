"""Helpers for building parametric FreeCAD masters (run inside FreeCAD: freecadcmd or the GUI).

Every master in cad/parts/ has a `params` spreadsheet (column A the name, B the value with
that name as its alias, C a note) and Part primitives whose sizes and positions are
expressions on it, so a part changes by editing the sheet and recomputing, in the GUI or
headless. The builders in tools/cad_parts.py use these helpers to make a master the first
time; after that the .FCStd is the master and is edited by hand.

Expressions are plain strings in FreeCAD's expression language; `p.name` below is written
`params.name` in them. Numbers are mm and degrees.
"""

from __future__ import annotations

import FreeCAD as App
import Part  # noqa: F401  (registers the Part:: types)

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)


def new_doc(name: str):
    for d in list(App.listDocuments().values()):
        if d.Name == name:
            App.closeDocument(d.Name)
    return App.newDocument(name)


def sheet(doc, rows: list[tuple[str, float, str]], name: str = "params"):
    """rows: (alias, value, note). A heading row is ("", None, "heading")."""
    s = doc.addObject("Spreadsheet::Sheet", name)
    s.set("A1", "name")
    s.set("B1", "value")
    s.set("C1", "note")
    for i, (alias, value, note) in enumerate(rows, start=2):
        if alias:
            s.set(f"A{i}", alias)
            s.set(f"B{i}", str(value) if not isinstance(value, str) else value)
            s.setAlias(f"B{i}", alias)
        s.set(f"C{i}", "'" + note if note else "")
    s.setColumnWidth("A", 150)
    s.setColumnWidth("C", 520)
    doc.recompute()
    return s


def _place(obj, x="0", y="0", z="0", axis: App.Vector | None = None, angle: str | None = None):
    base, exprs = App.Vector(), {}
    for k, v in (("x", x), ("y", y), ("z", z)):
        try:
            setattr(base, k, float(str(v)))
        except ValueError:
            exprs[f".Placement.Base.{k}"] = str(v)
    rot = App.Rotation()
    if axis is not None:
        try:
            rot = App.Rotation(axis, float(str(angle)))
        except ValueError:
            rot = App.Rotation(axis, 1)          # sets the axis; the angle comes from the expression
            exprs[".Placement.Rotation.Angle"] = str(angle)
    obj.Placement = App.Placement(base, rot)
    for k, v in exprs.items():
        obj.setExpression(k, v)


def _set(obj, prop: str, value):
    v = str(value)
    try:
        setattr(obj, prop, float(v))
    except ValueError:
        obj.setExpression(prop, v)


def box(doc, name, l, w, h, x="0", y="0", z="0", axis=None, angle=None):
    """A box from its min corner (x, y, z) with sizes l (X), w (Y), h (Z), before rotation."""
    o = doc.addObject("Part::Box", name)
    _set(o, "Length", l)
    _set(o, "Width", w)
    _set(o, "Height", h)
    _place(o, x, y, z, axis, angle)
    return o


def cyl(doc, name, r, h, x="0", y="0", z="0", axis=None, angle=None):
    """A cylinder along +Z from (x, y, z), radius r, height h (then rotated about axis)."""
    o = doc.addObject("Part::Cylinder", name)
    _set(o, "Radius", r)
    _set(o, "Height", h)
    _place(o, x, y, z, axis, angle)
    return o


def cone(doc, name, r1, r2, h, x="0", y="0", z="0", axis=None, angle=None):
    o = doc.addObject("Part::Cone", name)
    _set(o, "Radius1", r1)
    _set(o, "Radius2", r2)
    _set(o, "Height", h)
    _place(o, x, y, z, axis, angle)
    return o


def hexprism(doc, name, circumradius, h, x="0", y="0", z="0", axis=None, angle=None):
    o = doc.addObject("Part::Prism", name)
    o.Polygon = 6
    _set(o, "Circumradius", circumradius)
    _set(o, "Height", h)
    _place(o, x, y, z, axis, angle)
    return o


def wedge(doc, name, xmin, xmax, ymin, ymax, zmin, zmax, x2min, x2max, z2min, z2max,
          x="0", y="0", z="0", axis=None, angle=None):
    """Part::Wedge: the face at Ymin spans X xmin..xmax, Z zmin..zmax; the face at Ymax
    spans X x2min..x2max, Z z2min..z2max. Good for tapers, ramps and frustums of boxes."""
    o = doc.addObject("Part::Wedge", name)
    for prop, v in (("Xmin", xmin), ("Xmax", xmax), ("Ymin", ymin), ("Ymax", ymax), ("Zmin", zmin),
                    ("Zmax", zmax), ("X2min", x2min), ("X2max", x2max), ("Z2min", z2min), ("Z2max", z2max)):
        _set(o, prop, v)
    _place(o, x, y, z, axis, angle)
    return o


def fuse(doc, name, objs):
    if len(objs) == 1:
        return objs[0]
    o = doc.addObject("Part::MultiFuse", name)
    o.Shapes = objs
    o.Refine = True
    for s in objs:
        s.Visibility = False
    return o


def cut(doc, name, base, tools):
    t = tools[0] if len(tools) == 1 else fuse(doc, name + "Cuts", tools)
    o = doc.addObject("Part::Cut", name)
    o.Base, o.Tool = base, t
    o.Refine = True
    base.Visibility = t.Visibility = False
    return o


def common(doc, name, a, b):
    o = doc.addObject("Part::Common", name)
    o.Base, o.Tool = a, b
    o.Refine = True
    a.Visibility = b.Visibility = False
    return o


def group(doc, name, objs):
    g = doc.addObject("App::DocumentObjectGroup", name)
    for o in objs:
        g.addObject(o)
    return g


def check(doc, names):
    doc.recompute()
    bad = [o.Name for o in doc.Objects if not o.isValid()]
    if bad:
        raise RuntimeError(f"{doc.Name}: invalid objects {bad}")
    for n in names:
        s = doc.getObject(n).Shape
        if s.isNull() or not s.isValid() or len(s.Solids) != 1:
            raise RuntimeError(f"{doc.Name}.{n}: not one valid solid ({len(s.Solids)} solids)")


def direction(edge):
    v = edge.Vertexes[-1].Point - edge.Vertexes[0].Point
    return v.normalize() if v.Length > 1e-9 else v


def mid(edge):
    return edge.valueAt((edge.FirstParameter + edge.LastParameter) / 2)


def _edges(base, pick):
    s = base.Shape
    def straight(e):
        try:
            return e.Curve.TypeId == "Part::GeomLine"
        except TypeError:          # blend curves left by an earlier fillet
            return False

    out = [i + 1 for i, e in enumerate(s.Edges) if straight(e) and pick(e, s)]
    if not out:
        raise RuntimeError(f"{base.Name}: no edges picked")
    return out


def fillet(doc, name, base, radius, pick):
    """Round the straight edges of `base` that pick(edge, shape) chooses. The edges are picked
    now, from the primitive as built; a box or wedge keeps its edge numbering when the sheet
    changes its sizes, so the fillet follows. The radius is fixed here."""
    o = doc.addObject("Part::Fillet", name)
    o.Base = base
    o.Edges = [(i, radius, radius) for i in _edges(base, pick)]
    base.Visibility = False
    return o


def chamfer(doc, name, base, size, pick):
    o = doc.addObject("Part::Chamfer", name)
    o.Base = base
    o.Edges = [(i, size, size) for i in _edges(base, pick)]
    base.Visibility = False
    return o
