"""Rarity audit of every gun (user, 2026-11-21: "audit each gun spawns and if they're considered still rare, expose them
more under the extend option").

Runs vanilla's loot tables, GoM's ItemInsertion and both mods' loot code in a real Lua (lupa, audit.lua), Extend Loot
Areas off and on, in the game's event order (merge, OnInitGlobalModData, OnLoadMapZones), then scores each gun:
- containers: the sum over every list of rolls x weight x the gun's share of the entry (ItemPickerJava rolls every
  item of a list on its own each roll, its chance growing with its weight; a spawner picks an alternative evenly,
  then a gun of its list evenly; a vanilla gun stands for GoM's replacements of it),
- zombies: the sum over outfits of the chance one carries it (a port of AttachedWeaponDefinitions.addRandomAttachedWeapon,
  presets' 6% Chance of Attached Weapon, day 0),
and prints the spawner weight factors that lift every gun to the median container score (ExtendLootAreas.lua
RARE_WEIGHTS; with the option on the dump already has them applied, so a rerun after a loot change should be made
with RARE_WEIGHTS emptied first).

    py scripts/loot/audit.py <lupa dir> <out dir>
"""
import collections
import glob
import os
import random
import re
import sys
GOMS = r"C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media/scripts"
ROOT = r"C:/Users/Chen/Zomboid/Workshop/GoMExtensionGunsOfTien/Contents/mods"
guns = set()
for f in glob.glob(GOMS + "/**/*.txt", recursive=True) + glob.glob(ROOT + "/*/42/media/scripts/**/*.txt", recursive=True):
    t = open(f, encoding='utf-8', errors='replace').read()
    m = re.search(r'module\s+(\w+)', t)
    if not m: continue
    for im in re.finditer(r'\n\s*item\s+(\w+)\s*\{(.*?)\n\s*\}', t, re.S):
        if re.search(r'SubCategory\s*=\s*Firearm', im.group(2)): guns.add(m.group(1) + '.' + im.group(1))
skip = {'GunsOfTien.UZI_2H', 'GunsOfTienPost93.GROZAGL_GP25', 'MarzGuns.CAR15_M203_Weapon', 'MarzGuns.M203_Weapon'}
guns -= skip

def load(f):
    sp = collections.defaultdict(lambda: collections.defaultdict(float)); rp = collections.defaultdict(lambda: collections.defaultdict(float))
    pl = []; sd = {}; sw = collections.defaultdict(list); co = {}
    for line in open(f, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if p[0] == 'SP': sp[p[1]][p[5]] += 1.0 / int(p[2]) / int(p[4])
        elif p[0] == 'RP': rp[p[1]][p[5]] += 1.0 / int(p[2]) / int(p[4])
        elif p[0] == 'PL':
            try: pl.append((p[1], p[2], float(p[3]), p[4], float(p[5])))
            except ValueError: pass
        elif p[0] == 'SD': sd[p[1]] = (int(float(p[2])), int(float(p[3])), [o for o in p[4].split(',') if o])
        elif p[0] == 'SW': sw[p[1]].append(p[2])
        elif p[0] == 'CO': co[p[1]] = (int(float(p[2])), int(float(p[3])), [s for s in p[4].split(',') if s])
    return sp, rp, pl, sd, sw, co

def p_entry(entry, sp, rp):
    """gun -> probability for one item entry (spawner, vanilla gun replaced by GoM, or a gun)"""
    if entry in sp: return sp[entry]
    e = entry if '.' in entry else 'Base.' + entry
    if e in rp: return rp[e]
    if e in guns: return {e: 1.0}
    return {}

def containers(sp, rp, pl):
    score = collections.defaultdict(float); where = collections.defaultdict(lambda: collections.defaultdict(float))
    for prefix, lst, rolls, item, w in pl:
        for g, p in p_entry(item, sp, rp).items():
            v = rolls * w * p
            score[g] += v; where[g][lst] += v
    return score, where

def zombies(sp, rp, sd, sw, co, cow=6, n=6000):
    slotgun = {}
    for s, ws in sw.items():
        d = collections.defaultdict(float)
        for w in ws:
            for g, p in p_entry(w, sp, rp).items(): d[g] += p / len(ws)
        slotgun[s] = d
    outfits = sorted({o for v in sd.values() for o in v[2]} | set(co))
    res = collections.defaultdict(dict)
    def applicable(slots, o):
        r = []
        for s in slots:
            if s not in sd: continue
            ch, ds, outs = sd[s]
            if ds > 0: r.append(s)          # day 0 here: skip daySurvived ones
            elif outs:
                if o in outs: r.append(s)
            else: r.append(s)
        return [s for s in r if sd[s][1] == 0]
    rnd = random.Random(1)
    for o in outfits:
        acc = collections.defaultdict(float)
        c = co.get(o)
        for _ in range(n):
            if c and rnd.randrange(100) < c[0]:
                pool = applicable(c[2], o); rep = c[1]; ch = c[0]
            else:
                if rnd.randrange(100) + 1 > cow: continue
                pool = applicable(list(sd), o); rep = 1; ch = None
            pool = list(pool); got = collections.defaultdict(float)
            while rep > 0 and pool:
                tot = sum(sd[s][0] for s in pool)
                if tot <= 0: break
                x = rnd.randrange(tot); a = 0
                for s in pool:
                    a += sd[s][0]
                    if x < a: pick = s; break
                pool.remove(pick); rep -= 1
                for g, p in slotgun.get(pick, {}).items(): got[g] = 1 - (1 - got[g]) * (1 - p)
                if ch is not None and rnd.randrange(100) >= ch: break
            for g, p in got.items(): acc[g] += p
        for g, v in acc.items(): res[g][o] = v / n
    return res


LUPA, OUT = sys.argv[1], os.path.abspath(sys.argv[2])
sys.path.insert(0, LUPA)
import lupa  # noqa: E402
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
for flag in (False, True):
    lupa.LuaRuntime().execute("return loadfile([[%s]])" % os.path.join(HERE, "audit.lua"))(
        flag, os.path.join(OUT, "audit_%s.tsv" % flag))

res = {}
for flag in (False, True):
    sp, rp, pl, sd, sw, co = load(os.path.join(OUT, "audit_%s.tsv" % flag))
    contrib = collections.defaultdict(lambda: collections.defaultdict(float))
    for prefix, lst, rolls, item, w in pl:
        key = item if item in sp else ("Base." + item if "." not in item else item)
        for g, p in p_entry(item, sp, rp).items():
            contrib[g][key] += rolls * w * p
    z = zombies(sp, rp, sd, sw, co)
    res[flag] = (sp, contrib, {g: sum(z.get(g, {}).values()) for g in guns})
allg = sorted(guns)
cont = {f: {g: sum(res[f][1][g].values()) for g in allg} for f in res}
print("%-34s %9s %9s %9s %9s" % ("gun", "cont off", "cont on", "zomb off", "zomb on"))
for g in sorted(allg, key=lambda g: cont[True][g]):
    print("%-34s %9.1f %9.1f %8.2f%% %8.2f%%" % (g, cont[False][g], cont[True][g], res[False][2][g] * 100,
                                                  res[True][2][g] * 100))
sp, contrib, _ = res[True]
M = sorted(cont[True].values())[len(allg) // 2]
factor = collections.defaultdict(lambda: 1.0)
for _ in range(30):
    cur = {g: sum(v * (factor[s] if s in sp else 1) for s, v in contrib[g].items()) for g in allg}
    need = {}
    for g in allg:
        if cur[g] >= M * 0.999:
            continue
        srcs = [(v * factor[s], s) for s, v in contrib[g].items() if s in sp]
        if srcs:
            v, s = max(srcs)
            need[s] = max(need.get(s, 1), min(4.0, factor[s] * (1 + (M - cur[g]) / v)))
    changed = [s for s, f in need.items() if f > factor[s] + 1e-6]
    for s in changed:
        factor[s] = need[s]
    if not changed:
        break
print("median container score (option on): %.1f; factors lifting every gun to it (cap 4):" % M)
for s, f in sorted(factor.items(), key=lambda x: -x[1]):
    if f > 1.001:
        print('    ["%s"] = %.1f,' % (s, f + 0.049))
