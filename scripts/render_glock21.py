"""Review renders of the exported Glock 21, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_glock21.py -- OUT_DIR

Imports what build_glock21.py wrote, places the parts at glock21_points.json the way the engine does (offset, then
rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the right side at the
reference photo's scale for the outline check, both sides, 3/4 views, the slide back, the magazine fitted and alone,
GoM's pistol parts at their points (Beretta mount with a sight, the underbarrel lights and a laser, the .45 mount
device with the P45), and GoM's Glock 17 and USP at the same scale.

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
POINTS = json.load(open(os.path.join(HERE, "glock21_points.json")))
K = 0.000603
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')       # GoM's pistols (and this one) are modelled upside down


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


GOM_PARTS = {  # name: (fbx, texture folder, point)
    "Beretta_Mount": ("rails", "rails", "rail_up"), "PL4_Sight": ("scopes", "scopes", "scope"),
    "PS1_Sight": ("scopes", "scopes", "scope"), "LP_Light": ("pointers", "pointers", "underbarrel"),
    "TL_Light": ("pointers", "pointers", "underbarrel"), "PJ-3_Laser": ("pointers", "pointers", "underbarrel"),
    "Muzzle_Mount_Device": ("muzzles", "muzzles", "canon"), "P45_Suppressor": ("suppressors", "suppressors", "canon"),
}


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

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_GLOCK21.fbx"), os.path.join(TEX, "GLOCK21.png"))
    body, slide = gun["GLOCK21_BODY"], gun["GLOCK21_SLIDE"]
    n = "45Magazine13_GLOCK21"
    mag = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx"),
               os.path.join(TEX, n + ".png"), keep=n)[n]
    gom = {}
    if GOM:
        for n, (cat, tex, _) in GOM_PARTS.items():
            gom.update(load(os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
                            os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (tex, n)), keep=n))

    def state(with_mag=True, fired=False, extra=()):
        place(body)
        place(slide, POINTS["slide_fired"] if fired else None)
        objs = [body, slide]
        if with_mag:
            place(mag)
            objs.append(mag)
        for n in extra:
            if n in gom:
                place(gom[n], POINTS[GOM_PARTS[n][2]])
                objs.append(gom[n])
        show_only(objs)

    right, left = (1, 0, 0), (-1, 0, 0)          # the camera looks along these: (1, 0, 0) sees the gun's right side
    q_left = (-0.62, -0.5, -0.6)
    q_right = (0.7, -0.45, -0.55)
    c = up(104.5, 67.0)
    state()
    # right side at the photo's scale: 240 mm across 1200 px, centred on photo (104.5, 67)
    render("right_photo", right, c, 240 * K, 1200, 900)
    json.dump({"right_photo": {"centre_mm": [104.5, 67.0], "px_per_mm": 1200 / 240.0, "size": [1200, 900]}},
              open(os.path.join(OUT, "cameras.json"), "w"))
    render("left", left, c, 240 * K, 1200, 900)
    render("q_left", q_left, c, 250 * K, 1200, 900)
    render("q_right", q_right, c, 250 * K, 1200, 900)
    render("top", (0, 0, -1), up(104.5, 0.0) * Vector((0, 1, 0)), 240 * K, 1200, 300)
    render("front", (0, -1, 0), up(0.0, 67.0) * Vector((0, 0, 1)), 160 * K, 500, 600)
    render("back", (0, 1, 0), up(0.0, 67.0) * Vector((0, 0, 1)), 160 * K, 500, 600)
    state(fired=True)
    render("fired_q", q_right, c, 250 * K, 1200, 900)
    state(with_mag=False)
    render("nomag_under", (0.25, -0.2, 0.95), c, 250 * K, 1000, 800)
    place(mag)
    show_only([mag])
    render("mag_alone", right, up(165.0, 55.0), 150 * K, 500, 700)
    render("mag_q", q_left, up(165.0, 55.0), 150 * K, 500, 700)
    if gom:
        state(extra=("Beretta_Mount", "PL4_Sight", "LP_Light"))
        render("gom_right", right, up(90.0, 80.0), 300 * K, 1300, 1000)
        render("gom_q", q_left, up(90.0, 80.0), 300 * K, 1300, 1000)
        state(extra=("Muzzle_Mount_Device", "P45_Suppressor", "TL_Light"))
        render("supp_right", right, up(30.0, 80.0), 380 * K, 1500, 900)
        state(extra=("PJ-3_Laser", "Beretta_Mount", "PS1_Sight"))
        render("laser_right", right, up(70.0, 85.0), 280 * K, 1200, 900)
        # GoM's Glock 17 and USP next to it at the same scale, right side
        for name, tex, mag_n in (("GLOCK17", "GLOCK17", "9x19Magazine17_Glock"), ("USP", "USP", None)):
            other = load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % name),
                         os.path.join(GOM, "textures/weapons/firearms/pistols/%s.png" % tex))
            objs = list(other.values())
            if mag_n:
                objs += list(load(os.path.join(GOM, "models_X/weapons/magazines/pistols.fbx"),
                                  os.path.join(GOM, "textures/weapons/magazines/pistols/%s.png" % mag_n),
                                  keep=mag_n).values())
            for o in objs:
                place(o)
            show_only(objs)
            render("gom_%s_right" % name.lower(), right, Vector((0.0, 0.06, 0.0)), 0.21, 900, 700)
            for o in objs:
                o.hide_render = True
                o.name = "done_" + o.name
        state()
        render("glock21_right", right, Vector((0.0, 0.06, 0.0)), 0.21, 900, 700)


main()
