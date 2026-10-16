--[[
    Guns of Tien - Post-93 -- Hot Brass (spent casing ejection) for the MP7A1, P90 TR, Five-seveN and UCP

    Casings by round item key, ejection by gun full type (falls back to a default per reload type), pressure by the
    Gunworks ammo profile name. Hot Brass ships the casings HBVCEF.46x30_Casing / 57x28_Casing. Only with Hot Brass (HBVCEFb42).
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

-- Hot Brass launches a casing from a point in front of the shooter (forward / side / height, tiles and levels from
-- the feet), not from the gun model. Both guns are held like a pistol, out at arm's length, so they start where GoM
-- starts its handgun-held SMGs (MP5K / TEC9 / MAC10: forward 0.55, side 0.06, height 0.53).
SpentCasingPhysics.RegisterWeaponParams({
    -- Thrown out to the right like GoM's MP5K (about 1 s in the air, 1.7 tiles out).
    ["GunsOfTienPost93.MP7A1"] = {
        forwardOffset = 0.55,
        sideOffset    = 0.06,
        heightOffset  = 0.53,
        shellForce    = 0.60,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The P90 throws its cases straight down through the port under the grip: a short fall from under the gun with a
    -- slight forward drift (about 0.5 s). Hot Brass's own P90 entry (verticalForce -0.6) lands them almost at once.
    ["GunsOfTienPost93.P90TR"] = {
        forwardOffset = 0.50,
        sideOffset    = 0.0,
        heightOffset  = 0.45,
        shellForce    = 0.15,
        sideSpread    = 10,
        heightSpread  = { 0, 10 },
        ejectAngle    = 0,
        verticalForce = -0.05,
        spinForce     = { 24, 34 },
    },
    -- Pistols ejecting to the right: GoM's M92FS values.
    ["GunsOfTienPost93.UCP"] = {
        forwardOffset = 0.40,
        sideOffset    = 0.0,
        heightOffset  = 0.50,
        shellForce    = 0.60,
        sideSpread    = 45,
        heightSpread  = 60,
        spinForce     = { 12, 16 },
    },
    ["MarzGuns.FIVESEVEN"] = {
        forwardOffset = 0.40,
        sideOffset    = 0.0,
        heightOffset  = 0.50,
        shellForce    = 0.60,
        sideSpread    = 45,
        heightSpread  = 60,
        spinForce     = { 12, 16 },
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
