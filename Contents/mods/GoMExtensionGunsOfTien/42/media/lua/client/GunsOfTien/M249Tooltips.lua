--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the M249, its 200-round box and the belt
    links both belt boxes take (GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own
    entries), and its bipod's lines, shown under the gun while that state is fitted (Tooltips.lua; stats in shared/GunsOfTien/M249.lua, GoM's M60
    bipod's, worded as HandlingTooltips.lua words the M60's).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.M249"] = {
    "Uses .223/5.56x45mm NATO rounds.",
    "Compatible Magazines: M249 200Rds Box, STANAG",
    "Jam Chance doubled with STANAG magazines",
}
lines["GunsOfTien.556x45Box200_M249"] = { "Uses .223/5.56x45mm NATO rounds.", "Takes one M27 Belt Link per round" }
-- GoM's M60 box is a belt too (shared/GunsOfTien/BeltLinks.lua): its own lines, then ours
local m60 = lines["MarzGuns.762x51Box100_M60"] or {}
local listed = false
for _, line in ipairs(m60) do
    if line == "Takes one M13 Belt Link per round" then listed = true end
end
if not listed then m60[#m60 + 1] = "Takes one M13 Belt Link per round" end
lines["MarzGuns.762x51Box100_M60"] = m60

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates["GunsOfTien.M249_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 30%",
    "Critical and Hit Chance increased by 10%",
    "No endurance used to fire",
}
GunsOfTien_TooltipStates["GunsOfTien.M249_Integrated_Bipod_Folded"] = {
    "Folding bipod folded:",
    "Hit Chance reduced by 20%",
    "Firing uses endurance",
}
