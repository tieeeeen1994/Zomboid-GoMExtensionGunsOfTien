--[[
    Guns of Tien - Post-93 -- Gunworks' real single fire (one shot per click) on Post-93's guns with Single fire only,
    registered with Gunworks' RateOfFire at Guns of Marz's 600 rpm as GoM registers its own semi-automatic guns,
    pistols, bolt rifles and launchers (see the main mod's GunsOfTien/RealSingleFire.lua).
--]]

local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
pcall(require, "MarzWeapons/Registries/RPM")

local M = "GunsOfTienPost93."
RateOfFire.RegisterMultipleWeapons({
    -- pistols (GoM's M92FS); the Five-seveN is Post-93's item in GoM's module
    ["MarzGuns.FIVESEVEN"] = { rpm = 600, enableSpread = true },
    [M .. "UCP"] = { rpm = 600, enableSpread = true },
    [M .. "HK416QR22"] = { rpm = 600, enableSpread = true },
    -- semi-automatic rifles (GoM's AR-15, M14, SVD)
    [M .. "MDR223"] = { rpm = 600, enableSpread = true },
    [M .. "MDR308"] = { rpm = 600, enableSpread = true },
    [M .. "MK11"] = { rpm = 600, enableSpread = true },
    -- bolt-action rifles (GoM's M24, Mosin)
    [M .. "SV98"] = { rpm = 600, enableSpread = true },
    [M .. "SV99"] = { rpm = 600, enableSpread = true },
    -- the Groza's GP-25 (GoM's M203)
    [M .. "GROZAGL_GP25"] = { rpm = 600, enableSpread = false },
    -- the A-91M's launcher (GoM's M203)
    [M .. "A91M_GL"] = { rpm = 600, enableSpread = false },
})
