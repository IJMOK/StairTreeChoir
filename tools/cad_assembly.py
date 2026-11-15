"""The whole setup as one FreeCAD assembly, linked to the masters (15 Nov 2026). Run by
tools/cad_export.py (python -m tools.cad), after the parts are exported.

  cad/stair-tree-complete.FCStd  one complete tree as it stands in the show: the tree, its 92
                               disks, pixels, tree box with every bought part, sockets and skis,
                               each an App::Link to its master (generated: don't edit it)
  cad/stair-tree-choir.FCStd   generated: don't edit it. Open it in FreeCAD to look round
                               the setup; every part is an App::Link to its master in
                               cad/parts/ (or to the generated tree), so it always shows the
                               masters as they are saved.
  cad/stair-tree-choir.step    one tree as it stands in the show, with its box, mounts and
                               disks, plus the Site A box: for NX or any viewer
  cad/previews/assembly-*.png  pictures
  cad/placements.json          where the box and sockets sit on the tree (for docs/tree-wiring.html)
  docs/cad-checks.md           clearances: screws against the pixel holes and the old stair
                               holes, the storage stack, tower clashes

World frame: mm, Z up, the ground at Z = 0, the show's front facing -Y (FreeCAD's front view).
  TreeUnit         one tree with everything screwed to it, in the tree's own frame (cad_tree.py)
  Show             6 trees (Site A) on their skis, 0.5m apart, and the site box
  Storage          14 trees face up in a stack on their towers
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import FreeCAD as App
import Part

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
for p in (str(ROOT), str(TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import cad_components  # noqa: E402
import cad_preview  # noqa: E402
import cad_tree  # noqa: E402

PARTS_DIR = ROOT / "cad" / "parts"
OUT = ROOT / "cad" / "stair-tree-choir.FCStd"
COMPLETE = ROOT / "cad" / "stair-tree-complete.FCStd"
STEP = ROOT / "cad" / "stair-tree-choir.step"
PREVIEW_DIR = ROOT / "cad" / "previews"
CHECKS = ROOT / "docs" / "cad-checks.md"
PLACEMENTS = ROOT / "cad" / "placements.json"

V = App.Vector
ROT0 = App.Rotation()
# The back ski half is the front one turned round a vertical axis through the tree's centre
# plane (socket frame: y vertical when standing, the centre plane at z = -15).
BACK = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), 180), V(0, 0, -15))
SHOW_TREES = 6
STORE_TREES = 14
SHOW_SPACING = 500

# Where things sit on the tree, in its frame (X right from the front, Y up, front face Z = 0).
# Bottom sockets: centred midway between base-row pixels, so their back-leg screws fall
# between pixel holes (the base row is every 30mm from x = 25.9).
SOCKET_BOTTOM_X = (55.9, 326.1)
PIXEL_FLANGE = (13.6, 1.0)        # bullet pixel flange: diameter, thickness proud of the disk
PIXEL_DOME = (12.0, 8.0)          # dome: diameter, height in front of the flange (Ray Wu listing)
PLUG_ABOVE_EDGE = 20              # the 12V run's SP17 plug ends at least this far above the tree's
                                  # bottom edge: off the wet grass, clear of the sockets and towers


def load(name):
    for d in App.listDocuments().values():
        if Path(d.FileName).resolve() == (PARTS_DIR / f"{name}.FCStd").resolve():
            return d
    doc = App.openDocument(str(PARTS_DIR / f"{name}.FCStd"))
    doc.recompute()
    return doc


def pl(x=0.0, y=0.0, z=0.0, rot=ROT0):
    return App.Placement(V(x, y, z), rot)


def link(doc, name, target, placement, parent=None, label=None):
    o = doc.addObject("App::Link", name)
    o.setLink(target)
    o.Placement = placement
    if label:
        o.Label = label
    if parent is not None:
        parent.addObject(o)
    return o


def feature(doc, name, shape, parent=None, label=None, colour=None):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if label:
        o.Label = label
    if parent is not None:
        parent.addObject(o)
    return o


def moved(shape, placement):
    s = shape.copy()
    s.Placement = placement.multiply(s.Placement)
    return s


# --------------------------------------------------------------------------- placements

def socket_placements(layout):
    """Socket frame -> tree frame. Bottom sockets point down (x -> -X, y -> -Y), the top
    one up."""
    h = layout["blank"]["height"]
    top_x = sum(x for x, y in layout["blank"]["polygon"] if y == 0) / 2
    bottom = [pl(x, 0, 0, App.Rotation(V(0, 0, 1), 180)) for x in SOCKET_BOTTOM_X]
    return bottom + [pl(top_x, h, 0)]


def box_to_tree(p, x, y):
    """Tree box frame -> tree frame, the box's z = 0 (cover bottom) at tree Y = y and the
    plate's left edge at tree X = x. Box x -> X, box y (away from the tree) -> -Z, z -> Y.
    The spacers put the plate's tree face spacer_l off the back face."""
    m = App.Matrix(1, 0, 0, x, 0, 0, 1, y, 0, -1, 0, -layout_t() - p["spacer_l"], 0, 0, 0, 1)
    return App.Placement(m)


_T = {}


def layout_t():
    return _T["t"]


def ear_screws(p, place):
    pts = []
    for x in (-p["ear_w"] / 2, p["box_w"] + p["ear_w"] / 2):
        for z in (p["mount_z0"], p["mount_z1"]):
            pts.append(place.multVec(V(x, -p["spacer_l"], z)))
    return pts


def nodes_xy(layout):
    h = layout["blank"]["height"]
    return [(n["x"], h - n["y"]) for n in layout["nodes"]]


def nearest(pt, nodes):
    return min(math.hypot(pt.x - x, pt.y - y) for x, y in nodes)


def place_tree_box(layout, p, drop):
    """Lowest, then leftmost spot on the node-1 side where the SP17 plug (hanging `drop`
    below the box's z = 0) ends PLUG_ABOVE_EDGE above the tree's bottom edge, all four ear
    screws keep 13mm (hole radius 7.5 + a 4mm screw + 3.5mm of oak) from every pixel hole,
    the old stair holes are clear and the box stays inside the outline."""
    nodes = nodes_xy(layout)
    old = [(h["x"], layout["blank"]["height"] - h["y"], h["dia"] / 2) for h in layout["blank"]["existing_holes"]]
    outline = cad_tree.outline(layout, 0, 1)
    for y in range(math.ceil(drop + PLUG_ABOVE_EDGE), 400):
        for x in range(30, 200):
            place = box_to_tree(p, x, y)
            screws = ear_screws(p, place)
            if any(nearest(s, nodes) < 13 for s in screws):
                continue
            if any(math.hypot(s.x - ox, s.y - oy) < r + 6 for s in screws for ox, oy, r in old):
                continue
            corners = [place.multVec(V(cx, 0, cz)) for cx in (-p["ear_w"], p["box_w"] + p["ear_w"])
                       for cz in (0, p["plate_top"])]
            if all(outline.isInside(V(c.x, c.y, -0.5), 0.01, True) for c in corners):
                return x, y, min(nearest(s, nodes) for s in screws)
    raise RuntimeError("no place for the tree box")


# --------------------------------------------------------------------------- geometry

def pixel_standins(layout):
    """The bullet pixels' flange and dome in front of the tree, for clearances."""
    out = []
    for x, y in nodes_xy(layout):
        f = Part.makeCylinder(PIXEL_FLANGE[0] / 2, PIXEL_FLANGE[1], V(x, y, 0))
        dome = Part.makeCylinder(PIXEL_DOME[0] / 2, PIXEL_DOME[1] - PIXEL_DOME[0] / 2, V(x, y, PIXEL_FLANGE[1]))
        cap = Part.makeSphere(PIXEL_DOME[0] / 2, V(x, y, PIXEL_FLANGE[1] + PIXEL_DOME[1] - PIXEL_DOME[0] / 2),
                              V(0, 0, 1), 0, 90)
        out += [f, dome, cap]
    return Part.makeCompound(out)


def site_box_standins():
    """Site A box contents, indicative (none of the layout is decided). DRiBOX frame:
    x along its 330, y across its 230 (front, the lid-seal side, at y = 0), z up from the floor.
    The floor is about 290 x 190 (x 20-310, y 20-210) because the walls taper: the PSU and
    hood fill the back, the fuse box and the Pi the front strip, the amp goes on the front
    wall above the fuse box and the Pi's buck pod on the hood."""
    items = {
        "DRiBOX (inside at the top)": (Part.makeBox(330, 230, 140), "#cfe3f7", 0.12),
        "usable floor (about 290 x 190)": (Part.makeBox(290, 190, 0.5, V(20, 20, -0.5)), "#9fb8cf", 0.5),
        "Blade fuse box (stand-in, PPFH-76ATO10 to measure)": (Part.makeBox(110, 60, 35, V(72, 24, 0)), "#444444", 1),
        "Pi 3 in its case (stand-in)": (Part.makeBox(85, 56, 22, V(190, 26, 0)), "#2e7d32", 1),
        "XH-M541 amp (stand-in, size to measure), on the front wall": (Part.makeBox(100, 25, 70, V(75, 20, 45)), "#7a4bb3", 1),
    }
    return items


# --------------------------------------------------------------------------- main

def main():
    layout = cad_tree.load_layout()
    _T["t"] = layout["blank"]["thickness"]
    tree_doc = App.openDocument(str(cad_tree.FCSTD))
    mounts, box, hood, pods, disk = (load(n) for n in ("tree-mounts", "tree-box", "psu-cover", "player-pods", "pixel-disk"))
    mp = json.loads((PARTS_DIR / "tree-mounts-params.json").read_text(encoding="utf-8"))
    bp = json.loads((PARTS_DIR / "tree-box-params.json").read_text(encoding="utf-8"))

    bought = App.openDocument(str(cad_components.BOUGHT_FCSTD))
    for name in ("stair_tree_complete", "stair_tree_choir"):
        if name in App.listDocuments():
            App.closeDocument(name)

    # ---- one complete tree, in its own file: everything on it linked to its master
    cdoc = App.newDocument("stair_tree_complete")
    cdoc.saveAs(str(COMPLETE))            # links to other files need the owner saved first
    unit = cdoc.addObject("App::Part", "TreeUnit")
    unit.Label = "Tree unit (tree frame)"
    link(cdoc, "Tree", tree_doc.getObject("Tree"), pl(), unit, "Tree (generated from the layout)")
    disks = cdoc.addObject("App::Part", "PixelDisks")
    disks.Label = "92 pixel disks"
    unit.addObject(disks)
    flip = App.Rotation(V(1, 0, 0), 180)
    for i, (x, y) in enumerate(nodes_xy(layout), 1):
        link(cdoc, f"Disk{i:02d}", disk.getObject("Disk"), pl(x, y, 0, flip), disks, f"pixel disk {i}")
    feature(cdoc, "Pixels", pixel_standins(layout), unit, "92 pixels (stand-ins: flange and dome)")
    sockets = socket_placements(layout)
    for i, s in enumerate(sockets):
        link(cdoc, f"Socket{i}", mounts.getObject("Socket"), s, unit, ["socket, bottom left", "socket, bottom right", "socket, top"][i])
    solids, locs, _ = cad_components.placed(bp)
    drop = -min(cad_components.moved(solids[n], l).BoundBox.ZMin for n, l in locs.items())
    bx, by, box_clear = place_tree_box(layout, bp, drop)
    bplace = box_to_tree(bp, bx, by)
    tb = cdoc.addObject("App::Part", "TreeBox")
    tb.Label = "Tree box"
    tb.Placement = bplace
    unit.addObject(tb)
    link(cdoc, "BoxBase", box.getObject("Base"), pl(), tb, "base")
    link(cdoc, "BoxCover", box.getObject("Cover"), pl(), tb, "cover")
    for name, l in locs.items():
        src = bought.getObject(cad_components.DUPLICATES.get(name, name))
        link(cdoc, f"Box_{name}", src, l, tb, f"{name} (bought part, stand-in)")
    lift = mp["ski_h"]
    stand = App.Rotation(V(1, 0, 0), 90)
    standing = cdoc.addObject("App::Part", "StairTree")
    standing.Label = f"Stair tree, standing on two skis ({lift:.0f}mm off the ground)"
    standing.Placement = pl(0, 0, lift, stand)
    link(cdoc, "Unit", unit, pl(), standing, "tree unit")
    unit.Visibility = False
    for j, s in enumerate(sockets[:2]):
        link(cdoc, f"Ski{j}", mounts.getObject("SkiHalf"), s, standing, "ski half, front")
        link(cdoc, f"SkiBack{j}", mounts.getObject("SkiHalf"), s.multiply(BACK), standing, "ski half, back")
    cdoc.recompute()
    cdoc.save()

    # ---- the whole setup links that tree unit
    doc = App.newDocument("stair_tree_choir")
    doc.saveAs(str(OUT))
    unit_c = unit
    unit = doc.addObject("App::Link", "TreeUnit")
    unit.setLink(unit_c)
    unit.Label = "Tree unit (from stair-tree-complete.FCStd)"
    unit.Visibility = False

    # ---- the show: tree frame -> world (tree Y up, front facing -Y), ground at z = 0
    show = doc.addObject("App::Part", "Show")
    show.Label = f"Show: Site A, {SHOW_TREES} trees on skis, and the site box"
    for k in range(SHOW_TREES):
        x0 = k * (layout["blank"]["width"] + SHOW_SPACING)
        t = doc.addObject("App::Part", f"ShowTree{k + 1}")
        t.Label = f"tree in slot {k + 1}"
        t.Placement = pl(x0, 0, lift, stand)
        show.addObject(t)
        link(doc, f"ShowUnit{k + 1}", unit, pl(), t, "tree unit")
        for j, s in enumerate(sockets[:2]):
            link(doc, f"Ski{k + 1}_{j}", mounts.getObject("SkiHalf"), s, t, "ski half, front")
            link(doc, f"SkiBack{k + 1}_{j}", mounts.getObject("SkiHalf"), s.multiply(BACK), t, "ski half, back")
    sb = doc.addObject("App::Part", "SiteBox")
    sb.Label = "Site A box (layout indicative)"
    sb.Placement = pl(-900, -100, 0)
    show.addObject(sb)
    psu_at = pl(20 + 53, 230 - 20 - 118.5, 0)                 # PSU frame in the box: hood end at x = 20
    link(doc, "Hood", hood.getObject("Hood"), psu_at, sb, "PSU hood with IEC inlet")
    link(doc, "Psu", hood.getObject("RefPsu"), psu_at, sb, "LRS-350-12")
    link(doc, "Iec", hood.getObject("RefIecFlange"), psu_at, sb, "IEC inlet flange")
    buck_at = pl(160, 150, 63)                                # on the hood's roof, 12V side
    link(doc, "BuckBase", pods.getObject("BuckBase"), buck_at, sb, "buck pod (on the hood)")
    link(doc, "BuckLid", pods.getObject("BuckLid"), buck_at, sb, "buck pod lid")
    standins = site_box_standins()
    for i, (label, (shape, colour, alpha)) in enumerate(standins.items()):
        feature(doc, f"SiteItem{i}", shape, sb, label)

    # ---- the show, raised: a tower lying between each bottom socket and its ski
    riser = pl(0, mp["y_out"], 0)
    lift_hi = lift + mp["y_out"]
    raised = doc.addObject("App::Part", "ShowRaised")
    raised.Label = "Show, raised: towers as risers between socket and ski"
    raised.Placement = pl(0, 1500, lift_hi, stand)
    link(doc, "RaisedUnit", unit, pl(), raised, "tree unit")
    for j, s in enumerate(sockets[:2]):
        link(doc, f"RaisedTower{j}", mounts.getObject("Tower"), s, raised, "tower (riser)")
        link(doc, f"RaisedSki{j}", mounts.getObject("SkiHalf"), s.multiply(riser), raised, "ski half, front")
        link(doc, f"RaisedSkiBack{j}", mounts.getObject("SkiHalf"), s.multiply(riser).multiply(BACK), raised, "ski half, back")

    # ---- storage: trees face up, stacked on their towers
    store = doc.addObject("App::Part", "Storage")
    store.Label = f"Storage: {STORE_TREES} trees stacked on towers"
    z_bottom = mp["tree_t"] + mp["below"]
    for k in range(STORE_TREES):
        t = doc.addObject("App::Part", f"StoreTree{k + 1}")
        t.Placement = pl(-2000, 0, z_bottom + k * mp["pitch"])
        store.addObject(t)
        link(doc, f"StoreUnit{k + 1}", unit, pl(), t, "tree unit")
        for j, s in enumerate(sockets):
            link(doc, f"Tower{k + 1}_{j}", mounts.getObject("Tower"), s, t, "tower")

    doc.recompute()
    doc.save()

    # ---- checks and pictures, from the source shapes with the same placements
    tree = tree_doc.getObject("Tree").Shape
    sock, half, tower = (mounts.getObject(n).Shape for n in ("Socket", "SkiHalf", "Tower"))
    ski = Part.makeCompound([half, moved(half, BACK)])        # one foot's pair of halves, in the socket frame
    pix = pixel_standins(layout)
    base, cover = box.getObject("Base").Shape, box.getObject("Cover").Shape
    box_parts = [moved(base, bplace), moved(cover, bplace)] + [
        moved(cad_components.moved(solids[n], l), bplace) for n, l in locs.items()]
    socks = [moved(sock, s) for s in sockets]
    disk_shape = disk.getObject("Disk").Shape
    disks_placed = [moved(disk_shape, pl(x, y, 0, flip)) for x, y in nodes_xy(layout)]
    bbb = Part.makeCompound(box_parts[:2]).BoundBox
    placements = {
        "_comment": "Generated by tools/cad_assembly.py: where things sit on the tree, tree frame (mm, X right "
                    "from the front, Y up from the bottom edge). Read by tools/gen_tree_wiring.py.",
        "tree_box": {"plate_left_x": bx, "cover_bottom_y": by,
                     "footprint": [round(bbb.XMin, 1), round(bbb.YMin, 1), round(bbb.XMax, 1), round(bbb.YMax, 1)],
                     "ear_screws": [[round(q.x, 1), round(q.y, 1)] for q in ear_screws(bp, bplace)]},
        "sockets": [{"x": round(s.Base.x, 1), "y": round(s.Base.y, 1), "points": "down" if s.Base.y < 1 else "up",
                     "width": mp["dt_tip"], "leg_h": mp["leg_h"], "depth": mp["dt_h"],
                     "screws": [[round(s.multVec(V(sx, mp["screw_y"], 0)).x, 1), round(s.multVec(V(sx, mp["screw_y"], 0)).y, 1)]
                                for sx in (-mp["screw_x"], mp["screw_x"], -mp["front_x"], mp["front_x"])]} for s in sockets],
    }
    PLACEMENTS.write_text(json.dumps(placements, indent=1) + "\n", encoding="utf-8", newline="\n")
    results = checks(layout, mp, bp, tree, socks, sockets, box_parts, pix, tower, ski, bx, by, box_clear)
    CHECKS.write_text(checks_doc(results), encoding="utf-8", newline="\n")
    print("\n".join(results))

    # pictures
    wood = "#c8a26b"
    unit_items = [(tree, wood), (Part.makeCompound(socks), "#3b7dd8"), (pix, "#f5f5f5"),
                  (Part.makeCompound(box_parts[:1] + box_parts[2:]), "#4682b4"), (box_parts[1], "#b0c4de", 0.5)]
    shown = [(moved(s, App.Placement(V(0, 0, lift), stand)), c, *a) for s, c, *a in
             unit_items + [(Part.makeCompound([moved(ski, s) for s in sockets[:2]]), "#d88a3b")]]
    cad_preview.render(shown, str(PREVIEW_DIR / "assembly-show-tree.png"), elev=12, azim=-70,
                       title=f"in the show: on two skis ({lift:.0f}mm up)", size=(6, 7), deflection=2.0)
    cad_preview.render(shown, str(PREVIEW_DIR / "assembly-complete-back.png"), elev=15, azim=110,
                       title="the complete tree from behind: box, sockets, skis", size=(6, 7), deflection=2.0)
    riser = pl(0, mp["y_out"], 0)
    hi = App.Placement(V(0, 0, lift + mp["y_out"]), stand)
    shown_hi = [(moved(s, hi), c, *a) for s, c, *a in
                unit_items + [(Part.makeCompound([moved(tower, s) for s in sockets[:2]]), "#5aa05a"),
                              (Part.makeCompound([moved(ski, s.multiply(riser)) for s in sockets[:2]]), "#d88a3b")]]
    cad_preview.render(shown_hi, str(PREVIEW_DIR / "assembly-show-raised.png"), elev=12, azim=-70,
                       title=f"raised: towers as risers ({lift + mp['y_out']:.0f}mm up)", size=(6, 7), deflection=2.0)
    stack = []
    for k in range(3):
        place = pl(0, 0, z_bottom + k * mp["pitch"])
        stack += [(moved(tree, place), wood), (moved(Part.makeCompound([moved(tower, s) for s in sockets]), place), "#5aa05a"),
                  (moved(Part.makeCompound(box_parts), place), "#4682b4"), (moved(pix, place), "#f5f5f5")]
    cad_preview.render(stack, str(PREVIEW_DIR / "assembly-storage.png"), elev=8, azim=-25,
                       title="storage: 3 of the 14, face up on towers", size=(7, 6), deflection=3.0)
    site = [(moved(hood.getObject("Hood").Shape, psu_at), "#d9d9d9"), (moved(hood.getObject("RefPsu").Shape, psu_at), "#666666"),
            (moved(hood.getObject("RefIecFlange").Shape, psu_at), "#222222"),
            (moved(pods.getObject("BuckBase").Shape, pl(160, 150, 63)), "#7a9cc6")]
    site += [(s, c, a) for s, c, a in standins.values()]
    cad_preview.render(site, str(PREVIEW_DIR / "assembly-site-box.png"), elev=35, azim=-60,
                       title="Site A box (indicative layout)", size=(7, 5))

    # STEP: one tree as it stands, and the site box
    import Import
    step_doc = App.newDocument("choir_step")
    objs = []
    for name, s in (("tree", tree), ("pixel_disks", Part.makeCompound(disks_placed)), ("sockets", Part.makeCompound(socks)),
                    ("skis", Part.makeCompound([moved(ski, s) for s in sockets[:2]])),
                    ("tree_box", Part.makeCompound(box_parts))):
        o = step_doc.addObject("Part::Feature", name)
        o.Shape = moved(s, App.Placement(V(0, 0, lift), stand))
        objs.append(o)
    for name, s in (("site_box_hood", hood.getObject("Hood").Shape), ("site_box_psu", hood.getObject("RefPsu").Shape)):
        o = step_doc.addObject("Part::Feature", name)
        o.Shape = moved(moved(s, psu_at), pl(-900, -100, 0))
        objs.append(o)
    Import.export(objs, str(STEP))
    from cad_export import scrub
    scrub(STEP)
    App.closeDocument(step_doc.Name)
    App.closeDocument(doc.Name)
    App.closeDocument(cdoc.Name)
    print(f"wrote {COMPLETE.relative_to(ROOT)}, {OUT.relative_to(ROOT)}, {STEP.relative_to(ROOT)}, {CHECKS.relative_to(ROOT)}, cad/previews/assembly-*.png")


def checks(layout, mp, bp, tree, socks, sockets, box_parts, pix, tower, ski, bx, by, box_clear):
    out = []
    nodes = nodes_xy(layout)
    t = layout["blank"]["thickness"]
    pr = layout["params"]
    # socket screws on the back face
    worst, front = [], []
    for s in sockets:
        for sx in (-mp["screw_x"], mp["screw_x"]):
            worst.append(nearest(s.multVec(V(sx, mp["screw_y"], -t)), nodes))
        for sx in (-mp["front_x"], mp["front_x"]):
            front.append(nearest(s.multVec(V(sx, mp["screw_y"], 0)), nodes))
    hole_r = pr["clearance_dia"] / 2
    cb_r = pr["front_counterbore_dia"] / 2
    out.append(f"Socket front screws (2 per socket, 4 × 16 into the front face beside the legs): nearest pixel centre "
               f"{min(front):.1f}mm away, {min(front) - cb_r - mp['screw_d'] / 2:.1f}mm of oak to its counterbore. "
               + ("OK." if min(front) - cb_r - mp["screw_d"] / 2 >= 3 else "**Too close.**"))
    out.append(f"Socket back screws (2 per socket, 4 × 16 into the back face, {16 - mp['wall']:.0f}mm into the oak; "
               f"the front pair is offset {mp['screw_x'] - mp['front_x']:.0f}mm along the edge and each goes "
               f"{16 - mp['wall']:.0f}mm in, so they can't meet in the {t:.0f}mm): nearest pixel hole centre {min(worst):.1f}mm away, so "
               f"{min(worst) - hole_r - mp['screw_d'] / 2:.1f}mm of oak to the clearance hole. "
               f"They sit {abs(mp['screw_y']):.0f}mm in from the edge; the pixel leads run between holes "
               f"{pr['edge_inset']:.0f}mm in. " + ("OK." if min(worst) - hole_r - mp["screw_d"] / 2 >= 3 else "**Too close.**"))
    old = [(h["name"], h["x"], layout["blank"]["height"] - h["y"], h["dia"] / 2) for h in layout["blank"]["existing_holes"]]
    near_old = min(math.hypot(s.multVec(V(sx, mp["screw_y"], 0)).x - ox, s.multVec(V(sx, mp["screw_y"], 0)).y - oy) - r
                   for s in sockets for sx in (-mp["screw_x"], mp["screw_x"], -mp["front_x"], mp["front_x"])
                   for _, ox, oy, r in old)
    out.append(f"Socket screws to the old stair holes: {near_old:.1f}mm at the nearest. "
               + ("OK." if near_old > 5 else "**Too close.**"))
    # legs against the counterbores (front) and holes
    cb = Part.makeCompound([Part.makeCylinder(pr["front_counterbore_dia"] / 2, t, V(x, y, -t)) for x, y in nodes])
    leg_gap = min(s.distToShape(cb)[0] for s in socks)
    out.append(f"Socket legs to the nearest pixel counterbore: {leg_gap:.1f}mm. " + ("OK." if leg_gap > 1 else "**Too close.**"))
    clash = sum(s.common(tree).Volume for s in socks)
    out.append(f"Sockets against the tree: {clash:.1f} mm³ of overlap. " + ("OK." if clash < 1 else "**Clash.**"))
    # tree box
    out.append(f"Tree box: plate's left edge at X = {bx}mm, cover bottom at Y = {by}mm (from the tree's bottom-left), "
               f"node 1's side. Its ear screws are {box_clear:.1f}mm from the nearest pixel hole centre. "
               "Placed by search (tools/cad_assembly.py place_tree_box): mark the real position from the tree.")
    bb = Part.makeCompound(box_parts).BoundBox
    out.append(f"Tree box stands {-bb.ZMin - t:.0f}mm off the back face, the pixels {pix.BoundBox.ZMax:.0f}mm "
               f"proud of the front (flange {PIXEL_FLANGE[1]:g} + dome {PIXEL_DOME[1]:g}, from the listing).")
    # the SP16 plug hanging below the box
    low = bb.YMin
    out.append(f"Lowest point of the box (the SP17 plug on the SP16): {low:.0f}mm above the tree's bottom edge, "
               f"{low + mp['ski_h']:.0f}mm above the ground in the show; the cable bends below it.")
    plug_hit = sum(Part.makeCompound(box_parts).common(s).Volume for s in socks)
    out.append(f"Tree box against the sockets: {plug_hit:.1f} mm³. " + ("OK." if plug_hit < 1 else "**Clash.**"))
    # storage
    p = mp["pitch"]
    gap = (p + bb.ZMin) - pix.BoundBox.ZMax
    out.append(f"Storage pitch {p:.0f}mm: the box under each tree clears the pixels of the tree below by {gap:.1f}mm. "
               + ("OK." if gap > 5 else "**Too tight.**"))
    zt = -(mp["tree_t"] + mp["below"])
    out.append(f"Storage stack of {STORE_TREES}: {(STORE_TREES - 1) * p + p + mp['spig_h']:.0f}mm tall to the top spigot; "
               f"each tower drops {mp['spig_h']:.0f}mm into the one above. The bottom towers stand on the floor.")
    towers = [moved(tower, s) for s in sockets]
    tw_clash = sum(tt.common(tree).Volume + tt.common(Part.makeCompound(box_parts)).Volume for tt in towers)
    above = Part.makeCompound([moved(x, pl(0, 0, p)) for x in [tree] + box_parts])
    tw_up = sum(tt.common(above).Volume for tt in towers)
    out.append(f"Towers against the tree and its box: {tw_clash:.1f} mm³; against the tree above: {tw_up:.1f} mm³. "
               + ("OK." if tw_clash + tw_up < 1 else "**Clash.**"))
    ok_bottom = zt <= bb.ZMin
    out.append(f"Tower bottoms are {-zt - t:.0f}mm below the back face; the box reaches {-bb.ZMin - t:.0f}mm: "
               + ("the towers carry the stack, not the boxes." if ok_bottom else "**the box hits the floor first.**"))
    # show
    out.append(f"Show: the tree's bottom edge stands {mp['ski_h']:.0f}mm above the ground on two feet "
               f"{SOCKET_BOTTOM_X[1] - SOCKET_BOTTOM_X[0]:.0f}mm apart, each two ski halves covering "
               f"{ski.BoundBox.ZLength:.0f}mm front to back (each half {mp['half_l'] - mp['butt_gap']:.0f}mm; a whole set prints on one 256 bed). "
               "They slide onto the sockets' dovetail rails from front and back; the stakes lock them.")
    riser = pl(0, mp["y_out"], 0)
    skis_hi = [moved(ski, s.multiply(riser)) for s in sockets[:2]]
    risers = [moved(tower, s) for s in sockets[:2]]
    hit = sum(r.common(tree).Volume + r.common(Part.makeCompound(box_parts)).Volume + r.common(sk).Volume
              for r, sk in zip(risers, skis_hi)) + sum(sk.common(tree).Volume for sk in skis_hi)
    out.append(f"Show, raised: a tower lying between each bottom socket and its ski lifts the bottom edge to "
               f"{mp['ski_h'] + mp['y_out']:.0f}mm. Risers against the tree, its box and the skis: "
               f"{hit:.1f} mm³. " + ("OK." if hit < 1 else "**Clash.**"))
    return out


def checks_doc(results):
    return "\n".join(["# CAD checks", "",
                      "Generated by `python -m tools.cad` (tools/cad_assembly.py) from the masters in cad/parts/ and "
                      "data/tree-layout.json. Every number is from the models: change a master, re-export, read this again.",
                      "", *[f"- {r}" for r in results], ""])
