"""A-91M Prototype: KBP's first A-91M, its 40 mm launcher OVER the barrel, for Guns of Tien - Post-93 (Blender 5.2).

    blender -b --factory-startup -P scripts/post93/build_a91m_proto.py -- [--size 1024]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_A91MPROTO.fbx  A91MPROTO_BODY (the launcher's sight leaf folded),
                                                             A91MPROTO_BODY_GL (the same body, the leaf raised: the
                                                             launcher weapon's model), A91MPROTO_BOLT (the charging
                                                             hook on the gas tube, under the carrying handle),
                                                             A91MPROTO_RAIL_UP (GoM's rail on our clamp on the handle)
    M/textures/weapons/GunsOfTienPost93/A91MPROTO.png           512 atlas
    scripts/post93/a91m_proto_points.json                        attachment points (game space)

User, 2026-11-25: "GoT A-91 7.62 version with the launcher on top". The real gun is a 7.62x39 one (Modern Firearms'
"7.62-A91M"); in the game it is the "A-91M Prototype", the longer-barrelled gun of the two, in 7.62x54R on the
SV-98's magazines, a 20-round one made for it (the user's choice the same day: an invented chambering, so the photo's
AK magazine is not drawn). Three
remodel passes and then the user's corrections from crops of the renders (the guard's bright wedge
is shine, not a gap; no slits between bodies; the launcher sits on the beam): CLAUDE.md "7.62-A91M". The helpers,
materials and the handle clamp are build_a91m.py's; only the photo frame and the gun are this file's.

References in references/a91 (SOURCES.txt). The measuring photo is Modern Firearms' 762-a91m.jpg (1024 px, the RIGHT
side, muzzle right); references/a91/top_launcher/zonwar_A-91.jpg is a second photo of the same gun with the leaf
folded. No photo shows its left side, top or front: the left is the right without the selector, the widths are the
A-91M's. Scale: 1.289 px a mm, from fitting GoM's AK-47 magazine's outline to the photo's magazine (IoU 0.53 with
the receiver in the box, the outlines within a pixel; the same fit puts the A-91M's photo at 1.2425), which makes
the gun about 760 mm long: a longer gun than the later A-91M (660 mm), as its proportions against the magazine show.
Every profile below is in the photo's pixels (x forward, y down), read from 5-14x gridded crops.
Origin: the grip's rear top (the A-91M's), so the hands sit as on GoM's FAMAS.

GoM's rifle conventions: upright, +Y muzzle, +Z top, +X the gun's LEFT, 0.603 of real size.
"""

import sys as _sys
_sys.dont_write_bytecode = True
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_a91m as base  # noqa: E402  (sets kit.K and kit.MATS)

kit = base.kit
K = base.K
MATS = base.MATS
ZERO = [0.0, 0.0, 0.0]
GUN = "A91MPROTO"
FBX_GUN = os.path.join(kit.MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_A91MPROTO.fbx")
POINTS_JSON = os.path.join(HERE, "a91m_proto_points.json")

# ==================================================================================================
# Photo frame: px -> game (y forward, z up) mm. build_a91m.py's helpers read these through its module globals
# ==================================================================================================

S = 1.289                          # px a mm (GoM's AK-47 magazine fitted to the photo's)
ORIGIN = (449.0, 252.0)            # the grip's rear top
BORE = 206.5                       # the bore's row
LX = -4.0                          # mm: the launcher sits a little to the right (Small Arms Review, 1998)
LAUNCH = 154.0                     # the launcher's axis row
# The game's gun is not the photo's: it is the 7.62x54R "prototype", built without a reference from the photo's
# 7.62x39 gun the way a maker scales a rifle up for a longer round (the SCAR-L to the SCAR-H: a longer magazine well
# and receiver, a heavier and longer barrel, a bigger muzzle device; user, 2026-11-25: "work on this without
# references. Just know the calibre and make some parts longer"). The round is 21 mm longer than the 7.62x39.
REAR = -30.0                       # px: everything behind the magazine well's front moves back 23 mm (well + bolt travel)
REAR_FROM = 300.0                  # the photo's magazine well front: what is behind it moves
BARREL = 45.0                      # px: the barrel 35 mm longer ahead of the launcher's front plate
# The scale is from GoM's AK magazine fitted to the photo's (origin 258.8, 279.2, tilt 4.25 degrees: the whole of
# GoM's magazine on the photo's seen part). The game's gun takes the SV-98's magazines (build_sv98.py's 10 and
# build_sv98_mag20.py's 20; GoM's SVD magazine at first): their origin is the feed lips' front, the box 94 mm long
# behind it and 3 mm above it. In the photo's frame: the rear on the magazine catch (x 222 + REAR), the top 15 mm
# inside the receiver (its bottom at row 268), upright
MAG_FIT = (222.0 + REAR + 94.0 * S, 268.0 - 12.0 * S, 0.0)
REC_HALF = 16.5                    # mm: the receiver's half width, over the magazines' 15 (the photo gun's: 15)


def P(x, y):
    return (x - ORIGIN[0]) / S, (ORIGIN[1] - y) / S


base.S, base.ORIGIN, base.BORE, base.P = S, ORIGIN, BORE, P
PL, mm, slab, boss, pxbox, rrect = base.PL, base.mm, base.slab, base.boss, base.pxbox, base.rrect


def lathe(b, axis_y, prof_px, seg=16, mat="metal", x0=0.0, phase=0.5):
    """prof_px: [(photo x, radius px)] along the bore at photo row axis_y, the axis x0 mm off the centre."""
    b.lathe("y", (x0, 0.0, P(0.0, axis_y)[1]), [(P(x, axis_y)[0], mm(r)) for x, r in prof_px], seg=seg, mat=mat,
            phase=phase)


def turned(pts, hinge, deg):
    """Photo points turned about `hinge` by deg (clockwise on the photo, y down)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(hinge[0] + (x - hinge[0]) * c - (y - hinge[1]) * s, hinge[1] + (x - hinge[0]) * s + (y - hinge[1]) * c)
            for x, y in pts]


# ==================================================================================================
# The gun's profiles (Modern Firearms 762-a91m.jpg px)
# ==================================================================================================

G = dict(
    # ---- the upper: butt, cheek cover, receiver, the selector on the right, the magazine catch ----
    # its joint with the receiver's rounded rear end is an arc (8x crop); the receiver runs 3 px under it, so the
    # three bodies that meet there (cover, butt, receiver) leave no slit (user, 2026-11-25: "holes")
    butt=[(16, 190), (20, 183), (36, 178), (41, 192), (50, 207), (58, 222), (63, 240), (66, 254), (76, 267),
          (100, 275), (92, 290), (80, 312), (70, 345), (66, 358), (58, 365), (42, 365), (35, 357), (30, 320),
          (23, 255), (17, 215)],
    butt_boss=(47.0, 244.0, 11.0),
    butt_fold=[(41, 192), (50, 207), (58, 222), (63, 240), (66, 254), (76, 267)],
    loop=(100.0, 304.5, 8.0, 3.5),                     # the sling loop on the leg's front edge: centre, outer / inner r
    loop_stem=[(84, 298), (94, 299), (94, 307), (82, 305)],
    # x from, to; at x = 200: top, the chamfer's foot, bottom; the top's half width; its rise forward (px a px)
    cover=(36.0, 363.0, 174.4, 199.0, 213.5, 9.5, 6.5 / 294.0),
    pad=(122.0, 177.0, 238.0, 197.0, 9.0),             # the cheek pad on the cover's chamfer
    hump=[(326, 173), (331, 165), (338, 155), (345, 149), (350, 148), (363, 148), (363, 176)],
    receiver=[(47, 214), (363, 208.5), (363, 268), (182, 268), (182, 286), (120, 286), (113, 280), (100, 277),
              (73, 266), (63, 254), (60, 240), (55, 222)],
    # the AK-style selector on the right (Modern Firearms; Small Arms Review 1998): a housing plate, the lever's
    # pointer over it, the marks ahead of its tip
    selector=[(110, 250), (118, 240), (165, 226), (182, 220), (228, 236), (270, 248.5), (232, 256), (200, 272),
              (180, 283), (120, 283), (113, 268)],
    pointer=[(222, 233), (270, 248.5), (218, 258)],
    # raised heads: the receiver's cross pin (both sides); on the selector's plate two rivets and a screw
    rec_pin=(309.0, 238.0, 4.5),
    plate_heads=((157.0, 237.0, 2.6), (168.0, 241.0, 2.6), (175.0, 273.0, 3.0)),
    catch=[(180, 265), (222, 265), (222, 316), (214, 319), (168, 319), (170, 313), (180, 300), (185, 286)],
    # the receiver's front plate, the handle's rear leg on it, the gas tube's socket
    plate=(363.0, 373.0, 148.0, 270.0),
    leg=[(364, 104), (373, 104), (373, 150), (364, 150)],
    socket=[(372, 140), (378, 143), (384, 160), (386, 185), (384, 226), (379, 258), (372, 268)],
    # ---- the carrying handle: a bar with seven clips, a pin at each end, the hanger and the strap to the gas tube
    handle=[(366, 104), (370, 96), (378, 92.5), (662, 90), (669, 93), (673, 100), (673, 118), (668, 125),
            (656, 126), (650, 118), (612, 117), (600, 113), (420, 114), (404, 117), (398, 128), (390, 128),
            (384, 118), (372, 118), (366, 112)],
    clips=(415.0, 445.5, 477.0, 509.0, 541.0, 573.0, 605.0),
    clip_w=8.0,
    handle_pins=((374.5, 113.0, 4.0), (395.0, 113.0, 8.5), (661.0, 117.0, 7.5)),
    hanger=(611.0, 652.0, 116.5, 121.0),
    hanger_lugs=((618.0, 625.0), (636.0, 644.0)),
    strap=(609.5, 614.5, 117.0, 197.0),
    strap_foot=(612.0, 626.0, 190.0, 197.0),
    handle_bar=(378.0, 668.0, 91.0, 114.0),            # for the rail clamp: x, top / bottom y
    # ---- the gas system: tube, collar, rod, sleeve, the launcher's rear mount on it ----
    gas_y=185.0,
    gas_tube=[(383, 12.0), (603, 12.0), (603, 13.5), (612, 13.5)],
    gas_rod=[(612, 8.0), (627, 8.0)],
    gas_sleeve=[(625, 12.0), (652, 12.0)],
    ear=[(650, 172), (654, 162), (664, 158), (672, 162), (676, 172), (672, 184), (660, 188), (652, 182)],
    ear_pin=(662.0, 172.0, 5.5),
    hook=[(577, 150), (578, 138), (583, 129), (592, 124.5), (601, 124), (606, 127), (606, 132), (604, 135),
          (603, 140), (603, 147), (604, 152), (606, 156), (606, 162), (598, 163), (588, 160), (580, 156)],
    hook_base=[(573, 173), (574, 163), (580, 158), (600, 160), (602, 173)],
    # ---- the stock: beam, frame bar, grip, bottom strut and fore grip in one moulding ----
    # its top is at row 193 (brightness down the photo's columns at x 690-800): behind the launcher the gas tube
    # lies sunk into it, hiding that edge, and the launcher rests on it
    beam=[(371, 193.5), (805, 193), (806, 227), (371, 227)],
    # under the beam, a little narrower: the rear web to the grip, the frame bar, the block ahead of the fore grip
    under=[(373, 226), (806, 226), (806, 240), (779, 242), (716, 243), (497, 243), (494, 256), (449, 262),
           (444, 258), (436, 252), (392, 256), (380, 262), (373, 268)],
    # grip, bottom strut and fore grip: one frame round the opening, so the three meet without a seam and the
    # opening's edge is rounded all the way round. Its top bar lies inside the beam and `under`, and is kept more
    # than two bevels thick: a thinner one turned inside out and closed the top of the opening
    frame=[(449, 215), (779, 215), (780, 262), (784, 269), (784, 278), (778, 285), (772, 296), (772, 312),
           (778, 338), (783, 356), (785, 372), (760, 373), (735, 378), (700, 392), (652, 407), (600, 409),
           (540, 401), (449, 394), (448, 290)],
    frame_hole=[(497, 244), (714, 244), (716, 262), (714, 300), (712, 330), (706, 340), (690, 346), (600, 370),
                (535, 387), (527, 389), (521, 381), (516, 362), (508, 325), (500, 292), (497, 270)],
    grip_ribs=dict(first=295.0, pitch=8.6, count=10, rear=447.0, front=((290, 497), (330, 505), (380, 517))),
    fore_ribs=dict(first=295.0, pitch=8.6, count=9, rear=715.0, front=((290, 770), (312, 771), (338, 777),
                                                                      (372, 784))),
    # the case chute on the right, under the beam: cases leave forward over the grip (bstudy.net, zonwar.ru)
    chute=(381.0, 482.0, 235.0, 8.5),
    # ---- the rifle's trigger: a strap guard (a round bow, its tail to the grip), a thin blade on a pivot ----
    # the guard (14x crop): a polished strap that drops straight from the frame bar and bends round a circle
    # under the trigger; behind the trigger its two edges part, the upper one up to the frame, the lower one back
    # to the grip, and the bright wedge between them is the same metal shining, not a gap (user, 2026-11-25:
    # "it's just shine and NOT transparent"; built as a fork at first)
    bow=(567.5, 267.5, 27.5, 22.0, 0.0, 120.0),        # centre, outer / inner radius, from / to (degrees, 90 = down)
    guard_low=[(544, 293), (534, 289), (524, 285.5), (515, 286.5), (507, 291), (495, 293)],   # on to the grip
    guard_high=[(495, 241), (505.5, 241.5), (507, 257), (512.5, 267), (521, 275.5), (532, 280.5), (544, 285.5)],
    trigger_house=[(528, 241), (542, 241), (541, 252), (538, 258), (532, 257), (529, 250)],
    trigger_pin=(536.0, 253.0, 4.5),
    trigger=[(534, 255), (539, 256), (543, 266), (547, 273), (553, 279), (553.5, 281.5), (549, 281), (543, 275.5),
             (538.5, 267)],
    sear=[(495, 242), (530, 242), (530, 252), (533, 253), (533, 255.5), (520, 255), (495, 254)],
    frame_pin=(536.5, 234.0, 2.5),
    # ---- the barrel ahead of the beam: the launcher's cradle on it, the front plate, the flash hider ----
    barrel=[(800, 9.5), (930, 9.5)],
    cradle=[(803, 16.0), (815, 16.0), (815, 14.0), (876, 14.0), (876, 16.0), (884, 16.0)],
    cradle_y=208.0,
    front_plate=(884.0, 896.0, 187.0, 240.0),
    brackets=(828.0, 862.0, 186.0, 197.0),
    hider=(930.0, 937.0, 995.0, 13.0, 16.5),           # x: step ring from, body from, front; radii
    # ---- the launcher's trigger under the barrel, in a long open guard ----
    gl_house=(826.0, 875.0, 221.0, 235.0),
    gl_pivot=[(814, 222), (831, 222), (831, 237), (820, 238), (814, 232)],
    gl_trigger=[(818, 236), (829, 236), (828.5, 250), (830.5, 262), (836, 269.5), (840, 272), (839, 275.5),
                (833, 273.5), (826, 265), (822, 252)],
    gl_guard_out=[(897, 226), (896, 245), (891, 258), (881, 270), (867, 279), (850, 284.5), (832, 287.5),
                  (816, 288.5)],
    gl_guard_in=[(816, 281), (835, 280), (852, 277), (866, 271), (876, 262), (882, 250), (884, 236), (884, 226)],
    gl_lug=(894.0, 913.0, 222.0, 238.0),
    # ---- the launcher over the barrel: tube with its flared mouth, a hex nut, the breech, its sight leaf ----
    # x rear, bell from, front; radius at the rear, at the bell, the mouth's, the bore's (it widens a little forward)
    tube=(762.0, 866.0, 888.0, 34.0, 36.5, 46.0, 26.0),
    tube_catch=[(865, 113), (866.5, 99), (869, 97), (872, 101), (874, 110), (873, 117), (866, 118)],
    tube_lever=[(884, 174), (905, 172), (912, 178), (911, 187), (890, 190), (884, 188)],
    tube_lever_pin=(906.0, 181.0, 2.5),
    nut=(737.0, 762.0, 26.0),
    # behind the nut the breech is a housing under the axis, as low as the tube; the leaf's lug stands on it
    housing=[(704, 147), (737, 147), (737, 195), (704, 195)],
    # what carries the launcher on the beam: a saddle under the breech and the tube's rear (the photo is dark from
    # the tube down to the beam; user, 2026-11-25: "the launcher is floating which is not correct")
    saddle=[(650, 181), (668, 181), (737, 184), (737, 176), (762, 176), (762, 186), (830, 186), (830, 195),
            (650, 195)],
    lug=[(706, 148), (706, 134), (712, 126), (732, 124), (740, 131), (740, 148)],
    hinge=(722.0, 131.0, 4.5),
    leaf=[(706, 133), (759, 26), (764, 27), (748, 96), (735, 128), (729, 139), (712, 141)],   # raised (the photo)
    leaf_up=69.4,                                      # degrees it folds forward, down beside the tube
    breech=[(672, 160), (676, 152), (686, 147), (700, 146), (706, 150), (706, 184), (700, 187), (676, 186),
            (672, 180)],
    breech_ear=[(680, 147), (682, 137), (689, 132.5), (697, 134), (701, 141), (699, 148)],
    breech_pin=(691.0, 141.0, 4.5),
    lever=[(668, 175), (707, 172), (707, 178.5), (668, 182)],
    wire=[(672, 186.5), (731, 181.5), (755, 182), (755, 184.5), (731, 184), (672, 189)],
    wire_clip=(729.0, 734.0, 178.0, 192.0),
    muzzle_x=995.0,
    # half widths, mm
    widths=dict(rec=15.0, cover=18.5, hump=9.5, butt=21.0, catch=6.0, plate=17.5, handle=8.0, clip=9.3, beam=16.0,
                under=14.5, grip=13.5, leaf=22.5),
)


def stretch(g):
    """The photo's profiles moved for the longer round: the rear group back by REAR, the barrel on by BARREL."""
    back = lambda x: x + REAR if x < REAR_FROM else x
    for k in ("butt", "butt_fold", "loop_stem", "receiver", "selector", "pointer", "catch"):
        g[k] = [(back(x), y) for x, y in g[k]]
    for k in ("butt_boss", "loop", "rec_pin"):
        g[k] = (back(g[k][0]),) + tuple(g[k][1:])
    g["cover"] = (g["cover"][0] + REAR,) + tuple(g["cover"][1:])
    x0, y0, x1, y1, r = g["pad"]
    g["pad"] = (x0 + REAR, y0, x1 + REAR, y1, r)
    g["plate_heads"] = tuple((back(x), y, r) for x, y, r in g["plate_heads"])
    # a heavier barrel, longer ahead of the front plate, and a bigger flash hider on it
    g["barrel"] = [(800, 10.5), (930 + BARREL, 10.5)]
    h0, h1, h2, hr0, hr1 = g["hider"]
    g["hider"] = (h0 + BARREL, h1 + BARREL, h2 + BARREL + 8.0, 14.5, 18.0)
    g["muzzle_x"] = g["hider"][2]
    g["widths"]["rec"] = REC_HALF
    return g


stretch(G)


# ==================================================================================================
# Meshes
# ==================================================================================================

def rib_front(rb, y):
    pts = rb["front"]
    for (ya, xa), (yb, xb) in zip(pts, pts[1:]):
        if y <= yb:
            return xa + (xb - xa) * (y - ya) / (yb - ya)
    return pts[-1][1]


def band(outer, inner):
    return list(outer) + list(inner)


def arc(cx, cy, r, a0, a1, step=10.0):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def build_body(name, g):
    w = g["widths"]
    b = kit.Builder()

    # ---- butt, receiver, cheek cover, hump ----
    slab(b, g["butt"], half=w["butt"], bevel=4.0, res=2, mat="rubber")
    bx, by, br = g["butt_boss"]
    for sx in (1, -1):
        boss(b, bx, by, br, sx * (w["butt"] - 0.5), sx * (w["butt"] + 1.5), seg=16, mat="rubber")
    lx, ly, lro, lri = g["loop"]
    slab(b, base.ellipse(lx, ly, lro, lro, 16), [base.ellipse(lx, ly, lri, lri, 12)], half=1.5, bevel=0.4,
         mat="steel")
    slab(b, g["loop_stem"], half=1.5, bevel=0.3, mat="steel")
    slab(b, g["receiver"], half=w["rec"], bevel=1.2, mat="steel")
    # the cover: a flat top, a broad chamfer each side (the cheek pads lie on it), a short upright foot; it rises
    # to the front as the photo's does
    ca, cb, ct, cf, cbm, ctw, rise = g["cover"]
    cw = w["cover"]
    zt, zf, zb = P(0.0, ct)[1], P(0.0, cf)[1], P(0.0, cbm)[1]
    shear = Matrix.Identity(4)
    shear[2][1], shear[2][3] = rise, -rise * P(200.0, 0.0)[0]
    b.prism("y", [(-cw, zb), (cw, zb), (cw, zf), (ctw, zt), (-ctw, zt), (-cw, zf)], P(ca, 0.0)[0], P(cb, 0.0)[0],
            mat="poly", bevel=0.9, xf=shear)
    slab(b, g["hump"], half=w["hump"], bevel=1.4, res=1, mat="poly")
    slab(b, g["selector"], half=0.9, bevel=0.3, mat="steel", x0=-(w["rec"] + 0.9))
    slab(b, g["pointer"], half=0.7, bevel=0.25, mat="dark", x0=-(w["rec"] + 2.2))
    px_, py_, pr_ = g["rec_pin"]
    for sx in (1, -1):
        boss(b, px_, py_, pr_, sx * (w["rec"] - 0.3), sx * (w["rec"] + 0.8), seg=10, mat="metal")
    for px_, py_, pr_ in g["plate_heads"]:
        boss(b, px_, py_, pr_, -(w["rec"] + 1.5), -(w["rec"] + 2.5), seg=8, mat="metal")
    slab(b, g["catch"], half=w["catch"], bevel=0.8, mat="steel")
    x0, x1, y0, y1 = g["plate"]
    pxbox(b, x0, x1, y0, y1, -w["plate"], w["plate"], mat="steel", bevel=1.0)
    slab(b, g["leg"], half=w["handle"], bevel=0.8, mat="steel")
    slab(b, g["socket"], half=13.0, bevel=2.0, res=1, mat="steel")

    # ---- the carrying handle ----
    slab(b, g["handle"], half=w["handle"], bevel=1.0, mat="steel")
    for cx in g["clips"]:
        pxbox(b, cx - g["clip_w"] / 2, cx + g["clip_w"] / 2, 88.5, 116.0, -w["clip"] - 0.4, w["clip"] + 0.4,
              mat="steel", bevel=0.9)
    for hx, hy, hr in g["handle_pins"]:
        for sx in (1, -1):
            boss(b, hx, hy, hr, sx * (w["handle"] - 0.3), sx * (w["handle"] + 1.6), seg=12, mat="metal")
    x0, x1, y0, y1 = g["hanger"]
    pxbox(b, x0, x1, y0, y1, -6.0, 6.0, mat="steel", bevel=0.4)
    for la, lb in g["hanger_lugs"]:
        pxbox(b, la, lb, y1 - 0.5, y1 + 6.0, -6.0, 6.0, mat="steel", bevel=0.5)
    x0, x1, y0, y1 = g["strap"]
    pxbox(b, x0, x1, y0, y1, -6.0, 6.0, mat="steel", bevel=0.5)
    x0, x1, y0, y1 = g["strap_foot"]
    pxbox(b, x0, x1, y0, y1, -6.0, 6.0, mat="steel", bevel=0.5)

    # ---- the gas system and the launcher's rear mount on it ----
    gy = g["gas_y"]
    t = g["gas_tube"]
    lathe(b, gy, [(t[0][0], 0.0)] + t + [(t[-1][0], 0.0)], seg=14, mat="dark")
    for key, mat in (("gas_rod", "metal"), ("gas_sleeve", "dark")):
        t = g[key]
        lathe(b, gy, [(t[0][0], 0.0)] + t + [(t[-1][0], 0.0)], seg=12, mat=mat)
    slab(b, g["ear"], half=9.0, bevel=1.2, mat="steel")
    ex, ey, er = g["ear_pin"]
    for sx in (1, -1):
        boss(b, ex, ey, er, sx * 8.7, sx * 10.6, seg=10, mat="metal")

    # ---- the stock ----
    slab(b, g["beam"], half=w["beam"], bevel=2.0, res=1, mat="poly")
    slab(b, g["under"], half=w["under"], bevel=1.5, res=1, mat="poly")
    slab(b, g["frame"], [g["frame_hole"]], half=w["grip"], bevel=5.0, res=2, mat="poly")
    for key in ("grip_ribs", "fore_ribs"):
        rb = g[key]
        for i in range(rb["count"]):
            cy = rb["first"] + i * rb["pitch"]
            pxbox(b, rb["rear"], rib_front(rb, cy) - 3.0, cy - 2.4, cy + 2.4, -(w["grip"] + 1.6), w["grip"] + 1.6,
                  mat="poly", bevel=1.2)
    c0, c1, cy, cr = g["chute"]
    lathe(b, cy, [(c0, 0.0), (c0, cr), (c1, cr), (c1, cr - 2.0), (c1 - 14.0, cr - 2.0), (c1 - 14.0, 0.0)], seg=12,
          mat="steel", x0=-(w["under"] - 2.5))

    # ---- the rifle's trigger and its guard ----
    cx, cy, ro, ri, a0, a1 = g["bow"]
    guard = [(cx + ri, 240.0), (cx + ro, 240.0)] + arc(cx, cy, ro, a0, a1) + g["guard_low"] + g["guard_high"] + \
        arc(cx, cy, ri, a1, a0)
    slab(b, guard, half=5.0, bevel=0.7, mat="bright")
    slab(b, g["trigger_house"], half=3.5, bevel=0.5, mat="metal")
    tx, ty, tr = g["trigger_pin"]
    for sx in (1, -1):
        boss(b, tx, ty, tr, sx * 3.2, sx * 4.4, seg=10, mat="dark")
    slab(b, g["trigger"], half=3.0, bevel=0.5, mat="metal")
    slab(b, g["sear"], half=2.5, bevel=0.5, mat="dark")
    fx, fy, fr = g["frame_pin"]
    for sx in (1, -1):
        boss(b, fx, fy, fr, sx * (w["under"] - 0.3), sx * (w["under"] + 0.7), seg=8, mat="bright")

    # ---- the barrel, the launcher's cradle on it, the front plate, the flash hider ----
    t = g["barrel"]
    lathe(b, BORE, [(t[0][0], 0.0)] + t + [(t[-1][0], 0.0)], seg=12, mat="steel")
    t = g["cradle"]
    lathe(b, g["cradle_y"], [(t[0][0], 0.0)] + t + [(t[-1][0], 0.0)], seg=16, mat="steel")
    x0, x1, y0, y1 = g["front_plate"]
    pxbox(b, x0, x1, y0, y1, -12.0, 12.0, mat="steel", bevel=2.0)
    x0, x1, y0, y1 = g["brackets"]
    pxbox(b, x0, x1, y0, y1, -9.0, 9.0, mat="steel", bevel=0.8)
    h0, h1, h2, hr0, hr1 = g["hider"]
    lathe(b, BORE, [(h0, 0.0), (h0, hr0), (h1, hr0), (h1 + 2.0, hr1), (h2 - 2.0, hr1), (h2, hr1 - 2.0), (h2, 7.0),
                    (h2 - 12.0, 7.0), (h2 - 12.0, 0.0)], seg=14, mat="steel")

    # ---- the launcher's trigger and guard ----
    x0, x1, y0, y1 = g["gl_house"]
    pxbox(b, x0, x1, y0, y1, -6.0, 6.0, mat="metal", bevel=0.8)
    slab(b, g["gl_pivot"], half=4.0, bevel=0.6, mat="dark")
    slab(b, g["gl_trigger"], half=3.0, bevel=0.6, mat="bright")
    slab(b, band(g["gl_guard_out"], g["gl_guard_in"]), half=7.0, bevel=0.8, mat="bright")
    x0, x1, y0, y1 = g["gl_lug"]
    pxbox(b, x0, x1, y0, y1, -6.0, 6.0, mat="steel", bevel=1.0)

    # ---- the launcher: tube (a real bore), hex nut, breech collar, the block and lever behind it ----
    t0, t1, t2, tr, tr1, tm, tb = g["tube"]
    lathe(b, LAUNCH, [(t0, 0.0), (t0, tr), (t1, tr1), (t1 + 6.0, tr1 + 1.5), (t1 + 12.0, tr1 + 4.5),
                      (t1 + 14.0, tm - 0.5), (t1 + 15.0, tm), (t2, tm), (t2, tm - 5.0), (t2 - 4.0, tb + 3.0),
                      (t2 - 40.0, tb), (t2 - 40.0, 0.0)], seg=28, mat="dark", x0=LX)
    slab(b, g["tube_catch"], half=2.5, bevel=0.5, mat="steel", x0=LX)
    slab(b, g["tube_lever"], half=2.5, bevel=0.5, mat="steel", x0=LX)
    px_, py_, pr_ = g["tube_lever_pin"]
    for sx in (1, -1):
        boss(b, px_, py_, pr_, LX + sx * 2.2, LX + sx * 3.4, seg=8, mat="metal")
    n0, n1, nr = g["nut"]
    lathe(b, LAUNCH, [(n0, 0.0), (n0, nr - 2.5), (n0 + 2.5, nr), (n1 - 2.5, nr), (n1, nr - 2.5), (n1, 0.0)], seg=6,
          mat="metal", x0=LX)
    slab(b, g["housing"], half=17.0, bevel=5.0, res=2, mat="dark", x0=LX)
    slab(b, g["saddle"], half=10.0, bevel=1.0, mat="steel", x0=LX)
    slab(b, g["lug"], half=8.0, bevel=1.0, mat="steel", x0=LX)
    hx, hy, hr = g["hinge"]
    boss(b, hx, hy, hr, LX - 9.6, w["leaf"] + 1.6, seg=10, mat="metal")       # the leaf's cross pin, its head right
    slab(b, g["breech"], half=10.0, bevel=1.2, mat="steel", x0=LX)
    bx, by, br = g["breech_pin"]
    slab(b, g["breech_ear"], half=6.0, bevel=0.8, mat="steel", x0=LX)
    for sx in (1, -1):
        boss(b, bx, by, br, LX + sx * 5.7, LX + sx * 7.4, seg=10, mat="metal")
    slab(b, g["lever"], half=11.5, bevel=0.6, mat="metal", x0=LX)
    slab(b, g["wire"], half=0.8, bevel=0.2, mat="metal", x0=LX - 12.0)
    x0, x1, y0, y1 = g["wire_clip"]
    pxbox(b, x0, x1, y0, y1, LX - 13.2, LX - 10.5, mat="metal", bevel=0.3)
    return b.to_object(name)


def build_leaf(name, g, folded):
    """The launcher's folding sight: a fin on a cross pin beside the tube, raised as in the photo or folded forward
    along the tube (zonwar's photo, where the side view hides it)."""
    b = kit.Builder()
    pts = turned(g["leaf"], g["hinge"][:2], g["leaf_up"]) if folded else g["leaf"]
    slab(b, pts, half=1.0, bevel=0.3, mat="dark", x0=g["widths"]["leaf"])
    return b.to_object(name)


def build_bolt(name, g):
    """The charging hook and its foot on the gas tube, under the carrying handle."""
    b = kit.Builder()
    slab(b, g["hook"], half=3.5, bevel=0.9, res=1, mat="steel")
    slab(b, g["hook_base"], half=5.0, bevel=0.8, mat="metal")
    return b.to_object(name)


# ==================================================================================================
# Texture: build_a91m.py's materials and wear, this gun's details at the photo's places
# ==================================================================================================

BASE = dict(base.BASE, dark=(40, 40, 43))        # the launcher tube and gas tube: black, but not a hole


def paint(maps, kind, g=None):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind != "body":
        return np.clip(base.common(maps, col, mat), 0, 255)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    X, Y = ORIGIN[0] + y * S, ORIGIN[1] - z * S              # back to photo px
    side = np.abs(n[..., 0]) > 0.7
    right = n[..., 0] < -0.7
    is_ = lambda m: mat == MATS.index(m)
    poly, steel, rubber, dark = is_("poly"), is_("steel"), is_("rubber"), is_("dark")
    w = g["widths"]
    rr, screw = base.rr_mask, base.screw

    # -- the cheek pad on the cover's chamfer: darker rubber with a soft rim --
    x0, y0, x1, y1, r = g["pad"]
    cov = poly & (X > 100 + REAR) & (X < 260 + REAR) & (Y > 170) & (Y < 202) & (np.abs(n[..., 0]) > 0.35)
    d = rr(X, Y, x0, y0, x1, y1, r)
    col[cov & (d < 0)] = 36
    col[cov & (d >= 0) & (d < 1.3)] *= 1.25
    # -- the receiver: a pin, a rivet, two oval slots; on the right the selector's marks --
    rec = steel & side & (X > 60 + REAR) & (X < 363) & (Y > 205) & (Y < 287) & (np.abs(x) < w["rec"] + 0.5)
    recr = rec & right
    for cx, cy in ((285.0, 233.0), (282.0, 251.0), (286.0, 251.0), (290.0, 251.0)):
        col[recr & (np.hypot(X - cx - REAR, Y - cy) < 1.5)] = (190, 40, 34)
    # -- the butt: its fold line, grooves across the back --
    bs = rubber & side
    for (xa, ya), (xb, yb) in zip(g["butt_fold"], g["butt_fold"][1:]):
        t = np.clip(((X - xa) * (xb - xa) + (Y - ya) * (yb - ya)) / ((xb - xa) ** 2 + (yb - ya) ** 2), 0, 1)
        col[bs & (np.hypot(X - xa - t * (xb - xa), Y - ya - t * (yb - ya)) < 0.9)] *= 0.55
    col[rubber & (n[..., 1] < -0.6) & (np.mod(Y, 8.0) < 2.4)] *= 0.6
    # -- the magazine catch: its slot --
    ct = steel & side & (X > 168 + REAR) & (X < 222 + REAR) & (Y > 287) & (np.abs(x) < w["catch"] + 0.5)
    col[ct & (rr(X, Y, 186.0 + REAR, 296.0, 212.0 + REAR, 300.0, 1.5) < 0)] *= 0.45
    # -- the stock: the frame bar's seam and its lit edge --
    st = poly & side & (X > 495) & (X < 735) & (np.abs(x) > w["under"] - 0.6) & (np.abs(x) < w["under"] + 0.4)
    col[st & (np.abs(Y - 227.5) < 1.0)] *= 0.5
    col[st & (Y > 231.5) & (Y < 236.0)] *= 1.18
    # -- the case chute's mouth, the gas tube's slot for the hook --
    c0, c1, cy, cr = g["chute"]
    col[steel & (X > c1 - 15.0) & (X < c1 + 1.0) & (n[..., 1] > 0.5) & (np.abs(Y - cy) < cr) & (x < 0)] = 5
    col[poly & right & (X > c0) & (X < c1) & (Y > 226.5) & (Y < cy + cr + 2.0)] *= 0.6        # the chute's recess
    col[dark & (X > 400) & (X < 600) & (n[..., 2] > 0.75) & (np.abs(x) < 2.4) & (np.abs(Y - g["gas_y"] + 12) < 3)] = 8
    # -- the handle: the open channel on top between the clips --
    hb = steel & (X > 385) & (X < 650) & (Y < 93) & (n[..., 2] > 0.7)
    col[hb & (np.abs(x) < 4.6)] *= 0.5
    # -- the launcher's bore, the flash hider's bore and its long slots --
    t0, t1, t2, tr, tr1, tm, tb = g["tube"]
    rad = np.hypot(x - LX, (Y - LAUNCH) / S)
    col[dark & (X > t2 - 41.0) & (rad < (tb + 1.0) / S) & (n[..., 1] > 0.5)] = 5
    col[dark & (X > t2 - 40.5) & (rad < (tb + 2.0) / S) & (np.abs(n[..., 1]) < 0.5)] *= 0.4
    h0, h1, h2, hr0, hr1 = g["hider"]
    zb = (ORIGIN[1] - BORE) / S
    rad = np.hypot(x, z - zb)
    col[steel & (X > h2 - 13.0) & (rad < 7.5 / S) & (n[..., 1] > 0.5)] = 5
    hd = steel & (X > h1 + 9.0) & (X < h2 - 5.0) & (rad > (hr1 - 1.5) / S) & (rad < (hr1 + 1.0) / S) & \
        (np.abs(n[..., 1]) < 0.5)
    ang = np.arctan2(z - zb, x)
    col[hd & (np.abs(np.sin(2.0 * ang)) < 0.19)] = 9
    col = base.common(maps, col, mat)
    rim = dark & (X > t2 - 8.5) & (np.abs(np.hypot(x - LX, (Y - LAUNCH) / S) - tm / S) < 1.3) & \
        (np.abs(n[..., 1]) < 0.6)
    col[rim] = col[rim] * 1.5 + 22.0
    # the round parts' sheen: a band of light along their upper side
    for (ax, ay, ar, xa, xb) in ((LX, LAUNCH, (tr + tr1) / 2.0, t0, t1), (0.0, g["gas_y"], 12.0, 383.0, 603.0),
                                 (0.0, BORE, hr1, h1, h2), (0.0, g["cradle_y"], 14.0, 815.0, 876.0),
                                 (-(w["under"] - 2.5), cy, cr, c0, c1)):
        sel = (X > xa) & (X < xb) & (np.abs(np.hypot(x - ax, (Y - ay) / S) - ar / S) < 2.2) & (np.abs(n[..., 1]) < 0.5)
        nz = n[..., 2][sel]
        col[sel] *= (0.80 + 0.25 * np.clip(nz, -1, 1))[..., None]
        col[sel] += (30.0 * np.exp(-((nz - 0.55) / 0.17) ** 2))[..., None]
    return np.clip(col, 0, 255)


# ==================================================================================================
# Points
# ==================================================================================================

def gp(x, y, xoff=0.0):
    yy, zz = P(x, y)
    return [round(xoff * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


def points(g):
    muzzle = gp(g["muzzle_x"], BORE)
    ro = base.rail_origin(g)
    return {
        "muzzle": {"offset": muzzle, "rotate": [-90.0, 0.0, -180.0]},
        "muzzle_gl": {"offset": gp(g["tube"][2], LAUNCH, LX), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": [muzzle[0], round(muzzle[1] - base.AK_CANON_BACK, 4), muzzle[2]], "rotate": ZERO},
        "magazine": {"offset": gp(MAG_FIT[0], MAG_FIT[1]), "rotate": [MAG_FIT[2], 0.0, 0.0]},
        "bolt_fired": {"offset": [0.0, round(-base.CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "rail_up": {"offset": [0.0, 0.0, 0.0], "rotate": ZERO},
        "scope": {"offset": [round(c + d, 4) + 0.0 for c, d in zip(ro, base.GOM_SCOPE_FROM_RAIL)], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / base.K_OLD, 4), round(0.13 * K / base.K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
    }


def joined(name, parts):
    """One mesh object from copies of `parts` (their UVs kept)."""
    copies = []
    for o in parts:
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    bpy.ops.object.select_all(action='DESELECT')
    for c in copies:
        c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    copies[0].name = copies[0].data.name = name
    return copies[0]


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
    os.makedirs(kit.TEX_DIR, exist_ok=True)
    g = G
    core = build_body("core", g)
    leaf = build_leaf("leaf", g, folded=True)
    bolt = build_bolt(GUN + "_BOLT", g)
    mount = base.build_handle_mount(GUN + "_RAIL_UP", g)
    kit.unwrap([core, leaf, bolt, mount], 0.003)
    base.paint = paint                                   # base.texture() paints through its module global
    maps = [base.bake(core, [core, leaf, bolt], 512), base.bake(leaf, [core, leaf], 512),
            base.bake(bolt, [core, bolt], 512), base.bake(mount, [mount, core], 512)]
    base.texture(maps, ["body", "leaf", "bolt", "mount"], [g] * 4, 512, os.path.join(kit.TEX_DIR, GUN + ".png"))
    # the two bodies: the same core with the leaf folded, or raised (the folded leaf's mesh turned about its pin, so
    # both use the same texels)
    body = joined(GUN + "_BODY", [core, leaf])
    hy, hz = P(*g["hinge"][:2])
    pivot = Matrix.Translation((0.0, hy * K, -hz * K))     # FBX data space: (x, y, -z) game units
    leaf.data.transform(pivot @ Matrix.Rotation(math.radians(-g["leaf_up"]), 4, 'X') @ pivot.inverted())
    body_gl = joined(GUN + "_BODY_GL", [core, leaf])
    out_objs = [body, body_gl, bolt, mount]
    bounds = {o.name: kit.bounds_of(o) for o in out_objs}
    out = {GUN: points(g), "_bounds": bounds}
    out["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the grip's rear top",
        "magazine": "the SV-98's magazines' feed lips' front: their rear on the catch, their top 15 mm into the receiver",
        "muzzle_gl": "the launcher tube's bore at its mouth: the launcher weapon's muzzle",
        "canon": "GoM's AK mount (0.0282 behind the muzzle, the Grozas')",
        "bolt_fired": "the charging hook back %.0f mm (GoM's AK swap)" % base.CARRIER_TRAVEL,
    }
    with open(POINTS_JSON, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    kit.export(out_objs, FBX_GUN)
    for name, bd in bounds.items():
        print("%-20s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
