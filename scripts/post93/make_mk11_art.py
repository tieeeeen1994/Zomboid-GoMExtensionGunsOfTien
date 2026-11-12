#!/usr/bin/env python3
"""Mk 11 Mod 0 inventory icon (Python 3 + Pillow).

    py scripts/post93/make_mk11_art.py

P/textures/item_GunsOfTienPost93_MK11.png (32x32 RGBA) rendered from the FBX build_mk11.py exported on GoM's AR15
texture, with make_mp7_art.py's renderer and the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's
item_M4A1.png), as the main mod's SR-25 (make_sr25_art.py): bare, with the main mod's KAC 20. The review sheet is
make_mk11_preview.py's (docs/post93_mk11_preview.png).
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
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
PTS = json.load(open(os.path.join(HERE, "mk11_points.json")))
FBX_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_MK11.fbx")
FBX_MAG = os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx")
GUN_TEX = os.path.join(A.G, "textures/weapons/firearms/assault_rifles/AR15.png")
MAG_TEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles/556x45Magazine20_STANAG.png")


def main():
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    objs = [(A.load_game(FBX_GUN, n), 0) for n in ("MK11_BODY", "MK11_BOLT", "MK11_CHARGING_HANDLE")]
    objs.append((A.attach(A.load_game(FBX_MAG, "762x51Magazine20_SR25"), PTS["magazine"]), 1))
    icon = A.shade(objs, [A.img(GUN_TEX), A.img(MAG_TEX)], dict(rifle["camera"]), rifle["light"])
    icon.save(os.path.join(P93, "textures/item_GunsOfTienPost93_MK11.png"))
    print("wrote the Mk 11 icon")


if __name__ == "__main__":
    main()
