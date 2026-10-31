#!/usr/bin/env python3
"""KRISS Vector .45 / 9mm inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_vector_art.py [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) rendered from the exported FBX files and textures
with make_mp7_art.py's renderer and the cameras and lights fitted on GoM's own icons:

    gun               item_MP5.png (mp7_icon_cameras.json)                      both Vectors, stock deployed, the
                                                                                standard magazine
    pistol_magazine   item_9x19Magazine17_GLOCK.png (fiveseven_icon_cameras.json)  our Glock magazines (the 30 .45,
                                                                                the 33 and 40 9mm), from their
                                                                                pistol-space models

--renders DIR (render_vector.py's output) also writes docs/post93_vector_preview.png: the renders flipped to the
game's handedness, the Vector .45's left side with the outline traced from its reference drawing laid over it
(vector_reference_outline.json; the drawing itself is not in the repo).
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
import make_fiveseven_art as F             # noqa: E402

ROOT, MEDIA, TEX, ICONS, G = A.ROOT, A.MEDIA, A.TEX, A.ICONS, A.G
MAIN_TEX = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/textures/weapons/GunsOfTien")
PREVIEW = os.path.join(ROOT, "docs/post93_vector_preview.png")
PTS = json.load(open(os.path.join(HERE, "vector_points.json")))
OUTLINE = json.load(open(os.path.join(HERE, "vector_reference_outline.json")))["outline"]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTOR.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_VECTOR_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_VECTOR_parts.fbx")
VECTOR_MAGS = ["45Magazine13_VECTOR", "45Magazine30_VECTOR", "9x19Magazine17_VECTOR", "9x19Magazine33_VECTOR",
               "9x19Magazine40_VECTOR"]
GUN_MAG = {"VECTOR45": "45Magazine13_VECTOR", "VECTOR9": "9x19Magazine17_VECTOR"}
# item -> (its pistol-space model, that model's texture)
OWN_MAGS = {
    "45Magazine30_GLOCK21": ("45Magazine30_GLOCK21", os.path.join(MAIN_TEX, "45Magazine13_GLOCK21.png")),
    "9x19Magazine33_GLOCK": ("9x19Magazine33_GLOCK17",
                             os.path.join(G, "textures/weapons/magazines/pistols/9x19Magazine17_Glock.png")),
    "9x19Magazine40_GLOCK": ("9x19Magazine40_GLOCK17",
                             os.path.join(G, "textures/weapons/magazines/pistols/9x19Magazine17_Glock.png")),
}


def gun_objs(gun):
    """The gun with its stock deployed (as GoM's MP5 icon shows its own) and its standard magazine."""
    objs = [(A.load_game(FBX_GUN, "VECTOR_BODY"), 0), (A.load_game(FBX_GUN, "VECTOR_BOLT"), 0),
            (A.load_game(FBX_GUN, "VECTOR_HANDLE"), 0),
            (A.attach(A.load_game(FBX_PARTS, "VECTOR_STOCK"), PTS["stock"]), 1),
            (A.attach(A.load_game(FBX_MAGS, GUN_MAG[gun]), PTS["magazine"]), 2)]
    texes = [A.img(os.path.join(TEX, gun + ".png")), A.img(os.path.join(TEX, gun + "_STOCK.png")),
             A.img(os.path.join(TEX, GUN_MAG[gun] + ".png"))]
    return objs, texes


def make_icons():
    rifle = json.load(open(A.CAMERAS_JSON))
    pistol = json.load(open(F.CAMERAS_JSON))
    made = {}
    for gun in GUN_MAG:
        objs, texes = gun_objs(gun)
        made[gun] = A.shade(objs, texes, dict(rifle["gun"]["camera"]), rifle["gun"]["light"])
    for item, (model, tex) in OWN_MAGS.items():
        made[item] = A.shade([(A.load_game(FBX_MAGS, model), 0)], [A.img(tex)],
                             dict(pistol["pistol_magazine"]["camera"]), pistol["pistol_magazine"]["light"])
    for name, icon in made.items():
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
    return made


def check():
    for path, names in ((FBX_GUN, ("VECTOR_BODY", "VECTOR_BOLT", "VECTOR_HANDLE", "VECTOR_RAIL_LEFT",
                                   "VECTOR_RAIL_RIGHT")),
                        (FBX_MAGS, tuple(VECTOR_MAGS) + tuple(m for m, _ in OWN_MAGS.values())),
                        (FBX_PARTS, ("VECTOR_STOCK",))):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-24s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))
        missing = set(names) - {n for n, _, _ in lcl}
        assert not missing, missing


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    """The Vector .45's left-side render with the drawing's outline (red) laid over it; the share of the render
    outside it (the drawing's suppressor, optic, raised sights and grip are masked out of the outline)."""
    cams = json.load(open(os.path.join(renders, "cameras.json")))["V45_left"]
    k, ppm, (W, Hh) = cams["k"], cams["px_per_mm"], cams["size"]
    L0, H0 = cams["photo_origin_mm"]
    lmid, zc = cams["centre_game"][1], cams["centre_game"][2]

    def px(L, H):
        return W / 2 - ((L0 - L) * k - lmid) / k * ppm, Hh / 2 - ((H - H0) * k - zc) / k * ppm

    im = render(renders, "V45_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    pts = [px(*p) for p in OUTLINE]
    d.line(pts + pts[:1], fill=(220, 30, 30), width=2)
    ox, oy = px(L0, H0)
    d.line([(ox - 8, oy), (ox + 8, oy)], fill=(30, 60, 220), width=2)
    d.line([(ox, oy - 8), (ox, oy + 8)], fill=(30, 60, 220), width=2)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    a, b = im.getchannel("A").load(), mask.load()
    inter = union = model = 0
    for x in range(W):
        for y in range(Hh):
            m, p = a[x, y] > 128, b[x, y] > 128
            inter += m and p
            union += m or p
            model += m
    return bg, inter / max(1, union), (model - inter) / max(1, model)


def sheet(renders, icons):
    p = B.Page(renders, 2480, 6000, "KRISS Vector .45 and 9mm, GunsOfTienPost93.VECTOR45 / VECTOR9: Workbench renders "
                                    "of the exported FBX files + textures (no specular), as the game shows them")
    y = 70
    ov, iou, outside = outline_panel(renders)
    p.d.text((30, y), "Vector .45 left side, 30-round magazine; red = outline traced from the reference drawing (its "
             "suppressor, optic and grip masked out); overlap %.1f%%, render outside it %.1f%%; blue cross = origin"
             % (iou * 100, outside * 100), fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 2440, im=ov)
    y += 34 + 1230 + 20
    print("Vector .45 silhouette IoU %.3f, outside %.3f" % (iou, outside))

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    def row(y, panels):
        """Panels side by side (name, width, label); returns the y under the tallest."""
        x, tallest = 20, 0
        for name, w, label in panels:
            tallest = max(tallest, put(name, x, y, w, label))
            x += w + 20
        return y + tallest + 20

    y = row(y, [("V45_right", 1210, "Vector .45 right side (ejection port, stock hinge), flat dark earth"),
                ("V9_left", 1210, "Vector 9mm left side, GoM's Glock 17 magazine, sand")])
    y = row(y, [("V45_q_left", 800, "Vector .45 from behind, left"), ("V45_q_right", 800, "from behind, right"),
                ("V9_folded_q", 800, "Vector 9mm, stock folded to the right")])
    y = row(y, [("V45_fitted_q", 1210, "with GoM's Aimpoint, MKC foregrip, SR7 light and AimRight laser (KRISS's side "
                                       "rails)"),
                ("V9_folded_top", 1210, "from above, stock folded")])
    y = row(y, [("V45_13_left", 1210, "Vector .45 with the Glock 21's 13-round magazine"),
                ("V9_40_left", 1210, "Vector 9mm with KRISS's 40-round magazine")])
    y = row(y, [("mag_" + n, 260, n.split("_")[0]) for n in VECTOR_MAGS]
            + [("G21_30_left", 300, "30 on the Glock 21"), ("G17_33_left", 300, "33 on GoM's Glock 17"),
               ("G17_40_left", 300, "40 on GoM's Glock 17")])
    y = row(y, [("prop2_left", 400, "Glock 21 / GoM's Glock 17 magazines"), ("prop2_front", 400, "at Bip01_Prop2"),
                ("gom_MP5", 1500, "GoM's MP5 at the same scale")])
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5.png", "item_9x19Magazine17_GLOCK.png")]
    p.icons(20, y, refs[:1] + [(icons["VECTOR45"], "VECTOR45"), (icons["VECTOR9"], "VECTOR9")])
    p.icons(1000, y, refs[1:] + [(icons[n], n.split("_")[0]) for n in OWN_MAGS])
    p.im = p.im.crop((0, 0, p.im.width, y + 250))
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
