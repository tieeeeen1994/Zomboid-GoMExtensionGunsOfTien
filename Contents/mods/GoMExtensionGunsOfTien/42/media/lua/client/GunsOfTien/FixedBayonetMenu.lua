--[[
    Guns of Tien -- Fix / Unfix Bayonet (shared/GunsOfTien/FixedBayonet.lua has the why): its own key (default Z,
    which vanilla binds only to switching seats in a vehicle, where no one stabs; vanilla binds every other free
    letter but K, which TienInspectWeapon and Tien's Skill Mastery use), the firearm radial menu (Gunworks' Deploy
    Bayonet icon) and the inventory context menu. Instant, as Gunworks' underbarrel switch (user, 2026-11-19).

    The key is a vanilla key binding (the keyBinding table, [Guns of Tien] section in the controls), as
    TienInspectWeapon's: OnKeyPressed fires on release and not while a text box has focus. The radial menu only
    opens for firearms, so a fixed bayonet is unfixed with the key or the context menu.

    Multiplayer: the client asks the server (the swap is the server's, it moves items) and refreshes the hotbar when
    the answer comes; single player swaps at once.
--]]

require("ISUI/ISInventoryPaneContextMenu")
require("ISUI/ISFirearmRadialMenu")

local FixedBayonet = require("GunsOfTien/FixedBayonet")

local RADIAL_ICON = "media/ui/GunworksRadial_DeployBayonet.png"
local REQUEST_GAP_MS = 500

local function registerKeyBinding()
    if not keyBinding then return end
    for _, existing in ipairs(keyBinding) do
        if existing.value == FixedBayonet.KEYBIND then return end
    end
    table.insert(keyBinding, { value = "[GunsOfTien]" })
    table.insert(keyBinding, { value = FixedBayonet.KEYBIND, key = Keyboard.KEY_Z })
end

registerKeyBinding()

local lastRequest = 0

--- fix = true: gun -> fixed bayonet; false: back. The item must be in the primary hand.
function FixedBayonet.Request(player, item, fix)
    if not player or not item or player:getPrimaryHandItem() ~= item then return end
    if player:isAttacking() or player:isAttackStarted() then return end
    if isClient() then
        local now = getTimestampMs()
        if now - lastRequest < REQUEST_GAP_MS then return end
        lastRequest = now
        sendClientCommand(player, FixedBayonet.MODULE, FixedBayonet.COMMAND, { itemId = item:getID(), fix = fix })
    elseif fix then
        FixedBayonet.Fix(player, item)
    else
        FixedBayonet.Unfix(player, item)
    end
end

--- What the held item offers: true = Fix, false = Unfix, nil = nothing.
local function offer(item)
    if FixedBayonet.IsFixed(item) then return false end
    if FixedBayonet.CanFix(item) then return true end
    return nil
end

Events.OnKeyPressed.Add(function(key)
    if not getCore():isKey(FixedBayonet.KEYBIND, key) then return end
    local player = getSpecificPlayer(0)
    if not player or player:isDead() or player:getVehicle() then return end
    local item = player:getPrimaryHandItem()
    local fix = offer(item)
    if fix ~= nil then FixedBayonet.Request(player, item, fix) end
end)

Events.OnServerCommand.Add(function(module, command, args)
    if module ~= FixedBayonet.MODULE or command ~= FixedBayonet.COMMAND then return end
    for i = 0, getNumActivePlayers() - 1 do
        local hotbar = getSpecificPlayer(i) and getPlayerHotbar(i)
        if hotbar then hotbar.needsRefresh = true end
    end
end)

local function label(fix)
    return getText(fix and "IGUI_GunsOfTien_FixBayonet" or "IGUI_GunsOfTien_UnfixBayonet")
end

Events.OnFillInventoryObjectContextMenu.Add(function(playerNum, context, items)
    local player = getSpecificPlayer(playerNum)
    if not player then return end
    for _, v in ipairs(items) do
        local item = instanceof(v, "InventoryItem") and v or v.items[1]
        local fix = offer(item)
        if fix ~= nil then
            local option = context:addOption(label(fix), player, FixedBayonet.Request, item, fix)
            if player:getPrimaryHandItem() ~= item then
                option.notAvailable = true
                local tooltip = ISInventoryPaneContextMenu.addToolTip()
                tooltip:setName(label(fix))
                tooltip.description = getText("IGUI_GunsOfTien_FixBayonetHold")
                option.toolTip = tooltip
            end
            return
        end
    end
end)

local fillMenu = ISFirearmRadialMenu.fillMenu

function ISFirearmRadialMenu:fillMenu()
    fillMenu(self)
    local weapon = self.character:getPrimaryHandItem()
    if not FixedBayonet.CanFix(weapon) then return end
    local character = self.character
    getPlayerRadialMenu(self.playerNum):addSlice(label(true), getTexture(RADIAL_ICON), function()
        FixedBayonet.Request(character, weapon, true)
    end)
end
