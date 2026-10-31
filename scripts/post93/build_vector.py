"""KRISS Vector .45 and 9mm models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_vector.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_VECTOR.fbx       VECTOR_BODY, VECTOR_BOLT, VECTOR_HANDLE,
                                                                   VECTOR_RAIL_LEFT, VECTOR_RAIL_RIGHT (the .45),
                                                                   VECTOR9_* (the same turned: the 9mm is held
                                                                   like a pistol)
    P/models_X/weapons/parts/GunsOfTienPost93_VECTOR_parts.fbx    VECTOR_STOCK, VECTOR9_STOCK (turned)
    P/models_X/weapons/magazines/GunsOfTienPost93_VECTOR_magazines.fbx
        45Magazine13_VECTOR, 45Magazine30_VECTOR, 9x19Magazine17_VECTOR / 33_VECTOR / 40_VECTOR (on the Vectors),
        45Magazine30_GLOCK21 (on the main mod's Glock 21), 9x19Magazine33_GLOCK17 / _40 (on GoM's Glock 17)
    P/textures/weapons/GunsOfTienPost93/VECTOR45.png, VECTOR9.png  256 (body, bolt, handle, side rails: flat dark
                                                                   earth / sand); VECTOR45_STOCK.png, VECTOR9_STOCK.png
                                                                   128; VECTOR_<magazine>.png 128 each
    scripts/post93/vector_points.json                              attachment points (game space), the .45's
    scripts/post93/vector9_points.json                             the 9mm's (turned, held like a pistol)

The KRISS Vector SMG (Gen II; user, 2026-10-30): the .45 ACP gun (2006) and the 9mm (2011) on one body, as the UMPs,
the .45 in flat dark earth, the 9mm in sand; the .45 held as a rifle, the 9mm like a pistol (user, 2026-11-01:
VECTOR9_* below). Traced by hand on a millimetre grid from Wikimedia Commons "Kriss Vector
SMG Realistic.png" (Gasteiz, CC BY-SA 3.0; references/vector): a straight left-side drawing of a Vector SMG with a
suppressor, an EOTech, a vertical grip and KRISS's 30-round .45 magazine, scaled by its top rail's crossbars (1.95 px
per 10 mm pitch: 566 mm from the receiver's front to the butt, stock out, against KRISS's 610). Profiles are in that
drawing's (L, H) mm: L back from the receiver's front face (the barrel's threaded end stands 13 mm ahead of it), H up
from the frame's lowest point. Checked against the real Gen II carbine of "Kriss Vector left.JPG" (Michael E.
Cumpston, CC BY-SA 4.0).

The gun: the upper shroud (a full-length top rail), the front block under it (the bore, the short bottom rail, the
non-reciprocating charging handle on the left), the "Super V" housing angled down behind it (the magazine well at its
front, the drawing's V), the trigger window, the grip and the loop that closes the hand's opening under it, the
side-folding stock (it folds forward along the right side about its hinge, the UMPs' way). Side rails are KRISS's
bolt-on kit (Gen II, 3 and 9 o'clock): GoM's optional Picatinny_Rail_Left / _Right drawn with our short VECTOR_RAIL_*.
The flip-up sights are drawn folded. Magazines are Glock's: the Vector .45 takes the Glock 21's 13 (the main mod's)
and KRISS's 30-round MagEx2, the Vector 9mm GoM's Glock 17 17-round, Glock's 33 and KRISS's 40-round MagEx2. On the
Vectors they hang from `magazine` (their feed lips), their rake built in (the well leans 0.342, as the Glock 21's grip);
the 30 is also drawn on the Glock 21 and the 33 / 40 on GoM's Glock 17, as copies of those pistols' own magazine meshes
stretched below a cut (their textures and the hand's Bip01_Prop2 point kept).
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402

MEDIA = kit.MEDIA
TEX_DIR = kit.TEX_DIR
MAIN_MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
FBX = {
    "gun": os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_VECTOR.fbx"),
    "mags": os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_VECTOR_magazines.fbx"),
    "parts": os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_VECTOR_parts.fbx"),
}
POINTS_JSON = os.path.join(HERE, "vector_points.json")
POINTS9_JSON = os.path.join(HERE, "vector9_points.json")

K = 0.000603                       # game units per real mm: the M16A2's proportion (every Guns of Tien gun)
K_OLD = 0.00072                    # GoM's rifles: the `world` floor point is scaled from them
K_GOM = 0.00072                    # GoM's pistols are drawn at 0.72 of real size
kit.K = K
MATS = ["polymer", "grip", "rail", "metal", "dark", "tan", "rubber", "magpoly", "brass", "copper"]
kit.MATS[:] = MATS

# Photo frame: the origin is the rear-top of the pistol grip (its back edge meets the receiver), the bore axis H.
L0, H0 = 328.0, 132.0
BORE = 115.5                       # the suppressor's axis in the drawing
MUZZLE_L = -13.0                   # the threaded barrel's end, ahead of the receiver's front face
CANON_L = -1.0                     # the receiver's front face: a can or mount device screwed on stops here
SEAM = 132.0                       # the upper shroud over the front block and the housing
TOP = 166.0                        # the shroud's top (the rail's mounting face)
RAIL_TOP = (4.0, 302.0)            # the top rail, L
RAIL_BASE, RAIL_TEETH = 3.0, 3.5   # kit.picatinny(): crossbar tops at TOP + 3.0 + 3.5 - 1 = 171.5 (the drawing's)
FRONT_BOTTOM = 100.5               # the front block's underside (the bottom rail hangs under it)
BOTTOM_RAIL = (10.0, 82.0)
BOTTOM_TEETH = 93.0                # the bottom rail's crossbar faces
SIDE_RAIL = (24.0, 86.0)           # KRISS's side rail kit (our short model), on the front block's faces
SIDE_RAIL_H = 116.0
OPTIC_L, FOREGRIP_L = 150.0, 48.0
HANDLE = (18.0, 82.0, 130.5, 140.0)            # the charging handle's grip (left), L / H
HANDLE_TRAVEL = 55.0
PORT = (108.0, 150.0, 135.0, 152.0)            # the ejection port on the right of the shroud, L / H
PORT_SPLIT = (PORT[0] + PORT[1]) / 2.0
CARRIER_TRAVEL = PORT_SPLIT - PORT[0] - 0.5
HINGE_L = 341.0                    # the receiver's rear face = the stock's front face
W_UPPER, W_FRONT, W_HOUSING, W_GRIP, W_GUARD, W_LOOP = 22.0, 22.0, 23.5, 15.0, 8.0, 9.0      # half widths, mm
W_STOCK, W_STOCK_FRONT = 11.0, 16.0
HINGE_X = -(W_HOUSING + 1.0 + W_STOCK_FRONT) / 2.0   # the hinge pin (right, -X): folded, the stock lies 1 mm off the housing
# The magazine well: its front edge runs L = 132 + 0.342 (8 - H) (the drawing's 30-round), 37 mm deep (Glock 21)
MAG_RAKE = math.atan(0.342)        # radians from vertical, the base toward the butt
MAG_LIPS = (119.5, 100.0)          # the .45 magazines' feed lips (top centre), photo L / H
SIDE_BASE, SIDE_TEETH = 1.5, 3.0


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
# Profiles (photo L, H mm), read on the drawing's millimetre grid
# ==================================================================================================

UPPER = [(0.5, SEAM), (0.5, 162.5), (3.5, TOP), (326.0, TOP), (334.0, 163.5), (340.0, 156.0), (HINGE_L, 140.0),
         (337.0, 133.0), (330.0, SEAM)]
FRONT = [(0.5, FRONT_BOTTOM + 1.0), (2.0, FRONT_BOTTOM), (102.0, FRONT_BOTTOM), (102.0, SEAM + 0.5), (0.5, SEAM + 0.5)]
# the Super V housing: down from the front block, the magazine well's mouth at its foot, back along its underside to
# the loop, up its slanted rear edge (the hand's opening behind it) to the trigger window
HOUSING = [(100.0, SEAM + 0.5), (100.0, FRONT_BOTTOM), (104.0, 92.0), (121.0, 22.0), (122.5, 15.0), (127.0, 9.0),
           (133.0, 7.0), (246.0, 5.0), (250.0, 9.0), (246.0, 35.0), (226.5, 93.0), (222.0, 98.0), (219.0, 104.0),
           (217.0, SEAM + 0.5)]
# the hand's opening: its front edge the housing's rear (226.5, 93) - (245, 35), a V-shaped floor down to (271, 20)
# (the loop), its back edge the grip's front (273, 95) - (299, 37); the slanted bar over it under the trigger window
LOOP = [(247.0, 5.0), (273.0, 11.0), (308.0, 25.0), (326.0, 32.0), (318.0, 37.0), (300.0, 34.5), (271.0, 20.0),
        (245.0, 35.0), (242.0, 20.0)]
GUARD = [(220.0, 92.8), (274.0, 94.6), (268.0, 104.5), (222.0, 97.5)]
# the grip: its back hollowed for the thumb's web at the top (L 315.5 at H 118), a lip at the foot
GRIP = [(266.0, SEAM + 0.5), (266.0, 104.0), (273.0, 95.0), (299.0, 37.0), (303.0, 33.0), (338.0, 33.0),
        (341.0, 38.0), (341.0, 48.0), (339.5, 55.0), (336.0, 69.0), (331.5, 83.0), (326.0, 94.0), (321.0, 104.0),
        (316.5, 113.0), (315.5, 118.0), (317.5, 124.0), (322.0, 129.0), (328.0, SEAM + 0.5)]
TRIGGER = [(254.0, SEAM), (260.0, SEAM), (262.0, 124.0), (266.0, 116.0), (267.5, 109.0), (265.5, 106.5),
           (262.5, 108.0), (259.5, 114.0), (256.5, 121.0), (254.0, 127.0)]
SELECTOR = [(268.0, 146.0), (270.0, 151.0), (284.0, 156.0), (292.0, 152.0), (290.0, 147.0), (276.0, 142.0)]
SELECTOR_PIVOT = (276.0, 148.0)
BOLT_RELEASE = [(107.0, 113.0), (116.0, 113.0), (116.0, 127.0), (107.0, 127.0)]     # tan, left
FRONT_SIGHT = [(27.0, TOP - 0.5), (27.0, 172.0), (30.0, 175.0), (50.0, 175.0), (52.0, 172.0), (52.0, TOP - 0.5)]
REAR_SIGHT = [(278.0, TOP - 0.5), (278.0, 174.0), (281.0, 178.0), (299.0, 178.0), (301.0, 174.0), (301.0, TOP - 0.5)]

# The stock, deployed as drawn: the arm back from the hinge, the strut down to the foot, the frame's upper and lower
# members back to the butt plate (open between them), the butt plate on two posts.
STOCK = [(HINGE_L - 3.0, 162.0), (352.0, 162.0), (362.0, 156.0), (372.0, 149.0), (474.0, 148.4), (480.0, 142.0),
         (487.0, 119.0), (523.0, 119.0), (523.0, 92.0), (503.0, 89.0), (500.0, 84.0), (513.0, 45.0), (523.0, 44.0),
         (523.0, 0.0), (511.0, 1.0), (498.5, 10.0), (495.0, 16.0), (488.8, 37.0), (485.6, 48.0), (476.0, 74.0),
         (469.6, 93.0), (460.0, 115.5), (450.0, 127.5), (372.0, 127.5), (355.0, 133.0), (HINGE_L - 3.0, 133.0)]
BUTT = (529.5, 565.0, -5.0, 122.0)
BUTT_POSTS = ((99.5, 113.0), (25.0, 38.0))      # H, between the frame (L 523) and the butt plate


# ==================================================================================================
# Geometry
# ==================================================================================================

def picatinny(b, La, Lb, frame, **kw):
    ya, yb = sorted((L0 - La, L0 - Lb))
    kit.picatinny(b, ya, yb, frame, **kw)


def build_body():
    b = kit.Builder()
    slab(b, UPPER, half=W_UPPER, bevel=1.8, res=1)
    slab(b, FRONT, half=W_FRONT, bevel=1.8, res=1)
    slab(b, HOUSING, half=W_HOUSING, bevel=2.4, res=1)
    slab(b, LOOP, half=W_LOOP, bevel=2.0, res=1)
    slab(b, GUARD, half=W_GUARD, bevel=1.4, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=4.0, res=1, mat="grip")
    slab(b, TRIGGER, half=3.0, bevel=0.6, mat="dark")
    slab(b, FRONT_SIGHT, half=8.0, bevel=1.0, mat="dark")
    slab(b, REAR_SIGHT, half=10.0, bevel=1.2, mat="dark")
    slab(b, SELECTOR, half=1.0, bevel=0.4, mat="dark", x0=W_UPPER + 0.8)                 # left side
    cl, ch = SELECTOR_PIVOT
    y, z = P(cl, ch)
    b.lathe("x", (0, y, z), [(W_UPPER - 0.5, 0), (W_UPPER - 0.5, 5.0), (W_UPPER + 2.0, 5.0),
                             (W_UPPER + 2.6, 3.8), (W_UPPER + 2.6, 0)], seg=12, mat="dark")
    slab(b, BOLT_RELEASE, half=1.2, bevel=0.5, mat="tan", x0=W_HOUSING + 0.8)             # left side
    # the top rail on the shroud, the bottom rail under the front block (both moulded in)
    picatinny(b, RAIL_TOP[1], RAIL_TOP[0], lambda u, h, yy: Vector((u, yy, TOP - H0 + h)),
              base_h=RAIL_BASE, tooth_h=RAIL_TEETH, mat="rail")
    picatinny(b, BOTTOM_RAIL[1], BOTTOM_RAIL[0], lambda u, h, yy: Vector((u, yy, FRONT_BOTTOM - H0 - h)),
              base_h=3.0, tooth_h=FRONT_BOTTOM - BOTTOM_TEETH - 3.0 + 1.0, mat="rail")
    # the barrel's threaded end out of the front face
    b.lathe("y", (0, 0, BORE - H0), [(P(6.0, 0)[0], 0), (P(6.0, 0)[0], 8.2), (P(0.0, 0)[0], 8.2),
                                     (P(0.0, 0)[0], 7.2), (P(MUZZLE_L + 0.8, 0)[0], 7.2),
                                     (P(MUZZLE_L, 0)[0], 6.4), (P(MUZZLE_L, 0)[0], 0)], seg=16, mat="metal",
            phase=0.5)
    return b.to_object("VECTOR_BODY")


def build_carrier():
    """The bolt's side in the ejection port's front half (bolt_lock); bolt_fired slides it back over the rear half."""
    b = kit.Builder()
    box(b, PORT[0] + 0.5, PORT_SPLIT - 0.2, PORT[2] + 0.5, PORT[3] - 0.5, -(W_UPPER + 0.35), -(W_UPPER - 0.4),
        mat="metal", bevel=0.1)
    return b.to_object("VECTOR_BOLT")


def build_handle():
    """The charging handle on the left of the shroud's front (it does not reciprocate); handle_back while racked."""
    b = kit.Builder()
    La, Lb, Ha, Hb = HANDLE
    box(b, La, Lb, Ha, Hb, W_UPPER - 2.0, W_UPPER + 3.0, mat="tan", bevel=0.8)
    box(b, Lb - 14.0, Lb, Ha - 1.0, Hb + 1.0, W_UPPER + 3.0, W_UPPER + 9.0, mat="tan", bevel=1.8)       # the knob
    return b.to_object("VECTOR_HANDLE")


def build_side_rail(name, sign):
    """KRISS's side rail (Gen II kit) for GoM's optional Picatinny_Rail_Left / _Right: origin on the front block's face
    (rail_left / rail_right), standing out along sign * X, two screws through its end pads."""
    b = kit.Builder()
    half = (SIDE_RAIL[1] - SIDE_RAIL[0]) / 2.0
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((sign * h, yy, u)), base_h=SIDE_BASE, tooth_h=SIDE_TEETH,
                  mat="dark")
    for yy in (-half + 3.0, half - 3.0):
        b.lathe("x", (0, yy, 0), [(0.0, 0), (0.0, 2.2), (sign * 2.8, 2.2), (sign * 3.2, 1.6), (sign * 3.2, 0)],
                seg=8, mat="metal")
    return b.to_object(name)


def build_stock():
    """Origin = the hinge: the stock's front face on the bore axis; modelled deployed, extending along -Y."""
    b = kit.Builder()
    q = lambda pts: [(HINGE_L - L, H - BORE) for L, H in pts]
    kit.slab(b, q(STOCK), [], W_STOCK, 2.4, 1, "polymer", 0.0)
    kit.slab(b, q([(HINGE_L - 3.0, 133.0), (HINGE_L - 3.0, 162.0), (356.0, 162.0), (356.0, 133.0)]), [],
             W_STOCK_FRONT, 2.0, 1, "polymer", 0.0)
    La, Lb, Ha, Hb = BUTT
    b.box(-W_STOCK - 2.0, W_STOCK + 2.0, HINGE_L - Lb, HINGE_L - La, Ha - BORE, Hb - BORE, mat="rubber", bevel=2.5)
    for h0, h1 in BUTT_POSTS:
        b.box(-W_STOCK + 3.0, W_STOCK - 3.0, HINGE_L - La - 1.0, HINGE_L - 521.0, h0 - BORE, h1 - BORE, mat="dark",
              bevel=1.0)
    # the hinge knuckles on the receiver's right rear corner, round the pin (they stay put when it folds)
    for h0, h1 in ((136.0, 146.0), (150.0, 160.0)):
        b.lathe("z", (HINGE_X, 0.0, 0.0), [(h0 - BORE, 0), (h0 - BORE, 4.5), (h1 - BORE, 4.5), (h1 - BORE, 0)],
                seg=12, mat="metal")
    return b.to_object("VECTOR_STOCK")


# The Vectors' magazines, built like the UMPs': a swept double-stack body, origin at the feed lips (top centre),
# raked as the well. name: (rounds, lips to base, half width, half depth, front-edge shift, calibre, extended from)
MAGS = {
    "45Magazine13_VECTOR": (13, 118.0, 12.3, 18.5, 0.0, "45", None),       # the Glock 21's (main mod)
    "45Magazine30_VECTOR": (30, 220.0, 12.3, 18.5, 0.0, "45", 105.0),      # KRISS MagEx2 on it (+17)
    "9x19Magazine17_VECTOR": (17, 128.0, 11.2, 16.0, -2.5, "9", None),     # GoM's Glock 17's
    "9x19Magazine33_VECTOR": (33, 226.0, 11.2, 16.0, -2.5, "9", None),     # Glock's 33
    "9x19Magazine40_VECTOR": (40, 268.0, 11.2, 16.0, -2.5, "9", 115.0),    # KRISS MagEx2 on a Glock 17 (+23)
}
BASE_T = 6.0                       # base plate thickness
EXTRA_MM = {"45": 6.0, "9": 6.1}   # each extra round (double stack) adds this much


def mag_axis(s):
    a = MAG_RAKE
    return (-s * math.sin(a), -s * math.cos(a))           # y forward: down the axis the base moves toward the butt


def mag_local(y, z, shift):
    a = MAG_RAKE
    return -y * math.sin(a) - z * math.cos(a), y * math.cos(a) - z * math.sin(a) + shift


def sweep(b, s_list, w, d, c, mat, shift):
    bm = b.bm
    a = MAG_RAKE
    ny, nz = math.cos(a), -math.sin(a)                   # across the magazine, toward the muzzle
    rings = []
    for s in s_list:
        cy, cz = mag_axis(s)
        sec = [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]
        rings.append([bm.verts.new((x, cy + (u - shift) * ny, cz + (u - shift) * nz)) for x, u in sec])
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_magazine(name):
    rounds, length, w, d, shift, cal, ext = MAGS[name]
    b = kit.Builder()
    end = length - BASE_T
    steps = sorted({round(s, 3) for s in [4.0 + k * 8.0 for k in range(int((end - 4.0) // 8.0) + 1)] + [end]})
    sweep(b, steps, w, d, 1.8, "magpoly", shift)
    sweep(b, [0.0, 4.5], w - 2.5, d - 2.5, 1.5, "metal", shift)                    # steel-lined feed lips
    sweep(b, [end - 0.5, length], w + 1.2, d + 1.8, 2.2, "magpoly", shift)          # base plate
    if ext:                                                                          # KRISS's extension's collar
        sweep(b, [ext - 2.0, ext + 2.0], w + 0.8, d + 1.0, 1.8, "magpoly", shift)
    # the top round, bullet forward
    cy, cz = 2.0 - shift, -4.0
    if cal == "9":
        b.lathe("y", (0, cy, cz), [(-13.0, 0), (-13.0, 4.9), (6.0, 4.9), (6.5, 4.5)], seg=8, mat="brass")
        b.lathe("y", (0, cy, cz), [(6.5, 4.5), (11.0, 4.2), (14.5, 2.4), (15.7, 0)], seg=8, mat="copper")
    else:
        b.lathe("y", (0, cy, cz - 0.5), [(-15.0, 0), (-15.0, 6.0), (7.8, 6.0), (8.2, 5.6)], seg=8, mat="brass")
        b.lathe("y", (0, cy, cz - 0.5), [(8.2, 5.6), (12.0, 5.3), (16.0, 3.4), (17.4, 0)], seg=8, mat="copper")
    return b.to_object(name)


# ==================================================================================================
# Pistol copies: GoM's Glock 17 magazine and the main mod's Glock 21 magazine stretched below a cut
# ==================================================================================================

def stretch_copy(src, name, extra_units):
    """A copy of `src`'s mesh (FBX data space, the pistol modelled upside down: data z = up) with every vertex below
    the middle of its length moved down its long axis by extra_units, UVs kept (the texture stretches along it)."""
    me = src.data.copy()
    me.name = name
    co = np.array([v.co[:] for v in me.vertices])
    c = co.mean(axis=0)
    _, _, vt = np.linalg.svd(co - c)
    axis = vt[0] / np.linalg.norm(vt[0])
    if axis[2] < 0:                                        # pointing up, toward the feed lips
        axis = -axis
    s = (co - c) @ axis
    cut = (s.min() + s.max()) / 2.0
    low = s < cut
    co[low] -= axis * extra_units
    for v, p in zip(me.vertices, co):
        v.co = p
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, axis, cut


# ==================================================================================================
# Painting
# ==================================================================================================

COLOURS = {  # sRGB polymer of each gun: flat dark earth (the .45), sand (the 9mm; user, 2026-10-30)
    "VECTOR45": {"polymer": (116, 97, 70), "grip": (110, 92, 66)},
    "VECTOR9": {"polymer": (192, 176, 134), "grip": (184, 168, 127)},
}
BASE = {"polymer": (126, 108, 80), "grip": (120, 103, 77), "rail": (34, 34, 36), "metal": (54, 55, 58),
        "dark": (24, 24, 25), "tan": (150, 132, 100), "rubber": (30, 30, 31), "magpoly": (34, 34, 36),
        "brass": (150, 118, 62), "copper": (140, 82, 52)}
for ch, rows in {"K": ["101", "110", "100", "110", "101"], "V": ["101", "101", "101", "101", "010"],
                 "C": ["111", "100", "100", "100", "111"], "T": ["111", "010", "010", "010", "010"],
                 "O": ["111", "101", "101", "101", "111"], "U": ["101", "101", "101", "101", "111"],
                 "L": ["100", "100", "100", "100", "111"], "B": ["110", "101", "110", "101", "110"],
                 "5": ["111", "100", "111", "001", "111"], "9": ["111", "101", "111", "001", "111"],
                 "H": ["101", "101", "111", "101", "101"]}.items():
    kit.FONT.setdefault(ch, rows)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def near_line(L, H, pts, w):
    m = np.zeros(L.shape, bool)
    for (la, ha), (lb, hb) in zip(pts, pts[1:]):
        dl, dh = lb - la, hb - ha
        t = np.clip(((L - la) * dl + (H - ha) * dh) / max(dl * dl + dh * dh, 1e-9), 0, 1)
        m |= np.hypot(L - (la + t * dl), H - (ha + t * dh)) < w
    return m


def pin(col, L, H, sel, cL, cH, r=2.6):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.9)] *= 0.4
    col[sel & (d <= r - 0.9)] = col[sel & (d <= r - 0.9)] * 0.5 + 18


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "rail", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.93 + 0.14 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.98 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 70.0, 40.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None]
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint_gun(maps, gun, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    poly = mat == MATS.index("polymer")
    shroud = poly & side & (np.abs(x) > W_UPPER - 0.6) & (H > SEAM - 1.0)
    front = poly & side & (np.abs(x) > W_FRONT - 0.6) & (H < SEAM + 1.0) & (L < 101.0)
    housing = poly & side & (np.abs(x) > W_HOUSING - 0.6)
    body = shroud | front | housing
    # seams: shroud / lower, the front block / housing
    col[body & (np.abs(H - SEAM) < 0.7) & (L > 1) & (L < HINGE_L - 1)] *= 0.55
    # the charging handle's channel (left), the ejection port (right) with the bolt's side in its rear half
    col[shroud & left & rounded_rect(L, H, HANDLE[0] - 2.0, HANDLE[1] + HANDLE_TRAVEL + 2.0, 131.5, 139.0, 2.0)] = 12
    port = shroud & right & rounded_rect(L, H, *PORT, 2.5)
    chamber = port & (L < PORT_SPLIT)
    col[chamber] = col[chamber] * 0.2 + 10
    carrier = port & ~chamber
    col[carrier] = np.array(BASE["metal"]) * 1.45
    col[carrier & (L < PORT_SPLIT + 0.8)] *= 0.5
    # the drawing's slot on the shroud's left, the housing's big V and its outline panel
    col[shroud & left & rounded_rect(L, H, 62.0, 95.0, 155.0, 162.0, 3.0)] *= 0.35
    col[housing & near_line(L, H, [(150.0, 117.0), (176.0, 88.0), (210.0, 117.0)], 1.0)] *= 0.6
    col[housing & near_line(L, H, [(118.0, 96.0), (128.0, 55.0), (148.0, 30.0)], 0.9)] *= 0.65
    col[housing & near_line(L, H, [(212.0, 120.0), (232.0, 40.0), (238.0, 20.0)], 0.9)] *= 0.65
    # pins and screws (the drawing's)
    for cL, cH, sel in ((20.0, 113.0, front), (68.0, 113.0, front), (69.0, 150.0, shroud), (107.0, 152.0, shroud),
                        (140.0, 112.0, housing), (155.0, 72.0, housing), (172.0, 37.0, housing),
                        (188.0, 18.0, housing), (233.0, 15.0, housing), (196.0, 150.0, shroud)):
        pin(col, L, H, sel, cL, cH)
    # markings: "KRISS" and "VECTOR" on the shroud's left (left side u = +L), the calibre on the right (u = -L)
    col[shroud & left & kit.text_mask(L, H, "KRISS", 200.0, 151.0, 5.0)] += 34
    col[shroud & left & kit.text_mask(L, H, "VECTOR", 228.0, 151.0, 5.0)] += 34
    cal = ".45 ACP" if gun == "VECTOR45" else "9MM"
    col[shroud & right & kit.text_mask(-L, H, cal, -240.0, 146.0, 4.0)] += 30
    # safe / fire marks by the selector (left)
    col[shroud & left & (np.hypot(L - 290.0, H - 160.0) < 1.6)] = (205, 205, 200)
    col[shroud & left & (np.hypot(L - 296.0, H - 145.0) < 1.6)] = (186, 46, 40)
    # the grip's textured panel
    grip = (mat == MATS.index("grip")) & side & (np.abs(x) > W_GRIP - 0.8)
    panel = (grip & (H > 41.0) & (H < 113.0) & (L > 305.0 + 0.07 * (113.0 - H)) & (L < 319.0 + 0.25 * (113.0 - H)))
    chk = panel & (kit.vnoise(p, 0.6, 31) > 0.5)
    col[chk] += 10
    col[panel & ~chk] *= 0.8
    # rails: crossbar faces a little lighter; the bore
    rail = mat == MATS.index("rail")
    col[rail & (n[..., 2] > 0.7)] += 8
    metal = mat == MATS.index("metal")
    r = np.hypot(x, z - (BORE - H0))
    col[metal & (r < (5.8 if gun == "VECTOR45" else 4.6)) & (L < MUZZLE_L + 1.0)] = 6
    col[metal & (L > MUZZLE_L + 1.0) & (L < -1.0) & (np.mod(L, 1.4) < 0.5)] *= 0.6        # threads


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    gun = kind.split(":")[0]
    base = dict(BASE, **COLOURS.get(gun, {}))
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = base[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    part = kind.split(":")[1] if ":" in kind else "gun"
    if part == "gun":
        paint_gun(maps, gun, col)
    elif part == "carrier":
        L, H = L0 - y, z + H0
        face = right & (np.abs(x) > W_UPPER + 0.2)
        col[face & ((np.abs(H - 140.0) < 0.5) | (np.abs(H - 146.0) < 0.5))] *= 0.6
        col[face & (L < PORT[0] + 2.0)] *= 0.55
    elif part == "handle":
        col[side & (np.mod(y, 1.6) < 0.6) & (np.abs(x) > W_UPPER + 8.5)] *= 0.6               # the knob's grooves
    elif part == "stock":
        L, H = HINGE_L - y, z + BORE
        face = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_STOCK - 0.8)
        col[face & near_line(L, H, [(372.0, 145.0), (466.0, 145.0)], 0.7)] *= 0.6
        col[face & near_line(L, H, [(372.0, 131.0), (444.0, 131.0)], 0.7)] *= 0.6
        for cL, cH in ((345.0, 147.0), (517.0, 106.0), (517.0, 31.5)):
            d = np.hypot(L - cL, H - cH)
            col[face & (d < 4.0)] = 14
            col[face & (d >= 4.0) & (d < 5.0)] += 14
        rub = mat == MATS.index("rubber")
        col[rub & side & (np.mod(H, 9.0) < 1.2)] *= 0.6
    elif part in MAGS:
        rounds, length, w, d, shift, cal, ext = MAGS[part]
        s, u = mag_local(y, z, shift)
        mp = mat == MATS.index("magpoly")
        body = mp & side & (np.abs(x) > w - 0.6)
        back = length - s
        # Glock's witness holes down the back (numbered every few rounds), the calibre near the base
        bk = mp & (n[..., 1] < -0.5) & (s > 12.0) & (back > BASE_T + 6.0)
        step = 22.0 if cal == "45" else 18.0
        for k in range(int((length - 24.0) // step)):
            col[bk & (np.hypot(x, s - (14.0 + k * step)) < 1.4)] = 12
        for face, uu in ((body & left, -u), (body & right, u)):
            col[face & kit.text_mask(uu, back, str(rounds), -6.0, BASE_T + 8.0, 5.0)] += 40
            col[face & kit.text_mask(uu, back, ".45" if cal == "45" else "9MM", -8.0, BASE_T + 16.0, 3.4)] += 30
        if ext:
            col[mp & side & (s > ext - 2.0) & (s < ext + 2.0)] += 10                         # the extension's collar
        col[mp & (back < BASE_T + 0.5) & side] += 18
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
# Attachment points (GoM's rifle set at the relations our UMPs and SCARs use)
# ==================================================================================================

def gp(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4) + 0.0, round(y * K, 4) + 0.0, round(z * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    rail_top = (TOP + RAIL_BASE + RAIL_TEETH - 1.0 - H0) * K
    face = (W_FRONT + SIDE_BASE + SIDE_TEETH - 1.0) * K       # the side rails' crossbar faces
    sy = round(P(sum(SIDE_RAIL) / 2.0, 0)[0] * K, 4)
    sz = round((SIDE_RAIL_H - H0) * K, 4)
    oy = round(P(OPTIC_L, 0)[0] * K, 4)
    bottom = (BOTTOM_TEETH - H0) * K
    stock = gp(HINGE_L, BORE)
    pts = {
        "muzzle": {"offset": gp(MUZZLE_L, BORE), "rotate": [-90.0, 0.0, -180.0]},
        # the receiver's front face, where a can screwed onto the threads stops: GoM's .45 mount device and P45
        # (the Vector .45, as the UMP45), the main mod's 9x19mm SMG mount device and Mk9 (the Vector 9mm, as the UMP9)
        "canon": {"offset": gp(CANON_L, BORE), "rotate": ZERO},
        "magazine": {"offset": gp(*MAG_LIPS), "rotate": ZERO},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up and its scopes sit 0.0032 under the rail's top
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        # the bottom rail moulded in: GoM's foregrips 0.003 above its crossbar faces
        "rail_down": {"offset": [0.0, round(P(sum(BOTTOM_RAIL) / 2.0, 0)[0] * K, 4), round(bottom + 0.0055, 4)],
                      "rotate": ZERO},
        "foregrip": {"offset": [0.0, round(P(FOREGRIP_L, 0)[0] * K, 4), round(bottom + 0.003, 4)], "rotate": ZERO},
        # KRISS's side rails (our VECTOR_RAIL_LEFT / _RIGHT, origins on the front block's faces); GoM's lights 0.0007
        # out from the crossbar faces, its lasers 0.0018 out and 0.0008 lower (the AUG A1's relations)
        "rail_left": {"offset": [round(W_FRONT * K, 4), sy, sz], "rotate": ZERO},
        "light_left": {"offset": [round(face + 0.0007, 4), sy, sz], "rotate": ZERO},
        "rail_right": {"offset": [round(-W_FRONT * K, 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(face + 0.0018), 4), sy, round(sz - 0.0008, 4)], "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-HANDLE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "stock": {"offset": stock, "rotate": ZERO},
        # turned 180 degrees about the hinge pin: offset = stock + 2 x the pin's x
        "stock_folded": {"offset": [round(stock[0] + 2.0 * HINGE_X * K, 4), stock[1], stock[2]],
                         "rotate": [0.0, 0.0, 180.0]},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},                               # every GoM rifle's, scaled
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the rear-top of the "
                 "pistol grip (the drawing's L %.0f, H %.0f)" % (L0, H0),
        "magazine": "45Magazine13_VECTOR / 30 and 9x19Magazine17_VECTOR / 33 / 40 hang from here (the .45's feed lips; "
                    "the 9mm ones 2.5 mm forward so their front edge meets the well's), their rake built in",
        "stock": "VECTOR_STOCK (GunsOfTienPost93_VECTOR_parts.fbx) modelled deployed, origin at the hinge: its front "
                 "face on the bore axis",
        "stock_folded": "the same node turned 180 degrees about the hinge pin at x %.1f mm (the right side)" % HINGE_X,
        "bolt_fired": "VECTOR_BOLT back %.1f mm real: each shot and held open when empty (GoM's Bolt_Fired)"
                      % CARRIER_TRAVEL,
        "handle_back": "VECTOR_HANDLE (the charging handle, left) back %.0f mm real, only while racked; KRISS's handle "
                       "does not reciprocate" % HANDLE_TRAVEL,
        "rails": "integral top (L %.0f-%.0f) and bottom (L %.0f-%.0f) rails; GoM's optional Picatinny_Rail_Left / "
                 "_Right drawn as VECTOR_RAIL_LEFT / _RIGHT (L %.0f-%.0f, H %.0f)" % (
                     RAIL_TOP + BOTTOM_RAIL + SIDE_RAIL + (SIDE_RAIL_H,)),
    }
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE,
                      "real_mm_per_game_unit": round(1.0 / K, 2), "k": K}
    pts["_bounds"] = bounds
    return pts


# The Vector 9mm is held like a pistol (user, 2026-11-01), GoM's MP5K way (Post-93's MP7s and P90 too): its model is
# the .45's turned 180 degrees about the bore axis (game x -> -x, z -> -z), the nodes of its own files turned with it
# (VECTOR9_*: copies of the .45's, the same UVs), so their points keep their rotates (a half turn about Z commutes
# with the turn about Y: the folded stock's stays); parts modelled upright get TURN (the magazines, GoM's optics,
# foregrips, lights and lasers), as on the MP7 and the Mini Uzi.
UPRIGHT_PARTS = ("magazine", "rail_up", "scope", "rail_down", "foregrip", "light_left", "laser_right")


def turned_copy(ob, name):
    me = ob.data.copy()
    me.name = name
    me.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))         # FBX data space: x and data z negated alike
    copy = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(copy)
    return copy


def handgun_points(pts, bounds):
    out = {}
    for name, p in pts.items():
        if name.startswith("_") or name == "world":
            continue
        x, y, z = p["offset"]
        out[name] = {"offset": [round(-x, 4) + 0.0, y, round(-z, 4) + 0.0],
                     "rotate": list(kit.TURN) if name in UPRIGHT_PARTS else list(p["rotate"])}
    # GoM's handgun-held SMGs' floor pose (MP5K, TEC9, MAC10), scaled; on the back like a rifle (never holstered), so
    # the rifle points turn it upright there (build_mp7.py's handgun_points)
    out["world"] = {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}
    for name in ("rifle_back", "rifle_back_bag"):
        out[name] = {"offset": [0.0, 0.0, 0.0], "rotate": list(kit.TURN)}
    out["_notes"] = {
        "units": "game units (0.603 of real size); held like a pistol, so modelled upside down as GoM's MP5K: +Y "
                 "muzzle, +Z the gun's BOTTOM, +X its RIGHT; origin = the rear-top of the pistol grip (the drawing's "
                 "L %.0f, H %.0f)" % (L0, H0),
        "nodes": "VECTOR9_BODY / _BOLT / _HANDLE / _RAIL_LEFT / _RAIL_RIGHT (GunsOfTienPost93_VECTOR.fbx) and "
                 "VECTOR9_STOCK (the parts file): the .45's nodes turned, drawn at these points with their own rotates",
        "turned": "parts modelled upright (magazines, GoM's optics / foregrips / lights / lasers) get rotate -180 0 -180",
        "rifle_back": "rifle_back / rifle_back_bag (vanilla's Rifle On Back locations) turn the upside-down model "
                      "upright when it hangs in the back slot",
    }
    out["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "bore_mm": BORE,
                      "real_mm_per_game_unit": round(1.0 / K, 2), "k": K}
    out["_bounds"] = bounds
    return out


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

    body, bolt, handle = build_body(), build_carrier(), build_handle()
    rails = [build_side_rail("VECTOR_RAIL_LEFT", 1), build_side_rail("VECTOR_RAIL_RIGHT", -1)]
    stock = build_stock()
    mags = [build_magazine(name) for name in MAGS]
    kit.unwrap([body, bolt, handle] + rails, 0.005)
    for o in [stock] + mags:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    # the bolt is baked with the body only (it moves); the handle with the body; the side rails alone (own origins)
    gun_maps = [bake(body, [body, handle], 256), bake(bolt, [body, bolt], 256), bake(handle, [body, handle], 256)]
    gun_maps += [bake(r, [r], 256) for r in rails]
    stock_maps = [bake(stock, [stock], 128)]
    for gun in ("VECTOR45", "VECTOR9"):
        texture(gun_maps, [gun, gun + ":carrier", gun + ":handle", gun + ":rail", gun + ":rail"], 256,
                os.path.join(TEX_DIR, gun + ".png"))
        texture(stock_maps, [gun + ":stock"], 128, os.path.join(TEX_DIR, gun + "_STOCK.png"))
    for m in mags:
        texture([bake(m, [m], 128)], ["VECTOR45:" + m.name], 128, os.path.join(TEX_DIR, m.name + ".png"))

    # the pistols' own magazine meshes, stretched (their textures are theirs: the main mod's and GoM's)
    copies, extras = [], {}
    g21 = kit.import_mesh(os.path.join(MAIN_MEDIA, "models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx"),
                          "45Magazine13_GLOCK21")
    gom = kit.gom_glock17_magazine()
    ob, _, _ = stretch_copy(g21, "45Magazine30_GLOCK21", 17 * EXTRA_MM["45"] * K)
    copies.append(ob)
    for rounds in (33, 40):
        ob, _, _ = stretch_copy(gom, "9x19Magazine%d_GLOCK17" % rounds, (rounds - 17) * EXTRA_MM["9"] * K_GOM)
        copies.append(ob)
    extras["glock21_45Magazine13_prop2"] = kit.bip01_prop2(g21, gom)
    extras["glock21_45Magazine30_prop2"] = extras["glock21_45Magazine13_prop2"]
    extras["glock17_prop2"] = {"offset": kit.GOM_GLOCK_PROP2[0], "rotate": kit.GOM_GLOCK_PROP2[1]}

    bounds = {o.name: kit.bounds_of(o) for o in [body, bolt, handle, stock] + rails + mags + copies}
    bounds["VECTOR_BOLT_fired"] = kit.bounds_of(bolt, (0, -CARRIER_TRAVEL * K, 0))
    bounds["VECTOR_HANDLE_back"] = kit.bounds_of(handle, (0, -HANDLE_TRAVEL * K, 0))
    pts = points(bounds)
    pts["_extras"]["pistol_magazines"] = extras
    bounds["VECTOR_STOCK_deployed"] = kit.bounds_at(stock, pts["stock"])
    bounds["VECTOR_STOCK_folded"] = kit.bounds_at(stock, pts["stock_folded"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    for name, b in bounds.items():
        print("VECTOR %-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    for o in (g21, gom):
        bpy.data.objects.remove(o)
    turned = [turned_copy(o, o.name.replace("VECTOR_", "VECTOR9_", 1)) for o in [body, bolt, handle] + rails]
    stock9 = turned_copy(stock, "VECTOR9_STOCK")
    b9 = {o.name: kit.bounds_of(o) for o in turned + [stock9]}
    pts9 = handgun_points(pts, b9)
    b9["VECTOR9_STOCK_deployed"] = kit.bounds_at(stock9, pts9["stock"])
    b9["VECTOR9_STOCK_folded"] = kit.bounds_at(stock9, pts9["stock_folded"])
    with open(POINTS9_JSON, "w") as fh:
        json.dump(pts9, fh, indent=2)
        fh.write("\n")
    for name, b in b9.items():
        print("VECTOR %-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    kit.export([body, bolt, handle] + rails + turned, FBX["gun"])
    kit.export(mags + copies, FBX["mags"])
    kit.export([stock, stock9], FBX["parts"])


if __name__ == "__main__":
    main()
