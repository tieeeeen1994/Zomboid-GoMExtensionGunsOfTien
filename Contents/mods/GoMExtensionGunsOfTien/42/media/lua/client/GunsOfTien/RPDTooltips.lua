--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the RPD and its belt drum (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries). Its bipod, as GoM's M60's,
    changes no stats, so it has no lines.
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "RPD"] = { "Uses 7.62x39mm rounds" }
lines[M .. "762x39Drum100_RPD"] = { "Uses 7.62x39mm rounds." }

-- GoM's bipods change no stats since its November 2026 update (the M60's, BAR's and M24's, its rail bipod but for
-- its spread), so this bipod's states show no lines (Tooltips.lua shows nothing for a state without effects)
