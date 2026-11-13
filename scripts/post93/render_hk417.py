"""Review renders of the HK417s build_hk417.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_hk417.py -- OUT_DIR

Each gun from both sides and 3/4, its sight states, both magazines, fitted with GoM's parts at the gun's points
(approximation: the part models' own points are not applied, as render_hk416.py), and HK417_photo.png: the 16" from
its left at the measuring photo's scale and framing (references/hk417/bing/b_028.jpg, 2.08 px a mm), for
make_hk417_preview.py to lay over the photo (mirrored: game space is Blender's, the mirror image of the game's).
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
PTS = json.load(open(os.path.join(HERE, "hk417_points.json")))
AR_TEX = f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png"
TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")
FBX = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK417.fbx")
R = 0.000603
PHOTO = dict(px=2.08, trig_px=1264.5, trig_y=107.7, bore_px=679.0, w=2000, h=1500)
RED_DOTS = ("EXPS1_Sight", "EXPS3_Sight", "Aimpoint_Sight", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "Kobra_Sight")


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
    gun = load(FBX, AR_TEX)
    marks = load(FBX, os.path.join(TEX, "HK416_MARKINGS.png"), keep=["HK417_MARKINGS"])["HK417_MARKINGS"]
    mags = load(os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_HK417_magazines.fbx"),
                os.path.join(TEX, "HK417_MAG.png"))
    bolt, handle, stock = gun["HK417_BOLT"], gun["HK417_CHARGING_HANDLE"], gun["HK417_STOCK"]
    parts = {}
    for cat, name in (("scopes", "Aimpoint_Sight"), ("scopes", "LR4X_Scope"), ("scopes", "LR10X_Scope"),
                      ("foregrips", "MKC_Foregrip"), ("pointers", "SR7_Light"), ("pointers", "AimRight_Laser"),
                      ("bipods", "Bipod_Deployed")):
        try:
            parts[name] = load(f"{GOM}/models_X/weapons/parts/{cat}.fbx", f"{GOM}/textures/weapons/parts/{cat}/{name}.png",
                               keep=[name])[name]
        except Exception as e:                                   # noqa: BLE001
            print("skip", name, e)

    def state(g, mag=20, extra=(), body_key=None, folded=True):
        p = PTS[g]
        optic = [n for n, pt in extra if pt == "scope"]
        key = body_key or ("_BODY" if not optic else ("_BODY_RD" if optic[0] in RED_DOTS else "_BODY_FD"))
        body = gun[g + key]
        place(body)
        place(bolt)
        place(handle)
        place(stock, p["stock_folded"] if folded else p["stock"])
        place(marks)
        shown = [body, bolt, handle, stock, marks]
        if mag:
            m = mags["762x51Magazine%d_HK417" % mag]
            place(m, p["magazine"])
            shown.append(m)
        for name, point in extra:
            if name in parts:
                place(parts[name], p[point])
                shown.append(parts[name])
        show_only(shown)

    left, right = (-1, 0, 0), (1, 0, 0)
    for g, size, cy in (("HK417", 0.62, 0.13), ("HK417S", 0.68, 0.16)):
        centre = Vector((0.0, cy, 0.0))
        state(g)
        render(g + "_left", left, centre, size, 2000, 700)
        render(g + "_right", right, centre, size, 2000, 700)
        render(g + "_q", (-0.62, -0.5, -0.45), centre, size, 2000, 950)
        render(g + "_front_q", (0.55, 0.6, -0.4), Vector((0.0, cy + 0.13, 0.03)), 0.32, 1200, 800)
        state(g, folded=False)
        render(g + "_deployed_right", right, centre, size + 0.04, 2000, 700)
        state(g, extra=[("Aimpoint_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
                        ("AimRight_Laser", "laser_right")])
        render(g + "_fitted_q", (0.62, -0.5, -0.45), centre, size, 2000, 950)
        state(g, extra=[("LR10X_Scope" if g == "HK417S" else "LR4X_Scope", "scope"), ("Bipod_Deployed", "bipod")])
        render(g + "_scope_right", right, centre, size, 2000, 800)
        for key in ("_BODY", "_BODY_RD", "_BODY_FD"):
            state(g, mag=None, body_key=key)
            render(g + "_sights" + key, right, Vector((0.0, cy + 0.04, 0.02)), size * 0.75, 1800, 500)
    for n in (10, 20):
        state("HK417", mag=n)
        render("HK417_mag%d" % n, right, Vector((0.0, 0.1, -0.02)), 0.3, 1200, 1000)
    # the measuring photo's framing (its left side; the render is mirrored back in the preview)
    ph = PHOTO
    B = PTS["HK417"]["_extras"]["bore_mm"]
    cy_mm = ph["trig_y"] + (ph["trig_px"] - ph["w"] / 2.0) / ph["px"]
    cz_mm = B + (ph["bore_px"] - ph["h"] / 2.0) / ph["px"]
    state("HK417", mag=10, body_key="_BODY_FD")
    render("HK417_photo", left, Vector((0.0, cy_mm * R, cz_mm * R)), ph["w"] / ph["px"] * R, ph["w"], ph["h"])


main()
