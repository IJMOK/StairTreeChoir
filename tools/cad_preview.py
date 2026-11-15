"""Shaded PNG previews of FreeCAD shapes, headless (FreeCAD's own Python has matplotlib).

  render([(shape, "#c8874a"), ...], "out.png", elev=25, azim=-60)

Used by tools/cad_export.py (one picture per printed part) and tools/cad_assembly.py
(the whole setup). Flat shading from one light; good enough to see that a part is right,
not a rendering.
"""

from __future__ import annotations

import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

LIGHT = np.array([0.35, -0.55, 0.75])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _tris(shape, deflection):
    pts, tris = shape.tessellate(deflection)
    if not tris:
        return np.zeros((0, 3, 3))
    p = np.array([[v.x, v.y, v.z] for v in pts])
    return p[np.array(tris)]


def render(items, path, elev=22, azim=-62, title=None, size=(8, 6), deflection=None, edge=False):
    """items: (shape, colour) pairs, or (shape, colour, alpha)."""
    fig = plt.figure(figsize=size, dpi=110)
    ax = fig.add_subplot(projection="3d")
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    view = np.array([np.cos(np.radians(elev)) * np.cos(np.radians(azim)),
                     np.cos(np.radians(elev)) * np.sin(np.radians(azim)), np.sin(np.radians(elev))])
    for item in items:
        shape, colour = item[0], item[1]
        alpha = item[2] if len(item) > 2 else 1.0
        bb = shape.BoundBox
        d = deflection or max(bb.DiagonalLength / 400, 0.05)
        t = _tris(shape, d)
        if not len(t):
            continue
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        n[(n @ view) < 0] *= -1                     # light whichever side faces us
        shade = 0.45 + 0.55 * np.clip(n @ LIGHT, 0, 1)
        rgb = np.array(to_rgb(colour))
        fc = np.clip(shade[:, None] * rgb[None, :], 0, 1)
        fc = np.hstack([fc, np.full((len(fc), 1), alpha)])
        coll = Poly3DCollection(t, facecolors=fc, edgecolors=(0, 0, 0, 0.15) if edge else fc, linewidths=0.1)
        ax.add_collection3d(coll)
        lo = np.minimum(lo, t.reshape(-1, 3).min(0))
        hi = np.maximum(hi, t.reshape(-1, 3).max(0))
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=11)
    fig.subplots_adjust(0, 0, 1, 0.95 if title else 1)
    # Write beside it and swap in: a picture open in a viewer (Windows locks it) gets a few
    # retries rather than failing the whole export.
    tmp = f"{path}.tmp.png"
    fig.savefig(tmp, facecolor="white")
    plt.close(fig)
    for attempt in range(10):
        try:
            os.replace(tmp, path)
            return
        except OSError:
            time.sleep(0.5)
    os.remove(tmp)
    print(f"could not replace {path} (open in another program?): left as it was")
