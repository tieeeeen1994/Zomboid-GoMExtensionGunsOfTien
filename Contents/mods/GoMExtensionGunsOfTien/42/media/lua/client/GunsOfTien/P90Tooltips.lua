--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the P90 with its ring sight and the P90
    family's magazine and round that moved here from Post-93 with it on 2026-11-03 (the SP90 and its mount device are
    Post-93's): GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own entries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M93 = "GunsOfTienPost93."

lines["GunsOfTien.P90"] = {
    "Uses 5.7x28mm rounds.",
    "Integrated ring sight",
    "Available Picatinny Slots: Left, Right.",
    "50-round magazine on top. Ejects spent cases downward.",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines[M93 .. "57x28Magazine50_P90"] = { "Uses 5.7x28mm rounds." }
lines[M93 .. "57x28_Bullet"] = { "SS190 steel and aluminium penetrator", "Piercing targets", "Able to hit up to 2 targets" }
