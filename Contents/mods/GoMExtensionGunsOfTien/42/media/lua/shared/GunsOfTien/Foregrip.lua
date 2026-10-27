--[[
    Guns of Tien -- integral folding front grips (the main mod's Steyr AUG A1, Post-93's MP7A1).

    A gun's folding grip is two hidden parts of part type ForegripIntegrated, swapped like GoM's integrated stocks: the
    folded one and the deployed one, each drawn through the gun's own ModelWeaponPart line at its point. The fitted
    part is the state, so there is nothing else to save or restore; its stats come from Gunworks'
    CustomStatsAttachments layer (registered beside each gun: GoM's Stub Foregrip numbers on the deployed part),
    applied again by StatsFactory.ReapplyAllModifiers after each swap and by Gunworks on every equip.

    Gunworks' FoldingStock cannot be used a second time for the same gun: it keeps one entry per gun type and the
    state in modData.StockFolded. Its SwapStockAttachment is a plain part swap by part type and is reused here.

    ISFoldForegripGoT mirrors Gunworks' ISFoldStock: the swap is done in complete() (the server in multiplayer, the
    player's game in single player) and sent back with Gunworks' CallSyncHandWeaponFields. A gun found without
    either part (spawned before the grip existed) counts as folded; unfolding fits the deployed part.

    Moved here from Post-93 (2026-10-27) when the AUG A1 got the same fold: Post-93 requires this mod and registers
    its MP7A1 with Foregrip.Register, so one timed action and one menu (client/GunsOfTien/ForegripMenu.lua) serve
    every gun. Each entry names its own menu descriptions (the AUG's grip folds forward under the barrel, the MP7's up
    under the receiver).
--]]

require("TimedActions/ISBaseTimedAction")

local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Animations = require("WeaponSystems/Utils/Animations")

local Foregrip = GunsOfTien_Foregrip or {}
GunsOfTien_Foregrip = Foregrip

Foregrip.PART_TYPE = "ForegripIntegrated"
Foregrip.GUNS = Foregrip.GUNS or {}

--- gun full type -> { folded = part, deployed = part, foldDesc = text key, unfoldDesc = text key }
function Foregrip.Register(gun, entry)
    Foregrip.GUNS[gun] = entry
end

function Foregrip.Has(weapon)
    return weapon ~= nil and instanceof(weapon, "HandWeapon") and Foregrip.GUNS[weapon:getFullType()] ~= nil
end

function Foregrip.Entry(weapon)
    return Foregrip.Has(weapon) and Foregrip.GUNS[weapon:getFullType()] or nil
end

function Foregrip.IsDeployed(weapon)
    if not Foregrip.Has(weapon) then return false end
    local part = weapon:getWeaponPart(Foregrip.PART_TYPE)
    return part ~= nil and part:getFullType() == Foregrip.GUNS[weapon:getFullType()].deployed
end

function Foregrip.SetDeployed(weapon, deployed)
    if not Foregrip.Has(weapon) then return end
    local entry = Foregrip.GUNS[weapon:getFullType()]
    FoldingStock.SwapStockAttachment(weapon, Foregrip.PART_TYPE, deployed and entry.deployed or entry.folded)
    StatsFactory.ReapplyAllModifiers(weapon)
end

function Foregrip.Toggle(weapon)
    Foregrip.SetDeployed(weapon, not Foregrip.IsDeployed(weapon))
end

-------------------------------------------------
-- Timed action (as Gunworks' ISFoldStock)
-------------------------------------------------
ISFoldForegripGoT = ISBaseTimedAction:derive("ISFoldForegripGoT")

function ISFoldForegripGoT:isValid()
    if isClient() and self.weapon then
        return self.character:getInventory():containsID(self.weapon:getID())
    end
    return self.character:getPrimaryHandItem() == self.weapon
end

function ISFoldForegripGoT:start()
    if isClient() and self.weapon then
        self.weapon = self.character:getInventory():getItemById(self.weapon:getID())
    end
    Animations.CallSyncHandWeaponFields(self.character, self.weapon)
    self:setActionAnim(self.animation)
end

function ISFoldForegripGoT:update()
end

function ISFoldForegripGoT:perform()
    ISBaseTimedAction.perform(self)
end

function ISFoldForegripGoT:complete()
    Foregrip.Toggle(self.weapon)
    Animations.CallSyncHandWeaponFields(self.character, self.weapon)
    return true
end

function ISFoldForegripGoT:stop()
    ISBaseTimedAction.stop(self)
end

function ISFoldForegripGoT:new(character, weapon, anim)
    local o = ISBaseTimedAction.new(self, character)
    o.stopOnWalk = false
    o.stopOnRun = true
    o.maxTime = 30
    o.weapon = weapon
    o.animation = anim
    o.useProgressBar = false
    return o
end

--- Queue it from a menu: equip the gun first if it is not in the primary hand (Gunworks' FoldStockContext).
function Foregrip.Queue(player, weapon)
    if not player or not weapon then return end
    if player:getPrimaryHandItem() ~= weapon then
        ISTimedActionQueue.add(ISEquipWeaponAction:new(player, weapon, 50, true, weapon:isTwoHandWeapon()))
    end
    if weapon:getContainer() == player:getInventory() then
        ISTimedActionQueue.add(ISFoldForegripGoT:new(player, weapon, CharacterActionAnims.Craft))
    end
end

return Foregrip
