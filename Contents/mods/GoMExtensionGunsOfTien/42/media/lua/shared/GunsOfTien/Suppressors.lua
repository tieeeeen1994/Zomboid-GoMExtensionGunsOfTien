--[[
    Guns of Tien -- AWC's Mk9 suppressor on Guns of Marz's MP5 and MP5A2 (user, 2026-10-22: "make a 9mm non-pistol
    suppressor so that non pistol 9mm guns can get a mount device too, only if supported"), and one 9mm mount device
    for every 9mm gun (user, 2026-11-23: "let's merge mounting device of 9mm")

    GoM's 9mm cans (M&P, Shh9) fit its pistols only. The Mk9 (items_suppressors.txt) needs a mount device first, GoM's
    rule for every can, and fits the 9mm SMGs whose real barrels take one: the MP5 and MP5A2 (H&K's three-lug barrel),
    and Post-93's UMP9 (threaded; Post-93's Guns.lua adds it to the parts' MountOn and lists the parts in the UMP9's
    own script). Not the MP5K (a flush end cap, no lugs or threads: only the MP5K-N had them), the MP5SD (integral
    can) or the TEC-9 (its threaded barrel would take one; the user left it out). The main mod's Uzi, Mini Uzi and
    Micro Uzi take it too (user, 2026-10-23; the real Mk9 took the place of the Uzi's barrel nut), and the Steyr TMP
    (user, 2026-11-11; its barrel is threaded for a can): the parts' MountOn and the guns' lines are in their own
    scripts, the `canon` point in their models.
    Every 9mm can fits every 9mm gun that takes the mount, pistols and SMGs alike (user, 2026-11-23: "change the 9mm
    suppressor to also take into pistols and SMGs... unify their stats", then "make it the same"): GoM's M&P and Shh9
    join the SMGs (here, Post-93's files and MuzzleFamilies.lua; drawn through `_GoT` models on the guns at our size),
    the Mk9 the pistols (its script). Stats: GoM's for its 9mm cans, the same on all three (sound and volume x0.3,
    damage x0.9, no flash; the Mk9 slowed aiming x1.1 until then). The MP5SD stays the better quiet gun (user,
    2026-10-22: "make it so that MP5SD is better than the MP5 with silencer option"): the MP5's 93 / 27 gives 28 / 8
    with any can against the SD's 25 / 6 (sound_model.py gives the SD no supersonic crack: its ported barrel slows
    standard rounds below the speed of sound; the user set it to 25 / 6). The SD is also far lighter
    (2.1 against 2.0 + 1.2 + 0.5); the MP5 keeps its harder hits and longer range, as the real SD's slower bullets give
    up.

    One mount device per calibre, as every other family (.45, 4.6x30mm, 5.7x28mm, 7.62x51mm, AR, AK): GoM's Pistol
    mount, renamed "9x19mm Family Muzzle Mounting Device" (ItemName.json), carries all three cans. Its MountOn gets the main mod's SMGs and GoM's MP5s here
    (Post-93 appends its UMP9, AUG Para and 9mm Vectors), and every SMG draws it with our adapter
    (`SMG9_Muzzle_Mount_Device_GoT`, Tim Bixler's three-lug adapter: the guns' scripts, the MP5s' lines below).
    The main mod's own mount, GunsOfTien.SMG9_Muzzle_Mount_Device ("9x19mm SMG Family" until 2026-11-23), stays
    defined, because an item type cannot be renamed in a saved world: an item of a type that no longer exists is
    dropped when its world loads (InventoryItem.loadItem: CreateItem gives null), a mount fitted on a gun included.
    In a world from before, server/GunsOfTien/RemovedParts.lua swaps each old one for GoM's (GunsOfTien_ReplacedParts
    below): on guns and loose, in every chunk as it loads, in each player's inventory 10 s after joining and in each
    vehicle once loaded. Until then, and anywhere that misses, the old one works as the same item in all but its ID:
    the same name, GoM's icon and floor model, every 9mm gun in its MountOn (its script), drawn as GoM's mount on the
    pistols (lines below), accepted by all three cans (RequiredAttachment's any-of lists), never spawned (Loot.lua).

    The MP5 and MP5A2 are drawn with Guns of Tien's MP5 models (scripts/build_mp5.py, models_mp5.txt: GoM's meshes at
    the Uzis' proportion), which carry the `canon` point (the front face of the front sight housing on the bore axis,
    measured on GoM's meshes by scripts/build_mk9.py, scaled with the gun). At that size the parts are drawn through
    their `_GoT` models (models_suppressors.txt), as on the Uzis and the UMP9, so the Mk9 is one size on every gun. The
    guns' ModelWeaponPart lines are appended with Item.DoParam (it appends even when the part type is already listed,
    so each script is patched once, as Lasers.lua does). MountOn is replaced by DoParam, so it is read and written back
    whole (as Glock21.lua does). Scripts are rebuilt on leaving a game, so it runs again at every world load.
--]]

local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")

local SUPPRESSOR = "GunsOfTien.Mk9_Suppressor"
local MOUNT = "MarzGuns.Pistol_Muzzle_Mount_Device"          -- GoM's, shown as "9x19mm Family Muzzle Mounting Device"
local OLD_MOUNT = "GunsOfTien.SMG9_Muzzle_Mount_Device"      -- the main mod's, kept for worlds that have one
local PISTOL_CANS = { "MarzGuns.M&P_Suppressor", "MarzGuns.Shh9_Suppressor" }

-- old mounts in a saved world become GoM's, fitted or loose, as server/GunsOfTien/RemovedParts.lua meets them
GunsOfTien_ReplacedParts = GunsOfTien_ReplacedParts or {}
GunsOfTien_ReplacedParts[OLD_MOUNT] = MOUNT

-- the main mod's SMGs and GoM's MP5s: on GoM's mount's and pistol cans' MountOn (the Mk9's and the old mount's are
-- in their scripts)
local SMGS = { "MarzGuns.MP5", "MarzGuns.MP5A2", "GunsOfTien.UZI", "GunsOfTien.MINIUZI", "GunsOfTien.MICROUZI",
    "GunsOfTien.UZI_2H", "GunsOfTien.TMP" }
-- gun -> { part, the model it is drawn with }: GoM's MP5s (their `canon` point is in our MP5 models; the parts' own
-- size scaled to the guns'), and GoM's 9mm pistols for the old mount (GoM's own mount model, as on its pistols) and
-- the Mk9 (at GoM's size, as built)
local LINES = {}
for _, gun in ipairs({ "MarzGuns.MP5", "MarzGuns.MP5A2" }) do
    LINES[gun] = {
        { OLD_MOUNT, "GunsOfTien.SMG9_Muzzle_Mount_Device_GoT" },
        { MOUNT, "GunsOfTien.SMG9_Muzzle_Mount_Device_GoT" },
        { SUPPRESSOR, "GunsOfTien.Mk9_Suppressor_GoT" },
        { PISTOL_CANS[1], "GunsOfTien.M&P_Suppressor_GoT" },
        { PISTOL_CANS[2], "GunsOfTien.Shh9_Suppressor_GoT" },
    }
end
for _, gun in ipairs({ "MarzGuns.M92FS", "MarzGuns.M93R", "MarzGuns.HIPOWER", "MarzGuns.P226", "MarzGuns.GLOCK17",
    "MarzGuns.VP70M" }) do
    LINES[gun] = { { OLD_MOUNT, "MarzGuns.Muzzle_Mount_Device" }, { SUPPRESSOR, SUPPRESSOR } }
end

CSA.RegisterMultipleParts({
    [SUPPRESSOR] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
})
-- lists are any-of: either mount carries any 9mm can (GoM's own rule for its cans names its mount the same way)
RequiredAttachment.RegisterRequired({ SUPPRESSOR }, { MOUNT, OLD_MOUNT })
RequiredAttachment.RegisterRequired(PISTOL_CANS, { MOUNT, OLD_MOUNT })

local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local entry = tostring(current:get(i))
            if not seen[entry] then
                seen[entry] = true
                list[#list + 1] = entry
            end
        end
    end
    local changed = false
    for _, gun in ipairs(guns) do
        if not seen[gun] then
            seen[gun] = true
            list[#list + 1] = gun
            changed = true
        end
    end
    if changed then script:DoParam("MountOn = " .. table.concat(list, ";")) end
end

local patched = {}       -- gun item scripts given their lines (scripts are new objects after a reload)

local function patchScripts()
    appendMountOn(MOUNT, SMGS)
    for _, can in ipairs(PISTOL_CANS) do appendMountOn(can, SMGS) end
    local manager = ScriptManager.instance
    for gun, lines in pairs(LINES) do
        local item = manager:getItem(gun)
        if item and not patched[item] then
            patched[item] = true
            for _, line in ipairs(lines) do
                item:DoParam("ModelWeaponPart = " .. line[1] .. " " .. line[2] .. " canon canon")
            end
        elseif not item then
            print("[GunsOfTien] suppressors: item script not found: " .. gun)
        end
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
