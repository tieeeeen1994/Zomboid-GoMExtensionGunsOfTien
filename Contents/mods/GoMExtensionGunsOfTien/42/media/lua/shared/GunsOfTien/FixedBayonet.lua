--[[
    Guns of Tien -- fixing a bayonet turns the gun into a spear until it is unfixed (user, 2026-11-19).

    Gunworks' own bayonet (Utils/Bayonet.lua) stabbed with a shove or after a second of sprinting by putting a
    client-only stand-in weapon, MarzGuns.Attack_Bayonet, in the hands for one swing. The server never had that item:
    its EquipPacket.processServer looked the stand-in up by ID, found nothing and emptied the hands, and the hit
    packet's weapon (fields/hit/Weapon.parse: getInventory():getItemWithID) failed isConsistent, so the server dropped
    every bayonet hit. No Spear, Strength or Fitness XP, no endurance cost, no maintenance roll (the zombie was hurt
    only because the attacker's client applies its own hits).

    Now a fixed bayonet is a mode, built the way Gunworks swaps a rifle for its underbarrel launcher
    (Utils/Underbarrel.lua PerformSwap): the server takes the gun out of the inventory, keeps all of it in the new
    item's modData (ammo, chambered round, magazine, parts with their condition and modData, condition, name, fire
    mode, modData, Underbarrel.StatePreservers) and puts a real melee item in its place, in the same hands and hotbar
    slot. Unfixing rebuilds the gun from that record. Gunworks' PerformSwap cannot be reused: it refuses to start
    from a weapon that is not ranged, so it could never switch back from a melee one, and its helpers are local.

    The melee items (scripts/GunsOfTien/items_fixedbayonet.txt, gen_scripts.py fixed_bayonets) are one per gun, so
    each weighs what its gun weighs (HandWeapon.getActualWeight is the script weight plus the parts' weight
    modifiers; a per-item weight cannot be set) and draws the gun's model with every part on it. Their combat stats
    are Attack_Bayonet's (user: "Use the current stats of the stand-in"), Spear category, so vanilla does all the
    rest on the server: damage, XP, endurance, wear, how other players see the stab. The gun's parts are cloned onto
    the item without their stat changes (attachWeaponPart(part, false): a scope's MaxRange bonus would lengthen the
    stab); their weight still counts.

    Wear: the item's condition is the bayonet's (the attachment part's, which Gunworks copies from the knife when it
    is fitted; the SKS's folding bayonet is part of the gun, so the gun's), 0..10, and each hit loses a point 1 in N
    times, N the knife's ConditionLowerChanceOneIn (40 to 75; the SKS's own), as Gunworks' RollConditionLoss did.
    That N is set per item and not saved, so it is set again whenever the item is equipped (OnEquipPrimary runs on
    the server and on the owner's client, which rolls wear in multiplayer and sends it with syncItemFields). At 0
    the item's OnBreak queues it: the gun comes back with the bayonet taken off as a broken knife (Gunworks'
    RemoveBayonet), or a broken SKS.

    Gunworks' stab is switched off (Bayonet.BayonetAttack): a shove with a bayonet on the gun is a shove, and the
    sprint charge does nothing. Spear attacks of the fixed item are vanilla's, the sprint charge included.

    The gun's item ID changes on every swap, as with Gunworks' underbarrel. The hotbar slot stays: the attached slot
    fields travel with the item (InventoryItem.save), and ISHotbar's refresh picks it up by slot index.

    Sandbox option FixedBayonets (default on; user, 2026-11-19: "not all would want this change"), read when it is
    used, so a change applies at once: off = Gunworks' own stab again and no Fix Bayonet, but a gun already fixed
    can still be unfixed (key, menu, server), so no one is left holding a spear.
--]]

local Bayonet = require("WeaponSystems/Utils/Bayonet")
local Underbarrel = require("WeaponSystems/Utils/Underbarrel")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Ammo = require("WeaponSystems/Utils/Ammo")

local FixedBayonet = GunsOfTien_FixedBayonet or {}
GunsOfTien_FixedBayonet = FixedBayonet

FixedBayonet.MODULE = "GunsOfTien"
FixedBayonet.COMMAND = "fixedBayonet"
FixedBayonet.KEYBIND = "GunsOfTien_FixBayonet"
FixedBayonet.FALLBACK = "GunsOfTien.FixedBayonet"
FixedBayonet.ITEM_PREFIX = "GunsOfTien.FixedBayonet_"

local KEY_GUN = "GoT_FixedBayonetGun"          -- on the melee item: the gun, everything needed to rebuild it
local KEY_PART = "GoT_FixedBayonetPart"        -- on the melee item: the bayonet attachment's full type (nil: SKS)
local KEY_LOWER = "GoT_FixedBayonetWear"       -- on the melee item: 1 in N chance to lose condition per hit
local KNIFE_CONDITION_MAX = 10                 -- every Guns of Marz bayonet knife's ConditionMax
local DEFAULT_WEAR = 75

function FixedBayonet.IsEnabled()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.FixedBayonets == true
end

local function IsReservedModDataKey(key)
    return type(key) ~= "string" or key:sub(1, 16) == "GoT_FixedBayonet"
end

-------------------------------------------------
-- Which item a gun turns into
-------------------------------------------------

function FixedBayonet.ItemTypeFor(gunType)
    if not gunType then return nil end
    local own = FixedBayonet.ITEM_PREFIX .. (gunType:match("%.(.+)$") or gunType)
    if getScriptManager():getItem(own) then return own end
    return FixedBayonet.FALLBACK
end

function FixedBayonet.IsFixed(item)
    return item ~= nil and instanceof(item, "HandWeapon") and type(item:getModData()[KEY_GUN]) == "table"
end

local function BayonetPart(gun)
    local part = Bayonet.GetAttachedBayonetPart(gun)
    if part and part:getCondition() > 0 then return part end
    return nil
end

--- A ranged gun with a bayonet fitted (or the SKS's folding one), not switched to an underbarrel weapon, while the
--- sandbox option is on.
function FixedBayonet.CanFix(gun)
    if not FixedBayonet.IsEnabled() then return false end
    if not gun or not instanceof(gun, "HandWeapon") or not gun:isRanged() or gun:isBroken() then return false end
    if Underbarrel.IsWeaponInUnderbarrelMode(gun) then return false end
    return Bayonet.HasIntegratedBayonet(gun) or BayonetPart(gun) ~= nil
end

-------------------------------------------------
-- Record of the gun (Gunworks' Underbarrel BuildSnapshot / RebuildFromSnapshot, plus blood and favourite)
-------------------------------------------------

local function DeepCopyData(value)
    local valueType = type(value)
    if valueType == "number" or valueType == "string" or valueType == "boolean" then return value end
    if valueType ~= "table" then return nil end
    local copy = {}
    for key, item in pairs(value) do
        local keyType = type(key)
        if keyType == "string" or keyType == "number" then
            local copied = DeepCopyData(item)
            if copied ~= nil then copy[key] = copied end
        end
    end
    return copy
end

local function CopyModData(modData)
    local copy = {}
    for key, value in pairs(modData) do
        if not IsReservedModDataKey(key) then
            local copied = DeepCopyData(value)
            if copied ~= nil then copy[key] = copied end
        end
    end
    return copy
end

local function DetachAllParts(weapon, doChange)
    local attached = weapon:getAllWeaponParts()
    if not attached or attached:size() == 0 then return end
    local parts = {}
    for i = 0, attached:size() - 1 do parts[#parts + 1] = attached:get(i) end
    for i = 1, #parts do weapon:detachWeaponPart(nil, parts[i], doChange) end
end

local function Snapshot(gun)
    local modData = gun:getModData()
    local ammoType = gun:getAmmoType()
    local snapshot = {
        type = gun:getFullType(),
        condition = gun:getCondition(),
        conditionMax = gun:getConditionMax(),
        haveBeenRepaired = gun:getHaveBeenRepaired(),
        weaponSprite = gun:getWeaponSprite(),
        customName = gun:isCustomName() and modData.customName ~= nil and tostring(modData.customName) or nil,
        bloodLevel = gun:getBloodLevel(),
        favorite = gun:isFavorite(),
        ammo = {
            currentAmmoCount = gun:getCurrentAmmoCount(),
            roundChambered = gun:isRoundChambered(),
            spentRoundChambered = gun:isSpentRoundChambered(),
            spentRoundCount = gun:getSpentRoundCount(),
            jammed = gun:isJammed(),
            containsClip = gun:isContainsClip(),
            magazineType = gun:getMagazineType(),
            maxAmmo = gun:getMaxAmmo(),
            ammoType = ammoType and ammoType:getItemKey() or nil,
            fireMode = gun:getFireMode(),
            ammoList = Ammo.CopyAmmoList(modData.AmmoList),
        },
        parts = {},
        modData = CopyModData(modData),
        preservers = {},
    }
    local parts = gun:getAllWeaponParts()
    if parts then
        for i = 0, parts:size() - 1 do
            local part = parts:get(i)
            if part then
                snapshot.parts[#snapshot.parts + 1] = {
                    type = part:getFullType(),
                    partType = part:getPartType(),
                    condition = part:getCondition(),
                    modData = DeepCopyData(part:getModData()),
                }
            end
        end
    end
    -- other mods' state that is not in modData, registered with Gunworks for its underbarrel swap
    for i = 1, #Underbarrel.StatePreservers do
        local preserver = Underbarrel.StatePreservers[i]
        local data = preserver.snapshot(gun)
        if data ~= nil then snapshot.preservers[preserver.id] = DeepCopyData(data) end
    end
    return snapshot
end

local function RestoreAmmo(gun, ammo)
    if not ammo then return end
    -- MagazineType before ContainsClip: Java guards ContainsClip on usesExternalMagazine()
    if ammo.magazineType then
        gun:setMagazineType(ammo.magazineType)
        local magazine = instanceItem(ammo.magazineType)
        if magazine then gun:setMaxAmmo(magazine:getMaxAmmo()) end
    elseif ammo.maxAmmo then
        gun:setMaxAmmo(ammo.maxAmmo)
    end
    local ammoEnum = ammo.ammoType and Ammo.GetEnumForBullet(ammo.ammoType) or nil
    if ammoEnum then gun:setAmmoType(ammoEnum) end
    gun:setCurrentAmmoCount(ammo.currentAmmoCount or 0)
    gun:setRoundChambered(ammo.roundChambered == true)
    gun:setSpentRoundChambered(ammo.spentRoundChambered == true)
    gun:setSpentRoundCount(ammo.spentRoundCount or 0)
    gun:setJammed(ammo.jammed == true)
    if ammo.containsClip ~= nil then gun:setContainsClip(ammo.containsClip == true) end
    gun:getModData().AmmoList = Ammo.CopyAmmoList(ammo.ammoList)
end

local function Rebuild(snapshot)
    if type(snapshot) ~= "table" or not snapshot.type then return nil end
    local gun = instanceItem(snapshot.type)
    if not gun or not instanceof(gun, "HandWeapon") then return nil end

    -- a fresh instance's OnCreate may have fitted parts of its own
    DetachAllParts(gun, true)
    for _, saved in ipairs(snapshot.parts or {}) do
        local part = instanceItem(saved.type)
        if part and instanceof(part, "WeaponPart") then
            gun:attachWeaponPart(part)
            local attached = saved.partType and gun:getWeaponPart(saved.partType) or nil
            if attached and attached:getFullType() == saved.type then
                if saved.condition ~= nil then attached:setCondition(saved.condition) end
                if saved.modData then
                    local partModData = attached:getModData()
                    for key, value in pairs(saved.modData) do partModData[key] = value end
                end
            end
        end
    end

    local modData = gun:getModData()
    for key, value in pairs(snapshot.modData or {}) do
        if not IsReservedModDataKey(key) then modData[key] = value end
    end
    if snapshot.conditionMax and snapshot.conditionMax > 0 then gun:setConditionMax(snapshot.conditionMax) end
    if snapshot.condition ~= nil then gun:setCondition(snapshot.condition, false) end
    if snapshot.haveBeenRepaired then gun:setHaveBeenRepaired(snapshot.haveBeenRepaired) end
    if snapshot.weaponSprite and snapshot.weaponSprite ~= "" and gun:getWeaponSprite() ~= snapshot.weaponSprite then
        gun:setWeaponSprite(snapshot.weaponSprite)
    end
    if snapshot.customName and snapshot.customName ~= "" then
        gun:setName(snapshot.customName)
        gun:setCustomName(true)
    end
    if snapshot.bloodLevel then gun:setBloodLevel(snapshot.bloodLevel) end
    if snapshot.favorite then gun:setFavorite(true) end

    RestoreAmmo(gun, snapshot.ammo)
    for i = 1, #Underbarrel.StatePreservers do
        local preserver = Underbarrel.StatePreservers[i]
        local data = snapshot.preservers and snapshot.preservers[preserver.id]
        if data ~= nil then preserver.restore(gun, data) end
    end
    StatsFactory.ReapplyAllModifiers(gun)
    if snapshot.ammo and snapshot.ammo.fireMode then gun:setFireMode(snapshot.ammo.fireMode) end
    return gun
end

-------------------------------------------------
-- The swap (server, or the player's own game in single player)
-------------------------------------------------

--- Put `new` where `old` is: same container, same hands, same hotbar slot (Gunworks' ReplaceEquipped, sent the
--- same way; the slot fields travel in the item's bytes).
local function Replace(player, old, new)
    local inventory = player:getInventory()
    local container = old:getContainer() or inventory
    local inHand = player:getPrimaryHandItem() == old

    new:setAttachedSlot(old:getAttachedSlot())
    new:setAttachedSlotType(old:getAttachedSlotType())
    new:setAttachedToModel(old:getAttachedToModel())

    player:removeFromHands(old)
    player:removeAttachedItem(old)
    container:Remove(old)
    sendRemoveItemFromContainer(container, old)

    local added = container:AddItem(new) or new
    sendAddItemToContainer(container, added)
    if isServer() then sendItemStats(added) end

    if inHand then
        player:setPrimaryHandItem(added)
        player:setSecondaryHandItem(added:isTwoHandWeapon() and added or nil)
        player:resetEquippedHandsModels()
    end
    syncHandWeaponFields(player, added)
    if isServer() and inHand then sendEquip(player) end
    -- single player: the hotbar is here (a server's client refreshes on the command's answer)
    local hotbar = not isServer() and getPlayerHotbar and getPlayerHotbar(player:getPlayerNum())
    if hotbar then hotbar.needsRefresh = true end
    return added
end

local function ApplyWear(item)
    local wear = item:getModData()[KEY_LOWER]
    if type(wear) == "number" and wear >= 1 then item:setConditionLowerChance(wear) end
end

--- Gun in the primary hand -> its melee item. Returns the new item, or nil when nothing changed.
function FixedBayonet.Fix(player, gun)
    if not player or not FixedBayonet.CanFix(gun) or player:getPrimaryHandItem() ~= gun then return nil end
    local item = instanceItem(FixedBayonet.ItemTypeFor(gun:getFullType()))
    if not item or not instanceof(item, "HandWeapon") then return nil end

    local part, wear, condition
    if Bayonet.HasIntegratedBayonet(gun) then
        if not Bayonet.IsBayonetDeployed(gun) then Bayonet.ToggleIntegratedBayonet(gun) end
        wear, condition = gun:getConditionLowerChance(), gun:getCondition()
    else
        part = BayonetPart(gun)
        local knife = Bayonet.GetKnifeTypeFromAttachment(part:getFullType())
        local script = knife and getScriptManager():getItem(knife)
        wear = script and script:getConditionLowerChance() or DEFAULT_WEAR
        condition = math.min(part:getCondition(), KNIFE_CONDITION_MAX)
    end

    local modData = item:getModData()
    modData[KEY_GUN] = Snapshot(gun)
    modData[KEY_PART] = part and part:getFullType() or nil
    modData[KEY_LOWER] = wear
    ApplyWear(item)
    item:setCondition(math.max(1, math.min(condition, item:getConditionMax())), false)

    -- drawn like the gun: its parts (weight counted, stats not applied) and its model (a sawn Mosin keeps its cut)
    DetachAllParts(item, false)
    local parts = gun:getAllWeaponParts()
    for i = 0, (parts and parts:size() or 0) - 1 do
        local copy = instanceItem(parts:get(i):getFullType())
        if copy and instanceof(copy, "WeaponPart") then item:attachWeaponPart(copy, false) end
    end
    if not item:getModelWeaponPart() then item:setModelWeaponPart(gun:getModelWeaponPart()) end
    if gun:getWeaponSprite() then item:setWeaponSprite(gun:getWeaponSprite()) end
    item:setBloodLevel(gun:getBloodLevel())
    if gun:isFavorite() then item:setFavorite(true) end

    return Replace(player, gun, item)
end

--- Melee item -> its gun, wherever the item is in the player's inventory. At condition 0 the bayonet comes off as a
--- broken knife (an SKS stays broken). Returns the gun, or nil when nothing changed.
function FixedBayonet.Unfix(player, item)
    if not player or not FixedBayonet.IsFixed(item) then return nil end
    local modData = item:getModData()
    local gun = Rebuild(modData[KEY_GUN])
    if not gun then return nil end

    local condition = item:getCondition()
    if modData[KEY_PART] then
        local part = Bayonet.GetAttachedBayonetPart(gun)
        if part then
            part:setCondition(condition, false)
            if condition <= 0 then
                local removed, knife = Bayonet.RemoveBayonet(gun, player)
                if removed and knife and isServer() then sendAddItemToContainer(player:getInventory(), knife) end
            end
        end
    else
        gun:setCondition(condition, false)
    end
    gun:setBloodLevel(item:getBloodLevel())

    return Replace(player, item, gun)
end

-------------------------------------------------
-- Every side
-------------------------------------------------

-- Gunworks' stab with a client-only stand-in is off while the option is on: a shove with a bayonet fitted stays a
-- shove (the attack hook passes vanilla's hook as callback), the sprint charge (no callback) does nothing.
FixedBayonet.gunworksAttack = FixedBayonet.gunworksAttack or Bayonet.BayonetAttack
Bayonet.BayonetAttack = function(character, chargeDelta, weapon, callback)
    if not FixedBayonet.IsEnabled() then
        return FixedBayonet.gunworksAttack(character, chargeDelta, weapon, callback)
    end
    if callback then return callback(character, chargeDelta, weapon) end
end

--- Item scripts take what the live gun scripts have now, so a Guns of Marz update needs no new build: the weight,
--- and the ModelWeaponPart list (every instance shares its script's list, Item.InstanceItem setModelWeaponPart, so
--- refilling it reaches items already made). Runs at OnLoadedMapZones, after this and other mods' load-time edits.
function FixedBayonet.SyncScripts()
    local guns = {}
    for gun in pairs(Bayonet.BayonetMountableWeapons) do guns[gun] = true end
    for gun in pairs(Bayonet.IntegratedBayonets) do guns[gun] = true end
    for gun in pairs(guns) do
        local itemType = FixedBayonet.ItemTypeFor(gun)
        local gunScript = getScriptManager():getItem(gun)
        if itemType ~= FixedBayonet.FALLBACK and gunScript then
            getScriptManager():getItem(itemType):DoParam("Weight", tostring(gunScript:getActualWeight()))
            local ours = instanceItem(itemType)
            local theirs = instanceItem(gun)
            local list = ours and ours:getModelWeaponPart()
            local gunList = theirs and instanceof(theirs, "HandWeapon") and theirs:getModelWeaponPart()
            if list and gunList and list ~= gunList then
                list:clear()
                list:addAll(gunList)
            end
        end
    end
end

Events.OnLoadedMapZones.Add(FixedBayonet.SyncScripts)

Events.OnEquipPrimary.Add(function(character, item)
    if FixedBayonet.IsFixed(item) then ApplyWear(item) end
end)

-- OnBreak of the melee items (their script; Java calls it on the server or in single player, with the player whose
-- main inventory holds the item). Unfixed on the next tick (server/GunsOfTien/FixedBayonet.lua), out of the hit.
FixedBayonet.broken = FixedBayonet.broken or {}

function FixedBayonet.OnBreak(item, player)
    if item and player and instanceof(player, "IsoPlayer") then
        FixedBayonet.broken[#FixedBayonet.broken + 1] = { item = item, player = player }
    end
end

return FixedBayonet
