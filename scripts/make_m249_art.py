#!/usr/bin/env python3
"""M249 and belt link inventory icons and the M249's review sheet (Python 3 + Pillow).

    python3 scripts/make_m249_art.py [--fit] [--renders DIR]

Icons (32x32 RGBA, Contents/mods/GoMExtensionGunsOfTien/42/media/textures/item_GunsOfTien_<name>.png) rendered from
the FBX files and textures build_m249.py exported, with make_mp7_art.py's renderer. Cameras and lights are fitted on
GoM's own icons (m249_icon_cameras.json; --fit searches again, slow):

    lmg   item_M60.png                M60 body + bolt + folded bipod + its 100-round box and belt
    box   item_762x51Box100_M60.png   762x51Box100_M60 (fitted, but the icon uses the MP7 magazine's camera and light
                                      from post93/mp7_icon_cameras.json, see make_icons)

--renders DIR (render_m249.py's output) also writes docs/m249_preview.png: the renders flipped to the game's
handedness, the right side with the outline traced from the reference photo (m249_reference_outline.json, from
docs/m249_usaf.jpg turned 13 degrees) laid over it.
"""

import json
import os
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
PREVIEW = os.path.join(ROOT, "docs/m249_preview.png")
CAMERAS_JSON = os.path.join(HERE, "m249_icon_cameras.json")
PTS = json.load(open(os.path.join(HERE, "m249_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_M249.fbx")
FBX_BOX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_M249_box.fbx")
FBX_LINKS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_Links.fbx")
GOM_TEX = os.path.join(G, "textures/weapons")
GOM_LMG = os.path.join(G, "models_X/weapons/magazines/lmgs.fbx")
ZERO = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}


def gom_scene(kind):
    box_tex = A.img(os.path.join(GOM_TEX, "magazines/lmgs/762x51Box100_M60.png"))
    if kind == "lmg":
        f = os.path.join(G, "models_X/weapons/firearms/M60.fbx")
        objs = [(A.load_game(f, n), 0) for n in ("M60_BODY", "M60_BOLT", "M60_BIPOD_FOLDED")]
        objs += [(A.load_game(GOM_LMG, n), 1) for n in ["762x51Box100_M60"] + ["762x51_M60_%d" % i
                                                                               for i in range(1, 10)]]
        texes = [A.img(os.path.join(GOM_TEX, "firearms/lmgs/M60.png")), box_tex]
        icon = "item_M60.png"
    else:
        objs = [(A.load_game(GOM_LMG, "762x51Box100_M60"), 0)]
        texes = [box_tex]
        icon = "item_762x51Box100_M60.png"
    return Image.open(os.path.join(G, "textures", icon)).convert("RGBA"), objs, texes


def fit_all():
    result = {}
    for kind in ("lmg", "box"):
        icon, objs, texes = gom_scene(kind)
        err, cam = A.fit_camera(icon, objs, texes)
        grid = A.raster(objs, cam, icon.width, 4)
        lerr, light = A.fit_light(icon, grid, texes)
        print(kind, "camera error %.2f" % err, cam, "light error %.2f" % lerr, light)
        result[kind] = {"camera": cam, "light": light}
    with open(CAMERAS_JSON, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")


def make_icons():
    fitted = json.load(open(CAMERAS_JSON))
    # GoM's M60 box is wider than deep and the camera fitted on its icon lays ours on its side, and its light turns
    # olive drab yellow: the box uses the MP7 magazine's camera and light (fitted on GoM's MP5 magazine), upright with
    # its stencilled side in view
    fitted["box"] = json.load(open(A.CAMERAS_JSON))["magazine"]
    gun = [(A.load_game(FBX_GUN, "M249_BODY"), 0), (A.attach(A.load_game(FBX_GUN, "M249_COVER"), PTS["cover"]), 0),
           (A.load_game(FBX_GUN, "M249_BIPOD_FOLDED"), 0),
           (A.attach(A.load_game(FBX_BOX, "556x45Box200_M249"), PTS["box"]), 1)]
    gun += [(A.load_game(FBX_BOX, "556x45_M249_%d" % i), 1) for i in range(1, 10)]
    texes = [A.img(os.path.join(TEX, "M249.png")), A.img(os.path.join(TEX, "556x45Box200_M249.png"))]
    scenes = {"M249": ("lmg", gun, texes),
              "556x45Box200_M249": ("box", [(A.load_game(FBX_BOX, "556x45Box200_M249"), 0)], texes[1:])}
    # belt links and their boxes (build_links.py): the boxes with the MP7 magazine's camera and light; the links,
    # which no GoM icon resembles, seen a little from above, the wide loop with its hole and both narrow loops in view (yaw 120, pitch 30) in that light
    # made grey (its three channels averaged, the mount device's light turned the steel blue) and brighter
    mp7 = json.load(open(A.CAMERAS_JSON))
    mag = mp7["magazine"]["light"]
    grey = [sum(c[0] for c in mag["coef"]) / 3.0 * 1.8, sum(c[1] for c in mag["coef"]) / 3.0 * 1.4]
    fitted["link"] = {"camera": {"yaw": 120.0, "pitch": 30.0, "roll": 0.0, "bbox": (3, 3, 29, 29)},
                      "light": {"dir": mag["dir"], "coef": [grey, grey, grey]}}
    fitted["linkbox"] = mp7["magazine"]
    for node, kind in (("M27_Link", "link"), ("M13_Link", "link"), ("LinkBox_M27", "linkbox"),
                       ("LinkBox_M13", "linkbox")):
        scenes[node] = (kind, [(A.load_game(FBX_LINKS, node), 0)], [A.img(os.path.join(TEX, node + ".png"))])
    made = {}
    for name, (kind, objs, tx) in scenes.items():
        icon = A.shade(objs, tx, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % name))
        made[name] = icon
    return made


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    """The right-side render (muzzle right after the flip, as the photo) with the traced outline over it."""
    cams = json.load(open(os.path.join(renders, "cameras.json")))["M249_right"]
    k, ppm, (W, Hh) = cams["k"], cams["px_per_mm"], cams["size"]
    L0, H0 = cams["photo_origin_mm"]
    lmid = cams["centre_game"][1]
    out = json.load(open(os.path.join(HERE, "m249_reference_outline.json")))["outline"]

    def px(L, H):
        return W / 2 + ((L0 - L) * k - lmid) / k * ppm, Hh / 2 - (H - H0) * ppm

    im = render(renders, "M249_right")
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    pts = [px(*p) for p in out]
    d.line(pts + pts[:1], fill=(220, 30, 30), width=2)
    ox, oy = px(L0, H0)
    d.line([(ox - 8, oy), (ox + 8, oy)], fill=(30, 60, 220), width=2)
    d.line([(ox, oy - 8), (ox, oy + 8)], fill=(30, 60, 220), width=2)
    return bg


def sheet(renders, icons):
    p = B.Page(renders, 2480, 4500, "M249 Light Machine Gun (PIP), GunsOfTien.M249: Workbench renders of the "
                                    "exported FBX files + textures, as the game shows them")
    y = 70
    p.d.text((30, y), "Right side, bipod folded, no feed; red = outline traced from docs/m249_usaf.jpg (bipod "
                      "deployed there); blue cross = origin", fill=(40, 40, 40), font=p.FS)
    p.put(None, 20, y + 34, 2440, im=outline_panel(renders))
    y += 34 + 1070 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("M249_left_box", 20, y, 1200, "left side, 200-round box and belt")
    put("M249_left_stanag", 1240, y, 1200, "left side, GoM's 30-round STANAG in the magazine well")
    y += 560
    put("M249_q_left_box", 20, y, 1200, "from behind, left")
    put("M249_q_right_box", 1240, y, 1200, "from behind, right (cocking handle)")
    y += 700
    put("M249_q_left_open", 20, y, 1200, "feed cover open")
    put("M249_left_deployed", 1240, y, 1200, "bipod deployed")
    y += 780
    put("M249_front_box", 20, y, 400, "front: box")
    put("M249_front_stanag", 440, y, 400, "front: STANAG")
    put("M249_front_deployed", 860, y, 400, "front: bipod")
    put("M249_belt4", 1280, y, 600, "four rounds left on the belt")
    y += 480
    p.d.text((30, y), "Same scale, left side: GoM's M60", fill=(20, 20, 20), font=p.F)
    put("gom_M60_left", 20, y + 40, 1200, None)
    y += 640
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_M60.png", "item_762x51Box100_M60.png")]
    p.icons(20, y, refs + [(icons["M249"], "M249"), (icons["556x45Box200_M249"], "200-round box")])
    p.save(PREVIEW)


def main():
    if "--fit" in sys.argv:
        fit_all()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
