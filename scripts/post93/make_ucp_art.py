#!/usr/bin/env python3
"""H&K UCP prototype inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_ucp_art.py [--renders DIR [--photo REFERENCE.png]]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) with the cameras and lights make_fiveseven_art.py
fitted on GoM's Glock 17 and its magazine (fiveseven_icon_cameras.json: `pistol`, `pistol_magazine`), so the two
pistols' icons match; the 40-round drum with the MP7 drum's (mp7_icon_cameras.json `drum`, fitted on GoM's MP5 drum). --renders DIR (render_ucp.py's output) also writes docs/post93_ucp_preview.png, every render
flipped to the game's handedness, with the outline traced from the reference photo (ucp_reference_outline.json) laid
over the left side at the photo's scale.
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
import make_fiveseven_art as F             # noqa: E402

ROOT, MEDIA, TEX, ICONS, G = A.ROOT, A.MEDIA, A.TEX, A.ICONS, A.G
PREVIEW = os.path.join(ROOT, "docs/post93_ucp_preview.png")
POINTS = json.load(open(os.path.join(HERE, "ucp_points.json")))
OUTLINE = json.load(open(os.path.join(HERE, "ucp_reference_outline.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UCP.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UCP_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UCP_parts.fbx")
MAG = "46x30Magazine20_UCP"
MAG40 = "46x30Magazine40_UCP"


def make_icons():
    fitted = json.load(open(F.CAMERAS_JSON))
    fitted["drum"] = json.load(open(A.CAMERAS_JSON))["drum"]
    scenes = {"UCP": ("pistol", [(A.load_game(FBX_GUN, "UCP_BODY"), 0), (A.load_game(FBX_GUN, "UCP_SLIDE"), 0),
                                 (A.load_game(FBX_MAGS, MAG), 1)],
                      [A.img(os.path.join(TEX, "UCP.png")), A.img(os.path.join(TEX, MAG + ".png"))]),
              MAG: ("pistol_magazine", [(A.load_game(FBX_MAGS, MAG), 0)], [A.img(os.path.join(TEX, MAG + ".png"))]),
              MAG40: ("drum", [(A.load_game(FBX_MAGS, MAG40), 0)],
                      [A.img(os.path.join(TEX, MAG40 + ".png"))])}
    made = {}
    for name, (kind, objs, texes) in scenes.items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    for path, names in ((FBX_GUN, ("UCP_BODY", "UCP_SLIDE")), (FBX_MAGS, (MAG, MAG40)), (FBX_PARTS, ("UCP_Muzzle_Mount_Device",))):
        objects, unit, lcl = A.header_check(path)
        print("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            mn, mx = A.bounds(A.load_game(path, n))
            print("  %-26s Lcl rot %s scl %s  game min %s max %s" % (n, rot, scl, mn, mx))


def render(renders, name):
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    ren = render(renders, "left_photo")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # left side as in the photo: muzzle on the left
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
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=2)
    ox, oy = px(*POINTS["_extras"]["photo_origin_mm"])
    d.line([(ox - 25, oy), (ox + 25, oy)], fill=(0, 120, 255, 255), width=2)
    d.line([(ox, oy - 25), (ox, oy + 25)], fill=(0, 120, 255, 255), width=2)
    return page, iou


def photo_at_scale(renders):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    if "--photo" not in sys.argv:                    # the photo's rights are unclear, so it is not kept in the repo
        return None
    photo = sys.argv[sys.argv.index("--photo") + 1]
    im = Image.open(photo).convert("RGBA")
    s = OUTLINE["px_per_mm"]
    k = ppm / s
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    mx, my = OUTLINE["photo_px"]["x_muzzle"] * k, OUTLINE["photo_px"]["y_lowest"] * k
    left, top = mx - (w / 2 - cL * ppm), my - (h / 2 + cH * ppm)
    return im.crop((round(left), round(top), round(left) + w, round(top) + h))


def sheet(renders, icons):
    p = B.Page(renders, 2480, 4200, "H&K UCP Prototype (GunsOfTienPost93.UCP) for GoM Extension: Guns of Tien - "
                                    "Post-93: Workbench renders of the exported FBX files + textures, as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.put(None, 20, y + 50, 1200, im=ov)
    p.d.text((30, y), "left side at the photo's scale; red = outline traced from the reference photo; silhouette "
             "overlap (IoU) %.1f%%; blue cross = origin" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    ph = photo_at_scale(renders)
    if ph is not None:
        p.put(None, 1250, y + 50, 1200, im=ph)
        p.d.text((1260, y), "reference photo (about 2004 prototype), same scale", fill=(40, 40, 40), font=p.FS)
    y += 50 + 900 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("q_left", 20, y, 800, "left side from behind")
    put("q_right", 840, y, 800, "right side from behind (ejection port: not in the photo)")
    put("fired", 1660, y, 800, "slide back (slide_fired)")
    y += 620
    put("right", 20, y, 800, "right side")
    put("top", 840, y, 800, "top")
    put("front", 1660, y, 260, "front")
    put("back", 1940, y, 260, "rear")
    put("mag20_alone", 2220, y, 240, MAG)
    y += 620
    put("mag40_left", 20, y, 640, MAG40 + " (40-round drum) fitted")
    put("mag40_q", 680, y, 640, "drum, left from behind")
    put("mag40_back", 1340, y, 400, "from behind")
    put("mag40_alone", 1760, y, 400, "the drum")
    y += 680
    put("supp_q", 20, y, 1200, "MP7's mount device (as UCP_Muzzle_Mount_Device) + Rotex-II suppressor at 'canon'")
    put("gom_q", 1240, y, 1200, "GoM: Beretta_Mount (rail_up), PL4_Sight (scope), LP_Light (underbarrel)")
    y += 820
    put("gom2_q", 20, y, 800, "Beretta_Mount, PS1_Sight, LP_Light, suppressor")
    put("lp_right", 840, y, 500, "LP Tactical Light (GoM pistol light)")
    put("tl_right", 1360, y, 500, "TL Tactical Light (GoM pistol light)")
    put("mount_q", 1880, y, 580, "mount device: the threaded-barrel adapter")
    y += 420
    p.d.text((30, y), "Same scale, left side: GoM's Glock 17 and the UCP", fill=(20, 20, 20), font=p.F)
    put("glock_left", 20, y + 40, 600, None)
    put("ucp_left", 640, y + 40, 600, None)
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_GLOCK17.png", "item_9x19Magazine17_GLOCK.png")]
    p.icons(1280, y + 40, refs[:1] + [(icons["UCP"], "UCP")])
    p.icons(1280, y + 290, refs[1:] + [(icons[MAG], MAG), (icons[MAG40], MAG40)])
    p.save(PREVIEW)
    print("silhouette IoU %.3f" % iou)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
