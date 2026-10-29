--[[
    Guns of Tien -- the Uzi, Mini Uzi and Micro Uzi (docs/design.md 4f; user, 2026-10-23) in Gunworks' and Guns of
    Marz's registries.

    IMI's open-bolt 9mm family, registered as GoM registers its MP5K / MAC-10, all three held like a pistol (the Uzi
    since 2026-10-30, user: "the rifle stance doesn't look good on it"; it still hangs on the back, the Mini and Micro
    are holstered; items_uzi.txt):
    - one magazine profile, "9x19mm Uzi", for all three (IMI's 20 / 25 / 32 and the long 40 / 50 fit every Uzi), the
      magazines in GoM's 9x19mm family (its rounds and the main mod's 147gr / Hollow Point / [+P+]);
    - rate of fire 600 / 950 / 1200 rpm (IMI's figures), the slow heavy Uzi steadier than GoM's MP5 (800, 0.1 / 1.5),
      the Micro wilder than its MAC-10 (1000, 0.2 / 2.0); select fire Auto / Single;
    - stocks: the Uzi's folding metal stock with GoM's MP5 stock stats, the Mini's and Micro's side-folding stock with
      its MAC-10's (Gunworks' FoldingStock, parts in items_uzi.txt), each folded on a found gun as GoM's;
    - the bolt seen through the ejection port on the right moves as GoM animates its MP5K / MAC-10 (its Bolt_Lock /
      Bolt_Fired swap: back on each shot and on an empty gun); IMI's top cocking knob does not reciprocate, so it
      slides back along its top cover slot only while racked (ChargingHandle.lua; user, 2026-10-30);
    - reload: GoM's own animations (GoMReloads.lua), its MP5K's ("handgun2") for all three;
    - AWC's Mk9 on its 9x19mm SMG mount device (the real Mk9 replaced the Uzi's barrel nut; Suppressors.lua has the
      can's stats and rule, the parts' MountOn and the guns' ModelWeaponPart lines are in their scripts);
    - no rails, optics, lights, lasers or bayonet (none on a 1993 Uzi).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadAnims", "Stocks", "AttachmentCustomStats",
    "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local UZI = M .. "UZI"
local MINIUZI = M .. "MINIUZI"
local MICROUZI = M .. "MICROUZI"
local GUNS = { UZI, MINIUZI, MICROUZI }
local MAGS = {}
for _, n in ipairs({ 20, 25, 32, 40, 50 }) do
    MAGS[#MAGS + 1] = M .. "9x19Magazine" .. n .. "_UZI"
end

-------------------------------------------------
-- Magazines: one profile for the three guns, in GoM's 9x19mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x19mm Uzi", MAGS)
for _, gun in ipairs(GUNS) do
    Magazine.RegisterWeaponWithProfile("9x19mm Uzi", gun)
end
Ammo.RegisterMultipleItemsWithFamilies({ ["9x19mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire)
-------------------------------------------------
RateOfFire.RegisterWeapon(UZI, { rpm = 600, enableSpread = true, sustainedSpread = 0.08, maxSpread = 1.3 })
RateOfFire.RegisterWeapon(MINIUZI, { rpm = 950, enableSpread = true, sustainedSpread = 0.18, maxSpread = 2.2 })
RateOfFire.RegisterWeapon(MICROUZI, { rpm = 1200, enableSpread = true, sustainedSpread = 0.25, maxSpread = 2.8 })

-------------------------------------------------
-- The bolt in the ejection port: GoM's bolt swap (its AnimationsFiring.lua "Bolt"); the cocking knob, back only while
-- racked
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ChargingHandle.Register(gun)
end

-------------------------------------------------
-- Reload animations: GoM's (GoMReloads.lua), all three held like a pistol on its MP5K's
-------------------------------------------------
local GoMReloads = require("GunsOfTien/GoMReloads")
for _, gun in ipairs(GUNS) do
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("handgun2"))
end

-------------------------------------------------
-- Folding stocks: the Uzi's with GoM's MP5 stock stats, the Mini's and Micro's with its MAC-10's
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    local name = gun:sub(#M + 1)
    FoldingStock.RegisterWeapon(gun, {
        attachments = {
            partType = "StockIntegrated",
            folded = M .. name .. "_Integrated_Stock_Folded",
            deployed = M .. name .. "_Integrated_Stock_Deployed",
        },
        initialState = "folded",
    })
end
CSA.RegisterMultipleParts({
    [M .. "UZI_Integrated_Stock_Folded"] = {},
    [M .. "UZI_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.75),
    },
    [M .. "MINIUZI_Integrated_Stock_Folded"] = {},
    [M .. "MINIUZI_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.1),
        SF.Multiply("AimingTime", 0.9),
    },
    [M .. "MICROUZI_Integrated_Stock_Folded"] = {},
    [M .. "MICROUZI_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.1),
        SF.Multiply("AimingTime", 0.9),
    },
})

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the cocking knob, the stock folded, one
-- magazine by GoM's MP5 rule (shortest likeliest), each gun's standard magazine first: the Uzi's 32, the Mini's and
-- Micro's 20. The long 40 / 50 come loose only (server/GunsOfTien/Loot.lua); a mount device sometimes, as GoM's MP5 /
-- MAC-10 come with theirs.
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local function entry(gun, mags)
        local optionals = {}
        for _, e in ipairs(mags) do optionals[#optionals + 1] = e end
        optionals[#optionals + 1] = M .. "SMG9_Muzzle_Mount_Device:5"
        return {
            required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD, gun .. "_Integrated_Stock_Folded" },
            optionals = optionals,
        }
    end
    spawnTable[UZI] = entry(UZI, { MAGS[3] .. ":30", MAGS[2] .. ":20", MAGS[1] .. ":5" })
    spawnTable[MINIUZI] = entry(MINIUZI, { MAGS[1] .. ":30", MAGS[2] .. ":20", MAGS[3] .. ":5" })
    spawnTable[MICROUZI] = entry(MICROUZI, { MAGS[1] .. ":30", MAGS[2] .. ":20", MAGS[3] .. ":5" })
end

GunsOfTien_Uzi = { UZI = UZI, MINIUZI = MINIUZI, MICROUZI = MICROUZI, GUNS = GUNS, MAGS = MAGS }
