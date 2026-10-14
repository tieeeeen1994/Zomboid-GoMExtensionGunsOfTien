#!/usr/bin/env python3
"""MP7A1 inventory icons, FBX check and the review sheet (Python 3 + Pillow).

    python3 scripts/post93/make_mp7_art.py [--fit] [--renders DIR]

Icons (32x32 RGBA, P/textures/item_GunsOfTienPost93_<name>.png) are rendered from the exported FBX files and
textures the way GoM's own icons look: for each icon family a camera is fitted to a GoM icon with the GoM mesh it
shows (make_art.py's method: orthographic yaw / pitch / roll, model fitted into the icon's alpha box, silhouette
plus colour score), and a simple light (texture x (ambient + diffuse x lambert), per channel) is fitted to that GoM
icon's pixels. Cameras and lights are stored in mp7_icon_cameras.json; --fit searches again (slow) and rewrites it.

    gun        item_MP5.png                 MP5 body + bolt + stock (deployed) + 30 magazine
    magazine   item_9x19Magazine30_MP5.png  9x19Magazine30_MP5
    suppressor item_MKI_Suppressor.png      MKI_Suppressor
    mount      item_Muzzle_Mount_Device.png Muzzle_Mount_Device

--renders DIR (the output of render_mp7.py) also writes docs/post93_mp7_preview.png.
"""

import json
import math
import os
import struct
import sys
import zlib

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import make_art as MA                      # noqa: E402  (FBX reader, rasteriser, camera conventions)

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MEDIA = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media")
TEX = os.path.join(MEDIA, "textures/weapons/GunsOfTienPost93")
ICONS = os.path.join(MEDIA, "textures")
PREVIEW = os.path.join(ROOT, "docs/post93_mp7_preview.png")
G = MA.GOM
POINTS = json.load(open(os.path.join(HERE, "mp7_points.json")))
FBX_GUN = os.path.join(MEDIA, "models_X/weapons/firearms/GunsOfTienPost93_MP7A1.fbx")
FBX_MAGS = os.path.join(MEDIA, "models_X/weapons/magazines/GunsOfTienPost93_MP7_magazines.fbx")
FBX_PARTS = os.path.join(MEDIA, "models_X/weapons/parts/GunsOfTienPost93_MP7_parts.fbx")
MP5_MAG_POINT = {"offset": [0.0, 0.1191, 0.0377], "rotate": [10.2946, 0.0, 0.0]}   # GoM smgs.txt, model MP5


# ==================================================================================================
# FBX meshes in game space (x, y, -raw z), not centred
# ==================================================================================================

_roots = {}


def _fbx_roots(path):
    if path not in _roots:
        with open(path, "rb") as fh:
            data = fh.read()
        version = struct.unpack_from("<I", data, 23)[0]
        off, roots = 27, []
        while off < len(data) - 160:
            node, off = MA._read_node(data, off, version)
            if node is None:
                break
            roots.append(node)
        _roots[path] = roots
    return _roots[path]


def load_game(path, geometry):
    """[(p0, p1, p2), (uv0, uv1, uv2)] in game coordinates."""
    roots = _fbx_roots(path)
    geo = next(g for g in MA._walk(roots, "Geometry") if g["props"][1].split(b"\x00")[0].decode() == geometry)
    child = lambda parent, nm: next(c for c in parent["children"] if c["name"] == nm)
    flat = child(geo, "Vertices")["props"][0]
    pvi = child(geo, "PolygonVertexIndex")["props"][0]
    layer = child(geo, "LayerElementUV")
    uvs = child(layer, "UV")["props"][0]
    direct = b"IndexToDirect" in child(layer, "ReferenceInformationType")["props"][0]
    uv_index = child(layer, "UVIndex")["props"][0] if direct else None
    verts = [(flat[i * 3], flat[i * 3 + 1], -flat[i * 3 + 2]) for i in range(len(flat) // 3)]

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
    return tris


def attach(tris, point):
    """The engine's attachment transform: translate(offset) . rotateXYZ(degrees)."""
    if not point:
        return tris
    ox, oy, oz = point["offset"]
    rx, ry, rz = [math.radians(a) for a in point.get("rotate", [0, 0, 0])]

    def tf(p):
        x, y, z = p
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        return x + ox, y + oy, z + oz

    return [([tf(p) for p in ps], uvs) for ps, uvs in tris]


def header_check(path):
    roots = _fbx_roots(path)
    objects = sorted({c["name"] for r in roots if r["name"] == "Objects" for c in r["children"]})
    unit = [c["props"][-1] for r in roots if r["name"] == "GlobalSettings" for c in MA._walk([r], "P")
            if c["props"][0] == b"UnitScaleFactor"]
    lcl = []
    for m in MA._walk(roots, "Model"):
        ps = {c["props"][0]: c["props"][4:] for c in MA._walk([m], "P")}
        lcl.append((m["props"][1].split(b"\x00")[0].decode(), [round(v, 4) for v in ps.get(b"Lcl Rotation", [0, 0, 0])],
                    [round(v, 4) for v in ps.get(b"Lcl Scaling", [1, 1, 1])]))
    return objects, unit, lcl


# ==================================================================================================
# Rendering: per sub-pixel (texture, uv, lambert normal), GoM's camera conventions (make_art._rotate)
# ==================================================================================================

def raster(objs, camera, size=32, ss=4):
    """objs: [(tris, texture index)]; returns a size*ss grid of None or (tex, u, v, nx, ny, nz)."""
    yaw, pitch, roll = camera["yaw"], camera["pitch"], camera.get("roll", 0.0)
    proj = []
    for tris, ti in objs:
        for ps, uvs in tris:
            proj.append(([MA._rotate(p, yaw, pitch, roll) for p in ps], uvs, ti))
    xs = [p[0] for ps, _, _ in proj for p in ps]
    ys = [p[1] for ps, _, _ in proj for p in ps]
    bx0, by0, bx1, by1 = camera["bbox"]
    scale = min((bx1 - bx0) / (max(xs) - min(xs)), (by1 - by0) / (max(ys) - min(ys))) * ss
    ox = bx0 * ss + ((bx1 - bx0) * ss - (max(xs) - min(xs)) * scale) / 2
    oy = by0 * ss + ((by1 - by0) * ss - (max(ys) - min(ys)) * scale) / 2
    side = size * ss
    grid = [[None] * side for _ in range(side)]
    depth = [[-1e30] * side for _ in range(side)]
    mnx, mny = min(xs), min(ys)
    for ps, uvs, ti in proj:
        a, b, c = ps
        n = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
             (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
             (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        ln = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        n = tuple(v / ln for v in n)
        if n[2] < 0:
            n = tuple(-v for v in n)

        def store(x, y, d, uv, ti=ti, n=n):
            if d > depth[y][x]:
                depth[y][x] = d
                grid[y][x] = (ti, uv[0], uv[1]) + n

        pts = [((p[0] - mnx) * scale + ox, (p[1] - mny) * scale + oy, p[2]) for p in ps]
        MA._fill_triangle(pts, uvs, side, side, store)
    return grid


def sample(tex, u, v):
    w, h = tex.size
    return tex.getpixel((min(w - 1, max(0, int(u % 1.0 * w))), min(h - 1, max(0, int((1 - v % 1.0) * h)))))


def pixel_terms(grid, texes, size, ss, light):
    """Per icon pixel: coverage, mean texel colour, mean texel colour x lambert."""
    lx, ly, lz = light
    out = [[None] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            t0, t1, n = [0.0] * 3, [0.0] * 3, 0
            for j in range(ss):
                for i in range(ss):
                    g = grid[y * ss + j][x * ss + i]
                    if g is None:
                        continue
                    c = sample(texes[g[0]], g[1], g[2])
                    lam = max(0.0, g[3] * lx + g[4] * ly + g[5] * lz)
                    for k in range(3):
                        t0[k] += c[k]
                        t1[k] += c[k] * lam
                    n += 1
            if n:
                out[y][x] = (n / (ss * ss), [v / n for v in t0], [v / n for v in t1])
    return out


def light_dirs():
    for az in range(0, 360, 30):
        for el in (10, 30, 50, 70, 89):
            a, e = math.radians(az), math.radians(el)
            yield (math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))


def fit_light(icon, grid, texes, ss=4):
    """Light direction and per-channel (ambient, diffuse) that best give the GoM icon from its texture."""
    src = icon.load()
    best = None
    for L in light_dirs():
        terms = pixel_terms(grid, texes, icon.width, ss, L)
        rows = [(src[x, y], terms[y][x]) for y in range(icon.height) for x in range(icon.width)
                if terms[y][x] is not None and src[x, y][3] > 200 and terms[y][x][0] > 0.99]
        coef, err = [], 0.0
        for k in range(3):
            s00 = sum(t[1][k] ** 2 for _, t in rows)
            s01 = sum(t[1][k] * t[2][k] for _, t in rows)
            s11 = sum(t[2][k] ** 2 for _, t in rows)
            r0 = sum(t[1][k] * c[k] for c, t in rows)
            r1 = sum(t[2][k] * c[k] for c, t in rows)
            det = s00 * s11 - s01 * s01 or 1e-9
            a = (r0 * s11 - r1 * s01) / det
            b = (r1 * s00 - r0 * s01) / det
            if b < 0:                                     # no negative light: ambient only
                a, b = r0 / (s00 or 1e-9), 0.0
            coef.append((a, b))
            err += sum(abs(c[k] - (a * t[1][k] + b * t[2][k])) for c, t in rows)
        err /= max(1, len(rows))
        if best is None or err < best[0]:
            best = (err, {"dir": [round(v, 4) for v in L], "coef": [[round(a, 4), round(b, 4)] for a, b in coef]})
    return best


def shade(objs, texes, camera, light, size=32, ss=4):
    grid = raster(objs, camera, size, ss)
    terms = pixel_terms(grid, texes, size, ss, light["dir"])
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = terms[y][x]
            if t is None:
                continue
            c = [MA.clamp8(light["coef"][k][0] * t[1][k] + light["coef"][k][1] * t[2][k]) for k in range(3)]
            px[x, y] = tuple(c) + (MA.clamp8(255 * t[0]),)
    return img


# ==================================================================================================
# Camera fitting (only with --fit)
# ==================================================================================================

def coverage_error(icon, objs, cam, ss):
    grid = raster(objs, cam, icon.width, ss)
    a = icon.getchannel("A").load()
    err = 0.0
    for y in range(icon.height):
        for x in range(icon.width):
            cover = sum(1 for j in range(ss) for i in range(ss) if grid[y * ss + j][x * ss + i] is not None)
            err += abs(cover / (ss * ss) - a[x, y] / 255.0)
    return err, grid


def colour_error(icon, grid, texes, ss):
    src = icon.load()
    pairs = []
    for y in range(icon.height):
        for x in range(icon.width):
            cs = [sample(texes[g[0]], g[1], g[2]) for j in range(ss) for i in range(ss)
                  for g in [grid[y * ss + j][x * ss + i]] if g is not None]
            if cs and src[x, y][3] > 200:
                pairs.append((src[x, y], [sum(c[k] for c in cs) / len(cs) for k in range(3)]))
    gains = []
    for k in range(3):
        den = sum(b[k] ** 2 for _, b in pairs) or 1.0
        gains.append(sum(a[k] * b[k] for a, b in pairs) / den)
    return sum(abs(a[k] - gains[k] * b[k]) for a, b in pairs for k in range(3)) / max(1, len(pairs))


def fit_camera(icon, objs, texes):
    bbox = MA.alpha_bbox(icon)

    def score(cam, ss=3):
        e, grid = coverage_error(icon, objs, cam, ss)
        return e + 0.3 * colour_error(icon, grid, texes, ss)

    cands = []
    for yaw in range(0, 360, 15):
        for pitch in range(-75, 90, 15):
            for roll in range(-90, 91, 15):
                cam = {"yaw": float(yaw), "pitch": float(pitch), "roll": float(roll), "bbox": bbox}
                cands.append((coverage_error(icon, objs, cam, 1)[0], cam))
    cands.sort(key=lambda c: c[0])
    best = None
    for _, cam in cands[:10]:
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
# Scenes
# ==================================================================================================

def img(path):
    return Image.open(path).convert("RGB")


def gom_scene(kind):
    """(GoM icon, objs, textures) the camera and light of `kind` are fitted on."""
    gom_tex = os.path.join(G, "textures/weapons")
    if kind == "gun":
        f = os.path.join(G, "models_X/weapons/firearms/MP5.fbx")
        mag = os.path.join(G, "models_X/weapons/magazines/smgs.fbx")
        objs = [(load_game(f, n), 0) for n in ("MP5_BODY", "MP5_BOLT", "MP5_STOCK")]
        objs.append((attach(load_game(mag, "9x19Magazine30_MP5"), MP5_MAG_POINT), 1))
        texes = [img(os.path.join(gom_tex, "firearms/smgs/MP5.png")),
                 img(os.path.join(gom_tex, "magazines/smgs/9x19Magazine30_MP5.png"))]
        icon = "item_MP5.png"
    elif kind == "magazine":
        objs = [(load_game(os.path.join(G, "models_X/weapons/magazines/smgs.fbx"), "9x19Magazine30_MP5"), 0)]
        texes = [img(os.path.join(gom_tex, "magazines/smgs/9x19Magazine30_MP5.png"))]
        icon = "item_9x19Magazine30_MP5.png"
    elif kind == "suppressor":
        objs = [(load_game(os.path.join(G, "models_X/weapons/parts/suppressors.fbx"), "MKI_Suppressor"), 0)]
        texes = [img(os.path.join(gom_tex, "parts/suppressors/MKI_Suppressor.png"))]
        icon = "item_MKI_Suppressor.png"
    else:
        objs = [(load_game(os.path.join(G, "models_X/weapons/parts/muzzles.fbx"), "Muzzle_Mount_Device"), 0)]
        texes = [img(os.path.join(gom_tex, "parts/muzzles/Muzzle_Mount_Device.png"))]
        icon = "item_Muzzle_Mount_Device.png"
    return Image.open(os.path.join(G, "textures", icon)).convert("RGBA"), objs, texes


def our_scenes():
    """{icon name: (kind, objs, textures)}"""
    gun_tex = img(os.path.join(TEX, "MP7A1.png"))
    out = {}
    mag30 = attach(load_game(FBX_MAGS, "46x30Magazine30_MP7"), POINTS["magazine"])
    out["MP7A1"] = ("gun", [(load_game(FBX_GUN, "MP7A1_BODY"), 0), (load_game(FBX_GUN, "MP7A1_BOLT"), 0),
                            (attach(load_game(FBX_GUN, "MP7A1_STOCK"), POINTS["stock_folded"]), 0), (mag30, 1)],
                    [gun_tex, img(os.path.join(TEX, "46x30Magazine30_MP7.png"))])
    for r in (20, 30, 40):
        n = "46x30Magazine%d_MP7" % r
        out[n] = ("magazine", [(load_game(FBX_MAGS, n), 0)], [img(os.path.join(TEX, n + ".png"))])
    for n, kind in (("MP7_Suppressor", "suppressor"), ("MP7_Muzzle_Mount_Device", "mount")):
        out[n] = (kind, [(load_game(FBX_PARTS, n), 0)], [img(os.path.join(TEX, n + ".png"))])
    return out


CAMERAS_JSON = os.path.join(HERE, "mp7_icon_cameras.json")


def fit_all():
    result = {}
    for kind in ("gun", "magazine", "suppressor", "mount"):
        icon, objs, texes = gom_scene(kind)
        err, cam = fit_camera(icon, objs, texes)
        grid = raster(objs, cam, icon.width, 4)
        lerr, light = fit_light(icon, grid, texes)
        print(kind, "camera error %.2f" % err, cam, "light error %.2f" % lerr, light)
        result[kind] = {"camera": cam, "light": light}
    with open(CAMERAS_JSON, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")


def make_icons():
    fitted = json.load(open(CAMERAS_JSON))
    made = {}
    for name, (kind, objs, texes) in our_scenes().items():
        cam = dict(fitted[kind]["camera"])
        icon = shade(objs, texes, cam, fitted[kind]["light"])
        path = os.path.join(ICONS, "item_GunsOfTienPost93_%s.png" % name)
        icon.save(path)
        made[name] = icon
    return made


# ==================================================================================================
# Checks and the review sheet
# ==================================================================================================

def bounds(tris):
    ps = [p for t, _ in tris for p in t]
    return [round(min(p[k] for p in ps), 4) for k in range(3)], [round(max(p[k] for p in ps), 4) for k in range(3)]


def check():
    lines = []
    for path, names in ((FBX_GUN, ("MP7A1_BODY", "MP7A1_BOLT", "MP7A1_STOCK")),
                        (FBX_MAGS, ("46x30Magazine20_MP7", "46x30Magazine30_MP7", "46x30Magazine40_MP7")),
                        (FBX_PARTS, ("MP7_Suppressor", "MP7_Muzzle_Mount_Device"))):
        objects, unit, lcl = header_check(path)
        lines.append("%s: objects %s, UnitScaleFactor %s" % (os.path.basename(path), objects, unit))
        for n, rot, scl in lcl:
            tris = load_game(path, n)
            mn, mx = bounds(tris)
            lines.append("  %-26s %5d tris  Lcl rot %s scl %s  game min %s max %s" % (n, len(tris), rot, scl, mn, mx))
    print("\n".join(lines))
    return lines


def font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def outline_panel(renders):
    """The model's left side at the reference photo's scale with the photo's traced outline (mp7_reference_outline.json)
    over it, and how much of the two silhouettes overlap (IoU)."""
    ref_json = json.load(open(os.path.join(HERE, "mp7_reference_outline.json")))
    cam = json.load(open(os.path.join(renders, "cameras.json")))["left_photo"]
    ren = Image.open(os.path.join(renders, "left_photo.png")).convert("RGBA")
    w, h = cam["size"]
    ppm = cam["px_per_mm"]
    cL, cH = cam["centre_mm"]

    def px(L, H):                                   # left side: muzzle on the right, L grows to the left
        return w / 2 - (L - cL) * ppm, h / 2 - (H - cH) * ppm

    ref = Image.new("L", (w, h), 0)
    rd = ImageDraw.Draw(ref)
    rd.polygon([px(*q) for q in ref_json["outline"]], fill=255)
    for hole in ref_json["holes"]:
        rd.polygon([px(*q) for q in hole], fill=0)
    model = ren.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    a, b = ref.load(), model.load()
    both = either = 0
    for y in range(h):
        for x in range(w):
            r, m = a[x, y] > 0, b[x, y] > 0
            both += r and m
            either += r or m
    page = Image.new("RGBA", (w, h), (250, 250, 248, 255))
    page.alpha_composite(ren)
    d = ImageDraw.Draw(page)
    for loop in [ref_json["outline"]] + ref_json["holes"]:
        pts = [px(*q) for q in loop]
        d.line(pts + [pts[0]], fill=(230, 30, 30, 255), width=3)
    L0, H0 = POINTS["_extras"]["photo_origin_mm"]
    ox, oy = px(L0, H0)
    d.line([(ox - 30, oy), (ox + 30, oy)], fill=(0, 120, 255, 255), width=2)
    d.line([(ox, oy - 30), (ox, oy + 30)], fill=(0, 120, 255, 255), width=2)
    for name, c in (("muzzle", (255, 160, 0)), ("canon", (255, 160, 0)), ("magazine", (0, 170, 80)),
                    ("scope", (170, 0, 200)), ("rail_left", (0, 120, 255))):
        o = POINTS[name]["offset"]
        x, y = px(L0 - o[1] / 0.00072, H0 + o[2] / 0.00072)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=c + (255,), width=3)
        d.text((x + 8, y - 22), name, fill=c + (255,), font=font(18))
    return page, both / max(1, either)


def sheet(renders, icons):
    W = 2480
    F, FS = font(26), font(18)
    page = Image.new("RGB", (W, 4000), (236, 236, 232))
    d = ImageDraw.Draw(page)

    def put(name, x, y, w=None, label=None, bg=(250, 250, 248)):
        im = Image.open(os.path.join(renders, name + ".png")).convert("RGBA")
        if w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        box = Image.new("RGBA", im.size, bg + (255,))
        box.alpha_composite(im)
        page.paste(box.convert("RGB"), (x, y))
        if label:
            d.text((x + 10, y + 8), label, fill=(40, 40, 40), font=FS)
        return im.size

    d.text((30, 20), "H&K MP7A1 for GoM Extension: Guns of Tien - Post-93 (Workbench renders of the exported FBX "
           "files + textures; parts placed at mp7_points.json)", fill=(20, 20, 20), font=F)
    y = 70
    put("q34_in", 20, y, 820, "3/4 front, stock collapsed, 30 rounds")
    put("side_in", 850, y, 820, "left side, stock collapsed, 30 rounds")
    put("right_in", 1680, y, 780, "right side (ejection port)")
    y += 560
    put("side_out", 20, y, 1200, "left side, stock deployed, 40 rounds")
    put("q34_out", 1240, y, 1220, "3/4, stock deployed, 40 rounds")
    y += 610
    put("side_supp", 20, y, 1200, "suppressor + muzzle mount device at 'canon', 20 rounds")
    put("q34_supp", 1240, y, 1220, "3/4 with suppressor")
    y += 610
    put("top_in", 20, y, 1200, "top")
    for i, r in enumerate((20, 30, 40)):
        put("mag%d_q34" % r, 1240 + i * 410, y, 400, "%d rounds" % r)
    y += 420
    put("parts_side", 20, y, 600, "MP7_Suppressor + MP7_Muzzle_Mount_Device (origin = mount face)")
    put("parts_q34", 640, y, 600)
    # overlay on GoM's MP5, same camera and scale
    a = Image.open(os.path.join(renders, "overlay_mp7.png")).convert("RGBA")
    b = Image.open(os.path.join(renders, "overlay_mp5.png")).convert("RGBA")
    ov = Image.new("RGBA", a.size, (250, 250, 248, 255))
    def red(alpha):
        return Image.merge("RGBA", (Image.new("L", a.size, 215), Image.new("L", a.size, 50),
                                    Image.new("L", a.size, 50), b.getchannel("A").point(lambda v: int(v * alpha))))

    ov.alpha_composite(red(0.45))       # MP5 behind,
    ov.alpha_composite(a)               # the MP7,
    ov.alpha_composite(red(0.28))       # and the MP5 again, faint, over it
    cam = json.load(open(os.path.join(renders, "cameras.json")))["overlay"]
    od = ImageDraw.Draw(ov)
    sw, sh = cam["size"]
    ppu = sw / cam["scale"]
    ox = sw / 2 + (0 - cam["centre"][0]) * ppu
    oy = sh / 2 - (0 - cam["centre"][1]) * ppu
    od.line([(ox - 30, oy), (ox + 30, oy)], fill=(0, 120, 255, 255), width=2)
    od.line([(ox, oy - 30), (ox, oy + 30)], fill=(0, 120, 255, 255), width=2)
    od.text((ox + 8, oy + 6), "origin", fill=(0, 90, 220, 255), font=FS)
    ov = ov.resize((1200, round(ov.height * 1200 / ov.width)), Image.LANCZOS)
    page.paste(ov.convert("RGB"), (1260, y))
    d.text((1270, y + 8), "left side over GoM's MP5 (red), same scale; blue = model origin (rear-top of grip)",
           fill=(40, 40, 40), font=FS)
    y += 620
    ov, iou = outline_panel(renders)
    ov = ov.resize((1700, round(ov.height * 1700 / ov.width)), Image.LANCZOS)
    page.paste(ov.convert("RGB"), (20, y + 60))
    d.text((30, y), "left side at the photo's scale (docs/mp7_2.png); red = its traced outline "
           "(mp7_reference_outline.json); silhouette overlap (IoU) %.1f%%" % (iou * 100), fill=(20, 20, 20), font=F)
    d.text((30, y + 32), "blue cross = model origin (rear-top of the grip); circles = attachment points",
           fill=(40, 40, 40), font=FS)
    print("silhouette IoU %.3f" % iou)
    y += 60 + ov.height + 20
    # icons: ours and GoM's references, native and x6
    d.text((30, y), "Icons (32x32, shown x6 and 1:1), next to the GoM icons whose camera and light they reuse",
           fill=(20, 20, 20), font=F)
    y += 40
    refs = ["item_MP5.png", "item_9x19Magazine30_MP5.png", "item_MKI_Suppressor.png", "item_Muzzle_Mount_Device.png"]
    row = [(Image.open(os.path.join(G, "textures", r)).convert("RGBA"), r[5:-4]) for r in refs]
    row += [(icons[n], n) for n in ("MP7A1", "46x30Magazine20_MP7", "46x30Magazine30_MP7", "46x30Magazine40_MP7",
                                     "MP7_Suppressor", "MP7_Muzzle_Mount_Device")]
    x = 20
    for im, label in row:
        bg = Image.new("RGBA", (192, 192), (150, 150, 150, 255))
        bg.alpha_composite(im.resize((192, 192), Image.NEAREST))
        page.paste(bg.convert("RGB"), (x, y))
        small = Image.new("RGBA", (32, 32), (150, 150, 150, 255))
        small.alpha_composite(im)
        page.paste(small.convert("RGB"), (x, y + 200))
        d.text((x + 40, y + 205), label[:24], fill=(40, 40, 40), font=FS)
        x += 244
    page.save(PREVIEW)
    print("wrote", PREVIEW)


def main():
    if "--fit" in sys.argv:
        fit_all()
    check()
    icons = make_icons()
    if "--renders" in sys.argv:
        sheet(sys.argv[sys.argv.index("--renders") + 1], icons)


if __name__ == "__main__":
    main()
