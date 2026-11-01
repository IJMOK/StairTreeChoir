# Archive

Superseded work, kept for reference (tidy of 1 Nov 2026). Nothing in the build, tests or docs depends on anything here, and `tools/make_public.py` leaves the folder out of the public copy. To bring something back, `git mv` it.

## `nx-tree-box/`: old NX imports of the tree box

Three imports of `cad/tree-box-assembly.step`, each kept together so its assembly links still resolve. NX added the number to a part's name when that name was already taken; it is the part's entity id in the STEP file, which is how each set was matched to a commit.

| Folder | Design | Assembly | STEP from |
|---|---|---|---|
| `1-box-and-lid-28oct/` | Box + lid | `tree-box-assembly.prt` | 28 Oct, around 0e126fc |
| `2-sliding-cover-28oct/` | Base + sliding cover | none (no assembly links to these parts) | e63841e |
| `3-clip-on-cover-30oct/` | L base + clip-on cover | `tree-box-assembly10.prt` | 30 Oct 20:32, just before 6c0ea5c. `tree-box-baseNH.stp` is an export from it, 30 Oct 20:56 |

Commit 0707947 calls set 3 "for the wrap-round cover", but it is the clip-on cover. The wrap-round design has not been imported into NX yet: import `cad/tree-box-assembly.step`.

To open an old assembly, set the NX load option to "From Folder". "As Saved" looks in `cad/`, where the parts no longer are.

## `nx-imports/`

`stair-tree_step.prt`, `fixture-plate_step.prt` and `stair-tree-cnc-layout_dxf.prt`: raw STEP and DXF imports from 25-26 Oct. No other part links to them. The CAM set is still in `cad/`: `tree.prt`, `fixture-plate.prt`, `Clamp.prt`, `stair-tree-assembly_step.prt`.

## `nx-logs/`

NX import and export logs. Not in git.

## `printed-site-box/`

The printed site box of 23 Oct 2026 and its STL and STEP exports, replaced by the bought DRiBOX on 26 Oct. `sealed-box.scad` is its shell, also mentioned as an optional webcam box in `docs/webcam.md`. It uses `enclosure/seal.scad`. To export one:

```
openscad -o site-box-6-trees.stl -D 'part="box"' -D 'trees=6' site-box.scad   # also 4 and 2
openscad -o site-box-lid.stl     -D 'part="lid"' site-box.scad
```

## `docs/`

- `morning-notes.md`: session notes, 23-24 Oct. Its one live warning, the hand-fixed timing, is now in `xlights/README.md`.
- `show-folder-moves.md`: old to new names from the 24 Oct xLights show folder tidy.
