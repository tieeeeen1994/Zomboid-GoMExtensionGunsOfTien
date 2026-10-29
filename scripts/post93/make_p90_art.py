#!/usr/bin/env python3
"""FN P90 TR inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_p90_art.py [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) are rendered from the exported FBX files and
textures with the cameras and lights make_mp7_art.py fitted to GoM's own icons (mp7_icon_cameras.json): the gun with
the MP5's, the magazine with the MP5 magazine's (stood on end first, the way GoM's magazines hang), the suppressor
and the mount with GoM's. The icon code is make_mp7_art.py's, imported.

--renders DIR (the output of render_p90.py) also writes the sheets docs/post93_p90_preview.png (the gun; its outline
panel lays the outline traced from the reference photo, p90_reference_outline.json, over the model's right side at
the photo's scale and reports how much of the two silhouettes overlap), post93_p90_magazine.png,
post93_p90_attachments.png (our suppressor and mount, GoM's optics / lights / lasers at the P90's points) and
post93_p90_ammo.png (the 5.7x28mm rounds and boxes).
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402  (FBX reader, attach, icon shading)

ROOT = A.ROOT
MEDIA = A.MEDIA
TEX = A.TEX
ICONS = A.ICONS
G = A.G
PREVIEW = os.path.join(ROOT, "docs/post93_p90_preview.png")
POINTS = json.load(open(os.path.join(HERE, "p90_points.json")))
OUTLINE = json.load(open(os.path.join(HERE, "p90_reference_outline.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx")
NAMES = {FBX_GUN: ("P90TR_BODY", "P90TR_BOLT", "P90TR_HANDLE"), FBX_MAGS: ("57x28Magazine50_P90",),
         FBX_PARTS: ("P90_Suppressor", "P90_Muzzle_Mount_Device")}
STAND_UP = {"offset": [0.0, 0.0, 0.0], "rotate": [90.0, 0.0, 0.0]}     # magazine length from -Y to -Z
# The P90 is held like a pistol and so modelled upside down; icons and sheets show it upright.
HANDGUN = POINTS["_extras"].get("handgun_hold", False)
UPRIGHT = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 180.0 if HANDGUN else 0.0, 0.0]}


def upright_offset(o):
    return [-o[0], o[1], -o[2]] if HANDGUN else list(o)


def our_scenes():
    """{icon name: (camera kind, objs, textures)}"""
    gun_tex = A.img(os.path.join(TEX, "P90TR.png"))
    mag_tex = A.img(os.path.join(TEX, "57x28Magazine50_P90.png"))
    mag = A.load_game(FBX_MAGS, "57x28Magazine50_P90")
    gun = [(A.load_game(FBX_GUN, "P90TR_BODY"), 0), (A.load_game(FBX_GUN, "P90TR_BOLT"), 0),
           (A.load_game(FBX_GUN, "P90TR_HANDLE"), 0),
           (A.attach(mag, POINTS["magazine"]), 1)]
    out = {"P90TR": ("gun", [(A.attach(t, UPRIGHT), i) for t, i in gun], [gun_tex, mag_tex]),
           "57x28Magazine50_P90": ("magazine", [(A.attach(mag, STAND_UP), 0)], [mag_tex])}
    for n, kind in (("P90_Suppressor", "suppressor"), ("P90_Muzzle_Mount_Device", "mount")):
        out[n] = (kind, [(A.load_game(FBX_PARTS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    return out


def make_icons():
    fitted = json.load(open(A.CAMERAS_JSON))
    made = {}
    for name, (kind, objs, texes) in our_scenes().items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    lines = []
    for path, names in NAMES.items():
        objects, unit, lcl = A.header_check(path)
        lines.append("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            tris = A.load_game(path, n)
            mn, mx = A.bounds(tris)
            lines.append("  %-26s %5d tris  Lcl rot %s scl %s  game min %s max %s" % (n, len(tris), rot, scl, mn, mx))
    print("\n".join(lines))
    return lines


def font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def outline_panel(renders):
    """The model's right side (render) with the photo's traced outline over it, and the silhouette overlap."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))["right_photo"]
    ren = Image.open(os.path.join(renders, "right_photo.png")).convert("RGBA")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # right side: muzzle on the left, L grows to the right
        return w / 2 + (L - cL) * ppm, h / 2 - (H - cH) * ppm

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
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=3)
    ox, oy = px(*POINTS["_extras"]["photo_origin_mm"])
    d.line([(ox - 30, oy), (ox + 30, oy)], fill=(0, 120, 255, 255), width=2)
    d.line([(ox, oy - 30), (ox, oy + 30)], fill=(0, 120, 255, 255), width=2)
    for name, col in (("muzzle", (255, 160, 0)), ("canon", (255, 160, 0)), ("magazine", (0, 170, 80)),
                      ("scope", (170, 0, 200)), ("rail_left", (0, 120, 255))):
        o = upright_offset(POINTS[name]["offset"])
        L = POINTS["_extras"]["photo_origin_mm"][0] - o[1] / 0.00072
        H = POINTS["_extras"]["photo_origin_mm"][1] + o[2] / 0.00072
        x, y = px(L, H)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=col + (255,), width=3)
        d.text((x + 8, y - 22), name, fill=col + (255,), font=font(18))
    return page, iou


def sheet(renders, icons):
    W = 2480
    F, FS = font(26), font(18)
    page = Image.new("RGB", (W, 3210), (236, 236, 232))
    d = ImageDraw.Draw(page)

    def put(name, x, y, w=None, label=None, bg=(250, 250, 248), im=None):
        im = im if im is not None else Image.open(os.path.join(renders, name + ".png")).convert("RGBA")
        if w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        box = Image.new("RGBA", im.size, bg + (255,))
        box.alpha_composite(im)
        page.paste(box.convert("RGB"), (x, y))
        if label:
            d.text((x + 10, y + 8), label, fill=(40, 40, 40), font=FS)
        return im.size

    d.text((30, 20), "FN P90 TR for GoM Extension: Guns of Tien - Post-93 (Workbench renders of the exported FBX "
           "files + textures; parts placed at p90_points.json)", fill=(20, 20, 20), font=F)
    y = 70
    put("photo2", 20, y, 1210, "right side from ahead, like the second reference photo")
    put("photo3", 1250, y, 1210, "left side from behind, like the third reference photo")
    y += 720
    ov, iou = outline_panel(renders)
    put(None, 20, y + 56, 1600, None, im=ov)
    d.text((30, y + 2), "right side at the photo's scale; red = outline traced from the reference photo "
           "(p90_reference_outline.json); silhouette overlap (IoU) %.1f%%" % (iou * 100), fill=(40, 40, 40), font=FS)
    d.text((30, y + 26), "blue cross = model origin (rear-top of the grip column); circles = attachment points",
           fill=(40, 40, 40), font=FS)
    put("front", 1650, y, 400, "front")
    put("mag_q34", 2060, y, 400, "57x28Magazine50_P90")
    put("parts_q34", 2060, y + 220, 400, "suppressor + mount device")
    y += 710
    put("top", 20, y, 1210, "top")
    put("under", 1250, y, 1210, "underside (ejection port behind the grip)")
    y += 280
    put("supp_q34", 20, y, 1210, "P90_Muzzle_Mount_Device + P90_Suppressor at 'canon'")
    put("nomag", 1250, y, 1210, "no magazine (the window goes through)")
    y += 720
    d.text((30, y), "Same scale, left side: GoM's FAMAS, GoM's MP5, the P90 TR", fill=(20, 20, 20), font=F)
    y += 40
    for i, n in enumerate(("gom_famas", "gom_mp5", "p90_same")):
        put(n, 20 + i * 820, y, 800)
    y += 300
    d.text((30, y), "Icons (32x32, shown x6 and 1:1), next to the GoM icons whose camera and light they reuse",
           fill=(20, 20, 20), font=F)
    y += 40
    refs = ["item_MP5.png", "item_9x19Magazine30_MP5.png", "item_MKI_Suppressor.png", "item_Muzzle_Mount_Device.png"]
    row = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4]) for r in refs]
    row += [(icons[n], n) for n in ("P90TR", "57x28Magazine50_P90", "P90_Suppressor", "P90_Muzzle_Mount_Device")]
    x = 20
    for im, label in row:
        bg = Image.new("RGBA", (192, 192), (150, 150, 150, 255))
        bg.alpha_composite(im.resize((192, 192), Image.NEAREST))
        page.paste(bg.convert("RGB"), (x, y))
        small = Image.new("RGBA", (32, 32), (150, 150, 150, 255))
        small.alpha_composite(im)
        page.paste(small.convert("RGB"), (x, y + 200))
        d.text((x + 40, y + 205), label[:24], fill=(40, 40, 40), font=FS)
        x += 300
    page.save(PREVIEW)
    print("wrote", PREVIEW, "silhouette IoU %.3f" % iou)


class Page:
    """A sheet with a title, labelled panels and icon rows."""

    def __init__(self, renders, w, h, title):
        self.renders, self.F, self.FS = renders, font(26), font(18)
        self.im = Image.new("RGB", (w, h), (236, 236, 232))
        self.d = ImageDraw.Draw(self.im)
        self.d.text((30, 20), title, fill=(20, 20, 20), font=self.F)

    def put(self, name, x, y, w, label=None, im=None, bg=(250, 250, 248)):
        im = im if im is not None else Image.open(os.path.join(self.renders, name + ".png")).convert("RGBA")
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        box = Image.new("RGBA", im.size, bg + (255,))
        box.alpha_composite(im)
        self.im.paste(box.convert("RGB"), (x, y))
        if label:
            self.d.text((x + 10, y + 8), label, fill=(40, 40, 40), font=self.FS)
        return im.size[1]

    def heading(self, x, y, text):
        self.d.text((x, y), text, fill=(20, 20, 20), font=self.F)

    def texture(self, path, x, y, w, label):
        tex = Image.open(path).convert("RGBA").resize((w, w), Image.NEAREST)
        self.im.paste(tex.convert("RGB"), (x, y + 30))
        self.d.text((x, y), label, fill=(40, 40, 40), font=self.FS)

    def icons(self, x, y, items):
        for im, label in items:
            bg = Image.new("RGBA", (192, 192), (150, 150, 150, 255))
            bg.alpha_composite(im.resize((192, 192), Image.NEAREST))
            self.im.paste(bg.convert("RGB"), (x, y))
            small = Image.new("RGBA", (32, 32), (150, 150, 150, 255))
            small.alpha_composite(im)
            self.im.paste(small.convert("RGB"), (x, y + 200))
            self.d.text((x + 40, y + 205), label[:26], fill=(40, 40, 40), font=self.FS)
            x += 300

    def save(self, path):
        self.im.save(path)
        print("wrote", path)


def icon(name):
    return Image.open(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name)).convert("RGBA")


def magazine_sheet(renders):
    p = Page(renders, 2480, 1880, "57x28Magazine50_P90: the P90 TR's 50-round magazine (smoky translucent body, rounds "
                                  "lying across it in two rows, grey end caps)")
    y = 70
    y += p.put("mag_right", 20, y, 1200, "right side (bullet tips through the body)") + 10
    p.put("mag_left", 20, y, 1200, "left side (case heads)")
    p.put("mag_like2", 1250, 70, 1210, "from the front right")
    y += 210
    p.put("mag_top", 20, y, 1200, "top (rounds seen lying across)")
    y += 220
    p.put("mag_like3", 20, y, 1200, "from the rear left")
    p.put("mag_seated", 1250, 600, 1210, "seated on the receiver, under the rail block and the hoop")
    y = 1390
    p.texture(os.path.join(TEX, "57x28Magazine50_P90.png"), 20, y, 384, "texture 57x28Magazine50_P90.png (128 px, x3)")
    p.heading(450, y, "Icon, next to GoM's MP5 magazine whose camera and light it reuses (stood on end)")
    p.icons(450, y + 40, [(Image.open(os.path.join(G, "textures/item_9x19Magazine30_MP5.png")).convert("RGBA"),
                           "9x19Magazine30_MP5 (GoM)"), (icon("57x28Magazine50_P90"), "57x28Magazine50_P90")])
    p.d.text((1100, y + 60), "Mesh: 176 tris, origin at the front end of the bottom face (point `magazine`).\n"
             "Holds 50 5.7x28mm rounds: SS190, SB193, SS197SR (Gunworks family 5.7x28mm).",
             fill=(40, 40, 40), font=p.FS)
    p.save(os.path.join(ROOT, "docs/post93_p90_magazine.png"))


def attachments_sheet(renders):
    p = Page(renders, 2480, 3170, "P90 TR attachments: its suppressor and muzzle mount device, and GoM's optics, "
                                  "lights and lasers at the P90's points")
    y = 70
    p.put("full_like2", 20, y, 1210, "suppressor + mount, Aimpoint, BrightPoint-5 light, AimRight laser")
    p.put("full_like3", 1250, y, 1210, "the same from the rear left")
    y += 720
    p.heading(30, y, "Muzzle: P90_Muzzle_Mount_Device clamps over the knurled ring and flash hider; P90_Suppressor "
                     "slides over it (both at 'canon')")
    y += 40
    p.put("mount_alone", 20, y, 500, "P90_Muzzle_Mount_Device")
    p.put("mount_fitted", 540, y, 560, "mount on the gun")
    p.put("supp_alone", 1120, y, 1340, "P90_Suppressor (origin = the receiver face)")
    y += 380
    p.put("supp_right", 20, y, 1210, "fitted, right side")
    p.put("supp_q34", 1250, y, 1210, "fitted, from the front right")
    y += 720
    p.heading(30, y, "GoM optics on the TR top rail (point 'scope'; mounted through the hidden integrated rail part)")
    y += 40
    for i, n in enumerate(("Aimpoint_Sight", "EXPS3_Sight", "ReflexS2_Sight", "ElcanX2_Scope")):
        p.put("opt_" + n, 20 + i * 615, y, 600, n)
    y += 330
    p.heading(30, y, "GoM lights (point 'light_left') and lasers ('laser_right') on the rail block's side bosses")
    y += 40
    p.put("acc_left", 20, y, 760, "left: BrightPoint-5 light")
    p.put("acc_right", 800, y, 760, "right: AimRight laser")
    p.put("acc_front", 1580, y, 400, "from the front")
    p.put("acc2_like2", 2000, y, 460, "SR7 light, LRX-7 laser")
    y += 420
    p.texture(os.path.join(TEX, "P90_Suppressor.png"), 20, y, 256, "P90_Suppressor.png (128 px, x2)")
    p.texture(os.path.join(TEX, "P90_Muzzle_Mount_Device.png"), 300, y, 256, "P90_Muzzle_Mount_Device.png")
    refs = [(Image.open(os.path.join(G, "textures", r + ".png")).convert("RGBA"), r[5:] + " (GoM)")
            for r in ("item_MKI_Suppressor", "item_Muzzle_Mount_Device")]
    p.icons(620, y + 30, refs + [(icon("P90_Suppressor"), "P90_Suppressor"),
                                 (icon("P90_Muzzle_Mount_Device"), "P90_Muzzle_Mount_Device")])
    p.save(os.path.join(ROOT, "docs/post93_p90_attachments.png"))


def ammo_sheet(renders):
    p = Page(renders, 2480, 1500, "5.7x28mm for the P90 TR: SS190 (standard, black tip, pierces 2), SB193 (subsonic, "
                                  "violet), SS197SR (polymer tip, blue)")
    y = 70
    variants = (("SS190", "standard: steel / aluminium penetrator"), ("SB193", "subsonic: x0.7 damage, sound x0.7"),
                ("SS197SR", "polymer tip: x1.15 damage, no pierce"))
    for i, (v, note) in enumerate(variants):
        x = 20 + i * 820
        p.put("round_" + v, x, y, 390, "57x28_Bullet%s" % ("" if v == "SS190" else "_" + v))
        p.put("box_" + v, x + 400, y, 390, "57x28_Box%s (50)" % ("" if v == "SS190" else "_" + v))
        p.d.text((x, y + 400), note, fill=(40, 40, 40), font=p.FS)
    y += 450
    p.heading(30, y, "World textures (rounds on GoM's 57x28_Round mesh at 0.015, boxes on vanilla's HandGunAmmoBox at 0.4)")
    y += 40
    wt = os.path.join(MEDIA, "textures/worlditems/GunsOfTienPost93")
    for i, (v, _) in enumerate(variants):
        p.texture(os.path.join(wt, "Rounds/GunsOfTienPost93_57x28_Round_%s.png" % v), 20 + i * 820, y, 256,
                  "Round_%s" % v)
        p.texture(os.path.join(wt, "Boxes/GunsOfTienPost93_57x28_Box_%s.png" % v), 300 + i * 820, y, 256,
                  "Box_%s" % v)
    y += 330
    p.heading(30, y, "Icons (cartons of 12 boxes and crates of 4 cartons use vanilla's ammo parcel and GoM's crate)")
    p.icons(20, y + 40, [(icon("57x28_Round_" + v), "Round_" + v) for v, _ in variants]
            + [(icon("57x28_Box_" + v), "Box_" + v) for v, _ in variants])
    p.save(os.path.join(ROOT, "docs/post93_p90_ammo.png"))


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        renders = sys.argv[sys.argv.index("--renders") + 1]
        sheet(renders, icons)
        magazine_sheet(renders)
        attachments_sheet(renders)
        ammo_sheet(renders)


if __name__ == "__main__":
    main()
