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
      The spread comes back too, once the server's copy is out (or 1 s later), so a zombie that survived is a
      normal zombie again for the next fire.
    - Our fire is the weak one (user, 2026-11-26: "another kind of fire source ALWAYS overwrites it"): a zombie
      already burning from something else ignores our hit, and one of ours that stands on burning ground (a
      Molotov, any fire: the square's IsoFlagType.burning, what vanilla's FireCheck lights zombies from) is handed
      over on every machine: no end time, vanilla's rate, its spread and corpse fire back, never put out by us.
    - Zombie objects are recycled (42.22 `VirtualZombieManager.reuseZombie` -> `IsoZombie.resetForReuse`): the
      reset wipes the mod data and the online ID but keeps fireSpreadProbability and fireKillRate, so a zombie
      that despawns or dies while ours would hand spread 0 and our 18x burn rate to the next zombie built from
      its object. Every machine keeps the objects it changed (`touched`) with our mark in their mod data; one
      found dead or with the mark gone (wiped by the reset) gets vanilla's numbers back and drops its burn.
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

local touched = {}          -- zombie object -> its burn key: objects whose rate or spread this machine changed

-- mark an object we change (the mark is in its mod data, which a reuse of the object wipes)
local function touch(zombie, key)
    zombie:getModData()[MARK] = true
    touched[zombie] = key
end

local function contain(zombie, key)
    touch(zombie, key)
    zombie:setFireSpreadProbability(0)
end

-- a normal zombie again: vanilla's rate and spread (so its corpse fire too), no mark
local function release(zombie)
    zombie:getModData()[MARK] = nil
    zombie:setFireSpreadProbability(VANILLA_SPREAD)
    zombie:setFireKillRate(VANILLA_RATE)
    touched[zombie] = nil
end

local function onBurningGround(zombie)
    local sq = zombie:getCurrentSquare()
    return sq ~= nil and sq:has(IsoFlagType.burning)
end

local MP = isClient() or isServer()

-- The burns are the server's (user, 2026-11-25: "Can we not make the burns owned by the server?"): it decides
-- which zombie burns until when and tells every client (`burn {id, ms}`); each machine keeps the same table and the
-- one running the zombie now applies it every 100 ms: lit, at BURN_RATE, out when the time is up. The damage
-- itself cannot be the server's: the owner's ZombiePacket overwrites the server copy's health. So when another
-- client takes the zombie over mid-burn, it already has the entry and carries on with the same fire and rate.
-- Key: online ID in multiplayer, the zombie itself in single player (no online IDs there).
local burns = {}            -- key -> local real time (ms) the fire goes out
local cooling = {}          -- server / single player, key -> real time (ms): our fire is out, give the spread back
                            -- once this copy has stopped burning (the owner's packet), at the latest at that time

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
    local function find(key)                           -- the zombie for a table key (built once a check)
        if not MP then return key end
        if not byId then
            byId = {}
            local list = getCell():getZombieList()
            for i = 0, list:size() - 1 do
                local z = list:get(i)
                byId[z:getOnlineID()] = z
            end
        end
        return byId[key]
    end
    for zombie, key in pairs(touched) do
        if zombie:isDead() then
            release(zombie)
        elseif not zombie:getModData()[MARK] then
            release(zombie)                            -- recycled into another zombie (the reset wiped the mark)
            burns[key], cooling[key] = nil, nil
        end
    end
    for key, ends in pairs(burns) do
        now = now or getTimestampMs()
        local zombie = find(key)
        if zombie and zombie:isDead() then
            burns[key] = nil
        elseif zombie and onBurningGround(zombie) then
            burns[key] = nil                           -- another fire: vanilla's from here on
            release(zombie)
        elseif now >= ends then
            burns[key] = nil
            if zombie then
                if runsHere(zombie) and zombie:isOnFire() then zombie:StopBurning() end
                zombie:setFireKillRate(VANILLA_RATE)
                if isClient() then release(zombie) else cooling[key] = now + 1000 end
            end
        elseif zombie and runsHere(zombie) then
            if not zombie:isOnFire() then zombie:SetOnFire() end
            touch(zombie, key)
            zombie:setFireKillRate(BURN_RATE)
        end
    end
    for key, deadline in pairs(cooling) do
        now = now or getTimestampMs()
        local zombie = find(key)
        if burns[key] then
            cooling[key] = nil                         -- lit again by us: contain() still holds
        elseif not zombie or zombie:isDead() then
            cooling[key] = nil
        elseif not zombie:isOnFire() or now >= deadline then
            cooling[key] = nil
            release(zombie)
        end
    end
end)

-- the hit, on the shooter's machine only (OnHitZombie also fires on the server and on clients replaying the hit)
Events.OnHitZombie.Add(function(zombie, wielder, bodyPart, weapon)
    if isServer() or not weapon or not instanceof(wielder, "IsoPlayer") or not wielder:isLocalPlayer() then return end
    local chance = weapon.getAmmoType and CHANCE[weapon:getAmmoType()]
    if not chance or zombie:isDead() or ZombRandFloat(0, 1) >= chance then return end
    if zombie:isOnFire() and not burns[MP and zombie:getOnlineID() or zombie] then return end   -- not ours
    if isClient() then
        sendClientCommand(wielder, MODULE, IGNITE, { id = zombie:getOnlineID() })
    else
        contain(zombie, zombie)
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
        if zombie:isOnFire() and not burns[args.id] then return end   -- another fire burns it: that one wins
        if math.abs(zombie:getX() - player:getX()) > 80 or math.abs(zombie:getY() - player:getY()) > 80 then return end
        contain(zombie, args.id)
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
    if not zombie:getModData()[MARK] then return end
    burns[MP and zombie:getOnlineID() or zombie] = nil
    zombie:StopBurning()
    release(zombie)
end)
