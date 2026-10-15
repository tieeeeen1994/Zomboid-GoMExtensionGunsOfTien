"""Writes the item, model and recipe scripts and the item / recipe translations of GoM Extension: Guns of Tien.

Run from anywhere: python3 scripts/gen_scripts.py. The round table below is the one source of truth; registries.lua
and the Lua profiles use the same full types.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Contents', 'mods', 'GoMExtensionGunsOfTien',
                    '42', 'media')
MODULE = 'GunsOfTien'

# Per calibre: round weight, rounds per box, GoM round mesh (in Rounds.fbx), mesh scale, box mesh, box scale, box
# weight / carton weight / crate weight (GoM's base box of that calibre), carton icon + model.
CALIBRES = {
    '762x39': dict(weight='0.012', per_box=20, mesh='762x39_Round', scale='0.015', box_mesh='WorldItems/RifleAmmoBox',
                   box_scale='0.6', box_w='0.216', carton_w='2.074', crate_w='6.637', military=True, name='7.62x39mm'),
    '9x19': dict(weight='0.009', per_box=50, mesh='9x19_Round', scale='0.015', box_mesh='WorldItems/HandGunAmmoBox',
                 box_scale='0.4', box_w='0.405', carton_w='3.888', crate_w='12.442', military=False, name='9x19mm'),
    '45': dict(weight='0.0145', per_box=50, mesh='45_Round', scale='0.015', box_mesh='WorldItems/HandGunAmmoBox',
               box_scale='0.4', box_w='0.653', carton_w='6.269', crate_w='20.061', military=False, name='.45 ACP'),
    '9x39': dict(weight='0.0115', per_box=20, mesh='9x39_Round', scale='0.015', box_mesh='WorldItems/RifleAmmoBox',
                 box_scale='0.6', box_w='0.207', carton_w='1.987', crate_w='6.358', military=True, name='9x39mm'),
    '3006': dict(weight='0.019', per_box=20, mesh='3006_Round', scale='0.015', box_mesh='WorldItems/RifleAmmoBox',
                 box_scale='0.6', box_w='0.342', carton_w='3.283', crate_w='10.506', military=True,
                 name='.30-06 Springfield'),
    '308': dict(weight='0.0175', per_box=20, mesh='762x51_Round', scale='0.015', box_mesh='WorldItems/RifleAmmoBox',
                box_scale='0.6', box_w='0.315', carton_w='3.024', crate_w='9.677', military=True,
                name='.308 Winchester'),
    '3030': dict(weight='0.015', per_box=20, mesh='3030_Round', scale='0.015', box_mesh='WorldItems/RifleAmmoBox',
                 box_scale='0.6', box_w='0.27', carton_w='2.592', crate_w='8.294', military=True, name='.30-30'),
    '12Gauge': dict(weight='0.031', per_box=25, mesh='12Gauge_Shell', scale='0.012',
                    box_mesh='WorldItems/BoxOfShotGunShells', box_scale='0.6', box_w='0.698', carton_w='6.701',
                    crate_w='21.443', military=True, name='12 Gauge', shell=True),
}

# Rounds: (calibre, variant item suffix, art suffix, English variant name)
ROUNDS = [
    ('762x39', 'US', 'US', 'US'),
    ('762x39', 'SP', 'SP', 'Soft Point'),
    ('762x39', 'SteelCore', 'SteelCore', 'Steel Core'),
    ('9x19', 'Subsonic', 'SS', '147gr'),
    ('9x19', 'HollowPoint', 'HP', 'Hollow Point'),
    ('9x19', 'PPP', 'PPP', '[+P+]'),
    ('45', 'HollowPoint', 'HP', 'Hollow Point'),
    ('45', 'P', 'P', '[+P]'),
    ('9x39', 'SP6', 'SP6', 'SP-6'),
    ('3006', 'SP', 'SP', 'Soft Point'),
    ('308', 'SP', 'SP', 'Soft Point'),
    ('12Gauge', 'Birdshot', 'Birdshot', 'Birdshot'),
]

# GoM's naming: '<calibre> <name> Round / Box', 'Carton of <calibre> <name> Boxes', +P in square brackets; a real
# load name gets its use after it in parentheses, as GoM writes 'MKI Suppressor (5.56mm Rifles)'.
USAGE = {('762x39', 'US'): 'Subsonic', ('762x39', 'SteelCore'): 'Armor Piercing', ('9x19', 'Subsonic'): 'Subsonic',
         ('9x39', 'SP6'): 'Armor Piercing'}


# The ids registered in media/registries.lua (gunsoftien:<id>).
AMMO_IDS = {
    ('762x39', 'US'): 'bullet_762x39_us', ('762x39', 'SP'): 'bullet_762x39_sp',
    ('762x39', 'SteelCore'): 'bullet_762x39_steel_core', ('9x19', 'Subsonic'): 'bullet_9x19_subsonic',
    ('9x19', 'HollowPoint'): 'bullet_9x19_hollow_point', ('9x19', 'PPP'): 'bullet_9x19_ppp',
    ('45', 'HollowPoint'): 'bullet_45_hollow_point', ('45', 'P'): 'bullet_45_p', ('9x39', 'SP6'): 'bullet_9x39_sp6',
    ('3006', 'SP'): 'bullet_3006_sp', ('308', 'SP'): 'bullet_308_sp',
    ('12Gauge', 'Birdshot'): 'shell_12g_birdshot',
}


def round_item(cal, var):
    return f"{cal}_Shell_{var}" if CALIBRES[cal].get('shell') else f"{cal}_Bullet_{var}"


def round_art(cal, art):
    return f"{cal}_Shell_{art}" if CALIBRES[cal].get('shell') else f"{cal}_Round_{art}"


def box_art(cal, art):
    return f"{cal}_Box_{art}"


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)


def items():
    out = [f"module {MODULE} {{\n    imports {{ Base }}\n"]
    for cal, var, art, _ in ROUNDS:
        c = CALIBRES[cal]
        shell = c.get('shell')
        tags = 'base:ammo;base:shotgunshell' if shell else 'base:ammo'
        out.append(f"""
    item {round_item(cal, var)} {{
        DisplayCategory  = Ammo,
        ItemType         = base:normal,
        Weight           = {c['weight']},
        Icon             = {round_art(cal, art)},
        count            = {6 if shell else 5},
        MetalValue       = 1.0,
        WorldStaticModel = {MODULE}.{round_art(cal, art)},
        Tags             = {tags},
        AmmoType         = gunsoftien:{AMMO_IDS[(cal, var)]},
    }}
""")
    for cal, var, art, _ in ROUNDS:
        c = CALIBRES[cal]
        per = c['per_box']
        sounds = ('BoxOfShellsPlaceAll', 'BoxOfShellsPlaceOne') if c.get('shell') else \
            ('BoxOfRoundsPlaceAll', 'BoxOfRoundsPlaceOne')
        gift = '        AlwaysWelcomeGift  = true,\n' if per == 20 else ''
        metal = {20: '40.0', 25: '24.0', 50: '30.0'}[per]
        out.append(f"""
    item {cal}_Box_{var} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['box_w']},
        Icon               = {box_art(cal, art)},
{gift}        MetalValue         = {metal},
        PlaceMultipleSound = {sounds[0]},
        PlaceOneSound      = {sounds[1]},
        StaticModel        = {MODULE}.{box_art(cal, art)},
        WorldStaticModel   = {MODULE}.{box_art(cal, art)},
        DoubleClickRecipe  = GunsOfTien_OpenBoxOf{per}Bullets,
        Tags               = base:hasmetal;base:ignorezombiedensity;base:ammo;gunsoftien:ammobox{per};gunsoftien:ammobox,
    }}
""")
        parcel_icon, parcel_model = ('Parcel_Medium_Military', 'Parcel_Military_Medium') if c['military'] else \
            ('Parcel_Medium_Ammo', 'Parcel_Ammo_Medium')
        out.append(f"""
    item {cal}_Carton_{var} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['carton_w']},
        Icon               = {parcel_icon},
        AlwaysWelcomeGift  = true,
        MetalValue         = 400.0,
        PlaceMultipleSound = BoxOfRoundsPlaceAll,
        PlaceOneSound      = BoxOfRoundsPlaceOne,
        WorldStaticModel   = {parcel_model},
        Tags               = base:hasmetal;base:ignorezombiedensity;gunsoftien:ammocarton,
        DoubleClickRecipe  = GunsOfTien_OpenCartonOfBoxesOfAmmo,
    }}

    item {cal}_Crate_{var} {{
        DisplayCategory    = Ammo,
        ItemType           = base:normal,
        Weight             = {c['crate_w']},
        Icon               = Ammo_Crate,
        AlwaysWelcomeGift  = true,
        MetalValue         = 400.0,
        PlaceMultipleSound = BoxOfRoundsPlaceAll,
        PlaceOneSound      = BoxOfRoundsPlaceOne,
        WorldStaticModel   = MarzGuns.Ammo_Crate,
        Tags               = base:hasmetal;base:ignorezombiedensity;gunsoftien:ammocrate,
        DoubleClickRecipe  = GunsOfTien_OpenCrateOfBoxesOfAmmo,
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTien/items_ammo.txt', ''.join(out))


def models():
    out = [f"module {MODULE} {{\n"]
    for cal, var, art, _ in ROUNDS:
        c = CALIBRES[cal]
        out.append(f"""
    model {round_art(cal, art)} {{
        mesh    = Worlditems/Ammunition/Rounds|{c['mesh']},
        texture = worlditems/GunsOfTien/Rounds/{round_art(cal, art)},
        scale   = {c['scale']},
    }}

    model {box_art(cal, art)} {{
        mesh    = {c['box_mesh']},
        texture = worlditems/GunsOfTien/Boxes/{box_art(cal, art)},
        scale   = {c['box_scale']},
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTien/models_ammo.txt', ''.join(out))


def recipes():
    def mapper(pairs):
        width = max(len(a) for a, _ in pairs)
        return ''.join(f"            {a.ljust(width)} = {b},\n" for a, b in pairs)

    out = ["module Base {\n"]
    for per, action in ((20, 'OpenAmmoBox'), (25, 'OpenShellsBox'), (50, 'OpenAmmoBox')):
        rows = [(cal, var) for cal, var, _, _ in ROUNDS if CALIBRES[cal]['per_box'] == per]
        if not rows:
            continue
        opened = [(f"{MODULE}.{round_item(c, v)}", f"{MODULE}.{c}_Box_{v}") for c, v in rows]
        packed = [(f"{MODULE}.{c}_Box_{v}", f"{MODULE}.{round_item(c, v)}") for c, v in rows]
        inputs = ';'.join(f"{MODULE}.{round_item(c, v)}" for c, v in rows)
        out.append(f"""
    craftRecipe GunsOfTien_OpenBoxOf{per}Bullets {{
        timedAction = {action},
        time        = 15,
        category    = Packing,
        recipeGroup = OpenBox,
        canWalk     = true,
        Tags        = InHandCraft;CanBeDoneInDark,
        inputs {{
            item 1 tags[gunsoftien:ammobox{per}] mappers[ammoType] flags[Prop2;AllowFavorite;InheritFavorite],
        }}
        outputs {{
            item {per} mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper(opened)}        }}
    }}

    craftRecipe GunsOfTien_Place{per}BulletsInBox {{
        timedAction = PlaceAmmoInBox,
        time        = 15,
        category    = Packing,
        canWalk     = true,
        Tags        = InHandCraft,
        inputs {{
            item {per} [{inputs}] mappers[ammoType] flags[AllowFavorite;InheritFavorite;IsExclusive],
        }}
        outputs {{
            item 1 mapper:ammoType,
        }}
        itemMapper ammoType {{
{mapper(packed)}        }}
    }}
""")
    all_rows = [(cal, var) for cal, var, _, _ in ROUNDS]
    for name, action, time, tags, tag, count, pairs in (
            ('GunsOfTien_OpenCartonOfBoxesOfAmmo', 'UnPackBox', 50, 'InHandCraft;CanBeDoneInDark',
             'gunsoftien:ammocarton', 12, [(f"{MODULE}.{c}_Box_{v}", f"{MODULE}.{c}_Carton_{v}") for c, v in all_rows]),
            ('GunsOfTien_PlaceBoxesOfAmmoInCarton', 'PackingBox', 50, 'InHandCraft', 'gunsoftien:ammobox', 12,
             [(f"{MODULE}.{c}_Carton_{v}", f"{MODULE}.{c}_Box_{v}") for c, v in all_rows]),
            ('GunsOfTien_OpenCrateOfBoxesOfAmmo', 'UnPackBox', 100, 'InHandCraft;CanBeDoneInDark',
             'gunsoftien:ammocrate', 4, [(f"{MODULE}.{c}_Carton_{v}", f"{MODULE}.{c}_Crate_{v}") for c, v in all_rows]),
            ('GunsOfTien_PlaceBoxesOfAmmoInCrates', 'PackingBox', 100, 'InHandCraft', 'gunsoftien:ammocarton', 4,
             [(f"{MODULE}.{c}_Crate_{v}", f"{MODULE}.{c}_Carton_{v}") for c, v in all_rows])):
        opening = name.startswith('GunsOfTien_Open')
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
    write('scripts/GunsOfTien/recipes_ammo.txt', ''.join(out))


def translations():
    names = {}
    for cal, var, _, label in ROUNDS:
        c = CALIBRES[cal]
        unit = 'Shell' if c.get('shell') else 'Round'
        use = f" ({USAGE[(cal, var)]})" if (cal, var) in USAGE else ""
        names[f"{MODULE}.{round_item(cal, var)}"] = f"{c['name']} {label} {unit}{use}"
        names[f"{MODULE}.{cal}_Box_{var}"] = f"{c['name']} {label} Box{use}"
        names[f"{MODULE}.{cal}_Carton_{var}"] = f"Carton of {c['name']} {label} Boxes{use}"
        names[f"{MODULE}.{cal}_Crate_{var}"] = f"Crate of {c['name']} {label} Boxes{use}"
    # GoM's plain rounds, named for what they are (translations merge by key, the later mod wins).
    names.update({
        'SWMG.9x39_Bullet': '9x39mm SP-5 Round',
        'MarzGuns.9x39_Box': '9x39mm SP-5 Box',
        'MarzGuns.9x39_Carton': 'Carton of 9x39mm SP-5 Boxes',
        'MarzGuns.9x39_Crate': 'Crate of 9x39mm SP-5 Boxes',
        'SWMG.545x39_Bullet': '5.45x39mm 7N6 Round',
        'MarzGuns.545x39_Box': '5.45x39mm 7N6 Box',
        'MarzGuns.545x39_Carton': 'Carton of 5.45x39mm 7N6 Boxes',
        'MarzGuns.545x39_Crate': 'Crate of 5.45x39mm 7N6 Boxes',
    })
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    recipes_tr = {}
    for per in sorted({CALIBRES[c]['per_box'] for c, _, _, _ in ROUNDS}):
        recipes_tr[f"GunsOfTien_OpenBoxOf{per}Bullets"] = f"Open Box ({per} Bullets)"
        recipes_tr[f"GunsOfTien_Place{per}BulletsInBox"] = f"Pack Ammo in Box ({per} Bullets)"
    recipes_tr.update({
        'GunsOfTien_OpenCartonOfBoxesOfAmmo': 'Open Carton of Ammo Boxes',
        'GunsOfTien_PlaceBoxesOfAmmoInCarton': 'Place Ammo Boxes in Carton',
        'GunsOfTien_OpenCrateOfBoxesOfAmmo': 'Open Crate of Ammo Boxes',
        'GunsOfTien_PlaceBoxesOfAmmoInCrates': 'Place Ammo Boxes in Crate',
    })
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(recipes_tr, indent=2) + '\n')


# Ammo Maker types this mod adds (shared/GunsOfTien/AmmoMaker.lua): type -> (English name, tooltip description).
AMMOMAKER_TYPES = [
    ('762x39SS', '7.62x39mm US', '7.62x39mm US sub sonic round - 1960s'),
    ('762x39SP', '7.62x39mm SP', '7.62x39mm SP soft point round - 1980s'),
    ('9x19ParaSS', '9mm Luger SS', '9mm Luger SS 147gr sub sonic round - 1988'),
    ('9x19ParaHP', '9mm Luger HP', '9mm Luger HP hollow point round - 1970s'),
    ('9x19ParaPPP', '9mm Luger +P+', '9mm Luger +P+ high pressure round - 1980s'),
    ('45ACPHP', '.45 ACP HP', '.45 ACP HP hollow point round - 1970s'),
    ('45ACPP', '.45 ACP +P', '.45 ACP +P high pressure round - 1980s'),
    ('3006SpringSP', '.30-06 Springfield SP', '.30-06 Springfield SP soft point round - 1910s'),
    ('308WinSP', '.308 Winchester SP', '.308 Winchester SP soft point round - 1952'),
    ('12Bird', '12 bore birdshot', '12 bore birdshot (aka. 12-gauge) - 18.5mm - 1860'),
]


def ammomaker():
    out = ["/* Placeholders Ammo Maker fills from shared/GunsOfTien/AmmoMaker.lua (recipe:Load at OnInitGlobalModData). */\n\nmodule Base {\n"]
    for name, _, _ in AMMOMAKER_TYPES:
        out.append(f"""
\tcraftRecipe Make{name}
\t{{
\t\ttimedAction = MakeAmmo,
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
\t\ttimedAction = ProduceAmmo,
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
    write('scripts/GunsOfTien/recipes_ammomaker.txt', ''.join(out))
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    recipes_tr = json.load(open(path))
    tooltips = {}
    for name, label, desc in AMMOMAKER_TYPES:
        recipes_tr[f"Make{name}"] = f"Make {label}"
        recipes_tr[f"Produce{name}"] = f"Produce {label}"
        tooltips[f"Tooltip_Recipe_Make{name}"] = f"Assemble {desc}"
        tooltips[f"Tooltip_Recipe_Produce{name}"] = f"Assemble {label} rounds with reloading press"
    # This mod's own Ammo Maker parts (scripts/GunsOfTien/items_ammomaker_parts.txt), named in Ammo Maker's style.
    recipes_tr.update({
        'GunsOfTien_MakeSoftPointBullet': 'Make Soft Point Bullet',
        'GunsOfTien_MakeBirdshot': 'Pour Birdshot Pellets',
        'GunsOfTien_ProduceBirdshot': 'Pour Birdshot Pellets (Furnace)',
    })
    tooltips.update({
        'Tooltip_Recipe_GunsOfTien_MakeSoftPointBullet': 'File the jacket off the nose of a standard rifle bullet so the lead shows',
        'Tooltip_Recipe_GunsOfTien_MakeBirdshot': 'Pour molten iron from small iron items through a strainer into water',
        'Tooltip_Recipe_GunsOfTien_ProduceBirdshot': 'Pour molten iron from a crucible through a strainer into water',
        'Tooltip_Item_GunsOfTien_BulletRifleSSP': 'Small size soft point rifle bullet. Craftable from standard bullets with a file',
        'Tooltip_Item_GunsOfTien_BulletRifleMSP': 'Medium size soft point rifle bullet. Craftable from standard bullets with a file',
        'Tooltip_Item_GunsOfTien_Birdshot': 'Birdshot pellets for shotgun shells. Poured through a strainer into water at any furnace',
        'Tooltip_Item_GunsOfTien_BoxBulletsRifleSSP': 'Box of 25 Bullets Rifle S SP',
        'Tooltip_Item_GunsOfTien_BoxBulletsRifleMSP': 'Box of 25 Bullets Rifle M SP',
        'Tooltip_Item_GunsOfTien_BoxBirdshot': 'Box of 25 Birdshot Pellets',
    })
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    names.update({
        'GunsOfTien.BulletRifleSSP': 'Bullet Rifle S SP',
        'GunsOfTien.BulletRifleMSP': 'Bullet Rifle M SP',
        'GunsOfTien.Birdshot': 'Birdshot Pellets',
        'GunsOfTien.BoxBulletsRifleSSP': 'Box Bullets Rifle S SP',
        'GunsOfTien.BoxBulletsRifleMSP': 'Box Bullets Rifle M SP',
        'GunsOfTien.BoxBirdshot': 'Box Birdshot Pellets',
    })
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(recipes_tr, indent=2) + '\n')
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tooltips, indent=2) + '\n')


if __name__ == '__main__':
    items()
    models()
    recipes()
    translations()
    ammomaker()
    print('written under', os.path.normpath(ROOT))
