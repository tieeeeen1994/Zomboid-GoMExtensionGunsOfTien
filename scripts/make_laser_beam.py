"""The lit laser's beam for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/make_laser_beam.py

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/parts/GunsOfTien_LaserBeam.fbx      node GunsOfTien_LaserBeam
    M/textures/weapons/GunsOfTien/LaserBeam.png            32 x 8, solid red

A short beam about as long as GoM's laser units (0.055-0.069 game units; user, 2026-10-18: "the same length as the
attachment itself... really short"), drawn by the engine as a weapon part (shared/GunsOfTien/Lasers.lua fits it while
the laser is lit), so it sits exactly on the laser on every gun and moves with every animation. Two crossed quads (one
level, one upright) so it shows from the isometric camera and from the side; origin at the start, along +Y (the
part's forward, as GoM's parts); each laser's model script moves it to that laser's lens (gen_scripts.py, LASER_LENS).
The engine draws weapon parts opaque: texture alpha is not blended, only cut away below 0.01 (user's screenshots,
2026-10-18: a colour darkened along the fade showed as a black tail, visible on a lit floor, gone on a dark one), and a
screen-door fade (pixels dropped against noise) looked dotted at game size. So the beam is solid plain red and only
narrows to a point at the tip (TIP_WIDTH), which reads as fading out and looks the same on a lit floor and in the dark
(user chose this, option B of three previews, 2026-10-18). Its shader is unlit (scripts/make_laser_shader.py,
gunsoftien_laser), so it stays bright at night.
FBX conventions as build_mp7.py: data = (game x, game y, -game z), rotation (90, 0, 0), scale 0.01, its export and
deterministic rewrite.
"""

import os
import sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.normpath(os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media"))
FBX = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_LaserBeam.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/LaserBeam.png")

LENGTH = 0.26           # game units (~0.4 tiles): about a compact SMG's length (user, 2026-10-18: "make the laser longer"; first 0.065, a laser unit's length)
HALF_WIDTH = 0.002      # game units each side of the axis, at the lens
TIP_WIDTH = 0.0         # the half width at the tip, as a fraction of HALF_WIDTH (0 = a point)
TEX_W, TEX_H = 32, 8
COLOUR = (1.0, 0.16, 0.12)


def build():
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    w, t, l = HALF_WIDTH, HALF_WIDTH * TIP_WIDTH, LENGTH
    quads = [
        [(-w, 0, 0), (w, 0, 0), (t, l, 0), (-t, l, 0)],      # level, narrowing to the tip
        [(0, 0, -w), (0, 0, w), (0, l, t), (0, l, -t)],      # upright
    ]
    for quad in quads:
        verts = [bm.verts.new((x, y, -z)) for x, y, z in quad]   # FBX data z = -game z
        face = bm.faces.new(verts)
        for loop, (u, v) in zip(face.loops, [(0.02, 0.0), (0.02, 1.0), (0.98, 1.0), (0.98, 0.0)]):
            loop[uv].uv = (u, v)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    me = bpy.data.meshes.new("GunsOfTien_LaserBeam")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("GunsOfTien_LaserBeam", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def texture():
    rgba = np.ones((TEX_H, TEX_W, 4), np.float32)          # opaque throughout: the taper is the fade
    for i in range(3):
        rgba[..., i] = COLOUR[i]
    img = bpy.data.images.new("LaserBeam", TEX_W, TEX_H, alpha=True)
    img.colorspace_settings.name = 'sRGB'
    img.pixels.foreach_set(rgba.ravel())
    os.makedirs(os.path.dirname(TEX), exist_ok=True)
    img.filepath_raw = TEX
    img.file_format = 'PNG'
    img.save()


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ob = build()
    texture()
    kit.export([ob], FBX)
    print("wrote", FBX, "and", TEX)


main()
