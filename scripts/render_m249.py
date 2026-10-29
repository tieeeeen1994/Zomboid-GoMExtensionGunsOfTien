"""Review renders of the exported M249 assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_m249.py -- OUT_DIR

Imports what build_m249.py wrote, places every part at m249_points.json the way the engine does (offset, then
rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the right side at the
reference photo's scale (make_m249_art.py lays the traced outline over it), the left side, 3/4 views with the box and
belt, with a GoM STANAG magazine, with the feed cover open, the bipod folded and deployed, the box alone, and GoM's M60
at the same scale. Game space is used as Blender world space, the mirror image of what the game shows; make_m249_art.py
flips every render left-right.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "m249_points.json")))
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)


# load / place / render: render_scar.py's (importing it would run its main())
def load(path, texture, keep=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    img = bpy.data.images.load(texture, check_existing=True)
    m = bpy.data.materials.new(os.path.basename(texture))
    nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = 'Closest'
    nt.links.new(t.outputs[0], nt.nodes["Principled BSDF"].inputs[0])
    objs = {}
    for o in set(bpy.data.objects) - before:
        if keep and o.name != keep:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name] = o
    return objs


def place(o, point=None):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


def render(name, direction, centre, scale, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.ortho_scale = scale
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


class R:
    load, render = staticmethod(load), staticmethod(render)


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

    gun = R.load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_M249.fbx"), os.path.join(TEX, "M249.png"))
    box = R.load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_M249_box.fbx"),
                 os.path.join(TEX, "556x45Box200_M249.png"))
    belt = [box["556x45_M249_%d" % i] for i in range(1, 10)]
    stanag = None
    if GOM:
        stanag = R.load(os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx"),
                        os.path.join(GOM, "textures/weapons/magazines/assault_rifles/556x45Magazine30_STANAG.png"),
                        keep="556x45Magazine30_STANAG").get("556x45Magazine30_STANAG")

    def state(feed="box", cover_open=False, deployed=False, rounds=9):
        objs = [gun["M249_BODY"], gun["M249_COVER"], gun["M249_BOLT"], gun["M249_HANDLE"]]
        place(gun["M249_BOLT"])
        place(gun["M249_HANDLE"])
        place(gun["M249_BODY"])
        place(gun["M249_COVER"], PTS["cover_open" if cover_open else "cover"])
        bip = gun["M249_BIPOD_DEPLOYED" if deployed else "M249_BIPOD_FOLDED"]
        place(bip, PTS["integrated_bipod"])
        objs.append(bip)
        if feed == "box":
            place(box["556x45Box200_M249"], PTS["box"])
            objs.append(box["556x45Box200_M249"])
            for o in belt[:rounds]:
                place(o, PTS["belt"])
                objs.append(o)
        elif feed == "stanag" and stanag is not None:
            place(stanag, PTS["magazine"])
            objs.append(stanag)
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.hide_render = o not in objs

    k = PTS["_extras"]["k"]
    length = 1100.0
    lmid = 0.12
    centre = Vector((0.0, lmid, 0.0))
    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    w = 1600
    cams = {}
    state(feed="none")
    R.render("M249_right", right, centre, length * k, w, 700)
    cams["M249_right"] = {"centre_game": [0.0, lmid, 0.0], "px_per_mm": w / length, "size": [w, 700],
                          "photo_origin_mm": PTS["_extras"]["photo_origin_mm"], "k": k}
    state()
    R.render("M249_left_box", left, centre, length * k, w, 700)
    R.render("M249_q_left_box", q_left, centre, length * k, w, 900)
    R.render("M249_q_right_box", q_right, centre, length * k, w, 900)
    R.render("M249_front_box", (0, -1, 0), Vector((0.0, 0.0, 0.0)), 0.3, 800, 800)
    R.render("M249_top_box", (0, 0, -1), centre, length * k, w, 400)
    state(feed="stanag")
    R.render("M249_left_stanag", left, centre, length * k, w, 700)
    R.render("M249_front_stanag", (0, -1, 0), Vector((0.0, 0.0, 0.0)), 0.3, 800, 800)
    state(cover_open=True)
    R.render("M249_q_left_open", q_left, centre + Vector((0, 0, 0.05)), length * k, w, 1000)
    state(deployed=True)
    R.render("M249_left_deployed", left, centre + Vector((0, 0, -0.04)), length * k, w, 800)
    R.render("M249_front_deployed", (0, -1, 0), Vector((0.0, 0.0, -0.03)), 0.3, 800, 800)
    state(rounds=4)
    R.render("M249_belt4", q_left, Vector((0.0, 0.11, 0.0)), 0.25, 900, 800)
    if GOM:
        objs = R.load(os.path.join(GOM, "models_X/weapons/firearms/M60.fbx"),
                      os.path.join(GOM, "textures/weapons/firearms/lmgs/M60.png"))
        m60box = R.load(os.path.join(GOM, "models_X/weapons/magazines/lmgs.fbx"),
                        os.path.join(GOM, "textures/weapons/magazines/lmgs/762x51Box100_M60.png"))
        shown = [objs["M60_BODY"], objs["M60_BOLT"], objs["M60_BIPOD_FOLDED"], m60box["762x51Box100_M60"]]
        shown += [m60box["762x51_M60_%d" % i] for i in range(1, 10)]
        for o in shown:
            place(o)
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.hide_render = o not in shown
        R.render("gom_M60_left", left, Vector((0.0, 0.17, 0.0)), length * k, w, 700)
        R.render("gom_M60_q_left", q_left, Vector((0.0, 0.17, 0.0)), length * k, w, 900)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
