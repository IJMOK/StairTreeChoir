"""Exports everything from the FreeCAD masters: one command for all the CAD (15 Nov 2026).

  python -m tools.cad            (finds freecadcmd and runs this; or, by hand, from the repo root:)
  freecadcmd -c "import sys; sys.path[:0] = ['.', 'tools']; import cad_export; cad_export.main()"

In order:
  1. the tread from data/tree-layout.json        tools/cad_tree.py   -> cad/tree/ (stair-tree.FCStd, CAM STEPs)
  2. every printed part from its master           cad/parts/*.FCStd   -> print/*.stl (laid out for the bed),
                                                                         cad/printed/*.step (as fitted),
                                                                         cad/previews/*.png
  3. the tree box's bought parts and fit checks   tools/cad_components.py -> cad/components/, docs/tree-box-parts.md
  4. the whole setup                              tools/cad_assembly.py -> cad/stair-tree-choir.FCStd (+ .step, pictures)

Save a master in FreeCAD before running this: it reads the files on disk. Each export
recomputes the master and stops if any feature is broken or a part isn't one solid.
"""

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
for p in (str(ROOT), str(TOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import cad_preview  # noqa: E402

PARTS_DIR = ROOT / "cad" / "parts"
PRINT_DIR = ROOT / "print"
STEP_DIR = ROOT / "cad" / "printed"
PREVIEW_DIR = ROOT / "cad" / "previews"
LINEAR, ANGULAR = 0.01, math.radians(3)     # finer than a 0.4 nozzle can show

RX = App.Vector(1, 0, 0)
RY = App.Vector(0, 1, 0)


@dataclass
class Out:
    """One printed part: the bodies it is made of, how it lies on the bed, its file names."""
    master: str
    bodies: list[str]
    stl: str | None                     # print/<stl>.stl
    step: str | None = None             # cad/printed/<step>.step
    rot: tuple = ()                     # (axis, degrees) applied before dropping onto the bed
    colour: str = "#8fb3d9"
    count: str = ""                     # how many to print, for print/README.md
    notes: str = ""
    extra: dict = field(default_factory=dict)


OUTS = [
    # tree box (Rob, 31 Oct 2026): base tree face down, cover back down
    Out("tree-box", ["Base"], "tree-box-base", "tree-box-base", (RX, 90), "#4682b4", "1 per tree",
        "PETG, tree face on the bed, no supports"),
    Out("tree-box", ["Cover"], "tree-box-cover", "tree-box-cover", (RX, -90), "#b0c4de", "1 per tree",
        "PETG, back on the bed, no supports"),
    Out("tree-box", ["Spacer"], "tree-box-spacer", None, (), "#4682b4", "4 per tree", "10mm tube, either end down"),
    Out("tree-box", ["Coupon"], "tree-box-coupon", None, (), "#999999", "1, first",
        "fit test: SP16, PG7, RP-SMA, M3 and M2 inserts"),
    Out("tree-box", ["SealStrip", "SealBar"], "tree-box-seal-test", None, (), "#999999", "1, first",
        "the cord squeeze from the hook and one screw"),
    # tree mounts (Rob, 15 Nov 2026)
    Out("tree-mounts", ["Socket"], "tree-socket", "tree-socket", (RX, -90), "#3b7dd8", "3 per tree",
        "PETG, rail down (its wide face on the bed), legs up, no supports, 4 walls, 40% infill; v2: crush ribs grip the "
        "tread, two 5mm countersunk screws up into the edge (5 x 45 bottom, 5 x 35 top) through the jig's pilots"),
    Out("tree-mounts", ["Tower"], "tree-tower", "tree-tower", (RX, -90), "#5aa05a", "3 per tree (storage)",
        "PETG, on its back, 3 walls, 15% infill, support on the build plate only, under the latch tongue (snap it out "
        "through the window); a tree lying face up drops onto its three and clicks in, "
        "and each tab drops into the pocket of the tower above. Six to a plate: tower-plate.3mf"),
    Out("tree-mounts", ["Stand"], "tree-stand", "tree-stand", (), "#d88a3b", "2 per tree (show)",
        "PETG, upright (back end down), no supports, 3 walls, 15% infill; slides onto a bottom socket from the "
        "front and clicks home on its latch, a tent pole through it"),
    Out("tree-mounts", ["PoleCap"], "tree-pole-cap", "tree-pole-cap", (RX, -90), "#d88a3b", "4 per tree (show)",
        "PETG, sole on the bed, no supports, 4 walls, 40% infill; one on each end of each pole (crush ribs grip it), "
        "a peg (up to 9mm) through it at 45 deg, its tip under the tree"),
    Out("tree-mounts", ["DovetailCoupon"], "tree-dovetail-coupon", None, (), "#d88a3b", "1, first",
        "the back 30mm of a stand's slot block, its stop and latch: try the slide (`clr`) and the click on one socket's rail; "
        "try a pole in a cap (`cap_rib_id`)"),
    Out("tree-mounts", ["DrillJig"], "tree-drill-jig", "tree-drill-jig", (RX, -90), "#999999", "1 (or 2)",
        "PETG, base on the bed, no supports, 4 walls, 40% infill: drop it over the edge with its hole on the pixel "
        "straight above the socket, clamp, drill the two 3.5mm pilots about 45 deep"),
    # site box
    Out("psu-cover", ["Hood"], "psu-hood", "psu-hood", (RY, -90), "#d9d9d9", "1 for Site A",
        "PETG, end wall on the bed, no supports, 4 walls, 40% infill: it carries mains"),
    Out("psu-cover-lrs", ["Hood"], "psu-hood-lrs", "psu-hood-lrs", (RY, -90), "#c8c8c8", "1 if Site A runs on the LRS-350-12",
        "PETG, end wall on the bed, no supports, 4 walls, 40% infill: it carries mains"),
    Out("player-pods", ["BuckBase"], "pod-buck-base", "pod-buck-base", (), "#7a9cc6", "1 per site",
        "floor on the bed, no supports"),
    Out("player-pods", ["BuckLid"], "pod-buck-lid", "pod-buck-lid", (RX, 180), "#a9c1de", "1 per site",
        "plate on the bed, clips up"),
    # CNC and pixels
    Out("pixel-disk", ["Disk"], "pixel-disk", "pixel-disk", (), "#333333", "92 per tree",
        "PETG, front face on the bed, no supports, 100% infill"),
    Out("step-clamp", ["Clamp"], "step-clamp", "step-clamp", (RX, -90), "#aa5555", "4",
        "PETG, on its side as exported, 4 walls, 40% infill"),
    Out("step-clamp", ["Washer"], "step-clamp-washer", "step-clamp-washer", (), "#555555", "4", "flat"),
]


def scrub(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"FILE_NAME\('[^']*','[^']*'", f"FILE_NAME('{path.name}','2026-01-01T00:00:00'", text, count=1)
    text = re.sub(r"Open CASCADE STEP translator [\d.]+ \d+", path.stem, text)
    path.write_text(text, encoding="utf-8", newline="\n")


def params(doc) -> dict[str, float]:
    sheet = doc.getObject("params")
    out = {}
    for row in range(2, 500):
        a = sheet.getAlias(f"B{row}")
        if a:
            out[a] = sheet.get(a)
    return out


def open_master(name: str):
    doc = App.openDocument(str(PARTS_DIR / f"{name}.FCStd"))
    doc.recompute()
    broken = [o.Name for o in doc.Objects if not o.isValid()]
    if broken:
        raise RuntimeError(f"{name}: broken features {broken}")
    return doc


def on_bed(shape, rot):
    s = shape.copy()
    if rot:
        s.rotate(App.Vector(), rot[0], rot[1])
    bb = s.BoundBox
    s.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
    return s


def export_part(doc, o: Out) -> dict:
    shapes = [doc.getObject(b).Shape for b in o.bodies]
    for b, s in zip(o.bodies, shapes):
        if s.isNull() or not s.isValid() or len(s.Solids) != 1:
            raise RuntimeError(f"{o.master}.{b}: not one valid solid")
    shape = Part.makeCompound(shapes) if len(shapes) > 1 else shapes[0]
    info = {"master": o.master, "bodies": o.bodies, "volume_cm3": round(sum(s.Volume for s in shapes) / 1000, 1)}
    if o.stl:
        placed = on_bed(shape, o.rot)
        mesh = MeshPart.meshFromShape(Shape=placed, LinearDeflection=LINEAR, AngularDeflection=ANGULAR, Relative=False)
        if not mesh.isSolid() or mesh.hasNonManifolds():
            raise RuntimeError(f"{o.stl}: the mesh isn't a closed solid")
        mesh.write(str(PRINT_DIR / f"{o.stl}.stl"))
        bb = placed.BoundBox
        info["bed_mm"] = [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)]
        cad_preview.render([(placed, o.colour)], str(PREVIEW_DIR / f"{o.stl}.png"), title=f"{o.stl} (as printed)",
                           size=(5, 4))
    if o.step:
        path = STEP_DIR / f"{o.step}.step"
        shape.exportStep(str(path))
        scrub(path)
    return info


PLATE = 255          # the P1S's usable bed, mm (Rob: a full set for one tree on one plate)
BED = 256            # the P1S's bed (Bambu preset printable_area); Bambu Studio centres the plate on it
EXCLUDE = (18, 28)   # the P1S's bed_exclude_area, front left: kept clear for the filament cutter (Rob)
GAP = 2.5            # between parts on the plate


def check_plate(parts):
    """No two parts touching, and nothing in the P1S's excluded corner once Bambu Studio centres
    the plate on the bed. Returns the layout's size."""
    for i, a in enumerate(parts):
        for b in parts[i + 1:]:
            if a.distToShape(b)[0] < GAP - 0.05:
                raise RuntimeError("plate: parts overlap")
    bb = Part.makeCompound(parts).BoundBox
    ox, oy = (BED - bb.XLength) / 2 - bb.XMin, (BED - bb.YLength) / 2 - bb.YMin
    corner = Part.makeBox(EXCLUDE[0], EXCLUDE[1], 300, App.Vector(-ox, -oy, -1))
    if any(p.common(corner).Volume > 0 for p in parts):
        raise RuntimeError("plate: a part lands in the P1S's excluded corner")
    if bb.XLength > PLATE or bb.YLength > PLATE:
        raise RuntimeError(f"plate needs {bb.XLength:.0f} x {bb.YLength:.0f}mm: more than the {PLATE}mm plate")
    return bb.XLength, bb.YLength


def _at(shape, x, y):
    c = shape.copy()
    c.translate(App.Vector(x, y, 0))
    return c


def tree_plate(doc):
    """One tree's show set on one plate: the 3 sockets in a row across the front (clear of the
    P1S's excluded corner), the 2 display stands upright behind them and the 4 pole caps in a
    2 x 2 block beside the stands."""
    sock = on_bed(doc.getObject("Socket").Shape, (RX, -90))
    stand = on_bed(doc.getObject("Stand").Shape, ())
    cap = on_bed(doc.getObject("PoleCap").Shape, (RX, -90))
    sb, tb, cb = sock.BoundBox, stand.BoundBox, cap.BoundBox
    parts = [_at(sock, EXCLUDE[0] + GAP + i * (sb.XLength + GAP), 0) for i in range(3)]
    y2 = sb.YLength + GAP
    parts += [_at(stand, i * (tb.XLength + GAP), y2) for i in range(2)]
    x_caps = 2 * (tb.XLength + GAP)
    parts += [_at(cap, x_caps + (i % 2) * (cb.XLength + GAP), y2 + (i // 2) * (cb.YLength + GAP)) for i in range(4)]
    return parts, check_plate(parts)


def tower_plate(doc):
    """Two trees' storage towers (6) on their backs on one plate (v2, Rob 17 Nov 2026): four
    side by side along the back, clear of the excluded corner, and two turned across in front."""
    tower = on_bed(doc.getObject("Tower").Shape, (RX, -90))
    across = on_bed(tower, (App.Vector(0, 0, 1), 90))
    b, a = tower.BoundBox, across.BoundBox
    y_back = 2 * (a.YLength + GAP)
    parts = [_at(tower, EXCLUDE[0] + GAP + i * (b.XLength + GAP), y_back) for i in range(4)]
    parts += [_at(across, EXCLUDE[0] + GAP + 40, j * (a.YLength + GAP)) for j in range(2)]
    return parts, check_plate(parts)


PLATE_NAMES = [*(f"socket-{i}" for i in range(1, 4)), *(f"stand-{i}" for i in range(1, 3)),
               *(f"pole-cap-{i}" for i in range(1, 5))]


def write_3mf(path: Path, named_shapes) -> None:
    """A plain 3MF with one mesh object per part, each where it sits on the plate. Bambu Studio
    keeps them as separate objects (so each is checked against the P1S's excluded corner on its
    own, and any can be skipped), where a single STL is one object whose box covers the corner."""
    import zipfile
    objs = []
    for i, (name, shape) in enumerate(named_shapes, 1):
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=LINEAR, AngularDeflection=ANGULAR, Relative=False)
        pts, facets = mesh.Topology
        v = "".join(f'<vertex x="{q.x:.4f}" y="{q.y:.4f}" z="{q.z:.4f}"/>' for q in pts)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in facets)
        objs.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{v}</vertices>'
                    f'<triangles>{t}</triangles></mesh></object>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + "".join(objs)
             + "</resources><build>" + "".join(f'<item objectid="{i}"/>' for i in range(1, len(objs) + 1))
             + "</build></model>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)


def write_print_readme(infos: list[tuple[Out, dict]]) -> None:
    lines = ["# Print files", "",
             "Everything to print, laid out for the bed (Bambu P1S). Generated by `python -m tools.cad` from the "
             "FreeCAD masters in [cad/parts/](../cad/parts/): don't edit these, change the master and re-export "
             "([cad/README.md](../cad/README.md)).", "",
             "| File | From | How many | Size on the bed (mm) | Solid volume | Print it |",
             "|---|---|---|---|---|---|"]
    for o, info in infos:
        if not o.stl:
            continue
        x, y, z = info["bed_mm"]
        ext = "3mf" if o.stl == "tower-plate" else "stl"
        lines.append(f"| [{o.stl}.{ext}]({o.stl}.{ext}) | `{o.master}.FCStd` {' + '.join(o.bodies)} | {o.count} | "
                     f"{x:g} × {y:g} × {z:g} | {info['volume_cm3']:g} cm³ | {o.notes} |")
    lines += ["", "Solid volume is the part with no infill; the slicer gives the real weight.",
              "Previews of every part: [cad/previews/](../cad/previews/).", ""]
    old = (PRINT_DIR / "README.md").read_text(encoding="utf-8") if (PRINT_DIR / "README.md").exists() else ""
    start, end = "<!-- sliced -->", "<!-- /sliced -->"
    if start in old and end in old:          # the section tools/slice.py writes: keep it
        lines += [old[old.index(start):old.index(end) + len(end)], ""]
    (PRINT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main(parts: bool = True, tree: bool = True, components: bool = True, assembly: bool = True) -> None:
    for d in (PRINT_DIR, STEP_DIR, PREVIEW_DIR):
        d.mkdir(parents=True, exist_ok=True)
    if tree:
        import cad_tree
        cad_tree.main()
    if parts:
        infos, docs = [], {}
        for o in OUTS:
            if o.master not in docs:
                docs[o.master] = open_master(o.master)
            info = export_part(docs[o.master], o)
            infos.append((o, info))
            print(f"{o.stl or o.step}: {info['volume_cm3']} cm3" + (f", bed {info['bed_mm']}" if "bed_mm" in info else ""))
        parts_, (px, py) = tree_plate(docs["tree-mounts"])
        plate = Part.makeCompound(parts_)
        mesh = MeshPart.meshFromShape(Shape=plate, LinearDeflection=LINEAR, AngularDeflection=ANGULAR, Relative=False)
        mesh.write(str(PRINT_DIR / "tree-plate.stl"))
        write_3mf(PRINT_DIR / "tree-plate.3mf", list(zip(PLATE_NAMES, parts_)))
        cad_preview.render([(plate, "#d88a3b")], str(PREVIEW_DIR / "tree-plate.png"), elev=60, azim=-90,
                           title=f"one tree's show set on one plate: {px:.0f} x {py:.0f}mm of {PLATE}", size=(5, 5))
        infos.append((Out("tree-mounts", ["3 Socket + 2 Stand + 4 PoleCap"], "tree-plate", None, (), "#d88a3b", "1 per tree",
                          "PETG, as laid out: one tree's show set (3 sockets, 2 display stands, 4 pole caps) on one plate"),
                      {"volume_cm3": round(plate.Volume / 1000, 1), "bed_mm": [round(px, 1), round(py, 1),
                                                                               round(plate.BoundBox.ZLength, 1)]}))
        print(f"tree-plate: {px:.0f} x {py:.0f}mm")
        towers, (tx, ty) = tower_plate(docs["tree-mounts"])
        tplate = Part.makeCompound(towers)
        write_3mf(PRINT_DIR / "tower-plate.3mf", [(f"tower-{i}", t) for i, t in enumerate(towers, 1)])
        cad_preview.render([(tplate, "#5aa05a")], str(PREVIEW_DIR / "tower-plate.png"), elev=50, azim=-70,
                           title=f"two trees' storage towers on one plate: {tx:.0f} x {ty:.0f}mm", size=(5, 4))
        infos.append((Out("tree-mounts", ["6 Tower"], "tower-plate", None, (), "#5aa05a", "1 per 2 trees",
                          "PETG, as laid out (3MF, six objects): two trees' storage towers"),
                      {"volume_cm3": round(tplate.Volume / 1000, 1), "bed_mm": [round(tx, 1), round(ty, 1),
                                                                                round(tplate.BoundBox.ZLength, 1)]}))
        # sizes the other tools read
        for name in ("tree-box", "tree-mounts", "psu-cover", "psu-cover-lrs"):
            (PARTS_DIR / f"{name}-params.json").write_text(json.dumps(params(docs[name]), indent=1) + "\n",
                                                           encoding="utf-8", newline="\n")
        for d in docs.values():
            App.closeDocument(d.Name)
        write_print_readme(infos)
    if components:
        import cad_components
        cad_components.main()
    if assembly:
        import cad_assembly
        cad_assembly.main()
    # FreeCAD keeps a .FCBak beside a file it saves over: these are all regenerated, so drop them.
    for bak in (ROOT / "cad").rglob("*.FCBak"):
        bak.unlink()
