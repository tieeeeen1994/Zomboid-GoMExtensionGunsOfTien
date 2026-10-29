"""Crops of the AUG A1 reference photo with build_aug.py's millimetre grid, for reading profile points off it (Pillow).

    py scripts/aug_photo_grid.py L_FROM L_TO H_FROM H_TO ZOOM OUT.png [STEP_MM]

L back from the muzzle tip, H up from the heel, real mm; red lines every STEP mm along L, blue along H. Needs the
photo at references/aug/aug_nobg.png (Commons "Steyr AUG 5,56 mm noBG.png", not in the repo).
"""

import os
import sys

from PIL import Image, ImageDraw

PHOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "aug", "aug_nobg.png")
X0, Y0, S = 270.0, 2190.0, 5.62911          # muzzle tip x, heel y, px per mm (build_aug.py's frame)


def photo():
    im = Image.open(PHOTO)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def crop(im, La, Lb, Ha, Hb, zoom, out, step=10):
    box = (int(X0 + La * S), int(Y0 - Hb * S), int(X0 + Lb * S), int(Y0 - Ha * S))
    c = im.crop(box)
    c = c.resize((int(c.width * zoom), int(c.height * zoom)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    L = (int(La) // step + 1) * step
    while L < Lb:
        X = ((X0 + L * S) - box[0]) * zoom
        d.line([(X, 0), (X, c.height)], fill=(255, 0, 0) if L % 50 == 0 else (255, 150, 150), width=1)
        d.text((X + 2, 2), str(L), fill=(220, 0, 0))
        L += step
    H = (int(Ha) // step + 1) * step
    while H < Hb:
        Y = ((Y0 - H * S) - box[1]) * zoom
        d.line([(0, Y), (c.width, Y)], fill=(0, 0, 255) if H % 50 == 0 else (150, 150, 255), width=1)
        d.text((2, Y + 2), str(H), fill=(0, 0, 220))
        H += step
    c.save(out)
    print(out, c.size)


if __name__ == "__main__":
    a = sys.argv[1:]
    crop(photo(), float(a[0]), float(a[1]), float(a[2]), float(a[3]), float(a[4]), a[5], int(a[6]) if len(a) > 6 else 10)
