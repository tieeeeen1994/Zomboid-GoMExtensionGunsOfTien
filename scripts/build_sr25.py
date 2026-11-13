"""Knight's SR-25 Match (1990) from Guns of Marz's own AR15 (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_sr25.py

User, 2026-11-11 (docs/design.md 4l): Stoner's 7.62x51mm AR-10 revival for Knight's Armament, as first sold, the Match
rifle (1118 mm, 4.88 kg, Wikipedia "SR-25"), main mod, built on GoM's AR15 (its flat-top AR with a fixed stock) so it
looks like GoM's ARs, the RPK's way on GoM's AK-47. Fitted to the user's two photos of a 1990 rifle (2026-11-11: an
auction listing's right and left sides, Knight's Mfg. Co. Vero Beach markings, a 20-round steel magazine; they were
pasted into the chat and are not on disk, so the landmarks below were read off them by eye on the right-side photo,
1118 mm over 1952 px = 1.746 px/mm, mm forward of the grip's rear top):
- GoM's AR15 is mapped piecewise along the bore onto them (KNOTS: the stock's butt 321 mm behind the grip, the
  magazine's centre 137.5 ahead, the upper receiver's front 194 ahead), 1.05 in height and 1.06 across (the AR-10 is a
  little bigger every way);
- everything of GoM's ahead of the receiver (barrel, gas tube, tapered handguard, delta ring, front sight block, flash
  hider) is dropped, and the photo's parts are drawn in its place: a ribbed barrel nut ring (60 mm across, 27 long),
  a straight round free-float tube (60 mm across, its axis 5 mm under the bore, to 518 mm), a small gas block at its
  front (to 541 mm), a slim match barrel standing 256 mm out with a plain crowned muzzle (no front sight, no flash
  hider), a sling stud under the tube at 461 mm; painted from GoM's own texture (the barrel's steel, the handguard's
  black);
- the bolt and charging handle are GoM's AR15_BOLT / AR15_CHARGING_HANDLE mapped the same way;
- KAC's steel 20-round magazine (modelled on the M16's): GoM's STANAG 20 grown to the photo's (66 mm front to back,
  25 across, 152 from the feed lips to the base), on GoM's STANAG texture.
GoM's AR15 is drawn at 0.603 of real size (the M16A2's proportion), the size every Guns of Tien gun has, so nothing is
rescaled for the game. GoM's own flat-top rail stays on the upper for its optics (the photos show a scope base
screwed onto the flat top there).

Writes:
    media/models_X/weapons/firearms/GunsOfTien_SR25.fbx           SR25_BODY, SR25_BOLT, SR25_CHARGING_HANDLE
    media/models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx  762x51Magazine20_SR25
    scripts/sr25_points.json                                       GoM's AR15 points grown the same way, the muzzle
                                                                   moved to the new barrel's end, the bipod under the
                                                                   handguard's stud
The gun keeps GoM's texture (weapons/firearms/assault_rifles/AR15), the magazine GoM's STANAG 20's.
"""

import json
import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
OUT_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SR25.fbx")
OUT_MAG = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTien_SR25_magazine.fbx")
POINTS = os.path.join(HERE, "sr25_points.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

R = 0.000603                    # GoM's ARs: game units per real mm (the M16A2's proportion, ours too)
# The landmarks above were read from the grip's rear top, where the grip meets the receiver at its back. GoM's origin
# (the hand) is not there: GoM's grip meets the receiver GRIP_TOP mm ahead of it. Until 2026-11-14 the landmarks were
# pinned to the origin, which squeezed GoM 0..168 (grip, trigger, guard) to 0.82 of its size: a guard opening 45 mm long
# against the photo's 51, the grip 20 % thin, the magazine and everything ahead about 35 mm too close to the hand (the
# trigger audit, TODO.md; measured on IMFDB's 4798 px right side of a Mk 11 Mod 0, KAC's lower with the A2 grip and
# stock: GoM's grip edges and trigger guard pins land on the photo's at one scale, 1.03 of GoM's along the bore, and
# its lower front and upper receiver front at the photo landmarks + 35 within 6 mm). So every photo landmark is
# GRIP_TOP further forward of the origin; the overall length stays 1118.
GRIP_TOP = 35.0
KNOTS = ((-273.5, -321.0 + GRIP_TOP), (0.0, 0.0), (168.0, 137.5 + GRIP_TOP),
         (218.5, 194.0 + GRIP_TOP))     # GoM AR15 mm -> SR-25 mm along the bore
GROW_Z, GROW_X = 1.05, 1.06
CUT = 212.0                     # GoM's pieces starting this far ahead of the grip (mm) are the barrel group: dropped
RING = (194.0 + GRIP_TOP, 221.0 + GRIP_TOP, 30.0)   # the barrel nut's ribbed ring: L from, to, radius
TUBE = (221.0 + GRIP_TOP, 499.0 + GRIP_TOP, 30.0, -5.0)   # the free-float tube: L from, to, radius, its axis against
                                    # the bore (the listing's 12" composite handguard, ring included; the photo read 518)
GAS = (499.0 + GRIP_TOP, 522.0 + GRIP_TOP)   # the low profile gas block ahead of it
MUZZLE = 797.0 + GRIP_TOP       # 1118 mm overall with the butt at -321 + GRIP_TOP
BARREL_R = (8.6, 7.4)           # the barrel out of the gas block, at the muzzle (the photo's 17 and 14 mm)
STUD = 450.0 + GRIP_TOP         # the sling stud under the tube (the bipod clamps on it)
# GoM's trigger blade sits 4.6 mm behind the Mk 11 photo's once mapped: its middle at mid-height of the guard opening
# (z -31 .. -22 after growing) goes to the photo's (455.5 px at row 200 of the crop: GoM 94.5, here 97.0; rows 170 and
# 230 put it 1.5 mm further forward, and the photo's blade is thicker: 98.5)
TRIGGER_Y = 98.5
# The integrated scope: Leupold's Vari-X III 3.5-10x40 (the listing: "w/ high target knobs", on a B-Square base and
# rings): 1" tube, 40 mm objective, about 315 mm long, its eyepiece just over the grip (the photo), its axis 77 mm over
# the bore (the photo's tall rings). Profile (mm forward of the grip, radius) from the eyepiece to the objective.
SCOPE_Z = 77.0
SCOPE = [(y + GRIP_TOP, r) for y, r in
         [(-6.0, 1.0), (-6.0, 19.0), (-4.0, 20.0), (58.0, 20.0), (72.0, 15.0), (100.0, 15.0), (104.0, 12.7),
          (214.0, 12.7), (246.0, 23.5), (304.0, 23.5), (309.0, 22.0), (309.0, 1.0)]]
SCOPE_RINGS = (88.0 + GRIP_TOP, 182.0 + GRIP_TOP)   # the B-Square rings, 16 mm wide, on risers (22 x 16) from the base
BASE = (6.0 + GRIP_TOP, 196.0 + GRIP_TOP, 33.0, 11.0)   # the B-Square base on the flat top: L from, to, its top over
                                                        # the bore, half width
TURRET = 140.0 + GRIP_TOP       # the high target knobs: elevation on top, windage on the right
BIPOD_LEG = 200.0               # Harris 1A2-BR (6-9"): pivot to foot
MAG_DEPTH, MAG_WIDTH, MAG_LEN = 66.0, 25.0, 152.0     # KAC's 20: 2.6" front to back (user, 2026-11-11: 76 was "too large"), the photo's length


def ymap(y):
    for (a0, b0), (a1, b1) in zip(KNOTS, KNOTS[1:]):
        if y <= a1 or (a1, b1) == KNOTS[-1]:
            if y < KNOTS[0][0]:
                a1, b1 = KNOTS[1]
                a0, b0 = KNOTS[0]
            return b0 + (y - a0) * (b1 - b0) / (a1 - a0)
    return y


def grow(x, y, z):
    """GoM's AR15 (real mm, origin at the grip) to the SR-25's size."""
    return x * GROW_X, ymap(y), z * GROW_Z


def gy(v):
    return v.co.y / R


def gz(v):
    return -v.co.z / R


def islands(bm):
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


def uv_patch(bm, uv, comp):
    """The UV box of the island's largest face (in UV area), shrunk to its middle: a patch of that part's paint."""
    best, area = None, -1.0
    for f in {f for v in comp for f in v.link_faces}:
        us = [l[uv].uv for l in f.loops]
        a = (max(u.x for u in us) - min(u.x for u in us)) * (max(u.y for u in us) - min(u.y for u in us))
        if a > area:
            best, area = us, a
    u0, u1 = min(u.x for u in best), max(u.x for u in best)
    v0, v1 = min(u.y for u in best), max(u.y for u in best)
    du, dv = (u1 - u0) * 0.25, (v1 - v0) * 0.25
    return u0 + du, v0 + dv, u1 - du, v1 - dv


def paint(uv, patch, faces):
    """UVs inside a patch: each face spread over a small square of it (build_rpk.py's way)."""
    u0, v0, u1, v1 = patch
    for i, f in enumerate(faces):
        fu = u0 + (u1 - u0) * ((i * 0.37) % 0.8)
        fv = v0 + (v1 - v0) * ((i * 0.61) % 0.8)
        du, dv = (u1 - u0) * 0.2, (v1 - v0) * 0.2
        for j, loop in enumerate(f.loops):
            loop[uv].uv = (fu + du * (j in (1, 2)), fv + dv * (j in (2, 3)))


def lathe(bm, uv, patch, bore, profile, seg=24, axis_x=0.0):
    """Rings about an axis along y at height `bore` (game mm): profile [(y, r)] from the rear forward, capped."""
    rings = []
    for y, r in profile:
        rings.append([bm.verts.new(((axis_x + r * math.cos(2 * math.pi * i / seg)) * R, y * R,
                                    -(bore + r * math.sin(2 * math.pi * i / seg)) * R)) for i in range(seg)])
    _skin(bm, uv, patch, rings, seg)


def lathe_z(bm, uv, patch, base, profile, seg=20):
    """Rings about a vertical axis from `base` (x, y, z game mm) up: profile [(dz, r)]."""
    x0, y0, z0 = base
    rings = [[bm.verts.new(((x0 + r * math.cos(2 * math.pi * i / seg)) * R, (y0 + r * math.sin(2 * math.pi * i / seg)) * R,
                            -(z0 + dz) * R)) for i in range(seg)] for dz, r in profile]
    _skin(bm, uv, patch, rings, seg)


def lathe_x(bm, uv, patch, base, profile, seg=20):
    """Rings about an axis along x from `base`: profile [(dx, r)] (negative dx = the gun's right)."""
    x0, y0, z0 = base
    rings = [[bm.verts.new(((x0 + dx) * R, (y0 + r * math.cos(2 * math.pi * i / seg)) * R,
                            -(z0 + r * math.sin(2 * math.pi * i / seg)) * R)) for i in range(seg)] for dx, r in profile]
    _skin(bm, uv, patch, rings, seg)


def _skin(bm, uv, patch, rings, seg):
    faces = []
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i])) for i in range(seg)]
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    paint(uv, patch, faces)


def ring_ribbed(bm, uv, patch, cz, y0, y1, r, rib=1.2, seg=40):
    """A ring about an axis along y at height cz, with axial ribs (every other segment `rib` lower)."""
    rr = [r - (rib if i % 2 else 0.0) for i in range(seg)]
    rings = [[bm.verts.new((rr[i] * math.cos(2 * math.pi * i / seg) * R, y * R,
                            -(cz + rr[i] * math.sin(2 * math.pi * i / seg)) * R)) for i in range(seg)] for y in (y0, y1)]
    a, b = rings
    faces = [bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i])) for i in range(seg)]
    faces.append(bm.faces.new(list(reversed(a))))
    faces.append(bm.faces.new(b))
    paint(uv, patch, faces)


def box(bm, uv, patch, centre, size):
    hx, hy, hz = [s / 2.0 for s in size]
    vs = [bm.verts.new(((centre[0] + sx * hx) * R, (centre[1] + sy * hy) * R, -(centre[2] + sz * hz) * R))
          for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    paint(uv, patch, [bm.faces.new([vs[i] for i in f]) for f in faces])


def grow_mesh(bm):
    for v in bm.verts:
        x, y, z = grow(v.co.x / R, gy(v), gz(v))
        v.co = Vector((x * R, y * R, -z * R))


def align_trigger(bm, target_y):
    """Move GoM's trigger (the thin island hanging into the guard opening) along the bore so its blade's middle at
    mid-height of the opening is at target_y (mm, after growing); returns the move."""
    for c in islands(bm):
        ys = [gy(v) for v in c]
        if (len(c) >= 40 and max(abs(v.co.x) for v in c) / R < 4.5 and min(ys) > 50.0 and max(ys) < 135.0
                and min(gz(v) for v in c) < -30.0):
            band = [gy(v) for v in c if -31.0 <= gz(v) <= -22.0]
            dy = target_y - (min(band) + max(band)) / 2.0
            for v in c:
                v.co.y += dy * R
            print("trigger moved %.1f mm forward" % dy)
            return dy
    raise RuntimeError("GoM's trigger island not found")


def gom_points():
    text = open(f"{GOM}/scripts/MarzWeapons/models/weapons/assault_rifles.txt", encoding="utf-8").read()
    m = re.search(r"\bmodel\s+AR15\s*\{(.*?)\n    \}", text, re.S)
    out = {}
    for a in re.finditer(r"attachment\s+(\w+)\s*\{(.*?)\}", m.group(1), re.S):
        off = [float(x) for x in re.search(r"offset\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        rot = [float(x) for x in re.search(r"rotate\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        out[a.group(1)] = {"offset": off, "rotate": rot}
    return out


def build_gun():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/firearms/AR15.fbx")
    objs = {o.name.split(".")[0]: o for o in set(bpy.data.objects) - before if o.type == 'MESH'}
    body = objs["AR15_BODY"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv = bm.loops.layers.uv.active
    comps = islands(bm)
    ahead = [c for c in comps if min(gy(v) for v in c) >= CUT]
    barrel = max((c for c in ahead if max(v.co.x for v in c) / R < 12.0),
                 key=lambda c: max(gy(v) for v in c) - min(gy(v) for v in c))
    guard = max(ahead, key=lambda c: max(abs(v.co.x) for v in c))
    zs = [gz(v) for v in barrel]
    bore = (min(zs) + max(zs)) / 2.0
    steel, black = uv_patch(bm, uv, barrel), uv_patch(bm, uv, guard)
    recv_front = max(gy(v) for c in comps if c not in ahead for v in c)
    bmesh.ops.delete(bm, geom=[v for c in ahead for v in c], context='VERTS')
    grow_mesh(bm)
    align_trigger(bm, TRIGGER_Y)
    bore_g = bore * GROW_Z
    rear = min(gy(v) for v in bm.verts)
    # the magazine well: the piece round the magazine's place (GoM's lips at 168, mapped to 137.5) that ends low but
    # well above the grip's bottom; its bottom lip's span along the bore is where the magazine is centred (user,
    # 2026-11-11: "it's still badly positioned. center it")
    wells = [c for c in islands(bm) if min(gy(v) for v in c) < KNOTS[2][1] < max(gy(v) for v in c)
             and -70.0 < min(gz(v) for v in c) < -35.0]
    well = max(wells, key=lambda c: len(c))
    wz = min(gz(v) for v in well)
    lip = [gy(v) for v in well if gz(v) < wz + 15.0]     # the bottom edge rises 13 mm from its rear to its front
    well_mm = (min(lip), max(lip), wz)
    hz = bore_g + TUBE[3]
    old_faces = set(bm.faces)
    # the barrel from inside the ring to the crowned muzzle (its rear part hidden in the tube)
    lathe(bm, uv, steel, bore_g, [(RING[0] - 10.0, 10.0), (GAS[1], 10.0), (GAS[1], BARREL_R[0]),
                                  (MUZZLE - 1.5, BARREL_R[1]), (MUZZLE, BARREL_R[1] - 1.2), (MUZZLE, 3.5)], seg=20)
    # the barrel nut's ribbed ring, the free-float tube (rounded front lip), the gas block, the sling stud
    ring_ribbed(bm, uv, black, hz, RING[0], RING[1], RING[2])
    lathe(bm, uv, black, hz, [(TUBE[0] - 0.5, TUBE[2] - 2.0), (TUBE[0], TUBE[2]), (TUBE[1] - 3.0, TUBE[2]),
                              (TUBE[1], TUBE[2] - 3.0), (TUBE[1], 12.0)], seg=32)
    box(bm, uv, steel, (0.0, (GAS[0] + GAS[1]) / 2.0, bore_g + 0.5), (24.0, GAS[1] - GAS[0], 39.0))
    box(bm, uv, steel, (0.0, GAS[1] - 9.0, bore_g + 22.5), (8.0, 16.0, 6.0))
    stud = STUD
    box(bm, uv, steel, (0.0, stud, hz - TUBE[2] - 3.5), (6.0, 7.0, 8.0))
    front, muzzle = RING[0], MUZZLE
    # the integrated scope (part of the body, as the AUG's): the B-Square base, two rings on risers, the Leupold
    sz = bore_g + SCOPE_Z
    box(bm, uv, black, (0.0, (BASE[0] + BASE[1]) / 2.0, bore_g + BASE[2] - 5.0), (2 * BASE[3], BASE[1] - BASE[0], 10.0))
    for yr in SCOPE_RINGS:
        box(bm, uv, black, (0.0, yr, (bore_g + BASE[2] + sz - 12.0) / 2.0), (22.0, 16.0, sz - 12.0 - bore_g - BASE[2]))
        lathe(bm, uv, black, sz, [(yr - 8.0, 17.0), (yr + 8.0, 17.0)], seg=20, axis_x=0.0)
    lathe(bm, uv, black, sz, SCOPE, seg=24)
    lathe_z(bm, uv, black, (0.0, TURRET, sz + 10.0), [(0.0, 8.0), (8.0, 8.0), (8.5, 12.5), (28.0, 12.5),
                                                      (30.0, 10.5)])                                 # elevation
    lathe_x(bm, uv, black, (-10.0, TURRET, sz), [(0.0, 8.0), (-8.0, 8.0), (-8.5, 12.5), (-26.0, 12.5),
                                                 (-28.0, 10.5)])                                     # windage, right
    box(bm, uv, black, (0.0, TURRET, sz), (26.0, 30.0, 26.0))
    lathe_x(bm, uv, black, (10.0, TURRET, sz), [(0.0, 7.5), (8.0, 7.5)])                           # parallax, left
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in old_faces])
    bm.to_mesh(body.data)
    bm.free()
    for name in ("AR15_BOLT", "AR15_CHARGING_HANDLE"):
        b2 = bmesh.new()
        b2.from_mesh(objs[name].data)
        grow_mesh(b2)
        b2.to_mesh(objs[name].data)
        b2.free()
    body.name = body.data.name = "SR25_BODY"
    objs["AR15_BOLT"].name = objs["AR15_BOLT"].data.name = "SR25_BOLT"
    objs["AR15_CHARGING_HANDLE"].name = objs["AR15_CHARGING_HANDLE"].data.name = "SR25_CHARGING_HANDLE"
    for o in set(bpy.data.objects) - before:
        if o.name not in ("SR25_BODY", "SR25_BOLT", "SR25_CHARGING_HANDLE"):
            bpy.data.objects.remove(o)
    info = {"bore_mm": round(bore_g, 2), "receiver_front_mm": round(front, 1), "muzzle_mm": round(muzzle, 1),
            "rear_mm": round(rear, 1), "stud_mm": round(stud, 1),
            "hg_bottom_mm": round(bore_g + TUBE[3] - TUBE[2], 2), "gom_receiver_front_mm": round(recv_front, 1),
            "well_bottom_mm": [round(well_mm[0], 1), round(well_mm[1], 1), round(well_mm[2], 1)]}
    info["patches"] = {"steel": steel, "black": black}
    return [bpy.data.objects[n] for n in ("SR25_BODY", "SR25_BOLT", "SR25_CHARGING_HANDLE")], info


def rod(bm, uv, patch, a, b, r, seg=10):
    """A rod from a to b (game mm), radius r, capped."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    up = side.cross(d)
    rings = []
    for c in (a, b):
        ring = []
        for i in range(seg):
            q = c + r * (math.cos(2 * math.pi * i / seg) * side + math.sin(2 * math.pi * i / seg) * up)
            ring.append(bm.verts.new((q.x * R, q.y * R, -q.z * R)))
        rings.append(ring)
    _skin(bm, uv, patch, rings, seg)


def build_bipod(info, deployed):
    """The integrated bipod, a Harris 1A2-BR on the sling stud (gun space, drawn at the origin as the AUG HBAR's):
    the body clamped on the stud, two legs (outer tube, inner leg, rubber foot) pivoting at its sides; folded they lie
    forward under the barrel, deployed they stand down, splayed a little, the feet a touch forward."""
    name = "SR25_BIPOD_DEPLOYED" if deployed else "SR25_BIPOD_FOLDED"
    steel, black = info["patches"]["steel"], info["patches"]["black"]
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    y0 = info["stud_mm"]
    zb = info["hg_bottom_mm"]
    box(bm, uv, black, (0.0, y0, zb - 12.0), (40.0, 26.0, 16.0))               # the body under the stud
    box(bm, uv, steel, (0.0, y0, zb - 3.0), (10.0, 14.0, 6.0))                 # its clamp on the stud
    for sgn in (-1, 1):
        pivot = Vector((sgn * 23.0, y0, zb - 14.0))
        rod(bm, uv, steel, pivot - Vector((sgn * 4.0, 0, 0)), pivot + Vector((sgn * 3.0, 0, 0)), 5.5)   # the pivot boss
        if deployed:
            d = Vector((sgn * 0.17, 0.08, -1.0)).normalized()
        else:
            d = Vector((sgn * 0.01, 1.0, 0.02)).normalized()
        knee = pivot + d * BIPOD_LEG * 0.6
        foot = pivot + d * BIPOD_LEG
        rod(bm, uv, black, pivot, knee, 5.0)
        rod(bm, uv, steel, knee - d * 8.0, foot, 3.8)
        rod(bm, uv, black, foot - d * 4.0, foot + d * 10.0, 6.5)                 # the rubber foot
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    o.scale = (0.01, 0.01, 0.01)
    bpy.context.scene.collection.objects.link(o)
    return o


def build_magazine():
    """GoM's STANAG 20 grown to the SR-25 pattern: depth and width to KAC's, length (feed lips, the origin, to the
    base) to 158 mm; the lips and top round stay at the origin."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/magazines/assault_rifles.fbx")
    mag = None
    for o in set(bpy.data.objects) - before:
        if o.name.split(".")[0] == "556x45Magazine20_STANAG" and mag is None:
            mag = o
        else:
            bpy.data.objects.remove(o)
    vs = mag.data.vertices
    # raw mesh units: GoM's magazines are drawn at 0.65 of real; find the extents in that space
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    print("STANAG 20 raw bounds", [round(min(a), 4) for a in (xs, ys, zs)], [round(max(a), 4) for a in (xs, ys, zs)])
    w, d, ln = max(xs) - min(xs), max(ys) - min(ys), max(abs(min(zs)), abs(max(zs)))
    sx, sy, sz = MAG_WIDTH * R / w, MAG_DEPTH * R / d, MAG_LEN * R / ln
    mag.data.transform(Matrix.Diagonal((sx, sy, sz, 1.0)))
    mag.name = mag.data.name = "762x51Magazine20_SR25"
    ys2 = [v.co.y for v in mag.data.vertices]
    return mag, {"scale_xyz": [round(sx, 4), round(sy, 4), round(sz, 4)],
                 "centre_mm": round((min(ys2) + max(ys2)) / 2.0 / R, 2)}


def main():
    if GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    gun, info = build_gun()
    gun += [build_bipod(info, False), build_bipod(info, True)]
    info.pop("patches")
    mag, minfo = build_magazine()
    pts = {}
    for name, p in gom_points().items():
        x, y, z = grow(*(c / R for c in p["offset"]))
        pts[name] = {"offset": [round(x * R, 4) + 0.0, round(y * R, 4) + 0.0, round(z * R, 4) + 0.0],
                     "rotate": p["rotate"]}
    # GoM's points the SR-25 keeps: no muzzle device, bayonet or rails on the match rifle, and its scope and bipod
    # are its own (user, 2026-11-11: "sr-25 should have integrated scope, integrated bipod")
    for name in ("canon", "bayonet", "rail_down", "rail_left", "rail_right", "laser_right", "light_left",
                 "foregrip", "rail_up", "scope", "bipod"):
        pts.pop(name, None)
    pts["muzzle"]["offset"] = [0.0, round(info["muzzle_mm"] * R, 4), round(info["bore_mm"] * R, 4)]
    # the magazine centred in the well's bottom opening (its own middle there, along the bore); its height stays GoM's
    wa, wb, _ = info["well_bottom_mm"]
    pts["magazine"]["offset"][1] = round(((wa + wb) / 2.0 - minfo["centre_mm"]) * R, 4)
    pts["integrated_bipod"] = {"offset": [0.0, 0.0, 0.0], "rotate": [0.0, 0.0, 0.0]}
    pts["_extras"] = dict(info, magazine=minfo, k=R, knots=KNOTS, grow_zx=[GROW_Z, GROW_X])
    for objs, out in ((gun, OUT_GUN), ([mag], OUT_MAG)):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'})
        print("wrote", out, sorted(o.name for o in objs))
    with open(POINTS, "w") as fh:
        json.dump(pts, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS, json.dumps(pts["_extras"]))


if __name__ == "__main__":
    main()
