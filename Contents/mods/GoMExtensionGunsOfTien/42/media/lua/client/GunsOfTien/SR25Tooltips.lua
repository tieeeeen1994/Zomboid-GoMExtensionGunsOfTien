--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the SR-25 and KAC's 20 (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries, worded as RPKTooltips.lua),
    and the integrated bipod's lines, shown under the gun while it is deployed (Tooltips.lua; stats in
    shared/GunsOfTien/SR25.lua, GoM's rail bipod's without its spread line: the SR-25 is semi-automatic).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "SR25"] = {
    "Uses .308/7.62x51mm NATO rounds.",
    "Takes SR-25 pattern magazines.",
    "Integrated 3.5-10x scope and folding bipod.",
}
lines[M .. "762x51Magazine20_SR25"] = { "Uses .308/7.62x51mm NATO rounds." }

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates[M .. "SR25_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 10%",
    "Critical and Hit Chance increased by 15%",
}
