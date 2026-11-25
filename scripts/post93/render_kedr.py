"""Review renders of the exported PP-91 Kedr, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_kedr.py -- OUT_DIR

Imports what build_kedr.py wrote, places the parts at kedr_points.json the way the engine does (offset, then
rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR:

    left_photo      the left side as the measuring photo has it (the stock open, the 30-round magazine in), 4 px a
                    mm: the view to lay on the photo (scripts/ref_crop.py --overlay) and to score against the traced
                    outline (kedr_reference_outline.json); left_a / left_b the same at 8 px a mm in two halves
    folded_*        the stock folded, the 20-round magazine in: left, right, top, front, back, 3/4 views
    open_q, open_right, fired_*, mag30_*, nomag_*, <magazine>_side / _q / _back
    cmp_*           beside GoM's MAC-10 and MP5K and the main mod's Micro Uzi at one game scale

The gun is modelled upside down (held like a pistol) and is turned back upright here. Game space is Blender world
space, the mirror image of what the game shows: flip every render left-right to see the gun as in game.
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
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "kedr_points.json")))
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_KEDR_magazines.fbx")
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')
KG = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
MAG_NAMES = {r: "9x18Magazine%d_KEDR" % r for r in (20, 30)}


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
        if keep and o.name not in keep:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name] = o
    return objs


def place(o, point=None, handgun=True, scale=1.0):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = ((UPRIGHT if handgun else Matrix.Identity(4)) @ mat @ Matrix.Scale(scale, 4)
                      @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0)))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


def up(L, H, x=0.0):
    """Photo (L, H) mm (real, on the middle plane unless x) -> world position on the upright gun."""
    return Vector((x * KG, (L0 - L) * KG, (H - H0) * KG))


def render(name, direction, centre, size_mm, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = size_mm * KG
    cam.location = Vector(centre) - d * 2.0
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
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    mags = {r: load(MAGS, os.path.join(TEX, n + ".png"), keep=[n])[n] for r, n in MAG_NAMES.items()}
    objs = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_KEDR.fbx"),
                os.path.join(TEX, "KEDR.png"))
    body, bolt = objs["KEDR_BODY"], objs["KEDR_BOLT"]
    folded, deployed = objs["KEDR_STOCK_FOLDED"], objs["KEDR_STOCK_DEPLOYED"]
    p = PTS

    def state(mag=20, fired=False, opened=False):
        place(body)
        place(bolt, p["bolt_fired"] if fired else None)
        stock = deployed if opened else folded
        place(stock)
        shown = [body, bolt, stock]
        if mag:
            place(mags[mag], p["magazine"])
            shown.append(mags[mag])
        show_only(shown)

    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    cams = {}
    # as the measuring photo: the stock open, the 30-round magazine, 4 px a mm
    state(mag=30, opened=True)
    render("left_photo", left, up(267.5, 112.5), 560.0, 2240, 1040)
    cams["left_photo"] = {"centre_mm": [267.5, 112.5], "px_per_mm": 4.0, "size": [2240, 1040]}
    # the same at 8 px a mm in two halves, for the part crops
    for name, cL in (("left_a", 150.0), ("left_b", 400.0)):
        render(name, left, up(cL, 112.5), 320.0, 2560, 2080)
        cams[name] = {"centre_mm": [cL, 112.5], "px_per_mm": 8.0, "size": [2560, 2080]}
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    render("open_q", q_left, up(267.5, 112.5), 580.0, 2320, 1300)
    render("open_right", right, up(267.5, 112.5), 560.0, 2240, 1040)
    c = up(155.0, 130.0)
    state()
    render("folded_left", left, c, 340.0, 1360, 1040)
    render("folded_right", right, c, 340.0, 1360, 1040)
    render("folded_q_left", q_left, c, 360.0, 1440, 1160)
    render("folded_q_right", q_right, c, 360.0, 1440, 1160)
    render("folded_q_front_left", (-0.55, 0.6, -0.35), c, 360.0, 1440, 1160)
    render("folded_q_front_right", (0.55, 0.6, -0.35), c, 360.0, 1440, 1160)
    render("folded_q_top_left", (-0.45, -0.35, -0.82), c, 360.0, 1440, 1160)
    render("folded_top", (0, 0, -1), up(155.0, H0), 340.0, 1360, 340)
    render("folded_front", (0, -1, 0), up(L0, 130.0), 260.0, 1040, 1040)
    render("folded_back", (0, 1, 0), up(L0, 130.0), 260.0, 1040, 1040)
    render("folded_under", (0.15, -0.1, 0.98), c, 360.0, 1440, 760)
    state(fired=True)
    render("fired_right", right, c, 340.0, 1360, 1040)
    render("fired_left", left, c, 340.0, 1360, 1040)
    state(mag=30)
    render("mag30_left", left, up(155.0, 105.0), 340.0, 1360, 1160)
    state(mag=None)
    render("nomag_left", left, c, 340.0, 1360, 1040)
    for r, o in mags.items():
        place(o, handgun=False)
        show_only([o])
        ctr = Vector((0.0, -0.002, -0.05))
        render("%s_side" % MAG_NAMES[r], right, ctr, 190.0, 640, 640)
        render("%s_q" % MAG_NAMES[r], (0.6, -0.6, -0.45), ctr, 190.0, 640, 640)
        render("%s_back" % MAG_NAMES[r], (0, 1, 0), ctr, 190.0, 640, 640)
    # beside GoM's MAC-10 and MP5K and our Micro Uzi at one game scale (ours are drawn at 0.603 of real size, GoM's
    # SMGs at 0.72)
    K = 0.000603
    span = 470.0
    cw, ch = int(span * 2.0), int(span * 0.75 * 2.0)
    cc = Vector((0.0, 0.07, -0.02))

    def game_render(name):
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = span * K
        d = Vector(left).normalized()
        cam.location = cc - d * 2.0
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.resolution_x, sc.render.resolution_y = cw, ch
        sc.render.filepath = os.path.join(OUT, name + ".png")
        bpy.ops.render.render(write_still=True)

    state()
    game_render("cmp_KEDR")
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    uzi = load(os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_MICROUZI.fbx"),
               os.path.join(MAIN, "textures/weapons/GunsOfTien/MICROUZI.png"))
    shown = []
    for o in uzi.values():
        place(o)
        shown.append(o)
    show_only(shown)
    game_render("cmp_MICROUZI")
    if GOM:
        for name in ("MP5K", "MAC10"):
            g = load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % name),
                     os.path.join(GOM, "textures/weapons/firearms/smgs/%s.png" % name))
            shown = []
            for o in g.values():
                if "FOLDED" in o.name or "BOLT" in o.name and "DEPLOYED" in o.name:
                    continue
                place(o)
                shown.append(o)
            show_only(shown)
            game_render("cmp_gom_" + name)


main()
