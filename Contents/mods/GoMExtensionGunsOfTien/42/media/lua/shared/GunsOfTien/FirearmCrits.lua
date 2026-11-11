--[[
    Guns of Tien -- firearm critical hits per target (user, 2026-11-11; sandbox FirearmCritRule / FirearmCritLead).

    What changed in Build 42.22 (42.21 and 42.22.2 Java compared, CombatManager / IsoPlayer):
    - 42.21 rolled a gun's crit once per target: `CombatManager.processHit` (~2927) ran
      `setCriticalHit(Rand.Next(100) < calculateCritChance(target))` for every bullet or pellet that hit (hit reaction
      SHOT), before that target's damage. 42.22 removed that line (and the one in `IsoPlayer.hitConsequences`), so
      only the roll in `pressedAttack` (`CombatManager.isCriticalHit` ~3185, one per trigger pull, for the closest
      target) is left: a shot hitting several targets (shotgun pellets, piercing rounds) crits on all of them or none.
    - What the flag does to each target, in `attackCollisionCheck`'s per-target order (~1050-1240):
      1. `getHitDamage` → `processHit` → `resolveHitReaction` (~2911): with the flag set, a head hit reaction (and so
         `applyRangeHitLocationDamage`'s head x3) for a target that is not the ballistics camera target (the one under
         the reticle takes the body part it was aimed at instead);
      2. `target:Hit` → Lua `OnWeaponHitCharacter(wielder, target, weapon, damage)` → `processHitDamage` (crit x
         max(2, CritDmgMultiplier), IsoGameCharacter ~6037) → zombie `hitConsequences` (knocked down on a crit, ~4206).
      No Lua event fires between one target's step 2 and the next target's step 1, so a per-target roll can only be
      made in step 2: it decides that target's crit damage and knockdown, and the next target's head reaction follows
      it. The first target of a shot keeps the trigger-pull roll, so a shot hitting one target is unchanged.
    - Who rolls (42.22 "damage calculated on the server"): a hit on a zombie is rolled by the shooter's client and the
      server takes its damage as sent (`Hit.process`, remote damage 0..200); hits on players and animals are rolled
      by the server, whose `PlayerHitPacket.processServer` sets one crit for the batch (the client's for a zombie as
      closest target, else its own `isCriticalHit` roll) and then fires `OnWeaponSwingHitPoint` for aimed firearms.
      So this file runs on both: a client for its local players' zombie hits, the server for player and animal
      targets, single player for everything.

    Rules (FirearmCritRule, labelled Default / Old / Enhanced): 1 = Build 42.22 (nothing done), 2 = one roll per
    target at `calculateCritChance(target)` as 42.21, 3 = per target but led by the trigger-pull roll: with lead k
    (FirearmCritLead / 100) and the target's
    chance p, a crit pull gives p + (1 - p) k, no crit p (1 - k). The average stays p for any k; k = 0 is rule 2,
    k = 1 is rule 1. Weapons tagged NoCriticals never crit (as `isCriticalHit`).
    Read live: both options are read at every hit.
--]]

GunsOfTien_FirearmCrits = GunsOfTien_FirearmCrits or {}
local Crits = GunsOfTien_FirearmCrits

Crits.RULE_PER_SHOT = 1
Crits.RULE_PER_TARGET = 2
Crits.RULE_LED = 3

local function vars()
    return SandboxVars and SandboxVars.GunsOfTien
end

--- The rule chosen in the sandbox (1 when unknown).
function Crits.rule()
    local v = vars()
    local rule = v and tonumber(v.FirearmCritRule)
    if rule == Crits.RULE_PER_TARGET or rule == Crits.RULE_LED then return rule end
    return Crits.RULE_PER_SHOT
end

--- How far later targets follow the trigger-pull roll under rule 3, 0..1.
function Crits.lead()
    local v = vars()
    local lead = v and tonumber(v.FirearmCritLead) or 50
    if lead < 0 then lead = 0 elseif lead > 100 then lead = 100 end
    return lead / 100
end

--- A target's own crit chance (0..100), as 42.21's per-target roll had it.
function Crits.chance(wielder, weapon, target)
    if weapon:hasTag(ItemTag.NO_CRITICALS) then return 0 end
    local chance = wielder:calculateCritChance(target)
    if chance < 0 then return 0 elseif chance > 100 then return 100 end
    return chance
end

--- The chance led by the trigger pull: p + (100 - p) k after a crit pull, p (1 - k) after none.
function Crits.led(chance, pullCrit, lead)
    if pullCrit then return chance + (100 - chance) * lead end
    return chance * (1 - lead)
end

-- wielder -> { weapon, pull, hits } for the shot being processed right now; cleared on the next tick
local attacks = {}
local pending = false

--- Whether this side rolls that target's damage (see the header).
local function rollsHere(wielder, target)
    if isServer() then return not instanceof(target, "IsoZombie") end
    if isClient() then return wielder:isLocalPlayer() and instanceof(target, "IsoZombie") end
    return true
end

local function onSwingHitPoint(owner, weapon)
    if not (owner and weapon and instanceof(owner, "IsoPlayer") and instanceof(weapon, "HandWeapon")) then return end
    if not weapon:isAimedFirearm() then return end
    if isClient() and not owner:isLocalPlayer() then return end
    attacks[owner] = { weapon = weapon, pull = owner:isCriticalHit(), hits = 0 }
    pending = true
end

local function onWeaponHitCharacter(wielder, target, weapon, damage)
    local attack = wielder and attacks[wielder]
    if not attack or attack.weapon ~= weapon or not target then return end
    local rule = Crits.rule()
    if rule == Crits.RULE_PER_SHOT then return end
    if not rollsHere(wielder, target) then return end

    attack.hits = attack.hits + 1
    if attack.hits == 1 then
        -- the first target keeps the trigger pull's roll (and its head reaction, made with it)
        wielder:setCriticalHit(attack.pull)
        return
    end
    local chance = Crits.chance(wielder, weapon, target)
    if rule == Crits.RULE_LED then
        chance = Crits.led(chance, attack.pull, Crits.lead())
    end
    wielder:setCriticalHit(ZombRandFloat(0, 100) < chance)
end

local function onTick()
    if not pending then return end
    attacks = {}
    pending = false
end

Events.OnWeaponSwingHitPoint.Add(onSwingHitPoint)
Events.OnWeaponHitCharacter.Add(onWeaponHitCharacter)
Events.OnTick.Add(onTick)
