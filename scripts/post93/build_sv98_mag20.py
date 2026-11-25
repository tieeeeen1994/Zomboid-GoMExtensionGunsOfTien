"""A 20-round 7.62x54R magazine of the SV-98's pattern, for Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_sv98_mag20.py

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/magazines/GunsOfTienPost93_SV98_magazine20.fbx   762x54Magazine20_SV98
    M/textures/weapons/GunsOfTienPost93/762x54Magazine20_SV98.png       128

User, 2026-11-25: "introduce a 20-round mag which is also compatible with SV-98", for the A-91M Prototype (7.62x54R,
build_a91m_proto.py), whose 10 rounds were thin for automatic fire. An invented magazine: build_sv98.py's 10-round
box with 55 mm more body (ten more rimmed rounds in two columns, about 11 mm a pair), the same origin at the feed
lips' front, so it seats in the SV-98's well as its own does and hangs 55 mm lower. Its own file, so the SV-98's
meshes and textures are not rebuilt.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sv98 as base  # noqa: E402

kit = base.kit
NAME = "762x54Magazine20_SV98"
EXTRA = 55.0                       # mm of body under the 10-round one's
FBX = os.path.join(kit.MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV98_magazine20.fbx")


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.seed = 0
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 0
    scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0, 0, 0)
    mag = base.build_magazine(EXTRA, NAME)
    kit.unwrap([mag], 0.012)
    base.texture([mag], [[mag]], ["mag"], 128, os.path.join(base.TEX_DIR, NAME + ".png"))
    bd = kit.bounds_of(mag)
    kit.export([mag], FBX)
    print("%-24s tris %4d  min %s  max %s" % (NAME, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
