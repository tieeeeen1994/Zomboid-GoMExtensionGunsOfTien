--[[
    Guns of Tien - Post-93 -- H&K HK417 16" "Recce" and 20" "Sniper" (user, 2026-11-13; docs/post93_design.md
    "H&K HK417") in Gunworks' and Guns of Marz's registries.

    The HK416's 7.62x51mm big brother in its original pattern (2006-), built on GoM's AR15 grown to the 7.62 size
    (scripts/post93/build_hk417.py), registered as our HK416 (HK416.lua) and Mk 11 (MK11.lua):
    - H&K's own translucent 10 and 20-round polymer magazines, a profile of their own ("7.62x51mm HK417": real HK417
      magazines fit neither the SR-25 nor the SCAR-H), in GoM's 7.62x51mm family;
    - select fire, Auto / Single at H&K's 600 rpm; the Sniper's longer, heavier barrel spreads a little less;
    - GoM's AR bolt and charging handle as on its AR15, GoM's AR15 reload with its bolt catch rule (as the Mk 11);
    - H&K's six-position stock (HK417_Integrated_Stock_Folded / _Deployed, Gunworks' FoldingStock), with GoM's CAR-15 /
      our SCARs' stock stats when out (as the HK416's);
    - four hidden integrated rails (modelled in the body) as parents of GoM's optics (top), foregrips and bipods
      (bottom), lights (left) and lasers (right);
    - the iron sights follow the optic (IronSights.lua): H&K's flip-ups as on the HK416, the rear folded under a red
      dot, both under a magnified scope; the rear sight sits at the very rear of the flat top, clear of every optic's
      mount, so no state takes it off;
    - at canon the SCAR-H's 7.62x51mm mount device and SOCOM762-RC (their scripts list both guns; GoM's rule makes the
      can need the mount, Guns.lua).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local GoMReloads = require("GunsOfTien/GoMReloads")
local IronSights = require("GunsOfTienPost93/IronSights")
require("GunsOfTienPost93/Guns")             -- the SCAR-H's mount device and suppressor rule first

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "Stocks", "ReloadsAndAnims/ReloadAnims",
    "ReloadsAndAnims/AnimationsFiring", "Bipods", "AttachmentCustomStats", "AttachmentsRequiredParts",
    "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local HK417 = M .. "HK417"
local HK417S = M .. "HK417S"
local GUNS = { HK417, HK417S }
local MAGS = { M .. "762x51Magazine20_HK417", M .. "762x51Magazine10_HK417" }
local RAIL_UP = M .. "HK417_Integrated_Rail_Up"
local RAIL_DOWN = M .. "HK417_Integrated_Rail_Down"
local RAIL_LEFT = M .. "HK417_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "HK417_Integrated_Rail_Right"
local STOCK_FOLDED = M .. "HK417_Integrated_Stock_Folded"
local STOCK_DEPLOYED = M .. "HK417_Integrated_Stock_Deployed"

-------------------------------------------------
-- Magazines, rate of fire (600 rpm; the SCAR-H spreads 0.22 / 3.5)
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x51mm HK417", MAGS)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x51mm"] = MAGS })
for _, gun in ipairs(GUNS) do Magazine.RegisterWeaponWithProfile("7.62x51mm HK417", gun) end
RateOfFire.RegisterWeapon(HK417, { rpm = 600, enableSpread = true, sustainedSpread = 0.2, maxSpread = 3.2 })
RateOfFire.RegisterWeapon(HK417S, { rpm = 600, enableSpread = true, sustainedSpread = 0.18, maxSpread = 3.0 })
RateOfFire.RegisterSpreadPartModifier(STOCK_DEPLOYED, { sustainedSpreadMult = 0.75, maxSpreadMult = 0.85 })

-------------------------------------------------
-- GoM's AR15 bolt and charging handle, GoM's AR15 reload; H&K's stock; the iron sights
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
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
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("ar15_rifle", { rules = "boltCatchAfterEmptyInsert" }))
    FoldingStock.RegisterWeapon(gun, {
        attachments = { partType = "StockIntegrated", folded = STOCK_FOLDED, deployed = STOCK_DEPLOYED },
        initialState = "folded",
    })
    IronSights.Register(gun)
end
CSA.RegisterMultipleParts({
    [STOCK_FOLDED] = {},
    [STOCK_DEPLOYED] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.85),
    },
})

-------------------------------------------------
-- The integrated rails as parents of GoM's parts
-------------------------------------------------
local OPTICS = {}
for _, list in ipairs({ IronSights.RED_DOTS, IronSights.SCOPES }) do
    for _, o in ipairs(list) do OPTICS[#OPTICS + 1] = o end
end
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local BIPODS = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(BIPODS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })
CSA.RegisterMultipleParts({ [RAIL_UP] = {}, [RAIL_DOWN] = {}, [RAIL_LEFT] = {}, [RAIL_RIGHT] = {} })
PreventRemoval.Register({ RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT, MAGS[1], MAGS[2] })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): GoM's AR15 bolt and handle, the stock in,
-- the four rails; the 20 mostly, the 10 now and then; the Recce with the SCAR-H's accessories at GoM's chances, the
-- Sniper with the Mk 11's (no ":PR*": the rails are integral)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local required = { "MarzGuns.Bolt_Lock", "MarzGuns.Charging_Handle_Close", STOCK_FOLDED,
        RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT }
    spawnTable[HK417] = {
        required = required,
        optionals = {
            MAGS[1] .. ":50", MAGS[2] .. ":15",
            "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5", "MarzGuns.ElcanX2_Scope:3",
            "MarzGuns.LR4X_Scope:3", "MarzGuns.TA28_Scope:3",
            "MarzGuns.MKC_Foregrip:3", "MarzGuns.Bipod_Folded:3",
            "MarzGuns.AimRight_Laser:2", "MarzGuns.SR7_Light:2",
            M .. "SCARH_Muzzle_Mount_Device:5",
        },
    }
    spawnTable[HK417S] = {
        required = required,
        optionals = {
            MAGS[1] .. ":50", MAGS[2] .. ":15",
            "MarzGuns.LR4X_Scope:5", "MarzGuns.TR06X_Scope:3", "MarzGuns.LR10X_Scope:3", "MarzGuns.ElcanX2_Scope:3",
            "MarzGuns.Bipod_Folded:10", "MarzGuns.MKC_Foregrip:3",
            "MarzGuns.AimRight_Laser:2", "MarzGuns.SR7_Light:2",
            M .. "SCARH_Muzzle_Mount_Device:5",
        },
    }
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as HK416.lua does): GoM's rail
-- parts (the mount device and SOCOM762-RC list both guns in their own scripts)
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
    for _, list in ipairs({ OPTICS, FOREGRIPS, BIPODS, LIGHTS, LASERS }) do
        for _, part in ipairs(list) do appendMountOn(part, GUNS) end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_HK417 = { HK417 = HK417, HK417S = HK417S, MAGS = MAGS }
