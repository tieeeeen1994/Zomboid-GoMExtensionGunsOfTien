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
        # sentences end with a full stop (user, 2026-10-19), unlike Ammo Maker's own recipe tooltips
        tooltips[f"Tooltip_Recipe_Make{name}"] = f"Assemble {desc}."
        tooltips[f"Tooltip_Recipe_Produce{name}"] = f"Assemble {label} rounds with reloading press."
    # This mod's own Ammo Maker parts (scripts/GunsOfTien/items_ammomaker_parts.txt), named in Ammo Maker's style.
    recipes_tr.update({
        'GunsOfTien_MakeSoftPointBullet': 'Make Soft Point Bullet',
        'GunsOfTien_MakeBirdshot': 'Pour Birdshot Pellets',
        'GunsOfTien_ProduceBirdshot': 'Pour Birdshot Pellets (Furnace)',
    })
    tooltips.update({
        'Tooltip_Recipe_GunsOfTien_MakeSoftPointBullet': 'File the jacket off the nose of a standard rifle bullet so the lead shows.',
        'Tooltip_Recipe_GunsOfTien_MakeBirdshot': 'Pour molten iron from small iron items through a strainer into water.',
        'Tooltip_Recipe_GunsOfTien_ProduceBirdshot': 'Pour molten iron from a crucible through a strainer into water.',
        'Tooltip_Item_GunsOfTien_BulletRifleSSP': 'Small size soft point rifle bullet. Craftable from standard bullets with a file.',
        'Tooltip_Item_GunsOfTien_BulletRifleMSP': 'Medium size soft point rifle bullet. Craftable from standard bullets with a file.',
        'Tooltip_Item_GunsOfTien_Birdshot': 'Birdshot pellets for shotgun shells. Poured through a strainer into water at any furnace.',
        'Tooltip_Item_GunsOfTien_BoxBulletsRifleSSP': 'Box of 25 Bullets Rifle S SP',
        'Tooltip_Item_GunsOfTien_BoxBulletsRifleMSP': 'Box of 25 Bullets Rifle M SP',
        'Tooltip_Item_GunsOfTien_BoxBirdshot': 'Box of 25 Birdshot Pellets',
    })
    # The gun tooltip names each fitted part's row "Tooltip_weapon_<PartType>" (HandWeapon.DoTooltip); GoM and
    # Gunworks translate most part types but not these, which showed as raw keys (user, 2026-10-18). Animated1-9 are
    # the M60's visible belt rounds.
    tooltips.update({
        'Tooltip_weapon_LaserRifle': 'Laser',
        'Tooltip_weapon_LightRifle': 'Weapon Light',
        'Tooltip_weapon_BayonetIntegrated': 'Bayonet (Integrated)',
        'Tooltip_weapon_BayonetKnife': 'Bayonet',
        'Tooltip_weapon_BoosterScope': 'Magnifier',
        'Tooltip_weapon_Shellholder': 'Shell Holder',
        'Tooltip_weapon_UnderbarrelChamber': 'Underbarrel Chamber',
    })
    tooltips.update({'Tooltip_weapon_Animated%d' % n: 'Belt Round %d' % n for n in range(1, 10)})
    # Item tooltips GoM's scripts name but never translated (scripts/check_gom_translations.py lists them). Its break
    # action barrels are real, detachable parts (the _Open item is the same barrel with the action broken open, swapped
    # in by GoM's animations); GoM gives stats only to the double-barrel's sawn-off ones (AttachmentCustomStats.lua sets
    # Aiming Time 30, Hit Chance 70, spread 2.0, range 15 against the gun's 40 / 65 / 0.6 / 20, the same on all three
    # guns), and SawnStock.lua gives the Stevens 555's and TOZ-34's the same (user, 2026-10-19). The Masterkey's key is
    # a leftover name. The sawn-off barrels' stats are Information lines in GoM's attachment style (client
    # GunsOfTien/Tooltips.lua, user 2026-10-19), not part of this text.
    full = 'Full-length barrels for the %s.'
    sawn = 'Sawn-off barrels for the %s.'
    tooltips.update({
        'Tooltip_DOUBLEBARREL_Barrel_Close': full % 'double-barrel shotgun',
        'Tooltip_DOUBLEBARREL_Barrel_Open': full % 'double-barrel shotgun',
        'Tooltip_DOUBLEBARREL_Barrel_Sawnoff_Close': sawn % 'double-barrel shotgun',
        'Tooltip_DOUBLEBARREL_Barrel_Sawnoff_Open': sawn % 'double-barrel shotgun',
        'Tooltip_DOUBLE_DEUCE_Barrel_Close': full % 'Double Deuce',
        'Tooltip_DOUBLE_DEUCE_Barrel_Open': full % 'Double Deuce',
        'Tooltip_STEVENS_555_Barrel_Close': full % 'Stevens 555',
        'Tooltip_STEVENS_555_Barrel_Open': full % 'Stevens 555',
        'Tooltip_STEVENS_555_Barrel_Sawnoff_Close': sawn % 'Stevens 555',
        'Tooltip_TOZ34_Barrel_Close': full % 'TOZ-34',
        'Tooltip_TOZ34_Barrel_Open': full % 'TOZ-34',
        'Tooltip_TOZ34_Barrel_Sawnoff_Close': sawn % 'TOZ-34',
        'Tooltip_Rail': 'Underbarrel 12 gauge shotgun for the M16A2, 5 buckshot shells. Switch between rifle and '
                        'shotgun from the firearm radial menu.',
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
    # GoM items without a name: the hidden weapon a fitted bayonet stabs with, and explosion fragments (debris models)
    names['MarzGuns.Attack_Bayonet'] = 'Bayonet'
    names.update({'MarzGuns.frag_%d' % n: 'Fragment' for n in range(16)})
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(recipes_tr, indent=2) + '\n')
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tooltips, indent=2) + '\n')


# The lit laser's beam (shared/GunsOfTien/Lasers.lua, scripts/make_laser_beam.py): one hidden weapon part per GoM
# laser, fitted while it is lit and drawn by the engine at the gun's mount point for that laser (GoM's
# ModelWeaponPart lines: its rifle lasers on laser_right, its pistol lasers on underbarrel), then moved by the beam
# model's own attachment of the same name to the laser's lens. Lens = centre of the laser's lens in its own model
# space (game units, +Y forward, +Z up), measured on 2026-10-18 from front renders of GoM's pointers.fbx with its
# textures (the coloured aperture; AimRight's upper of its two, LRX-7's red one) and the mesh's front face.
# The beam models use shader gunsoftien_laser: vanilla's basicEffect without the lighting multiply, so the beam is
# always bright (scripts/make_laser_shader.py writes it into media/shaders).
LASER_LENS = {
    'AimRight_Laser': ('laser_right', (-0.0075, 0.0357, 0.0125)),
    'LRX-7_Laser': ('laser_right', (-0.0049, 0.0375, 0.0077)),
    'PJ-3_Laser': ('underbarrel', (0.0002, 0.0357, 0.0139)),
    'PX1_Laser': ('underbarrel', (0.0001, 0.0325, 0.0075)),
    'TR-1_Laser': ('underbarrel', (0.0002, 0.0260, 0.0080)),
}


def lasers():
    models = [f"module {MODULE} {{\n"]
    items = [f"module {MODULE} {{\n"]
    for laser, (point, (x, y, z)) in LASER_LENS.items():
        beam = 'LaserBeam_' + laser.replace('-', '')
        models.append(f"""
    model {beam} {{
        mesh     = weapons/parts/GunsOfTien_LaserBeam|GunsOfTien_LaserBeam,
        texture  = weapons/GunsOfTien/LaserBeam,
        shader   = gunsoftien_laser,
        cullFace = None,
        attachment {point} {{ offset = {x:.4f} {y:.4f} {z:.4f}, rotate = 0.0000 0.0000 0.0000, }}
    }}
""")
        items.append(f"""
    item {beam} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = LaserBeam,
        Weight          = 0.0,
        WeightModifier  = 0.0,
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    models.append("}\n")
    items.append("}\n")
    write('scripts/GunsOfTien/models_lasers.txt', ''.join(models))
    write('scripts/GunsOfTien/items_lasers.txt', ''.join(items))
    # the gun tooltip's row while it is lit ("Laser Beam: On")
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    for laser in LASER_LENS:
        names[f'{MODULE}.LaserBeam_' + laser.replace('-', '')] = 'On'
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tips = json.load(open(tip_path))
    tips['Tooltip_weapon_LaserBeam'] = 'Laser Beam'
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tips, indent=2) + '\n')


# The 9x19mm SMG suppressor (user, 2026-10-22): GoM's 9mm cans (M&P, Shh9 on its Pistol mount) fit its pistols only.
# AWC's Mk9 (12.0" x 2.0", AWC's can for the Uzi, MAC and MP5) on its own mount device (Tim Bixler's three-lug adapter),
# for the 9mm SMGs whose real barrels take a can: GoM's MP5 and MP5A2 (three-lug barrel) here, the UMP9 (threaded)
# appended by Post-93. Not the MP5K (flush end cap), the MP5SD (integral can) or the TEC-9 (user). Mesh and textures:
# scripts/build_mk9.py; icons: scripts/make_mk9_art.py; GoM's guns get the `canon` point and their ModelWeaponPart
# lines at run time (shared/GunsOfTien/Suppressors.lua). Weights as GoM's: its biggest cans 1.2, every mount 0.5.
SMG9_GUNS = 'MarzGuns.MP5;MarzGuns.MP5A2'
SMG9_PARTS = [('Mk9_Suppressor', 'Canon', 1.2, 'Mk9 Suppressor (9mm SMGs)'),
              ('SMG9_Muzzle_Mount_Device', 'CanonMount', 0.5, '9x19mm SMG Family Muzzle Mounting Device')]


def smg_suppressor():
    models = [f"module {MODULE} {{\n"]
    items = [f"module {MODULE} {{\n"]
    for part, ptype, weight, _ in SMG9_PARTS:
        models.append(f"""
    model {part} {{
        mesh     = weapons/parts/GunsOfTien_SMG9_parts|{part},
        texture  = weapons/GunsOfTien/{part},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
        items.append(f"""
    item {part} {{
        DisplayCategory  = WeaponPart,
        ItemType         = base:weaponpart,
        Icon             = GunsOfTien_{part},
        Weight           = {weight},
        WeightModifier   = {weight},
        MountOn          = {SMG9_GUNS},
        PartType         = {ptype},
        WorldStaticModel = {MODULE}.{part},
        CanAttach        = MarzGuns_AttachAndDetach.requiredTools,
        CanDetach        = MarzGuns_AttachAndDetach.requiredTools,
    }}
""")
    models.append("}\n")
    items.append("}\n")
    write('scripts/GunsOfTien/models_suppressors.txt', ''.join(models))
    write('scripts/GunsOfTien/items_suppressors.txt', ''.join(items))
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    for part, _, _, name in SMG9_PARTS:
        names[f'{MODULE}.{part}'] = name
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


# Sawn-off stocks (shared/GunsOfTien/SawnStock.lua, scripts/build_sawn_stocks.py): GoM's three break-action shotguns,
# the guns whose barrels GoM lets you saw off, get a hidden integrated stock part (the wooden stock, fitted at spawn)
# that the "Saw Off Shotgun Stock" recipe replaces with its sawn-off twin. The stockless body mesh is
# GunsOfTien_SawnStocks.fbx; Gunworks' ConditionalModel shows it while the sawn-off part is fitted: <GUN>_SAWNSTOCK
# with GoM's muzzle point (full barrels), <GUN>_SAWNSTOCK_SHORT with the muzzle at the end of GoM's sawn-off barrels
# (their mesh's front, measured 2026-10-19), so the flash leaves the real muzzle. The three holster points turn the
# upright rifle-held model the way GoM's pistols are modelled (upside down), as the P90's rifle_back does the other way.
# gun: (English name as GoM's barrel parts, GoM's muzzle offset, front of GoM's sawn-off barrel)
SAWN_STOCK_GUNS = {
    'DOUBLEBARREL': ('Double Barrel', (0.0, 0.4830, 0.0217), 0.3410),
    'STEVENS_555': ('Stevens 555', (0.0, 0.5418, 0.0250), 0.4180),
    'TOZ34': ('TOZ-34', (0.0, 0.5213, 0.0180), 0.3820),
}
SAWN_STOCK_WEIGHT = -0.5      # the buttstock sawn away (GoM's barrels: 3.0 full, 1.0 sawn off)
HOLSTER_POINTS = ('holster_right', 'holster_left', 'ShoulderHolster')
# The pieces sawn away are items (user, 2026-10-19), weighing what the gun or the barrels lose, so nothing appears or
# vanishes: the stock 0.5 (fuel and charcoal like Unusable Wood, which burns by weight), the barrel ends 2.0 (GoM's 3.0 ->
# 1.0; steel tagged "large" for smelting, 4 crucible uses = one Steel Bar, as vanilla's 2.0 Steel Bar). Meshes:
# build_sawn_stocks.py, bounds in sawn_offcuts.json; icons: make_offcut_art.py.
STOCK_OFFCUT_WEIGHT = -SAWN_STOCK_WEIGHT
BARREL_OFFCUTS_WEIGHT = 2.0
OFFCUT_BOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sawn_offcuts.json')


def floor_point(bounds):
    """The `world` point of an offcut: GoM's floor rotation for parts (90 0 -90, which the engine inverts: the model
    lies on its side, its x up), offset so that it rests on the floor (lowest x) centred along y and z."""
    (x0, y0, z0), (x1, y1, z1) = bounds
    return f"{x0:.4f} {(y0 + y1) / 2:.4f} {(z0 + z1) / 2:.4f}"


def sawn_stocks():
    offcuts = json.load(open(OFFCUT_BOUNDS))
    models = [f"module {MODULE} {{\n"]
    items = [f"module {MODULE} {{\n"]
    for gun, (_, (mx, my, mz), short_y) in SAWN_STOCK_GUNS.items():
        holsters = ''.join(f"""
        attachment {p} {{
            offset = 0.0000 0.0000 0.0000,
            rotate = -180.0000 0.0000 -180.0000,
        }}
""" for p in HOLSTER_POINTS)
        for suffix, y in (('', my), ('_SHORT', short_y)):
            models.append(f"""
    model {gun}_SAWNSTOCK{suffix} {{
        mesh     = weapons/firearms/GunsOfTien_SawnStocks|{gun}_BODY_SAWNSTOCK,
        texture  = weapons/firearms/shotguns/{gun},
        cullFace = None,

        attachment muzzle {{
            offset = {mx:.4f} {y:.4f} {mz:.4f},
            rotate = -90.0000 0.0000 -180.0000,
        }}

        attachment world {{
            offset = 0.0200 0.1300 0.0000,
            rotate = 180.0000 0.0000 180.0000,
        }}
{holsters}    }}
""")
        for item, node, bounds in (('StockOffcut', 'STOCK_OFFCUT', offcuts[gun]['stock']),
                                   ('BarrelOffcuts', 'BARREL_OFFCUTS', offcuts[gun]['barrels'])):
            models.append(f"""
    model {gun}_{item} {{
        mesh     = weapons/firearms/GunsOfTien_SawnStocks|{gun}_{node},
        texture  = weapons/firearms/shotguns/{gun},
        cullFace = None,

        attachment world {{
            offset = {floor_point(bounds)},
            rotate = 90.0000 0.0000 -90.0000,
        }}
    }}
""")
        items.append(f"""
    item {gun}_StockOffcut {{
        DisplayCategory  = Junk,
        ItemType         = base:normal,
        Weight           = {STOCK_OFFCUT_WEIGHT:.1f},
        Icon             = GunsOfTien_{gun}_StockOffcut,
        WorldStaticModel = {MODULE}.{gun}_StockOffcut,
        Tooltip          = Tooltip_GunsOfTien_StockOffcut,
        Tags             = base:isfirefuel;base:makewoodcharcoalsmall,
    }}

    item {gun}_BarrelOffcuts {{
        DisplayCategory  = Material,
        ItemType         = base:normal,
        Weight           = {BARREL_OFFCUTS_WEIGHT:.1f},
        Icon             = GunsOfTien_{gun}_BarrelOffcuts,
        WorldStaticModel = {MODULE}.{gun}_BarrelOffcuts,
        Tooltip          = Tooltip_GunsOfTien_BarrelOffcuts,
        Tags             = base:hasmetal;base:smeltablesteellarge,
    }}
""")
        for suffix, weight in (('', 0.0), ('_Sawnoff', SAWN_STOCK_WEIGHT)):
            items.append(f"""
    item {gun}_Stock{suffix} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = StockIntegrated,
        Weight          = 0.0,
        WeightModifier  = {weight:.1f},
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    models.append("}\n")
    items.append("}\n")
    guns = ';'.join(f"MarzGuns.{gun}" for gun in SAWN_STOCK_GUNS)
    recipe = f"""/* Sawing the walnut buttstock off GoM's break-action shotguns behind the pistol grip (shared/GunsOfTien/SawnStock.lua).
   Any saw cuts wood; the gun is kept and gets its sawn-off stock part in OnCreate, which also hands over the gun's own
   <GUN>_StockOffcut (one recipe for three guns, so no outputs block, as vanilla's gas mask filter recipes). */

module Base {{

	craftRecipe GunsOfTien_SawOffShotgunStock
	{{
		timedAction = SawOffShotgun,
		time = 150,
		OnTest = GunsOfTien_SawnStock.OnTest,
		OnCreate = GunsOfTien_SawnStock.OnCreate,
		ToolTip = Tooltip_Recipe_GunsOfTien_SawOffShotgunStock,
		Tags = InHandCraft,
		category = Weaponry,
		inputs
		{{
			item 1 tags[base:saw;base:smallsaw;base:metalsaw;base:crudesaw] mode:keep flags[Prop1;MayDegrade],
			item 1 [{guns}] mode:keep flags[Prop2],
		}}
	}}
}}
"""
    # GoM's barrel recipe uses vanilla's SawOffShotgun action, whose sound is the carpentry saw (Sawing, right for the
    # walnut stock); a hacksaw through steel barrels gets the metalworking one (CraftMetalSawing, vanilla's
    # SawSmallItemMetal). The game has only those two saw sounds. A recipe resolves its timedAction in OnScriptsLoaded,
    # before Lua, so SawnStock.lua hands this one to the action instead (ISHandcraftAction.new).
    timed = """/* The barrel cut's timed action (shared/GunsOfTien/SawnStock.lua): vanilla's SawOffShotgun with the metal sawing sound. */

module Base {

	timedAction GunsOfTien_SawOffShotgunBarrels
	{
		metabolics = MediumWork,
		actionAnim = SawOffShotgun,
		sound = CraftMetalSawing,
		prop1 = Base.Hacksaw,
		muscleStrainFactor = 0.0133,
		muscleStrainSkill = Strength,
		muscleStrainParts = Hand_R;ForeArm_R;UpperArm_R,
	}
}
"""
    write('scripts/GunsOfTien/timedactions_sawnstocks.txt', timed)
    write('scripts/GunsOfTien/models_sawnstocks.txt', ''.join(models))
    write('scripts/GunsOfTien/items_sawnstocks.txt', ''.join(items))
    write('scripts/GunsOfTien/recipes_sawnstocks.txt', recipe)
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    for gun, (name, _, _) in SAWN_STOCK_GUNS.items():
        # GoM's style: "Double Barrel" / "Double Barrel Sawnoff"; shown in the gun tooltip's "Stock (Integrated)" row
        names[f'{MODULE}.{gun}_Stock'] = f'{name} Stock'
        names[f'{MODULE}.{gun}_Stock_Sawnoff'] = f'{name} Stock Sawnoff'
        names[f'{MODULE}.{gun}_StockOffcut'] = f'{name} Stock Offcut'
        # GoM calls the Double Barrel's barrels "Double Barrel" and the others' "<gun> Barrel"
        names[f'{MODULE}.{gun}_BarrelOffcuts'] = f'{name} Offcuts' if gun == 'DOUBLEBARREL' else f'{name} Barrel Offcuts'
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    rec_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    rec = json.load(open(rec_path))
    rec['GunsOfTien_SawOffShotgunStock'] = 'Saw Off Shotgun Stock'
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(rec, indent=2) + '\n')
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tips = json.load(open(tip_path))
    tips['Tooltip_Recipe_GunsOfTien_SawOffShotgunStock'] = (
        "Saws the stock off behind the grip.")
    tips['Tooltip_GunsOfTien_StockOffcut'] = (
        "As good as scrap wood.")
    tips['Tooltip_GunsOfTien_BarrelOffcuts'] = (
        "As good as a steel bar.")
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tips, indent=2) + '\n')


if __name__ == '__main__':
    items()
    models()
    recipes()
    translations()
    ammomaker()
    lasers()
    sawn_stocks()
    smg_suppressor()
    print('written under', os.path.normpath(ROOT))
