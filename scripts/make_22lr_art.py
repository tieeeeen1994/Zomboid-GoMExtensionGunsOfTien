#!/usr/bin/env python3
"""Icons and world-model textures for the .22 LR round and box of GoM Extension: Guns of Tien (gen_scripts.py
ammo_22lr()).

Everything is derived from Guns of Marz's own PNGs and meshes (read only) with the helpers of make_art.py and
post93/make_ammo_art.py; nothing is hand-edited and every run writes the same bytes.

Round. GoM ships the mesh (Rounds.fbx node 22_Round, textured Pistol_Light_Round_Base by its MarzGuns.22_Round_Base
model: an orange case and a black bullet) but no icon and no .22 item. Ours is a 40 gr lead round nose in a brass case:
  * World texture = Pistol_Standard_Round_Base (GoM's brass, as its 9x19 / .38 / .30-30) with the bullet repainted
    dull lead grey (make_art.paint: flat colour that keeps the texel's shading). The 22_Round mesh's bullet and case
    share one UV island (a heeled bullet is as wide as its case), so make_art.bullet_fractions cannot tell them apart;
    the bullet is where GoM's own .22 texture is black, plus Pistol_Standard's own bullet texels around it.
  * Icon = a render of the mesh with GoM's 9x19 icon camera, colour and shading learned from GoM's
    item_9x19_Round_Base.png against Pistol_Standard_Round_Base.png (make_ammo_art's renderer, re-referenced; its
    5.56 reference gave a too-orange brass).
Box. A 50-round HandGunAmmoBox from GoM's 9x19_Box with make_ammo_art.make_box (its lid flap and tray), the sleeve
redrawn in a layout of its own (layout_22lr): a yellow face framed in green, a snarling gold wolf's head (draw_wolf,
original art) on a green roundel where GoM's 9x19 box has its gold eagle, a huge ".22", a green "LONG RIFLE" ribbon,
the long side green; "40 GR LEAD" on the lid sticker.

Usage:  python3 scripts/make_22lr_art.py              write every output
        python3 scripts/make_22lr_art.py --sheet [P]  also write a contact sheet (default docs/22lr_art_sheet.png)
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "post93"))
import make_art as A  # noqa: E402
import make_ammo_art as M  # noqa: E402  (round renderer, box builder)

ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media/textures")
SHEET = os.path.join(ROOT, "docs/22lr_art_sheet.png")
ROUND = "GunsOfTien_22LR_Round"
BOX = "GunsOfTien_22LR_Box"

LEAD = (112, 114, 118)              # dull lead grey (bare lead with its lubricant)
CASE_TEXTURE = "Pistol_Standard_Round_Base"
GOM_22_TEXTURE = "Pistol_Light_Round_Base"
ROUND_CAMERA = A.CAMERAS["item_9x19_Round_Base.png"]

M.CALIBRES["22LR"] = dict(text=".22", panel=(226, 196, 64), ink=(24, 40, 20))
BOX_SPEC = dict(name=BOX, calibre="22LR", outer=(46, 112, 64), band=(236, 224, 150), text=(28, 72, 36),
                load="Long Rifle", sticker="40 GR LEAD", note="layout_22lr: yellow face, wolf roundel, .22, LONG RIFLE ribbon")

def draw_wolf(size=400, gold=(232, 182, 58), shade=(196, 140, 40), dark=(84, 50, 12)):
    """The .22 LR box's emblem in the place GoM's 9x19 box has its gold eagle (user, 2026-11-13: "we can use an animal
    emblem like the 9mm box... use another emblem"): a snarling gold wolf's head, drawn here (original art, nothing
    of the game's), 4x supersampled."""
    k = 4
    W = H = 200
    img = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    D, G, S = dark + (255,), gold + (255,), shade + (255,)
    head = [(10, 92), (30, 80), (60, 70), (88, 60), (106, 48), (116, 40), (124, 4), (142, 32), (150, 18), (158, 44),
            (172, 56), (186, 80), (194, 110), (198, 142), (184, 148), (192, 160), (172, 164), (178, 178), (156, 174),
            (152, 190), (136, 176), (116, 164), (98, 150), (76, 142), (52, 140), (32, 136), (30, 128), (50, 120),
            (90, 110), (36, 104), (18, 102)]
    d.polygon(P(head), fill=G)
    # shading: lower jaw, throat and neck, the far ear
    d.polygon(P([(50, 120), (90, 110), (120, 120), (150, 134), (198, 142), (184, 148), (192, 160), (172, 164),
                 (178, 178), (156, 174), (152, 190), (136, 176), (116, 164), (98, 150), (76, 142), (52, 140),
                 (32, 136), (30, 128)]), fill=S)
    d.polygon(P([(142, 32), (150, 18), (158, 44), (150, 46)]), fill=S)
    d.polygon(P(head), outline=D, width=3 * k)
    # open mouth, fangs
    d.polygon(P([(36, 104), (90, 110), (50, 120), (30, 128), (26, 114)]), fill=(76, 16, 14, 255))
    for tri in ([(30, 104), (38, 104), (34, 117)], [(52, 106), (58, 107), (55, 115)], [(70, 108), (75, 108), (72, 114)],
                [(36, 126), (43, 123), (37, 113)], [(56, 118), (61, 116), (57, 110)]):
        d.polygon(P(tri), fill=(252, 248, 232, 255))
    # nose, brow and slanted eye with a glint, inner ear
    d.polygon(P([(6, 90), (18, 85), (21, 96), (9, 98)]), fill=D)
    d.line(P([(80, 66), (104, 58), (118, 60)]), fill=D, width=4 * k, joint="curve")
    d.polygon(P([(90, 76), (116, 64), (112, 76), (98, 80)]), fill=D)
    d.polygon(P([(104, 70), (110, 68), (108, 72)]), fill=(255, 236, 120, 255))
    d.polygon(P([(126, 14), (138, 36), (128, 42), (121, 38)]), fill=D)
    # ruff: short strokes along the back of the neck
    for line in ([(160, 70), (176, 84)], [(168, 96), (186, 108)], [(170, 122), (190, 132)], [(126, 96), (150, 104)]):
        d.line(P(line), fill=D, width=3 * k)
    return img.resize((size, size), Image.LANCZOS)


def layout_22lr(img, spec, cal):
    """A layout unlike the 4.6x30 and 5.7x28 boxes (post93/make_ammo_art.py): a yellow face in a green frame, the
    wolf on a green roundel ringed in gold at the top, a huge green ".22", a green "LONG RIFLE" ribbon at the tray
    end; the long side green with the name in yellow."""
    green, yellow, ink = spec["outer"], cal["panel"], cal["ink"]
    gold = (232, 182, 58)
    M.fill(img, M.FACE, green)
    M.fill(img, (2, 24, 45, 89), yellow)
    d = ImageDraw.Draw(img)
    d.ellipse((8, 26, 39, 55), fill=M.shade(green, 0.8) + (255,), outline=gold + (255,), width=2)
    M.picture(img, draw_wolf(), (11, 29, 36, 52))
    M.text(img, (4, 57, 43, 76), ".22", ink)
    M.fill(img, (0, 79, 47, 88), green)
    M.text(img, (3, 80, 44, 87), "LONG RIFLE", yellow)
    M.fill(img, M.SIDE, green)
    M.text(img, (50, 26, 61, 88), ".22 LONG RIFLE", yellow, True)


def use_9x19_reference():
    """Point make_ammo_art's icon model at GoM's 9x19 icon and its brass texture (the same case texture we use)."""
    M.REF_ICON = "item_9x19_Round_Base.png"
    M.REF_GEOMETRY = "9x19_Round"
    M.REF_TEXTURE = CASE_TEXTURE
    M._model = None


def bullet_texels():
    """Texels of the 22_Round's bullet: black in GoM's .22 texture, or Pistol_Standard's own (yellow, no blue)
    bullet texels in the same top band, grown by one texel into the gutter."""
    gom22 = Image.open(os.path.join(A.GOM_ROUNDS, GOM_22_TEXTURE + ".png")).convert("RGBA").load()
    case = Image.open(os.path.join(A.GOM_ROUNDS, CASE_TEXTURE + ".png")).convert("RGBA").load()
    band = 36                                            # the bullet island lies in rows 0..35 of 128
    cells = {(x, y) for y in range(band) for x in range(128) if gom22[x, y][3] > 0 and A.lum(gom22[x, y]) < 70}
    # Pistol_Standard's bullet reaches a few texels further right; its primer disc (top right, also B ~ 0) is not it
    cells |= {(x, y) for y in range(band) for x in range(26, 103)
              if case[x, y][3] > 0 and case[x, y][2] < 12 and (x < 90 or y >= 17)}
    grown = set(cells)
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < 128 and 0 <= y + dy < band:
                grown.add((x + dx, y + dy))
    return grown


def make_round():
    use_9x19_reference()
    tex = Image.open(os.path.join(A.GOM_ROUNDS, CASE_TEXTURE + ".png")).convert("RGBA")
    px = tex.load()
    cells = sorted(bullet_texels())
    ref = A._median([A.lum(px[c]) for c in cells if px[c][3] > 200])
    world = tex.copy()
    wp = world.load()
    for c in cells:
        if wp[c][3]:
            wp[c] = A.paint(wp[c], LEAD, ref, 1.0)
    return M.render_round_icon("22_Round", world, ROUND_CAMERA), world


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def build():
    icon, world = make_round()
    written = [(save(icon, os.path.join(OUT, "item_%s.png" % ROUND)), "render of 22_Round"),
               (save(world, os.path.join(OUT, "worlditems/GunsOfTien/Rounds", ROUND + ".png")),
                CASE_TEXTURE + ".png, bullet in lead grey")]
    icon, world = M.make_box(BOX_SPEC, layout_22lr)
    written += [(save(icon, os.path.join(OUT, "item_%s.png" % BOX)), M.BOX_ICON),
                (save(world, os.path.join(OUT, "worlditems/GunsOfTien/Boxes", BOX + ".png")),
                 "%s.png, %s" % (M.BOX_TEX, BOX_SPEC["note"]))]
    return written


def contact_sheet(path, scale=6):
    cell = 32 * scale
    pad, label_h = 12, 18
    font = ImageFont.truetype(A.FONT, 13)
    icons = [("GoM 9x19 Round", Image.open(os.path.join(A.GOM_TEX, "item_9x19_Round_Base.png"))),
             (".22 LR Round", Image.open(os.path.join(OUT, "item_%s.png" % ROUND)))
             , ("GoM 9x19 Box", Image.open(os.path.join(A.GOM_TEX, M.BOX_ICON))),
             (".22 LR Box", Image.open(os.path.join(OUT, "item_%s.png" % BOX)))]
    round_tex = Image.open(os.path.join(OUT, "worlditems/GunsOfTien/Rounds", ROUND + ".png"))
    box_tex = Image.open(os.path.join(OUT, "worlditems/GunsOfTien/Boxes", BOX + ".png"))
    width = pad + len(icons) * (cell + pad)
    height = pad + label_h + cell + pad + label_h + 256 + pad
    sheet = Image.new("RGBA", (max(width, pad + 256 + pad + 128 + pad + 256 + pad), height), (78, 80, 88, 255))
    d = ImageDraw.Draw(sheet)
    x = pad
    for text, img in icons:
        d.text((x, pad), text, font=font, fill=(255, 255, 255, 255))
        d.rectangle((x, pad + label_h, x + cell - 1, pad + label_h + cell - 1), fill=(96, 98, 108, 255))
        sheet.alpha_composite(img.convert("RGBA").resize((cell, cell), Image.NEAREST), (x, pad + label_h))
        x += cell + pad
    y = pad + label_h + cell + pad
    d.text((pad, y), "round texture", font=font, fill=(255, 255, 255, 255))
    sheet.alpha_composite(round_tex.convert("RGBA").resize((256, 256), Image.NEAREST), (pad, y + label_h))
    x = pad + 256 + pad
    d.text((x, y), "box texture / on the mesh", font=font, fill=(255, 255, 255, 255))
    sheet.alpha_composite(box_tex.convert("RGBA").resize((128, 256), Image.NEAREST), (x, y + label_h))
    sheet.alpha_composite(M.box_preview(box_tex, 8), (x + 128 + pad, y + label_h))
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
