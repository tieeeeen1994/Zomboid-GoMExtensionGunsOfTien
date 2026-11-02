--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the RPD and its belt drum (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries), and its bipod's lines, shown
    under the gun while that state is fitted (Tooltips.lua; stats in shared/GunsOfTien/RPD.lua, GoM's M60 bipod's,
    worded as M249Tooltips.lua words them).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "RPD"] = {
    "Uses 7.62x39mm rounds.",
    "Compatible Magazines: RPD 100Rds Belt Drum",
}
lines[M .. "762x39Drum100_RPD"] = { "Uses 7.62x39mm rounds." }

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates[M .. "RPD_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 30%",
    "Critical and Hit Chance increased by 10%",
    "No endurance used to fire",
}
GunsOfTien_TooltipStates[M .. "RPD_Integrated_Bipod_Folded"] = {
    "Folding bipod folded:",
    "Hit Chance reduced by 20%",
    "Firing uses endurance",
}
