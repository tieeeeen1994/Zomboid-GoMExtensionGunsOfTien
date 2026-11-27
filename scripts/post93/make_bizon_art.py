#!/usr/bin/env python3
"""PP-19 Bizon family inventory icons and the magazines' off-hand points (Python 3 + Pillow).

    py scripts/post93/make_bizon_art.py

Run after build_bizon.py (which rewrites bizon_points.json) and before gen_post93_guns.py (which reads `_mag_prop2`).

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) with make_mp7_art.py's renderer, as the 9A-91's
(make_9a91_art.py): the guns on the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's M4A1
icon), lit a third brighter (blued black all over), each with its standard magazine and its stock open (user,
2026-11-28: "for the icons, don't use folded versions"); the magazines on make_aug_art.py's magazine camera. The Vityaz pair's second side
(`_PAIR_2`) shares the pair's icon, as GoM's MP5 jungle pair shares one.

`_mag_prop2` (written into bizon_points.json): each magazine's Bip01_Prop2, for GoM's AK reload, which draws the
magazine in the off hand: GoM's AS VAL 20's point (the 9A-91's source) with its offset moved so our magazine's middle
lands where GoM's does (build_mp7.py bip01_prop2, in game coordinates).
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_aug_art as AUG                 # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
ICONS = os.path.join(MEDIA, "textures")
POINTS_JSON = os.path.join(HERE, "bizon_points.json")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_BIZON.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_BIZON_magazines.fbx")
TEXDIR = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
RIFLE_CAMERAS = os.path.join(HERE, "scar_icon_cameras.json")
MAGS = ["9x18Magazine64_BIZON", "9x19Magazine53_BIZON", "762x25Magazine45_BIZON", "762x25Magazine35_BIZON",
        "9x19Magazine30_VITYAZ", "9x19Magazine30_VITYAZ_PAIR"]
# gun -> (nodes, its magazine, the point it hangs at)
GUNS = {
    "BIZON": (("BIZON_BODY", "BIZON_BOLT"), "9x18Magazine64_BIZON", ("magazine",)),
    "BIZON201": (("BIZON201_BODY", "BIZON_BOLT", "BIZON_STOCK_DEPLOYED"), "9x19Magazine53_BIZON", ("magazine",)),
    "BIZON207": (("BIZON207_BODY", "BIZON_BOLT"), "762x25Magazine35_BIZON", ("BIZON207", "magazine_box")),
    "VITYAZ": (("VITYAZ_BODY", "BIZON_BOLT", "BIZON_STOCK_DEPLOYED"), "9x19Magazine30_VITYAZ", ("VITYAZ", "magazine")),
}
GOM_ASVAL_PROP2 = ([0.0279, 0.0937, -0.0020], [-86.2737, 31.4012, -93.4148])   # GoM's 9x39Magazine20


def point(pts, path):
    for key in path:
        pts = pts[key]
    return pts


def make_icons(pts):
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    gun_light = dict(rifle["light"], coef=[[a * 1.35, b * 1.35] for a, b in rifle["light"]["coef"]])
    tex = A.img(os.path.join(TEXDIR, "BIZON.png"))
    for gun, (nodes, mag, at) in GUNS.items():
        objs = [(A.load_game(FBX_GUN, n), 0) for n in nodes]
        objs.append((A.attach(A.load_game(FBX_MAGS, mag), point(pts, at)), 1))
        icon = A.shade(objs, [tex, A.img(os.path.join(TEXDIR, mag + ".png"))], dict(rifle["camera"]), gun_light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
    light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    objs = {m: [(A.load_game(FBX_MAGS, m), 0)] for m in MAGS}
    cams = AUG.mag_cameras(objs)
    for m in MAGS:
        icon = A.shade(objs[m], [A.img(os.path.join(TEXDIR, m + ".png"))], cams[m], light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % m))


def centre(tris):
    ps = [p for t, _ in tris for p in t]
    return [sum(p[k] for p in ps) / len(ps) for k in range(3)]


def rotate_xyz(r, v):
    """rotateXYZ (JOML, degrees) applied to v: Rx . Ry . Rz . v"""
    x, y, z = v
    rx, ry, rz = [math.radians(a) for a in r]
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    return [x, y, z]


def prop2_points():
    gom = centre(A.load_game(os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx"), "9x39Magazine20"))
    a, r = GOM_ASVAL_PROP2
    out = {}
    for m in MAGS:
        ours = centre(A.load_game(FBX_MAGS, m))
        t = rotate_xyz(r, [gom[k] - ours[k] for k in range(3)])
        out[m] = {"offset": [round(a[k] + t[k], 4) for k in range(3)], "rotate": list(r)}
    return out


def main():
    pts = json.load(open(POINTS_JSON))
    make_icons(pts)
    pts["_mag_prop2"] = prop2_points()
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    print("icons written under", ICONS, "; _mag_prop2 in", POINTS_JSON)


if __name__ == "__main__":
    main()
