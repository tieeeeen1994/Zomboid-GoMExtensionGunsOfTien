"""Desert Tech MDRx .223 and .308 models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_mdr.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_MDR223.fbx       MDR223_BODY, _BOLT, _HANDLE, _RAIL_LEFT, _RAIL_RIGHT
    P/models_X/weapons/firearms/GunsOfTienPost93_MDR308.fbx       MDR308_BODY, _BOLT, _HANDLE, _RAIL_LEFT, _RAIL_RIGHT,
                                                                  _BIPOD_FOLDED, _BIPOD_DEPLOYED (on MDR308_BIPOD.png)
    P/models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx  762x51Magazine10_PMAG, 762x51Magazine20_PMAG,
                                                                  762x51Magazine25_PMAG, 762x51Magazine50_PMAG (D-50)
    P/textures/weapons/GunsOfTienPost93/<name>.png                MDR223 (black), MDR308 (flat dark earth), 256;
                                                                  128 for each magazine
    scripts/post93/mdr223_points.json, mdr308_points.json         attachment points (game space)

Design: docs/post93_design.md, "Desert Tech MDRx .223 and .308". One MDRx chassis for both guns, traced from Desert
Tech's right-side photo (muzzle right) of a flat dark earth 16" MDRx (references/mdr/deserttech/c196b688..., not in the repo:
trace_outline.py at --length 698.5, the 16" forward-eject rifle's published 27.5"; its height then reads 198.5 mm
against the published 200.4, and its top rail's crossbars 9.9 mm apart). Profiles are in that photo's (L, H) mm: L back
from the muzzle tip, H up from the pistol grip's bottom. Real rifles Desert Tech sold (user, 2026-11-04):
  - MDR223: .223 Wylde, 16" barrel, side ejection, black: the port is a window in the right side's panel, the left
    side carries the plain cover of Desert Tech's forward-to-side kit.
  - MDR308: 7.62 NATO, 20" barrel (101.6 mm longer, the muzzle device moved out with it), forward ejection, flat
    dark earth: the forward-eject chute panel on both sides (as both photos show), its viewing window on the right.
    BLK LBL's 20" ALX bipod handguard in place of the polymer one (user, 2026-11-04; "ALX" below): an aluminium
    M-LOK frame whose two legs (MDR308_BIPOD_FOLDED / _DEPLOYED, gun space, drawn at `integrated_bipod`) fold back
    flush into its underside from a pivot at the nose.
Both take GoM's optional left and right Picatinny rails as our short M-LOK sections (MDR*_RAIL_LEFT / _RIGHT, origin
on the handguard's side face, drawn at rail_left / rail_right), GoM's lights and lasers on them (user, 2026-11-04).
Both have the ambidextrous non-reciprocating charging handle at the front of the upper's slot (MDR*_HANDLE, back only
while racked) and the bolt carrier seen in the right side's window (MDR*_BOLT, GoM's Bolt swap). The magazine well is
behind the grip: GoM's STANAG magazines (the .223, through the main mod's `_GoT` models) and our SR-25-pattern PMAGs
(the .308) hang from `magazine`, their feed lips, placed so GoM's STANAG 30 shows below the well where the black
16" .223's PMAG does in Midwest Gun Works' photo (references/mdr/retail).

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, 0.603 of real size (the M16A2's proportion, as every gun of ours).
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
FIRE_DIR = os.path.join(MEDIA, "models_X/weapons/firearms")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_PMAG_magazines.fbx")

K = 0.000603                       # game units per real mm (the M16A2's proportion)
K_OLD = 0.00065                    # GoM's rifles' (the `world` point is scaled from it, as on the SCARs)
kit.K = K
MATS = ["polymer", "upper", "dark", "metal", "rubber", "brass", "copper", "magpoly", "alx", "leg", "carbon"]
kit.MATS[:] = MATS

# ==================================================================================================
# The chassis (photo L, H mm)
# ==================================================================================================

L0, H0 = 388.0, 104.0              # origin: the grip's back meets the trigger housing
BORE_H = 153.4                     # the muzzle device's axis
TWENTY = 101.6                     # the 20" barrel against the photographed 16"

W_CHASSIS, W_UPPER, W_HG, W_RISER, W_PAD = 25.0, 25.6, 26.0, 26.2, 25.9
W_GRIP, W_GUARD = 15.0, 7.0
RAIL_FLOOR, RAIL_TOP = 193.6, 197.0
UPPER_RAIL = (242.0, 470.0)        # the upper receiver's rail
HG_RAIL = (117.0, 225.0)           # the handguard's rail
HG_BOTTOM = 130.3                  # the handguard's underside (foregrips)

# the polymer chassis: butt, magazine well, trigger housing (the upper and handguard are drawn over it)
CHASSIS = [(262.0, 113.0), (282.0, 135.0), (282.0, 175.0), (694.9, 172.9), (698.5, 166.7), (697.6, 164.9),
           (698.1, 156.3), (697.2, 150.9), (695.4, 137.0), (693.1, 126.7), (690.4, 112.7), (688.2, 105.1),
           (686.4, 94.8), (684.6, 83.1), (681.4, 73.2), (678.3, 63.3), (674.7, 52.6), (673.3, 47.2), (671.1, 42.7),
           (665.7, 38.2), (657.6, 36.8), (620.3, 36.8), (615.4, 38.6), (609.6, 40.4), (603.3, 45.8), (599.2, 51.7),
           (596.1, 57.9), (592.9, 62.4), (589.3, 71.4), (586.2, 75.9), (558.8, 75.5), (551.6, 71.4), (551.6, 66.5),
           (544.4, 67.4), (510.7, 73.2), (460.9, 80.9), (457.3, 81.8), (455.9, 83.1), (456.8, 87.6), (453.7, 100.2),
           (451.9, 104.7), (448.3, 106.9), (448.3, 110.1), (446.1, 111.8), (406.5, 112.7), (396.2, 112.3),
           (388.0, 104.0), (340.0, 101.0), (275.4, 99.3), (270.9, 99.3), (267.7, 100.6), (264.6, 104.7),
           (264.1, 108.7)]
# the aluminium upper receiver, its rail on top; its front under the handguard's rear
UPPER = [(241.0, 184.0), (241.0, RAIL_FLOOR), (470.0, RAIL_FLOOR), (477.9, 187.8), (648.6, 187.8), (652.7, 183.3),
         (681.0, 182.5), (681.0, 153.0), (650.0, 133.0), (285.0, 133.0), (262.0, 150.0)]
# the cheek riser over the upper's rear, the rubber butt pad
RISER = [(484.0, 187.8), (648.6, 187.8), (652.0, 184.0), (642.0, 169.0), (632.0, 165.0), (504.0, 165.0)]
PAD = [(681.0, 182.5), (690.9, 181.0), (692.7, 179.2), (694.9, 172.9), (698.5, 166.7), (697.6, 164.9),
       (698.1, 156.3), (697.2, 150.9), (695.4, 137.0), (693.1, 126.7), (690.4, 112.7), (688.2, 105.1),
       (686.4, 94.8), (684.6, 83.1), (681.4, 73.2), (678.3, 63.3), (674.7, 52.6), (673.3, 47.2), (671.1, 42.7),
       (665.7, 38.2), (657.6, 36.8), (655.5, 40.0), (661.0, 70.0), (668.0, 110.0), (674.0, 150.0), (678.5, 175.0)]
# the handguard: hand stop hooking down at its nose, its rail on top, its rear tucked under the upper's front
HANDGUARD = [(66.9, 121.3), (66.9, 162.2), (75.0, 172.9), (85.3, 183.3), (93.9, 186.0), (114.5, RAIL_FLOOR),
             (225.5, RAIL_FLOOR), (227.3, 185.1), (240.0, 184.0), (293.0, 161.0), (265.0, 112.5), (261.0, 112.7),
             (253.8, 118.6), (250.7, 119.0), (245.3, 122.6), (237.2, 124.4), (231.8, 127.1), (223.7, 128.0),
             (217.4, 130.7), (91.6, HG_BOTTOM), (89.4, 129.4), (85.3, 129.4), (83.1, 127.6), (81.3, 125.3),
             (80.0, 119.0), (77.7, 117.2), (69.6, 116.3), (67.8, 117.7)]
# the upper row of M-LOK slots is open (the photo's background shows through); the lower row is painted
MLOK_TOP = [(188.0, 211.0), (159.0, 181.0), (130.0, 149.0), (100.0, 119.0)]
MLOK_TOP_H = (176.0, 181.0)
MLOK_LOW = [(158.0, 192.0), (117.0, 150.0), (74.0, 108.0)]
MLOK_LOW_H = (154.0, 161.0)
FRONT_BLOCK = [(227.3, 184.0), (227.3, 198.1), (231.8, 198.1), (232.7, 195.4), (236.7, 195.4), (237.6, 198.5),
               (241.7, 198.1), (241.7, 184.0)]
GRIP = [(342.7, 68.7), (344.1, 62.4), (357.1, 13.9), (357.1, 10.8), (354.4, 4.5), (354.9, 2.2), (356.7, 0.9),
        (360.3, 0.0), (392.6, 7.2), (398.4, 9.4), (402.9, 13.0), (402.5, 20.7), (400.7, 31.0), (397.1, 46.7),
        (390.4, 65.1), (385.0, 76.4), (381.4, 88.0), (382.7, 96.6), (386.8, 103.8), (389.0, 108.0), (340.0, 108.0),
        (338.7, 75.0)]
# (2026-11-13, trigger audit: the guard's top edge, hidden in the chassis, was within two bevels of the opening's top, so
# the bevel's offsets crossed and the curve fill closed the opening's top and buried the trigger; it now reaches
# 6.5 mm up inside the chassis. See kit.slab in CLAUDE.md, "Slab holes and bevels".)
GUARD = [(345.0, 106.0), (338.7, 68.3), (320.3, 62.0), (283.9, 67.8), (282.1, 71.0), (275.4, 97.5), (273.6, 99.3),
         (275.0, 106.0)]
GUARD_HOLE = [(332.4, 99.5), (285.2, 99.5), (283.9, 96.6), (283.4, 85.8), (286.6, 73.2), (288.4, 71.9), (318.9, 67.4),
              (334.7, 72.3), (337.3, 75.5), (337.8, 79.5)]
# Desert Tech's skeletonised trigger (trigger audit 2026-11-14, read off references/mdr/deserttech's studio right side,
# the model registered on it at 2.23 px a mm, IoU 0.98): a curved front blade (face L 315.9 at the top, 316.8 at H 94,
# 314.6 at the tip) and a straight rear bar (L 322.2-324, flaring to 326.7 at the top), joined at the tip (H 71.4) and
# by a brace at H 91-92.5, two narrow windows between. It was a thin diagonal blade, its face about 3 mm back.
TRIGGER = [(327.5, 101.0), (326.7, 99.2), (325.0, 96.5), (324.0, 93.8), (324.0, 78.5), (323.6, 77.0), (322.5, 76.0),
           (320.0, 74.5), (318.0, 73.0), (316.5, 71.5), (315.5, 71.0), (314.6, 71.6), (314.6, 75.0), (315.0, 78.0),
           (315.5, 81.2), (315.9, 84.0), (316.4, 88.4), (316.8, 93.8), (316.2, 97.0), (315.9, 99.2), (315.9, 101.0)]
TRIGGER_WINDOWS = [[(324.0, 99.0), (321.0, 99.0), (321.6, 96.0), (321.8, 93.3), (322.3, 93.3), (322.8, 96.0)],
                   [(322.2, 90.3), (321.3, 90.3), (320.8, 85.0), (320.2, 80.0), (319.5, 77.6), (320.2, 76.5),
                    (321.0, 77.0), (322.2, 78.5)]]
MAG_RELEASE = [(452.0, 103.0), (453.0, 86.0), (462.0, 82.0), (463.0, 95.0), (458.0, 104.0)]
SELECTOR = (367.0, 124.0)

# The rear side panels (black): Desert Tech's forward-eject chute, or the side-eject port frame / plain cover
PANEL = [(473.0, 140.0), (473.0, 160.0), (478.0, 162.5), (618.0, 162.5), (624.0, 157.0), (624.0, 145.0),
         (618.0, 140.0)]
PANEL_BLOCK = [(473.0, 123.0), (473.0, 140.0), (504.0, 140.0), (504.0, 123.0)]
PANEL_HALF = 0.9
PANEL_X = W_UPPER + PANEL_HALF - 0.1          # the panel's centre plane (its inner face 0.1 into the upper)
# where the carrier shows on the right side: the side-eject port (the .223) or the chute's viewing window (the .308)
WINDOW = {"side": (480.0, 560.0, 144.0, 157.0), "forward": (520.0, 600.0, 147.0, 156.0)}

# the charging handle (both sides, at the front of its slot) and its pull
HANDLE = (278.0, 292.0, 168.0, 180.0)
HANDLE_SLOT = (275.0, 410.0, 167.5, 171.0)
CH_TRAVEL = 110.0

MAG_L, MAG_H = 490.0, 128.0        # the magazine's feed lips (module docstring)
OPTIC_L = 390.0                    # over the grip on the upper's rail
# No GoM bipod point: the MDRx takes its own handguard bipod (user, 2026-11-04), the .308's ALX below
FOREGRIP_L = 150.0

# --------------------------------------------------------------------------------------------------
# BLK LBL's ALX bipod handguard on the .308 (user, 2026-11-04): Desert Tech's FDE photos of the 16" one
# (references/mdr/alx, the store's "WLVRN/MDRX ALX Bipod 16" Handguard"): 9" (228.6 mm) long, 1 7/8" across, legs
# 6 1/4" to 9 1/8" tall, aluminium with carbon fibre inner legs. Read on a millimetre grid over 6f9266eb.png (left
# side, muzzle right, 7.826 px/mm): L = 67 + (1856 - x) / 7.826, H = 197 - (y - 210) / 7.826 (its nose on the stock
# handguard's, its rail top on RAIL_TOP). The 16" lines up with the stock handguard: its rail starts at L 229.5,
# where a shelf (H 186.4) runs under the MDRx's black front block, its rear tucks under the upper and into the
# chassis down to L 294.5. The 20" (the .308's) is the same piece 101.6 mm longer ahead of ALX_SPLIT, with two more
# M-LOK columns and a second lower slot; its legs are the 16"'s (Desert Tech lists one leg height, 6 1/4" to 9 1/8",
# for every length), so the leg window ends with them, 101.6 mm earlier, and the underside behind it is closed. The
# nose is then 4 mm behind the Ratchet compensator.
# --------------------------------------------------------------------------------------------------
W_ALX = 23.8                       # half of 1 7/8"
ALX_LIP = 1.25                     # half thickness of the side walls' lower lips under the leg window
ALX_SPLIT = 125.0                  # the 20" is the 16" stretched here


def fwd(L):
    return L - TWENTY if L < ALX_SPLIT else L


# the frame's side outline (16" L, H): rail floor, shelf, rear tab, the leg window's notch (open across the whole
# width: the legs fold up into it from below), the nose sloping back to the rail
ALX_16 = [(229.6, RAIL_FLOOR), (229.6, 186.4), (246.5, 186.4), (266.0, 163.0), (289.0, 161.0), (292.5, 159.5),
          (294.5, 156.0), (294.5, 146.5), (293.0, 142.0), (271.0, 118.5), (268.0, 118.5), (256.0, 125.0),
          (244.0, 125.0), (247.5, 149.7), (113.0, 149.7), (101.0, 160.0), (92.0, 160.0), (86.0, 150.0),
          (81.5, 140.0), (79.5, 125.0), (70.5, 125.0), (70.0, 126.5), (70.0, 143.0), (71.5, 150.0), (74.5, 160.0),
          (77.0, 170.0), (81.0, 180.0), (94.0, 190.0), (96.5, RAIL_FLOOR)]
WINDOW_REAR = ((244.0, 125.0), (247.5, 149.7))   # the leg window's slanted rear edge (16"): moves with the legs
ALX = [(L - TWENTY if (L, H) in WINDOW_REAR else fwd(L), H) for L, H in ALX_16]
ALX_LIPS = [(fwd(79.5), 125.0), (244.0 - TWENTY, 125.0), (244.0 - TWENTY, 128.8),
            (fwd(79.5), 128.8)]                   # under the window, sides only
ALX_RAIL = (fwd(98.5), 229.5)
# M-LOK: two rows of long slots (Desert Tech: M-LOK at 2, 3, 9 and 10 o'clock), the front column's ends slanted on
# the photo; the 20" adds two columns between the 16"'s middle and front ones (14 mm webs, as the photo's)
ALX_ROW_A = [(172.5, 196.5), (133.0, 158.5), (82.4, 118.4), (32.4, 68.4), (fwd(92.0), fwd(120.0))]
ALX_ROW_A_H = (177.3, 183.0)
ALX_ROW_B = [(a - 2.75, c - 2.75) for a, c in ALX_ROW_A]
ALX_ROW_B_H = (169.5, 175.3)
ALX_LOW = [(124.0, 155.0), (23.4, 54.4)]          # the lower slot (one on the 16")
ALX_LOW_H = (153.8, 159.8)
ALX_VSLOT = (216.5, 229.0, 165.0, 185.5)         # the upright slot behind the rows
ALX_QD = (179.5, 156.6, 4.3)                      # the round QD socket hole
ALX_SCREWS = [(191.5, 156.6, 3.3), (222.0, 156.5, 3.3), (291.0, 153.2, 3.5)]
# the legs (the user's photos, 2026-11-04: Firearmland's FDE ALX deployed, a black MDRx standing on one): each an
# extruded aluminium housing with diagonal grip grooves and a release latch near its end, a carbon fibre inner leg
# that slides out of it, a round rubber foot with a chamfered tip; a Torx pivot screw on the knuckle and a ribbed
# black release paddle in the nose's cut-out above the hinge. Pivot at the nose, folded back flush into the window
# (H 128.8-149.7) side by side, the inner leg pushed home (the 16" photo: housing to L 214, the foot to L 243.5).
LEG_PIVOT = (fwd(88.5), 139.0)
LEG_X = 10.1                       # each leg's centre off the bore line (the two fill the 41 mm channel)
LEG_W, LEG_H = 9.5, 10.2           # the housing's half width, half height
LEG_HOUSING = 125.5                # pivot to the housing's end
LEG_LEN = 155.0                    # pivot to the foot's tip, folded (6 1/4" with the knuckle: Desert Tech's lowest)
LEG_EXT = 55.0                     # the inner leg drawn out when deployed (of 73: 9 1/8" - 6 1/4")
TUBE_R, FOOT_R = 6.0, 8.5
# deployed: swung down past vertical by 3 degrees (feet a little forward); seen from the front the legs make a 45
# degree V (user, 2026-11-04: "nearly 45 degrees"; the first build splayed them 8 degrees each, the HBAR's). The
# knuckle and neck stay upright inside the nose and the bar splays from a knee just under the frame (LEG_KNEE from
# the pivot): splayed from the pivot, the bar's top would cut through the side walls' lips.
LEG_DOWN, LEG_SPLAY, LEG_KNEE = 93.0, 22.5, 19.5      # the splayed bar's inner top corner rises 3.6 mm

# GoM's optional Picatinny_Rail_Left / _Right (user, 2026-11-04): our short M-LOK rail sections, five crossbars
# (48.8 mm: crossbars 2 mm from both ends, so two M-LOK screws sit in the outer gaps), drawn at rail_left /
# rail_right with their origin on the handguard's side face. The .223's on the stock handguard's lower M-LOK row
# (where its lights and lasers were), the .308's on the ALX's 3 / 9 o'clock row (B), over its third column.
SIDE_RAIL_LEN, SIDE_BASE, SIDE_TEETH = 48.8, 1.5, 3.0
SIDE_RAIL = {"MDR223": (133.5, 157.5, W_HG),
             "MDR308": ((ALX_ROW_B[2][0] + ALX_ROW_B[2][1]) / 2.0, sum(ALX_ROW_B_H) / 2.0, W_ALX)}


class Gun:
    def __init__(self, name, barrel, eject, bore_r, colours, alx=False):
        self.name, self.barrel, self.eject, self.bore_r, self.colours = name, barrel, eject, bore_r, colours
        self.alx = alx                                 # BLK LBL's ALX bipod handguard (the .308) or the stock one
        self.muzzle = -(barrel - 16.0) * 25.4          # L of the muzzle tip
        self.window = WINDOW[eject]
        La, Lb = self.window[:2]
        self.split = (La + Lb) / 2.0                   # the window's front half shows the chamber, its rear the carrier
        self.travel = self.split - La - 0.5


BLACK = {"polymer": (46, 46, 49), "upper": (54, 54, 58)}
FDE = {"polymer": (170, 142, 100), "upper": (150, 124, 98)}
G223 = Gun("MDR223", 16.0, "side", 9.5, BLACK)
G308 = Gun("MDR308", 20.0, "forward", 10.5, FDE, alx=True)
GUNS = (G223, G308)


def P(L, H):
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


def stadium(La, Lb, Ha, Hb, n=6):
    r = (Hb - Ha) / 2.0
    c = (Ha + Hb) / 2.0
    pts = [(Lb - r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, n)]
    pts += [(La + r + r * math.cos(a), c + r * math.sin(a)) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, n)]
    return pts


def rect(La, Lb, Ha, Hb):
    return [(La, Ha), (Lb, Ha), (Lb, Hb), (La, Hb)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body(g):
    b = kit.Builder()
    slab(b, CHASSIS, half=W_CHASSIS, bevel=3.0, res=1, mat="polymer")
    slab(b, UPPER, half=W_UPPER, bevel=1.5, res=0, mat="upper")
    slab(b, RISER, half=W_RISER, bevel=2.0, res=1, mat="polymer")
    slab(b, PAD, half=W_PAD, bevel=2.0, res=1, mat="rubber")
    if g.alx:
        build_alx(b)
        hg_rail = (ALX_RAIL[0], ALX_RAIL[1], "alx")
    else:
        slots = [stadium(a, c, *MLOK_TOP_H) for a, c in MLOK_TOP]
        slab(b, HANDGUARD, slots, half=W_HG, bevel=2.0, res=1, mat="polymer")
        hg_rail = (HG_RAIL[0], HG_RAIL[1], "polymer")
    slab(b, GRIP, half=W_GRIP, bevel=4.0, res=1, mat="polymer")
    slab(b, GUARD, [GUARD_HOLE], half=W_GUARD, bevel=1.5, res=0, mat="polymer")
    slab(b, TRIGGER, TRIGGER_WINDOWS, half=2.8, bevel=0.3, mat="dark")
    slab(b, MAG_RELEASE, half=21.0, bevel=0.8, mat="dark")
    slab(b, FRONT_BLOCK, half=12.0, bevel=0.6, mat="dark")
    for La, Lb, mat in ((UPPER_RAIL[0], UPPER_RAIL[1], "upper"), hg_rail):
        ya, yb = sorted((L0 - Lb, L0 - La))
        kit.picatinny(b, ya, yb, lambda u, h, y: Vector((u, y, RAIL_FLOOR - H0 + h)), base_h=0.5,
                      tooth_h=RAIL_TOP - RAIL_FLOOR + 0.5, mat=mat)
    # the rear side panels: the left one plain (side eject) or the chute (forward eject); the right one with the
    # carrier's window cut through it
    win = rect(*g.window)
    slab(b, PANEL, half=PANEL_HALF, bevel=0.5, mat="dark", x0=PANEL_X)
    slab(b, PANEL, [win], half=PANEL_HALF, bevel=0.5, mat="dark", x0=-PANEL_X)
    both(lambda s: slab(b, PANEL_BLOCK, half=PANEL_HALF, bevel=0.5, mat="dark", x0=s * PANEL_X))
    # the selector on both sides
    cl, ch = SELECTOR
    both(lambda s: b.lathe("x", (0, *P(cl, ch)), [(s * (W_CHASSIS - 0.5), 0), (s * (W_CHASSIS - 0.5), 7.0),
                                                  (s * (W_CHASSIS + 1.8), 7.0), (s * (W_CHASSIS + 2.4), 5.5),
                                                  (s * (W_CHASSIS + 2.4), 0)], seg=12, mat="dark"))
    both(lambda s: box(b, cl - 12.0, cl + 1.0, ch - 2.0, ch + 2.0, s * (W_CHASSIS + 1.6), s * (W_CHASSIS + 4.0),
                       mat="dark", bevel=0.6))
    # barrel (inside the handguard from the chamber, out of its nose on the 20") and Desert Tech's Ratchet compensator
    m = g.muzzle
    y = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(y(300.0), 0), (y(300.0), g.bore_r), (y(m + 66.0), g.bore_r),
                                       (y(m + 66.0), 0)], seg=14, mat="metal", phase=0.5)
    b.lathe("y", (0, 0, BORE_H - H0), [(y(m + 66.0), 0), (y(m + 66.0), 10.5), (y(m + 58.0), 10.5), (y(m + 58.0), 11.2),
                                       (y(m + 48.0), 11.2), (y(m + 47.0), 10.6), (y(m + 20.0), 10.6),
                                       (y(m + 18.0), 9.6), (y(m + 1.0), 9.6), (y(m), 8.6), (y(m), 4.5),
                                       (y(m + 10.0), 4.5), (y(m + 10.0), 0)], seg=16, mat="dark", phase=0.5)
    return b.to_object(g.name + "_BODY")


def circle(cL, cH, r, n=16):
    return [(cL + r * math.cos(2 * math.pi * k / n), cH + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def build_alx(b):
    """BLK LBL's ALX frame (part of the body): the solid side outline with its M-LOK slots, upright slot and QD hole
    cut through (daylight shows through them, the barrel through the low ones, as on the stock handguard), the leg
    window's notch open across the whole width, the side walls' thin lower lips under it, and at the channel's
    front the bracket and pin the legs hinge on (the pin stays when they swing down)."""
    holes = [stadium(a, c, *ALX_ROW_A_H) for a, c in ALX_ROW_A]
    holes += [stadium(a, c, *ALX_ROW_B_H) for a, c in ALX_ROW_B]
    holes += [stadium(a, c, *ALX_LOW_H) for a, c in ALX_LOW]
    La, Lb, Ha, Hb = ALX_VSLOT
    holes.append([(L, H) for H, L in stadium(Ha, Hb, La, Lb)][::-1])     # upright: swapped, wound as the rest
    holes.append(circle(*ALX_QD))
    # bevel 0.6: each hole's curve is offset by the bevel into the metal, and the two rows are 2 mm apart (1.2
    # made their loops cross and the fill flipped inside out)
    slab(b, ALX, holes, half=W_ALX, bevel=0.6, res=0, mat="alx")
    both(lambda s: slab(b, ALX_LIPS, half=ALX_LIP, bevel=0.4, mat="alx", x0=s * (W_ALX - ALX_LIP)))
    pl, ph = LEG_PIVOT
    box(b, pl - 4.0, pl + 5.0, ph + 8.8, 150.5, -(W_ALX - 2.0), W_ALX - 2.0, mat="dark", bevel=0.6)
    # the ribbed release paddle on both sides in the nose's cut-out, hung from its top edge
    both(lambda s: box(b, fwd(91.0), fwd(100.0), 150.5, 160.3, s * (W_ALX - 3.0), s * (W_ALX - 0.2), mat="dark",
                       bevel=0.6))
    for hr in (152.0, 154.2, 156.4, 158.6):                     # its ribs, standing 0.6 mm proud
        both(lambda s: box(b, fwd(91.6), fwd(99.4), hr - 0.45, hr + 0.45, s * (W_ALX - 0.4), s * (W_ALX + 0.4),
                           mat="dark", bevel=0.2))
    b.lathe("x", (0, *P(pl, ph)), [(-(W_ALX - 2.0), 0), (-(W_ALX - 2.0), 3.0), (W_ALX - 2.0, 3.0),
                                   (W_ALX - 2.0, 0)], seg=10, mat="dark")


def leg_xf(s, deployed, knee=False):
    """Leg s (+1 the gun's left, -1 its right) from its local frame (pivot at the origin, the leg along -Y, its top
    +Z) into the gun's builder space (mm). Deployed, the knuckle and neck only swing down; `knee` = the bar below
    LEG_KNEE, also turned outward about the knee (local Z, along the gun once swung down) by LEG_SPLAY."""
    pl, ph = LEG_PIVOT
    t = Matrix.Translation(Vector((s * LEG_X, L0 - pl, ph - H0)))
    if not deployed:
        return t
    m = t @ Matrix.Rotation(math.radians(LEG_DOWN), 4, 'X')
    if knee:
        k = Matrix.Translation(Vector((0.0, -LEG_KNEE, 0.0)))
        m = m @ k @ Matrix.Rotation(math.radians(s * LEG_SPLAY), 4, 'Z') @ k.inverted()
    return m


def build_bipod(g, deployed):
    """The ALX's two legs (gun space, drawn at `integrated_bipod`, the HBAR's way): extruded aluminium bars with a
    knuckle round the pivot, the rubber foot at the end; folded they lie flush in the window, deployed they swing
    down at the nose."""
    b = kit.Builder()
    n = LEG_LEN
    for s in (1, -1):
        xf, bar = leg_xf(s, deployed), leg_xf(s, deployed, knee=True)
        # the housing starts at the knee, 19.5 mm from the pivot: deployed and splayed, its corners stay 1.9 mm
        # under the frame's bottom edge (H 125), and only the narrower neck and the knuckle turn inside the nose,
        # seated against its inner wall as the photo's hinge block is
        b.box(-LEG_W, LEG_W, -LEG_HOUSING, -LEG_KNEE, -LEG_H, LEG_H, mat="leg", bevel=3.0, xf=bar)
        b.box(-(LEG_W - 1.0), LEG_W - 1.0, -(LEG_KNEE + 1.5), 0.0, -8.0, 8.0, mat="leg", bevel=1.5, xf=xf)
        b.lathe("x", (0, 0, 0), [(-(LEG_W - 1.0), 0), (-(LEG_W - 1.0), 8.5), (LEG_W - 1.0, 8.5),
                                 (LEG_W - 1.0, 0)], seg=16, mat="leg", xf=xf)
        # the Torx pivot screw's head on the knuckle's outer side
        b.lathe("x", (0, 0, 0), [(s * (LEG_W - 1.2), 0), (s * (LEG_W - 1.2), 4.4), (s * (LEG_W - 0.3), 4.0),
                                 (s * (LEG_W - 0.3), 0)], seg=14, mat="metal", xf=xf)
        # the carbon inner leg (drawn out when deployed) and the rubber foot
        e = LEG_EXT if deployed else 0.0
        t0, t1 = LEG_HOUSING + e, LEG_LEN + e
        if deployed:
            b.lathe("y", (0, 0, 0), [(-(LEG_HOUSING - 8.0), 0), (-(LEG_HOUSING - 8.0), TUBE_R), (-(t0 + 1.0), TUBE_R),
                                     (-(t0 + 1.0), 0)], seg=12, mat="carbon", xf=bar)
        b.lathe("y", (0, 0, 0), [(-t0, 0), (-t0, FOOT_R - 1.0), (-(t0 + 1.5), FOOT_R), (-(t1 - 5.0), FOOT_R),
                                 (-(t1 - 1.0), FOOT_R - 2.0), (-t1, FOOT_R - 3.5), (-t1, 0)], seg=16, mat="rubber",
                xf=bar)
    if deployed:
        foot = leg_xf(1, True, knee=True) @ Vector((0.0, -(n + LEG_EXT), 0.0))
        assert foot.x > LEG_X + 50.0 and foot.y > L0 - LEG_PIVOT[0], foot     # splayed out, a little forward
    return b.to_object("%s_BIPOD_%s" % (g.name, "DEPLOYED" if deployed else "FOLDED"))


def build_side_rail(g, s):
    """Our short M-LOK Picatinny section for GoM's Picatinny_Rail_Left (s = +1) / _Right (-1): origin on the
    handguard's side face at the rail's centre, crossbars standing out along s * X, two M-LOK screws in the outer
    gaps between crossbars."""
    b = kit.Builder()
    half = SIDE_RAIL_LEN / 2.0
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((s * h, yy, u)), base_h=SIDE_BASE, tooth_h=SIDE_TEETH,
                  mat="dark")
    for yy in (-15.0, 15.0):
        b.lathe("x", (0, yy, 0), [(0.0, 0), (0.0, 2.2), (s * 2.8, 2.2), (s * 3.2, 1.6), (s * 3.2, 0)], seg=8,
                mat="metal")
    return b.to_object("%s_RAIL_%s" % (g.name, "LEFT" if s > 0 else "RIGHT"))


def build_bolt(g):
    """The bolt carrier's side over the front half of the right side's window, flush with the upper (GoM's Bolt
    swap slides it back over the rear half: the chamber shows in front of it, nothing stands outside the window)."""
    b = kit.Builder()
    La, Lb, Ha, Hb = g.window
    box(b, La + 0.3, g.split, Ha + 0.3, Hb - 0.3, -(W_UPPER + 0.45), -(W_UPPER - 0.6), mat="metal", bevel=0.2)
    return b.to_object(g.name + "_BOLT")


def build_handle(g):
    """Desert Tech's ambidextrous charging handle: a knob on each side at the front of the upper's slot. It does not
    reciprocate: the main mod's ChargingHandle part moves it back only while racked."""
    b = kit.Builder()
    La, Lb, Ha, Hb = HANDLE
    both(lambda s: box(b, La, Lb, Ha, Hb, s * (W_UPPER - 1.0), s * (W_UPPER + 3.2), mat="dark", bevel=1.0))
    both(lambda s: box(b, La - 3.0, La + 3.0, Ha + 2.0, Hb + 1.5, s * (W_UPPER + 1.5), s * (W_UPPER + 4.0),
                       mat="dark", bevel=0.8))
    return b.to_object(g.name + "_HANDLE")


# ==================================================================================================
# Magpul PMAG LR/SR (SR-25 pattern) and the D-50 drum: origin at the feed lips, +Y forward, hanging down
# ==================================================================================================

PMAG_FRONT, PMAG_REAR, PMAG_W = 37.0, -37.0, 13.6
PMAG_LEN = {10: 106.0, 20: 158.0, 25: 184.0}      # lips to the base plate's bottom


def mag_round(b):
    """The top round, 7.62x51 (the SCAR-H magazines'), the bullet forward."""
    r0 = PMAG_FRONT - 6.0
    b.lathe("y", (0, 0, 3.0), [(r0 - 71.0, 0), (r0 - 71.0, 6.0), (r0 - 30.0, 6.0), (r0 - 26.0, 4.2),
                               (r0 - 20.0, 4.0)], seg=10, mat="brass")
    b.lathe("y", (0, 0, 3.0), [(r0 - 20.0, 4.0), (r0 - 10.0, 3.6), (r0 - 3.0, 1.6), (r0, 0)], seg=10, mat="copper")


def mag_top(b, foot):
    """The body from the lips down to `foot` (z), the lips' shoulders and the top round."""
    f, r = PMAG_FRONT, PMAG_REAR
    body = [(f, foot), (f, -6.0), (f - 4.0, -1.0), (r + 4.0, -1.0), (r, -6.0), (r, foot)]
    kit.slab(b, body, [], PMAG_W, 1.6, 1, "magpoly", 0.0)
    lips = [(f - 10.0, -1.5), (r + 6.0, -1.5), (r + 8.0, 2.0), (f - 18.0, 2.0)]
    both(lambda s: kit.slab(b, lips, [], 1.2, 0.3, 0, "magpoly", s * (PMAG_W - 2.0)))
    mag_round(b)


def build_pmag(rounds):
    b = kit.Builder()
    n = PMAG_LEN[rounds]
    mag_top(b, -(n - 8.0))
    f, r = PMAG_FRONT, PMAG_REAR
    # the flared base plate with its grip ridge at the back
    plate = [(f + 2.5, -(n - 9.0)), (f + 3.5, -(n - 3.0)), (f + 1.0, -n), (r - 1.0, -n), (r - 4.0, -(n - 3.0)),
             (r - 3.0, -(n - 9.0))]
    kit.slab(b, plate, [], PMAG_W + 1.4, 1.6, 1, "magpoly", 0.0)
    return b.to_object("762x51Magazine%d_PMAG" % rounds)


DRUM_R, DRUM_HALF = 70.0, 39.0
DRUM_Z = -(58.0 + DRUM_R - 22.0)     # the drum's centre under the lips: the tower runs 22 mm into it


def build_drum():
    """Magpul's PMAG D-50 LR/SR: a feed tower into one round drum whose faces look to the front and back (its axis
    along the barrel, as the MP7's and the SCAR-H's drums; user, 2026-11-04: the first build faced the sides, as
    Magpul's D-60 does), the loading lever on its front face, a base pad under it."""
    b = kit.Builder()
    mag_top(b, DRUM_Z + DRUM_R - 10.0)
    h, r = DRUM_HALF, DRUM_R
    b.lathe("y", (0.0, 0.0, DRUM_Z), [(-h, 0), (-h, r - 8.0), (-h + 1.4, r - 3.0), (-h + 4.0, r), (h - 4.0, r),
                                      (h - 1.4, r - 3.0), (h, r - 8.0), (h, 0)], seg=32, mat="magpoly")
    for s in (-1, 1):                                      # the raised hubs on both faces
        b.lathe("y", (0.0, 0.0, DRUM_Z), [(s * h, 0), (s * h, 24.0), (s * (h + 2.0), 22.0), (s * (h + 2.0), 0)],
                seg=20, mat="magpoly")
    b.lathe("y", (0.0, 0.0, DRUM_Z), [(h + 2.0, 0), (h + 2.0, 9.0), (h + 7.0, 9.0), (h + 7.0, 0)], seg=14,
            mat="magpoly")                                 # the loading lever's boss on the front face
    b.box(-14.0, 14.0, h + 7.0, h + 11.0, DRUM_Z - 3.5, DRUM_Z + 3.5, mat="magpoly", bevel=1.0)
    b.box(-22.0, 22.0, -h + 6.0, h - 6.0, DRUM_Z - r - 3.0, DRUM_Z - r + 6.0, mat="magpoly", bevel=1.5)
    return b.to_object("762x51Magazine50_PMAG")


# ==================================================================================================
# Painting
# ==================================================================================================

SHARED = {"dark": (24, 24, 25), "metal": (52, 52, 54), "rubber": (34, 34, 35), "brass": (150, 118, 62),
          "copper": (140, 82, 52), "magpoly": (42, 42, 44),
          "alx": (146, 124, 90), "leg": (50, 50, 54),         # the ALX's FDE anodising (the photos), its satin black legs
          "carbon": (36, 36, 39)}

kit.FONT.setdefault("5", ["111", "100", "111", "001", "111"])


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] *= 0.6


def common(maps, col, mat, light):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    dark = np.isin(mat, [MATS.index(m) for m in ("dark", "metal", "rubber", "magpoly", "leg", "carbon")]) | ~light
    wear = np.where(dark, 46.0, 30.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 0.97, 0.92])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint_gun(maps, g, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    poly = (mat == MATS.index("polymer")) & side
    upper = (mat == MATS.index("upper")) & side & (np.abs(x) > W_UPPER - 0.6)
    dark = (mat == MATS.index("dark")) & side
    hg = poly & (np.abs(x) > W_HG - 0.6) & (L < 295.0)
    butt = poly & (np.abs(x) > W_CHASSIS - 0.6) & (L > 455.0) & (H < 135.0)
    housing = poly & (np.abs(x) > W_CHASSIS - 0.6) & (L > 260.0) & (L < 455.0) & (H > 98.0)
    riser = poly & (np.abs(x) > W_RISER - 0.6) & (H > 164.0)
    grip = poly & (np.abs(x) > W_GRIP - 0.8) & (H < 100.0) & (L > 338.0)
    # the charging handle's slot and its front stop, the upper's seams
    La, Lb, Ha, Hb = HANDLE_SLOT
    col[upper & rounded_rect(L, H, La, Lb, Ha, Hb, 1.6)] = 10
    col[upper & rounded_rect(L, H, 254.0, 268.0, 177.0, 181.0, 1.6)] = 12
    col[upper & (np.abs(H - 186.0) < 0.5) & (L > 250) & (L < 470)] *= 0.6
    col[upper & (np.abs(H - 142.0) < 0.5) & (L > 300) & (L < 470)] *= 0.7
    # the window on the right: its front half the open chamber, its rear the carrier's grooved side (drawn on the
    # upper's side face behind the panel's cut)
    Wa, Wb, Wc, Wd = g.window
    win = (mat == MATS.index("upper")) & right & (L >= Wa) & (L <= Wb) & (H >= Wc) & (H <= Wd)
    col[win & (L < g.split)] = 6
    rear = win & (L >= g.split)
    col[rear] = 40
    col[rear & (np.mod(L, 4.0) < 1.0)] = 26
    # screws through the upper and chassis, the rear sling socket, the selector's marks
    for cL, cH in ((465.0, 162.0), (423.0, 162.0), (465.0, 141.0), (423.0, 141.0), (640.0, 172.0), (664.0, 161.0),
                   (664.0, 146.0), (300.0, 150.0)):
        pin(col, L, H, upper, cL, cH, 2.6)
    for cL, cH in ((448.0, 122.0), (410.0, 115.0), (560.0, 115.0), (450.0, 104.0), (282.0, 118.0)):
        pin(col, L, H, poly & (np.abs(x) > W_CHASSIS - 0.6), cL, cH, 2.4)
    d = np.hypot(L - 668.0, H - 126.0)
    col[poly & (d < 7.0)] *= 0.35
    col[poly & (d < 4.5)] = 8
    sl, sh = SELECTOR
    col[housing & (np.hypot(L - (sl + 3.0), H - (sh + 10.0)) < 1.6)] = (190, 40, 36)
    col[housing & (np.hypot(L - (sl - 12.0), H - (sh + 2.0)) < 1.4)] = (220, 218, 210)
    # the bolt catch's vented paddle and the trigger housing's seam
    vent = housing & rounded_rect(L, H, 286.0, 297.0, 110.0, 122.0, 1.5)
    col[vent] *= 0.3
    col[vent & (np.mod(H, 2.6) < 1.0)] = 30
    col[housing & (np.abs(H - 133.5) < 0.5)] *= 0.6
    # the butt: stippled panels and the cheek riser's seam
    panel = butt & (L > 560.0) & (L < 650.0) & (H > 62.0) & (H < 128.0) & (H < 128.0 - 0.6 * (L - 560.0) + 60.0)
    grains = panel & (kit.vnoise(p, 0.6, 21) > 0.55)
    col[grains] += 14
    col[panel & ~grains] *= 0.82
    col[riser & (np.abs(H - 165.6) < 0.6)] *= 0.55
    # the handguard: the lower M-LOK row, the QD socket, its diagonal ribs
    for a, c in MLOK_LOW:
        col[hg & rounded_rect(L, H, a, c, MLOK_LOW_H[0], MLOK_LOW_H[1], 3.0)] = 8
    col[hg & rounded_rect(L, H, 213.0, 226.0, 158.0, 172.0, 2.0)] = 14
    rib = hg & (H > 133.0) & (H < 150.0) & (L > 85.0) & (L < 280.0) & (np.mod(L + 0.6 * H, 26.0) < 2.0)
    col[rib] *= 0.75
    # the grip: stippled panel and finger grooves at its back
    gp = grip & (H > 12.0) & (H < 85.0)
    grains = gp & (kit.vnoise(p, 0.6, 22) > 0.55)
    col[grains] += 14
    col[gp & ~grains] *= 0.85
    col[grip & (L > 390.0) & (H > 20.0) & (H < 70.0) & (np.mod(H, 3.5) < 1.2)] *= 0.6
    # the chute / cover panels: the forward-eject chute's long slot and latch, the side-eject cover's recess
    pnl = dark & (np.abs(x) > PANEL_X + PANEL_HALF - 0.4)
    if g.eject == "forward":
        col[pnl & left & rounded_rect(L, H, 508.0, 607.0, 146.0, 157.0, 2.0)] = 6
        col[pnl & rounded_rect(L, H, 478.0, 498.0, 126.0, 158.0, 1.5)] += 10
    else:
        col[pnl & left & rounded_rect(L, H, 482.0, 610.0, 144.0, 158.0, 3.0)] *= 0.7
        col[pnl & right & ~rounded_rect(L, H, Wa - 3.0, Wb + 3.0, Wc - 3.0, Wd + 3.0, 2.0) & (L < Wb + 6.0)] += 8
    pin(col, L, H, pnl, 615.0, 151.0, 2.2)
    # the ALX: its Torx screws, the rear double-screw plate (mostly inside the upper and chassis)
    if g.alx:
        alx = (mat == MATS.index("alx")) & side & (np.abs(x) > W_ALX - 0.6)
        for cL, cH, r in ALX_SCREWS:
            d = np.hypot(L - cL, H - cH)
            col[alx & (d < r)] = 14
            col[alx & (d < 0.45 * r)] = 34
        col[alx & rounded_rect(L, H, 247.0, 269.5, 142.0, 160.0, 4.0)] = 18
        # the release paddle's horizontal ribs (the photos')
        paddle = dark & (L > fwd(91.0) - 0.5) & (L < fwd(100.0) + 0.5) & (H > 150.0) & (H < 160.5)
        col[paddle & (np.mod(H, 1.5) < 0.6)] = 8
        col[paddle & (np.mod(H, 1.5) >= 0.6) & (np.mod(H, 1.5) < 0.9)] = 44
        for cL in (252.7, 261.5):
            d = np.hypot(L - cL, H - 151.0)
            col[alx & (d < 4.4) & (d > 3.4)] = 8
    # the Ratchet compensator: its ports, the slot between its two front prongs, the bore
    metal = mat == MATS.index("dark")
    r = np.hypot(x, z - (BORE_H - H0))
    a = np.arctan2(x, z - (BORE_H - H0))
    m = g.muzzle
    comp = metal & (L > m - 0.5) & (L < m + 48.0) & (r > 8.5)
    for cL in (m + 26.0, m + 37.0):
        col[comp & (np.abs(L - cL) < 3.5) & (np.abs(np.abs(a) - math.pi / 2) < 0.6)] = 6
    col[comp & (L < m + 17.0) & (np.abs(np.abs(a) - math.pi / 2) < 0.35)] = 6
    col[metal & (r < 4.8) & (L < m + 10.5)] = 5
    return col


def paint_mag(maps, col, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    mp = (mat == MATS.index("magpoly"))
    if kind == "drum":
        dz = z - DRUM_Z
        r = np.hypot(x, dz)
        fwd, back = n[..., 1] > 0.7, n[..., 1] < -0.7
        face = mp & (fwd | back) & (np.abs(y) > DRUM_HALF - 0.5) & (r < DRUM_R - 3.0)
        col[face & (np.abs(r - 58.0) < 0.9)] *= 0.5
        col[face & (np.abs(r - 30.0) < 0.7)] *= 0.6
        for k in range(10):
            ang = k * math.pi / 5.0
            dd = np.abs(np.cos(ang) * dz - np.sin(ang) * x)
            col[face & (dd < 1.0) & (r > 31.5) & (r < 56.5)] *= 0.8
        # "50" upright under the hub, reading the right way in game (the SCAR-H drum's rule: seen from behind, the
        # gun's right (-X) is on the viewer's right)
        for f, uu in ((face & back, -x), (face & fwd, x)):
            col[f & kit.text_mask(uu, dz, "50", -11.2, -52.0, 16.0)] = (78, 78, 80)
        tower = mp & side & (z > DRUM_Z + DRUM_R - 2.0)
        col[tower & (np.abs(z + 20.0) < 0.8)] *= 0.7
        return col
    rounds = int(kind[4:])
    n_len = PMAG_LEN[rounds]
    body = mp & side & (np.abs(x) > PMAG_W - 0.6)
    # Magpul's waffle panels down the sides (rows of rounded squares), a texture band under the lips, the dot matrix
    top, bottom = -14.0, -(n_len - 16.0)
    rows = max(1, int((top - bottom) // 30))
    hrow = (top - bottom) / rows
    for k in range(rows):
        za = bottom + k * hrow
        for ya, yb in ((-31.0, -3.0), (3.0, 31.0)):
            q = body & rounded_rect(y, z, ya, yb, za + 2.0, za + hrow - 2.0, 3.0)
            col[q & ~rounded_rect(y, z, ya + 1.2, yb - 1.2, za + 3.2, za + hrow - 3.2, 2.0)] *= 0.6
    band = body & (z > -12.0) & (z < -6.0) & (np.mod(y, 2.4) < 0.9)
    col[band] *= 0.7
    dots = body & (z > -(n_len - 24.0)) & (z < -(n_len - 34.0)) & (y > 10.0) & (y < 28.0)
    col[dots & (np.mod(y, 2.2) < 1.0) & (np.mod(z, 2.2) < 1.0)] += 22
    col[mp & side & (z < -(n_len - 10.0)) & (y < -30.0) & (np.mod(z, 2.0) < 0.8)] *= 0.65   # the plate's ridge
    return col


def paint_legs(maps, col, deployed):
    """The ALX's legs, in each leg's own frame (leg_xf): the diagonal grip grooves along the housing's sides
    (rising towards the pivot, as the photos'), the grey release latch in its recess near the housing's end, the
    Torx star of the pivot screw, the carbon inner leg's twill weave, the foot's grip rings."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    legm = np.isin(mat, [MATS.index(m) for m in ("leg", "rubber", "carbon", "metal")])
    for s in (1, -1):
        inv = np.array(leg_xf(s, deployed).inverted(), np.float32)
        lp = p @ inv[:3, :3].T + inv[:3, 3]
        ln = n @ inv[:3, :3].T
        if deployed:                 # the bar below the knee is splayed: its own frame there
            inv2 = np.array(leg_xf(s, True, knee=True).inverted(), np.float32)
            lp2 = p @ inv2[:3, :3].T + inv2[:3, 3]
            below = (-lp[..., 1] > LEG_KNEE + 0.5)[..., None]
            lp = np.where(below, lp2, lp)
            ln = np.where(below, n @ inv2[:3, :3].T, ln)
        mine = legm & (np.sign(p[..., 0]) == s)
        ly, lz = lp[..., 1], lp[..., 2]
        d = -ly
        sidef = mine & (np.abs(ln[..., 0]) > 0.7)
        housing = mine & (mat == MATS.index("leg"))
        grooves = sidef & housing & (d > 40.0) & (d < LEG_HOUSING - 28.0) & (lz > -6.0) & (lz < LEG_H - 2.0)
        ph = np.mod(d + lz, 7.0)
        col[grooves & (ph < 2.0)] = 12
        col[grooves & (ph >= 2.0) & (ph < 3.0)] += 34              # the lit lip of each groove
        latch = sidef & housing & (d > LEG_HOUSING - 19.0) & (d < LEG_HOUSING - 3.0) & (lz > LEG_H - 4.5)
        col[latch] = 10                                                 # the recess
        col[latch & (d > LEG_HOUSING - 17.0) & (d < LEG_HOUSING - 5.0) & (lz > LEG_H - 3.5)] = (112, 112, 116)
        # the Torx star on the screw head (6 lobes) and the knuckle round it
        screw = mine & (mat == MATS.index("metal")) & (np.abs(ln[..., 0]) > 0.7)
        r = np.hypot(ly, lz)
        star = r < 1.4 + 0.5 * np.cos(6.0 * np.arctan2(lz, ly))
        col[screw] = 26
        col[screw & star] = 6
        col[screw & (r > 3.6)] = 40
        # the inner leg's 2/2 twill (1.5 mm tows), the foot's rings
        carbon = mine & (mat == MATS.index("carbon"))
        arc = np.arctan2(lp[..., 0], lz) * TUBE_R
        tw = np.mod(np.floor(d / 1.5) + np.floor(arc / 1.5), 4) < 2
        col[carbon & tw] += 12
        col[carbon & ~tw] -= 6
        rubber = mine & (mat == MATS.index("rubber"))
        col[rubber & (np.mod(d, 3.0) < 0.8) & (np.hypot(lp[..., 0], lz) > FOOT_R - 0.4)] *= 0.6
    return col


def paint(maps, kind, g=None):
    mat = maps["mat"]
    col = np.zeros(maps["pos"].shape, np.float32)
    base = dict(SHARED)
    if g is not None:
        base.update(g.colours)
    for i, name in enumerate(MATS):
        col[mat == i] = base.get(name, SHARED["dark"])
    light = np.zeros(mat.shape, bool)
    if g is not None and g.colours is FDE:
        light = np.isin(mat, [MATS.index("polymer"), MATS.index("upper"), MATS.index("alx")])
    if kind == "gun":
        col = paint_gun(maps, g, col)
    elif kind in ("pmag10", "pmag20", "pmag25", "drum"):
        col = paint_mag(maps, col, kind)
    elif kind in ("bipod_folded", "bipod_deployed"):
        col = paint_legs(maps, col, kind == "bipod_deployed")
    col = common(maps, col, mat, light)
    return np.clip(col, 0, 255)


def texture(objects, contexts, kinds, size, path, g=None):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = kit.bake_maps(ob, ctx, bake)
        if kit.DEBUG:
            kit.dump_maps(maps, os.path.join(kit.DEBUG, ob.name))
        c = paint(maps, kind, g)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Attachment points
# ==================================================================================================

def gp(L, H, x=0.0):
    yy, zz = P(L, H)
    return [round(x * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]
# How far GoM's foregrips sit from the stock handguard's underside (fit_audit.py, as the PS90's); its lights 0.0007
# out from our side rails' crossbar faces, its lasers 0.0018 out and 0.0008 lower (the Vectors' / AUG A1's
# relations to a rail of this height)
FOREGRIP_UP = -0.0008
LIGHT_OUT, LASER_OUT, LASER_DOWN = 0.0007, 0.0018, 0.0008


def points(g, bounds):
    rail_top = (RAIL_TOP - H0) * K
    oy = gp(OPTIC_L, 0)[1]
    side_l, side_h, wall = SIDE_RAIL[g.name]
    sy, sz = gp(side_l, side_h)[1:]
    face = wall * K                                            # the handguard's side, our rails' origins
    bars = (wall + SIDE_BASE + SIDE_TEETH - 1.0) * K           # their crossbar faces (kit.picatinny)
    bottom = (HG_BOTTOM - H0) * K
    canon = g.muzzle + (28.8 if g is G223 else 48.0)
    pts = {
        "muzzle": {"offset": gp(g.muzzle, BORE_H), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": gp(canon, BORE_H), "rotate": ZERO},
        "magazine": {"offset": gp(MAG_L, MAG_H), "rotate": ZERO},
        # the SCARs' / MP7's relations to the rail's top (GoM's Picatinny_Rail_Up and its scopes)
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        "rail_left": {"offset": [round(face, 4), sy, sz], "rotate": ZERO},
        "light_left": {"offset": [round(bars + LIGHT_OUT, 4), sy, sz], "rotate": ZERO},
        "rail_right": {"offset": [round(-face, 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(bars + LASER_OUT), 4), sy, round(sz - LASER_DOWN, 4)], "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-g.travel * K, 4), 0.0], "rotate": ZERO},
        "handle_back": {"offset": [0.0, round(-CH_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},                               # every GoM rifle's, scaled
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the rear-top of the "
                 "pistol grip (photo L %.0f, H %.0f)" % (L0, H0),
        "magazine": ("GoM's STANAG magazines (the main mod's _GoT models) hang from here, their feed lips"
                     if g is G223 else "762x51Magazine10/20/25/50_PMAG, origin at their feed lips"),
        "canon": ("as GoM's M4A1, 28.8 mm (0.0187) behind the muzzle: GoM's AR mount device and its muzzle parts"
                  if g is G223 else "the compensator's rear: SCARH_Muzzle_Mount_Device and SCARH_Suppressor"),
        "accessories": "optics on the upper's rail at L %.0f; GoM's optional Picatinny_Rail_Left / _Right drawn as "
                       "%s_RAIL_LEFT / _RIGHT (our M-LOK sections, origin on the side face at L %.1f, H %.1f), "
                       "lights / lasers on them; %s" % (
                           OPTIC_L, g.name, side_l, side_h,
                           "no foregrips: the ALX's legs fold into its underside" if g.alx else
                           "foregrips under the handguard at L %.0f (GoM's bipods do not fit)" % FOREGRIP_L),
        "bolt_fired": "%s_BOLT (the carrier in the right side's %s) back %.1f mm real"
                      % (g.name, "side-eject port" if g.eject == "side" else "chute's viewing window", g.travel),
        "handle_back": "%s_HANDLE (both knobs) back %.0f mm real, only while racked" % (g.name, CH_TRAVEL),
    }
    if g.alx:
        # BLK LBL's ALX legs are modelled in the gun's space (the HBAR's and the M249's way)
        pts["integrated_bipod"] = {"offset": ZERO, "rotate": ZERO}
        pts["_notes"]["integrated_bipod"] = "%s_BIPOD_FOLDED / _DEPLOYED are modelled in the gun's space" % g.name
    else:
        pts["rail_down"] = {"offset": [0.0, gp(FOREGRIP_L, 0)[1], round(bottom + 0.0025, 4)], "rotate": ZERO}
        pts["foregrip"] = {"offset": [0.0, gp(FOREGRIP_L, 0)[1], round(bottom + FOREGRIP_UP, 4)], "rotate": ZERO}
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE_H,
                      "real_mm_per_game_unit": round(1.0 / K, 2), "k": K, "barrel_in": g.barrel, "eject": g.eject,
                      "length_mm": 698.5 - g.muzzle}
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

    guns = {}
    for g in GUNS:
        objs = [build_body(g), build_bolt(g), build_handle(g), build_side_rail(g, 1), build_side_rail(g, -1)]
        if g.alx:
            objs += [build_bipod(g, False), build_bipod(g, True)]
        guns[g.name] = tuple(objs)
    mags = [build_pmag(10), build_pmag(20), build_pmag(25), build_drum()]
    for objs in guns.values():
        kit.unwrap([o for o in objs if "_BIPOD_" not in o.name], 0.005)
        legs = [o for o in objs if "_BIPOD_" in o.name]
        if legs:                       # their own texture (512): the 2 mm grooves need ~0.4 mm texels
            kit.unwrap(legs, 0.008)
    for o in mags:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    for g in GUNS:
        body, bolt, handle, rail_l, rail_r = guns[g.name][:5]
        legs = list(guns[g.name][5:])
        near = legs[:1]                        # the folded legs shade the ALX's channel
        objs = [body, bolt, handle, rail_l, rail_r]
        ctx = [[body, handle] + near, [body, bolt], [body, handle], [rail_l], [rail_r]]
        texture(objs, ctx, ["gun", "bolt", "handle", "rail", "rail"], 256, os.path.join(TEX_DIR, g.name + ".png"), g)
        if legs:
            texture(legs, [[body, o] for o in legs], ["bipod_folded", "bipod_deployed"], 512,
                    os.path.join(TEX_DIR, g.name + "_BIPOD.png"), g)
    for kind, m in zip(("pmag10", "pmag20", "pmag25", "drum"), mags):
        texture([m], [[m]], [kind], 128, os.path.join(TEX_DIR, m.name + ".png"))

    shared = {o.name: kit.bounds_of(o) for o in mags}
    for g in GUNS:
        objs = guns[g.name]
        bounds = {o.name: kit.bounds_of(o) for o in objs}
        bounds.update(shared)
        with open(os.path.join(HERE, g.name.lower() + "_points.json"), "w") as fh:
            json.dump(points(g, bounds), fh, indent=2)
            fh.write("\n")
        kit.export(list(objs), os.path.join(FIRE_DIR, "GunsOfTienPost93_%s.fbx" % g.name))
        for name, bd in bounds.items():
            print("%s %-24s tris %5d  min %s  max %s" % (g.name, name, bd["tris"], bd["min"], bd["max"]))
    kit.export(mags, FBX_MAGS)


if __name__ == "__main__":
    main()
