--[[
    Guns of Tien - Post-93 -- Guns of Marz's grip stances on Post-93's guns, as the main mod's GunsOfTien/GripStances.lua
    (see there): every two-handed gun that reloads with GoM's MP5 or FAMAS reload takes GoM's "SMG" stance with its
    "ForegripSMG" variant, as GoM's MP5s and FAMAS: the AUG A3, Para and HBAR, the MDRx .223 and .308, the PS90, the
    Groza-1 (with and without its GP-25) and Groza-4, the UMP45 and UMP9, the Vector .45 and its CRB. The one-handed
    guns (MP7s, P90 TR, Vector 9mm and SDP, Groza-2, pistols) are left as they are.
--]]

local GripAnim = require("WeaponSystems/Utils/GripAnim")
local SMG = require("GunsOfTien/GripStances")

local M = "GunsOfTienPost93."
local entries = {}
for _, gun in ipairs({ "AUGA3", "AUGPARA", "AUGHBAR", "MDR223", "MDR308", "PS90", "GROZA1", "GROZAGL", "GROZA4",
    "UMP45", "UMP9", "VECTOR45", "VECTORCRB", "A91M", "A91MPROTO" }) do
    entries[M .. gun] = SMG
end
GripAnim.RegisterMultipleWeapons(entries)
