--[[
    Guns of Tien -- sawing the stock off Guns of Marz's break-action shotguns (user, 2026-10-19: "only the wooden stocks
    of the older shotguns can be sawn... or rather those whose barrels can be sawn off"): the Double Barrel, the
    Stevens 555 and the TOZ-34, so that with sawn-off barrels too the gun is compact enough for a holster.

    GoM models these stocks into the gun's body mesh, so there was nothing to take off. Now:
    - Part: each gun has a hidden integrated stock (part type StockIntegrated, like GoM's SPAS-12 stock, so the gun
      tooltip's row reads "Stock (Integrated): Stevens 555 Stock"), fitted at spawn through GoM's required parts. A gun
      without one (spawned before this existed) gets it when its look is next applied (ApplyLook: re-applied, or
      listed in a client's container). The recipe "Saw Off Shotgun Stock"
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

    The Mosin-Nagant Obrez (user, 2026-10-29: "a closer to realistic obrez", from a photo of one): GoM's Mosin has its
    barrel and full-length forend in the body mesh, so both cuts are ours, each a recipe of its own like the shotguns'
    ("Saw Off Rifle Stock", any saw; "Saw Off Rifle Barrel", GoM's barrel recipe's metal saws and our metal sawing
    action).
    - Parts: hidden integrated MOSIN_Stock and MOSIN_Barrel (part type BarrelIntegrated), each swapped for its
      sawn-off twin by its recipe. Models (ConditionalModel): MOSIN_SAWNSTOCK, MOSIN_SAWNBARREL (barrel 4 cm past the
      upper band, the front sight moved back onto it, muzzle point there) and MOSIN_OBREZ (both, with holster points).
    - Offcuts: the stock cut hands over MOSIN_StockOffcut (0.5, wood); the barrel cut MOSIN_BarrelOffcut (0.6, small
      steel to smelt) and MOSIN_ForendOffcut (0.3, wood). The gun loses what they weigh (part WeightModifiers).
    - Barrel cut (the Obrez's real numbers: ~27 cm barrel, about half the energy, a .50 AE's): damage x0.85, Hit Chance
      60 -> 50 and Aiming Time 70 -> 45 (rear sight only, lighter), sights 4-12 (GoM's short carbines) and 2-9 with
      the stock sawn off too (GoM's magnum revolvers: no shoulder), range x0.5, Recoil Delay x1.2, sound x1.35 (the
      mod's sound model, sound_model.py: +3 dB per halving of the 28.7" barrel, 10.5" left) and vanilla's sawn-off
      shotgun flash. The stock cut adds the shotguns' handling layer on top. Sight ranges are the gun's own, so a fitted
      scope keeps its own pair.
    - Bayonet: the lug goes with the barrel, so the barrel cut takes a fitted bayonet off into the inventory and
      UpgradeExclusives hides the bayonets' Upgrade options on a sawn-off barrel.
    - Holster: with both cuts.

    Names (user, 2026-10-29): a gun's name follows its cuts ("Mosin-Nagant Obrez", "Sawn-Off Double Barrel Pistol",
    IG_UI.json IGUI_GunsOfTien_<GUN>_SawnBarrel / SawnStock / SawnBoth; a shotgun's barrels count as sawn while GoM's
    sawn-off barrels are fitted). InventoryItem.name is per item and saved as a plain string whenever it differs from
    the script's name, so it is set again in this machine's language after every ReapplyAllModifiers (a StatsFactory
    restore handler: Gunworks re-applies a player's whole inventory at game start and a gun on every equip and part
    change). A name the player gave the gun (isCustomName) is left alone. A gun nobody has handled since the server
    named it keeps the server's language: English on a dedicated server, which has no mod translations at all (42.21
    GameServer.main runs Translator.loadFiles once at startup, before doMinimumInit loads the mods, and never again;
    getText of our key gave the key back, so guns sawn there showed "IGUI_GunsOfTien_..." in every container the
    client did not rename them in). So the name comes from getTextOrNull, else from ENGLISH (a copy of IG_UI.json's),
    and a client renames our guns in every container it lists (client/GunsOfTien/SawnNames.lua).
    Icons (user, 2026-10-29): each cut state has its own (make_offcut_art.py: the gun drawn as GoM's icon of it, at
    the same scale, so it reads shorter), shown through modData customInventoryIcon, set with the name.
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
SawnStock.BARREL_PART_TYPE = "BarrelIntegrated"
SawnStock.GUNS = {}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34" }) do
    SawnStock.GUNS["MarzGuns." .. gun] = {
        gun = gun,
        stock = M .. gun .. "_Stock",
        sawn = M .. gun .. "_Stock_Sawnoff",
        model = M .. gun .. "_SAWNSTOCK",
        shortModel = M .. gun .. "_SAWNSTOCK_SHORT",
        shortBarrels = { "MarzGuns." .. gun .. "_Barrel_Sawnoff_Close", "MarzGuns." .. gun .. "_Barrel_Sawnoff_Open" },
        stockOffcut = M .. gun .. "_StockOffcut",
        barrelOffcuts = M .. gun .. "_BarrelOffcuts",
    }
end
SawnStock.GUNS["MarzGuns.MOSIN"] = {
    gun = "MOSIN",
    stock = M .. "MOSIN_Stock",
    sawn = M .. "MOSIN_Stock_Sawnoff",
    barrel = M .. "MOSIN_Barrel",
    sawnBarrel = M .. "MOSIN_Barrel_Sawnoff",
    model = M .. "MOSIN_SAWNSTOCK",
    barrelModel = M .. "MOSIN_SAWNBARREL",
    shortModel = M .. "MOSIN_OBREZ",
    stockOffcut = M .. "MOSIN_StockOffcut",
    barrelCutOffcuts = { M .. "MOSIN_BarrelOffcut", M .. "MOSIN_ForendOffcut" },
}

-- GoM's full-length barrels, which its barrel recipe saws: full type -> our offcuts of them
SawnStock.FULL_BARRELS = {}
for _, entry in pairs(SawnStock.GUNS) do
    if entry.barrelOffcuts then
        SawnStock.FULL_BARRELS["MarzGuns." .. entry.gun .. "_Barrel_Close"] = entry.barrelOffcuts
        SawnStock.FULL_BARRELS["MarzGuns." .. entry.gun .. "_Barrel_Open"] = entry.barrelOffcuts
    end
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

--- The barrel sawn off: the Mosin's sawn-off barrel part, or GoM's sawn-off barrels on a shotgun.
function SawnStock.IsBarrelSawn(weapon)
    local entry = SawnStock.Entry(weapon)
    if not entry then return false end
    if entry.sawnBarrel then
        local part = weapon:getWeaponPart(SawnStock.BARREL_PART_TYPE)
        return part ~= nil and part:getFullType() == entry.sawnBarrel
    end
    local barrel = weapon:getWeaponPart("Barrel")
    local barrelType = barrel and barrel:getFullType()
    return barrelType == entry.shortBarrels[1] or barrelType == entry.shortBarrels[2]
end

--- Sawn-off stock and sawn-off barrel(s) (or, on a shotgun, none fitted): short enough for a holster.
function SawnStock.FitsHolster(weapon)
    if not SawnStock.IsSawn(weapon) then return false end
    local entry = SawnStock.GUNS[weapon:getFullType()]
    if not entry.sawnBarrel and not weapon:getWeaponPart("Barrel") then return true end
    return SawnStock.IsBarrelSawn(weapon)
end

-------------------------------------------------
-- Model, handling, shell holder, spawn
-------------------------------------------------
for gun, entry in pairs(SawnStock.GUNS) do
    local rules
    if entry.sawnBarrel then
        rules = {
            { parts = { [SawnStock.PART_TYPE] = entry.sawn, [SawnStock.BARREL_PART_TYPE] = entry.sawnBarrel },
              model = entry.shortModel },
            { parts = { [SawnStock.PART_TYPE] = entry.sawn }, model = entry.model },
            { parts = { [SawnStock.BARREL_PART_TYPE] = entry.sawnBarrel }, model = entry.barrelModel },
        }
    else
        rules = {
            { parts = { [SawnStock.PART_TYPE] = entry.sawn, Barrel = entry.shortBarrels }, model = entry.shortModel },
            { parts = { [SawnStock.PART_TYPE] = entry.sawn }, model = entry.model },
        }
    end
    ConditionalModel.Register(gun, { rules = rules })
end

SawnStock.HANDLING = {
    StatsFactory.Multiply("AimingTime", 0.75),
    StatsFactory.Multiply("HitChance", 0.87),
    StatsFactory.Multiply("RecoilDelay", 1.3),
}

--- Vanilla's sawn-off shotgun flash, unless something before (a suppressor) changed the gun's own.
--- HandWeapon:setMuzzleFlashModelKey takes a Java ModelKey, not its name: a string threw here (3.5.0 - 3.6.0), which
--- broke every ReapplyAllModifiers of a gun with its barrel sawn off, the barrel cut's own included (OnCreate had
--- already handed over the offcuts and swapped the part on the server, then threw before sending the gun back, so
--- the owner's Mosin kept its barrel). The key is taken from the vanilla item that uses it.
local SAWN_FLASH_ITEM = "Base.DoubleBarrelShotgunSawnoff"
local sawnFlashKey
local function bigFlash(weapon, base)
    if not sawnFlashKey then
        local script = ScriptManager.instance:getItem(SAWN_FLASH_ITEM)
        sawnFlashKey = script and script:getMuzzleFlashModelKey()
        if not sawnFlashKey then return end
    end
    if weapon:getMuzzleFlashModelKey() == base:getMuzzleFlashModelKey() then
        weapon:setMuzzleFlashModelKey(sawnFlashKey)
    end
end

-- The Mosin's barrel cut, before the stock's handling (multipliers on GoM's 60 / 70 / 18 / 60 / 1.9-2.2).
SawnStock.BARREL_HANDLING = {
    StatsFactory.Multiply("MinDamage", 0.85),
    StatsFactory.Multiply("MaxDamage", 0.85),
    StatsFactory.Multiply("HitChance", 50 / 60),
    StatsFactory.Multiply("AimingTime", 45 / 70),
    StatsFactory.Multiply("RecoilDelay", 1.2),
    StatsFactory.Multiply("MaxRange", 0.5),
    StatsFactory.Multiply("SoundRadius", 1.35),
    StatsFactory.Multiply("SoundVolume", 1.35),
    bigFlash,
}
SawnStock.BARREL_SIGHTS = { StatsFactory.Set("MinSightRange", 4), StatsFactory.Set("MaxSightRange", 12) }
SawnStock.OBREZ_SIGHTS = { StatsFactory.Set("MinSightRange", 2), StatsFactory.Set("MaxSightRange", 9) }

local function append(list, mods)
    for _, mod in ipairs(mods) do list[#list + 1] = mod end
end

local function handling(weapon)
    local stock, barrel = SawnStock.IsSawn(weapon), SawnStock.Entry(weapon).sawnBarrel and SawnStock.IsBarrelSawn(weapon)
    if not stock and not barrel then return nil end
    local mods = {}
    if barrel then
        append(mods, SawnStock.BARREL_HANDLING)
        append(mods, stock and SawnStock.OBREZ_SIGHTS or SawnStock.BARREL_SIGHTS)
    end
    if stock then append(mods, SawnStock.HANDLING) end
    return mods
end

local layerRegistered = false
for _, layer in ipairs(StatsFactory.ModifierLayers or {}) do
    if layer.id == "GunsOfTien_SawnStock" then layerRegistered = true end
end
if not layerRegistered then
    StatsFactory.RegisterModifierLayer("GunsOfTien_SawnStock",
        handling,
        { AimingTime = true, HitChance = true, RecoilDelay = true, MinDamage = true, MaxDamage = true,
          MaxRange = true, MinSightRange = true, MaxSightRange = true, SoundRadius = true, SoundVolume = true,
          MuzzleFlashModelKey = true },
        function(weapon)
            return SawnStock.Entry(weapon) ~= nil
        end)
end

-------------------------------------------------
-- Names
-------------------------------------------------

--- "SawnBarrel", "SawnStock", "SawnBoth" or nil.
function SawnStock.State(weapon)
    local stock, barrel = SawnStock.IsSawn(weapon), SawnStock.IsBarrelSawn(weapon)
    return stock and barrel and "SawnBoth" or barrel and "SawnBarrel" or stock and "SawnStock" or nil
end

-- IG_UI.json's names, for a machine without the mod's translations (a dedicated server); keep the two in step
SawnStock.ENGLISH = {
    IGUI_GunsOfTien_DOUBLEBARREL_SawnBarrel = "Sawn-Off Double Barrel Shotgun",
    IGUI_GunsOfTien_DOUBLEBARREL_SawnStock = "Double Barrel Shotgun (Sawn-Off Stock)",
    IGUI_GunsOfTien_DOUBLEBARREL_SawnBoth = "Sawn-Off Double Barrel Pistol",
    IGUI_GunsOfTien_STEVENS_555_SawnBarrel = "Sawn-Off Stevens 555 Shotgun",
    IGUI_GunsOfTien_STEVENS_555_SawnStock = "Stevens 555 Double Barrel Shotgun (Sawn-Off Stock)",
    IGUI_GunsOfTien_STEVENS_555_SawnBoth = "Sawn-Off Stevens 555 Pistol",
    IGUI_GunsOfTien_TOZ34_SawnBarrel = "Sawn-Off TOZ-34 Shotgun",
    IGUI_GunsOfTien_TOZ34_SawnStock = "TOZ-34 Double Barrel Shotgun (Sawn-Off Stock)",
    IGUI_GunsOfTien_TOZ34_SawnBoth = "Sawn-Off TOZ-34 Pistol",
    IGUI_GunsOfTien_MOSIN_SawnBarrel = "Mosin-Nagant Bolt Rifle (Sawn-Off Barrel)",
    IGUI_GunsOfTien_MOSIN_SawnStock = "Mosin-Nagant Bolt Rifle (Sawn-Off Stock)",
    IGUI_GunsOfTien_MOSIN_SawnBoth = "Mosin-Nagant Obrez",
}

--- The gun's name for its cuts, in this machine's language (English where the mod's translations are missing); the
--- script's name when nothing is sawn off.
function SawnStock.NameFor(weapon)
    local entry = SawnStock.Entry(weapon)
    if not entry then return nil end
    local state = SawnStock.State(weapon)
    if not state then return weapon:getScriptItem():getDisplayName() end
    local key = "IGUI_GunsOfTien_" .. entry.gun .. "_" .. state
    return getTextOrNull(key) or SawnStock.ENGLISH[key] or key
end

--- Fit the full integrated stock / barrel to a gun found before they existed (GoM's spawn table only gives them to
--- guns made since), so the gun tooltip lists them ("Barrel (Integrated): Full Barrel"). They change no stat and no
--- model; doChange false skips the part's stat sums and OnAttach.
local function fitMissingParts(weapon, entry)
    if entry.stock and not weapon:getWeaponPart(SawnStock.PART_TYPE) then
        local part = instanceItem(entry.stock)
        if part then weapon:attachWeaponPart(part, false) end
    end
    if entry.barrel and not weapon:getWeaponPart(SawnStock.BARREL_PART_TYPE) then
        local part = instanceItem(entry.barrel)
        if part then weapon:attachWeaponPart(part, false) end
    end
end

--- Name and inventory icon for the gun's cuts, and its integrated parts if it lacks them. The icon goes in modData
--- customInventoryIcon, which InventoryItem.getTexture reads (Texture.getSharedTexture of it) before the item's own
--- texture; modData is saved and travels with the item, so a gun the server sawed shows it on every client, in any
--- container.
function SawnStock.ApplyLook(weapon)
    local entry = SawnStock.Entry(weapon)
    if not entry then return end
    fitMissingParts(weapon, entry)
    local state = SawnStock.State(weapon)
    local icon = state and ("media/textures/item_GunsOfTien_" .. entry.gun .. "_" .. state .. ".png") or nil
    if icon or weapon:hasModData() then
        local modData = weapon:getModData()
        if modData.customInventoryIcon ~= icon then modData.customInventoryIcon = icon end
    end
    if weapon:isCustomName() then return end
    local name = SawnStock.NameFor(weapon)
    if name and weapon:getDisplayName() ~= name then weapon:setName(name) end
end

if StatsFactory.RegisterRestoreHandler then      -- replaces its own entry on a Lua reload
    StatsFactory.RegisterRestoreHandler("GunsOfTien_SawnStock", SawnStock.ApplyLook)
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
    for _, barrel in ipairs(entry.shortBarrels or {}) do
        if not CustomStatsAttachments.RegisteredParts[barrel] then
            CustomStatsAttachments.RegisterPart(barrel, sawnBarrelStats)
        end
    end
end

local sawnParts = {}
for _, entry in pairs(SawnStock.GUNS) do
    if not entry.sawnBarrel then sawnParts[#sawnParts + 1] = entry.sawn end
end
UpgradeExclusives.SetExclusives("MarzGuns.Shellholder", sawnParts)

-- GoM's bayonets for rifles (Bayonets.lua lists the Mosin), all PartType BayonetKnife
SawnStock.BAYONETS = { "MarzGuns.K98_Bayonet_Attachment", "MarzGuns.M5_Bayonet_Attachment",
    "MarzGuns.M9_Bayonet_Attachment", "MarzGuns.M1905_Bayonet_Attachment", "MarzGuns.M1_Bayonet_Attachment" }
for _, bayonet in ipairs(SawnStock.BAYONETS) do
    UpgradeExclusives.SetExclusives(bayonet, SawnStock.GUNS["MarzGuns.MOSIN"].sawnBarrel)
end

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
            if entry.barrel then
                present = false
                for _, part in ipairs(t.required) do
                    if part == entry.barrel then present = true end
                end
                if not present then table.insert(t.required, entry.barrel) end
            end
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

--- Take a fitted part off into the character's inventory.
local function detachTo(weapon, character, partType)
    local part = weapon:getWeaponPart(partType)
    if not part then return end
    weapon:detachWeaponPart(part)
    local inventory = character:getInventory()
    local added = inventory:AddItem(part)
    if added and isServer() then sendAddItemToContainer(inventory, added) end
end

--- Re-apply model, stats and name, and send the gun back (server) or redraw it (single player).
local function finish(weapon, character)
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

local function handOver(character, fullType)
    local offcut = instanceItem(fullType)
    if offcut then Actions.addOrDropItem(character, offcut) end      -- dropped at the feet when too heavy, and sent
end

--- Server / single player: saw the stock off, give back a shell holder and the stock offcut, re-apply model and
--- stats, send it back.
function SawnStock.Saw(weapon, character)
    local entry = SawnStock.Entry(weapon)
    if not entry or SawnStock.IsSawn(weapon) then return end
    detachTo(weapon, character, "Shellholder")
    handOver(character, entry.stockOffcut)
    FoldingStock.SwapStockAttachment(weapon, SawnStock.PART_TYPE, entry.sawn)
    finish(weapon, character)
end

--- Server / single player: saw the Mosin's barrel and forend off, give back a bayonet and the two offcuts.
function SawnStock.SawBarrel(weapon, character)
    local entry = SawnStock.Entry(weapon)
    if not entry or not entry.sawnBarrel or SawnStock.IsBarrelSawn(weapon) then return end
    detachTo(weapon, character, "BayonetKnife")
    for _, offcut in ipairs(entry.barrelCutOffcuts) do handOver(character, offcut) end
    FoldingStock.SwapStockAttachment(weapon, SawnStock.BARREL_PART_TYPE, entry.sawnBarrel)
    finish(weapon, character)
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

--- The rifle barrel recipe: a gun only while its barrel is whole.
function GunsOfTien_SawnStock.OnTestBarrel(item, character)
    if SawnStock.Entry(item) then
        return not SawnStock.IsBarrelSawn(item)
    end
    return true
end

function GunsOfTien_SawnStock.OnCreateBarrel(craftRecipeData, character)
    local kept = craftRecipeData:getAllKeepInputItems()
    for i = 0, kept:size() - 1 do
        local item = kept:get(i)
        local entry = SawnStock.Entry(item)
        if entry and entry.sawnBarrel and not SawnStock.IsBarrelSawn(item) then
            SawnStock.SawBarrel(item, character)
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
-- The wrapper must name every one of vanilla's parameters: the server rebuilds the action by calling new with the
-- client table's values of new's parameter names (NetTimedAction.set reads the prototype's locvars), so a `...`
-- arrives empty, containers is nil and serverStart's setContainers throws for every handcraft (2026-10-19).
local BARREL_RECIPE = "SawnOffShotgunBarrels"
local BARREL_ACTION = "GunsOfTien_SawOffShotgunBarrels"
if ISHandcraftAction and not ISHandcraftAction.GunsOfTien_new then
    ISHandcraftAction.GunsOfTien_new = ISHandcraftAction.new
    ISHandcraftAction.new = function(self, character, craftRecipe, containers, isoObject, craftBench, manualInputs,
                                     items, recipeItem, variableInputRatio, eatPercentage)
        local o = ISHandcraftAction.GunsOfTien_new(self, character, craftRecipe, containers, isoObject, craftBench,
            manualInputs, items, recipeItem, variableInputRatio, eatPercentage)
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
    local waiting = {}      -- { weapon, player, sprite, until } re-applied once the sawn-off part has arrived, i.e.
                            -- once the client's parts give the model the server sent (a Mosin may have one cut already)

    Events.OnServerCommand.Add(function(module, command, args)
        if module ~= SawnStock.MODULE or command ~= SawnStock.COMMAND or type(args) ~= "table" then return end
        for i = 0, getNumActivePlayers() - 1 do
            local player = getSpecificPlayer(i)
            local weapon = player and player:getInventory():getItemWithIDRecursiv(args.id)
            if weapon and SawnStock.Entry(weapon) then
                if args.sprite then weapon:setWeaponSprite(args.sprite) end
                player:resetEquippedHandsModels()
                waiting[#waiting + 1] = { weapon = weapon, player = player, sprite = args.sprite,
                                          untilMs = getTimestampMs() + 10000 }
            end
        end
    end)

    Events.OnTick.Add(function()
        if #waiting == 0 then return end
        local now = getTimestampMs()
        for i = #waiting, 1, -1 do
            local w = waiting[i]
            if ConditionalModel.ResolveModel(w.weapon) == w.sprite then
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
