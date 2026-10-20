"""Measure a tread outline from a top-down photo with an A4 sheet lying on it.

Usage: python tools/measure_tread.py photo.jpg out-overlay.png
Prints the A4 sheet size in pixels, the four fitted corners in mm (in the
sheet's frame), side lengths, corner angles and rough corner radii. Used on
20 Oct 2026 to write data/blank.json (CLAUDE.md section 9). Needs
opencv-python-headless and numpy (not in requirements.txt; install on demand).
"""
import sys
import cv2
import numpy as np

path, out = sys.argv[1], sys.argv[2]
img = cv2.imread(path)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)

# Paper: bright, unsaturated. Wood: orange, saturated.
paper = ((v > 170) & (s < 40)).astype(np.uint8) * 255
wood = ((h > 5) & (h < 25) & (s > 90) & (v > 70)).astype(np.uint8) * 255
k = np.ones((7, 7), np.uint8)


def largest(mask):
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return max(cs, key=cv2.contourArea)


tread = largest(cv2.bitwise_or(paper, wood))
# Paper must lie inside the tread: mask it.
tm = np.zeros_like(paper)
cv2.drawContours(tm, [tread], -1, 255, -1)
pc = largest(cv2.bitwise_and(paper, tm))
peri = cv2.arcLength(pc, True)
quad = cv2.approxPolyDP(pc, 0.02 * peri, True).reshape(-1, 2).astype(np.float32)
assert len(quad) == 4, quad
quad = cv2.cornerSubPix(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), quad.reshape(-1, 1, 2), (7, 7), (-1, -1),
                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.01)).reshape(-1, 2)
# Order: start at corner, make the first side the long one (297).
d = [np.linalg.norm(quad[i] - quad[(i + 1) % 4]) for i in range(4)]
if d[0] < d[1]:
    quad = np.roll(quad, -1, axis=0)
dst = np.array([[0, 0], [297, 0], [297, 210], [0, 210]], np.float32)
H = cv2.getPerspectiveTransform(quad.astype(np.float32), dst)
print("paper px sides", [round(float(x), 1) for x in d])

pts = cv2.perspectiveTransform(tread.reshape(-1, 1, 2).astype(np.float32), H).reshape(-1, 2)
hull = cv2.convexHull(pts).reshape(-1, 2)
# Fit quadrilateral then refine each side with a line fit away from corners.
peri = cv2.arcLength(hull, True)
for eps in np.linspace(0.005, 0.05, 50):
    q = cv2.approxPolyDP(hull, eps * peri, True).reshape(-1, 2)
    if len(q) == 4:
        break
print("approx quad mm", q.round(1).tolist())
lines = []
for i in range(4):
    a, b = q[i], q[(i + 1) % 4]
    ab = b - a
    L = np.linalg.norm(ab)
    u = ab / L
    n = np.array([-u[1], u[0]])
    rel = pts - a
    t = rel @ u
    dist = np.abs(rel @ n)
    sel = pts[(t > 0.15 * L) & (t < 0.85 * L) & (dist < 12)]
    vx, vy, x0, y0 = cv2.fitLine(sel, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    lines.append((np.array([x0, y0]), np.array([vx, vy])))
corners = []
for i in range(4):
    (p, e), (r, f) = lines[i - 1], lines[i]
    A = np.array([e, -f]).T
    t = np.linalg.solve(A, r - p)
    corners.append(p + e * t[0])
corners = np.array(corners)
sides = [float(np.linalg.norm(corners[i] - corners[(i + 1) % 4])) for i in range(4)]
print("corners mm", corners.round(1).tolist())
print("sides mm", [round(x, 1) for x in sides])
for i in range(4):
    a, b, c = corners[i - 1], corners[i], corners[(i + 1) % 4]
    v1, v2 = a - b, c - b
    ang = np.degrees(np.arccos(v1 @ v2 / np.linalg.norm(v1) / np.linalg.norm(v2)))
    # corner rounding: gap between sharp corner and nearest contour point
    gap = np.min(np.linalg.norm(pts - b, axis=1))
    r = gap / (1 / np.sin(np.radians(ang) / 2) - 1)
    print(f"corner {i}: angle {ang:.1f} deg, rounding radius ~{r:.0f} mm")

vis = img.copy()
cv2.drawContours(vis, [tread], -1, (0, 0, 255), 4)
cv2.polylines(vis, [quad.astype(np.int32)], True, (255, 0, 0), 4)
x, y, w, hh = cv2.boundingRect(tread)
cv2.imwrite(out, vis[max(0, y - 60):y + hh + 60, max(0, x - 60):x + w + 60])
