--[[
    Guns of Tien -- the Steyr TMP (docs/design.md 4m; user, 2026-11-11) in Gunworks' and Guns of Marz's registries.

    Steyr's 9x19mm machine pistol (designed 1989, made 1992-2001), registered as GoM registers its MP5K / MAC-10 and
    as the Mini Uzi: held like a pistol and holstered (items_tmp.txt):
    - its own magazine profile, "9x19mm TMP", with Steyr's 15 and 30-round polymer magazines only (user, 2026-11-11),
      in GoM's 9x19mm family (its rounds and the main mod's 147gr / Hollow Point / [+P+]);
    - 900 rpm (Steyr's 850-900), select fire Auto / Single; the fixed front grip holds it steadier than the Micro Uzi
      (1200 rpm, 0.25 / 2.8), wilder than the Mini (950, 0.18 / 2.2): 0.2 / 2.4;
    - the bolt seen through the ejection port on the right moves as GoM animates its MP5K / MAC-10 (its Bolt_Lock /
      Bolt_Fired swap: back on each shot and on an empty gun); the cocking knob at the rear top slides straight back
      only while racked (ChargingHandle.lua);
    - reload: GoM's own animations (GoMReloads.lua), its MP5K's ("handgun2");
    - AWC's Mk9 on the 9x19mm SMG mount device over its threaded barrel (Suppressors.lua has the can's stats and
      rule, the parts' MountOn and the gun's ModelWeaponPart lines are in their scripts);
    - no stock (Steyr's optional fixed stock came later), no bayonet;
    - GoM's optional Picatinny rails (user, 2026-11-12; Rails.lua): the top for red dots (as the Uzi: longer optics
      overhang a gun this short), the left for lights, the right (ahead of the ejection port) for lasers, drawn as our
      short TMP_RAIL_* (build_rails.py). No bottom rail: the front grip is moulded into the frame.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local TMP = M .. "TMP"
local MAGS = { M .. "9x19Magazine15_TMP", M .. "9x19Magazine30_TMP" }

-------------------------------------------------
-- Magazines: the TMP's own profile, in GoM's 9x19mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x19mm TMP", MAGS)
Magazine.RegisterWeaponWithProfile("9x19mm TMP", TMP)
Ammo.RegisterMultipleItemsWithFamilies({ ["9x19mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire)
-------------------------------------------------
RateOfFire.RegisterWeapon(TMP, { rpm = 900, enableSpread = true, sustainedSpread = 0.2, maxSpread = 2.4 })

-------------------------------------------------
-- The bolt in the ejection port: GoM's bolt swap; the cocking knob, back only while racked
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(TMP, ChargingHandle.ANIMATED_PARTS)

-------------------------------------------------
-- Reload animation: GoM's (GoMReloads.lua), held like a pistol on its MP5K's
-------------------------------------------------
local GoMReloads = require("GunsOfTien/GoMReloads")
ReloadAnim.RegisterWeapon(TMP, GoMReloads.profile("handgun2"))

local Rails = require("GunsOfTien/Rails")
Rails.Register(TMP, { sides = { "Up", "Left", "Right" }, optics = Rails.RED_DOTS, lights = true, lasers = true })

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the cocking knob, one magazine by GoM's MP5
-- rule (the 30 the TMP was issued with likelier than the short 15), a mount device sometimes, as GoM's MP5 / MAC-10
-- come with theirs; GoM's MP5 accessories with their rails (":PR*") at its chances, as the Uzi's, plus its lasers.
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[TMP] = {
        required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD },
        optionals = { MAGS[2] .. ":30", MAGS[1] .. ":20", M .. "SMG9_Muzzle_Mount_Device:5" },
    }
    local list = spawnTable[TMP].optionals
    for _, optic in ipairs(Rails.RED_DOTS) do list[#list + 1] = optic .. ":5:PRU" end
    for _, e in ipairs({ "MarzGuns.BrightPoint-5_Light:10:PRL", "MarzGuns.SR7_Light:10:PRL",
        "MarzGuns.AimRight_Laser:2:PRR", "MarzGuns.LRX-7_Laser:2:PRR" }) do
        list[#list + 1] = e
    end
end

GunsOfTien_TMP = { TMP = TMP, MAGS = MAGS }
