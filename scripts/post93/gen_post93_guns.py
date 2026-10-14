"""Writes the MP7A1 / P90 TR item and model scripts, their parts, repair recipes and names for Guns of Tien - Post-93.

Run after the model builders (build_mp7.py / build_p90.py), which write the attachment points to mp7_points.json and
p90_points.json next to this script: python3 scripts/post93/gen_post93_guns.py
Icons are item_GunsOfTienPost93_<name>.png (prefixed, so another mod's MP7 or P90 icon cannot replace them).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', 'Contents', 'mods', 'GoMExtensionGunsOfTienPost93', '42', 'media')
M = 'GunsOfTienPost93'
TEX = 'weapons/GunsOfTienPost93'

# GoM accessories the guns can carry, drawn at the gun's points (same lists as the MP5's ModelWeaponPart lines).
OPTICS = ['EXPS1_Sight', 'EXPS3_Sight', 'ElcanX2_Scope', 'LR10X_Scope', 'Aimpoint_Sight', 'TA28_Scope', 'LR4X_Scope',
          'OKP3_Sight', 'ReflexS2_Sight', 'JS14_Sight', 'Kobra_Sight', 'TR06X_Scope', 'PSO1_Scope', 'LRX12X_Scope']
LASERS = ['AimRight_Laser', 'LRX-7_Laser']
LIGHTS = ['BrightPoint-5_Light', 'SR7_Light']


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)


def load_points(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def vec(value):
    """A point from the builders' JSON: [x, y, z], {"x":..}, or {"offset": [...], "rotate": [...]}."""
    if isinstance(value, dict):
        if 'offset' in value:
            return vec(value['offset'])
        if 'x' in value:
            return [value['x'], value['y'], value['z']]
    return list(value)


def rot(value):
    if isinstance(value, dict) and 'rotate' in value:
        return list(value['rotate'])
    return None


def attachment(name, value, rotate=None):
    o = vec(value)
    r = rotate if rotate is not None else rot(value)
    line = f"        attachment {name} {{ offset = {o[0]:.4f} {o[1]:.4f} {o[2]:.4f},"
    if r is not None:
        line += f" rotate = {r[0]:.4f} {r[1]:.4f} {r[2]:.4f},"
    return line + " }\n"


def gun_model(model, file, node_body, points, extra_points):
    out = f"""
    model {model} {{
        mesh     = weapons/firearms/{file}|{node_body},
        texture  = {TEX}/{model},
        cullFace = None,
"""
    out += attachment('muzzle', points['muzzle'], rot(points['muzzle']) or [-90, 0, -180])
    out += attachment('world', points.get('world', [0.02, 0.13, 0]), rot(points.get('world', {})) or [180, 0, 180])
    for name in ['magazine', 'scope', 'rail_up', 'rail_left', 'rail_right', 'laser_right', 'light_left', 'canon',
                 'bolt_fired'] + extra_points:
        if name in points:
            out += attachment(name, points[name])
    return out + "    }\n"


def models(mp7, p90):
    out = [f"module {M} {{\n"]
    out.append(gun_model('MP7A1', 'GunsOfTienPost93_MP7A1', 'MP7A1_BODY', mp7, ['stock_folded']))
    out.append(gun_model('P90TR', 'GunsOfTienPost93_P90TR', 'P90TR_BODY', p90, []))
    for model, file, node, tex in [
            ('MP7A1_BOLT', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_BOLT', 'MP7A1'),
            ('MP7A1_STOCK', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_STOCK', 'MP7A1'),
            ('P90TR_BOLT', 'firearms/GunsOfTienPost93_P90TR', 'P90TR_BOLT', 'P90TR')]:
        out.append(f"""
    model {model} {{
        mesh     = weapons/{file}|{node},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    parts = [(f'46x30Magazine{n}_MP7', 'magazines/GunsOfTienPost93_MP7_magazines') for n in (20, 30, 40)]
    parts += [('57x28Magazine50_P90', 'magazines/GunsOfTienPost93_P90_magazines')]
    parts += [(p, 'parts/GunsOfTienPost93_MP7_parts') for p in ('MP7_Suppressor', 'MP7_Muzzle_Mount_Device')]
    parts += [(p, 'parts/GunsOfTienPost93_P90_parts') for p in ('P90_Suppressor', 'P90_Muzzle_Mount_Device')]
    for node, file in parts:
        out.append(f"""
    model {node} {{
        mesh     = weapons/{file}|{node},
        texture  = {TEX}/{node},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_guns.txt', ''.join(out))


def model_parts(gun, mags, rails, suppressor, mount, stock):
    lines = [f"        ModelWeaponPart              = MarzGuns.Bolt_Lock {M}.{gun}_BOLT bolt_lock bolt_lock,",
             f"        ModelWeaponPart              = MarzGuns.Bolt_Fired {M}.{gun}_BOLT bolt_fired bolt_fired,"]
    if stock:
        lines += [f"        ModelWeaponPart              = {M}.{gun}_Integrated_Stock_Folded {M}.{gun}_STOCK stock_folded stock_folded,",
                  f"        ModelWeaponPart              = {M}.{gun}_Integrated_Stock_Deployed {M}.{gun}_STOCK stock stock,"]
    lines += [f"        ModelWeaponPart              = {M}.{m} {M}.{m} magazine magazine," for m in mags]
    lines += [f"        ModelWeaponPart              = {M}.{mount} {M}.{mount} canon canon,",
              f"        ModelWeaponPart              = {M}.{suppressor} {M}.{suppressor} canon canon,"]
    lines += [f"        ModelWeaponPart              = MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"        ModelWeaponPart              = MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"        ModelWeaponPart              = MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


GUN_COMMON = """        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        FireMode                     = Auto,
        FireModePossibilities        = Auto/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        IdleAnim                     = Idle_Weapon2,
        RunAnim                      = Run_Weapon2,
        SwingAnim                    = Rifle,
        AimReleaseSound              = M16AimRelease,
        BreakSound                   = M16Break,
        BringToBearSound             = M16BringToBear,
        ClickSound                   = M16Jam,
        DropSound                    = M1911Drop,
        EjectAmmoStartSound          = M1911EjectAmmoStart,
        EjectAmmoSound               = M1911EjectAmmo,
        EjectAmmoStopSound           = M1911EjectAmmoStop,
        EquipSound                   = M1911Equip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = M1911InsertAmmoStart,
        InsertAmmoSound              = M1911InsertAmmo,
        InsertAmmoStopSound          = M1911InsertAmmoStop,
        RackSound                    = M16Rack,
        ShellFallSound               = M16CartridgeFall,
        SwingSound                   = M9Shoot,
        UnequipSound                 = M16UnEquip,
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
        KnockBackOnNoDeath           = true,
        KnockdownMod                 = 3.0,
        MultipleHitConditionAffected = false,
        ToHitModifier                = 1.5,
        JamGunChance                 = 1,
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        DoorDamage                   = 5,
        Projectilecount              = 1,
        PiercingBullets              = true,
        MaxHitcount                  = 2,
"""


def items(mp7, p90):
    mp7_mags = [f'46x30Magazine{n}_MP7' for n in (20, 30, 40)]
    p90_mags = ['57x28Magazine50_P90']
    out = [f"module {M} {{\n    imports {{ Base }}\n"]
    # Realistic sound (the main mod's model, M16 = 175 / 50): 4.6x30 ~6 gr, 180 mm barrel; 5.7x28 ~6.7 gr, 263 mm.
    out.append(f"""
    item MP7A1 {{
        MinDamage                    = 0.9,
        MaxDamage                    = 1.4,
        CriticalChance               = 20.0,
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 4.0,
        HitChance                    = 52,
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = 35,
        RecoilDelay                  = 12,
        MaxRange                     = 28.0,
        AimingPerkRangeModifier      = 0,
        MinSightRange                = 3,
        MaxSightRange                = 12.0,
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        ConditionLowerChanceOneIn    = 220,
        StopPower                    = 2.0,
        Weight                       = 1.9,
        MetalValue                   = 25.0,
{GUN_COMMON}        AmmoType                     = gunsoftienpost93:bullet_46x30,
        AmmoBox                      = {M}.46x30_Box,
        MagazineType                 = {M}.46x30Magazine20_MP7,
        MaxAmmo                      = 20,
        Reloadtime                   = 22,
        Icon                         = GunsOfTienPost93_MP7A1,
        WeaponSprite                 = {M}.MP7A1,
        SoundGain                    = 1.6,
        SoundRadius                  = 114,
        SoundVolume                  = 33,
{model_parts('MP7A1', mp7_mags, None, 'MP7_Suppressor', 'MP7_Muzzle_Mount_Device', True)}    }}

    item P90TR {{
        MinDamage                    = 1.0,
        MaxDamage                    = 1.5,
        CriticalChance               = 20.0,
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 4.0,
        HitChance                    = 55,
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = 35,
        RecoilDelay                  = 12,
        MaxRange                     = 32.0,
        AimingPerkRangeModifier      = 0,
        MinSightRange                = 4,
        MaxSightRange                = 14.0,
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        ConditionLowerChanceOneIn    = 220,
        StopPower                    = 2.0,
        Weight                       = 2.6,
        MetalValue                   = 25.0,
{GUN_COMMON}        AmmoType                     = gunsoftienpost93:bullet_57x28,
        AmmoBox                      = {M}.57x28_Box,
        MagazineType                 = {M}.57x28Magazine50_P90,
        MaxAmmo                      = 50,
        Reloadtime                   = 28,
        Icon                         = GunsOfTienPost93_P90TR,
        WeaponSprite                 = {M}.P90TR,
        SoundGain                    = 1.7,
        SoundRadius                  = 118,
        SoundVolume                  = 34,
{model_parts('P90TR', p90_mags, None, 'P90_Suppressor', 'P90_Muzzle_Mount_Device', False)}    }}
""")
    for mag, cap, weight, ammo, guns in [(mp7_mags[0], 20, 0.12, 'bullet_46x30', 'MP7A1'),
                                         (mp7_mags[1], 30, 0.17, 'bullet_46x30', 'MP7A1'),
                                         (mp7_mags[2], 40, 0.22, 'bullet_46x30', 'MP7A1'),
                                         (p90_mags[0], 50, 0.40, 'bullet_57x28', 'P90TR')]:
        out.append(f"""
    item {mag} {{
        AmmoType         = gunsoftienpost93:{ammo},
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {M}.{guns},
        PartType         = Clip,
        Tags             = base:hasmetal;base:riflemagazine,
        Weight           = {weight},
        WeightModifier   = {weight},
        StaticModel      = {M}.{mag},
        WorldStaticModel = {M}.{mag},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
""")
    for part, ptype, weight in [('MP7A1_Integrated_Stock_Folded', 'StockIntegrated', None),
                                ('MP7A1_Integrated_Stock_Deployed', 'StockIntegrated', 0.2),
                                ('MP7A1_Integrated_Rail_Up', 'RailUp', None),
                                ('MP7A1_Integrated_Rail_Left', 'RailLeft', None),
                                ('MP7A1_Integrated_Rail_Right', 'RailRight', None),
                                ('P90TR_Integrated_Rail_Up', 'RailUp', None),
                                ('P90TR_Integrated_Rail_Left', 'RailLeft', None),
                                ('P90TR_Integrated_Rail_Right', 'RailRight', None)]:
        w = f"        Weight          = {weight},\n        WeightModifier  = {weight},\n" if weight else ''
        out.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
{w}        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    for part, ptype, weight, gun in [('MP7_Suppressor', 'Canon', 0.35, 'MP7A1'),
                                     ('MP7_Muzzle_Mount_Device', 'CanonMount', 0.1, 'MP7A1'),
                                     ('P90_Suppressor', 'Canon', 0.4, 'P90TR'),
                                     ('P90_Muzzle_Mount_Device', 'CanonMount', 0.1, 'P90TR')]:
        out.append(f"""
    item {part} {{
        DisplayCategory  = WeaponPart,
        ItemType         = base:weaponpart,
        Icon             = GunsOfTienPost93_{part},
        Weight           = {weight},
        WeightModifier   = {weight},
        MountOn          = {M}.{gun},
        PartType         = {ptype},
        WorldStaticModel = {M}.{part},
        CanAttach        = MarzGuns_AttachAndDetach.requiredTools,
        CanDetach        = MarzGuns_AttachAndDetach.requiredTools,
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/items_guns.txt', ''.join(out))
    write(f'scripts/{M}/fixing_guns.txt', f"""module Base {{
    fixing Fix MP7A1 {{
        Require = {M}.MP7A1,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix P90TR {{
        Require = {M}.P90TR,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
}}
""")


def translations():
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(path)) if os.path.exists(path) else {}
    names.update({
        f'{M}.MP7A1': 'H&K MP7A1 Personal Defense Weapon',
        f'{M}.P90TR': 'FN P90 TR Personal Defense Weapon',
        f'{M}.46x30Magazine20_MP7': 'MP7 20Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine30_MP7': 'MP7 30Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine40_MP7': 'MP7 40Rds 4.6x30mm Magazine',
        f'{M}.57x28Magazine50_P90': 'P90 50Rds 5.7x28mm Magazine',
        f'{M}.MP7A1_Integrated_Stock_Folded': 'MP7A1 Integrated Stock (Collapsed)',
        f'{M}.MP7A1_Integrated_Stock_Deployed': 'MP7A1 Integrated Stock (Extended)',
        f'{M}.MP7A1_Integrated_Rail_Up': 'MP7A1 Integrated Rail (Up)',
        f'{M}.MP7A1_Integrated_Rail_Left': 'MP7A1 Integrated Rail (Left)',
        f'{M}.MP7A1_Integrated_Rail_Right': 'MP7A1 Integrated Rail (Right)',
        f'{M}.P90TR_Integrated_Rail_Up': 'P90 TR Integrated Rail (Up)',
        f'{M}.P90TR_Integrated_Rail_Left': 'P90 TR Integrated Rail (Left)',
        f'{M}.P90TR_Integrated_Rail_Right': 'P90 TR Integrated Rail (Right)',
        f'{M}.MP7_Suppressor': 'MP7 Suppressor (4.6x30mm)',
        f'{M}.MP7_Muzzle_Mount_Device': 'MP7 Muzzle Mount Device',
        f'{M}.P90_Suppressor': 'P90 Suppressor (5.7x28mm)',
        f'{M}.P90_Muzzle_Mount_Device': 'P90 Muzzle Mount Device',
    })
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    mp7 = load_points('mp7_points.json')
    p90 = load_points('p90_points.json')
    models(mp7, p90)
    items(mp7, p90)
    translations()
    print('written under', os.path.normpath(ROOT))
