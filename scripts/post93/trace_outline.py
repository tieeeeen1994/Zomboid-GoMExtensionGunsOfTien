#!/usr/bin/env python3
"""Trace a gun's side outline from a photo on a light background (Python 3 + Pillow + numpy).

    python3 scripts/post93/trace_outline.py PHOTO OUT.json --length MM --muzzle left|right [--threshold 235]
                                            [--eps 1.5] [--grid GRID.png]

The background is every light pixel (luminance above --threshold) connected to the image border; everything else is
the gun. Its outer boundary (Moore neighbour trace) is simplified with Douglas-Peucker (--eps px) and written in the
builders' photo coordinates, real millimetres: L back from the muzzle tip, H up from the lowest point, scaled so the
gun is --length mm long. Light regions enclosed by the gun (the trigger opening) are written as "holes_traced"; they
often run round the trigger and need cleaning by hand into "holes". --grid writes the photo with a 10 mm grid and the
traced outline drawn over it, for reading off the positions of details. (fiveseven_reference_outline.json was made
with the same steps before this script existed.)
"""

import argparse
import json
import math
from collections import deque

import numpy as np
from PIL import Image, ImageDraw


def flood_background(light):
    h, w = light.shape
    bg = np.zeros_like(light)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and light[yy, xx] and not bg[yy, xx]:
                bg[yy, xx] = True
                q.append((yy, xx))
    return bg


def largest_component(mask):
    h, w = mask.shape
    lab = np.zeros(mask.shape, np.int32)
    best, n = (0, 0), 0
    for y0 in range(h):
        for x0 in np.nonzero(mask[y0] & (lab[y0] == 0))[0]:
            n += 1
            st, cnt = [(y0, x0)], 0
            lab[y0, x0] = n
            while st:
                y, x = st.pop()
                cnt += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and lab[yy, xx] == 0:
                        lab[yy, xx] = n
                        st.append((yy, xx))
            if cnt > best[0]:
                best = (cnt, n)
    return lab == best[1]


def trace(mask):
    """Moore-neighbour boundary trace (clockwise on screen)."""
    h, w = mask.shape

    def on(x, y):
        return 0 <= y < h and 0 <= x < w and mask[y, x]

    ys, xs = np.nonzero(mask)
    i = np.lexsort((xs, ys))[0]
    sx, sy = int(xs[i]), int(ys[i])
    nb = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    pts, cx, cy, back = [(sx, sy)], sx, sy, 6
    for _ in range(400000):
        found = False
        for k in range(1, 9):
            j = (back + k) % 8
            nx, ny = cx + nb[j][0], cy + nb[j][1]
            if on(nx, ny):
                bx, by = cx + nb[(j - 1) % 8][0], cy + nb[(j - 1) % 8][1]
                cx, cy = nx, ny
                back = nb.index((bx - cx, by - cy))
                found = True
                break
        if not found or (cx, cy) == (sx, sy):
            break
        pts.append((cx, cy))
    return pts


def simplify(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    ab = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*ab)
    d = [abs(ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / n if n > 0 else math.hypot(p[0] - a[0], p[1] - a[1])
         for p in pts]
    i = int(np.argmax(d))
    if d[i] > eps:
        return simplify(pts[:i + 1], eps)[:-1] + simplify(pts[i:], eps)
    return [pts[0], pts[-1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("out")
    ap.add_argument("--length", type=float, required=True)
    ap.add_argument("--muzzle", choices=("left", "right"), required=True)
    ap.add_argument("--threshold", type=float, default=235.0)
    ap.add_argument("--eps", type=float, default=1.5)
    ap.add_argument("--grid")
    ap.add_argument("--source", default="")
    a = ap.parse_args()

    lum = np.asarray(Image.open(a.photo).convert("L")).astype(np.float32)
    light = lum > a.threshold
    bg = flood_background(light)
    holes = light & ~bg
    gun = largest_component(~bg)
    ys, xs = np.nonzero(gun)
    x0, x1, y1 = int(xs.min()), int(xs.max()), int(ys.max())
    s = (x1 - x0) / a.length

    def mm(p):
        L = (p[0] - x0) / s if a.muzzle == "left" else (x1 - p[0]) / s
        return [round(L, 1), round((y1 - p[1]) / s, 1)]

    outline = simplify(trace(gun) + [trace(gun)[0]], a.eps)[:-1]
    hole = largest_component(holes) if holes.any() else None
    traced = simplify(trace(hole) + [trace(hole)[0]], a.eps)[:-1] if hole is not None else []
    data = {"source": a.source or a.photo,
            "units": "real mm; L back from the muzzle tip, H up from the lowest point; scaled to %.0f mm long; "
                     "traced at %.1f px tolerance (trace_outline.py)" % (a.length, a.eps),
            "px_per_mm": round(s, 4), "photo_px": {"x_muzzle": x0 if a.muzzle == "left" else x1, "y_lowest": y1},
            "outline": [mm(p) for p in outline], "holes_traced": [[mm(p) for p in traced]] if traced else [],
            "holes": []}
    with open(a.out, "w") as fh:
        json.dump(data, fh, indent=0)
    print("%d outline points, %.3f px/mm, height %.1f mm" % (len(outline), s, (y1 - ys.min()) / s))

    if a.grid:
        im = Image.open(a.photo).convert("RGB")
        k = max(1, int(round(1100 / im.width)))
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        xm = (x0 if a.muzzle == "left" else x1) * k
        sgn = 1 if a.muzzle == "left" else -1
        for Lmm in range(0, int(a.length) + 11, 10):
            x = xm + sgn * Lmm * s * k
            d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if Lmm % 50 == 0 else (255, 170, 170), width=1)
            d.text((x + 2, 2 + (Lmm % 20) * 0.6), str(Lmm), fill=(200, 0, 0))
        for Hmm in range(0, int((y1 - ys.min()) / s) + 11, 10):
            y = (y1 - Hmm * s) * k
            d.line([(0, y), (im.width, y)], fill=(0, 0, 255) if Hmm % 50 == 0 else (170, 170, 255), width=1)
            d.text((2, y - 11), str(Hmm), fill=(0, 0, 200))

        def px(p):
            return xm + sgn * p[0] * s * k, (y1 - p[1] * s) * k

        pts = [px(p) for p in data["outline"]]
        d.line(pts + pts[:1], fill=(0, 190, 0), width=1)
        if traced:
            pts = [px(p) for p in data["holes_traced"][0]]
            d.line(pts + pts[:1], fill=(0, 190, 0), width=1)
        im.save(a.grid)


if __name__ == "__main__":
    main()
