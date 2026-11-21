--[[
    Guns of Tien -- sandbox GunsOfTien.ExtendLootAreas (off by default): every gun, Guns of Marz's included, in more
    places that bend reality but still make sense in game (user, 2026-11-21: "we need to expose ALL guns").

    How zombies get guns (42.22 Java AttachedWeaponDefinitions.addRandomAttachedWeapon, read from the Lua table at the
    first zombie dressed and again only after a Lua file loads): an outfit with a custom list
    (`attachedWeaponCustomOutfit[name]`) rolls its `chance` once (else it falls to the generic path), picks a slot
    weighted by the slots' `chance` among those whose `outfit` names the zombie's, and keeps going up to `maxitem`
    only while each further roll is under `chance` again; an outfit without one rolls the sandbox's Chance of Attached
    Weapon (6% in the presets) and takes one slot among every generic one and its own. The slot's `weapons` entry is
    picked evenly; GoM's spawners there (and vanilla guns, which GoM replaces) become its guns. Kahlua tables keep
    insertion order, so GoM's AttachedWeaponDefinitions.lua (which returns at its first missing slot) adds every
    vanilla slot's guns; only the mod-only ones at its end are skipped without those mods.

    With the option (odds from a Python port of the Java over vanilla's file plus GoM's additions, 2026-11-21):
    - Armed officers (user: "we do notice officers don't have guns on them"): the Police, PoliceState, PoliceRiot,
      Police_SWAT and Sheriff_Deputy lists always roll (vanilla 40 / 50 / 60 / 60 / 50, "reduced as Police zombies are
      quite commonplace"): a police zombie carries a handgun about 65% and some gun about 88% of the time (vanilla
      19% / 28%), riot police and SWAT always.
    - Armed soldiers: the army outfits have no custom list (about 1 soldier in 55 armed); ArmyCamoGreen / Desert get
      two of rifle / holster / belt / bedroll (some gun about 88%, the rifle about 55%), Ghillie all three of rifle /
      belt / bedroll. The generic knives no longer come with them. Lists another mod made are left alone.
    - Armed bandits (user: "maybe criminals should have them too"): vanilla commented the holster out of the plain
      Bandit's list (Bandit / Early / Mid / Late armed about 6 / 20 / 39 / 48%); their lists always roll and hold both
      handgun holsters and the criminals' back rifle slot `gunOnBackCrime`, whose outfit list gets the bandits:
      about 45 / 74 / 93 / 98%.
    - Armed hunters and park rangers (generic in vanilla, about 2%): custom lists at 90, hunters two of back rifle /
      ranger holster / shoulder holster, rangers one of ranger holster / police long gun (about 90%). Survivalists and
      private militia: lists always roll, and the mid / late survivalist names join the two holsters' outfit lists,
      which vanilla limits to the early ones (early about 77%, mid and late always, militia about 94%; vanilla 25 / 8
      / 6 / 34%). Survivalist02..05 and their _Mid / _Late share the tables of the three named.
    - GoM's spawners in new places (EXTENDED_PLACES, x GoM's LootMultiplier, at OnPreDistributionMerge as GoM's own)
      and on new zombie slots (EXTENDED_SLOTS), for the guns that were found in few places or never on a zombie:
      its post-1993 guns (G36 / G36C, Benelli M4, AA-12, Rhino, MP-412; only late homes and bags) in gun stores, the
      special pawn shop list and SWAT armouries, and (that spawner mixes long guns and revolvers, so it goes on no
      zombie slot) GoM's own kits copied into the spawner of their kind (EXTENDED_COPIES): the G36 / G36C with the
      police rifles, the Benelli M4 with the police shotguns, the Rhino and MP-412 with the civilian revolvers; the AA-12 (SWAT shotgun spawner) in SWAT armouries; the short SMGs (MP5K,
      TEC-9, MAC-10, the Uzis, TMP; never on a zombie) in shoulder holsters and drug labs, drug shacks and stashes;
      the imported pistols (Hi-Power, P226, Glock 17, VP70M, USP, M93R, Glock 21, PPK...; never on a zombie) in the
      civilian and shoulder holsters; the Russian rifles (AKs, SVD, AS VAL, the RPKs, RPD, SVU...; never on a zombie)
      on criminals' backs and in mid / late survivalists' back bags; the heavy army spawner (M79, M60, M249) on
      soldiers' backs and in the bunker and light army trucks; the Double Deuce (big game rifle) on hunters' backs;
      the cowboy rifles (Winchester 1894 / 1873, M1895, 1887; only pawn shops) in gun stores' rifles, hunting
      lockers, ranger stations and mid-game homes.
    Everything added to a vanilla or GoM table is taken out again (and vanilla's chances put back) before the next
    world adds it, so turning the option off restores vanilla at the next load. Post-93's own Loot.lua adds its guns
    to more GoM spawners under the same option.
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")
require("Definitions/AttachedWeaponDefinitions")

local function extendLootAreas()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.ExtendLootAreas == true
end

local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.MarzGuns
    local value = vars and tonumber(vars.LootMultiplier)
    if not value then return 1 end
    return math.max(0, value)
end

local G = "MarzGuns."

-------------------------------------------------
-- Zombie outfits
-------------------------------------------------
local OUTFIT_CHANCES = {
    Police = 100, PoliceState = 100, PoliceRiot = 100, Police_SWAT = 100, Sheriff_Deputy = 100,
    Bandit = 100, Bandit_Early = 100, Bandit_Mid = 100, Bandit_Late = 100,
    Survivalist = 100, Survivalist_Mid = 100, Survivalist_Late = 100, PrivateMilitia = 100,
}

-- slots added to existing custom lists
local OUTFIT_SLOTS = {
    { "Bandit", { "handgunHolster", "handgunHolsterShoulder", "gunOnBackCrime" } },
    { "Bandit_Early", { "handgunHolster", "handgunHolsterShoulder", "gunOnBackCrime" } },
    { "Bandit_Mid", { "handgunHolster", "handgunHolsterShoulder", "gunOnBackCrime" } },
    { "Bandit_Late", { "handgunHolster", "handgunHolsterShoulder", "gunOnBackCrime" } },
}

-- outfit names added to slots' outfit filters
local SURVIVALIST_LATER = {
    "Survivalist_Mid", "Survivalist02_Mid", "Survivalist03_Mid", "Survivalist04_Mid", "Survivalist05_Mid",
    "Survivalist_Late", "Survivalist02_Late", "Survivalist03_Late", "Survivalist04_Late", "Survivalist05_Late",
}
local SLOT_OUTFITS = {
    { "gunOnBackCrime", { "Bandit", "Bandit_Early", "Bandit_Mid", "Bandit_Late" } },
    { "handgunHolster", SURVIVALIST_LATER },
    { "handgunHolsterShoulder", SURVIVALIST_LATER },
}

-- custom lists made where vanilla (and every other mod) has none
local OUTFIT_LISTS = {
    ArmyCamoGreen = { chance = 100, maxitem = 2, slots = { "assaultRifleArmyOnBack", "handgunHolsterArmy", "armyBelt", "armyGreenBedroll" } },
    ArmyCamoDesert = { chance = 100, maxitem = 2, slots = { "assaultRifleArmyOnBack", "handgunHolsterArmy", "armyBelt", "armyDesertBedroll" } },
    Ghillie = { chance = 100, maxitem = 3, slots = { "rifleOnBackGhillie", "armyBelt", "armyGreenBedroll" } },
    Hunter = { chance = 90, maxitem = 2, slots = { "gunOnBackHunter", "handgunHolsterRanger", "handgunHolsterShoulder" } },
    Ranger = { chance = 90, maxitem = 1, slots = { "handgunHolsterRanger", "shotgunPolice" } },
}

-------------------------------------------------
-- GoM's spawners in new places and on new slots
-------------------------------------------------
-- { spawner, distribution ("pd" procedural, "vd" vehicle, "bd" bag), list, weight }, near GoM's own weights for
-- spawners of the kind
local EXTENDED_PLACES = {
    { G .. "World_Anachronistic_Spawner", "pd", "GunStoreGuns", 3 },
    { G .. "World_Anachronistic_Spawner", "pd", "GunStoreCases", 3 },
    { G .. "World_Anachronistic_Spawner", "pd", "PawnShopGunsSpecial", 2 },
    { G .. "World_Anachronistic_Spawner", "pd", "SWATStorageGuns", 4 },
    { G .. "Zombie_SWAT_Shotgun_Spawner", "pd", "SWATStorageGuns", 4 },
    { G .. "World_Short_SMG_Spawner", "pd", "DrugLabGuns", 4 },
    { G .. "World_Short_SMG_Spawner", "pd", "DrugShackWeapons", 4 },
    { G .. "World_Short_SMG_Spawner", "pd", "PlankStashGun", 2 },
    { G .. "World_Army_Heavy_Spawner", "pd", "ArmyBunkerStorage", 2 },
    { G .. "World_Army_Heavy_Spawner", "vd", "ArmyLightTruckBed", 2 },
    { G .. "Zombie_Cowboy_Rifles_Spawner", "pd", "GunStoreRifles", 4 },
    { G .. "Zombie_Cowboy_Rifles_Spawner", "pd", "HuntingLockers", 4 },
    { G .. "Zombie_Cowboy_Rifles_Spawner", "pd", "RangerStorageGuns", 4 },
    { G .. "Zombie_Cowboy_Rifles_Spawner", "pd", "FirearmWeapons_Mid", 3 },
}

-- { slot, spawner }: holstered guns only in holster slots, long guns only on backs
local EXTENDED_SLOTS = {
    { "handgunHolsterShoulder", G .. "World_Short_SMG_Spawner" },
    { "handgunHolster", G .. "World_Import_Pistol_Spawner" },
    { "handgunHolsterShoulder", G .. "World_Import_Pistol_Spawner" },
    { "gunOnBackCrime", G .. "World_Russian_Rifle_Spawner" },
    { "meleeInBackBag_Mid", G .. "World_Russian_Rifle_Spawner" },
    { "meleeInBackBag_Late", G .. "World_Russian_Rifle_Spawner" },
    { "assaultRifleArmyOnBack", G .. "World_Army_Heavy_Spawner" },
    { "gunOnBackHunter", G .. "World_Big_Game_Rifle_Spawner" },
    -- zombie-rare families (scripts/loot/audit.py): long guns onto back slots that outfits really use
    { "assaultRifleOnBack", G .. "Zombie_Army_Rifle_Spawner" },          -- private militia
    { "assaultRifleOnBack", G .. "World_Import_Rifle_Spawner" },
    { "huntingRifleOnBack", G .. "World_Russian_Rifle_Spawner" },
    { "gunOnBackBountyHunter", G .. "World_Import_Rifle_Spawner" },
    { "gunOnBackBountyHunter", G .. "World_Russian_Rifle_Spawner" },
    { "gunOnBackBountyHunter", G .. "Zombie_Oldies_Spawner" },
    { "meleeInBackBag_Late", G .. "Zombie_Oldies_Spawner" },
    { "meleeInBackBag_Late", G .. "Zombie_Army_Rifle_Spawner" },
    { "meleeInBackBag", G .. "Zombie_Civilian_SemiRifle_Spawner" },       -- GoM put it only on the unused
    { "gunOnBackHunter", G .. "Zombie_Civilian_SemiRifle_Spawner" },      -- gunOnBackBagSurvivalist slot
}

-- { slot, spawner, extra entries }: a slot picks one of its weapons evenly, so another entry of a spawner already there
-- raises its share (the police and SWAT SMGs, ten kits sharing one entry, on police and SWAT backs)
local EXTENDED_SLOT_COPIES = {
    { "shotgunPolice", G .. "Zombie_Police_SMG_Spawner", 1 },
    { "gunOnBackSWAT", G .. "Zombie_Police_SMG_Spawner", 1 },
    { "assaultRifleArmyOnBack", G .. "Zombie_Army_Rifle_Spawner", 1 },
    { "meleeInBackBag", G .. "World_Import_Rifle_Spawner", 2 },
    { "meleeInBackBag_Mid", G .. "World_Import_Rifle_Spawner", 2 },
    { "meleeInBackBag_Late", G .. "World_Import_Rifle_Spawner", 2 },
    { "meleeInBackBag_Mid", G .. "World_Russian_Rifle_Spawner", 2 },
    { "meleeInBackBag_Late", G .. "World_Russian_Rifle_Spawner", 2 },
    { "gunOnBackCrime", G .. "World_Russian_Rifle_Spawner", 1 },
    { "meleeInBackBag_Late", G .. "Zombie_Army_Rifle_Spawner", 1 },
    { "meleeInBackBag", G .. "Zombie_Civilian_SemiRifle_Spawner", 1 },
    { "gunOnBackHunter", G .. "World_Big_Game_Rifle_Spawner", 1 },
}

-- GoM's own kits copied into a spawner of their kind, so guns of a spawner that cannot go on a zombie slot (its
-- post-1993 one mixes long guns and revolvers) still reach zombies: { from spawner, gun, to spawner }. The G36's kit
-- gives a G36 or a G36C, as GoM's does.
local ANACHRONISTIC = G .. "World_Anachronistic_Spawner"
local EXTENDED_COPIES = {
    { ANACHRONISTIC, G .. "G36", G .. "Zombie_Police_Rifle_Spawner" },          -- SWAT and police carbines
    { ANACHRONISTIC, G .. "BENELLI_M4", G .. "Zombie_Police_Shotgun_Spawner" }, -- police shotguns
    { ANACHRONISTIC, G .. "RHINO", G .. "Zombie_Civilian_Revolver_Spawner" },  -- civilian revolvers
    { ANACHRONISTIC, G .. "MP412", G .. "Zombie_Civilian_Revolver_Spawner" },
}

-------------------------------------------------
-- Applying and undoing
-------------------------------------------------
local added = {}
local vanillaChances = {}
local madeLists = {}

local function addTo(list, value)
    for _, existing in ipairs(list) do
        if existing == value then return end
    end
    list[#list + 1] = value
    added[#added + 1] = { list, value }
end

local function removeAdded()
    for i = #added, 1, -1 do
        local list, value = added[i][1], added[i][2]
        for j = #list, 1, -1 do
            if list[j] == value then
                table.remove(list, j)
                break
            end
        end
    end
    added = {}
end

local function applyZombies()
    removeAdded()
    local extend = extendLootAreas()
    local defs = AttachedWeaponDefinitions
    local outfits = type(defs) == "table" and defs.attachedWeaponCustomOutfit
    if type(outfits) ~= "table" then return end
    for name, chance in pairs(OUTFIT_CHANCES) do
        local outfit = outfits[name]
        if type(outfit) == "table" then
            if vanillaChances[name] == nil then vanillaChances[name] = outfit.chance end
            outfit.chance = extend and chance or vanillaChances[name]
        end
    end
    for name, list in pairs(OUTFIT_LISTS) do
        if madeLists[name] and outfits[name] == madeLists[name] then outfits[name] = nil end
        madeLists[name] = nil
        if extend and outfits[name] == nil then
            local weapons = {}
            for _, slot in ipairs(list.slots) do
                if type(defs[slot]) == "table" then weapons[#weapons + 1] = defs[slot] end
            end
            if #weapons > 0 then
                local made = { chance = list.chance, maxitem = list.maxitem, weapons = weapons }
                outfits[name] = made
                madeLists[name] = made
            end
        end
    end
    if not extend then return end
    for _, entry in ipairs(OUTFIT_SLOTS) do
        local outfit = outfits[entry[1]]
        if type(outfit) == "table" and type(outfit.weapons) == "table" then
            for _, slot in ipairs(entry[2]) do
                if type(defs[slot]) == "table" then addTo(outfit.weapons, defs[slot]) end
            end
        end
    end
    for _, entry in ipairs(SLOT_OUTFITS) do
        local definition = defs[entry[1]]
        if type(definition) == "table" and type(definition.outfit) == "table" then
            for _, name in ipairs(entry[2]) do addTo(definition.outfit, name) end
        end
    end
    for _, entry in ipairs(EXTENDED_SLOTS) do
        local definition = defs[entry[1]]
        if type(definition) == "table" and type(definition.weapons) == "table" then addTo(definition.weapons, entry[2]) end
    end
    for _, entry in ipairs(EXTENDED_SLOT_COPIES) do
        local definition = defs[entry[1]]
        local weapons = type(definition) == "table" and definition.weapons
        if type(weapons) == "table" then
            for _ = 1, entry[3] do
                weapons[#weapons + 1] = entry[2]
                added[#added + 1] = { weapons, entry[2] }
            end
        end
    end
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    if type(map) ~= "table" then return end
    for _, entry in ipairs(EXTENDED_COPIES) do
        local from, to = map[entry[1]], map[entry[3]]
        local kit = nil
        for _, alternative in ipairs(type(from) == "table" and from or {}) do
            local first = type(alternative) == "table" and alternative[1]
            for _, item in ipairs(type(first) == "table" and type(first.items) == "table" and first.items or {}) do
                if item == entry[2] then kit = alternative end
            end
        end
        if kit and type(to) == "table" then
            addTo(to, kit)
        else
            print("[GunsOfTien] Extend Loot Areas: " .. entry[2] .. " or " .. entry[3] .. " not found in Guns of Marz's tables")
        end
    end
end

Events.OnInitGlobalModData.Add(applyZombies)

-- Before the merge, as GoM inserts its own spawners (OnPreDistributionMerge).
local function applyPlaces()
    if not extendLootAreas() then return end
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local distributions = { pd = ProceduralDistributions.list, vd = VehicleDistributions, bd = BagsAndContainers }
    for _, entry in ipairs(EXTENDED_PLACES) do
        local list = distributions[entry[2]] and distributions[entry[2]][entry[3]]
        if type(list) == "table" and type(list.items) == "table" then
            list.items[#list.items + 1] = entry[1]
            list.items[#list.items + 1] = entry[4] * multiplier
        end
    end
end

Events.OnPreDistributionMerge.Add(applyPlaces)

-------------------------------------------------
-- Rare guns (user, 2026-11-21: "audit each gun spawns and if they're considered still rare, expose them more")
-------------------------------------------------
-- Audited by scripts/loot/audit.py: a gun's container score is the sum over every loot list of rolls x the weight of
-- each entry that can give it x its share of that entry (a GoM spawner picks an alternative evenly, then one gun of
-- the alternative's list evenly; a vanilla gun stands for GoM's replacements of it). ItemPickerJava rolls every
-- item of a list on its own each roll (Rand.Next(10000) < its spawn chance, which grows with its weight), so weights
-- add up across lists. Two things kept guns far below the median: alternatives that share one slot among several guns
-- (GoM's M16A2 / M16A3 / M203 / CAR-15 / M4A1 kit gives an M4A1 a fifth of one slot) and spawners crowded by both
-- mods (the police SMG spawner holds ten kits).
-- 1. Shared kits split: every gun spawner alternative whose gun list holds several guns gets a copy per extra gun, so
--    each gun has the share of an alternative of its own. At OnLoadMapZones, after both mods' OnInitGlobalModData
--    additions; the copies are taken out again at the next load.
-- 2. Spawner weights raised (RARE_WEIGHTS, at OnPostDistributionMerge, after GoM's and our insertions): each factor
--    is the one the audit found lifting the spawner's guns to the median gun's container score (after the splits),
--    capped at 4. The loot lists are read into Java (ItemPickerJava.Parse) right after the merge, before any event
--    that sees the spawner additions, so the factors are worked out offline: rerun the audit after a loot change.
local NOT_GUN_SPAWNERS = { "Magazine", "Optic", "Muzzle", "Suppressor", "Foregrip", "Light", "Bayonet", "Attachment",
    "Ordnance" }

local function isGunSpawner(name)
    if type(name) ~= "string" then return false end
    for _, word in ipairs(NOT_GUN_SPAWNERS) do
        if string.find(name, word, 1, true) then return false end
    end
    return true
end

local splitCopies = {}

local function splitSharedKits()
    for i = #splitCopies, 1, -1 do
        local list, copy = splitCopies[i][1], splitCopies[i][2]
        for j = #list, 1, -1 do
            if list[j] == copy then
                table.remove(list, j)
                break
            end
        end
    end
    splitCopies = {}
    if not extendLootAreas() then return end
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    local map = ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap
    if type(map) ~= "table" then return end
    for name, list in pairs(map) do
        if isGunSpawner(name) and type(list) == "table" then
            for i = 1, #list do
                local alternative = list[i]
                local first = type(alternative) == "table" and alternative[1]
                local guns = type(first) == "table" and type(first.items) == "table" and #first.items or 0
                for _ = 2, guns do
                    local copy = {}
                    for k, group in ipairs(alternative) do copy[k] = group end
                    list[#list + 1] = copy
                    splitCopies[#splitCopies + 1] = { list, copy }
                end
            end
        end
    end
end

Events.OnLoadMapZones.Add(splitSharedKits)

-- (audit of 2026-11-21: median gun 42.2 at LootMultiplier 1; every gun reaches it with these)
local RARE_WEIGHTS = {
    [G .. "Zombie_Police_SMG_Spawner"] = 3.8,       -- MP5s, Uzi, P90s, MP7s, UMPs, Vectors, AUG Para
    [G .. "World_Import_Pistol_Spawner"] = 3.8,     -- M93R, Hi-Power, PPK, Vector SDP...
    [G .. "Zombie_Police_Handgun_Spawner"] = 3.7,   -- P226, VP70M, UCP...
    [G .. "Zombie_Police_Rifle_Spawner"] = 3.1,     -- CAR-15, XM177, HK416, SCAR-L, G36s
    [G .. "World_Import_Rifle_Spawner"] = 3.0,      -- AUG A1, SR-25, FAMAS, PSG-1, FNC...
    [G .. "Zombie_Cowboy_Rifles_Spawner"] = 2.8,    -- Winchester 1887...
    [G .. "World_Army_Heavy_Spawner"] = 2.7,        -- M79, M60, M249
    [G .. "World_Army_Rifle_Spawner"] = 2.5,        -- M16A3, M4A1, M203, HK417s, SCAR-H, Mk 11...
    [G .. "World_Russian_Rifle_Spawner"] = 1.9,     -- RPKs, RPD, SVD, SVU, SV-98 / 99, Grozas...
    [G .. "Zombie_Civilian_Handgun_Spawner"] = 1.9,
    [G .. "World_Anachronistic_Spawner"] = 1.8,     -- G36s, Benelli M4, AA-12, Rhino, MP-412
    [G .. "Zombie_Civilian_Shotgun_Spawner"] = 1.7, -- TOZ-34...
    [G .. "World_Big_Game_Rifle_Spawner"] = 1.4,    -- Double Deuce
    [G .. "World_Short_SMG_Spawner"] = 1.2,         -- Uzis, TMP, MP5K, TEC-9, MAC-10
    [G .. "Zombie_Army_Handgun_Spawner"] = 1.1,
}

local function raiseRareWeights()
    if not extendLootAreas() then return end
    for _, distribution in ipairs({ ProceduralDistributions.list, VehicleDistributions, BagsAndContainers }) do
        for _, list in pairs(distribution) do
            local items = type(list) == "table" and list.items
            if type(items) == "table" then
                for i = 1, #items - 1, 2 do
                    local factor = RARE_WEIGHTS[items[i]]
                    if factor and type(items[i + 1]) == "number" then items[i + 1] = items[i + 1] * factor end
                end
            end
        end
    end
end

Events.OnPostDistributionMerge.Add(raiseRareWeights)
