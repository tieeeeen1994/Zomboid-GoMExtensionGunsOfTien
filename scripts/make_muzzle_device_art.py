#!/usr/bin/env python3
"""Inventory icons for the real muzzle devices (Python 3 + Pillow).

    python3 scripts/make_muzzle_device_art.py

Writes item_GunsOfTien_<node>.png (main mod) and item_GunsOfTienPost93_<node>.png (Post-93), 32x32 RGBA, from the
FBX and textures scripts/build_muzzle_devices.py exported, with make_mp7_art.py's renderer and the MP7's mount
camera and light (post93/mp7_icon_cameras.json, fitted on GoM's AR mount device icon), as every muzzle part of ours.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_mp7_art as A                   # noqa: E402
import muzzle_devices as MD                # noqa: E402

MEDIA = {"main": os.path.join(A.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media"),
         "post93": os.path.join(A.ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")}
TEX = {"main": "textures/weapons/GunsOfTien", "post93": "textures/weapons/GunsOfTienPost93"}
FBX = {"main": "models_X/weapons/parts/GunsOfTien_muzzle_devices.fbx",
       "post93": "models_X/weapons/parts/GunsOfTienPost93_muzzle_devices.fbx"}


def main():
    fitted = json.load(open(A.CAMERAS_JSON))
    for d in MD.DEVICES:
        mod, node = d["mod"], d["node"]
        icon = A.shade([(A.load_game(os.path.join(MEDIA[mod], FBX[mod]), node), 0)],
                       [A.img(os.path.join(MEDIA[mod], TEX[mod], node + ".png"))],
                       dict(fitted["mount"]["camera"]), fitted["mount"]["light"])
        path = os.path.join(MEDIA[mod], "textures", "item_%s_%s.png" % (MD.MODULES[mod], node))
        icon.save(path)
        print("wrote", os.path.relpath(path, A.ROOT))


if __name__ == "__main__":
    main()
