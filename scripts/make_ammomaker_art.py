#!/usr/bin/env python3
"""Icons and world-model textures for Guns of Tien's Ammo Maker parts, in Ammo Maker's own art.

Everything is derived from Ammo Maker's PNGs and box meshes (workshop 2788256295, read only); nothing is
hand-painted. Deterministic: run it again and every output is byte-identical.

How Ammo Maker marks its bullet variants, and what this script does the same way:
  * Bullets: AP / TR are the standard bullet with the nose painted (dark steel / red); HP is a blunter render.
    Soft point (SP) = the standard bullet with the point filed back to a rounded meplat and the nose (in front of
    the jacket's mouth) in dull lead grey, lighter and blunter than AP's dark pointed steel tip.
  * Rifle boxes: the variant code is printed small under the calibre letter ("HP", "AP", "TR" in the calibre
    cyan), the labels on both long sides say "RIFLE S HP 25", and AP / TR paint the tip of the bullet drawn on
    the lid. SP boxes start from the HP box: code "SP" printed in lead silver instead of cyan (its own colour,
    so the box tells apart from HP / AP at icon size), labels "RIFLE S SP", and the lid's bullet gets the soft
    point nose.
  * Birdshot: the Balls 00 pouch art (round lead balls with a dark rim) with many small pellets instead of three
    big balls: a triangular heap of 28 pellets on the icon, a hex cluster of 7 pellets on each of the 7 discs of
    the world model (Ammo Maker's Balls00 mesh, every disc shows the whole 16x16 texture). The box keeps Ammo
    Maker's buckshot box (magenta shot print) with the three balls replaced by a heap of 28 pellets, "00"
    replaced by shot size "8", and the labels "BALL 00" -> "BIRDSHOT".
  Lettering is Ammo Maker's own stencil glyphs cut from its box textures (B from BALL, R I S H P from RIFLE S HP,
  D from HANDGUN, O T from SHOTGUN); the small code S is its big calibre S scaled down; the big 8 is two of its
  big 0s stacked.

Box icons are renders of the box meshes: an orthographic camera fitted to each Ammo Maker icon (CAMERAS, found
with --fit through make_art.py's mesh reader and fitter) says which texel every icon pixel shows, and the
texture's changed pixels are repainted with the new texels, lit by the render's colour gain and the icon's own shading (box_icon).

Usage:  python3 make_ammomaker_art.py            write every output
        python3 make_ammomaker_art.py --fit      re-fit the box icon cameras and print them
        python3 make_ammomaker_art.py --sheet P  also write a contact sheet to P
"""

import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_art  # noqa: E402  (FBX reader, camera fit, icon transfer; not changed by this script)

AM = os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/2788256295/"
                        "mods/AmmoMaker")
AM_MEDIA = [os.path.join(AM, d, "media") for d in ("common", "42.20", "42", "")]
OUT = os.path.normpath(os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media/textures"))


def am_file(rel):
    for media in AM_MEDIA:
        path = os.path.join(media, rel)
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Ammo Maker file not found: " + rel)


def am_icon(name):
    return Image.open(am_file("textures/Item_ammomaker_%s.png" % name)).convert("RGBA")


def am_world(name):
    return Image.open(am_file("textures/WorldItems/ammomaker_%s.png" % name))


def am_mesh(name):
    return make_art.load_mesh(am_file("models_X/WorldItems/ammomaker_%s.fbx" % name))


# ==================================================================================================
# Colour helpers
# ==================================================================================================

lum = make_art.lum
clamp8 = make_art.clamp8


def mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def lead_of(c):
    """Copper jacket shade -> soft lead of the same shading: dull blue-grey, its range squeezed so that it
    reads lighter and flatter than Ammo Maker's dark AP steel."""
    v = 80 + (lum(c) - 60) * 0.58
    return (v - 5, v - 1, v + 6)


SILVER = (184, 188, 196)          # SP code on the box: lead silver where HP / AP / TR print the calibre colour
WHITE = (250, 250, 250)


# ==================================================================================================
# Pixel tools: inpainting, glyphs
# ==================================================================================================

def inpaint(img, mask, vertical=0.3):
    """Fill the pixels of `mask` (set of (x, y)) from their neighbours, ring by ring (onion peel). Rows weigh
    more than columns (`vertical`): the box art's bands and stripes run along x, so a hole takes its row's shade
    instead of smearing a stripe's glow into it. Runs of a row with known pixels at both ends are first filled
    by straight interpolation between them."""
    px = img.load()
    todo = set(mask)
    w, h = img.size
    for y in sorted({p[1] for p in todo}):
        xs = sorted(p[0] for p in todo if p[1] == y)
        runs, start = [], xs[0]
        for a, b in zip(xs, xs[1:] + [None]):
            if b != a + 1:
                runs.append((start, a))
                start = b
        for x0, x1 in runs:
            if x0 - 1 < 0 or x1 + 1 >= w:
                continue
            left, right = px[x0 - 1, y], px[x1 + 1, y]
            for x in range(x0, x1 + 1):
                t = (x - x0 + 1) / (x1 - x0 + 2)
                px[x, y] = tuple(clamp8(left[k] + (right[k] - left[k]) * t) for k in range(3)) + tuple(px[x, y][3:])
                todo.discard((x, y))
    while todo:
        ring = {}
        for x, y in todo:
            acc, n = [0.0, 0.0, 0.0], 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if (dx or dy) and 0 <= q[0] < w and 0 <= q[1] < h and q not in todo:
                        c = px[q]
                        weight = 1.0 if dy == 0 else (vertical if dx == 0 else vertical * 0.7)
                        for k in range(3):
                            acc[k] += c[k] * weight
                        n += weight
            if n:
                ring[(x, y)] = tuple(clamp8(acc[k] / n) for k in range(3))
        if not ring:
            break
        for p, c in ring.items():
            px[p] = c + tuple(px[p][3:])
            todo.discard(p)


def dilate(points, r=1, size=None):
    out = set()
    for x, y in points:
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                q = (x + dx, y + dy)
                if size is None or (0 <= q[0] < size[0] and 0 <= q[1] < size[1]):
                    out.add(q)
    return out


def _percentile(values, f):
    values = sorted(values)
    return values[min(len(values) - 1, int(f * len(values)))]


def white_glyph(img, box, bg_pad=10):
    """Alpha (list of rows of 0..1) of white stencil lettering in box (x0, y0, x1, y1 inclusive): the pixel's
    lift over its row's background (low percentile of the row around it) against full white."""
    img = img.convert("RGB")
    x0, y0, x1, y1 = box
    rows = []
    for y in range(y0, y1 + 1):
        around = [lum(img.getpixel((x, y))) for x in range(max(0, x0 - bg_pad), min(img.width, x1 + bg_pad + 1))]
        bg = _percentile(around, 0.15)
        rows.append([max(0.0, min(1.0, (lum(img.getpixel((x, y))) - bg - 6) / max(40.0, 238 - bg)))
                     for x in range(x0, x1 + 1)])
    return rows


def ink_glyph(img, box, channel):
    """Alpha of coloured print (cyan: B - R, magenta: R - G) in box, against its strongest pixel."""
    img = img.convert("RGB")
    x0, y0, x1, y1 = box

    def strength(c):
        return c[2] - c[0] if channel == "cyan" else c[0] - c[1]

    vals = [[strength(img.getpixel((x, y))) for x in range(x0, x1 + 1)] for y in range(y0, y1 + 1)]
    full = _percentile([v for row in vals for v in row], 0.97)
    return [[max(0.0, min(1.0, (v - 12) / max(1.0, full - 12))) for v in row] for row in vals]


def glyph_points(alpha, x, y, threshold=0.04):
    return {(x + i, y + j) for j, row in enumerate(alpha) for i, a in enumerate(row) if a > threshold}


def stamp(img, alpha, x, y, colour):
    px = img.load()
    for j, row in enumerate(alpha):
        for i, a in enumerate(row):
            if a > 0 and 0 <= x + i < img.width and 0 <= y + j < img.height:
                c = px[x + i, y + j]
                px[x + i, y + j] = tuple(clamp8(v) for v in mix(c, colour, a)) + tuple(c[3:])


def rot180(alpha):
    return [list(reversed(row)) for row in reversed(alpha)]


def alpha_image(alpha):
    h, w = len(alpha), len(alpha[0])
    im = Image.new("L", (w, h))
    im.putdata([clamp8(a * 255) for row in alpha for a in row])
    return im


def image_alpha(im):
    w, h = im.size
    data = list(im.tobytes())
    return [[data[j * w + i] / 255.0 for i in range(w)] for j in range(h)]


def scale_alpha(alpha, w, h):
    return image_alpha(alpha_image(alpha).resize((w, h), Image.LANCZOS))


def trim(alpha, threshold=0.05):
    """Crop away empty columns / rows at the edges."""
    cols = [i for i in range(len(alpha[0])) if any(row[i] > threshold for row in alpha)]
    rows = [j for j, row in enumerate(alpha) if any(a > threshold for a in row)]
    return [row[cols[0]:cols[-1] + 1] for row in alpha[rows[0]:rows[-1] + 1]]


def word(glyphs, gap=1):
    """Glyph alphas of equal height side by side."""
    h = max(len(g) for g in glyphs)
    rows = [[] for _ in range(h)]
    for n, g in enumerate(glyphs):
        for j in range(h):
            src = g[j] if j < len(g) else [0.0] * len(g[0])
            rows[j].extend(src + ([0.0] * gap if n < len(glyphs) - 1 else []))
    return rows


# ==================================================================================================
# Bullets: soft point nose
# ==================================================================================================

def _axis(points):
    """Weighted centroid and unit direction of the principal axis, pointing up (bullets point up / up-right)."""
    sw = sum(w for _, _, w in points)
    cx = sum(x * w for x, _, w in points) / sw
    cy = sum(y * w for _, y, w in points) / sw
    sxx = sum((x - cx) ** 2 * w for x, _, w in points)
    syy = sum((y - cy) ** 2 * w for _, y, w in points)
    sxy = sum((x - cx) * (y - cy) * w for x, y, w in points)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    dx, dy = math.cos(ang), math.sin(ang)
    if dy > 0 or (abs(dy) < 1e-9 and dx < 0):
        dx, dy = -dx, -dy
    return (cx, cy), (dx, dy)


def soft_point(img, weight, blunt, lead_len, round_k, background=None):
    """Repaint a bullet's nose as exposed lead and file its point back.

    weight[(x, y)] = how much of the pixel is bullet (icon: alpha; texture: copper mask). The point is cut
    `blunt` px back along the bullet's axis to a rounded meplat (t <= cut - round_k * d^2), the last
    `lead_len` px in front of that become lead, and a thin darker line marks the jacket's mouth. Icons lose the
    cut-off alpha; textures (background given: the same image with the bullet's cut tip inpainted) show the
    background there."""
    pts = [(x + 0.5, y + 0.5, w) for (x, y), w in weight.items() if w > 0.25]
    (cx, cy), (dx, dy) = _axis(pts)
    nx, ny = -dy, dx
    t_tip = max((x - cx) * dx + (y - cy) * dy for x, y, w in pts if w > 0.5) + 0.5
    cut = t_tip - blunt
    mouth = cut - lead_len
    px = img.load()
    bg = background.load() if background is not None else None
    ss = 4
    for (x, y), w in weight.items():
        if w <= 0:
            continue
        kept = lead = edge = 0
        for j in range(ss):
            for i in range(ss):
                sx, sy = x + (i + 0.5) / ss, y + (j + 0.5) / ss
                t = (sx - cx) * dx + (sy - cy) * dy
                d = (sx - cx) * nx + (sy - cy) * ny
                if t <= cut - round_k * d * d:
                    kept += 1
                    if t > mouth:
                        lead += 1
                    elif t > mouth - 0.8:
                        edge += 1
        n = ss * ss
        if kept == n and lead == 0 and edge == 0:
            continue
        c = px[x, y]
        col = c[:3]
        if lead:
            col = mix(col, lead_of(col), lead / kept)
        if edge:
            col = tuple(v * (1 - 0.22 * edge / kept) for v in col)
        cover = kept / n
        if 0 < cover < 1:
            col = tuple(v * 0.88 for v in col)             # the new rim of the meplat, like the outline
        if bg is None:
            px[x, y] = tuple(clamp8(v) for v in col) + (clamp8(c[3] * cover),)
        else:
            a = w * cover
            base = bg[x, y]
            px[x, y] = tuple(clamp8(base[k] + (col[k] - base[k]) * (a if a < 1 else 1) / max(w, 1e-6) * min(1, w))
                             for k in range(3)) + tuple(c[3:])
    return img


def icon_weight(icon):
    a = icon.getchannel("A").load()
    return {(x, y): a[x, y] / 255.0 for y in range(icon.height) for x in range(icon.width) if a[x, y]}


def copper_weight(img, box):
    """Soft mask of the copper bullet drawn in box (x0, y0, x1, y1 incl.), holes (highlights) closed."""
    rgb = img.convert("RGB")
    m = Image.new("L", img.size, 0)
    mp = m.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            r, g, b = rgb.getpixel((x, y))
            mp[x, y] = clamp8(max(0.0, min(1.0, ((r - b) - 22) / 48.0)) * 255)
    closed = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    m = ImageChops.lighter(m, closed)
    mp = m.load()
    return {(x, y): mp[x, y] / 255.0 for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if mp[x, y] > 8}


def soft_point_texture(tex, box, blunt, lead_len, round_k):
    """soft_point() on the bullet drawn on a box texture: the filed-off tip shows the lid behind it."""
    tex = tex.convert("RGB")
    weight = copper_weight(tex, box)
    pts = [(x + 0.5, y + 0.5, w) for (x, y), w in weight.items() if w > 0.25]
    (cx, cy), (dx, dy) = _axis(pts)
    t_tip = max((x - cx) * dx + (y - cy) * dy for x, y, w in pts if w > 0.5) + 0.5
    cut = t_tip - blunt
    gone = {p for p in weight if (p[0] + 0.5 - cx) * dx + (p[1] + 0.5 - cy) * dy > cut - 1.5}
    background = tex.copy()
    inpaint(background, dilate(gone, 1, tex.size))
    return soft_point(tex, weight, blunt, lead_len, round_k, background)


# Item icons: (blunt, lead length, rounding) in icon pixels; the M bullet is ~1.4x the S one.
BULLET_ICONS = {
    "GunsOfTien_BulletRifleSSP": ("BulletRifleS", 3.0, 7.5, 0.30),
    "GunsOfTien_BulletRifleMSP": ("BulletRifleM", 4.0, 10.0, 0.20),
}


def make_bullet_icon(name):
    src, blunt, lead_len, k = BULLET_ICONS[name]
    icon = am_icon(src)
    return soft_point(icon, icon_weight(icon), blunt, lead_len, k)


# ==================================================================================================
# Birdshot: pellets from Ammo Maker's own ball
# ==================================================================================================

def ball_sprite(img, centre, radius):
    """A ball cut out of Ammo Maker art as an RGBA sprite with a round, anti-aliased edge."""
    cx, cy = centre
    size = int(math.ceil(radius * 2)) + 2
    x0, y0 = int(round(cx - size / 2)), int(round(cy - size / 2))
    src = img.convert("RGBA").crop((x0, y0, x0 + size, y0 + size))
    mask = Image.new("L", (size * 4, size * 4), 0)
    ox, oy = (cx - x0) * 4, (cy - y0) * 4
    ImageDraw.Draw(mask).ellipse((ox - radius * 4, oy - radius * 4, ox + radius * 4, oy + radius * 4), fill=255)
    mask = mask.resize((size, size), Image.BOX)
    src.putalpha(ImageChops.multiply(src.getchannel("A"), mask))
    return src


def pellet_heap(sprite, rows, pitch, seed, squash=0.87, jitter=0.12):
    """Hex-packed triangle of pellets (1 at the top, `rows` at the bottom) drawn back to front, at the
    sprite's own scale. Returns the RGBA layer."""
    rnd = random.Random(seed)
    d = sprite.width
    width = int((rows - 1) * pitch + d + 4)
    height = int((rows - 1) * pitch * squash + d + 4)
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow = Image.new("L", layer.size, 0)
    spots = []
    for r in range(rows):
        for i in range(r + 1):
            x = (width - d) / 2 + (i - r / 2) * pitch + rnd.uniform(-jitter, jitter) * pitch
            y = 2 + r * pitch * squash + rnd.uniform(-jitter, jitter) * pitch
            spots.append((y, x))
    sd = ImageDraw.Draw(shadow)
    for y, x in spots:                         # the heap's own shade in the gaps between pellets
        sd.ellipse((x - d * 0.1, y - d * 0.05, x + d * 1.1, y + d * 1.15), fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(d * 0.12))
    layer = Image.composite(Image.new("RGBA", layer.size, (34, 32, 30, 255)), layer, shadow)
    layer.putalpha(shadow)
    for y, x in sorted(spots):
        layer.alpha_composite(sprite, (int(round(x)), int(round(y))))
    return layer


def make_birdshot_icon():
    """Balls 00's icon is three 24 px balls in a triangle; birdshot is a 28-pellet triangle in the same place."""
    src = am_icon("Balls00")
    sprite = ball_sprite(src, (32.0, 18.6), 12.4)          # the top ball, at 4x the pellet size
    heap = pellet_heap(sprite, 7, sprite.width * 0.98, seed=8)
    scale = 7.3 / sprite.width
    heap = heap.resize((round(heap.width * scale), round(heap.height * scale)), Image.LANCZOS)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    bbox = src.getbbox()
    cx = (bbox[0] + bbox[2]) / 2
    out.alpha_composite(heap, (int(round(cx - heap.width / 2)), int(round((bbox[1] + bbox[3]) / 2 - heap.height / 2))))
    return out


def make_birdshot_world():
    """Balls00's model is 7 flat discs each showing the whole 16x16 ball; birdshot shows 7 pellets per disc."""
    src = am_world("Balls00").convert("RGBA")
    big = src.resize((96, 96), Image.BICUBIC)
    sprite = ball_sprite(big, (48, 48), 47)
    sprite = sprite.resize((34, 34), Image.LANCZOS)
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    rim = src.getpixel((1, 8))[:3]
    ImageDraw.Draw(canvas).ellipse((6, 6, 122, 122), fill=tuple(int(v * 0.7) for v in rim) + (255,))
    canvas = canvas.filter(ImageFilter.GaussianBlur(3))
    centres = [(64, 64)] + [(64 + 37 * math.cos(math.radians(a)), 64 + 37 * math.sin(math.radians(a)))
                             for a in range(-90, 270, 60)]
    for x, y in sorted(centres, key=lambda p: p[1]):
        canvas.alpha_composite(sprite, (int(round(x - 17)), int(round(y - 17))))
    out = Image.new("RGBA", canvas.size, rim + (255,))
    out.alpha_composite(canvas)
    return out.resize((16, 16), Image.LANCZOS).convert(src.mode)


# ==================================================================================================
# Boxes
# ==================================================================================================

def _letters():
    """Ammo Maker's label lettering (7 px tall white stencil), cut from its box textures."""
    rifle = am_world("BoxBulletsRifleSHP")
    hand = am_world("BoxBulletsHandgunS")
    hull = am_world("BoxHullsShotgunS")
    balls = am_world("BoxBalls00")
    cut = lambda img, x0, x1, y0: trim(white_glyph(img, (x0, y0, x1, y0 + 6)))
    return {
        "B": cut(balls, 2, 8, 69),
        "R": cut(rifle, 3, 8, 74),
        "I": cut(rifle, 10, 12, 74),
        "S": cut(rifle, 32, 37, 74),
        "H": cut(rifle, 41, 47, 74),
        "D": cut(hand, 22, 28, 70),
        "O": cut(hull, 15, 21, 77),
        "T": cut(hull, 22, 27, 77),
    }


# Rifle boxes, from the HP box of the calibre. Rects are inclusive (x0, y0, x1, y1); a glyph source is
# (Ammo Maker texture, rect). The M label has no S of its own: it borrows the S box's, same lettering.
RIFLE_BOXES = {
    "GunsOfTien_BoxBulletsRifleSSP": dict(
        src="BoxBulletsRifleSHP", icon="BoxBulletsRifleSHP", mesh="BoxBulletsRifleS",
        front_s=("BoxBulletsRifleSHP", (32, 74, 37, 80)), front_h=(41, 74, 47, 80),   # "RIFLE S HP 25"
        back_s=("BoxBulletsRifleSHP", (41, 11, 47, 18)), back_h=(32, 11, 38, 18),    # upside down, far side
        big_s=("BoxBulletsRifleS", (60, 28, 78, 49)), code=(56, 51, 76, 61),          # calibre S, code "HP"
        bullet=(0, 17, 58, 68), bullet_fit=(3.0, 8.0, 0.18)),
    "GunsOfTien_BoxBulletsRifleMSP": dict(
        src="BoxBulletsRifleMHP", icon="BoxBulletsRifleMHP", mesh="BoxBulletsRifleM",
        front_s=("BoxBulletsRifleS", (32, 74, 37, 80)), front_h=(40, 75, 46, 81),    # "RIFLE M HP 25"
        back_s=("BoxBulletsRifleSHP", (41, 11, 47, 18)), back_h=(26, 10, 32, 17),
        big_s=("BoxBulletsRifleS", (60, 28, 78, 49)), code=(49, 52, 69, 62),
        bullet=(0, 17, 58, 70), bullet_fit=(3.0, 8.0, 0.18)),
}


def make_rifle_box_texture(name):
    cfg = RIFLE_BOXES[name]
    tex = am_world(cfg["src"]).convert("RGB")
    for s_key, h_key in (("front_s", "front_h"), ("back_s", "back_h")):
        (s_src, s_box), h_box = cfg[s_key], cfg[h_key]
        s_alpha = white_glyph(am_world(s_src), s_box)
        h_alpha = white_glyph(tex, h_box)
        inpaint(tex, dilate(glyph_points(h_alpha, h_box[0], h_box[1], 0.08), 1, tex.size))
        x = h_box[0] + (h_box[2] - h_box[0] - (s_box[2] - s_box[0])) // 2
        stamp(tex, s_alpha, x, h_box[1], WHITE)
    # Code "HP" -> "SP" in lead silver: keep the P, make the S from the big calibre S scaled down.
    big_src, big_box = cfg["big_s"]
    big = trim(ink_glyph(am_world(big_src), big_box, "cyan"))
    code = ink_glyph(tex, cfg["code"], "cyan")
    x0, y0 = cfg["code"][:2]
    pts = glyph_points(code, x0, y0, 0.06)
    cols = sorted({p[0] for p in pts})
    rows = sorted({p[1] for p in pts})
    height = rows[-1] - rows[0] + 1
    gaps = [c for c in range(cols[0], cols[-1]) if c not in cols]
    split = gaps[len(gaps) // 2] if gaps else (cols[0] + cols[-1]) // 2
    p_alpha = [row[split - x0:] for row in code]
    s_small = scale_alpha(big, max(3, round(len(big[0]) * height / len(big))), height)
    inpaint(tex, dilate(pts, 1, tex.size))
    stamp(tex, s_small, cols[0] + (split - cols[0] - len(s_small[0])) // 2, rows[0], SILVER)
    stamp(tex, p_alpha, split, y0, SILVER)
    blunt, lead_len, k = cfg["bullet_fit"]
    return soft_point_texture(tex, cfg["bullet"], blunt, lead_len, k)


BALLS_BOX = dict(
    balls=[(31.3, 29.6), (18.2, 51.9), (44.7, 51.9)], ball_r=12.2,   # the three 00 balls on the lid
    zeros=[(59, 31, 74, 51), (77, 31, 92, 51)],                      # the big magenta "00"
    front_label=(2, 68, 42, 76), front_at=(3, 69),                   # "BALL 00" on the near side
    back_label=(55, 5, 95, 13), back_end=(93, 6),                    # the same upside down on the far side
)


def make_birdshot_box_texture():
    cfg = BALLS_BOX
    tex = am_world("BoxBalls00").convert("RGB")
    orig = tex.copy()
    # Lid picture: three balls -> a heap of small pellets cut from the same art.
    sprite = ball_sprite(orig, cfg["balls"][0], cfg["ball_r"] - 1.0)
    gone = set()
    for cx, cy in cfg["balls"]:
        r = cfg["ball_r"]
        gone |= {(x, y) for y in range(int(cy - r - 1), int(cy + r + 2)) for x in range(int(cx - r - 1), int(cx + r + 2))
                 if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r and 0 <= x < 128 and 0 <= y < 128}
    inpaint(tex, gone)
    heap = pellet_heap(sprite, 7, sprite.width * 0.98, seed=36)
    scale = 6.2 / sprite.width
    heap = heap.resize((round(heap.width * scale), round(heap.height * scale)), Image.LANCZOS)
    xs = [c[0] for c in cfg["balls"]]
    ys = [c[1] for c in cfg["balls"]]
    hx = (min(xs) + max(xs)) / 2 - heap.width / 2
    hy = (min(ys) - cfg["ball_r"] + max(ys) + cfg["ball_r"]) / 2 - heap.height / 2
    lid = tex.convert("RGBA")
    lid.alpha_composite(heap, (int(round(hx)), int(round(hy))))
    tex = lid.convert("RGB")
    # Shot size "00" -> "8": two of Ammo Maker's big stencil 0s stacked (top one smaller, as in the type).
    zero = trim(ink_glyph(orig, cfg["zeros"][0], "magenta"))
    pts = set()
    for box in cfg["zeros"]:
        pts |= glyph_points(ink_glyph(orig, box, "magenta"), box[0], box[1], 0.05)
    magenta = _ink_colour(orig, pts)
    inpaint(tex, dilate(pts, 1, tex.size))
    w, h = len(zero[0]), len(zero)
    top = scale_alpha(zero, round(w * 0.84), round(h * 0.48))
    bottom = scale_alpha(zero, w, round(h * 0.56))
    eight_h = len(top) + len(bottom) - 1
    x_mid = (cfg["zeros"][0][0] + cfg["zeros"][1][2] + 1) / 2
    y0 = cfg["zeros"][0][1] + (h - eight_h) // 2
    stamp(tex, top, int(round(x_mid - len(top[0]) / 2)), y0, magenta)
    stamp(tex, bottom, int(round(x_mid - w / 2)), y0 + len(top) - 1, magenta)
    # Labels "BALL 00" -> "BIRDSHOT" on both long sides.
    letters = _letters()
    text = word([letters[ch] for ch in "BIRDSHOT"], gap=0)   # 1 px gaps would run into "2500"
    for rect, flip in ((cfg["front_label"], False), (cfg["back_label"], True)):
        x0, y0r, x1, y1 = rect
        old = white_glyph(orig, rect)
        inpaint(tex, dilate(glyph_points(old, x0, y0r, 0.08), 1, tex.size))
    stamp(tex, text, cfg["front_at"][0], cfg["front_at"][1], WHITE)
    back = rot180(text)
    stamp(tex, back, cfg["back_end"][0] - len(back[0]) + 1, cfg["back_end"][1], WHITE)
    return tex


def _ink_colour(img, pts):
    """The print's full colour: median of its strongest pixels."""
    px = img.convert("RGB").load()
    cols = sorted((px[p] for p in pts), key=lambda c: -(c[0] - c[1] + c[2] - c[1]))
    best = cols[:max(1, len(cols) // 4)]
    return tuple(sorted(c[k] for c in best)[len(best) // 2] for k in range(3))


# ==================================================================================================
# Box icons: the texture's change carried onto Ammo Maker's render of the box
# ==================================================================================================

# Ammo Maker icon -> mesh view, found with --fit (yaw, pitch, roll in degrees; bbox = icon pixels it fills).
CAMERAS = {
    "BoxBulletsRifleSHP": dict(yaw=315.5, pitch=28.5, roll=0.0, bbox=(6, 15, 58, 50)),     # fitted on ...RifleS
    "BoxBulletsRifleMHP": dict(yaw=313.5, pitch=30.0, roll=1.0, bbox=(5, 12, 60, 53)),     # fitted on ...RifleM
    "BoxBalls00": dict(yaw=314.0, pitch=32.0, roll=-0.5, bbox=(3, 14, 62, 50)),
}


def box_icon(icon_name, mesh_name, old_tex, new_tex, ss=4):
    """Repaint the icon pixels whose texels changed with the new texture seen through the fitted camera, lit
    like the icon: one colour gain for the whole render (least squares over the box) times the pixel's own
    shading (icon brightness over the old texture's). Unlike make_art.transfer_icon's added difference, a
    strong colour swap (cyan -> silver, magenta print -> lid) leaves no tint of the old colour behind."""
    icon = am_icon(icon_name)
    grid = make_art.icon_uv_grid(am_mesh(mesh_name), CAMERAS[icon_name], icon.width, ss)
    old = make_art._texel_average(grid, old_tex.convert("RGB"), icon.width, ss)
    new = make_art._texel_average(grid, new_tex.convert("RGB"), icon.width, ss)
    src = icon.load()
    pairs = [(src[x, y], old[y][x]) for y in range(icon.height) for x in range(icon.width)
             if old[y][x] is not None and old[y][x][3] == 1.0 and src[x, y][3] > 200]
    gain = [sum(a[k] * b[k] for a, b in pairs) / max(1.0, sum(b[k] * b[k] for _, b in pairs)) for k in range(3)]
    out = icon.copy()
    dst = out.load()
    w_, h_ = icon.size

    def shade_at(x, y):
        """Icon brightness over the lit old texels, over 3x3 pixels: the fitted camera can be a pixel off,
        and a lone pixel's ratio would then light new print like the old print's neighbour."""
        a = b = 0.0
        for j in (-1, 0, 1):
            for i in (-1, 0, 1):
                xx, yy = x + i, y + j
                if 0 <= xx < w_ and 0 <= yy < h_ and old[yy][xx] is not None and src[xx, yy][3] > 0:
                    a += lum(src[xx, yy]) + 8
                    b += lum([gain[k] * old[yy][xx][k] for k in range(3)]) + 8
        return max(0.55, min(1.3, a / b)) if b else 1.0

    for y in range(icon.height):
        for x in range(icon.width):
            c, o, n = src[x, y], old[y][x], new[y][x]
            if o is None or c[3] == 0:
                continue
            diff = max(abs(n[k] - o[k]) for k in range(3))
            if diff < 3:
                continue
            shade = shade_at(x, y)
            replaced = [shade * gain[k] * n[k] for k in range(3)]
            added = [c[k] + shade * gain[k] * (n[k] - o[k]) for k in range(3)]
            w = min(1.0, diff / 20.0) * o[3]
            dst[x, y] = tuple(clamp8(added[k] + (replaced[k] - added[k]) * w) for k in range(3)) + (c[3],)
    return out


# ==================================================================================================
# Build
# ==================================================================================================

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=False)
    return path


def build():
    """Write every output; returns [(path, made from)]."""
    done = []
    icon = lambda n: os.path.join(OUT, "Item_%s.png" % n)
    world = lambda n: os.path.join(OUT, "WorldItems", "%s.png" % n)
    for name, (src, _, _, _) in BULLET_ICONS.items():
        done.append((save(make_bullet_icon(name), icon(name)), "Item_ammomaker_%s.png" % src))
    done.append((save(make_birdshot_icon(), icon("GunsOfTien_Birdshot")), "Item_ammomaker_Balls00.png"))
    done.append((save(make_birdshot_world(), world("GunsOfTien_Birdshot")), "WorldItems/ammomaker_Balls00.png"))
    for name, cfg in RIFLE_BOXES.items():
        tex = make_rifle_box_texture(name)
        done.append((save(tex, world(name)), "WorldItems/ammomaker_%s.png" % cfg["src"]))
        done.append((save(box_icon(cfg["icon"], cfg["mesh"], am_world(cfg["src"]), tex), icon(name)),
                     "Item_ammomaker_%s.png" % cfg["icon"]))
    tex = make_birdshot_box_texture()
    done.append((save(tex, world("GunsOfTien_BoxBirdshot")), "WorldItems/ammomaker_BoxBalls00.png"))
    done.append((save(box_icon("BoxBalls00", "BoxBalls00", am_world("BoxBalls00"), tex),
                      icon("GunsOfTien_BoxBirdshot")), "Item_ammomaker_BoxBalls00.png"))
    return done


# ==================================================================================================
# Contact sheet: Ammo Maker's art next to the new art
# ==================================================================================================

def _am(name):
    return lambda: am_icon(name)


def _new(name, world=False):
    return lambda: Image.open(os.path.join(OUT, "WorldItems" if world else "", ("%s.png" if world else "Item_%s.png") % name))


def _amw(name):
    return lambda: am_world(name)


SHEET_ROWS = [
    [("AM S", _am("BulletRifleS")), ("AM S HP", _am("BulletRifleSHP")), ("AM S AP", _am("BulletRifleSAP")),
     ("NEW S SP", _new("GunsOfTien_BulletRifleSSP"))],
    [("AM M", _am("BulletRifleM")), ("AM M HP", _am("BulletRifleMHP")), ("AM M AP", _am("BulletRifleMAP")),
     ("NEW M SP", _new("GunsOfTien_BulletRifleMSP"))],
    [("AM Balls 00", _am("Balls00")), ("NEW Birdshot", _new("GunsOfTien_Birdshot")),
     ("AM Box Balls 00", _am("BoxBalls00")), ("NEW Box Birdshot", _new("GunsOfTien_BoxBirdshot"))],
    [("AM Box S", _am("BoxBulletsRifleS")), ("AM Box S HP", _am("BoxBulletsRifleSHP")),
     ("AM Box S AP", _am("BoxBulletsRifleSAP")), ("NEW Box S SP", _new("GunsOfTien_BoxBulletsRifleSSP"))],
    [("AM Box M", _am("BoxBulletsRifleM")), ("AM Box M HP", _am("BoxBulletsRifleMHP")),
     ("AM Box M AP", _am("BoxBulletsRifleMAP")), ("NEW Box M SP", _new("GunsOfTien_BoxBulletsRifleMSP"))],
    [("AM tex Box S HP", _amw("BoxBulletsRifleSHP")), ("NEW tex Box S SP", _new("GunsOfTien_BoxBulletsRifleSSP", True)),
     ("AM tex Box M HP", _amw("BoxBulletsRifleMHP")), ("NEW tex Box M SP", _new("GunsOfTien_BoxBulletsRifleMSP", True))],
    [("AM tex Box Balls 00", _amw("BoxBalls00")), ("NEW tex Box Birdshot", _new("GunsOfTien_BoxBirdshot", True)),
     ("AM tex Balls 00 (16px)", _amw("Balls00")), ("NEW tex Birdshot (16px)", _new("GunsOfTien_Birdshot", True))],
]


def contact_sheet(path, cell=256):
    pad, label_h = 10, 16
    cols = max(len(r) for r in SHEET_ROWS)
    sheet = Image.new("RGBA", (pad + cols * (cell + pad), pad + len(SHEET_ROWS) * (cell + label_h + pad)),
                      (40, 40, 40, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for r, row in enumerate(SHEET_ROWS):
        for c, (label, get) in enumerate(row):
            img = get().convert("RGBA")
            scale = max(1, cell // max(img.size))
            img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
            x = pad + c * (cell + pad)
            y = pad + r * (cell + label_h + pad)
            bg = Image.new("RGBA", (cell, cell), (90, 90, 90, 255))
            bg.alpha_composite(img, ((cell - img.width) // 2, (cell - img.height) // 2))
            sheet.alpha_composite(bg, (x, y + label_h))
            draw.text((x + 2, y + 2), label, fill=(255, 255, 160, 255) if label.startswith("NEW") else (230, 230, 230, 255),
                      font=font)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    sheet.save(path)


def fit_all():
    for icon_name, mesh_name in (("BoxBulletsRifleSHP", "BoxBulletsRifleS"), ("BoxBulletsRifleMHP", "BoxBulletsRifleM"),
                                 ("BoxBalls00", "BoxBalls00")):
        err, cam = make_art.fit_camera(am_icon(icon_name), am_mesh(mesh_name), am_world(icon_name))
        print('    "%s": dict(yaw=%.1f, pitch=%.1f, roll=%.1f, bbox=%r),  # score %.1f'
              % (icon_name, cam["yaw"], cam["pitch"], cam["roll"], tuple(cam["bbox"]), err))


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit_all()
        sys.exit(0)
    for path, source in build():
        img = Image.open(path)
        print("%-55s %3dx%-3d %-4s <- %s" % (os.path.relpath(path, OUT), img.width, img.height, img.mode, source))
    if "--sheet" in sys.argv:
        contact_sheet(sys.argv[sys.argv.index("--sheet") + 1])
