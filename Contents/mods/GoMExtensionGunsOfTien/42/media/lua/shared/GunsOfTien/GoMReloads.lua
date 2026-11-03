--[[
    Guns of Tien -- every gun of both mods reloads with one of Guns of Marz's own reload animations (user, 2026-10-29:
    "drop all animations that we have ... use EXISTING GOM ANIMATIONS please for our guns"). This mod ships no
    AnimSet node and no clip: the guns are held with vanilla's rifle or pistol clips, as GoM's are, and each is
    registered in Gunworks' reload registry with one of GoM's animIds, the way GoM's Registries/ReloadAnims.lua does
    (`magazineProfile`: Gunworks' "none" style, the magazine swapped when the action ends). "none" only means the gun's
    own magazine part is not animated: the off hand still shows the magazine wherever GoM's node fires Gunworks'
    `attachToHand` / `detachFromHand` events (pistol_reload, famas_rifle and m60_lmg loads and unloads), placed by
    the magazine model's own `attachment Bip01_Prop2`.

    GoM keeps its durations (the clips' lengths) in a local table, so they are copied here; `profile(animId)` gives a
    fresh table each call (Gunworks keeps the one it is given).

    Which gun takes which (the closest GoM gun in how it is held and loaded):
    - "MP5" (GoM's MP5 / MP5A2 / MP5SD): the UMP45 and UMP9, the Vector .45, the unused two-handed Uzi (UZI_2H);
    - "handgun2" (GoM's MP5K / TEC-9, held like a pistol): the Uzi, Mini Uzi and Micro Uzi, the MP7A1 / A2, the P90 TR,
      the Vector 9mm;
    - "pistol_reload" (GoM's pistols): the Glock 21, the Five-seveN, the UCP Prototype;
    - "famas_rifle" (GoM's FAMAS): the AUG A1, A3, Para and HBAR, the PS90 Carbine (a top-loading bullpup: GoM has no
      top-loading reload, and the user turned down the MP5's, 2026-11-03);
    - "left_handle_load" (GoM's BAR / AA-12: rifle magazine pushed straight in, charging handle on the left): the
      SCAR-L and SCAR-H, whose handles are on the left (GoM's FNC reload, "fnc_rifle", racks with the left hand
      reaching over to the right side; its FAL's, "fal_rifle", racks on the left but rocks the magazine in);
    - "m60_lmg" (GoM's M60): the M249;
    - "ak_rifle" (GoM's AKs and SVD: the handle on the right, racked with the left hand over the top): the RPK and
      RPK-74.
--]]

local GoMReloads = {}

-- GoM's RELOAD_DURATIONS (MarzWeapons/Registries/ReloadAnims.lua), seconds
local DURATIONS = {
    MP5 = { unload = 2.2, load = 2.2, rack = 1.4 },
    handgun2 = { unload = 1.29613, load = 1.29613, rack = 0.999844 },
    pistol_reload = { unload = 1.466667, load = 1.466667, rack = 1.7 },
    famas_rifle = { unload = 1.533333, load = 1.533333, rack = 2.2, rackAim = 1.5 },
    left_handle_load = { unload = 1.733333, load = 1.733333, rack = 1.966667, rackAim = 1.966667 },
    m60_lmg = { unload = 7.533333, load = 8.7, rack = 2.766667 },
    ak_rifle = { unload = 1.866667, load = 1.866667, rack = 2.066667, rackAim = 1.666667 },
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
