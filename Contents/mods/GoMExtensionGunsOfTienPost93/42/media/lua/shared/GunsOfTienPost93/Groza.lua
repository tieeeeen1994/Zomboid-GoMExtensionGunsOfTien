--[[
    Guns of Tien - Post-93 -- the OTs-14 Groza family (user, 2026-11-11 / 12; docs/post93_design.md "OTs-14 Groza
    family") in Gunworks' and Guns of Marz's registries.

    TsKIB SOO's bullpup on the AKS-74U's mechanism, shown in April 1994 (scripts/post93/build_groza.py; items_groza.txt):
    - Groza-1: 7.62x39mm, long barrel, forend and front grip; GoM's "762x39" magazines (its 30 and 75, the main mod's
      RPK 40 and drum); GoM's AK muzzle mount and PBS-1 (with it fitted, 7.62x39 US Subsonic cycles the gun without
      racking: the main mod's Ammunition.lua rule, as on GoM's AKs);
    - Groza-2 Prototype: 5.45x39mm, the compact OTs-14-4A (no forend); held like a pistol (user, 2026-11-12), as GoM's
      MP5K and Post-93's MP7, so GoM's MP5K reload ("handgun2"); GoM's "545x39" magazines; no muzzle parts;
    - Groza-4: 9x39mm, short barrel inside the forend, front grip; GoM's AS VAL magazines ("AS Val"); its suppressor
      built in, as GoM's AS VAL (user, 2026-11-12): the quiet sound is in the gun's own stats (items_groza.txt) and the
      can a hidden part that cannot come off, with no stats of its own;
    - all: Auto / Single at 700 rpm; GoM's AK bolt swap (carrier and handle in one, on the right), closing on an empty
      chamber as an AK does (the main mod's RPK.lua wrapper, extended to these guns); GoM's FAMAS reload (a bullpup's:
      the magazine behind the grip; the Groza-2's MP5K one), GoM's magazines in the off hand at our size
      (HandMagazines.lua);
    - Groza-1 with GP-25 (user, 2026-11-12: "Make the Groza-1 with GP-25 now"), built as GoM's M16A2_M203: the Groza-1
      (its magazines, parts, rate and reload) with a hidden GROZAGL_GP25_Integrated part (PartType Underbarrel) that
      Gunworks' Underbarrel swaps for the launcher weapon GROZAGL_GP25 (Gunworks' radial menu: switch to the
      underbarrel and back), which draws its own model (`model = "self"`: the same body, its muzzle at the GP-25's
      bore) and gets the rifle's parts cloned onto it. The launcher: GoM's 40mm family (the M203's rounds stand in for
      the VOG-25, GoM having no other grenade round), GoM's M203 reload ("m203_reload", the double-barrel archetype),
      caseless (no spent case to pull out). No tube-opening part: the GP-25 is loaded from the muzzle;
    - optics: GoM's Picatinny Rail (Up) on the carrying handle (drawn as GROZA_RAIL_UP: a base clamped on the handle
      with GoM's own rail on it, so GoM's optics grip it at GoM's spacing) and every GoM optic on it (Rails.lua; GoM's
      own rule makes the optics need the rail). No side rails: the real gun has none.
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
local GROZA1 = M .. "GROZA1"
local GROZA2 = M .. "GROZA2"
local GROZA4 = M .. "GROZA4"
local GROZAGL = M .. "GROZAGL"
local GUNS = { GROZA1, GROZA2, GROZA4, GROZAGL }
local SUPPRESSOR = M .. "GROZA4_Integrated_Suppressor"
local GP25 = M .. "GROZAGL_GP25"                         -- the launcher weapon
local GP25_PART = M .. "GROZAGL_GP25_Integrated"         -- the rifle's hidden underbarrel part

local MAGS_762 = { "MarzGuns.762x39Magazine30", "MarzGuns.762x39Magazine75", "GunsOfTien.762x39Magazine40_RPK",
    "GunsOfTien.762x39Drum75_RPK" }
local MAGS = {
    [GROZA1] = MAGS_762,
    [GROZAGL] = MAGS_762,
    [GROZA2] = { "MarzGuns.545x39Magazine30_Bakelite", "MarzGuns.545x39Magazine45_Bakelite",
        "MarzGuns.545x39Magazine60_Bakelite", "MarzGuns.545x39Magazine100_Drum" },
    [GROZA4] = { "MarzGuns.9x39Magazine10", "MarzGuns.9x39Magazine20", "MarzGuns.9x39Magazine30" },
}

-------------------------------------------------
-- Magazines: GoM's own profiles
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("762x39", GROZA1)
Magazine.RegisterWeaponWithProfile("762x39", GROZAGL)
Magazine.RegisterWeaponWithProfile("545x39", GROZA2)
Magazine.RegisterWeaponWithProfile("AS Val", GROZA4)

-------------------------------------------------
-- Rate of fire: 700 rpm (the AKS-74U's mechanism; GoM's AKS-74U 650, 0.25 / 3.5, its AS VAL 900, 0.12 / 3.0). The
-- bullpup's straight line keeps the 7.62 one a little steadier than GoM's AK-47 (0.3 / 3.5).
-------------------------------------------------
RateOfFire.RegisterWeapon(GROZA1, { rpm = 700, enableSpread = true, sustainedSpread = 0.27, maxSpread = 3.3 })
RateOfFire.RegisterWeapon(GROZAGL, { rpm = 700, enableSpread = true, sustainedSpread = 0.27, maxSpread = 3.3 })
RateOfFire.RegisterWeapon(GROZA2, { rpm = 700, enableSpread = true, sustainedSpread = 0.22, maxSpread = 3.2 })
RateOfFire.RegisterWeapon(GROZA4, { rpm = 700, enableSpread = true, sustainedSpread = 0.15, maxSpread = 3.0 })

-------------------------------------------------
-- The bolt (GoM's AK bolt swap), closing on the empty chamber as an AK does, and the reload (GoM's FAMAS)
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
    local hand = {}
    for _, mag in ipairs(MAGS[gun]) do
        if mag:sub(1, 9) == "MarzGuns." then
            local name = mag:match("[^.]+$")
            -- the main mod's _Hand items (AK and AK-74 magazines); ours for the AS VAL's
            hand[mag] = (gun == GROZA4 and M or "GunsOfTien.") .. name .. "_Hand"
        end
    end
    HandMagazines.register(gun, hand)
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile(gun == GROZA2 and "handgun2" or "famas_rifle",
        { partState = { props = HandMagazines.props(hand) } }))
end

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
-- The Groza-4's built-in suppressor: drawn by a hidden part that cannot come off; the gun's own stats are the quiet
-- ones (as GoM's AS VAL), so the part has none
-------------------------------------------------
CSA.RegisterMultipleParts({ [SUPPRESSOR] = {} })
PreventRemoval.Register({ SUPPRESSOR })

-------------------------------------------------
-- The GP-25: GoM's M16A2_M203 way (its Underbarrel.lua, Ammunition.lua "40mm", ReloadAnims.lua "m203_reload")
-------------------------------------------------
Underbarrel.Register({ attachment = GP25_PART, weapon = GP25, model = "self" })
Ammo.RegisterMultipleItemsWithFamilies({ ["40mm"] = { GP25 } })
ReloadAnim.RegisterWeapon(GP25, GoMReloads.nonMagazineProfile("m203_reload", "doublebarrel", true))
CSA.RegisterMultipleParts({ [GP25_PART] = {} })
PreventRemoval.Register({ GP25_PART })

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as MK11.lua does): GoM's
-- magazines, and the Groza-1's AK muzzle mount and PBS-1 (GoM's rule: the PBS-1 needs the mount)
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
    for gun, mags in pairs(MAGS) do
        for _, mag in ipairs(mags) do appendMountOn(mag, { gun }) end
    end
    appendMountOn("MarzGuns.AK_Muzzle_Mount_Device", { GROZA1, GROZAGL })
    appendMountOn("MarzGuns.PBS-1_Suppressor", { GROZA1, GROZAGL })
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt; GoM's AK / AK-74 / AS VAL magazine
-- chances (the standard one mostly); now and then a red dot or low scope with its rail (":PRU"), at GoM's M16A2
-- chances; the Groza-4's built-in suppressor and the GP-25 always (GoM's M16A2_M203 its M203), the Groza-1's AK muzzle
-- mount now and then.
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
        [GROZA1] = { "MarzGuns.762x39Magazine30:40", "MarzGuns.762x39Magazine75:1",
            "GunsOfTien.762x39Magazine40_RPK:3", "MarzGuns.AK_Muzzle_Mount_Device:5" },
        [GROZA2] = { "MarzGuns.545x39Magazine30_Bakelite:40", "MarzGuns.545x39Magazine45_Bakelite:3",
            "MarzGuns.545x39Magazine100_Drum:1" },
        [GROZA4] = { "MarzGuns.9x39Magazine20:40", "MarzGuns.9x39Magazine10:10", "MarzGuns.9x39Magazine30:5" },
        [GROZAGL] = { "MarzGuns.762x39Magazine30:40", "MarzGuns.762x39Magazine75:1",
            "GunsOfTien.762x39Magazine40_RPK:3", "MarzGuns.AK_Muzzle_Mount_Device:5" },
    }
    for gun, list in pairs(optionals) do
        for _, o in ipairs(optics()) do list[#list + 1] = o end
        local required = { "MarzGuns.Bolt_Lock" }
        if gun == GROZA4 then required[2] = SUPPRESSOR end
        if gun == GROZAGL then required[2] = GP25_PART end
        spawnTable[gun] = { required = required, optionals = list }
    end
end

GunsOfTienPost93_Groza = { GUNS = GUNS, MAGS = MAGS, SUPPRESSOR = SUPPRESSOR, GP25 = GP25, GP25_PART = GP25_PART }
