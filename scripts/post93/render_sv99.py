"""Review renders of the exported SV-99 (the polymer stock's shape in green plywood), read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_sv99.py -- OUT_DIR

Imports what build_sv99.py wrote with SV99.png, the magazine on `magazine`, GoM's PSO-1 / LR10X on `scope`
for the fitted views, the toggle lever at `bolt_lock` / `bolt_fired`, places parts at sv99_points.json the way the engine does (offset,
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
PTS = json.load(open(os.path.join(HERE, "sv99_points.json")))
SCALE = 1.0
K = 0.000603
PX_PER_MM = 1.862
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV99.fbx")
TEXD = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/")
MAG_FBX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV99_magazines.fbx")
MAG_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/22LRMagazine5_SV99.png")


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

    info = {}
    fit = load(GOM + "/models_X/weapons/parts/scopes.fbx",
               {"PSO1_Scope": GOM + "/textures/weapons/parts/scopes/PSO1_Scope.png",
                "LR4X_Scope": GOM + "/textures/weapons/parts/scopes/LR4X_Scope.png"})
    for gun in ("SV99",):
        pts = PTS[gun]
        nodes = [gun + "_" + n for n in ("BODY", "BOLT", "BIPOD_FOLDED", "BIPOD_DEPLOYED")]
        g = load(GUN_FBX, {n: TEXD + gun + ".png" for n in nodes})
        mag = load(MAG_FBX, {"22LRMagazine5_SV99": MAG_TEX})["22LRMagazine5_SV99"]
        for o in g.values():
            place(o)
        place(g[gun + "_BOLT"], pts["bolt_lock"])
        place(mag, pts["magazine"])
        for o in fit.values():
            place(o, pts["scope"])
        body, bolt = g[gun + "_BODY"], g[gun + "_BOLT"]
        fold, dep = g[gun + "_BIPOD_FOLDED"], g[gun + "_BIPOD_DEPLOYED"]
        lo, hi = bounds([body])
        info[gun] = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1)}
        centre = Vector((0.0, (lo.y + hi.y) / 2.0, (lo.z + hi.z) / 2.0))
        span, tall = 1100, 300
        right, left, front = (1, 0, 0), (-1, 0, 0), (0, -1, 0)
        base = [bolt, mag]
        render(gun + "_right", [body, fold] + base, right, span, centre, tall)
        render(gun + "_left", [body, fold] + base, left, span, centre, tall)
        render(gun + "_right_deployed_pso1", [body, dep, fit["PSO1_Scope"]] + base, right, span,
               centre + Vector((0, 0, -0.02)), 400)
        render(gun + "_left_lr4x", [body, fold, fit["LR4X_Scope"]] + base, left, span, centre + Vector((0, 0, 0.01)), 340)
        render(gun + "_q", [body, dep] + base, (0.7, -0.45, -0.5), span, centre + Vector((0, 0, -0.03)), 560)
        render(gun + "_q_back", [body, fold] + base, (-0.7, 0.45, -0.5), span, centre, 560)
        render(gun + "_front", [body, dep] + base, front, 360, centre + Vector((0, 0, -0.03)), 360)
        render(gun + "_lever_closed", [body, fold, bolt, mag], right, 420, Vector((0, 0.03, -0.01)), 220)
        place(bolt, pts["bolt_fired"])
        render(gun + "_lever_open", [body, fold, bolt, mag], right, 420, Vector((0, 0.03, -0.01)), 220)
        for o in list(g.values()) + [mag]:
            o.hide_render = True
            o.name = "done_" + o.name
    print("SIZES", info)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
