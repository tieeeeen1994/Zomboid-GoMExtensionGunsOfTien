--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the SR-25 and KAC's 20 (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries, worded as RPKTooltips.lua),
    and none for the integrated bipod (GoM's bipods change no stats since its November 2026 update, and the
    SR-25 is semi-automatic, so it has no spread line either).
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "SR25"] = { "Uses .308/7.62x51mm NATO rounds" }
lines[M .. "762x51Magazine20_SR25"] = { "Uses .308/7.62x51mm NATO rounds." }

-- GoM's bipods change no stats since its November 2026 update (the M60's, BAR's and M24's, its rail bipod but for
-- its spread), so this bipod's states show no lines (Tooltips.lua shows nothing for a state without effects)
