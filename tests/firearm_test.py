"""Runs the real FirearmCrits.lua and FirearmMinimumDamage.lua in a real Lua (lupa 5.5) against mocks.

- Hit chance: FirearmMinimumDamage's copy of `CombatManager.calculateHitChanceData` gives the numbers worked out by
  hand from the 42.22.2 Java (a Hunting Rifle: hit chance 50, +4 per Aiming level, with the x8 scope's 15-22 tiles
  and with iron sights' 2-10, settled and with 40 aim delay; combat config defaults), plus the penalties it adds.
- Minimum damage: the shot's minimum hit chance is 100 while it runs and back on the next tick; a failed roll on a
  zombie scales the weapon damage multipliers to the share (divided by the crit multiplier on a crit) for that one
  hit; 100 % never rolls zombies; 0 % or "Firearms Use Damage Chance" Disabled do nothing; in single player a failed
  roll on a player or animal misses (Zombies only) or does no damage (All types); an MP client leaves them alone.
- Crits: Default / Old / Enhanced per-target rates on 9-pellet shots.

Setup once: py -m pip install --target tests/.lupa lupa      Run: py tests/firearm_test.py
Breaks (each should print FAILED): nopointblank, nocritdivide, nominrestore."""
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parent
sys.path.insert(0, str(here / '.lupa'))
import lupa

LUA = repo / 'Contents/mods/GoMExtensionGunsOfTien/42/media/lua/shared/GunsOfTien'
dmg = (LUA / 'FirearmMinimumDamage.lua').read_bytes().decode('utf-8').replace('\r\n', '\n')
crits = (LUA / 'FirearmCrits.lua').read_bytes().decode('utf-8').replace('\r\n', '\n')

m = sys.argv[1] if len(sys.argv) > 1 else ''
if m == 'nopointblank':
    dmg = dmg.replace('chance = chance / (base * 1.1)', '')
if m == 'nocritdivide':
    dmg = dmg.replace('factor = factor / math.max(2, weapon:getCriticalDamageMultiplier())', '')
if m == 'nominrestore':
    dmg = dmg.replace('getCombatConfig():set(CombatConfigKey.MINIMUM_TO_HIT_CHANCE, shot.minimum)', '')


def hand(A, d, delay, scope):
    """The 42.22.2 Java worked by hand (no penalties): see CombatManager ~2504-2584, 2674-2820."""
    import math
    PB = 3.5
    def sightless(d):
        if d > PB: return (PB - d) * (15 + (PB - d) * -0.7)
        return (PB - d) / PB * 40 if d < PB else 0
    def dsl(a, d):
        if d < PB: a *= d / PB
        elif d > PB: a *= 1 + (d - PB * 0.1)
        return a
    def dm(d, mn, mx):
        if d < mn: return (d - mn) * (4 + (d - mn) * -0.3) if d > PB else 0
        if d > mx: return -((d - mx) * (4 + (d - mx) * 0.3))
        s = (mx - mn) * 0.5
        return 15 * math.exp(-(d - (mn + s)) ** 2 / (2 * ((mx - mn) / 7)) ** 2)
    def adp(a, d, mn, mx):
        if mn > -1 and mn <= d <= mx:
            s = (mx - mn) * 0.5; a *= 1 - (1 - abs(d - (mn + s)) / s) * 0.25
        elif d > mx: a *= 1 + (d - mx) * 0.1
        return a * (d / PB if d < PB else 1)
    h = min(50, 95) + 4 * A
    mn = scope[0] * (1 - A / 30); mx = scope[1] * (1 + A / 30)
    h += max(sightless(d) - dsl(delay, d), dm(d, mn, mx) - adp(delay, d, mn, mx))
    if d < PB:
        h /= d / PB * 1.1
    return max(5, min(100, int(h)))


cases = []
for scope in ((15, 22), (2, 10)):
    for A in (0, 5, 10):
        for delay in (0, 40):
            for d in (2, 5, 10, 15, 20, 25, 30, 35):
                cases.append((A, d, delay, scope[0], scope[1], hand(A, d, delay, scope)))

lua = lupa.LuaRuntime()
g = lua.globals()
g.dmgsrc = dmg
g.critsrc = crits
g.cases = lua.table_from([lua.table_from(c) for c in cases])
result = lua.execute(r'''
local out = {}
local function check(name, ok) out[#out + 1] = name .. "=" .. tostring(ok == true) end
math.randomseed(3)

-- game mocks ---------------------------------------------------------------------------------------------
local defaults = { BASE_WEAPON_DAMAGE_MULTIPLIER = 0.3, WEAPON_LEVEL_DAMAGE_MULTIPLIER_INCREMENT = 0.1,
    POINT_BLANK_DISTANCE = 3.5, LOW_LIGHT_THRESHOLD = 0.75, LOW_LIGHT_TO_HIT_MAXIMUM_PENALTY = 50,
    POINT_BLANK_TO_HIT_MAXIMUM_BONUS = 40, POINT_BLANK_DROP_OFF_TO_HIT_PENALTY = 0.7,
    OPTIMAL_RANGE_TO_HIT_MAXIMUM_BONUS = 15, OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY = 4,
    OPTIMAL_RANGE_DROP_OFF_TO_HIT_PENALTY_INCREMENT = 0.3, MINIMUM_TO_HIT_CHANCE = 5, MAXIMUM_START_TO_HIT_CHANCE = 95,
    MAXIMUM_TO_HIT_CHANCE = 100, MOVING_TO_HIT_PENALTY = 5, RUNNING_TO_HIT_PENALTY = 15, SPRINTING_TO_HIT_PENALTY = 25,
    MARKSMAN_TRAIT_TO_HIT_BONUS = 20, ARM_PAIN_TO_HIT_MODIFIER = 0.1, PANIC_TO_HIT_BASE_PENALTY = 4,
    PANIC_TO_HIT_DISTANCE_MODIFIER = 0.5, STRESS_TO_HIT_BASE_PENALTY = 4, STRESS_TO_HIT_DISTANCE_MODIFIER = 0.5,
    TIRED_TO_HIT_BASE_PENALTY = 2.5, ENDURANCE_TO_HIT_BASE_PENALTY = 2.5, DRUNK_TO_HIT_BASE_PENALTY = 4,
    DRUNK_TO_HIT_DISTANCE_MODIFIER = 0.5, WIND_INTENSITY_TO_HIT_PENALTY = 6, WIND_INTENSITY_TO_HIT_AIMING_MODIFIER = 0.2,
    WIND_INTENSITY_TO_HIT_MINIMUM_MARKSMAN_MODIFIER = 0.6, WIND_INTENSITY_TO_HIT_MAXIMUM_MARKSMAN_MODIFIER = 1,
    RAIN_INTENSITY_TO_HIT_DISTANCE_MODIFIER = 0.5, FOG_INTENSITY_DISTANCE_MODIFIER = 10,
    POINT_BLANK_MAXIMUM_DISTANCE_MODIFIER = 1, SIGHTLESS_TO_HIT_BASE_DISTANCE = 15, SIGHTLESS_TO_HIT_PRONE_MODIFIER = 2,
    SIGHTLESS_AIM_DELAY_TO_HIT_DISTANCE_MODIFIER = 0.1 }
CombatConfigKey = {}
for k in pairs(defaults) do CombatConfigKey[k] = k end
local config = {}
for k, v in pairs(defaults) do config[k] = v end
local configObj = { get = function(_, k) return config[k] end, set = function(_, k, v) config[k] = v end }
function getCombatConfig() return configObj end

local handlers = {}
Events = setmetatable({}, { __index = function(t, name)
    local e = { Add = function(f) handlers[name] = handlers[name] or {}; table.insert(handlers[name], f) end }
    rawset(t, name, e)
    return e
end })
local function fire(name, ...) for _, f in ipairs(handlers[name] or {}) do f(...) end end
local server, client = false, false
function isServer() return server end
function isClient() return client end
function instanceof(o, c) return o ~= nil and type(o) == "table" and o.classes ~= nil and o.classes[c] == true end
function ZombRand(n) return math.random(0, n - 1) end
function ZombRandFloat(a, b) return a + math.random() * (b - a) end
Perks = { Aiming = "Aiming", Nimble = "Nimble" }
MoodleType = { PANIC = "PANIC", STRESS = "STRESS", TIRED = "TIRED", ENDURANCE = "ENDURANCE", DRUNK = "DRUNK" }
CharacterTrait = { MARKSMAN = "MARKSMAN" }
ItemTag = { THERMAL = "thermal", NO_CRITICALS = "nocrit" }
BodyPartType = { Hand_L = 0, UpperArm_R = 5, ToIndex = function(i) return i end }
local climate = { wind = 0, rain = 0, fog = 0 }
function getClimateManager()
    return { getWindIntensity = function() return climate.wind end, getRainIntensity = function() return climate.rain end,
        getFogIntensity = function() return climate.fog end }
end
SandboxVars = { GunsOfTien = {}, FirearmUseDamageChance = 2, FirearmWeatherMultiplier = 1, FirearmMoodleMultiplier = 1,
    FirearmHeadGearEffect = true }

local square = { outside = false, light = 1 }
function square.isOutside() return square.outside end
function square.getLightLevel() return square.light end

local function newPlayer()
    local p = { classes = { IsoPlayer = true, IsoGameCharacter = true }, aiming = 0, delay = 0, moving = 0, pain = 0,
        moodles = {}, marksman = false, vision = 1, crit = false, x = 0, y = 0 }
    function p.isLocalPlayer() return true end
    function p.getPerkLevel(_, perk) return perk == "Aiming" and p.aiming or 0 end
    function p.getAimingDelay() return p.delay end
    function p.getBeenMovingFor() return p.moving end
    function p.hasTrait(_, t) return t == "MARKSMAN" and p.marksman end
    function p.getBodyDamage() return { getBodyParts = function() return { get = function()
        return { getPain = function() return p.pain end } end } end } end
    function p.getMoodles() return { getMoodleLevel = function(_, t) return p.moodles[t] or 0 end } end
    function p.getCharacterTraits() return { getTraitWeatherPenaltyModifier = function() return 1 end } end
    function p.getWornItemsVisionModifier() return p.vision end
    function p.getPlayerNum() return 0 end
    function p.getVehicle() return nil end
    function p.getX() return p.x end
    function p.getY() return p.y end
    function p.getZ() return 0 end
    function p.isCriticalHit() return p.crit end
    function p.setCriticalHit(_, b) p.crit = b end
    function p.calculateCritChance() return 30 end
    return p
end
local function newGun(base, mn, mx)
    local w = { classes = { HandWeapon = true }, mn = mn, mx = mx }
    function w.isAimedFirearm() return true end
    function w.getHitChance() return base end
    function w.getAimingPerkHitChanceModifier() return 4 end
    function w.getMinSightRange(_, o) return w.mn * (1 - o.aiming / 30) end
    function w.getMaxSightRange(_, o) return w.mx * (1 + o.aiming / 30) end
    function w.getActiveSight() return nil end
    function w.getLowLightBonus() return 0 end
    function w.getCriticalDamageMultiplier() return 5 end
    function w.hasTag() return false end
    return w
end
local function newZombie(d)
    local z = { classes = { IsoZombie = true, IsoGameCharacter = true }, x = d, y = 0, prone = false }
    function z.getX() return z.x end
    function z.getY() return z.y end
    function z.getZ() return 0 end
    function z.isProne() return z.prone end
    function z.getSquare() return square end
    return z
end

assert(load(critsrc))()
assert(load(dmgsrc))()
local Fire = GunsOfTien_FirearmMinimumDamage

-- hit chance against the Java worked by hand -------------------------------------------------------------
local bad = 0
for i = 1, #cases do
    local c = cases[i]
    local p, w, z = newPlayer(), newGun(50, c[4], c[5]), newZombie(c[2])
    p.aiming, p.delay = c[1], c[3]
    local got = Fire.hitChance(p, w, z, Fire.distance(p, z), 5)
    if got ~= c[6] then
        bad = bad + 1
        if bad <= 5 then out[#out + 1] = string.format("  mismatch A=%d d=%d delay=%d scope=%d-%d: %s vs %s",
            c[1], c[2], c[3], c[4], c[5], tostring(got), tostring(c[6])) end
    end
end
check("hitChanceMatchesJava(" .. #cases .. ")", bad == 0)

-- penalties
local p, w, z = newPlayer(), newGun(50, 15, 22), newZombie(20)
p.aiming = 10
local clean = Fire.hitChance(p, w, z, 20, 5)
p.marksman = true
check("marksmanPlus20", Fire.hitChance(p, w, z, 20, 5) == math.min(100, clean + 20))
p.marksman = false
p.aiming = 0
local base0 = Fire.hitChance(p, w, z, 20, 5)
square.light = 0.375
check("darknessMinus25", Fire.hitChance(p, w, z, 20, 5) == math.max(5, base0 - 25))
square.light = 1
p.moodles.PANIC = 2
check("panicMinus28At20", Fire.hitChance(p, w, z, 20, 5) == math.max(5, base0 - 28))
p.moodles.PANIC = nil
p.vision = 2
check("headgearHalvesVision", Fire.hitChance(p, w, z, 20, 5) == math.max(5, base0 - 50))
p.vision = 1
square.outside, climate.fog = true, 0.1
check("fogMinus20At20", Fire.hitChance(p, w, z, 20, 5) == math.max(5, base0 - 20))
square.outside, climate.fog = false, 0

-- minimum damage during a shot ----------------------------------------------------------------------------
local function shoot(share, targets, opts)
    opts = opts or {}
    SandboxVars.GunsOfTien.FirearmMinimumDamage = share
    local shooter, gun = opts.shooter or newPlayer(), opts.gun or newGun(50, 15, 22)
    shooter.crit = opts.crit or false
    fire("OnWeaponSwingHitPoint", shooter, gun)
    local seen = {}
    for _, t in ipairs(targets) do
        t.avoid = false
        function t.setAvoidDamage(_, b) t.avoid = b end
        fire("OnWeaponHitCharacter", shooter, t, gun, 1)
        seen[#seen + 1] = { min = config.MINIMUM_TO_HIT_CHANCE, base = config.BASE_WEAPON_DAMAGE_MULTIPLIER,
            inc = config.WEAPON_LEVEL_DAMAGE_MULTIPLIER_INCREMENT, avoid = t.avoid }
    end
    fire("OnTick")
    return seen
end

-- aiming 0 at 30 tiles with the x8: chance 5 -> about 94 % fail
local far = newZombie(30)
local fails, scaledOk, n = 0, true, 4000
for i = 1, n do
    local s = shoot(25, { far })[1]
    if s.min ~= 100 then scaledOk = false end
    if math.abs(s.base - 0.3) > 1e-9 then
        fails = fails + 1
        if math.abs(s.base - 0.075) > 1e-9 or math.abs(s.inc - 0.025) > 1e-9 then scaledOk = false end
    end
end
check("minimumForcedDuringShot", scaledOk)
check("failRateIsVanillas", math.abs(fails / n - 0.94) < 0.02)
check("everythingBackAfterTick", config.MINIMUM_TO_HIT_CHANCE == 5 and config.BASE_WEAPON_DAMAGE_MULTIPLIER == 0.3
    and config.WEAPON_LEVEL_DAMAGE_MULTIPLIER_INCREMENT == 0.1)

-- a second hit puts the first hit's scaling back before deciding its own
local near = newZombie(2)
local twoOk = true
for i = 1, 300 do
    local s = shoot(25, { far, near })
    if math.abs(s[2].base - 0.3) > 1e-9 then twoOk = false end   -- 2 tiles: chance 100, never scaled
end
check("nextHitUnscaled", twoOk)

-- a crit divides its multiplier out
local critOk, critSeen = true, 0
for i = 1, 500 do
    local s = shoot(50, { far }, { crit = true })[1]
    if math.abs(s.base - 0.3) > 1e-9 then
        critSeen = critSeen + 1
        if math.abs(s.base - 0.3 * 0.5 / 5) > 1e-9 then critOk = false end
    end
end
check("critMultiplierDividedOut", critOk and critSeen > 0)

local all = true
for i = 1, 300 do
    local s = shoot(100, { far })[1]
    if s.min ~= 100 or math.abs(s.base - 0.3) > 1e-9 then all = false end
end
check("hundredLandsEverything", all)

local off = shoot(0, { far })[1]
check("zeroDoesNothing", off.min == 5 and off.base == 0.3)
SandboxVars.FirearmUseDamageChance = 1
local dis = shoot(50, { far })[1]
check("disabledDoesNothing", dis.min == 5 and dis.base == 0.3)
SandboxVars.FirearmUseDamageChance = 2

local car = newPlayer(); car.getVehicle = function() return {} end
local veh = shoot(50, { far }, { shooter = car })[1]
check("vehicleLeftToVanilla", veh.min == 5)

-- players and animals
local function animal(d)
    local a = newZombie(d)
    a.classes = { IsoPlayer = true, IsoAnimal = true, IsoGameCharacter = true }
    function a.getVehicle() return nil end
    function a.isSprinting() return false end
    function a.isRunning() return false end
    function a.isPlayerMoving() return false end
    return a
end
local deer = animal(30)
local missed = 0
for i = 1, 500 do if shoot(50, { deer })[1].avoid then missed = missed + 1 end end
check("spAnimalFailMisses", missed > 400)
SandboxVars.FirearmUseDamageChance = 3
local zeroed = 0
for i = 1, 500 do
    local s = shoot(50, { deer })[1]
    if s.base == 0 and not s.avoid then zeroed = zeroed + 1 end
end
check("spAnimalAllTypesNoDamage", zeroed > 400)
SandboxVars.FirearmUseDamageChance = 2
client = true
local mpOk = true
for i = 1, 200 do
    local s = shoot(50, { deer })[1]
    if s.avoid or s.base ~= 0.3 then mpOk = false end
end
check("mpClientLeavesAnimals", mpOk)
client = false
server = true
check("serverDoesNothing", shoot(50, { far })[1].min == 5)
server = false

-- crits: Default / Old / Enhanced on 9-pellet shots
SandboxVars.GunsOfTien.FirearmMinimumDamage = 0
local function critRates(rule, lead)
    SandboxVars.GunsOfTien.FirearmCritRule, SandboxVars.GunsOfTien.FirearmCritLead = rule, lead
    local p, w, z = newPlayer(), newGun(50, 15, 22), newZombie(5)
    local later, laterPull, nPull, laterNo, nNo = 0, 0, 0, 0, 0
    local N = 20000
    for i = 1, N do
        local pull = math.random(0, 99) < 30
        p.crit = pull
        fire("OnWeaponSwingHitPoint", p, w)
        for k = 1, 9 do
            fire("OnWeaponHitCharacter", p, z, w, 1)
            if k > 1 then
                if p.crit then later = later + 1 end
                if pull then nPull = nPull + 1; if p.crit then laterPull = laterPull + 1 end
                else nNo = nNo + 1; if p.crit then laterNo = laterNo + 1 end end
            end
        end
        fire("OnTick")
    end
    return 100 * later / (8 * N), 100 * laterPull / nPull, 100 * laterNo / nNo
end
local a, b, c = critRates(1, 50)
check("critDefaultAllOrNone", b == 100 and c == 0)
a, b, c = critRates(2, 50)
check("critOldIndependent", math.abs(b - 30) < 1.5 and math.abs(c - 30) < 1.5)
a, b, c = critRates(3, 50)
check("critEnhancedLed", math.abs(b - 65) < 1.5 and math.abs(c - 15) < 1.5 and math.abs(a - 30) < 1.5)

return table.concat(out, "\n")
''')

print(result)
bad = [line for line in result.split('\n') if line.endswith('=false')]
if bad:
    print('FAILED:', bad)
    sys.exit(1)
print('OK')
