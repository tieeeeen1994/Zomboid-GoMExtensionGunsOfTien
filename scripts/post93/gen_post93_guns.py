"""Writes the MP7A1 / P90 TR / Five-seveN / UCP Prototype / SCAR-L / SCAR-H / UMP45 / UMP9 / Steyr AUG A3, Para and HBAR
/ KRISS Vector .45, 9mm, CRB and SDP / PS90 Carbine / MDRx .223 and .308 item and model scripts, their parts, repair recipes and names for Guns of Tien - Post-93
(the AUGs' points: build_aug3.py's auga3 / augpara / aughbar_points.json; the Vectors': build_vector.py's
vector_points.json / vector9_points.json, build_vectorcrb.py's vectorcrb_points.json, build_vectorsdp.py's
vectorsdp_points.json; the MDRx's: build_mdr.py's mdr223 / mdr308_points.json).

Run after the model builders (build_mp7.py / build_p90.py / build_fiveseven.py / build_ucp.py / build_scar.py /
build_ump.py), which write the attachment points to mp7_points.json, p90_points.json, fiveseven_points.json,
ucp_points.json, scarl_points.json, scarh_points.json and ump_points.json next to this script:
python3 scripts/post93/gen_post93_guns.py
The Five-seveN is the item MarzGuns.FIVESEVEN: Guns of Marz names it ("5.7x28mm Five-SeveN" in its ItemName.json; ours
renames it "Five-SeveN", 2026-11-01) but ships nothing else, so its item block (items_fiveseven.txt) is in GoM's module and everything it uses is ours.
Icons are item_GunsOfTienPost93_<name>.png (prefixed, so another mod's MP7 or P90 icon cannot replace them).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', 'Contents', 'mods', 'GoMExtensionGunsOfTienPost93', '42', 'media')
M = 'GunsOfTienPost93'
TEX = 'weapons/GunsOfTienPost93'

# GoM accessories the guns can carry, drawn at the gun's points (same lists as the MP5's ModelWeaponPart lines).
# optic -> how far the UMPs draw it raised (its own `scope` point; fit_audit.py)
UMP_OPTIC_RAISE = {'PSO1_Scope': 0.0056}
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
                 'bolt_fired', 'handle_back'] + extra_points:
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
    # MP7A1_1H / MP7A2_1H: the same model, kept for guns saved with it (a one-hand swap until 2026-10-28)
    out.append(gun_model('MP7A1', 'GunsOfTienPost93_MP7A1', 'MP7A1_BODY', mp7,
                         ['stock_folded', 'foregrip_deployed', 'rifle_back', 'rifle_back_bag'])
               .replace('    model MP7A1 {', '    model MP7A1_1H {', 1))
    # the MP7A2's body and texture are its own; bolt carrier, handle and stock are the A1's models (MP7A1_BOLT /
    # MP7A1_HANDLE / MP7A1_STOCK)
    out.append(gun_model('MP7A2', 'GunsOfTienPost93_MP7A2', 'MP7A2_BODY', mp7a2,
                         ['stock_folded', 'rail_down', 'foregrip', 'rifle_back', 'rifle_back_bag']))
    out.append(gun_model('MP7A2', 'GunsOfTienPost93_MP7A2', 'MP7A2_BODY', mp7a2,
                         ['stock_folded', 'rail_down', 'foregrip', 'rifle_back', 'rifle_back_bag']).replace('    model MP7A2 {', '    model MP7A2_1H {', 1))
    out.append(gun_model('P90TR', 'GunsOfTienPost93_P90TR', 'P90TR_BODY', p90, ['rifle_back', 'rifle_back_bag']))
    out.append(pistol_model('FIVESEVEN', fiveseven))
    out.append(pistol_model('UCP', ucp))
    scar_points = ['stock', 'stock_folded', 'rail_down', 'foregrip', 'bipod']
    out.append(gun_model('SCARL', 'GunsOfTienPost93_SCARL', 'SCARL_BODY', scarl, scar_points))
    out.append(gun_model('SCARH', 'GunsOfTienPost93_SCARH', 'SCARH_BODY', scarh, scar_points))
    # both UMPs are one mesh (UMP_BODY) with their own textures (markings); bolt and stock shared
    for gun in UMPS:
        out.append(gun_model(gun, 'GunsOfTienPost93_UMP', 'UMP_BODY', ump, ['stock', 'stock_folded', 'rail_down', 'foregrip']))
    # GoM's optics drawn on the UMPs through a model of their own, raised where its mount went into the receiver
    # (scripts/fit_audit.py, 2026-10-26: the PSO-1's side bracket 6.9 x 0.001 into the UMP against 1.3 on GoM's guns)
    for o, dz in UMP_OPTIC_RAISE.items():
        out.append(f"""
    model {o}_UMP {{
        mesh     = weapons/parts/scopes|{o},
        texture  = weapons/parts/scopes/{o},
        cullFace = None,
        attachment scope {{ offset = 0.0000 0.0000 {dz:.4f}, rotate = 0.0000 0.0000 0.0000, }}
    }}
""")
    for model, file, node, tex in [
            ('SCARL_BOLT', 'firearms/GunsOfTienPost93_SCARL', 'SCARL_BOLT', 'SCARL'),
            ('SCARH_BOLT', 'firearms/GunsOfTienPost93_SCARH', 'SCARH_BOLT', 'SCARH'),
            # one folding stock for both SCARs, drawn at each gun's stock / stock_folded point
            ('SCAR_STOCK', 'parts/GunsOfTienPost93_SCAR_parts', 'SCAR_STOCK', 'SCAR_STOCK'),
            # the charging handle's texels are the same in both UMP textures
            ('UMP_BOLT', 'firearms/GunsOfTienPost93_UMP', 'UMP_BOLT', 'UMP9'),
            ('UMP_HANDLE', 'firearms/GunsOfTienPost93_UMP', 'UMP_HANDLE', 'UMP9'),
            ('UMP_STOCK', 'parts/GunsOfTienPost93_UMP_parts', 'UMP_STOCK', 'UMP_STOCK'),
            # the MP7's bolt carrier in its ejection port, and its T charging handle (moved only while racked)
            ('MP7A1_BOLT', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_BOLT', 'MP7A1'),
            ('MP7A1_HANDLE', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_HANDLE', 'MP7A1'),
            ('MP7A1_STOCK', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_STOCK', 'MP7A1'),
            ('MP7A1_FOREGRIP', 'firearms/GunsOfTienPost93_MP7A1', 'MP7A1_FOREGRIP', 'MP7A1'),
            ('P90TR_BOLT', 'firearms/GunsOfTienPost93_P90TR', 'P90TR_BOLT', 'P90TR'),
            ('P90TR_HANDLE', 'firearms/GunsOfTienPost93_P90TR', 'P90TR_HANDLE', 'P90TR')]:
        out.append(f"""
    model {model} {{
        mesh     = weapons/{file}|{node},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    parts = [(f'46x30Magazine{n}_MP7', 'magazines/GunsOfTienPost93_MP7_magazines') for n in (20, 30, 40, 60)]
    # the P90's magazine is the main mod's since 2026-11-03 (its gen_scripts.py ammo_57x28()); the SP90 and the mount
    # device stay here (user, 2026-11-03: post-1993), and fit the main mod's P90 too
    parts += [(p, 'parts/GunsOfTienPost93_P90_parts') for p in ('P90_Suppressor', 'P90_Muzzle_Mount_Device')]
    # GoM's pistol magazines are modelled where they sit in the gun (no `magazine` point) with this floor pose
    parts += [(f'57x28Magazine{n}_FIVESEVEN', 'magazines/GunsOfTienPost93_FIVESEVEN_magazines') for n in (20, 30)]
    parts += [(f'46x30Magazine{n}_UCP', 'magazines/GunsOfTienPost93_UCP_magazines') for n in (20, 40)]
    parts += [(p, 'parts/GunsOfTienPost93_MP7_parts') for p in ('MP7_Suppressor', 'MP7_Muzzle_Mount_Device')]
    parts += [(p, 'parts/GunsOfTienPost93_FIVESEVEN_parts') for p in ('FIVESEVEN_Suppressor',
                                                                       'FIVESEVEN_Muzzle_Mount_Device')]
    parts += [('UCP_Muzzle_Mount_Device', 'parts/GunsOfTienPost93_UCP_parts')]
    parts += [(f'762x51Magazine{n}_SCARH', 'magazines/GunsOfTienPost93_SCARH_magazines') for n in (20, 10, 50)]
    parts += [(p, 'parts/GunsOfTienPost93_SCAR_parts') for p in ('SCARH_Suppressor', 'SCARH_Muzzle_Mount_Device')]
    parts += [(m, 'magazines/GunsOfTienPost93_UMP_magazines') for m in UMP_MAGS]
    # the pistol magazines in the reload's off hand: Gunworks draws them at Bip01_Prop2 through their own point of that
    # name (build_mp7.py bip01_prop2(), each points file's _extras.prop2; the long one shares its gun's 20's)
    prop2 = {f'57x28Magazine{n}_FIVESEVEN': fiveseven['_extras']['prop2'] for n in (20, 30)}
    prop2.update({f'46x30Magazine{n}_UCP': ucp['_extras']['prop2'] for n in (20, 40)})
    for node, file in parts:
        hand = ''
        if node in prop2:
            o, r = prop2[node]['offset'], prop2[node]['rotate']
            hand = (f"\n        attachment Bip01_Prop2 {{ offset = {o[0]:.4f} {o[1]:.4f} {o[2]:.4f}, "
                    f"rotate = {r[0]:.4f} {r[1]:.4f} {r[2]:.4f}, }}")
        out.append(f"""
    model {node} {{
        mesh     = weapons/{file}|{node},
        texture  = {TEX}/{node},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}{hand}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_guns.txt', ''.join(out))


# Guns whose charging handle does not reciprocate (user, 2026-10-30; all of ours but the SCARs): GoM's Bolt part
# draws the bolt carrier, and the main mod's ChargingHandle part (shared/GunsOfTien/ChargingHandle.lua) the handle,
# back only while racked. The UMPs and AUGs add theirs in ump_parts() / aug3_parts().
HANDLE_GUNS = {'MP7A1', 'P90TR', 'PS90'}


def handle_lines(model):
    w = "        ModelWeaponPart              = "
    return [f"{w}GunsOfTien.ChargingHandle_Forward {model} handle handle,",
            f"{w}GunsOfTien.ChargingHandle_Back {model} handle_back handle_back,"]


def model_parts(gun, mags, rails, suppressor, mount, stock, foregrip=False):
    lines = [f"        ModelWeaponPart              = MarzGuns.Bolt_Lock {M}.{gun}_BOLT bolt_lock bolt_lock,",
             f"        ModelWeaponPart              = MarzGuns.Bolt_Fired {M}.{gun}_BOLT bolt_fired bolt_fired,"]
    if gun in HANDLE_GUNS:
        lines += handle_lines(f"{M}.{gun}_HANDLE")
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
# The MP7s and the P90 are one-handed, held like GoM's MP5K (GoM's animations only since 2026-10-29: the MP7s were
# two-handed for our short SMG stance from 2026-10-26 to then).


# GoM's pistol parts the Five-seveN takes (the ModelWeaponPart lines of GoM's Glock 17 / M92FS)
PISTOL_SIGHTS = ['PL4_Sight', 'PM2_Sight', 'PS1_Sight']
# GoM's two pistol lights (LP: compact weapon light; TL: a flashlight in a clamp, the pre-rail way) and its three
# pistol lasers, all on the underbarrel rail (one at a time: GoM gives them all PartType Underbarrel). No lasers from
# 2026-10-16 until 2026-11-13 (user: "all our pistols should be able to be attached a laser attachment").
PISTOL_POINTERS = ['LP_Light', 'TL_Light']
PISTOL_LASERS = ['PJ-3_Laser', 'PX1_Laser', 'TR-1_Laser']


def pistol_laser_lines():
    """GoM's pistol lasers and their beams (the main mod's Lasers.lua) at the underbarrel point, as on the Glock 21."""
    lines = [f"        ModelWeaponPart             = MarzGuns.{o} MarzGuns.{o} underbarrel underbarrel,"
             for o in PISTOL_LASERS]
    lines += [f"        ModelWeaponPart             = GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"GunsOfTien.LaserBeam_{o.replace('-', '')} underbarrel underbarrel," for o in PISTOL_LASERS]
    return lines


def fiveseven_item():
    """MarzGuns.FIVESEVEN, as GoM's pistols (GLOCK17 is the template) on our 5.7x28mm. Light recoil (HitChance 57,
    RecoilDelay 9), M92FS-class damage, pierces 2 with the standard SS190 round like the P90 (its script round, which
    Gunworks never profiles), realistic sound (the main mod's model: 5.7x28mm ~6.7 gr from a 122 mm barrel = 148 / 42;
    the M16 is 175 / 50). Takes GoM's Beretta mount and pistol sights, its pistol lasers and lights on the rail, the
    5.7x28mm family's mount device (shared with the P90, as GoM's pistols share theirs) and its own SFN-57 suppressor
    (user, 2026-10-16: one suppressor per gun)."""
    parts = [f"        ModelWeaponPart             = MarzGuns.Slide_Lock {M}.FIVESEVEN_SLIDE slide_Lock slide_Lock,",
             f"        ModelWeaponPart             = MarzGuns.Slide_Fired {M}.FIVESEVEN_SLIDE slide_fired slide_fired,"]
    parts += [f"        ModelWeaponPart             = {M}.57x28Magazine{n}_FIVESEVEN {M}.57x28Magazine{n}_FIVESEVEN "
              f"magazine magazine," for n in (20, 30)]
    parts += ["        ModelWeaponPart             = MarzGuns.Beretta_Mount MarzGuns.Beretta_Mount rail_up rail_up,"]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} scope scope," for s in PISTOL_SIGHTS]
    parts += pistol_laser_lines()
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
    125 / 36). Takes GoM's Beretta mount and pistol sights, its pistol lasers and lights (as the Five-seveN), and the
    MP7's mount device (drawn as UCP_Muzzle_Mount_Device) and Rotex-II suppressor (user: "use the MP7 suppressor")."""
    parts = [f"        ModelWeaponPart             = MarzGuns.Slide_Lock {M}.UCP_SLIDE slide_Lock slide_Lock,",
             f"        ModelWeaponPart             = MarzGuns.Slide_Fired {M}.UCP_SLIDE slide_fired slide_fired,",
             f"        ModelWeaponPart             = {M}.46x30Magazine20_UCP {M}.46x30Magazine20_UCP magazine magazine,",
             f"        ModelWeaponPart             = {M}.46x30Magazine40_UCP {M}.46x30Magazine40_UCP magazine magazine,",
             "        ModelWeaponPart             = MarzGuns.Beretta_Mount MarzGuns.Beretta_Mount rail_up rail_up,"]
    parts += [f"        ModelWeaponPart             = MarzGuns.{s} MarzGuns.{s} scope scope," for s in PISTOL_SIGHTS]
    parts += pistol_laser_lines()
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
{GUN_HANDGUN}        AmmoType                     = gunsoftienpost93:bullet_46x30,
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
                                         (mp7_mags[3], 60, 0.22, 'bullet_46x30', mp7s)]:    # drum, as the MP5's 60
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
                                     ('P90_Suppressor', 'Canon', 0.9, f'{M}.P90TR;{M}.PS90;GunsOfTien.P90'),
                                     ('FIVESEVEN_Suppressor', 'Canon', 0.8, 'MarzGuns.FIVESEVEN'),
                                     ('P90_Muzzle_Mount_Device', 'CanonMount', 0.5,
                                      f'{M}.P90TR;MarzGuns.FIVESEVEN;{M}.PS90;GunsOfTien.P90')]:
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
        # GoM's STANAG magazines through the main mod's models at our size (gen_scripts.py stanag_got)
        lines += [f"{w}MarzGuns.{m} GunsOfTien.{m}_GoT magazine magazine," for m in STANAGS]
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
    # GoM's weights: its heaviest suppressors 1.2 for the 7.62 can (38 x 190 mm); every mount device 0.5. The MDRx .308
    # takes both (5/8x24, as the SCAR-H; user, 2026-11-04).
    for part, ptype, weight in (('SCARH_Suppressor', 'Canon', 1.2), ('SCARH_Muzzle_Mount_Device', 'CanonMount', 0.5)):
        out.append(f"""
    item {part} {{
        DisplayCategory  = WeaponPart,
        ItemType         = base:weaponpart,
        Icon             = GunsOfTienPost93_{part},
        Weight           = {weight},
        WeightModifier   = {weight},
        MountOn          = {M}.SCARH;{M}.MDR308;{M}.MK11,
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
             f"{w}GunsOfTien.ChargingHandle_Forward {M}.UMP_HANDLE handle handle,",
             f"{w}GunsOfTien.ChargingHandle_Back {M}.UMP_HANDLE handle_back handle_back,",
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
    lines += [f"{w}MarzGuns.{o} {(M + '.' + o + '_UMP') if o in UMP_OPTIC_RAISE else 'MarzGuns.' + o} scope scope,"
              for o in OPTICS]
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


# ==================================================================================================
# KRISS Vector .45 and 9mm, user 2026-10-30 (build_vector.py; docs/post93_design.md)
# ==================================================================================================

VECTORS = ['VECTOR45', 'VECTOR9', 'VECTORCRB', 'VECTORSDP']
# the Vector CRB (user, 2026-11-03: ".45 ACP gets the longer barrel"; build_vectorcrb.py) is the Vector .45 as KRISS's
# CRB Enhanced: its own body (M-LOK handguard, the 16" barrel's shroud) and M4-type stock, the .45's magazines, muzzle
# parts, bolt, handle and side rails
# the Vector SDP ("9x19 gets the shorter one"; build_vectorsdp.py) is the Vector 9mm without its stock, held like a
# pistol as it is: its own turned body, the 9mm's magazines, muzzle parts and turned bolt, handle and side rails
VECTOR_BASE = {'VECTORCRB': 'VECTOR45', 'VECTORSDP': 'VECTOR9'}
VECTOR_NO_STOCK = {'VECTORSDP'}
# Glock's magazines (KRISS built the Vector's well for them): the .45 the main mod's Glock 21 13 and KRISS's MagEx2 30
# (ours; it fits the Glock 21 too), the 9mm GoM's Glock 17 17, Glock's 33 and KRISS's MagEx2 40 (ours; they fit GoM's
# Glock 17 too). (item, the model drawn on the Vector at `magazine`)
VECTOR_MAGS = {
    'VECTOR45': [('GunsOfTien.45Magazine13_GLOCK21', '45Magazine13_VECTOR'),
                 (f'{M}.45Magazine30_GLOCK21', '45Magazine30_VECTOR')],
    'VECTOR9': [('MarzGuns.9x19Magazine17_GLOCK', '9x19Magazine17_VECTOR'),
                (f'{M}.9x19Magazine33_GLOCK', '9x19Magazine33_VECTOR'),
                (f'{M}.9x19Magazine40_GLOCK', '9x19Magazine40_VECTOR')],
}
VECTOR_MAGS['VECTORCRB'] = VECTOR_MAGS['VECTOR45']
VECTOR_MAGS['VECTORSDP'] = VECTOR_MAGS['VECTOR9']
# our magazines: (item, rounds, weight, ammo, the pistol, the Vector, the pistol-space model (its StaticModel and what
# the pistol draws), that model's texture, its Bip01_Prop2 in vector_points.json). GoM's weights: its pistol
# magazines 0.05, its Thompson 20 / 30 = 0.1 / 0.15.
VECTOR_OWN_MAGS = [
    ('45Magazine30_GLOCK21', 30, 0.15, 'swmg:bullet_45', 'GunsOfTien.GLOCK21', 'VECTOR45', '45Magazine30_GLOCK21',
     'weapons/GunsOfTien/45Magazine13_GLOCK21', 'glock21_45Magazine30_prop2'),
    ('9x19Magazine33_GLOCK', 33, 0.1, 'swmg:bullet_9x19', 'MarzGuns.GLOCK17', 'VECTOR9', '9x19Magazine33_GLOCK17',
     'weapons/magazines/pistols/9x19Magazine17_Glock', 'glock17_prop2'),
    ('9x19Magazine40_GLOCK', 40, 0.12, 'swmg:bullet_9x19', 'MarzGuns.GLOCK17', 'VECTOR9', '9x19Magazine40_GLOCK17',
     'weapons/magazines/pistols/9x19Magazine17_Glock', 'glock17_prop2'),
]
VECTOR_MAG_MODELS = ['45Magazine13_VECTOR', '45Magazine30_VECTOR', '9x19Magazine17_VECTOR', '9x19Magazine33_VECTOR',
                     '9x19Magazine40_VECTOR']
# Stats (docs/post93_design.md): GoM's MAC-10 (its other 1000+ rpm SMG) and our UMPs; a 5.5" barrel, under the UMPs'
# 7.9": the .45 a little under the UMP45, the 9mm a little under the UMP9; KRISS's Super V recoil system keeps both
# steadier than any other SMG here (recoil 12 / 11 against the UMPs' 17 / 15; aiming 35 against 40). 2.7 kg x GoM's
# SMG weight ratio (~0.78). Sounds from sound_model.py (5.5": .45 = 78 / 22, 9mm = 107 / 31).
VECTOR_STATS = {
    'VECTOR45': dict(min=1.0, max=1.6, crit=22.0, hit=52, aim=35, recoil=12, range=25.0, stop=2.5, weight=2.1,
                     clip=13, ammo='swmg:bullet_45', box='MarzGuns.45_Box', shoot='M1911Shoot', radius=78, volume=22),
    'VECTOR9': dict(min=0.9, max=1.4, crit=20.0, hit=52, aim=35, recoil=11, range=25.0, stop=2.0, weight=2.0,
                    clip=17, ammo='swmg:bullet_9x19', box='MarzGuns.9x19_Box', shoot='M9Shoot', radius=107, volume=31),
    # The CRB: the Vector .45 with a 16" barrel against 5.5" (230gr .45 ACP at about 1000 ft/s against 850, ~35% more
    # energy, still subsonic), as the PS90 against the P90 TR: more damage and range, steadier and more accurate from
    # two hands and 3.5 kg (7.8 lb x GoM's SMG weight ratio ~0.78 = 2.7), slower to bring up; GoM's .45 Camp Carbine
    # (16.5", 1.0-1.3, hit 55, range 30) is semi-automatic. Sound: sound_model.py's .45 from 16" = 57 / 16.
    'VECTORCRB': dict(min=1.1, max=1.8, crit=22.0, hit=57, aim=40, recoil=11, range=32.0, stop=2.5, weight=2.7,
                      clip=13, ammo='swmg:bullet_45', box='MarzGuns.45_Box', shoot='M1911Shoot', radius=57, volume=16,
                      minsight=5, maxsight=16.0),
    # The SDP: the Vector 9mm's 5.5" barrel (its damage and sound) without a stock: the SMG with its stock folded
    # (hit 52, aim 35) a little less steady, lighter and quicker to bring up, shorter-ranged; 5.9 lb (2.7 kg, the
    # SMG's weight less its 0.2 stock part).
    'VECTORSDP': dict(min=0.9, max=1.4, crit=20.0, hit=50, aim=33, recoil=12, range=22.0, stop=2.0, weight=1.9,
                      clip=17, ammo='swmg:bullet_9x19', box='MarzGuns.9x19_Box', shoot='M9Shoot', radius=107,
                      volume=31),
}


def vector_parts(gun):
    """GoM's accessories on the Vectors: optics on the integral top rail, foregrips on the integral bottom rail,
    lights and lasers on GoM's optional Picatinny_Rail_Left / _Right drawn as KRISS's side rails (VECTOR_RAIL_LEFT /
    _RIGHT); at canon the .45 GoM's .45 mount device and P45, the 9mm the main mod's 9x19mm SMG mount device and Mk9
    (the UMPs' way); the gun's own stock colour, the bolt in the port, the charging handle; its magazines. The 9mm
    draws the turned nodes of its pistol-held model (VECTOR9_*)."""
    w = "        ModelWeaponPart              = "
    tex = VECTOR_BASE.get(gun, gun)
    n = 'VECTOR9' if tex == 'VECTOR9' else 'VECTOR'
    lines = [f"{w}MarzGuns.Bolt_Lock {M}.{n}_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {M}.{n}_BOLT bolt_fired bolt_fired,",
             f"{w}GunsOfTien.ChargingHandle_Forward {M}.{n}_HANDLE handle handle,",
             f"{w}GunsOfTien.ChargingHandle_Back {M}.{n}_HANDLE handle_back handle_back,"]
    if gun not in VECTOR_NO_STOCK:
        lines += [f"{w}{M}.VECTOR_Integrated_Stock_Folded {M}.{gun}_STOCK stock_folded stock_folded,",
                  f"{w}{M}.VECTOR_Integrated_Stock_Deployed {M}.{gun}_STOCK stock stock,"]
    lines += [f"{w}{item} {M}.{model} magazine magazine," for item, model in VECTOR_MAGS[gun]]
    if tex == 'VECTOR45':
        lines += [f"{w}MarzGuns.45_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,",
                  f"{w}MarzGuns.P45_Suppressor MarzGuns.P45_Suppressor canon canon,"]
    else:
        lines += [f"{w}GunsOfTien.SMG9_Muzzle_Mount_Device GunsOfTien.SMG9_Muzzle_Mount_Device_GoT canon canon,",
                  f"{w}GunsOfTien.Mk9_Suppressor GunsOfTien.Mk9_Suppressor_GoT canon canon,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"{w}MarzGuns.{g} MarzGuns.{g} foregrip foregrip," for g in FOREGRIPS]
    lines += [f"{w}MarzGuns.Picatinny_Rail_Left {M}.{n}_RAIL_LEFT rail_left rail_left,",
              f"{w}MarzGuns.Picatinny_Rail_Right {M}.{n}_RAIL_RIGHT rail_right rail_right,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


def vector_item(gun):
    """The UMP's item block (ump_item) with the Vector's stats, magazines and parts."""
    s = VECTOR_STATS[gun]
    block = ump_item('UMP45')
    head, tail = block.split("        MinDamage", 1)
    tail = "        MinDamage" + tail
    for key, value in (('MinDamage', s['min']), ('MaxDamage', s['max']), ('CriticalChance', s['crit']),
                       ('HitChance', s['hit']), ('Aimingtime', s['aim']), ('RecoilDelay', s['recoil']),
                       ('MaxRange', s['range']), ('StopPower', s['stop']), ('Weight', s['weight']),
                       ('AmmoType', s['ammo']), ('AmmoBox', s['box']), ('ClipSize', s['clip']),
                       ('MagazineType', VECTOR_MAGS[gun][0][0]), ('MaxAmmo', s['clip']),
                       ('Icon', f'GunsOfTienPost93_{gun}'), ('WeaponSprite', f'{M}.{gun}'),
                       ('SwingSound', s['shoot']), ('SoundRadius', s['radius']), ('SoundVolume', s['volume']),
                       ('ConditionLowerChanceOneIn', 200), ('MinSightRange', s.get('minsight', 4)),
                       ('MaxSightRange', s.get('maxsight', 12.0))):
        lines = tail.split('\n')
        hits = [i for i, l in enumerate(lines) if l.split('=')[0].strip() == key]
        assert len(hits) == 1, key
        name = lines[hits[0]].split('=')[0]
        lines[hits[0]] = f"{name}= {value},"
        tail = '\n'.join(lines)
    tail = tail.replace(ump_parts('UMP45'), vector_parts(gun))
    assert vector_parts(gun) in tail
    if VECTOR_BASE.get(gun, gun) == 'VECTOR9':
        # held like a pistol (user, 2026-11-01), as the MP7s and the P90 (GUN_HANDGUN): one hand when not aiming,
        # Handgun swing, handgun reload mechanics; still the back slot, never a holster
        for a, c in (("WeaponReloadType             = boltaction,", "WeaponReloadType             = handgun,"),
                     ("        TwoHandWeapon                = true,\n", ""),
                     ("        RequiresEquippedBothHands    = true,\n", ""),
                     ("        IdleAnim                     = Idle_Weapon2,\n", ""),
                     ("SwingAnim                    = Rifle,", "SwingAnim                    = Handgun,"),
                     ("MuzzleFlashModelKey          = muzzle_flash_shotgun,",
                      "MuzzleFlashModelKey          = muzzle_flash_handgun,")):
            assert tail.count(a) == 1, a
            tail = tail.replace(a, c)
    return head.replace('item UMP45 {', f'item {gun} {{') + tail


def vectors():
    """Models, items and repairs of the Vectors (files of their own: models_vector.txt, items_vector.txt,
    fixing_vector.txt). One mesh for the SMGs, each its own texture (colour and markings); the 9mm is held like a
    pistol, so it draws the .45's nodes turned (VECTOR9_*, build_vector.py) at its turned points (vector9_points.json).
    The CRB has a body and stock of its own (build_vectorcrb.py) and draws the .45's other nodes; the SDP a turned
    body of its own and no stock (build_vectorsdp.py), the 9mm's other turned nodes."""
    pts = load_points('vector_points.json')
    pts9 = load_points('vector9_points.json')
    prop2 = pts['_extras']['pistol_magazines']
    out = [f"module {M} {{\n"]
    out.append(gun_model('VECTOR45', 'GunsOfTienPost93_VECTOR', 'VECTOR_BODY', pts,
                         ['stock', 'stock_folded', 'rail_down', 'foregrip']))
    out.append(gun_model('VECTOR9', 'GunsOfTienPost93_VECTOR', 'VECTOR9_BODY', pts9,
                         ['stock', 'stock_folded', 'rail_down', 'foregrip', 'rifle_back', 'rifle_back_bag']))
    out.append(gun_model('VECTORCRB', 'GunsOfTienPost93_VECTORCRB', 'VECTORCRB_BODY',
                         load_points('vectorcrb_points.json'), ['stock', 'stock_folded', 'rail_down', 'foregrip']))
    out.append(gun_model('VECTORSDP', 'GunsOfTienPost93_VECTORSDP', 'VECTORSDP_BODY',
                         load_points('vectorsdp_points.json'), ['rail_down', 'foregrip', 'rifle_back',
                                                                'rifle_back_bag']))
    for n, tex in (('VECTOR', 'VECTOR45'), ('VECTOR9', 'VECTOR9')):
        for part in ('BOLT', 'HANDLE', 'RAIL_LEFT', 'RAIL_RIGHT'):
            out.append(f"""
    model {n}_{part} {{
        mesh     = weapons/firearms/GunsOfTienPost93_VECTOR|{n}_{part},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    for gun, node, fbx in (('VECTOR45', 'VECTOR_STOCK', 'parts/GunsOfTienPost93_VECTOR_parts'),
                           ('VECTOR9', 'VECTOR9_STOCK', 'parts/GunsOfTienPost93_VECTOR_parts'),
                           ('VECTORCRB', 'VECTORCRB_STOCK', 'firearms/GunsOfTienPost93_VECTORCRB')):
        out.append(f"""
    model {gun}_STOCK {{
        mesh     = weapons/{fbx}|{node},
        texture  = {TEX}/{gun}_STOCK,
        cullFace = None,
    }}
""")
    # the magazines as they sit in the Vector: origin at the feed lips, raked as the well
    for mag in VECTOR_MAG_MODELS:
        out.append(f"""
    model {mag} {{
        mesh     = weapons/magazines/GunsOfTienPost93_VECTOR_magazines|{mag},
        texture  = {TEX}/{mag},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
    # our magazines in the pistol's own space (drawn on the Glock 21 / GoM's Glock 17, and the item's model): the
    # pistol's magazine stretched below its middle, with its texture, GoM's floor pose and the hand's point
    for item, *_, model, tex, p in VECTOR_OWN_MAGS:
        o, r = prop2[p]['offset'], prop2[p]['rotate']
        out.append(f"""
    model {model} {{
        mesh     = weapons/magazines/GunsOfTienPost93_VECTOR_magazines|{model},
        texture  = {tex},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
        attachment Bip01_Prop2 {{ offset = {o[0]:.4f} {o[1]:.4f} {o[2]:.4f}, rotate = {r[0]:.4f} {r[1]:.4f} {r[2]:.4f}, }}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_vector.txt', ''.join(out))

    items = [f"module {M} {{\n"] + [vector_item(g) for g in VECTORS]
    for mag, cap, weight, ammo, pistol, gun, model, *_ in VECTOR_OWN_MAGS:
        items.append(f"""
    item {mag} {{
        AmmoType         = {ammo},
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {pistol};{';'.join(f'{M}.{g}' for g in VECTORS if VECTOR_BASE.get(g, g) == gun)},
        PartType         = Clip,
        Tags             = base:hasmetal;base:pistolmagazine,
        Weight           = {weight},
        WeightModifier   = {weight},
        StaticModel      = {M}.{model},
        WorldStaticModel = {M}.{model},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
""")
    for part, ptype, weight in [('VECTOR_Integrated_Stock_Folded', 'StockIntegrated', None),
                                ('VECTOR_Integrated_Stock_Deployed', 'StockIntegrated', 0.2),
                                ('VECTOR_Integrated_Rail_Up', 'RailUp', None),
                                ('VECTOR_Integrated_Rail_Down', 'RailDown', None)]:
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
    write(f'scripts/{M}/items_vector.txt', ''.join(items))
    write(f'scripts/{M}/fixing_vector.txt', "module Base {\n" + "\n".join(f"""    fixing Fix {g} {{
        Require = {M}.{g},
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
""" for g in VECTORS) + "}\n")


# ==================================================================================================
# Steyr AUG A3, AUG Para and AUG HBAR, user 2026-10-28 (build_aug3.py; docs/post93_design.md)
# ==================================================================================================

AUG3 = ['AUGA3', 'AUGPARA', 'AUGHBAR']
AUG3_MAGS = {
    'AUGA3': ['GunsOfTien.556x45Magazine30_AUG', 'GunsOfTien.556x45Magazine42_AUG'],   # the A1's (main mod)
    'AUGPARA': [f'{M}.9x19Magazine25_AUG', f'{M}.9x19Magazine32_AUG'],
    'AUGHBAR': [f'{M}.762x39Magazine30_AUG', f'{M}.762x39Magazine50_AUG'],
}
# our magazines: (item, rounds, weight, ammo, gun): GoM's weights (MP5 30 = 0.18, AK 30 = 0.2, its AK drum 75 = 0.6)
AUG3_OWN_MAGS = [('9x19Magazine25_AUG', 25, 0.15, 'swmg:bullet_9x19', 'AUGPARA'),
                 ('9x19Magazine32_AUG', 32, 0.18, 'swmg:bullet_9x19', 'AUGPARA'),
                 ('762x39Magazine30_AUG', 30, 0.2, 'swmg:bullet_762x39', 'AUGHBAR'),
                 ('762x39Magazine50_AUG', 50, 0.4, 'swmg:bullet_762x39', 'AUGHBAR')]
# Stats (docs/post93_design.md: balanced on each gun's real rate of fire and what reviews say): the A3 the A1's, the
# Para from GoM's MP5, the HBAR from GoM's AK-47. Sounds from sound_model.py (5.56 from 20" = the A1's 175 / 50, 9mm
# from 16.5" = 77 / 22, 7.62x39 from 24.4" = 155 / 44); the A1's M16 handling sounds, the round's shot (GoM's MP5 9mm,
# its AK-47's JS14Shoot).
AUG3_STATS = {
    'AUGA3': dict(min=1.0, max=1.8, crit=25.0, critmult=4.2, hit=45, hitmod=5, aim=45, recoil=15, range=50.0,
                  minsight=8, maxsight=16.0, jam=0.8, cond=200, condmax=10, stop=2.0, door=6, weight=3.6, metal=50.0,
                  ammo='swmg:bullet_556x45', box='MarzGuns.556x45_Box', clip=30, shoot='M16Shoot', gain=2.2,
                  radius=175, volume=50),
    'AUGPARA': dict(min=1.0, max=1.7, crit=20.0, critmult=4.0, hit=52, hitmod=4, aim=40, recoil=13, range=35.0,
                    minsight=4, maxsight=12.0, jam=0.8, cond=200, condmax=10, stop=2.0, door=5, weight=3.3,
                    metal=40.0, ammo='swmg:bullet_9x19', box='MarzGuns.9x19_Box', clip=25, shoot='M9Shoot', gain=2.0,
                    radius=77, volume=22),
    'AUGHBAR': dict(min=1.6, max=1.9, crit=25.0, critmult=6.0, hit=55, hitmod=4, aim=65, recoil=13, range=60.0,
                    minsight=8, maxsight=16.0, jam=0.8, cond=220, condmax=15, stop=2.0, door=6, weight=4.9,
                    metal=60.0, ammo='swmg:bullet_762x39', box='MarzGuns.762x39_Box', clip=30, shoot='JS14Shoot',
                    gain=2.0, radius=155, volume=44),
}


def aug3_parts(gun):
    """Every A3-receiver AUG: the A1's bolt carrier, the charging handle (moved only while racked), the A1's folding
    grip parts (the Para draws its own sand handle and grip), its magazines, GoM's optics on the integral top rail,
    lasers on the integral right rail, lights on GoM's optional left rail drawn as the main mod's short AUG_RAIL_LEFT
    (scripts/build_rails.py, the A1's too); the A3
    GoM's AR muzzle family, the Para the main mod's 9x19mm SMG mount and Mk9 (their `_GoT` models), the HBAR its
    integrated bipod and no muzzle parts."""
    w = "        ModelWeaponPart              = "
    handle = f'{M}.AUGPARA_HANDLE' if gun == 'AUGPARA' else 'GunsOfTien.AUG_HANDLE'
    grip = f'{M}.AUGPARA_FOREGRIP' if gun == 'AUGPARA' else 'GunsOfTien.AUG_FOREGRIP'
    lines = [f"{w}MarzGuns.Bolt_Lock GunsOfTien.AUG_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired GunsOfTien.AUG_BOLT bolt_fired bolt_fired,"]
    lines += handle_lines(handle)
    lines += [f"{w}GunsOfTien.AUG_Integrated_Foregrip_Folded {grip} foregrip_folded foregrip_folded,",
              f"{w}GunsOfTien.AUG_Integrated_Foregrip_Deployed {grip} foregrip_deployed foregrip_deployed,"]
    lines += [f"{w}{m} {m} magazine magazine," for m in AUG3_MAGS[gun]]
    if gun == 'AUGA3':
        lines += [f"{w}MarzGuns.AR_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,"]
        lines += [f"{w}MarzGuns.{p} MarzGuns.{p} canon canon," for p in AR_MUZZLE]
    elif gun == 'AUGPARA':
        lines += [f"{w}GunsOfTien.SMG9_Muzzle_Mount_Device GunsOfTien.SMG9_Muzzle_Mount_Device_GoT canon canon,",
                  f"{w}GunsOfTien.Mk9_Suppressor GunsOfTien.Mk9_Suppressor_GoT canon canon,"]
    else:
        lines += [f"{w}{M}.AUGHBAR_Integrated_Bipod_Folded {M}.AUGHBAR_BIPOD_FOLDED integrated_bipod integrated_bipod,",
                  f"{w}{M}.AUGHBAR_Integrated_Bipod_Deployed {M}.AUGHBAR_BIPOD_DEPLOYED integrated_bipod "
                  f"integrated_bipod,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.Picatinny_Rail_Left GunsOfTien.AUG_RAIL_LEFT rail_left rail_left,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


def aug3_item(gun):
    s = AUG3_STATS[gun]
    return f"""
    item {gun} {{
        MinDamage                    = {s['min']},
        MaxDamage                    = {s['max']},
        CriticalChance               = {s['crit']},
        AimingPerkCritModifier       = 5,
        CritDmgMultiplier            = {s['critmult']},
        HitChance                    = {s['hit']},
        AimingPerkHitChanceModifier  = {s['hitmod']},
        Aimingtime                   = {s['aim']},
        RecoilDelay                  = {s['recoil']},
        MaxRange                     = {s['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {s['minsight']},
        MaxSightRange                = {s['maxsight']},
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = {s['jam']},
        ConditionLowerChanceOneIn    = {s['cond']},
        ConditionMax                 = {s['condmax']},
        PushBackMod                  = 0.3,
        StopPower                    = {s['stop']},
        DoorDamage                   = {s['door']},
        Projectilecount              = 1,
        MaxHitCount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {s['weight']},
        MetalValue                   = {s['metal']},
        FireMode                     = Auto,
        FireModePossibilities        = Auto/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = {s['ammo']},
        AmmoBox                      = {s['box']},
        MagazineType                 = {AUG3_MAGS[gun][0]},
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
        SwingSound                   = {s['shoot']},
        UnequipSound                 = M16UnEquip,
        SoundGain                    = {s['gain']},
        SoundRadius                  = {s['radius']},
        SoundVolume                  = {s['volume']},
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{aug3_parts(gun)}        KnockBackOnNoDeath           = true,
    }}
"""


def augs():
    """Models, items and repairs of the three A3-receiver AUGs (files of their own: models_aug.txt, items_aug.txt,
    fixing_aug.txt)."""
    pts = {g: load_points(g.lower() + '_points.json') for g in AUG3}
    out = [f"module {M} {{\n"]
    for gun in AUG3:
        extra = ['foregrip_deployed', 'foregrip_folded'] + (['integrated_bipod'] if gun == 'AUGHBAR' else [])
        out.append(gun_model(gun, f'GunsOfTienPost93_{gun}', f'{gun}_BODY', pts[gun], extra))
    for model, file, tex in [('AUGPARA_HANDLE', 'GunsOfTienPost93_AUGPARA', 'AUGPARA'),
                             ('AUGPARA_FOREGRIP', 'GunsOfTienPost93_AUGPARA', 'AUGPARA'),
                             ('AUGHBAR_BIPOD_FOLDED', 'GunsOfTienPost93_AUGHBAR', 'AUGHBAR'),
                             ('AUGHBAR_BIPOD_DEPLOYED', 'GunsOfTienPost93_AUGHBAR', 'AUGHBAR')]:
        out.append(f"""
    model {model} {{
        mesh     = weapons/firearms/{file}|{model},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    # the off hand's magazine during GoM's FAMAS reload: GoM's STANAG point as it is (gen_scripts.py GOM_STANAG_PROP2)
    for mag, *_ in AUG3_OWN_MAGS:
        out.append(f"""
    model {mag} {{
        mesh     = weapons/magazines/GunsOfTienPost93_AUG_magazines|{mag},
        texture  = {TEX}/{mag},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
        attachment Bip01_Prop2 {{ offset = 0.0200 0.0538 -0.0146, rotate = -94.9600 23.4300 -89.8200, }}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_aug.txt', ''.join(out))

    items = [f"module {M} {{\n"] + [aug3_item(g) for g in AUG3]
    for mag, cap, weight, ammo, gun in AUG3_OWN_MAGS:
        items.append(f"""
    item {mag} {{
        AmmoType         = {ammo},
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {M}.{gun},
        PartType         = Clip,
        Tags             = {'base:hasmetal;' if gun == 'AUGPARA' else ''}base:riflemagazine,
        Weight           = {weight},
        WeightModifier   = {weight},
        StaticModel      = {M}.{mag},
        WorldStaticModel = {M}.{mag},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
""")
    for part, ptype in [('AUG_Integrated_Rail_Up', 'RailUp'), ('AUG_Integrated_Rail_Right', 'RailRight'),
                        ('AUGHBAR_Integrated_Bipod_Folded', 'BipodIntegrated'),
                        ('AUGHBAR_Integrated_Bipod_Deployed', 'BipodIntegrated')]:
        items.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write(f'scripts/{M}/items_aug.txt', ''.join(items))
    # GoM repairs its FAMAS with Aiming=3, as the main mod's AUG A1
    write(f'scripts/{M}/fixing_aug.txt', "module Base {\n" + "\n".join(f"""    fixing Fix {g} {{
        Require = {M}.{g},
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
""" for g in AUG3) + "}\n")


# ==================================================================================================
# PS90 Carbine, user 2026-11-03 (build_ps90.py)
# ==================================================================================================

# The P90 TR's numbers for the PS90's 16" (407 mm) barrel against the TR's 263 mm: SS190 leaves it at about
# 850 m/s against 715 (~40% more energy), so more damage and range; two hands and 3.3 kg steady it (2.6 = GoM's SMG
# weight ratio ~0.78), and it comes up slower. Sound: the main mod's model, the 5.7x28mm's barrel 263 -> 407 mm =
# -1.9 dB (118 / 34 -> 104 / 30).
PS90_STATS = dict(min=1.1, max=1.7, hit=57, aim=40, recoil=11, range=40.0, minsight=5, maxsight=16.0, weight=2.6,
                  radius=104, volume=30)


def ps90():
    """The PS90 Carbine (user, 2026-11-03; files of its own: models_ps90.txt, items_ps90.txt, fixing_ps90.txt): the
    TR's body with the PS90's long barrel and an M-LOK handguard, held as a rifle, so drawn upright at
    ps90_points.json. Takes the P90's magazine, mount device and SP90 (their MountOn in items()), GoM's optics on the
    receiver's rail, its foregrips under the handguard and its lights and lasers on its sides (four hidden integral
    rail parts; the handguard's M-LOK slots carry them, no rails drawn)."""
    pts = load_points('ps90_points.json')
    s = PS90_STATS
    out = [f"module {M} {{\n"]
    out.append(gun_model('PS90', 'GunsOfTienPost93_PS90', 'PS90_BODY', pts, ['rail_down', 'foregrip']))
    for part in ('BOLT', 'HANDLE'):
        out.append(f"""
    model PS90_{part} {{
        mesh     = weapons/firearms/GunsOfTienPost93_PS90|PS90_{part},
        texture  = {TEX}/PS90,
        cullFace = None,
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_ps90.txt', ''.join(out))
    parts = model_parts('PS90', ['57x28Magazine50_P90'], None, 'P90_Suppressor', 'P90_Muzzle_Mount_Device', False)
    parts += ''.join(f"        ModelWeaponPart              = MarzGuns.{g} MarzGuns.{g} foregrip foregrip,\n"
                     for g in FOREGRIPS)
    items = [f"module {M} {{\n    imports {{ Base }}\n", f"""
    item PS90 {{
        MinDamage                    = {s['min']},
        MaxDamage                    = {s['max']},
        CriticalChance               = 20.0,
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 4.0,
        HitChance                    = {s['hit']},
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = {s['aim']},
        RecoilDelay                  = {s['recoil']},
        MaxRange                     = {s['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {s['minsight']},
        MaxSightRange                = {s['maxsight']},
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        ConditionLowerChanceOneIn    = 220,
        StopPower                    = 2.0,
        Weight                       = {s['weight']},
        MetalValue                   = 30.0,
{GUN_COMMON}        AmmoType                     = gunsoftienpost93:bullet_57x28,
        AmmoBox                      = {M}.57x28_Box,
        MagazineType                 = {M}.57x28Magazine50_P90,
        MaxAmmo                      = 50,
        Reloadtime                   = 28,
        Icon                         = GunsOfTienPost93_PS90,
        WeaponSprite                 = {M}.PS90,
        SoundGain                    = 1.7,
        SoundRadius                  = {s['radius']},
        SoundVolume                  = {s['volume']},
{parts}    }}
"""]
    for side in ('Up', 'Down', 'Left', 'Right'):
        items.append(f"""
    item PS90_Integrated_Rail_{side} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = Rail{side},
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write(f'scripts/{M}/items_ps90.txt', ''.join(items))
    write(f'scripts/{M}/fixing_ps90.txt', f"""module Base {{
    fixing Fix PS90 {{
        Require = {M}.PS90,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
}}
""")

# ==================================================================================================
# Desert Tech MDRx .223 and .308, user 2026-11-04 (build_mdr.py; docs/post93_design.md)
# ==================================================================================================

MDRS = ['MDR223', 'MDR308']
# Magpul's SR-25-pattern PMAG LR/SR and its D-50 drum: (item, rounds, weight) at GoM's weights (its FAL 20 = 0.2
# steel, so a polymer 20 0.15; the SCAR-H drum 0.5)
PMAGS = [('762x51Magazine10_PMAG', 10, 0.1), ('762x51Magazine20_PMAG', 20, 0.15),
         ('762x51Magazine25_PMAG', 25, 0.18), ('762x51Magazine50_PMAG', 50, 0.5)]
# Semi-automatic only (user, 2026-11-04), as GoM's AR-15 and M14: FireMode Single, no FireModePossibilities.
# The .223 from GoM's AR-15 (the same round from a 16" barrel against its 20": its damage), steadier and slower to
# come up (a 3.7 kg bullpup); the .308 from GoM's M14 (22" against the MDR's 20": a little less top damage), quicker to
# aim. Sounds from sound_model.py (5.56 from 16" = 187 / 53, 7.62x51 from 20" = 216 / 62, the SCAR-H's); GoM's AR-15
# (M16 events) and M14 (M14 events, the SCAR-H's MSR788Shoot) handling sounds.
# RecoilDelay paces semi-automatic fire (the next shot waits for it, ~30 units a second at Aiming 0); user,
# 2026-11-11: fire faster, so 13 -> 10 and 16 -> 12 (about a third quicker than GoM's AR-15 / M14).
MDR_STATS = {
    'MDR223': dict(min=0.8, max=1.6, crit=20.0, critmult=3.5, hit=52, hitmod=4, aim=35, recoil=10, range=50.0,
                   minsight=8, maxsight=16.0, minangle=0.965, jam=1.0, cond=220, condmax=15, stop=2.0, door=4,
                   weight=3.7, metal=45.0, ammo='swmg:bullet_556x45', box='MarzGuns.556x45_Box', clip=30,
                   mag='MarzGuns.556x45Magazine30_STANAG', prefix='M16', shoot='M16Shoot', gain=2.0, radius=187,
                   volume=53),
    'MDR308': dict(min=1.2, max=2.1, crit=40.0, critmult=4.5, hit=52, hitmod=5, aim=50, recoil=12, range=60.0,
                   minsight=10, maxsight=18.0, minangle=0.95, jam=1.0, cond=240, condmax=10, stop=2.0, door=5,
                   weight=4.1, metal=55.0, ammo='swmg:bullet_762x51', box='MarzGuns.762x51_Box', clip=20,
                   mag=f'{M}.762x51Magazine20_PMAG', prefix='M14', shoot='MSR788Shoot', gain=2.5, radius=216,
                   volume=62),
}


def mdr_parts(gun):
    """The bolt carrier in the right side's window (GoM's Bolt swap), the ambidextrous charging handle (back only while
    racked), the magazines (GoM's STANAGs at our size on the .223, the PMAGs on the .308), the muzzle parts (GoM's AR
    family on the .223, the SCAR-H's mount and SOCOM762-RC on the .308), GoM's optics on the top rail (a hidden
    integral part), lights and lasers on GoM's optional Picatinny_Rail_Left / _Right drawn as our M-LOK sections
    (MDR*_RAIL_LEFT / _RIGHT; user, 2026-11-04). The .223 takes GoM's foregrips under its handguard (a hidden
    integral part); the .308 has BLK LBL's ALX bipod handguard, whose legs fold into its underside (no foregrips),
    drawn at `integrated_bipod` as the AUG HBAR's. No GoM bipod on either (user, 2026-11-04)."""
    w = "        ModelWeaponPart              = "
    lines = [f"{w}MarzGuns.Bolt_Lock {M}.{gun}_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {M}.{gun}_BOLT bolt_fired bolt_fired,"]
    lines += handle_lines(f"{M}.{gun}_HANDLE")
    if gun == 'MDR223':
        lines += [f"{w}MarzGuns.{m} GunsOfTien.{m}_GoT magazine magazine," for m in STANAGS]
        lines += [f"{w}MarzGuns.AR_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,"]
        lines += [f"{w}MarzGuns.{p} MarzGuns.{p} canon canon," for p in AR_MUZZLE]
    else:
        lines += [f"{w}{M}.{m} {M}.{m} magazine magazine," for m, _, _ in PMAGS]
        lines += [f"{w}GunsOfTien.762x51Magazine20_SR25 GunsOfTien.762x51Magazine20_SR25 magazine magazine,"]
        lines += [f"{w}{M}.SCARH_Muzzle_Mount_Device {M}.SCARH_Muzzle_Mount_Device canon canon,",
                  f"{w}{M}.SCARH_Suppressor {M}.SCARH_Suppressor canon canon,"]
        lines += [f"{w}{M}.MDR308_Integrated_Bipod_Folded {M}.MDR308_BIPOD_FOLDED integrated_bipod integrated_bipod,",
                  f"{w}{M}.MDR308_Integrated_Bipod_Deployed {M}.MDR308_BIPOD_DEPLOYED integrated_bipod "
                  f"integrated_bipod,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    if gun == 'MDR223':
        lines += [f"{w}MarzGuns.{g} MarzGuns.{g} foregrip foregrip," for g in FOREGRIPS]
    lines += [f"{w}MarzGuns.Picatinny_Rail_Left {M}.{gun}_RAIL_LEFT rail_left rail_left,",
              f"{w}MarzGuns.Picatinny_Rail_Right {M}.{gun}_RAIL_RIGHT rail_right rail_right,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    return '\n'.join(lines) + '\n'


def mdr_item(gun):
    s = MDR_STATS[gun]
    p = s['prefix']
    return f"""
    item {gun} {{
        MinDamage                    = {s['min']},
        MaxDamage                    = {s['max']},
        CriticalChance               = {s['crit']},
        AimingPerkCritModifier       = 5,
        CritDmgMultiplier            = {s['critmult']},
        HitChance                    = {s['hit']},
        AimingPerkHitChanceModifier  = {s['hitmod']},
        Aimingtime                   = {s['aim']},
        RecoilDelay                  = {s['recoil']},
        MaxRange                     = {s['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {s['minsight']},
        MaxSightRange                = {s['maxsight']},
        MinRange                     = 0.61,
        MinAngle                     = {s['minangle']},
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = {s['jam']},
        ConditionLowerChanceOneIn    = {s['cond']},
        ConditionMax                 = {s['condmax']},
        PushBackMod                  = 0.3,
        StopPower                    = {s['stop']},
        DoorDamage                   = {s['door']},
        Projectilecount              = 1,
        MaxHitCount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {s['weight']},
        MetalValue                   = {s['metal']},
        FireMode                     = Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = {s['ammo']},
        AmmoBox                      = {s['box']},
        MagazineType                 = {s['mag']},
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
        SwingSound                   = {s['shoot']},
        UnequipSound                 = {p}UnEquip,
        SoundGain                    = {s['gain']},
        SoundRadius                  = {s['radius']},
        SoundVolume                  = {s['volume']},
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{mdr_parts(gun)}        KnockBackOnNoDeath           = true,
    }}
"""


def mdrs():
    """Models, items and repairs of the two MDRx rifles and the PMAGs (files of their own: models_mdr.txt,
    items_mdr.txt, fixing_mdr.txt)."""
    pts = {g: load_points(g.lower() + '_points.json') for g in MDRS}
    out = [f"module {M} {{\n"]
    for gun in MDRS:
        out.append(gun_model(gun, f'GunsOfTienPost93_{gun}', f'{gun}_BODY', pts[gun],
                             ['integrated_bipod'] if gun == 'MDR308' else ['rail_down', 'foregrip']))
        parts = ['BOLT', 'HANDLE', 'RAIL_LEFT', 'RAIL_RIGHT']
        if gun == 'MDR308':
            parts += ['BIPOD_FOLDED', 'BIPOD_DEPLOYED']
        for part in parts:
            tex = f"{gun}_BIPOD" if part.startswith('BIPOD') else gun
            out.append(f"""
    model {gun}_{part} {{
        mesh     = weapons/firearms/GunsOfTienPost93_{gun}|{gun}_{part},
        texture  = {TEX}/{tex},
        cullFace = None,
    }}
""")
    # the off hand's magazine during GoM's FAMAS reload: GoM's STANAG point as it is (modelled about the feed lips,
    # hanging down, as GoM's STANAGs; gen_scripts.py GOM_STANAG_PROP2)
    for mag, _, _ in PMAGS:
        out.append(f"""
    model {mag} {{
        mesh     = weapons/magazines/GunsOfTienPost93_PMAG_magazines|{mag},
        texture  = {TEX}/{mag},
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
        attachment Bip01_Prop2 {{ offset = 0.0200 0.0538 -0.0146, rotate = -94.9600 23.4300 -89.8200, }}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_mdr.txt', ''.join(out))

    items = [f"module {M} {{\n"] + [mdr_item(g) for g in MDRS]
    for mag, cap, weight in PMAGS:
        items.append(f"""
    item {mag} {{
        AmmoType         = swmg:bullet_762x51,
        CanStack         = false,
        DisplayCategory  = WeaponMagazine,
        Icon             = GunsOfTienPost93_{mag},
        ItemType         = base:weaponpart,
        MaxAmmo          = {cap},
        MountOn          = {M}.MDR308;{M}.MK11;GunsOfTien.SR25,
        PartType         = Clip,
        Tags             = base:riflemagazine,
        Weight           = {weight},
        WeightModifier   = {weight},
        StaticModel      = {M}.{mag},
        WorldStaticModel = {M}.{mag},
        UseDelta         = 1,
        CanAttach        = MarzGuns_AttachAndDetach.IsMagazine,
        CanDetach        = MarzGuns_AttachAndDetach.IsMagazine,
    }}
""")
    # the hidden integral top and bottom rails (the sides take GoM's optional rails), the ALX's legs
    for part, ptype in [('MDR_Integrated_Rail_Up', 'RailUp'), ('MDR_Integrated_Rail_Down', 'RailDown'),
                        ('MDR308_Integrated_Bipod_Folded', 'BipodIntegrated'),
                        ('MDR308_Integrated_Bipod_Deployed', 'BipodIntegrated')]:
        items.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write(f'scripts/{M}/items_mdr.txt', ''.join(items))
    # GoM repairs its FAMAS (its other bullpup) with Aiming=3, as the AUGs
    write(f'scripts/{M}/fixing_mdr.txt', "module Base {\n" + "\n".join(f"""    fixing Fix {g} {{
        Require = {M}.{g},
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
""" for g in MDRS) + "}\n")


# Knight's Mk 11 Mod 0 (user, 2026-11-12; docs/post93_design.md "Knight's Mk 11 Mod 0"; meshes and points:
# scripts/post93/build_mk11.py on the main mod's SR-25 receiver and GoM's AR15 texture; registries:
# shared/GunsOfTienPost93/MK11.lua). Moddable: integrated Picatinny rails on all four sides (hidden parts, modelled in
# the body) for GoM's optics, foregrips, bipods, lights and lasers; the 7.62x51mm mount device and SOCOM762-RC; the
# SR-25 pattern magazines (the main mod's KAC 20, the PMAGs); GoM's AR bolt and charging handle parts drawn with its
# own nodes. Semi-automatic only. Stats from the MDRx .308 (the same 20" 7.62x51, GoM's M14 base) with a match
# barrel's accuracy (HitChance 56) and GoM's M14 pace (RecoilDelay 14); weight 4.5 (9.8 lb empty, GoM's M14 4.2 for
# 4.5 kg); sound 216 / 62 from sound_model.py (7.62x51 from 20", as the SCAR-H and MDRx .308).
MK11_TEX = 'weapons/firearms/assault_rifles/AR15'
MK11_RAILS = [('MK11_Integrated_Rail_Up', 'RailUp'), ('MK11_Integrated_Rail_Down', 'RailDown'),
              ('MK11_Integrated_Rail_Left', 'RailLeft'), ('MK11_Integrated_Rail_Right', 'RailRight')]


def mk11():
    pts = load_points('mk11_points.json')
    out = [f"module {M} {{\n", f"""
    model MK11 {{
        mesh     = weapons/firearms/GunsOfTienPost93_MK11|MK11_BODY,
        texture  = {MK11_TEX},
        cullFace = None,
"""]
    for name in ('muzzle', 'world', 'magazine', 'bolt_fired', 'charging_handle_open', 'canon', 'scope', 'foregrip',
                 'bipod', 'light_left', 'laser_right'):
        out.append(attachment(name, pts[name]))
    out.append("    }\n")
    for node in ('BOLT', 'CHARGING_HANDLE'):
        out.append(f"""
    model MK11_{node} {{
        mesh     = weapons/firearms/GunsOfTienPost93_MK11|MK11_{node},
        texture  = {MK11_TEX},
        cullFace = None,
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_mk11.txt', ''.join(out))

    w = "        ModelWeaponPart              = "
    lines = [f"{w}MarzGuns.Bolt_Lock {M}.MK11_BOLT bolt_lock bolt_lock,",
             f"{w}MarzGuns.Bolt_Fired {M}.MK11_BOLT bolt_fired bolt_fired,",
             f"{w}MarzGuns.Charging_Handle_Close {M}.MK11_CHARGING_HANDLE charging_handle_lock charging_handle_lock,",
             f"{w}MarzGuns.Charging_Handle_Open {M}.MK11_CHARGING_HANDLE charging_handle_open charging_handle_open,",
             f"{w}GunsOfTien.762x51Magazine20_SR25 GunsOfTien.762x51Magazine20_SR25 magazine magazine,"]
    lines += [f"{w}{M}.{m} {M}.{m} magazine magazine," for m, _, _ in PMAGS]
    lines += [f"{w}{M}.SCARH_Muzzle_Mount_Device {M}.SCARH_Muzzle_Mount_Device canon canon,",
              f"{w}{M}.SCARH_Suppressor {M}.SCARH_Suppressor canon canon,"]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
    lines += [f"{w}MarzGuns.{g} MarzGuns.{g} foregrip foregrip," for g in FOREGRIPS]
    lines += [f"{w}MarzGuns.{b} MarzGuns.{b} bipod bipod," for b in ('Bipod_Deployed', 'Bipod_Folded')]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} laser_right laser_right," for o in LASERS]
    lines += [f"{w}GunsOfTien.LaserBeam_{o.replace('-', '')} GunsOfTien.LaserBeam_{o.replace('-', '')} "
              f"laser_right laser_right," for o in LASERS]
    lines += [f"{w}MarzGuns.{o} MarzGuns.{o} light_left light_left," for o in LIGHTS]
    items = [f"module {M} {{\n", f"""
    item MK11 {{
        MinDamage                    = 1.2,
        MaxDamage                    = 2.1,
        CriticalChance               = 40.0,
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 4.5,
        HitChance                    = 56,
        AimingPerkHitChanceModifier  = 5,
        Aimingtime                   = 50,
        RecoilDelay                  = 14,
        MaxRange                     = 60.0,
        AimingPerkRangeModifier      = 0,
        MinSightRange                = 10,
        MaxSightRange                = 18.0,
        MinRange                     = 0.61,
        MinAngle                     = 0.95,
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = 1.0,
        ConditionLowerChanceOneIn    = 260,
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        StopPower                    = 2.0,
        DoorDamage                   = 5,
        Projectilecount              = 1,
        MaxHitCount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = 4.5,
        MetalValue                   = 55.0,
        FireMode                     = Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = swmg:bullet_762x51,
        AmmoBox                      = MarzGuns.762x51_Box,
        MagazineType                 = GunsOfTien.762x51Magazine20_SR25,
        MaxAmmo                      = 20,
        Reloadtime                   = 25,
        WeaponReloadType             = boltaction,
        TwoHandWeapon                = true,
        RequiresEquippedBothHands    = true,
        UseEndurance                 = false,
        MinimumSwingtime             = 0.5,
        Swingtime                    = 0.5,
        SwingAmountBeforeImpact      = 0.0,
        Icon                         = GunsOfTienPost93_MK11,
        IdleAnim                     = Idle_Weapon2,
        RunAnim                      = Run_Weapon2,
        SwingAnim                    = Rifle,
        WeaponSprite                 = {M}.MK11,
        AimReleaseSound              = M14AimRelease,
        BreakSound                   = M14Break,
        BringToBearSound             = M14BringToBear,
        ClickSound                   = M14Jam,
        DropSound                    = M14Drop,
        EjectAmmoStartSound          = M14EjectAmmoStart,
        EjectAmmoSound               = M14EjectAmmo,
        EjectAmmoStopSound           = M14EjectAmmoStop,
        EquipSound                   = M14Equip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = M14InsertAmmoStart,
        InsertAmmoSound              = M14InsertAmmo,
        InsertAmmoStopSound          = M14InsertAmmoStop,
        RackSound                    = M14Rack,
        ShellFallSound               = M14CartridgeFall,
        SwingSound                   = MSR788Shoot,
        UnequipSound                 = M14UnEquip,
        SoundGain                    = 2.5,
        SoundRadius                  = 216,
        SoundVolume                  = 62,
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{chr(10).join(lines)}
        KnockBackOnNoDeath           = true,
    }}
"""]
    for part, ptype in MK11_RAILS:
        items.append(f"""
    item {part} {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = {ptype},
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    items.append("}\n")
    write(f'scripts/{M}/items_mk11.txt', ''.join(items))
    # GoM repairs its M14 / PSG-1 with Aiming=3
    write(f'scripts/{M}/fixing_mk11.txt', f"""module Base {{
    fixing Fix MK11 {{
        Require = {M}.MK11,
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
}}
""")
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(path))
    names[f'{M}.MK11'] = 'Mk 11 Mod 0 Semi-Automatic Rifle'     # GoM's "PSG-1 Semi-Automatic Rifle" (user, 2026-11-12)
    for part, ptype in MK11_RAILS:
        names[f'{M}.{part}'] = 'Mk 11 Integrated Rail (%s)' % ptype[4:]
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


# The OTs-14 Groza (user, 2026-11-11 / 12; docs/post93_design.md "OTs-14 Groza family"; meshes and points:
# scripts/post93/build_groza.py; registries: shared/GunsOfTienPost93/Groza.lua). TsKIB SOO's bullpup on the AKS-74U's
# mechanism, shown in April 1994. Three regular guns on one atlas (the GP-25 version is its own, later):
# - GROZA1 "Groza-1": 7.62x39, the long barrel (GROZA_BODY), forend and front grip; GoM's "762x39" magazines (its 30
#   and 75 box at our size, the main mod's RPK 40 and drum); GoM's AK muzzle mount and PBS-1 (so US Subsonic cycles it);
# - GROZA2 "Groza-2 Prototype": 5.45x39, the compact OTs-14-4A of the user's photo, no forend; held like a pistol
#   (user, 2026-11-12: "hold Groza-2 using handgun stance"), as GoM's MP5K and our MP7: GROZA2_HELD (the body turned
#   180 degrees about the bore) and its turned points (groza_points.json "held"), GoM's handgun item lines
#   (GUN_HANDGUN's); GoM's "545x39" magazines (Bakelite 30 / 45 / 60, the 100 drum) at our size; no muzzle parts;
# - GROZA4 "Groza-4": 9x39, the short barrel in the forend (GROZA4_BODY), front grip; GoM's AS VAL 10 / 20 / 30 at our
#   size; its suppressor built in (user, 2026-11-12: "9x39 default ammo is treated as subsonic... but the gun took the
#   stats into its own", GoM's AS VAL): the quiet sound in the gun's own stats (GoM's AS VAL lines, CapGunRevolverShoot
#   at gain 0.8, no muzzle flash) and the can drawn by a hidden part that cannot come off (as the SR-25's scope).
# All: GoM's Picatinny Rail (Up) drawn as GROZA_RAIL_UP (a base clamped on the carrying handle with GoM's own rail on
# it) and GoM's optics on it; the AK carrier and handle as one part on GoM's bolt swap; Auto / Single at 700 rpm.
# Stats from GoM's AK-47 (Groza-1), AKS-74U (Groza-2) and AS VAL (Groza-4), a bullpup's steadier hold (HitChance a
# little up); sounds from sound_model.py: 7.62x39 from 16.5" = 175 / 50 (GoM's AK-47's), 5.45 from about 8" =
# 205 / 59 (its AKS-74U's), the Groza-4 24 / 6: a bit louder than GoM's AS VAL (22 / 6 in the main mod's
# SoundTable, the user's figure for the integrally suppressed guns), as in real life (user, 2026-11-12: "make the groza
# louder as it's louder in real life", then "just a bit", "like maybe a 24 / 6"): the AS VAL's can wraps a ported barrel, the
# Groza's is a plain can on the muzzle of an ordinary one.
GROZAS = {
    'GROZA1': dict(body='GROZA_BODY', mag_point='magazine_762x39', muzzle='muzzle_long', canon='long',
                   name='Groza-1 Assault Rifle', min=1.5, max=1.8, crit=25.0, critmult=6.0, hit=52, aim=50,
                   range=50.0, sight=(8, 16.0), jam=0.5, cond=300, weight=3.0, ammo='swmg:bullet_762x39',
                   box='MarzGuns.762x39_Box', mag='MarzGuns.762x39Magazine30', clip=30, shoot='JS14Shoot', gain=2.0,
                   radius=175, volume=50),
    'GROZA2': dict(body='GROZA2_HELD', held=True, mag_point='magazine_545x39', muzzle='muzzle_compact', canon=None,
                   name='Groza-2 Prototype Assault Rifle', min=1.0, max=1.6, crit=25.0, critmult=3.0, hit=35, aim=25,
                   range=40.0, sight=(6, 14.0), jam=0.5, cond=250, weight=2.6, ammo='swmg:bullet_545x39',
                   box='MarzGuns.545x39_Box', mag='MarzGuns.545x39Magazine30_Bakelite', clip=30, shoot='JS14Shoot',
                   gain=2.0, radius=205, volume=59),
    'GROZA4': dict(body='GROZA4_BODY', mag_point='magazine', muzzle='muzzle', canon='integral', flash=False,
                   name='Groza-4 Assault Rifle', min=0.7, max=1.4, crit=20.0, critmult=4.5, hit=52, aim=35,
                   range=45.0, sight=(6, 14.0), jam=1.0, cond=250, weight=2.7, ammo='swmg:bullet_9x39',
                   box='MarzGuns.9x39_Box', mag='MarzGuns.9x39Magazine20', clip=20, shoot='CapGunRevolverShoot',
                   gain=0.8, radius=24, volume=6),
}
# GROZAGL "Groza-1 Assault Rifle with GP-25" (user, 2026-11-12: "Make the Groza-1 with GP-25 now"), built as GoM's
# M16A2_M203 (its "M16A2 Assault Rifle with M203"): the Groza-1 on GROZAGL_BODY (the GP-25's casing as the handguard,
# its trigger base in place of the rifle's guard), the Groza-1's stats, parts and magazines, heavier by the launcher
# (GoM: the M16A2 3.4, with the M203 4.7; the GP-25 is 1.5 kg and replaces the forend: 3.0 + 1.2); a hidden
# GROZAGL_GP25_Integrated part (PartType Underbarrel, GoM's M16A2_M203_Integrated) that Gunworks' Underbarrel swaps for
# the launcher weapon GROZAGL_GP25 (shared/GunsOfTienPost93/Groza.lua), drawn with its own model: the same body with
# its muzzle at the GP-25's bore (`muzzle_gl`), as GoM's M16A2_M203_Underbarrel.
GROZAS['GROZAGL'] = dict(GROZAS['GROZA1'], body='GROZAGL_BODY', name='Groza-1 Assault Rifle with GP-25', weight=4.2)
GROZA_GL_LAUNCHER_MODEL = dict(GROZAS['GROZAGL'], muzzle='muzzle_gl', canon_muzzle='muzzle_long')

GROZA_MAGS = {   # GoM's magazines each takes, and the model it is drawn with at our size
    'GROZA1': [('MarzGuns.762x39Magazine30', 'GunsOfTien.762x39Magazine30_GoT'),
               ('MarzGuns.762x39Magazine75', 'GunsOfTien.762x39Magazine75_GoT'),
               ('GunsOfTien.762x39Magazine40_RPK', 'GunsOfTien.762x39Magazine40_RPK'),
               ('GunsOfTien.762x39Drum75_RPK', 'GunsOfTien.762x39Drum75_RPK')],
    'GROZA2': [('MarzGuns.545x39Magazine%s' % n, 'GunsOfTien.545x39Magazine%s_GoT' % n)
               for n in ('30_Bakelite', '45_Bakelite', '60_Bakelite', '100_Drum')],
    'GROZA4': [('MarzGuns.9x39Magazine%d' % n, f'{M}.9x39Magazine%d_GoT' % n) for n in (10, 20, 30)],
}
GROZA_MAGS['GROZAGL'] = GROZA_MAGS['GROZA1']
GROZA_GOT_SCALE = round(0.603 / 0.645, 4)          # GoM's rifles' magazines at our size (build_rpk.py's SCALE)
GOM_9X39_PROP2 = ('0.0279 0.0937 -0.0020', '-86.2737 31.4012 -93.4148')   # GoM's own, kept unscaled (HandMagazines)
GROZA_AK_CANON_BACK = 0.0282     # GoM's AK-47: its canon 0.0302 behind its muzzle at 0.645 = 46.8 mm, at our 0.603


def grozas():
    pts = load_points('groza_points.json')
    out = [f"module {M} {{\n"]
    for gun, g in list(GROZAS.items()) + [('GROZAGL_GP25', GROZA_GL_LAUNCHER_MODEL)]:
        muzzle = pts[g['muzzle']]
        if g.get('held'):           # held like a pistol: the turned body's points, all of them precomputed
            out.append(f"""
    model {gun} {{
        mesh     = weapons/firearms/GunsOfTienPost93_GROZA|{g['body']},
        texture  = {TEX}/GROZA,
        cullFace = None,
""")
            for name, value in pts['held'].items():
                out.append(attachment(name, value))
            out.append("    }\n")
            continue
        out.append(f"""
    model {gun} {{
        mesh     = weapons/firearms/GunsOfTienPost93_GROZA|{g['body']},
        texture  = {TEX}/GROZA,
        cullFace = None,
""")
        out.append(attachment('muzzle', muzzle, [-90, 0, -180]))
        out.append(attachment('world', pts['world']))
        out.append(attachment('magazine', pts[g['mag_point']]))
        for name in ('bolt_fired', 'rail_up', 'scope'):
            out.append(attachment(name, pts[name]))
        if g['canon'] == 'integral':
            out.append(attachment('canon', pts['canon']))
        elif g['canon'] == 'long':
            o = pts[g.get('canon_muzzle', g['muzzle'])]['offset']
            out.append(attachment('canon', [o[0], round(o[1] - GROZA_AK_CANON_BACK, 4), o[2]], [0, 0, 0]))
        out.append("    }\n")
    for node in ('GROZA_BOLT', 'GROZA_RAIL_UP'):
        out.append(f"""
    model {node} {{
        mesh     = weapons/firearms/GunsOfTienPost93_GROZA|{node},
        texture  = {TEX}/GROZA,
        cullFace = None,
    }}
""")
    out.append(f"""
    model GROZA_Suppressor {{
        mesh     = weapons/parts/GunsOfTienPost93_GROZA_parts|GROZA_Suppressor,
        texture  = {TEX}/GROZA_Suppressor,
        cullFace = None,
        attachment world {{ offset = 0.0000 0.0000 0.0000, rotate = 90.0000 0.0000 -90.0000, }}
    }}
""")
    for n in (10, 20, 30):
        out.append(f"""
    model 9x39Magazine{n}_GoT {{
        mesh     = weapons/magazines/assault_rifles|9x39Magazine{n},
        texture  = weapons/magazines/assault_rifles/9x39Magazine{n},
        cullFace = None,
        scale    = {GROZA_GOT_SCALE:.4f},
        attachment Bip01_Prop2 {{ offset = {GOM_9X39_PROP2[0]}, rotate = {GOM_9X39_PROP2[1]}, }}
    }}
""")
    out.append("}\n")
    write(f'scripts/{M}/models_groza.txt', ''.join(out))

    w = "        ModelWeaponPart              = "
    items = [f"module {M} {{\n"]
    for gun, g in GROZAS.items():
        lines = [f"{w}MarzGuns.Bolt_Lock {M}.GROZA_BOLT bolt_lock bolt_lock,",
                 f"{w}MarzGuns.Bolt_Fired {M}.GROZA_BOLT bolt_fired bolt_fired,"]
        lines += [f"{w}{mag} {model} magazine magazine," for mag, model in GROZA_MAGS[gun]]
        lines += [f"{w}MarzGuns.Picatinny_Rail_Up {M}.GROZA_RAIL_UP rail_up rail_up,"]
        lines += [f"{w}MarzGuns.{o} MarzGuns.{o} scope scope," for o in OPTICS]
        if g['canon'] == 'long':
            lines += [f"{w}MarzGuns.AK_Muzzle_Mount_Device MarzGuns.Muzzle_Mount_Device canon canon,",
                      f"{w}MarzGuns.PBS-1_Suppressor MarzGuns.PBS-1_Suppressor canon canon,"]
        elif g['canon'] == 'integral':
            lines += [f"{w}{M}.GROZA4_Integrated_Suppressor {M}.GROZA_Suppressor canon canon,"]
        if gun == 'GROZAGL':
            gl_lines = list(lines)      # the launcher weapon draws the rifle's parts too (Gunworks clones them onto it)
        text = f"""
    item {gun} {{
        MinDamage                    = {g['min']},
        MaxDamage                    = {g['max']},
        CriticalChance               = {g['crit']},
        AimingPerkCritModifier       = 5,
        CritDmgMultiplier            = {g['critmult']},
        HitChance                    = {g['hit']},
        AimingPerkHitChanceModifier  = 4,
        Aimingtime                   = {g['aim']},
        RecoilDelay                  = 15,
        MaxRange                     = {g['range']},
        AimingPerkRangeModifier      = 0,
        MinSightRange                = {g['sight'][0]},
        MaxSightRange                = {g['sight'][1]},
        MinRange                     = 0.61,
        MinAngle                     = 0.965,
        AimingPerkMinAngleModifier   = 0.01,
        JamGunChance                 = {g['jam']},
        ConditionLowerChanceOneIn    = {g['cond']},
        ConditionMax                 = 10,
        PushBackMod                  = 0.3,
        StopPower                    = 2.0,
        DoorDamage                   = 5,
        Projectilecount              = 1,
        MaxHitCount                  = 1,
        PiercingBullets              = false,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        SubCategory                  = Firearm,
        AttachmentType               = Rifle,
        Tags                         = base:hasmetal;base:firearm,
        Weight                       = {g['weight']},
        MetalValue                   = 40.0,
        FireMode                     = Auto,
        FireModePossibilities        = Auto/Single,
        CyclicRateMultiplier         = 1.0,
        IsAimedFirearm               = true,
        Ranged                       = true,
        AmmoType                     = {g['ammo']},
        AmmoBox                      = {g['box']},
        MagazineType                 = {g['mag']},
        MaxAmmo                      = {g['clip']},
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
        SwingSound                   = {g['shoot']},
        UnequipSound                 = M16UnEquip,
        SoundGain                    = {g['gain']},
        SoundRadius                  = {g['radius']},
        SoundVolume                  = {g['volume']},
        NPCSoundBoost                = 1.5,
        MuzzleFlashModelKey          = muzzle_flash_shotgun,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 3,
        SplatSize                    = 3,
        OnCreate                     = MarzGuns_OnCreate.AttachParts,
{chr(10).join(lines)}
        KnockBackOnNoDeath           = true,
    }}
"""
        if g.get('held'):           # GoM's handgun-held lines (GUN_HANDGUN's edits of GUN_COMMON)
            for a, b in (("WeaponReloadType             = boltaction,", "WeaponReloadType             = handgun,"),
                         ("        TwoHandWeapon                = true,\n", ""),
                         ("        RequiresEquippedBothHands    = true,\n", ""),
                         ("        IdleAnim                     = Idle_Weapon2,\n", ""),
                         ("SwingAnim                    = Rifle,", "SwingAnim                    = Handgun,"),
                         ("MuzzleFlashModelKey          = muzzle_flash_shotgun,",
                          "MuzzleFlashModelKey          = muzzle_flash_handgun,")):
                assert a in text, a
                text = text.replace(a, b)
        if g.get('flash') is False:  # GoM's AS VAL has no muzzle flash
            text = text.replace("        MuzzleFlashModelKey          = muzzle_flash_shotgun,\n", "")
        items.append(text)
    # The GP-25 as a weapon (GoM's M203_Weapon / CAR15_M203_Weapon, its stats and sounds: 40mm, one round, GoM's
    # double-barrel reload), drawn as the Groza with its muzzle at the GP-25's bore. Its VOG-25 grenade is caseless, so
    # nothing is left to pull out (ManuallyRemoveSpentRounds false; GoM's M203 keeps its spent case). GoM's 40mm
    # family (the M203's rounds) stands in for the VOG-25: the same 40 mm bore, and GoM has no other grenade round.
    items.append(f"""
    item GROZAGL_GP25 {{
        MinDamage                    = 1.8,
        MaxDamage                    = 2.0,
        CriticalChance               = 70.0,
        AimingPerkCritModifier       = 6,
        CritDmgMultiplier            = 12.0,
        HitChance                    = 65,
        AimingPerkHitChanceModifier  = 4,
        AimingMod                    = 2.0,
        Aimingtime                   = 40,
        MaxRange                     = 10.0,
        MinSightRange                = 3,
        MaxSightRange                = 8.0,
        MinRange                     = 0.67,
        MinAngle                     = 0.9,
        JamGunChance                 = 0,
        ConditionLowerChanceOneIn    = 50,
        ConditionMax                 = 8,
        DoorDamage                   = 30,
        MaxHitcount                  = 9,
        PiercingBullets              = false,
        Projectilecount              = 9,
        ProjectileSpread             = 3.5,
        ProjectileWeightCenter       = 1.0,
        DisplayCategory              = Weapon,
        ItemType                     = base:weapon,
        AttachmentType               = Rifle,
        Weight                       = {GROZAS['GROZAGL']['weight']},
        MetalValue                   = 80.0,
        FireMode                     = Single,
        IsAimedFirearm               = true,
        IsAimedHandWeapon            = true,
        AmmoType                     = swmg:round_40mm_buckshot,
        AmmoBox                      = MarzGuns.40mm_Box_Buckshot,
        MaxAmmo                      = 1,
        HaveChamber                  = false,
        InsertAllBulletsReload       = true,
        needtobeclosedoncereload     = true,
        Icon                         = GunsOfTienPost93_GROZAGL,
        AimReleaseSound              = DoubleBarrelShotgunAimRelease,
        BreakSound                   = DoubleBarrelShotgunBreak,
        BringToBearSound             = DoubleBarrelShotgunBringToBear,
        ClickSound                   = DoubleBarrelShotgunJam,
        DropSound                    = DoubleBarrelShotgunDrop,
        EjectAmmoStartSound          = DoubleBarrelShotgunEjectAmmoStart,
        EjectAmmoSound               = DoubleBarrelShotgunEjectAmmo,
        EjectAmmoStopSound           = DoubleBarrelShotgunEjectAmmoStop,
        EquipSound                   = DoubleBarrelShotgunEquip,
        HitSound                     = BulletImpact,
        ImpactSound                  = null,
        InsertAmmoStartSound         = DoubleBarrelShotgunInsertAmmoStart,
        InsertAmmoSound              = DoubleBarrelShotgunInsertAmmo,
        InsertAmmoStopSound          = DoubleBarrelShotgunInsertAmmoStop,
        ManuallyRemoveSpentRounds    = false,
        MuzzleFlashModelKey          = muzzle_flash_shotgun_double_barrel,
        PushBackMod                  = 0.8,
        RackAfterShoot               = false,
        Ranged                       = true,
        RangeFalloff                 = true,
        RecoilDelay                  = 30,
        Reloadtime                   = 25,
        RequiresEquippedBothHands    = true,
        RunAnim                      = Run_Weapon2,
        ShellFallSound               = DoubleBarrelShotgunCartridgeFall,
        SoundGain                    = 4.0,
        SoundRadius                  = 300,
        SoundVolume                  = 300,
        StopPower                    = 40.0,
        SubCategory                  = Firearm,
        SwingSound                   = DoubleBarrelShotgunShoot,
        Swingtime                    = 2.0,
        Tags                         = base:hasmetal;base:firearm,
        TwoHandWeapon                = true,
        UnequipSound                 = DoubleBarrelShotgunUnEquip,
        UseEndurance                 = false,
        WeaponReloadType             = doublebarrelshotgun,
        WeaponSprite                 = {M}.GROZAGL_GP25,
        SplatBloodOnNoDeath          = true,
        SplatNumber                  = 5,
        AngleFalloff                 = true,
        KnockBackOnNoDeath           = true,
{chr(10).join(gl_lines)}
    }}

    item GROZAGL_GP25_Integrated {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = Underbarrel,
        Weight          = 0.2,
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    # the Groza-4's built-in can: a hidden part that cannot come off (the SR-25's integrated parts), no stats of its own
    items.append(f"""
    item GROZA4_Integrated_Suppressor {{
        ItemType        = base:weaponpart,
        DisplayCategory = WeaponPart,
        MountOn         = MarzGuns.FakeItem,
        PartType        = Canon,
        CanAttach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
        CanDetach       = MarzGuns_AttachAndDetach.CannotBeRemoved,
    }}
""")
    for n in (10, 20, 30):     # GoM's AS VAL magazines at our size in the off hand (the main mod's HandMagazines.lua)
        items.append(f"""
    item 9x39Magazine{n}_Hand {{
        DisplayCategory  = WeaponMagazine,
        ItemType         = base:normal,
        Icon             = 9x39Magazine{n},
        Weight           = 0.0,
        Hidden           = true,
        StaticModel      = {M}.9x39Magazine{n}_GoT,
        WorldStaticModel = {M}.9x39Magazine{n}_GoT,
    }}
""")
    items.append("}\n")
    write(f'scripts/{M}/items_groza.txt', ''.join(items))
    # GoM repairs its AKs with Aiming=3
    write(f'scripts/{M}/fixing_groza.txt', "module Base {\n" + "\n".join(f"""    fixing Fix {g} {{
        Require = {M}.{g},
        Fixer   = MarzGuns.RepairPack; Aiming=3,
    }}
""" for g in GROZAS) + "}\n")
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(path))
    for gun, g in GROZAS.items():
        names[f'{M}.{gun}'] = g['name']      # GoM's "AS VAL Assault Rifle"; "Prototype" as the UCP's (user)
    names.pop(f'{M}.GROZA_Suppressor', None)          # detachable until 2026-11-12
    names[f'{M}.GROZA4_Integrated_Suppressor'] = 'Groza-4 Integrated Suppressor'
    names[f'{M}.GROZAGL_GP25'] = 'GP-25 Grenade Launcher'                     # GoM: "M203 Grenade Launcher"
    names[f'{M}.GROZAGL_GP25_Integrated'] = 'GP-25 Integrated Grenade Launcher'
    for n in (10, 20, 30):
        names[f'{M}.9x39Magazine{n}_Hand'] = f'AS VAL {n}Rds 9x39mm Magazine'
    write('lua/shared/Translate/EN/ItemName.json', json.dumps(names, indent=2, ensure_ascii=False) + '\n')


def translations():
    path = os.path.join(ROOT, 'lua/shared/Translate/EN/ItemName.json')
    names = json.load(open(path)) if os.path.exists(path) else {}
    # GoM's naming: model and class, no maker ("MP5 Submachine Gun", "MP5 Integrated Stock (Folded)").
    names.update({
        f'{M}.MP7A1': 'MP7A1 Submachine Gun',                 # the variant named since the A2 (user, 2026-10-18)
        f'{M}.MP7A2': 'MP7A2 Submachine Gun',
        f'{M}.MP7A2_Integrated_Rail_Down': 'MP7 Integrated Rail (Down)',
        # the TR, since the main mod's P90 with the ring sight took the plain name (user, 2026-11-03)
        f'{M}.P90TR': 'P90 TR Submachine Gun',
        f'{M}.46x30Magazine20_MP7': 'MP7 20Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine30_MP7': 'MP7 30Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine40_MP7': 'MP7 40Rds 4.6x30mm Magazine',
        f'{M}.46x30Magazine60_MP7': 'MP7 60Rds Drum 4.6x30mm Magazine',
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
        f'{M}.P90TR_Integrated_Rail_Up': 'P90 TR Integrated Rail (Up)',
        f'{M}.P90TR_Integrated_Rail_Left': 'P90 TR Integrated Rail (Left)',
        f'{M}.P90TR_Integrated_Rail_Right': 'P90 TR Integrated Rail (Right)',
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
        # generic since the Mk 11 Mod 0 takes it too (user, 2026-11-12), as the 4.6x30mm / 5.7x28mm mount devices
        f'{M}.SCARH_Muzzle_Mount_Device': '7.62x51mm Family Muzzle Mounting Device',
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
        # the main mod's "Steyr AUG A1 Assault Rifle" and "AUG 30Rds 5.56x45mm Magazine"; the HBAR's 50 is long, as
        # GoM's "Extended" magazines
        f'{M}.AUGA3': 'Steyr AUG A3 Assault Rifle',
        f'{M}.AUGPARA': 'Steyr AUG Para Submachine Gun',
        f'{M}.AUGHBAR': 'Steyr AUG HBAR Light Machine Gun',
        f'{M}.9x19Magazine25_AUG': 'AUG Para 25Rds 9x19mm Magazine',
        f'{M}.9x19Magazine32_AUG': 'AUG Para 32Rds 9x19mm Magazine',
        f'{M}.762x39Magazine30_AUG': 'AUG 30Rds 7.62x39mm Magazine',
        f'{M}.762x39Magazine50_AUG': 'AUG 50Rds 7.62x39mm Extended Magazine',
        f'{M}.AUG_Integrated_Rail_Up': 'AUG Integrated Rail (Up)',
        f'{M}.AUG_Integrated_Rail_Right': 'AUG Integrated Rail (Right)',
        f'{M}.AUGHBAR_Integrated_Bipod_Folded': 'AUG HBAR Integrated Bipod (Folded)',
        f'{M}.AUGHBAR_Integrated_Bipod_Deployed': 'AUG HBAR Integrated Bipod (Deployed)',
        # GoM: "Glock-17 17Rds 9x19mm Magazine"; the main mod's "Glock-21 13Rds .45 ACP Magazine"
        # no maker in the name (user, 2026-11-01), as GoM's "MP5 Submachine Gun"
        f'{M}.VECTOR45': 'Vector .45 Submachine Gun',
        f'{M}.VECTOR9': 'Vector 9mm Submachine Gun',
        # KRISS's 16" Vector CRB; GoM names carbines "<model> Carbine" (SKS Carbine, Camp Carbine), as the PS90
        f'{M}.VECTORCRB': 'Vector .45 Carbine',
        # KRISS's stockless SDP, a pistol (as the CRB is the carbine)
        f'{M}.VECTORSDP': 'Vector 9mm Pistol',
        # GoM's own name for the Five-seveN is "5.7x28mm Five-SeveN": the calibre dropped (user, 2026-11-01), GoM's
        # spelling kept as our magazines have it. Translations merge by key in mod order, so ours wins.
        'MarzGuns.FIVESEVEN': 'Five-SeveN',
        f'{M}.45Magazine30_GLOCK21': 'Glock-21 30Rds .45 ACP Extended Magazine',
        f'{M}.9x19Magazine33_GLOCK': 'Glock-17 33Rds 9x19mm Extended Magazine',
        f'{M}.9x19Magazine40_GLOCK': 'Glock-17 40Rds 9x19mm Extended Magazine',
        f'{M}.VECTOR_Integrated_Stock_Folded': 'Vector Integrated Stock (Folded)',
        f'{M}.VECTOR_Integrated_Stock_Deployed': 'Vector Integrated Stock (Deployed)',
        f'{M}.VECTOR_Integrated_Rail_Up': 'Vector Integrated Rail (Up)',
        f'{M}.VECTOR_Integrated_Rail_Down': 'Vector Integrated Rail (Down)',
        # the TR is "P90 Submachine Gun"; GoM names carbines "<model> Carbine" (its SKS Carbine); the PS90 is
        # FN's 16" carbine, whose handguard this one is made for (user, 2026-11-03: "call it PS90")
        f'{M}.PS90': 'PS90 Carbine',
        f'{M}.PS90_Integrated_Rail_Up': 'PS90 Integrated Rail (Up)',
        f'{M}.PS90_Integrated_Rail_Down': 'PS90 Integrated Rail (Down)',
        f'{M}.PS90_Integrated_Rail_Left': 'PS90 Integrated Rail (Left)',
        f'{M}.PS90_Integrated_Rail_Right': 'PS90 Integrated Rail (Right)',
        # GoM: "Mini-14 Semi-Automatic Rifle", "PSG-1 Semi-Automatic Rifle"; Desert Tech's model name and calibre
        # (user, 2026-11-04: "MDR .223 and MDR .308"; the MDRx, the shell these are modelled on)
        f'{M}.MDR223': 'MDRx .223 Semi-Automatic Rifle',
        f'{M}.MDR308': 'MDRx .308 Semi-Automatic Rifle',
        # the SR-25-pattern magazines named like GoM's STANAGs ("STANAG 30Rds 5.56x45mm Magazine"; user, 2026-11-04:
        # "something like PMAG 20 ROUND"), the drum as the MP7's and SCAR-H's
        f'{M}.762x51Magazine10_PMAG': 'PMAG 10Rds 7.62x51mm Magazine',
        f'{M}.762x51Magazine20_PMAG': 'PMAG 20Rds 7.62x51mm Magazine',
        f'{M}.762x51Magazine25_PMAG': 'PMAG 25Rds 7.62x51mm Magazine',
        f'{M}.762x51Magazine50_PMAG': 'PMAG 50Rds Drum 7.62x51mm Magazine',
        f'{M}.MDR_Integrated_Rail_Up': 'MDRx Integrated Rail (Up)',
        f'{M}.MDR_Integrated_Rail_Down': 'MDRx Integrated Rail (Down)',
        f'{M}.MDR308_Integrated_Bipod_Folded': 'MDRx .308 ALX Bipod (Folded)',
        f'{M}.MDR308_Integrated_Bipod_Deployed': 'MDRx .308 ALX Bipod (Deployed)',
    })
    for moved in ('57x28Magazine50_P90',):    # the main mod's now
        names.pop(f'{M}.{moved}', None)
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
    augs()
    vectors()
    ps90()
    mdrs()
    mk11()
    grozas()
    translations()
    print('written under', os.path.normpath(ROOT))
