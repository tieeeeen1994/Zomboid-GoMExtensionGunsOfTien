--[[
    Guns of Tien - Post-93 -- the MP7A1's integral folding front grip.

    The real MP7A1 has a vertical front grip that folds up under the receiver. It is two hidden parts of part type
    ForegripIntegrated, swapped like GoM's integrated stocks: MP7A1_Integrated_Foregrip_Folded (drawn at the gun's
    origin, the mesh is modelled folded) and ..._Deployed (drawn at the model's foregrip_deployed point, turned 90
    degrees down about the hinge pin). The fitted part is the state, so there is nothing else to save or restore; its
    stats come from Gunworks' CustomStatsAttachments layer (Guns.lua: GoM's Stub Foregrip numbers on the deployed
    part), applied again by StatsFactory.ReapplyAllModifiers after each swap and by Gunworks on every equip.

    Gunworks' FoldingStock cannot be used a second time for the same gun: it keeps one entry per gun type and the
    state in modData.StockFolded. Its SwapStockAttachment is a plain part swap by part type and is reused here.

    ISFoldForegripGoT mirrors Gunworks' ISFoldStock: the swap is done in complete() (the server in multiplayer, the
    player's game in single player) and sent back with Gunworks' CallSyncHandWeaponFields. A gun found without
    either part (spawned before the grip existed) counts as folded; unfolding fits the deployed part.
--]]

require("TimedActions/ISBaseTimedAction")

local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Animations = require("WeaponSystems/Utils/Animations")

local M = "GunsOfTienPost93."

local Foregrip = {}

Foregrip.PART_TYPE = "ForegripIntegrated"
Foregrip.GUNS = {
    [M .. "MP7A1"] = { folded = M .. "MP7A1_Integrated_Foregrip_Folded", deployed = M .. "MP7A1_Integrated_Foregrip_Deployed" },
}

function Foregrip.Has(weapon)
    return weapon ~= nil and instanceof(weapon, "HandWeapon") and Foregrip.GUNS[weapon:getFullType()] ~= nil
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
