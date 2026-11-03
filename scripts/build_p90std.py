"""FN P90 with its ring sight (1990) for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_p90std.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_P90.fbx    P90_BODY, P90_BOLT, P90_HANDLE, and P90_RAIL_LEFT / _RIGHT
                                                      (our short rails, drawn for GoM's optional Picatinny_Rail_Left /
                                                      _Right)
    M/textures/weapons/GunsOfTien/P90.png             256, every node
    scripts/p90std_points.json                        attachment points (game space)

The P90 as FN made it from 1990 (user, 2026-11-03: "the P90 with ring sight", in the main mod, its plain name; the
Post-93 one is the P90 TR): the TR's body (Post-93's build_p90.py, imported: the same lower, butt, magazine, handles
and muzzle, measured on the user's TR photos) with the original upper, the receiver housing flat-topped at H 181 under
the HC-14 ring sight's hood (L 67-155; square across, 30 x 30 mm, up to H 211: user, 2026-11-03), a sight knob on
each side at the front. No rails of its own (FN
added side rails in the mid-2000s, the "P90 Standard"); GoM's optional rails go where FN later put them, on the
housing's sides (user, 2026-11-03: "optional picatinny rails upgrade instead of integrated"); no top rail ("there
should be no optional top rail for p90"), so no optics: the ring sight is the gun's sight.

Measured on Commons "FN P90 Standard Submachine Gun Right Side.jpg" (FN Herstal / Stéphane Moureaux, CC BY-SA 2.0;
references/p90, not in the repo), a P90 Standard (its side rail aside, the 1990 shape), mirrored to the TR photo's
view (muzzle left): 500 mm = 1857 px, so L = (x - 120) / 3.714, H = (970 - y) / 3.714 in the mirrored image; its trigger
loop and belly flats land on the TR's (L 141-161 and 276-296), its bore at H 102 (the TR's 99.8).

Held like a pistol as the TR is (GoM's MP5K way), so modelled upright and turned 180 degrees about the bore axis at
export (build_mp7.py's TURN); GoM's upright parts get TURN at their points, our own nodes are turned with the gun.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_p90 as p90  # noqa: E402  (sets build_mp7's K and material list)

kit = p90.kit
K = p90.K
L0, H0, BORE_H = p90.L0, p90.H0, p90.BORE_H
MEDIA = kit.MAIN_MEDIA
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_P90.fbx")
POINTS_JSON = os.path.join(HERE, "p90std_points.json")

p90.MATS.append("sight")
kit.MATS.append("sight")
p90.BASE["sight"] = (40, 41, 44)     # the ring sight's black housing

TOP_H = 181.0                        # the receiver housing's flat top
# The ring sight's hood: L front / back, H bottom / top. Square across (user, 2026-11-03: "make it squarish so when
# you look into the scope, you see a square"): 30 x 30 mm, taller than the photo's 17 mm, with a square window at each
# end.
HOOD = (67.0, 155.0, 181.0, 211.0)
W_HOOD = 15.0                        # half width
LENS = 11.5                          # half the square window's side
LENS_H = ((HOOD[2] + HOOD[3]) / 2.0 - LENS, (HOOD[2] + HOOD[3]) / 2.0 + LENS)
KNOB = (66.0, 168.0, 8.0)            # the sight's knobs, both sides
# the upper: the TR's METAL with its rail block gone, flat at H 181, the front column straight up to the top
METAL = [(42.5, 93.0), (205.0, 93.0), (210.0, 95.5), (213.5, 99.5), (215.0, 105.0), (214.5, 125.0),
         (212.5, 141.0), (208.0, 158.0), (201.0, 172.0), (193.0, TOP_H), (53.0, TOP_H), (46.5, 177.5),
         (44.0, 172.0), (42.1, 142.5)]
TOP_SLOT = [(173.0, 161.0), (191.0, 161.0), (193.0, 163.0), (193.0, 168.0), (191.0, 170.0), (175.0, 170.0),
            (173.0, 168.0)]
# our short rails for GoM's optional ones, on each side of the housing where FN put its own later (no top rail)
SIDE_RAIL = (82.0, 142.0)            # L
SIDE_RAIL_H = 166.0
RAIL_BASE, RAIL_TEETH = 3.6, 6.0     # base height, crossbar height above the surface (the TR's 175-181)
PITCH = 9.92


def teeth(La, Lb):
    out, L = [], La + 1.5
    while L + 5.3 <= Lb - 1.0:
        out.append(L)
        L += PITCH
    return out


def build_body():
    b = kit.Builder()
    box, slab, both = p90.box, p90.slab, p90.both
    # the TR's lower, receiver band, butt, panels, catch, release tab, tracks and trigger (build_p90.build_body)
    slab(b, p90.FRAME, [p90.TRIGGER_HOLE, p90.THUMBHOLE], half=p90.W_FRAME, bevel=5.0, res=1)
    box(b, 205.0, 356.0, 84.0, 118.0, -p90.W_BAND, p90.W_BAND, bevel=2.0)
    slab(b, p90.BUTT, half=p90.W_BUTT, bevel=4.0, res=1)
    both(lambda s: box(b, 320.0, 359.0, 36.0, 74.0, s * (p90.W_FRAME - 2.0), s * (p90.W_FRAME + 1.0), bevel=0.8))
    box(b, 314.0, 342.0, 104.0, 118.4, -27.0, 27.0, bevel=2.5)
    box(b, 344.0, 360.0, 119.0, 134.0, -15.0, 15.0, mat="rail", bevel=1.0)
    T = p90.TRACK
    both(lambda s: box(b, T[0], T[1], T[2], T[3], s * (p90.W_METAL - 0.5), s * (p90.W_METAL + 1.5),
                       mat="metal", bevel=0.6))
    box(b, 148.0, 169.0, 46.5, 53.0, -8.0, 8.0, mat="dark", bevel=0.8)
    # the original upper and the ring sight
    slab(b, METAL, [p90.MAG_WINDOW, TOP_SLOT], half=p90.W_METAL, bevel=2.0, res=0, mat="metal")
    hood = [(HOOD[0], HOOD[2] - 0.5), (HOOD[1] + 6.0, HOOD[2] - 0.5), (HOOD[1], HOOD[3] - 8.0), (HOOD[1], HOOD[3]),
            (HOOD[0] + 1.5, HOOD[3]), (HOOD[0], HOOD[3] - 1.5)]
    slab(b, hood, half=W_HOOD, bevel=1.5, res=1, mat="sight")
    for s in (1, -1):                                 # the knobs, a short cylinder across each side
        b.lathe("x", (0, 0, 0), [(s * (p90.W_METAL - 0.5), 0), (s * (p90.W_METAL - 0.5), KNOB[2]),
                                 (s * (p90.W_METAL + 2.2), KNOB[2]), (s * (p90.W_METAL + 3.0), KNOB[2] - 1.0),
                                 (s * (p90.W_METAL + 3.0), 0)], seg=14, mat="sight",
                xf=Matrix.Translation((0.0, L0 - KNOB[0], KNOB[1] - H0)))
    # the TR's barrel collar, knurled ring and flash hider
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, p90.BORE_Z), [(t(p90.CANON_L + 1.0), 0), (t(p90.CANON_L + 1.0), 9.3), (t(38.5), 9.3),
                                      (t(38.5), 11.0), (t(37.8), 11.7), (t(29.2), 11.7), (t(28.5), 11.0),
                                      (t(28.5), 10.4), (t(1.2), 10.4), (t(0.0), 9.2), (t(0.0), 5.0), (t(12.0), 5.0),
                                      (t(12.0), 0)], seg=16, mat="metal", phase=0.5)
    return b.to_object("P90_BODY")


def rail_side(s):
    """s = 1 the left (+x), -1 the right; origin at the housing's face, the rail's middle."""
    b = kit.Builder()
    x0 = p90.W_METAL - 0.5
    p90.box(b, SIDE_RAIL[0], SIDE_RAIL[1], SIDE_RAIL_H - 7.8, SIDE_RAIL_H + 7.8, s * x0, s * (x0 + RAIL_BASE + 0.5),
            mat="rail", bevel=0.4)
    for L in teeth(*SIDE_RAIL):
        p90.box(b, L, L + 5.3, SIDE_RAIL_H - 10.6, SIDE_RAIL_H + 10.6, s * (x0 + 0.5), s * (x0 + RAIL_TEETH + 0.5),
                mat="rail", bevel=0.5)
    return b, (s * p90.W_METAL, sum(SIDE_RAIL) / 2.0, SIDE_RAIL_H)


def at_origin(builder, where, name):
    """The rail's mesh with its point as origin (photo L, H to game mm, then the shift)."""
    x, L, H = where
    dy, dz = L0 - L, H - H0
    for v in builder.bm.verts:
        v.co.x -= x
        v.co.y -= dy
        v.co.z -= dz
    return builder.to_object(name)


# ==================================================================================================
# Painting: the TR's (build_p90.paint), the old housing's plain sides, the sight's windows and knobs
# ==================================================================================================

def paint(maps, kind):
    common = p90.common
    p90.common = lambda maps, col, mat: col          # the TR's details without its final shading
    try:
        col = p90.paint(maps, "gun" if kind == "gun" else ("carrier" if kind == "carrier" else
                                                           ("bolt" if kind == "bolt" else "rail")))
    finally:
        p90.common = common
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    if kind in ("gun", "carrier", "bolt"):
        L, H = L0 - y, z + H0
    else:                                             # a rail node: its own origin (offset by its point)
        ox, oL, oH = RAIL_ORIGINS[kind]
        L, H = oL - y, z + oH
    side = np.abs(n[..., 0]) > 0.7
    if kind == "gun":
        metal = mat == p90.MATS.index("metal")
        sight = mat == p90.MATS.index("sight")
        # the TR's rail-block recess painted on the housing's sides: the old housing is plain there, two hex screws
        # where FN's later side rail bolts on
        plain = metal & side & (L > 96) & (L < 150) & (H > 156) & (H < 176)
        col[plain] = np.array(p90.BASE["metal"], np.float32)
        for cL in (87.0, 140.0):
            p90.screw(col, L, H, metal & side & (np.abs(x) > p90.W_METAL - 0.6), cL, 167.0, r=2.6)
        # the sight's windows at both ends of the hood: dark glass with a blue cast, a lighter rim
        ends = sight & (np.abs(n[..., 1]) > 0.7) & (H > LENS_H[0]) & (H < LENS_H[1]) & (np.abs(x) < LENS)
        glow = np.clip((H - LENS_H[0]) / (LENS_H[1] - LENS_H[0]), 0, 1)[ends]
        col[ends] = np.array([22, 40, 64], np.float32) + (glow * 52.0)[..., None] * np.array([0.6, 0.9, 1.2])
        rim = sight & (np.abs(n[..., 1]) > 0.7) & ~ends & (H > LENS_H[0] - 1.5) & (H < LENS_H[1] + 1.5) &             (np.abs(x) < LENS + 1.5)
        col[rim] += 34
        # knobs: a slot across each face, a knurled edge
        knob = sight & side & (np.abs(x) > p90.W_METAL + 0.5)
        r = np.hypot(L - KNOB[0], H - KNOB[1])
        col[knob & (np.abs(H - KNOB[1]) < 0.9) & (r < KNOB[2] - 2.0)] *= 0.3
        col[sight & ~side & (np.abs(x) > p90.W_METAL) & (np.mod(np.arctan2(H - KNOB[1], L - KNOB[0]) * 7.0, 1.0)
                                                         < 0.5) & (r > KNOB[2] - 1.5) & (r < KNOB[2] + 0.5)] *= 0.6
    return np.clip(p90.common(maps, col, maps["mat"]), 0, 255)


RAIL_ORIGINS = {}                                    # kind -> (x, L, H) of a rail node's origin


def texture(objects, contexts, kinds, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = kit.bake_maps(ob, ctx, bake)
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points (upright, then turned with build_mp7.handgun_points)
# ==================================================================================================

ZERO = [0.0, 0.0, 0.0]


def g(L, H, x=0.0):
    yy, zz = p90.P(L, H)
    return [round(x * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


def points(bounds, origins):
    face = (p90.W_METAL - 0.5 + RAIL_TEETH + 0.5) * K          # the side rails' crossbar faces
    sy, sz = g(sum(SIDE_RAIL) / 2.0, SIDE_RAIL_H)[1:]
    pts = {
        "muzzle": {"offset": g(0.0, BORE_H), "rotate": [-90.0, 0.0, -180.0]},     # the TR's
        "magazine": {"offset": g(p90.MAG_L, p90.MAG_H)},
        "canon": {"offset": g(p90.CANON_L, BORE_H), "rotate": ZERO},
        # our rails, turned with the gun (their own nodes): drawn at their points with no rotate of their own
        "rail_left": {"offset": g(origins["left"][1], origins["left"][2], origins["left"][0]), "rotate": ZERO},
        "rail_right": {"offset": g(origins["right"][1], origins["right"][2], origins["right"][0]), "rotate": ZERO},
        # GoM's parts (upright, turned at their points): lights 0.0001 in
        # from the crossbar faces, lasers 0.0003 out and 0.0008 lower (fit_audit.py: the TR's 0.0007 / 0.0018 out left
        # them floating 0.5 / 2.0 on these short rails, as on the PS90's panels)
        "light_left": {"offset": [round(face - 0.0001, 4), sy, sz]},
        "laser_right": {"offset": [round(-(face + 0.0003), 4), sy, round(sz - 0.0008, 4)]},
        "bolt_fired": {"offset": [0.0, round(-p90.CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-p90.CH_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    pts = kit.handgun_points(pts)
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle; held like a pistol, so modelled upside down as GoM's "
                 "handgun-held guns are: +Z the gun's BOTTOM, +X its RIGHT; origin = rear-top of the grip column "
                 "(the TR photo's L %.0f, H %.0f)" % (L0, H0),
        "rails": "P90_RAIL_LEFT / _RIGHT on the housing's sides (L %.0f-%.0f, H %.0f): drawn for GoM's optional "
                 "Picatinny_Rail_Left / _Right, turned with the gun; no top rail, so no optics" % (SIDE_RAIL + (SIDE_RAIL_H,)),
        "magazine": "57x28Magazine50_P90 (the P90 family's magazine, upright) at its front end on top of the receiver",
        "canon": "the receiver's front face where the barrel collar starts: the P90's mount device and SP90",
        "bolt_fired": "P90_BOLT (the bolt in the port under the gun) back %.1f mm real" % p90.CARRIER_TRAVEL,
        "handle_back": "P90_HANDLE back %.0f mm real, only while racked" % p90.CH_TRAVEL,
    }
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "real_mm_per_game_unit": round(1.0 / K, 2),
                      "photo_px_per_mm": 1857 / 500.0,
                      "photo_map": "mirrored Commons photo: L = (x - 120) / 3.714, H = (970 - y) / 3.714"}
    pts["_bounds"] = bounds
    return pts


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

    body = build_body()
    bolt = p90.build_carrier()
    bolt.name = bolt.data.name = "P90_BOLT"
    handle = p90.build_handle()
    handle.name = handle.data.name = "P90_HANDLE"
    origins, rails = {}, []
    for key, (builder, where) in (("left", rail_side(1)), ("right", rail_side(-1))):
        origins[key] = where
        RAIL_ORIGINS["rail_" + key] = where
        rails.append(at_origin(builder, where, "P90_RAIL_" + key.upper()))
    kit.unwrap([body, bolt, handle] + rails, 0.006)
    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, bolt, handle] + rails, [[body, handle], [body, bolt], [body, handle]] + [[r] for r in rails],
            ["gun", "carrier", "bolt", "rail_left", "rail_right"], 256, os.path.join(TEX_DIR, "P90.png"))

    every = [body, bolt, handle] + rails
    for o in every:                                   # held like a pistol: turned 180 degrees about the bore axis
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in every}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds, origins), fh, indent=2)
        fh.write("\n")
    kit.export(every, FBX_GUN)
    for name, bd in bounds.items():
        print("%-14s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
