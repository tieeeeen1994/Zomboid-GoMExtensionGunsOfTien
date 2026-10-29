"""Review renders of the exported AUG A3-receiver guns, read back from the FBX files (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/render_aug3.py -- OUT_DIR [--gun a3]

Imports what build_aug3.py wrote, with the main mod's A1 charging handle, folding grip and magazines, places every part
at <gun>_points.json the way the engine does (offset, then rotateXYZ in degrees, game space) and renders orthographic
Workbench views into OUT_DIR: the right side at the reference photo's scale (2.575 px/mm, for the overlay in
make_aug3_sheet.py), the left side, 3/4 views, top and front, the grip folded with the handle back, and the gun dressed
with GoM's parts at their points (ElcanX2 on the rail, the optional left rail (our AUG_RAIL_LEFT) with an SR7 light, the AimRight
laser on the right rail, the AR mount device with the MKI suppressor). Game space is Blender world space, the mirror
image of what the game shows; the sheet flips every render left-right.
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
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
MAIN_TEX = os.path.join(MAIN, "textures/weapons/GunsOfTien")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = ARGS[0]
GUN = ARGS[ARGS.index("--gun") + 1] if "--gun" in ARGS else "a3"
NAME = {"a3": "AUGA3", "para": "AUGPARA", "hbar": "AUGHBAR"}[GUN]
PTS = json.load(open(os.path.join(HERE, NAME.lower() + "_points.json")))
K = PTS["_extras"]["k"]
L0, H0 = PTS["_extras"]["photo_origin_mm"]
PX_PER_MM = 2.575                   # the Interpolitex photo's scale (sheet overlay)
LMAX, HMAX = 790.0, 200.0


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


def gom(cat, name, tex):
    return load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                os.path.join(GOM, "textures/weapons/%s.png" % tex), keep=[name])[name]


def main():
    global LMAX
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

    own = load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_%s.fbx" % NAME),
               os.path.join(TEX, NAME + ".png"))
    body = own[NAME + "_BODY"]
    # every A3-receiver gun draws the A3's short left rail
    rail = own.get("AUG_RAIL_LEFT") or load(os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_AUGA3.fbx"),
                                            os.path.join(TEX, "AUGA3.png"), keep=["AUG_RAIL_LEFT"])["AUG_RAIL_LEFT"]
    # every AUG draws the A1's bolt carrier; the Para its own sand handle and grip, the others the A1's
    a1 = load(os.path.join(MAIN, "models_X/weapons/firearms/GunsOfTien_AUG.fbx"),
              os.path.join(MAIN_TEX, "AUG.png"), keep=["AUG_BOLT", "AUG_HANDLE", "AUG_FOREGRIP"])
    bolt = a1["AUG_BOLT"]
    if NAME + "_HANDLE" in own:                          # the Para's own sand copies
        handle, fg = own[NAME + "_HANDLE"], own[NAME + "_FOREGRIP"]
    else:
        handle, fg = a1["AUG_HANDLE"], a1["AUG_FOREGRIP"]
    own_mags = {"para": ("9x19Magazine%d_AUG", (25, 32)), "hbar": ("762x39Magazine%d_AUG", (30, 50))}
    if GUN in own_mags:
        fmt, counts = own_mags[GUN]
        mags = {r: load(os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_AUG_magazines.fbx"),
                        os.path.join(TEX, (fmt % r) + ".png"), keep=[fmt % r])[fmt % r] for r in counts}
    else:
        mags = {r: load(os.path.join(MAIN, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx"),
                        os.path.join(MAIN_TEX, "556x45Magazine%d_AUG.png" % r), keep=["556x45Magazine%d_AUG" % r])
                ["556x45Magazine%d_AUG" % r] for r in (30, 42)}
    mag = mags[min(mags)]
    parts = {}
    if GOM:
        for cat, name, tex, point in (("parts/scopes", "ElcanX2_Scope", "parts/scopes/ElcanX2_Scope", "scope"),
                                      ("parts/pointers", "SR7_Light", "parts/pointers/SR7_Light", "light_left"),
                                      ("parts/pointers", "AimRight_Laser", "parts/pointers/AimRight_Laser",
                                       "laser_right"),
                                      ("parts/muzzles", "Muzzle_Mount_Device", "parts/muzzles/Muzzle_Mount_Device",
                                       "canon"),
                                      ("parts/suppressors", "MKI_Suppressor", "parts/suppressors/MKI_Suppressor",
                                       "canon")):
            try:
                parts[name] = (gom(cat, name, tex), point)
            except Exception as e:                       # a texture named differently: skip that part
                print("skip", name, e)

    parts["Picatinny_Rail_Left"] = (rail, "rail_left")   # GoM's item, our short model
    # the main mod's 9x19mm SMG mount and Mk9, drawn on our guns with the *_GoT models (scale 0.8375)
    smg = load(os.path.join(MAIN, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx"),
               os.path.join(MAIN_TEX, "SMG9_Muzzle_Mount_Device.png"), keep=["SMG9_Muzzle_Mount_Device"])
    sup = load(os.path.join(MAIN, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx"),
               os.path.join(MAIN_TEX, "Mk9_Suppressor.png"), keep=["Mk9_Suppressor"])
    parts["SMG9_Muzzle_Mount_Device"] = (smg["SMG9_Muzzle_Mount_Device"], "canon", 0.8375)
    parts["Mk9_Suppressor"] = (sup["Mk9_Suppressor"], "canon", 0.8375)
    mount, can = {"para": ("SMG9_Muzzle_Mount_Device", "Mk9_Suppressor"),
                  "hbar": (None, None)}.get(GUN, ("Muzzle_Mount_Device", "MKI_Suppressor"))
    bipods = {k: own.get("AUGHBAR_BIPOD_" + k.upper()) for k in ("folded", "deployed")}

    def state(folded=False, fired=False, with_mag=True, dressed=(), bipod="folded", racked=False):
        """fired: the bolt carrier back (each shot, held open when empty); racked: the handle back as well."""
        place(body)
        place(bolt, PTS["bolt_fired"] if fired or racked else None)
        place(handle, PTS["handle_back"] if racked else None)
        place(fg, PTS["foregrip_folded" if folded else "foregrip_deployed"])
        shown = [body, bolt, handle, fg]
        if bipods[bipod] is not None:
            place(bipods[bipod], PTS["integrated_bipod"])
            shown.append(bipods[bipod])
        if with_mag:
            place(mag, PTS["magazine"])
            shown.append(mag)
        for name in dressed:
            if name in parts:
                o, point = parts[name][:2]
                place(o, PTS[point])
                if len(parts[name]) > 2:
                    o.matrix_world = o.matrix_world @ Matrix.Diagonal((parts[name][2],) * 3 + (1.0,))
                shown.append(o)
        show_only(shown)

    if GUN == "hbar":                                     # 110 mm longer, the bipod's feet below
        LMAX = 900.0
    span, tall = LMAX + 120.0, HMAX + 160.0
    w, h = int(span * PX_PER_MM), int(tall * PX_PER_MM)
    L_mid = LMAX / 2.0 - (110.0 if GUN == "hbar" else 0.0)
    centre = Vector((0.0, (L0 - L_mid) * K, (HMAX / 2.0 - H0 - 20.0) * K))
    left, right = (-1, 0, 0), (1, 0, 0)
    q_left, q_right = (-0.62, -0.5, -0.45), (0.7, -0.45, -0.5)
    state()
    render(NAME + "_right", right, centre, span, w, h)
    json.dump({NAME: {"px_per_mm": PX_PER_MM, "size": [w, h], "centre_mm": [L_mid, HMAX / 2.0 - 20.0],
                      "span_mm": [span, tall]}}, open(os.path.join(OUT, "cameras.json"), "w"), indent=1)
    render(NAME + "_left", left, centre, span, w, h)
    render(NAME + "_q_right", q_right, centre, span, w, int(h * 1.15))
    render(NAME + "_q_left", q_left, centre, span, w, int(h * 1.15))
    render(NAME + "_top", (0, 0, -1), centre, span, w, int(140 * PX_PER_MM))
    render(NAME + "_front", (0, -1, 0), centre + Vector((0, 0, 0.02)), 260, 520, 640)
    state(folded=True, fired=True)
    render(NAME + "_folded_fired_left", left, centre, span, w, h)
    dressed = ("ElcanX2_Scope", "Picatinny_Rail_Left", "SR7_Light", "AimRight_Laser", mount)
    state(folded=True, dressed=dressed)
    render(NAME + "_dressed_left", left, centre, span, w, h)
    render(NAME + "_dressed_right", right, centre, span, w, h)
    render(NAME + "_dressed_q_left", q_left, centre, span, w, int(h * 1.15))
    render(NAME + "_dressed_top", (0, 0, -1), centre, span, w, int(140 * PX_PER_MM))
    # the short left rail alone, the charging handle forward and back (its path must clear the rail)
    near = Vector((0.0, (L0 - 300.0) * K, (135.0 - H0) * K))
    for fired in (False, True):
        state(fired=fired, dressed=("Picatinny_Rail_Left",))
        render(NAME + "_rail_left_%s" % ("back" if fired else "forward"), left, near, 260, 1040, 640)
        render(NAME + "_rail_left_q_%s" % ("back" if fired else "forward"), q_left, near, 260, 1040, 760)
    state(dressed=("ElcanX2_Scope", mount, can))
    render(NAME + "_suppressed_right", right, centre, span + 200, int((span + 200) * PX_PER_MM), h)
    if bipods["deployed"] is not None:                   # the HBAR on its legs, grip unfolded and folded
        for folded in (False, True):
            state(folded=folded, bipod="deployed")
            tag = "_folded" if folded else ""
            render(NAME + "_bipod%s_left" % tag, left, centre, span, w, int(h * 1.25))
            render(NAME + "_bipod%s_q_left" % tag, q_left, centre, span, w, int(h * 1.35))
            render(NAME + "_bipod%s_front" % tag, (0, -1, 0), centre + Vector((0, 0, 0.0)), 300, 600, 640)
        state(folded=True)
        render(NAME + "_folded_bottom", (0, 0, 1), centre, span, w, int(140 * PX_PER_MM))
    for r, m in mags.items():                            # every magazine fitted, and alone
        state(folded=True)
        place(mag)
        place(m, PTS["magazine"])
        show_only([body, bolt, handle, fg, m])
        render(NAME + "_mag%d_left" % r, left, centre, span, w, int(h * 1.2))
        if bipods["deployed"] is not None:               # standing on its legs with this magazine
            place(bipods["deployed"], PTS["integrated_bipod"])
            show_only([body, bolt, handle, fg, m, bipods["deployed"]])
            render(NAME + "_mag%d_bipod_left" % r, left, centre, span, w, int(h * 1.3))
            render(NAME + "_mag%d_bipod_q_left" % r, q_left, centre, span, w, int(h * 1.4))
        place(m)
        show_only([m])
        render("mag%d_left" % r, left, Vector((0, 0.0, -0.06)), 260, 520, 600)
        render("mag%d_q" % r, q_right, Vector((0, 0.0, -0.06)), 260, 520, 600)
        render("mag%d_rear" % r, (0, 1, 0), Vector((0, 0.0, -0.05)), 300, 600, 520)
        render("mag%d_front" % r, (0, -1, 0), Vector((0, 0.0, -0.05)), 300, 600, 520)


main()
