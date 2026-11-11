#!/usr/bin/env python3
"""Steyr TMP inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_tmp_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files and textures build_tmp.py
exported, with Post-93's make_mp7_art.py renderer and its cameras and lights (post93/mp7_icon_cameras.json, fitted on
GoM's own icons), as the Uzis':

    gun        item_MP5.png                 the TMP with its 30-round magazine, turned upright (it is modelled upside
                                            down, held like a pistol)
    magazine   item_9x19Magazine30_MP5.png  the 15 and the 30

--renders DIR (render_tmp.py's output) also writes docs/tmp_preview.png: the left side with the outline traced from
the photo laid over it (scripts/tmp_reference_outline.json; the photo is not in the repo), other views, the Mk9, GoM's
MP5K / MAC-10 at the same scale, and the icons beside GoM's.
"""

import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/tmp_preview.png")
PTS = json.load(open(os.path.join(HERE, "tmp_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TMP.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TMP_magazines.fbx")
MAGS = ["9x19Magazine15_TMP", "9x19Magazine30_TMP"]
GUN_MAG = MAGS[1]


def gun_objs():
    """The TMP with its 30-round magazine, turned upright."""
    up = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0, 0.0]}
    objs = [(A.load_game(FBX_GUN, "TMP_BODY"), 0), (A.load_game(FBX_GUN, "TMP_BOLT"), 0),
            (A.load_game(FBX_GUN, "TMP_HANDLE"), 0),
            (A.attach(A.load_game(FBX_MAGS, GUN_MAG), PTS["magazine"]), 1)]
    objs = [(A.attach(t, up), i) for t, i in objs]
    return objs, [A.img(os.path.join(TEX, "TMP.png")), A.img(os.path.join(TEX, GUN_MAG + ".png"))]


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    scenes = {"TMP": ("gun",) + gun_objs()}
    for n in MAGS:
        scenes[n] = ("magazine", [(A.load_game(FBX_MAGS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
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


def render(renders, name):
    return Image.open(os.path.join(renders, name + ".png")).convert("RGBA")


def outline_panel(renders):
    """The left-side render with the photo's traced outline (red) and their silhouette IoU. The render is game space
    (muzzle right, the photo's muzzle is left), so the outline is mirrored onto it."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))["TMP"]
    (W, Hh), s = cam["size"], cam["px_per_mm"]
    Lc, Hc = cam["photo_centre_mm"]
    out = json.load(open(os.path.join(HERE, "tmp_reference_outline.json")))["outline"]
    pts = [(W / 2 - (L - Lc) * s, Hh / 2 - (H - Hc) * s) for L, H in out]
    im = render(renders, "TMP_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    ImageDraw.Draw(bg).line(pts + pts[:1], fill=(220, 30, 30), width=2)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    a, b = im.getchannel("A").load(), mask.load()
    inter = union = 0
    for x in range(W):
        for y in range(Hh):
            m, p = a[x, y] > 128, b[x, y] > 128
            inter += m and p
            union += m or p
    return bg, inter / max(1, union)


def sheet(renders, icons):
    p = B.Page(renders, 2480, 3750, "Steyr TMP, GunsOfTien.TMP: Workbench renders of the exported FBX files + "
                                    "textures, muzzle right")
    y = 70
    ov, iou = outline_panel(renders)
    p.d.text((30, y), "Left side, red = outline traced from the photo (Commons, public domain), overlap %.1f%%"
             % (iou * 100), fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 1200, im=ov)
    print("TMP silhouette IoU %.3f" % iou)

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("TMP_right", 1250, y + 34, 1200, "Right side (ejection port)")
    y += 34 + 1100
    put("TMP_q_left", 20, y, 800, "From the front, left")
    put("TMP_q_right", 840, y, 800, "From behind, right")
    put("TMP_15_left", 1660, y, 800, "15-round magazine (flush with the grip)")
    y += 700
    put("TMP_racked_right", 20, y, 1200, "Racked: the cocking knob back, the bolt open")
    put("TMP_mk9_left", 1240, y, 1200, "With the 9x19mm SMG mount device and Mk9")
    y += 640
    for i, (g, label) in enumerate((("cmp_TMP", "TMP"), ("cmp_gom_MP5K", "MP5K (GoM)"), ("cmp_gom_MAC10",
                                                                                           "MAC-10 (GoM)"))):
        put(g, 20 + i * 820, y, 800, label + ", all three at the same scale (game units)")
    y += 640
    put("TMP_top", 20, y, 800, "From above")
    y += 300
    refs = [(Image.open(os.path.join(A.G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5K.png", "item_MAC10.png", "item_9x19Magazine30_MP5.png")]
    p.icons(20, y, refs + [(icons["TMP"], "TMP")] + [(icons[n], n.split("_")[0][-2:] + " rounds") for n in MAGS])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
