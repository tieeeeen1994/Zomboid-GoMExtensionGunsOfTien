"""AWC Mk9 suppressor and the 9x19mm SMG mount device for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_mk9.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx   Mk9_Suppressor, SMG9_Muzzle_Mount_Device
    M/textures/weapons/GunsOfTien/<node>.png              128 px each
    scripts/smg9_points.json                              the `canon` point measured on GoM's MP5 and MP5A2

GoM's 9mm suppressors (M&P, Shh9) fit its pistols only, so its 9mm SMGs had none (user, 2026-10-22: "make a 9mm
non-pistol suppressor so that non pistol 9mm guns can get a mount device too, only if supported"; checked against the
real guns: GoM's MP5 and MP5A2 have H&K's three-lug barrel, the UMP9 a threaded one; the plain MP5K has a flush end
cap and the MP5SD its integral can, so neither takes it; the TEC-9's threaded barrel would, but the user left it
out). The can is AWC's Mk9 (user's choice), AWC's 9mm SMG can for the Uzi, MAC and H&K MP5, fitted to the MP5's three
lugs with Tim Bixler's adapter (patented 1988) and a cap threaded behind the lugs, or onto a threaded barrel: 12.0"
long, 2.0" across, 24 oz (retailer listing; no drawing found), made in the 1980s (an owner's 1980s unit). Big on purpose:
the user saw it and kept it over the shorter SMG cans that fit three-lug and threaded barrels alike (AWC MK9A 10",
Gemtech MK9K about 7-9" but likely after July 1993, AWC Tac-9 with no published size). The mount device is that adapter: a threaded locking cap behind the lugs and a
three-lug sleeve over the barrel, the part every can on GoM's guns needs first (GoM's rule). Both are built at GoM's
SMG scale (0.72 of real size, as GoM's MP5 and our UMP) with their origin at `canon` (the can's rear face against the
front sight housing, or on the UMP9 the barrel collar), along +Y.

GoM's MP5 and MP5A2 model scripts have no `canon` point, and a model script cannot be declared again from another mod
(each later block resets mesh and texture, see ZomboidFixesB42's CLAUDE.md), so shared/GunsOfTien/Suppressors.lua adds
it at run time from the values measured here: the front face of the front sight housing (the largest y of the body's
vertices off the barrel, r > 0.0105 from the bore axis, behind the barrel tip) on the bore axis (GoM's muzzle z).
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTien_SMG9_parts.fbx")
POINTS_JSON = os.path.join(HERE, "smg9_points.json")
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                          "3722134990/mods/GunsOfMarz/42.16/media"),
                       "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                       "42.16/media") if os.path.isdir(p))

K = 0.00072                        # game units per real mm: GoM's MP5 family
kit.K = K
MATS = ["suppressor", "metal", "dark"]
kit.MATS[:] = MATS
kit.FONT.setdefault("W", ["101", "101", "111", "111", "101"])
kit.FONT.setdefault("C", ["111", "100", "100", "100", "111"])
kit.FONT.setdefault("K", ["101", "101", "110", "101", "101"])
kit.FONT.setdefault("9", ["111", "101", "111", "001", "111"])

SUPP_LEN, SUPP_R = 304.8, 25.4     # 12.0" x 2.0"
COUPLER_R, COUPLER_LEN = 16.0, 20.0
MOUNT_LEN = 30.0
LUG_A, LUG_B = 17.0, 25.0          # the three lugs along the sleeve


def build_suppressor():
    """AWC's Mk9: a plain anodised tube with a front cap, the three-lug coupler (a knurled locking collar) at the
    rear; origin at `canon`, along +Y."""
    b = kit.Builder()
    L, R = SUPP_LEN, SUPP_R
    b.lathe("y", (0, 0, 0), [(-1.5, 0), (-1.5, 12.5), (-1.0, 14.5), (0.0, COUPLER_R), (COUPLER_LEN - 2.0, COUPLER_R),
                              (COUPLER_LEN - 1.0, 17.5), (COUPLER_LEN + 1.0, 17.5), (COUPLER_LEN + 3.5, R - 2.0),
                              (COUPLER_LEN + 5.0, R), (L - 14.0, R), (L - 13.0, R - 0.8), (L - 11.0, R - 0.8),
                              (L - 10.0, R), (L - 3.0, R), (L, R - 3.0), (L, 7.0), (L - 4.0, 5.5), (L - 4.0, 0)],
            seg=24, mat="suppressor")
    return b.to_object("Mk9_Suppressor")


def build_mount():
    """Tim Bixler's three-lug adapter: the cap threaded on behind the lugs (flats for a wrench) and the sleeve with
    three lugs the can's coupler locks onto, over the barrel (GoM's MP5 barrel is 10.4 mm in radius at full size, the
    UMP9's collar 9.4); origin at `canon`, along +Y."""
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(-1.0, 0), (-1.0, 12.5), (0.0, 13.5), (11.0, 13.5), (12.0, 12.5), (13.0, 11.6),
                              (MOUNT_LEN - 1.5, 11.6), (MOUNT_LEN, 10.6), (MOUNT_LEN, 5.6), (MOUNT_LEN - 6.0, 5.0),
                              (MOUNT_LEN - 6.0, 0)], seg=18, mat="metal", phase=0.5)
    for k in range(3):                                 # the lugs, 120 degrees apart, the first on top
        xf = Matrix.Rotation(math.radians(120.0 * k), 4, 'Y')
        b.box(-4.0, 4.0, LUG_A, LUG_B, 10.5, 14.2, mat="metal", bevel=0.5, xf=xf)
    return b.to_object("SMG9_Muzzle_Mount_Device")


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {"suppressor": (38, 38, 40), "metal": (56, 56, 58), "dark": (28, 28, 29)}   # sRGB: black anodising, steel


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    r = np.hypot(x, z)
    if kind == "suppressor":
        knurl = (y > 1.5) & (y < COUPLER_LEN - 2.5) & (r > COUPLER_R - 0.6)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 2.0) < 1.0) ^ (np.mod(np.arctan2(x[knurl], z[knurl])
                                                                              * COUPLER_R / 2.0 / math.pi * 2.0, 1.0)
                                                                    < 0.5)))[..., None]
        tube = r > SUPP_R - 0.6
        col[tube & (np.abs(y - (SUPP_LEN - 12.0)) < 1.2)] *= 0.5                      # the front cap's joint
        # "AWC MK9" along the tube, read from the gun's left (the suppressors' text in build_mp7.py runs along -y)
        ang = np.arctan2(x, -z)
        tx = kit.text_mask(-y, ang * SUPP_R, "AWC MK9", -190.0, -3.5, 7.0)
        col[tx & tube] = col[tx & tube] * 0.3 + 120
        col[(r < 6.0) & (y > SUPP_LEN - 1.0)] = 6                                      # the bore
    elif kind == "mount":
        flats = (y > 1.0) & (y < 10.0) & (r > 13.0) & (np.abs(np.mod(np.arctan2(x, z) / (2 * math.pi) * 2, 1) - .5)
                                                         < .12)
        col[flats] += 22
        col[(y > 0.5) & (y < 10.5) & (r > 13.0) & (np.mod(y, 1.6) < 0.5) & ~flats] *= 0.7   # the cap's threads
        col[r < 5.4] = 7
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def common(maps, col, mat):
    """GoM's look, as the SCARs': grain, light from above, AO, bright worn edges."""
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = mat == MATS.index("metal")
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = 60.0 * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 0.97, 0.92])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def texture(ob, kind, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    maps = kit.bake_maps(ob, [ob], bake)
    if kit.DEBUG:
        kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
    col = paint(maps, kind)
    m = maps["cover"]
    col = kit.dilate(np.where(m[..., None], col, 0), m, 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# The `canon` point on GoM's MP5 and MP5A2
# ==================================================================================================

# GoM's model scripts (smgs.txt): the muzzle point's z is the bore axis
GOM_GUNS = {"MP5": 0.0410, "MP5A2": 0.0410}


def measure_canon(gun, bore_z):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(GOM, "models_X/weapons/firearms/%s.fbx" % gun))
    new = set(bpy.data.objects) - before
    body = next(o for o in new if o.name.split(".")[0] == gun + "_BODY")
    body.matrix_world = Matrix.Diagonal((1.0, 1.0, -1.0, 1.0))      # game space (mesh data z is game -z)
    bpy.context.view_layer.update()
    vs = [body.matrix_world @ v.co for v in body.data.vertices]
    tip = max(v[1] for v in vs)
    off = [v[1] for v in vs if v[1] < tip - 0.01 and 0.0105 < math.hypot(v[0], v[2] - bore_z) < 0.05]
    canon = max(off)
    for o in new:
        bpy.data.objects.remove(o)
    return round(canon, 4), round(tip, 4)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.seed = 0
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 0
    scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0, 0, 0)

    points = {}
    for gun, bore_z in GOM_GUNS.items():
        canon, tip = measure_canon(gun, bore_z)
        points["MarzGuns." + gun] = {"offset": [0.0, canon, bore_z], "rotate": [0.0, 0.0, 0.0]}
        print("%s canon y %.4f (barrel tip %.4f, %.1f mm full size ahead)" % (gun, canon, tip, (tip - canon) / K))

    supp, mount = build_suppressor(), build_mount()
    for o in (supp, mount):
        kit.unwrap([o], 0.012)
    os.makedirs(TEX_DIR, exist_ok=True)
    texture(supp, "suppressor", 128, os.path.join(TEX_DIR, "Mk9_Suppressor.png"))
    texture(mount, "mount", 128, os.path.join(TEX_DIR, "SMG9_Muzzle_Mount_Device.png"))
    bounds = {o.name: kit.bounds_of(o) for o in (supp, mount)}
    for name, b in bounds.items():
        print("%-26s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    points["_notes"] = {
        "canon": "GoM's MP5 / MP5A2: the front face of the front sight housing on the bore axis, where a three-lug can "
                 "stops (shared/GunsOfTien/Suppressors.lua adds it to GoM's model scripts at run time)",
        "units": "game units, GoM's model space: +Y muzzle, +Z top, +X the gun's left",
    }
    points["_bounds"] = bounds
    with open(POINTS_JSON, "w") as fh:
        json.dump(points, fh, indent=2)
        fh.write("\n")
    kit.export([supp, mount], FBX_PARTS)


if __name__ == "__main__":
    main()
