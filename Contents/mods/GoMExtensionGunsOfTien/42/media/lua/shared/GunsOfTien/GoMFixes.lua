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

-- A full rack never leaves the bolt open, however it ends. stop and perform run where the clip plays (the owner's
-- client, single player), never on a server.
local okAnimations, Animations = pcall(require, "WeaponSystems/Utils/Animations")
if okHooks and okAnimations and type(Animations) == "table" and Animations.rackAction and ISRackFirearm then
    local function closeBolt(action)
        local gun, character = action.gun, action.character
        if action.gunworksRackPhase or not gun or not character then return end
        if gun:getModData().gunworksBoltOpen ~= true then return end
        -- rackAction puts the gun back in the hands to redraw it: only for the gun that is in them
        if character:getPrimaryHandItem() ~= gun then return end
        Animations.rackAction(character, gun, false)
    end
    local rackStop = ISRackFirearm.stop
    function ISRackFirearm:stop(...)
        closeBolt(self)
        return rackStop(self, ...)
    end
    local rackPerform = ISRackFirearm.perform
    function ISRackFirearm:perform(...)
        closeBolt(self)
        return rackPerform(self, ...)
    end
end
