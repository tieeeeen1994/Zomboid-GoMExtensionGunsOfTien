"""M249 Light Machine Gun (PIP) models and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_m249.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_M249.fbx         M249_BODY, M249_COVER (the feed cover, drawn closed or
                                                             open at its points), M249_BIPOD_FOLDED, M249_BIPOD_DEPLOYED
    M/models_X/weapons/magazines/GunsOfTien_M249_box.fbx    556x45Box200_M249 (the 200-round box, origin at the
                                                             middle of its top), 556x45_M249_1..9 (the belt from the
                                                             box to the feed tray, in the gun's space)
    M/textures/weapons/GunsOfTien/M249.png                  256, shared by the four gun nodes
    M/textures/weapons/GunsOfTien/556x45Box200_M249.png     128, the box and the nine belt rounds
    scripts/m249_points.json                                attachment points (game space)

The PIP M249 (user, 2026-10-22: "M249E2", the informal name of a gun with the Product Improvement kit): M240-style
polymer stock, heat shield over the barrel, folding carrying handle, PIP handguard, no rails. Traced from the US Air
Force's public-domain side photo "M249 Automatic Rifle" (Wikimedia Commons File:M249_Automatic_Rifle.jpg, the right
side (cocking handle, ejection side; muzzle right), bipod down, no box), turned 13.0 degrees clockwise so the bore is level and scaled to the field manual's
1038 mm overall (FM 23-14, 1994, Table 1-2): 3.817 px/mm. Profiles are written in that photo's (L, H) mm: L back from
the muzzle tip, H up from the lowest point (the bipod's foot). The bore is at H 321.
The 200-round box (olive drab plastic, clipped under the receiver, the belt rising from it into the feed tray on the
left) is from the US Army's 1985 photo DA-SC-85-11586 and the USMC's 1989 photo DM-ST-90-02821 (its stencil); its size
(112 x 88 x 165 mm) is read off those photos against the gun, no published drawing.

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, drawn at 0.603 of real size, the M16A2's proportion (0.65 before 2026-10-26, as GoM draws most of its rifles) (the SCARs too; GoM's STANAG
magazines then match). GoM's M60 is the pattern for the belt: nine visible round nodes in the gun's own space, shown
one per round left in the box from nine down.
"""

import sys as _sys
_sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_M249.fbx")
FBX_BOX = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_M249_box.fbx")
POINTS_JSON = os.path.join(HERE, "m249_points.json")

K = 0.000603                       # game units per real mm: the M16A2's proportion (user, 2026-10-26: our guns resized in their meshes; was 0.00065, GoM's rifles)
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "polymer", "metal", "dark", "rubber", "od", "brass", "copper", "link"]
kit.MATS[:] = MATS
for ch, rows in {"C": ["111", "100", "100", "100", "111"], "T": ["111", "010", "010", "010", "010"],
                 "O": ["111", "101", "101", "101", "111"], "5": ["111", "100", "111", "001", "111"],
                 "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
                 "-": ["000", "000", "111", "000", "000"], "L": ["100", "100", "100", "100", "111"],
                 "B": ["110", "101", "110", "101", "110"], "U": ["101", "101", "101", "101", "111"],
                 "H": ["101", "101", "111", "101", "101"]}.items():
    kit.FONT.setdefault(ch, rows)

# Photo coordinates (mm) of the model origin: the grip's back edge meets the trigger housing. game y = L0 - L,
# z = H - H0.
L0, H0 = 707.0, 251.0
BORE = 321.0
GAS = 291.0                        # the gas cylinder's axis under the barrel
HINGE = (480.0, 352.0)             # the feed cover's hinge, at its front
BOX_TOP = (538.0, 270.0, 33.0)     # middle of the box's top: L, H, x (left of centre, as the box hangs)
BOX_L, BOX_W, BOX_H = 112.0, 88.0, 165.0
MAG_LIPS = (535.0, 290.0, 12.0)    # where a STANAG's feed lips sit: L, H, x
MAG_TILT = -45.0                   # its well slants down to the left, 45 degrees (rotate about Y, game space)
COVER_OPEN = -70.0                 # the feed cover swung up about its hinge (rotate about X)
PIVOT = (255.0, 266.0, 11.0)       # bipod leg pivots: L, H, |x|
W_RECV, W_COVER, W_TRIG, W_GRIP, W_STOCK, W_HG, W_SHIELD = 27.0, 28.0, 15.0, 15.0, 20.0, 30.0, 22.0

# the belt: centre (x, H) of each round on its way from the tray (1, inside the receiver, seen with the cover open) to
# the box's mouth (9); the rounds lie along the bore, case heads at L 545
BELT = [(10.0, 322.0), (22.0, 322.0), (33.0, 320.0), (43.0, 316.0), (51.0, 309.0), (56.0, 300.0), (58.0, 290.0),
        (57.0, 280.0), (55.0, 270.0)]
ROUND_HEAD_L = 545.0


def P(L, H):
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def box(b, La, Lb, Ha, Hb, xa, xb, mat="steel", bevel=0.0, xf=None):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel, xf=xf)


def lathe_y(b, H, profile, seg=16, mat="metal", x=0.0, bevel=0.0):
    """Revolved about a line along the barrel at height H: profile [(L, radius)] from the rear forward."""
    b.lathe("y", (x, 0, H - H0), [(L0 - L, r) for L, r in profile], seg=seg, mat=mat, phase=0.5, bevel=bevel)


def both(fn):
    for s in (1, -1):
        fn(s)


def along(p0, p1):
    """Matrix taking +Y (length |p1 - p0|) from the origin onto the segment p0 -> p1 (game mm)."""
    d = Vector(p1) - Vector(p0)
    return Matrix.Translation(Vector(p0)) @ Vector((0, 1, 0)).rotation_difference(d.normalized()).to_matrix().to_4x4(), \
        d.length


def gpt(L, H, x=0.0):
    return Vector((x, L0 - L, H - H0))


# ==================================================================================================
# Profiles (photo L, H mm)
# ==================================================================================================

# the receiver: steel box from the barrel's trunnion back to the buttstock plate; its top under the feed cover
RECV = [(482.0, 274.5), (482.0, 346.5), (712.0, 346.5), (712.0, 356.0), (740.0, 357.5), (765.0, 351.0),
        (784.0, 344.0), (786.0, 330.0), (781.0, 307.0), (775.0, 290.0), (770.0, 272.0), (764.0, 263.0),
        (756.0, 260.0), (712.0, 257.0), (712.0, 272.0), (584.0, 272.0), (582.0, 274.5)]
TRIG_HOUSING = [(584.0, 250.5), (584.0, 273.0), (713.0, 273.0), (713.0, 250.5)]
COVER = [(480.0, 346.5), (480.0, 357.0), (484.0, 362.0), (490.0, 362.0), (495.0, 356.5), (538.0, 356.5),
         (540.0, 361.0), (565.0, 361.0), (566.0, 356.5), (712.0, 356.5), (712.0, 346.5)]
REAR_SIGHT = [(646.0, 355.0), (646.0, 372.0), (649.0, 374.6), (651.0, 377.0), (684.0, 385.6), (693.5, 385.6),
              (700.0, 382.8), (707.0, 375.7), (709.0, 370.7), (711.0, 364.0), (711.0, 355.0)]
APERTURE = (690.0, 371.0, 6.0)
STOCK = [(784.0, 263.0), (821.0, 263.0), (845.0, 260.0), (883.0, 252.0), (891.0, 247.0), (894.0, 240.5),
         (894.0, 233.7), (890.0, 226.0), (888.0, 218.0), (889.7, 214.6), (893.4, 211.4), (899.7, 209.9),
         (978.5, 206.2), (1000.0, 204.6), (1013.0, 203.8), (1016.0, 205.4), (1020.5, 214.0), (1021.0, 236.8),
         (1021.0, 325.0), (1019.0, 331.0), (1005.0, 334.3), (971.0, 330.1), (940.0, 327.5), (926.0, 321.5),
         (916.0, 309.7), (903.0, 302.3), (892.0, 301.3), (827.0, 315.2), (812.0, 322.0), (786.0, 338.0)]
BUTTPLATE = [(1019.0, 205.0), (1027.0, 206.0), (1031.0, 215.0), (1031.0, 326.0), (1027.0, 334.5), (1019.0, 334.5)]
GRIP = [(652.0, 252.0), (646.0, 224.0), (671.0, 164.0), (672.5, 155.6), (670.0, 148.3), (671.0, 145.0),
        (674.0, 143.3), (680.4, 143.0), (700.0, 146.7), (711.0, 149.3), (728.0, 154.0), (733.0, 156.4),
        (736.0, 159.3), (736.0, 162.0), (733.0, 164.5), (728.6, 171.6), (697.0, 225.3), (694.5, 232.0),
        (695.3, 239.0), (700.3, 245.7), (705.5, 248.1), (707.4, 250.7), (713.0, 252.0)]
TRIGGER = [(643.0, 251.0), (636.0, 240.0), (630.0, 232.0), (624.0, 225.0), (620.0, 222.0), (617.0, 224.0),
           (622.0, 232.0), (628.0, 242.0), (632.0, 251.0)]
GUARD = [(646.0, 224.0), (641.0, 216.0), (604.0, 215.0), (597.0, 218.5), (598.0, 222.0), (605.0, 218.5),
         (640.0, 219.0), (643.5, 226.0)]
GUARD_FRONT = [(596.0, 251.0), (596.0, 236.0), (604.0, 229.0), (616.0, 234.0), (612.0, 238.0), (604.0, 237.0),
               (601.0, 242.0), (604.0, 251.0)]
HANDGUARD = [(483.0, 276.0), (483.0, 253.0), (478.0, 246.0), (472.0, 241.3), (345.0, 241.3), (345.0, 303.0),
             (345.0, 331.0), (472.0, 331.0), (483.0, 336.0)]
HG_CAP = [(346.0, 241.0), (338.0, 240.5), (331.0, 242.0), (329.0, 246.0), (328.0, 266.0), (330.0, 300.0),
          (346.0, 303.0)]
SHIELD = [(285.0, 331.0), (285.0, 347.0), (290.0, 352.0), (472.0, 352.0), (476.0, 348.0), (476.0, 331.0)]
FRONT_SIGHT = [(215.0, 322.0), (215.0, 346.0), (207.0, 362.0), (206.5, 382.0), (191.0, 382.5), (190.0, 372.0),
               (192.0, 362.0), (192.0, 336.0), (190.0, 322.0)]
FS_HOLES = [[(200.0, 368.0), (200.0, 378.0), (195.0, 378.0), (195.0, 368.0)],
            [(207.0, 340.0), (207.0, 351.0), (198.0, 351.0), (198.0, 340.0)]]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    slab(b, RECV, half=W_RECV, bevel=1.5, mat="steel")
    slab(b, TRIG_HOUSING, half=W_TRIG, bevel=1.2, mat="steel")
    # buttstock plate on the receiver's back, the M240-style polymer stock and its rubber butt pad
    slab(b, [(776.0, 262.0), (790.0, 262.0), (792.0, 345.0), (778.0, 347.0)], half=W_RECV + 1.0, bevel=1.5,
         mat="metal")
    slab(b, STOCK, half=W_STOCK, bevel=3.5, res=1, mat="polymer")
    slab(b, BUTTPLATE, half=W_STOCK + 1.0, bevel=2.0, res=1, mat="rubber")
    slab(b, GRIP, half=W_GRIP, bevel=4.0, res=1, mat="polymer")
    slab(b, TRIGGER, half=2.6, bevel=0.6, mat="dark")
    slab(b, GUARD, half=3.5, bevel=0.6, mat="steel")
    slab(b, GUARD_FRONT, half=7.0, bevel=0.8, mat="steel")
    # feed tray lip where the belt comes in on the left, under the cover
    box(b, 488.0, 560.0, 298.0, 302.5, W_RECV - 1.0, W_RECV + 5.0, mat="steel", bevel=0.8)
    # magazine well for STANAG magazines: a sleeve slanting down to the left from the feed lips
    lips = gpt(MAG_LIPS[0], MAG_LIPS[1], MAG_LIPS[2])
    tilt = Matrix.Translation(lips) @ Matrix.Rotation(math.radians(MAG_TILT), 4, 'Y') @ Matrix.Translation(-lips)
    ya, yb = L0 - 572.0, L0 - 480.0
    z0, z1 = lips.z - 30.0, lips.z - 6.0
    for xa, xb in ((lips.x - 17.0, lips.x - 13.0), (lips.x + 13.0, lips.x + 17.0)):
        b.box(xa, xb, ya, yb, z0, z1, mat="steel", bevel=0.6, xf=tilt)
    for y0, y1 in ((ya, ya + 4.0), (yb - 4.0, yb)):
        b.box(lips.x - 17.0, lips.x + 17.0, y0, y1, z0, z1, mat="steel", bevel=0.6, xf=tilt)
    # cocking handle on the right, at the front of its slot (it does not move when firing)
    box(b, 494.0, 524.0, 303.0, 318.0, -W_RECV + 1.0, -W_RECV - 9.0, mat="steel", bevel=1.0)
    b.lathe("x", (-W_RECV - 9.0, *P(506.0, 311.0)), [(0.0, 0.0), (0.0, 7.0), (-10.0, 7.0), (-11.0, 5.5),
                                                     (-11.0, 0.0)], seg=12, mat="dark")
    # forward: PIP handguard and its front cap, the heat shield over the barrel
    slab(b, HANDGUARD, half=W_HG, bevel=3.0, res=1, mat="polymer")
    slab(b, HG_CAP, half=W_HG + 0.8, bevel=1.5, mat="metal")
    slab(b, SHIELD, half=W_SHIELD, bevel=1.8, mat="steel")
    # barrel (from inside the receiver), flash hider, front sight block, gas block
    lathe_y(b, BORE, [(490.0, 0.0), (490.0, 12.0), (330.0, 12.0), (330.0, 10.0), (190.0, 10.0), (189.0, 8.5),
                      (122.0, 8.5), (67.0, 6.5), (51.0, 6.5), (50.0, 9.5), (46.0, 10.2), (4.0, 10.2), (0.0, 9.5),
                      (0.0, 4.2), (6.0, 4.2), (6.0, 0.0)], seg=16, mat="metal")
    slab(b, FRONT_SIGHT, FS_HOLES, half=6.0, bevel=0.8, mat="steel")
    box(b, 215.0, 330.0, 282.0, 322.0, -13.0, 13.0, mat="metal", bevel=2.0)
    # gas cylinder and regulator under the barrel, with the bipod's clamp
    lathe_y(b, GAS, [(330.0, 0.0), (330.0, 12.0), (232.0, 12.0), (230.0, 14.0), (184.0, 14.0), (182.0, 11.0),
                     (180.0, 13.5), (167.0, 13.5), (165.0, 11.5), (165.0, 0.0)], seg=16, mat="metal")
    lathe_y(b, GAS, [(280.0, 0.0), (280.0, 17.0), (238.0, 17.0), (238.0, 0.0)], seg=16, mat="metal")
    box(b, 245.0, 265.0, PIVOT[1] - 6.0, GAS - 14.0, -16.0, 16.0, mat="steel", bevel=1.5)
    # carrying handle (PIP, folding; up as photographed): its pivot on the heat shield, the arm, the rubber grip
    lathe_y(b, 353.5, [(470.0, 0.0), (470.0, 8.5), (421.0, 8.5), (421.0, 0.0)], seg=12, mat="steel")
    box(b, 378.0, 422.0, 349.0, 357.0, -3.5, 3.5, mat="steel", bevel=1.0)
    box(b, 374.0, 382.0, 352.0, 402.0, -3.5, 3.5, mat="steel", bevel=1.0)
    centre = gpt(417.0, 414.0)
    rot = kit.rot_x(-16.7, centre)
    b.lathe("y", tuple(centre), [(-47.0, 0.0), (-47.0, 9.5), (45.0, 9.5), (47.0, 8.0), (47.0, 0.0)], seg=14,
            mat="rubber", xf=rot)
    return b.to_object("M249_BODY")


def build_cover():
    """The feed cover with the rear sight, origin at its hinge (front): cover y = HINGE L - L, z = H - HINGE H."""
    b = kit.Builder()
    q = lambda pts: [(HINGE[0] - L, H - HINGE[1]) for L, H in pts]
    kit.slab(b, q(COVER), [], W_COVER, 1.2, 0, "steel", 0.0)
    a_l, a_h, a_r = APERTURE
    hole = [(a_l + a_r * math.cos(2 * math.pi * k / 12), a_h + a_r * math.sin(2 * math.pi * k / 12))
            for k in range(12)]
    kit.slab(b, q(REAR_SIGHT), [q(hole)], 10.0, 1.0, 0, "steel", 0.0)
    # latch block at the back of the cover, the two latch buttons on its sides
    b.box(-W_COVER - 1.5, W_COVER + 1.5, HINGE[0] - 712.0, HINGE[0] - 702.0, 356.5 - HINGE[1] - 9.0,
          356.5 - HINGE[1] + 1.5, mat="steel", bevel=1.0)
    return b.to_object("M249_COVER")


def leg(b, p0, p1):
    xf, n = along(p0, p1)
    b.lathe("y", (0, 0, 0), [(0.0, 0.0), (0.0, 5.5), (n * 0.55, 5.5), (n * 0.55 + 1.0, 4.5), (n, 4.5), (n, 0.0)],
            seg=10, mat="steel", xf=xf)
    b.box(-9.0, 9.0, n - 5.0, n + 2.0, -3.0, 3.0, mat="dark", bevel=0.8, xf=xf)        # the foot
    b.box(-6.5, 6.5, -2.0, 14.0, -6.5, 6.5, mat="steel", bevel=1.0, xf=xf)              # the hinge knuckle


def build_bipod(deployed):
    b = kit.Builder()
    for s in (1, -1):
        p0 = gpt(PIVOT[0], PIVOT[1], s * PIVOT[2])
        p1 = gpt(232.0, 22.0, s * 100.0) if deployed else gpt(60.0, PIVOT[1], s * PIVOT[2])
        leg(b, p0, p1)
    return b.to_object("M249_BIPOD_DEPLOYED" if deployed else "M249_BIPOD_FOLDED")


def build_box():
    """The 200-round box in its own frame: origin at the middle of its top, +Y forward, +X the gun's left."""
    b = kit.Builder()
    hl, hw, h = BOX_L / 2.0, BOX_W / 2.0, BOX_H
    b.box(-hw, hw, -hl, hl, -h, -7.0, mat="od", bevel=3.0)
    b.box(-hw - 1.2, hw + 1.2, -hl - 1.2, hl + 1.2, -9.0, 0.0, mat="od", bevel=2.0)         # the lid
    b.box(-hw - 3.0, -hw + 0.5, -14.0, 14.0, -40.0, -6.0, mat="dark", bevel=1.0)             # latch, inner side
    b.box(-hw + 6.0, -hw + 22.0, -hl + 8.0, hl - 8.0, 0.0, 6.0, mat="od", bevel=1.5)         # dovetail rail
    for y in (-hl + 10.0, hl - 10.0):                                                         # carrying strap loops
        b.box(hw - 2.0, hw + 3.0, y - 6.0, y + 6.0, -30.0, -18.0, mat="od", bevel=1.0)
    return b.to_object("556x45Box200_M249")


def build_round(i, x, H):
    """One 5.56x45 M855 round of the belt with its M27 link, lying along the bore, case head at ROUND_HEAD_L."""
    b = kit.Builder()
    y0 = L0 - ROUND_HEAD_L
    c = (x, 0.0, H - H0)
    b.lathe("y", c, [(y0, 0.0), (y0, 4.6), (y0 + 1.2, 4.6), (y0 + 1.3, 4.0), (y0 + 2.6, 4.0), (y0 + 3.4, 4.7),
                     (y0 + 36.5, 4.5), (y0 + 39.5, 3.1), (y0 + 44.7, 3.1)], seg=8, mat="brass")
    b.lathe("y", c, [(y0 + 44.7, 2.9), (y0 + 50.0, 2.6), (y0 + 54.5, 1.4), (y0 + 57.4, 0.0)], seg=8, mat="copper")
    b.box(x - 5.4, x + 5.4, y0 + 8.0, y0 + 20.0, H - H0 - 5.4, H - H0 + 5.4, mat="link")
    return b.to_object("556x45_M249_%d" % i)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: phosphated steel, black polymer, a greyer barrel and gas parts, OD box, brass, copper, links
    "steel": (56, 56, 58), "polymer": (46, 46, 48), "metal": (70, 70, 72), "dark": (22, 22, 23),
    "rubber": (36, 36, 37), "od": (86, 88, 64), "brass": (158, 126, 66), "copper": (146, 90, 56),
    "link": (40, 40, 42),
}
YELLOW = (196, 170, 70)


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def common(maps, col, mat):
    """build_scar.py's weathering: grain, mottling, light AO, bright worn edges."""
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "brass", "copper", "link")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.97 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 80.0, 40.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
    wear = np.where(mat == MATS.index("od"), 40.0, wear)
    col += (convex * wear)[..., None] * np.array([1.0, 0.98, 0.94])
    col *= (1.0 - 0.3 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.7
    left, right, top = n[..., 0] > 0.7, n[..., 0] < -0.7, n[..., 2] > 0.7
    steel = mat == MATS.index("steel")
    poly = mat == MATS.index("polymer")
    if kind == "body":
        L, H = L0 - y, z + H0
        recv = steel & side & (np.abs(x) > W_RECV - 0.6) & (L > 482) & (L < 786)
        # the belt's way in under the cover on the left, the cocking handle's slot on the right, the ejection port
        # under the right side
        col[recv & left & rounded_rect(L, H, 494.0, 556.0, 312.0, 342.0, 2.0)] = 12
        col[recv & right & rounded_rect(L, H, 494.0, 640.0, 304.0, 310.0, 2.5)] = 12
        col[steel & (n[..., 2] < -0.7) & (x < -4.0) & (x > -W_RECV + 2.0) & (L > 548.0) & (L < 600.0)] = 10
        # rivets and pins along the receiver, the stamped markings on its left
        for cL in (500.0, 560.0, 620.0, 680.0, 740.0, 772.0):
            pin(col, L, H, recv, cL, 280.0)
        for cL, cH in ((590.0, 335.0), (650.0, 335.0), (760.0, 300.0), (600.0, 260.0), (700.0, 262.0)):
            pin(col, L, H, recv | (steel & side & (np.abs(x) > W_TRIG - 0.6)), cL, cH, 3.0)
        # on the right, as photographed; text there reads toward the muzzle in game (u = -L)
        for text, h in (("MG 5.56MM M249", 291.0), ("FN MFG INC", 283.0)):
            col[recv & right & kit.text_mask(-L, H, text, -728.0, h, 4.5)] += 55
        # heat shield vents, the handguard's ribs, the grip's grooves
        sh = steel & (np.abs(x) <= W_SHIELD + 0.5) & (L > 284.0) & (L < 477.0) & (H > 330.0)
        for k in range(11):
            cL = 300.0 + k * 16.0
            col[sh & side & (np.hypot((L - cL) / 4.5, (H - 343.0) / 2.6) < 1.0)] = 8
            col[sh & top & (np.hypot((L - cL) / 4.5, x / 6.0) < 1.0)] = 8
        hg = poly & side & (np.abs(x) > W_HG - 1.0) & (L > 345.0) & (L < 483.0)
        for hh in (258.0, 270.0, 282.0, 294.0):
            col[hg & (np.abs(H - hh) < 1.2) & (L > 352.0) & (L < 468.0)] *= 0.5
        grip = poly & side & (L > 645.0) & (L < 737.0) & (H < 250.0)
        for hh in np.arange(162.0, 222.0, 6.0):
            col[grip & (np.abs(H - hh) < 1.0)] *= 0.55
        # carrying handle grip: rubber rings
        rub = mat == MATS.index("rubber")
        col[rub & (L < 470.0) & (np.mod(L, 9.0) < 2.2)] *= 0.6
        # barrel: the bore and the flash hider's slots; the front sight's post
        metal = mat == MATS.index("metal")
        r = np.hypot(x, H - BORE)
        ang = np.mod(np.arctan2(x, H - BORE) / (2 * math.pi) * 6.0, 1.0)
        col[metal & (L > 5.0) & (L < 26.0) & (r > 9.4) & (np.abs(ang - 0.5) < 0.13)] = 8
        col[metal & (r < 4.6) & (L < 6.5)] = 6
        col[steel & (np.abs(x) < 6.5) & (L > 189.0) & (L < 216.0) & (H > 362.0)] *= 0.8
    elif kind == "cover":
        L, H = HINGE[0] - y, z + HINGE[1]
        cov = steel & side & (np.abs(x) > W_COVER - 0.6)
        for cL in (500.0, 600.0, 700.0):
            pin(col, L, H, cov, cL, 351.5, 2.2)
        col[steel & top & (np.abs(x) < W_COVER - 3.0) & (np.abs(L - 590.0) < 0.8)] *= 0.55
        col[steel & (np.abs(x) > W_COVER + 0.8) & (L > 700.0)] *= 1.25                 # the latch buttons
    elif kind == "bipod":
        pass
    elif kind == "box":
        od = mat == MATS.index("od")
        face = od & left & (x > BOX_W / 2.0 - 0.6)
        u, v = -y, z                                     # reads from the muzzle end toward the stock (game view)
        u0 = -BOX_L / 2.0 + 10.0
        for k, text in enumerate(("200 CARTRIDGES", "5.56 MM", "4-M855-1-M856", "M27", "FOR MG M249")):
            col[face & kit.text_mask(u, v, text, u0, -32.0 - k * 15.0, 7.0)] = YELLOW
        col[face & (np.hypot(u - (u0 + 70.0), v + 108.0) < 4.0)] = YELLOW               # the ball / tracer marks
        col[face & rounded_rect(u, v, u0 + 64.0, u0 + 82.0, -95.0, -90.0, 1.0)] = YELLOW
        # the belt's mouth on top, on the outer side of the lid
        col[od & top & (x > 12.0) & (x < 34.0) & (np.abs(y) < BOX_L / 2.0 - 12.0) & (z > -1.0)] = 14
    elif kind == "round":
        cop = mat == MATS.index("copper")
        tip = cop & ((L0 - y) < ROUND_HEAD_L - 52.5)                                      # M855: green tip
        col[tip] = (70, 112, 60)
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

def gp(L, H, x=0.0):
    return [round(x * K, 4) + 0.0, round((L0 - L) * K, 4) + 0.0, round((H - H0) * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]


def points(bounds):
    hinge = gp(*HINGE)
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(MAG_LIPS[0], MAG_LIPS[1], MAG_LIPS[2]), "rotate": [0.0, MAG_TILT, 0.0]},
        "box": {"offset": gp(BOX_TOP[0], BOX_TOP[1], BOX_TOP[2]), "rotate": ZERO},
        "belt": {"offset": ZERO, "rotate": ZERO},
        "cover": {"offset": hinge, "rotate": ZERO},
        "cover_open": {"offset": hinge, "rotate": [COVER_OPEN, 0.0, 0.0]},
        "integrated_bipod": {"offset": ZERO, "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0], "rotate": [180.0, 0.0, 180.0]},  # every GoM rifle's, scaled with the gun
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size, the M16A2's proportion); +Y muzzle, +Z top, +X the gun's left; origin = the "
                 "rear-top of the pistol grip (photo L %.0f, H %.0f)" % (L0, H0),
        "magazine": "GoM's STANAG magazines, their feed lips here, slanting %g degrees down to the left" % -MAG_TILT,
        "box": "556x45Box200_M249, origin at the middle of its top",
        "belt": "556x45_M249_1..9 are modelled in the gun's space (GoM's M60 way)",
        "cover": "M249_COVER, origin at its hinge; cover_open swings it up %g degrees" % -COVER_OPEN,
        "integrated_bipod": "M249_BIPOD_FOLDED / _DEPLOYED are modelled in the gun's space",
    }
    # hand targets for the reload clips (game units, gun space)
    pts["_extras"] = {
        "handgun_hold": False, "photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K,
        "real_mm_per_game_unit": round(1.0 / K, 2),
        "cover_latch": gp(706.0, 357.0), "cover_front": gp(560.0, 360.0),
        "tray_entry": gp(520.0, 322.0, W_RECV + 4.0), "box_top_outer": gp(BOX_TOP[0], BOX_TOP[1], BOX_TOP[2] + 30.0),
        "box_bottom": gp(BOX_TOP[0], BOX_TOP[1] - BOX_H, BOX_TOP[2]),
        "cocking_handle": gp(506.0, 311.0, -W_RECV - 16.0), "carry_handle": gp(417.0, 414.0),
        "handguard_left": gp(410.0, 290.0, W_HG + 2.0),
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

    body, cover = build_body(), build_cover()
    bip_f, bip_d = build_bipod(False), build_bipod(True)
    bx = build_box()
    rounds = [build_round(i + 1, x, H) for i, (x, H) in enumerate(BELT)]
    gun = [body, cover, bip_f, bip_d]
    kit.unwrap(gun, 0.004)
    kit.unwrap([bx] + rounds, 0.008)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture(gun, [[o] for o in gun], ["body", "cover", "bipod", "bipod"], 256, os.path.join(TEX_DIR, "M249.png"))
    texture([bx] + rounds, [[o] for o in [bx] + rounds], ["box"] + ["round"] * len(rounds), 128,
            os.path.join(TEX_DIR, "556x45Box200_M249.png"))

    bounds = {o.name: kit.bounds_of(o) for o in gun + [bx] + rounds}
    pts = points(bounds)
    bounds["M249_COVER_closed"] = kit.bounds_at(cover, pts["cover"])
    bounds["M249_COVER_open"] = kit.bounds_at(cover, pts["cover_open"])
    bounds["556x45Box200_M249_fitted"] = kit.bounds_at(bx, pts["box"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export([bx] + rounds, FBX_BOX)
    for name, bd in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
