#!/usr/bin/env python3
"""HK416 inventory icon (Python 3 + Pillow).

    py scripts/post93/make_hk416_art.py

P/textures/item_GunsOfTienPost93_HK416.png (32x32 RGBA) rendered from the FBX build_hk416.py exported on GoM's AR15
texture, with make_mp7_art.py's renderer and the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's
item_M4A1.png), as the Mk 11 (make_mk11_art.py): bare, sights up, stock in, with GoM's STANAG 30. The review sheet is
make_hk416_preview.py's (docs/post93_hk416_preview.png).

Also P/textures/weapons/GunsOfTienPost93/HK416_MARKINGS.png (32x16): the selector labels' texture (build_hk416.py
HK416_MARKINGS; GoM's AR15 texture has no red or white): the left half H&K's red label, the right half the white one,
each with a dark pictogram stroke (a round, or the crossed round of safe) and a darker rim.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
from PIL import Image, ImageDraw            # noqa: E402

ROOT = A.ROOT
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
PTS = json.load(open(os.path.join(HERE, "hk416_points.json")))
FBX_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK416.fbx")
FBX_MAG = os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx")
GUN_TEX = os.path.join(A.G, "textures/weapons/firearms/assault_rifles/AR15.png")
MAG_TEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles/556x45Magazine30_STANAG.png")


def markings():
    im = Image.new("RGB", (32, 16))
    d = ImageDraw.Draw(im)
    for x0, fill, rim, mark in ((0, (206, 30, 36), (150, 18, 22), (90, 10, 12)),
                                (16, (232, 232, 226), (170, 170, 166), (40, 40, 40))):
        d.rectangle((x0, 0, x0 + 15, 15), fill=rim)
        d.rectangle((x0 + 1, 1, x0 + 14, 14), fill=fill)
        d.rectangle((x0 + 4, 6, x0 + 11, 9), fill=mark)          # a round lying along the label
    d.line((21, 4, 26, 11), fill=(40, 40, 40))                  # crossed out on the safe label
    out = os.path.join(P93, "textures/weapons/GunsOfTienPost93/HK416_MARKINGS.png")
    im.save(out)
    return out


def main():
    print("wrote", markings())
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    objs = [(A.load_game(FBX_GUN, n), 0) for n in ("HK416_BODY", "HK416_BOLT", "HK416_CHARGING_HANDLE")]
    objs.append((A.attach(A.load_game(FBX_GUN, "HK416_STOCK"), PTS["stock_folded"]), 0))
    objs.append((A.attach(A.load_game(FBX_MAG, "556x45Magazine30_STANAG"), PTS["magazine"]), 1))
    icon = A.shade(objs, [A.img(GUN_TEX), A.img(MAG_TEX)], dict(rifle["camera"]), rifle["light"])
    icon.save(os.path.join(P93, "textures/item_GunsOfTienPost93_HK416.png"))
    print("wrote the HK416 icon")


if __name__ == "__main__":
    main()
