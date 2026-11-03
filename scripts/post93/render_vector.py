"""Review renders of the exported KRISS Vector assets, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_vector.py -- OUT_DIR

Imports what build_vector.py wrote, places every part at vector_points.json the way the engine does (offset, then
rotateXYZ in degrees, game space) and renders orthographic Workbench views into OUT_DIR: the Vector .45's left side
at its reference drawing's scale with the 30-round magazine (for the outline check in make_vector_art.py), both guns'
right side and 3/4 views, the stock folded, every magazine, GoM's optic, foregrip, light and laser at their points
(the light and laser on our side rails), the 30-round copy on the main mod's Glock 21 and the 33 / 40 copies on GoM's
Glock 17, the Glock 21 magazine against GoM's Glock 17 one at their Bip01_Prop2 points (the hand's frame), and GoM's
MP5 at the same scale. Game space is Blender world space, the mirror image of what the game shows; make_vector_art.py
flips every render left-right.
"""

import json
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy                                # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
OUT = sys.argv[sys.argv.index("--") + 1]
PTS = json.load(open(os.path.join(HERE, "vector_points.json")))
FIRE = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTOR.fbx")
FIRE_CRB = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTORCRB.fbx")
PTS_CRB = json.load(open(os.path.join(HERE, "vectorcrb_points.json")))
FIRE_SDP = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTORSDP.fbx")
PTS_SDP = json.load(open(os.path.join(HERE, "vectorsdp_points.json")))
PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_VECTOR_parts.fbx")
MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_VECTOR_magazines.fbx")
MAG_NAMES = ["45Magazine13_VECTOR", "45Magazine30_VECTOR", "9x19Magazine17_VECTOR", "9x19Magazine33_VECTOR",
             "9x19Magazine40_VECTOR"]


# load / place / render: render_ump.py's (rifles are upright, nothing is turned)
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


def retexture(o, texture):
    img = bpy.data.images.load(texture, check_existing=True)
    o.data.materials[0].node_tree.nodes["Image Texture"].image = img


def place(o, point=None):
    """Engine attachment transform: translate(offset) . rotateXYZ(rotate); mesh data z is game -z."""
    import math
    from mathutils import Matrix
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


def render(name, direction, centre, scale, w, h):
    import math
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


def gom(cat, name, tex_dir):
    return load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                os.path.join(GOM, "textures/weapons/%s/%s.png" % (tex_dir, name)), keep=name)[name]


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

    objs = load(FIRE, os.path.join(TEX, "VECTOR45.png"))
    guns = objs
    body, bolt, handle = objs["VECTOR_BODY"], objs["VECTOR_BOLT"], objs["VECTOR_HANDLE"]
    rail_l, rail_r = objs["VECTOR_RAIL_LEFT"], objs["VECTOR_RAIL_RIGHT"]
    stock = load(PARTS, os.path.join(TEX, "VECTOR45_STOCK.png"), keep="VECTOR_STOCK")["VECTOR_STOCK"]
    mags = {n: load(MAGS, os.path.join(TEX, n + ".png"), keep=n)[n] for n in MAG_NAMES}
    g_parts = {}
    if GOM:
        for cat, name, tex in (("parts/scopes", "Aimpoint_Sight", "parts/scopes"),
                               ("parts/scopes", "EXPS3_Sight", "parts/scopes"),
                               ("parts/foregrips", "MKC_Foregrip", "parts/foregrips"),
                               ("parts/pointers", "SR7_Light", "parts/pointers"),
                               ("parts/pointers", "AimRight_Laser", "parts/pointers"),
                               ("parts/muzzles", "Muzzle_Mount_Device", "parts/muzzles"),
                               ("parts/suppressors", "P45_Suppressor", "parts/suppressors")):
            try:
                g_parts[name] = gom(cat, name, tex)
            except Exception as e:
                print("skip", name, e)
    crb = load(FIRE_CRB, os.path.join(TEX, "VECTORCRB.png"), keep="VECTORCRB_BODY")["VECTORCRB_BODY"]
    crb_stock = load(FIRE_CRB, os.path.join(TEX, "VECTORCRB_STOCK.png"), keep="VECTORCRB_STOCK")["VECTORCRB_STOCK"]

    p = PTS

    def state(gun, mag, folded=False, extra=(), rails=False):
        nonlocal p
        # the CRB: its own body, stock and points, the .45's other nodes and texture
        is_crb = gun == "VECTORCRB"
        b, st = (crb, crb_stock) if is_crb else (body, stock)
        p = PTS_CRB if is_crb else PTS
        tex = "VECTOR45" if is_crb else gun
        for o in (bolt, handle, rail_l, rail_r):
            retexture(o, os.path.join(TEX, tex + ".png"))
        if not is_crb:
            retexture(body, os.path.join(TEX, gun + ".png"))
            retexture(stock, os.path.join(TEX, gun + "_STOCK.png"))
        place(b)
        place(bolt)
        place(handle)
        place(st, p["stock_folded"] if folded else p["stock"])
        shown = [b, bolt, handle, st]
        if rails:
            place(rail_l, p["rail_left"])
            place(rail_r, p["rail_right"])
            shown += [rail_l, rail_r]
        if mag:
            place(mags[mag], p["magazine"])
            shown.append(mags[mag])
        for name, point in extra:
            o = g_parts.get(name)
            if o is not None:
                place(o, p[point])
                shown.append(o)
        show_only(shown)

    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    k = p["_extras"]["k"]
    L0, H0 = p["_extras"]["photo_origin_mm"]
    length = 760.0
    lmid = (p["_bounds"]["VECTOR_BODY"]["max"][1] + p["_bounds"]["VECTOR_STOCK_deployed"]["min"][1]) / 2.0
    zc = -0.03
    centre = Vector((0.0, lmid, zc))
    w = 1600
    cams = {}
    state("VECTOR45", "45Magazine30_VECTOR")
    render("V45_left", left, centre, length * k, w, 800)
    cams["V45_left"] = {"centre_game": [0.0, lmid, zc], "px_per_mm": w / length, "size": [w, 800],
                        "photo_origin_mm": [L0, H0], "k": k}
    render("V45_right", right, centre, length * k, w, 800)
    render("V45_q_left", q_left, centre, length * k, w, 900)
    render("V45_q_right", q_right, centre, length * k, w, 900)
    render("V45_top", (0, 0, -1), centre, length * k, w, 360)
    state("VECTOR45", "45Magazine13_VECTOR")
    render("V45_13_left", left, centre, length * k, w, 800)
    state("VECTOR9", "9x19Magazine17_VECTOR")
    render("V9_left", left, centre, length * k, w, 800)
    render("V9_right", right, centre, length * k, w, 800)
    render("V9_q_right", q_right, centre, length * k, w, 900)
    for n in ("9x19Magazine33_VECTOR", "9x19Magazine40_VECTOR"):
        state("VECTOR9", n)
        render("V9_%s_left" % n.split("Magazine")[1].split("_")[0], left, centre, length * k, w, 800)
    state("VECTOR9", "9x19Magazine17_VECTOR", folded=True)
    render("V9_folded_q", q_right, centre, length * k, w, 900)
    render("V9_folded_top", (0, 0, -1), centre, length * k, w, 360)
    render("V9_folded_right", right, centre, length * k, w, 800)
    state("VECTOR45", None)
    render("V_nomag_under", (0.25, -0.2, 0.95), centre, length * k, w, 700)
    extra = [("Aimpoint_Sight", "scope"), ("MKC_Foregrip", "foregrip"), ("SR7_Light", "light_left"),
             ("AimRight_Laser", "laser_right")]
    state("VECTOR45", "45Magazine30_VECTOR", extra=extra, rails=True)
    render("V45_fitted_q", q_left, centre, (length + 100) * k, w, 900)
    render("V45_fitted_qr", q_right, centre, (length + 100) * k, w, 900)
    render("V45_fitted_front", (0, -1, 0), Vector((0.0, 0.0, zc)), 0.2, 700, 700)

    # the Vector CRB: the 16" barrel's shroud on the .45 (vectorcrb_points.json), longer, so a wider frame
    clen = 1080.0
    cmid = (PTS_CRB["_bounds"]["VECTORCRB_BODY"]["max"][1]
            + PTS_CRB["_bounds"]["VECTORCRB_STOCK_deployed"]["min"][1]) / 2.0
    cc = Vector((0.0, cmid, zc))
    state("VECTORCRB", "45Magazine13_VECTOR")
    render("CRB_left", left, cc, clen * k, w, 640)
    render("CRB_right", right, cc, clen * k, w, 640)
    render("CRB_q_left", q_left, cc, clen * k, w, 760)
    render("CRB_top", (0, 0, -1), cc, clen * k, w, 300)
    render("CRB_front", (0, -1, 0), Vector((0.0, 0.0, zc)), 0.2, 700, 700)
    state("VECTORCRB", "45Magazine30_VECTOR", folded=True)
    render("CRB_folded_q", q_right, cc, clen * k, w, 760)
    state("VECTORCRB", "45Magazine30_VECTOR", extra=extra + [("Muzzle_Mount_Device", "canon"),
                                                             ("P45_Suppressor", "canon")], rails=True)
    render("CRB_fitted_q", q_left, cc, (clen + 200) * k, w, 800)
    render("CRB_fitted_left", left, Vector((0.0, cmid + 0.03, zc)), (clen + 200) * k, w, 600)
    p = PTS

    # The Vector 9mm as the game assembles it: held like a pistol, its turned nodes (VECTOR9_*) and the upright parts at
    # vector9_points.json, the whole turned back upright here (a half turn about Y): these must match V9_left,
    # V45_fitted_q and V9_folded_top pixel for pixel in outline.
    import math
    from mathutils import Matrix
    p9 = json.load(open(os.path.join(HERE, "vector9_points.json")))
    up = Matrix.Rotation(math.pi, 4, 'Y')
    t9 = {n: guns[n] for n in ("VECTOR9_BODY", "VECTOR9_BOLT", "VECTOR9_HANDLE", "VECTOR9_RAIL_LEFT",
                               "VECTOR9_RAIL_RIGHT")}
    for o in t9.values():
        retexture(o, os.path.join(TEX, "VECTOR9.png"))
    stock9 = load(PARTS, os.path.join(TEX, "VECTOR9_STOCK.png"), keep="VECTOR9_STOCK")["VECTOR9_STOCK"]

    def pistol(mag, folded=False, extra=(), rails=False):
        placed = [(t9["VECTOR9_BODY"], None), (t9["VECTOR9_BOLT"], None), (t9["VECTOR9_HANDLE"], None),
                  (stock9, p9["stock_folded"] if folded else p9["stock"])]
        if rails:
            placed += [(t9["VECTOR9_RAIL_LEFT"], p9["rail_left"]), (t9["VECTOR9_RAIL_RIGHT"], p9["rail_right"])]
        if mag:
            placed.append((mags[mag], p9["magazine"]))
        placed += [(g_parts[n], p9[pt]) for n, pt in extra if n in g_parts]
        for o, point in placed:
            place(o, point)
            o.matrix_world = up @ o.matrix_world
        show_only([o for o, _ in placed])

    pistol("9x19Magazine17_VECTOR")
    render("V9_pistol_left", left, centre, length * k, w, 800)
    pistol("9x19Magazine17_VECTOR", folded=True)
    render("V9_pistol_folded_top", (0, 0, -1), centre, length * k, w, 360)
    pistol("9x19Magazine17_VECTOR", extra=extra, rails=True)
    render("V9_pistol_fitted_q", q_left, centre, (length + 100) * k, w, 900)

    # The Vector SDP the same way: its own turned body, the 9mm's turned bolt, handle and side rails, at
    # vectorsdp_points.json, turned back upright; SDP_photo is the right side at the photo's scale and framing
    # (references/vector/sdp_right.png: 4.78 px per mm, 2048 x 1717, centre at L 182, H 51.7) for the overlay check.
    sdp = load(FIRE_SDP, os.path.join(TEX, "VECTORSDP.png"))["VECTORSDP_BODY"]

    def sdp_state(mag, extra=(), rails=False):
        placed = [(sdp, None), (t9["VECTOR9_BOLT"], None), (t9["VECTOR9_HANDLE"], None)]
        if rails:
            placed += [(t9["VECTOR9_RAIL_LEFT"], PTS_SDP["rail_left"]), (t9["VECTOR9_RAIL_RIGHT"], PTS_SDP["rail_right"])]
        if mag:
            placed.append((mags[mag], PTS_SDP["magazine"]))
        placed += [(g_parts[n], PTS_SDP[pt]) for n, pt in extra if n in g_parts]
        for o, point in placed:
            place(o, point)
            o.matrix_world = up @ o.matrix_world
        show_only([o for o, _ in placed])

    sdp_state("9x19Magazine33_VECTOR", rails=True)
    L0p, H0p = PTS["_extras"]["photo_origin_mm"]
    render("SDP_photo", right, Vector((0.0, (L0p - 182.0) * k, (51.7 - H0p) * k)), 2048 / 4.78 * k, 2048, 1717)
    sdp_state("9x19Magazine17_VECTOR")
    render("SDP_left", left, centre, length * k, w, 800)
    render("SDP_right", right, centre, length * k, w, 800)
    render("SDP_q_left", q_left, centre, length * k, w, 900)
    render("SDP_q_right", q_right, centre, length * k, w, 900)
    sdp_state("9x19Magazine40_VECTOR", extra=extra, rails=True)
    render("SDP_fitted_q", q_left, centre, (length + 100) * k, w, 900)
    for n, m in mags.items():
        place(m)
        show_only([m])
        render("mag_" + n, left, Vector((0, -0.02, -0.08)), 0.2, 500, 700)

    # the pistol copies on their guns (gun space: the guns' magazines carry no point), at the pistols' own scale
    pmags = load(MAGS, os.path.join(MAIN, "textures/weapons/GunsOfTien/45Magazine13_GLOCK21.png"),
                 keep="45Magazine30_GLOCK21")
    g21 = load(os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_GLOCK21.fbx"),
               os.path.join(MAIN, "textures/weapons/GunsOfTien/GLOCK21.png"))
    g21_13 = load(os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx"),
                  os.path.join(MAIN, "textures/weapons/GunsOfTien/45Magazine13_GLOCK21.png"))["45Magazine13_GLOCK21"]
    for o in list(g21.values()) + list(pmags.values()) + [g21_13]:
        place(o)
    show_only(list(g21.values()) + list(pmags.values()))
    render("G21_30_left", left, Vector((0.0, 0.04, 0.05)), 0.26, 700, 900)
    if GOM:
        gtex = os.path.join(GOM, "textures/weapons/magazines/pistols/9x19Magazine17_Glock.png")
        g17 = load(os.path.join(GOM, "models_X/weapons/firearms/GLOCK17.fbx"),
                   os.path.join(GOM, "textures/weapons/firearms/pistols/GLOCK17.png"))
        g17_17 = load(os.path.join(GOM, "models_X/weapons/magazines/pistols.fbx"), gtex,
                      keep="9x19Magazine17_GLOCK17")["9x19Magazine17_GLOCK17"]
        copies = {n: load(MAGS, gtex, keep=n)[n] for n in ("9x19Magazine33_GLOCK17", "9x19Magazine40_GLOCK17")}
        for o in list(g17.values()) + list(copies.values()) + [g17_17]:
            place(o)
        for n, o in copies.items():
            show_only(list(g17.values()) + [o])
            render("G17_%s_left" % n.split("Magazine")[1].split("_")[0], left, Vector((0.0, 0.04, 0.06)), 0.3,
                   700, 1000)
        # the hand's frame: GoM's magazine at its Bip01_Prop2, the Glock 21's at the one build_vector.py worked out
        prop = p["_extras"]["pistol_magazines"]
        place(g17_17, prop["glock17_prop2"])
        place(g21_13, prop["glock21_45Magazine13_prop2"])
        show_only([g17_17, g21_13])
        render("prop2_left", left, Vector((0.0, 0.0, 0.0)), 0.2, 700, 700)
        render("prop2_front", (0, -1, 0), Vector((0.0, 0.0, 0.0)), 0.2, 700, 700)
        objs = load(os.path.join(GOM, "models_X/weapons/firearms/MP5.fbx"),
                    os.path.join(GOM, "textures/weapons/firearms/smgs/MP5.png"))
        for o in objs.values():
            place(o)
        show_only(list(objs.values()))
        ys = [(o.matrix_world @ Vector(c)).y for o in objs.values() for c in o.bound_box]
        render("gom_MP5", left, Vector((0.0, (min(ys) + max(ys)) / 2.0, -0.01)), length * k * 1.25, int(w * 1.25),
               700)
    json.dump(cams, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)


main()
