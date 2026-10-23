# Cutting a tree on the CNC

One tree per setup, 4mm two-flute carbide end mill with enough reach for 30mm (Rob, 23 Oct 2026). Not a production run: take it gently and watch the first one all the way through.

Files: `cad/stair-tree-cnc-layout.dxf` (or `.svg`), mm, front view. Layers:

| Layer | Op | What |
|---|---|---|
| `FRONT_HOLES` | 1, face up | 92 pixel holes, right through |
| `BACK_CHANNEL` | 2, face down | wiring channel centreline, 15mm wide × 12mm deep (mirrored) |
| `BACK_POCKET` | 2, face down | data-in pocket at node 1 (25mm) and exit slot down to the bottom edge (mirrored) |
| `BACK_COUNTERBORE` | 2, face down | only if the pixel test says a counterbore is needed |
| `EXISTING` | — | reference only: the old fixing holes in the back. Don't cut. |
| `REG` | — | not used; the flip is located from two finished holes (below) |
| `BLANK` | — | the tread outline, for positioning only |

## Before the first tree

1. **Offcut test** (pixels needed): cut 11.8, 12.0, 12.2 and 12.5mm holes in an oak offcut, plus 20mm of channel at 15mm and 18mm wide. Push a pixel into each hole and lay its lead in the channel. Set `hole_dia` (and a counterbore if wanted) in `tools/tree_layout.py`, then `make all`.
2. **Tape-check the tread** against `data/blank.json`: length ~894, wide end ~382, narrow end ~92. If one is out by more than about 3mm, fix the JSON and regenerate before cutting.
3. Screw a sacrificial MDF sheet to the bed under the tree: the holes go right through and the bit needs somewhere to finish.

## Op 1: front face up, pixel holes

- Set the tread face up, wide end against a straight stop and roughly square to X. Clamp it at the wide end and the narrow end with the printed step clamps (`fixtures/`, M6 into the strut channel nuts), with each clamp gripping no more than 10mm of the edge. The holes start 16mm from the edge.
- Origin: line the `BLANK` outline up on the tread (bottom-left corner and bottom edge). A few mm out doesn't matter, but keep it the same across the tree.
- Toolpath: helical bore each hole to the finished diameter, through to 0.5mm into the MDF.
- Peck/clear: lift out of the hole every 6–8mm of depth and blow the chips out. Deep oak holes pack with chips, and packed chips are what snap a 4mm bit.
- Keep the 2 alignment holes on the centreline open (node 36 at the apex and node 64 in the middle of the wide mouth, x = 191 on the outline). Every hole goes through anyway; these two are the ones you use in op 2.

## Op 2: flip, back face up, channel and pocket

- Flip the tread left-to-right about its long centreline (top stays at the top). The `BACK_*` layers are already mirrored for this.
- **Locate from the holes, not the fence.** Jog to the centre of node 36's hole and set X/Y zero there (the same point in the mirrored file: x = 191, y = 22 from the blank's top-left). Jog to node 64's hole (x = 191, y = 737): if the board is skewed, rotate it until both centres sit on the same X, or use your controller's rotation/skew if it has one. The channel only has to pass over each hole (15mm channel over a 12mm hole), so ±1mm is plenty.
- Clamp, and check clamp clearance against the channel path. The channel runs about 22mm in from the edge all round.
- Channel: 15mm wide (two or three passes of the 4mm bit, or an adaptive pocket), 12mm deep in steps. It follows the node order and already swings round the old 17mm fixing holes.
- Pocket at node 1: 25mm across, as deep as the channel, plus the exit slot down through the bottom edge (this is where the pixel lead goes into the control boot's shelf hole).

## Feeds for oak (starting point, 4mm 2-flute carbide)

| | Value |
|---|---|
| Spindle | 18,000 rpm |
| Feed | 800–1000 mm/min (≈0.025mm per tooth: gentle) |
| Plunge / helix | 300 mm/min, helix step 1mm per turn |
| Depth per pass | 1.5–2mm in the channel (0.5 × D); holes 1mm per helix turn |
| Width per pass | ≤ 40% of the bit in the channel; or adaptive clearing |
| Finish | a 0.2mm finishing pass on the hole walls for the push fit |

Listen and look at the chips: dust means the feed is too slow (heat dulls the bit); a screech or shower of splinters means it's too fast or too deep. Slow down in the narrow top end, where there's less wood to hold the board.

## After cutting

Sand the front lightly (don't round the hole edges), then oil per CLAUDE.md §3 before fitting the pixels. Check the oil doesn't close up the push fit: the holes may need a quick pass with a 12mm drill bit by hand.
