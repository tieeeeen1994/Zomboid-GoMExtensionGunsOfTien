"""The real muzzle devices both mods add, one table for every tool that needs it (user, 2026-11-23: "Option A", real
devices built from scratch; "Real fit only"; built-in devices on the guns stay cosmetic, as GoM's AR-15 birdcage).

Read by gen_scripts.py (the main mod's items, models, names, our guns' model lines and the generated
lua/shared/GunsOfTien/MuzzleDevicesTable.lua that MuzzleFamilies.lua and Tooltips.lua read), post93/gen_post93_guns.py
(the SureFire items and Post-93's guns' lines), build_muzzle_devices.py (meshes, textures) and
make_muzzle_device_art.py (icons).

Stats are GoM's for its three AR devices by kind, flat since its November 2026 update (AttachmentCustomStats.lua):
flash hider (LX) and muzzle brake (Trix42) Sound Radius -10 and Volume -2, compensator (LR2) -15 and -4, all remove
the muzzle flash; weights LX 0.9, LR2 1.0, Trix42 1.2. Each needs its family's
mount device first (GoM's rule). `guns` is the real fit, by thread or lug pattern (research 2026-11-23, sources in
CLAUDE.md "Real muzzle devices"): an item type in another mod is only a string until that mod is loaded.
`scale` = game units per real mm, the proportion of the guns that wear it (GoM's AKs ~0.64, its pistols ~0.70-0.72,
its Thompson 0.66, our guns 0.603; the MP5 flash hider was built at 0.603 for our MP5 models of before 2026-11-23,
and is drawn on GoM's own MP5s, 0.779 of their old size, through a scaled model: gen_scripts.py MP5_PART_SCALE).
"""

KINDS = {                      # kind: (weight, Sound Radius change, Sound Volume change, tooltip effect line: GoM's)
    'hider': (0.9, -10, -2, "Sound Radius reduced by 10 and Volume by 2"),
    'brake': (1.2, -10, -2, "Sound Radius reduced by 10 and Volume by 2"),
    'comp': (1.0, -15, -4, "Sound Radius reduced by 15 and Volume by 4"),
}
# What each kind does beyond GoM's sound cut and flash removal (user, 2026-11-24: "can we also buff these? Like they
# provide other stats bonuses?", the real roles, on GoM's three AR devices too). Each kind does its real job, and each
# bonus is sized like GoM's other parts so it shows (lasers Aiming Time -2 / -3, Hit +1-3%; foregrips -9 / -10,
# automatic fire spread x0.85-0.9): a compensator holds the muzzle down (spread x0.9, Aiming Time -3), a brake takes
# the kick (Aiming Time -5, spread x0.95), a flash hider keeps the flash out of the shooter's eyes (Hit Chance +2%).
# Aiming Time is the aim-in time after raising the gun (resetAimingDelay) and 5% of it is added to the aiming delay
# after every shot (CombatManager.setAimingDelay), so it is what "less recoil" can move here. Not Recoil Delay
# (traced 2026-11-24): Gunworks' RateOfFire layer sets it to 1 on every registered gun in its Real fire modes (every
# GoM gun and ours), and HandWeapon.getRecoilDelay(owner) scales it by Aiming skill and cuts it to an int, so it is
# already 0 for anyone with Aiming 1 or more: nothing left to take off. Spread acts on automatic fire only (Gunworks'
# RegisterSpreadPartModifier, guns whose rate-of-fire profile has spread). Written into
# lua/shared/GunsOfTien/MuzzleDeviceKinds.lua: MuzzleFamilies.lua applies it, Tooltips.lua shows `lines` (GoM's wording).
BONUS = {
    'comp': dict(aim=-3, spread=0.9, lines=["Aiming Time reduced by 3", "Automatic fire spread reduced by 10%"]),
    'brake': dict(aim=-5, spread=0.95, lines=["Aiming Time reduced by 5", "Automatic fire spread reduced by 5%"]),
    'hider': dict(hit=2, lines=["Hit Chance increased by 2%"]),
}
GOM_KINDS = {'MarzGuns.LR2_Compensator': 'comp', 'MarzGuns.LX_Flashhider': 'hider',
             'MarzGuns.Trix42_Muzzlebreak': 'brake'}
MODULES = {'main': 'GunsOfTien', 'post93': 'GunsOfTienPost93'}

AK_MOUNT = 'MarzGuns.AK_Muzzle_Mount_Device'
NINE_MOUNT = 'MarzGuns.Pistol_Muzzle_Mount_Device'
OLD_NINE_MOUNT = 'GunsOfTien.SMG9_Muzzle_Mount_Device'
ACP45_MOUNT = 'MarzGuns.45_Muzzle_Mount_Device'
NATO762_MOUNT = 'GunsOfTienPost93.SCARH_Muzzle_Mount_Device'

AK762 = ['MarzGuns.AK47', 'GunsOfTien.RPK', 'MarzGuns.SKS', 'GunsOfTienPost93.GROZA1', 'GunsOfTienPost93.GROZAGL',
         'GunsOfTienPost93.A91M']
AK545 = ['MarzGuns.AK74', 'MarzGuns.AKS74U', 'GunsOfTien.RPK74', 'GunsOfTienPost93.GROZA2']
NATO762_THREADED = ['GunsOfTien.SR25', 'GunsOfTienPost93.SCARH', 'GunsOfTienPost93.HK417', 'GunsOfTienPost93.HK417S',
                    'GunsOfTienPost93.MK11', 'GunsOfTienPost93.MDR308', 'MarzGuns.G3', 'MarzGuns.M24', 'MarzGuns.PSG1',
                    'MarzGuns.REMINGTON_700']

DEVICES = [
    # 7.62x39 AKs: M14x1 LH (the SKS through its threading kit, as for the PBS-1)
    dict(node='AKM_Slant_Compensator', mod='main', kind='comp', name='AKM Slant Compensator (7.62x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK762, scale=0.00064),
    # 5.45 AKs: M24x1.5 RH
    dict(node='AK74_Muzzle_Brake', mod='main', kind='brake', name='AK-74 Muzzle Brake (5.45x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK545, scale=0.00064),
    dict(node='AKS74U_Muzzle_Booster', mod='main', kind='hider', name='AKS-74U Muzzle Booster (5.45x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK545, scale=0.00064),
    # H&K's three lugs: the MP5 and MP5A2 only (the MP5K's barrel ends flush)
    dict(node='MP5_Flash_Hider', mod='main', kind='hider', name='Three-Lug Flash Hider (MP5s)',
         mounts=[NINE_MOUNT, OLD_NINE_MOUNT], family='9x19mm', guns=['MarzGuns.MP5', 'MarzGuns.MP5A2'], scale=0.000603,
         drawn=0.00072 * 0.779),  # GoM's MP5s since its November 2026 update (gen_scripts.py GOM_MP5_K)
    # IPSC race compensators on a custom threaded barrel (Clark Custom, 1980s): the 9mm pistols such guns were built
    # on by 1993, and the 1911
    dict(node='Clark_Compensator_9mm', mod='main', kind='comp', name='Clark Compensator (9mm Pistols)',
         mounts=[NINE_MOUNT, OLD_NINE_MOUNT], family='9x19mm',
         guns=['MarzGuns.M92FS', 'MarzGuns.HIPOWER', 'MarzGuns.P226'],
         scale=0.00072),
    dict(node='Cutts_Compensator', mod='main', kind='comp', name='Cutts Compensator (Thompson)',
         mounts=[ACP45_MOUNT], family='.45', guns=['MarzGuns.THOMPSON'], scale=0.00066),
    dict(node='Clark_Compensator_45', mod='main', kind='comp', name='Clark Compensator (.45 Pistols)',
         mounts=[ACP45_MOUNT], family='.45', guns=['MarzGuns.M1911'], scale=0.00070),
    # SureFire's suppressor mounts (Post-93): 5/8-24, SR25 and M15x1 versions; FAL and M14 versions of the SF3P only
    dict(node='SF3P_Flash_Hider', mod='post93', kind='hider', name='SF3P Flash Hider (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED + ['MarzGuns.FAL', 'MarzGuns.M14'], scale=0.000603),
    dict(node='SFMB_Muzzle_Brake', mod='post93', kind='brake', name='SFMB Muzzle Brake (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED, scale=0.000603),
    dict(node='WarComp_Flash_Hider', mod='post93', kind='comp', name='WarComp Flash Hider (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED, scale=0.000603),
]


def full_type(d):
    return MODULES[d['mod']] + '.' + d['node']


def of_mod(mod):
    return [d for d in DEVICES if d['mod'] == mod]


def model_lines(w, gun):
    """ModelWeaponPart lines of every device the gun takes, drawn with the device's own model at `canon`."""
    return [f"{w}{full_type(d)} {full_type(d)} canon canon," for d in DEVICES if gun in d['guns']]


def lua_table():
    """lua/shared/GunsOfTien/MuzzleDevicesTable.lua: what MuzzleFamilies.lua (stats, mounts, GoM's guns' lines) and
    Tooltips.lua need. The guns a device fits are not written out: GunLines.lua names them in its tooltip from its
    MountOn (`guns`)."""
    out = ["-- Generated by scripts/gen_scripts.py from scripts/muzzle_devices.py: do not edit.\n",
           "return {\n"]
    for d in DEVICES:
        _, radius, volume, effect = KINDS[d['kind']]
        guns = ", ".join(f'"{g}"' for g in d['guns'])
        mounts = ", ".join(f'"{m}"' for m in d['mounts'])
        out.append(f'    ["{full_type(d)}"] = {{ radius = {radius}, volume = {volume}, family = "{d["family"]}", '
                   f'kind = "{d["kind"]}", effect = "{effect}",\n'
                   f'        mounts = {{ {mounts} }},\n        guns = {{ {guns} }} }},\n')
    out.append("}\n")
    return ''.join(out)


def lua_kinds():
    """lua/shared/GunsOfTien/MuzzleDeviceKinds.lua: each kind's bonus (BONUS) and GoM's three devices' kinds."""
    out = ["-- Generated by scripts/gen_scripts.py from scripts/muzzle_devices.py: do not edit.\n",
           "return {\n"]
    for kind in ('comp', 'brake', 'hider'):
        b = BONUS[kind]
        fields = [f"{k} = {b[k]:g}" for k in ('aim', 'hit', 'spread') if k in b]
        lines = ", ".join(f'"{l}"' for l in b['lines'])
        out.append(f"    {kind} = {{ {', '.join(fields)}, lines = {{ {lines} }} }},\n")
    gom = ", ".join(f'["{t}"] = "{k}"' for t, k in GOM_KINDS.items())
    out.append(f"    gom = {{ {gom} }},\n")
    out.append("}\n")
    return ''.join(out)
