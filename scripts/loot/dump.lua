local EXTEND = ...
local GOM = [[C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722134990/mods/GunsOfMarz/42.16/media/lua/shared/]]
-- the repo's Contents/mods, from this file's own path (it was written with one machine's absolute path)
local ROOT = debug.getinfo(1, "S").source:sub(2):gsub("\\", "/"):match("^(.*)/[^/]*$") .. "/../../Contents/mods/"
local PZ = [[C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/lua/shared/]]
local cache = {}
function require(name)
  if cache[name] then return cache[name] end
  if name:find("^MarzWeapons/OnCreate/") then local r = dofile(GOM .. name .. ".lua"); cache[name] = r or true; return r end
  -- our own shared tables (the main mod's Loot.lua reads GunsOfTien/MuzzleDevicesTable since 3.21.0)
  for _, mod in ipairs({ "GoMExtensionGunsOfTien", "GoMExtensionGunsOfTienPost93" }) do
    local f = io.open(ROOT .. mod .. "/42/media/lua/shared/" .. name .. ".lua")
    if f then f:close(); local r = dofile(ROOT .. mod .. "/42/media/lua/shared/" .. name .. ".lua"); cache[name] = r or true; return r end
  end
  cache[name] = true; return true
end
local auto = { __index = function(t, k) local v = { items = {} }; rawset(t, k, v); return v end }
ProceduralDistributions = { list = setmetatable({}, auto) }
VehicleDistributions = setmetatable({}, auto)
BagsAndContainers = setmetatable({}, auto)
SuburbsDistributions = {}
dofile(PZ .. "Definitions/AttachedWeaponDefinitions.lua")
for _, k in ipairs({"AmazonaSpear","StalkerKnife","PrepperHolster","HeadhunterRifle","DeadlyHeadhunterRifle","HECU_Gasmask_Rifle"}) do AttachedWeaponDefinitions[k] = AttachedWeaponDefinitions[k] or { weapons = {}, outfit = {"(UndeadSurvivors/HECU)"} } end
dofile(GOM .. "MarzWeapons/Definitions/AttachedWeaponDefinitions.lua")
SandboxVars = { MarzGuns = { LootMultiplier = 1 }, GunsOfTien = { ExtendLootAreas = EXTEND } }
local handlers = {}
Events = setmetatable({}, { __index = function(_, k) return { Add = function(f) handlers[k] = handlers[k] or {}; table.insert(handlers[k], f) end } end })
ScriptManager = { instance = { getItem = function() return nil end } }
assert(pcall(dofile, ROOT .. "GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/Loot.lua"))
dofile(ROOT .. "GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/ExtendLootAreas.lua")
dofile(ROOT .. "GoMExtensionGunsOfTienPost93/42/media/lua/server/GunsOfTienPost93/Loot.lua")
for _, f in ipairs(handlers.OnInitGlobalModData or {}) do f() end
for _, f in ipairs(handlers.OnPreDistributionMerge or {}) do f() end
local out = io.open([[]] .. (select(2, ...)) .. [[]], "w")
local map = require("MarzWeapons/OnCreate/ItemSpawnerTable").ItemSpawnerMap
for k, list in pairs(map) do for _, alt in ipairs(list) do if alt[1] then for _, g in ipairs(alt[1].items) do out:write("SP\t", k, "\t", g, "\n") end end end end
local rep = require("MarzWeapons/OnCreate/VanillaReplacerTable").VanillaWeaponMap
for k, list in pairs(rep) do for _, alt in ipairs(list) do for _, g in ipairs(alt[1].items) do out:write("RP\t", k, "\t", g, "\n") end end end
for k, d in pairs(AttachedWeaponDefinitions) do
  if type(d) == "table" and type(d.weapons) == "table" and k ~= "attachedWeaponCustomOutfit" then
    for _, w in ipairs(d.weapons) do out:write("SL\t", k, "\t", w, "\t", table.concat(d.outfit or {}, ","), "\n") end
  end
end
for k, o in pairs(AttachedWeaponDefinitions.attachedWeaponCustomOutfit) do
  for _, w in ipairs(o.weapons) do out:write("CO\t", k, "\t", tostring(w.id), "\t", tostring(o.chance), "\n") end
end
for _, t in ipairs({ { "pd", ProceduralDistributions.list }, { "vd", VehicleDistributions }, { "bd", BagsAndContainers } }) do
  for name, l in pairs(t[2]) do for i = 1, #l.items - 1, 2 do out:write("PL\t", name, "\t", l.items[i], "\t", tostring(l.items[i+1]), "\n") end end
end
out:close()
