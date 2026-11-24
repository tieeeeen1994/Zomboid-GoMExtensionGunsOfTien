"""KBP A-91M (7.62x39) and 5.56A-91 (5.56x45) bullpups with their integral 40 mm launcher, for Guns of Tien - Post-93
(Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_a91m.py -- [--size 1024]

Writes (M = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    M/models_X/weapons/firearms/GunsOfTienPost93_A91M.fbx    A91M_BODY (7.62 mm A-91M), A91M556_BODY (5.56A-91), each
                                                            with its launcher under the barrel; A91M_BOLT /
                                                            A91M556_BOLT (the charging handle on the right, on the gas
                                                            piston rod: GoM's AK swap draws it back on each shot);
                                                            A91M_RAIL_UP / A91M556_RAIL_UP (GoM's Picatinny rail on our
                                                            clamp on the carrying handle, the Grozas' way)
    M/models_X/weapons/magazines/GunsOfTienPost93_A91M_magazines.fbx   556x45Magazine30_A91M
    M/textures/weapons/GunsOfTienPost93/A91M.png             512 atlas (both bodies, bolts and mounts)
    M/textures/weapons/GunsOfTienPost93/556x45Magazine30_A91M.png 128
    scripts/post93/a91m_points.json                          attachment points (game space), both guns

User, 2026-11-25 (docs/post93_design.md "KBP A-91M and 5.56A-91"): the bullpup with the 40 mm launcher is the A-91M of
1998 (Post-93). References in references/a91 (SOURCES.txt):
- A-91M: GunRF's A91M2.jpg (880 px, studio right side, muzzle left) at 1.294 px a mm (660 mm, brake tip x 9 to the
  butt's back x 863). Profiles in its pixels (x rearward, y down), read from per-column foreground runs (the photo's
  dark gun on white) and 3-10x gridded crops: the slotted brake x 10-48 on the bore (y 125.5), the front sight block
  with its ring hood, the launcher's leaf standing over it, the launcher tube x 42-188 (axis y 172.5), the casing that
  is the lower receiver and handguard (GunRF's field strip: launcher, grip and triggers are one lower), the guard
  opening with the launcher's ring trigger in front and the rifle's crescent blade behind (10x crop), the gas tube,
  the carrying handle and its diopter, the stock body and rubber butt, the AK magazine catch.
- 5.56A-91: Commons' KBP_A_91_noBG.png (1300 px, right side, transparent background) at 1.693 px a mm (670 mm, x 89 to
  1223), read the same way on its alpha mask: the flash hider, the taller front block, the flat-topped handle, its own
  straight polymer magazine (modelled), the lower housing behind the magazine.
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
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_A91M_magazines.fbx")
POINTS_JSON = os.path.join(HERE, "a91m_points.json")
MAG_NAME = "556x45Magazine30_A91M"
GOM = kit.GOM if hasattr(kit, "GOM") else next(
    (p for p in ("C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media",)
     if os.path.isdir(p)), None)

K = 0.000603
K_OLD = 0.00065
kit.K = K
MATS = ["steel", "poly", "dark", "rubber", "metal", "bright"]
kit.MATS[:] = MATS
ZERO = [0.0, 0.0, 0.0]

# ==================================================================================================
# Photo frames: px -> game (y forward, z up) mm, origin at the grip's rear top
# ==================================================================================================

FRAMES = {
    "7": dict(s=1.294, origin=(495.0, 168.0), bore=125.5),
    "5": dict(s=1.693, origin=(718.0, 288.0), bore=221.0),
}


def P(f, x, y):
    fr = FRAMES[f]
    ox, oy = fr["origin"]
    return (ox - x) / fr["s"], (oy - y) / fr["s"]


def PL(f, pts):
    return [P(f, x, y) for x, y in pts]


def mm(f, px):
    return px / FRAMES[f]["s"]


def ellipse(cx, cy, rx, ry, n=24):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rrect(x0, y0, x1, y1, r, n=5):
    """A rounded rectangle in photo px (y down), counter-clockwise on screen."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def crescent(front, thick):
    """A trigger blade: its front edge (top to bottom, photo px) and the same line `thick` px further back."""
    back = [(x + thick, y) for x, y in reversed(front)]
    return front + back


# ==================================================================================================
# Profiles: A-91M (GunRF A91M2.jpg px)
# ==================================================================================================

G7 = dict(
    frame="7",
    brake=(10.0, 48.0, 12.5),                          # x from, to, radius px (19 mm across, slotted)
    front_block=[(47, 88), (52, 83), (140, 83), (147, 76), (158, 68), (170, 67), (179, 71), (182, 80), (186, 104),
                 (188, 142), (47, 142)],
    sight_ring=(160.0, 97.0, 13.0),                    # the front sight's ring hood (painted)
    leaf=[(178, 104), (178, 26), (181, 21), (187, 19), (193, 21), (197, 27), (197, 104)],
    leaf_window=[(182, 56), (193, 56), (193, 96), (182, 96)],
    strut=[(189, 50), (193, 49), (215, 105), (211, 107)],
    tube=(42.0, 188.0, 172.5, 30.0),                   # x front, rear, axis y, radius px (45 mm across)
    tube_rings=((148.0, 156.0), (176.0, 186.0)),
    lower=[(186, 104), (200, 104), (214, 112), (505, 112), (505, 168), (436, 168), (436, 196), (432, 201),
           (345, 202), (300, 203), (186, 203)],
    opening=(345.0, 152.0, 433.0, 194.0, 12.0),       # the guard's opening: x0, y0, x1, y1, corner r (px)
    ring_trigger=(359.0, 173.5, 12.0, 18.5, 2.6),      # the launcher's ring: centre, radii, wall (px)
    trigger=[(405, 154), (407, 162), (409.5, 170), (409, 180), (406, 188), (403, 191)],
    trigger_thick=3.0,
    gas_tube=(287.0, 505.0, 98.5, 11.5),               # x from, to, axis y, radius px
    handle=[(312, 30), (316, 24), (322, 23), (522, 23), (526, 16), (534, 12), (544, 14), (550, 22), (550, 45),
            (316, 45), (312, 40)],
    front_post=[(318, 45), (337, 45), (341, 88), (323, 88)],
    rear_post=[(527, 45), (548, 45), (548, 112), (530, 112)],
    diopter=[(343, 88), (343, 66), (348, 59), (356, 57), (364, 61), (367, 70), (366, 88)],
    receiver=[(505, 112), (548, 112), (548, 64), (556, 64), (572, 76), (590, 84), (800, 84), (800, 108), (796, 130),
              (790, 150), (785, 167), (505, 167)],
    grip=[(436, 168), (500, 168), (497, 172), (493, 178), (492, 200), (492, 270), (489, 276), (423, 289), (420, 286),
          (424, 272), (428, 250), (431, 230), (432, 210), (434, 196)],
    butt=[(800, 84), (822, 80), (845, 80), (855, 88), (857, 110), (853, 160), (850, 200), (847, 238), (840, 247),
          (812, 247), (805, 240), (796, 210), (789, 185), (785, 167), (790, 150), (796, 130), (800, 108)],
    under=[[(685, 167), (689, 190), (692, 205), (700, 207), (703, 196), (701, 167)],          # the AK magazine catch
           [(758, 167), (776, 167), (776, 186), (760, 186)],                                 # the rear lug
           [(703, 196), (746, 186), (747, 189.5), (704, 200)]],                              # the catch's rod
    recv_bottom=167.0,
    catch_front=685.0,
    handle_knob=(380.0, 100.0),                        # the charging handle on the rod (px), right side
    handle_bar=(322.0, 522.0, 23.0, 45.0),             # the carrying handle's bar between its posts: x, top / bottom y
    muzzle_x=10.0,
    hand_x0=200.0, hand_x1=345.0,                      # the casing's ribbed stretch (painted)
    widths=dict(rec=15.0, lower=16.5, block=13.0, handle=6.0, post=6.5, grip=13.0, butt=19.0, under=5.0),
)

# ==================================================================================================
# Profiles: 5.56A-91 (Commons KBP_A_91_noBG.png px)
# ==================================================================================================

G5 = dict(
    frame="5",
    brake=(85.0, 127.0, 17.0),                         # the flash hider
    front_block=[(127, 205), (130, 166), (140, 163), (200, 160), (240, 155), (250, 151), (260, 145), (270, 138),
                 (280, 135), (290, 139), (300, 148), (302, 244), (127, 244)],
    sight_ring=(268.0, 170.0, 20.0),
    leaf=[(301, 198), (301, 91), (305, 85), (313, 83), (319, 85), (322, 91), (322, 198)],
    leaf_window=[(305, 118), (318, 118), (318, 175), (305, 175)],
    strut=[(316, 120), (320, 118), (342, 195), (338, 198)],
    tube=(117.0, 302.0, 282.5, 40.0),
    tube_rings=((262.0, 272.0), (288.0, 300.0)),
    lower=[(300, 198), (445, 198), (448, 171), (500, 166), (545, 170), (548, 186), (720, 186), (720, 290),
           (640, 318), (632, 323), (300, 323)],
    opening=(506.0, 255.0, 629.0, 309.0, 18.0),
    ring_trigger=(532.0, 283.5, 18.0, 23.5, 3.2),
    trigger=[(592, 258), (596, 270), (600, 284), (598, 295), (594, 303)],
    trigger_thick=7.0,
    gas_tube=(545.0, 770.0, 176.5, 2.2),               # the bright gas piston rod over the body
    handle=[(500, 104), (510, 98), (520, 89), (770, 88), (790, 88), (790, 129), (505, 129), (500, 121)],
    front_post=[(506, 129), (545, 129), (548, 186), (515, 172)],
    rear_post=[(768, 129), (790, 129), (790, 190), (768, 190)],
    diopter=[(520, 129), (520, 140), (524, 150), (532, 154), (540, 150), (544, 140), (544, 129)],
    receiver=[(720, 186), (768, 186), (768, 129), (788, 108), (800, 102), (810, 107), (822, 130), (835, 150),
              (848, 163), (1150, 168), (1135, 240), (1126, 288), (1090, 290), (1085, 308), (1020, 311), (1012, 318),
              (1008, 345), (1000, 355), (975, 357), (963, 350), (963, 287), (858, 284), (720, 290)],
    grip=[(722, 288), (718, 300), (715, 350), (713, 400), (712, 431), (700, 434), (612, 446), (607, 440), (612, 430),
          (620, 405), (628, 370), (632, 335), (630, 318), (640, 300)],
    butt=[(1150, 170), (1180, 163), (1205, 163), (1218, 170), (1222, 190), (1220, 260), (1217, 330), (1212, 375),
          (1200, 393), (1165, 393), (1150, 386), (1140, 367), (1130, 330), (1126, 290), (1135, 240), (1145, 200)],
    under=[],
    recv_bottom=286.0,
    catch_front=963.0,
    handle_knob=(600.0, 180.0),
    handle_bar=(545.0, 768.0, 88.0, 129.0),
    muzzle_x=85.0,
    hand_x0=320.0, hand_x1=500.0,
    mag=[(860, 267), (962, 267), (963, 287), (962, 330), (958, 365), (950, 400), (940, 441), (930, 476), (920, 506),
         (910, 534), (902, 578), (892, 586), (880, 583), (850, 570), (820, 557), (800, 549), (783, 540), (780, 532),
         (790, 514), (800, 492), (810, 466), (820, 435), (830, 402), (840, 364), (850, 315), (858, 284)],
    widths=dict(rec=15.5, lower=16.5, block=14.0, handle=7.0, post=7.0, grip=13.5, butt=19.0, under=5.0, mag=12.5),
)

GUNS = {"A91M": G7, "A91M556": G5}

# GoM's AK magazines seated as on the Grozas (build_groza.py MAG_SEAT, measured on GoM's AK-47 with its magazine): the
# feed lips 22.7 mm into the receiver, the back edge 28.7 mm behind the lips and 0.5 mm ahead of the magazine catch
AK_SEAT = (22.7, 28.7)
CARRIER_TRAVEL = 100.0             # mm: the piston rod's stroke (7.62x39 AK; the handle rides it)
GOM_RAIL_LEN, GOM_RAIL_BELOW = 0.0756, 0.0011
GOM_SCOPE_FROM_RAIL = (0.0, -0.0066, 0.0039)
AK_CANON_BACK = 0.0282             # GoM's AK-47 canon behind its muzzle, at our 0.603 (the Grozas')
AR_CANON_BACK = 28.8               # mm: GoM's M4A1 (the SCAR-L's)
GOM_STANAG_PROP2 = ([0.0200, 0.0538, -0.0146], [-94.9600, 23.4300, -89.8200])


def slab(b, f, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="steel", x0=0.0):
    return kit.slab(b, PL(f, outline), [PL(f, h) for h in holes], half, bevel, res, mat, x0)


def lathe_y(b, f, axis_y, prof_px, seg=16, mat="metal"):
    """prof_px: [(photo x, radius px)] along the bore at photo row axis_y."""
    _, z = P(f, 0.0, axis_y)
    b.lathe("y", (0.0, 0.0, z), [(P(f, x, axis_y)[0], mm(f, r)) for x, r in prof_px], seg=seg, mat=mat, phase=0.5)


def build_body(name, g):
    f, w = g["frame"], g["widths"]
    b = kit.Builder()
    bore = FRAMES[f]["bore"]
    # the muzzle device on the bore
    a, c, r = g["brake"]
    lathe_y(b, f, bore, [(c, 0.0), (c, r - 1.0), (c - 2.0, r), (a + 2.0, r), (a, r - 2.0), (a, 0.0)], seg=16,
            mat="steel")
    slab(b, f, g["front_block"], half=w["block"], bevel=1.5, res=1, mat="steel")
    slab(b, f, g["leaf"], [g["leaf_window"]], half=1.6, bevel=0.4, mat="steel", x0=0.0)
    slab(b, f, g["strut"], half=1.2, bevel=0.3, mat="steel", x0=0.0)
    # the launcher's tube: a rounded front lip round its 40 mm bore, its collar rings
    t0, t1, ty, tr = g["tube"]
    lathe_y(b, f, ty, [(t1, 0.0), (t1, tr), (t0 + 6.0, tr), (t0 + 2.0, tr - 2.5), (t0, tr - 6.0), (t0, 0.0)], seg=32,
            mat="poly")
    for ra, rb in g["tube_rings"]:
        lathe_y(b, f, ty, [(rb, 0.0), (rb, tr + 1.5), (ra, tr + 1.5), (ra, 0.0)], seg=32, mat="steel")
    # the lower: the launcher's casing, the handguard and the trigger housing, its guard opening
    ox0, oy0, ox1, oy1, rr = g["opening"]
    slab(b, f, g["lower"], [rrect(ox0, oy0, ox1, oy1, rr)], half=w["lower"], bevel=2.0, res=1, mat="poly")
    cx, cy, rx, ry, wall = g["ring_trigger"]
    slab(b, f, ellipse(cx, cy, rx, ry), [ellipse(cx, cy, rx - wall, ry - wall)], half=2.5, bevel=0.5, mat="dark")
    slab(b, f, crescent(g["trigger"], g["trigger_thick"]), half=2.5, bevel=0.5, mat="dark")
    # the gas tube (A-91M) or the bright piston rod (5.56A-91) under the carrying handle
    a, c, ay, ar = g["gas_tube"]
    lathe_y(b, f, ay, [(c, 0.0), (c, ar), (a + 4.0, ar), (a, ar * 0.6), (a, 0.0)],
            seg=14, mat="bright" if f == "5" else "steel")
    slab(b, f, g["handle"], half=w["handle"], bevel=1.2, res=1, mat="steel")
    slab(b, f, g["front_post"], half=w["post"], bevel=1.0, mat="steel")
    slab(b, f, g["rear_post"], half=w["post"] + 3.0, bevel=1.0, mat="steel")
    slab(b, f, g["diopter"], half=6.0, bevel=0.8, mat="dark")
    slab(b, f, g["receiver"], half=w["rec"], bevel=1.6, res=1, mat="poly")
    slab(b, f, g["grip"], half=w["grip"], bevel=3.0, res=1, mat="poly")
    slab(b, f, g["butt"], half=w["butt"], bevel=2.5, res=1, mat="rubber")
    for part in g["under"]:
        slab(b, f, part, half=w["under"], bevel=0.6, mat="steel")
    return b.to_object(name)


def build_bolt(name, g):
    """The charging handle on the right of the piston rod (GunRF: either side; the photos show it right)."""
    f = g["frame"]
    b = kit.Builder()
    kx, ky = g["handle_knob"]
    y, z = P(f, kx, ky)
    xr = -(g["widths"]["rec"] + 2.0)
    b.box(xr, xr - 9.0, y - 5.0, y + 5.0, z - 3.5, z + 3.5, mat="steel", bevel=0.8)
    b.lathe("x", (xr - 9.0, y, z), [(0.0, 0.0), (0.0, 5.0), (-7.0, 5.0), (-8.0, 3.5), (-8.0, 0.0)], seg=12,
            mat="steel")
    return b.to_object(name)


def rail_origin(g):
    f = g["frame"]
    x0, x1, top, _ = g["handle_bar"]
    y, z = P(f, (x0 + x1) / 2.0, top)
    return (0.0, y * K, (z + 5.0) * K + GOM_RAIL_BELOW)


def build_handle_mount(name, g):
    """GoM's Picatinny_Rail_Up on a plate clamped on the carrying handle's bar (the Grozas' GROZA_RAIL_UP)."""
    f = g["frame"]
    x0, x1, top, bot = g["handle_bar"]
    b = kit.Builder()
    ym, zt = P(f, (x0 + x1) / 2.0, top)
    _, zb = P(f, 0.0, bot)
    half_len = GOM_RAIL_LEN / K / 2.0
    hw = g["widths"]["handle"]
    b.box(-hw - 4.0, hw + 4.0, ym - half_len, ym + half_len, zt, zt + 5.0, mat="steel", bevel=0.6)
    for jy in (ym - half_len + 8.0, ym + half_len - 8.0):
        for sx in (1, -1):
            b.box(sx * (hw + 0.5), sx * (hw + 4.0), jy - 8.0, jy + 8.0, zb - 1.0, zt + 0.5, mat="steel", bevel=0.5)
        b.box(-hw - 4.0, hw + 4.0, jy - 8.0, jy + 8.0, zb - 3.5, zb - 1.0, mat="steel", bevel=0.5)
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


def build_magazine(g):
    """The 5.56A-91's own 30-round polymer magazine, from the photo; origin at the feed lips' front (GoM's way), drawn
    at the gun's `magazine` point. Its floor plate, its ribbed rear spine painted."""
    f = g["frame"]
    b = kit.Builder()
    lx, ly = g["mag"][0]
    oy, oz = P(f, lx, ly)

    def M(pts):
        return [(P(f, x, y)[0] - oy, P(f, x, y)[1] - oz) for x, y in pts]

    kit.slab(b, M(g["mag"]), (), g["widths"]["mag"], 1.5, 1, "poly", 0.0)
    floor = [(781, 528), (792, 512), (902, 575), (896, 590), (886, 590)]
    kit.slab(b, M(floor), (), g["widths"]["mag"] + 1.0, 0.8, 0, "poly", 0.0)
    return b.to_object(MAG_NAME)


# ==================================================================================================
# Texture (GoM's way, as the Grozas: dark steel with worn edges, black polymer)
# ==================================================================================================

BASE = {"steel": (40, 41, 44), "poly": (30, 30, 32), "dark": (17, 17, 18), "rubber": (26, 26, 27), "metal": (46, 47, 50),
        "bright": (150, 152, 156)}


def common(maps, col, mat):
    p, n = maps["pos"], maps["nrm"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    is_metal = np.isin(mat, [MATS.index(m) for m in ("steel", "metal", "dark", "bright")])
    mott = kit.vnoise(p, 6.0, 1) * 0.6 + kit.vnoise(p, 1.6, 2) * 0.4
    col *= (0.88 + 0.24 * mott)[..., None]
    streak = kit.vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.82 + 0.36 * streak[is_metal])[..., None]
    col *= (0.96 + 0.12 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.62 + 0.38 * np.clip(ao_b, 0, 1) ** 1.5) * (0.66 + 0.34 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 110.0, 45.0) * (0.7 + 0.6 * kit.vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.32 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    return col


def paint(maps, kind, g=None):
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    col = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        col[mat == i] = BASE[name]
    if kind == "body" and g is not None:
        f = g["frame"]
        s = FRAMES[f]["s"]
        ox, oy = FRAMES[f]["origin"]
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        X, Y = ox - y * s, oy - z * s                   # back to photo px
        side = np.abs(n[..., 0]) > 0.7
        poly = (mat == MATS.index("poly")) & side
        # the casing's vertical ribs under the handguard, the grip's horizontal grooves
        rib = poly & (X > g["hand_x0"]) & (X < g["hand_x1"]) & (Y > g["opening"][1] + 16) & (Y < g["opening"][3] + 2)
        col[rib & (np.mod(X, 9.0) < 2.5)] *= 0.5
        gx = [q[0] for q in g["grip"]]
        grip = poly & (X > min(gx) + 4) & (X < max(gx) - 4) & (Y > g["recv_bottom"] + 14)
        col[grip & (np.mod(Y, 5.0) < 1.6)] *= 0.55
        # the receiver's screws and seam, the front sight's ring
        rec = poly & (X > g["receiver"][0][0] + 20) & (Y < g["recv_bottom"] - 4) & (Y > g["recv_bottom"] - 90)
        col[rec & (np.abs(Y - (g["recv_bottom"] - 4.0)) < 0.6)] *= 0.5
        cx, cy, cr = g["sight_ring"]
        d = np.hypot(X - cx, Y - cy)
        ring = side & (mat == MATS.index("steel")) & (d < cr) & (d > cr - 3.0)
        col[ring] *= 0.45
        # the launcher's bore and the muzzle's
        t0, t1, ty, tr = g["tube"]
        col[(np.abs(X - t0) < 1.0) & (np.hypot(x / 1.0, (Y - ty) / s * 1.0) < (tr - 7.0) / s)] = 6
        bore = FRAMES[f]["bore"]
        col[(np.abs(X - g["muzzle_x"]) < 1.0) & (np.hypot(x, (Y - bore) / s) < 3.0)] = 6
        # the brake's slots
        a, c, r = g["brake"]
        br = (mat == MATS.index("steel")) & (X > a + 4) & (X < c - 4) & (np.abs(n[..., 1]) < 0.5)
        col[br & (np.mod(X - a, 8.0) < 3.0) & (np.abs(Y - bore) < r * 0.55)] = 10
    col = common(maps, col, mat)
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

def gp(f, x, y, xoff=0.0):
    yy, zz = P(f, x, y)
    return [round(xoff * K, 4) + 0.0, round(yy * K, 4) + 0.0, round(zz * K, 4) + 0.0]


def points(gun, g):
    f = g["frame"]
    bore = FRAMES[f]["bore"]
    s = FRAMES[f]["s"]
    muzzle = gp(f, g["muzzle_x"], bore)
    if gun == "A91M":
        ins, rear = AK_SEAT
        lips_x = g["catch_front"] - (0.5 + rear) * s
        lips_y = g["recv_bottom"] - ins * s
        magazine = gp(f, lips_x, lips_y)
        canon = [muzzle[0], round(muzzle[1] - AK_CANON_BACK, 4), muzzle[2]]
    else:
        magazine = gp(f, *g["mag"][0])
        canon = [muzzle[0], round(muzzle[1] - AR_CANON_BACK * K, 4), muzzle[2]]
    t0, _, ty, _ = g["tube"]
    ro = rail_origin(g)
    return {
        "muzzle": {"offset": muzzle, "rotate": [-90.0, 0.0, -180.0]},
        "muzzle_gl": {"offset": gp(f, t0, ty), "rotate": [-90.0, 0.0, -180.0]},
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
    mag = build_magazine(G5)
    kit.unwrap(bodies + bolts + mounts, 0.004)
    kit.unwrap([mag], 0.01)
    gs = list(GUNS.values())
    maps = [bake(o, [o, bl], 512) for o, bl in zip(bodies, bolts)]
    maps += [bake(bl, [o, bl], 512) for o, bl in zip(bodies, bolts)]
    maps += [bake(m, [m, o], 512) for m, o in zip(mounts, bodies)]
    texture(maps, ["body"] * 2 + ["bolt"] * 2 + ["mount"] * 2, gs + gs + gs, 512, os.path.join(TEX_DIR, "A91M.png"))
    texture([bake(mag, [mag], 128)], ["mag"], [None], 128, os.path.join(TEX_DIR, MAG_NAME + ".png"))
    bounds = {o.name: kit.bounds_of(o) for o in bodies + bolts + mounts + [mag]}
    out = {gun: points(gun, g) for gun, g in GUNS.items()}
    gom_mag = kit.import_mesh(os.path.join(GOM, "models_X/weapons/magazines/assault_rifles.fbx"),
                              "556x45Magazine30_STANAG")
    out["_mag_prop2"] = kit.bip01_prop2(mag, gom_mag, GOM_STANAG_PROP2) if gom_mag else None
    if gom_mag:
        bpy.data.objects.remove(gom_mag)
    out["_bounds"] = bounds
    out["_notes"] = {
        "units": "game units (0.603 of real size); +Y muzzle, +Z top, +X the gun's left; origin = the grip's rear top",
        "magazine": "A91M: GoM's AK magazines' feed lips (the Grozas' seat); A91M556: its own magazine's lips",
        "muzzle_gl": "the launcher tube's bore at its front: the launcher weapon's muzzle",
        "canon": "A91M: GoM's AK mount (0.0282 behind the muzzle, the Grozas'); A91M556: GoM's AR mount (28.8 mm)",
        "bolt_fired": "the charging handle back %.0f mm (GoM's AK swap)" % CARRIER_TRAVEL,
    }
    with open(POINTS_JSON, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    kit.export(bodies + bolts + mounts, FBX_GUN)
    kit.export([mag], FBX_MAGS)
    for name, bd in bounds.items():
        print("%-20s tris %5d  min %s  max %s" % (name, bd["tris"], bd["min"], bd["max"]))


if __name__ == "__main__":
    main()
