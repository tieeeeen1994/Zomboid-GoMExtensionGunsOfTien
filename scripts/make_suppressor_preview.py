"""Workshop preview41 (3.20.0): every suppressor and the guns it fits (user, 2026-11-23: "a preview of being able to
attach suppressors to most guns").

One block per calibre family: its cans (icons beside the title), the mount it needs, and every gun it can really be
fitted on as inventory slots, bordered by the mod the gun comes from (make_loot_previews.py's slots); a last block for
the guns with one built in. The lists come from the attachment audit, which runs every mod's Lua in lupa and counts a
can as fitting only when its mount device fits the gun too:

    py scripts/attachment_audit.py --suppressors <dir>/suppressors.json > <dir>/audit.md
    py scripts/make_suppressor_preview.py <dir>/suppressors.json
"""
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_workshop_art import BOLD, ROOT, background, font, paste_with_shadow, save_under, text_layer  # noqa: E402
import make_loot_previews as mlp  # noqa: E402
from make_loot_previews import (DARK, GOM_C, GREY, MARGIN, POST_C, TIEN_C, W, draw_block, icon_image,  # noqa: E402
                                mod_of, one_line, page_fonts, short_name)

# not guns of their own: the underbarrel launchers' weapon items, and the Uzi's two-handed hold (the Uzi swapped)
LEFT_OUT = {"MarzGuns.M79", "MarzGuns.M203_Weapon", "MarzGuns.CAR15_M203_Weapon", "GunsOfTienPost93.GROZAGL_GP25",
            "GunsOfTien.UZI_2H"}
TAILS = (" SEMI-AUTOMATIC RIFLE", " SNIPER RIFLE", " LIGHT MACHINE GUN", " CIVILIAN RIFLE", " BATTLE RIFLE",
         " MARKSMAN RIFLE", " ASSAULT RIFLE")


def gun_name(g):
    """make_loot_previews' short name without the kind the page does not need ("MINI-14 SEMI-AUTOMATIC RIFLE");
    the two HK417s keep theirs."""
    n = short_name(g).replace(" ASSAULT RIFLE WITH ", " WITH ")
    if g.startswith("GunsOfTienPost93.HK417"):
        return n.replace(" RIFLE", "")
    for tail in TAILS:
        if n.endswith(tail):
            return n[:-len(tail)]
    return n
P = "GunsOfTienPost93."
# (title, cans, where, Post-93 line)
FAMILIES = [
    ("9X19MM", ["MarzGuns.M&P_Suppressor", "MarzGuns.Shh9_Suppressor", "GunsOfTien.Mk9_Suppressor"],
     "M&P, Shh9 or AWC Mk9 on the 9x19mm muzzle mount", "the AUG Para, UMP9 and 9mm Vectors"),
    ("5.56MM", ["MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor"],
     "MKI or NDR on the AR muzzle mount", "the SCAR-L, HK416, AUG A3 and MDRx .223"),
    ("AK", ["MarzGuns.PBS-1_Suppressor"], "PBS-1 on the AK muzzle mount", "the Groza-1 and Groza-2"),
    (".45 ACP", ["MarzGuns.P45_Suppressor"], "P45 on the .45 muzzle mount", "the UMP45 and Vector .45s"),
    ("7.62X51MM", [P + "SCARH_Suppressor"], "", "SOCOM762-RC on the SCAR-H's muzzle mount"),
    ("4.6X30MM AND 5.7X28MM", [P + "MP7_Suppressor", P + "P90_Suppressor", P + "FIVESEVEN_Suppressor"], "",
     "Rotex-II, SP90 and SFN-57 on their muzzle mounts"),
]


def order(guns):
    rank = {GOM_C: 0, TIEN_C: 1, POST_C: 2}
    return sorted(set(guns) - LEFT_OUT, key=lambda g: (rank[mod_of(g)], gun_name(g)))


def block_icons(layer, cans, x_right, y):
    x = x_right
    for can in reversed(cans):
        ic = icon_image(can, 32)
        x -= 32
        paste_with_shadow(layer, _placed(layer.size, ic, (x, y - 2)), (0, 2), 2, 110)
        x -= 4


def _placed(size, im, xy):
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(im, xy)
    return out


def legend(d, y, f):
    items = (("GUNS OF MARZ", GOM_C), ("GUNS OF TIEN", TIEN_C), ("POST-93 ADD-ON", POST_C))
    widths = [26 + d.textlength(t, font=f) for t, _ in items]
    x = (W - sum(widths) - 30 * (len(items) - 1)) / 2
    for (t, c), w in zip(items, widths):
        d.rounded_rectangle((x, y, x + 18, y + 18), radius=3, fill=(255, 255, 255, 60), outline=c + (255,), width=3)
        d.text((x + 26, y + 9), t, font=f, fill=DARK, anchor="lm")
        x += w + 30


def main():
    data = json.load(open(sys.argv[1]))
    cans, built_in = data["cans"], data["built_in"]
    guns = [g for g in data["guns"] if g not in LEFT_OUT]
    taking = ({g for gs in cans.values() for g in gs} | set(built_in)) - LEFT_OUT
    main_guns = [g for g in guns if not g.startswith(P)]
    main_taking = {g for c, gs in cans.items() if not c.startswith(P) for g in gs if not g.startswith(P)} \
        | {g for g in built_in if not g.startswith(P)}
    main_taking -= LEFT_OUT
    print("main mod: %d of %d, with Post-93: %d of %d" % (len(main_taking), len(main_guns), len(taking), len(guns)))

    tall = 4000
    layer = Image.new("RGBA", (W, tall), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fonts = page_fonts()
    layer.alpha_composite(text_layer(layer.size, (W // 2, 40), "SUPPRESSORS", font(BOLD, 40, b"Bold"), DARK + (255,),
                                     anchor="mm", spacing=3))
    layer.alpha_composite(text_layer(
        layer.size, (W // 2, 80), "%d OF %d GUNS TAKE ONE  ·  %d OF %d WITH THE POST-93 ADD-ON"
        % (len(main_taking), len(main_guns), len(taking), len(guns)), font(BOLD, 20, b"Bold"), GREY + (255,),
        anchor="mm", spacing=3))
    legend(d, 104, font(BOLD, 13, b"Bold"))
    y = one_line(d, 146, "Only where the real gun takes one  ·  each needs its calibre's muzzle mount first") + 12

    blocks = []
    for title, family, where, post in FAMILIES:
        fits = order(g for c in family for g in cans.get(c, []))
        blocks.append((title, family, fits, where, post))
    blocks.append(("BUILT IN", [], order(built_in), "No mount needed", ""))
    mlp.short_name = gun_name                     # draw_cells names the slots through the module's global
    columns, gap = 2, 36
    width = (W - 2 * MARGIN - gap * (columns - 1)) // columns
    tops = [y] * columns
    for title, family, fits, where, post in blocks:
        c = tops.index(min(tops))
        x0 = MARGIN + c * (width + gap)
        block_icons(layer, family, x0 + width, tops[c])
        tops[c] = draw_block(layer, d, tops[c], title, fits, set(), where, post, "", fonts, x0, width)
    y = one_line(d, max(tops), "Every suppressor: 70% quieter, 10% less damage, no muzzle flash")
    h = y + 24
    page = background((W, h)).convert("RGBA")
    page.alpha_composite(layer.crop((0, 0, W, h)))
    save_under(page.convert("RGB"), os.path.join(ROOT, "preview41.png"))
    print("wrote preview41.png", page.size)


if __name__ == "__main__":
    main()
