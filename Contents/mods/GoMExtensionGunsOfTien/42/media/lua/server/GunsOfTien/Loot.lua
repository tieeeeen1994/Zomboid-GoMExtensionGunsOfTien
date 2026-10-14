--[[
    Guns of Tien -- loot

    Two routes, the same ones Guns of Marz uses for its own ammo:

    - World containers: each box is added next to a vanilla box of the same calibre in the loot lists that hold it
      (ProceduralDistributions, the top-level SuburbsDistributions / BagsAndContainers / VehicleDistributions
      entries), at a share of that box's weight. Lists of the army, police or SWAT are skipped for loads they would
      not stock (hunting soft points, Chinese steel core). With GoM's vanilla ammo replacement on, the vanilla box
      still turns into GoM's; ours spawn beside it. Runs on OnPostDistributionMerge (sandbox options are loaded by
      then, as GoM's own loot code relies on).
    - GoM spawner items (guns on zombies and in the world come with their magazines and boxes): an extra bonus group
      is appended to the alternative whose gun fires the round, so it adds boxes instead of replacing GoM's.
      Done at OnInitGlobalModData (after the sandbox options are loaded, before any item is created).

    Sandbox GunsOfTien.AmmoLootMultiplier scales both (0 = no loot from this mod).
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")

local M = "GunsOfTien."

local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    local value = vars and tonumber(vars.AmmoLootMultiplier)
    if not value then return 1 end
    return math.max(0, value)
end

-- Loot lists that belong to the army, police or SWAT.
local function isServiceList(name)
    local lower = string.lower(name)
    return string.find(lower, "army", 1, true) ~= nil
        or string.find(lower, "police", 1, true) ~= nil
        or string.find(lower, "swat", 1, true) ~= nil
        or string.find(lower, "military", 1, true) ~= nil
end

-- { new box, vanilla box beside it, share of its weight, where }
-- where: "all", "civilian" (not army / police / SWAT) or "service" (army / police / SWAT and gun stores).
local WORLD = {
    { M .. "9x19_Box_HollowPoint", "Base.Bullets9mmBox", 0.5, "all" },
    { M .. "9x19_Box_Subsonic", "Base.Bullets9mmBox", 0.25, "service" },
    { M .. "9x19_Box_PPP", "Base.Bullets9mmBox", 0.15, "service" },
    { M .. "9x19_Carton_HollowPoint", "Base.Bullets9mmCarton", 0.5, "all" },

    { M .. "45_Box_HollowPoint", "Base.Bullets45Box", 0.5, "all" },
    { M .. "45_Box_P", "Base.Bullets45Box", 0.2, "service" },
    { M .. "45_Carton_HollowPoint", "Base.Bullets45Carton", 0.5, "all" },

    { M .. "12Gauge_Box_Birdshot", "Base.ShotgunShellsBox", 0.8, "civilian" },
    { M .. "12Gauge_Carton_Birdshot", "Base.ShotgunShellsCarton", 0.8, "civilian" },

    { M .. "3006_Box_SP", "Base.308Box", 0.4, "civilian" },
    { M .. "308_Box_SP", "Base.308Box", 0.6, "civilian" },
    { M .. "308_Carton_SP", "Base.308Carton", 0.6, "civilian" },

    -- No vanilla 7.62x39 exists; Vanilla Weapons Plus puts its 7.62x39 beside the 5.56 box the same way.
    { M .. "762x39_Box_SteelCore", "Base.556Box", 0.12, "civilian" },
    { M .. "762x39_Box_SP", "Base.556Box", 0.08, "civilian" },
}

local function wanted(where, listName)
    if where == "all" then return true end
    local service = isServiceList(listName)
    if where == "civilian" then return not service end
    if where == "service" then
        return service or string.find(string.lower(listName), "gunstore", 1, true) ~= nil
    end
    return false
end

local function insertBeside(lists, newItem, baseItem, share, where)
    local script = ScriptManager.instance:getItem(baseItem)
    if not script or not ScriptManager.instance:getItem(newItem) then return end
    local name, fullName = script:getName(), script:getFullName()
    for _, lootTable in ipairs(lists) do
        for listName, data in pairs(lootTable) do
            local items = type(listName) == "string" and type(data) == "table" and data.items
            if type(items) == "table" and wanted(where, listName) then
                -- Collected first: the list grows while this runs.
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

local function addWorldLoot()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local lists = { ProceduralDistributions.list, SuburbsDistributions, BagsAndContainers, VehicleDistributions }
    for _, entry in ipairs(WORLD) do
        insertBeside(lists, entry[1], entry[2], entry[3] * multiplier, entry[4])
    end
end

Events.OnPostDistributionMerge.Add(addWorldLoot)

-- { spawner, gun in the alternative's main group, boxes (one picked per roll), up to this many }
local SPAWNERS = {
    { "MarzGuns.Zombie_Civilian_Handgun_Spawner", "MarzGuns.M92FS", { M .. "9x19_Box_HollowPoint" }, 2 },
    { "MarzGuns.Zombie_Civilian_Handgun_Spawner", "MarzGuns.HIPOWER", { M .. "9x19_Box_HollowPoint" }, 2 },
    { "MarzGuns.Zombie_Civilian_Handgun_Spawner", "MarzGuns.M1911", { M .. "45_Box_HollowPoint" }, 2 },
    { "MarzGuns.Zombie_Civilian_Shotgun_Spawner", "MarzGuns.DOUBLEBARREL", { M .. "12Gauge_Box_Birdshot" }, 4 },
    { "MarzGuns.Zombie_Civilian_Shotgun_Spawner", "MarzGuns.MOSSBERG_590", { M .. "12Gauge_Box_Birdshot" }, 4 },
    { "MarzGuns.Zombie_Civilian_SemiRifle_Spawner", "MarzGuns.M1903", { M .. "3006_Box_SP" }, 4 },
    { "MarzGuns.Zombie_Civilian_SemiRifle_Spawner", "MarzGuns.REMINGTON_700", { M .. "308_Box_SP" }, 4 },
    { "MarzGuns.Zombie_Civilian_SemiRifle_Spawner", "MarzGuns.SKS",
        { M .. "762x39_Box_SteelCore", M .. "762x39_Box_SP" }, 3 },

    { "MarzGuns.Zombie_Police_Handgun_Spawner", "MarzGuns.M92FS",
        { M .. "9x19_Box_HollowPoint", M .. "9x19_Box_Subsonic", M .. "9x19_Box_PPP" }, 3 },
    { "MarzGuns.Zombie_Police_Handgun_Spawner", "MarzGuns.P226",
        { M .. "9x19_Box_HollowPoint", M .. "9x19_Box_Subsonic", M .. "9x19_Box_PPP" }, 3 },
    { "MarzGuns.Zombie_Police_Handgun_Spawner", "MarzGuns.VP70M",
        { M .. "9x19_Box_HollowPoint", M .. "9x19_Box_Subsonic" }, 3 },
    { "MarzGuns.Zombie_Police_SMG_Spawner", "MarzGuns.MP5", { M .. "9x19_Box_Subsonic", M .. "9x19_Box_HollowPoint" }, 3 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", "MarzGuns.M92FS",
        { M .. "9x19_Box_HollowPoint", M .. "9x19_Box_Subsonic", M .. "9x19_Box_PPP" }, 3 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", "MarzGuns.P226",
        { M .. "9x19_Box_HollowPoint", M .. "9x19_Box_Subsonic", M .. "9x19_Box_PPP" }, 3 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", "MarzGuns.USP", { M .. "45_Box_HollowPoint", M .. "45_Box_P" }, 3 },

    { "MarzGuns.Zombie_Cowboy_Rifles_Spawner", "MarzGuns.W1887", { M .. "12Gauge_Box_Birdshot" }, 2 },
    { "MarzGuns.Zombie_Hunter_SemiRifles_Spawner", "MarzGuns.M1903", { M .. "3006_Box_SP" }, 4 },
    { "MarzGuns.Zombie_Hunter_SemiRifles_Spawner", "MarzGuns.REMINGTON_700", { M .. "308_Box_SP" }, 4 },
    { "MarzGuns.Zombie_Hunter_SemiRifles_Spawner", "MarzGuns.SKS",
        { M .. "762x39_Box_SP", M .. "762x39_Box_SteelCore" }, 4 },
    { "MarzGuns.Zombie_Survivalist_Rifle_Spawner", "MarzGuns.AK47", { M .. "762x39_Box_SteelCore" }, 3 },

    { "MarzGuns.World_Russian_Rifle_Spawner", "MarzGuns.AK47", { M .. "762x39_Box_US" }, 2 },
    { "MarzGuns.World_Russian_Rifle_Spawner", "MarzGuns.ASVAL", { M .. "9x39_Box_SP6" }, 3 },
}

local function contains(list, value)
    if type(list) ~= "table" then return false end
    for _, v in ipairs(list) do
        if v == value then return true end
    end
    return false
end

-- Groups this file appended: { alternative, group }. Lua is not always reloaded between two games, so they are taken
-- out again before the next world adds its own (the loot multiplier may differ).
local added = {}

local function removeAdded()
    for i = #added, 1, -1 do
        local alternative, group = added[i][1], added[i][2]
        for j = #alternative, 1, -1 do
            if alternative[j] == group then
                table.remove(alternative, j)
                break
            end
        end
    end
    added = {}
end

local function addSpawnerLoot()
    removeAdded()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    if not map then
        print("[GunsOfTien] Guns of Marz spawner table not found, no spawner loot added")
        return
    end
    for _, entry in ipairs(SPAWNERS) do
        local spawner, gun, boxes, count = entry[1], entry[2], entry[3], entry[4]
        local amount = math.floor(count * multiplier + 0.5)
        local alternatives = map[spawner]
        if amount > 0 and type(alternatives) == "table" then
            for _, alternative in ipairs(alternatives) do
                local main = alternative[1]
                if type(main) == "table" and contains(main.items, gun) then
                    local items = {}
                    for _, box in ipairs(boxes) do
                        if ScriptManager.instance:getItem(box) then items[#items + 1] = box end
                    end
                    if #items > 0 then
                        local group = { items = items, amountChance = amount }
                        alternative[#alternative + 1] = group
                        added[#added + 1] = { alternative, group }
                    end
                end
            end
        end
    end
end

Events.OnInitGlobalModData.Add(addSpawnerLoot)
