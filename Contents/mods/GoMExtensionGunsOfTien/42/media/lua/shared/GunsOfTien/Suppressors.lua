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
    rounds below the speed of sound; the Mk9 on a plain MP5 keeps the crack), 23 / 7 against the suppressed MP5's
    28 / 8, and it is far lighter (2.1 against 2.0 + 1.2 + 0.5) and quicker to bring up; the MP5 keeps its harder hits
    and longer range, as the real SD's slower bullets give up.

    GoM's MP5 and MP5A2 model scripts have no `canon` point, where GoM draws muzzle parts. A model script cannot be
    declared again from another mod (every later block resets its mesh and texture), so the point is added to GoM's
    ModelScript at run time (ModelAttachment, ModelScript:addAttachment), at the front face of the front sight housing
    on the bore axis, measured on GoM's meshes by scripts/build_mk9.py (scripts/smg9_points.json). The engine looks
    a part's point up by name in the gun's model script when it draws it. The guns' ModelWeaponPart lines are
    appended with Item.DoParam (it appends even when the part type is already listed, so each script is patched
    once, as Lasers.lua does). Scripts are rebuilt on leaving a game, so both run again at every world load.
--]]

local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")

local SUPPRESSOR = "GunsOfTien.Mk9_Suppressor"
local MOUNT = "GunsOfTien.SMG9_Muzzle_Mount_Device"

-- gun item / model script -> its `canon` point (scripts/smg9_points.json)
local GUNS = {
    ["MarzGuns.MP5"] = { 0.0, 0.2796, 0.041 },
    ["MarzGuns.MP5A2"] = { 0.0, 0.2811, 0.041 },
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
    for gun, offset in pairs(GUNS) do
        local model = manager:getModelScript(gun)
        if model and not model:getAttachmentById("canon") then
            local point = ModelAttachment.new("canon")
            point:getOffset():set(offset[1], offset[2], offset[3])
            point:getRotate():set(0.0, 0.0, 0.0)
            model:addAttachment(point)
        elseif not model then
            print("[GunsOfTien] suppressors: model script not found: " .. gun)
        end
        local item = manager:getItem(gun)
        if item and not patched[item] then
            patched[item] = true
            for _, part in ipairs({ MOUNT, SUPPRESSOR }) do
                item:DoParam("ModelWeaponPart = " .. part .. " " .. part .. " canon canon")
            end
        end
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
