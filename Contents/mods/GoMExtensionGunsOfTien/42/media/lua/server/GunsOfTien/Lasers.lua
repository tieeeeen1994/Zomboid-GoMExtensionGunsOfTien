--[[
    Guns of Tien -- laser batteries drain on the server (shared/GunsOfTien/Lasers.lua has the design).

    Every 10 game minutes each gun a player carries (in hand, on the back, in a bag) with its laser switched on loses
    one charge (WeaponPart.update's rate for an activated part; the part is never activated, so the engine does not
    drain it too): the beam is part of the gun's model and shows wherever the gun is drawn, so it drains wherever it
    is. At 0 the laser switches off, its beam part comes off and its bonus goes. The gun goes back to its owner with
    its parts' charge and modData (syncHandWeaponFields); a gun in hand whose beam came on or off is re-equipped
    instead (CallSyncHandWeaponFields), which shows the change to every other player too.
    Every game minute those guns are also checked for a beam that no longer matches (a laser taken off, or switched
    off elsewhere), so a beam never stays on a gun without its lit laser.
    Every game minute each laser a player carries that never had its battery (a part starts at one charge: an empty
    Remaining bar) gets a full one (Lasers.InitCharge) and goes back to the owner (syncItemFields carries the uses).
--]]

if isClient() then return end

local Lasers = require("GunsOfTien/Lasers")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")
local Animations = require("WeaponSystems/Utils/Animations")

local function players()
    local list = {}
    local online = getOnlinePlayers()
    if online and online:size() > 0 then
        for i = 0, online:size() - 1 do
            list[#list + 1] = online:get(i)
        end
    else
        for i = 0, getNumActivePlayers() - 1 do
            local p = getSpecificPlayer(i)
            if p then list[#list + 1] = p end
        end
    end
    return list
end

--- Send the gun back: re-equipped when its beam changed and it is in hand (everyone sees it), else its fields to the
--- owner (parts with their charge, modData).
local function send(player, weapon, beamChanged)
    if beamChanged and player:getPrimaryHandItem() == weapon then
        Animations.CallSyncHandWeaponFields(player, weapon)
    elseif isServer() then
        syncHandWeaponFields(player, weapon)
    end
end

--- Every gun the player carries (hands, back slot, bags) that is switched on or still carries a beam: the beam is part
--- of the gun's model, so it shows wherever the gun is drawn, and a lit laser drains wherever it is.
local function laserGuns(player)
    local found = player:getInventory():getAllEvalRecurse(function(item)
        return instanceof(item, "HandWeapon")
            and (Lasers.IsSwitchedOn(item) or item:getWeaponPart(Lasers.BEAM_PART_TYPE) ~= nil)
    end, ArrayList.new())
    local list = {}
    for i = 0, found:size() - 1 do
        list[#list + 1] = found:get(i)
    end
    return list
end

local function drain()
    for _, player in ipairs(players()) do
        if not player:isDead() then
            for _, weapon in ipairs(laserGuns(player)) do
                if Lasers.IsSwitchedOn(weapon) then
                    local part = Lasers.GetLaser(weapon)
                    if part then
                        Lasers.InitCharge(part)
                        local uses = part:getCurrentUses()
                        if uses > 0 then
                            part:setCurrentUses(uses - 1)
                        end
                        if part:getCurrentUses() <= 0 then
                            weapon:getModData()[Lasers.KEY] = nil
                            StatsFactory.ReapplyAllModifiers(weapon)
                        end
                    else
                        weapon:getModData()[Lasers.KEY] = nil      -- the laser was taken off
                    end
                    send(player, weapon, Lasers.UpdateBeam(weapon))
                end
            end
        end
    end
end

local function checkBeams()
    for _, player in ipairs(players()) do
        if not player:isDead() then
            for _, weapon in ipairs(laserGuns(player)) do
                if Lasers.IsSwitchedOn(weapon) and not Lasers.GetLaser(weapon) then
                    weapon:getModData()[Lasers.KEY] = nil
                end
                if Lasers.UpdateBeam(weapon) then
                    send(player, weapon, true)
                end
            end
        end
    end
end

local function uncharged(part)
    return part ~= nil and not (part:hasModData() and part:getModData().GunsOfTien_LaserCharged)
end

--- Lasers come with a battery: a laser part starts with one charge (an empty Remaining bar) and only switching it on
--- used to fill it, so each laser a player carries that never had its battery (loose, in a bag or on a gun) gets it
--- here, and goes back to the owner.
local function chargeNew()
    for _, player in ipairs(players()) do
        if not player:isDead() then
            local found = player:getInventory():getAllEvalRecurse(function(item)
                if Lasers.TYPES[item:getFullType()] then return uncharged(item) end
                return instanceof(item, "HandWeapon") and uncharged(Lasers.GetLaser(item))
            end, ArrayList.new())
            for i = 0, found:size() - 1 do
                local item = found:get(i)
                if instanceof(item, "HandWeapon") then
                    Lasers.InitCharge(Lasers.GetLaser(item))
                    send(player, item, false)
                else
                    Lasers.InitCharge(item)
                    if isServer() then item:syncItemFields() end
                end
            end
        end
    end
end

Events.EveryTenMinutes.Add(drain)
Events.EveryOneMinute.Add(checkBeams)
Events.EveryOneMinute.Add(chargeNew)
