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

Post-93's KRISS Vector .45 and 9mm (preview15, `vector45` / `vector9`): the UMPs' view and scale, from the upright
VECTOR_* nodes with each gun's texture (the 9mm's turned nodes match them in outline), stocks deployed.

Post-93's MDRx .223 and .308 (preview22, `mdr223` / `mdr308`): the SCARs' view and scale, both fitted out.

Post-93's Vector .45 Carbine and Vector 9mm Pistol (preview21, `vectorcrb` / `vectorsdp`): one view and scale, the
CRB from its upright nodes, the SDP from its turned ones turned back upright, both fitted out.

The main mod's Glock 21 (preview16, `glock21` / `glock21_fitted`): bare and with GoM's pistol parts, both from the bare
gun's camera so they line up, turned upright (`assembled` + `upright`), seen so the slide's markings read after the
mirror.

3.13.0 (2026-11-12): the main mod's SR-25 (preview23, `sr25`: KAC's 20, its bipod deployed, its scope in the body) and
Steyr TMP (preview24, `tmp` / `tmp_fitted`: bare, and on GoM's rails with an Aimpoint, SR7 light, LRX-7 laser and the
Mk9 on its mount, both from the bare gun's camera, turned upright); Post-93's Mk 11 Mod 0 (preview25, `mk11`: GoM's
LR10X, bipod and laser on its rails, KAC's 20, the SOCOM762-RC) and the four Grozas (preview26, `groza1` / `grozagl` /
`groza2` / `groza4`: one view and scale, each with GoM's standard magazine of its calibre at our size; the Groza-2
from its upright body).
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


def post93_file(rel):
    """A Post-93-named asset, wherever it lives: the P90's magazine, mount device and SP90 moved to the main mod on
    2026-11-03 under their old names and paths."""
    path = os.path.join(MEDIA, rel)
    return path if os.path.exists(path) else os.path.join(MAIN_MEDIA, rel)
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
VECTOR_VARIANT_SCALE, VECTOR_VARIANT_SIZE = 0.8, (2400, 1400)     # preview21: the CRB is 0.54 long
SMG9_PARTS = os.path.join(MAIN_MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")
SMG9_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTien")
MK9_SCALE, MK9_SIZE = 0.82, (2400, 1000)

M249_SCALE, M249_SIZE = 0.86, (2400, 1300)
# the M249 from its left (box and belt side) after make_workshop_art.py mirrors it back: game space as world space is
# the game's mirror image, so the camera looks from the world's +X
M249_VIEW = (-0.92, 0.3, -0.2)
UZI_VIEW, UZI_SCALE, UZI_SIZE = (-0.92, 0.3, -0.2), 0.62, (2400, 1400)

# preview12, the AUGs: the main mod's A1 and Post-93's A3, Para and HBAR, drawn as the game draws them: body, bolt at
# its origin (bolt_lock), the front grip folded, a magazine, the HBAR's bipod folded (`assembled`: fbx, node,
# texture, point name or None in that gun's points file). A3 and HBAR use the A1's bolt and grip (main mod's AUG
# texture), as their item scripts do.
AUG_VIEW, AUG_SCALE, AUG_SIZE = (0.92, 0.3, -0.16), 0.62, (2400, 1200)
MAIN_FIRE = os.path.join(MAIN_MEDIA, "models_X/weapons/firearms")
MAIN_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTien")
MAIN_AUG = os.path.join(MAIN_FIRE, "GunsOfTien_AUG.fbx")
MAIN_AUG_MAGS = os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")
POST_FIRE = os.path.join(MEDIA, "models_X/weapons/firearms")
POST_AUG_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_AUG_magazines.fbx")
A1_BOLT_GRIP = [(MAIN_AUG, "AUG_BOLT", os.path.join(MAIN_TEX, "AUG.png"), None),
                (MAIN_AUG, "AUG_HANDLE", os.path.join(MAIN_TEX, "AUG.png"), None),
                (MAIN_AUG, "AUG_FOREGRIP", os.path.join(MAIN_TEX, "AUG.png"), "foregrip_folded")]

# preview13, the Obrez: GoM's Mosin-Nagant whole and sawn off (our MOSIN_BODY_OBREZ), GoM's bolt at its origin,
# viewed like the sawn-off shotguns (DB_VIEW), one scale for both so the Obrez shows its true length
GOM_MOSIN = (os.path.join(GOM, "models_X/weapons/firearms/MOSIN.fbx"),
             os.path.join(GOM, "textures/weapons/firearms/bolt_rifles/MOSIN.png"))
MOSIN_SCALE, MOSIN_SIZE = 1.02, (2400, 900)

# preview16, the main mod's Glock 21: bare (as it was in 1993) and fitted out with GoM's Beretta mount and PS1 sight,
# TL light, .45 mount device and P45, at one scale and from the bare gun's camera, so the two line up (`assembled`
# with `upright`: modelled upside down like GoM's pistols); the UCP's view, so the slide's left-side markings face
# the camera after make_workshop_art.py mirrors it back
G21_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_GLOCK21.fbx")
G21_BARE = [(G21_FBX, "GLOCK21_BODY", os.path.join(MAIN_TEX, "GLOCK21.png"), None),
            (G21_FBX, "GLOCK21_SLIDE", os.path.join(MAIN_TEX, "GLOCK21.png"), None),
            (os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx"),
             "45Magazine13_GLOCK21", os.path.join(MAIN_TEX, "45Magazine13_GLOCK21.png"), None)]
G21_VIEW, G21_SCALE, G21_SIZE = (-0.8, -0.3, -0.35), 0.46, (2400, 1400)


# preview17, the main mod's RPK and RPK-74 (2026-11-02): GoM's AK textures on our meshes; the RPK with its 75-round
# drum and its bipod deployed, the RPK-74 with GoM's Bakelite 45 (drawn at our scale, as its `_GoT` model) and its
# bipod folded (`assembled` tuples may carry a fifth item, the part model's scale; `points_key` picks the gun's own
# points in rpk_points.json)
RPK_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_RPK.fbx")
RPK_MAGS = os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_RPK_magazines.fbx")
GOM_AK_TEX = os.path.join(GOM, "textures/weapons/firearms/assault_rifles")
GOM_AK_MAGS = os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx")
RPK_SCALE = round(0.603 / 0.645, 4)
RPK_VIEW, RPK_ORTHO, RPK_SIZE = (0.88, -0.4, -0.2), 0.78, (2400, 1500)
# preview18, the main mod's RPD (2026-11-02): its drum fitted and its bipod deployed, from the RPKs' front quarter (the
# drum's round front face in view)
RPD_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_RPD.fbx")
RPD_DRUM = os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_RPD_drum.fbx")


# preview19 / preview20 (2026-11-03): the main mod's P90 with its ring sight (held like a pistol, so modelled upside
# down: `upright`) and Post-93's PS90 Carbine (rifle-held, upright), each bare and fitted out at one scale from the
# bare gun's camera (`centre_on_assembled`), seen from the gun's left (lights side) and mirrored back by
# make_workshop_art.py. The P90 family's magazine, mount and SP90 are the main mod's (moved 2026-11-03).
P90STD_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_P90.fbx")
P90_MAGS = os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
P90_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx")     # Post-93's
P90_PART_TEX = os.path.join(MAIN_MEDIA, "textures/weapons/GunsOfTienPost93")
P90_MAG = (P90_MAGS, "57x28Magazine50_P90", os.path.join(P90_PART_TEX, "57x28Magazine50_P90.png"), "magazine")
P90_MUZZLE = [(P90_PARTS, n, os.path.join(TEX, n + ".png"), "canon")
              for n in ("P90_Muzzle_Mount_Device", "P90_Suppressor")]
P90STD_BARE = [(P90STD_FBX, n, os.path.join(MAIN_TEX, "P90.png"), None)
               for n in ("P90_BODY", "P90_BOLT", "P90_HANDLE")] + [P90_MAG]
PS90_FBX = os.path.join(POST_FIRE, "GunsOfTienPost93_PS90.fbx")
PS90_BARE = [(PS90_FBX, n, os.path.join(TEX, "PS90.png"), None)
             for n in ("PS90_BODY", "PS90_BOLT", "PS90_HANDLE")] + [P90_MAG]
P90_VIEW, P90_SCALE, P90_SIZE = (-0.88, 0.32, -0.26), 0.5, (2400, 1500)
PS90_SCALE = 0.68                    # the PS90 with its SP90 is 0.15 longer
BOX_VIEW, BOX_SIZE = (-1.0, 0.0, 0.0), (800, 560)      # ammo box pictures: straight from the side


# 3.13.0 (2026-11-12): SR-25, TMP, Mk 11, Grozas
SR25_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_SR25.fbx")
GOM_AR15_TEX = os.path.join(GOM, "textures/weapons/firearms/assault_rifles/AR15.png")
KAC20 = (os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx"), "762x51Magazine20_SR25",
         os.path.join(GOM, "textures/weapons/magazines/assault_rifles/556x45Magazine20_STANAG.png"), "magazine")
TMP_FBX = os.path.join(MAIN_FIRE, "GunsOfTien_TMP.fbx")
TMP_BARE = [(TMP_FBX, n, os.path.join(MAIN_TEX, "TMP.png"), p) for n, p in
            (("TMP_BODY", None), ("TMP_BOLT", None), ("TMP_HANDLE", None))] + [
    (os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_TMP_magazines.fbx"), "9x19Magazine30_TMP",
     os.path.join(MAIN_TEX, "9x19Magazine30_TMP.png"), "magazine")]
RAILS_FBX = os.path.join(MAIN_MEDIA, "models_X/weapons/parts/GunsOfTien_rails.fbx")
TMP_VIEW, TMP_SCALE, TMP_SIZE = (-0.88, 0.32, -0.26), 0.5, (2400, 1500)
MK11_FBX = os.path.join(POST_FIRE, "GunsOfTienPost93_MK11.fbx")
SCAR_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx")
GROZA_FBX = os.path.join(POST_FIRE, "GunsOfTienPost93_GROZA.fbx")
GROZA_TEX = os.path.join(TEX, "GROZA.png")
GROZA_VIEW, GROZA_SCALE, GROZA_SIZE = (0.92, 0.3, -0.16), 0.6, (2400, 1200)


def groza(body, mag_geo, mag_tex, mag_point, extra=()):
    """A Groza as its item script draws it: body, the carrier, GoM's magazine at our size (`_GoT`), more parts."""
    return [(GROZA_FBX, body, GROZA_TEX, None), (GROZA_FBX, "GROZA_BOLT", GROZA_TEX, None),
            (GOM_AK_MAGS, mag_geo, os.path.join(GOM, "textures/weapons/magazines/assault_rifles/%s.png" % mag_tex),
             mag_point, RPK_SCALE)] + list(extra)


def gom_part(cat, name, point):
    return (os.path.join(GOM, "models_X/weapons/parts/%s.fbx" % cat),
            name, os.path.join(GOM, "textures/weapons/parts/%s/%s.png" % (cat, name)), point)


GUNS = {
    "sr25": {"points": "sr25_points.json",
             "assembled": [(SR25_FBX, n, GOM_AR15_TEX, pt) for n, pt in
                           (("SR25_BODY", None), ("SR25_BOLT", None), ("SR25_CHARGING_HANDLE", None),
                            ("SR25_BIPOD_DEPLOYED", "integrated_bipod"))] + [KAC20],
             "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE},
    "tmp": {"points": "tmp_points.json", "assembled": TMP_BARE, "upright": True, "centre_on_assembled": True,
            "view": TMP_VIEW, "scale": TMP_SCALE, "size": TMP_SIZE},
    "tmp_fitted": {
        "points": "tmp_points.json", "upright": True, "centre_on_assembled": True,
        "assembled": TMP_BARE + [(RAILS_FBX, "TMP_RAIL_" + s, os.path.join(MAIN_TEX, "Rails.png"), "rail_" + s.lower())
                                 for s in ("UP", "LEFT", "RIGHT")] + [
            gom_part("scopes", "Aimpoint_Sight", "scope"), gom_part("pointers", "SR7_Light", "light_left"),
            gom_part("pointers", "LRX-7_Laser", "laser_right")] + [
            (SMG9_PARTS, n, os.path.join(SMG9_TEX, n + ".png"), "canon", round(0.000603 / 0.00072, 4))
            for n in ("SMG9_Muzzle_Mount_Device", "Mk9_Suppressor")],
        "view": TMP_VIEW, "scale": TMP_SCALE, "size": TMP_SIZE,
    },
    "mk11": {"points": "post93/mk11_points.json",
             "assembled": [(MK11_FBX, n, GOM_AR15_TEX, None) for n in ("MK11_BODY", "MK11_BOLT", "MK11_CHARGING_HANDLE")]
             + [KAC20] + [(SCAR_PARTS, n, os.path.join(TEX, n + ".png"), "canon")
                          for n in ("SCARH_Muzzle_Mount_Device", "SCARH_Suppressor")] + [
                 gom_part("scopes", "LR10X_Scope", "scope"), gom_part("bipods", "Bipod_Deployed", "bipod"),
                 gom_part("pointers", "AimRight_Laser", "laser_right")],
             "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE},
    "groza1": {"points": "post93/groza_points.json",
               "assembled": groza("GROZA_BODY", "762x39Magazine30", "762x39Magazine30", "magazine_762x39", [
                   (GROZA_FBX, "GROZA_RAIL_UP", GROZA_TEX, "rail_up"), gom_part("scopes", "Kobra_Sight", "scope")]),
               "view": GROZA_VIEW, "scale": GROZA_SCALE, "size": GROZA_SIZE},
    "grozagl": {"points": "post93/groza_points.json",
                "assembled": groza("GROZAGL_BODY", "762x39Magazine30", "762x39Magazine30", "magazine_762x39"),
                "view": GROZA_VIEW, "scale": GROZA_SCALE, "size": GROZA_SIZE},
    "groza2": {"points": "post93/groza_points.json",
               "assembled": groza("GROZA2_BODY", "545x39Magazine30", "545x39Magazine30", "magazine_545x39"),
               "view": GROZA_VIEW, "scale": GROZA_SCALE, "size": GROZA_SIZE},
    "groza4": {"points": "post93/groza_points.json",
               "assembled": groza("GROZA4_BODY", "9x39Magazine20", "9x39Magazine20", "magazine", [
                   (os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_GROZA_parts.fbx"), "GROZA_Suppressor",
                    os.path.join(TEX, "GROZA_Suppressor.png"), "canon"),
                   (GROZA_FBX, "GROZA_RAIL_UP", GROZA_TEX, "rail_up"), gom_part("scopes", "LR4X_Scope", "scope")]),
               "view": GROZA_VIEW, "scale": GROZA_SCALE, "size": GROZA_SIZE},
    "p90std": {"points": "p90std_points.json", "assembled": P90STD_BARE, "upright": True, "centre_on_assembled": True,
               "view": P90_VIEW, "scale": P90_SCALE, "size": P90_SIZE},
    "p90std_fitted": {
        "points": "p90std_points.json", "upright": True, "centre_on_assembled": True,
        "assembled": P90STD_BARE + [(P90STD_FBX, "P90_RAIL_" + s, os.path.join(MAIN_TEX, "P90.png"), "rail_" + s.lower())
                                    for s in ("LEFT", "RIGHT")] + [      # no SP90: Post-93's (the main mod's page)
            gom_part("pointers", "SR7_Light", "light_left"), gom_part("pointers", "AimRight_Laser", "laser_right")],
        "view": P90_VIEW, "scale": P90_SCALE, "size": P90_SIZE,
    },
    "ps90": {"points": "post93/ps90_points.json", "assembled": PS90_BARE, "centre_on_assembled": True,
             "view": P90_VIEW, "scale": PS90_SCALE, "size": P90_SIZE},
    "ps90_fitted": {
        "points": "post93/ps90_points.json", "centre_on_assembled": True,
        "assembled": PS90_BARE + P90_MUZZLE + [
            gom_part("scopes", "Aimpoint_Sight", "scope"), gom_part("pointers", "SR7_Light", "light_left"),
            gom_part("pointers", "AimRight_Laser", "laser_right"), gom_part("foregrips", "MKC_Foregrip", "foregrip")],
        "view": P90_VIEW, "scale": PS90_SCALE, "size": P90_SIZE,
    },
    "glock21": {"points": "glock21_points.json", "assembled": G21_BARE, "upright": True, "centre_on_assembled": True,
                "view": G21_VIEW, "scale": G21_SCALE, "size": G21_SIZE},
    "glock21_fitted": {
        "points": "glock21_points.json", "upright": True, "centre_on_assembled": True,
        "assembled": G21_BARE + [gom_part("rails", "Beretta_Mount", "rail_up"), gom_part("scopes", "PS1_Sight", "scope"),
                                 gom_part("pointers", "TL_Light", "underbarrel"),
                                 gom_part("muzzles", "Muzzle_Mount_Device", "canon"),
                                 gom_part("suppressors", "P45_Suppressor", "canon")],
        "view": G21_VIEW, "scale": G21_SCALE, "size": G21_SIZE,
    },
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
    # the MDRx .223 and .308 (preview22): rifles like the SCARs, the same view and scale (the .308 with its 20" barrel
    # and the SOCOM762-RC is about as long as the SCAR-H fitted out); the .223 with GoM's EXPS3, MKC foregrip, AR mount +
    # MKI and a STANAG 30 (at our size), the .308 with GoM's Elcan, its ALX legs deployed (their own texture; no
    # foregrip fits under them), the SCAR-H's mount + SOCOM762-RC and a PMAG 20; both with GoM's right Picatinny rail
    # (our M-LOK section) and a laser on it, the side this view shows
    "mdr223": {
        "rifle": True, "points": "post93/mdr223_points.json",
        "fbx": "GunsOfTienPost93_MDR223", "tex": "MDR223",
        "nodes": [("MDR223_BODY", None), ("MDR223_BOLT", None), ("MDR223_HANDLE", None),
                  ("MDR223_RAIL_RIGHT", "rail_right")],
        "gom_mag": ("magazines/assault_rifles", "556x45Magazine30_STANAG", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip"),
                ("muzzles", "Muzzle_Mount_Device", "canon"), ("suppressors", "MKI_Suppressor", "canon"),
                ("pointers", "LRX-7_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE,
    },
    "mdr308": {
        "rifle": True, "points": "post93/mdr308_points.json",
        "fbx": "GunsOfTienPost93_MDR308", "tex": "MDR308",
        "nodes": [("MDR308_BODY", None), ("MDR308_BOLT", None), ("MDR308_HANDLE", None),
                  ("MDR308_RAIL_RIGHT", "rail_right"),
                  ("MDR308_BIPOD_DEPLOYED", "integrated_bipod", "GunsOfTienPost93_MDR308", "MDR308_BIPOD")],
        "mag": ("GunsOfTienPost93_PMAG_magazines", "762x51Magazine20_PMAG", "magazine"),
        "parts": [("GunsOfTienPost93_SCAR_parts", "SCARH_Muzzle_Mount_Device"),
                  ("GunsOfTienPost93_SCAR_parts", "SCARH_Suppressor")],
        "gom": [("scopes", "ElcanX2_Scope", "scope"), ("pointers", "AimRight_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": RIFLE_SCALE, "size": RIFLE_SIZE,
    },
    # the UMPs (preview7): rifles like the SCARs, the same view, a scale for their length; one body file for both, each
    # with its own texture; stocks deployed, fitted out with GoM's MP5 accessories (no muzzle parts; the UMP45's P45
    # suppressor came after preview7)
    "ump45": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP45",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None), ("UMP_HANDLE", None),
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
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None), ("UMP_HANDLE", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "9x19Magazine30_UMP", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip")],
        "view": RIFLE_VIEW, "scale": UMP_SCALE, "size": UMP_SIZE,
    },
    # the KRISS Vectors (preview15): laid out like the UMPs, from the upright nodes with each gun's texture (the 9mm's
    # turned VECTOR9_* nodes match them in outline, render_vector.py), stocks deployed, fitted out with GoM's
    # accessories; the .45's laser on GoM's right Picatinny Rail (the side the view shows after the mirror)
    "vector45": {
        "rifle": True, "points": "post93/vector_points.json",
        "fbx": "GunsOfTienPost93_VECTOR", "tex": "VECTOR45",
        "nodes": [("VECTOR_BODY", None), ("VECTOR_BOLT", None), ("VECTOR_HANDLE", None),
                  ("VECTOR_RAIL_RIGHT", "rail_right"),
                  ("VECTOR_STOCK", "stock", "parts/GunsOfTienPost93_VECTOR_parts", "VECTOR45_STOCK")],
        "mag": ("GunsOfTienPost93_VECTOR_magazines", "45Magazine30_VECTOR", "magazine"),
        "parts": [],
        "gom": [("scopes", "Aimpoint_Sight", "scope"), ("pointers", "AimRight_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": UMP_SCALE, "size": UMP_SIZE,
    },
    "vector9": {
        "rifle": True, "points": "post93/vector_points.json",
        "fbx": "GunsOfTienPost93_VECTOR", "tex": "VECTOR9",
        "nodes": [("VECTOR_BODY", None), ("VECTOR_BOLT", None), ("VECTOR_HANDLE", None),
                  ("VECTOR_STOCK", "stock", "parts/GunsOfTienPost93_VECTOR_parts", "VECTOR9_STOCK")],
        "mag": ("GunsOfTienPost93_VECTOR_magazines", "9x19Magazine33_VECTOR", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip")],
        "view": RIFLE_VIEW, "scale": UMP_SCALE, "size": UMP_SIZE,
    },
    # the Vector .45 Carbine (CRB Enhanced, rifle-held, upright: its own body and stock, the .45's other nodes) and the
    # Vector 9mm Pistol (SDP, held like a pistol: its turned body and the 9mm's turned nodes at vectorsdp_points.json,
    # turned back upright) for preview21, one view and scale so their sizes compare; GoM's laser on the right rail
    "vectorcrb": {
        "rifle": True, "points": "post93/vectorcrb_points.json",
        "fbx": "GunsOfTienPost93_VECTORCRB", "tex": "VECTORCRB",
        "nodes": [("VECTORCRB_BODY", None), ("VECTOR_BOLT", None, "GunsOfTienPost93_VECTOR", "VECTOR45"),
                  ("VECTOR_HANDLE", None, "GunsOfTienPost93_VECTOR", "VECTOR45"),
                  ("VECTOR_RAIL_RIGHT", "rail_right", "GunsOfTienPost93_VECTOR", "VECTOR45"),
                  ("VECTORCRB_STOCK", "stock", "GunsOfTienPost93_VECTORCRB", "VECTORCRB_STOCK")],
        "mag": ("GunsOfTienPost93_VECTOR_magazines", "45Magazine30_VECTOR", "magazine"),
        "parts": [],
        "gom": [("scopes", "Aimpoint_Sight", "scope"), ("foregrips", "MKC_Foregrip", "foregrip"),
                ("pointers", "AimRight_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": VECTOR_VARIANT_SCALE, "size": VECTOR_VARIANT_SIZE,
    },
    "vectorsdp": {
        "points": "post93/vectorsdp_points.json",
        "fbx": "GunsOfTienPost93_VECTORSDP", "tex": "VECTORSDP",
        "nodes": [("VECTORSDP_BODY", None), ("VECTOR9_BOLT", None, "GunsOfTienPost93_VECTOR", "VECTOR9"),
                  ("VECTOR9_HANDLE", None, "GunsOfTienPost93_VECTOR", "VECTOR9"),
                  ("VECTOR9_RAIL_RIGHT", "rail_right", "GunsOfTienPost93_VECTOR", "VECTOR9")],
        "mag": ("GunsOfTienPost93_VECTOR_magazines", "9x19Magazine33_VECTOR", "magazine"),
        "parts": [],
        "gom": [("scopes", "EXPS3_Sight", "scope"), ("pointers", "AimRight_Laser", "laser_right")],
        "view": RIFLE_VIEW, "scale": VECTOR_VARIANT_SCALE, "size": VECTOR_VARIANT_SIZE,
    },
    # GoM's MP5 and MP5A2 with the main mod's mount device and AWC Mk9 (preview8), stocks deployed, nothing else fitted
    "mp5_mk9": {"gom_smg": "MP5", "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE},
    "mp5a2_mk9": {"gom_smg": "MP5A2", "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE},
    "ump9_mk9": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP9",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None), ("UMP_HANDLE", None),
                  ("UMP_STOCK", "stock", "parts/GunsOfTienPost93_UMP_parts", "UMP_STOCK")],
        "mag": ("GunsOfTienPost93_UMP_magazines", "9x19Magazine30_UMP", "magazine"),
        "parts": [], "gom": [], "main_parts": ["SMG9_Muzzle_Mount_Device", "Mk9_Suppressor"],
        "view": RIFLE_VIEW, "scale": MK9_SCALE, "size": MK9_SIZE,
    },
    "ump45_p45": {
        "rifle": True, "points": "post93/ump_points.json",
        "fbx": "GunsOfTienPost93_UMP", "tex": "UMP45",
        "nodes": [("UMP_BODY", None), ("UMP_BOLT", None), ("UMP_HANDLE", None),
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
    "rpk": {
        "points": "rpk_points.json", "points_key": "RPK",
        "assembled": [(RPK_FBX, n, os.path.join(GOM_AK_TEX, "AK47.png"), None)
                      for n in ("RPK_BODY", "RPK_BOLT", "RPK_BIPOD_DEPLOYED")] + [
            (RPK_MAGS, "762x39Drum75_RPK", os.path.join(MAIN_TEX, "762x39Drum75_RPK.png"), "magazine")],
        "view": RPK_VIEW, "scale": RPK_ORTHO, "size": RPK_SIZE,
    },
    "rpk74": {
        "points": "rpk_points.json", "points_key": "RPK74",
        "assembled": [(RPK_FBX, n, os.path.join(GOM_AK_TEX, "AK74.png"), None)
                      for n in ("RPK74_BODY", "RPK74_BOLT", "RPK74_BIPOD_FOLDED")] + [
            (GOM_AK_MAGS, "545x39Magazine45", os.path.join(GOM, "textures/weapons/magazines/assault_rifles/"
                                                                "545x39Magazine45.png"), "magazine", RPK_SCALE)],
        "view": RPK_VIEW, "scale": RPK_ORTHO, "size": RPK_SIZE,
    },
    "rpd": {
        "points": "rpd_points.json",
        "assembled": [(RPD_FBX, n, os.path.join(MAIN_TEX, "RPD.png"), None)
                      for n in ("RPD_BODY", "RPD_BOLT", "RPD_BIPOD_DEPLOYED")] + [
            (RPD_DRUM, "762x39Drum100_RPD", os.path.join(MAIN_TEX, "762x39Drum100_RPD.png"), "magazine")],
        "view": RPK_VIEW, "scale": RPK_ORTHO, "size": (2400, 1800),
    },
    "aug": {
        "points": "aug_points.json",
        "assembled": [(MAIN_AUG, "AUG_BODY", os.path.join(MAIN_TEX, "AUG.png"), None)] + A1_BOLT_GRIP + [
            (MAIN_AUG_MAGS, "556x45Magazine30_AUG", os.path.join(MAIN_TEX, "556x45Magazine30_AUG.png"), "magazine")],
        "view": AUG_VIEW, "scale": AUG_SCALE, "size": AUG_SIZE,
    },
    "auga3": {
        "points": "post93/auga3_points.json",
        "assembled": [(os.path.join(POST_FIRE, "GunsOfTienPost93_AUGA3.fbx"), "AUGA3_BODY", os.path.join(TEX, "AUGA3.png"),
                       None)] + A1_BOLT_GRIP + [
            (MAIN_AUG_MAGS, "556x45Magazine30_AUG", os.path.join(MAIN_TEX, "556x45Magazine30_AUG.png"), "magazine")],
        "view": AUG_VIEW, "scale": AUG_SCALE, "size": AUG_SIZE,
    },
    "augpara": {
        "points": "post93/augpara_points.json",
        "assembled": [(os.path.join(POST_FIRE, "GunsOfTienPost93_AUGPARA.fbx"), node, os.path.join(TEX, "AUGPARA.png"),
                       point) for node, point in (("AUGPARA_BODY", None), ("AUGPARA_HANDLE", None),
                                                  ("AUGPARA_FOREGRIP", "foregrip_folded"))] + [
            (MAIN_AUG, "AUG_BOLT", os.path.join(MAIN_TEX, "AUG.png"), None)] + [
            (POST_AUG_MAGS, "9x19Magazine32_AUG", os.path.join(TEX, "9x19Magazine32_AUG.png"), "magazine")],
        "view": AUG_VIEW, "scale": AUG_SCALE, "size": AUG_SIZE,
    },
    "aughbar": {
        "points": "post93/aughbar_points.json",
        "assembled": [(os.path.join(POST_FIRE, "GunsOfTienPost93_AUGHBAR.fbx"), node, os.path.join(TEX, "AUGHBAR.png"),
                       point) for node, point in (("AUGHBAR_BODY", None),
                                                  ("AUGHBAR_BIPOD_FOLDED", "integrated_bipod"))] + A1_BOLT_GRIP + [
            (POST_AUG_MAGS, "762x39Magazine30_AUG", os.path.join(TEX, "762x39Magazine30_AUG.png"), "magazine")],
        "view": AUG_VIEW, "scale": AUG_SCALE, "size": AUG_SIZE,
    },
    "mosin_full": {
        "files": [(GOM_MOSIN[0], "MOSIN_BODY", GOM_MOSIN[1]), (GOM_MOSIN[0], "MOSIN_BOLT", GOM_MOSIN[1])],
        "view": DB_VIEW, "scale": MOSIN_SCALE, "size": MOSIN_SIZE,
    },
    "mosin_obrez": {
        "files": [(SAWN, "MOSIN_BODY_OBREZ", GOM_MOSIN[1]), (GOM_MOSIN[0], "MOSIN_BOLT", GOM_MOSIN[1])],
        # the camera of the whole rifle's render, so the two line up on the receiver in make_workshop_art.py
        "centre_on": [(GOM_MOSIN[0], "MOSIN_BODY", GOM_MOSIN[1]), (GOM_MOSIN[0], "MOSIN_BOLT", GOM_MOSIN[1])],
        "view": DB_VIEW, "scale": MOSIN_SCALE, "size": MOSIN_SIZE,
    },
    "mp7": {
        "points": "post93/mp7_points.json",
        "fbx": "GunsOfTienPost93_MP7A1", "tex": "MP7A1",
        "nodes": [("MP7A1_BODY", None), ("MP7A1_BOLT", None), ("MP7A1_HANDLE", None), ("MP7A1_STOCK", "stock_folded"),
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
                  ("MP7A1_HANDLE", None, "GunsOfTienPost93_MP7A1", "MP7A1"),
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
        "nodes": [("P90TR_BODY", None), ("P90TR_BOLT", None), ("P90TR_HANDLE", None)],
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
    # Pictures on the ammo boxes (2026-11-13, make_ammo_art.py; user: no GoM eagle on our boxes): each calibre's gun,
    # bare, straight from the side as a box print shows it. 4.6x30mm: the MP7A1 (stock and grip folded, 30-round
    # magazine). (The 5.7x28mm boxes show no gun since 2026-11-13: their maker's wasp.)
    "box_mp7": {
        "points": "post93/mp7_points.json",
        "fbx": "GunsOfTienPost93_MP7A1", "tex": "MP7A1",
        "nodes": [("MP7A1_BODY", None), ("MP7A1_BOLT", None), ("MP7A1_HANDLE", None), ("MP7A1_STOCK", "stock_folded"),
                  ("MP7A1_FOREGRIP", None)],
        "mag": ("GunsOfTienPost93_MP7_magazines", "46x30Magazine30_MP7", "magazine"),
        "parts": [], "gom": [],
        "view": BOX_VIEW, "scale": 0.34, "size": BOX_SIZE,
    },
    # the 4.6x30mm Subsonic box shows the UCP (user, 2026-11-13), bare, with its 20-round magazine
    "box_ucp": {
        "points": "post93/ucp_points.json",
        "fbx": "GunsOfTienPost93_UCP", "tex": "UCP",
        "nodes": [("UCP_BODY", None), ("UCP_SLIDE", None)],
        "mag": ("GunsOfTienPost93_UCP_magazines", "46x30Magazine20_UCP", None),
        "parts": [], "gom": [],
        "view": BOX_VIEW, "scale": 0.24, "size": BOX_SIZE,
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
    for node, point in ((gun + "_BODY", None), (gun + "_BOLT", None), (gun + "_HANDLE", None), stock):
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
    if "assembled" in spec:
        points = json.load(open(os.path.join(HERE, spec["points"])))
        if "points_key" in spec:
            points = points[spec["points_key"]]
        objs = []
        for fbx, node, tex, point, *scale in spec["assembled"]:
            o = load(fbx, tex, node)
            place(o, points[point] if point else None, upright=spec.get("upright", False),
                  scale=scale[0] if scale else 1.0)
            objs.append(o)
        return objs
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
        o = load(post93_file("models_X/weapons/magazines/%s.fbx" % f),
                 post93_file("textures/weapons/GunsOfTienPost93/%s.png" % node), node)
        place(o, points[point] if point else None, up)
    objs.append(o)
    for f, node in spec["parts"]:
        o = load(post93_file("models_X/weapons/parts/%s.fbx" % f),
                 post93_file("textures/weapons/GunsOfTienPost93/%s.png" % node), node)
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
        if "centre_on" in spec:
            centre = centre_of(build({"files": spec["centre_on"]}))
        elif spec.get("centre_on_assembled"):         # the bare gun's own parts (the Glock 21's first three)
            centre = centre_of(objs[:3])
        else:
            centre = centre_of(objs)
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.hide_render = o not in objs
        cam.location = Vector(centre) - d * 2.0
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(OUT, "ad_%s.png" % name)
        bpy.ops.render.render(write_still=True)


main()
