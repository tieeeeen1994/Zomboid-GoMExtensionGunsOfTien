--[[
    Guns of Tien -- belt links on the server (shared/GunsOfTien/BeltLinks.lua): a client reports the links of the
    shots it fired from a belt box (client/GunsOfTien/BeltLinks.lua). If the gun in its hands is that gun with a belt
    box fitted, the links are thrown out of it (BeltLinks.eject) two a tick, so a burst's links come out over the
    burst instead of in one clump, no more than the M249's adverse rate allows since the last report.
--]]

if isClient() then return end

local MAX_RPM = 1000
local PER_TICK = 2
local last = {}                      -- online ID -> time of the last report (ms)
local queue = {}                     -- { player, weapon, link, count }

local function onClientCommand(module, command, player, args)
    if module ~= "GunsOfTien" or command ~= "beltLinks" then return end
    local BeltLinks = GunsOfTien_BeltLinks
    if not (BeltLinks and player and type(args) == "table") then return end
    local id, n = tonumber(args.id), tonumber(args.n)
    if not id or not n or n < 1 then return end
    local weapon = player:getPrimaryHandItem()
    if not (weapon and weapon:getID() == id) then return end
    local link = BeltLinks.linkForGun(weapon)
    if not link then return end
    local now = getTimestampMs()
    local key = player:getOnlineID()
    local allowed = math.floor((now - (last[key] or (now - 1000))) * MAX_RPM / 60000) + 2
    last[key] = now
    queue[#queue + 1] = { player = player, weapon = weapon, link = link, count = math.min(math.floor(n), allowed, 40) }
end

local function onTick()
    if #queue == 0 then return end
    local BeltLinks = GunsOfTien_BeltLinks
    for i = #queue, 1, -1 do
        local q = queue[i]
        local n = math.min(PER_TICK, q.count)
        for _ = 1, n do
            BeltLinks.eject(q.player, q.weapon, q.link)
        end
        q.count = q.count - n
        if q.count <= 0 then table.remove(queue, i) end
    end
end

Events.OnClientCommand.Add(onClientCommand)
Events.OnTick.Add(onTick)
