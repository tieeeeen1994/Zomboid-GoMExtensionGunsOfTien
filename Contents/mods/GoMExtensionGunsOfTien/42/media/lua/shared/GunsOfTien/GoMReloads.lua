--[[
    Guns of Tien -- every gun of both mods reloads with one of Guns of Marz's own reload animations (user, 2026-10-29:
    "drop all animations that we have ... use EXISTING GOM ANIMATIONS please for our guns"). This mod ships no
    AnimSet node and no clip: the guns are held with vanilla's rifle or pistol clips, as GoM's are, and each is
    registered in Gunworks' reload registry with one of GoM's animIds, the way GoM's Registries/ReloadsAndAnims/ReloadAnims.lua does
    (`magazineProfile`: Gunworks' "none" style, the magazine swapped when the action ends). "none" only means the gun's
    own magazine part is not animated: the off hand still shows the magazine wherever GoM's node fires Gunworks'
    `attachToHand` / `detachFromHand` events (pistol_reload, famas_rifle and m60_lmg loads and unloads), placed by
    the magazine model's own `attachment Bip01_Prop2`.

    GoM keeps its durations (the clips' lengths) in a local table, so they are copied here; `profile(animId)` gives a
    fresh table each call (Gunworks keeps the one it is given).

    Which gun takes which (the closest GoM gun in how it is held and loaded):
    - "MP5" (GoM's MP5 / MP5A2 / MP5SD until 2026-11-03, now on "hk_rifle"): the UMP45 and UMP9, the Vector .45 and
      CRB, the unused two-handed Uzi (UZI_2H). Kept on purpose (user, 2026-11-04: "only if applicable to reality"):
      "hk_rifle" is the MP5's own drill, the handle pulled back and locked in its notch before the magazine change,
      then slapped out of it. The UMP and the Vector lock their bolt open on the last round (a catch, released by
      a button or a tug on the handle), so the opening stroke an empty "hk_rifle" reload plays first is not theirs;
      the old MP5 rack (one pull and release of a handle high on the left front, after the magazine) is how they
      are reloaded, and both handles sit there. The Uzi, open bolt, is cocked with one pull too.
      GoM ships these nodes but no GoM gun uses them now: if a GoM update drops them, these guns lose their reload;
    - "ar15_rifle" (GoM's AR-15 and M4A1, the rear T-handle, with GoM's "boltCatchAfterEmptyInsert" rule): the SR-25,
      Post-93's Mk 11 Mod 0;
    - "handgun2" (GoM's MP5K / TEC-9, held like a pistol): the Uzi, Mini Uzi and Micro Uzi, the Steyr TMP, the MP7A1 / A2, the P90 TR,
      the Vector 9mm;
    - "pistol_reload" (GoM's pistols): the Glock 21, the Five-seveN, the UCP Prototype;
    - "famas_rifle" (GoM's FAMAS): the AUG A1, A3, Para and HBAR, the PS90 Carbine (a top-loading bullpup: GoM has no
      top-loading reload, and the user turned down the MP5's, 2026-11-03), the MDRx .223 and .308 (Post-93);
    - "left_handle_load" (GoM's BAR / AA-12: rifle magazine pushed straight in, charging handle on the left): the
      SCAR-L and SCAR-H, whose handles are on the left (GoM's FNC reload, "fnc_rifle", racks with the left hand
      reaching over to the right side; its FAL's, "fal_rifle", racks on the left but rocks the magazine in);
    - "m60_lmg" (GoM's M60): the M249;
    - "ak_rifle" (GoM's AKs and SVD: the handle on the right, racked with the left hand over the top): the RPK and
      RPK-74;
    - "m203_reload" (GoM's M203, non-magazine: `nonMagazineProfile`): Post-93's GP-25 on the Groza-1.
--]]

local GoMReloads = {}

-- GoM's RELOAD_DURATIONS (MarzWeapons/Registries/ReloadsAndAnims/ReloadAnims.lua, its clips' lengths), seconds.
-- GoM's own MP5s moved to "hk_rifle" (two-stroke rack) on 2026-11-03; its "MP5" nodes still ship, with no entry in
-- that table any more, so theirs are the lengths of the clips those nodes play (Bob_Reload_Rifle_Load, MP5_Rack,
-- MP5_Aim_Rack, from its CLIP_SECONDS).
local DURATIONS = {
    MP5 = { unload = 1.733333, load = 1.733333, rack = 1.272127, rackAim = 0.864086 },
    handgun2 = { unload = 1.29613, load = 1.29613, rack = 0.999844 },
    pistol_reload = { unload = 1.466667, unloadAim = 1.933333, load = 1.466667, loadAim = 1.1, rack = 1.7,
        rackAim = 1.233333 },
    famas_rifle = { unload = 1.533333, load = 1.533333, rack = 2.2, rackAim = 1.5 },
    left_handle_load = { unload = 1.733333, load = 1.733333, rack = 1.966667, rackAim = 1.966667 },
    m60_lmg = { unload = 7.533333, load = 6.75, rack = 2.766667 },
    ak_rifle = { unload = 1.866667, load = 1.866667, rack = 2.066667, rackAim = 1.666667 },
    -- GoM's AR-15 / M4A1 (its rear T-handle; with its rule "boltCatchAfterEmptyInsert"): the SR-25 and Mk 11 Mod 0
    ar15_rifle = { unload = 2.5, load = 2.5, rack = 2.166667, rackAim = 1.666667, rackClose = 1.695455 },
    -- GoM's M203 (one grenade, its double-barrel archetype): Post-93's GP-25 on the Groza
    m203_reload = { unload = 2.0, unloadAim = 2.2, load = 2.0, loadAim = 2.2, rack = 1.1, rackAim = 1.1 },
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

--- A Gunworks reload profile for a gun loaded round by round, as GoM's ReloadAnims.lua nonMagazineProfile builds
--- them (its M203: "m203_reload", archetype "doublebarrel", its own unload).
---@param animId string
---@param archetype string
---@param customUnload boolean|nil
---@return table
function GoMReloads.nonMagazineProfile(animId, archetype, customUnload)
    local durations = {}
    for k, v in pairs(DURATIONS[animId]) do
        durations[k] = v
    end
    return { animId = animId, archetype = archetype, customUnload = customUnload, durations = durations }
end

return GoMReloads
