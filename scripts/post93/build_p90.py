"""FN P90 TR models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_p90.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx          P90TR_BODY, P90TR_BOLT
    P/models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx  57x28Magazine50_P90
    P/models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx          P90_Suppressor, P90_Muzzle_Mount_Device
    P/textures/weapons/GunsOfTienPost93/<name>.png                  P90TR (256, body + bolt), one 128 texture per
                                                                     magazine / part
    scripts/post93/p90_points.json                                  attachment points (game space)

The P90 is held like a pistol (SwingAnim = Handgun), so its body and bolt are exported upside down, the way GoM
builds its pistols, MP5K, TEC9 and MAC10: everything below is modelled and baked upright and turned 180 degrees
about the bore axis at export, with the attachment points (see points()).

The shape is measured from a side photo of a P90 TR (CLAUDE.md, "P90 TR reference"; its traced outline is
p90_reference_outline.json, which render_p90.py / make_p90_art.py lay over the model to check it). Every side
profile below is written in that photo's coordinates, real millimetres: L back from the muzzle tip, H up from the
gun's lowest point. Each part is one such profile (holes allowed: the trigger opening, the thumbhole, the magazine
window) extruded across the gun with a chamfered or two-step rounded edge, which is how GoM's own guns are built:
flat faceted hard-surface shapes, the detail (screws, seams, markings, edge wear) in the baked texture.

Geometry helpers, bakes, noise, FBX export and the deterministic FBX rewrite come from build_mp7.py (imported as a
library; its material list is replaced by this gun's). GoM's conventions: game +Y muzzle, +Z top, +X the gun's
LEFT, origin at the rear-top of the pistol grip, 0.72 of real size.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402

MEDIA = kit.MEDIA
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_P90TR.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_P90_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_P90_parts.fbx")
TEX_DIR = kit.TEX_DIR
POINTS_JSON = os.path.join(HERE, "p90_points.json")

K = kit.K                          # game units per real millimetre
MATS = ["polymer", "grip", "metal", "rail", "dark", "smoke", "magcap", "brass", "copper", "suppressor"]
kit.MATS[:] = MATS                 # build_mp7's Builder, materials and bake passes index this list

# Photo coordinates (mm) of the model origin: the rear-top of the grip column, where the thumbhole's front edge
# meets the frame above it. game y = L0 - L, game z = H - H0.
L0, H0 = 237.0, 80.0
BORE_H = 99.8                      # bore axis (flash hider centre in the photo)
BORE_Z = BORE_H - H0
CANON_L = 43.0                     # receiver front face, where the barrel collar starts
RAIL_TOP_H = 181.0                 # top of the Picatinny teeth
BOSS_L, BOSS_H = 83.0, 162.0       # side accessory boss on the rail block (both sides)
BOSS_X = 28.0                      # its outer face
MAG_L, MAG_H = 79.5, 118.5         # magazine origin: front end, bottom face, centred
CH_TRAVEL = 60.0                   # charging handle pull

W_FRAME, W_BAND, W_BUTT, W_METAL, W_MAG = 23.5, 25.0, 27.5, 25.5, 23.0   # half widths


def P(L, H):
    """Photo (L, H) mm -> game (y, z) mm."""
    return L0 - L, H - H0


# ==================================================================================================
# Geometry
# ==================================================================================================

def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    """Side profile [(L, H)] with optional holes, extruded across x0 - half .. x0 + half (build_mp7.slab)."""
    return kit.slab(b, [P(L, H) for L, H in outline], [[P(L, H) for L, H in h] for h in holes], half, bevel, res,
                    mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def both(fn):
    for s in (1, -1):
        fn(s)


def circle(cL, cH, r, n=10, phase=0.0):
    return [(cL + r * math.cos(2 * math.pi * (k + phase) / n), cH + r * math.sin(2 * math.pi * (k + phase) / n))
            for k in range(n)]


# The lower frame: front hand stop, the trigger loop, the grip column, the belly under the thumbhole, up to the
# seam under the receiver (H 93). Points from the traced photo outline.
FRAME = [(43.0, 93.0), (43.0, 81.0), (47.4, 37.4), (61.1, 37.7), (62.9, 40.4), (62.9, 54.1), (66.1, 58.2),
         (70.5, 60.0), (86.0, 59.4), (90.4, 55.9), (91.9, 53.2), (94.2, 35.7), (98.3, 25.7), (103.6, 18.1),
         (110.6, 11.1), (116.4, 7.0), (124.3, 3.2), (134.3, 0.6), (170.0, 0.3), (170.9, 3.8), (164.7, 29.5),
         (166.5, 33.6), (168.5, 35.7), (172.9, 37.2), (188.1, 37.2), (203.3, 21.9), (218.3, 11.7), (236.7, 4.1),
         (254.8, 0.9), (300.2, 0.9), (304.9, 7.0), (365.7, 26.6), (375.0, 26.6), (375.0, 93.0)]
TRIGGER_HOLE = [(157.1, 76.7), (160.6, 72.8), (162.4, 68.2), (162.4, 60.9), (161.0, 52.5), (157.5, 46.5),
                (151.0, 42.6), (145.0, 41.4), (139.8, 41.3), (131.9, 41.8), (127.6, 44.2), (124.3, 47.4),
                (121.7, 52.7), (121.1, 58.2), (122.0, 62.3), (126.1, 68.5), (132.8, 72.3), (136.0, 74.3),
                (139.3, 77.2), (143.4, 79.0), (149.8, 79.6)]
THUMBHOLE = [(234.3, 76.4), (237.6, 79.3), (242.2, 81.6), (276.8, 81.9), (282.0, 80.2), (289.1, 75.8),
             (295.5, 68.2), (297.8, 60.6), (297.0, 52.4), (292.3, 44.5), (286.1, 39.5), (277.6, 36.6),
             (272.4, 36.6), (267.7, 37.7), (241.7, 48.6), (234.1, 54.4), (231.1, 59.7), (230.5, 67.3),
             (231.7, 72.0)]
# The butt: a tall slab, its upper front face at the magazine's rear end, the lower one behind the frame.
BUTT = [(352.0, 118.0), (352.0, 139.5), (488.3, 140.4), (498.5, 139.6), (500.0, 137.8), (500.0, 131.9),
        (497.1, 102.7), (496.8, 69.9), (500.0, 25.2), (499.1, 23.1), (495.3, 22.5), (374.2, 22.2),
        (372.1, 26.6), (369.0, 27.5), (369.0, 84.0), (352.0, 84.0)]
# The TR's metal upper: the receiver band under the magazine, the front column, the rail block over the magazine
# and the hoop arching down behind it. The magazine window and the slot in the block go through it.
METAL = [(42.5, 93.0), (205.0, 93.0), (210.0, 95.5), (213.5, 99.5), (215.0, 105.0), (214.5, 125.0),
         (212.5, 141.0), (208.0, 158.0), (203.5, 170.0), (199.5, 176.0), (60.3, 176.0), (47.4, 159.2),
         (43.0, 148.3), (42.1, 142.5)]
MAG_WINDOW = [(78.5, 118.5), (175.5, 118.5), (176.5, 134.0), (175.5, 143.0), (173.0, 150.0), (169.5, 155.3),
              (93.0, 144.2), (86.0, 141.6), (78.5, 141.6)]
TOP_SLOT = [(164.4, 164.4), (165.6, 163.3), (193.7, 163.3), (196.9, 164.4), (196.9, 169.4), (195.4, 170.9),
            (167.1, 170.9), (164.4, 169.4)]
HANDLE = [(69.0, 99.0), (70.5, 96.0), (75.0, 94.5), (84.0, 95.0), (86.5, 98.0), (86.5, 106.0), (84.0, 110.5),
          (77.0, 112.0), (71.5, 110.5), (69.0, 106.5)]
RAIL_TEETH = [60.3 + i * 9.92 for i in range(14)]     # front edge of each tooth, 5.3 mm long


def build_body():
    b = kit.Builder()
    slab(b, FRAME, [TRIGGER_HOLE, THUMBHOLE], half=W_FRAME, bevel=5.0, res=1)
    # receiver band (polymer) from the hoop into the butt, the butt, the raised FN logo panels
    box(b, 205.0, 356.0, 84.0, 118.0, -W_BAND, W_BAND, bevel=2.0)
    slab(b, BUTT, half=W_BUTT, bevel=4.0, res=1)
    both(lambda s: box(b, 320.0, 359.0, 36.0, 74.0, s * (W_FRAME - 2.0), s * (W_FRAME + 1.0), bevel=0.8))
    # magazine catch housing under the magazine's rear end, release tab at the butt's top front
    box(b, 314.0, 342.0, 104.0, 118.4, -27.0, 27.0, bevel=2.5)
    box(b, 344.0, 360.0, 119.0, 134.0, -15.0, 15.0, mat="rail", bevel=1.0)
    # metal upper, rail on top, accessory bosses on the sides
    slab(b, METAL, [MAG_WINDOW, TOP_SLOT], half=W_METAL, bevel=2.0, res=0, mat="metal")
    box(b, 57.0, 198.0, 175.0, 178.6, -7.8, 7.8, mat="rail", bevel=0.4)
    for L in RAIL_TEETH:
        box(b, L, L + 5.3, 175.0, RAIL_TOP_H, -10.6, 10.6, mat="rail", bevel=0.5)

    def boss(s):
        box(b, 77.0, 89.0, 149.5, 172.0, s * (W_METAL - 1.0), s * BOSS_X, mat="metal", bevel=0.6)
        box(b, 71.0, 95.0, 156.5, 167.5, s * (W_METAL - 1.0), s * BOSS_X, mat="metal", bevel=0.6)
    both(boss)
    # trigger at the bottom rear of the trigger loop
    box(b, 148.0, 169.0, 46.5, 53.0, -8.0, 8.0, mat="dark", bevel=0.8)
    # barrel collar, knurled ring and the flash hider with its open bore (lathe t = game y)
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_Z), [(t(CANON_L + 1.0), 0), (t(CANON_L + 1.0), 9.3), (t(38.5), 9.3), (t(38.5), 11.0),
                                  (t(37.8), 11.7), (t(29.2), 11.7), (t(28.5), 11.0), (t(28.5), 10.4),
                                  (t(1.2), 10.4), (t(0.0), 9.2), (t(0.0), 5.0), (t(12.0), 5.0), (t(12.0), 0)],
            seg=16, mat="metal", phase=0.5)
    return b.to_object("P90TR_BODY")


def build_bolt():
    """The two charging handles, forward (bolt_lock); bolt_fired slides them back along the side tracks."""
    b = kit.Builder()
    hole = circle(77.5, 103.5, 4.2, 8, 0.5)
    both(lambda s: slab(b, HANDLE, [hole], half=2.5, bevel=0.8, res=0, mat="metal", x0=s * (W_METAL + 2.0)))
    both(lambda s: box(b, 72.0, 84.0, 101.0, 106.0, s * (W_METAL - 1.5), s * (W_METAL + 0.5), mat="metal"))
    return b.to_object("P90TR_BOLT")


def build_magazine():
    """Smoky translucent body between two opaque end caps, origin at the front end of its bottom face."""
    b = kit.Builder()
    box(b, 88.0, 322.0, 118.6, 141.4, -(W_MAG - 0.2), W_MAG - 0.2, mat="smoke", bevel=1.5)
    box(b, MAG_L, 88.5, MAG_H, 141.8, -W_MAG, W_MAG, mat="magcap", bevel=1.2)
    box(b, 321.5, 350.5, MAG_H, 141.6, -W_MAG, W_MAG, mat="magcap", bevel=1.5)
    box(b, 334.0, 346.0, 141.0, 142.6, -9.0, 9.0, mat="magcap", bevel=0.5)          # rear grip ridge
    shift = Vector((0.0, L0 - MAG_L, MAG_H - H0))
    for v in b.bm.verts:
        v.co -= shift
    return b.to_object("57x28Magazine50_P90")


def build_suppressor():
    """Origin at the receiver's front face (`canon`); slides over the mount device on the flash hider."""
    b = kit.Builder()
    L = 172.0
    b.lathe("y", (0, 0, 0), [(4.0, 0), (4.0, 13.8), (30.0, 13.8), (32.0, 16.0), (36.0, 19.0), (L - 8, 19.0),
                              (L - 3, 17.8), (L, 14.0), (L, 5.5), (L - 6, 4.8), (L - 6, 0)], seg=20, mat="suppressor")
    return b.to_object("P90_Suppressor")


def build_mount():
    """Sleeve clamped over the knurled ring and the flash hider, origin at the receiver's front face."""
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(0.5, 0), (0.5, 10.0), (1.5, 12.6), (14.0, 12.6), (15.0, 12.0), (19.0, 12.0),
                              (20.0, 12.6), (44.0, 12.6), (45.5, 11.4), (45.5, 6.0), (38.0, 5.6), (38.0, 0)],
            seg=16, mat="metal", phase=0.5)
    return b.to_object("P90_Muzzle_Mount_Device")


# ==================================================================================================
# Painting (numpy): base colours, grain, AO, edge highlights the way GoM's textures carry them, then the
# details of the photo by position (photo L, H) and facing.
# ==================================================================================================

BASE = {  # sRGB
    "polymer": (50, 50, 52), "grip": (47, 47, 49), "metal": (47, 48, 51), "rail": (52, 53, 56), "dark": (16, 16, 17),
    "smoke": (70, 52, 38), "magcap": (66, 58, 52), "brass": (150, 118, 62), "copper": (120, 66, 44),
    "suppressor": (46, 47, 50),
}

for ch, rows in {  # 3x5 glyphs build_mp7 lacks
        "N": ["101", "111", "111", "111", "101"], "H": ["101", "101", "111", "101", "101"],
        "E": ["111", "100", "110", "100", "111"], "R": ["110", "101", "110", "101", "101"],
        "T": ["111", "010", "010", "010", "010"], "L": ["100", "100", "100", "100", "111"],
        "B": ["110", "101", "110", "101", "110"], "G": ["111", "100", "101", "101", "111"],
        "I": ["111", "010", "010", "010", "111"], "U": ["101", "101", "101", "101", "111"],
        "5": ["111", "100", "111", "001", "111"], "8": ["111", "101", "111", "101", "111"],
        "9": ["111", "101", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    """Inside of a rounded rectangle in photo coordinates."""
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def common(maps, col, mat):
    """Grain, light, AO and edge highlights for every texel: the MP7's recipe made flatter and lighter, with
    brighter edges, the way GoM's textures look (median ~40, edges ~75 sRGB)."""
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "rail", "brass", "copper", "suppressor")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.99 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    # GoM's textures are flat panels with little occlusion: keep the AO light
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 78.0, 62.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def screw(col, L, H, sel, cL, cH, r=2.6, cross=False):
    d = np.hypot(L - cL, H - cH)
    ring = sel & (d < r) & (d > r - 0.9)
    head = sel & (d <= r - 0.9)
    col[ring] *= 0.4
    col[head] += 10
    ang = np.arctan2(H - cH, L - cL)
    if cross:
        slot = head & ((np.abs(L - cL) < 0.45) | (np.abs(H - cH) < 0.45))
    else:  # hex socket
        hexr = (r - 1.6) / np.maximum(np.cos(np.mod(ang, math.pi / 3) - math.pi / 6), 0.5)
        slot = head & (d < hexr)
    col[slot] = col[slot] * 0.25 + 4


SCREWS = [(49.0, 72.5), (96.0, 72.5), (210.6, 72.5), (309.0, 72.5), (145.3, 18.4), (239.8, 26.9), (290.0, 20.3),
          (374.5, 43.7), (447.0, 35.8), (419.3, 117.3), (480.0, 110.8)]


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0                       # back to the photo's coordinates
    if kind == "mag":                           # the magazine's mesh is local to its own origin
        L, H = MAG_L - y, z + MAG_H
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    if kind == "gun":
        polymer = mat == MATS.index("polymer")
        metal = mat == MATS.index("metal")
        # Butt seam halfway up, the rubber butt plate behind its seam, the sling slot at the bottom rear.
        butt = polymer & (L > 369) & (np.abs(x) > W_BUTT - 4.6)
        col[butt & side & (np.abs(H - 93.0) < 0.55)] *= 0.45
        col[polymer & (L > 489.0)] *= 0.86
        col[polymer & (np.abs(L - 489.0) < 0.5)] *= 0.4
        slot = side & (L > 450) & (L < 474) & (H > 27.8) & (H < 31.2)
        col[slot] = 9
        # FN monogram panel on both sides: raised border, oval ring, a scribble of the monogram.
        panel = side & (np.abs(x) > W_FRAME - 0.5) & rounded_rect(L, H, 320.0, 359.0, 36.0, 74.0, 4.0)
        inner = rounded_rect(L, H, 321.5, 357.5, 37.5, 72.5, 3.0)
        col[panel & ~inner] += 14
        ov = np.hypot((L - 339.5) / 14.0, (H - 57.0) / 9.5)
        col[panel & (np.abs(ov - 1.0) < 0.07)] += 18
        mono = panel & (ov < 0.85) & (kit.vnoise(p, 1.1, 9) > 0.6)
        col[mono] += 16
        lic = panel & (np.abs(H - 41.0) < 1.2) & (L > 324) & (L < 355) & (np.mod(L, 2.2) < 1.3)
        col[lic] += 10
        # "FN HERSTAL BELGIUM" raised panel on the right side of the receiver band.
        fnp = right & (L > 226) & (L < 304) & (H > 98.5) & (H < 109) & (np.abs(x) > W_BAND - 0.6)
        fni = rounded_rect(L, H, 227.5, 302.5, 100.0, 107.5, 1.5)
        col[fnp & ~fni] += 13
        txt = kit.text_mask(L, H, "FN HERSTAL BELGIUM", 229.0, 101.0, 5.0)   # right side: reads toward +L
        col[fnp & fni & txt] += 22
        # Metal upper: recessed window at the front, oval recess and its notch on the rail block, the side
        # tracks of the charging handles, the moulding line under the rail.
        up = metal & side
        win = up & rounded_rect(L, H, 45.0, 74.0, 121.5, 140.5, 2.0)
        col[win & ~rounded_rect(L, H, 46.5, 72.5, 123.0, 139.0, 1.5)] += 12
        col[win & rounded_rect(L, H, 46.5, 72.5, 123.0, 139.0, 1.5)] *= 0.45
        stad = up & rounded_rect(L, H, 99.0, 145.0, 160.0, 171.0, 5.5)
        col[stad & ~rounded_rect(L, H, 100.5, 143.5, 161.5, 169.5, 4.0)] *= 0.4
        col[up & (np.hypot(L - 140.0, H - 156.0) < 2.4)] *= 0.35
        track = up & (L > 88) & (L < 205) & (H > 105.5) & (H < 110.5)
        col[track] = col[track] * 0.3 + 3
        col[up & (np.abs(H - 93.6) < 0.5)] *= 0.5
        # Screws: frame and butt (both sides), the boss's hex screw, the cross-head screw ahead of the handle.
        sides_far = side & (np.abs(x) > W_FRAME - 0.6)
        for cL, cH in SCREWS:
            screw(col, L, H, sides_far, cL, cH)
        screw(col, L, H, side & (np.abs(x) > BOSS_X - 0.4), BOSS_L - 2.0, BOSS_H, r=3.0)
        screw(col, L, H, up, 85.0, 99.0, r=2.2, cross=True)
        # Underside: ejection port behind the grip, a seam along the belly.
        under = n[..., 2] < -0.7
        port = under & (L > 262) & (L < 296) & (np.abs(x) < 8.0)
        col[port] = col[port] * 0.2 + 3
        # Trigger ribs, flash hider ports, knurled ring, the bore.
        trig = mat == MATS.index("dark")
        col[trig & (np.mod(L, 2.0) < 0.8)] += 9
        r = np.hypot(x, z - BORE_Z)
        ring = metal & (L > 28.8) & (L < 38.2) & (r > 11.2)
        a = np.arctan2(x, z - BORE_Z)
        col[ring] *= (0.6 + 0.6 * ((np.mod(L[ring], 1.4) < 0.7) ^ (np.mod(a[ring] * 8.0 / math.pi, 1.0) < 0.5)))[..., None]
        hider = metal & (L < 28.5) & (r > 9.8)
        for cL in (8.0, 17.0):
            for ca in (math.radians(55), math.radians(-55)):
                arc = (np.mod(a - ca + math.pi, 2 * math.pi) - math.pi) * 10.4
                col[hider & (np.hypot(L - cL, arc) < 2.6)] = 8
        col[metal & (r < 5.4) & (L < 12.5)] = 7
    elif kind == "bolt":
        hole_in = side & (np.hypot(L - 77.5, H - 103.5) < 5.0)
        col[hole_in] *= 0.8
    elif kind == "mag":
        smoke = mat == MATS.index("smoke")
        cap = mat == MATS.index("magcap")
        # Rounds lie across the magazine in two rows: bullet tips seen on the right, case heads on the left, the
        # bodies through the top. Smoky plastic: colours pulled to the body colour, edges lighter.
        rows = (124.5, 135.5)
        pitch = 9.6
        on = smoke & (L > 91) & (L < 319)
        for k, hr in enumerate(rows):
            lc = np.round((L - 91.0 - k * pitch / 2) / pitch) * pitch + 91.0 + k * pitch / 2
            d = np.hypot(L - lc, H - hr)
            tip = on & right & (d < 2.6)
            col[tip] = col[tip] * 0.45 + np.array([118, 52, 34]) * 0.55
            head = on & left & (d < 4.0)
            col[head] = col[head] * 0.45 + np.array([150, 112, 58]) * 0.55
            col[on & left & (d < 1.3)] *= 0.7
        top = on & (n[..., 2] > 0.7)
        band = np.mod(L - 91.0, pitch) < 7.0
        col[top & band] = col[top & band] * 0.55 + np.array([140, 104, 56]) * 0.45
        col[top & band & (np.abs(x) > 14.0)] = col[top & band & (np.abs(x) > 14.0)] * 0.6 + np.array([110, 56, 38]) * 0.4
        col[smoke & ((np.abs(H - 119.6) < 0.7) | (np.abs(H - 140.4) < 0.7))] += 18
        col[cap & side & (L > 81) & (L < 87) & (H > 122) & (H < 138)] *= 0.6
        col[cap & (L > 334) & (L < 346) & (n[..., 2] > 0.7) & (np.mod(L, 2.0) < 0.9)] *= 0.65
    elif kind == "suppressor":
        yy = y
        r = np.hypot(x, z)
        knurl = (yy > 6) & (yy < 28) & (r > 13.4)
        a = np.arctan2(x, z)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(yy[knurl], 2.0) < 1.0) ^ (np.mod(a[knurl] * 17.2 / math.pi, 1.0)
                                                                         < 0.5)))[..., None]
        col[(np.abs(yy - 38.5) < 0.7) | (np.abs(yy - 162.0) < 0.6)] *= 0.5
        ang = np.arctan2(x, -z)
        tx = kit.text_mask(yy, ang * 19.0, "5.7X28", 80.0, -3.0, 6.0)
        col[tx & (r > 18.5)] = col[tx & (r > 18.5)] * 0.3 + 120
        col[(r < 5.6) & (yy > 165)] = 8
    elif kind == "mount":
        yy = y
        r = np.hypot(x, z)
        ang = np.mod(np.arctan2(x, z) / (2 * math.pi) * 6.0, 1.0)
        slot = (yy > 24) & (yy < 40) & (r > 12.2) & (np.abs(ang - 0.5) < 0.14)
        col[slot] = 10
        flats = (yy > 2) & (yy < 13.5) & (r > 12.2) & (np.abs(np.mod(np.arctan2(x, z) / (2 * math.pi) * 2, 1) - .5) < .12)
        col[flats] += 20
        col[r < 6.1] = 9
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

def g(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4), round(y * K, 4), round(z * K, 4)]


# Held like a pistol: GoM's handgun-held guns (pistols, MP5K, TEC9, MAC10; SwingAnim = Handgun) are modelled upside
# down, turned 180 degrees about the barrel axis (game x -> -x, z -> -z) around the same rear-top-of-grip origin, and
# their attachment points with them; a part modelled upright gets rotate (-180, 0, -180) (= that turn), as on the
# MP5K's rail_up / scope. The P90 is built and baked upright and turned only at export (points() and main()).
TURN = [-180.0, 0.0, -180.0]


def turned(point, part=True):
    """An upright point in the handgun-held model: offset x, z negated, an upright part turned with the gun."""
    x, y, z = point["offset"]
    out = {"offset": [round(-x, 4) + 0.0, y, round(-z, 4) + 0.0]}
    if "rotate" in point:
        out["rotate"] = point["rotate"]
    elif part:
        out["rotate"] = list(TURN)
    return out


def points(bounds):
    rail_top = (RAIL_TOP_H - H0) * K
    optic_y = round((L0 - 140.0) * K, 4)              # optics over the grip, toward the rear of the rail
    side = BOSS_X * K
    by, bz = P(BOSS_L, BOSS_H)
    pts = {
        "muzzle": {"offset": g(0.0, BORE_H), "rotate": [-90.0, 0.0, -180.0]},     # as on the MP5K: unchanged
        "magazine": {"offset": g(MAG_L, MAG_H)},
        # same relations to the rail's top as on the MP7 (GoM's Picatinny_Rail_Up and the MP5's scope)
        "rail_up": {"offset": [0.0, optic_y, round(rail_top - 0.0055, 4)]},
        "scope": {"offset": [0.0, optic_y, round(rail_top - 0.0032, 4)]},
        "rail_left": {"offset": [round(side - 0.0055, 4), round(by * K, 4), round(bz * K, 4)]},
        "rail_right": {"offset": [round(-(side - 0.0055), 4), round(by * K, 4), round(bz * K, 4)]},
        "light_left": {"offset": [round(side - 0.0055 + 0.0062, 4), round(by * K, 4), round(bz * K, 4)]},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), round(by * K, 4), round(bz * K - 0.0008, 4)]},
        "canon": {"offset": g(CANON_L, BORE_H), "rotate": [0.0, 0.0, 0.0]},          # round parts: GoM leaves 0
        "bolt_fired": {"offset": [0.0, round(-CH_TRAVEL * K, 4), 0.0], "rotate": [0.0, 0.0, 0.0]},
    }
    pts = {k: turned(v) for k, v in pts.items()}
    # floor pose of GoM's handgun-held SMGs (MP5K, TEC9, MAC10)
    pts["world"] = {"offset": [-0.025, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}
    # Carried on the back like a rifle (never in a holster): the body's rifle points expect an upright rifle model,
    # and an attached item's own attachment of the same name is applied on top, so these turn the P90 back upright
    # (a half turn is its own inverse, so it does not matter whether the engine inverts it).
    for name in ("rifle_back", "rifle_back_bag"):
        pts[name] = {"offset": [0.0, 0.0, 0.0], "rotate": list(TURN)}
    pts["_notes"] = {
        "units": "game units (0.72 of real size); +Y muzzle; held like a pistol, so modelled upside down as GoM's "
                 "handgun-held guns are: +Z the gun's BOTTOM, +X its RIGHT; origin = rear-top of the grip column "
                 "(photo L %.0f, H %.0f)" % (L0, H0),
        "rifle_back": "rifle_back / rifle_back_bag (vanilla's Rifle On Back locations) turn the upside-down model "
                      "upright when it hangs in the back slot",
        "turned": "parts modelled upright (magazine, GoM optics / lights / lasers) get rotate -180 0 -180, as on "
                  "GoM's MP5K; render_p90.py / make_p90_art.py turn everything back for display",
        "magazine": "57x28Magazine50_P90's origin is its front end, centred, on its bottom face; the node lies along "
                    "-Y from there on top of the receiver",
        "canon": "receiver front face where the barrel collar starts; P90_Muzzle_Mount_Device and P90_Suppressor "
                 "have their origin there and extend along +Y over the flash hider",
        "rail_left/right": "the accessory bosses on the sides of the rail block",
        "bolt_fired": "charging handles pulled back 60 mm real (P90TR_BOLT is modelled forward); they do not "
                      "reciprocate when firing",
    }
    pts["_extras"] = {
        "ejection_port_upright": g(279.0, 1.0),
        "handgun_hold": True,
        "photo_origin_mm": [L0, H0],
        "real_mm_per_game_unit": round(1.0 / K, 2),
    }
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
    mag = build_magazine()
    supp, mount = build_suppressor(), build_mount()

    kit.unwrap([body, bolt], 0.006)
    for o in (mag, supp, mount):
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, bolt], [[body, bolt], [body, bolt]], ["gun", "bolt"], 256, os.path.join(TEX_DIR, "P90TR.png"))
    texture([mag], [[mag]], ["mag"], 128, os.path.join(TEX_DIR, "57x28Magazine50_P90.png"))
    texture([supp], [[supp]], ["suppressor"], 128, os.path.join(TEX_DIR, "P90_Suppressor.png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "P90_Muzzle_Mount_Device.png"))

    for o in (body, bolt):                              # held like a pistol: turned 180 degrees about the bore axis
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in (body, bolt, mag, supp, mount)}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")

    kit.export([body, bolt], FBX_GUN)
    kit.export([mag], FBX_MAGS)
    kit.export([supp, mount], FBX_PARTS)
    for name, b in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
