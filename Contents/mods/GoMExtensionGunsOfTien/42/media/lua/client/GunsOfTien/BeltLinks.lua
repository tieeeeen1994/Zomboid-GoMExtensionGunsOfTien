--[[
    Guns of Tien -- belt links on an MP client (shared/GunsOfTien/BeltLinks.lua): the links of the shots fired from a
    belt box, counted per gun by the shared OnWeaponSwingHitPoint handler, go to the server twice a second (one
    command for a burst instead of one a round), which throws them out of the gun.
--]]

if not isClient() then return end

local SEND_MS = 500
local lastSend = 0

local function flush()
    local BeltLinks = GunsOfTien_BeltLinks
    if not BeltLinks then return end
    local now = getTimestampMs()
    if now - lastSend < SEND_MS then return end
    lastSend = now
    local player = getPlayer()
    if not player then return end
    for id, n in pairs(BeltLinks.pending) do
        if n > 0 then
            sendClientCommand(player, "GunsOfTien", "beltLinks", { id = id, n = n })
        end
        BeltLinks.pending[id] = nil
    end
end

Events.OnTick.Add(flush)
