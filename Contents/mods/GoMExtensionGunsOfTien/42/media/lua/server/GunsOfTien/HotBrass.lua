--[[
    Guns of Tien -- Hot Brass (spent casing ejection) for the new rounds

    Hot Brass looks a casing up by the gun's round (AmmoType item key); a round with no entry ejects nothing when
    fired. Pressure profiles are keyed by the Gunworks ammo profile name and scale how hard the casing is thrown
    (Guns of Marz: subsonic 0.25, AP / HP 1.1, overpressured 1.7). Only when Hot Brass (mod id HBVCEFb42) is on.
--]]

if not getActivatedMods():contains("HBVCEFb42") then return end

local ok, SpentCasingPhysics = pcall(require, "SpentCasingPhysics/Init")
if not ok or type(SpentCasingPhysics) ~= "table" then return end

SpentCasingPhysics.RegisterCasingToAmmo({
    ["GunsOfTien.762x39_Bullet_US"] = "HBVCEF.762x39_Casing",
    ["GunsOfTien.762x39_Bullet_SP"] = "HBVCEF.762x39_Casing",
    ["GunsOfTien.762x39_Bullet_SteelCore"] = "HBVCEF.762x39_Casing",
    ["GunsOfTien.9x19_Bullet_Subsonic"] = "HBVCEF.9x19_Casing",
    ["GunsOfTien.9x19_Bullet_HollowPoint"] = "HBVCEF.9x19_Casing",
    ["GunsOfTien.9x19_Bullet_PPP"] = "HBVCEF.9x19_Casing",
    ["GunsOfTien.45_Bullet_HollowPoint"] = "HBVCEF.45_Casing",
    ["GunsOfTien.45_Bullet_P"] = "HBVCEF.45_Casing",
    ["GunsOfTien.9x39_Bullet_SP6"] = "HBVCEF.9x39_Casing",
    ["GunsOfTien.3006_Bullet_SP"] = "HBVCEF.3006_Casing",
    ["GunsOfTien.308_Bullet_SP"] = "HBVCEF.308_Casing",
    -- Hot Brass has only red and green hulls; birdshot hulls are green more often than not.
    ["GunsOfTien.12Gauge_Shell_Birdshot"] = "HBVCEF.12Gauge_Hull_Green",
})

SpentCasingPhysics.RegisterPressureProfiles({
    ["GunsOfTien_762x39US"] = 0.25,
    ["GunsOfTien_9x19Subsonic"] = 0.7,
    ["GunsOfTien_9x19PPP"] = 1.5,
    ["GunsOfTien_45P"] = 1.3,
    ["GunsOfTien_12GaugeBirdshot"] = 0.9,
})

-- The M249 throws its cases (no links: user, 2026-10-22) down and to the right through the port at the bottom of the
-- receiver's right side: Post-93's P90 fall (a short drop from under the gun) turned out to the right, at GoM's M60
-- position along the gun.
SpentCasingPhysics.RegisterWeaponParams({
    ["GunsOfTien.M249"] = {
        forwardOffset = 0.30,
        sideOffset    = 0.08,
        heightOffset  = 0.44,
        shellForce    = 0.30,
        sideSpread    = 30,
        heightSpread  = { 0, 10 },
        ejectAngle    = 80,
        verticalForce = -0.05,
        spinForce     = { 46, 64 },
    },
})
