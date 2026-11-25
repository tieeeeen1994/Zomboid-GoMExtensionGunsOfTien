"""Tokarev TT pistol model and textures for GoM Extension: Guns of Tien (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_tt.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (M = Contents/mods/GoMExtensionGunsOfTien/42/media):
    M/models_X/weapons/firearms/GunsOfTien_TT33.fbx               TT33_BODY, TT33_SLIDE
    M/models_X/weapons/magazines/GunsOfTien_TT33_magazines.fbx    762x25Magazine8_TT33
    M/textures/weapons/GunsOfTien/TT33.png                         512 atlas (frame, grips, slide)
    M/textures/weapons/GunsOfTien/762x25Magazine8_TT33.png         128
    scripts/tt_points.json                                       attachment points (game space)

Fedor Tokarev's service pistol in 7.62x25mm (TT-30 of 1930, simplified as the TT-33 from 1933; user, 2026-11-23:
the Tokarev release, with the PPSh-41). Built as the wartime Tula gun the photos show: blued steel, black ribbed
bakelite grips with the star in a circle and CCCP, alternating wide and narrow slide serrations, the slide stop on the
left with its split retaining clip on the right, no safety but the hammer's half cock, a lanyard loop at the heel,
an eight-round magazine. No GoM parts: no rail, no threaded barrel.

Built as build_ppk.py builds the PPK (GoM's way for pistols): body + slide nodes, the slide drawn through
MarzGuns.Slide_Lock / Slide_Fired, the magazine in the gun's own space, modelled and baked upright and turned upside
down at export, origin 11 mm behind the deepest point of the back strap under the tang at its height, 0.603 of real
size (every Guns of Tien gun).

References: references/tt/ (SOURCES.tsv, sheet_*.png; fetched with scripts/ref_hunt.py). Measured on
a flat studio photo of a 1944 TT-33's left side (Wikimedia Commons "Tokarev TT-33-IMG 6553-white.jpg", Rama, CC BY-SA
2.0 FR; references/tt/tt33_left_rama_6553.jpg, 1920 px), traced (post93/trace_outline.py, threshold 235) into
scripts/tt_reference_outline.json at 195 mm (7.70 px a mm; the height then reads 127.6 mm from the magazine's base to
the rear sight, the published 134 with the lanyard loop hanging). Profiles are in that photo's (L, H) mm: L back from
the muzzle, H up from the magazine's base. Inner lines were read off gridded crops (scripts/ref_crop.py). Right-side
parts (ejection port, extractor, retaining clip) from Armemuseum's right-side photo of a 1940 gun (Commons "TT-30
Tokarev 002.jpg", which is a TT-33 whatever its file name) and Rock Island Auction's lots (nine TT-33s, six angles
each). Widths: 30 mm over the grips (published); slide and frame from the auction lots' rear and top views.
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
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_TT33.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_TT33_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "tt_points.json")
MAG_NAME = "762x25Magazine8_TT33"

K = 0.000603                       # game units per real mm: the M16A2's proportion (every Guns of Tien gun)
K_OLD = 0.00072                    # GoM's pistols: the `world` floor point is scaled from them
kit.K = K
MATS = ["metal", "grip", "barrel", "dark", "magsteel", "brass", "copper"]
kit.MATS[:] = MATS
for ch, rows in {"C": ["111", "100", "100", "100", "111"], "8": ["111", "101", "111", "101", "111"],
                 "9": ["111", "101", "111", "001", "111"], "5": ["111", "100", "111", "001", "111"]}.items():
    kit.FONT.setdefault(ch, rows)

# Origin: 11 mm behind the deepest point of the back strap under the tang (L 180.4, H 70), at its height
L0, H0 = 191.4, 70.0
BORE_H = 109.8                     # the barrel's centre at the muzzle (H 104.2 to 115.5)
SLIDE_TOP, SLIDE_BOTTOM = 121.3, 100.2
SLIDE_TRAVEL = 40.0                # GoM's Glock 17 runs back 32 mm; the 35 mm Tokarev round a little more
W_SLIDE, W_FRAME, W_GRIP, W_GUARD = 10.8, 9.6, 15.0, 4.6
W_MAG, W_BASE = 6.2, 7.6
ROUND_TOP = 4.6                    # the slide's shoulders round over its upper 4.6 mm (the highlight band H 117-121)
TOP_FLAT = 4.6                     # half width of the flat along the top
RAKE = 0.2214                      # the front strap's lean: mm forward per mm up (L 147.6 H 5.3 to L 138.7 H 45.5)


def P(L, H):
    return L0 - L, H - H0


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="metal", x0=0.0):
    return kit.slab(b, [P(L, H) for L, H in outline], [[P(L, H) for L, H in h] for h in holes], half, bevel, res,
                    mat, x0)


def circle(cL, cH, r, a0=0.0, a1=360.0, n=24, rh=None):
    """Points on a circle (an ellipse with rh) in (L, H), from angle a0 to a1 degrees (0 = toward the rear, 90 = up)."""
    rh = r if rh is None else rh
    return [(cL + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cH + rh * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + (0 if a1 - a0 >= 360 else 1))]


# ==================================================================================================
# Profiles (photo L, H mm)
# ==================================================================================================

def slide_top(L):
    """The slide's top edge: the bushing's lower face, flat, then the rounded rear down to the frame's tang."""
    pts = [(1.8, 119.9), (3.8, 120.3), (4.4, 121.6), (80.0, SLIDE_TOP), (183.5, SLIDE_TOP), (185.5, 119.3),
           (187.3, 116.8), (190.5, 112.6), (191.9, 110.7), (193.7, 106.9), (194.7, 103.4), (195.0, 100.6)]
    return float(np.interp(L, [p[0] for p in pts], [p[1] for p in pts]))


def slide_half(L):
    """The slide's rear corners are rounded seen from above, the bushing a little narrower than the slide."""
    return float(np.interp(L, [1.8, 4.3, 4.5, 190.0, 193.0, 195.0], [W_SLIDE - 0.7, W_SLIDE - 0.7, W_SLIDE, W_SLIDE,
                                                                     W_SLIDE - 0.8, W_SLIDE - 2.6]))


SLIDE_STATIONS = sorted(set([1.8, 2.6, 3.8, 4.3, 4.5, 20.0, 50.0, 80.0, 120.0, 160.0, 183.5, 184.5, 185.5, 186.4,
                             187.3, 188.9, 190.5, 191.9, 192.8, 193.7, 194.2, 194.7, 195.0]))
ARC = 6                            # points per quarter of the rounded shoulders


def slide_section(L):
    hb, ht, w = SLIDE_BOTTOM, slide_top(L), slide_half(L)
    h = max(ht - hb, 0.3)
    rr = min(ROUND_TOP, h * 0.8)
    tf = TOP_FLAT * min(1.0, w / W_SLIDE)
    c = min(0.5, h * 0.15)
    e = 2.0 / 2.4                                         # a superellipse, a little squarer than a circle
    right = [(w, hb + c), (w, ht - rr)]
    for k in range(1, ARC):
        t = math.pi / 2 * k / ARC
        right.append((tf + (w - tf) * math.cos(t) ** e, ht - rr + rr * math.sin(t) ** e))
    right.append((tf, ht))
    left = [(-x, H) for x, H in reversed(right)]
    return [(w - c, hb)] + right + left + [(-w + c, hb)]


# The slide's lower front: the recoil spring's housing under the barrel, ending where the frame's dust cover begins
TUNNEL = [(1.8, 101.5), (51.0, 101.5), (51.0, 89.1), (26.4, 89.1), (1.8, 88.7)]

FRONT_SIGHT = [(4.6, 121.2), (6.4, 121.9), (6.9, 123.9), (7.9, 124.7), (14.3, 124.7), (14.7, 124.5), (14.9, 122.0),
               (14.9, 121.2)]
REAR_SIGHT = [(164.6, 121.0), (164.9, 121.9), (165.2, 125.6), (165.9, 126.1), (166.5, 126.3), (167.1, 127.2),
              (167.7, 127.6), (168.9, 127.4), (169.1, 127.2), (169.8, 123.5), (170.7, 121.6), (170.7, 121.0)]

# Frame: the dust cover from the slide's step, the top under the slide, the tang, the back strap, the butt, the front
# strap up to the trigger guard's rear root, the roof of the guard's opening, the guard's front root.
FRAME = [(51.3, 100.4), (195.0, 100.4), (195.0, 93.9), (194.1, 90.2), (192.5, 87.6), (190.3, 85.4), (187.1, 83.0),
         (183.3, 79.1), (182.1, 77.3), (181.4, 75.3), (180.8, 73.5), (180.4, 69.9), (180.8, 64.4), (182.1, 57.2),
         (188.1, 34.2), (190.7, 25.1), (192.4, 17.9), (193.2, 13.0), (193.2, 9.4), (192.8, 6.5), (192.0, 5.7),
         (147.9, 5.2), (147.6, 5.6), (143.9, 22.9), (138.7, 45.5), (136.7, 51.7), (135.1, 54.4), (132.8, 56.5),
         (131.0, 57.2), (128.4, 58.6), (128.2, 86.2), (97.0, 86.2), (85.5, 86.7), (76.3, 87.0), (51.3, 86.3)]

# The trigger guard and its opening (the opening's front and bottom off the trace; its rear wall behind the trigger)
GUARD = [(79.0, 93.0), (79.0, 86.7), (81.7, 85.7), (84.1, 84.2), (86.3, 81.3), (87.2, 79.0), (89.5, 69.4), (90.2, 67.6),
         (91.2, 65.3), (92.2, 63.8), (93.7, 62.0), (95.0, 60.9), (99.4, 58.7), (103.0, 57.8), (108.3, 57.6),
         (118.5, 58.3), (124.7, 58.3), (129.5, 57.7), (132.8, 56.5), (134.4, 55.4), (134.4, 64.0), (131.0, 93.0)]
OPENING = [(101.6, 86.0), (127.2, 86.0), (127.6, 80.0), (127.6, 70.0), (127.0, 65.0), (125.6, 62.4), (123.0, 61.2),
           (110.6, 60.9), (105.9, 60.9), (103.9, 61.2), (100.8, 62.0), (98.3, 63.1), (96.4, 64.6), (94.6, 66.6),
           (93.4, 69.0), (92.8, 71.5), (92.2, 74.8), (92.5, 77.6), (92.9, 79.0), (94.2, 81.8), (95.9, 83.9),
           (97.2, 84.8), (98.5, 85.4)]
# The trigger (it slides straight back): the front face off the trace, bowed back to L 115.6, the tip at L 109.9
# H 61.5, the broad body behind it up into the frame
TRIGGER = [(116.6, 88.5), (116.4, 86.1), (115.8, 85.9), (114.7, 85.1), (113.7, 83.9), (113.4, 83.3), (113.5, 80.9),
           (114.7, 78.5), (115.4, 76.5), (115.6, 74.8), (115.6, 71.8), (115.2, 69.4), (113.8, 65.7), (112.9, 64.4),
           (109.9, 61.6), (110.6, 61.1), (113.0, 60.5), (124.0, 60.5), (126.5, 61.4), (128.6, 64.0), (129.0, 88.5)]

# The grip panels (one each side, clipped on from inside: no screws). The left one is cut away at the heel for the
# lanyard loop.
# Edges read off the photo's brightness along rows and columns (ribs against smooth steel): the top at H 88.5, the
# rear edge leaning back from L 171 under the tang to 2.8 mm inside the back strap, the front edge 7.5 mm behind the
# front strap.
GRIP_TOP = [(140.0, 84.0), (140.6, 86.2), (142.0, 87.8), (144.5, 88.5), (150.0, 88.8), (160.0, 88.3), (166.0, 87.5),
            (169.0, 86.6), (171.0, 85.0), (172.5, 82.5), (174.0, 78.0), (176.5, 70.0), (178.8, 62.0), (180.6, 55.0),
            (185.5, 36.0), (188.4, 25.0)]
GRIP_FRONT = [(155.4, 5.9), (154.4, 6.6), (153.5, 10.0), (151.3, 20.0), (149.3, 30.0), (147.7, 40.0), (145.2, 50.0),
              (144.0, 60.0), (141.9, 70.0), (141.5, 78.0)]
GRIP = GRIP_TOP + [(190.0, 17.5), (190.8, 12.5), (190.8, 8.5), (190.2, 6.3), (189.0, 5.9)] + GRIP_FRONT
GRIP_LEFT = GRIP_TOP + [(189.6, 19.2), (185.0, 19.8), (181.0, 18.8), (178.5, 16.0), (177.2, 12.0),
                        (176.8, 5.9)] + GRIP_FRONT
EMBLEM = (163.2, 48.8, 10.5, 8.6)  # centre, the ring's outer and inner radius
RIVET_R = 2.6

# The slide stop on the left: a flat lever from its round front end on the axis pin to the thumb piece at the rear,
# which turns up into the slide's notch; a raised shelf for the thumb
STOP_AXIS = (108.7, 94.3)
SLIDE_STOP = circle(108.9, 94.3, 3.3, 70.0, 290.0, 14) + [
    (117.0, 91.3), (124.0, 92.6), (133.0, 95.2), (138.5, 96.6), (140.6, 97.8), (140.8, 100.4), (138.0, 100.4),
    (136.8, 98.6), (118.5, 98.2), (112.0, 97.7)]
STOP_SHELF = [(118.5, 96.1), (133.5, 96.5), (135.0, 98.5), (118.5, 98.4)]
# its split retaining clip on the right: a flat spring forked round the axis pin's groove, riveted behind
CLIP = [(105.0, 91.4), (131.2, 91.4), (132.4, 92.6), (132.4, 97.2), (131.2, 98.4), (105.0, 98.4), (103.9, 97.3),
        (103.9, 92.5)]
CLIP_RIVET = (127.1, 94.9)

HAMMER_C, HAMMER_R = (178.3, 119.6), 5.4          # the round knurled spur, down
MAG_BUTTON = (136.2, 66.3, 3.0)    # left side, a round head; the catch's slotted end on the right
FRAME_PIN = (159.8, 114.7)         # the firing pin's retaining pin through the slide (slotted on the left)
LOOP = (185.6, 11.0, 4.8, 3.3)     # the lanyard loop, folded up against the frame in the left panel's cut

# The magazine: raked as the front strap, 36 mm deep; its base plate a little longer and tilted (lower at the front)
MAG_DEPTH, MAG_TOP, MAG_FOOT = 36.0, 92.0, 3.0


def mag_front(H):
    return 150.9 - RAKE * (H - 5.7)


MAG_BODY = [(mag_front(MAG_FOOT), MAG_FOOT), (mag_front(MAG_FOOT) + MAG_DEPTH, MAG_FOOT),
            (mag_front(MAG_TOP) + MAG_DEPTH, MAG_TOP), (mag_front(MAG_TOP), MAG_TOP)]
MAG_BASE = [(147.3, 2.1), (147.5, 0.4), (149.3, 0.0), (161.5, 0.5), (188.6, 1.2), (189.7, 2.2), (189.7, 3.9),
            (188.0, 4.3), (149.9, 3.4), (147.6, 2.6)]
ROUND_TIP = mag_front(MAG_TOP) + 0.8


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
    slab(b, GUARD, [OPENING], half=W_GUARD, bevel=1.1, res=1)
    slab(b, GRIP, half=W_GRIP / 2, bevel=2.2, res=2, mat="grip", x0=-W_GRIP / 2)      # the right panel
    slab(b, GRIP_LEFT, half=W_GRIP / 2, bevel=2.2, res=2, mat="grip", x0=W_GRIP / 2)
    slab(b, TRIGGER, half=2.7, bevel=0.8, res=1)
    cL, cH = HAMMER_C
    hammer = []                                           # the spur's rim is cut into teeth
    for k in range(57):
        a = math.radians(-40.0 + 260.0 * k / 56)
        r = HAMMER_R - (0.55 if k % 2 else 0.0)
        hammer.append((cL + r * math.cos(a), cH + r * math.sin(a)))
    hammer += [(174.6, 108.0), (181.6, 108.0)]
    slab(b, hammer, half=3.2, bevel=0.25)
    # the slide stop and its shelf on the left (+X upright), its clip on the right
    slab(b, SLIDE_STOP, half=0.9, bevel=0.35, res=1, x0=W_FRAME + 0.7)
    slab(b, STOP_SHELF, half=1.3, bevel=0.4, res=1, x0=W_FRAME + 1.6)
    slab(b, CLIP, half=0.5, bevel=0.2, x0=-(W_FRAME + 0.4))
    aL, aH = STOP_AXIS
    b.lathe("x", (0.0, L0 - aL, aH - H0), [(-W_FRAME - 1.5, 0.0), (-W_FRAME - 1.5, 1.6), (W_FRAME, 1.6),
                                           (W_FRAME, 0.0)], seg=12, mat="metal")
    rL, rH = CLIP_RIVET
    b.lathe("x", (0.0, L0 - rL, rH - H0), [(-W_FRAME - 1.3, 0.0), (-W_FRAME - 1.3, 1.5), (-W_FRAME, 1.5),
                                           (-W_FRAME, 0.0)], seg=10, mat="metal")
    # the magazine catch: a round button on the left, its slotted end flush on the right
    bL, bH, br = MAG_BUTTON
    b.lathe("x", (0.0, L0 - bL, bH - H0), [(-W_FRAME - 0.4, 0.0), (-W_FRAME - 0.4, br - 0.6), (W_FRAME, br - 0.6),
                                           (W_FRAME, br), (W_FRAME + 1.6, br), (W_FRAME + 2.3, br - 0.9),
                                           (W_FRAME + 2.3, 0.0)], seg=16, mat="metal")
    # the lanyard loop: a wire ring folded up against the frame's left side
    oL, oH, ra, rb_ = LOOP
    slab(b, circle(oL, oH, ra, 0.0, 360.0, 20, rb_), [circle(oL, oH, ra - 1.5, 0.0, 360.0, 16, rb_ - 1.5)[::-1]],
         half=0.75, bevel=0.5, res=1, x0=W_FRAME + 0.75)
    # the barrel: out of the bushing by 1.8 mm, the bore recessed at the crown; bared when the slide runs back
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(SLIDE_TRAVEL + 26.0), 0), (t(SLIDE_TRAVEL + 26.0), 5.7), (t(0.4), 5.7),
                                       (t(0.0), 5.2), (t(0.0), 3.3), (t(1.4), 2.9), (t(1.4), 0)], seg=18,
            mat="barrel", phase=0.5)
    return b.to_object("TT33_BODY")


def build_slide():
    b = kit.Builder()
    loft(b, [(L, slide_section(L)) for L in SLIDE_STATIONS], "metal")
    # narrower than the frame: it runs back into the dust cover when the slide recoils
    slab(b, TUNNEL, half=W_FRAME - 1.2, bevel=4.0, res=2)
    slab(b, FRONT_SIGHT, half=1.2, bevel=0.35, res=1)
    slab(b, REAR_SIGHT, half=4.2, bevel=0.5, res=1)
    # the bushing's collar round the barrel
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_H - H0), [(t(2.2), 5.9), (t(0.5), 5.9), (t(0.5), 7.9), (t(1.4), 8.2), (t(2.2), 8.2)],
            seg=18, mat="metal", phase=0.5)
    return b.to_object("TT33_SLIDE")


def build_magazine():
    b = kit.Builder()
    slab(b, MAG_BODY, half=W_MAG, bevel=0.9, res=1, mat="magsteel")
    slab(b, MAG_BASE, half=W_BASE, bevel=0.8, res=1, mat="magsteel")
    front, rear = mag_front(MAG_TOP), mag_front(MAG_TOP) + MAG_DEPTH
    lips = [(front + 9.0, MAG_TOP - 0.2), (rear - 1.0, MAG_TOP - 0.2), (rear - 2.0, MAG_TOP + 3.0),
            (front + 15.0, MAG_TOP + 3.0)]
    for s in (1, -1):
        slab(b, lips, half=0.6, bevel=0.2, mat="magsteel", x0=s * (W_MAG - 0.6))
    rL = ROUND_TIP                          # the top round: a bottle-necked case, a round-nosed jacketed bullet
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, MAG_TOP + 3.6 - H0), [(t(rL + 34.6), 0), (t(rL + 34.6), 4.95), (t(rL + 33.4), 4.95),
                                              (t(rL + 33.2), 4.4), (t(rL + 32.4), 4.4), (t(rL + 32.2), 4.9),
                                              (t(rL + 16.0), 4.75), (t(rL + 13.4), 4.2), (t(rL + 10.6), 4.2),
                                              (t(rL + 10.6), 3.95), (t(rL + 5.0), 3.7), (t(rL + 2.2), 2.7),
                                              (t(rL + 0.7), 1.5), (t(rL), 0)], seg=12, mat="brass", phase=0.5)
    return b.to_object(MAG_NAME)


# ==================================================================================================
# Painting
# ==================================================================================================

BASE = {  # sRGB, off the measuring photo (user, 2026-11-25: "change the texture of TT-33 to copper as well like the
    # reference"): bluing worn to a warm copper-brown patina (its slide reads 138 118 101 lit, its frame 99 81 72),
    # dark brown bakelite grips (ribs 78 58 46 to 167 147 133), the same steel for the bore and the magazine
    "metal": (132, 104, 80), "grip": (50, 35, 26), "barrel": (138, 112, 90), "dark": (22, 19, 17),
    "magsteel": (104, 84, 68), "brass": (156, 122, 64), "copper": (150, 100, 70),
}


def in_poly(L, H, pts):
    inside = np.zeros(L.shape, bool)
    for i in range(len(pts)):
        (la, ha), (lb, hb) = pts[i], pts[(i + 1) % len(pts)]
        if ha == hb:
            continue
        inside ^= ((ha > H) != (hb > H)) & (L < la + (H - ha) * (lb - la) / (hb - ha))
    return inside


def pin(col, L, H, sel, cL, cH, r=1.2, slot=None):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.45)] *= 0.45
    col[sel & (d <= r - 0.45)] += 14
    if slot is not None:                                  # a screwdriver slot at `slot` degrees
        a = math.radians(slot)
        off = np.abs((L - cL) * math.sin(a) + (H - cH) * math.cos(a))
        col[sel & (d <= r - 0.45) & (off < 0.3)] = 14


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("metal", "barrel", "magsteel", "brass", "copper")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.9 + 0.2 * streak[is_metal])[..., None]
    up = np.clip(n[..., 2], -1, 1)
    col *= (0.98 + 0.12 * up)[..., None]
    col[is_metal] += (np.clip(up[is_metal], 0, 1) * 9.0)[..., None] * np.array([1.15, 1.0, 0.85])
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 80.0, 30.0) * (0.75 + 0.5 * kit.vnoise(p, 2.5, 5))     # holster wear on blued edges
    col += (convex * wear)[..., None] * np.array([1.0, 0.92, 0.84])
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def star(L, H, cL, cH, ro, ri, turn=0.0):
    """A five-pointed star, one point up (turned `turn` degrees)."""
    pts = []
    for k in range(10):
        a = math.radians(90.0 + turn + 36.0 * k)
        r = ro if k % 2 == 0 else ri
        pts.append((cL + r * math.cos(a), cH + r * math.sin(a)))
    return in_poly(L, H, pts)


# the slide's grip serrations: wide oval cuts with a narrow one between each pair (the wartime pattern), the narrow
# ones running out of the slide's lower edge
SERR = dict(first=147.5, pitch=6.17, count=7, wide=1.8, top=117.6, bottom=103.8, narrow_top=117.2)
RELIEF = (5.2, 44.5, 100.6, 107.7)          # the flat milled into each side at the front, its rear end curving down
NOTCH = (86.0, 95.0, 102.8)                 # the slide stop's take-down notch in the slide's lower edge, left side
PORT = (82.2, 113.2, 112.0)                 # the ejection port: L from, L to, its lower edge on the right side
EXTRACTOR = (113.2, 139.6, 113.0, 115.3)    # the bar behind the port, on the right


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
        gs = grip & side & (np.abs(x) > W_GRIP - 1.0)
        eL, eH, ro, ri = EMBLEM
        d = np.hypot(L - eL, H - eH)
        # vertical ribs leaning as the grip does, a band of level ones along the bottom
        u = L + RAKE * H
        rib = np.mod(u, 2.4)
        band = H < 9.2
        field = gs & (d > ro) & ~band
        col[field & (rib < 0.9)] *= 0.34
        col[field & (rib >= 0.9) & (rib < 1.6)] += 52
        col[field & (rib >= 1.6)] += 16
        hb = np.mod(H, 1.1)
        col[gs & band & (hb < 0.45)] *= 0.45
        col[gs & band & (hb >= 0.45)] += 18
        # the emblem: a raised ring, a stippled ground, the star, CCCP between its points, the catch's rivet
        ring = gs & (d <= ro) & (d > ri)
        col[ring] += 34
        col[gs & (np.abs(d - ro) < 0.45)] *= 0.3
        col[gs & (np.abs(d - ri) < 0.4)] *= 0.35
        ground = gs & (d <= ri)
        col[ground] *= 0.75
        col[ground & ((np.mod(L * 1.6, 1.0) < 0.5) ^ (np.mod(H * 1.6, 1.0) < 0.5))] *= 0.6
        st = ground & star(L, H, eL, eH, 8.3, 3.3)
        col[st] = np.array(BASE["grip"]) + 44
        col[st & ~star(L, H, eL, eH, 7.5, 2.7)] *= 0.45       # the star's raised edge
        ang = np.degrees(np.arctan2(H - eH, L - eL))
        col[st & (np.mod(ang + 90.0, 36.0) < 2.2) & (d > 1.0)] *= 0.55          # the arms' ridges and valleys
        for letter, a in (("C", 126.0), ("C", 54.0), ("C", 198.0), ("P", -18.0)):
            for sel, uu, sgn in ((gs & left, L, 1.0), (gs & right, -L, -1.0)):
                # u runs to screen right on either side (the left side shows L growing to the right), so the
                # letters read left to right on both panels
                cu = sgn * eL + 6.3 * math.cos(math.radians(a))
                cv = eH + 6.3 * math.sin(math.radians(a))
                col[sel & ground & ~st & kit.text_mask(uu, H, letter, cu - 0.9, cv - 1.25, 2.5)] += 34
        col[gs & (d < RIVET_R)] = (176, 148, 128)
        col[gs & (np.abs(d - RIVET_R) < 0.35)] = 14
        frame = metal & side & (np.abs(x) > W_FRAME - 0.6) & (np.abs(x) < W_FRAME + 0.25)
        col[frame & left & (L > 176.0) & (H < 20.5)] *= 0.6
        # the serial and the year on the frame's left under the slide, Tula's star between them
        col[frame & left & kit.text_mask(L, H, "81087", 146.6, 94.3, 2.9)] += 30
        col[frame & left & kit.text_mask(L, H, "1941", 170.6, 94.3, 2.9)] += 30
        col[frame & left & star(L, H, 166.4, 95.7, 1.6, 0.65)] += 30
        # the slide stop: its axis pin's head, the shelf's grooves; the clip's fork and rivet on the right
        aL, aH = STOP_AXIS
        lev = metal & left & (x > W_FRAME + 0.3)
        col[lev] += 22                                       # worn bright: the thumb rubs it
        col[lev & in_poly(L, H, STOP_SHELF) & (np.mod(L, 1.3) < 0.5)] *= 0.5
        clip = metal & right & (x < -W_FRAME - 0.3)
        col[clip] += 16
        col[clip & (np.abs(H - aH) < 0.3) & (L > 103.8) & (L < 124.0)] = 14          # the fork's slit
        pin(col, L, H, clip, aL, aH, 1.6)
        pin(col, L, H, clip, *CLIP_RIVET, 1.5)
        # the magazine catch: a knurled button on the left, a slotted head on the right
        bL, bH, br = MAG_BUTTON
        db = np.hypot(L - bL, H - bH)
        knurl = metal & left & (x > W_FRAME + 1.8) & (db < br - 0.3)
        col[knurl & ((np.mod(L * 2.4, 1.0) < 0.35) ^ (np.mod(H * 2.4, 1.0) < 0.35))] *= 0.55
        pin(col, L, H, metal & right & (x < -W_FRAME + 0.1), bL, bH, br - 0.6, slot=20.0)
        # the hammer's knurled rim
        cL, cH = HAMMER_C
        dh = np.hypot(L - cL, H - cH)
        rim_f = metal & ~side & (dh > HAMMER_R - 1.0) & (H > 112.0) & (np.abs(x) < 3.4)
        angh = np.arctan2(H - cH, L - cL)
        col[rim_f & (np.mod(angh * 30 / np.pi, 1.0) < 0.45)] *= 0.45
        col[metal & in_poly(L, H, TRIGGER) & (np.abs(x) < 2.9) & (H < 86.0)] += 8
        # grooves across the back strap and the front strap's lower half? no: both are plain on the TT
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[(mat == MATS.index("barrel")) & (r < 3.2) & (L < 1.5)] = 8              # the bore
        col[(mat == MATS.index("barrel")) & fwd & (r < 5.4) & (r > 3.2)] += 18      # the crown
    elif kind == "slide":
        sl = metal & side & (np.abs(x) > W_SLIDE - 0.9)
        s = SERR
        ser = sl & (H > SLIDE_BOTTOM) & (H < s["top"] + 0.5)
        for k in range(s["count"]):
            c = s["first"] + s["pitch"] * k
            # the wide cut: a tall oval, shaded on its front wall and lit on its rear one
            hc = (s["top"] + s["bottom"]) / 2
            hh = (s["top"] - s["bottom"]) / 2
            e = ((L - c) / s["wide"]) ** 2 + (np.clip(np.abs(H - hc) - (hh - s["wide"]), 0, None) / s["wide"]) ** 2
            inside = ser & (e < 1.0)
            col[inside] += 20
            col[inside & (L < c - 0.5)] *= 0.45
            col[inside & (L > c + 0.6)] += 46
            col[ser & (e >= 1.0) & (e < 1.4)] *= 0.55
            # the narrow cut ahead of it, down through the lower edge
            cn = c - s["pitch"] / 2
            nar = ser & (np.abs(L - cn) < 0.55) & (H < s["narrow_top"]) & (L > 143.5)
            col[nar] *= 0.3
            col[ser & (np.abs(L - cn - 0.85) < 0.32) & (H < s["narrow_top"]) & (L > 143.5)] += 50
        # the relief flats at the front: darker (they keep their blue), the step along their top edge lit
        la, lb, ha, hb = RELIEF
        end = lb + 5.5 * np.clip((hb - H) / (hb - ha), 0, 1) ** 0.5
        rel = sl & (L > la) & (L < end) & (H > ha) & (H < hb)
        col[rel] *= 0.5
        col[sl & (L > la) & (L < lb + 1.0) & (np.abs(H - hb - 0.3) < 0.35)] += 30
        col[sl & (np.abs(L - 4.5) < 0.3)] *= 0.45                                  # the bushing's joint
        col[sl & (np.abs(L - 5.2) < 0.35)] += 34
        tun = metal & side & (H < SLIDE_BOTTOM) & (L < 51.5)
        col[tun & (np.abs(L - 4.5) < 0.3)] *= 0.5
        # the slide stop's notch in the lower edge, left side
        na, nb, nh = NOTCH
        notch = sl & left & (L > na) & (L < nb) & (H < SLIDE_BOTTOM + (nh - SLIDE_BOTTOM) * np.clip((L - na) / 6.0, 0, 1) ** 0.6)
        col[notch] = 12
        col[sl & left & (np.abs(L - nb - 0.4) < 0.35) & (H < nh)] += 30
        # the ejection port on the right, over the shoulder to the top; the barrel's chamber in it
        pa, pb, ph = PORT
        port = metal & (x < 1.0) & (L > pa) & (L < pb) & (H > ph)
        col[port] = (48, 40, 35)
        edge_p = port & ((np.abs(L - pa) < 0.8) | (np.abs(L - pb) < 0.8) | ((H < ph + 0.8) & (x < 0)) | (x > 0.2))
        col[edge_p] = 10
        ea, eb, eh0, eh1 = EXTRACTOR
        ext = sl & right & (L > ea) & (L < eb) & (H > eh0) & (H < eh1)
        col[ext] += 12
        col[sl & right & (L > ea) & (L < eb) & ((np.abs(H - eh0) < 0.3) | (np.abs(H - eh1) < 0.3))] *= 0.45
        col[sl & right & (np.abs(L - eb) < 0.3) & (H > eh0) & (H < eh1)] *= 0.45
        # the firing pin's retaining pin: slotted on the left, plain on the right
        pin(col, L, H, sl & left, *FRAME_PIN, 1.5, slot=35.0)
        pin(col, L, H, sl & right, *FRAME_PIN, 1.3)
        # the rear sight's notch, the hammer's slot in the slide's rear
        rs = metal & (L > 164.0) & (L < 171.0) & (H > 124.6) & (np.abs(x) < 0.9)
        col[rs] = 8
        col[metal & (np.abs(x) < 3.5) & (L > 172.5) & (H > 108.0) & ~side & (up | back)] = 12
        r = np.hypot(x, p[..., 2] - (BORE_H - H0))
        col[metal & fwd & (L < 2.6) & (r < 6.0)] = 12        # the bushing's hole round the barrel
        # the recoil spring's plug in the tunnel's front face
        rp = np.hypot(x, H - 94.6)
        col[metal & fwd & (L < 3.0) & (H < 100.0) & (np.abs(rp - 3.6) < 0.35)] *= 0.4
    elif kind == "mag":
        ms = mat == MATS.index("magsteel")
        msd = ms & side & (H > 5.0)
        # witness holes on both sides: a staggered row of seven
        for k in range(7):
            hh = MAG_TOP - 14.0 - k * 10.5
            ll = mag_front(hh) + MAG_DEPTH * (0.62 if k % 2 == 0 else 0.42)
            dd = np.hypot(L - ll, H - hh)
            col[msd & (dd < 1.5)] = 10
            col[msd & (dd < 2.0) & (dd >= 1.5)] += 16
        br = mat == MATS.index("brass")
        col[br & (L < ROUND_TIP + 10.6)] = BASE["copper"]
        col[br & back & (np.hypot(x, p[..., 2] - (MAG_TOP + 3.6 - H0)) < 2.2)] *= 0.8
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
        "parts": "none: no rail and no threaded barrel on a Tokarev",
        "slide_fired": "TT33_SLIDE back %.0f mm real" % SLIDE_TRAVEL,
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
    texture([body, slide], [[body, slide], [body, slide]], ["gun", "slide"], 512, os.path.join(TEX_DIR, "TT33.png"))
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
