--[[
    Guns of Tien - Post-93 -- loot for the MP7A1 and MP7A2, the P90 TR and PS90, the Five-seveN, the UCP Prototype, the SCAR-L and
    SCAR-H, the UMP45 and UMP9, the Steyr AUG A3, Para and HBAR, the KRISS Vector .45, 9mm, CRB and SDP, the MDRx .223
    and .308, the Mk 11, the HK416, the HK416 .22 pistol, the HK417s, the Grozas, the SV-98 and SV-99, and their
    ammunition

    How Guns of Marz's loot works (traced 2026-11-21 in GoM's ItemInsertion.lua, ItemSpawner.lua,
    ZombieAttachmentReplacer.lua and AttachedWeaponDefinitions.lua): GoM puts ~45 spawner items (scripts with
    `OnCreate = MarzGuns_OnCreate.SelectItem`) into vanilla loot lists with a weight (x its LootMultiplier) and into
    vanilla zombie attachment slots. A created spawner looks itself up by full type in `ItemSpawnerMap`, picks one of
    its alternatives **evenly** (`r:random(#entry)`), and becomes the alternative's gun plus minAmountChance ..
    maxAmountChance of each later group (magazines, boxes). On zombies the same lookup runs on attached items and on
    the inventory at death. So an alternative added to a GoM spawner adds no guns to the world: it shares that
    spawner's spawns. Until 2026-11-21 most Post-93 guns were alternatives in GoM's World_Anachronistic_Spawner (21
    alternatives, placed only in FirearmWeapons_Late, SafehouseBin_Late, SurvivorBag_Late and BanditBag_Late, on no
    zombie), so each was rare and found only late in homes and bags.

    Since 2026-11-21 (user: "whatever suits reality"; the AUG HBAR "in line with AUG family"; then "add spawners to
    places where we think it can be applicable, AND if GoM doesn't add a spawner to"):
    - Each gun is an alternative in the GoM spawner that holds its kind of gun, packed as that spawner packs its own
      (GUNS below): the law-enforcement SMGs in the police SMG spawner, the modern military rifles in the army rifle
      spawners, the civilian rifles (the AUG A3 and HBAR with the main mod's AUG A1) in the import rifle spawner, the
      Five-seveN and Vector SDP in the import pistol spawner, the Russian guns in the Russian rifle spawner. Zombies
      come with those spawners' slots, plus the Grozas in the mercenary rifle spawner and the SV-98 / SV-99 in the
      mercenary sniper spawner (Undead Survivors' outfits), the HK416 and SCAR-L in GoM's police rifle spawner (SWAT
      zombies' back slot), the Five-seveN and UCP in the police and SWAT handgun spawners (beside the Glock 17 and
      M92FS, user 2026-10-17; the UCP was never sold, so it is in no civilian or criminal spawner).
    - A spawner of our own would only double the gun rolls where GoM's of the same kind already is (the 3.18.0 build
      had five such spawners; user: "why duplicate a spawner when a GoM spawner is in the same place already"). So
      new placements go only where GoM places no spawner of that kind and the guns belong (PLACES below), and they
      place GoM's own spawner: SWATStorageGuns (GoM puts only part spawners there; its guns come from vanilla's
      replaced pistols, M16s, SPAS-12 and M24) gets the police SMG spawner (at 10, GoM's police shotgun weight in
      PoliceStorageGuns) and the police rifle spawner (at 6, GoM's police SMG weight on a SWAT van's rear seat), so
      the SWAT armoury holds SWAT SMGs and carbines, GoM's MP5s and CAR-15s among them. Vanilla has SWATStorageGuns
      only in `policeswat` rooms, so (user: "make the area wider") police stations' PoliceStorageGuns
      (`policegunstorage`, `policestorage`, the captain's office locker; also `security` rooms, which share the list)
      get the police rifle spawner at 6, under GoM's police shotgun there (10) and vanilla's pistols and shotguns
      (patrol rifles were common in US police armouries after 1997; SMGs were SWAT's, so the police SMG spawner goes
      there only with Extend Loot Areas).
    - More places where reality puts these guns (user, 2026-11-21: "for lore accuracy, implement them"): patrol
      rifles (GoM's police rifle spawner) in police cars' trunks (6) and rear seats (4) and on police zombies' back
      slot (`shotgunPolice`: Police, PoliceState, PoliceRiot, Sheriff_Deputy, PrivateMilitia outfits); the Mk 11 and
      the HK417 Marksman beside the M24 in GoM's army sniper spawner (`Zombie_Army_SemiRifle_Spawner`, the Ghillie
      outfit's back slot); the civilian rifles on survivalist zombies (GoM's import rifle spawner in the
      `meleeInBackBag`, `_Mid`, `_Late` slots, the only gun slots the Survivalist outfits use: vanilla commented
      `gunOnBackBagSurvivalist` out of them) and in ordinary pawn shops (`PawnShopGuns` 3, as GoM's
      `PawnShopGunsSpecial`).
    - Sandbox GunsOfTien.ExtendLootAreas (main mod's page, off by default; user: "lore inaccuracies but still
      viable"): EXTENDED below. (Arming the zombie outfits and GoM's spawners in new places are the main mod's
      server/GunsOfTien/ExtendLootAreas.lua, since they hand out GoM's guns too.) Regular police with SMGs (police
      SMG spawner in PoliceStorageGuns 3, police cars 4 / 3, the `shotgunPolice` slot), criminals with Grozas, UMP45s and Vector 9mms (GoM's crime rifle spawner: bank
      robbers, bandit bags, stashes, the special pawn shop list), survivalists with SCAR-Ls, HK416s and Groza-1s (its
      survivalist rifle spawner: survivor bags, survivalists' vehicles), civilians with Five-seveNs and Vector SDPs
      (its civilian handgun spawner: civilian holsters, homes, pawn shops, stashes, pistol cases), and the civilian
      rifles among GoM's replacements for vanilla's JS-2000 / AR-type `Base.JS14_Rifle` (homes, closets, garages,
      police storage; only with GoM's sandbox VanillaWeaponReplacement on; its entries count `amountChance` 0..n).
      Read at OnInitGlobalModData and OnPreDistributionMerge, so a change takes effect at the next world load.
    - GoM's Anachronistic spawner gets nothing back: its five guns (G36 / G36C, Benelli M4, AA-12, Rhino, MP-412 REX)
      are its own again.
    - Everything added to a GoM list (spawner alternatives, slot entries, replacements) is taken out again before the
      next world adds it (Lua is not always reloaded).
    - Suppressors and muzzle devices join GoM's MarzGuns.World_Suppressor_Spawner (SWAT gun storage, police evidence,
      drug labs, drug shacks) and MarzGuns.World_Muzzle_Device_Spawner (gun stores, garages, SWAT and army storage)
      as GoM's own have been since its November 2026 update ("Ensure a muzzle mount device per suppressor spawn"):
      one alternative per mount, the cans or devices and their mount device, so each spawn picks one alternative and
      one item of it with the mount it needs (the MP7's can with its mount, the P90's and Five-seveN's with the
      5.7x28mm mount, the SCAR-H's can and the SureFire devices with the 7.62x51mm mount). The mount
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
-- A count is a number (1 to it, as GoM's maxAmountChance without a minimum) or { min, max }.
local function group(items, count)
    if type(count) == "table" then
        return { items = items, minAmountChance = count[1], maxAmountChance = count[2] }
    end
    return { items = items, maxAmountChance = count }
end

local function kit(guns, mags, boxes)
    return function(magCount, boxCount)
        local alternative = { group(guns, 1) }
        if mags then alternative[#alternative + 1] = group(mags, magCount) end
        alternative[#alternative + 1] = group(boxes, boxCount)
        return alternative
    end
end

-- Law enforcement SMGs
local mp7 = kit({ M .. "MP7A1", M .. "MP7A2" },     -- one of the two, as GoM's MP5 / MP5A2 / MP5SD
    { M .. "46x30Magazine20_MP7", M .. "46x30Magazine30_MP7", M .. "46x30Magazine40_MP7" }, { M .. "46x30_Box" })
local p90tr = kit({ M .. "P90TR" }, { M .. "57x28Magazine50_P90" }, { M .. "57x28_Box" })
local ump45 = kit({ M .. "UMP45" }, { M .. "45Magazine25_UMP" }, { "MarzGuns.45_Box" })
local ump9 = kit({ M .. "UMP9" }, { M .. "9x19Magazine30_UMP" }, { "MarzGuns.9x19_Box" })
-- the Vectors with Glock's standard magazines (the main mod's Glock 21 13, GoM's Glock 17 17)
local vector45 = kit({ M .. "VECTOR45" }, { "GunsOfTien.45Magazine13_GLOCK21" }, { "MarzGuns.45_Box" })
local vector9 = kit({ M .. "VECTOR9" }, { "MarzGuns.9x19Magazine17_GLOCK" }, { "MarzGuns.9x19_Box" })
local augPara = kit({ M .. "AUGPARA" }, { M .. "9x19Magazine25_AUG", M .. "9x19Magazine32_AUG" }, { "MarzGuns.9x19_Box" })

-- Modern military rifles
local scarl = kit({ M .. "SCARL" }, { "MarzGuns.556x45Magazine30_STANAG" }, { "MarzGuns.556x45_Box" })
local scarh = kit({ M .. "SCARH" }, { M .. "762x51Magazine20_SCARH" }, { "MarzGuns.762x51_Box" })
local hk416 = kit({ M .. "HK416" }, { "MarzGuns.556x45Magazine30_STANAG" }, { "MarzGuns.556x45_Box" })
local hk417 = kit({ M .. "HK417", M .. "HK417S" }, { M .. "762x51Magazine20_HK417" }, { "MarzGuns.762x51_Box" })
local mk11 = kit({ M .. "MK11" }, { "GunsOfTien.762x51Magazine20_SR25" }, { "MarzGuns.762x51_Box" })
local hk417s = kit({ M .. "HK417S" }, { M .. "762x51Magazine20_HK417" }, { "MarzGuns.762x51_Box" })     -- the Marksman alone

-- Civilian rifles (civilian boxes: .223 and .308 where the gun takes them)
local mdr223 = kit({ M .. "MDR223" }, { "MarzGuns.556x45Magazine30_STANAG" }, { "MarzGuns.223_Box" })
local mdr308 = kit({ M .. "MDR308" }, { M .. "762x51Magazine20_PMAG" }, { "MarzGuns.308_Box" })
local augA3 = kit({ M .. "AUGA3" }, { "GunsOfTien.556x45Magazine30_AUG" }, { "MarzGuns.556x45_Box" })
local augHbar = kit({ M .. "AUGHBAR" }, { M .. "762x39Magazine30_AUG" }, { "MarzGuns.762x39_Box" })
local ps90 = kit({ M .. "PS90" }, { M .. "57x28Magazine50_P90" }, { M .. "57x28_Box" })
local vectorCrb = kit({ M .. "VECTORCRB" }, { "GunsOfTien.45Magazine13_GLOCK21" }, { "MarzGuns.45_Box" })
local hk416qr22 = kit({ M .. "HK416QR22" }, { M .. "22LRMagazine20_HK416" }, { "GunsOfTien.22LR_Box" })

-- Pistols (the Five-seveN's 30 and the UCP's drum only on found guns, 5%)
local fiveseven = kit({ "MarzGuns.FIVESEVEN" }, { M .. "57x28Magazine20_FIVESEVEN" }, { M .. "57x28_Box" })
local ucp = kit({ M .. "UCP" }, { M .. "46x30Magazine20_UCP" }, { M .. "46x30_Box" })
local vectorSdp = kit({ M .. "VECTORSDP" }, { "MarzGuns.9x19Magazine17_GLOCK" }, { "MarzGuns.9x19_Box" })

-- Russian guns: the Grozas with GoM's standard magazines of their calibre (the Groza-1's alternative gives it or the
-- Groza-1 with the GP-25, as GoM's M16 alternative picks its M16A2_M203)
local groza1 = kit({ M .. "GROZA1", M .. "GROZAGL" }, { "MarzGuns.762x39Magazine30" }, { "MarzGuns.762x39_Box" })
local groza2 = kit({ M .. "GROZA2" }, { "MarzGuns.545x39Magazine30_Bakelite" }, { "MarzGuns.545x39_Box" })
local groza4 = kit({ M .. "GROZA4" }, { "MarzGuns.9x39Magazine20" }, { "MarzGuns.9x39_Box" })
local sv98 = kit({ M .. "SV98" }, { M .. "762x54Magazine10_SV98" }, { "MarzGuns.762x54_Box" })
local sv99 = kit({ M .. "SV99" }, { M .. "22LRMagazine5_SV99" }, { "GunsOfTien.22LR_Box" })
-- the 9A-91 and VSK-94 with their own magazine and GoM's 9x39 box, as the Groza-4
local a91 = kit({ M .. "9A91" }, { M .. "9x39Magazine20_9A91" }, { "MarzGuns.9x39_Box" })
local vsk94 = kit({ M .. "VSK94" }, { M .. "9x39Magazine20_9A91" }, { "MarzGuns.9x39_Box" })
-- the A-91M with GoM's AK-47 30 and box
local a91m = kit({ M .. "A91M" }, { "MarzGuns.762x39Magazine30" }, { "MarzGuns.762x39_Box" })
local a91mProto = kit({ M .. "A91MPROTO" }, { M .. "762x54Magazine20_SV98" }, { "MarzGuns.762x54_Box" })
-- the Kedr with its magazines and the main mod's 9x18mm box (the round has no loot of its own)
local kedr = kit({ M .. "KEDR" }, { M .. "9x18Magazine20_KEDR", M .. "9x18Magazine30_KEDR" }, { "GunsOfTien.9x18_Box" })

-- High-capacity magazines on their own, as GoM's in its high-capacity magazine spawners (its M92FS 50, M93R 60, MP5
-- 60 / 100 drums: the magazine and up to two boxes; only with GoM's sandbox SpawnHighCapMags on, which places them).
local function highCap(mag, box) return kit({ mag }, nil, { box }) end

-------------------------------------------------
-- Alternatives in Guns of Marz's spawners
-------------------------------------------------
-- { GoM spawner, alternative, magazines, boxes }: counts as that spawner packs its own guns (GoM's ItemSpawnerTable).
local G = "MarzGuns."
local POLICE_SMG = G .. "Zombie_Police_SMG_Spawner"         -- MP5s: 4 magazines, 4 boxes
local POLICE_RIFLE = G .. "Zombie_Police_Rifle_Spawner"     -- M16A1 / XM177 / CAR-15: 4, 4
local ARMY_WORLD = G .. "World_Army_Rifle_Spawner"          -- 6, 6
local ARMY_ZOMBIE = G .. "Zombie_Army_Rifle_Spawner"        -- 4, 4
local IMPORT_RIFLE = G .. "World_Import_Rifle_Spawner"      -- 3-6, 3-6
local IMPORT_PISTOL = G .. "World_Import_Pistol_Spawner"    -- 3-6, 3-6
local RUSSIAN_RIFLE = G .. "World_Russian_Rifle_Spawner"    -- 6, 6
local MERC_RIFLE = G .. "Zombie_Mercenary_Rifles_Spawner"   -- AKs: 2-4 / 4-8, 4-8 / 6-10
local MERC_SNIPER = G .. "Zombie_Mercenary_Sniper_Spawner"  -- SVD: 3-6, 6-10
local POLICE_HANDGUN = G .. "Zombie_Police_Handgun_Spawner"
local SWAT_HANDGUN = G .. "Zombie_SWAT_Handgun_Spawner"
local ARMY_SNIPER = G .. "Zombie_Army_SemiRifle_Spawner"    -- M24 / Remington 700: 4 boxes
local CRIME_RIFLE = G .. "Zombie_Crime_Rifle_Spawner"       -- FNC / AKs / AS VAL: 2-4, 2-4
local SURVIVALIST_RIFLE = G .. "Zombie_Survivalist_Rifle_Spawner" -- AKs: 4, 4
local CIVILIAN_HANDGUN = G .. "Zombie_Civilian_Handgun_Spawner"   -- M92FS / Glock 17 / M1911 / Hi-Power: 2-4, 3
local RANGE = { 3, 6 }

local GUNS = {
    -- law-enforcement SMGs
    { POLICE_SMG, mp7, 4, 4 }, { POLICE_SMG, p90tr, 4, 4 }, { POLICE_SMG, ump45, 4, 4 }, { POLICE_SMG, ump9, 4, 4 },
    { POLICE_SMG, vector45, 4, 4 }, { POLICE_SMG, vector9, 4, 4 }, { POLICE_SMG, augPara, 4, 4 },
    -- the SWAT carbines also with GoM's police rifles (SWAT zombies, and SWAT storage below)
    { POLICE_RIFLE, hk416, 4, 4 }, { POLICE_RIFLE, scarl, 4, 4 },
    -- modern military rifles
    { ARMY_WORLD, scarl, 6, 6 }, { ARMY_WORLD, scarh, 6, 6 }, { ARMY_WORLD, hk416, 6, 6 }, { ARMY_WORLD, hk417, 6, 6 },
    { ARMY_WORLD, mk11, 6, 6 },
    { ARMY_ZOMBIE, scarl, 4, 4 }, { ARMY_ZOMBIE, scarh, 4, 4 }, { ARMY_ZOMBIE, hk416, 4, 4 },
    { ARMY_ZOMBIE, hk417, 4, 4 }, { ARMY_ZOMBIE, mk11, 4, 4 },
    -- the army's marksman rifles beside the M24 (Ghillie zombies)
    { ARMY_SNIPER, mk11, 4, 4 }, { ARMY_SNIPER, hk417s, 4, 4 },
    -- civilian rifles, the AUG A3 and HBAR beside the main mod's AUG A1
    { IMPORT_RIFLE, mdr223, RANGE, RANGE }, { IMPORT_RIFLE, mdr308, RANGE, RANGE }, { IMPORT_RIFLE, augA3, RANGE, RANGE },
    { IMPORT_RIFLE, augHbar, RANGE, RANGE }, { IMPORT_RIFLE, ps90, RANGE, RANGE }, { IMPORT_RIFLE, vectorCrb, RANGE, RANGE },
    { IMPORT_RIFLE, hk416qr22, RANGE, RANGE },
    -- pistols
    { IMPORT_PISTOL, fiveseven, RANGE, RANGE }, { IMPORT_PISTOL, vectorSdp, RANGE, RANGE },
    { POLICE_HANDGUN, fiveseven, 4, 4 }, { SWAT_HANDGUN, fiveseven, 4, 4 },
    { POLICE_HANDGUN, ucp, 4, 4 }, { SWAT_HANDGUN, ucp, 4, 4 },
    -- Russian guns
    { RUSSIAN_RIFLE, groza1, 6, 6 }, { RUSSIAN_RIFLE, groza2, 6, 6 }, { RUSSIAN_RIFLE, groza4, 6, 6 },
    { RUSSIAN_RIFLE, sv98, 6, 6 }, { RUSSIAN_RIFLE, sv99, 6, 6 },
    { MERC_RIFLE, groza1, { 2, 4 }, { 4, 8 } }, { MERC_RIFLE, groza2, { 2, 4 }, { 4, 8 } },
    { MERC_RIFLE, groza4, { 2, 4 }, { 4, 8 } },
    { MERC_SNIPER, sv98, { 3, 6 }, { 6, 10 } }, { MERC_SNIPER, sv99, { 3, 6 }, { 6, 10 } },
    { RUSSIAN_RIFLE, a91, 6, 6 }, { RUSSIAN_RIFLE, vsk94, 6, 6 },
    { MERC_RIFLE, a91, { 2, 4 }, { 4, 8 } }, { MERC_SNIPER, vsk94, { 3, 6 }, { 6, 10 } },
    { RUSSIAN_RIFLE, a91m, 6, 6 }, { MERC_RIFLE, a91m, { 2, 4 }, { 4, 8 } },
    { RUSSIAN_RIFLE, a91mProto, 6, 6 }, { MERC_RIFLE, a91mProto, { 2, 4 }, { 4, 8 } },
    -- high-capacity magazines
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_MP7", M .. "46x30_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine60_MP7", M .. "46x30_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "57x28Magazine30_FIVESEVEN", M .. "57x28_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "46x30Magazine40_UCP", M .. "46x30_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "762x51Magazine50_SCARH", "MarzGuns.762x51_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "45Magazine30_GLOCK21", "MarzGuns.45_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "9x19Magazine33_GLOCK", "MarzGuns.9x19_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "9x19Magazine40_GLOCK", "MarzGuns.9x19_Box"), nil, 2 },
    { G .. "World_HighCap_Tactical_Magazine_Spawner", highCap(M .. "762x51Magazine50_PMAG", "MarzGuns.762x51_Box"), nil, 2 },
    -- the HBAR's 50 beside GoM's own 7.62x39 75 (its high-capacity Russian-calibre magazine spawner)
    { G .. "World_HighCap_Russian_Magazine_Spawner", highCap(M .. "762x39Magazine50_AUG", "MarzGuns.762x39_Box"), nil, 2 },
    -- the 20-round 7.62x54R magazine (the SV-98's and the A-91M Prototype's) there too
    { G .. "World_HighCap_Russian_Magazine_Spawner", highCap(M .. "762x54Magazine20_SV98", "MarzGuns.762x54_Box"), nil, 2 },
}

-- GoM's spawners placed where GoM places no spawner of that kind and the guns belong: { spawner, distribution ("pd"
-- procedural, "vd" vehicle, "bd" bag), list, weight }.
local PLACES = {
    { POLICE_SMG, "pd", "SWATStorageGuns", 10 },
    { POLICE_RIFLE, "pd", "SWATStorageGuns", 6 },
    -- patrol rifles: police stations' gun storage (policegunstorage, policestorage, the captain's office; vanilla also
    -- uses the list for security rooms), under GoM's police shotgun there (10), and police cars (GoM's police shotgun
    -- is 10 in the trunk, 6 on the rear seat)
    { POLICE_RIFLE, "pd", "PoliceStorageGuns", 6 },
    { POLICE_RIFLE, "vd", "PoliceTruckBed", 6 },
    { POLICE_RIFLE, "vd", "PoliceSeatRear", 4 },
    -- civilian rifles in ordinary pawn shops too (GoM: PawnShopGunsSpecial 3)
    { IMPORT_RIFLE, "pd", "PawnShopGuns", 3 },
}

-- Zombie attachment slots: { slot, spawner } (a slot picks one of its weapons evenly, as GoM's additions do).
local SLOTS = {
    -- patrol rifles on police zombies' backs (Police, PoliceState, PoliceRiot, Sheriff_Deputy, PrivateMilitia)
    { "shotgunPolice", POLICE_RIFLE },
    -- civilian rifles on survivalists (the only gun slots their outfits use)
    { "meleeInBackBag", IMPORT_RIFLE }, { "meleeInBackBag_Mid", IMPORT_RIFLE }, { "meleeInBackBag_Late", IMPORT_RIFLE },
}

-- Only while GunsOfTien.ExtendLootAreas is off (user, 2026-11-26: "Extend Loot off should be lore accurate while
-- extend loot on should expose the guns to loot distribution regardless of lore"): the Kedr, a Russian police gun
-- that reached nobody's gun store, lies with the Russian guns (drug labs, stashes, police evidence, survivalists'
-- and bandits' vehicles, late homes). With the option on that spawner goes onto zombies' backs (the main mod's
-- ExtendLootAreas.lua), no place for a holstered gun, so the Kedr moves to the short SMG spawner (EXTENDED_GUNS).
local LORE_GUNS = {
    { RUSSIAN_RIFLE, kedr, 6, 6 },
}

-- Sandbox GunsOfTien.ExtendLootAreas: places that bend reality but still make sense in game.
local EXTENDED_GUNS = {
    -- the Kedr with GoM's holstered machine pistols (MP5K, TEC-9, MAC-10; the main mod's Uzis, TMP and Skorpion):
    -- gun stores, pawn shops, glove boxes, bandit bags, homes, shoulder holsters, drug labs, shacks and stashes
    { G .. "World_Short_SMG_Spawner", kedr, 6, 6 },
    -- criminals with Grozas and SMGs
    { CRIME_RIFLE, groza1, { 2, 4 }, { 2, 4 } }, { CRIME_RIFLE, groza2, { 2, 4 }, { 2, 4 } },
    { CRIME_RIFLE, groza4, { 2, 4 }, { 2, 4 } }, { CRIME_RIFLE, a91, { 2, 4 }, { 2, 4 } },
    { CRIME_RIFLE, a91m, { 2, 4 }, { 2, 4 } }, { CRIME_RIFLE, a91mProto, { 2, 4 }, { 2, 4 } },
    { CRIME_RIFLE, ump45, { 2, 4 }, { 2, 4 } },
    { CRIME_RIFLE, vector9, { 2, 4 }, { 2, 4 } },
    -- survivalists with military and Russian rifles
    { SURVIVALIST_RIFLE, scarl, 4, 4 }, { SURVIVALIST_RIFLE, hk416, 4, 4 }, { SURVIVALIST_RIFLE, groza1, 4, 4 },
    -- civilians with the modern pistols
    { CIVILIAN_HANDGUN, fiveseven, { 2, 4 }, 3 }, { CIVILIAN_HANDGUN, vectorSdp, { 2, 4 }, 3 },
}
local EXTENDED_PLACES = {
    -- regular police with SMGs (under the patrol rifles)
    { POLICE_SMG, "pd", "PoliceStorageGuns", 3 },
    { POLICE_SMG, "vd", "PoliceTruckBed", 4 },
    { POLICE_SMG, "vd", "PoliceSeatRear", 3 },
}
local EXTENDED_SLOTS = {
    { "shotgunPolice", POLICE_SMG },
}
-- The civilian rifles among GoM's replacements for vanilla's AR-type rifle (homes, closets, garages, police storage),
-- in the replacement table's own form: { items, amountChance } with 0..amountChance of each later group.
local EXTENDED_REPLACEMENTS = {
    { "Base.JS14_Rifle", { mdr223, mdr308, augA3, augHbar, ps90, vectorCrb, hk416qr22 }, 4, 4 },
}

local function extendLootAreas()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.ExtendLootAreas == true
end

local function asReplacement(alternative)
    local entry = {}
    for _, option in ipairs(alternative) do
        entry[#entry + 1] = { items = option.items, amountChance = option.maxAmountChance or 1 }
    end
    return entry
end

-- Alternatives added to a GoM spawner, as GoM's own there: { spawner, the cans or devices, their mount device }
local PART_ALTERNATIVES = {
    { "MarzGuns.World_Suppressor_Spawner", { M .. "MP7_Suppressor" }, M .. "MP7_Muzzle_Mount_Device" },
    { "MarzGuns.World_Suppressor_Spawner", { M .. "P90_Suppressor", M .. "FIVESEVEN_Suppressor" },
        M .. "P90_Muzzle_Mount_Device" },
    { "MarzGuns.World_Suppressor_Spawner", { M .. "SCARH_Suppressor" }, M .. "SCARH_Muzzle_Mount_Device" },
    { "MarzGuns.World_Suppressor_Spawner", { M .. "9A91_Suppressor" }, M .. "9A91_Muzzle_Mount_Device" },
    { "MarzGuns.World_Muzzle_Device_Spawner",
        { M .. "SF3P_Flash_Hider", M .. "SFMB_Muzzle_Brake", M .. "WarComp_Flash_Hider" }, M .. "SCARH_Muzzle_Mount_Device" },
}

-- Parts added to the item list of a GoM vanilla attachment replacement's first alternative.
local VANILLA_ATTACHMENTS = {
    { "Base.ChokeTubeImproved", { M .. "MP7_Muzzle_Mount_Device", M .. "P90_Muzzle_Mount_Device",
        M .. "SCARH_Muzzle_Mount_Device", M .. "9A91_Muzzle_Mount_Device" } },
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
    local partGroup = type(first) == "table" and first[1]
    local items = type(partGroup) == "table" and partGroup.items
    if type(items) ~= "table" then
        print("[GunsOfTienPost93] " .. label .. " not found, its parts will not spawn there")
        return
    end
    for _, item in ipairs(parts) do
        items[#items + 1] = item
        addedParts[#addedParts + 1] = { items, item }
    end
end

local function addTo(list, value)
    list[#list + 1] = value
    added[#added + 1] = { list, value }
end

local function addGuns(map, guns)
    for _, entry in ipairs(guns) do
        local list = map[entry[1]]
        if type(list) == "table" then
            addTo(list, entry[2](entry[3], entry[4]))
        else
            print("[GunsOfTienPost93] " .. entry[1] .. " not found, some Post-93 loot will not spawn there")
        end
    end
end

local function addSlots(slots)
    for _, entry in ipairs(slots) do
        local definition = AttachedWeaponDefinitions and AttachedWeaponDefinitions[entry[1]]
        local weapons = type(definition) == "table" and definition.weapons
        if type(weapons) == "table" then addTo(weapons, entry[2]) end
    end
end

local function addSpawners()
    removeAdded()
    local map = spawnerMap()
    if not map then
        print("[GunsOfTienPost93] Guns of Marz spawner table not found, the Post-93 guns will not spawn")
        return
    end
    local extend = extendLootAreas()
    addGuns(map, GUNS)
    addSlots(SLOTS)
    if extend then
        addGuns(map, EXTENDED_GUNS)
        addSlots(EXTENDED_SLOTS)
    else
        addGuns(map, LORE_GUNS)
    end
    for _, entry in ipairs(PART_ALTERNATIVES) do
        local list = map[entry[1]]
        if type(list) == "table" then
            addTo(list, { { items = entry[2], maxAmountChance = 1 }, { items = { entry[3] }, maxAmountChance = 1 } })
        else
            print("[GunsOfTienPost93] " .. entry[1] .. " not found, its parts will not spawn there")
        end
    end
    local okR, replacer = pcall(require, "MarzWeapons/OnCreate/VanillaReplacerTable")
    local attachments = okR and type(replacer) == "table" and replacer.VanillaAttachmentMap
    for _, entry in ipairs(VANILLA_ATTACHMENTS) do
        addParts(type(attachments) == "table" and attachments[entry[1]], "Guns of Marz's " .. entry[1] .. " replacement",
            entry[2])
    end
    local weapons = okR and type(replacer) == "table" and replacer.VanillaWeaponMap
    if extend then
        for _, entry in ipairs(EXTENDED_REPLACEMENTS) do
            local list = type(weapons) == "table" and weapons[entry[1]]
            if type(list) == "table" then
                for _, gun in ipairs(entry[2]) do addTo(list, asReplacement(gun(entry[3], entry[4]))) end
            else
                print("[GunsOfTienPost93] Guns of Marz's " .. entry[1] .. " replacement not found, Extend Loot Areas leaves it")
            end
        end
    end
end

Events.OnInitGlobalModData.Add(addSpawners)

-------------------------------------------------
-- GoM's spawners in new places
-------------------------------------------------
-- Before the merge, as GoM inserts its own (OnPreDistributionMerge), so they are in the merged lists the same way.
local function addSpawnerLoot()
    local multiplier = lootMultiplier()
    if multiplier <= 0 then return end
    local distributions = { pd = ProceduralDistributions.list, vd = VehicleDistributions, bd = BagsAndContainers }
    local function place(places)
        for _, entry in ipairs(places) do
            local list = distributions[entry[2]] and distributions[entry[2]][entry[3]]
            if type(list) == "table" and type(list.items) == "table" then
                list.items[#list.items + 1] = entry[1]
                list.items[#list.items + 1] = entry[4] * multiplier
            end
        end
    end
    place(PLACES)
    if extendLootAreas() then place(EXTENDED_PLACES) end
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
