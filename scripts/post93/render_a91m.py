"""Review renders of the exported A-91M, read back from the FBX file (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_a91m.py -- OUT_DIR

Imports what build_a91m.py wrote with A91M.png; the A-91M with GoM's AK-47 30 (at our size, as the Grozas draw it);
GoM's rail on our handle clamp and GoM's LR4X on `scope` for the fitted views; places
parts at a91m_points.json the way the engine does (offset, then rotateXYZ in degrees) and renders orthographic
Workbench views into OUT_DIR. `<gun>_photo` is the left side at its measuring photo's px a mm, for the overlay
check (make_a91m_art.py overlay). Game space is used as Blender world space, which is its mirror image (game space is
left-handed, CLAUDE.md "Handedness of the review renders"), so the camera is mirrored (scale x -1): every view is the
gun as the game shows it, the left side (+X, the measuring photo's) with its muzzle on the left.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
GOM = "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media"
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "a91m_points.json")))
K = 0.000603
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_A91M.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/A91M.png")
GOM_SCALE = 0.603 / 0.645
PHOTO_PX = {"A91M": 1.294}


def material(texture):
    m = bpy.data.materials.get(texture)
    if m:
        return m
    m = bpy.data.materials.new(texture)
    nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    nt.links.new(t.outputs[0], nt.nodes["Principled BSDF"].inputs[0])
    return m


def load(path, textures, scale=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    objs = {}
    for o in set(bpy.data.objects) - before:
        name = o.name.split(".")[0]
        if name not in textures:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(material(textures[name]))
        if scale != 1.0:
            o.data.transform(Matrix.Scale(scale, 4))
        objs[name] = o
    return objs


def place(o, point=None):
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


def bounds(objs):
    bpy.context.view_layer.update()
    vs = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])


def render(name, objs, direction, span_mm, centre, tall_mm, px_per_mm=2.0):
    show_only(objs)
    span, tall = span_mm * K, tall_mm * K
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = centre - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = max(span, tall)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = int(span_mm * px_per_mm), int(tall_mm * px_per_mm)
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_cavity = False
    sc.display.shading.show_specular_highlight = False
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.exposure = 1.0
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    cam.scale = (-1.0, 1.0, 1.0)                # the mirror: see the module docstring
    sc.collection.objects.link(cam)
    sc.camera = cam

    nodes = [g + s for g in ("A91M",) for s in ("_BODY", "_BOLT", "_RAIL_UP")]
    info = {}
    for gun in ("A91M",):
        pts = PTS[gun]
        g = load(GUN_FBX, {n: TEX for n in nodes})
        mag = load(GOM + "/models_X/weapons/magazines/assault_rifles.fbx",
                   {"762x39Magazine30": GOM + "/textures/weapons/magazines/assault_rifles/762x39Magazine30.png"},
                   GOM_SCALE)["762x39Magazine30"]
        scope = load(GOM + "/models_X/weapons/parts/scopes.fbx",
                     {"LR4X_Scope": GOM + "/textures/weapons/parts/scopes/LR4X_Scope.png"})["LR4X_Scope"]
        for o in g.values():
            place(o)
        place(mag, pts["magazine"])
        place(scope, pts["scope"])
        body, bolt, rail = g[gun + "_BODY"], g[gun + "_BOLT"], g[gun + "_RAIL_UP"]
        lo, hi = bounds([body])
        info[gun] = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1)}
        lo2, hi2 = bounds([body, mag])
        info[gun]["height_with_mag_mm"] = round((hi2.z - lo2.z) / K, 1)
        centre = Vector((0.0, (lo2.y + hi2.y) / 2.0, (lo2.z + hi2.z) / 2.0))
        span = (hi2.y - lo2.y) / K + 40
        tall = (hi2.z - lo2.z) / K + 60
        right, left = (1, 0, 0), (-1, 0, 0)         # looking along: from the gun's right, from its left
        base = [body, bolt, mag]
        # the bare body at its measuring photo's scale, framed on the body alone, for the overlay
        cb = Vector((0.0, (lo2.y + hi2.y) / 2.0, (lo2.z + hi2.z) / 2.0))
        render(gun + "_photo", [body, bolt, mag], left, (hi2.y - lo2.y) / K, cb, (hi2.z - lo2.z) / K, PHOTO_PX[gun])
        info[gun]["photo_frame_mm"] = [round(lo2.y / K, 3), round(hi2.y / K, 3), round(lo2.z / K, 3),
                                       round(hi2.z / K, 3)]
        render(gun + "_right", base, right, span, centre, tall)
        render(gun + "_left", base, left, span, centre, tall)
        render(gun + "_left_optic", base + [rail, scope], left, span, centre, tall + 140)
        render(gun + "_q", base, (-0.7, -0.45, -0.5), span, centre, tall + 150)             # left, from the front
        render(gun + "_q_optic", base + [rail, scope], (0.7, -0.45, -0.5), span, centre, tall + 150)
        render(gun + "_q_back", base, (-0.7, 0.55, -0.45), span, centre, tall + 150)        # left, from behind
        render(gun + "_q_right", base, (0.7, -0.5, -0.45), span, centre, tall + 150)
        render(gun + "_q_right_back", base, (0.7, 0.55, -0.45), span, centre, tall + 150)
        render(gun + "_q_low", base, (-0.6, -0.6, 0.35), span, centre, tall + 150)
        render(gun + "_top", base + [rail, scope], (0, 0, -1), 140, centre, span)
        render(gun + "_front", base, (0, -1, 0), 220, centre, tall)
        place(bolt, pts["bolt_fired"])
        render(gun + "_bolt_back", base, left, span, centre, tall)
        for o in list(g.values()) + [mag, scope]:
            bpy.data.objects.remove(o)
    print("SIZES", info)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
