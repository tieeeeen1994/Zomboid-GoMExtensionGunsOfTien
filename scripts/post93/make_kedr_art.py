#!/usr/bin/env python3
"""PP-91 Kedr inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_kedr_art.py [--renders DIR [--photo references/kedr/kedr_left_open.jpg
                                                      --folded-photo references/kedr/raw/commons_008.jpg
                                                      --right-photo references/kedr/raw/commons_003.jpg]]

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) with make_mp7_art.py's renderer and its cameras and
lights (mp7_icon_cameras.json, fitted on GoM's MP5 icons), as the MP7's:

    KEDR                    the gun with its stock folded and the 20-round magazine in, turned upright (it is
                            modelled upside down, held like a pistol)
    9x18Magazine<n>_KEDR    the 20 and the 30

--renders DIR (render_kedr.py's output) also writes docs/post93_kedr_preview.png, every render flipped to the game's
handedness: the left side with the stock open as the measuring photo has it, the photo's traced outline over it
(kedr_reference_outline.json) and the photo beside it (--photo), the part-by-part panels of the remodel passes (the
photo with the model's red outline beside the model's same crop; scripts/ref_crop.py), the folded gun beside
--folded-photo, the right side beside --right-photo, other views, GoM's MAC-10 and MP5K and the main mod's Micro Uzi
at the same scale, and the icons beside GoM's.
"""

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT, G = A.ROOT, A.G
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/post93_kedr_preview.png")
PTS = json.load(open(os.path.join(HERE, "kedr_points.json")))
OUTLINE_JSON = os.path.join(HERE, "kedr_reference_outline.json")
OUTLINE = json.load(open(OUTLINE_JSON))
OUTLINE["holes_traced"] = [h for h in OUTLINE["holes_traced"] if len(h) >= 3]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_KEDR.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_KEDR_magazines.fbx")
MAGS = ["9x18Magazine20_KEDR", "9x18Magazine30_KEDR"]
GUN_MAG = MAGS[0]
PARTS = [("trigger and guard", "left_a", (158, 220, 116, 162)),
         ("front sight, barrel and the receiver's front", "left_a", (-6, 150, 150, 236)),
         ("cocking handle and slot, hinge and rear sight", "left_a", (150, 312, 150, 240)),
         ("grip", "left_a", (200, 300, 50, 172)),
         ("magazine housing and catch", "left_a", (100, 200, 110, 175)),
         ("butt plate", "left_b", (480, 545, 90, 185))]


def arg(key):
    return sys.argv[sys.argv.index(key) + 1] if key in sys.argv else None


def gun_objs():
    up = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0, 0.0]}
    objs = [(A.load_game(FBX_GUN, n), 0) for n in ("KEDR_BODY", "KEDR_BOLT", "KEDR_STOCK_FOLDED")]
    objs.append((A.attach(A.load_game(FBX_MAGS, GUN_MAG), PTS["magazine"]), 1))
    objs = [(A.attach(t, up), i) for t, i in objs]
    return objs, [A.img(os.path.join(TEX, "KEDR.png")), A.img(os.path.join(TEX, GUN_MAG + ".png"))]


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    scenes = {"KEDR": ("gun",) + gun_objs()}
    for n in MAGS:
        scenes[n] = ("magazine", [(A.load_game(FBX_MAGS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
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
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def on_paper(im, colour=(250, 250, 248, 255)):
    page = Image.new("RGBA", im.size, colour)
    page.alpha_composite(im)
    return page


def outline_panel(renders):
    import numpy as np
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    ren = render(renders, "left_photo")             # mirrored once: muzzle left, as the photo
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):
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
    return page, iou, cam


def photo_at_scale(photo, cam):
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    s, xm, y0 = OUTLINE["px_per_mm"], OUTLINE["photo_px"]["x_muzzle"], OUTLINE["photo_px"]["y_lowest"]
    x0, y1 = xm + (cL - w / 2 / ppm) * s, y0 - (cH + h / 2 / ppm) * s
    im = Image.open(photo).convert("RGB")
    return im.transform((w, h), Image.EXTENT, (x0, y1, x0 + w / ppm * s, y1 + h / ppm * s), Image.BICUBIC,
                        fillcolor=(255, 255, 255)).convert("RGBA")


def part_pairs(renders, photo, px=10):
    cams = json.load(open(os.path.join(renders, "cameras.json")))
    out = []
    for label, view, (la, lb, ha, hb) in PARTS:
        cam = cams[view]
        ren = on_paper(render(renders, view), (240, 240, 236, 255)).convert("RGB")
        ppm = cam["px_per_mm"]
        w, h = cam["size"]
        cL, cH = cam["centre_mm"]
        tmp = os.path.join(renders, "_part.png")
        subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(HERE), "ref_crop.py"), photo, OUTLINE_JSON,
                        tmp, str(la), str(lb), str(ha), str(hb), "--px", str(px), "--nogrid", "--overlay",
                        os.path.join(renders, view + ".png"), os.path.join(renders, "cameras.json"), view],
                       check=True, stdout=subprocess.DEVNULL)
        ph = Image.open(tmp).convert("RGBA")
        box = (w / 2 + (la - cL) * ppm, h / 2 - (hb - cH) * ppm, w / 2 + (lb - cL) * ppm, h / 2 - (ha - cH) * ppm)
        out.append((label, ph, ren.transform(ph.size, Image.EXTENT, box, Image.BICUBIC).convert("RGBA")))
        os.remove(tmp)
    return out


def sheet(renders, icons):
    photo, folded_photo, right_photo = arg("--photo"), arg("--folded-photo"), arg("--right-photo")
    p = B.Page(renders, 2480, 20000, "PP-91 Kedr (GunsOfTienPost93.KEDR) for GoM Extension: Guns of Tien, Post-93: "
                                     "Workbench renders of the exported FBX files + textures")
    y = 70
    ov, iou, cam = outline_panel(renders)
    p.d.text((30, y), "left side, the stock open and the 30-round magazine in, as the measuring photo; red = the "
             "photo's traced outline; IoU %.1f%%" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    y += 30 + p.put(None, 20, y + 30, 2440, im=ov) + 10
    if photo:
        p.d.text((30, y), "the measuring photo (zonawar.ru on gunrf.ru), same scale", fill=(40, 40, 40), font=p.FS)
        y += 30 + p.put(None, 20, y + 30, 2440, im=photo_at_scale(photo, cam)) + 20

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
    p.d.text((30, y), "The stock folded (KEDR_STOCK_FOLDED), the 20-round magazine: as the game shows it "
             "(muzzle left = the gun's right side)", fill=(20, 20, 20), font=p.F)
    y += 40
    hq = put("folded_left", 20, y, 1200, "left side")
    if folded_photo:
        p.put(None, 1250, y, 1200, "reference, folded (Vitaly Kuzmin, Commons, CC BY-SA 4.0; taken at a slant)",
              im=Image.open(folded_photo).convert("RGBA"))
    y += hq + 10
    hq = put("folded_right", 20, y, 1200, "right side: the ejection port, the selector and its lever")
    if right_photo:
        p.put(None, 1250, y, 1200, "reference, right side (Vitaly Kuzmin, Commons)",
              im=ImageOps.mirror(Image.open(right_photo).convert("RGBA")))
    y += hq + 10
    hq = put("folded_q_left", 20, y, 1200, "left side from behind")
    put("folded_q_right", 1250, y, 1200, "right side from behind")
    y += hq + 10
    hq = put("folded_q_front_left", 20, y, 1200, "left side from the front: the butt plate round the barrel")
    put("folded_q_front_right", 1250, y, 1200, "right side from the front")
    y += hq + 10
    hq = put("folded_q_top_left", 20, y, 1200, "from above: the strut along the top's left")
    put("fired_right", 1250, y, 1200, "the bolt back (bolt_fired): the port open, the handle back on the left")
    y += hq + 10
    y += put("open_q", 20, y, 2440, "the stock open (KEDR_STOCK_DEPLOYED)") + 10
    hq = put("mag30_left", 20, y, 800, "the 30-round magazine")
    put("nomag_left", 840, y, 800, "no magazine")
    put("folded_top", 1660, y, 800, "top")
    y += hq + 10
    x = 20
    for n in MAGS:
        put(n + "_side", x, y, 260, n.split("_")[0][-2:] + " rounds")
        put(n + "_q", x + 270, y, 260, None)
        put(n + "_back", x + 540, y, 260, None)
        x += 815
    put("folded_front", x, y, 260, "front")
    put("folded_back", x + 270, y, 260, "rear")
    y += 290
    p.d.text((30, y), "Same game scale, left to right: this Kedr and the main mod's Micro Uzi (0.603 of real size, "
             "as every Guns of Tien gun), GoM's MAC-10 and MP5K (0.72)", fill=(20, 20, 20), font=p.F)
    y += 40
    for i, g in enumerate(("cmp_KEDR", "cmp_MICROUZI", "cmp_gom_MAC10", "cmp_gom_MP5K")):
        hq = put(g, 20 + i * 610, y, 600, None)
    y += hq + 20
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5K.png", "item_MAC10.png", "item_9x19Magazine30_MP5.png")]
    p.icons(20, y, refs + [(icons["KEDR"], "KEDR")] + [(icons[n], n.split("_")[0][-2:] + " rounds") for n in MAGS])
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
