#!/usr/bin/env python3
"""SVU inventory icon, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_svu_art.py [--renders DIR]

Icon (32x32 RGBA, M/textures/item_GunsOfTien_SVU.png) rendered from the FBX build_svu.py exported, SVU.png and GoM's
SVD magazine at our scale, with Post-93's make_mp7_art.py renderer and the SCARs' rifle camera and light
(post93/scar_icon_cameras.json, fitted on GoM's item_M4A1.png), as the AUG's and RPKs': sights raised, no optic.

--renders DIR (render_svu.py's output) also writes docs/svu_preview.png: the gun's right side over the measuring
photo at the same scale (references/svu/svu_a/kuzmin2015_svua_01.jpg, Vitaly V. Kuzmin, 2.026 px a mm), the left
side folded with GoM's AK mount and PSO-1 over the left photo, the 3/4 views and front, and the icon beside GoM's
SVD's.
"""

import json
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/svu_preview.png")
PTS = json.load(open(os.path.join(HERE, "svu_points.json")))
SCALE = PTS["_extras"]["scale"]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SVU.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/SVU.png")
GOM_MAGS = os.path.join(A.G, "models_X/weapons/magazines/semi_rifles.fbx")
GOM_MTEX = os.path.join(A.G, "textures/weapons/magazines/semi_rifles/762x54Magazine10_SVD.png")
RIFLE_CAMERAS = os.path.join(HERE, "post93/scar_icon_cameras.json")
REFS = os.path.join(ROOT, "references/svu")


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in ps], uvs) for ps, uvs in tris]


def make_icon():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    mag = scaled(A.load_game(GOM_MAGS, "762x54Magazine10_SVD"), SCALE)
    objs = [(A.load_game(FBX_GUN, "SVU_BODY"), 0), (A.load_game(FBX_GUN, "SVU_BOLT"), 0),
            (A.attach(mag, PTS["magazine"]), 1)]
    icon = A.shade(objs, [A.img(TEX), A.img(GOM_MTEX)], dict(rifle["camera"]), rifle["light"])
    icon.save(os.path.join(ICONS, "item_GunsOfTien_SVU.png"))
    return icon


def check():
    objects, unit, lcl = A.header_check(FBX_GUN)
    print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(FBX_GUN), objects, unit))
    for n, rot, scl in lcl:
        mn, mx = A.bounds(A.load_game(FBX_GUN, n))
        print("  %-14s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def on_white(im):
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg


def gun_strip(render, flip):
    """A render (2 px a real mm) trimmed to the gun, the butt at x = 20."""
    import numpy as np
    im = Image.open(render).convert("RGBA")
    if flip:
        im = ImageOps.mirror(im)
    a = np.array(im)[..., 3]
    xs = np.nonzero(a.max(0) > 0)[0]
    left = flip and xs.min() or xs.min()
    return on_white(im.crop((left - 20, 0, left + 1860, im.height)))


def photo(name, butt_x, px_per_mm, top, bottom, flip=False):
    """The photo at 2 px a mm, the butt at x = 20 (flip: a left side, butt on the right, mirrored)."""
    path = os.path.join(REFS, name)
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    if flip:
        im = ImageOps.mirror(im)
        butt_x = im.width - butt_x
    f = 2.0 / px_per_mm
    im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    bx = round(butt_x * f)
    return im.crop((bx - 20, round(top * f), bx + 1860, round(bottom * f))).convert("RGBA")


def sheet(renders, icon):
    p = B.Page(renders, 1960, 3900, "SVU (OTs-03, 1991), GunsOfTien.SVU: Workbench renders of the exported FBX on "
                                    "SVU.png, each under its photo at the same scale (2 px a mm)")
    r = lambda n: os.path.join(renders, n + ".png")
    y = 70
    ph = photo("svu_a/kuzmin2015_svua_01.jpg", 62, 2.026, 420, 1000)
    if ph:
        y += p.put(None, 20, y, 1880, "right side, Vitaly V. Kuzmin (an SVU-A: outwardly the 1991 SVU)", im=ph) + 10
    y += p.put(None, 20, y, 1880, "the gun's right side, sights raised (game view)",
               im=gun_strip(r("SVU_right"), True)) + 30
    ph = photo("svu_a/kuzmin2015_svua_18.jpg", 1830, 1.972, 280, 900, flip=True)
    if ph:
        y += p.put(None, 20, y, 1880, "left side, Kuzmin (mirrored, butt left), PSO-1 on its side mount", im=ph) + 10
    y += p.put(None, 20, y, 1880, "left side, sights folded, GoM's AK mount and PSO-1 (mirrored like the photo)",
               im=gun_strip(r("SVU_FD_left_pso1"), False)) + 30
    p.put(None, 20, y, 930, "3/4 from the front left", im=on_white(Image.open(r("SVU_q"))))
    y += p.put(None, 970, y, 930, "3/4 from behind", im=on_white(Image.open(r("SVU_q_back")))) + 20
    p.put(None, 20, y, 300, "front", im=on_white(Image.open(r("SVU_front"))))
    gom = Image.open(os.path.join(A.G, "textures", "item_SVD.png")).convert("RGBA")
    p.icons(360, y + 40, [(gom, "SVD (GoM)"), (icon, "SVU")])
    p.save(PREVIEW)


def main():
    check()
    icon = make_icon()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icon)


if __name__ == "__main__":
    main()
