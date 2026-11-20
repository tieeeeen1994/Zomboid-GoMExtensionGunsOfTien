"""Izhmash SV-98 (7.62x54R) model and textures for Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_sv98.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_SV98.fbx       SV98_BODY, SV98_BOLT, SV98_BIPOD_FOLDED,
                                                                SV98_BIPOD_DEPLOYED
    M/models_X/weapons/magazines/GunsOfTienPost93_SV98_magazines.fbx   762x54Magazine10_SV98
    M/textures/weapons/GunsOfTienPost93/SV98.png                512 atlas (stock, metal)
    M/textures/weapons/GunsOfTienPost93/762x54Magazine10_SV98.png      128
    scripts/post93/sv98_points.json                             attachment points (game space)

User, 2026-11-20 (docs/sv98_sv99_svu_research.md, docs/post93_design.md "SV-98 and SV-99"): Izhmash's bolt-action
sniper rifle of 1998-2000 (adopted 2003), Post-93, the plywood-stock rifle (the only one by 2000): green laminated
"aviation plywood" thumbhole stock with long grooves along the forend, a stippled grip, a skeleton butt with two
windows, an adjustable comb on two posts and a rubber butt plate on its adjuster; the round receiver with its rail on
top (modelled; a hidden integrated rail part is the parent of GoM's optics, as on Post-93's Mk 11), the bolt with its
ball knob on the right, the 650 mm free-floated barrel, the hooded front sight on its band, the conical muzzle sleeve,
the drum rear sight on the receiver's front, its own 10-round polymer magazine (only its floor shows under the stock)
and the bipod that folds back into the forend's slot (two nodes, as the RPK's). Not modelled: the detachable carrying
handle, the mirage strap, the rear monopod, the suppressor.

Built on the kit of post93/build_mp7.py, as build_ppk.py builds the PPK: slabs of the side outline (holes cut),
lathed metal, the texture painted per pixel from baked position / normal / material / occlusion maps. Modelled upright
(+X the gun's left, as GoM's rifles), 0.603 of real size. Origin: where GoM's M24 has it against its trigger and bore
(the trigger blade 57.5 mm ahead of the origin, the bore 16 mm over it, real mm), so the rifle sits in the
vanilla rifle clips as GoM's bolt rifles do.

Reference (references/sv98, SOURCES.txt): zonawar's studio right side, sv98/ru_003.jpg (2048 px, the rifle with
carrying handle and a scope; 1.566 px a mm over its 1200 mm, butt pad to muzzle sleeve), read column by column
(the stock's green, the metal's dark: its top and bottom per 10 mm) and on mm grids for the holes and parts. Profiles
are in that photo's (L, R) mm: L forward from the butt pad's rear, R down from the photo's row 280.
"""

import sys as _sys
_sys.dont_write_bytecode = True
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV98.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV98_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "sv98_points.json")
MAG_NAME = "762x54Magazine10_SV98"

K = 0.000603
kit.K = K
MATS = ["wood", "rubber", "metal", "silver", "dark", "magpoly", "stipple", "rail"]
kit.MATS[:] = MATS
for ch, rows in {"V": ["101", "101", "101", "101", "010"], "-": ["000", "000", "111", "000", "000"],
                 "9": ["111", "101", "111", "001", "111"], "8": ["111", "101", "111", "101", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

TRIGGER_L = 404.0                  # the blade's middle
BORE_R = 24.0                      # the bore's row (barrel 14..36 at L 950-1130, receiver axis)
L0 = TRIGGER_L - 57.5              # GoM's M24: trigger 0.036 ahead of the origin at its 0.626 = 57.5 mm real
R0 = BORE_R + 16.0                 # GoM's M24: bore 0.0099 over the origin = 16 mm real
W_STOCK, W_FOREND, W_COMB = 21.0, 22.0, 17.0
RECEIVER = (388.0, 562.0, 16.0)    # L from, to, radius (round, on the bore)
BOLT_TRAVEL = 92.0                 # the 7.62x54R bolt's throw (back until the knob clears the trigger opening's rear)


def P(L, R):
    return L - L0, R0 - R


def PL(pts):
    return [P(L, R) for L, R in pts]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="wood", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def ellipse(cL, cR, a, b, rot=0.0, n=28):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cL + a * math.cos(t) * c - b * math.sin(t) * s, cR + a * math.cos(t) * s + b * math.sin(t) * c)
            for t in (2 * math.pi * k / n for k in range(n))]


def rounded_rect(La, Lb, Ra, Rb, r, n=4):
    pts = []
    for cL, cR, a0 in ((Lb - r, Ra + r, 270.0), (Lb - r, Rb - r, 0.0), (La + r, Rb - r, 90.0), (La + r, Ra + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cL + r * math.cos(a), cR + r * math.sin(a)))
    return pts


# ==================================================================================================
# Profiles (photo L, R mm)
# ==================================================================================================

# The stock body: the top behind the comb, the wrist rising to the receiver, the forend's top under the barrel to the
# rounded tip, its bottom back to the trigger opening, the grip's front and bottom, the lower bar back to the butt.
STOCK = [(66, 80), (245, 80), (250, 62), (258, 53), (330, 51), (345, 46), (360, 41.5), (380, 37), (400, 36.5),
         (450, 35.8), (560, 34), (580, 33.2), (720, 31.3), (820, 30.0), (868, 30.0), (880, 34), (886, 45), (886, 56),
         (882, 64), (875, 72), (860, 77), (850, 82), (840, 87), (820, 90), (800, 92.6), (760, 97), (700, 98.3),
         (650, 99), (580, 100), (560, 103), (540, 106), (520, 110.5), (500, 117.5), (470, 125), (450, 130),
         (430, 137), (410, 140), (398, 139), (388, 136), (378, 132), (368, 126), (360, 124), (357, 140), (354, 170),
         (351, 190), (345, 197), (330, 197.3), (310, 193.5), (290, 186.5), (280, 179.4), (270, 171), (260, 166),
         (250, 169), (240, 172.4), (230, 177), (220, 180), (210, 182.6), (200, 184.5), (190, 187), (160, 187),
         (152, 193), (140, 196), (100, 198), (66, 198)]
THUMBHOLE = ellipse(266.0, 106.0, 31.0, 38.0, -28.0)
WINDOWS = [rounded_rect(99, 159, 100, 154, 7), rounded_rect(179, 215, 100, 153, 7)]
# the trigger opening, traced off the photo (ru_003.jpg x 560-760, y 330-520 at 6.3 px a mm; user, 2026-11-20: the
# trigger was "completely wrong"): a flat top, a rounded rear, the front and bottom fuller
TRIGGER_OPENING = [(378.0, 100.6), (379.9, 95.0), (384.4, 91.3), (392.4, 89.1), (403.6, 87.5), (413.2, 87.0),
                   (422.7, 87.8), (429.1, 91.8), (433.1, 99.0), (433.6, 107.0), (431.5, 114.9), (425.9, 121.3),
                   (417.9, 124.5), (406.8, 125.3), (395.6, 124.5), (386.0, 122.1), (379.9, 116.5), (377.7, 108.6)]
COMB = [(72, 50), (72, 32), (78, 27), (240, 26), (255, 28), (250, 40), (242, 50)]
COMB_BLOCK = [(105, 82), (105, 50), (238, 50), (238, 82)]
PAD = [(8, 77), (28, 75), (31, 213), (12, 215), (4, 205), (1, 160), (1, 110), (3, 90)]
ADJUSTER = [(30, 62), (66, 58), (68, 200), (30, 202)]
GRIP_STIPPLE = [(292, 92), (346, 92), (352, 130), (346, 190), (300, 187), (276, 160), (272, 125)]
FOREND_GROOVES = [(452, 550), (595, 700), (735, 820)]
GROOVE_R = (54.0, 68.0)
# the blade, traced off the same crop: a thin hook hanging from the opening's top (its root inside the stock), its
# back bulging rearward, its tip curled forward (it bulged forward until 2026-11-20)
TRIGGER = [(407.6, 84.5), (406.6, 91.0), (403.6, 99.0), (402.3, 107.0), (404.4, 113.3), (406.3, 116.5),
           (405.8, 117.5), (403.3, 114.6), (400.7, 108.6), (399.7, 100.6), (400.4, 92.3), (401.2, 84.5)]
# the barrel: radius at L (mm), tapering from the receiver to the band
BARREL = [(560, 11.5), (700, 11.0), (1135, 9.5)]
BAND = (1134.0, 1170.0, 16.0)
SLEEVE = [(1170, 13.5), (1186, 13.5), (1192, 11.5), (1200, 10.0)]
FRONT_POST = (1145.0, 1160.0, -6.0, 10.0)          # L, L, R top, R bottom (the post's block on the band)
HOOD = (1143.0, 1162.0, -14.0, -6.0)
REAR_SIGHT = (564.0, 584.0, 2.0, 12.0)             # the drum sight's block on the receiver's front
RAIL = (398.0, 556.0)                              # the receiver's rail (L), over the ejection port as on the photo
KNOB = (401.0, 66.0, 9.0)                          # L, R, radius of the bolt's ball
HANDLE_ROOT = (419.0, BORE_R)
SHROUD = (377.0, 391.0, 11.5)
SAFETY = (386.0, 397.0, 29.0, 35.0)                # the safety lever behind the handle (right side)
MAG_BOX = (440.0, 532.0, 40.0, 113.0, 15.0)        # L from, to, R top (feed lips), R floor (flush with the stock
                                                   # at the well's front: the floor sits recessed in the well), half width
# the bipod: its head under the forend's tip, legs back in the forend's slot or down and splayed
BIPOD_HEAD = (868.0, 80.0)
BIPOD_LEG = 215.0
BIPOD_SPLAY, BIPOD_RAKE = 12.0, 6.0


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, STOCK, [THUMBHOLE, TRIGGER_OPENING] + WINDOWS, half=W_STOCK, bevel=3.5, res=1, mat="wood")
    slab(b, COMB, half=W_COMB, bevel=3.0, res=1, mat="wood")
    slab(b, COMB_BLOCK, half=11.0, bevel=1.0, mat="rubber")
    slab(b, PAD, half=W_STOCK - 0.5, bevel=4.0, res=1, mat="rubber")
    slab(b, ADJUSTER, half=W_STOCK - 2.0, bevel=1.5, mat="rubber")
    slab(b, TRIGGER, half=2.4, bevel=0.4, mat="metal")
    # the receiver and barrel, round on the bore; the drum sight; the front sight on its band; the muzzle sleeve
    y_bore, z_bore = P(0.0, BORE_R)
    rec = RECEIVER
    b.lathe("y", (0.0, 0.0, z_bore), [(rec[0] - L0, 0.0), (rec[0] - L0, rec[2] - 2.0), (rec[0] - L0 + 2.0, rec[2]),
                                       (rec[1] - L0, rec[2]), (rec[1] - L0, 0.0)], seg=16, mat="metal")
    prof = [(BARREL[0][0] - L0, 0.0)] + [(L - L0, r) for L, r in BARREL] + [(BARREL[-1][0] - L0, 0.0)]
    b.lathe("y", (0.0, 0.0, z_bore), prof, seg=14, mat="metal")
    L1, L2, r = BAND
    b.lathe("y", (0.0, 0.0, z_bore), [(L1 - L0, 0.0), (L1 - L0, r - 1.0), (L1 - L0 + 1.0, r), (L2 - L0 - 1.0, r),
                                       (L2 - L0, r - 1.0), (L2 - L0, 0.0)], seg=14, mat="metal")
    sl = [(SLEEVE[0][0] - L0, 0.0)] + [(L - L0, r) for L, r in SLEEVE] + [(SLEEVE[-1][0] - L0, 6.5),
                                                                          (SLEEVE[-1][0] - L0 - 6.0, 5.0),
                                                                          (SLEEVE[-1][0] - L0 - 6.0, 0.0)]
    b.lathe("y", (0.0, 0.0, z_bore), sl, seg=14, mat="metal")
    La, Lb, Rt, Rb = FRONT_POST
    gbox(b, La, Lb, Rb, Rt, -4.0, 4.0, mat="metal", bevel=0.5)
    La, Lb, Rt, Rb = HOOD
    for x0, x1 in ((-8.0, -6.0), (6.0, 8.0)):
        gbox(b, La, Lb, Rb + 2.0, Rt, x0, x1, mat="metal")
    gbox(b, La, Lb, Rt + 2.0, Rt, -8.0, 8.0, mat="metal")
    # the rail on the receiver's top (MIL-STD-1913 crossbars, the kit's), the parent of GoM's optics
    face = z_bore + RECEIVER[2] - 1.0
    kit.picatinny(b, RAIL[0] - L0, RAIL[1] - L0, lambda u, h, y: Vector((u, y, face + h)))
    La, Lb, Rt, Rb = REAR_SIGHT
    gbox(b, La, Lb, Rb, Rt, -9.0, 9.0, mat="metal", bevel=1.5)
    return b.to_object("SV98_BODY")


def gbox(b, La, Lb, Ra, Rb, xa, xb, mat="metal", bevel=0.0):
    """A box between photo L and rows R (any order) and x (game mm)."""
    (y0, z0), (y1, z1) = P(La, Ra), P(Lb, Rb)
    return b.box(min(xa, xb), max(xa, xb), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1), mat=mat, bevel=bevel)


def build_bolt():
    """What moves back when the bolt is worked: the shroud behind the receiver, the handle and its ball."""
    b = kit.Builder()
    y_bore, z_bore = P(0.0, BORE_R)
    s0, s1, r = SHROUD
    b.lathe("y", (0.0, 0.0, z_bore), [(s0 - L0, 0.0), (s0 - L0, r - 3.0), (s0 - L0 + 3.0, r), (s1 - L0, r),
                                       (s1 - L0, 0.0)], seg=12, mat="metal")
    # the bolt body (bright, cadmium-plated): inside the receiver when closed, bridging the gap behind it when open
    b.lathe("y", (0.0, 0.0, z_bore), [(s1 - L0, 0.0), (s1 - L0, 9.0), (s1 - L0 + BOLT_TRAVEL + 4.0, 9.0),
                                       (s1 - L0 + BOLT_TRAVEL + 4.0, 0.0)], seg=12, mat="silver")
    root = Vector((-RECEIVER[2] + 2.0, *P(*HANDLE_ROOT)))
    kL, kR, kr = KNOB
    knob = Vector((-30.0, *P(kL, kR)))
    d = knob - root
    n = d.normalized()
    # the handle: a rod from the bolt body out and down to the ball (game x negative = the gun's right)
    length = d.length - kr * 0.7
    xf = Matrix.Translation(root) @ n.to_track_quat('Y', 'Z').to_matrix().to_4x4()
    b.lathe("y", (0.0, 0.0, 0.0), [(0.0, 0.0), (0.0, 4.2), (length, 3.4), (length, 0.0)], seg=10, mat="silver",
            xf=xf)
    prof = [(-kr, 0.0)] + [(kr * math.sin(math.radians(a)), kr * math.cos(math.radians(a)))
                           for a in range(-80, 90, 20)] + [(kr, 0.0)]
    b.lathe("y", tuple(knob), prof, seg=14, mat="rubber")
    # the safety lever on the right, behind the handle
    La, Lb, Rt, Rb = SAFETY
    gbox(b, La, Lb, Rb, Rt, -RECEIVER[2] - 3.0, -RECEIVER[2] + 1.0, mat="metal", bevel=0.6)
    return b.to_object("SV98_BOLT")


def build_bipod(deployed):
    b = kit.Builder()
    hL, hR = BIPOD_HEAD
    head = Vector((0.0, *P(hL, hR)))
    gbox(b, hL - 12, hL + 12, hR + 8, hR - 4, -12.0, 12.0, mat="metal", bevel=1.0)
    for s in (-1, 1):
        top = head + Vector((s * 8.0, 0.0, -6.0))
        if deployed:
            d = Vector((s * math.sin(math.radians(BIPOD_SPLAY)), math.sin(math.radians(BIPOD_RAKE)), -1.0)).normalized()
        else:
            d = Vector((s * 0.02, -1.0, -0.04)).normalized()
        foot = top + d * BIPOD_LEG
        xf = Matrix.Translation(top) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4()
        b.lathe("y", (0.0, 0.0, 0.0), [(0.0, 0.0), (0.0, 5.0), (BIPOD_LEG * 0.55, 5.0), (BIPOD_LEG * 0.55, 4.0),
                                        (BIPOD_LEG, 4.0), (BIPOD_LEG, 0.0)], seg=8, mat="metal", xf=xf)
        foot_box = (foot.x - 6.0, foot.x + 6.0, foot.y - 9.0, foot.y + 9.0, foot.z - 5.0, foot.z + 1.0)
        if not deployed:
            foot_box = (foot.x - 4.0, foot.x + 4.0, foot.y - 2.0, foot.y + 16.0, foot.z - 9.0, foot.z + 1.0)
        b.box(*foot_box, mat="rubber", bevel=1.0)
    return b.to_object("SV98_BIPOD_DEPLOYED" if deployed else "SV98_BIPOD_FOLDED")


def build_magazine():
    """The 10-round polymer magazine: a box from its feed lips to the floor, the floor plate a little wider. Origin at
    the feed lips' front (GoM's magazines' way), drawn at the gun's `magazine` point."""
    b = kit.Builder()
    La, Lb, Rt, Rf, hw = MAG_BOX
    top = P(Lb, Rt)
    def M(L, R):
        y, z = P(L, R)
        return y - top[0], z - top[1]
    body = [M(La + 4, Rt), M(Lb, Rt), M(Lb, Rf - 4), M(La, Rf - 4), M(La, Rt + 10)]
    kit.slab(b, body, (), hw, 1.5, 0, "magpoly", 0.0)
    floor = [M(La - 2, Rf - 5), M(Lb + 2, Rf - 5), M(Lb + 2, Rf), M(La - 2, Rf)]
    kit.slab(b, floor, (), hw + 1.0, 1.0, 0, "magpoly", 0.0)
    lips = [M(La + 12, Rt - 3), M(Lb - 6, Rt - 3), M(Lb - 6, Rt + 1), M(La + 12, Rt + 1)]
    kit.slab(b, lips, (), hw - 4.0, 0.5, 0, "metal", 0.0)
    return b.to_object(MAG_NAME)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {"wood": (36, 112, 96), "rubber": (30, 31, 31), "metal": (40, 42, 45), "silver": (168, 168, 160),
        "dark": (14, 14, 15), "magpoly": (32, 33, 34), "stipple": (30, 96, 82), "rail": (38, 40, 43)}


def in_poly(L, R, pts):
    inside = np.zeros(L.shape, bool)
    n = len(pts)
    for i in range(n):
        (L1, R1), (L2, R2) = pts[i], pts[(i + 1) % n]
        cond = ((R1 > R) != (R2 > R)) & (L < (L2 - L1) * (R - R1) / ((R2 - R1) or 1e-9) + L1)
        inside ^= cond
    return inside


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "silver", "rail")])
    mott = kit.vnoise(p, 8.0, 1) * 0.6 + kit.vnoise(p, 2.0, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    up = np.clip(n[..., 2], -1, 1)
    col *= (0.97 + 0.12 * up)[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 45.0, 22.0) * (0.75 + 0.5 * kit.vnoise(p, 3.0, 5))
    col += (convex * wear)[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x = p[..., 0]
    L, R = p[..., 1] + L0, R0 - p[..., 2]
    side = np.abs(n[..., 0]) > 0.6
    wood = mat == MATS.index("wood")
    if kind == "gun":
        # laminated plywood: on the sides, the veneer's contour bands (flat-cut layers); on the cut edges, the layers
        # themselves as lines along the stock (every 1.6 mm across it)
        warp = 14.0 * kit.vnoise(p * np.array([1.0, 0.15, 1.0]), 30.0, 7) + 4.0 * kit.vnoise(p, 6.0, 9)
        band = np.sin((R + warp) * 2 * np.pi / 13.0)
        shade = 0.9 + 0.08 * band + 0.16 * (kit.vnoise(p * np.array([1.0, 0.3, 1.0]), 25.0, 8) - 0.5)
        ws = wood & side
        col[ws] *= shade[ws][..., None]
        layer = np.sin(x * 2 * np.pi / 3.2)
        we = wood & ~side
        col[we] *= (0.86 + 0.16 * layer[we])[..., None]
        col[we] += np.array([10.0, 18.0, 14.0])
        # the stippled grip panels
        st = ws & in_poly(L, R, GRIP_STIPPLE)
        dots = kit.vnoise(p, 0.9, 11)
        col[st] = np.array(BASE["stipple"]) * (0.7 + 0.5 * dots[st])[..., None]
        # the forend's long grooves (a darker recess with a lit lower rim)
        for La, Lb in FOREND_GROOVES:
            g = ws & in_poly(L, R, rounded_rect(La, Lb, GROOVE_R[0], GROOVE_R[1], 6.5))
            col[g] *= 0.62
            rim = ws & in_poly(L, R, rounded_rect(La - 1.2, Lb + 1.2, GROOVE_R[0] - 1.2, GROOVE_R[1] + 1.2, 7.5)) & ~g
            col[rim] *= 1.18
        # screws: the forend's front, the stock's bolts, the sling swivel stud
        for cL, cR, r in ((870, 50, 3.5), (420, 50, 2.6), (300, 175, 4.5), (275, 99, 3.0), (60, 190, 4.0)):
            d = np.hypot(L - cL, R - cR)
            col[side & (d < r)] = np.array(BASE["metal"]) * 1.2
            col[side & (d < r) & (d > r - 0.8)] *= 0.5
        metal = mat == MATS.index("metal")
        # the receiver's ejection port (right side, the bolt's bright body inside) and the loading port's edge
        right = n[..., 0] < -0.3
        port = metal & right & (L > 425) & (L < 482) & (R > BORE_R - 11) & (R < BORE_R + 3)
        col[port] = np.array(BASE["silver"]) * (0.8 + 0.25 * kit.vnoise(p, 2.0, 12))[port][..., None]
        col[metal & right & (np.abs(L - 425) < 0.8) & (R > BORE_R - 11) & (R < BORE_R + 3)] *= 0.4
        # markings on the receiver's left: "SV-98" and the calibre (a dim stamp)
        left = n[..., 0] > 0.3
        stamp = metal & left & kit.text_mask(-L, -R, "SV-98", -500.0, -BORE_R - 2.0, 4.5)
        col[stamp] *= 1.5
        # the muzzle's bore
        bore = (mat == MATS.index("metal")) & (n[..., 1] > 0.6) & (L > 1195) & (np.hypot(x, R - BORE_R) < 4.0)
        col[bore] = BASE["dark"]
    elif kind == "bolt":
        pass
    elif kind == "mag":
        rib = (mat == MATS.index("magpoly")) & side & (np.sin(R * 2 * np.pi / 8.0) > 0.6)
        col[rib] *= 1.25
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


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

def g(L, R, x=0.0):
    y, z = P(L, R)
    return [round(x * K, 4) + 0.0, round(y * K, 4) + 0.0, round(z * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]
# GoM's optics on our rails sit with their `scope` point 3.2 x 0.001 under the crossbars' top (the Mk 11's relation,
# CLAUDE.md "Mk 11 Mod 0"); the kit's crossbars top out 9 mm over the rail's mounting face
SCOPE_UNDER_TOP = 0.0032


def points():
    top = (R0 - BORE_R + RECEIVER[2] - 1.0 + 9.0) * K
    scope = [0.0, round((RAIL[0] + RAIL[1]) / 2.0 - L0, 1) * K, top - SCOPE_UNDER_TOP]
    scope = [round(v, 4) + 0.0 for v in scope]
    pts = {
        "muzzle": {"offset": g(SLEEVE[-1][0], BORE_R), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": g(MAG_BOX[1], MAG_BOX[2]), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-BOLT_TRAVEL * K, 4), round(2.0 * K, 4)], "rotate": ZERO},
        "scope": {"offset": scope, "rotate": ZERO},
        # GoM's M24's floor pose, at our scale
        "world": {"offset": [0.0193, 0.1252, 0.0], "rotate": [180.0, 0.0, 180.0]},
    }
    pts["_extras"] = {"photo_origin_mm": [L0, R0], "real_mm_per_game_unit": round(1.0 / K, 2),
                      "bore_z": round((R0 - BORE_R) * K, 4)}
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
    folded, deployed = build_bipod(False), build_bipod(True)
    mag = build_magazine()
    kit.unwrap([body, bolt, folded, deployed], 0.006)
    kit.unwrap([mag], 0.012)
    os.makedirs(TEX_DIR, exist_ok=True)
    gun = [body, bolt, folded, deployed]
    texture(gun, [gun] * 4, ["gun", "bolt", "bipod", "bipod"], 512, os.path.join(TEX_DIR, "SV98.png"))
    texture([mag], [[mag]], ["mag"], 128, os.path.join(TEX_DIR, MAG_NAME + ".png"))
    bounds = {o.name: kit.bounds_of(o) for o in gun + [mag]}
    kit.export(gun, FBX_GUN)
    kit.export([mag], FBX_MAGS)
    pts = points()
    pts["_bounds"] = bounds
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    for name, bb in bounds.items():
        print("%-24s tris %5d  min %s  max %s" % (name, bb["tris"], bb["min"], bb["max"]))


if __name__ == "__main__":
    main()
