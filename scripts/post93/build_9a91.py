"""KBP 9A-91 and VSK-94 (9x39mm) models and textures for Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_9a91.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_9A91.fbx   9A91_BODY (the 9A-91 without its stock), 9A91_STOCK_DEPLOYED,
                                                            9A91_STOCK_FOLDED, VSK94_BODY (the VSK-94: the same receiver,
                                                            its skeleton stock and grip, its handguard), 9A91_BOLT (the
                                                            carrier's side and the folding charging handle, right side)
    M/models_X/weapons/magazines/GunsOfTienPost93_9A91_magazines.fbx   9x39Magazine20_9A91
    M/models_X/weapons/parts/GunsOfTienPost93_9A91_parts.fbx           9A91_Suppressor, 9A91_Muzzle_Mount_Device,
                                                                       9A91_AK_Mount (the look of GoM's AK Mounting
                                                                       Rail on these two guns: a low side bracket)
    M/textures/weapons/GunsOfTienPost93/9A91.png                512 atlas (the four gun nodes and the bolt)
    M/textures/weapons/GunsOfTienPost93/9x39Magazine20_9A91.png 128
    M/textures/weapons/GunsOfTienPost93/9A91_Suppressor.png     128 (the can and the mount)
    M/textures/weapons/GunsOfTienPost93/9A91_AK_Mount.png       128
    scripts/post93/a91_points.json                             attachment points (game space), both guns

User, 2026-11-24 (TODO.md "9x39 release"; docs/post93_design.md "9A-91 and VSK-94"): KBP's 9A-91 compact assault
rifle (police, made from 1994) as current production guns are (Wikipedia "9A-91": the selector on the right, a sight
rail on the receiver's left, the charging handle folding up on the carrier), and its 1995 sniper version VSK-94 on the
same receiver (skeleton polymer stock with its pistol grip, a longer diamond-pattern handguard, the 9A-91's magazine).
Both take the same detachable suppressor on the threaded barrel (Wikipedia "VSK-94": "unlike the VSS, the suppressor
of the VSK-94 is not an integrated design").

Built on the kit of post93/build_mp7.py, as build_sv98.py: slabs of the side outlines, lathed metal, the texture
painted per pixel from baked maps. Modelled upright (+X the gun's left, as GoM's rifles), 0.603 of real size.
Origin: where GoM's AKS-74U (the closest GoM gun, the same AK reload) has it against its trigger and bore: the
trigger blade 0.066 game units ahead of the origin, the bore 0.0148 over it, so the rifles sit in the vanilla rifle
clips as GoM's AKs do (measured on GoM's AKS74U_BODY in Blender, 2026-11-24).

References (references/9a91, references/vsk94, SOURCES.txt there):
- 9A-91: IMFDB's 9A-91silenced.jpg (2500 px, studio right side, stock deployed, its can and a Kobra on the left
  rail's mount) read at 2.785 px a mm: butt to muzzle 594 mm (Wikipedia) and receiver rear to muzzle 373 mm (the
  folded length) both give it within 0.1 %, the height 192 against the published 190. The muzzle under the can from
  KardeN's photo with the can off (modernfirearms.net 9a-91_3.jpg: the barrel's collar and thread stand 0.31 of the
  handguard's length out of it). Controls and rails from Vitaly Kuzmin's 45 photos (Commons, CC BY-SA 4.0): the
  folding hook-shaped charging handle at the receiver's front right (25), the selector lever with its red dots (27),
  the long dovetail rail on the left (06), the folded stock flat on the receiver (01, 15), the front sight on the
  handguard's front (32). Profiles are in that photo's pixels (x right = forward, y down).
- VSK-94: IMFDB's VSK-94.jpg (2516 px, right side, PSO-1), 2.56 px a mm (butt to can front 932 mm, Wikipedia; the
  can reads 312 mm against the 9A-91's 307: the same can). Its stock, grip and handguard in that photo's pixels,
  registered on the trigger blade and the bore; the receiver is the 9A-91's (the photo's receiver reads 5 % longer
  than the 9A-91 photo's, so the handguard, barrel and can are placed from our receiver's front).
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

MEDIA = kit.MEDIA
TEX_DIR = kit.TEX_DIR
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_9A91.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_9A91_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_9A91_parts.fbx")
POINTS_JSON = os.path.join(HERE, "a91_points.json")
MAG_NAME = "9x39Magazine20_9A91"

K = 0.000603
kit.K = K
MATS = ["steel", "poly", "dark", "bright", "rubber"]
kit.MATS[:] = MATS
for ch, rows in {"9": ["111", "101", "111", "001", "111"], "A": ["010", "101", "111", "101", "101"],
                 "-": ["000", "000", "111", "000", "000"], "B": ["110", "101", "110", "101", "110"],
                 "C": ["111", "100", "100", "100", "111"], "K": ["101", "101", "110", "101", "101"],
                 " ": ["000", "000", "000", "000", "000"]}.items():
    kit.FONT.setdefault(ch, rows)

# ==================================================================================================
# Photo frames
# ==================================================================================================

S9 = 2.785                         # 9A-91 photo, px a mm
TRIG9, BORE9 = 924.0, 323.0        # the trigger blade's middle (x), the bore (y: the can's axis)
SV = 2.56                          # VSK-94 photo
# registered on the receiver the two guns share (edge correlation of the 9A-91 photo's receiver, scaled 2.56 / 2.785,
# on the VSK-94 photo, 2026-11-24: 9A-91 (700, 240) lands on (808, 305), the halves agree within 1 px). The first
# build took the bore for y 400; this photo's can axis reads 377-381 and the receiver puts the bore at 381.3, so the
# stock sat 7.4 mm too high on the receiver.
TRIGV, BOREV = 1014.0, 381.3
ORIGIN_TO_TRIGGER = 0.066 / K      # GoM's AKS-74U: 109.5 mm real
BORE_Z = 0.0148 / K                # 24.5 mm real


def P(x, y):
    """9A-91 photo px -> game (y, z) mm."""
    return (x - TRIG9) / S9 + ORIGIN_TO_TRIGGER, (BORE9 - y) / S9 + BORE_Z


def PV(x, y):
    """VSK-94 photo px -> game (y, z) mm, registered on the trigger and bore."""
    return (x - TRIGV) / SV + ORIGIN_TO_TRIGGER, (BOREV - y) / SV + BORE_Z


def PL(pts, f=P):
    return [f(x, y) for x, y in pts]


def gy(x):
    return P(x, BORE9)[0]


Z_BORE = BORE_Z
FRONT9 = gy(1301.0)                # the receiver's front (the handguard starts there)
HG_LEN = (1597.0 - 1297.0) / S9   # the 9A-91 handguard, 108 mm
MUZZLE_OUT = 0.31 * HG_LEN         # barrel (collar and thread) out of the handguard's front (KardeN's photo)

W_REC, W_COVER, W_HG, W_GRIP, W_MAG = 15.0, 13.0, 18.0, 14.0, 12.0
# the stock's strut is a stamped U channel as wide as the receiver (Kuzmin's 13 and 36): its side walls run on as the
# two ears round the hinge pin, and folded it lies over the top cover (W_CHAN: the folded channel's web)
W_STRUT, W_BUTT, W_CHAN = 15.6, 16.6, 12.5
EAR_X = W_REC + 1.2                # the ears' middle across (they lie on the receiver's sides, 2 mm plate)
W_VSK_BAR, W_VSK_BUTT = 14.0, 19.0
RAIL_OUT = 22.0                    # the left dovetail rail's outer face (x, real mm from the bore's plane)
BOLT_TRAVEL = 70.0                 # the carrier's stroke (GoM's AKS-74U 0.047 at 0.645 = 73 mm)

# ==================================================================================================
# Profiles: 9A-91 photo px (IMFDB 9A-91silenced.jpg), read on 10 px gridded crops
# ==================================================================================================

# the receiver: the stamped body from the hinge block at the rear to its front at the handguard, the top cover's
# rear step, the lower edge level over the grip, trigger guard and magazine well
# (its rear face is behind the stock's ears: re-read on the 12x crop, 2026-11-24; the first trace ran round the ear)
RECEIVER = [(686, 388), (686, 300), (694, 293), (700, 285), (710, 279), (710, 254), (730, 255), (740, 251),
            (753, 242), (1180, 243), (1252, 245), (1301, 250), (1302, 390), (1290, 394), (1020, 396), (986, 396),
            (986, 391), (873, 391), (873, 396), (700, 396), (690, 392)]
# the top cover's raised strip over the receiver (drawn narrower, standing 1 mm proud)
COVER = [(710, 254), (730, 255), (740, 251), (753, 242), (1180, 243), (1252, 245), (1252, 262), (710, 262)]
# the magazine well's skirt over the magazine's top: its lower edge a curve from the front of the guard up to the
# well's front (the curved line on the photo's magazine)
SKIRT = [(1016, 394), (1200, 394), (1200, 412), (1180, 415), (1150, 420), (1125, 427), (1100, 437), (1080, 447),
         (1060, 460), (1045, 473), (1034, 484), (1022, 492), (1016, 488)]
# Under the receiver, read on 6x and 8x gridded crops of the photo (2026-11-24, redone: the first trace drew the
# blade as a straight sliver, the housing as one box and the guard as a band up the front):
# the trigger frame (Kuzmin's 12, 14, 27): a bright steel box under the receiver, open at the bottom, narrower than
# the receiver; the bright strip on the photo is its side, and the trigger's root rises into it. The dark band under
# it ahead of the trigger in the measuring photo is the Kobra's side mount on the far (left) side, seen through the
# guard (the user, 2026-11-24): their two side photos without an optic (a current "14 BM 052" and an early gun) show
# open air there.
STRIP = [(873, 391), (986, 391), (986, 402), (873, 402)]
FRAME_W = 7.5                      # the frame's half width (mm)
# the pistol grip (polymer): rear edge from the receiver down to the heel, the bottom, the front edge up to the nub
# the guard ends on, then straight up to the receiver. No web behind the trigger: the dark wedge there in the IMFDB
# photo is the same side mount (the photos without an optic show the guard's opening clear up to the grip)
GRIP = [(720, 390), (726, 396), (738, 420), (742, 440), (738, 456), (722, 484), (700, 524), (680, 564), (668, 596),
        (664, 620), (666, 640), (680, 646), (720, 654), (760, 660), (790, 664), (802, 668), (800, 656), (794, 646),
        (786, 628), (788, 600), (796, 572), (808, 546), (824, 512), (832, 490), (840, 479), (856, 475), (866, 480),
        (872, 479), (866, 470), (862, 440), (861, 394)]
# per gun (the VSK-94's guard is a full loop of its own, traced on its own photo): the blade (a thin stamped
# crescent, about 1.5 mm thick, concave forward), the guard's band (outer and inner lines, rear to front), the catch
# plate that closes the guard's front (the opening's edge, then down to the magazine), the magazine catch's spike
TG_9A91 = {
    "trigger": [(906, 393), (906, 403), (908, 412), (909.5, 420), (909, 430), (910, 440), (912, 449), (916, 459), (921, 466),
                (927, 473), (933, 479), (936, 480), (938, 477), (931, 470), (925, 463), (920, 456), (916, 448),
                (914, 440), (913, 430), (914, 420), (916, 412), (919, 406), (922, 403), (922, 393)],
    "guard_out": [(866, 480), (872, 486), (884, 492), (900, 497), (930, 499), (960, 497), (982, 492), (994, 488)],
    "guard_in": [(866, 472), (872, 479), (884, 486), (900, 491), (930, 493), (960, 490), (980, 485), (990, 481)],
    "plate": [(996, 400), (1003, 412), (1007, 425), (1008, 440), (1006, 455), (1000, 470), (990, 483), (986, 490),
              (1022, 490), (1022, 396)],
    "catch": [(994, 490), (1012, 490), (1010, 507), (1007, 522), (1004, 532), (1002, 536), (1003, 530), (1005, 522),
              (1004.5, 512), (1001.5, 500)],
}
TG_VSK = {     # VSK-94 photo px
    "trigger": [(998, 446), (998, 452), (999, 465), (1000, 480), (1001, 494), (1005, 506), (1011, 516), (1019, 522), (1024, 522),
                (1024, 519), (1019, 514), (1012.5, 505), (1008, 494), (1005.5, 481), (1006, 468), (1009, 458),
                (1011, 452), (1011, 446)],
    "guard_out": [(955, 448), (955, 465), (957, 489), (966, 508), (976, 520), (991, 530), (1010, 536.5), (1030, 537),
                  (1050, 534), (1065, 530)],
    "guard_in": [(960, 448), (960, 465), (962, 488), (970, 506), (980, 517), (994, 526), (1010, 532), (1030, 532),
                 (1050, 529), (1062, 526)],
    "plate": [(1077, 447), (1085, 462), (1089, 481), (1086, 500), (1080, 512), (1072, 522), (1062, 529), (1062, 534),
              (1104, 534), (1104, 447)],
    "catch": [(1078, 534), (1098, 534), (1096, 548), (1094, 560), (1091, 571), (1089, 566), (1090, 552), (1086, 542)],
}
# the handguard (polymer), ribbed under a smooth top band
HANDGUARD = [(1297, 240), (1306, 230), (1318, 228), (1578, 228), (1592, 234), (1598, 246), (1598, 370),
             (1592, 380), (1580, 384), (1310, 384), (1300, 378), (1297, 368)]
HG_RIBS = (1316, 1585, 262, 380, 13)     # x from, to, y top, bottom, count
FRONT_SIGHT = [(1552, 230), (1556, 222), (1576, 222), (1580, 230)]
REAR_SIGHT = [(1206, 244), (1208, 232), (1214, 228), (1232, 228), (1236, 236), (1236, 244)]
GAS_BLOCK = [(1252, 245), (1284, 247), (1296, 252), (1296, 268), (1252, 268)]     # front of the cover, over the gas tube
HINGE = (676.0, 304.0)             # the stock's hinge pin (px)
# the stock's ear on each side of the receiver, round the pin (10x crop): the channel's side wall carried forward
EAR = [(656, 312), (658, 300), (661, 293), (666, 288), (672, 285.5), (678, 285), (684, 286), (690, 290), (694, 295),
       (696, 302), (696.5, 315), (695, 326), (690, 330), (688, 335), (691, 342), (694, 350), (695.5, 360),
       (694.5, 370), (691, 378), (686, 385), (672, 388), (650, 390), (650, 331)]
FOLD_DEG = -169.97                 # deployed to folded, about the pin (the strut's line turned level, pointing forward)
SELECTOR = [(852, 296), (870, 296), (874, 330), (882, 366), (870, 376), (854, 374), (850, 350), (856, 326)]
# the stock (deployed): the stamped strut from the hinge down to the butt, the butt block and its folding plate
STRUT = [(657, 312), (655, 320), (650, 329), (640, 335), (630, 337), (560, 352), (500, 363), (400, 387), (300, 400),
         (280, 407), (260, 413), (240, 420), (220, 427), (205, 431), (120, 433), (120, 475), (200, 463), (300, 450),
         (400, 437), (500, 417), (640, 390), (657, 389)]
STRUT_LOW = [(120, 475), (200, 463), (300, 450), (400, 437), (500, 417), (640, 390), (657, 389)]
STRUT_WEB = 7.0                    # the channel's web along its lower edge (px up from it); it is open on top
BUTT_BLOCK = [(42, 430), (120, 428), (122, 480), (84, 482), (43, 476)]
BUTT_PLATE = [(42, 478), (80, 482), (80, 640), (74, 648), (48, 650), (42, 640)]
# the bolt: the folding charging handle (hook up, as folded on Kuzmin's 25) on its base plate, and the carrier's
# side seen in the receiver's slot
HANDLE_BASE = [(1116, 300), (1192, 300), (1196, 312), (1192, 324), (1116, 324)]
HANDLE_HOOK = [(1184, 306), (1188, 272), (1192, 246), (1196, 232), (1204, 224), (1214, 222), (1218, 228),
               (1206, 234), (1201, 250), (1198, 276), (1198, 306)]
CARRIER = [(1000, 312), (1116, 312), (1116, 330), (1000, 330)]
# the left dovetail rail (Kuzmin's 06: from 119 px ahead of the receiver's rear to its front, its middle just under
# the bore), in this photo's frame
RAIL = (774.0, 1296.0, 300.0, 352.0)
# the magazine: the 20-round steel box, its top inside the receiver
MAG = (1022.0, 1197.0, 380.0, 757.0)

# ==================================================================================================
# VSK-94 (IMFDB VSK-94.jpg px)
# ==================================================================================================

# the skeleton stock: its top under the receiver (behind the ears it steps up to the comb), the front down the grip
VSK_STOCK = [(957, 447), (957, 480), (954, 497), (941, 515), (931, 535), (922, 552), (911, 584), (900, 612),
             (880, 650), (863, 690), (879, 704), (884, 719), (78, 716), (70, 700), (66, 440), (68, 426), (770, 426),
             (770, 443)]
VSK_WINDOWS = [[(226, 481), (526, 481), (526, 658), (226, 658)],
               [(581, 481), (832, 479), (826, 505), (821, 526), (800, 572), (779, 616), (758, 640), (737, 658),
                (581, 658)]]
VSK_PAD = [(66, 426), (124, 426), (124, 716), (70, 716), (66, 700)]
# the plates the stock is pinned by, on each side of the receiver's rear (the 9A-91's hinge pin, a plain plate)
VSK_EAR = [(770, 353), (772, 348), (777, 345.5), (796, 345.5), (801, 348), (804, 354), (804.5, 392), (801, 398),
           (800, 430), (798, 435.5), (773, 435.5), (770, 432)]
# the handguard: a tongue back to the receiver's front under the gas block, the top strip, the underside rising
# forward; the front sight's hood on its front top and the sling ring at the front
VSK_HG = [(1362, 364), (1408, 361), (1412, 352), (1413, 326), (1418, 318), (1426, 315), (1430, 306), (1436, 303),
          (1596, 303), (1600, 301), (1645, 301), (1647, 318), (1650, 325), (1650, 410), (1647, 416), (1500, 426),
          (1368, 437), (1363, 432)]
# the gas block between the receiver's front and the handguard's upper part, over its tongue
VSK_GAS = [(1355, 305), (1432, 305), (1432, 318), (1415, 322), (1414, 362), (1355, 362)]
VSK_FSIGHT = [(1610, 302), (1611, 288), (1616, 281), (1624, 279), (1633, 281), (1638, 288), (1639, 302)]
VSK_RING = (1656.0, 319.0, 8.0)
VSK_PANEL = [(1380, 402), (1450, 352), (1625, 340), (1555, 392)]     # the diamond panel on each side


# ==================================================================================================
# Geometry
# ==================================================================================================

def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0, f=P):
    return kit.slab(b, PL(outline, f), [PL(h, f) for h in holes], half, bevel, res, mat, x0)


def lathe_bore(b, profile, seg=16, mat="steel"):
    """profile [(game y mm, radius)] on the bore."""
    b.lathe("y", (0.0, 0.0, Z_BORE), profile, seg=seg, mat=mat)


def rot_px(pts, deg, centre=None):
    """Photo px turned about the hinge pin (y runs down, so a negative angle lifts what hangs behind the pin)."""
    cx, cy = centre or HINGE
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def ears(b, outline, f=P):
    """The stock's two ears: 2 mm plates on the receiver's sides, round the hinge pin."""
    for s in (1, -1):
        slab(b, outline, half=1.0, bevel=0.4, mat="steel", x0=s * EAR_X, f=f)


def trigger_frame(b):
    """The open-bottomed steel box under the receiver: two side walls, the end walls, the receiver's floor seen
    through it."""
    for s in (1, -1):
        slab(b, STRIP, half=0.9, bevel=0.3, mat="bright", x0=s * (FRAME_W - 0.9))
    for xa, xb in ((873, 879), (980, 986)):
        slab(b, [(xa, 391), (xb, 391), (xb, 402), (xa, 402)], half=FRAME_W, bevel=0.3, mat="bright")
    slab(b, [(879, 391), (980, 391), (980, 394), (879, 394)], half=FRAME_W - 1.8, bevel=0.2, mat="dark")


def receiver(b, vsk=False):
    slab(b, RECEIVER, half=W_REC, bevel=1.2, mat="steel")
    slab(b, COVER, half=W_COVER, bevel=1.5, mat="steel", x0=0.0)
    slab(b, SKIRT, half=W_REC - 0.6, bevel=0.8, mat="steel")
    trigger_frame(b)
    slab(b, GAS_BLOCK, half=W_COVER - 1.0, bevel=1.0, mat="steel")
    slab(b, REAR_SIGHT, half=6.5, bevel=0.6, mat="steel")
    tg, f = (TG_VSK, PV) if vsk else (TG_9A91, P)
    slab(b, tg["trigger"], half=2.3, bevel=0.25, mat="steel", f=f)
    b.strip(PL(tg["guard_out"], f), PL(tg["guard_in"], f), -5.0, 5.0, mat="steel", bevel=0.4)
    slab(b, tg["plate"], half=W_REC - 2.0, bevel=0.6, mat="steel", f=f)
    slab(b, tg["catch"], half=2.5, bevel=0.3, mat="steel", f=f)
    # the selector lever on the right (game -x), pivoting at its top
    slab(b, SELECTOR, half=1.2, bevel=0.3, mat="steel", x0=-W_REC - 1.0)
    # the hinge: the receiver's lug between the stock's ears, the pin through both with its washers
    hx, hy = HINGE
    slab(b, [(hx - 12, hy - 14), (hx + 12, hy - 14), (hx + 12, hy + 18), (hx - 12, hy + 18)], half=W_REC, bevel=1.0,
         mat="steel")
    y, z = P(hx, hy)
    e = EAR_X + 1.0
    b.lathe("x", (0.0, y, z), [(-e - 0.6, 0.0), (-e - 0.6, 4.0), (e + 0.6, 4.0), (e + 0.6, 0.0)], seg=12, mat="steel")
    b.lathe("x", (0.0, y, z), [(-e - 1.4, 0.0), (-e - 1.4, 1.8), (e + 1.4, 1.8), (e + 1.4, 0.0)], seg=10,
            mat="bright")
    # the left dovetail rail: a plate on the receiver's side with the dovetail's two sloped faces (the side mount's
    # clamp grips it); the AK mount's bracket is drawn on it (build_ak_mount)
    La, Lb, ya, yb = RAIL
    y0, z1 = P(La, ya)
    y1, z0 = P(Lb, yb)
    prof = [(z0 + 1.5, W_REC - 0.5), (z0, W_REC + 3.0), (z0 + 2.5, RAIL_OUT), (z1 - 2.5, RAIL_OUT),
            (z1, W_REC + 3.0), (z1 - 1.5, W_REC - 0.5)]
    b.prism("y", [(x, z) for z, x in prof], y0, y1, mat="steel", bevel=0.4)
    # the screws holding it
    for xx in (820, 1000, 1180):
        yy, zz = P(xx, (ya + yb) / 2.0)
        b.lathe("x", (0.0, yy, zz), [(RAIL_OUT - 0.5, 0.0), (RAIL_OUT - 0.5, 2.2), (RAIL_OUT + 0.6, 2.0),
                                     (RAIL_OUT + 0.6, 0.0)], seg=10, mat="bright")


def barrel(b, front):
    """The barrel's collar and thread out of the handguard's front (`front`, game y mm)."""
    lathe_bore(b, [(front - 4.0, 0.0), (front - 4.0, 14.0), (front + 9.0, 14.0), (front + 10.0, 12.5),
                   (front + 10.0, 7.8), (front + MUZZLE_OUT, 7.8), (front + MUZZLE_OUT, 4.6),
                   (front + MUZZLE_OUT - 3.0, 4.6), (front + MUZZLE_OUT - 3.0, 0.0)], seg=16, mat="steel")


def build_a91_body():
    b = kit.Builder()
    receiver(b)
    slab(b, GRIP, half=W_GRIP, bevel=2.5, res=1, mat="poly")
    slab(b, HANDGUARD, half=W_HG, bevel=3.0, res=1, mat="poly")
    slab(b, FRONT_SIGHT, half=3.5, bevel=0.5, mat="steel")
    barrel(b, P(1598, BORE9)[0])
    return b.to_object("9A91_BODY")


def build_stock(folded):
    b = kit.Builder()
    if not folded:
        # the U channel, open on top (it closes over the top cover when folded): two side walls and the web
        web = STRUT_LOW + [(x, y - STRUT_WEB) for x, y in reversed(STRUT_LOW)]
        slab(b, web, half=W_STRUT - 0.5, bevel=0.8, mat="steel")
        for s in (1, -1):
            slab(b, STRUT, half=1.1, bevel=0.5, mat="steel", x0=s * (W_STRUT - 1.1))
        ears(b, EAR)
        slab(b, BUTT_BLOCK, half=W_STRUT, bevel=1.5, mat="steel")
        slab(b, BUTT_PLATE, half=W_BUTT, bevel=2.0, res=1, mat="steel")
        return b.to_object("9A91_STOCK_DEPLOYED")
    # folded flat on the receiver (Kuzmin's 01 / 15): the strut's channel over the top cover from the hinge to the
    # receiver's front, the butt block and its plate folded flat along it at the front, the rear sight in the channel;
    # the ears turned up with it about the pin
    y_h, z_h = P(*HINGE)
    top = P(0, 243)[1]
    y_end = FRONT9 - 4.0
    b.box(-W_CHAN, W_CHAN, y_h - 6.0, y_end - 30.0, top + 4.6, top + 7.0, mat="steel", bevel=0.8)
    for s in (-1, 1):                    # the channel's flanges down the cover's sides
        b.box(s * (W_COVER + 0.6), s * (W_COVER + 2.6), y_h + 8.0, y_end - 30.0, top - 3.0, top + 7.0, mat="steel",
              bevel=0.5)
    # the arm from the hinge up onto the cover
    b.prism("x", [(y_h - 8.0, z_h - 5.0), (y_h + 10.0, z_h - 5.0), (y_h + 18.0, top + 7.0), (y_h - 6.0, top + 7.0)],
            -W_CHAN, W_CHAN, mat="steel", bevel=0.8)
    ears(b, rot_px(EAR, FOLD_DEG))
    # the butt block and plate at the front
    b.box(-W_BUTT, W_BUTT, y_end - 32.0, y_end, top + 4.0, top + 13.0, mat="steel", bevel=1.5)
    b.box(-W_BUTT + 1.0, W_BUTT - 1.0, y_end - 90.0, y_end - 30.0, top + 7.0, top + 11.5, mat="steel", bevel=1.2)
    return b.to_object("9A91_STOCK_FOLDED")


VSK_HANDGUARD_LEN = PV(1650.0, 0.0)[0] - FRONT9     # 113 mm (the first build read the receiver's front 6.5 mm late)


def build_vsk_body():
    b = kit.Builder()
    receiver(b, vsk=True)
    slab(b, VSK_STOCK, VSK_WINDOWS, half=W_VSK_BAR, bevel=3.0, res=1, mat="poly", f=PV)
    slab(b, VSK_PAD, half=W_VSK_BUTT, bevel=3.0, res=1, mat="rubber", f=PV)
    ears(b, VSK_EAR, f=PV)
    slab(b, VSK_HG, half=W_HG, bevel=3.0, res=1, mat="poly", f=PV)
    slab(b, VSK_FSIGHT, half=3.5, bevel=0.5, mat="steel", f=PV)
    slab(b, VSK_GAS, half=W_COVER - 1.0, bevel=1.0, mat="steel", f=PV)
    barrel(b, FRONT9 + VSK_HANDGUARD_LEN)
    return b.to_object("VSK94_BODY")


def build_bolt():
    b = kit.Builder()
    slab(b, CARRIER, half=1.0, bevel=0.3, mat="bright", x0=-W_REC - 0.2)
    slab(b, HANDLE_BASE, half=1.8, bevel=0.5, mat="steel", x0=-W_REC - 1.8)
    slab(b, HANDLE_HOOK, half=2.2, bevel=0.5, mat="steel", x0=-W_REC - 2.6)
    return b.to_object("9A91_BOLT")


def build_magazine():
    """The 20-round stamped steel box, straight, its rear spine ribbed. Origin at the feed lips' front (GoM's
    magazines' way), drawn at the gun's `magazine` point."""
    b = kit.Builder()
    La, Lb, top, bot = MAG
    oy, oz = P(Lb, top)
    def M(x, y):
        gy_, gz = P(x, y)
        return gy_ - oy, gz - oz
    body = [M(La + 6, top), M(Lb, top), M(Lb, bot - 6), M(La, bot - 6), M(La, top + 16)]
    kit.slab(b, body, (), W_MAG, 1.2, 0, "steel", 0.0)
    floor = [M(La - 2, bot - 8), M(Lb + 2, bot - 8), M(Lb + 2, bot), M(La - 2, bot)]
    kit.slab(b, floor, (), W_MAG + 1.0, 0.8, 0, "steel", 0.0)
    lips = [M(La + 20, top - 5), M(Lb - 10, top - 5), M(Lb - 10, top + 2), M(La + 20, top + 2)]
    kit.slab(b, lips, (), W_MAG - 4.0, 0.4, 0, "bright", 0.0)
    return b.to_object(MAG_NAME)


CAN_LEN = 855.0 / S9               # 307 mm (rear cone to front lip)
CAN_R = 21.5


def build_suppressor():
    """The detachable can, in its own frame: origin on the bore at its rear face (the gun's `canon`), +Y forward.
    A short cone onto the barrel's collar, the knurled grip section, the tube, the front lip."""
    b = kit.Builder()
    L = CAN_LEN
    prof = [(0.0, 0.0), (0.0, 13.0), (5.0, 16.0), (9.0, CAN_R - 0.5), (10.0, CAN_R), (L - 6.0, CAN_R),
            (L - 5.0, CAN_R + 0.6), (L - 1.0, CAN_R + 0.6), (L, CAN_R - 1.0), (L, 6.5), (L - 4.0, 5.5),
            (L - 4.0, 0.0)]
    b.lathe("y", (0.0, 0.0, 0.0), prof, seg=20, mat="steel")
    return b.to_object("9A91_Suppressor")


def build_mount():
    """The 9x39mm mount device: the can's threaded adapter, a knurled ring screwed over the barrel's collar."""
    b = kit.Builder()
    b.lathe("y", (0.0, 0.0, 0.0), [(-2.0, 0.0), (-2.0, 14.8), (-1.0, 15.6), (11.0, 15.6), (12.0, 14.8),
                                   (12.0, 9.0), (MUZZLE_OUT - 10.0, 9.0), (MUZZLE_OUT - 10.0, 0.0)],
            seg=18, mat="steel")
    return b.to_object("9A91_Muzzle_Mount_Device")


# GoM's AK Mounting Rail (MarzGuns.AK_Mount) is a tall truss made for the AK's deep receiver: on this low one its rail
# stood 33 mm over the top cover (the user, 2026-11-24: "is that how the mount really works on these guns? That looks
# horrible"). The real Kobra and PSO-1 clamp straight onto the left dovetail and sit just over the cover. So these two
# guns draw GoM's mount item with a model of our own (ModelWeaponPart names it, as the AUGs draw GoM's side rail): a
# clamp on the dovetail, two posts up the left side, a bridge over the cover carrying a short Picatinny strip on the
# bore's line. It clears the folded stock (web top at cover + 7, butt plate from FRONT9 - 94 forward).
COVER_TOP = P(0, 243)[1]
MOUNT_Y = FRONT9 - 135.0           # the strip's middle (the Kobra over the receiver's middle, as on the photo)
MOUNT_Z = COVER_TOP + 10.0         # the strip's mounting face = the model's origin (`rail_up`)
MOUNT_LEN = 80.0
SCOPE_UP = 0.0                     # GoM's optics' origin on the mounting face: they sit 0.5-1.5 into the strip
#                                    (fit_audit; GoM's own medians 1.1-1.6), their clamps reaching 2.4 under it


def build_ak_mount():
    b = kit.Builder()
    zc = (P(0, RAIL[2])[1] + P(0, RAIL[3])[1]) / 2.0 - MOUNT_Z        # the dovetail's middle
    hh = (P(0, RAIL[2])[1] - P(0, RAIL[3])[1]) / 2.0
    out = RAIL_OUT + 0.3
    b.box(out, out + 4.5, -30.0, 30.0, zc - hh - 3.2, zc + hh + 3.2, mat="steel", bevel=0.8)      # the clamp's plate
    for s in (1, -1):                                                 # its two jaws over the dovetail's edges
        za, zb = sorted((zc + s * (hh + 0.3), zc + s * (hh + 3.2)))
        b.box(W_REC + 1.0, out + 0.5, -30.0, 30.0, za, zb, mat="steel", bevel=0.4)
    b.lathe("x", (0.0, -10.0, zc), [(out + 4.5, 0.0), (out + 4.5, 4.2), (out + 7.0, 4.2), (out + 7.0, 0.0)], seg=10,
            mat="steel")                                              # the locking lever's boss and arm
    b.box(out + 5.0, out + 7.0, -10.0, 24.0, zc - 2.6, zc + 2.6, mat="steel", bevel=0.7)
    for ya, yb in ((-30.0, -19.0), (19.0, 30.0)):                     # the posts
        b.box(out + 0.5, out + 4.5, ya, yb, zc + hh + 2.5, -0.5, mat="steel", bevel=0.6)
    b.box(-10.6, out + 4.5, -30.0, 30.0, -2.2, 0.0, mat="steel", bevel=0.5)                       # the bridge
    kit.picatinny(b, -MOUNT_LEN / 2.0, MOUNT_LEN / 2.0, lambda u, h, yy: Vector((u, yy, h)), base_h=2.5, tooth_h=4.0,
                  mat="steel")
    return b.to_object("9A91_AK_Mount")


# ==================================================================================================
# Painting
# ==================================================================================================

# a little brighter than GoM's AKS-74U texture (mean 42 / 39 / 37), as its AS VAL's (48 / 46 / 44): the photos' guns
# are blued steel worn grey, the polymer a shade lighter and duller than the steel
BASE = {"steel": (50, 52, 57), "poly": (46, 47, 49), "dark": (12, 12, 13), "bright": (128, 130, 132),
        "rubber": (34, 34, 35)}


def in_poly(a, c, pts):
    inside = np.zeros(a.shape, bool)
    n = len(pts)
    for i in range(n):
        (a1, c1), (a2, c2) = pts[i], pts[(i + 1) % n]
        cond = ((c1 > c) != (c2 > c)) & (a < (a2 - a1) * (c - c1) / ((c2 - c1) or 1e-9) + a1)
        inside ^= cond
    return inside


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "bright")])
    mott = kit.vnoise(p, 8.0, 1) * 0.6 + kit.vnoise(p, 2.0, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    up = np.clip(n[..., 2], -1, 1)
    col *= (0.96 + 0.14 * up)[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    # the 9A-91s in the photos are worn to bright steel on every sharp edge
    wear = np.where(is_metal, 75.0, 18.0) * (0.6 + 0.6 * kit.vnoise(p, 3.0, 5))
    col += (convex * wear)[..., None]
    return col


def paint(maps, kind):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    side = np.abs(n[..., 0]) > 0.6
    right = n[..., 0] < -0.6
    poly = mat == MATS.index("poly")
    steel = mat == MATS.index("steel")
    if kind in ("a91", "vsk"):
        # the grip's checkered panels (9A-91's grip; the VSK-94's on its stock's grip)
        if kind == "a91":
            gp = [P(*q) for q in [(716, 470), (760, 470), (800, 486), (782, 600), (776, 640), (690, 628), (700, 560)]]
        else:
            gp = [PV(*q) for q in [(826, 548), (900, 548), (878, 620), (862, 690), (760, 690), (790, 600)]]
        grip = poly & side & in_poly(y, z, gp)
        chk = (np.sin(y * 2 * np.pi / 3.4) > 0.35) | (np.sin(z * 2 * np.pi / 3.4) > 0.35)
        col[grip & chk] *= 0.55
        # the receiver's slots and lines: the carrier slot on the right, the cover's joint, the "9A-91" / "BCK 94"
        # marking and the selector's red dots
        slot = steel & right & (y > P(1000, 0)[0]) & (y < P(1120, 0)[0]) & (z < P(0, 312)[1]) & (z > P(0, 332)[1])
        col[slot] = BASE["dark"]
        joint = steel & side & (np.abs(z - P(0, 262)[1]) < 0.5) & (y > P(712, 0)[0]) & (y < P(1252, 0)[0])
        col[joint] *= 0.45
        for dx in (795, 938, 948, 958):
            dy, dz = P(dx, 358)
            d = np.hypot(y - dy, z - dz)
            col[right & steel & (d < 1.3)] = np.array([170.0, 30.0, 30.0])
        text = "9A-91" if kind == "a91" else "BCK 94"
        u0, v0 = P(1105, 365)
        tm = right & steel & kit.text_mask(y, z, text, u0, v0 - 1.0, 5.0)
        col[tm] *= 1.9
        if kind == "a91":
            # the handguard's ribs: vertical grooves under its smooth top band
            x0, x1, top, bot, nrib = HG_RIBS
            ya, yb = P(x0, 0)[0], P(x1, 0)[0]
            zt, zb = P(0, top)[1], P(0, bot)[1]
            band = poly & side & (y > ya) & (y < yb) & (z < zt) & (z > zb)
            ph = (y - ya) / ((yb - ya) / nrib)
            groove = np.abs(ph - np.round(ph)) < 0.22
            col[band & groove] *= 0.5
            col[band & ~groove] *= 1.12
            # the band's edge
            col[poly & side & (np.abs(z - zt) < 0.7) & (y > ya) & (y < yb)] *= 0.6
        else:
            # the VSK-94's diamond panel, slanted, on each side of its handguard
            u = y - FRONT9
            v = Z_BORE - z
            panel = poly & side & in_poly(y, z, [PV(*q) for q in VSK_PANEL])
            dia = (np.abs(((u + v) / 4.2) % 1.0 - 0.5) < 0.16) | (np.abs(((u - v) / 4.2) % 1.0 - 0.5) < 0.16)
            col[panel & dia] *= 0.5
            col[panel & ~dia] *= 1.1
        # the receiver's rivets and screw heads (right side: over the magazine well and at the front)
        for cx, cy in ((1062, 350), (1215, 358), (1272, 348), (865, 290), (918, 290)):
            dy_, dz_ = P(cx, cy)
            d = np.hypot(y - dy_, z - dz_)
            col[right & steel & (d < 2.6)] *= 1.6
            col[right & steel & (d < 2.6) & (d > 1.9)] *= 0.55
        # the muzzle's bore
        bore = (n[..., 1] > 0.6) & (np.hypot(x, z - Z_BORE) < 4.6) & steel
        col[bore & (y > FRONT9 + 50)] = BASE["dark"]
    elif kind == "stock":
        holes = (mat == MATS.index("steel")) & side
        col[holes] *= 1.0
    elif kind == "mag":
        spine = side & (np.sin(z * 2 * np.pi / 10.0) > 0.85)
        col[spine & (mat == MATS.index("steel"))] *= 1.2
    elif kind == "can":
        knurl = (y > 9.0) & (y < 65.0) & (np.abs(n[..., 1]) < 0.5)
        ang = np.arctan2(z, x)
        kn = (np.sin(ang * 60 + y * 1.6) > 0.3) ^ (np.sin(ang * 60 - y * 1.6) > 0.3)
        col[knurl & kn] *= 0.6
        col[(np.abs(n[..., 1]) > 0.6) & (np.hypot(x, z) < 6.0)] = BASE["dark"]
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

def g(y, z, x=0.0):
    return [round(x * K, 4) + 0.0, round(y * K, 4) + 0.0, round(z * K, 4) + 0.0]


ZERO = [0.0, 0.0, 0.0]
def points(body):
    # our bracket for GoM's AK mount (build_ak_mount): its origin on the bore's line, GoM's optics on its strip
    mount = g(MOUNT_Y, MOUNT_Z)
    scope = g(MOUNT_Y, MOUNT_Z + SCOPE_UP)
    front = FRONT9 + (VSK_HANDGUARD_LEN if body == "vsk" else HG_LEN)
    muzzle_y = front + MUZZLE_OUT
    pts = {
        "muzzle": {"offset": g(muzzle_y, Z_BORE), "rotate": [-90.0, 0.0, -180.0]},
        # the can's rear face on the handguard's front (it covers the collar and thread)
        "canon": {"offset": g(front, Z_BORE), "rotate": ZERO},
        "magazine": {"offset": g(*P(MAG[1], MAG[2])), "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-BOLT_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "rail_up": {"offset": mount, "rotate": ZERO},
        "scope": {"offset": scope, "rotate": ZERO},
        "world": {"offset": [0.0200, 0.1300, 0.0], "rotate": [180.0, 0.0, 180.0]},
    }
    if body == "a91":
        pts["stock"] = {"offset": ZERO, "rotate": ZERO}
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

    body, vsk = build_a91_body(), build_vsk_body()
    deployed, folded = build_stock(False), build_stock(True)
    bolt = build_bolt()
    mag = build_magazine()
    can, mount = build_suppressor(), build_mount()
    ak_mount = build_ak_mount()
    gun = [body, deployed, folded, vsk, bolt]
    kit.unwrap(gun, 0.005)
    kit.unwrap([mag], 0.012)
    kit.unwrap([can, mount], 0.012)
    kit.unwrap([ak_mount], 0.012)
    os.makedirs(TEX_DIR, exist_ok=True)
    # each body bakes against itself and the bolt (the deployed stock with the 9A-91), so AO matches what is drawn
    texture(gun, [[body, bolt, deployed], [deployed, body], [folded, body], [vsk, bolt], [bolt, body]],
            ["a91", "stock", "stock", "vsk", "bolt"], 512, os.path.join(TEX_DIR, "9A91.png"))
    texture([mag], [[mag]], ["mag"], 128, os.path.join(TEX_DIR, MAG_NAME + ".png"))
    texture([can, mount], [[can], [mount]], ["can", "can"], 128, os.path.join(TEX_DIR, "9A91_Suppressor.png"))
    texture([ak_mount], [[ak_mount]], ["mount"], 128, os.path.join(TEX_DIR, "9A91_AK_Mount.png"))
    bounds = {o.name: kit.bounds_of(o) for o in gun + [mag, can, mount, ak_mount]}
    kit.export(gun, FBX_GUN)
    kit.export([mag], FBX_MAGS)
    kit.export([can, mount, ak_mount], FBX_PARTS)
    # the off hand's point on the magazine (GoM's AS VAL 20's, its offset moved by the two meshes' centres)
    gom_mag = kit.import_mesh(os.path.join(kit.GOM, "models_X/weapons/magazines/assault_rifles.fbx"), "9x39Magazine20")
    prop2 = kit.bip01_prop2(mag, gom_mag, ([0.0279, 0.0937, -0.0020], [-86.2737, 31.4012, -93.4148]))
    out = {"9A91": points("a91"), "VSK94": points("vsk"), "_mag_prop2": prop2, "_bounds": bounds,
           "_extras": {"k": K, "origin_to_trigger_mm": ORIGIN_TO_TRIGGER, "bore_z_mm": BORE_Z,
                       "receiver_front_mm": FRONT9, "can_len_mm": CAN_LEN}}
    with open(POINTS_JSON, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    for name, bb in bounds.items():
        print("%-26s tris %5d  min %s  max %s" % (name, bb["tris"], bb["min"], bb["max"]))


if __name__ == "__main__":
    main()
