--[[
    Guns of Tien - Post-93 -- the PP-19 Bizon family (user, 2026-11-27: "We can build 4 guns. Bizon Parabellum, Bizon
    Tokarev, Bizon Makarov and Vityaz"; CLAUDE.md and docs/post93_design.md "PP-19 Bizon family") in Gunworks' and
    Guns of Marz's registries. Meshes: scripts/post93/build_bizon.py; scripts: gen_post93_guns.py bizon().

    Four guns on the AKS-74's receiver, registered as the 9A-91 is (9A91.lua): all held as rifles, two-handed, never
    holstered (the stockless PP-19 too), GoM's AK reload ("ak_rifle") with our magazine in the off hand, the carrier's
    handle on the right moving on each shot and closing on an empty chamber (GoM's AK bolt swap, the main mod's RPK.lua
    wrapper), Auto / Single:
    - PP-19 Bizon (1993, 9x18mm Makarov): its own 64-round helical, 650 rpm, no stock (a short gun held by its grip
      and handguard: wider spread than its stocked brothers), its compensator part of the body (no muzzle parts);
    - Bizon-2-01 (9x19mm): its own 53-round helical, 680 rpm, the AKS-74 folding stock with GoM's AKS-74U stock stats
      and spread, the 9x19mm muzzle family (mount device, the Mk9, GoM's M&P and Shh9, as the UMP9);
    - Bizon-2-07 (1997, 7.62x25mm Tokarev): the real 35-round box and an invented 45-round helical in one profile
      (as the main mod's RPK takes its 40 and drum), 700 rpm, a fixed stock, its railed handguard's integrated left
      and right rails as parents of GoM's lights and lasers (no top rail: optics go on the AK mount, user
      2026-11-28), no muzzle parts (no 7.62x25mm muzzle family);
    - Vityaz (PP-19-01, 2004, 9x19mm): its own 30-round box and the clipped pair (Gunworks' stacked pack, GoM's MP5
      jungle pair way: the two sides are two items, a reload flips the pack with GoM's jungle animation; taped and
      parted by recipes as GoM's), 750 rpm, the AKS-74 stock as the -2-01's, the 9x19mm muzzle family.
    Optics: GoM's AK side mount on the dovetail rail modelled on the receiver's left (all four, as the real guns),
    and every GoM optic on it (MountOn appended; GoM's own rule puts optics on the mount). GoM's
    optional Picatinny rails: the PP-19 and -2-01 left and right on the handguard, the Vityaz below, left and right
    (the main mod's Rails.lua); no optional top rail on the PP-19 and -2-01: it would take the AK mount's slot (both
    PartType RailUp) and an optic has one height on the gun (gen_post93_guns.py bizon()).
    A found gun: the bolt, a stock folded, its standard magazine at GoM's AKS-74U chances, now and then an optic on
    the AK mount (":AM", the 9A-91's chances); the long magazines (the -2-07's
    helical, the Vityaz pair) rarely.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local GoMReloads = require("GunsOfTien/GoMReloads")
local Rails = require("GunsOfTien/Rails")
require("GunsOfTien/RPK")                    -- the AK bolt wrapper (GunsOfTien_RPK.CLOSES_ON_EMPTY)

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "Stocks", "ReloadsAndAnims/ReloadAnims",
    "ReloadsAndAnims/AnimationsFiring", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments",
    "StackedMagazines" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local BIZON, BIZON201, BIZON207, VITYAZ = M .. "BIZON", M .. "BIZON201", M .. "BIZON207", M .. "VITYAZ"
local GUNS = { BIZON, BIZON201, BIZON207, VITYAZ }
local AK_MOUNT_GUNS = GUNS
local NINE_GUNS = { BIZON201, VITYAZ }
local MAG64 = M .. "9x18Magazine64_BIZON"
local MAG53 = M .. "9x19Magazine53_BIZON"
local BOX35 = M .. "762x25Magazine35_BIZON"
local HELIX45 = M .. "762x25Magazine45_BIZON"
local V30 = M .. "9x19Magazine30_VITYAZ"
local PAIR, PAIR2 = M .. "9x19Magazine30_VITYAZ_PAIR", M .. "9x19Magazine30_VITYAZ_PAIR_2"
local ALL_MAGS = { MAG64, MAG53, BOX35, HELIX45, V30, PAIR, PAIR2 }
local STOCKS = {
    [BIZON201] = { folded = M .. "BIZON201_Integrated_Stock_Folded", deployed = M .. "BIZON201_Integrated_Stock_Deployed" },
    [VITYAZ] = { folded = M .. "VITYAZ_Integrated_Stock_Folded", deployed = M .. "VITYAZ_Integrated_Stock_Deployed" },
}
local RAIL_LEFT, RAIL_RIGHT = M .. "BIZON207_Integrated_Rail_Left", M .. "BIZON207_Integrated_Rail_Right"

local OPTIC_NAMES = { "EXPS1_Sight", "EXPS3_Sight", "ElcanX2_Scope", "LR10X_Scope", "Aimpoint_Sight", "TA28_Scope",
    "LR4X_Scope", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "Kobra_Sight", "TR06X_Scope", "PSO1_Scope",
    "LRX12X_Scope" }
local OPTICS = {}
for _, o in ipairs(OPTIC_NAMES) do OPTICS[#OPTICS + 1] = "MarzGuns." .. o end
local NINE_PARTS = { "MarzGuns.Pistol_Muzzle_Mount_Device", "GunsOfTien.SMG9_Muzzle_Mount_Device",
    "GunsOfTien.Mk9_Suppressor", "MarzGuns.M&P_Suppressor", "MarzGuns.Shh9_Suppressor" }

-------------------------------------------------
-- Magazines: one profile per calibre (magazines never cross between the guns), in the rounds' families
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x18mm Bizon", { MAG64 })
Magazine.RegisterWeaponWithProfile("9x18mm Bizon", BIZON)
Magazine.RegisterMagazineProfile("9x19mm Bizon", { MAG53 })
Magazine.RegisterWeaponWithProfile("9x19mm Bizon", BIZON201)
Magazine.RegisterMagazineProfile("7.62x25mm Bizon-2-07", { BOX35, HELIX45 })
Magazine.RegisterWeaponWithProfile("7.62x25mm Bizon-2-07", BIZON207)
Magazine.RegisterMagazineProfile("9x19mm Vityaz", { V30, PAIR, PAIR2 })
Magazine.RegisterWeaponWithProfile("9x19mm Vityaz", VITYAZ)
Ammo.RegisterMultipleItemsWithFamilies({
    ["9x18mm"] = { MAG64 },
    ["9x19mm"] = { MAG53, V30, PAIR, PAIR2 },
    ["7.62x25mm"] = { BOX35, HELIX45 },
})
-- the Vityaz pair: GoM's MP5 jungle pair's registration with our two sides
local okStacked, StackedMagazines = pcall(require, "WeaponSystems/Utils/StackedMagazines")
if okStacked and StackedMagazines and StackedMagazines.RegisterMagazines then
    StackedMagazines.RegisterMagazines("9x19mm 2x30 Vityaz Dual Magazines", {
        magazines = { PAIR, PAIR2 },
        animation = "jungleMagReload",
        unloadDuration = 0.9,
        loadDuration = 1.0333,
    })
end

-------------------------------------------------
-- Rate of fire (factory figures: Bizon 650-700, Vityaz 700-800), spread between GoM's MP5 (0.1 / 1.5) and AKS-74U
-- (0.25 / 3.5): the light rounds' guns nearer the MP5, the stockless PP-19 wider
-------------------------------------------------
RateOfFire.RegisterWeapon(BIZON, { rpm = 650, enableSpread = true, sustainedSpread = 0.16, maxSpread = 2.0 })
RateOfFire.RegisterWeapon(BIZON201, { rpm = 680, enableSpread = true, sustainedSpread = 0.13, maxSpread = 1.8 })
RateOfFire.RegisterWeapon(BIZON207, { rpm = 700, enableSpread = true, sustainedSpread = 0.12, maxSpread = 1.8 })
RateOfFire.RegisterWeapon(VITYAZ, { rpm = 750, enableSpread = true, sustainedSpread = 0.12, maxSpread = 1.7 })

-------------------------------------------------
-- The bolt (GoM's AK bolt swap, closing on the empty chamber) and the reload (GoM's AK reload)
-------------------------------------------------
local closes = GunsOfTien_RPK and GunsOfTien_RPK.CLOSES_ON_EMPTY
for _, gun in ipairs(GUNS) do
    if closes then closes[gun] = true end
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("ak_rifle"))
end

-------------------------------------------------
-- The -2-01's and Vityaz's AKS-74 stock (GoM's AKS-74U stock: flat values since GoM's November 2026 update, and its
-- spread)
-------------------------------------------------
local stats = {}
for gun, s in pairs(STOCKS) do
    FoldingStock.RegisterWeapon(gun, {
        attachments = { partType = "StockIntegrated", folded = s.folded, deployed = s.deployed },
        initialState = "folded",
    })
    RateOfFire.RegisterSpreadPartModifier(s.deployed, { sustainedSpreadMult = 0.75, maxSpreadMult = 0.85 })
    stats[s.folded] = {}
    stats[s.deployed] = { SF.Adjust("HitChance", 8), SF.Adjust("AimingTime", -4) }
end
CSA.RegisterMultipleParts(stats)

-------------------------------------------------
-- Rails: GoM's optional ones (Rails.lua: the rail parts, the accessories on them, GoM's universal rail), and the
-- -2-07's integrated side rails as parents of GoM's lights and lasers
-------------------------------------------------
Rails.Register(BIZON, { sides = { "Left", "Right" }, lights = true, lasers = true })
Rails.Register(BIZON201, { sides = { "Left", "Right" }, lights = true, lasers = true })
Rails.Register(VITYAZ, { sides = { "Down", "Left", "Right" }, foregrips = true, lights = true, lasers = true })
RequiredAttachment.RegisterRequired(Rails.LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(Rails.LASERS, { RAIL_RIGHT })

PreventRemoval.Register(ALL_MAGS)
PreventRemoval.Register({ RAIL_LEFT, RAIL_RIGHT })

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as 9A91.lua does): GoM's AK
-- mount and its optics on all four, the lights and lasers on the -2-07's side rails, the 9x19mm muzzle family
-------------------------------------------------
local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local entry = tostring(current:get(i))
            if not seen[entry] then
                seen[entry] = true
                list[#list + 1] = entry
            end
        end
    end
    local changed = false
    for _, gun in ipairs(guns) do
        if not seen[gun] then
            seen[gun] = true
            list[#list + 1] = gun
            changed = true
        end
    end
    if changed then script:DoParam("MountOn = " .. table.concat(list, ";")) end
end

local function appendAll()
    appendMountOn("MarzGuns.AK_Mount", AK_MOUNT_GUNS)
    for _, part in ipairs(OPTICS) do appendMountOn(part, GUNS) end
    for _, list in ipairs({ Rails.LIGHTS, Rails.LASERS }) do
        for _, part in ipairs(list) do appendMountOn(part, { BIZON207 }) end
    end
    for _, part in ipairs(NINE_PARTS) do appendMountOn(part, NINE_GUNS) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)
-- and at once (user, 2026-11-25): a mod that lists a gun's slots from MountOn when its own Lua loads missed ours
pcall(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    -- GoM's optics on the AK mount (":AM"), the 9A-91's chances
    local function optics(suffix)
        local out = {}
        for _, o in ipairs({ "Kobra_Sight", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "EXPS3_Sight",
            "EXPS1_Sight", "Aimpoint_Sight" }) do out[#out + 1] = "MarzGuns." .. o .. ":3" .. suffix end
        for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope", "PSO1_Scope" }) do
            out[#out + 1] = "MarzGuns." .. o .. ":1" .. suffix
        end
        return out
    end
    local function entry(required, mags, suffix)
        local list = {}
        for _, m in ipairs(mags) do list[#list + 1] = m end
        for _, o in ipairs(optics(suffix)) do list[#list + 1] = o end
        return { required = required, optionals = list }
    end
    spawnTable[BIZON] = entry({ "MarzGuns.Bolt_Lock" }, { MAG64 .. ":50" }, ":AM")
    spawnTable[BIZON201] = entry({ "MarzGuns.Bolt_Lock", STOCKS[BIZON201].folded }, { MAG53 .. ":50" }, ":AM")
    spawnTable[BIZON207] = entry({ "MarzGuns.Bolt_Lock", RAIL_LEFT, RAIL_RIGHT },
        { BOX35 .. ":50", HELIX45 .. ":5" }, ":AM")
    local v = entry({ "MarzGuns.Bolt_Lock", STOCKS[VITYAZ].folded }, { V30 .. ":50", PAIR .. ":5" }, ":AM")
    spawnTable[VITYAZ] = v
end

GunsOfTienPost93_Bizon = { GUNS = GUNS, MAGS = ALL_MAGS }
