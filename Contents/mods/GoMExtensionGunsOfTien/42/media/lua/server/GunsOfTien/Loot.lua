--[[
    Guns of Tien -- loot for AWC's Mk9 suppressor and its 9x19mm SMG mount device (shared/GunsOfTien/Suppressors.lua)

    They join the item lists of Guns of Marz's MarzGuns.World_Suppressor_Spawner (SWAT gun storage, police evidence,
    drug labs, drug shacks) and MarzGuns.World_Muzzle_Device_Spawner (gun stores, garages, SWAT and army storage), as
    Post-93's suppressors and mount devices do: each spawn picks one entry of the list, so ours are one more equal
    choice in each. The mount device also joins GoM's list for vanilla's Improved Choke Tube
    (VanillaReplacerTable.VanillaAttachmentMap, used while GoM's sandbox VanillaAttachmentReplacement is on), which GoM
    turns into one of its mount devices wherever vanilla spawns one (user, 2026-10-22: loot the same as GoM). Found
    MP5s come without a can, as GoM's guns come without its cans. Everything follows GoM's own loot and its
    LootMultiplier, which scales how often GoM places these spawners. The items are taken out again before the next
    world adds them (Lua is not always reloaded).
--]]

-- { GoM table module, map field, key, our items }: each goes into the first alternative's first item list
local LISTS = {
    { "MarzWeapons/OnCreate/ItemSpawnerTable", "ItemSpawnerMap", "MarzGuns.World_Suppressor_Spawner",
        { "GunsOfTien.Mk9_Suppressor" } },
    { "MarzWeapons/OnCreate/ItemSpawnerTable", "ItemSpawnerMap", "MarzGuns.World_Muzzle_Device_Spawner",
        { "GunsOfTien.SMG9_Muzzle_Mount_Device" } },
    { "MarzWeapons/OnCreate/VanillaReplacerTable", "VanillaAttachmentMap", "Base.ChokeTubeImproved",
        { "GunsOfTien.SMG9_Muzzle_Mount_Device" } },
}

local added = {}

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
end

Events.OnInitGlobalModData.Add(addLoot)
