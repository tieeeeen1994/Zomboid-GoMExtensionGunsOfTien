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

# Real cartridge weights: 4.6x30 about 6.6 g, 5.7x28 about 6.0 g. 50-round boxes, as both are sold.
CALIBRES = {
    '46x30': dict(name='4.6x30mm', weight='0.0066', mesh='46x30_Round'),
    '57x28': dict(name='5.7x28mm', weight='0.006', mesh='57x28_Round'),
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
    _c.update(packed_weights(_c['weight']))

# (calibre, item suffix ('' = the standard round), art suffix, ammo type id, English variant name)
ROUNDS = [
    ('46x30', '', 'DM11', 'bullet_46x30', 'DM11'),
    ('46x30', '_Subsonic', 'SS', 'bullet_46x30_subsonic', 'Subsonic'),
    ('57x28', '', 'SS190', 'bullet_57x28', 'SS190'),
    ('57x28', '_SB193', 'SB193', 'bullet_57x28_sb193', 'SB193'),
    ('57x28', '_SS197SR', 'SS197SR', 'bullet_57x28_ss197sr', 'SS197SR'),
]

# GoM's naming, a real load name followed by its use in parentheses (as GoM's 'MKI Suppressor (5.56mm Rifles)').
USAGE = {'_SB193': 'Subsonic', '_SS197SR': 'Hollow Point'}


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)


def names(cal, suffix, art):
    tail = suffix if suffix else ''
    return dict(round=f"{cal}_Bullet{tail}", box=f"{cal}_Box{tail}", carton=f"{cal}_Carton{tail}",
                crate=f"{cal}_Crate{tail}", round_art=f"{ART}{cal}_Round_{art}", box_art=f"{ART}{cal}_Box_{art}")


def items():
    out = [f"module {MODULE} {{\n    imports {{ Base }}\n"]
    for cal, suffix, art, ammo_id, _ in ROUNDS:
        c, n = CALIBRES[cal], names(cal, suffix, art)
        out.append(f"""
    item {n['round']} {{
        DisplayCategory  = Ammo,
        ItemType         = base:normal,
        Weight           = {c['weight']},
        Icon             = {n['round_art']},
        count            = 5,
        MetalValue       = 1.0,
        WorldStaticModel = {MODULE}.{n['round_art']},
        Tags             = base:ammo,
        AmmoType         = gunsoftienpost93:{ammo_id},
    }}

    item {n['box']} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['box_w']},
        Icon               = {n['box_art']},
        MetalValue         = 30.0,
        PlaceMultipleSound = BoxOfRoundsPlaceAll,
        PlaceOneSound      = BoxOfRoundsPlaceOne,
        StaticModel        = {MODULE}.{n['box_art']},
        WorldStaticModel   = {MODULE}.{n['box_art']},
        DoubleClickRecipe  = GunsOfTienPost93_OpenBoxOf50Bullets,
        Tags               = base:hasmetal;base:ignorezombiedensity;base:ammo;gunsoftienpost93:ammobox50;gunsoftienpost93:ammobox,
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
        scale   = 0.015,
    }}

    model {n['box_art']} {{
        mesh    = WorldItems/HandGunAmmoBox,
        texture = worlditems/GunsOfTienPost93/Boxes/{n['box_art']},
        scale   = 0.4,
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTienPost93/models_ammo.txt', ''.join(out))


def recipes():
    def mapper(pairs):
        width = max(len(a) for a, _ in pairs)
        return ''.join(f"            {a.ljust(width)} = {b},\n" for a, b in pairs)

    rows = [names(cal, suffix, art) for cal, suffix, art, _, _ in ROUNDS]
    q = lambda name: f"{MODULE}.{name}"
    out = ["module Base {\n"]
    out.append(f"""
    craftRecipe GunsOfTienPost93_OpenBoxOf50Bullets {{
        timedAction = OpenAmmoBox,
        time        = 15,
        category    = Packing,
        recipeGroup = OpenBox,
        canWalk     = true,
        Tags        = InHandCraft;CanBeDoneInDark,
        inputs {{
            item 1 tags[gunsoftienpost93:ammobox50] mappers[ammoType] flags[Prop2;AllowFavorite;InheritFavorite],
        }}
        outputs {{
            item 50 mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper([(q(n['round']), q(n['box'])) for n in rows])}        }}
    }}

    craftRecipe GunsOfTienPost93_Place50BulletsInBox {{
        timedAction = PlaceAmmoInBox,
        time        = 15,
        category    = Packing,
        canWalk     = true,
        Tags        = InHandCraft,
        inputs {{
            item 50 [{';'.join(q(n['round']) for n in rows)}] mappers[ammoType] flags[AllowFavorite;InheritFavorite;IsExclusive],
        }}
        outputs {{
            item 1 mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper([(q(n['box']), q(n['round'])) for n in rows])}        }}
    }}
""")
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
        Tags        = {tags},
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
        item_names[q_full(n['round'])] = f"{c['name']} {label} Round{use}"
        item_names[q_full(n['box'])] = f"{c['name']} {label} Box{use}"
        item_names[q_full(n['carton'])] = f"Carton of {c['name']} {label} Boxes{use}"
        item_names[q_full(n['crate'])] = f"Crate of {c['name']} {label} Boxes{use}"
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(item_names, indent=2, ensure_ascii=False) + '\n')

    path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    recipe_names = json.load(open(path)) if os.path.exists(path) else {}
    recipe_names.update({
        'GunsOfTienPost93_OpenBoxOf50Bullets': 'Open Box (50 Bullets)',
        'GunsOfTienPost93_Place50BulletsInBox': 'Pack Ammo in Box (50 Bullets)',
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
