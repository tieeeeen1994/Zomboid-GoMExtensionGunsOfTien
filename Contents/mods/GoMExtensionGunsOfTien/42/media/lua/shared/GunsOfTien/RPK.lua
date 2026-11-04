--[[
    Guns of Tien -- the RPK and RPK-74 (docs/design.md 4j; user, 2026-11-02) in Gunworks' and Guns of Marz's
    registries.

    Kalashnikov's squad machine guns of 1961 (7.62x39mm) and 1974 (5.45x39mm), built on GoM's AK-47 and AK-74
    (scripts/build_rpk.py) and registered as GoM registers those (items_rpk.txt):
    - magazines: the RPK takes its own 40 and 75-round drum (in GoM's 7.62x39mm family, so the 7.62x39 loads of
      Ammunition.lua work in them) and GoM's 30 and 75, under a profile of its own; the 40 and the drum also fit GoM's
      AK-47; the RPK-74 takes GoM's whole "545x39" profile (its Bakelite 45 is the real RPK-74 magazine);
    - 600 rpm, Auto / Single, steadier in sustained fire than GoM's AKs (heavier barrel);
    - the bolt with its reciprocating handle moves on each shot and stays back when empty (GoM's AK bolt swap: the AK
      handle is on the carrier, so no ChargingHandle part);
    - GoM's AK reload ("ak_rifle", GoMReloads.lua), GoM's magazines in the off hand at the guns' size
      (HandMagazines.lua);
    - the folding bipod: two hidden parts each gun draws with its own model, GoM's rail bipod stats and spread when
      deployed, nothing when folded (folded on a found gun);
    - GoM's AK parts: the AK mount and every optic GoM fits on its AK-47 (they need the mount, GoM's
      AttachmentsRequiredParts.lua), the AK muzzle mount device and the PBS-1, appended to their MountOn. With the
      PBS-1 fitted, 7.62x39 US Subsonic cycles the RPK as it does the AKs (Ammunition.lua).
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local BipodSystem = require("WeaponSystems/Utils/BipodSystem")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/AnimationsFiring", "AttachmentCustomStats",
    "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local RPK = M .. "RPK"
local RPK74 = M .. "RPK74"
local MAG40 = M .. "762x39Magazine40_RPK"
local DRUM75 = M .. "762x39Drum75_RPK"
local OWN_MAGS = { MAG40, DRUM75 }
local RPK_MAGS = { MAG40, DRUM75, "MarzGuns.762x39Magazine30", "MarzGuns.762x39Magazine75" }
local RPK74_MAGS = { "MarzGuns.545x39Magazine45_Bakelite", "MarzGuns.545x39Magazine30_Bakelite",
    "MarzGuns.545x39Magazine60_Bakelite", "MarzGuns.545x39Magazine100_Drum" }
local FOLDED = M .. "RPK_Integrated_Bipod_Folded"
local DEPLOYED = M .. "RPK_Integrated_Bipod_Deployed"
local GUNS = { RPK, RPK74 }

-------------------------------------------------
-- Magazines
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x39mm RPK", RPK_MAGS)
Magazine.RegisterWeaponWithProfile("7.62x39mm RPK", RPK)
Magazine.RegisterWeaponWithProfile("545x39", RPK74)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x39mm"] = OWN_MAGS })

-- The 40 and the drum fit GoM's AK-47 too, as the real ones fit any AK (user, 2026-11-02): GoM's "762x39" profile
-- (appended to) and their MountOn (items_rpk.txt) take them, and GoM's AK-47 gets a model line for each, drawn at
-- GoM's size (`<magazine>_GoM`). Item.DoParam("ModelWeaponPart = ...") adds to the script's list (replacing an entry of the same part
-- type in place but appending it again: 42.21 Item.DoParam), and HandWeapon.setModelWeaponPart shares that list, so
-- AK-47s that already exist draw it too. Once per script object: the scripts are rebuilt when a game is left.
Magazine.RegisterMagazineProfile("762x39", OWN_MAGS)
local gomAk47Done = {}
local function gomAk47Model()
    local script = ScriptManager.instance:getItem("MarzGuns.AK47")
    if not script or gomAk47Done[script] then return end
    gomAk47Done[script] = true
    for _, mag in ipairs(OWN_MAGS) do
        script:DoParam("ModelWeaponPart = " .. mag .. " " .. mag .. "_GoM magazine magazine")
    end
end
Events.OnGameBoot.Add(gomAk47Model)
Events.OnInitGlobalModData.Add(gomAk47Model)

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire); GoM's AK-47 0.3 / 3.5, AK-74 0.2 / 3.0
-------------------------------------------------
RateOfFire.RegisterWeapon(RPK, { rpm = 600, enableSpread = true, sustainedSpread = 0.2, maxSpread = 3.0 })
RateOfFire.RegisterWeapon(RPK74, { rpm = 600, enableSpread = true, sustainedSpread = 0.15, maxSpread = 2.5 })

-------------------------------------------------
-- The bolt (GoM's AK bolt swap) and the reload (GoM's AK reload)
-------------------------------------------------
-- GoM's AK reload puts the magazine in the off hand: GoM's ones as our scaled _Hand items (HandMagazines.lua)
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local GoMReloads = require("GunsOfTien/GoMReloads")
local HandMagazines = require("GunsOfTien/HandMagazines")
local HAND = {
    [RPK] = HandMagazines.mapOf({ RPK_MAGS[3], RPK_MAGS[4] }),
    [RPK74] = HandMagazines.mapOf(RPK74_MAGS),
}
-- The AK's charging handle is part of the bolt carrier, so GoM's AK bolt model (carrier and handle in one) moving on
-- each shot and with the rack is right, as on the SCARs. But an AK has no bolt hold-open: the carrier closes on the
-- empty chamber after the last round. Gunworks (42.13 Animations.lockActionOpen) shows the bolt back for a cycle after
-- each shot and then lets releaseActionLock close it only while a round is chambered, i.e. holds it open on an empty
-- gun (right for the AUGs and UMPs). For the RPKs it closes always (releaseActionLockForce). lockActionOpen looks the
-- release up on the table at each shot, so the wrapper takes effect for the next one. GoM's own AKs are left as GoM
-- registers them.
local CLOSES_ON_EMPTY = { [RPK] = true, [RPK74] = true }
if not Animations.GunsOfTienRPKWrapped and Animations.releaseActionLock and Animations.releaseActionLockForce then
    Animations.GunsOfTienRPKWrapped = true
    local release = Animations.releaseActionLock
    function Animations.releaseActionLock(player, weapon)
        if weapon and weapon.getFullType and CLOSES_ON_EMPTY[weapon:getFullType()] then
            return Animations.releaseActionLockForce(player, weapon)
        end
        return release(player, weapon)
    end
end

for _, gun in ipairs(GUNS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    HandMagazines.register(gun, HAND[gun])
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("ak_rifle",
        { partState = { props = HandMagazines.props(HAND[gun]) } }))
end

-------------------------------------------------
-- The folding bipod: GoM's rail bipod (Bipod_Deployed) stats and spread
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    FoldingBipod.RegisterWeapon(gun, {
        attachments = { partType = "BipodIntegrated", folded = FOLDED, deployed = DEPLOYED },
        initialState = "folded",
    })
end
-- Rests on low walls, windows and tables while aiming (Gunworks' bipod stance, as GoM registers its bipods)
BipodSystem.RegisterBipod(DEPLOYED)
CSA.RegisterMultipleParts({
    [DEPLOYED] = {
        SF.Multiply("AimingTime", 1.1),
        SF.Multiply("CriticalChance", 1.15),
        SF.Multiply("HitChance", 1.15),
    },
    [FOLDED] = {},
})
RateOfFire.RegisterSpreadPartModifier(DEPLOYED, { sustainedSpreadMult = 0.65, maxSpreadMult = 0.65 })

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload; GoM's own are
-- registered by GoM)
-------------------------------------------------
PreventRemoval.Register(OWN_MAGS)

-------------------------------------------------
-- GoM's parts and magazines allowed on them: appended to their MountOn (DoParam replaces the list, so it is read and
-- written back whole, as Glock21.lua does)
-------------------------------------------------
local AK_PARTS = { "MarzGuns.AK_Mount", "MarzGuns.AK_Muzzle_Mount_Device", "MarzGuns.PBS-1_Suppressor" }
local OPTICS = { "EXPS1_Sight", "EXPS3_Sight", "ElcanX2_Scope", "LR10X_Scope", "Aimpoint_Sight", "TA28_Scope",
    "LR4X_Scope", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "Kobra_Sight", "TR06X_Scope", "PSO1_Scope",
    "LRX12X_Scope" }
for _, o in ipairs(OPTICS) do AK_PARTS[#AK_PARTS + 1] = "MarzGuns." .. o end

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
    for _, part in ipairs(AK_PARTS) do
        appendMountOn(part, RPK)
        appendMountOn(part, RPK74)
    end
    for i = 3, #RPK_MAGS do appendMountOn(RPK_MAGS[i], RPK) end
    for _, mag in ipairs(RPK74_MAGS) do appendMountOn(mag, RPK74) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the bipod folded, its own magazine
-- at GoM's AK chance for the 30, the AK's other magazines more rarely, GoM's AK-47 optics with the AK mount (":AM")
-- at GoM's chances.
-------------------------------------------------
local function optics()
    local out = {}
    for _, o in ipairs({ "ReflexS2_Sight", "Kobra_Sight", "OKP3_Sight", "JS14_Sight", "EXPS3_Sight", "EXPS1_Sight",
        "Aimpoint_Sight" }) do out[#out + 1] = "MarzGuns." .. o .. ":5:AM" end
    for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope" }) do out[#out + 1] = "MarzGuns." .. o .. ":3:AM" end
    for _, o in ipairs({ "TR06X_Scope", "PSO1_Scope", "LR10X_Scope", "LRX12X_Scope" }) do
        out[#out + 1] = "MarzGuns." .. o .. ":1:AM"
    end
    return out
end

local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local rpk = { MAG40 .. ":30", DRUM75 .. ":5", "MarzGuns.762x39Magazine30:10", "MarzGuns.762x39Magazine75:1" }
    local rpk74 = { "MarzGuns.545x39Magazine45_Bakelite:30", "MarzGuns.545x39Magazine30_Bakelite:10",
        "MarzGuns.545x39Magazine100_Drum:1" }
    for _, o in ipairs(optics()) do
        rpk[#rpk + 1] = o
        rpk74[#rpk74 + 1] = o
    end
    spawnTable[RPK] = { required = { "MarzGuns.Bolt_Lock", FOLDED }, optionals = rpk }
    spawnTable[RPK74] = { required = { "MarzGuns.Bolt_Lock", FOLDED }, optionals = rpk74 }
end

GunsOfTien_RPK = { RPK = RPK, RPK74 = RPK74, MAG40 = MAG40, DRUM75 = DRUM75, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
