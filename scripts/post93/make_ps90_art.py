#!/usr/bin/env python3
"""PS90 Carbine inventory icon and review sheet (Python 3 + Pillow, numpy).

    python3 scripts/post93/make_ps90_art.py [--renders DIR] [--photo PATH]

The icon (32x32 RGBA, P/textures/item_GunsOfTienPost93_PS90.png) is rendered from the exported FBX and texture with
make_mp7_art.py's renderer and the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's M4A1 icon):
the gun with the P90's magazine on top. --renders DIR (render_ps90.py's output) also writes
docs/post93_ps90_preview.png: the user's photo with the model's right side laid over it at the photo's scale (red:
model only, blue: photo only, which counts its drop shadow and red dot) and the share they overlap, the sides,
fitted out, the P90 TR at the same scale, the icon. The photo (references/ps90/ps90_right.png by default) is not in
the repo, its rights being unknown, and the sheet shows only its silhouette.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402  (FBX reader, attach, icon shading)
import make_p90_art as P                   # noqa: E402  (font)

ROOT = A.ROOT
MEDIA = A.MEDIA
TEX = A.TEX
ICONS = A.ICONS
MAIN_TEX = A.MAIN_TEX                # the P90 magazine is the main mod's (moved 2026-11-03)
POINTS = json.load(open(os.path.join(HERE, "ps90_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_PS90.fbx")
FBX_MAGS = os.path.join(A.MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
CAMERAS = os.path.join(HERE, "scar_icon_cameras.json")
PREVIEW = os.path.join(ROOT, "docs/post93_ps90_preview.png")
PHOTO = os.path.join(ROOT, "references/ps90/ps90_right.png")


def make_icon():
    cam = json.load(open(CAMERAS))["rifle"]
    objs = [(A.load_game(FBX_GUN, "PS90_BODY"), 0), (A.load_game(FBX_GUN, "PS90_BOLT"), 0),
            (A.load_game(FBX_GUN, "PS90_HANDLE"), 0),
            (A.attach(A.load_game(FBX_MAGS, "57x28Magazine50_P90"), POINTS["magazine"]), 1)]
    texes = [A.img(os.path.join(TEX, "PS90.png")), A.img(os.path.join(MAIN_TEX, "57x28Magazine50_P90.png"))]
    icon = A.shade(objs, texes, dict(cam["camera"]), cam["light"])
    icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_PS90.png"))
    return icon


def check():
    objects, unit, lcl = A.header_check(FBX_GUN)
    print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(FBX_GUN), objects, unit))
    for n, rot, scl in lcl:
        mn, mx = A.bounds(A.load_game(FBX_GUN, n))
        print("  %-12s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))
    assert {n for n, _, _ in lcl} >= {"PS90_BODY", "PS90_BOLT", "PS90_HANDLE"}


def outline(renders, photo):
    """The photo with the model's right side (render_ps90.py `right_photo`, the photo's scale and centre) compared."""
    ph = Image.open(photo).convert("RGB")
    pm = np.asarray(ph).astype(int).mean(2) < 215
    pm[400:480, 430:530] = False                       # the photo's red dot (not part of the gun)
    rm = np.asarray(Image.open(os.path.join(renders, "right_photo.png")).convert("RGBA"))[..., 3] > 128
    iou = (pm & rm).sum() / (pm | rm).sum()
    out = np.full(pm.shape + (3,), 250, np.uint8)       # silhouettes only: none of the photo's pixels
    out[pm & rm] = [70, 70, 74]
    out[rm & ~pm] = [220, 30, 30]
    out[pm & ~rm] = [30, 110, 230]
    print("silhouette overlap with the photo: %.3f" % iou)
    return Image.fromarray(out.astype("uint8")).crop((20, 380, 1180, 790)), iou


def sheet(renders, icon, photo):
    """Every render at half size (render_ps90.py gives the gun views one camera scale, so sizes compare)."""
    W = 1500
    over, iou = outline(renders, photo)
    rows = [
        [(over, "the user's photo's silhouette against the model's (grey: both, red: model only, blue: photo only), overlap %.3f" % iou,
          None)],
        [("left", "left side", None), ("right", "right side", None)],
        [("fitted_like", "SP90, Aimpoint, SR7, AimRight, MKC grip", (40, 40, 42)),
         ("fitted2_like", "Elcan, BrightPoint-5, MK2 grip", (40, 40, 42))],
        [("tr_left", "the P90 TR, same scale", None), ("render_like", "bare, from ahead", (40, 40, 42))],
    ]
    tiles = []
    for row in rows:
        out_row = []
        for im, label, bg in row:
            if isinstance(im, str):
                im = Image.open(os.path.join(renders, im + ".png")).convert("RGBA")
            w = 1160 if len(row) == 1 else 700
            im = im.convert("RGBA").resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)
            if bg is not None:
                back = Image.new("RGBA", im.size, bg + (255,))
                back.alpha_composite(im)
                im = back
            out_row.append((im, label))
        tiles.append(out_row)
    H = 70 + sum(max(im.size[1] for im, _ in row) + 40 for row in tiles) + 230
    out = Image.new("RGB", (W, H), (250, 250, 248))
    d = ImageDraw.Draw(out)
    d.text((30, 20), "PS90 Carbine (Post-93): the P90 TR's body with the PS90's barrel, cheek riser and the photo's "
           "M-LOK handguard", fill=(20, 20, 20), font=P.font(26))
    y = 70
    for row in tiles:
        for k, (im, label) in enumerate(row):
            x = 30 + k * 730
            out.paste(im, (x, y), im)
            d.text((x, y + im.size[1] + 4), label, fill=(60, 60, 60), font=P.font(18))
        y += max(im.size[1] for im, _ in row) + 40
    big = icon.resize((192, 192), Image.NEAREST)
    out.paste(big, (30, y), big)
    out.paste(icon, (240, y + 160), icon)
    d.text((280, y + 160), "item_GunsOfTienPost93_PS90 (32x32, x6 and 1:1)", fill=(60, 60, 60), font=P.font(18))
    out.save(PREVIEW)
    print("wrote", PREVIEW)


def main():
    check()
    icon = make_icon()
    if "--renders" in sys.argv:
        photo = sys.argv[sys.argv.index("--photo") + 1] if "--photo" in sys.argv else PHOTO
        sheet(sys.argv[sys.argv.index("--renders") + 1], icon, photo)


if __name__ == "__main__":
    main()
