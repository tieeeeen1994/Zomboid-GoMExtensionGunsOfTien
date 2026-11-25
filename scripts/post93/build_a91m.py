"""KBP A-91M (7.62x39) bullpup with its integral 40 mm launcher, for Guns of Tien - Post-93 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_a91m.py -- [--size 1024]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_A91M.fbx    A91M_BODY (the rifle with its launcher under the barrel),
                                                            A91M_BOLT (the charging hook on the gas piston rod, under
                                                            the carrying handle: GoM's AK swap draws it back on each
                                                            shot), A91M_RAIL_UP (GoM's Picatinny rail on our clamp on
                                                            the carrying handle, the Grozas' way)
    M/textures/weapons/GunsOfTienPost93/A91M.png             512 atlas (body, bolt and mount)
    scripts/post93/a91m_points.json                          attachment points (game space)

User, 2026-11-25 (docs/post93_design.md "KBP A-91M"): the bullpup with the 40 mm launcher is the A-91M of 1998
(Post-93). The 5.56A-91 was built beside it and removed the same day; the first model (flat extruded silhouettes) was
rejected ("terrible looking") and rebuilt here in three remodel passes (CLAUDE.md "A-91M").

References in references/a91 (SOURCES.txt). The measuring photo is GunRF's A91M2.jpg (880 px, studio LEFT side, muzzle
left) at 1.294 px a mm (660 mm, brake tip x 12 to the butt's back x 858); every profile below is in its pixels (x
rearward, y down), read from 4-5x gridded crops. What each part is comes from the other photos: GunRF's field strip
(a91m_raz.jpg: the barrel carries the tall front sight tower and the gas block with the handle's front post; the
launcher, its sight housing, the handguard, grip and triggers are one lower; the hook-shaped charging handle sits on
the piston rod) and the 5.56A-91 photos on Commons (A-91.jpg, Kuzmin's Interpolitex 2011 / 2012: the same lower, upper
and handle from 3/4, which give the depths: a narrow sight housing on a wider launcher breech, raised bars along the
handguard's lower edge, a polymer cheek cover wider than the steel receiver under it, a thick butt pad, the handle's
rear strut as two plates pinned to the lower).
Origin: the grip's back meets the receiver (the Grozas' and MDRx's), so the hands sit as on GoM's FAMAS.

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
import build_mp7 as kit  # noqa: E402

MEDIA = kit.MEDIA
TEX_DIR = kit.TEX_DIR
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_A91M.fbx")
POINTS_JSON = os.path.join(HERE, "a91m_points.json")
GOM = kit.GOM

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "poly", "dark", "rubber", "metal", "bright"]
kit.MATS[:] = MATS
ZERO = [0.0, 0.0, 0.0]

# ==================================================================================================
# Photo frame: px -> game (y forward, z up) mm, origin at the grip's rear top
# ==================================================================================================

S = 1.294                          # px a mm
ORIGIN = (495.0, 168.0)
BORE = 126.0                       # the bore's row


def P(x, y):
    return (ORIGIN[0] - x) / S, (ORIGIN[1] - y) / S


def PL(pts):
    return [P(x, y) for x, y in pts]


def mm(px):
    return px / S


def ellipse(cx, cy, rx, ry, n=24):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rrect(x0, y0, x1, y1, r, n=4):
    """A rounded rectangle in photo px (y down)."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ==================================================================================================
# The A-91M's profiles (GunRF A91M2.jpg px)
# ==================================================================================================

G7 = dict(
    brake=(12.0, 49.0, 12.5),                          # x from, to, radius px (19 mm across, slotted)
    # the launcher's sight housing on top of its breech: narrow, a see-through window at the front, the quadrant's
    # dial on the left
    sight_base=[(50, 87), (54, 84), (100, 83), (126, 80), (140, 74), (152, 68), (164, 65), (174, 66), (180, 71),
                (183, 79), (183, 128), (120, 128), (120, 112), (50, 112)],
    sight_window=[(64, 89), (88, 89), (88, 96), (80, 103), (72, 103), (64, 96)],   # the notch plate's cutout
    sight_pin=(106.0, 97.0, 3.2),
    dial=(162.0, 98.0, 13.0),                          # a round hole in the housing, the quadrant's lever across it
    dial_lever=(158.0, 95.0, 185.0, 101.0),
    breech=[(47, 114), (50, 111), (122, 109), (152, 126), (183, 126), (183, 150), (47, 150)],
    tube=(42.0, 190.0, 173.0, 30.0),                   # x front, rear, axis y, radius px (46 mm across)
    tube_rings=((150.0, 160.0), (180.0, 190.0)),
    tube_lug=[(152, 197), (166, 197), (166, 208), (160, 210), (152, 208)],
    # the rifle's front sight: a tall A-frame on the barrel (its line is the carrying handle's), hooded at the top
    tower=[(178, 27), (181, 22), (187, 20), (193, 22), (197, 28), (197, 50), (217, 113), (178, 113)],
    tower_window=[(185, 54), (192.5, 54), (211, 111), (185, 111)],
    tower_slot=(183.5, 29.0, 191.5, 46.0, 3.8),        # the oval slot in each side plate, the post seen through it
    post=(186.0, 189.5, 27.0, 50.0),
    # the lower: launcher casing, handguard and trigger housing in one, the guard's opening
    lower=[(183, 112), (549, 112), (549, 167), (446, 167), (446, 200), (183, 200)],
    # x0, y0, x1, y1; its front end is half an oval (rx 13.5 px), its rear end a half circle
    opening=(345.0, 152.5, 436.0, 194.5, 13.5),
    ribs=dict(first=203.0, pitch=15.1, count=10, w=8.0, top=176.0, bottom=200.0),
    # the launcher's trigger is a C-shaped bar across the opening, joined to its top and bottom edges: with the
    # opening's front end it closes one oval (user, 2026-11-25: "it's not a separate circle... it's like a C connected
    # to the oval"; Commons A-91.jpg, 6x crop). The rifle's is a broad fin hanging from the opening's top, pointed
    # at the bottom, a small block in front of it
    ring_trigger=(358.5, 173.5, 13.5, 21.0, 4.0),      # the oval's centre and radii (the opening's front end), wall
    trigger=[(405, 151), (408, 161), (411, 169), (412.5, 177), (411, 184), (406.5, 189),
             (409.5, 191), (417, 187.5), (422.5, 180.5), (425, 172), (425.5, 163), (425, 151)],
    trigger_tab=(407.5, 413.0, 171.0, 179.0),
    # the selector on the left: a steel lever from its knurled knob over the rear dimple down to the front
    selector=[(304.3, 159.8), (297.7, 152.2), (272.0, 174.5), (278.5, 182.0)],
    selector_head=[(272.0, 172.0), (281.0, 181.0), (272.0, 190.0), (263.0, 181.0)],   # its square end, set on a corner
    selector_knob=(300.5, 155.5, 5.5),
    grip=[(436, 167), (500, 167), (497, 172), (493, 180), (492, 200), (492, 268), (489, 276), (423, 290), (419, 287),
          (421, 281), (425, 268), (429, 248), (432, 228), (435, 210), (437, 200)],
    # the gas block with the handle's front post on it, the gas tube, the piston rod into the receiver
    gas_block=[(287, 112), (289, 104), (300, 88), (340, 88), (340, 112)],
    gas_tube=(340.0, 492.0, 98.5, 11.5),
    gas_rod=(498.0, 552.0, 98.5, 7.5),
    hook=[(342, 88), (342, 82), (348, 78), (350, 72), (347, 67), (343, 64), (344, 60), (352, 59), (360, 63),
          (365, 72), (366, 82), (366, 88)],
    # the carrying handle: a channel bar with four clips, the front post a fork on the gas block, the rear sight on
    # its back end, the rear strut two plates down to a pin in the lower
    handle=[(313, 30), (315, 25), (319, 23), (512, 23), (512, 45), (316, 45), (313, 40)],
    clips=((384.0, 388.5), (423.0, 427.5), (462.0, 466.5), (501.0, 505.5)),
    handle_pin=(323.0, 33.0, 5.0),
    front_post=[(316, 45), (338, 45), (341, 90), (326, 90), (322, 62)],
    rear_sight=[(512, 26), (515, 20), (521, 14), (529, 11), (538, 11), (545, 14), (549, 20), (549, 46), (512, 46)],
    sight_knob=(541.0, 35.0, 3.5),
    strut=[(535, 45), (549, 45), (549, 167), (522, 152), (519, 143), (522, 134), (530, 126), (531, 112), (533, 75)],
    strut_pin=(530.0, 143.0, 6.5),
    # the upper: the steel receiver box, the polymer cheek cover over it with its long recess, the end cap, the pad
    # its top hidden under the cover's foot; it and the hump start inside the lower's rear end (549): the photo
    # has no gap there (user, 2026-11-25: "why are they separated?")
    receiver=[(544, 112), (800, 112), (800, 167), (544, 167)],
    # the hump behind the strut: a ridge as wide as the cover's flat top, rising out of it (the cover's chamfers run
    # on under it to the front: as a full-width block it stood on the cover like a box)
    hump=[(549, 68), (551, 66), (564, 66), (569, 71), (577, 80), (592, 85.5), (549, 85.5)],
    cover=(549.0, 826.0, 83.5, 110.0, 117.0, 9.5),     # x from, to; top, the chamfer's foot, bottom; top half width
    # the case deflector on the right: a riveted plate with a spout to the front (Kuzmin 2011, A91M.jpg)
    deflector=[(769, 150), (762, 128), (742, 121), (704, 124), (696, 134), (631, 144), (631, 148), (690, 152),
               (700, 160), (742, 163), (764, 160)],
    loop=[(789, 191), (803, 191), (803, 200), (789, 200)],
    loop_hole=[(792, 193.5), (800.5, 193.5), (800.5, 197.5), (792, 197.5)],
    recess=(652.0, 88.0, 762.0, 109.0, 9.5),           # the cheek pad on the cover's chamfer
    cap=[(796, 112), (817, 112), (812, 130), (800, 167), (796, 167)],
    butt=[(829, 79), (852, 80), (858, 88), (858, 105), (853, 165), (847, 232), (842, 243), (835, 246), (812, 246),
          (805, 240), (801, 200), (800, 167), (812, 130), (820, 105)],
    # under the receiver, behind the magazine: the catch's bracket and paddle
    catch=[(686, 167), (776, 167), (776, 186), (748, 188), (703, 199), (700, 207), (694, 206), (690, 190)],
    recv_bottom=167.0,
    catch_front=685.0,
    handle_bar=(319.0, 512.0, 23.0, 45.0),             # the handle's bar between its ends: x, top / bottom y
    muzzle_x=12.0,
    # half widths, mm
    widths=dict(sight=9.0, breech=14.5, lower=16.5, rib=19.3, grip=13.5, block=9.0, handle=8.0, clip=9.3, rec=15.0,
                cover=18.5, hump=9.5, cap=17.0, butt=21.0, catch=6.0, tower=1.3, ear=5.7),
)

GUNS = {"A91M": G7}

# GoM's AK magazines seated as on the Grozas (build_groza.py MAG_SEAT, measured on GoM's AK-47 with its magazine): the
# feed lips 22.7 mm into the receiver, the back edge 28.7 mm behind the lips and 0.5 mm ahead of the magazine catch
AK_SEAT = (22.7, 28.7)
CARRIER_TRAVEL = 100.0             # mm: the piston rod's stroke (7.62x39 AK; the hook rides it)
GOM_RAIL_LEN, GOM_RAIL_BELOW = 0.0756, 0.0011
GOM_SCOPE_FROM_RAIL = (0.0, -0.0066, 0.0039)
AK_CANON_BACK = 0.0282             # GoM's AK-47 canon behind its muzzle, at our 0.603 (the Grozas')


def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(outline), [PL(h) for h in holes], half, bevel, res, mat, x0)


def lathe_y(b, axis_y, prof_px, seg=16, mat="metal"):
    """prof_px: [(photo x, radius px)] along the bore at photo row axis_y."""
    _, z = P(0.0, axis_y)
    b.lathe("y", (0.0, 0.0, z), [(P(x, axis_y)[0], mm(r)) for x, r in prof_px], seg=seg, mat=mat, phase=0.5)


def boss(b, px, py, r_px, x_from, x_to, seg=12, mat="steel"):
    """A round boss along x at photo (px, py), from x_from to x_to (mm, either sign), its outer edge chamfered."""
    y, z = P(px, py)
    r = mm(r_px)
    d = x_to - x_from
    c = 0.5 if d > 0 else -0.5
    b.lathe("x", (x_from, y, z), [(0.0, 0.0), (0.0, r), (d - c, r), (d, r - 0.5), (d, 0.0)], seg=seg, mat=mat)


def pxbox(b, x0, x1, y0, y1, xa, xb, mat="steel", bevel=0.0):
    """A box over photo px x0..x1, y0..y1, across xa..xb mm."""
    ya, za = P(x1, y1)
    yb, zb = P(x0, y0)
    b.box(min(xa, xb), max(xa, xb), ya, yb, za, zb, mat=mat, bevel=bevel)


def build_body(name, g):
    w = g["widths"]
    b = kit.Builder()

    # ---- the muzzle brake on the bore: four ribs and a crown ----
    a, c, r = g["brake"]
    prof = [(c, 0.0), (c, r - 2.6)]
    x = c
    for _ in range(4):
        prof += [(x - 1.5, r), (x - 5.0, r), (x - 6.0, r - 2.6), (x - 8.0, r - 2.6)]
        x -= 8.0
    prof += [(x - 1.5, r), (a + 1.5, r), (a, r - 2.0), (a, 4.5), (a + 10.0, 4.5), (a + 10.0, 0.0)]
    lathe_y(b, BORE, prof, seg=12, mat="steel")

    # ---- the launcher: tube (a real bore), its collars, the breech and the sight housing with its dial ----
    t0, t1, ty, tr = g["tube"]
    lathe_y(b, ty, [(t1, 0.0), (t1, tr), (t0 + 9.0, tr), (t0 + 9.0, tr + 1.8), (t0 + 1.5, tr + 1.8), (t0, tr),
                    (t0, tr - 4.5), (t0 + 34.0, tr - 4.5), (t0 + 34.0, 0.0)], seg=28, mat="poly")
    for ra, rb in g["tube_rings"]:
        lathe_y(b, ty, [(rb, 0.0), (rb, tr + 1.8), (ra, tr + 1.8), (ra, 0.0)], seg=28, mat="poly")
    slab(b, g["tube_lug"], half=3.5, bevel=0.6, mat="steel")
    slab(b, g["breech"], half=w["breech"], bevel=1.6, res=1, mat="steel")
    slab(b, g["sight_base"], [g["sight_window"]], half=w["sight"], bevel=1.2, res=0, mat="steel")
    dx, dy, dr = g["dial"]
    boss(b, dx, dy, dr, w["sight"] - 0.5, w["sight"] + 0.9, seg=16, mat="dark")
    lx0, ly0, lx1, ly1 = g["dial_lever"]
    pxbox(b, lx0, lx1, ly0, ly1, w["sight"] + 0.6, w["sight"] + 3.0, mat="metal", bevel=0.6)
    sx_, sy_, sr_ = g["sight_pin"]
    for sx in (1, -1):
        boss(b, sx_, sy_, sr_, sx * (w["sight"] - 0.3), sx * (w["sight"] + 1.3), seg=8, mat="dark")

    # ---- the rifle's front sight tower: two stamped side plates (leg, brace and hood in one, an oval slot in the
    # hood), the post between them, a cap over the top and the block they stand on ----
    sx0, sy0, sx1, sy1, srr = g["tower_slot"]
    for sx in (1, -1):
        slab(b, g["tower"], [g["tower_window"], rrect(sx0, sy0, sx1, sy1, srr)], half=w["tower"], bevel=0.35,
             mat="steel", x0=sx * (w["ear"] - w["tower"]))
    px0, px1, py0, py1 = g["post"]
    pxbox(b, px0, px1, py0, py1, -0.9, 0.9, mat="dark")
    pxbox(b, 179.0, 196.0, 20.5, 24.5, -w["ear"], w["ear"], mat="steel", bevel=0.5)
    pxbox(b, 177.0, 201.0, 101.0, 113.0, -(w["ear"] + 0.6), w["ear"] + 0.6, mat="steel", bevel=0.8)

    # ---- the lower: casing, handguard and trigger housing, with the raised bars along its lower edge ----
    ox0, oy0, ox1, oy1, orx = g["opening"]
    ocy, ory = (oy0 + oy1) / 2.0, (oy1 - oy0) / 2.0
    hole = [(ox0 + orx + orx * math.cos(math.radians(a)), ocy + ory * math.sin(math.radians(a)))
            for a in range(90, 271, 15)]                                    # the front end: half an oval
    hole += [(ox1 - ory + ory * math.cos(math.radians(a)), ocy + ory * math.sin(math.radians(a)))
             for a in range(-90, 91, 15)]                                   # the rear end: half a circle
    slab(b, g["lower"], [hole], half=w["lower"], bevel=1.8, res=1, mat="poly")
    # its top ledge and front frame stand a little proud
    pxbox(b, 183.0, 549.0, 111.5, 117.5, -(w["lower"] + 0.9), w["lower"] + 0.9, mat="poly", bevel=0.7)
    pxbox(b, 183.0, 196.0, 117.0, 200.0, -(w["lower"] + 0.7), w["lower"] + 0.7, mat="poly", bevel=0.7)
    rb = g["ribs"]
    for i in range(rb["count"]):
        cx = rb["first"] + i * rb["pitch"]
        for sx in (1, -1):
            pxbox(b, cx - rb["w"] / 2, cx + rb["w"] / 2, rb["top"], rb["bottom"], sx * (w["lower"] - 1.5),
                  sx * w["rib"], mat="poly", bevel=1.3)
    # the launcher's trigger: the rear half of that oval, a C whose ends run into the opening's top and bottom
    cx, cy, rx, ry, wall = g["ring_trigger"]
    arc = [(cx + rx * math.cos(math.radians(a)), cy + (ry + 2.0) * math.sin(math.radians(a)))
           for a in range(-100, 101, 10)]
    arc += [(cx + (rx - wall) * math.cos(math.radians(a)), cy + (ry + 2.0 - wall) * math.sin(math.radians(a)))
            for a in range(100, -101, -10)]
    slab(b, arc, half=4.0, bevel=0.5, mat="steel")
    slab(b, g["trigger"], half=3.2, bevel=0.8, mat="dark")
    tx0, tx1, ty0, ty1 = g["trigger_tab"]
    pxbox(b, tx0, tx1, ty0, ty1, -2.0, 2.0, mat="dark", bevel=0.4)
    # the selector's lever and knob, on the left
    slab(b, g["selector"], half=1.3, bevel=0.4, mat="metal", x0=w["lower"] + 1.5)
    slab(b, g["selector_head"], half=1.5, bevel=0.5, mat="metal", x0=w["lower"] + 1.7)
    kx_, ky_, kr_ = g["selector_knob"]
    boss(b, kx_, ky_, kr_, w["lower"] + 0.2, w["lower"] + 6.0, seg=10, mat="dark")
    slab(b, g["grip"], half=w["grip"] + 0.5, bevel=5.0, res=2, mat="poly")

    # ---- gas block, gas tube and piston rod ----
    slab(b, g["gas_block"], half=w["block"], bevel=1.2, mat="steel")
    a, c, ay, ar = g["gas_tube"]
    lathe_y(b, ay, [(c + 6.0, 0.0), (c + 6.0, ar - 4.0), (c, ar), (a, ar), (a, 0.0)], seg=14, mat="steel")
    a, c, ay, ar = g["gas_rod"]
    lathe_y(b, ay, [(c, 0.0), (c, ar), (a - 4.0, ar), (a - 4.0, 0.0)], seg=10, mat="metal")

    # ---- the carrying handle ----
    slab(b, g["handle"], half=w["handle"], bevel=1.0, res=0, mat="steel")
    for ca, cb in g["clips"]:
        pxbox(b, ca, cb, 21.5, 47.0, -w["clip"], w["clip"], mat="steel", bevel=0.5)
    hx, hy, hr = g["handle_pin"]
    for sx in (1, -1):
        boss(b, hx, hy, hr, sx * (w["handle"] - 0.3), sx * (w["handle"] + 1.6), seg=10, mat="dark")
        slab(b, g["front_post"], half=1.4, bevel=0.4, mat="steel", x0=sx * (w["handle"] - 1.4))
    slab(b, g["rear_sight"], half=7.5, bevel=1.2, mat="steel")
    kx, ky, kr = g["sight_knob"]
    for sx in (1, -1):
        boss(b, kx, ky, kr, sx * 7.2, sx * 9.6, seg=8, mat="dark")
    # the rear strut: two plates, outside the lower at the pin, closing in to the handle's width at its top
    _, z_low = P(0.0, 112.0)
    _, z_top = P(0.0, 46.0)
    x_low, x_top = w["lower"] + 1.2, w["handle"] - 0.2
    for sx in (1, -1):
        verts = slab(b, g["strut"], half=1.2, bevel=0.35, mat="steel", x0=0.0)
        for v in verts:
            t = min(max((v.co.z - z_low) / (z_top - z_low), 0.0), 1.0)
            v.co.x += sx * (x_low + (x_top - x_low) * t)
    sx_, sy_, sr_ = g["strut_pin"]
    for sx in (1, -1):
        boss(b, sx_, sy_, sr_, sx * (x_low + 1.0), sx * (x_low + 2.6), seg=12, mat="dark")

    # ---- the upper: receiver box, cheek cover, end cap, butt pad; the magazine catch under it ----
    slab(b, g["receiver"], half=w["rec"], bevel=1.2, mat="steel")
    slab(b, g["hump"], half=w["hump"], bevel=1.4, res=1, mat="poly")
    # the cheek cover: a flat top, a broad chamfer each side (the cheek pads lie on it), a short upright foot
    ca, cb, ct, cf, cbm, ctw = g["cover"]
    cw = w["cover"]
    zt, zf, zb = P(0.0, ct)[1], P(0.0, cf)[1], P(0.0, cbm)[1]
    b.prism("y", [(-cw, zb), (cw, zb), (cw, zf), (ctw, zt), (-ctw, zt), (-cw, zf)], P(cb, 0.0)[0], P(ca, 0.0)[0],
            mat="poly", bevel=0.9)
    slab(b, g["deflector"], half=0.9, bevel=0.3, mat="steel", x0=-(w["rec"] + 0.9))
    slab(b, g["loop"], [g["loop_hole"]], half=1.0, bevel=0.3, mat="steel")
    slab(b, g["cap"], half=w["cap"], bevel=1.5, mat="rubber")
    slab(b, g["butt"], half=w["butt"], bevel=4.0, res=2, mat="rubber")
    slab(b, g["catch"], half=w["catch"], bevel=0.8, mat="steel")
    return b.to_object(name)


def build_bolt(name, g):
    """The charging hook on the piston rod, standing through the gas tube's slot under the carrying handle (the
    field strip's part 3; GunRF: it can be turned to either side)."""
    b = kit.Builder()
    slab(b, g["hook"], half=3.5, bevel=0.9, res=1, mat="dark")
    return b.to_object(name)


def rail_origin(g):
    x0, x1, top, _ = g["handle_bar"]
    y, z = P((x0 + x1) / 2.0, top)
    return (0.0, y * K, (z + 5.0) * K + GOM_RAIL_BELOW)


def build_handle_mount(name, g):
    """GoM's Picatinny_Rail_Up on a plate clamped on the carrying handle's bar (the Grozas' GROZA_RAIL_UP)."""
    x0, x1, top, bot = g["handle_bar"]
    b = kit.Builder()
    ym, zt = P((x0 + x1) / 2.0, top)
    _, zb = P(0.0, bot)
    half_len = GOM_RAIL_LEN / K / 2.0
    hw = g["widths"]["clip"]
    b.box(-hw - 3.0, hw + 3.0, ym - half_len, ym + half_len, zt, zt + 5.0, mat="steel", bevel=0.6)
    for jy in (ym - half_len + 8.0, ym + half_len - 8.0):
        for sx in (1, -1):
            b.box(sx * (hw + 0.4), sx * (hw + 3.0), jy - 8.0, jy + 8.0, zb - 1.0, zt + 0.5, mat="steel", bevel=0.5)
        b.box(-hw - 3.0, hw + 3.0, jy - 8.0, jy + 8.0, zb - 3.5, zb - 1.0, mat="steel", bevel=0.5)
    base = b.to_object(name)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(GOM, "models_X/weapons/parts/rails.fbx"))
    rail = None
    for o in set(bpy.data.objects) - before:
        if o.name.split(".")[0] == "Picatinny_Rail_Up" and rail is None:
            rail = o
        else:
            bpy.data.objects.remove(o)
    ox, oy, oz = rail_origin(g)
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


# ==================================================================================================
# Texture (GoM's way, as the Grozas: dark steel with worn edges, black polymer), details at the photo's places
# ==================================================================================================

# the real gun is black all over (painted steel, black polymer): the materials differ in sheen more than in tone
BASE = {"steel": (60, 61, 65), "poly": (52, 52, 55), "dark": (30, 30, 32), "rubber": (66, 66, 68), "metal": (112, 113, 117),
        "bright": (150, 152, 156)}


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "dark", "bright")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.88 + 0.24 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.90 + 0.20 * streak[is_metal])[..., None]
    col *= (0.92 + 0.30 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.60 + 0.40 * np.clip(ao_b, 0, 1) ** 1.5) * (0.64 + 0.36 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 140.0, 62.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def rr_mask(X, Y, x0, y0, x1, y1, r):
    """Signed distance (px, negative inside) to a rounded rectangle."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    qx = np.abs(X - cx) - ((x1 - x0) / 2.0 - r)
    qy = np.abs(Y - cy) - ((y1 - y0) / 2.0 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def screw(col, sel, X, Y, cx, cy, r, head=112.0):
    """A screw head: a dark ring, a lighter head, a slot."""
    d = np.hypot(X - cx, Y - cy)
    col[sel & (d < r + 1.2)] *= 0.45
    col[sel & (d < r)] = head
    col[sel & (d < r) & (np.abs(Y - cy) < 0.6)] = 30


def paint(maps, kind, g=None):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body" and g is not None:
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        X, Y = ORIGIN[0] - y * S, ORIGIN[1] - z * S         # back to photo px
        side = np.abs(n[..., 0]) > 0.7
        left = n[..., 0] > 0.7
        right = n[..., 0] < -0.7
        is_ = lambda m: mat == MATS.index(m)
        poly, steel, rubber = is_("poly"), is_("steel"), is_("rubber")
        w = g["widths"]

        # -- the lower: its ledge and front frame, screws, the pin, the two dimples, the selector (left) --
        low = poly & side & (X > 183) & (X < 549) & (Y > 112) & (Y < 200) & (np.abs(x) > w["lower"] - 0.5)
        col[low & (Y < 117.5)] *= 1.15
        col[low & (np.abs(Y - 118.2) < 0.6)] *= 0.55
        col[low & (X < 196.0)] *= 1.1
        col[low & (np.abs(X - 196.8) < 0.6) & (Y > 118)] *= 0.55
        screw(col, low, X, Y, 247.0, 138.0, 3.0)
        screw(col, low, X, Y, 343.0, 138.0, 2.6)
        d = np.hypot(X - 428.0, Y - 140.0)
        col[low & (d < 5.5)] *= 0.4
        col[low & (d < 3.6)] = 120
        col[low & (d < 1.6)] = 25
        for cx, cy, rx, ry in ((237.0, 162.0, 9.0, 10.0), (311.0, 163.0, 9.0, 10.0)):
            d = np.hypot((X - cx) / rx, (Y - cy) / ry)
            m = low & (d < 1.0) & (Y > cy - 0.25 * ry)                        # a scoop: flat along its top
            depth = np.clip(1.0 - (Y - (cy - 0.25 * ry)) / (1.25 * ry), 0, 1)  # deepest under the flat edge
            col[m] *= (0.38 + 0.75 * (1.0 - depth[m]))[..., None]
            col[low & (d >= 1.0) & (d < 1.18) & (Y > cy + 0.3 * ry)] *= 1.5
        rb = g["ribs"]
        band = (Y > rb["top"]) & (Y < rb["bottom"]) & (X > rb["first"] - rb["w"]) & \
            (X < rb["first"] + rb["pitch"] * (rb["count"] - 1) + rb["w"])
        col[poly & side & band & (np.abs(x) > w["rib"] - 0.4)] *= 1.35
        col[low & band & (np.abs(x) < w["lower"] + 0.3)] *= 0.72
        lft = low & left
        col[lft & (np.hypot(X - 264.0, Y - 166.0) < 1.6)] = 190              # the selector's white dot
        # the grip's grooves
        gx = [q[0] for q in g["grip"]]
        grip = poly & side & (X > 448) & (X < max(gx) - 3) & (Y > 198) & (Y < 272)
        col[grip & (np.mod(Y, 5.2) < 2.0)] *= 0.5
        col[grip & (np.mod(Y, 5.2) > 2.0) & (np.mod(Y, 5.2) < 3.0)] *= 1.45

        # -- the cheek pads on the cover's chamfers: lighter rubber, a soft rim, a small tab under the middle --
        x0, y0, x1, y1, rr = g["recess"]
        dcv = rr_mask(X, Y, x0, y0, x1, y1, rr)
        cov = poly & (X > 590) & (X < 826) & (Y > 84) & (Y < 111) & (np.abs(n[..., 0]) > 0.35) & (n[..., 2] > 0.2)
        tab = (np.abs(X - (x0 + x1) / 2.0) < 7.0) & (Y >= y1 - 1.0) & (Y < y1 + 3.5)
        pad = cov & ((dcv < 0) | tab)
        col[pad] = 68
        col[cov & (dcv >= 0) & (dcv < 1.3) & ~tab] *= 0.6
        col[pad & (dcv > -1.6)] *= 0.85

        # -- the receiver box: screws and rivets; on the right the deflector's rivets and the fire marks --
        rec = steel & side & (X > 553) & (X < 800) & (Y > 117) & (Y < 167)
        screw(col, rec, X, Y, 674.0, 146.0, 2.8)
        screw(col, rec, X, Y, 759.0, 148.0, 2.8)
        for cx, cy in ((700.0, 162.0), (751.0, 163.0)):
            col[rec & (np.hypot(X - cx, Y - cy) < 2.0)] = 150
        plate = steel & right & (np.abs(x) > w["rec"] + 1.2)
        for cx, cy in ((756.0, 140.0), (742.0, 128.0), (712.0, 130.0), (738.0, 156.0)):
            dd_ = np.hypot(X - cx, Y - cy)
            col[plate & (dd_ < 3.0)] *= 0.5
            col[plate & (dd_ < 1.9)] = 120
        recr = rec & right & (np.abs(x) < w["rec"] + 0.5)
        cross = (np.abs((X - 622.0) - (Y - 126.0)) < 0.7) | (np.abs((X - 622.0) + (Y - 126.0)) < 0.7)
        col[recr & cross & (np.hypot(X - 622.0, Y - 126.0) < 3.5)] = 200
        for cx, cy in ((619.0, 140.0), (613.5, 152.0), (618.0, 152.0), (622.5, 152.0)):
            col[recr & (np.hypot(X - cx, Y - cy) < 1.5)] = (190, 40, 34)
        col[recr & (np.abs((X - 643.0) + (Y - 133.0) * 0.3) < 0.8) & (Y > 124) & (Y < 142)] = 12

        # -- the butt pad: grooves across its back, a rim line and two dimples on its sides --
        back = rubber & (n[..., 1] < -0.6)
        col[back & (np.mod(Y, 8.0) < 2.4)] *= 0.6
        pside = rubber & side
        col[pside & (np.abs(X - (853.0 - (Y - 90.0) * 0.068)) < 0.7) & (Y > 90) & (Y < 236)] *= 0.62
        for cx, cy in ((838.0, 96.0), (832.0, 120.0)):
            dd_ = np.hypot(X - cx, Y - cy)
            col[pside & (dd_ < 3.0)] *= 0.55
        # -- the launcher: its tube's long raised panel, the bores, the sight housing's notch --
        t0, t1, ty, tr = g["tube"]
        tube = poly & (X > t0 + 12) & (X < 148) & (np.abs(n[..., 0]) > 0.55)
        dt = rr_mask(X, Y, 62.0, 156.0, 128.0, 172.0, 6.0)
        col[tube & (np.abs(dt) < 1.1)] *= 1.5
        col[tube & (dt < -1.1)] *= 1.12
        rad = np.hypot(x, (Y - ty) / S)
        col[(X < t0 + 36.0) & (rad < (tr - 4.0) / S) & (np.abs(Y - ty) < tr) & (n[..., 1] > 0.5)] = 5
        col[poly & (X < t0 + 34.5) & (rad < (tr - 3.5) / S) & (np.abs(n[..., 1]) < 0.5)] *= 0.35
        rad = np.hypot(x, (Y - BORE) / S)
        col[steel & (X < g["muzzle_x"] + 11.0) & (rad < 4.8 / S) & (np.abs(Y - BORE) < 6)] = 5
        hs = steel & side & (np.abs(x) < w["sight"] + 0.6)
        col[hs & (rr_mask(X, Y, 70.0, 100.5, 86.0, 107.0, 1.5) < 0)] = 12
        # -- the carrying handle: the open channel on top, the slot at its front --
        hb = steel & (X > 345) & (X < 508) & (Y < 26) & (n[..., 2] > 0.7)
        col[hb & (np.abs(x) < 4.8)] *= 0.45
        hsd = steel & side & (Y > 23) & (Y < 45) & (np.abs(x) > w["handle"] - 0.5)
        col[hsd & (rr_mask(X, Y, 336.0, 27.0, 357.0, 38.5, 2.0) < 0)] = 11
        col[hsd & (np.abs(rr_mask(X, Y, 336.0, 27.0, 357.0, 38.5, 2.0) - 0.8) < 0.6)] *= 1.3
        col[hsd & (X > 345) & (X < 510) & (np.abs(Y - 40.0) < 0.6)] *= 0.6
        # -- the gas tube's slot for the hook, the rear sight's aperture face --
        gt = steel & (X > 345) & (X < 488) & (n[..., 2] > 0.75) & (np.abs(Y - 87.5) < 3)
        col[gt & (np.abs(x) < 2.6)] = 10
        # -- the front sight's ears: lighter worn rims are common()'s; the housing's dial: its marks --
        dd = np.hypot(X - g["dial"][0], Y - g["dial"][1])
        dial = (mat == MATS.index("dark")) & left & (dd < g["dial"][2]) & (X < 180)
        ang = np.arctan2(Y - g["dial"][1], X - g["dial"][0])
        col[dial] = 14
        col[dial & (dd > g["dial"][2] - 1.6)] = 60
        # the gas block's two grooves, the catch bracket's slot, the strut pin's clip
        gb = steel & side & (Y > 88) & (Y < 112) & (X > 300) & (X < 340) & (np.abs(x) > w["block"] - 0.5)
        for gx_ in (306.0, 323.0):
            col[gb & (np.abs(X - gx_) < 1.0)] *= 0.5
            col[gb & (np.abs(X - gx_ - 1.6) < 0.6)] *= 1.3
        ct = steel & side & (Y > 168) & (X > 686) & (X < 776) & (np.abs(x) < w["catch"] + 0.5)
        col[ct] *= 1.5
        col[ct & (X > 749)] *= 0.45
        col[ct & (rr_mask(X, Y, 706.0, 174.0, 742.0, 177.5, 1.5) < 0)] *= 0.45
        col[ct & (np.hypot(X - 697.0, Y - 180.0) < 2.2)] = 95
        dpn = np.hypot(X - g["strut_pin"][0], Y - g["strut_pin"][1])
        pin = (mat == MATS.index("dark")) & side & (dpn < g["strut_pin"][2]) & (X > 515) & (X < 545) & (Y > 130)
        col[pin & (dpn > 2.4) & (dpn < 4.3) & ~((np.abs(Y - g["strut_pin"][1]) < 1.2) & (X > g["strut_pin"][0]))] = 135
    col = common(maps, col, mat)
    if kind == "body" and g is not None:
        # the round parts' sheen (the launcher tube, the gas tube, the brake): a band of light along their upper side
        x, z = p[..., 0], p[..., 2]
        Xp, Yp = ORIGIN[0] - p[..., 1] * S, ORIGIN[1] - z * S
        t0, t1, ty, tr = g["tube"]
        ga, gc, gy, gr = g["gas_tube"]
        ba, bc, br_ = g["brake"]
        for sel in ((Xp < t1 + 1) & (Xp > t0 + 1) & (np.abs(np.hypot(x, (Yp - ty) / S) - tr / S) < 2.2),
                    (Xp < gc + 1) & (Xp > ga) & (np.abs(np.hypot(x, (Yp - gy) / S) - gr / S) < 1.0),
                    (Xp < bc) & (Xp > ba) & (np.abs(np.hypot(x, (Yp - BORE) / S) - br_ / S) < 1.0)):
            sel = sel & (np.abs(n[..., 1]) < 0.5)
            nz = n[..., 2][sel]
            col[sel] *= (0.80 + 0.25 * np.clip(nz, -1, 1))[..., None]
            col[sel] += (30.0 * np.exp(-((nz - 0.55) / 0.17) ** 2))[..., None]
    return np.clip(col, 0, 255)


def bake(ob, ctx, size):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    return kit.bake_maps(ob, ctx, bake_size)


def texture(maps_list, kinds, gs, size, path):
    bake_size = max(size * 4, kit.BAKE // (256 // size) if size < 256 else kit.BAKE)
    col = np.zeros((bake_size, bake_size, 3), np.float32)
    cover = np.zeros((bake_size, bake_size), bool)
    for maps, kind, g in zip(maps_list, kinds, gs):
        c = paint(maps, kind, g)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = kit.dilate(col, cover, 4 * (bake_size // size))
    kit.save_png(col, size, path)


# ==================================================================================================
# Points
# ==================================================================================================

def gp(x, y, xoff=0.0):
    yy, zz = P(x, y)
    return [round(xoff * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


def points(gun, g):
    muzzle = gp(g["muzzle_x"], BORE)
    ins, rear = AK_SEAT
    lips_x = g["catch_front"] - (0.5 + rear) * S
    lips_y = g["recv_bottom"] - ins * S
    magazine = gp(lips_x, lips_y)
    canon = [muzzle[0], round(muzzle[1] - AK_CANON_BACK, 4), muzzle[2]]
    t0, _, ty, _ = g["tube"]
    ro = rail_origin(g)
    return {
        "muzzle": {"offset": muzzle, "rotate": [-90.0, 0.0, -180.0]},
        "muzzle_gl": {"offset": gp(t0, ty), "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": canon, "rotate": ZERO},
        "magazine": {"offset": magazine, "rotate": ZERO},
        "bolt_fired": {"offset": [0.0, round(-CARRIER_TRAVEL * K, 4), 0.0], "rotate": ZERO},
        "rail_up": {"offset": [0.0, 0.0, 0.0], "rotate": ZERO},
        "scope": {"offset": [round(c + d, 4) + 0.0 for c, d in zip(ro, GOM_SCOPE_FROM_RAIL)], "rotate": ZERO},
        "world": {"offset": [round(0.02 * K / K_OLD, 4), round(0.13 * K / K_OLD, 4), 0.0], "rotate": [180.0, 0.0, 180.0]},
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
    bodies, bolts, mounts = [], [], []
    for gun, g in GUNS.items():
        bodies.append(build_body(gun + "_BODY", g))
        bolts.append(build_bolt(gun + "_BOLT", g))
        mounts.append(build_handle_mount(gun + "_RAIL_UP", g))
    kit.unwrap(bodies + bolts + mounts, 0.003)
    gs = list(GUNS.values())
    maps = [bake(o, [o, bl], 512) for o, bl in zip(bodies, bolts)]
    maps += [bake(bl, [o, bl], 512) for o, bl in zip(bodies, bolts)]
    maps += [bake(m, [m, o], 512) for m, o in zip(mounts, bodies)]
    n = len(gs)
    texture(maps, ["body"] * n + ["bolt"] * n + ["mount"] * n, gs * 3, 512, os.path.join(TEX_DIR, "A91M.png"))
    bounds = {o.name: kit.bounds_of(o) for o in bodies + bolts + mounts}
    out = {gun: points(gun, g) for gun, g in GUNS.items()}
    out["_bounds"] = bounds
    out["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the grip's rear top",
        "magazine": "GoM's AK magazines' feed lips (the Grozas' seat)",
        "muzzle_gl": "the launcher tube's bore at its front: the launcher weapon's muzzle",
        "canon": "GoM's AK mount (0.0282 behind the muzzle, the Grozas')",
        "bolt_fired": "the charging hook back %.0f mm (GoM's AK swap)" % CARRIER_TRAVEL,
    }
    with open(POINTS_JSON, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    kit.export(bodies + bolts + mounts, FBX_GUN)
    for name, bd in bounds.items():
        print("%-20s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
