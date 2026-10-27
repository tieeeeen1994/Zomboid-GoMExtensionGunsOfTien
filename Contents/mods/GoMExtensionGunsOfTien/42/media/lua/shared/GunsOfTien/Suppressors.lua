--[[
    Guns of Tien -- AWC's Mk9 suppressor and its 9x19mm SMG mount device on Guns of Marz's MP5 and MP5A2 (user,
    2026-10-22: "make a 9mm non-pistol suppressor so that non pistol 9mm guns can get a mount device too, only if
    supported")

    GoM's 9mm cans (M&P, Shh9) need its Pistol mount and fit its pistols only. The Mk9 (items_suppressors.txt) needs
    its own mount device first, GoM's rule for every can, and fits the 9mm SMGs whose real barrels take one: the MP5
    and MP5A2 (H&K's three-lug barrel), and Post-93's UMP9 (threaded; Post-93's Guns.lua adds it to the parts' MountOn
    and lists the parts in the UMP9's own script). Not the MP5K (a flush end cap, no lugs or threads: only the MP5K-N
    had them), the MP5SD (integral can) or the TEC-9 (its threaded barrel would take one; the user left it out). The
    main mod's Uzi, Mini Uzi and Micro Uzi take it too (user, 2026-10-23; the real Mk9 took the place of the Uzi's
    barrel nut): the parts' MountOn and the guns' lines are in their own scripts, the `canon` point in their models.
    Stats are GoM's for its 9mm cans, plus Aiming Time x1.1 (GoM's deployed bipod and LR4X scope): 24 oz on a 12" tube
    out at the muzzle. So the MP5SD stays the better quiet gun (user, 2026-10-22: "make it so that MP5SD is better than
    the MP5 with silencer option"): sound_model.py gives it no supersonic crack (its ported barrel slows standard
    rounds below the speed of sound; the Mk9 on a plain MP5 keeps the crack; the user later set it to 25 / 6),
    against the suppressed MP5's 28 / 8, and it is far lighter (2.1 against 2.0 + 1.2 + 0.5) and quicker to bring up; the MP5 keeps its harder hits
    and longer range, as the real SD's slower bullets give up.

    The MP5 and MP5A2 are drawn with Guns of Tien's MP5 models (scripts/build_mp5.py, models_mp5.txt: GoM's meshes at
    the Uzis' proportion), which carry the `canon` point (the front face of the front sight housing on the bore axis,
    measured on GoM's meshes by scripts/build_mk9.py, scaled with the gun). At that size the parts are drawn through
    their `_GoT` models (models_suppressors.txt), as on the Uzis and the UMP9, so the Mk9 is one size on every gun. The
    guns' ModelWeaponPart lines are appended with Item.DoParam (it appends even when the part type is already listed,
    so each script is patched once, as Lasers.lua does). Scripts are rebuilt on leaving a game, so it runs again at
    every world load.
--]]

local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")

local SUPPRESSOR = "GunsOfTien.Mk9_Suppressor"
local MOUNT = "GunsOfTien.SMG9_Muzzle_Mount_Device"

-- GoM's guns that take the parts (their `canon` point is in our MP5 models)
local GUNS = { "MarzGuns.MP5", "MarzGuns.MP5A2" }
-- part item -> the model it is drawn with on those guns (the parts' own size scaled to the guns')
local MODELS = {
    [MOUNT] = "GunsOfTien.SMG9_Muzzle_Mount_Device_GoT",
    [SUPPRESSOR] = "GunsOfTien.Mk9_Suppressor_GoT",
}

CSA.RegisterMultipleParts({
    [SUPPRESSOR] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Multiply("AimingTime", 1.1),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
})
RequiredAttachment.RegisterRequired({ SUPPRESSOR }, { MOUNT })

local patched = {}       -- gun item scripts given their lines (scripts are new objects after a reload)

local function patchScripts()
    local manager = ScriptManager.instance
    for _, gun in ipairs(GUNS) do
        local item = manager:getItem(gun)
        if item and not patched[item] then
            patched[item] = true
            for _, part in ipairs({ MOUNT, SUPPRESSOR }) do
                item:DoParam("ModelWeaponPart = " .. part .. " " .. MODELS[part] .. " canon canon")
            end
        elseif not item then
            print("[GunsOfTien] suppressors: item script not found: " .. gun)
        end
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
