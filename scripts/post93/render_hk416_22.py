"""Review renders of the HK416 .22 pistols build_hk416_22.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_hk416_22.py -- OUT_DIR

Each pistol (turned back upright for viewing) from both sides and 3/4, its sight states, its magazines; plus a
right-side view at the measuring photo's own scale and framing (<gun>_photo.png) for make_hk416_22_preview.py to lay
over the photo. Game space is Blender's, the mirror image of what the game shows; the camera on -x sees the gun's right
side with the muzzle to the left, as the mirrored photos.
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
PTS = json.load(open(os.path.join(HERE, "hk416_22_points.json")))
TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")
AR_TEX = f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png"
R = 0.000603
# the measuring photos (build_hk416_22.py PH): px a mm, the well's front face px, the bore px, the photo's height
PHOTO = {"QR22": (3.72, 930.0, 330.0, 1000), "ML22": (3.66, 995.0, 379.0, 1200)}
MAG_POINT = {"offset": [0.0, 0.1015, 0.0144], "rotate": [0.0, 0.0, 0.0]}   # GoM's AR15 (upright)


def material(texture):
    m = bpy.data.materials.new(os.path.basename(texture))
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    return m


def load(path, textures):
    """textures: node name -> texture (the default under None)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    objs = {}
    for o in set(bpy.data.objects) - before:
        if o.type != 'MESH':
            bpy.data.objects.remove(o)
            continue
        n = o.name.split(".")[0]
        o.data.materials.clear()
        o.data.materials.append(material(textures.get(n, textures[None])))
        objs[n] = o
    return objs


def place(o, turned=False, point=None):
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = mat @ (Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0)) if turned else Matrix.Diagonal((1.0, 1.0, -1.0, 1.0)))


def upright_point(p):
    x, y, z = p["offset"]
    return {"offset": [-x, y, -z], "rotate": [0.0, 0.0, 0.0]}


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
    mags = load(os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_HK416_22_magazines.fbx"),
                {None: os.path.join(TEX, "HK416_22_MAG.png")})
    marks_tex = os.path.join(TEX, "HK416_MARKINGS.png")
    gens = (("QR22", ("", "_RD", "_FD"), 10), ("ML22", ("", "_RD", "_FD", "_RDX", "_FDX"), 20))
    for gen, states, mag_rds in gens:
        if "HK416" + gen not in PTS:            # shelved (build_hk416_22.py GENS)
            continue
        n = "HK416" + gen
        body_tex = AR_TEX if gen == "QR22" else os.path.join(TEX, "HK416ML22.png")
        tex = {None: AR_TEX, n + "_MARKINGS": marks_tex}
        for s in states:
            tex[n + "_BODY" + s] = body_tex
        gun = load(os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_%s.fbx" % n), tex)
        pts = PTS[n]
        bolt, handle, marks = gun[n + "_BOLT"], gun[n + "_CHARGING_HANDLE"], gun[n + "_MARKINGS"]
        mag = mags["22LRMagazine%d_HK416" % mag_rds]

        def state(body_key="", fired=False, racked=False, magazine=mag):
            body = gun[n + "_BODY" + body_key]
            place(body, turned=True)
            place(bolt, turned=True, point=upright_point(pts["bolt_fired"]) if fired else None)
            place(handle, turned=True, point=upright_point(pts["charging_handle_open"]) if racked else None)
            place(marks, turned=True)
            shown = [body, bolt, handle, marks]
            if magazine:
                place(magazine, point=MAG_POINT)
                shown.append(magazine)
            show_only(shown)
        right, left = (1, 0, 0), (-1, 0, 0)
        centre = Vector((0.0, 0.2 * 1.0, 0.0))
        SIZE, W, H = 0.34, 1800, 1000
        state()
        render(n + "_right", right, Vector((0.0, 0.135, 0.0)), SIZE, W, H)
        render(n + "_left", left, Vector((0.0, 0.135, 0.0)), SIZE, W, H)
        render(n + "_q", (0.6, -0.55, -0.45), Vector((0.0, 0.135, 0.0)), SIZE, W, int(H * 1.1))
        render(n + "_front_q", (0.55, -0.6, -0.4) if False else (-0.55, -0.6, -0.4), Vector((0.0, 0.2, 0.02)),
               0.24, 1400, 900)
        render(n + "_rear_q", (0.55, 0.6, -0.4), Vector((0.0, 0.07, 0.01)), 0.2, 1400, 900)
        for s in states:
            state(s, magazine=None)
            render(n + "_sights" + (s or "_UP"), right, Vector((0.0, 0.135, 0.02)), SIZE, W, 700)
        for rds in (10, 20, 30):
            state(magazine=mags["22LRMagazine%d_HK416" % rds])
            render(n + "_mag%d" % rds, right, Vector((0.0, 0.11, -0.02)), 0.3, 1400, 1000)
        state(fired=True, racked=True)
        render(n + "_racked", right, Vector((0.0, 0.09, 0.0)), 0.2, 1400, 900)
        # fitted (the QR22's rails): GoM's Aimpoint on the rear-off body, MKC foregrip, SR7 light, AimRight laser
        if gen == "QR22":
            parts = {}
            for fbx, node, tx in (("scopes", "Aimpoint_Sight", "scopes"), ("foregrips", "MKC_Foregrip", "foregrips"),
                                  ("pointers", "SR7_Light", "pointers"), ("pointers", "AimRight_Laser", "pointers")):
                path = f"{GOM}/models_X/weapons/parts/{fbx}.fbx"
                if not os.path.exists(path):
                    continue
                got = load(path, {None: f"{GOM}/textures/weapons/parts/{tx}/{node}.png"})
                for k, o in got.items():
                    if k != node:
                        bpy.data.objects.remove(o)
                if node in got:
                    parts[node] = got[node]
            where = {"Aimpoint_Sight": "scope", "MKC_Foregrip": "foregrip", "SR7_Light": "light_left",
                     "AimRight_Laser": "laser_right"}
            state("_RD", magazine=mags["22LRMagazine20_HK416"])
            shown = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]
            for node, o in parts.items():
                place(o, point=upright_point(pts[where[node]]))
                shown.append(o)
            show_only(shown)
            render(n + "_fitted_right", right, Vector((0.0, 0.135, 0.0)), SIZE, W, H)
            render(n + "_fitted_q", (0.6, -0.55, -0.45), Vector((0.0, 0.135, 0.0)), SIZE, W, int(H * 1.1))
            for o in parts.values():
                o.hide_render = True
                o.name = o.name + "_done"
        # the photo's framing: its px a mm across 1800 px, its well face and bore where the photo has them
        px, mw, bore, ph = PHOTO[gen]
        B = pts["_extras"]["bore_mm"]
        cy = 206.7 + (mw - 900.0) / px
        cz = B - (ph / 2.0 - bore) / px
        state(magazine=mag)
        render(n + "_photo", right, Vector((0.0, cy * R, cz * R)), 1800 * R / px, 1800, ph)
        for o in gun.values():
            o.hide_render = True
            o.name = o.name + "_done"


main()
