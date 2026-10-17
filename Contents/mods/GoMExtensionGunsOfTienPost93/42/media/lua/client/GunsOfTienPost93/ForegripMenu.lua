--[[
    Guns of Tien - Post-93 -- "Fold / Unfold Foregrip" for the MP7A1's integral front grip (shared/Foregrip.lua), in
    the two places Gunworks offers "Fold / Unfold Stock": the inventory context menu of the gun
    (Gunworks_ContextMenu_ISUI addFoldableStockOption, same tooltip and "move to inventory" rule) and the firearm
    radial menu (Gunworks wraps ISFirearmRadialMenu.fillMenu and adds its slices after vanilla's; this wrapper runs
    after it, our mod loads after SWMG). The radial icons are ours (scripts/post93/make_foregrip_radial.py), drawn in
    Gunworks' style.
--]]

require("ISUI/ISInventoryPaneContextMenu")
require("ISUI/ISFirearmRadialMenu")

local Foregrip = require("GunsOfTienPost93/Foregrip")

local function texts(weapon)
    if Foregrip.IsDeployed(weapon) then
        return getText("IGUI_GunsOfTienPost93_FoldForegrip"), getText("IGUI_GunsOfTienPost93_FoldForegripDesc"),
            "media/ui/GunsOfTienPost93_Radial_FoldForegrip.png"
    end
    return getText("IGUI_GunsOfTienPost93_UnfoldForegrip"), getText("IGUI_GunsOfTienPost93_UnfoldForegripDesc"),
        "media/ui/GunsOfTienPost93_Radial_UnfoldForegrip.png"
end

local function addOption(playerObj, item, context)
    if not Foregrip.Has(item) then return end
    local name, desc = texts(item)
    local option = context:addOption(name, playerObj, Foregrip.Queue, item)
    local tooltip = ISInventoryPaneContextMenu.addToolTip()
    tooltip:setName(name)
    tooltip.texture = item:getTex()
    if item:getContainer() == playerObj:getInventory() then
        tooltip.description = desc
    else
        option.notAvailable = true
        tooltip.description = getText("IGUI_MoveToInventory")
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
        addOption(playerObj, item, context)
    end
end)

local fillMenu = ISFirearmRadialMenu.fillMenu

function ISFirearmRadialMenu:fillMenu()
    fillMenu(self)
    local weapon = self.character:getPrimaryHandItem()
    if not Foregrip.Has(weapon) then return end
    local name, _, icon = texts(weapon)
    local character = self.character
    getPlayerRadialMenu(self.playerNum):addSlice(name, getTexture(icon), function()
        ISTimedActionQueue.add(ISFoldForegripGoT:new(character, weapon, CharacterActionAnims.Craft))
    end)
end
