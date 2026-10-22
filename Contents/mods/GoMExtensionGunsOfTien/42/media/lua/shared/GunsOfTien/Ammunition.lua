--[[
    Guns of Tien -- the new rounds in Gunworks' ammo families, their stat profiles, realistic piercing and the
    7.62x39 US cycling rule.

    How Gunworks uses this (Gunworks_gang_framework WeaponSystems/Utils/Ammo.lua, StatsFactory.lua):
    - A family lists the rounds a magazine or gun can take; RegisterAmmoFamily appends to an existing family, and the
      order is the default reload priority, so ours go after Guns of Marz's (required first below).
    - A profile is an array of modifiers `function(weapon, base)` applied by the "Ammo" StatsFactory layer while
      modData ActiveAmmoProfile names it. Before any layer runs, every stat in an applicable layer's restore set is
      put back to the shadow item's value (script + attachments), so each stat a profile touches must be in a
      restore set, or it compounds or sticks after switching rounds.
    - The attack hook switches the profile when the round about to fire differs from the gun's AmmoType
      (Ammo.AmmoProfileSetter returns early when they are equal), so a gun that only ever fires its script's own
      round never gets an ammo profile. Piercing for those plain rounds is therefore a layer of its own, keyed by
      the gun's current AmmoType, not a profile.

    Sandbox (page GunsOfTien): RealisticPiercing, SubsonicRackRule (1 always rack, 2 unless a PBS-1 is fitted,
    3 never).
--]]

local Ammo = require("WeaponSystems/Utils/Ammo")
local SF = require("WeaponSystems/Utils/StatsFactory")
pcall(require, "MarzWeapons/Registries/Ammunition")

local GunsOfTien = {}

local function vars()
    return SandboxVars and SandboxVars.GunsOfTien
end

local function realisticPiercing()
    local v = vars()
    return v ~= nil and v.RealisticPiercing == true
end

local function subsonicRackRule()
    local v = vars()
    local rule = v and tonumber(v.SubsonicRackRule)
    return rule or 2
end

-- Stats our profiles change that Guns of Marz's restore set does not cover.
Ammo.RegisterRestoreStats({ "ProjectileSpread", "ProjectileWeightCenter", "HitChance" })

-------------------------------------------------
-- Families
-------------------------------------------------
local T = GunsOfTien_AmmoTypes

Ammo.RegisterMultipleAmmoFamilies({
    ["7.62x39mm"] = {
        { type = "GunsOfTien.762x39_Bullet_US", enum = T.BULLET_762x39_US, profile = "GunsOfTien_762x39US" },
        { type = "GunsOfTien.762x39_Bullet_SP", enum = T.BULLET_762x39_SP, profile = "GunsOfTien_762x39SP" },
        { type = "GunsOfTien.762x39_Bullet_SteelCore", enum = T.BULLET_762x39_SteelCore, profile = "GunsOfTien_762x39SteelCore" },
    },
    ["9x19mm"] = {
        { type = "GunsOfTien.9x19_Bullet_Subsonic", enum = T.BULLET_9x19_Subsonic, profile = "GunsOfTien_9x19Subsonic" },
        { type = "GunsOfTien.9x19_Bullet_HollowPoint", enum = T.BULLET_9x19_HollowPoint, profile = "GunsOfTien_9x19HollowPoint" },
        { type = "GunsOfTien.9x19_Bullet_PPP", enum = T.BULLET_9x19_PPP, profile = "GunsOfTien_9x19PPP" },
    },
    [".45 ACP"] = {
        { type = "GunsOfTien.45_Bullet_HollowPoint", enum = T.BULLET_45_HollowPoint, profile = "GunsOfTien_45HollowPoint" },
        { type = "GunsOfTien.45_Bullet_P", enum = T.BULLET_45_P, profile = "GunsOfTien_45P" },
    },
    ["9x39mm"] = {
        { type = "GunsOfTien.9x39_Bullet_SP6", enum = T.BULLET_9x39_SP6, profile = "GunsOfTien_9x39SP6" },
    },
    [".30-06"] = {
        { type = "GunsOfTien.3006_Bullet_SP", enum = T.BULLET_3006_SP, profile = "GunsOfTien_RifleSoftPoint" },
    },
    ["7.62x51mm"] = {
        { type = "GunsOfTien.308_Bullet_SP", enum = T.BULLET_308_SP, profile = "GunsOfTien_RifleSoftPoint" },
    },
    ["12Gauge"] = {
        { type = "GunsOfTien.12Gauge_Shell_Birdshot", enum = T.SHELL_12G_Birdshot, profile = "GunsOfTien_12GaugeBirdshot" },
    },
})

-------------------------------------------------
-- Profiles
-------------------------------------------------
-- Helpers return a group of modifiers; list() flattens groups and single modifiers into one profile.
local function damage(factor)
    return { SF.Multiply("MaxDamage", factor), SF.Multiply("MinDamage", factor) }
end

local function sound(factor)
    return { SF.Multiply("SoundRadius", factor), SF.Multiply("SoundVolume", factor) }
end

local function pierce(targets)
    return { SF.Set("PiercingBullets", targets > 1), SF.Set("MaxHitCount", targets) }
end

local function list(...)
    local out = {}
    for _, value in ipairs({ ... }) do
        if type(value) == "table" then
            for _, modifier in ipairs(value) do out[#out + 1] = modifier end
        else
            out[#out + 1] = value
        end
    end
    return out
end

-- Does the gun have this part fitted?
local function hasPart(weapon, fullType)
    local parts = weapon:getAllWeaponParts()
    if not parts then return false end
    for i = 0, parts:size() - 1 do
        local part = parts:get(i)
        if part and part:getFullType() == fullType then return true end
    end
    return false
end

local PBS1 = "MarzGuns.PBS-1_Suppressor"

-- The US round burns too little powder to work an AK's gas system; the PBS-1's back pressure pushes enough gas into
-- the gas port to cycle it (the round and the suppressor were made as a pair).
function GunsOfTien.subsonicNeedsRack(weapon)
    local rule = subsonicRackRule()
    if rule == 1 then return true end
    if rule == 3 then return false end
    return not hasPart(weapon, PBS1)
end

Ammo.RegisterMultipleAmmoStats({
    ["GunsOfTien_762x39US"] = list(
        damage(0.5),
        SF.Multiply("CritDmgMultiplier", 0.8),
        sound(0.5),
        SF.Multiply("ConditionLowerChanceOneIn", 2.0),
        function(weapon)
            weapon:setRackAfterShoot(GunsOfTien.subsonicNeedsRack(weapon))
        end
    ),
    ["GunsOfTien_762x39SP"] = list(
        damage(1.2),
        SF.Multiply("CritDmgMultiplier", 1.15),
        SF.Multiply("CriticalChance", 1.05),
        SF.Multiply("ConditionLowerChanceOneIn", 0.9),
        pierce(1)
    ),
    ["GunsOfTien_762x39SteelCore"] = list(
        damage(0.9),
        SF.Multiply("CritDmgMultiplier", 0.95),
        SF.Multiply("CriticalChance", 0.9),
        SF.Multiply("ConditionLowerChanceOneIn", 0.85),
        pierce(3)
    ),
    ["GunsOfTien_9x19Subsonic"] = list(
        damage(0.85),
        sound(0.7)
    ),
    ["GunsOfTien_9x19HollowPoint"] = list(
        damage(1.2),
        SF.Multiply("CritDmgMultiplier", 1.15),
        SF.Multiply("CriticalChance", 1.05),
        SF.Multiply("ConditionLowerChanceOneIn", 0.9)
    ),
    ["GunsOfTien_9x19PPP"] = list(
        damage(1.2),
        SF.Multiply("CritDmgMultiplier", 1.1),
        sound(1.1),
        SF.Multiply("ConditionLowerChanceOneIn", 0.6)
    ),
    ["GunsOfTien_45HollowPoint"] = list(
        damage(1.2),
        SF.Multiply("CritDmgMultiplier", 1.15),
        SF.Multiply("CriticalChance", 1.05),
        SF.Multiply("ConditionLowerChanceOneIn", 0.9)
    ),
    ["GunsOfTien_45P"] = list(
        damage(1.15),
        SF.Multiply("CritDmgMultiplier", 1.1),
        sound(1.1),
        SF.Multiply("ConditionLowerChanceOneIn", 0.7)
    ),
    ["GunsOfTien_9x39SP6"] = list(
        damage(0.9),
        SF.Multiply("CritDmgMultiplier", 0.95),
        pierce(3)
    ),
    ["GunsOfTien_RifleSoftPoint"] = list(
        damage(1.2),
        SF.Multiply("CritDmgMultiplier", 1.15),
        SF.Multiply("CriticalChance", 1.1),
        pierce(1)
    ),
    -- Pellets only exist on RangeFalloff guns (every GoM shotgun: 9 pellets, 9 hits, and the native code returns at
    -- most 9 pellet records). Each pellet rolls its own hit and damage, so lower damage per pellet, a wider pattern
    -- and a shorter reach make it deadly up close and weak beyond a few tiles. A crit multiplies every pellet hit
    -- (GoM shotguns: 70% chance, ×12), so both are cut too.
    ["GunsOfTien_12GaugeBirdshot"] = list(
        damage(0.3),
        SF.Multiply("CriticalChance", 0.4),
        SF.Multiply("CritDmgMultiplier", 0.5),
        SF.Multiply("MaxRange", 0.5),
        function(weapon)
            weapon:setProjectileSpread(math.max(0.3, weapon:getProjectileSpread() * 2.0))
        end
    ),
})

-------------------------------------------------
-- Realistic piercing for the plain rounds (a layer, see the top comment)
-------------------------------------------------
-- AmmoType enum -> modifiers while RealisticPiercing is on. Full metal jacket rifle rounds pass through a zombie
-- into the one behind it; GoM gives every rifle MaxHitCount 1, so its PiercingBullets = true does nothing. Plain
-- .30-30 is what real .30-30 almost always is, a flat-nosed soft point (pointed bullets are unsafe in a tube
-- magazine). GoM's plain 5.45 is the 7N6: steel core, and it tumbles.
local PLAIN_ROUNDS = {}

local function addPlain(enum, modifiers)
    if enum then PLAIN_ROUNDS[enum] = modifiers end
end

local SW = SWMG_AmmoTypes or {}
local fmj = list(pierce(2))
addPlain(SW.BULLET_3006, fmj)
addPlain(SW.BULLET_762x51, fmj)
addPlain(SW.BULLET_308, fmj)
addPlain(AmmoType.BULLETS_308, fmj)
addPlain(SW.BULLET_3030, list(pierce(1)))
addPlain(AmmoType.BULLETS_3030, list(pierce(1)))
addPlain(SW.BULLET_545x39, list(pierce(3), SF.Multiply("CriticalChance", 1.1)))

local function plainModifiers(weapon)
    if not weapon or not weapon.getAmmoType then return nil end
    local enum = weapon:getAmmoType()
    return enum and PLAIN_ROUNDS[enum] or nil
end

local layerRegistered = false
for _, layer in ipairs(SF.ModifierLayers or {}) do
    if layer.id == "GunsOfTien_RealisticPiercing" then layerRegistered = true end
end
if not layerRegistered then
    SF.RegisterModifierLayer("GunsOfTien_RealisticPiercing",
        function(weapon)
            if not realisticPiercing() then return nil end
            return plainModifiers(weapon)
        end,
        -- Restored whenever the layer applies, so turning the option off puts GoM's values back.
        { PiercingBullets = true, MaxHitCount = true, CriticalChance = true },
        function(weapon)
            return plainModifiers(weapon) ~= nil
        end)
end

-------------------------------------------------
-- The 147gr subsonic round is no quieter in the MP5SD
-------------------------------------------------
-- The round's sound x0.7 is the supersonic crack taken away (sound_model.py: -5 dB = x0.71). The MP5SD's ported
-- barrel already slows standard rounds below the speed of sound, and its sound (SoundTable.lua) has no crack, so the
-- round would take it away twice (user, 2026-10-22). Layers run in registration order, after Gunworks' "Ammo" layer,
-- so this one puts the SD's sound back to the shadow item's (script + attachments); the round's damage stays.
local SD = "MarzGuns.MP5SD"
local SUBSONIC_PROFILE = "GunsOfTien_9x19Subsonic"

local function scriptSound(weapon, base)
    weapon:setSoundRadius(base:getSoundRadius())
    weapon:setSoundVolume(base:getSoundVolume())
end

local sdRegistered = false
for _, layer in ipairs(SF.ModifierLayers) do
    if layer.id == "GunsOfTien_SubsonicInMP5SD" then sdRegistered = true end
end
if not sdRegistered then
    SF.RegisterModifierLayer("GunsOfTien_SubsonicInMP5SD",
        function(weapon)
            local md = weapon:getModData()
            if md.ActiveAmmoProfile ~= SUBSONIC_PROFILE then return nil end
            return { scriptSound }
        end,
        { SoundRadius = true, SoundVolume = true },
        function(weapon)
            return weapon and weapon.getFullType and weapon:getFullType() == SD
        end)
end

-------------------------------------------------
-- Keep the US round's cycling up to date on the shooter's copy
-------------------------------------------------
-- Gunworks re-applies stats on equip, attach / detach (server-side `complete` in MP) and round-type changes, but
-- the client's copy is not re-applied after a server-side attach, so the attack hook's per-shot call is used to
-- notice a PBS-1 fitted or removed (or the sandbox rule changed) since the last apply.
if not Ammo.GunsOfTienWrapped then
    Ammo.GunsOfTienWrapped = true
    local vanillaSetter = Ammo.AmmoProfileSetter
    function Ammo.AmmoProfileSetter(weapon, bulletType)
        vanillaSetter(weapon, bulletType)
        if not weapon or not weapon.getModData then return end
        local md = weapon:getModData()
        if md.ActiveAmmoProfile ~= "GunsOfTien_762x39US" then return end
        local signature = tostring(subsonicRackRule()) .. (hasPart(weapon, PBS1) and "P" or "-")
        if md.GunsOfTienCycling ~= signature then
            md.GunsOfTienCycling = signature
            SF.ReapplyAllModifiers(weapon)
        end
    end
end

return GunsOfTien
