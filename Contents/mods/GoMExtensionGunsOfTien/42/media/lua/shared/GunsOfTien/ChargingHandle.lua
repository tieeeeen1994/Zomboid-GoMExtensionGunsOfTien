--[[
    Guns of Tien -- charging handles that do not reciprocate (user, 2026-10-30: "the charging handle and the bolt is
    not always the same, and this is the case for MP7 and AUG").

    On every gun of both mods but the SCARs (whose handle rides with the carrier) the real handle stays forward while
    the gun fires: the Uzi, Mini and Micro Uzi (IMI's top knob), the M249, the Steyr AUGs, and Post-93's MP7s, P90
    and UMPs (2026-10-30). Only the bolt or carrier inside moves, seen through the ejection port (on the right, under
    the P90 and the M249). So on these guns GoM's Bolt part (MarzGuns.Bolt_Lock / Bolt_Fired, which Gunworks swaps on each shot,
    while the gun is empty and during the rack) draws the bolt (`<gun>_BOLT`, a plate over the port's front half),
    and the handle is a part of its own: GunsOfTien.ChargingHandle_Forward / _Back (PartType ChargingHandle,
    items_handles.txt), drawn by each gun's ModelWeaponPart lines at `handle` / `handle_back`.

    The handle goes back only while racked: between the rack clip's rackStart and rackEnd events (GoM's handgun2 and
    FAMAS racks send both). It is set before Gunworks' own ISRackFirearm hooks run, whose Animations.CallAnimate
    re-sends the gun's parts (syncHandWeaponFields + re-equip), so it travels with Gunworks' bolt sync. A gun saved
    before 2026-10-30 has no ChargingHandle part: it gets the forward one when equipped (as the M249's Bolt part,
    M249.lua) or at its first shot / rack; a found gun comes with it (the guns' spawn tables).
--]]

require("TimedActions/ISRackFirearm")

local Animations = require("WeaponSystems/Utils/Animations")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

local ChargingHandle = {}

ChargingHandle.FORWARD = "GunsOfTien.ChargingHandle_Forward"
ChargingHandle.BACK = "GunsOfTien.ChargingHandle_Back"
ChargingHandle.PART_TYPE = "ChargingHandle"

local guns = {}

--- A gun whose handle is the ChargingHandle part (its item script draws both states).
---@param fullType string
function ChargingHandle.Register(fullType)
    guns[fullType] = true
end

function ChargingHandle.Has(weapon)
    return weapon ~= nil and instanceof(weapon, "HandWeapon") and guns[weapon:getFullType()] == true
end

--- Fits the handle forward or back; false when it already was.
function ChargingHandle.Set(weapon, back)
    local want = back and ChargingHandle.BACK or ChargingHandle.FORWARD
    local part = weapon:getWeaponPart(ChargingHandle.PART_TYPE)
    if part and part:getFullType() == want then return false end
    weapon:attachWeaponPart(instanceItem(want), true)
    return true
end

PreventRemoval.Register({ ChargingHandle.FORWARD, ChargingHandle.BACK })

-- Wrapped once even if this file is reloaded (Gunworks' own hooks are wrapped under these)
if not ISRackFirearm.GunsOfTienChargingHandle then
    ISRackFirearm.GunsOfTienChargingHandle = true

    local animEvent = ISRackFirearm.animEvent
    function ISRackFirearm:animEvent(event, parameter)
        if ChargingHandle.Has(self.gun) then
            if event == "rackStart" then
                ChargingHandle.Set(self.gun, true)
            elseif event == "rackEnd" then
                ChargingHandle.Set(self.gun, false)
            end
        end
        return animEvent(self, event, parameter)
    end

    local complete = ISRackFirearm.complete
    function ISRackFirearm:complete()
        if ChargingHandle.Has(self.gun) then ChargingHandle.Set(self.gun, false) end
        return complete(self)
    end

    local stop = ISRackFirearm.stop
    function ISRackFirearm:stop()
        if ChargingHandle.Has(self.gun) then ChargingHandle.Set(self.gun, false) end
        return stop(self)
    end

    -- a gun saved without the part gets it at its first shot or rack (Gunworks syncs right after this call)
    local callAnimationFunction = Animations.CallAnimationFunction
    function Animations.CallAnimationFunction(weapon, open)
        if ChargingHandle.Has(weapon) and not weapon:getWeaponPart(ChargingHandle.PART_TYPE) then
            ChargingHandle.Set(weapon, false)
        end
        return callAnimationFunction(weapon, open)
    end
end

-- ... or as soon as its owner equips it (the M249's way, M249.lua)
Events.OnEquipPrimary.Add(function(character, item)
    if not (item and character and character.isLocalPlayer and character:isLocalPlayer() and ChargingHandle.Has(item))
        or item:getWeaponPart(ChargingHandle.PART_TYPE) then
        return
    end
    ChargingHandle.Set(item, false)
    Animations.CallSyncHandWeaponFields(character, item)
end)

return ChargingHandle
