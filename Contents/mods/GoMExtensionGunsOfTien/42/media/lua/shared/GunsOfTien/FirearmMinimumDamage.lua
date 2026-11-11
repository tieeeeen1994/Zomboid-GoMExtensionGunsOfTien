--[[
    Guns of Tien -- minimum firearm damage (user, 2026-11-11; sandbox FirearmMinimumDamage, 0-100 %, default 0).

    Since Build 42.22 a gun's failed hit roll on a zombie (vanilla sandbox "Firearms Use Damage Chance", Zombies only
    or All types of target) staggers it for no damage: `CombatManager.getHitData` (~677) rolls
    `Rand.Next(100) <= hitChance`, and a failed roll returns `calculateHitData(..., ignoreDamage = true)`, so `Hit`
    works the damage out and `hitConsequences` skips applying it. In 42.21 the flag was only added after `Hit` had run
    (`attackCollisionCheck` ~1159 / ~1212), so every hit that reached a zombie did full damage: a bug, fixed in 42.22.
    This option gives a failed roll a share of the damage the same hit would have done had it landed (after body part,
    clothing, range and the gun's damage roll; without the crit multiplier, which vanilla never gives a failed roll).
    0 = vanilla, 100 = 42.21 (every hit lands).

    How (Lua never sees the game's roll: no event fires between `getHitData` and `Hit`, and the statistics it bumps are
    not exposed):
    - The roll is taken over for the shot. At `OnWeaponSwingHitPoint` (before `calculateHitInfoList` works out each
      target's chance) a local player's aimed firearm, not in a vehicle, sets the combat config's
      MINIMUM_TO_HIT_CHANCE to 100, so Java's roll always succeeds; it is put back on the next tick.
    - `OnWeaponHitCharacter` (inside `Hit`, before `processHitDamage`) rolls vanilla's chance itself:
      `Fire.hitChance` is `CombatManager.calculateHitChanceData`'s ranged branch for a target not in a vehicle,
      written out in Lua with the combat config's values read live, at the server's distance
      (`getHitDistanceSquared`: centres, floors 3 apart; the client's hit list measures to the nearest bone).
    - A failed roll on a zombie scales that hit: BASE_WEAPON_DAMAGE_MULTIPLIER and
      WEAPON_LEVEL_DAMAGE_MULTIPLIER_INCREMENT (`applyWeaponLevelDamageModifier`, a factor of every hit's damage in
      `processHitDamage`) times share / crit multiplier when the shot is a crit, put back at the next hit and on the
      next tick. Everything after is vanilla's: the hit counts as landed, the damage it returns is what the hit packet
      carries (42.22 has the server and the zombie's owner apply a client's zombie damage as sent), kills and
      corpses. A crit pull still knocks the zombie down, as on a vanilla failed roll. Hits that were failed rolls
      give Aiming XP (the server awards it for every hit not flagged ignored).
    - 100 skips the roll for zombies: every hit lands, crits included, as in 42.21.
    - Players and animals are rolled by the server in MP, which this never touches. In single player this client
      rolls them too: a failed roll is made a miss again (`setAvoidDamage`, consumed by `Hit` right after the event;
      the blood and hit sound already played) under Zombies only, and a no-damage hit (share 0) under All types.
    Read live at each shot. Off while "Firearms Use Damage Chance" is Disabled (a failed roll is a clean miss there).
--]]

GunsOfTien_FirearmMinimumDamage = GunsOfTien_FirearmMinimumDamage or {}
local Fire = GunsOfTien_FirearmMinimumDamage

--- The share (0..1) from the sandbox; 0 when unknown.
function Fire.share()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    local v = vars and tonumber(vars.FirearmMinimumDamage) or 0
    if v < 0 then v = 0 elseif v > 100 then v = 100 end
    return v / 100
end

--- Vanilla's "Firearms Use Damage Chance": 1 Disabled, 2 Zombies only, 3 All types of target.
function Fire.damageChanceMode()
    return SandboxVars and tonumber(SandboxVars.FirearmUseDamageChance) or 2
end

local function cfg(key)
    return getCombatConfig():get(CombatConfigKey[key])
end

local function javaInt(x)
    if x >= 0 then return math.floor(x) end
    return math.ceil(x)
end

-- CombatManager.getDistanceModifierSightless
local function distanceModifierSightless(dist, prone)
    local pb = cfg("POINT_BLANK_DISTANCE")
    if dist > pb then
        return (pb - dist) * (cfg("SIGHTLESS_TO_HIT_BASE_DISTANCE") + (pb - dist) * -cfg("POINT_BLANK_DROP_OFF_TO_HIT_PENALTY"))
    elseif dist < pb then
        return (pb - dist) / pb * cfg("POINT_BLANK_TO_HIT_MAXIMUM_BONUS") * (prone and cfg("SIGHTLESS_TO_HIT_PRONE_MODIFIER") or 1)
    end
    return 0
end

-- CombatManager.getAimDelayPenaltySightless
local function aimDelayPenaltySightless(aimDelay, dist)
    local pb = cfg("POINT_BLANK_DISTANCE")
    if dist < pb then
        aimDelay = aimDelay * (dist / pb)
    elseif dist > pb then
        aimDelay = aimDelay * (1 + (dist - pb * cfg("SIGHTLESS_AIM_DELAY_TO_HIT_DISTANCE_MODIFIER")))
    end
    return aimDelay
end

-- CombatManager.getDistanceModifier
local function distanceModifier(dist, min, max)
    if dist < min then
        if dist > cfg("POINT_BLANK_DISTANCE") then
            return (dist - min) * (cfg("OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY")
                + (dist - min) * -cfg("OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY_INCREMENT"))
        end
        return 0
    elseif dist > max then
        return -((dist - max) * (cfg("OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY")
            + (dist - max) * cfg("OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY_INCREMENT")))
    end
    local scale = (max - min) * 0.5
    return cfg("OPTIMAL_RANGE_TO_HIT_MAXIMUM_BONUS")
        * math.exp(-((dist - (min + scale)) ^ 2) / ((2 * ((max - min) / 7)) ^ 2))
end

-- CombatManager.getAimDelayPenalty
local function aimDelayPenalty(delay, dist, min, max)
    if min > -1 and dist >= min and dist <= max then
        local scale = (max - min) * 0.5
        delay = delay * (1 - (1 - math.abs(dist - (min + scale)) / scale) * 0.25)
    elseif dist > max then
        delay = delay * (1 + (dist - max) * 0.1)
    end
    local pb = cfg("POINT_BLANK_DISTANCE")
    return delay * (dist < pb and dist / pb or 1)
end

-- CombatManager.getMovePenalty
local function movePenalty(owner, dist)
    local penalty = owner:getBeenMovingFor()
        * (1 - (owner:getPerkLevel(Perks.Aiming) + owner:getPerkLevel(Perks.Nimble)) / 40)
    if dist < 10 then
        penalty = penalty * (dist / 10)
    else
        penalty = penalty * (1 + (dist - 10) * 0.07)
    end
    return penalty
end

-- CombatManager.getPainPenalty
local function painPenalty(owner)
    local parts = owner:getBodyDamage():getBodyParts()
    local pain = 0
    for i = BodyPartType.ToIndex(BodyPartType.Hand_L), BodyPartType.ToIndex(BodyPartType.UpperArm_R) do
        pain = pain + parts:get(i):getPain()
    end
    return pain * cfg("ARM_PAIN_TO_HIT_MODIFIER")
end

-- CombatManager.getWeatherPenalty
local function weatherPenalty(owner, weapon, square, dist)
    local penalty = 0
    if not square then return penalty end
    local sight = weapon:getActiveSight()
    local thermal = sight ~= nil and sight:hasTag(ItemTag.THERMAL)
    if square:isOutside() then
        local climate = getClimateManager()
        local marksman = owner:hasTrait(CharacterTrait.MARKSMAN)
        penalty = penalty + climate:getWindIntensity()
            * (cfg("WIND_INTENSITY_TO_HIT_PENALTY") - owner:getPerkLevel(Perks.Aiming) * cfg("WIND_INTENSITY_TO_HIT_AIMING_MODIFIER"))
            * dist
            * (marksman and cfg("WIND_INTENSITY_TO_HIT_MINIMUM_MARKSMAN_MODIFIER") or cfg("WIND_INTENSITY_TO_HIT_MAXIMUM_MARKSMAN_MODIFIER"))
        penalty = penalty + climate:getRainIntensity() * dist * cfg("RAIN_INTENSITY_TO_HIT_DISTANCE_MODIFIER")
        penalty = penalty * owner:getCharacterTraits():getTraitWeatherPenaltyModifier()
        if not thermal then
            penalty = penalty + climate:getFogIntensity() * cfg("FOG_INTENSITY_DISTANCE_MODIFIER") * dist
        end
        penalty = penalty * math.min(dist / cfg("POINT_BLANK_DISTANCE"), cfg("POINT_BLANK_MAXIMUM_DISTANCE_MODIFIER"))
        penalty = penalty * (tonumber(SandboxVars.FirearmWeatherMultiplier) or 1)
    end
    if thermal then return penalty end
    local light = square:getLightLevel(owner:getPlayerNum())
    local threshold = cfg("LOW_LIGHT_THRESHOLD")
    if light < threshold then
        penalty = penalty + math.max(0, cfg("LOW_LIGHT_TO_HIT_MAXIMUM_PENALTY") * (1 - light / threshold))
            - weapon:getLowLightBonus()
    end
    return penalty
end

-- CombatManager.getMoodlesPenalty
local function moodlesPenalty(owner, dist)
    local m = owner:getMoodles()
    return (m:getMoodleLevel(MoodleType.PANIC) * (cfg("PANIC_TO_HIT_BASE_PENALTY") + dist * cfg("PANIC_TO_HIT_DISTANCE_MODIFIER"))
        + m:getMoodleLevel(MoodleType.STRESS) * (cfg("STRESS_TO_HIT_BASE_PENALTY") + dist * cfg("STRESS_TO_HIT_DISTANCE_MODIFIER"))
        + m:getMoodleLevel(MoodleType.TIRED) * cfg("TIRED_TO_HIT_BASE_PENALTY")
        + m:getMoodleLevel(MoodleType.ENDURANCE) * cfg("ENDURANCE_TO_HIT_BASE_PENALTY")
        + m:getMoodleLevel(MoodleType.DRUNK) * (cfg("DRUNK_TO_HIT_BASE_PENALTY") + dist * cfg("DRUNK_TO_HIT_DISTANCE_MODIFIER")))
        * (tonumber(SandboxVars.FirearmMoodleMultiplier) or 1)
end

--- The server's distance for a hit roll (`CombatManager.getHitDistanceSquared`).
function Fire.distance(owner, target)
    local dx, dy = owner:getX() - target:getX(), owner:getY() - target:getY()
    local dz = (math.floor(owner:getZ()) - math.floor(target:getZ())) * 3
    return math.sqrt(dx * dx + dy * dy + dz * dz)
end

--- Vanilla's hit chance (`calculateHitChanceData`, ranged, shooter not in a vehicle), with the minimum the game had
--- before the shot (`minimum`, as this file raised the live one). Checked against the Java in tests/firearm_test.py.
function Fire.hitChance(owner, weapon, target, dist, minimum)
    local maximum = cfg("MAXIMUM_TO_HIT_CHANCE")
    local chance = math.min(weapon:getHitChance(), cfg("MAXIMUM_START_TO_HIT_CHANCE"))
    chance = chance + weapon:getAimingPerkHitChanceModifier() * owner:getPerkLevel(Perks.Aiming)
    local max = weapon:getMaxSightRange(owner)
    local min = weapon:getMinSightRange(owner)
    local prone = target:isProne()
    local delay = math.max(0, owner:getAimingDelay())
    chance = chance + math.max(distanceModifierSightless(dist, prone) - aimDelayPenaltySightless(delay, dist),
        distanceModifier(dist, min, max) - aimDelayPenalty(delay, dist, min, max))
    local combined = movePenalty(owner, dist)
    if instanceof(target, "IsoPlayer") then   -- players and animals (single player only; see the header)
        local vehicle = target:getVehicle()
        if vehicle then
            chance = chance - math.abs(vehicle:getCurrentSpeedKmHour()) * 2
        elseif target:isSprinting() then
            chance = chance - cfg("SPRINTING_TO_HIT_PENALTY")
        elseif target:isRunning() then
            chance = chance - cfg("RUNNING_TO_HIT_PENALTY")
        elseif target:isPlayerMoving() then
            chance = chance - cfg("MOVING_TO_HIT_PENALTY")
        end
    end
    if owner:hasTrait(CharacterTrait.MARKSMAN) then
        chance = chance + cfg("MARKSMAN_TRAIT_TO_HIT_BONUS")
    end
    combined = combined + painPenalty(owner)
    combined = combined + weatherPenalty(owner, weapon, target:getSquare(), dist)
    combined = combined + moodlesPenalty(owner, dist)
    if SandboxVars.FirearmHeadGearEffect ~= false then
        combined = combined + maximum - maximum / owner:getWornItemsVisionModifier()
    end
    local pb = cfg("POINT_BLANK_DISTANCE")
    if dist < pb then
        local base = dist / pb
        combined = combined * (base / 5)
        chance = chance / (base * 1.1)
    end
    chance = chance - combined
    return math.max(minimum, math.min(maximum, javaInt(chance)))
end

-- the shot being processed: { owner, minimum (the game's), share, mode }; cleared on the next tick
local shot = nil
-- combat config values changed for the hit being processed: { key = value before }
local scaled = nil

local function unscale()
    if not scaled then return end
    local config = getCombatConfig()
    for key, value in pairs(scaled) do config:set(CombatConfigKey[key], value) end
    scaled = nil
end

local function scale(factor)
    local config = getCombatConfig()
    scaled = {}
    for _, key in ipairs({ "BASE_WEAPON_DAMAGE_MULTIPLIER", "WEAPON_LEVEL_DAMAGE_MULTIPLIER_INCREMENT" }) do
        local before = config:get(CombatConfigKey[key])
        scaled[key] = before
        config:set(CombatConfigKey[key], before * factor)
    end
end

local function endShot()
    unscale()
    if shot then
        getCombatConfig():set(CombatConfigKey.MINIMUM_TO_HIT_CHANCE, shot.minimum)
        shot = nil
    end
end

local function onSwingHitPoint(owner, weapon)
    endShot()
    if isServer() then return end
    if not (owner and weapon and instanceof(owner, "IsoPlayer") and instanceof(weapon, "HandWeapon")) then return end
    if not owner:isLocalPlayer() or not weapon:isAimedFirearm() or owner:getVehicle() then return end
    local share = Fire.share()
    local mode = Fire.damageChanceMode()
    if share <= 0 or mode == 1 then return end
    local config = getCombatConfig()
    shot = { owner = owner, weapon = weapon, share = share, mode = mode,
        minimum = config:get(CombatConfigKey.MINIMUM_TO_HIT_CHANCE) }
    config:set(CombatConfigKey.MINIMUM_TO_HIT_CHANCE, 100)
end

local warned = false

local function onWeaponHitCharacter(wielder, target, weapon, damage)
    unscale()
    if not shot or wielder ~= shot.owner or weapon ~= shot.weapon or not target then return end
    local zombie = instanceof(target, "IsoZombie")
    if not zombie and isClient() then return end   -- the server rolls players and animals
    if zombie and shot.share >= 1 then return end  -- 100 %: every hit lands, as in 42.21

    local ok, chance = pcall(Fire.hitChance, wielder, weapon, target, Fire.distance(wielder, target), shot.minimum)
    if not ok then
        if not warned then
            warned = true
            print("[GunsOfTien] minimum firearm damage: hit chance failed, hits land in full: " .. tostring(chance))
        end
        return
    end
    if ZombRand(100) <= chance then return end   -- vanilla's roll: Rand.Next(100) <= hitChance

    if not zombie then
        if shot.mode == 2 then
            target:setAvoidDamage(true)          -- Zombies only: a failed roll misses
        else
            scale(0)                             -- All types of target: a hit for no damage
        end
        return
    end
    local factor = shot.share
    if wielder:isCriticalHit() then
        factor = factor / math.max(2, weapon:getCriticalDamageMultiplier())
    end
    scale(factor)
end

Events.OnWeaponSwingHitPoint.Add(onSwingHitPoint)
Events.OnWeaponHitCharacter.Add(onWeaponHitCharacter)
Events.OnTick.Add(function()
    if shot or scaled then endShot() end
end)
