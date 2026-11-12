--[[
    Guns of Tien -- Knight's SR-25 Match (docs/design.md 4l; user, 2026-11-11) in Gunworks' and Guns of Marz's
    registries.

    Stoner's 7.62x51mm AR-10 revival as first sold (1990): a 24" match barrel, a free-float tube, semi-automatic only
    (no rate of fire registered, as GoM's AR-15 / M14 / PSG-1). Built on GoM's AR15 receiver (scripts/build_sr25.py):
    - magazines: KAC's steel 20 in the "7.62x51mm SR-25" profile, in GoM's 7.62x51mm family; Post-93's PMAGs (the
      SR-25 pattern) join the same profile (Gunworks merges profiles registered under one name) and list the SR-25
      in their MountOn;
    - GoM's AR bolt and charging handle as on its AR15 (GoM's own table, local to its AnimationsFiring.lua, repeated
      here): the bolt on each shot, the T-handle back while racked; GoM's AR15 reload ("ar15_rifle" with its
      "boltCatchAfterEmptyInsert" rule);
    - integrated: the Leupold Vari-X III 3.5-10x (user, 2026-11-11 "integrated scope", GoM's LR10X stats, user
      2026-11-12) as a hidden Scope part; the Harris bipod on the handguard's stud as Gunworks' FoldingBipod (found
      folded) with GoM's rail bipod stats deployed (no spread modifier: semi-automatic) and Gunworks' bipod stance.
    No muzzle parts or rails (the match rifle had none); no optics, its scope is fixed.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local Animations = require("WeaponSystems/Utils/Animations")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local BipodSystem = require("WeaponSystems/Utils/BipodSystem")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local GoMReloads = require("GunsOfTien/GoMReloads")

for _, file in ipairs({ "Ammunition", "Magazines", "ReloadsAndAnims/ReloadAnims", "ReloadsAndAnims/AnimationsFiring",
    "Bipods", "AttachmentCustomStats", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local SR25 = M .. "SR25"
local MAG = M .. "762x51Magazine20_SR25"
local SCOPE = M .. "SR25_Integrated_Scope"
local FOLDED = M .. "SR25_Integrated_Bipod_Folded"
local DEPLOYED = M .. "SR25_Integrated_Bipod_Deployed"

-------------------------------------------------
-- Magazines: KAC's 20 in the SR-25 pattern's profile (Post-93's PMAGs join it), GoM's 7.62x51mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x51mm SR-25", { MAG })
Magazine.RegisterWeaponWithProfile("7.62x51mm SR-25", SR25)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x51mm"] = { MAG } })

-------------------------------------------------
-- GoM's AR15 bolt and charging handle (its Bolt_AR15 entry), GoM's AR15 reload
-------------------------------------------------
local BOLT_AR15 = {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
    reload = {
        MultipleAttachment = {
            Bolt            = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
            Charging_Handle = { open = "MarzGuns.Charging_Handle_Open", locked = "MarzGuns.Charging_Handle_Close" },
        },
        close = {
            MultipleAttachment = {
                Bolt = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
            },
        },
    },
}
Animations.RegisterWeaponWithAnimatedParts(SR25, BOLT_AR15)
ReloadAnim.RegisterWeapon(SR25, GoMReloads.profile("ar15_rifle", { rules = "boltCatchAfterEmptyInsert" }))

-------------------------------------------------
-- The integrated scope (GoM's LR10X) and bipod (GoM's rail bipod, semi-automatic: no spread modifier)
-------------------------------------------------
FoldingBipod.RegisterWeapon(SR25, {
    attachments = { partType = "BipodIntegrated", folded = FOLDED, deployed = DEPLOYED },
    initialState = "folded",
})
BipodSystem.RegisterBipod(DEPLOYED)
CSA.RegisterMultipleParts({
    [SCOPE] = {
        SF.Multiply("AimingTime", 1.35),
        SF.Multiply("CriticalChance", 1.3),
        SF.Multiply("HitChance", 1.3),
        SF.Multiply("MaxSightRange", 1.7),
        SF.Multiply("MinSightRange", 1.7),
    },
    [FOLDED] = {},
    [DEPLOYED] = {
        SF.Multiply("AimingTime", 1.1),
        SF.Multiply("CriticalChance", 1.15),
        SF.Multiply("HitChance", 1.15),
    },
})

PreventRemoval.Register({ MAG, SCOPE })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): GoM's AR15 bolt and handle, the scope, the
-- bipod folded, KAC's 20 at GoM's PSG-1 magazine chance
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[SR25] = {
        required = { "MarzGuns.Bolt_Lock", "MarzGuns.Charging_Handle_Close", SCOPE, FOLDED },
        optionals = { MAG .. ":40" },
    }
end

GunsOfTien_SR25 = { SR25 = SR25, MAG = MAG, SCOPE = SCOPE, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
