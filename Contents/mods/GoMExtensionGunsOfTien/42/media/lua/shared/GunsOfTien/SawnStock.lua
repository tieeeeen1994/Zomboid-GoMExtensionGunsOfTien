--[[
    Guns of Tien -- sawing the stock off Guns of Marz's break-action shotguns (user, 2026-10-19: "only the wooden stocks
    of the older shotguns can be sawn... or rather those whose barrels can be sawn off"): the Double Barrel, the
    Stevens 555 and the TOZ-34, so that with sawn-off barrels too the gun is compact enough for a holster.

    GoM models these stocks into the gun's body mesh, so there was nothing to take off. Now:
    - Part: each gun has a hidden integrated stock (part type StockIntegrated, like GoM's SPAS-12 stock, so the gun
      tooltip's row reads "Stock (Integrated): Stevens 555 Stock"), fitted at spawn through GoM's required parts. A gun
      without one (spawned before this existed) has its full stock too. The recipe "Saw Off Shotgun Stock"
      (recipes_sawnstocks.txt: any saw, gun kept) fits the sawn-off twin instead; it is never removed, the fitted part
      is the whole state (saved and synced with the gun's parts).
    - Offcuts (user, 2026-10-19: "we should just introduce new items"): what is sawn away is kept, weighing what the gun
      loses. The stock recipe hands over <GUN>_StockOffcut (0.5, burns and makes charcoal like Unusable Wood), and
      GoM's "Saw Off Shotgun Barrels" (craftRecipe Base.SawnOffShotgunBarrels, which had no OnCreate and gave nothing
      back) gets an OnCreate here that hands over <GUN>_BarrelOffcuts (2.0 = GoM's 3.0 - 1.0, steel to smelt). Their
      meshes are the pieces build_sawn_stocks.py cuts off GoM's own.
    - Sound: both recipes use vanilla's SawOffShotgun action, whose sound is the carpentry saw ("Sawing"): right for
      the stock, wrong for a hacksaw through steel. GoM's barrel recipe gets timedactions_sawnstocks.txt's
      GunsOfTien_SawOffShotgunBarrels (the same with "CraftMetalSawing"), handed to the action in ISHandcraftAction.new:
      a recipe resolves its timedAction in OnScriptsLoaded, before any Lua, and has no setter.
    - Model: the stockless body (scripts/build_sawn_stocks.py cuts GoM's mesh behind the pistol grip) is shown by
      Gunworks' ConditionalModel, a StatsFactory layer that sets the gun's own WeaponSprite (HandWeapon saves it per
      gun) from its parts on every ReapplyAllModifiers: <GUN>_SAWNSTOCK_SHORT with GoM's sawn-off barrels (muzzle point
      at their end), <GUN>_SAWNSTOCK with full ones. Barrels are parts drawn at the gun's origin, so both fit.
    - Handling: a layer of our own after GoM's CustomStatsAttachments (whose sawn-off barrel Sets AimingTime 30 and
      HitChance 70 on the Double Barrel): AimingTime x0.75, quicker to aim in like GoM's sawn-off barrels (40 to 30;
      user, 2026-10-19: "aiming in should be faster like a sawn off barrel"), so both together give 22; Hit Chance
      x0.87 and Recoil Delay x1.3 (no shoulder to steady it or take the kick; the longer recoil also adds more aiming
      delay per shot). The
      sawn-off part weighs -0.5 (HandWeapon.getActualWeight adds every part's WeightModifier).
    - Sawn-off barrels: GoM gives stats only to the Double Barrel's (AttachmentCustomStats.lua: Aiming Time 30, Hit
      Chance 70, spread 2.0, range 15, against 40 / 65 / 0.6 / 20 on all three guns); the Stevens 555's and TOZ-34's
      only got lighter. They get the same entry (user, 2026-10-19: "give the same stats to the sawn off barrels and
      stocks"), copied from GoM's registration so it follows GoM's numbers; one GoM registers itself is left alone.
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
local CustomStatsAttachments = require("WeaponSystems/Utils/CustomStatsAttachments")
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
        stockOffcut = M .. gun .. "_StockOffcut",
        barrelOffcuts = M .. gun .. "_BarrelOffcuts",
    }
end

-- GoM's full-length barrels, which its barrel recipe saws: full type -> our offcuts of them
SawnStock.FULL_BARRELS = {}
for _, entry in pairs(SawnStock.GUNS) do
    local gun = entry.barrelOffcuts:sub(#M + 1, -#"_BarrelOffcuts" - 1)
    SawnStock.FULL_BARRELS["MarzGuns." .. gun .. "_Barrel_Close"] = entry.barrelOffcuts
    SawnStock.FULL_BARRELS["MarzGuns." .. gun .. "_Barrel_Open"] = entry.barrelOffcuts
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
    StatsFactory.Multiply("AimingTime", 0.75),
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

-- The Double Barrel's sawn-off barrel stats on the Stevens 555's and TOZ-34's (GoM's lua/shared loads before ours).
local SAWN_BARREL_STATS = {
    StatsFactory.Set("AimingTime", 30),
    StatsFactory.Set("HitChance", 70),
    StatsFactory.Set("ProjectileSpread", 2.0),
    StatsFactory.Set("MaxRange", 15.0),
}
local gomSawn = CustomStatsAttachments.RegisteredParts["MarzGuns.DOUBLEBARREL_Barrel_Sawnoff_Close"]
local sawnBarrelStats = gomSawn and gomSawn.modifiers or SAWN_BARREL_STATS
for _, entry in pairs(SawnStock.GUNS) do
    for _, barrel in ipairs(entry.shortBarrels) do
        if not CustomStatsAttachments.RegisteredParts[barrel] then
            CustomStatsAttachments.RegisterPart(barrel, sawnBarrelStats)
        end
    end
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

--- Server / single player: saw the stock off, give back a shell holder and the stock offcut, re-apply model and
--- stats, send it back.
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
    local offcut = instanceItem(entry.stockOffcut)
    if offcut then Actions.addOrDropItem(character, offcut) end      -- dropped at the feet when too heavy, and sent
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

--- GoM's barrel recipe (server / single player): the barrel ends sawn off its full-length barrels.
function GunsOfTien_SawnStock.OnCreateBarrels(craftRecipeData, character)
    local consumed = craftRecipeData:getAllConsumedItems()
    for i = 0, consumed:size() - 1 do
        local offcuts = SawnStock.FULL_BARRELS[consumed:get(i):getFullType()]
        local item = offcuts and instanceItem(offcuts)
        if item then
            Actions.addOrDropItem(character, item)
            return
        end
    end
end

-- Recipe scripts are fresh at every world load, and OnLoadMapZones follows their PostWorldDictionaryInit on client,
-- server and single player. Load on a loaded recipe sets only the keys given (and resets its display name). GoM's
-- recipe has no OnCreate of its own; if a GoM update adds one, this replaces it.
local function hookBarrelRecipe()
    local recipe = ScriptManager.instance:getCraftRecipe("Base.SawnOffShotgunBarrels")
    if not recipe then
        print("[GunsOfTien] SawnStock: GoM's SawnOffShotgunBarrels recipe not found, sawn-off barrels give no offcuts")
        return
    end
    local displayName = recipe:getTranslationName()
    recipe:Load(recipe:getName(), "craftRecipe " .. recipe:getName()
        .. " { OnCreate = GunsOfTien_SawnStock.OnCreateBarrels, }")
    recipe:overrideTranslationName(displayName)
end

Events.OnLoadMapZones.Add(hookBarrelRecipe)

-- The metal sawing sound for GoM's barrel recipe: ISHandcraftAction takes its anim, props and sound from
-- self.actionScript, set in new from the recipe (vanilla's ISHandcraftAction, client and server alike).
local BARREL_RECIPE = "SawnOffShotgunBarrels"
local BARREL_ACTION = "GunsOfTien_SawOffShotgunBarrels"
if ISHandcraftAction and not ISHandcraftAction.GunsOfTien_new then
    ISHandcraftAction.GunsOfTien_new = ISHandcraftAction.new
    ISHandcraftAction.new = function(self, character, craftRecipe, ...)
        local o = ISHandcraftAction.GunsOfTien_new(self, character, craftRecipe, ...)
        if o and craftRecipe and craftRecipe:getName() == BARREL_RECIPE then
            local script = ScriptManager.instance:getTimedActionScript(BARREL_ACTION)
            if script then o.actionScript = script end
        end
        return o
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
