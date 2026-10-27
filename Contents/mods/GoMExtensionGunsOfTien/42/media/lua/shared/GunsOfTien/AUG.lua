--[[
    Guns of Tien -- the Steyr AUG A1 (docs/design.md 4g; user, 2026-10-27) in Gunworks' and Guns of Marz's registries.

    Steyr's bullpup of 1977 (the Austrian Army's StG 77), imported to the US as the semi-automatic AUG/SA until the
    1989 import ban; registered as GoM registers its FAMAS (items_aug.txt):
    - its own magazine profile "5.56x45mm AUG" (Steyr's translucent 30 and 42; the A1 takes no STANAG), in GoM's
      5.56x45mm family (its 5.56 loads and .223);
    - 700 rpm (Steyr gives 680-750), steadier than GoM's FAMAS (1000) and FNC (750) between them, select fire Auto /
      Single (the A1's two-stage trigger);
    - the charging handle on the left rides with the bolt carrier: GoM's Bolt_Lock / Bolt_Fired swap moves it;
    - hold and reload: the bullpup set shared with GoM's FAMAS (Bullpup.lua; docs/design.md 4h);
    - the integral 1.5x scope, a hidden part with no model, below GoM's 2x Elcan: Aiming Time x1.05, Hit and Crit
      Chance x1.05, sight range x1.15;
    - the folding front grip (shared/GunsOfTien/Foregrip.lua swaps its two parts), unfolded with GoM's Stub Foregrip
      stats and spread, as Post-93's MP7A1;
    - no rails, optics, lights, lasers, bayonet or muzzle parts (user, 2026-10-27: none fit a 1993 A1).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Foregrip = require("GunsOfTien/Foregrip")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "AnimationsFiring", "AttachmentCustomStats",
    "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local AUG = M .. "AUG"
local MAGS = { M .. "556x45Magazine30_AUG", M .. "556x45Magazine42_AUG" }
local FOLDED = M .. "AUG_Integrated_Foregrip_Folded"
local DEPLOYED = M .. "AUG_Integrated_Foregrip_Deployed"
local SCOPE = M .. "AUG_Integrated_Scope"

-------------------------------------------------
-- Magazines: Steyr's own, in GoM's 5.56x45mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("5.56x45mm AUG", MAGS)
Magazine.RegisterWeaponWithProfile("5.56x45mm AUG", AUG)
Ammo.RegisterMultipleItemsWithFamilies({ ["5.56x45mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire); the unfolded grip steadies it as GoM's Stub Foregrip does
-------------------------------------------------
RateOfFire.RegisterWeapon(AUG, { rpm = 700, enableSpread = true, sustainedSpread = 0.12, maxSpread = 2.5 })
RateOfFire.RegisterSpreadPartModifier(DEPLOYED, { sustainedSpreadMult = 0.85, maxSpreadMult = 0.85 })

-------------------------------------------------
-- The charging handle rides with the bolt (GoM's rifles' bolt swap)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(AUG, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})

-- Hold and reload: the bullpup set, shared with GoM's FAMAS (Bullpup.lua)

-------------------------------------------------
-- Integrated parts: the 1.5x scope, the folding grip (GoM's Stub Foregrip numbers unfolded)
-------------------------------------------------
CSA.RegisterMultipleParts({
    [SCOPE] = {
        SF.Multiply("AimingTime", 1.05),
        SF.Multiply("CriticalChance", 1.05),
        SF.Multiply("HitChance", 1.05),
        SF.Multiply("MaxSightRange", 1.15),
        SF.Multiply("MinSightRange", 1.15),
    },
    [FOLDED] = {},
    [DEPLOYED] = {
        SF.Multiply("AimingTime", 0.8),
        SF.Multiply("CriticalChance", 1.15),
        SF.Multiply("HitChance", 1.15),
    },
})
Foregrip.Register(AUG, {
    folded = FOLDED,
    deployed = DEPLOYED,
    foldDesc = "IGUI_GunsOfTien_AUGFoldForegripDesc",
    unfoldDesc = "IGUI_GunsOfTien_AUGUnfoldForegripDesc",
})

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the scope, the grip folded, its 30 at
-- GoM's FAMAS chance for a 30, the 42 rarely (it comes loose in GoM's high-capacity AR spawner, Loot.lua).
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[AUG] = {
        required = { "MarzGuns.Bolt_Lock", SCOPE, FOLDED },
        optionals = { MAGS[1] .. ":30", MAGS[2] .. ":5" },
    }
end

GunsOfTien_AUG = { AUG = AUG, MAGS = MAGS, SCOPE = SCOPE, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
