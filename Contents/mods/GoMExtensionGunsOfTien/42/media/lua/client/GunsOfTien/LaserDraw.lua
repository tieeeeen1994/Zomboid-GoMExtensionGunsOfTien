--[[
    Guns of Tien -- lit lasers show a red dot where the gun points, with a faint beam (user, 2026-10-18: "Dot and faint
    beam"; shared/GunsOfTien/Lasers.lua has the design).

    Drawn for every character with a lit laser in hand who is aiming: the local players from their own gun (its
    modData and the laser's charge come from the server), other players from the server's broadcast
    (LaserMenu.lua, Lasers.Remote). B42's renderer gives Lua no world draw event, so this draws in the UI pass
    (OnPreUIDraw: over the world, under the UI) at isoToScreenX/Y of world points (TienLastSeenWhere's arrow does the
    same). Lua cannot read bone or muzzle positions (no AnimationPlayer access), so the beam starts in front of the
    character at about shoulder height (GUN_FORWARD, GUN_HEIGHT, in tiles and floor levels) along their facing.

    The beam runs on in steps of STEP tiles until a square boundary blocks it (IsoGridSquare.isBlockedTo: walls,
    closed doors and windows), the gun's range (at most MAX_RANGE) or a zombie / player within HIT_RADIUS of the line,
    whose chest takes the dot. Same floor only.
--]]

local Lasers = require("GunsOfTien/Lasers")

local GUN_FORWARD = 0.45        -- tiles from the character's centre to the muzzle while aiming
local GUN_HEIGHT = 0.5          -- floor levels above the feet (a level is a wall's height)
local CHEST_HEIGHT = 0.45       -- where the dot lands on a character
local MAX_RANGE = 40
local STEP = 0.2
local HIT_RADIUS = 0.3
local BEAM_ALPHA = 0.18
local BEAM_WIDTH = 1.2          -- pixels each side of the line
local DOT_SIZE = 3.5            -- pixels, radius
local GLOW_SIZE = 9

local beamTex, dotTex

local function textures()
    if not dotTex then
        dotTex = getTexture("media/ui/circle.png")
        beamTex = getTexture("media/ui/whitebar.png") or dotTex
    end
    return beamTex, dotTex
end

--- Nearest character along the ray (distance in tiles), skipping the shooter.
local function nearestCharacter(shooter, x0, y0, z, dx, dy, range)
    local best = range
    local function test(chr)
        if chr == shooter or chr:isDead() or math.floor(chr:getZ()) ~= z then return end
        local rx, ry = chr:getX() - x0, chr:getY() - y0
        local along = rx * dx + ry * dy
        if along <= 0 or along >= best then return end
        if math.abs(rx * dy - ry * dx) <= HIT_RADIUS then
            best = along
        end
    end
    local zombies = getCell():getZombieList()
    if zombies then
        for i = 0, zombies:size() - 1 do
            test(zombies:get(i))
        end
    end
    local players = getOnlinePlayers()
    if players and players:size() > 0 then
        for i = 0, players:size() - 1 do
            test(players:get(i))
        end
    else
        for i = 0, getNumActivePlayers() - 1 do
            local p = getSpecificPlayer(i)
            if p then test(p) end
        end
    end
    return best, best < range
end

--- Where the beam stops: (distance, hit a character).
local function traceBeam(shooter, x0, y0, z, dx, dy, range)
    local limit, onCharacter = nearestCharacter(shooter, x0, y0, z, dx, dy, range)
    local cell = getCell()
    local prev = cell:getGridSquare(math.floor(x0), math.floor(y0), z)
    if not prev then return 0, false end
    local t = STEP
    while t < limit do
        local sq = cell:getGridSquare(math.floor(x0 + dx * t), math.floor(y0 + dy * t), z)
        if not sq then return t, false end
        if sq ~= prev then
            if prev:isBlockedTo(sq) then return t, false end
            prev = sq
        end
        t = t + STEP
    end
    return limit, onCharacter
end

local function quad(tex, ax, ay, bx, by, half, r, g, b, a)
    local lx, ly = bx - ax, by - ay
    local len = math.sqrt(lx * lx + ly * ly)
    if len < 0.5 then return end
    local nx, ny = -ly / len * half, lx / len * half
    getRenderer():renderPoly(tex, ax + nx, ay + ny, bx + nx, by + ny, bx - nx, by - ny, ax - nx, ay - ny, r, g, b, a)
end

local function disc(tex, x, y, radius, r, g, b, a)
    getRenderer():renderPoly(tex, x - radius, y - radius, x + radius, y - radius, x + radius, y + radius,
        x - radius, y + radius, r, g, b, a)
end

local function drawLaser(playerNum, chr, weapon)
    local dir = chr:getForwardDirection()
    local dx, dy = dir:getX(), dir:getY()
    local len = math.sqrt(dx * dx + dy * dy)
    if len < 0.001 then return end
    dx, dy = dx / len, dy / len
    local z = math.floor(chr:getZ())
    local x0, y0 = chr:getX() + dx * GUN_FORWARD, chr:getY() + dy * GUN_FORWARD
    local range = math.min(weapon:getMaxRange() > 0 and weapon:getMaxRange() or MAX_RANGE, MAX_RANGE)
    local dist, onCharacter = traceBeam(chr, x0, y0, z, dx, dy, range)
    local ex, ey = x0 + dx * dist, y0 + dy * dist
    local endHeight = onCharacter and CHEST_HEIGHT or GUN_HEIGHT
    local zf = chr:getZ()
    local sx0, sy0 = isoToScreenX(playerNum, x0, y0, zf + GUN_HEIGHT), isoToScreenY(playerNum, x0, y0, zf + GUN_HEIGHT)
    local sx1, sy1 = isoToScreenX(playerNum, ex, ey, zf + endHeight), isoToScreenY(playerNum, ex, ey, zf + endHeight)
    local beam, dot = textures()
    if not dot then return end
    quad(beam, sx0, sy0, sx1, sy1, BEAM_WIDTH, 1.0, 0.1, 0.08, BEAM_ALPHA)
    disc(dot, sx1, sy1, GLOW_SIZE, 1.0, 0.15, 0.1, 0.25)
    disc(dot, sx1, sy1, DOT_SIZE, 1.0, 0.2, 0.15, 0.95)
end

local function laserWeapon(chr, isLocal)
    if not chr or chr:isDead() or not chr:isAiming() then return nil end
    local weapon = chr:getPrimaryHandItem()
    if not weapon or not Lasers.GetLaser(weapon) then return nil end
    if isLocal then
        return Lasers.IsLit(weapon) and weapon or nil
    end
    return Lasers.Remote[chr:getOnlineID()] and weapon or nil
end

Events.OnPreUIDraw.Add(function()
    local player = getSpecificPlayer(0)
    if not player then return end
    local drawn = {}
    for i = 0, getNumActivePlayers() - 1 do
        local p = getSpecificPlayer(i)
        local weapon = laserWeapon(p, true)
        if weapon then
            drawLaser(0, p, weapon)
        end
        if p then drawn[p] = true end
    end
    local online = getOnlinePlayers()
    if online then
        for i = 0, online:size() - 1 do
            local p = online:get(i)
            if not drawn[p] and not p:isLocalPlayer() then
                local weapon = laserWeapon(p, false)
                if weapon then
                    drawLaser(0, p, weapon)
                end
            end
        end
    end
end)
