#!/usr/bin/env python3
"""PPSh-41 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_ppsh41_art.py [--renders DIR [--photo references/ppsh41/ppsh41_left_ria84_1677.jpg
                                                 --right-photo references/ppsh41/raw/ria_000.jpg
                                                 --box-photo references/ppsh41/raw/commons_003.jpg]]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) with Post-93's make_mp7_art.py renderer:

    PPSH41                    the SCARs' rifle camera and light (post93/scar_icon_cameras.json, fitted on GoM's
                              item_M4A1.png), as the RPK's: the gun with its drum on
    762x25Drum71_PPSH41       a three-quarter view of its front face (it faces forward: from the side it is a slab),
                              as the RPD's and the RPK's drums, in the rifle's light
    762x25Magazine35_PPSH41   the SCARs' rifle magazine camera

--renders DIR (render_ppsh41.py's output) also writes docs/ppsh41_preview.png, every render flipped to the game's
handedness: the left side at 3 px a mm with the outline traced from the reference photo
(ppsh41_reference_outline.json) laid over it and the photo beside it (--photo), the part-by-part panels of the remodel
passes (the photo with the model's red outline beside the model; scripts/ref_crop.py on render_ppsh41.py's 8 px a mm
views), the right side beside --right-photo, the box magazine beside --box-photo, 3/4 views, the magazines, and GoM's
Thompson at the same scale.
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

ROOT, G = A.ROOT, A.G
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/ppsh41_preview.png")
PTS = json.load(open(os.path.join(HERE, "ppsh41_points.json")))
OUTLINE_JSON = os.path.join(HERE, "ppsh41_reference_outline.json")
OUTLINE = json.load(open(OUTLINE_JSON))
OUTLINE["holes_traced"] = [h for h in OUTLINE["holes_traced"] if len(h) >= 3]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_PPSH41.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_PPSH41_magazines.fbx")
DRUM, BOX = "762x25Drum71_PPSH41", "762x25Magazine35_PPSH41"
RIFLE_CAMERAS = os.path.join(HERE, "post93/scar_icon_cameras.json")
PARTS = [("trigger, guard and selector", "left_c", (415, 545, 70, 130)),
         ("muzzle compensator and front sight", "left_a", (-5, 110, 140, 205)),
         ("hinge and magazine housing", "left_b", (240, 400, 100, 195)),
         ("rear sight and receiver cap", "left_c", (410, 560, 110, 205)),
         ("the stock's wrist", "left_c", (520, 650, 40, 170))]


def arg(key):
    return sys.argv[sys.argv.index(key) + 1] if key in sys.argv else None


def make_icons():
    cams = json.load(open(RIFLE_CAMERAS))
    rifle = cams["rifle"]
    gun = [(A.load_game(FBX_GUN, "PPSH41_BODY"), 0), (A.load_game(FBX_GUN, "PPSH41_BOLT"), 0),
           (A.attach(A.load_game(FBX_MAGS, DRUM), PTS["magazine"]), 1)]
    texes = [A.img(os.path.join(TEX, "PPSH41.png")), A.img(os.path.join(TEX, DRUM + ".png"))]
    drum_cam = {"yaw": 320.0, "pitch": 0.0, "roll": 0.0, "bbox": [1, 1, 31, 31]}
    scenes = {"PPSH41": (rifle, gun, texes),
              DRUM: ({"camera": drum_cam, "light": rifle["light"]}, [(A.load_game(FBX_MAGS, DRUM), 0)], texes[1:]),
              # the rifle's light: the SCAR magazine's own was fitted to GoM's blue STANAG icon
              BOX: ({"camera": cams["rifle_magazine"]["camera"], "light": rifle["light"]},
                    [(A.load_game(FBX_MAGS, BOX), 0)], [A.img(os.path.join(TEX, BOX + ".png"))])}
    made = {}
    for name, (fit, objs, tx) in scenes.items():
        icon = A.shade(objs, tx, dict(fit["camera"]), fit["light"])
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
    import numpy as np
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
    a = np.asarray(ref) > 0
    b = np.asarray(ren.getchannel("A")) > 127
    iou = (a & b).sum() / max(1, (a | b).sum())
    page = on_paper(ren)
    d = ImageDraw.Draw(page)
    for loop in [OUTLINE["outline"]] + OUTLINE["holes_traced"]:
        pts = [px(*p) for p in loop]
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=2)
    ox, oy = px(*PTS["_extras"]["photo_origin_mm"])
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
    out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    out.paste(im, (-round(left), -round(top)))
    return out


def part_pairs(renders, photo, px=8):
    cams = json.load(open(os.path.join(renders, "cameras.json")))
    out = []
    for label, view, (la, lb, ha, hb) in PARTS:
        cam = cams[view]
        ren = on_paper(render(renders, view), (240, 240, 236, 255)).convert("RGB")
        ppm = cam["px_per_mm"]
        w, h = cam["size"]
        cL, cH = cam["centre_mm"]
        tmp = os.path.join(renders, "_part.png")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "ref_crop.py"), photo, OUTLINE_JSON, tmp, str(la),
                        str(lb), str(ha), str(hb), "--px", str(px), "--nogrid", "--overlay",
                        os.path.join(renders, view + ".png"), os.path.join(renders, "cameras.json"), view],
                       check=True, stdout=subprocess.DEVNULL)
        ph = Image.open(tmp).convert("RGBA")
        box = (w / 2 + (la - cL) * ppm, h / 2 - (hb - cH) * ppm, w / 2 + (lb - cL) * ppm, h / 2 - (ha - cH) * ppm)
        out.append((label, ph, ren.transform(ph.size, Image.EXTENT, box, Image.BICUBIC).convert("RGBA")))
        os.remove(tmp)
    return out


def sheet(renders, icons):
    photo, right_photo, box_photo = arg("--photo"), arg("--right-photo"), arg("--box-photo")
    p = B.Page(renders, 2480, 12000, "PPSh-41 (GunsOfTien.PPSH41) for GoM Extension: Guns of Tien: Workbench renders "
                                     "of the exported FBX files + textures, as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.d.text((30, y), "left side with the drum, 3 px a mm; red = the photo's traced outline (its drum hangs askew); "
             "IoU %.1f%%; blue = origin" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    y += 30 + p.put(None, 20, y + 30, 2440, im=ov) + 10
    if photo:
        p.d.text((30, y), "reference photo (Rock Island Auction lot 84/1677), same scale", fill=(40, 40, 40), font=p.FS)
        y += 30 + p.put(None, 20, y + 30, 2440, im=photo_at_scale(renders, photo)) + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    if photo:
        p.d.text((30, y), "Part by part: the photo with the model's outline in red, and the model's same crop",
                 fill=(20, 20, 20), font=p.F)
        y += 40
        for label, ph, mo in part_pairs(renders, photo):
            ww = 1200
            hh = round(ph.height * ww / ph.width)
            p.put(None, 20, y + 30, ww, im=ph)
            p.put(None, 1250, y + 30, ww, im=mo)
            p.d.text((30, y), label, fill=(40, 40, 40), font=p.FS)
            y += hh + 50
    y += put("right", 20, y, 2440, "right side (the cocking handle and its slot, the ejection port on top)") + 10
    if right_photo:
        rp = Image.open(right_photo).convert("RGBA")
        y += p.put(None, 20, y, 2440, "right-side reference (Rock Island Auction lot 89/405)", im=rp) + 10
    y += put("fired_right", 20, y, 2440, "the handle back (bolt_fired, 85 mm): each shot, cocked, empty") + 10
    y += put("box_left", 20, y, 2440, "with the 35-round box") + 10
    if box_photo:
        bp = Image.open(box_photo).convert("RGBA")
        y += p.put(None, 20, y, 1500, "reference with the box (Wikimedia Commons)", im=bp) + 10
    hq = put("q_left", 20, y, 1200, "left side from behind")
    put("q_right", 1250, y, 1200, "right side from behind")
    y += hq + 10
    hq = put("q_front_left", 20, y, 1200, "left side from the front")
    put("q_back_right", 1250, y, 1200, "right side from the front")
    y += hq + 10
    y += put("top", 20, y, 2440, "top (slots along the jacket, the ejection port, the handle on the right)") + 10
    x = 20
    for n, label in ((DRUM + "_side", "the drum from the side"), (DRUM + "_q", None), (DRUM + "_front", "its front"),
                     (BOX + "_side", "the box"), (BOX + "_q", None), ("front", "front"), ("back", "rear")):
        put(n, x, y, 330, label)
        x += 345
    y += 350
    p.d.text((30, y), "Same scale, right side: this PPSh-41 (0.603 of real size, as every Guns of Tien gun) and GoM's "
             "Thompson with its drum", fill=(20, 20, 20), font=p.F)
    y += 40
    hq = put("ppsh_right", 20, y, 1200, None)
    put("gom_thompson_right", 1250, y, 1200, None)
    y += hq + 20
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_THOMPSON.png", "item_45Magazine100_THOMPSON.png", "item_45Magazine30_THOMPSON.png")]
    p.icons(20, y, [refs[0], (icons["PPSH41"], "PPSH41"), refs[1], (icons[DRUM], DRUM), refs[2], (icons[BOX], BOX)])
    p.im = p.im.crop((0, 0, 2480, y + 260))
    p.save(PREVIEW)
    print("silhouette IoU %.3f" % iou)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(arg("--renders"), icons)


if __name__ == "__main__":
    main()
