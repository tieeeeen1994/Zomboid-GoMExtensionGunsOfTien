#!/usr/bin/env python3
"""SV-98 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_sv98_art.py [--renders DIR]

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) rendered from the FBX files build_sv98.py exported, with
make_mp7_art.py's renderer: the gun on the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's
item_M4A1.png), bipod folded, no optic; the magazine from the side on make_aug_art.py's magazine camera.

--renders DIR (render_sv98.py's output) also writes docs/post93_sv98_preview.png: the gun's right side over the
measuring photo (references/sv98/sv98/ru_003.jpg, 1.566 px a mm) with the render's outline in red, fitted out, the
3/4 views and front, the bolt forward and back, and the icons beside GoM's M24's.
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
PREVIEW = os.path.join(ROOT, "docs/post93_sv98_preview.png")
PTS = json.load(open(os.path.join(HERE, "sv98_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV98.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV98_magazines.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/SV98.png")
MAG = "762x54Magazine10_SV98"
MTEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/%s.png" % MAG)
RIFLE_CAMERAS = os.path.join(HERE, "scar_icon_cameras.json")
PHOTO = os.path.join(ROOT, "references/sv98/sv98/ru_003.jpg")
PHOTO_PPM, PHOTO_BUTT = 1.566, 53


def make_icons():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    gun = [(A.load_game(FBX_GUN, n), 0) for n in ("SV98_BODY", "SV98_BOLT", "SV98_BIPOD_FOLDED")]
    icon = A.shade(gun, [A.img(TEX)], dict(rifle["camera"]), rifle["light"])
    icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_SV98.png"))
    objs = {MAG: [(A.load_game(FBX_MAGS, MAG), 0)]}
    light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    mag = A.shade(objs[MAG], [A.img(MTEX)], AUG.mag_cameras(objs)[MAG], light)
    mag.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % MAG))
    return {"SV98": icon, MAG: mag}


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


def overlay(render):
    """The render (the gun's right side at the photo's px a mm, mirrored to the photo's view) laid on the photo: the
    butt on the photo's butt, the height by the best overlap with the photo's stock and metal; its outline in red."""
    ph = Image.open(PHOTO).convert("RGB")
    r = ImageOps.mirror(Image.open(render).convert("RGBA"))
    a = np.array(r)[..., 3] > 0
    xs = np.nonzero(a.max(0))[0]
    im = np.array(ph).astype(int)
    rr, gg, bb = im[..., 0], im[..., 1], im[..., 2]
    fg = ((gg > rr + 25) & (gg > 60) & (bb > rr)) | (im.sum(-1) < 250)
    ox = PHOTO_BUTT - xs.min()
    best = None
    for dy in range(-150, 350, 2):
        sub = np.zeros_like(fg)
        h, w = a.shape
        y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
        x0, x1 = max(0, ox), min(fg.shape[1], ox + w)
        sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - ox:x1 - ox]
        reg, f = sub[:, 53:1700], fg[:, 53:1700]
        iou = (reg & f).sum() / max((reg | f).sum(), 1)
        if best is None or iou > best[0]:
            best = (iou, sub)
    sub = best[1]
    er = np.array(Image.fromarray(sub.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))) > 0
    out = np.array(ph).copy()
    out[sub & ~er] = [255, 0, 0]
    return Image.fromarray(out).crop((0, 120, 2048, 700)).convert("RGBA")


def sheet(renders, icons):
    p = B.Page(renders, 2100, 2900, "SV-98, GunsOfTienPost93.SV98: Workbench renders of the exported FBX on SV98.png "
                                    "(red: the render's outline on the measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    y = 70
    if os.path.exists(PHOTO):
        y += p.put(None, 20, y, 2040, "zonawar's studio right side (references/sv98/sv98/ru_003.jpg), the render's "
                                      "outline in red", im=overlay(os.path.join(renders, "SV98_right.png"))) + 20
    y += p.put(None, 20, y, 2040, "the gun's right side, bipod folded (game view)",
               im=on_white(ImageOps.mirror(r("SV98_right")))) + 20
    p.put(None, 20, y, 1010, "GoM's PSO-1 on the rail, bipod deployed (game view)",
          im=on_white(ImageOps.mirror(r("SV98_right_deployed_pso1"))))
    y += p.put(None, 1050, y, 1010, "left side, GoM's LR10X (mirrored)", im=on_white(r("SV98_left_deployed_lr10x"))) + 20
    p.put(None, 20, y, 1010, "3/4 from the front, bipod deployed", im=on_white(r("SV98_q")))
    y += p.put(None, 1050, y, 1010, "3/4 from behind", im=on_white(r("SV98_q_back"))) + 20
    p.put(None, 20, y, 400, "front", im=on_white(r("SV98_front")))
    p.put(None, 440, y, 780, "bolt forward", im=on_white(ImageOps.mirror(r("SV98_bolt_open"))))
    y += p.put(None, 1240, y, 780, "bolt back (bolt_fired)", im=on_white(ImageOps.mirror(r("SV98_bolt_back")))) + 20
    gom = Image.open(os.path.join(A.G, "textures", "item_M24.png")).convert("RGBA")
    p.icons(20, y, [(gom, "M24 (GoM)"), (icons["SV98"], "SV-98"), (icons[MAG], "SV-98 10Rds")])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
