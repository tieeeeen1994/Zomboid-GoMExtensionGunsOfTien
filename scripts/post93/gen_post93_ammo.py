"""Writes the ammunition scripts and their translations of GoM Extension: Guns of Tien - Post-93.

Run: python3 scripts/post93/gen_post93_ammo.py. The table below is the one source of truth; registries.lua and the Lua
profiles use the same full types. Gun items and their names are written elsewhere (gen_post93_guns.py).
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Contents', 'mods',
                    'GoMExtensionGunsOfTienPost93', '42', 'media')
MODULE = 'GunsOfTienPost93'
ART = 'GunsOfTienPost93_'

# Real cartridge weights: 4.6x30 about 6.6 g, 5.7x28 about 6.0 g, on GoM's scale (AmmoPatch.lua: about 0.0007 a
# gram, e.g. 5.56x45 12 g = 0.0085, 7.62x51 24.5 g = 0.0165; user, 2026-11-11, from a player's real-weight table).
# 50-round boxes, as both are sold.
CALIBRES = {
    '46x30': dict(name='4.6x30mm', weight='0.0046', mesh='46x30_Round'),
    '57x28': dict(name='5.7x28mm', weight='0.0042', mesh='57x28_Round'),
    # the main mod's calibre (gen_scripts.py ammo_762x25_9x18: 10.6 g, GoM's 5.7x28 mesh at 0.0129); its hollow
    # point is ours (user, 2026-11-25: "Then include them in post 1993", no date found for one before 1993)
    '762x25': dict(name='7.62x25mm Tokarev', weight='0.0074', mesh='57x28_Round', scale='0.0129'),
    # the main mod's 9x18 (gen_scripts.py: 10.0 g, GoM's 9x19 mesh at 0.0135)
    '9x18': dict(name='9x18mm Makarov', weight='0.007', mesh='9x19_Round', scale='0.0135'),
    # Guns of Marz's calibres, with its boxes, their weights and meshes (the main mod's gen_scripts.py CALIBRES); the
    # special rounds audit's later loads (2026-11-25, TODO.md)
    '762x54': dict(name='7.62x54mmR', weight='0.016', mesh='762x54_Round', per_box=20, box_w='0.288', carton_w='2.765',
                   crate_w='8.848', box_mesh='WorldItems/RifleAmmoBox', box_scale='0.6'),
    '545x39': dict(name='5.45x39mm', weight='0.007', mesh='545x39_Round', per_box=20, box_w='0.126', carton_w='1.21',
                   crate_w='3.872', box_mesh='WorldItems/RifleAmmoBox', box_scale='0.6'),
    '762x39': dict(name='7.62x39mm', weight='0.012', mesh='762x39_Round', per_box=20, box_w='0.216', carton_w='2.074',
                   crate_w='6.637', box_mesh='WorldItems/RifleAmmoBox', box_scale='0.6'),
    '3030': dict(name='.30-30', weight='0.015', mesh='3030_Round', per_box=20, box_w='0.27', carton_w='2.592',
                 crate_w='8.294', box_mesh='WorldItems/RifleAmmoBox', box_scale='0.6'),
    '9x19': dict(name='9x19mm', weight='0.009', mesh='9x19_Round', box_w='0.405', carton_w='3.888', crate_w='12.442'),
    '50': dict(name='.50 AE', weight='0.024', mesh='50_Round', per_box=25, box_w='0.54', carton_w='5.184',
               crate_w='16.589'),
    '12Gauge': dict(name='12 Gauge', weight='0.031', mesh='12Gauge_Shell', scale='0.012', per_box=25, box_w='0.698',
                    carton_w='6.701', crate_w='21.443', box_mesh='WorldItems/BoxOfShotGunShells', box_scale='0.6',
                    shell=True),
}
ROUNDS_PER_BOX, BOXES_PER_CARTON, CARTONS_PER_CRATE = 50, 12, 4


def packed_weights(round_w):
    """GoM's packing bonus (its ammo_boxes.txt): a box weighs 0.9 of its rounds, a carton 0.8 of its boxes and a
    crate 0.8 of its cartons, each rounded to 3 decimals from the rounded step before, so every step down is lighter
    per round (user, 2026-10-25: packing must always pay)."""
    box = round(float(round_w) * ROUNDS_PER_BOX * 0.9, 3)
    carton = round(box * BOXES_PER_CARTON * 0.8, 3)
    crate = round(carton * CARTONS_PER_CRATE * 0.8, 3)
    return dict(box_w=f"{box:g}", carton_w=f"{carton:g}", crate_w=f"{crate:g}")


for _c in CALIBRES.values():
    for _k, _v in packed_weights(_c['weight']).items():
        _c.setdefault(_k, _v)                 # GoM's calibres keep GoM's own box weights

# (calibre, item suffix ('' = the standard round), art suffix, ammo type id, English variant name)
# 5.7x28mm SS190 (GunsOfTienPost93.57x28_Bullet / _Box / _Carton / _Crate) moved to the main mod on 2026-11-03 for its
# P90 with the ring sight, under the same IDs (the main mod's gen_scripts.py ammo_57x28()); its two other loads stay.
ROUNDS = [
    ('46x30', '', 'DM11', 'bullet_46x30', 'DM11'),
    ('46x30', '_Subsonic', 'SS', 'bullet_46x30_subsonic', 'Subsonic'),
    ('57x28', '_SB193', 'SB193', 'bullet_57x28_sb193', 'SB193'),
    ('57x28', '_SS197SR', 'SS197SR', 'bullet_57x28_ss197sr', 'SS197SR'),
    ('762x25', '_HollowPoint', 'HP', 'bullet_762x25_hollow_point', 'Hollow Point'),
    # Special rounds audit (2026-11-25): later or undated loads (TODO.md "Special rounds audit")
    ('46x30', '_DM21', 'DM21', 'bullet_46x30_dm21', 'DM21'),
    ('9x18', '_PMM', 'PMM', 'bullet_9x18_pmm', 'PMM'),
    ('9x18', '_RG028', 'RG028', 'bullet_9x18_rg028', 'RG028'),
    ('762x54', '_SP', 'SP', 'bullet_762x54_sp', 'Soft Point'),
    ('762x54', '_7N13', '7N13', 'bullet_762x54_7n13', '7N13'),
    ('545x39', '_7N22', '7N22', 'bullet_545x39_7n22', '7N22'),
    ('9x19', '_7N21', '7N21', 'bullet_9x19_7n21', '7N21'),
    ('762x39', '_HollowPoint', 'HP', 'bullet_762x39_hollow_point', 'Hollow Point'),
    ('3030', '_FTX', 'FTX', 'bullet_3030_ftx', 'FTX'),
    ('50', '_HollowPoint', 'HP', 'bullet_50_hollow_point', 'Hollow Point'),
    ('12Gauge', '_DragonsBreath', 'DragonsBreath', 'shell_12g_dragons_breath', "Dragon's Breath"),
]

# GoM's naming, a real load name followed by its use in parentheses (as GoM's 'MKI Suppressor (5.56mm Rifles)').
USAGE = {'_SB193': 'Subsonic', '_SS197SR': 'Hollow Point', '_RG028': 'Armor Piercing', '_7N13': 'Armor Piercing',
         '_7N22': 'Armor Piercing', '_7N21': 'Armor Piercing', '_FTX': 'Polymer Tip', '_DragonsBreath': 'Incendiary'}


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)


def names(cal, suffix, art):
    tail = suffix if suffix else ''
    kind = 'Shell' if CALIBRES[cal].get('shell') else 'Bullet'
    return dict(round=f"{cal}_{kind}{tail}", box=f"{cal}_Box{tail}", carton=f"{cal}_Carton{tail}",
                crate=f"{cal}_Crate{tail}", round_art=f"{ART}{cal}_{'Shell' if kind == 'Shell' else 'Round'}_{art}", box_art=f"{ART}{cal}_Box_{art}")


def items():
    out = [f"module {MODULE} {{\n    imports {{ Base }}\n"]
    for cal, suffix, art, ammo_id, _ in ROUNDS:
        c, n = CALIBRES[cal], names(cal, suffix, art)
        per, shell = c.get('per_box', ROUNDS_PER_BOX), c.get('shell')
        sounds = ('BoxOfShellsPlaceAll', 'BoxOfShellsPlaceOne') if shell else ('BoxOfRoundsPlaceAll', 'BoxOfRoundsPlaceOne')
        out.append(f"""
    item {n['round']} {{
        DisplayCategory  = Ammo,
        ItemType         = base:normal,
        Weight           = {c['weight']},
        Icon             = {n['round_art']},
        count            = {6 if shell else 5},
        MetalValue       = 1.0,
        WorldStaticModel = {MODULE}.{n['round_art']},
        Tags             = {'base:ammo;base:shotgunshell' if shell else 'base:ammo'},
        AmmoType         = gunsoftienpost93:{ammo_id},
    }}

    item {n['box']} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['box_w']},
        Icon               = {n['box_art']},
        MetalValue         = {dict({20: '40.0', 25: '24.0'}).get(per, '30.0')},
        PlaceMultipleSound = {sounds[0]},
        PlaceOneSound      = {sounds[1]},
        StaticModel        = {MODULE}.{n['box_art']},
        WorldStaticModel   = {MODULE}.{n['box_art']},
        DoubleClickRecipe  = GunsOfTienPost93_OpenBoxOf{per}Bullets,
        Tags               = base:hasmetal;base:ignorezombiedensity;base:ammo;gunsoftienpost93:ammobox{per};gunsoftienpost93:ammobox,
    }}

    item {n['carton']} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['carton_w']},
        Icon               = Parcel_Medium_Ammo,
        AlwaysWelcomeGift  = true,
        MetalValue         = 400.0,
        PlaceMultipleSound = BoxOfRoundsPlaceAll,
        PlaceOneSound      = BoxOfRoundsPlaceOne,
        WorldStaticModel   = Parcel_Ammo_Medium,
        Tags               = base:hasmetal;base:ignorezombiedensity;gunsoftienpost93:ammocarton,
        DoubleClickRecipe  = GunsOfTienPost93_OpenCartonOfBoxesOfAmmo,
    }}

    item {n['crate']} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['crate_w']},
        Icon               = Ammo_Crate,
        AlwaysWelcomeGift  = true,
        MetalValue         = 400.0,
        PlaceMultipleSound = BoxOfRoundsPlaceAll,
        PlaceOneSound      = BoxOfRoundsPlaceOne,
        WorldStaticModel   = MarzGuns.Ammo_Crate,
        Tags               = base:hasmetal;base:ignorezombiedensity;gunsoftienpost93:ammocrate,
        DoubleClickRecipe  = GunsOfTienPost93_OpenCrateOfBoxesOfAmmo,
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTienPost93/items_ammo.txt', ''.join(out))


def models():
    out = [f"module {MODULE} {{\n"]
    for cal, suffix, art, _, _ in ROUNDS:
        c, n = CALIBRES[cal], names(cal, suffix, art)
        out.append(f"""
    model {n['round_art']} {{
        mesh    = Worlditems/Ammunition/Rounds|{c['mesh']},
        texture = worlditems/GunsOfTienPost93/Rounds/{n['round_art']},
        scale   = {c.get('scale', '0.015')},
    }}

    model {n['box_art']} {{
        mesh    = {c.get('box_mesh', 'WorldItems/HandGunAmmoBox')},
        texture = worlditems/GunsOfTienPost93/Boxes/{n['box_art']},
        scale   = {c.get('box_scale', '0.4')},
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTienPost93/models_ammo.txt', ''.join(out))


BOX_SIZES = (20, 25, 50)


def box_recipes(per, action, rows, q, mapper):
    return f"""
    craftRecipe GunsOfTienPost93_OpenBoxOf{per}Bullets {{
        timedAction = {action},
        time        = 15,
        category    = Packing,
        recipeGroup = OpenBox,
        canWalk     = true,
        Tags        = InHandCraft;CanBeDoneInDark;CanBeDoneWhileWalking,
        inputs {{
            item 1 tags[gunsoftienpost93:ammobox{per}] mappers[ammoType] flags[Prop2;AllowFavorite;InheritFavorite],
        }}
        outputs {{
            item {per} mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper([(q(n['round']), q(n['box'])) for n in rows])}        }}
    }}

    craftRecipe GunsOfTienPost93_Place{per}BulletsInBox {{
        timedAction = PlaceAmmoInBox,
        time        = 15,
        category    = Packing,
        canWalk     = true,
        Tags        = InHandCraft;CanBeDoneWhileWalking,
        inputs {{
            item {per} [{';'.join(q(n['round']) for n in rows)}] mappers[ammoType] flags[AllowFavorite;InheritFavorite;IsExclusive],
        }}
        outputs {{
            item 1 mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper([(q(n['box']), q(n['round'])) for n in rows])}        }}
    }}
"""


def recipes():
    def mapper(pairs):
        width = max(len(a) for a, _ in pairs)
        return ''.join(f"            {a.ljust(width)} = {b},\n" for a, b in pairs)

    rows = [names(cal, suffix, art) for cal, suffix, art, _, _ in ROUNDS]
    q = lambda name: f"{MODULE}.{name}"
    out = ["module Base {\n"]
    # one open / pack pair per box size (GoM's boxes: 20 rifle rounds, 25 shells or .50 AE, 50 pistol rounds)
    for per in BOX_SIZES:
        sized = [names(cal, suffix, art) for cal, suffix, art, _, _ in ROUNDS
                 if CALIBRES[cal].get('per_box', ROUNDS_PER_BOX) == per]
        action = 'OpenShellsBox' if any(CALIBRES[cal].get('shell') for cal, *_ in ROUNDS
                                         if CALIBRES[cal].get('per_box', ROUNDS_PER_BOX) == per) else 'OpenAmmoBox'
        out.append(box_recipes(per, action, sized, q, mapper))
    for name, action, time, tags, tag, count, pairs, opening in (
            ('GunsOfTienPost93_OpenCartonOfBoxesOfAmmo', 'UnPackBox', 50, 'InHandCraft;CanBeDoneInDark',
             'gunsoftienpost93:ammocarton', 12, [(q(n['box']), q(n['carton'])) for n in rows], True),
            ('GunsOfTienPost93_PlaceBoxesOfAmmoInCarton', 'PackingBox', 50, 'InHandCraft', 'gunsoftienpost93:ammobox',
             12, [(q(n['carton']), q(n['box'])) for n in rows], False),
            ('GunsOfTienPost93_OpenCrateOfBoxesOfAmmo', 'UnPackBox', 100, 'InHandCraft;CanBeDoneInDark',
             'gunsoftienpost93:ammocrate', 4, [(q(n['carton']), q(n['crate'])) for n in rows], True),
            ('GunsOfTienPost93_PlaceBoxesOfAmmoInCrates', 'PackingBox', 100, 'InHandCraft',
             'gunsoftienpost93:ammocarton', 4, [(q(n['crate']), q(n['carton'])) for n in rows], False)):
        in_count, out_count = (1, count) if opening else (count, 1)
        flags = 'AllowFavorite;InheritFavorite' if opening else 'AllowFavorite;InheritFavorite;IsExclusive'
        out.append(f"""
    craftRecipe {name} {{
        timedAction = {action},
        time        = {time},
        category    = Packing,
        canWalk     = true,
        Tags        = {tags};CanBeDoneWhileWalking,
        inputs {{
            item {in_count} tags[{tag}] mappers[ammoType] flags[{flags}],
        }}
        outputs {{
            item {out_count} mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper(pairs)}        }}
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTienPost93/recipes_ammo.txt', ''.join(out))


def translations():
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    item_names = json.load(open(path)) if os.path.exists(path) else {}
    for cal, suffix, art, _, label in ROUNDS:
        c, n = CALIBRES[cal], names(cal, suffix, art)
        use = f" ({USAGE[suffix]})" if suffix in USAGE else ""
        item_names[q_full(n['round'])] = f"{c['name']} {label} {'Shell' if c.get('shell') else 'Round'}{use}"
        item_names[q_full(n['box'])] = f"{c['name']} {label} Box{use}"
        item_names[q_full(n['carton'])] = f"Carton of {c['name']} {label} Boxes{use}"
        item_names[q_full(n['crate'])] = f"Crate of {c['name']} {label} Boxes{use}"
    for moved in ('57x28_Bullet', '57x28_Box', '57x28_Carton', '57x28_Crate'):      # named by the main mod now
        item_names.pop(q_full(moved), None)
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(item_names, indent=2, ensure_ascii=False) + '\n')

    path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    recipe_names = json.load(open(path)) if os.path.exists(path) else {}
    for per in BOX_SIZES:
        recipe_names[f'GunsOfTienPost93_OpenBoxOf{per}Bullets'] = f'Open Box ({per} Bullets)'
        recipe_names[f'GunsOfTienPost93_Place{per}BulletsInBox'] = f'Pack Ammo in Box ({per} Bullets)'
    recipe_names.update({
        'GunsOfTienPost93_OpenCartonOfBoxesOfAmmo': 'Open Carton of Ammo Boxes',
        'GunsOfTienPost93_PlaceBoxesOfAmmoInCarton': 'Place Ammo Boxes in Carton',
        'GunsOfTienPost93_OpenCrateOfBoxesOfAmmo': 'Open Crate of Ammo Boxes',
        'GunsOfTienPost93_PlaceBoxesOfAmmoInCrates': 'Place Ammo Boxes in Crate',
    })
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(recipe_names, indent=2) + '\n')


AMMOMAKER_TYPES = [
    ('46x30SS', '4.6x30mm SS', '4.6x30mm SS sub sonic round - 2001'),
    ('57x28SS', '5.7x28mm SB193', '5.7x28mm SB193 sub sonic round - 1990s'),
    ('57x28SR', '5.7x28mm SS197SR', '5.7x28mm SS197SR polymer tip round - 2000s'),
    ('762x25TokHP', '7.62x25mm Tokarev HP', '7.62x25mm Tokarev hollow point round'),
    # Special rounds audit (2026-11-25): later or undated loads
    ('46x30DM21', '4.6x30mm DM21', '4.6x30mm DM21 soft core round - 2000s'),
    ('9x18MakPMM', '9x18mm Makarov PMM', '9x18mm Makarov PMM high pressure round - 1990s'),
    ('9x18MakRG028', '9x18mm Makarov RG028', '9x18mm Makarov RG028 armour piercing round'),
    ('762x54RSP', '7.62x54mmR SP', '7.62x54mmR SP soft point hunting round'),
    ('762x54R7N13', '7.62x54mmR 7N13', '7.62x54mmR 7N13 steel core round - 1990s'),
    ('545x39_7N22', '5.45x39mm 7N22', '5.45x39mm 7N22 armour piercing round - 1998'),
    ('9x19Para7N21', '9mm Luger 7N21', '9mm Luger 7N21 armour piercing high pressure round'),
    ('762x39HP', '7.62x39mm HP', '7.62x39mm HP hollow point round - 1990s'),
    ('3030WinFTX', '.30-30 Winchester FTX', '.30-30 Winchester FTX polymer tip round - 2005'),
    ('50AEHP', '.50 AE HP', '.50 Action Express HP hollow point round'),
    ('12DragonsBreath', "12 bore dragon's breath", "12 bore dragon's breath (aka. 12-gauge) - 18.5mm"),
]


def ammomaker():
    # Timed actions: the main mod's copies of Ammo Maker's (its scripts/GunsOfTien/timedactions_ammomaker.txt), so
    # these load without Ammo Maker; AmmoMaker.lua hides the recipes then.
    out = ["/* Placeholders Ammo Maker fills from shared/GunsOfTienPost93/AmmoMaker.lua (recipe:Load), hidden without it. */\n\nmodule Base {\n"]
    for name, _, _ in AMMOMAKER_TYPES:
        out.append(f"""
\tcraftRecipe Make{name}
\t{{
\t\ttimedAction = GunsOfTien_MakeAmmo,
\t\tTime = 30,
\t\tTags = InHandCraft,
\t\tNeedToBeLearn = False,
\t\tcategory = AmmoMakerAmmo,
\t\txpAward = Reloading:3,
\t\tToolTip = Tooltip_Recipe_Make{name},
\t\tinputs {{}}
\t\toutputs {{}}
\t}}

\tcraftRecipe Produce{name}
\t{{
\t\ttimedAction = GunsOfTien_ProduceAmmo,
\t\tTime = 100,
\t\tTags = AnySurfaceCraft;CanBeDoneFromFloor,
\t\tNeedToBeLearn = False,
\t\tcategory = AmmoMakerAmmo,
\t\txpAward = Reloading:10,
\t\tToolTip = Tooltip_Recipe_Produce{name},
\t\tinputs {{}}
\t\toutputs {{}}
\t}}
""")
    out.append("}\n")
    write('scripts/GunsOfTienPost93/recipes_ammomaker.txt', ''.join(out))
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    recipe_names = json.load(open(path))
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tooltips = json.load(open(tip_path)) if os.path.exists(tip_path) else {}
    for name, label, desc in AMMOMAKER_TYPES:
        recipe_names[f"Make{name}"] = f"Make {label}"
        recipe_names[f"Produce{name}"] = f"Produce {label}"
        # sentences end with a full stop (user, 2026-10-19), unlike Ammo Maker's own recipe tooltips
        tooltips[f"Tooltip_Recipe_Make{name}"] = f"Assemble {desc}."
        tooltips[f"Tooltip_Recipe_Produce{name}"] = f"Assemble {label} rounds with reloading press."
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(recipe_names, indent=2) + '\n')
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tooltips, indent=2) + '\n')


def q_full(name):
    return f"{MODULE}.{name}"


if __name__ == '__main__':
    items()
    models()
    recipes()
    translations()
    ammomaker()
    print('written under', os.path.normpath(ROOT))
