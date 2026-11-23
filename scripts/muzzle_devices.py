"""The real muzzle devices both mods add, one table for every tool that needs it (user, 2026-11-23: "Option A", real
devices built from scratch; "Real fit only"; built-in devices on the guns stay cosmetic, as GoM's AR-15 birdcage).

Read by gen_scripts.py (the main mod's items, models, names, our guns' model lines and the generated
lua/shared/GunsOfTien/MuzzleDevicesTable.lua that MuzzleFamilies.lua and Tooltips.lua read), post93/gen_post93_guns.py
(the SureFire items and Post-93's guns' lines), build_muzzle_devices.py (meshes, textures) and
make_muzzle_device_art.py (icons).

Stats are GoM's for its three AR devices by kind: flash hider (LX) and muzzle brake (Trix42) sound and volume x0.95,
compensator (LR2) x0.90, all remove the muzzle flash; weights LX 0.9, LR2 1.0, Trix42 1.2. Each needs its family's
mount device first (GoM's rule). `guns` is the real fit, by thread or lug pattern (research 2026-11-23, sources in
CLAUDE.md "Real muzzle devices"): an item type in another mod is only a string until that mod is loaded.
`scale` = game units per real mm, the proportion of the guns that wear it (GoM's AKs ~0.64, its pistols ~0.70-0.72,
its Thompson 0.66, our guns and the MP5s on our models 0.603).
"""

KINDS = {                      # kind: (weight, sound and volume multiplier, tooltip effect line)
    'hider': (0.9, 0.95, "Sound Radius and Volume reduced by 5%"),
    'brake': (1.2, 0.95, "Sound Radius and Volume reduced by 5%"),
    'comp': (1.0, 0.90, "Sound Radius and Volume reduced by 10%"),
}
MODULES = {'main': 'GunsOfTien', 'post93': 'GunsOfTienPost93'}

AK_MOUNT = 'MarzGuns.AK_Muzzle_Mount_Device'
NINE_MOUNT = 'MarzGuns.Pistol_Muzzle_Mount_Device'
OLD_NINE_MOUNT = 'GunsOfTien.SMG9_Muzzle_Mount_Device'
ACP45_MOUNT = 'MarzGuns.45_Muzzle_Mount_Device'
NATO762_MOUNT = 'GunsOfTienPost93.SCARH_Muzzle_Mount_Device'

AK762 = ['MarzGuns.AK47', 'GunsOfTien.RPK', 'MarzGuns.SKS', 'GunsOfTienPost93.GROZA1', 'GunsOfTienPost93.GROZAGL']
AK545 = ['MarzGuns.AK74', 'MarzGuns.AKS74U', 'GunsOfTien.RPK74', 'GunsOfTienPost93.GROZA2']
NATO762_THREADED = ['GunsOfTien.SR25', 'GunsOfTienPost93.SCARH', 'GunsOfTienPost93.HK417', 'GunsOfTienPost93.HK417S',
                    'GunsOfTienPost93.MK11', 'GunsOfTienPost93.MDR308', 'MarzGuns.G3', 'MarzGuns.M24', 'MarzGuns.PSG1',
                    'MarzGuns.REMINGTON_700']

DEVICES = [
    # 7.62x39 AKs: M14x1 LH (the SKS through its threading kit, as for the PBS-1)
    dict(node='AKM_Slant_Compensator', mod='main', kind='comp', name='AKM Slant Compensator (7.62x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK762, fits='AK-47, RPK, SKS, Groza-1', scale=0.00064),
    # 5.45 AKs: M24x1.5 RH
    dict(node='AK74_Muzzle_Brake', mod='main', kind='brake', name='AK-74 Muzzle Brake (5.45x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK545, fits='AK-74, AKS-74U, RPK-74, Groza-2', scale=0.00064),
    dict(node='AKS74U_Muzzle_Booster', mod='main', kind='hider', name='AKS-74U Muzzle Booster (5.45x39mm AKs)',
         mounts=[AK_MOUNT], family='AK', guns=AK545, fits='AK-74, AKS-74U, RPK-74, Groza-2', scale=0.00064),
    # H&K's three lugs: the MP5 and MP5A2 only (the MP5K's barrel ends flush)
    dict(node='MP5_Flash_Hider', mod='main', kind='hider', name='H&K Three-Lug Flash Hider (MP5s)',
         mounts=[NINE_MOUNT, OLD_NINE_MOUNT], family='9x19mm', guns=['MarzGuns.MP5', 'MarzGuns.MP5A2'],
         fits='MP5A3, MP5A2', scale=0.000603),
    # IPSC race compensators on a custom threaded barrel (Clark Custom, 1980s): the 9mm pistols such guns were built
    # on by 1993, and the 1911
    dict(node='Clark_Compensator_9mm', mod='main', kind='comp', name='Clark Compensator (9mm Pistols)',
         mounts=[NINE_MOUNT, OLD_NINE_MOUNT], family='9x19mm',
         guns=['MarzGuns.M92FS', 'MarzGuns.HIPOWER', 'MarzGuns.P226'], fits='Beretta 92FS, Hi-Power, P226',
         scale=0.00072),
    dict(node='Cutts_Compensator', mod='main', kind='comp', name='Cutts Compensator (Thompson)',
         mounts=[ACP45_MOUNT], family='.45', guns=['MarzGuns.THOMPSON'], fits='Thompson', scale=0.00066),
    dict(node='Clark_Compensator_45', mod='main', kind='comp', name='Clark Compensator (.45 Pistols)',
         mounts=[ACP45_MOUNT], family='.45', guns=['MarzGuns.M1911'], fits='M1911', scale=0.00070),
    # SureFire's suppressor mounts (Post-93): 5/8-24, SR25 and M15x1 versions; FAL and M14 versions of the SF3P only
    dict(node='SF3P_Flash_Hider', mod='post93', kind='hider', name='SF3P Flash Hider (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED + ['MarzGuns.FAL', 'MarzGuns.M14'],
         fits='7.62x51mm rifles', scale=0.000603),
    dict(node='SFMB_Muzzle_Brake', mod='post93', kind='brake', name='SFMB Muzzle Brake (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED,
         fits='7.62x51mm rifles except the FAL and M14', scale=0.000603),
    dict(node='WarComp_Flash_Hider', mod='post93', kind='comp', name='WarComp Flash Hider (7.62x51mm Weapons)',
         mounts=[NATO762_MOUNT], family='7.62x51mm', guns=NATO762_THREADED,
         fits='7.62x51mm rifles except the FAL and M14', scale=0.000603),
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
    Tooltips.lua need."""
    out = ["-- Generated by scripts/gen_scripts.py from scripts/muzzle_devices.py: do not edit.\n",
           "return {\n"]
    for d in DEVICES:
        _, sound, effect = KINDS[d['kind']]
        guns = ", ".join(f'"{g}"' for g in d['guns'])
        mounts = ", ".join(f'"{m}"' for m in d['mounts'])
        out.append(f'    ["{full_type(d)}"] = {{ sound = {sound:.2f}, family = "{d["family"]}", '
                   f'effect = "{effect}", fits = "{d["fits"]}",\n'
                   f'        mounts = {{ {mounts} }},\n        guns = {{ {guns} }} }},\n')
    out.append("}\n")
    return ''.join(out)
