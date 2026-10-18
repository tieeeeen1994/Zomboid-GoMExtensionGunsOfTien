--[[
    Guns of Tien -- sawing the stock off Guns of Marz's break-action shotguns (user, 2026-10-19: "only the wooden stocks
    of the older shotguns can be sawn... or rather those whose barrels can be sawn off"): the Double Barrel, the
    Stevens 555 and the TOZ-34, so that with sawn-off barrels too the gun is compact enough for a holster.

    GoM models these stocks into the gun's body mesh, so there was nothing to take off. Now:
    - Part: each gun has a hidden integrated stock (part type StockIntegrated, like GoM's SPAS-12 stock, so the gun
      tooltip's row reads "Stock (Integrated): Stevens 555 Stock"), fitted at spawn through GoM's required parts. A gun
      without one (spawned before this existed) has its full stock too. The recipe "Saw Off Shotgun Stock"
      (recipes_sawnstocks.txt: any saw, gun kept, a piece of Unusable Wood out) fits the sawn-off twin instead; it is
      never removed, the fitted part is the whole state (saved and synced with the gun's parts).
    - Model: the stockless body (scripts/build_sawn_stocks.py cuts GoM's mesh behind the pistol grip) is shown by
      Gunworks' ConditionalModel, a StatsFactory layer that sets the gun's own WeaponSprite (HandWeapon saves it per
      gun) from its parts on every ReapplyAllModifiers: <GUN>_SAWNSTOCK_SHORT with GoM's sawn-off barrels (muzzle point
      at their end), <GUN>_SAWNSTOCK with full ones. Barrels are parts drawn at the gun's origin, so both fit.
    - Handling: a layer of our own after GoM's CustomStatsAttachments (whose sawn-off barrel Sets AimingTime 30 and
      HitChance 70 on the Double Barrel): AimingTime +10 (42.21 CombatManager.setAimingDelay caps the post-shot
      aiming delay at the gun's AimingTime; these guns have 0, so GoM-style multipliers would do nothing), Hit Chance
      x0.87 and Recoil Delay x1.3, the reverse of GoM's deployed stocks (Aiming Time x0.75, Hit Chance x1.15). The
      sawn-off part weighs -0.5 (HandWeapon.getActualWeight adds every part's WeightModifier).
    - Holster: AttachmentType is per gun in the engine (InventoryItem.attachmentType) but never saved, so
      HandWeapon:getAttachmentType is wrapped (through its class metatable, like ZomboidFixesB42's MedicalCheck) to
      answer "Holster" for a gun with the sawn-off stock and sawn-off barrels (or no barrel). Every Lua caller asks
      that way: vanilla ISHotbar, Plysken Attachments Reborn, Gunworks. "Holster" fits vanilla's right and left belt
      holsters and the shoulder holster; the models' holster points turn the upright gun the way GoM's pistols are
      modelled. A sawn-off stock with full barrels stays a back-slot gun.
    - Shell holder: GoM's Shellholder sits on the buttstock, so the recipe takes it off into the inventory and
      Gunworks' UpgradeExclusives hides its Upgrade option on a sawn-off stock.
    - Sync: OnCreate runs on the server in multiplayer (ISHandcraftAction:performRecipe), which re-applies the gun
      there (model + stats in the item bytes other clients get when it is equipped or re-sent) and sends it back with
      syncHandWeaponFields (parts, not the sprite). The owner's copy is told the model at once (`sawnStock` command)
      and re-applied once its parts have arrived (the packets are unordered).
--]]

local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local ConditionalModel = require("WeaponSystems/Utils/ConditionalModel")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local UpgradeExclusives = require("WeaponSystems/Utils/UpgradeExclusives")
local Animations = require("WeaponSystems/Utils/Animations")

local M = "GunsOfTien."

local SawnStock = {}

SawnStock.MODULE = "GunsOfTien"
SawnStock.COMMAND = "sawnStock"
SawnStock.PART_TYPE = "StockIntegrated"
SawnStock.GUNS = {}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34" }) do
    SawnStock.GUNS["MarzGuns." .. gun] = {
        stock = M .. gun .. "_Stock",
        sawn = M .. gun .. "_Stock_Sawnoff",
        model = M .. gun .. "_SAWNSTOCK",
        shortModel = M .. gun .. "_SAWNSTOCK_SHORT",
        shortBarrels = { "MarzGuns." .. gun .. "_Barrel_Sawnoff_Close", "MarzGuns." .. gun .. "_Barrel_Sawnoff_Open" },
    }
end

function SawnStock.Entry(weapon)
    if not weapon or not instanceof(weapon, "HandWeapon") then return nil end
    return SawnStock.GUNS[weapon:getFullType()]
end

function SawnStock.IsSawn(weapon)
    local entry = SawnStock.Entry(weapon)
    if not entry then return false end
    local part = weapon:getWeaponPart(SawnStock.PART_TYPE)
    return part ~= nil and part:getFullType() == entry.sawn
end

--- Sawn-off stock and sawn-off barrels (or none fitted): short enough for a holster.
function SawnStock.FitsHolster(weapon)
    if not SawnStock.IsSawn(weapon) then return false end
    local barrel = weapon:getWeaponPart("Barrel")
    if not barrel then return true end
    local entry = SawnStock.GUNS[weapon:getFullType()]
    local barrelType = barrel:getFullType()
    return barrelType == entry.shortBarrels[1] or barrelType == entry.shortBarrels[2]
end

-------------------------------------------------
-- Model, handling, shell holder, spawn
-------------------------------------------------
for gun, entry in pairs(SawnStock.GUNS) do
    ConditionalModel.Register(gun, {
        rules = {
            { parts = { [SawnStock.PART_TYPE] = entry.sawn, Barrel = entry.shortBarrels }, model = entry.shortModel },
            { parts = { [SawnStock.PART_TYPE] = entry.sawn }, model = entry.model },
        },
    })
end

SawnStock.HANDLING = {
    StatsFactory.Adjust("AimingTime", 10),
    StatsFactory.Multiply("HitChance", 0.87),
    StatsFactory.Multiply("RecoilDelay", 1.3),
}

local layerRegistered = false
for _, layer in ipairs(StatsFactory.ModifierLayers or {}) do
    if layer.id == "GunsOfTien_SawnStock" then layerRegistered = true end
end
if not layerRegistered then
    StatsFactory.RegisterModifierLayer("GunsOfTien_SawnStock",
        function(weapon)
            return SawnStock.IsSawn(weapon) and SawnStock.HANDLING or nil
        end,
        { AimingTime = true, HitChance = true, RecoilDelay = true },
        function(weapon)
            return SawnStock.Entry(weapon) ~= nil
        end)
end

local sawnParts = {}
for _, entry in pairs(SawnStock.GUNS) do
    sawnParts[#sawnParts + 1] = entry.sawn
end
UpgradeExclusives.SetExclusives("MarzGuns.Shellholder", sawnParts)

local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    for gun, entry in pairs(SawnStock.GUNS) do
        local t = spawnTable[gun]
        if t then
            t.required = t.required or {}
            local present = false
            for _, part in ipairs(t.required) do
                if part == entry.stock then present = true end
            end
            if not present then table.insert(t.required, entry.stock) end
        end
    end
end

-------------------------------------------------
-- Holster: the gun's attachment type follows its parts
-------------------------------------------------
local meta = __classmetatables and HandWeapon and __classmetatables[HandWeapon.class]
local index = meta and meta.__index
local vanillaAttachmentType = index and (index.GunsOfTien_getAttachmentType or index.getAttachmentType)
if vanillaAttachmentType then
    index.GunsOfTien_getAttachmentType = vanillaAttachmentType      -- kept, so a Lua reload does not wrap twice
    index.getAttachmentType = function(weapon, ...)
        if SawnStock.FitsHolster(weapon) then return "Holster" end
        return vanillaAttachmentType(weapon, ...)
    end
else
    print("[GunsOfTien] SawnStock: HandWeapon:getAttachmentType is not reachable, sawn-off shotguns stay on the back")
end

-------------------------------------------------
-- The recipe (recipes_sawnstocks.txt)
-------------------------------------------------

--- Server / single player: saw the stock off, give back a shell holder, re-apply model and stats, send it back.
function SawnStock.Saw(weapon, character)
    local entry = SawnStock.Entry(weapon)
    if not entry or SawnStock.IsSawn(weapon) then return end
    local inventory = character:getInventory()
    local holder = weapon:getWeaponPart("Shellholder")
    if holder then
        weapon:detachWeaponPart(holder)
        local added = inventory:AddItem(holder)
        if added and isServer() then sendAddItemToContainer(inventory, added) end
    end
    FoldingStock.SwapStockAttachment(weapon, SawnStock.PART_TYPE, entry.sawn)
    StatsFactory.ReapplyAllModifiers(weapon)
    if isServer() then
        if character:isHandItem(weapon) then
            Animations.CallSyncHandWeaponFields(character, weapon)   -- re-equipped, so other players see the new model
        else
            syncHandWeaponFields(character, weapon)
        end
        sendServerCommand(character, SawnStock.MODULE, SawnStock.COMMAND,
            { id = weapon:getID(), sprite = weapon:getWeaponSprite() })
    else
        character:resetEquippedHandsModels()
    end
end

GunsOfTien_SawnStock = GunsOfTien_SawnStock or {}

--- Every candidate input item: a gun only while its stock is whole.
function GunsOfTien_SawnStock.OnTest(item, character)
    if SawnStock.Entry(item) then
        return not SawnStock.IsSawn(item)
    end
    return true
end

function GunsOfTien_SawnStock.OnCreate(craftRecipeData, character)
    local kept = craftRecipeData:getAllKeepInputItems()
    for i = 0, kept:size() - 1 do
        local item = kept:get(i)
        if SawnStock.Entry(item) and not SawnStock.IsSawn(item) then
            SawnStock.Saw(item, character)
            return
        end
    end
end

-------------------------------------------------
-- The owner's copy in multiplayer
-------------------------------------------------
if isClient() then
    local waiting = {}      -- { weapon, player, until } re-applied once the sawn-off part has arrived

    Events.OnServerCommand.Add(function(module, command, args)
        if module ~= SawnStock.MODULE or command ~= SawnStock.COMMAND or type(args) ~= "table" then return end
        for i = 0, getNumActivePlayers() - 1 do
            local player = getSpecificPlayer(i)
            local weapon = player and player:getInventory():getItemWithIDRecursiv(args.id)
            if weapon and SawnStock.Entry(weapon) then
                if args.sprite then weapon:setWeaponSprite(args.sprite) end
                player:resetEquippedHandsModels()
                waiting[#waiting + 1] = { weapon = weapon, player = player, untilMs = getTimestampMs() + 10000 }
            end
        end
    end)

    Events.OnTick.Add(function()
        if #waiting == 0 then return end
        local now = getTimestampMs()
        for i = #waiting, 1, -1 do
            local w = waiting[i]
            if SawnStock.IsSawn(w.weapon) then
                StatsFactory.ReapplyAllModifiers(w.weapon)
                w.player:resetEquippedHandsModels()
                table.remove(waiting, i)
            elseif now > w.untilMs then
                table.remove(waiting, i)
            end
        end
    end)
end

return SawnStock
