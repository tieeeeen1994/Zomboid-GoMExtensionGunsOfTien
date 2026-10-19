#!/usr/bin/env python3
"""Inventory icons of the sawn-off offcuts and their review sheet (Python 3 + Pillow).

    python3 scripts/make_offcut_art.py [--fit]

The offcuts are the pieces build_sawn_stocks.py cuts off GoM's own meshes (GunsOfTien_SawnStocks.fbx), drawn with GoM's
gun textures, so their icons are rendered like GoM's (post93/make_mp7_art.py's renderer): per gun a camera and light
fitted to a GoM icon with the GoM mesh it shows, stored in offcut_icon_cameras.json (--fit, or a missing file, fits them
again; a few minutes):

    barrels_<GUN>  item_<GUN>_Barrel.png   <GUN>_BARREL_CLOSE            -> <GUN>_BARREL_OFFCUTS
    stock_<GUN>    item_<GUN>.png          <GUN>_BODY + _BARREL_CLOSE    -> <GUN>_STOCK_OFFCUT

The camera fits the model into the GoM icon's alpha box, so an offcut fills its icon as GoM's parts do. Writes
media/textures/item_GunsOfTien_<GUN>_BarrelOffcuts.png / _StockOffcut.png and docs/sawn_offcuts_preview.png (GoM's
icon beside ours, enlarged).
"""

import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402  (FBX reader, renderer, camera and light fitting)

ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
ICONS = os.path.join(MEDIA, "textures")
FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SawnStocks.fbx")
CAMERAS_JSON = os.path.join(HERE, "offcut_icon_cameras.json")
PREVIEW = os.path.join(ROOT, "docs/sawn_offcuts_preview.png")
G = A.G
GUNS = ("DOUBLEBARREL", "STEVENS_555", "TOZ34")


def texture(gun):
    return A.img(os.path.join(G, "textures/weapons/firearms/shotguns/%s.png" % gun))


def gom_scene(kind):
    """(GoM icon, objs, textures) the camera and light of `kind` are fitted on."""
    what, gun = kind.split("_", 1)
    fbx = os.path.join(G, "models_X/weapons/firearms/%s.fbx" % gun)
    barrels = (A.load_game(fbx, gun + "_BARREL_CLOSE"), 0)
    if what == "barrels":
        objs, icon = [barrels], "item_%s_Barrel.png" % gun
    else:
        objs, icon = [(A.load_game(fbx, gun + "_BODY"), 0), barrels], "item_%s.png" % gun
    return Image.open(os.path.join(G, "textures", icon)).convert("RGBA"), objs, [texture(gun)]


def our_scenes():
    """{icon name: (kind, objs, textures)}"""
    out = {}
    for gun in GUNS:
        out[gun + "_BarrelOffcuts"] = ("barrels_" + gun, [(A.load_game(FBX, gun + "_BARREL_OFFCUTS"), 0)], [texture(gun)])
        out[gun + "_StockOffcut"] = ("stock_" + gun, [(A.load_game(FBX, gun + "_STOCK_OFFCUT"), 0)], [texture(gun)])
    return out


def fit_all():
    result = {}
    for gun in GUNS:
        for what in ("barrels", "stock"):
            kind = "%s_%s" % (what, gun)
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
    made = {}
    for name, (kind, objs, texes) in our_scenes().items():
        icon = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        icon.save(os.path.join(ICONS, "item_GunsOfTien_%s.png" % name))
        made[name] = (kind, icon)
    return made


def sheet(made, scale=6):
    """Rows per gun: GoM's icon, GoM's mesh rendered with the fitted camera (the fit check), our icon; at 1x and xN."""
    fitted = json.load(open(CAMERAS_JSON))
    cell = 32 * scale + 56          # the icon at 1x, then enlarged
    rows = list(made.items())
    page = Image.new("RGBA", (3 * cell + 220, len(rows) * (32 * scale + 18) + 30), (58, 58, 58, 255))
    d = ImageDraw.Draw(page)
    for i, label in enumerate(("GoM icon", "GoM mesh, fitted camera", "ours")):
        d.text((220 + i * cell, 8), label, fill=(230, 230, 230, 255))
    for r, (name, (kind, icon)) in enumerate(rows):
        y = 30 + r * (32 * scale + 18)
        gom_icon, objs, texes = gom_scene(kind)
        check = A.shade(objs, texes, dict(fitted[kind]["camera"]), fitted[kind]["light"])
        d.text((8, y + 16 * scale - 6), name, fill=(230, 230, 230, 255))
        for i, im in enumerate((gom_icon, check, icon)):
            x = 220 + i * cell
            page.alpha_composite(im, (x, y))
            page.alpha_composite(im.resize((32 * scale, 32 * scale), Image.NEAREST), (x + 40, y))
    page.save(PREVIEW)


def main():
    if "--fit" in sys.argv or not os.path.exists(CAMERAS_JSON):
        fit_all()
    made = make_icons()
    sheet(made)
    print("wrote", len(made), "icons and", PREVIEW)


if __name__ == "__main__":
    main()
