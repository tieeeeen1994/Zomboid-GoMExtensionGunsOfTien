--[[
    Guns of Tien -- realistic gun sounds, worked out from real loudness with the M16 as the reference

    A gun's SoundRadius (tiles zombies hear it) and SoundVolume (how strongly it draws them) are copied from its item
    script when the gun is created or loaded (Item.InstanceItem; HandWeapon.save does not write them), and Gunworks'
    StatsFactory restores them from a gun built from the script before applying suppressor (×0.3) and ammo
    (subsonic ×0.5...) multipliers. So the script values are set here, at OnInitGlobalModData (no player or chunk is
    loaded yet), on clients too: the world sound comes from the shooter's own copy. Scripts are reloaded on leaving a
    game, so this runs again at every world load.

    The values come from scripts/sound_model.py (SoundTable.lua).
--]]

local TABLE = require("GunsOfTien/SoundTable")

local function applyScripts()
    local manager = ScriptManager.instance
    for fullType, values in pairs(TABLE) do
        local script = manager:getItem(fullType)
        if script then
            script:setSoundRadius(values[1])
            script:setSoundVolume(values[2])
        end
    end
end

Events.OnInitGlobalModData.Add(applyScripts)
