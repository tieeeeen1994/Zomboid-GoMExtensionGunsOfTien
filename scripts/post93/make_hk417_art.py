#!/usr/bin/env python3
"""HK417 textures and inventory icons (Python 3 + Pillow).

    py scripts/post93/make_hk417_art.py            the magazine texture (before build_hk417.py's renders)
    py scripts/post93/make_hk417_art.py --icons    and the icons (after build_hk417.py)

- P/textures/weapons/GunsOfTienPost93/HK417_MAG.png (32x32): H&K's smoke-grey translucent polymer (left half: a dark
  grey-green with a little mottling, the rounds showing through as darker bands) and black (right half: the base
  plate, the window frames, the feed lips).
- P/textures/item_GunsOfTienPost93_HK417.png / _HK417S.png: the rifles on the SCARs' rifle camera and light
  (scar_icon_cameras.json, fitted on GoM's M4A1 icon), bare, sights up, stock in, with the 20-round magazine, as the
  HK416's (make_hk416_art.py);
- P/textures/item_GunsOfTienPost93_762x51Magazine10_HK417.png / 20: on the SCARs' rifle magazine camera with the MP7
  magazine light (as the SCAR-H's and the PMAGs').
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")


def mag_texture():
    im = Image.new("RGB", (32, 32))
    px = im.load()
    for y in range(32):
        for x in range(32):
            n = ((x * 7 + y * 13) % 5) - 2
            if x < 16:
                band = -6 if (y // 3) % 2 else 0                  # the rounds showing through
                px[x, y] = (62 + n + band, 67 + n + band, 62 + n + band)
            else:
                px[x, y] = (24 + n // 2, 25 + n // 2, 24 + n // 2)
    out = os.path.join(TEX, "HK417_MAG.png")
    im.save(out)
    print("wrote", out)


def icons():
    import make_mp7_art as A
    pts = json.load(open(os.path.join(HERE, "hk417_points.json")))
    fbx_gun = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK417.fbx")
    fbx_mags = os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_HK417_magazines.fbx")
    gun_tex = A.img(os.path.join(A.G, "textures/weapons/firearms/assault_rifles/AR15.png"))
    mark_tex = A.img(os.path.join(TEX, "HK416_MARKINGS.png"))
    mag_tex = A.img(os.path.join(TEX, "HK417_MAG.png"))
    scar = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))
    mp7 = json.load(open(A.CAMERAS_JSON))
    made = {}
    for gun in ("HK417", "HK417S"):
        p = pts[gun]
        objs = [(A.load_game(fbx_gun, gun + "_BODY"), 0)]
        objs += [(A.load_game(fbx_gun, n), 0) for n in ("HK417_BOLT", "HK417_CHARGING_HANDLE")]
        objs.append((A.attach(A.load_game(fbx_gun, "HK417_STOCK"), p["stock_folded"]), 0))
        objs.append((A.load_game(fbx_gun, "HK417_MARKINGS"), 1))
        objs.append((A.attach(A.load_game(fbx_mags, "762x51Magazine20_HK417"), p["magazine"]), 2))
        made[gun] = A.shade(objs, [gun_tex, mark_tex, mag_tex], dict(scar["rifle"]["camera"]), scar["rifle"]["light"])
    for n in (10, 20):
        name = "762x51Magazine%d_HK417" % n
        made[name] = A.shade([(A.load_game(fbx_mags, name), 0)], [mag_tex], dict(scar["rifle_magazine"]["camera"]),
                             mp7["magazine"]["light"])
    for name, icon in made.items():
        icon.save(os.path.join(P93, "textures", "item_GunsOfTienPost93_%s.png" % name))
    print("wrote the icons:", ", ".join(made))


if __name__ == "__main__":
    mag_texture()
    if "--icons" in sys.argv:
        icons()
