"""Steyr AUG A3-receiver guns for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_aug3.py -- --gun a3|para|hbar|mags [--size 1024]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    --gun a3    M/models_X/weapons/firearms/GunsOfTienPost93_AUGA3.fbx     AUGA3_BODY, AUG_RAIL_LEFT
                M/textures/weapons/GunsOfTienPost93/AUGA3.png              256 atlas (body, the short left rail)
                scripts/post93/auga3_points.json
    --gun para  M/models_X/weapons/firearms/GunsOfTienPost93_AUGPARA.fbx   AUGPARA_BODY, AUGPARA_BOLT,
                                                                           AUGPARA_FOREGRIP
                M/textures/weapons/GunsOfTienPost93/AUGPARA.png            256 atlas
                scripts/post93/augpara_points.json
    --gun hbar  M/models_X/weapons/firearms/GunsOfTienPost93_AUGHBAR.fbx   AUGHBAR_BODY, AUGHBAR_BIPOD_FOLDED,
                                                                           AUGHBAR_BIPOD_DEPLOYED
                M/textures/weapons/GunsOfTienPost93/AUGHBAR.png            256 atlas
                scripts/post93/aughbar_points.json
    --gun mags  M/models_X/weapons/magazines/GunsOfTienPost93_AUG_magazines.fbx  9x19Magazine25_AUG,
                                                    9x19Magazine32_AUG, 762x39Magazine30_AUG, 762x39Magazine50_AUG
                M/textures/weapons/GunsOfTienPost93/<magazine>.png         128 each (after --gun para)

Design: docs/post93_design.md, "Steyr AUG A3, AUG Para and AUG HBAR". Everything is built on the main mod's A1
(scripts/build_aug.py, imported as `a1`): the same photo frame (L back from the A1's muzzle, H up from the butt's heel,
real mm), the same stock, trigger frame, grip, folding grip and painting. The A3 receiver replaces the A1's cast scope
and carrying handle with a raised upper carrying a Picatinny rail, and adds the right-side rail of the A3 SF.

A3: the A1's barrel; the charging handle (GunsOfTien.AUG_BOLT), the folding grip (GunsOfTien.AUG_FOREGRIP) and the
magazines are the A1's own models, drawn at this gun's points (the same Steyr green). Measured on Commons "Interpolitex
2011 (405-9)" (Vitaly V. Kuzmin, CC BY-SA 4.0; two A3s, right side, kept out of the repo in tmp/ref/aug_variants),
scaled by the receiver (the A1's L 249-402, 153 mm: 2.575 px/mm) and anchored at the receiver's front face and the
bore: the rail's crossbars reach H ~186 from L ~264 back to L ~494 over the stock's top; the right-side rail (the black
gun) lies on the receiver at L 282-381, centred H 143. The receiver has no left rail (the charging handle runs along
that side and leaves no room for GoM's 125 mm rail): GoM's Picatinny_Rail_Left is an optional upgrade, drawn as this
mod's short AUG_RAIL_LEFT at `rail_left` on the receiver's front-left, under the handle's path. Every A3-receiver gun
uses that one model (the A3's texture).

Para: Steyr's 9x19mm AUG (user, 2026-10-28: on the A3 receiver, sand). Blowback: a 420 mm barrel with no gas cylinder
and no flash hider, its muzzle 125 mm behind the A1's (Steyr: 665 mm long against 790; 88 mm shorter barrel, the A1's
37 mm hider gone), stepped as in Commons "AUG 9mm 03" (Steyr Mannlicher, CC BY 2.0, 550 px, left side), with a collar
22 mm behind the muzzle where the main mod's 9x19mm SMG mount device starts (`canon`, the UMP9's relation). Steyr's
straight 25 / 32-round steel magazines (MPi 69 pattern) sit in the AUG well through a grey adapter that fills its
mouth; they hang from the A1's `magazine` point (the bullpup reload's place). Its own sand copies of the charging
handle and folding grip (the A1's are green).

HBAR: Steyr's 7.62x39mm AUG (Enforce Tac 2025) with the 621 mm heavy barrel and its folding bipod (user, 2026-10-28:
"a possible setup"; green as the A3). The barrel is 113 mm longer than the A1's (Steyr: 900 mm long against 790), heavy
(21 mm) ahead of the A1's gas cylinder, with a ported brake (TFB's HBAR photo) and the bipod's clamp behind it; the
legs (AUGHBAR_BIPOD_FOLDED / _DEPLOYED, modelled in the gun's space as the main mod's M249's, drawn at
`integrated_bipod`) fold back under the barrel, beside the folded grip, long enough to stand the gun on its feet.
The A1's charging handle and folding grip. Steyr's own 7.62x39mm magazine (TFB's Enforce Tac video): the AUG's smoke
polymer, curved like an AK magazine, hung from the A1's `magazine` point; and a 50-round box on the same curve, wide
as a coffin all the way (user, 2026-10-28, in place of drums: C-Mag style 75 / 150 drums were built and dropped).
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
sys.path.insert(0, os.path.join(HERE, ".."))
import build_aug as a1  # noqa: E402  (sets kit.K / kit.MATS and imports build_mp7 as kit)

kit = a1.kit
K = a1.K
MEDIA = os.path.join(kit.ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
FIRE_DIR = os.path.join(MEDIA, "models_X/weapons/firearms")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_AUG_magazines.fbx")

GUN = kit.arg("--gun", "a3")
NAME = {"a3": "AUGA3", "para": "AUGPARA", "hbar": "AUGHBAR", "mags": "AUG_magazines"}[GUN]

# The A3 upper (photo L, H mm)
RAIL_FLOOR, RAIL_TOP = 177.0, 186.0          # the rail's mounting face on the upper; its crossbars' tops
RAIL = (264.0, 494.0)                        # front and rear ends of the top rail
UPPER = [(262.0, 161.0), (262.0, RAIL_FLOOR), (RAIL[1], RAIL_FLOOR), (RAIL[1] + 4.0, RAIL_FLOOR - 4.0),
         (RAIL[1] + 4.0, 163.5), (402.0, 161.0)]
NOSE = [(262.0, RAIL_FLOOR), (262.0, 158.0), (249.0, 150.0), (246.0, 156.0), (252.0, 168.0)]
SIDE_RAIL = (282.0, 381.0)                   # the right-side rail's ends
SIDE_RAIL_H = 143.0                          # its centre line
# The optional left rail: GoM's Picatinny_Rail_Left item drawn with this short model (AUG_RAIL_LEFT, 4 crossbars,
# like Corvus Defensio's A3 receiver rail) on the receiver's front-left, under the charging handle's path (its lowest
# edge H 140, resting at L 255-290 and running back to L 382) and ahead of the stock's shell and the trigger frame
# (both from L 298). GoM's own model (125 mm long, 25 mm across) has no room on that side.
LEFT_RAIL = (256.0, 297.0)
LEFT_RAIL_H = 129.5                          # its centre line: the crossbars' upper edge 10.6 mm above, under H 140
OPTIC_L = 400.0                              # where GoM's optics sit on the rail (the A1's scope centre is L 420)
W_UPPER = 18.0                               # the upper's half width over the receiver

# The Para (photo L, H mm of the A1's frame)
PARA_MUZZLE = 125.0
PARA_CANON = 147.0                           # the collar's front face: the SMG mount device starts here
PARA_BARREL = [(250.0, 0.0), (250.0, 18.0), (246.0, 18.0), (246.0, 12.0), (196.0, 12.0), (194.0, 10.0),
               (172.0, 10.0), (170.0, 8.0), (153.0, 8.0), (153.0, 8.5), (PARA_CANON, 8.5), (PARA_CANON, 6.5),
               (PARA_MUZZLE + 0.8, 6.5), (PARA_MUZZLE, 5.8), (PARA_MUZZLE, 0.0)]
ADAPTER_TOP = (545.0, 612.0, 70.0, 77.0)     # the plate filling the well's mouth
ADAPTER = (557.0, 597.0, 20.0, 72.0)         # the sleeve round the magazine below it
W_ADAPTER = 15.5
# its release paddle behind (photo), the top edge up inside the stock's sloping underside (the A1's STOCK runs from
# (612, 76.5) down to (661, 27)), so no gap shows between them (user, 2026-10-28)
ADAPTER_PADDLE = [(591.0, 77.0), (613.0, 77.0), (653.0, 37.0), (609.0, 27.0), (591.0, 17.0)]
PARA_MAG_LEN = {25: 150.0, 32: 187.0}        # lips to base, 5.3 mm a round (9x19mm, double stack)
PARA_MAG_W, PARA_MAG_D = 12.0, 18.0          # half width across, half depth front to back
# The HBAR (photo L, H mm of the A1's frame; negative L = ahead of the A1's muzzle)
HBAR_MUZZLE = -110.0
HBAR_BARREL = [(250.0, 0.0), (250.0, 18.0), (246.0, 18.0), (246.0, 13.5), (198.0, 13.5), (197.0, 10.5),
               (-14.0, 10.5), (-14.0, 13.0), (-34.0, 13.0), (-34.0, 10.5), (-60.0, 10.5), (-60.0, 11.5),
               (HBAR_MUZZLE + 1.0, 11.5), (HBAR_MUZZLE, 10.5), (HBAR_MUZZLE, 0.0)]
BIPOD_PIVOT = (-24.0, 128.0, 9.0)            # the legs' pivots on the clamp's underside: L, H, |x|
# legs 245 mm, so the deployed feet reach below the 7.62x39mm 30's base (H about -100) and the gun stands on them
# (the 50's base hangs about 5 cm lower, as an RPK's long magazines do); folded back they lie beside the folded grip
# (its half width 15; the legs' inner edge at 16.5), clear of the gas valve (|x| < 6) and ending ahead of the grip's
# bracket (L 228), so no longer legs fit
BIPOD_FOLDED_END = (221.0, 127.0, 21.0)
BIPOD_FOOT = (-50.0, -110.0, 60.0)           # deployed: feet down, a little forward, splayed
# The 7.62x39mm magazine: the AUG's construction on an AK magazine's curve
# lips to base along its axis, 5.6 mm a round. The 50 (user, 2026-10-28: the LMG's long box in place of drums, "the
# outer part thicker", 50 rounds) carries the 30's curve on to 251 mm, wide as a coffin (the rounds four abreast, as
# SureFire's high-capacity magazines) all the way up to the well (user: "thick all the way"; inside the stock's 54 mm).
AK_MAG_LEN = {30: 195.0, 50: 251.0}
COFFIN_W = 25.0                              # the 50's half width across
AK_MAG_W, AK_MAG_D = 17.0, 31.0
AK_MAG_RAKE, AK_MAG_R = 6.0, 420.0           # its base about 65 mm ahead of its top, one magazine depth (TFB)
# Sand polymer (user, 2026-10-28), the grey adapter and steel magazines
PARA_COLOURS = {"polymer": (176, 160, 124), "grip": (168, 152, 117), "scope": (96, 98, 100), "magpoly": (70, 72, 75)}


def build_body():
    b = kit.Builder()
    slab, box = a1.slab, a1.box
    slab(b, a1.STOCK, half=a1.W_STOCK, bevel=4.0, res=1, mat="polymer")
    slab(b, a1.FRAME, [a1.OPENING], half=a1.W_GUARD, bevel=2.5, res=1, mat="polymer")
    slab(b, a1.GRIP, half=a1.W_GRIP, bevel=4.5, res=1, mat="polymer")
    slab(b, a1.TRIGGER, half=3.5, bevel=0.6, mat="dark")
    La, Lb, Ha, Hb = a1.SAFETY
    box(b, La, Lb, Ha, Hb, -(a1.W_STOCK + 1.5), a1.W_STOCK + 1.5, mat="dark", bevel=0.8)
    slab(b, a1.MAG_RELEASE, half=7.0, bevel=1.0, mat="dark")
    La, Lb, Ha, Hb = a1.PORT_COVER
    box(b, La, Lb, Ha, Hb, a1.W_STOCK - 1.0, a1.W_STOCK + 1.2, mat="metal", bevel=0.5)
    # the receiver as on the A1, the A3's upper on it carrying the rail back over the stock, its sloped nose
    La, Lb, Ha, Hb = a1.RECEIVER
    box(b, La, Lb, Ha, Hb, -a1.W_RCV, a1.W_RCV, mat="metal", bevel=1.8)
    slab(b, UPPER, half=W_UPPER, bevel=1.5, mat="metal")
    slab(b, NOSE, half=W_UPPER - 4.0, bevel=1.2, mat="metal")
    ya, yb = sorted((a1.y(RAIL[1]), a1.y(RAIL[0])))
    # the rail body (6.5 mm) with its crossbars 3.5 mm proud: kit.picatinny() puts the crossbars' tops at
    # base_h + tooth_h - 1 above the mounting face
    kit.picatinny(b, ya, yb, lambda u, h, yy: Vector((u, yy, a1.z(RAIL_FLOOR) + h)), base_h=6.5,
                  tooth_h=RAIL_TOP - RAIL_FLOOR - 5.5, mat="dark")
    # the right-side rail (-X = the gun's right), its crossbars standing out from the receiver's face
    ya, yb = sorted((a1.y(SIDE_RAIL[1]), a1.y(SIDE_RAIL[0])))
    kit.picatinny(b, ya, yb, lambda u, h, yy: Vector((-(a1.W_RCV + h), yy, a1.z(SIDE_RAIL_H) + u)), base_h=1.5,
                  tooth_h=3.0, mat="dark")
    slab(b, a1.FG_BRACKET, half=10.0, bevel=1.2, mat="barrel")
    if GUN == "hbar":
        a1.bore_lathe(b, HBAR_BARREL, seg=18)
        La, Lb, Ha, Hb = a1.GAS_VALVE
        box(b, La, Lb, Ha, Hb, -6.0, 6.0, mat="dark", bevel=0.8)
        # the bipod's clamp block under the barrel at the pivots
        box(b, -34.0, -14.0, BIPOD_PIVOT[1] - 6.0, a1.BORE - 6.0, -12.0, 12.0, mat="dark", bevel=1.0)
    elif GUN == "para":
        a1.bore_lathe(b, PARA_BARREL, seg=18)
        # the magazine adapter (grey: the "scope" material, unused on the A3 receiver), filling the well's mouth
        for La, Lb, Ha, Hb, half in (ADAPTER_TOP + (a1.W_STOCK - 7.0,), ADAPTER + (W_ADAPTER,)):
            box(b, La, Lb, Ha, Hb, -half, half, mat="scope", bevel=1.0)
        slab(b, ADAPTER_PADDLE, half=8.0, bevel=1.0, mat="scope")
    else:
        a1.bore_lathe(b, a1.BARREL, seg=18)
        a1.bore_lathe(b, a1.COLLAR, seg=18)
        a1.bore_lathe(b, a1.NUT, seg=6, phase=0.0)
        a1.bore_lathe(b, a1.HIDER, seg=16)
        La, Lb, Ha, Hb = a1.GAS_VALVE
        box(b, La, Lb, Ha, Hb, -6.0, 6.0, mat="dark", bevel=0.8)
    return b.to_object(NAME + "_BODY")


def build_left_rail():
    """Origin = the rail's centre on the receiver's left face (rail_left); it stands out along +X."""
    b = kit.Builder()
    half = (LEFT_RAIL[1] - LEFT_RAIL[0]) / 2.0
    kit.picatinny(b, -half, half, lambda u, h, yy: Vector((h, yy, u)), base_h=1.5, tooth_h=3.0, mat="dark")
    for yy in (-half + 3.0, half - 3.0):                   # the two screws through the end pads
        b.lathe("x", (0, yy, 0), [(0.0, 0), (0.0, 2.2), (2.8, 2.2), (3.2, 1.6), (3.2, 0)], seg=8, mat="metal")
    return b.to_object("AUG_RAIL_LEFT")


def leg(b, p0, p1):
    """A bipod leg from p0 to p1 (game mm), as the M249's (build_m249.py)."""
    d = Vector(p1) - Vector(p0)
    n = d.length
    xf = Matrix.Translation(Vector(p0)) @ Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    b.lathe("y", (0, 0, 0), [(0.0, 0.0), (0.0, 4.5), (n * 0.55, 4.5), (n * 0.55 + 1.0, 3.8), (n, 3.8), (n, 0.0)],
            seg=10, mat="barrel", xf=xf)
    b.box(-7.0, 7.0, n - 4.0, n + 2.0, -2.5, 2.5, mat="dark", bevel=0.8, xf=xf)          # the foot
    b.box(-5.0, 5.0, -2.0, 10.0, -5.0, 5.0, mat="barrel", bevel=0.8, xf=xf)              # the hinge knuckle


def build_bipod(deployed):
    b = kit.Builder()
    for s in (1, -1):
        L, H, x = BIPOD_PIVOT
        p0 = Vector((s * x, a1.y(L), a1.z(H)))
        Le, He, xe = BIPOD_FOOT if deployed else BIPOD_FOLDED_END
        leg(b, p0, Vector((s * xe, a1.y(Le), a1.z(He))))
    return b.to_object("AUGHBAR_BIPOD_" + ("DEPLOYED" if deployed else "FOLDED"))


def ak_mag_shape():
    """Point build_aug's magazine sweep at the 7.62x39mm magazine's curve and size (module globals it reads)."""
    a1.MAG_LEN, a1.MAG_W, a1.MAG_D = AK_MAG_LEN, AK_MAG_W, AK_MAG_D
    a1.MAG_RAKE, a1.MAG_R = math.radians(AK_MAG_RAKE), AK_MAG_R
    a1.MAG_C = (a1.MAG_R * math.cos(a1.MAG_RAKE), a1.MAG_R * math.sin(a1.MAG_RAKE))


def mag_width(rounds, s):
    """Half width across at s below the lips: the 30's, or the 50's coffin width all the way."""
    return COFFIN_W if rounds == 50 else AK_MAG_W


def sweep_var(b, s_list, wfun, d, c, mat):
    """build_aug.mag_sweep() with the half width a function of s."""
    bm = b.bm
    rings = []
    for s_ in s_list:
        (cy, cz), a = a1.mag_frame(s_)
        ny, nz = math.cos(a), math.sin(a)
        w = wfun(s_)
        sec = [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]
        rings.append([bm.verts.new((x, cy + u * ny, cz + u * nz)) for x, u in sec])
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_ak_magazine(rounds):
    ak_mag_shape()
    b = kit.Builder()
    end = AK_MAG_LEN[rounds]
    w, d = AK_MAG_W, AK_MAG_D
    steps = sorted({round(6.0 + k * 10.0, 3) for k in range(int((end - 8.0) // 10.0) + 1)} | {end - 8.0})
    sweep_var(b, steps, lambda s_: mag_width(rounds, s_), d, 3.0, "magpoly")
    a1.mag_sweep(b, [0.0, 6.0], w - 4.5, d - 3.0, 2.0, "magpoly")                       # feed lips
    wb = mag_width(rounds, end)
    sweep_var(b, [end - 8.0, end], lambda s_: wb + 1.2, d + 1.5, 3.0, "dark")           # the black base plate
    # the top round: 7.62x39mm, case 38.6 mm with its shoulder, bullet forward
    b.lathe("y", (0, -2.0, -4.6), [(-27.0, 0), (-27.0, 5.6), (3.0, 5.3), (5.5, 4.4), (11.6, 4.3)], seg=8,
            mat="brass")
    b.lathe("y", (0, -2.0, -4.6), [(11.6, 3.9), (18.0, 3.8), (25.0, 2.0), (28.0, 0)], seg=8, mat="copper")
    return b.to_object("762x39Magazine%d_AUG" % rounds)


def paint_ak_mag(maps, col, rounds):
    """build_aug.paint_mag() at the 7.62x39mm round's size: brass cases bullets forward through the smoke polymer, a
    staggered column 5.6 mm a round, the AUG's moulded waffle and the count near the base."""
    ak_mag_shape()
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, yy, zz = p[..., 0], p[..., 1], p[..., 2]
    side = (mat == a1.MATS.index("magpoly")) & (np.abs(n[..., 0]) > 0.7) & (np.abs(x) > AK_MAG_W - 0.8)
    s_, u = a1.mag_local(yy, zz)
    count = int((AK_MAG_LEN[rounds] - 26.0) // 5.6)
    for k in range(count):
        sk = 11.0 + k * 5.6
        off = 1.8 if k % 2 else -1.8
        band = side & (np.abs(s_ - sk) < 2.8)
        case = band & (u > -27.0 + off) & (u < 11.0 + off)
        col[case] = col[case] * 0.3 + np.array([150, 118, 62]) * 0.62
        col[case & (np.abs(s_ - sk + 1.2) < 0.7)] += 22
        tip = band & (np.abs(s_ - sk) < 1.9) & (u >= 11.0 + off) & (u < 27.0 + off)
        col[tip] = col[tip] * 0.4 + np.array([140, 82, 52]) * 0.55
        col[side & (np.abs(s_ - sk - 2.8) < 0.5) & (u > -28.0) & (u < 29.0)] *= 0.6
    waffle = side & (s_ > 14.0) & (s_ < AK_MAG_LEN[rounds] - 14.0) & (np.abs(u) < AK_MAG_D - 5.0)
    col[waffle & ((np.mod(s_, 14.0) < 1.0) | (np.mod(u + 40.0, 13.0) < 1.0))] *= 0.78
    col[side & (n[..., 0] > 0.7) & kit.text_mask(-u, -s_, str(rounds), -6.0, -(AK_MAG_LEN[rounds] - 18.0), 6.0)] *= 0.55


def build_para_magazine(rounds):
    """Straight steel box, origin at the feed lips (top centre), +Y toward the muzzle."""
    b = kit.Builder()
    end = PARA_MAG_LEN[rounds]
    w, d = PARA_MAG_W, PARA_MAG_D
    b.box(-w, w, -d, d, -(end - 6.0), -4.0, mat="magpoly", bevel=1.2)
    b.box(-(w - 3.0), w - 3.0, -(d - 2.0), d - 4.0, -4.0, 0.0, mat="magpoly", bevel=0.6)   # feed lips
    b.box(-(w + 1.2), w + 1.2, -(d + 1.5), d + 2.5, -end, -(end - 6.0), mat="dark", bevel=1.0)  # floor plate
    # the top round: 9x19mm, case 19 mm, bullet forward
    b.lathe("y", (0, -2.0, -5.0), [(-11.0, 0), (-11.0, 4.9), (8.0, 4.9), (8.0, 4.6)], seg=8, mat="brass")
    b.lathe("y", (0, -2.0, -5.0), [(8.0, 4.6), (12.5, 4.2), (16.5, 2.4), (18.0, 0)], seg=8, mat="copper")
    return b.to_object("9x19Magazine%d_AUG" % rounds)


def paint_para_mag(maps, col, rounds):
    """Pressed ribs along both sides, witness holes up the back showing brass."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    x, yy, zz = p[..., 0], p[..., 1], p[..., 2]
    side = (mat == a1.MATS.index("magpoly")) & (np.abs(n[..., 0]) > 0.7)
    col[side & (np.abs(yy - 4.0) < 5.0) & (zz < -12.0) & (zz > -(PARA_MAG_LEN[rounds] - 12.0))] *= 0.8
    col[side & (np.abs(yy - 4.0) < 0.6) & (zz < -12.0) & (zz > -(PARA_MAG_LEN[rounds] - 12.0))] += 22
    for k in range(5, rounds + 1, 5 if rounds < 30 else 4):
        hz = -(10.0 + k * 5.3)
        hole = side & (np.hypot(yy + PARA_MAG_D - 6.0, zz - hz) < 1.8)
        col[hole] = (120, 94, 50)


def paint(maps, kind):
    if isinstance(kind, tuple):                              # ("para_mag" | "ak_mag", rounds)
        p, mat = maps["pos"], maps["mat"]
        col = np.zeros(p.shape, np.float32)
        for i, name in enumerate(a1.MATS):
            col[mat == i] = a1.BASE[name]
        {"para_mag": paint_para_mag, "ak_mag": paint_ak_mag}[kind[0]](maps, col, kind[1])
        return np.clip(a1.common(maps, col, mat), 0, 255)
    return a1.paint(maps, kind)


def texture(maps_list, kinds, size, path):
    """build_aug.texture() with this file's paint() (the Para's magazines)."""
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
    gp, ZERO = a1.gp, a1.ZERO
    rail_top = a1.z(RAIL_TOP) * K
    oy = round(a1.y(OPTIC_L) * K, 4)
    sy = round(a1.y(sum(SIDE_RAIL) / 2.0) * K, 4)
    sz = round(a1.z(SIDE_RAIL_H) * K, 4)
    ly, lz = round(a1.y(sum(LEFT_RAIL) / 2.0) * K, 4), round(a1.z(LEFT_RAIL_H) * K, 4)
    side = (a1.W_RCV + 1.5 + 3.0 - 1.0) * K           # the right rail's crossbar faces (base 1.5, crossbars 3.0)
    hinge = gp(*a1.FG_HINGE)
    muzzle = gp({"para": PARA_MUZZLE, "hbar": HBAR_MUZZLE}.get(GUN, 0.0), a1.BORE)
    pts = {
        "muzzle": {"offset": muzzle, "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(*a1.MAG_LIPS), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-a1.TRAVEL * K, 4) + 0.0, 0.0], "rotate": ZERO},
        "foregrip_deployed": {"offset": hinge, "rotate": ZERO},
        "foregrip_folded": {"offset": hinge, "rotate": [90.0, 0.0, 0.0]},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up and its scopes sit 0.0032 under that rail's
        # top (the MP7's and SCAR's relations)
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)], "rotate": ZERO},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)], "rotate": ZERO},
        # the integral right rail: the SCAR's relations to its crossbar face
        "rail_right": {"offset": [round(-(side - 0.0055), 4), sy, sz], "rotate": ZERO},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), sy, round(sz - 0.0008, 4)], "rotate": ZERO},
        # the optional left rail: AUG_RAIL_LEFT's origin on the receiver's left face; GoM's lights sit 0.0007 out
        # from a rail's crossbar faces (the SCAR's rail_left + 0.0062 with rail_left 0.0055 inside them)
        "rail_left": {"offset": [round(a1.W_RCV * K, 4), ly, lz], "rotate": ZERO},
        "light_left": {"offset": [round((a1.W_RCV + 3.5) * K + 0.0007, 4), ly, lz], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / a1.K_OLD, 4), round(0.13 * K / a1.K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
    }
    if GUN == "para":
        # the main mod's 9x19mm SMG mount device (and its Mk9) start at the collar's front face (the UMP9's relation)
        pts["canon"] = {"offset": gp(PARA_CANON, a1.BORE), "rotate": ZERO}
    elif GUN == "hbar":
        # no muzzle parts (no 7.62x39mm can or device in GoM); the bipod's legs are modelled in the gun's space
        pts["integrated_bipod"] = {"offset": ZERO, "rotate": ZERO}
    else:
        # GoM's AR mount device, as on its M4A1 and our SCAR-L: 0.0187 behind the muzzle
        pts["canon"] = {"offset": [0.0, round(muzzle[1] - 0.0187, 4), muzzle[2]], "rotate": ZERO}
    own = GUN == "para"
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the rear-top of "
                 "the pistol grip (the A1's photo L %.0f, H %.0f)" % (a1.L0, a1.H0),
        "magazine": {"para": "9x19Magazine25/32_AUG (their feed lips), in the A1's well through the adapter",
                     "hbar": "762x39Magazine30_AUG (its feed lips)"}.get(
                         GUN, "the A1's 556x45Magazine30/42_AUG (their feed lips)"),
        "bolt_fired": "%s (the A1's charging handle) back %.0f mm real" % (
            NAME + "_BOLT" if own else "GunsOfTien.AUG_BOLT", a1.TRAVEL),
        "foregrip": "%s (the A1's grip) at its hinge pin; folded = turned 90 degrees forward" % (
            NAME + "_FOREGRIP" if own else "GunsOfTien.AUG_FOREGRIP"),
        "rails": "integral top (L %.0f-%.0f, crossbars H %.0f) and right (L %.0f-%.0f, H %.0f); left = GoM's "
                 "optional Picatinny_Rail_Left, drawn as AUG_RAIL_LEFT (L %.0f-%.0f, H %.1f)" % (
                     RAIL + (RAIL_TOP,) + SIDE_RAIL + (SIDE_RAIL_H,) + LEFT_RAIL + (LEFT_RAIL_H,)),
    }
    if GUN == "para":
        pts["_notes"]["canon"] = ("the barrel collar's front face, %.0f mm behind the muzzle: the 9x19mm SMG mount "
                                  "device and the Mk9" % (PARA_CANON - PARA_MUZZLE))
    elif GUN == "hbar":
        pts["_notes"]["integrated_bipod"] = "AUGHBAR_BIPOD_FOLDED / _DEPLOYED are modelled in the gun's space"
    else:
        pts["_notes"]["canon"] = "GoM's AR mount device and its muzzle parts, 0.0187 behind the muzzle (its M4A1)"
    pts["_extras"] = {"handgun_hold": False, "photo_origin_mm": [a1.L0, a1.H0], "bore_mm": a1.BORE, "k": K}
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

    if GUN == "mags":
        build_magazines()
        return
    body = build_body()
    if GUN == "hbar":
        extra = [build_bipod(False), build_bipod(True)]
        kinds = ["bolt", "bolt"]
    elif GUN == "a3":
        extra = [build_left_rail()]
        kinds = ["bolt"]
    else:
        a1.BASE.update(PARA_COLOURS)
        bolt, fg = a1.build_bolt(), a1.build_foregrip()
        for o, suffix in ((bolt, "_BOLT"), (fg, "_FOREGRIP")):         # object and mesh (the FBX geometry's name)
            o.name = o.data.name = NAME + suffix
        extra = [bolt, fg]
        kinds = ["bolt", "foregrip"]
    kit.unwrap([body] + extra, 0.005)
    # parts with their own origin (the rail at its point, the grip at its pin) are baked alone; the handle and the
    # bipod (in the gun's space) with the body
    near = extra[:1] if GUN in ("para", "hbar") else []
    maps = [a1.bake(body, [body] + near, 256)]
    for o in extra:
        in_gun = o.name.endswith("_BOLT") or "_BIPOD_" in o.name
        maps.append(a1.bake(o, [body, o] if in_gun else [o], 256))
    texture(maps, ["body"] + kinds, 256, os.path.join(TEX_DIR, NAME + ".png"))
    objs = [body] + extra
    bounds = {o.name: kit.bounds_of(o) for o in objs}

    pts = points(bounds)
    with open(os.path.join(HERE, NAME.lower() + "_points.json"), "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(objs, os.path.join(FIRE_DIR, "GunsOfTienPost93_%s.fbx" % NAME))
    for name, bb in bounds.items():
        print("%s %-26s tris %5d  min %s  max %s" % (NAME, name, bb["tris"], bb["min"], bb["max"]))


def build_magazines():
    """Every AUG magazine of this mod in one file: the Para's steel 25 / 32, the HBAR's smoke 7.62x39mm 30 and 50."""
    mags, bounds = [], {}
    point = json.load(open(os.path.join(HERE, "augpara_points.json")))["magazine"]
    for build, rounds, kind, colour in ((build_para_magazine, 25, "para_mag", PARA_COLOURS["magpoly"]),
                                        (build_para_magazine, 32, "para_mag", PARA_COLOURS["magpoly"]),
                                        (build_ak_magazine, 30, "ak_mag", a1.BASE["magpoly"]),
                                        (build_ak_magazine, 50, "ak_mag", a1.BASE["magpoly"])):
        m = build(rounds)
        kit.unwrap([m], 0.012)
        saved = a1.BASE["magpoly"]
        a1.BASE["magpoly"] = colour
        texture([a1.bake(m, [m], 128)], [(kind, rounds)], 128, os.path.join(TEX_DIR, m.name + ".png"))
        a1.BASE["magpoly"] = saved
        bounds[m.name] = kit.bounds_of(m)
        bounds[m.name + "_fitted"] = kit.bounds_at(m, point)
        mags.append(m)
    kit.export(mags, FBX_MAGS)
    for name, bb in bounds.items():
        print("AUG mag %-28s tris %5d  min %s  max %s" % (name, bb["tris"], bb["min"], bb["max"]))


if __name__ == "__main__":
    main()
