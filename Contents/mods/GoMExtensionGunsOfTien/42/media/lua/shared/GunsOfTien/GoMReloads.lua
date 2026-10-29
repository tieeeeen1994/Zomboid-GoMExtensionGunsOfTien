--[[
    Guns of Tien -- every gun of both mods reloads with one of Guns of Marz's own reload animations (user, 2026-10-29:
    "drop all animations that we have ... use EXISTING GOM ANIMATIONS please for our guns"). This mod ships no
    AnimSet node and no clip: the guns are held with vanilla's rifle or pistol clips, as GoM's are, and each is
    registered in Gunworks' reload registry with one of GoM's animIds, the way GoM's Registries/ReloadAnims.lua does
    (`magazineProfile`: Gunworks' "none" style, the magazine swapped when the action ends).

    GoM keeps its durations (the clips' lengths) in a local table, so they are copied here; `profile(animId)` gives a
    fresh table each call (Gunworks keeps the one it is given).

    Which gun takes which (the closest GoM gun in how it is held and loaded):
    - "MP5" (GoM's MP5 / MP5A2 / MP5SD): the Uzi, the UMP45 and UMP9;
    - "handgun2" (GoM's MP5K / TEC-9, held like a pistol): the Mini and Micro Uzi, the MP7A1 / A2, the P90 TR;
    - "pistol_reload" (GoM's pistols): the Five-seveN, the UCP Prototype;
    - "famas_rifle" (GoM's FAMAS): the AUG A1, A3, Para and HBAR;
    - "fnc_rifle" (GoM's FNC: rifle magazine change, side charging handle): the SCAR-L;
    - "fal_rifle" (GoM's FAL): the SCAR-H;
    - "m60_lmg" (GoM's M60): the M249.
--]]

local GoMReloads = {}

-- GoM's RELOAD_DURATIONS (MarzWeapons/Registries/ReloadAnims.lua), seconds
local DURATIONS = {
    MP5 = { unload = 2.2, load = 2.2, rack = 1.4 },
    handgun2 = { unload = 1.29613, load = 1.29613, rack = 0.999844 },
    pistol_reload = { unload = 1.466667, load = 1.466667, rack = 1.7 },
    famas_rifle = { unload = 1.533333, load = 1.533333, rack = 2.2, rackAim = 1.5 },
    fnc_rifle = { unload = 2.5, load = 2.5, rack = 2.066667, rackAim = 1.666667 },
    fal_rifle = { unload = 2.7, load = 2.7, rack = 1.2, rackAim = 1.666667 },
    m60_lmg = { unload = 7.533333, load = 8.7, rack = 2.766667 },
}

--- A Gunworks reload profile playing GoM's animation `animId`.
---@param animId string
---@param extra table|nil more profile fields (partState...)
---@return table
function GoMReloads.profile(animId, extra)
    local durations = {}
    for k, v in pairs(DURATIONS[animId]) do
        durations[k] = v
    end
    local profile = { animId = animId, style = "none", durations = durations }
    for k, v in pairs(extra or {}) do
        profile[k] = v
    end
    return profile
end

return GoMReloads
