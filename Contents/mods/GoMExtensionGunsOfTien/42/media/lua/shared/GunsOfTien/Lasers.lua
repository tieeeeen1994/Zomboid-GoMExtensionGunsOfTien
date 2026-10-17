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
    - Look (third version, user 2026-10-18: "the same length as the attachment itself", exact on the attachment): a
      short red beam drawn by the engine as part of the gun. While lit, the gun carries a hidden part
      (GunsOfTien.LaserBeam_<laser>, part type LaserBeam, items_lasers.txt) whose model (models_lasers.txt, mesh from
      scripts/make_laser_beam.py) the engine draws at the gun's mount point for that laser and moves to the laser's
      lens by its own attachment of the same name, so it follows the gun through every animation, on every gun, for
      every player (fitted parts reach other clients with the gun, CallSyncHandWeaponFields re-equips it). Each gun
      that takes a laser needs a ModelWeaponPart line for its beam: Item.DoParam("ModelWeaponPart = ...") appends one
      (42.21 Item.DoParam; it appends even when the part type is already listed, so each script is patched once). The
      first two versions drew a dot / a fading line over the screen (OnPreUIDraw) from estimated positions: Lua cannot
      read the muzzle (BallisticsController is not exposed), so they never sat on the attachment.
--]]

require("TimedActions/ISBaseTimedAction")

local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Animations = require("WeaponSystems/Utils/Animations")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
pcall(require, "MarzWeapons/Registries/AttachmentCustomStats")

local Lasers = {}

-- laser -> its beam part and the gun mount point GoM draws that laser at (its ModelWeaponPart lines)
Lasers.TYPES = {
    ["MarzGuns.AimRight_Laser"] = { beam = "GunsOfTien.LaserBeam_AimRight_Laser", point = "laser_right" },
    ["MarzGuns.LRX-7_Laser"] = { beam = "GunsOfTien.LaserBeam_LRX7_Laser", point = "laser_right" },
    ["MarzGuns.PJ-3_Laser"] = { beam = "GunsOfTien.LaserBeam_PJ3_Laser", point = "underbarrel" },
    ["MarzGuns.PX1_Laser"] = { beam = "GunsOfTien.LaserBeam_PX1_Laser", point = "underbarrel" },
    ["MarzGuns.TR-1_Laser"] = { beam = "GunsOfTien.LaserBeam_TR1_Laser", point = "underbarrel" },
}
Lasers.BEAM_PART_TYPE = "LaserBeam"

-- the beam parts never show in the attachment menus (as the integrated rails)
local beams = {}
for _, entry in pairs(Lasers.TYPES) do beams[#beams + 1] = entry.beam end
PreventRemoval.Register(beams)
Lasers.USE_DELTA = 0.00033
Lasers.KEY = "GunsOfTien_LaserOn"

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

--- Switched on, fitted and with charge left: the beam shows and the bonus applies.
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

--- Server / single player: fit the beam part while the laser is lit, take it off otherwise (or when the laser is
--- gone). Returns true when the gun's parts changed.
function Lasers.UpdateBeam(weapon)
    if not weapon or not instanceof(weapon, "HandWeapon") then return false end
    local beam = weapon:getWeaponPart(Lasers.BEAM_PART_TYPE)
    local laser = Lasers.GetLaser(weapon)
    local want = laser and Lasers.IsLit(weapon) and Lasers.TYPES[laser:getFullType()].beam or nil
    if want and (not beam or beam:getFullType() ~= want) then
        FoldingStock.SwapStockAttachment(weapon, Lasers.BEAM_PART_TYPE, want)
        return true
    elseif not want and beam then
        weapon:detachWeaponPart(beam)
        return true
    end
    return false
end

--- Server / single player: switch a gun's laser, fit or remove its beam and re-apply its stats. Returns the new lit
--- state.
function Lasers.SetSwitchedOn(weapon, on)
    local part = Lasers.GetLaser(weapon)
    if not part then return false end
    Lasers.InitCharge(part)
    weapon:getModData()[Lasers.KEY] = on and part:getCurrentUses() > 0 or nil
    Lasers.UpdateBeam(weapon)
    StatsFactory.ReapplyAllModifiers(weapon)
    return Lasers.IsLit(weapon)
end

-------------------------------------------------
-- Item scripts: battery like GoM's weapon lights, 3x their life; each gun that takes a laser draws its beam
-------------------------------------------------
local patched = {}       -- gun script objects given their beam lines (scripts are new objects after a reload)

local function patchScripts()
    for fullType, entry in pairs(Lasers.TYPES) do
        local script = ScriptManager.instance:getItem(fullType)
        if script then
            script:DoParam("UseDelta = " .. tostring(Lasers.USE_DELTA))
            script:DoParam("Tags = base:flashlight;base:usesbattery")
            -- the guns this laser mounts on; Post-93's own guns list their beams in their item scripts
            local item = instanceItem(fullType)
            local guns = item and item.getMountOn and item:getMountOn()
            if guns then
                for i = 0, guns:size() - 1 do
                    local gunType = tostring(guns:get(i))
                    local gun = gunType:find("^GunsOfTienPost93%.") == nil and ScriptManager.instance:getItem(gunType)
                    if gun then
                        patched[gun] = patched[gun] or {}
                        if not patched[gun][entry.beam] then
                            patched[gun][entry.beam] = true
                            gun:DoParam("ModelWeaponPart = " .. entry.beam .. " " .. entry.beam .. " " .. entry.point
                                .. " " .. entry.point)
                        end
                    end
                end
            end
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
    Lasers.SetSwitchedOn(self.weapon, not Lasers.IsSwitchedOn(self.weapon))
    -- re-equips the gun: the owner gets its parts (beam, charge) and modData, everyone else the gun with its beam
    Animations.CallSyncHandWeaponFields(self.character, self.weapon)
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
