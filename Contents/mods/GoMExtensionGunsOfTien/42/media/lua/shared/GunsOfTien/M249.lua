--[[
    Guns of Tien -- the M249 Light Machine Gun (docs/design.md 4d; user, 2026-10-22) in Gunworks' and Guns of Marz's
    registries.

    The PIP M249 of July 1993: full auto only, fed from its own 200-round box (items_m249.txt, PartType Clip, in GoM's
    5.56x45mm family) or, as the real gun's emergency feed, any of GoM's STANAG magazines: one magazine profile of our
    own holds both (Gunworks lets a gun have one profile, and a profile any items; insertion checks no type). Every
    other registration follows GoM's M60, its one belt-fed gun:
    - the belt: nine rounds from the box to the feed tray, GoM's Bullet_1..9 parts (PartType Animated1..9) drawn with
      our round models, attached while that many rounds are left (Animations.CheckStates). Gunworks shows them
      whatever is in the Clip slot, so for the M249 they are taken off while a STANAG is fitted.
    - rate of fire: two Auto rates, 750 and 1000 rpm (user, 2026-10-22: the original gun's gas regulator, normal and
      adverse; Gunworks lists one Auto entry per rate, as for GoM's BAR).
    - the integrated bipod with GoM's M60 bipod stats; the feed cover a hidden part (closed, or open while reloading:
      the reload clips swap it with Gunworks' gwSetPart events).
    - no bolt part: the cocking handle does not move when firing. The chambered round is kept (no HaveChamber =
      false, as GoM's M60): a box changed mid-belt fires on, a gun run dry is cocked again.
    - STANAG feed: jam chance x2 (user, 2026-10-22: FM 23-14 warns magazine feed "will increase the chance of
      stoppages"), a stat layer for the M249 alone (the same STANAGs keep their stats on an M16). Gunworks re-applies
      stats on equip, attach and round changes but not on a magazine swap, so the attack hook's per-shot call notices
      a change of feed (as Ammunition.lua does for the PBS-1).
    - reload: our animId "M249", Gunworks' attachments style (the box and magazine leave the gun with the hand).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")

for _, file in ipairs({ "Magazines", "RPM", "ReloadAnims", "Bipods", "AttachmentCustomStats", "PermanentAttachments",
    "AnimationsFiring", "Ammunition" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M249 = "GunsOfTien.M249"
local BOX = "GunsOfTien.556x45Box200_M249"
local COVER_CLOSED = "GunsOfTien.M249_Feed_Cover_Closed"
local COVER_OPEN = "GunsOfTien.M249_Feed_Cover_Open"
local BIPOD_FOLDED = "GunsOfTien.M249_Integrated_Bipod_Folded"
local BIPOD_DEPLOYED = "GunsOfTien.M249_Integrated_Bipod_Deployed"
local STANAGS = {}
for _, n in ipairs({ 20, 25, 30, 50, 60, 75, 100, 150 }) do
    STANAGS[#STANAGS + 1] = "MarzGuns.556x45Magazine" .. n .. "_STANAG"
end

local function isM249(weapon)
    return weapon ~= nil and weapon.getFullType ~= nil and weapon:getFullType() == M249
end

-- what feeds the gun now: the box, a STANAG (its full type), or nil
local function feedOf(weapon)
    local clip = weapon.getWeaponPart and weapon:getWeaponPart("Clip")
    return clip and clip:getFullType() or nil
end

-------------------------------------------------
-- Feed: its own profile (the box first, then GoM's STANAGs); the box in GoM's 5.56 family
-------------------------------------------------
local feed = { BOX }
for _, m in ipairs(STANAGS) do feed[#feed + 1] = m end
Magazine.RegisterMagazineProfile("GunsOfTien_M249", feed)
Magazine.RegisterWeaponWithProfile("GunsOfTien_M249", M249)
Ammo.RegisterMultipleItemsWithFamilies({ ["5.56x45mm"] = { BOX } })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire): the gas regulator's two settings
-------------------------------------------------
RateOfFire.RegisterWeapon(M249, {
    rpm = { [1] = 750, [2] = 1000 },
    enableSpread = true,
    sustainedSpread = 0.2,
    maxSpread = 3.5,
})

-------------------------------------------------
-- The belt (GoM's M60 way), hidden while a STANAG feeds the gun
-------------------------------------------------
local belt = {}
for i = 1, 9 do
    belt[i] = { threshold = i, part = "MarzGuns.Bullet_" .. i, slot = "Animated" .. i }
end
Animations.RegisterWeaponsWithCustomStates(M249, belt)
if not Animations.GunsOfTienM249Wrapped then
    Animations.GunsOfTienM249Wrapped = true
    local checkStates = Animations.CheckStates
    function Animations.CheckStates(weapon)
        if isM249(weapon) and feedOf(weapon) ~= BOX then
            for i = 1, 9 do
                local part = weapon:getWeaponPart("Animated" .. i)
                if part then weapon:detachWeaponPart(part) end
            end
            return
        end
        return checkStates(weapon)
    end
end

-------------------------------------------------
-- Integrated bipod: GoM's M60 bipod and its stats
-------------------------------------------------
FoldingBipod.RegisterWeapon(M249, {
    attachments = { partType = "BipodIntegrated", folded = BIPOD_FOLDED, deployed = BIPOD_DEPLOYED },
    initialState = "folded",
})
CSA.RegisterMultipleParts({
    [BIPOD_DEPLOYED] = {
        SF.Multiply("AimingTime", 1.3),
        SF.Multiply("CriticalChance", 1.1),
        SF.Multiply("HitChance", 1.1),
    },
    [BIPOD_FOLDED] = {
        SF.Set("UseEndurance", true),
        SF.Set("EnduranceMod", 0.3),
        SF.Multiply("HitChance", 0.8),
    },
})

-------------------------------------------------
-- STANAG feed jams twice as often
-------------------------------------------------
local registered = false
for _, layer in ipairs(SF.ModifierLayers) do
    if layer.id == "GunsOfTien_M249MagazineFeed" then registered = true end
end
if not registered then
    SF.RegisterModifierLayer("GunsOfTien_M249MagazineFeed",
        function(weapon)
            local f = feedOf(weapon)
            if f == nil or f == BOX then return nil end
            return { SF.Multiply("JamGunChance", 2.0) }
        end,
        { JamGunChance = true },
        isM249)
end
if not Ammo.GunsOfTienM249Wrapped then
    Ammo.GunsOfTienM249Wrapped = true
    local setter = Ammo.AmmoProfileSetter
    function Ammo.AmmoProfileSetter(weapon, bulletType)
        setter(weapon, bulletType)
        if not isM249(weapon) then return end
        local md = weapon:getModData()
        local f = feedOf(weapon) or ""
        if md.GunsOfTienM249Feed ~= f then
            md.GunsOfTienM249Feed = f
            SF.ReapplyAllModifiers(weapon)
        end
    end
end

-------------------------------------------------
-- Reload: animId "M249" (AnimSets *M249_GoT.xml), the box or magazine leaving the gun with the hand. The part spec
-- names one item type and Gunworks only takes off / puts on that type, so before each swap it is pointed at the feed
-- involved (as Post-93's MP7, whose four magazines need the same). The clips open and close the feed cover with
-- Gunworks' gwSetPart marker ("FeedCover=GunsOfTien.M249_Feed_Cover_Open"), which only its "none" style reads, so
-- the M249's markers are passed to it from the attachments style's part event; partState.ensure puts the closed
-- cover back once a reload ends or is cut short.
-------------------------------------------------
ReloadAnim.RegisterWeapon(M249, {
    animId = "M249",
    style = "attachments",
    magItem = BOX,
    attachments = { magPart = { itemType = BOX, partType = "Clip" } },
    durations = { unload = 2.4, load = 3.2, rack = 1.5 },
    partState = { ensure = { COVER_CLOSED } },
})
if not ReloadAnim.GunsOfTienM249Wrapped then
    ReloadAnim.GunsOfTienM249Wrapped = true
    pcall(require, "WeaponSystems/ReloadAnim/Visuals")
    pcall(require, "WeaponSystems/ReloadAnim/PartSwap")
    local resolveReloadMagItem = ReloadAnim.resolveReloadMagItem
    local function pointMagPart(action, handler)
        if not (resolveReloadMagItem and action and handler and handler.animId == "M249" and handler.parts) then
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
            ReloadAnim[name] = function(action, handler, event, ...)
                if name == "handleWeaponPartAnimEvent" and handler and handler.animId == "M249"
                        and event == "gwSetPart" and ReloadAnim.handleGwSetPartAnimEvent then
                    return ReloadAnim.handleGwSetPartAnimEvent(action, handler, event, ...)
                end
                pointMagPart(action, handler)
                return original(action, handler, event, ...)
            end
        end
    end
end

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (the box goes with the reload, as GoM's M60 box)
-------------------------------------------------
PreventRemoval.Register({ BOX, COVER_CLOSED, COVER_OPEN })

-------------------------------------------------
-- A found gun: the cover closed, the bipod folded, the box at GoM's M60 chance
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[M249] = {
        required = { COVER_CLOSED, BIPOD_FOLDED },
        optionals = { BOX .. ":50" },
    }
end

-------------------------------------------------
-- GoM's STANAG magazines on the M249: append it to their MountOn (DoParam replaces the list, so it is read and
-- written back whole; Post-93's Guns.lua does the same for its guns)
-------------------------------------------------
local function appendMountOn(partType, gun)
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
    if seen[gun] then return end
    list[#list + 1] = gun
    script:DoParam("MountOn = " .. table.concat(list, ";"))
end

local function appendAll()
    for _, part in ipairs(STANAGS) do appendMountOn(part, M249) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTien_M249 = { GUN = M249, BOX = BOX, STANAGS = STANAGS, COVER_CLOSED = COVER_CLOSED, COVER_OPEN = COVER_OPEN,
    BIPOD_FOLDED = BIPOD_FOLDED, BIPOD_DEPLOYED = BIPOD_DEPLOYED, feedOf = feedOf }
