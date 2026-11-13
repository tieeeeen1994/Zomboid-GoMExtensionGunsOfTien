"""H&K HK417 16" "Recce" and 20" "Sniper" from Guns of Marz's AR15 and our HK416 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_hk417.py

User, 2026-11-13 (TODO.md "the HK416 / HK417 set"): the HK416's 7.62x51mm big brother in its original pattern
(2006-), Post-93, rifle-held: the 16" Recce and the 20" Sniper, the same receiver, stock and magazines (H&K's own
translucent 10 and 20-round polymer magazines; real HK417 magazines do not fit the SR-25), the Sniper with a longer
barrel and a longer rail system.

References (references/hk417/, SOURCES.txt; gathered before modelling): the measuring photo is H&K's own press photo of
a 16" gun from its left (references/hk417/bing/b_028.jpg, 2000 px, serial 89-141008, sights folded, 10-round magazine,
the stock part way out), nearly orthographic. Its scale, 2.08 px a mm, is the mean of three reads that agree within
4 %: the trigger guard's opening (56 mm, as on the AR-15), H&K's grip from the bore to its base (157 mm, the HK416's
traced grip) and the overall length (905 / 985 mm stock in / out, the stock part way). Lengths are anchored on the
trigger guard opening's centre (107.7 mm ahead of the grip origin, as on GoM's AR15), so everything behind the trigger
group is GoM's AR15 / our HK416 unchanged (H&K's grip and stock fit as on the HK416) and the receiver ahead of it is
stretched to the photo: the upper's front lands at 240.2 mm (GoM's AR15 218.5), the magazine well grows to the
7.62 magazine. Heights and widths grow 5 / 6 % as on our SR-25 (an AR-10 is a little bigger every way). The 20"
Sniper from IMFDB's HK417 20" side view (imfdb/HK417_20MOD.jpg, scaled by the receiver): the rail system and the
barrel each about 100 mm longer.

Parts, as on the HK416 (build_hk416.py) unless said:
- the Free Floating Rail System, longer and a little wider: from the upper's front to 471.6 mm (16") / 570.6 (20"),
  top crossbars flush with the receiver's flat top, bottom crossbars 30.3 mm under the bore, side rails at the bore,
  the photo's oval slots over and under the side rails, the QD sling cup at the front, two cover screws low at the rear;
- the gas block with H&K's flip-up front sight just ahead of the rail system; the barrel (9.0 mm radius, stepped to
  8.0 for its last 29 mm) and H&K's long flash hider (GoM's birdcage stretched to the photo's 63 mm);
- H&K's diopter rear sight at the flat top's rear end (25-58 mm, the photo's), the receiver's flat top carried to the
  rear; sight states as the HK416's (both up / rear folded / both folded; no optic needs the rear taken off);
- H&K's grip, telescopic stock (HK417_STOCK, the HK416's at this bore), the selector mirrored and H&K's selector labels;
- H&K's 10 and 20-round magazines: smoke-grey polymer, the photo's 86 mm deep straight magazine, 100 / 140 mm out of the
  well, a black base plate, raised window frames on the sides.

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_HK417.fbx   HK417_BODY / HK417S_BODY (sights up) and their _RD
                                                             (rear folded), _FD (both) states, HK417_BOLT, HK417_CHARGING_HANDLE,
                                                             HK417_STOCK, HK417_MARKINGS
    P/models_X/weapons/magazines/GunsOfTienPost93_HK417_magazines.fbx   762x51Magazine10_HK417, 762x51Magazine20_HK417
    P/textures/weapons/GunsOfTienPost93/HK417_MAG.png        (make_hk417_art.py)
    scripts/post93/hk417_points.json                         {"HK417": points, "HK417S": points}
The guns keep GoM's AR15 texture; the markings HK416_MARKINGS.png.
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import build_sr25 as sr  # noqa: E402
import build_mk11 as mk  # noqa: E402
import build_hk416 as hk  # noqa: E402

R = sr.R
P93 = hk.P93
OUT_GUN = os.path.join(P93, "models_X/weapons/firearms/GunsOfTienPost93_HK417.fbx")
OUT_MAGS = os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_HK417_magazines.fbx")
POINTS = os.path.join(HERE, "hk417_points.json")

# the photo (b_028.jpg, px) to gun mm: along the bore from the trigger guard opening's centre, heights from the bore
PX, TRIG_PX, TRIG_Y, BORE_PX = 2.08, 1264.5, 107.7, 679.0


def py(x):
    return TRIG_Y + (TRIG_PX - x) / PX


def bh(ypx):
    """A photo height (px) as mm over the bore."""
    return (BORE_PX - ypx) / PX


# GoM's AR15 mm -> HK417 mm along the bore: unchanged behind the trigger guard's front, stretched ahead of it so the
# upper's front lands where the photo has it
KNOTS = ((-400.0, -400.0), (135.7, 135.7), (218.5, py(989.0)))
GROW_Z, GROW_X = sr.GROW_Z, sr.GROW_X
GOM_FH, GOM_FH_LEN = hk.FH_GOM, hk.FH_GOM_LEN
TRIGGER_PX = 1289.0                  # the photo's trigger blade, its middle at mid-height (build_hk416.align_trigger)

# per gun: the rail system's front, the side / bottom rails' fronts, the gas block (front sight), the barrel's step,
# the flash hider's rear (canon) and the muzzle; the 20" Sniper's rail and barrel each SNIPER_EXTRA longer
SNIPER_EXTRA = 99.0
BASE16 = dict(hg_end=py(507.5), side_front=py(545.0), bottom_front=py(530.0), gas=(py(505.0), py(470.0)),
              step=py(235.0), canon=py(175.0), muzzle=py(44.0))
VARIANTS = {"HK417": dict(BASE16, extra=0.0)}
VARIANTS["HK417S"] = dict({k: (tuple(v + SNIPER_EXTRA for v in val) if isinstance(val, tuple) else val + SNIPER_EXTRA)
                           for k, val in BASE16.items()}, extra=SNIPER_EXTRA)
VARIANTS["HK417S"]["muzzle"] = BASE16["muzzle"] + 101.6          # 20" against 16"
VARIANTS["HK417S"]["canon"] = BASE16["canon"] + 101.6
VARIANTS["HK417S"]["step"] = BASE16["step"] + 101.6
SIDE_REAR, BOTTOM_REAR = py(980.0), py(980.0)
BARREL_R = (9.0, 8.0)
HG_HALF = 25.0                       # the rail box's half width (side crossbars out to 32)
RAIL_BOT_UNDER_BORE = -bh(742.0)     # the bottom crossbars' faces under the bore (30.3)
SIDE_H = bh(679.5)                   # the side rails' middle over the bore
# the photo's slots (y from, to; row height over the bore) on both sides; the Sniper repeats the front ones further on
SLOT_ROWS = (bh(650.0), bh(704.0))
SLOTS16 = [((py(530.0), py(577.0)), 0), ((py(582.0), py(597.0)), 0), ((py(635.0), py(702.0)), 0),
           ((py(582.0), py(615.0)), 1), ((py(635.0), py(702.0)), 1)]
QD16 = (py(550.0), bh(709.0))
SCREWS = [(py(802.0), bh(716.0)), (py(880.0), bh(716.0))]
# the sights, H&K's as on the HK416 (heights over the flat top's crossbars as there): front post top 29.4 over the
# rail, its base's top 10.8 under it; the rear diopter base at the flat top's rear end (photo: 25-58 mm)
FRONT_TOP, FRONT_BASE, FRONT_LEN = 29.4, -10.8, 8.3
REAR = (25.0, 57.6, 12.4, 29.4, (35.1, 55.8))
# (no rear-off states as on the HK416: the rear sight sits at the flat top's very rear, and folded it clears every
# GoM optic's mount; fit_audit against each state, 2026-11-13)
SIGHT_STATES = [("_BODY", True, True), ("_BODY_RD", True, False), ("_BODY_FD", False, False)]
SCOPE_Y = 150.0
# H&K's magazines (photo px: the 10-round's front and rear edges from the well down, its base plate's bottom)
MAG10_FRONT = [(1012.0, 835.0), (992.0, 985.0)]
MAG10_REAR = [(1190.0, 850.0), (1177.0, 1015.0)]
MAG10_BASE = 1042.0
MAG20_EXTRA = 40.0                   # the 20 is longer by this along its edges (photos: 1.9 x as long as deep)
MAG_HALF = 15.5
MAG_PATCH = {"SMOKE": (0.06, 0.1, 0.44, 0.9), "DARK": (0.56, 0.1, 0.94, 0.9)}


def ymap(y):
    for (a0, b0), (a1, b1) in zip(KNOTS, KNOTS[1:]):
        if y <= a1:
            return b0 + (y - a0) * (b1 - b0) / (a1 - a0)
    (a0, b0), (a1, b1) = KNOTS[-2], KNOTS[-1]
    return b0 + (y - a0) * (b1 - b0) / (a1 - a0)


def grow_mesh(bm):
    for v in bm.verts:
        x, y, z = v.co.x / R, sr.gy(v), sr.gz(v)
        v.co.x, v.co.y, v.co.z = x * GROW_X * R, ymap(y) * R, -z * GROW_Z * R


def import_ar15():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/firearms/AR15.fbx")
    return {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}, before


def build_gun(name, var, keep_parts):
    """One gun's body states (and, with keep_parts, the bolt, handle, stock and markings)."""
    objs, before = import_ar15()
    body = objs["AR15_BODY"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv = bm.loops.layers.uv.active
    comps = sr.islands(bm)
    hk.align_trigger(comps, py(TRIGGER_PX))           # GoM's blade onto H&K's (y is unchanged behind 135.7)

    def ymin(c):
        return min(sr.gy(v) for v in c)

    def ymax(c):
        return max(sr.gy(v) for v in c)
    ahead = [c for c in comps if ymin(c) >= hk.CUT]
    barrel = max((c for c in ahead if max(v.co.x for v in c) / R < 12.0), key=lambda c: ymax(c) - ymin(c))
    guard = max(ahead, key=lambda c: max(abs(v.co.x) for v in c))
    fh = [c for c in ahead if ymin(c) >= GOM_FH - 1.0]
    zs = [sr.gz(v) for v in barrel]
    bore = (min(zs) + max(zs)) / 2.0
    steel, black = sr.uv_patch(bm, uv, barrel), sr.uv_patch(bm, uv, guard)
    stock = [c for c in comps if ymin(c) < hk.STOCK_CUT]
    selector = [c for c in comps if min(v.co.x for v in c) / R > 13.0 and ymin(c) > 45.0 and ymax(c) < 90.0
                and min(sr.gz(v) for v in c) > -5.0 and max(sr.gz(v) for v in c) < 16.0]
    boss = min(selector, key=lambda c: ymax(c))
    pivot = (ymap((ymin(boss) + ymax(boss)) / 2.0),
             GROW_Z * (min(sr.gz(v) for v in boss) + max(sr.gz(v) for v in boss)) / 2.0)
    grip = [c for c in comps if min(sr.gz(v) for v in c) < hk.GRIP_CUT and c not in stock]
    top_rail = [c for c in comps if c not in ahead and ymin(c) > 20.0 and ymax(c) > 200.0
                and min(sr.gz(v) for v in c) > 50.0]
    rail_top = GROW_Z * max(sr.gz(v) for c in top_rail for v in c if sr.gy(v) > hk.RAIL_REAR + 1.0)
    rear_sight = [v for c in top_rail for v in c if sr.gy(v) < hk.RAIL_REAR - 0.5]
    rail_x = GROW_X * max(v.co.x for c in top_rail for v in c) / R
    rail_y0 = ymap(min(sr.gy(v) for c in top_rail for v in c))
    rail_z0 = GROW_Z * min(sr.gz(v) for c in top_rail for v in c)
    rail_mid = GROW_Z * min(sr.gz(v) for c in top_rail for v in c
                            if sr.gy(v) > hk.RAIL_REAR + 1.0 and sr.gz(v) / 1.0 > rail_z0 / GROW_Z + 1.0)
    # H&K's flash hider: GoM's birdcage, kept with its original along-bore position for the stretch below
    fh_y = {v: sr.gy(v) for c in fh for v in c}
    bmesh.ops.delete(bm, geom=[v for c in ahead + stock + grip if c not in fh for v in c] + rear_sight,
                     context='VERTS')
    for c in selector:
        hk.mirror_island(bm, uv, c)
    grow_mesh(bm)
    B = bore * GROW_Z
    k = (var["muzzle"] - var["canon"]) / GOM_FH_LEN
    for v, y0 in fh_y.items():
        if v.is_valid:
            # a little fatter than GoM's (the photo's 21 mm against GoM's 5.56 birdcage)
            x, z = v.co.x / R, sr.gz(v)
            v.co.x = x * 1.08 * R
            v.co.z = -(B + (z - B) * 1.08) * R
            v.co.y = (var["canon"] + (y0 - GOM_FH) * k) * R
    old = set(bm.faces)
    extra = var["extra"]
    # GoM's flat-top rail carried on to the receiver's rear (H&K's upper is railed full length)
    mk.prism(bm, uv, black, [(rail_x, rail_z0), (rail_x, rail_mid), (rail_x - 1.0, rail_top),
                             (-rail_x + 1.0, rail_top), (-rail_x, rail_mid), (-rail_x, rail_z0)],
             rail_y0, hk.RAIL_REAR + 0.5)
    # the barrel: inside the rail system, the thick part to the step, the thin part to the flash hider
    recv_front = ymap(hk.RECV_FRONT)
    sr.lathe(bm, uv, steel, B, [(recv_front - 10.0, BARREL_R[0]), (var["step"], BARREL_R[0]),
                                (var["step"] + 2.0, BARREL_R[1]), (var["canon"] + 1.0, BARREL_R[1]),
                                (var["canon"] + 1.0, 3.0)], seg=20)
    # the rail system: a chamfered box, a slightly larger front cap, a collar at the receiver
    rail_bot = B - RAIL_BOT_UNDER_BORE
    tbase = rail_top - B - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    bbase = B - rail_bot - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    za, zb = B - bbase, B + tbase
    y0, y1 = recv_front, var["hg_end"]
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF, HG_HALF, za, zb, 8.0), y0 + 4.0, y1 - 7.0)
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF - 1.0, HG_HALF + 1.0, za - 1.0, zb, 9.0), y1 - 7.0, y1)
    mk.prism(bm, uv, black, mk.chamfered(-HG_HALF + 2.0, HG_HALF - 2.0, za + 2.0, zb, 7.0), y0, y0 + 4.0)
    side_h = B + SIDE_H
    mk.rail(bm, uv, black, y0, y1, "top", B, tbase, tbase + mk.RAIL_BASE[1])
    mk.rail(bm, uv, black, BOTTOM_REAR, var["bottom_front"], "bottom", B, bbase, bbase + mk.RAIL_BASE[1])
    for side in ("left", "right"):
        mk.rail(bm, uv, black, SIDE_REAR, var["side_front"], side, side_h, HG_HALF, HG_HALF + mk.RAIL_BASE[1])
    # the slots over and under the side rails (the Sniper: the photo's front group moved forward, the long slot kept
    # behind it), the QD sling cup at the front, the cover's two screws low at the rear
    slots = [((a + extra, b + extra), row) for (a, b), row in SLOTS16]
    if extra:
        slots += [(SLOTS16[2][0], 0), (SLOTS16[4][0], 1)]
    for s in (-1, 1):
        for (a, b), row in slots:
            zc = B + SLOT_ROWS[row]
            hk.stadium(bm, uv, hk.DARK, s * HG_HALF, min(a, b), max(a, b), zc - 2.0, zc + 2.0)
        qy, qz = QD16[0] + extra, B + QD16[1]
        sr.lathe_x(bm, uv, black, (s * HG_HALF, qy, qz), [(0.0, 6.5), (s * 1.8, 6.5), (s * 1.8, 4.2)])
        sr.lathe_x(bm, uv, hk.DARK, (s * (HG_HALF + 1.0), qy, qz), [(0.0, 4.0), (s * 1.0, 4.0)])
        for sy, sz in SCREWS:
            sr.lathe_x(bm, uv, hk.DARK, (s * HG_HALF, sy, B + sz), [(0.0, 2.2), (s * 0.6, 2.2)], seg=10)
    # the gas block (the front sight's base), round the barrel ahead of the rail system's cap
    g0, g1 = var["gas"]
    btop, bbot = rail_top + FRONT_BASE, B - 22.0
    sr.box(bm, uv, black, (0.0, (g0 + g1) / 2.0, (btop + bbot) / 2.0), (26.0, g1 - g0, btop - bbot))
    # H&K's grip (the HK416's traced grip, at this bore)
    rows = [(B + (hk.BORE_PX - y) / hk.PX, hk.py(xf), hk.py(xb)) for y, xf, xb in hk.GRIP_PX]
    hk.loft_z(bm, uv, black, sorted(rows, key=lambda r: -r[0]), hk.GRIP_HALF, 5.0)
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in old])
    heights = {"base": rail_top + REAR[2], "top": rail_top + REAR[3]}
    sight = dict(rail_top=rail_top, btop=btop, top=rail_top + FRONT_TOP, fy=(g0 + g1) / 2.0, fl=FRONT_LEN,
                 rear=(REAR[0], REAR[1], "base", "top", REAR[4]), rz=lambda key: heights[key])
    marks = hk.build_markings(bm, pivot, body) if keep_parts else None
    out = []
    for suffix, front_up, rear_up in SIGHT_STATES:
        b2 = bm.copy()
        uv2 = b2.loops.layers.uv.active
        old2 = set(b2.faces)
        hk.add_sights(b2, uv2, black, sight, front_up, rear_up)
        bmesh.ops.recalc_face_normals(b2, faces=[f for f in b2.faces if f not in old2])
        me = bpy.data.meshes.new(name + suffix)
        b2.to_mesh(me)
        b2.free()
        for mat in body.data.materials:
            me.materials.append(mat)
        o = bpy.data.objects.new(name + suffix, me)
        o.matrix_world = body.matrix_world.copy()
        bpy.context.scene.collection.objects.link(o)
        out.append(o)
    bm.free()
    if keep_parts:
        for old_name, new in (("AR15_BOLT", "HK417_BOLT"), ("AR15_CHARGING_HANDLE", "HK417_CHARGING_HANDLE")):
            b2 = bmesh.new()
            b2.from_mesh(objs[old_name].data)
            grow_mesh(b2)
            b2.to_mesh(objs[old_name].data)
            b2.free()
            objs[old_name].name = objs[old_name].data.name = new
            out.append(objs[old_name])
        st = hk.build_stock(B, black, body)
        st.name = st.data.name = "HK417_STOCK"
        marks.name = marks.data.name = "HK417_MARKINGS"
        out += [st, marks]
    keep = set(out)
    for o in set(bpy.data.objects) - before:
        if o not in keep:
            bpy.data.objects.remove(o)
    faces = {"top": rail_top, "bottom": rail_bot, "side": HG_HALF + mk.RAIL_BASE[1] + mk.RAIL_TOOTH[1], "bore": B,
             "side_h": side_h}
    return out, faces


# --- magazines ---------------------------------------------------------------------------------------------------

def build_mag(name, front, rear, top_z, plate_h, to_local):
    """An H&K HK417 magazine from its front and rear edges (gun mm (y, z), top to bottom), straight up into the well to
    top_z: smoke-grey polymer sections (quads only), a black base plate under base_z, raised window frames on both
    sides (dark), the feed lips' dark top; the plate reaches plate_h under the body's lowest corner."""
    n = 14
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")

    def v(x, y, z):
        return bm.verts.new(to_local(x, y, z))

    def resample(pts, k):
        return [(pts[0][0] + (pts[1][0] - pts[0][0]) * i / (k - 1), pts[0][1] + (pts[1][1] - pts[0][1]) * i / (k - 1))
                for i in range(k)]
    F = [(front[0][0], top_z)] + resample(front, n)
    Bk = [(rear[0][0], top_z)] + resample(rear, n)
    ch = 2.0
    half = MAG_HALF

    def ring(yf, zf, yb, zb, h):
        dy, dz = yb - yf, zb - zf
        L = math.hypot(dy, dz)
        ux, uz = dy / L, dz / L
        pts = [(-h + ch, 0.0), (h - ch, 0.0), (h, ch), (h, L - ch), (h - ch, L), (-h + ch, L), (-h, L - ch), (-h, ch)]
        return [v(x, yf + ux * t, zf + uz * t) for x, t in pts]
    rings = [ring(yf, zf, yb, zb, half) for (yf, zf), (yb, zb) in zip(F, Bk)]
    faces = []
    m = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[k], b[k], b[(k + 1) % m], a[(k + 1) % m])) for k in range(m)]
    top = bm.faces.new(rings[0])
    faces.append(bm.faces.new(list(reversed(rings[-1]))))
    sr.paint(uv, MAG_PATCH["SMOKE"], faces)
    sr.paint(uv, MAG_PATCH["DARK"], [top])
    # the base plate: a wider black slab under the body's end, square to its slanted bottom edge (the magazine is
    # raked), a little longer than the body front and back
    (yf, zf), (yb, zb) = F[-1], Bk[-1]
    ey, ez = yb - yf, zb - zf
    L = math.hypot(ey, ez)
    ey, ez = ey / L, ez / L
    ny, nz = ez, -ey                       # the edge's normal, pointing down
    if nz > 0:
        ny, nz = -ny, -nz
    corners = []
    for t, lift in ((-1.5, 3.0), (L + 1.5, 3.0), (L + 1.5, -plate_h), (-1.5, -plate_h)):
        corners.append((yf + ey * t - ny * lift, zf + ez * t - nz * lift))
    xs = (-half - 1.2, half + 1.2)
    vs = [[v(x, y, z) for (y, z) in corners] for x in xs]
    a0, a1 = vs
    pf = [bm.faces.new((a0[k], a0[(k + 1) % 4], a1[(k + 1) % 4], a1[k])) for k in range(4)]
    pf += [bm.faces.new(a0), bm.faces.new(list(reversed(a1)))]
    sr.paint(uv, MAG_PATCH["DARK"], pf)
    # window frames: three raised bars across each side, and one along the front third
    for s in (-1, 1):
        x = s * (half + 0.2)
        for fz in (0.30, 0.48, 0.66):
            i = int(fz * n) + 1
            (y0, z0), (y1, z1) = F[i], Bk[i]
            ya, yb2 = y0 + (y1 - y0) * 0.12, y0 + (y1 - y0) * 0.78
            za_, zb_ = z0 + (z1 - z0) * 0.12, z0 + (z1 - z0) * 0.78
            quad = [v(x, ya, za_ + 0.9), v(x, yb2, zb_ + 0.9), v(x, yb2, zb_ - 0.9), v(x, ya, za_ - 0.9)]
            sr.paint(uv, MAG_PATCH["DARK"], [bm.faces.new(quad if s > 0 else list(reversed(quad)))])
        i0, i1 = 2, int(0.70 * n) + 1
        ya, za_ = F[i0][0] + (Bk[i0][0] - F[i0][0]) * 0.35, F[i0][1] + (Bk[i0][1] - F[i0][1]) * 0.35
        yb2, zb_ = F[i1][0] + (Bk[i1][0] - F[i1][0]) * 0.35, F[i1][1] + (Bk[i1][1] - F[i1][1]) * 0.35
        quad = [v(x, ya - 0.9, za_), v(x, ya + 0.9, za_), v(x, yb2 + 0.9, zb_), v(x, yb2 - 0.9, zb_)]
        sr.paint(uv, MAG_PATCH["DARK"], [bm.faces.new(quad if s > 0 else list(reversed(quad)))])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def build_magazines(B, mag_point):
    """H&K's 10 and 20-round magazines in the frame GoM's STANAG uses at the gun's `magazine` point."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/magazines/assault_rifles.fbx")
    stanag = next(o for o in set(bpy.data.objects) - before if o.name.startswith("556x45Magazine30_STANAG"))
    ox, oy, oz = mag_point["offset"]
    top_z = max((-v.co.z + oz) / R for v in stanag.data.vertices)
    like = stanag.matrix_world.copy()
    for o in set(bpy.data.objects) - before:
        bpy.data.objects.remove(o)

    def to_local(x, y, z):
        return (x * R - ox, y * R - oy, -(z * R - oz))

    def conv(q):
        return py(q[0]), B + bh(q[1])
    F10, B10 = [conv(q) for q in MAG10_FRONT], [conv(q) for q in MAG10_REAR]
    plate = 10.0                                                 # the base plate's thickness (the photo's 13 at the
                                                                 # rear corner, less its slant)

    def longer(edge, d):
        (y0, z0), (y1, z1) = edge
        L = math.hypot(y1 - y0, z1 - z0)
        return [(y0, z0), (y1 + (y1 - y0) / L * d, z1 + (z1 - z0) / L * d)]
    mags = []
    for rds, extra in ((10, 0.0), (20, MAG20_EXTRA)):
        F, Bk = longer(F10, extra), longer(B10, extra)
        o = build_mag("762x51Magazine%d_HK417" % rds, F, Bk, top_z, plate, to_local)
        o.matrix_world = like
        mags.append(o)
        print("magazine", rds, "front", [tuple(round(c, 1) for c in p) for p in F], "plate", round(plate, 1))
    return mags


def g(v):
    return round(v * R, 4) + 0.0


def points(var, f):
    gom = sr.gom_points()
    B = f["bore"]
    pts = {}
    for k in ("magazine", "bolt_fired", "charging_handle_open"):
        x, y, z = (c / R for c in gom[k]["offset"])
        pts[k] = {"offset": [g(x * GROW_X), g(ymap(y)) if k == "magazine" else g(y), g(z * GROW_Z)],
                  "rotate": gom[k]["rotate"]}
    pts["world"] = gom["world"]
    e = var["extra"]
    pts.update({
        "muzzle": {"offset": [0.0, g(var["muzzle"]), g(B)], "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": [0.0, g(var["canon"]), g(B)], "rotate": [0.0, 0.0, 0.0]},
        "stock": {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]},
        "stock_folded": {"offset": [0.0, g(hk.STOCK_TRAVEL), 0.0], "rotate": [0.0, 0.0, 0.0]},
        "scope": {"offset": [0.0, g(SCOPE_Y), round(g(f["top"]) - 0.0032, 4)], "rotate": [0.0, 0.0, 0.0]},
        "foregrip": {"offset": [0.0, g(390.0 + e), round(g(f["bottom"]) + 0.003, 4)], "rotate": [0.0, 0.0, 0.0]},
        "bipod": {"offset": [0.0, g(435.0 + e), round(g(f["bottom"]) + 0.003 - 0.0044, 4)], "rotate": [0.0, 0.0, 0.0]},
        "light_left": {"offset": [round(g(f["side"]) + 0.0007, 4), g(420.0 + e), g(f["side_h"])],
                       "rotate": [0.0, 0.0, 0.0]},
        "laser_right": {"offset": [round(-g(f["side"]) - 0.0018, 4), g(420.0 + e), round(g(f["side_h"]) - 0.0008, 4)],
                        "rotate": [0.0, 0.0, 0.0]},
    })
    pts["_extras"] = {"bore_mm": round(B, 2), "rail_faces_mm": {k: round(v, 2) for k, v in f.items()},
                      "handguard_mm": [round(ymap(hk.RECV_FRONT), 1), round(var["hg_end"], 1)],
                      "canon_mm": round(var["canon"], 1), "muzzle_mm": round(var["muzzle"], 1), "k": R}
    return pts


def main():
    if sr.GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    allpts, objs = {}, []
    for i, (name, var) in enumerate(VARIANTS.items()):
        out, f = build_gun(name, var, keep_parts=(i == 0))
        objs += out
        allpts[name] = points(var, f)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT_GUN), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT_GUN, use_selection=True, object_types={'MESH'})
    print("wrote", OUT_GUN, sorted(o.name for o in objs))
    mags = build_magazines(allpts["HK417"]["_extras"]["bore_mm"], allpts["HK417"]["magazine"])
    bpy.ops.object.select_all(action='DESELECT')
    for o in mags:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT_MAGS), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT_MAGS, use_selection=True, object_types={'MESH'})
    print("wrote", OUT_MAGS, [o.name for o in mags])
    with open(POINTS, "w") as fh:
        json.dump(allpts, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS, json.dumps({k: v["_extras"] for k, v in allpts.items()}))


if __name__ == "__main__":
    main()
