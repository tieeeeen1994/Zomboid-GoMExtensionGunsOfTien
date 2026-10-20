"""FN SCAR-L (Mk 16 STD) and SCAR-H (Mk 17 LB) models and textures for GoM Extension: Guns of Tien - Post-93
(Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_scar.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_SCARL.fbx        SCARL_BODY, SCARL_BOLT
    P/models_X/weapons/firearms/GunsOfTienPost93_SCARH.fbx        SCARH_BODY, SCARH_BOLT
    P/models_X/weapons/magazines/GunsOfTienPost93_SCARH_magazines.fbx  762x51Magazine20_SCARH, 762x51Magazine10_SCARH,
                                                                  762x51Magazine50_SCARH (ProMag's 50-round drum)
    P/models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx      SCAR_STOCK (both guns), SCARH_Suppressor,
                                                                  SCARH_Muzzle_Mount_Device
    P/textures/weapons/GunsOfTienPost93/<name>.png                SCARL, SCARH (256, body + charging handle),
                                                                  128 for the stock, each magazine and each part
    scripts/post93/scarl_points.json, scarh_points.json           attachment points (game space)

Both rifles are FN's SOCOM SCARs in flat dark earth (user, 2026-10-20): the SCAR-L as the Mk 16 STD (13.8" barrel)
and the SCAR-H as the Mk 17 LB (20" barrel), select fire, with the standard side-folding stock. Traced from the
user's two left-side photos (not kept in the repo: an FN product photo and a retailer's photo of a replica), by
trace_outline.py, scaled by their Picatinny rails (10.0 mm per crossbar, MIL-STD-1913):
  - SCAR-H: a SCAR-H TPRS (20" barrel, 1.814 px/mm, 1031.5 mm as photographed). Its precision stock is not used: the
    standard folding stock of the SCAR-L photo goes on the H too (FN's Mk 16 and Mk 17 share it).
  - SCAR-L: a licensed replica of the CQC (10" barrel, 1.490 px/mm, 789.3 mm stock extended, 2 mm off the real
    gun's published length). The photo is turned 0.66 degrees (the rails slope), so its points are straightened
    (fix_l) before use, and the barrel is lengthened by 97 mm ahead of the gas block to the STD's 13.8".
Profiles are written in each photo's (L, H) mm: L back from the photographed muzzle, H up from the lowest point.

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, every part in its own node or file and drawn at the gun's points. Drawn at 0.65 of
real size, as GoM draws its rifles (M4A1 0.63, G36 0.61, FAL 0.67 of their real lengths; the MP7 / P90 / pistols
use 0.72, as GoM's MP5 family). The SCAR-L takes GoM's STANAG magazines at `magazine` (their mesh, 0.65 scale, matches
the replica's magazine within 2 mm). The stock is one shared node, modelled deployed with its origin at the hinge
(the front face of the stock's hinge, on the bore axis); each gun's `stock` point puts it there and `stock_folded`
swings it 180 degrees about the hinge pin on the right side, so it lies along the right of the receiver as FN's does.
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
    "SCARL": os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SCARL.fbx"),
    "SCARH": os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SCARH.fbx"),
    "mags": os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SCARH_magazines.fbx"),
    "parts": os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_SCAR_parts.fbx"),
}

K = 0.00065                        # game units per real mm: GoM's rifles
kit.K = K
MATS = ["tan", "polymer", "black", "metal", "dark", "rubber", "magsteel", "brass", "copper", "suppressor"]
kit.MATS[:] = MATS

# The SCAR-L photo slopes 0.66 degrees (its top rail falls 4.6 mm over 400 mm toward the stock): straightened about L 300.
TILT_L = 0.0115
STD_EXTRA = 97.0                   # Mk 16 STD barrel (13.8") against the photographed CQC's 10"


def fix_l(points):
    return [(L, round(H + TILT_L * (L - 300.0), 2)) for L, H in points]


class Gun:
    """One rifle's photo frame: origin (L0, H0) = rear-top of the pistol grip, bore height, half widths."""

    def __init__(self, name, L0, H0, bore, **kw):
        self.name, self.L0, self.H0, self.bore = name, L0, H0, bore
        self.__dict__.update(kw)

    def P(self, L, H):
        return self.L0 - L, H - self.H0

    def y(self, L):
        return self.L0 - L

    def z(self, H):
        return H - self.H0


# SCAR-L (straightened photo coordinates). Origin: the grip's back meets the receiver at L 491, H 132.
SL = Gun("SCARL", 491.0, 132.0, 186.0,
         muzzle=-STD_EXTRA, canon=-STD_EXTRA + 28.8,        # canon as GoM's M4A1: 0.0187 behind the muzzle
         front=125.0, rear=528.0, hinge=548.0,
         rail_top=232.1, rail_floor=229.8, bottom=159.3, bottom_floor=161.9, seam=173.0, hg_top=180.0,
         side_rail=(127.0, 230.0), side_rail_h=186.5, bottom_rail=(127.0, 298.0), step=300.0,
         w_upper=25.0, w_hg=24.0, w_lower=18.0, w_grip=15.0, w_guard=8.0, w_hinge=24.0,
         mag=(363.0, 163.0), optic_l=405.0, foregrip_l=215.0, bipod_l=140.0,
         handle=(268.0, 288.0, 207.0, 217.0), travel=85.0,
         port=(330.0, 398.0, 197.0, 216.0))
# SCAR-H (photo coordinates as traced). Origin: grip meets receiver at L 756, H 113.
SH = Gun("SCARH", 756.0, 113.0, 168.0,
         muzzle=0.0, canon=45.0,
         front=216.0, rear=797.0, hinge=820.0,
         rail_top=216.1, rail_floor=213.4, bottom=140.0, bottom_floor=142.8, seam=158.0, hg_top=180.0,
         side_rail=(218.0, 419.0), side_rail_h=169.0, bottom_rail=(218.0, 543.0), step=421.0,
         w_upper=27.0, w_hg=26.0, w_lower=21.0, w_grip=15.0, w_guard=8.5, w_hinge=26.0,
         mag=(614.0, 150.0), optic_l=640.0, foregrip_l=330.0, bipod_l=240.0,
         handle=(322.0, 350.0, 185.0, 200.0), travel=95.0,
         port=(585.0, 662.0, 178.0, 203.0))
W_STOCK = 21.0


def slab(g, b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="tan", x0=0.0):
    return kit.slab(b, [g.P(L, H) for L, H in outline], [[g.P(L, H) for L, H in h] for h in holes], half, bevel,
                    res, mat, x0)


def box(g, b, La, Lb, Ha, Hb, xa, xb, mat="tan", bevel=0.0):
    ya, yb = sorted((g.y(La), g.y(Lb)))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, g.z(Ha), g.z(Hb), mat=mat, bevel=bevel)


def lathe_bore(g, b, profile, seg=16, mat="metal"):
    """Revolved about the bore: profile [(L, radius)] from the rear to the muzzle."""
    b.lathe("y", (0, 0, g.z(g.bore)), [(g.y(L), r) for L, r in profile], seg=seg, mat=mat, phase=0.5)


def both(fn):
    for s in (1, -1):
        fn(s)


# ==================================================================================================
# Profiles (photo L, H mm; the SCAR-L's straightened)
# ==================================================================================================

L_PROFILES = {k: fix_l(v) for k, v in {
    # the lower receiver: polymer, from the handguard's rear down round the magazine well and trigger guard to the
    # grip, back under the receiver to the hinge
    "lower": [(300.0, 173.5), (308.0, 170.5), (308.7, 161.1), (311.4, 158.4), (320.0, 157.0), (324.8, 155.0),
              (328.9, 149.7), (328.9, 127.5), (326.2, 122.2), (326.2, 116.8), (332.0, 114.0), (398.0, 104.0),
              (406.7, 99.3), (459.8, 98.7), (466.0, 101.0), (466.0, 128.0), (490.0, 128.0), (492.0, 134.0),
              (496.7, 140.9), (503.4, 143.6), (528.0, 143.6), (528.0, 170.0)],
    "guard_hole": [(402.0, 132.0), (447.0, 132.0), (450.0, 129.0), (450.0, 106.0), (447.0, 103.0), (404.0, 103.0),
                   (400.0, 107.0), (400.0, 128.0)],
    "trigger": [(431.0, 132.0), (437.0, 132.0), (440.0, 124.0), (442.0, 114.0), (440.0, 107.0), (437.0, 106.0),
                (436.0, 110.0), (434.0, 118.0), (431.0, 126.0)],
    "grip": [(457.0, 128.0), (458.0, 100.0), (465.8, 88.6), (465.8, 85.2), (463.1, 80.5), (463.8, 78.5),
             (470.5, 77.9), (473.2, 75.2), (488.6, 46.3), (488.6, 43.6), (485.9, 38.9), (492.6, 34.2), (529.6, 42.3),
             (538.3, 45.6), (539.0, 48.3), (530.9, 60.4), (522.8, 72.5), (492.0, 120.1), (490.6, 128.0),
             (492.0, 134.0), (470.0, 134.0)],
    "front_sight": [(100.0, 207.0), (100.0, 234.0), (103.0, 240.0), (103.0, 264.0), (101.0, 282.0), (106.0, 283.0),
                    (110.0, 279.0), (114.0, 279.0), (118.0, 283.0), (120.0, 282.0), (118.0, 264.0), (118.0, 240.0),
                    (121.0, 234.0), (121.0, 207.0)],
    # flip-up rear sight, folded flat on the rail (GoM optics sit over it)
    "rear_sight": [(450.0, 231.0), (450.0, 236.0), (454.0, 239.0), (486.0, 239.0), (490.0, 236.0), (490.0, 231.0)],
    "bolt_release": [(362.0, 157.0), (362.0, 164.0), (395.0, 164.0), (397.0, 160.0), (395.0, 157.0)],
    "mag_release": [(357.0, 147.0), (357.0, 152.0), (410.0, 152.0), (410.0, 147.0)],
    "bolt_catch": [(396.0, 150.0), (396.0, 178.0), (403.0, 178.0), (403.0, 150.0)],
    "selector": [(440.0, 149.0), (440.0, 155.0), (460.0, 157.0), (488.0, 154.0), (488.0, 150.0), (460.0, 147.0)],
}.items()}
L_PROFILES["selector_pivot"] = fix_l([(460.0, 152.0)])[0]

H_PROFILES = {
    "lower": [(545.0, 158.0), (549.7, 153.3), (549.7, 146.1), (551.9, 141.1), (555.7, 138.4), (565.6, 136.7),
              (569.5, 132.9), (570.6, 130.1), (570.6, 109.7), (567.3, 104.2), (567.3, 98.7), (574.0, 99.0),
              (652.0, 84.0), (660.0, 82.0), (668.7, 79.4), (722.2, 79.9), (725.0, 82.0), (727.0, 112.0),
              (755.0, 113.0), (760.8, 121.3), (769.1, 124.6), (797.0, 125.0), (797.0, 158.0)],
    "guard_hole": [(664.0, 111.0), (708.0, 111.0), (712.0, 107.0), (712.0, 88.0), (708.0, 84.0), (664.0, 84.0),
                   (660.0, 88.0), (660.0, 107.0)],
    "trigger": [(694.0, 111.0), (700.0, 111.0), (700.0, 104.0), (698.0, 96.0), (694.0, 90.0), (690.0, 88.0),
                (688.0, 90.0), (692.0, 96.0), (694.0, 104.0)],
    "grip": [(722.0, 112.0), (722.0, 80.0), (725.0, 76.6), (730.5, 66.2), (730.5, 62.3), (727.7, 58.4),
             (728.8, 54.6), (735.4, 54.6), (741.0, 48.5), (753.6, 25.9), (753.6, 22.6), (750.9, 18.2), (751.4, 16.5),
             (755.3, 13.2), (761.4, 13.2), (799.4, 23.7), (804.4, 25.9), (805.5, 27.0), (804.9, 29.8),
             (756.4, 100.9), (755.8, 113.0)],
    "front_sight": [(218.0, 213.0), (218.0, 226.0), (228.0, 231.0), (239.0, 233.0), (239.0, 256.0), (248.0, 256.5),
                    (248.0, 233.0), (246.0, 226.0), (245.0, 213.0)],
    "rear_sight": [(746.0, 215.0), (746.0, 220.0), (750.0, 223.0), (788.0, 223.0), (792.0, 220.0), (792.0, 215.0)],
    "bolt_release": [(563.0, 146.0), (563.0, 153.0), (608.0, 153.0), (610.0, 149.0), (608.0, 146.0)],
    "mag_release": [(563.0, 130.0), (563.0, 136.0), (640.0, 136.0), (640.0, 130.0)],
    "bolt_catch": [(650.0, 147.0), (650.0, 170.0), (662.0, 170.0), (662.0, 147.0)],
    "selector": [(705.0, 134.0), (705.0, 140.0), (720.0, 142.0), (752.0, 139.0), (752.0, 134.0), (720.0, 133.0)],
    "selector_pivot": (720.0, 138.0),
}

# The folding stock, traced on the SCAR-L photo (straightened), shared by both guns. Its own frame: u = L - 548 (back
# from the stock's front face at the hinge), h = H - the bore (186).
STOCK_RAW = fix_l([(548.0, 147.0), (548.0, 236.0), (556.0, 241.0), (566.0, 236.0), (570.0, 232.0), (595.0, 226.0),
                   (640.0, 216.0), (667.0, 205.0), (671.0, 200.5), (762.0, 197.0), (766.0, 202.0), (785.0, 201.5),
                   (789.0, 197.0), (789.0, 186.0), (784.0, 135.0), (783.0, 96.0), (785.0, 80.0), (784.0, 63.0),
                   (781.0, 59.0), (764.0, 58.0), (762.0, 64.0), (752.0, 65.0), (745.0, 70.0), (712.0, 134.0),
                   (709.0, 142.0), (664.0, 145.0)])
STOCK_FRONT_L = 548.0
STOCK = [(L - STOCK_FRONT_L, H - SL.bore) for L, H in STOCK_RAW]
PAD_U = 773.0 - STOCK_FRONT_L       # the rubber butt pad behind this


# ==================================================================================================
# Geometry
# ==================================================================================================

def upper(g, b):
    """Tan aluminium upper with its rail along the top; the black handguard under its front with the bottom rail and
    the side rails; the barrel, gas block, front sight and muzzle."""
    # the upper reaches down to the lower receiver behind `step`, to the handguard's top in front of it
    slab(g, b, [(g.front, g.hg_top), (g.front, g.rail_floor), (g.rear, g.rail_floor), (g.rear, g.seam),
                (g.step, g.seam), (g.step, g.hg_top)],
         half=g.w_upper, bevel=1.6, mat="tan")
    hg_rear = g.bottom_rail[1] + 2.0
    hg = [(g.front, g.bottom_floor), (g.front, g.hg_top + 0.5), (g.step, g.hg_top + 0.5)]
    if hg_rear > g.step + 1.0:                           # SCAR-H: under the upper back to the magazine well
        hg += [(g.step, g.seam + 0.5), (hg_rear, g.seam + 0.5)]
    hg += [(max(hg_rear, g.step), g.bottom_floor)]
    slab(g, b, hg, half=g.w_hg, bevel=1.4, mat="black")
    ya, yb = sorted((g.y(g.rear - 2.0), g.y(g.front + 2.0)))
    kit.picatinny(b, ya, yb, lambda u, h, y: Vector((u, y, g.z(g.rail_floor) + h)), base_h=0.5,
                  tooth_h=g.rail_top - g.rail_floor + 0.5, mat="tan")
    ya, yb = sorted((g.y(g.bottom_rail[1]), g.y(g.bottom_rail[0])))
    kit.picatinny(b, ya, yb, lambda u, h, y: Vector((u, y, g.z(g.bottom_floor) - h)), base_h=0.5,
                  tooth_h=g.bottom_floor - g.bottom + 0.5, mat="black")
    ya, yb = sorted((g.y(g.side_rail[1]), g.y(g.side_rail[0])))
    for s in (1, -1):
        kit.picatinny(b, ya, yb, lambda u, h, y, s=s: Vector((s * (g.w_hg + h), y, g.z(g.side_rail_h) + u)),
                      base_h=1.5, tooth_h=3.0, mat="black")
    # hinge block at the rear (the stock folds about its right side)
    slab(g, b, [(g.rear, g.seam - 26.0 if g is SL else 127.0), (g.rear, g.rail_floor + 1.0),
                (g.hinge, g.rail_floor + 1.0), (g.hinge, g.seam - 26.0 if g is SL else 127.0)],
         half=g.w_hinge, bevel=1.5, mat="black")
    slab(g, b, PROF[g.name]["front_sight"], half=7.0, bevel=0.8, mat="black")
    slab(g, b, PROF[g.name]["rear_sight"], half=9.0, bevel=0.8, mat="black")


def barrel_l(b):
    g = SL
    m = g.muzzle
    # flash hider (A2-style birdcage FN fits, as photographed), its lock collar, the barrel, the gas block
    lathe_bore(g, b, [(m + 50.0, 0), (m + 50.0, 9.0), (m + 30.0, 9.0), (m + 28.0, 10.8), (m + 20.0, 10.8),
                      (m + 18.0, 11.0), (m + 1.0, 11.0), (m, 10.0), (m, 4.2), (m + 8.0, 4.2), (m + 8.0, 0)], seg=16)
    lathe_bore(g, b, [(80.0, 0), (80.0, 7.6), (m + 49.0, 7.6), (m + 49.0, 0)], seg=14)
    lathe_bore(g, b, [(126.0, 0), (126.0, 15.0), (80.0, 15.0), (80.0, 0)], seg=16, mat="black")   # gas block
    box(g, b, 79.0, 93.0, 199.0, 213.0, -8.0, 8.0, mat="black", bevel=1.0)                         # regulator
    box(g, b, 98.0, 123.0, 196.0, 209.0, -10.0, 10.0, mat="black", bevel=1.0)                      # sight base


def barrel_h(b):
    g = SH
    lathe_bore(g, b, [(55.0, 0), (55.0, 10.0), (46.0, 10.0), (45.0, 11.0), (30.0, 11.0), (28.0, 10.2),
                      (22.0, 10.2), (20.0, 11.0), (1.0, 11.0), (0.0, 10.0), (0.0, 4.6), (9.0, 4.6), (9.0, 0)], seg=16)
    lathe_bore(g, b, [(217.0, 0), (217.0, 9.6), (112.0, 9.6), (110.0, 8.2), (54.0, 8.2), (54.0, 0)], seg=14)
    lathe_bore(g, b, [(219.0, 0), (219.0, 14.0), (213.0, 14.0), (213.0, 0)], seg=16, mat="black")  # barrel nut


def lower(g, b):
    p = PROF[g.name]
    slab(g, b, p["lower"], [p["guard_hole"]], half=g.w_lower, bevel=2.2, res=1, mat="polymer")
    slab(g, b, p["grip"], half=g.w_grip, bevel=4.0, res=1, mat="polymer")
    slab(g, b, p["trigger"], half=2.8, bevel=0.6, mat="dark")
    x = g.w_lower
    both(lambda s: slab(g, b, p["bolt_release"], half=0.9, bevel=0.4, mat="polymer", x0=s * (x + 0.6)))
    both(lambda s: slab(g, b, p["selector"], half=1.0, bevel=0.4, mat="dark", x0=s * (x + 2.4)))
    cl, ch = p["selector_pivot"]
    both(lambda s: b.lathe("x", (0, *g.P(cl, ch)), [(s * (x - 0.5), 0), (s * (x - 0.5), 6.5), (s * (x + 2.0), 6.5),
                                                    (s * (x + 2.6), 5.0), (s * (x + 2.6), 0)], seg=12, mat="dark"))
    slab(g, b, p["mag_release"], half=0.9, bevel=0.3, mat="dark", x0=x + 0.6)       # left side only, as FN's
    slab(g, b, p["bolt_catch"], half=1.0, bevel=0.4, mat="dark", x0=x + 0.8)


def build_body(g):
    b = kit.Builder()
    upper(g, b)
    (barrel_l if g is SL else barrel_h)(b)
    lower(g, b)
    return b.to_object(g.name + "_BODY")


def build_bolt(g):
    """The charging handle on the left (FN's is reversible; both photos' guns carry it left), forward: bolt_lock.
    It rides with the bolt carrier, so GoM's Bolt_Fired swap pulls it back by `travel` on each shot."""
    b = kit.Builder()
    La, Lb, Ha, Hb = g.handle
    box(g, b, La, Lb, Ha, Hb, g.w_upper - 3.0, g.w_upper + 6.0, mat="dark", bevel=1.0)
    box(g, b, La + 2.0, Lb - 1.0, Ha + 1.0, Hb - 1.0, g.w_upper + 6.0, g.w_upper + 17.0, mat="dark", bevel=2.0)
    return b.to_object(g.name + "_BOLT")


def build_stock():
    """Origin = the hinge: the stock's front face on the bore axis; modelled deployed, extending along -Y."""
    b = kit.Builder()
    kit.slab(b, [(-u, h) for u, h in STOCK], [], W_STOCK, 3.0, 1, "polymer", 0.0)
    # rubber butt pad over the rear
    pad = [(u, h) for u, h in STOCK if u >= PAD_U - 0.5]
    lo, hi = min(h for _, h in pad), max(h for _, h in pad)
    b.box(-W_STOCK - 0.6, W_STOCK + 0.6, -(STOCK[13][0] + 0.6), -PAD_U, lo - 0.6, hi + 0.6, mat="rubber", bevel=1.5)
    return b.to_object("SCAR_STOCK")


MAG_TOP, MAG_FRONT, MAG_REAR = 150.0, 575.0, 653.0    # SCAR-H magazine in its photo (H 150 = the feed lips)
MAG_W = 13.5


def build_scarh_mag(rounds):
    """FN's steel 20-round SCAR-H magazine (and a 10-round one 60 mm shorter), straight, origin at the feed lips."""
    b = kit.Builder()
    short = 0.0 if rounds == 20 else 60.0
    bottom = 14.0 + short
    q = lambda L, H: (SH.mag[0] - L, H - MAG_TOP)            # magazine frame: y forward, z from the lips
    body = [q(MAG_FRONT, bottom), q(MAG_FRONT, MAG_TOP - 3.0), q(MAG_FRONT + 4.0, MAG_TOP),
            q(MAG_REAR - 4.0, MAG_TOP), q(MAG_REAR, MAG_TOP - 3.0), q(MAG_REAR, bottom + 4.0)]
    kit.slab(b, body, [], MAG_W, 1.6, 0, "magsteel", 0.0)
    plate = [q(574.0, bottom + 6.0), q(572.0, bottom - 4.0), q(575.0, bottom - 12.0), q(590.0, bottom - 14.0),
             q(648.0, bottom - 9.0), q(653.0, bottom - 5.0), q(653.0, bottom + 2.0)]
    kit.slab(b, plate, [], MAG_W + 1.5, 2.0, 1, "polymer", 0.0)
    lips = [q(MAG_FRONT + 10.0, MAG_TOP - 1.0), q(MAG_REAR - 6.0, MAG_TOP - 1.0), q(MAG_REAR - 8.0, MAG_TOP + 3.0),
            q(MAG_FRONT + 18.0, MAG_TOP + 3.0)]
    both(lambda s: kit.slab(b, lips, [], 1.2, 0.3, 0, "magsteel", s * (MAG_W - 2.0)))
    # top round: 7.62x51, the bullet forward
    r0 = q(MAG_FRONT + 6.0, 0)[0]
    b.lathe("y", (0, 0, 3.0), [(r0 - 71.0, 0), (r0 - 71.0, 6.0), (r0 - 30.0, 6.0), (r0 - 26.0, 4.2),
                               (r0 - 20.0, 4.0)], seg=10, mat="brass")
    b.lathe("y", (0, 0, 3.0), [(r0 - 20.0, 4.0), (r0 - 10.0, 3.6), (r0 - 3.0, 1.6), (r0, 0)], seg=10, mat="copper")
    return b.to_object("762x51Magazine%d_SCARH" % rounds)


# ProMag's DRM-A41 (user, 2026-10-20): a 50-round polymer drum sold for the civilian SCAR 17S (FN made only the 10
# and 20), in FDE as the gun. A feed tower like the 20-round body down out of the magazine well into one round drum
# whose faces look to the front and back (its axis along the barrel, as the MP7's drum; user, 2026-10-20: the first
# build faced the sides), winding knob on the front face. About 144 mm across and 84 mm thick (the tower is 78 deep;
# approximate: no published drawing), its top 2 mm under the magazine well's rear edge (H 84).
DRUM_R, DRUM_HALF = 72.0, 42.0
DRUM_H = 84.0 - 2.0 - DRUM_R          # photo H of the drum's centre


def build_scarh_drum():
    b = kit.Builder()
    q = lambda L, H: (SH.mag[0] - L, H - MAG_TOP)
    foot = DRUM_H + 20.0
    tower = [q(MAG_FRONT, foot), q(MAG_FRONT, MAG_TOP - 3.0), q(MAG_FRONT + 4.0, MAG_TOP), q(MAG_REAR - 4.0, MAG_TOP),
             q(MAG_REAR, MAG_TOP - 3.0), q(MAG_REAR, foot)]
    kit.slab(b, tower, [], MAG_W, 1.6, 0, "polymer", 0.0)
    lips = [q(MAG_FRONT + 10.0, MAG_TOP - 1.0), q(MAG_REAR - 6.0, MAG_TOP - 1.0), q(MAG_REAR - 8.0, MAG_TOP + 3.0),
            q(MAG_FRONT + 18.0, MAG_TOP + 3.0)]
    both(lambda s: kit.slab(b, lips, [], 1.2, 0.3, 0, "magsteel", s * (MAG_W - 2.0)))
    h, r = DRUM_HALF, DRUM_R
    c = (0.0, 0.0, DRUM_H - MAG_TOP)
    b.lathe("y", c, [(-h, 0), (-h, r - 7.0), (-h + 1.2, r - 3.0), (-h + 3.0, r), (h - 3.0, r), (h - 1.2, r - 3.0),
                     (h, r - 7.0), (h, 0)], seg=28, mat="polymer")
    for sgn in (-1, 1):                                    # hub caps on both faces
        b.lathe("y", c, [(sgn * h, 0), (sgn * h, 20.0), (sgn * (h + 2.0), 18.5), (sgn * (h + 2.0), 0)], seg=18,
                mat="polymer")
    # winding knob on the front face (toward the muzzle): a round boss with a flat wing across it
    b.lathe("y", c, [(h + 2.0, 0), (h + 2.0, 9.0), (h + 7.0, 9.0), (h + 7.0, 0)], seg=14, mat="dark")
    b.box(-14.0, 14.0, h + 7.0, h + 11.0, c[2] - 3.5, c[2] + 3.5, mat="dark", bevel=1.0)
    r0 = q(MAG_FRONT + 6.0, 0)[0]                          # top round, as on the box magazines
    b.lathe("y", (0, 0, 3.0), [(r0 - 71.0, 0), (r0 - 71.0, 6.0), (r0 - 30.0, 6.0), (r0 - 26.0, 4.2),
                               (r0 - 20.0, 4.0)], seg=10, mat="brass")
    b.lathe("y", (0, 0, 3.0), [(r0 - 20.0, 4.0), (r0 - 10.0, 3.6), (r0 - 3.0, 1.6), (r0, 0)], seg=10, mat="copper")
    return b.to_object("762x51Magazine50_SCARH")


SUPP_LEN, SUPP_R = 190.0, 19.0
MOUNT_LEN = 52.0


def build_suppressor():
    """A 1.5" 7.62 can of the SureFire FA762SS kind, slid over the mount device; origin at `canon`, along +Y."""
    b = kit.Builder()
    L = SUPP_LEN
    b.lathe("y", (0, 0, 0), [(-2.0, 0), (-2.0, 14.0), (-1.0, 15.5), (22.0, 15.5), (24.0, 17.5), (28.0, SUPP_R),
                              (L - 8.0, SUPP_R), (L - 3.0, SUPP_R - 2.0), (L, SUPP_R - 6.0), (L, 5.5),
                              (L - 5.0, 4.8), (L - 5.0, 0)], seg=20, mat="suppressor")
    return b.to_object("SCARH_Suppressor")


def build_mount():
    """The fast-attach muzzle device the can locks onto, over the SCAR-H's flash hider (r 11 mm, 45 mm long);
    origin at `canon` (the hider's rear), along +Y."""
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(-1.0, 0), (-1.0, 12.0), (0.0, 13.0), (12.0, 13.0), (13.0, 14.5), (19.0, 14.5),
                              (20.0, 13.0), (MOUNT_LEN - 2.0, 13.0), (MOUNT_LEN, 11.5), (MOUNT_LEN, 5.2),
                              (MOUNT_LEN - 8.0, 4.8), (MOUNT_LEN - 8.0, 0)], seg=18, mat="metal")
    return b.to_object("SCARH_Muzzle_Mount_Device")


PROF = {"SCARL": L_PROFILES, "SCARH": H_PROFILES}


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: FN's flat dark earth (anodised upper, polymer lower and stock), black parts, phosphated steel
    "tan": (166, 146, 116), "polymer": (158, 132, 104), "black": (44, 43, 41), "metal": (58, 58, 60),
    "dark": (30, 30, 31), "rubber": (34, 34, 35), "magsteel": (150, 124, 94), "brass": (150, 118, 62),
    "copper": (140, 82, 52), "suppressor": (40, 40, 42),
}


kit.FONT.setdefault("5", ["111", "100", "111", "001", "111"])      # as build_ucp.py adds it


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] *= 0.55


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "brass", "copper", "magsteel")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal | (mat == MATS.index("black")), 60.0, 34.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 0.97, 0.92])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    if kind in ("SCARL", "SCARH"):
        g = SL if kind == "SCARL" else SH
        L, H = g.L0 - y, z + g.H0
        tan = (mat == MATS.index("tan")) & side & (np.abs(x) > g.w_upper - 0.6)
        poly = (mat == MATS.index("polymer")) & side & (np.abs(x) > g.w_lower - 0.6)
        grip = (mat == MATS.index("polymer")) & side & (np.abs(x) > g.w_grip - 0.8) & (H < g.H0 + 2.0) & (L > g.L0 - 40)
        black = (mat == MATS.index("black")) & side
        # the upper / lower seam, the upper's slots (left: charging channel and vents; right: ejection port)
        col[side & (np.abs(H - g.seam) < 0.6) & (L > g.front)] *= 0.55
        Ha, Hb = g.handle[2], g.handle[3]
        if g is SL:
            for La, Lb in ((157.0, 190.0), (192.0, 218.0), (222.0, 250.0)):
                col[tan & left & rounded_rect(L, H, La, Lb, 211.0, 218.0, 3.4)] = 12
            col[tan & left & rounded_rect(L, H, 258.0, 402.0, Ha + 1.5, Hb - 2.5, 3.0)] = 12
        else:
            col[tan & left & rounded_rect(L, H, 260.0, 352.0, 184.0, 204.0, 4.0)] = 14
            col[tan & left & rounded_rect(L, H, 352.0, 450.0, Ha + 4.0, Hb - 4.0, 3.0)] = 12
            col[tan & left & rounded_rect(L, H, 510.0, 665.0, 191.0, 197.0, 3.0)] = 12
        Pa, Pb, Pc, Pd = g.port
        port = tan & right & rounded_rect(L, H, Pa, Pb, Pc, Pd, 3.0)
        col[port] = col[port] * 0.2 + 8
        col[tan & right & rounded_rect(L, H, Pa - 2, Pb + 2, Pc - 2, Pd + 2, 4.0) & ~port] *= 0.75
        # FN's roundel on both sides, pins and screws through the upper
        logo_l = g.L0 - 25.0
        d = np.hypot((L - logo_l) / 1.3, H - (g.seam + 14.0))
        col[tan & (np.abs(d - 7.0) < 0.9)] = (226, 222, 210)
        col[tan & (d < 5.5) & (np.mod(L * 1.7, 2.0) < 0.7)] += 30
        for cL in (g.front + 12.0, g.L0 - 160.0, g.L0 - 75.0, g.rear - 22.0, g.rear - 10.0):
            pin(col, L, H, tan, cL, g.seam + 13.0)
        for cL in (g.L0 - 140.0, g.L0 - 40.0):
            pin(col, L, H, poly, cL, g.seam - 13.0, 2.6)
        # selector marks: S (safe) white, 1 and F red
        sel_l, sel_h = PROF[kind]["selector_pivot"]
        col[poly & (np.hypot(L - (sel_l - 16.0), H - (sel_h + 4.0)) < 1.4)] = (210, 208, 200)
        col[poly & (np.hypot(L - (sel_l - 5.0), H - (sel_h + 13.0)) < 1.4)] = (180, 40, 36)
        col[poly & (np.hypot(L - (sel_l + 9.0), H - (sel_h + 12.0)) < 1.4)] = (180, 40, 36)
        # grip: stippled panel
        panel = grip & (H < g.H0 - 18.0) & (H > g.H0 - 82.0)
        grains = panel & (kit.vnoise(p, 0.6, 21) > 0.55)
        col[grains] += 18
        col[panel & ~grains] *= 0.8
        # handguard: the rail covers' oval panels and screws
        for cL in (g.front + 8.0, g.side_rail[0] + 40.0, g.side_rail[1] - 30.0):
            pin(col, L, H, black & (np.abs(x) > g.w_hg + 3.5), cL, g.side_rail_h, 2.2)
        r = np.hypot(x, z - g.z(g.bore))
        metal = mat == MATS.index("metal")
        m = g.muzzle
        ang = np.mod(np.arctan2(x, z - g.z(g.bore)) / (2 * math.pi) * 6.0, 1.0)
        col[metal & (L > m + 1.5) & (L < m + 17.0) & (r > 9.5) & (np.abs(ang - 0.5) < 0.12)] = 8   # hider slots
        col[metal & (r < 4.8) & (L < m + 9.5)] = 6                                                 # the bore
    elif kind == "bolt":
        pass
    elif kind == "stock":
        u, h = -y, z
        pol = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_STOCK - 0.8)
        col[pol & (np.abs(h - (8.0 - 0.13 * u)) < 0.6) & (u > 12) & (u < 120)] *= 0.55      # cheek riser's edge
        col[pol & (np.abs(u - 122.0) < 0.6) & (h > -40) & (h < 14)] *= 0.55              # the telescoping joint
        for k in range(6):
            col[pol & (np.hypot(u - (135.0 + k * 9.5), h + 12.0) < 1.6)] *= 0.6             # position marks
        col[pol & rounded_rect(u, h, 168.0, 196.0, 6.0, 12.0, 2.5)] = 14                     # sling slot
        col[pol & rounded_rect(u, h, 200.0, 215.0, -22.0, -6.0, 2.0)] = 26                   # length latch
        ribs = pol & (u > 165) & (h < -35) & (np.mod(h, 6.0) < 1.6)
        col[ribs] *= 0.7
    elif kind == "drum":
        q_l = SH.mag[0] - y
        hh = z + MAG_TOP
        poly = (mat == MATS.index("polymer"))
        dz = hh - DRUM_H
        r = np.hypot(x, dz)
        fwd, back = n[..., 1] > 0.7, n[..., 1] < -0.7
        face = poly & (fwd | back) & (np.abs(y) > DRUM_HALF - 0.5) & (r < DRUM_R - 3.0)
        col[face & (np.abs(r - 60.0) < 0.9)] *= 0.55                     # groove round each face
        col[face & (np.abs(r - 30.0) < 0.7)] *= 0.62
        for k in range(12):                                              # moulded spokes between the rings
            a = k * math.pi / 6.0
            d = np.abs(np.cos(a) * dz - np.sin(a) * x)
            col[face & (d < 1.0) & (r > 31.5) & (r < 58.5)] *= 0.8
        # "50" upright under the hub, reading the right way in game: seen from behind the gun's right (-X) is on the
        # viewer's right, so it reads toward -X there (the MP7 drum's rule)
        for f, uu in ((face & back, -x), (face & fwd, x)):
            col[f & kit.text_mask(uu, dz, "50", -11.2, -55.0, 16.0)] = (60, 50, 40)
        tower = poly & side & (hh > DRUM_H + DRUM_R)
        for rl in (588.0, 640.0):
            col[tower & (np.abs(q_l - rl) < 1.4)] *= 0.72
    elif kind.startswith("mag"):
        q_l = SH.mag[0] - y                                       # photo L on the gun
        steel = (mat == MATS.index("magsteel")) & side
        for rl in (588.0, 598.0, 628.0, 640.0):                   # pressed ribs
            col[steel & (np.abs(q_l - rl) < 1.4)] *= 0.72
            col[steel & (np.abs(q_l - rl - 1.6) < 0.5)] += 18
        hh = z + MAG_TOP
        if kind == "mag20":
            col[steel & left & (np.abs(q_l - 613.0) < 3.0) & (np.abs(hh - 40.0) < 0.6)] = (40, 36, 30)
        col[(mat == MATS.index("polymer")) & side & rounded_rect(q_l, hh, 582.0, 640.0,
                                                                  (14.0 if kind == "mag20" else 74.0) - 10.0,
                                                                  (14.0 if kind == "mag20" else 74.0) - 6.0, 1.5)] = 60
    elif kind == "suppressor":
        r = np.hypot(x, z)
        a = np.arctan2(x, z)
        knurl = (y > 1) & (y < 21) & (r > 14.5)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 2.0) < 1.0) ^ (np.mod(a[knurl] * 17.2 / math.pi, 1.0)
                                                                         < 0.5)))[..., None]
        col[(np.abs(y - 26.0) < 0.8) | (np.abs(y - (SUPP_LEN - 6.0)) < 0.7)] *= 0.5
        col[(r < 6.0) & (y > SUPP_LEN - 1.0)] = 6
    elif kind == "mount":
        r = np.hypot(x, z)
        a = np.mod(np.arctan2(x, z) / (2 * math.pi) * 24.0, 1.0)
        col[(y > 13) & (y < 19) & (r > 13.5) & (a < 0.45)] *= 0.45                     # the can's ratchet teeth
        ang = np.mod(np.arctan2(x, z) / (2 * math.pi) * 3.0, 1.0)
        col[(y > 26) & (y < MOUNT_LEN - 3) & (r > 12.0) & (np.abs(ang - 0.5) < 0.13)] = 9  # three ports
        col[r < 5.4] = 7
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
# Attachment points (GoM's rifle set, at the relations GoM's M4A1 / FAL and our MP7 use)
# ==================================================================================================

def gp(g, L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round(g.y(L) * K, 4) + 0.0, round(g.z(H) * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def points(g, bounds):
    rail_top = g.z(g.rail_top) * K
    side = (g.w_hg + 3.5) * K                            # the side rails' crossbar faces (picatinny(): 1.5 + 3.0 - 1)
    sy = round(g.y(sum(g.side_rail) / 2) * K, 4)
    sz = round(g.z(g.side_rail_h) * K, 4)
    oy = round(g.y(g.optic_l) * K, 4)
    bottom = g.z(g.bottom) * K
    stock = gp(g, g.hinge, g.bore)
    hinge_x = -(g.w_upper + W_STOCK) / 2.0 - 1.0          # the hinge pin, on the right
    pts = {
        "muzzle": {"offset": gp(g, g.muzzle, g.bore), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(g, *g.mag), "rotate": ZERO},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up, and its scopes sit 0.0032 under that rail's
        # top (the MP7's relations, as on GoM's MP5)
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        "rail_left": {"offset": [round(side - 0.0055, 4), sy, sz], "rotate": ZERO},
        "rail_right": {"offset": [round(-(side - 0.0055), 4), sy, sz], "rotate": ZERO},
        "light_left": {"offset": [round(side - 0.0055 + 0.0062, 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), sy, round(sz - 0.0008, 4)], "rotate": ZERO},
        "rail_down": {"offset": [0.0, round(g.y(sum(g.bottom_rail) / 2) * K, 4), round(bottom + 0.0055, 4)],
                      "rotate": ZERO},
        "foregrip": {"offset": [0.0, round(g.y(g.foregrip_l) * K, 4), round(bottom + 0.003, 4)], "rotate": ZERO},
        "canon": {"offset": gp(g, g.canon, g.bore), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-g.travel * K, 4), 0.0], "rotate": ZERO},
        "stock": {"offset": stock, "rotate": ZERO},
        # turned 180 degrees about the hinge pin: offset = stock + 2 x the pin's x
        "stock_folded": {"offset": [round(stock[0] + 2.0 * hinge_x * K, 4), stock[1], stock[2]],
                         "rotate": [0.0, 0.0, 180.0]},
    }
    # GoM's bipods (its FAL: 0.0006 under the bottom of the rail they clamp to), at the handguard's front
    pts["bipod"] = {"offset": [0.0, round(g.y(g.bipod_l) * K, 4), round(bottom + 0.0006, 4)], "rotate": ZERO}
    pts["world"] = {"offset": [0.02, 0.13, 0.0], "rotate": [180.0, 0.0, 180.0]}       # every GoM rifle
    pts["_notes"] = {
        "units": "game units (0.65 of real size, GoM's rifles); +Y muzzle, +Z top, +X the gun's left; origin = the "
                 "rear-top of the pistol grip (photo L %.0f, H %.0f)" % (g.L0, g.H0),
        "magazine": ("GoM's STANAG magazines hang from here (their feed lips)" if g is SL
                     else "762x51Magazine20/10_SCARH, origin at their feed lips"),
        "stock": "SCAR_STOCK (shared, in GunsOfTienPost93_SCAR_parts.fbx) is modelled deployed with its origin at "
                 "the hinge: its front face on the bore axis",
        "stock_folded": "the same node turned 180 degrees about the hinge pin at x %.1f mm (the right side)" % hinge_x,
        "bolt_fired": "the charging handle back %.0f mm real (it reciprocates on the SCAR)" % g.travel,
        "canon": ("as GoM's M4A1, 28.8 mm (0.0187) behind the muzzle: GoM's AR mount device and its muzzle parts"
                  if g is SL else "the flash hider's rear: SCARH_Muzzle_Mount_Device and SCARH_Suppressor"),
    }
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [g.L0, g.H0], "bore_mm": g.bore,
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

    guns = {g.name: (build_body(g), build_bolt(g)) for g in (SL, SH)}
    stock = build_stock()
    mags = [build_scarh_mag(20), build_scarh_mag(10), build_scarh_drum()]
    supp, mount = build_suppressor(), build_mount()
    for body, bolt in guns.values():
        kit.unwrap([body, bolt], 0.005)
    for o in [stock] + mags + [supp, mount]:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    for name, (body, bolt) in guns.items():
        texture([body, bolt], [[body, bolt], [body, bolt]], [name, "bolt"], 256, os.path.join(TEX_DIR, name + ".png"))
    texture([stock], [[stock]], ["stock"], 128, os.path.join(TEX_DIR, "SCAR_STOCK.png"))
    for kind, m in zip(("mag20", "mag10", "drum"), mags):
        texture([m], [[m]], [kind], 128, os.path.join(TEX_DIR, m.name + ".png"))
    texture([supp], [[supp]], ["suppressor"], 128, os.path.join(TEX_DIR, "SCARH_Suppressor.png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "SCARH_Muzzle_Mount_Device.png"))

    shared = {o.name: kit.bounds_of(o) for o in [stock] + mags + [supp, mount]}
    for g in (SL, SH):
        body, bolt = guns[g.name]
        bounds = {o.name: kit.bounds_of(o) for o in (body, bolt)}
        bounds.update(shared)
        pts = points(g, bounds)
        bounds["SCAR_STOCK_deployed"] = kit.bounds_at(stock, pts["stock"])
        bounds["SCAR_STOCK_folded"] = kit.bounds_at(stock, pts["stock_folded"])
        with open(os.path.join(HERE, g.name.lower() + "_points.json"), "w") as fh:
            json.dump(pts, fh, indent=2)
            fh.write("\n")
        kit.export([body, bolt], FBX[g.name])
        for name, b in bounds.items():
            print("%s %-28s tris %5d  min %s  max %s" % (g.name, name, b["tris"], b["min"], b["max"]))
    kit.export(mags, FBX["mags"])
    kit.export([stock, supp, mount], FBX["parts"])


if __name__ == "__main__":
    main()
