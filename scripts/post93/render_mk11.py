"""Review renders of the Mk 11 Mod 0 build_mk11.py exported (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_mk11.py -- OUT_DIR

The bare gun (its rails and folded sights) from both sides and 3/4, and fitted the way the game draws parts at the
gun's points (approximation: the part models' own points are not applied, as render_mdr.py): GoM's LR4X scope, its
bipod folded and deployed, a foregrip, a light and a laser, the 7.62x51mm mount device and SOCOM762-RC, the main
mod's KAC 20 and Post-93's PMAG 20; GoM's AR15 and the main mod's SR-25 at the same scale. Game space is Blender's,
the mirror image of what the game shows.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "mk11_points.json")))
SR25 = json.load(open(os.path.join(HERE, "..", "sr25_points.json")))
AR_TEX = f"{GOM}/textures/weapons/firearms/assault_rifles/AR15.png"
P93TEX = os.path.join(P93, "textures/weapons/GunsOfTienPost93")


def load(path, texture, keep=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    m = bpy.data.materials.new(os.path.basename(texture))
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    objs = {}
    for o in set(bpy.data.objects) - before:
        n = o.name.split(".")[0]
        if o.type != 'MESH' or (keep and n not in keep):
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        o.name = n + "_" + os.path.basename(path)[:12]
        objs[n] = o
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


def render(name, direction, centre, size, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = size
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
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam
    gun = load(os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_MK11.fbx"), AR_TEX)
    body, bolt, handle = gun["MK11_BODY"], gun["MK11_BOLT"], gun["MK11_CHARGING_HANDLE"]
    kac = load(os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx"),
               f"{GOM}/textures/weapons/magazines/assault_rifles/556x45Magazine20_STANAG.png")["762x51Magazine20_SR25"]
    pmag = load(os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx"),
                os.path.join(P93TEX, "762x51Magazine20_PMAG.png"), keep=["762x51Magazine20_PMAG"])["762x51Magazine20_PMAG"]
    scar = os.path.join(P93, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx")
    supp = load(scar, os.path.join(P93TEX, "SCARH_Suppressor.png"), keep=["SCARH_Suppressor"])["SCARH_Suppressor"]
    mount = load(scar, os.path.join(P93TEX, "SCARH_Muzzle_Mount_Device.png"),
                 keep=["SCARH_Muzzle_Mount_Device"])["SCARH_Muzzle_Mount_Device"]
    parts = {}
    for cat, name in (("scopes", "LR4X_Scope"), ("scopes", "LR10X_Scope"), ("scopes", "LRX12X_Scope"), ("bipods", "Bipod_Deployed"), ("bipods", "Bipod_Folded"),
                      ("foregrips", "MKC_Foregrip"), ("pointers", "SR7_Light"), ("pointers", "AimRight_Laser")):
        try:
            parts[name] = load(f"{GOM}/models_X/weapons/parts/{cat}.fbx",
                               f"{GOM}/textures/weapons/parts/{cat}/{name}.png", keep=[name])[name]
        except Exception as e:                                   # noqa: BLE001
            print("skip", name, e)

    def state(mag=kac, extra=(), can=False, fired=False, racked=False):
        place(body)
        place(bolt, PTS["bolt_fired"] if fired else None)
        place(handle, PTS["charging_handle_open"] if racked else None)
        place(mag, PTS["magazine"])
        shown = [body, bolt, handle, mag]
        for name, point in extra:
            if name in parts:
                place(parts[name], PTS[point])
                shown.append(parts[name])
        if can:
            place(mount, PTS["canon"])
            place(supp, PTS["canon"])
            shown += [mount, supp]
        show_only(shown)

    W, H, SIZE = 2000, 700, 0.8
    centre = Vector((0.0, 0.18, 0.0))
    left, right = (-1, 0, 0), (1, 0, 0)
    state()
    render("MK11_left", left, centre, SIZE, W, H)
    render("MK11_right", right, centre, SIZE, W, H)
    render("MK11_q", (-0.62, -0.5, -0.45), centre, SIZE, W, int(H * 1.3))
    render("MK11_hg_q", (-0.55, -0.45, -0.7), Vector((0.0, 0.2, 0.02)), 0.3, 1200, 800)
    state(mag=pmag, extra=[("LR4X_Scope", "scope"), ("Bipod_Folded", "bipod")], can=True)
    render("MK11_sniper_left", left, centre + Vector((0, 0.06, 0)), SIZE + 0.1, W, H)
    state(extra=[("LR4X_Scope", "scope"), ("Bipod_Deployed", "bipod")], can=True)
    render("MK11_bipod_left", left, centre + Vector((0, 0.06, -0.03)), SIZE + 0.1, W, int(H * 1.2))
    state(extra=[("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"), ("AimRight_Laser", "laser_right")])
    render("MK11_tactical_q", (0.62, -0.5, -0.45), centre, SIZE, W, int(H * 1.3))
    render("MK11_tactical_left", left, centre, SIZE, W, H)
    state(mag=pmag, extra=[("LRX12X_Scope", "scope"), ("Bipod_Deployed", "bipod")], can=True)
    render("MK11_12x_left", left, centre + Vector((0, 0.06, -0.03)), SIZE + 0.1, W, int(H * 1.2))
    render("MK11_12x_q", (-0.62, -0.5, -0.45), centre + Vector((0, 0.06, 0)), SIZE + 0.1, W, int(H * 1.3))
    state(extra=[("LR10X_Scope", "scope"), ("Bipod_Folded", "bipod")])
    render("MK11_10x_left", left, centre, SIZE, W, H)
    state(fired=True, racked=True)
    render("MK11_racked_right", right, Vector((0.0, 0.05, 0.0)), 0.3, 1200, 700)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    g = load(f"{GOM}/models_X/weapons/firearms/AR15.fbx", AR_TEX)
    for o in g.values():
        place(o)
    show_only(list(g.values()))
    render("gom_AR15", left, centre, SIZE, W, H)
    s = load(os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_SR25.fbx"), AR_TEX)
    shown = [o for n, o in s.items() if "DEPLOYED" not in n]
    for o in shown:
        place(o)
    show_only(shown)
    render("sr25", left, centre, SIZE, W, H)


main()
