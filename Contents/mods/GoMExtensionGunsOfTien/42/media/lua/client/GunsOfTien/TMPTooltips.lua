--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Steyr TMP and its magazines (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; worded as UziTooltips.lua).
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.TMP"] = { "Uses 9x19mm rounds" }
for _, n in ipairs({ 15, 30 }) do
    lines["GunsOfTien.9x19Magazine" .. n .. "_TMP"] = { "Uses 9x19mm rounds." }
end
