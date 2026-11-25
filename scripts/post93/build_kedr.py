"""PP-91 Kedr model and textures for GoM Extension: Guns of Tien, Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_kedr.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_KEDR.fbx   KEDR_BODY, KEDR_BOLT (the bolt's side in the right
                                                            ejection port and the cocking handle on the left),
                                                            KEDR_STOCK_FOLDED / _DEPLOYED (drawn in place)
    M/models_X/weapons/magazines/GunsOfTienPost93_KEDR_magazines.fbx   9x18Magazine20 / 30_KEDR
    M/textures/weapons/GunsOfTienPost93/KEDR.png            256, the gun's four nodes
    M/textures/weapons/GunsOfTienPost93/9x18Magazine<n>_KEDR.png   128 each
    scripts/post93/kedr_points.json                         attachment points (game space)

User, 2026-11-26: "For makarov guns, let's add Skorpion and Kedr". Dragunov's PP-71 of 1970 went into production at
Zlatoust as the PP-91 Kedr in 1994 (the Ministry of the Interior's adoption; every photographed gun is stamped
"ПО ЗМЗ 1994г"), so it is Post-93's. 9x18mm Makarov, closed bolt, about 1000 rounds a minute, 20 and 30-round
magazines, a stock that folds up and over the top. Held like a pistol and holstered, as the MP7 and the TMP.

Measuring photo: zonawar.ru's studio shot on gunrf.ru (raw/gunrf_000.jpg, 2000 px: the LEFT side, muzzle left,
stock open, a 30-round magazine; references/kedr), a true side view: at 3.522 px a mm the muzzle to the hinge knob's
rear is the published 305 mm folded and the open gun 535 (530 published). Traced with trace_outline.py:
kedr_reference_outline.json. Profiles are in that photo's (L, H) mm: L back from the muzzle, H up from the lowest
point (the 30-round magazine's base).

Vitaly Kuzmin's 37 photos (Commons, CC BY-SA 4.0) are sharper but every one is taken at a slant: laid on the studio
photo by the muzzle and the hinge, their magazine catch sits 11 mm and their trigger 13 mm too far forward, and they
show the grip's base and the magazine's back. They are used for what a part is, not for where: the right side (the
ejection port in the cover's right, the selector with its long lever: "OSN Saturn 94-11"), the folded stock (two
struts, one along each edge of the top, and the slotted butt plate hanging in front of the receiver with the barrel
through its slot: "Kedr 01"), the butt plate itself ("Kedr 29"), the top ("Kedr 04").

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): +Y muzzle, +Z top, +X the gun's LEFT, origin at the rear-top of
the pistol grip (here where the hand's web sits under the grip's hump), 0.603 of real size. Held like a pistol, so
the gun's nodes are modelled and baked upright and turned 180 degrees about the bore axis at export with their
points; the magazines stay upright and get TURN at their point.
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_KEDR.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_KEDR_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "kedr_points.json")

K = 0.000603
K_OLD = 0.00072
kit.K = K
MATS = ["steel", "grip", "dark", "bolt", "mag", "brass", "copper"]
kit.MATS[:] = MATS
ZERO = [0.0, 0.0, 0.0]

# photo (L, H) of the model origin: the hollow under the grip's hump. game y = L0 - L, z = H - H0.
L0, H0 = 267.0, 146.0
BORE = 187.25
W_RECV, W_GRIP, W_TOWER = 15.0, 14.0, 7.5
TOP = 211.2                        # the receiver cover's top
PIVOT = (299.0, 203.4)             # the stock's hinge (its knurled knob on the left)
STRUT_X = (9.5, 12.5)              # the stock's two struts, flat strips on edge, |x| from .. to: folded, one along
                                   # each edge of the top with the front sight's hood between them (user, 2026-11-26,
                                   # with a 3D render: "it needs to be left and right"; a single 9 mm bar on the
                                   # right until then); the side views show them as one
STRUT_TOP = 7.8                    # how far the folded strut stands over the cover
MAG = (140.1, 166.0)               # the magazines' feed lips (the middle of their main body; axis straight down)
PORT = (136.0, 184.0, 197.0, 209.0)   # the ejection port in the cover's right: L front, L rear, H low, H high
SLOT = (180.0, 287.0, 193.0, 197.0)   # the cocking slot along the left
BOLT_TRAVEL = (PORT[1] - PORT[0]) / 2.0 - 0.5

# ==================================================================================================
# Profiles (photo L, H mm) off the traced outline and 2x gridded crops of the studio photo
# ==================================================================================================

RECV = [(82.0, 211.0), (289.5, 211.5), (290.0, 168.7), (256.4, 167.2), (248.0, 154.7), (211.7, 154.0),
        (178.6, 153.6), (166.5, 153.6), (166.5, 138.5), (165.5, 136.8), (126.8, 136.0), (123.2, 139.1),
        (122.9, 150.2), (121.0, 154.2), (118.7, 156.2), (113.3, 157.9), (90.3, 161.6), (83.2, 163.3), (82.0, 166.7)]
# the front sight's bracket ahead of the receiver, round the barrel: its hood stands 18 mm over the cover
TOWER = [(66.7, 196.5), (67.3, 199.3), (71.0, 214.9), (72.7, 224.3), (73.8, 227.1), (76.9, 228.8), (81.2, 228.8),
         (83.2, 227.4), (86.0, 226.6), (88.6, 223.7), (89.2, 221.7), (90.9, 219.2), (90.6, 217.5), (87.4, 217.2),
         (86.9, 215.5), (88.0, 214.6), (90.9, 214.4), (91.7, 213.5), (94.0, 212.7), (94.8, 211.0), (98.0, 210.7),
         (98.0, 200.0), (84.0, 200.0), (84.0, 166.7), (81.5, 166.7), (81.5, 168.1), (79.8, 170.1), (75.8, 173.2),
         (69.6, 177.7), (66.7, 179.2)]
TOWER_HOLE = (77.5, 212.7, 4.0)    # the hood's round window: L, H, radius (see-through on the real gun)
BRACKET = [(286.0, 212.0), (293.3, 220.3), (297.0, 220.3), (302.7, 220.0), (305.2, 208.7), (306.1, 204.1),
           (304.9, 197.3), (303.5, 191.6), (300.5, 184.0), (297.3, 174.6), (294.7, 171.2), (288.2, 166.4),
           (286.0, 166.4)]
REAR_SIGHT = [(293.3, 219.5), (293.8, 231.5), (295.0, 233.1), (296.1, 232.3), (296.4, 219.5)]
GRIP = [(211.7, 160.0), (211.5, 130.0), (213.5, 129.5), (220.0, 125.8), (222.9, 122.4), (224.3, 118.4),
        (224.3, 114.7), (222.6, 110.2), (223.4, 105.3), (227.4, 101.6), (229.7, 95.7), (229.7, 92.0), (228.6, 88.0),
        (229.4, 83.5), (234.2, 78.1), (235.7, 74.7), (235.4, 69.3), (233.7, 66.2), (232.0, 64.2), (232.3, 61.3),
        (234.8, 59.1), (240.5, 57.9), (245.6, 59.6), (254.1, 62.5), (276.0, 71.5), (280.8, 73.5), (286.5, 76.9),
        (289.6, 80.1), (289.6, 85.5), (265.8, 132.9), (265.2, 134.6), (265.2, 140.5), (268.0, 146.2), (275.4, 152.2),
        (276.5, 156.2), (276.3, 162.4), (276.5, 172.0), (254.0, 172.0), (246.0, 160.0)]
GUARD_IN = [(178.5, 156.0), (176.5, 152.5), (173.8, 149.9), (172.1, 146.8), (170.4, 140.8), (168.9, 137.7),
            (169.4, 134.0), (170.9, 130.9), (173.2, 128.6), (176.0, 127.2), (186.0, 126.9), (197.9, 126.6),
            (206.0, 128.4), (213.0, 130.7)]
GUARD_T = 2.1
TRIGGER = [(188.5, 156.0), (188.5, 153.3), (191.4, 151.3), (193.4, 149.1), (195.9, 144.2), (197.0, 140.3),
           (197.3, 135.4), (196.8, 131.5), (196.2, 130.3), (196.5, 129.2), (197.6, 129.5), (198.7, 130.6),
           (200.2, 136.3), (200.2, 142.8), (198.7, 149.6), (197.3, 153.3), (197.3, 156.0)]
HANDLE = [(171.8, 195.8), (171.8, 201.0), (173.5, 202.7), (176.5, 202.7), (180.3, 199.5), (180.3, 195.8)]
MAG_CATCH = (154.9, 165.5, 147.4, 154.2)
SELECTOR = ((178.0, 177.0), (207.0, 158.5))      # on the right: its boss, the tip of its lever (at safe)
AXIS_BOSS = (241.5, 170.0)                       # the selector's axis on the left, in its pressed dish
LATCH = (241.5, 250.5, 218.9)                    # the folded strut's catch on the cover
RIVETS = [(111.0, 190.5), (118.7, 176.3), (144.5, 177.2), (174.9, 170.0), (279.9, 186.0), (279.9, 174.0)]
# the stock open (studio photo): the strut's two edges down to the butt, and the butt plate standing up from its end
STRUT_OPEN = [(293.0, 200.0), (296.0, 207.0), (302.0, 207.0), (305.8, 189.4), (328.5, 181.1), (360.9, 168.1),
              (394.9, 155.0), (443.2, 135.4), (494.3, 118.4), (497.5, 118.7), (497.5, 105.0), (492.9, 105.9),
              (477.6, 113.6), (424.8, 131.5), (382.7, 146.8), (333.9, 163.5), (298.1, 176.6), (294.0, 186.0)]
CHEEK_OPEN = [(494.6, 105.9), (496.6, 118.7), (513.6, 166.1), (516.7, 172.6), (520.4, 174.9), (526.0, 175.4),
              (533.5, 174.0), (535.2, 168.1), (528.7, 101.9), (520.2, 98.2), (510.2, 100.2)]
PLATE_OPEN = [(526.2, 102.5), (528.7, 101.9), (535.2, 168.1), (534.6, 175.4), (532.0, 175.8)]
PLATE_OPEN_END = [(526.2, 102.5), (528.7, 101.9), (530.3, 118.0), (527.8, 118.5)]
ROOF_OPEN = [(494.6, 105.9), (510.2, 100.2), (520.2, 98.2), (528.7, 101.9), (528.0, 105.2), (520.0, 101.6),
             (510.6, 103.6), (496.0, 109.2)]
# folded (Kuzmin's "Kedr 01", laid on the studio photo by the muzzle and the bore): the plate hangs in front of the
# front sight's bracket, its wide end up at the strut's front
CHEEK_FOLDED = [(40.5, 216.0), (72.0, 216.0), (69.5, 180.0), (61.5, 152.0), (59.6, 146.5), (57.2, 148.0)]
PLATE_FOLDED = [(40.5, 216.5), (43.1, 216.5), (59.8, 148.0), (57.2, 148.0)]
PLATE_FOLDED_END = [(40.5, 216.5), (43.1, 216.5), (46.8, 201.5), (44.2, 201.5)]


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="steel", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def gp(L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round((L0 - L) * K, 4) + 0.0, round((H - H0) * K, 4) + 0.0]


def circle(cL, cH, r, n=14):
    return [(cL + r * math.cos(2 * math.pi * i / n), cH + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    y = lambda L: L0 - L  # noqa: E731
    zb = BORE - H0
    # the barrel, its collar in the front sight's bracket
    b.lathe("y", (0, 0, zb), [(y(86.0), 0), (y(86.0), 7.6), (y(63.6), 7.6), (y(63.0), 6.35), (y(1.4), 6.35),
                              (y(0.4), 5.3), (y(0.4), 0)], seg=20, mat="steel", phase=0.5)
    slab(b, RECV, half=W_RECV, bevel=1.4)
    slab(b, TOWER, [circle(*TOWER_HOLE)], half=W_TOWER, bevel=0.9)
    # the front sight's post inside the hood
    b.lathe("z", (0, y(79.5), 0), [(213.0 - H0, 1.4), (225.5 - H0, 1.0), (225.5 - H0, 0)], seg=8, mat="steel")
    slab(b, BRACKET, half=W_RECV - 1.0, bevel=1.2)
    slab(b, REAR_SIGHT, half=3.2, bevel=0.4)
    box(b, LATCH[0], LATCH[1], TOP - 1.0, LATCH[2], -2.5, 2.5, bevel=0.8)
    # the cover's raised guide over the cocking slot, the magazine catch and the hinge's knurled knob, all on the
    # left; the selector's axis in its dish there
    box(b, 151.0, 259.0, 197.0, 203.0, W_RECV - 0.6, W_RECV + 1.1, bevel=0.5)
    c = MAG_CATCH
    box(b, c[0], c[1], c[2], c[3], W_RECV - 0.6, W_RECV + 1.9, mat="dark", bevel=0.6)
    box(b, 280.5, 287.0, 197.0, 204.0, W_RECV - 0.6, W_RECV + 1.3, mat="dark", bevel=0.5)      # the cover's catch
    b.lathe("x", (0, y(PIVOT[0]), PIVOT[1] - H0), [(W_RECV - 2.0, 0), (W_RECV - 2.0, 6.2), (W_RECV + 4.0, 6.2),
                                                   (W_RECV + 4.7, 5.4), (W_RECV + 4.7, 0)], seg=16, mat="dark")
    b.lathe("x", (0, y(PIVOT[0]), PIVOT[1] - H0), [(-(W_RECV + 1.2), 0), (-(W_RECV + 1.2), 3.6),
                                                   (-(W_RECV - 2.0), 3.6), (-(W_RECV - 2.0), 0)], seg=12, mat="steel")
    b.lathe("x", (0, y(AXIS_BOSS[0]), AXIS_BOSS[1] - H0), [(W_RECV - 0.6, 0), (W_RECV - 0.6, 3.3),
                                                           (W_RECV + 1.2, 3.3), (W_RECV + 1.6, 2.7),
                                                           (W_RECV + 1.6, 0)], seg=12, mat="steel")
    # the selector on the right: a round boss and its long lever lying back to the safe mark
    (pL, pH), (tL, tH) = SELECTOR
    w = W_RECV
    b.lathe("x", (0, y(pL), pH - H0), [(-(w + 3.0), 0), (-(w + 3.0), 7.4), (-(w + 2.2), 8.4), (-(w - 0.6), 8.4),
                                       (-(w - 0.6), 0)], seg=16, mat="steel")
    d = math.hypot(tL - pL, tH - pH)
    ux, uy = (tL - pL) / d, (tH - pH) / d

    def lv(a, across):
        return pL + ux * a + uy * across, pH + uy * a - ux * across

    lever = [lv(0.0, 6.0), lv(10.0, 5.2), lv(d - 9.0, 2.6), lv(d - 6.5, 4.2), lv(d - 0.8, 4.2), lv(d, 3.2),
             lv(d, -3.2), lv(d - 0.8, -4.2), lv(d - 6.5, -4.2), lv(d - 9.0, -3.0), lv(10.0, -5.4), lv(0.0, -6.0)]
    slab(b, lever, half=1.0, bevel=0.35, mat="steel", x0=-(w + 1.2))
    # the plastic grip, the guard's strap and the trigger
    slab(b, GRIP, half=W_GRIP, bevel=4.0, res=1, mat="grip")
    gi = GUARD_IN
    go = []
    for i, (L, H) in enumerate(gi):
        (ax, ay), (cx, cy) = gi[max(i - 1, 0)], gi[min(i + 1, len(gi) - 1)]
        dx, dy = cx - ax, cy - ay
        dd = math.hypot(dx, dy)
        go.append((L + GUARD_T * dy / dd, H - GUARD_T * dx / dd))
    b.strip(PL(go), PL(gi), -5.5, 5.5, mat="steel", bevel=0.4)
    slab(b, TRIGGER, half=2.4, bevel=0.6, mat="dark")
    return b.to_object("KEDR_BODY")


def build_bolt():
    """The bolt's side in the right ejection port's front half (bolt_fired slides it back over the rear half, as
    the Uzis' and the TMP's) and the cocking handle on the left, fixed to the bolt."""
    La, Lb, Ha, Hb = PORT
    b = kit.Builder()
    box(b, La + 1.0, (La + Lb) / 2.0 - 0.3, Ha + 1.0, Hb - 1.0, -(W_RECV + 0.35), -(W_RECV - 0.4), mat="bolt",
        bevel=0.1)
    slab(b, HANDLE, half=5.0, bevel=0.9, mat="bolt", x0=W_RECV + 4.0)
    return b.to_object("KEDR_BOLT")


def butt(b, cheek, plate, plate_end, roof=None):
    """The slotted butt plate: two thin cheeks, the plate's two tines beside its slot, the solid end by the hinge."""
    for xs in (1.0, -1.0):
        slab(b, cheek, half=0.9, bevel=0.3, x0=xs * 12.1)
        slab(b, plate, half=3.2, bevel=0.5, x0=xs * 9.8)
    slab(b, plate_end, half=13.0, bevel=0.5)
    if roof:
        slab(b, roof, half=13.0, bevel=0.8)


def build_stock_folded():
    """The two struts along the top's edges with their rear ends down in the hinge, the butt plate hanging in
    front."""
    b = kit.Builder()
    for xa, xb in ((STRUT_X[0], STRUT_X[1]), (-STRUT_X[1], -STRUT_X[0])):
        box(b, 66.0, 298.0, TOP - 0.8, TOP + STRUT_TOP, xa, xb, bevel=0.8)
        box(b, 292.5, 300.5, PIVOT[1] - 3.0, TOP + STRUT_TOP, xa, xb, bevel=0.8)
    butt(b, CHEEK_FOLDED, PLATE_FOLDED, PLATE_FOLDED_END)
    # the plate's wide end over the strut's front, with its knurled catch
    box(b, 40.5, 69.0, 214.5, TOP + STRUT_TOP, -13.0, 13.0, bevel=1.0)
    box(b, 46.0, 56.0, TOP + STRUT_TOP - 0.4, TOP + STRUT_TOP + 1.2, -5.0, 5.0, mat="dark", bevel=0.5)
    return b.to_object("KEDR_STOCK_FOLDED")


def build_stock_deployed():
    b = kit.Builder()
    xa, xb = STRUT_X
    for xs in (1.0, -1.0):
        slab(b, STRUT_OPEN, half=(xb - xa) / 2.0, bevel=0.8, x0=xs * (xa + xb) / 2.0)
    butt(b, CHEEK_OPEN, PLATE_OPEN, PLATE_OPEN_END, ROOF_OPEN)
    return b.to_object("KEDR_STOCK_DEPLOYED")


MAG_LEN = {20: 122.0, 30: 166.0}   # feed lips to base: 136 mm of the 30 hangs under the housing (4.4 mm a round)
MAG_W, MAG_D = 10.5, 13.5          # the main body: half width, half depth (27 mm front to back)
SPINE_W, SPINE_D = 7.0, 8.2        # the narrower spine down its back
MAG_BASE = 3.0


def mag_name(r):
    return "9x18Magazine%d_KEDR" % r


def build_magazine(r):
    """Origin at the feed lips (top centre of the main body); the steel body straight down with two pressed ribs a
    side, the narrower spine down its back, a base plate a little proud, the top round with its bullet forward."""
    b = kit.Builder()
    L = MAG_LEN[r]
    b.box(-MAG_W, MAG_W, -MAG_D, MAG_D, -(L - MAG_BASE), -6.0, mat="mag", bevel=1.0)
    b.box(-SPINE_W, SPINE_W, -MAG_D - SPINE_D, -MAG_D + 1.5, -(L - MAG_BASE), -10.0, mat="mag", bevel=0.8)
    b.box(-MAG_W + 2.4, MAG_W - 2.4, -MAG_D + 1.5, MAG_D - 3.5, -6.5, 0.0, mat="mag", bevel=0.7)
    b.box(-MAG_W - 0.8, MAG_W + 0.8, -MAG_D - SPINE_D - 0.8, MAG_D + 1.5, -L, -(L - MAG_BASE), mat="mag", bevel=0.8)
    for xs in (1.0, -1.0):
        for yc in (-4.6, 4.4):
            b.box(xs * (MAG_W - 0.3), xs * (MAG_W + 0.7), yc - 1.3, yc + 1.3, -(L - MAG_BASE - 10.0), -38.0, mat="mag",
                  bevel=0.45)
    b.lathe("y", (0, -1.0, -4.2), [(-10.5, 0), (-10.5, 4.95), (4.5, 4.95), (5.0, 4.6)], seg=8, mat="brass")
    b.lathe("y", (0, -1.0, -4.2), [(5.0, 4.6), (8.5, 4.5), (12.5, 2.9), (14.2, 0)], seg=8, mat="copper")
    return b.to_object(mag_name(r))


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: black-painted steel a little lighter than GoM's MP5K, the textured black grip, the bolt worn grey
    "steel": (50, 51, 57), "grip": (34, 34, 36), "dark": (30, 30, 33), "bolt": (84, 85, 88),
    "mag": (56, 57, 62), "brass": (150, 118, 62), "copper": (140, 82, 52),
}
rounded_rect = kit.rounded_rect


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "dark", "bolt", "mag", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.88 + 0.24 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.84 + 0.32 * streak[is_metal])[..., None]
    col *= (0.96 + 0.12 * np.clip(n[..., 2], -1, 1))[..., None]
    col *= (0.86 + 0.28 * np.clip((p[..., 2] + 90.0) / 160.0, 0.0, 1.0))[..., None]     # lighter towards the top
    occ = (0.62 + 0.38 * np.clip(ao_b, 0, 1) ** 1.5) * (0.66 + 0.34 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 110.0, 55.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.05])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def rivet(col, L, H, sel, cL, cH, r=1.9):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r + 0.8) & (d >= r)] *= 0.55
    col[sel & (d < r)] += 46


def ribs(col, sel, coord, pitch, dark=0.55, light=6.0):
    col[sel & (np.mod(coord, pitch) < pitch * 0.4)] *= dark
    col[sel & (np.mod(coord, pitch) >= pitch * 0.4)] += light


def segment(L, H, a, b):
    """Distance of (L, H) from the segment a-b."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    t = np.clip(((L - ax) * dx + (H - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
    return np.hypot(L - ax - t * dx, H - ay - t * dy)


def paint_body(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    side = left | right
    steel = mat == MATS.index("steel")
    recv = steel & side & (np.abs(x) > W_RECV - 0.6) & (np.abs(x) < W_RECV + 0.5) & (L > 82.0) & (L < 290.5)
    # the seam between the cover and the receiver ahead of the slot; the cocking slot along the left
    col[recv & (np.abs(H - 192.8) < 0.5) & (L < 152.0)] *= 0.5
    sa, sb, sl, sh = SLOT
    col[recv & left & (L > sa) & (L < sb) & (H > sl) & (H < sh)] = 9
    col[recv & right & (np.abs(H - 192.8) < 0.5) & (L > PORT[1])] *= 0.5
    # the pressed belt round the receiver's lower edge: a lighter crest a few millimetres inside the edge
    belt = [(84.0, 170.5), (123.0, 171.5), (140.0, 170.5), (154.0, 168.0), (167.0, 162.5), (178.5, 158.5),
            (246.0, 158.5), (254.5, 170.5), (288.0, 172.0)]
    d = np.minimum.reduce([segment(L, H, a, b) for a, b in zip(belt, belt[1:])])
    col[recv & (d < 0.7)] += 30
    col[recv & (d >= 0.7) & (d < 1.5) & (H < 175.0)] *= 0.7
    for cL, cH in RIVETS:
        rivet(col, L, H, recv, cL, cH)
    rivet(col, L, H, recv, 162.0, 165.8, r=1.2)
    # the axis' pressed dish on the left; the selector's three marks on the right
    d = np.hypot(L - AXIS_BOSS[0], H - AXIS_BOSS[1])
    col[recv & left & (d < 6.6) & (d > 5.6)] *= 0.55
    col[recv & left & (d <= 5.6) & (d > 3.4)] *= 0.8
    for cL, cH in ((215.5, 185.6), (215.5, 173.0), (215.5, 166.5)):          # the auto, single and safe marks
        col[recv & right & (np.hypot(L - cL, H - cH) < 1.0)] = 150
    # the ejection port on the right: dark inside (the KEDR_BOLT plate covers its front half)
    La, Lb, Ha, Hb = PORT
    port = recv & right & rounded_rect(L, H, La, Lb, Ha, Hb, 2.0)
    col[port] = 11
    # the magazine catch's and the hinge knob's chequering
    dark = mat == MATS.index("dark")
    col[dark & (np.abs(n[..., 0]) > 0.7) & ((np.mod(L, 1.6) < 0.6) | (np.mod(H, 1.6) < 0.6))] *= 0.55
    # the two holes low in the front sight's bracket (not see-through: the barrel's collar is behind them)
    tower = steel & side & (np.abs(x) > W_TOWER - 0.6) & (np.abs(x) < W_TOWER + 0.5) & (L < 84.0)
    col[tower & (np.hypot(L - 76.1, H - 200.6) < 3.0)] = 12
    col[tower & (np.hypot(L - 79.6, H - 175.8) < 1.9)] = 12
    # the muzzle's bore
    r = np.hypot(x, z - (BORE - H0))
    col[steel & (L < 1.2) & (r < 3.7)] = 6
    # the grip: the chequered panel on each side, the base plate's line, a soft sheen on the textured plastic
    grip = mat == MATS.index("grip")
    gs = grip & side
    a, b_, c, e = (233.0, 128.9), (253.5, 130.3), (276.3, 84.3), (247.9, 75.0)

    def inside(p0, p1):                                   # left of the edge p0 -> p1 (the panel's inside)
        return (p1[0] - p0[0]) * (H - p0[1]) - (p1[1] - p0[1]) * (L - p0[0]) < 0

    panel = gs & inside(a, b_) & inside(b_, c) & inside(c, e) & inside(e, a)
    u, v = L * 0.42 + H * 0.9, L * 0.9 - H * 0.42
    col[panel] *= 0.8
    col[panel & ((np.mod(u, 2.6) < 0.9) | (np.mod(v, 2.6) < 0.9))] *= 0.55
    base = segment(L, H, (236.0, 62.5), (287.5, 83.5))
    col[gs & (base < 0.6)] *= 0.5
    col[gs] += (8.0 * kit.vnoise(p, 1.2, 9))[gs][..., None]


def paint_bolt(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    L, H = L0 - p[..., 1], p[..., 2] + H0
    plate = (mat == MATS.index("bolt")) & (n[..., 0] < -0.7)
    mid = (PORT[2] + PORT[3]) / 2.0
    col[plate & (np.abs(H - mid) < 0.5)] *= 0.6
    col[plate & (L > (PORT[0] + PORT[1]) / 2.0 - 1.6)] *= 0.55


def paint_stock(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    dark = mat == MATS.index("dark")
    ribs(col, dark, p[..., 1], 1.4, 0.6, 8.0)


def paint_mag(maps, col, r):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, z = p[..., 0], p[..., 2]
    back = MAG_LEN[r] + z
    side = np.abs(n[..., 0]) > 0.7
    body = (mat == MATS.index("mag")) & side & (np.abs(x) > MAG_W - 0.6)
    for face, uu in ((body & (n[..., 0] > 0.7), p[..., 1]), (body & (n[..., 0] < -0.7), -p[..., 1])):
        col[face & kit.text_mask(uu, back, str(r), -9.5, MAG_BASE + 4.0, 4.4)] += 34


def paint(maps, kind):
    p, mat = maps["pos"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body":
        paint_body(maps, col)
    elif kind == "bolt":
        paint_bolt(maps, col)
    elif kind == "stock":
        paint_stock(maps, col)
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


def repack(objects, shrink, margin):
    """Pack the objects' UV islands again with the `shrink` objects' islands scaled down first and islands turned
    by quarter turns only (build_skorpion.py's: at 256 px an island at an odd angle turns straight lines into
    staircases)."""
    for o, f in shrink.items():
        for d in o.data.uv_layers.active.data:
            d.uv = (d.uv[0] * f, d.uv[1] * f)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, rotate_method='CARDINAL', margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


# ==================================================================================================
# Attachment points
# ==================================================================================================

def weighted_normals(objects):
    """Vertex normals weighted by face area, sharp edges kept: a rounded edge (two 22.5 degree steps, under the
    kit's 35 degree sharp angle) otherwise tilts the normals round a large flat face, and its triangles then shade
    as a fan of light and dark wedges (seen on both grips' sides)."""
    for ob in objects:
        mod = ob.modifiers.new("weighted", 'WEIGHTED_NORMAL')
        mod.mode = 'FACE_AREA'
        mod.weight = 100
        mod.keep_sharp = True
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=mod.name)


def points(bounds):
    pts = {
        "muzzle": {"offset": gp(0.4, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(*MAG), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-BOLT_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    notes = {
        "magazine": "9x18Magazine20 / 30_KEDR hang straight down from here (their feed lips)",
        "bolt_fired": "KEDR_BOLT (the bolt's side in the right ejection port, the cocking handle on the left) back "
                      "%.1f mm real: each shot and held open when empty (GoM's Bolt_Fired)" % BOLT_TRAVEL,
        "stocks": "KEDR_STOCK_FOLDED / _DEPLOYED are drawn in place (no point)",
    }
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["magazine"]["rotate"] = list(kit.TURN)
    pts["world"] = {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": ZERO}
    pts["_notes"] = dict(notes, units="game units (0.603 of real size, the M16A2's proportion); +Y muzzle; held like "
                         "a pistol, so modelled upside down as GoM's MP5K / MAC-10: +Z the gun's BOTTOM, +X its RIGHT; "
                         "origin = the hollow under the grip's hump (photo L %.0f, H %.0f)" % (L0, H0))
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K}
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

    body, bolt = build_body(), build_bolt()
    folded, deployed = build_stock_folded(), build_stock_deployed()
    gun = [body, bolt, folded, deployed]
    mags = [build_magazine(r) for r in MAG_LEN]
    weighted_normals(gun + mags)
    kit.unwrap(gun, 0.006)
    repack(gun, {folded: 0.7, deployed: 0.7}, 0.006)
    for m in mags:
        kit.unwrap([m], 0.012)
        repack([m], {}, 0.012)
    # the bolt and each stock are baked with the body only (they move or swap)
    maps = [bake(body, [body, bolt, folded], 256), bake(bolt, [body, bolt], 256),
            bake(folded, [body, folded], 256), bake(deployed, [body, deployed], 256)]
    texture(maps, ["body", "bolt", "stock", "stock"], 256, os.path.join(TEX_DIR, "KEDR.png"))
    for r, m in zip(MAG_LEN, mags):
        texture([bake(m, [m], 128)], [r], 128, os.path.join(TEX_DIR, m.name + ".png"))

    for o in gun:                                      # held like a pistol: turned 180 degrees about the bore
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in gun}
    bounds["KEDR_BOLT_fired"] = kit.bounds_of(bolt, (0, -BOLT_TRAVEL * K, 0))
    pts = points(bounds)
    pts["_mags"] = {m.name: kit.bounds_of(m) for m in mags}
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export(mags, FBX_MAGS)
    for name, bd in list(bounds.items()) + list(pts["_mags"].items()):
        print("%-26s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
