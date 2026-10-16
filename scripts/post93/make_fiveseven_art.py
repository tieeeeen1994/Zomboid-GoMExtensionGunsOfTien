#!/usr/bin/env python3
"""FN Five-seveN inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_fiveseven_art.py [--fit] [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) are rendered from the exported FBX files and
textures with make_mp7_art.py's renderer, with a camera and light fitted to GoM's own pistol icons (stored in
fiveseven_icon_cameras.json; --fit, or a missing file, fits them again, which takes a few minutes):

    pistol           item_GLOCK17.png                GLOCK17 body + slide + 9x19Magazine17_Glock
    pistol_magazine  item_9x19Magazine17_GLOCK.png   9x19Magazine17_Glock

    pistol_suppressor item_M&P_Suppressor.png        M&P_Suppressor (GoM's pistol can; for the SFN-57)

--renders DIR (the output of render_fiveseven.py) also writes docs/post93_fiveseven_preview.png: every render is
flipped left-right first, so the sheet shows the gun as the game does (render_fiveseven.py explains why); the outline
panel lays the outline traced from the reference photo (fiveseven_reference_outline.json) over the model's right
side at the photo's scale and reports how much of the two silhouettes overlap.
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402  (FBX reader, attach, icon shading, camera fitting)
import make_p90_art as B                   # noqa: E402  (font, Page)

ROOT = A.ROOT
MEDIA = A.MEDIA
TEX = A.TEX
ICONS = A.ICONS
G = A.G
PREVIEW = os.path.join(ROOT, "docs/post93_fiveseven_preview.png")
POINTS = json.load(open(os.path.join(HERE, "fiveseven_points.json")))
OUTLINE = json.load(open(os.path.join(HERE, "fiveseven_reference_outline.json")))
CAMERAS_JSON = os.path.join(HERE, "fiveseven_icon_cameras.json")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_FIVESEVEN.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_FIVESEVEN_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_FIVESEVEN_parts.fbx")
MAGS = ("57x28Magazine20_FIVESEVEN", "57x28Magazine30_FIVESEVEN")


def gom_scene(kind):
    """(GoM icon, objs, textures) the camera and light of `kind` are fitted on."""
    gom_tex = os.path.join(G, "textures/weapons")
    mags = os.path.join(G, "models_X/weapons/magazines/pistols.fbx")
    mag_tex = A.img(os.path.join(gom_tex, "magazines/pistols/9x19Magazine17_Glock.png"))
    if kind == "pistol":
        f = os.path.join(G, "models_X/weapons/firearms/GLOCK17.fbx")
        objs = [(A.load_game(f, n), 0) for n in ("GLOCK17_BODY", "GLOCK17_SLIDE")]
        objs.append((A.load_game(mags, "9x19Magazine17_Glock"), 1))
        texes = [A.img(os.path.join(gom_tex, "firearms/pistols/GLOCK17.png")), mag_tex]
        icon = "item_GLOCK17.png"
    elif kind == "pistol_suppressor":
        objs = [(A.load_game(os.path.join(G, "models_X/weapons/parts/suppressors.fbx"), "M&P_Suppressor"), 0)]
        texes = [A.img(os.path.join(gom_tex, "parts/suppressors/M&P_Suppressor.png"))]
        icon = "item_M&P_Suppressor.png"
    else:
        objs = [(A.load_game(mags, "9x19Magazine17_Glock"), 0)]
        texes = [mag_tex]
        icon = "item_9x19Magazine17_GLOCK.png"
    return Image.open(os.path.join(G, "textures", icon)).convert("RGBA"), objs, texes


def fit_camera(icon, objs, texes):
    """make_mp7_art.fit_camera's local search, seeded with side views (its coarse grid finds a twisted twin of GoM's
    near-side pistol views: camera error 110 against 52 for the Glock)."""
    bbox = A.MA.alpha_bbox(icon)

    def score(cam, ss=3):
        e, grid = A.coverage_error(icon, objs, cam, ss)
        return e + 0.3 * A.colour_error(icon, grid, texes, ss)

    seeds = [{"yaw": yaw, "pitch": pitch, "roll": float(roll), "bbox": bbox}
             for yaw in (90.0, 270.0) for pitch in (0.0, 180.0) for roll in range(0, 360, 15)]
    seeds.sort(key=lambda c: score(c, 2))
    best = None
    for cam in seeds[:5]:
        cur, err, step = dict(cam), score(cam), 4.0
        while step >= 0.5:
            improved = False
            for key in ("yaw", "pitch", "roll"):
                for d in (-step, step):
                    trial = dict(cur)
                    trial[key] += d
                    e = score(trial)
                    if e < err - 1e-9:
                        cur, err, improved = trial, e, True
            if not improved:
                step /= 2
        if best is None or err < best[0]:
            best = (err, cur)
    return best


def fit_all(kinds=("pistol", "pistol_magazine", "pistol_suppressor")):
    result = json.load(open(CAMERAS_JSON)) if os.path.exists(CAMERAS_JSON) else {}
    for kind in kinds:
        icon, objs, texes = gom_scene(kind)
        err, cam = fit_camera(icon, objs, texes)
        grid = A.raster(objs, cam, icon.width, 4)
        lerr, light = A.fit_light(icon, grid, texes)
        print(kind, "camera error %.2f" % err, cam, "light error %.2f" % lerr, light)
        result[kind] = {"camera": cam, "light": light}
    with open(CAMERAS_JSON, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")


def our_scenes():
    """{icon name: (camera kind, objs, textures)}; our meshes share GoM's pistol conventions, so no turn."""
    gun_tex = A.img(os.path.join(TEX, "FIVESEVEN.png"))
    out = {"FIVESEVEN": ("pistol", [(A.load_game(FBX_GUN, "FIVESEVEN_BODY"), 0),
                                    (A.load_game(FBX_GUN, "FIVESEVEN_SLIDE"), 0),
                                    (A.load_game(FBX_MAGS, MAGS[0]), 1)],
                         [gun_tex, A.img(os.path.join(TEX, MAGS[0] + ".png"))])}
    for n in MAGS:
        out[n] = ("pistol_magazine", [(A.load_game(FBX_MAGS, n), 0)], [A.img(os.path.join(TEX, n + ".png"))])
    out["FIVESEVEN_Suppressor"] = ("pistol_suppressor", [(A.load_game(FBX_PARTS, "FIVESEVEN_Suppressor"), 0)],
                                   [A.img(os.path.join(TEX, "FIVESEVEN_Suppressor.png"))])
    return out


def make_icons():
    if "--fit" in sys.argv:
        fit_all()
    fitted = json.load(open(CAMERAS_JSON)) if os.path.exists(CAMERAS_JSON) else {}
    missing = [k for k in ("pistol", "pistol_magazine", "pistol_suppressor") if k not in fitted]
    if missing:
        fit_all(missing)
        fitted = json.load(open(CAMERAS_JSON))
    made = {}
    for name, (kind, objs, texes) in our_scenes().items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name))
        made[name] = icon
    return made


def check():
    lines = []
    for path, names in ((FBX_GUN, ("FIVESEVEN_BODY", "FIVESEVEN_SLIDE")), (FBX_MAGS, MAGS),
                        (FBX_PARTS, ("FIVESEVEN_Suppressor", "FIVESEVEN_Muzzle_Mount_Device"))):
        objects, unit, lcl = A.header_check(path)
        lines.append("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            tris = A.load_game(path, n)
            mn, mx = A.bounds(tris)
            lines.append("  %-26s %5d tris  Lcl rot %s scl %s  game min %s max %s" % (n, len(tris), rot, scl, mn, mx))
    print("\n".join(lines))


def render(renders, name):
    """A render as the game shows it (flipped left-right, render_fiveseven.py)."""
    return ImageOps.mirror(Image.open(os.path.join(renders, name + ".png")).convert("RGBA"))


def outline_panel(renders):
    cam = json.load(open(os.path.join(renders, "cameras.json")))["right_photo"]
    ren = render(renders, "right_photo")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # right side as in the photo: muzzle on the right
        return w / 2 - (L - cL) * ppm, h / 2 - (H - cH) * ppm

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
    for name, col in (("muzzle", (255, 160, 0)), ("canon", (255, 160, 0)), ("scope", (170, 0, 200)),
                      ("rail_up", (170, 0, 200)), ("underbarrel", (0, 150, 80))):
        o = POINTS[name]["offset"]                  # upside down: upright = (-x, y, -z)
        L = POINTS["_extras"]["photo_origin_mm"][0] - o[1] / 0.00072
        H = POINTS["_extras"]["photo_origin_mm"][1] - o[2] / 0.00072
        x, y = px(L, H)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=col + (255,), width=3)
        d.text((x + 7, y - 20), name, fill=col + (255,), font=B.font(16))
    return page, iou


def photo_at_scale(renders):
    """The reference photo cropped and scaled like the outline panel."""
    cam = json.load(open(os.path.join(renders, "cameras.json")))["right_photo"]
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]
    photo = Image.open(os.path.join(ROOT, "docs/fiveseven_atf.jpg")).convert("RGBA")
    s = 1106.0 / 208.0                              # the trace's px per mm (it was made on this file)
    x1, y1 = 1513.0, 878.0                          # muzzle tip and lowest point in the photo
    k = ppm / s
    photo = photo.resize((round(photo.width * k), round(photo.height * k)), Image.LANCZOS)
    mx, my = x1 * k, y1 * k                         # photo (L 0, H 0) in the scaled photo
    left = mx - (w / 2 + cL * ppm)
    top = my - (h / 2 + cH * ppm)
    return photo.crop((round(left), round(top), round(left) + w, round(top) + h))


def sheet(renders, icons):
    p = B.Page(renders, 2480, 5200, "FN Five-seveN (MarzGuns.FIVESEVEN) for GoM Extension: Guns of Tien - Post-93: "
                                    "Workbench renders of the exported FBX files + textures, as the game shows them")
    y = 70
    ov, iou = outline_panel(renders)
    p.put(None, 20, y + 50, 1200, im=ov)
    p.d.text((30, y), "right side at the photo's scale; red = outline traced from the reference photo; silhouette "
             "overlap (IoU) %.1f%%; blue cross = origin" % (iou * 100), fill=(40, 40, 40), font=p.FS)
    p.put(None, 1250, y + 50, 1200, im=photo_at_scale(renders))
    p.d.text((1260, y), "reference: docs/fiveseven_atf.jpg (U.S. ATF, public domain), same scale",
             fill=(40, 40, 40), font=p.FS)
    y += 50 + 900 + 20

    def put(name, x, y, w, label):
        return p.put(None, x, y, w, label, im=render(renders, name))

    put("q_left", 20, y, 800, "left side from behind (like Five-seveN_USG.jpg)")
    put("q_right", 840, y, 800, "right side from behind")
    put("fired", 1660, y, 800, "slide back (slide_fired)")
    y += 620
    put("left", 20, y, 800, "left side")
    put("top", 840, y, 800, "top")
    put("front", 1660, y, 260, "front")
    put("back", 1940, y, 260, "rear")
    put("nomag_under", 2220, y, 240, "no magazine")
    y += 620
    put("mag30_right", 20, y, 700, "57x28Magazine30_FIVESEVEN fitted")
    put("mag30_q", 740, y, 700, "30-round, left from behind")
    put("mag20_alone", 1460, y, 240, "20-round")
    put("mag30_alone", 1720, y, 240, "30-round")
    y += 640
    put("supp_q", 20, y, 1200, "the shared mount device (as FIVESEVEN_Muzzle_Mount_Device) + SFN-57 at 'canon'")
    put("gom_q", 1240, y, 1200, "GoM: Beretta_Mount (rail_up), PL4_Sight (scope), LP_Light (underbarrel)")
    y += 820
    put("gom2_q", 20, y, 800, "Beretta_Mount, PS1_Sight, LP_Light, suppressor")
    put("lp_right", 840, y, 500, "LP Tactical Light (GoM pistol light)")
    put("tl_right", 1360, y, 500, "TL Tactical Light (GoM pistol light)")
    put("mount_q", 1880, y, 580, "mount device: the threaded-barrel adapter")
    put("supp_alone", 1880, y + 400, 580, "SFN-57 Suppressor")
    y += 600
    p.d.text((30, y), "Same scale, right side: GoM's Glock 17 and the Five-seveN", fill=(20, 20, 20), font=p.F)
    put("glock_right", 20, y + 40, 600, None)
    put("fiveseven_right", 640, y + 40, 600, None)
    refs = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4] + " (GoM)")
            for r in ("item_GLOCK17.png", "item_9x19Magazine17_GLOCK.png")]
    p.icons(1280, y + 40, refs[:1] + [(icons["FIVESEVEN"], "FIVESEVEN")])
    p.icons(1280, y + 290, refs[1:] + [(icons[n], n) for n in MAGS])
    p.icons(1280, y + 540, [(Image.open(os.path.join(G, "textures/item_M&P_Suppressor.png")).convert("RGBA"),
                             "M&P_Suppressor (GoM)"), (icons["FIVESEVEN_Suppressor"], "FIVESEVEN_Suppressor")])
    p.save(PREVIEW)
    print("silhouette IoU %.3f" % iou)


def main():
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
