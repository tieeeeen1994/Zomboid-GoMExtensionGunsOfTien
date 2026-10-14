--[[
    Guns of Tien - Post-93 -- loot for the MP7A1, the P90 TR and their ammunition

    - Guns come through Guns of Marz's spawner items: a new alternative (the gun with its magazines and boxes) in
      MarzGuns.World_Anachronistic_Spawner (GoM's post-1993 guns: G36, Benelli M4, AA-12...; gun stores and late
      loot) and MarzGuns.Zombie_Police_SMG_Spawner (SWAT zombies, police bags, prison riot storage, SWAT vehicles).
      Each added alternative is taken out again before the next world adds it (Lua is not always reloaded).
    - Boxes also turn up next to vanilla 9mm boxes in police, SWAT and gun store lists, rarely.

    Scaled by the main mod's sandbox option GunsOfTien.AmmoLootMultiplier (0 = none of this).
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")

local M = "GunsOfTienPost93."

local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    local value = vars and tonumber(vars.AmmoLootMultiplier)
    if not value then return 1 end
    return math.max(0, value)
end

-------------------------------------------------
-- Gun spawners
-------------------------------------------------
local function mp7Alternative(boxes)
    return {
        { items = { M .. "MP7A1" }, amountChance = 1 },
        { items = { M .. "46x30Magazine20_MP7", M .. "46x30Magazine30_MP7", M .. "46x30Magazine40_MP7" }, amountChance = 3 },
        { items = { M .. "46x30_Box" }, amountChance = boxes },
    }
end

local function p90Alternative(boxes)
    return {
        { items = { M .. "P90TR" }, amountChance = 1 },
        { items = { M .. "57x28Magazine50_P90" }, amountChance = 3 },
        { items = { M .. "57x28_Box", M .. "57x28_Box_SS197SR" }, amountChance = boxes },
    }
end

local SPAWNERS = {
    { "MarzGuns.World_Anachronistic_Spawner", mp7Alternative, 4 },
    { "MarzGuns.World_Anachronistic_Spawner", p90Alternative, 4 },
    { "MarzGuns.Zombie_Police_SMG_Spawner", mp7Alternative, 2 },
    { "MarzGuns.Zombie_Police_SMG_Spawner", p90Alternative, 2 },
}

local added = {}

local function removeAdded()
    for i = #added, 1, -1 do
        local list, alternative = added[i][1], added[i][2]
        for j = #list, 1, -1 do
            if list[j] == alternative then
                table.remove(list, j)
                break
            end
        end
    end
    added = {}
end

local function addSpawners()
    removeAdded()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    if not map then
        print("[GunsOfTienPost93] Guns of Marz spawner table not found, the MP7A1 and P90 TR will not spawn")
        return
    end
    for _, entry in ipairs(SPAWNERS) do
        local list = map[entry[1]]
        local boxes = math.floor(entry[3] * multiplier + 0.5)
        if type(list) == "table" then
            local alternative = entry[2](boxes)
            list[#list + 1] = alternative
            added[#added + 1] = { list, alternative }
        end
    end
end

Events.OnInitGlobalModData.Add(addSpawners)

-------------------------------------------------
-- Boxes in world containers
-------------------------------------------------
local WORLD = {
    { M .. "46x30_Box", "Base.Bullets9mmBox", 0.05 },
    { M .. "46x30_Box_Subsonic", "Base.Bullets9mmBox", 0.02 },
    { M .. "57x28_Box", "Base.Bullets9mmBox", 0.05 },
    { M .. "57x28_Box_SB193", "Base.Bullets9mmBox", 0.02 },
    { M .. "57x28_Box_SS197SR", "Base.Bullets9mmBox", 0.03 },
}

local function isWantedList(name)
    local lower = string.lower(name)
    return string.find(lower, "police", 1, true) ~= nil
        or string.find(lower, "swat", 1, true) ~= nil
        or string.find(lower, "gunstore", 1, true) ~= nil
end

local function addWorldLoot()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    for _, entry in ipairs(WORLD) do
        local newItem, baseItem, share = entry[1], entry[2], entry[3] * multiplier
        local script = ScriptManager.instance:getItem(baseItem)
        if script and ScriptManager.instance:getItem(newItem) then
            local name, fullName = script:getName(), script:getFullName()
            for listName, data in pairs(ProceduralDistributions.list) do
                local items = type(listName) == "string" and type(data) == "table" and data.items
                if type(items) == "table" and isWantedList(listName) then
                    local weights = {}
                    for i = 1, #items - 1, 2 do
                        if (items[i] == name or items[i] == fullName) and type(items[i + 1]) == "number" then
                            weights[#weights + 1] = items[i + 1]
                        end
                    end
                    for _, weight in ipairs(weights) do
                        items[#items + 1] = newItem
                        items[#items + 1] = weight * share
                    end
                end
            end
        end
    end
end

Events.OnPostDistributionMerge.Add(addWorldLoot)
