--[[
    Guns of Tien -- the Walther PPK in .22 LR (user, 2026-11-19: "one mag only", "should fit an ankle holster") in
    Gunworks' and Guns of Marz's registries.

    Carl Walther's PPK of 1931 in .22 long rifle, as the post-war Ulm gun found in the US in 1993 (scripts/build_ppk.py),
    registered as GoM registers its pistols and as the Glock 21 is (items_ppk.txt):
    - its 8-round magazine, the only one, a profile of its own in the main mod's ".22 LR" family (the plain round and
      the Subsonic, Hollow Point and Hyper Velocity loads; Post-93's HK416 .22 is the other gun of the family);
    - the slide swapped on each shot (GoM's Slide_Fired / Slide_Lock), no rate of fire (semi-automatic only);
    - reload: GoM's own pistol animation (GoMReloads.lua);
    - no GoM parts: its sights, lights, lasers and cans dwarf a 155 mm pistol, and the .22 PPK had no rail or thread;
    - holstered as GoM's Detective .38 and our Micro Uzi are (AttachmentType HolsterSmall), so the ankle holster
      takes it too;
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
local PPK = M .. "PPK"
local MAGS = { M .. "22LRMagazine8_PPK" }

-------------------------------------------------
-- Magazine: its own profile, in the main mod's .22 LR family
-------------------------------------------------
Magazine.RegisterMagazineProfile(".22 LR PPK", MAGS)
Magazine.RegisterWeaponWithProfile(".22 LR PPK", PPK)
Ammo.RegisterMultipleItemsWithFamilies({ [".22 LR"] = MAGS })

-------------------------------------------------
-- The slide (GoM's pistol slide swap, as its Glock 17) and GoM's pistol reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(PPK, {
    SingleAttachment = { open = "MarzGuns.Slide_Fired", locked = "MarzGuns.Slide_Lock" },
    cycleTicks = 5,
})
require("WeaponSystems/ReloadAnim/HandlerFactory").RegisterWeapon(PPK,
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
    spawnTable[PPK] = {
        required = { "MarzGuns.Slide_Lock" },
        optionals = { MAGS[1] .. ":50" },
    }
end

GunsOfTien_PPK = { GUN = PPK, MAGS = MAGS }
