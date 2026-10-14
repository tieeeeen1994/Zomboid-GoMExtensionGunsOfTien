#!/usr/bin/env python3
"""Build every FN P90 TR asset of GoM Extension: Guns of Tien - Post-93, in order (Python 3 + Pillow, Blender 5.2).

    python3 make_p90.py [--quick] [--no-preview]

1. p90_decals.py   decal sheets (Pillow)                         -> a temporary work folder
2. build_p90.py    meshes, FBX export, bakes, textures (Blender)  -> media/models_X, media/textures/weapons/...
3. p90_icons.py    32x32 icons (Pillow, GoM's icon cameras)       -> media/textures/item_GunsOfTienPost93_*.png
4. p90_points.json attachment points for the model script, checked against the exported FBX
5. p90_preview.py  review renders (Blender) + layout here         -> docs/post93_p90_preview.png

The geometry, the points and every number live in p90_geometry.py. Same inputs, same files: bakes and noise are
seeded and PNGs are written without metadata.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
DOCS = os.path.join(ROOT, "docs")
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
sys.path.insert(0, HERE)
import p90_geometry as G  # noqa: E402
import p90_meshio as IO  # noqa: E402


def run(cmd):
    print("+", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout + res.stderr
    for line in out.splitlines():
        if line.startswith("[") or "Error" in line or "Traceback" in line or line.startswith("  File"):
            print("   ", line)
    if res.returncode != 0 or "Traceback" in out:
        raise SystemExit("failed: %s" % " ".join(cmd))


def blender(script, *args):
    run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, script), "--"] + list(args))


def verify():
    """Read the FBX files back as the game does; check the header against GoM's and return the bounds."""
    fx = os.path.join(MEDIA, "models_X/weapons")
    files = {
        "firearms/GunsOfTienPost93_P90TR.fbx": ["P90TR_BODY", "P90TR_BOLT"],
        "magazines/GunsOfTienPost93_P90_magazines.fbx": ["57x28Magazine50_P90"],
        "parts/GunsOfTienPost93_P90_parts.fbx": ["P90_Suppressor", "P90_Muzzle_Mount_Device"],
    }
    report = {}
    for rel, nodes in files.items():
        path = os.path.join(fx, rel)
        h = IO.header(path)
        assert h["version"] == 7400 and h["UnitScaleFactor"] == 1.0, h
        assert h["objects"] == ["Geometry", "Model"], h["objects"]
        assert (h["UpAxis"], h["FrontAxis"], h["CoordAxis"]) == (1, 2, 0), h
        assert sorted(h["models"]) == sorted(nodes), h["models"]
        for node, lcl in h["models"].items():
            rot = lcl.get("Lcl Rotation", (0, 0, 0))
            sca = lcl.get("Lcl Scaling", (1, 1, 1))
            assert all(abs(v) < 1e-3 for v in rot) and all(abs(v - 1) < 1e-3 for v in sca), (node, lcl)
        for node in nodes:
            tris = IO.load_game_mesh(path, node)
            b = IO.bounds(tris)
            report[node] = {"tris": len(tris), "x": [round(v, 4) for v in b[0]], "y": [round(v, 4) for v in b[1]],
                            "z": [round(v, 4) for v in b[2]]}
            print("    %-26s %5d tris  x %+.4f..%+.4f  y %+.4f..%+.4f  z %+.4f..%+.4f"
                  % ((node, len(tris)) + b[0] + b[1] + b[2]))
    return report


def write_points(bounds):
    pts = G.points()
    with_mag = {k: [min(bounds["P90TR_BODY"][k][0], bounds["57x28Magazine50_P90"][k][0] + o),
                    max(bounds["P90TR_BODY"][k][1], bounds["57x28Magazine50_P90"][k][1] + o)]
                for k, o in zip("xyz", pts["magazine"]["offset"])}
    data = dict(pts)
    data["_notes"] = {
        "keys": "keys starting with _ are not attachment points",
        "space": "game space: +Y muzzle, +Z top, +X the gun's left; origin = rear-top of the pistol grip",
        "magazine": "57x28Magazine50_P90's origin is its front end, centred, on its bottom face; the node lies "
                    "along -Y from there on the receiver top, so `magazine` is that front-centre mounting point",
        "canon": "front face of the receiver nose where the flash hider starts (GoM puts canon behind the muzzle "
                 "tip, FAMAS 0.034); P90_Muzzle_Mount_Device and P90_Suppressor have their origin at their rear "
                 "face and extend along +Y over the flash hider",
        "bolt_fired": "charging handle travel (P90TR_BOLT is modelled forward); the real P90's handles do not "
                      "reciprocate when firing",
        "ejection_port": "centre of the downward ejection port under the stock, behind the grip (Hot Brass)",
        "rail_up/scope": "top of the Picatinny teeth, above the grip; the rail's underside clears the magazine",
    }
    data["_extras"] = G.extras()
    data["_bounds"] = {k: bounds[k] for k in bounds}
    data["_bounds"]["gun_with_magazine"] = [[round(a, 4), round(b, 4)] for a, b in with_mag.values()]
    path = os.path.join(HERE, "p90_points.json")
    lines = ["{"]
    keys = list(data)
    for i, k in enumerate(keys):
        sep = "," if i < len(keys) - 1 else ""
        if k.startswith("_"):
            body = json.dumps(data[k], indent=2).replace("\n", "\n  ")
            lines.append('  "%s": %s%s' % (k, body, sep))
        else:
            lines.append('  "%s": %s%s' % (k, json.dumps(data[k]), sep))
    lines.append("}")
    with open(path, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print("    wrote", path)


# --------------------------------------------------------------------------------------------------
# Preview sheet
# --------------------------------------------------------------------------------------------------

def outline(img, colour):
    """Edge pixels of an RGBA render's silhouette, as an RGBA overlay."""
    a = img.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    from PIL import ImageFilter
    edge = Image.eval(Image.merge("RGB", [a, a, a]).filter(ImageFilter.FIND_EDGES).getchannel("R"),
                      lambda v: 255 if v > 0 else 0)
    edge = edge.filter(ImageFilter.MaxFilter(3))
    over = Image.new("RGBA", img.size, colour + (0,))
    over.putalpha(edge)
    return over


def preview(prev):
    with open(os.path.join(prev, "views.json")) as handle:
        views = json.load(handle)
    font = ImageFont.truetype(FONT, 22)
    small = ImageFont.truetype(FONT, 16)
    W = 1900
    sheet = Image.new("RGBA", (W, 3200), (118, 120, 124, 255))
    d = ImageDraw.Draw(sheet)

    def put(name, x, y, label, scale=1.0):
        im = Image.open(os.path.join(prev, "view_%s.png" % name)).convert("RGBA")
        if scale != 1.0:
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        sheet.alpha_composite(im, (x, y))
        d.text((x + 8, y + 6), label, font=font, fill=(255, 255, 255, 255))
        return im

    d.text((16, 10), "FN P90 TR for GoM Extension: Guns of Tien - Post-93  (generated by scripts/post93/make_p90.py)",
           font=font, fill=(255, 255, 255, 255))
    put("p90_34", 0, 40, "3/4 front, magazine fitted")
    put("p90_left", 950, 40, "left side (+X), muzzle left")
    put("p90_right", 950, 560, "right side (-X)")
    put("p90_top", 0, 650, "top (gun's left up)")
    put("p90_rear34", 0, 960, "3/4 rear")
    put("p90_under", 950, 1080, "underside: ejection port, selector")
    put("mag_34", 0, 1700, "57x28Magazine50_P90 alone")
    put("supp_34", 600, 1700, "P90_Suppressor fitted at canon")
    put("mount_34", 1300, 1700, "P90_Muzzle_Mount_Device over the flash hider", 1.0)

    # Scale / origin overlay: P90 with GoM's FAMAS (red) and MP5 (cyan) silhouettes, same camera.
    y0 = 2650
    base = Image.open(os.path.join(prev, "view_p90_left_wide.png")).convert("RGBA")
    famas = Image.open(os.path.join(prev, "view_famas_left.png")).convert("RGBA")
    mp5 = Image.open(os.path.join(prev, "view_mp5_left.png")).convert("RGBA")
    ghost = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for img, col in ((famas, (255, 70, 60)), (mp5, (60, 220, 255))):
        ghost.alpha_composite(outline(img, col))
    over = Image.new("RGBA", base.size, (0, 0, 0, 0))
    over.alpha_composite(base)
    over.alpha_composite(ghost)
    v = views["p90_left_wide"]
    px_per = v["res"][0] / v["scale"]

    def to_px(game):
        world = (game[0], -game[1], game[2])
        rel = [world[k] - v["centre"][k] for k in range(3)]
        return (v["res"][0] / 2 + sum(rel[k] * v["right"][k] for k in range(3)) * px_per,
                v["res"][1] / 2 - sum(rel[k] * v["up"][k] for k in range(3)) * px_per)

    od = ImageDraw.Draw(over)
    ox, oy = to_px((0, 0, 0))
    od.line([(ox - 30, oy), (ox + 30, oy)], fill=(255, 255, 0, 255), width=2)
    od.line([(ox, oy - 30), (ox, oy + 30)], fill=(255, 255, 0, 255), width=2)
    for name, col in (("muzzle", (255, 255, 0)), ("canon", (255, 160, 0)), ("magazine", (0, 255, 120)),
                      ("scope", (255, 0, 255)), ("light_left", (255, 255, 255))):
        x, y = to_px(G.points()[name]["offset"])
        od.ellipse([x - 5, y - 5, x + 5, y + 5], outline=col + (255,), width=2)
        od.text((x + 6, y - 20), name, font=small, fill=col + (255,))
    x, y = to_px(G.extras()["ejection_port"])
    od.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 120, 120, 255), width=2)
    od.text((x + 6, y + 2), "ejection port", font=small, fill=(255, 120, 120, 255))
    for gy in range(-4, 6):
        x, _ = to_px((0, gy * 0.05, 0))
        od.line([(x, 470), (x, 490)], fill=(230, 230, 230, 255), width=1)
        od.text((x - 14, 455), "%+.2f" % (gy * 0.05), font=small, fill=(230, 230, 230, 255))
    sheet.alpha_composite(over, (0, y0 - 420))
    d.text((8, y0 - 410), "Same camera and scale: P90 TR textured, GoM FAMAS outline red, GoM MP5 outline cyan; "
           "yellow cross = model origin (rear-top of the grip); ticks = game y",
           font=small, fill=(255, 255, 255, 255))
    put("famas_left", 0, y0 + 90, "GoM FAMAS (same scale)", 0.62)
    put("mp5_left", 760, y0 + 90, "GoM MP5 (same scale)", 0.62)

    # Icons at 1x and 4x next to GoM's.
    gom = os.path.join(G_TEX, "item_%s.png")
    x = 1560
    d.text((x, y0 + 80), "icons (ours, then GoM's)", font=small, fill=(255, 255, 255, 255))
    ours = ["P90TR", "57x28Magazine50_P90", "P90_Suppressor", "P90_Muzzle_Mount_Device"]
    theirs = ["MP5", "9x19Magazine30_MP5", "MKI_Suppressor", "Muzzle_Mount_Device"]
    for i, (a, b) in enumerate(zip(ours, theirs)):
        ia = Image.open(os.path.join(MEDIA, "textures/item_GunsOfTienPost93_%s.png" % a)).convert("RGBA")
        ib = Image.open(gom % b).convert("RGBA")
        yy = y0 + 105 + i * 70
        sheet.alpha_composite(ia, (x, yy + 16))
        sheet.alpha_composite(ia.resize((64, 64), Image.NEAREST), (x + 40, yy))
        sheet.alpha_composite(ib.resize((64, 64), Image.NEAREST), (x + 120, yy))
        sheet.alpha_composite(ib, (x + 192, yy + 16))
    sheet = sheet.crop((0, 0, W, y0 + 430))
    os.makedirs(DOCS, exist_ok=True)
    path = os.path.join(DOCS, "post93_p90_preview.png")
    sheet.convert("RGB").save(path)
    print("    wrote", path)


G_TEX = os.path.join(os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600"),
                     "3722134990/mods/GunsOfMarz/42.16/media/textures")


def main():
    quick = "--quick" in sys.argv
    work = tempfile.mkdtemp(prefix="p90_")
    try:
        run([sys.executable, os.path.join(HERE, "p90_decals.py"), work])
        blender("build_p90.py", "--media", MEDIA, "--work", work, *(["--quick"] if quick else []))
        run([sys.executable, os.path.join(HERE, "p90_icons.py"), MEDIA])
        print("verify:")
        write_points(verify())
        if "--no-preview" not in sys.argv:
            prev = os.path.join(work, "prev")
            blender("p90_preview.py", "--media", MEDIA, "--out", prev)
            preview(prev)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
