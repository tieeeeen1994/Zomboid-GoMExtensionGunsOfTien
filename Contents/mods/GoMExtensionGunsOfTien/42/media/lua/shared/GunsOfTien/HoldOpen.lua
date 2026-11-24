--[[
    Guns of Tien -- the bolt held open after the last round, on our rifles that have a bolt catch and GoM's bolt
    catch reload (user, 2026-11-24: "follow if it's realistic for them").

    Guns of Marz's 2026-11-23 update holds the bolt open on its M16s, M4A1, CAR-15, XM177, AR15, SKS and M1 Garand:
    its MarzWeapons/Hooks/LockOpenWeapons.lua sets Gunworks' bolt flag (modData.gunworksBoltOpen) when the round in
    the chamber is fired with none left to feed, and its reload rule "boltCatchAfterEmptyInsert" then turns the rack
    after the new magazine into the bolt catch slap (a closing stroke, the "ar15_rifle" reload's rackClose clip)
    instead of a pull on the charging handle. Its list of guns is local to that file, so ours are listed here and
    flagged the same way, in the same place (ISReloadWeaponAction.onShoot, wrapped with the Remove / Add convention
    every gun mod uses; on the server too, where GoMFixes.lua fits the open bolt part before the weapon sync).

    Only a gun registered with the "ar15_rifle" reload and that rule may be listed: without a closing stroke the
    flag could only be cleared by a full rack (GoMFixes.lua's trigger pull check would clear it at once).
    Real rifles, checked 2026-11-24:
    - HK416 and HK417: H&K's manuals for their civilian twins, the MR556A1 and MR762A1: the bolt catch "is also
      automatically activated when firing the last round in a magazine", released by pressing its top (the HK417
      got its hold-open with the polymer magazine of the later prototypes, Wikipedia);
    - SR-25 and Mk 11 Mod 0: Stoner's AR-10 pattern, the bolt catch a labelled control in Knight's M110 / Mk 11
      manual (ArmaLite's AR-10 SuperSASS manual, the same pattern: the carrier locks to the rear when the last
      round is fired; reload by pressing the top of the catch).
    Not listed: Walther's HK416 .22 (its bolt catch is a dummy, and its reload is GoM's MP5K one, with no slap).
    Our other guns that lock open in reality (AUGs, UMPs, Vectors, SCARs, pistols) have no closing stroke among
    GoM's reloads; Gunworks already draws their bolt back while they are empty.
--]]

require("TimedActions/ISReloadWeaponAction")

local HoldOpen = { guns = {} }

--- List a gun whose bolt stays open after its last round. It must have GoM's "ar15_rifle" reload with the rule
--- "boltCatchAfterEmptyInsert" (GoMReloads.profile).
---@param fullType string
function HoldOpen.register(fullType)
    HoldOpen.guns[fullType] = true
end

local onShoot = ISReloadWeaponAction.onShoot
Events.OnWeaponSwingHitPoint.Remove(onShoot)
ISReloadWeaponAction.onShoot = function(player, weapon, ...)
    -- before the shot is counted: the chambered round is the last one
    if weapon and HoldOpen.guns[weapon:getFullType()] and weapon:isRoundChambered()
        and weapon:getCurrentAmmoCount() == 0 then
        weapon:getModData().gunworksBoltOpen = true
    end
    return onShoot(player, weapon, ...)
end
Events.OnWeaponSwingHitPoint.Add(ISReloadWeaponAction.onShoot)

return HoldOpen
