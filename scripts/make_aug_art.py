#!/usr/bin/env python3
"""Steyr AUG A1 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/make_aug_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files and textures build_aug.py
exported, with Post-93's make_mp7_art.py renderer:

    gun        the SCARs' rifle camera and light (post93/scar_icon_cameras.json, fitted on GoM's item_M4A1.png): the
               AUG with its grip folded and its 30-round magazine
    magazine   straight from the side (MAG_CAMERA), the gun's light 15% brighter, the 30-round at the 42-round's
               scale. The MP7's magazine light (fitted on GoM's blued MP5 magazine: blue gain twice the red) ringed
               the light grey translucent body in blue, and fitting each magazine to the box drew both the same size
               (user, 2026-10-28: "fix the mag icon")

--renders DIR (render_aug.py's output) also writes docs/aug_preview.png: the left side with the outline of the
reference photo laid over it (the Commons photo, references/aug, not in the repo; its dark pixels, the sling included,
so the overlap is a lower bound), other views, both magazines, GoM's FAMAS at the same scale, and the icons beside
GoM's FAMAS and STANAG icons.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/aug_preview.png")
PTS = json.load(open(os.path.join(HERE, "aug_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_AUG.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")
MAGS = ["556x45Magazine30_AUG", "556x45Magazine42_AUG"]
RIFLE_CAMERAS = os.path.join(HERE, "post93/scar_icon_cameras.json")
# the reference photo (references/aug/aug_nobg.png): muzzle tip x, heel y, px per mm (build_aug.py's frame)
PHOTO = os.path.join(ROOT, "references/aug/aug_nobg.png")
PHOTO_X0, PHOTO_Y0, PHOTO_S = 270.0, 2190.0, 5.62911


def gun_objs():
    """The gun with its grip folded and its 30-round magazine."""
    objs = [(A.load_game(FBX_GUN, "AUG_BODY"), 0), (A.load_game(FBX_GUN, "AUG_BOLT"), 0),
            (A.load_game(FBX_GUN, "AUG_HANDLE"), 0),
            (A.attach(A.load_game(FBX_GUN, "AUG_FOREGRIP"), PTS["foregrip_folded"]), 0),
            (A.attach(A.load_game(FBX_MAGS, MAGS[0]), PTS["magazine"]), 1)]
    return objs, [A.img(os.path.join(TEX, "AUG.png")), A.img(os.path.join(TEX, MAGS[0] + ".png"))]


MAG_CAMERA = {"yaw": 270.0, "pitch": 0.0, "roll": 34.0, "bbox": [1, 1, 31, 32]}


def extent(objs, cam):
    pts = [A.MA._rotate(p, cam["yaw"], cam["pitch"], cam["roll"]) for tris, _ in objs for ps, _ in tris for p in ps]
    return max(p[0] for p in pts) - min(p[0] for p in pts), max(p[1] for p in pts) - min(p[1] for p in pts)


def mag_cameras(objs):
    """Per magazine, MAG_CAMERA with its box shrunk round the centre so every magazine has the longest one's scale."""
    bx0, by0, bx1, by1 = MAG_CAMERA["bbox"]
    s = min(min((bx1 - bx0) / w, (by1 - by0) / h) for w, h in (extent(o, MAG_CAMERA) for o in objs.values()))
    out = {}
    for n, o in objs.items():
        w, h = extent(o, MAG_CAMERA)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        out[n] = dict(MAG_CAMERA, bbox=[cx - w * s / 2, cy - h * s / 2, cx + w * s / 2, cy + h * s / 2])
    return out


def make_icons():
    rifle = json.load(open(RIFLE_CAMERAS))["rifle"]
    scenes = {"AUG": (rifle,) + gun_objs()}
    mag_light = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    objs = {n: [(A.load_game(FBX_MAGS, n), 0)] for n in MAGS}
    for n, cam in mag_cameras(objs).items():
        scenes[n] = ({"camera": cam, "light": mag_light}, objs[n], [A.img(os.path.join(TEX, n + ".png"))])
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


def render(renders, name, flip=True):
    im = Image.open(os.path.join(renders, name + ".png")).convert("RGBA")
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def outline_panel(renders):
    """The left-side render (the photo's state, mirrored back to the photo's handedness: muzzle left) with the photo's
    gun outline (red: the edge of its dark pixels) and their overlap in the photo's frame."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))["AUG"]
    (W, Hh), s = cam["size"], cam["px_per_mm"]
    Lc, Hc = cam["photo_centre_mm"]
    im = render(renders, "AUG_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    if not os.path.exists(PHOTO):
        return bg, None
    ph = Image.open(PHOTO)
    white = Image.new("RGBA", ph.size, (255, 255, 255, 255))
    white.alpha_composite(ph)
    dark = np.array(white.convert("L")) < 130
    # the photo's frame cropped and scaled to the render's: render px (u, v) <-> photo mm (L, H)
    L0, H0 = Lc - W / 2 / s, Hc + Hh / 2 / s
    box = (int(PHOTO_X0 + L0 * PHOTO_S), int(PHOTO_Y0 - H0 * PHOTO_S),
           int(PHOTO_X0 + (L0 + W / s) * PHOTO_S), int(PHOTO_Y0 - (H0 - Hh / s) * PHOTO_S))
    m = Image.fromarray(dark.astype(np.uint8) * 255).crop(box).resize((W, Hh))
    mm = np.array(m) > 128
    edge = mm ^ np.array(Image.fromarray(mm).filter(ImageFilter.MinFilter(3)))
    arr = np.array(bg)
    arr[edge] = (220, 30, 30, 255)
    model = np.array(im.getchannel("A")) > 128
    iou = (model & mm).sum() / max(1, (model | mm).sum())
    return Image.fromarray(arr), iou


def sheet(renders, icons):
    p = B.Page(renders, 2480, 3360, "Steyr AUG A1, GunsOfTien.AUG: Workbench renders of the exported FBX files + "
                                    "textures, muzzle left (the photo's and the game's view)")
    y = 70
    ov, iou = outline_panel(renders)
    label = "left side, grip down, no magazine (the photo's state)"
    if iou is not None:
        label += ", red = the photo's dark pixels (sling included), overlap %.1f%%" % (iou * 100)
        print("AUG silhouette IoU %.3f (the sling counts against it)" % iou)
    p.d.text((30, y), label, fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 1800, im=ov)
    y += 34 + 680

    def put(name, x, y, w, label, flip=True):
        return p.put(None, x, y, w, label, im=render(renders, name, flip))

    put("AUG_left_mag", 20, y, 1200, "30-round magazine")
    put("AUG_folded_42_fired", 1240, y, 1200, "grip folded, 42-round magazine, charging handle back (fired)")
    y += 620
    put("AUG_right", 20, y, 1200, "right side (ejection port)", flip=False)
    put("AUG_q_right", 1240, y, 1200, "from behind, right")
    y += 640
    put("AUG_folded_q", 20, y, 1200, "grip folded under the barrel")
    put("gom_FAMAS", 1240, y, 1200, "GoM's FAMAS at the same scale")
    y += 640
    put("mag30_q", 20, y, 500, "30-round")
    put("mag42_q", 540, y, 500, "42-round")
    refs = [(Image.open(os.path.join(A.G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_FAMAS.png", "item_556x45Magazine30_STANAG.png")]
    p.icons(1100, y, refs + [(icons[n], n) for n in ["AUG"] + MAGS])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
