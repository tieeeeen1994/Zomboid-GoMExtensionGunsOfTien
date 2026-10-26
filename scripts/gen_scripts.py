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
    # Ammo Maker is optional (as in Guns of Marz): without it AmmoMaker.lua hides these recipes. A recipe whose
    # timedAction does not exist throws in OnScriptsLoaded and stops that pass for every recipe after it, so the
    # placeholders use copies of Ammo Maker's MakeAmmo / ProduceAmmo (only its sound names, played when crafting).
    timed = """/* Ammo Maker's MakeAmmo / ProduceAmmo under names of our own, so the placeholders in recipes_ammomaker.txt load
   without Ammo Maker (a recipe whose timedAction is missing breaks script loading). Its sounds play only with it. */

module Base {

	timedAction GunsOfTien_MakeAmmo
	{
		metabolics = Default,
		actionAnim = Making,
		sound = MakeAmmo,
	}

	timedAction GunsOfTien_ProduceAmmo
	{
		metabolics = Default,
		actionAnim = Making,
		sound = ProduceAmmo,
	}
}
"""
    write('scripts/GunsOfTien/timedactions_ammomaker.txt', timed)
    out = ["/* Placeholders Ammo Maker fills from shared/GunsOfTien/AmmoMaker.lua (recipe:Load at OnInitGlobalModData), hidden without it. */\n\nmodule Base {\n"]
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
# The main mod's Uzis take it too (user, 2026-10-23: the real Mk9 took the Uzi barrel nut's place), listed in their
# own scripts (uzi() below).
SMG9_GUNS = 'MarzGuns.MP5;MarzGuns.MP5A2;GunsOfTien.UZI;GunsOfTien.MINIUZI;GunsOfTien.MICROUZI'
SMG9_PARTS = [('Mk9_Suppressor', 'Canon', 1.2, 'Mk9 Suppressor (9mm SMGs)'),
              ('SMG9_Muzzle_Mount_Device', 'CanonMount', 0.5, '9x19mm SMG Family Muzzle Mounting Device')]
# Both parts are built at GoM's SMG size (0.72 of real, GoM's MP5s), while Guns of Tien's own guns are drawn at the
# M16A2's proportion (0.603, user 2026-10-26): our Uzis and the UMP9 draw them through a second model of the same mesh,
# `<part>_GoT`, scaled down by as much (a gun's ModelWeaponPart line names the model it draws a part with).
GOT_PART_SCALE = round(0.000603 / 0.00072, 4)


# GoM's STANAG magazines at our size (user, 2026-10-26: "i want those with their own sizes"). GoM built them at 0.65
# of real size, as its rifles, and draws them so in its own ARs; our SCAR-L (Post-93) and M249, drawn at the M16A2's
# 0.603, draw them through `<magazine>_GoT`: GoM's mesh and texture with `scale` = 0.603 / 0.65 (a part model's own
# scale, about its origin: the feed lips at the gun's `magazine` point). `<magazine>_Hand` is a hidden item with that
# model, which M249.lua shows in the left hand during the M249's reload in place of GoM's (Gunworks puts an item of
# the magazine's type on the reload location, drawn with its own model). GoM's guns keep GoM's models.
STANAG_GOT_SCALE = round(0.000603 / 0.00065, 4)
STANAG_TEXTURE = {25: 20}           # GoM's 25-round magazine uses the 20-round's texture
STANAG_SIZES = (20, 25, 30, 50, 60, 75, 100, 150)


def stanag_got():
    gom_names = {20: 'STANAG 20Rds 5.56x45mm Magazine', 25: 'STANAG 25Rds 5.56x45mm Magazine',
                 30: 'STANAG 30Rds 5.56x45mm Magazine', 50: 'STANAG 50Rds 5.56x45mm Magazine',
                 60: 'STANAG 60Rds Jungle-Style 5.56x45mm Magazine', 75: 'STANAG 75Rds 5.56x45mm Magazine',
                 100: 'STANAG 100Rds 5.56x45mm Magazine', 150: 'STANAG 150Rds 5.56x45mm Magazine'}
    models = [f"module {MODULE} {{\n"]
    items = [f"module {MODULE} {{\n"]
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    for n in STANAG_SIZES:
        mag = f'556x45Magazine{n}_STANAG'
        tex = f'556x45Magazine{STANAG_TEXTURE.get(n, n)}_STANAG'
        models.append(f"""
    model {mag}_GoT {{
        mesh     = weapons/magazines/assault_rifles|{mag},
        texture  = weapons/magazines/assault_rifles/{tex},
        cullFace = None,
        scale    = {STANAG_GOT_SCALE:.4f},
    }}
""")
        items.append(f"""
    item {mag}_Hand {{
        DisplayCategory  = WeaponMagazine,
        ItemType         = base:normal,
        Icon             = {mag},
        Weight           = 0.0,
        Hidden           = true,
        StaticModel      = {MODULE}.{mag}_GoT,
        WorldStaticModel = {MODULE}.{mag}_GoT,
    }}
""")
        names[f'{MODULE}.{mag}_Hand'] = gom_names[n]
    models.append("}\n")
    items.append("}\n")
    write('scripts/GunsOfTien/models_stanag.txt', ''.join(models))
    write('scripts/GunsOfTien/items_stanag.txt', ''.join(items))
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


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

    model {part}_GoT {{
        mesh     = weapons/parts/GunsOfTien_SMG9_parts|{part},
        texture  = weapons/GunsOfTien/{part},
        scale    = {GOT_PART_SCALE:.4f},
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


# M249 Light Machine Gun (docs/design.md 4d, scripts/build_m249.py, shared/GunsOfTien/M249.lua): the PIP gun, fed from
# its own 200-round box or GoM's STANAG magazines, belt rounds as GoM's M60 shows its own (GoM's Bullet_1..9 parts,
# our round models), the feed cover as a part (closed, or open while reloading), GoM's M60 stats pattern.
M249_POINTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'm249_points.json')
M249_BOX = '556x45Box200_M249'
M249_STANAGS = ['556x45Magazine%s_STANAG' % n for n in (20, 25, 30, 50, 60, 75, 100, 150)]
M249_PARTS = [  # hidden integrated parts: (item, part type, weight, English name)
    ('M249_Feed_Cover_Closed', 'FeedCover', None, 'M249 Feed Cover (Closed)'),
    ('M249_Feed_Cover_Open', 'FeedCover', None, 'M249 Feed Cover (Open)'),
    ('M249_Integrated_Bipod_Folded', 'BipodIntegrated', None, 'M249 Integrated Bipod (Folded)'),
    ('M249_Integrated_Bipod_Deployed', 'BipodIntegrated', 0.7, 'M249 Integrated Bipod (Deployed)'),
]


def m249_attachment(name, point):
    o, r = point['offset'], point['rotate']
    return (f"        attachment {name} {{ offset = {o[0]:.4f} {o[1]:.4f} {o[2]:.4f}, "
            f"rotate = {r[0]:.4f} {r[1]:.4f} {r[2]:.4f}, }}\n")


def m249():
    pts = json.load(open(M249_POINTS))
    tex = 'weapons/GunsOfTien'
    out = [f"module {MODULE} {{\n", f"""
    model M249 {{
        mesh     = weapons/firearms/GunsOfTien_M249|M249_BODY,
        texture  = {tex}/M249,
        cullFace = None,
"""]
    for name in ('muzzle', 'world', 'magazine', 'box', 'belt', 'cover', 'cover_open', 'integrated_bipod'):
        out.append(m249_attachment(name, pts[name]))
    out.append("    }\n")
    for node in ('M249_COVER', 'M249_BIPOD_FOLDED', 'M249_BIPOD_DEPLOYED'):
        out.append(f"""
    model {node} {{
        mesh     = weapons/firearms/GunsOfTien_M249|{node},
        texture  = {tex}/M249,
        cullFace = None,
    }}
""")
    # the box lies on its side on the floor (floor_point), like the offcuts; the belt rounds share its texture
    b = pts['_bounds'][M249_BOX]
    out.append(f"""
    model {M249_BOX} {{
        mesh     = weapons/magazines/GunsOfTien_M249_box|{M249_BOX},
        texture  = {tex}/{M249_BOX},
        cullFace = None,
        attachment world {{ offset = {floor_point((b['min'], b['max']))}, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
    for i in range(1, 10):
        out.append(f"""
    model 556x45_M249_{i} {{
        mesh     = weapons/magazines/GunsOfTien_M249_box|556x45_M249_{i},
        texture  = {tex}/{M249_BOX},
        cullFace = None,
    }}
""")
    out.append("}\n")
    write('scripts/GunsOfTien/models_m249.txt', ''.join(out))

    w = "        ModelWeaponPart              = "
    parts = [f"{w}{MODULE}.M249_Feed_Cover_Closed {MODULE}.M249_COVER cover cover,",
             f"{w}{MODULE}.M249_Feed_Cover_Open {MODULE}.M249_COVER cover_open cover_open,",
             f"{w}{MODULE}.M249_Integrated_Bipod_Folded {MODULE}.M249_BIPOD_FOLDED integrated_bipod integrated_bipod,",
             f"{w}{MODULE}.M249_Integrated_Bipod_Deployed {MODULE}.M249_BIPOD_DEPLOYED integrated_bipod "
             f"integrated_bipod,",
             f"{w}{MODULE}.{M249_BOX} {MODULE}.{M249_BOX} box box,"]
    parts += [f"{w}MarzGuns.{m} {MODULE}.{m}_GoT magazine magazine," for m in M249_STANAGS]   # at our size
    parts += [f"{w}MarzGuns.Bullet_{i} {MODULE}.556x45_M249_{i} belt belt," for i in range(1, 10)]
    items = [f"module {MODULE} {{\n", f"""
    item M249 {{
        MinDamage                    = 1.0,
        MaxDamage                    = 1.8,
        CriticalChance               = 25.0,
        AimingPerkCritModifier       = 5,
        CritDmgMultiplier            = 4.0,
        HitChance                    = 35,
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = 60,
        RecoilDelay                  = 15,
        MaxRange                     = 55.0,
        AimingPerkRangeModifier      = 0,
        MinSightRange                = 10,
        MaxSightRange                = 18.0,
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = 0.9,
        ConditionLowerChanceOneIn    = 210,
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        StopPower                    = 1.8,
        DoorDamage                   = 5,
        Projectilecount              = 1,
        MaxHitcount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = 5.3,
        MetalValue                   = 45.0,
        FireMode                     = Auto,
        FireModePossibilities        = Auto,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = swmg:bullet_556x45,
        AmmoBox                      = MarzGuns.556x45_Box,
        MagazineType                 = {MODULE}.{M249_BOX},
        MaxAmmo                      = 200,
        Reloadtime                   = 25,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        Icon                         = GunsOfTien_M249,
        IdleAnim                     = Idle_Weapon2,
        RunAnim                      = Run_Weapon2,
        SwingAnim                    = Rifle,
        WeaponSprite                 = {MODULE}.M249,
        AimReleaseSound              = M16AimRelease,
        BreakSound                   = M16Break,
        BringToBearSound             = M16BringToBear,
        ClickSound                   = M16Jam,
        DropSound                    = M16Drop,
        EjectAmmoStartSound          = M16EjectAmmoStart,
        EjectAmmoSound               = M16EjectAmmo,
        EjectAmmoStopSound           = M16EjectAmmoStop,
        EquipSound                   = M16Equip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = M16InsertAmmoStart,
        InsertAmmoSound              = M16InsertAmmo,
        InsertAmmoStopSound          = M16InsertAmmoStop,
        RackSound                    = M16Rack,
        ShellFallSound               = M16CartridgeFall,
        SwingSound                   = M16Shoot,
        UnequipSound                 = M16UnEquip,
        SoundGain                    = 2.5,
        SoundRadius                  = 180,
        SoundVolume                  = 51,
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{chr(10).join(parts)}
        KnockBackOnNoDeath           = true,
        MultipleHitConditionAffected = false,
        ToHitModifier                = 1.5,
    }}

    item {M249_BOX} {{
        AmmoType         = swmg:bullet_556x45,
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTien_{M249_BOX},
        ItemType         = base:weaponpart,
        MaxAmmo          = 200,
        MountOn          = {MODULE}.M249,
        PartType         = Clip,
        Tags             = base:riflemagazine,
        Weight           = 0.8,
        WeightModifier   = 0.8,
        StaticModel      = {MODULE}.{M249_BOX},
        WorldStaticModel = {MODULE}.{M249_BOX},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
"""]
    for part, ptype, weight, _ in M249_PARTS:
        wl = f"        Weight          = {weight},\n        WeightModifier  = {weight},\n" if weight else ''
        items.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
{wl}        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write('scripts/GunsOfTien/items_m249.txt', ''.join(items))
    # GoM repairs both its machine guns with Aiming=6 (its M16A2: 3)
    write('scripts/GunsOfTien/fixing_m249.txt', f"""module Base {{
    fixing Fix M249 {{
        Require = {MODULE}.M249,
        Fixer   = MarzGuns.RepairPack; Aiming=6,
    }}
}}
""")
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    names[f'{MODULE}.M249'] = 'M249 Light Machine Gun'
    names[f'{MODULE}.{M249_BOX}'] = 'M249 200Rds 5.56x45mm Box'
    for part, _, _, name in M249_PARTS:
        names[f'{MODULE}.{part}'] = name
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tips = json.load(open(tip_path))
    tips['Tooltip_weapon_FeedCover'] = 'Feed Cover'          # the gun tooltip's row for the fitted cover part
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tips, indent=2) + '\n')


# Belt links (docs/design.md 4e, scripts/build_links.py, shared/GunsOfTien/BeltLinks.lua): the M249's M27 and GoM's
# M60's M13 disintegrating links, consumed when a belt box is filled and given back when it is fired or emptied.
# (item, box, per box, link weight, links made from one small metal sheet, English names). A box weighs 0.9 of its
# links, GoM's ammo box bonus, so packing always pays (user, 2026-10-25).
LINKS = [
    ('M27_Link', 'LinkBox_M27', 200, 0.002, 50, 'M27 5.56mm Belt Link', 'Box of M27 Belt Links'),
    ('M13_Link', 'LinkBox_M13', 100, 0.003, 40, 'M13 7.62mm Belt Link', 'Box of M13 Belt Links'),
]
LINKS_BOUNDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'links_bounds.json')


def belt_links():
    bounds = json.load(open(LINKS_BOUNDS))
    models, items = [f"module {MODULE} {{\n"], [f"module {MODULE} {{\n"]
    recipes = ["/* Belt links: open / pack a box of them, and stamp them from a small sheet of metal (vanilla's metalworking\n"
               "   tools; shared/GunsOfTien/BeltLinks.lua puts them to use). */\n\nmodule Base {\n"]
    for link, box, per, weight, made, link_name, box_name in LINKS:
        for node in (link, box):
            b = bounds[node]
            models.append(f"""
    model {node} {{
        mesh     = weapons/parts/GunsOfTien_Links|{node},
        texture  = weapons/GunsOfTien/{node},
        attachment world {{ offset = {floor_point((b['min'], b['max']))}, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
        items.append(f"""
    item {link} {{
        DisplayCategory  = AmmoParts,
        ItemType         = base:normal,
        Icon             = GunsOfTien_{link},
        WorldStaticModel = {MODULE}.{link},
        Weight           = {weight},
        Tags             = base:hasmetal,
        ToolTip          = Tooltip_Item_GunsOfTien_{link},
    }}

    item {box} {{
        DisplayCategory  = AmmoParts,
        ItemType         = base:normal,
        Icon             = GunsOfTien_{box},
        WorldStaticModel = {MODULE}.{box},
        Weight           = {round(per * weight * 0.9, 3)},
        ToolTip          = Tooltip_Item_GunsOfTien_{box},
    }}
""")
        recipes.append(f"""
    craftRecipe GunsOfTien_Open{box} {{
        timedAction = OpenAmmoBox,
        time        = 15,
        category    = Packing,
        recipeGroup = OpenBox,
        canWalk     = true,
        Tags        = InHandCraft;CanBeDoneInDark,
        inputs {{
            item 1 [{MODULE}.{box}] flags[Prop2;AllowFavorite;InheritFavorite],
        }}
        outputs {{
            item {per} {MODULE}.{link},
        }}
    }}

    craftRecipe GunsOfTien_Pack{box} {{
        timedAction = PlaceAmmoInBox,
        time        = 15,
        category    = Packing,
        canWalk     = true,
        Tags        = InHandCraft,
        inputs {{
            item {per} [{MODULE}.{link}] flags[AllowFavorite;InheritFavorite],
        }}
        outputs {{
            item 1 {MODULE}.{box},
        }}
    }}

    craftRecipe GunsOfTien_Make{link}s {{
        timedAction   = MakingHammer_Surface,
        time          = 300,
        Tags          = AnySurfaceCraft,
        SkillRequired = MetalWelding:2,
        xpAward       = MetalWelding:5,
        category      = AmmoMakerParts,
        NeedToBeLearn = False,
        ToolTip       = Tooltip_Recipe_GunsOfTien_Make{link}s,
        inputs {{
            item 1 [Base.SmallSheetMetal],
            item 1 tags[base:sheetmetalsnips] mode:keep flags[MayDegradeLight],
            item 1 tags[base:hammer] mode:keep flags[MayDegradeVeryLight],
            item 1 tags[base:metalworkingpunch] mode:keep flags[MayDegradeLight],
        }}
        outputs {{
            item {made} {MODULE}.{link},
        }}
    }}
""")
    models.append("}\n")
    items.append("}\n")
    recipes.append("}\n")
    write('scripts/GunsOfTien/models_links.txt', ''.join(models))
    write('scripts/GunsOfTien/items_links.txt', ''.join(items))
    write('scripts/GunsOfTien/recipes_links.txt', ''.join(recipes))
    # landing sounds of spent links (scripts/make_link_sounds.py), the events Hot Brass plays for its "Link" family
    # (shared/GunsOfTien/BeltLinks.lua); set up as Hot Brass's own casing sounds (volume 0.3, heard to 10 tiles)
    sounds = ["module Base\n{\n"]
    for surface in ('Concrete', 'Dirt', 'Grass', 'Puddles', 'Snow', 'Wood'):
        for n in range(1, 7):
            sounds.append(f"""    sound GunsOfTien_Link_{surface}_{n}
    {{
        category = Item,
        maxInstancesPerEmitter = 2,
        clip
        {{
            distanceMax = 10,
            volume = 0.3,
            file = media/sounds/gunsoftien_link_{surface.lower()}_{n:02d}.ogg,
        }}
    }}

""")
    sounds.append("}\n")
    write('scripts/GunsOfTien/sounds_links.txt', ''.join(sounds))
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    rec_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Recipes.json')
    rec = json.load(open(rec_path))
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tips = json.load(open(tip_path))
    for link, box, per, _, made, link_name, box_name in LINKS:
        names[f'{MODULE}.{link}'] = link_name
        names[f'{MODULE}.{box}'] = box_name
        short = link_name.split(' ')[0]                       # "M27"
        gun = 'M249' if short == 'M27' else 'M60'
        rec[f'GunsOfTien_Open{box}'] = f'Open {box_name}'
        rec[f'GunsOfTien_Pack{box}'] = f'Pack {link_name}s'
        rec[f'GunsOfTien_Make{link}s'] = f'Make {link_name}s'
        tips[f'Tooltip_Item_GunsOfTien_{link}'] = (
            f"Holds one round in the {gun}'s belt. Filling its belt box takes one link per round. Thrown out of the "
            f"gun when its round is fired.")
        tips[f'Tooltip_Item_GunsOfTien_{box}'] = f"{per} links, one {gun} belt."
        tips[f'Tooltip_Recipe_GunsOfTien_Make{link}s'] = f"Stamp {made} links out of a small sheet of metal."
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    write('lua/shared/Translate/EN/Recipes.json', json.dumps(rec, indent=2) + '\n')
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tips, indent=2) + '\n')


# Uzi, Mini Uzi and Micro Uzi (docs/design.md 4f, user 2026-10-23; meshes and points: scripts/build_uzi.py, icons:
# scripts/make_uzi_art.py, registries: shared/GunsOfTien/Uzi.lua). The Uzi is held as a rifle (GoM's MP5), the Mini
# and Micro like a pistol and holstered (GoM's MP5K / MAC-10: models upside down, Handgun swing, handgun reload
# mechanics; the Micro is HolsterSmall, as GoM's Detective .38, so it also fits vanilla's ankle holster: user, 2026-10-23,
# and every slot that takes Holster takes HolsterSmall too). One set of IMI magazines for all three. Stocks: the Uzi's two in-place nodes drawn at the origin (GoM's
# MAC-10 lines name a `stock` point its model lacks), the Mini's / Micro's one node at `stock` / `stock_folded`.
UZI_POINTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uzi_points.json')
UZIS = ['UZI', 'MINIUZI', 'MICROUZI']
UZI_MAGS = [(20, 0.08), (25, 0.12), (32, 0.15), (40, 0.2), (50, 0.22)]   # GoM's MP5 20 / 30 / 60: 0.08 / 0.18 / 0.22
UZI_NAMES = {'UZI': 'Uzi Submachine Gun', 'MINIUZI': 'Mini Uzi Submachine Gun',
             'MICROUZI': 'Micro Uzi Submachine Gun'}
# Real: 260 / 197 / 117 mm barrels, 3.5 / 2.7 / 1.95 kg, 600 / 950 / 1200 rpm. Damage and handling between GoM's MP5
# (8.9", 1.0-1.6) and MP5K (4.5", 0.6-1.0) by barrel; weights by GoM's SMG ratio (~0.78 of the kilograms); sound from
# sound_model.py's model (9mm from a 10.2" / 7.8" / 4.6" barrel; the main mod's SoundTable is for GoM's guns only).
UZI_STATS = {
    'UZI': dict(min=1.0, max=1.6, crit=20.0, hit=50, aim=40, recoil=15, range=30.0, stop=2.0, weight=2.7,
                radius=89, volume=25, sight=(4, 12.0), angle=(0.965, 0.01), knock=4.0, mag=32),
    'MINIUZI': dict(min=0.9, max=1.4, crit=20.0, hit=48, aim=30, recoil=13, range=27.0, stop=3.0, weight=2.1,
                    radius=97, volume=28, sight=(3, 11.0), angle=(0.96, 0.03), knock=3.0, mag=20),
    'MICROUZI': dict(min=0.6, max=1.0, crit=25.0, hit=45, aim=25, recoil=12, range=25.0, stop=4.0, weight=1.5,
                     radius=113, volume=32, sight=(2, 10.0), angle=(0.95, 0.05), knock=2.0, mag=20),
}
UZI_PARTS = [  # hidden integrated stocks: (item, part type, weight, English name); GoM's MAC-10 stock weighs 0.2
    ('UZI_Integrated_Stock_Folded', 'StockIntegrated', None, 'Uzi Integrated Stock (Folded)'),
    ('UZI_Integrated_Stock_Deployed', 'StockIntegrated', 0.2, 'Uzi Integrated Stock (Deployed)'),
    ('MINIUZI_Integrated_Stock_Folded', 'StockIntegrated', None, 'Mini Uzi Integrated Stock (Folded)'),
    ('MINIUZI_Integrated_Stock_Deployed', 'StockIntegrated', 0.2, 'Mini Uzi Integrated Stock (Deployed)'),
    ('MICROUZI_Integrated_Stock_Folded', 'StockIntegrated', None, 'Micro Uzi Integrated Stock (Folded)'),
    ('MICROUZI_Integrated_Stock_Deployed', 'StockIntegrated', 0.2, 'Micro Uzi Integrated Stock (Deployed)'),
]


def uzi_mag(rounds):
    return f'9x19Magazine{rounds}_UZI'


def uzi_item(gun):
    s = UZI_STATS[gun]
    rifle = gun == 'UZI'
    w = "        ModelWeaponPart              = "
    parts = [f"{w}MarzGuns.Bolt_Lock {MODULE}.{gun}_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {MODULE}.{gun}_BOLT bolt_fired bolt_fired,"]
    if rifle:
        parts += [f"{w}{MODULE}.UZI_Integrated_Stock_Folded {MODULE}.UZI_STOCK_FOLDED stock stock,",
                  f"{w}{MODULE}.UZI_Integrated_Stock_Deployed {MODULE}.UZI_STOCK_DEPLOYED stock stock,"]
    else:
        parts += [f"{w}{MODULE}.{gun}_Integrated_Stock_Folded {MODULE}.{gun}_STOCK stock_folded stock_folded,",
                  f"{w}{MODULE}.{gun}_Integrated_Stock_Deployed {MODULE}.{gun}_STOCK stock stock,"]
    parts += [f"{w}{MODULE}.{uzi_mag(r)} {MODULE}.{uzi_mag(r)} magazine magazine," for r, _ in UZI_MAGS]
    parts += [f"{w}{MODULE}.{p} {MODULE}.{p}_GoT canon canon," for p in ('SMG9_Muzzle_Mount_Device', 'Mk9_Suppressor')]
    # rifle-held as GoM's MP5 (M16 handling sounds, two hands, back slot); pistol-held as its MP5K (M9 sounds, holster).
    # The Mini Uzi is two-handed too, for the compact SMG stance (user: "let's require them to be 2-handed"; CLAUDE.md
    # "One-handed after equipping"); the Micro Uzi stays one-handed.
    snd = 'M16' if rifle else 'M9'
    # (2026-10-26, user: "they can be held in one hand, but they can also be held with 2 hands": no longer
    # RequiresEquippedBothHands; two hands by default, Equip Primary for one, shared OneHand.lua swaps model and reload)
    both_hands = """        TwoHandWeapon                = true,
""" if gun == 'MINIUZI' else ''
    hold = (f"""        AttachmentType               = Rifle,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        IdleAnim                     = Idle_Weapon2,
        SwingAnim                    = Rifle,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
""" if rifle else f"""        AttachmentType               = {'HolsterSmall' if gun == 'MICROUZI' else 'Holster'},
        WeaponReloadType             = handgun,
{both_hands}        SwingAnim                    = Handgun,
        MuzzleFlashModelKey          = muzzle_flash_handgun,
""")
    return f"""
    item {gun} {{
        MinDamage                    = {s['min']},
        MaxDamage                    = {s['max']},
        CriticalChance               = {s['crit']},
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 4.0,
        HitChance                    = {s['hit']},
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = {s['aim']},
        RecoilDelay                  = {s['recoil']},
        MaxRange                     = {s['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {s['sight'][0]},
        MaxSightRange                = {s['sight'][1]},
        MinRange                     = 0.61,
        MinAngle                     = {s['angle'][0]},
        AimingPerkMinAngleModifier   = {s['angle'][1]},
        JamGunChance                 = 1,
        ConditionLowerChanceOneIn    = 220,
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        StopPower                    = {s['stop']},
        DoorDamage                   = 5,
        Projectilecount              = 1,
        MaxHitcount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {s['weight']},
        MetalValue                   = 30.0,
        FireMode                     = Auto,
        FireModePossibilities        = Auto/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = swmg:bullet_9x19,
        AmmoBox                      = MarzGuns.9x19_Box,
        ClipSize                     = {s['mag']},
        MagazineType                 = {MODULE}.{uzi_mag(s['mag'])},
        MaxAmmo                      = {s['mag']},
        Reloadtime                   = {25 if rifle else 30},
{hold}        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        Icon                         = GunsOfTien_{gun},
        RunAnim                      = Run_Weapon2,
        WeaponSprite                 = {MODULE}.{gun},
        AimReleaseSound              = {snd}AimRelease,
        BreakSound                   = {snd}Break,
        BringToBearSound             = {snd}BringToBear,
        ClickSound                   = {snd}Jam,
        DropSound                    = M9Drop,
        EjectAmmoStartSound          = M9EjectAmmoStart,
        EjectAmmoSound               = M9EjectAmmo,
        EjectAmmoStopSound           = M9EjectAmmoStop,
        EquipSound                   = {snd}Equip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = M9InsertAmmoStart,
        InsertAmmoSound              = M9InsertAmmo,
        InsertAmmoStopSound          = M9InsertAmmoStop,
        RackSound                    = {snd}Rack,
        ShellFallSound               = M9CartridgeFall,
        SwingSound                   = M9Shoot,
        UnequipSound                 = {snd}UnEquip,
        SoundGain                    = {2.0 if rifle else 1.5},
        SoundRadius                  = {s['radius']},
        SoundVolume                  = {s['volume']},
        NPCSoundBoost                = 1.5,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{chr(10).join(parts)}
        KnockBackOnNoDeath           = true,
        KnockdownMod                 = {s['knock']},
        MultipleHitConditionAffected = false,
        ToHitModifier                = 1.5,
    }}
"""


def uzi():
    pts = json.load(open(UZI_POINTS))
    tex = 'weapons/GunsOfTien'
    models = [f"module {MODULE} {{\n"]
    for gun in UZIS:
        p = pts[gun]
        models.append(f"""
    model {gun} {{
        mesh     = weapons/firearms/GunsOfTien_{gun}|{gun}_BODY,
        texture  = {tex}/{gun},
        cullFace = None,
""")
        for name in ('muzzle', 'world', 'magazine', 'canon', 'bolt_fired', 'stock', 'stock_folded'):
            if name in p:
                models.append(m249_attachment(name, p[name]))
        models.append("    }\n")
        if gun == 'MINIUZI':
            # held in one hand (OneHand.lua): the same model, not turned upright by CompactStance.lua, so vanilla's
            # pistol clips draw it the right way up
            body = models[-1 - sum(1 for name in ('muzzle', 'world', 'magazine', 'canon', 'bolt_fired', 'stock',
                                                  'stock_folded') if name in p) - 1:]
            models.append("".join(body).replace("    model MINIUZI {", "    model MINIUZI_1H {", 1))
        nodes = ['BOLT'] + (['STOCK_FOLDED', 'STOCK_DEPLOYED'] if gun == 'UZI' else ['STOCK'])
        for node in nodes:
            models.append(f"""
    model {gun}_{node} {{
        mesh     = weapons/firearms/GunsOfTien_{gun}|{gun}_{node},
        texture  = {tex}/{gun},
        cullFace = None,
    }}
""")
    for r, _ in UZI_MAGS:
        models.append(f"""
    model {uzi_mag(r)} {{
        mesh     = weapons/magazines/GunsOfTien_UZI_magazines|{uzi_mag(r)},
        texture  = {tex}/{uzi_mag(r)},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
    models.append("}\n")
    write('scripts/GunsOfTien/models_uzi.txt', ''.join(models))

    items = [f"module {MODULE} {{\n"] + [uzi_item(gun) for gun in UZIS]
    guns = ';'.join(f'{MODULE}.{g}' for g in UZIS)
    for r, weight in UZI_MAGS:
        items.append(f"""
    item {uzi_mag(r)} {{
        AmmoType         = swmg:bullet_9x19,
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTien_{uzi_mag(r)},
        ItemType         = base:weaponpart,
        MaxAmmo          = {r},
        MountOn          = {guns},
        PartType         = Clip,
        Tags             = base:hasmetal;base:riflemagazine,
        Weight           = {weight},
        WeightModifier   = {weight},
        StaticModel      = {MODULE}.{uzi_mag(r)},
        WorldStaticModel = {MODULE}.{uzi_mag(r)},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
""")
    for part, ptype, weight, _ in UZI_PARTS:
        wl = f"        Weight          = {weight},\n        WeightModifier  = {weight},\n" if weight else ''
        items.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
{wl}        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write('scripts/GunsOfTien/items_uzi.txt', ''.join(items))
    # GoM repairs its SMGs with Aiming=3
    write('scripts/GunsOfTien/fixing_uzi.txt', "module Base {\n" + ''.join(f"""    fixing Fix {gun} {{
        Require = {MODULE}.{gun},
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
""" for gun in UZIS) + "}\n")
    names_path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(names_path))
    for gun in UZIS:
        names[f'{MODULE}.{gun}'] = UZI_NAMES[gun]
    for r, _ in UZI_MAGS:      # GoM's names ("MP5 30Rds 9x19mm Magazine", "MAC-10 40Rds .45 ACP Extended Magazine")
        names[f'{MODULE}.{uzi_mag(r)}'] = f"Uzi {r}Rds 9x19mm {'Extended ' if r >= 40 else ''}Magazine"
    for part, _, _, name in UZI_PARTS:
        names[f'{MODULE}.{part}'] = name
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


# GoM's MP5K held in one hand (OneHand.lua): GoM's model (MarzGuns/models/weapons/smgs.txt, Guns of Marz 42.16) under
# our module, without the turn CompactStance.lua gives GoM's own in the hand, so vanilla's pistol clips draw it the right
# way up. OneHand.lua copies GoM's live mesh, texture and points over it at game start (a GoM update stays in step).
MP5K_1H = """module GunsOfTien {

    model MP5K_1H {
        mesh     = weapons/firearms/MP5K|MP5K_BODY,
        texture  = weapons/firearms/smgs/MP5K,
        cullFace = None,
        attachment muzzle {
            offset = 0.0000 0.2202 -0.0445,
            rotate = -90.0000 0.0000 -180.0000,
        }
        attachment world {
            offset = -0.0250 -0.0000 -0.0000,
            rotate = 0.0000 0.0000 0.0000,
        }
        attachment bolt_fired {
            offset = 0.0000 -0.0297 0.0000,
            rotate = 0.0000 0.0000 0.0000,
        }
        attachment magazine {
            offset = 0.0000 0.1196 -0.0388,
            rotate = 171.7924 0.0000 180.0000,
        }
        attachment rail_up {
            offset = 0.0000 0.1153 -0.0663,
            rotate = -180.0000 0.0000 -180.0000,
        }
        attachment scope {
            offset = 0.0000 0.1292 -0.0693,
            rotate = -180.0000 0.0000 -180.0000,
        }
        attachment canon {
            offset = 0.0000 0.2252 -0.0408,
            rotate = 0.0000 0.0000 0.0000,
        }
    }
}
"""


def one_hand():
    write('scripts/GunsOfTien/models_onehand.txt', MP5K_1H)


if __name__ == '__main__':
    items()
    models()
    recipes()
    translations()
    ammomaker()
    lasers()
    sawn_stocks()
    smg_suppressor()
    stanag_got()
    m249()
    belt_links()
    uzi()
    one_hand()
    print('written under', os.path.normpath(ROOT))
