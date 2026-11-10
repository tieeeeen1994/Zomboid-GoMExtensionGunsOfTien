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
