"""Review renders of the HK416 build_hk416.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_hk416.py -- OUT_DIR

The bare gun from both sides and 3/4, its rail system and sights up close, the stock collapsed, and fitted the way
the game draws parts at the gun's points (approximation: the part models' own points are not applied, as
render_mk11.py), each optic on the body ConditionalModel gives it (sights up, rear folded for a red dot, both folded
for a magnified scope): GoM's Aimpoint, LR4X, foregrip, light, laser, AR mount device + MKI and STANAG 30; GoM's M4A1 at the
same scale. Game space is Blender's, the mirror image of what the game shows.
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
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "hk416_points.json")))
AR_TEX = f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png"


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
        n = o.name.split(".")[0]
        if o.type != 'MESH' or (keep and n not in keep):
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        o.name = n + "_" + os.path.basename(path)[:12]
        objs[n] = o
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
    gun = load(os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK416.fbx"), AR_TEX)
    bodies = {k: gun["HK416_" + k] for k in ("BODY", "BODY_RD", "BODY_FD")}
    bolt, handle, stock = (gun["HK416_" + n] for n in ("BOLT", "CHARGING_HANDLE", "STOCK"))
    marks = load(os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK416.fbx"),
                 os.path.join(P93, "textures/weapons/GunsOfTienPost93/HK416_MARKINGS.png"),
                 keep=["HK416_MARKINGS"])["HK416_MARKINGS"]
    red_dots = ("EXPS1_Sight", "EXPS3_Sight", "Aimpoint_Sight", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight",
                "Kobra_Sight")
    parts = {}
    for cat, name, tex in (("magazines/assault_rifles", "556x45Magazine30_STANAG", "magazines/assault_rifles"),
                           ("parts/muzzles", "Muzzle_Mount_Device", "parts/muzzles"),
                           ("parts/suppressors", "MKI_Suppressor", "parts/suppressors"),
                           ("parts/scopes", "Aimpoint_Sight", "parts/scopes"),
                           ("parts/scopes", "EXPS3_Sight", "parts/scopes"),
                           ("parts/scopes", "LR4X_Scope", "parts/scopes"),
                           ("parts/scopes", "ElcanX2_Scope", "parts/scopes"),
                           ("parts/foregrips", "MKC_Foregrip", "parts/foregrips"),
                           ("parts/pointers", "SR7_Light", "parts/pointers"),
                           ("parts/pointers", "AimRight_Laser", "parts/pointers"),
                           ("parts/bipods", "Bipod_Deployed", "parts/bipods")):
        try:
            parts[name] = load(f"{GOM}/models_X/weapons/{cat}.fbx", f"{GOM}/textures/weapons/{tex}/{name}.png",
                               keep=[name])[name]
        except Exception as e:                                   # noqa: BLE001
            print("skip", name, e)
    mag = parts["556x45Magazine30_STANAG"]

    def state(extra=(), can=False, fired=False, racked=False, folded=False):
        optic = [n for n, pt in extra if pt == "scope"]
        body = bodies["BODY" if not optic else ("BODY_RD" if optic[0] in red_dots else "BODY_FD")]
        place(body)
        place(bolt, PTS["bolt_fired"] if fired else None)
        place(handle, PTS["charging_handle_open"] if racked else None)
        place(stock, PTS["stock_folded"] if folded else PTS["stock"])
        place(mag, PTS["magazine"])
        place(marks)
        shown = [body, bolt, handle, stock, mag, marks]
        for name, point in extra:
            if name in parts:
                place(parts[name], PTS[point])
                shown.append(parts[name])
        if can:
            for n in ("Muzzle_Mount_Device", "MKI_Suppressor"):
                place(parts[n], PTS["canon"])
                shown.append(parts[n])
        show_only(shown)

    W, H, SIZE = 2000, 800, 0.62
    centre = Vector((0.0, 0.105, 0.0))
    left, right = (-1, 0, 0), (1, 0, 0)
    state()
    render("HK416_left", left, centre, SIZE, W, H)
    render("HK416_right", right, centre, SIZE, W, H)
    render("HK416_q", (-0.62, -0.5, -0.45), centre, SIZE, W, int(H * 1.3))
    render("HK416_front_q", (0.55, 0.6, -0.4), Vector((0.0, 0.25, 0.03)), 0.3, 1200, 800)
    render("HK416_rail_q", (-0.55, -0.45, -0.5), Vector((0.0, 0.18, 0.03)), 0.3, 1200, 800)
    state(folded=True)
    render("HK416_collapsed_right", right, centre, SIZE, W, H)
    state(extra=[("EXPS3_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
                 ("AimRight_Laser", "laser_right")], can=True)
    render("HK416_fitted_right", right, centre + Vector((0, 0.04, 0)), SIZE + 0.1, W, H)
    render("HK416_fitted_q", (0.62, -0.5, -0.45), centre, SIZE + 0.1, W, int(H * 1.3))
    state(extra=[("LR4X_Scope", "scope"), ("Bipod_Deployed", "bipod")])
    render("HK416_lr4x_right", right, centre, SIZE, W, H)
    state(extra=[("ElcanX2_Scope", "scope")])
    render("HK416_elcan_right", right, centre, SIZE, W, H)
    for key in ("BODY", "BODY_RD", "BODY_FD"):
        place(bodies[key])
        place(bolt)
        place(handle)
        place(marks)
        show_only([bodies[key], bolt, handle, marks])
        render("HK416_sights_" + key, right, Vector((0.0, 0.17, 0.02)), 0.36, 1500, 500)
    state(fired=True, racked=True)
    render("HK416_racked_right", right, Vector((0.0, 0.05, 0.0)), 0.3, 1200, 700)
    for name, d in (("HK416_selector_left", left), ("HK416_selector_right", right)):
        render(name, d, Vector((0.0, 0.035, 0.008)), 0.09, 900, 600)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    g = load(f"{GOM}/models_X/weapons/firearms/M4A1.fbx", f"{GOM}/textures/weapons/firearms/assault_rifles/M4A1.png")
    for o in g.values():
        place(o)
    place(mag, {"offset": [0.0, 0.1015, 0.0144]})
    show_only(list(g.values()) + [mag])
    render("gom_M4A1_right", right, centre, SIZE, W, H)


main()
