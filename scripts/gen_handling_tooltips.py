#!/usr/bin/env python3
"""Tooltips that say what Guns of Marz's stocks, bipods, selectors and parts really do.

    python3 scripts/gen_handling_tooltips.py

GoM's tooltip table (MarzWeapons/ItemTooltipsTable.lua) says only "Has Integrated Stock" / "Has Integrated Bipod" for
some guns and nothing for others that have one (MP5, MAC10, SPAS12...), nothing about the SPAS-12's pump / semi
selector, and its part lines leave out what Gunworks' spread modifiers (Registries/RPM.lua) and the item scripts'
own modifiers (the lights' AimingTimeModifier) do. This reads GoM's registries and scripts (Stocks.lua, Bipods.lua,
AttachmentCustomStats.lua with its DA.RegisterPair selector pairs, RPM.lua's RegisterSpreadPartModifier,
OnCreate/AttachAndDetach.lua's tools per part type, the item scripts for base stats and modifiers) and writes
Contents/mods/GoMExtensionGunsOfTien/42/media/lua/client/GunsOfTien/HandlingTooltips.lua:
- one line per gun with a folding stock, bipod or mode selector, in the style of GoM's part tooltips and the Post-93
  MP7s ("Collapsible stock: deployed, Aiming Time reduced by 25%, Hit Chance increased by 15%."), replacing GoM's
  vague line or added after the others;
- the lines a part's own tooltip is missing (spread, script modifiers, the tool to fit it), before its "Needs ..."
  line.
Run again after a GoM update; never hand-edit the output.
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media/lua/client/GunsOfTien/HandlingTooltips.lua")
MEDIA = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                            "3722134990/mods/GunsOfMarz/42.16/media"),
                         "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                         "42.16/media") if os.path.isdir(p))
GOM = os.path.join(MEDIA, "lua")
REG = os.path.join(GOM, "shared/MarzWeapons/Registries")

# How each gun's stock moves on the real gun: side- or top-folding, else telescoping ("collapsible").
FOLDING = {"MarzGuns.AKS74U", "MarzGuns.ASVAL", "MarzGuns.FNC", "MarzGuns.G36C", "MarzGuns.G36", "MarzGuns.SPAS12"}
VAGUE = {"stock": "Has Integrated Stock", "bipod": "Has Integrated Bipod"}
LABEL = {"AimingTime": "Aiming Time", "HitChance": "Hit Chance", "CriticalChance": "Critical Chance",
         "RecoilDelay": "Recoil Delay", "JamGunChance": "Jam Chance"}
# item script modifier -> the stat it changes (vanilla adds the part's value to the gun's)
SCRIPT_MODS = {"AimingTimeModifier": "Aiming Time", "HitChanceModifier": "Hit Chance"}


def read(path):
    return open(path, encoding="utf-8").read()


def label(stat):
    return LABEL.get(stat, re.sub(r"(?<!^)([A-Z])", r" \1", stat))


def registrations(text):
    """{gun: (folded part, deployed part)} from a RegisterMultipleWeapons block."""
    out = {}
    for m in re.finditer(r'\["([\w.]+)"\]\s*=\s*\{\s*attachments\s*=\s*\{(.*?)\}', text, re.S):
        body = m.group(2)
        folded = re.search(r'folded\s*=\s*"([\w.-]+)"', body).group(1)
        deployed = re.search(r'deployed\s*=\s*"([\w.-]+)"', body).group(1)
        out[m.group(1)] = (folded, deployed)
    return out


def part_stats(text):
    """{part: [(op, stat, value)]} from AttachmentCustomStats.lua (Multiply / Set / Adjust; comments ignored)."""
    out = {}
    for m in re.finditer(r'\["([\w.-]+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        body = re.sub(r"--[^\n]*", "", m.group(2))
        out[m.group(1)] = [(op, stat, value.strip()) for op, stat, value in
                           re.findall(r'SF\.(\w+)\("(\w+)",\s*([^)]+)\)', body)]
    return out


def spread_mods(text):
    """{part: (sustained, max)} from RPM.lua's RegisterSpreadPartModifier."""
    out = {}
    for part, body in re.findall(r'RegisterSpreadPartModifier\("([\w.-]+)",\s*\{([^}]*)\}', text):
        s = re.search(r'sustainedSpreadMult\s*=\s*([\d.]+)', body)
        m = re.search(r'maxSpreadMult\s*=\s*([\d.]+)', body)
        out[part] = (float(s.group(1)) if s else 1.0, float(m.group(1)) if m else 1.0)
    return out


def items():
    """{fullType: {params}} of GoM's item scripts (first value of each key, lower-cased keys)."""
    out = {}
    for f in glob.glob(os.path.join(MEDIA, "scripts/**/*.txt"), recursive=True):
        txt = read(f)
        for m in re.finditer(r'(?m)^\s*item\s+([\w\-]+)\s*\{(.*?)\n\s*\}', txt, re.S):
            params = {}
            for k, v in re.findall(r'(?m)^\s*(\w+)\s*=\s*([^\n]*?),?\s*$', m.group(2)):
                params.setdefault(k.lower(), v.strip())
            out["MarzGuns." + m.group(1)] = params
    return out


def tools(text):
    """{partType: tool name} from AttachAndDetach.lua's RegisterPartTools."""
    return {pt: tool for pt, tool in re.findall(r'\["(\w+)"\]\s*=\s*\{\s*Check\.(\w+)', text)}


def pct(f):
    return round(abs(f - 1.0) * 100)


def change(stat, f):
    return "%s %s by %d%%" % (label(stat), "reduced" if f < 1 else "increased", pct(f))


def spread_text(s):
    sustained, widest = s
    if sustained == widest:
        return "Automatic fire spread %s by %d%%" % ("reduced" if sustained < 1 else "increased", pct(sustained))
    return "Automatic fire spread %s by %d%% (its widest by %d%%)" % ("reduced" if sustained < 1 else "increased",
                                                                    pct(sustained), pct(widest))


def effects(ops, base=None, spread=None):
    """GoM's part-tooltip wording: Aiming Time first, Critical and Hit Chance merged when equal, then the rest; Set /
    Adjust are given against the gun's own value (`base`, lower-cased script keys)."""
    base = base or {}
    rel = {}
    for op, stat, v in ops:
        if op == "Multiply":
            rel[stat] = float(v)
        elif op in ("Set", "Adjust") and stat in LABEL:
            b = float(base.get(stat.lower(), "nan"))
            new = float(v) if op == "Set" else b + float(v)
            if b == b and b != 0:
                rel[stat] = new / b
    sets = {stat: v for op, stat, v in ops if op == "Set"}
    out = []
    if "AimingTime" in rel:
        out.append(change("AimingTime", rel.pop("AimingTime")))
    crit, hit = rel.pop("CriticalChance", None), rel.pop("HitChance", None)
    if crit is not None and crit == hit:
        out.append("Critical and Hit Chance %s by %d%%" % ("reduced" if crit < 1 else "increased", pct(crit)))
    else:
        for stat, f in (("CriticalChance", crit), ("HitChance", hit)):
            if f is not None:
                out.append(change(stat, f))
    for stat, f in sorted(rel.items()):
        out.append(change(stat, f))
    if spread:
        out.append(spread_text(spread)[0].lower() + spread_text(spread)[1:])
    if sets.get("RackAfterShot") == "true":
        out.append("rack after every shot")
    elif sets.get("RackAfterShot") == "false":
        out.append("no racking between shots")
    if sets.get("UseEndurance") == "false":
        out.append("no endurance used to fire")
    elif sets.get("UseEndurance") == "true":
        out.append("firing uses endurance")
    return out


def line(feature, states):
    """'<Feature>: <state>, <effects>; <state>, <effects>.' or a plain no-effect line."""
    parts = ["%s, %s" % (state, ", ".join(eff)) for state, eff in states if eff]
    if not parts:
        return "%s: no effect on handling." % feature
    return "%s: %s." % (feature, "; ".join(parts))


def lua_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    stats_text = read(os.path.join(REG, "AttachmentCustomStats.lua"))
    stats = part_stats(stats_text)
    spread = spread_mods(read(os.path.join(REG, "RPM.lua")))
    script = items()
    tool_of = tools(read(os.path.join(GOM, "shared/MarzWeapons/OnCreate/AttachAndDetach.lua")))
    table = read(os.path.join(GOM, "client/MarzWeapons/ItemTooltipsTable.lua"))
    gom_lines = {k: re.findall(r'"([^"]*)"', v)
                 for k, v in re.findall(r'\["([\w.-]+)"\]\s*=\s*\{(.*?)\}', table, re.S)}

    # ---- gun lines: folding stocks and bipods, mode selectors
    rows = []
    for kind, file in (("stock", "Stocks.lua"), ("bipod", "Bipods.lua")):
        for gun, (folded, deployed) in sorted(registrations(read(os.path.join(REG, file))).items()):
            feature = ("Folding stock" if gun in FOLDING else "Collapsible stock") if kind == "stock" else "Folding bipod"
            text = line(feature, [("deployed", effects(stats.get(deployed, []), spread=spread.get(deployed))),
                                  ("folded", effects(stats.get(folded, []), spread=spread.get(folded)))])
            rows.append((gun, VAGUE[kind], text))
            missing = [p for p in (folded, deployed) if p not in stats]
            note = " (no stats registered for %s)" % ", ".join(missing) if missing else ""
            print("%-18s %s%s" % (gun, text, note))
    for a, b in re.findall(r'DA\.RegisterPair\("([\w.-]+)",\s*"([\w.-]+)"\)', stats_text):
        pa, pb = script.get(a, {}), script.get(b, {})
        if pa.get("parttype") != "Selector" or pb.get("parttype") != "Selector":
            continue
        gun = pa.get("mounton", "").split(";")[0]
        base = script.get(gun, {})
        states = []
        for part in (a, b):
            mode = re.search(r'_([^_]+)$', part).group(1).lower()
            mode = {"pump": "pump action", "semi": "semi-automatic"}.get(mode, mode)
            states.append((mode, effects(stats.get(part, []), base=base, spread=spread.get(part))))
        text = line("Mode selector", states)
        rows.append((gun, "", text))
        print("%-18s %s" % (gun, text))
    print("GoM vague lines found: %d" % len(re.findall(r'"(Has Integrated (?:Stock|Bipod))', table)))

    # ---- part lines GoM's own part tooltips leave out
    part_rows = []
    for part, lines in sorted(gom_lines.items()):
        p = script.get(part)
        if not p or not p.get("parttype") or p.get("mounton") == "MarzGuns.FakeItem":
            continue
        joined = " ".join(lines).lower()
        add = []
        if part in spread and "spread" not in joined:
            add.append(spread_text(spread[part]))   # no full stop, as GoM's stat lines
        for key, stat in SCRIPT_MODS.items():
            v = p.get(key.lower())
            if v and stat.lower() not in joined:
                n = float(v)
                add.append("%s %s by %g" % (stat, "increased" if n > 0 else "reduced", abs(n)))
        tool = tool_of.get(p.get("parttype"))
        if tool and "needs " not in joined:
            add.append("Needs %s to install or remove." % tool)
        for text in add:
            part_rows.append((part, text))
            print("%-30s + %s" % (part, text))

    out = ['''--[[
    Guns of Tien -- what Guns of Marz's stocks, bipods, selectors and parts really do, in its tooltips (generated by
    scripts/gen_handling_tooltips.py from GoM's registries and item scripts; do not edit).

    GoM's tooltip table says only "Has Integrated Stock" / "Has Integrated Bipod" for some guns and nothing for others
    that have a stock, bipod or mode selector; its part lines leave out Gunworks' spread modifiers and the item
    scripts' own modifiers. Gun lines state what each state does, in the wording of GoM's part tooltips and of the
    Post-93 MP7s' lines, and replace GoM's vague line (or are added after the gun's other lines); part lines are added
    before the part's "Needs ..." line. GoM draws tooltipsPergun[fullType] at render time.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

local function listOf(fullType)
    local list = lines[fullType]
    if not list then
        list = {}
        lines[fullType] = list
    end
    return list
end

-- { gun, GoM's vague line it replaces ("" = none), the clear line }
local HANDLING = {
''']
    for gun, vague, text in rows:
        out.append("    { %s, %s, %s },\n" % (lua_str(gun), lua_str(vague), lua_str(text)))
    out.append('''}

-- { part, a line its tooltip is missing }
local PART_LINES = {
''')
    for part, text in part_rows:
        out.append("    { %s, %s },\n" % (lua_str(part), lua_str(text)))
    out.append('''}

for _, row in ipairs(HANDLING) do
    local list, vague, text = listOf(row[1]), row[2], row[3]
    local done = false
    for i, entry in ipairs(list) do
        if entry == text or (vague ~= "" and (entry == vague or entry == vague .. ".")) then
            list[i] = text
            done = true
        end
    end
    if not done then
        list[#list + 1] = text
    end
end

for _, row in ipairs(PART_LINES) do
    local list, text = listOf(row[1]), row[2]
    local present, at = false, #list + 1
    for i, entry in ipairs(list) do
        if entry == text then present = true end
        if at > #list and entry:find("^Needs ") then at = i end
    end
    if not present then
        table.insert(list, at, text)
    end
end
''')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    sys.exit(main())
