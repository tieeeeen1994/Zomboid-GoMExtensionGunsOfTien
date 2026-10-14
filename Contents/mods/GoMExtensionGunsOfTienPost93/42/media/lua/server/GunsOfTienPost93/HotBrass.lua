--[[
    Guns of Tien - Post-93 -- Hot Brass (spent casing ejection) for the MP7A1 and P90 TR

    Casings by round item key, ejection by gun full type (falls back to a default per reload type), pressure by the
    Gunworks ammo profile name. Hot Brass ships the casings HBVCEF.46x30_Casing / 57x28_Casing, and its own
    parameters for another mod's P90 (downward ejection) and MP7, which these follow. Only with Hot Brass (HBVCEFb42).
--]]

if not getActivatedMods():contains("HBVCEFb42") then return end

local ok, SpentCasingPhysics = pcall(require, "SpentCasingPhysics/Init")
if not ok or type(SpentCasingPhysics) ~= "table" then return end

SpentCasingPhysics.RegisterCasingToAmmo({
    ["GunsOfTienPost93.46x30_Bullet"] = "HBVCEF.46x30_Casing",
    ["GunsOfTienPost93.46x30_Bullet_Subsonic"] = "HBVCEF.46x30_Casing",
    ["GunsOfTienPost93.57x28_Bullet"] = "HBVCEF.57x28_Casing",
    ["GunsOfTienPost93.57x28_Bullet_SB193"] = "HBVCEF.57x28_Casing",
    ["GunsOfTienPost93.57x28_Bullet_SS197SR"] = "HBVCEF.57x28_Casing",
})

SpentCasingPhysics.RegisterWeaponParams({
    ["GunsOfTienPost93.MP7A1"] = {
        forwardOffset = 0.40,
        sideOffset    = 0.0,
        heightOffset  = 0.45,
        shellForce    = 0.60,
        sideSpread    = 30,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The P90 throws its cases straight down through the port behind the grip.
    ["GunsOfTienPost93.P90TR"] = {
        forwardOffset = 0.35,
        sideOffset    = 0.10,
        heightOffset  = 0.50,
        shellForce    = 0.10,
        sideSpread    = 10,
        ejectAngle    = 0,
        verticalForce = -0.6,
        spinForce     = { 24, 34 },
    },
})

SpentCasingPhysics.RegisterPressureProfiles({
    ["GunsOfTienPost93_46x30Subsonic"] = 0.4,
    ["GunsOfTienPost93_57x28SB193"] = 0.4,
})

SpentCasingPhysics.RegisterItemSound({
    ["HBVCEF.46x30_Casing"] = "Bullet",
    ["HBVCEF.57x28_Casing"] = "Bullet",
})
