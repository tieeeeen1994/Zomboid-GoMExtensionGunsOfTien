--[[
    Guns of Tien - Post-93 -- H&K HK416 D14.5RS (user, 2026-11-13; docs/post93_design.md "H&K HK416 D14.5RS") in
    Gunworks' and Guns of Marz's registries.

    H&K's 14.5" carbine (2004), built on GoM's AR15 at its own size (scripts/post93/build_hk416.py). Select fire,
    Auto / Single (H&K's safe / semi / auto) at 850 rpm.
    - H&K's Free Floating Rail System and the receiver's flat top: four hidden integrated rails
      (HK416_Integrated_Rail_Up / _Down / _Left / _Right, modelled in the body) as parents of GoM's optics (top),
      foregrips and bipods (bottom), lights (left) and lasers (right), as the SCARs' and the Mk 11's;
    - the iron sights follow the optic (user, 2026-11-13): Gunworks' ConditionalModel swaps the gun's model by what is
      in its Scope slot: no optic = both flip-up sights up (HK416), a red dot or holographic sight = the rear folded and
      the front seen through it (HK416_RD), a magnified scope = both folded (HK416_FD). The three bodies share every
      attachment point. Optics from other mods leave the sights up;
    - H&K's six-position stock (HK416_Integrated_Stock_Folded / _Deployed, Gunworks' FoldingStock as GoM's M4A1), with
      GoM's CAR-15 / our SCARs' stock stats when out;
    - magazines: GoM's STANAG profile (GoM's own magazines and models, as its M4A1); muzzle: GoM's AR mount device and
      its suppressors, compensator, flash hider and muzzle brake (GoM's own rule: a can needs the mount);
    - GoM's AR bolt and charging handle as on its AR15 (its table repeated, as MK11.lua), GoM's AR15 reload with its
      bolt catch rule.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local ConditionalModel = require("WeaponSystems/Utils/ConditionalModel")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local GoMReloads = require("GunsOfTien/GoMReloads")
require("GunsOfTienPost93/Guns")             -- the SCAR-L's STANAG and AR muzzle registrations first

for _, file in ipairs({ "Magazines", "RPM", "Stocks", "ReloadsAndAnims/ReloadAnims", "ReloadsAndAnims/AnimationsFiring",
    "Bipods", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local HK416 = M .. "HK416"
local RAIL_UP = M .. "HK416_Integrated_Rail_Up"
local RAIL_DOWN = M .. "HK416_Integrated_Rail_Down"
local RAIL_LEFT = M .. "HK416_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "HK416_Integrated_Rail_Right"
local STOCK_FOLDED = M .. "HK416_Integrated_Stock_Folded"
local STOCK_DEPLOYED = M .. "HK416_Integrated_Stock_Deployed"

-------------------------------------------------
-- Magazines, rate of fire (H&K's 850 rpm; GoM's M4A1's spread, the same 5.56 from 14.5")
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("STANAG", HK416)          -- GoM's own profile (M16s, M4A1, FNC...)
RateOfFire.RegisterWeapon(HK416, { rpm = 850, enableSpread = true, sustainedSpread = 0.10, maxSpread = 2.5 })

-------------------------------------------------
-- GoM's AR15 bolt and charging handle, GoM's AR15 reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(HK416, {
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
ReloadAnim.RegisterWeapon(HK416, GoMReloads.profile("ar15_rifle", { rules = "boltCatchAfterEmptyInsert" }))

-------------------------------------------------
-- H&K's telescopic stock
-------------------------------------------------
FoldingStock.RegisterWeapon(HK416, {
    attachments = { partType = "StockIntegrated", folded = STOCK_FOLDED, deployed = STOCK_DEPLOYED },
    initialState = "folded",
})
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
-- GoM's optics: no magnification (the front sight is seen through them), then the magnified ones
local RED_DOTS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.Aimpoint_Sight", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight",
}
local SCOPES = {
    "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope",
    "MarzGuns.TR06X_Scope", "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local OPTICS = {}
for _, list in ipairs({ RED_DOTS, SCOPES }) do
    for _, o in ipairs(list) do OPTICS[#OPTICS + 1] = o end
end
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local BIPODS = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
local STANAGS = {}
for _, n in ipairs({ 20, 25, 30, 50, 60, 75, 100, 150 }) do
    STANAGS[#STANAGS + 1] = "MarzGuns.556x45Magazine" .. n .. "_STANAG"
end
local AR_MUZZLE = { "MarzGuns.AR_Muzzle_Mount_Device", "MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor",
    "MarzGuns.LR2_Compensator", "MarzGuns.LX_Flashhider", "MarzGuns.Trix42_Muzzlebreak" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(BIPODS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })
CSA.RegisterMultipleParts({ [RAIL_UP] = {}, [RAIL_DOWN] = {}, [RAIL_LEFT] = {}, [RAIL_RIGHT] = {} })
PreventRemoval.Register({ RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT })

-------------------------------------------------
-- The iron sights follow the optic (the bodies in models_hk416.txt)
-------------------------------------------------
ConditionalModel.Register(HK416, {
    rules = {
        { parts = { Scope = RED_DOTS }, model = M .. "HK416_RD" },
        { parts = { Scope = SCOPES }, model = M .. "HK416_FD" },
    },
    default = HK416,
})

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): GoM's AR15 bolt and handle, the stock in,
-- the four rails; GoM's M4A1 magazines and optics at its chances (no ":PR*": the rails are integral), the SCAR-L's
-- extras
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[HK416] = {
        required = { "MarzGuns.Bolt_Lock", "MarzGuns.Charging_Handle_Close", STOCK_FOLDED,
            RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT },
        optionals = {
            "MarzGuns.556x45Magazine20_STANAG:30", "MarzGuns.556x45Magazine25_STANAG:20",
            "MarzGuns.556x45Magazine30_STANAG:50",
            "MarzGuns.ReflexS2_Sight:5", "MarzGuns.Kobra_Sight:5", "MarzGuns.OKP3_Sight:5", "MarzGuns.JS14_Sight:5",
            "MarzGuns.EXPS3_Sight:5", "MarzGuns.EXPS1_Sight:5", "MarzGuns.Aimpoint_Sight:5",
            "MarzGuns.LR4X_Scope:3", "MarzGuns.TA28_Scope:3", "MarzGuns.ElcanX2_Scope:3",
            "MarzGuns.TR06X_Scope:1", "MarzGuns.PSO1_Scope:1", "MarzGuns.LR10X_Scope:1", "MarzGuns.LRX12X_Scope:1",
            "MarzGuns.Stub_Foregrip:2", "MarzGuns.MKC_Foregrip:2", "MarzGuns.MK2_Foregrip:2",
            "MarzGuns.AimRight_Laser:2", "MarzGuns.LRX-7_Laser:2",
            "MarzGuns.BrightPoint-5_Light:2", "MarzGuns.SR7_Light:2",
            "MarzGuns.Bipod_Folded:2", "MarzGuns.AR_Muzzle_Mount_Device:5",
        },
    }
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as MK11.lua does): GoM's rail
-- parts, its STANAG magazines and its AR muzzle family
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
    for _, list in ipairs({ OPTICS, FOREGRIPS, BIPODS, LIGHTS, LASERS, STANAGS, AR_MUZZLE }) do
        for _, part in ipairs(list) do appendMountOn(part, { HK416 }) end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_HK416 = { HK416 = HK416, RED_DOTS = RED_DOTS, SCOPES = SCOPES }
