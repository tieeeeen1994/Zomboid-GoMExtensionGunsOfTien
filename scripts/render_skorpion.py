"""Review renders of the exported Skorpion vz. 82, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_skorpion.py -- OUT_DIR

Imports what build_skorpion.py wrote, places the parts at skorpion_points.json the way the engine does (offset, then
rotateXYZ in degrees, game space) and renders Workbench views into OUT_DIR:

    left_persp      the left side through the measuring photo's own lens (build_skorpion.py's D_CAM and axis), 8 px a
                    mm on the gun's middle plane: the view to lay on the photo (scripts/ref_crop.py --overlay) and to
                    score against the traced outline. An orthographic view does not match that photo.
    left_photo      the same side, orthographic, 4 px a mm
    right, top, front, back, q_*   the stock folded, the 24-round magazine in
    open_*          the stock open
    fired_*         the bolt back
    mag12_*, mag30_*, nomag_*, <magazine>_side / _q
    cmp_*           beside GoM's MAC-10 and MP5K and our Micro Uzi at one game scale

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
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "skorpion_points.json")))
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SKORPION_magazines.fbx")
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')
KG = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
D_CAM, AX_L, AX_H = PTS["_extras"]["lens_mm"]
MAG_NAMES = {r: "9x18Magazine%d_SKORPION" % r for r in (12, 24, 30)}


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


def render(name, direction, centre, size_mm, w, h, persp=None):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    if persp:
        cam.data.type = 'PERSP'
        cam.data.sensor_fit = 'HORIZONTAL'
        cam.data.sensor_width = 36.0
        cam.data.lens = persp * 36.0 / size_mm
        cam.location = Vector(centre) - d * (persp * KG)
        cam.data.clip_start = 0.01
    else:
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
    objs = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SKORPION.fbx"),
                os.path.join(TEX, "SKORPION.png"))
    body, bolt = objs["SKORPION_BODY"], objs["SKORPION_BOLT"]
    folded, deployed = objs["SKORPION_STOCK_FOLDED"], objs["SKORPION_STOCK_DEPLOYED"]
    p = PTS

    def state(mag=24, fired=False, opened=False):
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
    state()
    # the photo's lens: 300 x 260 mm of the middle plane at 8 px a mm, centred on its axis
    render("left_persp", left, up(AX_L, AX_H), 300.0, 2400, 2080, persp=D_CAM)
    cams["left_persp"] = {"centre_mm": [AX_L, AX_H], "px_per_mm": 8.0, "size": [2400, 2080]}
    c = up(135.0, 85.0)
    render("left_photo", left, c, 300.0, 1200, 1040)
    cams["left_photo"] = {"centre_mm": [135.0, 85.0], "px_per_mm": 4.0, "size": [1200, 1040]}
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    render("right", right, c, 300.0, 1200, 1040)
    render("q_left", q_left, c, 320.0, 1280, 1100)
    render("q_right", q_right, c, 320.0, 1280, 1100)
    render("q_front_left", (-0.55, 0.6, -0.35), c, 320.0, 1280, 1100)
    render("q_back_right", (0.55, 0.6, -0.4), c, 320.0, 1280, 1100)
    render("q_top_left", (-0.45, -0.35, -0.82), c, 320.0, 1280, 1100)
    render("top", (0, 0, -1), up(135.0, H0), 300.0, 1200, 320)
    render("front", (0, -1, 0), up(L0, 85.0), 260.0, 1040, 1040)
    render("back", (0, 1, 0), up(L0, 85.0), 260.0, 1040, 1040)
    render("under", (0.15, -0.1, 0.98), c, 320.0, 1280, 700)
    state(fired=True)
    render("fired_left", left, c, 300.0, 1200, 1040)
    render("fired_top", (-0.25, -0.2, -0.95), c, 300.0, 1200, 700)
    co = up(270.0, 85.0)
    state(opened=True)
    render("open_left", left, co, 580.0, 2320, 1040)
    render("open_q", q_left, co, 580.0, 2320, 1300)
    render("open_top", (0, 0, -1), up(270.0, H0), 580.0, 2320, 320)
    cams["open_left"] = {"centre_mm": [270.0, 85.0], "px_per_mm": 4.0, "size": [2320, 1040]}
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    for r in (12, 30):
        state(mag=r)
        render("mag%d_left" % r, left, up(135.0, 60.0), 300.0, 1200, 1200)
    state(mag=None)
    render("nomag_left", left, c, 300.0, 1200, 1040)
    render("nomag_under", (0.1, -0.05, 0.99), c, 300.0, 1200, 500)
    for r, o in mags.items():
        place(o, handgun=False)
        show_only([o])
        ctr = Vector((0.0, 0.0, -0.058))
        render("%s_side" % MAG_NAMES[r], right, ctr, 215.0, 640, 640)
        render("%s_q" % MAG_NAMES[r], (0.6, -0.6, -0.45), ctr, 215.0, 640, 640)
        render("%s_back" % MAG_NAMES[r], (0, 1, 0), ctr, 215.0, 640, 640)
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
    game_render("cmp_SKORPION")
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    uzi = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_MICROUZI.fbx"),
               os.path.join(TEX, "MICROUZI.png"))
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
