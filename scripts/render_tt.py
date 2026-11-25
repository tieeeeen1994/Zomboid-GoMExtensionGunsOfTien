"""Review renders of the exported Tokarev TT, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_tt.py -- OUT_DIR

Imports what build_tt.py wrote, places the parts at tt_points.json the way the engine does (offset, then rotateXYZ in
degrees, game space) and renders orthographic Workbench views into OUT_DIR: the left side at the reference photo's
scale for the outline check and the part-by-part crops (scripts/ref_crop.py --overlay), both sides, 3/4 views, the
slide back, the magazine fitted and alone, and GoM's M1911 (its closest gun) and Glock 17 at the same scale.

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
POINTS = json.load(open(os.path.join(HERE, "tt_points.json")))
K = 0.000603
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')       # GoM's pistols (and this one) are modelled upside down
MAG = "762x25Magazine8_TT33"


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

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TT33.fbx"), os.path.join(TEX, "TT33.png"))
    body, slide = gun["TT33_BODY"], gun["TT33_SLIDE"]
    mag = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TT33_magazines.fbx"),
               os.path.join(TEX, MAG + ".png"), keep=MAG)[MAG]

    def state(with_mag=True, fired=False):
        place(body)
        place(slide, POINTS["slide_fired"] if fired else None)
        objs = [body, slide]
        if with_mag:
            place(mag)
            objs.append(mag)
        show_only(objs)

    right, left = (1, 0, 0), (-1, 0, 0)          # the camera looks along these: (1, 0, 0) sees the gun's right side
    q_left = (-0.62, -0.5, -0.6)
    q_right = (0.7, -0.45, -0.55)
    c = up(98.0, 64.0)
    state()
    # left side at 10 px a mm for the photo overlays: 230 x 150 mm, centred on photo (98, 64)
    render("left_photo", left, c, 230 * K, 2300, 1500)
    json.dump({"left_photo": {"centre_mm": [98.0, 64.0], "px_per_mm": 10.0, "size": [2300, 1500]}},
              open(os.path.join(OUT, "cameras.json"), "w"))
    render("right", right, c, 230 * K, 2300, 1500)
    render("q_left", q_left, c, 235 * K, 1400, 1050)
    render("q_right", q_right, c, 235 * K, 1400, 1050)
    render("q_front_left", (-0.55, 0.6, -0.35), c, 235 * K, 1400, 1050)
    render("q_front_right", (0.55, 0.6, -0.35), c, 235 * K, 1400, 1050)
    render("top", (0, 0, -1), up(98.0, 0.0) * Vector((0, 1, 0)), 215 * K, 1720, 400)
    render("front", (0, -1, 0), up(0.0, 64.0) * Vector((0, 0, 1)), 150 * K, 500, 750)
    render("back", (0, 1, 0), up(0.0, 64.0) * Vector((0, 0, 1)), 150 * K, 500, 750)
    render("q_top_left", (-0.45, -0.55, -0.7), c, 235 * K, 1400, 1050)
    render("q_back_right", (0.55, 0.6, -0.4), c, 235 * K, 1400, 1050)
    state(fired=True)
    render("fired_q", q_right, c, 250 * K, 1400, 1050)
    render("fired_left", left, c, 260 * K, 1600, 1050)
    state(with_mag=False)
    render("nomag_under", (0.25, -0.2, 0.95), c, 235 * K, 1000, 800)
    place(mag)
    show_only([mag])
    render("mag_alone", right, up(165.0, 48.0), 130 * K, 500, 800)
    render("mag_q", q_left, up(165.0, 48.0), 130 * K, 500, 800)
    if GOM:
        # GoM's M1911 and Glock 17 at the same scale, right side
        for gun_name in ("M1911", "GLOCK17"):
            other = load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % gun_name),
                         os.path.join(GOM, "textures/weapons/firearms/pistols/%s.png" % gun_name))
            objs = list(other.values())
            for o in objs:
                place(o)
            show_only(objs)
            render("gom_%s_right" % gun_name.lower(), right, Vector((0.0, 0.06, 0.0)), 0.23, 1000, 760)
            render("gom_%s_q" % gun_name.lower(), q_right, Vector((0.0, 0.06, 0.0)), 0.23, 1000, 760)
            for o in objs:
                o.hide_render = True
                o.name = "done_" + o.name
        state()
        render("tt_right", right, Vector((0.0, 0.06, 0.0)), 0.23, 1000, 760)
        render("tt_q", q_right, Vector((0.0, 0.06, 0.0)), 0.23, 1000, 760)


main()
