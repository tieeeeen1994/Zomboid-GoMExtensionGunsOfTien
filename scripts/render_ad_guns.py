"""The Post-93 guns, fitted out, for the Workshop art (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/render_ad_guns.py -- OUT_DIR [NAME ...]

Renders OUT_DIR/ad_<name>.png (all of GUNS, or the names given): transparent orthographic Workbench renders of the
exported FBX files and textures. The MP7 and the P90 share one angle and scale (so the two keep their real sizes
against each other), muzzle to the right, seen from the left a little behind and above; the Five-seveN and the UCP
share another scale, each from the side its markings are on. Parts are placed at the guns' attachment points the way
the engine does (scripts/post93/render_p90.py); all four are held like pistols and so modelled upside down, so
everything is turned back upright. Game space is used as world space, the mirror image of the game
(render_fiveseven.py): the pistols' renders (`flip`) are mirrored back by make_workshop_art.py, which lays them out.

The main mod's sawn-off shotgun (preview5): GoM's Double Barrel whole (`db_full`: GoM's body and full barrels) and
sawn off (`db_sawn`: our stockless body from GunsOfTien_SawnStocks.fbx and GoM's sawn-off barrels), one view and scale
so the two keep their sizes against each other. GoM's rifle-held guns are modelled upright, so `files` specs are not
turned; their barrels are drawn at the gun's origin, as the engine draws them (no attachment point).

The SCAR-L and SCAR-H (preview6) are rifles, modelled upright (`rifle`: nothing turned), one view and scale so they
keep their real sizes against each other, the double barrel's view (mirrored back by make_workshop_art.py). A node
entry's file may name a folder (`parts/...`: the shared stock), and the SCAR-L's magazine is GoM's STANAG (`gom_mag`).
The UMP45 and UMP9 (preview7) the same way, from one body file with each gun's texture.

The suppressors added 2026-10-22 (preview8), one view and scale: the main mod's AWC Mk9 on GoM's MP5 and MP5A2
(`gom_smg`: GoM's own body, bolt, stock and 30-round magazine at its model script's magazine point, the Mk9 and its
mount device at the `canon` point build_mk9.py measured, scripts/smg9_points.json; the game gets it from
Suppressors.lua at run time) and on the UMP9 (`main_parts`), and GoM's P45 on the UMP45.

The main mod's M249 (preview9, `m249`): bipod deployed, feed cover closed, its 200-round box and belt, from its left.

The main mod's Uzi, Mini Uzi and Micro Uzi (preview10, `uzi` / `miniuzi` / `microuzi`): one view and scale so they keep
their real sizes against each other, from their left (the markings) after the mirror; the Uzi and Micro with the stock
folded, the Mini with it deployed (the user's photo), each with its standard magazine (scripts/uzi_points.json; the
Mini and Micro are modelled upside down and turned upright, the Uzi is rifle-held and upright).
"""

import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
MAIN_MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                          "3722134990/mods/GunsOfMarz/42.16/media"),
                       "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                       "42.16/media") if os.path.isdir(p))
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = ARGS[0]
UPRIGHT = Matrix.Rotation(math.pi, 4, 'Y')
VIEW = (-0.8, 0.5, -0.3)             # looking from the gun's left, a little behind and above: muzzle to the right
SCALE = 0.62                         # ortho width (game units) of the MP7 and P90 renders
SIZE = (1600, 900)
PISTOL_SCALE = 0.34                  # the same for the two pistols (fitted Five-seveN: 0.28 long)
PISTOL_SIZE = (2000, 1100)

GOM_DB = (os.path.join(GOM, "models_X/weapons/firearms/DOUBLEBARREL.fbx"),
          os.path.join(GOM, "textures/weapons/firearms/shotguns/DOUBLEBARREL.png"))
SAWN = os.path.join(MAIN_MEDIA, "models_X/weapons/firearms/GunsOfTien_SawnStocks.fbx")
DB_VIEW, DB_SCALE, DB_SIZE = (0.8, 0.45, -0.25), 0.78, (2400, 1000)

RIFLE_VIEW, RIFLE_SCALE, RIFLE_SIZE = (0.92, 0.3, -0.16), 0.98, (2400, 1000)
UMP_SCALE, UMP_SIZE = 0.62, (2400, 1400)
SMG9_PARTS = os.path.join(MAIN_MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")
SMG9_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTien")
MK9_SCALE, MK9_SIZE = 0.82, (2400, 1000)

M249_SCALE, M249_SIZE = 0.86, (2400, 1300)
# the M249 from its left (box and belt side) after make_workshop_art.py mirrors it back: game space as world space is
# the game's mirror image, so the camera looks from the world's +X
M249_VIEW = (-0.92, 0.3, -0.2)
UZI_VIEW, UZI_SCALE, UZI_SIZE = (-0.92, 0.3, -0.2), 0.62, (2400, 1400)

GUNS = {
    # the main mod's Uzis (preview10): (gun, stock folded, magazine)
    "uzi": {"uzi": ("UZI", True, "9x19Magazine32_UZI"), "view": UZI_VIEW, "scale": UZI_SCALE, "size": UZI_SIZE},
    "miniuzi": {"uzi": ("MINIUZI", False, "9x19Magazine20_UZI"), "view": UZI_VIEW, "scale": UZI_SCALE,
                "size": UZI_SIZE},
    "microuzi": {"uzi": ("MICROUZI", True, "9x19Magazine20_UZI"), "view": UZI_VIEW, "scale": UZI_SCALE,
                 "size": UZI_SIZE},
    # the main mod's M249 (preview9): bipod deployed, feed cover closed, the 200-round box and its belt
    "m249": {"m249": True, "view": M249_VIEW, "scale": M249_SCALE, "size": M249_SIZE},
    # fitted out: the SCAR-L with GoM's EXPS3, MKC foregrip, AR mount + MKI; the SCAR-H with GoM's Elcan and bipod,
    # its own mount device and SOCOM762-RC suppressor; stocks deployed
    "scarl": {
        "rifle": True, "points": "post93/scarl_points.json",
        "fbx": "GunsOfTienPost93_SCARL", "tex": "SCARL",
        "nodes": [("SCARL_BODY", None), ("SCARL_BOLT", None),
                  ("SCAR_STOCK", "stock", "parts/GunsOfTienPost93_SCAR_parts", "SCAR_STOCK")],
        "gom_mag": ("magazines/assault_rifles", "556x45Magazine30_STANAG", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip"),
                ("muzzles", "Muzzle_Mount_Device", "canon"), ("suppressors", "MKI_Suppressor", "canon")],
        "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE,
    },
    "scarh": {
        "rifle": True, "points": "post93/scarh_points.json",
        "fbx": "GunsOfTienPost93_SCARH", "tex": "SCARH",
        "nodes": [("SCARH_BODY", None), ("SCARH_BOLT", None),
                  ("SCAR_STOCK", "stock", "parts/GunsOfTienPost93_SCAR_parts", "SCAR_STOCK")],
        "mag": ("GunsOfTienPost93_SCARH_magazines", "762x51Magazine20_SCARH", "magazine"),
        "parts": [("GunsOfTienPost93_SCAR_parts", "SCARH_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_SCAR_parts", "SCARH_Suppressor")],
        "gom": [("scopes", "ElcanX2_Scope", "scope"), ("bipods", "Bipod_Deployed", "bipod")],
        "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE,
    },
    # the UMPs (preview7): rifles like the SCARs, the same view, a scale for their length; one body file for both, each
    # with its own texture; stocks deployed, fitted out with GoM's MP5 accessories (no muzzle parts; the UMP45's P45
    # suppressor came after preview7)
    "ump45": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP45",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "45Magazine25_UMP", "magazine"),
        "parts": [],
        # the laser: the view shows the right side (after the mirror), where a light on the left rail would be hidden
        "gom": [("scopes", "Aimpoint_Sight", "scope"), ("pointers", "AimRight_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": UMP_SCALE, "size": UMP_SIZE,
    },
    "ump9": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP9",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "9x19Magazine30_UMP", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip")],
        "view": RIFLE_VIEW, "scale": UMP_SCALE, "size": UMP_SIZE,
    },
    # GoM's MP5 and MP5A2 with the main mod's mount device and AWC Mk9 (preview8), stocks deployed, nothing else fitted
    "mp5_mk9": {"gom_smg": "MP5", "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE},
    "mp5a2_mk9": {"gom_smg": "MP5A2", "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE},
    "ump9_mk9": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP9",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "9x19Magazine30_UMP", "magazine"),
        "parts": [], "gom": [], "main_parts": ["SMG9_Muzzle_Mount_Device", "Mk9_Suppressor"],
        "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE,
    },
    "ump45_p45": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP45",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "45Magazine25_UMP", "magazine"),
        "parts": [], "gom": [("muzzles", "Muzzle_Mount_Device", "canon"), ("suppressors", "P45_Suppressor", "canon")],
        "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE,
    },
    # world space is the game's mirror image, so these show the gun's right side, muzzle left, until
    # make_workshop_art.py mirrors them back to the game's view (left side, muzzle right)
    "db_full": {
        "files": [(GOM_DB[0], "DOUBLEBARREL_BODY", GOM_DB[1]), (GOM_DB[0], "DOUBLEBARREL_BARREL_CLOSE", GOM_DB[1])],
        "view": DB_VIEW, "scale": DB_SCALE, "size": DB_SIZE,
    },
    "db_sawn": {
        "files": [(SAWN, "DOUBLEBARREL_BODY_SAWNSTOCK", GOM_DB[1]),
                  (GOM_DB[0], "DOUBLEBARREL_BARREL_SAWNOFF_CLOSE", GOM_DB[1])],
        "view": DB_VIEW, "scale": DB_SCALE, "size": DB_SIZE,
    },
    "mp7": {
        "points": "post93/mp7_points.json",
        "fbx": "GunsOfTienPost93_MP7A1", "tex": "MP7A1",
        "nodes": [("MP7A1_BODY", None), ("MP7A1_BOLT", None), ("MP7A1_STOCK", "stock_folded"),
                  ("MP7A1_FOREGRIP", None)],
        "mag": ("GunsOfTienPost93_MP7_magazines", "46x30Magazine30_MP7", "magazine"),
        "parts": [("GunsOfTienPost93_MP7_parts", "MP7_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_MP7_parts", "MP7_Suppressor")],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("pointers", "AimRight_Laser", "laser_right")],
    },
    # the MP7A2 on its own (preview4): fitted out: GoM's Stub Foregrip on the bottom one, stock
    # deployed; its bolt and stock are nodes of the A1's file (a node entry may name its own file and texture)
    "mp7a2": {
        "points": "post93/mp7a2_points.json",
        "fbx": "GunsOfTienPost93_MP7A2", "tex": "MP7A2",
        "nodes": [("MP7A2_BODY", None), ("MP7A1_BOLT", None, "GunsOfTienPost93_MP7A1", "MP7A1"),
                  ("MP7A1_STOCK", None, "GunsOfTienPost93_MP7A1", "MP7A1")],
        "mag": ("GunsOfTienPost93_MP7_magazines", "46x30Magazine40_MP7", "magazine"),
        "parts": [("GunsOfTienPost93_MP7_parts", "MP7_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_MP7_parts", "MP7_Suppressor")],
        # no light: it would cover the side rail, the handguard being the point of the picture
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "Stub_Foregrip", "foregrip")],
        "view": (-0.85, 0.42, -0.22), "scale": 0.68, "size": (2400, 1350),
    },
    "p90": {
        "points": "post93/p90_points.json",
        "fbx": "GunsOfTienPost93_P90TR", "tex": "P90TR",
        "nodes": [("P90TR_BODY", None), ("P90TR_BOLT", None)],
        "mag": ("GunsOfTienPost93_P90_magazines", "57x28Magazine50_P90", "magazine"),
        "parts": [("GunsOfTienPost93_P90_parts", "P90_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_P90_parts", "P90_Suppressor")],
        "gom": [("scopes", "Aimpoint_Sight", "scope"), ("pointers", "BrightPoint-5_Light", "light_left"),
                ("pointers", "AimRight_Laser", "laser_right")],
    },
    # the pistols: magazines have no point (drawn at the gun's origin, as GoM's Glock's), the muzzle parts at canon;
    # views are in world space, i.e. before make_workshop_art.py mirrors them back (render_fiveseven.py's like_r /
    # like_usg, flatter): the Five-seveN's right side, muzzle right; the UCP's left side, muzzle left
    "fiveseven": {
        "points": "post93/fiveseven_points.json",
        "fbx": "GunsOfTienPost93_FIVESEVEN", "tex": "FIVESEVEN",
        "nodes": [("FIVESEVEN_BODY", None), ("FIVESEVEN_SLIDE", None)],
        "mag": ("GunsOfTienPost93_FIVESEVEN_magazines", "57x28Magazine20_FIVESEVEN", None),
        "parts": [("GunsOfTienPost93_FIVESEVEN_parts", "FIVESEVEN_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_FIVESEVEN_parts", "FIVESEVEN_Suppressor")],
        "gom": [],                   # only what the mod adds
        "view": (0.8, -0.3, -0.35), "scale": PISTOL_SCALE, "size": PISTOL_SIZE,
    },
    "ucp": {
        "points": "post93/ucp_points.json",
        "fbx": "GunsOfTienPost93_UCP", "tex": "UCP",
        "nodes": [("UCP_BODY", None), ("UCP_SLIDE", None)],
        "mag": ("GunsOfTienPost93_UCP_magazines", "46x30Magazine40_UCP", None),
        "parts": [("GunsOfTienPost93_UCP_parts", "UCP_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_MP7_parts", "MP7_Suppressor")],
        "gom": [],
        "view": (-0.8, -0.3, -0.35), "scale": PISTOL_SCALE, "size": PISTOL_SIZE,
    },
}


def load(path, texture, keep):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    img = bpy.data.images.load(texture, check_existing=True)
    m = bpy.data.materials.new(os.path.basename(texture))
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    found = None
    for o in set(bpy.data.objects) - before:
        if o.name.split(".")[0] != keep:
            bpy.data.objects.remove(o)
            continue
        o.data.materials.clear()
        o.data.materials.append(m)
        found = o
    return found


# Our guns draw GoM's STANAG magazines and the main mod's Mk9 / SMG9 mount through models of their own scaled to our
# size (gen_scripts.py GOT_PART_SCALE / STANAG_GOT_SCALE; user, 2026-10-26)
GOT_PART_SCALE = round(0.000603 / 0.00072, 4)
STANAG_GOT_SCALE = round(0.000603 / 0.00065, 4)


def place(o, point=None, upright=True, scale=1.0):
    """Engine attachment transform (offset, then rotateXYZ in degrees, then the part model's own scale), turned upright
    (guns held like pistols are modelled upside down); mesh data z is game -z."""
    mat = Matrix.Identity(4)
    if point:
        rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]
        mat = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X')
               @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rz, 4, 'Z'))
    o.matrix_world = ((UPRIGHT if upright else Matrix.Identity(4)) @ mat @ Matrix.Scale(scale, 4)
                      @ Matrix.Diagonal((1.0, 1.0, -1.0, 1.0)))


def gom_smg(gun):
    """GoM's SMG as its item script draws it with the stock deployed (body, bolt and stock nodes at the origin), its
    30-round magazine at the model script's point, the Mk9 and its mount device at the measured `canon`."""
    fbx = os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % gun)
    tex = os.path.join(GOM, "textures/weapons/firearms/smgs/%s.png" % gun)
    objs = []
    for node in (gun + "_BODY", gun + "_BOLT", gun + "_STOCK"):
        o = load(fbx, tex, node)
        if o:                                            # the MP5A2's fixed stock is part of its body
            place(o, upright=False)
            objs.append(o)
    o = load(os.path.join(GOM, "models_X/weapons/magazines/smgs.fbx"),
             os.path.join(GOM, "textures/weapons/magazines/smgs/9x19Magazine30_MP5.png"), "9x19Magazine30_MP5")
    place(o, {"offset": [0.0, 0.1191, 0.0377]}, False)   # GoM's MP5 / MP5A2 model scripts
    objs.append(o)
    canon = json.load(open(os.path.join(HERE, "smg9_points.json")))["MarzGuns." + gun]
    for node in ("SMG9_Muzzle_Mount_Device", "Mk9_Suppressor"):
        o = load(SMG9_PARTS, os.path.join(SMG9_TEX, node + ".png"), node)
        place(o, canon, False)
        objs.append(o)
    return objs


def m249():
    """The M249 as its item script draws it with a full box: body, the closed feed cover at its point, the deployed
    bipod and the nine belt rounds (modelled in the gun's space), the box at its point (scripts/m249_points.json)."""
    pts = json.load(open(os.path.join(HERE, "m249_points.json")))
    gun = os.path.join(MAIN_MEDIA, "models_X/weapons/firearms/GunsOfTien_M249.fbx")
    box = os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_M249_box.fbx")
    tex, box_tex = os.path.join(SMG9_TEX, "M249.png"), os.path.join(SMG9_TEX, "556x45Box200_M249.png")
    objs = []
    for fbx, t, node, point in [(gun, tex, "M249_BODY", None), (gun, tex, "M249_COVER", "cover"),
                                (gun, tex, "M249_BIPOD_DEPLOYED", None), (box, box_tex, "556x45Box200_M249", "box")] + \
            [(box, box_tex, "556x45_M249_%d" % i, None) for i in range(1, 10)]:
        o = load(fbx, t, node)
        place(o, pts[point] if point else None, False)
        objs.append(o)
    return objs


def uzi(gun, folded, mag):
    """An Uzi as its item script draws it: body and cocking knob, the stock (the Uzi's two in-place nodes, the Mini's /
    Micro's one node at stock / stock_folded), the magazine at its point."""
    pts = json.load(open(os.path.join(HERE, "uzi_points.json")))[gun]
    up = pts["_extras"]["handgun_hold"]
    fbx = os.path.join(MAIN_MEDIA, "models_X/weapons/firearms/GunsOfTien_%s.fbx" % gun)
    tex = os.path.join(SMG9_TEX, gun + ".png")
    if gun == "UZI":
        stock = ("UZI_STOCK_FOLDED" if folded else "UZI_STOCK_DEPLOYED", None)
    else:
        stock = (gun + "_STOCK", "stock_folded" if folded else "stock")
    objs = []
    for node, point in ((gun + "_BODY", None), (gun + "_BOLT", None), stock):
        o = load(fbx, tex, node)
        place(o, pts[point] if point else None, up)
        objs.append(o)
    o = load(os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx"),
             os.path.join(SMG9_TEX, mag + ".png"), mag)
    place(o, pts["magazine"], up)
    objs.append(o)
    return objs


def build(spec):
    if "uzi" in spec:
        return uzi(*spec["uzi"])
    if "m249" in spec:
        return m249()
    if "gom_smg" in spec:
        return gom_smg(spec["gom_smg"])
    if "files" in spec:
        objs = []
        for fbx, node, tex in spec["files"]:
            o = load(fbx, tex, node)
            place(o, upright=False)
            objs.append(o)
        return objs
    points = json.load(open(os.path.join(HERE, spec["points"])))
    up = not spec.get("rifle", False)
    objs = []
    for node, point, *src in spec["nodes"]:
        fbx, tex = src if src else (spec["fbx"], spec["tex"])
        folder = "" if "/" in fbx else "firearms/"
        o = load(os.path.join(MEDIA, "models_X/weapons/%s%s.fbx" % (folder, fbx)), os.path.join(TEX, tex + ".png"), node)
        place(o, points[point] if point else None, up)
        objs.append(o)
    if "gom_mag" in spec:
        cat, node, point = spec["gom_mag"]
        o = load(os.path.join(GOM, "models_X/weapons/%s.fbx" % cat),
                 os.path.join(GOM, "textures/weapons/%s/%s.png" % (cat, node)), node)
        place(o, points[point] if point else None, up, STANAG_GOT_SCALE)
    else:
        f, node, point = spec["mag"]
        o = load(os.path.join(MEDIA, "models_X/weapons/magazines/%s.fbx" % f), os.path.join(TEX, node + ".png"), node)
        place(o, points[point] if point else None, up)
    objs.append(o)
    for f, node in spec["parts"]:
        o = load(os.path.join(MEDIA, "models_X/weapons/parts/%s.fbx" % f), os.path.join(TEX, node + ".png"), node)
        place(o, points["canon"], up)
        objs.append(o)
    for cat, node, point in spec["gom"]:
        o = load(os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
                 os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (cat, node)), node)
        place(o, points[point], up)
        objs.append(o)
    for node in spec.get("main_parts", []):              # the main mod's Mk9 and its mount on a Post-93 gun
        o = load(SMG9_PARTS, os.path.join(SMG9_TEX, node + ".png"), node)
        place(o, points["canon"], up, GOT_PART_SCALE)
        objs.append(o)
    return objs


def centre_of(objs):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return [(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)]


def main():
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_cavity = True
    sc.display.shading.cavity_type = 'WORLD'
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = 'ORTHO'
    cam.data.clip_end = 10.0
    sc.collection.objects.link(cam)
    sc.camera = cam
    for name, spec in GUNS.items():
        if ARGS[1:] and name not in ARGS[1:]:
            continue
        sc.render.resolution_x, sc.render.resolution_y = spec.get("size", SIZE)
        cam.data.ortho_scale = spec.get("scale", SCALE)
        d = Vector(spec.get("view", VIEW)).normalized()
        objs = build(spec)
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.hide_render = o not in objs
        cam.location = Vector(centre_of(objs)) - d * 2.0
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(OUT, "ad_%s.png" % name)
        bpy.ops.render.render(write_still=True)


main()
