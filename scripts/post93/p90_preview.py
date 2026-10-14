"""Blender (headless) review renders of the P90 TR assets, read back from the exported FBX files the way the game
reads them (game = raw x, raw y, -raw z), next to GoM's FAMAS and MP5 at the same scale.

    Blender -b --factory-startup -P p90_preview.py -- --media MEDIA --out DIR

Writes DIR/view_*.png (Workbench, textured, transparent background) and DIR/views.json (each orthographic
camera: centre, scale, resolution, axes) for make_p90.py, which lays out docs/post93_p90_preview.png.
After import every object sits under an empty that maps game space onto Blender's Z-up world as
(game x, -game y, game z): +X the gun's left, -Y the muzzle, +Z up.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p90_geometry as G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ARGS = dict(zip(argv[0::2], argv[1::2]))
MEDIA = os.path.abspath(ARGS["--media"])
OUT = os.path.abspath(ARGS["--out"])
GOM = os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/3722134990/mods/"
                         "GunsOfMarz/42.16/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
POINTS = G.points()


def to_world(p):
    return Vector((p[0], -p[1], p[2]))


def import_nodes(path, nodes, texture, offset=(0, 0, 0), rot_x=0.0, collection="p90"):
    """Import an FBX, keep the named nodes, place them at a game-space point (+ rotation about game X)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    img = bpy.data.images.load(texture, check_existing=True)
    mat = bpy.data.materials.new("m_" + os.path.basename(texture))
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    mat.node_tree.nodes.active = tex
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    mat.node_tree.links.new(tex.outputs[0], bsdf.inputs["Base Color"])
    kept = []
    for o in new:
        if o.type != "MESH" or o.name.split(".")[0] not in nodes:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(mat)
        # raw -> game: (x, y, -z) on the FBX data; imported objects carry rotation 90 / scale 0.01.
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(Matrix.Diagonal((1, 1, -1, 1)))
        o.data.flip_normals()
        # game -> world (x, -y, z), with the part's own rotation about game X and offset.
        c, s = math.cos(math.radians(rot_x)), math.sin(math.radians(rot_x))
        rx = Matrix(((1, 0, 0, 0), (0, c, -s, 0), (0, s, c, 0), (0, 0, 0, 1)))
        o.data.transform(rx)
        o.data.transform(Matrix.Translation(offset))
        o.data.transform(Matrix.Diagonal((1, -1, 1, 1)))
        o.data.flip_normals()
        o["set"] = collection
        kept.append(o)
    return kept


def show(sets):
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = o.get("set") not in sets


def camera(name, direction, centre, scale, res, up=None):
    """Orthographic camera looking along `direction` (world) at `centre`, Z up (or Y for a top view)."""
    scene = bpy.context.scene
    cam = bpy.data.objects.get("cam")
    if cam is None:
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
        scene.collection.objects.link(cam)
        scene.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    cam.data.clip_start = 0.001
    cam.data.clip_end = 10
    d = Vector(direction).normalized()
    if up is None:
        up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    up = Vector(up)
    cam.location = Vector(centre) - d * 2.0
    right = d.cross(up).normalized()
    true_up = right.cross(d).normalized()
    m = Matrix((right, true_up, -d)).transposed()
    cam.rotation_euler = m.to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT, "view_%s.png" % name)
    bpy.ops.render.render(write_still=True)
    return {"centre": list(centre), "scale": scale, "res": list(res), "right": list(right), "up": list(true_up)}


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.display.shading.show_cavity = False
    scene.display.shading.show_backface_culling = False
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"

    fire = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx")
    magf = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
    parts = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx")
    import_nodes(fire, {"P90TR_BODY", "P90TR_BOLT"}, os.path.join(TEX, "P90TR.png"), collection="p90")
    import_nodes(magf, {"57x28Magazine50_P90"}, os.path.join(TEX, "57x28Magazine50_P90.png"),
                 POINTS["magazine"]["offset"], collection="p90")
    import_nodes(parts, {"P90_Suppressor"}, os.path.join(TEX, "P90_Suppressor.png"), POINTS["canon"]["offset"],
                 collection="supp")
    import_nodes(parts, {"P90_Muzzle_Mount_Device"}, os.path.join(TEX, "P90_Muzzle_Mount_Device.png"),
                 POINTS["canon"]["offset"], collection="mount")
    import_nodes(magf, {"57x28Magazine50_P90"}, os.path.join(TEX, "57x28Magazine50_P90.png"), collection="magalone")
    # GoM references (read only).
    gf = os.path.join(GOM, "models_X/weapons/firearms")
    import_nodes(os.path.join(gf, "FAMAS.fbx"), {"FAMAS_BODY", "FAMAS_BOLT"},
                 os.path.join(GOM, "textures/weapons/firearms/assault_rifles/FAMAS.png"), collection="famas")
    import_nodes(os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx"), {"556x45Magazine30_STANAG"},
                 os.path.join(GOM, "textures/weapons/magazines/assault_rifles/556x45Magazine30_STANAG.png"),
                 (0, -0.0763, 0.0146), collection="famas")
    import_nodes(os.path.join(gf, "MP5.fbx"), {"MP5_BODY", "MP5_BOLT", "MP5_STOCK"},
                 os.path.join(GOM, "textures/weapons/firearms/smgs/MP5.png"), collection="mp5")
    import_nodes(os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"), {"9x19Magazine20_MP5"},
                 os.path.join(GOM, "textures/weapons/magazines/smgs/9x19Magazine20_MP5.png"),
                 (0, 0.1191, 0.0377), rot_x=10.2946, collection="mp5")

    views = {}
    mid = (0, -0.01, 0.0)
    show({"p90"})
    views["p90_34"] = camera("p90_34", (-0.75, 0.6, -0.35), mid, 0.42, (900, 600))
    views["p90_left"] = camera("p90_left", (-1, 0, 0), mid, 0.42, (900, 500))
    views["p90_right"] = camera("p90_right", (1, 0, 0), mid, 0.42, (900, 500))
    views["p90_top"] = camera("p90_top", (0, 0, -1), mid, 0.42, (900, 300), up=(1, 0, 0))
    views["p90_rear34"] = camera("p90_rear34", (0.7, -0.6, -0.4), mid, 0.42, (900, 600))
    views["p90_under"] = camera("p90_under", (-0.6, 0.3, 0.75), mid, 0.42, (900, 600))
    show({"magalone"})
    views["mag_34"] = camera("mag_34", (-0.7, 0.5, -0.5), (0, 0.09, 0.01), 0.22, (600, 360))
    show({"p90", "supp"})
    views["supp_34"] = camera("supp_34", (-0.75, 0.6, -0.35), (0, -0.07, 0.0), 0.56, (900, 500))
    show({"supp", "mount"})
    for o in bpy.data.objects:
        if o.get("set") == "supp":
            o.hide_render = True
    show({"mount", "p90"})
    views["mount_34"] = camera("mount_34", (-0.6, 0.5, -0.4), (0, -0.17, 0.014), 0.12, (600, 400))
    show({"famas"})
    views["famas_left"] = camera("famas_left", (-1, 0, 0), (0, -0.04, 0.0), 0.62, (1200, 500))
    show({"mp5"})
    views["mp5_left"] = camera("mp5_left", (-1, 0, 0), (0, -0.04, 0.0), 0.62, (1200, 500))
    show({"p90"})
    views["p90_left_wide"] = camera("p90_left_wide", (-1, 0, 0), (0, -0.04, 0.0), 0.62, (1200, 500))
    with open(os.path.join(OUT, "views.json"), "w") as handle:
        json.dump(views, handle, indent=1)


main()
