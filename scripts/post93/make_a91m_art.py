#!/usr/bin/env python3
"""A-91M inventory icon, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_a91m_art.py [--renders DIR]

The icon (32x32 RGBA, textures/item_GunsOfTienPost93_A91M.png) from the FBX build_a91m.py exported, with
make_mp7_art.py's renderer on the SCARs' rifle camera and light (as the Grozas): the A-91M with GoM's AK-47 30 at our
size.

--renders DIR (render_a91m.py's output) also writes docs/post93_a91m_preview.png: the gun's left side with its outline
in red on its measuring photo (references/a91: GunRF's A91M2.jpg at 1.294 px a mm, the left side, muzzle left, as the
render `A91M_photo`), the triggers zoomed, the game views, then the reference photos beside the matching renders.
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
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/A91M.png")
GOM_MAGS = os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx")
GOM_AK_TEX = os.path.join(A.G, "textures/weapons/magazines/assault_rifles/762x39Magazine30.png")
SCALE = round(0.603 / 0.645, 4)
# gun -> photo, its px a mm, the trigger crop (photo px)
PHOTOS = {
    "A91M": (os.path.join(ROOT, "references/a91/A91M2.jpg"), (325, 135, 455, 210)),
}
REFS = [("A91M2.jpg", "GunRF: the A-91M (7.62 mm), the measuring photo"),
        ("a91m_raz.jpg", "GunRF's field strip: the launcher, grip and triggers are one lower; the hook (3) rides the rod"),
        ("commons_A-91.jpg", "Commons A-91.jpg (R. Wilk): the 5.56 gun with the same launcher and lower, for the depths"),
        ("commons_556A-91_Interpolitex-2012.jpg", "Commons (V. Kuzmin): the 5.56 gun without launcher, the upper from 3/4")]
NOTES = [
    "A-91M (7.62x39, KBP's catalogue gun with the launcher under the barrel); the 5.56A-91 was removed (user, 2026-11-25).",
    "- rebuilt after the first model was rejected; three remodel passes (CLAUDE.md \"A-91M\")",
    "- the measuring photo shows the LEFT side: the launcher sight's dial and the selector's marks are on the left only",
    "- the charging hook stands on the piston rod under the carrying handle (the field strip's part 3) and rides back on each shot",
    "- the ejection port on the right is placed over the magazine's front (GunRF: cases leave forward on the right; no photo of that side)",
    "- not built yet (TODO): the first 7.62-A91M with the launcher over the barrel",
]


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in ps], uvs) for ps, uvs in tris]


def make_icons():
    rifle = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))["rifle"]
    light = dict(rifle["light"], coef=[[a * 1.35, b * 1.35] for a, b in rifle["light"]["coef"]])
    gun_tex = A.img(TEX)
    made = {}
    for gun in ("A91M",):
        mag, mtex = scaled(A.load_game(GOM_MAGS, "762x39Magazine30"), SCALE), A.img(GOM_AK_TEX)
        objs = [(A.load_game(FBX_GUN, gun + "_BODY"), 0), (A.load_game(FBX_GUN, gun + "_BOLT"), 0),
                (A.attach(mag, PTS[gun]["magazine"]), 1)]
        icon = A.shade(objs, [gun_tex, mtex], dict(rifle["camera"]), light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
        made[gun] = icon
    return made


def check():
    for path in (FBX_GUN,):
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


def overlay(gun, render, at=None):
    """The render (same side and scale as the photo) laid on the photo at `at` (x, y), or where the silhouettes
    overlap best, its outline in red. Returns the overlay, the trigger crop zoomed 4x, the IoU and the offset."""
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
    for dy in ([at[1]] if at else range(oy0 - 20, oy0 + 21)):
        for dx in ([at[0]] if at else range(ox0 - 20, ox0 + 21)):
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


def beside(gun, render, off, box, zoom):
    """The photo's crop over the same crop of the photo-scale render (registered by `off`), both zoomed."""
    ph = Image.open(PHOTOS[gun][0]).convert("RGB")
    r = Image.open(render).convert("RGBA")
    bg = Image.new("RGBA", ph.size, (236, 236, 232, 255))
    bg.alpha_composite(r, off)
    size = ((box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom)
    a = ph.crop(box).resize(size, Image.LANCZOS)
    b = bg.convert("RGB").crop(box).resize(size, Image.LANCZOS)
    out = Image.new("RGB", (size[0], size[1] * 2 + 8), (200, 60, 60))
    out.paste(a, (0, 0))
    out.paste(b, (0, size[1] + 8))
    return out.convert("RGBA")


def sheet(renders, icons):
    p = B.Page(renders, 2100, 14000, "A-91M (Post-93): Workbench renders of the exported FBX on A91M.png "
                                    "(red: the render's outline on the measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    ref = lambda n: Image.open(os.path.join(ROOT, "references/a91", n)).convert("RGBA")
    y = 70
    gun = "A91M"
    photo_render = os.path.join(renders, gun + "_photo.png")
    # where the render sits on the photo, from the model's own frame (build_a91m.py: 1.294 px a mm, origin 495, 168)
    # and not from the best overlap, which GoM's larger magazine pulls a few px off
    frame = json.load(open(os.path.join(renders, "sizes.json")))[gun]["photo_frame_mm"]
    off = (round(495.0 - frame[1] * 1.294), round(168.0 - frame[3] * 1.294))
    full, zoom, iou, _ = overlay(gun, photo_render, off)
    print("%s: placed by the model's frame at %s, silhouette IoU %.3f" % (gun, off, iou))
    p.put(None, 20, y, 1400, "its measuring photo (left side), the model's outline in red (IoU %.2f)" % iou,
          im=full.convert("RGBA"))
    trig = beside(gun, photo_render, off, PHOTOS[gun][1], 5)
    p.put(None, 1440, y, 640, "trigger guard, photo over model: the launcher's loop, the rifle's fin", im=trig)
    y += max(round(full.height * 1400 / full.width), round(trig.height * 640 / trig.width)) + 20
    p.heading(20, y, "Part by part: the measuring photo over the model at the same scale")
    y += 40
    p.put(None, 20, y, 1010, "front half", im=beside(gun, photo_render, off, (0, 0, 460, 300), 3))
    y += p.put(None, 1050, y, 1010, "rear half", im=beside(gun, photo_render, off, (440, 0, 880, 300), 3)) + 25
    p.heading(20, y, "Beside the photos")
    y += 40
    p.put(None, 20, y, 1010, REFS[0][1], im=ref(REFS[0][0]))
    y += p.put(None, 1050, y, 1010, "the model, left side, GoM's AK-47 30 in", im=on_white(r(gun + "_left"))) + 15
    p.put(None, 20, y, 1010, REFS[2][1], im=ref(REFS[2][0]))
    y += p.put(None, 1050, y, 1010, "the model, 3/4 from the left front", im=on_white(r(gun + "_q"))) + 15
    p.put(None, 20, y, 1010, REFS[3][1], im=ref(REFS[3][0]))
    y += p.put(None, 1050, y, 1010, "the model, 3/4 from the right front", im=on_white(r(gun + "_q_right"))) + 15
    p.put(None, 20, y, 1010, REFS[1][1], im=ref(REFS[1][0]))
    y += p.put(None, 1050, y, 1010, "the model from below, left", im=on_white(r(gun + "_q_low"))) + 25
    p.heading(20, y, "Game views")
    y += 40
    p.put(None, 20, y, 1010, "right side", im=on_white(r(gun + "_right")))
    y += p.put(None, 1050, y, 1010, "GoM's rail on the handle clamp, GoM's LR4X", im=on_white(r(gun + "_left_optic"))) + 15
    p.put(None, 20, y, 1010, "3/4 from behind, left", im=on_white(r(gun + "_q_back")))
    y += p.put(None, 1050, y, 1010, "3/4 from behind, right", im=on_white(r(gun + "_q_right_back"))) + 15
    p.put(None, 20, y, 1010, "3/4 with the scope", im=on_white(r(gun + "_q_optic")))
    y += p.put(None, 1050, y, 1010, "charging hook back (bolt_fired)", im=on_white(r(gun + "_bolt_back"))) + 15
    p.put(None, 20, y, 1600, "top (muzzle right)", im=on_white(r(gun + "_top").rotate(-90, expand=True)))
    y += p.put(None, 1640, y, 420, "front", im=on_white(r(gun + "_front"))) + 25
    gom = lambda n: Image.open(os.path.join(A.G, "textures", "item_%s.png" % n)).convert("RGBA")
    p.icons(20, y, [(gom("FAMAS"), "FAMAS (GoM)"), (gom("AK47"), "AK-47 (GoM)"), (icons["A91M"], "A-91M")])
    y += 250
    for line in NOTES:
        p.d.text((30, y), line, fill=(30, 30, 30), font=p.FS)
        y += 26
    lo = p.im.crop((0, 0, 2100, y + 10))
    lo.save(PREVIEW)
    print("wrote", PREVIEW, lo.size)
    return {gun: iou}


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
