#!/usr/bin/env python3
"""9A-91 / VSK-94 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_9a91_art.py [--renders DIR]

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) rendered from the FBX files build_9a91.py exported, with
make_mp7_art.py's renderer: the guns on the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's
item_M4A1.png) with their magazine, the 9A-91's stock folded as GoM's AKS-74U icon shows its own; the magazine on
make_aug_art.py's magazine camera; the can and the mount device on the MP7's (mp7_icon_cameras.json).

--renders DIR (render_9a91.py's output) also writes docs/post93_9a91_preview.png: each gun's right side with its
outline in red on its measuring photo (references/9a91/imfdb/9A-91silenced.jpg at 2.785 px a mm,
references/vsk94/imfdb/VSK-94.jpg at 2.56), the trigger zoomed on both, the left side beside Kuzmin's, the fitted,
folded, 3/4, top, front and bolt-back views, and the icons beside GoM's.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402
import make_aug_art as AUG                 # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/post93_9a91_preview.png")
PTS = json.load(open(os.path.join(HERE, "a91_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_9A91.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_9A91_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_9A91_parts.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/A91.png")
MAG = "9x39Magazine20_A91"
MTEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/%s.png" % MAG)
CTEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/A91_Suppressor.png")
RIFLE_CAMERAS = os.path.join(HERE, "scar_icon_cameras.json")
MP7_CAMERAS = os.path.join(HERE, "mp7_icon_cameras.json")
RENDER_PPM = 2.785
PHOTOS = {
    "A91": (os.path.join(ROOT, "references/9a91/imfdb/9A-91silenced.jpg"), 2.785, 240, (840, 380, 1040, 540)),
    "VSK94": (os.path.join(ROOT, "references/vsk94/imfdb/VSK-94.jpg"), 2.56, 330, (930, 420, 1130, 580)),
}
NOTES = [
    "To review (decisions taken overnight, docs/post93_design.md \"KBP 9A-91 and VSK-94\"):",
    "- the current-production 9A-91 (left dovetail rail for GoM's AK side mount, selector on the right, folding charging handle), not the 1994 first model",
    "- both guns take the same detachable 9A-91 can on a new 9x39mm mount device; the TODO had the VSK-94's built in, but the real one is not integral",
    "- ribbed handguard on the 9A-91 (IMFDB's measuring photo), diamond on the VSK-94; one 20-round magazine (GoM's AS VAL magazines do not fit the real gun)",
    "- the VSK-94 shares the 9A-91's receiver: its photo reads 5% larger than the 9A-91's, so its trigger zoom sits a few mm off while the 9A-91's matches",
    "- GoM's AK side mount stands as tall on these guns as on GoM's AKs (its optics sit 1.6-3.0 into the mount, GoM's own 1.1-1.6: fit_audit, nothing flagged)",
]
LEFT_PHOTO = os.path.join(ROOT, "references/9a91/commons/9mm_KBP_9A-91_compact_assault_rifle_-_06.jpg")


def make_icons():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    mp7 = json.load(open(MP7_CAMERAS))
    # the guns are blued black all over (GoM's AKs have wood): lit a third brighter so the icons read as GoM's do
    gun_light = dict(rifle["light"], coef=[[a * 1.35, b * 1.35] for a, b in rifle["light"]["coef"]])
    made = {}
    mag = A.attach(A.load_game(FBX_MAGS, MAG), PTS["A91"]["magazine"])
    for gun, nodes in (("A91", ("A91_BODY", "A91_BOLT", "A91_STOCK_FOLDED")), ("VSK94", ("VSK94_BODY", "A91_BOLT"))):
        objs = [(A.load_game(FBX_GUN, n), 0) for n in nodes] + [(mag, 1)]
        icon = A.shade(objs, [A.img(TEX), A.img(MTEX)], dict(rifle["camera"]), gun_light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
        made[gun] = icon
    objs = {MAG: [(A.load_game(FBX_MAGS, MAG), 0)]}
    light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    made[MAG] = A.shade(objs[MAG], [A.img(MTEX)], AUG.mag_cameras(objs)[MAG], light)
    made[MAG].save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % MAG))
    for n, kind in (("A91_Suppressor", "suppressor"), ("A91_Muzzle_Mount_Device", "mount")):
        objs = [(A.load_game(FBX_PARTS, n), 0)]
        made[n] = A.shade(objs, [A.img(CTEX)], dict(mp7[kind]["camera"]), mp7[kind]["light"])
        made[n].save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % n))
    return made


def check():
    for path in (FBX_GUN, FBX_MAGS, FBX_PARTS):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def on_white(im):
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg


def overlay(gun, render):
    """The render (the gun's right side, mirrored to the photo's view, scaled to the photo's px a mm) registered on
    the photo by the best silhouette overlap below `top` (the optics on the photos are left out), its outline in red.
    Returns the overlay, the trigger crop zoomed 3x, the IoU and the offset."""
    path, ppm, top, trig = PHOTOS[gun]
    ph = Image.open(path).convert("RGB")
    r = ImageOps.mirror(Image.open(render).convert("RGBA"))
    if abs(ppm - RENDER_PPM) > 1e-6:
        r = r.resize((round(r.width * ppm / RENDER_PPM), round(r.height * ppm / RENDER_PPM)), Image.LANCZOS)
    a = np.array(r)[..., 3] > 128
    im = np.array(ph).astype(int)
    fg = im.max(-1) < 150          # the gun, not the photo's soft grey drop shadow
    fg[:top] = False
    a_rows = np.nonzero(a.any(1))[0]
    a_cols = np.nonzero(a.any(0))[0]
    f_rows = np.nonzero(fg.any(1))[0]
    f_cols = np.nonzero(fg.any(0))[0]
    ox0 = f_cols.min() - a_cols.min()
    oy0 = f_rows.max() - a_rows.max()
    best = None
    h, w = a.shape
    for dy in range(oy0 - 30, oy0 + 31, 1):
        for dx in range(ox0 - 30, ox0 + 31, 2):
            sub = np.zeros_like(fg)
            y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
            x0, x1 = max(0, dx), min(fg.shape[1], dx + w)
            if y1 <= y0 or x1 <= x0:
                continue
            sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            sub[:top] = False
            iou = (sub & fg).sum() / max((sub | fg).sum(), 1)
            if best is None or iou > best[0]:
                best = (iou, dx, dy)
    iou, dx, dy = best
    sub = np.zeros_like(fg)
    y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
    x0, x1 = max(0, dx), min(fg.shape[1], dx + w)
    sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    er = np.array(Image.fromarray(sub.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))) > 0
    out = np.array(ph).copy()
    out[sub & ~er] = [255, 0, 0]
    full = Image.fromarray(out)
    tx0, ty0, tx1, ty1 = trig
    zoom = full.crop(trig).resize(((tx1 - tx0) * 3, (ty1 - ty0) * 3), Image.NEAREST)
    return full, zoom, iou, (dx, dy)


def sheet(renders, icons):
    p = B.Page(renders, 2100, 7000, "9A-91 and VSK-94 (Post-93): Workbench renders of the exported FBX on A91.png "
                                    "(red: the render's outline on the measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    y = 70
    notes = {}
    for gun, label in (("A91", "9A-91"), ("VSK94", "VSK-94")):
        full, zoom, iou, off = overlay(gun, os.path.join(renders, gun + "_right_can.png"))
        notes[gun] = iou
        print("%s: silhouette IoU %.3f at %s" % (gun, iou, off))
        crop = full.crop((0, 40, full.width, full.height - 20))
        p.put(None, 20, y, 1400, "%s: IMFDB's studio right side, the model's outline in red (IoU %.2f below the "
                                 "optic)" % (label, iou), im=crop.convert("RGBA"))
        p.put(None, 1440, y, 640, "%s trigger and guard, 3x" % label, im=zoom.convert("RGBA"))
        y += max(round(crop.height * 1400 / crop.width), round(zoom.height * 640 / zoom.width)) + 20
    p.heading(20, y, "9A-91 (game view: the right side as the game draws it)")
    y += 40
    p.put(None, 20, y, 1010, "right side, stock deployed, its can", im=on_white(ImageOps.mirror(r("A91_right_can"))))
    y += p.put(None, 1050, y, 1010, "GoM's AK side mount and Kobra on the left rail",
               im=on_white(ImageOps.mirror(r("A91_right_optic")))) + 15
    p.put(None, 20, y, 1010, "bare (the barrel's collar and thread)", im=on_white(ImageOps.mirror(r("A91_right"))))
    y += p.put(None, 1050, y, 1010, "stock folded on the receiver", im=on_white(ImageOps.mirror(r("A91_folded")))) + 15
    p.put(None, 20, y, 1010, "left side: the dovetail rail, mount device only",
          im=on_white(ImageOps.mirror(r("A91_left_mount"))))
    if os.path.exists(LEFT_PHOTO):
        lp = Image.open(LEFT_PHOTO).convert("RGBA")
        y += p.put(None, 1050, y, 1010, "Kuzmin's left side (Commons 06)", im=lp) + 15
    p.put(None, 20, y, 1010, "3/4 from the front", im=on_white(r("A91_q")))
    y += p.put(None, 1050, y, 1010, "3/4 from behind", im=on_white(r("A91_q_back"))) + 15
    p.put(None, 20, y, 680, "3/4, stock folded", im=on_white(r("A91_folded_q")))
    p.put(None, 720, y, 680, "carrier and handle back (bolt_fired)", im=on_white(ImageOps.mirror(r("A91_bolt_back"))))
    y += p.put(None, 1440, y, 300, "front", im=on_white(r("A91_front"))) + 15
    y += p.put(None, 20, y, 2040, "top (muzzle right)", im=on_white(r("A91_top").rotate(-90, expand=True))) + 25
    p.heading(20, y, "VSK-94 (game view)")
    y += 40
    p.put(None, 20, y, 1010, "its can", im=on_white(ImageOps.mirror(r("VSK94_right_can"))))
    y += p.put(None, 1050, y, 1010, "GoM's AK side mount and PSO-1",
               im=on_white(ImageOps.mirror(r("VSK94_right_optic")))) + 15
    p.put(None, 20, y, 1010, "left side, mount device only", im=on_white(ImageOps.mirror(r("VSK94_left_mount"))))
    y += p.put(None, 1050, y, 1010, "left side, PSO-1", im=on_white(ImageOps.mirror(r("VSK94_left_optic")))) + 15
    p.put(None, 20, y, 1010, "3/4 from the front", im=on_white(r("VSK94_q")))
    y += p.put(None, 1050, y, 1010, "3/4 from behind", im=on_white(r("VSK94_q_back"))) + 15
    p.put(None, 20, y, 680, "carrier and handle back", im=on_white(ImageOps.mirror(r("VSK94_bolt_back"))))
    y += p.put(None, 720, y, 300, "front", im=on_white(r("VSK94_front"))) + 25
    gom = lambda n: Image.open(os.path.join(A.G, "textures", "item_%s.png" % n)).convert("RGBA")
    p.icons(20, y, [(gom("AKS74U"), "AKS-74U (GoM)"), (gom("ASVAL"), "AS VAL (GoM)"), (icons["A91"], "9A-91"),
                    (icons["VSK94"], "VSK-94"), (icons[MAG], "9A-91 20Rds"), (icons["A91_Suppressor"], "can"),
                    (icons["A91_Muzzle_Mount_Device"], "mount device")])
    y += 250
    for line in NOTES:
        p.d.text((30, y), line, fill=(30, 30, 30), font=p.FS)
        y += 26
    lo = p.im.crop((0, 0, 2100, y + 10))
    lo.save(PREVIEW)
    print("wrote", PREVIEW, lo.size)
    return notes


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
