#!/usr/bin/env python3
"""Walther PPK inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_ppk_art.py [--renders DIR [--photo references/ppk22/ppk22_right_110860LR.jpg
                                              --left-photo references/ppk22/ppk22_left_ulm.jpg]]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) with the cameras and lights Post-93's make_fiveseven_art.py
fitted on GoM's Glock 17 and its magazine (post93/fiveseven_icon_cameras.json: `pistol`, `pistol_magazine`), as the
Glock 21's. --renders DIR (render_ppk.py's output) also writes docs/ppk_preview.png, every render flipped to the game's
handedness, with the outline traced from the reference photo (ppk_reference_outline.json) laid over the right side at
the photo's scale, and the photos beside the renders with --photo / --left-photo (they are not kept in the repo).
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402
import make_fiveseven_art as F             # noqa: E402

ROOT, G = A.ROOT, A.G
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/ppk_preview.png")
POINTS = json.load(open(os.path.join(HERE, "ppk_points.json")))
OUTLINE = json.load(open(os.path.join(HERE, "ppk_reference_outline.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_PPK.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_PPK_magazines.fbx")
MAG = "22LRMagazine8_PPK"


def make_icons():
    fitted = json.load(open(F.CAMERAS_JSON))
    scenes = {"PPK": ("pistol", [(A.load_game(FBX_GUN, "PPK_BODY"), 0),
                                 (A.load_game(FBX_GUN, "PPK_SLIDE"), 0), (A.load_game(FBX_MAGS, MAG), 1)],
                      [A.img(os.path.join(TEX, "PPK.png")), A.img(os.path.join(TEX, MAG + ".png"))]),
              MAG: ("pistol_magazine", [(A.load_game(FBX_MAGS, MAG), 0)], [A.img(os.path.join(TEX, MAG + ".png"))])}
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
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["right_photo"]
    ren = render(renders, "right_photo")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # right side as in the photo: muzzle on the right
        return w / 2 + (cL - L) * ppm, h / 2 - (H - cH) * ppm

    ref = Image.new("L", (w, h), 0)
    rd = ImageDraw.Draw(ref)
    rd.polygon([px(*p) for p in OUTLINE["outline"]], fill=255)
    for hole in OUTLINE["holes"]:
        rd.polygon([px(*p) for p in hole], fill=0)
    model = ren.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    a, b = ref.load(), model.load()
    both = either = 0
    for y in range(h):
        for x in range(w):
            r, m = a[x, y] > 0, b[x, y] > 0
            both += r and m
            either += r or m
    iou = both / max(1, either)
    page = Image.new("RGBA", (w, h), (250, 250, 248, 255))
    page.alpha_composite(ren)
    d = ImageDraw.Draw(page)
    for loop in [OUTLINE["outline"]] + OUTLINE["holes"]:
        pts = [px(*p) for p in loop]
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=2)
    ox, oy = px(*POINTS["_extras"]["photo_origin_mm"])
    d.line([(ox - 25, oy), (ox + 25, oy)], fill=(0, 120, 255, 255), width=2)
    d.line([(ox, oy - 25), (ox, oy + 25)], fill=(0, 120, 255, 255), width=2)
    return page, iou


def photo_at_scale(renders, key="--photo"):
    if key not in sys.argv:
        return None
    cam = json.load(open(os.path.join(renders, "cameras.json")))["right_photo"]
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    im = Image.open(sys.argv[sys.argv.index(key) + 1]).convert("RGBA")
    k = ppm / OUTLINE["px_per_mm"]
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    mx, my = OUTLINE["photo_px"]["x_muzzle"] * k, OUTLINE["photo_px"]["y_lowest"] * k
    left, top = mx - (w / 2 + cL * ppm), my - (h / 2 + cH * ppm)
    return im.crop((round(left), round(top), round(left) + w, round(top) + h))


def sheet(renders, icons):
    p = B.Page(renders, 2480, 3400, "Walther PPK .22 LR (GunsOfTien.PPK) for GoM Extension: Guns of Tien: Workbench "
                                    "renders of the exported FBX files + textures, as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.put(None, 20, y + 50, 1200, im=ov)
    p.d.text((30, y), "right side, photo scale; red = the photo's traced outline (lanyard loop not modelled); "
             "IoU %.1f%%; blue = origin" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    ph = photo_at_scale(renders)
    if ph is not None:
        p.put(None, 1250, y + 50, 1200, im=ph)
        p.d.text((1260, y), "reference photo, same scale", fill=(40, 40, 40), font=p.FS)
    y += 50 + 900 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("left", 20, y, 1200, "left side (safety lever, magazine button, Ulm inscriptions)")
    if "--left-photo" in sys.argv:
        lp = Image.open(sys.argv[sys.argv.index("--left-photo") + 1]).convert("RGBA")
        p.put(None, 1300, y + 30, 900, "left-side reference (an Ulm 'Modell PPK Cal. 22 l.r.')", im=lp)
    y += 940
    put("q_left", 20, y, 800, "left side from behind")
    put("q_right", 840, y, 800, "right side from behind (ejection port)")
    put("fired_q", 1660, y, 800, "slide back (slide_fired, 22 mm)")
    y += 620
    put("top", 20, y, 800, "top")
    put("front", 840, y, 220, "front")
    put("back", 1080, y, 220, "rear")
    put("mag_alone", 1320, y, 240, MAG)
    put("mag_q", 1580, y, 240, None)
    y += 380
    p.d.text((30, y), "Same scale, right side: this PPK, the main mod's Glock 21 (both 0.603 of real size) and GoM's "
             "Glock 17 (0.72)", fill=(20, 20, 20), font=p.F)
    put("ppk_right", 20, y + 40, 600, None)
    put("glock21_right", 640, y + 40, 600, None)
    put("gom_glock17_right", 1260, y + 40, 600, None)
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_GLOCK17.png", "item_9x19Magazine17_GLOCK.png")]
    p.icons(1880, y + 40, refs[:1] + [(icons["PPK"], "PPK")])
    p.icons(1900, y + 290, refs[1:] + [(icons[MAG], MAG)])
    p.save(PREVIEW)
    print("silhouette IoU %.3f" % iou)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
