--[[
    Guns of Tien - Post-93 -- loot for the MP7A1 and MP7A2, the P90 TR and PS90, the Five-seveN, the UCP Prototype, the SCAR-L and
    SCAR-H, the UMP45 and UMP9, the Steyr AUG A3, Para and HBAR, the KRISS Vector .45, 9mm, CRB and SDP, the MDRx .223
    and .308, the Mk 11, the HK416, the HK416 .22 pistol, the HK417s, the Grozas, the SV-98 and SV-99, and their
    ammunition

    How Guns of Marz's loot works (traced 2026-11-21 in GoM's ItemInsertion.lua, ItemSpawner.lua,
    ZombieAttachmentReplacer.lua and AttachedWeaponDefinitions.lua): GoM puts ~45 spawner items (scripts with
    `OnCreate = MarzGuns_OnCreate.SelectItem`) into vanilla loot lists with a weight (x its LootMultiplier) and into
    vanilla zombie attachment slots. A created spawner looks itself up by full type in
    `ItemSpawnerMap`, picks one of its alternatives **evenly** (`r:random(#entry)`), and becomes the alternative's
    gun plus 1..maxAmountChance of each later group (magazines, boxes). On zombies the same lookup runs on attached
    items and on the inventory at death. So adding an alternative to a GoM spawner adds no guns to the world: it only
    splits that spawner's slot once more. Until 2026-11-21 most Post-93 guns were alternatives in GoM's
    World_Anachronistic_Spawner (21 alternatives, placed only in FirearmWeapons_Late, SafehouseBin_Late,
    SurvivorBag_Late and BanditBag_Late, on no zombie), its police SMG spawner (10) and army rifle spawners (9 / 11),
    so each was rare and GoM's own guns there were diluted.

    Since 2026-11-21 (user: "we can do both"; "whatever suits reality"):
    - Spawners of our own (items_spawners.txt), resolved by GoM's SelectItem because they are in its ItemSpawnerMap.
      Each is placed where the GoM spawner of the same kind of gun is, at that spawner's weight there (x GoM's
      LootMultiplier), so they add guns instead of diluting GoM's:
      - Zombie_SWAT_PDW_Spawner (law-enforcement SMGs: MP7s, P90 TR, UMP45, UMP9, Vector .45 and 9mm, AUG Para) where
        GoM's police SMG spawner is (Bag_Police, PrisonRiotStorage, SWAT truck bed and rear seat, the SWAT back slot),
        plus SWATStorageGuns, where GoM puts no gun spawner, at the 10 GoM gives its police shotgun spawner in
        PoliceStorageGuns.
      - World_ / Zombie_Modern_Army_Rifle_Spawner (SCAR-L, SCAR-H, HK416, HK417s, Mk 11) where GoM's army rifle
        spawners are, except FirearmWeapons_Late (civilian homes: no select-fire rifles there).
      - World_Modern_Sporting_Rifle_Spawner (rifles sold to civilians: MDRx .223 and .308, the AUG A3 and the AUG
        HBAR with it (user: "in line with AUG family"), PS90, Vector CRB, HK416 .22, plus GoM's Benelli M4, sold to
        civilians too) where GoM's import rifle spawner is, plus GoM's Anachronistic places (late homes and survivor /
        bandit bags) and the survivalist back slot.
      - World_Modern_Pistol_Spawner (Five-seveN, Vector SDP, plus GoM's Chiappa Rhino) where GoM's import pistol
        spawner is, plus the late survivor and bandit bags (it replaces the Five-seveN / UCP direct bag entries; the
        UCP was never sold, so it is police and SWAT only).
      - World_Post_Soviet_Spawner (Grozas, SV-98, SV-99, plus GoM's MP-412 REX, none of them sold in the US) where GoM's
        Russian rifle spawner is, plus the mercenary rifle slots (Undead Survivors' outfits).
      GoM's own guns are copied from its tables (the alternative whose gun list holds them), so their packing follows
      GoM's updates; they also stay in GoM's Anachronistic spawner.
    - GoM's spawners, where one fits a gun: the Five-seveN and the UCP in its police and SWAT handgun spawners (beside
      the Glock 17 and M92FS, user 2026-10-17), the SV-98 also in its mercenary sniper spawner, high-capacity
      magazines in its high-capacity magazine spawners, suppressors and mount devices in its part spawners.
    - Each alternative added to a GoM spawner is taken out again before the next world adds it (Lua is not always
      reloaded); our own map entries are simply set again.
    - Suppressors and mount devices join the item lists of GoM's MarzGuns.World_Suppressor_Spawner (SWAT gun storage,
      police evidence, drug labs, drug shacks) and MarzGuns.World_Muzzle_Device_Spawner (gun stores, garages, SWAT and
      army storage): each spawn picks one entry of the list, so ours are two more equal choices in each. The mount
      devices also join GoM's list for vanilla's Improved Choke Tube (VanillaReplacerTable.VanillaAttachmentMap, used
      while GoM's sandbox VanillaAttachmentReplacement is on), which GoM turns into one of its mount devices.
    - Standard boxes and cartons (4.6x30mm DM11) turn up next to vanilla 9mm boxes and cartons in police, SWAT and gun
      store lists, rarely. The special loads (4.6x30mm Subsonic, 5.7x28mm SB193 and SS197SR) never spawn as loot, as
      GoM never spawns its own: they come from Ammo Maker (user, 2026-10-17). The 5.7x28mm SS190 and .22 LR boxes and
      cartons are the main mod's loot.
    Like GoM's own, the crates (4 cartons) never spawn: they are only packed.

    Scaled by Guns of Marz's own sandbox option MarzGuns.LootMultiplier ("GoM Loot Multiplier", user 2026-10-17: no
    option of our own), as GoM scales its spawner placements. Spawner contents keep fixed counts, as GoM's do.
--]]

require("Items/ProceduralDistributions")
require("Vehicles/VehicleDistributions")
require("Items/Distribution_BagsAndContainers")
require("Definitions/AttachedWeaponDefinitions")

local M = "GunsOfTienPost93."

local function lootMultiplier()
    local vars = SandboxVars and SandboxVars.MarzGuns
    local value = vars and tonumber(vars.LootMultiplier)
    if not value then return 1 end
    return math.max(0, value)
end

local function spawnerMap()
    local ok, spawnerTable = pcall(require, "MarzWeapons/OnCreate/ItemSpawnerTable")
    return ok and type(spawnerTable) == "table" and spawnerTable.ItemSpawnerMap or nil
end

-------------------------------------------------
-- Alternatives (the gun, then its magazines and boxes)
-------------------------------------------------
local function kit(guns, mags, magCount, boxes, boxCount)
    local alternative = { { items = guns, maxAmountChance = 1 } }
    if mags then alternative[#alternative + 1] = { items = mags, maxAmountChance = magCount } end
    alternative[#alternative + 1] = { items = boxes, maxAmountChance = boxCount }
    return alternative
end

-- Law enforcement SMGs, as GoM's MP5 kit carries its 30: up to 3 magazines and n boxes.
local function mp7(boxes)
    return kit({ M .. "MP7A1", M .. "MP7A2" },     -- one of the two, as GoM's MP5 / MP5A2 / MP5SD
        { M .. "46x30Magazine20_MP7", M .. "46x30Magazine30_MP7", M .. "46x30Magazine40_MP7" }, 3, { M .. "46x30_Box" }, boxes)
end
local function p90tr(boxes)
    return kit({ M .. "P90TR" }, { M .. "57x28Magazine50_P90" }, 3, { M .. "57x28_Box" }, boxes)
end
local function ump45(boxes)
    return kit({ M .. "UMP45" }, { M .. "45Magazine25_UMP" }, 3, { "MarzGuns.45_Box" }, boxes)
end
local function ump9(boxes)
    return kit({ M .. "UMP9" }, { M .. "9x19Magazine30_UMP" }, 3, { "MarzGuns.9x19_Box" }, boxes)
end
-- The Vectors with Glock's standard magazines (the main mod's Glock 21 13, GoM's Glock 17 17)
local function vector45(boxes)
    return kit({ M .. "VECTOR45" }, { "GunsOfTien.45Magazine13_GLOCK21" }, 3, { "MarzGuns.45_Box" }, boxes)
end
local function vector9(boxes)
    return kit({ M .. "VECTOR9" }, { "MarzGuns.9x19Magazine17_GLOCK" }, 3, { "MarzGuns.9x19_Box" }, boxes)
end
local function augPara(boxes)
    return kit({ M .. "AUGPARA" }, { M .. "9x19Magazine25_AUG", M .. "9x19Magazine32_AUG" }, 3, { "MarzGuns.9x19_Box" }, boxes)
end

-- Modern military rifles, as GoM's army rifles come in each spawner: the gun, up to n magazines, up to n boxes.
local function scarl(count)
    return kit({ M .. "SCARL" }, { "MarzGuns.556x45Magazine30_STANAG" }, count, { "MarzGuns.556x45_Box" }, count)
end
local function scarh(count)
    return kit({ M .. "SCARH" }, { M .. "762x51Magazine20_SCARH" }, count, { "MarzGuns.762x51_Box" }, count)
end
local function hk416(count)
    return kit({ M .. "HK416" }, { "MarzGuns.556x45Magazine30_STANAG" }, count, { "MarzGuns.556x45_Box" }, count)
end
local function hk417(count)
    return kit({ M .. "HK417", M .. "HK417S" }, { M .. "762x51Magazine20_HK417" }, count, { "MarzGuns.762x51_Box" }, count)
end
local function mk11(count)
    return kit({ M .. "MK11" }, { "GunsOfTien.762x51Magazine20_SR25" }, count, { "MarzGuns.762x51_Box" }, count)
end

-- Civilian rifles, packed as GoM packs its AR-15 (civilian boxes): up to 3 magazines and n boxes.
local function mdr223(boxes)
    return kit({ M .. "MDR223" }, { "MarzGuns.556x45Magazine30_STANAG" }, 3, { "MarzGuns.223_Box" }, boxes)
end
local function mdr308(boxes)
    return kit({ M .. "MDR308" }, { M .. "762x51Magazine20_PMAG" }, 3, { "MarzGuns.308_Box" }, boxes)
end
local function augA3(boxes)
    return kit({ M .. "AUGA3" }, { "GunsOfTien.556x45Magazine30_AUG" }, 3, { "MarzGuns.556x45_Box" }, boxes)
end
local function augHbar(boxes)
    return kit({ M .. "AUGHBAR" }, { M .. "762x39Magazine30_AUG" }, 3, { "MarzGuns.762x39_Box" }, boxes)
end
local function ps90(boxes)
    return kit({ M .. "PS90" }, { M .. "57x28Magazine50_P90" }, 3, { M .. "57x28_Box" }, boxes)
end
local function vectorCrb(boxes)
    return kit({ M .. "VECTORCRB" }, { "GunsOfTien.45Magazine13_GLOCK21" }, 3, { "MarzGuns.45_Box" }, boxes)
end
local function hk416qr22(boxes)
    return kit({ M .. "HK416QR22" }, { M .. "22LRMagazine20_HK416" }, 3, { "GunsOfTien.22LR_Box" }, boxes)
end

-- Pistols, as GoM's pistols come: the gun, up to 4 magazines (the Vector SDP 3, as the Vectors), n boxes; the
-- Five-seveN's 30 and the UCP's drum only on found guns (5%).
local function fiveseven(boxes)
    return kit({ "MarzGuns.FIVESEVEN" }, { M .. "57x28Magazine20_FIVESEVEN" }, 4, { M .. "57x28_Box" }, boxes)
end
local function ucp(boxes)
    return kit({ M .. "UCP" }, { M .. "46x30Magazine20_UCP" }, 4, { M .. "46x30_Box" }, boxes)
end
local function vectorSdp(boxes)
    return kit({ M .. "VECTORSDP" }, { "MarzGuns.9x19Magazine17_GLOCK" }, 3, { "MarzGuns.9x19_Box" }, boxes)
end

-- Russian guns: the Grozas with up to n of GoM's standard magazines of their calibre and n boxes (the Groza-1's
-- alternative gives it or the Groza-1 with the GP-25, as GoM's M16 alternative picks its M16A2_M203).
local function groza(guns, mag, box)
    local items = {}
    for _, gun in ipairs(guns) do items[#items + 1] = M .. gun end
    return function(count) return kit(items, { mag }, count, { box }, count) end
end
local groza1 = groza({ "GROZA1", "GROZAGL" }, "MarzGuns.762x39Magazine30", "MarzGuns.762x39_Box")
local groza2 = groza({ "GROZA2" }, "MarzGuns.545x39Magazine30_Bakelite", "MarzGuns.545x39_Box")
local groza4 = groza({ "GROZA4" }, "MarzGuns.9x39Magazine20", "MarzGuns.9x39_Box")
local function sv98(count)
    return kit({ M .. "SV98" }, { M .. "762x54Magazine10_SV98" }, count, { "MarzGuns.762x54_Box" }, count + 2)
end
local function sv99(boxes)
    return kit({ M .. "SV99" }, { M .. "22LRMagazine5_SV99" }, 3, { "GunsOfTien.22LR_Box" }, boxes)
end

-- One of GoM's own alternatives, found by its gun in a GoM spawner (nil when GoM no longer has it there).
local function gom(spawner, gun)
    return function()
        local map = spawnerMap()
        local list = map and map[spawner]
        if type(list) ~= "table" then return nil end
        for _, alternative in ipairs(list) do
            local first = type(alternative) == "table" and alternative[1]
            if type(first) == "table" and type(first.items) == "table" then
                for _, item in ipairs(first.items) do
                    if item == gun then return alternative end
                end
            end
        end
        print("[GunsOfTienPost93] " .. gun .. " not found in " .. spawner .. ", it is left out of our spawners")
        return nil
    end
end

-------------------------------------------------
-- Our spawners
-------------------------------------------------
local SWAT_PDW = M .. "Zombie_SWAT_PDW_Spawner"
local ARMY_WORLD = M .. "World_Modern_Army_Rifle_Spawner"
local ARMY_ZOMBIE = M .. "Zombie_Modern_Army_Rifle_Spawner"
local SPORTING = M .. "World_Modern_Sporting_Rifle_Spawner"
local PISTOL = M .. "World_Modern_Pistol_Spawner"
local POST_SOVIET = M .. "World_Post_Soviet_Spawner"

local ANACHRONISTIC = "MarzGuns.World_Anachronistic_Spawner"

-- { spawner, { { alternative function, count }, ... } }: counts as the GoM spawner each one stands beside.
local OWN_SPAWNERS = {
    { SWAT_PDW, { { mp7, 2 }, { p90tr, 2 }, { ump45, 2 }, { ump9, 2 }, { vector45, 2 }, { vector9, 2 }, { augPara, 2 } } },
    { ARMY_WORLD, { { scarl, 6 }, { scarh, 6 }, { hk416, 6 }, { hk417, 6 }, { mk11, 6 } } },
    { ARMY_ZOMBIE, { { scarl, 4 }, { scarh, 4 }, { hk416, 4 }, { hk417, 4 }, { mk11, 4 } } },
    { SPORTING, { { mdr223, 4 }, { mdr308, 4 }, { augA3, 4 }, { augHbar, 4 }, { ps90, 4 }, { vectorCrb, 4 },
        { hk416qr22, 4 }, { gom(ANACHRONISTIC, "MarzGuns.BENELLI_M4") } } },
    { PISTOL, { { fiveseven, 4 }, { vectorSdp, 4 }, { gom(ANACHRONISTIC, "MarzGuns.RHINO") } } },
    { POST_SOVIET, { { groza1, 3 }, { groza2, 3 }, { groza4, 3 }, { sv98, 3 }, { sv99, 4 },
        { gom(ANACHRONISTIC, "MarzGuns.MP412") } } },
}

-- Where they go: { spawner, distribution ("pd" procedural, "vd" vehicle, "bd" bag), list, weight }, each weight the
-- one GoM gives the spawner of the same kind of gun in that list (GoM's ItemInsertion.lua).
local PLACES = {
    -- GoM's Zombie_Police_SMG_Spawner places, plus SWAT gun storage (GoM's police shotgun weight in police storage)
    { SWAT_PDW, "pd", "SWATStorageGuns", 10 },
    { SWAT_PDW, "pd", "PrisonRiotStorage", 3 },
    { SWAT_PDW, "vd", "PoliceSWATTruckBed", 10 },
    { SWAT_PDW, "vd", "PoliceSWATSeatRear", 6 },
    { SWAT_PDW, "bd", "Bag_Police", 4 },
    -- GoM's World_Army_Rifle_Spawner places, without FirearmWeapons_Late (homes)
    { ARMY_WORLD, "pd", "ArmyStorageGuns", 15 },
    { ARMY_WORLD, "pd", "ArmyBunkerStorage", 4 },
    { ARMY_WORLD, "vd", "ArmyLightTruckBed", 10 },
    { ARMY_WORLD, "vd", "ArmyHeavyTruckBed", 10 },
    { ARMY_WORLD, "bd", "ALICEpack_Army", 5 },
    { ARMY_WORLD, "bd", "RifleCase3", 15 },
    { ARMY_WORLD, "bd", "BanditBag_Late", 2 },
    -- GoM's World_Import_Rifle_Spawner places, then its World_Anachronistic_Spawner places
    { SPORTING, "pd", "GunStoreCases", 10 },
    { SPORTING, "pd", "GunStoreGuns", 10 },
    { SPORTING, "pd", "GunStoreRifles", 6 },
    { SPORTING, "pd", "PawnShopGunsSpecial", 3 },
    { SPORTING, "pd", "PoliceEvidence", 3 },
    { SPORTING, "vd", "SurvivalistTruckBed", 6 },
    { SPORTING, "vd", "SurvivalistSeatRear", 4 },
    { SPORTING, "bd", "RifleCase4", 15 },
    { SPORTING, "pd", "FirearmWeapons_Late", 5 },
    { SPORTING, "pd", "SafehouseBin_Late", 5 },
    { SPORTING, "bd", "SurvivorBag_Late", 2 },
    { SPORTING, "bd", "BanditBag_Late", 1 },
    -- GoM's World_Import_Pistol_Spawner places, plus the late survivor and bandit bags (its Anachronistic weights)
    { PISTOL, "pd", "GunStorePistols", 8 },
    { PISTOL, "pd", "PawnShopGuns", 4 },
    { PISTOL, "pd", "PoliceEvidence", 4 },
    { PISTOL, "pd", "DrugLabGuns", 8 },
    { PISTOL, "pd", "DrugShackWeapons", 6 },
    { PISTOL, "pd", "PlankStashGun", 4 },
    { PISTOL, "vd", "BanditSeatFront", 4 },
    { PISTOL, "vd", "LuxuryGloveBox", 0.5 },
    { PISTOL, "bd", "SurvivorBag_Late", 2 },
    { PISTOL, "bd", "BanditBag_Late", 1 },
    -- GoM's World_Russian_Rifle_Spawner places
    { POST_SOVIET, "pd", "DrugLabGuns", 25 },
    { POST_SOVIET, "pd", "DrugShackWeapons", 25 },
    { POST_SOVIET, "pd", "DrugLabMoney", 10 },
    { POST_SOVIET, "pd", "PoliceEvidence", 10 },
    { POST_SOVIET, "pd", "SafehouseBin_Late", 10 },
    { POST_SOVIET, "pd", "PlankStashGun", 1 },
    { POST_SOVIET, "vd", "SurvivalistTruckBed", 10 },
    { POST_SOVIET, "vd", "SurvivalistSeatRear", 10 },
    { POST_SOVIET, "vd", "SurvivalistSeatFront", 10 },
    { POST_SOVIET, "vd", "BanditTruckBed", 4 },
    { POST_SOVIET, "vd", "BanditSeatRear", 3 },
}

-- Zombie attachment slots (vanilla AttachedWeaponDefinitions; a slot picks one of its weapons evenly, as GoM's
-- additions do). The mercenary slots exist only with Undead Survivors.
local SLOTS = {
    { "gunOnBackSWAT", SWAT_PDW },
    { "assaultRifleArmyOnBack", ARMY_ZOMBIE },
    { "gunOnBackBagSurvivalist", SPORTING },
    { "AmazonaSpear", POST_SOVIET },
    { "StalkerKnife", POST_SOVIET },
}

for _, entry in ipairs(SLOTS) do
    local definition = AttachedWeaponDefinitions and AttachedWeaponDefinitions[entry[1]]
    local weapons = type(definition) == "table" and definition.weapons
    if type(weapons) == "table" then
        local present = false
        for _, weapon in ipairs(weapons) do
            if weapon == entry[2] then present = true end
        end
        if not present then weapons[#weapons + 1] = entry[2] end
    end
end

-------------------------------------------------
-- Alternatives in Guns of Marz's spawners
-------------------------------------------------
-- High-capacity magazines on their own, as GoM's in its World_HighCap_Tactical_Magazine_Spawner (its M92FS 50, M93R
-- 60, MP5 60 / 100 drums: the magazine and up to two boxes; SWAT / police storage and gun stores, no homes; only with
-- GoM's sandbox SpawnHighCapMags on, which places that spawner).
local function highCap(mag, box)
    return function() return kit({ mag }, nil, nil, { box }, 2) end
end

local GOM_SPAWNERS = {
    { "MarzGuns.Zombie_Police_Handgun_Spawner", fiveseven, 4 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", fiveseven, 4 },
    { "MarzGuns.Zombie_Police_Handgun_Spawner", ucp, 4 },
    { "MarzGuns.Zombie_SWAT_Handgun_Spawner", ucp, 4 },
    { "MarzGuns.Zombie_Mercenary_Sniper_Spawner", sv98, 6 },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_MP7", M .. "46x30_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine60_MP7", M .. "46x30_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "57x28Magazine30_FIVESEVEN", M .. "57x28_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_UCP", M .. "46x30_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "762x51Magazine50_SCARH", "MarzGuns.762x51_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "45Magazine30_GLOCK21", "MarzGuns.45_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "9x19Magazine33_GLOCK", "MarzGuns.9x19_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "9x19Magazine40_GLOCK", "MarzGuns.9x19_Box") },
    { "MarzGuns.World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "762x51Magazine50_PMAG", "MarzGuns.762x51_Box") },
    -- the HBAR's 50 beside GoM's own 7.62x39 75 (its high-capacity Russian-calibre magazine spawner)
    { "MarzGuns.World_HighCap_Russian_Magazine_Spawner", highCap(M .. "762x39Magazine50_AUG", "MarzGuns.762x39_Box") },
}

-- Parts added to the item list of a GoM spawner's first alternative.
local PART_SPAWNERS = {
    { "MarzGuns.World_Suppressor_Spawner",
        { M .. "MP7_Suppressor", M .. "P90_Suppressor", M .. "FIVESEVEN_Suppressor", M .. "SCARH_Suppressor" } },
    { "MarzGuns.World_Muzzle_Device_Spawner", { M .. "MP7_Muzzle_Mount_Device", M .. "P90_Muzzle_Mount_Device",
        M .. "SCARH_Muzzle_Mount_Device" } },
}

-- Parts added to the item list of a GoM vanilla attachment replacement's first alternative.
local VANILLA_ATTACHMENTS = {
    { "Base.ChokeTubeImproved", { M .. "MP7_Muzzle_Mount_Device", M .. "P90_Muzzle_Mount_Device",
        M .. "SCARH_Muzzle_Mount_Device" } },
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

local function addParts(list, label, parts)
    local first = type(list) == "table" and list[1]
    local group = type(first) == "table" and first[1]
    local items = type(group) == "table" and group.items
    if type(items) ~= "table" then
        print("[GunsOfTienPost93] " .. label .. " not found, its parts will not spawn there")
        return
    end
    for _, item in ipairs(parts) do
        items[#items + 1] = item
        addedParts[#addedParts + 1] = { items, item }
    end
end

local function addSpawners()
    removeAdded()
    local map = spawnerMap()
    if not map then
        print("[GunsOfTienPost93] Guns of Marz spawner table not found, the Post-93 guns will not spawn")
        return
    end
    -- ours first: GoM's alternatives are copied from GoM's lists before anything of ours is added to them
    for _, entry in ipairs(OWN_SPAWNERS) do
        local list = {}
        for _, alternative in ipairs(entry[2]) do
            local built = alternative[1](alternative[2])
            if built then list[#list + 1] = built end
        end
        map[entry[1]] = list
    end
    for _, entry in ipairs(GOM_SPAWNERS) do
        local list = map[entry[1]]
        if type(list) == "table" then
            local alternative = entry[2](entry[3])
            list[#list + 1] = alternative
            added[#added + 1] = { list, alternative }
        end
    end
    for _, entry in ipairs(PART_SPAWNERS) do
        addParts(map[entry[1]], entry[1], entry[2])
    end
    local okR, replacer = pcall(require, "MarzWeapons/OnCreate/VanillaReplacerTable")
    local attachments = okR and type(replacer) == "table" and replacer.VanillaAttachmentMap
    for _, entry in ipairs(VANILLA_ATTACHMENTS) do
        addParts(type(attachments) == "table" and attachments[entry[1]], "Guns of Marz's " .. entry[1] .. " replacement",
            entry[2])
    end
end

-- Set at file load too, so a spawner created before the world's OnInitGlobalModData still resolves.
addSpawners()
Events.OnInitGlobalModData.Add(addSpawners)

-------------------------------------------------
-- Our spawners in vanilla loot lists
-------------------------------------------------
-- Before the merge, as GoM inserts its own (OnPreDistributionMerge), so they are in the merged lists the same way.
local function addSpawnerLoot()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local distributions = { pd = ProceduralDistributions.list, vd = VehicleDistributions, bd = BagsAndContainers }
    for _, entry in ipairs(PLACES) do
        local list = distributions[entry[2]] and distributions[entry[2]][entry[3]]
        if type(list) == "table" and type(list.items) == "table" then
            list.items[#list.items + 1] = entry[1]
            list.items[#list.items + 1] = entry[4] * multiplier
        end
    end
end

Events.OnPreDistributionMerge.Add(addSpawnerLoot)

-------------------------------------------------
-- Boxes and cartons in world containers
-------------------------------------------------
-- Beside vanilla's 9mm box / carton (GoM's own boxes and cartons come in place of or beside vanilla ones), only in
-- police, SWAT and gun store lists: no civilian homes. Every loot table (procedural rooms, vehicles, bags, the top-level
-- suburbs lists), as GoM's Distribution.Insert does. (An entry marked `true` in a fourth field goes in every list.)
-- The 5.7x28mm SS190 box and carton are the main mod's loot since 2026-11-03 (its server/GunsOfTien/Loot.lua): they
-- moved there with the P90, and the .22 LR box and carton on 2026-11-19 with the Walther PPK.
local WORLD = {
    { M .. "46x30_Box", "Base.Bullets9mmBox", 0.05 },
    { M .. "46x30_Carton", "Base.Bullets9mmCarton", 0.05 },
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
        local newItem, baseItem, share, everywhere = entry[1], entry[2], entry[3] * multiplier, entry[4]
        local script = ScriptManager.instance:getItem(baseItem)
        if script and ScriptManager.instance:getItem(newItem) then
            local name, fullName = script:getName(), script:getFullName()
            for _, lootTable in ipairs(tables) do
                for listName, data in pairs(lootTable) do
                    local items = type(listName) == "string" and type(data) == "table" and data.items
                    if type(items) == "table" and (everywhere or isWantedList(listName)) then
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
