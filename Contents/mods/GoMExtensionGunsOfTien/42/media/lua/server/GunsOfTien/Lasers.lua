--[[
    Guns of Tien -- laser batteries drain on the server (shared/GunsOfTien/Lasers.lua has the design).

    Every 10 game minutes each player's gun in hand with its laser switched on loses one charge (WeaponPart.update's
    rate for an activated part; the part is never activated, so the engine does not drain it too). At 0 the laser
    switches off and its bonus goes. The gun goes back to its owner with syncHandWeaponFields (fitted parts with their
    charge, and the modData), and the lit state is broadcast again, which also tells players who joined since.
    A gun put away keeps its switch but neither drains nor shows a dot.
--]]

if isClient() then return end

local Lasers = require("GunsOfTien/Lasers")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")

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

local function drain()
    for _, player in ipairs(players()) do
        local weapon = player:getPrimaryHandItem()
        if not player:isDead() and Lasers.IsSwitchedOn(weapon) then
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
                weapon:getModData()[Lasers.KEY] = nil          -- the laser was taken off
            end
            if isServer() then
                syncHandWeaponFields(player, weapon)
            end
            Lasers.Broadcast(player, Lasers.IsLit(weapon))
        end
    end
end

Events.EveryTenMinutes.Add(drain)
