#!/usr/bin/env python3
"""A-91M / 5.56A-91 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_a91m_art.py [--renders DIR]

Icons (32x32 RGBA, textures/item_GunsOfTienPost93_<name>.png) from the FBX files build_a91m.py exported, with
make_mp7_art.py's renderer on the SCARs' rifle camera and light (as the Grozas): the A-91M with GoM's AK-47 30 at our
size, the 5.56A-91 with its own magazine; the magazine on make_aug_art.py's magazine camera.

--renders DIR (render_a91m.py's output) also writes docs/post93_a91m_preview.png: each gun's side with its outline in
red on its measuring photo (references/a91: GunRF's A91M2.jpg at 1.294 px a mm, Commons' KBP_A_91_noBG.png at 1.693;
both show the left side, muzzle left, as the render `<gun>_photo` does), the triggers zoomed, then the game views.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402
import make_aug_art as AUG                 # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/post93_a91m_preview.png")
PTS = json.load(open(os.path.join(HERE, "a91m_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_A91M.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_A91M_magazines.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/A91M.png")
MAG = "556x45Magazine30_A91M"
MTEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/%s.png" % MAG)
GOM_MAGS = os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx")
GOM_AK_TEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles/762x39Magazine30.png")
SCALE = round(0.603 / 0.645, 4)
# gun -> photo, its px a mm, the trigger crop (photo px)
PHOTOS = {
    "A91M": (os.path.join(ROOT, "references/a91/A91M2.jpg"), (330, 130, 450, 215)),
    "A91M556": (os.path.join(ROOT, "references/a91/KBP_A_91_noBG.png"), (495, 245, 640, 335)),
}
REFS = [("762-a91m.jpg", "the first 7.62-A91M: launcher over the barrel (not built)"),
        ("556-a91m-1.jpg", "the late 5.56 version: railed forearm and front grip instead of the launcher (not built)"),
        ("a91m_raz.jpg", "GunRF's field strip: launcher, grip and triggers are one lower")]
NOTES = [
    "To review (decisions taken overnight, docs/post93_design.md \"KBP A-91M and 5.56A-91\"):",
    "- built: the 7.62 mm A-91M (KBP's catalogue gun, AK magazines) and the 5.56A-91 (its own straight 30-round magazine), both with the launcher under the barrel",
    "- not built: the first 7.62-A91M with the launcher over the barrel, the late 5.56 gun with a railed forearm instead of the launcher",
    "- both measuring photos show the LEFT side (muzzle left); the charging handle is put on the right (GunRF: either side)",
    "- the launcher is integral on both, GoM's M203 way (the 5.56's real one detaches, GoM has no detachable launcher a rifle fires without)",
    "- optics on GoM's Picatinny Rail (Up) clamped on the carrying handle (the Grozas' way); A-91M: GoM's AK mount and AK muzzle parts, no PBS-1; 5.56A-91: GoM's AR mount family",
]


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in ps], uvs) for ps, uvs in tris]


def make_icons():
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    light = dict(rifle["light"], coef=[[a * 1.35, b * 1.35] for a, b in rifle["light"]["coef"]])
    gun_tex = A.img(TEX)
    made = {}
    for gun in ("A91M", "A91M556"):
        if gun == "A91M":
            mag, mtex = scaled(A.load_game(GOM_MAGS, "762x39Magazine30"), SCALE), A.img(GOM_AK_TEX)
        else:
            mag, mtex = A.load_game(FBX_MAGS, MAG), A.img(MTEX)
        objs = [(A.load_game(FBX_GUN, gun + "_BODY"), 0), (A.load_game(FBX_GUN, gun + "_BOLT"), 0),
                (A.attach(mag, PTS[gun]["magazine"]), 1)]
        icon = A.shade(objs, [gun_tex, mtex], dict(rifle["camera"]), light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
        made[gun] = icon
    objs = {MAG: [(A.load_game(FBX_MAGS, MAG), 0)]}
    mlight = dict(rifle["light"], coef=[[a * 1.15, b * 1.15] for a, b in rifle["light"]["coef"]])
    made[MAG] = A.shade(objs[MAG], [A.img(MTEX)], AUG.mag_cameras(objs)[MAG], mlight)
    made[MAG].save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % MAG))
    return made


def check():
    for path in (FBX_GUN, FBX_MAGS):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def on_white(im):
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg


def photo_mask(path):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    if a[..., 3].min() < 255:                                   # transparent background: its alpha, no drop shadow
        return (a[..., 3] > 128) & (a[..., :3].max(-1) < 235), Image.open(path).convert("RGBA")
    return a[..., :3].max(-1) < 200, Image.open(path).convert("RGBA")


def overlay(gun, render):
    """The render (same side and scale as the photo) registered on the photo by the best silhouette overlap, its
    outline in red. Returns the overlay, the trigger crop zoomed 4x, the IoU and the offset."""
    path, trig = PHOTOS[gun]
    fg, ph = photo_mask(path)
    bg = Image.new("RGBA", ph.size, (255, 255, 255, 255))
    ph = Image.alpha_composite(bg, ph).convert("RGB")
    a = np.array(Image.open(render).convert("RGBA"))[..., 3] > 128
    a_rows, a_cols = np.nonzero(a.any(1))[0], np.nonzero(a.any(0))[0]
    f_rows, f_cols = np.nonzero(fg.any(1))[0], np.nonzero(fg.any(0))[0]
    ox0, oy0 = f_cols.min() - a_cols.min(), f_rows.min() - a_rows.min()
    best = None
    h, w = a.shape
    for dy in range(oy0 - 20, oy0 + 21):
        for dx in range(ox0 - 20, ox0 + 21):
            sub = np.zeros_like(fg)
            y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
            x0, x1 = max(0, dx), min(fg.shape[1], dx + w)
            if y1 <= y0 or x1 <= x0:
                continue
            sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            iou = (sub & fg).sum() / max((sub | fg).sum(), 1)
            if best is None or iou > best[0]:
                best = (iou, dx, dy)
    iou, dx, dy = best
    sub = np.zeros_like(fg)
    y0, y1 = max(0, dy), min(fg.shape[0], dy + h)
    x0, x1 = max(0, dx), min(fg.shape[1], dx + w)
    sub[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    er = np.array(Image.fromarray(sub.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))) > 0
    out = np.array(ph).copy()
    out[sub & ~er] = [255, 0, 0]
    full = Image.fromarray(out)
    tx0, ty0, tx1, ty1 = trig
    zoom = full.crop(trig).resize(((tx1 - tx0) * 4, (ty1 - ty0) * 4), Image.NEAREST)
    return full, zoom, iou, (dx, dy)


def sheet(renders, icons):
    p = B.Page(renders, 2100, 7600, "A-91M and 5.56A-91 (Post-93): Workbench renders of the exported FBX on A91M.png "
                                    "(red: the render's outline on the measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    y = 70
    ious = {}
    for gun, label in (("A91M", "A-91M (7.62x39)"), ("A91M556", "5.56A-91")):
        full, zoom, iou, off = overlay(gun, os.path.join(renders, gun + "_photo.png"))
        ious[gun] = iou
        print("%s: silhouette IoU %.3f at %s" % (gun, iou, off))
        p.put(None, 20, y, 1400, "%s: its measuring photo (left side), the model's outline in red (IoU %.2f)"
              % (label, iou), im=full.convert("RGBA"))
        p.put(None, 1440, y, 640, "%s triggers: the launcher's ring, the rifle's blade, 4x" % label,
              im=zoom.convert("RGBA"))
        y += max(round(full.height * 1400 / full.width), round(zoom.height * 640 / zoom.width)) + 20
    for gun, label in (("A91M", "A-91M"), ("A91M556", "5.56A-91")):
        p.heading(20, y, "%s (game views)" % label)
        y += 40
        p.put(None, 20, y, 1010, "side, magazine in", im=on_white(r(gun + "_right")))
        y += p.put(None, 1050, y, 1010, "GoM's rail on the handle clamp, GoM's LR4X", im=on_white(r(gun + "_right_optic"))) + 15
        p.put(None, 20, y, 1010, "3/4 from the front", im=on_white(r(gun + "_q")))
        y += p.put(None, 1050, y, 1010, "3/4 from behind", im=on_white(r(gun + "_q_back"))) + 15
        p.put(None, 20, y, 1010, "3/4 with the scope", im=on_white(r(gun + "_q_optic")))
        y += p.put(None, 1050, y, 1010, "charging handle back (bolt_fired)", im=on_white(r(gun + "_bolt_back"))) + 15
        p.put(None, 20, y, 1600, "top (muzzle right)", im=on_white(r(gun + "_top").rotate(-90, expand=True)))
        y += p.put(None, 1640, y, 420, "front", im=on_white(r(gun + "_front"))) + 25
    p.heading(20, y, "Other versions (references/a91), not built")
    y += 40
    x = 20
    h = 0
    for name, label in REFS:
        im = Image.open(os.path.join(ROOT, "references/a91", name)).convert("RGBA")
        h = max(h, p.put(None, x, y, 660, label, im=im))
        x += 690
    y += h + 25
    gom = lambda n: Image.open(os.path.join(A.G, "textures", "item_%s.png" % n)).convert("RGBA")
    p.icons(20, y, [(gom("FAMAS"), "FAMAS (GoM)"), (gom("AK47"), "AK-47 (GoM)"), (icons["A91M"], "A-91M"),
                    (icons["A91M556"], "5.56A-91"), (icons[MAG], "5.56A-91 30Rds")])
    y += 250
    for line in NOTES:
        p.d.text((30, y), line, fill=(30, 30, 30), font=p.FS)
        y += 26
    lo = p.im.crop((0, 0, 2100, y + 10))
    lo.save(PREVIEW)
    print("wrote", PREVIEW, lo.size)
    return ious


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
