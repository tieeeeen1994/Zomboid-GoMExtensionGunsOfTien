#!/usr/bin/env python3
"""A-91M inventory icon, FBX check and the review sheet (Python 3 + Pillow).

    py scripts/post93/make_a91m_art.py [GUN ...] [--renders DIR]

GUN: A91M (the default) or A91MPROTO (build_a91m_proto.py's gun, its measuring photo the RIGHT side: sheet
docs/post93_a91m_proto_preview.png). With --renders every see-through opening of the model's side view is checked
against the photo (`openings`): one where the photo shows the gun and not the background is reported.

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
SCALE = round(0.603 / 0.645, 4)
# gun -> points file, measuring photo, its px a mm, the model's origin in it, the side it shows, the trigger crop,
# the magazine drawn in it (FBX, node, texture, scale: GoM's at our size, our own as built)
SPECS = {
    "A91M": ("a91m_points.json", "A91M2.jpg", 1.294, (495.0, 168.0), "left", (325, 135, 455, 210),
             (os.path.join(A.G, "models_X/weapons/magazines/assault_rifles.fbx"), "762x39Magazine30",
              os.path.join(A.G, "textures/weapons/magazines/assault_rifles/762x39Magazine30.png"), SCALE)),
    "A91MPROTO": ("a91m_proto_points.json", "762-a91m.jpg", 1.289, (449.0, 252.0), "right", (485, 215, 615, 310),
                  (os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV98_magazine20.fbx"),
                   "762x54Magazine20_SV98",
                   os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/762x54Magazine20_SV98.png"), 1.0)),
}
GUNS = [a for a in sys.argv[1:] if a in SPECS] or ["A91M"]
PTS = {gun: json.load(open(os.path.join(HERE, SPECS[gun][0])))[gun] for gun in SPECS}
fbx_of = lambda gun: os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_%s.fbx" % gun)
tex_of = lambda gun: os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/%s.png" % gun)
# gun -> photo, its px a mm, the trigger crop (photo px)
PHOTOS = {gun: (os.path.join(ROOT, "references/a91", sp[1]), sp[5]) for gun, sp in SPECS.items()}
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
    made = {}
    for gun in GUNS:
        gun_tex = A.img(tex_of(gun))
        mag_fbx, mag_node, mag_tex, mag_scale = SPECS[gun][6]
        mag, mtex = scaled(A.load_game(mag_fbx, mag_node), mag_scale), A.img(mag_tex)
        objs = [(A.load_game(fbx_of(gun), gun + "_BODY"), 0), (A.load_game(fbx_of(gun), gun + "_BOLT"), 0),
                (A.attach(mag, PTS[gun]["magazine"]), 1)]
        icon = A.shade(objs, [gun_tex, mtex], dict(rifle["camera"]), light)
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % gun))
        made[gun] = icon
    return made


def check():
    for path in [fbx_of(gun) for gun in GUNS]:
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


def photo_offset(gun, renders):
    """Where the photo-scale render sits on the measuring photo, from the model's own frame (the builders' px a mm
    and origin), not from the best overlap, which GoM's magazine pulls a few px off."""
    _, _, px, (ox, oy), side = SPECS[gun][:5]
    frame = json.load(open(os.path.join(renders, "sizes.json")))[gun]["photo_frame_mm"]
    x = ox - frame[1] * px if side == "left" else ox + frame[0] * px
    return round(x), round(oy - frame[3] * px)


def openings(gun, render, off, floor=180):
    """Every enclosed see-through region of the photo-scale render, with the photo's mean brightness there: one the
    photo does not show as background (under `floor`) is a slit between bodies that meet on the real gun, a part
    that floats, or a shine modelled as a gap (user, 2026-11-25). Returns those; prints all. A small real hole (a
    sling ring) reads darker than the background from the photo's blur, hence 180."""
    ph = np.asarray(Image.open(PHOTOS[gun][0]).convert("L")).astype(int)
    a = np.array(Image.open(render).convert("RGBA"))[..., 3] > 128
    m = 20                                                   # a margin of background all round
    solid = np.zeros((ph.shape[0] + 2 * m, ph.shape[1] + 2 * m), bool)
    y0, x0 = max(0, m + off[1]), max(0, m + off[0])
    y1, x1 = min(solid.shape[0], m + off[1] + a.shape[0]), min(solid.shape[1], m + off[0] + a.shape[1])
    solid[y0:y1, x0:x1] = a[y0 - m - off[1]:y1 - m - off[1], x0 - m - off[0]:x1 - m - off[0]]
    seen = solid.copy()
    bad = []
    for sy, sx in zip(*np.nonzero(~solid)):
        if seen[sy, sx]:
            continue
        seen[sy, sx] = True
        stack, cells, edge = [(sy, sx)], [], False
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if not (0 <= yy < solid.shape[0] and 0 <= xx < solid.shape[1]):
                    edge = True
                elif not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if edge or len(cells) < 3:
            continue
        ys, xs = np.array(cells).T - m
        ok = (ys >= 0) & (ys < ph.shape[0]) & (xs >= 0) & (xs < ph.shape[1])
        mean = ph[ys[ok], xs[ok]].mean() if ok.any() else 255.0
        box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        print("  opening %5d px at x %d..%d, y %d..%d: photo brightness %.0f%s" % (
            len(cells), box[0], box[2], box[1], box[3], mean, "" if mean >= floor else "  <-- not background"))
        if mean < floor:
            bad.append(box)
    return bad


def beside(gun, render, off, box, zoom):
    """The photo's crop over the same crop of the photo-scale render (registered by `off`), both zoomed."""
    pad = 80                                             # the model may reach past the photo's edges
    src = Image.open(PHOTOS[gun][0]).convert("RGB")
    ph = Image.new("RGB", (src.width + 2 * pad, src.height + 2 * pad), (255, 255, 255))
    ph.paste(src, (pad, pad))
    r = Image.open(render).convert("RGBA")
    bg = Image.new("RGBA", ph.size, (236, 236, 232, 255))
    bg.alpha_composite(r, (off[0] + pad, off[1] + pad))
    box = (box[0] + pad, box[1] + pad, box[2] + pad, box[3] + pad)
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
    off = photo_offset(gun, renders)
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


NOTES_PROTO = [
    "A-91M Prototype (Post-93): the first A-91M, its 40 mm launcher over the barrel (user, 2026-11-25). In the game the",
    "  longer-barrelled gun of the two, in 7.62x54R on the SV-98's magazines (10, and a 20 made for it): an invented",
    "  chambering and magazine (the real gun is 7.62x39).",
    "- measuring photo: Modern Firearms 762-a91m.jpg, the RIGHT side; scale 1.289 px a mm from GoM's AK magazine fitted to",
    "  the photo's (the gun is about 760 mm long); no photo shows the left side, top or front: the left is the right",
    "  without the selector and the case chute, the widths are the A-91M's; the photo's AK magazine is not the game's",
    "- the launcher's sight leaf folds forward beside the tube (zonwar's photo); the launcher weapon's model raises it",
    "- stretched without a reference for the longer round (as a SCAR-H against a SCAR-L): magazine well and receiver",
    "  23 mm longer to the rear, a heavier barrel 35 mm longer, a bigger flash hider; about 820 mm long",
    "- three remodel passes, then the user's corrections: the guard's bright wedge is shine (solid), no slits between",
    "  bodies, the launcher sits on the beam (CLAUDE.md \"A-91M Prototype\")",
]


def sheet_proto(renders, icons):
    gun = "A91MPROTO"
    p = B.Page(renders, 2100, 16000, "A-91M Prototype (Post-93): Workbench renders of the exported FBX on A91MPROTO.png "
                                    "(red: the render's outline on the measuring photo)")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    ref = lambda n: Image.open(os.path.join(ROOT, "references/a91", n)).convert("RGBA")
    photo_render = os.path.join(renders, gun + "_photo.png")
    off = photo_offset(gun, renders)
    full, zoom, iou, _ = overlay(gun, photo_render, off)
    print("%s: placed by the model's frame at %s, silhouette IoU %.3f" % (gun, off, iou))
    bad = openings(gun, photo_render, off)
    y = 70
    p.put(None, 20, y, 1400, "the 7.62x39 gun's photo (right side) with the model's outline in red: the game's gun "
          "is stretched for its round, so the rear and the muzzle lie outside it", im=full.convert("RGBA"))
    trig = beside(gun, photo_render, off, PHOTOS[gun][1], 5)
    p.put(None, 1440, y, 640, "trigger guard, photo over model: one polished piece, solid behind the trigger", im=trig)
    y += max(round(full.height * 1400 / full.width), round(trig.height * 640 / trig.width)) + 20
    p.heading(20, y, "Part by part: the measuring photo over the model at the same scale")
    y += 40
    p.put(None, 20, y, 1010, "launcher, its seat on the beam; the barrel 35 mm longer than the photo's",
          im=beside(gun, photo_render, off, (590, 10, 1070, 300), 3))
    y += p.put(None, 1050, y, 1010, "butt, receiver, selector: 23 mm further back than the photo's; the 20-round magazine",
               im=beside(gun, photo_render, off, (-40, 130, 400, 400), 3)) + 15
    p.put(None, 20, y, 1010, "carrying handle, charging hook, gas tube", im=beside(gun, photo_render, off, (350, 70, 720, 300), 3))
    y += p.put(None, 1050, y, 1010, "grips and the frame round the opening", im=beside(gun, photo_render, off, (430, 220, 810, 420), 3)) + 25
    p.heading(20, y, "Beside the photos")
    y += 40
    p.put(None, 20, y, 1010, "Modern Firearms: the 7.62-A91M, the measuring photo (leaf raised)", im=ref("762-a91m.jpg"))
    y += p.put(None, 1050, y, 1010, "the launcher weapon's model (leaf raised), the 20-round magazine in",
               im=on_white(r(gun + "_gl_right"))) + 15
    p.put(None, 20, y, 1010, "zonwar.ru: the same gun, the leaf folded", im=ref("top_launcher/zonwar_A-91.jpg"))
    y += p.put(None, 1050, y, 1010, "the rifle's model (leaf folded), right side", im=on_white(r(gun + "_right"))) + 25
    p.heading(20, y, "Game views (no photo shows these sides)")
    y += 40
    p.put(None, 20, y, 1010, "left side", im=on_white(r(gun + "_left")))
    y += p.put(None, 1050, y, 1010, "GoM's rail on the handle clamp, GoM's LR4X", im=on_white(r(gun + "_left_optic"))) + 15
    p.put(None, 20, y, 1010, "3/4 from the left front", im=on_white(r(gun + "_q")))
    y += p.put(None, 1050, y, 1010, "3/4 from the right front", im=on_white(r(gun + "_q_right"))) + 15
    p.put(None, 20, y, 1010, "3/4 from behind, left", im=on_white(r(gun + "_q_back")))
    y += p.put(None, 1050, y, 1010, "3/4 from behind, right", im=on_white(r(gun + "_q_right_back"))) + 15
    p.put(None, 20, y, 1010, "launcher weapon, 3/4 (leaf raised)", im=on_white(r(gun + "_gl_q")))
    y += p.put(None, 1050, y, 1010, "from below, left", im=on_white(r(gun + "_q_low"))) + 15
    p.put(None, 20, y, 1010, "charging hook back (bolt_fired)", im=on_white(r(gun + "_bolt_back")))
    y += p.put(None, 1050, y, 600, "front", im=on_white(r(gun + "_front"))) + 15
    y += p.put(None, 20, y, 1600, "top (muzzle right)", im=on_white(r(gun + "_top").rotate(-90, expand=True))) + 25
    gom = lambda n: Image.open(os.path.join(A.G, "textures", "item_%s.png" % n)).convert("RGBA")
    a91m = Image.open(os.path.join(ICONS, "item_GunsOfTienPost93_A91M.png")).convert("RGBA")
    p.icons(20, y, [(gom("FAMAS"), "FAMAS (GoM)"), (gom("AK47"), "AK-47 (GoM)"), (a91m, "A-91M"),
                    (icons[gun], "A-91M Prototype")])
    y += 250
    for line in NOTES_PROTO:
        p.d.text((30, y), line, fill=(30, 30, 30), font=p.FS)
        y += 26
    lo = p.im.crop((0, 0, 2100, y + 10))
    out = os.path.join(ROOT, "docs/post93_a91m_proto_preview.png")
    lo.save(out)
    print("wrote", out, lo.size)
    return bad


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        renders = sys.argv[sys.argv.index("--renders") + 1]
        if "A91M" in GUNS:
            sheet(renders, icons)
        if "A91MPROTO" in GUNS:
            sheet_proto(renders, icons)


if __name__ == "__main__":
    main()
