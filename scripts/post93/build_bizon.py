"""PP-19 Bizon family models and textures for GoM Extension: Guns of Tien, Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_bizon.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_BIZON.fbx   BIZON_BODY (PP-19 Bizon, 9x18: no stock, an end cap on
                                                             the receiver, the slotted compensator), BIZON201_BODY
                                                             (Bizon-2-01, 9x19: the barrel's threaded tip out of the
                                                             front sight for the 9x19 mount, the AKS-74 hinge),
                                                             BIZON207_BODY (Bizon-2-07, 7.62x25: the barrel 115 mm
                                                             longer out of a railed handguard, a box magazine well,
                                                             a fixed AK-74-style stock), BIZON_BOLT (the AK carrier's
                                                             handle on the right), BIZON_STOCK_FOLDED / _DEPLOYED
                                                             (the AKS-74 stock of the -2-01, drawn in place)
    M/models_X/weapons/magazines/GunsOfTienPost93_BIZON_magazines.fbx  9x18Magazine64_BIZON, 9x19Magazine53_BIZON,
                                                             762x25Magazine45_BIZON (helicals, one shape),
                                                             762x25Magazine35_BIZON (the -07's curved box)
    M/textures/weapons/GunsOfTienPost93/BIZON.png            512, the bodies, bolt and stocks
    M/textures/weapons/GunsOfTienPost93/<magazine>.png       128 each
    scripts/post93/bizon_points.json                         attachment points (game space)

User, 2026-11-27 (TODO.md item 2): four guns, the three Bizons on one receiver here and the Vityaz on its own.
Agreed line-up: PP-19 Bizon (9x18, stockless with an end cap, its own compensator), Bizon-2-01 (9x19, AK folding
stock, the 9x19 muzzle family), Bizon-2-07 (7.62x25, a fixed AK-74-style polymer stock, a barrel lengthened to
345 mm "call of duty longer barrel" style out past an aftermarket railed handguard with integrated top and side
rails and no bottom rail, the real 35-round box and an invented 45-round helical); all two-handed, none holstered.

Measuring photo: Chester County Armory's studio shot of a Bizon on Russian factory parts (references/bizon/raw/
cca_007.jpg, 1674 px, the RIGHT side, muzzle right, stock folded out of sight on the left, a 64-round helical in),
traced with trace_outline.py at the published 425 mm folded length (3.193 px a mm); its grip, receiver and pistol
grip proportions read true (the same dealer's cca_000, stock open, is foreshortened 0.88 vertically: the gun lies on
the table and the camera looks down; only the stock's shape is taken from it, its heights scaled by 165 / 146).
Profiles are in that photo's (L, H) mm: L back from the muzzle tip, H up from the grip's base.

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): +Y muzzle, +Z top, +X the gun's LEFT, 0.603 of real size.
Origin where GoM's AKS-74U has it against its trigger and bore (build_9a91.py): the trigger blade 109.5 mm real
ahead of the origin, the bore 24.5 mm over it, so the Bizons sit in the rifle clips as GoM's AKs do.
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_BIZON.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_BIZON_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "bizon_points.json")

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "grip", "dark", "bolt", "poly", "rail", "mag", "brass", "copper"]
kit.MATS[:] = MATS
kit.FONT.setdefault("5", ["111", "100", "111", "001", "111"])
kit.FONT.setdefault("8", ["111", "101", "111", "101", "111"])
kit.FONT.setdefault("9", ["111", "101", "111", "001", "111"])
ZERO = [0.0, 0.0, 0.0]

BORE = 128.7
TRIGGER_L = 345.0                  # the trigger blade's middle
ORIGIN_TO_TRIGGER = 0.066 / K      # GoM's AKS-74U: 109.5 mm real
L0 = TRIGGER_L + ORIGIN_TO_TRIGGER
H0 = BORE - 0.0148 / K

W_RECV, W_COVER, W_HG, W_FSB, W_TOWER, W_GRIP, W_CATCH = 12.5, 12.0, 15.0, 10.5, 6.0, 13.5, 10.0
HELIX_R, HELIX_H = 26.3, 90.5      # the helical: radius, axis H
HELIX_L = (53.0, 278.0)            # its front face, its rear face (against the catch housing)
MAG_PT = (278.0, 116.5)            # the helicals' point: their rear face's top
LONG = 115.0                       # the -2-07's barrel: 345 mm against the photo gun's 230
# the -2-07's box: the middle of its feed lips (receiver bottom), L, H; front to back, side to side. Overlaid on
# vpk_000 (2026-11-27, tmp/bizon/vpk000_trace.json, scaled by the trigger guard): 37-38 mm deep (it was 31, too short
# for a 35 mm round), its well from L 256 to the guard
BOX_LIPS = (277.0, 100.0)
BOX_D, BOX_W = 38.0, 22.0
CARRIER_TRAVEL = 70.0

# ==================================================================================================
# Profiles (photo L, H mm), read off 5-8 px a mm gridded crops of cca_007 (tmp/bizon/c_*.png)
# ==================================================================================================

RECV = [(236.0, 100.0), (423.0, 100.0), (423.0, 136.0), (421.5, 139.0), (420.0, 141.0), (418.3, 144.2),
        (415.8, 147.5), (412.5, 151.3), (408.3, 155.0), (404.2, 160.0), (400.0, 163.7), (395.8, 165.3),
        (300.0, 165.5), (258.0, 165.5), (236.0, 165.5)]
# the recoil spring guide's button, through the cover's rounded end (cca_007)
COVER_BUTTON = [(415.0, 146.0), (418.3, 147.5), (417.1, 152.1), (414.2, 153.3), (411.3, 152.9), (410.0, 151.5)]
REAR_SIGHT = [(212.0, 119.0), (236.0, 119.0), (236.0, 166.0), (232.0, 169.0), (214.0, 169.0), (212.0, 166.0)]
LEAF = [(207.0, 168.5), (236.0, 168.5), (236.5, 171.5), (233.0, 172.5), (207.0, 171.5)]
SLIDER = [(209.5, 165.0), (216.5, 165.0), (217.0, 176.0), (213.0, 178.0), (209.0, 176.0)]
HANDGUARD = [(62.0, 163.0), (62.0, 127.0), (66.0, 122.0), (75.0, 118.5), (212.0, 118.0), (212.0, 164.0)]
HG_SLOTS = [(72.0, 90.0), (104.0, 121.0), (137.0, 154.0)]     # the three slots, L; H 141 .. 146.5
HG_SLOT_H = (141.0, 146.5)
FSB = [(40.0, 119.0), (62.0, 119.0), (62.0, 141.0), (40.0, 141.0)]
TOWER = [(42.0, 141.0), (42.0, 171.0), (44.0, 175.5), (48.0, 177.8), (53.0, 177.2), (56.0, 173.0), (57.0, 168.0),
         (59.0, 155.0), (61.0, 141.0)]
TOWER_HOLE = [(46.5, 144.0), (56.0, 144.0), (56.5, 152.5), (46.5, 153.0)]
GRIP = [(361.0, 100.5), (361.0, 92.0), (363.5, 78.0), (367.5, 62.0), (373.0, 44.0), (378.5, 28.0), (382.0, 18.0),
        (381.5, 10.0), (383.5, 3.0), (390.0, 0.5), (405.0, 0.0), (418.0, 1.5), (423.5, 6.0), (424.0, 13.0),
        (421.0, 22.0), (416.0, 40.0), (411.0, 60.0), (407.5, 78.0), (406.0, 92.0), (409.0, 100.5)]
GUARD_IN = [(299.5, 76.5), (301.5, 74.5), (306.0, 72.6), (320.0, 70.6), (338.0, 68.8), (351.0, 68.2), (356.0, 69.5),
            (359.0, 73.5), (360.3, 80.0), (360.8, 90.0), (361.0, 100.5)]
GUARD_T = 2.3
TRIGGER = [(346.0, 100.0), (348.5, 93.0), (347.0, 86.5), (343.0, 81.0), (337.5, 77.5), (334.0, 76.8), (334.5, 78.0),
           (339.5, 81.2), (343.5, 86.0), (345.0, 92.0), (343.0, 100.0)]
CATCH = [(278.0, 104.0), (300.0, 104.0), (300.0, 76.0), (296.5, 72.0), (281.0, 72.0), (278.0, 76.0)]
CATCH_LEVER = [(289.0, 74.0), (293.5, 74.0), (293.5, 63.0), (291.5, 61.5), (289.0, 63.0)]
HANDLE = (296.0, 141.5)            # the charging handle's knob on the right (L, H)
SELECTOR = ((368.0, 124.5), (302.0, 132.5))   # its pivot, the lever's front tip (right side)
SLING_PLATE = [(410.0, 113.0), (424.0, 113.0), (424.0, 123.5), (410.0, 123.5)]
RIVETS = [(256.0, 128.0), (241.0, 128.0), (318.0, 110.0), (325.0, 103.5), (300.0, 118.0), (383.0, 109.0),
          (389.0, 121.0), (420.5, 130.5), (420.5, 104.5)]
# the AKS-74 stock off cca_000 (heights x 165 / 146 about the grip's base), the -2-01 only
STOCK_SCALE_H = 165.0 / 146.0
# the stock's hinge pin (vertical axis), L, H: at the receiver's rear face, where the open butt (L 660, the
# published 660 mm) folds to commons_040's (L 185)
HINGE = (422.5, 124.0)
# its length behind the hinge x 0.97 (2026-11-27): the published 660 mm open (PP-19, compensator to butt), where it
# made 667; cca_000's overlay had the butt 8-10 mm long too (tmp/bizon/cca000s.jpg)
STOCK_TUBE = ((440.0, 124.0), (647.0, 119.3), 7.8)      # the top tube: from, to, radius
# the butt plate and the strut off cca_019 (the stock's straight side view, 3.54 px a mm by the stock's length):
# the plate's rear edge falls nearly straight, its front edge curves down into the strut (no forward toe); the strut
# grows out of the hinge lug, its bottom edge leaving the lug's bottom rear corner (L 452, H 98) so nothing juts
# below the lug, 6.5 mm deep there and 20 mm at the butt (the real hinge reaches lower, but its block reads badly
# proportioned that low, and a strut hanging under it reads worse: user, 2026-11-27)
STOCK_STRUT = [(440.0, 108.0), (440.0, 102.4), (640.0, 29.5), (636.0, 51.0)]   # the lower strap, side outline
BUTT = [(644.5, 127.1), (658.5, 127.0), (660.6, 125.5), (660.0, 121.5), (658.0, 97.5), (655.5, 69.2),
        (653.8, 46.6), (653.5, 32.5), (652.1, 28.3), (648.7, 27.5), (640.0, 29.0), (634.0, 50.0), (640.0, 58.0),
        (642.5, 75.0), (644.5, 97.5), (646.0, 107.5), (647.0, 112.0), (644.5, 118.0)]
HINGE_BLOCK = [(422.0, 98.0), (437.0, 98.0), (439.0, 131.0), (422.0, 131.0)]
END_CAP = [(422.0, 101.0), (426.0, 102.0), (428.0, 105.5), (428.0, 132.0), (426.0, 135.5), (422.0, 136.5)]
# the -2-07's fixed AK-74-style stock (its proportions on the receiver's height)
# (the comb falls 17 mm to the butt, the bottom runs straight from the wrist to the toe at 17 degrees, the butt plate
# 112 mm tall: an AK-74's polymer stock on this receiver)
# built in one piece (ak_stock: rounded sections lofted along it, user 2026-11-27: the two slabs read as a plank
# with a seam): 25 mm across at the wrist, flaring to 33 at the body, the moulded groove down each side; a small
# fill under the cover's rounded end, so no crevice opens there (user, 2026-11-27)
AK_TOP = [(422.0, 151.0), (445.0, 151.0), (671.0, 134.0)]
AK_BOTTOM = [(422.0, 101.0), (433.0, 100.0), (447.0, 94.0), (661.0, 22.0), (671.0, 22.0)]
AK_TANG = [(422.0, 135.0), (420.0, 141.0), (417.0, 146.0), (414.5, 150.5), (427.0, 150.5), (427.0, 135.0)]
AK_GROOVE = (475.0, 625.0, 1.8)     # the side groove: from, to (L), depth; its middle H 128 - (L - 470) / 5, 10 wide


# ---------- the Vityaz (PP-19-01), on the same AK receiver ----------
# Measured on Rock Island Auction's KP-9 (Kalashnikov USA's copy, references/vityaz/raw/ria_003.jpg, left side, 2400
# px, traced at its published 18.25 in = 463.5 mm, 4.997 px a mm) and laid on the Bizon's photo by the receiver they
# share (KP-9 L - 20, H - 71: the trigger, the receiver's bottom and its rear agree within 2-5 mm). The plain gun's
# parts (its AK-74 cover, the AKS-74 stock, the muzzle) from Kuzmin's PP-19-01 set (references/vityaz/raw/commons_*).
V_BORE = 133.0
RECV_V = [(230.0, 100.0)] + RECV[1:-1] + [(230.0, 165.5)]
# one piece with the receiver's front (the trunnion) under it, so no seam runs between them: L 203-231 down to the
# trunnion's bottom (the KP-9's receiver starts at the handguard's rear face, its bottom 6 mm above the well's), its
# front 4 mm inside the handguard so the handguard's rounded rear edge leaves no slit
V_REAR_SIGHT = [(166.0, 146.0), (203.0, 146.0), (203.0, 107.0), (231.0, 107.0), (231.0, 166.0), (228.0, 172.0), (207.0, 176.0), (200.0, 178.5),
                (168.0, 178.5), (166.3, 177.0), (166.0, 173.0)]
V_LEAF = [(180.0, 175.5), (230.0, 175.5), (230.0, 182.5), (227.0, 182.5), (226.5, 179.0), (180.0, 178.7)]
V_SLIDER = [(185.0, 173.0), (192.0, 173.0), (192.5, 179.5), (188.5, 181.5), (184.5, 179.5)]
V_FSB = [(17.0, 122.0), (43.0, 122.0), (43.0, 145.0), (17.0, 145.0)]
V_TOWER = [(18.0, 145.0), (18.0, 178.0), (20.0, 182.5), (25.0, 184.0), (30.0, 183.0), (32.5, 178.0), (34.0, 160.0),
           (37.0, 145.0)]
V_TOWER_HOLE = [(21.0, 151.0), (31.5, 151.0), (31.5, 160.0), (21.0, 160.0)]
V_UPPER = (48.0, 166.0, 160.5, 13.5)       # the round upper handguard: L front, L rear, axis H, radius
V_LOWER = [(43.0, 147.0), (43.0, 120.0), (46.0, 116.0), (70.0, 115.0), (150.0, 110.5), (178.0, 107.0),
           (184.0, 100.5), (190.0, 99.5), (195.0, 100.8), (200.0, 101.4), (204.0, 103.2), (206.0, 105.8),
           (207.0, 147.0)]
# the rivets on the receiver's front (in V_REAR_SIGHT)
V_RIVETS = [(216.5, 145.0), (217.0, 133.0), (237.0, 133.0), (217.0, 118.0)]
# the AK side-mount dovetail rail on the left of the receiver, on every body (the real PP-19-01 mounts optics there
# and has a plain cover, the KP-9's railed cover is Kalashnikov USA's; the Bizons have it too: commons_040, a Russian
# MVD Bizon's left side, and cca_020): read off Kuzmin's left view (commons_005, scaled by the
# trigger and the magazine's front): a base plate L 286-382, H 110-122, two raised dovetail blocks with a gap
SIDE_RAIL = [(286.0, 112.0), (290.0, 110.0), (382.0, 110.0), (382.0, 122.0), (290.0, 122.0), (286.0, 120.0)]
SIDE_BLOCKS = ([(296.0, 112.0), (334.0, 112.0), (334.0, 120.0), (299.0, 120.0), (296.0, 117.0)],
                 [(343.0, 112.0), (381.0, 112.0), (381.0, 120.0), (343.0, 120.0)])
V_WELL = [(230.0, 101.0), (281.0, 101.0), (281.0, 78.0), (276.0, 74.0), (238.0, 74.0), (234.0, 77.0)]
V_CATCH = [(281.0, 101.0), (309.0, 101.0), (309.0, 72.5), (306.0, 69.0), (284.0, 69.0), (281.0, 72.0)]
V_CATCH_LEVER = [(291.0, 70.0), (295.5, 70.0), (295.5, 61.0), (293.5, 59.5), (291.0, 61.0)]
V_GUARD_IN = [(309.5, 75.5), (311.5, 73.2), (317.0, 71.4), (335.0, 70.0), (351.0, 68.6), (356.0, 69.8),
              (359.0, 73.5), (360.3, 80.0), (360.8, 90.0), (361.0, 100.5)]
# the AK-74M-pattern grip, longer than the Bizon's (10 mm lower, its toe flared 20 mm further back): KP-9 trace
V_GRIP = [(362.0, 100.5), (362.0, 90.0), (366.0, 80.0), (371.9, 70.9), (391.3, 10.3), (391.0, -4.8), (395.5, -9.0),
          (403.5, -10.0), (435.5, -0.4), (443.3, 4.8), (443.3, 9.1), (416.9, 58.9), (411.7, 71.9), (413.5, 83.3),
          (417.5, 88.9), (422.9, 93.1), (424.0, 100.5)]
V_MAG_LIPS = (255.5, 100.0)                # the magazine's feed lips (middle)
# the 30 is curved (KP-9 trace: its front edge leans 5 degrees under the well, 27 at the base pad, 42 mm forward over
# 143 mm down): an arc of radius V_MAG_R from V_MAG_RAKE; 36 mm front to back along the receiver
V_MAG_RAKE, V_MAG_R, V_MAG_LEN, V_MAG_D, V_MAG_W = 5.0, 380.0, 168.0, 35.0, 22.0


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


def y(L):
    return L0 - L


def rounded(La, Lb, Ha, Hb, r, n=4):
    """A rounded rectangle (L, H)."""
    pts = []
    for cL, cH, a0 in ((Lb - r, Hb - r, 0), (La + r, Hb - r, 90), (La + r, Ha + r, 180), (Lb - r, Ha + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cL + r * math.cos(a), cH + r * math.sin(a)))
    return pts


# ==================================================================================================
# Geometry
# ==================================================================================================

def receiver(b, rear="hinge", vityaz=False):
    """The AK receiver and cover, the rear sight, grip, guard, trigger, selector, the helical's catch housing (the
    Vityaz: the AK-74's long rear sight base, its magazine well and catch)."""
    slab(b, RECV_V if vityaz else RECV, half=W_RECV, bevel=1.2)
    box(b, 300.0, 392.0, 162.0, 165.8, -W_COVER, W_COVER, bevel=0.8)              # the cover's ribbed top
    if vityaz:
        slab(b, V_REAR_SIGHT, half=W_RECV - 1.0, bevel=1.5)
        slab(b, V_LEAF, half=5.0, bevel=0.4)
        slab(b, V_SLIDER, half=7.0, bevel=0.8, mat="dark")
    else:
        slab(b, REAR_SIGHT, half=W_RECV - 1.5, bevel=1.0)
        slab(b, LEAF, half=5.0, bevel=0.4)
        slab(b, SLIDER, half=7.0, bevel=0.8, mat="dark")
    slab(b, V_GRIP if vityaz else GRIP, half=W_GRIP, bevel=3.5, res=1, mat="grip")
    gi = V_GUARD_IN if vityaz else GUARD_IN
    go = []
    for i, (L, H) in enumerate(gi):
        (ax, ay), (cx, cy) = gi[max(i - 1, 0)], gi[min(i + 1, len(gi) - 1)]
        dx, dy = cx - ax, cy - ay
        dd = math.hypot(dx, dy)
        go.append((L - GUARD_T * dy / dd, H + GUARD_T * dx / dd))
    b.strip(PL(go), PL(gi), -6.0, 6.0, mat="steel", bevel=0.4)
    slab(b, TRIGGER, half=2.6, bevel=0.6, mat="dark")
    if vityaz:
        slab(b, V_WELL, half=V_MAG_W / 2.0 + 3.0, bevel=1.5, res=1, mat="grip")
        slab(b, V_CATCH, half=W_CATCH, bevel=1.0)
        slab(b, V_CATCH_LEVER, half=4.0, bevel=0.5, mat="dark")
    else:
        slab(b, CATCH, half=W_CATCH, bevel=1.0)
        slab(b, CATCH_LEVER, half=4.0, bevel=0.5, mat="dark")
    # the selector on the right: its pivot boss and the long lever forward and up to the cover's edge
    (pL, pH), (tL, tH) = SELECTOR
    b.lathe("x", (0, y(pL), pH - H0), [(-(W_RECV + 1.8), 0), (-(W_RECV + 1.8), 6.0), (-(W_RECV + 1.2), 6.8),
                                       (-(W_RECV - 0.5), 6.8), (-(W_RECV - 0.5), 0)], seg=16, mat="steel")
    d = math.hypot(tL - pL, tH - pH)
    ux, uy = (tL - pL) / d, (tH - pH) / d

    def lv(a, across):
        return pL + ux * a - uy * across, pH + uy * a + ux * across

    lever = [lv(0.0, 4.5), lv(d - 6.0, 2.6), lv(d, 2.0), lv(d, -1.8), lv(d - 6.0, -2.4), lv(0.0, -4.5)]
    slab(b, lever, half=0.8, bevel=0.3, x0=-(W_RECV + 1.0))
    # the upper flap of the selector over the cover's edge (the dust cover's slot)
    box(b, 336.0, 412.0, 134.5, 144.5, -(W_RECV + 0.9), -(W_RECV - 0.4), bevel=0.3)
    slab(b, SLING_PLATE, half=W_RECV + 1.0, bevel=0.6, mat="bolt")
    slab(b, SIDE_RAIL, half=1.5, bevel=0.5, x0=W_RECV + 1.2)                       # the side rail, on the left (+x)
    for blk in SIDE_BLOCKS:
        slab(b, blk, half=1.3, bevel=0.4, x0=W_RECV + 3.6)
    slab(b, COVER_BUTTON, half=3.5, bevel=0.6)
    if rear == "hinge":
        slab(b, HINGE_BLOCK, half=W_RECV + 1.5, bevel=1.5)
        b.lathe("z", (W_RECV + 4.0, y(HINGE[0]), 0), [(105.0 - H0, 0), (105.0 - H0, 4.0), (128.0 - H0, 4.0),
                                                     (128.0 - H0, 0)], seg=12, mat="dark")
    elif rear == "cap":
        slab(b, END_CAP, half=W_RECV + 0.5, bevel=2.5, res=1)
    elif rear == "fixed":
        ak_stock(b)
        slab(b, AK_TANG, half=11.0, bevel=1.5, res=1, mat="poly")
        slab(b, [(669.0, 131.0), (677.5, 131.0), (677.5, 25.0), (671.0, 21.5), (669.0, 21.5)], half=17.5,
             bevel=1.5, mat="dark")                                                     # the butt plate


def front(b, kind):
    """Barrel, front sight block, handguard and muzzle per gun."""
    zb = BORE - H0
    if kind == "long":
        muzzle = 38.0 - LONG
        b.lathe("y", (0, 0, zb), [(y(236.0), 0), (y(236.0), 8.0), (y(62.0), 8.0), (y(62.0), 7.2),
                                  (y(muzzle + 2.0), 7.2), (y(muzzle + 1.0), 6.2), (y(muzzle), 6.2),
                                  (y(muzzle), 0)], seg=20, mat="steel", phase=0.5)
    elif kind == "thread":
        b.lathe("y", (0, 0, zb), [(y(236.0), 0), (y(236.0), 8.0), (y(40.0), 8.0), (y(40.0), 6.8), (y(30.0), 6.8),
                                  (y(29.0), 6.0), (y(14.0), 6.0), (y(13.0), 5.2), (y(13.0), 0)], seg=20,
                mat="steel", phase=0.5)
    else:
        b.lathe("y", (0, 0, zb), [(y(236.0), 0), (y(236.0), 8.0), (y(40.0), 8.0), (y(40.0), 0)], seg=20,
                mat="steel", phase=0.5)
        # the slotted compensator: a collar on the sight block's front, the body, a flared nose
        b.lathe("y", (0, 0, zb), [(y(41.0), 0), (y(41.0), 10.5), (y(36.0), 10.5), (y(36.0), 6.6), (y(5.0), 6.6),
                                  (y(2.5), 8.2), (y(0.0), 8.2), (y(0.0), 0)], seg=20, mat="steel", phase=0.5)
    slab(b, FSB, half=W_FSB, bevel=1.2)
    slab(b, TOWER, [TOWER_HOLE], half=W_TOWER, bevel=0.8)
    b.lathe("z", (0, y(51.5), 0), [(153.0 - H0, 1.3), (171.0 - H0, 1.0), (171.0 - H0, 0)], seg=8, mat="steel")
    if kind == "long":
        # the aftermarket railed handguard: a squared tube round the barrel with Picatinny rails on the top and
        # both sides, none underneath (the helical's place)
        hg = [(62.0, 159.0), (62.0, 123.0), (66.0, 119.0), (212.0, 119.0), (212.0, 159.0)]
        slab(b, hg, [rounded(a + 6.0, c - 6.0, 126.0, 134.0, 3.5) for a, c in ((75.0, 115.0), (125.0, 200.0))],
             half=W_HG - 1.0, bevel=2.0)
        top_h, side_h = 159.0, 140.0

        def frame_top(u, h, yy):
            return Vector((u, yy, top_h - H0 + h))

        kit.picatinny(b, y(208.0), y(66.0), frame_top, mat="rail")
        for s in (1.0, -1.0):
            def frame_side(u, h, yy, s=s):
                return Vector((s * (W_HG - 1.0 + h), yy, side_h - H0 + u))
            kit.picatinny(b, y(200.0), y(80.0), frame_side, mat="rail")
        # the front latch the helical hooks on, under the sight block
        box(b, 60.0, 75.0, 116.0, 123.0, -6.0, 6.0, bevel=0.8)
    else:
        slots = [rounded(a, c, HG_SLOT_H[0], HG_SLOT_H[1], 2.6) for a, c in HG_SLOTS]
        slab(b, HANDGUARD, slots, half=W_HG, bevel=2.2, res=1)
        box(b, 77.0, 92.0, 162.5, 166.5, -5.0, 5.0, bevel=0.8)                     # the top bar
        box(b, 60.0, 75.0, 116.0, 123.0, -6.0, 6.0, bevel=0.8)                     # the helical's front latch


def box_well(b):
    """The -2-07's box magazine well under the receiver, ahead of the catch housing."""
    La, Lb = BOX_LIPS[0] - BOX_D / 2.0 - 3.0, BOX_LIPS[0] + BOX_D / 2.0 + 3.0
    slab(b, [(La, 101.0), (Lb, 101.0), (Lb, 86.0), (La + 2.0, 86.0), (La, 89.0)], half=BOX_W / 2.0 + 2.5,
         bevel=1.0)


def front_vityaz(b):
    """The Vityaz: AK-74 front sight block on the barrel, the threaded tip for the 9x19 mount, the round upper
    handguard with its front nut, the ribbed lower handguard with its finger stop."""
    zb = V_BORE - H0
    b.lathe("y", (0, 0, zb), [(y(230.0), 0), (y(230.0), 8.0), (y(17.0), 8.0), (y(17.0), 6.8), (y(9.0), 6.8),
                              (y(8.0), 6.0), (y(-6.0), 6.0), (y(-7.0), 5.2), (y(-7.0), 0)], seg=20,
            mat="steel", phase=0.5)
    slab(b, V_FSB, half=W_FSB, bevel=1.2)
    slab(b, V_TOWER, [V_TOWER_HOLE], half=W_TOWER, bevel=0.8)
    b.lathe("z", (0, y(26.0), 0), [(V_TOWER_HOLE[0][1] - H0, 1.3), (180.0 - H0, 1.0), (180.0 - H0, 0)], seg=8,
            mat="steel")
    uL0, uL1, uH, ur = V_UPPER
    b.lathe("y", (0, 0, uH - H0), [(y(uL0 - 16.0), 0), (y(uL0 - 16.0), 9.5), (y(uL0 + 1.0), 9.5),
                                   (y(uL0 + 1.0), ur - 1.5), (y(uL0 + 3.0), ur), (y(uL1 - 4.0), ur),
                                   (y(uL1), ur - 3.5), (y(uL1), 0)], seg=24, mat="poly", phase=0.5)
    slab(b, V_LOWER, half=W_HG, bevel=6.0, res=2, mat="poly")


def _lerp(pts, L):
    for (a, ha), (c, hc) in zip(pts, pts[1:]):
        if L <= c:
            t = 0.0 if c == a else max(0.0, (L - a) / (c - a))
            return ha + (hc - ha) * t
    return pts[-1][1]


def ak_stock(b, L0s=422.0, L1s=670.0):
    """The -2-07's polymer stock as one lofted piece: rounded-rectangle sections between AK_TOP and AK_BOTTOM,
    25 mm wide at the wrist flaring to 33, the side groove pressed in (a ring's side heights always include the
    groove's four edge heights, so every ring has the same vertices)."""
    gA, gB, gD = AK_GROOVE
    stations = [L0s + (L1s - L0s) * i / 44 for i in range(45)]
    rings = []
    for L in stations:
        ht, hb = _lerp(AK_TOP, L), _lerp(AK_BOTTOM, L)
        t = min(1.0, max(0.0, (L - 452.0) / 48.0))
        w = 12.5 + 4.0 * t * t * (3 - 2 * t)
        r = min(7.0, 0.45 * w, 0.2 * (ht - hb))
        gc = 128.0 - (L - 470.0) / 5.0
        fade = min(1.0, max(0.0, (L - gA) / 10.0), max(0.0, (gB - L) / 10.0))
        lo, hi = hb + r + 0.8, ht - r - 0.8
        side = sorted([lo + (hi - lo) * k / 9 for k in range(10)] +
                      [min(hi - 0.2, max(lo + 0.2, gc + d)) for d in (-5.0, -3.5, 3.5, 5.0)])

        def depth(H):
            g = 1.0 if abs(H - gc) <= 3.5 else max(0.0, (5.0 - abs(H - gc)) / 1.5)
            return gD * fade * g

        pts = []
        for k in range(5):                                    # bottom right corner, -90 .. 0 degrees
            a = math.radians(-90.0 + 90.0 * k / 4)
            pts.append((w - r + r * math.cos(a), hb + r + r * math.sin(a)))
        pts += [(w - depth(H), H) for H in side]
        for k in range(5):                                    # top right, 0 .. 90
            a = math.radians(90.0 * k / 4)
            pts.append((w - r + r * math.cos(a), ht - r + r * math.sin(a)))
        for k in range(5):                                    # top left, 90 .. 180
            a = math.radians(90.0 + 90.0 * k / 4)
            pts.append((-w + r + r * math.cos(a), ht - r + r * math.sin(a)))
        pts += [(-(w - depth(H)), H) for H in reversed(side)]
        for k in range(5):                                    # bottom left, 180 .. 270
            a = math.radians(180.0 + 90.0 * k / 4)
            pts.append((-w + r + r * math.cos(a), hb + r + r * math.sin(a)))
        rings.append([b.bm.verts.new((x, y(L), H - H0)) for x, H in pts])
    faces = [b.bm.faces.new(rings[0][::-1]), b.bm.faces.new(rings[-1])]
    n = len(rings[0])
    for ra, rb in zip(rings, rings[1:]):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(b.bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for ring in rings for v in ring], faces, "poly", 0.0, None)


def build_body(name, rear, kind):
    b = kit.Builder()
    if kind == "vityaz":
        receiver(b, rear, vityaz=True)
        front_vityaz(b)
        return b.to_object(name)
    receiver(b, rear)
    front(b, kind)
    if kind == "long":
        box_well(b)
    return b.to_object(name)


def build_bolt():
    """The AK carrier's charging handle on the right, at the front of its slot (moves with the carrier)."""
    b = kit.Builder()
    hL, hH = HANDLE
    box(b, hL - 2.0, hL + 22.0, hH - 3.0, hH + 3.0, -(W_RECV + 0.5), -(W_RECV - 1.0), mat="bolt", bevel=0.4)
    b.lathe("x", (0, y(hL), hH - H0), [(-(W_RECV - 1.0), 0), (-(W_RECV - 1.0), 3.2), (-(W_RECV + 4.0), 3.2),
                                       (-(W_RECV + 5.0), 4.6), (-(W_RECV + 9.0), 4.6), (-(W_RECV + 9.5), 3.8),
                                       (-(W_RECV + 9.5), 0)], seg=14, mat="bolt")
    return b.to_object("BIZON_BOLT")


def tube(b, a, c, r, mat="steel", seg=14):
    """A round bar between photo points a and c."""
    (aL, aH), (cL, cH) = a, c
    dy, dz = y(cL) - y(aL), cH - aH
    length = math.hypot(dy, dz)
    phi = math.atan2(-dz, -dy)
    centre = Vector((0.0, y(aL), aH - H0))
    xf = Matrix.Translation(centre) @ Matrix.Rotation(phi, 4, 'X') @ Matrix.Translation(-centre)
    b.lathe("y", centre, [(0.0, 0), (0.0, r), (-length, r), (-length, 0)], seg=seg, mat=mat, xf=xf)


FOLD_X = W_HG + 8.5                # the folded stock's top tube, beside the handguard on the left
FOLD_TILT = -13.0                  # degrees: the folded stock's plane leans out at the bottom, over the helical
FOLD_PITCH, FOLD_LIFT = 9.5, 0.0   # degrees up toward the muzzle about the hinge, mm up (2026-11-27: commons_040
                                   # laid on the model by the compensator and the cover's top, tmp/bizon/c040m_trace.json:
                                   # the tube rises from the hinge, H 120, to the butt's top, H 162 at L 195-203; the
                                   # old 19 mm lift came from a trace scaled to the sling)
# the Vityaz has no helical: its stock folds flat against the receiver's and handguard's left side, a little pitched
# up as on the Bizon (Kuzmin's PP-19-01 set, commons_005 / _008): the tube from a third down the receiver at the
# hinge to the butt, whose top sits just over the cover's, its foot 30 mm under the receiver (2026-11-27: commons_005
# laid on the model by the upper handguard and the cover, tmp/bizon/c005m_trace.json: tube H 121 at the hinge, 160 at
# the butt, butt H 71-171 at L 185-205)
V_FOLD = (W_HG + 9.0, 0.0, 12.0, -6.0)


def build_stock(folded, name=None, fold=None):
    """The AKS-74 stock: its top tube, the lower strap, the butt plate, the hinge's lug. Folded, it swings forward
    round the hinge onto the gun's left side (mirrored about the hinge, moved out to FOLD_X)."""
    b = kit.Builder()
    tube(b, STOCK_TUBE[0], STOCK_TUBE[1], STOCK_TUBE[2])
    slab(b, STOCK_STRUT, half=4.0, bevel=0.8)
    slab(b, BUTT, half=8.5, bevel=2.0, res=1)
    slab(b, [(434.0, 98.0), (450.0, 98.0), (450.0, 130.0), (434.0, 130.0)], half=6.0, bevel=1.0)
    if folded:
        # Kuzmin's left view of a folded gun (commons_040): the tube rises forward from the hinge (H 143) to the
        # butt's top over the rear sight (L 195, H 173), the butt's foot level with the helical's bottom third (H 83):
        # the hinge pin leans, so the stock is pitched FOLD_PITCH and lifted FOLD_LIFT as well as mirrored
        fx, tilt, pitch, lift = fold or (FOLD_X, FOLD_TILT, FOLD_PITCH, FOLD_LIFT)
        pivot = Vector((0.0, y(HINGE[0]), STOCK_TUBE[0][1] - H0))
        tube_axis = pivot + Vector((0.0, 0.0, lift))
        xf = (Matrix.Translation(tube_axis + Vector((fx, 0.0, 0.0)))
              @ Matrix.Rotation(math.radians(tilt), 4, 'Y') @ Matrix.Translation(-tube_axis)
              @ Matrix.Translation((0.0, 0.0, lift))
              @ Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(pitch), 4, 'X') @ Matrix.Translation(-pivot)
              @ Matrix.Translation((0.0, 2.0 * y(HINGE[0]), 0.0)) @ Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)))
        for v in b.bm.verts:
            v.co = xf @ v.co
        import bmesh
        bmesh.ops.reverse_faces(b.bm, faces=list(b.bm.faces))
    return b.to_object(name or ("BIZON_STOCK_FOLDED" if folded else "BIZON_STOCK_DEPLOYED"))


# ---------- magazines ----------

HELIX_RIB_PITCH = 4.6
MAGS = {"9x18Magazine64_BIZON": ("helix", "64"), "9x19Magazine53_BIZON": ("helix", "53"),
        "762x25Magazine45_BIZON": ("helix", "45"), "762x25Magazine35_BIZON": ("box", "35"),
        "9x19Magazine30_VITYAZ": ("vbox", "30"), "9x19Magazine30_VITYAZ_PAIR": ("vpair", "30")}


def build_helix(name):
    """Origin at MAG_PT (the rear face's top); the tube, its front cap, the front foot and the hook on top."""
    b = kit.Builder()
    oL, oH = MAG_PT

    def yy(L):
        return oL - L

    zc = HELIX_H - oH
    fL, rL = HELIX_L
    b.lathe("y", (0, 0, zc), [(yy(rL), 0), (yy(rL), HELIX_R - 1.0), (yy(rL - 1.5), HELIX_R),
                              (yy(fL + 38.0), HELIX_R), (yy(fL + 37.0), HELIX_R + 0.6), (yy(fL + 3.0), HELIX_R + 0.6),
                              (yy(fL), HELIX_R - 2.4), (yy(fL), 0)], seg=28, mat="poly", phase=0.5)
    # the front foot under the cap and the hook that latches on the sight block's latch
    foot = [(77.0, 67.0), (92.0, 67.0), (92.0, 58.0), (84.0, 55.0), (78.5, 56.5)]
    b2 = kit.slab(b, [(yy(L), H - oH) for L, H in foot], [], 9.0, 1.0, 0, "poly", 0.0)
    hook = [(63.0, 113.0), (76.0, 113.0), (76.0, 121.5), (70.0, 121.5), (63.0, 118.0)]
    kit.slab(b, [(yy(L), H - oH) for L, H in hook], [], 5.0, 0.6, 0, "mag", 0.0)
    # the rear feed tower that rises into the receiver over the tube's back
    kit.slab(b, [(yy(L), H - oH) for L, H in [(236.0, 110.0), (278.0, 110.0), (278.0, 116.5), (236.0, 116.5)]],
             [], 9.5, 0.8, 0, "mag", 0.0)
    return b.to_object(name)


BOX_LEN, BOX_R = 171.0, 360.0      # the box below its lips, the radius of its forward curve (vpk_000: 25 mm forward
                                   # over the top 130 mm, its base 61-78 mm under the grip's base)


def curved_box(b, length, radius, d, w, a0=0.0, flare=1.4, x0=0.0, bevel=0.6, s0=0.0):
    """A magazine body below its lips (origin), sweeping forward (+y) on an arc of `radius` from `a0` degrees off
    vertical; d front to back, w side to side, a base `flare` wider over its last 4 mm; from `s0` mm down the arc."""
    bm = b.bm
    a0 = math.radians(a0)
    n = 14
    rings = []
    stations = [(s0 + (length - s0) * i / n, 0.0) for i in range(n + 1)] + [(length, flare), (length + 4.0, flare)]
    for sm, grow in stations:
        a = a0 + sm / radius
        cy = radius * (math.cos(a0) - math.cos(a))                     # forward = +y, down = -z
        cz = -radius * (math.sin(a) - math.sin(a0))
        ty, tz = math.sin(a), -math.cos(a)                               # tangent (down and forward)
        ny, nz = -tz, ty                                                 # normal, toward the front
        hd = d / 2.0 * (1.0 + 0.06 * min(sm, length) / length) + grow
        hw = w / 2.0 + grow
        ring = []
        for xs, k in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ring.append(bm.verts.new((x0 + xs * hw, cy + ny * k * hd, cz + nz * k * hd)))
        rings.append(ring)
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, "mag", bevel, None)


V_MAG_SLEEVE = 80.0    # the lower body's stepped sleeve, from this far down the arc (Kuzmin's commons_014 / _025)


def vityaz_mag(b, x0=0.0):
    """One Vityaz 30: a curved polymer box, the stepped sleeve over its lower half (1.5 mm proud front and back, 1 at
    the sides), its base pad, the top round."""
    curved_box(b, V_MAG_LEN, V_MAG_R, V_MAG_D, V_MAG_W, V_MAG_RAKE, flare=1.6, x0=x0, bevel=1.2)
    curved_box(b, V_MAG_LEN, V_MAG_R, V_MAG_D + 3.0, V_MAG_W + 2.0, V_MAG_RAKE, flare=0.6, x0=x0, bevel=1.0,
               s0=V_MAG_SLEEVE)
    b.lathe("y", (x0, -1.0, -3.5), [(-10.5, 0), (-10.5, 4.95), (4.5, 4.95), (5.0, 4.6)], seg=8, mat="brass")
    b.lathe("y", (x0, -1.0, -3.5), [(5.0, 4.6), (8.5, 4.5), (12.5, 2.9), (14.2, 0)], seg=8, mat="copper")


def build_vityaz_mag(name, pair=False):
    """Origin at the feed lips' middle. The pair: a second magazine clipped beside it on the left (+x), its lips
    15 mm lower (the clip holds them staggered), two clamps round both."""
    b = kit.Builder()
    vityaz_mag(b)
    if pair:
        gap = V_MAG_W + 3.0
        before = set(b.bm.verts)
        vityaz_mag(b, x0=gap)
        a = math.radians(V_MAG_RAKE)
        for v in b.bm.verts:
            if v not in before:
                v.co.z -= 15.0 * math.cos(a)
                v.co.y += 15.0 * math.sin(a)
        for sm in (60.0, 125.0):                                         # the clamps round both, on the arc
            t = a + sm / V_MAG_R
            xf = (Matrix.Translation((0.0, V_MAG_R * (math.cos(a) - math.cos(t)), -V_MAG_R * (math.sin(t) - math.sin(a))))
                  @ Matrix.Rotation(t, 4, 'X'))
            b.box(-V_MAG_W / 2.0 - 3.0, gap + V_MAG_W / 2.0 + 3.0, -V_MAG_D / 2.0 - 3.2, V_MAG_D / 2.0 + 3.2,
                  -6.0, 6.0, mat="dark", bevel=0.8, xf=xf)                 # (round the sleeve too)
    return b.to_object(name)


def build_box(name):
    """Origin at the feed lips' middle; a curved steel box sweeping forward as it goes down, a base plate."""
    b = kit.Builder()
    curved_box(b, BOX_LEN, BOX_R, BOX_D, BOX_W)
    b.lathe("y", (0, -2.0, -3.5), [(-12.0, 0), (-12.0, 4.7), (6.0, 4.7), (7.0, 4.0)], seg=8, mat="brass")
    b.lathe("y", (0, -2.0, -3.5), [(7.0, 4.0), (12.0, 3.6), (15.0, 1.5), (16.0, 0)], seg=8, mat="copper")
    return b.to_object(name)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: blued/black steel, the black Bakelite-look grip, the helical's black polymer, rails
    "steel": (46, 47, 52), "grip": (32, 32, 34), "dark": (28, 28, 31), "bolt": (88, 89, 92),
    "poly": (36, 37, 39), "rail": (38, 39, 42), "mag": (58, 59, 64), "brass": (150, 118, 62), "copper": (140, 82, 52),
}


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "dark", "bolt", "rail", "mag", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.88 + 0.24 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.84 + 0.32 * streak[is_metal])[..., None]
    col *= (0.96 + 0.12 * np.clip(n[..., 2], -1, 1))[..., None]
    col *= (0.86 + 0.28 * np.clip((p[..., 2] + 110.0) / 180.0, 0.0, 1.0))[..., None]
    occ = (0.62 + 0.38 * np.clip(ao_b, 0, 1) ** 1.5) * (0.66 + 0.34 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 105.0, 50.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.05])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def rivet(col, L, H, sel, cL, cH, r=2.0):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r + 0.8) & (d >= r)] *= 0.55
    col[sel & (d < r)] += 40


def paint_body(maps, col, body=""):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, z = p[..., 0], p[..., 2]
    L, H = L0 - p[..., 1], z + H0
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    side = left | right
    steel = mat == MATS.index("steel")
    recv = steel & side & (np.abs(x) > W_RECV - 0.6) & (np.abs(x) < W_RECV + 0.6) & (L > 236.0) & (L < 423.5)
    # the cover's seam, the charging slot on the right, the dust cover's slot under the selector's flap
    col[recv & (np.abs(H - 148.0) < 0.45) & (L > 300.0)] *= 0.5
    col[recv & right & (L > 300.0) & (L < 395.0) & (np.abs(H - 141.0) < 1.6)] = 10
    col[recv & (np.abs(H - 102.5) < 0.5)] += 22                     # the lower rail's lip
    for cL, cH in RIVETS:
        rivet(col, L, H, recv, cL, cH)
    if body == "VITYAZ_BODY":
        trun = steel & side & (np.abs(x) > W_RECV - 1.7) & (L > 207.5) & (L < 245.0) & (H < 150.0)
        for cL, cH in V_RIVETS:
            rivet(col, L, H, trun, cL, cH)
    col[recv & right & (np.hypot(L - 255.0, H - 131.0) < 4.0)] *= 0.8
    # the handguard's pressed ridge and the helical's catch housing's hole
    hg = steel & side & (np.abs(x) > W_HG - 0.8) & (L > 62.0) & (L < 212.0)
    col[hg & (np.abs(H - 133.0) < 0.6)] *= 0.6
    col[hg & (np.abs(H - 134.2) < 0.5)] += 18
    catch = steel & side & (np.abs(x) > W_CATCH - 0.7) & (L > 278.0) & (L < 300.0) & (H < 104.0)
    col[catch & (np.hypot(L - 289.0, H - 89.0) < 3.2)] = 12
    # the compensator's slots
    r = np.hypot(x, z - (BORE - H0))
    comp = steel & (L < 36.0) & (L > 5.0) & (r > 5.5)
    ang = np.arctan2(z - (BORE - H0), x)
    col[comp & (L > 8.0) & (L < 24.0) & (np.abs(np.abs(ang) - math.pi / 2) > 0.5) & (np.abs(np.abs(ang) - math.pi / 2) < 1.15)] = 10
    col[steel & (L < 1.0) & (r < 4.0)] = 6
    col[steel & (np.abs(L - (38.0 - LONG)) < 1.0) & (r < 4.0)] = 6
    col[steel & (np.abs(L - 13.0) < 1.0) & (r < 4.0)] = 6
    # the thread on the -2-01's tip
    col[steel & (L > 14.0) & (L < 29.0) & (r > 5.5) & (r < 6.4) & (np.mod(L, 1.1) < 0.45)] *= 0.55
    # the grip's chequered panel
    grip = mat == MATS.index("grip")
    gs = grip & side
    panel = gs & (body != "VITYAZ_BODY") & (H > 10.0) & (H < 87.0) & (L > 0.4 * (87.0 - H) + 368.0) & (L < 0.18 * (87.0 - H) + 402.0)
    u, v = L * 0.42 + H * 0.9, L * 0.9 - H * 0.42
    col[panel] *= 0.82
    col[panel & ((np.mod(u, 2.2) < 0.8) | (np.mod(v, 2.2) < 0.8))] *= 0.55
    col[gs] += (7.0 * kit.vnoise(p, 1.2, 9))[gs][..., None]
    # the Vityaz's lower handguard: its horizontal ribs over the rear two thirds
    vhg = (mat == MATS.index("poly")) & side & (np.abs(x) > W_HG - 1.0) & (L > 80.0) & (L < 205.0) & (H > 122.0) & (H < 144.0)
    col[vhg & (np.mod(H, 3.2) < 1.1)] *= 0.55
    # the -2-07's stock: the moulded groove down each side
    poly = (mat == MATS.index("poly")) & side
    groove = poly & (L > 470.0) & (L < 630.0) & (np.abs(H - (128.0 - (L - 470.0) * 0.2)) < 5.0)
    col[groove] *= 0.78
    col[poly & (L > 470.0) & (L < 630.0) & (np.abs(np.abs(H - (128.0 - (L - 470.0) * 0.2)) - 5.0) < 0.6)] *= 0.6


def paint_stock(maps, col):
    pass


def paint_helix(maps, col, label):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    oL, oH = MAG_PT
    L, H = oL - p[..., 1], p[..., 2] + oH
    poly = mat == MATS.index("poly")
    zc = H - HELIX_H
    ang = np.arctan2(zc, p[..., 0])
    lower = poly & (zc < -2.0) & (L > 92.0) & (L < 274.0)
    col[lower & (np.mod(L, HELIX_RIB_PITCH) < 1.6)] *= 0.55
    col[lower & (np.mod(L, HELIX_RIB_PITCH) >= 1.6)] += 6
    # the round count stamped on each side
    side = poly & (np.abs(n[..., 0]) > 0.55) & (zc > 0.0)
    left = side & (p[..., 0] > 0)
    right = side & (p[..., 0] < 0)
    col[left & kit.text_mask(-p[..., 1], H, label, 184.0 - oL, 89.5, 6.0)] += 40
    col[right & kit.text_mask(p[..., 1], H, label, oL - 206.0, 89.5, 6.0)] += 40


def paint_box(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    side = (mat == MATS.index("mag")) & (np.abs(n[..., 0]) > 0.7)
    col[side & (np.abs(p[..., 2] + 60.0) < 50.0) & (np.abs(p[..., 1] - 0.0018 * p[..., 2] ** 2) < 3.0)] *= 0.7


# Each gun its own furniture colour (user, 2026-11-27: "different colors for each bizon if available"), each a real
# finish of its parts: the PP-19 the plum Bakelite-look grip of the AKS-74 parts it was built from in 1993; the
# Bizon-2-01 all black, as the measuring photo's gun; the -2-07 the AK-74's plum polymer stock and grip of its day
# (1997); the Vityaz all black (user, 2026-11-27: "leave vityaz black").
PLUM = (84, 38, 34)
BODY_COLOURS = {"BIZON_BODY": {"grip": PLUM}, "BIZON207_BODY": {"grip": PLUM, "poly": PLUM}}


def paint(maps, kind):
    p, mat = maps["pos"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind.startswith("body"):
        body = kind.split(":")[1] if ":" in kind else ""
        for name, rgb in BODY_COLOURS.get(body, {}).items():
            col[mat == MATS.index(name)] = rgb
        paint_body(maps, col, body)
    elif kind == "stock":
        paint_stock(maps, col)
    elif kind == "box":
        paint_box(maps, col)
    elif kind.startswith("helix:"):
        paint_helix(maps, col, kind.split(":")[1])
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


TEX = 1024


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


def weighted_normals(objects):
    for ob in objects:
        mod = ob.modifiers.new("weighted", 'WEIGHTED_NORMAL')
        mod.mode = 'FACE_AREA'
        mod.weight = 100
        mod.keep_sharp = True
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=mod.name)


# ==================================================================================================
# Attachment points
# ==================================================================================================

RAIL_TOP_H = 159.0 + 4.0           # the -2-07's top rail's mounting face (base) H
GOM_RAIL_UP_H = 165.8              # GoM's Picatinny_Rail_Up seat: the cover's top


def points(bounds):
    pts = {
        "BIZON": {"muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
                  "canon": {"offset": gp(0.0, BORE), "rotate": ZERO}},
        "BIZON201": {"muzzle": {"offset": gp(13.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
                     "canon": {"offset": gp(13.0, BORE), "rotate": ZERO}},
        "BIZON207": {"muzzle": {"offset": gp(38.0 - LONG, BORE), "rotate": [-90.0, 0.0, -180.0]},
                     "canon": {"offset": gp(38.0 - LONG, BORE), "rotate": ZERO},
                     "magazine_box": {"offset": gp(*BOX_LIPS), "rotate": ZERO},
                     "rail_up": {"offset": gp(137.0, RAIL_TOP_H), "rotate": ZERO},
                     "rail_left": {"offset": gp(140.0, 140.0, W_HG + 3.0), "rotate": ZERO},
                     "rail_right": {"offset": gp(140.0, 140.0, -(W_HG + 3.0)), "rotate": ZERO}},
        "VITYAZ": {"muzzle": {"offset": gp(-7.0, V_BORE), "rotate": [-90.0, 0.0, -180.0]},
                   "canon": {"offset": gp(-7.0, V_BORE), "rotate": ZERO},
                   "magazine": {"offset": gp(*V_MAG_LIPS), "rotate": ZERO},
                   "rail_down": {"offset": gp(120.0, 110.0), "rotate": ZERO}},
        "magazine": {"offset": gp(*MAG_PT), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
        "rail_up_cover": {"offset": gp(330.0, GOM_RAIL_UP_H), "rotate": ZERO},
        "handguard_side_left": {"offset": gp(140.0, 140.0, W_HG), "rotate": ZERO},
        "handguard_side_right": {"offset": gp(140.0, 140.0, -W_HG), "rotate": ZERO},
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin as GoM's AKS-74U "
                 "against trigger and bore (photo L %.1f, H %.1f)" % (L0, H0),
        "magazine": "the helicals' rear face top (all three helicals); BIZON207 magazine_box the box's feed lips",
        "bolt_fired": "BIZON_BOLT (the carrier's handle) back %.0f mm real" % CARRIER_TRAVEL,
        "stocks": "BIZON_STOCK_FOLDED / _DEPLOYED (the -2-01) are drawn in place",
        "rails": "rail_up_cover / handguard_side_*: where GoM's optional rails sit on the PP-19 and -2-01 (wiring "
                 "places them); BIZON207 rail_* are its integrated rails' faces",
    }
    pts["_extras"] = {"photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K, "long_mm": LONG}
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

    bodies = [build_body("BIZON_BODY", "cap", "comp"), build_body("BIZON201_BODY", "hinge", "thread"),
              build_body("BIZON207_BODY", "fixed", "long"), build_body("VITYAZ_BODY", "hinge", "vityaz")]
    bolt = build_bolt()
    folded, deployed = build_stock(True), build_stock(False)
    v_folded = build_stock(True, "VITYAZ_STOCK_FOLDED", V_FOLD)
    gun = bodies + [bolt, folded, deployed, v_folded]
    mags = [build_helix(n) if k == "helix" else build_box(n) if k == "box" else build_vityaz_mag(n, k == "vpair")
            for n, (k, _) in MAGS.items()]
    weighted_normals(gun + mags)
    kit.unwrap(gun, 0.004)
    for m in mags:
        kit.unwrap([m], 0.01)
    # 1024 (2026-11-27): eight objects share this atlas, and at 512 the painted rivets, ribs and seams went blocky
    maps = [bake(o, [o, bolt], TEX) for o in bodies] + [bake(bolt, [bodies[1], bolt], TEX),
                                                         bake(folded, [bodies[1], folded], TEX),
                                                         bake(deployed, [bodies[1], deployed], TEX),
                                                         bake(v_folded, [bodies[3], v_folded], TEX)]
    texture(maps, ["body:" + o.name for o in bodies] + ["body", "stock", "stock", "stock"], TEX,
            os.path.join(TEX_DIR, "BIZON.png"))
    for (n, (k, label)), m in zip(MAGS.items(), mags):
        texture([bake(m, [m], 128)], ["helix:" + label if k == "helix" else "box" if k == "box" else "vbox"], 128,
                os.path.join(TEX_DIR, n + ".png"))

    bounds = {o.name: kit.bounds_of(o) for o in gun}
    bounds["BIZON_BOLT_fired"] = kit.bounds_of(bolt, (0, -CARRIER_TRAVEL * K, 0))
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
