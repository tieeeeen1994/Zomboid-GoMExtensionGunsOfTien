--[[
    Guns of Tien -- Gunworks' real single fire on our semi-automatic guns (Guns of Marz's November 2026 update: "New
    Real Semi Auto Firemode for all weapons. Semiauto no longer fires when holding down click like a delayed full auto.
    you will need to click for each shoot").

    Gunworks turns a gun's Single / Auto / Burst into RealSingle / RealAuto / RealBurst only for guns registered with
    its RateOfFire (client/WeaponSystems/Client.lua FiremodeSwitchCheck, on every swing); a RealSingle gun fires once
    per click (Hooks/CustomSystemHooks.lua latches the trigger). GoM registers every one of its semi-automatic guns,
    pistols, bolt and lever rifles and launchers at 600 rpm (its Registries/RPM.lua: pistols and rifles with spread
    on, launchers and shotguns off). Our select-fire guns are registered in their own files; the guns with Single fire
    only are registered here the same way (their scripts give FireMode and FireModePossibilities Single, as GoM's).
    Post-93's are in its own RealSingleFire.lua.
--]]

local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
pcall(require, "MarzWeapons/Registries/RPM")

RateOfFire.RegisterMultipleWeapons({
    -- pistols (GoM's M1911 / Glock 17)
    ["GunsOfTien.GLOCK21"] = { rpm = 600, enableSpread = true },
    ["GunsOfTien.PPK"] = { rpm = 600, enableSpread = true },
    -- marksman rifles (GoM's SVD / PSG-1)
    ["GunsOfTien.SR25"] = { rpm = 600, enableSpread = true },
    ["GunsOfTien.SVU"] = { rpm = 600, enableSpread = true },
})
