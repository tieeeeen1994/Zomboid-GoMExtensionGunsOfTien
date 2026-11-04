--[[
    Guns of Tien -- the RPD light machine gun, first model (docs/design.md 4k; user, 2026-11-02: "Older RPD pls.") in
    Gunworks' and Guns of Marz's registries, on GoM's M60 pattern as our M249 (items_rpd.txt):

    - feed: its 100-round belt drum only (a non-disintegrating belt coiled in a drum hung on the dovetail under the
      receiver; no belt shows outside it), one profile of its own, the drum in GoM's 7.62x39mm family so the 7.62x39
      loads of Ammunition.lua work in it. No belt-link rule (BeltLinks.lua: its belt does not come apart). US Subsonic
      racks after every shot (user, 2026-11-02): the rule in Ammunition.lua does it, as the PBS-1 never fits it;
    - 700 rpm (650-750), full auto only, as GoM's M60 spread;
    - the first model's straight operating handle is fixed to the slide and moves with it on every shot ("oscillated
      ... back and forth during firing", Small Arms Review), so it is the gun's Bolt part on GoM's swap (RPD_BOLT),
      no ChargingHandle part. It fires from an open bolt; Gunworks' states are kept (back after each shot and while
      empty, the M249's and Uzis' rule, user 2026-10-30);
    - the folding bipod: GoM's M60 bipod stats (deployed steadier, folded costs endurance and Hit), as the M249;
    - reload: GoM's M60 reload (GoMReloads.lua), the drum in the off hand at its own size (it is our model).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local BipodSystem = require("WeaponSystems/Utils/BipodSystem")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")

for _, file in ipairs({ "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims", "Bipods", "AttachmentCustomStats", "PermanentAttachments",
    "ReloadsAndAnims/AnimationsFiring", "Ammunition" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local RPD = M .. "RPD"
local DRUM = M .. "762x39Drum100_RPD"
local FOLDED = M .. "RPD_Integrated_Bipod_Folded"
local DEPLOYED = M .. "RPD_Integrated_Bipod_Deployed"

-------------------------------------------------
-- Feed: the belt drum, in GoM's 7.62x39mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("GunsOfTien_RPD", { DRUM })
Magazine.RegisterWeaponWithProfile("GunsOfTien_RPD", RPD)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x39mm"] = { DRUM } })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire); GoM's M60 spread, as the M249
-------------------------------------------------
RateOfFire.RegisterWeapon(RPD, { rpm = 700, enableSpread = true, sustainedSpread = 0.2, maxSpread = 3.5 })

-------------------------------------------------
-- The operating handle on the slide (GoM's bolt swap)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(RPD, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})

-------------------------------------------------
-- Integrated bipod: GoM's M60 bipod and its stats
-------------------------------------------------
FoldingBipod.RegisterWeapon(RPD, {
    attachments = { partType = "BipodIntegrated", folded = FOLDED, deployed = DEPLOYED },
    initialState = "folded",
})
-- Rests on low walls, windows and tables while aiming (Gunworks' bipod stance, as GoM registers its bipods)
BipodSystem.RegisterBipod(DEPLOYED)
CSA.RegisterMultipleParts({
    [DEPLOYED] = {
        SF.Multiply("AimingTime", 1.3),
        SF.Multiply("CriticalChance", 1.1),
        SF.Multiply("HitChance", 1.1),
    },
    [FOLDED] = {
        SF.Set("UseEndurance", true),
        SF.Set("EnduranceMod", 0.3),
        SF.Multiply("HitChance", 0.8),
    },
})

-------------------------------------------------
-- Reload: GoM's M60 reload, the drum swapped as the action ends
-------------------------------------------------
ReloadAnim.RegisterWeapon(RPD, require("GunsOfTien/GoMReloads").profile("m60_lmg"))

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (the drum goes with the reload)
-------------------------------------------------
PreventRemoval.Register({ DRUM })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the bipod folded, its drum at the
-- M249's chance for its box. No optics: the RPD has no mount.
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[RPD] = { required = { "MarzGuns.Bolt_Lock", FOLDED }, optionals = { DRUM .. ":50" } }
end

GunsOfTien_RPD = { RPD = RPD, DRUM = DRUM, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
