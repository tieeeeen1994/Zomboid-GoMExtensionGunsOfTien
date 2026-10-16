"""H&K UCP prototype models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_ucp.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_UCP.fbx         UCP_BODY, UCP_SLIDE
    P/models_X/weapons/magazines/GunsOfTienPost93_UCP_magazines.fbx  46x30Magazine20_UCP, 46x30Magazine40_UCP (drum)
    P/models_X/weapons/parts/GunsOfTienPost93_UCP_parts.fbx      UCP_Muzzle_Mount_Device (a model only)
    P/textures/weapons/GunsOfTienPost93/<name>.png               UCP (256, body + slide), 128 for each magazine and
                                                                  the mount
    scripts/post93/ucp_points.json                               attachment points (game space)

The UCP ("Universal" or "Ultimate Combat Pistol", P46) was H&K's 4.6x30mm companion pistol to the MP7: prototypes from
about 2004, cancelled in July 2009, never sold; in game the item "UCP Prototype" (user, 2026-10-17). Built exactly as
build_fiveseven.py builds the Five-seveN, which is built the way GoM builds its pistols: body + slide nodes, the
slide drawn through MarzGuns.Slide_Lock / Slide_Fired, the magazine in the gun's own space (no `magazine` point),
modelled and baked upright and turned upside down at export, origin in the web of the grip under the beavertail,
0.72 of real size. It takes the MP7's Rotex-II suppressor on the MP7's mount device (user: "use the MP7 suppressor as
well"), drawn on this gun as a threaded-barrel adapter of its own, as the Five-seveN does with the 5.7x28mm mount.

The shape is traced from a side photo of the about-2004 prototype (left side, muzzle left; guns.fandom.com
File:HKUCP2004Proto.jpg, 550 px, unclear rights: a reference only, not shipped) by trace_outline.py into
ucp_reference_outline.json, scaled to the 200 mm published for it (barrel 130 mm, 850 g, 20 rounds). Profiles are in
that photo's (L, H) mm: L back from the muzzle, H up from the lowest point. The photo shows only the left side: the
right side gets the ejection port and the ambidextrous controls mirrored.
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
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402

MEDIA = kit.MEDIA
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_UCP.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_UCP_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_UCP_parts.fbx")
TEX_DIR = kit.TEX_DIR
POINTS_JSON = os.path.join(HERE, "ucp_points.json")

K = kit.K
MATS = ["polymer", "grip", "metal", "rail", "dark", "control", "magpoly", "brass", "copper", "suppressor"]
kit.MATS[:] = MATS

# Origin: 11 mm behind the deepest point of the back edge under the beavertail (L 177.2, H 74.8), at its height, as on
# the Five-seveN (bore 40.5 mm above, the slide's bottom 28 mm above; GoM's Glock 17: 47 / 27.6).
L0, H0 = 188.0, 75.0
BORE_H = 115.5
CANON_L = 0.6
SLIDE_BOTTOM, SLIDE_TOP = 103.0, 125.6
SLIDE_TRAVEL = 30.0
RAIL_TEETH_H = 92.2
MAG_RAKE = 0.30                    # the grip's front and back edges lean 16-18 degrees
MAG_TOP = 90.0
# The 40-round magazine is a small drum (user, 2026-10-17; the prototype is only known with its 20-round), built like
# the MP7's 60-round drum: a feed tower like the 20-round body down out of the grip into a drum facing front and back
# (its axis along the barrel), its top just under the grip; smaller than the MP7's (92 mm across): 68 mm across, 50 mm
# front to back so the 45 mm deep feed tower fits inside it.
DRUM_R = 34.0
DRUM_HALF = 25.0
DRUM_L = 175.0                     # its centre: on the magazine's axis where it leaves the grip
DRUM_H = 6.0 - 1.5 - DRUM_R        # top 1.5 mm under the grip's bottom (H ~6)

W_SLIDE, W_FRAME, W_GRIP, W_GUARD = 12.2, 13.0, 14.5, 6.0
W_MAG, W_BASE = 9.0, 12.5


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
# Profiles (traced; ucp_reference_outline.json)
# ==================================================================================================

SLIDE = [(0.6, SLIDE_BOTTOM), (0.6, 118.5), (1.1, 123.0), (2.7, 125.0), (4.6, SLIDE_TOP), (186.0, SLIDE_TOP),
         (188.0, 124.9), (190.1, 121.8), (191.3, 118.0), (194.7, 105.1), (195.2, SLIDE_BOTTOM)]
FRONT_SIGHT = [(8.0, 125.0), (8.0, 129.4), (11.0, 130.2), (15.9, 129.4), (17.3, 125.0)]
REAR_SIGHT = [(175.0, 125.0), (176.0, 126.0), (178.4, 128.7), (184.4, 128.7), (185.2, 127.9), (185.6, 125.0)]

# Frame: the rounded front of the dust cover, the rail under it, down to the trigger opening's top, back over the grip
# to the beavertail.
FRAME = [(1.1, SLIDE_BOTTOM), (1.1, 102.0), (3.4, 99.8), (4.9, 96.0), (7.6, 93.4), (12.1, 92.2), (12.1, 94.6),
         (56.5, 94.6), (56.5, 92.2), (72.9, 91.8), (74.8, 91.1), (77.5, 89.0), (80.0, 91.5), (186.0, 91.5),
         (186.0, 85.4), (188.6, 85.4), (192.8, 86.5), (197.0, 90.3), (197.7, 92.2), (197.7, 97.2), (196.2, 103.2),
         (195.2, SLIDE_BOTTOM)]
RAIL_TEETH = [(12.1, 15.6), (19.7, 23.5), (28.5, 32.6), (38.0, 41.7), (47.4, 51.2), (55.9, 56.5)]

# Squared trigger guard with a flat front, the opening (behind the trigger it reaches the grip's front strap).
GUARD = [(72.0, 92.0), (74.8, 91.1), (77.8, 88.0), (79.3, 85.0), (79.3, 76.7), (78.6, 75.1), (78.6, 72.9),
         (77.8, 72.1), (77.8, 69.4), (79.3, 67.6), (88.0, 66.0), (96.8, 65.3), (103.2, 64.9), (114.6, 65.3),
         (118.4, 66.0), (121.8, 67.6), (126.0, 66.8), (129.8, 65.7), (131.0, 67.0), (131.0, 92.0)]
OPENING = [(86.9, 91.5), (84.6, 89.9), (83.5, 86.9), (83.5, 75.5), (84.3, 72.5), (85.8, 71.0), (95.3, 70.6),
           (110.0, 70.8), (118.0, 71.2), (122.5, 72.5), (124.2, 75.0), (123.0, 82.0), (120.5, 88.5), (118.5, 91.5)]
TRIGGER = [(108.5, 91.5), (111.5, 91.5), (113.5, 86.0), (117.0, 80.0), (117.5, 75.5), (115.0, 72.0), (110.0, 70.5),
           (107.0, 71.0), (108.5, 72.5), (112.5, 74.5), (114.0, 77.5), (112.5, 82.0), (109.5, 87.0)]

GRIP = [(118.5, 92.0), (120.5, 88.5), (123.0, 82.0), (124.2, 75.0), (125.5, 70.0), (129.0, 66.0), (131.3, 64.1),
        (132.8, 60.7), (133.6, 58.1), (134.7, 48.6), (135.5, 44.8), (137.4, 39.5), (140.0, 30.7), (143.1, 25.0),
        (144.6, 21.3), (145.4, 19.4), (146.0, 13.0), (146.4, 7.4), (198.6, 5.5), (198.1, 17.5), (195.8, 26.9),
        (194.7, 28.5), (193.9, 31.5), (192.8, 36.1), (190.9, 43.3), (189.4, 47.8), (186.0, 55.0), (184.4, 58.8),
        (181.8, 64.1), (179.9, 67.9), (178.4, 71.0), (177.2, 74.8), (177.6, 78.6), (178.4, 80.1), (181.8, 83.9),
        (186.0, 85.4), (186.0, 92.0)]

# Controls on the frame (left side in the photo; mirrored on the right, H&K's ambidextrous layout): the slide release
# paddle with its pivot, the long slide stop, the rear lever (safety / decocker), the paddle magazine release at the
# rear of the trigger guard.
SLIDE_RELEASE = [(59.5, 97.0), (61.0, 100.5), (66.0, 103.6), (73.5, 103.0), (75.5, 99.5), (72.5, 96.0), (66.0, 96.5)]
SLIDE_STOP = [(98.0, 95.5), (152.0, 95.0), (153.5, 96.5), (153.0, 100.5), (98.0, 101.0)]
REAR_LEVER = [(159.5, 97.0), (162.0, 101.0), (184.0, 101.4), (189.5, 99.5), (189.5, 95.0), (186.0, 93.0),
              (176.0, 95.0)]
MAG_RELEASE = [(124.0, 66.5), (126.5, 72.5), (130.5, 72.0), (131.5, 66.0)]

MAG_BODY = [(149.0, 7.5), (194.0, 5.8), (194.0 - MAG_RAKE * (MAG_TOP - 5.8), MAG_TOP),
            (149.0 - MAG_RAKE * (MAG_TOP - 7.5), MAG_TOP)]
BASE_PLATE = [(147.0, 7.4), (144.6, 3.4), (145.7, 2.3), (148.4, 1.1), (153.7, 0.4), (167.7, 0.8), (182.9, 0.0),
              (192.4, 0.4), (196.6, 0.8), (199.6, 3.0), (200.0, 4.6), (198.8, 5.8)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, FRAME, half=W_FRAME, bevel=1.8, res=1)
    for La, Lb in RAIL_TEETH:
        box(b, La, Lb, RAIL_TEETH_H, 94.9, -10.6, 10.6, mat="rail", bevel=0.4)
    slab(b, GUARD, [OPENING], half=W_GUARD, bevel=1.6, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=3.5, res=2, mat="grip")
    slab(b, TRIGGER, half=2.8, bevel=0.8, mat="dark")
    both(lambda s: slab(b, SLIDE_RELEASE, half=0.7, bevel=0.3, mat="control", x0=s * (W_FRAME + 0.4)))
    both(lambda s: slab(b, SLIDE_STOP, half=0.6, bevel=0.3, mat="dark", x0=s * (W_FRAME + 0.3)))
    both(lambda s: slab(b, REAR_LEVER, half=0.7, bevel=0.3, mat="dark", x0=s * (W_FRAME + 0.4)))
    slab(b, MAG_RELEASE, half=W_GUARD + 1.5, bevel=0.6, mat="dark")
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(SLIDE_TRAVEL + 12.0), 0), (t(SLIDE_TRAVEL + 12.0), 5.6),
                                       (t(CANON_L + 0.4), 5.6), (t(CANON_L), 5.0), (t(CANON_L), 2.6), (t(10.0), 2.6),
                                       (t(10.0), 0)], seg=14, mat="metal", phase=0.5)
    return b.to_object("UCP_BODY")


def build_slide():
    b = kit.Builder()
    slab(b, SLIDE, half=W_SLIDE, bevel=1.6, res=1, mat="metal")
    slab(b, FRONT_SIGHT, half=1.6, bevel=0.4, mat="dark")
    slab(b, REAR_SIGHT, half=7.0, bevel=0.8, mat="dark")
    return b.to_object("UCP_SLIDE")


def build_magazine():
    b = kit.Builder()
    slab(b, MAG_BODY, half=W_MAG, bevel=1.0, mat="magpoly")
    slab(b, BASE_PLATE, half=W_BASE, bevel=1.6, res=1, mat="polymer")
    feed_lips_and_round(b)
    return b.to_object("46x30Magazine20_UCP")


def feed_lips_and_round(b):
    front, rear = MAG_BODY[3][0], MAG_BODY[2][0]
    fl = [(front + 1.0, MAG_TOP - 0.2), (rear - 1.0, MAG_TOP - 0.2), (rear - 2.0, MAG_TOP + 2.0),
          (front + 6.0, MAG_TOP + 2.0)]
    both(lambda s: slab(b, fl, half=1.1, bevel=0.3, mat="magpoly", x0=s * (W_MAG - 1.1)))
    rL = front + 3.0                                     # the top round: DM11's long pointed bullet forward
    b.lathe("y", (0, 0, MAG_TOP + 2.0 - H0), [(L0 - (rL + 38.5), 0), (L0 - (rL + 38.5), 4.0),
                                              (L0 - (rL + 17.0), 4.0), (L0 - (rL + 13.5), 2.6),
                                              (L0 - (rL + 2.0), 2.3), (L0 - rL, 0.8), (L0 - rL, 0)],
            seg=10, mat="brass", phase=0.5)


def build_drum():
    """The 40-round drum, in the gun's space like the 20: feed tower, drum with hub caps, a winding key in front."""
    b = kit.Builder()
    foot = DRUM_H + 12.0                                  # the tower's foot, inside the drum
    tower = [MAG_BODY[3], (MAG_BODY[0][0] + MAG_RAKE * (MAG_BODY[0][1] - foot), foot),
             (MAG_BODY[1][0] + MAG_RAKE * (MAG_BODY[1][1] - foot), foot), MAG_BODY[2]]
    slab(b, tower, half=W_MAG, bevel=1.0, mat="magpoly")
    feed_lips_and_round(b)
    h, r = DRUM_HALF, DRUM_R
    c = (0.0, L0 - DRUM_L, DRUM_H - H0)
    b.lathe("y", c, [(-h, 0), (-h, r - 5.0), (-h + 1.0, r - 2.0), (-h + 2.5, r), (h - 2.5, r), (h - 1.0, r - 2.0),
                     (h, r - 5.0), (h, 0)], seg=24, mat="magpoly")
    for sgn in (-1, 1):                                   # hub caps on both faces
        b.lathe("y", c, [(sgn * h, 0), (sgn * h, 11.0), (sgn * (h + 1.2), 10.2), (sgn * (h + 1.2), 0)], seg=16,
                mat="magpoly")
    b.lathe("y", c, [(h + 1.2, 0), (h + 1.2, 5.5), (h + 4.0, 5.5), (h + 4.0, 0)], seg=12, mat="metal")
    b.box(-8.0, 8.0, c[1] + h + 4.0, c[1] + h + 6.4, c[2] - 1.8, c[2] + 1.8, mat="metal", bevel=0.5)
    return b.to_object("46x30Magazine40_UCP")


def build_mount():
    """The MP7's mount device as it looks on this pistol: the barrel's threaded end 15 mm out of the slide with a
    knurled adapter, inside the Rotex-II's collar (radius 13.5 mm). Origin at `canon`, along +Y."""
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(-0.6, 0), (-0.6, 5.6), (0.0, 5.6), (0.0, 6.8), (0.8, 7.4), (14.2, 7.4), (15.0, 6.6),
                              (15.0, 3.0), (11.0, 2.8), (11.0, 0)], seg=16, mat="metal", phase=0.5)
    return b.to_object("UCP_Muzzle_Mount_Device")


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: H&K's black polymer and nitrided slide, grey-black controls
    "polymer": (44, 44, 46), "grip": (42, 42, 44), "metal": (46, 47, 50), "rail": (46, 46, 49), "dark": (22, 22, 23),
    "control": (58, 58, 61), "magpoly": (38, 38, 40), "brass": (150, 118, 62), "copper": (120, 66, 44),
    "suppressor": (44, 45, 48),
}
for ch, rows in {
        "H": ["101", "101", "111", "101", "101"], "K": ["101", "101", "110", "101", "101"],
        "U": ["101", "101", "101", "101", "111"], "C": ["111", "100", "100", "100", "111"],
        "8": ["111", "101", "111", "101", "111"], "5": ["111", "100", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def in_poly(L, H, pts):
    inside = np.zeros(L.shape, bool)
    for i in range(len(pts)):
        (la, ha), (lb, hb) = pts[i], pts[(i + 1) % len(pts)]
        if ha == hb:
            continue
        inside ^= ((ha > H) != (hb > H)) & (L < la + (H - ha) * (lb - la) / (hb - ha))
    return inside


def near_line(L, H, pts, w):
    m = np.zeros(L.shape, bool)
    for (la, ha), (lb, hb) in zip(pts, pts[1:]):
        dl, dh = lb - la, hb - ha
        t = np.clip(((L - la) * dl + (H - ha) * dh) / max(dl * dl + dh * dh, 1e-9), 0, 1)
        m |= np.hypot(L - (la + t * dl), H - (ha + t * dh)) < w
    return m


def pin(col, L, H, sel, cL, cH, r=2.0):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 14


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "rail", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.99 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 78.0, 62.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


FRONT_PANEL = [(134.6, 57.0), (140.0, 57.0), (151.5, 13.6), (144.8, 13.6)]       # stippling along the front strap
HK_PANEL = [(147.0, 66.0), (166.0, 66.0), (171.0, 60.0), (172.0, 27.0), (155.0, 27.0)]   # H&K's ribbed panel
REAR_PANEL = [(177.5, 64.0), (182.0, 64.0), (197.6, 12.7), (189.0, 12.7)]        # stippled backstrap
FRAME_PINS = [(88.5, 98.0), (157.0, 98.5)]


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x = p[..., 0]
    L, H = L0 - p[..., 1], p[..., 2] + H0
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7      # upright game space: +X the gun's left
    up, fwd, back = n[..., 2] > 0.7, n[..., 1] > 0.7, n[..., 1] < -0.7
    if kind == "gun":
        grip = (mat == MATS.index("grip")) & side & (np.abs(x) > W_GRIP - 0.6)
        frame = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_FRAME - 0.6)
        for poly in (FRONT_PANEL, REAR_PANEL):            # stippling: random raised grains
            pm = grip & in_poly(L, H, poly)
            grains = pm & (kit.vnoise(maps["pos"], 0.55, 21) > 0.55)
            col[grains] += 24
            col[pm & ~grains] *= 0.72
        hk = grip & in_poly(L, H, HK_PANEL)
        col[grip & near_line(L, H, HK_PANEL + HK_PANEL[:1], 0.5)] *= 0.5
        col[hk & (np.mod(L - 0.3 * H, 3.0) < 1.1)] *= 0.4                       # long ribs leaning with the grip
        col[hk & (np.mod(L - 0.3 * H, 3.0) > 1.1) & (np.mod(L - 0.3 * H, 3.0) < 1.6)] += 16
        col[hk & (np.abs(np.mod(H - 30.0, 9.0) - 4.5) < 0.5)] *= 0.7            # broken into H&K's letter blocks
        col[grip & near_line(L, H, [(176.0, 66.0), (192.0, 7.0)], 0.5)] *= 0.55   # the backstrap's border line
        col[grip & left & kit.text_mask(L, H, "HK UCP", 162.0, 18.6, 4.4)] += 30      # left: reads rearward
        col[grip & right & kit.text_mask(-L, H, "HK UCP", -180.0, 18.6, 4.4)] += 30   # right: toward the muzzle
        for cL, cH in FRAME_PINS:
            pin(col, L, H, frame, cL, cH)
        col[frame & near_line(L, H, [(1.5, 101.6), (195.0, 101.6)], 0.4)] *= 0.6   # moulding line under the slide
        col[frame & (np.hypot(L - 193.0, H - 97.6) < 1.1)] = (200, 200, 195)        # the white dot at the rear lever
        ctl = mat == MATS.index("control")
        col[ctl & side & (np.mod(L + 0.5 * H, 1.6) < 0.6)] *= 0.65                  # slide release ribs
        col[(mat == MATS.index("dark")) & (np.mod(H, 1.4) < 0.5) & fwd] += 10
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("metal")) & (r < 2.8) & (L < 1.2)] = 7
    elif kind == "slide":
        sl = (mat == MATS.index("metal")) & side
        # Rear serrations (both sides): twelve grooves, the top leaning forward, between L 129 and 194.
        g = np.mod(L + 0.35 * (H - 110.0) - 131.0, 5.2)
        ser = sl & (L > 128.5) & (L < 194.5) & (H > 103.6) & (H < 118.6)
        col[ser & (g < 1.4)] *= 0.3
        col[ser & (g > 1.4) & (g < 2.0)] += 26
        col[sl & left & kit.text_mask(L, H, "HK UCP", 13.7, 107.6, 6.0)] += 30
        col[sl & left & kit.text_mask(L, H, "4.6X30", 97.7, 106.6, 3.0)] += 30
        col[sl & left & (np.hypot(L - 116.7, H - 111.0) < 3.0)] *= 0.55            # round recess (chamber)
        pin(col, L, H, sl, 157.3, 117.6, 1.6)
        # Ejection port on the right (not in the photo; sized for the 30 mm case): the gap, the barrel hood.
        port = sl & right & (L > 72) & (L < 106) & (H > 111.5)
        hood = port & (L > 73.5) & (L < 104.5) & (H > 113.0) & (H < 124.8)
        col[port & ~hood] = 8
        col[hood] = col[hood] * 0.6 + np.array([62, 63, 66]) * 0.4
        col[hood & kit.text_mask(-L, H, "4.6X30", -102.0, 116.0, 2.6)] += 46
        top_port = (mat == MATS.index("metal")) & up & (L > 72) & (L < 106) & (x < -2.0)
        col[top_port] = col[top_port] * 0.3 + 6
        dark = mat == MATS.index("dark")                    # three-dot sights
        col[dark & back & (L < 20) & (np.hypot(x, H - 127.8) < 1.0)] = (225, 225, 215)
        col[dark & back & (L > 180) & (np.hypot(np.abs(x) - 3.8, H - 127.0) < 0.9)] = (225, 225, 215)
        col[dark & back & (L > 180) & (np.abs(x) < 1.2) & (H > 126.6)] = 6
        col[dark & up & (L > 180) & (np.abs(x) < 1.2)] = 6
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("metal")) & fwd & (L < 1.4) & (r < 6.2)] = 6
    elif kind in ("mag", "drum"):
        mp = mat == MATS.index("magpoly")
        base = mat == MATS.index("polymer")
        s = math.atan(MAG_RAKE)
        Lb, Hb = 171.0, 6.5
        u = -(L - Lb) * math.sin(s) + (H - Hb) * math.cos(s)
        v = -(L - Lb) * math.cos(s) - (H - Hb) * math.sin(s)
        tower = mp & side & (np.abs(x) > W_MAG - 0.6)
        col[tower & (np.abs(v - 2.0) < 0.8) & (u > 8) & (u < 76)] *= 0.5
        for k in range(3):
            col[tower & (np.hypot(v - 10.0, u - (70.0 - k * 9.0)) < 1.6)] = 9   # round-count holes
        if kind == "mag":
            col[mp & right & kit.text_mask(v, u, "20", 6.0, 6.0, 5.0)] = (176, 176, 170)
            col[mp & left & kit.text_mask(-v, u, "20", -14.0, 6.0, 5.0)] = (176, 176, 170)
            col[base & side & near_line(L, H, [(147.5, 5.4), (196.0, 3.6)], 0.4)] *= 0.5
        else:
            # the drum's faces: a groove round each, a ring round the hub, "40" upright under it, reading the right
            # way in game from behind (the gun's right, -X, on the viewer's right) and from the front
            dz = H - DRUM_H
            r = np.hypot(x, dz)
            face = mp & (np.abs(n[..., 1]) > 0.7) & (np.abs(np.abs(L - DRUM_L) - DRUM_HALF) < 0.4) & (r < DRUM_R - 2.0)
            col[face & (np.abs(r - 28.5) < 0.7)] *= 0.55
            col[face & (np.abs(r - 11.5) < 0.5)] *= 0.6
            for f, uu in ((face & back, -x), (face & fwd, x)):
                col[f & kit.text_mask(uu, dz, "40", -5.6, -24.0, 7.0)] = (190, 190, 184)
        br = mat == MATS.index("brass")
        rL = MAG_BODY[3][0] + 3.0
        col[br & (L < rL + 13.5)] = BASE["copper"]
    elif kind == "mount":
        y, z = p[..., 1], p[..., 2]
        r = np.hypot(x, z)
        a = np.arctan2(x, z)
        knurl = (y > 2.0) & (y < 12.5) & (r > 7.0)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 1.6) < 0.8) ^ (np.mod(a[knurl] * 9.0 / math.pi, 1.0)
                                                                        < 0.5)))[..., None]
        col[(r > 7.0) & (np.abs(y - 13.4) < 0.4)] *= 0.5
        col[r < 3.2] = 8
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
# Attachment points (GoM's pistol set, at the relations GoM's Glock 17 and our Five-seveN use)
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
        "underbarrel": {"offset": g(34.0, RAIL_TEETH_H), "rotate": ZERO},
        "canon": {"offset": g(CANON_L, BORE_H), "rotate": ZERO},
        "slide_fired": {"offset": [0.0, round(-SLIDE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["world"] = {"offset": [-0.009, 0.062, 0.0], "rotate": ZERO}
    pts["_notes"] = {
        "units": "game units (0.72 of real size); +Y muzzle; modelled upside down as GoM's pistols are: +Z the gun's "
                 "BOTTOM, +X its RIGHT; origin = the web of the grip under the beavertail (photo L %.0f, H %.0f)"
                 % (L0, H0),
        "magazine": "no magazine point: 46x30Magazine20_UCP and the 40-round drum 46x30Magazine40_UCP are modelled in "
                    "the gun's space and drawn at its origin",
        "canon": "the barrel's crown; the item GunsOfTienPost93.MP7_Muzzle_Mount_Device (shared with the MP7, drawn "
                 "here with the model UCP_Muzzle_Mount_Device) and MP7_Suppressor, extending along +Y",
        "slide_fired": "UCP_SLIDE back %.0f mm real" % SLIDE_TRAVEL,
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
    mags = [build_magazine(), build_drum()]
    mount = build_mount()
    kit.unwrap([body, slide], 0.006)
    for o in mags + [mount]:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, slide], [[body, slide], [body, slide]], ["gun", "slide"], 256, os.path.join(TEX_DIR, "UCP.png"))
    for name, kind, m in zip(("46x30Magazine20_UCP", "46x30Magazine40_UCP"), ("mag", "drum"), mags):
        texture([m], [[m]], [kind], 128, os.path.join(TEX_DIR, name + ".png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "UCP_Muzzle_Mount_Device.png"))

    for o in [body, slide] + mags:                        # upside down, as GoM's pistols
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in [body, slide] + mags + [mount]}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")

    kit.export([body, slide], FBX_GUN)
    kit.export(mags, FBX_MAGS)
    kit.export([mount], FBX_PARTS)
    for name, b in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
