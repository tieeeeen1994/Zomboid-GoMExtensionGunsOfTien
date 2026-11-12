"""OTs-14 Groza model and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_groza.py -- [--size 1024] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_GROZA.fbx   GROZA4_BODY (the Groza-4: short barrel in the forend,
                                                             front grip), GROZA_BODY (Groza-1 / -2: the long barrel and
                                                             its slotted compensator out of the forend), GROZAGL_BODY
                                                             (the long barrel with the GP-25 in place of the forend,
                                                             front grip and trigger guard), GROZA2_BODY (the Groza-2:
                                                             compact, no forend, the barrel's collar and threaded tip
                                                             out of the front housing), GROZA2_HELD (GROZA2_BODY
                                                             turned 180 degrees about the bore: the Groza-2 is held
                                                             like a pistol, user 2026-11-12), GROZA_BOLT (the AK
                                                             carrier and its handle on the right, one part as on
                                                             GoM's AKs)
    P/models_X/weapons/parts/GunsOfTienPost93_GROZA_parts.fbx  GROZA_Suppressor (the Groza-4's own can)
    P/textures/weapons/GunsOfTienPost93/GROZA.png            512, the four bodies and the carrier
    P/textures/weapons/GunsOfTienPost93/GROZA_Suppressor.png 128
    scripts/post93/groza_points.json                         attachment points (game space)

User, 2026-11-11 (docs/post93_design.md "OTs-14 Groza family"): TsKIB SOO's bullpup on the AKS-74U's mechanism, shown in
April 1994, so Post-93; one body for the Groza-1 (7.62x39), Groza-4 (9x39) and Groza-2 (5.45x39), each on GoM's
magazines of its calibre, the Groza-4 with its own suppressor. Shapes traced from the Commons drawing "GrozaOC14
noBG.png" (Steifer, CC BY-SA 4.0: the basic version's left side, muzzle left; its opaque pixels only, the drop shadow is
semi-transparent) with trace_outline.py at the Groza-4's published 610 mm (2.097 px/mm):
scripts/groza_reference_outline.json; profiles read off 5 mm gridded crops of it. Colours from the Commons photo
"ОЦ-14 "Гроза" (лёгкий штурмовой вариант).jpg" (CC BY-SA 4.0, the light assault version's left side): blued steel,
a black forend and front grip, a plum Bakelite pistol grip, an orange-brown cover over the gas tube, the steel butt
plate with its holes. The long barrel and the GP-25 from the user's photo (2026-11-11: a Groza-1 with the GP-25, right
side, an AK-47 magazine; read by eye at the receiver's scale, 1.51 px/mm): the barrel stands 159 mm past the short
gun's muzzle (about 770 mm overall: Wikipedia's 420 mm barrel for the Groza-1 against the Groza-4's 240), a slotted
compensator; the GP-25's ribbed tube under it from 105 mm behind to 41 mm ahead of the short muzzle, held by a clamp
round the barrel, its frame where the trigger guard was (the trigger showing in its round opening), its leaf sight
standing over the barrel. Profiles in the drawing's (L, H) mm: L back from the muzzle, H up from the magazine's base;
the bore is at H 171.

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, 0.603 of real size.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_mp7 as kit  # noqa: E402

MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_GROZA.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_GROZA_parts.fbx")
POINTS_JSON = os.path.join(HERE, "groza_points.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "poly", "bakelite", "cover", "dark", "metal"]
kit.MATS[:] = MATS
kit.FONT.setdefault("B", ["110", "101", "110", "101", "110"])
ZERO = [0.0, 0.0, 0.0]

L0, H0 = 270.0, 145.0              # the origin: the pistol grip's rear meets the front housing
BORE = 171.0
W_REC, W_FRONT, W_FOREND, W_GRIP, W_FGRIP, W_BUTT = 15.0, 16.5, 14.0, 13.0, 14.0, 21.0
# GoM's magazines, each seated as on GoM's own rifle (measured 2026-11-11 on GoM's AK-47 / AK-74 / AS VAL with their
# magazines at their points, the magazine meshes cut by the receiver's bottom plane): the feed lips that deep into the
# receiver, the back edge at the receiver's bottom 0.5 mm in front of the magazine release, where an AK magazine locks
# (user, 2026-11-11: "make the mag release closer to the mag"; seated by their front edges on the well's front, GoM's
# differently sized magazines left the AS VAL 20 8.5 mm short of it). Until then all three shared one point with the
# lips 7 mm over the receiver's bottom ("the groza mag looks like it doesn't fit").
# The magazines curve forward as they go down, so the back edge is taken halfway down the release: the mean of its
# place at the receiver's bottom and 15 mm lower (762x39 34.1 / 32.4, 545x39 39.0 / 32.7, 9x39 36.3 / 35.1).
# { calibre: (insertion mm, back edge behind the lips mm) }
RECV_BOTTOM = 145.0
# The AK-47 30 and AS VAL 20 then still showed 4.6 / 3.9 mm of gap in the side renders (a lug at their very top reaches
# further back than the edge seen below it), so their values are taken from the renders.
MAG_SEAT = {"762x39": (22.7, 28.7), "545x39": (27.7, 35.4), "9x39": (31.9, 31.8)}


def mag_lips(cal):
    ins, rear = MAG_SEAT[cal]
    return MAG_CATCH[0][0] - 0.5 - rear, RECV_BOTTOM + ins

CARRIER_TRAVEL = 100.0             # the AK carrier's stroke (handle and carrier one part, GoM's AK swap)
SUPP = (-2.0, 168.0, 21.0)         # the Groza-4's can: from the muzzle forward (its back face 2 mm into the forend)
LONG_MUZZLE = -148.0               # the Groza-1 / -2 muzzle (the user's photo -159, weaponland's -143), a short
                                   # slotted muzzle device on a barrel 18 mm across (weaponland's photo)
# The GP-25 module, from the user's photo and weaponland.ru's / wikireading.ru's photos of the Groza-1 and OTs-14-4A with
# it (references/groza: wl_groza1_gl.jpg, read on a grid at the receiver's scale, 1.39 mm a pixel): the launcher's
# casing is the gun's handguard (no separate GP-25 grip or quadrant sight); its front hangs from a coupling clamped
# round the barrel, which carries the frame sight (folded back over the barrel, as on the user's photo); the rifle's
# trigger base is replaced by the launcher's, the trigger in its round opening, the AV / GR selector on its left.
GL_TUBE = (-32.0, 103.0, 125.0, 36.0)   # the tube in its ribbed sleeve: L front, L rear, axis H, radius (72 mm across)
GL_RIBS = (-8.0, 18.0, 44.0, 70.0)      # its circumferential grooves (L)
GL_COUPLING = (-28.0, -2.0, 12.5)       # the coupling round the barrel over the tube's front: L from, to, radius
GL_FRAME = [(100.0, 152.0), (100.0, 91.0), (160.0, 90.0), (168.0, 94.0), (175.0, 103.0), (181.0, 116.0),
            (188.0, 130.0), (197.0, 140.0), (208.0, 147.0), (208.0, 152.0)]   # the trigger base, side outline
GL_HOLE = (148.0, 128.0, 17.0)          # its round opening (34 mm), the trigger in it
GL_TRIGGER_SHIFT = -34.0           # the rifle's trigger shape, hanging from the round opening's top
# The compact Groza-2 (user, 2026-11-11: "I want Groza-2 to be the image i posted", a compact OTs-14-4A, right side
# three-quarter, references/groza/user_compact_4a.png): no forend or front grip, the rifle's trigger guard, the
# barrel out of the front housing in a thick collar, then a threaded tip under a grooved thread protector; read
# against the front housing's 167 mm (about 1 px a mm in the photo): the tip about 82 mm past the sight post.
COMPACT = [(52.0, 10.5), (62.0, 10.5), (62.0, 9.0), (80.0, 9.0), (80.0, 12.5), (127.0, 12.5)]   # (L, radius)
GL_LEAF = (-20.0, 186.0, 112.0, 90.0)   # the frame sight: hinge L, H, height, angle from the barrel (user, 2026-11-11:
                                        # "put the iron sight perpendicular", standing up as on weaponland's photo)

# ==================================================================================================
# Profiles (drawing L, H mm)
# ==================================================================================================

FOREND = [(1.5, 178.0), (1.5, 140.0), (5.0, 135.5), (20.0, 135.5), (22.0, 141.0), (24.0, 152.0), (48.0, 155.0),
          (84.0, 156.0), (115.0, 157.0), (123.0, 158.0), (123.0, 181.0), (110.0, 181.0), (5.0, 180.5)]
FRONT_GRIP = [(48.0, 155.0), (49.0, 133.0), (48.0, 101.0), (49.0, 70.0), (52.0, 62.0), (58.0, 58.5), (72.0, 58.5),
              (78.0, 62.0), (81.0, 85.0), (77.0, 112.0), (79.0, 151.0), (84.0, 156.0)]
FRONT_HOUSING = [(133.0, 143.0), (133.0, 193.0), (301.0, 193.0), (301.0, 143.0)]
HANDLE_OUT = [(135.0, 192.0), (135.0, 252.0), (139.0, 257.0), (150.0, 257.0), (156.0, 250.0), (290.0, 259.0),
              (300.0, 258.0), (306.0, 250.0), (318.0, 222.0), (318.0, 192.0)]
HANDLE_WIN = [(156.0, 216.0), (156.0, 243.0), (285.0, 250.0), (297.0, 241.0), (304.0, 225.0), (300.0, 216.0)]
RECEIVER = [(300.0, 145.0), (300.0, 205.0), (312.0, 210.0), (345.0, 221.0), (552.0, 214.0), (560.0, 208.0),
            (560.0, 140.0), (515.0, 140.0), (515.0, 145.0)]
STEP = [(480.0, 140.0), (480.0, 146.0), (515.0, 146.0), (515.0, 140.0)]
STOCK_FRAME = [(552.0, 215.0), (586.0, 220.0), (588.0, 97.0), (580.0, 95.0), (575.0, 133.0), (552.0, 140.0)]
BUTT = [(587.0, 95.0), (587.0, 218.0), (592.0, 221.0), (607.0, 221.0), (611.0, 216.0), (611.0, 98.0),
        (607.0, 93.0), (591.0, 93.0)]
# Trigger guard and trigger (user, 2026-11-11: "They look horrible"), read off the Commons photo of the light assault
# version at full size (4360 px, the guard 6.8 px a mm): the guard a steel band 10 mm wide and 2.5 thick round a
# 49 x 32 mm opening, its front leg beside the housing's front lug, its rear rising into the grip's front; the trigger
# slender, 11 mm wide at its root, curving down and forward to its point 23 mm under the housing. (The drawing's guard
# was 11 mm too shallow.)
GUARD_IN = [(151.0, 145.0), (151.0, 118.0), (152.5, 114.5), (156.0, 113.0), (192.0, 113.0), (197.0, 115.0),
            (200.0, 119.0), (204.5, 126.0)]
GUARD_OUT = [(148.5, 145.0), (148.5, 117.0), (150.5, 112.5), (155.5, 110.5), (193.0, 110.5), (200.0, 113.0),
             (204.5, 118.0), (208.0, 125.0)]   # the rear runs 2-4 mm into the grip's front, as on the photo
GUARD_LUG = (138.0, 148.5, 130.0)       # the housing's front lug the guard's front leg drops beside: L from, to, its foot
TRIGGER = [(192.2, 146.0), (192.2, 143.5), (189.2, 138.4), (187.0, 132.5), (183.4, 126.6), (178.2, 122.2),
           (173.8, 120.3), (172.6, 120.4), (176.7, 123.0), (181.9, 128.8), (184.1, 136.2), (181.9, 143.5),
           (181.9, 146.0)]
PISTOL_GRIP = [(205.0, 147.0), (204.0, 126.0), (209.0, 118.0), (226.0, 99.0), (236.0, 77.0), (240.0, 55.0), (244.0, 41.0),
               (282.0, 57.0), (276.0, 72.5), (265.0, 98.0), (256.0, 120.0), (258.0, 137.0), (275.0, 147.0)]
# The AK magazine release behind the magazine (the same photo, 2026-11-11: the user found the hooked paddle
# "horrible"): a flat square paddle with its pivot pin, hanging from a mounting tab on the receiver's bottom, a thin
# spring rod out of its lower front corner.
MAG_CATCH = [(424.0, 141.0), (424.0, 121.0), (426.5, 117.0), (446.0, 117.0), (446.0, 141.0)]
MAG_CATCH_TAB = (427.0, 443.0, 141.0, 146.0)


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="steel", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def lathe_y(b, H, profile, seg=16, mat="metal"):
    b.lathe("y", (0, 0, H - H0), [(L0 - L, r) for L, r in profile], seg=seg, mat=mat, phase=0.5)


def gp(L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round((L0 - L) * K, 4) + 0.0, round((H - H0) * K, 4) + 0.0]


def circle(cL, cH, r, n=20):
    import math
    return [(cL + r * math.cos(2 * math.pi * i / n), cH + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def build_body(kind):
    """kind: "short" (Groza-4), "long" (Groza-1), "gl" (the Groza-1 with the GP-25), "compact" (Groza-2)."""
    b = kit.Builder()
    if kind in ("short", "long"):
        slab(b, FOREND, half=W_FOREND, bevel=2.5, res=1, mat="poly")
        slab(b, FRONT_GRIP, half=W_FGRIP, bevel=4.0, res=1, mat="poly")
    if kind != "gl":
        b.strip(PL(GUARD_OUT), PL(GUARD_IN), -5.0, 5.0, mat="steel", bevel=0.6)
        box(b, GUARD_LUG[0], GUARD_LUG[1], GUARD_LUG[2], 146.0, -8.0, 8.0, mat="steel", bevel=1.0)
    if kind == "compact":
        # the collar and threaded tip out of the front housing, the latch block under its front (where a forend or the
        # launcher locks on)
        prof = [(COMPACT[-1][0], 0.0)] + list(reversed(COMPACT)) + [(COMPACT[0][0], 0.0)]
        lathe_y(b, BORE, prof, seg=20, mat="steel")
        box(b, 126.0, 146.0, 136.0, 146.0, -9.0, 9.0, mat="steel", bevel=1.0)
    if kind in ("long", "gl"):
        lathe_y(b, BORE, [(124.0, 0.0), (124.0, 9.0), (LONG_MUZZLE + 20.0, 9.0), (LONG_MUZZLE + 20.0, 0.0)],
                seg=16, mat="metal")                                # the long barrel out of the forend / housing
        lathe_y(b, BORE, [(LONG_MUZZLE + 21.0, 0.0), (LONG_MUZZLE + 21.0, 11.0), (LONG_MUZZLE + 19.0, 12.0),
                          (LONG_MUZZLE + 1.5, 12.0), (LONG_MUZZLE, 10.5), (LONG_MUZZLE, 0.0)], seg=16,
                mat="steel")                                        # the slotted muzzle device
    if kind == "gl":
        import math
        a, r_, hz, rad = GL_TUBE
        # the tube in its sleeve: the front end rounded, a lip where the barrel's bore opens, the rear capped
        lathe_y(b, hz, [(r_, 0.0), (r_, rad - 4.0), (r_ - 4.0, rad), (a + 9.0, rad), (a + 4.0, rad - 3.0),
                        (a + 1.5, rad - 9.0), (a, rad - 14.0), (a, 0.0)], seg=32, mat="poly")
        lathe_y(b, hz, [(a + 0.5, 0.0), (a + 0.5, 21.0), (a - 1.0, 21.0), (a - 1.0, 0.0)], seg=24, mat="dark")
        # the coupling round the barrel, its web down onto the tube's front, the sight's hinge block on top
        c0, c1, cr = GL_COUPLING
        lathe_y(b, BORE, [(c1, 0.0), (c1, cr), (c0, cr), (c0, 0.0)], seg=20, mat="steel")
        box(b, c0 + 3.0, c1 - 4.0, hz + rad - 8.0, BORE - 4.0, -9.0, 9.0, mat="steel", bevel=1.0)
        hL, hH, ln, rake = GL_LEAF
        box(b, hL - 6.0, hL + 6.0, BORE + 6.0, hH + 2.0, -6.0, 6.0, mat="steel", bevel=0.8)
        # the frame sight standing up across the barrel: a 22 mm wide, 3 mm thin frame whose long window faces the
        # shooter, looked through along the bore (user, 2026-11-11: "which is the facing of the hole"; it was built
        # as a plate along the barrel, its window facing the sides); edge-on from the side, as on weaponland's photo
        top = hH + ln
        for xa, xb, ha, hb in ((-11.0, -7.0, hH, top), (7.0, 11.0, hH, top), (-11.0, 11.0, top - 8.0, top),
                               (-11.0, 11.0, hH, hH + 14.0)):
            box(b, hL - 1.6, hL + 1.6, ha, hb, xa, xb, mat="steel", bevel=0.3)
        # the launcher's trigger base: the frame from the tube's rear to the pistol grip, its round opening, the
        # trigger in it, the selector's knob on the left
        slab(b, GL_FRAME, [circle(GL_HOLE[0], GL_HOLE[1], GL_HOLE[2], 24)], half=15.0, bevel=2.0, res=1, mat="steel")
        slab(b, [(L + GL_TRIGGER_SHIFT, H) for L, H in TRIGGER], half=2.5, bevel=0.5, mat="dark")
        b.lathe("x", (15.0, L0 - 117.0, 140.0 - H0), [(0.0, 0.0), (0.0, 4.5), (3.5, 4.5), (3.5, 0.0)], seg=12,
                mat="dark")
    lathe_y(b, BORE, [(134.0, 0.0), (134.0, 9.0), (131.0, 9.0), (131.0, 13.5), (118.0, 13.5), (118.0, 0.0)],
            seg=20, mat="metal")                                    # the barrel nut's rings
    slab(b, FRONT_HOUSING, half=W_FRONT, bevel=1.5)
    slab(b, HANDLE_OUT, [HANDLE_WIN], half=7.0, bevel=1.0)
    lathe_y(b, 204.5, [(290.0, 0.0), (290.0, 11.5), (157.0, 11.5), (157.0, 0.0)], seg=18, mat="cover")   # gas tube
    b.lathe("x", (0, L0 - 289.0, 252.0 - H0), [(-8.0, 0.0), (-8.0, 7.5), (8.0, 7.5), (8.0, 0.0)], seg=14,
            mat="dark")                                             # the rear sight's drum
    slab(b, RECEIVER, half=W_REC, bevel=1.4, res=1)
    slab(b, STEP, half=W_REC - 1.0, bevel=0.8)
    slab(b, STOCK_FRAME, half=W_BUTT - 4.0, bevel=1.5)
    slab(b, BUTT, half=W_BUTT, bevel=2.0, res=1)
    if kind != "gl":
        slab(b, TRIGGER, half=2.5, bevel=0.5, mat="dark")
    slab(b, PISTOL_GRIP, half=W_GRIP, bevel=3.5, res=1, mat="bakelite")
    slab(b, MAG_CATCH, half=4.0, bevel=1.0)
    box(b, MAG_CATCH_TAB[0], MAG_CATCH_TAB[1], MAG_CATCH_TAB[2], MAG_CATCH_TAB[3], -6.0, 6.0, mat="steel", bevel=0.6)
    b.lathe("x", (0, L0 - 434.0, 126.0 - H0), [(-5.0, 0.0), (-5.0, 2.6), (5.0, 2.6), (5.0, 0.0)], seg=12, mat="metal")
    slab(b, [(425.5, 119.0), (427.5, 119.0), (425.5, 104.0), (424.0, 104.5)], half=1.0, bevel=0.2, mat="metal")
    return b.to_object({"short": "GROZA4_BODY", "long": "GROZA_BODY", "gl": "GROZAGL_BODY",
                        "compact": "GROZA2_BODY"}[kind])


def build_carrier():
    """The AK carrier's handle on the right (an AKS-74U's), forward; GoM's AK swap draws it back on each shot."""
    b = kit.Builder()
    box(b, 352.0, 366.0, 182.0, 190.0, -W_REC + 1.0, -W_REC - 11.0, mat="steel", bevel=1.0)
    b.lathe("x", (-(W_REC + 11.0), L0 - 357.0, 186.0 - H0), [(0.0, 0.0), (0.0, 6.0), (-9.0, 6.0), (-10.0, 4.5),
                                                               (-10.0, 0.0)], seg=12, mat="steel")
    return b.to_object("GROZA_BOLT")


# The optics mount (user, 2026-11-12: "that's not how the scope works on groza"; wikireading.ru: "оптический прицел,
# устанавливаемый непосредственно на рукоятку для переноски", the optical sight mounted directly on the carrying
# handle; its drawing of a commercial scope shows the mount block clamped on the handle's top bar just behind the
# front post, the scope above the handle, its eyepiece back over the receiver). The PSO-1 side rail was only on an
# early 7.62 model or prototype. In game it is GoM's optional Picatinny_Rail_Up (user, 2026-11-12: "let's use GoM's
# Up"; the main mod's Uzi top rails and the MDRx side rails are GoM's rail items drawn with our models), drawn as
# GROZA_RAIL_UP: a clamp round the top bar and a short rail on it, modelled in the gun's space (drawn at rail_up =
# the origin), on the gun's atlas.
# GoM's optics are made to clamp GoM's own rail at GoM's spacing (on its M4A1 / M16A3: scope = rail_up + (0, -0.0066,
# +0.0039)); a rail of our own made with other dimensions left them not gripping it (user, 2026-11-12: "the sniper
# wasn't even holding"). So the mount carries GoM's Picatinny_Rail_Up mesh itself (rails.fbx, 0.0756 long, 0.0152 wide,
# its origin 0.0011 over its bottom), on our base: a plate as long as the rail between the handle's posts (its top bar
# runs L 156-290), with a clamp jaw round the bar at each end (the bar rises 8.4 mm along the plate, so the plate is
# level and the jaws reach down to it).
GOM_RAIL_LEN, GOM_RAIL_BELOW = 0.0756, 0.0011     # game units
RAIL_L = 223.0                                    # the rail's middle (L)
MOUNT_BASE = (159.5, 286.5, 259.0, 264.0, 12.0)   # the plate: L from, to, H bottom, top, half width
JAWS = ((162.0, 178.0, 241.5), (268.0, 284.0, 249.0))   # (L from, to, bottom H) under the plate, round the bar
GOM_SCOPE_FROM_RAIL = (0.0, -0.0066, 0.0039)


def rail_origin():
    return (0.0, (L0 - RAIL_L) * K, (MOUNT_BASE[3] - H0) * K + GOM_RAIL_BELOW)


def build_handle_mount():
    b = kit.Builder()
    m0, m1, h0, h1, hw = MOUNT_BASE
    slab(b, [(m0, h0), (m1, h0), (m1, h1 - 1.5), (m1 - 1.5, h1), (m0 + 1.5, h1), (m0, h1 - 1.5)], half=hw,
         bevel=0.5, mat="steel")
    for a, c, bot in JAWS:
        for sx in (1, -1):
            box(b, a, c, bot, h0 + 0.5, sx * 7.2, sx * 11.5, mat="steel", bevel=0.6)
            b.lathe("x", (sx * 11.5, L0 - (a + c) / 2.0, (bot + 4.0) - H0),
                    [(0.0, 0.0), (0.0, 3.2), (sx * 1.6, 3.2), (sx * 1.6, 0.0)], seg=12, mat="metal")
        box(b, a, c, bot, bot + 3.0, -11.5, 11.5, mat="steel", bevel=0.6)    # the jaw's bottom bridge under the bar
    base = b.to_object("GROZA_RAIL_UP")
    # GoM's rail on it, joined into the same node (FBX data space: (x, y, -z) game units, as our builder writes)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(GOM, "models_X/weapons/parts/rails.fbx"))
    rail = None
    for o in set(bpy.data.objects) - before:
        if o.name.split(".")[0] == "Picatinny_Rail_Up" and rail is None:
            rail = o
        else:
            bpy.data.objects.remove(o)
    ox, oy, oz = rail_origin()
    rail.data.transform(Matrix.Translation((ox, oy, -oz)))
    rail.matrix_world = Matrix.Identity(4)
    rail.data.materials.clear()
    for m in base.data.materials:
        rail.data.materials.append(m)
    for poly in rail.data.polygons:
        poly.material_index = MATS.index("steel")
    bpy.ops.object.select_all(action='DESELECT')
    rail.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    return base


def build_suppressor():
    """The Groza-4's detachable can, in its own frame: origin on the bore at the muzzle, +Y forward."""
    a, ln, r = SUPP
    b = kit.Builder()
    b.lathe("y", (0, 0, 0), [(a, 0.0), (a, r - 2.0), (a + 2.0, r), (a + ln - 3.0, r), (a + ln, r - 3.0),
                             (a + ln, 5.0), (a + ln - 1.0, 0.0)], seg=24, mat="steel")
    return b.to_object("GROZA_Suppressor")


# Colours and wear in GoM's way (user, 2026-11-11: "look at as val and AKS. can we make the texture similar-ish?";
# measured on GoM's AKS74U.png / ASVAL.png: grey steel at median 32-39, 5th-95th percentile 16-83, its wood a muted
# red-brown about (84, 63, 52)): darker steel with brighter worn edges and deeper crevices than before (median 49,
# 24-98), the gas tube's cover as GoM's AKS wood with grain, the Bakelite grip a muted plum-brown.
BASE = {"steel": (41, 42, 45), "poly": (31, 31, 33), "bakelite": (86, 52, 44), "cover": (112, 70, 50),
        "dark": (18, 18, 19), "metal": (46, 47, 50)}


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "dark")])
    wood = mat == MATS.index("cover")
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.88 + 0.24 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.82 + 0.36 * streak[is_metal])[..., None]
    grain = kit.vnoise(p * np.array([2.2, 0.03, 2.2]), 1.0, 7)        # long grain along the wooden cover
    col[wood] *= (0.78 + 0.36 * grain[wood])[..., None]
    col *= (0.96 + 0.12 * np.clip(n[..., 2], -1, 1))[..., None]      # lit from above, as GoM's bakes
    occ = (0.62 + 0.38 * np.clip(ao_b, 0, 1) ** 1.5) * (0.66 + 0.34 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 115.0, 50.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body":
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        L, H = L0 - y, z + H0
        side = np.abs(n[..., 0]) > 0.7
        steel = (mat == MATS.index("steel")) & side
        rec = steel & (np.abs(x) > W_REC - 0.6) & (L > 300.0) & (L < 560.0)
        # the dust cover's seam and rib, the receiver's rivets (as photographed), the butt plate's holes
        col[rec & (np.abs(H - 199.0) < 0.7)] *= 0.45
        col[rec & kit.rounded_rect(L, H, 380.0, 520.0, 186.0, 190.0, 1.8)] *= 0.5
        for cL, cH in ((320, 172), (338, 172), (362, 156), (430, 163), (444, 163), (456, 163), (430, 156),
                       (444, 156), (456, 156), (490, 156), (504, 156), (528, 165), (548, 175), (548, 152),
                       (366, 157), (388, 157)):
            d = np.hypot(L - cL, H - cH)
            col[rec & (d < 2.6)] *= 0.5
            col[rec & (d < 1.6)] += 48                      # rivet heads catch the light, as GoM paints them
        # the receiver's seams: the front trunnion, the rear block, the dust cover's lower edge
        for sL in (312.0, 346.0, 551.0):
            col[rec & (np.abs(L - sL) < 0.6) & (H < 212.0)] *= 0.5
        col[rec & (np.abs(H - 147.5) < 0.5)] *= 0.6
        # the front housing's recessed side panel with its screw (the photos), its seam over the trigger guard
        fh = steel & (np.abs(x) > W_FRONT - 0.6) & (L > 133.0) & (L < 301.0)
        col[fh & kit.rounded_rect(L, H, 150.0, 292.0, 158.0, 188.0, 3.0)] *= 0.72
        col[fh & kit.rounded_rect(L, H, 150.0, 292.0, 187.0, 188.5, 0.5)] += 22
        col[fh & (np.abs(H - 150.0) < 0.5)] *= 0.55
        for cL, cH in ((282.0, 173.0), (180.0, 151.5)):
            d = np.hypot(L - cL, H - cH)
            col[fh & (d < 3.0)] *= 0.5
            col[fh & (d < 1.9)] += 45
        # lighter towards the top, darker low down, as GoM's baked lighting
        col[steel] *= (0.84 + 0.3 * np.clip((H[steel] - 100.0) / 160.0, 0.0, 1.0))[..., None]
        col[rec & kit.rounded_rect(L, H, 398.0, 422.0, 154.0, 162.0, 3.5)] *= 0.55        # the selector's slot
        butt = steel & (np.abs(x) > W_BUTT - 0.6) & (L > 587.0)
        for hH in (195.0, 170.0, 145.0, 120.0):
            col[butt & kit.rounded_rect(L, H, 593.0, 605.0, hH - 7.0, hH + 7.0, 2.5)] = 12
        # the grip's chequering, the front grip's rings
        bk = (mat == MATS.index("bakelite")) & side
        col[bk & (L > 238.0) & (L < 268.0) & (H > 62.0) & (H < 128.0) & (((L * 1.2 + H) % 3.0) < 1.0)] *= 0.7
        fg = (mat == MATS.index("poly")) & (L > 46.0) & (L < 84.0) & (H > 62.0) & (H < 100.0)
        col[fg & (np.mod(H, 6.0) < 2.0)] *= 0.55
        # the bore at the forend's front (the short gun) or the compensator's front, the compensator's slots
        col[(np.abs(L - 1.5) < 0.8) & (np.hypot(x, H - BORE) < 4.6)] = 6
        col[(np.abs(L - LONG_MUZZLE) < 0.8) & (np.hypot(x, H - BORE) < 4.6)] = 6
        comp = (mat == MATS.index("steel")) & (L < LONG_MUZZLE + 18.0) & (L > LONG_MUZZLE + 3.0) & (
            np.hypot(x, H - BORE) > 10.5)
        col[comp & (np.abs(np.mod(L - LONG_MUZZLE, 7.0) - 3.5) < 1.5) & (np.abs(n[..., 1]) < 0.5)] = 10
        # the compact's thread under the protector, the protector's grooves, its bore
        r_b = np.hypot(x, H - BORE)
        tip = (mat == MATS.index("steel")) & (np.abs(n[..., 1]) < 0.5) & (L > 52.5) & (L < 79.5) & (r_b < 11.0)
        col[tip & (L > 62.0) & (np.mod(L, 1.5) < 0.6)] *= 0.55
        col[tip & (L < 62.0) & (np.mod(L, 2.5) < 1.0)] *= 0.5
        col[(np.abs(L - 52.0) < 0.8) & (r_b < 4.6)] = 6
        # the GP-25 sleeve's axial ribs and its two screws a side
        a, r_, hz, rad = GL_TUBE
        tube = (mat == MATS.index("poly")) & (L > a + 3.0) & (L < r_ - 3.0) & (np.hypot(x, H - hz) > rad - 1.5)
        for g in GL_RIBS:
            col[tube & (np.abs(L - g) < 1.3)] *= 0.45
            col[tube & (np.abs(L - g - 1.8) < 0.6)] += 18
        for cL in (5.0, 31.0, 57.0, 83.0):
            col[tube & (np.abs(n[..., 0]) > 0.8) & (np.hypot(L - cL, H - (hz + 8.0)) < 3.0)] = (120, 120, 124)
        frame = (mat == MATS.index("steel")) & side & (L > 100.0) & (L < 210.0) & (H < 152.0) & (np.abs(x) > 13.0)
        col[frame & (n[..., 0] > 0.7) & kit.text_mask(L, H, "AB", 170.0, 143.0, 3.5)] += 60
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def bake(ob, ctx, size):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    return kit.bake_maps(ob, ctx, bake_size)


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


def points(bounds):
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": gp(0.0, BORE), "rotate": ZERO},
        "magazine": {"offset": gp(*mag_lips("9x39")), "rotate": ZERO},
        "magazine_762x39": {"offset": gp(*mag_lips("762x39")), "rotate": ZERO},
        "magazine_545x39": {"offset": gp(*mag_lips("545x39")), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the pistol grip's "
                 "rear top (drawing L %.0f, H %.0f)" % (L0, H0),
        "canon": "the muzzle on the bore: GROZA_Suppressor (Groza-4 only) is modelled about it",
        "magazine": "GoM's AS VAL magazines' feed lips (the Groza-4's model; drawn through their _GoT models); "
                    "magazine_762x39 / _545x39 the AK-47's and AK-74's, for the Groza-1's and -2's models",
        "bolt_fired": "GROZA_BOLT (the AK carrier's handle on the right) back %.0f mm real (GoM's AK swap)"
                      % CARRIER_TRAVEL,
    }
    pts["_extras"] = {"photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K}
    pts["_bounds"] = bounds
    return pts


def held_points(pts):
    """The Groza-2's points on GROZA2_HELD: each upright point turned with the body (x, z negated); every part drawn
    there (the shared bolt and handle rail, modelled in place, and GoM's magazines and optics, modelled upright) turned
    by the point (kit.TURN, as the MP7's); GoM's handgun floor pose (its MP5K / MAC10: -0.025, no turn) at our scale;
    the back-slot turns for its rifle slots (kit.handgun_points)."""
    def tn(name):
        x, y, z = pts[name]["offset"]
        return [round(-x, 4) + 0.0, y, round(-z, 4) + 0.0]
    turn = list(kit.TURN)
    return {
        "muzzle": {"offset": tn("muzzle_compact"), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": tn("magazine_545x39"), "rotate": turn},
        "bolt_lock": {"offset": [0.0, 0.0, 0.0], "rotate": turn},
        "bolt_fired": {"offset": tn("bolt_fired"), "rotate": turn},
        "rail_up": {"offset": tn("rail_up"), "rotate": turn},
        "scope": {"offset": tn("scope"), "rotate": turn},
        "world": {"offset": [round(-0.025 * K / K_OLD, 4), 0.0, 0.0], "rotate": ZERO},
        "rifle_back": {"offset": [0.0, 0.0, 0.0], "rotate": turn},
        "rifle_back_bag": {"offset": [0.0, 0.0, 0.0], "rotate": turn},
    }


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
    bodies = [build_body(k) for k in ("short", "long", "gl", "compact")]
    bolt, supp, mount = build_carrier(), build_suppressor(), build_handle_mount()
    kit.unwrap(bodies + [bolt, mount], 0.004)
    kit.unwrap([supp], 0.01)
    texture([bake(o, [o, bolt], 512) for o in bodies] + [bake(bolt, [bodies[0], bolt], 512),
                                                         bake(mount, [mount, bodies[0]], 512)],
            ["body"] * 4 + ["bolt", "supp"], 512, os.path.join(TEX_DIR, "GROZA.png"))
    texture([bake(supp, [supp], 128)], ["supp"], 128, os.path.join(TEX_DIR, "GROZA_Suppressor.png"))
    # The Groza-2 held like a pistol (user, 2026-11-12: "hold Groza-2 using handgun stance"), as GoM's MP5K and our MP7 /
    # P90: its body turned 180 degrees about the bore at export (build_mp7.py TURN), a copy so the upright GROZA2_BODY
    # stays for the renders, icons and previews; the shared bolt, handle rail and GoM's magazines and optics are turned
    # by its points instead (held_points).
    held = bodies[3].copy()
    held.data = bodies[3].data.copy()
    held.name = held.data.name = "GROZA2_HELD"
    bpy.context.scene.collection.objects.link(held)
    held.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bodies.append(held)
    bounds = {o.name: kit.bounds_of(o) for o in bodies + [bolt, supp, mount]}
    pts = points(bounds)
    # GoM's Picatinny_Rail_Up drawn as GROZA_RAIL_UP at the origin (modelled in place); GoM's optics on its rail, 0.0032 under the crossbars' tops
    # (our guns' relation to GoM's optics), over the rail's middle
    pts["rail_up"] = {"offset": [0.0, 0.0, 0.0], "rotate": ZERO}
    pts["scope"] = {"offset": [round(c + d, 4) + 0.0 for c, d in zip(rail_origin(), GOM_SCOPE_FROM_RAIL)],
                    "rotate": ZERO}
    pts["muzzle_long"] = {"offset": gp(LONG_MUZZLE, BORE), "rotate": [-90.0, 0.0, -180.0]}
    pts["muzzle_compact"] = {"offset": gp(COMPACT[0][0], BORE), "rotate": [-90.0, 0.0, -180.0]}
    # the GP-25's bore opening (the tube's front on its axis): the launcher weapon's muzzle (gen_post93_guns.py
    # GROZAGL_GP25, as GoM's M16A2_M203_Underbarrel model moves its muzzle to the M203's)
    pts["muzzle_gl"] = {"offset": gp(GL_TUBE[0], GL_TUBE[2]), "rotate": [-90.0, 0.0, -180.0]}
    pts["held"] = held_points(pts)
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(bodies + [bolt, mount], FBX_GUN)
    kit.export([supp], FBX_PARTS)
    for name, bd in bounds.items():
        print("%-20s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
