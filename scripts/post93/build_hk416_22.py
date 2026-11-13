"""The two H&K HK416 .22 LR pistols and their magazines, from Guns of Marz's AR15 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/post93/build_hk416_22.py

User, 2026-11-13 (docs/post93_design.md "H&K HK416 .22 LR pistols"): both generations, held like pistols, Auto and
Single, named by their rails:
- HK416QR22 "HK416 .22 Quad Rail Pistol": Carl Walther's (about 2009/10-2018), black, a short four-sided rail, the
  barrel inside a long round shroud (an integral suppressor in game, user's choice), H&K-style hooded front sight on
  the rail's front and rotary diopter rear;
- HK416ML22 "HK416 .22 M-LOK Pistol": Umarex's for H&K USA (2019-), HK bronze, the HK416 A5-style M-LOK handguard,
  polymer flip-up sights, 4-prong flash hider.
Both: no stock and no buffer tube (a round end cap where the tube would start), H&K's grip, the HK416's selector
labels, H&K's polymer .22 magazines (10 straight, 20 curved, 30 long curved).

References (references/hk416_22/, SOURCES.txt; gathered before modelling): the measuring photos are right sides,
mirrored (muzzle left) and resized to 1800 px wide: gen1/bing_133.jpg (Walther, 3000 px) and gen2/bing_037.jpg
(HK bronze, 4896 px). Both map to GoM's AR15 receiver as the HK416's photo does: the magazine well's front face at
206.7 mm ahead of the grip origin (the HK416 photo's x 710), and its scale from the run from that face to the trigger
guard's opening (71 mm on the HK416), 3.72 / 3.66 px a mm; the trigger opening (56 mm), the H&K grip (38.7 mm deep),
the upper's front (218.5) and the barrels (9" / 8.5" from the bolt face) all agree with it. (H&K's 425 mm / Walther's
17.2" overall lengths are 6-13 % short of what the photos give at that scale: measured without the flash hider or the
end cap, it seems.) Heights on the rail system and the sights are measured from the receiver's flat top (GoM's
receiver sits lower over the bore than the real one), the rest from the bore, as on the HK416.

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_HK416QR22.fbx   HK416QR22_BODY (sights up), _BODY_RD (the rear off:
        any red dot), _BODY_FD (both off: a magnified scope), HK416QR22_BOLT, _CHARGING_HANDLE, _MARKINGS
    P/models_X/weapons/firearms/GunsOfTienPost93_HK416ML22.fbx   HK416ML22_BODY (sights up), _BODY_RD (rear folded),
        _BODY_FD (both folded), _BODY_RDX / _BODY_FDX (rear off: the Kobra, Elcan, TR06X), _BOLT, _CHARGING_HANDLE,
        _MARKINGS
    P/models_X/weapons/magazines/GunsOfTienPost93_HK416_22_magazines.fbx   22LRMagazine10_HK416 / 20 / 30
    scripts/post93/hk416_22_points.json
The guns' nodes are exported turned (held like a pistol, the Vector SDP's way); the magazines upright (the
turned `magazine` point turns them). The QR22 keeps GoM's AR15 texture; the ML22
body uses textures/weapons/GunsOfTienPost93/HK416ML22.png (make_hk416_22_art.py: GoM's AR15 texture in its top-left
quarter, the same in HK bronze in its top-right; bronze faces take the right one); the bolt and charging handle keep
GoM's AR15 texture; the magazines HK416_22_MAG.png.
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import build_sr25 as sr  # noqa: E402
import build_mk11 as mk  # noqa: E402
import build_hk416 as hk  # noqa: E402

R = sr.R
P93 = hk.P93
FIRE = os.path.join(P93, "models_X/weapons/firearms")
OUT = {"QR22": os.path.join(FIRE, "GunsOfTienPost93_HK416QR22.fbx"),
       "ML22": os.path.join(FIRE, "GunsOfTienPost93_HK416ML22.fbx")}
OUT_MAGS = os.path.join(P93, "models_X/weapons/magazines/GunsOfTienPost93_HK416_22_magazines.fbx")
POINTS = os.path.join(HERE, "hk416_22_points.json")

MW_MM = 206.7                       # GoM's magazine well front face (mm ahead of the grip origin)
# per photo: px a mm, the well's front face (px), the bore, the rail system's top and bottom (photo y px)
PH = {"QR22": dict(px=3.72, mw=930.0, bore=330.0, top=195.0, bot=450.0),
      "ML22": dict(px=3.66, mw=995.0, bore=379.0, top=240.0, bot=487.0)}
RECV_FRONT = hk.RECV_FRONT          # 218.5: GoM's upper receiver's front
SCOPE_Y = 150.0                     # GoM's optics over the receiver (the HK416's place; clear of both rear sights)
HG_HALF = {"QR22": 23.0, "ML22": 25.0}
DARK = hk.DARK
MAG_PATCH = {"GREY": (0.06, 0.1, 0.44, 0.9), "DARK": (0.56, 0.1, 0.94, 0.9)}

# sight states: name suffix, front (True up / False folded / None off), rear (the same)
STATES = {"QR22": [("", True, True), ("_RD", True, None), ("_FD", None, None)],
          "ML22": [("", True, True), ("_RD", True, False), ("_FD", False, False), ("_RDX", True, None),
                   ("_FDX", False, None)]}


def py(gen, x):
    """Photo x (px, the mirrored 1800 px photo) to mm ahead of the grip origin."""
    p = PH[gen]
    return MW_MM + (p["mw"] - x) / p["px"]


class Heights:
    """Photo heights (px) to mm: on the rail system / sights from the receiver's flat top (rz), else from the bore."""

    def __init__(self, gen, B, rail_top):
        self.p, self.B, self.rail_top = PH[gen], B, rail_top
        self.hb = B - (self.p["bot"] - self.p["bore"]) / self.p["px"]

    def rz(self, ypx):
        p = self.p
        f = (ypx - p["top"]) / (p["bot"] - p["top"])
        return self.rail_top - f * (self.rail_top - self.hb)

    def bz(self, ypx):
        return self.B + (self.p["bore"] - ypx) / self.p["px"]

    def over_rail(self, ypx):
        """Height over the rail top in real mm (the sights stand on the rail: no compression)."""
        return self.rail_top + (self.p["top"] - ypx) / self.p["px"]


def arc_prism(bm, uv, patch, cz, y0, y1, r_in, r_out, a0, a1, seg=4):
    """A curved bar along y about the bore: the ring between r_in and r_out from angle a0 to a1 (radians, 0 = the
    gun's left, +x), quads only (no concave caps)."""
    def ring(y):
        out = []
        for i in range(seg + 1):
            a = a0 + (a1 - a0) * i / seg
            out.append((r_out * math.cos(a), cz + r_out * math.sin(a)))
        for i in range(seg, -1, -1):
            a = a0 + (a1 - a0) * i / seg
            out.append((r_in * math.cos(a), cz + r_in * math.sin(a)))
        return [bm.verts.new((x * R, y * R, -z * R)) for x, z in out]
    a, b = ring(y0), ring(y1)
    n = len(a)
    faces = [bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
    m = seg + 1
    for k in range(seg):                      # the ends, as quads between the outer and inner arcs
        o, i = k, n - 1 - k
        faces.append(bm.faces.new((a[o + 1], a[o], a[i], a[i - 1])))
        faces.append(bm.faces.new((b[o], b[o + 1], b[i - 1], b[i])))
    sr.paint(uv, patch, faces)
    return m


def import_ar15():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/firearms/AR15.fbx")
    return {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}, before


def receiver(gen):
    """GoM's AR15 receiver, everything ahead of it, its stock, buffer tube, end plate and A2 grip gone, the flat-top
    rail carried to the rear, the selector mirrored onto the right, H&K's grip. Returns the bmesh and what the gun's
    own parts need."""
    objs, before = import_ar15()
    body = objs["AR15_BODY"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv = bm.loops.layers.uv.active
    bronze = bm.faces.layers.int.new("bronze")
    comps = sr.islands(bm)

    def ymin(c):
        return min(sr.gy(v) for v in c)

    def ymax(c):
        return max(sr.gy(v) for v in c)
    ahead = [c for c in comps if ymin(c) >= hk.CUT]
    barrel = max((c for c in ahead if max(v.co.x for v in c) / R < 12.0), key=lambda c: ymax(c) - ymin(c))
    guard = max(ahead, key=lambda c: max(abs(v.co.x) for v in c))
    zs = [sr.gz(v) for v in barrel]
    B = (min(zs) + max(zs)) / 2.0
    steel, black = sr.uv_patch(bm, uv, barrel), sr.uv_patch(bm, uv, guard)
    behind = [c for c in comps if ymin(c) < -30.0]                         # stock, buffer tube
    endplate = [c for c in comps if ymin(c) > 5.0 and ymax(c) < 13.5]
    selector = [c for c in comps if min(v.co.x for v in c) / R > 13.0 and ymin(c) > 45.0 and ymax(c) < 90.0
                and min(sr.gz(v) for v in c) > -5.0 and max(sr.gz(v) for v in c) < 16.0]
    boss = min(selector, key=lambda c: ymax(c))
    pivot = ((ymin(boss) + ymax(boss)) / 2.0, (min(sr.gz(v) for v in boss) + max(sr.gz(v) for v in boss)) / 2.0)
    grip = [c for c in comps if min(sr.gz(v) for v in c) < hk.GRIP_CUT and c not in behind]
    top_rail = [c for c in comps if c not in ahead and ymin(c) > 20.0 and ymax(c) > 200.0
                and min(sr.gz(v) for v in c) > 50.0]
    rail_top = max(sr.gz(v) for c in top_rail for v in c if sr.gy(v) > hk.RAIL_REAR + 1.0)
    rear_sight = [v for c in top_rail for v in c if sr.gy(v) < hk.RAIL_REAR - 0.5]
    rail_x = max(v.co.x for c in top_rail for v in c) / R
    rail_y0 = min(sr.gy(v) for c in top_rail for v in c)
    rail_z0 = min(sr.gz(v) for c in top_rail for v in c)
    rail_mid = min(sr.gz(v) for c in top_rail for v in c if sr.gy(v) > hk.RAIL_REAR + 1.0 and sr.gz(v) > rail_z0 + 1.0)
    # the gen-2 finish: the receivers and the flat top in bronze (GoM's big islands: upper, lower, magazine well, rail)
    big = [c for c in comps if c not in ahead + behind + grip + endplate and len(c) >= 80
           and (max(sr.gz(v) for v in c) - min(sr.gz(v) for v in c)) > 18.0 and ymax(c) - ymin(c) > 90.0]
    for c in big:
        for f in {f for v in c for f in v.link_faces}:
            f[bronze] = 1
    bmesh.ops.delete(bm, geom=[v for c in ahead + behind + grip + endplate for v in c] + rear_sight, context='VERTS')
    old = set(bm.faces)
    for c in selector:
        hk.mirror_island(bm, uv, c)
    before_rail = set(bm.faces)
    mk.prism(bm, uv, black, [(rail_x, rail_z0), (rail_x, rail_mid), (rail_x - 1.0, rail_top), (-rail_x + 1.0, rail_top),
                             (-rail_x, rail_mid), (-rail_x, rail_z0)], rail_y0, hk.RAIL_REAR + 0.5)
    for f in set(bm.faces) - before_rail:
        f[bronze] = 1
    # H&K's grip (the HK416's traced outline: the same grip on the same receiver)
    rows = [(B + (hk.BORE_PX - y) / hk.PX, hk.py(xf), hk.py(xb)) for y, xf, xb in hk.GRIP_PX]
    hk.loft_z(bm, uv, black, sorted(rows, key=lambda r: -r[0]), hk.GRIP_HALF, 5.0)
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in old])
    info = dict(B=B, rail_top=rail_top, black=black, steel=steel, pivot=pivot, body=body, objs=objs, before=before,
                bronze=bronze)
    return bm, uv, info


def new_faces(bm, before):
    return [f for f in bm.faces if f not in before]


def end_cap(bm, uv, black, cz, r, y_front, y_rear, ring):
    """The round cap where an AR's buffer tube would start: a body, a rounded rear and a knurled ring."""
    sr.lathe(bm, uv, black, cz, [(y_rear, r * 0.72), (y_rear + 1.6, r * 0.93), (y_rear + 3.5, r),
                                 (y_front, r), (y_front, r * 0.8)], seg=24)
    sr.ring_ribbed(bm, uv, black, cz, ring[0], ring[1], r + 0.6, rib=0.9, seg=36)


def build_qr22(bm, uv, info):
    """Walther's: the short quad rail, the shroud, the end cap with its sling ring."""
    g = "QR22"
    B, rail_top, black, steel = info["B"], info["rail_top"], info["black"], info["steel"]
    h = Heights(g, B, rail_top)
    HG = HG_HALF[g]
    y_end = py(g, 315.0)                                  # the rail system's front (372.0)
    y_cap = py(g, 305.0)                                  # ... its front plate (374.7)
    muzzle = py(g, 47.0)                                  # the shroud's front (444.1)
    lip = py(g, 80.0)
    # the shroud round the barrel, from inside the rail system to the muzzle, the bore's dark mouth
    r_sh, r_lip = 136.0 / 2 / PH[g]["px"], 122.0 / 2 / PH[g]["px"]
    sr.lathe(bm, uv, black, B, [(RECV_FRONT + 4.0, r_sh), (lip - 0.8, r_sh), (lip + 0.8, r_lip), (muzzle - 1.2, r_lip),
                                (muzzle, r_lip - 1.2)], seg=28)
    sr.lathe(bm, uv, DARK, B, [(muzzle - 1.0, 3.6), (muzzle + 0.05, 3.6)], seg=12)
    # the rail box: rails at 12, 3, 6 and 9 o'clock, a front plate, a collar at the receiver
    tbase = rail_top - B - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    hb = h.hb
    bbase = B - hb - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    za, zb = B - bbase, B + tbase
    y0 = RECV_FRONT
    mk.prism(bm, uv, black, mk.chamfered(-HG, HG, za, zb, 8.0), y0 + 4.0, y_end)
    mk.prism(bm, uv, black, mk.chamfered(-HG - 0.6, HG + 0.6, za - 0.6, zb, 9.0), y_end, y_cap)
    mk.prism(bm, uv, black, mk.chamfered(-HG + 2.0, HG - 2.0, za + 2.0, zb, 7.0), y0, y0 + 4.0)
    side_h = h.rz(337.0)
    mk.rail(bm, uv, black, y0, y_cap, "top", B, tbase, tbase + mk.RAIL_BASE[1])
    mk.rail(bm, uv, black, py(g, 880.0), py(g, 330.0), "bottom", B, bbase, bbase + mk.RAIL_BASE[1])
    for side in ("left", "right"):
        mk.rail(bm, uv, black, py(g, 860.0), py(g, 370.0), side, side_h, HG, HG + mk.RAIL_BASE[1])
    for s in (-1, 1):
        for (x0, x1), (r0, r1) in (((355.0, 490.0), (280.0, 290.0)), ((545.0, 677.0), (280.0, 290.0)),
                                   ((360.0, 490.0), (380.0, 390.0)), ((545.0, 680.0), (380.0, 390.0))):
            hk.stadium(bm, uv, DARK, s * HG, py(g, x1), py(g, x0), h.rz(r1), h.rz(r0))
        # the rail's fastening bolt (a hex head low on each side)
        yb, zc = (py(g, 805.0) + py(g, 745.0)) / 2.0, h.rz(410.0)
        sr.lathe_x(bm, uv, black, (s * HG, yb, zc), [(0.0, 7.0), (s * 1.6, 7.0)], seg=6)
        sr.lathe_x(bm, uv, DARK, (s * (HG + 1.6), yb, zc), [(0.0, 3.2), (s * 0.5, 3.2)], seg=6)
    # the end cap (photo: from the lower's rear back 27 mm, its top 8 mm under the rail's, 36 mm across) and the sling
    # ring under it
    r_cap = 135.0 / 2 / PH[g]["px"]
    cz = rail_top - (225.0 - PH[g]["top"]) / PH[g]["px"] - r_cap
    end_cap(bm, uv, black, cz, r_cap, 11.0, -16.0, (-9.0, -14.5))
    ring_z = rail_top - (382.0 - PH[g]["top"]) / PH[g]["px"]
    sr.lathe_x(bm, uv, black, (-1.2, -4.0, ring_z), [(0.0, 5.0), (2.4, 5.0)], seg=14)
    sr.lathe_x(bm, uv, DARK, (-1.4, -4.0, ring_z), [(0.0, 2.6), (2.8, 2.6)], seg=10)
    sr.box(bm, uv, black, (0.0, -1.0, (ring_z + cz - r_cap * 0.6) / 2.0), (2.4, 5.0, cz - r_cap * 0.6 - ring_z))
    return dict(muzzle=muzzle, canon=y_end, top=rail_top, side=HG + mk.RAIL_BASE[1] + mk.RAIL_TOOTH[1],
                side_h=side_h, bottom=hb, h=h)


def build_ml22(bm, uv, info):
    """H&K USA's: the A5-style M-LOK handguard, the barrel and the 4-prong flash hider, the end cap. Returns the
    faces to paint bronze too."""
    g = "ML22"
    B, rail_top, black, steel = info["B"], info["rail_top"], info["black"], info["steel"]
    h = Heights(g, B, rail_top)
    HG = HG_HALF[g]
    hg_end = py(g, 268.0)                                 # 405.3
    muzzle = py(g, 20.0)                                  # 473.1
    collar = (py(g, 255.0), py(g, 170.0))                 # 408.9 .. 432.1
    px = PH[g]["px"]
    r_fh, r_bar = 78.0 / 2 / px, 55.0 / 2 / px
    # the barrel inside the handguard and out of it, the flash hider's collar and its four prongs
    sr.lathe(bm, uv, steel, B, [(RECV_FRONT - 5.0, r_bar), (collar[0] + 2.0, r_bar)], seg=20)
    sr.lathe(bm, uv, black, B, [(collar[0], r_fh - 0.6), (collar[0] + 1.0, r_fh), (collar[1], r_fh),
                                (collar[1], r_fh - 1.6)], seg=24)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        arc_prism(bm, uv, black, B, collar[1] - 0.5, muzzle, 5.2, r_fh, a - 0.52, a + 0.52, seg=3)
    sr.lathe(bm, uv, DARK, B, [(collar[1] - 0.6, 5.0), (collar[1] - 0.3, 5.0)], seg=12)
    # the handguard: a chamfered box, its top rail flush with the receiver's, a collar at the receiver
    before = set(bm.faces)
    tbase = rail_top - B - mk.RAIL_TOOTH[1] - mk.RAIL_BASE[1]
    za, zb = h.hb, B + tbase
    y0 = RECV_FRONT
    mk.prism(bm, uv, black, mk.chamfered(-HG, HG, za, zb, 10.0), y0 + 4.0, hg_end)
    mk.prism(bm, uv, black, mk.chamfered(-HG + 2.0, HG - 2.0, za + 2.0, zb, 9.0), y0, y0 + 4.0)
    mk.rail(bm, uv, black, y0, hg_end, "top", B, tbase, tbase + mk.RAIL_BASE[1])
    # the round QD socket's boss at the rear of each side
    qy, qz = py(g, 902.0), h.rz(382.0)
    for s in (-1, 1):
        sr.lathe_x(bm, uv, black, (s * HG, qy, qz), [(0.0, 8.5), (s * 1.2, 8.5), (s * 1.2, 7.2)], seg=16)
    bronze_faces = new_faces(bm, before)
    for s in (-1, 1):
        sr.lathe_x(bm, uv, DARK, (s * (HG + 1.2), qy, qz), [(0.0, 5.0), (s * 0.4, 5.0)], seg=12)
        # M-LOK slots: three rows, as on the photo (x px spans, y px rows)
        for (r0, r1), spans in (((322.0, 342.0), ((300, 360), (395, 515), (550, 670))),
                                ((370.0, 395.0), ((297, 420), (452, 578), (608, 731), (763, 825))),
                                ((417.0, 442.0), ((305, 358), (372, 420), (457, 512), (522, 575), (609, 666),
                                                  (674, 730)))):
            for x0, x1 in spans:
                hk.stadium(bm, uv, DARK, s * HG, py(g, x1), py(g, x0), h.rz(r1), h.rz(r0), seg=4)
        # the rail lock (a dark plate with its screw) low on the rear of each side
        ly0, ly1 = py(g, 868.0), py(g, 785.0)
        sr.box(bm, uv, DARK, (s * (HG + 0.6), (ly0 + ly1) / 2.0, (h.rz(418.0) + h.rz(482.0)) / 2.0),
               (1.6, ly1 - ly0, h.rz(418.0) - h.rz(482.0)))
        sr.lathe_x(bm, uv, black, (s * (HG + 1.4), (ly0 + ly1) / 2.0, h.rz(450.0)), [(0.0, 4.4), (s * 0.8, 4.4)],
                   seg=12)
    # the end cap: from the lower's rear back 25 mm, 31 mm across, centred 35 mm under the rail's top
    r_cap = 113.0 / 2 / px
    cz = rail_top - (312.0 - PH[g]["top"]) / px - r_cap
    end_cap(bm, uv, black, cz, r_cap, 11.0, -13.6, (-8.0, -13.0))
    return dict(muzzle=muzzle, canon=collar[0], top=rail_top, side=HG + 1.2, side_h=qz, bottom=h.hb, h=h), \
        bronze_faces


def sights_qr22(bm, uv, black, h, front, rear):
    """Walther's H&K-style sights, clamped on the rail: the hooded front post on the rail's front, the rotary
    diopter at the rear; each up or taken off (None)."""
    g = "QR22"
    rt = h.rail_top
    if front:
        b0, b1 = py(g, 488.0), py(g, 383.0)               # the clamp along the rail (325.5 .. 353.7)
        f0, f1 = py(g, 455.0), py(g, 385.0)               # the ring's ears (334.4 .. 353.2)
        top, btop = h.over_rail(57.0), rt + 5.0
        sr.box(bm, uv, black, (0.0, (b0 + b1) / 2.0, rt + 2.5), (22.0, b1 - b0, 5.0))
        fy, fl = (f0 + f1) / 2.0, f1 - f0
        for side in (-1, 1):
            sr.box(bm, uv, black, (side * 8.0, fy, (btop + top) / 2.0), (3.2, fl, top - btop))
        sr.box(bm, uv, black, (0.0, fy, (btop + top - 4.0) / 2.0), (2.6, 3.0, top - 4.0 - btop))
        sr.box(bm, uv, black, (0.0, fy, top - 1.0), (19.2, fl, 2.0))
        # the brace from the ring down to the clamp's front
        sr.box(bm, uv, black, (0.0, (b0 + f0) / 2.0, btop + 4.0), (12.0, f0 - b0 + 2.0, 8.0))
    if rear:
        r0, r1 = py(g, 1470.0), py(g, 1330.0)             # the clamp (61.5 .. 99.2)
        d0, d1 = py(g, 1400.0), py(g, 1325.0)             # the drum (80.4 .. 99.5)
        zb_top = h.over_rail(150.0)
        dr = (h.over_rail(45.0) - zb_top) / 2.0
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0, (rt + zb_top) / 2.0), (24.0, r1 - r0, zb_top - rt + 1.0))
        sr.lathe_x(bm, uv, black, (-10.0, (d0 + d1) / 2.0, zb_top + dr - 0.5), [(0.0, dr), (20.0, dr)], seg=16)
        # the guards behind the drum
        g0 = py(g, 1460.0)
        sr.box(bm, uv, black, (0.0, (g0 + d0) / 2.0, zb_top + dr * 0.8), (22.0, d0 - g0, dr * 1.6))


def sights_ml22(bm, uv, black, h, front, rear):
    """H&K USA's polymer flip-ups: up, folded (False) or, for the rear, taken off (None)."""
    g = "ML22"
    rt = h.rail_top
    if front is not None:
        b0, b1 = py(g, 400.0), py(g, 312.0)               # the base (369.3 .. 393.3)
        sr.box(bm, uv, black, (0.0, (b0 + b1) / 2.0, rt + 3.0), (18.0, b1 - b0, 6.0))
        sr.lathe_x(bm, uv, black, (-8.0, py(g, 335.0), rt + 5.5), [(0.0, 4.6), (16.0, 4.6)], seg=12)
        if front:
            f0, f1 = py(g, 450.0), py(g, 400.0)           # the frame (355.6 .. 369.3)
            top = h.over_rail(97.0)
            fy, fl = (f0 + f1) / 2.0, f1 - f0
            for side in (-1, 1):
                sr.box(bm, uv, black, (side * 6.2, fy, (rt + 4.0 + top) / 2.0), (3.0, fl, top - rt - 4.0))
            sr.box(bm, uv, black, (0.0, fy, (rt + 4.0 + top - 5.0) / 2.0), (2.4, 2.6, top - 5.0 - rt - 4.0))
            sr.box(bm, uv, black, (0.0, fy, rt + 6.0), (15.4, fl, 4.0))
        else:
            # folded back onto the rail behind its base
            sr.box(bm, uv, black, (0.0, b0 - 15.0, rt + 3.5), (15.4, 32.0, 7.0))
    if rear is None:
        return
    r0, r1 = py(g, 1505.0), py(g, 1330.0)                 # the base (67.4 .. 115.2)
    if rear:
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0, rt + 3.0), (18.0, r1 - r0, 6.0))
        a0, a1 = py(g, 1395.0), py(g, 1335.0)             # the aperture frame (97.6 .. 114.0)
        top = h.over_rail(88.0)
        ay, al = (a0 + a1) / 2.0, a1 - a0
        for side in (-1, 1):
            sr.box(bm, uv, black, (side * 7.0, ay, (rt + 5.0 + top) / 2.0), (3.0, al, top - rt - 5.0))
        sr.box(bm, uv, black, (0.0, ay, (rt + 5.0 + top - 6.0) / 2.0), (11.0, 2.4, top - 6.0 - rt - 5.0))
        sr.lathe_x(bm, uv, DARK, (-0.5, ay - 1.25, top - 13.0), [(0.0, 1.6), (1.0, 1.6)], seg=10)
        sr.box(bm, uv, black, (0.0, ay, rt + 7.0), (17.0, al, 4.0))
        # the windage knob on the right side
        sr.lathe_x(bm, uv, black, (-9.0, py(g, 1455.0), rt + 9.0), [(0.0, 6.0), (-5.0, 6.0), (-5.0, 4.5)], seg=14)
    else:
        # folded flat: a low block (3.5 mm over the rail, the HK416's lesson: higher goes into the optics)
        low = rt + 2.0
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0, (rt + low) / 2.0), (18.0, r1 - r0, low - rt + 1.0))
        sr.box(bm, uv, black, (0.0, (r0 + r1) / 2.0 + 3.0, low + 0.75), (16.0, r1 - r0 - 10.0, 1.5))


def remap_bronze(bm, uv, layer):
    """The ML22's texture: GoM's AR15 texture in the top-left quarter, in bronze in the top-right."""
    for f in bm.faces:
        off = 0.5 if f[layer] else 0.0
        for loop in f.loops:
            u, v = loop[uv].uv
            loop[uv].uv = (u * 0.5 + off, v * 0.5 + 0.5)


def build_gun(gen):
    bm, uv, info = receiver(gen)
    black = info["black"]
    if gen == "QR22":
        f = build_qr22(bm, uv, info)
        bronze_faces = []
    else:
        f, bronze_faces = build_ml22(bm, uv, info)
        for face in bronze_faces:
            face[info["bronze"]] = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = info["body"]
    name = "HK416" + gen
    marks = hk.build_markings(bm, info["pivot"], body)
    marks.name = marks.data.name = name + "_MARKINGS_UP"
    out = []
    for suffix, front, rear in STATES[gen]:
        b2 = bm.copy()
        uv2 = b2.loops.layers.uv.active
        old2 = set(b2.faces)
        if gen == "QR22":
            sights_qr22(b2, uv2, black, f["h"], front, rear)
        else:
            sights_ml22(b2, uv2, black, f["h"], front, rear)
        bmesh.ops.recalc_face_normals(b2, faces=[x for x in b2.faces if x not in old2])
        if gen == "ML22":
            remap_bronze(b2, uv2, b2.faces.layers.int["bronze"])
        me = bpy.data.meshes.new(name + "_BODY" + suffix + "_UP")
        b2.to_mesh(me)
        b2.free()
        o = bpy.data.objects.new(me.name, me)
        o.matrix_world = body.matrix_world.copy()
        bpy.context.scene.collection.objects.link(o)
        out.append(o)
    bm.free()
    for old_name, new in (("AR15_BOLT", "_BOLT_UP"), ("AR15_CHARGING_HANDLE", "_CHARGING_HANDLE_UP")):
        ob = info["objs"][old_name]
        ob.name = ob.data.name = name + new
        out.append(ob)
    out.append(marks)
    for o in set(bpy.data.objects) - info["before"]:
        if not o.name.startswith(name):
            bpy.data.objects.remove(o)
    return out, f, info["B"]


# --- magazines ---------------------------------------------------------------------------------------------------

def mag_outline(gen, front_px, rear_px):
    """Photo outlines (px) to gun mm (y, z): the front and rear edges from the well's bottom down."""
    p = PH[gen]

    def conv(q):
        return py(gen, q[0]), MAG_B[0] + (p["bore"] - q[1]) / p["px"]
    return [conv(q) for q in front_px], [conv(q) for q in rear_px]


MAG_B = [0.0]


def resample(pts, n):
    """n points evenly along a polyline."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out = []
    for i in range(n):
        t = d[-1] * i / (n - 1)
        k = max(j for j in range(len(d)) if d[j] <= t + 1e-9)
        k = min(k, len(pts) - 2)
        f = (t - d[k]) / max(d[k + 1] - d[k], 1e-9)
        out.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f))
    return out


def build_mag(name, front, rear, top_z, half, slot, screws, to_local):
    """A magazine from its front and rear edges (gun mm, top to bottom), straight up into the well to top_z: a
    ladder of sections across x (quads only), a dark feed slot and screws on both sides."""
    n = 18
    F = [(front[0][0], top_z)] + resample(front, n)
    Bk = [(rear[0][0], top_z)] + resample(rear, n)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")

    def v(x, y, z):
        lx, ly, lz = to_local(x, y, z)
        return bm.verts.new((lx, ly, lz))
    ch = 1.2
    rings = []
    for (yf, zf), (yb, zb) in zip(F, Bk):
        # a section across: front face chamfered, sides, rear face (y, z along the line from front to rear)
        dy, dz = yb - yf, zb - zf
        L = math.hypot(dy, dz)
        ux, uz = dy / L, dz / L
        pts = [(-half + ch, 0.0), (half - ch, 0.0), (half, ch), (half, L - ch), (half - ch, L), (-half + ch, L),
               (-half, L - ch), (-half, ch)]
        rings.append([v(x, yf + ux * t, zf + uz * t) for x, t in pts])
    faces = []
    m = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[k], b[k], b[(k + 1) % m], a[(k + 1) % m])) for k in range(m)]
    faces.append(bm.faces.new(rings[0]))
    faces.append(bm.faces.new(list(reversed(rings[-1]))))
    sr.paint(uv, MAG_PATCH["GREY"], faces)
    # the slot: a dark strip on each side along the curve at `slot[0]` of the depth, from slot[1] to slot[2] of the
    # length; the screws: dark dots at (fraction of depth, fraction of length)
    for s in (-1, 1):
        x = s * (half + 0.15)
        k0, k1 = int(slot[1] * n) + 1, int(slot[2] * n) + 1
        for k in range(k0, k1):
            (yf0, zf0), (yb0, zb0) = F[k], Bk[k]
            (yf1, zf1), (yb1, zb1) = F[k + 1], Bk[k + 1]
            ya, za = yf0 + (yb0 - yf0) * slot[0], zf0 + (zb0 - zf0) * slot[0]
            yb_, zb_ = yf1 + (yb1 - yf1) * slot[0], zf1 + (zb1 - zf1) * slot[0]
            w = 2.0
            quad = [v(x, ya - w, za), v(x, ya + w, za), v(x, yb_ + w, zb_), v(x, yb_ - w, zb_)]
            fq = bm.faces.new(quad if s > 0 else list(reversed(quad)))
            sr.paint(uv, MAG_PATCH["DARK"], [fq])
        for df, dl in screws:
            k = int(dl * n) + 1
            (yf0, zf0), (yb0, zb0) = F[k], Bk[k]
            yc, zc = yf0 + (yb0 - yf0) * df, zf0 + (zb0 - zf0) * df
            ring = [v(x, yc + 1.6 * math.cos(2 * math.pi * i / 8), zc + 1.6 * math.sin(2 * math.pi * i / 8))
                    for i in range(8)]
            fq = bm.faces.new(ring if s > 0 else list(reversed(ring)))
            sr.paint(uv, MAG_PATCH["DARK"], [fq])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def build_magazines(B, mag_point):
    """H&K's 10 / 20 / 30-round .22 magazines in the frame GoM's STANAG uses at the gun's `magazine` point."""
    MAG_B[0] = B
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{sr.GOM}/models_X/weapons/magazines/assault_rifles.fbx")
    stanag = next(o for o in set(bpy.data.objects) - before if o.name.startswith("556x45Magazine30_STANAG"))
    ox, oy, oz = mag_point["offset"]
    gun = [((v.co.x + ox) / R, (v.co.y + oy) / R, (-v.co.z + oz) / R) for v in stanag.data.vertices]
    top_z = max(p[2] for p in gun)
    half = max(abs(p[0]) for p in gun)
    print("STANAG in gun mm: top z %.1f, half width %.1f, y %.1f .. %.1f" %
          (top_z, half, min(p[1] for p in gun), max(p[1] for p in gun)))
    like = stanag.matrix_world.copy()
    for o in set(bpy.data.objects) - before:
        bpy.data.objects.remove(o)

    def to_local(x, y, z):
        return (x * R - ox, y * R - oy, -(z * R - oz))
    mags = []
    # 20: the gen-2 photo; 10: the gen-1 photo (straight); 30: the 20's edges carried on along their curves
    f20 = [(1000, 690), (992, 760), (982, 820), (968, 880), (952, 940), (938, 1000), (928, 1035)]
    b20 = [(1238, 690), (1236, 720), (1228, 780), (1215, 850), (1200, 920), (1182, 990), (1162, 1060), (1150, 1100)]
    F20, B20 = mag_outline("ML22", f20, b20)
    F10, B10 = mag_outline("QR22", [(935, 640), (935, 810)], [(1157, 640), (1157, 818)])

    def extend(pts, extra):
        # carry a curve on by `extra` mm, turning as its last stretch turns
        out = list(pts)
        (y0, z0), (y1, z1), (y2, z2) = pts[-3], pts[-2], pts[-1]
        a1 = math.atan2(z1 - z0, y1 - y0)
        a2 = math.atan2(z2 - z1, y2 - y1)
        turn = (a2 - a1)
        step = math.dist(pts[-1], pts[-2])
        a, y, z, done = a2, y2, z2, 0.0
        while done < extra:
            a += turn
            y, z = y + step * math.cos(a), z + step * math.sin(a)
            out.append((y, z))
            done += step
        return out
    F30, B30 = extend(F20, 42.0), extend(B20, 42.0)
    for n_rds, (F, Bk) in ((10, (F10, B10)), (20, (F20, B20)), (30, (F30, B30))):
        o = build_mag("22LRMagazine%d_HK416" % n_rds, F, Bk, top_z, half - 0.4,
                      (0.62, 0.08, 0.78 if n_rds > 10 else 0.6), [(0.42, 0.25), (0.42, 0.85), (0.88, 0.5)],
                      to_local)
        o.matrix_world = like
        mags.append(o)
    return mags


# --- export ------------------------------------------------------------------------------------------------------

def turned(ob, name):
    """The node held like a pistol: data x and z negated (the Vector SDP's way), the object's transform kept."""
    me = ob.data.copy()
    me.name = name
    me.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    o = bpy.data.objects.new(name, me)
    o.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(o)
    return o


def g(v):
    return round(v * R, 4) + 0.0


def points(f, B):
    gom = sr.gom_points()
    pts = {k: gom[k] for k in ("magazine", "bolt_fired", "charging_handle_open")}
    pts.update({
        "muzzle": {"offset": [0.0, g(f["muzzle"]), g(B)], "rotate": [-90.0, 0.0, -180.0]},
        "canon": {"offset": [0.0, g(f["canon"]), g(B)], "rotate": [0.0, 0.0, 0.0]},
        "scope": {"offset": [0.0, g(SCOPE_Y), round(g(f["top"]) - 0.0032, 4)], "rotate": [0.0, 0.0, 0.0]},
        "light_left": {"offset": [round(g(f["side"]) + 0.0007, 4), g(300.0), g(f["side_h"])], "rotate": [0.0, 0.0, 0.0]},
        "laser_right": {"offset": [round(-g(f["side"]) - 0.0018, 4), g(300.0), round(g(f["side_h"]) - 0.0008, 4)],
                        "rotate": [0.0, 0.0, 0.0]},
    })
    # turned (held like a pistol): x and z negated; parts modelled upright turn with -180 0 -180 (build_vector.py)
    upright = ("magazine", "scope", "light_left", "laser_right")
    out = {}
    for name, p in pts.items():
        x, y, z = p["offset"]
        out[name] = {"offset": [round(-x, 4) + 0.0, y, round(-z, 4) + 0.0],
                     "rotate": [-180.0, 0.0, -180.0] if name in upright else list(p["rotate"])}
    out["world"] = {"offset": [round(-0.025 * R / 0.00072, 4), 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}
    for name in ("rifle_back", "rifle_back_bag"):
        out[name] = {"offset": [0.0, 0.0, 0.0], "rotate": [-180.0, 0.0, -180.0]}
    out["_extras"] = {"bore_mm": round(B, 2), "muzzle_mm": round(f["muzzle"], 1), "canon_mm": round(f["canon"], 1),
                      "rail_top_mm": round(f["top"], 2), "k": R, "turned": True}
    return out


def main():
    if sr.GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    allpts = {}
    for gen in ("QR22", "ML22"):
        ups, f, B = build_gun(gen)
        allpts["HK416" + gen] = points(f, B)
        exp = [turned(o, o.name[:-3]) for o in ups]
        bpy.ops.object.select_all(action='DESELECT')
        for o in exp:
            o.select_set(True)
        bpy.ops.export_scene.fbx(filepath=OUT[gen], use_selection=True, object_types={'MESH'})
        print("wrote", OUT[gen], [o.name for o in exp])
        for o in exp:
            bpy.data.objects.remove(o)
        for o in ups:
            o.hide_set(True)
            o.name = o.name + "_done"
    # the magazines stay upright: the turned guns' `magazine` point turns them (-180 0 -180)
    mags = build_magazines(B, sr.gom_points()["magazine"])
    bpy.ops.object.select_all(action='DESELECT')
    for o in mags:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=OUT_MAGS, use_selection=True, object_types={'MESH'})
    print("wrote", OUT_MAGS, [o.name for o in mags])
    with open(POINTS, "w") as fh:
        json.dump(allpts, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS)


if __name__ == "__main__":
    main()
