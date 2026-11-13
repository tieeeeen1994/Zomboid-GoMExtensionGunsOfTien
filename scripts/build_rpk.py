"""The RPK and RPK-74 from Guns of Marz's own AK-47 and AK-74 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_rpk.py

User, 2026-11-02 (docs/design.md 4j): Kalashnikov's squad machine guns of 1961 (7.62x39mm) and 1974 (5.45x39mm),
main mod, built on GoM's AKs so they look like GoM's and take GoM's magazines. What sets an RPK apart from its AK,
read from the references (references/rpk, not in the repo: Commons "7.62mm light machine gun RPK.png", right side,
CC BY-SA 3.0, levelled by 10.4 degrees; "Soviet RPK-74.JPEG", left side, public domain) and Wikipedia's figures:
- the barrel: 590 mm against the AK's 415, so everything ahead of the gas block (the bare barrel, the cleaning rod,
  the front sight block, the muzzle) moves 175 mm forward and the barrel and rod stretch over the gap. The RPK-74's
  muzzle device is short (1060 mm overall against the AK-74's 943 + 175): the AK-74's brake is squeezed to MUZZLE_74.
- the club-foot stock: GoM's AK stock is sliced every STOCK_STEP mm along its length and each slice's heights
  mapped from the AK's outline to the RPK's (STOCK_PROFILE, measured on the levelled RPK photo, mm against the bore,
  over the stock's length), so the stock keeps GoM's UVs and wood.
- the folding bipod clamped behind the front sight block (new geometry, textured from each gun's bare barrel steel),
  two nodes in the gun's space (drawn at the origin, GoM's M60 way and our M249's): folded back under the barrel, or
  deployed with the legs splayed.
- the RPK's 40-round box: GoM's 762x39Magazine30 bent on along its own arc (the real one is the 30 made longer on the
  same curve), as GoM's magazines with the feed lips at the origin.
- the RPK's 75-round drum (DRUM_*): GoM's 30's header on a feed tower, a steel drum facing forward as GoM's drums do,
  stepped (tapered) toward its front face, leaning forward as GoM's AK-74 drum, on a texture of its own
  (drum_texture()).
Everything is then scaled by SCALE = 0.603 / GoM's 0.645 (GoM draws both AKs at 0.644 / 0.646 of real length: AK-47
0.5605 for 870 mm, AK-74 0.6089 for 943), the M16A2 proportion every Guns of Tien gun is drawn at; GoM's magazines are
drawn on them through `_GoT` models of the same scale (gen_scripts.py rpk()).

Writes:
    media/models_X/weapons/firearms/GunsOfTien_RPK.fbx       RPK_BODY / RPK_BOLT / RPK_BIPOD_FOLDED / _DEPLOYED,
                                                             RPK74_BODY / RPK74_BOLT / RPK74_BIPOD_FOLDED / _DEPLOYED
    media/models_X/weapons/magazines/GunsOfTien_RPK_magazines.fbx   762x39Magazine40_RPK, 762x39Drum75_RPK
    media/textures/weapons/GunsOfTien/762x39Drum75_RPK.png  the drum's texture (256, RGB)
    scripts/rpk_points.json                                  each model's points (GoM's x SCALE, the muzzle ones moved)
The guns keep GoM's textures (weapons/firearms/assault_rifles/AK47 / AK74), the 40 GoM's 30's.
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
OUT_GUNS = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_RPK.fbx")
OUT_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_RPK_magazines.fbx")
POINTS = os.path.join(HERE, "rpk_points.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

R = 0.000645                    # GoM's AKs: game units per real mm
SCALE = round(0.603 / 0.645, 4)
STRETCH = 175.0                 # RPK barrel 590 mm, AK 415 (Wikipedia)
STOCK_STEP = 4.0                # mm between stock slices
# Per gun: GoM's model, ours, everything ahead of `cut` (mm from the grip) moves STRETCH forward; the front sight
# block's rear (bipod clamp behind it); the steel patch of GoM's texture the bipod is painted from (u0, v0, u1, v1:
# the AK-47's bare barrel strip, the AK-74's barrel band)
GUNS = {
    "RPK": {"gom": "AK47", "cut": 565.0, "sight": 599.0, "steel": (1 / 256, 0.47, 15 / 256, 0.98)},
    "RPK74": {"gom": "AK74", "cut": 565.0, "sight": 596.0, "steel": (95 / 256, 0.84, 250 / 256, 0.90)},
}
MUZZLE_74 = (621.0, 0.45)       # the AK-74 brake ahead of 621 mm squeezed to 45 % (38 mm, the RPK-74's short device)
# The RPK's stock, measured on the levelled photo: (t, height in mm against the bore), t = 0 at the receiver's rear,
# 1 at the butt (217 mm). Top: the comb falls 30 mm; bottom: the wrist under the receiver, then the club foot.
STOCK_TOP = [(0.0, -3.1), (0.34, -14.3), (0.65, -22.4), (1.0, -30.0)]
STOCK_BOTTOM = [(0.0, -46.0), (0.13, -54.6), (0.28, -64.5), (0.36, -73.5), (0.40, -86.0), (0.425, -99.4),
                (0.435, -117.3), (0.455, -126.3), (0.50, -133.0), (0.65, -135.3), (0.94, -137.5), (1.0, -138.0)]
# The bipod (mm): clamp, legs (photo: 325 mm from the hinge to the foot, 10 mm rods), feet
CLAMP_LEN, LEG_LEN, LEG_R, FOOT = 24.0, 325.0, 4.5, (34.0, 22.0, 3.0)
SPLAY, RAKE = 13.0, 4.0         # deployed: each leg out from the vertical, and forward (degrees)
MAG_FACTOR = 1.42               # the 40's arc below the header against the 30's ((40 - 6) / (30 - 6) rounds)
MAG_SPLIT = -160.0              # degrees about the arc's centre where the header ends (rear edge -166 at its foot)
# The RPK's 75-round drum (user, 2026-11-02; references/rpk: Commons "Izhmash museum 1.jpg" and "Operation Charkh
# Restoration 110405-A-CA126-060.jpg", both three-quarter views; Small Arms Review "AK-74 Drum Magazines": the Soviet
# drum is spot-welded steel, "tapered", its feed tower "attached to the main body at an angle" so that the body "is
# angled forward" on the rifle, a loading lever on its front; KCI's copy about 7 x 3 in, 2.1 lb). Like GoM's own drums
# (its AK-74 100 and Thompson 100) it faces forward: its round faces look along the barrel, so from the side it shows
# its ribbed band. Its axis leans DRUM_TILT degrees (front face up, the body's bottom forward) as GoM's AK-74 drum's
# (measured: 30, middle 32 mm ahead of and 117 below the lips, 190 across, 86 deep). The photos' round face with the
# winding hub is the front face seen at an angle, the stepped rings the tapered band (user, 2026-11-02: the first
# build, faces to the sides, was wrong). The tower's top is GoM's 30's header (feed lips, catch), so it seats as GoM's
# magazines do. Real mm from the feed lips (game y forward, z up); a profile point is (radius, a), a along the axis
# (front +), from the front hub round the steps and band to the rear face's middle.
DRUM_CENTRE = (32.0, -120.0)
DRUM_TILT = 30.0
DRUM_PROFILE = [(0.0, 43.0), (16.0, 43.0), (16.0, 39.0), (75.0, 39.0), (75.0, 30.0), (79.0, 30.0), (79.0, 20.0),
                (83.0, 20.0), (83.0, 8.0), (87.5, 8.0), (87.5, -38.0), (0.0, -38.0)]
DRUM_TOWER = (-32.5, 39.5, 14.5, -40.0, -82.0)   # y rear, y front, half-width, top z, bottom z (into the disc):
                                                  # GoM's 30 is 31.5 / 38.6 mm either side of the lips, 29 mm wide
DRUM_HEADER_Z = -46.0           # GoM's 30 kept above this (its header: lips, catch lug, the top of the body)
DRUM_SEGMENTS = 32


def lerp_profile(prof, t):
    t = min(max(t, prof[0][0]), prof[-1][0])
    for (t0, h0), (t1, h1) in zip(prof, prof[1:]):
        if t <= t1:
            return h0 + (h1 - h0) * (t - t0) / ((t1 - t0) or 1.0)
    return prof[-1][1]


def islands(bm):
    """Connected vertex sets."""
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop()
            comp.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    stack.append(b)
        out.append(comp)
    return out


def gy(v):          # game y / z of a raw vertex, in real mm at GoM's scale
    return v.co.y / R


def gz(v):
    return -v.co.z / R


def set_gyz(v, y=None, z=None):
    if y is not None:
        v.co.y = y * R
    if z is not None:
        v.co.z = -z * R


# GoM's AK triggers sit 3-3.6 mm (at our size) ahead of where the RPK / RPK-74 photos have the blade (trigger audit
# 2026-11-13, user: "the triggers you make are not good"; references/rpk/rpk_level.png and Soviet_RPK-74.jpg
# registered on the guns): moved back along the bore, in GoM's mm before SCALE.
TRIGGER_MOVE = {"RPK": -3.0 / SCALE, "RPK74": -3.6 / SCALE}


def move_trigger(bm, dy):
    """GoM's AK trigger: the thin island (|x| < 4.5 mm) hanging into the guard, 20-40 vertices."""
    for c in islands(bm):
        ys, zs = [gy(v) for v in c], [gz(v) for v in c]
        if (20 <= len(c) <= 40 and max(abs(v.co.x) for v in c) / R < 4.5 and 70.0 < min(ys) and max(ys) < 120.0
                and 18.0 < max(ys) - min(ys) < 40.0 and min(zs) < -30.0):
            for v in c:
                v.co.y += dy * R
            print("trigger moved %.1f mm" % dy)
            return
    raise RuntimeError("GoM's AK trigger island not found")


def bore_z(bm):
    """The bore height and the bare barrel's radius (mm): the longest piece starting ahead of the receiver is the
    barrel (the receiver end to the muzzle in one), its last ring behind the front sight block the bare barrel's."""
    barrel = max((c for c in islands(bm) if min(gy(v) for v in c) > 200.0),
                 key=lambda c: max(gy(v) for v in c) - min(gy(v) for v in c))
    y_ring = max(gy(v) for v in barrel if gy(v) < 601.0)
    ring = [v for v in barrel if abs(gy(v) - y_ring) < 1.0]
    zs = [gz(v) for v in ring]
    print("barrel ring", len(ring), sorted({round(gy(v)) for v in ring}))
    return (min(zs) + max(zs)) / 2.0, (max(zs) - min(zs)) / 2.0


def stock(bm, bore):
    """Slice GoM's stock and map every slice's heights onto the club-foot outline."""
    parts = [c for c in islands(bm) if max(gy(v) for v in c) < 12.0 and min(gy(v) for v in c) < -150.0]
    verts = {v for c in parts for v in c}
    y_front = max(gy(v) for v in verts)
    y_rear = min(gy(v) for v in verts)
    geom = list(verts) + list({e for v in verts for e in v.link_edges}) + list({f for v in verts for f in v.link_faces})
    y = y_rear + STOCK_STEP
    while y < y_front - 1.0:
        res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=(0.0, y * R, 0.0), plane_no=(0.0, 1.0, 0.0))
        geom = list(set(geom) | set(res["geom"]) | set(res["geom_cut"]))
        y += STOCK_STEP
    bm.verts.ensure_lookup_table()
    verts = [g for g in geom if isinstance(g, bmesh.types.BMVert)]
    # the AK's outline per slice: lowest and highest vertex within half a step
    cols = {}
    for v in verts:
        k = round((gy(v) - y_rear) / STOCK_STEP)
        lo, hi = cols.get(k, (1e9, -1e9))
        cols[k] = (min(lo, gz(v)), max(hi, gz(v)))
    keys = sorted(cols)
    # GoM's AK-47 butt is slanted (bottom corner 18 mm ahead of the top): behind the bottom corner a slice cuts the
    # rear face, so its outline is taken where the slant starts (else the face folds onto the new bottom line)
    z_min = min(gz(v) for v in verts)
    y_slant = min(gy(v) for v in verts if gz(v) < z_min + 2.0)

    def outline(yv):
        k = (max(yv, y_slant) - y_rear) / STOCK_STEP
        k0 = max(keys[0], min(keys[-1], math.floor(k)))
        k1 = min(keys[-1], k0 + 1)
        a, b = cols[k0], cols.get(k1, cols[k0])
        f = min(max(k - k0, 0.0), 1.0)
        return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f

    for v in verts:
        yv, zv = gy(v), gz(v)
        t = (y_front - yv) / (y_front - y_rear)
        lo, hi = outline(yv)
        nlo, nhi = bore + lerp_profile(STOCK_BOTTOM, t), bore + lerp_profile(STOCK_TOP, t)
        f = min(max((zv - lo) / ((hi - lo) or 1.0), 0.0), 1.0)     # no spikes where a slice is thin
        set_gyz(v, z=nlo + (nhi - nlo) * f)
    return y_front, y_rear


def lengthen(bm, spec, gun):
    for v in bm.verts:
        y = gy(v)
        if gun == "RPK74" and y > MUZZLE_74[0]:
            y = MUZZLE_74[0] + (y - MUZZLE_74[0]) * MUZZLE_74[1]
        if y > spec["cut"]:
            y += STRETCH
        set_gyz(v, y=y)


def add_box(bm, uv, steel, centre, size, rot=Matrix.Identity(3)):
    """A box in game mm (centre, size) turned by rot about its centre, painted from the steel patch."""
    hx, hy, hz = [s / 2.0 for s in size]
    corners = [Vector((sx * hx, sy * hy, sz * hz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    vs = []
    for c in corners:
        p = Vector(centre) + rot @ c
        vs.append(bm.verts.new((p.x * R, p.y * R, -p.z * R)))
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    paint(bm, uv, steel, [bm.faces.new([vs[i] for i in f]) for f in faces])


def add_rod(bm, uv, steel, a, b, r, sides=8):
    """A rod from a to b (game mm), radius r."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d)
    ring = lambda c: [bm.verts.new(((c + r * (math.cos(2 * math.pi * i / sides) * side
                                              + math.sin(2 * math.pi * i / sides) * up)).x * R,
                                    (c + r * (math.cos(2 * math.pi * i / sides) * side
                                              + math.sin(2 * math.pi * i / sides) * up)).y * R,
                                    -(c + r * (math.cos(2 * math.pi * i / sides) * side
                                               + math.sin(2 * math.pi * i / sides) * up)).z * R))
                      for i in range(sides)]
    ra, rb = ring(a), ring(b)
    faces = [bm.faces.new((ra[i], ra[(i + 1) % sides], rb[(i + 1) % sides], rb[i])) for i in range(sides)]
    faces.append(bm.faces.new(list(reversed(ra))))
    faces.append(bm.faces.new(rb))
    paint(bm, uv, steel, faces)


def paint(bm, uv, steel, faces):
    """UVs inside the steel patch: each face spread over a small square of it, so the steel's grain shows."""
    u0, v0, u1, v1 = steel
    for i, f in enumerate(faces):
        fu = u0 + (u1 - u0) * ((i * 0.37) % 0.8)
        fv = v0 + (v1 - v0) * ((i * 0.61) % 0.8)
        du, dv = (u1 - u0) * 0.2, (v1 - v0) * 0.2
        for j, loop in enumerate(f.loops):
            loop[uv].uv = (fu + du * (j in (1, 2)), fv + dv * (j in (2, 3)))


def bipod(name, spec, bore, barrel_r, muzzle_y, deployed):
    """The bipod in the gun's space: a clamp behind the front sight block, a hinge under it, two legs and feet."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    steel = spec["steel"]
    c1 = spec["sight"] + STRETCH
    c0 = c1 - CLAMP_LEN
    yc = (c0 + c1) / 2.0
    w = 2 * (barrel_r + 3.0)
    add_box(bm, uv, steel, (0, yc, bore), (w, CLAMP_LEN, w))                       # clamp round the barrel
    hinge_z = bore - barrel_r - 9.0
    add_box(bm, uv, steel, (0, yc, hinge_z), (w + 6.0, 14.0, 9.0))                  # hinge block
    for s in (-1, 1):
        top = Vector((s * 7.0, yc, hinge_z))
        if deployed:
            d = Vector((s * math.sin(math.radians(SPLAY)), math.sin(math.radians(RAKE)), -1.0)).normalized()
            foot = top + d * LEG_LEN
            add_rod(bm, uv, steel, top, foot, LEG_R)
            add_box(bm, uv, steel, (foot.x, foot.y, foot.z - FOOT[2] / 2), FOOT)
        else:
            foot = Vector((s * 7.0, yc - LEG_LEN, hinge_z - 9.0))
            add_rod(bm, uv, steel, top, foot, LEG_R)
            add_box(bm, uv, steel, (foot.x, foot.y + FOOT[0] / 2 - 4.0, foot.z - LEG_R - FOOT[2] / 2),
                    (FOOT[1] * 0.6, FOOT[0], FOOT[2]))                  # the foot folded flat under the leg's end
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    o.scale = (0.01, 0.01, 0.01)
    bpy.context.scene.collection.objects.link(o)
    return o


def magazine40(o):
    """GoM's 30 bent on along its own arc. GoM bent the body in four straight segments round one centre ahead of
    it: its rear edge (the outline's hull from below the header to the lowest point) lies on a circle within 0.2 mm.
    Every vertex past MAG_SPLIT degrees below the header is turned on about that centre by MAG_FACTOR."""
    import numpy as np
    me = o.data
    pts = sorted({(round(v.co.y, 6), round(-v.co.z, 6)) for v in me.vertices})

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    hull = []
    for p in pts:                                       # lower hull (y rising): the rear edge, then the base
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    low = min(pts, key=lambda p: p[1])
    rear = [p for p in hull if p[1] < -0.02 and p[0] <= low[0] + 1e-6]
    A = np.array([[y, z, 1.0] for y, z in rear])
    D, E, F = np.linalg.lstsq(A, -np.array([y * y + z * z for y, z in rear]), rcond=None)[0]
    cy, cz = -D / 2.0, -E / 2.0
    radius = math.sqrt(cy * cy + cz * cz - F)
    print("magazine arc: centre", round(cy, 4), round(cz, 4), "r", round(radius, 4),
          "worst", round(max(abs(math.hypot(y - cy, z - cz) - radius) for y, z in rear), 5))
    a_split = math.radians(MAG_SPLIT)
    for v in me.vertices:
        y, z = v.co.y, -v.co.z
        a = math.atan2(z - cz, y - cy)
        if a <= a_split or a > 0.0:                     # the header (and anything behind the centre) stays
            continue
        r = math.hypot(y - cy, z - cz)
        a2 = a_split + (a - a_split) * MAG_FACTOR
        v.co.y, v.co.z = cy + r * math.cos(a2), -(cz + r * math.sin(a2))
    me.update()


def drum75(header):
    """The 75-round drum on the 256 px texture DRUM_TEXTURE: GoM's 30's header (its UVs moved into the top-left
    quarter, which holds GoM's 30's texture), the feed tower (bottom right, plain steel), the disc's faces planar-mapped
    on the top-right quarter (rings, hub, welds painted there by drum_texture()), its rim and steps round the bottom
    left. Built in GoM's units (real mm x R), scaled like everything else by the caller."""
    me = header.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.active
    cut = DRUM_HEADER_Z * R
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if any(-v.co.z < cut for v in f.verts)], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    for f in bm.faces:
        for loop in f.loops:
            u, v = loop[uv].uv
            loop[uv].uv = (u * 0.5, 0.5 + v * 0.5)
    pt = lambda x, y, z: bm.verts.new((x * R, y * R, -z * R))          # real mm, game axes -> raw
    gom_faces = set(bm.faces)

    def quad_uv(f, u0, v0, u1, v1):
        for j, loop in enumerate(f.loops):
            loop[uv].uv = (u0 if j in (0, 3) else u1, v0 if j in (0, 1) else v1)

    # the feed tower: a box from under the header's sleeve into the disc
    yr, yf, hw, zt, zb = DRUM_TOWER
    c = [pt(sx * hw, y, z) for sx in (-1, 1) for y in (yr, yf) for z in (zb, zt)]
    for idx in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        quad_uv(bm.faces.new([c[i] for i in idx]), 0.55, 0.05, 0.95, 0.45)
    # the drum: DRUM_PROFILE revolved about its own axis, which leans DRUM_TILT degrees from the barrel's line
    cy, cz = DRUM_CENTRE
    t = math.radians(DRUM_TILT)
    axis, up = (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))      # (y, z) of the axis and of "up" in its plane

    def local(r, phi, a):
        """game mm of a point at radius r, angle phi (0 = the gun's left, +x; pi / 2 = up) and a along the axis"""
        side, upc = r * math.cos(phi), r * math.sin(phi)
        return (side, cy + a * axis[0] + upc * up[0], cz + a * axis[1] + upc * up[1])

    rings = []
    for r, a in DRUM_PROFILE:
        if r == 0.0:
            rings.append([pt(*local(0.0, 0.0, a))])
        else:
            rings.append([pt(*local(r, 2 * math.pi * j / DRUM_SEGMENTS, a)) for j in range(DRUM_SEGMENTS)])
    r_max = max(r for r, _ in DRUM_PROFILE)

    def face_uv(f, corners, cyl):
        """corners: (radius, a, segment index j) per loop. Faces (constant a) planar on the top-right quarter; band
        and step walls (constant r) round the bottom-left quarter, the angle across (a quad's second segment index
        never wraps to 0: the seam takes j = DRUM_SEGMENTS), a up it"""
        for loop, (r, a, j) in zip(f.loops, corners):
            if cyl:
                loop[uv].uv = (0.02 + 0.46 * j / DRUM_SEGMENTS, 0.25 + 0.23 * a / 43.0)
            else:
                phi = 2 * math.pi * j / DRUM_SEGMENTS
                loop[uv].uv = (0.75 + 0.245 * r * math.cos(phi) / r_max, 0.75 + 0.245 * r * math.sin(phi) / r_max)

    for i in range(len(DRUM_PROFILE) - 1):
        (r0, a0), (r1, a1) = DRUM_PROFILE[i], DRUM_PROFILE[i + 1]
        ra, rb = rings[i], rings[i + 1]
        cyl = r0 == r1
        for j in range(DRUM_SEGMENTS):
            k = (j + 1) % DRUM_SEGMENTS
            if len(ra) == 1:
                verts, corners = (ra[0], rb[j], rb[k]), ((r0, a0, j + 0.5), (r1, a1, j), (r1, a1, j + 1))
            elif len(rb) == 1:
                verts, corners = (ra[j], rb[0], ra[k]), ((r0, a0, j), (r1, a1, j + 0.5), (r0, a0, j + 1))
            else:
                verts = (ra[j], rb[j], rb[k], ra[k])
                corners = ((r0, a0, j), (r1, a1, j), (r1, a1, j + 1), (r0, a0, j + 1))
            face_uv(bm.faces.new(verts), corners, cyl)
    # the loading lever on the front face: a flat bar from the hub out towards the top rear, 6 mm wide, 3 mm proud
    a_front = DRUM_PROFILE[2][1]
    phi = math.radians(115.0)
    lever = []
    for a in (a_front, a_front + 3.0):
        for r, off in ((6.0, -3.0), (58.0, -3.0), (58.0, 3.0), (6.0, 3.0)):
            x, y, z = local(r, phi, a)
            # the bar's width: sideways in the face's plane, perpendicular to its radius
            dx = -off * math.sin(phi)
            dup = off * math.cos(phi)
            lever.append(pt(x + dx, y + dup * up[0], z + dup * up[1]))
    for idx in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        quad_uv(bm.faces.new([lever[i] for i in idx]), 0.6, 0.1, 0.9, 0.2)
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in gom_faces])   # ours only
    bm.to_mesh(me)
    bm.free()
    me.update()


DRUM_TEXTURE = os.path.join(MEDIA, "textures/weapons/GunsOfTien/762x39Drum75_RPK.png")


def drum_texture():
    """256 px, RGB: GoM's 30's texture top left; the drum's faces top right (dark blued steel, a ring line at each
    radius of DRUM_PROFILE, spot welds, the hub's winding boss and slot); the band and step walls bottom left (a
    darker line at each step's edge along the axis); plain steel bottom right (tower, lever)."""
    import numpy as np
    src = bpy.data.images.load(f"{GOM}/textures/weapons/magazines/assault_rifles/762x39Magazine30.png")
    w, h = src.size
    gom = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
    if (w, h) != (128, 128):                           # GoM's are 128; nearest resample otherwise
        ys = (np.arange(128) * h // 128)
        xs = (np.arange(128) * w // 128)
        gom = gom[ys][:, xs]
    steel = np.median(gom[..., :3].reshape(-1, 3), axis=0)
    rng = np.random.default_rng(75)
    tex = np.ones((256, 256, 4), dtype=np.float32)      # rows bottom-up (Blender's pixel order)
    tex[..., :3] = steel * 0.95
    tex[..., :3] *= (1.0 + rng.normal(0.0, 0.035, (256, 256, 1))).astype(np.float32)
    tex[128:, :128] = gom                               # top left: v 0.5..1, u 0..0.5
    # top right: the face, u = 0.75 + 0.245 du, v = 0.75 + 0.245 dv
    yy, xx = np.mgrid[0:128, 0:128]
    du = ((xx + 0.5) / 256.0 + 0.5 - 0.75) / 0.245
    dv = ((yy + 0.5) / 256.0 + 0.5 - 0.75) / 0.245
    r_max = max(p[0] for p in DRUM_PROFILE)
    rr = np.hypot(du, dv) * r_max
    face = np.ones((128, 128, 3), dtype=np.float32) * steel * (0.9 + 0.12 * (1 - np.clip(rr / r_max, 0, 1)))[..., None]
    for r in sorted({p[0] for p in DRUM_PROFILE if 0 < p[0] < r_max}):
        face[np.abs(rr - r) < 1.1] *= 0.55
        face[np.abs(rr - r - 1.6) < 0.6] *= 1.35        # the step's lit edge
    ang = np.arctan2(dv, du)
    for a in np.radians(np.arange(0, 360, 30)):          # spot welds on the plate
        d = np.hypot(rr * np.cos(ang) - 52.0 * math.cos(a), rr * np.sin(ang) - 52.0 * math.sin(a))
        face[d < 1.8] *= 0.7
    face[rr < 15.0] *= 1.25                             # the winding boss
    face[(np.abs(rr * np.sin(ang)) < 1.5) & (rr < 12.0)] *= 0.45
    tex[128:, 128:, :3] = face
    # bottom left: the band and step walls, the axis up v (v = 0.25 + 0.23 a / 43)
    amm = ((np.arange(128) + 0.5) / 256.0 - 0.25) / 0.23 * 43.0
    band = np.ones(128, dtype=np.float32)
    for a in sorted({p[1] for p in DRUM_PROFILE}):
        band[np.abs(amm - a) < 1.2] = 0.5
    for a in np.arange(-30.0, 8.0, 9.5):                  # the band's pressed ribs
        band[np.abs(amm - a) < 0.8] = 0.7
    tex[:128, :128, :3] = steel[None, None, :] * band[:, None, None] * 1.05
    tex[:128, :128, :3] *= (1.0 + rng.normal(0.0, 0.03, (128, 128, 1))).astype(np.float32)
    tex[..., :3] = np.clip(tex[..., :3], 0.0, 1.0)
    tex[..., 3] = 1.0
    img = bpy.data.images.new("762x39Drum75_RPK", 256, 256, alpha=False)
    img.pixels = tex.ravel().tolist()
    sc = bpy.context.scene
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    os.makedirs(os.path.dirname(DRUM_TEXTURE), exist_ok=True)
    img.save_render(DRUM_TEXTURE)
    print("wrote", DRUM_TEXTURE)


def gom_points(gun):
    import re
    text = open(f"{GOM}/scripts/MarzWeapons/models/weapons/assault_rifles.txt", encoding="utf-8").read()
    m = re.search(r"\bmodel\s+%s\s*\{(.*?)\n    \}" % gun, text, re.S)
    out = {}
    for a in re.finditer(r"attachment\s+(\w+)\s*\{(.*?)\}", m.group(1), re.S):
        off = [float(x) for x in re.search(r"offset\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        rot = [float(x) for x in re.search(r"rotate\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        out[a.group(1)] = {"offset": off, "rotate": rot}
    return out


def main():
    if GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out_guns, data = [], {"_extras": {"scale": SCALE, "stretch_mm": STRETCH, "gom_mm_unit": R}}
    for gun, spec in GUNS.items():
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/firearms/{spec['gom']}.fbx")
        objs = {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}
        body, bolt = objs[spec["gom"] + "_BODY"], objs[spec["gom"] + "_BOLT"]
        bm = bmesh.new()
        bm.from_mesh(body.data)
        bm.verts.ensure_lookup_table()
        bore, barrel_r = bore_z(bm)
        stock(bm, bore)
        move_trigger(bm, TRIGGER_MOVE[gun])
        lengthen(bm, spec, gun)
        muzzle_y = max(gy(v) for v in bm.verts if abs(gz(v) - bore) < barrel_r + 1.0)
        bm.to_mesh(body.data)
        bm.free()
        body.name = body.data.name = gun + "_BODY"
        bolt.name = bolt.data.name = gun + "_BOLT"
        parts = [body, bolt,
                 bipod(gun + "_BIPOD_FOLDED", spec, bore, barrel_r, muzzle_y, False),
                 bipod(gun + "_BIPOD_DEPLOYED", spec, bore, barrel_r, muzzle_y, True)]
        for o in parts:
            o.data.transform(Matrix.Scale(SCALE, 4))
        out_guns += parts
        pts = gom_points(spec["gom"])
        pts["muzzle"]["offset"][1] = muzzle_y * R          # the barrel's end (MuzzlePoints.lua's way for GoM's AK-47)
        pts["canon"]["offset"][1] += STRETCH * R           # the front sight block's face, ahead of any squeeze
        for p in pts.values():
            p["offset"] = [round(x * SCALE, 4) + 0.0 for x in p["offset"]]
        data[gun] = pts
        data["_extras"][gun] = {"bore_mm": round(bore, 2), "barrel_r_mm": round(barrel_r, 2),
                                "muzzle_mm": round(muzzle_y, 1), "length_mm_real": None}
    # the 40
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/magazines/assault_rifles.fbx")
    mag = None
    for o in set(bpy.data.objects) - before:
        if o.name.split(".")[0] == "762x39Magazine30" and mag is None:
            mag = o
        elif o not in out_guns:
            bpy.data.objects.remove(o)
    drum = mag.copy()
    drum.data = mag.data.copy()
    bpy.context.scene.collection.objects.link(drum)
    magazine40(mag)
    drum75(drum)
    drum_texture()
    for o, name in ((mag, "762x39Magazine40_RPK"), (drum, "762x39Drum75_RPK")):
        o.data.transform(Matrix.Scale(SCALE, 4))
        o.name = o.data.name = name
    for objs, out in ((out_guns, OUT_GUNS), ([mag, drum], OUT_MAGS)):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'})
        print("wrote", out, sorted(o.name for o in objs))
    with open(POINTS, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS)


main()
