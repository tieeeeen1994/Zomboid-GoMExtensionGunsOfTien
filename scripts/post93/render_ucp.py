"""Review renders of the exported H&K UCP prototype assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_ucp.py -- OUT_DIR

Imports what build_ucp.py wrote, places the parts at ucp_points.json the way the engine does (offset,
then rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the right side at the
reference photo's scale for the outline check, 3/4 views, the slide back, the magazine, the MP7's mount device
(drawn as UCP_Muzzle_Mount_Device) and Rotex-II suppressor at `canon`, GoM's pistol parts at their points, and GoM's
Glock 17 at the same scale.

Game space is used as Blender world space (data z flipped back), which is the mirror image of what the game shows
(the engine imports with Assimp's MAKE_LEFT_HANDED; Blender's own FBX import shows the true handedness).
make_ucp_art.py flips every render left-right before using it, so the sheets show the gun as it looks in game:
left side = muzzle to the left, as in the photo, and the markings read the right way.
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
POINTS = json.load(open(os.path.join(HERE, "ucp_points.json")))
K = 0.000603                       # the builder's (the M16A2's proportion since 2026-10-26)
L0, H0 = POINTS["_extras"]["photo_origin_mm"]
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')       # GoM's pistols (and this one) are modelled upside down


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


def up(L, H):
    """Photo (L, H) mm -> world position of that point on the upright gun."""
    return Vector((0.0, (L0 - L) * K, (H - H0) * K))


GOM_PARTS = {  # name: (fbx, point)
    "Beretta_Mount": ("rails", "rail_up"), "PL4_Sight": ("scopes", "scope"), "PS1_Sight": ("scopes", "scope"),
    "LP_Light": ("pointers", "underbarrel"), "TL_Light": ("pointers", "underbarrel"),
}


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

    gun = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UCP.fbx"), os.path.join(TEX, "UCP.png"))
    body, slide = gun["UCP_BODY"], gun["UCP_SLIDE"]
    mags = {}
    for r in (20, 40):
        n = "46x30Magazine%d_UCP" % r
        mags[r] = load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UCP_magazines.fbx"),
                       os.path.join(TEX, n + ".png"), keep=n)[n]
    n = "UCP_Muzzle_Mount_Device"                        # the MP7's mount device item as drawn on this gun
    mount = load(os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UCP_parts.fbx"),
                 os.path.join(TEX, n + ".png"), keep=n)[n]
    supp = load(os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx"),
                os.path.join(TEX, "MP7_Suppressor.png"), keep="MP7_Suppressor")["MP7_Suppressor"]
    gom = {}
    if GOM:
        for n, (cat, _) in GOM_PARTS.items():
            gom.update(load(os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
                            os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (cat, n)), keep=n))

    def state(mag=20, fired=False, supp_on=False, mount_on=False, extra=()):
        place(body)
        place(slide, POINTS["slide_fired"] if fired else None)
        objs = [body, slide]
        if mag:
            place(mags[mag])
            objs.append(mags[mag])
        if supp_on or mount_on:
            place(mount, POINTS["canon"])
            objs.append(mount)
        if supp_on:
            place(supp, POINTS["canon"])
            objs.append(supp)
        for n in extra:
            place(gom[n], POINTS[GOM_PARTS[n][1]])
            objs.append(gom[n])
        show_only(objs)

    right, left = (1, 0, 0), (-1, 0, 0)          # the camera looks along these: (1, 0, 0) sees the gun's right side
    like_usg = (-0.62, -0.5, -0.6)               # Five-seveN_USG.jpg: left side from behind and above
    like_r = (0.7, -0.45, -0.55)                 # right side from behind and above
    c = up(100.0, 65.0)
    state()
    # left side at the photo's scale: 240 mm across 1200 px, centred on photo (100, 65)
    render("left_photo", left, c, 240 * K, 1200, 900)
    json.dump({"left_photo": {"centre_mm": [100.0, 65.0], "px_per_mm": 1200 / 240.0, "size": [1200, 900]}},
              open(os.path.join(OUT, "cameras.json"), "w"))
    render("right", right, c, 240 * K, 1200, 900)
    render("q_left", like_usg, c, 250 * K, 1200, 900)
    render("q_right", like_r, c, 250 * K, 1200, 900)
    render("top", (0, 0, -1), up(104.0, 0.0) * Vector((0, 1, 0)), 240 * K, 1200, 300)
    render("front", (0, -1, 0), up(0.0, 75.0) * Vector((0, 0, 1)), 160 * K, 500, 600)
    render("back", (0, 1, 0), up(0.0, 75.0) * Vector((0, 0, 1)), 160 * K, 500, 600)
    state(fired=True)
    render("fired", like_r, c, 250 * K, 1200, 900)
    state(mag=0)
    render("nomag_under", (0.25, -0.2, 0.95), c, 250 * K, 1000, 800)
    for r in (20, 40):
        place(mags[r])
        show_only([mags[r]])
        render("mag%d_alone" % r, left, up(170.0, 45.0 if r == 20 else 15.0), 150 * K, 500, 700 if r == 20 else 820)
    state(mag=40)
    render("mag40_left", left, up(110.0, 35.0), 280 * K, 1200, 1100)
    render("mag40_q", like_usg, up(110.0, 35.0), 300 * K, 1200, 1100)
    render("mag40_back", (0, 1, 0), up(0.0, 35.0) * Vector((0, 0, 1)), 200 * K, 700, 800)
    state(supp_on=True)
    render("supp_left", left, up(30.0, 80.0), 380 * K, 1400, 800)
    render("supp_q", like_r, up(30.0, 80.0), 360 * K, 1400, 900)
    state(mount_on=True)
    render("mount_q", like_r, up(5.0, 112.0), 60 * K, 700, 500)
    if gom:
        state(extra=("Beretta_Mount", "PL4_Sight", "LP_Light"))
        render("gom_left", left, up(90.0, 80.0), 300 * K, 1300, 1000)
        render("gom_q", like_usg, up(90.0, 85.0), 300 * K, 1300, 1000)
        state(extra=("Beretta_Mount", "PS1_Sight", "LP_Light"), supp_on=True)
        render("gom2_q", like_r, up(50.0, 85.0), 380 * K, 1400, 1000)
        state(extra=("LP_Light",))
        render("lp_right", right, up(60.0, 95.0), 200 * K, 1000, 700)
        state(extra=("TL_Light",))
        render("tl_right", right, up(40.0, 95.0), 240 * K, 1000, 700)
        # GoM's Glock 17 (body, slide, magazine) next to it at the same scale, right side
        glock = load(os.path.join(GOM, "models_X/weapons/firearms/GLOCK17.fbx"),
                     os.path.join(GOM, "textures/weapons/firearms/pistols/GLOCK17.png"))
        gmag = load(os.path.join(GOM, "models_X/weapons/magazines/pistols.fbx"),
                    os.path.join(GOM, "textures/weapons/magazines/pistols/9x19Magazine17_Glock.png"),
                    keep="9x19Magazine17_Glock")
        for o in list(glock.values()) + list(gmag.values()):
            place(o)
        show_only(list(glock.values()) + list(gmag.values()))
        render("glock_left", left, Vector((0.0, 0.06, 0.0)), 0.21, 900, 700)
        state()
        render("ucp_left", left, Vector((0.0, 0.06, 0.0)), 0.21, 900, 700)


main()
