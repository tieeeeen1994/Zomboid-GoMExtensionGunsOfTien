"""H&K MP7A1 models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless).

    Blender -b --factory-startup -P scripts/post93/build_mp7.py -- [--size 1024] [--samples 48]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx        MP7A1_BODY, MP7A1_BOLT, MP7A1_STOCK
    P/models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx  46x30Magazine20/30/40_MP7
    P/models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx       MP7_Suppressor, MP7_Muzzle_Mount_Device
    P/textures/weapons/GunsOfTienPost93/<name>.png                MP7A1 (256, shared by the three gun nodes),
                                                                  one 128 texture per magazine / part
    scripts/post93/mp7_points.json                                attachment points (game space)

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): game space +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, drawn at 0.72 of real size. FBX object name = node name, mesh data =
(game x, game y, -game z), rotation (90, 0, 0), scale 0.01, export_scene.fbx with its defaults.

Everything is modelled below in real millimetres around that origin (O = the grip's rear edge where it meets
the receiver) and scaled by K at the end. Textures are baked in Cycles (object position, normal, material,
two ambient occlusion distances and an edge mask from the Bevel node) and painted from those maps with numpy:
base colours, noise, AO, edge wear, grip stippling, pins, ejection port, threads and the small markings.
Fixed seeds and sample counts: the same Blender build gives the same files.
"""

import json
import math
import os
import struct
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
POINTS_JSON = os.path.join(HERE, "mp7_points.json")

K = 0.00072                       # game units per real millimetre (GoM's MP5 family: 0.72 of real size)
RAKE = math.radians(14.0)         # pistol grip / magazine rake from vertical, bottom to the rear
T = math.tan(RAKE)

# Key real dimensions (mm, origin O, +Y forward, +Z up)
BORE_Z = 38.0                     # bore axis above O
MUZZLE_Y = 280.0                  # muzzle face (415 mm overall with the stock in: butt plate rear at -135)
REAR_Y = -121.0                   # receiver rear face
BUTT_REAR = -135.0                # butt plate rear, stock collapsed
STOCK_TRAVEL = 223.0              # 638 - 415
RAIL_TOP = 72.0                   # top of the Picatinny teeth
SIDE_RAIL_Z = 36.0                # side rail centre height
SIDE_RAIL_X = 25.5                # side rail tooth faces
SIDE_RAIL_Y = (162.0, 234.0)
GRIP_DEPTH = 58.0                 # front-back, measured horizontally
MAG_TOP_Z = 30.0                  # magazine feed lips, just under the bore
CH_TRAVEL = 50.0                  # charging handle pull

MATS = ["polymer", "grip", "metal", "rail", "dark", "brass", "copper", "magpoly", "suppressor"]


def arg(name, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


BAKE = arg("--size", 1024)
SAMPLES = arg("--samples", 48)
DEBUG = arg("--debug", "")


# ==================================================================================================
# Geometry primitives (into one bmesh per node; coordinates in mm, game orientation)
# ==================================================================================================

FRAMES = {"x": (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),   # axis, profile u, profile v
          "y": (Vector((0, 1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
          "z": (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)))}


def orient_outward(bm, faces):
    """Every primitive is built with one consistent winding; flip the whole shell if it points inward (signed
    volume). bmesh.ops.recalc_face_normals gave different results from run to run inside a large bmesh."""
    vol = 0.0
    for f in faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1]))
    if vol < 0:
        bmesh.ops.reverse_faces(bm, faces=faces)


def canonical(bm):
    """The same polygons in a fixed order: vertices sorted by position, each face starting at its smallest vertex,
    faces sorted. bmesh's element order after bevels was not the same from run to run, and triangulation and UV
    unwrapping follow element order."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    key = lambda co: (round(co.x, 4), round(co.y, 4), round(co.z, 4))
    polys = []
    for f in bm.faces:
        ks = [key(v.co) for v in f.verts]
        i = ks.index(min(ks))
        polys.append((f.material_index, tuple(ks[i:] + ks[:i])))
    bm.free()
    polys.sort()
    out = bmesh.new()
    verts = {}
    for k in sorted({k for _, ks in polys for k in ks}):
        verts[k] = out.verts.new(k)
    for mat, ks in polys:
        try:
            f = out.faces.new([verts[k] for k in ks])
        except ValueError:                              # a duplicate face left by overlapping parts
            continue
        f.material_index = mat
    return out


class Builder:
    def __init__(self):
        self.bm = bmesh.new()

    def _finish(self, verts, faces, mat, bevel, xf):
        if xf is not None:
            for v in verts:
                v.co = xf @ v.co
        for f in faces:
            f.material_index = MATS.index(mat)
        orient_outward(self.bm, faces)
        if bevel > 0:
            self.bm.edges.index_update()
            edges = sorted({e for f in faces for e in f.edges}, key=lambda e: e.index)   # stable order
            res = bmesh.ops.bevel(self.bm, geom=list(verts) + edges, offset=bevel, offset_type='OFFSET',
                                  segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
            for f in res["faces"]:
                f.material_index = MATS.index(mat)
        return verts

    def prism(self, axis, profile, a0, a1, mat="polymer", bevel=0.0, xf=None):
        """Polygon `profile` [(u, v)] in the plane across `axis`, extruded from a0 to a1 along it."""
        A, U, V = FRAMES[axis]
        lo = [self.bm.verts.new(A * a0 + U * u + V * v) for u, v in profile]
        hi = [self.bm.verts.new(A * a1 + U * u + V * v) for u, v in profile]
        n = len(profile)
        faces = [self.bm.faces.new(lo[::-1]), self.bm.faces.new(hi)]
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
        return self._finish(lo + hi, faces, mat, bevel, xf)

    def box(self, x0, x1, y0, y1, z0, z1, mat="polymer", bevel=0.0, xf=None):
        return self.prism("x", [(y0, z0), (y1, z0), (y1, z1), (y0, z1)], x0, x1, mat, bevel, xf)

    def lathe(self, axis, centre, profile, seg=12, mat="metal", bevel=0.0, xf=None, phase=0.0):
        """Surface of revolution: profile [(t along axis, radius)], radius 0 = a pole; open ends are capped."""
        A, U, V = FRAMES[axis]
        c = Vector(centre)
        rings, faces = [], []
        for t, r in profile:
            if r <= 1e-9:
                rings.append([self.bm.verts.new(c + A * t)])
            else:
                rings.append([self.bm.verts.new(c + A * t + U * (r * math.cos(2 * math.pi * (k + phase) / seg))
                                                + V * (r * math.sin(2 * math.pi * (k + phase) / seg)))
                              for k in range(seg)])
        for ra, rb in zip(rings, rings[1:]):
            for k in range(seg):
                k1 = (k + 1) % seg
                if len(ra) == 1 and len(rb) == 1:
                    continue
                if len(ra) == 1:
                    faces.append(self.bm.faces.new((ra[0], rb[k1], rb[k])))
                elif len(rb) == 1:
                    faces.append(self.bm.faces.new((ra[k], ra[k1], rb[0])))
                else:
                    faces.append(self.bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
        if len(rings[0]) > 1:
            faces.append(self.bm.faces.new(rings[0][::-1]))
        if len(rings[-1]) > 1:
            faces.append(self.bm.faces.new(rings[-1]))
        verts = [v for r in rings for v in r]
        return self._finish(verts, faces, mat, bevel, xf)

    def strip(self, outer, inner, x0, x1, mat="polymer", bevel=0.0):
        """A band between two matching polylines in the YZ plane (an open loop such as a trigger guard)."""
        bm = self.bm
        o0 = [bm.verts.new((x0, y, z)) for y, z in outer]
        o1 = [bm.verts.new((x1, y, z)) for y, z in outer]
        i0 = [bm.verts.new((x0, y, z)) for y, z in inner]
        i1 = [bm.verts.new((x1, y, z)) for y, z in inner]
        faces = []
        for k in range(len(outer) - 1):
            faces.append(bm.faces.new((o0[k], o0[k + 1], i0[k + 1], i0[k])))
            faces.append(bm.faces.new((o1[k], i1[k], i1[k + 1], o1[k + 1])))
            faces.append(bm.faces.new((o0[k], o1[k], o1[k + 1], o0[k + 1])))
            faces.append(bm.faces.new((i0[k], i0[k + 1], i1[k + 1], i1[k])))
        e = len(outer) - 1
        faces.append(bm.faces.new((o0[0], i0[0], i1[0], o1[0])))
        faces.append(bm.faces.new((o1[e], i1[e], i0[e], o0[e])))
        return self._finish(o0 + o1 + i0 + i1, faces, mat, bevel, None)

    def to_object(self, name, scale_mm=True):
        bm = canonical(self.bm)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')
        s = K if scale_mm else 1.0
        for v in bm.verts:                              # game (x, y, z) mm -> FBX data (x, y, -z) game units
            v.co = Vector((v.co.x * s, v.co.y * s, -v.co.z * s))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)     # the z mirror turned every shell inside out
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in MATS:
            me.materials.append(material(m))
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(35))
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def rot_x(deg, pivot=(0, 0, 0)):
    p = Vector(pivot)
    return Matrix.Translation(p) @ Matrix.Rotation(math.radians(deg), 4, 'X') @ Matrix.Translation(-p)


# ==================================================================================================
# The MP7A1
# ==================================================================================================

def grip_lines(z):
    """Rear and front edge y of the raked pistol grip at height z (horizontal depth GRIP_DEPTH)."""
    return T * z, GRIP_DEPTH + T * z


def mag_axis():
    """Magazine top centre (feed lips) and its downward unit axis, both in mm."""
    d = Vector((0.0, -math.sin(RAKE), -math.cos(RAKE)))
    s = MAG_TOP_Z / math.cos(RAKE)
    top = Vector((0.0, GRIP_DEPTH / 2, 0.0)) - d * s
    return top, d


def picatinny(b, y0, y1, frame, base_w=15.6, base_h=4.0, tooth_w=21.2, tooth_h=6.0, pitch=10.0, tooth_len=5.2,
              mat="rail"):
    """MIL-STD-1913 style rail: a continuous base and teeth every `pitch`. frame(u, h, y) -> point, with u across
    the rail and h up from its mounting face."""
    def block(u0, u1, h0, h1, ya, yb, bev):
        pts = [frame(u, h, y) for (u, h, y) in [(u0, h0, ya), (u1, h0, ya), (u1, h1, ya), (u0, h1, ya),
                                                (u0, h0, yb), (u1, h0, yb), (u1, h1, yb), (u0, h1, yb)]]
        bm = b.bm
        v = [bm.verts.new(p) for p in pts]
        f = [bm.faces.new(q) for q in ((v[0], v[3], v[2], v[1]), (v[4], v[5], v[6], v[7]), (v[0], v[1], v[5], v[4]),
                                       (v[1], v[2], v[6], v[5]), (v[2], v[3], v[7], v[6]), (v[3], v[0], v[4], v[7]))]
        b._finish(v, f, mat, bev, None)

    block(-base_w / 2, base_w / 2, -0.5, base_h, y0, y1, 0.6)
    y = y0 + 2.0
    while y + tooth_len <= y1 - 1.0:
        block(-tooth_w / 2, tooth_w / 2, base_h - 1.0, base_h + tooth_h - 1.0 + 0.0, y, y + tooth_len, 0.0)
        y += pitch


def build_body():
    b = Builder()
    # Upper receiver (narrow, carries the top rail) and lower receiver (wider, stock rod channels).
    b.prism("x", [(REAR_Y, 30), (245, 30), (245, 52), (238, 62), (REAR_Y + 3, 62), (REAR_Y, 58)],
            -15.5, 15.5, bevel=1.6)
    b.prism("x", [(REAR_Y + 7, 0), (6, 0), (52, 0), (218, 0), (230, 5), (238, 16), (241, 30), (241, 36),
                  (REAR_Y, 36), (REAR_Y, 8)], -19.0, 19.0, bevel=1.6)
    # Rear shoulder under the charging handle and the barrel collar at the front.
    b.box(-12, 12, REAR_Y - 2.0, REAR_Y + 6, 34, 48, bevel=1.0)
    b.lathe("y", (0, 0, BORE_Z), [(238, 0), (238, 12.5), (250, 12.5), (252, 11.0), (252, 0)], seg=16,
            mat="polymer", bevel=0.0)
    # Side rail mounts, both sides.
    for s in (1, -1):
        b.box(min(s * 14, s * 19.6), max(s * 14, s * 19.6), SIDE_RAIL_Y[0] - 4, SIDE_RAIL_Y[1] + 3, 24, 48,
              bevel=1.2)
        picatinny(b, SIDE_RAIL_Y[0], SIDE_RAIL_Y[1],
                  lambda u, h, y, s=s: Vector((s * (19.6 + h), y, SIDE_RAIL_Z + u)),
                  base_h=2.4, tooth_h=3.5 + 0.0)
    # Top rail along the whole receiver.
    picatinny(b, -110, 243, lambda u, h, y: Vector((u, y, 62 + h)), base_h=4.0, tooth_h=6.0 + 1.0)
    # Flip-up iron sights, raised.
    b.box(-10, 10, -104, -84, 71, 75, mat="rail", bevel=0.8)
    for s in (1, -1):
        b.box(min(s * 7, s * 10), max(s * 7, s * 10), -101, -87, 75, 83, mat="rail", bevel=0.6)
    b.box(-6, 6, -96, -92, 75, 84, mat="rail", bevel=0.5)
    b.box(-10, 10, 220, 238, 71, 75, mat="rail", bevel=0.8)
    for s in (1, -1):
        b.box(min(s * 7, s * 10), max(s * 7, s * 10), 222, 236, 75, 85, mat="rail", bevel=0.6)
    b.box(-1.3, 1.3, 227, 231, 75, 83.5, mat="rail")
    # Pistol grip (raked), with the magazine well recessed into its base.
    rz = [0, -18, -50, -80, -92]
    rear = [(grip_lines(z)[0] - (0, 1.5, 3.0, 1.5, 0)[i], z) for i, z in enumerate(rz)]
    fb = (rear[-1][0] + GRIP_DEPTH * math.cos(RAKE) * math.cos(RAKE),
          -92 - GRIP_DEPTH * math.cos(RAKE) * math.sin(RAKE))
    front = [fb, (grip_lines(-90)[1] + 1.0, -90), (grip_lines(-78)[1] + 2.0, -78), (grip_lines(-68)[1] + 0.5, -68),
             (grip_lines(-56)[1] + 2.0, -56), (grip_lines(-44)[1], -44), (grip_lines(0)[1], 2)]
    prof = [(rear[0][0], 2)] + rear[1:] + front
    b.prism("x", prof, -16, 16, mat="grip", bevel=1.8)
    top, d = mag_axis()
    perp = Vector((0, math.cos(RAKE), -math.sin(RAKE)))
    well_c = Vector((0, rear[-1][0], -92)) + perp * (GRIP_DEPTH * math.cos(RAKE) / 2)
    # well: dark box along the magazine axis, its open end at the grip base
    xf = Matrix.Translation(well_c) @ Matrix.Rotation(-RAKE, 4, 'X')
    b.box(-11.5, 11.5, -22.5, 22.5, -0.6, 18, mat="dark", xf=xf)
    # Trigger guard (open band from the grip front to the receiver) and trigger.
    outer = [(grip_lines(-48)[1] - 5, -48), (54, -54), (66, -57), (102, -57), (115, -52), (122, -40), (124, -20),
             (124, 1.5)]
    inner = [(grip_lines(-36)[1] - 1, -36), (57, -43.5), (68, -46.5), (99, -46.5), (108, -43), (113, -34),
             (114.5, -20), (114.5, 1.5)]
    b.strip(outer, inner, -8.5, 8.5, bevel=0.0)
    b.prism("x", [(73, 2), (79, 2), (77, -12), (73, -24), (68.5, -29), (66.5, -27.5), (70.5, -14)], -3, 3,
            mat="metal", bevel=0.5)
    # Magazine release paddle at the back of the guard.
    b.box(-6, 6, grip_lines(-30)[1] - 1.5, grip_lines(-30)[1] + 3.5, -34, -22, mat="metal", bevel=0.6)
    # Front grip folded forward under the receiver; its hinge sits just ahead of the trigger guard.
    b.prism("x", [(128, 0.5), (232, 0.5), (238, -3), (238, -12), (232, -17.5), (216, -17.5), (208, -15.8),
                  (198, -17.5), (190, -15.8), (180, -17.5), (142, -17.5), (130, -15), (126, -8)], -13, 13,
            bevel=1.5)
    b.lathe("x", (0, 133, -8), [(-14.5, 0), (-14.5, 6.5), (14.5, 6.5), (14.5, 0)], seg=12, mat="polymer")
    # Ambidextrous selector levers and the bolt catch.
    for s in (1, -1):
        b.lathe("x", (0, 20, 27), [(s * 18.5, 0), (s * 18.5, 6), (s * 21.5, 6), (s * 22.5, 4.5), (s * 22.5, 0)],
                seg=12, mat="metal")
        b.prism("x", [(20, 31), (3, 25.5), (1, 22.5), (3.5, 20.5), (20, 23.5)],
                min(s * 20, s * 22.3), max(s * 20, s * 22.3), mat="metal", bevel=0.4)
    b.box(18.5, 21, -6, 8, 40, 46, mat="metal", bevel=0.5)
    # Sling loops: rear left, front left.
    b.box(15, 20, -112, -100, 44, 56, bevel=1.0)
    b.box(18.5, 23, 236, 241, 2, 14, bevel=0.8)
    # Barrel with its threaded muzzle and an open bore.
    b.lathe("y", (0, 0, BORE_Z), [(250, 0), (250, 8.5), (262, 8.5), (262, 7.2), (MUZZLE_Y - 0.6, 7.2),
                                   (MUZZLE_Y, 6.4), (MUZZLE_Y, 2.4), (MUZZLE_Y - 9, 2.4), (MUZZLE_Y - 9, 0)],
            seg=14, mat="metal")
    return b.to_object("MP7A1_BODY")


def build_bolt():
    b = Builder()
    b.box(-5.5, 5.5, REAR_Y - 10, -70, 50, 58, mat="metal", bevel=0.6)               # shaft into the receiver
    b.prism("x", [(REAR_Y - 13, 50), (REAR_Y - 4, 50), (REAR_Y - 4, 58.5), (REAR_Y - 9, 60), (REAR_Y - 13, 58.5)],
            -22, 22, mat="polymer", bevel=1.4)                                        # T handle
    b.box(12, 20, REAR_Y - 11, REAR_Y + 1, 58, 61.5, mat="metal", bevel=0.5)          # latch
    return b.to_object("MP7A1_BOLT")


def build_stock():
    b = Builder()
    y0 = BUTT_REAR - STOCK_TRAVEL
    plate = [(y0 + 14, 42), (y0 + 14, -22), (y0 + 8, -25), (y0 + 1.5, -21), (y0, -8), (y0 - 0.6, 10), (y0, 28),
             (y0 + 2.5, 40), (y0 + 8, 44.5)]
    b.prism("x", plate, -22, 22, mat="polymer", bevel=2.0)
    b.box(-17, 17, y0 + 13, y0 + 18, -12, 20, mat="polymer", bevel=1.0)               # rod yoke / latch housing
    for s in (1, -1):
        b.lathe("y", (s * 19.0, 0, 9.0), [(y0 + 12, 0), (y0 + 12, 4.5), (REAR_Y + 6 - 0.0, 4.5),
                                          (REAR_Y + 6, 0)], seg=10, mat="metal")
    b.box(-6, 6, y0 + 4, y0 + 12, -27, -22, mat="metal", bevel=0.6)                   # release button
    return b.to_object("MP7A1_STOCK")


def build_magazine(rounds):
    """Straight double-stack magazine, origin at the feed lips, hanging along -Z (raked by the attachment)."""
    top, d = mag_axis()
    grip_base = 132.7                                   # mag top to the grip base along the axis (see mag_axis)
    length = grip_base + 5.0 + {20: 0.0, 30: 48.0, 40: 96.0}[rounds]
    b = Builder()
    w, dep = 9.5, 20.0
    b.prism("z", [(-w, -dep), (w, -dep), (w, dep - 2), (w - 2, dep), (-w + 2, dep), (-w, dep - 2)],
            -(length - 5.0), -6.0, mat="magpoly", bevel=1.0)
    b.prism("z", [(-7, -18), (7, -18), (7, 16), (5, 18.5), (-5, 18.5), (-7, 16)], -6.5, 0.0, mat="magpoly",
            bevel=0.8)                                                                   # feed lips
    b.prism("x", [(-dep - 1.5, -length), (dep + 4.0, -length), (dep + 4.0, -length + 3.0),
                  (dep + 1.0, -length + 5.5), (-dep - 1.5, -length + 5.5)], -11.0, 11.0, mat="magpoly",
            bevel=1.0)                                                                   # base plate
    # top round: steel-cored bullet forward, brass case
    b.lathe("y", (0, 0, -2.6), [(-17.5, 0), (-17.5, 4.0), (5.0, 4.0), (6.5, 2.4), (12.5, 2.4)], seg=8, mat="brass")
    b.lathe("y", (0, 0, -2.6), [(12.5, 2.4), (16.0, 2.0), (19.2, 0.7), (19.6, 0)], seg=8, mat="copper")
    return b.to_object("46x30Magazine%d_MP7" % rounds)


def build_suppressor():
    b = Builder()
    L = 190.0
    b.lathe("y", (0, 0, 0), [(0, 0), (0, 7.2), (0, 13.5), (1.5, 15.0), (24, 15.0), (25.5, 16.5), (29, 17.2),
                              (L - 9, 17.2), (L - 4, 16.0), (L, 13.0), (L, 4.0), (L - 6, 3.2), (L - 6, 0)],
            seg=20, mat="suppressor")
    return b.to_object("MP7_Suppressor")


def build_mount():
    b = Builder()
    b.lathe("y", (0, 0, 0), [(-14, 0), (-14, 7.0), (-14, 9.0), (-12.5, 10.0), (0, 10.0), (2, 9.2), (6, 9.2),
                              (7, 8.4), (22, 8.4), (23, 7.4), (23, 5.2), (14, 5.0), (14, 0)],
            seg=16, mat="metal", phase=0.5)
    return b.to_object("MP7_Muzzle_Mount_Device")


# ==================================================================================================
# Materials, UVs, baking
# ==================================================================================================

def material(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    return m


def unwrap(objects, margin):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def set_pass(kind, image):
    """Point every material at `image` and make it emit the requested bake pass."""
    for i, name in enumerate(MATS):
        m = material(name)
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(em.outputs[0], out.inputs[0])
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        nt.nodes.active = tex
        if kind == "pos":
            tc = nt.nodes.new("ShaderNodeTexCoord")
            mp = nt.nodes.new("ShaderNodeVectorMath")
            mp.operation = 'MULTIPLY_ADD'
            mp.inputs[1].default_value = (1.0, 1.0, 1.0)
            mp.inputs[2].default_value = (0.5, 0.5, 0.5)
            nt.links.new(tc.outputs["Object"], mp.inputs[0])
            nt.links.new(mp.outputs[0], em.inputs[0])
        elif kind == "nrm":
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            tr = nt.nodes.new("ShaderNodeVectorTransform")
            tr.vector_type = 'NORMAL'
            tr.convert_from = 'WORLD'
            tr.convert_to = 'OBJECT'
            nt.links.new(geo.outputs["Normal"], tr.inputs[0])
            mp = nt.nodes.new("ShaderNodeVectorMath")
            mp.operation = 'MULTIPLY_ADD'
            mp.inputs[1].default_value = (0.5, 0.5, 0.5)
            mp.inputs[2].default_value = (0.5, 0.5, 0.5)
            nt.links.new(tr.outputs[0], mp.inputs[0])
            nt.links.new(mp.outputs[0], em.inputs[0])
        elif kind == "mat":
            em.inputs[0].default_value = ((i + 0.5) / 16.0, 0.0, 0.0, 1.0)
        elif kind == "occ":
            # R: short-range AO (cavities), G: broad AO, B: edge mask (normal against the bevelled normal)
            ao1 = nt.nodes.new("ShaderNodeAmbientOcclusion")
            ao1.samples = 16
            ao1.inputs["Distance"].default_value = 3.0 * K
            ao2 = nt.nodes.new("ShaderNodeAmbientOcclusion")
            ao2.samples = 16
            ao2.inputs["Distance"].default_value = 22.0 * K
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            bev = nt.nodes.new("ShaderNodeBevel")
            bev.samples = 8
            bev.inputs["Radius"].default_value = 1.4 * K
            dot = nt.nodes.new("ShaderNodeVectorMath")
            dot.operation = 'DOT_PRODUCT'
            nt.links.new(geo.outputs["Normal"], dot.inputs[0])
            nt.links.new(bev.outputs[0], dot.inputs[1])
            inv = nt.nodes.new("ShaderNodeMath")
            inv.operation = 'SUBTRACT'
            inv.inputs[0].default_value = 1.0
            nt.links.new(dot.outputs["Value"], inv.inputs[1])
            comb = nt.nodes.new("ShaderNodeCombineXYZ")
            nt.links.new(ao1.outputs["AO"], comb.inputs[0])
            nt.links.new(ao2.outputs["AO"], comb.inputs[1])
            nt.links.new(inv.outputs[0], comb.inputs[2])
            nt.links.new(comb.outputs[0], em.inputs[0])


def bake_maps(target, context_objects, size):
    """Baked maps of one object: dict of (size, size, 3) float arrays plus a coverage mask."""
    scene = bpy.context.scene
    for o in scene.objects:
        o.hide_render = o not in context_objects
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    maps = {}
    for kind, samples in (("pos", 1), ("nrm", 1), ("mat", 1), ("occ", SAMPLES)):
        img = bpy.data.images.new("bake_" + kind, size, size, alpha=True, float_buffer=True)
        img.colorspace_settings.name = 'Non-Color'
        img.pixels.foreach_set(np.zeros(size * size * 4, dtype=np.float32))
        set_pass(kind, img)
        scene.cycles.samples = samples
        bpy.ops.object.bake(type='EMIT', margin=0, use_clear=False)
        arr = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(arr)
        maps[kind] = arr.reshape(size, size, 4)[:, :, :3].copy()
        bpy.data.images.remove(img)
    maps["cover"] = maps["pos"].max(axis=2) > 0.01
    maps["pos"] = (maps["pos"] - 0.5) / K            # back to millimetres, FBX data space (z flipped)
    maps["pos"][:, :, 2] *= -1.0                     # game z
    n = maps["nrm"] * 2.0 - 1.0
    n[:, :, 2] *= -1.0
    maps["nrm"] = n
    maps["mat"] = np.clip((maps["mat"][:, :, 0] * 16.0).astype(int), 0, len(MATS) - 1)
    return maps


# ==================================================================================================
# Painting (numpy)
# ==================================================================================================

def _hash(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFF).astype(np.float32) / 65535.0


def vnoise(p, scale, seed):
    """Smooth value noise in 3D, p in mm, feature size `scale` mm, output 0..1."""
    q = p / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = ((f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1])
                     * (f[..., 2] if dz else 1 - f[..., 2]))
                out = out + w * _hash(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out


FONT = {  # 3x5 pixel glyphs, rows top to bottom
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "011", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"], "A": ["010", "101", "111", "101", "101"],
    "M": ["101", "111", "111", "101", "101"], "P": ["110", "101", "110", "100", "100"],
    "X": ["101", "101", "010", "101", "101"], ".": ["000", "000", "000", "000", "010"],
    " ": ["000", "000", "000", "000", "000"], "S": ["111", "100", "111", "001", "111"],
    "F": ["111", "100", "110", "100", "100"],
}


def text_mask(u, v, text, u0, v0, height):
    """Mask of `text` drawn with its baseline-left corner at (u0, v0) mm, glyph height `height` mm."""
    px = height / 5.0
    cu = np.floor((u - u0) / px).astype(int)
    cv = np.floor((v0 + height - v) / px).astype(int)
    m = np.zeros(u.shape, bool)
    for k, ch in enumerate(text):
        g = FONT[ch]
        for r in range(5):
            for c in range(3):
                if g[r][c] == "1":
                    m |= (cu == k * 4 + c) & (cv == r)
    return m


def srgb_to_lin(c):
    c = np.asarray(c, np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


BASE = {  # sRGB base colours, before AO / wear
    "polymer": (50, 50, 52), "grip": (46, 46, 48), "metal": (56, 58, 62), "rail": (48, 48, 50),
    "dark": (12, 12, 13), "brass": (150, 118, 62), "copper": (140, 82, 52), "magpoly": (50, 50, 53),
    "suppressor": (48, 49, 52),
}


def paint(maps, kind):
    """Final sRGB colour (0..255 float) for every texel of one baked object."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    base = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        base[mat == i] = BASE[name]
    is_metal = (mat == MATS.index("metal")) | (mat == MATS.index("brass")) | (mat == MATS.index("copper"))
    col = base.copy()
    # Material grain: polymer mottling, metal brushed streaks along the bore axis.
    mott = vnoise(p, 6.0, 1) * 0.6 + vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    # Grip stippling: a speckled panel with a smooth border.
    g = mat == MATS.index("grip")
    speck = vnoise(p, 0.9, 4)
    side = np.abs(n[..., 0]) > 0.6
    panel = g & side & (p[..., 2] < -14) & (p[..., 2] > -84)
    col[panel] *= (0.78 + 0.45 * (speck[panel] > 0.55))[..., None]
    # Top light, ambient occlusion.
    col *= (0.98 + 0.16 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.42 + 0.58 * np.clip(ao_b, 0, 1) ** 1.3) * (0.62 + 0.38 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    # Edge wear on convex edges (open to the sky: short AO high), dirt in the concave ones.
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal, 72.0, 52.0) * (0.7 + 0.6 * vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
    if kind == "gun":
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
        lower = (np.abs(x) > 18.0) & (z > 0) & (z < 36)
        upper = (np.abs(x) > 14.5) & (z > 36) & (z < 61)
        # Pins through the lower receiver (both sides) and the grip.
        for py, pz, r in ((-70, 20, 2.6), (-20, 24, 2.4), (60, 24, 2.6), (95, 26, 2.4), (150, 20, 2.6),
                          (205, 14, 2.4)):
            dd = np.hypot(y - py, z - pz)
            ring = (left | right) & lower & (dd < r)
            col[ring & (dd > r - 1.0)] *= 0.45
            col[ring & (dd <= r - 1.0)] += 14
        # Seam between the receiver halves (moulding line) and a takedown seam ahead of the guard.
        seam = (left | right) & (np.abs(x) > 18.0) & (np.abs(z - 33.5) < 0.5) & (y > REAR_Y + 3) & (y < 236)
        col[seam] *= 0.55
        # Ejection port on the right side (-X) of the upper receiver.
        port = right & upper & (y > 70) & (y < 118) & (z > 39) & (z < 55)
        rim = right & upper & (y > 68) & (y < 120) & (z > 37.5) & (z < 56.5) & ~port
        col[port] = col[port] * 0.25 + np.array([4, 4, 5])
        col[rim] += 16
        # Selector markings around the levers: safe white, single and auto red.
        sel = (left | right) & lower
        marks = ((np.hypot(y - 33.5, z - 31.5) < 1.9, (205, 205, 200)),
                 (np.hypot(y - 25.0, z - 34.5) < 1.9, (190, 40, 36)),
                 ((np.abs(y - 13.0) < 3.4) & (np.abs(z - 34.0) < 1.3), (190, 40, 36)))
        for m, c in marks:
            col[sel & m] = c
        # Engraved designation on the left of the upper receiver, calibre on the right.
        tl = text_mask(y, z, "MP7A1", 120.0, 44.0, 6.0)
        col[left & upper & tl] = col[left & upper & tl] * 0.4 + 70
        tr = text_mask(-y, z, "4.6X30", -205.0, 44.0, 5.0)
        col[right & upper & tr] = col[right & upper & tr] * 0.4 + 66
        # Barrel threads and the bore.
        thr = is_metal & (y > 262) & (y < MUZZLE_Y - 0.5) & (np.hypot(x, z - BORE_Z) > 6.5)
        col[thr] *= (0.7 + 0.5 * (np.mod(y[thr], 1.6) < 0.8))[..., None]
        bore = (np.hypot(x, z - BORE_Z) < 2.5) & (y > MUZZLE_Y - 9.5)
        col[bore] = 8
        # Rear sight aperture.
        ap = (np.hypot(x, z - 80.5) < 1.6) & (np.abs(y + 94) < 2.5)
        col[ap] = 10
    elif kind.startswith("mag"):
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        rounds = kind[3:]
        side = np.abs(n[..., 0]) > 0.7
        length = 132.7 + 5.0 + {"20": 0.0, "30": 48.0, "40": 96.0}[rounds]
        # capacity ticks (2 / 3 / 4 white bars) on both sides above the base plate, readable at 128 px
        for k in range(int(rounds) // 10):
            zc = -length + 10.0 + k * 3.6
            tick = side & (np.abs(z - zc) < 0.9) & (np.abs(y + 4.0) < 6.0)
            col[tick] = (190, 190, 184)
        # vertical pressing ribs on the body sides
        rib = side & (np.abs(np.abs(y) - 13.0) < 0.9) & (z < -12) & (z > -length + 10)
        col[rib] *= 0.72
    elif kind == "suppressor":
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        r = np.hypot(x, z)
        knurl = (y > 2) & (y < 23) & (r > 14)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 2.0) < 1.0) ^ (np.mod(np.arctan2(x[knurl], z[knurl]) * 17.2
                                                                                 / math.pi, 1.0) < 0.5)))[..., None]
        band = (np.abs(y - 26.8) < 0.7) | (np.abs(y - 182.0) < 0.6)
        col[band & (r > 15)] *= 0.5
        ang = np.arctan2(x, -z)
        tx = text_mask(y, ang * 17.2, "4.6X30", 70.0, -3.0, 6.0)
        col[tx & (r > 16.5)] = col[tx & (r > 16.5)] * 0.3 + 120
        col[(r < 3.5) & (y > 185)] = 8
    elif kind == "mount":
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        r = np.hypot(x, z)
        ang = np.mod(np.arctan2(x, z) / (2 * math.pi) * 6.0, 1.0)
        slot = (y > 9) & (y < 21) & (r > 7.5) & (np.abs(ang - 0.5) < 0.16)
        col[slot] = 10
        flats = (y > -12) & (y < -1) & (r > 9.4) & (np.abs(np.mod(np.arctan2(x, z) / (2 * math.pi) * 2, 1) - .5) < 0.12)
        col[flats] += 20
        col[r < 5.6] = 9
    return np.clip(col, 0, 255)


def dilate(col, cover, steps):
    col = col.copy()
    cov = cover.copy()
    for _ in range(steps):
        acc = np.zeros_like(col)
        cnt = np.zeros(cov.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            acc += np.roll(np.roll(col * cov[..., None], dy, 0), dx, 1)
            cnt += np.roll(np.roll(cov.astype(np.float32), dy, 0), dx, 1)
        grow = (~cov) & (cnt > 0)
        col[grow] = acc[grow] / cnt[grow][..., None]
        cov = cov | grow
    col[~cov] = col[cov].mean(axis=0)
    return col


def save_png(col, size, path):
    """col: (S, S, 3) sRGB 0..255 at bake size, rows bottom-up; box-filtered down to `size`, saved as RGB PNG."""
    s = col.shape[0] // size
    small = col.reshape(size, s, size, s, 3).mean(axis=(1, 3)) / 255.0
    img = bpy.data.images.new(os.path.basename(path), size, size, alpha=False)
    img.colorspace_settings.name = 'sRGB'
    rgba = np.concatenate([small, np.ones((size, size, 1))], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


def dump_maps(maps, prefix):
    """--debug DIR: the baked maps of one object as PNGs (occ = short AO, broad AO, edge x 9)."""
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    occ = maps["occ"].copy()
    occ[..., 2] = np.clip(occ[..., 2] * 9.0, 0, 1)
    for name, arr in (("occ", occ), ("nrm", maps["nrm"] * 0.5 + 0.5), ("mat", np.repeat(maps["mat"][..., None] / 8.0, 3, 2))):
        save_png(np.clip(arr, 0, 1) * 255.0, arr.shape[0], prefix + "_" + name + ".png")


def texture(objects, contexts, kinds, size, path):
    bake = max(size * 4, BAKE // (256 // size) if size < 256 else BAKE)
    col = np.zeros((bake, bake, 3), np.float32)
    cover = np.zeros((bake, bake), bool)
    for ob, ctx, kind in zip(objects, contexts, kinds):
        maps = bake_maps(ob, ctx, bake)
        if DEBUG:
            dump_maps(maps, os.path.join(DEBUG, ob.name))
        c = paint(maps, kind)
        m = maps["cover"]
        col[m] = c[m]
        cover |= m
    col = dilate(col, cover, 4 * (bake // size))
    save_png(col, size, path)


# ==================================================================================================
# Export and attachment points
# ==================================================================================================

def export(objects, path):
    for o in objects:
        o.data.materials.clear()
        o.rotation_euler = (math.radians(90), 0, 0)
        o.scale = (0.01, 0.01, 0.01)
        o.hide_render = False
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True)
    normalize_fbx(path)


def _fbx_nodes(data, off, version, out, path):
    """Flat list of (path, name, [(type, offset, value)]) for every node of a binary FBX (7.x)."""
    while True:
        if version >= 7500:
            end, nprops, _ = struct.unpack_from("<QQQ", data, off)
            off += 24
        else:
            end, nprops, _ = struct.unpack_from("<III", data, off)
            off += 12
        nlen = data[off]
        name = data[off + 1:off + 1 + nlen].decode("ascii", "replace")
        off += 1 + nlen
        if end == 0:
            return off
        props = []
        for _ in range(nprops):
            kind = chr(data[off])
            off += 1
            if kind in "YCIFDL":
                size = {"Y": 2, "C": 1, "I": 4, "F": 4, "D": 8, "L": 8}[kind]
                props.append((kind, off, struct.unpack_from("<" + {"Y": "h", "C": "b", "I": "i", "F": "f", "D": "d",
                                                                    "L": "q"}[kind], data, off)[0]))
                off += size
            elif kind in "fdlbic":
                off += 12 + struct.unpack_from("<III", data, off)[2]
                props.append((kind, off, None))
            else:
                length = struct.unpack_from("<I", data, off)[0]
                props.append((kind, off + 4, data[off + 4:off + 4 + length]))
                off += 4 + length
        out.append((path, name, props))
        if off < end:
            off = _fbx_nodes(data, off, version, out, path + (name,))
        off = end
        if path == () and off >= len(data) - 200:
            return off


def normalize_fbx(path):
    """Blender stamps each export with the time and keys objects by memory address; rewrite both in place (same
    lengths) so the same model gives the same bytes: time 2026-01-01 00:00:00.000, ids from a hash of class + name."""
    import hashlib
    data = bytearray(open(path, "rb").read())
    version = struct.unpack_from("<I", data, 23)[0]
    nodes = []
    _fbx_nodes(bytes(data), 27, version, nodes, ())
    stamp = {"Year": 2026, "Month": 1, "Day": 1, "Hour": 0, "Minute": 0, "Second": 0, "Millisecond": 0}
    remap = {}
    for p, name, props in nodes:
        if p[-1:] == ("CreationTimeStamp",) and name in stamp:
            struct.pack_into("<i", data, props[0][1], stamp[name])
        if len(p) == 1 and p[0] in ("Objects", "Documents") and props and props[0][0] == "L":
            label = name.encode() + b"|" + (props[1][2] if len(props) > 1 and props[1][2] else b"")
            new = int.from_bytes(hashlib.sha1(label).digest()[:6], "little") + 1000
            remap[props[0][2]] = new
            struct.pack_into("<q", data, props[0][1], new)
    for p, name, props in nodes:
        if p == ("Connections",) and name == "C":
            for kind, off, val in props[1:3]:
                if kind == "L" and val in remap:
                    struct.pack_into("<q", data, off, remap[val])
    open(path, "wb").write(bytes(data))


def g(v):
    return [round(float(c) * K, 4) for c in v]


def points(bounds):
    top, d = mag_axis()
    rail_top = RAIL_TOP * K
    side = SIDE_RAIL_X * K
    rail_y = sum(SIDE_RAIL_Y) / 2
    pts = {
        "muzzle": {"offset": g((0, MUZZLE_Y, BORE_Z)), "rotate": [-90.0, 0.0, -180.0]},
        "world": {"offset": [0.02, 0.13, 0.0], "rotate": [180.0, 0.0, 180.0]},
        "magazine": {"offset": g(top), "rotate": [round(-math.degrees(RAKE), 4), 0.0, 0.0]},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up and MP5's scope sits 0.0032 under that
        # rail's top: the same relations on the integral rail.
        "rail_up": {"offset": [0.0, round(70 * K, 4), round(rail_top - 0.0055, 4)]},
        "scope": {"offset": [0.0, round(70 * K, 4), round(rail_top - 0.0032, 4)]},
        "rail_left": {"offset": [round(side - 0.0055, 4), round(rail_y * K, 4), round(SIDE_RAIL_Z * K, 4)]},
        "rail_right": {"offset": [round(-(side - 0.0055), 4), round(rail_y * K, 4), round(SIDE_RAIL_Z * K, 4)]},
        # MP5: light_left = rail_left + 0.0062 x, laser_right = rail_right - 0.0073 x, 0.0008 lower
        "light_left": {"offset": [round(side - 0.0055 + 0.0062, 4), round((rail_y + 1.5) * K, 4),
                                  round(SIDE_RAIL_Z * K, 4)]},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), round((rail_y + 1.5) * K, 4),
                                   round(SIDE_RAIL_Z * K - 0.0008, 4)]},
        "canon": {"offset": g((0, MUZZLE_Y, BORE_Z))},
        "bolt_fired": {"offset": [0.0, round(-CH_TRAVEL * K, 4), 0.0]},
        "stock_folded": {"offset": [0.0, round(STOCK_TRAVEL * K, 4), 0.0]},
    }
    pts["_bounds"] = bounds
    pts["_notes"] = {
        "units": "game units (0.72 of real size); +Y muzzle, +Z top, +X the gun's left; origin = rear-top of grip",
        "magazine": "magazine meshes are straight along -Z; the attachment rotate rakes them back 14 degrees "
                    "(GoM's MP5 uses +10.29 to tilt its magazine bottom forward)",
        "bolt_fired": "charging handle pulled back 50 mm real; the real MP7 handle does not reciprocate",
        "stock_folded": "MP7A1_STOCK is modelled deployed at the origin; this offset slides it in (223 mm real)",
    }
    return pts


def bounds_of(ob, offset=(0, 0, 0)):
    vs = [(v.co.x, v.co.y, -v.co.z) for v in ob.data.vertices]
    mn = [round(min(v[i] for v in vs) + offset[i], 4) for i in range(3)]
    mx = [round(max(v[i] for v in vs) + offset[i], 4) for i in range(3)]
    return {"min": mn, "max": mx, "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons)}


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

    body, bolt, stock = build_body(), build_bolt(), build_stock()
    mags = [build_magazine(r) for r in (20, 30, 40)]
    supp, mount = build_suppressor(), build_mount()

    unwrap([body, bolt, stock], 0.006)
    for o in mags + [supp, mount]:
        unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    texture([body, bolt, stock], [[body, bolt], [body, bolt], [stock]], ["gun", "gun", "gun"], 256,
            os.path.join(TEX_DIR, "MP7A1.png"))
    for r, m in zip((20, 30, 40), mags):
        texture([m], [[m]], ["mag%d" % r], 128, os.path.join(TEX_DIR, "46x30Magazine%d_MP7.png" % r))
    texture([supp], [[supp]], ["suppressor"], 128, os.path.join(TEX_DIR, "MP7_Suppressor.png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "MP7_Muzzle_Mount_Device.png"))

    bounds = {o.name: bounds_of(o) for o in [body, bolt, stock] + mags + [supp, mount]}
    bounds["MP7A1_STOCK_folded"] = bounds_of(stock, (0, STOCK_TRAVEL * K, 0))
    with open(POINTS_JSON, "w") as fh:
        json.dump(points(bounds), fh, indent=2)
        fh.write("\n")

    export([body, bolt, stock], FBX_GUN)
    export(mags, FBX_MAGS)
    export([supp, mount], FBX_PARTS)
    for name, b in bounds.items():
        print("%-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
