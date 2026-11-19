--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Walther PPK and its magazine (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; shared/GunsOfTien/PPK.lua).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.PPK"] = {
    "Uses .22 LR rounds.",
    "Fits an ankle holster.",
}
lines["GunsOfTien.22LRMagazine8_PPK"] = { "Uses .22 LR rounds." }
