import re, collections, sys, json
S = sys.argv[1]
GOMI = r"C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media/lua/server/MarzWeapons/Distribution/ItemInsertion.lua"
def read(f):
    sp = collections.defaultdict(list); slot = collections.defaultdict(set); pl = collections.defaultdict(dict); slotout = {}
    for line in open(f, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if p[0] == 'SP' and p[2] not in sp[p[1]]: sp[p[1]].append(p[2])
        elif p[0] == 'SL': slot[p[2]].add(p[1]); slotout[p[1]] = p[3]
        elif p[0] == 'PL': pl[p[2]][p[1]] = p[3]
    return sp, slot, pl, slotout
off = read(S + '/dump_False.tsv'); on = read(S + '/dump_True.tsv')
gi = open(GOMI, encoding='utf-8').read()
gompl = collections.defaultdict(dict)
for m in re.finditer(r'add(Item|Mag)\("(\w+)",\s*"([\w.]+)",\s*([\d.]+)', gi): gompl[m.group(3)][m.group(2)] = m.group(4)
out = {}
for s in sorted(set(on[0]) | set(off[0])):
    if not re.search(r'(Spawner)$', s) or re.search(r'Magazine|Optic|Muzzle|Suppressor|Foregrip|Light|Bayonet|Attachment|Ordnance', s): continue
    gb = off[0].get(s, []); ge = on[0].get(s, [])
    places_off = dict(gompl.get(s, {})); places_off.update(off[2].get(s, {}))
    places_on = dict(places_off); places_on.update(on[2].get(s, {}))
    out[s] = dict(guns=gb, ext_guns=[g for g in ge if g not in gb], places=sorted(places_off), ext_places=sorted(set(places_on) - set(places_off)),
                  slots=sorted(off[1].get(s, ())), ext_slots=sorted(set(on[1].get(s, ())) - set(off[1].get(s, ()))))
json.dump(out, open(S + '/spawners.json', 'w'), indent=1)
for s, d in out.items():
    print(s.replace('MarzGuns.', ''), len(d['guns']), '+', len(d['ext_guns']))
    print('   guns:', ' '.join(g.split('.')[1] for g in d['guns']), '| ext:', ' '.join(g.split('.')[1] for g in d['ext_guns']))
    print('   places:', ', '.join(d['places']), '| ext:', ', '.join(d['ext_places']))
    print('   slots:', ', '.join(d['slots']), '| ext:', ', '.join(d['ext_slots']))
