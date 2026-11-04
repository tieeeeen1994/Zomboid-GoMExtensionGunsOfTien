--[[
    Guns of Tien -- the Glock 21 (user, 2026-10-30) in Gunworks' and Guns of Marz's registries.

    Glock's .45 ACP pistol of 1990, as the second-generation gun of 1993 (no accessory rail, no finger grooves:
    scripts/build_glock21.py), registered as GoM registers its Glock 17 and USP and as Post-93 registers its
    Five-seveN and UCP (items_glock21.txt):
    - its 13-round magazine, its own profile, in GoM's ".45 ACP" family (GoM's .45 rounds and the main mod's Hollow
      Point and +P); Post-93's KRISS Vector .45 takes it too, and adds KRISS's 30-round magazine to the profile
      (Post-93's Vector.lua, which also gives this gun the ModelWeaponPart line that draws it);
    - the slide swapped on each shot (GoM's Slide_Fired / Slide_Lock), no rate of fire (semi-automatic only);
    - reload: GoM's own pistol animation (GoMReloads.lua);
    - GoM's pistol parts, as on its Glock 17 although the Gen 2 has no rail (user: "GoM's parts anyway"): the Beretta
      mount and its sights (GoM's rule: the sights need the mount), the PJ-3 / PX1 / TR-1 lasers (each with its beam,
      Lasers.lua) and the LP / TL lights under the dust cover, and GoM's .45 mount device and P45 suppressor, as on
      its USP;
    - a found gun as GoM's Glock 17 comes: the magazine at 50, a sight with the mount (":BM"), lasers and lights at 5.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local Animations = require("WeaponSystems/Utils/Animations")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

for _, file in ipairs({ "Ammunition", "Magazines", "ReloadsAndAnims/AnimationsFiring", "ReloadsAndAnims/ReloadAnims", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local GLOCK21 = M .. "GLOCK21"
local MAGS = { M .. "45Magazine13_GLOCK21" }

-------------------------------------------------
-- Magazine: its own profile, in GoM's .45 ACP family
-------------------------------------------------
Magazine.RegisterMagazineProfile(".45 ACP Glock 21", MAGS)
Magazine.RegisterWeaponWithProfile(".45 ACP Glock 21", GLOCK21)
Ammo.RegisterMultipleItemsWithFamilies({ [".45 ACP"] = MAGS })

-------------------------------------------------
-- The slide (GoM's pistol slide swap, as its Glock 17) and GoM's pistol reload
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(GLOCK21, {
    SingleAttachment = { open = "MarzGuns.Slide_Fired", locked = "MarzGuns.Slide_Lock" },
    cycleTicks = 5,
})
require("WeaponSystems/ReloadAnim/HandlerFactory").RegisterWeapon(GLOCK21,
    require("GunsOfTien/GoMReloads").profile("pistol_reload"))

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table), as GoM's Glock 17 comes
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[GLOCK21] = {
        required = { "MarzGuns.Slide_Lock" },
        optionals = {
            MAGS[1] .. ":50",
            "MarzGuns.PL4_Sight:5:BM", "MarzGuns.PM2_Sight:5:BM", "MarzGuns.PS1_Sight:5:BM",
            "MarzGuns.PJ-3_Laser:5", "MarzGuns.PX1_Laser:5", "MarzGuns.TR-1_Laser:5",
            "MarzGuns.LP_Light:5", "MarzGuns.TL_Light:5",
        },
    }
end

-------------------------------------------------
-- GoM's pistol parts allowed on it: appended to their MountOn (DoParam replaces the list, so it is read and written
-- back whole, as Post-93's Guns.lua does for the Five-seveN and UCP)
-------------------------------------------------
local PARTS = {
    "MarzGuns.Beretta_Mount", "MarzGuns.PL4_Sight", "MarzGuns.PM2_Sight", "MarzGuns.PS1_Sight",
    "MarzGuns.PJ-3_Laser", "MarzGuns.PX1_Laser", "MarzGuns.TR-1_Laser", "MarzGuns.LP_Light", "MarzGuns.TL_Light",
    "MarzGuns.45_Muzzle_Mount_Device", "MarzGuns.P45_Suppressor",
}

local function appendMountOn(partType, gun)
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
    if seen[gun] then return end
    list[#list + 1] = gun
    script:DoParam("MountOn = " .. table.concat(list, ";"))
end

local function appendAll()
    for _, part in ipairs(PARTS) do appendMountOn(part, GLOCK21) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTien_Glock21 = { GUN = GLOCK21, MAGS = MAGS }
