"""Review renders of the exported SV-98, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_sv98.py -- OUT_DIR

Imports what build_sv98.py wrote with SV98.png, its magazine on `magazine`, GoM's Picatinny Rail (Up) and PSO-1 /
LR10X on `rail_up` / `scope` for the fitted views, places parts at sv98_points.json the way the engine does (offset,
then rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR at PX_PER_MM real.
Game space is Blender world space, the mirror image of what the game shows: the camera at +X shows the gun's left.
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
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "sv98_points.json")))
SCALE = 1.0
K = 0.000603
PX_PER_MM = 1.566
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV98.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/SV98.png")
MAG_FBX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV98_magazines.fbx")
MAG_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/762x54Magazine10_SV98.png")


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


def render(name, objs, direction, span_mm, centre, tall_mm):
    show_only(objs)
    span, tall = span_mm * K, tall_mm * K
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = centre - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = max(span, tall)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = int(span_mm * PX_PER_MM), int(tall_mm * PX_PER_MM)
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
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    g = load(GUN_FBX, {n: TEX for n in ("SV98_BODY", "SV98_BOLT", "SV98_BIPOD_FOLDED", "SV98_BIPOD_DEPLOYED")})
    mag = load(MAG_FBX, {"762x54Magazine10_SV98": MAG_TEX})["762x54Magazine10_SV98"]
    fit = load(GOM + "/models_X/weapons/parts/rails.fbx",
               {"Picatinny_Rail_Up": GOM + "/textures/weapons/parts/rails/Picatinny_Rail.png"})
    fit.update(load(GOM + "/models_X/weapons/parts/scopes.fbx",
                    {"PSO1_Scope": GOM + "/textures/weapons/parts/scopes/PSO1_Scope.png",
                     "LR10X_Scope": GOM + "/textures/weapons/parts/scopes/LR10X_Scope.png"}))
    for o in g.values():
        place(o)
    place(mag, PTS["magazine"])
    fit.pop("Picatinny_Rail_Up", None)
    for n, o in fit.items():
        place(o, PTS["scope"])
    body, bolt = g["SV98_BODY"], g["SV98_BOLT"]
    fold, dep = g["SV98_BIPOD_FOLDED"], g["SV98_BIPOD_DEPLOYED"]
    lo, hi = bounds([body])
    info = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1)}
    print("SIZES", info)
    centre = Vector((0.0, (lo.y + hi.y) / 2.0, (lo.z + hi.z) / 2.0))
    span, tall = 1260, 320
    right, left, front = (1, 0, 0), (-1, 0, 0), (0, -1, 0)
    q = (0.7, -0.45, -0.5)
    base = [bolt, mag]
    rail = []
    render("SV98_right", [body, fold] + base + rail, right, span, centre, tall)
    render("SV98_left", [body, fold] + base + rail, left, span, centre, tall)
    render("SV98_right_deployed_pso1", [body, dep, fit.get("PSO1_Scope")] + base + rail, right, span,
           centre + Vector((0, 0, -0.02)), 420)
    render("SV98_left_deployed_lr10x", [body, dep, fit.get("LR10X_Scope")] + base + rail, left, span,
           centre + Vector((0, 0, -0.02)), 420)
    render("SV98_q", [body, dep] + base + rail, q, span, centre + Vector((0, 0, -0.03)), 600)
    render("SV98_q_back", [body, fold] + base + rail, (-0.7, 0.45, -0.5), span, centre, 600)
    render("SV98_front", [body, dep] + base + rail, front, 400, centre + Vector((0, 0, -0.03)), 400)
    render("SV98_bolt_open", [body, fold, mag] + rail, right, 500, Vector((0, 0.03, 0.0)), 220)
    place(bolt, PTS["bolt_fired"])
    render("SV98_bolt_back", [body, fold, bolt, mag] + rail, right, 500, Vector((0, 0.03, 0.0)), 220)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
