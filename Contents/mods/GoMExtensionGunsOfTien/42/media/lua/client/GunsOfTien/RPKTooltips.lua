--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the RPK, the RPK-74 and the RPK's 40-round
    magazine (GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; GoM's AK-47
    and AK-74 wording), and the bipod's lines, shown under the gun while it is deployed (Tooltips.lua; stats in
    shared/GunsOfTien/RPK.lua, GoM's rail bipod's, worded as HandlingTooltips.lua words that bipod).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "RPK"] = {
    "Uses 7.62x39mm rounds.",
    "Compatible Magazines: RPK 40Rds, RPK 75Rds Drum, AK-47",
    "Compatible Mounting Device: AK Mount",
    "Compatible Muzzle Device: AK Muzzle Mount",
}
lines[M .. "RPK74"] = {
    "Uses 5.45x39mm rounds.",
    "Compatible Magazines: AK-74",
    "Compatible Mounting Device: AK Mount",
    "Compatible Muzzle Device: AK Muzzle Mount",
}
lines[M .. "762x39Magazine40_RPK"] = { "Uses 7.62x39mm rounds.", "Fits the RPK and AK-47" }
lines[M .. "762x39Drum75_RPK"] = { "Uses 7.62x39mm rounds.", "Fits the RPK and AK-47" }

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates[M .. "RPK_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 10%",
    "Critical and Hit Chance increased by 15%",
    "Automatic fire spread reduced by 35%",
}
