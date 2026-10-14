#!/usr/bin/env python3
"""Inventory icons and world-model textures for GoM Extension: Guns of Tien.

Everything is derived from Guns of Marz's own PNGs and meshes (read only); nothing here is hand-edited.

How GoM marks its 5.56 variants (SS / AP / HP / OP), which this script copies:
  * Rounds: the front 72% of the bullet (f >= 0.28 along it) is painted one flat colour (SS blue, AP red,
    HP dark green, OP purple), keeping the texture's shading. GoM's round icons are renders of the round mesh;
    the same paint shows on the icon's bullet tip, a little lighter (read from its 5.56 icons).
  * Boxes: the rifle box texture's accent band (the L-shaped background round the side labels) takes a light
    shade of the variant colour, the fine-print panel becomes a label naming the load in the variant colour
    ("subsonic rounds", "HOLLOW POINT", "[P+]"), and the bullet drawn on the box gets the tip. GoM's box icons
    are renders of the box mesh with that texture.
  * Shotgun boxes (buckshot / slug) differ only by the colour of their printed panel.

Icons: the round and box meshes are read from GoM's Rounds.fbx and the game's box FBX files, and an
orthographic camera fitted to each GoM icon (silhouette + colour, CAMERAS below; `--fit` searches again) says
which texel every icon pixel shows. Round icons are painted where the mesh shows painted texels; box icons get
the texture's change added to each pixel, scaled by the icon's own shading. Print recolours (handgun boxes,
12 gauge) are hue swaps done on texture and icon alike.

Usage:  python3 make_art.py            write every output
        python3 make_art.py --fit      re-fit the icon cameras and print them
        python3 make_art.py --sheet P  also write a contact sheet to P
"""

import colorsys
import math
import os
import struct
import sys
import zlib

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSHOP = os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600")
GOM = os.path.join(WORKSHOP, "3722134990/mods/GunsOfMarz/42.16/media")
GAME = os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/"
                          "Project Zomboid.app/Contents/Java/media")
OUT = os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media/textures")

GOM_TEX = os.path.join(GOM, "textures")
GOM_ROUNDS = os.path.join(GOM_TEX, "worlditems/Ammunition/Rounds")
GOM_BOXES = os.path.join(GOM_TEX, "worlditems/Ammunition/Boxes")
ROUNDS_FBX = os.path.join(GOM, "models_X/worlditems/Ammunition/Rounds.fbx")
BOX_FBX = os.path.join(GAME, "models_X/WorldItems/%s.fbx")

FONT = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"


# ==================================================================================================
# Binary FBX: just enough to read meshes (vertices, polygons, UVs) by geometry name.
# ==================================================================================================

_SCALAR = {"Y": "<h", "C": "<b", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}
_ARRAY = {"f": "f", "d": "d", "l": "q", "b": "b", "i": "i", "c": "B"}


def _read_node(data, off, version):
    if version >= 7500:
        end, nprops, _ = struct.unpack_from("<QQQ", data, off)
        off += 24
    else:
        end, nprops, _ = struct.unpack_from("<III", data, off)
        off += 12
    name_len = data[off]
    off += 1
    name = data[off:off + name_len].decode("utf-8", "replace")
    off += name_len
    if end == 0:
        return None, off
    props = []
    for _ in range(nprops):
        kind = chr(data[off])
        off += 1
        if kind in _SCALAR:
            fmt = _SCALAR[kind]
            props.append(struct.unpack_from(fmt, data, off)[0])
            off += struct.calcsize(fmt)
        elif kind in _ARRAY:
            count, encoding, length = struct.unpack_from("<III", data, off)
            off += 12
            raw = data[off:off + length]
            off += length
            if encoding == 1:
                raw = zlib.decompress(raw)
            props.append(list(struct.unpack("<%d%s" % (count, _ARRAY[kind]), raw)))
        elif kind in "SR":
            length = struct.unpack_from("<I", data, off)[0]
            off += 4
            props.append(data[off:off + length])
            off += length
        else:
            raise ValueError("unknown FBX property type %r" % kind)
    children = []
    while off < end:
        node, off = _read_node(data, off, version)
        if node is None:
            break
        children.append(node)
    return {"name": name, "props": props, "children": children}, end


def _walk(nodes, name):
    for node in nodes:
        if node["name"] == name:
            yield node
        yield from _walk(node["children"], name)


_mesh_cache = {}


def load_mesh(path, geometry=None):
    """Triangles of one mesh as [(p0, p1, p2), (uv0, uv1, uv2)], positions centred on the bounding box."""
    key = (path, geometry)
    if key in _mesh_cache:
        return _mesh_cache[key]
    with open(path, "rb") as handle:
        data = handle.read()
    version = struct.unpack_from("<I", data, 23)[0]
    off, roots = 27, []
    while off < len(data) - 160:
        node, off = _read_node(data, off, version)
        if node is None:
            break
        roots.append(node)
    geos = list(_walk(roots, "Geometry"))
    if geometry is not None:
        geos = [g for g in geos if g["props"][1].split(b"\x00")[0].decode() == geometry]
    geo = geos[0]
    child = lambda parent, nm: next(c for c in parent["children"] if c["name"] == nm)
    flat = child(geo, "Vertices")["props"][0]
    pvi = child(geo, "PolygonVertexIndex")["props"][0]
    layer = child(geo, "LayerElementUV")
    uvs = child(layer, "UV")["props"][0]
    direct = b"IndexToDirect" in child(layer, "ReferenceInformationType")["props"][0]
    uv_index = child(layer, "UVIndex")["props"][0] if direct else None
    verts = [(flat[i * 3], flat[i * 3 + 1], flat[i * 3 + 2]) for i in range(len(flat) // 3)]
    centre = [(min(a) + max(a)) / 2 for a in zip(*verts)]
    verts = [tuple(v[k] - centre[k] for k in range(3)) for v in verts]

    def uv_of(corner):
        i = uv_index[corner] if uv_index is not None else corner
        return uvs[i * 2], uvs[i * 2 + 1]

    tris, poly = [], []
    for corner, index in enumerate(pvi):
        last = index < 0
        poly.append((~index if last else index, corner))
        if last:
            for i in range(1, len(poly) - 1):
                trio = (poly[0], poly[i], poly[i + 1])
                tris.append(([verts[v] for v, _ in trio], [uv_of(c) for _, c in trio]))
            poly = []
    _mesh_cache[key] = tris
    return tris


# ==================================================================================================
# Rasterising: which texel (u, v) every icon sub-pixel shows, and which mesh point every texel is.
# ==================================================================================================

def _rotate(p, yaw, pitch, roll):
    x, y, z = p
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))
    x, y = x * cy - y * sy, x * sy + y * cy
    y, z = y * cp - z * sp, y * sp + z * cp
    x, z = x * cr - z * sr, x * sr + z * cr
    return x, -z, -y                       # screen x, screen y (down), depth (bigger = nearer)


def _fill_triangle(pts, attrs, width, height, store):
    """Barycentric fill; store(x, y, depth, interpolated attrs) for every covered pixel centre."""
    (ax, ay), (bx, by), (cx, cy) = [(p[0], p[1]) for p in pts]
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12:
        return
    x0 = max(0, int(math.floor(min(ax, bx, cx))))
    x1 = min(width - 1, int(math.ceil(max(ax, bx, cx))))
    y0 = max(0, int(math.floor(min(ay, by, cy))))
    y1 = min(height - 1, int(math.ceil(max(ay, by, cy))))
    for y in range(y0, y1 + 1):
        py = y + 0.5
        for x in range(x0, x1 + 1):
            px = x + 0.5
            wa = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
            wb = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
            wc = 1 - wa - wb
            if wa < -1e-6 or wb < -1e-6 or wc < -1e-6:
                continue
            depth = wa * pts[0][2] + wb * pts[1][2] + wc * pts[2][2]
            interp = tuple(wa * attrs[0][k] + wb * attrs[1][k] + wc * attrs[2][k] for k in range(len(attrs[0])))
            store(x, y, depth, interp)


def icon_uv_grid(tris, camera, size=32, ss=4):
    """uv per sub-pixel (size*ss square, None where empty), the model fitted into camera['bbox']."""
    yaw, pitch, roll = camera["yaw"], camera["pitch"], camera.get("roll", 0.0)
    proj = [([_rotate(p, yaw, pitch, roll) for p in ps], uvs) for ps, uvs in tris]
    xs = [p[0] for ps, _ in proj for p in ps]
    ys = [p[1] for ps, _ in proj for p in ps]
    bx0, by0, bx1, by1 = camera["bbox"]
    scale = min((bx1 - bx0) / (max(xs) - min(xs)), (by1 - by0) / (max(ys) - min(ys))) * ss
    ox = bx0 * ss + ((bx1 - bx0) * ss - (max(xs) - min(xs)) * scale) / 2
    oy = by0 * ss + ((by1 - by0) * ss - (max(ys) - min(ys)) * scale) / 2
    side = size * ss
    grid = [[None] * side for _ in range(side)]
    depth = [[-1e30] * side for _ in range(side)]

    def store(x, y, d, uv):
        if d > depth[y][x]:
            depth[y][x] = d
            grid[y][x] = uv

    for ps, uvs in proj:
        pts = [((p[0] - min(xs)) * scale + ox, (p[1] - min(ys)) * scale + oy, p[2]) for p in ps]
        _fill_triangle(pts, uvs, side, side, store)
    return grid


def texel_positions(tris, width, height):
    """Mesh point (x, y, z) behind every texel, None where no triangle maps (UV space raster)."""
    grid = [[None] * width for _ in range(height)]

    def store(x, y, d, pos):
        grid[y][x] = pos

    for ps, uvs in tris:
        pts = [(u * width, (1 - v) * height, 0.0) for u, v in uvs]
        _fill_triangle(pts, ps, width, height, store)
    return grid


# ==================================================================================================
# Colour helpers
# ==================================================================================================

def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def clamp8(v):
    return max(0, min(255, int(round(v))))


def paint(c, colour, ref_lum, gamma=1.0):
    """Repaint pixel c flat `colour`, keeping its shading relative to ref_lum (GoM's tip paint does this)."""
    k = (max(lum(c), 1.0) / ref_lum) ** gamma
    return tuple(clamp8(colour[i] * k) for i in range(3)) + tuple(c[3:])


def set_hue(c, hue, sat_scale=1.0, val_scale=1.0):
    r, g, b = (v / 255.0 for v in c[:3])
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, min(1.0, s * sat_scale), min(1.0, v * val_scale))
    return (clamp8(r * 255), clamp8(g * 255), clamp8(b * 255)) + tuple(c[3:])


def hue_of(c):
    h, s, v = colorsys.rgb_to_hsv(*(x / 255.0 for x in c[:3]))
    return h * 360.0, s, v


# ==================================================================================================
# Icon transfer: icon pixel += shading * (new texel average - old texel average)
# ==================================================================================================

def _texel_average(grid, tex, size, ss):
    tw, th = tex.size
    px = tex.load()
    out = [[None] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            acc, n = [0.0, 0.0, 0.0], 0
            for j in range(ss):
                for i in range(ss):
                    uv = grid[y * ss + j][x * ss + i]
                    if uv is None:
                        continue
                    c = px[min(tw - 1, max(0, int(uv[0] % 1.0 * tw))), min(th - 1, max(0, int((1 - uv[1] % 1.0) * th)))]
                    acc[0] += c[0]
                    acc[1] += c[1]
                    acc[2] += c[2]
                    n += 1
            if n:
                out[y][x] = (acc[0] / n, acc[1] / n, acc[2] / n, n / (ss * ss))
    return out


def transfer_icon(icon, tris, camera, old_tex, new_tex, ss=4):
    """Add the texture's change (old_tex -> new_tex) to the icon pixels showing it, scaled by their shading."""
    grid = icon_uv_grid(tris, camera, icon.width, ss)
    old = _texel_average(grid, old_tex.convert("RGB"), icon.width, ss)
    new = _texel_average(grid, new_tex.convert("RGB"), icon.width, ss)
    out = icon.copy()
    src, dst = icon.load(), out.load()
    for y in range(icon.height):
        for x in range(icon.width):
            c = src[x, y]
            if old[y][x] is None or c[3] == 0:
                continue
            shade = max(0.3, min(1.8, (lum(c) + 8) / (lum(old[y][x]) + 8)))
            dst[x, y] = tuple(clamp8(c[k] + shade * (new[y][x][k] - old[y][x][k])) for k in range(3)) + (c[3],)
    return out


# ==================================================================================================
# Camera fitting (only for --fit; results are stored in CAMERAS)
# ==================================================================================================

def alpha_bbox(icon, threshold=40):
    a = icon.getchannel("A")
    pts = [(x, y) for y in range(icon.height) for x in range(icon.width) if a.getpixel((x, y)) > threshold]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1)


def silhouette_error(icon, tris, camera, ss=3):
    grid = icon_uv_grid(tris, camera, icon.width, ss)
    a = icon.getchannel("A").load()
    err = 0.0
    for y in range(icon.height):
        for x in range(icon.width):
            cover = sum(1 for j in range(ss) for i in range(ss) if grid[y * ss + j][x * ss + i] is not None)
            err += abs(cover / (ss * ss) - a[x, y] / 255.0)
    return err


def colour_error(icon, tris, camera, tex, ss=3):
    """Mean error after the best per-channel gain: tells mirror / 180 degree twins of a silhouette apart."""
    grid = icon_uv_grid(tris, camera, icon.width, ss)
    avg = _texel_average(grid, tex.convert("RGB"), icon.width, ss)
    src = icon.load()
    pairs = [(src[x, y], avg[y][x]) for y in range(icon.height) for x in range(icon.width)
             if avg[y][x] is not None and src[x, y][3] > 200]
    gains = []
    for k in range(3):
        den = sum(b[k] * b[k] for _, b in pairs) or 1.0
        gains.append(sum(a[k] * b[k] for a, b in pairs) / den)
    return sum(abs(a[k] - gains[k] * b[k]) for a, b in pairs for k in range(3)) / max(1, len(pairs))


def fit_camera(icon, tris, tex):
    """Coarse grid on silhouette + colour, then a pattern search on the same score.

    Silhouette alone cannot tell a box from its 180 degree twin, so the colour match (texture rendered through
    the camera against the icon) is part of the score from the start."""
    bbox = alpha_bbox(icon)

    def score(cam, ss=3):
        return silhouette_error(icon, tris, cam, ss) + 0.3 * colour_error(icon, tris, cam, tex, ss)

    cands = []
    for yaw in range(0, 360, 15):
        for pitch in range(-75, 90, 15):
            for roll in range(-90, 91, 15):
                cam = {"yaw": float(yaw), "pitch": float(pitch), "roll": float(roll), "bbox": bbox}
                cands.append((silhouette_error(icon, tris, cam, 2), cam))
    cands.sort(key=lambda c: c[0])
    best = None
    for _, cam in cands[:16]:
        cur, cur_err, step = dict(cam), score(cam), 4.0
        while step >= 0.5:
            improved = False
            for key in ("yaw", "pitch", "roll"):
                for d in (-step, step):
                    trial = dict(cur)
                    trial[key] += d
                    e = score(trial)
                    if e < cur_err - 1e-9:
                        cur, cur_err, improved = trial, e, True
            if not improved:
                step /= 2
        if best is None or cur_err < best[0]:
            best = (cur_err, cur)
    return best


# ==================================================================================================
# GoM's own variant colours, read from its 5.56 textures
# ==================================================================================================

def _median(values):
    values = sorted(values)
    return values[len(values) // 2]


def _median_colour(pixels):
    return tuple(int(_median([c[k] for c in pixels])) for k in range(3))


_band_mask = None


def band_mask():
    """GoM's rifle box template: the L-shaped accent band, i.e. the green background of 556x45_Box."""
    global _band_mask
    if _band_mask is None:
        px = Image.open(os.path.join(GOM_BOXES, "556x45_Box.png")).convert("RGB").load()
        _band_mask = {(x, y) for y in range(128) for x in range(64)
                      if px[x, y][1] > px[x, y][0] + 8 and px[x, y][1] > px[x, y][2] + 8}
    return _band_mask


LABEL_RECT = (31, 6, 46, 73)        # the fine-print panel GoM turns into the variant label (x0, y0, x1, y1 incl.)


def gom_scheme(variant):
    """(tip paint, band colour, label text colour) of a GoM 5.56 variant: SS, AP, HP or OP."""
    base = Image.open(os.path.join(GOM_ROUNDS, "Nato_Round_Base.png")).convert("RGBA").load()
    var = Image.open(os.path.join(GOM_ROUNDS, "Nato_Round_%s.png" % variant)).convert("RGBA").load()
    painted = [(base[x, y], var[x, y]) for y in range(3, 31) for x in range(30, 101)
               if var[x, y][3] > 200 and max(abs(base[x, y][k] - var[x, y][k]) for k in range(3)) > 25]
    # Normalise each painted texel to the bullet's median brightness, then take the median: GoM's flat paint.
    ref = _median([lum(b) for b, _ in painted])
    tip = _median_colour([tuple(v[k] * ref / max(lum(b), 1.0) for k in range(3)) for b, v in painted])
    box = Image.open(os.path.join(GOM_BOXES, "556x45_Box_%s.png" % variant)).convert("RGB").load()
    band = _median_colour([box[x, y] for x, y in band_mask()])
    x0, y0, x1, y1 = LABEL_RECT
    label = sorted((box[x, y] for y in range(y0 + 2, y1 - 1) for x in range(x0 + 2, x1 - 1)), key=lum)
    text = _median_colour(label[:len(label) // 8])
    return {"tip": tip, "band": band, "text": text}


# ==================================================================================================
# The variants
# ==================================================================================================
# Paint on a bullet is a list of (f0, f1, colour): f is the position along the exposed bullet, 0 at the case
# mouth, 1 at the point. GoM paints f >= 0.28 (rows 3-19 of its bullet island).

GOM_PAINT_FROM = 0.28

LEAD = (100, 102, 110)            # exposed soft lead: dull dark grey
STEEL = (206, 211, 217)         # bright bare steel
BLACK = (30, 30, 32)
US_GREEN = (48, 140, 62)        # Soviet "US" subsonic band


def schemes():
    s = {v: gom_scheme(v) for v in ("SS", "AP", "HP", "OP")}
    return {
        "SS": dict(paint=[(GOM_PAINT_FROM, 1.0, s["SS"]["tip"])], band=s["SS"]["band"], text=s["SS"]["text"]),
        "AP": dict(paint=[(GOM_PAINT_FROM, 1.0, s["AP"]["tip"])], band=s["AP"]["band"], text=s["AP"]["text"]),
        "HP": dict(paint=[(GOM_PAINT_FROM, 1.0, s["HP"]["tip"])], band=s["HP"]["band"], text=s["HP"]["text"]),
        "OP": dict(paint=[(GOM_PAINT_FROM, 1.0, s["OP"]["tip"])], band=s["OP"]["band"], text=s["OP"]["text"]),
        # Not in GoM: black point over a green band (Soviet US); boxes use GoM's subsonic colours.
        "US": dict(paint=[(0.30, 0.56, US_GREEN), (0.56, 1.0, BLACK)], band=s["SS"]["band"], text=s["SS"]["text"]),
        # SP-6: real black point (GoM's AP red would look like the plain 9x39's orange point); box in AP colours.
        "SP6": dict(paint=[(GOM_PAINT_FROM, 1.0, BLACK)], band=s["AP"]["band"], text=s["AP"]["text"]),
        # Not in GoM: exposed lead point; boxes amber.
        "SP": dict(paint=[(0.35, 1.0, LEAD)], band=(247, 172, 96), text=(150, 62, 10)),
        # Not in GoM: silver steel point in GoM's tip style; boxes steel blue-grey.
        "STEEL": dict(paint=[(GOM_PAINT_FROM, 1.0, STEEL)], band=(192, 202, 212), text=(46, 56, 72)),
    }


# ==================================================================================================
# Cameras: GoM icon -> mesh view, found with --fit (yaw, pitch, roll in degrees; bbox = icon pixels it fills)
# ==================================================================================================

CAMERAS = {
    "item_762x39_Round_Base.png": dict(yaw=315.0, pitch=-84.0, roll=90.0, bbox=(0, 0, 32, 32)),
    "item_9x39_Round_Base.png": dict(yaw=269.5, pitch=0.0, roll=45.5, bbox=(0, 0, 32, 32)),
    "item_9x19_Round_Base.png": dict(yaw=269.5, pitch=31.5, roll=46.0, bbox=(0, 0, 32, 32)),
    "item_45_Round_Base.png": dict(yaw=269.5, pitch=36.5, roll=45.5, bbox=(0, 0, 32, 32)),
    "item_3006_Round_Base.png": dict(yaw=269.5, pitch=14.0, roll=45.0, bbox=(0, 0, 32, 32)),
    "item_308_Round.png": dict(yaw=269.0, pitch=12.0, roll=45.0, bbox=(0, 0, 32, 32)),
    "item_556x45_Round_Base.png": dict(yaw=269.5, pitch=-54.0, roll=45.0, bbox=(0, 0, 32, 32)),
    # Every rifle box icon is the same render of RifleAmmoBox.
    "item_762x39_Box.png": dict(yaw=42.5, pitch=45.0, roll=2.0, bbox=(0, 2, 32, 30)),
    "item_9x39_Box.png": dict(yaw=42.5, pitch=45.0, roll=2.0, bbox=(0, 2, 32, 30)),
    "item_3006_Box.png": dict(yaw=42.5, pitch=45.0, roll=2.0, bbox=(0, 2, 32, 30)),
    "item_308_Box.png": dict(yaw=42.5, pitch=45.0, roll=2.0, bbox=(0, 2, 32, 30)),
    "item_556x45_Box.png": dict(yaw=42.5, pitch=45.0, roll=2.0, bbox=(0, 2, 32, 30)),
    "item_9x19_Box.png": dict(yaw=237.0, pitch=34.0, roll=-0.5, bbox=(0, 3, 32, 30)),
    "item_45_Box.png": dict(yaw=236.5, pitch=33.5, roll=1.0, bbox=(0, 3, 32, 30)),
}



# ==================================================================================================
# What to make
# ==================================================================================================
# Round: name, round mesh (submesh of GoM's Rounds.fbx), GoM texture of that model, GoM icon, scheme.

ROUNDS = [
    ("762x39_Round_US", "762x39_Round", "Russian_Steel_Round_Base", "item_762x39_Round_Base.png", "US"),
    ("762x39_Round_SP", "762x39_Round", "Russian_Steel_Round_Base", "item_762x39_Round_Base.png", "SP"),
    ("762x39_Round_SteelCore", "762x39_Round", "Russian_Steel_Round_Base", "item_762x39_Round_Base.png", "STEEL"),
    ("9x19_Round_SS", "9x19_Round", "Pistol_Standard_Round_Base", "item_9x19_Round_Base.png", "SS"),
    ("9x19_Round_HP", "9x19_Round", "Pistol_Standard_Round_Base", "item_9x19_Round_Base.png", "HP"),
    ("9x19_Round_PPP", "9x19_Round", "Pistol_Standard_Round_Base", "item_9x19_Round_Base.png", "OP"),
    ("45_Round_HP", "45_Round", "Pistol_Medium_Round_Base", "item_45_Round_Base.png", "HP"),
    ("45_Round_P", "45_Round", "Pistol_Medium_Round_Base", "item_45_Round_Base.png", "OP"),
    ("9x39_Round_SP6", "9x39_Round", "Russian_Steel_Round_Base", "item_9x39_Round_Base.png", "SP6"),
    ("3006_Round_SP", "3006_Round", "Nato_Round_Base", "item_3006_Round_Base.png", "SP"),
    ("308_Round_SP", "762x51_Round", "Nato_Round_CIV", "item_308_Round.png", "SP"),
]

# Rifle boxes share GoM's template (band, label panel, bullet drawing). bullet = (tip, mouth, across0, across1,
# axis): the drawn projectile, from its point to the case mouth, along x (pointing left) or y (pointing up).
RIFLE_BOXES = {
    "762x39": dict(tex="762x39_Box", icon="item_762x39_Box.png", bullet=(1, 12, 113, 122, "x")),
    "9x39": dict(tex="9x39_Box", icon="item_9x39_Box.png", bullet=(81, 96, 33, 43, "y")),
    # The .30-06 band is shaded tan, close to its panel colour: a wider match takes all of it.
    "3006": dict(tex="3006_Box", icon="item_3006_Box.png", bullet=(2, 13, 113, 122, "x"), band_tolerance=125),
    "308": dict(tex="308_Box", icon="item_308_Box.png", bullet=(2, 12, 113, 122, "x")),
}

BOXES = [
    # name, base calibre, scheme, label
    ("762x39_Box_US", "762x39", "US", "US SUBSONIC"),
    ("762x39_Box_SP", "762x39", "SP", "SOFT POINT"),
    ("762x39_Box_SteelCore", "762x39", "STEEL", "STEEL CORE"),
    ("9x39_Box_SP6", "9x39", "SP6", "SP-6 AP"),
    ("3006_Box_SP", "3006", "SP", "SOFT POINT"),
    ("308_Box_SP", "308", "SP", "SOFT POINT"),
    ("9x19_Box_SS", "9x19", "SS", "SUBSONIC"),          # 9x19: short, the lid sticker is small
    ("9x19_Box_HP", "9x19", "HP", "HOLLOW PT"),
    ("9x19_Box_PPP", "9x19", "OP", "[+P+]"),
    ("45_Box_HP", "45", "HP", "HOLLOW POINT"),
    ("45_Box_P", "45", "OP", "[+P]"),
]

BIRDSHOT_HUE = 222.0             # royal blue hull: GoM uses red (buckshot), green (slug), yellow (.410 model)


# ==================================================================================================
# Rounds
# ==================================================================================================

def bullet_fractions(geometry, width=128, height=128):
    """{(x, y): f} for the bullet's UV island (GoM's rounds all share one layout), f 0 at the case mouth .. 1 at
    the point, measured along the mesh's own axis; texels in the island's gutter take their neighbour's f."""
    tris = load_mesh(ROUNDS_FBX, geometry)
    grid = texel_positions(tris, width, height)
    axis = max(range(3), key=lambda k: max(abs(p[k]) for ps, _ in tris for p in ps))
    cells = [(x, y) for y in range(height) for x in range(width) if grid[y][x] is not None]
    # Each end of the axis starts a UV island: the bullet (a long dome) at the point, the flat head / primer
    # disc at the other end. The point is the end whose island spans more of the axis.
    best = None
    for sign in (1, -1):
        end = max(cells, key=lambda c: sign * grid[c[1]][c[0]][axis])
        island = _flood(grid, end, width, height)
        values = {c: sign * grid[c[1]][c[0]][axis] for c in island}
        extent = max(values.values()) - min(values.values())
        if best is None or extent > best[0]:
            best = (extent, island, values)
    _, island, values = best
    lo, hi = min(values.values()), max(values.values())
    f = {c: (v - lo) / (hi - lo) for c, v in values.items()}
    xs, ys = [c[0] for c in island], [c[1] for c in island]
    for _ in range(3):                                   # spread into the gutter
        grown = dict(f)
        for y in range(max(0, min(ys) - 3), min(height, max(ys) + 4)):
            for x in range(max(0, min(xs) - 3), min(width, max(xs) + 4)):
                if (x, y) in grown or grid[y][x] is not None:
                    continue
                near = [f[n] for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)) if n in f]
                if near:
                    grown[(x, y)] = sum(near) / len(near)
        f = grown
    return f


def _flood(grid, start, width, height):
    seen, stack = {start}, [start]
    while stack:
        x, y = stack.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < width and 0 <= n[1] < height and n not in seen and grid[n[1]][n[0]] is not None:
                seen.add(n)
                stack.append(n)
    return seen


def colour_at(paint_list, f):
    for f0, f1, colour in paint_list:
        if f0 <= f <= f1:
            return colour
    return None


def paint_round_texture(tex, fractions, paint_list):
    out = tex.convert("RGBA").copy()
    px = out.load()
    ref = _median([lum(px[x, y]) for (x, y) in fractions if px[x, y][3] > 200])
    for (x, y), f in fractions.items():
        colour = colour_at(paint_list, f)
        if colour is not None and px[x, y][3] > 0:
            px[x, y] = paint(px[x, y], colour, ref)
    return out


def paint_coverage(grid, fractions, paint_list, size, ss, tex_size=128):
    """Per icon pixel: share of its sub-pixels on the bullet, and on each paint layer."""
    bullet = [[0.0] * size for _ in range(size)]
    layers = [[[0.0] * size for _ in range(size)] for _ in paint_list]
    for y in range(size):
        for x in range(size):
            hits = [0] * len(paint_list)
            on_bullet = 0
            for j in range(ss):
                for i in range(ss):
                    uv = grid[y * ss + j][x * ss + i]
                    if uv is None:
                        continue
                    key = (min(tex_size - 1, int(uv[0] % 1.0 * tex_size)),
                           min(tex_size - 1, int((1 - uv[1] % 1.0) * tex_size)))
                    f = fractions.get(key)
                    if f is None:
                        continue
                    on_bullet += 1
                    for n, (f0, f1, _) in enumerate(paint_list):
                        if f0 <= f <= f1:
                            hits[n] += 1
                            break
            bullet[y][x] = on_bullet / float(ss * ss)
            for n in range(len(paint_list)):
                layers[n][y][x] = hits[n] / float(ss * ss)
    return bullet, layers


_icon_paints = None


def icon_paint_colour(colour):
    """The colour a paint takes in a round icon. GoM's own four paints (SS, AP, HP, OP) are read from its 5.56
    icons, where they came out lighter than in the textures (AP orange-red, OP lilac); any other paint is used
    as is."""
    global _icon_paints
    if _icon_paints is None:
        tris = load_mesh(ROUNDS_FBX, "556x45_Round")
        fractions = bullet_fractions("556x45_Round")
        base = Image.open(os.path.join(GOM_TEX, "item_556x45_Round_Base.png")).convert("RGBA").load()
        grid = icon_uv_grid(tris, CAMERAS["item_556x45_Round_Base.png"], 32, 4)
        _, (painted,) = paint_coverage(grid, fractions, [(GOM_PAINT_FROM, 1.0, None)], 32, 4)
        cells = [(x, y) for y in range(32) for x in range(32) if painted[y][x] >= 0.75 and base[x, y][3] > 200]
        ref = _median([lum(base[c]) for c in cells])
        _icon_paints = {}
        for v in ("SS", "AP", "HP", "OP"):
            icon = Image.open(os.path.join(GOM_TEX, "item_556x45_Round_%s.png" % v)).convert("RGBA").load()
            seen = _median_colour([tuple(icon[c][k] * ref / max(lum(base[c]), 1.0) for k in range(3))
                                   for c in cells])
            _icon_paints[gom_scheme(v)["tip"]] = seen
    return _icon_paints.get(tuple(colour), tuple(colour))


def paint_round_icon(icon, geometry, camera, fractions, paint_list, ss=4):
    """Paint the icon where the mesh shows painted texels, the way the texture is painted (GoM's own method)."""
    grid = icon_uv_grid(load_mesh(ROUNDS_FBX, geometry), camera, icon.width, ss)
    bullet, layers = paint_coverage(grid, fractions, paint_list, icon.width, ss)
    out = icon.copy()
    src, dst = icon.load(), out.load()
    ref = _median([lum(src[x, y]) for y in range(icon.height) for x in range(icon.width)
                   if bullet[y][x] >= 0.75 and src[x, y][3] > 200])
    for y in range(icon.height):
        for x in range(icon.width):
            c = src[x, y]
            if c[3] == 0:
                continue
            new = list(c)
            for n, (_, _, colour) in enumerate(paint_list):
                w = layers[n][y][x]
                if w > 0:
                    target = paint(c, icon_paint_colour(colour), ref)
                    new = [new[k] * (1 - w) + target[k] * w for k in range(3)] + [c[3]]
            dst[x, y] = tuple(clamp8(v) for v in new[:3]) + (c[3],)
    return out


def make_round(name, geometry, model_tex, icon_name, scheme, sch):
    fractions = bullet_fractions(geometry)
    base = Image.open(os.path.join(GOM_ROUNDS, model_tex + ".png")).convert("RGBA")
    paint_list = sch[scheme]["paint"]
    world = paint_round_texture(base, fractions, paint_list)
    icon = Image.open(os.path.join(GOM_TEX, icon_name)).convert("RGBA")
    return paint_round_icon(icon, geometry, CAMERAS[icon_name], fractions, paint_list), world


def recolour_hue(img, hue, test, sat_scale=1.0):
    out = img.convert("RGBA").copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3] > 0 and test(c):
                px[x, y] = set_hue(c, hue, sat_scale)
    return out


def is_red(c):
    h, s, v = hue_of(c)
    return (h < 18 or h > 340) and s > 0.35 and v > 0.15


def is_reddish(c):
    """Red print in an icon, where rendering and scaling left it paler than in the texture."""
    h, s, v = hue_of(c)
    return (h < 20 or h > 335) and s > 0.18 and v > 0.12


def is_green(c):
    h, s, v = hue_of(c)
    return 70 < h < 170 and s > 0.15 and v > 0.12


# ==================================================================================================
# Boxes
# ==================================================================================================

def render_text(text, width, height, ink, vertical):
    """Anti-aliased text fitted into width x height; vertical text reads bottom to top like GoM's labels."""
    up = 8
    long_side, short_side = (height, width) if vertical else (width, height)
    size = int(short_side * up * 1.05)
    while True:
        font = ImageFont.truetype(FONT, size)
        x0, y0, x1, y1 = font.getbbox(text)
        if x1 - x0 <= long_side * up * 0.94 or size < 8:
            break
        size -= 2
    mask = Image.new("L", (x1 - x0 + 2 * up, y1 - y0 + 2 * up), 0)
    # A faint stroke keeps the letters as solid as GoM's after the 8x reduction.
    ImageDraw.Draw(mask).text((up - x0, up - y0), text, font=font, fill=255, stroke_width=max(1, size // 40),
                              stroke_fill=255)
    if vertical:
        mask = mask.rotate(90, expand=True)
    scale = min(width / mask.width, height / mask.height)
    mask = mask.resize((max(1, round(mask.width * scale)), max(1, round(mask.height * scale))), Image.LANCZOS)
    layer = Image.new("RGBA", (width, height), tuple(ink) + (0,))
    solid = Image.new("RGBA", mask.size, tuple(ink) + (255,))
    layer.paste(solid, ((width - mask.width) // 2, (height - mask.height) // 2), mask)
    return layer


def draw_label(img, rect, text, fill, ink, vertical=True):
    """GoM-style label panel: the variant's light colour, a border and the load's name in its dark colour."""
    x0, y0, x1, y1 = rect
    border = tuple(int(fill[k] * 0.55 + ink[k] * 0.45) for k in range(3))
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x1, y1), fill=tuple(fill))
    d.rectangle((x0, y0, x1, y1), outline=border)
    w, h = x1 - x0 - 3, y1 - y0 - 3
    layer = render_text(text, w, h, ink, vertical)
    img.alpha_composite(layer, (x0 + 2, y0 + 2))


def recolour_band(img, colour, tolerance=70):
    """GoM's variants turn the accent band their light colour; panels inside the band are left alone."""
    px = img.load()
    cells = [(x, y) for x, y in band_mask()]
    base = _median_colour([px[c] for c in cells])
    ref = lum(base)
    for c in cells:
        if sum(abs(px[c][k] - base[k]) for k in range(3)) < tolerance:
            px[c] = paint(px[c], colour, ref, gamma=0.5)


def paint_bullet_drawing(img, bullet, paint_list):
    tip, mouth, a0, a1, axis = bullet
    px = img.load()
    cells = []
    for along in range(min(tip, mouth), max(tip, mouth) + 1):
        for across in range(a0, a1 + 1):
            cells.append(((along, across) if axis == "x" else (across, along), along))
    background = _median_colour([px[x, y] for x, y in band_mask()])
    drawn = [(c, a) for c, a in cells if sum(abs(px[c][k] - background[k]) for k in range(3)) > 60]
    if not drawn:
        return
    ref = _median([lum(px[c]) for c, _ in drawn])
    for c, along in drawn:
        f = (mouth - along) / float(mouth - tip)
        colour = colour_at(paint_list, f)
        if colour is not None:
            px[c] = paint(px[c], colour, ref)


def make_rifle_box(calibre, scheme, label, sch):
    cfg = RIFLE_BOXES[calibre]
    base = Image.open(os.path.join(GOM_BOXES, cfg["tex"] + ".png")).convert("RGBA")
    tex = base.copy()
    s = sch[scheme]
    paint_bullet_drawing(tex, cfg["bullet"], s["paint"])
    recolour_band(tex, s["band"], cfg.get("band_tolerance", 70))
    draw_label(tex, LABEL_RECT, label, s["band"], s["text"])
    icon = Image.open(os.path.join(GOM_TEX, cfg["icon"])).convert("RGBA")
    out_icon = transfer_icon(icon, load_mesh(BOX_FBX % "RifleAmmoBox"), CAMERAS[cfg["icon"]], base, tex)
    return out_icon, tex


# Handgun boxes (HandGunAmmoBox): GoM's red print takes the variant's hue, and a label is added where the
# box has room for one (9x19: the "GUN AMMO" sticker on the lid flap; .45: beside the pistol, on the lid).
HANDGUN_BOXES = {
    "9x19": dict(tex="9x19_Box", icon="item_9x19_Box.png", label=((2, 3, 33, 17), False)),
    "45": dict(tex="45_Box", icon="item_45_Box.png", label=((47, 33, 62, 86), True)),
}


def make_handgun_box(calibre, scheme, label, sch):
    cfg = HANDGUN_BOXES[calibre]
    base = Image.open(os.path.join(GOM_BOXES, cfg["tex"] + ".png")).convert("RGBA")
    s = sch[scheme]
    hue = hue_of(s["paint"][-1][2])[0]
    recoloured = recolour_hue(base, hue, is_red)
    tex = recoloured.copy()
    rect, vertical = cfg["label"]
    draw_label(tex, rect, label, s["band"], s["text"], vertical)
    # The print colour is swapped on the icon directly (adding a red -> blue texel change to the icon's light
    # edge pixels turns them neon); only the label goes through the camera transfer.
    icon = recolour_hue(Image.open(os.path.join(GOM_TEX, cfg["icon"])), hue, is_reddish)
    out_icon = transfer_icon(icon, load_mesh(BOX_FBX % "HandGunAmmoBox"), CAMERAS[cfg["icon"]], recoloured, tex)
    return out_icon, tex


# ==================================================================================================
# Output
# ==================================================================================================

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def build():
    sch = schemes()
    written = []
    rounds_dir = os.path.join(OUT, "worlditems/GunsOfTien/Rounds")
    boxes_dir = os.path.join(OUT, "worlditems/GunsOfTien/Boxes")
    for name, geometry, model_tex, icon_name, scheme in ROUNDS:
        icon, world = make_round(name, geometry, model_tex, icon_name, scheme, sch)
        written.append((save(icon, os.path.join(OUT, "item_%s.png" % name)), icon_name))
        written.append((save(world, os.path.join(rounds_dir, name + ".png")), model_tex + ".png"))
    for name, calibre, scheme, label in BOXES:
        if calibre in RIFLE_BOXES:
            icon, world = make_rifle_box(calibre, scheme, label, sch)
            src = RIFLE_BOXES[calibre]
        else:
            icon, world = make_handgun_box(calibre, scheme, label, sch)
            src = HANDGUN_BOXES[calibre]
        written.append((save(icon, os.path.join(OUT, "item_%s.png" % name)), src["icon"]))
        written.append((save(world.convert("RGB"), os.path.join(boxes_dir, name + ".png")), src["tex"] + ".png"))
    # 12 gauge birdshot: GoM tells buckshot and slug apart by hull / box colour only.
    shell = Image.open(os.path.join(GOM_TEX, "item_12Gauge_Shell_Red.png"))
    written.append((save(recolour_hue(shell, BIRDSHOT_HUE, is_red),
                         os.path.join(OUT, "item_12Gauge_Shell_Birdshot.png")), "item_12Gauge_Shell_Red.png"))
    shell_tex = Image.open(os.path.join(GOM_ROUNDS, "Shotgun_Shell_Red.png"))
    written.append((save(recolour_hue(shell_tex, BIRDSHOT_HUE, is_red),
                         os.path.join(rounds_dir, "12Gauge_Shell_Birdshot.png")), "Shotgun_Shell_Red.png"))
    box = Image.open(os.path.join(GOM_TEX, "item_12Gauge_Box_Buckshot.png"))
    written.append((save(recolour_hue(box, BIRDSHOT_HUE, is_green, 1.35),
                         os.path.join(OUT, "item_12Gauge_Box_Birdshot.png")), "item_12Gauge_Box_Buckshot.png"))
    box_tex = Image.open(os.path.join(GOM_BOXES, "12Gauge_Box_Buckshot.png"))
    written.append((save(recolour_hue(box_tex, BIRDSHOT_HUE, is_green, 1.35).convert("RGB"),
                         os.path.join(boxes_dir, "12Gauge_Box_Birdshot.png")), "12Gauge_Box_Buckshot.png"))
    return written


# ==================================================================================================
# Contact sheet
# ==================================================================================================

SHEET_ROWS = [
    ("7.62x39", "item_762x39_Round_Base.png", ["762x39_Round_US", "762x39_Round_SP", "762x39_Round_SteelCore"],
     "item_762x39_Box.png", ["762x39_Box_US", "762x39_Box_SP", "762x39_Box_SteelCore"]),
    ("9x19", "item_9x19_Round_Base.png", ["9x19_Round_SS", "9x19_Round_HP", "9x19_Round_PPP"],
     "item_9x19_Box.png", ["9x19_Box_SS", "9x19_Box_HP", "9x19_Box_PPP"]),
    (".45 ACP", "item_45_Round_Base.png", ["45_Round_HP", "45_Round_P"], "item_45_Box.png",
     ["45_Box_HP", "45_Box_P"]),
    ("9x39", "item_9x39_Round_Base.png", ["9x39_Round_SP6"], "item_9x39_Box.png", ["9x39_Box_SP6"]),
    ("12 gauge", "item_12Gauge_Shell_Red.png", ["12Gauge_Shell_Birdshot"], "item_12Gauge_Box_Buckshot.png",
     ["12Gauge_Box_Birdshot"]),
    (".30-06", "item_3006_Round_Base.png", ["3006_Round_SP"], "item_3006_Box.png", ["3006_Box_SP"]),
    (".308", "item_308_Round.png", ["308_Round_SP"], "item_308_Box.png", ["308_Box_SP"]),
]


def contact_sheet(path, scale=4):
    cell = 32 * scale
    pad, label_h = 10, 14
    cols = 1 + max(1 + len(r[2]) + 1 + len(r[4]) for r in SHEET_ROWS)
    width = pad + 90 + cols * (cell + pad)
    height = pad + len(SHEET_ROWS) * (cell + label_h + pad)
    sheet = Image.new("RGBA", (width, height), (78, 80, 88, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT, 12)

    def put(img, x, y, text, gom):
        big = img.convert("RGBA").resize((cell, cell), Image.NEAREST)
        bg = (62, 64, 72, 255) if gom else (96, 98, 108, 255)
        d.rectangle((x, y + label_h, x + cell - 1, y + label_h + cell - 1), fill=bg)
        sheet.alpha_composite(big, (x, y + label_h))
        d.text((x, y), text, font=font, fill=(255, 220, 120, 255) if gom else (255, 255, 255, 255))

    y = pad
    for title, base_round, rounds, base_box, boxes in SHEET_ROWS:
        d.text((pad, y + label_h + cell // 2 - 8), title, font=ImageFont.truetype(FONT, 16), fill=(255, 255, 255, 255))
        x = pad + 90
        put(Image.open(os.path.join(GOM_TEX, base_round)), x, y, "GoM " + base_round[5:-4], True)
        x += cell + pad
        for n in rounds:
            put(Image.open(os.path.join(OUT, "item_%s.png" % n)), x, y, n, False)
            x += cell + pad
        x += pad
        put(Image.open(os.path.join(GOM_TEX, base_box)), x, y, "GoM " + base_box[5:-4], True)
        x += cell + pad
        for n in boxes:
            put(Image.open(os.path.join(OUT, "item_%s.png" % n)), x, y, n, False)
            x += cell + pad
        y += cell + label_h + pad
    sheet.save(path)


def fit_all():
    jobs = [(icon, ROUNDS_FBX, geo, os.path.join(GOM_ROUNDS, tex + ".png"))
            for _, geo, tex, icon, _ in ROUNDS]
    jobs += [(c["icon"], BOX_FBX % "RifleAmmoBox", None, os.path.join(GOM_BOXES, c["tex"] + ".png"))
             for c in RIFLE_BOXES.values()]
    jobs += [(c["icon"], BOX_FBX % "HandGunAmmoBox", None, os.path.join(GOM_BOXES, c["tex"] + ".png"))
             for c in HANDGUN_BOXES.values()]
    done = set()
    for icon_name, fbx, geo, tex in jobs:
        if icon_name in done:
            continue
        done.add(icon_name)
        icon = Image.open(os.path.join(GOM_TEX, icon_name)).convert("RGBA")
        err, cam = fit_camera(icon, load_mesh(fbx, geo), Image.open(tex))
        print('    "%s": dict(yaw=%.1f, pitch=%.1f, roll=%.1f, bbox=%r),  # score %.1f'
              % (icon_name, cam["yaw"], cam["pitch"], cam["roll"], tuple(cam["bbox"]), err))


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit_all()
        sys.exit(0)
    for path, source in build():
        img = Image.open(path)
        print("%-60s %dx%d %s  <- %s" % (os.path.relpath(path, OUT), img.width, img.height, img.mode, source))
    if "--sheet" in sys.argv:
        contact_sheet(sys.argv[sys.argv.index("--sheet") + 1])
