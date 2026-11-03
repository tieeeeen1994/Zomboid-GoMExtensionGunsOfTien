#!/usr/bin/env python3
"""The P90 with its ring sight: inventory icon and review sheet (Python 3 + Pillow, numpy).

    python3 scripts/make_p90std_art.py [--renders DIR]

The icon (32x32 RGBA, M/textures/item_GunsOfTien_P90.png) is rendered from the exported FBX and texture with
Post-93's make_mp7_art.py renderer and the camera and light it fitted on GoM's MP5 icon (mp7_icon_cameras.json, the
P90 TR's icon camera): the gun upright with the P90's magazine, no rails. --renders DIR (render_p90std.py's output)
also writes docs/p90_preview.png: the Commons photo's silhouette against the model's (references/p90, not in the repo:
only the silhouette is shown), the sides, the optional rails bare and fitted out, the P90 TR at the same scale.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402  (FBX reader, attach, icon shading)
import make_p90_art as P                   # noqa: E402  (font)

ROOT = A.ROOT
MAIN = A.MAIN_MEDIA
POINTS = json.load(open(os.path.join(HERE, "p90std_points.json")))
FBX_GUN = os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_P90.fbx")
FBX_MAGS = os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
PREVIEW = os.path.join(ROOT, "docs/p90_preview.png")
PHOTO = os.path.join(ROOT, "references/p90/p90_standard_mirrored.png")
UPRIGHT = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0, 0.0]}     # the model is turned (held like a pistol)


def make_icon():
    fitted = json.load(open(A.CAMERAS_JSON))["gun"]
    mag = A.attach(A.load_game(FBX_MAGS, "57x28Magazine50_P90"), POINTS["magazine"])
    gun = [(A.load_game(FBX_GUN, n), 0) for n in ("P90_BODY", "P90_BOLT", "P90_HANDLE")] + [(mag, 1)]
    objs = [(A.attach(t, UPRIGHT), i) for t, i in gun]
    texes = [A.img(os.path.join(MAIN, "textures/weapons/GunsOfTien/P90.png")),
             A.img(os.path.join(MAIN, "textures/weapons/GunsOfTienPost93/57x28Magazine50_P90.png"))]
    icon = A.shade(objs, texes, dict(fitted["camera"]), fitted["light"])
    icon.save(os.path.join(MAIN, "textures/item_GunsOfTien_P90.png"))
    return icon


def check():
    objects, unit, lcl = A.header_check(FBX_GUN)
    print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(FBX_GUN), objects, unit))
    names = {n for n, _, _ in lcl}
    for n, rot, scl in lcl:
        mn, mx = A.bounds(A.load_game(FBX_GUN, n))
        print("  %-15s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))
    assert names >= {"P90_BODY", "P90_BOLT", "P90_HANDLE", "P90_RAIL_LEFT", "P90_RAIL_RIGHT"}, names
    assert "P90_RAIL_UP" not in names, "no top rail on the P90 (user, 2026-11-03)"


def outline(renders):
    pm = np.asarray(Image.open(PHOTO).convert("RGB")).astype(int).mean(2) < 200
    rm = np.asarray(Image.open(os.path.join(renders, "right_photo.png")).convert("RGBA"))[..., 3] > 128
    iou = (pm & rm).sum() / (pm | rm).sum()
    out = np.full(pm.shape + (3,), 250, np.uint8)       # silhouettes only: none of the photo's pixels
    out[pm & rm] = [70, 70, 74]
    out[rm & ~pm] = [220, 30, 30]
    out[pm & ~rm] = [30, 110, 230]
    print("silhouette overlap with the photo: %.3f" % iou)
    return Image.fromarray(out).crop((80, 200, 2020, 1000)), iou


def sheet(renders, icon):
    W = 1500
    over, iou = outline(renders)
    rows = [
        [(over, "Commons photo of a P90 Standard (its side rails fitted here too) against the model: grey both, red "
                "model only, blue photo only, overlap %.3f" % iou, None)],
        [("left", "left side", None), ("right", "right side", None)],
        [("sight_rear", "into the ring sight from behind: a square window", None),
         ("sight_front", "and from ahead", None)],
        [("sight_like", "the ring sight's hood and knob", None), ("rails_like", "GoM's optional rails: the sides only",
                                                                  (40, 40, 42))],
        [("fitted_like", "SP90, SR7, AimRight", (40, 40, 42)),
         ("fitted2_like", "BrightPoint-5, LRX-7", (40, 40, 42))],
        [("tr_left", "the P90 TR (Post-93), same scale", None), ("racked", "handles back (racked)", (40, 40, 42))],
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
    d.text((30, 20), "P90 (1990, ring sight; main mod): the P90 TR's body, the original upper, GoM's optional side rails",
           fill=(20, 20, 20), font=P.font(26))
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
    d.text((280, y + 160), "item_GunsOfTien_P90 (32x32, x6 and 1:1)", fill=(60, 60, 60), font=P.font(18))
    out.save(PREVIEW)
    print("wrote", PREVIEW)


def main():
    check()
    icon = make_icon()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icon)


if __name__ == "__main__":
    main()
