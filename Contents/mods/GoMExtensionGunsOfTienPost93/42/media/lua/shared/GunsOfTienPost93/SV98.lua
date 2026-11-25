--[[
    Guns of Tien - Post-93 -- the Izhmash SV-98 (user, 2026-11-20; docs/post93_design.md "SV-98 and SV-99") in
    Gunworks' and Guns of Marz's registries.

    Izhmash's bolt-action sniper rifle of 1998-2000 (adopted 2003) in its plywood stock, 7.62x54R
    (scripts/post93/build_sv98.py; items_sv98.txt), registered as GoM registers its M24:
    - its own 10-round polymer magazine (a profile of its own, in GoM's "7.62x54mm" family, the Mosin's and SVD's
      rounds);
    - the bolt and its handle back after each shot and on the rack (GoM's bolt swap), racked after every shot (the
      script's RackAfterShoot);
    - reload: GoM's magazine bolt-action nodes (vanilla's hunting rifle clips; the main mod's GoMReloads.lua
      "boltaction"): GoM has no other reload for a bolt rifle with a magazine;
    - the rail on the receiver: a hidden integrated rail, the parent of GoM's optics (the Mk 11's way), so the rifle
      takes every GoM optic and none needs GoM's rail upgrade;
    - the bipod in the forend: two hidden parts drawn with their own models, folded on a found gun, resting the rifle
      on walls and tables when deployed (GoM's M24 bipod: no stat changes, Gunworks' bipod stance).
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
local SV98 = M .. "SV98"
local MAG = M .. "762x54Magazine10_SV98"
-- an invented 20-round magazine of the same pattern (user, 2026-11-25; scripts/post93/build_sv98_mag20.py), made for
-- the A-91M Prototype, which is registered with this profile in A91M.lua
local MAG20 = M .. "762x54Magazine20_SV98"
local MAGS = { MAG, MAG20 }
local RAIL_UP = M .. "SV98_Integrated_Rail_Up"
local FOLDED = M .. "SV98_Integrated_Bipod_Folded"
local DEPLOYED = M .. "SV98_Integrated_Bipod_Deployed"

-------------------------------------------------
-- Magazine
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x54mm SV-98", MAGS)
Magazine.RegisterWeaponWithProfile("7.62x54mm SV-98", SV98)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x54mm"] = MAGS })

-------------------------------------------------
-- The bolt and the reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(SV98, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})
ReloadAnim.RegisterWeapon(SV98, GoMReloads.profile("boltaction"))

-------------------------------------------------
-- The rail on the receiver, parent of GoM's optics
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
CSA.RegisterMultipleParts({ [RAIL_UP] = {} })

-------------------------------------------------
-- The bipod (GoM's M24 way: Gunworks' folding bipod and bipod stance, no stat changes)
-------------------------------------------------
FoldingBipod.RegisterWeapon(SV98, {
    attachments = { partType = "BipodIntegrated", folded = FOLDED, deployed = DEPLOYED },
    initialState = "folded",
})
BipodSystem.RegisterBipod(DEPLOYED)

PreventRemoval.Register({ MAG, MAG20, RAIL_UP })

-------------------------------------------------
-- MountOn appended for GoM's optics (DoParam replaces the list, so it is read and written back whole, as MK11.lua
-- does)
-------------------------------------------------
local function appendMountOn(partType, gun)
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
    if seen[gun] then return end
    list[#list + 1] = gun
    script:DoParam("MountOn = " .. table.concat(list, ";"))
end

local function appendAll()
    for _, part in ipairs(OPTICS) do appendMountOn(part, SV98) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)
-- and at once (user, 2026-11-25): GoM's guns are in its parts' MountOn from the script files on, and a mod that
-- lists a gun's slots from MountOn when its own Lua loads (before OnGameBoot) missed ours
pcall(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the rail, the bipod folded, its
-- magazine at GoM's SVD chance, GoM's M24 optics at its chances (no ":PRU": the rail is the gun's own)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local optionals = { MAG .. ":50" }
    for _, o in ipairs({ "ReflexS2_Sight", "Kobra_Sight", "OKP3_Sight", "JS14_Sight", "EXPS3_Sight", "EXPS1_Sight",
        "Aimpoint_Sight", "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":1"
    end
    for _, o in ipairs({ "TR06X_Scope", "PSO1_Scope", "LR10X_Scope", "LRX12X_Scope" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":5"
    end
    spawnTable[SV98] = { required = { "MarzGuns.Bolt_Lock", RAIL_UP, FOLDED }, optionals = optionals }
end

GunsOfTienPost93_SV98 = { GUN = SV98, MAG = MAG, MAGS = MAGS, PROFILE = "7.62x54mm SV-98", RAIL_UP = RAIL_UP, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
