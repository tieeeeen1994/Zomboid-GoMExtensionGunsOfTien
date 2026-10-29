"""Review renders of the exported Steyr AUG A1, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_aug.py -- OUT_DIR

Imports what build_aug.py wrote, places every part at aug_points.json the way the engine does (offset, then rotateXYZ
in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the left side at PX_PER_MM in the
photo's state (front grip down, no magazine; cameras.json gives the frame for make_aug_art.py's outline check), the
right side, 3/4 views, the grip folded, both magazines fitted, the magazines alone, and GoM's FAMAS at the same scale.
Game space is Blender world space, the mirror image of what the game shows; make_aug_art.py flips every render
left-right.
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
PTS = json.load(open(os.path.join(HERE, "aug_points.json")))
K = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_AUG.fbx")
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")
PX_PER_MM = 2.0
LMAX, HMAX = 790.0, 236.0          # the photo's frame: muzzle to butt, heel to the scope turret's top


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

    objs = load(GUN, os.path.join(TEX, "AUG.png"))
    body, bolt, handle, fg = objs["AUG_BODY"], objs["AUG_BOLT"], objs["AUG_HANDLE"], objs["AUG_FOREGRIP"]
    mags = {r: load(MAGS, os.path.join(TEX, "556x45Magazine%d_AUG.png" % r), keep=["556x45Magazine%d_AUG" % r])
            ["556x45Magazine%d_AUG" % r] for r in (30, 42)}

    def state(folded=False, mag=30, fired=False, racked=False):
        """fired: the bolt carrier back (each shot, held open when empty); racked: the handle back as well."""
        place(body)
        place(bolt, PTS["bolt_fired"] if fired or racked else None)
        place(handle, PTS["handle_back"] if racked else None)
        place(fg, PTS["foregrip_folded" if folded else "foregrip_deployed"])
        shown = [body, bolt, handle, fg]
        if mag:
            place(mags[mag], PTS["magazine"])
            shown.append(mags[mag])
        show_only(shown)

    span, tall = LMAX + 80.0, HMAX + 80.0
    w, h = int(span * PX_PER_MM), int(tall * PX_PER_MM)
    centre = Vector((0.0, (L0 - LMAX / 2.0) * K, (HMAX / 2.0 - H0) * K))
    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    state(mag=None)
    render("AUG_left", left, centre, span, w, h)
    json.dump({"AUG": {"px_per_mm": PX_PER_MM, "size": [w, h], "photo_centre_mm": [LMAX / 2.0, HMAX / 2.0]}},
              open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    low = centre + Vector((0, 0, -0.03))
    state()
    render("AUG_left_mag", left, low, span, w, int((tall + 100) * PX_PER_MM))
    render("AUG_right", right, low, span, w, int((tall + 100) * PX_PER_MM))
    render("AUG_q_right", q_right, low, span, w, int((tall + 140) * PX_PER_MM))
    render("AUG_q_left", q_left, low, span, w, int((tall + 140) * PX_PER_MM))
    render("AUG_top", (0, 0, -1), centre, span, w, int(160 * PX_PER_MM))
    render("AUG_front", (0, -1, 0), low, 300, 600, 700)
    # the bolt carrier in the ejection port on the right (closed / fired or held open), the handle on the left
    port = Vector((0.0, (L0 - 525.5) * K, (120.25 - H0) * K))
    for name, kw in (("closed", {}), ("fired", {"fired": True}), ("racked", {"racked": True})):
        state(**kw)
        render("AUG_port_%s" % name, right, port, 120, 600, 400)
        render("AUG_handle_%s" % name, left, low, span, w, int((tall + 100) * PX_PER_MM))
    state(folded=True, mag=42, fired=True)
    render("AUG_folded_42_fired", left, low, span, w, int((tall + 160) * PX_PER_MM))
    render("AUG_folded_q", q_right, low, span, w, int((tall + 160) * PX_PER_MM))
    for r, m in mags.items():
        place(m)
        show_only([m])
        render("mag%d_left" % r, left, Vector((0, 0.015, -0.07)), 260, 520, 560)
        render("mag%d_q" % r, q_right, Vector((0, 0.015, -0.07)), 260, 520, 560)
    if GOM:
        g = load(os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"),
                 os.path.join(GOM, "textures/weapons/firearms/assault_rifles/FAMAS.png"))
        shown = []
        for o in g.values():
            place(o)
            shown.append(o)
        show_only(shown)
        render("gom_FAMAS", left, centre, span, w, h)


main()
