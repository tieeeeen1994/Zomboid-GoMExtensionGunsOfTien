"""Review renders of the OTs-14 Groza build_groza.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_groza.py -- OUT_DIR

The Groza-4 (short barrel in the forend) with GoM's AS VAL 20, also with its suppressor, the left side at a fixed
scale for the outline check (cameras.json); the long Groza-1 with GoM's 7.62x39 30 and Groza-2 with its AK-74 30 (the
carrier back); the GP-25 body with the 7.62x39 30 (the user's photo: right side); every magazine drawn at 0.603 /
0.645 of GoM's size as its `_GoT` models are; 3/4 views; GoM's AKS-74U and AS VAL at the same scale.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "groza_points.json")))
K = 0.000603
GOT = 0.603 / 0.645
PX = 2.0


def load(path, texture, keep=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    m = bpy.data.materials.new(os.path.basename(texture))
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    objs = {}
    for o in set(bpy.data.objects) - before:
        if o.type != 'MESH' or (keep and o.name.split(".")[0] not in keep):
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name.split(".")[0]] = o
    return objs


def place(o, point=None, scale=1.0):
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = mat @ Matrix.Scale(scale, 4) @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


def render(name, direction, centre, size_mm, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = size_mm * K
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
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
    gun = load(os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_GROZA.fbx"), os.path.join(TEX, "GROZA.png"))
    supp = load(os.path.join(P93, "models_X/weapons/parts/GunsOfTienPost93_GROZA_parts.fbx"),
                os.path.join(TEX, "GROZA_Suppressor.png"))["GROZA_Suppressor"]
    mags = {}
    for n in ("762x39Magazine30", "9x39Magazine20", "545x39Magazine30"):
        mags[n] = load(f"{GOM}/models_X/weapons/magazines/assault_rifles.fbx",
                       f"{GOM}/textures/weapons/magazines/assault_rifles/{n}.png", keep=[n])[n]
    bodies = {k: gun[k] for k in ("GROZA4_BODY", "GROZA_BODY", "GROZAGL_BODY", "GROZA2_BODY")}
    bolt = gun["GROZA_BOLT"]
    L0, H0 = PTS["_extras"]["photo_origin_mm"]
    Lmax, Hmax = 610.0, 257.5
    span, tall = Lmax + 40.0, Hmax + 40.0
    w, h = int(span * PX), int(tall * PX)
    centre = Vector((0.0, (L0 - Lmax / 2.0) * K, (Hmax / 2.0 - H0) * K))

    def state(mag, can=False, fired=False, body="GROZA4_BODY"):
        body = bodies[body]
        place(body)
        place(bolt, PTS["bolt_fired"] if fired else None)
        key = {"762x39Magazine30": "magazine_762x39", "545x39Magazine30": "magazine_545x39"}.get(mag, "magazine")
        place(mags[mag], PTS[key], GOT)
        shown = [body, bolt, mags[mag]]
        if can:
            place(supp, PTS["canon"])
            shown.append(supp)
        show_only(shown)

    wide = centre + Vector((0, 0.05, 0))
    state("762x39Magazine30", body="GROZA_BODY")
    render("GROZA1_left", (-1, 0, 0), wide, span + 160, w + 320, h)
    render("GROZA1_q", (0.7, -0.45, -0.5), wide, span + 160, w + 320, int(h * 1.2))
    state("762x39Magazine30", body="GROZAGL_BODY")
    tall_c = wide + Vector((0, 0, 0.022))      # room for the frame sight standing up (112 mm over its hinge)
    hh = h + int(75 * PX)
    render("GROZAGL_right", (1, 0, 0), tall_c, span + 160, w + 320, hh)
    render("GROZAGL_left", (-1, 0, 0), tall_c, span + 160, w + 320, hh)
    render("GROZAGL_q", (-0.62, -0.5, -0.45), tall_c, span + 160, w + 320, int(hh * 1.2))
    state("9x39Magazine20")
    render("GROZA4_left", (-1, 0, 0), centre, span, w, h)
    state("9x39Magazine20", can=True)
    render("GROZA4_supp_left", (-1, 0, 0), centre + Vector((0, 0.05, 0)), span + 160, w + 320, h)
    render("GROZA4_supp_q", (-0.62, -0.5, -0.45), centre + Vector((0, 0.05, 0)), span + 160, w + 320, int(h * 1.2))
    state("545x39Magazine30", fired=True, body="GROZA2_BODY")
    render("GROZA2_left_fired", (-1, 0, 0), wide, span + 160, w + 320, h)
    render("GROZA2_right_fired", (1, 0, 0), wide, span + 160, w + 320, h)
    render("GROZA2_q", (0.7, -0.5, -0.35), centre, span, w, int(h * 1.2))
    json.dump({"GROZA": {"px_per_mm": PX, "size": [w, h], "photo_centre_mm": [Lmax / 2.0, Hmax / 2.0]}},
              open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    for name in ("AKS74U", "ASVAL"):
        g = load(f"{GOM}/models_X/weapons/firearms/{name}.fbx",
                 f"{GOM}/textures/weapons/firearms/assault_rifles/{name}.png")
        shown = []
        for o in g.values():
            if "DEPLOYED" in o.name:
                continue
            place(o)
            shown.append(o)
        show_only(shown)
        render("gom_" + name, (-1, 0, 0), Vector((0.0, 0.1, -0.01)), 900, 1800, 600)


main()
