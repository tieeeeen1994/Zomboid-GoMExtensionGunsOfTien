#!/usr/bin/env python3
"""Inventory icons for AWC's Mk9 suppressor and the 9x19mm SMG mount device (Python 3 + Pillow).

    python3 scripts/make_mk9_art.py

Writes Contents/mods/GoMExtensionGunsOfTien/42/media/textures/item_GunsOfTien_<node>.png (32x32 RGBA) from the FBX and
textures build_mk9.py exported, with make_mp7_art.py's renderer and the MP7's suppressor and mount cameras and lights
(post93/mp7_icon_cameras.json, fitted on GoM's MKI suppressor and AR mount device icons), as every can of ours.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402

MEDIA = os.path.join(A.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
ICONS = os.path.join(MEDIA, "textures")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")


def main():
    fitted = json.load(open(A.CAMERAS_JSON))
    for node, kind in (("Mk9_Suppressor", "suppressor"), ("SMG9_Muzzle_Mount_Device", "mount")):
        icon = A.shade([(A.load_game(FBX_PARTS, node), 0)], [A.img(os.path.join(TEX, node + ".png"))],
                       dict(fitted[kind]["camera"]), fitted[kind]["light"])
        path = os.path.join(ICONS, "item_GunsOfTien_%s.png" % node)
        icon.save(path)
        print("wrote", os.path.relpath(path, A.ROOT))


if __name__ == "__main__":
    main()
