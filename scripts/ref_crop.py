#!/usr/bin/env python3
"""A crop of a measuring photo with a millimetre grid in the builders' (L, H) coordinates, for reading details off it.

    py -I scripts/ref_crop.py PHOTO OUTLINE.json OUT.png L_from L_to H_from H_to [--px 12] [--muzzle left|right]
                              [--overlay RENDER.png CAMERAS.json KEY]

PHOTO is the photo trace_outline.py traced into OUTLINE.json (its px_per_mm and photo_px place the grid). Lines every
millimetre (faint), every 5 (stronger, labelled), every 10 (strongest); --px = output pixels per mm. The crop keeps
the photo's handedness. --overlay draws the red outline of a render (render_*.py's photo-scale view, its
cameras.json entry KEY: centre_mm, px_per_mm, size; mirrored when the photo's muzzle is on the left) over the crop,
which is the part-by-part check of the remodel passes: trigger and guard first.
"""

import argparse
import json

import numpy as np
from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("outline")
    ap.add_argument("out")
    ap.add_argument("box", type=float, nargs=4)
    ap.add_argument("--px", type=float, default=12.0)
    ap.add_argument("--muzzle", default="left")
    ap.add_argument("--overlay", nargs=3)
    ap.add_argument("--nogrid", action="store_true")
    a = ap.parse_args()
    o = json.load(open(a.outline))
    s, xm, y0 = o["px_per_mm"], o["photo_px"]["x_muzzle"], o["photo_px"]["y_lowest"]
    sgn = 1 if a.muzzle == "left" else -1
    la, lb, ha, hb = a.box
    xa, xb = sorted((xm + sgn * la * s, xm + sgn * lb * s))
    ya, yb = y0 - hb * s, y0 - ha * s
    im = Image.open(a.photo).convert("RGB")
    w, h = round((lb - la) * a.px), round((hb - ha) * a.px)
    crop = im.transform((w, h), Image.EXTENT, (xa, ya, xb, yb), Image.BICUBIC)
    d = ImageDraw.Draw(crop, "RGBA")

    def X(L):
        return ((L - la) if sgn > 0 else (lb - L)) * a.px

    def Y(H):
        return (hb - H) * a.px

    if a.overlay:
        ren, cams, key = a.overlay
        cam = json.load(open(cams))[key]
        r = np.asarray(Image.open(ren).convert("RGBA"))[..., 3] > 127
        if sgn > 0:
            r = r[:, ::-1]                       # renders show game space mirrored: muzzle right for the left side
        rw, rh = cam["size"]
        ppm = cam["px_per_mm"]
        cL, cH = cam["centre_mm"]
        ys, xs = np.mgrid[0:h, 0:w]
        Lm = (la + xs / a.px) if sgn > 0 else (lb - xs / a.px)
        Hm = hb - ys / a.px
        u = np.round(rw / 2 + sgn * (Lm - cL) * ppm).astype(int)
        v = np.round(rh / 2 - (Hm - cH) * ppm).astype(int)
        ok = (u >= 0) & (u < rw) & (v >= 0) & (v < rh)
        m = np.zeros((h, w), bool)
        m[ok] = r[v[ok], u[ok]]
        edge = m ^ (np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1) & m)
        edge |= np.roll(edge, 1, 0) | np.roll(edge, 1, 1)
        arr = np.asarray(crop).copy()
        arr[edge] = (255, 30, 30)
        crop = Image.fromarray(arr)
        d = ImageDraw.Draw(crop, "RGBA")
    if not a.nogrid:
        for L in range(int(np.floor(la)), int(np.ceil(lb)) + 1):
            c = (255, 0, 0, 150) if L % 10 == 0 else (255, 60, 60, 95) if L % 5 == 0 else (255, 120, 120, 38)
            d.line([(X(L), 0), (X(L), h)], fill=c, width=1)
            if L % 5 == 0:
                d.text((X(L) + 2, 2), str(L), fill=(255, 255, 0, 255))
        for H in range(int(np.floor(ha)), int(np.ceil(hb)) + 1):
            c = (0, 80, 255, 150) if H % 10 == 0 else (60, 120, 255, 95) if H % 5 == 0 else (120, 160, 255, 38)
            d.line([(0, Y(H)), (w, Y(H))], fill=c, width=1)
            if H % 5 == 0:
                d.text((2, Y(H) - 11), str(H), fill=(0, 255, 255, 255))
    crop.save(a.out)
    print("wrote", a.out, crop.size)


if __name__ == "__main__":
    main()
