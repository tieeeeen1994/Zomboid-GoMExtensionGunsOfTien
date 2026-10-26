"""IMI Uzi, Mini Uzi and Micro Uzi models and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_uzi.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_UZI.fbx        UZI_BODY, UZI_BOLT, UZI_STOCK_FOLDED, UZI_STOCK_DEPLOYED
    M/models_X/weapons/firearms/GunsOfTien_MINIUZI.fbx    MINIUZI_BODY, MINIUZI_BOLT, MINIUZI_STOCK
    M/models_X/weapons/firearms/GunsOfTien_MICROUZI.fbx   MICROUZI_BODY, MICROUZI_BOLT, MICROUZI_STOCK
    M/models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx  9x19Magazine20/25/32/40/50_UZI (all three guns)
    M/textures/weapons/GunsOfTien/<gun>.png                one 256 atlas per gun (body, cocking knob, stock),
                                                           128 per magazine
    scripts/uzi_points.json                                attachment points of the three guns (game space)

Each gun is traced from its own side photo (the user's, 2026-10-23, and one from Wikimedia Commons; none is kept in
the repo: tmp/ref/uzi). Profiles are written in that photo's coordinates, real millimetres: L back from the muzzle tip,
H up from the photo's lowest point:
- Uzi: Commons "Uzi of the israeli armed forces" (Uziel Galishto, CC BY-SA 3.0): left side, stock folded, a 25-round
  magazine, scaled to IMI's 470 mm folded (2.519 px/mm; the receiver then measures 452 mm, the published stockless
  length is 445, and the magazine 32.9 mm front to back).
- Mini Uzi: the user's side photo (left side, stock deployed, a 20-round magazine), scaled to IMI's 600 mm with the
  stock deployed (its folded length then comes out at the published 360).
- Micro Uzi: the user's side photo (left side, stock folded forward, its butt plate hanging under the barrel as a
  front grip, a 20-round magazine), scaled by the magazine (the same IMI magazine as in the Uzi photo): 257 mm folded
  (published 250 to 282).
The three photos do not agree on the height under the receiver to within about 15 mm, so each gun keeps its own
photo's proportions and only the magazines are shared: every gun's `magazine` point puts the 20-round magazine's
base 22 mm under its own grip, as all three photos show.

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): +Y muzzle, +Z top, +X the gun's LEFT, origin at the rear-top of
the pistol grip, 0.603 of real size, the M16A2's proportion (0.72 before 2026-10-26, GoM's SMGs). The Uzi is held as a rifle (upright model, GoM's MP5). The Mini and
Micro Uzi are held like a pistol (user, 2026-10-23: GoM's MP5K / MAC-10 way), so they are modelled and baked upright
and their gun nodes are turned 180 degrees about the bore axis at export, with their points (build_mp7.py's TURN /
turned()); magazines stay upright. The cocking knob on top does not reciprocate (bolt_fired = bolt_lock).
Stocks: the Uzi's twin-strut metal stock folds down under the receiver with its butt plate standing behind the grip,
so it is two nodes modelled in the gun's own space (UZI_STOCK_FOLDED / _DEPLOYED, drawn at the gun's origin, GoM's
MAC-10 way). The Mini's and Micro's single-strut stock folds forward along the right side about a vertical hinge pin
at the receiver's right rear, so each is one node modelled deployed with its origin at that pin: `stock` puts it
there, `stock_folded` adds a half turn about Z (the butt plate then hangs under the barrel, as on the Micro photo).
Real sizes: Uzi 260 mm barrel, Mini 197, Micro 117; the Uzi deployed 640, Mini 600, Micro about 460.
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
FBX_DIR = os.path.join(MEDIA, "models_X/weapons/firearms")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_UZI_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "uzi_points.json")

K = 0.000603                       # game units per real mm: the M16A2's proportion (user, 2026-10-26: our guns resized in their meshes; was 0.00072, GoM's SMGs)
K_OLD = 0.00072
kit.K = K
MATS = ["metal", "polymer", "grip", "dark", "barrel", "hg", "magmetal", "brass", "copper"]
kit.MATS[:] = MATS
for ch, rows in {"U": ["101", "101", "101", "101", "111"], "Z": ["111", "001", "010", "100", "111"],
                 "C": ["111", "100", "100", "100", "111"], "O": ["111", "101", "101", "101", "111"],
                 "9": ["111", "101", "111", "001", "111"], "5": ["111", "100", "111", "001", "111"],
                 "8": ["111", "101", "111", "101", "111"], "L": ["100", "100", "100", "100", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

ZERO = [0.0, 0.0, 0.0]


class Frame:
    """A photo's (L, H) mm frame: origin (L0, H0) = the rear-top of the grip, bore height `bore`."""

    def __init__(self, L0, H0, bore):
        self.L0, self.H0, self.bore = L0, H0, bore

    def P(self, L, H):
        return self.L0 - L, H - self.H0

    def PL(self, pts):
        return [self.P(L, H) for L, H in pts]

    def y(self, L):
        return self.L0 - L

    def z(self, H):
        return H - self.H0

    def gp(self, L, H, x=0.0):
        y, z = self.P(L, H)
        return [round(x * K, 4) + 0.0, round(y * K, 4) + 0.0, round(z * K, 4) + 0.0]


def slab(b, f, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="metal", x0=0.0):
    return kit.slab(b, f.PL(outline), [f.PL(h) for h in holes], half, bevel, res, mat, x0)


def both(fn):
    for s in (1, -1):
        fn(s)


def barrel(b, f, muzzle_r, nut_r, nut_front, nut_back, crown=0.6):
    """The barrel nut (knurled, its front face = `canon`) and the barrel out of it."""
    zb = f.z(f.bore)
    y = f.y
    b.lathe("y", (0, 0, zb), [(y(nut_back), 0), (y(nut_back), nut_r - 1.5), (y(nut_back - 1.2), nut_r),
                              (y(nut_front + 1.2), nut_r), (y(nut_front), nut_r - 1.5), (y(nut_front), 0)],
            seg=24, mat="dark", phase=0.5)
    b.lathe("y", (0, 0, zb), [(y(nut_front + 2.0), 0), (y(nut_front + 2.0), muzzle_r), (y(crown), muzzle_r),
                              (y(0.0), muzzle_r - crown), (y(0.0), 0)], seg=16, mat="barrel", phase=0.5)


def sight_ears(b, f, outline, gap, base, mat="metal", post=None, drum=None):
    """Two protective ears either side of the sight (front post or rear flip aperture), on a base block."""
    both(lambda s: slab(b, f, outline, half=2.2, bevel=0.6, mat=mat, x0=s * (gap + 2.2)))
    slab(b, f, base, half=gap + 4.4, bevel=0.8, mat=mat)
    if post:
        slab(b, f, post, half=1.2, bevel=0.3, mat="dark")
    if drum:
        (dl, dh, dr) = drum
        dy, dz = f.P(dl, dh)
        b.lathe("x", (0, dy, dz), [(-gap, 0), (-gap, dr), (gap, dr), (gap, 0)], seg=14, mat="dark")


def knob(f, L, H_base, H_top, r, name):
    """The cocking knob on top (a knurled cap on a neck), axis vertical through L."""
    b = kit.Builder()
    yk = f.y(L)
    z0, z1 = f.z(H_base), f.z(H_top)
    b.lathe("z", (0, yk, 0), [(z0 - 1.0, 0), (z0 - 1.0, r * 0.5), (z0 + 3.0, r * 0.5), (z0 + 4.0, r),
                              (z1 - 1.5, r), (z1, r - 1.5), (z1, 0)], seg=24, mat="dark")
    return b.to_object(name)


def guard(b, f, outer, inner, half=2.6):
    b.strip(f.PL(outer), f.PL(inner), -half, half, mat="metal", bevel=0.5)


# ==================================================================================================
# The Uzi (Commons photo, left side, stock folded, 470 mm)
# ==================================================================================================

UZI = Frame(330.0, 140.0, 171.0)
UZI_W, UZI_W_HG, UZI_W_TH, UZI_W_GRIP = 21.0, 24.0, 17.0, 15.5
UZI_CANON_L = 64.0                 # the barrel nut's front face (where AWC's Mk9 took the nut's place)
UZI_MAG = (290.0, 142.5)           # the magazine's feed lips: its axis in the grip, 20-round base 22 mm under it
UZI_HINGE = (457.0, 165.0)


def uzi_body():
    f, b = UZI, kit.Builder()
    slab(b, f, [(93, 156), (93, 199), (158, 199), (161, 202), (235, 204.8), (320, 204.4), (353, 202.4), (394, 200.5),
                (442, 201), (442, 158)], half=UZI_W, bevel=1.4, res=1)
    # the stock's hinge block on the receiver's rear end
    slab(b, f, [(440, 158), (440, 190), (452, 190), (458, 184), (461, 172), (459, 160), (455, 156)], half=18.0,
         bevel=1.2)
    both(lambda s: b.lathe("x", (0, f.y(UZI_HINGE[0]), f.z(UZI_HINGE[1])),
                           [(s * 18.0, 0), (s * 18.0, 5.0), (s * 20.0, 5.0), (s * 20.0, 0)], seg=12, mat="dark"))
    # the trigger housing (grip frame) under the receiver, behind it the rear of the grip safety's housing
    slab(b, f, [(213, 141), (213, 158), (350, 158), (350, 135), (343, 129), (331, 129), (328, 133), (328, 141)],
         half=UZI_W_TH, bevel=1.2)
    slab(b, f, [(98, 145), (98, 184), (102, 189), (211, 189), (215, 185), (215, 145), (211, 141), (102, 141)],
         half=UZI_W_HG, bevel=3.0, res=1, mat="hg")
    slab(b, f, [(270.5, 141), (270.5, 55), (272, 50.5), (276, 47), (318, 46.5), (322, 50), (326, 58), (327.5, 72),
                (325.5, 91), (322.5, 98), (321, 102), (321, 141)], half=UZI_W_GRIP, bevel=3.0, res=1, mat="grip")
    slab(b, f, [(321, 136), (321, 103), (324, 101), (328, 102), (330, 107), (330, 133), (327, 136)], half=10.0,
         bevel=1.2, mat="dark")
    guard(b, f, [(217.5, 141), (217.5, 117), (220, 111), (225, 106.4), (231.4, 104.4), (251.3, 104), (266, 111),
                 (270.7, 115.1)],
          [(221, 141), (221, 118), (223, 114), (226, 110.5), (232, 108), (250.5, 108), (264, 114.5), (270.7, 119)])
    slab(b, f, [(249.3, 141), (252.1, 131.4), (251.3, 125.8), (249.7, 122.7), (246.5, 119.5), (242.1, 116.7),
                (242.5, 113.9), (245.3, 114.3), (249.7, 116.7), (255.2, 122.7), (257.2, 129.4), (257.2, 141)],
         half=3.0, bevel=0.5, mat="dark")
    # selector on the grip frame's left, above the grip
    slab(b, f, [(318, 147), (318, 152), (332, 153.5), (334, 150), (332, 146)], half=1.2, bevel=0.4, mat="dark",
         x0=UZI_W_TH + 0.8)
    sight_ears(b, f, [(96, 199), (96, 208), (99, 215), (105, 219.5), (112, 221), (119, 219.5), (125, 215), (128, 208),
                      (128, 199)], 6.0, [(95, 197), (95, 205), (129, 205), (129, 197)],
               post=[(110.5, 200), (110.5, 214), (113.5, 214), (113.5, 200)])
    sight_ears(b, f, [(396, 200), (396, 212), (400, 220.7), (409, 225.1), (419.6, 226.7), (427.5, 224.3),
                      (434.7, 217.5), (437, 210.8), (437, 200)], 8.5, [(395, 199), (395, 206), (438, 206), (438, 199)],
               drum=(418.0, 213.0, 8.5))
    barrel(b, f, 8.0, 16.5, UZI_CANON_L, 93.0)
    return b.to_object("UZI_BODY")


def uzi_stock_folded():
    """Folded under: the butt plate stands behind the grip, the struts run from its top along the receiver's
    bottom and down to its middle (the photo's curved brace)."""
    f, b = UZI, kit.Builder()
    slab(b, f, [(447, 150), (447, 58), (449, 52), (451.3, 46.4), (456, 46), (459, 47.2), (464, 54), (466.4, 63.5),
                (469.6, 140.9), (468, 144), (462.5, 150.4), (458, 160), (452, 160)], half=19.0, bevel=2.0, res=1)
    strut = [(349, 133), (349, 157.5), (446, 157.5), (446, 92), (442, 84.5), (437, 88.5), (430.7, 100.4), (425, 108.4),
             (412.8, 120.3), (400, 127.8), (386.6, 132.2), (364.8, 133)]
    window = [(408, 135), (432, 135), (440, 127), (440, 110), (433, 113), (420, 126)]
    both(lambda s: slab(b, f, strut, [window], half=2.0, bevel=0.5, x0=s * 18.5))
    slab(b, f, [(349, 150), (349, 157.5), (440, 157.5), (440, 150)], half=16.6, bevel=0.6)     # cross plate
    return b.to_object("UZI_STOCK_FOLDED")


def uzi_stock_deployed():
    """Unfolded: the struts run from the hinge straight back and a little down to the butt plate (640 mm long)."""
    f, b = UZI, kit.Builder()
    strut = [(452, 160), (452, 170), (461, 174), (614, 161), (618, 153), (614, 148), (461, 158)]
    both(lambda s: slab(b, f, strut, half=2.0, bevel=0.5, x0=s * 18.5))
    slab(b, f, [(612, 58), (612, 170), (616, 176), (630, 176), (636, 170), (640, 150), (640, 80), (634, 64),
                (626, 56), (616, 56)], half=19.0, bevel=2.0, res=1)
    slab(b, f, [(600, 150), (600, 160), (612, 160), (612, 150)], half=16.6, bevel=0.6)     # cross bar
    return b.to_object("UZI_STOCK_DEPLOYED")


# ==================================================================================================
# The Mini Uzi (user's photo, left side, stock deployed, 600 mm)
# ==================================================================================================

MINI = Frame(258.0, 112.0, 145.0)
MINI_W, MINI_W_HG, MINI_W_TH, MINI_W_GRIP = 20.0, 23.0, 16.0, 15.5
MINI_CANON_L = 40.0
MINI_MAG = (219.0, 118.0)
MINI_HINGE = (350.0, 150.0)


def mini_body():
    f, b = MINI, kit.Builder()
    slab(b, f, [(66, 124), (66, 172), (100, 174), (126.5, 173.5), (138.3, 177.4), (171.5, 179.3), (242.6, 178),
                (286.3, 173.5), (322, 172), (340, 170), (340, 124)], half=MINI_W, bevel=1.4, res=1)
    slab(b, f, [(338, 128), (338, 170), (345, 170), (352, 166), (357, 156), (357, 136), (350, 130)], half=17.0,
         bevel=1.0)
    slab(b, f, [(148, 110), (148, 125), (276, 125), (268, 119), (262, 110)], half=MINI_W_TH, bevel=1.2)
    slab(b, f, [(70, 116), (70, 166), (74, 170), (146, 170), (150, 166), (150, 116), (146, 112), (74, 112)],
         half=MINI_W_HG, bevel=3.0, res=1, mat="hg")
    slab(b, f, [(200.9, 111), (200.9, 37.8), (201.5, 30), (205, 25.5), (236.7, 24), (247.8, 24.1), (256.3, 34.6),
                (258.3, 39.8), (258.9, 55.4), (257.6, 69.1), (254.3, 75), (254.3, 111)], half=MINI_W_GRIP,
         bevel=3.0, res=1, mat="grip")
    slab(b, f, [(254.3, 108), (254.3, 77), (257.6, 76.3), (260.2, 80.2), (259.5, 103.7), (263, 108)], half=10.0,
         bevel=1.2, mat="dark")
    guard(b, f, [(148, 110), (150, 89.3), (153.3, 85.4), (159.1, 82.2), (184.6, 81.5), (200.9, 90.7)],
          [(152.6, 110), (152.6, 94.6), (155.9, 90), (159.8, 88), (180.7, 87.4), (200.9, 96.5)])
    slab(b, f, [(184, 110), (183.5, 103), (181, 97.5), (177, 92.5), (172.5, 90.7), (172.8, 94.5), (176.5, 97.5),
                (178.5, 102), (178.8, 110)], half=3.0, bevel=0.5, mat="dark")
    slab(b, f, [(244, 116), (244, 120.5), (257, 122), (259, 119), (257, 115)], half=1.2, bevel=0.4, mat="dark",
         x0=MINI_W_TH + 0.8)
    sight_ears(b, f, [(74.3, 172), (74.3, 182.6), (77, 187.2), (82.8, 191.7), (88.7, 193), (94.6, 191.7),
                      (99.8, 187.8), (101.7, 184.6), (101.7, 172)], 5.5, [(73, 170), (73, 177), (103, 177), (103, 170)],
               post=[(86.5, 172), (86.5, 187), (89.5, 187), (89.5, 172)])
    sight_ears(b, f, [(287, 172), (288.9, 185.9), (294.1, 191.7), (298, 193.7), (310.4, 194.3), (316.3, 191.7),
                      (322.2, 185.9), (324, 172)], 8.0, [(286, 170), (286, 176), (325, 176), (325, 170)],
               drum=(305.0, 182.0, 8.0))
    barrel(b, f, 7.2, 14.5, MINI_CANON_L, 66.0)
    return b.to_object("MINIUZI_BODY")


def mini_stock():
    """Origin at the hinge pin (MINI_HINGE, x on the right); modelled deployed as photographed: one bent strut and a
    slanted butt plate, the butt a little toward the middle."""
    f = Frame(MINI_HINGE[0], MINI_HINGE[1], MINI.bore)
    b = kit.Builder()
    hx = -(MINI_W + 3.0)
    b.lathe("z", (0, 0, 0), [(-14.0, 0), (-14.0, 5.5), (16.0, 5.5), (16.0, 0)], seg=12, mat="dark")
    strut = [(350, 157), (392.6, 153.3), (425.2, 144.1), (461.7, 127.8), (572, 110.5), (572, 93), (545.9, 95.9),
             (452, 112.2), (440.2, 116.7), (413.5, 131.1), (402.4, 135), (350, 143)]
    slab(b, f, strut, half=4.0, bevel=1.0, res=1)
    slab(b, f, [(569, 112), (570, 92), (581.1, 17.6), (585.7, 10.4), (590.9, 11.1), (595.4, 14.3), (599.3, 22.8),
                (600, 32), (591.5, 95.2), (588.3, 108.9), (579.8, 116.7), (574, 116.7)], half=13.0, bevel=2.0, res=1,
         x0=-hx * 0.5)
    ob = b.to_object("MINIUZI_STOCK")
    return ob


# ==================================================================================================
# The Micro Uzi (user's photo, left side, stock folded forward, 257 mm)
# ==================================================================================================

MICRO = Frame(186.0, 110.0, 133.5)
MICRO_W, MICRO_W_TH, MICRO_W_GRIP = 19.5, 15.5, 15.5
MICRO_CANON_L = 38.0
MICRO_MAG = (147.0, 118.0)
MICRO_HINGE = (250.0, 142.0)


def micro_body():
    f, b = MICRO, kit.Builder()
    slab(b, f, [(50, 117), (50, 160), (54, 162.5), (104, 164.7), (174.4, 165.8), (188.4, 165.2), (205, 163),
                (237, 160), (252.1, 159.8), (254.3, 153.9), (254.3, 121), (250, 117)], half=MICRO_W, bevel=1.4, res=1)
    slab(b, f, [(240, 120), (240, 156), (250, 158), (256.5, 152.3), (257, 138.8), (254.8, 128), (248, 120)],
         half=17.0, bevel=1.0)
    slab(b, f, [(82, 108), (82, 118), (192, 118), (192, 110), (188, 107)], half=MICRO_W_TH, bevel=1.2)
    slab(b, f, [(128.5, 110), (128.5, 26), (129.6, 22), (133, 20), (164, 20), (176.6, 23.8), (182, 30.8),
                (183.6, 40), (183.6, 55.6), (181.4, 66.9), (181.4, 110)], half=MICRO_W_GRIP, bevel=3.0, res=1,
         mat="grip")
    slab(b, f, [(181.4, 104), (181.4, 68.6), (183.6, 68.6), (185.2, 74), (185.2, 101), (188, 106)], half=10.0,
         bevel=1.2, mat="dark")
    guard(b, f, [(85, 110), (85, 95), (80, 87), (84, 81.5), (111, 75), (128.5, 79)],
          [(89.5, 110), (89.5, 94), (86.5, 89), (100, 85.5), (111, 79.5), (128.5, 83)])
    slab(b, f, [(110.5, 110), (110.7, 101), (109.6, 96), (106, 92.5), (103, 91.5), (104, 94), (106.5, 97), (107, 103),
                (106.5, 110)], half=3.0, bevel=0.5, mat="dark")
    slab(b, f, [(172, 112), (172, 116.5), (185, 117.5), (187, 114.5), (185, 111)], half=1.2, bevel=0.4, mat="dark",
         x0=MICRO_W_TH + 0.8)
    sight_ears(b, f, [(55.1, 160), (55.1, 172.2), (59.9, 177.1), (67.5, 176.6), (76.7, 166.3), (77.7, 160)], 5.0,
               [(54, 159), (54, 165), (78, 165), (78, 159)], post=[(64.5, 160), (64.5, 173), (67.5, 173), (67.5, 160)])
    sight_ears(b, f, [(207.3, 160), (207.3, 170.6), (212.2, 175.5), (216.5, 177.1), (227.3, 177.1), (234.9, 170.6),
                      (235.4, 160)], 7.5, [(206, 158.5), (206, 164), (236, 164), (236, 158.5)],
               drum=(221.0, 169.0, 7.0))
    barrel(b, f, 8.0, 15.0, MICRO_CANON_L, 50.0)
    return b.to_object("MICROUZI_BODY")


def micro_stock():
    """Origin at the hinge pin (MICRO_HINGE, x on the right); modelled deployed, i.e. the photo's folded stock
    turned back half a turn about the pin: L' = 2 x 250 - L. The strut bends down from the hinge toward the butt."""
    f = Frame(MICRO_HINGE[0], MICRO_HINGE[1], MICRO.bore)
    b = kit.Builder()
    hx = -(MICRO_W + 3.0)
    m = lambda pts: [(2.0 * MICRO_HINGE[0] - L, H) for L, H in pts]
    b.lathe("z", (0, 0, 0), [(-14.0, 0), (-14.0, 5.0), (14.0, 5.0), (14.0, 0)], seg=12, mat="dark")
    strut = m([(250, 150), (180, 150), (110, 128), (64, 126), (62, 116), (110, 118), (180, 140), (250, 136)])
    slab(b, f, strut, half=3.5, bevel=1.0, res=1)
    butt = m([(66.4, 126), (66.4, 37.8), (64.8, 32.4), (59.4, 31.3), (54.5, 37.8), (51.8, 52.4), (49.1, 99.3),
              (50.2, 118), (56, 126)])
    slab(b, f, butt, half=11.0, bevel=2.0, res=1, x0=-hx * 0.5)
    return b.to_object("MICROUZI_STOCK")


# ==================================================================================================
# Magazines (shared): IMI's steel double-stack magazines, straight, hanging from the feed lips
# ==================================================================================================

MAG_LEN = {20: 118.0, 25: 142.0, 32: 175.6, 40: 214.0, 50: 262.0}   # feed lips to base, 4.8 mm a round
MAG_W, MAG_D = 11.5, 16.5          # half width (across), half depth (front to back)
MAG_BASE = 6.0


def mag_name(r):
    return "9x19Magazine%d_UZI" % r


def build_magazine(r):
    """Origin at the feed lips (top centre); the body straight down along -Z, a narrower lip section at the top, a
    stamped rib down each side, the base plate, the top round with its bullet forward (+Y)."""
    b = kit.Builder()
    L = MAG_LEN[r]
    b.box(-MAG_W, MAG_W, -MAG_D, MAG_D, -(L - MAG_BASE), -6.0, mat="magmetal", bevel=1.0)
    b.box(-MAG_W + 2.5, MAG_W - 2.5, -MAG_D + 1.5, MAG_D - 3.0, -6.5, 0.0, mat="magmetal", bevel=0.8)   # feed lips
    for s in (1, -1):                                                    # the stamped rib down each side
        xa, xb = sorted((s * (MAG_W - 0.8), s * (MAG_W + 0.6)))
        b.box(xa, xb, -4.0, 4.0, -(L - MAG_BASE - 8.0), -16.0, mat="magmetal", bevel=0.4)
    b.box(-MAG_W - 1.0, MAG_W + 1.0, -MAG_D - 1.2, MAG_D + 1.2, -L, -(L - MAG_BASE), mat="dark", bevel=1.0)
    b.lathe("y", (0, -2.0, -4.2), [(-12.5, 0), (-12.5, 4.9), (6.0, 4.9), (6.5, 4.5)], seg=8, mat="brass")
    b.lathe("y", (0, -2.0, -4.2), [(6.5, 4.5), (11.0, 4.2), (14.5, 2.4), (15.7, 0)], seg=8, mat="copper")
    return b.to_object(mag_name(r))


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: IMI's black-grey phosphate steel, black plastic grip and handguard, blued barrel
    "metal": (52, 53, 56), "polymer": (36, 36, 38), "grip": (34, 34, 36), "dark": (22, 22, 23), "barrel": (44, 45, 48),
    "hg": (36, 36, 38), "magmetal": (58, 58, 60), "brass": (150, 118, 62), "copper": (140, 82, 52),
}
rounded_rect = kit.rounded_rect


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "barrel", "magmetal", "brass", "copper", "dark")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.98 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 70.0, 50.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def groove(col, sel, L, H, La, Lb, Ha, Hb):
    """A pressed groove in the stamped receiver: dark floor, a lighter lip along its top."""
    r = (Hb - Ha) / 2.0
    col[sel & rounded_rect(L, H, La, Lb, Ha, Hb, r)] *= 0.55
    col[sel & rounded_rect(L, H, La, Lb, Hb, Hb + 0.9, 0.4)] += 16


def knurl(col, sel, ang, pitch_deg=10.0):
    col[sel & (np.mod(np.degrees(ang), pitch_deg) < pitch_deg * 0.45)] *= 0.55


# per gun: (frame, side grooves [(La, Lb, Ha, Hb)], port recess, slot plates, markings, handguard, pins, grip panel)
SPEC = {
    "UZI": dict(frame=UZI, w=UZI_W, w_th=UZI_W_TH, w_grip=UZI_W_GRIP, knob=(187.5, 9.5),
                grooves=[(345, 405, 166, 172), (345, 405, 177, 183), (226, 266, 166, 172), (226, 266, 177, 183),
                         (130, 214, 192, 196)],
                port=(270, 322, 178, 200), th_slot=[(268, 340, 145, 154), (226, 262, 147.5, 151.5)],
                pins=[(316, 150), (284, 150), (242, 150), (402, 182), (402, 168), (125, 150), (200, 150)],
                text=[("UZI", 405.0, 186.0, 5.0), ("9MM", 405.0, 160.5, 3.5)], right_text=("IMI", 430.0, 172.0, 5.0),
                grip=(271.0, 326.0, 52.0, 112.0), hg=(98.0, 215.0), sel=((318, 155.5), (325, 155.5), (332, 155.5)),
                ribs_hg=True),
    "MINIUZI": dict(frame=MINI, w=MINI_W, w_th=MINI_W_TH, w_grip=MINI_W_GRIP, knob=(161.5, 9.5),
                    grooves=[(265, 325, 137, 143), (265, 325, 147, 153), (200, 240, 137, 143), (200, 240, 147, 153),
                             (155, 195, 137, 143), (155, 195, 147, 153)],
                    port=(175, 232, 155, 172), th_slot=[(175, 232, 114, 122)],
                    pins=[(255, 118), (228, 118), (183, 118), (130, 130), (100, 130)],
                    text=[("MINI", 296.0, 158.0, 4.0), ("UZI", 296.0, 128.0, 4.5)],
                    right_text=("IMI", 315.0, 150.0, 5.0), grip=(202.0, 257.0, 30.0, 90.0), hg=(70.0, 150.0),
                    sel=((244, 124.5), (250, 124.5), (256, 124.5)), ribs_hg=True),
    "MICROUZI": dict(frame=MICRO, w=MICRO_W, w_th=MICRO_W_TH, w_grip=MICRO_W_GRIP, knob=(93.0, 5.0),
                     grooves=[(115, 165, 142, 148), (175, 200, 142, 148), (95, 125, 142, 148)],
                     port=(130, 170, 135, 162), th_slot=[(125, 170, 111, 116)],
                     pins=[(178, 113), (150, 113), (105, 113), (230, 128)],
                     text=[("MICRO", 202.0, 128.0, 3.5), ("UZI", 208.0, 121.0, 3.5)],
                     right_text=("IMI", 215.0, 140.0, 4.5), grip=(130.0, 182.0, 28.0, 85.0), hg=None,
                     sel=((172, 120), (178, 120), (184, 120)), ribs_hg=False),
}


def paint_gun(maps, kind, col):
    s = SPEC[kind]
    f = s["frame"]
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = f.L0 - y, z + f.H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    metal = mat == MATS.index("metal")
    rec = metal & side & (np.abs(x) > s["w"] - 0.6)
    th = metal & side & (np.abs(x) > s["w_th"] - 0.6) & (np.abs(x) < s["w_th"] + 0.6)
    for g in s["grooves"]:
        groove(col, rec, L, H, *g)
    # the left side's stamped recess over the bolt (as photographed), the ejection port on the right with the bolt
    La, Lb, Ha, Hb = s["port"]
    col[rec & left & rounded_rect(L, H, La, Lb, Ha, Hb, 2.0)] *= 0.62
    col[rec & left & rounded_rect(L, H, La - 1.2, Lb + 1.2, Hb, Hb + 1.0, 0.4)] += 14
    port = rec & right & rounded_rect(L, H, La, Lb, Ha + 2.0, Hb - 2.0, 2.0)
    col[port] = col[port] * 0.2 + 10
    col[port & (np.abs(H - (Ha + Hb) / 2.0) < (Hb - Ha) * 0.22)] += 30                     # the bolt's side
    for (La, Lb, Ha, Hb) in s["th_slot"]:
        col[th & rounded_rect(L, H, La, Lb, Ha, Hb, 2.0)] *= 0.6
        col[th & rounded_rect(L, H, La, Lb, Hb, Hb + 0.9, 0.4)] += 14
    for cL, cH in s["pins"]:
        pin(col, L, H, (rec | th), cL, cH)
    # markings: left side reads in game with u = +L, right side u = -L (build_ump.py)
    for text, u0, v0, hgt in s["text"]:
        col[rec & left & kit.text_mask(L, H, text, u0, v0, hgt)] += 34
    text, u0, v0, hgt = s["right_text"]
    col[rec & right & kit.text_mask(-L, H, text, -u0 - 13.0, v0, hgt)] += 34
    # selector letters above the grip on the left (S safe, R repeat, A automatic)
    for (cL, cH), ch, c in zip(s["sel"], "ARS", ((186, 46, 40), (205, 205, 200), (205, 205, 200))):
        col[(th | rec) & left & kit.text_mask(L, H, ch, cL - 1.5, cH - 1.5, 3.0)] = c
    # grip: the horizontal ribs of the moulded panel, bounded by a diagonal at the top front
    gm = (mat == MATS.index("grip")) & side & (np.abs(x) > s["w_grip"] - 0.8)
    gLa, gLb, gHa, gHb = s["grip"]
    panel = gm & (L > gLa + 6.0) & (L < gLb - 4.0) & (H > gHa) & (H < gHb) & ((H - gHb) < -(gLb - L) * 0.9 + 20.0)
    col[panel & (np.mod(H, 2.4) < 1.0)] *= 0.6
    col[panel & (np.mod(H, 2.4) >= 1.0)] += 6
    for k in range(2):                                                    # the two grip screws
        pin(col, L, H, gm, gLb - 14.0, gHa + 12.0 + k * 28.0, 3.0)
    # handguard: the vertical ribs all round it
    if s["hg"]:
        hg = mat == MATS.index("hg")
        La, Lb = s["hg"]
        ribs = hg & (L > La + 6.0) & (L < Lb - 5.0) & (np.abs(n[..., 1]) < 0.6)
        col[ribs & (np.mod(L, 3.3) < 1.3)] *= 0.55
        col[ribs & (np.mod(L, 3.3) >= 1.3)] += 8
        for cL in (La + 27.0, Lb - 15.0):
            pin(col, L, H, hg & side, cL, f.bore - 21.0, 3.2)
    # the barrel nut's knurling, the bore, the Mini's compensator cuts on top near the muzzle
    zb = f.bore - f.H0
    ang = np.arctan2(x, z - zb)
    dark = mat == MATS.index("dark")
    nut = dark & (np.hypot(x, z - zb) > 10.0) & (np.abs(n[..., 1]) < 0.6) & (L < 100) & (L > 30)
    knurl(col, nut, ang, 8.0)
    col[nut & (np.mod(L, 1.6) < 0.6)] *= 0.7
    bar = mat == MATS.index("barrel")
    col[bar & (np.hypot(x, z - zb) < 4.6) & (L < 0.8)] = 6
    if kind == "MINIUZI":
        for k in range(3):
            col[bar & (z - zb > 4.0) & (np.abs(x) < 1.4) & (np.abs(L - (4.0 + k * 4.5)) < 1.2)] = 8


def paint_knob(maps, kind, col):
    f = SPEC[kind]["frame"]
    p, n = maps["pos"], maps["nrm"]
    x, y = p[..., 0], p[..., 1]
    yk = f.y(SPEC[kind]["knob"][0])
    side = np.abs(n[..., 2]) < 0.5
    knurl(col, side & (np.hypot(x, y - yk) > SPEC[kind]["knob"][1] - 0.8), np.arctan2(x, y - yk), 12.0)


def paint(maps, kind):
    p, mat = maps["pos"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    gun, part = kind
    if part == "body":
        paint_gun(maps, gun, col)
    elif part == "knob":
        paint_knob(maps, gun, col)
    elif part == "mag":
        n = maps["nrm"]
        x, z = p[..., 0], p[..., 2]
        s = -z
        side = np.abs(n[..., 0]) > 0.7
        body = (mat == MATS.index("magmetal")) & side & (np.abs(x) > MAG_W - 0.6)
        r = gun
        back = MAG_LEN[r] - s
        for face, uu in ((body & (n[..., 0] > 0.7), p[..., 1]), (body & (n[..., 0] < -0.7), -p[..., 1])):
            col[face & kit.text_mask(uu, back, str(r), -4.0, MAG_BASE + 10.0, 5.0)] += 36
        # witness holes down the back edge
        for k in range(int((MAG_LEN[r] - 30) // 24)):
            col[side & (np.hypot(p[..., 1] + MAG_D - 4.0, s - (24.0 + k * 24.0)) < 1.6)] = 12
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

def points(kind, bounds):
    f = SPEC[kind]["frame"]
    canon_L = {"UZI": UZI_CANON_L, "MINIUZI": MINI_CANON_L, "MICROUZI": MICRO_CANON_L}[kind]
    mag = {"UZI": UZI_MAG, "MINIUZI": MINI_MAG, "MICROUZI": MICRO_MAG}[kind]
    pts = {
        "muzzle": {"offset": f.gp(0.0, f.bore), "rotate": [-90.0, 0.0, -180.0]},
        # the barrel nut's front face: the 9x19mm SMG mount device and the Mk9 start here, along +Y
        "canon": {"offset": f.gp(canon_L, f.bore), "rotate": ZERO},
        "magazine": {"offset": f.gp(*mag), "rotate": ZERO},
        "bolt_fired": {"offset": ZERO, "rotate": ZERO},
    }
    notes = {
        "canon": "the barrel nut's front face (%.0f mm behind the muzzle): GunsOfTien.SMG9_Muzzle_Mount_Device and "
                 "Mk9_Suppressor start here" % canon_L,
        "magazine": "the shared 9x19Magazine*_UZI meshes hang straight down from here (their feed lips); the 20-round's "
                    "base 22 mm under the grip",
        "bolt_fired": "the cocking knob on top does not reciprocate",
    }
    if kind == "UZI":
        pts["world"] = {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0], "rotate": [180.0, 0.0, 180.0]}  # every GoM rifle's, scaled
        notes["stock"] = ("UZI_STOCK_FOLDED / _DEPLOYED are modelled in place in the gun's space (GoM's MAC-10 way): "
                          "no point, drawn at the origin")
        handgun = False
    else:
        hl, hh = MINI_HINGE if kind == "MINIUZI" else MICRO_HINGE
        hx = -(SPEC[kind]["w"] + 3.0)
        hinge = f.gp(hl, hh, hx)
        pts["stock"] = {"offset": hinge, "rotate": ZERO}
        pts["stock_folded"] = {"offset": hinge, "rotate": [0.0, 0.0, 180.0]}
        notes["stock"] = ("%s_STOCK is modelled deployed with its origin at the hinge pin (photo L %.0f, H %.0f, %.0f "
                          "mm right of centre); stock_folded turns it half a turn about Z through the pin, forward "
                          "along the right side" % (kind, hl, hh, -hx))
        # held like a pistol: everything turned with the gun (build_mp7.py's turned()); the magazine (upright) gets
        # TURN; muzzle and canon keep GoM's MP5K values; the stock is a node of the gun's own file, turned with it,
        # and a half turn about Z commutes with the turn about Y, so its rotates stay
        pts = {k: kit.turned(v, part=(k == "magazine")) for k, v in pts.items()}
        pts["magazine"]["rotate"] = list(kit.TURN)
        pts["world"] = {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": ZERO}  # GoM's MP5K / MAC-10, scaled
        handgun = True
    pts["_notes"] = dict(notes, units="game units (0.603 of real size, the M16A2's proportion); +Y muzzle; " + (
        "held like a pistol, so modelled upside down as GoM's MP5K / MAC-10: +Z the gun's BOTTOM, +X its RIGHT"
        if handgun else "+Z top, +X the gun's left") + "; origin = rear-top of the grip (photo L %.0f, H %.0f)"
        % (f.L0, f.H0))
    pts["_extras"] = {"handgun_hold": handgun, "photo_origin_mm": [f.L0, f.H0], "bore_mm": f.bore, "k": K}
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

    guns = {
        "UZI": [uzi_body(), knob(UZI, 187.5, 204.0, 220.5, 9.5, "UZI_BOLT"), uzi_stock_folded(),
                uzi_stock_deployed()],
        "MINIUZI": [mini_body(), knob(MINI, 161.5, 178.0, 192.0, 9.5, "MINIUZI_BOLT"), mini_stock()],
        "MICROUZI": [micro_body(), knob(MICRO, 93.0, 164.5, 180.0, 5.0, "MICROUZI_BOLT"), micro_stock()],
    }
    mags = [build_magazine(r) for r in MAG_LEN]
    for objs in guns.values():
        kit.unwrap(objs, 0.006)
    for m in mags:
        kit.unwrap([m], 0.012)

    all_points = {}
    for kind, objs in guns.items():
        body, bolt = objs[0], objs[1]
        stocks = objs[2:]
        maps = [bake(body, [body, bolt], 256), bake(bolt, [body, bolt], 256)]
        kinds = [(kind, "body"), (kind, "knob")]
        for st in stocks:
            ctx = [st, body] if kind == "UZI" and st.name.endswith("FOLDED") else [st]
            maps.append(bake(st, ctx, 256))
            kinds.append((kind, "stock"))
        texture(maps, kinds, 256, os.path.join(TEX_DIR, kind + ".png"))
        handgun = kind != "UZI"
        if handgun:                                        # held like a pistol: turned 180 degrees about the bore
            for o in objs:
                o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
        bounds = {o.name: kit.bounds_of(o) for o in objs}
        pts = points(kind, bounds)
        if handgun:
            bounds[kind + "_STOCK_folded"] = kit.bounds_at(stocks[0], pts["stock_folded"])
        all_points[kind] = pts
        kit.export(objs, os.path.join(FBX_DIR, "GunsOfTien_%s.fbx" % kind))
    for r, m in zip(MAG_LEN, mags):
        texture([bake(m, [m], 128)], [(r, "mag")], 128, os.path.join(TEX_DIR, m.name + ".png"))
    all_points["_mags"] = {m.name: kit.bounds_of(m) for m in mags}
    kit.export(mags, FBX_MAGS)
    with open(POINTS_JSON, "w") as fh:
        json.dump(all_points, fh, indent=2)
        fh.write("\n")
    for kind, pts in all_points.items():
        for name, b in (pts.get("_bounds") or pts).items():
            print("%-10s %-24s tris %5d  min %s  max %s" % (kind, name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
