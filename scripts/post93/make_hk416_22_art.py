"""Textures of the HK416 .22 pistols (plain Python with Pillow; build_hk416_22.py draws on them).

    py scripts/post93/make_hk416_22_art.py

- textures/weapons/GunsOfTienPost93/HK416ML22.png (512): GoM's AR15 texture (256) in the top-left quarter, the
  same in HK bronze in the top-right (each texel's brightness against the texture's mean carried onto the bronze),
  copies of both below (padding, unused). The ML22 body's receivers, flat top and handguard use the right half.
- textures/weapons/GunsOfTienPost93/HK416_22_MAG.png (32): H&K's charcoal-grey polymer (left half) and black
  (right half: the feed slot, the screws).
Icons come later, with the items.
"""
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
    print("wrote HK416ML22.png, HK416_22_MAG.png in", TEX)


if __name__ == "__main__":
    main()
