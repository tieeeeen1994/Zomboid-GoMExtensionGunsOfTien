--[[
    Guns of Tien - Post-93 -- Walther's HK416 .22 Tactical Pistol, shown as "HK416 .22 Quad Rail Pistol" (user,
    2026-11-13; docs/post93_design.md "H&K HK416 .22 LR pistols") in Gunworks' and Guns of Marz's registries.

    Carl Walther's licensed .22 LR copy of the HK416 (about 2009/10-2018), built on GoM's AR15 receiver like our HK416
    (scripts/post93/build_hk416_22.py). H&K USA's later M-LOK pistol was shelved (user: "let's use walther's").
    - held like a pistol (the Vector SDP's way: turned model, GoM's MP5K reload "handgun2"), back slot, never a holster;
    - semi-automatic only, as the real pistol (user, 2026-11-14: "make HK416 pistol semi automatic"; it was select
      fire Auto / Single at 900 rpm): FireMode Single, no FireModePossibilities and no RateOfFire registration, as the
      MDRs, so its pace is RecoilDelay 6 alone (about 5 shots a second at most; GoM's pistols 11-17);
    - H&K's polymer .22 magazines, 10 straight, 20 and 30 curved: a profile of their own, ".22 LR HK416", in the main
      mod's ".22 LR" family (its plain round and the Subsonic, Hollow Point and Hyper Velocity loads);
    - the long round barrel shroud is only a shroud, as on the real gun (user, 2026-11-13: "Plain shroud, loud"; it
      was an integral suppressor first): a .22 LR's sound from a 9" barrel (items_hk416_22.txt), no muzzle parts;
    - Walther's quad rail: four hidden integrated rails (HK416QR22_Integrated_Rail_Up / _Down / _Left / _Right,
      modelled in the body) as parents of GoM's optics (top), foregrips (bottom; user, 2026-11-13: "let it take a
      foregrip", as the pistol-held MP7A2 and Vector SDP), lights (left) and lasers (right);
    - the iron sights follow the optic (IronSights.lua): Walther's H&K-style sights are clamped on the rail and come
      off for an optic, the rear under a red dot (HK416QR22_RD), both under a magnified scope (HK416QR22_FD);
    - GoM's AR bolt and charging handle as on its AR15 (HK416.lua's table); a plain MP5K reload (GoM's AR bolt catch
      rule plays a close clip the MP5K's reload does not have).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local GoMReloads = require("GunsOfTien/GoMReloads")
local IronSights = require("GunsOfTienPost93/IronSights")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims",
    "ReloadsAndAnims/AnimationsFiring", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local GUN = M .. "HK416QR22"
local MAGS = { M .. "22LRMagazine10_HK416", M .. "22LRMagazine20_HK416", M .. "22LRMagazine30_HK416" }
local RAIL_UP = M .. "HK416QR22_Integrated_Rail_Up"
local RAIL_DOWN = M .. "HK416QR22_Integrated_Rail_Down"
local RAIL_LEFT = M .. "HK416QR22_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "HK416QR22_Integrated_Rail_Right"

-------------------------------------------------
-- Magazines (semi-automatic only: no rate of fire registration)
-------------------------------------------------
Magazine.RegisterMagazineProfile(".22 LR HK416", MAGS)
Magazine.RegisterWeaponWithProfile(".22 LR HK416", GUN)
Ammo.RegisterMultipleItemsWithFamilies({ [".22 LR"] = MAGS })

-------------------------------------------------
-- GoM's AR15 bolt and charging handle, GoM's MP5K reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(GUN, {
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
})
-- (no "boltCatchAfterEmptyInsert": its close step needs a rackClose clip, which GoM's MP5K reload has not got)
ReloadAnim.RegisterWeapon(GUN, GoMReloads.profile("handgun2"))

-------------------------------------------------
-- The integrated rails as parents of GoM's parts, the iron sights by the optic
-------------------------------------------------
local OPTICS = {}
for _, list in ipairs({ IronSights.RED_DOTS, IronSights.SCOPES }) do
    for _, o in ipairs(list) do OPTICS[#OPTICS + 1] = o end
end
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })
CSA.RegisterMultipleParts({ [RAIL_UP] = {}, [RAIL_DOWN] = {}, [RAIL_LEFT] = {}, [RAIL_RIGHT] = {} })
PreventRemoval.Register({ RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT, MAGS[1], MAGS[2], MAGS[3] })
IronSights.Register(GUN)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, handle and rails; the 20 it was sold
-- with, sometimes the 10 or the 30; red dots and the short scopes now and then, foregrips, lights and lasers at GoM's MP5
-- chances (no ":PR*": the rails are integral)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[GUN] = {
        required = { "MarzGuns.Bolt_Lock", "MarzGuns.Charging_Handle_Close", RAIL_UP, RAIL_DOWN, RAIL_LEFT,
            RAIL_RIGHT },
        optionals = {
            MAGS[2] .. ":50", MAGS[1] .. ":15", MAGS[3] .. ":5",
            "MarzGuns.ReflexS2_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5",
            "MarzGuns.JS14_Sight:3", "MarzGuns.LR4X_Scope:2",
            "MarzGuns.Stub_Foregrip:5", "MarzGuns.MKC_Foregrip:5", "MarzGuns.MK2_Foregrip:3",
            "MarzGuns.BrightPoint-5_Light:5", "MarzGuns.SR7_Light:5",
            "MarzGuns.AimRight_Laser:3", "MarzGuns.LRX-7_Laser:3",
        },
    }
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as HK416.lua does): GoM's
-- optics, foregrips, lights and lasers
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
        for _, part in ipairs(list) do appendMountOn(part, { GUN }) end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_HK416_22 = { HK416QR22 = GUN, MAGS = MAGS }
