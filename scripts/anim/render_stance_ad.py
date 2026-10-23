"""The short SMG stance for the Workshop art (preview11; Blender 5.2, headless).

    blender -b --factory-startup -P scripts/anim/render_stance_ad.py -- <game media> <out_dir> [shot ...]

Renders <out_dir>/stance_<shot>.png: a game character dressed from the game's own files, posed from the shipped
stance clips (compact_build.stance_clip: the pack's gun-bone move undone, so the guns are drawn as the build previews
draw them), the set's gun on Bip01_Prop1 (hold_preview.GUNS, turned upright like the build); transparent orthographic
Workbench renders at one scale, so the figures keep their sizes against each other. make_workshop_art.py lays them
out.

Dressing (OUTFITS, from media/clothing/clothingItems): the body (models_X/Skinned/MaleBody.X / FemaleBody.X) wears
the skin texture with the items that are only textures composited over it (`m_BaseTextures`: shirts, boots); items
with a skinned mesh (`m_MaleModel` / `m_FemaleModel`: jackets, trousers, vests, hoodies) and the hair
(media/hairStyles) are their own meshes with their textures (TINT items and hair tinted); static items (`m_Static`,
helmets) hang on their `m_AttachBone`. The game's body masks (parts hidden under clothes) are left out. Every vanilla
file has its own bind pose, so each mesh is moved into the armature's rest pose (vertex = sum of weight x armature
rest x the file's skin offset, per bone) before the armature deforms it.
"""

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compact_build as B  # noqa: E402  (first: puts TienInspectWeapon's scripts/anim on the path)
import compact_stance as C  # noqa: E402
import hold_preview as HP  # noqa: E402
import pose  # noqa: E402
import x_import  # noqa: E402
import x_preview  # noqa: E402
import xanim  # noqa: E402

HAIR_BROWN, HAIR_BLACK, HAIR_BLONDE = (0.30, 0.20, 0.12), (0.09, 0.08, 0.08), (0.78, 0.62, 0.38)
# body, skin, texture-only items (path, tint), mesh items (model, texture, tint), hair (model, tint), static items
OUTFITS = {
    "survivor": dict(body="MaleBody", skin="Body/MaleBody01",
                     overlays=[("Clothes/Shirt_Tshirt_Textures/Tshirt_White", None),
                               ("Clothes/Shoes_Socks_Textres/BikerBoots", None)],
                     meshes=[("Clothes/Bob_Trousers", "Clothes/Trousers_Mesh/TrousersMesh_Denim", None),
                             ("Clothes/Bob_JacketLeather", "Clothes/Jacket/Jacket_Leather_Black", None)],
                     hair=("Hair/M_Hair_Short", HAIR_BROWN), static=[]),
    "police": dict(body="MaleBody", skin="Body/MaleBody02",
                   overlays=[("Clothes/Shirt_Tshirt_Textures/Shirt_Police", None),
                             ("Clothes/Shoes_Socks_Textres/BikerBoots", None)],
                   meshes=[("Clothes/Bob_Trousers", "Clothes/Trousers_Mesh/TrousersMesh_Police", None),
                           ("Clothes/Bob_BulletVest", "Clothes/BulletVest/Vest_BulletPolice", None)],
                   hair=("Hair/M_Hair_CrewCut", HAIR_BLACK), static=[]),
    "survivor_f": dict(body="FemaleBody", skin="Body/FemaleBody01",
                       overlays=[("Clothes/Shoes_Socks_Textres/Trainers_White", None)],
                       meshes=[("Clothes/Kate_Trousers", "Clothes/Trousers_Mesh/TrousersMesh_DenimBlack", None),
                               ("Clothes/Kate_HoodieDOWN", "Clothes/Hoodie/HoodieUP_White", (0.50, 0.16, 0.14))],
                       hair=("Hair/F_Hair_PonyTail", HAIR_BLONDE), static=[]),
    "soldier": dict(body="MaleBody", skin="Body/MaleBody03",
                    overlays=[("Clothes/Shirt_Tshirt_Textures/Shirt_CamoGreen", None),
                              ("Clothes/Shoes_Socks_Textres/ArmyBoots", None)],
                    meshes=[("Clothes/Bob_Trousers", "Clothes/Trousers_Mesh/TrousersMesh_CamoGreen", None),
                            ("Clothes/Bob_BulletVest", "Clothes/BulletVest/Vest_BulletCamoGreen", None)],
                    hair=None, static=[("clothes/M_ArmyHelmet", "Clothes/Hat/ArmyHelmet", "Bip01_Head")]),
}
# shot: (set, vanilla clip, frame or "stride", camera yaw (degrees round the figure, 0 = from the front), elevation,
#        outfit)
SHOTS = {
    "carried": ("Uzi", "Bob_IdleRifle", 0, 35, 8, "survivor"),
    "aimed": ("MP5K", "Bob_IdleAimRifle", 0, 60, 6, "police"),
    "crouched": ("MP7", "Bob_IdleSneak_Shotgun", 0, 40, 10, "survivor_f"),
    "running": ("Uzi", "Bob_RunRifle", "stride", 70, 8, "soldier"),
}
ORTHO = 1.2          # one scale for every shot (Bob stands ~1 unit tall)
RES = 1400


def find(base, rel, exts):
    """A game file by its path, ignoring case (the clothing XMLs and the folders disagree on it)."""
    d = base
    parts = rel.replace("\\", "/").split("/")
    for i, part in enumerate(parts):
        names = {n.lower(): n for n in os.listdir(d)}
        last = i == len(parts) - 1
        hit = next((names[(part + e).lower()] for e in (exts if last else ("",)) if (part + e).lower() in names), None)
        if hit is None:
            raise FileNotFoundError(os.path.join(base, rel))
        d = os.path.join(d, hit)
    return d


def load_px(path):
    """An image's pixels as an (h, w, 4) float array, top row first (Blender stores bottom row first)."""
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(img)
    return px


def resized(px, w, h):
    """Nearest-neighbour resample (game textures are pixel art at their own sizes)."""
    ys = (np.arange(h) * px.shape[0] // h)
    xs = (np.arange(w) * px.shape[1] // w)
    return px[ys][:, xs]


def tinted(px, tint):
    if tint is None:
        return px
    out = px.copy()
    out[..., :3] *= np.array(tint, dtype=np.float32)
    return out


def over(base, layer):
    """layer composited over base (straight alpha)."""
    a = layer[..., 3:4]
    out = base.copy()
    out[..., :3] = layer[..., :3] * a + base[..., :3] * (1 - a)
    out[..., 3:4] = a + base[..., 3:4] * (1 - a)
    return out


def image_material(name, px):
    h, w = px.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels = px[::-1].ravel()
    img.pack()
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    bsdf = nt.nodes.get("Principled BSDF")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.nodes.active = tex
    return mat


def add_skinned(arm_ob, rest, path, mat, name):
    """A game skinned mesh (.X) on the armature: moved from its file's bind pose into the armature's rest pose."""
    xm = xanim.read(path, with_mesh=True)
    verts, faces, skin = xm.mesh
    acc = [Vector() for _ in verts]
    wsum = [0.0] * len(verts)
    for bone, (idx, wts, off) in skin.items():
        if bone not in rest:
            continue
        m = rest[bone] @ x_import.m4(off)
        for i, w in zip(idx, wts):
            acc[i] += (m @ Vector(verts[i])) * w
            wsum[i] += w
    vs = [tuple(a / s) if s > 0 else tuple(verts[i]) for i, (a, s) in enumerate(zip(acc, wsum))]
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], [tuple(reversed(f)) for f in faces])
    me.update()
    if xm.mesh_uv:
        layer = me.uv_layers.new(name="UV")
        for loop in me.loops:
            u, v = xm.mesh_uv[loop.vertex_index]
            layer.data[loop.index].uv = (u, 1.0 - v)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = arm_ob
    for bone, (idx, wts, _) in skin.items():
        vg = ob.vertex_groups.new(name=bone)
        for i, w in zip(idx, wts):
            vg.add([i], w, "REPLACE")
    ob.modifiers.new("Armature", "ARMATURE").object = arm_ob
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def add_static(arm_ob, path, mat, bone, name):
    """A game static mesh (helmets) on a bone, in that bone's file frame (as the guns hang on Bip01_Prop1)."""
    xm = xanim.read(path, with_mesh=True)
    verts, faces, _ = xm.mesh
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(reversed(f)) for f in faces])
    me.update()
    if xm.mesh_uv:
        layer = me.uv_layers.new(name="UV")
        for loop in me.loops:
            u, v = xm.mesh_uv[loop.vertex_index]
            layer.data[loop.index].uv = (u, 1.0 - v)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    x_preview.attach_to_bone(ob, arm_ob, bone)
    return ob


def dress(arm_ob, rest, media, outfit):
    o = OUTFITS[outfit]
    tex = os.path.join(media, "textures")
    skinned = os.path.join(media, "models_X", "Skinned")
    skin = load_px(find(tex, o["skin"], (".png",)))
    for rel, tint in o["overlays"]:
        layer = tinted(load_px(find(tex, rel, (".png",))), tint)
        skin = over(skin, resized(layer, skin.shape[1], skin.shape[0]))
    add_skinned(arm_ob, rest, find(skinned, o["body"], (".x", ".X")), image_material(outfit + "_body", skin), "Body")
    for n, (model, texture, tint) in enumerate(o["meshes"]):
        im = tinted(load_px(find(tex, texture, (".png",))), tint)
        add_skinned(arm_ob, rest, find(skinned, model, (".x", ".X")), image_material("%s_%d" % (outfit, n), im),
                    "Cloth%d" % n)
    if o["hair"]:
        model, tint = o["hair"]
        im = tinted(load_px(find(tex, "F_Hair_White", (".png",))), tint)
        add_skinned(arm_ob, rest, find(skinned, model, (".x", ".X")), image_material(outfit + "_hair", im), "Hair")
    for model, texture, bone in o["static"]:
        im = load_px(find(tex, texture, (".png",)))
        add_static(arm_ob, find(os.path.join(media, "models_X", "static"), model, (".x", ".X")),
                   image_material(outfit + "_static", im), bone, "Static")


def render(media, out_dir, shot):
    set_name, clip, frame, yaw, elev, outfit = SHOTS[shot]
    src = os.path.join(media, "anims_X", "Bob")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ref = os.path.join(src, "Bob_IdleRifle.x")
    arm_ob = x_import.load(ref)
    for ob in [o for o in arm_ob.children if o.type == "MESH"]:
        bpy.data.objects.remove(ob, do_unlink=True)         # the clips' Bob mesh: dressed from the game's instead
    rest = x_import.rest_matrices(xanim.read(ref, with_mesh=True))
    dress(arm_ob, rest, media, outfit)
    gun = B.SETS[set_name]["gun"]
    spec = C.GUNS[gun]
    for part_path, node, m in HP.GUNS[gun]["parts"]:
        before = set(bpy.data.objects)
        HP.load_part(arm_ob, part_path, node, (C.FLIP @ m) if (spec["flip"] and m is not None) else
                     (C.FLIP if spec["flip"] else m))
        for ob in set(bpy.data.objects) - before:
            # texture shading draws a material without an image pale: the part's own colour as a 1-pixel image
            col = ob.data.materials[0].diffuse_color
            ob.data.materials[0] = image_material(ob.name, np.array([[list(col)]], dtype=np.float32))
            if not ob.data.uv_layers:
                ob.data.uv_layers.new(name="UV")
    xa, frames = B.stance_clip(src, os.path.join(out_dir, "_clips"), set_name, clip)
    arm_ob.animation_data.action = None         # the imported idle's keys would pose it over ours
    if frame == "stride":                       # the frame with the feet furthest apart
        ws = [pose.world(xa, q) for q in frames]
        frame = max(range(len(ws)), key=lambda i: (ws[i]["Bip01_L_Foot"].translation -
                                                   ws[i]["Bip01_R_Foot"].translation).length)
    x_import.apply_pose(arm_ob, pose.world(xa, frames[min(frame, len(frames) - 1)]))
    bpy.context.view_layer.update()
    # frame the figure: the camera on a circle round its centre (the character faces -Y)
    body = next(o for o in arm_ob.children if o.name == "Body")
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg).to_mesh()
    pts = [body.matrix_world @ v.co for v in ev.vertices]
    body.evaluated_get(dg).to_mesh_clear()
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (lo + hi) / 2
    a, e = math.radians(yaw), math.radians(elev)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam = x_preview.camera("Cam", tuple(c + d * 6.0), tuple(c))
    cam.data.ortho_scale = ORTHO
    sc = bpy.context.scene
    x_preview.setup_render(sc)
    sc.camera = cam
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.film_transparent = True
    sh = sc.display.shading
    sh.color_type = "TEXTURE"
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.cavity_type = "BOTH"
    sh.curvature_ridge_factor = 0.4
    sh.show_object_outline = False
    sc.view_settings.view_transform = "Standard"
    sc.render.filepath = os.path.join(out_dir, "stance_%s.png" % shot)
    bpy.ops.render.render(write_still=True)
    print("[stance-ad] wrote", sc.render.filepath)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    media, out_dir = args[0], args[1]
    os.makedirs(out_dir, exist_ok=True)
    for shot in args[2:] or list(SHOTS):
        render(media, out_dir, shot)
