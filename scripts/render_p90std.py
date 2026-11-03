"""Review renders of the P90 with its ring sight (main mod), read back from the exported FBX files (Blender 5.2,
headless).

    blender -b --factory-startup -P scripts/render_p90std.py -- OUT_DIR

Places the gun's nodes (turned: held like a pistol), our optional rails, the P90's magazine and muzzle parts and a
selection of GoM's optics, lights and lasers at the points of p90std_points.json the way the engine does (offset, then
rotateXYZ, game space), turns everything back upright and renders orthographic Workbench views into OUT_DIR: the sides,
top and front, the ring sight up close, the right side with the side rails at the Commons photo's scale and centre
(`right_photo`, for make_p90std_art.py's outline check), the rails bare and fitted out, the handles back, and the P90 TR
at the same scale. make_p90std_art.py assembles them into docs/p90_preview.png. Game space is Blender world space (data
z flipped).
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
# the P90's magazine, mount device and SP90 are the main mod's (moved 2026-11-03 for its P90, same names and paths)
MAIN_MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
MAIN_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
K = 0.000603
OUT = sys.argv[sys.argv.index("--") + 1]
POINTS = json.load(open(os.path.join(HERE, "p90std_points.json")))
TR = json.load(open(os.path.join(HERE, "post93", "p90_points.json")))
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
GOM_PARTS = {  # name: (fbx, point)
    "Aimpoint_Sight": ("scopes", "scope"), "EXPS3_Sight": ("scopes", "scope"), "ElcanX2_Scope": ("scopes", "scope"),
    "TA28_Scope": ("scopes", "scope"), "SR7_Light": ("pointers", "light_left"),
    "LRX-7_Laser": ("pointers", "laser_right"),
    "BrightPoint-5_Light": ("pointers", "light_left"), "AimRight_Laser": ("pointers", "laser_right"),
    "MKC_Foregrip": ("foregrips", "foregrip"), "MK2_Foregrip": ("foregrips", "foregrip"),
    "Stub_Foregrip": ("foregrips", "foregrip"),
}


def load(path, texture, keep=None):
    """Import an FBX, give every object a material showing `texture` (render_p90.py's)."""
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


TURNED = Matrix.Rotation(math.pi, 4, 'Y')         # the P90 TR is modelled upside down (held like a pistol)


def place(o, point=None, turned=False):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = (TURNED if turned else Matrix.Identity(4)) @ mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


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

    gun = load(os.path.join(MAIN_MEDIA, "models_X/weapons/firearms/GunsOfTien_P90.fbx"),
               os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTien/P90.png"))
    body, bolt, handle = gun["P90_BODY"], gun["P90_BOLT"], gun["P90_HANDLE"]
    rails = {k: gun["P90_RAIL_" + k.upper()] for k in ("left", "right")}
    mag = load(os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx"),
               os.path.join(MAIN_TEX, "57x28Magazine50_P90.png"))["57x28Magazine50_P90"]
    parts = {}
    for n in ("P90_Suppressor", "P90_Muzzle_Mount_Device"):
        parts.update(load(os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx"),
                          os.path.join(TEX, n + ".png"), keep=n))
    supp, mount = parts["P90_Suppressor"], parts["P90_Muzzle_Mount_Device"]
    gom = {}
    if GOM:
        for n, (cat, _) in GOM_PARTS.items():
            gom.update(load(os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
                            os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (cat, n)), keep=n))

    def state(mag_on=True, supp_on=False, racked=False, sides=(), extra=()):
        """Everything placed at the turned model's points, then turned back upright for display."""
        place(body, None, turned=True)
        place(bolt, POINTS["bolt_fired"] if racked else None, turned=True)
        place(handle, POINTS["handle_back"] if racked else None, turned=True)
        objs = [body, bolt, handle]
        for k in sides:
            place(rails[k], POINTS["rail_" + k], turned=True)
            objs.append(rails[k])
        if mag_on:
            place(mag, POINTS["magazine"], turned=True)
            objs.append(mag)
        if supp_on:
            place(mount, POINTS["canon"], turned=True)
            place(supp, POINTS["canon"], turned=True)
            objs += [mount, supp]
        for n in extra:
            place(gom[n], POINTS[GOM_PARTS[n][1]], turned=True)
            objs.append(gom[n])
        show_only(objs)
        return objs

    left, right = (-1, 0, 0), (1, 0, 0)
    like = (-0.72, -0.5, -0.32)
    behind = (0.75, 0.45, -0.3)
    c = (0.0, (L0 - 250.0) * K, (100.0 - H0) * K)
    state()
    render("left", left, c, 0.36, 1400, 640)
    render("right", right, c, 0.36, 1400, 640)
    render("like", like, c, 0.36, 1400, 820)
    render("behind", behind, c, 0.36, 1400, 820)
    render("top", (0, 0, -1), (0, c[1], 0), 0.36, 1400, 300)
    render("front", (0, -1, 0), (0, 0, c[2]), 0.14, 420, 420)
    sight = (0.0, (L0 - 110.0) * K, (175.0 - H0) * K)
    render("sight_like", like, sight, 0.12, 900, 640)
    render("sight_behind", (0.45, 0.85, -0.3), sight, 0.12, 900, 640)
    # looking into the sight from behind and from ahead: its square window
    into = (0.0, (L0 - 110.0) * K, (190.0 - H0) * K)
    render("sight_rear", (0.0, 1.0, 0.0), into, 0.09, 600, 600)      # the camera behind, looking toward the muzzle
    render("sight_front", (0.0, -1.0, 0.0), into, 0.09, 600, 600)
    # the mirrored Commons photo: 3.714 px per mm, its centre photo L 254.0, H 105.0
    state(sides=("left", "right"))
    render("right_photo", right, (0.0, (L0 - 254.0) * K, (105.0 - H0) * K), 2127 / 3.714 * K, 2127, 1160)
    state(sides=("left", "right"))
    render("rails_like", like, c, 0.36, 1400, 820)
    render("rails_behind", behind, c, 0.36, 1400, 820)
    state(racked=True)
    render("racked", like, c, 0.36, 1400, 820)
    if GOM:
        state(supp_on=True, sides=("left", "right"), extra=("SR7_Light", "AimRight_Laser"))
        render("fitted_like", like, (0, c[1] + 0.03, c[2]), 0.46, 1400, 860)
        render("fitted_left", left, (0, c[1] + 0.03, c[2]), 0.46, 1400, 560)
        render("fitted_right", right, (0, c[1] + 0.03, c[2]), 0.46, 1400, 560)
        state(sides=("left", "right"), extra=("BrightPoint-5_Light", "LRX-7_Laser"))
        render("fitted2_like", like, c, 0.38, 1400, 860)
    tr = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx"),
              os.path.join(TEX, "P90TR.png"))
    for o in tr.values():
        place(o, None, turned=True)
    place(mag, TR["magazine"], turned=True)
    show_only(list(tr.values()) + [mag])
    render("tr_left", left, c, 0.36, 1400, 640)


main()
