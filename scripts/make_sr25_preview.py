#!/usr/bin/env python3
"""The SR-25's review sheet from render_sr25.py's output (Python 3 + Pillow).

    py scripts/make_sr25_preview.py RENDERS_DIR

Writes docs/sr25_preview.png: the side views flipped to the game's handedness (the renders are Blender world space,
the game's mirror image; the right side then reads as the user's right-side photo, muzzle right), the integrated
bipod folded and deployed, the integrated scope, both magazines in the well, racked, and GoM's AR15 and M14 at the
same scale.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "sr25_preview.png")
R = sys.argv[1]


def img(name, flip=True):
    im = Image.open(os.path.join(R, name + ".png")).convert("RGBA")
    return ImageOps.mirror(im) if flip else im


try:
    FONT = ImageFont.truetype("arial.ttf", 26)
except OSError:
    FONT = ImageFont.load_default()
rows = [
    [("SR25_right", "Right side, bipod folded (as the user's photo: muzzle right)", 1.0)],
    [("SR25_left", "Left side", 1.0)],
    [("SR25_deployed_left", "Integrated Harris bipod deployed", 1.0)],
    [("SR25_scope_q", "Integrated Leupold Vari-X III 3.5-10x on B-Square base and rings", 0.66),
     ("SR25_deployed_front", "From the front, bipod deployed", 0.55)],
    [("SR25_kac_left", "KAC steel 20", 0.66), ("SR25_pmag_left", "Post-93's PMAG 20 (fits too)", 0.66),
     ("SR25_racked_right", "Racked: handle back, bolt open", 0.66)],
    [("gom_AR15", "GoM's AR15 (its base) at the same scale", 1.0)],
    [("gom_M14", "GoM's M14 at the same scale", 1.0)],
]
W = 1820
blocks = []
for row in rows:
    ims = [(img(n, flip=not n.endswith("_front") and not n.endswith("_q")), t, s) for n, t, s in row]
    h = max(int(im.height * s * (W / sum(int(i.width * ss) for i, _, ss in ims))) for im, _, s in ims) + 40
    blocks.append((ims, h))
H = sum(h for _, h in blocks) + 60
page = Image.new("RGBA", (W, H), (236, 236, 232, 255))
d = ImageDraw.Draw(page)
d.text((10, 10), "Knight's SR-25 Match (1990), GunsOfTien.SR25: renders of the exported FBX on GoM's AR15 texture",
       fill=(30, 30, 30), font=FONT)
y = 60
for ims, h in blocks:
    k = W / sum(int(i.width * s) for i, _, s in ims)
    x = 0
    for im, t, s in ims:
        im = im.resize((int(im.width * s * k), int(im.height * s * k)))
        page.alpha_composite(im, (x, y + 34))
        d.text((x + 8, y + 4), t, fill=(40, 40, 40), font=FONT)
        x += im.width
    y += h
page.convert("RGB").save(OUT)
print("wrote", os.path.normpath(OUT), page.size)
