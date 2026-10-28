#!/usr/bin/env python3
"""Steyr AUG A3, AUG Para and AUG HBAR inventory icons, FBX check and the preview sheet (Python 3 + Pillow).

    py scripts/post93/make_aug3_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTienPost93_<name>.png, M = Post-93's media) rendered from the FBX files and
textures build_aug3.py exported, the way the main mod's make_aug_art.py makes the A1's (make_mp7_art.py's renderer):

    guns       the SCARs' rifle camera and light (scar_icon_cameras.json, fitted on GoM's item_M4A1.png): each gun with
               its grip folded and its standard magazine (A3: the A1's 30, Para: the 25, HBAR: the 30, its bipod
               folded); the A3 and HBAR draw the A1's charging handle and grip with the A1's texture
    magazines  straight from the side (make_aug_art.MAG_CAMERA), the gun's light 15% brighter, each gun's pair at
               the longer one's scale

--renders DIR (the folder holding render_aug3.py's auga3 / augpara / aughbar outputs) also writes
docs/aug3_preview.png: each gun from both sides (game view), fitted with GoM's parts, the HBAR on its bipod, the
magazines, and the icons beside GoM's FAMAS, AK-47 and MP5 icons.
"""

import json
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402
import make_aug_art as AUG1                # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
ICONS = os.path.join(MEDIA, "textures")
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
MAIN_TEX = os.path.join(MAIN, "textures/weapons/GunsOfTien")
A1_FBX = os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_AUG.fbx")
A1_MAGS = os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_AUG_magazines.fbx")
PREVIEW = os.path.join(ROOT, "docs/aug3_preview.png")
GUNS = ["AUGA3", "AUGPARA", "AUGHBAR"]
MAGS = {"AUGPARA": ["9x19Magazine25_AUG", "9x19Magazine32_AUG"],
        "AUGHBAR": ["762x39Magazine30_AUG", "762x39Magazine50_AUG"]}


def fbx(gun):
    return os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_%s.fbx" % gun)


def gun_objs(gun):
    """The gun with its grip folded and its standard magazine; (tris, texture index) pairs and their textures."""
    pts = json.load(open(os.path.join(HERE, gun.lower() + "_points.json")))
    texes = [A.img(os.path.join(TEX, gun + ".png"))]
    objs = [(A.load_game(fbx(gun), gun + "_BODY"), 0)]
    if gun == "AUGPARA":
        objs += [(A.load_game(fbx(gun), "AUGPARA_BOLT"), 0),
                 (A.attach(A.load_game(fbx(gun), "AUGPARA_FOREGRIP"), pts["foregrip_folded"]), 0)]
    else:
        texes.append(A.img(os.path.join(MAIN_TEX, "AUG.png")))
        objs += [(A.load_game(A1_FBX, "AUG_BOLT"), 1),
                 (A.attach(A.load_game(A1_FBX, "AUG_FOREGRIP"), pts["foregrip_folded"]), 1)]
    if gun == "AUGHBAR":
        objs.append((A.load_game(fbx(gun), "AUGHBAR_BIPOD_FOLDED"), 0))
    if gun == "AUGA3":
        mag_fbx, mag, mag_tex = A1_MAGS, "556x45Magazine30_AUG", os.path.join(MAIN_TEX, "556x45Magazine30_AUG.png")
    else:
        mag = MAGS[gun][0]
        mag_fbx, mag_tex = FBX_MAGS, os.path.join(TEX, mag + ".png")
    texes.append(A.img(mag_tex))
    objs.append((A.attach(A.load_game(mag_fbx, mag), pts["magazine"]), len(texes) - 1))
    return objs, texes


def make_icons():
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    mag_light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    made = {}
    for gun in GUNS:
        objs, texes = gun_objs(gun)
        made[gun] = A.shade(objs, texes, dict(rifle["camera"]), rifle["light"])
    for gun, names in MAGS.items():
        objs = {n: [(A.load_game(FBX_MAGS, n), 0)] for n in names}
        for n, cam in AUG1.mag_cameras(objs).items():
            made[n] = A.shade(objs[n], [A.img(os.path.join(TEX, n + ".png"))], cam, mag_light)
    for name, icon in made.items():
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
    return made


def check():
    for path in [fbx(g) for g in GUNS] + [FBX_MAGS]:
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, gun, name):
    """A render_aug3.py image in the game's handedness (every render is mirrored)."""
    im = Image.open(os.path.join(renders, gun.lower(), name + ".png")).convert("RGBA")
    return ImageOps.mirror(im)


def sheet(renders, icons):
    p = B.Page(renders, 2480, 4500, "Steyr AUG A3, AUG Para, AUG HBAR (GunsOfTienPost93): Workbench renders of the "
                                    "exported FBX files + textures, the game's view")
    y = 70
    rows = [("AUGA3", "Steyr AUG A3 Assault Rifle: green, the A3 upper and short top rail, right rail; A1 magazine"),
            ("AUGPARA", "Steyr AUG Para Submachine Gun: sand, 420 mm barrel, 9mm adapter, 25-round magazine"),
            ("AUGHBAR", "Steyr AUG HBAR Light Machine Gun: 621 mm heavy barrel, folding bipod, 7.62x39 magazine")]
    for gun, title in rows:
        p.heading(30, y, title)
        y += 40
        h1 = p.put(None, 20, y, 1200, "left side, grip down", im=render(renders, gun, gun + "_left"))
        p.put(None, 1240, y, 1200, "right side", im=render(renders, gun, gun + "_right"))
        y += h1 + 10
        extra = (gun + "_bipod_q_left", "on its bipod") if gun == "AUGHBAR" else \
            (gun + "_suppressed_right", "ElcanX2, mount device and suppressor")
        h2 = p.put(None, 20, y, 1200, "GoM's ElcanX2, SR7 on the optional left rail, AimRight on the right rail",
                   im=render(renders, gun, gun + "_dressed_q_left"))
        h3 = p.put(None, 1240, y, 1200, extra[1], im=render(renders, gun, extra[0]))
        y += max(h2, h3) + 30
    x = 20
    for gun, names in MAGS.items():
        for n in names:
            rounds = n.split("Magazine")[1].split("_")[0]
            p.put(None, x, y, 300, rounds + "-round", im=render(renders, gun, "mag%s_q" % rounds))
            x += 320
    y += 380
    refs = [(Image.open(os.path.join(A.G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_FAMAS.png", "item_AK47.png", "item_MP5.png")]
    p.icons(20, y, refs + [(icons[g], g) for g in GUNS])
    p.icons(20, y + 270, [(icons[n], n) for names in MAGS.values() for n in names])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
