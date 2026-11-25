"""Review renders of the exported PPSh-41, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_ppsh41.py -- OUT_DIR

Imports what build_ppsh41.py wrote, places the parts at ppsh41_points.json the way the engine does (offset, then rotateXYZ in
degrees, game space) and renders orthographic Workbench views into OUT_DIR: the left side at the reference photo's
scale for the outline check and the part-by-part crops (scripts/ref_crop.py --overlay), both sides, 3/4 views, the
bolt back, the drum and the box fitted and alone, and GoM's Thompson (its closest gun) at the same scale.

Game space is used as Blender world space (data z flipped back), the mirror image of what the game shows; flip every
render left-right to see the gun as in game (render_fiveseven.py's note).
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
POINTS = json.load(open(os.path.join(HERE, "ppsh41_points.json")))
K = 0.000603
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
UPRIGHT = Matrix.Identity(4)                     # a rifle-held gun is modelled upright
DRUM, BOX = "762x25Drum71_PPSH41", "762x25Magazine35_PPSH41"


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


def place(o, point=None, upright=True):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = (UPRIGHT if upright else Matrix.Identity(4)) @ mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


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


def up(L, H):
    """Photo (L, H) mm -> world position of that point on the upright gun."""
    return Vector((0.0, (L0 - L) * K, (H - H0) * K))


def main():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_cavity = False
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_PPSH41.fbx"), os.path.join(TEX, "PPSH41.png"))
    body, bolt = gun["PPSH41_BODY"], gun["PPSH41_BOLT"]
    mags = {}
    for n in (DRUM, BOX):
        mags[n] = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_PPSH41_magazines.fbx"),
                       os.path.join(TEX, n + ".png"), keep=n)[n]

    def state(mag=DRUM, fired=False):
        place(body)
        place(bolt, POINTS["bolt_fired"] if fired else None)
        objs = [body, bolt]
        if mag:
            place(mags[mag], POINTS["magazine"])
            objs.append(mags[mag])
        show_only(objs)

    right, left = (1, 0, 0), (-1, 0, 0)          # the camera looks along these: (1, 0, 0) sees the gun's right side
    q_left = (-0.62, -0.5, -0.6)
    q_right = (0.7, -0.45, -0.55)
    c = up(421.0, 100.0)
    state()
    # left side at 3 px a mm for the photo overlays: 900 x 240 mm, centred on photo (421, 100)
    render("left_photo", left, c, 900 * K, 2700, 720)
    json.dump({"left_photo": {"centre_mm": [421.0, 100.0], "px_per_mm": 3.0, "size": [2700, 720]}},
              open(os.path.join(OUT, "cameras.json"), "w"))
    # close views at 8 px a mm for the part-by-part crops (front, middle, rear)
    cams = json.load(open(os.path.join(OUT, "cameras.json")))
    for name, cL in (("left_a", 110.0), ("left_b", 330.0), ("left_c", 530.0), ("left_d", 735.0)):
        render(name, left, up(cL, 100.0), 240 * K, 1920, 1760)
        cams[name] = {"centre_mm": [cL, 100.0], "px_per_mm": 8.0, "size": [1920, 1760]}
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"))
    render("right", right, c, 900 * K, 2700, 720)
    render("q_left", q_left, c, 900 * K, 1800, 1100)
    render("q_right", q_right, c, 900 * K, 1800, 1100)
    render("q_front_left", (-0.55, 0.6, -0.35), c, 900 * K, 1800, 1100)
    render("q_front_right", (0.55, 0.6, -0.35), c, 900 * K, 1800, 1100)
    render("q_back_right", (0.55, 0.6, -0.4), c, 900 * K, 1800, 1100)
    render("top", (0, 0, -1), up(421.0, 0.0) * Vector((0, 1, 0)), 900 * K, 2700, 300)
    render("front", (0, -1, 0), up(0.0, 100.0) * Vector((0, 0, 1)), 260 * K, 700, 700)
    render("back", (0, 1, 0), up(0.0, 100.0) * Vector((0, 0, 1)), 260 * K, 700, 700)
    render("under", (0.15, -0.1, 0.98), c, 900 * K, 1800, 700)
    state(fired=True)
    render("fired_right", right, c, 900 * K, 2700, 720)
    state(mag=BOX)
    render("box_left", left, c, 900 * K, 2700, 900)
    render("box_q", q_right, c, 900 * K, 1800, 1100)
    state(mag=None)
    render("nomag_left", left, c, 900 * K, 2700, 720)
    for n in (DRUM, BOX):
        place(mags[n])
        show_only([mags[n]])
        render("%s_side" % n, right, Vector((0.0, 0.01, -0.06)), 0.2, 600, 600)
        render("%s_q" % n, (0.6, -0.6, -0.45), Vector((0.0, 0.01, -0.06)), 0.2, 600, 600)
        render("%s_front" % n, (0, -1, 0), Vector((0.0, 0.0, -0.06)), 0.2, 600, 600)
    if GOM:
        game = Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))
        other = load(os.path.join(GOM, "models_X/weapons/firearms/THOMPSON.fbx"),
                     os.path.join(GOM, "textures/weapons/firearms/smgs/THOMPSON.png"))
        objs = list(other.values())
        d = load(os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
                 os.path.join(GOM, "textures/weapons/magazines/smgs/45Magazine100_THOMPSON.png"),
                 keep="45Magazine100_THOMPSON")["45Magazine100_THOMPSON"]
        for o in objs:
            o.matrix_world = game
        d.matrix_world = Matrix.Translation(Vector((0.0, 0.1055, 0.0366))) @ game
        show_only(objs + [d])
        render("gom_thompson_right", right, Vector((0.0, 0.05, 0.0)), 0.62, 1860, 760)
        render("gom_thompson_q", q_right, Vector((0.0, 0.05, 0.0)), 0.62, 1860, 1100)
        for o in objs + [d]:
            o.hide_render = True
        state()
        render("ppsh_right", right, Vector((0.0, 0.05, 0.0)), 0.62, 1860, 760)
        render("ppsh_q", q_right, Vector((0.0, 0.05, 0.0)), 0.62, 1860, 1100)


main()
