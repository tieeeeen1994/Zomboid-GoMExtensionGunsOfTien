"""Guns of Marz's data as GoM ships it now, read at build time (no hard-coded copies of it).

Sight windows (`sight`): GoM's November 2026 update gave every class of gun its own optimal range (MinSightRange /
MaxSightRange: shotguns 2-7, pistols 2-8, revolvers 2-9, SMGs 3-11 (short 2-10), carbines 5-14 (short 4-13), assault
rifles 7-17, battle rifles and LMGs 9-20, marksman rifles 11-23, bolt-action rifles 13-27). Each of our guns takes the
window of its closest GoM gun (GOM_EQUIVALENT in gen_scripts.py / post93/gen_post93_guns.py), read from that gun's
script, so a later GoM change follows on the next run.

Magazines:

gen_scripts.py (stanag_got, m249) and post93/gen_post93_guns.py (SCAR-L, MDRx .223, HK416) draw GoM's STANAG magazines
on our guns. GoM's November 2026 update renamed what its STANAG items are drawn with (the 50 is a 60-round extended
STANAG, the 75 a 60-round PMAG drum, the 150 a 100-round C-Mag, the 60 a jungle-taped pair of 30s with a second side
item `556x45Magazine60_STANAG_2`) and dropped the old model blocks, so every list here comes from GoM's own files:
- the items: GoM's Gunworks magazine profile "STANAG" (Registries/Magazines.lua), in its order;
- what each is drawn with: the item script's StaticModel (the model GoM's own guns name in their ModelWeaponPart
  line for that item);
- that model's mesh, texture and Bip01_Prop2 point (models/ammunition/*.txt);
- the item's Icon and English name.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_refs  # noqa: E402

GOM = [r for r in check_refs.OTHERS if '3722134990' in r.replace(os.sep, '/')]


def _profile(name):
    for root in GOM:
        p = os.path.join(root, 'lua/shared/MarzWeapons/Registries/Magazines.lua')
        if not os.path.isfile(p):
            continue
        text = open(p, encoding='utf-8').read()
        m = re.search(r'\["%s"\]\s*=\s*\{(.*?)\}' % re.escape(name), text, re.S)
        if m:
            return re.findall(r'"MarzGuns\.([^"]+)"', m.group(1))
    raise SystemExit(f"Guns of Marz's magazine profile {name!r} not found")


def _attachment(lines, name):
    """{offset, rotate} of attachment `name` in a model block's lines (one per line or written inline)."""
    text = ' '.join(lines)
    m = re.search(r'attachment\s+%s\s*\{(.*?)\}' % re.escape(name), text)
    if not m:
        return None
    body = m.group(1)
    off = re.search(r'offset\s*=\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', body)
    rot = re.search(r'rotate\s*=\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', body)
    return {'offset': [float(v) for v in off.groups()], 'rotate': [float(v) for v in rot.groups()]}


_SCRIPTS = None


def _scripts():
    """({item: kv}, {model: kv}) of GoM's scripts, parsed once."""
    global _SCRIPTS
    if _SCRIPTS is None:
        if not GOM:
            raise SystemExit('Guns of Marz not found')
        items, models = {}, {}
        for root in GOM:
            for kind, name, kv, _ in check_refs.parse_scripts(root):
                if kind == 'item':
                    items[name] = kv
                elif kind == 'model':
                    models[name] = kv
        _SCRIPTS = (items, models)
    return _SCRIPTS


def model(name):
    """{mesh, texture} of GoM's model `name` (e.g. 'MP5K')."""
    kv = _scripts()[1][f'MarzGuns.{name}']
    return {'mesh': kv['mesh'][-1], 'texture': kv['texture'][-1]}


def sight(gun):
    """(MinSightRange, MaxSightRange) of GoM's gun `gun` (e.g. 'MP5'), as our scripts write them: 3, 11.0."""
    kv = _scripts()[0][f'MarzGuns.{gun}']
    return int(float(kv['minsightrange'][-1])), float(kv['maxsightrange'][-1])


def stanags():
    """[{item, model, mesh, texture, prop2, icon, name}] for every magazine of GoM's "STANAG" profile, in its order."""
    items, models = _scripts()
    names = {}
    for root in GOM:
        p = os.path.join(root, 'lua/shared/Translate/EN/ItemName.json')
        if os.path.isfile(p):
            names.update(json.load(open(p, encoding='utf-8')))
    out = []
    for item in _profile('STANAG'):
        kv = items[f'MarzGuns.{item}']
        model = kv['staticmodel'][-1].split('.')[-1]
        mkv = models[f'MarzGuns.{model}']
        out.append({'item': item, 'model': model, 'mesh': mkv['mesh'][-1], 'texture': mkv['texture'][-1],
                    'prop2': _attachment(mkv.get('_lines', []), 'Bip01_Prop2'), 'icon': kv['icon'][-1],
                    'name': names[f'MarzGuns.{item}']})
    return out


if __name__ == '__main__':
    for s in stanags():
        print(s)
