#!/usr/bin/env python3
"""The HK416's review sheet from render_hk416.py's output (Python 3 + Pillow).

    py scripts/post93/make_hk416_preview.py RENDERS_DIR

Writes docs/post93_hk416_preview.png; side views flipped to the game's handedness (the renders are Blender world space).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "post93_hk416_preview.png"))
R = sys.argv[1]
try:
    FONT = ImageFont.truetype("arial.ttf", 26)
except OSError:
    FONT = ImageFont.load_default()
ITEMS = [("HK416_left", "HK416 D14.5RS, bare (left side): rail system with its slots, both sights up, H&K grip and stock (deployed), STANAG 30", True),
         ("HK416_right", "Right side", True),
         ("HK416_q", "Three quarters", False),
         ("HK416_rail_q", "The rail system and the receiver's full-length top rail", False),
         ("HK416_front_q", "The front: rail cap, QD cup, gas block with the MP5-type front sight, flash hider", False),
         ("HK416_collapsed_right", "Stock collapsed (stock_folded, 75 mm in, as in the IMFDB photo)", True),
         ("HK416_fitted_right", "GoM's EXPS3 (rear sight folds), MKC foregrip, SR7 (left), AimRight (right), AR mount device + MKI", True),
         ("HK416_fitted_q", "The same, three quarters", False),
         ("HK416_lr4x_right", "GoM's LR4X and bipod (both sights fold)", True),
         ("HK416_elcan_right", "GoM's Elcan (both sights fold)", True),
         ("HK416_sights_BODY", "Sights up: no optic (HK416_BODY)", True),
         ("HK416_sights_BODY_RD", "Rear sight folded: a red dot or holographic sight (HK416_BODY_RD)", True),
         ("HK416_sights_BODY_FD", "Both sights folded: a magnified scope (HK416_BODY_FD)", True),
         ("HK416_selector_left", "Selector labels, left side (red single shot above, white safe ahead, red auto behind)", True),
         ("HK416_selector_right", "Right side: GoM's selector mirrored (ambidextrous) with the same labels", True),
         ("HK416_racked_right", "Racked: charging handle back, bolt open", True),
         ("gom_M4A1_right", "GoM's M4A1 at the same scale", True)]
W = 1400
rows = []
for name, text, flip in ITEMS:
    im = Image.open(os.path.join(R, name + ".png")).convert("RGBA")
    im = ImageOps.mirror(im) if flip else im
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    rows.append((bg.resize((W, int(im.height * W / im.width))), text))
page = Image.new("RGB", (W, sum(r.height + 40 for r, _ in rows) + 60), (236, 236, 232))
d = ImageDraw.Draw(page)
d.text((10, 10), "HK416 D14.5RS (Post-93), GunsOfTienPost93.HK416: renders of the exported FBX on GoM's AR15 texture",
       fill=(30, 30, 30), font=FONT)
y = 60
for im, text in rows:
    d.text((10, y + 4), text, fill=(40, 40, 40), font=FONT)
    page.paste(im.convert("RGB"), (0, y + 36))
    y += im.height + 40
page.save(OUT)
print("wrote", OUT, page.size)
