--[[
    Guns of Tien -- the Tokarev TT-33 in 7.62x25mm (user, 2026-11-25: the Tokarev release) in Gunworks' and Guns of
    Marz's registries.

    Fedor Tokarev's service pistol of 1933, as the wartime Tula gun (scripts/build_tt.py), registered as GoM registers
    its pistols and as the Glock 21 and the PPK are (items_tt33.txt):
    - its 8-round magazine, a profile of its own in the main mod's "7.62x25mm" family (the plain round and the Steel
      Core and Subsonic loads; Post-93 adds a Hollow Point);
    - the slide swapped on each shot (GoM's Slide_Fired / Slide_Lock), no rate of fire (semi-automatic only);
    - reload: GoM's own pistol animation (GoMReloads.lua);
    - no GoM parts: it has no rail and no threaded barrel;
    - holstered as GoM's pistols (AttachmentType Holster);
    - a found gun comes with its magazine at 50 %, as GoM's pistols.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local Animations = require("WeaponSystems/Utils/Animations")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

for _, file in ipairs({ "Ammunition", "Magazines", "ReloadsAndAnims/AnimationsFiring", "ReloadsAndAnims/ReloadAnims", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local TT33 = M .. "TT33"
local MAGS = { M .. "762x25Magazine8_TT33" }

-------------------------------------------------
-- Magazine: its own profile, in the main mod's 7.62x25mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x25mm TT-33", MAGS)
Magazine.RegisterWeaponWithProfile("7.62x25mm TT-33", TT33)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x25mm"] = MAGS })

-------------------------------------------------
-- The slide (GoM's pistol slide swap, as its Glock 17) and GoM's pistol reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(TT33, {
    SingleAttachment = { open = "MarzGuns.Slide_Fired", locked = "MarzGuns.Slide_Lock" },
    cycleTicks = 5,
})
require("WeaponSystems/ReloadAnim/HandlerFactory").RegisterWeapon(TT33,
    require("GunsOfTien/GoMReloads").profile("pistol_reload"))

-------------------------------------------------
-- The magazine cannot be taken off through the vanilla upgrade menu (it goes with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table), as GoM's pistols come
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[TT33] = {
        required = { "MarzGuns.Slide_Lock" },
        optionals = { MAGS[1] .. ":50" },
    }
end

GunsOfTien_TT33 = { GUN = TT33, MAGS = MAGS }
