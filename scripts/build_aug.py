"""Steyr AUG A1 model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_aug.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_AUG.fbx        AUG_BODY, AUG_BOLT, AUG_HANDLE, AUG_FOREGRIP
    M/models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx  556x45Magazine30_AUG, 556x45Magazine42_AUG
    M/textures/weapons/GunsOfTien/AUG.png                 256 atlas (body, charging handle, foregrip)
    M/textures/weapons/GunsOfTien/556x45Magazine30/42_AUG.png  128 each
    scripts/aug_points.json                               attachment points (game space)

The AUG A1 (Austrian Army StG 77; user, 2026-10-27: Steyr green, no muzzle parts) is traced from the Wikimedia Commons
photo "Steyr AUG 5,56 mm" (MoserB, public domain; its background-removed copy "... noBG.png", CC BY-SA 4.0, was used
for the edges; neither is kept in the repo: references/aug): the left side, muzzle left, the folding front grip down,
the magazine out and lying beside the gun, a sling over the butt. Scaled to Steyr's 790 mm with the 508 mm barrel
(5.629 px/mm); the bore is level in the photo (barrel centre within 1 px over 1000 px). Profiles are written in that
photo's coordinates, real millimetres: L back from the muzzle tip, H up from the lowest point (the butt's heel).
The loose magazine measures 60 mm front to back and about 165 mm from its lips to its base, curved forward.

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, drawn at 0.603 of real size (the M16A2's proportion, every Guns of Tien gun since
2026-10-26). A bullpup as GoM's FAMAS: the grip near the middle, the magazine and action behind it.
Nodes: AUG_BODY (stock, receiver, the integral 1.5x scope and carrying handle, barrel, flash hider, trigger guard,
grip); AUG_BOLT = the bolt carrier seen through the ejection port on the right (GoM's Bolt_Fired swap slides it back
on each shot and while the gun is empty); AUG_HANDLE = the charging handle on the left, which does not reciprocate on
the real gun: drawn back by `handle_back` only while racked (GunsOfTien.ChargingHandle_Back); AUG_FOREGRIP = the folding front grip, modelled down (as photographed) with its origin at its hinge
pin, drawn at `foregrip_deployed` and, turned 90 degrees forward about the pin, at `foregrip_folded`, where it lies
under the barrel as on the real A1. The scope is part of the body (the A1's optic is cast into the receiver); its
stats come from a hidden part item with no model. GoM's optional side rails (Picatinny_Rail_Left / _Right, user
2026-10-30) are drawn at `rail_left` / `rail_right` with our short AUG_RAIL_LEFT / _RIGHT (build_rails.py, which reads
their place from the constants here); no top rail, as an optic over the integral scope would add its stats to the
scope's. The magazines (translucent smoke polymer, painted with the rounds
inside since GoM's textures carry no alpha) hang from `magazine`, their feed lips.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_AUG.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_AUG_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "aug_points.json")

K = 0.000603                       # game units per real mm: the M16A2's proportion (every Guns of Tien gun)
K_OLD = 0.00065                    # GoM's rifles: the `world` floor point is scaled from them
kit.K = K
MATS = ["polymer", "grip", "metal", "barrel", "dark", "scope", "magpoly", "brass", "copper"]
kit.MATS[:] = MATS
for ch, rows in {"A": ["010", "101", "111", "101", "101"], "U": ["101", "101", "101", "101", "111"],
                 "G": ["111", "100", "101", "101", "111"], "S": ["111", "100", "111", "001", "111"],
                 "T": ["111", "010", "010", "010", "010"], "E": ["111", "100", "111", "100", "111"],
                 "Y": ["101", "101", "010", "010", "010"], "R": ["110", "101", "110", "101", "101"],
                 "5": ["111", "100", "111", "001", "111"], "7": ["111", "001", "010", "010", "010"],
                 "2": ["111", "001", "111", "100", "111"], "4": ["101", "101", "111", "001", "001"],
                 "0": ["111", "101", "101", "101", "111"], "3": ["111", "001", "011", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

ZERO = [0.0, 0.0, 0.0]

# Photo frame: origin = the grip's back meeting the stock's underside (the rear-top of the pistol grip).
L0, H0 = 455.0, 100.0
BORE = 143.5
TRAVEL = 92.0                      # charging handle stroke, only while racked (it does not reciprocate)
W_STOCK, W_RCV, W_GRIP, W_GUARD, W_FG = 27.0, 21.0, 15.0, 9.0, 15.0     # half widths, mm
FG_HINGE = (249.0, 115.0)          # the front grip's pin under the barrel bracket
MAG_LIPS = (577.0, 90.0)           # the magazine's feed lips, inside the well (its mouth L 545-610 at H 77)
SCOPE_H = 214.5                    # the scope tube's axis


def P(L, H):
    return L0 - L, H - H0


def PL(pts):
    return [P(L, H) for L, H in pts]


def y(L):
    return L0 - L


def z(H):
    return H - H0


def gp(L, H, x=0.0):
    yy, zz = P(L, H)
    return [round(x * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((y(La), y(Lb)))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, z(Ha), z(Hb), mat=mat, bevel=bevel)


def bore_lathe(b, profile, seg=16, mat="barrel", phase=0.5):
    """Revolved about the bore: profile [(L, radius)] from the rear to the muzzle."""
    b.lathe("y", (0, 0, z(BORE)), [(y(L), r) for L, r in profile], seg=seg, mat=mat, phase=phase)


def both(fn):
    for s in (1, -1):
        fn(s)


# ==================================================================================================
# Profiles (photo L, H mm)
# ==================================================================================================

# The stock: one polymer shell from under the receiver's front to the butt, round the magazine well and the heel.
STOCK = [(298.0, 113.0), (298.0, 126.0), (398.0, 126.0), (400.0, 160.0), (405.0, 168.0), (412.0, 163.5),
         (760.0, 163.5), (772.0, 159.5), (782.0, 151.0), (788.0, 140.0), (776.0, 14.0), (770.0, 4.0),
         (668.0, 3.0), (658.0, 9.0), (655.0, 19.0), (661.0, 27.0), (612.0, 76.5), (545.0, 77.0), (537.0, 82.0),
         (530.0, 92.0), (522.0, 100.0), (455.0, 100.5), (452.0, 108.0), (340.0, 108.0), (330.0, 112.0)]
# The trigger guard and pistol grip, one moulding with the stock: the bar from under the receiver's front down and
# back to the grip's foot; the hand's opening behind it.
FRAME = [(300.0, 117.0), (318.0, 108.0), (330.0, 100.0), (340.0, 90.0), (352.0, 70.0), (368.0, 50.0),
         (376.0, 40.0), (384.0, 30.0), (392.0, 20.0), (400.0, 10.0), (410.0, 4.0), (470.0, 3.0), (477.0, 8.0),
         (479.0, 25.0), (476.0, 42.0), (468.0, 58.0), (458.0, 72.0), (452.0, 85.0), (453.0, 96.0), (460.0, 104.0),
         (460.0, 117.0)]
OPENING = [(345.0, 108.5), (396.0, 108.5), (401.0, 99.0), (405.0, 89.0), (417.0, 73.0), (431.0, 56.0),
           (439.0, 41.0), (444.0, 27.0), (443.0, 20.0), (436.0, 16.5), (418.0, 16.5), (410.0, 20.0), (400.0, 30.0),
           (392.0, 40.0), (384.0, 50.0), (366.0, 70.0), (352.0, 90.0), (346.0, 100.0)]
GRIP = [(402.0, 104.0), (405.0, 89.0), (417.0, 73.0), (431.0, 56.0), (439.0, 41.0), (444.0, 27.0), (446.0, 12.0),
        (452.0, 5.0), (470.0, 4.0), (477.0, 9.0), (478.5, 25.0), (475.5, 42.0), (467.5, 58.0), (457.5, 72.0),
        (451.5, 85.0), (452.5, 96.0), (458.0, 104.0)]
TRIGGER = [(367.0, 110.0), (371.0, 101.0), (369.0, 93.0), (365.0, 87.0), (367.0, 84.5), (374.0, 88.0), (380.0, 96.0),
           (382.0, 110.0)]
SAFETY = (405.0, 416.0, 116.5, 124.5)                       # the cross-bolt safety's ends, both sides
MAG_RELEASE = [(612.0, 77.0), (615.0, 66.0), (628.0, 58.0), (648.0, 56.0), (651.0, 60.0), (636.0, 66.0),
               (628.0, 77.0)]
PORT_COVER = (512.0, 535.0, 113.0, 125.5)                   # the left side's blanked port plate (ejection right)
# The ejection port on the right and the bolt carrier seen through it (user, 2026-10-30: the AUG's handle does not
# reciprocate, only the carrier moves): the port's front half is painted as the open chamber, its rear half as the
# carrier's side; AUG_BOLT is a thin plate over the front half, flush with the stock. Fired or held open it slides back
# over the rear half, so the chamber shows in front of it and nothing stands outside the port.
PORT = (PORT_COVER[0] - 4.0, PORT_COVER[1] + 8.0, PORT_COVER[2] + 1.0, PORT_COVER[3] + 1.0)   # L 508-543, H 114-126.5
PORT_SPLIT = (PORT[0] + PORT[1]) / 2.0
CARRIER_TRAVEL = PORT_SPLIT - PORT[0] - 0.5
BUTT_PLATE_L = 774.0                                        # the butt plate's seam (behind it: the plate)
# The aluminium receiver (the scope and carrying handle are cast into it on the A1)
RECEIVER = (249.0, 402.0, 120.0, 161.0)
# GoM's optional side rails (user, 2026-10-30), drawn with our short models (build_rails.py) on every AUG: the left one
# (AUG_RAIL_LEFT, 4 crossbars, like Corvus Defensio's A3 receiver rail) on the receiver's front-left, under the
# charging handle's path (its lowest edge H 140, resting at L 255-290 and running back to L 382) and ahead of the
# stock's shell and the trigger frame (both from L 298), where GoM's own 125 mm rail has no room; the right one
# (AUG_RAIL_RIGHT) where the A3 SF has its factory side rail (post93/build_aug3.py SIDE_RAIL), clear of the ejection
# port (L 508-543) and under the carrying handle's base (H 158).
LEFT_RAIL = (256.0, 297.0)
LEFT_RAIL_H = 129.5                # its centre line: the crossbars' upper edge 10.6 mm above, under H 140
RIGHT_RAIL = (282.0, 381.0)
RIGHT_RAIL_H = 143.0
SIDE_RAIL_BASE, SIDE_RAIL_TEETH = 1.5, 3.0      # kit.picatinny(): crossbar faces base + teeth - 1 off the receiver
HANDLE_BASE = [(278.0, 158.0), (278.0, 166.0), (300.0, 167.5), (406.0, 167.5), (406.0, 158.0)]
FRONT_LEG = [(318.0, 205.0), (347.0, 205.0), (305.0, 166.0), (280.0, 163.0), (278.0, 167.0)]
REAR_LEG = [(392.0, 205.0), (458.0, 206.0), (440.0, 201.5), (425.0, 193.0), (412.0, 180.0), (406.0, 166.0),
            (405.0, 160.0), (390.0, 160.0), (390.5, 180.0)]
SCOPE = [(316.0, 0.0), (316.0, 14.0), (318.0, 15.6), (326.0, 15.6), (328.0, 12.5), (446.0, 12.5), (458.0, 13.5),
         (512.0, 13.5), (514.0, 15.6), (523.0, 15.6), (525.0, 14.0), (525.0, 0.0)]
# Barrel: flash hider (open prongs, painted slots), its collar and lock nut, the barrel, the gas cylinder in front of
# the receiver, the barrel's locking ring at the receiver's face; the front grip's bracket under it.
HIDER = [(37.0, 0.0), (37.0, 9.0), (8.0, 8.4), (6.0, 9.0), (1.0, 9.0), (0.0, 8.2), (0.0, 0.0)]
BARREL = [(250.0, 0.0), (250.0, 18.0), (246.0, 18.0), (246.0, 13.5), (198.0, 13.5), (197.0, 8.0), (70.0, 8.0),
          (70.0, 9.8), (62.0, 9.8), (62.0, 0.0)]
COLLAR = [(50.0, 0.0), (50.0, 9.8), (37.0, 9.8), (37.0, 0.0)]
NUT = [(62.0, 0.0), (62.0, 9.4), (50.0, 9.4), (50.0, 0.0)]
FG_BRACKET = [(228.0, 112.0), (228.0, 133.0), (262.0, 133.0), (262.0, 112.0), (255.0, 108.0), (238.0, 108.0)]
GAS_VALVE = (205.0, 216.0, 127.0, 133.5)
# The folding front grip as photographed (down), in photo coordinates; the node is moved to its hinge.
FOREGRIP = [(236.0, 111.0), (236.0, 90.0), (238.0, 60.0), (235.0, 30.0), (232.0, 14.0), (236.0, 6.0), (248.0, 4.0),
            (260.0, 6.0), (264.0, 14.0), (263.0, 40.0), (264.0, 70.0), (267.0, 100.0), (266.0, 111.0)]
CH = [(255.0, 140.0), (255.0, 163.0), (258.0, 172.0), (267.0, 172.0), (270.0, 165.0), (289.0, 163.0), (290.0, 145.0),
      (286.0, 140.0)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, STOCK, half=W_STOCK, bevel=4.0, res=1, mat="polymer")
    slab(b, FRAME, [OPENING], half=W_GUARD, bevel=2.5, res=1, mat="polymer")
    slab(b, GRIP, half=W_GRIP, bevel=4.5, res=1, mat="polymer")
    slab(b, TRIGGER, half=3.5, bevel=0.6, mat="dark")
    La, Lb, Ha, Hb = SAFETY
    box(b, La, Lb, Ha, Hb, -(W_STOCK + 1.5), W_STOCK + 1.5, mat="dark", bevel=0.8)
    slab(b, MAG_RELEASE, half=7.0, bevel=1.0, mat="dark")
    La, Lb, Ha, Hb = PORT_COVER
    box(b, La, Lb, Ha, Hb, W_STOCK - 1.0, W_STOCK + 1.2, mat="metal", bevel=0.5)
    # receiver, the handle's base along its top, the two legs up to the scope, the tube with its turret
    La, Lb, Ha, Hb = RECEIVER
    box(b, La, Lb, Ha, Hb, -W_RCV, W_RCV, mat="metal", bevel=1.8)
    slab(b, HANDLE_BASE, half=12.0, bevel=1.2, mat="scope")
    slab(b, FRONT_LEG, half=6.5, bevel=1.4, res=1, mat="scope")
    slab(b, REAR_LEG, half=7.5, bevel=1.4, res=1, mat="scope")
    b.lathe("y", (0, 0, z(SCOPE_H)), [(y(L), r) for L, r in SCOPE], seg=20, mat="scope", phase=0.5)
    yt = y(380.0)
    b.lathe("z", (0, yt, 0), [(z(225.0), 0), (z(225.0), 7.5), (z(233.0), 7.5), (z(236.0), 5.5), (z(236.0), 0)],
            seg=6, mat="dark")
    b.lathe("z", (0, yt, 0), [(z(190.0), 0), (z(190.0), 6.5), (z(203.0), 6.5), (z(203.0), 0)], seg=6, mat="dark")
    # barrel and its parts
    bore_lathe(b, BARREL, seg=18)
    bore_lathe(b, COLLAR, seg=18)
    bore_lathe(b, NUT, seg=6, phase=0.0)
    bore_lathe(b, HIDER, seg=16)
    slab(b, FG_BRACKET, half=10.0, bevel=1.2, mat="barrel")
    La, Lb, Ha, Hb = GAS_VALVE
    box(b, La, Lb, Ha, Hb, -6.0, 6.0, mat="dark", bevel=0.8)
    return b.to_object("AUG_BODY")


def build_carrier():
    """The bolt carrier's side in the ejection port's front half (bolt_lock); bolt_fired slides it back over the
    port's rear half. A plate 0.35 mm proud of the stock's right face (-X), reaching 0.4 mm into it."""
    b = kit.Builder()
    box(b, PORT[0] + 0.5, PORT_SPLIT - 0.2, PORT[2] + 0.5, PORT[3] - 0.5, -(W_STOCK + 0.35), -(W_STOCK - 0.4),
        mat="metal", bevel=0.1)
    return b.to_object("AUG_BOLT")


def build_handle():
    """The charging handle, forward (handle), out of the receiver's left side; handle_back pulls it back while
    racked."""
    b = kit.Builder()
    slab(b, CH, half=4.5, bevel=1.0, res=1, mat="grip", x0=W_RCV + 3.5)
    box(b, 258.0, 286.0, 145.0, 158.0, W_RCV - 3.0, W_RCV + 1.0, mat="dark", bevel=0.5)
    return b.to_object("AUG_HANDLE")


def build_foregrip():
    """Origin at the hinge pin (FG_HINGE), modelled down as photographed."""
    b = kit.Builder()
    hl, hh = FG_HINGE
    q = [(hl - L, H - hh) for L, H in FOREGRIP]       # (y, z) mm from the pin
    kit.slab(b, q, [], W_FG, 6.0, 2, "grip", 0.0)
    b.lathe("x", (0, 0, 0), [(-9.0, 0), (-9.0, 7.5), (9.0, 7.5), (9.0, 0)], seg=14, mat="barrel")
    return b.to_object("AUG_FOREGRIP")


# The magazines: Steyr's translucent smoke polymer, double stack, curving forward. Origin at the feed lips, top centre.
MAG_LEN = {30: 165.0, 42: 220.0}   # lips to base (the 42 is 12 rounds x 4.6 mm longer)
MAG_W, MAG_D = 15.0, 29.0          # half width across, half depth front to back
MAG_RAKE = math.radians(8.0)       # forward lean at the lips
MAG_R = 800.0                      # curvature radius, bottom forward


MAG_C = (MAG_R * math.cos(MAG_RAKE), MAG_R * math.sin(MAG_RAKE))   # the axis's centre of curvature (y, z)


def mag_frame(s):
    """Centre (y, z) and lean of the magazine's axis at distance s below its lips: an arc about MAG_C, so the axis
    at lean a is MAG_C - MAG_R (cos a, sin a), running down and forward."""
    a = MAG_RAKE + s / MAG_R
    return (MAG_C[0] - MAG_R * math.cos(a), MAG_C[1] - MAG_R * math.sin(a)), a


def mag_local(yy, zz):
    """A point of a magazine as built -> (s down its axis from the lips, u across it toward the muzzle)."""
    vy, vz = yy - MAG_C[0], zz - MAG_C[1]
    a = np.arctan2(-vz, -vy)
    return (a - MAG_RAKE) * MAG_R, MAG_R - np.hypot(vy, vz)


def mag_sweep(b, s_list, w, d, c, mat):
    bm = b.bm
    rings = []
    for s in s_list:
        (cy, cz), a = mag_frame(s)
        ny, nz = math.cos(a), math.sin(a)        # across the magazine toward the muzzle (perpendicular to its axis)
        sec = [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]
        rings.append([bm.verts.new((x, cy + u * ny, cz + u * nz)) for x, u in sec])
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_magazine(rounds):
    b = kit.Builder()
    end = MAG_LEN[rounds]
    steps = sorted({round(6.0 + k * 10.0, 3) for k in range(int((end - 8.0) // 10.0) + 1)} | {end - 8.0})
    mag_sweep(b, steps, MAG_W, MAG_D, 3.0, "magpoly")
    mag_sweep(b, [0.0, 6.0], MAG_W - 4.0, MAG_D - 3.0, 2.0, "magpoly")                # feed lips
    mag_sweep(b, [end - 8.0, end], MAG_W + 1.2, MAG_D + 1.5, 3.0, "dark")             # the black base plate
    # top round: bullet forward (+Y), brass case
    b.lathe("y", (0, -1.5, -3.6), [(-21.5, 0), (-21.5, 4.8), (11.0, 4.8), (13.0, 3.2), (17.0, 3.0)], seg=8,
            mat="brass")
    b.lathe("y", (0, -1.5, -3.6), [(17.0, 3.0), (22.0, 2.7), (26.5, 1.2), (27.5, 0)], seg=8, mat="copper")
    return b.to_object("556x45Magazine%d_AUG" % rounds)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: Steyr green polymer, black anodised receiver and scope, phosphated barrel, smoke magazine
    "polymer": (84, 90, 74), "grip": (78, 84, 69), "metal": (40, 41, 43), "barrel": (44, 45, 47), "dark": (26, 26, 27),
    "scope": (34, 35, 37), "magpoly": (168, 166, 156), "brass": (150, 118, 62), "copper": (140, 82, 52),
}
rounded_rect = kit.rounded_rect


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "barrel", "dark", "scope", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.93 + 0.14 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    # the photographed gun's receiver and scope are worn silver at their edges; the polymer only lightens
    wear = np.where(np.isin(mat, [MATS.index("metal"), MATS.index("scope")]), 95.0,
                    np.where(is_metal, 60.0, 30.0)) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def pin(col, L, H, sel, cL, cH, r=2.6):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.9)] *= 0.45
    col[sel & (d <= r - 0.9)] *= 0.7
    col[sel & (d <= r - 0.9) & (np.abs(L - cL) < 0.45)] *= 0.5            # slotted screw


def paint_body(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, yy, zz = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - yy, zz + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    poly = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_STOCK - 0.8)
    grip = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_GRIP - 0.8) & (np.abs(x) < W_GRIP + 0.8)
    rcv = (mat == MATS.index("metal")) & side & (np.abs(x) > W_RCV - 0.8)
    # the butt plate seam and the plate, the cheek recess's edge along the top, screws, the sling stud
    col[poly & (np.abs(L - (BUTT_PLATE_L - 0.12 * (140.0 - H))) < 0.7)] *= 0.5
    col[poly & (L > BUTT_PLATE_L - 0.12 * (140.0 - H))] *= 0.85
    col[poly & (np.abs(H - 148.0) < 0.6) & (L > 600.0) & (L < 712.0)] *= 0.72
    col[poly & (np.abs(H - 148.6) < 0.5) & (L > 600.0) & (L < 712.0)] += 10
    for cL, cH in ((600.0, 88.0), (752.0, 9.0)):
        pin(col, L, H, poly, cL, cH, 3.2)
    d = np.hypot(L - 745.0, H - 100.0)
    col[poly & (d < 4.5)] = (120, 120, 118)
    col[poly & (d < 2.4)] = (40, 40, 40)
    # the ejection port on the right: its rim, the open chamber in its front half (AUG_BOLT covers it while the bolt
    # is closed), the bolt carrier's steel side with its lengthwise grooves in the rear half; the left one's blanked
    # plate ribbed
    La, Lb, Ha, Hb = PORT_COVER
    col[poly & right & rounded_rect(L, H, La - 6, Lb + 10, Ha - 1, Hb + 3, 2.0)] *= 0.55
    port = poly & right & rounded_rect(L, H, PORT[0], PORT[1], PORT[2], PORT[3], 1.5)
    chamber = port & (L < PORT_SPLIT)
    col[chamber] = col[chamber] * 0.25 + np.array([4, 4, 5])
    carrier = port & ~chamber
    col[carrier] = np.array(BASE["metal"]) * 1.45          # lit like the plate's face (the port's AO darkens it)
    col[carrier & ((np.abs(H - 118.5) < 0.5) | (np.abs(H - 122.5) < 0.5))] *= 0.6
    col[carrier & (L < PORT_SPLIT + 0.8)] *= 0.5                      # the shadow of the plate's rear edge
    plate = (mat == MATS.index("metal")) & left & (np.abs(x) > W_STOCK)
    col[plate & (np.mod(L, 1.8) < 0.7)] *= 0.6
    d = np.hypot(L - (La + Lb) / 2.0, H - (Ha + Hb) / 2.0)
    col[plate & (d < 3.2)] = (90, 92, 96)
    # the grip's chequered panel
    panel = grip & (H > 14.0) & (H < 92.0) & (L > 446.0 - (H - 14.0) * 0.55 + 6.0) & (L < 472.0)
    chk = (np.mod(L + H, 2.2) < 0.7) | (np.mod(L - H, 2.2) < 0.7)
    col[panel & chk] *= 0.78
    # receiver: the charging handle's slot along the left, the barrel latch, worn top edges
    col[rcv & left & rounded_rect(L, H, 288.0, 396.0, 146.0, 155.0, 3.5)] = 10
    col[rcv & right & rounded_rect(L, H, 262.0, 300.0, 132.0, 141.0, 2.0)] *= 0.55
    for cL in (258.0, 392.0):
        pin(col, L, H, rcv, cL, 128.0, 2.2)
    # scope: the lens faces, the reticle mark on the turret's side
    sc = mat == MATS.index("scope")
    r = np.hypot(x, zz - z(SCOPE_H))
    lens = sc & (np.abs(n[..., 1]) > 0.8) & (r < 12.0) & ((L < 317.0) | (L > 524.0))
    col[lens] = (30, 44, 58)
    col[lens & (r < 6.0) & (r > 4.6)] = (70, 90, 110)
    # trigger guard's moulded STEYR on the left above the grip (as on the photographed gun's stock)
    col[poly & left & kit.text_mask(L, H, "STEYR", 600.0, 120.0, 6.0)] *= 0.72
    # barrel: flash hider prongs' slots, the bore, the lock nut's flats
    bar = mat == MATS.index("barrel")
    rb = np.hypot(x, zz - z(BORE))
    ang = np.mod(np.arctan2(x, zz - z(BORE)) / (2 * math.pi) * 4.0, 1.0)
    col[bar & (L < 27.0) & (rb > 6.5) & (np.abs(ang - 0.25) < 0.08)] = 8
    col[bar & (rb < 3.8) & (L < 1.0)] = 6


def paint_mag(maps, col, rounds):
    """Translucent smoke polymer with the rounds showing through: a staggered column of brass cases (bullets
    forward), the ribs moulded down each side, the round count windows' numbers."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, yy, zz = p[..., 0], p[..., 1], p[..., 2]
    side = (mat == MATS.index("magpoly")) & (np.abs(n[..., 0]) > 0.7) & (np.abs(x) > MAG_W - 0.8)
    s, u = mag_local(yy, zz)
    # rounds lying across the magazine one above the other (4.6 mm apart, staggered 3 mm), bullets forward, a dark
    # line between them; the follower's empty space under the last
    count = int((MAG_LEN[rounds] - 24.0) // 4.6)
    for k in range(count):
        sk = 10.0 + k * 4.6
        off = 1.5 if k % 2 else -1.5
        band = side & (np.abs(s - sk) < 2.3)
        case = band & (u > -24.0 + off) & (u < 6.0 + off)
        col[case] = col[case] * 0.3 + np.array([150, 118, 62]) * 0.62
        col[case & (np.abs(s - sk + 1.0) < 0.6)] += 22                                  # the case's lit top
        tip = band & (np.abs(s - sk) < 1.5) & (u >= 6.0 + off) & (u < 17.0 + off)
        col[tip] = col[tip] * 0.4 + np.array([140, 82, 52]) * 0.55
        col[side & (np.abs(s - sk - 2.3) < 0.45) & (u > -25.0) & (u < 19.0)] *= 0.6
    col[side & ((np.abs(u - 25.0) < 0.8) | (np.abs(u + 25.0) < 0.8))] *= 0.8           # moulded ribs
    # the count moulded near the base, read from the gun's left (the butt to the viewer's right: -u)
    col[side & (n[..., 0] > 0.7) & kit.text_mask(-u, -s, str(rounds), -6.0, -(MAG_LEN[rounds] - 16.0), 6.0)] *= 0.55


def paint(maps, kind):
    p, mat = maps["pos"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body":
        paint_body(maps, col)
    elif kind == "foregrip":
        n = maps["nrm"]
        x, zz = p[..., 0], p[..., 2]
        g = (mat == MATS.index("grip")) & (np.abs(n[..., 1]) < 0.7)
        col[g & (zz < -20.0) & (zz > -100.0) & (np.mod(zz, 3.0) < 1.1)] *= 0.75        # moulded rings
    elif kind == "bolt":
        pass
    elif kind == "carrier":
        # the bolt carrier's side in the port: the bolt head's front edge and the port's two grooves
        n = maps["nrm"]
        L, H = L0 - p[..., 1], p[..., 2] + H0
        face = (n[..., 0] < -0.7) & (np.abs(p[..., 0]) > W_STOCK + 0.2)
        col[face & ((np.abs(H - 118.5) < 0.5) | (np.abs(H - 122.5) < 0.5))] *= 0.6
        col[face & (L < PORT[0] + 2.0)] *= 0.55
    elif isinstance(kind, int):
        paint_mag(maps, col, kind)
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def bake(ob, ctx, size):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    maps = kit.bake_maps(ob, ctx, bake_size)
    if kit.DEBUG:
        kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
    return maps


def texture(maps_list, kinds, size, path):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake_size, bake_size, 3), np.float32)
    cover = np.zeros((bake_size, bake_size), bool)
    for maps, kind in zip(maps_list, kinds):
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake_size // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points
# ==================================================================================================

def side_rail_points():
    """The side rails' points, the same on every AUG (the A3 receivers' left one too): AUG_RAIL_LEFT / _RIGHT have
    their origins on the receiver's faces; GoM's lights sit 0.0007 out from a rail's crossbar faces and its lasers
    0.0018 out and 0.0008 lower (the SCAR's relations: rail_left + 0.0062, rail_right - 0.0073, with GoM's rail
    standing 0.0055 out from its point)."""
    face = (W_RCV + SIDE_RAIL_BASE + SIDE_RAIL_TEETH - 1.0) * K
    ly, lz = round(y(sum(LEFT_RAIL) / 2.0) * K, 4), round(z(LEFT_RAIL_H) * K, 4)
    ry, rz = round(y(sum(RIGHT_RAIL) / 2.0) * K, 4), round(z(RIGHT_RAIL_H) * K, 4)
    return {
        "rail_left": {"offset": [round(W_RCV * K, 4), ly, lz], "rotate": ZERO},
        "light_left": {"offset": [round(face + 0.0007, 4), ly, lz], "rotate": ZERO},
        "rail_right": {"offset": [round(-W_RCV * K, 4), ry, rz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(face + 0.0018), 4), ry, round(rz - 0.0008, 4)], "rotate": ZERO},
    }


def points(bounds):
    hinge = gp(*FG_HINGE)
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(*MAG_LIPS), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-CARRIER_TRAVEL * K, 4) + 0.0, 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-TRAVEL * K, 4) + 0.0, 0.0], "rotate": ZERO},
        "foregrip_deployed": {"offset": hinge, "rotate": ZERO},
        # turned 90 degrees forward about the pin: the grip's foot swings toward the muzzle, under the barrel
        "foregrip_folded": {"offset": hinge, "rotate": [90.0, 0.0, 0.0]},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},                               # every GoM rifle's, scaled
    }
    pts.update(side_rail_points())
    pts["_notes"] = {
        "units": "game units (0.603 of real size, the M16A2's proportion); +Y muzzle, +Z top, +X the gun's left; "
                 "origin = the rear-top of the pistol grip (photo L %.0f, H %.0f)" % (L0, H0),
        "magazine": "556x45Magazine30/42_AUG, origin at their feed lips, inside the well (its mouth L 545-610)",
        "bolt_fired": "AUG_BOLT (the bolt carrier in the ejection port) back %.1f mm real: each shot and held open "
                      "when empty (GoM's Bolt_Fired)" % CARRIER_TRAVEL,
        "handle_back": "AUG_HANDLE (the charging handle) back %.0f mm real, only while racked "
                       "(GunsOfTien.ChargingHandle_Back); the AUG's handle does not reciprocate" % TRAVEL,
        "foregrip": "AUG_FOREGRIP is modelled down with its origin at the hinge pin (photo L %.0f, H %.0f); folded = "
                    "the same node turned 90 degrees forward about X, lying under the barrel" % FG_HINGE,
        "scope": "the integral 1.5x scope is part of AUG_BODY: no scope / top rail points (an optic over it would "
                 "add its stats to the scope's; user, 2026-10-30)",
        "rails": "GoM's optional Picatinny_Rail_Left / _Right, drawn as AUG_RAIL_LEFT (L %.0f-%.0f, H %.1f) and "
                 "AUG_RAIL_RIGHT (L %.0f-%.0f, H %.0f), origins on the receiver's faces (build_rails.py)" % (
                     LEFT_RAIL + (LEFT_RAIL_H,) + RIGHT_RAIL + (RIGHT_RAIL_H,)),
    }
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K}
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
    os.makedirs(TEX_DIR, exist_ok=True)

    body, bolt, handle, fg = build_body(), build_carrier(), build_handle(), build_foregrip()
    mags = [build_magazine(r) for r in MAG_LEN]
    kit.unwrap([body, bolt, handle, fg], 0.005)
    for m in mags:
        kit.unwrap([m], 0.012)
    # the grip is baked alone (its node is at the pin, not in the gun's space); the carrier with the body only (it
    # moves)
    maps = [bake(body, [body, handle], 256), bake(bolt, [body, bolt], 256), bake(handle, [body, handle], 256),
            bake(fg, [fg], 256)]
    texture(maps, ["body", "carrier", "bolt", "foregrip"], 256, os.path.join(TEX_DIR, "AUG.png"))
    for r, m in zip(MAG_LEN, mags):
        texture([bake(m, [m], 128)], [r], 128, os.path.join(TEX_DIR, m.name + ".png"))

    bounds = {o.name: kit.bounds_of(o) for o in (body, bolt, handle, fg)}
    bounds["AUG_BOLT_fired"] = kit.bounds_of(bolt, (0, -CARRIER_TRAVEL * K, 0))
    bounds["AUG_HANDLE_back"] = kit.bounds_of(handle, (0, -TRAVEL * K, 0))
    bounds.update({m.name: kit.bounds_of(m) for m in mags})
    pts = points(bounds)
    bounds["AUG_FOREGRIP_deployed"] = kit.bounds_at(fg, pts["foregrip_deployed"])
    bounds["AUG_FOREGRIP_folded"] = kit.bounds_at(fg, pts["foregrip_folded"])
    for m in mags:
        bounds[m.name + "_fitted"] = kit.bounds_at(m, pts["magazine"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export([body, bolt, handle, fg], FBX_GUN)
    kit.export(mags, FBX_MAGS)
    for name, bb in bounds.items():
        print("AUG %-28s tris %5d  min %s  max %s" % (name, bb["tris"], bb["min"], bb["max"]))


if __name__ == "__main__":
    main()
