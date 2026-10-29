"""Review renders of the exported Uzi, Mini Uzi and Micro Uzi, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_uzi.py -- OUT_DIR

Imports what build_uzi.py wrote, places every part at uzi_points.json the way the engine does (offset, then rotateXYZ
in degrees, game space) and renders orthographic Workbench views into OUT_DIR: each gun's left side at a fixed scale
(px_per_mm in cameras.json, for the outline check in make_uzi_art.py), its right side, 3/4 views, stock folded and
deployed, the Mk9 on its mount device, every magazine, and GoM's MP5 / MP5K at the same scale. The Mini and Micro Uzi
are modelled upside down (held like a pistol) and are turned back upright here. Game space is Blender world space,
the mirror image of what the game shows; make_uzi_art.py flips every render left-right.
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
PTS = json.load(open(os.path.join(HERE, "uzi_points.json")))
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx")
SMG9 = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')
PX_PER_MM = 2.0


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
        if keep and o.name not in keep:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name] = o
    return objs


def place(o, point=None, handgun=False):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = (UPRIGHT if handgun else Matrix.Identity(4)) @ mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


def render(name, direction, centre, size_mm, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.ortho_scale = size_mm * 0.00072
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

    mag_names = ["9x19Magazine%d_UZI" % r for r in (20, 25, 32, 40, 50)]
    mags = {n: load(MAGS, os.path.join(TEX, n + ".png"), keep=[n])[n] for n in mag_names}
    supp = load(SMG9, os.path.join(TEX, "Mk9_Suppressor.png"), keep=["Mk9_Suppressor"])["Mk9_Suppressor"]
    mount = load(SMG9, os.path.join(TEX, "SMG9_Muzzle_Mount_Device.png"),
                 keep=["SMG9_Muzzle_Mount_Device"])["SMG9_Muzzle_Mount_Device"]
    cams = {}
    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    for kind, mag, (Lmax, Hmax) in (("UZI", "9x19Magazine25_UZI", (470.0, 227.0)),
                                    ("MINIUZI", "9x19Magazine20_UZI", (600.0, 194.0)),
                                    ("MICROUZI", "9x19Magazine20_UZI", (257.0, 180.0))):
        p = PTS[kind]
        hg = p["_extras"]["handgun_hold"]
        L0, H0 = p["_extras"]["photo_origin_mm"]
        objs = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_%s.fbx" % kind),
                    os.path.join(TEX, kind + ".png"))
        body, bolt, handle = objs[kind + "_BODY"], objs[kind + "_BOLT"], objs[kind + "_HANDLE"]

        def state(folded, magname=mag, can=False):
            place(body, None, hg)
            place(bolt, None, hg)
            place(handle, None, hg)
            shown = [body, bolt, handle]
            if kind == "UZI":
                st = objs["UZI_STOCK_FOLDED" if folded else "UZI_STOCK_DEPLOYED"]
                place(st, None, hg)
            else:
                st = objs[kind + "_STOCK"]
                place(st, p["stock_folded" if folded else "stock"], hg)
            shown.append(st)
            if magname:
                place(mags[magname], p["magazine"], hg)
                shown.append(mags[magname])
            if can:
                place(mount, p["canon"], hg)
                place(supp, p["canon"], hg)
                shown += [mount, supp]
            show_only(shown)

        # the photo's own state first (Uzi and Micro folded, Mini deployed), the photo's frame centred, PX_PER_MM
        photo_folded = kind != "MINIUZI"
        k = 0.00072
        span, tall = Lmax + 80.0, Hmax + 80.0
        w, h = int(span * PX_PER_MM), int(tall * PX_PER_MM)
        centre = Vector((0.0, (L0 - Lmax / 2.0) * k, (Hmax / 2.0 - H0) * k))
        state(photo_folded)
        render(kind + "_left", left, centre, span, w, h)
        cams[kind] = {"px_per_mm": PX_PER_MM, "size": [w, h], "photo_centre_mm": [Lmax / 2.0, Hmax / 2.0]}
        render(kind + "_right", right, centre, span, w, h)
        render(kind + "_q_right", q_right, centre, span, w, int(h * 1.3))
        render(kind + "_q_left", q_left, centre, span, w, int(h * 1.3))
        state(not photo_folded)
        render(kind + "_other_left", left, centre, span, w, h)
        render(kind + "_other_q", q_right, centre, span, w, int(h * 1.3))
        render(kind + "_other_top", (0, 0, -1), centre, span, w, int(150 * PX_PER_MM))
        state(photo_folded, magname=None)
        render(kind + "_nomag_under", (0.25, -0.2, 0.95), centre, span, w, h)
        state(True, magname="9x19Magazine32_UZI", can=True)
        render(kind + "_mk9_left", left, centre + Vector((0, 0.08, 0)), span + 160, int((span + 160) * PX_PER_MM),
               h)
        for m in ("9x19Magazine40_UZI", "9x19Magazine50_UZI"):
            state(True, magname=m)
            render(kind + "_" + m.split("_")[0][-2:] + "_left", left, centre + Vector((0, 0, -0.04)), span, w,
                   int((tall + 110) * PX_PER_MM))
        for o in objs.values():
            o.hide_render = True
            o.name = o.name + "_done"
    if GOM:
        for name, tex in (("MP5", "MP5"), ("MP5K", "MP5K"), ("MAC10", "MAC10")):
            objs = load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % name),
                        os.path.join(GOM, "textures/weapons/firearms/smgs/%s.png" % tex))
            hg = name != "MP5"
            shown = []
            for o in objs.values():
                if "FOLDED" in o.name or "BOLT" in o.name and "DEPLOYED" in o.name:
                    continue
                place(o, None, hg)
                shown.append(o)
            show_only(shown)
            render("gom_" + name, left, Vector((0.0, 0.07, -0.03)), 600, 1200, 600)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
