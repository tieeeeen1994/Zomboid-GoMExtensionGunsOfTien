#!/usr/bin/env python3
"""Icons and world-model textures for the 7.62x25mm Tokarev and 9x18mm Makarov rounds and boxes of GoM Extension:
Guns of Tien (gen_scripts.py ammo_762x25_9x18()).

Everything is derived from Guns of Marz's own PNGs and meshes (read only) with the helpers of make_art.py and
post93/make_ammo_art.py, as make_22lr_art.py does; nothing is hand-edited and every run writes the same bytes.

Rounds (GoM has neither: no mesh, texture or item).
  * 7.62x25mm Tokarev on GoM's 57x28_Round mesh (the nearest bottlenecked pistol-size round; drawn at 0.86 for the
    Tokarev's 34.9 mm against the 5.7's 40.5) and its Nato_Round_Base texture, the case repainted in tombac (the
    Soviet 57-N-134's steel case clad in copper alloy) so it is not taken for a 5.7x28. Loads (gen_scripts.py
    LOADS_762x25): steel core (Soviet Pst, 57-N-134s) with GoM's AP tip paint, subsonic (China's heavy pointed
    round for the suppressed Type 64) with GoM's subsonic tip paint. Icons rendered with GoM's 5.56 icon camera,
    as the 5.7x28's (make_ammo_art).
  * 9x18mm Makarov on GoM's 9x19_Round (Pistol_Standard_Round_Base), the case repainted in the clad steel grey of
    the Soviet 57-N-181S. Icon with GoM's 9x19 icon camera and colour model (make_22lr_art's use_9x19_reference).
Boxes. 50-round HandGunAmmoBox boxes from GoM's 9x19_Box (make_ammo_art.make_box: lid flap, sticker, tray, now with
the tray's heads in the calibre's case colour), the visible sleeve redrawn in a layout of each calibre's own, with a
made-up maker and a fierce animal as GoM's own brand boxes (user, 2026-11-25, approving the proposal):
  * 7.62x25 "SAKER" (a falcon of the steppes): an olive-drab surplus face, a falcon's head (draw_falcon, original
    art) in a cream roundel ringed in the load's colour, "7.62x25" stencilled, a diagonal band in the load's
    colour, the maker's name, the load on a label at the tray end; the long side olive.
  * 9x18 "TUSKER": a cream face with a tall panel down the left in the load's colour holding a boar's head with its
    tusks (draw_boar, original art) and the maker's name up it, a huge black "9x18", "MAKAROV", the load on a
    label; the long side in the panel's colour.
No real makers' names or marks (Brown Bear, Golden Tiger, Wolf, Barnaul, Tula are real brands, so neither a bear nor
a tiger nor a wolf is used, and no maker's name).

Usage:  py scripts/make_762x25_9x18_art.py              write every output
        py scripts/make_762x25_9x18_art.py --sheet [P]  also write a contact sheet (default docs/762x25_9x18_art_sheet.png)
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "post93"))
import make_art as A  # noqa: E402
import make_ammo_art as M  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/textures")
SHEET = os.path.join(ROOT, "docs/762x25_9x18_art_sheet.png")

TOMBAC = (176, 104, 62)             # copper-alloy clad steel case (Soviet 57-N-134)
CLAD_STEEL = (128, 126, 118)        # grey clad steel case (Soviet 57-N-181S)
OLIVE = (88, 92, 56)                # the Tokarev box's surplus olive drab
CREAM = (232, 222, 192)
INK = (20, 20, 18)
RED = (150, 40, 34)

M.CALIBRES["762x25"] = dict(text="7.62x25", panel=OLIVE, ink=CREAM, maker="SAKER", tray=TOMBAC)
M.CALIBRES["9x18"] = dict(text="9x18", panel=CREAM, ink=INK, maker="TUSKER", tray=CLAD_STEEL)


def draw_falcon(size=400):
    """The Tokarev boxes' mascot: a falcon's head in profile facing left, as the .22's wolf is a head: the hooked
    beak on its yellow cere, the eye in its yellow ring under a fierce brow, the dark moustache stripe that marks a
    falcon, a cream throat, slate crown and nape feathers. Drawn here (original art), 4x supersampled, outlined and
    cropped to itself so it fills its roundel and reads at 25 texels."""
    k = 4
    W = H = 200
    img = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    OUTL, SLATE, DARK, CREAM_, BAR = (16, 16, 20, 255), (82, 90, 106, 255), (34, 36, 46, 255), (238, 228, 204, 255),         (130, 110, 86, 255)
    YEL, BEAK = (246, 198, 38, 255), (58, 62, 72, 255)
    head = [(54, 72), (64, 50), (84, 36), (116, 28), (150, 36), (178, 56), (194, 92), (196, 140), (186, 170),
            (196, 194), (150, 182), (122, 194), (96, 170), (70, 150), (54, 132), (46, 112), (54, 100)]
    d.polygon(P(head), fill=SLATE)
    # cream cheek and throat, barred low down
    d.polygon(P([(54, 104), (72, 104), (100, 128), (126, 160), (150, 182), (122, 194), (96, 170), (70, 150),
                 (54, 132), (46, 112)]), fill=CREAM_)
    for x, y in ((96, 156), (110, 168), (124, 178)):
        d.line(P([(x - 4, y - 3), (x + 4, y + 3)]), fill=BAR, width=3 * k)
    # nape feathers trailing back
    for f in ((150, 70, 188, 96), (156, 104, 192, 126), (150, 138, 186, 160)):
        d.line(P([(f[0], f[1]), (f[2], f[3])]), fill=DARK, width=4 * k)
    d.polygon(P(head), outline=OUTL, width=4 * k)
    # the moustache stripe, the brow, the eye
    d.polygon(P([(74, 90), (98, 92), (104, 118), (98, 146), (84, 140), (76, 114)]), fill=DARK)
    d.ellipse(P([(70, 64), (100, 94)]), fill=YEL, outline=OUTL, width=2 * k)
    d.ellipse(P([(78, 72), (94, 88)]), fill=(8, 8, 10, 255))
    d.ellipse(P([(84, 75), (89, 80)]), fill=(255, 255, 255, 255))
    d.polygon(P([(60, 62), (108, 60), (112, 70), (66, 72)]), fill=DARK)
    # cere and the hooked beak
    d.polygon(P([(52, 70), (64, 70), (64, 104), (52, 104)]), fill=YEL, outline=OUTL, width=2 * k)
    d.polygon(P([(52, 72), (28, 72), (12, 86), (6, 108), (16, 100), (28, 96), (52, 100)]), fill=BEAK, outline=OUTL,
              width=2 * k)
    d.polygon(P([(52, 100), (32, 102), (40, 112), (56, 112)]), fill=BEAK, outline=OUTL, width=2 * k)
    img = img.crop(img.getbbox())
    s = size / max(img.size)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def draw_boar(size=400):
    """The Makarov boxes' mascot: a wild boar's head, three-quarter front, snout down, tusks up, ears back, the
    bristle ridge raised and a red eye, drawn here (original art), 4x supersampled and outlined."""
    k = 4
    W = H = 200
    img = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    OUTL, HIDE, DARK, SNOUT, TUSK = (22, 14, 10, 255), (112, 74, 48, 255), (64, 40, 26, 255), (168, 112, 92, 255), \
        (244, 236, 214, 255)
    # bristle ridge (behind), spiky
    ridge = [(40, 70), (52, 40), (62, 58), (74, 26), (86, 52), (100, 18), (110, 50), (126, 24), (132, 56),
             (150, 36), (150, 76)]
    d.polygon(P(ridge), fill=DARK, outline=OUTL, width=2 * k)
    # ears, laid back
    for ear in ([(38, 72), (20, 40), (60, 60)], [(150, 72), (178, 44), (140, 58)]):
        d.polygon(P(ear), fill=HIDE, outline=OUTL, width=3 * k)
    # head: wide at the brow, tapering to the snout
    head = [(36, 76), (70, 58), (120, 56), (160, 76), (166, 104), (150, 132), (128, 150), (118, 176), (82, 176),
            (72, 150), (48, 130), (34, 104)]
    d.polygon(P(head), fill=HIDE, outline=OUTL, width=3 * k)
    d.polygon(P([(48, 130), (72, 150), (82, 176), (118, 176), (128, 150), (150, 132), (120, 140), (80, 140)]),
              fill=DARK)
    # snout disc with nostrils
    d.ellipse(P([(80, 156), (120, 190)]), fill=SNOUT, outline=OUTL, width=3 * k)
    d.ellipse(P([(88, 168), (96, 180)]), fill=OUTL)
    d.ellipse(P([(104, 168), (112, 180)]), fill=OUTL)
    # tusks curving up past the snout
    for tusk in ([(80, 160), (60, 150), (50, 124), (66, 142), (84, 152)], [(120, 160), (140, 150), (150, 124),
                                                                         (134, 142), (116, 152)]):
        d.polygon(P(tusk), fill=TUSK, outline=OUTL, width=2 * k)
    # angry brows and red eyes
    for eye, brow in (((62, 92, 78, 104), [(54, 84), (82, 96)]), ((122, 92, 138, 104), [(146, 84), (118, 96)])):
        d.ellipse(P([(eye[0], eye[1]), (eye[2], eye[3])]), fill=(196, 30, 24, 255), outline=OUTL, width=2 * k)
        d.line(P(brow), fill=OUTL, width=5 * k)
    img = img.crop(img.getbbox())
    s = size / max(img.size)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def layout_762x25(img, spec, cal):
    """Olive-drab surplus face: the falcon in a cream roundel ringed in the load's colour at the top (the end away
    from the tray), "7.62x25" stencilled in cream, a diagonal band in the load's colour, "SAKER", the load on a
    label at the tray end; the long side olive with the name in cream."""
    band = spec["outer"]
    M.fill(img, M.FACE, OLIVE)
    d = ImageDraw.Draw(img)
    d.ellipse((8, 24, 39, 53), fill=CREAM + (255,), outline=band + (255,), width=2)
    M.picture(img, draw_falcon(), (11, 27, 36, 50))
    M.text(img, (2, 55, 45, 63), cal["text"], CREAM)
    d.polygon([(0, 70), (47, 64), (47, 69), (0, 75)], fill=band + (255,))
    M.text(img, (4, 76, 43, 81), cal["maker"], CREAM)
    A.draw_label(img, (6, 83, 41, 90), spec["load"], spec["band"], spec["text"], vertical=False)
    M.fill(img, M.SIDE, OLIVE)
    M.fill(img, (48, 22, 63, 24), band)
    M.text(img, (50, 27, 61, 88), "7.62x25 TOKAREV %s" % spec["side"], CREAM, True)


def layout_9x18(img, spec, cal):
    """Cream face with a tall panel down its left in the load's colour: the boar at its top, "TUSKER" up it in
    cream; a huge black "9x18", "MAKAROV", the load on a label at the tray end; the long side in the panel's
    colour."""
    panel = spec["outer"]
    M.fill(img, M.FACE, CREAM)
    M.fill(img, (0, 22, 17, 91), panel)
    M.picture(img, draw_boar(), (1, 23, 16, 40))
    M.text(img, (3, 43, 14, 89), cal["maker"], CREAM, True)
    M.text(img, (19, 26, 46, 48), cal["text"], INK)
    M.text(img, (19, 51, 46, 58), "MAKAROV", INK)
    M.fill(img, (19, 61, 46, 62), panel)
    A.draw_label(img, (19, 76, 45, 89), spec["load"], spec["band"], spec["text"], vertical=False)
    M.fill(img, M.SIDE, panel)
    M.text(img, (50, 27, 61, 88), "9x18 MAKAROV %s" % spec["side"], CREAM, True)


# ==================================================================================================
# Rounds
# ==================================================================================================

def case_cells(geometry, texture):
    fractions = A.bullet_fractions(geometry)
    px = Image.open(os.path.join(A.GOM_ROUNDS, texture + ".png")).convert("RGBA").load()
    return [(x, y) for y in range(128) for x in range(128) if px[x, y][3] > 0 and (x, y) not in fractions]


def recase(tex, cells, colour):
    out = tex.copy()
    px = out.load()
    ref = A._median([A.lum(px[c]) for c in cells if px[c][3] > 200])
    for c in cells:
        px[c] = A.paint(px[c], colour, ref, 1.0)
    return out


def use_reference(kind):
    if kind == "9x19":
        M.REF_ICON, M.REF_GEOMETRY, M.REF_TEXTURE = "item_9x19_Round_Base.png", "9x19_Round", "Pistol_Standard_Round_Base"
    else:
        M.REF_ICON, M.REF_GEOMETRY, M.REF_TEXTURE = "item_556x45_Round_Base.png", "556x45_Round", "Nato_Round_Base"
    M._model = None


def make_round(geometry, texture, case, tip, ref_kind, camera):
    use_reference(ref_kind)
    fractions = A.bullet_fractions(geometry)
    base = recase(Image.open(os.path.join(A.GOM_ROUNDS, texture + ".png")).convert("RGBA"),
                  case_cells(geometry, texture), case)
    icon = M.render_round_icon(geometry, base, camera)
    if tip is None:
        return icon, base
    layers = [(A.GOM_PAINT_FROM, 1.0, tip, 1.0)]
    world = M.paint_texture(base, fractions, layers)
    icon = A.paint_round_icon(icon, geometry, camera, fractions, [(A.GOM_PAINT_FROM, 1.0, M.icon_colour(tip))])
    return icon, world


# (art suffix, tip scheme or None, box label, side text, sticker, box colour)
TOKAREV = [("", None, "TOKAREV", "", "STANDARD", RED),
           ("_SC", "AP", "STEEL CORE", "STEEL CORE", "STEEL CORE", None),
           ("_SS", "SS", "SUBSONIC", "SUBSONIC", "SUBSONIC", None)]
MAKAROV = [("", None, "MAKAROV", "", "STANDARD", RED)]
GOM_RED = (161, 67, 59)


def build():
    written = []
    tok_cam = M.ROUND_CAMERA
    mak_cam = A.CAMERAS["item_9x19_Round_Base.png"]
    for cal, geometry, texture, case, ref, cam, loads, layout in (
            ("762x25", "57x28_Round", "Nato_Round_Base", TOMBAC, "556", tok_cam, TOKAREV, layout_762x25),
            ("9x18", "9x19_Round", "Pistol_Standard_Round_Base", CLAD_STEEL, "9x19", mak_cam, MAKAROV, layout_9x18)):
        for art, scheme, label, side, sticker, colour in loads:
            tip = M.gom(scheme)["tip"] if scheme else None
            rnd, box = "GunsOfTien_%s_Round%s" % (cal, art), "GunsOfTien_%s_Box%s" % (cal, art)
            icon, world = make_round(geometry, texture, case, tip, ref, cam)
            written += [(save(icon, os.path.join(OUT, "item_%s.png" % rnd)), "render of %s" % geometry),
                        (save(world, os.path.join(OUT, "worlditems/GunsOfTien/Rounds", rnd + ".png")),
                         "%s.png, case %s, tip %s" % (texture, case, tip))]
            sch = M.gom(scheme) if scheme else None
            outer = colour or A.set_hue(GOM_RED, A.hue_of(tip)[0])
            spec = dict(name=box, calibre=cal, outer=outer,
                        band=sch["band"] if sch else (236, 226, 200), text=sch["text"] if sch else (60, 24, 20),
                        load=label, sticker=sticker, side=side or "",
                        note="layout_%s in %s" % (cal, label.lower()))
            icon, world = M.make_box(spec, layout)
            written += [(save(icon, os.path.join(OUT, "item_%s.png" % box)), M.BOX_ICON),
                        (save(world, os.path.join(OUT, "worlditems/GunsOfTien/Boxes", box + ".png")),
                         "%s.png, %s" % (M.BOX_TEX, spec["note"]))]
    return written


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def contact_sheet(path, scale=6):
    cell = 32 * scale
    pad, label_h = 12, 18
    font = ImageFont.truetype(A.FONT, 13)
    names = [("762x25", a[0]) for a in TOKAREV] + [("9x18", a[0]) for a in MAKAROV]
    rounds = ["GunsOfTien_%s_Round%s" % n for n in names]
    boxes = ["GunsOfTien_%s_Box%s" % n for n in names]
    ours = lambda n: Image.open(os.path.join(OUT, "item_%s.png" % n))
    icons = ([("GoM 9x19 Round", Image.open(os.path.join(A.GOM_TEX, "item_9x19_Round_Base.png")))]
             + [(n.replace("GunsOfTien_", ""), ours(n)) for n in rounds]
             + [("GoM 9x19 Box", Image.open(os.path.join(A.GOM_TEX, M.BOX_ICON)))]
             + [(n.replace("GunsOfTien_", ""), ours(n)) for n in boxes])
    per_row = 5
    rows = (len(icons) + per_row - 1) // per_row
    width = max(pad + per_row * (cell + pad), pad + len(boxes) * (128 + 160 + pad))
    height = pad + rows * (label_h + cell + pad) + (label_h + 128 + pad) + (label_h + 256 + pad) + 230
    sheet = Image.new("RGBA", (width, height), (78, 80, 88, 255))
    d = ImageDraw.Draw(sheet)
    for i, (text, img) in enumerate(icons):
        x = pad + (i % per_row) * (cell + pad)
        y = pad + (i // per_row) * (label_h + cell + pad)
        d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        d.rectangle((x, y + label_h, x + cell - 1, y + label_h + cell - 1), fill=(96, 98, 108, 255))
        sheet.alpha_composite(img.convert("RGBA").resize((cell, cell), Image.NEAREST), (x, y + label_h))
    y = pad + rows * (label_h + cell + pad)
    for i, n in enumerate(rounds):
        x = pad + i * (128 + pad)
        d.text((x, y), n.replace("GunsOfTien_", "") + " texture", font=font, fill=(255, 255, 255, 255))
        tex = Image.open(os.path.join(OUT, "worlditems/GunsOfTien/Rounds", n + ".png"))
        sheet.alpha_composite(tex.convert("RGBA").resize((128, 128), Image.NEAREST), (x, y + label_h))
    y += label_h + 128 + pad
    for i, n in enumerate(boxes):
        x = pad + i * (128 + 160 + pad)
        d.text((x, y), n.replace("GunsOfTien_", "") + " texture / on the mesh", font=font, fill=(255, 255, 255, 255))
        tex = Image.open(os.path.join(OUT, "worlditems/GunsOfTien/Boxes", n + ".png"))
        sheet.alpha_composite(tex.convert("RGBA").resize((128, 256), Image.NEAREST), (x, y + label_h))
        sheet.alpha_composite(M.box_preview(tex, 5), (x + 128, y + label_h + 40))
    y += label_h + 256 + pad
    d.text((pad, y), "emblems (original art): SAKER falcon (7.62x25 Tokarev), TUSKER boar (9x18 Makarov)", font=font,
           fill=(255, 255, 255, 255))
    for i, em in enumerate((draw_falcon(200), draw_boar(200))):
        bg = Image.new("RGBA", (200, 200), (236, 226, 200, 255))
        bg.alpha_composite(em, ((200 - em.width) // 2, (200 - em.height) // 2))
        sheet.alpha_composite(bg, (pad + i * 220, y + label_h))
    sheet.save(path)


if __name__ == "__main__":
    for path, source in build():
        img = Image.open(path)
        print("%-64s %dx%d %s  <- %s" % (os.path.relpath(path, OUT), img.width, img.height, img.mode, source))
    if "--sheet" in sys.argv:
        i = sys.argv.index("--sheet")
        target = sys.argv[i + 1] if len(sys.argv) > i + 1 else SHEET
        contact_sheet(target)
        print("sheet", target)
