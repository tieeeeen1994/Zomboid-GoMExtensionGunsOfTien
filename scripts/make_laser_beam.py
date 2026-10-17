"""The lit laser's beam for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/make_laser_beam.py

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/parts/GunsOfTien_LaserBeam.fbx      node GunsOfTien_LaserBeam
    M/textures/weapons/GunsOfTien/LaserBeam.png            32 x 8 RGBA, red fading to nothing along the beam

A short beam about as long as GoM's laser units (0.055-0.069 game units; user, 2026-10-18: "the same length as the
attachment itself... really short"), drawn by the engine as a weapon part (shared/GunsOfTien/Lasers.lua fits it while
the laser is lit), so it sits exactly on the laser on every gun and moves with every animation. Two crossed quads (one
level, one upright) so it shows from the isometric camera and from the side; origin at the start, along +Y (the
part's forward, as GoM's parts); each laser's model script moves it to that laser's lens (gen_scripts.py, LASER_LENS).
The texture's alpha falls from 1 at the lens to 0 at the tip (basicEffect.frag writes Alpha * texture alpha), its
colour premultiplied by it. The beam models use the unlit shader gunsoftien_laser (scripts/make_laser_shader.py),
so it stays bright at night.
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

LENGTH = 0.065          # game units (GoM's lasers are 0.055-0.069 long)
HALF_WIDTH = 0.002      # game units each side of the axis
TEX_W, TEX_H = 32, 8
COLOUR = (1.0, 0.16, 0.12)


def build():
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    w, l = HALF_WIDTH, LENGTH
    quads = [
        [(-w, 0, 0), (w, 0, 0), (w, l, 0), (-w, l, 0)],      # level
        [(0, 0, -w), (0, 0, w), (0, l, w), (0, l, -w)],      # upright
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
    u = (np.arange(TEX_W) + 0.5) / TEX_W                  # 0 at the lens, 1 at the tip
    alpha = np.clip(1.0 - u, 0.0, 1.0) ** 1.3
    across = 1.0 - np.abs((np.arange(TEX_H) + 0.5) / TEX_H * 2.0 - 1.0) * 0.5   # brighter along the middle
    a = np.outer(across, alpha)                           # rows = v, columns = u
    rgba = np.zeros((TEX_H, TEX_W, 4), np.float32)
    for i in range(3):
        rgba[..., i] = COLOUR[i] * a                      # premultiplied
    rgba[..., 3] = a
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
