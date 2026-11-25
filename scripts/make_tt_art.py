#!/usr/bin/env python3
"""Tokarev TT inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_tt_art.py [--renders DIR [--photo references/tt/tt33_left_rama_6553.jpg
                                             --right-photo references/tt/raw/commons_001.jpg
                                             --views references/tt/raw]]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) with the cameras and lights Post-93's make_fiveseven_art.py
fitted on GoM's Glock 17 and its magazine (post93/fiveseven_icon_cameras.json: `pistol`, `pistol_magazine`), as the
Glock 21's and the PPK's. --renders DIR (render_tt.py's output) also writes docs/tt_preview.png, every render flipped
to the game's handedness: the left side at the photo's scale with the outline traced from the reference photo
(tt_reference_outline.json) laid over it, the photo beside it (--photo), the part-by-part panels of the remodel passes
(the photo with the model's red outline beside the model, trigger and guard first; scripts/ref_crop.py), the right
side beside --right-photo, 3/4 views beside the auction lot's (--views: ria_001 ... 005).
"""

import json
import os
import subprocess
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
PREVIEW = os.path.join(ROOT, "docs/tt_preview.png")
POINTS = json.load(open(os.path.join(HERE, "tt_points.json")))
OUTLINE_JSON = os.path.join(HERE, "tt_reference_outline.json")
OUTLINE = json.load(open(OUTLINE_JSON))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TT33.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TT33_magazines.fbx")
MAG = "762x25Magazine8_TT33"
PARTS = [("trigger and guard", (76, 138, 52, 104)), ("slide front", (-3, 60, 84, 128)),
         ("slide rear, hammer, sights", (138, 198, 84, 130)), ("grip", (128, 198, -3, 92))]


def arg(key):
    return sys.argv[sys.argv.index(key) + 1] if key in sys.argv else None


def make_icons():
    fitted = json.load(open(F.CAMERAS_JSON))
    scenes = {"TT33": ("pistol", [(A.load_game(FBX_GUN, "TT33_BODY"), 0),
                                (A.load_game(FBX_GUN, "TT33_SLIDE"), 0), (A.load_game(FBX_MAGS, MAG), 1)],
                     [A.img(os.path.join(TEX, "TT33.png")), A.img(os.path.join(TEX, MAG + ".png"))]),
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


def on_paper(im, colour=(250, 250, 248, 255)):
    page = Image.new("RGBA", im.size, colour)
    page.alpha_composite(im)
    return page


def outline_panel(renders):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    ren = render(renders, "left_photo")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # left side as in the photo: muzzle on the left
        return w / 2 + (L - cL) * ppm, h / 2 - (H - cH) * ppm

    ref = Image.new("L", (w, h), 0)
    rd = ImageDraw.Draw(ref)
    rd.polygon([px(*p) for p in OUTLINE["outline"]], fill=255)
    for hole in OUTLINE["holes_traced"]:
        rd.polygon([px(*p) for p in hole], fill=0)
    model = ren.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    import numpy as np
    a, b = np.asarray(ref) > 0, np.asarray(model) > 0
    iou = (a & b).sum() / max(1, (a | b).sum())
    page = on_paper(ren)
    d = ImageDraw.Draw(page)
    for loop in [OUTLINE["outline"]] + OUTLINE["holes_traced"]:
        pts = [px(*p) for p in loop]
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=2)
    ox, oy = px(*POINTS["_extras"]["photo_origin_mm"])
    d.line([(ox - 25, oy), (ox + 25, oy)], fill=(0, 120, 255, 255), width=2)
    d.line([(ox, oy - 25), (ox, oy + 25)], fill=(0, 120, 255, 255), width=2)
    return page, iou


def photo_at_scale(renders, photo):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    im = Image.open(photo).convert("RGBA")
    k = ppm / OUTLINE["px_per_mm"]
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    mx, my = OUTLINE["photo_px"]["x_muzzle"] * k, OUTLINE["photo_px"]["y_lowest"] * k
    left, top = mx - (w / 2 - cL * ppm), my - (h / 2 + cH * ppm)
    return im.crop((round(left), round(top), round(left) + w, round(top) + h))


def part_pairs(renders, photo, px=14):
    """[(label, photo crop with the model's red outline, the model's same crop)] for the review."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    ren = on_paper(render(renders, "left_photo"), (240, 240, 236, 255)).convert("RGB")
    ppm = cam["px_per_mm"]
    w, h = cam["size"]
    cL, cH = cam["centre_mm"]
    out = []
    for label, (la, lb, ha, hb) in PARTS:
        tmp = os.path.join(renders, "_part.png")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "ref_crop.py"), photo, OUTLINE_JSON, tmp, str(la),
                        str(lb), str(ha), str(hb), "--px", str(px), "--nogrid", "--overlay",
                        os.path.join(renders, "left_photo.png"), os.path.join(renders, "cameras.json"), "left_photo"],
                       check=True, stdout=subprocess.DEVNULL)
        ph = Image.open(tmp).convert("RGBA")
        box = (w / 2 + (la - cL) * ppm, h / 2 - (hb - cH) * ppm, w / 2 + (lb - cL) * ppm, h / 2 - (ha - cH) * ppm)
        out.append((label, ph, ren.transform(ph.size, Image.EXTENT, box, Image.BICUBIC).convert("RGBA")))
        os.remove(tmp)
    return out


def sheet(renders, icons):
    photo, right_photo, views = arg("--photo"), arg("--right-photo"), arg("--views")
    p = B.Page(renders, 2480, 9600, "Tokarev TT-33 (GunsOfTien.TT33) for GoM Extension: Guns of Tien: Workbench renders of "
                                    "the exported FBX files + textures, as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.put(None, 20, y + 50, 1200, im=ov)
    p.d.text((30, y), "left side, photo scale; red = the photo's traced outline; IoU %.1f%%; blue = origin"
             % (iou * 100), fill=(40, 40, 40), font=p.FS)
    if photo:
        p.put(None, 1250, y + 50, 1200, im=photo_at_scale(renders, photo))
        p.d.text((1260, y), "reference photo (a 1944 TT-33, Wikimedia Commons, Rama), same scale", fill=(40, 40, 40),
                 font=p.FS)
    y += 50 + 790 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    if photo:
        p.d.text((30, y), "Part by part: the photo with the model's outline in red, and the model's same crop",
                 fill=(20, 20, 20), font=p.F)
        y += 40
        for label, ph, mo in part_pairs(renders, photo):
            ww = 900
            hh = round(ph.height * ww / ph.width)
            p.put(None, 20, y + 30, ww, im=ph)
            p.put(None, 940, y + 30, ww, im=mo)
            p.d.text((30, y), label, fill=(40, 40, 40), font=p.FS)
            y += hh + 50
    put("right", 20, y, 1200, "right side (ejection port, extractor, the slide stop's clip, the catch's slotted end)")
    if right_photo:
        rp = Image.open(right_photo).convert("RGBA")
        p.put(None, 1250, y + 30, 1150, "right-side reference (a 1940 TT-33, Armemuseum; nickel slide, red star)",
              im=rp)
    y += 830
    for n, x, label in (("q_left", 20, "left side from behind"), ("q_right", 840, "right side from behind"),
                        ("q_front_left", 1660, "left side from the front")):
        put(n, x, y, 800, label)
    y += 640
    if views:
        x = 20
        for n in ("ria_001", "ria_002", "ria_005"):
            f = os.path.join(views, n + ".jpg")
            if os.path.exists(f):
                p.put(None, x, y, 800, "reference: Rock Island Auction lot 5010/81" if x == 20 else None,
                      im=Image.open(f).convert("RGBA"))
            x += 820
        y += 500
    put("fired_q", 20, y, 800, "slide back (slide_fired, 40 mm): its spring tube runs into the dust cover")
    put("fired_left", 840, y, 800, None)
    put("q_top_left", 1660, y, 800, "from above")
    y += 640
    put("top", 20, y, 1100, "top")
    put("front", 1140, y, 200, "front")
    put("back", 1360, y, 200, "rear")
    put("mag_alone", 1580, y, 220, MAG)
    put("mag_q", 1820, y, 220, None)
    y += 400
    p.d.text((30, y), "Same scale, right side: this TT (0.603 of real size, as every Guns of Tien gun) and GoM's "
             "M1911 and Glock 17 (0.72)", fill=(20, 20, 20), font=p.F)
    put("tt_right", 20, y + 40, 600, None)
    put("gom_m1911_right", 640, y + 40, 600, None)
    put("gom_glock17_right", 1260, y + 40, 600, None)
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_M1911.png", "item_45Magazine7_M1911.png")]
    p.icons(1880, y + 40, refs[:1] + [(icons["TT33"], "TT-33")])
    p.icons(1900, y + 290, refs[1:] + [(icons[MAG], MAG)])
    p.im = p.im.crop((0, 0, 2480, y + 560))
    p.save(PREVIEW)
    print("silhouette IoU %.3f" % iou)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(arg("--renders"), icons)


if __name__ == "__main__":
    main()
