--[[
    Guns of Tien -- incendiary rounds set zombies on fire (user, 2026-11-25: "We can add incendiary rounds then"):
    the main mod's 7.62x54R B-32 and Post-93's 12 gauge Dragon's Breath. The fire stays on the zombie: it never
    lights the ground it walks over or the square it dies on.

    How the game burns a zombie (42.22 decompile, CLAUDE.md "Incendiary rounds"):
    - `SetOnFire()` lights it; `ReduceHealthWhenBurning` then takes health every update, only on the machine that
      runs the zombie (its owner client, or the server / single player when nobody owns it), until it dies. A zombie
      never goes out by itself.
    - In multiplayer the owner's ZombiePacket carries an IsOnFire flag (NetworkZombieVariables): every other copy,
      the server's included, lights or puts out its own to match. So a zombie must be lit on its owner, or the
      owner's next packet puts it out again: the shooter's client asks the server, the server tells every client
      (`getOwnerPlayer()`), single player lights it at once.
    - Ground fire comes from two places, both on the server / single player only: `SpreadFireMP` / `SpreadFire`
      while it burns, a roll against the zombie's own `fireSpreadProbability` (6), and the corpse, which starts a
      fire on its square when the zombie died burning. Zombies lit here get spread 0 and a mark; `OnZombieDead`
      fires before the corpse is made (`IsoGameCharacter.die` -> `Kill` -> `onKilled` -> OnZombieDead, then
      `becomeCorpse`), so the mark puts it out first and gives the spread back (zombie objects are reused).
    - It burns 3 s from the last hit (BURN_MS) at BURN_RATE (4 burns kill a normal zombie), then goes out and gets
      vanilla's rate back; the machine running it puts it out, and its next ZombiePacket puts out the other copies.
--]]

local MODULE, IGNITE, BURN = "GunsOfTien", "ignite", "burn"
local MARK = "GunsOfTien_Incendiary"
local VANILLA_SPREAD = 6
-- user, 2026-11-25: "make it so that the fire expires after like 3 seconds? Each hit again resets the timer"
local BURN_MS = 3000
-- user, 2026-11-25: "4 burns kill". ReduceHealthWhenBurning takes fireKillRate / 20 x GameTime multiplier a zombie
-- update (about 48 a real second at 1x whatever the frame rate: the multiplier carries 60 / fps and 0.8), so 3 s
-- of burning take 7.2 x rate. A normal-toughness zombie has 1.8-2.1 health (IsoZombie.DoZombieStats): a quarter of
-- 1.95 is 0.49, rate 0.068 (vanilla 0.0038). Tough zombies (3.5+) take about 8 burns, fragile ones (0.5+) one.
local BURN_RATE = 0.068
local VANILLA_RATE = 0.0038

-- AmmoType -> chance a hit lights the target (Gunworks sets the gun's AmmoType to the round it fires)
local CHANCE = {}
local T, P = GunsOfTien_AmmoTypes, GunsOfTienPost93_AmmoTypes
if T and T.BULLET_762x54_B32 then CHANCE[T.BULLET_762x54_B32] = 0.25 end
-- per pellet: nine pellets a shot, so most shots that hit light the target
if P and P.SHELL_12G_DragonsBreath then CHANCE[P.SHELL_12G_DragonsBreath] = 0.2 end

local function contain(zombie)
    zombie:getModData()[MARK] = true
    zombie:setFireSpreadProbability(0)
end

local MP = isClient() or isServer()

-- The burns are the server's (user, 2026-11-25: "Can we not make the burns owned by the server?"): it decides
-- which zombie burns until when and tells every client (`burn {id, ms}`); each machine keeps the same table and the
-- one running the zombie now applies it every 100 ms: lit, at BURN_RATE, out when the time is up. The damage
-- itself cannot be the server's: the owner's ZombiePacket overwrites the server copy's health. So when another
-- client takes the zombie over mid-burn, it already has the entry and carries on with the same fire and rate.
-- Key: online ID in multiplayer, the zombie itself in single player (no online IDs there).
local burns = {}            -- key -> local real time (ms) the fire goes out

local function start(key, ms)
    burns[key] = getTimestampMs() + ms                 -- every hit starts the 3 seconds again
end

local function findZombie(id)
    local list = getCell():getZombieList()
    for i = 0, list:size() - 1 do
        local zombie = list:get(i)
        if zombie:getOnlineID() == id then return zombie end
    end
end

-- does this machine run the zombie (and so apply its burn damage)?
local function runsHere(zombie)
    if isServer() then return zombie:getOwnerPlayer() == nil end
    if isClient() then return not zombie:isRemoteZombie() end
    return true
end

local tick = 0
Events.OnTick.Add(function()
    tick = tick + 1
    if tick % 6 ~= 0 then return end                   -- 100 ms at 60 fps; the damage itself is the game's, every update
    local byId, now
    for key, ends in pairs(burns) do
        now = now or getTimestampMs()
        local zombie = key
        if MP then
            if not byId then
                byId = {}
                local list = getCell():getZombieList()
                for i = 0, list:size() - 1 do
                    local z = list:get(i)
                    byId[z:getOnlineID()] = z
                end
            end
            zombie = byId[key]
        end
        if zombie and zombie:isDead() then
            burns[key] = nil
        elseif now >= ends then
            burns[key] = nil
            if zombie then
                if runsHere(zombie) and zombie:isOnFire() then zombie:StopBurning() end
                zombie:setFireKillRate(VANILLA_RATE)
            end
        elseif zombie and runsHere(zombie) then
            if not zombie:isOnFire() then zombie:SetOnFire() end
            zombie:setFireKillRate(BURN_RATE)
        end
    end
end)

-- the hit, on the shooter's machine only (OnHitZombie also fires on the server and on clients replaying the hit)
Events.OnHitZombie.Add(function(zombie, wielder, bodyPart, weapon)
    if isServer() or not weapon or not instanceof(wielder, "IsoPlayer") or not wielder:isLocalPlayer() then return end
    local chance = weapon.getAmmoType and CHANCE[weapon:getAmmoType()]
    if not chance or zombie:isDead() or ZombRandFloat(0, 1) >= chance then return end
    if isClient() then
        sendClientCommand(wielder, MODULE, IGNITE, { id = zombie:getOnlineID() })
    else
        contain(zombie)
        start(zombie, BURN_MS)
        zombie:SetOnFire()
        zombie:setFireKillRate(BURN_RATE)
    end
end)

if isServer() then
    Events.OnClientCommand.Add(function(module, command, player, args)
        if module ~= MODULE or command ~= IGNITE or type(args) ~= "table" or type(args.id) ~= "number" then return end
        local weapon = player:getPrimaryHandItem()
        if not instanceof(weapon, "HandWeapon") or not CHANCE[weapon:getAmmoType()] then return end
        local zombie = findZombie(args.id)
        if not zombie or zombie:isDead() then return end
        if math.abs(zombie:getX() - player:getX()) > 80 or math.abs(zombie:getY() - player:getY()) > 80 then return end
        contain(zombie)
        start(args.id, BURN_MS)
        sendServerCommand(MODULE, BURN, { id = args.id, ms = BURN_MS })     -- every client: whoever runs it now or later
    end)
elseif isClient() then
    Events.OnServerCommand.Add(function(module, command, args)
        if module ~= MODULE or command ~= BURN or type(args) ~= "table" or type(args.id) ~= "number" then return end
        start(args.id, tonumber(args.ms) or BURN_MS)
    end)
end

-- server / single player: out before the corpse is made, spread back for the next use of this zombie object
Events.OnZombieDead.Add(function(zombie)
    if isClient() then return end
    local md = zombie:getModData()
    if not md[MARK] then return end
    md[MARK] = nil
    burns[MP and zombie:getOnlineID() or zombie] = nil
    zombie:StopBurning()
    zombie:setFireSpreadProbability(VANILLA_SPREAD)
    zombie:setFireKillRate(VANILLA_RATE)
end)
-- ponytail: a lit zombie that despawns alive keeps spread 0 on its reused object; reset on reuse if that matters
