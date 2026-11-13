"""H&K HK416 D14.5RS from Guns of Marz's AR15 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_hk416.py

User, 2026-11-13 (TODO.md "the HK416 / HK417 set"): the standard 14.5" carbine, Post-93, 5.56 on GoM's STANAG
magazines, rifle-held. Built on GoM's AR15 at its own size (the HK416 is an M4-sized AR): its upper and lower
receiver, flat top, buffer tube, bolt and charging handle stay GoM's (GoM's AR15 bolt / handle table drives them);
GoM's A2 stock, A2 grip, fixed rear sight and everything ahead of the receiver are replaced by the HK416's own parts.

References (references/hk416/, SOURCES.txt; gathered before modelling, user 2026-11-13): the main side view is
IMFDB's "HK416_14.5_Current.jpg" (a D14.5RS from its left, nearly orthographic; 1.69 px a mm along and across,
read off GoM's receiver: its end plate at x 1040 = 11.4 mm behind the grip, the upper's front at x 690 = 218.5, the
bore at y 131.5 px); cross-checked with H&K's 2007 operator's manual (both sides, the rail system off the gun, its line
drawing, the diopter sight), the licensed VFC D14.5RS and HK416D replicas (3/4 views from both ends, close-ups of the
receiver, rail, sights, stock, grip), the HK416N photo and the user's photo of the left side. The photo's muzzle
lands at 618.5 mm against GoM's M4A1's 611 (the same 14.5" barrel), which checks the scale.
GoM's receiver is 9 mm lower over the bore than the real one, so parts on top (rail system, sights) are measured from
the receiver's flat top, everything else from the bore.

Parts:
- the Free Floating Rail System: rails at 12, 3, 6 and 9 o'clock, its top crossbars flush with the receiver's, from
  the upper's front to 447.6 mm ahead of the grip; a row of four oval slots over and under each side rail, the QD
  sling cup at the front, the lock boss under the rear;
- the gas block with H&K's MP5-type flip-up front sight (up) just ahead of it; the barrel stepped down ahead of the
  block (8.3 / 6.8 mm radius); H&K's flash hider (GoM's AR15 birdcage, stretched to the photo's 54 mm);
- H&K's rotary diopter rear sight (up, as in every photo) on the receiver's flat top, which runs to the rear; both
  sights also folded in two more bodies (user, 2026-11-13: the iron sights follow the optic fitted);
- H&K's ergonomic grip (traced; replaces GoM's A2 grip); GoM's selector mirrored onto the right side (H&K's is
  ambidextrous) and H&K's red and white selector labels on both sides (HK416_MARKINGS);
- H&K's telescopic stock as its own node: the housing over the buffer tube, the lower body, the butt block with the ribbed pad and the sling loop; drawn at `stock` deployed (75 mm back) and at
  `stock_folded` where the photo has it (all the way in).

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_HK416.fbx   HK416_BODY (sights up), HK416_BODY_RD (rear folded),
                                                             HK416_BODY_FD (both folded), HK416_BOLT,
                                                             HK416_CHARGING_HANDLE, HK416_STOCK,
                                                             HK416_MARKINGS (the selector labels, own texture)
    scripts/post93/hk416_points.json                         points
The gun keeps GoM's AR15 texture (weapons/firearms/assault_rifles/AR15).
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import build_sr25 as sr  # noqa: E402
import build_mk11 as mk  # noqa: E402

ROOT = sr.ROOT
P93 = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
OUT_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK416.fbx")
POINTS = os.path.join(HERE, "hk416_points.json")
R = sr.R

# the side photo (px) to gun mm
PX, END_PX, END_Y, BORE_PX = 1.69, 1040.0, 11.4, 131.5
RAIL_TOP_PX, RAIL_BOT_PX = 69.0, 183.5          # the rail system's top and bottom crossbars


def py(x):
    """Photo x (px) to mm ahead of the grip."""
    return END_Y + (END_PX - x) / PX


CUT = 212.0                        # GoM's AR15 pieces from here forward are its 20" barrel group (dropped)
STOCK_CUT = -200.0                 # ... the A2 stock's shell reaches back past this (dropped)
GRIP_CUT = -100.0                  # ... and its A2 grip reaches down past this (dropped)
RECV_FRONT = 218.5                 # GoM's AR15 upper receiver's front
RAIL_REAR = 59.5                   # GoM's flat-top rail starts here; behind it GoM's fixed rear sight (replaced by rail)
HG_END = py(303.0)                 # the rail system's front (447.6)
GAS = (py(300.0), py(272.0))       # the gas block / front sight base
STEP_Y = py(190.0)                 # the barrel steps down here
CANON, MUZZLE = py(105.0), py(14.0)  # the flash hider's rear and front (564.6, 618.5)
FH_GOM, FH_GOM_LEN = 688.4, 45.5   # GoM's AR15 flash hider's rear and length
BARREL_R = (8.3, 6.8)
HG_HALF = 23.0                     # the rail box's half width (side crossbars out to 30)
RAIL_BOT = 11.8                    # the bottom crossbars' faces (the photo's 31 mm under the bore)
SIDE_RAIL = (py(640.0), py(325.0))     # side rails' extent (crossbars), and the bottom rail's
BOTTOM_RAIL = (py(690.0) + 30.0, py(320.0))
SLOTS = [(py(380.0), py(362.0)), (py(458.0), py(405.0)), (py(540.0), py(488.0)), (py(602.0), py(570.0))]
SLOT_ROWS_PX = ((104.0, 112.0), (151.0, 157.0))
QD = (py(335.0), 158.0)            # the QD sling cup (y mm, photo y px)
LOCK = (py(660.0), py(620.0), 150.0, 170.0)   # the rail lock boss under the rear (y, y, photo y px)
FRONT_POST = (py(292.0), py(278.0), 12.0, 90.0, 167.0)   # post y span, its top, the base's top / bottom (px)
REAR_SIGHT = (py(945.0), py(890.0), 45.0, 12.0, (py(928.0), py(893.0)))   # base y, base top, top (px), drum y
SIGHT_STATES = [("HK416_BODY", True, True), ("HK416_BODY_RD", True, False), ("HK416_BODY_FD", False, False)]
SCOPE_Y = 150.0                    # GoM's optics over the receiver, ahead of the diopter (fit-checked)
STOCK_TRAVEL = 75.0                # the photo's stock is all the way in; deployed is this much further back
STOCK_HALF = (19.0, 16.0, 22.0)    # housing, lower body, butt block
# the stock's outline in the photo (px): housing (x, top, bottom), lower body, butt block
HOUSING_PX = [(1052, 103, 174), (1060, 101, 174), (1100, 101, 179), (1260, 101, 184), (1322, 101, 184)]
LOWER_PX = [(1108, 176, 190), (1120, 178, 218), (1200, 182, 219), (1220, 183, 236), (1240, 183, 257),
            (1260, 184, 277), (1280, 184, 296), (1300, 184, 311), (1322, 184, 312)]
BUTT_PX = [(1318, 91, 312), (1374, 91, 310), (1381, 128, 280), (1387, 165, 250)]
PAD_RIBS_PX = [172, 184, 195, 207, 219, 232, 244, 256, 268]
WINDOW_PX = (1262.0, 1312.0, 184.0, 193.0)       # the slot between the housing and the lower body
# H&K's grip, traced row by row (photo y, front x, back x), top (inside the lower) to the base
GRIP_PX = [(232, 932, 995), (245, 930, 1000), (280, 937, 1019), (300, 943, 1032), (310, 938, 1037),
           (320, 949, 1041), (340, 956, 1048), (360, 963, 1054), (380, 970, 1058), (390, 967, 1061),
           (397, 974, 1055)]
GRIP_HALF = 15.0
DARK = (0.6094, 0.9219, 0.6406, 0.9531)   # a near-black patch of GoM's AR15 texture (slots, holes)
# H&K's selector markings (user, 2026-11-13: "the red labels ... for selecting fire mode is an important detail"), read
# off the side photo round the selector's pivot (x 941, y 190 px): the red single-shot label above it, the white
# safe label ahead of it, the red automatic label behind it, low under the lever (photo px: x0, x1, y0, y1)
SEL_PIVOT_PX = (941.0, 190.0)
SEL_LABELS_PX = [("RED", 935.0, 951.0, 169.0, 177.0), ("WHITE", 910.0, 926.0, 190.0, 198.0),
                 ("RED", 957.0, 980.0, 195.0, 199.0)]
# their texture (HK416_MARKINGS.png, make_hk416_art.py): the left half red, the right half white
MARK_PATCH = {"RED": (0.06, 0.12, 0.44, 0.88), "WHITE": (0.56, 0.12, 0.94, 0.88)}


def loft(bm, uv, patch, cols, chamfer):
    """A solid along y from cross-sections [(y, z_top, z_bot, half_width)] (chamfered rectangles), capped."""
    rings = []
    for y, zt, zb, w in cols:
        c = min(chamfer, (zt - zb) / 2.5, w / 2.5)
        rings.append([bm.verts.new((x * R, y * R, -z * R)) for x, z in mk.chamfered(-w, w, zb, zt, c)])
    _skin(bm, uv, patch, rings)


def loft_z(bm, uv, patch, rows, half, chamfer):
    """A solid along z from horizontal sections [(z, y_front, y_back)] (chamfered rectangles across x), capped."""
    rings = []
    for z, yf, yb in rows:
        c = min(chamfer, (yf - yb) / 2.5, half / 2.5)
        rings.append([bm.verts.new((x * R, y * R, -z * R)) for x, y in mk.chamfered(-half, half, yb, yf, c)])
    _skin(bm, uv, patch, rings)


def _skin(bm, uv, patch, rings):
    n = len(rings[0])
    faces = []
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    sr.paint(uv, patch, faces)


def stadium(bm, uv, patch, x_face, y0, y1, z0, z1, out=0.4, seg=6):
    """A flat oval plate on a side face (x = its face), long along y, standing `out` off it."""
    r = (z1 - z0) / 2.0
    zc = (z0 + z1) / 2.0
    pts = []
    for i in range(seg + 1):
        a = -math.pi / 2 + math.pi * i / seg
        pts.append((y1 - r + r * math.cos(a), zc + r * math.sin(a)))
    for i in range(seg + 1):
        a = math.pi / 2 + math.pi * i / seg
        pts.append((y0 + r + r * math.cos(a), zc + r * math.sin(a)))
    s = 1.0 if x_face > 0 else -1.0
    rings = [[bm.verts.new((xx * R, yy * R, -zz * R)) for yy, zz in pts] for xx in (x_face - s * 0.3, x_face + s * out)]
    _skin(bm, uv, patch, rings)


def build_stock(bore, patch, like):
    """The stock where the photo has it (collapsed), moved back by STOCK_TRAVEL so that `stock` is deployed."""
    def p(x, y):
        return py(x) - STOCK_TRAVEL, bore + (BORE_PX - y) / PX
    me = bpy.data.meshes.new("HK416_STOCK")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    for cols, half, ch in ((HOUSING_PX, STOCK_HALF[0], 6.0), (LOWER_PX, STOCK_HALF[1], 4.0),
                           (BUTT_PX, STOCK_HALF[2], 4.0)):
        sec = []
        for x, top, bot in cols:
            y, zt = p(x, top)
            sec.append((y, zt, p(x, bot)[1], half))
        loft(bm, uv, patch, sorted(sec, key=lambda c: c[0]), ch)
    # the pad's ribs across the rear face, the sling loop on the butt's top
    yr = p(1386.0, 0)[0]
    for ry in PAD_RIBS_PX:
        sr.box(bm, uv, patch, (0.0, yr - 1.0, p(0, ry)[1]), (STOCK_HALF[2] * 2 - 6.0, 3.0, 2.6))
    ly, lz = p(1335.0, 87.0)
    sr.box(bm, uv, patch, (0.0, ly, lz), (5.0, 10.0, 6.0))
    # the dark slot under the housing (the diagonal ribs of the lower body were dropped: user, 2026-11-13)
    wx0, wx1, wy0, wy1 = WINDOW_PX
    for side in (-1, 1):
        stadium(bm, uv, DARK, side * STOCK_HALF[1], p(wx1, 0)[0], p(wx0, 0)[0], p(0, wy1)[1], p(0, wy0)[1], out=0.6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("HK416_STOCK", me)
    o.matrix_world = like.matrix_world.copy()
    bpy.context.scene.collection.objects.link(o)
    return o


def build_gun():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/firearms/AR15.fbx")
    objs = {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}
    body = objs["AR15_BODY"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv = bm.loops.layers.uv.active
    comps = sr.islands(bm)
    ahead = [c for c in comps if min(sr.gy(v) for v in c) >= CUT]
    barrel = max((c for c in ahead if max(v.co.x for v in c) / R < 12.0),
                 key=lambda c: max(sr.gy(v) for v in c) - min(sr.gy(v) for v in c))
    guard = max(ahead, key=lambda c: max(abs(v.co.x) for v in c))
    fh = [c for c in ahead if min(sr.gy(v) for v in c) >= FH_GOM - 1.0]
    zs = [sr.gz(v) for v in barrel]
    B = (min(zs) + max(zs)) / 2.0
    steel, black = sr.uv_patch(bm, uv, barrel), sr.uv_patch(bm, uv, guard)
    stock = [c for c in comps if min(sr.gy(v) for v in c) < STOCK_CUT]
    # GoM's selector (its round boss and lever on the gun's left, +x), mirrored onto the right: the HK416's is
    # ambidextrous
    selector = [c for c in comps if min(v.co.x for v in c) / R > 13.0 and min(sr.gy(v) for v in c) > 45.0
                and max(sr.gy(v) for v in c) < 90.0 and min(sr.gz(v) for v in c) > -5.0
                and max(sr.gz(v) for v in c) < 16.0]
    boss = min(selector, key=lambda c: max(sr.gy(v) for v in c))
    pivot = ((min(sr.gy(v) for v in boss) + max(sr.gy(v) for v in boss)) / 2.0,
             (min(sr.gz(v) for v in boss) + max(sr.gz(v) for v in boss)) / 2.0)
    grip = [c for c in comps if min(sr.gz(v) for v in c) < GRIP_CUT and c not in stock]
    top_rail = [c for c in comps if c not in ahead and min(sr.gy(v) for v in c) > 20.0
                and max(sr.gy(v) for v in c) > 200.0 and min(sr.gz(v) for v in c) > 50.0]
    rail_top = max(sr.gz(v) for c in top_rail for v in c if sr.gy(v) > RAIL_REAR + 1.0)
    rear_sight = [v for c in top_rail for v in c if sr.gy(v) < RAIL_REAR - 0.5]
    rail_x = max(v.co.x for c in top_rail for v in c) / R
    rail_y0 = min(sr.gy(v) for c in top_rail for v in c)
    rail_z0 = min(sr.gz(v) for c in top_rail for v in c)
    rail_mid = min(sr.gz(v) for c in top_rail for v in c if sr.gy(v) > RAIL_REAR + 1.0 and sr.gz(v) > rail_z0 + 1.0)
    # H&K's flash hider: GoM's birdcage moved to the barrel's end and stretched to the photo's length
    k = (MUZZLE - CANON) / FH_GOM_LEN
    for c in fh:
        for v in c:
            v.co.y = (CANON + (sr.gy(v) - FH_GOM) * k) * R
    bmesh.ops.delete(bm, geom=[v for c in ahead + stock + grip if c not in fh for v in c] + rear_sight,
                     context='VERTS')
    old = set(bm.faces)
    for c in selector:
        mirror_island(bm, uv, c)

    def rz(ypx):
        """A photo height on the rail system or its sights (px) to mm: from the receiver's flat top, at the photo's
        rail height per px (GoM's receiver sits lower over the bore than the real one)."""
        f = (ypx - RAIL_TOP_PX) / (RAIL_BOT_PX - RAIL_TOP_PX)
        return rail_top - f * (rail_top - RAIL_BOT)

    def bz(ypx):
        """A photo height elsewhere (px) to mm, from the bore."""
        return B + (BORE_PX - ypx) / PX

    # GoM's flat-top rail carried on to the receiver's rear (H&K's upper is railed full length)
    mk.prism(bm, uv, black, [(rail_x, rail_z0), (rail_x, rail_mid), (rail_x - 1.0, rail_top), (-rail_x + 1.0, rail_top),
                             (-rail_x, rail_mid), (-rail_x, rail_z0)], rail_y0, RAIL_REAR + 0.5)
    # the barrel: inside the rail system, the thick part to the step, the thin part to the flash hider
    sr.lathe(bm, uv, steel, B, [(RECV_FRONT - 10.0, BARREL_R[0]), (STEP_Y, BARREL_R[0]), (STEP_Y + 2.0, BARREL_R[1]),
                                (CANON + 1.0, BARREL_R[1]), (CANON + 1.0, 3.0)], seg=20)
    # the rail system: a chamfered box, a slightly larger front cap, a collar at the receiver
    tbase = rail_top - B - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    bbase = B - RAIL_BOT - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    za, zb = B - bbase, B + tbase
    y0, y1 = RECV_FRONT, HG_END
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF, HG_HALF, za, zb, 8.0), y0 + 4.0, y1 - 7.0)
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF - 1.0, HG_HALF + 1.0, za - 1.0, zb, 9.0), y1 - 7.0, y1)
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF + 2.0, HG_HALF - 2.0, za + 2.0, zb, 7.0), y0, y0 + 4.0)
    side_h = (rz(115.0) + rz(150.0)) / 2.0
    mk.rail(bm, uv, black, y0, y1, "top", B, tbase, tbase + mk.RAIL_BASE[1])
    mk.rail(bm, uv, black, BOTTOM_RAIL[0], BOTTOM_RAIL[1], "bottom", B, bbase, bbase + mk.RAIL_BASE[1])
    for side in ("left", "right"):
        mk.rail(bm, uv, black, SIDE_RAIL[0], SIDE_RAIL[1], side, side_h, HG_HALF, HG_HALF + mk.RAIL_BASE[1])
    # the oval slots over and under the side rails, the QD sling cup at the front, the lock boss under the rear
    for s in (-1, 1):
        for a, b in SLOTS:
            for r0, r1 in SLOT_ROWS_PX:
                stadium(bm, uv, DARK, s * HG_HALF, a, b, rz(r1), rz(r0))
        sr.lathe_x(bm, uv, black, (s * HG_HALF, QD[0], rz(QD[1])), [(0.0, 6.0), (s * 1.8, 6.0), (s * 1.8, 4.0)])
        sr.lathe_x(bm, uv, DARK, (s * (HG_HALF + 1.0), QD[0], rz(QD[1])), [(0.0, 3.8), (s * 1.0, 3.8)])
    sr.box(bm, uv, black, (0.0, (LOCK[0] + LOCK[1]) / 2.0, (rz(LOCK[2]) + rz(LOCK[3])) / 2.0),
           (2 * HG_HALF + 3.0, LOCK[1] - LOCK[0], rz(LOCK[2]) - rz(LOCK[3])))
    # the gas block (the front sight's base), round the barrel ahead of the rail system's cap
    fp0, fp1, ftop, fbase, fbot = FRONT_POST
    g0, g1 = GAS
    btop, bbot = rz(fbase), bz(fbot)
    sr.box(bm, uv, black, (0.0, (g0 + g1) / 2.0, (btop + bbot) / 2.0), (24.0, g1 - g0, btop - bbot))
    # H&K's grip
    rows = [(bz(y), py(xf), py(xb)) for y, xf, xb in GRIP_PX]
    loft_z(bm, uv, black, sorted(rows, key=lambda r: -r[0]), GRIP_HALF, 5.0)
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in old])
    # one body per sight state (Gunworks' ConditionalModel picks it from the optic fitted, HK416.lua): both sights
    # up; the rear folded (a red dot or holographic sight, the front seen through it); both folded (a magnified scope)
    sight = dict(rail_top=rail_top, btop=btop, top=rz(ftop), fy=(fp0 + fp1) / 2.0, fl=fp1 - fp0,
                 rear=REAR_SIGHT, rz=rz)
    marks = build_markings(bm, pivot, body)
    bodies = []
    for name, front_up, rear_up in SIGHT_STATES:
        b2 = bm.copy()
        uv2 = b2.loops.layers.uv.active
        old2 = set(b2.faces)
        add_sights(b2, uv2, black, sight, front_up, rear_up)
        bmesh.ops.recalc_face_normals(b2, faces=[f for f in b2.faces if f not in old2])
        me = bpy.data.meshes.new(name)
        b2.to_mesh(me)
        b2.free()
        for mat in body.data.materials:
            me.materials.append(mat)
        o = bpy.data.objects.new(name, me)
        o.matrix_world = body.matrix_world.copy()
        bpy.context.scene.collection.objects.link(o)
        bodies.append(o)
    bm.free()
    for old_name, new in (("AR15_BOLT", "HK416_BOLT"), ("AR15_CHARGING_HANDLE", "HK416_CHARGING_HANDLE")):
        objs[old_name].name = objs[old_name].data.name = new
    st = build_stock(B, black, body)
    for o in set(bpy.data.objects) - before:
        if not o.name.startswith("HK416_"):
            bpy.data.objects.remove(o)
    faces = {"top": rail_top, "bottom": RAIL_BOT, "side": HG_HALF + mk.RAIL_BASE[1] + mk.RAIL_TOOTH[1], "bore": B,
             "side_h": side_h}
    return bodies + [bpy.data.objects[n] for n in ("HK416_BOLT", "HK416_CHARGING_HANDLE")] + [st, marks], faces


def mirror_island(bm, uv, comp):
    """A copy of one of GoM's mesh islands mirrored to the other side (x negated, faces turned back round)."""
    vmap = {v: bm.verts.new((-v.co.x, v.co.y, v.co.z)) for v in comp}
    for f in {f for v in comp for f in v.link_faces}:
        loops = list(f.loops)
        nf = bm.faces.new([vmap[l.vert] for l in reversed(loops)])
        for nl, l in zip(nf.loops, reversed(loops)):
            nl[uv].uv = l[uv].uv


def build_markings(body_bm, pivot, like):
    """H&K's selector labels on both sides of the lower receiver, a node of its own on its own small texture
    (drawn by the gun's always-fitted left rail part, models_hk416.txt): each label a thin plate standing 0.3 mm off
    the receiver's side, found by a ray along x at its middle; placed round GoM's selector pivot as the photo has
    them round H&K's."""
    tree = BVHTree.FromBMesh(body_bm)
    me = bpy.data.meshes.new("HK416_MARKINGS")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    px0, py0 = SEL_PIVOT_PX
    for colour, x0, x1, y0, y1 in SEL_LABELS_PX:
        ya, yb = pivot[0] + (px0 - x1) / PX, pivot[0] + (px0 - x0) / PX
        za, zb = pivot[1] + (py0 - y1) / PX, pivot[1] + (py0 - y0) / PX
        yc, zc = (ya + yb) / 2.0, (za + zb) / 2.0
        for side in (1.0, -1.0):
            hit, _, _, _ = tree.ray_cast(Vector((side * 60.0 * R, yc * R, -zc * R)), Vector((-side, 0.0, 0.0)))
            if hit is None:
                print("no receiver under the label at", round(yc, 1), round(zc, 1))
                continue
            xf = hit.x / R
            sr.box(bm, uv, MARK_PATCH[colour], (xf + side * 0.15, yc, zc), (0.3, yb - ya, zb - za))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("HK416_MARKINGS", me)
    o.matrix_world = like.matrix_world.copy()
    bpy.context.scene.collection.objects.link(o)
    return o


def add_sights(bm, uv, black, s, front_up, rear_up):
    """H&K's MP5-type flip-up front sight on the gas block and its rotary diopter rear sight on the flat top, each
    up (as in every photo) or folded (the front back onto the rail system's top, the rear forward onto its base)."""
    rail_top, btop, top, fy, fl, rz = s["rail_top"], s["btop"], s["top"], s["fy"], s["fl"], s["rz"]
    if front_up:
        # two protective ears, the post, the hood's top
        for side in (-1, 1):
            sr.box(bm, uv, black, (side * 8.0, fy, (btop + top) / 2.0), (3.2, fl, top - btop))
        sr.box(bm, uv, black, (0.0, fy, (btop + top - 4.0) / 2.0), (2.6, 3.0, top - 4.0 - btop))
        sr.box(bm, uv, black, (0.0, fy, top - 1.0), (19.2, fl, 2.0))
    else:
        # the hinge block on the gas block, the ears and post lying back along the top rail
        sr.box(bm, uv, black, (0.0, fy, (btop + rail_top + 4.0) / 2.0), (19.2, fl, rail_top + 4.0 - btop))
        length = (top - btop) * 0.8
        sr.box(bm, uv, black, (0.0, fy - fl / 2.0 - length / 2.0, rail_top + 2.5), (19.2, length, 5.0))
    r0, r1, rbase, rtop, (d0, d1) = s["rear"]
    zb_top = rz(rbase)
    dr = (rz(rtop) - zb_top) / 2.0
    if rear_up:
        # the clamp base (the photo's height), the drum across the bore between its two guards
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0, (rail_top + zb_top) / 2.0),
              (24.0, r1 - r0, zb_top - rail_top + 1.0))
        sr.lathe_x(bm, uv, black, (-10.0, (d0 + d1) / 2.0, zb_top + dr - 0.5), [(0.0, dr), (20.0, dr)], seg=16)
        for side in (-1, 1):
            sr.box(bm, uv, black, (side * 11.0, (d0 + d1) / 2.0, zb_top + dr * 0.8), (2.4, d1 - d0 + 4.0, dr * 1.6))
    else:
        # folded: the sight body pivots down into the clamp, leaving a low block (about 10 mm over the rail) with the
        # drum's guards lying forward on it, so a scope's long body clears it
        low = rail_top + 7.0
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0, (rail_top + low) / 2.0), (24.0, r1 - r0, low - rail_top + 1.0))
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0 + 3.0, low + 1.5), (22.0, r1 - r0 - 10.0, 3.0))


def g(v):
    return round(v * R, 4) + 0.0


def main():
    if sr.GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    gun, f = build_gun()
    B = f["bore"]
    gom = sr.gom_points()
    pts = {k: gom[k] for k in ("magazine", "bolt_fired", "charging_handle_open", "world")}
    # GoM's relations for parts on rails, as on the Mk 11 (build_mk11.py)
    pts.update({
        "muzzle": {"offset": [0.0, g(MUZZLE), g(B)], "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": [0.0, g(CANON), g(B)], "rotate": [0.0, 0.0, 0.0]},
        "stock": {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]},
        "stock_folded": {"offset": [0.0, g(STOCK_TRAVEL), 0.0], "rotate": [0.0, 0.0, 0.0]},
        "scope": {"offset": [0.0, g(SCOPE_Y), round(g(f["top"]) - 0.0032, 4)], "rotate": [0.0, 0.0, 0.0]},
        "foregrip": {"offset": [0.0, g(370.0), round(g(f["bottom"]) + 0.003, 4)], "rotate": [0.0, 0.0, 0.0]},
        "bipod": {"offset": [0.0, g(410.0), round(g(f["bottom"]) + 0.003 - 0.0044, 4)], "rotate": [0.0, 0.0, 0.0]},
        "light_left": {"offset": [round(g(f["side"]) + 0.0007, 4), g(400.0), g(f["side_h"])], "rotate": [0.0, 0.0, 0.0]},
        "laser_right": {"offset": [round(-g(f["side"]) - 0.0018, 4), g(400.0), round(g(f["side_h"]) - 0.0008, 4)],
                        "rotate": [0.0, 0.0, 0.0]},
    })
    pts["_extras"] = {"bore_mm": round(B, 2), "rail_faces_mm": {k: round(v, 2) for k, v in f.items()},
                      "handguard_mm": [RECV_FRONT, round(HG_END, 1)], "canon_mm": round(CANON, 1),
                      "muzzle_mm": round(MUZZLE, 1), "k": R}
    bpy.ops.object.select_all(action='DESELECT')
    for o in gun:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT_GUN), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT_GUN, use_selection=True, object_types={'MESH'})
    with open(POINTS, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    print("wrote", OUT_GUN, POINTS, json.dumps(pts["_extras"]))


if __name__ == "__main__":
    main()
