"""Review renders of the exported RPK and RPK-74, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_rpk.py -- OUT_DIR

Imports what build_rpk.py wrote with GoM's textures, places the parts at rpk_points.json the way the engine does
(offset, then rotateXYZ in degrees, game space; the bipods and bolts at the origin) and renders orthographic Workbench
views into OUT_DIR at PX_PER_MM real: each gun's left and right side with the bipod folded and deployed and its
magazines, 3/4 views, the front, GoM's AK it is built on (at the same drawn scale, so the longer barrel and the stock
show), and the RPK's magazines alone (GoM's 30 and 75 at our scale beside our 40). Game space is Blender world space,
the mirror image of what the game shows: the "left" view (camera at +X) shows the gun's right side in game.
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
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "rpk_points.json")))
SCALE = PTS["_extras"]["scale"]
K = 0.000603                       # game units per real mm, every Guns of Tien gun
PX_PER_MM = 1.6
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPK.fbx")
MAG_FBX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPK_magazines.fbx")
TEX = GOM + "/textures/weapons/firearms/assault_rifles/"
MTEX = GOM + "/textures/weapons/magazines/assault_rifles/"
GOM_MAGS = GOM + "/models_X/weapons/magazines/assault_rifles.fbx"
DRUM_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/762x39Drum75_RPK.png")


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
    """Import an FBX; textures = {node name: texture path} (nodes not named are dropped)."""
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


def render(name, objs, direction, span_mm=None, centre=None, tall_mm=None):
    show_only(objs)
    lo, hi = bounds(objs)
    c = centre if centre is not None else (lo + hi) / 2.0
    span = span_mm * K if span_mm else (max(hi.y - lo.y, hi.x - lo.x) + 0.04)
    tall = tall_mm * K if tall_mm else (hi.z - lo.z + 0.04)
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = c - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = max(span, tall)
    sc = bpy.context.scene
    w, h = int(span / K * PX_PER_MM), int(tall / K * PX_PER_MM)
    if tall > span:
        w = int(tall / K * PX_PER_MM * span / tall)
    sc.render.resolution_x, sc.render.resolution_y = max(w, 16), max(h, 16)
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

    left, right, front = (-1, 0, 0), (1, 0, 0), (0, -1, 0)
    q = (0.7, -0.45, -0.5)
    info = {}
    for gun, gom, mags in (("RPK", "AK47", ["762x39Magazine30", "762x39Magazine75"]),
                           ("RPK74", "AK74", ["545x39Magazine30", "545x39Magazine45"])):
        tex = TEX + gom + ".png"
        g = load(GUN_FBX, {f"{gun}_{n}": tex for n in ("BODY", "BOLT", "BIPOD_FOLDED", "BIPOD_DEPLOYED")})
        m = load(GOM_MAGS, {n: MTEX + n + ".png" for n in mags}, SCALE)
        if gun == "RPK":
            m.update(load(MAG_FBX, {"762x39Magazine40_RPK": MTEX + "762x39Magazine30.png",
                                    "762x39Drum75_RPK": DRUM_TEX}))
        pts = PTS[gun]
        for o in g.values():
            place(o)
        for o in m.values():
            place(o, pts["magazine"])
        body, bolt = g[f"{gun}_BODY"], g[f"{gun}_BOLT"]
        fold, dep = g[f"{gun}_BIPOD_FOLDED"], g[f"{gun}_BIPOD_DEPLOYED"]
        mag_main = m.get("762x39Magazine40_RPK") or m["545x39Magazine45"]
        lo, hi = bounds([body])
        info[gun] = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1)}
        span = 1150
        centre = Vector((0.0, (lo.y + hi.y) / 2.0, -0.03))
        render(f"{gun}_left_folded", [body, bolt, fold, mag_main], left, span, centre, 420)
        render(f"{gun}_left_deployed", [body, bolt, dep, mag_main], left, span, centre + Vector((0, 0, -0.05)), 560)
        render(f"{gun}_right_folded", [body, bolt, fold, mag_main], right, span, centre, 420)
        render(f"{gun}_q_deployed", [body, bolt, dep, mag_main], q, span, centre + Vector((0, 0, -0.05)), 700)
        render(f"{gun}_front_deployed", [body, bolt, dep, mag_main], front, 420, centre + Vector((0, 0, -0.05)), 560)
        render(f"{gun}_under_folded", [body, bolt, fold, mag_main], (0.45, -0.35, 0.6), span, centre, 560)
        for n, o in m.items():
            render(f"{gun}_with_{n}", [body, bolt, fold, o], left, span, centre + Vector((0, 0, -0.04)), 560)
        if gun == "RPK":
            drum = m["762x39Drum75_RPK"]
            render("RPK_drum_q", [body, bolt, dep, drum], q, span, centre + Vector((0, 0, -0.05)), 700)
            render("RPK_drum_right", [body, bolt, fold, drum], right, span, centre + Vector((0, 0, -0.04)), 560)
            render("RPK_drum_front", [body, bolt, fold, drum], front, 420, centre + Vector((0, 0, -0.05)), 560)
            for n in ("762x39Drum75_RPK", "762x39Magazine40_RPK"):
                place(m[n])
                render(n + "_side", [m[n]], left, 300, Vector((0, 0.04, -0.09)), 300)
                render(n + "_q", [m[n]], (-0.6, -0.5, -0.4), 300, Vector((0, 0.04, -0.09)), 300)
                render(n + "_front", [m[n]], front, 300, Vector((0, 0.04, -0.09)), 300)
                place(m[n], pts["magazine"])
        # GoM's AK at the same drawn scale, lined up on the grip (the origin)
        a = load(f"{GOM}/models_X/weapons/firearms/{gom}.fbx", {f"{gom}_BODY": tex, f"{gom}_BOLT": tex}, SCALE)
        for o in a.values():
            place(o)
        render(f"{gun}_gom_{gom}", list(a.values()), left, span, centre, 420)
        if gun == "RPK":      # the 40 and the drum on GoM's AK-47, drawn at GoM's size (<model>_GoM)
            for n, tex in (("762x39Magazine40_RPK", MTEX + "762x39Magazine30.png"), ("762x39Drum75_RPK", DRUM_TEX)):
                extra = load(MAG_FBX, {n: tex}, SCALE / SCALE)
                o = extra[n]
                o.data.transform(Matrix.Scale(1.0 / SCALE, 4))
                o.data.transform(Matrix.Scale(SCALE, 4))      # GoM's AK-47 is drawn here at our scale too
                place(o, {"offset": [v * SCALE for v in (0.0, 0.1223, 0.0132)]})
                render(f"gom_AK47_with_{n}", list(a.values()) + [o], left, span, centre + Vector((0, 0, -0.04)), 560)
        render(f"{gun}_stock_detail", [body], left, 330, Vector((0, -0.12, -0.02)), 260)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
