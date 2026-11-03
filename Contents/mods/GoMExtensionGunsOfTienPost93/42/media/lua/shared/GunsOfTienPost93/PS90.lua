--[[
    Guns of Tien - Post-93 -- the PS90 Carbine (user, 2026-11-03) in Gunworks' and Guns of Marz's registries: the P90
    TR's body with the PS90's 16" barrel, long flash hider and cheek riser and an M-LOK handguard, from the user's photo
    (scripts/post93/build_ps90.py), registered as the TR is (Guns.lua) with these differences:
    - held as a rifle, two-handed (its item script), so it reloads with GoM's FAMAS reload ("famas_rifle", as the
      AUGs): GoM has no top-loading reload, and the FAMAS is its other bullpup; the user turned down GoM's MP5 one.
      That node shows the magazine in the off hand (attachToHand), placed by the P90 magazine's Bip01_Prop2;
    - 900 rpm like the TR, spreading less (two hands, a heavier gun);
    - the P90's magazine, mount device and SP90 (their MountOn in the item scripts);
    - GoM's optics on the receiver's rail; its lights (left), lasers (right) and foregrips (below) on the M-LOK
      handguard, which has no rails drawn: four hidden integral rail parts stand in for M-LOK rail sections.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")
local GoMReloads = require("GunsOfTien/GoMReloads")
require("GunsOfTienPost93/Guns")             -- the "5.7x28mm P90" profile first: the carbine joins it

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadAnims", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local PS90 = M .. "PS90"
local P90_MAG = M .. "57x28Magazine50_P90"
local RAIL_UP = M .. "PS90_Integrated_Rail_Up"
local RAIL_DOWN = M .. "PS90_Integrated_Rail_Down"
local RAIL_LEFT = M .. "PS90_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "PS90_Integrated_Rail_Right"

-------------------------------------------------
-- The P90's magazine; 900 rpm, steadier than the TR (0.06 / 1.1) with both hands on it
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("5.7x28mm P90", PS90)
RateOfFire.RegisterWeapon(PS90, { rpm = 900, enableSpread = true, sustainedSpread = 0.05, maxSpread = 0.9 })

-------------------------------------------------
-- GoM's bolt swap (the bolt seen through the port under the gun), the charging handles back only while racked (the
-- TR's), GoM's FAMAS reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(PS90, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})
ChargingHandle.Register(PS90)
ReloadAnim.RegisterWeapon(PS90, GoMReloads.profile("famas_rifle"))

-------------------------------------------------
-- Rails: the four integral rails as parents of GoM's optics, foregrips, lights and lasers (each side takes one kind,
-- GoM's rule); the suppressor already needs the P90's mount device (Guns.lua)
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })

PreventRemoval.Register({ RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the TR's chances, with GoM's foregrips at its
-- MP5's
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[PS90] = {
        required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD, RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT },
        optionals = {
            P90_MAG .. ":60",
            "MarzGuns.EXPS1_Sight:10", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:10",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.Stub_Foregrip:10", "MarzGuns.MKC_Foregrip:10", "MarzGuns.MK2_Foregrip:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            M .. "P90_Muzzle_Mount_Device:10",
        },
    }
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as Guns.lua does)
-------------------------------------------------
local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local e = tostring(current:get(i))
            if not seen[e] then
                seen[e] = true
                list[#list + 1] = e
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
    for _, list in ipairs({ OPTICS, FOREGRIPS, LIGHTS, LASERS }) do
        for _, part in ipairs(list) do appendMountOn(part, { PS90 }) end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_PS90 = { PS90 = PS90 }
