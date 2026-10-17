--[[
    Guns of Tien -- Guns of Marz's lasers run on a battery and are switched on and off (user, 2026-10-18: "the laser
    attachments don't really emit lasers... put a battery in there to turn it on").

    GoM's five lasers (AimRight, LRX-7 for rifles; PJ-3, PX1, TR-1 for pistols) were plain parts whose aiming bonus
    always applied and that showed nothing. Now:
    - Battery: their item scripts get GoM's lights' tags (base:flashlight;base:usesbattery) and a UseDelta, so vanilla's
      Insert / Remove Battery recipes work on a laser taken off the gun, exactly as on GoM's weapon lights (42.21
      RecipeCodeOnCreate.torchBatteryInsert handles a WeaponPart), and the gun tooltip shows the laser's "Remaining"
      bar (WeaponPart.DoBatteryTooltip). UseDelta 0.00033 = 3030 charges, one per 10 game minutes switched on: about 3
      weeks (user: 3x a weapon light; GoM's lights are 0.001, about a week).
    - On / off: the gun's modData (KEY), switched by ISToggleLaserGoT, whose complete() runs on the server (single
      player: locally) and sends the gun back with Gunworks' CallSyncHandWeaponFields (SyncHandWeaponFieldsPacket
      carries every fitted part's bytes, charge included, and the modData, server -> owner only). The part itself is
      never activated: WeaponPart.update would drain it on whichever side updates the gun, so the server drains
      it instead (server/GunsOfTien/Lasers.lua).
    - Stats: GoM's laser stats (Gunworks CustomStatsAttachments) are wrapped to apply only while the laser is lit
      (switched on with charge left); Gunworks re-applies stats on every equip, the toggle and the drain re-apply them.
    - Look: a red dot where the gun points while aiming, with a faint beam (client/GunsOfTien/LaserDraw.lua).
--]]

require("TimedActions/ISBaseTimedAction")

local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Animations = require("WeaponSystems/Utils/Animations")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
pcall(require, "MarzWeapons/Registries/AttachmentCustomStats")

local Lasers = {}

Lasers.TYPES = {
    ["MarzGuns.AimRight_Laser"] = true,
    ["MarzGuns.LRX-7_Laser"] = true,
    ["MarzGuns.PJ-3_Laser"] = true,
    ["MarzGuns.PX1_Laser"] = true,
    ["MarzGuns.TR-1_Laser"] = true,
}
Lasers.USE_DELTA = 0.00033
Lasers.KEY = "GunsOfTien_LaserOn"
Lasers.MODULE = "GunsOfTien"
Lasers.CMD = "laser"

--- The laser fitted to a gun, or nil.
function Lasers.GetLaser(weapon)
    if not weapon or not instanceof(weapon, "HandWeapon") then return nil end
    local parts = weapon:getAllWeaponParts()
    if not parts then return nil end
    for i = 0, parts:size() - 1 do
        local part = parts:get(i)
        if part and Lasers.TYPES[part:getFullType()] then
            return part
        end
    end
    return nil
end

function Lasers.IsSwitchedOn(weapon)
    return weapon ~= nil and weapon:hasModData() and weapon:getModData()[Lasers.KEY] == true
end

--- Switched on, fitted and with charge left: the dot shows and the bonus applies.
function Lasers.IsLit(weapon)
    if not Lasers.IsSwitchedOn(weapon) then return false end
    local part = Lasers.GetLaser(weapon)
    return part ~= nil and part:getCurrentUses() > 0
end

--- A laser made before it ran on a battery holds the default single charge: give it a full battery once. One whose
--- battery was inserted or used since keeps its charge (it is no longer at 1, or carries the mark).
function Lasers.InitCharge(part)
    if not part then return end
    local md = part:getModData()
    if md.GunsOfTien_LaserCharged then return end
    md.GunsOfTien_LaserCharged = true
    if part:getCurrentUses() <= 1 then
        part:setCurrentUsesFloat(1.0)
    end
end

--- Server / single player: switch a gun's laser and re-apply its stats. Returns the new lit state.
function Lasers.SetSwitchedOn(weapon, on)
    local part = Lasers.GetLaser(weapon)
    if not part then return false end
    Lasers.InitCharge(part)
    weapon:getModData()[Lasers.KEY] = on and part:getCurrentUses() > 0 or nil
    StatsFactory.ReapplyAllModifiers(weapon)
    return Lasers.IsLit(weapon)
end

--- Server: tell every client whether this player's laser is lit (they draw other players' dots from it).
function Lasers.Broadcast(player, lit)
    if isServer() and player then
        sendServerCommand(Lasers.MODULE, Lasers.CMD, { id = player:getOnlineID(), on = lit == true })
    end
end

-------------------------------------------------
-- Item scripts: battery like GoM's weapon lights, 3x their life
-------------------------------------------------
local function patchScripts()
    for fullType in pairs(Lasers.TYPES) do
        local script = ScriptManager.instance:getItem(fullType)
        if script then
            script:DoParam("UseDelta = " .. tostring(Lasers.USE_DELTA))
            script:DoParam("Tags = base:flashlight;base:usesbattery")
        end
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)

-------------------------------------------------
-- Stats: GoM's laser modifiers apply only while lit
-------------------------------------------------
for fullType in pairs(Lasers.TYPES) do
    local entry = CSA.RegisteredParts[fullType]
    if entry and entry.modifiers and not entry.GunsOfTienLaser then
        local wrapped = {}
        for i, modifier in ipairs(entry.modifiers) do
            wrapped[i] = function(weapon, base)
                if Lasers.IsLit(weapon) then
                    return modifier(weapon, base)
                end
            end
        end
        entry.modifiers = wrapped
        entry.GunsOfTienLaser = true
    end
end

-------------------------------------------------
-- Timed action: switch the laser (as Gunworks' ISFoldStock)
-------------------------------------------------
ISToggleLaserGoT = ISBaseTimedAction:derive("ISToggleLaserGoT")

function ISToggleLaserGoT:isValid()
    if isClient() and self.weapon then
        return self.character:getInventory():containsID(self.weapon:getID())
    end
    return self.character:getPrimaryHandItem() == self.weapon
end

function ISToggleLaserGoT:start()
    if isClient() and self.weapon then
        self.weapon = self.character:getInventory():getItemById(self.weapon:getID())
    end
    self:setActionAnim(self.animation)
end

function ISToggleLaserGoT:update()
end

function ISToggleLaserGoT:perform()
    self.character:playSound(Lasers.IsSwitchedOn(self.weapon) and "FlashlightOff" or "FlashlightOn")
    ISBaseTimedAction.perform(self)
end

function ISToggleLaserGoT:complete()
    local lit = Lasers.SetSwitchedOn(self.weapon, not Lasers.IsSwitchedOn(self.weapon))
    Animations.CallSyncHandWeaponFields(self.character, self.weapon)
    Lasers.Broadcast(self.character, lit)
    return true
end

function ISToggleLaserGoT:stop()
    ISBaseTimedAction.stop(self)
end

function ISToggleLaserGoT:new(character, weapon, anim)
    local o = ISBaseTimedAction.new(self, character)
    o.stopOnWalk = false
    o.stopOnRun = true
    o.maxTime = 10
    o.weapon = weapon
    o.animation = anim
    o.useProgressBar = false
    return o
end

--- From a menu: equip the gun first if needed, then switch.
function Lasers.Queue(player, weapon)
    if not player or not weapon then return end
    if player:getPrimaryHandItem() ~= weapon then
        ISTimedActionQueue.add(ISEquipWeaponAction:new(player, weapon, 50, true, weapon:isTwoHandWeapon()))
    end
    if weapon:getContainer() == player:getInventory() then
        ISTimedActionQueue.add(ISToggleLaserGoT:new(player, weapon, CharacterActionAnims.Craft))
    end
end

GunsOfTien_Lasers = Lasers
return Lasers
