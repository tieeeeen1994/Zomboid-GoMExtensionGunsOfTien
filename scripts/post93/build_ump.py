"""H&K UMP45 and UMP9 models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_ump.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx          UMP_BODY, UMP_BOLT (both guns)
    P/models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx  9x19Magazine30_UMP, 45Magazine25_UMP,
                                                                  45Magazine20_UMP, 45Magazine10_UMP
    P/models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx       UMP_STOCK (both guns)
    P/textures/weapons/GunsOfTienPost93/<name>.png                UMP9, UMP45 (256, the same body and charging handle
                                                                  with each gun's markings), 128 for the stock and
                                                                  each magazine
    scripts/post93/ump_points.json                                attachment points (game space, both guns)

The UMP is one polymer body for every calibre (H&K changes calibre with the barrel, bolt and magazine), so both guns
share one mesh, stock and set of attachment points; only the textures (markings) and the magazines differ (user,
2026-10-22: two separate guns, no conversion recipe). Traced from H&K's product photo of a UMP9 (left side, stock
deployed, 30-round magazine; the user's, not kept in the repo) by trace_outline.py, scaled by its top Picatinny rail
(18.13 px per 10.0 mm crossbar: 695 mm long with the stock deployed, H&K publishes 690); the right side (stock hinge,
ejection port) from the user's second reference, a third-party render of a UMP .45, whose own proportions are off and
were not measured. Profiles are written in the photo's (L, H) mm: L back from the muzzle tip, H up from the lowest
point (the 30-round magazine's base).

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at the
rear-top of the pistol grip, drawn at 0.72 of real size like GoM's MP5 family and our MP7 / P90; held as a rifle like
GoM's MP5 (two hands, back slot). The stock is one node modelled deployed with its origin at the hinge (its front face
on the bore axis); `stock_folded` swings it 180 degrees about the hinge pin on the right, as H&K's folds along the
receiver's right side. The charging handle does not reciprocate (as the MP5's): `bolt_fired` = `bolt_lock`.

Magazines hang from `magazine` (the feed lips) with their rake built in: the UMP9's 30-round curves forward from about
16 degrees under the receiver to 36 at its base (fitted to the photo's edges within 1 mm); the .45 magazines are straight at 18 degrees, the
25-round about as long as the UMP9's 30 (12.5 levels of .45 against 15 of 9mm) and the 20 / 10 shorter by 7.9 mm a
round (0.66 x the case diameter, a Glock 17 against its 33-round magazine). No published drawing of them was found.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402

MEDIA = kit.MEDIA
TEX_DIR = kit.TEX_DIR
FBX = {
    "gun": os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UMP.fbx"),
    "mags": os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UMP_magazines.fbx"),
    "parts": os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UMP_parts.fbx"),
}
POINTS_JSON = os.path.join(HERE, "ump_points.json")

K = 0.00072                        # game units per real mm: GoM's MP5 family
kit.K = K
MATS = ["polymer", "grip", "rail", "metal", "dark", "rubber", "magpoly", "smoke", "brass", "copper"]
kit.MATS[:] = MATS

# Photo frame: the origin is the rear-top of the pistol grip (its back edge meets the receiver), the bore axis H.
L0, H0 = 393.0, 171.0
BORE = 209.8
MUZZLE_FACE = 34.2                 # the receiver's nose where the barrel leaves it
CANON_L = 21.5                     # the barrel collar's front face (build_body's lathe), behind the threads
HINGE_L = 440.0                    # the receiver's rear face = the stock's front face
TOP = 252.6                        # upper receiver top (the rail sits on it)
SEAM = 229.0                       # upper / lower seam
HG_BOTTOM = 190.0                  # handguard bottom (the bottom rail hangs under it)
RAIL_TOP = (210.6, 370.5)          # top Picatinny rail, L
RAIL_FLOOR, RAIL_BASE, RAIL_CROSS = 253.1, 258.0, 260.8
SIDE_RAIL, SIDE_RAIL_H = (52.0, 157.0), 211.0
BOTTOM_RAIL, BOTTOM_TEETH = (55.0, 160.0), 179.8
OPTIC_L, FOREGRIP_L = 300.0, 112.0
W_UPPER, W_LOWER, W_HG, W_GRIP, W_GUARD = 21.0, 22.0, 22.0, 15.0, 7.0      # half widths, mm
W_STOCK, W_STOCK_FRONT = 13.0, 19.0
MAG_TOP = (234.0, 192.0)           # feed lips, photo L / H


def P(L, H):
    """Photo (L, H) mm -> game (y, z) mm."""
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def both(fn):
    for s in (1, -1):
        fn(s)


# ==================================================================================================
# Profiles (photo L, H mm), from the traced outline (tmp/ref/ump/ump9_outline.json) and the photo's details
# ==================================================================================================

UPPER = [(36.4, SEAM - 0.5), (36.4, 229.4), (38.0, 232.1), (40.0, TOP), (HINGE_L - 7.0, TOP),
         (HINGE_L, 251.4), (HINGE_L, SEAM - 0.5)]
# handguard and lower receiver in one polymer moulding: the nose, the magazine well, the trigger housing, the curve up
# behind the grip to the receiver's rear
LOWER = [(35.0, HG_BOTTOM), (MUZZLE_FACE, 202.4), (MUZZLE_FACE, 217.2), (35.8, 220.0), (36.4, SEAM + 0.5),
         (HINGE_L, SEAM + 0.5), (HINGE_L, 186.0), (432.8, 185.3), (401.4, 177.5), (393.1, 170.4), (390.0, 164.0),
         (352.0, 160.0), (252.0, 160.0), (247.0, 158.0), (246.5, 147.0), (243.0, 145.5), (196.5, 149.5),
         (193.0, 152.7), (199.6, 179.8), (183.6, 179.2), (161.6, HG_BOTTOM - 0.3)]
GRIP = [(352.0, 162.0), (350.5, 132.0), (355.6, 125.7), (379.4, 72.8), (381.0, 68.4), (379.4, 65.6), (379.4, 61.8),
        (382.1, 59.5), (386.0, 60.1), (403.6, 69.5), (425.1, 82.2), (427.9, 84.9), (427.3, 88.2), (392.0, 145.6),
        (389.3, 152.7), (389.3, 161.6), (391.5, 166.0)]
GUARD = [(252.0, 161.0), (253.6, 140.1), (270.7, 137.8), (274.0, 136.2), (279.6, 126.3), (286.7, 122.4),
         (331.4, 122.4), (339.7, 125.7), (349.6, 131.8), (353.0, 140.0), (353.0, 161.0)]
GUARD_HOLE = [(272.5, 159.0), (272.5, 152.0), (276.0, 143.0), (282.5, 133.5), (290.5, 127.0), (330.0, 126.8),
              (337.5, 129.0), (344.0, 134.0), (347.0, 141.0), (347.0, 159.0)]
TRIGGER = [(328.5, 159.5), (336.0, 159.5), (336.0, 150.0), (334.5, 141.0), (330.5, 134.5), (324.5, 130.0),
           (321.5, 130.5), (322.5, 133.0), (327.5, 137.5), (329.5, 143.0), (329.0, 150.0)]
# the paddle magazine release behind the magazine well (H&K's, both sides at once)
PADDLE = [(246.0, 148.0), (246.5, 126.0), (248.0, 124.0), (250.5, 124.5), (251.0, 135.0), (253.0, 141.0),
          (252.5, 148.0)]
FRONT_SIGHT = [(40.0, TOP - 0.5), (41.0, 260.3), (45.2, 270.7), (47.4, 280.1), (51.8, 286.7), (64.0, 286.2),
               (72.8, 263.0), (78.8, 256.9), (85.5, 254.2), (90.4, 253.6), (90.4, TOP - 0.5)]
REAR_SIGHT = [(373.8, TOP - 0.5), (373.8, 272.9), (379.4, 275.7), (394.8, 275.7), (432.3, 254.2), (432.3, TOP - 0.5)]
# sling mount under the nose
SLING = [(35.8, 178.6), (40.3, 169.8), (40.8, 163.2), (53.5, 163.8), (54.6, 179.2), (56.0, HG_BOTTOM + 0.5),
         (35.5, HG_BOTTOM + 0.5)]
SLING_HOLE = [(44.0, 167.5), (50.5, 167.5), (51.0, 175.5), (44.0, 175.5)]
# bolt catch lever on the left, in front of the magazine well; the selector lever above the grip (both sides)
CATCH = [(186.0, 181.0), (186.0, 191.5), (191.0, 195.5), (204.0, 195.5), (204.0, 191.0), (196.0, 187.0),
         (195.0, 181.0)]
SELECTOR = [(343.0, 184.0), (343.0, 188.0), (352.0, 192.5), (361.5, 190.0), (362.0, 186.5), (352.0, 180.5)]
SELECTOR_PIVOT = (352.0, 186.0)
HANDLE = (65.0, 85.0, 236.5, 247.5)            # charging handle knob, L / H

# The folding stock, as photographed (deployed); its own frame is shifted to the hinge in build_stock().
STOCK = [(HINGE_L, 186.4), (HINGE_L, 251.4), (442.2, 251.4), (450.5, 249.2), (477.0, 233.8), (496.2, 228.3),
         (506.7, 226.6), (689.8, 225.5), (692.5, 224.4), (695.3, 220.6), (692.5, 173.7), (694.7, 122.4),
         (692.5, 119.1), (688.1, 117.4), (679.3, 118.5), (676.6, 116.9), (660.6, 117.4), (476.4, 185.3),
         (469.8, 186.4)]
STOCK_WINDOW = [(645.7, 210.1), (665.5, 209.5), (666.6, 207.9), (666.1, 151.1), (662.2, 145.0), (652.3, 142.3),
                (647.9, 137.8), (642.4, 136.7), (590.0, 154.9), (581.7, 161.0), (579.5, 164.9), (570.7, 199.6),
                (570.1, 205.7), (571.2, 207.9), (574.5, 209.5)]
STOCK_OVAL = [(509.0, 191.0), (510.0, 205.0), (514.0, 210.0), (552.0, 210.0), (556.0, 206.0), (556.0, 183.0),
              (551.0, 178.0), (541.0, 177.5), (527.0, 181.5), (516.0, 186.5)]
STOCK_BLOCK = [(HINGE_L, 186.4), (HINGE_L, 251.4), (442.2, 251.4), (450.5, 249.2), (470.0, 237.5), (470.0, 186.4)]
PAD_L = 676.0                      # the rubber butt pad behind this
HINGE_X = -(W_LOWER + W_STOCK_FRONT) / 2.0 - 1.0   # the hinge pin, on the right (-X)


# ==================================================================================================
# Geometry
# ==================================================================================================

def picatinny(b, La, Lb, frame, **kw):
    ya, yb = sorted((L0 - La, L0 - Lb))
    kit.picatinny(b, ya, yb, frame, **kw)


def build_body():
    b = kit.Builder()
    slab(b, UPPER, half=W_UPPER, bevel=1.8, res=1)
    slab(b, LOWER, half=W_LOWER, bevel=2.2, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=4.0, res=1, mat="grip")
    slab(b, GUARD, [GUARD_HOLE], half=W_GUARD, bevel=1.6, res=1)
    slab(b, TRIGGER, half=3.0, bevel=0.6, mat="dark")
    slab(b, PADDLE, half=9.0, bevel=0.8, mat="dark")
    slab(b, FRONT_SIGHT, half=10.0, bevel=1.4, res=1)
    slab(b, REAR_SIGHT, half=16.0, bevel=1.6, res=1)
    slab(b, [(370.5, TOP - 0.5), (370.5, 258.0), (372.2, 261.9), (373.8, 261.9), (373.8, TOP - 0.5)],
         half=5.0, bevel=0.5, mat="dark")                                  # the rear sight's elevation stop
    slab(b, SLING, [SLING_HOLE], half=12.0, bevel=1.2)
    slab(b, CATCH, half=1.0, bevel=0.4, mat="dark", x0=W_LOWER + 0.8)        # left side only
    both(lambda s: slab(b, SELECTOR, half=1.0, bevel=0.4, mat="dark", x0=s * (W_LOWER + 2.0)))
    cl, ch = SELECTOR_PIVOT
    y, z = P(cl, ch)
    both(lambda s: b.lathe("x", (0, y, z), [(s * (W_LOWER - 0.5), 0), (s * (W_LOWER - 0.5), 6.0),
                                             (s * (W_LOWER + 2.2), 6.0), (s * (W_LOWER + 2.8), 4.6),
                                             (s * (W_LOWER + 2.8), 0)], seg=12, mat="dark"))
    # rails: the top one on the upper receiver, the side and bottom ones bolted to the handguard
    picatinny(b, RAIL_TOP[1] - 0.5, RAIL_TOP[0], lambda u, h, yy: Vector((u, yy, RAIL_FLOOR - H0 + h)),
              base_h=RAIL_BASE - RAIL_FLOOR, tooth_h=RAIL_CROSS - RAIL_BASE + 1.0)
    picatinny(b, BOTTOM_RAIL[1], BOTTOM_RAIL[0], lambda u, h, yy: Vector((u, yy, HG_BOTTOM - H0 - h)),
              base_h=5.0, tooth_h=HG_BOTTOM - BOTTOM_TEETH - 5.0 + 1.0)
    for s in (1, -1):
        picatinny(b, SIDE_RAIL[1], SIDE_RAIL[0],
                  lambda u, h, yy, s=s: Vector((s * (W_HG + h), yy, SIDE_RAIL_H - H0 + u)), base_h=1.5, tooth_h=3.0)
    # the barrel out of the nose: its shoulder, collar and threaded muzzle (no flash hider, as photographed)
    by, bz = 0.0, BORE - H0
    b.lathe("y", (0, by, bz), [(P(MUZZLE_FACE + 3.0, 0)[0], 0), (P(MUZZLE_FACE + 3.0, 0)[0], 7.4),
                               (P(25.9, 0)[0], 7.4), (P(24.8, 0)[0], 9.4), (P(CANON_L, 0)[0], 9.4),
                               (P(16.0, 0)[0], 6.0), (P(1.0, 0)[0], 5.8), (P(0.0, 0)[0], 4.8), (P(0.0, 0)[0], 0)],
            seg=16, mat="metal", phase=0.5)
    return b.to_object("UMP_BODY")


def build_bolt():
    """The charging handle on the left of the upper receiver's front, forward (it does not reciprocate)."""
    b = kit.Builder()
    La, Lb, Ha, Hb = HANDLE
    box(b, La + 3.0, Lb - 3.0, Ha + 2.5, Hb - 2.5, W_UPPER - 3.0, W_UPPER + 2.0, mat="dark", bevel=0.8)
    box(b, La, Lb, Ha, Hb, W_UPPER + 2.0, W_UPPER + 9.0, mat="dark", bevel=2.0)
    return b.to_object("UMP_BOLT")


def build_stock():
    """Origin = the hinge: the stock's front face on the bore axis; modelled deployed, extending along -Y."""
    b = kit.Builder()
    q = lambda pts: [(HINGE_L - L, H - BORE) for L, H in pts]
    kit.slab(b, q(STOCK), [q(STOCK_WINDOW), q(STOCK_OVAL)], W_STOCK, 2.4, 1, "polymer", 0.0)
    kit.slab(b, q(STOCK_BLOCK), [], W_STOCK_FRONT, 2.0, 1, "polymer", 0.0)
    pad = [(L, H) for L, H in STOCK if L >= PAD_L - 0.5]
    lo, hi = min(H for _, H in pad), max(H for _, H in pad)
    b.box(-W_STOCK - 0.6, W_STOCK + 0.6, HINGE_L - 695.0, HINGE_L - PAD_L, lo - BORE + 1.0, hi - BORE - 1.0,
          mat="rubber", bevel=1.5)
    # the hinge knuckles on the right rear corner of the receiver, round the pin (they stay put when it folds)
    for h0, h1 in ((190.0, 206.0), (232.0, 248.0)):
        b.lathe("z", (HINGE_X, 0.0, 0.0), [(h0 - BORE, 0), (h0 - BORE, 4.5), (h1 - BORE, 4.5),
                                                      (h1 - BORE, 0)], seg=12, mat="metal")
    return b.to_object("UMP_STOCK")


MAGS = {  # name: (rounds, length from the lips to the base plate's bottom, half width, half depth, kind)
    "9x19Magazine30_UMP": (30, 200.0, 11.5, 21.0, "curved"),
    "45Magazine25_UMP": (25, 196.0, 12.5, 22.0, "straight"),
    "45Magazine20_UMP": (20, 156.5, 12.5, 22.0, "straight"),
    "45Magazine10_UMP": (10, 77.5, 12.5, 22.0, "straight"),
}
CURVE_A0, CURVE_A1 = math.radians(16.0), math.radians(36.0)       # the UMP9's 30-round, top to base
STRAIGHT_A = math.radians(18.0)
BASE_T = 6.0                       # base plate thickness


def mag_axis(s, length, kind):
    """Point (y forward, z) mm and rake (radians from vertical, toward the muzzle) at s along the axis from the lips."""
    if kind == "straight":
        a = STRAIGHT_A
        return (s * math.sin(a), -s * math.cos(a)), a
    k = (CURVE_A1 - CURVE_A0) / length
    a = CURVE_A0 + k * s
    # integral of (sin a, -cos a) ds from 0 to s
    y = (math.cos(CURVE_A0) - math.cos(a)) / k
    z = -(math.sin(a) - math.sin(CURVE_A0)) / k
    return (y, z), a


def mag_local(y, z, length, kind):
    """A magazine texel (built frame) -> (s along the axis from the lips, u across it, + toward the muzzle)."""
    if kind == "straight":
        a = STRAIGHT_A
        return y * math.sin(a) - z * math.cos(a), y * math.cos(a) + z * math.sin(a)
    k = (CURVE_A1 - CURVE_A0) / length
    r = 1.0 / k
    # the axis is an arc about the centre c (perpendicular to the start direction, toward the muzzle side)
    cy, cz = r * math.cos(CURVE_A0), r * math.sin(CURVE_A0)
    dy, dz = y - cy, z - cz
    ang = np.arctan2(dz, dy) - math.atan2(-cz, -cy)
    ang = np.mod(ang + math.pi, 2 * math.pi) - math.pi
    s = ang * r
    u = r - np.hypot(dy, dz)
    return s, u


def mag_ring(bm, s, length, kind, w, d, c, du=0.0):
    (cy, cz), a = mag_axis(s, length, kind)
    ny, nz = math.cos(a), math.sin(a)                 # across the magazine, toward the muzzle
    sec = [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]
    return [bm.verts.new((x, cy + (u + du) * ny, cz + (u + du) * nz)) for x, u in sec]


def sweep(b, s_list, length, kind, w, d, c, mat, du=0.0):
    bm = b.bm
    rings = [mag_ring(bm, s, length, kind, w, d, c, du) for s in s_list]
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_magazine(name):
    """Double-stack polymer magazine, origin at the feed lips (top centre), raked forward as it hangs from the gun.
    H&K's 9mm magazine is black; its .45 magazines are smoked translucent polymer."""
    rounds, length, w, d, kind = MAGS[name]
    nine = name.startswith("9x19")
    mat = "magpoly" if nine else "smoke"
    b = kit.Builder()
    end = length - BASE_T
    steps = sorted({round(s, 3) for s in [4.0 + k * 8.0 for k in range(int((end - 4.0) // 8.0) + 1)] + [end]})
    sweep(b, steps, length, kind, w, d, 1.8, mat)
    sweep(b, [0.0, 4.5], length, kind, w - 3.0, d - 3.0, 1.5, mat)              # feed lips
    sweep(b, [44.0, 50.0], length, kind, w + 0.6, d + 0.6, 2.0, mat)            # the stop ridge under the magazine well
    sweep(b, [end - 0.5, length], length, kind, w + 1.2, d + 1.6, 2.2, "magpoly")   # base plate
    # the top round, bullet forward (9mm: copper-jacketed; .45: a fat round-nose)
    if nine:
        b.lathe("y", (0, -2.0, -3.6), [(-13.0, 0), (-13.0, 4.9), (6.0, 4.9), (6.5, 4.5)], seg=8, mat="brass")
        b.lathe("y", (0, -2.0, -3.6), [(6.5, 4.5), (11.0, 4.2), (14.5, 2.4), (15.7, 0)], seg=8, mat="copper")
    else:
        b.lathe("y", (0, -2.0, -4.5), [(-15.0, 0), (-15.0, 6.0), (7.8, 6.0), (8.2, 5.6)], seg=8, mat="brass")
        b.lathe("y", (0, -2.0, -4.5), [(8.2, 5.6), (12.0, 5.3), (16.0, 3.4), (17.4, 0)], seg=8, mat="copper")
    return b.to_object(name)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: H&K's black polymer, a slightly warmer grip, blackened steel rails and barrel
    "polymer": (44, 44, 46), "grip": (40, 40, 42), "rail": (36, 36, 38), "metal": (54, 55, 58), "dark": (22, 22, 23),
    "rubber": (30, 30, 31), "magpoly": (40, 40, 42), "smoke": (66, 62, 58), "brass": (150, 118, 62),
    "copper": (140, 82, 52),
}

for ch, rows in {"U": ["101", "101", "101", "101", "111"], "9": ["111", "101", "111", "001", "111"],
                 "5": ["111", "100", "111", "001", "111"], "H": ["101", "101", "111", "101", "101"],
                 "K": ["101", "110", "100", "110", "101"], "C": ["111", "100", "100", "100", "111"],
                 "L": ["100", "100", "100", "100", "111"], "O": ["111", "101", "101", "101", "111"]}.items():
    kit.FONT.setdefault(ch, rows)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "rail", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.98 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 72.0, 56.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint_gun(maps, kind, col):
    """The body and charging handle: kind UMP9 or UMP45 (the markings)."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    poly = mat == MATS.index("polymer")
    upper = poly & side & (np.abs(x) > W_UPPER - 0.6) & (H > SEAM - 1.0)
    lower = poly & side & (np.abs(x) > W_LOWER - 0.6) & (H < SEAM + 1.0)
    body = upper | lower
    grip = (mat == MATS.index("grip")) & side & (np.abs(x) > W_GRIP - 0.8)
    # the upper / lower seam, the charging handle's slot (left), the handguard's vent slots over the side rails
    col[body & (np.abs(H - SEAM) < 0.7) & (L > 37) & (L < HINGE_L - 1)] *= 0.5
    col[upper & left & rounded_rect(L, H, 84.0, 160.0, 238.5, 245.5, 3.0)] = 10
    for La, Lb in ((60.0, 100.0), (120.0, 155.0)):
        col[lower & rounded_rect(L, H, La, Lb, 217.5, 223.0, 2.5)] = 9
    # ejection port on the right of the upper receiver, over the magazine well, the bolt behind it
    port = upper & right & rounded_rect(L, H, 200.0, 258.0, 231.5, 246.0, 2.5)
    col[port] = col[port] * 0.2 + 10
    col[port & (H < 240) & (L > 214) & (L < 250)] += 34                       # the bolt face
    col[upper & right & rounded_rect(L, H, 198.0, 260.0, 229.5, 248.0, 3.5) & ~port] *= 0.7
    # pins and screws through the receiver (the photo's), the side rails' two screws
    for cL, cH in ((193.0, 198.0), (258.0, 199.5), (271.0, 181.0), (325.0, 182.0), (345.0, 169.0), (415.0, 189.0),
                   (420.0, 214.0)):
        pin(col, L, H, lower, cL, cH)
    for cL, cH in ((380.0, 241.0), (408.0, 240.0)):
        pin(col, L, H, upper, cL, cH, 2.0)
    for cL in (SIDE_RAIL[0] - 7.0, SIDE_RAIL[1] - 7.0):
        pin(col, L, H, (poly | (mat == MATS.index("rail"))) & side, cL, SIDE_RAIL_H, 3.2)
    # selector: safe (white), single, two-round and automatic (red), both sides, as the photo's
    for m, c in ((rounded_rect(L, H, 352.0, 361.0, 193.0, 197.0, 0.8), (205, 205, 200)),
                 (rounded_rect(L, H, 360.0, 368.0, 172.5, 176.5, 0.8), (186, 46, 40)),
                 (rounded_rect(L, H, 344.0, 360.0, 165.5, 169.5, 0.8) & (np.mod(L - 344.0, 5.4) < 4.4), (186, 46, 40)),
                 (rounded_rect(L, H, 330.0, 360.0, 161.0, 164.5, 0.8) & (np.mod(L - 330.0, 6.0) < 5.0), (186, 46, 40))):
        col[lower & m] = c
    # markings: "HK UMP" and the calibre on the left, read the right way in game (left side u = +L; CLAUDE.md
    # "Handedness of the review renders"); the calibre again on the right over the magazine well (u = -L)
    col[lower & left & text_mask(L, H, "HK UMP", 226.0, 201.5, 6.0)] += 34
    cal = "9X19" if kind == "UMP9" else ".45 ACP"
    col[lower & left & text_mask(L, H, cal, 162.0, 205.0, 4.0)] += 30
    col[lower & right & text_mask(-L, H, kind, -246.0, 201.5, 6.0)] += 34
    col[lower & left & rounded_rect(L, H, 266.0, 306.0, 199.0, 212.0, 1.5)] += 6       # "Heckler & Koch" panel
    for k in range(2):
        col[lower & left & (np.abs(H - (209.0 - k * 5.0)) < 0.9) & (L > 268.0) & (L < 304.0)
            & (np.mod(L, 3.1) < 2.0)] += 22
    # grip: the diagonal checkering panel of the photo
    u = (L - 0.5 * (H - 60.0)) - 360.0                       # along the grip's rake
    panel = grip & (H > 72.0) & (H < 146.0) & (u > 4.0) & (u < 40.0)
    chk = panel & (np.mod(L + H * 0.9, 2.6) < 1.1)
    col[chk] *= 0.62
    col[panel & ~chk] += 8
    # rails: crossbar faces slightly lighter, the bore, the muzzle threads
    rail = mat == MATS.index("rail")
    col[rail & (n[..., 2] > 0.7)] += 8
    metal = mat == MATS.index("metal")
    r = np.hypot(x, z - (BORE - H0))
    col[metal & (r < 4.6) & (L < 1.0)] = 6
    col[metal & (L > 1.0) & (L < 16.0) & (np.mod(L, 1.4) < 0.5)] *= 0.6


def text_mask(u, v, text, u0, v0, height):
    return kit.text_mask(u, v, text, u0, v0, height)


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    if kind in ("UMP9", "UMP45"):
        paint_gun(maps, kind, col)
    elif kind == "stock":
        L, H = HINGE_L - y, z + BORE
        poly = (mat == MATS.index("polymer")) & side
        face = poly & (np.abs(x) > W_STOCK - 0.8)
        block = poly & (np.abs(x) > W_STOCK_FRONT - 0.8)
        # the release button's ribs on the front block (both sides), the hinge line
        col[block & (L > 452) & (L < 468) & (H > 188) & (H < 214) & (np.mod(L, 3.0) < 1.2)] *= 0.55
        col[block & rounded_rect(L, H, 441.0, 451.0, 190.0, 212.0, 2.0)] = 12
        # the moulded rib along the struts (the photo's raised edge)
        col[face & (L > 480) & (L < 655) & (np.abs(H - (226.6 - 4.0)) < 0.7)] *= 0.6
        col[face & (L > 480) & (L < 655) & (np.abs(H - (185.3 - (L - 476.4) * 0.3686 + 4.0)) < 0.7)] *= 0.6
        for cL, cH, rr in ((503.0, 198.0, 4.2), (660.0, 133.0, 3.6)):
            d = np.hypot(L - cL, H - cH)
            col[face & (d < rr)] = 10
            col[face & (d >= rr) & (d < rr + 1.0)] += 14
    elif kind in MAGS:
        rounds, length, w, d, mkind = MAGS[kind]
        s, u = mag_local(y, z, length, mkind)
        body = side & (np.abs(x) > w - 0.6)
        back = length - s                                  # distance up from the base
        if kind.startswith("45"):
            # smoked translucent body: the rounds inside show as a darker brass column, lighter at the stack's top
            sm = (mat == MATS.index("smoke")) & body & (s > 8.0) & (back > BASE_T + 2.0)
            stack = sm & (np.abs(u + 2.0) < d - 5.0)
            col[stack] = col[stack] * 0.7 + np.array([34, 26, 12])
            for k in range(int(length // 11.5) + 1):        # case heads of the staggered rounds
                col[stack & (np.abs(s - (12.0 + k * 11.5)) < 0.6)] *= 0.7
            col[sm & (np.abs(np.abs(u + 2.0) - (d - 5.0)) < 0.8)] *= 0.75
            for face, uu in ((body & left, -u), (body & right, u)):
                col[face & text_mask(uu, back, str(rounds), -6.0, BASE_T + 8.0, 5.0)] += 40
                col[face & text_mask(uu, back, ".45 ACP", -14.0, BASE_T + 16.0, 3.0)] += 30
        else:
            # black polymer, the photo's moulded lines; the calibre near the base, upside down as photographed
            pm = (mat == MATS.index("magpoly")) & body
            for face, uu in ((pm & left, -u), (pm & right, u)):
                col[face & text_mask(uu, back, "9X19", -8.0, BASE_T + 8.0, 4.0)] += 30
                col[face & text_mask(uu, back, "30", -6.0, BASE_T + 16.0, 5.0)] += 34
            col[pm & (np.abs(u - (d - 8.0)) < 0.8) & (s > 55) & (back > 30)] *= 0.7
            col[pm & (np.abs(u + (d - 8.0)) < 0.8) & (s > 55) & (back > 30)] *= 0.7
        # the light grey steel band the magazine catch bears on, and the base plate's grey edge
        col[side & (s > 42.0) & (s < 51.0)] = col[side & (s > 42.0) & (s < 51.0)] * 0.4 + 70
        col[(mat == MATS.index("magpoly")) & (back < BASE_T + 0.5) & side] += 22
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def texture(maps_list, kinds, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for maps, kind in zip(maps_list, kinds):
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


def bake(ob, ctx, size):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    maps = kit.bake_maps(ob, ctx, bake_size)
    if kit.DEBUG:
        kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
    return maps


# ==================================================================================================
# Attachment points (GoM's rifle set at the relations GoM's MP5 and our MP7 / SCARs use)
# ==================================================================================================

def gp(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4) + 0.0, round(y * K, 4) + 0.0, round(z * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    rail_top = (RAIL_CROSS - H0) * K
    side = (W_HG + 3.5) * K                              # the side rails' crossbar faces (picatinny(): 1.5 + 3.0 - 1)
    sy = round(P(sum(SIDE_RAIL) / 2, 0)[0] * K, 4)
    sz = round((SIDE_RAIL_H - H0) * K, 4)
    oy = round(P(OPTIC_L, 0)[0] * K, 4)
    bottom = (BOTTOM_TEETH - H0) * K
    stock = gp(HINGE_L, BORE)
    hinge_x = HINGE_X
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        # the barrel collar's front face, where a can screwed onto the threads stops (GoM's .45 mount device and P45
        # suppressor start here, as on its MAC-10, whose canon is 17 mm behind the muzzle)
        "canon": {"offset": gp(CANON_L, BORE), "rotate": ZERO},
        "magazine": {"offset": gp(*MAG_TOP), "rotate": ZERO},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up, and its scopes sit 0.0032 under that rail's
        # top (the MP7's and SCARs' relations, as on GoM's MP5)
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        "rail_left": {"offset": [round(side - 0.0055, 4), sy, sz], "rotate": ZERO},
        "rail_right": {"offset": [round(-(side - 0.0055), 4), sy, sz], "rotate": ZERO},
        "light_left": {"offset": [round(side - 0.0055 + 0.0062, 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), sy, round(sz - 0.0008, 4)], "rotate": ZERO},
        "rail_down": {"offset": [0.0, round(P(sum(BOTTOM_RAIL) / 2, 0)[0] * K, 4), round(bottom + 0.0055, 4)],
                      "rotate": ZERO},
        "foregrip": {"offset": [0.0, round(P(FOREGRIP_L, 0)[0] * K, 4), round(bottom + 0.003, 4)], "rotate": ZERO},
        "bolt_fired": {"offset": ZERO, "rotate": ZERO},
        "stock": {"offset": stock, "rotate": ZERO},
        # turned 180 degrees about the hinge pin: offset = stock + 2 x the pin's x
        "stock_folded": {"offset": [round(stock[0] + 2.0 * hinge_x * K, 4), stock[1], stock[2]],
                         "rotate": [0.0, 0.0, 180.0]},
        "world": {"offset": [0.02, 0.13, 0.0], "rotate": [180.0, 0.0, 180.0]},       # every GoM rifle
    }
    pts["_notes"] = {
        "units": "game units (0.72 of real size, GoM's MP5 family); +Y muzzle, +Z top, +X the gun's left; origin = "
                 "the rear-top of the pistol grip (photo L %.0f, H %.0f)" % (L0, H0),
        "magazine": "the UMP9's and UMP45's magazines hang from here (their feed lips), their rake built in",
        "stock": "UMP_STOCK (shared, in GunsOfTienPost93_UMP_parts.fbx) is modelled deployed with its origin at the "
                 "hinge: its front face on the bore axis",
        "stock_folded": "the same node turned 180 degrees about the hinge pin at x %.1f mm (the right side)" % hinge_x,
        "bolt_fired": "the charging handle does not reciprocate: the same place as bolt_lock",
        "canon": "the barrel collar's front face, %.1f mm behind the muzzle: GoM's .45 mount device and P45 suppressor "
                 "(UMP45 only)" % CANON_L,
    }
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE,
                      "real_mm_per_game_unit": round(1.0 / K, 2), "k": K}
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

    body, bolt = build_body(), build_bolt()
    stock = build_stock()
    mags = [build_magazine(name) for name in MAGS]
    kit.unwrap([body, bolt], 0.005)
    for o in [stock] + mags:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    gun_maps = [bake(body, [body, bolt], 256), bake(bolt, [body, bolt], 256)]
    for gun in ("UMP9", "UMP45"):
        texture(gun_maps, [gun, gun], 256, os.path.join(TEX_DIR, gun + ".png"))
    texture([bake(stock, [stock], 128)], ["stock"], 128, os.path.join(TEX_DIR, "UMP_STOCK.png"))
    for m in mags:
        texture([bake(m, [m], 128)], [m.name], 128, os.path.join(TEX_DIR, m.name + ".png"))

    bounds = {o.name: kit.bounds_of(o) for o in [body, bolt, stock] + mags}
    pts = points(bounds)
    bounds["UMP_STOCK_deployed"] = kit.bounds_at(stock, pts["stock"])
    bounds["UMP_STOCK_folded"] = kit.bounds_at(stock, pts["stock_folded"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    for name, b in bounds.items():
        print("UMP %-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    kit.export([body, bolt], FBX["gun"])
    kit.export(mags, FBX["mags"])
    kit.export([stock], FBX["parts"])


if __name__ == "__main__":
    main()
