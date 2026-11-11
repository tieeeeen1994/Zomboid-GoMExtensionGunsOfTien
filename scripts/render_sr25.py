"""Review renders of the SR-25 build_sr25.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_sr25.py -- OUT_DIR

The SR-25 with KAC's 20 and with Post-93's PMAG 20 (the SR-25 pattern, which fits it too), its left and right sides,
3/4 views, the integrated bipod folded and deployed, the integrated scope close up, the bolt fired and the charging
handle back, and GoM's AR15 and M14 at the same scale (game units).
Game space is Blender world space, the mirror image of what the game shows.
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
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "sr25_points.json")))
GUN_TEX = f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png"
MAG_TEX = f"{GOM}/textures/weapons/magazines/assault_rifles/556x45Magazine20_STANAG.png"


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


def render(name, direction, centre, size, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.ortho_scale = size
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
    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SR25.fbx"), GUN_TEX)
    kac = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx"), MAG_TEX)
    kac = kac["762x51Magazine20_SR25"]
    pmag = load(os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx"),
                os.path.join(P93, "textures/weapons/GunsOfTienPost93/762x51Magazine20_PMAG.png"),
                keep=["762x51Magazine20_PMAG"])["762x51Magazine20_PMAG"]
    body, bolt, handle = gun["SR25_BODY"], gun["SR25_BOLT"], gun["SR25_CHARGING_HANDLE"]
    W, H, SIZE = 1800, 700, 0.75
    centre = Vector((0.0, 0.16, -0.01))
    left, right = (-1, 0, 0), (1, 0, 0)

    folded, deployed = gun["SR25_BIPOD_FOLDED"], gun["SR25_BIPOD_DEPLOYED"]

    def state(mag=kac, fired=False, racked=False, legs=False):
        place(body)
        place(bolt, PTS["bolt_fired"] if fired else None)
        place(handle, PTS["charging_handle_open"] if racked else None)
        place(mag, PTS["magazine"])
        bip = deployed if legs else folded
        place(bip)
        show_only([body, bolt, handle, mag, bip])

    state()
    render("SR25_left", left, centre, SIZE, W, H)
    render("SR25_right", right, centre, SIZE, W, H)
    render("SR25_q_left", (-0.62, -0.5, -0.45), centre, SIZE, W, int(H * 1.3))
    render("SR25_q_right", (0.7, -0.45, -0.5), centre, SIZE, W, int(H * 1.3))
    render("SR25_top", (0, 0, -1), centre, SIZE, W, 300)
    state(legs=True)
    render("SR25_deployed_left", left, centre + Vector((0, 0, -0.03)), SIZE, W, int(H * 1.25))
    render("SR25_deployed_front", (0, -1, 0), Vector((0.0, 0.0, 0.0)), 0.35, 700, 700)
    state()
    render("SR25_scope_q", (-0.6, -0.55, -0.35), Vector((0.0, 0.08, 0.05)), 0.32, 1200, 800)
    state(fired=True, racked=True)
    render("SR25_racked_right", right, Vector((0.0, 0.05, 0.0)), 0.3, 1200, 700)
    state(mag=pmag)
    render("SR25_pmag_left", left, Vector((0.0, 0.08, -0.02)), 0.3, 1200, 700)
    state()
    render("SR25_kac_left", left, Vector((0.0, 0.08, -0.02)), 0.3, 1200, 700)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    for name, tex in (("AR15", "assault_rifles/AR15"), ("M14", "battle_rifles/M14")):
        g = load(f"{GOM}/models_X/weapons/firearms/{name}.fbx", f"{GOM}/textures/weapons/firearms/{tex}.png")
        for o in g.values():
            place(o)
        show_only(list(g.values()))
        render("gom_" + name, left, centre, SIZE, W, H)


main()
