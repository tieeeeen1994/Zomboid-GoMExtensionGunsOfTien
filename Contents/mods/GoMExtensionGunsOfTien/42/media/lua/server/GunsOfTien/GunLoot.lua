--[[
    Guns of Tien -- sandbox GunsOfTien.GunLootPercent, "Gun Loot (%)" (0 to 200, 100 by default; user, 2026-11-21: "a
    sandbox option integer of 0 to 200 where it can affect the loot spawns globally. 0 being no guns spawn at all and
    200 doubling"): every gun, whichever mod it comes from, in containers and on zombies.

    A gun entry is a Guns of Marz gun spawner (a key of its ItemSpawnerMap that is no magazine, part or ordnance
    spawner) or any item whose script `isRanged()` (vanilla's guns, which GoM may replace, GoM's, ours, other mods'),
    except vanilla's toy cap guns (DisplayCategory Memento).
    Magazines, ammunition and parts are left alone.
    - Containers: at OnPostDistributionMerge (after GoM's and our insertions and Extend Loot Areas' weights) every gun
      entry's weight in every loot table (procedural, vehicle, bag and room lists, nested tables and junk lists, each
      table and each items array once: several bag lists share one items array) is multiplied by the percentage. ItemPickerJava rolls each item of a list on its own with a chance
      that grows with its weight (Rand.Next(10000) < getActualSpawnChance), so 200 about doubles a gun's chance (up to
      the roll's own cap) and 0 never spawns it. Like GoM's LootMultiplier this is read at the merge, which IsoWorld.init
      runs before SandboxOptions.load: a dedicated server has its sandbox loaded by then, single player continuing a
      save may still hold the previous session's values.
    - Zombies (Java AttachedWeaponDefinitions.addRandomAttachedWeapon picks a slot weighted by the slots' `chance`,
      then one of its weapons evenly): a slot whose weapons are all guns has its chance scaled (0 = never picked;
      OutfitRNG.Next(0) is 0 through LocationRNG.nextInt, so a list whose slots all weigh 0 gives nothing, no error);
      a slot that mixes guns with melee weapons (the bandits' and survivalists' back slots) loses that share of its gun
      entries, or gets copies of them above 100. Applied at OnLoadMapZones, after both mods' OnInitGlobalModData
      additions; undone at the next OnPreDistributionMerge, which IsoWorld.init fires before OnInitGlobalModData, so
      the other files' own undo finds their entries where they left them.
    100 changes nothing.
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")
require("Definitions/AttachedWeaponDefinitions")

local function factor()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    local value = vars and tonumber(vars.GunLootPercent)
    if not value then return 1 end
    return math.max(0, math.min(200, value)) / 100
end

local NOT_GUN_SPAWNERS = { "Magazine", "Optic", "Muzzle", "Suppressor", "Foregrip", "Light", "Bayonet", "Attachment",
    "Ordnance" }

local spawnerMap = nil
local isGunCache = {}

local function isGun(name)
    if type(name) ~= "string" then return false end
    local cached = isGunCache[name]
    if cached ~= nil then return cached end
    local result = false
    if spawnerMap == nil then
        local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
        spawnerMap = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap or {}
    end
    if spawnerMap[name] ~= nil then
        result = true
        for _, word in ipairs(NOT_GUN_SPAWNERS) do
            if string.find(name, word, 1, true) then result = false end
        end
    else
        local full = string.find(name, ".", 1, true) and name or ("Base." .. name)
        local script = ScriptManager.instance and ScriptManager.instance:getItem(full)
        if script then
            local ok, ranged = pcall(function() return script:isRanged() end)
            local okC, category = pcall(function() return script:getDisplayCategory() end)
            result = ok and ranged == true and not (okC and category == "Memento")    -- not the toy cap guns
        end
    end
    isGunCache[name] = result
    return result
end

-------------------------------------------------
-- Containers
-------------------------------------------------
local function scaleTable(t, f, seen, depth)
    if type(t) ~= "table" or seen[t] or depth > 6 then return end
    seen[t] = true
    local items = t.items
    if type(items) == "table" and not seen[items] then      -- several bag lists share one items array
        seen[items] = true
        for i = 1, #items - 1, 2 do
            if type(items[i + 1]) == "number" and isGun(items[i]) then items[i + 1] = items[i + 1] * f end
        end
    end
    for k, v in pairs(t) do
        if k ~= "items" and type(v) == "table" then scaleTable(v, f, seen, depth + 1) end
    end
end

local function scaleContainers()
    isGunCache = {}
    spawnerMap = nil
    local f = factor()
    if f == 1 then return end
    local seen = {}
    for _, root in ipairs({ ProceduralDistributions and ProceduralDistributions.list, VehicleDistributions,
                            BagsAndContainers, SuburbsDistributions }) do
        scaleTable(root, f, seen, 0)
    end
end

Events.OnPostDistributionMerge.Add(scaleContainers)

-------------------------------------------------
-- Zombies
-------------------------------------------------
local changedChances = {}   -- { slot definition, chance before }
local removedEntries = {}   -- { weapons list, index, value }, in removal order
local addedEntries = {}     -- { weapons list, value }

local function undoZombies()
    for i = #addedEntries, 1, -1 do
        local list, value = addedEntries[i][1], addedEntries[i][2]
        for j = #list, 1, -1 do
            if list[j] == value then
                table.remove(list, j)
                break
            end
        end
    end
    for i = #removedEntries, 1, -1 do
        local entry = removedEntries[i]
        table.insert(entry[1], math.min(entry[2], #entry[1] + 1), entry[3])
    end
    for i = #changedChances, 1, -1 do
        changedChances[i][1].chance = changedChances[i][2]
    end
    changedChances, removedEntries, addedEntries = {}, {}, {}
end

local function scaleZombies()
    undoZombies()
    local f = factor()
    if f == 1 or type(AttachedWeaponDefinitions) ~= "table" then return end
    local seen = {}
    for name, definition in pairs(AttachedWeaponDefinitions) do
        local weapons = name ~= "attachedWeaponCustomOutfit" and type(definition) == "table" and not seen[definition]
            and definition.weapons
        if type(definition) == "table" then seen[definition] = true end
        if type(weapons) == "table" and #weapons > 0 then
            local guns = {}
            for i, weapon in ipairs(weapons) do
                if isGun(weapon) then guns[#guns + 1] = i end
            end
            if #guns == #weapons then
                if type(definition.chance) == "number" then
                    changedChances[#changedChances + 1] = { definition, definition.chance }
                    definition.chance = math.floor(definition.chance * f + 0.5)
                end
            elseif #guns > 0 and f < 1 then
                for n = 1, math.floor(#guns * (1 - f) + 0.5) do      -- the last gun entries first
                    local index = guns[#guns - n + 1]
                    removedEntries[#removedEntries + 1] = { weapons, index, weapons[index] }
                    table.remove(weapons, index)
                end
            elseif #guns > 0 and f > 1 then
                local values = {}
                for _, index in ipairs(guns) do values[#values + 1] = weapons[index] end
                for n = 1, math.floor(#guns * (f - 1) + 0.5) do
                    local value = values[(n - 1) % #values + 1]
                    weapons[#weapons + 1] = value
                    addedEntries[#addedEntries + 1] = { weapons, value }
                end
            end
        end
    end
    -- The outfits with weapon lists of their own (police, bandits, hunters...) also roll for anything less often below
    -- 100 and more often above it (by the square root, since the slots' chances are scaled too; at most every time):
    -- inside a list made mostly of gun slots, scaling the slots' chances alone changes little.
    local outfits = AttachedWeaponDefinitions.attachedWeaponCustomOutfit
    if f ~= 1 and type(outfits) == "table" then
        local done = {}
        for _, outfit in pairs(outfits) do
            if type(outfit) == "table" and not done[outfit] and type(outfit.chance) == "number"
                    and type(outfit.weapons) == "table" then
                done[outfit] = true
                local hasGun = false
                for _, slot in ipairs(outfit.weapons) do
                    for _, weapon in ipairs(type(slot) == "table" and type(slot.weapons) == "table" and slot.weapons or {}) do
                        if isGun(weapon) then hasGun = true end
                    end
                end
                if hasGun then
                    changedChances[#changedChances + 1] = { outfit, outfit.chance }
                    outfit.chance = math.min(100, math.floor(outfit.chance * math.sqrt(f) + 0.5))
                end
            end
        end
    end
end

Events.OnLoadMapZones.Add(scaleZombies)
Events.OnPreDistributionMerge.Add(undoZombies)
