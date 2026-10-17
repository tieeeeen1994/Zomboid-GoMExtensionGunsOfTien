#!/usr/bin/env python3
"""Workshop art for GoM Extension: Guns of Tien (Python 3 + Pillow).

    python3 scripts/make_workshop_art.py [--renders DIR] [NAME ...]

Writes preview.png (exactly 256x256, what the game's Workshop uploader accepts: the title and the ammunition),
preview2.png (1024x1024, an ad for both mods, under Steam's 1 MB image limit, added on the Steam page by hand),
preview3.png (1024x1024, the Post-93 pistols, added the same way) and, for each mod's 42/ folder, poster.png
(512x512) and icon.png (128x128) for the in-game mod list; NAME (preview, preview2, preview3, posters, icons) writes
only those. The guns come from scripts/render_ad_guns.py (Blender), whose renders it reads from --renders (default
tmp/ad); the ammo boxes are the mods' own 32 px inventory icons, scaled up without smoothing.
"""

import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/textures")
POST = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/textures")
RENDERS = sys.argv[sys.argv.index("--renders") + 1] if "--renders" in sys.argv else os.path.join(ROOT, "tmp/ad")
ONLY = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] != "--renders"]


def _first(*paths):
    return next((p for p in paths if os.path.isfile(p)), None)


IMPACT = _first("/System/Library/Fonts/Supplemental/Impact.ttf", "C:/Windows/Fonts/impact.ttf")
BOLD = _first("C:/Windows/Fonts/bahnschrift.ttf", "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf", "C:/Windows/Fonts/arialbd.ttf")

AMBER = (255, 196, 64)
INK = (14, 15, 18)


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight and path.lower().endswith("bahnschrift.ttf"):
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


def background(size):
    """Light steel grey, brightest behind the guns, a faint warm tint there, and faint diagonal stripes."""
    w, h = size
    k = w / 512
    bg = Image.new("RGB", size)
    px = bg.load()
    for y in range(h):
        for x in range(w):
            dx, dy = (x - w * 0.5) / w, (y - h * 0.52) / h
            v = max(0.0, 1.0 - (dx * dx + dy * dy) * 2.2)
            px[x, y] = (int(112 + 70 * v), int(116 + 70 * v), int(122 + 70 * v))
    glow = Image.new("L", size, 0)
    ImageDraw.Draw(glow).ellipse((40 * k, 120 * k, w - 40 * k, 380 * k), fill=40)
    glow = glow.filter(ImageFilter.GaussianBlur(60 * k))
    bg = Image.composite(Image.new("RGB", size, (214, 196, 160)), bg, glow)
    stripes = Image.new("L", size, 0)
    d = ImageDraw.Draw(stripes)
    step = round(14 * k)
    for x in range(-h, w, step):
        d.line([(x, h), (x + h, 0)], fill=10, width=round(4 * k))
    return Image.composite(Image.new("RGB", size, (90, 94, 100)), bg, stripes)


def text_layer(size, xy, text, f, fill, stroke=0, stroke_fill=INK, anchor="la", spacing=0):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if spacing:
        x, y = xy
        total = sum(d.textlength(c, font=f) for c in text) + spacing * (len(text) - 1)
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        for c in text:
            d.text((x, y), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor="l" + anchor[1])
            x += d.textlength(c, font=f) + spacing
    else:
        d.text(xy, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)
    return layer


def shadow(layer, offset=(0, 4), blur=4, alpha=200):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    s = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    s.putalpha(ImageChops.offset(a, *offset))
    return s


def paste_with_shadow(page, layer, offset=(0, 4), blur=4, alpha=200):
    page.alpha_composite(shadow(layer, offset, blur, alpha))
    page.alpha_composite(layer)


def gun(name, scale, flip=False):
    """A render cropped and scaled; flip mirrors a pistol's render back to the game's view (render_ad_guns.py)."""
    im = Image.open(os.path.join(RENDERS, "ad_%s.png" % name)).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)


def icon(path, px):
    return Image.open(path).convert("RGBA").resize((px, px), Image.NEAREST)


def placed(size, im, xy):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.alpha_composite(im, xy)
    return layer


def save_under(page, path, limit=1_000_000):
    """PNG under Steam's 1 MB preview limit: full colour if it fits, else an adaptive 256-colour palette."""
    page.save(path, optimize=True)
    if os.path.getsize(path) > limit:
        page.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(path, optimize=True)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


def preview(path, W=1024):
    """The ad, laid out on a 512 grid and drawn at W x W."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")

    # title: the item's name, plainly
    page.alpha_composite(text_layer(size, (W // 2, u(44)), "GUNS OF MARZ EXTENSION", font(BOLD, u(30), b"Bold"),
                                    (28, 30, 34, 255), anchor="mm", spacing=u(2)))

    # the hero: the main mod's new ammunition, two rows of boxes
    rows = [["item_9x19_Box_HP.png", "item_9x19_Box_PPP.png", "item_45_Box_P.png", "item_9x39_Box_SP6.png"],
            ["item_762x39_Box_US.png", "item_762x39_Box_SteelCore.png", "item_12Gauge_Box_Birdshot.png",
             "item_3006_Box_SP.png"]]
    px = 32 * round(100 * k / 32)                 # whole multiples of the 32 px icons stay crisp
    step = px - u(12)
    for r, row in enumerate(rows):
        x0 = (W - (len(row) * step + u(12))) // 2 + (u(-18) if r == 0 else u(18))
        for n, name in enumerate(row):
            lift = u((0, 6, 2, 8)[n])
            paste_with_shadow(page, placed(size, icon(os.path.join(MAIN, name), px),
                                           (x0 + n * step, u(86 + r * 86) + lift)), (0, u(5)), u(4), 200)

    # the optional add-on: a framed panel with the two guns, same scale (true sizes against each other)
    top, bottom = u(306), u(410)
    panel = Image.new("RGBA", size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((u(116), top, W - u(116), bottom), radius=u(8), fill=(255, 255, 255, 46),
                         outline=(60, 64, 70, 140), width=max(1, u(1)))
    page.alpha_composite(panel)
    page.alpha_composite(text_layer(size, (W // 2, top + u(12)), "OPTIONAL  ·  POST-1993 ADD-ON",
                                    font(BOLD, u(11), b"Bold"), (40, 42, 48, 255), anchor="mm", spacing=u(2)))
    s = 0.118 * k
    mp7, p90 = gun("mp7", s), gun("p90", s)
    gy = bottom - u(8)
    paste_with_shadow(page, placed(size, mp7, (W // 2 - u(6) - mp7.width, gy - mp7.height)), (0, u(5)), u(5), 150)
    paste_with_shadow(page, placed(size, p90, (W // 2 + u(6), gy - p90.height)), (0, u(5)), u(5), 150)

    # selling points: a dark band with four amber-ticked lines
    band = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, u(424), W, H), fill=(8, 9, 11, 215))
    page.alpha_composite(band)
    d = ImageDraw.Draw(page)
    d.line([(0, u(424)), (W, u(424))], fill=AMBER + (255,), width=u(3))
    f = font(BOLD, u(19), b"Bold")
    for n, text in enumerate(("NEW AMMUNITION WITH AMMO MAKER RECIPES", "ADJUSTED STATS",
                              "2 NEW OPTIONAL GUNS FOR POST-1993")):
        x, y = 22, 432 + n * 26
        d.rectangle((u(x), u(y + 4), u(x + 10), u(y + 14)), fill=AMBER)
        d.text((u(x + 18), u(y)), text, font=f, fill=(238, 238, 238))

    save_under(page.convert("RGB"), path)


def preview3(path, W=1024):
    """The Post-93 pistols, laid out on a 512 grid: each gun fitted out at true size against the other, beside its
    name and a row of its parts as inventory slots (the 32 px icons at 2x); no text band."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "POST-1993 PISTOLS", 40, "OPTIONAL ADD-ON FOR GUNS OF MARZ EXTENSION")

    s = 0.19 * k
    rows = [  # gun, its side of the page, name, calibre, parts, top
        ("fiveseven", "right", "FN FIVE-SEVEN", "5.7X28MM", ["57x28Magazine20_FIVESEVEN", "57x28Magazine30_FIVESEVEN",
                                                           "FIVESEVEN_Suppressor", "57x28_Box_SS190"], 112),
        ("ucp", "left", "H&K UCP PROTOTYPE", "4.6X30MM", ["46x30Magazine20_UCP", "46x30Magazine40_UCP",
                                                         "MP7_Suppressor", "46x30_Box_DM11"], 288),
    ]
    slot, gap = u(36), u(4)
    for name, side, label, calibre, parts, top in rows:
        im = gun(name, s, flip=True)
        x = W - u(14) - im.width if side == "right" else u(14)
        paste_with_shadow(page, placed(size, im, (x, u(top))), (0, u(6)), u(6), 160)
        # the name block on the other side, level with the gun's middle (the UCP's drum hangs below it)
        bx = u(24) if side == "right" else W - u(24)
        anchor = "l" if side == "right" else "r"
        by = u(top) + round(im.height * (0.5 if side == "right" else 0.38)) - u(38)
        page.alpha_composite(text_layer(size, (bx, by), label, font(BOLD, u(17), b"Bold"), (28, 30, 34, 255),
                                        anchor=anchor + "a"))
        page.alpha_composite(text_layer(size, (bx, by + u(22)), calibre, font(BOLD, u(11), b"Bold"),
                                        (60, 64, 70, 255), anchor=anchor + "a", spacing=u(1)))
        row_w = len(parts) * slot + (len(parts) - 1) * gap
        sx = bx if side == "right" else bx - row_w
        sy = by + u(40)
        slots = Image.new("RGBA", size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(slots)
        for n, part in enumerate(parts):
            x0 = sx + n * (slot + gap)
            sd.rounded_rectangle((x0, sy, x0 + slot, sy + slot), radius=u(3), fill=(255, 255, 255, 52),
                                 outline=(60, 64, 70, 150), width=max(1, u(1)))
            ic = icon(os.path.join(POST, "item_GunsOfTienPost93_%s.png" % part), 64 * round(k / 2))
            slots.alpha_composite(ic, (x0 + (slot - ic.width) // 2, sy + (slot - ic.height) // 2))
        paste_with_shadow(page, slots, (0, u(2)), u(2), 120)

    save_under(page.convert("RGB"), path)


def preview_small(path, W=256):
    """The in-game uploader's preview: exactly 256x256. The title and the main mod's ammunition, boxes at 2x."""
    page = background((W, W)).convert("RGBA")
    k = W / 256
    page.alpha_composite(text_layer(page.size, (W // 2, round(26 * k)), "GUNS OF MARZ", font(BOLD, round(26 * k), b"Bold"),
                                    (28, 30, 34, 255), anchor="mm", spacing=round(1 * k)))
    page.alpha_composite(text_layer(page.size, (W // 2, round(52 * k)), "EXTENSION", font(BOLD, round(17 * k), b"Bold"),
                                    (60, 64, 70, 255), anchor="mm", spacing=round(3 * k)))
    rows = [["item_9x19_Box_HP.png", "item_45_Box_P.png", "item_9x39_Box_SP6.png"],
            ["item_762x39_Box_SteelCore.png", "item_12Gauge_Box_Birdshot.png", "item_3006_Box_SP.png"]]
    px = 64 * round(k)                             # 2x the 32 px icons, crisp
    step = px + round(8 * k)
    for r, row in enumerate(rows):
        x0 = (W - (len(row) * step - round(8 * k))) // 2 + round((-12 if r == 0 else 12) * k)
        for n, name in enumerate(row):
            lift = round((0, 5, 2)[n] * k)
            paste_with_shadow(page, placed(page.size, icon(os.path.join(MAIN, name), px),
                                           (x0 + n * step, round((76 + r * 80) * k) + lift)),
                              (0, round(3 * k)), round(3 * k), 200)
    page.convert("RGB").save(path, optimize=True)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


def band(page, lines, top):
    """The dark band along the bottom with amber-ticked lines (512-grid units, scaled to the page)."""
    W, H = page.size
    k = W / 512

    def u(v):
        return round(v * k)

    layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle((0, u(top), W, H), fill=(8, 9, 11, 215))
    page.alpha_composite(layer)
    d = ImageDraw.Draw(page)
    d.line([(0, u(top)), (W, u(top))], fill=AMBER + (255,), width=u(3))
    f = font(BOLD, u(19), b"Bold")
    for n, text in enumerate(lines):
        x, y = 22, top + 8 + n * 26
        d.rectangle((u(x), u(y + 4), u(x + 10), u(y + 14)), fill=AMBER)
        d.text((u(x + 18), u(y)), text, font=f, fill=(238, 238, 238))


def title(page, text, y=44, sub=None):
    W = page.size[0]
    k = W / 512
    page.alpha_composite(text_layer(page.size, (W // 2, round(y * k)), text, font(BOLD, round(30 * k), b"Bold"),
                                    (28, 30, 34, 255), anchor="mm", spacing=round(2 * k)))
    if sub:
        page.alpha_composite(text_layer(page.size, (W // 2, round((y + 30) * k)), sub, font(BOLD, round(14 * k), b"Bold"),
                                        (60, 64, 70, 255), anchor="mm", spacing=round(2 * k)))


def boxes_rows(page, rows, folder, y0, row_step, px_grid, stagger=18):
    W = page.size[0]
    k = W / 512
    px = 32 * max(1, round(px_grid * k / 32))
    step = px - round(12 * k)
    for r, row in enumerate(rows):
        x0 = (W - (len(row) * step + round(12 * k))) // 2 + round((-stagger if r == 0 else stagger) * k) * (len(rows) > 1)
        for n, name in enumerate(row):
            lift = round((0, 6, 2, 8, 4)[n % 5] * k)
            paste_with_shadow(page, placed(page.size, icon(os.path.join(folder, name), px),
                                           (x0 + n * step, round((y0 + r * row_step) * k) + lift)),
                              (0, round(5 * k)), round(4 * k), 200)


def poster_main(path, W=512):
    """In-game mod list poster of GoM Extension: Guns of Tien: its ammunition."""
    page = background((W, W)).convert("RGBA")
    title(page, "GUNS OF MARZ EXTENSION", 48)
    boxes_rows(page, [["item_9x19_Box_HP.png", "item_9x19_Box_PPP.png", "item_45_Box_P.png", "item_9x39_Box_SP6.png"],
                      ["item_762x39_Box_US.png", "item_762x39_Box_SteelCore.png", "item_12Gauge_Box_Birdshot.png",
                       "item_3006_Box_SP.png"]], MAIN, 150, 100, 96)
    band(page, ["NEW AMMUNITION WITH AMMO MAKER RECIPES", "ADJUSTED STATS"], 448)
    save_under(page.convert("RGB"), path)


def poster_post93(path, W=512):
    """In-game mod list poster of the Post-93 add-on: the MP7 and the P90 and their rounds."""
    page = background((W, W)).convert("RGBA")
    k = W / 512
    title(page, "POST-1993 ADD-ON", 44, "FOR GUNS OF MARZ EXTENSION")
    s = 0.235 * k
    mp7, p90 = gun("mp7", s), gun("p90", s)
    paste_with_shadow(page, placed(page.size, p90, ((W - p90.width) // 2 + round(26 * k), round(322 * k) - p90.height)),
                      (0, round(8 * k)), round(8 * k), 170)
    paste_with_shadow(page, placed(page.size, mp7, ((W - mp7.width) // 2 - round(26 * k), round(96 * k))),
                      (0, round(8 * k)), round(8 * k), 170)
    boxes_rows(page, [["item_GunsOfTienPost93_46x30_Box_DM11.png", "item_GunsOfTienPost93_46x30_Box_SS.png",
                       "item_GunsOfTienPost93_57x28_Box_SS190.png", "item_GunsOfTienPost93_57x28_Box_SB193.png",
                       "item_GunsOfTienPost93_57x28_Box_SS197SR.png"]], POST, 334, 0, 72)
    band(page, ["MP7 AND P90 WITH MAGAZINES AND SUPPRESSORS", "4.6X30MM AND 5.7X28MM AMMUNITION"], 422)
    save_under(page.convert("RGB"), path)


def mod_icon(path, item, W=128):
    """128 px in-game mod list icon: one inventory icon scaled up crisp on the poster's background."""
    page = background((W, W)).convert("RGBA")
    px = 32 * (W * 7 // 8 // 32)
    paste_with_shadow(page, placed(page.size, icon(item, px), ((W - px) // 2, (W - px) // 2)), (0, 3), 3, 200)
    page.convert("RGB").save(path, optimize=True)
    print("wrote", path)


if __name__ == "__main__":
    def want(name):
        return not ONLY or name in ONLY

    main_dir = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42")
    post_dir = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42")
    if want("preview2"):
        preview(os.path.join(ROOT, "preview2.png"))      # the full ad, added on the Steam page by hand
    if want("preview3"):
        preview3(os.path.join(ROOT, "preview3.png"))     # the pistols, added the same way
    if want("preview"):
        preview_small(os.path.join(ROOT, "preview.png"))
    if want("posters"):
        poster_main(os.path.join(main_dir, "poster.png"))
        poster_post93(os.path.join(post_dir, "poster.png"))
    if want("icons"):
        mod_icon(os.path.join(main_dir, "icon.png"), os.path.join(MAIN, "item_9x19_Box_HP.png"))
        mod_icon(os.path.join(post_dir, "icon.png"), os.path.join(POST, "item_GunsOfTienPost93_P90TR.png"))
