--[[
    Guns of Tien -- the PPSh-41 submachine gun in 7.62x25mm (user, 2026-11-23: the Tokarev release, with the TT-33)
    in Gunworks' and Guns of Marz's registries, on GoM's Thompson pattern (items_ppsh41.txt):

    - feed: its 71-round drum and the 35-round box of 1942, one profile of their own, both in the main mod's
      "7.62x25mm" family (the plain round, Steel Core and Subsonic; Post-93's Hollow Point);
    - about 900 rounds a minute, automatic with single shots on its selector; GoM's Thompson spread;
    - the cocking handle is fixed to the bolt and runs with it on every shot, so it is the gun's Bolt part on GoM's
      swap (PPSH41_BOLT), no ChargingHandle part. It fires from an open bolt; Gunworks' states are kept (back after
      each shot and while empty, the Uzis' and the RPD's rule, user 2026-10-30);
    - reload: GoM's Thompson reload (GoMReloads.lua), the magazine in the off hand at its own size;
    - held with GoM's SMG stance, as GoM holds its Thompson (GripStances.lua);
    - no GoM parts: no rail and no thread (the muzzle compensator is part of the barrel jacket).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims", "PermanentAttachments",
    "ReloadsAndAnims/AnimationsFiring" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local PPSH41 = M .. "PPSH41"
local DRUM = M .. "762x25Drum71_PPSH41"
local BOX = M .. "762x25Magazine35_PPSH41"
local MAGS = { DRUM, BOX }

-------------------------------------------------
-- Feed: the drum and the box, in the main mod's 7.62x25mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x25mm PPSh-41", MAGS)
Magazine.RegisterWeaponWithProfile("7.62x25mm PPSh-41", PPSH41)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x25mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire); GoM's Thompson spread
-------------------------------------------------
RateOfFire.RegisterWeapon(PPSH41, { rpm = 900, enableSpread = true, sustainedSpread = 0.3, maxSpread = 4.5 })

-------------------------------------------------
-- The cocking handle on the bolt (GoM's bolt swap, as its Thompson)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(PPSH41, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})

-------------------------------------------------
-- Reload: GoM's Thompson reload, the magazine swapped as the action ends
-------------------------------------------------
ReloadAnim.RegisterWeapon(PPSH41, require("GunsOfTien/GoMReloads").profile("thompson_marz"))

-------------------------------------------------
-- The magazines cannot be taken off through the vanilla upgrade menu (they go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, a magazine at GoM's chance
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[PPSH41] = { required = { "MarzGuns.Bolt_Lock" }, optionals = { DRUM .. ":50" } }
end

GunsOfTien_PPSH41 = { GUN = PPSH41, DRUM = DRUM, BOX = BOX, MAGS = MAGS }
