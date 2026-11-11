"""Review renders of the exported Steyr TMP, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_tmp.py -- OUT_DIR

Imports what build_tmp.py wrote, places every part at tmp_points.json the way the engine does (offset, then rotateXYZ
in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the left side at a fixed scale
(px_per_mm in cameras.json, for the outline check in make_tmp_art.py) with the 30-round magazine, as photographed,
its right side, 3/4 views, the 15-round magazine, the Mk9 on its mount device (drawn at the `_GoT` scale), the
cocking knob back and the bolt fired, and GoM's MP5K / MAC-10 at the same scale. The TMP is modelled upside down (held
like a pistol) and is turned back upright here. Game space is Blender world space, the mirror image of what the game
shows; make_tmp_art.py flips every render left-right.
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
PTS = json.load(open(os.path.join(HERE, "tmp_points.json")))
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TMP_magazines.fbx")
SMG9 = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')
PX_PER_MM = 3.0
K = 0.000603
GOT_PART_SCALE = 0.000603 / 0.00072        # gen_scripts.py: the Mk9 and its mount drawn through `<part>_GoT`


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


def place(o, point=None, handgun=True, scale=1.0):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = ((UPRIGHT if handgun else Matrix.Identity(4)) @ mat @ Matrix.Scale(scale, 4)
                      @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0)))


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
    cam.data.ortho_scale = size_mm * K
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

    mags = {n: load(MAGS, os.path.join(TEX, n + ".png"), keep=[n])[n] for n in ("9x19Magazine15_TMP",
                                                                               "9x19Magazine30_TMP")}
    supp = load(SMG9, os.path.join(TEX, "Mk9_Suppressor.png"), keep=["Mk9_Suppressor"])["Mk9_Suppressor"]
    mount = load(SMG9, os.path.join(TEX, "SMG9_Muzzle_Mount_Device.png"),
                 keep=["SMG9_Muzzle_Mount_Device"])["SMG9_Muzzle_Mount_Device"]
    objs = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TMP.fbx"), os.path.join(TEX, "TMP.png"))
    body, bolt, handle = objs["TMP_BODY"], objs["TMP_BOLT"], objs["TMP_HANDLE"]
    p = PTS
    L0, H0 = p["_extras"]["photo_origin_mm"]

    def state(mag="9x19Magazine30_TMP", can=False, racked=False, fired=False):
        place(body)
        place(bolt, p["bolt_fired"] if fired else None)
        place(handle, p["handle_back"] if racked else None)
        shown = [body, bolt, handle]
        if mag:
            place(mags[mag], p["magazine"])
            shown.append(mags[mag])
        if can:
            place(mount, p["canon"], scale=GOT_PART_SCALE)
            place(supp, p["canon"], scale=GOT_PART_SCALE)
            shown += [mount, supp]
        show_only(shown)

    Lmax, Hmax = 282.0, 241.0          # the photo's frame (tmp_reference_outline.json); the knob racked reaches 316
    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    span, tall = Lmax + 40.0, Hmax + 40.0
    w, h = int(span * PX_PER_MM), int(tall * PX_PER_MM)
    centre = Vector((0.0, (L0 - Lmax / 2.0) * K, (Hmax / 2.0 - H0) * K))
    state()
    render("TMP_left", left, centre, span, w, h)
    render("TMP_right", right, centre, span, w, h)
    render("TMP_q_right", q_right, centre, span, w, int(h * 1.2))
    render("TMP_q_left", q_left, centre, span, w, int(h * 1.2))
    render("TMP_top", (0, 0, -1), centre, span, w, int(120 * PX_PER_MM))
    render("TMP_front", (0, -1, 0), centre, tall, h, h)
    state(mag="9x19Magazine15_TMP")
    render("TMP_15_left", left, centre, span, w, h)
    state(racked=True, fired=True)
    render("TMP_racked_right", right, centre + Vector((0, -0.012, 0)), span + 40, w + 120, h)
    state(can=True)
    render("TMP_mk9_left", left, centre + Vector((0, 0.06, 0)), span + 200, int((span + 200) * PX_PER_MM), h)
    json.dump({"TMP": {"px_per_mm": PX_PER_MM, "size": [w, h], "photo_centre_mm": [Lmax / 2.0, Hmax / 2.0]}},
              open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    # GoM's MP5K and MAC-10 beside the TMP, all three in one frame size (game units: ours are drawn at 0.603 of real
    # size, GoM's SMGs at 0.72)
    cmp_span = 470.0
    cw, ch = int(cmp_span * 2.0), int(cmp_span * 0.75 * 2.0)
    ccentre = Vector((0.0, 0.07, -0.02))
    state()
    render("cmp_TMP", left, ccentre, cmp_span, cw, ch)
    if GOM:
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.name = o.name + "_done"
        for name in ("MP5K", "MAC10"):
            g = load(os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % name),
                     os.path.join(GOM, "textures/weapons/firearms/smgs/%s.png" % name))
            shown = []
            for o in g.values():
                if "FOLDED" in o.name or "BOLT" in o.name and "DEPLOYED" in o.name:
                    continue
                place(o)
                shown.append(o)
            show_only(shown)
            render("cmp_gom_" + name, left, ccentre, cmp_span, cw, ch)


main()
