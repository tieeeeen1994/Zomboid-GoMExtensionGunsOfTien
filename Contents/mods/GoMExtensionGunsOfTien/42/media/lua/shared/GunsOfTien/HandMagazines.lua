--[[
    Guns of Tien -- GoM's magazines in the off hand at our size during the reload of our guns that take them (user,
    2026-11-02: the RPKs, the M249 and Post-93's SCAR-L).

    Those guns are drawn at the M16A2's proportion (0.603 of real), so they draw GoM's magazines through scaled models
    (`<magazine>_GoT`, gen_scripts.py stanag_got() / rpk()). GoM's reload nodes that fire Gunworks' `attachToHand`
    (its AK, M60, FAMAS and pistol loads and unloads; not "left_handle_load", the SCAR-L's, which shows no magazine in
    the hand today) put an item of the magazine's own type in the off hand, drawn with GoM's unscaled model, 7 %
    bigger than on the gun. Gunworks (42.13 ReloadAnim/Props.lua) resolves that item on the reloading client in
    `handlePropAnimEvent` through `ReloadAnim.resolveReloadMagItem` (looked up on the shared table at call time) and
    sends it to the server, which creates it only if the gun's reload profile allows it (`isAllowedPropValue`: the
    gun's magazines, or the profile's `partState.props`). So for a registered gun the resolver is swapped for the call
    to answer the hidden `<magazine>_Hand` item (the scaled model, GoM's `Bip01_Prop2` point), and the gun's profile
    lists those items in `partState.props` (`HandMagazines.props`). The M249 had this until 2026-10-29, keyed on its
    own reload animId, and lost it with the animations.
--]]

local ReloadAnim = require("WeaponSystems/Utils/ReloadAnim")
pcall(require, "WeaponSystems/ReloadAnim/Visuals")
pcall(require, "WeaponSystems/ReloadAnim/Props")

local HandMagazines = {}

-- gun full type -> { [magazine full type] = hand item full type }
local guns = {}

--- Show `map`'s hand items in place of GoM's magazines during `gun`'s reload.
---@param gun string
---@param map table<string,string>
function HandMagazines.register(gun, map)
    guns[gun] = map
end

--- The hand items of `map`, for the gun's reload profile (`partState.props`), in a fixed order.
---@param map table<string,string>
---@return string[]
function HandMagazines.props(map)
    local out = {}
    for _, item in pairs(map) do out[#out + 1] = item end
    table.sort(out)
    return out
end

--- { [GoM magazine] = our hand item } for GoM magazine full types, by the `<name>_Hand` naming.
---@param magazines string[]
---@return table<string,string>
function HandMagazines.mapOf(magazines)
    local map = {}
    for _, mag in ipairs(magazines) do
        map[mag] = "GunsOfTien." .. mag:match("[^.]+$") .. "_Hand"
    end
    return map
end

if not ReloadAnim.GunsOfTienHandMagazines and ReloadAnim.handlePropAnimEvent then
    ReloadAnim.GunsOfTienHandMagazines = true
    local original = ReloadAnim.handlePropAnimEvent
    ReloadAnim.handlePropAnimEvent = function(action, handler, event, parameter)
        local map
        if (parameter == nil or parameter == "") and ReloadAnim.handEventKind
            and ReloadAnim.handEventKind(event) == "attach" and ReloadAnim.resolveActionGun then
            local gun = ReloadAnim.resolveActionGun(action, handler, true)
            map = gun and guns[gun:getFullType()]
        end
        local resolve = ReloadAnim.resolveReloadMagItem
        if not map or not resolve then
            return original(action, handler, event, parameter)
        end
        ReloadAnim.resolveReloadMagItem = function(a, h)
            local magType = resolve(a, h)
            return map[magType] or magType
        end
        local ok, result = pcall(original, action, handler, event, parameter)
        ReloadAnim.resolveReloadMagItem = resolve
        if not ok then error(result) end
        return result
    end
end

return HandMagazines
