#!/usr/bin/env python3
"""Uzi, Mini Uzi and Micro Uzi inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_uzi_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files and textures build_uzi.py
exported, with Post-93's make_mp7_art.py renderer and its cameras and lights (post93/mp7_icon_cameras.json, fitted on
GoM's own icons):

    gun        item_MP5.png                 each gun, stock folded, with its standard magazine (Uzi 32, Mini / Micro 20);
                                            the Mini and Micro are modelled upside down (held like a pistol) and are
                                            turned upright for the icon, as the MP7
    magazine   item_9x19Magazine30_MP5.png  every Uzi magazine

--renders DIR (render_uzi.py's output) also writes docs/uzi_preview.png: each gun's left side with the outline traced
from its reference photo laid over it (references/uzi/*_outline.json; the photos are not in the repo), other views,
the long magazines, the Mk9, GoM's MP5 / MP5K / MAC-10 at the same scale, and the icons beside GoM's.
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
PREVIEW = os.path.join(ROOT, "docs/uzi_preview.png")
PTS = json.load(open(os.path.join(HERE, "uzi_points.json")))
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx")
MAGS = ["9x19Magazine%d_UZI" % r for r in (20, 25, 32, 40, 50)]
GUN_MAG = {"UZI": "9x19Magazine32_UZI", "MINIUZI": "9x19Magazine20_UZI", "MICROUZI": "9x19Magazine20_UZI"}
OUTLINES = {"UZI": "uzi", "MINIUZI": "mini", "MICROUZI": "micro"}


def fbx(gun):
    return os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_%s.fbx" % gun)


def gun_objs(gun):
    """The gun with its stock folded and its standard magazine, turned upright when held like a pistol."""
    p = PTS[gun]
    handgun = p["_extras"]["handgun_hold"]
    up = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0 if handgun else 0.0, 0.0]}
    stock = (A.load_game(fbx(gun), "UZI_STOCK_FOLDED") if gun == "UZI"
             else A.attach(A.load_game(fbx(gun), gun + "_STOCK"), p["stock_folded"]))
    objs = [(A.load_game(fbx(gun), gun + "_BODY"), 0), (A.load_game(fbx(gun), gun + "_BOLT"), 0), (stock, 0),
            (A.attach(A.load_game(FBX_MAGS, GUN_MAG[gun]), p["magazine"]), 1)]
    objs = [(A.attach(t, up), i) for t, i in objs]
    return objs, [A.img(os.path.join(TEX, gun + ".png")), A.img(os.path.join(TEX, GUN_MAG[gun] + ".png"))]


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    scenes = {gun: ("gun",) + gun_objs(gun) for gun in GUN_MAG}
    for n in MAGS:
        scenes[n] = ("magazine", [(A.load_game(FBX_MAGS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % name))
        made[name] = icon
    return made


def check():
    for path, names in [(fbx(g), None) for g in GUN_MAG] + [(FBX_MAGS, None)]:
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-24s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return Image.open(os.path.join(renders, name + ".png")).convert("RGBA")


def outline_panel(renders, gun):
    """A gun's left-side render (the photo's state) with its photo's traced outline (red) and their silhouette IoU.
    The left-side render already has the photo's handedness (muzzle right)."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))[gun]
    (W, Hh), s = cam["size"], cam["px_per_mm"]
    Lc, Hc = cam["photo_centre_mm"]
    out = json.load(open(os.path.join(ROOT, "references/uzi/%s_outline.json" % OUTLINES[gun])))["outline"]
    pts = [(W / 2 - (L - Lc) * s, Hh / 2 - (H - Hc) * s) for L, H in out]
    im = render(renders, gun + "_left")
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
    p = B.Page(renders, 2480, 4700, "IMI Uzi, Mini Uzi and Micro Uzi, GunsOfTien.UZI / MINIUZI / MICROUZI: Workbench "
                                    "renders of the exported FBX files + textures, muzzle right")
    y = 70
    for gun, x, w in (("UZI", 20, 1220), ("MINIUZI", 1250, 1210)):
        ov, iou = outline_panel(renders, gun)
        p.d.text((x + 10, y), "%s left side, red = outline traced from its photo, overlap %.1f%%" % (gun, iou * 100),
                 fill=(40, 40, 40), font=p.FS)
        p.put(None, x, y + 34, w, im=ov)
        print("%s silhouette IoU %.3f" % (gun, iou))
    y += 34 + 640
    ov, iou = outline_panel(renders, "MICROUZI")
    p.d.text((30, y), "MICROUZI left side, stock folded, overlap %.1f%%" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 800, im=ov)
    print("MICROUZI silhouette IoU %.3f" % iou)

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("UZI_other_left", 840, y + 34, 800, "Uzi, stock deployed")
    put("MICROUZI_other_left", 1660, y + 34, 800, "Micro Uzi, stock deployed")
    y += 34 + 640
    put("UZI_q_right", 20, y, 800, "Uzi from behind, right (ejection port)")
    put("MINIUZI_q_right", 840, y, 800, "Mini Uzi, right")
    put("MICROUZI_q_right", 1660, y, 800, "Micro Uzi, right")
    y += 560
    put("MINIUZI_other_q", 20, y, 800, "Mini Uzi, stock folded along the right")
    put("MINIUZI_other_top", 840, y, 800, "Mini Uzi from above, stock folded")
    put("UZI_nomag_under", 1660, y, 800, "Uzi from below, no magazine")
    y += 560
    put("UZI_mk9_left", 20, y, 1200, "Uzi with the 9x19mm SMG mount device and Mk9, 32-round magazine")
    put("MICROUZI_mk9_left", 1240, y, 1200, "Micro Uzi with the Mk9")
    y += 560
    put("UZI_50_left", 20, y, 800, "Uzi, 50-round magazine")
    put("MINIUZI_40_left", 840, y, 800, "Mini Uzi, 40-round")
    put("MICROUZI_50_left", 1660, y, 800, "Micro Uzi, 50-round")
    y += 620
    for i, g in enumerate(("gom_MP5", "gom_MP5K", "gom_MAC10")):
        put(g, 20 + i * 820, y, 800, g[4:] + " (GoM) at the same scale")
    y += 440
    refs = [(Image.open(os.path.join(A.G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5.png", "item_MAC10.png", "item_9x19Magazine30_MP5.png")]
    p.icons(20, y, refs[:2] + [(icons[g], g) for g in GUN_MAG])
    p.icons(20, y + 260, refs[2:] + [(icons[n], n.split("_")[0][-2:] + " rounds") for n in MAGS])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
