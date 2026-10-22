--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Uzi, Mini Uzi and Micro Uzi and their
    magazines (GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own entries), and their
    stocks' lines, shown under a gun while its stock is deployed (Tooltips.lua; stats in shared/GunsOfTien/Uzi.lua:
    GoM's MP5 stock on the Uzi, its MAC-10 stock on the Mini and Micro, worded as HandlingTooltips.lua words those).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

for _, gun in ipairs({ "UZI", "MINIUZI", "MICROUZI" }) do
    lines["GunsOfTien." .. gun] = {
        "Uses 9x19mm rounds.",
        "Compatible Muzzle Device: 9x19mm SMG Muzzle Mount",
    }
end
for _, n in ipairs({ 20, 25, 32, 40, 50 }) do
    lines["GunsOfTien.9x19Magazine" .. n .. "_UZI"] = { "Uses 9x19mm rounds." }
end

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates["GunsOfTien.UZI_Integrated_Stock_Deployed"] = {
    "Folding stock deployed:",
    "Aiming Time reduced by 25%",
    "Hit Chance increased by 15%",
}
for _, gun in ipairs({ "MINIUZI", "MICROUZI" }) do
    GunsOfTien_TooltipStates["GunsOfTien." .. gun .. "_Integrated_Stock_Deployed"] = {
        "Folding stock deployed:",
        "Aiming Time reduced by 10%",
        "Hit Chance increased by 10%",
    }
end
