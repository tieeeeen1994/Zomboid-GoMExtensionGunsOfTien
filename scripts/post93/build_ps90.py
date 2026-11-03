"""FN PS90 Carbine model and texture for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_ps90.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_PS90.fbx   PS90_BODY, PS90_BOLT (the bolt under the gun), PS90_HANDLE
    P/textures/weapons/GunsOfTienPost93/PS90.png             256, body + bolt + handle
    scripts/post93/ps90_points.json                         attachment points (game space)

The PS90 (user, 2026-11-03) is the P90 TR's body (build_p90.py, imported: its photo coordinates, profiles and
painting) with what the user's photo of a PS90 shows on top of it (references/ps90/ps90_right.png, not in the repo:
a black PS90 seen from the right, muzzle left, 1200 px, with an aftermarket M-LOK handguard): the long flash hider,
the raised cheek riser on the butt and the handguard, a slab on each side over the barrel with a long window above
three M-LOK slots, a raised panel round the slots and a hand stop hooking down at its front. The photo was scaled to
the TR's photo coordinates by the body the two share: the trigger loop's and the belly's flat bottoms (L 152 and
277.5, 210 px apart) give 1.672 px per mm, and the butt's back then lands within 2 px of L 500; the bore matches
(H 98.7 against 99.8). L = 152 + (x - 570) / 1.672, H = (764 - y) / 1.672.

Held as a rifle (two-handed, SwingAnim Rifle), so nothing is turned at export: game +Y muzzle, +Z top, +X the gun's
LEFT, origin at the rear-top of the grip column (the TR's), 0.603 of real size. The handguard has no Picatinny rails
(the photo's has M-LOK slots): GoM's lights and lasers clamp onto its side panels, its foregrips under it, its
optics on the receiver's rail. The P90's magazine (57x28Magazine50_P90, upright) is drawn at `magazine`.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_p90 as p90  # noqa: E402  (sets build_mp7's K and material list)

kit = p90.kit
K = p90.K
L0, H0, BORE_H = p90.L0, p90.H0, p90.BORE_H
FBX_GUN = os.path.join(kit.MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_PS90.fbx")
POINTS_JSON = os.path.join(HERE, "ps90_points.json")
PHOTO_SCALE = 1.672                  # px per mm in the user's photo (module docstring)

# the handguard's own material (the TR's painting leaves it alone), appended to both lists
p90.MATS.append("hg")
kit.MATS.append("hg")
p90.BASE["hg"] = (44, 45, 48)        # black anodised aluminium, a little darker than the receiver

MUZZLE_L = -164.9                    # the flash hider's front (the photo; the TR's is L 0)
NOSE_L = -114.0                      # where it leaves the handguard
CANON_L = -118.0                     # the P90's mount device and SP90 start here (4 mm ahead of the nose)
HIDER_R = 9.3
X_IN, X_OUT = 25.6, 28.6             # the side slabs, over the metal upper (half 25.5)
PANEL_X = X_OUT + 1.2                # the raised panel round the M-LOK slots
STRAP_X = X_OUT + 1.5                # the raised strap and ledge
TOP_H = 136.0                        # the handguard's top (H 134.5 at the front, 138 at the back)
BOTTOM_H = 61.5                      # its underside ahead of the curve, where foregrips go
SIDE_L, SIDE_H = -70.0, 100.0        # GoM's lights / lasers: on the panel, between the front two slots
FOREGRIP_L = -60.0
OPTIC_L = 100.0                      # over the receiver's rail, where the photo's red dot sits

# side slab, (L, H), read on a 1 mm grid over the photo
PLATE = [(40.0, 138.0), (-96.0, 134.5), (-100.0, 134.0), (-103.5, 132.0), (-106.5, 127.0), (-113.0, 110.0),
         (-114.0, 106.0), (-112.0, 97.0), (-107.5, 80.0), (-104.5, 60.0), (-103.0, 45.0), (-101.0, 41.5),
         (-97.0, 41.0), (-95.0, 43.0), (-94.0, 50.0), (-93.5, 57.0), (-91.0, 60.5), (-88.0, BOTTOM_H),
         (-30.0, BOTTOM_H), (-20.0, 59.0), (-10.0, 54.5), (0.0, 47.5), (10.0, 42.0), (20.0, 39.5), (30.0, 38.5),
         (48.0, 38.0), (49.5, 92.0), (48.0, 112.5), (40.0, 112.5)]
# the long window above the slots (leaning ends), the three M-LOK slots (32 x 6.5 mm, at the bore)
WINDOW = [(-98.0, 115.5), (-28.5, 115.5), (-26.0, 118.5), (-31.5, 129.0), (-90.5, 129.0)]
MLOK = [(-97.8, -64.9), (-57.4, -23.8), (-16.3, 15.8)]
MLOK_H = (96.5, 103.0)
PANEL = [(-103.7, 92.0), (-101.7, 89.8), (20.6, 89.8), (22.6, 92.0), (22.6, 108.0), (20.6, 110.0), (-101.7, 110.0),
         (-103.7, 108.0)]
STRAP = [(-27.0, 133.5), (38.0, 133.5), (38.0, 118.0), (-19.0, 118.0)]
LEDGE = [(-6.0, 80.0), (38.0, 80.0), (38.0, 67.0), (4.0, 67.0)]
# the solid lower part between the slabs, under the barrel (the slots look into the space above it)
CORE = [(-104.5, 86.0), (-104.5, 60.0), (-103.0, 45.0), (-101.0, 41.5), (-97.0, 41.0), (-95.0, 43.0),
        (-94.0, 50.0), (-93.5, 57.0), (-91.0, 60.5), (-88.0, BOTTOM_H), (-30.0, BOTTOM_H), (-20.0, 59.0),
        (-10.0, 54.5), (0.0, 47.5), (10.0, 42.0), (20.0, 39.5), (30.0, 38.5), (46.0, 38.0), (46.0, 86.0)]
# the PS90's cheek riser on top of the butt (photo L 364-487, up to H 163.5)
RISER = [(364.0, 139.0), (364.0, 150.0), (369.0, 156.0), (377.0, 162.5), (382.0, 163.5), (476.0, 163.5),
         (483.0, 161.0), (486.5, 155.0), (486.5, 117.0), (483.0, 113.0), (392.0, 113.0), (380.0, 120.0),
         (372.0, 135.0)]
W_RISER = p90.W_BUTT + 0.6


def stadium(La, Lb, Ha, Hb, n=6):
    """A slot with round ends, as a polygon."""
    r = (Hb - Ha) / 2.0
    c = (Ha + Hb) / 2.0
    pts = [(Lb - r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, n)]
    pts += [(La + r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, n)]
    return pts


SLOTS = [stadium(a, b, *MLOK_H) for a, b in MLOK]


def build_body():
    b = kit.Builder()
    box, slab, both = p90.box, p90.slab, p90.both
    # --- the TR's body, as build_p90.build_body() but without its barrel, plus the PS90's cheek riser ---
    slab(b, p90.FRAME, [p90.TRIGGER_HOLE, p90.THUMBHOLE], half=p90.W_FRAME, bevel=5.0, res=1)
    box(b, 205.0, 356.0, 84.0, 118.0, -p90.W_BAND, p90.W_BAND, bevel=2.0)
    slab(b, p90.BUTT, half=p90.W_BUTT, bevel=4.0, res=1)
    slab(b, RISER, half=W_RISER, bevel=3.0, res=1)
    both(lambda s: box(b, 320.0, 359.0, 36.0, 74.0, s * (p90.W_FRAME - 2.0), s * (p90.W_FRAME + 1.0), bevel=0.8))
    box(b, 314.0, 342.0, 104.0, 118.4, -27.0, 27.0, bevel=2.5)
    box(b, 344.0, 360.0, 119.0, 134.0, -15.0, 15.0, mat="rail", bevel=1.0)
    slab(b, p90.METAL, [p90.MAG_WINDOW, p90.TOP_SLOT], half=p90.W_METAL, bevel=2.0, res=0, mat="metal")
    box(b, 57.0, 198.0, 175.0, 178.6, -7.8, 7.8, mat="rail", bevel=0.4)
    for L in p90.RAIL_TEETH:
        box(b, L, L + 5.3, 175.0, p90.RAIL_TOP_H, -10.6, 10.6, mat="rail", bevel=0.5)

    def boss(s):
        box(b, 77.0, 89.0, 149.5, 172.0, s * (p90.W_METAL - 1.0), s * p90.BOSS_X, mat="metal", bevel=0.6)
        box(b, 71.0, 95.0, 156.5, 167.5, s * (p90.W_METAL - 1.0), s * p90.BOSS_X, mat="metal", bevel=0.6)
    both(boss)
    T = p90.TRACK
    both(lambda s: box(b, T[0], T[1], T[2], T[3], s * (p90.W_METAL - 0.5), s * (p90.W_METAL + 1.5),
                       mat="metal", bevel=0.6))
    p90.build_trigger(b)

    # --- the handguard: two slabs with the window and slots, the raised panel, strap and ledge, a top cover, the
    # solid lower part ---
    holes = [WINDOW] + SLOTS
    both(lambda s: slab(b, PLATE, holes, half=(X_OUT - X_IN) / 2.0, bevel=0.7, res=0, mat="hg",
                        x0=s * (X_IN + X_OUT) / 2.0))
    both(lambda s: slab(b, PANEL, SLOTS, half=(PANEL_X - X_OUT + 0.4) / 2.0, bevel=0.4, res=0, mat="hg",
                        x0=s * (X_OUT - 0.4 + PANEL_X) / 2.0))
    for outline in (STRAP, LEDGE):
        both(lambda s, o=outline: slab(b, o, half=(STRAP_X - X_OUT + 0.4) / 2.0, bevel=0.5, res=0, mat="hg",
                                       x0=s * (X_OUT - 0.4 + STRAP_X) / 2.0))
    p90.box(b, -100.0, 40.0, TOP_H - 3.0, TOP_H, -X_OUT, X_OUT, mat="hg", bevel=1.0)
    slab(b, CORE, half=X_IN + 0.2, bevel=1.0, res=0, mat="hg")

    # --- barrel inside the handguard, the PS90's long slotted flash hider (lathe t = game y) ---
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(43.5), 0), (t(43.5), 8.0), (t(NOSE_L + 4.0), 8.0), (t(NOSE_L + 4.0), HIDER_R),
                                       (t(MUZZLE_L + 1.2), HIDER_R), (t(MUZZLE_L), HIDER_R - 1.2),
                                       (t(MUZZLE_L), 5.0), (t(MUZZLE_L + 12.0), 5.0), (t(MUZZLE_L + 12.0), 0)],
            seg=16, mat="metal", phase=0.5)
    return b.to_object("PS90_BODY")


def rename(ob, name):
    ob.name = name
    ob.data.name = name                 # the FBX geometry takes the mesh's name
    return ob


# ==================================================================================================
# Painting: the TR's (build_p90.paint) for everything it knows, then the handguard, riser and flash hider
# ==================================================================================================

def paint(maps, kind):
    common = p90.common
    p90.common = lambda maps, col, mat: col          # the TR's details without its final shading
    try:
        col = p90.paint(maps, kind)
    finally:
        p90.common = common
    if kind == "gun":
        p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        L, H = L0 - y, z + H0
        side = np.abs(n[..., 0]) > 0.7
        hg = mat == p90.MATS.index("hg")
        metal = mat == p90.MATS.index("metal")
        polymer = mat == p90.MATS.index("polymer")
        # hex screws: the handguard's clamp screws (the photo's), four detents on the strap
        outer = hg & side & (np.abs(x) > X_OUT - 0.4)
        for cL, cH in ((45.0, 127.0), (45.0, 74.0)):
            p90.screw(col, L, H, outer, cL, cH, r=3.0)
        for cL in (5.0, 11.0, 17.0, 23.0):
            dot = outer & (np.abs(x) > STRAP_X - 0.3) & (np.hypot(L - cL, H - 124.5) < 1.3)
            col[dot] *= 0.35
        # the cheek riser: its seam on the butt, the latch slot, two screws
        rs = polymer & side & (np.abs(x) > W_RISER - 0.4) & (L > 363) & (H > 111)
        col[rs & ((np.abs(H - 113.2) < 0.5) & (L > 385) & (L < 484))] *= 0.45
        slot = rs & (L > 437) & (L < 467) & (H > 121.5) & (H < 127.5)
        col[slot] = col[slot] * 0.2 + 3
        frame = rs & (L > 431) & (L < 474) & (H > 115) & (H < 133) & ~slot
        col[frame] += 8
        for cL, cH in (420.0, 121.0), (479.0, 117.5):
            p90.screw(col, L, H, rs, cL, cH, r=2.4)
        # flash hider: four long slots, the bore
        r = np.hypot(x, z - (BORE_H - H0))
        a = np.arctan2(x, z - (BORE_H - H0))
        hider = metal & (L < NOSE_L) & (r > HIDER_R - 0.5)
        for k in range(4):
            arc = (np.mod(a - (k + 0.5) * math.pi / 2 + math.pi, 2 * math.pi) - math.pi) * HIDER_R
            col[hider & (np.abs(arc) < 1.6) & (L > MUZZLE_L + 5.0) & (L < NOSE_L - 9.0)] = 8
        col[metal & (r < 5.4) & (L < MUZZLE_L + 12.5)] = 7
    return np.clip(p90.common(maps, col, maps["mat"]), 0, 255)


def texture(objects, contexts, kinds, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = kit.bake_maps(ob, ctx, bake)
        if kit.DEBUG:
            kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points
# ==================================================================================================

def g(L, H, x=0.0):
    yy, zz = p90.P(L, H)
    return [round(x * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def euler_xyz(R):
    """rotateXYZ angles (degrees) of R = Rx(a) Ry(b) Rz(c), the engine's attachment rotation."""
    b = math.asin(max(-1.0, min(1.0, R[0][2])))
    a = math.atan2(-R[1][2], R[2][2])
    c = math.atan2(-R[0][1], R[0][0])
    return [round(math.degrees(v), 4) + 0.0 for v in (a, b, c)]


def rot_xyz(deg):
    a, b, c = [math.radians(v) for v in deg]
    rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return rx @ ry @ rz


# GoM's STANAG 30 in the off hand (its FAMAS's only magazine; gen_scripts.py GOM_STANAG_PROP2): modelled about its
# feed lips, hanging down. The P90's magazine is modelled about its feed end on top of the gun, lying back along -Y;
# stood on its feed end first (Rz 180 . Rx 90: its length down, its depth forward), it is drawn where GoM's STANAG is.
GOM_STANAG_PROP2 = {"offset": [0.0200, 0.0538, -0.0146], "rotate": [-94.9600, 23.4300, -89.8200]}


def magazine_prop2():
    q = rot_xyz([0.0, 0.0, 180.0]) @ rot_xyz([90.0, 0.0, 0.0])
    r = rot_xyz(GOM_STANAG_PROP2["rotate"]) @ q
    assert np.allclose(rot_xyz(euler_xyz(r)), r, atol=1e-4)
    return {"offset": list(GOM_STANAG_PROP2["offset"]), "rotate": euler_xyz(r)}


# How far GoM's parts sit from the surface they clamp to (fit_audit.py, against GoM's own guns): set so lights,
# lasers and foregrips reach about as far into the panel / underside as they reach into GoM's rails.
LIGHT_IN, LASER_OUT, LASER_DOWN, FOREGRIP_UP = -0.0001, 0.0008, 0.0008, -0.0008


def points(bounds):
    rail_top = (p90.RAIL_TOP_H - H0) * K
    oy = g(OPTIC_L, 0)[1]
    sy, sz = g(SIDE_L, SIDE_H)[1:]
    face = PANEL_X * K
    bottom = (BOTTOM_H - H0) * K
    pts = {
        "muzzle": {"offset": g(MUZZLE_L, BORE_H), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": g(CANON_L, BORE_H), "rotate": ZERO},
        "magazine": {"offset": g(p90.MAG_L, p90.MAG_H), "rotate": ZERO},
        # the TR's relations to the rail's top (GoM's Picatinny_Rail_Up and the MP5's scope)
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        # under the handguard, and its M-LOK panels (no rails drawn: the clamps take an M-LOK rail section's place)
        "rail_down": {"offset": [0.0, g(FOREGRIP_L, 0)[1], round(bottom + 0.0025, 4)], "rotate": ZERO},
        "foregrip": {"offset": [0.0, g(FOREGRIP_L, 0)[1], round(bottom + FOREGRIP_UP, 4)], "rotate": ZERO},
        "rail_left": {"offset": [round(X_OUT * K, 4), sy, sz], "rotate": ZERO},
        "light_left": {"offset": [round(face - LIGHT_IN, 4), sy, sz], "rotate": ZERO},
        "rail_right": {"offset": [round(-X_OUT * K, 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(face + LASER_OUT), 4), sy, round(sz - LASER_DOWN, 4)], "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-p90.CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-p90.CH_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / p90.K_OLD, 4), round(0.13 * K / p90.K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},                               # every GoM rifle's, scaled
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; held as a rifle, so upright "
                 "(the P90 TR is turned); origin = rear-top of the grip column (the TR photo's L %.0f, H %.0f)"
                 % (L0, H0),
        "magazine": "57x28Magazine50_P90 (the TR's magazine model, upright) at its front end, on top of the receiver",
        "canon": "4 mm ahead of the handguard's nose (L %.0f) on the flash hider: P90_Muzzle_Mount_Device and "
                 "P90_Suppressor as on the TR" % NOSE_L,
        "accessories": "optics on the receiver's rail at L %.0f; lights / lasers on the handguard's M-LOK panels at "
                       "L %.0f, H %.0f; foregrips under it at L %.0f (no rails drawn)" % (OPTIC_L, SIDE_L, SIDE_H,
                                                                                         FOREGRIP_L),
        "bolt_fired": "PS90_BOLT (the bolt in the ejection port under the gun) back %.1f mm real" % p90.CARRIER_TRAVEL,
        "handle_back": "PS90_HANDLE (both charging handles) back %.0f mm real, only while racked" % p90.CH_TRAVEL,
        "prop2": "the P90 magazine's Bip01_Prop2 for GoM's FAMAS reload (attachToHand): stood on its feed end and "
                 "drawn where GoM's STANAG 30 is",
    }
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE_H,
                      "real_mm_per_game_unit": round(1.0 / K, 2), "k": K, "prop2": magazine_prop2(),
                      "length_mm": 500.0 - MUZZLE_L, "photo_px_per_mm": PHOTO_SCALE,
                      "photo_map": "L = 152 + (x - 570) / 1.672, H = (764 - y) / 1.672"}
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
    bolt = rename(p90.build_carrier(), "PS90_BOLT")
    handle = rename(p90.build_handle(), "PS90_HANDLE")
    kit.unwrap([body, bolt, handle], 0.006)
    os.makedirs(kit.TEX_DIR, exist_ok=True)
    texture([body, bolt, handle], [[body, handle], [body, bolt], [body, handle]], ["gun", "carrier", "bolt"], 256,
            os.path.join(kit.TEX_DIR, "PS90.png"))

    bounds = {o.name: kit.bounds_of(o) for o in (body, bolt, handle)}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")
    kit.export([body, bolt, handle], FBX_GUN)
    for name, bd in bounds.items():
        print("%-14s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
