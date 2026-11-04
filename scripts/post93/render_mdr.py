"""Review renders of the exported MDRx .223 / .308 assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_mdr.py -- OUT_DIR

Imports what build_mdr.py wrote, places every part at mdr223_points.json / mdr308_points.json the way the engine does
(offset, then rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: each gun's left
side at its reference photo's scale (for the outline check in make_mdr_art.py), the right side (the window and the
carrier), 3/4 views, the top, the carrier and handles back, the PMAGs and the D-50, GoM's STANAG 30 and AR mount device
+ MKI on the .223, the SCAR-H's mount device + SOCOM762-RC on the .308, GoM's optics, foregrip, light, laser and bipod
at their points, and GoM's FAMAS at the same scale. Game space is Blender world space, the mirror image of what the
game shows; make_mdr_art.py flips every render left-right (render_scar.py's helpers).
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


# load / place / render: render_scar.py's (importing it would run its main())
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


def place_at(o, point=None):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = mat @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))


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


def gom(cat, name, tex_dir):
    return load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                os.path.join(GOM, "textures/weapons/%s/%s.png" % (tex_dir, name)), keep=name)[name]


GUNS = ("MDR223", "MDR308")
PTS = {g: json.load(open(os.path.join(HERE, g.lower() + "_points.json"))) for g in GUNS}
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms")
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx")
SCAR_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx")
GOT_SCALE = 0.000603 / 0.00065        # the main mod's `_GoT` models of GoM's STANAGs


def place(o, point=None, scale=1.0):
    place_at(o, point)
    if scale != 1.0:
        o.matrix_world = o.matrix_world @ Matrix.Diagonal((scale, scale, scale, 1.0))


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


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
    for g in GUNS:
        objs = R.load(os.path.join(FIRE, "GunsOfTienPost93_%s.fbx" % g), os.path.join(TEX, g + ".png"))
        guns[g] = (objs[g + "_BODY"], objs[g + "_BOLT"], objs[g + "_HANDLE"])
    pmags = {r: R.load(MAGS, os.path.join(TEX, "762x51Magazine%d_PMAG.png" % r), keep="762x51Magazine%d_PMAG" % r)
             ["762x51Magazine%d_PMAG" % r] for r in (10, 20, 25, 50)}
    supp = R.load(SCAR_PARTS, os.path.join(TEX, "SCARH_Suppressor.png"), keep="SCARH_Suppressor")["SCARH_Suppressor"]
    mount = R.load(SCAR_PARTS, os.path.join(TEX, "SCARH_Muzzle_Mount_Device.png"),
                   keep="SCARH_Muzzle_Mount_Device")["SCARH_Muzzle_Mount_Device"]
    g_parts = {}
    if GOM:
        for cat, name, tex in (("magazines/assault_rifles", "556x45Magazine30_STANAG", "magazines/assault_rifles"),
                               ("parts/muzzles", "Muzzle_Mount_Device", "parts/muzzles"),
                               ("parts/suppressors", "MKI_Suppressor", "parts/suppressors"),
                               ("parts/scopes", "Aimpoint_Sight", "parts/scopes"),
                               ("parts/scopes", "LR4X_Scope", "parts/scopes"),
                               ("parts/foregrips", "MKC_Foregrip", "parts/foregrips"),
                               ("parts/pointers", "SR7_Light", "parts/pointers"),
                               ("parts/pointers", "AimRight_Laser", "parts/pointers"),
                               ("parts/bipods", "Bipod_Deployed", "parts/bipods")):
            try:
                g_parts[name] = gom(cat, name, tex)
            except Exception as e:
                print("skip", name, e)

    def state(g, mag=True, fired=False, back=False, rounds=20, extra=(), h_supp=False):
        p = PTS[g]
        body, bolt, handle = guns[g]
        place(body)
        place(bolt, p["bolt_fired"] if fired else None)
        place(handle, p["handle_back"] if back else None)
        objs = [body, bolt, handle]
        if mag:
            if g == "MDR223":
                m = g_parts.get("556x45Magazine30_STANAG")
                if m is not None:
                    place(m, p["magazine"], GOT_SCALE)
                    objs.append(m)
            else:
                place(pmags[rounds], p["magazine"])
                objs.append(pmags[rounds])
        if h_supp:
            place(mount, p["canon"])
            place(supp, p["canon"])
            objs += [mount, supp]
        for name, point in extra:
            o = g_parts.get(name)
            if o is not None:
                place(o, p[point], GOT_SCALE if name in ("Muzzle_Mount_Device", "MKI_Suppressor") else 1.0)
                objs.append(o)
        show_only(objs)

    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    cams = {}
    for g in GUNS:
        p = PTS[g]
        k = p["_extras"]["k"]
        L0, H0 = p["_extras"]["photo_origin_mm"]
        length = p["_extras"]["length_mm"] + 60.0
        b = p["_bounds"][g + "_BODY"]
        lmid = (b["max"][1] + b["min"][1]) / 2.0
        centre = Vector((0.0, lmid, -0.01))
        w = 1600
        state(g)
        R.render(g + "_left", left, centre, length * k, w, 600)
        cams[g + "_left"] = {"centre_game": [0.0, lmid, -0.01], "px_per_mm": w / length, "size": [w, 600],
                             "photo_origin_mm": [L0, H0], "k": k}
        R.render(g + "_right", right, centre, length * k, w, 600)
        R.render(g + "_q_left", q_left, centre, length * k, w, 800)
        R.render(g + "_q_right", q_right, centre, length * k, w, 800)
        R.render(g + "_top", (0, 0, -1), centre, length * k, w, 360)
        state(g, fired=True, back=True)
        R.render(g + "_back_right", right, centre, length * k, w, 600)
        state(g, mag=False)
        R.render(g + "_nomag_under", (0.25, -0.2, 0.95), centre, length * k, w, 700)
        if g == "MDR223":
            state(g, extra=[("Aimpoint_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
                            ("AimRight_Laser", "laser_right"), ("Muzzle_Mount_Device", "canon"),
                            ("MKI_Suppressor", "canon")])
        else:
            state(g, rounds=20, h_supp=True, extra=[("LR4X_Scope", "scope"), ("Bipod_Deployed", "bipod"),
                                                    ("SR7_Light", "light_left"), ("AimRight_Laser", "laser_right")])
        R.render(g + "_fitted_q", q_left, centre + Vector((0, 0.04, 0)), (length + 200) * k, w, 800)
        R.render(g + "_fitted_qr", q_right, centre + Vector((0, 0.04, 0)), (length + 200) * k, w, 800)
    state("MDR308", rounds=50)
    R.render("MDR308_drum_left", left, Vector((0.0, 0.0, -0.04)), 0.36, 1200, 900)
    R.render("MDR308_drum_q", q_right, Vector((0.0, 0.0, -0.04)), 0.36, 1200, 900)
    for r, m in pmags.items():
        place(m)
        show_only([m])
        R.render("pmag%d" % r, left, Vector((0, 0, -0.06 if r == 50 else -0.055)), 0.16, 500, 700)
        R.render("pmag%d_q" % r, q_right, Vector((0, 0, -0.06 if r == 50 else -0.055)), 0.16, 500, 700)
    if GOM:
        objs = R.load(os.path.join(GOM, "models_X/weapons/firearms/FAMAS.fbx"),
                      os.path.join(GOM, "textures/weapons/firearms/assault_rifles/FAMAS.png"))
        for o in objs.values():
            place(o)
        show_only(list(objs.values()))
        R.render("gom_FAMAS", left, Vector((0.0, 0.05, -0.01)), 900.0 * 0.00065, 1600, 600)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
