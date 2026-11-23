#!/usr/bin/env python3
"""What every gun of both mods (and GoM's, for comparison) can really take, against what its tooltip says.

    py -m pip install --target <dir> lupa
    PYTHONPATH=<dir> py scripts/attachment_audit.py [--json out.json] > report.md      (from the repo root)

Reads every item script of Gunworks, Guns of Marz and our two mods (MountOn, PartType, ModelWeaponPart), then runs
every shared, client and server Lua file of those four mods in a real Lua (lupa) against mocks, in the game's order
(shared, client, server; per folder the mods in load order), and fires OnGameBoot, OnInitGlobalModData,
OnLoadMapZones and OnGameStart, so that every MountOn appended from Lua (DoParam), every Gunworks registry
(UniversalAttachment, RequiredAttachment, PreventRemovals, GoM's spawn table) and every tooltip line is the one the
game ends up with.

Per gun, a part is **fittable** when its MountOn lists the gun and each of its required parents (Gunworks'
RequiredAttachment: all of `Dependencies`, one of `AnyDependencies`) is integrated on the gun (GoM's spawn table
"required" parts) or fittable itself. A rail side is offered by GoM's universal Picatinny Rail only when the gun's
UniversalAttachment outcome for it is also in that side's MountOn (Gunworks' CanInstallOutcome asks canAttach).
"""
import json
import os
import re
import sys
from collections import defaultdict

import lupa


def first(*paths):
    return next((p for p in paths if os.path.exists(p)), paths[0])


WS = first(os.path.expanduser("~/Library/Application Support/Steam/steamapps/workshop/content/108600"),
           "C:/Program Files (x86)/Steam/steamapps/workshop/content/108600")
GW = WS + "/3722064198/mods/Gunworks_gang_framework/42.13/media"
GOM = WS + "/3722134990/mods/GunsOfMarz/42.16/media"
MAIN = "Contents/mods/GoMExtensionGunsOfTien/42/media"
POST = "Contents/mods/GoMExtensionGunsOfTienPost93/42/media"
MODS = [("SWMG", GW), ("GunsOfMarz", GOM), ("GunsOfTien", MAIN), ("GunsOfTienPost93", POST)]

# ---------------------------------------------------------------------------------------------------------------
# Item scripts
# ---------------------------------------------------------------------------------------------------------------
items = {}          # full type -> {key: value} (repeated keys -> list under key + "[]")


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def parse_scripts(root):
    for dirpath, _, files in os.walk(root + "/scripts"):
        for f in sorted(files):
            if not f.endswith(".txt"):
                continue
            src = strip_comments(open(os.path.join(dirpath, f), encoding="utf-8", errors="replace").read())
            for mm in re.finditer(r"\bmodule\s+(\w+)\s*\{", src):
                module = mm.group(1)
                # the module body: up to its matching brace
                depth, i = 1, mm.end()
                while depth and i < len(src):
                    depth += {"{": 1, "}": -1}.get(src[i], 0)
                    i += 1
                body = src[mm.end():i - 1]
                for im in re.finditer(r"\bitem\s+([\w\-\.&]+)\s*\{([^{}]*)\}", body):
                    fields = {}
                    for entry in im.group(2).split(","):
                        if "=" not in entry:
                            continue
                        k, v = entry.split("=", 1)
                        k, v = k.strip(), v.strip()
                        fields.setdefault(k.lower() + "[]", []).append(v)
                        fields[k.lower()] = v
                    items[module + "." + im.group(1)] = fields


for _, root in MODS:
    parse_scripts(root)

mount_on = {t: [x.strip() for x in f.get("mounton", "").split(";") if x.strip()] for t, f in items.items()}


def item_kind(t):
    return (items.get(t, {}).get("itemtype") or "").lower()


names = {}
for _, root in MODS:
    p = root + "/lua/shared/Translate/EN/ItemName.json"
    if os.path.exists(p):
        names.update(json.load(open(p, encoding="utf-8")))


def name(t):
    return names.get(t) or names.get("ItemName_" + t) or items.get(t, {}).get("displayname") or t


# ---------------------------------------------------------------------------------------------------------------
# Lua
# ---------------------------------------------------------------------------------------------------------------
lua = lupa.LuaRuntime(unpack_returned_tuples=True)
G = lua.globals()
paths = []
for _, root in MODS:
    for folder in ("shared", "client", "server"):
        paths.append(root + "/lua/" + folder + "/?.lua")
G.package.path = ";".join(paths)

lua.execute(r'''
unpack = unpack or table.unpack
LOG = {}
local function log(s) LOG[#LOG + 1] = s end
STUB = nil
local stubmt = {}
stubmt.__index = function(t, k) return STUB end
stubmt.__call = function() return STUB end
stubmt.__concat = function(a, b) return (type(a) == "string" and a or "") .. (type(b) == "string" and b or "") end
stubmt.__len = function() return 0 end
stubmt.__add = function() return 0 end
stubmt.__sub = function() return 0 end
stubmt.__mul = function() return 0 end
stubmt.__div = function() return 0 end
stubmt.__unm = function() return 0 end
stubmt.__lt = function() return false end
stubmt.__le = function() return false end
stubmt.__tostring = function() return "STUB" end
STUB = setmetatable({}, stubmt)

-- Java lists
function JList(t)
    local o = { t = t or {} }
    function o:size() return #self.t end
    function o:get(i) return self.t[i + 1] end
    function o:add(v) self.t[#self.t + 1] = v return true end
    function o:contains(v) for _, x in ipairs(self.t) do if x == v then return true end end return false end
    function o:isEmpty() return #self.t == 0 end
    function o:iterator() local i = 0 return { hasNext = function() return i < #o.t end,
        next = function() i = i + 1 return o.t[i] end } end
    return setmetatable(o, { __index = function() return STUB end })
end
ArrayList = { new = function() return JList({}) end }

-- events
local events = {}
Events = setmetatable({}, { __index = function(_, name)
    events[name] = events[name] or { list = {} }
    local e = events[name]
    return { Add = function(f) e.list[#e.list + 1] = f end, Remove = function(f)
        for i = #e.list, 1, -1 do if e.list[i] == f then table.remove(e.list, i) end end end }
end })
function FIRE(name)
    local e = events[name]
    if not e then return end
    for _, f in ipairs({ unpack(e.list) }) do
        if RESET_LIMIT then RESET_LIMIT() end
        local ok, err = xpcall(f, debug.traceback)
        if not ok then log("event " .. name .. ": " .. tostring(err):sub(1, 600)) end
    end
end
LuaEventManager = { AddEvent = function() end }
triggerEvent = function() end

function isClient() return false end
function isServer() return false end
function getDebug() return false end
print = function(...) local t = {} for i = 1, select("#", ...) do t[#t + 1] = tostring((select(i, ...))) end io.stderr:write(table.concat(t, " ") .. string.char(10)) end
function getPlayer() return nil end
function getSpecificPlayer() return nil end
function getNumActivePlayers() return 0 end
function isDebugEnabled() return false end
function getText(k, ...) return k end
function getTextOrNull(k) return nil end
function instanceof(o, c) return type(o) == "table" and o.__class == c end
function getActivatedMods() return JList({ "SWMG", "GunsOfMarz", "GoMExtensionGunsOfTien",
    "GoMExtensionGunsOfTienPost93" }) end
function getGameTime() return STUB end
function newrandom() return { random = function(_, a, b) return 1 end } end
ZombRand = function() return 0 end
SandboxVars = setmetatable({}, { __index = function(t, k) local v = setmetatable({}, { __index = function() return nil end }) rawset(t, k, v) return v end })
''')

script_mocks = {}


def make_script(t):
    return script_mocks.setdefault(t, lua.eval('''function(t, py)
        local s = { __class = "Item", fullType = t }
        function s:DoParam(p) py.doparam(t, p) end
        function s:getFullName() return t end
        function s:getFullType() return t end
        function s:getName() return t:match("%.(.+)$") end
        function s:getModuleName() return t:match("^([^%.]+)") end
        function s:getDisplayName() return py.dname(t) end
        function s:getMountOn() return JList(py.mounton(t)) end
        function s:getMagazineType() return py.field(t, "magazinetype") end
        function s:isRanged() return tostring(py.field(t, "ranged") or ""):lower() == "true" end
        function s:getTags() return JList({}) end
        function s:getModData() return {} end
        return setmetatable(s, { __index = function() return STUB end })
    end''')(t, PY))


class Py:
    def doparam(self, t, p):
        k, _, v = str(p).partition("=")
        k, v = k.strip().lower(), v.strip()
        items.setdefault(t, {})[k] = v
        if k == "modelweaponpart":          # Item.DoParam appends a ModelWeaponPart line
            items[t].setdefault("modelweaponpart[]", []).append(v)
        if k == "mounton":
            mount_on[t] = [x.strip() for x in v.split(";") if x.strip()]

    def dname(self, t):
        return name(t)

    def field(self, t, k):
        return items.get(t, {}).get(k)

    def alltypes(self):
        return lua.table_from(sorted(items))

    def mounton(self, t):
        return lua.table_from(mount_on.get(t, []))


PY = Py()
G.PY = PY
lua.execute(r'''
local function scriptOf(t) if PY.field(t, "itemtype") or PY.field(t, "mounton") or PY.field(t, "displayname") then return MAKE_SCRIPT(t) end return nil end
ScriptManager = { instance = { getItem = function(_, t) return scriptOf(t) end,
    getAllItems = function() local l = {} for _, t in ipairs(PY.alltypes()) do l[#l + 1] = MAKE_SCRIPT(t) end return JList(l) end,
    getModelScript = function() return nil end,
    FindItem = function(_, t) return scriptOf(t) end } }
setmetatable(ScriptManager.instance, { __index = function() return STUB end })
function getScriptManager() return ScriptManager.instance end
function instanceItem(t)
    if not scriptOf(t) then return nil end
    local kind = PY.field(t, "itemtype") or ""
    local o = { __class = (kind == "base:weaponpart") and "WeaponPart" or (kind == "base:weapon") and "HandWeapon" or "InventoryItem" }
    function o:getFullType() return t end
    function o:getType() return t:match("%.(.+)$") end
    function o:getPartType() return PY.field(t, "parttype") end
    function o:getMagazineType() local m = PY.field(t, "magazinetype") if m and not m:find("%.") then m = t:match("^([^%.]+)") .. "." .. m end return m end
    function o:getMountOn() return JList(PY.mounton(t)) end
    function o:getModData() return {} end
    function o:getScriptItem() return scriptOf(t) end
    return setmetatable(o, { __index = function() return STUB end })
end
''')
G.MAKE_SCRIPT = lambda t: make_script(t)

# every global not set above is a stub (UI classes, Java statics...)
lua.execute(r'''
-- mods' own globals (GunsOfTien_*, MarzGuns_*...) are nil until a file sets them, as in game ("X = X or {}")
keyBinding = {}
setmetatable(_G, { __index = function(t, k) if type(k) == "string" and k:find("_") then return nil end return STUB end })
-- vanilla modules (TimedActions/..., ISUI/...) are not loaded: any module not found in the four mods is a stub
table.insert(package.searchers, function(n) return function() return STUB end end)
-- a loop waiting on a stub would never end: give up on any chunk after 50 M instructions
local count = 0
debug.sethook(function() count = count + 1 if count > 500 then count = 0 error("instruction limit") end end, "", 100000)
function RESET_LIMIT() count = 0 end
''')

load_errors = []


def load_folder(folder):
    for mod, root in MODS:
        base = root + "/lua/" + folder
        files = []
        for dirpath, _, fs in os.walk(base):
            for f in fs:
                if f.endswith(".lua"):
                    rel = os.path.relpath(os.path.join(dirpath, f), base).replace("\\", "/")
                    files.append(rel)
        for rel in sorted(files, key=str.lower):
            if rel.startswith("Translate/"):
                continue
            name = rel[:-4]
            sys.stderr.write("load %s %s/%s\n" % (mod, folder, rel))
            sys.stderr.flush()
            ok, err = lua.eval('''function(n)
                RESET_LIMIT()
                if package.loaded[n] ~= nil then return true, "" end
                local ok, r = xpcall(require, debug.traceback, n)
                if not ok then package.loaded[n] = false end
                return ok, tostring(r) end''')(name)
            if not ok:
                sys.stderr.write("FAILED %s %s/%s:\n%s\n" % (mod, folder, rel, err))
                load_errors.append("%s %s/%s: %s" % (mod, folder, rel, str(err).splitlines()[0][:200]))


# each mod's media/registries.lua runs before any Lua (ModRegistries.init; Gunworks' sets SWMG_AmmoTypes)
for _, root in MODS:
    reg = root + "/registries.lua"
    if os.path.exists(reg):
        try:
            lua.execute(open(reg, encoding="utf-8").read())
        except lupa.LuaError as e:
            sys.stderr.write("registries.lua %s: %s\n" % (root, e))
for folder in ("shared", "client", "server"):
    load_folder(folder)
for ev in ("OnGameBoot", "OnInitGlobalModData", "OnLoadMapZones", "OnGameStart"):
    lua.execute('FIRE("%s")' % ev)
for _ in range(3):
    lua.execute('FIRE("OnTick")')
for e in lua.eval("LOG").values():
    sys.stderr.write("LUA: %s\n" % e)


def lua_table(t):
    if t is None or lupa.lua_type(t) != "table":
        return {}
    return {k: t[k] for k in t.keys()}


def lua_list(t):
    if t is None or lupa.lua_type(t) != "table":
        return []
    return [t[i] for i in range(1, len(t) + 1)]


def req(name):
    return lua.eval('function(n) local v = package.loaded[n] if v then return v end return nil end')(name)


UA = req("WeaponSystems/Utils/UniversalAttachment")
MAG = req("WeaponSystems/Utils/Magazine")
RA = req("WeaponSystems/Utils/RequiredAttachment")
PR = req("WeaponSystems/Utils/PreventRemovals")
APT = req("MarzWeapons/OnCreate/AttachmentPointsTable")
TT = req("MarzWeapons/ItemTooltipsTable")

universal = defaultdict(list)
for gun, entries in lua_table(UA.Registry).items():
    for generic, outcomes in lua_table(entries).items():
        universal[gun] += [(generic, o) for o in lua_list(outcomes)]

deps_all = {c: set(lua_table(p).keys()) for c, p in lua_table(RA.Dependencies).items()}
deps_any = {c: set(lua_table(p).keys()) for c, p in lua_table(RA.AnyDependencies).items()}

spawn = {}
for gun, t in lua_table(APT.weaponAttachmentTablesAndChances).items():
    t = lua_table(t)
    spawn[gun] = {"required": lua_list(t.get("required")), "optionals": lua_list(t.get("optionals"))}
mount_codes = lua_table(APT.requiredAttachmentsForAttachments)

tooltips = {k: lua_list(v) if not isinstance(v, str) else [v] for k, v in lua_table(TT.tooltipsPergun).items()}
states = lua_table(G.GunsOfTien_TooltipStates) if G.GunsOfTien_TooltipStates else {}
states = {k: lua_list(v) for k, v in states.items()}

# ---------------------------------------------------------------------------------------------------------------
# Per gun
# ---------------------------------------------------------------------------------------------------------------
parts_on = defaultdict(set)      # gun -> parts whose MountOn lists it
for part, guns in mount_on.items():
    if item_kind(part) != "base:weaponpart":
        continue
    for g in guns:
        parts_on[g].add(part)

guns = sorted(t for t, f in items.items() if (f.get("itemtype") or "").lower() == "base:weapon"
              and (f.get("subcategory", "").lower() == "firearm" or "ammotype" in f or "magazinetype" in f)
              and not t.startswith("Base."))

SIDES = ["Up", "Down", "Left", "Right"]
RAIL = {s: "MarzGuns.Picatinny_Rail_" + s for s in SIDES}
MOUNTS = ["MarzGuns.AK_Mount", "MarzGuns.Sniper_Mount", "MarzGuns.Beretta_Mount", "MarzGuns.Colt_Mount",
          "MarzGuns.Heavy_Pistol_Rail"]
OPTICS_PARENTS = deps_any.get("MarzGuns.Aimpoint_Sight", set())


def category(part):
    pt = (items.get(part, {}).get("parttype") or "")
    p = part.lower()
    if pt in ("Canon", "CanonMount") or any(k in p for k in ("suppressor", "muzzle", "compensator", "flash")):
        return "muzzle"
    if "bayonet" in p:
        return "bayonet"
    if pt in ("Scope", "Sight") or "_sight" in p or "_scope" in p:
        return "optic"
    if "foregrip" in p:
        return "foregrip"
    if "bipod" in p:
        return "bipod"
    if "light" in p:
        return "light"
    if "laser" in p:
        return "laser"
    if "picatinny_rail" in p or "integrated_rail" in p or p.endswith("_mount"):
        return "rail"
    return "other"


def side_of_parent(parent):
    for s in SIDES:
        if parent.endswith("_" + s) or parent.endswith("Rail_" + s):
            return s
    return None


def mags_of(gun):
    prof = lua_table(MAG.WeaponMagazineProfile).get(gun)
    if not prof:
        return []
    return sorted(lua_list(lua_table(MAG.MagazineProfiles).get(prof)) or [])


report = {}
for gun in guns:
    integrated = set(spawn.get(gun, {}).get("required", []))
    fittable = set()
    candidates = set(parts_on[gun])
    # fixpoint: a part is fittable when its parents are integrated or fittable
    changed = True
    while changed:
        changed = False
        for p in sorted(candidates - fittable):
            have = integrated | fittable
            if deps_all.get(p) and not deps_all[p] <= have:
                continue
            if deps_any.get(p) and not (deps_any[p] & have):
                continue
            fittable.add(p)
            changed = True
    unfittable = candidates - fittable
    sides = {}
    for s in SIDES:
        integ = [p for p in integrated if side_of_parent(p) == s and ("Rail" in p)]
        removable = RAIL[s] in fittable
        univ = any(o == RAIL[s] for _, o in universal.get(gun, []))
        sides[s] = {"integrated": integ, "removable": removable, "universal": univ}
    by_cat = defaultdict(list)
    for p in sorted(fittable - integrated):
        by_cat[category(p)].append(p)
    # each fittable accessory: which side it hangs on
    acc_side = {}
    for p in fittable:
        parents = (deps_any.get(p, set()) | deps_all.get(p, set()))
        ss = {side_of_parent(x) for x in parents if "Rail" in x} - {None}
        mounts = {x for x in parents if x in MOUNTS}
        acc_side[p] = (sorted(ss), sorted(mounts))
    model_parts = [v.split()[0] for v in items[gun].get("modelweaponpart[]", []) if v.split()]
    invisible = sorted(p for p in fittable - integrated if p not in model_parts
                       and category(p) not in ("other",) and not items.get(p, {}).get("parttype", "").startswith("Clip"))
    spawn_bad = []
    for opt in spawn.get(gun, {}).get("optionals", []):
        bits = opt.split(":")
        part = bits[0]
        code = bits[2] if len(bits) > 2 else None
        if item_kind(part) == "base:weaponpart" and part not in fittable and code is None and "Bayonet" not in part:
            spawn_bad.append(opt)
        if code and (mount_codes.get(code) not in fittable and mount_codes.get(code) not in integrated):
            spawn_bad.append(opt + " (its rail does not fit)")
        if code and part not in parts_on[gun]:
            spawn_bad.append(opt + " (not in the part's MountOn)")
    report[gun] = {
        "name": name(gun), "sides": sides, "integrated": sorted(integrated), "fittable": sorted(fittable),
        "unfittable": sorted(unfittable), "by_cat": dict(by_cat), "acc_side": acc_side, "model_parts": model_parts,
        "invisible": invisible, "spawn_bad": spawn_bad, "tooltip": tooltips.get(gun),
        "universal": universal.get(gun, []),
        "magazines": mags_of(gun),
    }


# ---------------------------------------------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------------------------------------------
def short(p):
    return p.split(".", 1)[1]


out = []
w = out.append
w("# Attachment audit (generated by scripts/attachment_audit.py)\n")
if load_errors:
    w("\n## Lua files that did not load in the harness (their registrations are missing below)\n")
    for e in load_errors:
        w("- %s" % e)
for scope, prefix in (("Guns of Tien", "GunsOfTien."), ("Post-93", "GunsOfTienPost93."), ("Guns of Marz", "MarzGuns.")):
    w("\n## %s\n" % scope)
    for gun in guns:
        if not gun.startswith(prefix):
            continue
        r = report[gun]
        w("\n### %s (`%s`)\n" % (r["name"], gun))
        rails = []
        for s in SIDES:
            d = r["sides"][s]
            kind = []
            if d["integrated"]:
                kind.append("integrated")
            if d["removable"]:
                kind.append("rail")
            if d["universal"] and not d["removable"]:
                kind.append("UNIVERSAL ONLY (outcome not in MountOn)")
            if d["removable"] and not d["universal"]:
                kind.append("not offered by the universal rail")
            if kind:
                rails.append("%s: %s" % (s, ", ".join(kind)))
        w("- rails: %s" % ("; ".join(rails) or "none"))
        mounts = [short(p) for p in r["fittable"] if p in MOUNTS] + [short(p) for p in r["integrated"] if p in MOUNTS]
        if mounts:
            w("- mounts: %s" % ", ".join(sorted(set(mounts))))
        for cat in ("optic", "foregrip", "bipod", "light", "laser", "muzzle", "bayonet"):
            if r["by_cat"].get(cat):
                w("- %s: %s" % (cat, ", ".join(short(p) for p in r["by_cat"][cat])))
        # sides with a rail but nothing for them, accessories with no side
        for s in SIDES:
            d = r["sides"][s]
            if not (d["integrated"] or d["removable"]):
                continue
            users = [p for p, (ss, _) in r["acc_side"].items() if s in ss and category(p) != "rail"]
            if not users:
                w("- **ISSUE** %s rail: nothing fits on it" % s)
        if r["unfittable"]:
            w("- **ISSUE** in MountOn but never fittable (no parent rail / mount): %s"
              % ", ".join(short(p) for p in r["unfittable"]))
        if r["invisible"]:
            w("- **ISSUE** fittable but no ModelWeaponPart line (drawn nowhere): %s"
              % ", ".join(short(p) for p in r["invisible"]))
        if r["spawn_bad"]:
            w("- **ISSUE** spawn table: %s" % "; ".join(r["spawn_bad"]))
        if r["magazines"]:
            w("- magazines: %s" % ", ".join(name(m) for m in r["magazines"]))
        if r["tooltip"]:
            w("- tooltip: %s" % " / ".join(r["tooltip"]))
        else:
            w("- tooltip: (none)")

w("\n## Magazines (Information lines)\n")
for mag in sorted(tooltips, key=name):
    if any(line.startswith("Fits: ") for line in tooltips[mag]):
        w("- %s (`%s`): %s" % (name(mag), mag, " / ".join(tooltips[mag])))

sys.stdout.write("\n".join(out) + "\n")
if "--json" in sys.argv:
    json.dump(report, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=list)
