#!/usr/bin/env python3
"""Icons and world-model textures for the 4.6x30mm and 5.7x28mm ammunition of GoM Extension: Guns of Tien - Post-93.

Everything is derived from Guns of Marz's own PNGs and meshes (read only) with the helpers of ../make_art.py; nothing
is hand-edited and every run writes the same bytes.

Rounds. GoM ships the meshes (Rounds.fbx nodes 46x30_Round and 57x28_Round, textured H&K_Round_Base and
Nato_Round_Base by its own model scripts) but no icons, so the icons are rendered here:
  * The submesh is drawn with GoM's 5.56 icon camera (same 206-triangle mesh family, same UV layout), fitted to the
    whole 32x32 like every GoM round icon, with smooth normals.
  * Colour and shading are learned from GoM's item_556x45_Round_Base.png against Nato_Round_Base.png (the same
    texture the 5.7x28 uses): hue kept, saturation x the icon's ratio, value x a ratio looked up by screen-space
    normal; silhouette pixels get alpha = coverage and GoM's dark rim (colour x min(coverage, 0.75)).
  * World textures are GoM's texture with the bullet repainted (make_art's method: flat colour that keeps the
    texel's shading, along the bullet's own axis, f 0 = case mouth .. 1 = point; GoM's variants paint f >= 0.28).
    Icons are rendered from the variant's base texture, then painted the way make_art paints GoM-derived icons
    (GoM's own paints in their lighter icon shade; other paints lightened the same way).
Boxes. 50-round HandGunAmmoBox boxes built from GoM's 9x19_Box (red box, slate panel with the gold eagle, lid flap
sticker, tray of cartridge heads): the red takes the load's colour, the panel the calibre's (4.6x30 black, 5.7x28
light grey), the tray heads the calibre's case colour, the panel and side print say calibre and load, and the lid
sticker names the load in the load's light colour (make_art's label). Icons are GoM's item_9x19_Box.png with the
same recolours (by colour class, tray by position), the print changes carried over through GoM's fitted box camera
(transfer_print: new texels x the icon's own shading).

Usage:  python3 make_ammo_art.py               write every output
        python3 make_ammo_art.py --sheet [P]   also write the contact sheet (default docs/post93_ammo_art_sheet.png)
"""

import colorsys
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(HERE))
import make_art as A  # noqa: E402  (GoM paths, FBX reader, rasteriser, paint helpers)

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/textures")
SHEET = os.path.join(ROOT, "docs/post93_ammo_art_sheet.png")
PREFIX = "GunsOfTienPost93_"


# ==================================================================================================
# Round icon renderer
# ==================================================================================================

def _norm(v):
    length = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / length for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _sub(a, b):
    return tuple(a[k] - b[k] for k in range(3))


def _dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def smooth_normals(tris, crease=50.0):
    """Per-corner normals: area-weighted face normals of every face sharing the corner within `crease` degrees,
    turned outward by majority vote (the mesh is centred on its bounding box)."""
    faces = [_cross(_sub(ps[1], ps[0]), _sub(ps[2], ps[0])) for ps, _ in tris]
    vote = sum(1 if _dot(n, tuple(sum(p[k] for p in ps) / 3 for k in range(3))) > 0 else -1
               for (ps, _), n in zip(tris, faces))
    sign = 1 if vote >= 0 else -1
    faces = [tuple(sign * c for c in n) for n in faces]
    key = lambda p: tuple(round(c, 6) for c in p)
    users = {}
    for i, (ps, _) in enumerate(tris):
        for p in ps:
            users.setdefault(key(p), []).append(i)
    limit = math.cos(math.radians(crease))
    out = []
    for i, (ps, _) in enumerate(tris):
        own = _norm(faces[i])
        corners = []
        for p in ps:
            acc = [0.0, 0.0, 0.0]
            for j in users[key(p)]:
                if _dot(_norm(faces[j]), own) >= limit:
                    for k in range(3):
                        acc[k] += faces[j][k]
            corners.append(_norm(acc))
        out.append(corners)
    return out


def render_grid(tris, normals, camera, size=32, ss=4):
    """(u, v, nx, ny, nz) per sub-pixel, exactly the projection and fit of make_art.icon_uv_grid."""
    yaw, pitch, roll = camera["yaw"], camera["pitch"], camera.get("roll", 0.0)
    rot = lambda p: A._rotate(p, yaw, pitch, roll)
    proj = [[rot(p) for p in ps] for ps, _ in tris]
    xs = [p[0] for ps in proj for p in ps]
    ys = [p[1] for ps in proj for p in ps]
    bx0, by0, bx1, by1 = camera["bbox"]
    scale = min((bx1 - bx0) / (max(xs) - min(xs)), (by1 - by0) / (max(ys) - min(ys))) * ss
    ox = bx0 * ss + ((bx1 - bx0) * ss - (max(xs) - min(xs)) * scale) / 2
    oy = by0 * ss + ((by1 - by0) * ss - (max(ys) - min(ys)) * scale) / 2
    side = size * ss
    grid = [[None] * side for _ in range(side)]
    depth = [[-1e30] * side for _ in range(side)]

    def store(x, y, d, attrs):
        if d > depth[y][x]:
            depth[y][x] = d
            grid[y][x] = attrs

    for (ps, uvs), pp, ns in zip(tris, proj, normals):
        rn = [rot(n) for n in ns]
        pts = [((p[0] - min(xs)) * scale + ox, (p[1] - min(ys)) * scale + oy, p[2]) for p in pp]
        A._fill_triangle(pts, [tuple(uvs[i]) + tuple(rn[i]) for i in range(3)], side, side, store)
    return grid


def _texel(px, tw, th, uv):
    return px[min(tw - 1, max(0, int(uv[0] % 1.0 * tw))), min(th - 1, max(0, int((1 - uv[1] % 1.0) * th)))]


def pixel_data(grid, tex, size=32, ss=4):
    """Per icon pixel: (average texel colour, average normal, coverage) or None."""
    tex = tex.convert("RGB")
    tw, th = tex.size
    px = tex.load()
    out = [[None] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            subs = [grid[y * ss + j][x * ss + i] for j in range(ss) for i in range(ss)]
            subs = [s for s in subs if s is not None]
            if not subs:
                continue
            cols = [_texel(px, tw, th, s) for s in subs]
            colour = tuple(sum(c[k] for c in cols) / len(cols) for k in range(3))
            normal = _norm(tuple(sum(s[2 + k] for s in subs) for k in range(3)))
            out[y][x] = (colour, normal, len(subs) / float(ss * ss))
    return out


BINS = 10


def _bin(n):
    return (min(BINS - 1, int((n[0] + 1) / 2 * BINS)), min(BINS - 1, int((n[1] + 1) / 2 * BINS)))


def _hsv(c):
    return colorsys.rgb_to_hsv(*(v / 255.0 for v in c[:3]))


def _rgb(h, s, v):
    return tuple(A.clamp8(c * 255) for c in colorsys.hsv_to_rgb(h, max(0.0, min(1.0, s)), max(0.0, min(1.0, v))))


# GoM's 5.56 round: the reference for both new calibres (same mesh family and UV layout; 5.7x28 even shares the
# texture). Its camera is used for the new icons too.
REF_ICON = "item_556x45_Round_Base.png"
REF_GEOMETRY = "556x45_Round"
REF_TEXTURE = "Nato_Round_Base"
ROUND_CAMERA = A.CAMERAS[REF_ICON]

_model = None


def icon_model():
    """(saturation ratio, {normal bin: value ratio}) of GoM's round icon renders, learned from the 5.56 icon."""
    global _model
    if _model is None:
        tris = A.load_mesh(A.ROUNDS_FBX, REF_GEOMETRY)
        data = pixel_data(render_grid(tris, smooth_normals(tris), A.CAMERAS[REF_ICON]),
                          Image.open(os.path.join(A.GOM_ROUNDS, REF_TEXTURE + ".png")))
        icon = Image.open(os.path.join(A.GOM_TEX, REF_ICON)).convert("RGBA").load()
        sat, val = [], {}
        for y in range(32):
            for x in range(32):
                d = data[y][x]
                if d is None or d[2] < 0.99 or icon[x, y][3] < 250:
                    continue
                _, s1, v1 = _hsv(d[0])
                _, s2, v2 = _hsv(icon[x, y])
                if s1 > 0.2:
                    sat.append(s2 / s1)
                val.setdefault(_bin(d[1]), []).append((v2 + 0.02) / (v1 + 0.02))
        _model = (A._median(sat), {k: A._median(v) for k, v in sorted(val.items())})
    return _model


def _value_ratio(lut, n):
    b = _bin(n)
    if b not in lut:
        b = min(lut, key=lambda k: ((k[0] - b[0]) ** 2 + (k[1] - b[1]) ** 2, k))
    return lut[b]


def render_round_icon(geometry, tex, camera=ROUND_CAMERA, ss=4):
    sat, lut = icon_model()
    tris = A.load_mesh(A.ROUNDS_FBX, geometry)
    data = pixel_data(render_grid(tris, smooth_normals(tris), camera, 32, ss), tex, 32, ss)
    out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = out.load()
    for y in range(32):
        for x in range(32):
            d = data[y][x]
            if d is None:
                continue
            colour, normal, cover = d
            h, s, v = _hsv(colour)
            v = min(1.0, v * _value_ratio(lut, normal)) * (1.0 if cover >= 0.99 else min(cover, 0.75))
            px[x, y] = _rgb(h, s * sat, v) + (A.clamp8(cover * 255),)
    return out


# ==================================================================================================
# Round paint
# ==================================================================================================
# A paint layer is (f0, f1, colour, gamma); gamma < 1 flattens the texture's grain (a smooth polymer tip).

_gom = {}


def gom(variant):
    if variant not in _gom:
        _gom[variant] = A.gom_scheme(variant)
    return _gom[variant]


def copper():
    """GoM's copper jacket: the median bullet colour of Nato_Round_Base."""
    fractions = A.bullet_fractions(REF_GEOMETRY)
    px = Image.open(os.path.join(A.GOM_ROUNDS, REF_TEXTURE + ".png")).convert("RGBA").load()
    return A._median_colour([px[c] for c in fractions if px[c][3] > 200])


BLACK_TIP = (30, 30, 32)           # SS190 (the same black make_art uses for the SP-6 point)
VIOLET_TIP = (104, 38, 158)        # SB193: deeper than GoM's +P lilac, so the two purples stay apart
POLYMER_BLUE = (34, 84, 206)       # SS197SR: royal blue polymer tip, brighter than GoM's subsonic teal-blue


def icon_colour(colour):
    """GoM's four paints are mapped by make_art.icon_paint_colour; any other paint is lightened the way GoM's icons
    lighten theirs (value x1.2, saturation x0.85, read from those four)."""
    if tuple(colour) in {tuple(gom(v)["tip"]) for v in ("SS", "AP", "HP", "OP")}:
        return tuple(colour)
    h, s, v = _hsv(colour)
    return _rgb(h, s * 0.85, v * 1.2 + 0.03)


def paint_texture(tex, fractions, layers):
    out = tex.convert("RGBA").copy()
    px = out.load()
    ref = A._median([A.lum(px[c]) for c in fractions if px[c][3] > 200])
    for (x, y), f in sorted(fractions.items()):
        if px[x, y][3] == 0:
            continue
        for f0, f1, colour, gamma in layers:
            if f0 <= f <= f1:
                px[x, y] = A.paint(px[x, y], colour, ref, gamma)
                break
    return out


def round_specs():
    ss = gom("SS")["tip"]
    p = A.GOM_PAINT_FROM
    return [
        # name, geometry, GoM texture, layers on the base (world), layers painted on top of the base icon
        dict(name="46x30_Round_DM11", geometry="46x30_Round", texture="H&K_Round_Base",
             base=[(0.0, 1.0, copper(), 1.0)], paint=[],
             note="H&K_Round_Base with the bullet in GoM's copper (Nato_Round_Base jacket): copper-plated steel"),
        dict(name="46x30_Round_SS", geometry="46x30_Round", texture="H&K_Round_Base",
             base=[(0.0, 1.0, copper(), 1.0)], paint=[(p, 1.0, ss, 1.0)],
             note="DM11 + GoM's subsonic blue on f >= 0.28 (Nato_Round_SS paint)"),
        dict(name="57x28_Round_SS190", geometry="57x28_Round", texture="Nato_Round_Base",
             base=[], paint=[(p, 1.0, BLACK_TIP, 1.0)],
             note="Nato_Round_Base + black tip on f >= 0.28"),
        dict(name="57x28_Round_SB193", geometry="57x28_Round", texture="Nato_Round_Base",
             base=[], paint=[(p, 1.0, VIOLET_TIP, 1.0)],
             note="Nato_Round_Base + violet tip on f >= 0.28"),
        dict(name="57x28_Round_SS197SR", geometry="57x28_Round", texture="Nato_Round_Base",
             base=[], paint=[(0.62, 1.0, POLYMER_BLUE, 0.5)],
             note="Nato_Round_Base + short smooth blue polymer tip on f >= 0.62"),
    ]


def make_round(spec):
    fractions = A.bullet_fractions(spec["geometry"])
    gom_tex = Image.open(os.path.join(A.GOM_ROUNDS, spec["texture"] + ".png")).convert("RGBA")
    base = paint_texture(gom_tex, fractions, spec["base"]) if spec["base"] else gom_tex
    world = paint_texture(base, fractions, spec["paint"]) if spec["paint"] else base
    icon = render_round_icon(spec["geometry"], base)
    if spec["paint"]:
        icon = A.paint_round_icon(icon, spec["geometry"], ROUND_CAMERA, fractions,
                                  [(f0, f1, icon_colour(c)) for f0, f1, c, _ in spec["paint"]])
    return icon, world


# ==================================================================================================
# Boxes (GoM's 9x19 box template)
# ==================================================================================================

BOX_TEX = "9x19_Box"
BOX_ICON = "item_9x19_Box.png"
BOX_CAMERA = A.CAMERAS[BOX_ICON]

PANEL_RECT = (4, 26, 43, 90)        # slate panel with the eagle (incl. border)
PANEL_TEXT = (6, 65, 41, 88)        # "9x19mm / Parabellum" inside it
CALIBRE_LINE = (6, 65, 41, 79)     # GoM: big "9x19mm"
LOAD_LINE = (9, 79, 38, 87)         # GoM: small "Parabellum"
SIDE_TEXT = (50, 26, 59, 89)        # vertical "9x19mm Parabellum" on the long side
STICKER = (2, 3, 33, 17)            # "GUN AMMO" sticker on the lid flap (make_art's 9x19 label spot)
TRAY = (0, 92, 43, 127)             # cartridge heads


def _is_outer(c):
    h, s, v = A.hue_of(c)
    return (h < 20 or h > 335) and s > 0.3 and v > 0.1


def _is_outer_icon(c):
    return A.is_reddish(c)


def _is_panel(c):
    h, s, v = A.hue_of(c)
    return 195 < h < 245 and s > 0.12 and v > 0.3


def _is_panel_icon(c):
    h, s, v = A.hue_of(c)
    return 190 < h < 250 and s > 0.1 and v > 0.22


def _is_head(c):
    h, s, v = A.hue_of(c)
    return 25 < h < 75 and s > 0.15


def _inside(p, rect):
    return rect[0] <= p[0] <= rect[2] and rect[1] <= p[1] <= rect[3]


CALIBRES = {
    # panel colour and its ink (the 4.6x30 tray heads also take the H&K case colour, see make_box)
    "46x30": dict(text="4.6x30mm", panel=(46, 48, 52), ink=(232, 232, 226)),
    "57x28": dict(text="5.7x28mm", panel=(204, 206, 210), ink=(18, 18, 20)),
}


def case_colour(texture):
    """Median case colour of a GoM round texture (the case body below the bullet island)."""
    px = Image.open(os.path.join(A.GOM_ROUNDS, texture + ".png")).convert("RGBA").load()
    return A._median_colour([px[x, y] for y in range(40, 120) for x in range(10, 120) if px[x, y][3] > 200])


def box_specs():
    ss = gom("SS")
    red = (161, 67, 59)                           # GoM 9x19 box red, for the hue-swapped blues below
    return [
        # outer colour, sticker (band, text), panel load line, side text, sticker text
        dict(name="46x30_Box_DM11", calibre="46x30", outer=(112, 118, 52), band=(212, 216, 160),
             text=(62, 68, 18), load="DM11", sticker="STANDARD",
             note="olive (the H&K case lacquer)"),
        dict(name="46x30_Box_SS", calibre="46x30", outer=A.set_hue(red, A.hue_of(ss["tip"])[0]),
             band=ss["band"], text=ss["text"], load="SUBSONIC", sticker="SUBSONIC",
             note="GoM subsonic: red hue-swapped to the SS tip, sticker in Nato_Round_SS / 556x45_Box_SS colours"),
        dict(name="57x28_Box_SS190", calibre="57x28", outer=(52, 52, 56), band=(220, 220, 222),
             text=(20, 20, 22), load="SS190", sticker="STANDARD", note="black (the black tip)"),
        dict(name="57x28_Box_SB193", calibre="57x28", outer=A.set_hue(red, A.hue_of(VIOLET_TIP)[0]),
             band=(222, 204, 236), text=(76, 34, 112), load="SB193", sticker="SUBSONIC",
             note="violet (the violet tip)"),
        dict(name="57x28_Box_SS197SR", calibre="57x28", outer=A.set_hue(red, A.hue_of(POLYMER_BLUE)[0]),
             band=(178, 198, 242), text=(26, 52, 146), load="SS197SR", sticker="POLYMER TIP",
             note="royal blue (the polymer tip)"),
    ]


def _class_of(p, c):
    if _inside(p, TRAY) and _is_head(c):
        return "tray"
    if _inside(p, PANEL_RECT) and _is_panel(c):
        return "panel"
    if _is_outer(c):
        return "outer"
    return None


def _recolour(img, classes, targets, refs):
    out = img.copy()
    px = out.load()
    for p, k in classes.items():
        if k in targets:
            px[p] = A.paint(px[p], targets[k], refs[k])
    return out


def _texture_classes(img):
    px = img.load()
    return {(x, y): k for y in range(img.height) for x in range(img.width)
            for k in [_class_of((x, y), px[x, y])] if k is not None}


def _erase(img, rect, colour):
    ImageDraw.Draw(img).rectangle(rect, fill=tuple(colour) + (255,))


def _text(img, rect, text, ink, vertical):
    x0, y0, x1, y1 = rect
    img.alpha_composite(A.render_text(text, x1 - x0 + 1, y1 - y0 + 1, ink, vertical), (x0, y0))


def _ink_for(colour):
    return (238, 238, 232) if A.lum(colour) < 110 else (14, 14, 16)


def _icon_tray_weights():
    """Share of each icon pixel's sub-pixels that show the tray (the eagle is gold too, so position decides)."""
    grid = A.icon_uv_grid(A.load_mesh(A.BOX_FBX % "HandGunAmmoBox"), BOX_CAMERA, 32, 4)
    weights = {}
    for y in range(32):
        for x in range(32):
            n = 0
            for j in range(4):
                for i in range(4):
                    uv = grid[y * 4 + j][x * 4 + i]
                    if uv is not None and _inside((min(63, int(uv[0] % 1.0 * 64)),
                                                   min(127, int((1 - uv[1] % 1.0) * 128))), TRAY):
                        n += 1
            if n:
                weights[(x, y)] = n / 16.0
    return weights


def make_box(spec):
    cal = CALIBRES[spec["calibre"]]
    base = Image.open(os.path.join(A.GOM_BOXES, BOX_TEX + ".png")).convert("RGBA")
    classes = _texture_classes(base)
    bp = base.load()
    medians = {k: A._median_colour([bp[p] for p, c in classes.items() if c == k]) for k in ("outer", "panel", "tray")}
    refs = {k: A.lum(c) for k, c in medians.items()}
    targets = {"outer": spec["outer"], "panel": cal["panel"]}
    if spec["calibre"] == "46x30":
        # The tray shows brass heads (Pistol_Standard); give them the H&K case's olive: its hue and saturation,
        # and the tray's brightness scaled as the H&K case is to the brass one.
        hk, brass = _hsv(case_colour("H&K_Round_Base")), _hsv(case_colour("Pistol_Standard_Round_Base"))
        targets["tray"] = _rgb(hk[0], hk[1], _hsv(medians["tray"])[2] * hk[2] / brass[2])

    # A: GoM's print, recoloured (what the icon shows after the colour swaps). B: the new print.
    old = _recolour(base, classes, targets, refs)
    erased = base.copy()
    _erase(erased, PANEL_TEXT, medians["panel"])
    _erase(erased, SIDE_TEXT, medians["outer"])
    new = _recolour(erased, _texture_classes(erased), targets, refs)
    _text(new, CALIBRE_LINE, cal["text"], cal["ink"], False)
    _text(new, LOAD_LINE, spec["load"], cal["ink"], False)
    _text(new, SIDE_TEXT, "%s %s" % (cal["text"], spec["load"]), _ink_for(spec["outer"]), True)
    A.draw_label(new, STICKER, spec["sticker"], spec["band"], spec["text"], vertical=False)

    icon = Image.open(os.path.join(A.GOM_TEX, BOX_ICON)).convert("RGBA")
    out = icon.copy()
    src, dst = icon.load(), out.load()
    tray = _icon_tray_weights()
    for y in range(32):
        for x in range(32):
            c = src[x, y]
            if c[3] == 0:
                continue
            if _is_outer_icon(c):
                dst[x, y] = A.paint(c, targets["outer"], refs["outer"])
            elif _is_panel_icon(c):
                dst[x, y] = A.paint(c, targets["panel"], refs["panel"])
            elif "tray" in targets and (x, y) in tray and _is_head(c):
                w = tray[(x, y)]
                t = A.paint(c, targets["tray"], refs["tray"])
                dst[x, y] = tuple(A.clamp8(c[k] * (1 - w) + t[k] * w) for k in range(3)) + (c[3],)
    return transfer_print(out, old, new), new.convert("RGB")


def transfer_print(icon, old, new, ss=4):
    """Carry print changes (old -> new texture) into the icon. Unlike make_art.transfer_icon (additive), each
    changed pixel becomes the new texels' average x the icon's own shading there (its luminance over the old
    texels', kept within 15% so GoM's pixel noise does not speckle the new print), so light text on a dark panel stays as soft as GoM's dark text on its slate one."""
    grid = A.icon_uv_grid(A.load_mesh(A.BOX_FBX % "HandGunAmmoBox"), BOX_CAMERA, icon.width, ss)
    before = A._texel_average(grid, old.convert("RGB"), icon.width, ss)
    after = A._texel_average(grid, new.convert("RGB"), icon.width, ss)
    out = icon.copy()
    src, dst = icon.load(), out.load()
    for y in range(icon.height):
        for x in range(icon.width):
            c, o, n = src[x, y], before[y][x], after[y][x]
            if c[3] == 0 or o is None or max(abs(n[k] - o[k]) for k in range(3)) < 4:
                continue
            shade = max(0.85, min(1.15, (A.lum(c) + 8) / (A.lum(o) + 8)))
            w = o[3]
            dst[x, y] = tuple(A.clamp8(c[k] * (1 - w) + n[k] * shade * w) for k in range(3)) + (c[3],)
    return out


# ==================================================================================================
# Output and contact sheet
# ==================================================================================================

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def build():
    written = []
    for spec in round_specs():
        icon, world = make_round(spec)
        name = PREFIX + spec["name"]
        written.append((save(icon, os.path.join(OUT, "item_%s.png" % name)), "render of %s" % spec["geometry"]))
        written.append((save(world, os.path.join(OUT, "worlditems/GunsOfTienPost93/Rounds", name + ".png")),
                        spec["note"]))
    for spec in box_specs():
        icon, world = make_box(spec)
        name = PREFIX + spec["name"]
        written.append((save(icon, os.path.join(OUT, "item_%s.png" % name)), BOX_ICON))
        written.append((save(world, os.path.join(OUT, "worlditems/GunsOfTienPost93/Boxes", name + ".png")),
                        "%s.png, %s" % (BOX_TEX, spec["note"])))
    return written


def box_preview(tex, ss=8):
    """The box texture on HandGunAmmoBox through GoM's icon camera, flat (to read the print)."""
    grid = A.icon_uv_grid(A.load_mesh(A.BOX_FBX % "HandGunAmmoBox"), BOX_CAMERA, 32, ss)
    out = Image.new("RGBA", (32 * ss, 32 * ss), (0, 0, 0, 0))
    px, tp = out.load(), tex.convert("RGB").load()
    for y in range(32 * ss):
        for x in range(32 * ss):
            uv = grid[y][x]
            if uv is not None:
                px[x, y] = tp[min(63, int(uv[0] % 1.0 * 64)), min(127, int((1 - uv[1] % 1.0) * 128))] + (255,)
    return out


def contact_sheet(path, scale=4):
    cell = 32 * scale
    pad, label_h, left = 10, 16, 96
    font = ImageFont.truetype(A.FONT, 12)
    big = ImageFont.truetype(A.FONT, 16)
    gom_icon = lambda n: Image.open(os.path.join(A.GOM_TEX, n))
    ours = lambda n: Image.open(os.path.join(OUT, "item_%s%s.png" % (PREFIX, n)))
    rows = [
        ("GoM", [("9x19 Round", gom_icon("item_9x19_Round_Base.png"), True)]
         + [("556x45 %s" % v, gom_icon("item_556x45_Round_%s.png" % v), True) for v in ("Base", "SS", "AP", "HP", "OP")]
         + [("9x19 Box", gom_icon("item_9x19_Box.png"), True), ("556x45 Box", gom_icon("item_556x45_Box.png"), True),
            ("556x45 Box SS", gom_icon("item_556x45_Box_SS.png"), True)]),
        ("4.6x30", [(n, ours(n), False) for n in ("46x30_Round_DM11", "46x30_Round_SS")]
         + [(n, ours(n), False) for n in ("46x30_Box_DM11", "46x30_Box_SS")]),
        ("5.7x28", [(n, ours(n), False) for n in ("57x28_Round_SS190", "57x28_Round_SB193", "57x28_Round_SS197SR")]
         + [(n, ours(n), False) for n in ("57x28_Box_SS190", "57x28_Box_SB193", "57x28_Box_SS197SR")]),
    ]
    boxes = [s["name"] for s in box_specs()]
    rounds = [s["name"] for s in round_specs()]
    cols = max(len(r[1]) for r in rows)
    width = max(left + cols * (cell + pad), left + len(rounds) * (128 + pad), left + len(boxes) * (128 + 128 + pad))
    tex_rows_h = (128 + label_h + pad) + (256 + label_h + pad)
    height = pad + len(rows) * (cell + label_h + pad) + tex_rows_h + pad
    sheet = Image.new("RGBA", (width, height), (78, 80, 88, 255))
    d = ImageDraw.Draw(sheet)

    def put(img, x, y, w, h, text, gom_ref, resample=Image.NEAREST):
        d.rectangle((x, y + label_h, x + w - 1, y + label_h + h - 1),
                    fill=(62, 64, 72, 255) if gom_ref else (96, 98, 108, 255))
        sheet.alpha_composite(img.convert("RGBA").resize((w, h), resample), (x, y + label_h))
        d.text((x, y), text, font=font, fill=(255, 220, 120, 255) if gom_ref else (255, 255, 255, 255))

    y = pad
    for title, items in rows:
        d.text((pad, y + label_h + cell // 2 - 8), title, font=big, fill=(255, 255, 255, 255))
        x = left
        for text, img, gom_ref in items:
            put(img, x, y, cell, cell, text, gom_ref)
            x += cell + pad
        y += cell + label_h + pad
    d.text((pad, y + label_h + 56), "Round\ntextures", font=big, fill=(255, 255, 255, 255))
    x = left
    for n in rounds:
        put(Image.open(os.path.join(OUT, "worlditems/GunsOfTienPost93/Rounds", PREFIX + n + ".png")),
            x, y, 128, 128, n, False)
        x += 128 + pad
    y += 128 + label_h + pad
    d.text((pad, y + label_h + 120), "Box\ntextures\n(2x) and\non the\nmesh", font=big, fill=(255, 255, 255, 255))
    x = left
    for n in boxes:
        tex = Image.open(os.path.join(OUT, "worlditems/GunsOfTienPost93/Boxes", PREFIX + n + ".png"))
        put(tex, x, y, 128, 256, n, False)
        put(box_preview(tex, 4), x + 128, y + 64, 128, 128, "", False)
        x += 256 + pad
    sheet.save(path)


if __name__ == "__main__":
    for path, source in build():
        img = Image.open(path)
        print("%-72s %dx%d %s  <- %s" % (os.path.relpath(path, OUT), img.width, img.height, img.mode, source))
    if "--sheet" in sys.argv:
        i = sys.argv.index("--sheet")
        target = sys.argv[i + 1] if len(sys.argv) > i + 1 else SHEET
        contact_sheet(target)
        print("sheet", target)
