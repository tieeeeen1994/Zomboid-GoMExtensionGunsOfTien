#!/usr/bin/env python3
"""Groza inventory icons (Python 3 + Pillow).

    py scripts/post93/make_groza_art.py

P/textures/item_GunsOfTienPost93_GROZA1.png, _GROZA2, _GROZA4 and _GROZAGL (32x32 RGBA; the GP-25's launcher weapon
uses _GROZAGL, as GoM's M203_Weapon its M16A2_M203 icon), rendered from the FBX build_groza.py exported, with
make_mp7_art.py's renderer: the guns with the SCARs' rifle camera and light
(scar_icon_cameras.json, fitted on GoM's item_M4A1.png), each with its standard GoM magazine at our size (the `_GoT`
scale, gen_post93_guns.py GROZA_GOT_SCALE): the 7.62x39 30, the Bakelite 5.45 30, the AS VAL 20 (the Groza-4 with
its built-in can). The Groza-2 from the upright GROZA2_BODY (the game draws the turned GROZA2_HELD). Bare guns
otherwise, as GoM's icons. The review sheet is make_groza_preview.py's (docs/post93_groza_preview.png).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402

ROOT = A.ROOT
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")
PTS = json.load(open(os.path.join(HERE, "groza_points.json")))
FBX_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_GROZA.fbx")
FBX_PARTS = os.path.join(P93, "models_X/weapons/parts/GunsOfTienPost93_GROZA_parts.fbx")
GOM_MAGS = os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx")
GOM_MTEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles")
SCALE = round(0.603 / 0.645, 4)

# gun -> (body node, magazine point, GoM magazine geometry, its texture)
GUNS = {
    "GROZA1": ("GROZA_BODY", "magazine_762x39", "762x39Magazine30", "762x39Magazine30"),
    "GROZA2": ("GROZA2_BODY", "magazine_545x39", "mag 545 bak new.smd", "545x39Magazine30"),
    "GROZA4": ("GROZA4_BODY", "magazine", "9x39Magazine20", "9x39Magazine20"),
    "GROZAGL": ("GROZAGL_BODY", "magazine_762x39", "762x39Magazine30", "762x39Magazine30"),
}


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in ps], uvs) for ps, uvs in tris]


def main():
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    gun_tex = A.img(os.path.join(TEX, "GROZA.png"))
    for gun, (body, point, geo, mtex) in GUNS.items():
        mag = scaled(A.load_game(GOM_MAGS, geo), SCALE)
        objs = [(A.load_game(FBX_GUN, body), 0), (A.load_game(FBX_GUN, "GROZA_BOLT"), 0),
                (A.attach(mag, PTS[point]), 1)]
        texes = [gun_tex, A.img(os.path.join(GOM_MTEX, mtex + ".png"))]
        if gun == "GROZA4":
            objs.append((A.attach(A.load_game(FBX_PARTS, "GROZA_Suppressor"), PTS["canon"]), 2))
            texes.append(A.img(os.path.join(TEX, "GROZA_Suppressor.png")))
        icon = A.shade(objs, texes, dict(rifle["camera"]), rifle["light"])
        icon.save(os.path.join(P93, "textures/item_GunsOfTienPost93_%s.png" % gun))
    print("wrote the Groza icons")


if __name__ == "__main__":
    main()
