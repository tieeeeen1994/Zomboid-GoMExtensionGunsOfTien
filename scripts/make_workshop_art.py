#!/usr/bin/env python3
"""Workshop art for GoM Extension: Guns of Tien (Python 3 + Pillow).

    python3 scripts/make_workshop_art.py [--renders DIR] [NAME ...]

Writes preview.png (exactly 256x256, what the game's Workshop uploader accepts: the title and the ammunition),
preview2.png (1024x1024, an ad for both mods, under Steam's 1 MB image limit, added on the Steam page by hand),
preview3.png (1024x1024, the Post-93 pistols, added the same way), preview4.png (1024x1024, the MP7A2, the same),
preview5.png (1024x1024, the sawn-off shotguns, the same), preview6.png (1024x1024, the SCAR-L and SCAR-H, the same), preview7.png (1024x1024, the UMP45 and UMP9, the same), preview8.png (1024x1024, the suppressors added 2026-10-22, the same), preview9.png (1024x1024, the M249 and belt links, the same), preview10.png (1024x1024, the Uzi, Mini Uzi and Micro Uzi, the same), preview11.png (1024x1024, the short SMG stance, the same)
and, for each mod's 42/ folder, poster.png (512x512) and icon.png (128x128) for the in-game mod list; NAME (preview,
preview2 ... preview11, posters, icons) writes only those. The guns come from scripts/render_ad_guns.py (Blender), whose renders it reads from --renders (default
tmp/ad); preview11's posed figures from scripts/anim/render_stance_ad.py (Blender, same folder); the ammo boxes are the mods' own 32 px inventory icons, scaled up without smoothing.
"""

import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/textures")
POST = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/textures")
GOM = next((p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                            "3722134990/mods/GunsOfMarz/42.16/media/textures"),
                         "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                         "42.16/media/textures") if os.path.isdir(p)), None)
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


def has_glyph(f, c):
    """False when the font draws c as its missing-glyph box (DIN Alternate on the Mac has no middle dot)."""
    def drawn(ch):
        im = Image.new("L", (f.size * 2, f.size * 2), 0)
        ImageDraw.Draw(im).text((f.size // 2, f.size // 2), ch, font=f, fill=255)
        return im.tobytes()
    return drawn(c) != drawn("\u0378")


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
        dot = "·" in text and not has_glyph(f, "·")
        for c in text:
            if c == "·" and dot:            # drawn by hand where the font lacks it, halfway up the capitals
                l, t, r, b = d.textbbox((x, y), "H", font=f, anchor="l" + anchor[1])
                cx, cy, rad = x + d.textlength("·", font=f) / 2, (t + b) / 2, max(1.0, f.size * 0.09)
                d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=fill)
            else:
                d.text((x, y), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill,
                       anchor="l" + anchor[1])
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


def slot_row(page, icons, cx, y, label):
    """A centred row of inventory slots (512-grid units) under a small label; icons are full paths of 32 px icons."""
    W = page.size[0]
    k = W / 512

    def u(v):
        return round(v * k)

    size = page.size
    slot, gap = u(36), u(4)
    row_w = len(icons) * slot + (len(icons) - 1) * gap
    page.alpha_composite(text_layer(size, (u(cx), u(y)), label, font(BOLD, u(11), b"Bold"), (60, 64, 70, 255),
                                    anchor="ma", spacing=u(1)))
    sx, sy = u(cx) - row_w // 2, u(y + 18)
    slots = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(slots)
    for n, path in enumerate(icons):
        x0 = sx + n * (slot + gap)
        sd.rounded_rectangle((x0, sy, x0 + slot, sy + slot), radius=u(3), fill=(255, 255, 255, 52),
                             outline=(60, 64, 70, 150), width=max(1, u(1)))
        ic = icon(path, 64 * round(k / 2))
        slots.alpha_composite(ic, (x0 + (slot - ic.width) // 2, sy + (slot - ic.height) // 2))
    paste_with_shadow(page, slots, (0, u(2)), u(2), 120)


def preview4(path, W=1024):
    """The MP7A2, laid out on a 512 grid like preview3: the gun fitted out (stock deployed, GoM's Stub Foregrip on the
    bottom rail, EXPS3 sight, suppressor; render_ad_guns.py "mp7a2", mirrored back to the game's view), then two rows
    of inventory slots: what it shares with the MP7A1, and what its rails take from Guns of Marz."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "H&K MP7A2", 40, "OPTIONAL ADD-ON FOR GUNS OF MARZ EXTENSION")

    im = gun("mp7a2", 1.0, flip=True)
    s = min(u(480) / im.width, u(250) / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    paste_with_shadow(page, placed(size, im, ((W - im.width) // 2, u(112))), (0, u(6)), u(6), 160)

    post = lambda n: os.path.join(POST, "item_GunsOfTienPost93_%s.png" % n)
    gom = lambda n: os.path.join(GOM, "item_%s.png" % n)
    slot_row(page, [post("46x30Magazine20_MP7"), post("46x30Magazine30_MP7"), post("46x30Magazine40_MP7"),
                    post("46x30Magazine60_MP7"), post("MP7_Suppressor"), post("46x30_Box_DM11")],
             256, 358, "4.6X30MM  ·  THE MP7A1'S MAGAZINES, DRUM AND SUPPRESSOR")
    slot_row(page, [gom("Stub_Foregrip"), gom("MKC_Foregrip"), gom("MK2_Foregrip"), gom("EXPS3_Sight"),
                    gom("BrightPoint-5_Light"), gom("AimRight_Laser")],
             256, 428, "RAIL HANDGUARD  ·  GUNS OF MARZ FOREGRIPS, SIGHTS, LIGHTS, LASERS")

    save_under(page.convert("RGB"), path)


def preview5(path, W=1024):
    """The sawn-off shotguns, laid out on a 512 grid like preview4: GoM's Double Barrel whole and, under it at the same
    scale and lined up on the receiver, sawn off (stock and barrels; render_ad_guns.py "db_full" / "db_sawn", mirrored
    back to the game's view), then one row of inventory slots: the six offcuts of the three guns."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "SAWN-OFF SHOTGUNS", 40, "GUNS OF MARZ EXTENSION")

    full = Image.open(os.path.join(RENDERS, "ad_db_full.png")).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    sawn = Image.open(os.path.join(RENDERS, "ad_db_sawn.png")).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    box = full.getchannel("A").getbbox()
    s = u(440) / (box[2] - box[0])          # one scale for both, so the sawn-off one shows its true size
    full = full.resize((round(full.width * s), round(full.height * s)), Image.LANCZOS)
    sawn = sawn.resize((round(sawn.width * s), round(sawn.height * s)), Image.LANCZOS)
    x0 = (W - round((box[2] - box[0]) * s)) // 2 - round(box[0] * s)
    y_full = u(92) - round(box[1] * s)
    sbox = sawn.getchannel("A").getbbox()
    y_sawn = u(232) - sbox[1]
    paste_with_shadow(page, placed(size, full, (x0, y_full)), (0, u(6)), u(6), 160)
    paste_with_shadow(page, placed(size, sawn, (x0, y_sawn)), (0, u(6)), u(6), 160)

    # what sawing off does, beside the sawn-off gun
    bx = x0 + sbox[2] + u(14)
    by = y_sawn + sbox[1] + u(14)
    page.alpha_composite(text_layer(size, (bx, by), "SAWN OFF", font(BOLD, u(17), b"Bold"), (28, 30, 34, 255)))
    for n, line in enumerate(("FITS A HOLSTER", "QUICKER TO AIM IN", "LESS ACCURATE")):
        page.alpha_composite(text_layer(size, (bx, by + u(24 + n * 15)), line, font(BOLD, u(11), b"Bold"),
                                        (60, 64, 70, 255), spacing=u(1)))

    # only what this mod adds (user, 2026-10-19: "just add the what we add"): the offcuts, which name the three guns
    main = lambda n: os.path.join(MAIN, "item_GunsOfTien_%s.png" % n)
    guns = ("DOUBLEBARREL", "STEVENS_555", "TOZ34")
    slot_row(page, [p for g in guns for p in (main(g + "_StockOffcut"), main(g + "_BarrelOffcuts"))],
             256, 380, "DOUBLE BARREL  ·  STEVENS 555  ·  TOZ-34")
    page.alpha_composite(text_layer(size, (W // 2, u(446)), "OFFCUTS: SCRAP WOOD TO BURN, SCRAP STEEL TO SMELT",
                                    font(BOLD, u(11), b"Bold"), (60, 64, 70, 255), anchor="ma", spacing=u(1)))

    save_under(page.convert("RGB"), path)


def preview6(path, W=1024):
    """The SCAR-L and SCAR-H, laid out on a 512 grid like preview5: both fitted out at one scale, so they keep their
    real sizes against each other, lined up on the butt (render_ad_guns.py "scarl" / "scarh", mirrored back to the
    game's view), each under its name; then one row of inventory slots of what this mod adds besides the guns (the
    SCAR-H's magazines, drum, suppressor and mount device) and a line on what the SCAR-L takes from Guns of Marz."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    # no big title (user, 2026-10-20): the guns' own names carry the page, the add-on line on top
    page.alpha_composite(text_layer(size, (W // 2, u(34)), "OPTIONAL ADD-ON FOR GUNS OF MARZ EXTENSION",
                                    font(BOLD, u(14), b"Bold"), (60, 64, 70, 255), anchor="mm", spacing=u(2)))

    ims = {}
    for name in ("scarl", "scarh"):
        im = Image.open(os.path.join(RENDERS, "ad_%s.png" % name)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        ims[name] = im.crop(im.getchannel("A").getbbox())
    s = u(468) / ims["scarh"].width             # one scale for both: the SCAR-H (longest) fills the width
    x0 = (W - round(ims["scarh"].width * s)) // 2
    y = u(62)
    for name, label, sub in (("scarl", "FN SCAR-L", "MK 16  ·  5.56X45MM"),
                             ("scarh", "FN SCAR-H", "MK 17 LONG BARREL  ·  7.62X51MM")):
        im = ims[name].resize((round(ims[name].width * s), round(ims[name].height * s)), Image.LANCZOS)
        page.alpha_composite(text_layer(size, (x0 + u(4), y), label, font(BOLD, u(17), b"Bold"), (28, 30, 34, 255)))
        page.alpha_composite(text_layer(size, (x0 + u(92), y + u(5)), sub, font(BOLD, u(11), b"Bold"),
                                        (60, 64, 70, 255), spacing=u(1)))
        paste_with_shadow(page, placed(size, im, (x0, y + u(24))), (0, u(6)), u(6), 160)
        y += u(24) + im.height + u(16)

    # only what this mod adds besides the guns (preview5's rule): the SCAR-H's magazines, drum and muzzle parts
    post = lambda n: os.path.join(POST, "item_GunsOfTienPost93_%s.png" % n)
    slot_row(page, [post("SCARH"), post("762x51Magazine20_SCARH"), post("762x51Magazine10_SCARH"),
                    post("762x51Magazine50_SCARH"), post("SCARH_Suppressor"), post("SCARH_Muzzle_Mount_Device")],
             256, 400, "SCAR-H  ·  MAGAZINES, 50-ROUND DRUM, SUPPRESSOR")
    for n, line in enumerate(("SCAR-L TAKES GUNS OF MARZ STANAG MAGAZINES",
                              "FOLDING STOCK  ·  RAILS FOR GUNS OF MARZ SIGHTS, GRIPS, BIPODS")):
        page.alpha_composite(text_layer(size, (W // 2, u(464 + n * 16)), line, font(BOLD, u(11), b"Bold"),
                                        (60, 64, 70, 255), anchor="ma", spacing=u(1)))

    save_under(page.convert("RGB"), path)


def preview7(path, W=1024):
    """The UMP45 and UMP9, laid out like preview6: both fitted out at one scale (render_ad_guns.py "ump45" / "ump9",
    mirrored back to the game's view), each under its name, then one row of inventory slots (each gun and its
    magazines) and a line on what they have in common."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    page.alpha_composite(text_layer(size, (W // 2, u(34)), "OPTIONAL ADD-ON FOR GUNS OF MARZ EXTENSION",
                                    font(BOLD, u(14), b"Bold"), (60, 64, 70, 255), anchor="mm", spacing=u(2)))

    ims = {}
    for name in ("ump45", "ump9"):
        im = Image.open(os.path.join(RENDERS, "ad_%s.png" % name)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        ims[name] = im.crop(im.getchannel("A").getbbox())
    s = u(300) / max(im.width for im in ims.values())     # one scale for both: they are the same gun
    y = u(58)
    for name, label, sub, dx in (("ump45", "H&K UMP45", ".45 ACP", -u(36)), ("ump9", "H&K UMP9", "9X19MM", u(36))):
        im = ims[name].resize((round(ims[name].width * s), round(ims[name].height * s)), Image.LANCZOS)
        x0 = (W - im.width) // 2 + dx
        big = font(BOLD, u(17), b"Bold")
        page.alpha_composite(text_layer(size, (x0 + u(4), y), label, big, (28, 30, 34, 255)))
        page.alpha_composite(text_layer(size, (x0 + u(4) + round(big.getlength(label)) + u(8), y + u(5)), sub,
                                        font(BOLD, u(11), b"Bold"), (60, 64, 70, 255), spacing=u(1)))
        paste_with_shadow(page, placed(size, im, (x0, y + u(24))), (0, u(6)), u(6), 160)
        y += u(24) + im.height + u(10)

    post = lambda n: os.path.join(POST, "item_GunsOfTienPost93_%s.png" % n)
    slot_row(page, [post("UMP45"), post("45Magazine25_UMP"), post("45Magazine20_UMP"), post("45Magazine10_UMP"),
                    post("UMP9"), post("9x19Magazine30_UMP")],
             256, 404, "UMP45  ·  25, 20, 10-ROUND  ·  UMP9  ·  30-ROUND")
    page.alpha_composite(text_layer(size, (W // 2, u(466)), "SIDE-FOLDING STOCK  ·  TWO-ROUND BURST",
                                    font(BOLD, u(11), b"Bold"), (60, 64, 70, 255), anchor="ma", spacing=u(1)))

    save_under(page.convert("RGB"), path)


def preview8(path, W=1024):
    """The two suppressors added 2026-10-22, laid out like preview7: the main mod's AWC Mk9 on GoM's MP5 and on the
    UMP9, GoM's P45 on the UMP45 (render_ad_guns.py "mp5_mk9" / "ump9_mk9" / "ump45_p45", one view and scale, so the
    guns keep their real sizes, mirrored back to the game's view), each under its name and its can; then the parts in a
    slot row (ours, then GoM's P45 and .45 mount that the UMP45 now takes)."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "NEW SUPPRESSORS", 36, "GUNS OF MARZ EXTENSION")

    names = ("mp5_mk9", "ump9_mk9", "ump45_p45")
    ims = {}
    for name in names:
        im = Image.open(os.path.join(RENDERS, "ad_%s.png" % name)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        ims[name] = im.crop(im.getchannel("A").getbbox())
    s = u(290) / max(im.width for im in ims.values())     # one scale for all three
    y = u(80)
    big, small = font(BOLD, u(15), b"Bold"), font(BOLD, u(10), b"Bold")
    for name, label, sub, dx in (("mp5_mk9", "MP5", "AWC MK9", -u(40)),
                                 ("ump9_mk9", "UMP9", "AWC MK9  ·  POST-93 ADD-ON", 0),
                                 ("ump45_p45", "UMP45", "P45  ·  POST-93 ADD-ON", u(40))):
        im = ims[name].resize((round(ims[name].width * s), round(ims[name].height * s)), Image.LANCZOS)
        x0 = (W - im.width) // 2 + dx
        page.alpha_composite(text_layer(size, (x0 + u(4), y), label, big, (28, 30, 34, 255)))
        page.alpha_composite(text_layer(size, (x0 + u(4) + round(big.getlength(label)) + u(8), y + u(4)), sub, small,
                                        (60, 64, 70, 255), spacing=u(1)))
        paste_with_shadow(page, placed(size, im, (x0, y + u(18))), (0, u(5)), u(5), 160)
        y += u(18) + im.height + u(6)

    main = lambda n: os.path.join(MAIN, "item_GunsOfTien_%s.png" % n)
    gom = lambda n: os.path.join(GOM, "item_%s.png" % n)
    slot_row(page, [main("Mk9_Suppressor"), main("SMG9_Muzzle_Mount_Device"), gom("P45_Suppressor"),
                    gom("Muzzle_Mount_Device")], 256, 412, "AWC MK9 + 9MM SMG MOUNT  ·  P45 + .45 MOUNT")
    save_under(page.convert("RGB"), path)


def preview9(path, W=1024):
    """The M249 and belt links (2026-10-22), laid out like preview8: the gun with its box and belt, bipod deployed
    (render_ad_guns.py "m249", seen from its left, mirrored back to the game's view), then the box and both kinds of
    belt links with their boxes in a slot row."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "M249 LIGHT MACHINE GUN", 36, "GUNS OF MARZ EXTENSION")
    im = Image.open(os.path.join(RENDERS, "ad_m249.png")).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    im = im.crop(im.getchannel("A").getbbox())
    s = u(470) / im.width
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    y = u(118)
    paste_with_shadow(page, placed(size, im, ((W - im.width) // 2, y)), (0, u(6)), u(6), 160)
    main = lambda n: os.path.join(MAIN, "item_GunsOfTien_%s.png" % n)
    slot_row(page, [main("M249"), main("556x45Box200_M249"), main("M27_Link"), main("LinkBox_M27"),
                    main("M13_Link"), main("LinkBox_M13")], 256, 360, "200-ROUND BELTS  ·  M27 AND M13 BELT LINKS")
    # the change existing players must know about (user, 2026-10-22): belt boxes now take links
    page.alpha_composite(text_layer(size, (W // 2, u(438)), "LMG BELTS NOW NEED LINKS", font(BOLD, u(15), b"Bold"),
                                    (28, 30, 34, 255), anchor="ma", spacing=u(1)))
    page.alpha_composite(text_layer(size, (W // 2, u(460)),
                                    "M249 AND GOM'S M60  ·  ONE LINK PER ROUND LOADED  ·  FIRED LINKS EJECT",
                                    font(BOLD, u(11), b"Bold"), (60, 64, 70, 255), anchor="ma", spacing=u(1)))
    save_under(page.convert("RGB"), path)


def preview10(path, W=1024):
    """The Uzi, Mini Uzi and Micro Uzi (2026-10-23), laid out like preview8: the three at one scale (render_ad_guns.py
    "uzi" / "miniuzi" / "microuzi", from their left, mirrored back to the game's view), so they keep their real sizes,
    staggered, each under its name and rate of fire; then the guns and their shared magazines in a slot row, and the
    suppressor they all take."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "UZI · MINI UZI · MICRO UZI", 36, "GUNS OF MARZ EXTENSION")
    names = ("uzi", "miniuzi", "microuzi")
    ims = {}
    for name in names:
        im = Image.open(os.path.join(RENDERS, "ad_%s.png" % name)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        ims[name] = im.crop(im.getchannel("A").getbbox())
    # one scale for all three (their real sizes), as large as fits: the widest within 330, the three stacked in 250
    s = min(u(330) / max(im.width for im in ims.values()), u(250) / sum(im.height for im in ims.values()))
    y = u(78)
    big, small = font(BOLD, u(15), b"Bold"), font(BOLD, u(10), b"Bold")
    for name, label, sub, dx in (("uzi", "UZI", "600 RPM", -u(70)),
                                 ("miniuzi", "MINI UZI", "950 RPM  ·  FITS A HOLSTER", u(10)),
                                 ("microuzi", "MICRO UZI", "1200 RPM  ·  FITS AN ANKLE HOLSTER", u(60))):
        im = ims[name].resize((round(ims[name].width * s), round(ims[name].height * s)), Image.LANCZOS)
        x0 = (W - im.width) // 2 + dx
        line_w = u(4) + round(big.getlength(label)) + u(8) + round(small.getlength(sub)) + len(sub) * u(1)
        x0 = min(x0, W - u(24) - line_w)                  # the name line stays on the page
        page.alpha_composite(text_layer(size, (x0 + u(4), y), label, big, (28, 30, 34, 255)))
        page.alpha_composite(text_layer(size, (x0 + u(4) + round(big.getlength(label)) + u(8), y + u(4)), sub, small,
                                        (60, 64, 70, 255), spacing=u(1)))
        paste_with_shadow(page, placed(size, im, (x0, y + u(18))), (0, u(5)), u(5), 160)
        y += u(18) + im.height + u(6)
    main = lambda n: os.path.join(MAIN, "item_GunsOfTien_%s.png" % n)
    slot_row(page, [main(g) for g in ("UZI", "MINIUZI", "MICROUZI")] +
             [main("9x19Magazine%d_UZI" % r) for r in (20, 25, 32, 40, 50)],
             256, 404, "ONE SET OF MAGAZINES  ·  20, 25, 32, 40, 50-ROUND")
    page.alpha_composite(text_layer(size, (W // 2, u(466)), "AWC MK9 SUPPRESSOR FITS ALL THREE",
                                    font(BOLD, u(11), b"Bold"), (60, 64, 70, 255), anchor="ma", spacing=u(1)))
    save_under(page.convert("RGB"), path)


def preview11(path, W=1024):
    """The short SMG stance (2026-10-24): four game characters in four of its poses, one gun each
    (scripts/anim/render_stance_ad.py "carried" / "aimed" / "crouched" / "running": a survivor, a police officer, a
    woman in a hoodie, a soldier, dressed from the game's files; one scale, so the figures keep their sizes), standing
    on one line, each over its pose and gun, then preview2's dark band with the selling points."""
    H = W
    size = (W, H)
    k = W / 512

    def u(v):
        return round(v * k)

    page = background(size).convert("RGBA")
    title(page, "SHORT SMG STANCE", 36, "UZI  ·  MINI UZI  ·  MP5K  ·  MP7")
    shots = (("carried", "CARRIED", "UZI"), ("aimed", "AIMED", "MP5K"), ("crouched", "SNEAKING", "MP7"),
             ("running", "RUNNING", "UZI"))
    ims = {}
    for name, _, _ in shots:
        im = Image.open(os.path.join(RENDERS, "stance_%s.png" % name)).convert("RGBA")
        ims[name] = im.crop(im.getchannel("A").getbbox())
    gap = u(4)
    big, small = font(BOLD, u(15), b"Bold"), font(BOLD, u(10), b"Bold")
    band_top = u(424)
    # spacing from the title: the gun names end as far above the band as the title starts below the page's top, the
    # pose labels sit just under the feet, and the figures fill the room between the subtitle and the labels
    d = ImageDraw.Draw(page)
    title_top = d.textbbox((W // 2, u(36)), "SHORT SMG STANCE", font=font(BOLD, u(30), b"Bold"), anchor="mm")[1]
    sub_bottom = d.textbbox((W // 2, u(66)), "UZI", font=font(BOLD, u(14), b"Bold"), anchor="mm")[3]
    name_h = d.textbbox((0, 0), "UZI", font=small, anchor="la")[3]
    label_y = band_top - title_top - name_h - u(18)
    ground = label_y - u(8)
    top = sub_bottom + u(10)
    s = min((ground - top) / max(im.height for im in ims.values()),
            (W - u(28) - gap * (len(shots) - 1)) / sum(im.width for im in ims.values()))
    scaled = {n: im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) for n, im in ims.items()}
    x = (W - sum(im.width for im in scaled.values()) - gap * (len(shots) - 1)) // 2
    for name, label, gun_name in shots:
        im = scaled[name]
        paste_with_shadow(page, placed(size, im, (x, ground - im.height)), (0, u(5)), u(5), 150)
        cx = x + im.width // 2
        page.alpha_composite(text_layer(size, (cx, label_y), label, big, (28, 30, 34, 255), anchor="ma",
                                        spacing=u(1)))
        page.alpha_composite(text_layer(size, (cx, label_y + u(18)), gun_name, small, (60, 64, 70, 255), anchor="ma",
                                        spacing=u(1)))
        x += im.width + gap
    band(page, ["EVERY RIFLE ANIMATION REMADE FOR THEM", "BOTH HANDS ON THE GUN, CARRIED CLOSE",
                "OWN RELOADS, SNEAKING, SITTING AND EMOTES"], 424)
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
    if want("preview4"):
        preview4(os.path.join(ROOT, "preview4.png"))     # the MP7A2, added the same way
    if want("preview5"):
        preview5(os.path.join(ROOT, "preview5.png"))     # the sawn-off shotguns, added the same way
    if want("preview6"):
        preview6(os.path.join(ROOT, "preview6.png"))     # the SCAR-L and SCAR-H, added the same way
    if want("preview7"):
        preview7(os.path.join(ROOT, "preview7.png"))     # the UMP45 and UMP9, added the same way
    if want("preview8"):
        preview8(os.path.join(ROOT, "preview8.png"))     # the new suppressors, added the same way
    if want("preview9"):
        preview9(os.path.join(ROOT, "preview9.png"))     # the M249 and belt links, added the same way
    if want("preview10"):
        preview10(os.path.join(ROOT, "preview10.png"))   # the Uzis, added the same way
    if want("preview11"):
        preview11(os.path.join(ROOT, "preview11.png"))   # the short SMG stance, added the same way
    if want("preview"):
        preview_small(os.path.join(ROOT, "preview.png"))
    if want("posters"):
        poster_main(os.path.join(main_dir, "poster.png"))
        poster_post93(os.path.join(post_dir, "poster.png"))
    if want("icons"):
        mod_icon(os.path.join(main_dir, "icon.png"), os.path.join(MAIN, "item_9x19_Box_HP.png"))
        mod_icon(os.path.join(post_dir, "icon.png"), os.path.join(POST, "item_GunsOfTienPost93_P90TR.png"))
