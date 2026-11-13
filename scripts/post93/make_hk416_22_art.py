"""Textures of the HK416 .22 pistols (plain Python with Pillow; build_hk416_22.py draws on them).

    py scripts/post93/make_hk416_22_art.py

- textures/weapons/GunsOfTienPost93/HK416ML22.png (512): GoM's AR15 texture (256) in the top-left quarter, the
  same in HK bronze in the top-right (each texel's brightness against the texture's mean carried onto the bronze),
  copies of both below (padding, unused). The ML22 body's receivers, flat top and handguard use the right half.
- textures/weapons/GunsOfTienPost93/HK416_22_MAG.png (32): H&K's charcoal-grey polymer (left half) and black
  (right half: the feed slot, the screws).
- textures/item_GunsOfTienPost93_HK416QR22.png and the three magazines' icons (32x32 RGBA, make_mp7_art.py's
  renderer, after the textures): the pistol on the camera and light fitted on GoM's MP5 icon (mp7_icon_cameras.json
  "gun", as the Vector SDP: its turned nodes turned back upright, bare, sights up, the 20-round magazine), the
  magazines on the SCARs' rifle magazine camera (fitted on GoM's FAL magazine) with the MP7 magazine light, as the
  SCAR-H's and the PMAGs' (GoM's FAL light washes light-coloured magazines out).
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TEX = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
# the M-LOK pistol is shelved (build_hk416_22.py GENS): its bronze texture is made only when this is True
ML22 = False
BRONZE = (150, 116, 82)       # HK bronze at the texture's mean brightness (read off the H&K USA photos in shade)


def bronze_of(img):
    px = img.load()
    w, h = img.size
    lum = [[0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2] for x in range(w)] for y in range(h)]
    mean = sum(map(sum, lum)) / (w * h)
    out = Image.new("RGB", (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            k = max(0.35, min(1.7, lum[y][x] / mean))
            po[x, y] = tuple(min(255, int(c * k)) for c in BRONZE)
    return out


def main():
    os.makedirs(TEX, exist_ok=True)
    if ML22:
        ar = Image.open(f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png").convert("RGB")
        w, h = ar.size
        br = bronze_of(ar)
        out = Image.new("RGB", (2 * w, 2 * h))
        for y0 in (0, h):
            out.paste(ar, (0, y0))
            out.paste(br, (w, y0))
        out.save(os.path.join(TEX, "HK416ML22.png"))
    mag = Image.new("RGB", (32, 32))
    pm = mag.load()
    for y in range(32):
        for x in range(32):
            n = ((x * 7 + y * 13) % 5) - 2
            pm[x, y] = (74 + n, 74 + n, 77 + n) if x < 16 else (22, 22, 23)
    mag.save(os.path.join(TEX, "HK416_22_MAG.png"))
    print("wrote", "HK416ML22.png," if ML22 else "", "HK416_22_MAG.png in", TEX)


UPRIGHT = {"offset": [0.0, 0.0, 0.0], "rotate": [-180.0, 0.0, -180.0]}     # undoes the pistol hold's turn


def icons():
    sys.dont_write_bytecode = True
    import make_mp7_art as A
    media = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
    fbx_gun = os.path.join(media, "models_X/weapons/firearms/GunsOfTienPost93_HK416QR22.fbx")
    fbx_mags = os.path.join(media, "models_X/weapons/magazines/GunsOfTienPost93_HK416_22_magazines.fbx")
    pts = json.load(open(os.path.join(HERE, "hk416_22_points.json")))["HK416QR22"]
    x, y, z = pts["magazine"]["offset"]
    mag_up = {"offset": [-x + 0.0, y, -z + 0.0], "rotate": [0.0, 0.0, 0.0]}     # the turned point, upright
    gun_tex = A.img(f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png")
    mark_tex = A.img(os.path.join(TEX, "HK416_MARKINGS.png"))
    mag_tex = A.img(os.path.join(TEX, "HK416_22_MAG.png"))
    mp7 = json.load(open(A.CAMERAS_JSON))
    scar = json.load(open(os.path.join(HERE, "scar_icon_cameras.json")))
    objs = [(A.attach(A.load_game(fbx_gun, n), UPRIGHT), 0)
            for n in ("HK416QR22_BODY", "HK416QR22_BOLT", "HK416QR22_CHARGING_HANDLE")]
    objs.append((A.attach(A.load_game(fbx_gun, "HK416QR22_MARKINGS"), UPRIGHT), 1))
    objs.append((A.attach(A.load_game(fbx_mags, "22LRMagazine20_HK416"), mag_up), 2))
    out = {"HK416QR22": A.shade(objs, [gun_tex, mark_tex, mag_tex], dict(mp7["gun"]["camera"]), mp7["gun"]["light"])}
    for n in (10, 20, 30):
        name = "22LRMagazine%d_HK416" % n
        out[name] = A.shade([(A.load_game(fbx_mags, name), 0)], [mag_tex], dict(scar["rifle_magazine"]["camera"]),
                            mp7["magazine"]["light"])
    for name, icon in out.items():
        icon.save(os.path.join(media, "textures", "item_GunsOfTienPost93_%s.png" % name))
    print("wrote the icons:", ", ".join(out))


if __name__ == "__main__":
    main()
    icons()
