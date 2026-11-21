"""Rebuild the loot dump the Workshop previews 33-37 read (scripts/make_loot_previews.py).

Runs both mods' Loot.lua and the main mod's ExtendLootAreas.lua in a real Lua (lupa) over GoM's own tables, once with
Extend Loot Areas off and once on (dump.lua), then writes spawners.json and replacements.json next to the dumps
(spawner_data.py and the replacement step below).

    py -m pip install --target <dir>/lupa lupa
    py scripts/loot/build.py <lupa dir> <out dir>
    py scripts/make_loot_previews.py <out dir>/spawners.json
"""
import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
lupa_dir, out = sys.argv[1], os.path.abspath(sys.argv[2])
sys.path.insert(0, lupa_dir)
import lupa  # noqa: E402

os.makedirs(out, exist_ok=True)
for flag in (False, True):
    lupa.LuaRuntime().execute("return loadfile([[%s]])" % os.path.join(HERE, "dump.lua"))(
        flag, os.path.join(out, "dump_%s.tsv" % flag))
subprocess.check_call([sys.executable, os.path.join(HERE, "spawner_data.py"), out], stdout=subprocess.DEVNULL)


def replacements(path):
    m = collections.defaultdict(list)
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if p[0] == "RP" and p[2] not in m[p[1]]:
            m[p[1]].append(p[2])
    return m


off, on = replacements(os.path.join(out, "dump_False.tsv")), replacements(os.path.join(out, "dump_True.tsv"))
ext = {k: [g for g in v if g not in off.get(k, [])] for k, v in on.items()}
json.dump({"base": off, "ext": ext}, open(os.path.join(out, "replacements.json"), "w"), indent=1)
print("wrote", out)
