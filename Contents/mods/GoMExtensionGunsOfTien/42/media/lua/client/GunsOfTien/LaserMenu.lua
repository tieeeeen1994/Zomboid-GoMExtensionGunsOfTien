--[[
    Guns of Tien -- switching lasers from the menus, and what the client keeps about them
    (shared/GunsOfTien/Lasers.lua has the design).

    - "Turn Laser On / Off" in the gun's inventory context menu and in the firearm radial menu (Gunworks wraps
      ISFirearmRadialMenu.fillMenu; this mod loads after it). An empty battery greys the option out and says how to
      change it: take the laser off the gun and use vanilla's Insert Battery, as with GoM's weapon lights.
    - Other players' lasers: the server broadcasts { id = onlineID, on } when one switches and every 10 game minutes
      while lit; LaserDraw.lua reads Lasers.Remote.
    - Stats: SyncHandWeaponFieldsPacket sets the client's aiming time and hit chance from the server but not the
      critical chance, so the client re-applies Gunworks' stats itself whenever its gun's lit state changes.
    - The laser parts' tooltips say how they work now (GoM's tooltipsPergun lines, after its own).
--]]

require("ISUI/ISInventoryPaneContextMenu")
require("ISUI/ISFirearmRadialMenu")

local Lasers = require("GunsOfTien/Lasers")
local StatsFactory = require("WeaponSystems/Utils/StatsFactory")

Lasers.Remote = Lasers.Remote or {}

local ICON_ON = "media/ui/vehicles/vehicle_lightsON.png"
local ICON_OFF = "media/ui/vehicles/vehicle_lightsOFF.png"

local function texts(weapon)
    if Lasers.IsSwitchedOn(weapon) then
        return getText("IGUI_GunsOfTien_LaserOff"), getText("IGUI_GunsOfTien_LaserOffDesc"), ICON_OFF
    end
    return getText("IGUI_GunsOfTien_LaserOn"), getText("IGUI_GunsOfTien_LaserOnDesc"), ICON_ON
end

local function isEmpty(weapon)
    local part = Lasers.GetLaser(weapon)
    -- a laser never charged yet gets its first battery when switched on (Lasers.InitCharge)
    return part ~= nil and part:getModData().GunsOfTien_LaserCharged == true and part:getCurrentUses() <= 0
end

local function addOption(playerObj, item, context)
    if not Lasers.GetLaser(item) then return end
    local name, desc = texts(item)
    local option = context:addOption(name, playerObj, Lasers.Queue, item)
    local tooltip = ISInventoryPaneContextMenu.addToolTip()
    tooltip:setName(name)
    tooltip.texture = item:getTex()
    if item:getContainer() ~= playerObj:getInventory() then
        option.notAvailable = true
        tooltip.description = getText("IGUI_MoveToInventory")
    elseif not Lasers.IsSwitchedOn(item) and isEmpty(item) then
        option.notAvailable = true
        tooltip.description = getText("IGUI_GunsOfTien_LaserEmpty")
    else
        tooltip.description = desc
    end
    option.toolTip = tooltip
end

Events.OnFillInventoryObjectContextMenu.Add(function(playerNum, context, items)
    local playerObj = getSpecificPlayer(playerNum)
    for _, v in ipairs(items) do
        local item = v
        if not instanceof(v, "InventoryItem") then
            item = v.items[1]
        end
        if instanceof(item, "HandWeapon") then
            addOption(playerObj, item, context)
        end
    end
end)

local fillMenu = ISFirearmRadialMenu.fillMenu

function ISFirearmRadialMenu:fillMenu()
    fillMenu(self)
    local weapon = self.character:getPrimaryHandItem()
    if not Lasers.GetLaser(weapon) then return end
    if not Lasers.IsSwitchedOn(weapon) and isEmpty(weapon) then return end
    local name, _, icon = texts(weapon)
    local character = self.character
    getPlayerRadialMenu(self.playerNum):addSlice(name, getTexture(icon), function()
        ISTimedActionQueue.add(ISToggleLaserGoT:new(character, weapon, CharacterActionAnims.Craft))
    end)
end

-------------------------------------------------
-- Other players' lasers
-------------------------------------------------
Events.OnServerCommand.Add(function(module, command, args)
    if module ~= Lasers.MODULE or command ~= Lasers.CMD or type(args) ~= "table" then return end
    if args.id then
        Lasers.Remote[args.id] = args.on == true or nil
    end
end)

-------------------------------------------------
-- Re-apply stats when the local gun's lit state changes (the sync does not carry critical chance)
-------------------------------------------------
local applied = {}
local tick = 0

Events.OnTick.Add(function()
    tick = tick + 1
    if tick % 30 ~= 0 then return end
    for i = 0, getNumActivePlayers() - 1 do
        local player = getSpecificPlayer(i)
        local weapon = player and player:getPrimaryHandItem()
        if weapon and Lasers.GetLaser(weapon) then
            local lit = Lasers.IsLit(weapon)
            local id = weapon:getID()
            if applied[id] ~= lit then
                if applied[id] ~= nil then
                    StatsFactory.ReapplyAllModifiers(weapon)
                end
                applied[id] = lit
            end
        end
    end
end)

-------------------------------------------------
-- Tooltips of the laser parts
-------------------------------------------------
local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if ok and type(tooltips) == "table" and type(tooltips.tooltipsPergun) == "table" then
    local NOTE = "Bonus only while switched on: needs a battery (about 3 weeks switched on)."
    for fullType in pairs(Lasers.TYPES) do
        local list = tooltips.tooltipsPergun[fullType]
        if not list then
            list = {}
            tooltips.tooltipsPergun[fullType] = list
        end
        local present = false
        for _, line in ipairs(list) do
            if line == NOTE then present = true end
        end
        if not present then
            -- before GoM's "Needs Screwdriver..." line, so the bonus and its condition stay together
            local at = #list + 1
            for i, line in ipairs(list) do
                if line:find("^Needs ") then at = i break end
            end
            table.insert(list, at, NOTE)
        end
    end
end
