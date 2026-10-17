"""Review renders of the exported MP7A1 assets, read back from the FBX files (Blender 5.2, headless).

    Blender -b --factory-startup -P scripts/post93/render_mp7.py -- OUT_DIR

Imports the FBX files and textures build_mp7.py wrote, places the parts at the attachment points of
mp7_points.json the way the engine does (offset, then rotateXYZ in degrees, game space), and renders orthographic
Workbench views into OUT_DIR, plus GoM's MP5 at the same scale for the overlay. make_mp7_art.py assembles them
into docs/post93_mp7_preview.png. Game space is used as Blender world space (data z is flipped back).
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
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p))
OUT = sys.argv[sys.argv.index("--") + 1]
POINTS = json.load(open(os.path.join(HERE, "mp7_points.json")))
POINTS_A2 = json.load(open(os.path.join(HERE, "mp7a2_points.json")))

# GoM's MP5 points (scripts/MarzWeapons/models/weapons/smgs.txt)
MP5_MAG = {"offset": [0.0, 0.1191, 0.0377], "rotate": [10.2946, 0.0, 0.0]}


def load(path, texture):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    img = bpy.data.images.load(texture, check_existing=True)
    m = bpy.data.materials.new(os.path.basename(texture))
    m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    objs = {}
    for o in set(bpy.data.objects) - before:
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name] = o
    return objs


# The MP7 is held like a pistol and so modelled upside down (mp7_points.json "_notes"): the gun and everything placed
# on it are turned back upright for display; loose magazines, parts and GoM's MP5 are shown as they are.
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y') if POINTS["_extras"].get("handgun_hold") else Matrix.Identity(4)


def place(o, point=None, gun=True):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = (UPRIGHT if gun else Matrix.Identity(4)) @ mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))
    o.hide_render = False


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


def render(name, direction, centre, scale, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    up = 'Y'
    cam.rotation_euler = d.to_track_quat('-Z', up).to_euler()
    if abs(d.z) > 0.99:                                   # top view: muzzle to the right
        cam.rotation_euler = (0.0, 0.0, math.radians(90.0))
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

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx"), os.path.join(TEX, "MP7A1.png"))
    mags = {}
    for r in (20, 30, 40, 60):
        o = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx"),
                 os.path.join(TEX, "46x30Magazine%d_MP7.png" % r))
        for name, ob in o.items():
            if name.startswith("46x30Magazine%d_MP7" % r):
                mags[r] = ob
            else:
                bpy.data.objects.remove(ob)
    parts = {}
    for n in ("MP7_Suppressor", "MP7_Muzzle_Mount_Device"):
        o = load(os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx"), os.path.join(TEX, n + ".png"))
        for name, ob in o.items():
            if name.startswith(n):
                parts[n] = ob
            else:
                bpy.data.objects.remove(ob)
    body, bolt, stock, fgrip = gun["MP7A1_BODY"], gun["MP7A1_BOLT"], gun["MP7A1_STOCK"], gun["MP7A1_FOREGRIP"]
    body2 = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_MP7A2.fbx"),
                 os.path.join(TEX, "MP7A2.png"))["MP7A2_BODY"]
    stub = load(os.path.join(GOM, "models_X/weapons/parts/foregrips.fbx"),
                os.path.join(GOM, "textures/weapons/parts/foregrips/Stub_Foregrip.png"))
    for name, ob in list(stub.items()):
        if name != "Stub_Foregrip":
            bpy.data.objects.remove(ob)
    stub = bpy.data.objects["Stub_Foregrip"]
    supp, mount = parts["MP7_Suppressor"], parts["MP7_Muzzle_Mount_Device"]

    mp5 = load(os.path.join(GOM, "models_X/weapons/firearms/MP5.fbx"),
               os.path.join(GOM, "textures/weapons/firearms/smgs/MP5.png"))
    mp5mag = load(os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
                  os.path.join(GOM, "textures/weapons/magazines/smgs/9x19Magazine30_MP5.png"))
    for name, ob in list(mp5mag.items()):
        if name != "9x19Magazine30_MP5":
            bpy.data.objects.remove(ob)
    mp5mag = bpy.data.objects["9x19Magazine30_MP5"]
    for o in list(mp5.values()) + [mp5mag]:
        place(o, MP5_MAG if o is mp5mag else None, gun=False)

    side = (-1, 0, 0)                     # looking along -X: the gun's left side, muzzle to the right
    right = (1, 0, 0)
    q34 = (-0.75, -0.55, -0.42)           # 3/4 front left, from above
    top = (0, 0, -1)

    def gun_state(stock_in, mag, supp_on, grip_down=False, a2=False, vgrip=False):
        place(body2 if a2 else body)
        place(bolt)
        place(stock, POINTS["stock_folded"] if stock_in else None)
        objs = [body2 if a2 else body, bolt, stock]
        if a2:
            if vgrip:                                     # GoM's Stub Foregrip on the A2's bottom rail
                place(stub, POINTS_A2["foregrip"])
                objs.append(stub)
        else:
            place(fgrip, POINTS["foregrip_deployed"] if grip_down else None)
            objs.append(fgrip)
        if mag:
            place(mags[mag], POINTS["magazine"])
            objs.append(mags[mag])
        if supp_on:
            place(mount, POINTS["canon"])
            place(supp, POINTS["canon"])
            objs += [mount, supp]
        show_only(objs)

    c_in = (0, 0.06, -0.02)
    c_out = (0, -0.03, -0.02)
    gun_state(True, 30, False)
    render("q34_in", q34, c_in, 0.42, 900, 600)
    render("side_in", side, c_in, 0.42, 900, 600)
    render("right_in", right, c_in, 0.42, 900, 600)
    render("top_in", top, (0, 0.06, 0), 0.42, 900, 300)
    gun_state(False, 40, False, grip_down=True)
    render("side_out", side, c_out, 0.62, 1200, 600)
    render("q34_out", q34, c_out, 0.62, 1200, 600)
    gun_state(False, 20, True)
    render("side_supp", side, (0, 0.03, -0.02), 0.62, 1200, 600)
    render("q34_supp", q34, (0, 0.03, -0.02), 0.62, 1200, 600)
    gun_state(True, 60, False)
    render("side_drum", side, (0, 0.05, -0.05), 0.45, 900, 600)
    render("q34_drum", q34, (0, 0.05, -0.05), 0.45, 900, 600)
    gun_state(True, 30, False)
    show_only([body])
    render("body_only_in", side, c_in, 0.42, 900, 600)
    # MP7A2
    gun_state(True, 30, False, a2=True)
    render("a2_side_in", side, c_in, 0.42, 900, 600)
    render("a2_q34_in", q34, c_in, 0.42, 900, 600)
    render("a2_right_in", right, c_in, 0.42, 900, 600)
    gun_state(False, 40, False, a2=True, vgrip=True)
    render("a2_side_grip", side, c_out, 0.62, 1200, 600)
    render("a2_q34_grip", q34, c_out, 0.62, 1200, 600)

    # magazines and parts on their own
    for r in (20, 30, 40, 60):
        place(mags[r], gun=False)
        show_only([mags[r]])
        render("mag%d" % r, side, (0, 0, -0.085), 0.2, 400, 400)
        render("mag%d_q34" % r, q34, (0, 0, -0.085), 0.2, 400, 400)
    place(supp, gun=False)
    place(mount, gun=False)
    show_only([supp, mount])
    render("parts_side", side, (0, 0.06, 0), 0.18, 600, 200)
    render("parts_q34", q34, (0, 0.06, 0), 0.18, 600, 300)

    # Overlay: MP7 (stock deployed, 30 magazine) and GoM's MP5 (stock deployed, 30 magazine), same camera.
    gun_state(False, 30, False)
    render("overlay_mp7", side, (0, 0.02, -0.01), 0.62, 1240, 620)
    show_only(list(mp5.values()) + [mp5mag])
    render("overlay_mp5", side, (0, 0.02, -0.01), 0.62, 1240, 620)
    # left side at the reference photo's scale (docs/mp7_2.png: 888 px for 415 mm), stock in, 20 rounds
    L0, H0 = POINTS["_extras"]["photo_origin_mm"]
    ppm, cL, cH = 888 / 415.0, 200.0, 95.0
    gun_state(True, 20, False)
    render("left_photo", side, (0, (L0 - cL) * 0.00072, (cH - H0) * 0.00072), 1400 / ppm * 0.00072, 1400, 600)
    json.dump({"overlay": {"centre": [0.02, -0.01], "scale": 0.62, "size": [1240, 620]},
               "left_photo": {"centre_mm": [cL, cH], "px_per_mm": ppm, "size": [1400, 600]}},
              open(os.path.join(OUT, "cameras.json"), "w"))


main()
