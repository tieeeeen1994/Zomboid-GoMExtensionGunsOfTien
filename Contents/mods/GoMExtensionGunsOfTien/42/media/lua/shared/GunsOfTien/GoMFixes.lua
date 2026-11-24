--[[
    Guns of Tien -- two Guns of Marz registrations that miss their target (found 2026-10-19 while fixing its tooltips)

    - The Karabiner 98k bayonet fits no gun. Its attachment's item script mounts on the same sixteen guns as the
      other bayonets, but Registries/Bayonets.lua leaves "MarzGuns.K98_Bayonet_Attachment" out of
      Bayonet.RegisterMountableWeapon, and Gunworks' Bayonet.CanAttachBayonet asks only that registry. It is added
      to every gun that takes the M5 bayonet.
    - The overpressured 5.56's automatic fire spread penalty never applies: Registries/RPM.lua registers it as
      "MarzGuns.556x45_Bullet_Overpressured", but the round is SWMG.556x45_Bullet_Overpressured, and Gunworks'
      RateOfFire.getSpreadProfile looks modifiers up by the round's own full type. It is registered under that too.
    GoM's lua/shared loads before ours, so its registrations are in place here.

    Opening and packing ammo boxes can be done while walking again (42.22, 2026-11-10). Since 42.22,
    ISHandcraftAction:new makes a craft walkable only when its recipe has the CanBeDoneWhileWalking tag. The old
    "canWalk = true" key still loads (CraftRecipe:isCanWalk()), but only the crafting window reads it. Vanilla moved
    its own recipes to the tag, but GoM's open / pack box, carton and crate recipes only say canWalk. So walking
    stopped them, and because the craft was at the front of the queue, the whole queue was cleared with it (Tien's
    Ammo Bags' reload with box opening ended). Our own recipes carry the tag in their scripts. At every world load,
    every recipe that says canWalk without the tag gets it, added to getModTags(), the live list behind getTags(),
    which is what ISHandcraftAction:new reads. Recipe scripts are rebuilt at every world load, and OnLoadMapZones
    comes after that on client, server and single player.

    A Gunworks rack on a server is timed at the wrong reload speed (2026-11-11). Its ISRackFirearm:serverStart
    (Hooks/ReloadAnimHooks.lua) works out the rack's length as the profile's rack seconds / the character's
    ReloadSpeed variable, but sets the rack's own speed (self:initVars() = setReloadSpeed(chr, true): 0.8 + 0.04 x
    Reloading) only after that, so it reads the speed the magazine insert before it left (setReloadSpeed(chr, false):
    0.8 + 0.10 x Reloading, minus panic). Its eject, insert, load, unload and opening-stroke serverStarts set the
    speed first. The owner's client plays the clip at the rack's speed, so with any Reloading skill the server ends
    the rack early (77% of the clip at Reloading 5, 67% at 10). It chambers the round at 100 ms and its Done reaches
    the client before the clip's rackEnd, the event that clears Gunworks' bolt flag (modData.gunworksBoltOpen, set
    by rackStart). The gun is then loaded with its "bolt open", and every trigger pull says "Chamber is open, close
    it before firing." until a full rack plays. It shows on racks whose rackEnd comes late in the clip: GoM's old
    MP5 nodes (our UMPs, Vector .45 / CRB, UZI_2H: rackEnd at 0.79, from about Reloading 4) and left_handle_load
    (SCARs: 0.70, aimed 0.76). Setting the rack's speed before Gunworks' serverStart runs fixes the timing for
    every gun with a Gunworks reload profile (Gunworks' own initVars sets the same value again). Single player never
    runs serverStart.

    A rack cut short leaves the bolt "open" (2026-11-24, reported on the AUG HBAR, whose timings are right: its
    durations are GoM's clip lengths and its rackEnd comes at 0.40 of the clip, 0.49 aimed). Gunworks' bolt flag
    is set by the rack clip's rackStart and cleared only by its rackEnd, and nothing clears it when the rack ends
    between the two. The flag is the owner's alone: syncHandWeaponFields sends nothing from a client (42.22
    LuaManager: only when GameServer.server), and the server's own weapon syncs replace the client's parts and mod
    data with its copy, where a full rack is always closed. So a late server never opens the bolt; what does is
    the rack ending inside the stroke:
    - Tien's Skill Mastery's Running Reload (the report): starting or stopping a run restarts the rack clip (the
      walking and the running copies are separate nodes) while the server's rack timer runs on, so its Done lands
      after the second rackStart and before the rackEnd;
    - a trigger pull (vanilla's attackHook clears the action queue on every pull), sprinting without that
      signature, a hit.
    The gun then refuses to fire ("Chamber is open, close it before firing.") until the server's next weapon sync
    or a whole rack, each further pull cancels the rack that would close it, and an empty gun cannot be racked at
    all (canRack wants a round; only guns with reload rules may close an open bolt). Every full rack node of GoM
    and Gunworks has both events (only the opening strokes of two-stroke racks, which carry gunworksRackPhase, have
    rackStart alone), and Gunworks' server already records any rack but an opening stroke as leaving the bolt
    closed. So when a full rack stops or performs with the flag still set, the bolt is closed the way its rackEnd
    would have (Animations.rackAction: parts and flag). Single player too.

    A closing stroke that performs counts too (2026-11-24, after a report on GoM's 5.56 AR-15s). Since GoM's
    2026-11-23 update its M16s, M4A1, CAR-15, XM177, AR15, SKS and M1 Garand hold the bolt open on the last round
    (MarzWeapons/Hooks/LockOpenWeapons.lua sets the flag in onShoot, on the server too, where Gunworks never moves
    the bolt part: the server's next weapon sync leaves the owner with a closed bolt and the flag), and an empty
    reload ends with the bolt catch slap, a closing stroke (gunworksRackPhase "close", RackAR15Slap: rackStart at
    0.02, rackEnd at 0.26). The first version here skipped every stroke with a phase, so a slap whose Done came
    before its rackEnd kept the flag. Only an opening stroke leaves the bolt open (Gunworks' own rule since its
    2026-11-24 update: ISRackFirearm:complete closes for any phase but "open", but on a server its flag is already
    off by then, so nothing is sent). A closing stroke that is stopped is left alone: Gunworks' rules still hold
    the gun open (ReloadRules.openedBolts, cleared only when the stroke performs), and the next rack closes it.

    Three more holes around the flag, closed the same day (an audit of every way it is set, cleared and synced):
    - Held open, drawn closed (multiplayer, GoM alone, after every last round): a client sends a PlayerHit packet
      for each shot (42.22 CombatManager ~1282, a miss lists the square), so the server runs onShoot too and
      LockOpenWeapons.lua sets its flag, but Animations.lockActionOpen returns at once on a server and the bolt
      part there stays MarzGuns.Bolt_Lock. Vanilla's onShoot ends with the weapon sync, which replaces the owner's
      parts and mod data: bolt drawn closed, flag on, the trigger dead with nothing but a tooltip row to say why
      ("the bolt is simultaneously locked and considered an open chamber"). On a server, a shot that newly sets
      the flag now also fits the open bolt part (the firing entry's, what the owner's client shows) before that
      sync goes out. syncHandWeaponFields is swapped for the length of the onShoot call, because a second sync
      after it could overtake the first (both are RELIABLE, unordered).
    - A flag nothing can clear: with a chamber, the flag on and no reload action running, a gun is really open
      only if its reload rules would answer a rack with a closing stroke (two-stroke guns, pumps, GoM's AR-15s
      while the chamber is empty). Any other gun has no way to close it but a full rack, which an empty gun
      without rules cannot start (canRack) and which throws a live round out of a chambered one (an AR-15 whose
      slap was cancelled after single player's rackBullet at its start; any gun saved with the flag before
      3.23.1). So canShoot, asked at each trigger pull, closes such a bolt first. Gunworks' and Hot Brass's
      attack hooks ask it before vanilla's clears the action queue, hence the test on isRacking / isLoading /
      isUnloading. Guns without a chamber (break actions, launchers, revolvers) are left alone: open is a real
      state for them, and a rack closes them (Gunworks' ISRackFirearm:complete). They are also the only guns whose
      load and unload open the action (the openWeapon / closeWeapon events are on GoM's revolver, break shotgun,
      M79 and M203 nodes and Gunworks' BreakAction ones, every one HaveChamber = false), so on a gun with a
      chamber the flag only ever comes from a rack or from the hold-open, and nothing GoM leaves open on purpose
      is closed here.
    - A rack that ended with the gun no longer in the hands kept the flag (the redraw needs the gun held): its
      parts and flag are now set without the redraw.
--]]

local ok, Bayonet = pcall(require, "WeaponSystems/Utils/Bayonet")
if ok and type(Bayonet) == "table" and Bayonet.BayonetMountableWeapons and Bayonet.RegisterMountableWeapon then
    local guns = {}
    for gun, accepted in pairs(Bayonet.BayonetMountableWeapons) do
        if accepted["MarzGuns.M5_Bayonet_Attachment"] and not accepted["MarzGuns.K98_Bayonet_Attachment"] then
            guns[#guns + 1] = gun
        end
    end
    if #guns > 0 then
        Bayonet.RegisterMountableWeapon("MarzGuns.K98_Bayonet_Attachment", guns)
    end
end

local okRof, RateOfFire = pcall(require, "WeaponSystems/Utils/RateOfFire")
if okRof and type(RateOfFire) == "table" and RateOfFire.SpreadPartModifiers then
    local wrong = RateOfFire.SpreadPartModifiers["MarzGuns.556x45_Bullet_Overpressured"]
    if wrong and not RateOfFire.SpreadPartModifiers["SWMG.556x45_Bullet_Overpressured"] then
        RateOfFire.RegisterSpreadAmmoModifier("SWMG.556x45_Bullet_Overpressured", wrong)
    end
end

local WALK_TAG = "CanBeDoneWhileWalking"

local function tagWalkableRecipes()
    local recipes = getScriptManager():getAllCraftRecipes()
    for i = 0, recipes:size() - 1 do
        local recipe = recipes:get(i)
        if recipe:isCanWalk() and not recipe:getTags():contains(WALK_TAG) then
            recipe:getModTags():add(WALK_TAG)
        end
    end
end

Events.OnLoadMapZones.Add(tagWalkableRecipes)

-- Gunworks' lua/shared loads before ours (loadModAfter=SWMG), so its rack wrapper is the one replaced here.
local okHooks = pcall(require, "WeaponSystems/Hooks/ReloadAnimHooks")
if okHooks and ISRackFirearm and ISRackFirearm.serverStart and ISReloadWeaponAction
    and ISReloadWeaponAction.setReloadSpeed then
    local gunworksRackServerStart = ISRackFirearm.serverStart
    function ISRackFirearm:serverStart(...)
        if self.character then
            ISReloadWeaponAction.setReloadSpeed(self.character, true)
        end
        return gunworksRackServerStart(self, ...)
    end
end

-- A full rack never leaves the bolt open, however it ends, nor a closing stroke that performs. stop and perform run
-- where the clip plays (the owner's client, single player), never on a server.
local okAnimations, Animations = pcall(require, "WeaponSystems/Utils/Animations")
local boltFixes = okHooks and okAnimations and type(Animations) == "table" and Animations.rackAction
    and Animations.CallAnimationFunction and ISRackFirearm and ISReloadWeaponAction

--- Close the bolt the way a rack's rackEnd does: parts and flag. rackAction puts the gun back in the hands to redraw
--- it, so a gun that is not in them gets only the parts and the flag.
local function closeNow(character, gun, phase)
    if character:getPrimaryHandItem() == gun then
        Animations.rackAction(character, gun, false, phase)
    else
        Animations.CallAnimationFunction(gun, false, "reload", phase)
        gun:getModData().gunworksBoltOpen = nil
    end
end

if boltFixes then
    local function closeBolt(action, stopped)
        local gun, character = action.gun, action.character
        local phase = action.gunworksRackPhase
        if not gun or not character then return end
        -- an opening stroke leaves the bolt open; a closing stroke cut short leaves it as it was (still to close)
        if phase == "open" or (phase and stopped) then return end
        if gun:getModData().gunworksBoltOpen ~= true then return end
        closeNow(character, gun, phase)
    end
    local rackStop = ISRackFirearm.stop
    function ISRackFirearm:stop(...)
        closeBolt(self, true)
        return rackStop(self, ...)
    end
    local rackPerform = ISRackFirearm.perform
    function ISRackFirearm:perform(...)
        closeBolt(self)
        return rackPerform(self, ...)
    end
end

-- A trigger pull closes a bolt that nothing else could: see the header. Where triggers are pulled only.
if boltFixes and not isServer() and ISReloadWeaponAction.canShoot then
    local okRules, ReloadRules = pcall(require, "WeaponSystems/ReloadAnim/Rules")
    local okReloadAnim, ReloadAnim = pcall(require, "WeaponSystems/Utils/ReloadAnim")
    local haveRules = okRules and okReloadAnim and type(ReloadRules) == "table" and type(ReloadAnim) == "table"
        and ReloadAnim.GetHandlerForGun and ReloadRules.hasRules and ReloadRules.buildContext and ReloadRules.evaluate
    local BUSY = { "isRacking", "isLoading", "isUnloading" }

    -- Would the gun's reload rules turn a rack into a closing stroke now? Then it is open on purpose.
    local function rackAnswer(player, gun)
        local handler = ReloadAnim.GetHandlerForGun(gun)
        if not ReloadRules.hasRules(handler) then return nil end
        return ReloadRules.evaluate(handler, "instead", "rack", ReloadRules.buildContext(player, gun, "rack", nil))
    end

    local function staleOpenBolt(player, gun)
        if not gun:haveChamber() then return false end
        for i = 1, #BUSY do
            if player:getVariableBoolean(BUSY[i]) then return false end
        end
        if not haveRules then return true end
        local ok, answer = pcall(rackAnswer, player, gun)
        return ok and answer == nil         -- rules that fail: leave the gun as it is
    end

    local canShoot = ISReloadWeaponAction.canShoot
    ISReloadWeaponAction.canShoot = function(player, weapon, ...)
        if player and weapon and instanceof(weapon, "HandWeapon") and weapon:getModData().gunworksBoltOpen == true
            and staleOpenBolt(player, weapon) then
            closeNow(player, weapon)
        end
        return canShoot(player, weapon, ...)
    end
end

-- On a server, a shot that leaves the bolt held open (GoM's LockOpenWeapons.lua sets the flag there too, and our
-- HoldOpen.lua for our own rifles) also fits the open bolt part, before vanilla's onShoot syncs the weapon to its
-- owner: see the header. HoldOpen.lua is loaded first, so that its wrapper is inside this one (it sets the flag
-- before calling on; from outside, this one would take the bolt for already held open).
pcall(require, "GunsOfTien/HoldOpen")
if boltFixes and isServer() and ISReloadWeaponAction.onShoot then
    local onShoot = ISReloadWeaponAction.onShoot
    Events.OnWeaponSwingHitPoint.Remove(onShoot)
    ISReloadWeaponAction.onShoot = function(player, weapon, ...)
        if not weapon or not instanceof(weapon, "HandWeapon") or weapon:getModData().gunworksBoltOpen == true then
            return onShoot(player, weapon, ...)
        end
        local sync = syncHandWeaponFields
        local fitted = false
        local function fitOpenBolt()
            if not fitted and weapon:getModData().gunworksBoltOpen == true then
                fitted = true
                Animations.CallAnimationFunction(weapon, true)
            end
        end
        syncHandWeaponFields = function(character, item, ...)
            if item == weapon then fitOpenBolt() end
            return sync(character, item, ...)
        end
        local ok, err = pcall(onShoot, player, weapon, ...)
        syncHandWeaponFields = sync
        fitOpenBolt()                       -- a shot that sent no sync
        if not ok then error(err, 0) end
    end
    Events.OnWeaponSwingHitPoint.Add(ISReloadWeaponAction.onShoot)
end
