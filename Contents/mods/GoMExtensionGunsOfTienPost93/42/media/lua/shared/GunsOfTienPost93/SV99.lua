--[[
    Guns of Tien - Post-93 -- the Izhmash SV-99, its polymer stock's shape in green plywood (user, 2026-11-20;
    docs/post93_design.md "SV-98 and SV-99") in Gunworks' and Guns of Marz's registries.

    Izhmash's .22 LR sniper rifle (shown 1999, FSB 2004, MVD 2005), one item (scripts/post93/build_sv99.py;
    items_sv99.txt; a second, black-stocked item was dropped the day it was built), registered as the SV-98 (SV98.lua):
    - its own 5-round magazine, in the main mod's ".22 LR" family (the plain round and its Subsonic,
      Hollow Point and Hyper Velocity loads);
    - the straight-pull toggle lever (GoM's Bolt part, drawn about its pivot and swung back), worked after every shot
      (the script's RackAfterShoot): a manual action, so the main mod's subsonic rack rule for self-loaders has
      nothing to do here;
    - reload: GoM's magazine bolt-action nodes (the main mod's GoMReloads.lua "boltaction"), as the SV-98;
    - the rail on the receiver: a hidden integrated rail, the parent of GoM's optics; no iron sights (the real rifle
      has none);
    - the bipod under the forend: two hidden parts drawn with their own models, folded on a found gun, Gunworks'
      bipod stance when deployed (GoM's M24 way);
    - the suppressor is built in (the SV-99 is not seen without its can): the quiet sound is in the guns' own stats,
      and no muzzle part fits.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local Animations = require("WeaponSystems/Utils/Animations")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local BipodSystem = require("WeaponSystems/Utils/BipodSystem")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local GoMReloads = require("GunsOfTien/GoMReloads")
for _, file in ipairs({ "Ammunition", "Magazines", "ReloadsAndAnims/ReloadAnims", "ReloadsAndAnims/AnimationsFiring",
    "Bipods", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local GUNS = { M .. "SV99" }
local MAG = M .. "22LRMagazine5_SV99"
local RAIL_UP = M .. "SV99_Integrated_Rail_Up"
local FOLDED = M .. "SV99_Integrated_Bipod_Folded"
local DEPLOYED = M .. "SV99_Integrated_Bipod_Deployed"

Magazine.RegisterMagazineProfile(".22 LR SV-99", { MAG })
Ammo.RegisterMultipleItemsWithFamilies({ [".22 LR"] = { MAG } })

local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
CSA.RegisterMultipleParts({ [RAIL_UP] = {} })
BipodSystem.RegisterBipod(DEPLOYED)
PreventRemoval.Register({ MAG, RAIL_UP })

for _, gun in ipairs(GUNS) do
    Magazine.RegisterWeaponWithProfile(".22 LR SV-99", gun)
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("boltaction"))
    FoldingBipod.RegisterWeapon(gun, {
        attachments = { partType = "BipodIntegrated", folded = FOLDED, deployed = DEPLOYED },
        initialState = "folded",
    })
end

-------------------------------------------------
-- MountOn appended for GoM's optics (DoParam replaces the list, so it is read and written back whole)
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
    for _, part in ipairs(OPTICS) do appendMountOn(part, GUNS) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)
-- and at once (user, 2026-11-25): GoM's guns are in its parts' MountOn from the script files on, and a mod that
-- lists a gun's slots from MountOn when its own Lua loads (before OnGameBoot) missed ours
pcall(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the lever, the rail, the bipod folded, its
-- magazine at GoM's pistol chance, now and then a red dot or low scope (no ":PRU": the rail is the gun's own)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local optionals = { MAG .. ":50" }
    for _, o in ipairs({ "ReflexS2_Sight", "Kobra_Sight", "OKP3_Sight", "EXPS3_Sight", "Aimpoint_Sight" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":2"
    end
    for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "PSO1_Scope" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":5"
    end
    for _, gun in ipairs(GUNS) do
        spawnTable[gun] = { required = { "MarzGuns.Bolt_Lock", RAIL_UP, FOLDED }, optionals = optionals }
    end
end

GunsOfTienPost93_SV99 = { GUNS = GUNS, MAG = MAG, RAIL_UP = RAIL_UP, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
