"""Review renders of the exported SCAR-L / SCAR-H assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_scar.py -- OUT_DIR

Imports what build_scar.py wrote, places every part at scarl_points.json / scarh_points.json the way the engine does
(offset, then rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: each gun's
left side at its reference photo's scale (for the outline check in make_scar_art.py), the right side, 3/4 views, the
stock folded, the charging handle back, magazines, the SCAR-H's mount device and suppressor, GoM's AR mount device,
MKI suppressor and STANAG magazines on the SCAR-L, GoM's optics, foregrip, light, laser and bipod at their points, and
GoM's M4A1 and FAL at the same scale. Game space is used as Blender world space, the mirror image of what the game
shows; make_scar_art.py flips every render left-right (as make_ucp_art.py does).
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
UPRIGHT = Matrix.Identity(4)


# load / place / show_only / render: render_ucp.py's (rifles are upright, so place() never turns them)
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
    if abs(d.z) > 0.99:                                   # top / bottom view: muzzle to the right (after the flip)
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.ortho_scale = scale
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)



class R:
    load, render = staticmethod(load), staticmethod(render)
    place = staticmethod(place)

PTS = {g: json.load(open(os.path.join(HERE, g.lower() + "_points.json"))) for g in ("SCARL", "SCARH")}
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms")
PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx")
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SCARH_magazines.fbx")


def place(o, point=None):
    R.place(o, point, upright=False)


def gom(cat, name, tex_dir):
    return R.load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                  os.path.join(GOM, "textures/weapons/%s/%s.png" % (tex_dir, name)), keep=name)[name]


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

    guns = {}
    for g in ("SCARL", "SCARH"):
        objs = R.load(os.path.join(FIRE, "GunsOfTienPost93_%s.fbx" % g), os.path.join(TEX, g + ".png"))
        guns[g] = (objs[g + "_BODY"], objs[g + "_BOLT"])
    stock = R.load(PARTS, os.path.join(TEX, "SCAR_STOCK.png"), keep="SCAR_STOCK")["SCAR_STOCK"]
    supp = R.load(PARTS, os.path.join(TEX, "SCARH_Suppressor.png"), keep="SCARH_Suppressor")["SCARH_Suppressor"]
    mount = R.load(PARTS, os.path.join(TEX, "SCARH_Muzzle_Mount_Device.png"),
                   keep="SCARH_Muzzle_Mount_Device")["SCARH_Muzzle_Mount_Device"]
    hmags = {r: R.load(MAGS, os.path.join(TEX, "762x51Magazine%d_SCARH.png" % r),
                       keep="762x51Magazine%d_SCARH" % r)["762x51Magazine%d_SCARH" % r] for r in (20, 10, 50)}
    g_parts = {}
    if GOM:
        for cat, name, tex in (("magazines/assault_rifles", "556x45Magazine30_STANAG", "magazines/assault_rifles"),
                               ("magazines/assault_rifles", "556x45Magazine20_STANAG", "magazines/assault_rifles"),
                               ("parts/muzzles", "Muzzle_Mount_Device", "parts/muzzles"),
                               ("parts/suppressors", "MKI_Suppressor", "parts/suppressors"),
                               ("parts/scopes", "Aimpoint_Sight", "parts/scopes"),
                               ("parts/scopes", "ElcanX2_Scope", "parts/scopes"),
                               ("parts/foregrips", "MKC_Foregrip", "parts/foregrips"),
                               ("parts/pointers", "SR7_Light", "parts/pointers"),
                               ("parts/pointers", "AimRight_Laser", "parts/pointers"),
                               ("parts/bipods", "Bipod_Deployed", "parts/bipods")):
            try:
                g_parts[name] = gom(cat, name, tex)
            except Exception as e:                       # a texture named differently: skip that part
                print("skip", name, e)

    def state(g, mag=True, fired=False, folded=False, h_supp=False, extra=(), rounds=20):
        p = PTS[g]
        body, bolt = guns[g]
        place(body)
        place(bolt, p["bolt_fired"] if fired else None)
        place(stock, p["stock_folded"] if folded else p["stock"])
        objs = [body, bolt, stock]
        if mag:
            m = hmags[rounds] if g == "SCARH" else g_parts.get("556x45Magazine30_STANAG")
            if m is not None:
                place(m, p["magazine"])
                objs.append(m)
        if h_supp:
            place(mount, p["canon"])
            place(supp, p["canon"])
            objs += [mount, supp]
        for name, point in extra:
            o = g_parts.get(name)
            if o is not None:
                place(o, p[point])
                objs.append(o)
        show_only(objs)

    def show_only(objs):
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.hide_render = o not in objs

    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    cams = {}
    for g, length in (("SCARL", 900.0), ("SCARH", 1160.0)):
        p = PTS[g]
        k = p["_extras"]["k"]
        L0, H0 = p["_extras"]["photo_origin_mm"]
        lmid = (p["_bounds"][g + "_BODY"]["max"][1] + p["_bounds"]["SCAR_STOCK_deployed"]["min"][1]) / 2.0
        centre = Vector((0.0, lmid, 0.0))
        w = 1600
        state(g)
        R.render(g + "_left", left, centre, length * k, w, 600)
        cams[g + "_left"] = {"centre_game": [0.0, lmid, 0.0], "px_per_mm": w / length, "size": [w, 600],
                             "photo_origin_mm": [L0, H0], "k": k}
        R.render(g + "_right", right, centre, length * k, w, 600)
        R.render(g + "_q_left", q_left, centre, length * k, w, 800)
        R.render(g + "_q_right", q_right, centre, length * k, w, 800)
        R.render(g + "_top", (0, 0, -1), centre, length * k, w, 360)
        state(g, folded=True, fired=True)
        R.render(g + "_folded_q", q_right, centre, length * k, w, 800)
        R.render(g + "_folded_top", (0, 0, -1), centre, length * k, w, 360)
        state(g, mag=False)
        R.render(g + "_nomag_under", (0.25, -0.2, 0.95), centre, length * k, w, 700)
        extra = [("Aimpoint_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
                 ("AimRight_Laser", "laser_right")]
        if g == "SCARL":
            state(g, extra=extra + [("Muzzle_Mount_Device", "canon"), ("MKI_Suppressor", "canon")])
        else:
            state(g, h_supp=True, extra=[("ElcanX2_Scope", "scope"), ("Bipod_Deployed", "bipod"),
                                         ("SR7_Light", "light_left"), ("AimRight_Laser", "laser_right")])
        R.render(g + "_fitted_q", q_left, centre + Vector((0, 0.05, 0)), (length + 200) * k, w, 800)
        R.render(g + "_fitted_qr", q_right, centre + Vector((0, 0.05, 0)), (length + 200) * k, w, 800)
    p = PTS["SCARH"]
    state("SCARH", rounds=50)
    R.render("SCARH_drum_left", left, Vector((0.0, 0.1, -0.03)), 0.42, 1200, 900)
    R.render("SCARH_drum_q", q_right, Vector((0.0, 0.1, -0.03)), 0.42, 1200, 900)
    R.render("SCARH_drum_front", (0, -1, 0), Vector((0.0, 0.0, -0.03)), 0.2, 600, 700)
    for r, m in hmags.items():
        place(m)
        show_only([m])
        R.render("mag%d_SCARH" % r, left, Vector((0, 0, -0.065 if r == 50 else -0.045)), 0.2 if r == 50 else 0.16,
                 500, 700)
    place(mount)
    place(supp, {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]})
    show_only([mount])
    R.render("mount_q", q_right, Vector((0, 0.018, 0)), 0.06, 600, 500)
    show_only([supp])
    R.render("supp_q", q_right, Vector((0, 0.06, 0)), 0.15, 900, 500)
    if GOM:
        for name, tex, scale_mm in (("M4A1", "assault_rifles", 900.0), ("FAL", "battle_rifles", 1160.0)):
            objs = R.load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % name),
                          os.path.join(GOM, "textures/weapons/firearms/%s/%s.png" % (tex, name)))
            for o in objs.values():
                place(o)
            show_only(list(objs.values()))
            R.render("gom_" + name, left, Vector((0.0, 0.12 if name == "M4A1" else 0.17, 0.0)), scale_mm * 0.00065,
                     1600, 600)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
