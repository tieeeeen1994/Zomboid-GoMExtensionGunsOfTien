#!/usr/bin/env python3
"""SCAR-L / SCAR-H inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_scar_art.py [--fit] [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) rendered from the exported FBX files and textures
with make_mp7_art.py's renderer. Cameras and lights are fitted on GoM's own icons (scar_icon_cameras.json; --fit
searches again, slow):

    rifle           item_M4A1.png               M4A1 body + bolt + stock + 30-round STANAG
    rifle_magazine  item_762x51Magazine20_FAL.png  762x51Magazine20_FAL (the camera; the light is the MP7's
                                                   magazine light, see make_icons)
    suppressor / mount / drum: the MP7's (mp7_icon_cameras.json, fitted on GoM's MKI suppressor, AR mount device
                               and MP5 100-round drum)

--renders DIR (render_scar.py's output) also writes docs/post93_scar_preview.png: the renders flipped to the game's
handedness, each gun's left side with the outline traced from its reference photo laid over it (scarl_ / scarh_
reference_outline.json; the photos themselves are not in the repo).
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT, MEDIA, TEX, ICONS, G = A.ROOT, A.MEDIA, A.TEX, A.ICONS, A.G
PREVIEW = os.path.join(ROOT, "docs/post93_scar_preview.png")
CAMERAS_JSON = os.path.join(HERE, "scar_icon_cameras.json")
PTS = {g: json.load(open(os.path.join(HERE, g.lower() + "_points.json"))) for g in ("SCARL", "SCARH")}
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SCARH_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx")
GOM_TEX = os.path.join(G, "textures/weapons")
STANAG = os.path.join(G, "models_X/weapons/magazines/assault_rifles.fbx")
M4A1_MAG_POINT = {"offset": [0.0, 0.1015, 0.0144], "rotate": [0.0, 0.0, 0.0]}     # GoM's M4A1 model script


def gom_scene(kind):
    if kind == "rifle":
        f = os.path.join(G, "models_X/weapons/firearms/M4A1.fbx")
        objs = [(A.load_game(f, n), 0) for n in ("M4A1_BODY", "M4A1_BOLT", "M4A1_STOCK")]
        objs.append((A.attach(A.load_game(STANAG, "556x45Magazine30_STANAG"), M4A1_MAG_POINT), 1))
        texes = [A.img(os.path.join(GOM_TEX, "firearms/assault_rifles/M4A1.png")),
                 A.img(os.path.join(GOM_TEX, "magazines/assault_rifles/556x45Magazine30_STANAG.png"))]
        icon = "item_M4A1.png"
    else:
        objs = [(A.load_game(os.path.join(G, "models_X/weapons/magazines/battle_rifles.fbx"),
                             "762x51Magazine20_FAL"), 0)]
        texes = [A.img(os.path.join(GOM_TEX, "magazines/battle_rifles/762x51Magazine20_FAL.png"))]
        icon = "item_762x51Magazine20_FAL.png"
    return Image.open(os.path.join(G, "textures", icon)).convert("RGBA"), objs, texes


def fit_all():
    result = {}
    for kind in ("rifle", "rifle_magazine"):
        icon, objs, texes = gom_scene(kind)
        err, cam = A.fit_camera(icon, objs, texes)
        grid = A.raster(objs, cam, icon.width, 4)
        lerr, light = A.fit_light(icon, grid, texes)
        print(kind, "camera error %.2f" % err, cam, "light error %.2f" % lerr, light)
        result[kind] = {"camera": cam, "light": light}
    with open(CAMERAS_JSON, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")


def gun_objs(g):
    """The gun with its stock deployed (as GoM's M4A1 icon shows its own), charging handle forward, a magazine."""
    p = PTS[g]
    fbx = os.path.join(FIRE, "GunsOfTienPost93_%s.fbx" % g)
    objs = [(A.load_game(fbx, g + "_BODY"), 0), (A.load_game(fbx, g + "_BOLT"), 0),
            (A.attach(A.load_game(FBX_PARTS, "SCAR_STOCK"), p["stock"]), 1)]
    texes = [A.img(os.path.join(TEX, g + ".png")), A.img(os.path.join(TEX, "SCAR_STOCK.png"))]
    if g == "SCARL":
        objs.append((A.attach(A.load_game(STANAG, "556x45Magazine30_STANAG"), p["magazine"]), 2))
        texes.append(A.img(os.path.join(GOM_TEX, "magazines/assault_rifles/556x45Magazine30_STANAG.png")))
    else:
        objs.append((A.attach(A.load_game(FBX_MAGS, "762x51Magazine20_SCARH"), p["magazine"]), 2))
        texes.append(A.img(os.path.join(TEX, "762x51Magazine20_SCARH.png")))
    return objs, texes


def make_icons():
    fitted = json.load(open(CAMERAS_JSON))
    mp7 = json.load(open(A.CAMERAS_JSON))
    fitted["suppressor"], fitted["mount"], fitted["drum"] = mp7["suppressor"], mp7["mount"], mp7["drum"]
    # GoM's FAL magazine is blue-grey steel, and the light fitted on it (gains up to 1.9 on blue) washes the tan
    # magazines out: they keep its camera with the light fitted on GoM's MP5 magazine
    fitted["rifle_magazine"] = {"camera": fitted["rifle_magazine"]["camera"], "light": mp7["magazine"]["light"]}
    # the same for the drum: the MP7 drum's camera (fitted on GoM's MP5 drum), the magazine light (its own washed the
    # tan drum out as well)
    fitted["drum"] = {"camera": mp7["drum"]["camera"], "light": mp7["magazine"]["light"]}
    scenes = {}
    for g in ("SCARL", "SCARH"):
        scenes[g] = ("rifle",) + gun_objs(g)
    for r in (20, 10, 50):
        n = "762x51Magazine%d_SCARH" % r
        scenes[n] = ("drum" if r == 50 else "rifle_magazine", [(A.load_game(FBX_MAGS, n), 0)],
                     [A.img(os.path.join(TEX, n + ".png"))])
    for n, kind in (("SCARH_Suppressor", "suppressor"), ("SCARH_Muzzle_Mount_Device", "mount")):
        scenes[n] = (kind, [(A.load_game(FBX_PARTS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    for path, names in ((os.path.join(FIRE, "GunsOfTienPost93_SCARL.fbx"), ("SCARL_BODY", "SCARL_BOLT")),
                        (os.path.join(FIRE, "GunsOfTienPost93_SCARH.fbx"), ("SCARH_BODY", "SCARH_BOLT")),
                        (FBX_MAGS, ("762x51Magazine20_SCARH", "762x51Magazine10_SCARH", "762x51Magazine50_SCARH")),
                        (FBX_PARTS, ("SCAR_STOCK", "SCARH_Suppressor", "SCARH_Muzzle_Mount_Device"))):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-28s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


OUTLINES = {"SCARL": ("scarl_reference_outline.json", 0.0115, 125.0, "barrel lengthened 97 mm to the STD's 13.8\""),
            "SCARH": ("scarh_reference_outline.json", 0.0, 216.0, "TPRS stock in the photo: the standard one fitted")}


def outline_panel(renders, g):
    """The left-side render with the photo's outline (red) laid over it; IoU over the parts both share."""
    cams = json.load(open(os.path.join(renders, "cameras.json")))[g + "_left"]
    k, ppm, (W, Hh) = cams["k"], cams["px_per_mm"], cams["size"]
    L0, H0 = cams["photo_origin_mm"]
    lmid = cams["centre_game"][1]
    name, tilt, lmin, _ = OUTLINES[g]
    out = [(L, H + tilt * (L - 300.0)) for L, H in json.load(open(os.path.join(HERE, name)))["outline"]]

    def px(L, H):
        return W / 2 - ((L0 - L) * k - lmid) / k * ppm, Hh / 2 - (H - H0) * ppm

    im = render(renders, g + "_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    pts = [px(*p) for p in out]
    d.line(pts + pts[:1], fill=(220, 30, 30), width=2)
    ox, oy = px(L0, H0)
    d.line([(ox - 8, oy), (ox + 8, oy)], fill=(30, 60, 220), width=2)
    d.line([(ox, oy - 8), (ox, oy + 8)], fill=(30, 60, 220), width=2)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    lstock = PTS[g]["_extras"]["photo_origin_mm"][0] + 60.0 if g == "SCARH" else 1e9
    a, b = im.getchannel("A").load(), mask.load()
    inter = union = 0
    for x in range(W):
        L = L0 - ((W / 2 - x) / ppm * k + lmid) / k
        if L < lmin or L > lstock:
            continue
        for y in range(Hh):
            m, p = a[x, y] > 128, b[x, y] > 128
            inter += m and p
            union += m or p
    return bg, inter / max(1, union)


def sheet(renders, icons):
    p = B.Page(renders, 2480, 4980, "FN SCAR-L (Mk 16 STD) and SCAR-H (Mk 17 LB), GunsOfTienPost93.SCARL / SCARH: "
                                    "Workbench renders of the exported FBX files + textures, as the game shows them")
    y = 70
    for g in ("SCARL", "SCARH"):
        ov, iou = outline_panel(renders, g)
        p.d.text((30, y), "%s left side; red = outline traced from the reference photo (%s); silhouette overlap "
                 "%.1f%% from the receiver's front%s; blue cross = origin"
                 % (g, OUTLINES[g][3], iou * 100, " to the hinge" if g == "SCARH" else ""), fill=(40, 40, 40),
                 font=p.FS)
        p.put(None, 20, y + 34, 2440, im=ov)
        y += 34 + 915 + 20
        print("%s silhouette IoU %.3f" % (g, iou))

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    for g in ("SCARL", "SCARH"):
        put(g + "_q_left", 20, y, 800, g + ": left from behind")
        put(g + "_q_right", 840, y, 800, "right from behind (ejection port)")
        put(g + "_folded_q", 1660, y, 800, "stock folded, charging handle back")
        y += 420
    put("SCARL_fitted_q", 20, y, 1200, "SCAR-L: GoM's Aimpoint, MKC foregrip, SR7 light, AimRight laser, AR mount + MKI")
    put("SCARH_fitted_qr", 1240, y, 1200, "SCAR-H: GoM's Elcan, bipod, light, laser; its mount device + suppressor")
    y += 620
    put("SCARL_folded_top", 20, y, 1200, "SCAR-L from above, stock folded (right side)")
    put("SCARH_top", 1240, y, 1200, "SCAR-H from above")
    y += 300
    put("mag20_SCARH", 20, y, 300, "762x51Magazine20_SCARH")
    put("mag10_SCARH", 340, y, 300, "762x51Magazine10_SCARH")
    put("supp_q", 660, y, 700, "SCARH_Suppressor")
    put("mount_q", 1380, y, 500, "SCARH_Muzzle_Mount_Device")
    put("mag50_SCARH", 1900, y, 300, "762x51Magazine50_SCARH")
    y += 440
    put("SCARH_drum_left", 20, y, 800, "SCAR-H with ProMag's 50-round drum")
    put("SCARH_drum_q", 840, y, 800, "the drum from behind, right")
    put("SCARH_drum_front", 1660, y, 300, "from the front")
    y += 440
    p.d.text((30, y), "Same scale, left side: GoM's M4A1 / FAL and the SCARs", fill=(20, 20, 20), font=p.F)
    put("gom_M4A1", 20, y + 40, 1200, None)
    put("SCARL_left", 1240, y + 40, 1200, None)
    put("gom_FAL", 20, y + 520, 1200, None)
    put("SCARH_left", 1240, y + 520, 1200, None)
    y += 1000
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_M4A1.png", "item_FAL.png", "item_762x51Magazine20_FAL.png")]
    p.icons(20, y, refs[:2] + [(icons["SCARL"], "SCARL"), (icons["SCARH"], "SCARH")])
    p.icons(1240, y, refs[2:] + [(icons["762x51Magazine20_SCARH"], "20-round"),
                                 (icons["762x51Magazine10_SCARH"], "10-round")])
    p.icons(20, y + 260, [(icons["762x51Magazine50_SCARH"], "50-round drum"),
                          (icons["SCARH_Suppressor"], "SCARH_Suppressor"),
                          (icons["SCARH_Muzzle_Mount_Device"], "Mount Device")])
    p.save(PREVIEW)


def main():
    if "--fit" in sys.argv:
        fit_all()
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
