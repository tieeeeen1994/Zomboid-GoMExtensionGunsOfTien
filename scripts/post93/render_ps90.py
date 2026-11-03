"""Review renders of the PS90 Carbine, read back from the exported FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_ps90.py -- OUT_DIR

Places the gun's nodes, the P90's magazine and muzzle parts and a selection of GoM's optics, foregrips, lights and
lasers at the points of ps90_points.json the way the engine does (offset, then rotateXYZ, game space) and renders
orthographic Workbench views into OUT_DIR: the sides, top, bottom and front, the right side at the user's photo's
scale and centre (`right_photo`, for make_ps90_art.py's outline check), fitted out, the handles back, and the P90 TR
beside it at one scale.
make_ps90_art.py assembles them into docs/post93_ps90_preview.png. Game space is Blender world space (data z flipped).
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
# the P90's magazine, mount device and SP90 are the main mod's (moved 2026-11-03 for its P90, same names and paths)
MAIN_MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
MAIN_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
K = 0.000603
OUT = sys.argv[sys.argv.index("--") + 1]
POINTS = json.load(open(os.path.join(HERE, "ps90_points.json")))
TR = json.load(open(os.path.join(HERE, "p90_points.json")))
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
GOM_PARTS = {  # name: (fbx, point)
    "Aimpoint_Sight": ("scopes", "scope"), "EXPS3_Sight": ("scopes", "scope"), "ElcanX2_Scope": ("scopes", "scope"),
    "TA28_Scope": ("scopes", "scope"), "SR7_Light": ("pointers", "light_left"),
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

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_PS90.fbx"),
               os.path.join(TEX, "PS90.png"))
    body, bolt, handle = gun["PS90_BODY"], gun["PS90_BOLT"], gun["PS90_HANDLE"]
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

    def state(mag_on=True, supp_on=False, racked=False, extra=()):
        place(body)
        place(bolt, POINTS["bolt_fired"] if racked else None)
        place(handle, POINTS["handle_back"] if racked else None)
        objs = [body, bolt, handle]
        if mag_on:
            place(mag, POINTS["magazine"])
            objs.append(mag)
        if supp_on:
            place(mount, POINTS["canon"])
            place(supp, POINTS["canon"])
            objs += [mount, supp]
        for n in extra:
            place(gom[n], POINTS[GOM_PARTS[n][1]])
            objs.append(gom[n])
        show_only(objs)
        return objs

    left, right, top, under = (-1, 0, 0), (1, 0, 0), (0, 0, -1), (0, 0, 1)
    like = (-0.72, -0.5, -0.32)          # the left side from ahead and above, muzzle right
    behind = (0.75, 0.45, -0.3)          # the right side from behind and above
    c = (0.0, (L0 - 180.0) * K, (100.0 - H0) * K)
    hg = (0.0, (L0 + 30.0) * K, (95.0 - H0) * K)
    state()
    render("left", left, c, 0.43, 1400, 560)
    render("right", right, c, 0.43, 1400, 560)
    render("render_like", like, c, 0.43, 1400, 820)
    # the user's photo (1200 px, 1.672 px per mm): its centre is photo L 169.9, H 98.1 (build_ps90.py's map)
    render("right_photo", right, (0.0, (L0 - 169.94) * K, (98.09 - H0) * K), 1200 / 1.672 * K, 1200, 1200)
    render("behind", behind, c, 0.43, 1400, 820)
    render("top", top, (0, c[1], 0), 0.43, 1400, 300)
    render("under", under, (0, c[1], 0), 0.43, 1400, 300)
    render("front", (0, -1, 0), (0, 0, c[2]), 0.16, 420, 420)
    render("hg_like", like, hg, 0.17, 900, 700)
    render("hg_inside", (-0.3, -0.92, -0.25), hg, 0.12, 700, 600)
    state(racked=True)
    render("racked", like, c, 0.43, 1400, 820)
    state(supp_on=True)
    render("supp_left", left, (0, c[1] + 0.05, c[2]), 0.53, 1400, 480)
    if GOM:
        state(supp_on=True, extra=("Aimpoint_Sight", "SR7_Light", "AimRight_Laser", "MKC_Foregrip"))
        render("fitted_like", like, (0, c[1] + 0.05, c[2]), 0.53, 1400, 860)
        render("fitted_left", left, (0, c[1] + 0.05, c[2]), 0.53, 1400, 520)
        render("fitted_right", right, (0, c[1] + 0.05, c[2]), 0.53, 1400, 520)
        state(extra=("ElcanX2_Scope", "BrightPoint-5_Light", "MK2_Foregrip"))
        render("fitted2_like", like, c, 0.45, 1400, 860)
        for n in ("EXPS3_Sight", "TA28_Scope", "Stub_Foregrip"):
            state(extra=(n,))
            render("part_" + n, left, c, 0.43, 1400, 560)
    # the P90 TR (held like a pistol, turned back upright) at the same scale, left side
    tr = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx"),
              os.path.join(TEX, "P90TR.png"))
    for o in tr.values():
        place(o, None, turned=True)
    place(mag, TR["magazine"], turned=True)
    show_only(list(tr.values()) + [mag])
    render("tr_left", left, c, 0.43, 1400, 560)


main()
