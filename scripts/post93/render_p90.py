"""Review renders of the exported FN P90 TR assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_p90.py -- OUT_DIR

Imports the FBX files and textures build_p90.py wrote, places the parts at the attachment points of p90_points.json
the way the engine does (offset, then rotateXYZ in degrees, game space), and renders orthographic Workbench views
into OUT_DIR: views like the reference photos, the right side at the photo's scale for the outline check, the
parts, and GoM's FAMAS and MP5 at the same scale. make_p90_art.py assembles them into docs/post93_p90_preview.png.
Game space is used as Blender world space (data z is flipped back).
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
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
POINTS = json.load(open(os.path.join(HERE, "p90_points.json")))
K = 0.00072
L0, H0 = POINTS["_extras"]["photo_origin_mm"]

# GoM's magazine points (scripts/MarzWeapons/models/weapons/smgs.txt and assault_rifles.txt)
MP5_MAG = {"offset": [0.0, 0.1191, 0.0377], "rotate": [10.2946, 0.0, 0.0]}


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


def place(o, point=None):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
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


def render(name, direction, centre, scale, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:                                   # top / bottom view: muzzle to the right
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(90.0))
    cam.data.ortho_scale = scale
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
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx"), os.path.join(TEX, "P90TR.png"))
    body, bolt = gun["P90TR_BODY"], gun["P90TR_BOLT"]
    mag = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx"),
               os.path.join(TEX, "57x28Magazine50_P90.png"))["57x28Magazine50_P90"]
    parts = {}
    for n in ("P90_Suppressor", "P90_Muzzle_Mount_Device"):
        parts.update(load(os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx"),
                          os.path.join(TEX, n + ".png"), keep=n))
    supp, mount = parts["P90_Suppressor"], parts["P90_Muzzle_Mount_Device"]

    def gun_state(mag_on=True, supp_on=False, fired=False):
        place(body)
        place(bolt, POINTS["bolt_fired"] if fired else None)
        objs = [body, bolt]
        if mag_on:
            place(mag, POINTS["magazine"])
            objs.append(mag)
        if supp_on:
            place(mount, POINTS["canon"])
            place(supp, POINTS["canon"])
            objs += [mount, supp]
        show_only(objs)

    right, left, top, under = (1, 0, 0), (-1, 0, 0), (0, 0, -1), (0, 0, 1)
    like2 = (0.82, -0.42, -0.3)          # the second photo: right side, from a little ahead and above
    like3 = (-0.8, 0.5, -0.3)            # the third: left side from behind and above
    c = (0.0, (L0 - 250.0) * K, (90.0 - H0) * K)
    gun_state()
    render("photo2", like2, c, 0.40, 1200, 700)
    render("photo3", like3, c, 0.40, 1200, 700)
    render("left", left, c, 0.40, 1200, 560)
    render("top", top, (0, c[1], 0), 0.40, 1200, 260)
    render("under", under, (0, c[1], 0), 0.40, 1200, 260)
    render("front", (0, -1, 0), (0, 0, c[2]), 0.16, 420, 420)
    # right side at the photo's scale: 520 mm across 1777 px = 3.418 px per mm, centred on photo (250, 90)
    render("right_photo", right, c, 520 * K, 1777, 700)
    json.dump({"right_photo": {"centre_mm": [250.0, 90.0], "px_per_mm": 1777 / 520.0, "size": [1777, 700]}},
              open(os.path.join(OUT, "cameras.json"), "w"))
    gun_state(fired=True)
    render("bolt_fired", like2, c, 0.40, 1200, 700)
    gun_state(mag_on=False)
    render("nomag", like2, c, 0.40, 1200, 700)
    gun_state(supp_on=True)
    render("supp_right", right, (0, c[1] + 0.05, c[2]), 0.52, 1400, 560)
    render("supp_q34", like2, (0, c[1] + 0.05, c[2]), 0.52, 1400, 800)
    gun_state(mag_on=False)
    place(mount, POINTS["canon"])
    show_only([body, bolt, mount])
    render("mount_q34", like2, (0, 0.15, POINTS["canon"]["offset"][2]), 0.12, 500, 400)

    place(mag)
    show_only([mag])
    render("mag_q34", like2, (0, -0.097, 0.008), 0.22, 600, 300)
    place(supp)
    place(mount)
    show_only([supp, mount])
    render("parts_q34", like2, (0, 0.062, 0), 0.15, 600, 300)

    # GoM's FAMAS and MP5 (with their magazines) at the same scale, left side
    if GOM:
        famas = load(os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"),
                     os.path.join(GOM, "textures/weapons/firearms/assault_rifles/FAMAS.png"))
        mp5 = load(os.path.join(GOM, "models_X/weapons/firearms/MP5.fbx"),
                   os.path.join(GOM, "textures/weapons/firearms/smgs/MP5.png"))
        mp5mag = load(os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
                      os.path.join(GOM, "textures/weapons/magazines/smgs/9x19Magazine30_MP5.png"),
                      keep="9x19Magazine30_MP5")["9x19Magazine30_MP5"]
        for o in list(famas.values()) + list(mp5.values()):
            place(o)
        place(mp5mag, MP5_MAG)
        show_only(list(famas.values()))
        render("gom_famas", left, (0, 0.03, 0.0), 0.62, 1200, 420)
        show_only(list(mp5.values()) + [mp5mag])
        render("gom_mp5", left, (0, 0.03, 0.0), 0.62, 1200, 420)
        gun_state()
        render("p90_same", left, (0, 0.03, 0.0), 0.62, 1200, 420)

    magazine_views(gun_state, body, bolt, mag, right, left, like2, like3)
    if GOM:
        attachment_views(gun_state, right, left, like2, like3, c)
        ammo_views()


def magazine_views(gun_state, body, bolt, mag, right, left, like2, like3):
    """The magazine alone from each side, and seated on the gun seen from above."""
    place(mag)
    show_only([mag])
    mc = (0.0, -0.0976, 0.0087)
    render("mag_right", right, mc, 0.21, 1200, 200)
    render("mag_left", left, mc, 0.21, 1200, 200)
    render("mag_top", (0, 0, -1), (0.0, -0.0976, 0.0), 0.21, 1200, 200)
    render("mag_like2", like2, mc, 0.23, 1000, 420)
    render("mag_like3", like3, mc, 0.23, 1000, 420)
    gun_state()
    render("mag_seated", (0.55, -0.35, -0.76), (0.0, -0.01, 0.02), 0.44, 1000, 620)


GOM_PARTS = {  # name: (fbx, texture folder, attachment point on the gun)
    "Aimpoint_Sight": ("scopes", "scope"), "EXPS3_Sight": ("scopes", "scope"), "ReflexS2_Sight": ("scopes", "scope"),
    "ElcanX2_Scope": ("scopes", "scope"), "BrightPoint-5_Light": ("pointers", "light_left"),
    "SR7_Light": ("pointers", "light_left"), "AimRight_Laser": ("pointers", "laser_right"),
    "LRX-7_Laser": ("pointers", "laser_right"),
}


def attachment_views(gun_state, right, left, like2, like3, c):
    """Our suppressor and mount, and a selection of GoM's optics, lights and lasers at the P90's points."""
    parts = {}
    for n, (cat, _) in GOM_PARTS.items():
        parts.update(load(os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
                          os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (cat, n)), keep=n))
    supp = bpy.data.objects["P90_Suppressor"]
    mount = bpy.data.objects["P90_Muzzle_Mount_Device"]
    base = [o for o in bpy.data.objects if o.name in ("P90TR_BODY", "P90TR_BOLT", "57x28Magazine50_P90")]

    def fit(names, supp_on=False):
        gun_state(supp_on=supp_on)
        objs = list(base) + ([supp, mount] if supp_on else [])
        for n in names:
            place(parts[n], POINTS[GOM_PARTS[n][1]])
            objs.append(parts[n])
        show_only(objs)

    sc_c = (0.0, (L0 - 140.0) * K, (170.0 - H0) * K)
    for n in ("Aimpoint_Sight", "EXPS3_Sight", "ReflexS2_Sight", "ElcanX2_Scope"):
        fit([n])
        render("opt_" + n, right, sc_c, 0.22, 700, 360)
    fit(["BrightPoint-5_Light", "AimRight_Laser"])
    render("acc_left", left, (0.0, (L0 - 110.0) * K, (130.0 - H0) * K), 0.24, 800, 420)
    render("acc_right", right, (0.0, (L0 - 110.0) * K, (130.0 - H0) * K), 0.24, 800, 420)
    render("acc_front", (0, -1, 0), (0.0, 0.0, (110.0 - H0) * K), 0.11, 520, 520)
    fit(["SR7_Light", "LRX-7_Laser"])
    render("acc2_like2", like2, (0.0, (L0 - 110.0) * K, (130.0 - H0) * K), 0.26, 800, 520)
    fit(["Aimpoint_Sight", "BrightPoint-5_Light", "AimRight_Laser"], supp_on=True)
    render("full_like2", like2, (0, c[1] + 0.05, c[2]), 0.52, 1400, 820)
    render("full_like3", like3, (0, c[1] + 0.05, c[2]), 0.52, 1400, 820)
    # suppressor and mount alone and fitted, side by side
    place(supp)
    place(mount)
    show_only([mount])
    render("mount_alone", like2, (0, 0.017, 0), 0.06, 500, 320)
    show_only([supp])
    render("supp_alone", right, (0, 0.062, 0), 0.15, 900, 260)
    gun_state(mag_on=True)
    place(mount, POINTS["canon"])
    show_only(list(base) + [mount])
    render("mount_fitted", right, (0, 0.165, POINTS["canon"]["offset"][2]), 0.09, 600, 340)


def ammo_views():
    """5.7x28mm rounds (GoM's mesh, our textures) and boxes (vanilla's handgun box), at the model scripts' scales."""
    game = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/"
                                                "Project Zomboid.app/Contents/Java/media"),
                             "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media") if os.path.isdir(p)))
    tex = os.path.join(MEDIA, "textures/worlditems/GunsOfTienPost93")
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            o.hide_render = True
    for v in ("SS190", "SB193", "SS197SR"):
        r = load(os.path.join(GOM, "models_X/worlditems/Ammunition/Rounds.fbx"),
                 os.path.join(tex, "Rounds/GunsOfTienPost93_57x28_Round_%s.png" % v), keep="57x28_Round")
        rnd = r["57x28_Round"]
        rnd.name = "round_" + v
        rnd.matrix_world = Matrix.Diagonal((0.015, 0.015, 0.015, 1.0)) @ rnd.matrix_world
        bpy.context.view_layer.update()
        show_only([rnd])
        lo = [rnd.matrix_world @ Vector(cn) for cn in rnd.bound_box]
        mid = sum(lo, Vector()) / 8
        size = max((max(p[i] for p in lo) - min(p[i] for p in lo)) for i in range(3))
        render("round_" + v, (0.6, -0.25, -0.75), mid, size * 1.25, 400, 400)
        b = load(os.path.join(game, "models_X/WorldItems/HandGunAmmoBox.FBX"),
                 os.path.join(tex, "Boxes/GunsOfTienPost93_57x28_Box_%s.png" % v))
        box = list(b.values())
        for o in box:
            o.name = "box_%s_%s" % (v, o.name)
            o.matrix_world = Matrix.Diagonal((0.4, 0.4, 0.4, 1.0)) @ o.matrix_world
        bpy.context.view_layer.update()
        show_only(box)
        lo = [o.matrix_world @ Vector(cn) for o in box for cn in o.bound_box]
        mid = sum(lo, Vector()) / len(lo)
        size = max((max(p[i] for p in lo) - min(p[i] for p in lo)) for i in range(3))
        render("box_" + v, (0.6, -0.55, -0.6), mid, size * 1.35, 400, 400)


main()
