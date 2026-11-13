--[[
    Guns of Tien - Post-93 -- Hot Brass (spent casing ejection) for the MP7A1 / A2, P90 TR, Five-seveN, UCP, SCAR-L and SCAR-H,
    UMP45 and UMP9, Steyr AUG A3, Para and HBAR, KRISS Vector .45 and 9mm, MDRx .223 and .308

    Casings by round item key, ejection by gun full type (falls back to a default per reload type), pressure by the
    Gunworks ammo profile name. Hot Brass ships the casings HBVCEF.46x30_Casing / 57x28_Casing. Only with Hot Brass (HBVCEFb42).
--]]

if not getActivatedMods():contains("HBVCEFb42") then return end

local ok, SpentCasingPhysics = pcall(require, "SpentCasingPhysics/Init")
if not ok or type(SpentCasingPhysics) ~= "table" then return end

SpentCasingPhysics.RegisterCasingToAmmo({
    ["GunsOfTienPost93.46x30_Bullet"] = "HBVCEF.46x30_Casing",
    ["GunsOfTienPost93.46x30_Bullet_Subsonic"] = "HBVCEF.46x30_Casing",
    -- SS190 (GunsOfTienPost93.57x28_Bullet) is the main mod's since 2026-11-03 (its HotBrass.lua)
    ["GunsOfTienPost93.57x28_Bullet_SB193"] = "HBVCEF.57x28_Casing",
    ["GunsOfTienPost93.57x28_Bullet_SS197SR"] = "HBVCEF.57x28_Casing",
})

-- Hot Brass launches a casing from a point in front of the shooter (forward / side / height, tiles and levels from
-- the feet), not from the gun model. Both guns are held like a pistol, out at arm's length, so they start where GoM
-- starts its handgun-held SMGs (MP5K / TEC9 / MAC10: forward 0.55, side 0.06, height 0.53).
-- forwardOffset: the ejection port moved toward the grip when our guns were resized to the M16A2's proportion
-- (2026-10-26): each value lowered by (1 - size change) x the port's old distance ahead of the grip x 1.5 tiles a unit.
SpentCasingPhysics.RegisterWeaponParams({
    -- Thrown out to the right like GoM's MP5K (about 1 s in the air, 1.7 tiles out).
    ["GunsOfTienPost93.MP7A1"] = {
        forwardOffset = 0.544,
        sideOffset    = 0.06,
        heightOffset  = 0.53,
        shellForce    = 0.60,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- the MP7A2 ejects as the A1
    ["GunsOfTienPost93.MP7A2"] = {
        forwardOffset = 0.544,
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
    -- The PS90 Carbine throws them down the same chute, held as a rifle: the port nearer the shoulder.
    ["GunsOfTienPost93.PS90"] = {
        forwardOffset = 0.30,
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
        forwardOffset = 0.384,
        sideOffset    = 0.0,
        heightOffset  = 0.50,
        shellForce    = 0.60,
        sideSpread    = 45,
        heightSpread  = 60,
        spinForce     = { 12, 16 },
    },
    -- The SCARs eject to the right like GoM's M4A1 / FAL (their values; the SCAR-H's casings fly a little further).
    ["GunsOfTienPost93.SCARL"] = {
        forwardOffset = 0.291,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 30,
        ejectAngle    = 75,
        spinForce     = { 64, 128 },
    },
    ["GunsOfTienPost93.SCARH"] = {
        forwardOffset = 0.39,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 0.95,
        sideSpread    = 60,
        heightSpread  = 90,
        ejectAngle    = 80,
        spinForce     = { 86, 124 },
    },
    -- The HK416 ejects from its AR port as GoM's M4A1 (the SCAR-L's values, which are the M4A1's).
    ["GunsOfTienPost93.HK416"] = {
        forwardOffset = 0.291,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 30,
        ejectAngle    = 75,
        spinForce     = { 64, 128 },
    },
    -- The Mk 11 Mod 0 throws its cases out of its AR port as the main mod's SR-25 (GoM's AR15's angles, a 7.62x51's
    -- force).
    ["GunsOfTienPost93.MK11"] = {
        forwardOffset = 0.30,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 1.0,
        sideSpread    = 60,
        heightSpread  = 30,
        ejectAngle    = 75,
        spinForce     = { 74, 86 },
    },
    -- The Grozas eject to the right from the port behind the grip, close to the cheek: GoM's AKS-74U / AS VAL
    -- angles and force from the FAMAS's place (another bullpup). The Groza-2 is held like a pistol: the MP7's place
    -- and angles (another pistol-held gun) with the port's 0.1 further back, the AKS-74U's force (to check in game).
    ["GunsOfTienPost93.GROZA1"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 75,
        ejectAngle    = 45,
        spinForce     = { 164, 164 },
    },
    ["GunsOfTienPost93.GROZAGL"] = {           -- the Groza-1's port; the GP-25 itself is caseless
        forwardOffset = 0.10,
        sideOffset    = 0.10,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 75,
        ejectAngle    = 45,
        spinForce     = { 164, 164 },
    },
    ["GunsOfTienPost93.GROZA2"] = {
        forwardOffset = 0.44,
        sideOffset    = 0.06,
        heightOffset  = 0.53,
        shellForce    = 0.90,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 164, 164 },
    },
    ["GunsOfTienPost93.GROZA4"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.09,
        heightOffset  = 0.47,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 75,
        ejectAngle    = 45,
        spinForce     = { 64, 128 },
    },
    -- The UMPs eject to the right like GoM's MP5 (its values).
    ["GunsOfTienPost93.UMP45"] = {
        forwardOffset = 0.332,
        sideOffset    = 0.08,
        heightOffset  = 0.48,
        shellForce    = 0.65,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    ["GunsOfTienPost93.UMP9"] = {
        forwardOffset = 0.332,
        sideOffset    = 0.08,
        heightOffset  = 0.48,
        shellForce    = 0.65,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The AUGs eject to the right from the main mod's AUG A1 port, behind the grip (its values); the Para's 9mm cases
    -- thrown as gently as the UMPs', the HBAR's 7.62x39 a little further, as the SCAR-H's.
    ["GunsOfTienPost93.AUGA3"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.08,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 30,
        ejectAngle    = 55,
        spinForce     = { 64, 128 },
    },
    ["GunsOfTienPost93.AUGPARA"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.08,
        heightOffset  = 0.45,
        shellForce    = 0.65,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 55,
        spinForce     = { 24, 34 },
    },
    ["GunsOfTienPost93.AUGHBAR"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.08,
        heightOffset  = 0.45,
        shellForce    = 0.95,
        sideSpread    = 60,
        heightSpread  = 60,
        ejectAngle    = 60,
        spinForce     = { 86, 124 },
    },
    -- The Vectors eject to the right: the rifle-held .45 as the UMPs, the pistol-held 9mm as the MP7 (their values).
    ["GunsOfTienPost93.VECTOR45"] = {
        forwardOffset = 0.332,
        sideOffset    = 0.08,
        heightOffset  = 0.48,
        shellForce    = 0.65,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The CRB: the .45's receiver, port and hold
    ["GunsOfTienPost93.VECTORCRB"] = {
        forwardOffset = 0.332,
        sideOffset    = 0.08,
        heightOffset  = 0.48,
        shellForce    = 0.65,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    ["GunsOfTienPost93.VECTOR9"] = {
        forwardOffset = 0.544,
        sideOffset    = 0.06,
        heightOffset  = 0.53,
        shellForce    = 0.60,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The SDP: the 9mm's receiver, port and hold
    ["GunsOfTienPost93.VECTORSDP"] = {
        forwardOffset = 0.544,
        sideOffset    = 0.06,
        heightOffset  = 0.53,
        shellForce    = 0.60,
        sideSpread    = 50,
        heightSpread  = { 80, 100 },
        ejectAngle    = 80,
        spinForce     = { 24, 34 },
    },
    -- The MDRx .223 ejects to the right from its side-eject port behind the grip, as the AUG A3 (its values). The .308
    -- ejects forward: its chute carries the case along the right side and drops it out by the handguard's rear, ahead
    -- of the grip, forward and a little right, gently (the chute takes the speed out of it).
    ["GunsOfTienPost93.MDR223"] = {
        forwardOffset = 0.10,
        sideOffset    = 0.08,
        heightOffset  = 0.45,
        shellForce    = 0.90,
        sideSpread    = 60,
        heightSpread  = 30,
        ejectAngle    = 55,
        spinForce     = { 64, 128 },
    },
    ["GunsOfTienPost93.MDR308"] = {
        forwardOffset = 0.36,
        sideOffset    = 0.08,
        heightOffset  = 0.45,
        shellForce    = 0.45,
        sideSpread    = 20,
        heightSpread  = { 10, 30 },
        ejectAngle    = 25,
        spinForce     = { 24, 48 },
    },
    ["MarzGuns.FIVESEVEN"] = {
        forwardOffset = 0.383,
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
