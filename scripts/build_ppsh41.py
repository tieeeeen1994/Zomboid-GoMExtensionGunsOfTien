"""PPSh-41 submachine gun model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_ppsh41.py -- [--size 1024] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_PPSH41.fbx              PPSH41_BODY, PPSH41_BOLT (the cocking handle on
                                                                    the right, forward)
    M/models_X/weapons/magazines/GunsOfTien_PPSH41_magazines.fbx   762x25Drum71_PPSH41, 762x25Magazine35_PPSH41
                                                                    (origin at the middle of each one's top)
    M/textures/weapons/GunsOfTien/PPSH41.png                        256, the gun's two nodes
    M/textures/weapons/GunsOfTien/762x25Drum71_PPSH41.png           128
    M/textures/weapons/GunsOfTien/762x25Magazine35_PPSH41.png       128
    scripts/ppsh41_points.json                                      attachment points (game space)

Georgy Shpagin's submachine gun of 1941 in 7.62x25mm (user, 2026-11-23: the Tokarev release, with the TT-33): stamped
steel, the barrel jacket with four cooling slots a side running forward into the slanted muzzle compensator, a wooden
stock, the receiver hinged ahead of the magazine, a 71-round drum (copied from the Suomi's) or the 35-round curved box
of 1942, a selector lever inside the trigger guard ahead of the trigger. Published: 843 mm long, 269 mm barrel,
3.63 kg empty, about 900 rounds a minute, open bolt.

Traced from Rock Island Auction's left-side studio photo of a Soviet gun with its drum (lot 84/1677, 7078 px;
references/ppsh41/ppsh41_left_ria84_1677.jpg is it levelled by 0.29 degrees on the jacket's top edge):
scripts/ppsh41_reference_outline.json, scaled to 843 mm (8.25 px a mm). Profiles are in that photo's (L, H) mm: L back
from the muzzle, H up from the butt's toe. Details were read off gridded crops (scripts/ref_crop.py); the right side
(cocking handle, ejection port) from lot 89/405's right-side photo.

GoM's rifle conventions (CLAUDE.md, "Gun assets in GoM"): upright, +Y muzzle, +Z top, +X the gun's LEFT, 0.603 of real
size. A straight-stocked gun has no pistol grip to put the origin on: the SV-98's rule, from GoM's M24 (the trigger
57.5 mm ahead of the origin, the bore 16 mm over it), which puts it in the top of the stock's wrist. The drum faces
forward as every drum does (its round faces along the barrel), as GoM's Thompson drum.
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_PPSH41.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_PPSH41_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "ppsh41_points.json")
DRUM, BOX = "762x25Drum71_PPSH41", "762x25Magazine35_PPSH41"

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "wood", "metal", "dark", "mag", "brass"]
kit.MATS[:] = MATS
for ch, rows in {"5": ["111", "100", "111", "001", "111"], "9": ["111", "101", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

BORE = 165.0                       # the barrel's axis (seen through the slots at H 160-170)
TRIGGER_L = 495.0                  # the trigger blade's middle
L0, H0 = TRIGGER_L + 57.5, BORE - 16.0    # GoM's M24 rule (build_sv98.py): photo (552.5, 149)
# the stock off lot 89/405's top view (raw/ria_002.jpg, 7.7 px/mm between the rear cap, the sight and the handle):
# 48 mm of wood round a 33 mm receiver
W_JACKET, W_RECV, W_LOWER, W_STOCK, W_BUTT = 17.0, 17.0, 16.0, 23.0, 21.0
MAG_POINT = (318.0, 150.0)         # the middle of the magazine's top in the well
HANDLE_L, HANDLE_H, HANDLE_TRAVEL = 384.0, 172.0, 85.0     # the cocking handle forward; back when cocked or firing
SLOT_R = (378.0, 472.0, 166.5, 171.5)                      # its slot along the receiver's right side (lot 89/405)
PORT = (316.0, 365.0)              # the ejection port in the receiver's top, 14 mm wide (the same top view)
# the drum's radius, half thickness, its neck's height. 45 mm thick: 39 px-mm in the top view, 105 mm further from
# the lens than the receiver's top; the side photo's 59 mm is its edge plus the rear face, seen from behind the
# drum (the lens over L 421), which is why a fit to that outline alone came out 53 mm thick
DRUM_R, DRUM_HALF, DRUM_DROP = 68.0, 22.5, 7.0
# it hangs foot forward (lot 84/1677: the front edge leans 5 degrees), its middle at L 324
DRUM_TILT, DRUM_BACK = 5.0, 12.5

# ==================================================================================================
# Profiles (photo L, H mm), read off the traced photo on a 5 mm grid
# ==================================================================================================

# the muzzle compensator: the jacket's front, cut on a slant (the top leads), a port through each side
COMP = [(0.2, 177.5), (1.7, 179.7), (4.0, 180.9), (42.0, 180.5), (42.0, 146.5), (17.0, 146.9), (12.4, 149.2),
        (9.3, 152.0), (6.4, 156.5), (3.3, 162.9), (1.0, 169.0), (0.2, 174.0)]
COMP_PORT = (22.5, 164.5, 11.5, 9.0)        # centre, half length, half height
JACKET = [(40.0, 180.5), (255.0, 181.0), (255.0, 146.5), (40.0, 146.5)]
# the jacket's lug down to the hinge, under its rear end
JACKET_LUG = [(238.0, 147.0), (238.0, 166.0), (287.0, 166.0), (287.0, 138.3), (276.0, 138.3), (262.0, 139.5),
              (254.0, 140.3), (248.0, 142.3), (243.0, 144.5)]
SLOTS = [(45.0, 90.0), (100.0, 143.0), (155.0, 200.0), (209.0, 251.0)]     # each side, H 156-174
SLOT_H = (156.0, 174.0)
RECV = [(250.0, 181.0), (470.0, 181.0), (470.0, 164.0), (250.0, 164.0)]
# sights, cap and guard reread off the traced outline every 4 mm (pass 5)
REAR_CAP = [(470.0, 164.0), (470.0, 189.7), (512.0, 189.5), (515.0, 185.5), (517.0, 184.0), (526.0, 184.0),
            (532.0, 181.3), (536.0, 176.5), (538.5, 170.0), (539.0, 164.0)]
REAR_SIGHT_BASE = [(414.0, 180.0), (414.0, 187.5), (416.5, 189.2), (459.0, 189.5), (462.0, 187.5), (462.5, 180.0)]
REAR_SIGHT_EARS = [(426.0, 188.5), (429.0, 191.5), (432.5, 196.3), (436.0, 200.0), (440.5, 199.2), (444.0, 193.7),
                   (448.5, 190.0), (452.0, 188.5)]
FRONT_SIGHT_BASE = [(48.0, 180.0), (56.0, 184.3), (64.0, 187.0), (94.0, 187.0), (97.0, 185.0), (104.0, 183.0),
                    (106.0, 180.0)]
FRONT_SIGHT = (80.5, 191.5, 10.5, 9.0, 13.0)     # the hood: L, H of its axis, outer and inner radius, half length
# the lower receiver: the hinge at its front, the magazine housing, the band the stock butts against
LOWER = [(272.0, 146.0), (273.0, 158.0), (277.0, 164.5), (385.0, 164.5), (385.0, 117.0), (292.0, 117.0),
         (290.0, 141.0), (274.0, 141.0)]
HINGE, HINGE_PIN = (285.0, 153.5, 6.5), (263.0, 151.0, 5.0)
CATCH = [(352.0, 117.5), (353.0, 108.0), (358.0, 106.3), (384.0, 107.0), (392.0, 108.0), (397.0, 109.5),
         (398.5, 117.5)]
GUARD_TANG = [(410.0, 117.5), (411.5, 112.7), (431.5, 112.7), (431.5, 117.5)]     # the guard's plate ahead of its bow
# top, belly and the slanted rear taken off the traced outline (read by eye off the crops it came out 2-5 mm
# thin, with an upright butt)
STOCK = [(385.0, 163.5), (537.0, 163.5), (540.0, 163.1), (548.0, 157.6), (556.0, 149.2), (564.0, 142.8),
         (572.0, 137.4), (580.0, 134.2), (588.0, 131.5), (596.0, 129.4), (604.0, 127.8), (612.0, 126.4),
         (620.0, 126.0), (628.0, 126.8), (636.0, 128.8), (644.0, 131.4), (652.0, 132.9), (660.0, 133.2),
         (668.0, 133.1), (676.0, 132.4), (684.0, 131.6), (692.0, 130.9), (700.0, 130.2), (708.0, 129.6),
         (716.0, 129.2), (724.0, 128.6), (732.0, 127.9), (740.0, 127.2), (748.0, 126.6), (756.0, 125.6),
         (764.0, 124.8), (772.0, 123.9), (780.0, 123.1), (788.0, 122.5), (796.0, 121.9), (804.0, 121.0),
         (812.0, 120.1), (820.0, 119.1), (828.0, 118.5), (835.9, 114.0), (838.2, 110.0), (838.8, 104.0),
         (838.0, 94.0), (836.4, 82.0), (835.0, 70.0), (833.7, 58.0), (832.6, 46.0), (831.7, 34.0), (830.8, 22.0),
         (830.0, 12.0), (829.0, 6.0), (826.7, 2.0), (824.0, 0.1), (816.0, 1.0), (808.0, 1.8), (800.0, 3.1),
         (792.0, 4.5), (784.0, 6.4), (776.0, 8.1), (768.0, 10.0), (760.0, 12.0), (752.0, 14.1), (744.0, 16.6),
         (736.0, 19.1), (728.0, 21.9), (720.0, 24.6), (712.0, 27.4), (704.0, 30.4), (696.0, 33.4), (688.0, 36.9),
         (680.0, 40.5), (672.0, 44.0), (664.0, 47.4), (656.0, 51.0), (648.0, 54.8), (640.0, 57.8), (632.0, 59.0),
         (624.0, 54.9), (616.0, 53.4), (608.0, 55.8), (600.0, 64.2), (592.0, 75.1), (584.0, 84.0), (576.0, 90.4),
         (568.0, 95.6), (560.0, 99.9), (552.0, 104.1), (544.0, 107.9), (536.0, 110.5), (528.0, 112.6),
         (519.0, 112.5), (385.0, 116.5)]
BUTTPLATE = [(826.2, 2.0), (828.5, 6.0), (829.5, 12.0), (830.3, 22.0), (831.2, 34.0), (832.1, 46.0),
             (833.2, 58.0), (834.5, 70.0), (835.9, 82.0), (837.5, 94.0), (838.3, 104.0), (837.7, 110.0),
             (835.4, 114.0), (840.1, 114.0), (842.4, 110.0), (843.0, 104.0), (842.2, 94.0), (840.6, 82.0),
             (839.2, 70.0), (837.9, 58.0), (836.8, 46.0), (835.9, 34.0), (835.0, 22.0), (834.2, 12.0),
             (833.2, 6.0), (830.9, 2.0)]
# the trigger guard (a pressed strap), the trigger, the selector ahead of it
GUARD_OUT = [(431.0, 117.0), (433.5, 100.0), (436.0, 90.7), (440.0, 85.0), (444.0, 82.3), (448.0, 80.7), (456.0, 80.1),
             (498.0, 80.2), (504.0, 81.7), (508.0, 83.7), (512.0, 87.3), (516.0, 95.0), (518.5, 105.0), (520.5, 117.0)]
GUARD_IN = [(434.0, 117.0), (436.4, 100.5), (438.8, 92.0), (442.2, 87.3), (445.5, 85.0), (449.0, 83.6), (456.0, 83.1),
            (497.5, 83.2), (502.5, 84.5), (506.0, 86.2), (509.2, 89.2), (513.0, 96.0), (515.5, 105.5), (517.5, 117.0)]
# off the photo at 16 px a mm (ref_crop.py 428 524 76 122). The trigger a J: its blade hangs from L 490-504 and
# sweeps forward to its tip at L 486, the finger's side hollow
TRIGGER = [(490.5, 118.0), (490.2, 110.5), (493.0, 107.0), (494.8, 103.0), (495.5, 99.0), (494.5, 95.0),
           (492.0, 91.5), (489.0, 89.3), (485.8, 87.4), (487.0, 86.0), (490.5, 86.6), (494.0, 89.0), (497.0, 93.0),
           (498.8, 98.0), (499.5, 105.0), (501.0, 110.0), (503.5, 115.0), (504.0, 118.0)]
# the selector ahead of it: its housing (a thick plate, a thinner one under it), a stud, and the lever, a bent
# wire that ends in an open teardrop eye (walls 1.8 mm: the bevel stays under half of that)
SELECTOR = [(439.5, 117.5), (439.3, 113.0), (440.5, 111.2), (444.0, 110.8), (444.5, 109.0), (474.0, 109.0),
            (474.5, 110.8), (476.5, 111.2), (477.6, 113.0), (477.5, 117.5)]
SELECTOR_STUD = (451.5, 456.5, 106.3, 109.5)
SELECTOR_LEVER = [(458.0, 110.0), (459.6, 108.6), (459.9, 101.5), (458.9, 99.6), (458.7, 97.3), (459.6, 95.6),
                  (461.5, 94.8), (463.4, 95.6), (464.3, 97.3), (464.1, 99.6), (463.1, 101.5), (463.0, 108.6),
                  (466.0, 110.0)]
SELECTOR_EYE = [(461.5, 100.6), (460.6, 98.9), (460.5, 97.4), (461.0, 96.5), (461.5, 96.2), (462.1, 96.5),
                (462.6, 97.4), (462.5, 98.9)]
SWIVEL_FRONT = (143.0, 152.0, 150.0, 177.0)     # the front sling loop on the jacket's left
SWIVEL_PLATE = (685.0, 84.5, 21.0, 13.5)        # the rear sling plate on the stock's left: centre, half L, half H


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


def gpt(L, H, x=0.0):
    return Vector((x, L0 - L, H - H0))


def ellipse(cL, cH, rl, rh, n=20):
    return [(cL + rl * math.cos(2 * math.pi * k / n), cH + rh * math.sin(2 * math.pi * k / n)) for k in range(n)]


# ==================================================================================================
# Geometry
# ==================================================================================================

def build_body():
    b = kit.Builder()
    cL, cH, rl, rh = COMP_PORT
    slab(b, COMP, [ellipse(cL, cH, rl, rh)[::-1]], half=W_JACKET, bevel=2.6, res=1)
    slots = [[(La + 9.0 + 9.0 * math.cos(math.radians(a)), 165.0 + 9.0 * math.sin(math.radians(a)))
              for a in range(90, 271, 30)] +
             [(Lb - 9.0 + 9.0 * math.cos(math.radians(a)), 165.0 + 9.0 * math.sin(math.radians(a)))
              for a in range(-90, 91, 30)] for La, Lb in SLOTS]
    slab(b, JACKET, [h[::-1] for h in slots], half=W_JACKET, bevel=3.0, res=1)
    slab(b, JACKET_LUG, half=W_JACKET - 1.0, bevel=1.6, res=1)
    slab(b, RECV, half=W_RECV, bevel=4.0, res=2)
    slab(b, REAR_CAP, half=W_RECV + 0.6, bevel=3.0, res=1)
    slab(b, REAR_SIGHT_BASE, half=8.5, bevel=1.0)
    for s in (1, -1):                                        # the flip sight's two guards
        slab(b, REAR_SIGHT_EARS, half=1.3, bevel=0.5, x0=s * 6.5)
    box(b, 434.0, 439.0, 188.0, 195.5, -2.2, 2.2, mat="dark", bevel=0.4)      # the leaf between them
    slab(b, FRONT_SIGHT_BASE, half=9.0, bevel=0.8)
    fL, fH, ro, ri, fh = FRONT_SIGHT
    b.lathe("y", (0, 0, fH - H0), [(L0 - fL - fh, ri), (L0 - fL - fh, ro), (L0 - fL + fh, ro), (L0 - fL + fh, ri)],
            seg=18, mat="steel", phase=0.5)
    b.lathe("y", (0, 0, fH - H0), [(L0 - fL - fh, ri), (L0 - fL + fh, ri)], seg=18, mat="dark", phase=0.5)
    box(b, fL - 1.2, fL + 1.2, 183.0, 193.0, -1.0, 1.0, mat="dark")           # the post
    slab(b, LOWER, half=W_LOWER, bevel=2.2, res=1)
    for (hL, hH, hr), w in ((HINGE, W_LOWER + 1.6), (HINGE_PIN, W_JACKET + 1.2)):
        b.lathe("x", (0.0, L0 - hL, hH - H0), [(-w, 0.0), (-w, hr - 1.0), (-w + 1.0, hr), (w - 1.0, hr), (w, hr - 1.0),
                                               (w, 0.0)], seg=14, mat="metal")
    slab(b, CATCH, half=4.5, bevel=0.8)
    slab(b, GUARD_TANG, half=6.0, bevel=0.6)
    slab(b, STOCK, half=W_STOCK, bevel=5.5, res=2, mat="wood")
    slab(b, BUTTPLATE, half=W_STOCK + 0.4, bevel=1.4, res=1)
    b.strip(PL(GUARD_OUT), PL(GUARD_IN), -6.0, 6.0, mat="steel", bevel=0.5)
    slab(b, TRIGGER, half=2.6, bevel=0.6, res=1, mat="dark")
    slab(b, SELECTOR, half=5.0, bevel=0.8, res=1)
    box(b, *SELECTOR_STUD, -2.5, 2.5, mat="steel", bevel=0.8)
    slab(b, SELECTOR_LEVER, [SELECTOR_EYE[::-1]], half=1.0, bevel=0.3, res=1)
    # the barrel inside its jacket (seen through the compensator's ports and at the muzzle)
    # thick enough to close the slots behind it: no light through the gun but at the compensator's ports
    lathe_y(b, BORE, [(262.0, 0.0), (262.0, 9.6), (42.0, 9.6), (42.0, 3.9), (46.0, 3.9), (46.0, 0.0)], seg=16,
            mat="metal")
    # sling fittings on the left: the front loop on the jacket, the plate let into the stock
    sa, sb, ha, hb = SWIVEL_FRONT
    box(b, sa, sb, ha, hb, W_JACKET - 0.5, W_JACKET + 2.4, mat="metal", bevel=0.9)
    pL, pH, prl, prh = SWIVEL_PLATE
    slab(b, ellipse(pL, pH, prl, prh, 20), half=0.9, bevel=0.4, mat="metal", x0=W_STOCK - 0.3)
    return b.to_object("PPSH41_BODY")


def build_handle():
    """The cocking handle, fixed to the bolt, through the slot on the right; forward (bolt home)."""
    b = kit.Builder()
    box(b, HANDLE_L - 5.0, HANDLE_L + 5.0, HANDLE_H - 2.6, HANDLE_H + 2.6, -W_RECV + 2.0, -W_RECV - 9.0, bevel=0.8)
    box(b, HANDLE_L - 6.5, HANDLE_L + 6.5, HANDLE_H - 5.5, HANDLE_H + 5.5, -W_RECV - 9.0, -W_RECV - 20.0,
        mat="metal", bevel=1.6)
    return b.to_object("PPSH41_BOLT")


def build_drum():
    """The 71-round drum in its own frame: origin at the middle of its neck's top (the gun's `magazine` point), +Y
    forward, +X the gun's left. A flat canister facing forward: the cover on the front face with its catch, the
    winding hub on the rear face, pressed rings on both, a rolled band round it, the feed neck on top."""
    b = kit.Builder()
    r, h = DRUM_R, DRUM_HALF
    cz = -DRUM_DROP - r
    c = (0.0, 0.0, cz)
    # rolled shoulders
    sh = [(0.0, r - 12.0), (1.0, r - 7.0), (2.2, r - 3.0), (4.0, r)]
    b.lathe("y", c, [(-h, 0.0)] + [(-h + d, q) for d, q in sh] + [(-3.0, r), (-3.0, r + 0.6), (3.0, r + 0.6), (3.0, r)] +
            [(h - d, q) for d, q in sh[::-1]] + [(h, 0.0)], seg=32, mat="mag")
    for s in (1, -1):                                        # each face: a pressed ring, a raised middle
        b.lathe("y", c, [(s * (h - 0.4), 0.0), (s * (h - 0.4), r * 0.78), (s * (h + 1.4), r * 0.75),
                         (s * (h + 1.4), r * 0.42), (s * (h + 2.6), r * 0.38), (s * (h + 2.6), 0.0)][::s],
                seg=32, mat="mag")
    b.lathe("y", c, [(-h - 3.2, 0.0), (-h - 3.2, 7.0), (-h - 2.0, 8.5), (-h - 2.0, 0.0)], seg=14, mat="metal")   # hub
    b.box(-5.0, 5.0, h - 1.0, h + 4.5, cz + r - 20.0, cz + r - 3.0, mat="metal", bevel=0.8)    # the cover's catch
    b.box(-13.0, 13.0, -20.0, 20.0, -DRUM_DROP - 6.0, 0.0, mat="mag", bevel=1.2)               # the feed neck
    b.lathe("y", (0.0, 0.0, 3.2), [(-15.0, 0.0), (-15.0, 4.9), (2.0, 4.8), (6.0, 4.1), (10.0, 4.1), (15.0, 3.2),
                                   (19.0, 0.0)], seg=10, mat="brass")                           # the top round
    return b.to_object(DRUM)


# off Commons' left side of a gun with the box in (1200 px): 225 mm from its top, its foot 54 mm forward, 37 deep
BOX_R, BOX_LEN, BOX_DEPTH, BOX_HALF = 483.0, 222.0, 37.0, 11.0


def box_centre(s):
    """How far forward the 35-round box has curved, s mm below its top."""
    return BOX_R - math.sqrt(BOX_R * BOX_R - s * s)


def build_box():
    """The 35-round box of 1942 in its own frame (origin at the middle of its top): a curved stamped box leaning
    forward, a rib down each side, a floor plate."""
    b = kit.Builder()
    n = 12
    front = [(box_centre(BOX_LEN * k / n) + BOX_DEPTH / 2, -BOX_LEN * k / n) for k in range(n + 1)]
    rear = [(box_centre(BOX_LEN * k / n) - BOX_DEPTH / 2, -BOX_LEN * k / n) for k in range(n + 1)]
    body = [(BOX_DEPTH / 2, 3.0)] + front + rear[::-1] + [(-BOX_DEPTH / 2, 3.0)]
    kit.slab(b, body, (), BOX_HALF, 1.6, 1, "mag", 0.0)
    y0 = box_centre(BOX_LEN)
    kit.slab(b, [(y0 - BOX_DEPTH / 2 - 2.0, -BOX_LEN + 1.0), (y0 - BOX_DEPTH / 2 - 2.0, -BOX_LEN - 3.5),
                 (y0 + BOX_DEPTH / 2 + 2.5, -BOX_LEN - 4.5), (y0 + BOX_DEPTH / 2 + 2.5, -BOX_LEN + 0.5)], (),
             BOX_HALF + 1.2, 0.9, 1, "mag", 0.0)
    b.lathe("y", (0.0, 0.0, 5.2), [(-15.0, 0.0), (-15.0, 4.9), (2.0, 4.8), (6.0, 4.1), (10.0, 4.1), (15.0, 3.2),
                                   (19.0, 0.0)], seg=10, mat="brass")
    return b.to_object(BOX)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB: worn blued steel in GoM's range, orange-brown shellacked birch, the barrel, black, the magazines'
    # black paint, brass
    "steel": (56, 56, 60), "wood": (204, 118, 46), "metal": (72, 72, 76), "dark": (22, 22, 23),
    "mag": (44, 45, 47), "brass": (156, 122, 64),
}


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def pin(col, L, H, sel, cL, cH, r=2.4):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.8)] *= 0.4
    col[sel & (d <= r - 0.8)] += 12


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "mag")])
    wood = mat == MATS.index("wood")
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.92 + 0.16 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    grain = kit.vnoise(p * np.array([0.25, 0.02, 2.2]), 1.0, 7)          # long grain along the wood
    col[wood] *= (0.82 + 0.3 * grain[wood])[..., None]
    col *= (0.97 + 0.1 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 70.0, 40.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))
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
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    up = n[..., 2] > 0.7
    steel = mat == MATS.index("steel")
    wood = mat == MATS.index("wood")
    if kind == "body":
        L, H = L0 - y, z + H0
        jacket = steel & (L > 40.0) & (L < 256.0) & (H > 146.0)
        # the cooling slots: four a side, four along the top; the barrel shows in the side ones
        for La, Lb in SLOTS:
            s_top = jacket & up & rounded_rect(L, x, La, Lb, -6.0, 6.0, 5.5)
            col[s_top] = 10
            col[s_top & (np.abs(x) < 2.0)] = 40
        # the compensator: its slanted front plate and the hole the bullet leaves by, the top port
        comp = steel & (L < 41.0)
        col[comp & (n[..., 1] > 0.4) & (np.hypot(x, H - BORE) < 5.5)] = 6
        col[comp & up & rounded_rect(L, x, 10.0, 34.0, -7.0, 7.0, 6.0)] = 10
        col[steel & side & (np.abs(L - 41.0) < 0.6) & (H > 146.0)] *= 0.6
        # the receiver: the ejection port in its top, the handle's slot on the right, the seam
        # along the stock, the hinge's rounded plate, the rear cap's pin
        recv = steel & (L > 256.0) & (L < 470.0) & (H > 163.0)
        port = recv & up & rounded_rect(L, x, PORT[0], PORT[1], -7.0, 7.0, 2.0)
        col[port] = 12
        col[port & rounded_rect(L, x, PORT[0] + 1.5, PORT[1] - 1.5, -5.5, 5.5, 1.5)] = 100     # the bolt, bright in it
        col[recv & right & rounded_rect(L, H, SLOT_R[0], SLOT_R[1], SLOT_R[2], SLOT_R[3], 2.6)] = 12
        col[steel & side & (np.abs(H - 164.3) < 0.7) & (L > 290.0) & (L < 536.0)] *= 0.45
        cap = steel & side & (L > 468.0) & (L < 536.0) & (H > 164.0)
        pin(col, L, H, cap, 506.0, 173.5, 2.8)
        col[cap & (np.abs(L - 469.0) < 0.8)] *= 0.5
        low = steel & side & (L > 272.0) & (L < 386.0) & (H < 164.0) & (H > 116.0)
        col[low & (L > 372.0)] += 12                              # the band the stock butts against, rounded and lit
        col[low & (np.abs(L - 372.0) < 0.7)] *= 0.55
        pin(col, L, H, low, 360.0, 121.0, 2.2)
        # the wood: the sling plate's slot and screws on the left, the serial stamped behind it
        st = wood & side
        pL, pH, prl, prh = SWIVEL_PLATE
        plate = (mat == MATS.index("metal")) & left & (L > 660.0) & (L < 710.0) & (H > 68.0) & (H < 102.0)
        col[plate & rounded_rect(L, H, pL - 9.0, pL - 2.0, pH - 9.5, pH + 9.5, 2.0)] = 12
        col[plate & rounded_rect(L, H, pL + 1.0, pL + 9.0, pH - 9.5, pH + 9.5, 2.0)] = 12
        for sL, sH in ((pL - 16.0, pH + 2.0), (pL + 16.0, pH - 2.5)):
            dd = np.hypot(L - sL, H - sH)
            col[plate & (dd < 3.2)] += 20
            col[plate & (dd < 3.2) & (np.abs(H - sH) < 0.6)] = 16
        col[st & left & kit.text_mask(L, H, "7559", 770.0, 62.0, 7.0)] *= 0.55
        col[st & (L > 385.0) & (L < 388.5)] *= 0.7                # the stock's end grain against the band
        # the bore
        metal = mat == MATS.index("metal")
        col[metal & (np.hypot(x, H - BORE) < 4.1) & (L < 47.0)] = 6
        col[metal & (L > 44.0) & (L < 256.0)] *= 0.55            # the barrel in its jacket's shade
    elif kind == "bolt":
        pass
    elif kind == "drum":
        mg = mat == MATS.index("mag")
        r = np.hypot(x, z + DRUM_DROP + DRUM_R)
        face = mg & (np.abs(n[..., 1]) > 0.7)
        for rr in (0.76, 0.40):
            col[face & (np.abs(r - DRUM_R * rr) < 0.9)] *= 0.55
        col[face & (np.abs(r - DRUM_R * 0.58) < 1.4)] += 14
        band = mg & (np.abs(n[..., 1]) < 0.5) & (z < -DRUM_DROP - 2.0)
        col[band & (np.abs(y) < 3.2)] += 16                       # the rolled seam catches the light
        col[mg & (n[..., 1] < -0.7) & kit.text_mask(x, z, "71", -5.0, -DRUM_DROP - DRUM_R - 34.0, 9.0)] += 60
    elif kind == "box":
        mg = mat == MATS.index("mag")
        s = -z
        yc = BOX_R - np.sqrt(np.clip(BOX_R * BOX_R - s * s, 0, None))
        sd = mg & side & (s > 8.0) & (s < BOX_LEN - 6.0)
        col[sd & (np.abs(y - yc) < 2.6)] += 18                    # the long rib pressed into each side
        col[sd & (np.abs(np.abs(y - yc) - 3.2) < 0.6)] *= 0.6
    col = common(maps, col, mat)
    return np.clip(col, 0, 255)


def texture(objects, contexts, kinds, size, path):
    bake = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = kit.bake_maps(ob, ctx, bake)
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
    pts = {
        "muzzle": {"offset": gp(0.0, BORE), "rotate": [-90.0, 0.0, -180.0]},
        "magazine": {"offset": gp(*MAG_POINT), "rotate": ZERO},
        "bolt_lock": {"offset": ZERO, "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-HANDLE_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0],
                  "rotate": [180.0, 0.0, 180.0]},
    }
    pts["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = GoM's M24 rule for a "
                 "straight stock: the trigger 57.5 mm ahead, the bore 16 mm over it (photo L %.1f, H %.0f)" % (L0, H0),
        "magazine": "%s and %s, each with its origin at the middle of its top, pushed up into the well" % (DRUM, BOX),
        "bolt_fired": "PPSH41_BOLT (the cocking handle on the bolt, modelled forward) back %.0f mm real: each shot, "
                      "cocked (an open bolt rests back) and while empty (GoM's Bolt_Fired)" % HANDLE_TRAVEL,
    }
    pts["_extras"] = {"photo_origin_mm": [L0, H0], "bore_mm": BORE, "k": K}
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

    body, bolt = build_body(), build_handle()
    drum, mag = build_drum(), build_box()
    gun = [body, bolt]
    kit.unwrap(gun, 0.004)
    kit.unwrap([drum], 0.008)
    kit.unwrap([mag], 0.008)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture(gun, [[o] for o in gun], ["body", "bolt"], 256, os.path.join(TEX_DIR, "PPSH41.png"))
    texture([drum], [[drum]], ["drum"], 128, os.path.join(TEX_DIR, DRUM + ".png"))
    texture([mag], [[mag]], ["box"], 128, os.path.join(TEX_DIR, BOX + ".png"))

    # after painting (the paint reads the drum upright); FBX data is (x, y, -z), so foot forward is a turn the other way
    drum.data.transform(Matrix.Translation((0.0, -DRUM_BACK * K, 0.0)) @ kit.rot_x(-DRUM_TILT))
    bounds = {o.name: kit.bounds_of(o) for o in gun + [drum, mag]}
    pts = points(bounds)
    bounds["PPSH41_BOLT_fired"] = kit.bounds_of(bolt, (0, -HANDLE_TRAVEL * K, 0))
    for o in (drum, mag):
        bounds[o.name + "_fitted"] = kit.bounds_at(o, pts["magazine"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    kit.export(gun, FBX_GUN)
    kit.export([drum, mag], FBX_MAGS)
    for name, bd in bounds.items():
        print("%-30s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
