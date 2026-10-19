#!/usr/bin/env python3
"""Every tooltip text of both mods, as a Markdown checklist (the "Tooltip review" section of TODO.md).

    pip3 install --target <dir> lupa
    PYTHONPATH=<dir> python3 scripts/list_tooltips.py > review.md      (run from the repo root)
    PYTHONPATH=<dir> python3 scripts/list_tooltips.py --diff TODO.md   (the user's corrections, see below)

Runs GoM's ItemTooltipsTable.lua, then HandlingTooltips.lua, RoundTooltips.lua, Tooltips.lua and Post-93's
Tooltips.lua in a real Lua (lupa), and lists the Information lines of every item whose lines differ from GoM's, the
per-state lines (GunsOfTien_TooltipStates), the laser note, the sawn-off stock's holster lines, and every
Tooltip.json / IG_UI.json / Sandbox.json text.

Every entry carries a key in backticks (item type, translation key, or `File.lua NAME` for a text in Lua code), so
the user can rewrite the text after the colon in TODO.md. `--diff TODO.md` matches TODO's entries to these by key
and prints each one whose text differs (a correction to make in the code), plus keys only on one side.
"""
import lupa, os, json, re, sys
def first(*paths):
    return next((p for p in paths if os.path.exists(p)), paths[0])
WS = first(os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600"),
           "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600")
GOM = WS + "/3722134990/mods/GunsOfMarz/42.16/media/lua"
GW = WS + "/3722064198/mods/Gunworks_gang_framework/42.13/media/lua"
VAN = first(os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/Project Zomboid.app/Contents/Java/media/lua"),
            "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/lua")
MAIN = "Contents/mods/GoMExtensionGunsOfTien/42/media/lua"
POST = "Contents/mods/GoMExtensionGunsOfTienPost93/42/media/lua"
names = {}
for f in (VAN, GW, GOM, MAIN, POST):
    p = f + "/shared/Translate/EN/ItemName.json"
    if os.path.exists(p):
        names.update(json.load(open(p, encoding="utf-8")))
def name(t):
    return names.get(t) or names.get("ItemName_" + t) or t

lua = lupa.LuaRuntime()
lua.execute('''
unpack = unpack or table.unpack
local function ev() local h = {} return { Add = function(f) h[#h+1] = f end, Remove = function() end, run = function() for _, f in ipairs({unpack(h)}) do f() end end } end
Events = { OnGameStart = ev(), OnTick = ev() }
function instanceof() return false end
local gom = dofile([[%s/client/MarzWeapons/ItemTooltipsTable.lua]])
package.loaded["MarzWeapons/ItemTooltipsTable"] = gom
TABLE = gom.tooltipsPergun
ORIG = {}
for k, v in pairs(TABLE) do local c = {} for i, l in ipairs(v) do c[i] = l end ORIG[k] = c end
package.loaded["GunsOfTien/SawnStock"] = {}
package.loaded["GunsOfTien/Lasers"] = { TYPES = {} }
''' % GOM)
for f in ("HandlingTooltips.lua", "RoundTooltips.lua", "Tooltips.lua"):
    lua.execute('dofile([[%s/client/GunsOfTien/%s]])' % (MAIN, f))
lua.execute('dofile([[%s/client/GunsOfTienPost93/Tooltips.lua]])' % POST)
# the laser note (LaserMenu.lua needs the game; its line is read from the file)
laser_note = re.search(r'local NOTE = "([^"]+)"', open(MAIN + "/client/GunsOfTien/LaserMenu.lua").read()).group(1)
tooltips_src = open(MAIN + "/client/GunsOfTien/Tooltips.lua", encoding="utf-8").read()
fits_holster = re.search(r'local FITS_HOLSTER = "([^"]+)"', tooltips_src).group(1)
needs_barrels = re.search(r'local NEEDS_BARRELS = "([^"]+)"', tooltips_src).group(1)
laser_types = re.findall(r'"(MarzGuns\.[\w-]+_Laser)"', open(MAIN + "/shared/GunsOfTien/Lasers.lua").read())

def lst(t):
    return [t[i] for i in range(1, len(t) + 1)] if t else []
table, orig, states = lua.eval("TABLE"), lua.eval("ORIG"), lua.eval("GunsOfTien_TooltipStates")

def group(t):
    if t.startswith("GunsOfTienPost93."): return "post93"
    if re.search(r"Bullet|_Shell_", t): return "rounds"
    return "items"
out = {"rounds": [], "items": [], "post93": []}
for k in sorted(table.keys(), key=lambda k: name(k)):
    now = lst(table[k])
    was = lst(orig[k]) if orig[k] else None
    if now != was:
        out[group(k)].append((k, now))
pieces = []
def section(title, rows):
    pieces.append("\n### %s\n\n" % title)
    for k, lines in rows:
        pieces.append("- [ ] %s (`%s`): %s\n" % (name(k), k, " / ".join(lines) if lines else "(lines removed)"))
section("Rounds: Information lines (RealisticPiercing off; on, the plain .30-06 / .308 / 7.62x51 add "
        "\"Piercing targets / Able to hit up to 2 targets\", the 7N6 \"Critical Chance increased by 10% / Piercing targets / "
        "Able to hit up to 3 targets\")", out["rounds"])
section("Guns and parts: Information lines (always shown)", out["items"])
pieces.append("- [ ] Every laser, %s (`LaserMenu.lua NOTE`): %s\n" % (", ".join(name(t) for t in laser_types), laser_note))
section("Post-93: Information lines (always shown)", out["post93"])
pieces.append("\n### Guns: lines shown only while that part is fitted (after the gun's own lines)\n\n")
for k in sorted(states.keys(), key=lambda k: name(k)):
    pieces.append("- [ ] %s (`%s`): %s\n" % (name(k), k, " / ".join(lst(states[k]))))
pieces.append("- [ ] Sawn-off stock, also (`Tooltips.lua FITS_HOLSTER / NEEDS_BARRELS`): %s (with sawn-off barrels) / %s "
              "(with full barrels)\n" % (fits_holster, needs_barrels))
for title, path in (("Item, recipe and part-row tooltips (main mod Tooltip.json)", MAIN), ("Post-93 Tooltip.json", POST)):
    p = path + "/shared/Translate/EN/Tooltip.json"
    pieces.append("\n### %s\n\n" % title)
    for k, v in json.load(open(p, encoding="utf-8")).items():
        pieces.append("- [ ] `%s`: %s\n" % (k, v))
for title, f in (("Menu and option texts (main mod IG_UI.json)", MAIN + "/shared/Translate/EN/IG_UI.json"),
                 ("Post-93 IG_UI.json", POST + "/shared/Translate/EN/IG_UI.json"),
                 ("Sandbox options (main mod Sandbox.json)", MAIN + "/shared/Translate/EN/Sandbox.json")):
    if os.path.exists(f):
        pieces.append("\n### %s\n\n" % title)
        for k, v in json.load(open(f, encoding="utf-8")).items():
            pieces.append("- [ ] `%s`: %s\n" % (k, v))

def keyed(lines):
    """key -> text after the key's colon, for every checklist entry of a review list."""
    out = {}
    for line in lines:
        m = re.match(r"- \[[ x]\] (?:.*?\(`([^`]+)`\)|`([^`]+)`): (.*)$", line.rstrip("\r\n"))
        if m:
            out[m.group(1) or m.group(2)] = m.group(3)
    return out

if len(sys.argv) > 2 and sys.argv[1] == "--diff":
    todo = open(sys.argv[2], encoding="utf-8").read().split("\n")
    start = todo.index("## Tooltip review (2026-10-19)")
    end = next((i for i in range(start + 1, len(todo)) if todo[i].startswith("## ")), len(todo))
    now, want = keyed("".join(pieces).split("\n")), keyed(todo[start:end])
    for k in now:
        if k in want and want[k] != now[k]:
            sys.stdout.write("DIFF %s\n  code: %s\n  TODO: %s\n" % (k, now[k], want[k]))
    for k in now:
        if k not in want:
            sys.stdout.write("ONLY IN CODE %s: %s\n" % (k, now[k]))
    for k in want:
        if k not in now:
            sys.stdout.write("ONLY IN TODO %s: %s\n" % (k, want[k]))
else:
    sys.stdout.write("".join(pieces))
