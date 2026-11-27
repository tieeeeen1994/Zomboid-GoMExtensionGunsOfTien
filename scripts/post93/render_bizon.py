"""Review renders of the exported Bizon family, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_bizon.py -- OUT_DIR [photo]

Imports what build_bizon.py wrote, places the parts at bizon_points.json the way the engine does (offset, then
rotateXYZ in degrees) and renders orthographic Workbench views into OUT_DIR:

    right_photo     the PP-19 Bizon's right side as the measuring photo (cca_007) has it, 64-round helical in, 4 px a
                    mm: the view to lay on the photo (scripts/ref_crop.py --overlay); right_a / right_b at 8 px a mm
    <gun>_right / _left / _q / _q_front / _top / _under    each body with its usual magazine (the -2-01 stock open
                    and folded, the -2-07 with the box and with the helical)
    vityaz_photo    the Vityaz's left side as the KP-9 photo (ria_003) has it, 4 px a mm
    bizon201_photo  the Bizon-2-01's right side, stock open, as cca_000 has its PP-19, 4 px a mm
    bizon201_fold_photo  the Bizon-2-01's left side, stock folded, as commons_040 has its Bizon, 4 px a mm
    bizon207_photo  the Bizon-2-07's left side with its box, as vpk_000 has it, 4 px a mm
    cmp_*           beside GoM's AKS-74U at one scale
(photo: only the photo-scale views)
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
GOM = "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media"
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "bizon_points.json")))
KG = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
MAG_FBX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_BIZON_magazines.fbx")
MAGS = ["9x18Magazine64_BIZON", "9x19Magazine53_BIZON", "762x25Magazine45_BIZON", "762x25Magazine35_BIZON",
        "9x19Magazine30_VITYAZ", "9x19Magazine30_VITYAZ_PAIR"]


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


def up(L, H, x=0.0):
    return Vector((x * KG, (L0 - L) * KG, (H - H0) * KG))


def render(name, direction, centre, size_mm, w, h):
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0.0 if d.z < 0 else math.pi, 0.0, math.radians(-90.0))
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = size_mm * KG
    cam.location = Vector(centre) - d * 2.0
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
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam

    mags = {n: load(MAG_FBX, os.path.join(TEX, n + ".png"), keep=[n])[n] for n in MAGS}
    objs = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_BIZON.fbx"),
                os.path.join(TEX, "BIZON.png"))
    bolt = objs["BIZON_BOLT"]
    folded, deployed = objs["BIZON_STOCK_FOLDED"], objs["BIZON_STOCK_DEPLOYED"]
    p = PTS

    def state(gun, mag, stock=None, fired=False):
        body = objs[gun + "_BODY"]
        place(body)
        place(bolt, p["bolt_fired"] if fired else None)
        shown = [body, bolt]
        if stock:
            s = deployed if stock == "open" else objs["VITYAZ_STOCK_FOLDED"] if gun == "VITYAZ" else folded
            place(s)
            shown.append(s)
        if mag:
            pt = (p[gun]["magazine_box"] if mag.endswith("35_BIZON") else p[gun]["magazine"] if gun == "VITYAZ"
                  else p["magazine"])
            place(mags[mag], pt)
            shown.append(mags[mag])
        show_only(shown)

    right, left = (1, 0, 0), (-1, 0, 0)
    cams = {}
    state("BIZON", "9x18Magazine64_BIZON")
    render("right_photo", right, up(212.5, 89.0), 520.0, 2080, 920)
    cams["right_photo"] = {"centre_mm": [212.5, 89.0], "px_per_mm": 4.0, "size": [2080, 920]}
    for name, cL in (("right_a", 110.0), ("right_b", 330.0)):
        render(name, right, up(cL, 89.0), 260.0, 2080, 1520)
        cams[name] = {"centre_mm": [cL, 89.0], "px_per_mm": 8.0, "size": [2080, 1520]}
    # the Vityaz's left side as Rock Island Auction's KP-9 (ria_003) has it, no stock: its photo frame is the
    # model's L + 20, H + 71 (build_bizon.py)
    state("VITYAZ", "9x19Magazine30_VITYAZ")
    render("vityaz_photo", left, up(215.0, 60.0), 520.0, 2080, 1160)
    cams["vityaz_photo"] = {"centre_mm": [235.0, 131.0], "px_per_mm": 4.0, "size": [2080, 1160]}
    # the Bizon-2-01's right side, stock open, as the same dealer's cca_000 has its PP-19 (same frame as cca_007;
    # that photo is foreshortened 0.88 vertically, so stretch it first: tmp/bizon/cca000s.jpg)
    state("BIZON201", "9x19Magazine53_BIZON", "open")
    render("bizon201_photo", right, up(335.0, 89.0), 720.0, 2880, 920)
    cams["bizon201_photo"] = {"centre_mm": [335.0, 89.0], "px_per_mm": 4.0, "size": [2880, 920]}
    # the Bizon-2-01's left side, stock folded, as Kuzmin's MVD Bizon (commons_040) has it
    state("BIZON201", "9x19Magazine53_BIZON", "folded")
    render("bizon201_fold_photo", left, up(212.5, 89.0), 520.0, 2080, 920)
    cams["bizon201_fold_photo"] = {"centre_mm": [212.5, 89.0], "px_per_mm": 4.0, "size": [2080, 920]}
    # the Vityaz's left side, stock folded, as Kuzmin's PP-19-01 (commons_005)
    state("VITYAZ", "9x19Magazine30_VITYAZ", "folded")
    render("vityaz_fold_photo", left, up(212.5, 89.0), 520.0, 2080, 920)
    cams["vityaz_fold_photo"] = {"centre_mm": [212.5, 89.0], "px_per_mm": 4.0, "size": [2080, 920]}
    # the Bizon-2-07's left side with its box, as vpk.name's -2-07 (vpk_000: no stock, its own handguard), in the
    # model's frame (tmp/bizon/vpk000_trace.json scales that photo by the trigger guard)
    state("BIZON207", "762x25Magazine35_BIZON")
    render("bizon207_photo", left, up(280.0, 40.0), 820.0, 3280, 1200)
    cams["bizon207_photo"] = {"centre_mm": [280.0, 40.0], "px_per_mm": 4.0, "size": [3280, 1200]}
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    if "photo" in sys.argv[sys.argv.index("--") + 2:]:
        return

    views = {"right": right, "left": left, "q": (-0.62, -0.5, -0.45), "q_right": (0.62, -0.5, -0.45),
             "q_front": (-0.55, 0.6, -0.35), "top": (0, 0, -1), "under": (0.15, -0.1, 0.98)}
    setups = [("BIZON", "BIZON", "9x18Magazine64_BIZON", None, 230.0, 520.0),
              ("BIZON201_open", "BIZON201", "9x19Magazine53_BIZON", "open", 330.0, 720.0),
              ("BIZON201_folded", "BIZON201", "9x19Magazine53_BIZON", "folded", 230.0, 520.0),
              ("BIZON207_box", "BIZON207", "762x25Magazine35_BIZON", None, 280.0, 820.0),
              ("BIZON207_helix", "BIZON207", "762x25Magazine45_BIZON", None, 280.0, 820.0),
              ("VITYAZ_folded", "VITYAZ", "9x19Magazine30_VITYAZ", "folded", 220.0, 520.0),
              ("VITYAZ_open", "VITYAZ", "9x19Magazine30_VITYAZ_PAIR", "open", 330.0, 720.0)]
    for tag, gun, mag, stock, cL, span in setups:
        state(gun, mag, stock)
        c = up(cL, 95.0)
        for vn, d in views.items():
            hh = int(span * 0.55 * 2.5) if vn not in ("top", "under") else int(span * 0.35 * 2.5)
            render("%s_%s" % (tag, vn), d, c, span, int(span * 2.5), hh)
    state("BIZON", "9x18Magazine64_BIZON", fired=True)
    render("BIZON_fired_right", right, up(330.0, 120.0), 220.0, 1100, 600)
    for n, o in mags.items():
        place(o)
        show_only([o])
        render(n + "_side", right, Vector((0.0, 0.05, -0.03)), 260.0, 1040, 700)
        render(n + "_q", (0.6, -0.6, -0.45), Vector((0.0, 0.05, -0.03)), 260.0, 1040, 700)

    # beside GoM's AKS-74U at one scale
    state("BIZON201", "9x19Magazine53_BIZON", "open")
    render("cmp_BIZON201", left, Vector((0.0, 0.05, 0.0)), 900.0, 1800, 700)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.name = o.name + "_done"
    g = load(f"{GOM}/models_X/weapons/firearms/AKS74U.fbx", f"{GOM}/textures/weapons/firearms/assault_rifles/AKS74U.png")
    shown = []
    for o in g.values():
        if "FOLDED" in o.name:
            continue
        place(o)
        shown.append(o)
    show_only(shown)
    render("cmp_gom_AKS74U", left, Vector((0.0, 0.05, 0.0)), 900.0, 1800, 700)


main()
