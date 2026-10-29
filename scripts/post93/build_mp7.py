"""H&K MP7A1 models and textures for GoM Extension: Guns of Tien - Post-93 (Blender 5.2, headless); also the
shared geometry, bake, paint-helper and FBX code build_p90.py imports.

    blender -b --factory-startup -P scripts/post93/build_mp7.py -- [--size 1024] [--samples 48] [--debug DIR]

Writes (P = Contents/mods/GoMExtensionGunsOfTienPost93/42/media):
    P/models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx        MP7A1_BODY, MP7A1_BOLT, MP7A1_STOCK, MP7A1_FOREGRIP
    P/models_X/weapons/firearms/GunsOfTienPost93_MP7A2.fbx        MP7A2_BODY (bolt and stock: the A1's nodes)
    P/models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx  46x30Magazine20/30/40/60_MP7
    P/models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx       MP7_Suppressor, MP7_Muzzle_Mount_Device
    P/textures/weapons/GunsOfTienPost93/<name>.png                MP7A1 (256, shared by the four gun nodes), MP7A2,
                                                                  one 128 texture per magazine / part
    scripts/post93/mp7_points.json, mp7a2_points.json             attachment points (game space)

The shape is measured from H&K's side photo of an MP7A1 (docs/mp7_2.png; its traced outline is
mp7_reference_outline.json, which render_mp7.py / make_mp7_art.py lay over the model to check it). Every side profile
is written in that photo's coordinates, real millimetres: L back from the muzzle tip, H up from the lowest point
(stock collapsed, 20-round magazine). Each part is one such profile extruded across the gun with chamfered or
rounded edges (slab(), a filled 2D curve), GoM's flat faceted hard-surface style; the magazines are swept along an
axis that runs straight inside the grip and curves toward the muzzle below it (docs/mp7_1.png, mp7_4.png).

GoM's conventions (CLAUDE.md, "Gun assets in GoM"): game space +Y muzzle, +Z top, +X the gun's LEFT, origin at
the rear-top of the pistol grip, drawn at 0.603 of real size (the M16A2's proportion; 0.72 before 2026-10-26). The MP7 is held like a pistol, as GoM holds its MP5K,
TEC9 and MAC10: everything is modelled and baked upright and the gun nodes are turned 180 degrees about the bore axis
at export, with the attachment points (TURN, turned(); build_p90.py does the same). FBX object name = node name, mesh data =
(game x, game y, -game z), rotation (90, 0, 0), scale 0.01, export_scene.fbx with its defaults.

Textures are baked in Cycles (object position, normal, material, two ambient occlusion distances and an edge mask
from the Bevel node) and painted from those maps with numpy: base colours, grain, light AO, bright edges, then the
photo's details by position (grip ribs, slots, pins, markings, the folded grip's grooves). Fixed seeds and sample
counts: the same Blender build gives the same files.
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
FBX_GUN_A2 = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_MP7A2.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx")
TEX_DIR = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
POINTS_JSON = os.path.join(HERE, "mp7_points.json")
POINTS_JSON_A2 = os.path.join(HERE, "mp7a2_points.json")

# game units per real millimetre: the M16A2's proportion (GoM's M16A2 is drawn at 0.603 of its real length, true to
# vanilla's body; user, 2026-10-26: our guns resized in their meshes, TODO.md "New direction"). Was 0.00072 (GoM's MP5
# family), as the P90, Five-seveN and UCP still are (they set their own K until they are rebuilt).
K = 0.000603

# Photo coordinates (mm) of the model origin: the rear-top of the grip, where its back meets the receiver.
# game y = L0 - L, game z = H - H0.
L0, H0 = 289.0, 91.5
BORE_H = 120.0                    # bore axis
BORE_Z = BORE_H - H0
CANON_L = 47.7                    # the nose plate's face where the barrel leaves it
STOCK_TRAVEL = 223.0              # 638 - 415
# The integral front grip folds up under the receiver about a pin through its round front end (the knuckle, centre
# of the round nose of FRONT_GRIP, the release button beside it); unfolded it turns 90 degrees down, its free end
# (the serrated catch) at the bottom, about as low as the pistol grip.
FGRIP_HINGE = (90.8, 88.0)        # photo L, H
FGRIP_ANGLE = 90.0
RAIL_BASE_H, RAIL_TOP_H = 166.0, 169.6   # top rail mounting face, crossbar tops
SIDE_RAIL_L, SIDE_RAIL_H = (78.0, 140.0), 120.0
SIDE_RAIL_X = W_SIDE = 24.5       # side rail crossbar faces
MAG_L, MAG_H = 257.0, 104.0       # magazine top (feed lips), centred in the grip
CH_TRAVEL = 50.0                  # charging handle pull
W_LOWER, W_UPPER, W_NOSE, W_GRIP, W_FGRIP, W_GUARD, W_BUTT = 19.0, 15.5, 17.0, 16.5, 13.0, 6.0, 22.0   # half widths

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

def slab(b, outline, holes=(), half=10.0, bevel=1.0, res=0, mat="polymer", x0=0.0):
    """Side profile [(y, z)] in game mm with optional holes, extruded across x0 - half .. x0 + half, every edge
    chamfered (res 0) or rounded in res + 1 steps by `bevel` mm. Built as a filled 2D curve (offset -bevel keeps
    the silhouette on the drawn outline, holes cut cleanly), converted to a mesh and appended to the builder."""
    cu = bpy.data.curves.new("slab", 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    for loop in [outline] + list(holes):
        sp = cu.splines.new('POLY')
        sp.points.add(len(loop) - 1)
        for pt, (y, z) in zip(sp.points, loop):
            pt.co = (y, z, 0.0, 1.0)
        sp.use_cyclic_u = True
    cu.extrude = half - bevel
    cu.bevel_depth = bevel
    cu.bevel_resolution = res
    cu.offset = -bevel
    ob = bpy.data.objects.new("slab", cu)
    bpy.context.scene.collection.objects.link(ob)
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    # curve (u, v, w) -> game (x0 + w, u, v): a rotation, applied before the mesh joins the builder's bmesh
    me.transform(Matrix(((0, 0, 1, x0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    bm = b.bm
    old_v, old_f = set(bm.verts), set(bm.faces)        # from_mesh appends, but not at the end of the index order
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    verts = [v for v in bm.verts if v not in old_v]
    faces = [f for f in bm.faces if f not in old_f]
    assert verts and faces, "bmesh.from_mesh did not append"
    for f in faces:
        f.material_index = MATS.index(mat)
    orient_outward(bm, faces)
    return verts


# ==================================================================================================
# The MP7A1, from the traced photo (photo coordinates L, H in mm; see the module docstring)
# ==================================================================================================

def P(L, H):
    """Photo (L, H) mm -> game (y, z) mm."""
    return L0 - L, H - H0


def PL(points):
    return [P(L, H) for L, H in points]


def box(b, La, Lb, Ha, Hb, xa, xb, mat="polymer", bevel=0.0):
    ya, yb = sorted((L0 - La, L0 - Lb))
    return b.box(min(xa, xb), max(xa, xb), ya, yb, Ha - H0, Hb - H0, mat=mat, bevel=bevel)


def picatinny(b, y0, y1, frame, base_w=15.6, base_h=4.0, tooth_w=21.2, tooth_h=6.0, pitch=10.0, tooth_len=4.8,
              mat="rail"):
    """MIL-STD-1913 style rail: a continuous base and crossbars every `pitch` (10.0 mm, 5.2 mm slots). frame(u, h,
    y) -> point, with u across the rail and h up from its mounting face."""
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
        block(-tooth_w / 2, tooth_w / 2, base_h - 1.0, base_h + tooth_h - 1.0, y, y + tooth_len, 0.0)
        y += pitch


# Traced from docs/mp7_2.png (mp7_reference_outline.json).
UPPER = [(56.0, 135.0), (385.0, 135.0), (385.0, 165.0), (376.0, 166.5), (84.6, 166.5), (74.8, 163.6), (71.0, 161.7),
         (69.2, 160.3), (58.0, 160.3), (55.6, 155.2)]
LOWER = [(53.0, 135.0), (52.3, 103.8), (58.4, 104.7), (63.1, 103.8), (68.2, 101.4), (71.5, 98.1), (74.3, 93.0),
         (78.0, 93.0), (78.0, 103.5), (232.0, 103.5), (232.0, 91.6), (384.6, 91.6), (385.0, 135.0)]
NOSE = [(58.0, 160.3), (66.0, 160.3), (60.0, 135.0), (56.5, 118.0), (53.5, 107.0), (50.9, 102.8), (45.8, 93.0),
        (43.5, 92.1), (40.7, 93.5), (40.7, 97.7), (44.4, 111.7), (47.0, 121.0), (47.7, 127.1), (49.5, 130.9),
        (55.6, 155.2)]
GRIP = [(293.5, 91.6), (288.8, 89.3), (286.0, 86.5), (284.1, 81.8), (284.1, 75.7), (286.9, 62.2), (289.8, 41.6),
        (289.8, 20.1), (287.6, 3.0), (228.0, 3.0), (227.1, 5.0), (230.9, 15.4), (233.7, 30.4), (234.1, 69.2),
        (231.0, 74.5), (228.6, 80.4), (231.0, 86.5), (231.0, 94.0), (232.0, 103.0), (293.5, 103.0)]
FRONT_GRIP = [(78.0, 104.5), (74.3, 93.0), (74.3, 85.1), (76.6, 78.0), (79.9, 74.3), (85.1, 71.5), (177.0, 72.0),
              (180.4, 79.9), (176.2, 93.9), (176.2, 97.7), (179.0, 104.5)]
# The guard is a closed loop: its front post rises into the lower receiver, leaning forward about 12 degrees, along
# the folded grip's rear (measured on the user's right-side photo, 2026-10-18: inner edge L 181 at the bar to ~176 at
# the receiver); hidden behind the folded grip, it shows once the grip is unfolded.
GUARD_OUT = [(172.7, 104.0), (178.0, 79.0), (181.0, 73.8), (188.0, 70.8), (229.0, 71.0), (233.5, 70.0)]
GUARD_IN = [(176.7, 104.0), (181.5, 81.0), (184.0, 76.2), (190.0, 73.8), (228.0, 73.9), (232.5, 73.7)]
# the blade's top runs up into the receiver (its bottom is H 103.5): ending at H 101.5, as traced, left it floating
# (user, 2026-10-18: "trigger looks detached")
TRIGGER = [(228.0, 106.5), (222.0, 106.5), (222.0, 101.5), (219.0, 95.0), (214.0, 88.0), (208.0, 82.0),
           (203.5, 80.5), (203.0, 78.5), (206.0, 78.5), (212.0, 81.5), (218.0, 86.5), (223.0, 92.5)]
SELECTOR = [(237.0, 105.0), (241.0, 103.5), (262.0, 114.0), (261.0, 118.0), (258.0, 118.5)]
FRONT_SIGHT = [(89.3, 166.0), (89.3, 178.1), (90.2, 179.9), (111.2, 179.9), (112.2, 183.7), (117.8, 185.1),
               (120.1, 185.1), (122.0, 181.3), (127.6, 182.3), (134.6, 182.7), (135.5, 181.8), (135.5, 178.1),
               (132.7, 177.1), (132.3, 166.0)]
REAR_SIGHT = [(320.0, 166.0), (320.0, 179.9), (328.0, 179.9), (331.0, 183.2), (334.6, 185.1), (338.8, 185.1),
              (343.0, 183.2), (345.0, 185.5), (350.5, 186.0), (350.5, 179.9), (369.7, 179.0), (370.1, 174.3),
              (364.5, 173.9), (364.1, 170.1), (368.0, 166.0)]
BUTT = [(385.0, 148.0), (385.0, 91.6), (389.3, 57.0), (390.7, 53.7), (393.0, 41.1), (395.8, 38.3), (400.5, 36.0),
        (409.9, 36.0), (412.2, 38.3), (412.2, 83.2), (413.1, 86.9), (413.1, 113.6), (414.1, 115.0), (414.1, 144.4),
        (412.2, 146.7), (400.0, 147.2)]
HANDLE_L = (376.0, 394.0)            # the T charging handle, L (build_bolt)

# MP7A2 (user, 2026-10-18; measured on their left-side render of one, scaled 6.81 px/mm by the muzzle tip and the
# receiver's rear face; its hand stop, bore and grip land within 2-3 mm of the A1 photo's): the folding grip and its
# lug under the nose give way to a metal rail handguard wrapping the lower front, Picatinny rails on both sides and
# underneath (3, 6 and 9 o'clock). The rest is the A1's: receiver, nose, grip, guard, top rail, stock, bolt, magazines.
A2_LOWER = [(53.0, 135.0), (52.3, 103.8), (58.4, 104.7), (63.1, 103.8), (232.0, 103.5), (232.0, 91.6),
            (384.6, 91.6), (385.0, 135.0)]
A2_HG_PLATE = [(66.5, 101.0), (66.5, 124.0), (71.0, 128.5), (168.5, 128.5), (173.0, 124.0), (173.0, 101.0)]
A2_HG_BOTTOM = [(66.5, 101.5), (75.0, 91.8), (168.5, 91.8), (172.5, 95.5), (173.0, 101.5)]
A2_W_PLATE, A2_W_BOTTOM = W_LOWER + 1.5, 16.0      # half widths: the side plates stand 1.5 mm proud of the receiver
A2_SIDE_RAIL_L, A2_SIDE_RAIL_H = (88.0, 159.0), 118.0   # seven crossbars, L 90-157, H 107-129
A2_SIDE_RAIL_X = A2_W_PLATE + 3.5                   # crossbar faces
A2_BOTTOM_RAIL_L, A2_BOTTOM_H = (91.0, 168.0), 91.8     # crossbars under it to H 89.5
A2_BOTTOM_RAIL_BOTTOM = A2_BOTTOM_H - 2.3
A2_SCREWS = ((72.5, 118.0), (166.5, 118.0))         # the handguard's two cap screws each side
A2_FOREGRIP_L = 118.0                               # where a vertical grip sits on the bottom rail (forward third)


def build_body(a2=False):
    """The A1's body, or with a2 the MP7A2's: no folding-grip lug, the rail handguard instead of the short side rails."""
    b = Builder()
    slab(b, PL(A2_LOWER if a2 else LOWER), half=W_LOWER, bevel=2.5)
    slab(b, PL(UPPER), half=W_UPPER, bevel=2.0)
    slab(b, PL(NOSE), half=W_NOSE, bevel=1.5, mat="metal")
    slab(b, PL(GRIP), half=W_GRIP, bevel=4.5, res=1, mat="grip")
    b.strip(PL(GUARD_OUT), PL(GUARD_IN), -W_GUARD, W_GUARD)
    slab(b, PL(TRIGGER), half=3.0, bevel=0.6, mat="metal")
    # Picatinny rail along the top, sights on it (both flipped up), short side rails on both sides.
    rail_h = RAIL_BASE_H - H0
    # spine up to the slot floor (H 166.8), crossbars to RAIL_TOP_H, as traced
    picatinny(b, L0 - 375.0, L0 - 85.0, lambda u, h, y: Vector((u, y, rail_h + h)),
              base_h=0.8, tooth_h=RAIL_TOP_H - RAIL_BASE_H - 0.8 + 1.0)
    slab(b, PL(FRONT_SIGHT), half=10.0, bevel=0.8, mat="rail")
    slab(b, PL(REAR_SIGHT), half=10.0, bevel=0.8, mat="rail")
    ya, yb = sorted((P(SIDE_RAIL_L[0], 0)[0], P(SIDE_RAIL_L[1], 0)[0]))
    if a2:
        handguard(b)
    for s in (1, -1):
        if not a2:
            box(b, SIDE_RAIL_L[0] - 2.0, SIDE_RAIL_L[1] + 2.0, SIDE_RAIL_H - 8.0, SIDE_RAIL_H + 8.0,
                s * (W_LOWER - 1.0), s * (W_LOWER + 0.6), mat="rail", bevel=0.6)
            picatinny(b, ya, yb, lambda u, h, y, s=s: Vector((s * (W_LOWER + 0.6 + h), y, SIDE_RAIL_H - H0 + u)),
                      base_h=2.4, tooth_h=3.5)
        # ambidextrous selector: pivot and lever
        b.lathe("x", (0, *P(240.5, 107.5)), [(s * (W_LOWER - 0.5), 0), (s * (W_LOWER - 0.5), 5.5),
                                              (s * (W_LOWER + 2.2), 5.5), (s * (W_LOWER + 3.0), 4.2),
                                              (s * (W_LOWER + 3.0), 0)], seg=12, mat="metal")
        slab(b, PL(SELECTOR), half=1.2, bevel=0.4, mat="metal", x0=s * (W_LOWER + 1.8))
    # barrel collar, groove and the flash hider with its open bore (lathe t = game y)
    t = lambda L: L0 - L
    b.lathe("y", (0, 0, BORE_Z), [(t(52.0), 0), (t(52.0), 7.4), (t(41.0), 7.4), (t(41.0), 5.4), (t(36.5), 5.4),
                                  (t(36.5), 7.0), (t(1.0), 7.0), (t(0.0), 6.2), (t(0.0), 3.0), (t(10.0), 3.0),
                                  (t(10.0), 0)], seg=14, mat="metal", phase=0.5)
    return b.to_object("MP7A2_BODY" if a2 else "MP7A1_BODY")


def handguard(b):
    """MP7A2: the metal handguard round the lower front, its side plates and the block underneath, Picatinny rails on
    both sides (on the plates) and under the block."""
    slab(b, PL(A2_HG_PLATE), half=A2_W_PLATE, bevel=1.0, mat="metal")
    slab(b, PL(A2_HG_BOTTOM), half=A2_W_BOTTOM, bevel=1.5, mat="metal")
    ya, yb = sorted((P(A2_SIDE_RAIL_L[0], 0)[0], P(A2_SIDE_RAIL_L[1], 0)[0]))
    for s in (1, -1):
        picatinny(b, ya, yb, lambda u, h, y, s=s: Vector((s * (A2_W_PLATE + h), y, A2_SIDE_RAIL_H - H0 + u)),
                  base_h=1.0, tooth_h=3.5)
    ya, yb = sorted((P(A2_BOTTOM_RAIL_L[0], 0)[0], P(A2_BOTTOM_RAIL_L[1], 0)[0]))
    picatinny(b, ya, yb, lambda u, h, y: Vector((u, y, A2_BOTTOM_H - H0 - h)), base_h=0.8, tooth_h=2.5)


def build_bolt():
    """The T charging handle at the rear top of the receiver, forward (bolt_lock); bolt_fired pulls it back.
    As H&K's (2026-10-29, from Commons photos of the left and right sides): a flat stem in the channel under the rail's
    rear end, flush with the receiver's top, and at its back a crossbar whose two wings stand a few mm out of either
    side, each ending in a tab with vertical grip ribs that hangs a little lower (until then one 40 mm wide block, 17
    mm tall, across the whole rear end)."""
    b = Builder()
    La, Lb = HANDLE_L
    box(b, La, Lb, 158.0, 165.0, -(W_UPPER - 1.5), W_UPPER - 1.5, mat="rail", bevel=0.8)       # the stem
    box(b, Lb - 9.0, Lb, 156.0, 165.0, -(W_UPPER + 3.0), W_UPPER + 3.0, mat="rail", bevel=0.8)  # the crossbar
    for s in (1, -1):
        box(b, Lb - 10.0, Lb, 151.0, 165.5, s * (W_UPPER + 2.0), s * (W_UPPER + 5.5), mat="rail", bevel=1.0)
        for k in range(3):                                                    # the tab's grip ribs
            Lr = Lb - 8.5 + k * 3.0
            box(b, Lr, Lr + 1.4, 152.0, 164.5, s * (W_UPPER + 5.0), s * (W_UPPER + 6.3), mat="rail", bevel=0.3)
    return b.to_object("MP7A1_BOLT")


def build_foregrip():
    """The integral front grip, modelled folded where the photo shows it; foregrip_deployed swings it down."""
    b = Builder()
    slab(b, PL(FRONT_GRIP), half=W_FGRIP, bevel=3.0, res=1)
    return b.to_object("MP7A1_FOREGRIP")


def build_stock():
    """Butt plate and its two rods, modelled extended (STOCK_TRAVEL behind the collapsed position)."""
    b = Builder()
    slab(b, [P(L + STOCK_TRAVEL, H) for L, H in BUTT], half=W_BUTT, bevel=3.0, res=1)
    # The rods run 25 mm into the receiver (its back face is at L 385), so the extended stock has no gap; collapsed,
    # they reach L 137, still inside the upper receiver.
    for s in (1, -1):
        b.lathe("y", (s * 10.0, 0, 140.0 - H0), [(P(386.0 + STOCK_TRAVEL, 0)[0], 0),
                                                  (P(386.0 + STOCK_TRAVEL, 0)[0], 4.2),
                                                  (P(360.0, 0)[0], 4.2), (P(360.0, 0)[0], 0)], seg=10, mat="metal")
    return b.to_object("MP7A1_STOCK")


MAG_EXTRA = {20: 0.0, 30: 48.0, 40: 96.0}       # body length past the 20-round one (mm)
MAG_STRAIGHT = MAG_H - 4.5                       # straight inside the grip, down to the base plate of the 20-round
MAG_RADIUS = 400.0                               # the curve forward below the grip (30: ~7 degrees, 40: ~14)
# The 30 and 40-round magazines carry their lower part in a wider polymer sleeve, the base plate under it (H&K's own,
# from the user's photos, 2026-10-17): about a third / 44 % of the magazine's length, ~1 mm wider and 2 mm deeper a
# side than the metal body, a slightly raised rim at its top. The 20-round has none.
SLEEVE = {30: 50.0, 40: 86.0}


# The box magazines curve along their whole length, from the feed lips down (the user's photos of H&K's 30 and 40,
# 2026-10-17: "still look straight on the top"), on one radius: 20 ~10 degrees, 30 ~15, 40 ~20 in all. Each is then
# tilted back about its top so the part inside the grip has its chord on the grip's axis (it bows ~2 mm there; the
# grip has ~13 mm to spare either side). The drum's feed tower stays straight (mag_frame).
BOX_RADIUS = 560.0
BOX_TILT = -(MAG_STRAIGHT / BOX_RADIUS) / 2.0     # radians about X: the chord from the lips to the grip's bottom vertical


def mag_frame(s, box=False):
    """Centre (y, z) mm and forward tilt (radians) of the magazine's axis at distance s from its top, before a box
    magazine's tilt (box: curved from the top; otherwise straight inside the grip, MAG_RADIUS below it)."""
    if box:
        a = s / BOX_RADIUS
        return (BOX_RADIUS * (1 - math.cos(a)), -BOX_RADIUS * math.sin(a)), a
    if s <= MAG_STRAIGHT:
        return (0.0, -s), 0.0
    a = (s - MAG_STRAIGHT) / MAG_RADIUS
    return (MAG_RADIUS * (1 - math.cos(a)), -MAG_STRAIGHT - MAG_RADIUS * math.sin(a)), a


def box_local(y, z):
    """A point of a box magazine as built (tilted) -> (s along the axis from the top, u across it toward the muzzle)."""
    cb, sb = math.cos(-BOX_TILT), math.sin(-BOX_TILT)
    yy, zz = y * cb - z * sb, y * sb + z * cb             # undo the tilt
    s = BOX_RADIUS * np.arctan2(-zz, BOX_RADIUS - yy)     # the arc's centre of curvature is at (R, 0)
    u = BOX_RADIUS - np.hypot(BOX_RADIUS - yy, zz)
    return s, u


def mag_ring(bm, s, w, d, c, du=0.0, box=False):
    (cy, cz), a = mag_frame(s, box)
    ny, nz = math.cos(a), math.sin(a)                 # across the magazine, toward the muzzle
    sec = [(-w + c, -d), (w - c, -d), (w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c)]
    return [bm.verts.new((x, cy + (u + du) * ny, cz + (u + du) * nz)) for x, u in sec]


def sweep(b, s_list, w, d, c, mat, du=0.0, box=False):
    bm = b.bm
    rings = [mag_ring(bm, s, w, d, c, du, box) for s in s_list]
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for ra, rb in zip(rings, rings[1:]):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append(bm.faces.new((ra[k], ra[k1], rb[k1], rb[k])))
    b._finish([v for r in rings for v in r], faces, mat, 0.0, None)


def build_magazine(rounds):
    """Double-stack magazine, origin at the feed lips (top centre), curving toward the muzzle along its whole length
    (BOX_RADIUS) and tilted back so its part inside the grip sits on the grip's axis."""
    b = Builder()
    end = MAG_STRAIGHT + MAG_EXTRA[rounds]
    steps = [4.0 + k * 8.0 for k in range(int((end - 4.0) // 8.0) + 1)] + [end]
    sweep(b, sorted(set(round(s, 3) for s in steps)), 9.5, 18.0, 1.6, "magpoly", box=True)
    sweep(b, [0.0, 4.5], 7.0, 16.0, 1.5, "magpoly", box=True)                 # feed lips
    if rounds in SLEEVE:                                                        # lower polymer sleeve and its rim
        start = end - SLEEVE[rounds]
        sweep(b, sorted({round(start + k * 8.0, 3) for k in range(int(SLEEVE[rounds] // 8.0))} | {end}),
              10.6, 20.0, 2.0, "polymer", box=True)
        sweep(b, [start, start + 2.5], 10.9, 20.4, 2.0, "polymer", box=True)
    sweep(b, [end - 1.0, end + 4.0], 11.0, 20.5, 2.0, "magpoly", box=True)      # base plate
    # top round: steel-cored bullet forward, brass case
    b.lathe("y", (0, 0, -2.6), [(-17.5, 0), (-17.5, 4.0), (5.0, 4.0), (6.5, 2.4), (12.5, 2.4)], seg=8, mat="brass")
    b.lathe("y", (0, 0, -2.6), [(12.5, 2.4), (16.0, 2.0), (19.2, 0.7), (19.6, 0)], seg=8, mat="copper")
    tilt = rot_x(math.degrees(BOX_TILT))
    for v in b.bm.verts:
        v.co = tilt @ v.co
    return b.to_object("46x30Magazine%d_MP7" % rounds)


# 60-round drum (user, 2026-10-15; not an H&K part): a feed tower like the 20-round body up into the grip and a round
# drum under the grip facing front and back (its axis along the barrel: one round face toward the muzzle, one toward
# the shooter), its top just under the grip.
DRUM_R = 46.0                                    # 92 mm across
DRUM_HALF = 20.0                                 # 40 mm front to back (the magazine body is 36)
DRUM_Y = 4.0                                     # centre a little forward of the magazine axis
DRUM_Z = -(MAG_STRAIGHT + 3.0 + DRUM_R)          # top 1.5 mm under the grip's bottom


def build_drum():
    b = Builder()
    sweep(b, [4.0, MAG_STRAIGHT + 10.0], 9.5, 18.0, 1.6, "magpoly")             # feed tower, its foot inside the drum
    sweep(b, [0.0, 4.5], 7.0, 16.0, 1.5, "magpoly")                           # feed lips
    h, r = DRUM_HALF, DRUM_R
    c = (0, DRUM_Y, DRUM_Z)
    b.lathe("y", c, [(-h, 0), (-h, r - 6.0), (-h + 1.0, r - 2.5), (-h + 2.5, r), (h - 2.5, r), (h - 1.0, r - 2.5),
                     (h, r - 6.0), (h, 0)], seg=24, mat="magpoly")
    for sgn in (-1, 1):                                                         # hub caps on both faces
        b.lathe("y", c, [(sgn * h, 0), (sgn * h, 14.0), (sgn * (h + 1.5), 13.0), (sgn * (h + 1.5), 0)], seg=16,
                mat="magpoly")
    # winding key on the front face (toward the muzzle): a knob with a flat bar across it
    b.lathe("y", c, [(h + 1.5, 0), (h + 1.5, 7.0), (h + 5.0, 7.0), (h + 5.0, 0)], seg=12, mat="metal")
    b.box(-10.0, 10.0, DRUM_Y + h + 5.0, DRUM_Y + h + 8.0, DRUM_Z - 2.2, DRUM_Z + 2.2, mat="metal", bevel=0.6)
    b.lathe("y", (0, 0, -2.6), [(-17.5, 0), (-17.5, 4.0), (5.0, 4.0), (6.5, 2.4), (12.5, 2.4)], seg=8, mat="brass")
    b.lathe("y", (0, 0, -2.6), [(12.5, 2.4), (16.0, 2.0), (19.2, 0.7), (19.6, 0)], seg=8, mat="copper")
    return b.to_object("46x30Magazine60_MP7")


def build_suppressor():
    """Origin at `canon` (the nose plate's face); slides over the mount device on the flash hider."""
    b = Builder()
    L = 190.0
    b.lathe("y", (0, 0, 0), [(0, 0), (0, 7.2), (0, 13.5), (1.5, 15.0), (24, 15.0), (25.5, 16.5), (29, 17.2),
                              (L - 9, 17.2), (L - 4, 16.0), (L, 13.0), (L, 4.0), (L - 6, 3.2), (L - 6, 0)],
            seg=20, mat="suppressor")
    return b.to_object("MP7_Suppressor")


def build_mount():
    """Sleeve clamped over the barrel collar and the flash hider, origin at `canon`."""
    b = Builder()
    b.lathe("y", (0, 0, 0), [(-2.0, 0), (-2.0, 8.6), (-1.0, 9.6), (14.0, 9.6), (15.0, 9.0), (19.0, 9.0), (20.0, 9.6),
                              (50.0, 9.6), (51.5, 8.6), (51.5, 4.2), (44.0, 3.8), (44.0, 0)],
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
    # also used by build_p90.py / build_fiveseven.py (same glyphs as theirs)
    "N": ["101", "111", "111", "111", "101"], "E": ["111", "100", "110", "100", "111"],
    "R": ["110", "101", "110", "101", "101"], "G": ["111", "100", "101", "101", "111"],
    "I": ["111", "010", "010", "010", "111"], "D": ["110", "101", "101", "101", "110"],
    "Y": ["101", "101", "010", "010", "010"],
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


def rounded_rect(L, H, La, Lb, Ha, Hb, r):
    """Inside of a rounded rectangle in photo coordinates."""
    cl = np.clip(L, La + r, Lb - r)
    ch = np.clip(H, Ha + r, Hb - r)
    return (L >= La) & (L <= Lb) & (H >= Ha) & (H <= Hb) & (np.hypot(L - cl, H - ch) <= r)


def screw(col, L, H, sel, cL, cH, r=2.6):
    d = np.hypot(L - cL, H - cH)
    col[sel & (d < r) & (d > r - 0.9)] *= 0.4
    col[sel & (d <= r - 0.9)] += 10
    col[sel & (d < r - 1.7)] *= 0.35


def paint(maps, kind):
    """Final sRGB colour (0..255 float) for every texel of one baked object."""
    p, n, mat = maps["pos"], maps["nrm"], maps["mat"]
    ao_s, ao_b, edge = maps["occ"][..., 0], maps["occ"][..., 1], maps["occ"][..., 2]
    base = np.zeros(p.shape, np.float32)
    for i, name in enumerate(MATS):
        base[mat == i] = BASE[name]
    is_metal = (mat == MATS.index("metal")) | (mat == MATS.index("brass")) | (mat == MATS.index("copper"))
    col = base.copy()
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    L, H = L0 - y, z + H0                           # back to the photo's coordinates
    if kind == "stock":                             # the stock is modelled extended
        L = L - STOCK_TRAVEL
    side = np.abs(n[..., 0]) > 0.7
    left, right = n[..., 0] > 0.7, n[..., 0] < -0.7
    a2 = kind == "gun_a2"
    if kind in ("gun", "stock", "gun_a2"):
        lower = side & (np.abs(x) > W_LOWER - 0.6) & (H > 91) & (H < 135.5)
        upper = side & (np.abs(x) > W_UPPER - 0.6) & (H > 134.5) & (H < 167)
        grip = (mat == MATS.index("grip")) & side & (np.abs(x) > W_GRIP - 0.6)
        fgrip = (mat == MATS.index("polymer")) & side & (np.abs(x) > W_FGRIP - 0.6) & (H < 104) & (L < 181)
        # Grip: the panel of short vertical ribs, its border, the H&K MP7 moulding near the bottom.
        panel = grip & rounded_rect(L, H, 238.0, 283.0, 12.0, 80.0, 5.0)
        inner = rounded_rect(L, H, 239.5, 281.5, 13.5, 78.5, 4.0)
        col[panel & ~inner] += 12
        stag = np.mod(np.floor((L - 238.0) / 4.6), 2) * 4.5
        rib = panel & inner & (np.mod(L - 238.0, 4.6) < 1.7) & (np.mod(H - 12.0 + stag, 9.0) < 6.2) & (H > 28)
        col[rib] *= 0.6
        # Text reads the right way in game (game space is left-handed; CLAUDE.md "Handedness of the review renders"):
        # on the left side (+X) toward the rear (+L), on the right side toward the muzzle (-L). Fixed 2026-10-17: it
        # was written to read right in the mirrored review renders, so it read backwards in game.
        col[grip & left & text_mask(L, H, "MP7", 260.0, 18.5, 5.0)] += 26
        col[grip & right & text_mask(-L, H, "MP7", -264.0, 18.5, 5.0)] += 26
        # Receiver: seam, front vent slots, rear slots, the bolt-carrier recess, pins.
        col[side & (np.abs(H - 135.0) < 0.5) & (L > 56) & (L < 385)] *= 0.55
        for La, Lb in ((96.0, 108.0), (121.0, 140.0)):
            col[upper & rounded_rect(L, H, La, Lb, 153.5, 159.0, 2.7)] = 9
        for La, Lb in ((275.0, 286.0), (320.0, 331.0)):
            col[side & (np.abs(x) > W_UPPER - 0.6) & rounded_rect(L, H, La, Lb, 131.0, 136.0, 2.4)] = 9
        rec = lower & rounded_rect(L, H, 232.0, 302.0, 113.0, 128.0, 2.0)
        col[rec & ~rounded_rect(L, H, 233.2, 300.8, 114.2, 126.8, 1.4)] *= 0.5
        for cL, cH in ((380.0, 145.0), (380.0, 103.0)) + (() if a2 else ((104.7, 113.3),)):
            screw(col, L, H, side & (np.abs(x) > W_UPPER - 0.6), cL, cH, 2.4)
        # Selector marks on both sides: white safe symbol, red single, red row for auto.
        for m, c in ((rounded_rect(L, H, 270.0, 279.0, 108.0, 111.0, 0.8), (205, 205, 200)),
                     (rounded_rect(L, H, 271.0, 279.0, 101.5, 105.0, 0.8), (190, 40, 36)),
                     (rounded_rect(L, H, 264.5, 286.5, 94.8, 98.2, 0.8)
                      & (np.mod(L - 264.5, 5.5) < 4.6), (190, 40, 36))):
            col[lower & m] = c
        # Calibre on the left front, designation on the right upper.
        # (the A2's handguard covers the A1's spot: its calibre sits just behind it, as on the user's render)
        col[lower & left & text_mask(L, H, "4.6X30", 178.5 if a2 else 166.8, 120.5, 4.0)] += 30
        col[upper & right & text_mask(-L, H, "MP7A2" if a2 else "MP7A1", -170.0, 141.5, 5.0)] += 26
        # Ejection port on the right of the upper receiver.
        port = upper & right & (L > 196) & (L < 246) & (H > 139) & (H < 152)
        rim = upper & right & (L > 194.5) & (L < 247.5) & (H > 137.5) & (H < 153.5) & ~port
        col[port] = col[port] * 0.25 + np.array([4, 4, 5])
        col[rim] += 16
        # Folded front grip: grooves, the release button, the serrated catch at its rear.
        for hh in (80.0, 85.0, 90.0):
            col[fgrip & (L > 112) & (L < 166) & (np.abs(H - hh) < 0.5)] *= 0.5
        db = np.hypot(L - 101.5, H - 89.5)
        col[fgrip & (db < 6.2) & (db > 5.2)] *= 0.4
        col[fgrip & (db <= 5.2)] += 12
        col[fgrip & (L > 158) & (L < 178) & (H > 95.5) & (np.mod(L, 3.0) < 1.2)] *= 0.55
        # Flash hider slots and the bore; side rail screws.
        metal = mat == MATS.index("metal")
        r = np.hypot(x, z - BORE_Z)
        a = np.arctan2(x, z - BORE_Z)
        slot = metal & (L > 4) & (L < 30) & (r > 6.3) & (np.abs(np.mod(a * 6 / (2 * math.pi), 1.0) - 0.5) < 0.09)
        col[slot] = 9
        col[metal & (r < 3.2) & (L < 10.5)] = 8
        rail_side = (mat == MATS.index("rail")) & side & (np.abs(x) > W_LOWER + 0.4)
        if a2:
            plate = (mat == MATS.index("metal")) & side & (np.abs(x) > W_LOWER + 0.4)
            for cL, cH in A2_SCREWS:                      # the handguard's cap screws, either side
                screw(col, L, H, plate, cL, cH, 3.0)
        else:
            for cL in (SIDE_RAIL_L[0] + 1.5, SIDE_RAIL_L[1] - 1.5):
                screw(col, L, H, rail_side, cL, SIDE_RAIL_H, 2.2)
        # Stock: the two holes through the butt plate, the rubber pad at its rear.
        if kind == "stock":
            for cH in (46.5, 55.5):
                col[side & (np.hypot(L - 397.0, H - cH) < 2.6)] = 9
            col[L > 410.5] *= 0.85
    elif kind == "drum":
        dx, dz = x, z - DRUM_Z
        r = np.hypot(dx, dz)
        front, rear = n[..., 1] > 0.7, n[..., 1] < -0.7
        face = (front | rear) & (np.abs(y - DRUM_Y) > DRUM_HALF - 0.3) & (r < DRUM_R - 2.0)
        col[face & (np.abs(r - 39.0) < 0.8)] *= 0.55                      # groove round the face
        col[face & (np.abs(r - 14.5) < 0.6)] *= 0.6                       # around the hub cap
        # "60", upright, under the hub: from behind the gun's right (-X) is on the viewer's right, so it reads toward -X
        for f, u in ((face & rear, -dx), (face & front, dx)):
            col[f & text_mask(u, dz, "60", -6.8, -31.0, 9.0)] = (190, 190, 184)
        rib = side & (np.abs(np.abs(y) - 13.0) < 0.9) & (z < -12) & (z > -MAG_STRAIGHT + 8)
        col[rib] *= 0.72
    elif kind.startswith("mag"):
        rounds = int(kind[3:])
        end = MAG_STRAIGHT + MAG_EXTRA[rounds]
        s_ax, u = box_local(y, z)                          # along the curved axis from the top / across, toward the muzzle
        back = end - s_ax                                  # distance up from the end
        if rounds in SLEEVE:
            # the polymer sleeve (user's photos): witness slot near its top, the capacity moulded beside it, "MADE IN
            # GERMANY" and the calibre near the bottom, a round mark on the 40's; a faint grey-green tint. Text reads
            # the right way in game: on the left side (+X) toward the rear (-u), on the right side toward the muzzle.
            sl = (mat == MATS.index("polymer")) & side
            top = SLEEVE[rounds]
            col[sl] *= np.array([0.95, 1.0, 0.96])
            col[sl & rounded_rect(u, back, 0.4, 3.8, top - 18.0, top - 7.0, 1.7)] = 10
            for face, uu in ((sl & left, -u), (sl & right, u)):
                col[face & text_mask(uu, back, str(rounds), -15.0, top - 11.0, 4.0)] += 34
                col[face & text_mask(uu, back, "MADE IN GERMANY", -15.0, 11.5, 2.2)] += 24
                col[face & text_mask(uu, back, "4.6X30", -8.0, 7.0, 2.2)] += 24
            if rounds == 40:
                col[sl & (np.abs(np.hypot(u - 2.0, back - top * 0.42) - 2.6) < 0.5)] *= 0.5
        else:
            # capacity ticks (2 white bars) on both sides above the base plate, readable at 128 px
            for k in range(rounds // 10):
                tick = side & (np.abs(back - (9.0 + k * 3.6)) < 0.9) & (np.abs(u + 4.0) < 6.0)
                col[tick] = (190, 190, 184)
        # pressing ribs along the part inside the grip, the witness slot near the top
        rib = side & (np.abs(np.abs(u) - 13.0) < 0.9) & (s_ax > 12) & (s_ax < MAG_STRAIGHT - 8)
        col[rib] *= 0.72
        col[side & (np.abs(u + 2.0) < 1.2) & (s_ax > 18) & (s_ax < 34)] *= 0.4
    elif kind == "suppressor":
        r = np.hypot(x, z)
        knurl = (y > 2) & (y < 23) & (r > 14)
        col[knurl] *= (0.65 + 0.6 * ((np.mod(y[knurl], 2.0) < 1.0) ^ (np.mod(np.arctan2(x[knurl], z[knurl]) * 17.2
                                                                             / math.pi, 1.0) < 0.5)))[..., None]
        band = (np.abs(y - 26.8) < 0.7) | (np.abs(y - 182.0) < 0.6)
        col[band & (r > 15)] *= 0.5
        ang = np.arctan2(x, -z)
        tx = text_mask(-y, ang * 17.2, "4.6X30", -98.8, -3.0, 6.0)       # same span, y 70-98.8, read the right way
        col[tx & (r > 16.5)] = col[tx & (r > 16.5)] * 0.3 + 120
        col[(r < 3.5) & (y > 185)] = 8
    elif kind == "mount":
        r = np.hypot(x, z)
        ang = np.mod(np.arctan2(x, z) / (2 * math.pi) * 6.0, 1.0)
        slot = (y > 24) & (y < 42) & (r > 9.2) & (np.abs(ang - 0.5) < 0.14)
        col[slot] = 10
        flats = (y > 1) & (y < 13) & (r > 9.2) & (np.abs(np.mod(np.arctan2(x, z) / (2 * math.pi) * 2, 1) - .5) < .12)
        col[flats] += 20
        col[r < 4.4] = 9
    # Grain, light, AO and edge highlights: flat panels, light occlusion, bright edges (GoM's look, as on the P90).
    mott = vnoise(p, 6.0, 1) * 0.6 + vnoise(p, 1.6, 2) * 0.4
    col *= (0.9 + 0.2 * mott)[..., None]
    streak = vnoise(p * np.array([1.0, 0.08, 1.0]), 0.8, 3)
    col[is_metal] *= (0.92 + 0.16 * streak[is_metal])[..., None]
    col *= (0.99 + 0.08 * np.clip(n[..., 2], -1, 1))[..., None]
    occ = (0.7 + 0.3 * np.clip(ao_b, 0, 1) ** 1.3) * (0.74 + 0.26 * np.clip(ao_s, 0, 1))
    col *= occ[..., None]
    e = np.clip(edge * 9.0, 0, 1)
    convex = e * np.clip((ao_s - 0.55) / 0.4, 0, 1)
    wear = np.where(is_metal | (mat == MATS.index("rail")), 78.0, 62.0) * (0.75 + 0.5 * vnoise(p, 2.5, 5))
    col += (convex * wear)[..., None] * np.array([1.0, 1.0, 1.04])
    col *= (1.0 - 0.35 * e * (1 - np.clip((ao_s - 0.4) / 0.4, 0, 1)))[..., None]
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


# Held like a pistol: GoM's handgun-held guns (pistols, MP5K, TEC9, MAC10; SwingAnim = Handgun) are modelled upside
# down, turned 180 degrees about the barrel axis (game x -> -x, z -> -z) around the same rear-top-of-grip origin, and
# their attachment points with them; a part modelled upright gets rotate (-180, 0, -180) (= that turn), as on the
# MP5K's rail_up / scope. The MP7 and the P90 are built and baked upright and turned only at export (points(), main()).
TURN = [-180.0, 0.0, -180.0]


def turned(point, part=True):
    """An upright point in the handgun-held model: offset x, z negated, an upright part turned with the gun."""
    x, y, z = point["offset"]
    out = {"offset": [round(-x, 4) + 0.0, y, round(-z, 4) + 0.0]}
    if "rotate" in point:
        out["rotate"] = point["rotate"]
    elif part:
        out["rotate"] = list(TURN)
    return out


def handgun_points(pts):
    """Turn upright points for the handgun-held model, add the floor pose and the back-slot points."""
    pts = {k: turned(v) for k, v in pts.items()}
    # floor pose of GoM's handgun-held SMGs (MP5K, TEC9, MAC10), its height off the floor scaled with the gun from the
    # 0.72 they are drawn at
    pts["world"] = {"offset": [round(-0.025 * K / 0.00072, 4), 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}
    # Carried on the back like a rifle (never in a holster): the body's rifle points expect an upright rifle model,
    # and an attached item's own attachment of the same name is applied on top, so these turn the gun back upright
    # (a half turn is its own inverse, so it does not matter whether the engine inverts it).
    for name in ("rifle_back", "rifle_back_bag"):
        pts[name] = {"offset": [0.0, 0.0, 0.0], "rotate": list(TURN)}
    return pts


def points(bounds, a2=False):
    rail_top = (RAIL_TOP_H - H0) * K
    side = (A2_SIDE_RAIL_X if a2 else SIDE_RAIL_X) * K
    ry = round((L0 - sum(A2_SIDE_RAIL_L if a2 else SIDE_RAIL_L) / 2) * K, 4)
    rz = round(((A2_SIDE_RAIL_H if a2 else SIDE_RAIL_H) - H0) * K, 4)
    oy = round((L0 - 219.0) * K, 4)                 # optics over the trigger, mid-rail (as before)
    my, mz = P(MAG_L, MAG_H)
    cy, cz = P(CANON_L, BORE_H)
    pts = {
        "muzzle": {"offset": [0.0, round(L0 * K, 4), round(BORE_Z * K, 4)], "rotate": [-90.0, 0.0, -180.0]},  # as MP5K
        "magazine": {"offset": [0.0, round(my * K, 4), round(mz * K, 4)]},
        # GoM's Picatinny_Rail_Up spans z -0.0011..0.0055 from rail_up and MP5's scope sits 0.0032 under that
        # rail's top: the same relations on the integral rail.
        "rail_up": {"offset": [0.0, oy, round(rail_top - 0.0055, 4)]},
        "scope": {"offset": [0.0, oy, round(rail_top - 0.0032, 4)]},
        "rail_left": {"offset": [round(side - 0.0055, 4), ry, rz]},
        "rail_right": {"offset": [round(-(side - 0.0055), 4), ry, rz]},
        # MP5: light_left = rail_left + 0.0062 x, laser_right = rail_right - 0.0073 x, 0.0008 lower
        "light_left": {"offset": [round(side - 0.0055 + 0.0062, 4), ry, rz]},
        "laser_right": {"offset": [round(-(side - 0.0055 + 0.0073), 4), ry, round(rz - 0.0008, 4)]},
        "canon": {"offset": [0.0, round(cy * K, 4), round(cz * K, 4)], "rotate": [0.0, 0.0, 0.0]},  # round: GoM 0
        # the bolt and the stock are nodes of the gun's own file, turned with it
        "bolt_fired": {"offset": [0.0, round(-CH_TRAVEL * K, 4), 0.0], "rotate": [0.0, 0.0, 0.0]},
        "stock_folded": {"offset": [0.0, round(STOCK_TRAVEL * K, 4), 0.0], "rotate": [0.0, 0.0, 0.0]},
    }
    # Front grip unfolded: a turn about X through the hinge, offset = hinge - R . hinge (the engine draws a part at
    # offset + rotateXYZ . vertex). Upright, +90 swings the grip's rear end down; turned() keeps a given rotate as it
    # is, so it is written already turned: the half turn about Y flips the sign of a turn about X.
    if a2:
        # Bottom rail, for GoM's foregrips: its Picatinny_Rail_Down spans z -0.0055..0.0011 from rail_down, and the
        # MP5's foregrip point sits 0.003 above that rail's bottom (the clamp round the crossbars); the same relations
        # on the integral rail, the grip in the rail's forward third.
        bottom = (A2_BOTTOM_RAIL_BOTTOM - H0) * K
        pts["rail_down"] = {"offset": [0.0, round((L0 - sum(A2_BOTTOM_RAIL_L) / 2) * K, 4), round(bottom + 0.0055, 4)]}
        pts["foregrip"] = {"offset": [0.0, round((L0 - A2_FOREGRIP_L) * K, 4), round(bottom + 0.003, 4)]}
    else:
        hy, hz = [c * K for c in P(*FGRIP_HINGE)]
        pts["foregrip_deployed"] = {"offset": [0.0, round(hy + hz, 4), round(hz - hy, 4)],
                                    "rotate": [-FGRIP_ANGLE, 0.0, 0.0]}
    pts = handgun_points(pts)
    pts["_bounds"] = bounds
    pts["_notes"] = {
        "units": "game units (0.603 of real size, the M16A2's proportion); +Y muzzle; held like a pistol, so modelled upside down as GoM's "
                 "handgun-held guns are: +Z the gun's BOTTOM, +X its RIGHT; origin = rear-top of grip "
                 "(photo L %.0f, H %.1f)" % (L0, H0),
        "rifle_back": "rifle_back / rifle_back_bag (vanilla's Rifle On Back locations) turn the upside-down model "
                      "upright when it hangs in the back slot",
        "turned": "parts modelled upright (magazines, GoM optics / lights / lasers) get rotate -180 0 -180, as on "
                  "GoM's MP5K; render_mp7.py / make_mp7_art.py turn everything back for display",
        "magazine": "magazine meshes hang straight down from the feed lips inside the grip and curve toward the "
                    "muzzle below it (30 / 40 rounds), modelled upright",
        "canon": "the nose plate's face where the barrel leaves it; MP7_Muzzle_Mount_Device and MP7_Suppressor have "
                 "their origin there and extend along +Y over the flash hider",
        "bolt_fired": "charging handle pulled back 50 mm real; the real MP7 handle does not reciprocate",
        "stock_folded": "MP7A1_STOCK is modelled extended; this offset slides it in (223 mm real)",
    }
    if a2:
        pts["_notes"]["a2"] = ("MP7A2: the A1's points with the side rails on the handguard; rail_down / foregrip "
                               "under it for GoM's foregrips (upright parts, turned with the gun); bolt and stock are "
                               "the A1's nodes (MP7A1_BOLT / MP7A1_STOCK)")
    else:
        pts["_notes"]["foregrip_deployed"] = ("MP7A1_FOREGRIP is modelled folded (drawn folded at the gun's origin); "
                                              "this turns it %.0f degrees down about its hinge pin (photo L %.1f, "
                                              "H %.1f)" % ((FGRIP_ANGLE,) + FGRIP_HINGE))
    pts["_extras"] = {"handgun_hold": True, "photo_origin_mm": [L0, H0], "real_mm_per_game_unit": round(1.0 / K, 2)}
    return pts


def bounds_of(ob, offset=(0, 0, 0)):
    vs = [(v.co.x, v.co.y, -v.co.z) for v in ob.data.vertices]
    mn = [round(min(v[i] for v in vs) + offset[i], 4) for i in range(3)]
    mx = [round(max(v[i] for v in vs) + offset[i], 4) for i in range(3)]
    return {"min": mn, "max": mx, "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons)}


def bounds_at(ob, point):
    """bounds_of() for a node drawn at an attachment point (offset + rotateXYZ, game space)."""
    rx, ry, rz = [math.radians(a) for a in point["rotate"]]
    xf = (Matrix.Translation(Vector(point["offset"])) @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Rotation(ry, 4, 'Y')
          @ Matrix.Rotation(rz, 4, 'Z'))
    vs = [xf @ Vector((v.co.x, v.co.y, -v.co.z)) for v in ob.data.vertices]
    return {"min": [round(min(v[i] for v in vs), 4) for i in range(3)],
            "max": [round(max(v[i] for v in vs), 4) for i in range(3)],
            "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons)}


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

    body, bolt, stock, fgrip = build_body(), build_bolt(), build_stock(), build_foregrip()
    mags = [build_magazine(r) for r in (20, 30, 40)] + [build_drum()]
    supp, mount = build_suppressor(), build_mount()

    unwrap([body, bolt, stock, fgrip], 0.006)
    for o in mags + [supp, mount]:
        unwrap([o], 0.012)

    os.makedirs(TEX_DIR, exist_ok=True)
    # The front grip is baked on its own and the body without it: either face of the grip and the recess it folds
    # into are seen once it is unfolded, so neither may carry the other's shadow.
    texture([body, bolt, stock, fgrip], [[body, bolt], [body, bolt], [stock], [fgrip]], ["gun", "gun", "stock", "gun"],
            256, os.path.join(TEX_DIR, "MP7A1.png"))
    for r, m in zip((20, 30, 40, 60), mags):
        texture([m], [[m]], ["drum" if r == 60 else "mag%d" % r], 128,
                os.path.join(TEX_DIR, "46x30Magazine%d_MP7.png" % r))
    texture([supp], [[supp]], ["suppressor"], 128, os.path.join(TEX_DIR, "MP7_Suppressor.png"))
    texture([mount], [[mount]], ["mount"], 128, os.path.join(TEX_DIR, "MP7_Muzzle_Mount_Device.png"))

    # MP7A2: its own body and texture; bolt, stock, magazines and muzzle parts are the A1's.
    body2 = build_body(a2=True)
    unwrap([body2], 0.006)
    texture([body2], [[body2, bolt]], ["gun_a2"], 256, os.path.join(TEX_DIR, "MP7A2.png"))

    for o in (body, bolt, stock, fgrip, body2):                # held like a pistol: turned 180 degrees about the bore axis
        o.data.transform(Matrix.Diagonal((-1.0, 1.0, -1.0, 1.0)))
    bounds = {o.name: bounds_of(o) for o in [body, bolt, stock, fgrip] + mags + [supp, mount]}
    bounds["MP7A1_STOCK_folded"] = bounds_of(stock, (0, STOCK_TRAVEL * K, 0))
    pts = points(bounds)
    bounds["MP7A1_FOREGRIP_deployed"] = bounds_at(fgrip, pts["foregrip_deployed"])
    with open(POINTS_JSON, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    bounds2 = {o.name: bounds_of(o) for o in [body2, bolt, stock]}
    with open(POINTS_JSON_A2, "w") as fh:
        json.dump(points(bounds2, a2=True), fh, indent=2)
        fh.write("\n")

    export([body, bolt, stock, fgrip], FBX_GUN)
    export([body2], FBX_GUN_A2)
    export(mags, FBX_MAGS)
    export([supp, mount], FBX_PARTS)
    for name, b in list(bounds.items()) + [("MP7A2_BODY", bounds2["MP7A2_BODY"])]:
        print("%-28s tris %5d  min %s  max %s" % (name, b["tris"], b["min"], b["max"]))


if __name__ == "__main__":
    main()
