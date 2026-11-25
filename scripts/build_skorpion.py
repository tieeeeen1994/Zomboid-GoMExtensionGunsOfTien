"""Skorpion vz. 82 model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_skorpion.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_SKORPION.fbx   SKORPION_BODY, SKORPION_BOLT (the bolt under the top port
                                                          with its two cocking knobs), SKORPION_STOCK_FOLDED /
                                                          _DEPLOYED (the wire stock, drawn in place)
    M/models_X/weapons/magazines/GunsOfTien_SKORPION_magazines.fbx   9x18Magazine12 / 24 / 30_SKORPION
    M/textures/weapons/GunsOfTien/SKORPION.png            256, the gun's four nodes
    M/textures/weapons/GunsOfTien/9x18Magazine<n>_SKORPION.png   128 each
    scripts/skorpion_points.json                          attachment points (game space)

User, 2026-11-26: "For makarov guns, let's add Skorpion and Kedr". The Skorpion in 9x18mm Makarov is the Czechoslovak
army's Sa vz. 82 of 1982 (the vz. 61 rebuilt for the Soviet pistol round: straight steel magazines), so it goes in
the main mod. Its grip is the Skorpion's orange-brown beech one (user, 2026-11-26), on the measuring photo's shape. Held like a pistol and holstered, as the Micro Uzi and the TMP.

Measuring photo: Commons "Sa vz 61 Pistol 9 Makarov.jpg" (CC0; a current Czech Small Arms semi-automatic in the same
calibre, the LEFT side, muzzle left, stock folded, 5841 px; references/skorpion), cut out and traced at half size with
post93/trace_outline.py at 270 mm (10.49 px a mm): scripts/skorpion_reference_outline.json. Profiles are in that
photo's (L, H) mm: L back from the muzzle, H up from the lowest point (the base of the photo's 20-round polymer
magazine, which the vz. 82 never had).

**The photo is a phone's, taken from about 450 mm**: the far stock arm shows 10 mm inboard of the near one. So a
point z mm nearer the lens than the gun's middle plane is drawn (1 + z / (D - z)) times further from the lens axis
(photo L 134, H 92). `rl()` takes a photo point at a known depth back to real millimetres, `fix()` does it for a
slab's traced outline (edges facing away from the axis are the near face's, edges facing it the far face's), and
render_skorpion.py renders the model through the same lens for the outline check. Against the published figures the
middle plane then comes out 0.7-2 % small (sight radius 147 for 148 mm, folded 264.5 for 270, open 510 for 517), so
the gun's nodes are exported at 1.012 (`SCALE`).

The vz. 82's own parts are from modernfirearms.net's photo of one with its three magazines (raw/mf_004.jpg): steel
magazines of 12, 24 and 30 rounds, 100 / 158 / 187 mm (4.8 mm a round), 29.5 mm front to back with two long pressed
ribs a side; the selector marked 20 / 0 / 1. Widths from Rock Island's rear and 3/4 views of vz. 61 pistols (lots
2044/364, 2075/711): the upper 31 mm with 4 mm chamfers, the frame 24, the grip 29; 43 mm over the cocking knobs
(published).

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): +Y muzzle, +Z top, +X the gun's LEFT, origin at the rear-top of
the pistol grip (here the hollow under the grip's tang), 0.603 of real size. Held like a pistol, so the gun's nodes
are modelled and baked upright and turned 180 degrees about the bore axis at export with their points; the magazines
stay upright and get TURN at their point.
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
sys.path.insert(0, os.path.join(HERE, "post93"))
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTien")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SKORPION.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SKORPION_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "skorpion_points.json")

K = 0.000603
K_OLD = 0.00072
SCALE = 1.012                      # the gun's nodes: the photo's middle plane against the published lengths
KG = K * SCALE
MATS = ["steel", "grip", "dark", "bolt", "mag", "brass", "copper"]
kit.MATS[:] = MATS
ZERO = [0.0, 0.0, 0.0]

# the photo's lens: its axis meets the gun's middle plane at (AX_L, AX_H), D_CAM mm away
D_CAM, AX_L, AX_H = 450.0, 134.0, 92.0
# photo (L, H) of the model origin: the hollow under the grip's tang. game y = L0 - L, z = H - H0.
L0, H0 = 248.0, 112.0
BORE = 155.0
W_UPPER, W_FRAME, W_GRIP = 16.0, 12.0, 14.5
CHAMFER = 2.4                      # the upper's top and bottom edges
ARM_X, ARM_H, WIRE_R = 17.3, 175.0, 2.9   # the stock's two arms over the upper's top edges; 5.8 mm wire
ARCH_H = 153.0                     # where the butt's uprights turn into the arch over the barrel
PIVOT = (258.5, 150.2)             # the stock's hinge pin (real L, H)
STOCK_OPEN = 190.0                 # degrees from folded to open: the arms slope 10 degrees down to the butt
MAG = (133.5, 147.5)               # the magazines' feed lips (axis straight down)
KNOB = (78.5, 163.0)               # the cocking knobs (real L, H), one a side on the bolt
BOLT_TRAVEL = 55.0
PORT = (88.0, 134.0, 6.5)          # the ejection port in the top: L front, L rear, half width
TOP = 173.8                        # the upper's flat top (real H)
SEAM = 146.6                       # the upper's bottom edge on the frame


def rl(L, H, z=0.0):
    """A photo point z mm nearer the lens than the middle plane -> real (L, H)."""
    m = D_CAM / (D_CAM - z)
    return AX_L + (L - AX_L) / m, AX_H + (H - AX_H) / m


def fix(outline, half):
    """A slab's traced outline -> real. An edge facing away from the lens axis is drawn by the slab's near face
    (z = +half), one facing it by the far face, one running along the line to the axis by neither: z = half x the
    cosine between the vertex's outward normal and its direction from the axis (a hard near / far switch made the
    outline cross itself at small steps)."""
    n = len(outline)
    area = sum(outline[i][0] * outline[(i + 1) % n][1] - outline[(i + 1) % n][0] * outline[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = outline[i - 1], outline[i], outline[(i + 1) % n]
        e1, e2 = math.hypot(bx - ax, by - ay) or 1.0, math.hypot(cx - bx, cy - by) or 1.0
        nx = s * ((by - ay) / e1 + (cy - by) / e2)
        ny = -s * ((bx - ax) / e1 + (cx - bx) / e2)
        nl, rd = math.hypot(nx, ny) or 1.0, math.hypot(bx - AX_L, by - AX_H) or 1.0
        out.append(rl(bx, by, half * (nx * (bx - AX_L) + ny * (by - AX_H)) / (nl * rd)))
    return out


# ==================================================================================================
# Profiles (photo L, H mm) read off the traced outline and 8-9 px a mm gridded crops
# ==================================================================================================

# the upper receiver's slanted front edge on its side face (photo): bottom, top
UPPER_FRONT_M = ((55.5, 148.5), (60.5, 175.9))
# the rear cap with the hinge lug behind it (the stock's eyes sit outside the lug)
REAR_CAP_M = [(229.0, 148.5), (230.5, 142.0), (233.0, 139.0), (250.5, 139.3), (254.3, 140.8), (258.3, 142.8),
              (260.9, 144.3), (264.9, 145.5), (268.2, 147.5), (269.9, 151.2), (269.9, 154.1), (269.2, 156.3),
              (267.9, 158.1), (266.0, 159.5), (262.0, 160.3), (253.5, 160.8), (252.0, 165.0), (250.5, 169.5),
              (248.0, 173.8), (244.5, 176.5), (229.0, 176.7)]
FRAME_M = [(56.0, 149.5), (53.8, 140.0), (54.2, 138.0), (56.3, 137.0), (64.9, 136.6), (76.5, 135.6), (88.0, 135.0),
           (93.0, 133.8), (95.3, 132.9), (98.2, 130.3), (100.6, 129.4), (103.6, 126.5), (107.3, 124.8),
           (112.5, 123.9), (117.2, 122.3), (143.0, 119.6), (150.3, 118.3), (150.3, 113.2), (163.6, 112.9),
           (166.5, 113.0), (187.8, 112.2), (198.1, 111.6), (199.3, 110.1), (199.4, 91.5), (199.3, 83.4),
           (213.0, 83.4), (213.0, 110.0), (240.0, 110.0), (240.0, 115.0), (260.6, 115.0), (260.6, 118.1),
           (259.7, 120.1), (258.2, 121.1), (253.4, 123.2), (251.9, 124.6), (250.6, 126.7), (250.1, 128.5),
           (250.2, 139.3), (250.2, 149.5)]
# the plastic grip: a wider block under the frame down to its ledge, the hand's part below it
GRIP_TOP_M = [(204.6, 117.2), (260.5, 117.4), (262.3, 115.6), (262.3, 114.2), (261.7, 112.3), (259.3, 111.7),
              (256.1, 110.2), (253.1, 107.7), (251.8, 106.2), (250.3, 103.8), (249.4, 101.7), (248.9, 99.6),
              (248.7, 97.2), (249.4, 93.3), (251.2, 88.4), (204.6, 88.4)]
GRIP_M = [(206.5, 96.0), (248.9, 96.0), (249.4, 93.3), (252.8, 84.4), (256.2, 74.3), (257.9, 67.0), (259.5, 59.9),
          (260.9, 52.6), (261.9, 44.4), (262.5, 36.5), (262.8, 30.0), (262.3, 27.4), (260.8, 26.0), (257.7, 25.4),
          (214.6, 25.4), (212.3, 27.8), (212.9, 47.3), (213.8, 70.0), (213.6, 71.8), (212.6, 75.2), (210.2, 79.3),
          (208.2, 81.6), (206.5, 84.0)]
GUARD_IN_M = [(166.8, 115.5), (165.8, 112.2), (163.1, 109.7), (161.2, 106.6), (160.2, 103.7), (159.9, 99.9),
              (160.4, 96.5), (161.8, 92.9), (163.9, 90.1), (165.8, 88.3), (167.3, 87.4), (169.3, 86.4),
              (172.6, 85.6), (178.7, 85.3), (194.7, 85.2), (200.5, 85.2)]
GUARD_T = 1.7
TRIGGER_M = [(188.4, 115.0), (188.6, 109.0), (188.8, 103.9), (188.5, 101.7), (187.9, 99.7), (186.6, 96.9),
             (184.9, 94.4), (181.8, 90.7), (182.8, 89.7), (184.2, 90.3), (187.8, 93.4), (190.0, 96.0),
             (191.8, 99.1), (193.3, 103.8), (193.5, 106.1), (193.2, 110.4), (193.4, 115.0)]
# the selector on the frame's left: its pivot and the tip of its lever (photo, on the frame's face)
SELECTOR_M = ((217.5, 137.5), (238.5, 129.0))
MAG_CATCH_M = (151.0, 133.5)       # the ribbed button on the left
PIN_HEAD_M = (104.5, 134.0)        # the takedown pin's head at the frame's front
RIBS_M = (202.5, 222.5)            # the two pressed ribs round the upper's rear
FRONT_SIGHT = (64.3, 74.3, 184.4)  # the ears: L front, L rear, H top (middle plane)
REAR_SIGHT = (207.0, 221.0, 180.0)


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="steel", bevel=0.0, xf=None):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel, xf=xf)


def gp(L, H, x=0.0):
    return [round(x * KG, 4) + 0.0, round((L0 - L) * KG, 4) + 0.0, round((H - H0) * KG, 4) + 0.0]


def tube(b, path, r, seg=8, mat="steel", xf=None):
    """A round wire along a 3D polyline [(x, y, z)] in game mm (parallel-transported rings, capped ends)."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    t_prev = (pts[1] - pts[0]).normalized()
    ref = Vector((1.0, 0.0, 0.0)) if abs(t_prev.x) < 0.9 else Vector((0.0, 0.0, 1.0))
    u = t_prev.cross(ref).normalized()
    v = t_prev.cross(u).normalized()
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            t = t_prev
        elif i == n - 1:
            t = (pts[i] - pts[i - 1]).normalized()
        else:
            t = ((pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()).normalized()
        axis = t_prev.cross(t)
        if axis.length > 1e-9:
            rot = Matrix.Rotation(t_prev.angle(t), 3, axis.normalized())
            u, v = rot @ u, rot @ v
        t_prev = t
        rings.append([b.bm.verts.new(p + u * (r * math.cos(2 * math.pi * k / seg))
                                     + v * (r * math.sin(2 * math.pi * k / seg))) for k in range(seg)])
    faces = []
    for ra, rb in zip(rings, rings[1:]):
        for k in range(seg):
            k1 = (k + 1) % seg
            faces.append(b.bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    faces.append(b.bm.faces.new(rings[0][::-1]))
    faces.append(b.bm.faces.new(rings[-1]))
    return b._finish([w for ring in rings for w in ring], faces, mat, 0.0, xf)


def arc(c, r, a0, a1, steps):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def upper_section(xa, xb, grow=0.0):
    """The upper's cross-section between x = xa and xb (xb = W_UPPER: out to the chamfered side), as (x, z) game
    mm; `grow` moves the outside out (the pressed ribs)."""
    w, c, t, s = W_UPPER + grow, CHAMFER, TOP + grow - H0, SEAM - H0
    if xb < w:
        return [(xa, s), (xb, s), (xb, t), (xa, t)]
    return [(xa, s), (w - c, s), (w, s + c), (w, t - c), (w - c, t), (xa, t)]


def mirror(sec):
    return [(-x, z) for x, z in sec][::-1]


def build_body():
    b = kit.Builder()
    y = lambda L: L0 - L  # noqa: E731
    zb = BORE - H0
    # the barrel and the round front cap it screws into
    b.lathe("y", (0, 0, zb), [(y(66.0), 0), (y(66.0), 13.1), (y(42.0), 13.1), (y(39.6), 12.0), (y(38.4), 9.5),
                              (y(37.6), 6.3), (y(36.5), 5.3), (y(1.2), 5.3), (y(0.5), 4.6), (y(0.5), 0)],
            seg=20, mat="steel", phase=0.5)
    # the upper: full sections ahead of and behind the top ejection port, two rails beside it
    (fbL, _), (ftL, _) = (rl(L, H, W_UPPER) for L, H in UPPER_FRONT_M)
    rail = upper_section(PORT[2], W_UPPER)
    b.prism("y", rail, y(238.0), y(ftL), mat="steel")
    b.prism("y", mirror(rail), y(238.0), y(ftL), mat="steel")
    lid = upper_section(-PORT[2], PORT[2])
    b.prism("y", lid, y(PORT[0]), y(ftL), mat="steel")
    b.prism("y", lid, y(238.0), y(PORT[1]), mat="steel")
    # the upper's nose over the barrel cap, under the folded stock's front bend (user, 2026-11-26: light showed
    # between the cap, the bend and the slanted face; in the photo the far arm's bend fills it)
    b.prism("x", [(y(L), H - H0) for L, H in ((67.0, 164.0), (67.0, TOP), (49.1, 174.6), (44.0, 173.6),
                                               (40.0, 171.2), (39.6, 164.0))], -(W_UPPER - CHAMFER),
            W_UPPER - CHAMFER, mat="steel", bevel=0.8)
    # the slanted front face over the cap
    b.prism("x", [(y(fbL), SEAM - H0), (y(ftL), TOP - H0), (y(ftL), SEAM - H0)], -(W_UPPER - CHAMFER),
            W_UPPER - CHAMFER, mat="steel")
    slab(b, fix(REAR_CAP_M, 15.0), half=15.0, bevel=2.2, res=1)
    rib = upper_section(0.0, W_UPPER, 1.0)
    for Lm in RIBS_M:                                     # the pressed ribs: round the top and down both sides
        Lr = rl(Lm, 160.0, W_UPPER)[0]
        b.prism("y", mirror(rib)[:-1] + rib[:-1], y(Lr + 1.6), y(Lr - 1.6), mat="steel", bevel=0.5)
    # the frame, the plastic grip, the guard's strap and the trigger
    slab(b, fix(FRAME_M, W_FRAME), half=W_FRAME, bevel=1.2)
    slab(b, fix(GRIP_TOP_M, W_GRIP + 0.8), half=W_GRIP + 0.8, bevel=2.2, res=1, mat="grip")
    slab(b, fix(GRIP_M, W_GRIP - 0.5), half=W_GRIP - 0.5, bevel=4.0, res=1, mat="grip")
    gi = GUARD_IN_M
    go = []
    for i, (L, H) in enumerate(gi):                       # the strap: the opening's edge moved out by its thickness
        (ax, ay), (cx, cy) = gi[max(i - 1, 0)], gi[min(i + 1, len(gi) - 1)]
        dx, dy = cx - ax, cy - ay
        d = math.hypot(dx, dy)
        go.append((L + GUARD_T * dy / d, H - GUARD_T * dx / d))
    b.strip(PL(go), PL(gi), -5.0, 5.0, mat="steel", bevel=0.4)
    slab(b, TRIGGER_M, half=2.6, bevel=0.6, mat="dark")
    # sights: the front post between two ears, the rear flip leaf lying between the folded stock's arms
    fa, fb, ft = FRONT_SIGHT
    box(b, fa - 2.0, fb + 2.0, TOP - 0.5, TOP + 2.2, -6.0, 6.0, bevel=0.6)
    for xs in (1.0, -1.0):
        slab(b, [(fa, TOP + 1.0), (fa, ft - 2.5), (fa + 2.5, ft), (fb - 2.5, ft), (fb, ft - 2.5), (fb, TOP + 1.0)],
             half=1.0, bevel=0.4, x0=xs * 4.6)
    b.lathe("z", (0, y((fa + fb) / 2.0), 0), [(TOP + 1.0 - H0, 1.2), (ft - 1.5 - H0, 1.0), (ft - 1.5 - H0, 0)],
            seg=8, mat="steel")
    ra, rb, rt = REAR_SIGHT
    box(b, ra, rb, TOP - 0.5, TOP + 1.6, -5.0, 5.0, bevel=0.5)
    b.lathe("x", (0, y((ra + rb) / 2.0 + 1.0), TOP + 0.5 - H0), [(-1.4, 0), (-1.4, rt - TOP - 0.5), (1.4, rt - TOP - 0.5),
                                                                 (1.4, 0)], seg=14, mat="steel")
    # the selector on the left: a pivot boss and its lever, lying towards "1"
    (pL, pH), (tL, tH) = (rl(L, H, W_FRAME + 1.5) for L, H in SELECTOR_M)
    b.lathe("x", (0, y(pL), pH - H0), [(W_FRAME - 0.5, 0), (W_FRAME - 0.5, 3.6), (W_FRAME + 2.6, 3.6),
                                       (W_FRAME + 3.2, 3.0), (W_FRAME + 3.2, 0)], seg=14, mat="steel")
    d = math.hypot(tL - pL, tH - pH)
    ux, uy = (tL - pL) / d, (tH - pH) / d

    def lv(a, w):                                         # a mm along the lever from its pivot, w mm across it
        return pL + ux * a + uy * w, pH + uy * a - ux * w

    lever = [lv(-2.4, 2.2), lv(d - 5.0, 2.2), lv(d - 4.0, 3.3), lv(d - 0.8, 3.3), lv(d, 2.5), lv(d, -2.5),
             lv(d - 0.8, -3.3), lv(d - 4.0, -3.3), lv(d - 5.0, -2.2), lv(-2.4, -2.2)]
    slab(b, lever, half=1.4, bevel=0.5, mat="steel", x0=W_FRAME + 2.2)
    # the magazine catch (a ribbed button) and the takedown pin's head on the left; the pin's other end on the right
    cL, cH = rl(*MAG_CATCH_M, W_FRAME + 1.0)
    b.lathe("x", (0, y(cL), cH - H0), [(W_FRAME - 0.5, 0), (W_FRAME - 0.5, 4.4), (W_FRAME + 2.0, 4.4),
                                       (W_FRAME + 2.6, 3.6), (W_FRAME + 2.6, 0)], seg=14, mat="steel")
    hL, hH = rl(*PIN_HEAD_M, W_FRAME + 0.6)
    b.lathe("x", (0, y(hL), hH - H0), [(-(W_FRAME + 1.0), 0), (-(W_FRAME + 1.0), 2.6), (W_FRAME - 0.5, 2.6),
                                       (W_FRAME - 0.5, 3.8), (W_FRAME + 1.3, 3.8), (W_FRAME + 1.7, 3.2),
                                       (W_FRAME + 1.7, 0)], seg=14, mat="steel")
    # the lanyard loop under the grip
    loop = [(0.0, y(L), H - H0) for L, H in arc((228.2, 21.0), 3.6, 60.0, 480.0, 14)]
    tube(b, loop, 1.0, seg=6, mat="steel")
    box(b, 225.5, 231.0, 23.5, 26.5, -2.0, 2.0, mat="steel", bevel=0.4)
    return b.to_object("SKORPION_BODY")


def build_bolt():
    """The bolt under the top port (its top 1.3 mm under the upper's) with the two cocking knobs fixed to it; all of
    it runs back on every shot (bolt_fired)."""
    b = kit.Builder()
    y = lambda L: L0 - L  # noqa: E731
    box(b, PORT[0] - 8.0, PORT[1] + 14.0, 150.5, TOP - 1.3, -(PORT[2] - 0.2), PORT[2] - 0.2, mat="bolt", bevel=0.6)
    kL, kH = KNOB
    for xs in (1.0, -1.0):
        prof = [(5.0, 0), (5.0, 2.4), (W_UPPER + 1.2, 2.4), (W_UPPER + 1.2, 7.3), (W_UPPER + 4.6, 7.3),
                (W_UPPER + 6.0, 5.8), (W_UPPER + 6.0, 0)]
        b.lathe("x", (0, y(kL), kH - H0), [(xs * t, r) for t, r in prof][::-1 if xs < 0 else 1], seg=16, mat="dark")
    return b.to_object("SKORPION_BOLT")


def stock_path():
    """The folded stock's wire, one continuous run: left eye, up the leg, forward along the upper, down, round the
    butt's U, up, over the barrel in an arch, and back the same way on the right. Real (x, L, H)."""
    pL, pH = PIVOT
    side = [(pL - 0.2, pH + 5.0), (257.3, 164.0)]
    side += arc((251.1, ARM_H - 6.2), 6.2, 0.0, 90.0, 5)                 # the rear bend
    side += arc((49.1, ARM_H - 14.0), 14.0, 90.0, 180.0, 8)              # the front bend, down
    side += arc((22.15, 126.85), 12.95, 0.0, -180.0, 12)                 # the butt's U
    side += [(9.2, ARCH_H)]
    left = [(ARM_X, L, H) for L, H in side]
    over = [(ARM_X * math.cos(math.radians(a)), 9.2, ARCH_H + ARM_X * math.sin(math.radians(a)))
            for a in range(10, 180, 10)]
    return left + over + [(-x, L, H) for x, L, H in left[::-1]]


def build_stock(name):
    """The wire stock in place, folded over the top (main() swings a copy open about the hinge pin)."""
    b = kit.Builder()
    pv = Vector((0.0, L0 - PIVOT[0], PIVOT[1] - H0))
    xf = None
    tube(b, [(x, L0 - L, H - H0) for x, L, H in stock_path()], WIRE_R, seg=8, mat="steel", xf=xf)
    for xs in (1.0, -1.0):
        # the eye on the hinge pin, outside the lug; the knurled collar on the leg
        b.lathe("x", (0, pv.y, pv.z), [(xs * 15.2, 0), (xs * 15.2, 6.3), (xs * 19.4, 6.3), (xs * 20.0, 5.6),
                                       (xs * 20.0, 0)][::-1 if xs < 0 else 1], seg=14, mat="steel", xf=xf)
        b.lathe("z", (xs * ARM_X, L0 - 257.9, 0), [(157.5 - H0, 0), (157.5 - H0, 4.3), (165.0 - H0, 4.3),
                                                   (165.0 - H0, 0)], seg=10, mat="dark", xf=xf)
    # the cross piece between the arms near the hinge (it snaps over the rear sight's base)
    cL = [rl(L, 181.0, ARM_X)[0] for L in (229.5, 245.6)]
    b.box(-(ARM_X + 1.0), ARM_X + 1.0, L0 - cL[1], L0 - cL[0], 173.9 - H0, 179.6 - H0, mat="steel", bevel=1.0, xf=xf)
    return b.to_object(name)


MAG_LEN = {12: 100.0, 24: 158.0, 30: 187.0}   # feed lips to base (raw/mf_004.jpg: 4.8 mm a round)
MAG_W, MAG_D = 10.0, 14.75                    # half width, half depth (29.5 mm front to back)
MAG_BASE = 3.0


def mag_name(r):
    return "9x18Magazine%d_SKORPION" % r


def build_magazine(r):
    """Origin at the feed lips (top centre); the straight steel body down along -Z with two pressed ribs a side, the
    lips narrower at the top, a flat base plate a little proud, the top round with its bullet forward (+Y)."""
    b = kit.Builder()
    L = MAG_LEN[r]
    b.box(-MAG_W, MAG_W, -MAG_D, MAG_D, -(L - MAG_BASE), -6.0, mat="mag", bevel=1.0)
    b.box(-MAG_W + 2.2, MAG_W - 2.2, -MAG_D + 1.5, MAG_D - 3.5, -6.5, 0.0, mat="mag", bevel=0.7)
    b.box(-MAG_W - 0.8, MAG_W + 0.8, -MAG_D - 0.8, MAG_D + 1.6, -L, -(L - MAG_BASE), mat="mag", bevel=0.8)
    for xs in (1.0, -1.0):
        for yc in (-5.2, 4.2):
            b.box(xs * (MAG_W - 0.3), xs * (MAG_W + 0.7), yc - 1.3, yc + 1.3, -(L - MAG_BASE - 8.0), -14.0, mat="mag",
                  bevel=0.45)
    # the catch's notch block on the back, under the lips
    b.box(-4.5, 4.5, -MAG_D - 1.0, -MAG_D + 1.0, -30.0, -17.0, mat="mag", bevel=0.4)
    b.lathe("y", (0, -1.5, -4.2), [(-10.5, 0), (-10.5, 4.95), (4.5, 4.95), (5.0, 4.6)], seg=8, mat="brass")
    b.lathe("y", (0, -1.5, -4.2), [(5.0, 4.6), (8.5, 4.5), (12.5, 2.9), (14.2, 0)], seg=8, mat="copper")
    return b.to_object(mag_name(r))


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: blued steel as GoM's MAC-10 / MP5K (median 37-49), the orange-brown beech grip, the bolt bright
    "steel": (52, 53, 59), "grip": (190, 112, 44), "dark": (30, 30, 33), "bolt": (98, 98, 97),
    "mag": (58, 59, 64), "brass": (150, 118, 62), "copper": (140, 82, 52),
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
    col *= (0.86 + 0.28 * np.clip((p[..., 2] + 60.0) / 130.0, 0.0, 1.0))[..., None]     # lighter towards the top
    occ = (0.62 + 0.38 * np.clip(ao_b, 0, 1) ** 1.5) * (0.66 + 0.34 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 105.0, 30.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.05])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def pin(col, L, H, sel, cL, cH, r=2.0):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.7)] *= 0.4
    col[sel & (d <= r - 0.7)] += 12


def ribs(col, sel, coord, pitch, dark=0.55, light=6.0):
    col[sel & (np.mod(coord, pitch) < pitch * 0.4)] *= dark
    col[sel & (np.mod(coord, pitch) >= pitch * 0.4)] += light


def paint_body(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    side = left | right
    steel = mat == MATS.index("steel")
    upper = steel & side & (np.abs(x) > W_UPPER - 0.6) & (np.abs(x) < W_UPPER + 0.6) & (H > SEAM) & (L > 56.0)
    frame = steel & side & (np.abs(x) > W_FRAME - 0.6) & (np.abs(x) < W_FRAME + 0.6)
    # the cocking slots along both sides of the upper (the knob's stem runs in them), keyholed at the rear
    kL, kH = KNOB
    slot = upper & (L > kL) & (L < 148.5) & (np.abs(H - kH) < 0.9)
    slot |= upper & (np.hypot(L - 148.5, H - kH + 0.6) < 2.7)
    col[slot] = 9
    # the frame's step under the upper, its two pins, the long recessed panel over the magazine well
    fz = W_FRAME
    sL = lambda Lm, Hm: rl(Lm, Hm, fz)  # noqa: E731
    step = sL(140.0, 139.8)[1]
    col[frame & (np.abs(H - step) < 0.5) & (L > sL(95.0, 0)[0]) & (L < sL(190.0, 0)[0])] *= 0.5
    for Lm in (94.0, 104.5):
        pin(col, L, H, frame, *sL(Lm, 143.5), r=1.7)
    (a0, b0), (a1, b1) = sL(111.0, 123.5), sL(141.0, 137.5)
    panel = frame & rounded_rect(L, H, a0, a1, b0, b1, 2.0) & (H > b0 + (a1 - L) * 0.12)
    col[panel] *= 0.72
    pin(col, L, H, frame, *sL(166.5, 129.5), r=1.8)
    (a0, b0), (a1, b1) = sL(90.0, 130.5), sL(103.5, 139.3)
    wedge = frame & (L > a0) & (L < a1) & (H > b0) & (H < b1)
    col[wedge & ((np.mod(L + H, 2.2) < 0.9) | (np.mod(L - H, 2.2) < 0.9))] *= 0.6
    pin(col, L, H, frame, *sL(204.0, 123.5), r=1.6)
    # the bolt catch's oval and pin over the trigger, on the left; the frame's toothed lip behind the magazine
    lf = frame & left
    (a0, b0), (a1, b1) = sL(190.0, 138.3), sL(202.0, 142.0)
    col[lf & rounded_rect(L, H, a0, a1, b0, b1, 1.6)] += 16
    pin(col, L, H, lf, *sL(194.5, 136.0), r=2.9)
    lip = steel & (L > 151.0) & (L < 161.0) & (H > 112.5) & (H < 117.5) & side
    ribs(col, lip, L, 1.4, 0.6, 5.0)
    # the selector's sector under the lever and its 20 / 0 / 1 (white paint), left only
    (pL, pH) = sL(*SELECTOR_M[0])
    sector = lf & (np.abs(np.hypot(L - pL, H - (pH - 4.0)) - 13.2) < 0.45) & (H < pH - 2.0)
    col[sector] *= 0.5
    for Lm, Hm in ((198.0, 128.5), (217.5, 120.3), (241.5, 129.0)):       # 20, 0, 1
        tL, tH = sL(Lm, Hm)
        col[lf & (np.hypot(L - tL, H - tH) < 1.1)] = 150
    # under the open port: the frame's top between the rails; the muzzle's bore
    col[steel & (n[..., 2] > 0.7) & (np.abs(x) < PORT[2]) & (H > 140.0) & (H < TOP - 6.0) & (L > PORT[0] - 10.0)
        & (L < PORT[1] + 10.0)] = 12
    r = np.hypot(x, z - (BORE - H0))
    col[steel & (L < 1.2) & (r < 3.6)] = 6
    # the grip (user, 2026-11-26: "Can we use the brown orange grip for skorpion?"): the lacquered beech grip the
    # Skorpion is known by, orange-brown with the grain running down it and four grooves low on each side (Commons'
    # "Sa vz 61 Skorpion" photos); no ribs on its front or back
    grip = mat == MATS.index("grip")
    gs = grip & side
    gz = W_GRIP
    gL = lambda Lm, Hm: rl(Lm, Hm, gz)  # noqa: E731
    grain = kit.vnoise(p * np.array([1.0, 2.2, 0.16]), 1.7, 11) * 0.6 + kit.vnoise(p * np.array([1.0, 3.0, 0.3]), 0.7, 12) * 0.4
    col[grip] *= (0.78 + 0.44 * grain[grip])[..., None]
    for Lm, top in ((233.0, 71.0), (238.5, 73.0), (243.5, 71.0), (249.5, 60.0)):
        (c0, h0), (_, h1) = gL(Lm, 34.0), gL(Lm, top)
        col[gs & (np.abs(L - c0) < 1.1) & (H > h0) & (H < h1)] *= 0.3


def paint_bolt(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    y, z = p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0
    # the knobs' concentric rings on their faces
    knob = (mat == MATS.index("dark")) & (np.abs(n[..., 0]) > 0.7)
    d = np.hypot(L - KNOB[0], H - KNOB[1])
    col[knob & (np.mod(d, 1.5) < 0.6)] *= 0.5
    col[knob & (np.mod(d, 1.5) >= 0.6)] += 10
    # the bolt's top in the port: the extractor's groove and the ejector's slot
    top = (mat == MATS.index("bolt")) & (n[..., 2] > 0.7)
    col[top & (np.abs(p[..., 0] - 4.5) < 0.6) & (L > PORT[0]) & (L < PORT[0] + 22.0)] *= 0.45
    col[top & (np.abs(L - (PORT[0] + 30.0)) < 0.5)] *= 0.55


def paint_stock(maps, col):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    collar = mat == MATS.index("dark")
    ribs(col, collar, p[..., 0] * 3.0 + p[..., 1] * 3.0, 1.6, 0.6, 8.0)
    L, H = L0 - p[..., 1], p[..., 2] + H0
    d = np.hypot(L - PIVOT[0], H - PIVOT[1])
    eye = (mat == MATS.index("steel")) & (np.abs(n[..., 0]) > 0.7) & (d < 6.0)
    col[eye & (d < 3.0) & (d > 2.3)] *= 0.45
    col[eye & (d < 2.3) & (np.abs(H - PIVOT[1]) < 0.45)] *= 0.35


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


# ==================================================================================================
# Attachment points
# ==================================================================================================

def repack(objects, shrink, margin):
    """Pack the objects' UV islands again with the `shrink` objects' islands scaled down first (thin wire takes a
    third of the atlas at equal texel density and shows none of it) and islands turned by quarter turns only: at
    256 px a texel is over a millimetre, and an island lying at an odd angle turns straight ribs into staircases."""
    for o, f in shrink.items():
        uv = o.data.uv_layers.active.data
        for d in uv:
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
        "muzzle": {"offset": gp(0.5, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(*MAG), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-BOLT_TRAVEL * KG, 4), 0.0], "rotate": ZERO},
    }
    notes = {
        "magazine": "9x18Magazine12 / 24 / 30_SKORPION hang straight down from here (their feed lips)",
        "bolt_fired": "SKORPION_BOLT (the bolt under the top port with both cocking knobs) back %.0f mm real: each "
                      "shot and held open when empty (GoM's Bolt_Fired)" % BOLT_TRAVEL,
        "stocks": "SKORPION_STOCK_FOLDED / _DEPLOYED are drawn in place (no point): the wire stock over the top, "
                  "or swung %.0f degrees up and back about its hinge pin" % STOCK_OPEN,
    }
    # held like a pistol: everything turned with the gun; the magazine gets TURN; GoM's MP5K floor pose
    pts = {k: kit.turned(v) for k, v in pts.items()}
    pts["magazine"]["rotate"] = list(kit.TURN)
    pts["world"] = {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": ZERO}
    pts["_notes"] = dict(notes, units="game units (0.603 of real size, the M16A2's proportion; this gun's nodes x "
                         "%.3f, see build_skorpion.py); +Y muzzle; held like a pistol, so modelled upside down as "
                         "GoM's MP5K / MAC-10: +Z the gun's BOTTOM, +X its RIGHT; origin = the hollow under the "
                         "grip's tang (photo L %.0f, H %.0f)" % (SCALE, L0, H0))
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": KG,
                      "lens_mm": [D_CAM, AX_L, AX_H], "pivot_mm": list(PIVOT)}
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

    kit.K = KG
    body, bolt, folded = build_body(), build_bolt(), build_stock("SKORPION_STOCK_FOLDED")
    weighted_normals([body, bolt])
    kit.unwrap([body, bolt, folded], 0.006)
    repack([body, bolt, folded], {folded: 0.55}, 0.006)
    # the bolt and the stock are baked with the body only (they move or swap)
    maps = [bake(body, [body, bolt, folded], 256), bake(bolt, [body, bolt], 256), bake(folded, [body, folded], 256)]
    texture(maps, ["body", "bolt", "stock"], 256, os.path.join(TEX_DIR, "SKORPION.png"))
    # the open stock: the folded one swung about its hinge pin, on the same texels (FBX data z is game -z, so the
    # turn about X runs the other way there)
    deployed = folded.copy()
    deployed.data = folded.data.copy()
    deployed.name = deployed.data.name = "SKORPION_STOCK_DEPLOYED"
    scene.collection.objects.link(deployed)
    pv = Vector((0.0, (L0 - PIVOT[0]) * KG, -(PIVOT[1] - H0) * KG))
    deployed.data.transform(Matrix.Translation(pv) @ Matrix.Rotation(math.radians(-STOCK_OPEN), 4, 'X')
                            @ Matrix.Translation(-pv))
    gun = [body, bolt, folded, deployed]

    kit.K = K
    mags = [build_magazine(r) for r in MAG_LEN]
    for m in mags:
        kit.unwrap([m], 0.012)
        repack([m], {}, 0.012)
    for r, m in zip(MAG_LEN, mags):
        texture([bake(m, [m], 128)], [r], 128, os.path.join(TEX_DIR, m.name + ".png"))

    for o in gun:                                      # held like a pistol: turned 180 degrees about the bore
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: kit.bounds_of(o) for o in gun}
    bounds["SKORPION_BOLT_fired"] = kit.bounds_of(bolt, (0, -BOLT_TRAVEL * KG, 0))
    pts = points(bounds)
    pts["_mags"] = {m.name: kit.bounds_of(m) for m in mags}
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export(mags, FBX_MAGS)
    for name, bd in list(bounds.items()) + list(pts["_mags"].items()):
        print("%-28s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
