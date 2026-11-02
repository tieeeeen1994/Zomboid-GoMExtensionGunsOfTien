#!/usr/bin/env python3
"""RPK and RPK-74 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_rpk_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files build_rpk.py exported and GoM's
AK textures, with Post-93's make_mp7_art.py renderer:

    guns       the SCARs' rifle camera and light (post93/scar_icon_cameras.json, fitted on GoM's item_M4A1.png), as the
               AUG's: the RPK with its 40 and the RPK-74 with GoM's Bakelite 45 (drawn at build_rpk.py's SCALE, as the
               game draws it on them), bipods folded
    magazine   the RPK's 40 straight from the side (make_aug_art.py's MAG_CAMERA and magazine light), on GoM's 30's
               texture

--renders DIR (render_rpk.py's output) also writes docs/rpk_preview.png: both guns beside the reference photos at the
same scale (references/rpk, not in the repo: the RPK photo levelled, the RPK-74 photo as it is), the bipods, the RPK's
magazines, GoM's AKs at the same drawn scale, and the icons beside GoM's AK icons.
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402
import make_aug_art as AUG                 # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/rpk_preview.png")
PTS = json.load(open(os.path.join(HERE, "rpk_points.json")))
SCALE = PTS["_extras"]["scale"]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPK.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPK_magazines.fbx")
GOM_TEX = os.path.join(A.G, "textures/weapons/firearms/assault_rifles")
GOM_MTEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles")
GOM_MAGS = os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx")
MAG40 = "762x39Magazine40_RPK"
DRUM75 = "762x39Drum75_RPK"
DRUM_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/762x39Drum75_RPK.png")
RIFLE_CAMERAS = os.path.join(HERE, "post93/scar_icon_cameras.json")
REFS = os.path.join(ROOT, "references/rpk")


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in ps], uvs) for ps, uvs in tris]


def gun_objs(gun):
    gom = {"RPK": "AK47", "RPK74": "AK74"}[gun]
    if gun == "RPK":
        mag, mtex = A.load_game(FBX_MAGS, MAG40), "762x39Magazine30"
    else:
        # GoM's Bakelite 45: node 545x39Magazine45, its geometry named after GoM's source file
        mag, mtex = scaled(A.load_game(GOM_MAGS, "mag 545 45 new.smd"), SCALE), "545x39Magazine45"
    objs = [(A.load_game(FBX_GUN, gun + "_BODY"), 0), (A.load_game(FBX_GUN, gun + "_BOLT"), 0),
            (A.load_game(FBX_GUN, gun + "_BIPOD_FOLDED"), 0), (A.attach(mag, PTS[gun]["magazine"]), 1)]
    return objs, [A.img(os.path.join(GOM_TEX, gom + ".png")), A.img(os.path.join(GOM_MTEX, mtex + ".png"))]


def make_icons():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    scenes = {g: (rifle,) + gun_objs(g) for g in ("RPK", "RPK74")}
    mag_light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    # each fitted to the icon box on its own (a drum and a box at one scale would leave the box tiny)
    for n, tex in ((MAG40, os.path.join(GOM_MTEX, "762x39Magazine30.png")), (DRUM75, DRUM_TEX)):
        objs = {n: [(A.load_game(FBX_MAGS, n), 0)]}
        # the drum faces forward (as GoM's drums): from the side it is a slab, so a three-quarter view of its front
        # face, as GoM frames its AK-74 drum's icon
        cam = AUG.mag_cameras(objs)[n] if n == MAG40 else {"yaw": 320.0, "pitch": 0.0, "roll": 0.0, "bbox": [1, 1, 31, 31]}
        scenes[n] = ({"camera": cam, "light": mag_light}, objs[n], [A.img(tex)])
    made = {}
    for name, (fit, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fit["camera"]), fit["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % name))
        made[name] = icon
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


def photo(name, px_per_mm, length_mm):
    """A reference photo scaled to the renders' px per mm by the gun's real length (its dark pixels' extent)."""
    path = os.path.join(REFS, name)
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    import numpy as np
    dark = np.array(im.convert("L")) < 200
    xs = np.nonzero(dark.any(0))[0]
    f = length_mm * px_per_mm / (xs.max() - xs.min())
    return im.resize((int(im.width * f), int(im.height * f))).convert("RGBA")


def sheet(renders, icons):
    p = B.Page(renders, 2480, 4700, "RPK and RPK-74, GunsOfTien.RPK / RPK74: Workbench renders of the exported FBX "
                                    "files with GoM's textures, beside the reference photos at the same scale")
    flip = lambda im: im.transpose(Image.FLIP_LEFT_RIGHT)
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    y = 70
    ph = photo("rpk_level.png", 1.6, 1040.0)
    if ph:
        p.put(None, 20, y, 1200, "RPK, Commons \"7.62mm light machine gun RPK\" (levelled 10.4 degrees)", im=ph)
    p.put(None, 1240, y, 1200, "RPK, bipod deployed, the 40 (game view)", im=on_white(flip(r("RPK_left_deployed"))))
    y += 620
    ph = photo("Soviet_RPK-74.jpg", 1.6, 1060.0)
    if ph:
        p.put(None, 20, y, 1200, "RPK-74, Commons \"Soviet RPK-74\" (butt at the frame's edge)", im=ph)
    p.put(None, 1240, y, 1200, "RPK-74, bipod deployed, GoM's Bakelite 45 (the photo's side)",
          im=on_white(r("RPK74_left_deployed")))
    y += 620
    p.put(None, 20, y, 1200, "RPK, bipod folded under the barrel", im=on_white(flip(r("RPK_left_folded"))))
    p.put(None, 1240, y, 420, "RPK-74, front", im=on_white(r("RPK74_front_deployed")))
    p.put(None, 1680, y, 420, "RPK, front", im=on_white(r("RPK_front_deployed")))
    y += 620
    p.put(None, 20, y, 1200, "GoM's AK-47 at the same drawn scale", im=on_white(flip(r("RPK_gom_AK47"))))
    p.put(None, 1240, y, 1200, "GoM's AK-74 at the same drawn scale", im=on_white(flip(r("RPK74_gom_AK74"))))
    y += 560
    p.put(None, 20, y, 800, "GoM's 30 (at our scale)", im=on_white(flip(r("RPK_with_762x39Magazine30"))))
    p.put(None, 840, y, 800, "the RPK's 40 (GoM's 30 bent on along its arc)",
          im=on_white(flip(r("RPK_with_" + MAG40))))
    p.put(None, 1660, y, 800, "GoM's 75 (at our scale)", im=on_white(flip(r("RPK_with_762x39Magazine75"))))
    y += 420
    museum = os.path.join(REFS, "Izhmash_museum_1.jpg")
    if os.path.exists(museum):
        crop = Image.open(museum).convert("RGBA").crop((0, 930, 560, 1180))
        p.put(None, 20, y, 1000, "the 75 drum: Commons \"Izhmash museum 1\" (RPK, right side)", im=crop)
    p.put(None, 1040, y, 1400, "the RPK's 75-round drum (the photo's side)", im=on_white(r("RPK_drum_right")))
    y += 560
    for i, n in enumerate(("762x39Drum75_RPK_side", "762x39Drum75_RPK_q", "762x39Drum75_RPK_front")):
        p.put(None, 20 + i * 520, y, 500, ("drum: side", "drum: 3/4", "drum: front")[i], im=on_white(r(n)))
    p.put(None, 1580, y, 880, "bipod deployed, drum", im=on_white(r("RPK_drum_q")))
    y += 540
    p.put(None, 20, y, 1200, "GoM's AK-47 with the RPK's 40 (GoM's size)",
          im=on_white(flip(r("gom_AK47_with_" + MAG40))))
    p.put(None, 1240, y, 1200, "GoM's AK-47 with the drum (GoM's size)", im=on_white(flip(r("gom_AK47_with_" + DRUM75))))
    y += 560
    refs = [(Image.open(os.path.join(A.G, "textures", n)).convert("RGBA"), n[5:-4] + " (GoM)")
            for n in ("item_AK47.png", "item_AK74.png", "item_762x39Magazine30.png")]
    p.icons(20, y, refs + [(icons[n], n) for n in ("RPK", "RPK74", MAG40, DRUM75)])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
