"""Review renders of the exported 9A-91 and VSK-94, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_9a91.py -- OUT_DIR

Imports what build_9a91.py wrote with 9A91.png, the magazine on `magazine`, the can and mount on `canon`, our bracket for
GoM's AK mount (9A91_AK_Mount) on `rail_up` and GoM's Kobra / PSO-1 on `scope` for the fitted views, places parts at a91_points.json the way the engine does (offset,
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
PTS = json.load(open(os.path.join(HERE, "a91_points.json")))
SCALE = 1.0
K = 0.000603
PX_PER_MM = 2.785
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_9A91.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/9A91.png")
MAG_FBX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_9A91_magazines.fbx")
MAG_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/9x39Magazine20_9A91.png")
PART_FBX = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_9A91_parts.fbx")
PART_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/9A91_Suppressor.png")
AKM_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93/9A91_AK_Mount.png")


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
    sc.view_settings.exposure = 1.0          # the blued steel reads near black under the studio light
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    nodes = ("9A91_BODY", "9A91_STOCK_DEPLOYED", "9A91_STOCK_FOLDED", "VSK94_BODY", "9A91_BOLT")
    info = {}
    for gun, body_name in (("9A91", "9A91_BODY"), ("VSK94", "VSK94_BODY")):
        pts = PTS[gun]
        g = load(GUN_FBX, {n: TEX for n in nodes})
        mag = load(MAG_FBX, {"9x39Magazine20_9A91": MAG_TEX})["9x39Magazine20_9A91"]
        parts = load(PART_FBX, {"9A91_Suppressor": PART_TEX, "9A91_Muzzle_Mount_Device": PART_TEX})
        fit = {"AK_Mount": load(PART_FBX, {"9A91_AK_Mount": AKM_TEX})["9A91_AK_Mount"]}
        fit.update(load(GOM + "/models_X/weapons/parts/scopes.fbx",
                        {"PSO1_Scope": GOM + "/textures/weapons/parts/scopes/PSO1_Scope.png",
                         "Kobra_Sight": GOM + "/textures/weapons/parts/scopes/Kobra_Sight.png"}))
        for o in g.values():
            place(o)
        place(mag, pts["magazine"])
        for o in parts.values():
            place(o, pts["canon"])
        place(fit["AK_Mount"], pts["rail_up"])
        for n in ("PSO1_Scope", "Kobra_Sight"):
            place(fit[n], pts["scope"])
        body, bolt = g[body_name], g["9A91_BOLT"]
        extra = [g["9A91_STOCK_DEPLOYED"]] if gun == "9A91" else []
        lo, hi = bounds([body] + extra)
        info[gun] = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1)}
        lo2, hi2 = bounds([body] + extra + [mag, parts["9A91_Suppressor"]])
        info[gun]["length_with_can_mm"] = round((hi2.y - lo2.y) / K, 1)
        info[gun]["height_with_mag_mm"] = round((hi2.z - lo2.z) / K, 1)
        centre = Vector((0.0, (lo2.y + hi2.y) / 2.0, (lo2.z + hi2.z) / 2.0))
        span = (hi2.y - lo2.y) / K + 40
        tall = (hi2.z - lo2.z) / K + 120
        right, left, front = (1, 0, 0), (-1, 0, 0), (0, -1, 0)
        base = [body, bolt, mag] + extra
        can = [parts["9A91_Suppressor"]]
        render(gun + "_right", base, right, span, centre, tall)
        render(gun + "_right_can", base + can, right, span, centre, tall)
        render(gun + "_left", base + can, left, span, centre, tall)
        render(gun + "_left_mount", base + [parts["9A91_Muzzle_Mount_Device"]], left, span, centre, tall)
        sight = fit["Kobra_Sight"] if gun == "9A91" else fit["PSO1_Scope"]
        render(gun + "_left_optic", base + can + [fit["AK_Mount"], sight], left, span, centre, tall)
        render(gun + "_right_optic", base + can + [fit["AK_Mount"], sight], right, span, centre, tall)
        render(gun + "_q_optic", base + can + [fit["AK_Mount"], sight], (-0.7, -0.45, -0.5), span, centre, tall + 150)
        render(gun + "_q_mount", base + can + [fit["AK_Mount"]], (-0.7, 0.55, -0.45), span, centre, tall + 150)
        render(gun + "_q", base + can, (0.7, -0.45, -0.5), span, centre, tall + 150)
        render(gun + "_q_back", base + can, (-0.7, 0.55, -0.45), span, centre, tall + 150)
        render(gun + "_top", base + can, (0, 0, -1), 140, centre, span)      # the length runs up the image
        render(gun + "_front", base, front, 220, centre, tall)
        if gun == "9A91":
            render("9A91_folded", [body, bolt, mag, g["9A91_STOCK_FOLDED"]], right, span, centre, tall)
            render("9A91_folded_optic", [body, bolt, mag, g["9A91_STOCK_FOLDED"], fit["AK_Mount"], sight], right, span,
                   centre, tall)
            render("9A91_folded_q", [body, bolt, mag, g["9A91_STOCK_FOLDED"]], (0.7, -0.45, -0.5), span, centre,
                   tall + 150)
            # the folded stock under the bracket and each optic: from the left front (the bracket's side) and from
            # above the left rear, close up on the receiver
            folded = [body, bolt, mag, g["9A91_STOCK_FOLDED"], fit["AK_Mount"]]
            rc = Vector((0.0, centre.y + 0.01, centre.z + 0.02))
            for name, s in (("kobra", fit["Kobra_Sight"]), ("pso1", fit["PSO1_Scope"])):
                render("9A91_folded_%s_q" % name, folded + [s], (-0.7, -0.45, -0.5), 420, rc, 300)
                render("9A91_folded_%s_back" % name, folded + [s], (-0.6, 0.6, -0.55), 420, rc, 300)
                render("9A91_folded_%s_right" % name, folded + [s], right, 420, rc, 260)
        place(bolt, pts["bolt_fired"])
        render(gun + "_bolt_back", base, right, span, centre, tall)
        for o in list(g.values()) + [mag] + list(parts.values()) + list(fit.values()):
            bpy.data.objects.remove(o)
    print("SIZES", info)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
