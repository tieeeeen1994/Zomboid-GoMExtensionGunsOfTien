"""Walther PPK (.22 LR) model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_ppk.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_PPK.fbx              PPK_BODY, PPK_SLIDE
    M/models_X/weapons/magazines/GunsOfTien_PPK_magazines.fbx   22LRMagazine8_PPK
    M/textures/weapons/GunsOfTien/PPK.png                        512 atlas (frame, grip, slide; 512 where GoM's
                                                                 pistols are 256: at 256 a texel is 0.9 mm on this
                                                                 small gun and the 1.45 mm serrations vanish)
    M/textures/weapons/GunsOfTien/22LRMagazine8_PPK.png          128
    scripts/ppk_points.json                                      attachment points (game space)

Carl Walther's PPK of 1931 in .22 LR (user, 2026-11-19: one magazine only, fits an ankle holster), as the post-war Ulm
gun found in the US in 1993 (imported before 1968): blued steel, the brown wrap-around grip with Walther's banner, the
eight-round magazine with its brown finger rest, a ring hammer, the safety lever on the slide's left, the round
magazine button behind the trigger guard on the left. No loaded-chamber pin (the .22s have none).
No GoM parts (2026-11-19, after review renders with them fitted): GoM's pistol mount and sights, underbarrel lights and
lasers and 9x19 cans are sized for its full-size pistols and swamp a 155 mm gun whose dust cover is 30 mm long (the
lights hung in front of the trigger guard, the cans stood taller than the slide), and the .22 PPK had neither a rail
nor a threaded barrel; so only the muzzle (flash), slide and floor points.

Built as build_glock21.py builds the Glock 21, which is how GoM builds its pistols: body + slide nodes, the slide drawn
through MarzGuns.Slide_Lock / Slide_Fired, the magazine in the gun's own space (no `magazine` point), modelled and baked
upright and turned upside down at export, origin 11 mm behind the deepest point of the back edge under the tang at its
height, 0.603 of real size (every Guns of Tien gun). The slide is a loft (its top is round, so a side profile alone
cannot make it): cross-sections along the bore, flat sides up to 6 mm under the top, then a rounded top to a 6.4 mm
flat; its height at each station is the side profile's.

References: references/ppk22/ (SOURCES.txt, contact sheets; out of the repo). Measured on a flat studio photo of the
gun's right side, post-war Ulm PPK serial 110860 LR ("LR" = .22 long rifle; references/ppk22/ppk22_right_110860LR.jpg,
3000 px), traced (post93/trace_outline.py, threshold 225) into scripts/ppk_reference_outline.json at Walther's 155 mm
(18.34 px a mm; the height then reads 96.4 mm from the grip's bottom edge to the rear sight against Walther's 100 with
the flat base plate). Profiles are in that photo's (L, H) mm: L back from the muzzle, H up from the lowest point of the
finger rest. Trigger, guard opening and silhouette come off the trace; inner lines (slide / frame, grip panel, port,
serrations) were read off 1 mm gridded crops. Left-side parts (safety lever, magazine button, slide inscriptions) come
from a left-side photo of an Ulm "Modell PPK Cal. 22 l.r." (references/ppk22/ppk22_left_ulm.jpg), mirrored and fitted
onto the right photo's silhouette (IoU 0.87; it is stretched 9 % vertically, so its heights were rescaled on the
slide's top and bottom edges). Widths: Walther's 25 mm over the grips, the slide 22.6 and the frame 21.8 from a
straight rear view of a PPK (references/ppk22/raw/back_018.jpg: slide 0.91 of the grip, perspective allowed for).
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_PPK.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_PPK_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "ppk_points.json")
MAG_NAME = "22LRMagazine8_PPK"

K = 0.000603                       # game units per real mm: the M16A2's proportion (every Guns of Tien gun)
K_OLD = 0.00072                    # GoM's pistols: the `world` floor point is scaled from them
kit.K = K
MATS = ["metal", "grip", "barrel", "dark", "magsteel", "magpoly", "brass", "lead"]
kit.MATS[:] = MATS
for ch, rows in {"W": ["101", "101", "101", "111", "101"], "L": ["100", "100", "100", "100", "111"],
                 "T": ["111", "010", "010", "010", "010"], "H": ["101", "101", "111", "101", "101"],
                 "C": ["111", "100", "100", "100", "111"], "K": ["101", "101", "110", "101", "101"],
                 "B": ["110", "101", "110", "101", "110"], "O": ["111", "101", "101", "101", "111"],
                 "U": ["101", "101", "101", "101", "111"], "/": ["001", "001", "010", "100", "100"],
                 "5": ["111", "100", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

# Origin: 11 mm behind the deepest point of the back edge under the tang (L 135.3, H 67), at its height
L0, H0 = 146.3, 67.0
BORE_H = 101.0                     # the muzzle ring's centre on the photo
SLIDE_TOP, SLIDE_BOTTOM = 109.4, 88.5
SLIDE_TRAVEL = 22.0                # back until the slide's rear passes over the web of the hand (the PPK's slide bite)
W_SLIDE, W_FRAME, W_GRIP, W_GUARD = 11.3, 10.9, 12.5, 4.0
W_MAG, W_BASE = 5.3, 11.0
ROUND_TOP = 6.0                    # the slide's top rounds over its upper 6 mm (the highlight line at H 103.5)
TOP_FLAT = 3.2                     # half width of the flat along the top


def P(L, H):
    return L0 - L, H - H0


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="metal", x0=0.0):
    return kit.slab(b, [P(L, H) for L, H in outline], [[P(L, H) for L, H in h] for h in holes], half, bevel, res,
                    mat, x0)


def circle(cL, cH, r, a0=0.0, a1=360.0, n=24):
    """Points on a circle in (L, H), from angle a0 to a1 degrees (0 = toward the rear, 90 = up)."""
    return [(cL + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cH + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + (0 if a1 - a0 >= 360 else 1))]


# ==================================================================================================
# Profiles (photo L, H mm)
# ==================================================================================================

def slide_top(L):
    """The slide's top edge: the rounded front corner, flat, then the slanted rear face (L 125.2 H 107.6 to the slide's
    bottom at L 140.8)."""
    pts = [(2.4, 106.0), (2.6, 107.2), (3.0, 108.2), (3.6, 108.9), (4.4, SLIDE_TOP), (124.4, SLIDE_TOP),
           (125.2, 108.4), (126.0, 106.9), (133.0, 99.3), (139.4, 92.3), (140.4, 90.4), (140.8, 89.2)]
    return float(np.interp(L, [p[0] for p in pts], [p[1] for p in pts]))


def slide_bottom(L):
    """The slide's lower edge: the curved cut-away at the front (the frame's nose shows under it), then straight."""
    pts = [(2.4, 97.6), (3.2, 97.4), (5.0, 96.6), (7.0, 95.5), (9.5, 94.0), (12.0, 92.2), (14.0, 90.3), (15.2, 89.0),
           (16.5, SLIDE_BOTTOM), (140.8, 88.3)]
    return float(np.interp(L, [p[0] for p in pts], [p[1] for p in pts]))


def slide_half(L):
    """The slide's front corners are rounded seen from above too."""
    return float(np.interp(L, [2.4, 2.8, 3.4, 4.4, 5.5], [9.6, 10.4, 10.9, 11.2, W_SLIDE]))


SLIDE_STATIONS = sorted(set([2.4, 2.6, 2.8, 3.0, 3.4, 3.6, 4.0, 4.4, 5.0, 5.5, 7.0, 9.5, 12.0, 14.0, 15.2, 16.5,
                             30.0, 53.0, 81.5, 95.0, 110.0, 124.4, 125.2, 126.0, 128.0, 130.5, 133.0, 135.5, 137.5,
                             139.4, 140.4, 140.8]))
ARC = 7                            # points per quarter of the rounded top


def slide_section(L):
    hb, ht, w = slide_bottom(L), slide_top(L), slide_half(L)
    h = max(ht - hb, 0.3)
    rr = min(ROUND_TOP, h * 0.8)
    tf = TOP_FLAT * min(1.0, w / W_SLIDE)
    c = min(0.7, h * 0.15)
    e = 2.0 / 2.6                                         # a superellipse, a little squarer than a circle
    right = [(w, hb + c), (w, ht - rr)]
    for k in range(1, ARC):
        t = math.pi / 2 * k / ARC
        right.append((tf + (w - tf) * math.cos(t) ** e, ht - rr + rr * math.sin(t) ** e))
    right.append((tf, ht))
    left = [(-x, H) for x, H in reversed(right)]
    return [(w - c, hb)] + right + left + [(-w + c, hb)]


SLIDE_PROFILE = [(L, slide_top(L)) for L in SLIDE_STATIONS] + [(L, slide_bottom(L)) for L in reversed(SLIDE_STATIONS)]

FRONT_SIGHT = [(13.1, 109.0), (12.6, 109.2), (11.3, 109.3), (10.2, 111.4), (9.6, 111.7), (8.2, 111.5), (6.0, 110.9),
               (4.4, 109.9), (4.0, 109.0)]
REAR_SIGHT = [(121.9, 109.0), (120.2, 109.2), (119.0, 111.9), (117.7, 112.4), (116.1, 112.1), (115.2, 111.0),
              (114.5, 109.4), (114.0, 109.0)]

# The safety lever on the slide's left (as on the left-side photo: down, the safe / decocked position): a round boss,
# a ribbed arm down and forward over the grip's top, a rounded tab pointing forward.
SAFETY_BOSS = (119.5, 99.0, 4.2)
SAFETY_ARM = [(121.2, 96.6), (117.8, 95.4), (113.6, 86.4), (114.4, 85.6), (117.2, 85.6), (121.4, 92.0)]
SAFETY_TAB = [(116.6, 99.8), (112.0, 99.0), (108.6, 96.4), (107.4, 93.4), (108.4, 90.9), (110.8, 90.4), (113.6, 92.0),
              (116.4, 95.6)]

# Frame: the nose under the slide's cut-away, the dust cover, the tang behind the slide, the grip frame (its back edge
# 0.5 inside the wrap-around grip's), the butt, the front strap, the trigger guard's rear wall.
FRAME = [(3.3, 97.3), (5.0, 96.5), (7.0, 95.4), (9.5, 93.9), (12.0, 92.1), (14.0, 90.2), (15.2, 88.9), (16.5, 88.4),
         (140.6, 88.2), (141.6, 88.6), (143.3, 87.6), (146.0, 85.6), (148.9, 83.4), (150.0, 82.0), (150.4, 80.6),
         (150.2, 79.2), (149.0, 77.6), (146.0, 76.4), (141.1, 75.2), (138.4, 73.7), (136.8, 72.4),
         (135.9, 68.0), (136.3, 63.5), (137.8, 59.6), (141.0, 53.0), (144.5, 45.5), (148.2, 37.5), (151.3, 31.0),
         (153.0, 26.8), (153.8, 23.0), (154.0, 19.5), (154.4, 17.6), (153.8, 15.1), (151.0, 14.8), (145.0, 14.5),
         (141.0, 14.5), (135.3, 14.6), (135.0, 16.6),
         (104.3, 16.6), (103.1, 19.1), (102.2, 24.5), (100.6, 33.0), (98.8, 39.7), (96.6, 47.5), (95.8, 51.5),
         (93.5, 54.2), (90.5, 55.4), (87.3, 56.4), (82.0, 56.0), (79.0, 56.5), (76.5, 59.6),
         (78.3, 62.0), (80.0, 65.1), (81.2, 68.0), (81.5, 70.6), (80.9, 72.6), (79.6, 74.6), (77.8, 76.8), (76.0, 78.3),
         (74.5, 79.0), (74.5, 80.4), (29.0, 80.4), (28.7, 79.6), (27.2, 81.2), (25.0, 82.1), (19.8, 83.4), (13.3, 84.3),
         (12.5, 84.6), (11.7, 85.6), (8.5, 85.7), (7.2, 87.2), (4.7, 88.7), (3.6, 91.8), (3.3, 94.5)]

# The trigger guard (hinged at its front for take-down) and its opening, off the trace
GUARD = [(28.9, 80.8), (28.9, 79.6), (31.5, 79.0), (34.5, 78.4), (37.5, 77.7), (39.4, 76.0), (41.1, 73.4), (42.0, 69.5),
         (42.8, 65.3), (44.4, 61.7), (46.5, 59.2), (49.0, 57.1), (51.4, 55.5), (56.2, 54.0), (62.1, 53.6), (68.7, 53.9),
         (74.0, 54.4), (79.3, 55.0), (84.0, 55.6), (87.3, 56.1), (89.4, 55.8), (90.6, 55.2), (90.6, 62.0), (80.0, 80.8)]
OPENING = [(54.7, 78.9), (51.5, 77.9), (47.4, 74.8), (45.4, 71.6), (44.9, 68.0), (45.2, 65.5), (46.5, 62.8),
           (48.8, 60.3), (51.7, 58.5), (55.5, 57.3), (59.0, 56.8), (63.6, 56.6), (68.5, 57.1), (73.0, 58.2), (75.5, 59.4),
           (78.3, 62.0), (80.0, 65.1), (81.2, 68.0), (81.5, 70.6), (80.9, 72.6), (79.6, 74.6), (77.8, 76.8), (76.0, 78.3),
           (74.5, 78.9)]
# The trigger, off the trace: its front face bows back to L 65.4, the tip at L 55.1 H 59.4, the wide upper part behind
# it (the photo's dark block under the frame, L 69-76) running up into the frame.
TRIGGER = [(62.4, 80.6), (63.5, 78.5), (65.1, 74.7), (65.4, 71.7), (64.9, 68.7), (63.8, 66.0), (62.0, 63.6),
           (59.2, 61.4), (56.5, 59.9), (55.1, 59.4), (55.3, 58.3), (56.8, 57.6), (59.7, 58.0), (62.9, 59.3), (65.4, 61.1),
           (67.4, 63.6), (68.2, 66.4), (68.9, 69.2), (69.6, 71.6), (72.6, 73.8), (74.3, 75.8), (75.2, 77.6), (76.0, 80.6)]

# The wrap-around grip: its front edge a straight line (the steel front strap shows ahead of it), its bottom over the
# steel butt, its back covering the back strap, its top under the slide and beside the tang.
GRIP = [(90.2, 87.8), (136.0, 87.8), (137.2, 86.9), (138.5, 84.5), (138.6, 80.5), (138.0, 77.8), (136.9, 75.4),
        (136.2, 73.5), (135.6, 70.0), (135.5, 66.0), (136.0, 63.2), (137.3, 59.8), (140.5, 53.4), (143.9, 45.8),
        (147.7, 37.9), (151.1, 31.0), (153.3, 26.8), (154.4, 23.0), (154.8, 19.6), (154.4, 18.3), (153.4, 17.7),
        (107.4, 17.7), (107.0, 18.6), (90.2, 87.0)]

# The ring hammer (down, as on both photos): a knurled ring round a 1.7 mm hole, its neck running into the slide's slot
HAMMER_C, HAMMER_R, HAMMER_HOLE = (133.3, 103.6), 4.6, 1.7
MAG_BUTTON = (88.4, 85.0, 3.2)     # left side, knurled
FRAME_PIN = (64.0, 85.3)
GUARD_PIN = (81.2, 60.4)

# The magazine: its body raked as the front strap (0.25 mm back a mm down), 28 mm deep, top at H 84; a .22 LR round on
# top (40 gr lead round nose, 25 mm long, case 15.6, rim 6.9 across)
MAG_RAKE, MAG_DEPTH, MAG_TOP, MAG_FOOT = 0.25, 28.0, 84.0, 16.0


def mag_front(H):
    return 106.0 - MAG_RAKE * (H - 16.6)


MAG_BODY = [(mag_front(MAG_FOOT), MAG_FOOT), (mag_front(MAG_FOOT) + MAG_DEPTH, MAG_FOOT),
            (mag_front(MAG_TOP) + MAG_DEPTH, MAG_TOP), (mag_front(MAG_TOP), MAG_TOP)]
FINGER_REST = [(104.0, 16.6), (104.0, 15.2), (103.6, 10.5), (103.0, 7.6), (101.6, 5.0), (101.0, 3.4), (101.4, 1.9),
               (102.8, 0.3), (105.2, 0.0), (118.2, 3.2), (132.0, 5.9), (133.6, 7.0), (135.3, 9.2), (135.5, 10.3),
               (134.9, 13.6), (135.0, 16.6)]
FINGER_PANEL = [(132.2, 13.9), (110.2, 13.9), (110.8, 6.5)]          # the recessed triangle on each side
ROUND_TIP = mag_front(MAG_TOP) + 1.0


# ==================================================================================================
# Geometry
# ==================================================================================================

def loft(b, stations, mat):
    """Closed tube through cross-sections [(L, [(x, H), ...])] of equal length, capped at both ends."""
    bm = b.bm
    rings = [[bm.verts.new((x, L0 - L, H - H0)) for x, H in sec] for L, sec in stations]
    n = len(rings[0])
    faces = []
    for ra, rb in zip(rings, rings[1:]):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    faces.append(bm.faces.new(rings[0][::-1]))
    faces.append(bm.faces.new(rings[-1]))
    return b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_body():
    b = kit.Builder()
    slab(b, FRAME, half=W_FRAME, bevel=1.0, res=1)
    slab(b, GUARD, [OPENING], half=W_GUARD, bevel=0.9, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=3.2, res=2, mat="grip")
    slab(b, TRIGGER, half=2.6, bevel=0.6, res=1)
    cL, cH = HAMMER_C
    ring = circle(cL, cH, HAMMER_R, -50.0, 230.0, 28)
    hammer = ring + [(131.5, 95.0), (136.0, 95.0)]
    slab(b, hammer, [circle(cL, cH, HAMMER_HOLE, 0.0, 360.0, 14)[::-1]], half=3.0, bevel=0.5, res=1)
    # the magazine button, on the left (+X upright)
    bL, bH, br = MAG_BUTTON
    b.lathe("x", (0.0, L0 - bL, bH - H0), [(W_FRAME - 0.5, 0.0), (W_FRAME - 0.5, br), (W_FRAME + 1.0, br),
                                           (W_FRAME + 1.4, br - 0.4), (W_FRAME + 1.4, 0.0)], seg=16, mat="metal")
    # pins (both sides): the frame pin over the trigger, the guard's rear pin
    for pL, pH in (FRAME_PIN, GUARD_PIN):
        b.lathe("x", (0.0, L0 - pL, pH - H0), [(-W_FRAME - 0.3, 0.0), (-W_FRAME - 0.3, 1.2), (W_FRAME + 0.3, 1.2),
                                               (W_FRAME + 0.3, 0.0)], seg=10, mat="metal")
    # the barrel, fixed in the frame: out of the slide's front by 2.4 mm, the bore recessed at the crown
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(84.0), 0), (t(84.0), 6.3), (t(0.4), 6.3), (t(0.0), 5.8), (t(0.0), 3.4),
                                       (t(1.2), 2.8), (t(1.2), 0)], seg=18, mat="barrel", phase=0.5)
    return b.to_object("PPK_BODY")


def build_slide():
    b = kit.Builder()
    loft(b, [(L, slide_section(L)) for L in SLIDE_STATIONS], "metal")
    slab(b, FRONT_SIGHT, half=1.3, bevel=0.35, res=1)
    slab(b, REAR_SIGHT, half=3.0, bevel=0.5, res=1)
    xs = W_SLIDE + 0.7                                       # the safety on the left, standing 1.4 mm off the slide
    bL, bH, br = SAFETY_BOSS
    slab(b, circle(bL, bH, br, 0.0, 360.0, 20), half=0.8, bevel=0.35, res=1, x0=xs + 0.2)
    slab(b, SAFETY_ARM, half=0.7, bevel=0.3, res=1, x0=xs)
    slab(b, SAFETY_TAB, half=0.7, bevel=0.3, res=1, x0=xs)
    return b.to_object("PPK_SLIDE")


def build_magazine():
    b = kit.Builder()
    slab(b, MAG_BODY, half=W_MAG, bevel=0.8, res=1, mat="magsteel")
    slab(b, FINGER_REST, half=W_BASE, bevel=1.6, res=1, mat="magpoly")
    front, rear = mag_front(MAG_TOP), mag_front(MAG_TOP) + MAG_DEPTH
    lips = [(front + 4.0, MAG_TOP - 0.2), (rear - 1.0, MAG_TOP - 0.2), (rear - 2.5, MAG_TOP + 2.6),
            (front + 9.0, MAG_TOP + 2.6)]
    for s in (1, -1):
        slab(b, lips, half=0.6, bevel=0.2, mat="magsteel", x0=s * (W_MAG - 0.6))
    rL = ROUND_TIP                          # the top round, round nose forward
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, MAG_TOP + 3.0 - H0), [(t(rL + 25.0), 0), (t(rL + 25.0), 3.45), (t(rL + 23.9), 3.45),
                                              (t(rL + 23.8), 2.85), (t(rL + 9.4), 2.85), (t(rL + 9.4), 2.8),
                                              (t(rL + 5.0), 2.7), (t(rL + 2.6), 2.1), (t(rL + 1.0), 1.2),
                                              (t(rL), 0)], seg=12, mat="brass", phase=0.5)
    return b.to_object(MAG_NAME)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: Walther's blue-black bluing, the brown plastic grip and finger rest, a grey bore, lead and brass
    "metal": (44, 47, 55), "grip": (78, 52, 45), "barrel": (60, 62, 68), "dark": (22, 22, 24),
    "magsteel": (42, 45, 52), "magpoly": (72, 47, 42), "brass": (156, 122, 64), "lead": (92, 92, 96),
}


def in_poly(L, H, pts):
    inside = np.zeros(L.shape, bool)
    for i in range(len(pts)):
        (la, ha), (lb, hb) = pts[i], pts[(i + 1) % len(pts)]
        if ha == hb:
            continue
        inside ^= ((ha > H) != (hb > H)) & (L < la + (H - ha) * (lb - la) / (hb - ha))
    return inside


def pin(col, L, H, sel, cL, cH, r=1.2):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.5)] *= 0.45
    col[sel & (d <= r - 0.5)] += 14


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "barrel", "magsteel", "brass")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.9 + 0.2 * streak[is_metal])[..., None]
    # polished bluing catches the top light: brighter upward faces and a blue sheen
    up = np.clip(n[..., 2], -1, 1)
    col *= (0.98 + 0.12 * up)[..., None]
    col[is_metal] += (np.clip(up[is_metal], 0, 1) * 10.0)[..., None] * np.array([0.8, 0.9, 1.15])
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 75.0, 40.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))   # holster wear on blued edges
    col += (convex * wear)[..., None]
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


# the checkered field of each grip side (a rounded trapezoid under the banner), its screw
CHECKER = [(100.2, 72.5), (102.0, 74.8), (124.0, 74.8), (129.0, 73.0), (134.5, 63.0), (147.5, 28.0), (147.2, 23.5),
           (144.0, 21.7), (111.0, 21.7), (108.5, 24.0)]
GRIP_SCREW = (131.2, 44.3)
PORT = (53.0, 81.5, 98.0, 108.0)          # the ejection port on the right, round ended
SERRATIONS = (95.0, 127.0, 88.8, 100.5, 1.45)


FONT57 = {  # 5x7 glyphs for the grip's banner (the kit's 3x5 W reads as an H at that size)
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
}


def text57(u, v, text, u0, v0, height):
    """kit.text_mask with FONT57: baseline-left corner at (u0, v0) mm, glyph height `height` mm."""
    px = height / 7.0
    cu = np.floor((u - u0) / px).astype(int)
    cv = np.floor((v0 + height - v) / px).astype(int)
    m = np.zeros(u.shape, bool)
    for k, ch in enumerate(text):
        for r, row in enumerate(FONT57[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    m |= (cu == k * 6 + c) & (cv == r)
    return m


def ribbon(L, H, La, Lb, Hc, half, wave):
    """The Walther banner: a band waving along L, between La and Lb."""
    mid = Hc + wave * np.sin((L - La) / (Lb - La) * 2 * np.pi)
    inside = (L > La) & (L < Lb) & (np.abs(H - mid) < half)
    rim = inside & ((np.abs(np.abs(H - mid) - half) < 0.45) | (np.abs(L - La) < 0.5) | (np.abs(L - Lb) < 0.5))
    return inside, rim


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x = p[..., 0]
    L, H = L0 - p[..., 1], p[..., 2] + H0
    side = np.abs(n[..., 0]) > 0.6
    left, right = n[..., 0] > 0.6, n[..., 0] < -0.6      # upright game space: +X the gun's left
    up, fwd, back = n[..., 2] > 0.7, n[..., 1] > 0.5, n[..., 1] < -0.5
    metal = mat == MATS.index("metal")
    if kind == "gun":
        grip = mat == MATS.index("grip")
        gs = grip & side & (np.abs(x) > W_GRIP - 0.8)
        field = gs & in_poly(L, H, CHECKER)
        chk = (np.mod(H + 0.62 * L, 1.25) < 0.42) | (np.mod(H - 0.62 * L, 1.25) < 0.42)
        # the checkered field sits a little lower and reads darker than the smooth border round it (photo 76 / 88)
        col[field] *= 0.86
        col[field & chk] *= 0.58
        col[field & ~chk] += 16
        col[gs & ~field & (H > 18.5)] += 9                    # the smooth, shinier border
        # the banner with WALTHER in raised letters, outlined on the smooth grip (right side reads toward the
        # muzzle: u = -L)
        inside, rim = ribbon(L, H, 98.4, 128.4, 80.0, 3.4, 0.9)
        col[gs & rim] *= 0.5
        col[gs & right & text57(-L, H, "WALTHER", -124.0, 78.2, 3.6)] *= 0.5
        col[gs & left & text57(L, H, "WALTHER", 102.8, 78.2, 3.6)] *= 0.5
        # the screw in its escutcheon
        sL, sH = GRIP_SCREW
        d = np.hypot(L - sL, H - sH)
        col[gs & (d < 5.0)] = BASE["grip"]
        col[gs & (np.abs(d - 5.0) < 0.4)] *= 0.6
        col[gs & (d < 2.8)] = (58, 60, 66)
        col[gs & (d < 2.8) & (np.abs(H - sH + 0.3 * (L - sL)) < 0.35)] = 16
        col[gs & (np.abs(d - 2.8) < 0.3)] = 20
        # the checkered back strap of the wrap-around grip
        bstrap = grip & back & ~side & (H > 20.0) & (H < 72.0)
        chk2 = (np.mod(H + 0.5 * x, 1.4) < 0.5) | (np.mod(H - 0.5 * x, 1.4) < 0.5)
        col[bstrap & chk2] *= 0.6
        frame = metal & side & (np.abs(x) > W_FRAME - 0.6)
        pin(col, L, H, frame, *FRAME_PIN)
        pin(col, L, H, frame, *GUARD_PIN)
        # the serial down the frame's right side beside the grip, the proof mark beside it
        skew = L - 0.21 * (79.4 - H)
        col[frame & right & kit.text_mask(-H, -skew, "104573 LR", -79.4, -89.8, 2.6)] += 26
        col[frame & right & (np.hypot(L - 84.6, H - 64.5) < 0.9)] += 18
        # the magazine button's knurling
        bL, bH, br = MAG_BUTTON
        db = np.hypot(L - bL, H - bH)
        col[metal & left & (x > W_FRAME + 0.3) & (db < br + 0.2)] += 22              # polished, as the photo's
        knurl = metal & left & (x > W_FRAME + 1.2) & (db < br - 0.3)
        col[knurl & ((np.mod(L * 2.6, 1.0) < 0.35) ^ (np.mod(H * 2.6, 1.0) < 0.35))] *= 0.55
        # the hammer's knurled rim and the hole through it
        cL, cH = HAMMER_C
        dh = np.hypot(L - cL, H - cH)
        rim_f = metal & ~side & (dh > HAMMER_R - 0.8) & (dh < HAMMER_R + 0.6) & (H > 99.0)
        ang = np.arctan2(H - cH, L - cL)
        col[rim_f & (np.mod(ang * 26 / np.pi, 1.0) < 0.45)] *= 0.45
        col[metal & ~side & (dh < HAMMER_HOLE + 0.4)] *= 0.5
        col[metal & in_poly(L, H, TRIGGER) & (np.abs(x) < 2.8) & (H < 80.0)] += 26    # the polished trigger
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("barrel")) & (r < 3.0) & (L < 1.3)] = 8              # the bore
        col[(mat == MATS.index("barrel")) & fwd & (r < 5.9) & (r > 3.0)] += 18      # the crown
    elif kind == "slide":
        sl = metal & side & (np.abs(x) > W_SLIDE - 0.7) & (np.abs(x) < W_SLIDE + 0.1)   # not the safety lever
        sa, sb, ha, hb, pitch = SERRATIONS
        g = np.mod(L - sa, pitch)
        ser = sl & (L > sa) & (L < sb) & (H > ha) & (H < hb)
        col[ser & (g < 0.6)] *= 0.3                          # the grooves
        col[ser & (g >= 0.6) & (g < 1.05)] += 46              # the ridges' lit tops
        col[ser & (g >= 1.05)] += 14
        col[sl & (np.abs(L - sb) < 0.35) & (H > ha) & (H < hb)] *= 0.4     # the ribbed block's rear edge
        # the ejection port on the right: through the rounded top too, the barrel's chamber steel showing in it
        pa, pb, qa, qb = PORT
        rr = (qb - qa) / 2
        cl = np.clip(L, pa + rr, pb - rr)
        dp = np.hypot(L - cl, H - (qa + rr))
        port = metal & (x < -3.0) & (dp < rr)
        col[port] = (106, 110, 118)
        col[port & (dp > rr - 1.0)] = 10
        col[port & (dp < rr - 1.0) & (np.abs(H - 103.0) < 0.8)] *= 0.55
        # the extractor below the port's rear
        ext = sl & right & (L > 78.1) & (L < 92.8) & (H > 100.2) & (H < 103.9)
        col[ext] += 10
        col[sl & right & (L > 78.1) & (L < 92.8) & ((np.abs(H - 100.2) < 0.3) | (np.abs(H - 103.9) < 0.3))] *= 0.4
        col[sl & right & (np.abs(L - 92.4) < 0.35) & (H > 100.2) & (H < 103.9)] *= 0.4
        # the left side's inscriptions (u = +L reads toward the rear on the left, as Walther's do)
        col[sl & left & kit.text_mask(L, H, "CARL WALTHER WAFFENFABRIK ULM/DO.", 44.5, 94.7, 1.6)] += 30
        col[sl & left & kit.text_mask(L, H, "MODELL PPK CAL. 22 L.R.", 51.5, 91.8, 1.6)] += 30
        col[sl & left & kit.text_mask(L, H, "MADE IN W.GERMANY", 18.5, 91.8, 1.6)] += 30
        inside, rim = ribbon(L, H, 23.0, 39.0, 96.0, 1.4, 0.5)
        col[sl & left & rim] += 24
        col[sl & left & kit.text_mask(L, H, "WALTHER", 26.5, 95.3, 1.3)] += 30
        # the matted top flat, the sights' notch and post
        top = metal & up & (np.abs(x) < TOP_FLAT) & (L > 13.5) & (L < 114.0)
        col[top & (kit.vnoise(p, 0.35, 11) > 0.5)] *= 0.7
        rs = metal & back & (L > 116.0) & (L < 121.0) & (H > 110.6) & (np.abs(x) < 0.75)
        col[rs] = 8
        col[metal & up & (L > 115.5) & (L < 119.5) & (np.abs(x) < 0.75)] = 8
        # the safety's boss (a ring and a centre) and the ribbed arm
        bL, bH, br = SAFETY_BOSS
        dsb = np.hypot(L - bL, H - bH)
        lev = metal & left & (x > W_SLIDE + 1.0)
        col[metal & (x > W_SLIDE + 0.1)] += 42                                      # the polished safety lever
        col[lev & (np.abs(dsb - br + 0.7) < 0.3)] *= 0.5
        col[lev & in_poly(L, H, SAFETY_ARM) & (dsb > br) & (np.mod(L + 0.45 * H, 0.9) < 0.35)] *= 0.5
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[metal & fwd & (L < 3.0) & (r < 7.0)] = 12        # the slide's hole round the barrel
    elif kind == "mag":
        ms = mat == MATS.index("magsteel")
        msd = ms & side
        # witness holes on both sides, one under every second round (2, 4, 6, 8)
        for k in range(4):
            hh = MAG_TOP - 10.0 - k * 13.5
            ll = mag_front(hh) + MAG_DEPTH * 0.55
            col[msd & (np.hypot(L - ll, H - hh) < 1.3)] = 10
            col[msd & (np.hypot(L - ll, H - hh) < 1.8) & (np.hypot(L - ll, H - hh) >= 1.3)] += 16
        col[msd & right & kit.text_mask(-L, H, "22", -(mag_front(30.0) + 7.0), 28.0, 2.4)] += 22
        mp = mat == MATS.index("magpoly")
        col[mp & side & in_poly(L, H, FINGER_PANEL)] *= 0.62
        br = mat == MATS.index("brass")
        col[br & (L < ROUND_TIP + 9.4)] = BASE["lead"]
        col[br & back & (np.hypot(x, p[..., 2] - (MAG_TOP + 3.0 - H0)) < 1.6)] *= 0.8   # the rim's headstamp area
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
# Attachment points: the muzzle (flash), the slide's travel, GoM's pistol floor pose; no GoM parts
# ==================================================================================================

def g(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4), round(y * K, 4), round(z * K, 4)]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    pts = {
        "muzzle": {"offset": g(0.0, BORE_H), "rotate": [-90.0, 0.0, -180.0]},
        "slide_fired": {"offset": [0.0, round(-SLIDE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["world"] = {"offset": [round(-0.009 * K / K_OLD, 4), round(0.062 * K / K_OLD, 4), 0.0], "rotate": ZERO}
    pts["_notes"] = {
        "units": "game units (0.603 of real size, the M16A2's proportion); +Y muzzle; modelled upside down as GoM's "
                 "pistols are: +Z the gun's BOTTOM, +X its RIGHT; origin = the web of the grip under the tang "
                 "(photo L %.1f, H %.0f)" % (L0, H0),
        "magazine": "no magazine point: %s is modelled in the gun's space and drawn at its origin" % MAG_NAME,
        "parts": "none: GoM's pistol mount, sights, lights, lasers and cans dwarf a 155 mm pistol whose dust cover is "
                 "30 mm long, and the .22 PPK has no rail and no threaded barrel (review renders, 2026-11-19)",
        "slide_fired": "PPK_SLIDE back %.0f mm real" % SLIDE_TRAVEL,
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
    texture([body, slide], [[body, slide], [body, slide]], ["gun", "slide"], 512, os.path.join(TEX_DIR, "PPK.png"))
    texture([mag], [[mag]], ["mag"], 128, os.path.join(TEX_DIR, MAG_NAME + ".png"))

    for o in (body, slide, mag):                           # upside down, as GoM's pistols
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in (body, slide, mag)}
    pts = points(bounds)

    kit.export([body, slide], FBX_GUN)
    kit.export([mag], FBX_MAGS)
    # the hand's point for the loose magazine, from GoM's on its Glock 17 magazine (as the Glock 21's); the built
    # objects give up their names first, or the imported copy is renamed ".001" and not found
    for o in (body, slide, mag):
        o.name = "built_" + o.name
    ours = kit.import_mesh(FBX_MAGS, MAG_NAME)
    gom = kit.gom_glock17_magazine() if kit.GOM else None
    if ours is not None and gom is not None:
        pts["_extras"]["mag_prop2"] = kit.bip01_prop2(ours, gom)
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    for name, b in bounds.items():
        print("%-24s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))
    print("mag_prop2", pts["_extras"].get("mag_prop2"))


if __name__ == "__main__":
    main()
