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
- for every integrated stock, bipod and mode selector state with effects, its lines in the style of GoM's part
  tooltips: a heading ("Collapsible stock deployed:") and one effect per line ("Aiming Time reduced by 25%"), into
  the global GunsOfTien_TooltipStates (keyed by the part); client/GunsOfTien/Tooltips.lua shows them under a gun
  while that part is fitted, so only the current state's stats show. GoM's vague "Has Integrated Stock / Bipod"
  lines are removed;
- the lines a part's own tooltip is missing (spread, script modifiers, the tool to fit it), before its "Needs ..."
  line;
- the vague or missing lines of the rest (2026-10-19): the shell holder's "fire 40% faster" (its Recoil Delay), the
  bayonets' "Can be attached to compatible rifles" and the guns' "Can Attach Bayonet(s)" (the guns from
  Registries/Bayonets.lua, the K98 included as shared/GunsOfTien/GoMFixes.lua registers it), the Picatinny Rail,
  the speedloaders and stripper clip (Registries/SpeedLoader.lua), the slings and the VP70M stock, and "Uses ...
  rounds." / mounting and muzzle device lines for the magazines and guns GoM gave none (copied from items with the
  same round or part). Compact, in GoM's own form (user, 2026-10-19: "do not overexplain"): one fact per line, the
  number where GoM left it out.
The rounds' lines are gen_round_tooltips.py's. Run again after a GoM update; never hand-edit the output.
"""

import glob
import json
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
    sustained = s[0]
    return "Automatic fire spread %s by %d%%" % ("reduced" if sustained < 1 else "increased", pct(sustained))


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
        out.append("needs racking every shot")
    if sets.get("UseEndurance") == "false":
        out.append("no endurance used to fire")
    elif sets.get("UseEndurance") == "true":
        out.append("firing uses endurance")
    return out


def cap(text):
    return text[0].upper() + text[1:]


def state_lines(heading, eff):
    """GoM's attachment style (user, 2026-10-19: "the way GoM lists the buffs and debuffs is better"): a heading
    ("Folding stock deployed:", "Pump action:") and one effect per line, no full stop; nothing for a state without
    effects (user: "only display the proper CURRENT stats if they are active")."""
    return [cap(heading) + ":"] + [cap(e) for e in eff] if eff else []


def info_rows(script, gom_lines, tool_of, names):
    """(rows, part_rows) for the vague and missing lines that are not about handling (see the header)."""
    rows, part_rows = [], []
    reg = REG

    def name(full_type):
        return names.get(full_type, full_type.split(".")[-1])

    # shell holder: its real stat, and what it fits
    stats = part_stats(read(os.path.join(reg, "AttachmentCustomStats.lua")))
    holder = "MarzGuns.Shellholder"
    if holder in stats:
        rows.append((holder, "Allows the user to fire 40% faster", effects(stats[holder])[0]))
        rows.append((holder, "", "Attachable on stocks."))

    # bayonets
    btext = read(os.path.join(reg, "Bayonets.lua"))
    mountable = {}
    for atts, guns in re.findall(r'RegisterMountableWeapon\(\{([^}]*)\},\s*\{([^}]*)\}', btext, re.S):
        for gun in re.findall(r'"([\w.]+)"', guns):
            mountable.setdefault(gun, set()).update(re.findall(r'"([\w.]+)"', atts))
    knives = dict(re.findall(r'RegisterBayonetKnife\("([\w.]+)",\s*"([\w.]+)"', btext))
    m5 = "MarzGuns.M5_Bayonet_Attachment"
    for gun, atts in mountable.items():
        if m5 in atts:
            atts.add("MarzGuns.K98_Bayonet_Attachment")      # GoMFixes.lua
    for gun in sorted(mountable):
        text = "Can attach a bayonet."
        old = next((l for l in gom_lines.get(gun, []) if l.startswith("Can Attach Bayonet")), "")
        rows.append((gun, old, text))
    for knife in sorted(knives):
        old = next((l for l in gom_lines.get(knife, []) if "compatible rifles" in l), "")
        rows.append((knife, old, "Attachable on compatible guns."))
        rows.append((knife, "", "Cannot install if a muzzle device or M203 is installed."))

    # Picatinny Rail (Registries/UniversalAttachments.lua turns it into the slot picked)
    rail = "MarzGuns.Picatinny_Rail"
    rows.append((rail, "Allows attachments to be installed on weapons", "Adds a rail on one of the slots of the gun."))

    # speedloaders and stripper clips
    for gun, loader in re.findall(r'\["([\w.]+)"\]\s*=\s*"([\w.]+)"', read(os.path.join(reg, "SpeedLoader.lua"))):
        p = script.get(loader, {})
        kind = "stripper clip" if "Stripper" in loader else "speedloader"
        text = "Compatible with %d-round %s." % (int(float(p.get("maxammo", 0))), kind)
        old = next((l for l in gom_lines.get(gun, []) if l.startswith("Has Speedloader")), "")
        rows.append((gun, old, text))
        garbled = next((l for l in gom_lines.get(loader, []) if "previous fully loaded" in l), None)
        if garbled and (loader, garbled) not in [(r[0], r[1]) for r in rows]:
            rows.append((loader, garbled, "Reloads the revolver faster when fully loaded."))

    # parts with no line at all: slings, the VP70M stock
    for part, p in sorted(script.items()):
        if part in gom_lines or not p.get("parttype") or p.get("mounton") == "MarzGuns.FakeItem":
            continue
        tool = tool_of.get(p.get("parttype"))
        if p.get("parttype") == "Sling":
            rows.append((part, "", "Reduces encumbrance."))
        elif p.get("parttype") == "Stock":
            rows.append((part, "", "No Direct Stat Changes"))
        else:
            continue
        if tool:
            part_rows.append((part, "Needs %s to install or remove." % tool))

    # "Uses ... rounds." for magazines and guns GoM gave no lines, from items with the same round
    uses = {}
    for item, lines in gom_lines.items():
        ammo = script.get(item, {}).get("ammotype")
        for l in lines:
            if ammo and l.startswith("Uses "):
                uses.setdefault(ammo, l)
    uses.setdefault("swmg:bullet_2bore", "Uses 2-bore rounds.")
    for item, p in sorted(script.items()):
        ammo = p.get("ammotype")
        is_mag = p.get("parttype") == "Clip" and "Magazine" in item
        is_gun = p.get("subcategory") == "Firearm" and not item.endswith("_Weapon")
        if item in gom_lines or not ammo or not (is_mag or is_gun) or ammo not in uses:
            continue
        rows.append((item, "", uses[ammo]))
        if is_gun:
            # mounting / muzzle device lines of a gun that shares the part
            mine = {q for q, r in script.items() if item in [x.strip() for x in r.get("mounton", "").split(";")]}
            for prefix in ("Compatible Mounting Device:", "Compatible Muzzle Device:"):
                for other, lines in sorted(gom_lines.items()):
                    line = next((l for l in lines if l.startswith(prefix)), None)
                    theirs = {q for q, r in script.items()
                              if other in [x.strip() for x in r.get("mounton", "").split(";")]}
                    want = "RailUp" if "Mounting" in prefix else "CanonMount"
                    if line and any(script[q].get("parttype") == want for q in mine & theirs):
                        # "Subject: Detail" lines end without a full stop (user, 2026-10-19)
                        rows.append((item, "", line.rstrip(".")))
                        break
    return rows, part_rows


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
    states = {}        # integrated part -> its lines, shown while it is fitted (Tooltips.lua)
    for kind, file in (("stock", "Stocks.lua"), ("bipod", "Bipods.lua")):
        for gun, (folded, deployed) in sorted(registrations(read(os.path.join(REG, file))).items()):
            feature = ("Folding stock" if gun in FOLDING else "Collapsible stock") if kind == "stock" else "Folding bipod"
            rows.append((gun, VAGUE[kind], []))         # GoM's vague line goes, the state lines show instead
            for state, part in (("deployed", deployed), ("folded", folded)):
                lines = state_lines("%s %s" % (feature, state), effects(stats.get(part, []), spread=spread.get(part)))
                if lines:
                    states[part] = lines
                    print("%-18s %-40s %s" % (gun, part, " / ".join(lines)))
    for a, b in re.findall(r'DA\.RegisterPair\("([\w.-]+)",\s*"([\w.-]+)"\)', stats_text):
        pa, pb = script.get(a, {}), script.get(b, {})
        if pa.get("parttype") != "Selector" or pb.get("parttype") != "Selector":
            continue
        gun = pa.get("mounton", "").split(";")[0]
        base = script.get(gun, {})
        for part in (a, b):
            mode = re.search(r'_([^_]+)$', part).group(1).lower()
            mode = {"pump": "pump action", "semi": "semi-automatic"}.get(mode, mode)
            lines = state_lines(mode, effects(stats.get(part, []), base=base, spread=spread.get(part)))
            if lines:
                states[part] = lines
                print("%-18s %-40s %s" % (gun, part, " / ".join(lines)))
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

    names = json.load(open(os.path.join(MEDIA, "lua/shared/Translate/EN/ItemName.json"), encoding="utf-8"))
    more_rows, more_parts = info_rows(script, gom_lines, tool_of, names)
    for gun, vague, text in more_rows:
        print("%-36s %s%s" % (gun, ("[%s] -> " % vague) if vague else "+ ", text))
    rows += [(item, vague, [text]) for item, vague, text in more_rows]
    part_rows += more_parts

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

-- { item, GoM's vague line they replace ("" = none), the clear lines }
local HANDLING = {
''']
    for gun, vague, texts in rows:
        out.append("    { %s, %s, { %s } },\n" % (lua_str(gun), lua_str(vague), ", ".join(lua_str(t) for t in texts)))
    out.append('''}

-- integrated part -> its lines, shown under a gun while that part is fitted (Tooltips.lua sets them per render)
GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
local STATES = GunsOfTien_TooltipStates
''')
    for part in sorted(states):
        out.append("STATES[%s] = { %s }\n" % (lua_str(part), ", ".join(lua_str(t) for t in states[part])))
    out.append('''
-- { part, a line its tooltip is missing }
local PART_LINES = {
''')
    for part, text in part_rows:
        out.append("    { %s, %s },\n" % (lua_str(part), lua_str(text)))
    out.append('''}

for _, row in ipairs(HANDLING) do
    local list, vague, texts = listOf(row[1]), row[2], row[3]
    local present = false
    for _, entry in ipairs(list) do
        if entry == texts[1] then present = true end
    end
    if not present then
        -- in the vague line's place, else before a part's "Needs ..." line, else at the end
        local at = nil
        for i, entry in ipairs(list) do
            if vague ~= "" and (entry == vague or entry == vague .. ".") then at = i end
        end
        if at then
            table.remove(list, at)
        else
            at = #list + 1
            for i, entry in ipairs(list) do
                if entry:find("^Needs ") then at = i break end
            end
        end
        for j, text in ipairs(texts) do
            table.insert(list, at + j - 1, text)
        end
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
