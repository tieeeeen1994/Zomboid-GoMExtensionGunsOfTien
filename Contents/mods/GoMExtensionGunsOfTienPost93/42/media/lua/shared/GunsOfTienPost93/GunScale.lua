--[[
    Guns of Tien - Post-93 -- our guns in the M16A2's proportion, as the main mod's GunScale.lua does for every gun
    (TODO.md "Gun scale audit"). They were built at 0.65 (rifles) and 0.72 (SMGs, pistols) of their real length.
    The SCAR-L takes STANAG magazines, so it shares the M16A2's 1.00 (strict, open in TODO.md); the SCAR-H its own.
    Not yet: the MP7s and the P90, on our own clips solved for today's sizes.
--]]

local GunScale = require("GunsOfTien/GunScale")

local M = "GunsOfTienPost93."
GunScale.add({
    [M .. "SCARL"] = 1.00,
    [M .. "SCARH"] = 0.93,
    [M .. "UMP45"] = 0.83,
    [M .. "UMP9"] = 0.83,
    [M .. "UCP"] = 0.84,
    [M .. "FIVESEVEN"] = 0.84,      -- the Five-seveN item is MarzGuns.FIVESEVEN, its model ours
})
