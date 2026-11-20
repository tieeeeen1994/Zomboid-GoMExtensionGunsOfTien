#!/usr/bin/env python3
"""SV-99 (both stocks) inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_sv99_art.py [--renders DIR]

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) rendered from the FBX files build_sv99.py exported, with
make_mp7_art.py's renderer: each gun on the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's
item_M4A1.png), bipod folded, no optic; the magazine on make_aug_art.py's magazine camera.

--renders DIR (render_sv99.py's output) also writes docs/post93_sv99_preview.png: each gun over its measuring photo
(green: references/sv99/green_plywood/b2_003.jpg, 1.862 px a mm, right side; polymer: black_polymer/kalash_SV-99_2.jpg,
1.530 px a mm, left side mirrored) with the render's outline in red, fitted out, the 3/4 views, the toggle lever
forward and swung back, and the icons beside GoM's M24's.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

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
PREVIEW = os.path.join(ROOT, "docs/post93_sv99_preview.png")
PTS = json.load(open(os.path.join(HERE, "sv99_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV99.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV99_magazines.fbx")
TEXD = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/")
MAG = "22LRMagazine5_SV99"
MTEX = TEXD + MAG + ".png"
RIFLE_CAMERAS = os.path.join(HERE, "scar_icon_cameras.json")
# gun: (photo, px a mm, butt x, mirror the photo, mirror the render, crop)
PHOTOS = {"SV99": (os.path.join(ROOT, "references/sv99/green_plywood/b2_003.jpg"), 1.862, 27, False, True,
                   (0, 150, 2048, 700)),
          "SV99P": (os.path.join(ROOT, "references/sv99/black_polymer/kalash_SV-99_2.jpg"), 1.530, 270, True, False,
                    (200, 380, 1900, 1000))}
RENDER_PPM = 1.862


def make_icons():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    made = {}
    for gun in ("SV99", "SV99P"):
        objs = [(A.load_game(FBX_GUN, gun + n), 0) for n in ("_BODY", "_BIPOD_FOLDED")]
        objs.append((A.attach(A.load_game(FBX_GUN, gun + "_BOLT"), PTS[gun]["bolt_lock"]), 0))
        objs.append((A.attach(A.load_game(FBX_MAGS, MAG), PTS[gun]["magazine"]), 1))
        icon = A.shade(objs, [A.img(TEXD + gun + ".png"), A.img(MTEX)], dict(rifle["camera"]), rifle["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
        made[gun] = icon
    objs = {MAG: [(A.load_game(FBX_MAGS, MAG), 0)]}
    light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    mag = A.shade(objs[MAG], [A.img(MTEX)], AUG.mag_cameras(objs)[MAG], light)
    mag.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % MAG))
    made[MAG] = mag
    return made


def check():
    for path in (FBX_GUN, FBX_MAGS):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-24s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def on_white(im):
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg


def overlay(gun, render):
    """The render laid on the gun's photo (both with the butt on the left), the butt on the photo's butt, the height
    by the best overlap with the photo's stock and metal; the render's outline in red."""
    path, ppm, butt, mirror_photo, flip_render, crop = PHOTOS[gun]
    ph = Image.open(path).convert("RGB")
    if mirror_photo:
        ph = ImageOps.mirror(ph)
    r = Image.open(render).convert("RGBA")
    if flip_render:
        r = ImageOps.mirror(r)
    f = ppm / RENDER_PPM
    r = r.resize((round(r.width * f), round(r.height * f)), Image.NEAREST)
    a = np.array(r)[..., 3] > 0
    xs = np.nonzero(a.max(0))[0]
    im = np.array(ph).astype(int)
    if gun == "SV99":
        fg = ((im[..., 1] > im[..., 0] + 20) & (im[..., 1] > 60)) | (im.sum(-1) < 330)
    else:
        fg = im.sum(-1) < 300
    ox = butt - xs.min()
    best = None
    for dy in range(-300, 600, 2):
        sub = np.zeros_like(fg)
        h, w = a.shape
        y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
        x0, x1 = max(0, ox), min(fg.shape[1], ox + w)
        if y1 <= y0:
            continue
        sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - ox:x1 - ox]
        reg, ff = sub[:, butt:butt + 1300], fg[:, butt:butt + 1300]
        iou = (reg & ff).sum() / max((reg | ff).sum(), 1)
        if best is None or iou > best[0]:
            best = (iou, sub)
    sub = best[1]
    er = np.array(Image.fromarray(sub.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))) > 0
    out = np.array(ph).copy()
    out[sub & ~er] = [255, 0, 0]
    return Image.fromarray(out).crop(crop).convert("RGBA")


def sheet(renders, icons):
    p = B.Page(renders, 2100, 4300, "SV-99, GunsOfTienPost93.SV99 (green plywood) / SV99P (black polymer): Workbench "
                                    "renders of the exported FBX (red: the render's outline on each measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    y = 70
    for gun, view, flip, label in (("SV99", "SV99_right", True, "green plywood, zonawar's studio right side"),
                                   ("SV99P", "SV99P_left", False, "black polymer, Kalashnikov's left side (mirrored)")):
        if os.path.exists(PHOTOS[gun][0]):
            y += p.put(None, 20, y, 2040, label + ", the render's outline in red",
                       im=overlay(gun, os.path.join(renders, view + ".png"))) + 10
        im = r(view)
        y += p.put(None, 20, y, 2040, "the render", im=on_white(ImageOps.mirror(im) if flip else im)) + 20
    for gun in ("SV99", "SV99P"):
        p.put(None, 20, y, 1010, gun + ": GoM's PSO-1 on the rail, bipod deployed (game view)",
              im=on_white(ImageOps.mirror(r(gun + "_right_deployed_pso1"))))
        y += p.put(None, 1050, y, 1010, gun + ": 3/4 from the front", im=on_white(r(gun + "_q"))) + 10
    p.put(None, 20, y, 680, "toggle lever forward", im=on_white(ImageOps.mirror(r("SV99_lever_closed"))))
    p.put(None, 710, y, 680, "lever swung back (bolt_fired)", im=on_white(ImageOps.mirror(r("SV99_lever_open"))))
    y += p.put(None, 1400, y, 660, "3/4 from behind (polymer)", im=on_white(r("SV99P_q_back"))) + 20
    gom = Image.open(os.path.join(A.G, "textures", "item_M24.png")).convert("RGBA")
    p.icons(20, y, [(gom, "M24 (GoM)"), (icons["SV99"], "SV-99"), (icons["SV99P"], "SV-99 polymer"),
                    (icons[MAG], "SV-99 5Rds")])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
