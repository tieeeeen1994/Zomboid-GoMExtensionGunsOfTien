#!/usr/bin/env python3
"""RPD inventory icons and the review sheet (Python 3 + Pillow).

    py scripts/make_rpd_art.py [--renders DIR]

Icons (32x32 RGBA, M/textures/item_GunsOfTien_<name>.png) rendered from the FBX files build_rpd.py exported, with
Post-93's make_mp7_art.py renderer:

    RPD                the M249's machine gun camera and light (m249_icon_cameras.json "lmg", fitted on GoM's M60 icon):
                       the gun with its bipod folded and its drum on
    762x39Drum100_RPD  a three-quarter view of its front face (it faces forward, as every drum: from the side it is a
                       slab), as the RPK's drum, in the M249 gun's light

--renders DIR (render_rpd.py's output) also writes docs/rpd_preview.png: the left side over the reference photo at the
same scale (references/rpd, not in the repo: the Finnish army museum's photo), the drum against the Batey ha-Osef
photo's view, the right side with the handle forward and back, the bipod, the drum alone, and the icons beside GoM's
M60 icons.
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import make_p90_art as B                   # noqa: E402

ROOT = A.ROOT
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/rpd_preview.png")
PTS = json.load(open(os.path.join(HERE, "rpd_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPD.fbx")
FBX_DRUM = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPD_drum.fbx")
DRUM = "762x39Drum100_RPD"
REFS = os.path.join(ROOT, "references/rpd")


def make_icons():
    lmg = json.load(open(os.path.join(HERE, "m249_icon_cameras.json")))["lmg"]
    gun = [(A.load_game(FBX_GUN, "RPD_BODY"), 0), (A.load_game(FBX_GUN, "RPD_BOLT"), 0),
           (A.load_game(FBX_GUN, "RPD_BIPOD_FOLDED"), 0), (A.attach(A.load_game(FBX_DRUM, DRUM), PTS["magazine"]), 1)]
    texes = [A.img(os.path.join(TEX, "RPD.png")), A.img(os.path.join(TEX, DRUM + ".png"))]
    drum_cam = {"yaw": 320.0, "pitch": 0.0, "roll": 0.0, "bbox": [1, 1, 31, 31]}
    scenes = {"RPD": (lmg, gun, texes),
              DRUM: ({"camera": drum_cam, "light": lmg["light"]}, [(A.load_game(FBX_DRUM, DRUM), 0)], texes[1:])}
    made = {}
    for name, (fit, objs, tx) in scenes.items():
        icon = A.shade(objs, tx, dict(fit["camera"]), fit["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % name))
        made[name] = icon
    return made


def on_white(im):
    bg = Image.new("RGBA", im.size, (250, 250, 248, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return bg


def sheet(renders, icons):
    p = B.Page(renders, 2480, 3300, "RPD (first model), GunsOfTien.RPD: Workbench renders of the exported FBX files, "
                                    "beside the reference photos at the same scale")
    r = lambda n: Image.open(os.path.join(renders, n + ".png"))
    flip = lambda im: im.transpose(Image.FLIP_LEFT_RIGHT)
    y = 70
    photo = os.path.join(REFS, "rpd_finnish_white.png")
    cam = json.load(open(os.path.join(renders, "cameras.json")))["RPD"]
    if os.path.exists(photo):
        S, XM, YL = 4.4204, 4872, 1372                   # scripts/rpd_reference_outline.json
        f = cam["px_per_mm"] / S
        w, h = cam["size"]
        Lc, Hc = cam["photo_centre_mm"]
        box = (int(XM - (Lc + w / 2 / cam["px_per_mm"]) * S), int(YL - (Hc + h / 2 / cam["px_per_mm"]) * S),
               int(XM - (Lc - w / 2 / cam["px_per_mm"]) * S), int(YL - (Hc - h / 2 / cam["px_per_mm"]) * S))
        ph = Image.open(photo).convert("RGBA").crop(box).resize((w, h))
        p.put(None, 20, y, 1200, "the Finnish army museum's RPD (Commons, public domain): its left side", im=ph)
        ren = on_white(r("RPD_left"))
        p.put(None, 1240, y, 1200, "ours, the same view and scale (its bipod folded, no drum)", im=ren)
        y += 380
        p.put(None, 20, y, 1200, "the two laid over each other", im=Image.blend(ph.convert("RGB"), ren.convert("RGB"),
                                                                                0.5).convert("RGBA"))
        y += 380
    batey = os.path.join(REFS, "r_RPD-machine-gun-batey-haosef-1.png")
    if os.path.exists(batey):
        p.put(None, 20, y, 1000, "the drum fitted: Batey ha-Osef's RPD (CC BY 3.0), its right side from the front",
              im=Image.open(batey).convert("RGBA"))
    p.put(None, 1040, y, 1400, "ours from the front right (the drum faces forward)", im=on_white(r("RPD_q_front_right")))
    y += 720
    p.put(None, 20, y, 1200, "the right side, the operating handle forward", im=on_white(flip(r("RPD_right_drum"))))
    p.put(None, 1240, y, 1200, "the handle back (each shot, cocked, empty)", im=on_white(flip(r("RPD_right_fired"))))
    y += 600
    p.put(None, 20, y, 1200, "bipod deployed", im=on_white(r("RPD_deployed_q")))
    for i, n in enumerate(("drum_side", "drum_front", "drum_q")):
        p.put(None, 1240 + i * 400, y, 380, n.replace("_", ": "), im=on_white(r(n)))
    y += 820
    refs = [(Image.open(os.path.join(A.G, "textures", n)).convert("RGBA"), n[5:-4] + " (GoM)")
            for n in ("item_M60.png", "item_762x51Box100_M60.png")]
    p.icons(20, y, refs + [(icons[n], n) for n in ("RPD", DRUM)])
    p.save(PREVIEW)


def main():
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
