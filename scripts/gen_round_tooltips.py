#!/usr/bin/env python3
"""Information lines of every round with a stat profile, read off the profiles themselves.

    python3 scripts/gen_round_tooltips.py

Guns of Marz's round lines (MarzWeapons/ItemTooltipsTable.lua) were written by hand and drifted from its profiles
(Registries/Ammunition.lua): "decreased by 50%" for a ConditionLowerChanceOneIn of x1.5 (one chance in N, so the chance
falls by a third), critical changes left out, typos ("Change to degrade"), the subsonic's sound given twice; the .38
Special has a profile and no line at all. Ours (shared/GunsOfTien/Ammunition.lua) had the same faults. This reads
both mods' families and profiles (and GoM's RPM.lua spread modifiers per round) and writes
Contents/mods/GoMExtensionGunsOfTien/42/media/lua/client/GunsOfTien/RoundTooltips.lua, which replaces each such
round's lines in GoM's table:
- one line per stat, in GoM's wording, no full stop: damage, critical damage, critical chance, sound, range, pellet
  spread, automatic fire spread, wear, piercing, racking, single slug;
- NOTES below add what a number cannot say (why a round racks, that a soft point expands);
- the plain rounds' realistic piercing (sandbox RealisticPiercing) is applied on OnGameStart, when the option is known.
Post-93's rounds are written by hand in its own Tooltips.lua (checked against its profiles 2026-10-19).
Run again after a profile changes or a GoM update; never hand-edit the output.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
MAIN = os.path.join(ROOT, "Contents/mods/GoMExtensionGunsOfTien/42/media")
OUT = os.path.join(MAIN, "lua/client/GunsOfTien/RoundTooltips.lua")
GOM = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600/"
                                          "3722134990/mods/GunsOfMarz/42.16/media"),
                       "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/"
                       "42.16/media") if os.path.isdir(p))
GOM_AMMO = os.path.join(GOM, "lua/shared/MarzWeapons/Registries/Ammunition.lua")
GOM_RPM = os.path.join(GOM, "lua/shared/MarzWeapons/Registries/RPM.lua")
OUR_AMMO = os.path.join(MAIN, "lua/shared/GunsOfTien/Ammunition.lua")

# What the numbers cannot say. "before" / "after" lines go around the stat lines; "replace" swaps a stat line by its
# key (damage, pierce, rack, ...) for a clearer one, or drops it (None).
# Compact, in GoM's own form (user, 2026-10-19: "do not overexplain"): one fact per line, no full stop.
SUPPRESSED = "Stacks with suppressors for maximum effectiveness"      # GoM's line, spelt right
NOTES = {
    "GunsOfTien.762x39_Bullet_US": {"after": ["Needs racking every shot", "Cycles normally with a PBS-1 suppressor",
                                              SUPPRESSED]},
    "GunsOfTien.9x19_Bullet_Subsonic": {"after": [SUPPRESSED]},
    "SWMG.556x45_Bullet_Subsonic": {"after": [SUPPRESSED]},
    "SWMG.3030_Bullet": {"before": ["Does not pierce"]},
    "Base.3030Bullets": {"before": ["Does not pierce"]},
}
# Lines that go with the realistic piercing lines (option on), before them.
PIERCING_NOTES = {}


def read(path):
    return open(path, encoding="utf-8").read()


def number(v):
    v = v.strip()
    if v in ("true", "false"):
        return v == "true"
    try:
        return float(v)
    except ValueError:
        return v


def pct(f):
    return round(abs(f - 1.0) * 100)


def up_down(f, up="increased", down="decreased"):
    return "%s by %d%%" % (up if f > 1 else down, pct(f))


def stat_lines(mods):
    """[(key, line)] for a profile's modifiers {stat: ('mul' | 'set', value)}."""
    out = []

    def mul(stat):
        m = mods.get(stat)
        return m[1] if m and m[0] == "mul" and m[1] != 1.0 else None

    def put(stat):
        m = mods.get(stat)
        return m[1] if m and m[0] == "set" else None

    if mul("MaxDamage"):
        out.append(("damage", "Damage to targets " + up_down(mul("MaxDamage"))))
    if mul("CritDmgMultiplier"):
        out.append(("critdmg", "Critical Damage " + up_down(mul("CritDmgMultiplier"))))
    if mul("CriticalChance"):
        out.append(("critchance", "Critical Chance " + up_down(mul("CriticalChance"))))
    if mul("SoundRadius"):
        out.append(("sound", "Sound Radius and Volume " + up_down(mul("SoundRadius"), down="reduced")))
    if mul("MaxRange"):
        out.append(("range", "Range " + up_down(mul("MaxRange"), down="reduced")))
    if mul("ProjectileSpread"):
        f = mul("ProjectileSpread")
        out.append(("spread", "Pellet spread doubled" if f == 2 else "Pellet spread " + up_down(f, "wider by", "narrower by")))
    if mods.get("AutoSpread"):
        f = mods["AutoSpread"][1]
        out.append(("autospread", "Automatic fire spread doubled" if f == 2 else "Automatic fire spread " + up_down(f)))
    if mul("ConditionLowerChanceOneIn"):
        c = 1.0 / mul("ConditionLowerChanceOneIn")     # one chance in N: the chance is 1 / N
        if abs(c - 0.5) < 1e-9:
            text = "Chance to degrade weapon condition halved"
        elif abs(c - 2.0) < 1e-9:
            text = "Chance to degrade weapon condition doubled"
        else:
            text = "Chance to degrade weapon condition " + up_down(c)
        out.append(("wear", text))
    hits = put("MaxHitCount")
    if hits is not None:
        if hits > 1:
            out.append(("pierce", "Piercing targets"))
            out.append(("hits", "Able to hit up to %d targets" % hits))
        else:
            out.append(("pierce", "Does not pierce"))
    if put("RackAfterShot") is True:
        out.append(("rack", "Needs racking every shot"))
    if put("ProjectileCount") == 1:
        out.append(("slug", "One slug per shell"))
    return out


def with_notes(full_type, pairs, notes=NOTES):
    note = notes.get(full_type, {})
    lines = list(note.get("before", []))
    for key, text in pairs:
        if key in note.get("replace", {}):
            text = note["replace"][key]
        if text:
            lines.append(text)
    lines += note.get("after", [])
    return lines


# ---- GoM

def gom_families(text):
    return re.findall(r'\{\s*type\s*=\s*"([\w.]+)",\s*enum\s*=\s*([\w.]+),\s*profile\s*=\s*"(\w+)"\s*\}', text)


def gom_profiles(text):
    block = text[text.index("RegisterMultipleAmmoStats"):]
    out = {}
    for name, body in re.findall(r'\["(\w+)"\]\s*=\s*\{(.*?)\n\s*\},', block, re.S):
        mods = {}
        for op, stat, v in re.findall(r'StatsFactory\.(Multiply|Set)\("(\w+)",\s*([^)]+)\)', body):
            mods[stat] = ("mul" if op == "Multiply" else "set", number(v))
        out[name] = mods
    return out


def round_spread(text):
    """{round full type: multiplier} from RPM.lua's RegisterSpreadAmmoModifier. GoM registers its overpressured 5.56
    as "MarzGuns.556x45_Bullet_Overpressured", a type that does not exist (the round is SWMG.), so the penalty never
    applied; shared/GunsOfTien/GoMFixes.lua registers it under the real type, and so is it read here."""
    out = {}
    for key, body in re.findall(r'RegisterSpreadAmmoModifier\("([\w.]+)",\s*\{([^}]*)\}', text):
        s = re.search(r'sustainedSpreadMult\s*=\s*([\d.]+)', body)
        out[re.sub(r"^MarzGuns\.", "SWMG.", key)] = float(s.group(1)) if s else 1.0
    return out


# ---- ours

def our_mods(body):
    mods = {}
    for f in re.findall(r'\bdamage\(([\d.]+)\)', body):
        mods["MaxDamage"] = ("mul", float(f))
    for f in re.findall(r'\bsound\(([\d.]+)\)', body):
        mods["SoundRadius"] = ("mul", float(f))
    for n in re.findall(r'\bpierce\((\d+)\)', body):
        mods["MaxHitCount"] = ("set", float(n))
    for op, stat, v in re.findall(r'SF\.(Multiply|Set)\("(\w+)",\s*([^)]+)\)', body):
        mods[stat] = ("mul" if op == "Multiply" else "set", number(v))
    m = re.search(r'getProjectileSpread\(\)\s*\*\s*([\d.]+)', body)
    if m:
        mods["ProjectileSpread"] = ("mul", float(m.group(1)))
    return mods


def our_profiles(text):
    block = text[text.index("Ammo.RegisterMultipleAmmoStats"):]
    block = block[:block.index("\n})")]
    names = list(re.finditer(r'\["(\w+)"\]\s*=\s*list\(', block))
    out = {}
    for i, m in enumerate(names):
        end = names[i + 1].start() if i + 1 < len(names) else len(block)
        out[m.group(1)] = our_mods(block[m.end():end])
    return out


def our_families(text):
    return re.findall(r'type\s*=\s*"([\w.]+)",\s*enum\s*=\s*T\.(\w+),\s*profile\s*=\s*"(\w+)"', text)


def plain_rounds(text):
    """[(enum expression, mods)] of the RealisticPiercing layer (addPlain)."""
    lists = {name: our_mods(body) for name, body in re.findall(r'local\s+(\w+)\s*=\s*list\((.*?)\)\n', text)}
    out = []
    for enum, arg in re.findall(r'addPlain\(([\w.]+),\s*(.+)\)\n', text):
        enum = enum.replace("SW.", "SWMG_AmmoTypes.")
        out.append((enum, lists.get(arg.strip()) or our_mods(arg)))
    return out


def lua_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def lua_table(rows):
    out = []
    for full_type, lines in rows:
        out.append("    [%s] = {\n%s    },\n" % (lua_str(full_type), "".join("        %s,\n" % lua_str(l) for l in lines)))
    return "".join(out)


def main():
    gom_text, our_text = read(GOM_AMMO), read(OUR_AMMO)
    gprof, oprof = gom_profiles(gom_text), our_profiles(our_text)
    spread = round_spread(read(GOM_RPM))

    rounds = {}
    for full_type, enum, profile in gom_families(gom_text):
        mods = dict(gprof.get(profile, {}))
        if mods.get("ProjectileCount", ("", None))[1] == 0:
            continue                                    # 40 mm grenades: not a bullet's stats
        if full_type in spread:
            mods["AutoSpread"] = ("mul", spread[full_type])
        lines = with_notes(full_type, stat_lines(mods))
        if lines:
            rounds[full_type] = lines
    for full_type, enum, profile in our_families(our_text):
        rounds[full_type] = with_notes(full_type, stat_lines(oprof[profile]))

    enum_types = {}
    for full_type, enum, profile in gom_families(gom_text):
        enum_types.setdefault(enum, []).append(full_type)
    piercing = {}
    for enum, mods in plain_rounds(our_text):
        pairs = [(k, t) for k, t in stat_lines(mods) if not (k == "pierce" and t == "Does not pierce")]
        if not pairs:
            continue                                    # .30-30: never pierces either way (its notes say so)
        for full_type in enum_types.get(enum, []):
            piercing[full_type] = PIERCING_NOTES.get(full_type, []) + [t for _, t in pairs]

    for full_type in sorted(rounds):
        print("%-36s %s" % (full_type, " / ".join(rounds[full_type])))
    for full_type in sorted(piercing):
        print("%-36s + (RealisticPiercing) %s" % (full_type, " / ".join(piercing[full_type])))

    out = ['''--[[
    Guns of Tien -- the Information lines of every round with a stat profile, Guns of Marz's and ours (generated by
    scripts/gen_round_tooltips.py from both mods' ammo profiles; do not edit).

    Each round's lines in GoM's tooltipsPergun table are replaced by one line per stat its profile changes, so they
    match what the round does. The plain rounds' realistic piercing (sandbox RealisticPiercing) is added on
    OnGameStart, when sandbox options are known; before that (the main menu) the lines are the option-off ones.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

-- full type -> its lines
local ROUNDS = {
''', lua_table(sorted(rounds.items())), '''}

-- full type -> lines added while RealisticPiercing is on
local PIERCING = {
''', lua_table(sorted(piercing.items())), '''}

local function copy(list)
    local out = {}
    for i, line in ipairs(list) do out[i] = line end
    return out
end

local function apply()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    local piercingOn = vars ~= nil and vars.RealisticPiercing == true
    for fullType, list in pairs(ROUNDS) do
        lines[fullType] = copy(list)
    end
    for fullType, extra in pairs(PIERCING) do
        local list = lines[fullType] or {}
        lines[fullType] = list
        local ours = {}
        for _, line in ipairs(extra) do ours[line] = true end
        for i = #list, 1, -1 do
            if ours[list[i]] then table.remove(list, i) end
        end
        if piercingOn then
            for _, line in ipairs(extra) do list[#list + 1] = line end
        end
        if #list == 0 then lines[fullType] = nil end
    end
end

apply()
Events.OnGameStart.Add(apply)
''']
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    sys.exit(main())
