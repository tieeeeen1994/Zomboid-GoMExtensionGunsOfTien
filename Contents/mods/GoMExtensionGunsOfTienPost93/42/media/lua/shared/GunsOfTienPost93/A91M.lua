--[[
    Guns of Tien - Post-93 -- KBP's A-91M bullpup with its 40 mm launcher (user, 2026-11-25; docs/post93_design.md
    "KBP A-91M") in Gunworks' and Guns of Marz's registries. The 5.56A-91 export version was built beside it and
    removed (user, 2026-11-25).

    The bullpup assault rifle and grenade launcher of 1998 (scripts/post93/build_a91m.py; items_a91m.txt):
    - 7.62x39mm, GoM's "762x39" magazines as the Groza-1 (its AK-47 30 and 75, the main mod's RPK 40 and drum), GoM's
      AK mount and the AK 7.62 muzzle devices (GoM's and the main mod's AKM slant compensator); no PBS-1 (no source
      shows the gun with a suppressor);
    - Auto / Single at 700 rpm, GoM's AK bolt swap (the charging handle rides the gas piston rod, so it moves on each
      shot), closing on an empty chamber as an AK does (the main mod's RPK.lua wrapper), GoM's FAMAS reload (the
      magazine behind the grip), GoM's magazines in the off hand at our size (HandMagazines.lua);
    - the launcher, as the Groza-1's GP-25 (GoM's M16A2_M203 way): a hidden <gun>_GL_Integrated part (PartType
      Underbarrel) that Gunworks' Underbarrel swaps for the launcher weapon <gun>_GL (Gunworks' radial menu), drawn as
      the same body with its muzzle at the tube's bore; GoM's 40mm family standing in for the VOG-25, GoM's M203
      reload, caseless (muzzle-loaded, no spent case);
    - optics: GoM's Picatinny Rail (Up) on the carrying handle (drawn as <gun>_RAIL_UP: our clamp with GoM's rail on
      it, the Grozas' way) and every GoM optic on it (Rails.lua).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Underbarrel = require("WeaponSystems/Utils/Underbarrel")
local Ammo = require("WeaponSystems/Utils/Ammo")
local GoMReloads = require("GunsOfTien/GoMReloads")
local HandMagazines = require("GunsOfTien/HandMagazines")
local Rails = require("GunsOfTien/Rails")
require("GunsOfTien/RPK")                    -- the RPK 40 and drum in GoM's "762x39" profile, the AK bolt wrapper

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims",
    "ReloadsAndAnims/AnimationsFiring", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments",
    "Underbarrel" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local A91M = M .. "A91M"
local GUNS = { A91M }

local MAGS = {
    [A91M] = { "MarzGuns.762x39Magazine30", "MarzGuns.762x39Magazine75", "GunsOfTien.762x39Magazine40_RPK",
        "GunsOfTien.762x39Drum75_RPK" },
}

-------------------------------------------------
-- Magazines: GoM's AK profile
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("762x39", A91M)

-------------------------------------------------
-- Rate of fire: 700 rpm (600-800 published). The bullpup's straight line as the Grozas: a little steadier than
-- GoM's AK-47 (0.3 / 3.5)
-------------------------------------------------
RateOfFire.RegisterWeapon(A91M, { rpm = 700, enableSpread = true, sustainedSpread = 0.27, maxSpread = 3.3 })

-------------------------------------------------
-- The bolt (GoM's AK bolt swap: the handle on the piston rod), closing on the empty chamber as an AK does, and the
-- reload (GoM's FAMAS)
-------------------------------------------------
local closes = GunsOfTien_RPK and GunsOfTien_RPK.CLOSES_ON_EMPTY
if closes then
    for _, gun in ipairs(GUNS) do closes[gun] = true end
end
for _, gun in ipairs(GUNS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
end
local hand = {}
for _, mag in ipairs(MAGS[A91M]) do
    if mag:sub(1, 9) == "MarzGuns." then hand[mag] = "GunsOfTien." .. mag:match("[^.]+$") .. "_Hand" end
end
HandMagazines.register(A91M, hand)
ReloadAnim.RegisterWeapon(A91M, GoMReloads.profile("famas_rifle", { partState = { props = HandMagazines.props(hand) } }))

-------------------------------------------------
-- GoM's Picatinny Rail (Up) on the carrying handle, and GoM's optics on it
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
for _, gun in ipairs(GUNS) do
    Rails.Register(gun, { sides = { "Up" }, optics = OPTICS })
end

-------------------------------------------------
-- The launchers: GoM's M16A2_M203 way (its Underbarrel.lua, Ammunition.lua "40mm", ReloadAnims.lua "m203_reload")
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    local launcher, part = gun .. "_GL", gun .. "_GL_Integrated"
    Underbarrel.Register({ attachment = part, weapon = launcher, model = "self" })
    Ammo.RegisterMultipleItemsWithFamilies({ ["40mm"] = { launcher } })
    ReloadAnim.RegisterWeapon(launcher, GoMReloads.nonMagazineProfile("m203_reload", "doublebarrel", true))
    CSA.RegisterMultipleParts({ [part] = {} })
    PreventRemoval.Register({ part })
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as MK11.lua does): GoM's AK
-- magazines and AK mount (GoM's rule: the parts need the mount). The AKM slant compensator lists the A-91M in its
-- own script (the main mod's muzzle_devices.py).
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
    for _, mag in ipairs(MAGS[A91M]) do appendMountOn(mag, { A91M }) end
    appendMountOn("MarzGuns.AK_Muzzle_Mount_Device", { A91M })
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)
-- and at once (user, 2026-11-25): GoM's guns are in its parts' MountOn from the script files on, and a mod that
-- lists a gun's slots from MountOn when its own Lua loads (before OnGameBoot) missed ours
pcall(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt and the launcher always (GoM's
-- M16A2_M203 its M203), the standard magazine mostly, now and then a red dot or low scope with its rail (":PRU") at
-- GoM's M16A2 chances
-------------------------------------------------
local function optics()
    local out = {}
    for _, o in ipairs({ "ReflexS2_Sight", "Kobra_Sight", "OKP3_Sight", "JS14_Sight", "EXPS3_Sight", "EXPS1_Sight",
        "Aimpoint_Sight" }) do out[#out + 1] = "MarzGuns." .. o .. ":5:PRU" end
    for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope" }) do out[#out + 1] = "MarzGuns." .. o .. ":3:PRU" end
    return out
end

local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local optionals = {
        [A91M] = { "MarzGuns.762x39Magazine30:40", "MarzGuns.762x39Magazine75:1", "GunsOfTien.762x39Magazine40_RPK:3" },
    }
    for gun, list in pairs(optionals) do
        for _, o in ipairs(optics()) do list[#list + 1] = o end
        spawnTable[gun] = { required = { "MarzGuns.Bolt_Lock", gun .. "_GL_Integrated" }, optionals = list }
    end
end

GunsOfTienPost93_A91M = { GUNS = GUNS, MAGS = MAGS }
