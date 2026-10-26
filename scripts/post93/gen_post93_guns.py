"""Writes the MP7A1 / P90 TR / Five-seveN / UCP Prototype / SCAR-L / SCAR-H / UMP45 / UMP9 item and model scripts, their
parts, repair recipes and names for Guns of Tien - Post-93.

Run after the model builders (build_mp7.py / build_p90.py / build_fiveseven.py / build_ucp.py / build_scar.py /
build_ump.py), which write the attachment points to mp7_points.json, p90_points.json, fiveseven_points.json,
ucp_points.json, scarl_points.json, scarh_points.json and ump_points.json next to this script:
python3 scripts/post93/gen_post93_guns.py
The Five-seveN is the item MarzGuns.FIVESEVEN: Guns of Marz names it ("5.7x28mm Five-SeveN" in its ItemName.json) but
ships nothing else, so its item block (items_fiveseven.txt) is in GoM's module and everything it uses is ours.
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


def pistol_model(name, points):
    """GoM's pistol model scripts (its Glock 17): the points it uses, each with GoM's rotate; body + slide."""
    out = f"""
    model {name} {{
        mesh     = weapons/firearms/GunsOfTienPost93_{name}|{name}_BODY,
        texture  = {TEX}/{name},
        cullFace = None,
"""
    for point in ('muzzle', 'slide_fired', 'world', 'rail_up', 'scope', 'underbarrel', 'canon'):
        out += attachment(point, points[point])
    return out + f"""    }}

    model {name}_SLIDE {{
        mesh     = weapons/firearms/GunsOfTienPost93_{name}|{name}_SLIDE,
        texture  = {TEX}/{name},
        cullFace = None,
    }}
"""


def models(mp7, mp7a2, p90, fiveseven, ucp, scarl, scarh, ump):
    out = [f"module {M} {{\n"]
    out.append(gun_model('MP7A1', 'GunsOfTienPost93_MP7A1', 'MP7A1_BODY', mp7,
                         ['stock_folded', 'foregrip_deployed', 'rifle_back', 'rifle_back_bag']))
    # the MP7A2's body and texture are its own; bolt and stock are the A1's models (MP7A1_BOLT / MP7A1_STOCK)
    out.append(gun_model('MP7A2', 'GunsOfTienPost93_MP7A2', 'MP7A2_BODY', mp7a2,
                         ['stock_folded', 'rail_down', 'foregrip', 'rifle_back', 'rifle_back_bag']))
    out.append(gun_model('P90TR', 'GunsOfTienPost93_P90TR', 'P90TR_BODY', p90, ['rifle_back', 'rifle_back_bag']))
    out.append(pistol_model('FIVESEVEN', fiveseven))
    out.append(pistol_model('UCP', ucp))
    scar_points = ['stock', 'stock_folded', 'rail_down', 'foregrip', 'bipod']
    out.append(gun_model('SCARL', 'GunsOfTienPost93_SCARL', 'SCARL_BODY', scarl, scar_points))
    out.append(gun_model('SCARH', 'GunsOfTienPost93_SCARH', 'SCARH_BODY', scarh, scar_points))
    # both UMPs are one mesh (UMP_BODY) with their own textures (markings); bolt and stock shared
    for gun in UMPS:
        out.append(gun_model(gun, 'GunsOfTienPost93_UMP', 'UMP_BODY', ump, ['stock', 'stock_folded', 'rail_down', 'foregrip']))
    for model, file, node, tex in [
            ('SCARL_BOLT', 'firearms/GunsOfTienPost93_SCARL', 'SCARL_BOLT', 'SCARL'),
            ('SCARH_BOLT', 'firearms/GunsOfTienPost93_SCARH', 'SCARH_BOLT', 'SCARH'),
            # one folding stock for both SCARs, drawn at each gun's stock / stock_folded point
            ('SCAR_STOCK', 'parts/GunsOfTienPost93_SCAR_parts', 'SCAR_STOCK', 'SCAR_STOCK'),
            # the charging handle's texels are the same in both UMP textures
            ('UMP_BOLT', 'firearms/GunsOfTienPost93_UMP', 'UMP_BOLT', 'UMP9'),
            ('UMP_STOCK', 'parts/GunsOfTienPost93_UMP_parts', 'UMP_STOCK', 'UMP_STOCK'),
            ('MP7A1_BOLT', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_BOLT', 'MP7A1'),
            ('MP7A1_STOCK', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_STOCK', 'MP7A1'),
            ('MP7A1_FOREGRIP', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_FOREGRIP', 'MP7A1'),
            ('P90TR_BOLT', 'firearms/GunsOfTienPost93_P90TR', 'P90TR_BOLT', 'P90TR')]:
        out.append(f"""
    model {model} {{
        mesh     = weapons/{file}|{node},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    parts = [(f'46x30Magazine{n}_MP7', 'magazines/GunsOfTienPost93_MP7_magazines') for n in (20, 30, 40, 60)]
    parts += [('57x28Magazine50_P90', 'magazines/GunsOfTienPost93_P90_magazines')]
    # GoM's pistol magazines are modelled where they sit in the gun (no `magazine` point) with this floor pose
    parts += [(f'57x28Magazine{n}_FIVESEVEN', 'magazines/GunsOfTienPost93_FIVESEVEN_magazines') for n in (20, 30)]
    parts += [(f'46x30Magazine{n}_UCP', 'magazines/GunsOfTienPost93_UCP_magazines') for n in (20, 40)]
    parts += [(p, 'parts/GunsOfTienPost93_MP7_parts') for p in ('MP7_Suppressor', 'MP7_Muzzle_Mount_Device')]
    parts += [(p, 'parts/GunsOfTienPost93_P90_parts') for p in ('P90_Suppressor', 'P90_Muzzle_Mount_Device')]
    parts += [(p, 'parts/GunsOfTienPost93_FIVESEVEN_parts') for p in ('FIVESEVEN_Suppressor',
                                                                       'FIVESEVEN_Muzzle_Mount_Device')]
    parts += [('UCP_Muzzle_Mount_Device', 'parts/GunsOfTienPost93_UCP_parts')]
    parts += [(f'762x51Magazine{n}_SCARH', 'magazines/GunsOfTienPost93_SCARH_magazines') for n in (20, 10, 50)]
    parts += [(p, 'parts/GunsOfTienPost93_SCAR_parts') for p in ('SCARH_Suppressor', 'SCARH_Muzzle_Mount_Device')]
    parts += [(m, 'magazines/GunsOfTienPost93_UMP_magazines') for m in UMP_MAGS]
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


def model_parts(gun, mags, rails, suppressor, mount, stock, foregrip=False):
    lines = [f"        ModelWeaponPart              = MarzGuns.Bolt_Lock {M}.{gun}_BOLT bolt_lock bolt_lock,",
             f"        ModelWeaponPart              = MarzGuns.Bolt_Fired {M}.{gun}_BOLT bolt_fired bolt_fired,"]
    if stock:
        lines += [f"        ModelWeaponPart              = {M}.{gun}_Integrated_Stock_Folded {M}.{gun}_STOCK stock_folded stock_folded,",
                  f"        ModelWeaponPart              = {M}.{gun}_Integrated_Stock_Deployed {M}.{gun}_STOCK stock stock,"]
    if foregrip:
        # the front grip is modelled folded: no foregrip_folded point, so the folded part is drawn at the origin
        lines += [f"        ModelWeaponPart              = {M}.{gun}_Integrated_Foregrip_Folded {M}.{gun}_FOREGRIP foregrip_folded foregrip_folded,",
                  f"        ModelWeaponPart              = {M}.{gun}_Integrated_Foregrip_Deployed {M}.{gun}_FOREGRIP foregrip_deployed foregrip_deployed,"]
    lines += [f"        ModelWeaponPart              = {M}.{m} {M}.{m} magazine magazine," for m in mags]
    lines += [f"        ModelWeaponPart              = {M}.{mount} {M}.{mount} canon canon,",
              f"        ModelWeaponPart              = {M}.{suppressor} {M}.{suppressor} canon canon,"]
    lines += [f"        ModelWeaponPart              = MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"        ModelWeaponPart              = MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    # the lit laser's beam (main mod: shared/GunsOfTien/Lasers.lua adds these lines to GoM's own guns at load)
    lines += [f"        ModelWeaponPart              = GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"GunsOfTien.LaserBeam_{o.replace('-', '')} laser_right laser_right," for o in LASERS]
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

# The MP7 and the P90 are held like a pistol, as GoM holds its MP5K, TEC9 and MAC10: Handgun swing animation,
# handgun reload mechanics, one hand when not aiming (their models are built upside down to match). Unlike those they
# never fit a holster: AttachmentType stays Rifle (the back slot), and their models' rifle_back / rifle_back_bag
# attachments turn them upright there.
GUN_HANDGUN = (GUN_COMMON
               .replace("WeaponReloadType             = boltaction,", "WeaponReloadType             = handgun,")
               .replace("        TwoHandWeapon                = true,\n", "")
               .replace("        RequiresEquippedBothHands    = true,\n", "")
               .replace("        IdleAnim                     = Idle_Weapon2,\n", "")
               .replace("SwingAnim                    = Rifle,", "SwingAnim                    = Handgun,")
               .replace("MuzzleFlashModelKey          = muzzle_flash_shotgun,",
                        "MuzzleFlashModelKey          = muzzle_flash_handgun,"))
assert GUN_HANDGUN.count("Handgun") == 1 and "TwoHandWeapon" not in GUN_HANDGUN
# The MP7s keep the pistol hold but are two-handed, for the compact SMG stance (user: "let's require them to be
# 2-handed"; CLAUDE.md "One-handed after equipping"); the P90 stays one-handed.
GUN_HANDGUN_TWO_HANDS = GUN_HANDGUN.replace(
    "        WeaponReloadType             = handgun,\n",
    "        WeaponReloadType             = handgun,\n"
    "        TwoHandWeapon                = true,\n"
    "        RequiresEquippedBothHands    = true,\n")
assert GUN_HANDGUN_TWO_HANDS.count("TwoHandWeapon") == 1


# GoM's pistol parts the Five-seveN takes (the ModelWeaponPart lines of GoM's Glock 17 / M92FS)
PISTOL_SIGHTS = ['PL4_Sight', 'PM2_Sight', 'PS1_Sight']
# GoM's two pistol lights (LP: compact weapon light; TL: a flashlight in a clamp, the pre-rail way), no lasers
# (user, 2026-10-16)
PISTOL_POINTERS = ['LP_Light', 'TL_Light']


def fiveseven_item():
    """MarzGuns.FIVESEVEN, as GoM's pistols (GLOCK17 is the template) on our 5.7x28mm. Light recoil (HitChance 57,
    RecoilDelay 9), M92FS-class damage, pierces 2 with the standard SS190 round like the P90 (its script round, which
    Gunworks never profiles), realistic sound (the main mod's model: 5.7x28mm ~6.7 gr from a 122 mm barrel = 148 / 42;
    the M16 is 175 / 50). Takes GoM's Beretta mount and pistol sights, its two pistol lights on the rail, the
    5.7x28mm family's mount device (shared with the P90, as GoM's pistols share theirs) and its own SFN-57 suppressor
    (user, 2026-10-16: one suppressor per gun)."""
    parts = [f"        ModelWeaponPart             = MarzGuns.Slide_Lock {M}.FIVESEVEN_SLIDE slide_Lock slide_Lock,",
             f"        ModelWeaponPart             = MarzGuns.Slide_Fired {M}.FIVESEVEN_SLIDE slide_fired slide_fired,"]
    parts += [f"        ModelWeaponPart             = {M}.57x28Magazine{n}_FIVESEVEN {M}.57x28Magazine{n}_FIVESEVEN "
              f"magazine magazine," for n in (20, 30)]
    parts += ["        ModelWeaponPart             = MarzGuns.Beretta_Mount MarzGuns.Beretta_Mount rail_up rail_up,"]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} scope scope," for s in PISTOL_SIGHTS]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} underbarrel underbarrel,"
              for s in PISTOL_POINTERS]
    # the shared mount device item, drawn on the pistol as its own threaded-barrel adapter
    parts += [f"        ModelWeaponPart             = {M}.P90_Muzzle_Mount_Device {M}.FIVESEVEN_Muzzle_Mount_Device canon canon,",
              f"        ModelWeaponPart             = {M}.FIVESEVEN_Suppressor {M}.FIVESEVEN_Suppressor canon canon,"]
    write(f'scripts/{M}/items_fiveseven.txt', f"""module MarzGuns {{
    imports {{ Base }}

    item FIVESEVEN {{
        MinDamage                   = 0.6,
        MaxDamage                   = 1.0,
        CriticalChance              = 25.0,
        AimingPerkCritModifier      = 6,
        CritDmgMultiplier           = 4.0,
        HitChance                   = 57,
        AimingPerkHitChanceModifier = 4,
        Aimingtime                  = 18,
        RecoilDelay                 = 9,
        MaxRange                    = 22.0,
        AimingPerkRangeModifier     = 0,
        MinSightRange               = 1,
        MaxSightRange               = 10.0,
        MinRange                    = 0.61,
        MinAngle                    = 0.95,
        AimingPerkMinAngleModifier  = 0.05,
        JamGunChance                = 1.0,
        ConditionLowerChanceOneIn   = 230,
        ConditionMax                = 10,
        PushBackMod                 = 0.3,
        StopPower                   = 4.0,
        DoorDamage                  = 5,

        Projectilecount             = 1,
        MaxHitcount                 = 2,
        PiercingBullets             = true,

        DisplayCategory             = Weapon,
        ItemType                    = base:weapon,
        SubCategory                 = Firearm,
        AttachmentType              = Holster,
        Tags                        = base:hasmetal;base:firearm,
        Weight                      = 0.6,
        MetalValue                  = 25.0,
        IsAimedFirearm              = true,
        Ranged                      = true,
        AmmoType                    = gunsoftienpost93:bullet_57x28,
        AmmoBox                     = {M}.57x28_Box,
        ClipSize                    = 20,
        MagazineType                = {M}.57x28Magazine20_FIVESEVEN,
        MaxAmmo                     = 20,
        Reloadtime                  = 30,
        WeaponReloadType            = handgun,
        UseEndurance                = false,
        MinimumSwingtime            = 0.5,
        Swingtime                   = 0.5,
        SwingAmountBeforeImpact     = 0.0,

        Icon                        = GunsOfTienPost93_FIVESEVEN,
        RunAnim                     = Run_Weapon2,
        SwingAnim                   = Handgun,
        WeaponSprite                = {M}.FIVESEVEN,
        AimReleaseSound             = M9AimRelease,
        BreakSound                  = M9Break,
        BringToBearSound            = M9BringToBear,
        ClickSound                  = M9Jam,
        DropSound                   = M9Drop,
        EjectAmmoStartSound         = M9EjectAmmoStart,
        EjectAmmoSound              = M9EjectAmmo,
        EjectAmmoStopSound          = M9EjectAmmoStop,
        EquipSound                  = M9Equip,
        HitSound                    = BulletImpact,
        ImpactSound                 = null,
        InsertAmmoStartSound        = M9InsertAmmoStart,
        InsertAmmoSound             = M9InsertAmmo,
        InsertAmmoStopSound         = M9InsertAmmoStop,
        RackSound                   = M9Rack,
        ShellFallSound              = M9CartridgeFall,
        SwingSound                  = M9Shoot,
        UnequipSound                = M9UnEquip,
        SoundGain                   = 1.5,
        SoundRadius                 = 148,
        SoundVolume                 = 42,
        NPCSoundBoost               = 1.5,
        MuzzleFlashModelKey         = muzzle_flash_handgun,
        SplatBloodOnNoDeath         = true,
        SplatNumber                 = 3,
        SplatSize                   = 3,

        OnCreate                    = MarzGuns_OnCreate.AttachParts,
{chr(10).join(parts)}

        KnockBackOnNoDeath          = true,
        ToHitModifier               = 1.5,
    }}
}}
""")


def ucp_item():
    """GunsOfTienPost93.UCP, "UCP Prototype" (user, 2026-10-17): H&K's 4.6x30mm companion pistol to the MP7, prototypes
    from about 2004, cancelled 2009. Built and registered like the Five-seveN (GoM's pistol pattern). Published: 200 mm,
    130 mm barrel, 850 g, 20 rounds, 695 m/s. DM11 from it carries a little less energy than SS190 from the Five-seveN
    (1.6 g at 695 m/s against 2.0 g at about 650), so damage 0.55-0.95 (Five-seveN 0.6-1.0); weight 0.85 for 850 g (GoM's
    USP and M92FS weigh about their real kilograms); pierces 2 with DM11 like
    the MP7; light recoil. Realistic sound (the main mod's model: 4.6x30mm ~6 gr from 130 mm against the MP7's 180 mm =
    125 / 36). Takes GoM's Beretta mount and pistol sights, its two pistol lights (no lasers, as the Five-seveN), and the
    MP7's mount device (drawn as UCP_Muzzle_Mount_Device) and Rotex-II suppressor (user: "use the MP7 suppressor")."""
    parts = [f"        ModelWeaponPart             = MarzGuns.Slide_Lock {M}.UCP_SLIDE slide_Lock slide_Lock,",
             f"        ModelWeaponPart             = MarzGuns.Slide_Fired {M}.UCP_SLIDE slide_fired slide_fired,",
             f"        ModelWeaponPart             = {M}.46x30Magazine20_UCP {M}.46x30Magazine20_UCP magazine magazine,",
             f"        ModelWeaponPart             = {M}.46x30Magazine40_UCP {M}.46x30Magazine40_UCP magazine magazine,",
             "        ModelWeaponPart             = MarzGuns.Beretta_Mount MarzGuns.Beretta_Mount rail_up rail_up,"]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} scope scope," for s in PISTOL_SIGHTS]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} underbarrel underbarrel,"
              for s in PISTOL_POINTERS]
    parts += [f"        ModelWeaponPart             = {M}.MP7_Muzzle_Mount_Device {M}.UCP_Muzzle_Mount_Device canon canon,",
              f"        ModelWeaponPart             = {M}.MP7_Suppressor {M}.MP7_Suppressor canon canon,"]
    block = open(os.path.join(ROOT, f'scripts/{M}/items_fiveseven.txt')).read()
    body = block[block.index('    item FIVESEVEN {'):block.rindex('}')]
    for a, b in [('item FIVESEVEN {', 'item UCP {'),
                 ('MinDamage                   = 0.6,', 'MinDamage                   = 0.55,'),
                 ('MaxDamage                   = 1.0,', 'MaxDamage                   = 0.95,'),
                 ('HitChance                   = 57,', 'HitChance                   = 56,'),
                 ('StopPower                   = 4.0,', 'StopPower                   = 3.5,'),
                 ('Weight                      = 0.6,', 'Weight                      = 0.85,'),
                 ('AmmoType                    = gunsoftienpost93:bullet_57x28,',
                  'AmmoType                    = gunsoftienpost93:bullet_46x30,'),
                 (f'AmmoBox                     = {M}.57x28_Box,', f'AmmoBox                     = {M}.46x30_Box,'),
                 (f'MagazineType                = {M}.57x28Magazine20_FIVESEVEN,',
                  f'MagazineType                = {M}.46x30Magazine20_UCP,'),
                 ('Icon                        = GunsOfTienPost93_FIVESEVEN,', 'Icon                        = GunsOfTienPost93_UCP,'),
                 (f'WeaponSprite                = {M}.FIVESEVEN,', f'WeaponSprite                = {M}.UCP,'),
                 ('SoundRadius                 = 148,', 'SoundRadius                 = 125,'),
                 ('SoundVolume                 = 42,', 'SoundVolume                 = 36,')]:
        assert body.count(a) == 1, a
        body = body.replace(a, b)
    start = body.index('        ModelWeaponPart')
    end = body.index('\n\n        KnockBackOnNoDeath')
    body = body[:start] + '\n'.join(parts) + body[end:]
    return body


# GoM's foregrips, on the MP7A2's bottom rail (GoM draws them at the gun's `foregrip` point)
FOREGRIPS = ['Stub_Foregrip', 'MKC_Foregrip', 'MK2_Foregrip']


def mp7_item(name):
    """The MP7A1, or the MP7A2 (user, 2026-10-18): the same gun with a rail handguard for the A1's folding grip. Both use
    the A1's bolt, stock, magazines and muzzle parts; the A2 takes GoM's foregrips on its bottom rail instead."""
    a2 = name == 'MP7A2'
    mp7_mags = [f'46x30Magazine{n}_MP7' for n in (20, 30, 40, 60)]
    parts = model_parts('MP7A1', mp7_mags, None, 'MP7_Suppressor', 'MP7_Muzzle_Mount_Device', True, not a2)
    if a2:
        parts += ''.join(f"        ModelWeaponPart              = MarzGuns.{g} MarzGuns.{g} foregrip foregrip,\n"
                         for g in FOREGRIPS)
    return f"""
    item {name} {{
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
        Weight                       = 1.5,
        MetalValue                   = 25.0,
{GUN_HANDGUN_TWO_HANDS}        AmmoType                     = gunsoftienpost93:bullet_46x30,
        AmmoBox                      = {M}.46x30_Box,
        MagazineType                 = {M}.46x30Magazine20_MP7,
        MaxAmmo                      = 20,
        Reloadtime                   = 22,
        Icon                         = GunsOfTienPost93_{name},
        WeaponSprite                 = {M}.{name},
        SoundGain                    = 1.6,
        SoundRadius                  = 114,
        SoundVolume                  = 33,
{parts}    }}
"""


def items(mp7, p90):
    mp7_mags = [f'46x30Magazine{n}_MP7' for n in (20, 30, 40, 60)]
    p90_mags = ['57x28Magazine50_P90']
    mp7s = f'MP7A1;{M}.MP7A2'                          # both MP7s take every MP7 magazine
    out = [f"module {M} {{\n    imports {{ Base }}\n"]
    # Realistic sound (the main mod's model, M16 = 175 / 50): 4.6x30 ~6 gr, 180 mm barrel; 5.7x28 ~6.7 gr, 263 mm.
    out.append(mp7_item('MP7A1'))
    out.append(mp7_item('MP7A2'))
    out.append(f"""
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
        Weight                       = 2.0,
        MetalValue                   = 25.0,
{GUN_HANDGUN}        AmmoType                     = gunsoftienpost93:bullet_57x28,
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
    # Weights by GoM's own (user, 2026-10-17: "use the GoM standard"): its MP5 20 / 30 / 60 = 0.08 / 0.18 / 0.22, the
    # 50-60 round pistol-calibre magazines 0.2-0.25 (M92FS 50, M93R 60, AK 60).
    for mag, cap, weight, ammo, guns in [(mp7_mags[0], 20, 0.08, 'bullet_46x30', mp7s),
                                         (mp7_mags[1], 30, 0.18, 'bullet_46x30', mp7s),
                                         (mp7_mags[2], 40, 0.2, 'bullet_46x30', mp7s),
                                         (mp7_mags[3], 60, 0.22, 'bullet_46x30', mp7s),    # drum, as the MP5's 60
                                         (p90_mags[0], 50, 0.25, 'bullet_57x28', 'P90TR')]:
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
    # GoM's pistol magazines: standard 0.05 (Glock 17, M92FS 15, P226, USP 12), extended 0.2 (M92FS 30, USP 20), drums
    # 0.2-0.25 (M93R 60, M92FS 50)
    for mag, cap, weight, gun, ammo in [('57x28Magazine20_FIVESEVEN', 20, 0.05, 'MarzGuns.FIVESEVEN', 'bullet_57x28'),
                                        ('57x28Magazine30_FIVESEVEN', 30, 0.2, 'MarzGuns.FIVESEVEN', 'bullet_57x28'),
                                        ('46x30Magazine20_UCP', 20, 0.05, f'{M}.UCP', 'bullet_46x30'),
                                        ('46x30Magazine40_UCP', 40, 0.2, f'{M}.UCP', 'bullet_46x30')]:
        out.append(f"""
    item {mag} {{
        AmmoType         = gunsoftienpost93:{ammo},
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {gun},
        PartType         = Clip,
        Tags             = base:hasmetal;base:pistolmagazine,
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
                                ('MP7A1_Integrated_Foregrip_Folded', 'ForegripIntegrated', None),
                                ('MP7A1_Integrated_Foregrip_Deployed', 'ForegripIntegrated', None),
                                ('MP7A1_Integrated_Rail_Up', 'RailUp', None),
                                ('MP7A1_Integrated_Rail_Left', 'RailLeft', None),
                                ('MP7A1_Integrated_Rail_Right', 'RailRight', None),
                                ('MP7A2_Integrated_Rail_Down', 'RailDown', None),
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
    # the 5.7x28mm family's mount device fits the P90 and the Five-seveN; each has its own suppressor
    # GoM's weights (user, 2026-10-17): suppressors 0.8-1.2 whatever their size, matched by size: the Rotex-II (34 x 190
    # mm) and the SFN-57 (33 x 170) as its P45 (33 x 181) 0.8, the SP90 (38 x 172) as its NDR 0.9; every mount device 0.5
    for part, ptype, weight, gun in [('MP7_Suppressor', 'Canon', 0.8, f'{M}.MP7A1;{M}.MP7A2;{M}.UCP'),
                                     ('MP7_Muzzle_Mount_Device', 'CanonMount', 0.5, f'{M}.MP7A1;{M}.MP7A2;{M}.UCP'),
                                     ('P90_Suppressor', 'Canon', 0.9, f'{M}.P90TR'),
                                     ('FIVESEVEN_Suppressor', 'Canon', 0.8, 'MarzGuns.FIVESEVEN'),
                                     ('P90_Muzzle_Mount_Device', 'CanonMount', 0.5, f'{M}.P90TR;MarzGuns.FIVESEVEN')]:
        out.append(f"""
    item {part} {{
        DisplayCategory  = WeaponPart,
        ItemType         = base:weaponpart,
        Icon             = GunsOfTienPost93_{part},
        Weight           = {weight},
        WeightModifier   = {weight},
        MountOn          = {gun},
        PartType         = {ptype},
        WorldStaticModel = {M}.{part},
        CanAttach        = MarzGuns_AttachAndDetach.requiredTools,
        CanDetach        = MarzGuns_AttachAndDetach.requiredTools,
    }}
""")
    out.append(ucp_item())
    out += scar_items()
    out += ump_items()
    out.append("}\n")
    write(f'scripts/{M}/items_guns.txt', ''.join(out))
    write(f'scripts/{M}/fixing_guns.txt', f"""module Base {{
    fixing Fix MP7A1 {{
        Require = {M}.MP7A1,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix MP7A2 {{
        Require = {M}.MP7A2,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix P90TR {{
        Require = {M}.P90TR,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix FIVESEVEN {{
        Require = MarzGuns.FIVESEVEN,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix UCP {{
        Require = {M}.UCP,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix SCARL {{
        Require = {M}.SCARL,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix SCARH {{
        Require = {M}.SCARH,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix UMP45 {{
        Require = {M}.UMP45,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}

    fixing Fix UMP9 {{
        Require = {M}.UMP9,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
}}
""")


# ==================================================================================================
# FN SCAR-L (Mk 16 STD) and SCAR-H (Mk 17 LB), user 2026-10-20 (build_scar.py)
# ==================================================================================================

STANAGS = ['556x45Magazine%s_STANAG' % n for n in (20, 25, 30, 50, 60, 75, 100, 150)]
AR_MUZZLE = ['MKI_Suppressor', 'NDR_Suppressor', 'LR2_Compensator', 'LX_Flashhider', 'Trix42_Muzzlebreak']
SCARH_MAGS = ['762x51Magazine20_SCARH', '762x51Magazine10_SCARH', '762x51Magazine50_SCARH']


def scar_parts(gun):
    """GoM rifle parts on the SCARs' integral rails (their points in scarl / scarh_points.json), the shared folding
    stock, the charging handle; the SCAR-L's GoM STANAG magazines and AR muzzle parts, the SCAR-H's own."""
    w = "        ModelWeaponPart              = "
    lines = [f"{w}MarzGuns.Bolt_Lock {M}.{gun}_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {M}.{gun}_BOLT bolt_fired bolt_fired,",
             f"{w}{M}.SCAR_Integrated_Stock_Folded {M}.SCAR_STOCK stock_folded stock_folded,",
             f"{w}{M}.SCAR_Integrated_Stock_Deployed {M}.SCAR_STOCK stock stock,"]
    if gun == 'SCARL':
        lines += [f"{w}MarzGuns.{m} MarzGuns.{m} magazine magazine," for m in STANAGS]
        lines += [f"{w}MarzGuns.AR_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,"]
        lines += [f"{w}MarzGuns.{p} MarzGuns.{p} canon canon," for p in AR_MUZZLE]
    else:
        lines += [f"{w}{M}.{m} {M}.{m} magazine magazine," for m in SCARH_MAGS]
        lines += [f"{w}{M}.SCARH_Muzzle_Mount_Device {M}.SCARH_Muzzle_Mount_Device canon canon,",
                  f"{w}{M}.SCARH_Suppressor {M}.SCARH_Suppressor canon canon,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"{w}MarzGuns.{g} MarzGuns.{g} foregrip foregrip," for g in FOREGRIPS]
    lines += [f"{w}MarzGuns.{b} MarzGuns.{b} bipod bipod," for b in ('Bipod_Deployed', 'Bipod_Folded')]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


# Sounds: GoM's M4A1 (M16 events) and FAL (M14 events, MSR788Shoot) sets. Realistic sound (the main mod's model,
# M16 = 175 / 50): 5.56 from 13.8" = 196 / 56, 7.62x51 from 20" = 216 / 62.
SCAR_SOUNDS = {
    'SCARL': dict(prefix='M16', shoot='M16Shoot', gain=1.9, radius=196, volume=56),
    'SCARH': dict(prefix='M14', shoot='MSR788Shoot', gain=2.5, radius=216, volume=62),
}


def scar_item(gun, stats):
    snd = SCAR_SOUNDS[gun]
    p = snd['prefix']
    body = f"""
    item {gun} {{
        MinDamage                    = {stats['min']},
        MaxDamage                    = {stats['max']},
        CriticalChance               = {stats['crit']},
        AimingPerkCritModifier       = 5,
        CritDmgMultiplier            = {stats['critmult']},
        HitChance                    = {stats['hit']},
        AimingPerkHitChanceModifier  = {stats['hitmod']},
        Aimingtime                   = {stats['aim']},
        RecoilDelay                  = {stats['recoil']},
        MaxRange                     = {stats['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {stats['minsight']},
        MaxSightRange                = {stats['maxsight']},
        MinRange                     = 0.61,
        MinAngle                     = {stats['minangle']},
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = {stats['jam']},
        ConditionLowerChanceOneIn    = {stats['cond']},
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        StopPower                    = {stats['stop']},
        DoorDamage                   = {stats['door']},
        Projectilecount              = 1,
        MaxHitcount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {stats['weight']},
        MetalValue                   = {stats['metal']},
        FireMode                     = {stats['firemode']},
        FireModePossibilities        = Auto/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = {stats['ammo']},
        AmmoBox                      = {stats['box']},
        ClipSize                     = {stats['clip']},
        MagazineType                 = {stats['mag']},
        MaxAmmo                      = {stats['clip']},
        Reloadtime                   = 25,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        Icon                         = GunsOfTienPost93_{gun},
        IdleAnim                     = Idle_Weapon2,
        RunAnim                      = Run_Weapon2,
        SwingAnim                    = Rifle,
        WeaponSprite                 = {M}.{gun},
        AimReleaseSound              = {p}AimRelease,
        BreakSound                   = {p}Break,
        BringToBearSound             = {p}BringToBear,
        ClickSound                   = {p}Jam,
        DropSound                    = {p}Drop,
        EjectAmmoStartSound          = {p}EjectAmmoStart,
        EjectAmmoSound               = {p}EjectAmmo,
        EjectAmmoStopSound           = {p}EjectAmmoStop,
        EquipSound                   = {p}Equip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = {p}InsertAmmoStart,
        InsertAmmoSound              = {p}InsertAmmo,
        InsertAmmoStopSound          = {p}InsertAmmoStop,
        RackSound                    = {p}Rack,
        ShellFallSound               = {p}CartridgeFall,
        SwingSound                   = {snd['shoot']},
        UnequipSound                 = {p}UnEquip,
        SoundGain                    = {snd['gain']},
        SoundRadius                  = {snd['radius']},
        SoundVolume                  = {snd['volume']},
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{scar_parts(gun)}        KnockBackOnNoDeath           = true,
    }}
"""
    return body


def scar_items():
    """The SCAR-L as GoM's M4A1 (its 14.5" barrel against the Mk 16's 13.8": the same damage), a little steadier
    (FN's soft-shooting piston gun), more durable; the SCAR-H LB as GoM's FAL (21" barrel against the LB's 20": the
    same damage and range) but lighter and quicker to aim (3.9 kg against 4.25, folding stock, pistol grip). Both
    select fire (Auto / Single, no burst); weights at the real kilograms as GoM's rifles."""
    out = [scar_item('SCARL', dict(min=1.0, max=1.4, crit=18.0, critmult=3.5, hit=52, hitmod=5, aim=15, recoil=12,
                                   range=40.0, minsight=6, maxsight=14.0, minangle=0.965, jam=0.75, cond=250,
                                   stop=1.8, door=3, weight=3.3, metal=30.0, firemode='Auto',
                                   ammo='swmg:bullet_556x45', box='MarzGuns.556x45_Box', clip=30,
                                   mag='MarzGuns.556x45Magazine30_STANAG')),
           scar_item('SCARH', dict(min=1.3, max=1.8, crit=30.0, critmult=5.0, hit=52, hitmod=4, aim=50, recoil=15,
                                   range=60.0, minsight=10, maxsight=18.0, minangle=0.95, jam=0.5, cond=240,
                                   stop=2.0, door=6, weight=3.9, metal=40.0, firemode='Single',
                                   ammo='swmg:bullet_762x51', box='MarzGuns.762x51_Box', clip=20,
                                   mag=f'{M}.762x51Magazine20_SCARH'))]
    # FN's steel SCAR-H magazines (GoM's FAL 20 weighs 0.2) and ProMag's 50-round drum (GoM's 5.56 drums: 60 = 0.4,
    # 100 = 0.6)
    for mag, cap, weight in ((SCARH_MAGS[0], 20, 0.2), (SCARH_MAGS[1], 10, 0.12), (SCARH_MAGS[2], 50, 0.5)):
        out.append(f"""
    item {mag} {{
        AmmoType         = swmg:bullet_762x51,
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {M}.SCARH,
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
    for part, ptype, weight in [('SCAR_Integrated_Stock_Folded', 'StockIntegrated', None),
                                ('SCAR_Integrated_Stock_Deployed', 'StockIntegrated', 0.2),
                                ('SCAR_Integrated_Rail_Up', 'RailUp', None),
                                ('SCAR_Integrated_Rail_Down', 'RailDown', None),
                                ('SCAR_Integrated_Rail_Left', 'RailLeft', None),
                                ('SCAR_Integrated_Rail_Right', 'RailRight', None)]:
        wl = f"        Weight          = {weight},\n        WeightModifier  = {weight},\n" if weight else ''
        out.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
{wl}        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    # GoM's weights: its heaviest suppressors 1.2 for the 7.62 can (38 x 190 mm); every mount device 0.5
    for part, ptype, weight in (('SCARH_Suppressor', 'Canon', 1.2), ('SCARH_Muzzle_Mount_Device', 'CanonMount', 0.5)):
        out.append(f"""
    item {part} {{
        DisplayCategory  = WeaponPart,
        ItemType         = base:weaponpart,
        Icon             = GunsOfTienPost93_{part},
        Weight           = {weight},
        WeightModifier   = {weight},
        MountOn          = {M}.SCARH,
        PartType         = {ptype},
        WorldStaticModel = {M}.{part},
        CanAttach        = MarzGuns_AttachAndDetach.requiredTools,
        CanDetach        = MarzGuns_AttachAndDetach.requiredTools,
    }}
""")
    return out


# ==================================================================================================
# H&K UMP45 and UMP9, user 2026-10-22 (build_ump.py)
# ==================================================================================================

UMPS = ['UMP45', 'UMP9']
UMP_MAGS = ['9x19Magazine30_UMP', '45Magazine25_UMP', '45Magazine20_UMP', '45Magazine10_UMP']
UMP_GUN_MAGS = {'UMP45': UMP_MAGS[1:], 'UMP9': UMP_MAGS[:1]}


def ump_parts(gun):
    """GoM's MP5 accessories on the UMPs' integral rails (their points in ump_points.json): its optics, foregrips,
    lasers and lights, no bipods; at canon the UMP45 GoM's .45 mount device and P45 suppressor, as its MAC-10, the UMP9
    the main mod's 9x19mm SMG mount device and AWC Mk9 (user, 2026-10-22; GoM's 9mm suppressors fit its pistols only);
    the shared folding stock and charging handle; each gun's own magazines."""
    w = "        ModelWeaponPart              = "
    lines = [f"{w}MarzGuns.Bolt_Lock {M}.UMP_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {M}.UMP_BOLT bolt_fired bolt_fired,",
             f"{w}{M}.UMP_Integrated_Stock_Folded {M}.UMP_STOCK stock_folded stock_folded,",
             f"{w}{M}.UMP_Integrated_Stock_Deployed {M}.UMP_STOCK stock stock,"]
    lines += [f"{w}{M}.{m} {M}.{m} magazine magazine," for m in UMP_GUN_MAGS[gun]]
    if gun == 'UMP45':
        lines += [f"{w}MarzGuns.45_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,",
                  f"{w}MarzGuns.P45_Suppressor MarzGuns.P45_Suppressor canon canon,"]
    else:
        # the main mod's Mk9 at our size (its `_GoT` models; GoM's MP5s draw the GoM-sized ones)
        lines += [f"{w}GunsOfTien.SMG9_Muzzle_Mount_Device GunsOfTien.SMG9_Muzzle_Mount_Device_GoT canon canon,",
                  f"{w}GunsOfTien.Mk9_Suppressor GunsOfTien.Mk9_Suppressor_GoT canon canon,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"{w}MarzGuns.{g} MarzGuns.{g} foregrip foregrip," for g in FOREGRIPS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


# GoM's MP5 (9mm, M9Shoot) and its .45 guns' shot (MAC-10, M1911: M1911Shoot), the MP5's other sounds. Realistic sound
# (the main mod's model, M16 = 175 / 50): 9mm and .45 from the UMP's 200 mm (7.9") barrel = 96 / 28 and 70 / 20 (the
# .45 is subsonic).
UMP_STATS = {
    # the MP5's numbers; 2.3 kg x GoM's SMG weight ratio (~0.78)
    'UMP9': dict(min=1.0, max=1.6, crit=20.0, hit=50, aim=40, recoil=15, range=30.0, stop=2.0, weight=1.8, clip=30,
                 ammo='swmg:bullet_9x19', box='MarzGuns.9x19_Box', shoot='M9Shoot', radius=96, volume=28),
    # user, 2026-10-22: the .45 hits harder than the MP5 for its slower fire, recoil and smaller magazine; a little
    # less accurate and shorter-ranged (heavier recoil, slower round); 2.5 kg
    'UMP45': dict(min=1.1, max=1.8, crit=25.0, hit=48, aim=40, recoil=17, range=28.0, stop=2.5, weight=1.9, clip=25,
                  ammo='swmg:bullet_45', box='MarzGuns.45_Box', shoot='M1911Shoot', radius=70, volume=20),
}


def ump_item(gun):
    s = UMP_STATS[gun]
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
        MinSightRange                = 4,
        MaxSightRange                = 12.0,
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
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
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {s['weight']},
        MetalValue                   = 30.0,
        FireMode                     = Auto,
        FireModePossibilities        = Auto/Burst/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = {s['ammo']},
        AmmoBox                      = {s['box']},
        ClipSize                     = {s['clip']},
        MagazineType                 = {M}.{UMP_GUN_MAGS[gun][0]},
        MaxAmmo                      = {s['clip']},
        Reloadtime                   = 25,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        Icon                         = GunsOfTienPost93_{gun},
        IdleAnim                     = Idle_Weapon2,
        RunAnim                      = Run_Weapon2,
        SwingAnim                    = Rifle,
        WeaponSprite                 = {M}.{gun},
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
        SwingSound                   = {s['shoot']},
        UnequipSound                 = M16UnEquip,
        SoundGain                    = 2.0,
        SoundRadius                  = {s['radius']},
        SoundVolume                  = {s['volume']},
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{ump_parts(gun)}        KnockBackOnNoDeath           = true,
        KnockdownMod                 = 4.0,
        MultipleHitConditionAffected = false,
        ToHitModifier                = 1.5,
    }}
"""


def ump_items():
    """Both UMPs as GoM's MP5 is made (UMP_STATS), select fire with H&K's two-round burst (user, 2026-10-22)."""
    out = [ump_item(gun) for gun in UMPS]
    # H&K's polymer magazines by GoM's weights: its MP5 30 = 0.18; Thompson 30 / 20 = 0.15 / 0.1; pistol 0.05
    for mag, cap, weight, ammo, gun in (('9x19Magazine30_UMP', 30, 0.18, 'swmg:bullet_9x19', 'UMP9'),
                                        ('45Magazine25_UMP', 25, 0.15, 'swmg:bullet_45', 'UMP45'),
                                        ('45Magazine20_UMP', 20, 0.1, 'swmg:bullet_45', 'UMP45'),
                                        ('45Magazine10_UMP', 10, 0.05, 'swmg:bullet_45', 'UMP45')):
        out.append(f"""
    item {mag} {{
        AmmoType         = {ammo},
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {M}.{gun},
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
    for part, ptype, weight in [('UMP_Integrated_Stock_Folded', 'StockIntegrated', None),
                                ('UMP_Integrated_Stock_Deployed', 'StockIntegrated', 0.2),
                                ('UMP_Integrated_Rail_Up', 'RailUp', None),
                                ('UMP_Integrated_Rail_Down', 'RailDown', None),
                                ('UMP_Integrated_Rail_Left', 'RailLeft', None),
                                ('UMP_Integrated_Rail_Right', 'RailRight', None)]:
        wl = f"        Weight          = {weight},\n        WeightModifier  = {weight},\n" if weight else ''
        out.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
{wl}        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    return out


def translations():
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(path)) if os.path.exists(path) else {}
    # GoM's naming: model and class, no maker ("MP5 Submachine Gun", "MP5 Integrated Stock (Folded)").
    names.update({
        f'{M}.MP7A1': 'MP7A1 Submachine Gun',                 # the variant named since the A2 (user, 2026-10-18)
        f'{M}.MP7A2': 'MP7A2 Submachine Gun',
        f'{M}.MP7A2_Integrated_Rail_Down': 'MP7 Integrated Rail (Down)',
        f'{M}.P90TR': 'P90 Submachine Gun',
        f'{M}.46x30Magazine20_MP7': 'MP7 20Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine30_MP7': 'MP7 30Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine40_MP7': 'MP7 40Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine60_MP7': 'MP7 60Rds Drum 4.6x30mm Magazine',
        f'{M}.57x28Magazine50_P90': 'P90 50Rds 5.7x28mm Magazine',
        # MarzGuns.FIVESEVEN itself is named by GoM ("5.7x28mm Five-SeveN"); its magazines in GoM's style
        f'{M}.57x28Magazine20_FIVESEVEN': 'Five-SeveN 20Rds 5.7x28mm Magazine',
        f'{M}.57x28Magazine30_FIVESEVEN': 'Five-SeveN 30Rds 5.7x28mm Extended Magazine',
        f'{M}.UCP': 'UCP Prototype',                                  # user, 2026-10-17
        f'{M}.46x30Magazine20_UCP': 'UCP 20Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine40_UCP': 'UCP 40Rds Drum 4.6x30mm Magazine',
        f'{M}.MP7A1_Integrated_Stock_Folded': 'MP7 Integrated Stock (Folded)',
        f'{M}.MP7A1_Integrated_Stock_Deployed': 'MP7 Integrated Stock (Deployed)',
        f'{M}.MP7A1_Integrated_Foregrip_Folded': 'MP7 Integrated Foregrip (Folded)',
        f'{M}.MP7A1_Integrated_Foregrip_Deployed': 'MP7 Integrated Foregrip (Deployed)',
        f'{M}.MP7A1_Integrated_Rail_Up': 'MP7 Integrated Rail (Up)',
        f'{M}.MP7A1_Integrated_Rail_Left': 'MP7 Integrated Rail (Left)',
        f'{M}.MP7A1_Integrated_Rail_Right': 'MP7 Integrated Rail (Right)',
        f'{M}.P90TR_Integrated_Rail_Up': 'P90 Integrated Rail (Up)',
        f'{M}.P90TR_Integrated_Rail_Left': 'P90 Integrated Rail (Left)',
        f'{M}.P90TR_Integrated_Rail_Right': 'P90 Integrated Rail (Right)',
        f'{M}.MP7_Suppressor': 'Rotex-II Suppressor (4.6x30mm Weapons)',
        f'{M}.MP7_Muzzle_Mount_Device': '4.6x30mm Family Muzzle Mounting Device',
        f'{M}.P90_Suppressor': 'SP90 Suppressor',          # model only, no calibre (user, 2026-10-16)
        f'{M}.FIVESEVEN_Suppressor': 'SFN-57 Suppressor',
        f'{M}.P90_Muzzle_Mount_Device': '5.7x28mm Family Muzzle Mounting Device',
        # GoM: "FN FAL Battle Rifle", "FN FNC Assault Rifle", "FAL 20Rds 7.62x51mm Magazine"
        f'{M}.SCARL': 'FN SCAR-L Assault Rifle',
        f'{M}.SCARH': 'FN SCAR-H Battle Rifle',
        f'{M}.762x51Magazine20_SCARH': 'SCAR-H 20Rds 7.62x51mm Magazine',
        f'{M}.762x51Magazine10_SCARH': 'SCAR-H 10Rds 7.62x51mm Magazine',
        f'{M}.762x51Magazine50_SCARH': 'SCAR-H 50Rds Drum 7.62x51mm Magazine',     # as the MP7's 60 drum
        f'{M}.SCAR_Integrated_Stock_Folded': 'SCAR Integrated Stock (Folded)',
        f'{M}.SCAR_Integrated_Stock_Deployed': 'SCAR Integrated Stock (Deployed)',
        f'{M}.SCAR_Integrated_Rail_Up': 'SCAR Integrated Rail (Up)',
        f'{M}.SCAR_Integrated_Rail_Down': 'SCAR Integrated Rail (Down)',
        f'{M}.SCAR_Integrated_Rail_Left': 'SCAR Integrated Rail (Left)',
        f'{M}.SCAR_Integrated_Rail_Right': 'SCAR Integrated Rail (Right)',
        f'{M}.SCARH_Suppressor': 'SOCOM762-RC Suppressor (7.62x51mm Weapons)',
        f'{M}.SCARH_Muzzle_Mount_Device': 'SCAR-H Muzzle Mounting Device',
        # GoM: "MP5 Submachine Gun", "MP5 30Rds 9x19mm Magazine", "Thompson 20Rds .45 ACP Magazine", "G36 30Rds
        # 5.56x45mm Translucent Magazine" (the UMP45's are smoked translucent polymer)
        f'{M}.UMP45': 'UMP45 Submachine Gun',
        f'{M}.UMP9': 'UMP9 Submachine Gun',
        f'{M}.9x19Magazine30_UMP': 'UMP9 30Rds 9x19mm Magazine',
        f'{M}.45Magazine25_UMP': 'UMP45 25Rds .45 ACP Translucent Magazine',
        f'{M}.45Magazine20_UMP': 'UMP45 20Rds .45 ACP Translucent Magazine',
        f'{M}.45Magazine10_UMP': 'UMP45 10Rds .45 ACP Translucent Magazine',
        f'{M}.UMP_Integrated_Stock_Folded': 'UMP Integrated Stock (Folded)',
        f'{M}.UMP_Integrated_Stock_Deployed': 'UMP Integrated Stock (Deployed)',
        f'{M}.UMP_Integrated_Rail_Up': 'UMP Integrated Rail (Up)',
        f'{M}.UMP_Integrated_Rail_Down': 'UMP Integrated Rail (Down)',
        f'{M}.UMP_Integrated_Rail_Left': 'UMP Integrated Rail (Left)',
        f'{M}.UMP_Integrated_Rail_Right': 'UMP Integrated Rail (Right)',
    })
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')
    # the gun tooltip's row for the MP7A1's folding grip (Tooltip_weapon_<PartType>), named like GoM's "Stock (Integrated)"
    tip_path = os.path.join(ROOT, 'lua/shared/Translate/EN/Tooltip.json')
    tips = json.load(open(tip_path)) if os.path.exists(tip_path) else {}
    tips['Tooltip_weapon_ForegripIntegrated'] = 'Foregrip (Integrated)'
    write('lua/shared/Translate/EN/Tooltip.json', json.dumps(tips, indent=2) + '\n')


if __name__ == '__main__':
    mp7 = load_points('mp7_points.json')
    mp7a2 = load_points('mp7a2_points.json')
    p90 = load_points('p90_points.json')
    fiveseven = load_points('fiveseven_points.json')
    ucp = load_points('ucp_points.json')
    scarl = load_points('scarl_points.json')
    scarh = load_points('scarh_points.json')
    ump = load_points('ump_points.json')
    models(mp7, mp7a2, p90, fiveseven, ucp, scarl, scarh, ump)
    fiveseven_item()                      # before items(): ucp_item() copies its block
    items(mp7, p90)
    translations()
    print('written under', os.path.normpath(ROOT))
