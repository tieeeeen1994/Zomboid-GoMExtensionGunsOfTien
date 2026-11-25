--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Skorpion vz. 82 and its magazines
    (GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own entries;
    shared/GunsOfTien/Skorpion.lua). The gun's other lines (built-in parts, magazines) are written by GunLines.lua
    from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.SKORPION"] = { "Uses 9x18mm Makarov rounds" }
for _, rounds in ipairs({ 12, 24, 30 }) do
    lines["GunsOfTien.9x18Magazine" .. rounds .. "_SKORPION"] = { "Uses 9x18mm Makarov rounds." }
end

-- the wire stock's lines, shown under the gun while it is open (Tooltips.lua; stats in shared/GunsOfTien/Skorpion.lua:
-- GoM's MAC-10 stock, worded as the Mini and Micro Uzi's)
GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates["GunsOfTien.SKORPION_Integrated_Stock_Deployed"] = {
    "Folding stock deployed:",
    "Aiming Time reduced by 3",
    "Hit Chance increased by 4%",
}
