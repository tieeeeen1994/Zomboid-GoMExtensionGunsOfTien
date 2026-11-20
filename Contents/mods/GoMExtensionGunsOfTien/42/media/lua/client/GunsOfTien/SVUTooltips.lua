--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the SVU (GoM's tooltipsPergun table, read
    at render time, hard-coded English like GoM's own entries; GoM's SVD wording without its rail line: the 1991 SVU
    has no rail under the handguard). GoM's SVD magazine names its gun list only by calibre, so it is left alone.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

tooltips.tooltipsPergun["GunsOfTien.SVU"] = {
    "Uses 7.62x54mmR rounds.",
    "Compatible Magazines: SVD",
    "Compatible Mounting Device: AK Mount",
}
