"""The SVU (OTs-03, 1991) from Guns of Marz's own SVD (Blender 5.2, headless).

    blender -b --factory-startup -P scripts/build_svu.py

User, 2026-11-20 (docs/sv98_sv99_svu_research.md, docs/design.md 4p): TsKIB SOO's bullpup SVD, the first,
semi-automatic model (series production 1991), main mod, built on GoM's SVD so it looks like GoM's and takes GoM's
10-round magazine. What makes an SVD an SVU, read off the references (references/svu; the measuring photo is Vitaly
Kuzmin's right side of an SVU-A, svu_a/kuzmin2015_svua_01.jpg, outwardly the same gun, 2.026 px a mm at its 900 mm,
read on mm grids; the left side kuzmin2015_svua_18.jpg for the scope rail; IMFDB's studio SVU-A for the raised
sights):
- GoM's receiver, cover, bolt, magazine catch and safety, handguards, gas tube and gas block stay where they are;
  GoM's thumbhole stock and its SVD rear sight go.
- the barrel is 100 mm shorter: between the gas block and the front sight block GoM's barrel is squeezed so the front
  sight lands where the photo has it (BARREL_*), and Bondarev's three-chamber muzzle brake (CAN, a lathe profile, its
  front cap ported) covers what is left of GoM's flash hider;
- the butt: a boot-shaped shoulder piece under and behind the receiver (BUTT, the photo's outline);
- the pistol grip ahead of the magazine (GRIP); the trigger guard and the hook-shaped trigger traced off the photo
  (GUARD_OUT / GUARD_IN, TRIGGER; user, 2026-11-20: GoM's SVD guard, shortened, was "wrong", its top must be attached
  all along): the guard leaves the grip's front low down, runs forward and curves up into the trigger housing's strip
  (HOUSING) under the handguard's rear, so the housing is the opening's whole top and the blade hangs from it;
- the cheek rest on the receiver cover (CHEEK);
- the SVD's scope rail (on the receiver's left) moved forward onto the handguard's rear (RAIL_MOVE), where the SVU's
  is, with GoM's `rail_up` and `scope` points, so GoM's AK mount and optics sit as on the photo's PSO-1;
- folding sights: the front sight block on a tall folding post (GoM's sight, lifted FRONT_LIFT, on two plates) and a
  folding aperture rear sight on the cover's front. Two bodies: SVU_BODY with both raised (no optic) and
  SVU_FD_BODY with both folded back (any optic, shared/GunsOfTien/SVU.lua's ConditionalModel rule), as Post-93's
  iron sights.
Heights: GoM drew its SVD about 1.25 times as deep as the photo reads above the receiver's bottom (handguard 62 mm
against 48, receiver 67 against 55: the photo is taken from above at an angle), and its magazine short, so photo
rows above the receiver's bottom are scaled by Z_UP and below it by Z_DOWN (the butt's toe level with GoM's
magazine's bottom, as on the photo).
Lengthwise the photo is registered on GoM's receiver (both ends; GoM's magazine then sits 15 mm further forward in
it than the photo's). The whole gun then moves back so the trigger sits where GoM's SVD has it: the vanilla rifle
clips hold the gun at its origin, and a bullpup's grip is near its middle.
Everything is scaled by SCALE = 0.603 / GoM's 0.6625 (GoM draws the SVD 811.6 for 1225 mm), the M16A2 proportion
every Guns of Tien gun is drawn at; GoM's magazine is drawn on it through a `_GoT` model of the same scale.

Texture: SVU.png, 512 px: GoM's SVD.png (256) in the top-left quarter (every GoM UV moved there), a camouflage
patch in the bottom-left quarter painted in GoM's stock colours (brown with black blotches, the 1991 SVU's
"camouflage paint" on butt, grip and cheek rest) and GoM's barrel steel for the new metal (UVs in GoM's quarter).

Writes:
    media/models_X/weapons/firearms/GunsOfTien_SVU.fbx    SVU_BODY, SVU_FD_BODY, SVU_BOLT
    media/textures/weapons/GunsOfTien/SVU.png
    scripts/svu_points.json                               the model's points (GoM's SVD's, moved, x SCALE)
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
OUT_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTien_SVU.fbx")
OUT_TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTien/SVU.png")
POINTS = os.path.join(HERE, "svu_points.json")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                           "3722134990/mods/GunsOfMarz/42.16/media"),
                        "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                        "42.16/media") if os.path.isdir(p)), None)

R = 0.0006625                   # GoM's SVD: game units per real mm (811.6 units x 0.001 for 1225 mm)
SCALE = round(0.603 / 0.6625, 4)
PHOTO_TO_GOM = -4.5             # photo mm from the butt -> GoM's SVD mm (registered on the receiver's two ends)
Z_UP, Z_DOWN = 1.25, 0.9        # photo rows (mm) above / below the receiver's bottom -> GoM's depth
ROW_RX = 100.0                  # the receiver's bottom on the photo's grid rows (mm from the crop's top, 560 px)
TRIGGER_PHOTO = 424.9           # the traced blade's middle (its box's, as GoM's island's) on the photo (mm from the butt)
GOM_TRIGGER = 0.07385           # GoM's SVD trigger island's middle (y): the SVU's trigger goes there
GOM_GUARD = (0.0561, 0.1091)    # GoM's SVD guard island (deleted)
GOM_TRIG = (0.0688, 0.0789)     # GoM's SVD trigger island (deleted)
# The guard and trigger, traced off the photo at 4.05 px a mm (svu_a/kuzmin2015_svua_01.jpg, x 650-1020, y 720-980
# doubled): (mm from the butt, grid row). The guard band's outer and inner edges from where it leaves the grip's front
# (inside the grip) round its bottom and up its front into the housing; the blade from inside the housing down, its
# back bulging rearward, its tip hooked forward.
GUARD_OUT = [(394.0, 116.0), (399.3, 118.0), (406.2, 125.9), (411.2, 129.6), (438.3, 130.1), (448.2, 127.1),
             (453.8, 119.7), (456.8, 108.6), (456.1, 100.0), (453.1, 93.8), (450.1, 87.0)]
GUARD_IN = [(394.0, 119.2), (401.8, 120.4), (408.2, 124.9), (411.9, 127.6), (437.8, 127.8), (446.7, 125.1),
            (451.6, 118.5), (454.3, 108.6), (453.6, 100.7), (450.9, 95.0), (447.7, 87.0)]
TRIGGER = [(425.2, 86.5), (423.7, 98.7), (423.5, 104.9), (425.0, 112.3), (427.9, 118.0), (430.7, 120.9),
           (429.9, 122.4), (426.7, 120.4), (423.0, 116.0), (420.3, 109.8), (419.1, 102.4), (419.0, 86.5)]
GUARD_HW, TRIGGER_HW = 4.0 * 0.0006625, 2.4 * 0.0006625
HOUSING_ROW = 90.8              # the housing's bottom (the opening's top) on the photo
RAIL_MOVE = 0.087               # the scope rail onto the receiver's front and the handguard's rear: GoM's PSO-1 then
                                # sits where the photo's does (eyepiece over the magazine; the photo's bracket is
                                # 110 mm further forward, but GoM's scope reaches further ahead of its mount)
# the barrel: squeezed between GoM's gas block's front and its front sight block's rear, which lands on the photo's
# front sight (its base's middle at 750 mm)
BARREL_FROM, BARREL_SIGHT = 0.468, 0.5847
FRONT_SIGHT_PHOTO = 750.0
GOM_SIGHT_MID = (0.5847 + 0.6113) / 2.0
FRONT_LIFT = 0.0325             # the hood's top from GoM's 57 mm over the bore line to the photo's 96 (x Z_UP)
BORE_Z = 0.0262                 # GoM's barrel axis

# The butt, the photo's outline: (mm from the butt, grid row). From the receiver's bottom behind the magazine back to
# the receiver's rear end, up behind it, down the slanted rear face to the toe, and up the front edge.
BUTT = [(95, 99), (28, 99), (28, 66), (19, 67), (12, 78), (8, 110), (4, 145), (1, 170), (2, 183), (7, 191),
        (17, 194), (30, 193), (40, 188), (47, 170), (54, 148), (62, 124), (72, 106), (85, 99)]
BUTT_HW = 0.0113                # half width (GoM's receiver 0.0095)
# The grip (rows on the same grid): top under the handguard, the front over the guard's rear, raked back
GRIP = [(340, 90), (400, 90), (399, 118), (390, 130), (380, 145), (372, 162), (366, 180), (364, 187), (340, 183),
        (320, 178), (321, 165), (326, 150), (332, 130), (338, 112), (344, 98)]
GRIP_HW = 0.0105
CHEEK = (75.0, 215.0)           # the cheek rest along the cover (mm from the butt)
CHEEK_Z, CHEEK_T, CHEEK_HW = 0.0442, 0.0042, 0.0112
HOUSING = (330.0, 450.0, 0.0085, 0.0085)            # the trigger housing's strip: from, to (photo mm), top z, hw
# The strip's top over the handguard's rear (user, 2026-11-20, a crop of the preview: a flat plate standing off the
# handguard, "that gap in the top of the trigger guard"): GoM's handguard underside rises from 0.0088 to 0.0122 there
# while the strip stayed flat at 0.0085 and ran 5 mm past the guard's top. Measured on the export by rays up from the
# strip (final game y, the handguard's underside + 0.4 mm), and the strip now ends where the guard runs into it.
HOUSING_TOP = [(0.043, 0.0090), (0.044, 0.0092), (0.050, 0.0100), (0.056, 0.0108), (0.062, 0.0115), (0.068, 0.0119),
               (0.076, 0.0123), (0.086, 0.0125), (0.094, 0.0126)]
REAR_SIGHT = 321.0              # the rear sight's base (photo mm), on the cover's front
COVER_TOP = 0.0442
# Bondarev's muzzle brake: (photo mm, radius in GoM's mm), revolved about the bore
# (the photo's 40 mm across, its rear collar 45, the ported cap 28)
CAN = [(752, 9.0), (752, 22.5), (790, 22.5), (793, 20.0), (884, 20.0), (888, 17.5), (890, 14.0), (905, 14.0),
       (905, 9.0), (897, 7.0), (897, 0.0)]
CAN_SIDES = 24


def py(p):
    """Photo mm from the butt -> GoM's SVD game y"""
    return (p + PHOTO_TO_GOM) * R


def pz(row):
    """Photo grid row (mm from the crop's top) -> GoM's SVD game z (up)"""
    d = ROW_RX - row
    return (d * Z_UP if d > 0 else d * Z_DOWN) * R


SHIFT = GOM_TRIGGER - py(TRIGGER_PHOTO)


def pz_t(row):
    """The trigger group's rows -> game z, hung from GoM's handguard bottom (0.0062) at the photo's (row 88), below it
    at Z_DOWN: GoM's handguard sits lower than pz() puts the photo's, and the guard must meet the housing."""
    return 0.0062 - (row - 88.0) * Z_DOWN * R


def gy(v):
    return v.co.y


def gz(v):
    return -v.co.z


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


def box(c):
    xs, ys, zs = [v.co.x for v in c], [gy(v) for v in c], [gz(v) for v in c]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def pick(bm, test):
    """Vertices of every island whose box (x0, x1, y0, y1, z0, z1) passes test."""
    bm.verts.index_update()
    out = []
    for c in islands(bm):
        if test(*box(c)):
            out += c
    return out


def delete_verts(bm, verts):
    bmesh.ops.delete(bm, geom=list(set(verts)), context='VERTS')


# --------------------------------------------------------------------------------------------- texture and UVs
TEX = 512
CAMO_RECT = (0.0, 0.0, 0.5, 0.5)            # u0, v0, u1, v1 of the camouflage patch
STEEL_RECT = (0.52, 0.52, 0.98, 0.90)       # plain blued steel in GoM's barrel colour (top right)
DARK_RECT = (0.52, 0.93, 0.98, 0.98)        # the muzzle brake's bore and ports
UV_DENSITY = 1.35                           # camo UV units per game unit (GoM's stock: 2.7 on its 256 px texture)


def to_quarter(u, v):
    """GoM's UV -> the top-left quarter of SVU.png"""
    return u * 0.5, 0.5 + v * 0.5


def gom_uvs_to_quarter(bm):
    uv = bm.loops.layers.uv.active
    for f in bm.faces:
        for l in f.loops:
            l[uv].uv = to_quarter(*l[uv].uv)


def paint_steel(bm, faces, rect=STEEL_RECT):
    uv = bm.loops.layers.uv.active
    u0, v0, u1, v1 = rect
    for i, f in enumerate(faces):
        fu = u0 + (u1 - u0) * ((i * 0.37) % 0.8)
        fv = v0 + (v1 - v0) * ((i * 0.61) % 0.8)
        du, dv = (u1 - u0) * 0.2, (v1 - v0) * 0.2
        for j, loop in enumerate(f.loops):
            loop[uv].uv = (fu + du * (j in (1, 2)), fv + dv * (j in (2, 3)))


def paint_can(bm, faces, y0, y1, r_dark):
    """The brake: round the axis across the steel patch, along it up the patch (no seams of colour); its bore and
    ports (every face inside r_dark of the axis) dark."""
    uv = bm.loops.layers.uv.active
    for f in faces:
        dark = all(math.hypot(l.vert.co.x, gz(l.vert) - BORE_Z) <= r_dark + 1e-7 for l in f.loops)
        u0, v0, u1, v1 = DARK_RECT if dark else STEEL_RECT
        for l in f.loops:
            a = (math.atan2(gz(l.vert) - BORE_Z, l.vert.co.x) / (2 * math.pi)) % 1.0
            t = (gy(l.vert) - y0) / (y1 - y0)
            l[uv].uv = (u0 + (u1 - u0) * a, v0 + (v1 - v0) * t)


def paint_camo(bm, faces, origin):
    """Box mapping into the camouflage patch, each part from its own corner of it (origin: u, v offset)."""
    uv = bm.loops.layers.uv.active
    u0, v0, u1, v1 = CAMO_RECT
    for f in faces:
        n = f.normal
        for l in f.loops:
            x, y, z = l.vert.co.x, gy(l.vert), gz(l.vert)
            if abs(n.x) >= max(abs(n.y), abs(n.z)):
                a, b = y, z
            elif abs(n.z) >= abs(n.y):
                a, b = y, x
            else:
                a, b = x, z
            u = u0 + origin[0] + a * UV_DENSITY
            v = v0 + origin[1] + b * UV_DENSITY
            l[uv].uv = (min(max(u, u0 + 0.004), u1 - 0.004), min(max(v, v0 + 0.004), v1 - 0.004))


def svu_texture():
    """SVU.png: GoM's SVD.png top left, the camouflage patch bottom left (GoM's stock colours), the rest GoM's
    texture again (unused)."""
    import numpy as np
    src = bpy.data.images.load(f"{GOM}/textures/weapons/firearms/semi_rifles/SVD.png")
    w, h = src.size
    gom = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
    if (w, h) != (256, 256):
        sys.exit("GoM's SVD.png is not 256 px")
    tex = np.ones((TEX, TEX, 4), dtype=np.float32)       # rows bottom-up (Blender's order)
    tex[256:, :256] = gom
    tex[256:, 256:] = gom
    tex[:256, 256:] = gom
    # GoM's stock colours from its right-side chart (GoM UV u 0.10..0.28, v 0.36..0.54): brown and black
    patch = gom[int(0.36 * 256):int(0.54 * 256), int(0.10 * 256):int(0.28 * 256), :3].reshape(-1, 3)
    lum = patch.mean(1)
    dark = np.median(patch[lum < np.percentile(lum, 30)], axis=0)
    brown = np.median(patch[lum > np.percentile(lum, 55)], axis=0)
    rng = np.random.default_rng(1991)
    yy, xx = np.mgrid[0:256, 0:256].astype(np.float32)
    field = np.zeros((256, 256), dtype=np.float32)
    for _ in range(70):                                  # soft blotches, wrapped so seams do not show
        cx, cy = rng.uniform(0, 256, 2)
        sx, sy = rng.uniform(6, 20, 2)
        dx = np.minimum(np.abs(xx - cx), 256 - np.abs(xx - cx))
        dy = np.minimum(np.abs(yy - cy), 256 - np.abs(yy - cy))
        field += np.exp(-(dx / sx) ** 2 - (dy / sy) ** 2)
    field += rng.normal(0.0, 0.08, field.shape)
    blot = field > np.percentile(field, 62)
    camo = np.where(blot[..., None], dark, brown) * (1.0 + rng.normal(0.0, 0.05, (256, 256, 1)))
    tex[:256, :256, :3] = np.clip(camo, 0.0, 1.0)
    # top right: plain steel in GoM's barrel colour (its strip, GoM UV u 0..0.087, v 0.55..0.95), a dark band on top
    strip = gom[int(0.55 * 256):int(0.95 * 256), 0:22, :3].reshape(-1, 3)
    steel = np.median(strip, axis=0)
    tex[256:, 256:, :3] = np.clip(steel * (1.0 + rng.normal(0.0, 0.04, (256, 256, 1))), 0.0, 1.0)
    tex[int(0.92 * TEX):, 256:, :3] = steel * 0.35
    tex[..., 3] = 1.0
    img = bpy.data.images.new("SVU", TEX, TEX, alpha=False)
    img.pixels = tex.ravel().tolist()
    sc = bpy.context.scene
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    os.makedirs(os.path.dirname(OUT_TEX), exist_ok=True)
    img.save_render(OUT_TEX)
    print("wrote", OUT_TEX)


# --------------------------------------------------------------------------------------------- new geometry
def vert(bm, x, y, z):
    return bm.verts.new((x, y, -z))


def inset(poly, d):
    """Offset a closed polygon (y, z) inward by d (its winding found from the signed area)."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((-e0.y, e0.x)) * s, Vector((-e1.y, e1.x)) * s
        b = (n0 + n1)
        if b.length < 1e-9:
            b = n0
        b.normalize()
        k = d / max(b.dot(n0), 0.35)
        out.append(tuple(p1 + b * k))
    return out


def prism(bm, poly, hw, bevel):
    """A slab of the outline poly (game y, z), half width hw, its edges bevelled. Returns the new faces."""
    inner = inset(poly, bevel)
    loops = [[vert(bm, sx * hw_, y, z) for y, z in p] for sx, hw_, p in
             ((1, hw, inner), (1, hw - bevel, poly), (-1, hw - bevel, poly), (-1, hw, inner))]
    faces = []
    n = len(poly)
    for a, b in zip(loops, loops[1:]):
        for i in range(n):
            faces.append(bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i])))
    faces.append(bm.faces.new(loops[0]))
    faces.append(bm.faces.new(list(reversed(loops[-1]))))
    caps = [faces[-2], faces[-1]]
    res = bmesh.ops.triangulate(bm, faces=caps, quad_method='BEAUTY', ngon_method='BEAUTY')
    return [f for f in faces if f not in caps] + res["faces"]


def strip(bm, outer, inner, hw):
    """A band between two matching polylines (game y, z) across x -hw .. hw: an open loop such as a trigger guard."""
    o0, o1 = [vert(bm, -hw, y, z) for y, z in outer], [vert(bm, hw, y, z) for y, z in outer]
    i0, i1 = [vert(bm, -hw, y, z) for y, z in inner], [vert(bm, hw, y, z) for y, z in inner]
    faces = []
    for k in range(len(outer) - 1):
        faces += [bm.faces.new((o0[k], o0[k + 1], i0[k + 1], i0[k])), bm.faces.new((o1[k], i1[k], i1[k + 1], o1[k + 1])),
                  bm.faces.new((o0[k], o1[k], o1[k + 1], o0[k + 1])), bm.faces.new((i0[k], i0[k + 1], i1[k + 1], i1[k]))]
    e = len(outer) - 1
    faces += [bm.faces.new((o0[0], i0[0], i1[0], o1[0])), bm.faces.new((o1[e], i1[e], i0[e], o0[e]))]
    return faces


def cuboid(bm, x0, x1, y0, y1, z0, z1):
    c = [vert(bm, x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    idx = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))
    return [bm.faces.new([c[i] for i in f]) for f in idx]


def lathe(bm, profile, y_of, z_axis, sides):
    """profile: (y, radius) pairs (game units) revolved about the axis at height z_axis (x = 0)."""
    rings = []
    for y, r in profile:
        if r <= 0.0:
            rings.append([vert(bm, 0.0, y, z_axis)])
        else:
            rings.append([vert(bm, r * math.cos(2 * math.pi * i / sides), y,
                               z_axis + r * math.sin(2 * math.pi * i / sides)) for i in range(sides)])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            if len(a) == 1:
                faces.append(bm.faces.new((a[0], b[j], b[i])))
            elif len(b) == 1:
                faces.append(bm.faces.new((a[i], a[j], b[0])))
            else:
                faces.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    if len(rings[0]) > 1:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
    return faces


def ring(bm, cy, cz, r_out, r_in, thick, sides=12):
    """An aperture ring in the x-z plane (looking along the bore) at (0, cy, cz)."""
    pts = lambda r, y: [vert(bm, r * math.cos(2 * math.pi * i / sides), y,
                             cz + r * math.sin(2 * math.pi * i / sides)) for i in range(sides)]
    oa, ob = pts(r_out, cy - thick / 2), pts(r_out, cy + thick / 2)
    ia, ib = pts(r_in, cy - thick / 2), pts(r_in, cy + thick / 2)
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces += [bm.faces.new((oa[i], oa[j], ob[j], ob[i])), bm.faces.new((ia[j], ia[i], ib[i], ib[j])),
                  bm.faces.new((oa[j], oa[i], ia[i], ia[j])), bm.faces.new((ob[i], ob[j], ib[j], ib[i]))]
    return faces


def rear_sight(bm, raised):
    """The folding aperture sight on the cover's front: a hinge block, a leaf and its ring. Raised, the ring's middle
    at the front sight post's tip; folded, the leaf lies back along the cover."""
    y = py(REAR_SIGHT)
    base = cuboid(bm, -0.0070, 0.0070, y - 0.0055, y + 0.0055, COVER_TOP - 0.0005, COVER_TOP + 0.0035)
    z_ap = 0.052 + FRONT_LIFT
    hinge = Vector((0.0, y, COVER_TOP + 0.0035))
    leaf = cuboid(bm, -0.0050, 0.0050, y - 0.0016, y + 0.0016, COVER_TOP + 0.0035, z_ap - 0.0055)
    ap = ring(bm, y, z_ap, 0.0068, 0.0020, 0.0040)
    parts = leaf + ap
    if not raised:
        # turned about the hinge so its top goes back (game -y), lying just over the block's top
        for v in {v for f in parts for v in f.verts}:
            p = Vector((v.co.x, gy(v), gz(v))) - hinge
            q = Vector((p.x, -p.z, p.y)) + hinge + Vector((0.0, 0.0, 0.0018))
            v.co = (q.x, q.y, -q.z)
    return base + parts


def front_sight(bm, src_bm, raised, y_mid):
    """GoM's front sight block and hood (src_bm, at their squeezed place), lifted onto the folding post, and the
    post's two plates from the barrel collar; folded, everything above the hinge turned back along the barrel."""
    hinge = Vector((0.0, y_mid, 0.0325))
    new = []
    vmap = {}
    uv_src = src_bm.loops.layers.uv.active
    uv = bm.loops.layers.uv.active
    for f in src_bm.faces:
        vs = []
        for v in f.verts:
            if v not in vmap:
                vmap[v] = vert(bm, v.co.x, gy(v), gz(v) + FRONT_LIFT)
            vs.append(vmap[v])
        try:
            nf = bm.faces.new(vs)
        except ValueError:
            continue
        for l_new, l_old in zip(nf.loops, f.loops):
            l_new[uv].uv = l_old[uv_src].uv
        new.append(nf)
    post = []
    for sx in (-1, 1):
        post += cuboid(bm, sx * 0.0030, sx * 0.0042, y_mid - 0.0040, y_mid + 0.0040, 0.0300, 0.0285 + FRONT_LIFT + 0.004)
    paint_steel(bm, post)
    group = new + post
    if not raised:
        vs = {v for f in group for v in f.verts}
        for v in vs:
            p = Vector((v.co.x, gy(v), gz(v))) - hinge
            q = Vector((p.x, -p.z, p.y))                   # the top goes back (game -y)
            v.co = (q.x, q.y + hinge.y, -(q.z + hinge.z))
        lowest = min(gz(v) for v in vs)
        lift = 0.0350 - lowest                             # lying on the barrel's top
        for v in vs:
            v.co.z -= lift
    return group


# --------------------------------------------------------------------------------------------- the build
def gom_points():
    text = open(f"{GOM}/scripts/MarzWeapons/models/weapons/semi_rifles.txt", encoding="utf-8").read()
    m = re.search(r"\bmodel\s+SVD\s*\{(.*?)\n    \}", text, re.S)
    out = {}
    for a in re.finditer(r"attachment\s+(\w+)\s*\{(.*?)\}", m.group(1), re.S):
        off = [float(x) for x in re.search(r"offset\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        rot = [float(x) for x in re.search(r"rotate\s*=\s*([-\d. ]+),", a.group(2)).group(1).split()]
        out[a.group(1)] = {"offset": off, "rotate": rot}
    return out


def squeeze_y(y):
    """GoM's barrel between its gas block and front sight squeezed; the front sight and beyond moved back"""
    d = py(FRONT_SIGHT_PHOTO) - GOM_SIGHT_MID
    if y >= BARREL_SIGHT:
        return y + d
    if y > BARREL_FROM:
        return BARREL_FROM + (y - BARREL_FROM) * (BARREL_SIGHT + d - BARREL_FROM) / (BARREL_SIGHT - BARREL_FROM)
    return y


def main():
    if GOM is None:
        sys.exit("Guns of Marz not found")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=f"{GOM}/models_X/weapons/firearms/SVD.fbx")
    body, bolt = bpy.data.objects["SVD_BODY"], bpy.data.objects["SVD_BOLT"]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.verts.ensure_lookup_table()

    # GoM's thumbhole stock (with its grip), butt plate and the screw in it
    delete_verts(bm, pick(bm, lambda x0, x1, y0, y1, z0, z1: y0 < -0.09 or (y1 < 0.06 and z0 < -0.04)))
    # GoM's SVD rear sight (the tangent leaf on the barrel ahead of the receiver)
    delete_verts(bm, pick(bm, lambda x0, x1, y0, y1, z0, z1: y0 > 0.209 and y1 < 0.253 and z0 > 0.042))
    # GoM's SVD trigger and guard: replaced by the photo's (below)
    trig = pick(bm, lambda x0, x1, y0, y1, z0, z1: abs(y0 - GOM_TRIG[0]) < 0.001 and abs(y1 - GOM_TRIG[1]) < 0.001)
    guard = pick(bm, lambda x0, x1, y0, y1, z0, z1: abs(y0 - GOM_GUARD[0]) < 0.001 and abs(y1 - GOM_GUARD[1]) < 0.001)
    assert trig and guard, "GoM's SVD trigger or guard not found"
    delete_verts(bm, trig + guard)
    # the scope rail on the receiver's left (+x): the plate and its two pins
    rail = pick(bm, lambda x0, x1, y0, y1, z0, z1: x0 > 0.007 and 0.05 < y0 and y1 < 0.15 and z1 < 0.02)
    assert rail, "GoM's SVD side rail not found"
    for v in rail:
        v.co.y += RAIL_MOVE
    print("rail vertices", len(rail))
    # the front sight block's upper part (tower, pins, hood, post) is rebuilt on its folding post: kept aside
    sight_src = pick(bm, lambda x0, x1, y0, y1, z0, z1: y0 > 0.584 and y1 < 0.6040 and z0 > 0.0284)
    src = bmesh.new()
    src_uv = src.loops.layers.uv.new("UVMap")
    uv = bm.loops.layers.uv.active
    smap = {}
    sset = set(sight_src)
    for f in bm.faces:
        if all(v in sset for v in f.verts):
            vs = []
            for v in f.verts:
                if v not in smap:
                    smap[v] = src.verts.new(v.co)
                vs.append(smap[v])
            nf = src.faces.new(vs)
            for a, b in zip(nf.loops, f.loops):
                a[src_uv].uv = b[uv].uv
    delete_verts(bm, sight_src)
    # the barrel squeezed, the front sight block and what is beyond it moved back
    for v in bm.verts:
        v.co.y = squeeze_y(gy(v))
    for v in src.verts:
        v.co.y = squeeze_y(v.co.y)
    y_sight = squeeze_y(GOM_SIGHT_MID)
    gom_uvs_to_quarter(bm)
    for f in src.faces:
        for l in f.loops:
            l[src_uv].uv = to_quarter(*l[src_uv].uv)

    # new parts
    camo = []
    butt = [(py(x), pz(r)) for x, r in BUTT]
    camo.append((prism(bm, butt, BUTT_HW, 0.0022), (0.02, 0.30)))
    grip = [(py(x), pz(r)) for x, r in GRIP]
    camo.append((prism(bm, grip, GRIP_HW, 0.0020), (-0.13, 0.12)))
    c0, c1 = py(CHEEK[0]), py(CHEEK[1])
    t = CHEEK_T
    cheek = [(c0, CHEEK_Z - 0.0006), (c1, CHEEK_Z - 0.0006), (c1 + 0.002, CHEEK_Z + t * 0.5), (c1 - 0.002, CHEEK_Z + t),
             (c0 + 0.004, CHEEK_Z + t), (c0, CHEEK_Z + t * 0.6)]
    camo.append((prism(bm, cheek, CHEEK_HW, 0.0012), (0.24, 0.40)))
    bm.normal_update()
    for faces, origin in camo:
        paint_camo(bm, faces, origin)
    h0, h1, hz1, hhw = HOUSING
    yb, split, ye = pz_t(HOUSING_ROW), HOUSING_TOP[0][0] - SHIFT, py(h1)
    paint_steel(bm, cuboid(bm, -hhw, hhw, py(h0), split, yb, hz1))
    top = [(y - SHIFT, z) for y, z in HOUSING_TOP if y - SHIFT < ye]
    (ya, za), (yc, zc) = top[-1], next((y - SHIFT, z) for y, z in HOUSING_TOP if y - SHIFT >= ye)
    top.append((ye, za + (zc - za) * (ye - ya) / (yc - ya)))
    paint_steel(bm, prism(bm, [(split, yb)] + top + [(ye, yb)], hhw, 0.0002))
    paint_steel(bm, strip(bm, [(py(L), pz_t(r)) for L, r in GUARD_OUT], [(py(L), pz_t(r)) for L, r in GUARD_IN],
                          GUARD_HW))
    paint_steel(bm, prism(bm, [(py(L), pz_t(r)) for L, r in TRIGGER], TRIGGER_HW, 0.0003))
    can = [(py(x), r * R) for x, r in CAN]
    paint_can(bm, lathe(bm, can, None, BORE_Z, CAN_SIDES), can[0][0], can[-1][0] + 0.006, 9.0 * R)

    base = bpy.data.meshes.new("SVU_BASE")
    bm.normal_update()
    bm.to_mesh(base)
    bm.free()

    out = []
    for name, raised in (("SVU_BODY", True), ("SVU_FD_BODY", False)):
        b = bmesh.new()
        b.from_mesh(base)
        if not b.loops.layers.uv.active:
            b.loops.layers.uv.new("UVMap")
        paint_steel(b, rear_sight(b, raised))
        front_sight(b, src, raised, y_sight)
        for v in b.verts:
            v.co.y += SHIFT
        b.normal_update()
        bmesh.ops.recalc_face_normals(b, faces=b.faces)
        me = bpy.data.meshes.new(name)
        b.to_mesh(me)
        b.free()
        me.transform(Matrix.Scale(SCALE, 4))
        o = bpy.data.objects.new(name, me)
        o.rotation_euler = body.rotation_euler.copy()
        o.scale = body.scale.copy()
        bpy.context.scene.collection.objects.link(o)
        out.append(o)
        print(name, len(me.vertices), "verts")
    for v in bolt.data.vertices:
        v.co.y += SHIFT
    bolt.data.transform(Matrix.Scale(SCALE, 4))
    bolt.name = bolt.data.name = "SVU_BOLT"
    out.append(bolt)
    bpy.data.objects.remove(body)
    svu_texture()

    bpy.ops.object.select_all(action='DESELECT')
    for o in out:
        o.select_set(True)
    os.makedirs(os.path.dirname(OUT_GUN), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=OUT_GUN, use_selection=True, object_types={'MESH'})
    print("wrote", OUT_GUN, sorted(o.name for o in out))

    # points: GoM's SVD's, moved with the parts they belong to
    pts = gom_points()
    keep = {k: pts[k] for k in ("magazine", "bolt_fired", "rail_up", "scope", "world")}
    keep["rail_up"]["offset"][1] += RAIL_MOVE
    keep["scope"]["offset"][1] += RAIL_MOVE
    muzzle_y = py(max(x for x, _ in CAN))
    keep["muzzle"] = {"offset": [0.0, muzzle_y, BORE_Z], "rotate": pts["muzzle"]["rotate"]}
    # the gun lies on the floor round its middle as GoM's SVD does (its world point 0.125 behind its middle)
    mid = (py(0.0) + muzzle_y) / 2.0
    keep["world"]["offset"][1] = mid - (0.255 - pts["world"]["offset"][1])
    for k, p in keep.items():
        if k != "bolt_fired":
            p["offset"][1] += SHIFT
        p["offset"] = [round(x * SCALE, 4) + 0.0 for x in p["offset"]]
    keep["_extras"] = {"scale": SCALE, "shift": round(SHIFT, 5), "gom_unit_per_mm": R,
                       "length_mm_drawn": round((py(905) - py(0)) / R, 1)}
    with open(POINTS, "w") as fh:
        json.dump(keep, fh, indent=2)
        fh.write("\n")
    print("wrote", POINTS)


main()
