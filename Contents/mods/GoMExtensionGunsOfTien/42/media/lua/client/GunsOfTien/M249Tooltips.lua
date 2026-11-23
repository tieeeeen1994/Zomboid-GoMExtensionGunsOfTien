--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the M249, its 200-round box and the belt
    links both belt boxes take (GoM's tooltipsPergun table, read at render time, hard-coded English like GoM's own
    entries), and its bipod's lines, shown under the gun while that state is fitted (Tooltips.lua; stats in shared/GunsOfTien/M249.lua, GoM's M60
    bipod's, worded as HandlingTooltips.lua words the M60's).
    The gun's other lines (rails, mounts, built-in parts, magazines) are written by GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.M249"] = { "Uses .223/5.56x45mm NATO rounds" }
lines["GunsOfTien.556x45Box200_M249"] = { "Uses .223/5.56x45mm NATO rounds." }

-- The link line of each belt box (GoM's M60 box is a belt too: its own lines, then ours), only while the sandbox
-- option BeltLinks is on (shared/GunsOfTien/BeltLinks.lua). Known from the world load on, so set at OnGameStart, taken
-- out first so that another world loaded in the same session starts clean.
local LINK_LINES = {
    ["GunsOfTien.556x45Box200_M249"] = "Takes one M27 Belt Link per round",
    ["MarzGuns.762x51Box100_M60"] = "Takes one M13 Belt Link per round",
}

local function setLinkLines()
    local BeltLinks = GunsOfTien_BeltLinks
    local enabled = BeltLinks ~= nil and BeltLinks.isEnabled()
    for box, text in pairs(LINK_LINES) do
        local list = lines[box] or {}
        for i = #list, 1, -1 do
            if list[i] == text then table.remove(list, i) end
        end
        if enabled then list[#list + 1] = text end
        lines[box] = list
    end
end

Events.OnGameStart.Add(setLinkLines)

-- GoM's bipods change no stats since its November 2026 update (the M60's, BAR's and M24's, its rail bipod but for
-- its spread), so this bipod's states show no lines (Tooltips.lua shows nothing for a state without effects)
