--[[
    Guns of Tien - Post-93 -- the MP7A1 and P90 TR in Gunworks' and Guns of Marz's registries.

    Everything a GoM gun goes through, done for ours (CLAUDE.md, "Gun data and registries in GoM"): magazine
    profiles, rate of fire (required for Gunworks' real auto fire), the animated bolt, reload animations, the MP7's
    collapsible stock, integrated rails as parents of GoM's optics / lights / lasers, the suppressors and their mount
    devices, parts that cannot be removed, spawn-time parts and magazines, and GoM parts allowed on our guns
    (MountOn appended; DoParam replaces the list, so it is read and written back whole).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

for _, file in ipairs({ "Magazines", "RPM", "ReloadAnims", "Stocks", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local MP7 = M .. "MP7A1"
local P90 = M .. "P90TR"
local MP7_MAGS = { M .. "46x30Magazine20_MP7", M .. "46x30Magazine30_MP7", M .. "46x30Magazine40_MP7",
    M .. "46x30Magazine60_MP7" }
local P90_MAGS = { M .. "57x28Magazine50_P90" }

-------------------------------------------------
-- Magazines
-------------------------------------------------
Magazine.RegisterMagazineProfile("4.6x30mm MP7", MP7_MAGS)
Magazine.RegisterWeaponWithProfile("4.6x30mm MP7", MP7)
Magazine.RegisterMagazineProfile("5.7x28mm P90", P90_MAGS)
Magazine.RegisterWeaponWithProfile("5.7x28mm P90", P90)

-------------------------------------------------
-- Rate of fire: MP7A1 950 rpm, P90 900 rpm. Both are light-recoiling, so they spread less than the MP5.
-------------------------------------------------
RateOfFire.RegisterWeapon(MP7, { rpm = 950, enableSpread = true, sustainedSpread = 0.08, maxSpread = 1.3 })
RateOfFire.RegisterWeapon(P90, { rpm = 900, enableSpread = true, sustainedSpread = 0.06, maxSpread = 1.1 })

-------------------------------------------------
-- No animated bolt: on both the MP7 and the P90 the charging handle does not move when firing (the bolt inside
-- does), so neither is registered with Animations (GoM swaps Bolt_Fired / Bolt_Lock on each shot for guns whose
-- handle reciprocates). The handle model is drawn through the Bolt_Lock part (required at spawn).
-------------------------------------------------

-------------------------------------------------
-- Reload animations. Both guns are held like a pistol. The MP7's magazine goes up into the pistol grip, so it uses
-- vanilla's pistol clips (AnimSets MP7A1_*: Bob_Reload_Handgun_Load, its reverse baked into
-- anims_X/Bob/Bob_GunsOfTien_MP7_Unload, Bob_Reload_Handgun_Rack with GoM's rack events); the P90 its own
-- top-loading clips (AnimSets P90TR_*, clips anims_X/Bob/Bob_GunsOfTien_P90_*). A reload ends on its clip's events
-- (loadFinished...): without the clips the magazine insert waits forever (seen in game, 2026-10-15). Both use
-- Gunworks' "attachments" style so the magazine leaves the gun with the hand: the AnimSets' changeWeaponPart "mag"
-- events detach the magazine part (looks only) as the left hand leaves the gun in the unload, and put it back as the
-- new one is pressed home; the real unload / insert still happen at the clips' ends. Durations = the clips' lengths.
-------------------------------------------------
ReloadAnim.RegisterWeapon(MP7, {
    animId = "MP7A1",
    style = "attachments",
    magItem = MP7_MAGS[1],
    attachments = { magPart = { itemType = MP7_MAGS[1], partType = "Clip" } },
    durations = { unload = 1.5, load = 1.5, rack = 1.33 },
})
ReloadAnim.RegisterWeapon(P90, {
    animId = "P90TR",
    style = "attachments",
    magItem = M .. "57x28Magazine50_P90",
    attachments = { magPart = { itemType = M .. "57x28Magazine50_P90", partType = "Clip" } },
    durations = { unload = 1.4, load = 1.8, rack = 1.2 },
})
local NO_HAND_MAGAZINE = { MP7A1 = true, P90TR = true }
-- The magazine only leaves the gun / comes back at those events: no magazine shown in the left hand (user,
-- 2026-10-15). The attachments style shows Gunworks' reload magazine there (the eject's changeWeaponPart and the
-- insert's start, both through ReloadAnim.attachReloadMagazine, looked up on the shared table at call time), so that
-- one call is skipped for our guns; detachReloadMagazine then has nothing to remove.
pcall(require, "WeaponSystems/ReloadAnim/Visuals")
local attachReloadMagazine = ReloadAnim.attachReloadMagazine
if attachReloadMagazine then
    ReloadAnim.attachReloadMagazine = function(action, handler)
        if handler and NO_HAND_MAGAZINE[handler.animId] then
            return
        end
        return attachReloadMagazine(action, handler)
    end
end
-- The magazine part spec names one item type, and Gunworks only detaches a part of that type and attaches that type
-- (Visuals.detachWeaponPartSpec / attachWeaponPartSpec). The MP7 takes four (20 / 30 / 40, the 60 drum), so before
-- each swap the spec is pointed at the magazine involved: ReloadAnim.resolveReloadMagItem = the one being inserted, the one on the gun when the
-- eject started (_actualMagType), or the gun's saved MagazineType.
local resolveReloadMagItem = ReloadAnim.resolveReloadMagItem
local function pointMagPart(action, handler)
    if not (resolveReloadMagItem and action and handler and handler.animId == "MP7A1" and handler.parts) then
        return
    end
    local spec = handler.parts.mag
    local magType = resolveReloadMagItem(action, handler)
    if spec and magType and magType ~= "" then
        spec.itemType = magType
    end
end
for _, name in ipairs({ "handleWeaponPartAnimEvent", "setWeaponAttachmentState" }) do
    local original = ReloadAnim[name]
    if original then
        ReloadAnim[name] = function(action, handler, ...)
            pointMagPart(action, handler)
            return original(action, handler, ...)
        end
    end
end

-------------------------------------------------
-- MP7A1 collapsible stock (as GoM's MP5)
-------------------------------------------------
FoldingStock.RegisterWeapon(MP7, {
    attachments = {
        partType = "StockIntegrated",
        folded = M .. "MP7A1_Integrated_Stock_Folded",
        deployed = M .. "MP7A1_Integrated_Stock_Deployed",
    },
    initialState = "folded",
})

CSA.RegisterMultipleParts({
    [M .. "MP7A1_Integrated_Stock_Folded"] = {},
    [M .. "MP7A1_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.75),
    },
    -- GoM's suppressor stats (its pistol suppressors' sound).
    [M .. "MP7_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
    [M .. "P90_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
})

-------------------------------------------------
-- Integrated rails as mounts for GoM's optics, lights and lasers; suppressors need their mount device
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }

RequiredAttachment.RegisterRequired(OPTICS, { M .. "MP7A1_Integrated_Rail_Up", M .. "P90TR_Integrated_Rail_Up" })
RequiredAttachment.RegisterRequired(LIGHTS, { M .. "MP7A1_Integrated_Rail_Left", M .. "P90TR_Integrated_Rail_Left" })
RequiredAttachment.RegisterRequired(LASERS, { M .. "MP7A1_Integrated_Rail_Right", M .. "P90TR_Integrated_Rail_Right" })
RequiredAttachment.RegisterRequired({ M .. "MP7_Suppressor" }, { M .. "MP7_Muzzle_Mount_Device" })
RequiredAttachment.RegisterRequired({ M .. "P90_Suppressor" }, { M .. "P90_Muzzle_Mount_Device" })

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu
-------------------------------------------------
local permanent = {}
for _, list in ipairs({ MP7_MAGS, P90_MAGS }) do
    for _, part in ipairs(list) do permanent[#permanent + 1] = part end
end
for _, part in ipairs({ "MP7A1_Integrated_Rail_Up", "MP7A1_Integrated_Rail_Left", "MP7A1_Integrated_Rail_Right",
    "P90TR_Integrated_Rail_Up", "P90TR_Integrated_Rail_Left", "P90TR_Integrated_Rail_Right" }) do
    permanent[#permanent + 1] = M .. part
end
PreventRemoval.Register(permanent)

-------------------------------------------------
-- Parts and magazines a found gun comes with (GoM's MarzGuns_OnCreate.AttachParts reads this table)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[MP7] = {
        required = {
            "MarzGuns.Bolt_Lock",
            M .. "MP7A1_Integrated_Stock_Folded",
            M .. "MP7A1_Integrated_Rail_Up",
            M .. "MP7A1_Integrated_Rail_Left",
            M .. "MP7A1_Integrated_Rail_Right",
        },
        optionals = {
            M .. "46x30Magazine20_MP7:30",
            M .. "46x30Magazine30_MP7:20",
            M .. "46x30Magazine40_MP7:5",
            M .. "46x30Magazine60_MP7:2",
            "MarzGuns.EXPS1_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            M .. "MP7_Muzzle_Mount_Device:10",
        },
    }
    spawnTable[P90] = {
        required = {
            "MarzGuns.Bolt_Lock",
            M .. "P90TR_Integrated_Rail_Up",
            M .. "P90TR_Integrated_Rail_Left",
            M .. "P90TR_Integrated_Rail_Right",
        },
        optionals = {
            M .. "57x28Magazine50_P90:60",
            "MarzGuns.EXPS1_Sight:10", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:10",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            M .. "P90_Muzzle_Mount_Device:10",
        },
    }
end

-------------------------------------------------
-- GoM parts allowed on our guns: append to their MountOn
-------------------------------------------------
local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local entry = tostring(current:get(i))
            if not seen[entry] then
                seen[entry] = true
                list[#list + 1] = entry
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
    for _, part in ipairs(OPTICS) do appendMountOn(part, { MP7, P90 }) end
    for _, part in ipairs(LIGHTS) do appendMountOn(part, { MP7, P90 }) end
    for _, part in ipairs(LASERS) do appendMountOn(part, { MP7, P90 }) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_Guns = { MP7 = MP7, P90 = P90 }
