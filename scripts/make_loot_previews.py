"""Workshop previews 33-37: every gun spawner and its guns, one page per family (user, 2026-11-21: "list every spawner
and their guns in each preview. we can make the image big if needed").

Each spawner is a block: its name, where it turns up (Guns of Marz's own places and zombies, then what the Post-93
add-on adds, then what Extend Loot Areas adds), and its guns as inventory slots (the item's own 32 px icon at 2x) with
their names, the slot border coloured by the mod the gun comes from and an EXT badge on guns only that option adds.
The gun lists are read from a dump of the live tables (both mods' Loot.lua and ExtendLootAreas.lua run in lupa over
GoM's ItemSpawnerTable, option off and on; see CLAUDE.md "Workshop art"); the place texts are written here by hand
from that dump. Page 37 is GoM's replacements for the game's own guns.

    py scripts/make_loot_previews.py <spawners.json> [preview33 ...]
"""
import glob
import json
import os
import re
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_workshop_art import (AMBER, BOLD, GOM, INK, MAIN, POST, ROOT, background, font, paste_with_shadow,
                               save_under, text_layer)

GOM_MOD = os.path.dirname(GOM)                      # .../GunsOfMarz/42.16/media
MODS = os.path.join(ROOT, "Contents/mods")
VANILLA_NAMES = "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/lua/shared/Translate/EN/ItemName.json"

TIEN_C = (196, 132, 18)
POST_C = (0, 128, 140)
GOM_C = (64, 68, 74)
EXT_C = (150, 86, 0)
DARK = (28, 30, 34)
GREY = (52, 56, 62)


# ---------------------------------------------------------------------------------------------- item data
def item_data():
    icons, names = {}, {}
    files = glob.glob(GOM_MOD + "/scripts/**/*.txt", recursive=True) + glob.glob(MODS + "/*/42/media/scripts/**/*.txt",
                                                                               recursive=True)
    for f in files:
        t = open(f, encoding="utf-8", errors="replace").read()
        m = re.search(r"module\s+(\w+)", t)
        if not m:
            continue
        for im in re.finditer(r"\n\s*item\s+(\w+)\s*\{(.*?)\n\s*\}", t, re.S):
            full = m.group(1) + "." + im.group(1)
            ic = re.search(r"\bIcon\s*=\s*([\w]+)", im.group(2))
            dn = re.search(r"DisplayName\s*=\s*([^,\n]+)", im.group(2))
            if ic:
                icons[full] = ic.group(1)
            if dn:
                names[full] = dn.group(1).strip()
    for f in (GOM_MOD + "/lua/shared/Translate/EN/ItemName.json",
              MODS + "/GoMExtensionGunsOfTien/42/media/lua/shared/Translate/EN/ItemName.json",
              MODS + "/GoMExtensionGunsOfTienPost93/42/media/lua/shared/Translate/EN/ItemName.json"):
        for k, v in json.load(open(f, encoding="utf-8")).items():
            names[k] = v
    for k, v in json.load(open(VANILLA_NAMES, encoding="utf-8")).items():
        names.setdefault(k, v)
    textures = {}
    for d in (GOM, MAIN, POST):
        for p in glob.glob(os.path.join(d, "*.png")):
            textures[os.path.basename(p).lower()] = p
    return icons, names, textures


ICONS, NAMES, TEXTURES = item_data()


def icon_image(full, px):
    name = ICONS.get(full, full.split(".", 1)[1])
    path = TEXTURES.get(("item_%s.png" % name).lower())
    if not path:
        print("no icon for", full, name)
        return Image.new("RGBA", (px, px), (0, 0, 0, 0))
    return Image.open(path).convert("RGBA").resize((px, px), Image.NEAREST)


def mod_of(full):
    if full.startswith("GunsOfTienPost93.") or full == "MarzGuns.FIVESEVEN":   # the Five-seveN spawns with the add-on
        return POST_C
    if full.startswith("GunsOfTien."):
        return TIEN_C
    return GOM_C


def short_name(full):
    n = NAMES.get(full, full.split(".", 1)[1])
    n = re.sub(r"\s*\((Integrated|Folded|Deployed)[^)]*\)", "", n).upper()
    # the block's title already says what kind of gun it is
    for tail in (" SUBMACHINE GUN", " MACHINE PISTOL", " ASSAULT RIFLE", " SEMI-SHOTGUN", " AUTOMATIC SHOTGUN", " SHOTGUN",
                 " REVOLVER", " BOLT RIFLE", " BOLT-ACTION RIFLE", " SEMI-AUTO RIFLE", " LEVER-ACTION RIFLE"):
        if n.endswith(tail) and len(n) - len(tail) >= 3:
            n = n[:-len(tail)]
    return n


# ---------------------------------------------------------------------------------------------- the pages
S = "MarzGuns."
PAGES = {
    "preview33": ("LAW ENFORCEMENT", [
        ("Zombie_Police_Handgun_Spawner", "POLICE HANDGUNS",
         "Police bags, police car glove boxes and front seats, sheriffs' cars, prison guard lockers. Zombies: police, "
         "sheriffs, prison guards, SWAT, detectives, FBI agents, mobsters, hunters and park rangers", "", ""),
        ("Zombie_Police_Revolver_Spawner", "POLICE REVOLVERS",
         "Police bags and glove boxes, prison guard lockers and gun storage, revolver cases. Zombies: the same holsters "
         "as police handguns", "", ""),
        ("Zombie_Police_Shotgun_Spawner", "POLICE SHOTGUNS",
         "Police gun storage and evidence, police car trunks and rear seats, police bags, prison armouries and gun "
         "storage, shotgun cases. Zombies: police, sheriffs, SWAT, park rangers, private militia", "", ""),
        ("Zombie_Police_Rifle_Spawner", "POLICE AND SWAT RIFLES", "Zombies: SWAT",
         "SWAT and police gun storage, police car trunks and rear seats; police, sheriffs, park rangers and militia", ""),
        ("Zombie_Police_SemiRifle_Spawner", "POLICE MARKSMAN RIFLES",
         "Zombies: SWAT, police, sheriffs, park rangers, private militia", "", ""),
        ("Zombie_Police_SMG_Spawner", "POLICE AND SWAT SUBMACHINE GUNS",
         "SWAT van trunks and rear seats, police bags, prison riot storage. Zombies: SWAT", "SWAT gun storage",
         "Police gun storage, police car trunks and rear seats, police zombies"),
        ("Zombie_SWAT_Handgun_Spawner", "SWAT HANDGUNS",
         "SWAT van glove boxes and front seats. Zombies: SWAT; with Undead Survivors its preppers", "", ""),
        ("Zombie_SWAT_Shotgun_Spawner", "SWAT SHOTGUN", "SWAT van trunks, prison armouries. Zombies: SWAT", "",
         "SWAT gun storage"),
    ]),
    "preview34": ("MILITARY", [
        ("World_Army_Rifle_Spawner", "ARMY RIFLES",
         "Army gun storage and the bunker, army trucks, ALICE packs, military rifle cases, late homes, late bandit bags",
         "", ""),
        ("Zombie_Army_Rifle_Spawner", "ARMY RIFLES ON SOLDIERS", "Zombies: soldiers in camouflage", "",
         "Most soldiers carry a gun; also private militia and late survivalists"),
        ("World_Army_Heavy_Spawner", "HEAVY ARMY WEAPONS", "Army gun storage, heavy army trucks", "",
         "The bunker, light army trucks, soldiers' backs"),
        ("Zombie_Army_Handgun_Spawner", "ARMY HANDGUNS",
         "Army glove boxes and front seats, army lockers, the bunker's lockers, ALICE packs, pistol cases. Zombies: "
         "soldiers, drill instructors, soldiers in dress uniform, SWAT", "", ""),
        ("Zombie_Army_SemiRifle_Spawner", "ARMY SNIPER RIFLES", "Zombies: snipers in ghillie suits", "",
         "Every ghillie sniper carries one"),
        ("Zombie_Mercenary_Rifles_Spawner", "MERCENARY RIFLES",
         "Zombies, with Undead Survivors: its mercenaries and preppers", "", ""),
        ("Zombie_Mercenary_Sniper_Spawner", "MERCENARY SNIPER RIFLES", "Zombies, with Undead Survivors: its headhunters",
         "", ""),
    ]),
    "preview35": ("CIVILIAN", [
        ("Zombie_Civilian_Handgun_Spawner", "CIVILIAN HANDGUNS",
         "Homes' gun cabinets, pawn shops, pistol cases, plank stashes, early bandit bags, rarely school lockers. "
         "Zombies: bandits, bank robbers, bikers, bounty hunters, hunters, survivalists, private militia", "", ""),
        ("Zombie_Civilian_Revolver_Spawner", "CIVILIAN REVOLVERS",
         "Bar counters, handbags, pawn shops, plank stashes, park rangers' cars and storage, revolver cases, rarely school "
         "lockers. Zombies: the same holsters as civilian handguns", "", ""),
        ("Zombie_Civilian_Rifle_Spawner", "CIVILIAN RIFLES",
         "Mid-game homes, survivor bags. Zombies: private militia, bounty hunters, bandits, survivalists", "", ""),
        ("Zombie_Civilian_SemiRifle_Spawner", "CIVILIAN HUNTING RIFLES",
         "Homes' gun cabinets, gun store rifles, park ranger storage, rifle cases", "",
         "Zombies: hunters, early survivalists"),
        ("Zombie_Hunter_SemiRifles_Spawner", "HUNTERS' RIFLES",
         "Hunting lockers, garages, camping stores, hunters' and park rangers' trucks and storage, prison gun storage, "
         "mid-game homes, rifle cases. Zombies: hunters, private militia, bandits, survivalists", "",
         "Most hunters and park rangers carry a gun"),
        ("Zombie_Civilian_Shotgun_Spawner", "CIVILIAN SHOTGUNS",
         "Homes' gun cabinets, gun store shotguns, bar counters, shotgun cases, survivor bags. Zombies: bounty hunters, "
         "bandits, survivalists", "", ""),
        ("World_Import_Pistol_Spawner", "IMPORTED PISTOLS",
         "Gun store pistols, pawn shops, police evidence, drug labs and shacks, plank stashes, bandits' and luxury cars",
         "", "Zombies' holsters: bandits, bank robbers, bikers, bounty hunters, hunters, survivalists, private militia"),
        ("World_Import_Rifle_Spawner", "IMPORTED RIFLES",
         "Gun stores, special pawn shop guns, police evidence, survivalists' trucks, rifle cases, late homes",
         "Ordinary pawn shops; survivalist zombies", "Zombies: private militia, bounty hunters, more survivalists"),
        ("World_Short_SMG_Spawner", "SHORT SUBMACHINE GUNS",
         "Gun stores, special pawn shop guns, survivalists' glove boxes, bandit bags, mid-game homes", "",
         "Drug labs and shacks, plank stashes; zombies' shoulder holsters (bandits, bank robbers, bikers, bounty "
         "hunters, hunters, survivalists)"),
    ]),
    "preview36": ("CRIMINAL, RUSSIAN AND COLLECTORS'", [
        ("Zombie_Crime_Rifle_Spawner", "CRIMINALS' GUNS",
         "Bandit bags, special pawn shop guns, plank stashes. Zombies: bank robbers, bounty hunters, bandits, "
         "survivalists; with Undead Survivors its mercenaries", "", "Most bandits carry a gun"),
        ("Zombie_Survivalist_Rifle_Spawner", "SURVIVALISTS' RIFLES",
         "Survivor bags, survivalists' glove boxes and truck beds", "", ""),
        ("World_Russian_Rifle_Spawner", "RUSSIAN RIFLES",
         "Drug labs, drug money stashes and shacks, police evidence, survivalists' and bandits' vehicles, late homes and "
         "safehouse bins, plank stashes", "",
         "Zombies: bank robbers and bandits, mid and late survivalists, private militia, bounty hunters"),
        ("World_Anachronistic_Spawner", "POST-1993 GUNS",
         "Late homes and safehouse bins, late survivor and bandit bags", "",
         "Gun stores, special pawn shop guns, SWAT gun storage; the G36s, Benelli, Rhino and MP-412 also with police, "
         "SWAT and civilian zombies"),
        ("World_Surplus_Rifle_Spawner", "SURPLUS RIFLES",
         "Army surplus stores, garages, gun store rifles, pawn shops, hunters' and trappers' homes", "", ""),
        ("World_Oldies_Spawner", "WORLD WAR GUNS",
         "Gun store cases and rifles, pawn shops, safehouse bins, mid-game homes. Zombies: private militia, hunters", "",
         "Zombies: bounty hunters, late survivalists"),
        ("World_Big_Game_Rifle_Spawner", "BIG GAME RIFLE",
         "Adventurers' cars, hunting lockers, gun store rifles, special pawn shop guns, antique shops, rarely classy "
         "wardrobes", "", "Hunters' backs"),
        ("Zombie_Cowboy_Revolver_Spawner", "COWBOY REVOLVERS",
         "Special pawn shop guns, sheriffs' cars, park rangers' glove boxes and storage, revolver cases. Zombies: Wild "
         "West costumes", "", ""),
        ("Zombie_Cowboy_Rifles_Spawner", "COWBOY RIFLES", "Pawn shops. Zombies: Wild West costumes, bandits, survivalists",
         "", "Gun store rifles, hunting lockers, park ranger storage, mid-game homes"),
    ]),
}

# GoM's replacements for the game's own guns (VanillaReplacerTable.VanillaWeaponMap, with its sandbox Vanilla Weapon
# Replacement on, the default): { vanilla gun, where the game puts it }
REPLACEMENTS = [
    ("Base.Pistol", "Homes, police, SWAT and army storage, gun stores, drug labs, police and civilian zombies"),
    ("Base.Pistol2", "Homes, police and SWAT storage, gun stores, drug labs"),
    ("Base.Pistol3", "Homes, gun stores, pawn shops, drug labs, stashes"),
    ("Base.Revolver", "Homes, police storage, gun stores, park rangers"),
    ("Base.Revolver_Long", "Homes, police storage, gun stores, park rangers"),
    ("Base.Revolver_Short", "Homes, police, gun stores, drug labs, security desks, late safehouses"),
    ("Base.Shotgun", "Homes, closets and wardrobes, police storage, gun stores, hunters"),
    ("Base.ShotgunSawnoff", "Homes, bar counters, drug labs, police evidence"),
    ("Base.DoubleBarrelShotgun", "Homes, closets and wardrobes, gun stores, hunters"),
    ("Base.DoubleBarrelShotgunSawnoff", "Homes, bar counters, drug labs, police evidence"),
    ("Base.JS3T_Shotgun", "Army, police and SWAT storage, homes, gun stores, pawn shops"),
    ("Base.AssaultRifle", "Army and SWAT storage, homes, drug labs, special pawn shop guns"),
    ("Base.AssaultRifle2", "Homes, garages, gun stores, pawn shops"),
    ("Base.JS14_Rifle", "Homes, closets and wardrobes, garages, gun stores, police storage, drug labs"),
    ("Base.HuntingRifle", "Homes, closets and wardrobes, gun stores, hunting lockers, park rangers"),
    ("Base.VarmintRifle", "Homes, closets and wardrobes, gun stores, hunting lockers, park rangers"),
    ("Base.MSR7T_Rifle", "Army and SWAT storage, homes, gun stores"),
    ("Base.L92_Carbine", "Homes, closets and wardrobes, gun stores, hunting lockers"),
    ("Base.L94_Rifle", "Homes, closets and wardrobes, gun stores, hunting lockers"),
    ("Base.TrapperCarbine", "Homes, closets and wardrobes, gun stores, hunting lockers, drug labs"),
]


# ---------------------------------------------------------------------------------------------- drawing
W = 1024
MARGIN = 34
CELL_W, SLOT, ICON = 92, 70, 64
PER_ROW = (W - 2 * MARGIN) // CELL_W


def wrap(d, text, f, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if d.textlength(test, font=f) <= width or not line:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def draw_cells(layer, d, guns, ext, y, name_f, badge_f, x0=MARGIN, width=W - 2 * MARGIN):
    per_row = max(1, width // CELL_W)
    left = x0 + (width - per_row * CELL_W) // 2 if len(guns) >= per_row else x0
    rows = (len(guns) + per_row - 1) // per_row
    slots = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(slots)
    row_h = SLOT + 50
    for n, g in enumerate(guns):
        cx = left + (n % per_row) * CELL_W + CELL_W // 2
        top = y + (n // per_row) * row_h
        sx = cx - SLOT // 2
        sd.rounded_rectangle((sx, top, sx + SLOT, top + SLOT), radius=6, fill=(255, 255, 255, 60),
                             outline=mod_of(g) + (255,), width=3)
        ic = icon_image(g, ICON)
        slots.alpha_composite(ic, (sx + (SLOT - ICON) // 2, top + (SLOT - ICON) // 2))
        if g in ext:
            bw = int(sd.textlength("EXT", font=badge_f)) + 10
            sd.rounded_rectangle((sx + SLOT - bw + 4, top - 6, sx + SLOT + 4, top + 12), radius=4, fill=INK + (235,))
            sd.text((sx + SLOT - bw / 2 + 4, top + 3), "EXT", font=badge_f, fill=AMBER + (255,), anchor="mm")
        for m, line in enumerate(wrap(d, short_name(g), name_f, CELL_W - 4)[:3]):
            sd.text((cx, top + SLOT + 5 + m * 14), line, font=name_f, fill=DARK + (255,), anchor="ma")
    paste_with_shadow(layer, slots, (0, 2), 2, 110)
    return y + rows * row_h


def draw_block(layer, d, y, title_text, guns, ext, where, post, extend, fonts, x0=MARGIN, width=W - 2 * MARGIN):
    head_f, text_f, tag_f, name_f, badge_f = fonts
    size = 24
    while size > 14 and d.textlength(title_text, font=head_f) > width:     # a title steps down to fit its column
        size -= 1
        head_f = font(BOLD, size, b"Bold")
    d.text((x0, y), title_text, font=head_f, fill=DARK)
    y += 30
    for label, text, colour in (("", where, GREY), ("POST-93 ADD-ON: ", post, POST_C), ("EXTEND LOOT AREAS: ", extend, EXT_C)):
        if not text:
            continue
        for line in wrap(d, label + text, text_f, width):
            if label and line.startswith(label):
                d.text((x0, y), label, font=tag_f, fill=colour)
                d.text((x0 + d.textlength(label, font=tag_f), y), line[len(label):], font=text_f, fill=colour)
            else:
                d.text((x0, y), line, font=text_f, fill=colour)
            y += 19
    y += 10
    y = draw_cells(layer, d, guns, ext, y, name_f, badge_f, x0, width)
    d.line([(x0, y + 10), (x0 + width, y + 10)], fill=(60, 64, 70, 90), width=1)
    return y + 28


def legend(d, y, f):
    items = (("GUNS OF MARZ", GOM_C), ("GUNS OF TIEN", TIEN_C), ("POST-93 ADD-ON", POST_C))
    widths = [26 + d.textlength(t, font=f) for t, _ in items]
    ext_text = "ONLY WITH EXTEND LOOT AREAS"
    total = sum(widths) + 26 + 40 + d.textlength(ext_text, font=f) + 3 * 30
    x = (W - total) / 2
    for (t, c), w in zip(items, widths):
        d.rounded_rectangle((x, y, x + 18, y + 18), radius=3, fill=(255, 255, 255, 60), outline=c + (255,), width=3)
        d.text((x + 26, y + 9), t, font=f, fill=DARK, anchor="lm")
        x += w + 30
    d.rounded_rectangle((x, y, x + 34, y + 18), radius=4, fill=INK + (235,))
    d.text((x + 17, y + 9), "EXT", font=f, fill=AMBER, anchor="mm")
    d.text((x + 42, y + 9), ext_text, font=f, fill=DARK, anchor="lm")


def page_fonts():
    return (font(BOLD, 24, b"Bold"), font(BOLD, 15, b"SemiBold"), font(BOLD, 15, b"Bold"), font(BOLD, 11, b"Bold"),
            font(BOLD, 11, b"Bold"))


NOTE = "Each spawner gives one of its guns at random, with magazines and ammunition, scaled by Guns of Marz's loot multiplier"


def one_line(d, y, text):
    """One centred line (user): the font steps down until it fits."""
    size = 15
    while size > 9 and d.textlength(text, font=font(BOLD, size, b"SemiBold")) > W - 2 * MARGIN:
        size -= 1
    d.text((W // 2, y), text, font=font(BOLD, size, b"SemiBold"), fill=GREY, anchor="ma")
    return y + 19


def render(path, subtitle, blocks, columns=1, intro=None, note=NOTE):
    tall = 6000
    layer = Image.new("RGBA", (W, tall), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fonts = page_fonts()
    layer.alpha_composite(text_layer(layer.size, (W // 2, 40), "WHERE THE GUNS ARE FOUND", font(BOLD, 40, b"Bold"),
                                     DARK + (255,), anchor="mm", spacing=3))
    layer.alpha_composite(text_layer(layer.size, (W // 2, 80), subtitle, font(BOLD, 20, b"Bold"), GREY + (255,),
                                     anchor="mm", spacing=3))
    legend(d, 104, font(BOLD, 13, b"Bold"))
    y = 146
    if intro:
        y = one_line(d, y, intro) + 12
    gap = 36
    width = (W - 2 * MARGIN - gap * (columns - 1)) // columns
    tops = [y] * columns
    for b in blocks:                                  # each block into the shortest column
        c = tops.index(min(tops))
        tops[c] = draw_block(layer, d, tops[c], *b, fonts, MARGIN + c * (width + gap), width)
    y = one_line(d, max(tops), note)
    h = y + 24
    page = background((W, h)).convert("RGBA")
    page.alpha_composite(layer.crop((0, 0, W, h)))
    save_under(page.convert("RGB"), path)


def rare_spawners():
    """The spawners ExtendLootAreas.lua's RARE_WEIGHTS raise."""
    src = open(os.path.join(MODS, "GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/ExtendLootAreas.lua"),
               encoding="utf-8").read()
    block = src[src.index("local RARE_WEIGHTS = {"):]
    block = block[:block.index("\n}")]
    return set(re.findall(r'\[G \.\. "(\w+)"\]', block))


RARE = rare_spawners()


def spawner_blocks(data, entries):
    blocks = []
    for key, title_text, where, post, extend in entries:
        if key in RARE:
            extend = "Turns up more often" + ("; " + extend[0].lower() + extend[1:] if extend else "")
        d = data[S + key]
        guns = d["guns"] + d["ext_guns"]
        blocks.append((title_text, guns, set(d["ext_guns"]), where, post, extend))
    return blocks


def replacement_blocks(rep_map, ext_map):
    blocks = []
    for vanilla, where in REPLACEMENTS:
        guns = rep_map.get(vanilla, [])
        ext = ext_map.get(vanilla, [])
        blocks.append((NAMES.get(vanilla, vanilla).upper(), guns + ext, set(ext), where, "", ""))
    return blocks


def main():
    data = json.load(open(sys.argv[1]))
    reps = json.load(open(os.path.join(os.path.dirname(sys.argv[1]), "replacements.json")))
    want = [a for a in sys.argv[2:]] or list(PAGES) + ["preview37"]
    for name, (subtitle, entries) in PAGES.items():
        if name in want:
            render(os.path.join(ROOT, name + ".png"), subtitle, spawner_blocks(data, entries))
    if "preview37" in want:
        render(os.path.join(ROOT, "preview37.png"), "IN PLACE OF THE GAME'S OWN GUNS",
               replacement_blocks(reps["base"], reps["ext"]), columns=2,
               intro="Guns of Marz turns each of the game's own guns into one of these, wherever the game puts it, zombies included",
               note="Only while Guns of Marz's Vanilla Weapon Replacement is on (the default); each gives one of its guns at random")


if __name__ == "__main__":
    main()
