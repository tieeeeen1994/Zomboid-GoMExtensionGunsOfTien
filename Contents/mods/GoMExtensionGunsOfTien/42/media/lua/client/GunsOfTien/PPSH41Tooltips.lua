--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the PPSh-41 and its magazines (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries;
    shared/GunsOfTien/PPSH41.lua). The gun's other lines (rails, mounts, built-in parts, magazines) are written by
    GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.PPSH41"] = { "Uses 7.62x25mm Tokarev rounds" }
lines["GunsOfTien.762x25Drum71_PPSH41"] = { "Uses 7.62x25mm Tokarev rounds." }
lines["GunsOfTien.762x25Magazine35_PPSH41"] = { "Uses 7.62x25mm Tokarev rounds." }
