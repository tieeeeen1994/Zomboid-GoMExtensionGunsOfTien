#!/usr/bin/env python3
"""Skorpion vz. 82 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_skorpion_art.py [--renders DIR [--photo references/skorpion/skorpion_left_9mak.jpg
                                                   --mags-photo references/skorpion/raw/mf_004.jpg
                                                   --open-photo references/skorpion/raw/commons_010.jpg]]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) with Post-93's make_mp7_art.py renderer and its cameras and
lights (post93/mp7_icon_cameras.json, fitted on GoM's MP5 icons), as the Uzis' and the TMP's:

    SKORPION                    the gun with its stock folded and the 24-round magazine in, turned upright (it is
                                modelled upside down, held like a pistol)
    9x18Magazine<n>_SKORPION    the 12, the 24 and the 30

--renders DIR (render_skorpion.py's output) also writes docs/skorpion_preview.png, every render flipped to the game's
handedness: the left side through the measuring photo's lens with the photo's traced outline over it
(skorpion_reference_outline.json) and the photo beside it (--photo), the part-by-part panels of the remodel passes
(the photo with the model's red outline beside the model's same crop; scripts/ref_crop.py on the lens view), the
magazines beside --mags-photo, the open stock beside --open-photo, other views, GoM's MAC-10 and MP5K and our Micro
Uzi at the same scale, and the icons beside GoM's.
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
PREVIEW = os.path.join(ROOT, "docs/skorpion_preview.png")
PTS = json.load(open(os.path.join(HERE, "skorpion_points.json")))
OUTLINE_JSON = os.path.join(HERE, "skorpion_reference_outline.json")
OUTLINE = json.load(open(OUTLINE_JSON))
OUTLINE["holes_traced"] = [h for h in OUTLINE["holes_traced"] if len(h) >= 3]
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SKORPION.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SKORPION_magazines.fbx")
MAGS = ["9x18Magazine12_SKORPION", "9x18Magazine24_SKORPION", "9x18Magazine30_SKORPION"]
GUN_MAG = MAGS[1]
VIEW = "left_persp"
PARTS = [("trigger and guard", (152, 210, 78, 122)),
         ("selector, rear cap and the stock's hinge", (184, 274, 112, 190)),
         ("muzzle, the butt hooked over the barrel, front sight, cocking knob", (-6, 96, 104, 190)),
         ("grip", (194, 270, 14, 122)),
         ("frame over the magazine well", (88, 190, 108, 152))]


def arg(key):
    return sys.argv[sys.argv.index(key) + 1] if key in sys.argv else None


def gun_objs():
    up = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0, 0.0]}
    objs = [(A.load_game(FBX_GUN, n), 0) for n in ("SKORPION_BODY", "SKORPION_BOLT", "SKORPION_STOCK_FOLDED")]
    objs.append((A.attach(A.load_game(FBX_MAGS, GUN_MAG), PTS["magazine"]), 1))
    objs = [(A.attach(t, up), i) for t, i in objs]
    return objs, [A.img(os.path.join(TEX, "SKORPION.png")), A.img(os.path.join(TEX, GUN_MAG + ".png"))]


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    scenes = {"SKORPION": ("gun",) + gun_objs()}
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
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def on_paper(im, colour=(250, 250, 248, 255)):
    page = Image.new("RGBA", im.size, colour)
    page.alpha_composite(im)
    return page


def lens_panel(renders):
    """The lens view as the photo shows the gun (muzzle left) with the photo's outline in red; IoU with the
    magazine's column left out (the photo's is a modern polymer one)."""
    import numpy as np
    cam = json.load(open(os.path.join(renders, "cameras.json")))[VIEW]
    ren = render(renders, VIEW)                     # mirrored once: muzzle left, as the photo
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
    keep = np.ones_like(a)
    keep[int(px(0, 100)[1]):, int(px(110, 0)[0]):int(px(156, 0)[0])] = False
    iou = (a & b & keep).sum() / max(1, ((a | b) & keep).sum())
    page = on_paper(ren)
    d = ImageDraw.Draw(page)
    for loop in [OUTLINE["outline"]] + OUTLINE["holes_traced"]:
        pts = [px(*p) for p in loop]
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=3)
    box = (int(px(-12, 0)[0]), int(px(0, 196)[1]), int(px(282, 0)[0]), int(px(0, -24)[1]))
    return page.crop(box), iou, (cam, box)


def photo_at_scale(photo, cam, box):
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    s, xm, y0 = OUTLINE["px_per_mm"], OUTLINE["photo_px"]["x_muzzle"], OUTLINE["photo_px"]["y_lowest"]
    x0, y1 = xm + (cL - w / 2 / ppm) * s, y0 - (cH + h / 2 / ppm) * s
    im = Image.open(photo).convert("RGB")
    return im.transform((w, h), Image.EXTENT, (x0, y1, x0 + w / ppm * s, y1 + h / ppm * s), Image.BICUBIC,
                        fillcolor=(255, 255, 255)).crop(box).convert("RGBA")


def part_pairs(renders, photo, px=8):
    cam = json.load(open(os.path.join(renders, "cameras.json")))[VIEW]
    ren = on_paper(render(renders, VIEW), (240, 240, 236, 255)).convert("RGB")
    ppm = cam["px_per_mm"]
    w, h = cam["size"]
    cL, cH = cam["centre_mm"]
    out = []
    for label, (la, lb, ha, hb) in PARTS:
        tmp = os.path.join(renders, "_part.png")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "ref_crop.py"), photo, OUTLINE_JSON, tmp, str(la),
                        str(lb), str(ha), str(hb), "--px", str(px), "--nogrid", "--overlay",
                        os.path.join(renders, VIEW + ".png"), os.path.join(renders, "cameras.json"), VIEW],
                       check=True, stdout=subprocess.DEVNULL)
        ph = Image.open(tmp).convert("RGBA")
        box = (w / 2 + (la - cL) * ppm, h / 2 - (hb - cH) * ppm, w / 2 + (lb - cL) * ppm, h / 2 - (ha - cH) * ppm)
        out.append((label, ph, ren.transform(ph.size, Image.EXTENT, box, Image.BICUBIC).convert("RGBA")))
        os.remove(tmp)
    return out


def sheet(renders, icons):
    photo, mags_photo, open_photo = arg("--photo"), arg("--mags-photo"), arg("--open-photo")
    p = B.Page(renders, 2480, 18000, "Skorpion vz. 82 (GunsOfTien.SKORPION) for GoM Extension: Guns of Tien: "
                                     "Workbench renders of the exported FBX files + textures")
    y = 70
    ov, iou, (cam, box) = lens_panel(renders)
    p.d.text((30, y), "left side through the measuring photo's lens (a phone at 450 mm), as photographed; red = the "
             "photo's traced outline; IoU %.1f%% without the magazine" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    hh = p.put(None, 20, y + 30, 1210, im=ov)
    if photo:
        p.put(None, 1250, y + 30, 1210, "the photo (Commons, CC0: a current Czech 9 mm Makarov semi-automatic with "
              "a polymer magazine)", im=photo_at_scale(photo, cam, box))
    y += hh + 80

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
    p.d.text((30, y), "As the game shows it (muzzle left = the gun's right side)", fill=(20, 20, 20), font=p.F)
    y += 40
    hq = put("left_photo", 20, y, 1200, "left side, orthographic")
    put("right", 1250, y, 1200, "right side (no selector; the same knob and slot)")
    y += hq + 10
    hq = put("q_left", 20, y, 1200, "left side from behind")
    put("q_right", 1250, y, 1200, "right side from behind")
    y += hq + 10
    hq = put("q_top_left", 20, y, 1200, "from above: the top ejection port, the bolt under it")
    put("q_front_left", 1250, y, 1200, "left side from the front")
    y += hq + 10
    hq = put("fired_top", 20, y, 1200, "the bolt back (bolt_fired): both knobs with it, the port open")
    put("top", 1250, y, 1200, "top")
    y += hq + 10
    y += put("open_left", 20, y, 2440, "the stock open (SKORPION_STOCK_DEPLOYED): swung 190 degrees about its "
             "hinge pin") + 10
    if open_photo:
        y += p.put(None, 20, y, 1500, "reference with the stock open (Wikimedia Commons; a vz. 61)",
                   im=Image.open(open_photo).convert("RGBA")) + 10
    hq = put("mag12_left", 20, y, 800, "the 12-round magazine")
    put("mag30_left", 840, y, 800, "the 30-round magazine")
    put("nomag_left", 1660, y, 800, "no magazine")
    y += hq + 10
    x = 20
    for n in MAGS:
        put(n + "_side", x, y, 260, n.split("_")[0][-2:] + " rounds")
        put(n + "_q", x + 270, y, 260, None)
        put(n + "_back", x + 540, y, 260, None)
        x += 815
    y += 290
    if mags_photo:
        y += p.put(None, 20, y, 1100, "a vz. 82 with its three magazines (modernfirearms.net)",
                   im=Image.open(mags_photo).convert("RGBA")) + 10
    hq = put("front", 20, y, 600, "front")
    put("back", 640, y, 600, "rear")
    put("under", 1260, y, 1200, "from below")
    y += hq + 10
    p.d.text((30, y), "Same game scale, left to right: this Skorpion and our Micro Uzi (0.603 of real size, as "
             "every Guns of Tien gun), GoM's MAC-10 and MP5K (0.72)", fill=(20, 20, 20), font=p.F)
    y += 40
    for i, g in enumerate(("cmp_SKORPION", "cmp_MICROUZI", "cmp_gom_MAC10", "cmp_gom_MP5K")):
        hq = put(g, 20 + i * 610, y, 600, None)
    y += hq + 20
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_MP5K.png", "item_MAC10.png", "item_9x19Magazine30_MP5.png")]
    p.icons(20, y, refs + [(icons["SKORPION"], "SKORPION")] + [(icons[n], n.split("_")[0][-2:] + " rounds")
                                                               for n in MAGS])
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
