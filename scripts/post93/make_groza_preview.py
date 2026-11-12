#!/usr/bin/env python3
"""The OTs-14 Groza's review sheet from render_groza.py's output (Python 3 + Pillow).

    py scripts/post93/make_groza_preview.py RENDERS_DIR

Writes docs/post93_groza_preview.png: the left side with the drawing's traced outline (scripts/groza_reference_outline
.json) and their silhouette overlap, each calibre on GoM's magazines (Groza-1 7.62x39 AK-47 30, Groza-4 9x39 AS VAL
20, Groza-2 5.45x39 AK-74 30 with the carrier back), the Groza-4's suppressor, a 3/4 view, and GoM's AKS-74U and AS
VAL at the same scale; side views flipped to the game's handedness (the renders are Blender world space).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "docs", "post93_groza_preview.png")
R = sys.argv[1]
try:
    FONT = ImageFont.truetype("arial.ttf", 26)
except OSError:
    FONT = ImageFont.load_default()


def overlay():
    cam = json.load(open(os.path.join(R, "cameras.json")))["GROZA"]
    (W, Hh), s = cam["size"], cam["px_per_mm"]
    Lc, Hc = cam["photo_centre_mm"]
    out = json.load(open(os.path.join(ROOT, "scripts", "groza_reference_outline.json")))["outline"]
    im = Image.open(os.path.join(R, "GROZA4_left.png")).convert("RGBA")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    pts = [(W / 2 - (L - Lc) * s, Hh / 2 - (H - Hc) * s) for L, H in out]
    ImageDraw.Draw(bg).line(pts + pts[:1], fill=(220, 30, 30), width=2)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    a, b = np.array(im.getchannel("A")) > 128, np.array(mask) > 128
    return ImageOps.mirror(bg), (a & b).sum() / (a | b).sum()


ov, iou = overlay()
print("IoU %.3f" % iou)
items = [(ov, "Groza-4 (9x39, GoM's AS VAL 20), red = the drawing's outline, overlap %.1f%% (the drawing's sling "
               "loop and magazine differ)" % (iou * 100))]
for n, t in (("GROZA4_supp_left", "Groza-4 with its own suppressor"),
             ("GROZA1_left", "Groza-1 (7.62x39): the long barrel and slotted muzzle device, GoM's AK-47 30"),
             ("GROZAGL_right", "Groza-1 with the GP-25 (right side, as the user's photo)"),
             ("GROZAGL_left", "Groza-1 with the GP-25, left side"),
             ("GROZAGL_q", "Groza-1 with the GP-25 from the front, left"),
             ("GROZA2_left_fired", "Groza-2 Prototype (5.45x39), compact, GoM's AK-74 30, carrier back"),
             ("GROZA2_right_fired", "Groza-2, right side: the AK carrier handle back"),
             ("GROZA2_q", "Groza-2 from behind, right (as the user's photo)"),
             ("GROZA1_q", "Groza-1, 3/4 from behind, right"),
             ("GROZA4_MOUNT_left", "GoM's Picatinny Rail (Up), drawn as a base clamped on the carrying handle with GoM's own rail on it"),
             ("GROZA4_PSO1_Scope_left", "GoM's PSO-1 on it"),
             ("GROZA4_LR4X_Scope_q", "GoM's LR4X"),
             ("GROZA1_Kobra_Sight_left", "GoM's Kobra on the Groza-1"),
             ("gom_AKS74U", "GoM's AKS-74U at the same scale"),
             ("gom_ASVAL", "GoM's AS VAL at the same scale")):
    im = Image.open(os.path.join(R, n + ".png")).convert("RGBA")
    items.append((im if n.endswith("_q") else ImageOps.mirror(im), t))
W = 1400
rows = []
for im, t in items:
    k = W / im.width
    rows.append((im.resize((W, int(im.height * k))), t))
H = sum(r.height + 40 for r, _ in rows) + 60
page = Image.new("RGBA", (W, H), (236, 236, 232, 255))
d = ImageDraw.Draw(page)
d.text((10, 10), "OTs-14 Groza (Post-93), GunsOfTienPost93.GROZA*: renders of the exported FBX", fill=(30, 30, 30),
       font=FONT)
y = 60
for im, t in rows:
    d.text((10, y + 4), t, fill=(40, 40, 40), font=FONT)
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    page.alpha_composite(bg, (0, y + 36))
    y += im.height + 40
page.convert("RGB").save(OUT)
print("wrote", OUT, page.size)
