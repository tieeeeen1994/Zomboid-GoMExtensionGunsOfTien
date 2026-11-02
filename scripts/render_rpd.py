"""Review renders of the exported RPD, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_rpd.py -- OUT_DIR

Imports what build_rpd.py wrote, places the parts at rpd_points.json the way the engine does, and renders
orthographic Workbench views into OUT_DIR at PX_PER_MM real: the left side in the reference photo's state (bipod
folded, no drum; cameras.json gives the frame for make_rpd_art.py's outline check), with the drum, the right side
(the operating handle forward and back), 3/4 views from the front and the rear, the front, the bipod deployed, the drum
alone. Game space is Blender world space, the mirror image of what the game shows.
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
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "rpd_points.json")))
K = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPD.fbx")
DRUM = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPD_drum.fbx")
PX_PER_MM = 1.6
LMAX, HMAX = 1037.0, 196.0          # the photo's frame: muzzle tip to butt, the butt's toe to the front sight's top


def load(path, texture):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    m = bpy.data.materials.new(os.path.basename(texture))
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    objs = {}
    for o in set(bpy.data.objects) - before:
        o.data.materials.clear()
        o.data.materials.append(m)
        objs[o.name.split(".")[0]] = o
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


def render(name, objs, direction, centre, size_mm, w, h):
    show_only(objs)
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = Vector(centre) - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
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

    g = load(GUN, os.path.join(TEX, "RPD.png"))
    body, bolt, fold, dep = g["RPD_BODY"], g["RPD_BOLT"], g["RPD_BIPOD_FOLDED"], g["RPD_BIPOD_DEPLOYED"]
    drum = load(DRUM, os.path.join(TEX, "762x39Drum100_RPD.png"))["762x39Drum100_RPD"]

    def state(deployed=False, with_drum=True, fired=False):
        place(body)
        place(bolt, PTS["bolt_fired"] if fired else None)
        place(fold)
        place(dep)
        shown = [body, bolt, dep if deployed else fold]
        if with_drum:
            place(drum, PTS["magazine"])
            shown.append(drum)
        show_only(shown)
        return shown

    span, tall = LMAX + 80.0, HMAX + 80.0
    w, h = int(span * PX_PER_MM), int(tall * PX_PER_MM)
    centre = Vector((0.0, (L0 - LMAX / 2.0) * K, (HMAX / 2.0 - H0) * K))
    left, right = (-1, 0, 0), (1, 0, 0)
    objs = state(with_drum=False)
    render("RPD_left", objs, left, centre, span, w, h)
    json.dump({"RPD": {"px_per_mm": PX_PER_MM, "size": [w, h], "photo_centre_mm": [LMAX / 2.0, HMAX / 2.0]}},
              open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    low = centre + Vector((0, 0, -0.05))
    tall2 = int((tall + 200) * PX_PER_MM)
    objs = state()
    render("RPD_left_drum", objs, left, low, span, w, tall2)
    render("RPD_right_drum", objs, right, low, span, w, tall2)
    render("RPD_q_front_right", objs, (0.75, -0.55, -0.35), low, span, w, tall2)
    render("RPD_q_front_left", objs, (-0.75, -0.55, -0.35), low, span, w, tall2)
    render("RPD_q_rear_right", objs, (0.7, 0.5, -0.45), low, span, w, tall2)
    render("RPD_front", objs, (0, -1, 0), low, 520, 832, 700)
    render("RPD_top", objs, (0, 0, -1), centre, span, w, int(200 * PX_PER_MM))
    objs = state(fired=True)
    render("RPD_right_fired", objs, right, low, span, w, tall2)
    # the operating handle close up, from the front right and above: forward, then back
    hx = Vector(PTS["_extras"]["handle"])
    for name, fired in (("RPD_handle_forward", False), ("RPD_handle_back", True)):
        objs = state(fired=fired)
        render(name, objs, (0.75, -0.35, -0.55), hx + Vector((0, -0.03, 0)), 260, 640, 480)
    objs = state(deployed=True)
    render("RPD_deployed_q", objs, (0.75, -0.55, -0.35), centre + Vector((0, 0, -0.08)), span + 100, w + 160,
           int((tall + 420) * PX_PER_MM))
    render("RPD_deployed_left", objs, left, centre + Vector((0, 0, -0.08)), span, w, int((tall + 420) * PX_PER_MM))
    place(drum)
    show_only([drum])
    for name, d in (("drum_side", left), ("drum_front", (0, -1, 0)), ("drum_q", (0.6, -0.6, -0.45))):
        render(name, [drum], d, Vector((0, 0, -0.05)), 260, 520, 520)


main()
