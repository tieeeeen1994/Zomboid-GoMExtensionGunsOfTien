"""Blender (5.2, headless) build of the FN P90 TR assets for GoM Extension: Guns of Tien - Post-93.

    Blender -b --factory-startup -P build_p90.py -- --media MEDIA --work WORK [--quick]

MEDIA = Contents/mods/GoMExtensionGunsOfTienPost93/42/media; WORK = a scratch folder holding p90_decals.py's
sheets (make_p90.py runs everything in order). Writes:
  models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx          P90TR_BODY, P90TR_BOLT
  models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx  57x28Magazine50_P90
  models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx          P90_Suppressor, P90_Muzzle_Mount_Device
  textures/weapons/GunsOfTienPost93/{P90TR, 57x28Magazine50_P90, P90_Suppressor, P90_Muzzle_Mount_Device}.png

GoM's FBX recipe (CLAUDE.md, "Gun assets in GoM"): object name = node name = mesh name, mesh data = (game x,
game y, -game z), rotation_euler (90, 0, 0), scale 0.01, export_scene.fbx defaults, no materials. Game space:
+Y muzzle, +Z top, +X the gun's left; the gun's origin is the rear-top of the pistol grip.

Textures: the meshes are UV-unwrapped (smart project + pack) and Cycles bakes, per texel, ambient occlusion, an
edge mask (Bevel node normal against the shading normal), the part id, the position and the true normal. numpy
then paints each texel from those: base colour per part, AO, edge wear, low-frequency grime, fine grain, and the
decal sheets (seams, pins, slots, lettering, stippling) projected by the texel's position and facing, or for the
magazine the rounds seen through the smoky plastic. Bakes are 4x the final size and box-filtered down.
Everything is seeded: the same inputs give the same files.
"""

import json
import math
import os
import struct
import sys
import zlib

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p90_geometry as G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ARGS = {}
i = 0
while i < len(argv):
    if argv[i] == "--quick":
        ARGS["quick"] = True
        i += 1
    else:
        ARGS[argv[i].lstrip("-")] = argv[i + 1]
        i += 2
MEDIA = os.path.abspath(ARGS["media"])
WORK = os.path.abspath(ARGS["work"])
QUICK = ARGS.get("quick", False)
SS = 4                                     # bake supersampling

PART_IDS = {"polymer": 0, "grip": 1, "rail": 2, "metal": 3, "smoke": 4, "supp": 5, "mount": 6}

FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx")
FBX_MAG = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")


# ==================================================================================================
# Meshes
# ==================================================================================================

def gun_xform(x, u, v):
    return G.to_game(x, u, v)


def local_xform(x, u, v):
    return (x * G.S, u * G.S, v * G.S)


def make_object(name, parts, xform, offset=(0.0, 0.0, 0.0)):
    """Object in GoM's raw frame (data = game x, y, -z; rotation 90 deg about X), at scale 1 for baking."""
    bm = bmesh.new()
    pid_layer = bm.faces.layers.float.new("pid")
    for p in parts:
        verts = []
        for (x, u, v) in p["verts"]:
            gx, gy, gz = xform(x, u, v)
            verts.append(bm.verts.new((gx + offset[0], gy + offset[1], -(gz + offset[2]))))
        mats = p.get("face_mats", [p["mat"]] * len(p["faces"]))
        for f, mat in zip(p["faces"], mats):
            try:
                face = bm.faces.new([verts[k] for k in f])
            except ValueError:
                continue
            face[pid_layer] = PART_IDS[mat]
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    # Face attribute -> a FACE float attribute the shader can read.
    attr = me.attributes.get("pid")
    if attr is None or attr.domain != "FACE":
        pass
    for poly in me.polygons:
        poly.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(38))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90), 0.0, 0.0)
    return ob


def unwrap(objects, margin=0.006):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(52), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


# ==================================================================================================
# Baking
# ==================================================================================================

def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.seed = 7
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 6 * SS
    scene.render.bake.margin_type = "EXTEND"
    scene.render.bake.use_clear = True
    world = bpy.data.worlds.new("bake")
    world.light_settings.distance = 0.035            # game units, ~50 mm real
    scene.world = world


def bake_material(ob):
    mat = bpy.data.materials.new("bake_" + ob.name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit.outputs[0], out.inputs[0])
    img = nt.nodes.new("ShaderNodeTexImage")
    img.name = "target"
    nt.nodes.active = img
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    return mat


def set_emission(mat, kind):
    nt = mat.node_tree
    emit = next(n for n in nt.nodes if n.type == "EMISSION")
    for n in list(nt.nodes):
        if n.type not in ("EMISSION", "OUTPUT_MATERIAL", "TEX_IMAGE"):
            nt.nodes.remove(n)
    if kind == "pid":
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "GEOMETRY"
        a.attribute_name = "pid"
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = "MULTIPLY"
        m.inputs[1].default_value = 1.0 / 16.0
        nt.links.new(a.outputs["Fac"], m.inputs[0])
        nt.links.new(m.outputs[0], emit.inputs["Color"])
    elif kind in ("pos", "nrm"):
        g = nt.nodes.new("ShaderNodeNewGeometry")
        v = nt.nodes.new("ShaderNodeVectorMath")
        v.operation = "MULTIPLY_ADD"
        if kind == "pos":
            nt.links.new(g.outputs["Position"], v.inputs[0])
            v.inputs[1].default_value = (1.0, 1.0, 1.0)
        else:
            nt.links.new(g.outputs["True Normal"], v.inputs[0])
            v.inputs[1].default_value = (0.5, 0.5, 0.5)
        v.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(v.outputs[0], emit.inputs["Color"])
    elif kind == "edge":
        g = nt.nodes.new("ShaderNodeNewGeometry")
        b = nt.nodes.new("ShaderNodeBevel")
        b.samples = 16
        b.inputs["Radius"].default_value = 0.0011
        d = nt.nodes.new("ShaderNodeVectorMath")
        d.operation = "DOT_PRODUCT"
        nt.links.new(b.outputs[0], d.inputs[0])
        nt.links.new(g.outputs["Normal"], d.inputs[1])
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = "SUBTRACT"
        m.inputs[0].default_value = 1.0
        nt.links.new(d.outputs["Value"], m.inputs[1])
        k = nt.nodes.new("ShaderNodeMath")
        k.operation = "MULTIPLY"
        k.use_clamp = True
        k.inputs[1].default_value = 5.0
        nt.links.new(m.outputs[0], k.inputs[0])
        nt.links.new(k.outputs[0], emit.inputs["Color"])


def bake_group(objects, size, name):
    """Bake every pass for objects sharing one texture; returns dict of (size, size, 4) float arrays."""
    scene = bpy.context.scene
    res = {}
    mats = [bake_material(ob) for ob in objects]
    img = bpy.data.images.new("bake_" + name, size, size, alpha=False, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    for m in mats:
        m.node_tree.nodes["target"].image = img
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    for kind in ("ao", "edge", "pid", "pos", "nrm"):
        if kind == "ao":
            scene.cycles.samples = 32 if QUICK else 192
            bpy.ops.object.bake(type="AO")
        else:
            scene.cycles.samples = 4 if kind != "edge" else (8 if QUICK else 32)
            if kind in ("pid", "pos", "nrm"):
                scene.cycles.samples = 1
            for m in mats:
                set_emission(m, kind)
            bpy.ops.object.bake(type="EMIT")
        arr = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(arr)
        res[kind] = arr.reshape(size, size, 4)[::-1].copy()      # row 0 = top (v = 1)
        print("[build_p90] baked %s %s" % (name, kind))
    return res


# ==================================================================================================
# Painting (numpy)
# ==================================================================================================

RNG_LATTICE = np.random.default_rng(90).random((32, 32, 32)).astype(np.float32)


def vnoise(p, freq):
    """Trilinear value noise over a fixed 32^3 lattice; p (..., 3) in game units."""
    q = p * freq
    i0 = np.floor(q).astype(np.int64)
    f = q - i0
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (np.where(dx, f[..., 0], 1 - f[..., 0]) * np.where(dy, f[..., 1], 1 - f[..., 1])
                     * np.where(dz, f[..., 2], 1 - f[..., 2]))
                out = out + w * RNG_LATTICE[(i0[..., 0] + dx) % 32, (i0[..., 1] + dy) % 32, (i0[..., 2] + dz) % 32]
    return out


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def load_sheet(info):
    img = bpy.data.images.load(os.path.join(WORK, info["file"]))
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    arr = arr.reshape(h, w, 4)[::-1, :, :3].copy()                  # row 0 = top of the PNG
    return arr, info


def sample_sheet(sheet, a, b):
    """Bilinear sample of a decal sheet at millimetre coords (a horizontal, b vertical)."""
    arr, info = sheet
    h, w = arr.shape[:2]
    fx = (a - info["h_range"][0]) / (info["h_range"][1] - info["h_range"][0])
    fy = (b - info["v_range"][0]) / (info["v_range"][1] - info["v_range"][0])
    if info["flip_h"]:
        fx = 1 - fx
    if info["flip_v"]:
        fy = 1 - fy
    x = np.clip(fx * w - 0.5, 0, w - 1.001)
    y = np.clip(fy * h - 0.5, 0, h - 1.001)
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    tx, ty = (x - x0)[..., None], (y - y0)[..., None]
    c = (arr[y0, x0] * (1 - tx) * (1 - ty) + arr[y0, x0 + 1] * tx * (1 - ty)
         + arr[y0 + 1, x0] * (1 - tx) * ty + arr[y0 + 1, x0 + 1] * tx * ty)
    inside = (fx >= 0) & (fx <= 1) & (fy >= 0) & (fy <= 1)
    return c * inside[..., None]


def decode(b):
    """Game-space position / normal and part id per texel from the bakes."""
    pos = b["pos"][..., :3] - 0.5            # world = (game x, game z, game y)
    nrm = b["nrm"][..., :3] * 2 - 1
    gp = np.stack([pos[..., 0], pos[..., 2], pos[..., 1]], -1)
    gn = np.stack([nrm[..., 0], nrm[..., 2], nrm[..., 1]], -1)
    pid = np.rint(b["pid"][..., 0] * 16).astype(np.int64)
    ao = np.clip(b["ao"][..., 0], 0, 1)
    edge = np.clip(b["edge"][..., 0], 0, 1)
    return gp, gn, pid, ao, edge


def grain(shape, seed, amount):
    return (np.random.default_rng(seed).random(shape).astype(np.float32) - 0.5) * amount


def blur(a, r):
    """Separable box blur (radius r texels), edges clamped."""
    for axis in (0, 1):
        pad = [(0, 0)] * a.ndim
        pad[axis] = (r, r)
        p = np.pad(a, pad, mode="edge")
        c = np.cumsum(p, axis=axis)
        c = np.concatenate([np.zeros_like(np.take(c, [0], axis=axis)), c], axis=axis)
        n = a.shape[axis]
        a = (np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis) - np.take(c, np.arange(0, n), axis=axis)) / (2 * r + 1)
    return a


def finish(col, size):
    """Box-filter the supersampled paint down to the final size, clamp, 8-bit."""
    h = col.shape[0] // size
    col = col.reshape(size, h, size, h, 3).mean(axis=(1, 3))
    return np.clip(np.rint(col * 255), 0, 255).astype(np.uint8)


def shade(base, ao, edge, gp, wear=1.0, seed=1):
    """Common look: AO, edge highlights broken up by noise, grime, grain (all in display sRGB space)."""
    n_lo = vnoise(gp, 60.0)
    n_hi = vnoise(gp + 3.1, 400.0)
    col = base * (0.42 + 0.58 * ao[..., None] ** 1.3)[..., :] if base.ndim == 3 else base
    col = col * (0.9 + 0.2 * n_lo)[..., None]
    scratch = smoothstep(0.35, 0.75, n_hi) * 0.6 + 0.4
    col = col + (0.13 * wear * edge * scratch)[..., None]
    col = col + grain(ao.shape, seed, 0.03)[..., None]
    return col


def paint_gun(b, size):
    gp, gn, pid, ao, edge = decode(b)
    x = gp[..., 0] / G.S
    u = gp[..., 1] / G.S + G.U0
    v = gp[..., 2] / G.S + G.V0
    with open(os.path.join(WORK, "decals.json")) as handle:
        dec = json.load(handle)
    base = np.zeros(pid.shape + (3,), np.float32)
    colours = {0: (0.168, 0.165, 0.160), 1: (0.150, 0.148, 0.145), 2: (0.155, 0.156, 0.162),
               3: (0.205, 0.205, 0.215)}
    for k, c in colours.items():
        base[pid == k] = c
    rear = (u < 7.5) & (gn[..., 1] < -0.3) & (pid == 0)                 # rubber butt plate
    base[rear] = (0.115, 0.113, 0.112)
    # Butt plate ribs.
    ribs = (np.sin(v / 2.2) > 0.55) & rear
    base[ribs] *= 0.72

    col = shade(base, ao, edge * np.where(pid == 3, 1.4, 1.0), gp, seed=11)

    # Decals projected by facing.
    wl = smoothstep(0.45, 0.75, gn[..., 0])
    wr = smoothstep(0.45, 0.75, -gn[..., 0])
    wt = smoothstep(0.45, 0.75, gn[..., 2])
    wb = smoothstep(0.45, 0.75, -gn[..., 2])
    d = np.zeros(pid.shape + (3,), np.float32)
    for w, key, a, bb in ((wl, "side_left", u, v), (wr, "side_right", u, v), (wt, "top", u, x),
                          (wb, "bottom", u, x)):
        d += w[..., None] * sample_sheet(load_sheet(dec[key]), a, bb)
    poly = (pid <= 1)[..., None]
    dark, light, stip = d[..., 0:1], d[..., 1:2], d[..., 2:3]
    col = col * (1 - 0.72 * dark * poly) + 0.16 * light * poly
    st = grain(pid.shape, 23, 1.0)[..., None]
    col = col * (1 - stip * poly * (0.10 + 0.32 * (st > 0.18)))
    # Grip region (pid 1) stippled everywhere.
    gst = (pid == 1)[..., None] * (st > 0.1)
    col = col * (1 - 0.22 * gst)
    # Rail: anodised, slightly blue; deeper AO between the teeth already darkens the slots.
    return finish(col, size)


def mag_rows():
    """Cartridge centres (u along the magazine, v height) in the magazine frame: two staggered rows."""
    pitch = 7.9
    rows = []
    for row, (v, start) in enumerate(((7.2, -46.0), (14.4, -46.0 - pitch / 2))):
        for k in range(24):
            rows.append((start - k * pitch, v, row))
    return rows


def paint_mag(b, size, offset_mm):
    gp, gn, pid, ao, edge = decode(b)
    x = gp[..., 0] / G.S
    u = gp[..., 1] / G.S - offset_mm[0]
    v = gp[..., 2] / G.S - offset_mm[1]
    brass = np.array((0.62, 0.47, 0.22), np.float32)
    brass_dk = np.array((0.42, 0.30, 0.13), np.float32)
    tip = np.array((0.09, 0.09, 0.10), np.float32)
    copper = np.array((0.36, 0.30, 0.26), np.float32)
    tint = np.array((0.17, 0.16, 0.145), np.float32)

    cart = np.zeros(pid.shape + (3,), np.float32)
    seen = np.zeros(pid.shape, np.float32)
    pitch = 7.9
    in_stack = (u < -44.0) & (u > -238.0)
    # Sides: cartridge ends in two staggered rows (+x shows the bullets, -x the case heads).
    side = smoothstep(0.45, 0.75, np.abs(gn[..., 0]))
    best_d = np.full(pid.shape, 99.0, np.float32)
    best_row = np.zeros(pid.shape, np.int64)
    for (cu, cv, row) in mag_rows():
        dd = np.hypot(u - cu, v - cv)
        closer = dd < best_d
        best_d = np.where(closer, dd, best_d)
        best_row = np.where(closer, row, best_row)
    left = gn[..., 0] > 0
    disc = (best_d < 3.95) & in_stack
    end = np.where(left[..., None],
                   np.where((best_d < 1.3)[..., None], tip,
                            np.where((best_d < 2.85)[..., None], copper,
                                     np.where((best_d < 3.25)[..., None], brass, brass_dk))),
                   np.where((best_d < 1.1)[..., None], np.array((0.55, 0.53, 0.50), np.float32),
                            np.where((np.abs(best_d - 2.6) < 0.35)[..., None], brass_dk, brass)))
    end = end * (0.75 + 0.25 * (1 - (best_d / 3.95) ** 2))[..., None]
    end = end * np.where(best_row[..., None] == 0, 0.8, 1.0)
    cart += (side * disc)[..., None] * end
    seen += side * disc * 0.62
    # Top / bottom: rounds lying across, tips to +x; top shows the upper row, bottom the lower one.
    for w, row_start, dim in ((smoothstep(0.45, 0.75, gn[..., 2]), -46.0 - pitch / 2, 1.0),
                              (smoothstep(0.45, 0.75, -gn[..., 2]), -46.0, 0.7)):
        k = np.rint((row_start - u) / pitch)
        du = np.abs(u - (row_start - k * pitch))
        valid = (k >= 0) & (k < 24) & in_stack
        xr = x                                            # -20.25 case head .. +20.25 bullet tip
        rad = np.where(xr < 4.5, 3.95, np.where(xr < 8.65, 3.95 - (xr - 4.5) / 4.15 * 0.75,
                                                 np.clip(2.85 * (1 - ((xr - 8.65) / 11.6) ** 1.6), 0.4, 2.85)))
        rad = np.where((xr < -20.25) | (xr > 20.25), 0.0, rad)
        body = (du < rad) & valid
        colr = np.where((xr < 8.65)[..., None], brass,
                        np.where((xr > 15.5)[..., None], tip, copper))
        colr = np.where(((xr > -20.25) & (xr < -18.6))[..., None], brass_dk, colr)
        roundness = np.sqrt(np.clip(1 - (du / np.maximum(rad, 1e-3)) ** 2, 0, 1))
        colr = colr * (0.55 + 0.55 * roundness)[..., None] * dim
        cart += (w * body)[..., None] * colr
        seen += w * body * 0.6
        # Gaps between rounds show the other row, darker.
        gap = (~body) & valid & (np.abs(xr) < 20.0)
        cart += (w * gap)[..., None] * brass_dk * 0.45 * dim
        seen += w * gap * 0.45
    # Follower at the rear of the stack.
    foll = (u <= -238.0) & (u > -246.0)
    cart += (foll * np.maximum(side, 0.0))[..., None] * np.array((0.12, 0.12, 0.12), np.float32)
    seen += foll * side * 0.5

    smoke = pid == 4
    base = np.where(smoke[..., None], tint, np.array((0.155, 0.152, 0.150), np.float32))
    col = shade(base, ao, edge, gp, wear=0.8, seed=31)
    through = (seen * smoke)[..., None]
    col = col * (1 - through) + through * (cart * (0.55 + 0.45 * ao[..., None]) * 0.85 + tint * 0.25)
    # Plastic sheen: soft light band along the upper side faces and the top.
    sheen = smoke * (side * smoothstep(17.0, 23.0, v) * 0.06 + smoothstep(0.6, 0.9, gn[..., 2]) * 0.025)
    col = col + sheen[..., None]
    return finish(col, size)


def paint_lathe(b, size, kind):
    gp, gn, pid, ao, edge = decode(b)
    u = gp[..., 1] / G.S
    ang = np.arctan2(gp[..., 0], gp[..., 2])
    with open(os.path.join(WORK, "decals.json")) as handle:
        dec = json.load(handle)
    if kind == "supp":
        base = np.zeros(pid.shape + (3,), np.float32) + np.array((0.150, 0.150, 0.155), np.float32)
        sheet = load_sheet(dec["supp_wrap"])
        rad = G.SUPP_R
    else:
        base = np.zeros(pid.shape + (3,), np.float32) + np.array((0.185, 0.185, 0.192), np.float32)
        sheet = load_sheet(dec["mount_wrap"])
        rad = G.MOUNT_R
    col = shade(base, ao, edge * 1.3, gp, wear=1.2, seed=41 if kind == "supp" else 43)
    radial = 1 - smoothstep(0.5, 0.8, np.abs(gn[..., 1]))      # not the end faces
    d = sample_sheet(sheet, u, ang * rad) * radial[..., None]
    col = col * (1 - 0.65 * d[..., 0:1]) + 0.15 * d[..., 1:2]
    kn = d[..., 2:3]
    col = col * (1 - 0.35 * kn) + 0.05 * kn * (grain(pid.shape, 5, 1.0)[..., None] > 0)
    # Bore: dark inside the front opening.
    front = (gn[..., 1] > 0.5) & (np.hypot(gp[..., 0], gp[..., 2]) / G.S < (6.5 if kind == "supp" else 7.5))
    col[front] *= 0.25
    return finish(col, size)


# ==================================================================================================
# Output
# ==================================================================================================

def write_png(path, rgb):
    """8-bit RGB PNG, no metadata (deterministic)."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    print("[build_p90] wrote", path)


def export(objects, path, offset=(0.0, 0.0, 0.0)):
    """GoM recipe: clean copies (no materials or attributes), scale 0.01, rotation (90, 0, 0), defaults."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    copies = []
    for ob in objects:
        me = ob.data.copy()
        me.materials.clear()
        for a in [a for a in me.attributes if a.name == "pid"]:
            me.attributes.remove(a)
        if any(offset):
            me.transform(__import__("mathutils").Matrix.Translation((-offset[0], -offset[1], offset[2])))
        name = ob.name.split("__")[0]
        me.name = name
        cp = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(cp)
        cp.rotation_euler = (math.radians(90), 0.0, 0.0)
        cp.scale = (0.01, 0.01, 0.01)
        copies.append(cp)
    bpy.ops.object.select_all(action="DESELECT")
    for cp in copies:
        cp.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True)
    for cp in copies:
        me = cp.data
        bpy.data.objects.remove(cp)
        bpy.data.meshes.remove(me)
    print("[build_p90] wrote", path)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_scene()
    mag_off = G.to_game(0, G.MAG_FRONT_U, G.MAG_BASE_V)

    # Working names get a "__w" suffix so the export copies can take the node names.
    body = make_object("P90TR_BODY__w", G.body_parts(), gun_xform)
    bolt = make_object("P90TR_BOLT__w", G.bolt_parts(), gun_xform)
    mag = make_object("57x28Magazine50_P90__w", G.magazine_parts(), local_xform, mag_off)
    supp = make_object("P90_Suppressor__w", G.suppressor_parts(), local_xform)
    mount = make_object("P90_Muzzle_Mount_Device__w", G.mount_parts(), local_xform)
    for ob in (body, bolt, mag, supp, mount):
        print("[build_p90] %-30s %5d tris" % (ob.name, tri_count(ob)))

    unwrap([body, bolt], 0.004)
    unwrap([mag], 0.008)
    unwrap([supp], 0.008)
    unwrap([mount], 0.01)

    # Export the meshes (UVs are final now).
    export([body, bolt], FBX_GUN)
    export([mag], FBX_MAG, offset=mag_off)
    export([supp, mount], FBX_PARTS)

    # Bake. The magazine stays in place while the gun bakes (contact shadows), and the gun while the magazine
    # bakes; the suppressor and mount bake alone (moved apart so they do not shade each other).
    supp.location.x = 1.0
    mount.location.x = 2.0
    gun_size = 256 * SS
    small = 128 * SS
    b = bake_group([body, bolt], gun_size, "gun")
    write_png(os.path.join(TEX, "P90TR.png"), paint_gun(b, 256))
    b = bake_group([mag], small, "mag")
    mag_mm = (G.MAG_FRONT_U - G.U0, G.MAG_BASE_V - G.V0)
    write_png(os.path.join(TEX, "57x28Magazine50_P90.png"), paint_mag(b, 128, mag_mm))
    supp.location.x = 0.0
    b = bake_group([supp], small, "supp")
    write_png(os.path.join(TEX, "P90_Suppressor.png"), paint_lathe(b, 128, "supp"))
    supp.location.x = 1.0
    mount.location.x = 0.0
    b = bake_group([mount], small, "mount")
    write_png(os.path.join(TEX, "P90_Muzzle_Mount_Device.png"), paint_lathe(b, 128, "mount"))


main()
