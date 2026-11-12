#!/usr/bin/env python3
"""The Mk 11 Mod 0's review sheet from render_mk11.py's output (Python 3 + Pillow).

    py scripts/post93/make_mk11_preview.py RENDERS_DIR

Writes docs/post93_mk11_preview.png; side views flipped to the game's handedness (the renders are Blender world space).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "post93_mk11_preview.png"))
R = sys.argv[1]
try:
    FONT = ImageFont.truetype("arial.ttf", 26)
except OSError:
    FONT = ImageFont.load_default()
ITEMS = [("MK11_right", "Mk 11 Mod 0, bare: KAC rail handguard (four rails), folded front sight, KAC 20", True),
         ("MK11_left", "Left side", True),
         ("MK11_hg_q", "The rail handguard", False),
         ("MK11_sniper_left", "GoM's LR4X, its bipod folded, the 7.62x51mm mount device + SOCOM762-RC, a PMAG 20", True),
         ("MK11_bipod_left", "GoM's bipod deployed", True),
         ("MK11_12x_left", "Sniper setup: GoM's LRX12X (12x) on the integrated top rail, bipod deployed, SOCOM762-RC", True),
         ("MK11_12x_q", "The same from the front", False),
         ("MK11_10x_left", "GoM's LR10X (10x), bipod folded", True),
         ("MK11_tactical_q", "GoM's foregrip, light (left rail) and laser (right rail)", False),
         ("MK11_racked_right", "Racked: charging handle back, bolt open", True),
         ("sr25", "The 1990 SR-25 (main mod) at the same scale", True),
         ("gom_AR15", "GoM's AR15 (its base) at the same scale", True)]
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
d.text((10, 10), "Mk 11 Mod 0 (Post-93), GunsOfTienPost93.MK11: renders of the exported FBX on GoM's AR15 texture",
       fill=(30, 30, 30), font=FONT)
y = 60
for im, text in rows:
    d.text((10, y + 4), text, fill=(40, 40, 40), font=FONT)
    page.paste(im.convert("RGB"), (0, y + 36))
    y += im.height + 40
page.save(OUT)
print("wrote", OUT, page.size)
