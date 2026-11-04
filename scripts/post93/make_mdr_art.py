#!/usr/bin/env python3
"""MDRx .223 / .308 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_mdr_art.py [--renders DIR] [--photo PATH]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) rendered from the exported FBX files and textures
with make_mp7_art.py's renderer and the SCARs' cameras and lights (scar_icon_cameras.json, fitted on GoM's M4A1 and
FAL magazine icons): the guns with the rifle camera (the .223 with GoM's STANAG 30 at our size, the .308 with the
PMAG 20), the PMAGs with the rifle-magazine camera and the MP7 magazine's light, the D-50 with the MP7 drum's camera
and that light (make_scar_art.py's choices for the SCAR-H's magazines and drum).

--renders DIR (render_mdr.py's output) also writes docs/post93_mdr_preview.png: the renders flipped to the game's
handedness, each gun's left side with the outline traced from Desert Tech's photo laid over it (built from
--photo, references/mdr/deserttech/c196b688-a704-4ffb-909d-f6e44d461cbb.jpg by default, with trace_outline.py's
tracer; the photo itself is not in the repo, only its silhouette is drawn).
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
PREVIEW = os.path.join(ROOT, "docs/post93_mdr_preview.png")
GUNS = ("MDR223", "MDR308")
PTS = {g: json.load(open(os.path.join(HERE, g.lower() + "_points.json"))) for g in GUNS}
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx")
GOM_TEX = os.path.join(G, "textures/weapons")
STANAG = os.path.join(G, "models_X/weapons/magazines/assault_rifles.fbx")
GOT_SCALE = 0.000603 / 0.00065            # the main mod's `_GoT` models of GoM's STANAGs
PMAGS = ["762x51Magazine%d_PMAG" % r for r in (10, 20, 25, 50)]
PHOTO = os.path.join(ROOT, "references/mdr/deserttech/c196b688-a704-4ffb-909d-f6e44d461cbb.jpg")


def scaled(tris, s):
    return [([(x * s, y * s, z * s) for x, y, z in v], uv) for v, uv in tris]


def gun_objs(g):
    """The gun with its charging handles forward and a magazine: GoM's STANAG 30 at our size, or the PMAG 20."""
    p = PTS[g]
    fbx = os.path.join(FIRE, "GunsOfTienPost93_%s.fbx" % g)
    objs = [(A.load_game(fbx, g + n), 0) for n in ("_BODY", "_BOLT", "_HANDLE")]
    texes = [A.img(os.path.join(TEX, g + ".png"))]
    if g == "MDR223":
        objs.append((A.attach(scaled(A.load_game(STANAG, "556x45Magazine30_STANAG"), GOT_SCALE), p["magazine"]), 1))
        texes.append(A.img(os.path.join(GOM_TEX, "magazines/assault_rifles/556x45Magazine30_STANAG.png")))
    else:
        objs.append((A.attach(A.load_game(FBX_MAGS, "762x51Magazine20_PMAG"), p["magazine"]), 1))
        texes.append(A.img(os.path.join(TEX, "762x51Magazine20_PMAG.png")))
    return objs, texes


def make_icons():
    fitted = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))
    mp7 = json.load(open(A.CAMERAS_JSON))
    cams = {"rifle": fitted["rifle"],
            "rifle_magazine": {"camera": fitted["rifle_magazine"]["camera"], "light": mp7["magazine"]["light"]},
            "drum": {"camera": mp7["drum"]["camera"], "light": mp7["magazine"]["light"]}}
    scenes = {g: ("rifle",) + gun_objs(g) for g in GUNS}
    for n in PMAGS:
        scenes[n] = ("drum" if n.endswith("50_PMAG") else "rifle_magazine", [(A.load_game(FBX_MAGS, n), 0)],
                     [A.img(os.path.join(TEX, n + ".png"))])
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(cams[kind]["camera"]), cams[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    for path, names in [(os.path.join(FIRE, "GunsOfTienPost93_%s.fbx" % g), (g + "_BODY", g + "_BOLT", g + "_HANDLE"))
                        for g in GUNS] + [(FBX_MAGS, PMAGS)]:
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def traced_outline(photo):
    """The photo's silhouette in (L, H) mm with trace_outline.py's own steps (the scale the builder used)."""
    import numpy as np
    import trace_outline as T
    im = np.asarray(Image.open(photo).convert("L"), np.float32)
    gun = ~T.flood_background(im > 225)
    gun = T.largest_component(gun) if hasattr(T, "largest_component") else gun
    ys, xs = np.nonzero(gun)
    x_muzzle, y_low = xs.max(), ys.max()
    ppm = (xs.max() - xs.min()) / 698.5
    edge = gun & ~(np.roll(gun, 1, 0) & np.roll(gun, -1, 0) & np.roll(gun, 1, 1) & np.roll(gun, -1, 1))
    ey, ex = np.nonzero(edge)
    return [((x_muzzle - x) / ppm, (y_low - y) / ppm) for x, y in zip(ex, ey)], gun, (x_muzzle, y_low, ppm)


def outline_panel(renders, g, photo):
    """The left-side render with the photo's outline (red dots) over it; IoU over the chassis (the .308's longer
    barrel left out: the photo is a 16")."""
    cams = json.load(open(os.path.join(renders, "cameras.json")))[g + "_left"]
    k, ppm, (W, Hh) = cams["k"], cams["px_per_mm"], cams["size"]
    L0, H0 = cams["photo_origin_mm"]
    lmid, zc = cams["centre_game"][1], cams["centre_game"][2]

    def px(L, H):
        return W / 2 - ((L0 - L) * k - lmid) / k * ppm, Hh / 2 - ((H - H0) * k - zc) / k * ppm

    im = render(renders, g + "_left")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    if not photo or not os.path.exists(photo):
        return bg, None
    pts, gun, (xm, yl, pp) = traced_outline(photo)
    d = ImageDraw.Draw(bg)
    for L, H in pts[::2]:
        x, y = px(L, H)
        d.point((x, y), fill=(220, 30, 30))
    a = im.getchannel("A").load()
    inter = union = 0
    for x in range(W):
        L = L0 - ((W / 2 - x) / ppm * k + lmid) / k
        if L < 66.0 or L > 698.0:
            continue
        for y in range(Hh):
            H = H0 + ((Hh / 2 - y) / ppm * k + zc) / k
            sx, sy = int(round(xm - L * pp)), int(round(yl - H * pp))
            p = 0 <= sy < gun.shape[0] and 0 <= sx < gun.shape[1] and gun[sy, sx]
            m = a[x, y] > 128
            if H < 72.0 and 440.0 < L < 560.0:              # the magazine: none in the photo
                continue
            inter += m and p
            union += m or p
    return bg, inter / max(1, union)


def sheet(renders, icons, photo):
    p = B.Page(renders, 2480, 5500,"Desert Tech MDRx .223 (16\", side eject, black) and .308 (20\", forward eject, "
                                    "FDE), GunsOfTienPost93.MDR223 / MDR308: Workbench renders of the exported FBX "
                                    "files + textures, as the game shows them")
    y = 70
    for g in GUNS:
        ov, iou = outline_panel(renders, g, photo)
        label = "%s left side" % g
        if iou is not None:
            label += "; red = outline of Desert Tech's 16\" photo, silhouette overlap %.1f%% from the handguard's nose " \
                     "(magazine left out%s)" % (iou * 100, "; the photo has the stock handguard, ours BLK LBL's ALX"
                                                if g == "MDR308" else "")
            print("%s silhouette IoU %.3f" % (g, iou))
        p.d.text((30, y), label, fill=(40, 40, 40), font=p.FS)
        p.put(None, 20, y + 34, 2440, im=ov)
        y += 34 + 915 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    for g in GUNS:
        put(g + "_q_left", 20, y, 800, g + ": left from behind")
        put(g + "_q_right", 840, y, 800, "right from behind (the carrier's window)")
        put(g + "_back_right", 1660, y, 800, "right: carrier and charging handles back")
        y += 420
    put("MDR223_fitted_q", 20, y, 1200, "MDR223: GoM's Aimpoint, MKC foregrip, SR7 light, AimRight laser, AR mount + MKI")
    put("MDR308_fitted_qr", 1240, y, 1200, "MDR308: GoM's LR4X, light, laser; the SCAR-H's mount + SOCOM762-RC")
    y += 620
    put("MDR308_alx_deployed_q", 20, y, 1200, "MDR308: BLK LBL's ALX legs deployed (folded: its left side above)")
    put("MDR308_alx_deployed_front", 1240, y, 560, "from the front")
    put("MDR308_alx_folded_front", 1820, y, 560, "legs folded")
    y += 700
    put("MDR223_rails_left", 20, y, 1200, "MDR223: GoM's Picatinny Rail Left / Right drawn as our M-LOK sections")
    put("MDR308_rails_right", 1240, y, 1200, "MDR308: its right rail on the ALX's 3 o'clock M-LOK row")
    y += 480
    for i, r in enumerate((10, 20, 25, 50)):
        put("pmag%d" % r, 20 + i * 330, y, 300, "PMAG %d" % r)
    put("MDR308_drum_left", 1360, y, 1100, "MDR308 with the D-50")
    y += 520
    p.d.text((30, y), "Same scale, left side: GoM's FAMAS and the MDRs", fill=(20, 20, 20), font=p.F)
    put("gom_FAMAS", 20, y + 40, 800, None)
    put("MDR223_left", 840, y + 40, 800, None)
    put("MDR308_left", 1660, y + 40, 800, None)
    y += 380
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_M4A1.png", "item_FAL.png", "item_762x51Magazine20_FAL.png")]
    p.icons(20, y, refs[:2] + [(icons["MDR223"], "MDR223"), (icons["MDR308"], "MDR308")])
    p.icons(1240, y, refs[2:] + [(icons[n], n.split("_")[0][-2:] + " PMAG") for n in PMAGS])
    p.save(PREVIEW)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        photo = sys.argv[sys.argv.index("--photo") + 1] if "--photo" in sys.argv else PHOTO
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons, photo)


if __name__ == "__main__":
    main()
