--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Glock 21 and its magazine (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; worded as GoM words its USP,
    with the mount its Glock 17 takes; shared/GunsOfTien/Glock21.lua).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.GLOCK21"] = {
    "Uses .45 rounds.",
    "Compatible Mounting Device: Beretta Mount.",
    "Compatible Muzzle Device: .45 Muzzle Mount.",
}
lines["GunsOfTien.45Magazine13_GLOCK21"] = { "Uses .45 rounds." }
