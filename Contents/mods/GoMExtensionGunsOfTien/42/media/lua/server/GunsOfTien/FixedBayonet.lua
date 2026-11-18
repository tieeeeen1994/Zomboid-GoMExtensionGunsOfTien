--[[
    Guns of Tien -- the server's half of fixing a bayonet (shared/GunsOfTien/FixedBayonet.lua has the why).

    Command "fixedBayonet" { itemId, fix = true | false } from the player holding the gun or its melee item in the
    primary hand; anything else is ignored (Gunworks' underbarrelMode checks the same). The answer, the new item's
    ID, only tells the client to refresh its hotbar. Melee items that broke during a hit (their OnBreak) are unfixed
    on the next tick, wherever they are in the player's inventory. Runs in single player too, where the client file
    calls FixedBayonet.Fix / Unfix itself.
--]]

if isClient() then return end

local FixedBayonet = require("GunsOfTien/FixedBayonet")

local function reply(player, item)
    if item and isServer() then
        sendServerCommand(player, FixedBayonet.MODULE, FixedBayonet.COMMAND, { itemId = item:getID() })
    end
end

Events.OnClientCommand.Add(function(module, command, player, args)
    if module ~= FixedBayonet.MODULE or command ~= FixedBayonet.COMMAND then return end
    if not player or type(args) ~= "table" or type(args.itemId) ~= "number" then return end
    local held = player:getPrimaryHandItem()
    if not held or held:getID() ~= args.itemId then return end
    if args.fix == true then
        reply(player, FixedBayonet.Fix(player, held))
    elseif args.fix == false then
        reply(player, FixedBayonet.Unfix(player, held))
    end
end)

Events.OnTick.Add(function()
    local broken = FixedBayonet.broken
    if #broken == 0 then return end
    FixedBayonet.broken = {}
    for _, entry in ipairs(broken) do
        local player, item = entry.player, entry.item
        if not player:isDead() and player:getInventory():containsRecursive(item) and FixedBayonet.IsFixed(item) then
            reply(player, FixedBayonet.Unfix(player, item))
        end
    end
end)
