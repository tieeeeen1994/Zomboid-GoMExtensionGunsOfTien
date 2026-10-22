--[[
    Guns of Tien -- loot for AWC's Mk9 suppressor and its 9x19mm SMG mount device (shared/GunsOfTien/Suppressors.lua)
    and the M249

    They join the item lists of Guns of Marz's MarzGuns.World_Suppressor_Spawner (SWAT gun storage, police evidence,
    drug labs, drug shacks) and MarzGuns.World_Muzzle_Device_Spawner (gun stores, garages, SWAT and army storage), as
    Post-93's suppressors and mount devices do: each spawn picks one entry of the list, so ours are one more equal
    choice in each. The mount device also joins GoM's list for vanilla's Improved Choke Tube
    (VanillaReplacerTable.VanillaAttachmentMap, used while GoM's sandbox VanillaAttachmentReplacement is on), which GoM
    turns into one of its mount devices wherever vanilla spawns one (user, 2026-10-22: loot the same as GoM). Found
    MP5s come without a can, as GoM's guns come without its cans. Everything follows GoM's own loot and its
    LootMultiplier, which scales how often GoM places these spawners. The items are taken out again before the next
    world adds them (Lua is not always reloaded).

    The M249 Light Machine Gun spawns where GoM's M60 does (user, 2026-10-22; shared/GunsOfTien/M249.lua): an
    alternative in MarzGuns.Zombie_Army_Rifle_Spawner (the gun on army zombies' backs, beside GoM's M16 family, M14
    and M60) and in MarzGuns.World_Army_Heavy_Spawner (army storage, heavy army truck beds, beside its M79 and M60),
    packed as GoM's M60 kits there (the gun, up to 2 or 3 200-round boxes, up to 4 boxes of GoM's 5.56). Loose
    200-round boxes go into army ammunition storage at the M60 box's weights (GoM's ItemInsertion: 3 and 2), scaled by
    GoM's LootMultiplier as GoM scales its own. No civilian had one in 1993.
    Belt links (shared/GunsOfTien/BeltLinks.lua): a box of M27 links in each M249 kit and of M13 links in each of
    GoM's M60 kits (up to as many as the kit's belt boxes, a group added to GoM's own alternative), and loose boxes of
    both beside the belt boxes in army ammunition storage, at the belt boxes' weights.
--]]

require("Items/ProceduralDistributions")

-- { GoM table module, map field, key, our items }: each goes into the first alternative's first item list
local LISTS = {
    { "MarzWeapons/OnCreate/ItemSpawnerTable", "ItemSpawnerMap", "MarzGuns.World_Suppressor_Spawner",
        { "GunsOfTien.Mk9_Suppressor" } },
    { "MarzWeapons/OnCreate/ItemSpawnerTable", "ItemSpawnerMap", "MarzGuns.World_Muzzle_Device_Spawner",
        { "GunsOfTien.SMG9_Muzzle_Mount_Device" } },
    { "MarzWeapons/OnCreate/VanillaReplacerTable", "VanillaAttachmentMap", "Base.ChokeTubeImproved",
        { "GunsOfTien.SMG9_Muzzle_Mount_Device" } },
}

-- M249 kits, GoM's M60 kits in the same spawners: { spawner, belt boxes }
local M249_SPAWNERS = {
    { "MarzGuns.Zombie_Army_Rifle_Spawner", 2 },
    { "MarzGuns.World_Army_Heavy_Spawner", 3 },
}

local function m249Alternative(boxes)
    return {
        { items = { "GunsOfTien.M249" }, amountChance = 1 },
        { items = { "GunsOfTien.556x45Box200_M249" }, amountChance = boxes },
        { items = { "MarzGuns.556x45_Box" }, amountChance = 4 },
        { items = { "GunsOfTien.LinkBox_M27" }, amountChance = boxes },
    }
end

-- GoM's M60 kits get a group of M13 link boxes: { spawner, link boxes } (as many as the kit's belt boxes)
local M60_KITS = {
    { "MarzGuns.Zombie_Army_Rifle_Spawner", 2 },
    { "MarzGuns.World_Army_Heavy_Spawner", 3 },
}

local added = {}
local addedAlternatives = {}
local addedGroups = {}

local function removeAdded()
    for i = #added, 1, -1 do
        local items, item = added[i][1], added[i][2]
        for j = #items, 1, -1 do
            if items[j] == item then
                table.remove(items, j)
                break
            end
        end
    end
    added = {}
    for i = #addedAlternatives, 1, -1 do
        local list, alternative = addedAlternatives[i][1], addedAlternatives[i][2]
        for j = #list, 1, -1 do
            if list[j] == alternative then
                table.remove(list, j)
                break
            end
        end
    end
    addedAlternatives = {}
    for i = #addedGroups, 1, -1 do
        local alternative, group = addedGroups[i][1], addedGroups[i][2]
        for j = #alternative, 1, -1 do
            if alternative[j] == group then
                table.remove(alternative, j)
                break
            end
        end
    end
    addedGroups = {}
end

-- GoM's alternative in a spawner whose first group holds `gun`
local function alternativeWith(list, gun)
    for _, alternative in ipairs(list) do
        local first = type(alternative) == "table" and alternative[1]
        if type(first) == "table" and type(first.items) == "table" then
            for _, item in ipairs(first.items) do
                if item == gun then return alternative end
            end
        end
    end
    return nil
end

local function addLoot()
    removeAdded()
    for _, entry in ipairs(LISTS) do
        local ok, module = pcall(require, entry[1])
        local map = ok and type(module) == "table" and module[entry[2]]
        local list = type(map) == "table" and map[entry[3]]
        local first = type(list) == "table" and list[1]
        local group = type(first) == "table" and first[1]
        local items = type(group) == "table" and group.items
        if type(items) == "table" then
            for _, item in ipairs(entry[4]) do
                items[#items + 1] = item
                added[#added + 1] = { items, item }
            end
        else
            print("[GunsOfTien] Guns of Marz's " .. entry[3] .. " not found, our parts will not spawn there")
        end
    end
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    for _, entry in ipairs(M249_SPAWNERS) do
        local list = type(map) == "table" and map[entry[1]]
        if type(list) == "table" then
            local alternative = m249Alternative(entry[2])
            list[#list + 1] = alternative
            addedAlternatives[#addedAlternatives + 1] = { list, alternative }
        else
            print("[GunsOfTien] Guns of Marz's " .. entry[1] .. " not found, the M249 will not spawn there")
        end
    end
    for _, entry in ipairs(M60_KITS) do
        local list = type(map) == "table" and map[entry[1]]
        local alternative = type(list) == "table" and alternativeWith(list, "MarzGuns.M60")
        if alternative then
            local group = { items = { "GunsOfTien.LinkBox_M13" }, amountChance = entry[2] }
            alternative[#alternative + 1] = group
            addedGroups[#addedGroups + 1] = { alternative, group }
        else
            print("[GunsOfTien] Guns of Marz's M60 kit not found in " .. entry[1] .. ", no M13 links there")
        end
    end
end

Events.OnInitGlobalModData.Add(addLoot)

-------------------------------------------------
-- Loose 200-round boxes in army ammunition storage, as GoM's M60 box
-------------------------------------------------
local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.MarzGuns
    local value = vars and tonumber(vars.LootMultiplier)
    if not value then return 1 end
    return math.max(0, value)
end

local function addBoxes()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    for _, item in ipairs({ "GunsOfTien.556x45Box200_M249", "GunsOfTien.LinkBox_M27", "GunsOfTien.LinkBox_M13" }) do
        if ScriptManager.instance:getItem(item) then
            for name, weight in pairs({ ArmyStorageAmmunition = 3, ArmySurplusAmmoBoxes = 2 }) do
                local list = ProceduralDistributions.list[name]
                if type(list) == "table" and type(list.items) == "table" then
                    list.items[#list.items + 1] = item
                    list.items[#list.items + 1] = weight * multiplier
                end
            end
        end
    end
end

Events.OnPostDistributionMerge.Add(addBoxes)
