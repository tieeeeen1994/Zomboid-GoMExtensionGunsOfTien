--[[
    Guns of Tien - Post-93 -- loot for the MP7A1, the P90 TR, the Five-seveN, the UCP Prototype and their ammunition

    - Guns come through Guns of Marz's spawner items: a new alternative (the gun with its magazines and boxes) in
      MarzGuns.World_Anachronistic_Spawner (GoM's post-1993 guns: G36, Benelli M4, AA-12...; gun stores and late
      loot) and MarzGuns.Zombie_Police_SMG_Spawner (SWAT zombies, police bags, prison riot storage, SWAT vehicles);
      the Five-seveN (FN sold it to police) in GoM's police and SWAT handgun spawners (MarzGuns.Zombie_Police_Handgun_
      Spawner, Zombie_SWAT_Handgun_Spawner), next to the Glock 17 and M92FS. Not in the Anachronistic spawner: GoM
      puts that in vanilla's late survivor safehouses, rooms in civilian homes, and neither pistol belongs in a home
      (user, 2026-10-17).
    - Direct loot entries (OnPostDistributionMerge): the UCP Prototype, an H&K evaluation sample, very rarely in
      police and SWAT cars and police bags (about a twentieth of a GoM police pistol there; it always comes with a
      magazine); the Five-seveN and the UCP, each with a magazine and a box, in survivor and bandit zombies' late bags,
      at the share each gun of the Anachronistic spawner gets there (the user kept them in those bags).
      Each added alternative is taken out again before the next world adds it (Lua is not always reloaded).
    - Suppressors and mount devices join the item lists of GoM's MarzGuns.World_Suppressor_Spawner (SWAT gun storage,
      police evidence, drug labs, drug shacks) and MarzGuns.World_Muzzle_Device_Spawner (gun stores, garages, SWAT and
      army storage): each spawn picks one entry of the list, so ours are two more equal choices in each.
    - Standard boxes and cartons (4.6x30mm DM11, 5.7x28mm SS190) turn up next to vanilla 9mm boxes and cartons in
      police, SWAT and gun store lists, rarely. The special loads (4.6x30mm Subsonic, 5.7x28mm SB193 and SS197SR) never
      spawn as loot, as GoM never spawns its own (its 5.56 Hollow Point / Armor Piercing / Subsonic / Overpressured):
      they come from Ammo Maker (user, 2026-10-17).
    - High-capacity magazines (MP7 40 and 60 drum, Five-seveN 30, UCP drum) also on their own, each with boxes, as
      new alternatives of GoM's MarzGuns.World_HighCap_Tactical_Magazine_Spawner (with its M92FS / M93R / MP5 drums).
    Everything that can spawn follows GoM (user, 2026-10-17: "everything needs to be lootable the same as GoM").
    Like GoM's own, the crates (4 cartons) never spawn: they are only packed.

    Scaled by Guns of Marz's own sandbox option MarzGuns.LootMultiplier ("GoM Loot Multiplier", user 2026-10-17: no
    option of our own): it already scales how often GoM places its spawners, which carry our guns, magazines and
    parts; our own entries (boxes and cartons, the UCP's police entries, the survivor / bandit bag entries) are scaled
    by it the way GoM scales its insertions. Spawner contents keep fixed counts, as GoM's own alternatives do.
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")

local M = "GunsOfTienPost93."

local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.MarzGuns
    local value = vars and tonumber(vars.LootMultiplier)
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
        { items = { M .. "57x28_Box" }, amountChance = boxes },
    }
end

-- MarzGuns.FIVESEVEN, as GoM's police pistols come (4 magazines, 4 boxes); the 30-round only on found guns (5%).
local function fivesevenAlternative(boxes)
    return {
        { items = { "MarzGuns.FIVESEVEN" }, amountChance = 1 },
        { items = { M .. "57x28Magazine20_FIVESEVEN" }, amountChance = 4 },
        { items = { M .. "57x28_Box" }, amountChance = boxes },
    }
end

-- High-capacity magazines on their own, as GoM's in its World_HighCap_Tactical_Magazine_Spawner (its M92FS 50, M93R
-- 60, MP5 60 / 100 drums: the magazine and up to two boxes; SWAT / police storage and gun stores, no homes; only with
-- GoM's sandbox SpawnHighCapMags on, which places that spawner).
local function highCap(mag, box)
    return function()
        return {
            { items = { mag }, amountChance = 1 },
            { items = { box }, amountChance = 2 },
        }
    end
end

local SPAWNERS = {
    { "MarzGuns.World_Anachronistic_Spawner", mp7Alternative, 4 },
    { "MarzGuns.World_Anachronistic_Spawner", p90Alternative, 4 },
    { "MarzGuns.Zombie_Police_SMG_Spawner", mp7Alternative, 2 },
    { "MarzGuns.Zombie_Police_SMG_Spawner", p90Alternative, 2 },
    { "MarzGuns.Zombie_Police_Handgun_Spawner", fivesevenAlternative, 4 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", fivesevenAlternative, 4 },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_MP7", M .. "46x30_Box"), 0 },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine60_MP7", M .. "46x30_Box"), 0 },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "57x28Magazine30_FIVESEVEN", M .. "57x28_Box"), 0 },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_UCP", M .. "46x30_Box"), 0 },
}

-- Parts added to the item list of a GoM spawner's first alternative.
local PART_SPAWNERS = {
    { "MarzGuns.World_Suppressor_Spawner",
        { M .. "MP7_Suppressor", M .. "P90_Suppressor", M .. "FIVESEVEN_Suppressor" } },
    { "MarzGuns.World_Muzzle_Device_Spawner", { M .. "MP7_Muzzle_Mount_Device", M .. "P90_Muzzle_Mount_Device" } },
}

local added = {}
local addedParts = {}

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
    for i = #addedParts, 1, -1 do
        local items, item = addedParts[i][1], addedParts[i][2]
        for j = #items, 1, -1 do
            if items[j] == item then
                table.remove(items, j)
                break
            end
        end
    end
    addedParts = {}
end

local function addSpawners()
    removeAdded()
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    if not map then
        print("[GunsOfTienPost93] Guns of Marz spawner table not found, the Post-93 guns will not spawn")
        return
    end
    for _, entry in ipairs(SPAWNERS) do
        local list = map[entry[1]]
        local boxes = entry[3]
        if type(list) == "table" then
            local alternative = entry[2](boxes)
            list[#list + 1] = alternative
            added[#added + 1] = { list, alternative }
        end
    end
    for _, entry in ipairs(PART_SPAWNERS) do
        local list = map[entry[1]]
        local first = type(list) == "table" and list[1]
        local group = type(first) == "table" and first[1]
        local items = type(group) == "table" and group.items
        if type(items) == "table" then
            for _, item in ipairs(entry[2]) do
                items[#items + 1] = item
                addedParts[#addedParts + 1] = { items, item }
            end
        else
            print("[GunsOfTienPost93] " .. entry[1] .. " not found, its parts will not spawn there")
        end
    end
end

Events.OnInitGlobalModData.Add(addSpawners)

-------------------------------------------------
-- Boxes and cartons in world containers
-------------------------------------------------
-- Beside vanilla's 9mm box / carton (GoM's own boxes and cartons come in place of or beside vanilla ones), only in
-- police, SWAT and gun store lists: no civilian homes. Every loot table (procedural rooms, vehicles, bags, the top-level
-- suburbs lists), as GoM's Distribution.Insert does.
local WORLD = {
    { M .. "46x30_Box", "Base.Bullets9mmBox", 0.05 },
    { M .. "57x28_Box", "Base.Bullets9mmBox", 0.05 },
    { M .. "46x30_Carton", "Base.Bullets9mmCarton", 0.05 },
    { M .. "57x28_Carton", "Base.Bullets9mmCarton", 0.05 },
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
    local tables = { ProceduralDistributions.list, VehicleDistributions, BagsAndContainers, SuburbsDistributions }
    for _, entry in ipairs(WORLD) do
        local newItem, baseItem, share = entry[1], entry[2], entry[3] * multiplier
        local script = ScriptManager.instance:getItem(baseItem)
        if script and ScriptManager.instance:getItem(newItem) then
            local name, fullName = script:getName(), script:getFullName()
            for _, lootTable in ipairs(tables) do
                for listName, data in pairs(lootTable) do
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
end

Events.OnPostDistributionMerge.Add(addWorldLoot)

-------------------------------------------------
-- Direct entries: the UCP in police / SWAT loot, both pistols in survivor and bandit bags
-------------------------------------------------
-- GoM's Anachronistic spawner sits in SurvivorBag_Late at 2 and BanditBag_Late at 1 and picks one of its 7 guns
-- evenly, so each gets 2/7 and 1/7 there; GoM's police pistol spawner sits in police glove boxes at 12 (seats 8, bags
-- 6) for about 4 pistols, so a twentieth of one of those is ~0.15.
local SURVIVOR, BANDIT = 2 / 7, 1 / 7
local DIRECT = {
    { "vehicle", "PoliceGloveBox", M .. "UCP", 0.15 },
    { "vehicle", "PoliceSeatFront", M .. "UCP", 0.1 },
    { "vehicle", "PoliceSWATGloveBox", M .. "UCP", 0.15 },
    { "vehicle", "PoliceSWATSeatFront", M .. "UCP", 0.1 },
    { "bag", "Bag_Police", M .. "UCP", 0.08 },
}
for _, kit in ipairs({
    { "MarzGuns.FIVESEVEN", M .. "57x28Magazine20_FIVESEVEN", M .. "57x28_Box" },
    { M .. "UCP", M .. "46x30Magazine20_UCP", M .. "46x30_Box" } }) do
    for _, item in ipairs(kit) do
        DIRECT[#DIRECT + 1] = { "bag", "SurvivorBag_Late", item, SURVIVOR }
        DIRECT[#DIRECT + 1] = { "bag", "BanditBag_Late", item, BANDIT }
    end
end

local function addDirectLoot()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    for _, entry in ipairs(DIRECT) do
        local where, name, item, weight = entry[1], entry[2], entry[3], entry[4]
        local list = (where == "vehicle" and VehicleDistributions or BagsAndContainers)[name]
        if type(list) == "table" and type(list.items) == "table" and ScriptManager.instance:getItem(item) then
            list.items[#list.items + 1] = item
            list.items[#list.items + 1] = weight * multiplier
        end
    end
end

Events.OnPostDistributionMerge.Add(addDirectLoot)
