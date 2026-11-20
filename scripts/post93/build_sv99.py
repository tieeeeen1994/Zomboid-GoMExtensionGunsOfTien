"""Izhmash SV-99 (.22 LR) in its green plywood and black polymer stocks, for Guns of Tien - Post-93 (Blender 5.2).

    blender -b --factory-startup -P scripts/post93/build_sv99.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_SV99.fbx   SV99_BODY, SV99_BOLT, SV99_BIPOD_FOLDED / _DEPLOYED (green
                                                            plywood) and SV99P_BODY, SV99P_BOLT, SV99P_BIPOD_* (polymer)
    M/models_X/weapons/magazines/GunsOfTienPost93_SV99_magazines.fbx   22LRMagazine5_SV99
    M/textures/weapons/GunsOfTienPost93/SV99.png, SV99P.png     512 atlases (stock and metal)
    M/textures/weapons/GunsOfTienPost93/22LRMagazine5_SV99.png  128
    scripts/post93/sv99_points.json                             attachment points of both guns (game space)

User, 2026-11-20 (docs/sv98_sv99_svu_research.md, docs/post93_design.md "SV-98 and SV-99"): Izhmash's .22 LR sniper
rifle (shown 1999, FSB 2004, MVD 2005), Post-93: the BI-7-2 biathlon rifle's straight-pull toggle action with its
lever on the right, a 350 mm barrel, the factory baffle suppressor (built in: the SV-99 is never seen without it), a
small 5-round magazine standing out under the stock, a two-stage trigger in a metal guard (the push-button safety
at its front is left off: user, 2026-11-20), a rail on the receiver (no iron sights), a folding bipod under the forend. Two stocks of the
same barrelled action: the green laminated plywood one of 2007-2009 (the SV-98's stock made shorter: thumbhole, a
skeleton butt with two windows, a comb on posts, a hooked butt plate) and the black polymer one of 2009 on (an open
butt frame with one large opening and a slot, a box cheek riser, a horned butt plate, a slab-sided forend). The early
lacquered wooden stock (1999-2006) is not built: its photos are all small.

References (references/sv99): green: zonawar's studio right side, green_plywood/b2_003.jpg (2048 px, 1.862 px a mm over
its 1030 mm, butt plate to suppressor); polymer: Kalashnikov's catalogue left side, black_polymer/kalash_SV-99_2.jpg
(2120 px, mirrored, 1.530 px a mm). Read column by column (the stock's green or black, their tops, bottoms and holes)
and on mm grids. Each stock's outline is in its photo's (L, R) mm (L forward from the butt's rear, R down); both are
registered on the trigger blade (T) and the bore's row, so the action, barrel and suppressor are one set of numbers in
action mm (A forward of the trigger, D down from the bore). Origin as the SV-98's (GoM's M24's against its trigger
and bore): the trigger 57.5 mm ahead of it, the bore 16 mm over it.
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
import build_sv98 as sv98  # noqa: E402   (its paint helpers: plywood, the shared shading)

MEDIA = kit.MEDIA
TEX_DIR = kit.TEX_DIR
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_SV99.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_SV99_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "sv99_points.json")
MAG_NAME = "22LRMagazine5_SV99"

K = 0.000603
MATS = ["wood", "rubber", "metal", "silver", "dark", "magpoly", "stipple", "rail", "poly", "red"]
kit.MATS[:] = MATS
TRIGGER_Y, BORE_Z = 57.5, 16.0          # the SV-98's origin rule (GoM's M24)

# ---------------------------------------------------------------------------------------------- the action (A, D mm)
# read off the catalogue photo (black_polymer/kalash_SV-99_2.jpg, mirrored) where it shows them, the lever, port and
# magazine off the green one (right side); both registered on the trigger blade (overlays, 2026-11-20)
RECEIVER = (-36.0, 188.0, 15.0)          # A from, to, radius (round, on the bore)
RAIL = (-23.0, 93.0)
BARREL = (188.0, 472.0, 9.0)
CAN = [(470, 0.0), (470, 12.0), (476, 14.0), (510, 14.0), (512, 16.5), (637, 16.5), (640, 14.5), (640, 6.0),
       (634, 3.5), (634, 0.0)]           # the baffle can: its knurled rear band, the body, the front cap's bore
LEVER_PIVOT = (-8.0, -6.0)               # the toggle lever's pivot on the receiver's right (A, D)
LEVER = [(-16.0, -11.0), (0.0, -11.0), (0.0, 48.0), (-4.0, 51.0), (-12.0, 51.0), (-16.0, 47.0)]
LEVER_SWING = -62.0                      # degrees about x: the lever's end back (bolt_fired)
PORT = (-10.0, 84.0, -11.5, -2.5)        # the bright bolt / port strip along the receiver's right
MAG = (98.0, 130.0, 25.0, 96.5, 7.0)     # A from, to, D top (lips), D floor, half width


def A_to_game(A, D):
    return A + TRIGGER_Y, BORE_Z - D


# ---------------------------------------------------------------------------------------------- the stocks
# Each in its photo's (L, R) mm. T = the trigger blade's middle, BORE = the bore's row.
STOCKS = {
    "SV99": {   # green plywood, green_plywood/b2_003.jpg (right side)
        "T": 387.0, "BORE": 51.5, "mat": "wood", "half": 21.0, "joint": [(330, 55), (366, 55), (366, 118), (330, 118)],
        "body": [(58, 65), (330, 65), (345, 58), (360, 56), (520, 55.5), (700, 56.5), (835, 57.5), (845, 64),
                 (846, 78), (840, 87.5), (820, 90), (810, 97.2), (700, 102.6), (600, 108), (500, 112.8),
                 (420, 116), (395, 110), (360, 108), (342, 117), (336, 150), (332, 205), (320, 211), (300, 212),
                 (290, 210), (280, 206), (270, 200), (260, 191), (250, 184), (240, 181.5), (230, 184), (220, 185.3),
                 (210, 188.5), (200, 190), (190, 192.8), (180, 195), (170, 197), (140, 198), (130, 203), (58, 203)],
        "holes": [("circle", 241.0, 110.0, 29.0), ("rect", 82, 136, 94, 161, 8), ("rect", 147, 190, 94, 161, 8)],
        "comb": [(56, 54), (56, 42), (62, 38), (220, 38), (233, 42), (226, 54)], "comb_half": 17.0,
        "posts": [(108, 122), (160, 174)], "posts_r": (54, 65),
        "pad": [(5, 40), (45, 38), (48, 46), (30, 52), (26, 60), (24, 175), (18, 182), (8, 180), (2, 170), (10, 60),
                (3, 48)],
        "adjuster": [(24, 52), (58, 48), (60, 203), (26, 205)],
        "stipple": [(256, 118), (322, 118), (330, 150), (326, 204), (290, 208), (262, 192), (252, 150)],
        "bipod": (790.0, 97.0),
        "photo": "references/sv99/green_plywood/b2_003.jpg",
        # the trigger group traced off the photo (x 660-880, y 330-480 at 7.4 px a mm; user, 2026-11-20: "completely
        # wrong"): the steel guard's outer and inner edges from the stock down round and up into it (smoothed by
        # corner cutting at build time), the blade a hook from the stock's bottom (its root inside), its back
        # bulging rearward and its tip forward
        "guard_out": [(365.5, 106.0), (366.8, 114.1), (368.8, 126.2), (373.5, 136.9), (380.2, 142.3), (391.0, 144.3),
                      (403.1, 143.7), (412.5, 139.6), (419.2, 131.6), (421.2, 122.2), (422.1, 115.5), (422.5, 108.0)],
        "guard_in": [(373.5, 106.0), (373.5, 114.1), (372.9, 123.5), (375.5, 132.9), (381.6, 138.3), (391.0, 140.3),
                     (401.7, 139.6), (409.8, 136.3), (415.1, 130.2), (417.8, 122.2), (418.5, 116.1), (418.5, 108.0)],
        # the blade as a centre line from its root (inside the stock) to the tip, with its width (L, R, width mm):
        # the midpoints and spans of the traced front and back edges, a broad crescent tapering to a point
        "blade": [(393.0, 104.0, 5.6), (388.6, 113.6, 4.8), (385.2, 118.8, 4.0), (384.0, 125.5, 2.8), (385.0, 131.9, 1.9),
                  (387.4, 136.2, 1.0), (388.5, 137.4, 0.3)],
        "trigger_mat": "silver",
    },
    "SV99P": {  # black polymer, black_polymer/kalash_SV-99_2.jpg (left side, mirrored)
        "T": 395.0, "BORE": 46.0, "mat": "poly", "half": 20.0, "joint": [(333, 52), (369, 52), (369, 111), (333, 111)],
        "body": [(72, 66), (260, 66), (270, 72), (300, 74), (320, 70), (345, 62), (370, 56), (440, 40),
                 (830, 37), (836, 46), (834, 70), (826, 80), (780, 83.6), (700, 88), (600, 94), (500, 105),
                 (445, 107), (350, 104.5), (343, 110), (338, 195), (300, 194), (265, 190), (150, 190), (142, 200),
                 (72, 200)],
        "holes": [("poly", [(137, 113), (146, 104), (294, 104), (300, 110), (289, 160), (280, 165), (146, 165),
                            (137, 156)]),
                  ("rect", 100, 116, 115, 150, 7.5)],
        "riser": [(145, 104), (145, 46), (150, 42), (256, 42), (262, 46), (262, 104)], "riser_half": 16.0,
        "pad": [(38, 58), (53, 56), (53, 198), (38, 198)],
        "horns": [[(18, 50), (52, 52), (52, 59), (22, 56)], [(0, 208), (50, 193), (52, 200), (2, 214)]],
        "adjuster": [(53, 62), (72, 62), (72, 200), (53, 200)],
        "bipod": (800.0, 84.0),
        "photo": "references/sv99/black_polymer/kalash_SV-99_2.jpg",
        # the trigger group traced off the photo (mirrored, x 820-960, y 640-760 at 7.7 px a mm; the blade 1.5 mm forward
        # of the first trace and the underside over the guard raised 4 mm, after a matched overlay)
        "guard_out": [(372.5, 103.0), (373.9, 109.2), (377.1, 117.6), (379.7, 125.5), (385.6, 133.3), (394.8, 136.6),
                      (405.2, 136.6), (414.4, 133.3), (419.6, 126.8), (420.9, 117.6), (420.3, 109.8), (419.0, 103.0)],
        "guard_in": [(380.4, 103.0), (381.0, 108.5), (381.0, 117.6), (383.7, 125.5), (389.5, 130.7), (398.7, 132.7),
                     (404.5, 132.6), (409.2, 131.4), (415.7, 126.8), (418.3, 117.6), (417.0, 108.5), (415.7, 103.0)],
        "blade": [(400.0, 100.0, 3.8), (395.2, 108.8, 3.2), (391.6, 116.3, 2.6), (391.4, 123.5, 1.9), (393.0, 128.5, 1.1),
                  (394.8, 130.5, 0.3)],
        "trigger_mat": "metal",
    },
}


def stock_P(s, L, R):
    return A_to_game(L - s["T"], R - s["BORE"])


def rounded_rect(La, Lb, Ra, Rb, r, n=4):
    pts = []
    for cL, cR, a0 in ((Lb - r, Ra + r, 270.0), (Lb - r, Rb - r, 0.0), (La + r, Rb - r, 90.0), (La + r, Ra + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cL + r * math.cos(a), cR + r * math.sin(a)))
    return pts


def circle(cL, cR, r, n=28):
    return [(cL + r * math.cos(2 * math.pi * k / n), cR + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def hole_points(h):
    if h[0] == "circle":
        return circle(*h[1:])
    if h[0] == "rect":
        return rounded_rect(*h[1:])
    return list(h[1])


def smooth(pts, closed, iters=4):
    """Chaikin corner cutting through the traced points: smooth curves with no overshoot (a Catmull-Rom spline through
    close points spiked), an open line keeping its two ends."""
    P = [Vector(p) for p in pts]
    for _ in range(iters):
        out = [] if closed else [P[0]]
        n = len(P) if closed else len(P) - 1
        for k in range(n):
            a, b = P[k], P[(k + 1) % len(P)]
            out += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        if not closed:
            out.append(P[-1])
        P = out
    return [(p.x, p.y) for p in P]


def resample(pts, n):
    """An open polyline resampled to n points evenly along its length (the guard's two edges must pair up)."""
    P = [Vector(p) for p in pts]
    acc = [0.0]
    for a, b in zip(P, P[1:]):
        acc.append(acc[-1] + (b - a).length)
    out, j = [], 0
    for k in range(n):
        d = acc[-1] * k / (n - 1)
        while j < len(acc) - 2 and acc[j + 1] < d:
            j += 1
        f = (d - acc[j]) / max(acc[j + 1] - acc[j], 1e-9)
        q = P[j].lerp(P[j + 1], f)
        out.append((q.x, q.y))
    return out


def grow(loop, d):
    """A closed, densely sampled outline pushed out by d mm along its vertex normals (its winding found from the signed
    area)."""
    n = len(loop)
    area = sum(loop[i][0] * loop[(i + 1) % n][1] - loop[(i + 1) % n][0] * loop[i][1] for i in range(n))
    sgn = -1.0 if area > 0 else 1.0
    out = []
    for i in range(n):
        a, c = Vector(loop[i - 1]), Vector(loop[(i + 1) % n])
        t = (c - a).normalized()
        nrm = Vector((t.y, -t.x)) * sgn
        out.append(tuple(Vector(loop[i]) + nrm * d))
    return out


def blade_outline(s):
    """The trigger blade's outline: the centre line smoothed, each side offset by half its width along the line's
    normal, the tip closing to a point (a real blade's crescent: no traced kinks)."""
    pts = smooth([(L, R) for L, R, _ in s["blade"]], False, 3)
    ws = smooth([(k, w) for k, (_, _, w) in enumerate(s["blade"])], False, 3)
    centre = [Vector(stock_P(s, L, R)) for L, R in pts]
    left, right = [], []
    for k, c in enumerate(centre):
        a, b = centre[max(k - 1, 0)], centre[min(k + 1, len(centre) - 1)]
        t = (b - a).normalized()
        nrm = Vector((-t.y, t.x))
        w = ws[k][1] / 2.0
        left.append(tuple(c + nrm * w))
        right.append(tuple(c - nrm * w))
    return left + right[::-1]


def gbox(b, A0, A1, D0, D1, x0, x1, mat="metal", bevel=0.0):
    (y0, z0), (y1, z1) = A_to_game(A0, D0), A_to_game(A1, D1)
    return b.box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1), mat=mat, bevel=bevel)


# ---------------------------------------------------------------------------------------------- geometry
def build_body(name):
    s = STOCKS[name]
    b = kit.Builder()
    P = lambda pts: [stock_P(s, L, R) for L, R in pts]
    kit.slab(b, P(s["body"]), [P(hole_points(h)) for h in s["holes"]], s["half"], 3.0, 1, s["mat"], 0.0)
    if "comb" in s:
        kit.slab(b, P(s["comb"]), (), s["comb_half"], 2.5, 1, s["mat"], 0.0)
        for La, Lb in s["posts"]:
            Ra, Rb = s["posts_r"]
            kit.slab(b, P([(La, Ra), (Lb, Ra), (Lb, Rb), (La, Rb)]), (), 5.0, 1.0, 0, "rubber", 0.0)
    if "riser" in s:
        kit.slab(b, P(s["riser"]), (), s["riser_half"], 2.0, 1, "poly", 0.0)
    kit.slab(b, P(s["pad"]), (), s["half"] - 1.0, 2.5, 1, "rubber", 0.0)
    for horn in s.get("horns", []):
        kit.slab(b, P(horn), (), s["half"] - 4.0, 1.0, 0, "rubber", 0.0)
    kit.slab(b, P(s["adjuster"]), (), s["half"] - 2.0, 1.5, 0, "rubber", 0.0)
    kit.slab(b, P(s["joint"]), (), s["half"] + 0.6, 1.2, 0, "metal", 0.0)    # the butt's latch block at the wrist
    # the action: receiver, rail, barrel, the suppressor; the trigger, its guard and safety; the magazine well's
    # mouth is the stock's
    by, bz = A_to_game(0.0, 0.0)
    y = lambda A: A + TRIGGER_Y
    a0, a1, r = RECEIVER
    b.lathe("y", (0.0, 0.0, bz), [(y(a0), 0.0), (y(a0), r - 2.0), (y(a0) + 2.0, r), (y(a1), r), (y(a1), 0.0)], seg=16,
            mat="metal")
    face = bz + r - 1.0
    kit.picatinny(b, y(RAIL[0]), y(RAIL[1]), lambda u, h, yy: Vector((u, yy, face + h)))
    a0, a1, r = BARREL
    b.lathe("y", (0.0, 0.0, bz), [(y(a0), 0.0), (y(a0), r), (y(a1), r), (y(a1), 0.0)], seg=14, mat="metal")
    b.lathe("y", (0.0, 0.0, bz), [(y(A), rr) for A, rr in CAN], seg=18, mat="metal")
    # the trigger and its guard: smooth curves through the traced points, edges rounded (user, 2026-11-20: the
    # straight-segment versions looked "horrendous"; the red safety buttons removed too)
    kit.slab(b, blade_outline(s), (), 2.2, 0.5, 1, s["trigger_mat"], 0.0)
    band = (resample(smooth(P(s["guard_out"]), False), 40) + resample(smooth(P(s["guard_in"]), False), 40)[::-1])
    kit.slab(b, band, (), 4.0, 0.9, 1, "metal", 0.0)
    return b.to_object(name + "_BODY")


def lever_pivot_game():
    py, pz = A_to_game(*LEVER_PIVOT)
    return Vector((-24.0, py, pz))                  # outside the stock's right side (half widths 20-21)


def build_bolt(name):
    """The toggle lever, modelled about its pivot (the node's origin): drawn at `bolt_lock` and swung back at
    `bolt_fired`, both points at the pivot. The bright bolt in the port is painted on the receiver."""
    b = kit.Builder()
    piv = lever_pivot_game()
    pts = [(A_to_game(A, D)[0] - piv.y, A_to_game(A, D)[1] - piv.z) for A, D in LEVER]
    kit.slab(b, pts, (), 2.0, 0.6, 0, "silver", -2.0)
    b.lathe("x", (-3.0, 0.0, 0.0), [(-2.5, 0.0), (-2.5, 4.5), (2.5, 4.5), (2.5, 0.0)], seg=10, mat="metal")
    return b.to_object(name + "_BOLT")


def build_bipod(name, deployed):
    s = STOCKS[name]
    b = kit.Builder()
    hy, hz = stock_P(s, *s["bipod"])
    head = Vector((0.0, hy, hz))
    b.box(-9.0, 9.0, hy - 9.0, hy + 9.0, hz - 7.0, hz + 3.0, mat="metal", bevel=0.8)
    leg = 165.0
    for side in (-1, 1):
        top = head + Vector((side * 6.0, 0.0, -5.0))
        if deployed:
            d = Vector((side * math.sin(math.radians(14.0)), math.sin(math.radians(5.0)), -1.0)).normalized()
        else:
            d = Vector((side * 0.02, -1.0, -0.03)).normalized()
        xf = Matrix.Translation(top) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4()
        b.lathe("y", (0.0, 0.0, 0.0), [(0.0, 0.0), (0.0, 4.0), (leg * 0.55, 4.0), (leg * 0.55, 3.2), (leg, 3.2),
                                        (leg, 0.0)], seg=8, mat="metal", xf=xf)
        foot = top + d * leg
        if deployed:
            b.box(foot.x - 4.0, foot.x + 4.0, foot.y - 12.0, foot.y + 6.0, foot.z - 3.0, foot.z + 1.0, mat="rubber",
                  bevel=0.8)
    return b.to_object(name + ("_BIPOD_DEPLOYED" if deployed else "_BIPOD_FOLDED"))


def build_magazine():
    """The 5-round plastic box, origin at its lips' front (drawn at the guns' `magazine` point)."""
    b = kit.Builder()
    a0, a1, d0, d1, hw = MAG
    top = Vector(A_to_game(a1, d0))
    M = lambda A, D: (A_to_game(A, D)[0] - top.x, A_to_game(A, D)[1] - top.y)
    kit.slab(b, [M(a0, d0 + 2), M(a1, d0), M(a1, d1 - 3), M(a0, d1 - 3)], (), hw, 1.0, 0, "magpoly", 0.0)
    kit.slab(b, [M(a0 - 1.5, d1 - 4), M(a1 + 1.5, d1 - 4), M(a1 + 1.5, d1), M(a0 - 1.5, d1)], (), hw + 1.0, 0.8, 0,
             "magpoly", 0.0)
    return b.to_object(MAG_NAME)


# ---------------------------------------------------------------------------------------------- painting
BASE = dict(sv98.BASE, poly=(30, 31, 33), red=(170, 30, 26))


def paint(maps, kind, name):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, m in enumerate(MATS):
        col[mat == i] = BASE[m]
    x = p[..., 0]
    s = STOCKS[name]
    A, D = p[..., 1] - TRIGGER_Y, BORE_Z - p[..., 2]
    L, R = A + s["T"], D + s["BORE"]
    side = np.abs(n[..., 0]) > 0.6
    wood = mat == MATS.index("wood")
    poly = mat == MATS.index("poly")
    if kind == "gun":
        warp = 14.0 * kit.vnoise(p * np.array([1.0, 0.15, 1.0]), 30.0, 7) + 4.0 * kit.vnoise(p, 6.0, 9)
        band = np.sin((R + warp) * 2 * np.pi / 13.0)
        shade = 0.9 + 0.08 * band + 0.16 * (kit.vnoise(p * np.array([1.0, 0.3, 1.0]), 25.0, 8) - 0.5)
        ws = wood & side
        col[ws] *= shade[ws][..., None]
        we = wood & ~side
        col[we] *= (0.86 + 0.16 * np.sin(x * 2 * np.pi / 3.2)[we])[..., None]
        col[we] += np.array([10.0, 18.0, 14.0])
        if "stipple" in s:
            st = ws & sv98.in_poly(L, R, s["stipple"])
            col[st] = np.array(BASE["stipple"]) * (0.7 + 0.5 * kit.vnoise(p, 0.9, 11))[st][..., None]
        # polymer: a fine matt texture
        col[poly] *= (0.9 + 0.2 * kit.vnoise(p, 0.7, 13))[poly][..., None]
        metal = mat == MATS.index("metal")
        right = n[..., 0] < -0.3
        a0, a1, d0, d1 = PORT
        port = metal & right & (A > a0) & (A < a1) & (D > d0) & (D < d1)
        col[port] = np.array(BASE["silver"]) * (0.8 + 0.25 * kit.vnoise(p, 2.0, 12))[port][..., None]
        # the suppressor's knurled rear band and the front cap's bore
        knurl = metal & (A > 476) & (A < 510) & (np.abs(n[..., 1]) < 0.5)
        col[knurl] *= (0.75 + 0.35 * (kit.vnoise(p, 0.6, 14) > 0.5))[knurl][..., None]
        bore = metal & (n[..., 1] > 0.6) & (A > 628) & (np.hypot(x, D) < 6.5)
        col[bore] = BASE["dark"]
        left = n[..., 0] > 0.3
        col[metal & left & kit.text_mask(-A, -D, "SV-99", -120.0, 5.0, 4.0)] *= 1.6
    elif kind == "mag":
        rib = (mat == MATS.index("magpoly")) & side & (np.sin(D * 2 * np.pi / 6.0) > 0.7)
        col[rib] *= 1.2
    col = sv98.common(maps, col, mat)
    return np.clip(col, 0, 255)


def texture(objects, contexts, kinds, names, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind, name in zip(objects, contexts, kinds, names):
        maps = kit.bake_maps(ob, ctx, bake)
        c = paint(maps, kind, name)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake // size))
    kit.save_png(col, size, path)


# ---------------------------------------------------------------------------------------------- points
def g3(v):
    return [round(c * K, 4) + 0.0 for c in v]


def points(name):
    s = STOCKS[name]
    piv = lever_pivot_game()
    face_top = BORE_Z + RECEIVER[2] - 1.0 + 9.0
    pts = {
        "muzzle": {"offset": g3((0.0, CAN[-3][0] + TRIGGER_Y, BORE_Z)), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": g3((0.0, *A_to_game(MAG[1], MAG[2]))), "rotate": [0.0, 0.0, 0.0]},
        "bolt_lock": {"offset": g3(piv), "rotate": [0.0, 0.0, 0.0]},
        "bolt_fired": {"offset": g3(piv), "rotate": [LEVER_SWING, 0.0, 0.0]},
        "scope": {"offset": [0.0, round((sum(RAIL) / 2.0 + TRIGGER_Y) * K, 4), round(face_top * K - 0.0032, 4)],
                  "rotate": [0.0, 0.0, 0.0]},
        "world": {"offset": [0.0193, 0.1252 * 0.8, 0.0], "rotate": [180.0, 0.0, 180.0]},
    }
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
    out, data = [], {}
    for name in STOCKS:
        objs = [build_body(name), build_bolt(name), build_bipod(name, False), build_bipod(name, True)]
        kit.unwrap(objs, 0.006)
        os.makedirs(TEX_DIR, exist_ok=True)
        texture(objs, [objs] * 4, ["gun", "bolt", "bipod", "bipod"], [name] * 4, 512,
                os.path.join(TEX_DIR, name + ".png"))
        for o in objs:
            o.hide_render = True
        out += objs
        data[name] = points(name)
        data[name]["_bounds"] = {o.name: kit.bounds_of(o) for o in objs}
    mag = build_magazine()
    kit.unwrap([mag], 0.012)
    texture([mag], [[mag]], ["mag"], ["SV99"], 128, os.path.join(TEX_DIR, MAG_NAME + ".png"))
    data["_extras"] = {"origin": "trigger %.1f mm behind, bore %.1f mm under (GoM's M24 rule)" % (TRIGGER_Y, BORE_Z),
                       "real_mm_per_game_unit": round(1.0 / K, 2), "mag_bounds": kit.bounds_of(mag)}
    kit.export(out, FBX_GUN)
    kit.export([mag], FBX_MAGS)
    with open(POINTS_JSON, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    for name in STOCKS:
        for o, bb in data[name]["_bounds"].items():
            print("%-24s tris %5d  min %s  max %s" % (o, bb["tris"], bb["min"], bb["max"]))
    print("mag", data["_extras"]["mag_bounds"])


if __name__ == "__main__":
    main()
