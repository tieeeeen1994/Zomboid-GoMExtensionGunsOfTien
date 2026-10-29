#!/usr/bin/env python3
"""UMP45 / UMP9 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_ump_art.py [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) rendered from the exported FBX files and textures
with make_mp7_art.py's renderer and its cameras and lights (mp7_icon_cameras.json), which were fitted on GoM's own
icons:

    gun        item_MP5.png                 MP5 body + bolt + stock (deployed) + 30 magazine: both UMPs, stock deployed
    magazine   item_9x19Magazine30_MP5.png  every UMP magazine

--renders DIR (render_ump.py's output) also writes docs/post93_ump_preview.png: the renders flipped to the game's
handedness, the UMP9's left side with the outline traced from its reference photo laid over it
(ump9_reference_outline.json; the photo itself is not in the repo).
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT, MEDIA, TEX, ICONS, G = A.ROOT, A.MEDIA, A.TEX, A.ICONS, A.G
PREVIEW = os.path.join(ROOT, "docs/post93_ump_preview.png")
PTS = json.load(open(os.path.join(HERE, "ump_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx")
MAGS = ["9x19Magazine30_UMP", "45Magazine25_UMP", "45Magazine20_UMP", "45Magazine10_UMP"]
GUN_MAG = {"UMP9": "9x19Magazine30_UMP", "UMP45": "45Magazine25_UMP"}


def gun_objs(gun):
    """The gun with its stock deployed (as GoM's MP5 icon shows its own) and its standard magazine."""
    objs = [(A.load_game(FBX_GUN, "UMP_BODY"), 0), (A.load_game(FBX_GUN, "UMP_BOLT"), 0),
            (A.load_game(FBX_GUN, "UMP_HANDLE"), 0),
            (A.attach(A.load_game(FBX_PARTS, "UMP_STOCK"), PTS["stock"]), 1),
            (A.attach(A.load_game(FBX_MAGS, GUN_MAG[gun]), PTS["magazine"]), 2)]
    texes = [A.img(os.path.join(TEX, gun + ".png")), A.img(os.path.join(TEX, "UMP_STOCK.png")),
             A.img(os.path.join(TEX, GUN_MAG[gun] + ".png"))]
    return objs, texes


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    scenes = {gun: ("gun",) + gun_objs(gun) for gun in GUN_MAG}
    for n in MAGS:
        scenes[n] = ("magazine", [(A.load_game(FBX_MAGS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    for path, names in ((FBX_GUN, ("UMP_BODY", "UMP_BOLT", "UMP_HANDLE")), (FBX_MAGS, tuple(MAGS)), (FBX_PARTS, ("UMP_STOCK",))):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-24s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    """The UMP9's left-side render with the photo's outline (red) laid over it, and their silhouette IoU."""
    cams = json.load(open(os.path.join(renders, "cameras.json")))["UMP9_left"]
    k, ppm, (W, Hh) = cams["k"], cams["px_per_mm"], cams["size"]
    L0, H0 = cams["photo_origin_mm"]
    lmid, zc = cams["centre_game"][1], cams["centre_game"][2]
    out = json.load(open(os.path.join(HERE, "ump9_reference_outline.json")))["outline"]

    def px(L, H):
        return W / 2 - ((L0 - L) * k - lmid) / k * ppm, Hh / 2 - ((H - H0) * k - zc) / k * ppm

    im = render(renders, "UMP9_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    pts = [px(*p) for p in out]
    d.line(pts + pts[:1], fill=(220, 30, 30), width=2)
    ox, oy = px(L0, H0)
    d.line([(ox - 8, oy), (ox + 8, oy)], fill=(30, 60, 220), width=2)
    d.line([(ox, oy - 8), (ox, oy + 8)], fill=(30, 60, 220), width=2)
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
    p = B.Page(renders, 2480, 4300, "H&K UMP45 and UMP9, GunsOfTienPost93.UMP45 / UMP9: Workbench renders of the "
                                    "exported FBX files + textures (no specular), as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.d.text((30, y), "UMP9 left side; red = outline traced from H&K's photo; silhouette overlap %.1f%%; blue cross = "
             "origin" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 2440, im=ov)
    y += 34 + 1070 + 20
    print("UMP9 silhouette IoU %.3f" % iou)

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("UMP45_right", 20, y, 1200, "UMP45 right side (ejection port, stock hinge)")
    put("UMP45_left", 1240, y, 1200, "UMP45 left side, 25-round magazine")
    y += 545
    put("UMP9_q_left", 20, y, 800, "UMP9 from behind, left")
    put("UMP9_q_right", 840, y, 800, "from behind, right")
    put("UMP45_folded_q", 1660, y, 800, "UMP45, stock folded to the right")
    y += 470
    put("UMP9_fitted_q", 20, y, 1200, "UMP9 with GoM's Aimpoint, MKC foregrip, SR7 light, AimRight laser")
    put("UMP45_folded_top", 1240, y, 1200, "from above, stock folded")
    y += 620
    put("UMP45_20_left", 20, y, 1200, "UMP45 with the 20-round magazine")
    put("UMP45_10_left", 1240, y, 1200, "UMP45 with the 10-round magazine")
    y += 545
    x = 20
    for n in MAGS:
        put("mag_" + n, x, y, 300, n)
        x += 320
    put("gom_MP5", x + 20, y, 1000, "GoM's MP5 at the same scale")
    y += 440
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5.png", "item_9x19Magazine30_MP5.png")]
    p.icons(20, y, refs[:1] + [(icons["UMP9"], "UMP9"), (icons["UMP45"], "UMP45")])
    p.icons(1000, y, refs[1:] + [(icons[n], n.split("_")[0]) for n in MAGS[:2]])
    p.icons(1000, y + 260, [(icons[n], n.split("_")[0]) for n in MAGS[2:]])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
