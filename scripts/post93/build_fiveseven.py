"""FN Five-seveN models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_fiveseven.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_FIVESEVEN.fbx         FIVESEVEN_BODY, FIVESEVEN_SLIDE
    P/models_X/weapons/magazines/GunsOfTienPost93_FIVESEVEN_magazines.fbx  57x28Magazine20/30_FIVESEVEN
    P/models_X/weapons/parts/GunsOfTienPost93_FIVESEVEN_parts.fbx      FIVESEVEN_Suppressor, FIVESEVEN_Muzzle_Mount_Device
    P/textures/weapons/GunsOfTienPost93/<name>.png                     FIVESEVEN (256, body + slide), one 128
                                                                        texture per magazine and the suppressor
    scripts/post93/fiveseven_points.json                               attachment points (game space)

The gun is the item MarzGuns.FIVESEVEN (Guns of Marz names it, "5.7x28mm Five-SeveN", but ships nothing else), built
the way GoM builds its pistols (its Glock 17 is the template; CLAUDE.md, "FN Five-seveN"): a body node and a slide
node drawn through MarzGuns.Slide_Lock / Slide_Fired, magazines whose meshes sit in the gun's own space (the model
has no `magazine` point, so they are drawn at its origin), the model upside down (game +Z = the gun's bottom, +X its
right), origin in the web of the grip under the beavertail, 0.72 of real size. Everything below is modelled and baked
upright and turned 180 degrees about the bore axis at export, magazines included. Its suppressor, the SFN-57 (Gemtech's
can for the Five-seveN; user, 2026-10-16: one suppressor per gun), is built straight in that upside-down space with its
origin at `canon`; the muzzle mount device is the P90's item, shared (gen_post93_guns.py), drawn on this gun as a
threaded-barrel adapter of its own (FIVESEVEN_Muzzle_Mount_Device) instead of the P90's flash hider clamp.

The shape is measured from a side photo of an FNH USA Five-seveN (U.S. ATF, public domain:
commons.wikimedia.org/wiki/File:FN_Five_Seven.jpg, kept as docs/fiveseven_atf.jpg); its traced outline is
fiveseven_reference_outline.json (208 mm long), which render_fiveseven.py / make_fiveseven_art.py lay over the model.
Every profile is written in that photo's coordinates, real millimetres: L back from the muzzle, H up from the lowest
point (the 20-round magazine's base plate). Geometry helpers, bakes, noise and the FBX export come from build_mp7.py.
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_FIVESEVEN.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_FIVESEVEN_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_FIVESEVEN_parts.fbx")
TEX_DIR = kit.TEX_DIR
POINTS_JSON = os.path.join(HERE, "fiveseven_points.json")

K = kit.K                          # game units per real millimetre
MATS = ["polymer", "grip", "metal", "rail", "dark", "control", "magpoly", "brass", "copper", "suppressor"]
kit.MATS[:] = MATS                 # build_mp7's Builder, materials and bake passes index this list

# Photo coordinates (mm) of the model origin: in the web of the grip, 11 mm behind the deepest point of the back
# edge under the beavertail, at its height; GoM's Glock 17 has its origin the same way (12 mm behind its frame at
# that height, the bore 47 mm above; here 45). game y = L0 - L, game z = H - H0.
L0, H0 = 197.0, 87.0
BORE_H = 132.0                     # bore axis
CANON_L = 0.9                      # the barrel's crown, flush with the slide's face
SLIDE_BOTTOM, SLIDE_TOP = 120.6, 141.0
SLIDE_TRAVEL = 31.0                # slide_fired (GoM's Glock 32 mm, USP 38, M92FS 48)
RAIL_TEETH_H = 100.5               # bottom face of the accessory rail's crossbars
MAG_RAKE = 0.25                    # tan of the magazine's lean (the grip's front and back edges: 15 and 13 degrees)
MAG30_DROP = 40.0                  # the 30-round magazine is this much longer, along its axis
MAG_TOP = 94.0                     # the magazine body's top, under the feed lips (its front wall clears the opening)

W_SLIDE, W_SLIDE_FRONT, W_FRAME, W_FRAME_FRONT, W_GRIP, W_GUARD = 12.6, 11.0, 13.4, 11.0, 14.4, 6.5   # half widths
W_MAG, W_BASE = 9.5, 12.0


def P(L, H):
    """Photo (L, H) mm -> game (y, z) mm."""
    return L0 - L, H - H0


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


def shifted(points, dL, dH):
    return [(L + dL, H + dH) for L, H in points]


# ==================================================================================================
# Profiles (traced from the photo; fiveseven_reference_outline.json)
# ==================================================================================================

# Slide: a narrower steel front section ahead of the slanted step at L 60, the wider rear section behind it (the
# Five-seveN's polymer-clad slide), the rear corner rounded down to the vertical rear face.
SLIDE_FRONT = [(1.5, SLIDE_BOTTOM), (1.5, 138.6), (2.4, 140.3), (4.0, SLIDE_TOP), (62.5, SLIDE_TOP),
               (64.0, SLIDE_BOTTOM)]
SLIDE_REAR = [(61.3, SLIDE_BOTTOM), (59.8, SLIDE_TOP), (196.0, SLIDE_TOP), (199.6, 140.0), (202.4, 137.6),
              (204.6, 133.5), (205.0, 131.0), (205.0, SLIDE_BOTTOM)]
FRONT_SIGHT = [(8.1, 140.5), (8.1, 144.4), (8.8, 146.1), (11.3, 148.0), (14.3, 149.3), (16.2, 149.5), (18.2, 148.4),
               (20.3, 140.5)]
REAR_SIGHT = [(164.0, 140.5), (164.5, 142.4), (166.5, 143.6), (183.7, 143.8), (184.0, 147.0), (186.5, 147.3),
              (187.0, 149.0), (192.4, 149.0), (192.8, 148.2), (193.2, 140.5)]

# Frame above the trigger guard and grip: the rear part from the slide step to the beavertail, the narrower dust
# cover ahead of it with the accessory rail on its underside.
FRAME_REAR = [(62.5, SLIDE_BOTTOM), (205.6, SLIDE_BOTTOM), (206.6, 117.0), (207.6, 111.5), (208.0, 107.4),
              (207.8, 104.4), (207.1, 101.6), (205.9, 99.5), (204.1, 97.6), (201.6, 96.1), (190.1, 92.3),
              (187.8, 90.6), (186.3, 88.6), (185.0, 97.5), (74.0, 97.5), (71.0, 99.8), (65.5, 100.0), (62.5, 103.0)]
FRAME_FRONT = [(2.0, SLIDE_BOTTOM), (2.0, 112.8), (14.7, 112.8), (16.0, 103.0), (64.0, 103.0), (64.0, SLIDE_BOTTOM)]
RAIL_SLOTS = [22.0, 32.0, 42.0, 52.0, 62.0]             # slot centres, 10 mm pitch, 5.2 mm wide
RAIL_TEETH = [(16.3, 19.4)] + [(c + 2.6, c + 7.4) for c in RAIL_SLOTS[:-1]] + [(64.6, 67.0)]

# Trigger guard (outer edge, its top hidden in the frame) and the trigger opening inside it.
GUARD = [(70.0, 100.0), (74.5, 97.6), (75.2, 96.5), (76.0, 92.9), (77.6, 86.0), (79.0, 78.0), (80.3, 74.8),
         (82.0, 72.8), (85.6, 70.7), (115.7, 67.5), (128.8, 67.5), (133.0, 66.8), (135.8, 65.3), (137.3, 63.8),
         (139.0, 60.5), (139.0, 99.0)]
OPENING = [(88.0, 97.5), (85.4, 95.8), (83.1, 93.7), (81.6, 90.5), (81.2, 86.7), (82.9, 78.8), (83.9, 76.9),
           (85.2, 75.6), (88.0, 74.5), (117.0, 71.7), (121.7, 71.7), (125.6, 72.2), (129.6, 73.7), (131.1, 75.0),
           (132.2, 77.1), (132.4, 79.4), (131.8, 88.0), (131.5, 97.5)]
TRIGGER = [(112.0, 98.0), (112.0, 95.5), (112.3, 83.1), (110.6, 79.2), (106.8, 76.0), (106.8, 75.0), (108.5, 74.5),
           (111.7, 75.2), (114.9, 78.4), (116.6, 81.5), (117.8, 86.0), (118.3, 92.5), (120.5, 95.0), (123.0, 96.0),
           (123.0, 98.0)]

# Grip: raked front strap, the heel, the back strap up to the web under the beavertail.
GRIP = [(131.5, 100.0), (131.8, 88.0), (132.4, 79.4), (133.2, 72.0), (135.8, 65.3), (137.3, 63.8), (138.6, 61.0),
        (139.4, 56.0), (139.5, 49.1), (141.0, 45.0), (143.5, 39.7), (144.6, 33.5), (146.0, 27.5), (147.3, 21.5),
        (148.5, 16.0), (149.1, 13.6), (196.0, 8.6), (197.6, 3.6), (199.6, 1.2), (202.0, 1.3), (203.9, 2.8),
        (204.8, 5.5), (206.5, 9.6), (206.5, 12.4), (205.9, 17.7), (205.0, 21.5), (204.2, 26.0), (203.3, 31.0),
        (202.2, 35.5), (201.0, 40.0), (199.7, 45.0), (198.4, 49.5), (197.3, 53.5), (196.0, 57.5), (194.6, 62.4),
        (186.4, 82.0), (185.8, 84.1), (185.8, 86.7), (186.2, 88.2), (187.5, 90.3), (190.1, 92.3), (194.0, 94.0),
        (194.0, 100.0)]

# Controls, light grey on the real gun: the ambidextrous safety (disc and lever), the magazine release (both sides);
# on the left only the slide stop and the takedown lever.
SAFETY_DISC = circle(115.0, 113.2, 4.2, 12)
SAFETY_LEVER = [(112.0, 111.4), (102.5, 116.0), (101.5, 118.6), (103.0, 119.4), (113.8, 115.6)]
MAG_RELEASE = [(132.2, 79.0), (133.4, 69.6), (144.4, 70.6), (143.4, 79.6)]
SLIDE_STOP = [(150.0, 112.6), (166.0, 113.4), (166.5, 117.4), (150.0, 117.2)]
TAKEDOWN = [(83.5, 113.0), (94.0, 113.0), (94.0, 118.0), (83.5, 118.5)]

# Magazine: straight body leaning with the grip (inside the grip, front wall behind the trigger opening), its base
# plate with the forward finger lip under the grip.
MAG_BODY = [(153.0, 11.5), (197.0, 7.5), (197.0 - MAG_RAKE * (MAG_TOP - 7.5), MAG_TOP),
            (153.0 - MAG_RAKE * (MAG_TOP - 11.5), MAG_TOP)]
BASE_PLATE = [(152.5, 13.2), (149.1, 12.5), (148.6, 10.7), (145.0, 8.3), (144.6, 7.1), (145.6, 5.6), (147.3, 5.1),
              (154.8, 4.9), (168.1, 3.6), (178.5, 1.9), (191.8, 0.2), (197.5, 0.3), (197.0, 8.8)]
MAG30_SHIFT = (MAG30_DROP * math.sin(math.atan(MAG_RAKE)), -MAG30_DROP * math.cos(math.atan(MAG_RAKE)))


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, FRAME_REAR, half=W_FRAME, bevel=1.8, res=1)
    slab(b, FRAME_FRONT, half=W_FRAME_FRONT, bevel=1.4, res=1)
    for La, Lb in RAIL_TEETH:                                       # accessory rail crossbars
        box(b, La, Lb, RAIL_TEETH_H, 103.4, -10.6, 10.6, mat="rail", bevel=0.4)
    slab(b, GUARD, [OPENING], half=W_GUARD, bevel=1.6, res=1)
    slab(b, GRIP, half=W_GRIP, bevel=3.5, res=2, mat="grip")
    slab(b, TRIGGER, half=3.0, bevel=0.8, res=0, mat="dark")
    # controls
    both(lambda s: slab(b, SAFETY_DISC, half=0.7, bevel=0.3, mat="control", x0=s * (W_FRAME + 0.4)))
    both(lambda s: slab(b, SAFETY_LEVER, half=0.6, bevel=0.3, mat="control", x0=s * (W_FRAME + 0.9)))
    both(lambda s: slab(b, MAG_RELEASE, half=0.7, bevel=0.3, mat="control", x0=s * (W_GRIP + 0.2)))
    slab(b, SLIDE_STOP, half=0.6, bevel=0.3, mat="control", x0=W_FRAME + 0.4)        # +X = the gun's left
    slab(b, TAKEDOWN, half=0.6, bevel=0.3, mat="control", x0=W_FRAME + 0.4)
    # the barrel's front, inside the slide: its crown at the muzzle with the bore, and as much as shows with the slide
    # back (the rest is hidden and would only take texture space)
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(SLIDE_TRAVEL + 12.0), 0), (t(SLIDE_TRAVEL + 12.0), 6.2), (t(CANON_L + 0.4), 6.2), (t(CANON_L), 5.6),
                                       (t(CANON_L), 2.9), (t(10.0), 2.9), (t(10.0), 0)], seg=14, mat="metal",
            phase=0.5)
    return b.to_object("FIVESEVEN_BODY")


def build_slide():
    b = kit.Builder()
    slab(b, SLIDE_REAR, half=W_SLIDE, bevel=1.6, res=1, mat="metal")
    slab(b, SLIDE_FRONT, half=W_SLIDE_FRONT, bevel=1.3, res=1, mat="metal")
    slab(b, FRONT_SIGHT, half=1.7, bevel=0.4, mat="dark")
    slab(b, REAR_SIGHT, half=7.6, bevel=0.8, mat="dark")
    return b.to_object("FIVESEVEN_SLIDE")


def build_magazine(rounds):
    """In the gun's own space (drawn at its origin, as GoM's pistol magazines are)."""
    b = kit.Builder()
    body = list(MAG_BODY)
    base = BASE_PLATE
    if rounds == 30:
        dL, dH = MAG30_SHIFT
        body = [(body[0][0] + dL, body[0][1] + dH), (body[1][0] + dL, body[1][1] + dH), body[2], body[3]]
        base = shifted(BASE_PLATE, dL, dH)
    slab(b, body, half=W_MAG, bevel=1.0, res=0, mat="magpoly")
    slab(b, base, half=W_BASE, bevel=1.6, res=1, mat="polymer")
    # feed lips and the top round (case to the rear, bullet forward)
    top = MAG_TOP
    front, rear = MAG_BODY[3][0], MAG_BODY[2][0]
    fl = [(front + 1.0, top - 0.2), (rear - 1.0, top - 0.2), (rear - 2.0, top + 2.0), (front + 6.0, top + 2.0)]
    both(lambda s: slab(b, fl, half=1.2, bevel=0.3, mat="magpoly", x0=s * (W_MAG - 1.2)))
    rL = front + 3.0
    b.lathe("y", (0, 0, top + 2.2 - H0), [(L0 - (rL + 40.0), 0), (L0 - (rL + 40.0), 4.0), (L0 - (rL + 13.0), 4.0),
                                          (L0 - (rL + 9.0), 2.9), (L0 - (rL + 1.5), 2.6), (L0 - rL, 1.2),
                                          (L0 - rL, 0)], seg=10, mat="brass", phase=0.5)
    return b.to_object("57x28Magazine%d_FIVESEVEN" % rounds)


SUPP_LEN = 170.0                   # SFN-57: about 33 mm across, 170 mm long (approximate)


def build_suppressor():
    """Origin at `canon` (the barrel's crown), along +Y: a knurled collar that screws on over the shared mount
    device (the P90's sleeve, radius 12.6 mm), then the plain body. Round, so it is the same upright or upside down."""
    b = kit.Builder()
    n = SUPP_LEN
    b.lathe("y", (0, 0, 0), [(3.0, 0), (3.0, 13.8), (26.0, 13.8), (27.5, 15.2), (29.0, 16.5), (n - 6, 16.5),
                              (n - 2, 15.6), (n, 13.0), (n, 4.2), (n - 5, 3.6), (n - 5, 0)], seg=20, mat="suppressor")
    return b.to_object("FIVESEVEN_Suppressor")


def build_mount():
    """The shared 5.7x28mm mount device as it looks on this pistol: the threaded end of the barrel standing 15 mm out of
    the slide with a knurled thread adapter, origin at `canon`, inside the SFN-57's collar (radius 13.8 mm) when the
    can is on. (GoM's pistols draw their mount device with its oversized Muzzle_Mount_Device model, as big as their
    suppressors; a real adapter is this small.)"""
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(-0.6, 0), (-0.6, 6.2), (0.0, 6.2), (0.0, 7.2), (0.8, 7.8), (14.2, 7.8), (15.0, 7.0),
                              (15.0, 3.4), (11.0, 3.2), (11.0, 0)], seg=16, mat="metal", phase=0.5)
    return b.to_object("FIVESEVEN_Muzzle_Mount_Device")


# ==================================================================================================
# Painting (numpy): GoM's look (flat panels, light AO, bright edges) and the photo's details by position
# ==================================================================================================

BASE = {  # sRGB
    "polymer": (47, 47, 49), "grip": (45, 45, 47), "metal": (44, 45, 48), "rail": (49, 49, 52), "dark": (20, 20, 21),
    "control": (122, 124, 126), "magpoly": (40, 40, 42), "brass": (150, 118, 62), "copper": (120, 66, 44),
    "suppressor": (44, 45, 48),
}

for ch, rows in {  # 3x5 glyphs build_mp7 lacks
        "N": ["101", "111", "111", "111", "101"], "H": ["101", "101", "111", "101", "101"],
        "E": ["111", "100", "110", "100", "111"], "R": ["110", "101", "110", "101", "101"],
        "T": ["111", "010", "010", "010", "010"], "L": ["100", "100", "100", "100", "111"],
        "B": ["110", "101", "110", "101", "110"], "G": ["111", "100", "101", "101", "111"],
        "I": ["111", "010", "010", "010", "111"], "U": ["101", "101", "101", "101", "111"],
        "C": ["111", "100", "100", "100", "111"], "K": ["101", "101", "110", "101", "101"],
        "V": ["101", "101", "101", "101", "010"], "D": ["110", "101", "101", "101", "110"],
        "5": ["111", "100", "111", "001", "111"], "8": ["111", "101", "111", "101", "111"],
        "9": ["111", "101", "111", "001", "111"], "-": ["000", "000", "111", "000", "000"]}.items():
    kit.FONT.setdefault(ch, rows)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def in_poly(L, H, pts):
    """Inside a polygon [(L, H)] (even-odd)."""
    inside = np.zeros(L.shape, bool)
    n = len(pts)
    for i in range(n):
        (la, ha), (lb, hb) = pts[i], pts[(i + 1) % n]
        if ha == hb:
            continue
        cross = ((ha > H) != (hb > H)) & (L < la + (H - ha) * (lb - la) / (hb - ha))
        inside ^= cross
    return inside


def near_line(L, H, pts, w):
    """Within w mm of a polyline [(L, H)]."""
    m = np.zeros(L.shape, bool)
    for (la, ha), (lb, hb) in zip(pts, pts[1:]):
        dl, dh = lb - la, hb - ha
        t = np.clip(((L - la) * dl + (H - ha) * dh) / max(dl * dl + dh * dh, 1e-9), 0, 1)
        m |= np.hypot(L - (la + t * dl), H - (ha + t * dh)) < w
    return m


def pin(col, L, H, sel, cL, cH, r=2.2):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 14


def common(maps, col, mat):
    """Grain, light, AO and edge highlights (build_p90.py's recipe)."""
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "rail", "brass", "copper", "control")])
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


FRONT_PANEL = [(141.6, 64.3), (158.8, 64.3), (171.6, 13.5), (150.4, 13.5)]       # stippled panels on the grip
REAR_PANEL = [(181.5, 63.4), (192.6, 63.4), (202.0, 12.0), (184.5, 9.6)]
PALM_LINE = [(199.0, 110.5), (176.0, 110.8), (169.0, 108.5), (164.5, 103.0), (163.0, 96.0), (164.5, 86.0),
             (167.5, 72.0), (170.0, 66.0)]                                       # the palm swell's moulded border
FRAME_PINS = [(201.5, 113.3), (181.4, 113.5), (120.1, 104.2), (76.4, 107.0), (96.5, 114.5)]


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x = p[..., 0]
    L, H = L0 - p[..., 1], p[..., 2] + H0          # back to the photo's coordinates
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7  # upright: +X is the gun's left
    up, fwd, back = n[..., 2] > 0.7, n[..., 1] > 0.7, n[..., 1] < -0.7
    if kind == "gun":
        grip = (mat == MATS.index("grip")) & side & (np.abs(x) > W_GRIP - 0.6)
        frame = (mat == MATS.index("polymer")) & side
        # Grip: two stippled panels (raised dots), their borders, the FN monogram between them, the palm swell line,
        # horizontal ribs down the front strap.
        for poly in (FRONT_PANEL, REAR_PANEL):
            pm = grip & in_poly(L, H, poly)
            col[grip & near_line(L, H, poly + poly[:1], 0.55)] *= 0.5
            dots = pm & (np.hypot(np.mod(L, 1.9) - 0.95, np.mod(H, 1.9) - 0.95) < 0.62)
            col[dots] += 16
            col[pm & ~dots] *= 0.82
        ov = np.hypot((L - 177.2) / 5.8, (H - 50.7) / 6.8)
        col[grip & (np.abs(ov - 1.0) < 0.1)] *= 0.45
        col[grip & (ov < 0.8) & (kit.vnoise(maps["pos"], 0.9, 11) > 0.58)] += 14
        col[(grip | frame) & near_line(L, H, PALM_LINE, 0.45)] *= 0.5
        strap = (mat == MATS.index("grip")) & (n[..., 1] > 0.4) & (L > 138) & (L < 150) & (H > 14) & (H < 60)
        col[strap & (np.mod(H, 1.7) < 0.7)] *= 0.55
        # Frame: the safety's moulded surround, pins, the serial plate on the rail's sides, the markings.
        fr = frame & (np.abs(x) > W_FRAME - 0.6)
        col[fr & near_line(L, H, [(91.5, 120.4), (91.5, 112.0), (96.0, 107.2), (126.2, 107.2), (126.2, 120.4)],
                           0.45)] *= 0.5
        for cL, cH in FRAME_PINS:
            pin(col, L, H, fr, cL, cH)
        plate = side & (np.abs(x) > W_FRAME_FRONT - 0.6) & rounded_rect(L, H, 24.0, 56.0, 107.8, 113.2, 1.0)
        col[plate] = col[plate] * 0.2 + np.array([150, 151, 152]) * 0.8
        col[side & (np.abs(x) > W_FRAME_FRONT - 0.6) & near_line(L, H, [(22.5, 106.6), (57.5, 106.6), (57.5, 114.2),
                                                                       (22.5, 114.2), (22.5, 106.6)], 0.4)] *= 0.5
        col[fr & right & kit.text_mask(-L, H, "FNH USA", -155.7, 112.1, 3.0)] += 30         # reads toward the muzzle
        col[fr & right & kit.text_mask(-L, H, "FREDERICKSBURG VA", -163.1, 108.4, 2.3)] += 22
        col[fr & (L > 150.2) & (L < 153.8) & (np.abs(H - 104.1) < 0.6)] = 10               # the small slot under them
        # Safety: the red dot of the left disc (fire), safe / fire symbols beside the right one.
        ctl = mat == MATS.index("control")
        col[ctl & left & (np.hypot(L - 112.5, H - 116.5) < 0.9)] = (190, 30, 28)
        col[fr & right & rounded_rect(L, H, 93.5, 96.5, 116.2, 118.8, 0.6)] += 30
        col[fr & right & rounded_rect(L, H, 93.5, 96.5, 112.6, 115.0, 0.6) & ~rounded_rect(L, H, 94.4, 95.6,
                                                                                         113.4, 114.2, 0.3)] += 30
        col[ctl & side & (np.mod(L - 0.6 * H, 1.4) < 0.5) & (H > 110) & (L < 114)] *= 0.7     # lever ribs
        # Trigger guard front serrations, trigger face ribs.
        gfront = (mat == MATS.index("polymer")) & (n[..., 1] > 0.5) & (L > 74) & (L < 80) & (H > 82) & (H < 96)
        col[gfront & (np.mod(H, 1.6) < 0.6)] *= 0.55
        col[(mat == MATS.index("dark")) & (np.mod(H, 1.5) < 0.5) & (n[..., 1] > 0.3)] += 10
        # Barrel: the bore at the crown.
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("metal")) & (r < 3.1) & (L < 1.6)] = 7
    elif kind == "slide":
        sl = (mat == MATS.index("metal")) & side
        # Ejection port on the right (L 80-119, open to the top): the dark gap round the barrel hood, the hood with
        # its 5.7X28 marking; the port's cut seen on top.
        port = sl & right & (L > 80) & (L < 119) & (H > 127.5)
        hood = port & (L > 81.5) & (L < 117.5) & (H > 129.0) & (H < 139.8)
        col[port & ~hood] = 8
        col[hood] = col[hood] * 0.6 + np.array([62, 63, 66]) * 0.4
        col[hood & kit.text_mask(-L, H, "5.7X28", -115.0, 132.4, 2.6)] += 46
        top_port = (mat == MATS.index("metal")) & up & (L > 80) & (L < 119) & (x < -2.0)
        col[top_port] = col[top_port] * 0.3 + 6
        col[(mat == MATS.index("metal")) & up & (L > 80) & (L < 119) & (np.abs(x + 2.0) < 0.5)] *= 0.4
        # Markings: calibre on the right, maker on the left.
        col[sl & right & kit.text_mask(-L, H, "CAL 5.7X28", -86.0, 123.6, 2.6)] += 34
        col[sl & left & kit.text_mask(L, H, "FN HERSTAL BELGIUM", 92.0, 123.8, 3.2)] += 34
        # Rear serration panel (both sides): border and twelve slanted grooves; the vertical bar at the rear; the
        # line where the steel slide meets its rear cover; pins.
        panel_pts = [(151.0, 122.4), (191.5, 122.4), (191.5, 135.2), (156.6, 135.2)]
        sp = sl & in_poly(L, H, panel_pts)
        col[sl & near_line(L, H, panel_pts + panel_pts[:1], 0.5)] *= 0.45
        g = np.mod(L - 0.44 * (H - 122.4) - 154.0, 3.2)
        col[sp & (g < 1.15) & (L > 156)] *= 0.4
        col[sp & (g > 1.15) & (g < 1.6)] += 18
        bar = sl & rounded_rect(L, H, 192.3, 198.2, 122.6, 138.8, 2.2)
        col[sl & near_line(L, H, [(192.3, 124.8), (192.3, 136.6)], 0.45)] *= 0.45
        col[bar & (L > 194.5)] += 16
        col[sl & near_line(L, H, [(151.0, 141.0), (146.5, 136.5), (143.2, 131.0), (142.0, 126.0),
                                  (141.8, SLIDE_BOTTOM)], 0.4)] *= 0.5
        for cL, cH, r in ((167.8, 138.8, 1.2), (154.3, 135.0, 1.7)):
            pin(col, L, H, sl, cL, cH, r)
        # Three-dot sights: the front sight's white dot, the rear sight's two dots either side of its notch.
        dark = mat == MATS.index("dark")
        col[dark & back & (L < 25) & (np.hypot(x, H - 146.4) < 1.1)] = (225, 225, 215)
        col[dark & back & (L > 185) & (np.hypot(np.abs(x) - 4.0, H - 146.0) < 1.0)] = (225, 225, 215)
        col[dark & back & (L > 185) & (np.abs(x) < 1.3) & (H > 145.4)] = 6
        col[dark & up & (L > 186) & (np.abs(x) < 1.3)] = 6
        # The muzzle: the slide's face round the barrel.
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("metal")) & fwd & (L < 2.2) & (r < 6.9)] = 6
    elif kind.startswith("mag"):
        mp = mat == MATS.index("magpoly")
        base = mat == MATS.index("polymer")
        rounds = int(kind[3:])
        dL, dH = MAG30_SHIFT if rounds == 30 else (0.0, 0.0)
        # along the magazine: u up its axis from the base plate, v toward its front
        s = math.atan(MAG_RAKE)
        Lb, Hb = 175.0 + dL, 9.5 + dH
        u = -(L - Lb) * math.sin(s) + (H - Hb) * math.cos(s)
        v = -(L - Lb) * math.cos(s) - (H - Hb) * math.sin(s)
        # the long groove and the witness slots of FN's magazine, the round count above the base plate
        col[mp & side & (np.abs(v - 3.0) < 0.8) & (u > 8) & (u < 80 - dH)] *= 0.5
        for k in range(3):
            col[mp & side & rounded_rect(v, u, 9.0, 15.0, 70.0 - dH - k * 9.0, 73.0 - dH - k * 9.0, 1.4)] = 9
        count = "30" if rounds == 30 else "20"                  # right side reads toward the front, left toward the rear
        col[mp & right & kit.text_mask(v, u, count, 6.0, 6.0, 5.0)] = (176, 176, 170)
        col[mp & left & kit.text_mask(-v, u, count, -14.0, 6.0, 5.0)] = (176, 176, 170)
        col[base & side & near_line(L, H, shifted([(149.5, 9.8), (196.0, 5.6)], dL, dH), 0.4)] *= 0.5
        # the top round: brass case, copper bullet with SS190's black tip
        br = mat == MATS.index("brass")
        rL = MAG_BODY[3][0] + 3.0
        col[br & (L < rL + 9.0)] = BASE["copper"]
        col[br & (L < rL + 3.0)] = (24, 24, 26)
    elif kind == "suppressor":
        # Built in the gun's upside-down space: +X the gun's right, -Z its top, +Y forward.
        y, z = p[..., 1], p[..., 2]
        r = np.hypot(x, z)
        a = np.arctan2(x, z)
        knurl = (y > 5) & (y < 24) & (r > 13.4)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 2.0) < 1.0) ^ (np.mod(a[knurl] * 15.0 / math.pi, 1.0)
                                                                         < 0.5)))[..., None]
        col[(r > 16) & ((np.abs(y - 33.0) < 0.6) | (np.abs(y - (SUPP_LEN - 10.0)) < 0.6))] *= 0.5
        # the name on the gun's right, read from the right (toward the muzzle, the gun's top up)
        col[(x > 9.0) & (r > 16) & kit.text_mask(y, -z, "SFN-57", 72.0, -3.5, 7.0)] += 80
        col[(r < 4.6) & (y > SUPP_LEN - 6)] = 8
    elif kind == "mount":
        y, z = p[..., 1], p[..., 2]
        r = np.hypot(x, z)
        a = np.arctan2(x, z)
        knurl = (y > 2.0) & (y < 12.5) & (r > 7.4)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 1.6) < 0.8) ^ (np.mod(a[knurl] * 9.0 / math.pi, 1.0)
                                                                        < 0.5)))[..., None]
        col[(r > 7.4) & (np.abs(y - 13.4) < 0.4)] *= 0.5
        col[r < 3.6] = 8
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
# Attachment points (GoM's pistol set: muzzle, world, rail_up, scope, underbarrel, canon, slide_fired)
# ==================================================================================================

def g(L, H, x=0.0):
    y, z = P(L, H)
    return [round(x * K, 4), round(y * K, 4), round(z * K, 4)]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    # Each point keeps GoM's rotate: GoM's pistol parts (Beretta mount, pistol sights, lights / lasers) are modelled
    # upside down already, like the pistols, so none of them is turned (kit.turned only negates x and z).
    pts = {
        "muzzle": {"offset": g(0.0, BORE_H), "rotate": [-90.0, 0.0, -180.0]},
        # GoM's Glock 17: the Beretta mount's point 61 mm behind the muzzle and 11.4 mm under the slide's top,
        # the pistol sights 13 mm behind and 24 mm above that, the light / laser point on the rail's underside.
        "rail_up": {"offset": g(61.0, SLIDE_TOP - 11.4), "rotate": ZERO},
        "scope": {"offset": g(74.0, SLIDE_TOP + 12.6), "rotate": ZERO},
        "underbarrel": {"offset": g(36.0, RAIL_TEETH_H), "rotate": ZERO},
        "canon": {"offset": g(CANON_L, BORE_H), "rotate": ZERO},
        "slide_fired": {"offset": [0.0, round(-SLIDE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
    }
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["world"] = {"offset": [-0.009, 0.062, 0.0], "rotate": ZERO}                  # every GoM pistol's floor pose
    pts["_notes"] = {
        "units": "game units (0.72 of real size); +Y muzzle; modelled upside down as GoM's pistols are: +Z the gun's "
                 "BOTTOM, +X its RIGHT; origin = the web of the grip under the beavertail (photo L %.0f, H %.0f)"
                 % (L0, H0),
        "magazine": "no magazine point, as on GoM's Glock 17: 57x28Magazine20/30_FIVESEVEN are modelled in the gun's "
                    "space and drawn at its origin",
        "canon": "the barrel's crown; the item GunsOfTienPost93.P90_Muzzle_Mount_Device (shared with the P90, drawn "
                 "here with the model FIVESEVEN_Muzzle_Mount_Device) and FIVESEVEN_Suppressor, extending along +Y",
        "slide_fired": "FIVESEVEN_SLIDE (drawn through MarzGuns.Slide_Lock / Slide_Fired) back %.0f mm real"
                       % SLIDE_TRAVEL,
        "rail_up/scope/underbarrel": "GoM's pistol parts (Beretta_Mount, PL4 / PM2 / PS1 sights, PJ-3 / PX1 / TR-1 "
                                     "lasers, LP / TL lights) at GoM's Glock 17 relations",
    }
    pts["_extras"] = {
        "handgun_hold": True,
        "photo_origin_mm": [L0, H0],
        "real_mm_per_game_unit": round(1.0 / K, 2),
        "ejection_port_upright": g(100.0, 134.0, -W_SLIDE),
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

    body, slide = build_body(), build_slide()
    mags = [build_magazine(r) for r in (20, 30)]
    supp, mount = build_suppressor(), build_mount()

    kit.unwrap([body, slide], 0.006)
    for o in mags + [supp, mount]:
        kit.unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, slide], [[body, slide], [body, slide]], ["gun", "slide"], 256,
            os.path.join(TEX_DIR, "FIVESEVEN.png"))
    for r, m in zip((20, 30), mags):
        texture([m], [[m]], ["mag%d" % r], 128, os.path.join(TEX_DIR, "57x28Magazine%d_FIVESEVEN.png" % r))
    texture([supp], [[supp]], ["suppressor"], 128, os.path.join(TEX_DIR, "FIVESEVEN_Suppressor.png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "FIVESEVEN_Muzzle_Mount_Device.png"))

    for o in [body, slide] + mags:                      # upside down, as GoM's pistols: 180 degrees about the bore
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in [body, slide] + mags + [supp, mount]}
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")

    kit.export([body, slide], FBX_GUN)
    kit.export(mags, FBX_MAGS)
    kit.export([supp, mount], FBX_PARTS)
    for name, b in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
