--[[
    Guns of Tien -- the FN P90 with its ring sight (user, 2026-11-03; scripts/build_p90std.py, items_p90.txt) in
    Gunworks' and Guns of Marz's registries, and the P90 family's parts it brought into the main mod.

    The P90 as FN made it from 1990: the P90 TR of Post-93 with its original upper and the HC-14 ring sight instead of
    the TR's three rails, mechanically the same gun, registered as Post-93 registers the TR (its Guns.lua):
    - the "5.7x28mm P90" magazine profile (the P90's 50-round magazine; Post-93's P90 TR and PS90 join it), the
      magazine in the 5.7x28mm family (shared/GunsOfTien/Ammunition.lua: SS190 here, Post-93's SB193 / SS197SR);
    - 900 rpm, select fire Auto / Single, spreading less than GoM's MP5 (light recoil);
    - held like a pistol (GoM's MP5K way), so GoM's MP5K reload ("handgun2", GoMReloads.lua);
    - the bolt in the port under the gun on GoM's Bolt_Lock / Bolt_Fired swap, the charging handles back only while
      racked (ChargingHandle.lua);
    - the SP90 on the 5.7x28mm mount device when Post-93 is on (both are Post-93's, post-1993: their stats, rule and
      loot are there; their MountOn lists this P90);
    - GoM's optional Picatinny rails on the housing's sides only (user, 2026-11-03: "optional picatinny rails upgrade
      instead of integrated", "there should be no optional top rail for p90"; Rails.lua), where FN put its own later:
      its lights (left) and lasers (right), drawn as our P90_RAIL_LEFT / _RIGHT. No top rail, so no optics: the ring
      sight is its sight, without stats as a gun's own sights have none in GoM.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")
local GoMReloads = require("GunsOfTien/GoMReloads")
local Rails = require("GunsOfTien/Rails")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadAnims", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local P90 = "GunsOfTien.P90"
local M93 = "GunsOfTienPost93."
local MAG = M93 .. "57x28Magazine50_P90"

-------------------------------------------------
-- The P90 family's magazine profile (Post-93's P90 TR and PS90 register with it there)
-------------------------------------------------
Magazine.RegisterMagazineProfile("5.7x28mm P90", { MAG })
Magazine.RegisterWeaponWithProfile("5.7x28mm P90", P90)
PreventRemoval.Register({ MAG })

-------------------------------------------------
-- 900 rpm, light-recoiling (the TR's numbers)
-------------------------------------------------
RateOfFire.RegisterWeapon(P90, { rpm = 900, enableSpread = true, sustainedSpread = 0.06, maxSpread = 1.1 })

Animations.RegisterWeaponWithAnimatedParts(P90, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})
ChargingHandle.Register(P90)
ReloadAnim.RegisterWeapon(P90, GoMReloads.profile("handgun2"))

-------------------------------------------------
-- GoM's optional rails: left (lights) and right (lasers); no top rail
-------------------------------------------------
Rails.Register(P90, { sides = { "Left", "Right" }, lights = true, lasers = true })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the TR's chances, each accessory with its rail
-- (GoM's ":PR*" suffixes)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[P90] = {
        required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD },
        optionals = {
            MAG .. ":60",
            "MarzGuns.AimRight_Laser:5:PRR", "MarzGuns.LRX-7_Laser:5:PRR",
            "MarzGuns.BrightPoint-5_Light:10:PRL", "MarzGuns.SR7_Light:10:PRL",
        },
    }
end

GunsOfTien_P90 = { P90 = P90, MAG = MAG }
