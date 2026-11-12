#!/usr/bin/env python3
"""SR-25 inventory icons (Python 3 + Pillow).

    py scripts/make_sr25_art.py

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files build_sr25.py exported and
GoM's textures, with Post-93's make_mp7_art.py renderer, as the RPKs' (make_rpk_art.py):

    gun        the SCARs' rifle camera and light (post93/scar_icon_cameras.json, fitted on GoM's item_M4A1.png): the
               SR-25 with KAC's 20 and its bipod folded, on GoM's AR15 texture
    magazine   KAC's 20 from the side (make_aug_art.py's MAG_CAMERA, the magazine light), on GoM's STANAG 20 texture

The review sheet is make_sr25_preview.py's (docs/sr25_preview.png).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_aug_art as AUG                 # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
ICONS = os.path.join(MEDIA, "textures")
PTS = json.load(open(os.path.join(HERE, "sr25_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SR25.fbx")
FBX_MAG = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx")
GUN_TEX = os.path.join(A.G, "textures/weapons/firearms/assault_rifles/AR15.png")
MAG_TEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles/556x45Magazine20_STANAG.png")
MAG = "762x51Magazine20_SR25"
RIFLE_CAMERAS = os.path.join(HERE, "post93/scar_icon_cameras.json")


def main():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    gun = [(A.load_game(FBX_GUN, n), 0) for n in ("SR25_BODY", "SR25_BOLT", "SR25_CHARGING_HANDLE",
                                                   "SR25_BIPOD_FOLDED")]
    gun.append((A.attach(A.load_game(FBX_MAG, MAG), PTS["magazine"]), 1))
    icon = A.shade(gun, [A.img(GUN_TEX), A.img(MAG_TEX)], dict(rifle["camera"]), rifle["light"])
    icon.save(os.path.join(ICONS, "item_GunsOfTien_SR25.png"))
    mag_light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    objs = {MAG: [(A.load_game(FBX_MAG, MAG), 0)]}
    icon = A.shade(objs[MAG], [A.img(MAG_TEX)], dict(AUG.mag_cameras(objs)[MAG]), mag_light)
    icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % MAG))
    print("wrote the SR-25 icons")


if __name__ == "__main__":
    main()
