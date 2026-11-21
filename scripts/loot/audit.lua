local EXTEND, OUT = ...
local GOM = [[C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media/lua/]]
local ROOT = [[C:/Users/Chen/Zomboid/Workshop/GoMExtensionGunsOfTien/Contents/mods/]]
local PZ = [[C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/lua/]]
local cache = {}
function require(name)
  if cache[name] then return cache[name] end
  if name:find("^MarzWeapons/OnCreate/") then local r = dofile(GOM .. "shared/" .. name .. ".lua"); cache[name] = r or true; return r end
  if name == "Distribution/Functions.lua" then local t = { Insert = function() end, InsertMany = function() end, RemoveMany = function() end, RemoveEverywhere = function() end, SetChance = function() end }; cache[name] = t; return t end
  cache[name] = true; return true
end
local function stub() return setmetatable({}, { __index = function(t, k) local v = stub(); rawset(t, k, v); return v end }) end
ClutterTables = stub()
BagsAndContainers = {}
local okb, eb = pcall(dofile, PZ .. "server/Items/Distribution_BagsAndContainers.lua")
dofile(PZ .. "server/Items/ProceduralDistributions.lua")
VehicleDistributions = VehicleDistributions or {}
pcall(dofile, PZ .. "server/Vehicles/VehicleDistributions.lua")
SuburbsDistributions = SuburbsDistributions or {}
dofile(PZ .. "shared/Definitions/AttachedWeaponDefinitions.lua")
for _, k in ipairs({"AmazonaSpear","StalkerKnife","PrepperHolster","HeadhunterRifle","DeadlyHeadhunterRifle","HECU_Gasmask_Rifle"}) do AttachedWeaponDefinitions[k] = AttachedWeaponDefinitions[k] or { weapons = {}, outfit = {} } end
dofile(GOM .. "shared/MarzWeapons/Definitions/AttachedWeaponDefinitions.lua")
SandboxVars = { MarzGuns = { LootMultiplier = 1, SpawnHighCapMags = true, VanillaWeaponReplacement = true }, GunsOfTien = { ExtendLootAreas = EXTEND } }
local handlers = {}
_G.__handlers = handlers
Events = setmetatable({}, { __index = function(_, k) return { Add = function(f) handlers[k] = handlers[k] or {}; table.insert(handlers[k], f) end } end })
ScriptManager = { instance = { getItem = function() return nil end } }
dofile(GOM .. "server/MarzWeapons/Distribution/ItemInsertion.lua")
assert(pcall(dofile, ROOT .. "GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/Loot.lua"))
dofile(ROOT .. "GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/ExtendLootAreas.lua")
dofile(ROOT .. "GoMExtensionGunsOfTienPost93/42/media/lua/server/GunsOfTienPost93/Loot.lua")
for _, f in ipairs(handlers.OnPreDistributionMerge or {}) do f() end
for _, f in ipairs(handlers.OnPostDistributionMerge or {}) do pcall(f) end
for _, f in ipairs(handlers.OnInitGlobalModData or {}) do f() end
for _, f in ipairs(handlers.OnLoadMapZones or {}) do f() end
local out = io.open(OUT, "w")
out:write("BAGS\t", tostring(okb), "\t", tostring(eb), "\n")
local map = require("MarzWeapons/OnCreate/ItemSpawnerTable").ItemSpawnerMap
for k, list in pairs(map) do for i, alt in ipairs(list) do if alt[1] then for _, g in ipairs(alt[1].items) do out:write("SP\t", k, "\t", #list, "\t", i, "\t", #alt[1].items, "\t", g, "\n") end end end end
local rep = require("MarzWeapons/OnCreate/VanillaReplacerTable").VanillaWeaponMap
for k, list in pairs(rep) do for i, alt in ipairs(list) do for _, g in ipairs(alt[1].items) do out:write("RP\t", k, "\t", #list, "\t", i, "\t", #alt[1].items, "\t", g, "\n") end end end
local function lists(prefix, t)
  for name, l in pairs(t) do
    if type(l) == "table" and type(l.items) == "table" then
      local rolls = l.rolls or 1
      for i = 1, #l.items - 1, 2 do out:write("PL\t", prefix, "\t", name, "\t", rolls, "\t", tostring(l.items[i]), "\t", tostring(l.items[i+1]), "\n") end
    end
  end
end
lists("pd", ProceduralDistributions.list); lists("bd", BagsAndContainers)
for name, v in pairs(VehicleDistributions) do if type(v) == "table" and type(v.items) == "table" then lists("vd", { [name] = v }) end end
for k, d in pairs(AttachedWeaponDefinitions) do
  if type(d) == "table" and type(d.weapons) == "table" and k ~= "attachedWeaponCustomOutfit" then
    out:write("SD\t", k, "\t", tostring(d.chance or 0), "\t", tostring(d.daySurvived or 0), "\t", table.concat(d.outfit or {}, ","), "\n")
    for _, w in ipairs(d.weapons) do out:write("SW\t", k, "\t", w, "\n") end
  end
end
for name, o in pairs(AttachedWeaponDefinitions.attachedWeaponCustomOutfit) do
  local ids = {}
  for _, w in ipairs(o.weapons) do for k, d in pairs(AttachedWeaponDefinitions) do if d == w then ids[#ids+1] = k end end end
  out:write("CO\t", name, "\t", tostring(o.chance), "\t", tostring(o.maxitem or 1), "\t", table.concat(ids, ","), "\n")
end
out:close()
