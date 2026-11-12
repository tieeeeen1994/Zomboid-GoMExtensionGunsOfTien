--[[
    Guns of Tien - Post-93 -- Knight's Mk 11 Mod 0 (user, 2026-11-12; docs/post93_design.md "Knight's Mk 11 Mod 0")
    in Gunworks' and Guns of Marz's registries.

    The SR-25 as SOCOM adopted it in May 2000, built on the main mod's SR-25 receiver and stock
    (scripts/post93/build_mk11.py). Semi-automatic only (no rate of fire registered, as GoM's AR-15 / M14 / PSG-1).
    Moddable (user: "no integrated parts. I will have integrated picatinny rails though"):
    - KAC's rail handguard and the flat top: four hidden integrated rails (MK11_Integrated_Rail_Up / _Down / _Left /
      _Right, modelled in the body) as parents of GoM's optics (top), foregrips and bipods (bottom), lights (left) and
      lasers (right), as the SCARs' integrated rails; no Sniper Mounting Rail (GoM's only adds a rail to its bolt-action
      rifles);
    - magazines: the SR-25 pattern ("7.62x51mm SR-25"): the main mod's KAC 20 (found mostly, user 2026-11-12) and the
      PMAGs and D-50; KAC's 20 lists the Mk 11 and the MDRx .308 in its MountOn here (the main mod cannot name
      Post-93's guns);
    - muzzle: the 7.62x51mm mount device and SOCOM762-RC (Guns.lua's rule: the can needs the mount);
    - GoM's AR bolt and charging handle as on its AR15 (its table repeated, as SR25.lua), GoM's AR15 reload.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local GoMReloads = require("GunsOfTien/GoMReloads")
require("GunsOfTienPost93/Guns")             -- the SCAR-H's suppressor rule and stats first
require("GunsOfTien/SR25")                   -- the SR-25 pattern profile and KAC's 20 first

for _, file in ipairs({ "Magazines", "ReloadsAndAnims/ReloadAnims", "ReloadsAndAnims/AnimationsFiring", "Bipods",
    "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local MK11 = M .. "MK11"
local KAC = "GunsOfTien.762x51Magazine20_SR25"
local PMAGS = { M .. "762x51Magazine20_PMAG", M .. "762x51Magazine10_PMAG", M .. "762x51Magazine25_PMAG",
    M .. "762x51Magazine50_PMAG" }
local RAIL_UP = M .. "MK11_Integrated_Rail_Up"
local RAIL_DOWN = M .. "MK11_Integrated_Rail_Down"
local RAIL_LEFT = M .. "MK11_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "MK11_Integrated_Rail_Right"

-------------------------------------------------
-- Magazines: the SR-25 pattern (KAC's 20 registered by the main mod's SR25.lua, the PMAGs by MDR.lua)
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x51mm SR-25", PMAGS)
Magazine.RegisterWeaponWithProfile("7.62x51mm SR-25", MK11)

-------------------------------------------------
-- GoM's AR15 bolt and charging handle, GoM's AR15 reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(MK11, {
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
ReloadAnim.RegisterWeapon(MK11, GoMReloads.profile("ar15_rifle", { rules = "boltCatchAfterEmptyInsert" }))

-------------------------------------------------
-- The integrated rails as parents of GoM's parts
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
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

local permanent = { RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT }
for _, mag in ipairs(PMAGS) do permanent[#permanent + 1] = mag end
PreventRemoval.Register(permanent)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): GoM's AR15 bolt and handle, the four rails;
-- KAC's 20 mostly, the PMAGs and the D-50 rarer (user, 2026-11-12); the SCAR-H's accessories at GoM's chances
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[MK11] = {
        required = { "MarzGuns.Bolt_Lock", "MarzGuns.Charging_Handle_Close", RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT },
        optionals = {
            KAC .. ":50", PMAGS[1] .. ":15", PMAGS[2] .. ":5", PMAGS[3] .. ":5", PMAGS[4] .. ":2",
            "MarzGuns.LR4X_Scope:5", "MarzGuns.TR06X_Scope:3", "MarzGuns.LR10X_Scope:3", "MarzGuns.ElcanX2_Scope:3",
            "MarzGuns.Bipod_Folded:10", "MarzGuns.MKC_Foregrip:3",
            "MarzGuns.AimRight_Laser:2", "MarzGuns.SR7_Light:2",     -- no ":PR*": the rails are integral
            M .. "SCARH_Muzzle_Mount_Device:5",
        },
    }
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as MDR.lua does): GoM's rail
-- parts, and KAC's 20 for the Mk 11 and the MDRx .308 (it is the main mod's item; the mount device and SOCOM762-RC
-- list the Mk 11 in their own scripts)
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
        for _, part in ipairs(list) do appendMountOn(part, { MK11 }) end
    end
    appendMountOn(KAC, { MK11, M .. "MDR308" })
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_MK11 = { MK11 = MK11, RAILS = permanent }
