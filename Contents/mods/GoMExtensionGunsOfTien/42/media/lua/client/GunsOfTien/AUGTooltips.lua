--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the Steyr AUG A1 and its magazines (GoM's
    tooltipsPergun table, read at render time, hard-coded English like GoM's own entries; GoM's FAMAS wording for the
    round), and its folding front grip's lines, shown under the gun while the grip is unfolded (Tooltips.lua; stats in
    shared/GunsOfTien/AUG.lua: GoM's Stub Foregrip, worded as Post-93 words the MP7A1's).
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTien."

lines[M .. "AUG"] = { "Uses .223/5.56x45mm NATO rounds" }
for _, n in ipairs({ 30, 42 }) do
    lines[M .. "556x45Magazine" .. n .. "_AUG"] = { "Uses .223/5.56x45mm NATO rounds." }
end

GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates[M .. "AUG_Integrated_Foregrip_Deployed"] = {
    "Folding front grip unfolded:",
    "Aiming Time reduced by 10",
    "Critical Chance increased by 4%",
    "Hit Chance increased by 7%",
    "Automatic fire spread reduced by 15%",
}
