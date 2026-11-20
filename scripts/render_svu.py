"""Review renders of the exported SVU, read back from the FBX file (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_svu.py -- OUT_DIR

Imports what build_svu.py wrote with SVU.png, GoM's SVD magazine at our scale on `magazine`, GoM's AK mount and
PSO-1 on `rail_up` / `scope` for the fitted views, places parts at svu_points.json the way the engine does (offset,
then rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR at PX_PER_MM real.
Game space is Blender world space, the mirror image of what the game shows: the camera at +X shows the gun's left.
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
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "svu_points.json")))
SCALE = PTS["_extras"]["scale"]
K = 0.000603
PX_PER_MM = 2.0
GUN_FBX = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SVU.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/SVU.png")
MAG_FBX = GOM + "/models_X/weapons/magazines/semi_rifles.fbx"
MAG_TEX = GOM + "/textures/weapons/magazines/semi_rifles/762x54Magazine10_SVD.png"


def material(texture):
    m = bpy.data.materials.get(texture)
    if m:
        return m
    m = bpy.data.materials.new(texture)
    nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(texture, check_existing=True)
    t.interpolation = 'Closest'
    nt.links.new(t.outputs[0], nt.nodes["Principled BSDF"].inputs[0])
    return m


def load(path, textures, scale=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    objs = {}
    for o in set(bpy.data.objects) - before:
        name = o.name.split(".")[0]
        if name not in textures:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(material(textures[name]))
        if scale != 1.0:
            o.data.transform(Matrix.Scale(scale, 4))
        objs[name] = o
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


def bounds(objs):
    bpy.context.view_layer.update()
    vs = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])


def render(name, objs, direction, span_mm, centre, tall_mm):
    show_only(objs)
    span, tall = span_mm * K, tall_mm * K
    cam = bpy.data.objects["cam"]
    d = Vector(direction).normalized()
    cam.location = centre - d * 2.0
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = max(span, tall)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = int(span_mm * PX_PER_MM), int(tall_mm * PX_PER_MM)
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

    g = load(GUN_FBX, {n: TEX for n in ("SVU_BODY", "SVU_FD_BODY", "SVU_BOLT")})
    mag = load(MAG_FBX, {"762x54Magazine10_SVD": MAG_TEX}, SCALE)["762x54Magazine10_SVD"]
    fit = load(GOM + "/models_X/weapons/parts/rails.fbx", {"AK_Mount": GOM + "/textures/weapons/parts/rails/AK_Mount.png"})
    fit.update(load(GOM + "/models_X/weapons/parts/scopes.fbx",
                    {"PSO1_Scope": GOM + "/textures/weapons/parts/scopes/PSO1_Scope.png"}))
    for o in g.values():
        place(o)
    place(mag, PTS["magazine"])
    if "AK_Mount" in fit:
        place(fit["AK_Mount"], PTS["rail_up"])
    if "PSO1_Scope" in fit:
        place(fit["PSO1_Scope"], PTS["scope"])
    up, fd, bolt = g["SVU_BODY"], g["SVU_FD_BODY"], g["SVU_BOLT"]
    lo, hi = bounds([up])
    info = {"length_mm": round((hi.y - lo.y) / K, 1), "height_mm": round((hi.z - lo.z) / K, 1),
            "y0": round(lo.y, 4), "y1": round(hi.y, 4), "z0": round(lo.z, 4), "z1": round(hi.z, 4)}
    print("SIZES", info)
    centre = Vector((0.0, (lo.y + hi.y) / 2.0, (lo.z + hi.z) / 2.0))
    span, tall = 960, 300
    right, left, front = (1, 0, 0), (-1, 0, 0), (0, -1, 0)
    q = (0.7, -0.45, -0.5)
    base = [bolt, mag]
    render("SVU_right", [up] + base, right, span, centre, tall)      # the gun's right side (game), mirrored here
    render("SVU_left", [up] + base, left, span, centre, tall)
    render("SVU_FD_right", [fd] + base, right, span, centre, tall)
    render("SVU_FD_left_pso1", [fd] + base + list(fit.values()), left, span, centre + Vector((0, 0, 0.02)), 360)
    render("SVU_q", [up] + base, q, span, centre, 520)
    render("SVU_q_back", [up] + base, (-0.7, 0.45, -0.5), span, centre, 520)
    render("SVU_front", [up] + base, front, 300, centre, 300)
    render("SVU_top", [up] + base, (0, 0, -1), span, centre, 160)
    render("SVU_bottom", [up] + base, (0, 0, 1), span, centre, 160)
    json.dump(info, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


main()
