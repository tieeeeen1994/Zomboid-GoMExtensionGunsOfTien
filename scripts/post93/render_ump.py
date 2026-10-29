"""Review renders of the exported UMP45 / UMP9 assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_ump.py -- OUT_DIR

Imports what build_ump.py wrote, places every part at ump_points.json the way the engine does (offset, then rotateXYZ
in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the UMP9's left side at its reference
photo's scale (for the outline check in make_ump_art.py), both guns' right side and 3/4 views, the stock folded, every
magazine, GoM's optic, foregrip, light and laser at their points, and GoM's MP5 at the same scale. Game space is used
as Blender world space, the mirror image of what the game shows; make_ump_art.py flips every render left-right (as
make_scar_art.py does).
"""

import json
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = [a for a in sys.argv]          # render_scar reads OUT from argv as well
import bpy                                # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "ump_points.json")))
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx")
PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx")
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx")
MAG_NAMES = ["9x19Magazine30_UMP", "45Magazine25_UMP", "45Magazine20_UMP", "45Magazine10_UMP"]


# load / place / render: render_scar.py's (rifles are upright, nothing is turned)
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


def retexture(o, texture):
    img = bpy.data.images.load(texture, check_existing=True)
    o.data.materials[0].node_tree.nodes["Image Texture"].image = img


def place(o, point=None):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    import math
    from mathutils import Matrix
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
    import math
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


def gom(cat, name, tex_dir):
    return load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                os.path.join(GOM, "textures/weapons/%s/%s.png" % (tex_dir, name)), keep=name)[name]


def main():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_cavity = False
    sc.display.shading.show_specular_highlight = False   # it lifted the black polymer's dark details away
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    objs = load(FIRE, os.path.join(TEX, "UMP9.png"))
    body, bolt, handle = objs["UMP_BODY"], objs["UMP_BOLT"], objs["UMP_HANDLE"]
    stock = load(PARTS, os.path.join(TEX, "UMP_STOCK.png"), keep="UMP_STOCK")["UMP_STOCK"]
    mags = {n: load(MAGS, os.path.join(TEX, n + ".png"), keep=n)[n] for n in MAG_NAMES}
    g_parts = {}
    if GOM:
        for cat, name, tex in (("parts/scopes", "Aimpoint_Sight", "parts/scopes"),
                               ("parts/scopes", "EXPS3_Sight", "parts/scopes"),
                               ("parts/foregrips", "MKC_Foregrip", "parts/foregrips"),
                               ("parts/pointers", "SR7_Light", "parts/pointers"),
                               ("parts/pointers", "AimRight_Laser", "parts/pointers")):
            try:
                g_parts[name] = gom(cat, name, tex)
            except Exception as e:                       # a texture named differently: skip that part
                print("skip", name, e)

    p = PTS

    def state(gun, mag, folded=False, extra=()):
        retexture(body, os.path.join(TEX, gun + ".png"))
        retexture(bolt, os.path.join(TEX, gun + ".png"))
        retexture(handle, os.path.join(TEX, gun + ".png"))
        place(body)
        place(bolt)
        place(handle)
        place(stock, p["stock_folded"] if folded else p["stock"])
        shown = [body, bolt, handle, stock]
        if mag:
            place(mags[mag], p["magazine"])
            shown.append(mags[mag])
        for name, point in extra:
            o = g_parts.get(name)
            if o is not None:
                place(o, p[point])
                shown.append(o)
        show_only(shown)

    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    k = p["_extras"]["k"]
    L0, H0 = p["_extras"]["photo_origin_mm"]
    length = 760.0
    lmid = (p["_bounds"]["UMP_BODY"]["max"][1] + p["_bounds"]["UMP_STOCK_deployed"]["min"][1]) / 2.0
    centre = Vector((0.0, lmid, -0.01))
    w = 1600
    cams = {}
    state("UMP9", "9x19Magazine30_UMP")
    render("UMP9_left", left, centre, length * k, w, 700)
    cams["UMP9_left"] = {"centre_game": [0.0, lmid, -0.01], "px_per_mm": w / length, "size": [w, 700],
                         "photo_origin_mm": [L0, H0], "k": k}
    render("UMP9_right", right, centre, length * k, w, 700)
    render("UMP9_q_left", q_left, centre, length * k, w, 900)
    render("UMP9_q_right", q_right, centre, length * k, w, 900)
    render("UMP9_top", (0, 0, -1), centre, length * k, w, 360)
    state("UMP45", "45Magazine25_UMP")
    render("UMP45_left", left, centre, length * k, w, 700)
    render("UMP45_right", right, centre, length * k, w, 700)
    render("UMP45_q_right", q_right, centre, length * k, w, 900)
    state("UMP45", "45Magazine25_UMP", folded=True)
    render("UMP45_folded_q", q_right, centre, length * k, w, 900)
    render("UMP45_folded_top", (0, 0, -1), centre, length * k, w, 360)
    render("UMP45_folded_right", right, centre, length * k, w, 700)
    state("UMP9", None)
    render("UMP_nomag_under", (0.25, -0.2, 0.95), centre, length * k, w, 700)
    extra = [("Aimpoint_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
             ("AimRight_Laser", "laser_right")]
    state("UMP9", "9x19Magazine30_UMP", extra=extra)
    render("UMP9_fitted_q", q_left, centre, (length + 100) * k, w, 900)
    render("UMP9_fitted_qr", q_right, centre, (length + 100) * k, w, 900)
    for rounds in ("45Magazine20_UMP", "45Magazine10_UMP"):
        state("UMP45", rounds)
        render("UMP45_" + rounds.split("Magazine")[1].split("_")[0] + "_left", left, centre, length * k, w, 700)
    for n, m in mags.items():
        place(m)
        show_only([m])
        render("mag_" + n, left, Vector((0, 0.03, -0.07)), 0.2, 500, 700)
    if GOM:
        objs = load(os.path.join(GOM, "models_X/weapons/firearms/MP5.fbx"),
                    os.path.join(GOM, "textures/weapons/firearms/smgs/MP5.png"))
        for o in objs.values():
            place(o)
        show_only(list(objs.values()))
        render("gom_MP5", left, Vector((0.0, 0.1, -0.01)), length * k, w, 700)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
