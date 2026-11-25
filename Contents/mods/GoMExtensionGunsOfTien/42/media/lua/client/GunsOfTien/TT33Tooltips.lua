--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Tokarev TT-33 and its magazine (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; shared/GunsOfTien/TT33.lua).
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.TT33"] = { "Uses 7.62x25mm Tokarev rounds" }
lines["GunsOfTien.762x25Magazine8_TT33"] = { "Uses 7.62x25mm Tokarev rounds." }
