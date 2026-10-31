"""Glock 21 model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_glock21.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_GLOCK21.fbx          GLOCK21_BODY, GLOCK21_SLIDE
    M/models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx  45Magazine13_GLOCK21
    M/textures/weapons/GunsOfTien/GLOCK21.png                    256 atlas (frame + slide)
    M/textures/weapons/GunsOfTien/45Magazine13_GLOCK21.png       128
    scripts/glock21_points.json                                  attachment points (game space)

Glock's .45 ACP pistol of 1990 (user, 2026-10-30: the main mod, built before Post-93's KRISS Vector .45, which takes its
magazines), as the second-generation gun of 1993: no accessory rail on the dust cover and a straight front strap
without finger grooves, checkered front and back, pebbled sides. GoM's pistol parts fit it anyway (its sights on the
Beretta mount, its underbarrel lasers and lights, its .45 mount device and P45 suppressor), as on GoM's own Glock 17.

Built as Post-93's build_ucp.py / build_fiveseven.py build theirs, which is how GoM builds its pistols: body + slide
nodes, the slide drawn through MarzGuns.Slide_Lock / Slide_Fired, the magazine in the gun's own space (no `magazine`
point), modelled and baked upright and turned upside down at export, origin 11 mm behind the deepest point of the back
edge under the beavertail at its height, 0.603 of real size (every Guns of Tien gun).

Traced (post93/trace_outline.py) from Wikimedia Commons "Glock 21 Avriette.jpg" (Avriette, CC BY-SA 3.0, kept out of
the repo in references/glock21): the gun's right side, muzzle right, the loose magazine and an AA battery beside it,
scaled to Glock's 209 mm (the battery then reads 48.5 mm against 50.5, the height 134 against Glock's 139). That gun is
a third-generation one in a Hogue rubber grip sleeve: the profiles keep its slide, frame top and trigger guard, and draw
the second generation's plain dust cover where its rail is and its straight front strap and slimmer grip under the
sleeve. The loose magazine measures 118 mm from the feed lips to the base and 37 mm front to back. Profiles are in that
photo's (L, H) mm: L back from the muzzle, H up from the lowest point.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
import json
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_GLOCK21.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_GLOCK21_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "glock21_points.json")

K = 0.000603                       # game units per real mm: the M16A2's proportion (every Guns of Tien gun)
K_OLD = 0.00072                    # GoM's pistols: the `world` floor point is scaled from them
kit.K = K
MATS = ["polymer", "grip", "metal", "barrel", "dark", "magpoly", "brass", "copper"]
kit.MATS[:] = MATS
for ch, rows in {"U": ["101", "101", "101", "101", "111"], "T": ["111", "010", "010", "010", "010"],
                 "O": ["111", "101", "101", "101", "111"], "L": ["100", "100", "100", "100", "111"],
                 "C": ["111", "100", "100", "100", "111"], "K": ["101", "101", "110", "101", "101"],
                 "5": ["111", "100", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

# Origin: 11 mm behind the deepest point of the back edge under the beavertail (L 177.5, H 86), at its height
L0, H0 = 188.5, 86.0
BORE_H = 118.5
SLIDE_BOTTOM, SLIDE_TOP = 109.5, 131.0       # levelled (the photo's slide top falls 3 mm over its length)
SLIDE_TRAVEL = 34.0                          # GoM's Glock 17: 32 mm; the .45's longer round a little more
DUST_COVER_H = 93.5                          # the dust cover's flat underside (the Gen 2 has no rail there)
MAG_RAKE = 0.344                             # the front strap's lean (17.2 mm over 50)
MAG_TOP = 106.0

W_SLIDE, W_FRAME, W_GRIP, W_GUARD = 12.8, 12.6, 15.8, 5.5
W_MAG, W_BASE = 12.3, 13.4


def P(L, H):
    return L0 - L, H - H0


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    return kit.slab(b, [P(L, H) for L, H in outline], [[P(L, H) for L, H in h] for h in holes], half, bevel, res,
                    mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def both(fn):
    for s in (1, -1):
        fn(s)


# ==================================================================================================
# Profiles (traced; Gen 2 parts drawn over the Gen 3 photo's rail and grip sleeve)
# ==================================================================================================

SLIDE = [(0.4, SLIDE_BOTTOM), (0.0, 113.0), (0.0, 124.5), (0.6, 127.5), (2.2, 130.2), (3.6, SLIDE_TOP),
         (190.0, SLIDE_TOP), (191.6, 130.2), (192.4, 128.0), (192.5, 112.0), (192.0, SLIDE_BOTTOM)]
FRONT_SIGHT = [(8.5, 130.5), (8.5, 133.6), (9.5, 134.6), (13.0, 134.6), (14.2, 133.4), (14.2, 130.5)]
REAR_SIGHT = [(176.0, 130.5), (176.5, 133.8), (177.5, 134.8), (186.5, 134.8), (187.0, 133.6), (187.0, 130.5)]

# Frame: the dust cover's rounded front, its flat underside back to the trigger guard, the frame over the grip to the
# beavertail (the grip and the guard are their own slabs).
FRAME = [(1.6, SLIDE_BOTTOM), (1.3, 105.0), (2.1, 103.5), (2.6, 99.8), (3.9, 96.7), (6.9, 95.1), (13.7, DUST_COVER_H),
         (67.8, 92.6), (70.5, 91.0), (178.5, 91.0), (179.3, 90.8), (181.9, 93.4), (183.5, 94.3), (191.9, 96.4),
         (192.7, 97.1), (193.5, 99.5), (193.0, 102.6), (191.6, 105.0), (191.4, SLIDE_BOTTOM)]

# Squared trigger guard with its hooked front, the opening (behind the trigger it reaches the front strap).
GUARD = [(68.0, 92.0), (70.3, 88.2), (70.9, 86.9), (70.4, 76.1), (69.5, 72.0), (68.0, 68.3), (68.0, 65.9), (69.8, 63.8),
         (71.2, 63.2), (106.1, 60.7), (111.6, 61.5), (117.6, 64.1), (119.7, 64.1), (121.6, 63.3), (124.0, 62.0),
         (124.0, 92.0)]
OPENING = [(86.2, 89.5), (83.5, 88.8), (81.2, 87.5), (79.9, 86.2), (78.5, 83.7), (78.0, 81.9), (77.9, 76.9),
           (78.7, 74.3), (79.8, 72.5), (81.4, 71.2), (83.8, 70.3), (103.5, 69.1), (110.0, 68.9), (113.5, 69.6),
           (116.0, 71.5), (117.2, 74.5), (117.4, 80.0), (116.8, 85.5), (115.5, 89.5)]
TRIGGER = [(104.0, 90.0), (107.5, 90.0), (109.5, 86.0), (111.5, 80.0), (112.5, 74.5), (112.0, 71.5), (109.8, 70.6),
           (108.2, 71.2), (109.6, 73.0), (109.4, 77.5), (107.6, 82.5), (105.5, 86.5)]

# The Gen 2 grip: a straight front strap down from the guard (the photo's Hogue sleeve has finger grooves), its back
# edge 1.5 mm inside the sleeve's, the frame ending 6 mm above the magazine's base plate.
GRIP = [(117.5, 92.0), (117.5, 88.0), (118.0, 80.0), (118.5, 72.0), (119.7, 64.1), (121.6, 63.3), (122.8, 61.0),
        (123.6, 57.0), (125.6, 50.0), (128.2, 43.0), (131.0, 35.5), (134.2, 27.0), (137.4, 18.5), (139.8, 11.5),
        (140.8, 7.0), (142.5, 6.2), (204.6, 6.2), (205.4, 10.0), (205.0, 16.0), (203.6, 22.0), (201.2, 28.5),
        (198.0, 35.0), (194.0, 42.5), (189.6, 50.5), (185.6, 58.0), (182.6, 65.5), (180.2, 72.5), (178.6, 79.0),
        (177.6, 84.0), (177.5, 87.2), (178.5, 91.0), (178.5, 92.0)]

# Controls: the slide stop lever (left), the takedown lever's tabs (both sides), the magazine catch (left).
SLIDE_STOP = [(96.0, 103.2), (124.0, 103.6), (126.0, 105.5), (125.0, 107.6), (96.0, 107.6)]
TAKEDOWN = [(85.0, 99.5), (88.8, 99.5), (88.8, 107.5), (85.0, 107.5)]
MAG_CATCH = (120.0, 126.0, 73.0, 80.0)

MAG_BODY = [(148.0, 6.5), (186.0, 6.5), (186.0 - MAG_RAKE * (MAG_TOP - 6.5), MAG_TOP),
            (148.0 - MAG_RAKE * (MAG_TOP - 6.5), MAG_TOP)]
BASE_PLATE = [(146.0, 6.5), (143.6, 3.5), (144.8, 1.4), (148.0, 0.4), (188.0, 0.0), (191.0, 1.0), (192.4, 3.5),
              (191.0, 6.5)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, FRAME, half=W_FRAME, bevel=1.8, res=1)
    slab(b, GUARD, [OPENING], half=W_GUARD, bevel=1.6, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=3.5, res=2, mat="grip")
    slab(b, TRIGGER, half=3.0, bevel=0.8, mat="dark")
    slab(b, SLIDE_STOP, half=0.6, bevel=0.3, mat="dark", x0=W_FRAME + 0.3)
    both(lambda s: slab(b, TAKEDOWN, half=0.6, bevel=0.3, mat="dark", x0=s * (W_FRAME + 0.3)))
    La, Lb, Ha, Hb = MAG_CATCH
    box(b, La, Lb, Ha, Hb, W_GRIP - 2.0, W_GRIP + 1.2, mat="polymer", bevel=0.8)
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(SLIDE_TRAVEL + 12.0), 0), (t(SLIDE_TRAVEL + 12.0), 7.3),
                                       (t(0.4), 7.3), (t(0.0), 6.7), (t(0.0), 5.8), (t(10.0), 5.8),
                                       (t(10.0), 0)], seg=16, mat="barrel", phase=0.5)
    return b.to_object("GLOCK21_BODY")


def build_slide():
    b = kit.Builder()
    slab(b, SLIDE, half=W_SLIDE, bevel=1.4, res=1, mat="metal")
    slab(b, FRONT_SIGHT, half=1.8, bevel=0.4, mat="dark")
    slab(b, REAR_SIGHT, half=7.0, bevel=0.8, mat="dark")
    return b.to_object("GLOCK21_SLIDE")


def build_magazine():
    b = kit.Builder()
    slab(b, MAG_BODY, half=W_MAG, bevel=1.4, mat="magpoly")
    slab(b, BASE_PLATE, half=W_BASE, bevel=1.6, res=1, mat="magpoly")
    front, rear = MAG_BODY[3][0], MAG_BODY[2][0]
    fl = [(front + 1.0, MAG_TOP - 0.2), (rear - 1.0, MAG_TOP - 0.2), (rear - 2.0, MAG_TOP + 2.0),
          (front + 6.0, MAG_TOP + 2.0)]
    both(lambda s: slab(b, fl, half=1.4, bevel=0.3, mat="metal", x0=s * (W_MAG - 1.4)))
    rL = front + 2.5                                     # the top round: a .45 ACP ball round, round nose forward
    b.lathe("y", (0, 0, MAG_TOP + 3.0 - H0), [(L0 - (rL + 32.4), 0), (L0 - (rL + 32.4), 6.0),
                                              (L0 - (rL + 9.5), 6.0), (L0 - (rL + 9.5), 5.7),
                                              (L0 - (rL + 5.0), 5.3), (L0 - (rL + 1.5), 3.4), (L0 - rL, 0.6),
                                              (L0 - rL, 0)], seg=12, mat="brass", phase=0.5)
    return b.to_object("45Magazine13_GLOCK21")


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: Glock's black polymer, the Tenifer slide's matte grey-black, a grey barrel, steel-lined magazines
    "polymer": (38, 38, 40), "grip": (37, 37, 39), "metal": (50, 51, 54), "barrel": (70, 70, 72), "dark": (24, 24, 25),
    "magpoly": (34, 34, 36), "brass": (150, 118, 62), "copper": (124, 70, 46),
}


def in_poly(L, H, pts):
    inside = np.zeros(L.shape, bool)
    for i in range(len(pts)):
        (la, ha), (lb, hb) = pts[i], pts[(i + 1) % len(pts)]
        if ha == hb:
            continue
        inside ^= ((ha > H) != (hb > H)) & (L < la + (H - ha) * (lb - la) / (hb - ha))
    return inside


def pin(col, L, H, sel, cL, cH, r=1.8):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.7)] *= 0.4
    col[sel & (d <= r - 0.7)] += 12


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "barrel", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.99 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 70.0, 50.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None]
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


# the pebbled panel on each side of the grip (the Gen 2's texture; the Gen 3's finger grooves and thumb rests absent)
GRIP_PANEL = [(124.0, 66.0), (176.0, 66.0), (179.0, 58.0), (198.0, 20.0), (200.0, 10.0), (143.0, 10.0)]
FRAME_PINS = [(103.5, 99.7), (105.0, 107.0)]


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x = p[..., 0]
    L, H = L0 - p[..., 1], p[..., 2] + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7      # upright game space: +X the gun's left
    up, fwd, back = n[..., 2] > 0.7, n[..., 1] > 0.5, n[..., 1] < -0.5
    if kind == "gun":
        grip = mat == MATS.index("grip")
        sides = grip & side & (np.abs(x) > W_GRIP - 0.6)
        pebble = sides & in_poly(L, H, GRIP_PANEL)
        grains = pebble & (kit.vnoise(p, 0.5, 21) > 0.52)
        col[grains] += 16
        col[pebble & ~grains] *= 0.82
        # checkering on the front and back straps
        strap = grip & (fwd | back) & ~side & (H > 10.0) & (H < 88.0)
        chk = (np.mod(H + 0.35 * x, 1.8) < 0.6) | (np.mod(H - 0.35 * x, 1.8) < 0.6)
        col[strap & chk] *= 0.6
        frame = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_FRAME - 0.6)
        for cL, cH in FRAME_PINS:
            pin(col, L, H, frame, cL, cH)
        # the right side's import marking, reading toward the muzzle
        col[frame & right & kit.text_mask(-L, H, "MADE IN AUSTRIA", -158.0, 100.6, 2.2)] += 18
        col[frame & right & kit.text_mask(-L, H, "GLOCK INC SMYRNA GA", -158.0, 97.4, 2.2)] += 18
        col[frame & left & kit.text_mask(L, H, "GLOCK", 140.0, 98.4, 3.2)] += 14      # the Gen 2's moulded logo
        col[(mat == MATS.index("dark")) & (np.mod(H, 1.2) < 0.4) & side & (L < 90)] += 10  # takedown tab ribs
        trig = (mat == MATS.index("dark")) & fwd & (L > 102) & (L < 114)
        col[trig & (np.abs(x) < 0.6)] = 52                                           # the trigger safety's blade
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("barrel")) & (r < 5.9) & (L < 1.0)] = 8               # the bore
    elif kind == "slide":
        sl = (mat == MATS.index("metal")) & side
        # rear serrations (both sides): six vertical grooves between L 148 and 179
        g = np.mod(L - 148.5, 5.2)
        ser = sl & (L > 148.0) & (L < 179.5) & (H > 111.0) & (H < 129.6)
        col[ser & (g < 1.6)] *= 0.35
        col[ser & (g > 1.6) & (g < 2.2)] += 22
        col[sl & left & kit.text_mask(L, H, "21", 22.0, 114.5, 5.0)] += 24
        col[sl & left & kit.text_mask(L, H, "AUSTRIA", 33.0, 115.6, 3.0)] += 24
        col[sl & left & kit.text_mask(L, H, ".45 AUTO", 66.0, 115.6, 3.0)] += 24
        # the ejection port on the right and up over the top, the barrel hood in it, the extractor below it
        port = sl & right & (L > 110.3) & (L < 128.5) & (H > 121.0)
        hood = port & (L > 111.5) & (L < 127.5) & (H > 122.2)
        col[port & ~hood] = 8
        col[hood] = col[hood] * 0.6 + np.array([66, 66, 68]) * 0.4
        top_port = (mat == MATS.index("metal")) & up & (L > 110.3) & (L < 128.5) & (x < -1.5)
        col[top_port] = col[top_port] * 0.3 + 6
        col[sl & right & (L > 104.0) & (L < 110.0) & (np.abs(H - 120.0) < 1.2)] *= 0.5   # extractor
        dark = mat == MATS.index("dark")                  # Glock's sights: a white dot front, a white U at the rear
        col[dark & back & (L < 20) & (np.hypot(x, H - 133.2) < 0.9)] = (225, 225, 215)
        col[dark & back & (L > 175) & (np.abs(x) < 1.6) & (H > 132.6)] = 6
        u = dark & back & (L > 175) & (np.abs(np.abs(x) - 2.6) < 0.6) & (H > 131.6) & (H < 134.0)
        col[u] = (225, 225, 215)
        col[dark & back & (L > 175) & (np.abs(x) < 3.2) & (np.abs(H - 131.6) < 0.5)] = (225, 225, 215)
        col[dark & up & (L > 175) & (np.abs(x) < 1.6)] = 6
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("metal")) & fwd & (L < 1.0) & (r < 7.6)] = 8         # the slide's hole round the barrel
    elif kind == "mag":
        mp = mat == MATS.index("magpoly")
        back_face = mp & back & (H > 20.0) & (H < MAG_TOP - 6.0)
        # the witness holes down the back, numbered (every 4th round, the last at 13)
        for k, rnd in enumerate((5, 9, 13)):
            hh = MAG_TOP - 14.0 - k * 22.0
            ll = MAG_BODY[2][0] + MAG_RAKE * (MAG_TOP - hh)
            col[back_face & (np.hypot(x, H - hh) < 1.5) & (np.abs(L - ll) < 3.0)] = 12
        br = mat == MATS.index("brass")
        rL = MAG_BODY[3][0] + 2.5
        col[br & (L < rL + 9.5)] = BASE["copper"]
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
# Attachment points (GoM's pistol set, at the relations GoM's Glock 17 and our Five-seveN / UCP use)
# ==================================================================================================

def g(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4), round(y * K, 4), round(z * K, 4)]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    pts = {
        "muzzle": {"offset": g(0.0, BORE_H), "rotate": [-90.0, 0.0, -180.0]},
        "rail_up": {"offset": g(61.0, SLIDE_TOP - 11.4), "rotate": ZERO},
        "scope": {"offset": g(74.0, SLIDE_TOP + 12.6), "rotate": ZERO},
        "underbarrel": {"offset": g(34.0, DUST_COVER_H), "rotate": ZERO},
        "canon": {"offset": g(0.0, BORE_H), "rotate": ZERO},
        "slide_fired": {"offset": [0.0, round(-SLIDE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["world"] = {"offset": [round(-0.009 * K / K_OLD, 4), round(0.062 * K / K_OLD, 4), 0.0], "rotate": ZERO}
    pts["_notes"] = {
        "units": "game units (0.603 of real size, the M16A2's proportion); +Y muzzle; modelled upside down as GoM's "
                 "pistols are: +Z the gun's BOTTOM, +X its RIGHT; origin = the web of the grip under the beavertail "
                 "(photo L %.1f, H %.0f)" % (L0, H0),
        "magazine": "no magazine point: 45Magazine13_GLOCK21 is modelled in the gun's space and drawn at its origin",
        "underbarrel": "GoM's underbarrel lights and lasers on the dust cover's flat underside (the Gen 2 has no rail; "
                       "GoM's parts fit it anyway, as on GoM's Glock 17)",
        "canon": "the barrel's crown: GoM's .45 mount device (drawn with its MarzGuns.Muzzle_Mount_Device model) and "
                 "P45 suppressor, extending along +Y, as on GoM's USP",
        "slide_fired": "GLOCK21_SLIDE back %.0f mm real" % SLIDE_TRAVEL,
    }
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "real_mm_per_game_unit": round(1.0 / K, 2)}
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

    body, slide = build_body(), build_slide()
    mag = build_magazine()
    kit.unwrap([body, slide], 0.006)
    kit.unwrap([mag], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, slide], [[body, slide], [body, slide]], ["gun", "slide"], 256, os.path.join(TEX_DIR, "GLOCK21.png"))
    texture([mag], [[mag]], ["mag"], 128, os.path.join(TEX_DIR, "45Magazine13_GLOCK21.png"))

    for o in (body, slide, mag):                           # upside down, as GoM's pistols
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in (body, slide, mag)}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")

    kit.export([body, slide], FBX_GUN)
    kit.export([mag], FBX_MAGS)
    for name, b in bounds.items():
        print("%-24s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
