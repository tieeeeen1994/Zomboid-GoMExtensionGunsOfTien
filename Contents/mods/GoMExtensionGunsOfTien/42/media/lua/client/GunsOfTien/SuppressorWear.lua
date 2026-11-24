--[[
    Guns of Tien -- suppressor wear you can see and fix (user, 2026-11-25: "We can't repair the suppressors", "a
    condition bar under the gun tooltip").

    Since November 2026 GoM's cans (and ours: Mk9, MP7, P90, Five-seveN, SCAR-H, 9A-91) wear while mounted (Gunworks
    `AttachmentsDurability.RollConditionLowering`, server, at every shot: -1 condition 1 in ConditionLowerChance) and
    GoM ships fixings for them (MarzWeapons/recipes/fixing.txt). Only parts registered there wear: muzzle devices,
    scopes and the rest never lose condition.

    Repair. A mounted part is no inventory item, so no Repair is offered while it is on the gun, and Gunworks only
    takes it off once it is broken (condition 0). Vanilla's inventory menu offers Repair only for an item that is
    **not** broken (ISInventoryPaneContextMenu ~202, "broken objects needs to be reclaimed"), so a worn-out can was
    beyond the menu. The Java side does not care (42.22.2, traced 2026-11-25): `FixingManager.fixItem` raises the
    condition with `setConditionNoSound`, whose `setBroken(condition <= 0)` clears the flag, then `syncItemFields`;
    the client's SyncItemFieldsPacket applies it with `setCondition` (broken cleared there too); `ISFixAction` checks
    only the fixer. So vanilla's own Repair submenu (`buildFixingMenu`: same fixings, chances and skills) is added for
    a broken registered part, and nothing else: other broken items stay as vanilla wants them. A failed repair at
    condition 0 only uses the fixer (vanilla's `fixItem`).

    Condition bar. The gun's tooltip gets a bar per mounted registered part, labelled with its name and coloured as
    vanilla's Condition bar (`HandWeapon.DoTooltip(tooltip, layout)`: bad-to-good highlight colour by condition /
    max). Two ways a gun tooltip is drawn, both through the HandWeapon class metatable:
    - `item:DoTooltip(tooltip)` (vanilla ISToolTipInv, GoM's CustomItemTooltips): Java fills and renders its layout
      internally, so the bar goes in a layout of its own under it, as Gunworks' "Chamber is open" row
      (client/WeaponSystems/CanShootMessage.lua). The one-argument call only: the two-argument overload is Java's
      own fill.
    - `item:DoTooltipEmbedded(tooltip, layout, y)` from Lua (ZomboidFixesB42's GoM tooltip redraw, which never goes
      through DoTooltip): the bar is added to that layout, in the game's own columns, before it is rendered.
--]]

require("ISUI/ISInventoryPaneContextMenu")

local AttachmentsDurability = require("WeaponSystems/Utils/AttachmentsDurability")

local function wears(item)
    return AttachmentsDurability.IsAttachmentRegistered(item:getFullType())
end

-- Repair ----------------------------------------------------------------------------------------------------------

local function brokenWornPart(items)
    for _, item in ipairs(ISInventoryPane.getActualItems(items)) do
        if item:isBroken() and wears(item) then return item end
    end
end

Events.OnFillInventoryObjectContextMenu.Add(function(player, context, items)
    local part = brokenWornPart(items)
    if not part then return end
    local fixingList = FixingManager.getFixes(part)
    if fixingList:isEmpty() then return end
    local fixOption = context:addOption(getText("ContextMenu_Repair") .. " " .. getItemNameFromFullType(part:getFullType()), items, nil)
    local subMenuFix = ISContextMenu:getNew(context)
    context:addSubMenu(fixOption, subMenuFix)
    for i = 0, fixingList:size() - 1 do
        ISInventoryPaneContextMenu.buildFixingMenu(part, player, fixingList:get(i), i, fixOption, subMenuFix)
    end
end)

-- Condition bar ---------------------------------------------------------------------------------------------------

--- Add a bar per mounted part that wears; returns whether any was added.
local function addBars(layout, weapon)
    local parts = weapon:getAllWeaponParts()
    if not parts then return false end
    local added = false
    local bad, good = getCore():getBadHighlitedColor(), getCore():getGoodHighlitedColor()
    for i = 0, parts:size() - 1 do
        local part = parts:get(i)
        if part and wears(part) then
            local f = part:getCondition() / math.max(1, part:getConditionMax())
            local row = layout:addItem()
            row:setLabel(part:getDisplayName() .. ":", 1.0, 1.0, 0.8, 1.0)
            row:setProgress(f, bad:getR() + (good:getR() - bad:getR()) * f, bad:getG() + (good:getG() - bad:getG()) * f,
                bad:getB() + (good:getB() - bad:getB()) * f, 1.0)
            added = true
        end
    end
    return added
end

local index = __classmetatables[HandWeapon.class].__index

local doTooltip = index.DoTooltip
index.DoTooltip = function(weapon, tooltip, ...)
    doTooltip(weapon, tooltip, ...)
    if select("#", ...) ~= 0 then return end
    local layout = tooltip:beginLayout()
    if addBars(layout, weapon) then
        local padSide = getTextManager():MeasureStringX(tooltip:getFont(), "0")
        local endY = layout:render(padSide, tooltip:getHeight() - math.floor(padSide / 2), tooltip)
        tooltip:setHeight(endY + math.floor(padSide / 2))
    end
    tooltip:endLayout(layout)
end

local doTooltipEmbedded = index.DoTooltipEmbedded
index.DoTooltipEmbedded = function(weapon, tooltip, layout, ...)
    doTooltipEmbedded(weapon, tooltip, layout, ...)
    if layout then addBars(layout, weapon) end
end
