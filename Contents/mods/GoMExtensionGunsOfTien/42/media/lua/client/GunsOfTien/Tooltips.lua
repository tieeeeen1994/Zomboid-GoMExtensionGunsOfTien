--[[
    Guns of Tien -- a gun's Information lines for the integrated parts fitted on it now (user, 2026-10-19: "only
    display the proper CURRENT stats if they are active")

    GoM draws `tooltipsPergun[fullType]` under an item's tooltip (MarzWeapons/CustomItemTooltips.lua), and so does
    ZomboidFixesB42's GoM tooltip fix, both reading it when the tooltip renders. The table is per gun type, but a
    stock may be deployed or folded, a selector on pump or semi, a Double Barrel's stock sawn off or not. So the lines
    of each integrated part's state are kept in GunsOfTien_TooltipStates (part full type -> lines, in GoM's
    attachment style: a heading, then one effect per line): HandlingTooltips.lua fills it for GoM's stocks, bipods
    and selectors, Post-93's Tooltips.lua for the MP7's stock and grip, this file for the sawn-off stocks. For each
    render of a gun its type's lines are set to GoM's own plus those of the parts fitted on that gun, and for a
    sawn-off stock whether the gun fits a holster now. A state without effects shows nothing.

    The wrappers go on the first tick after the game starts, on top of every mod's tooltip render (theirs are
    installed at file load or OnGameStart), so the lines are set before any of them reads the table. Vanilla hands a
    tooltip its item with ISToolTipInv:new(item) as well as setItem, so render is the one sure place.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end
local okStock, SawnStock = pcall(require, "GunsOfTien/SawnStock")
if not okStock or type(SawnStock) ~= "table" then SawnStock = nil end

local lines = tooltips.tooltipsPergun
GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
local STATES = GunsOfTien_TooltipStates

-- the sawn-off stock (SawnStock.HANDLING)
local SAWN = {
    "Sawn-off stock:",
    "Aiming Time reduced by 25%",
    "Hit Chance reduced by 13%",
    "Recoil Delay increased by 30%",
}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34" }) do
    STATES["GunsOfTien." .. gun .. "_Stock_Sawnoff"] = SAWN
end
local FITS_HOLSTER = "Fits a holster."
local NEEDS_BARRELS = "Fits a holster with sawn-off barrels."

local base = {}        -- gun type -> GoM's own lines, taken the first time a gun of that type has state lines

local function copy(list)
    local out = {}
    for i, line in ipairs(list or {}) do out[i] = line end
    return out
end

--- Set the gun type's lines from this gun: GoM's own, then those of the integrated parts fitted on it.
local function setLines(item)
    if not item or not instanceof(item, "HandWeapon") then return end
    local add = {}
    local parts = item:getAllWeaponParts()
    if parts then
        for i = 0, parts:size() - 1 do
            local part = parts:get(i)
            local state = part and STATES[part:getFullType()]
            if state then
                for _, line in ipairs(state) do add[#add + 1] = line end
            end
        end
    end
    if SawnStock and SawnStock.IsSawn(item) then
        add[#add + 1] = SawnStock.FitsHolster(item) and FITS_HOLSTER or NEEDS_BARRELS
    end

    local fullType = item:getFullType()
    if #add == 0 and not base[fullType] then return end
    if not base[fullType] then base[fullType] = copy(lines[fullType]) end
    local list = copy(base[fullType])
    for _, line in ipairs(add) do list[#list + 1] = line end
    lines[fullType] = #list > 0 and list or nil
end

local function wrap(class)
    if not class or class.GunsOfTien_render then return end
    class.GunsOfTien_render = class.render
    class.render = function(self, ...)
        setLines(self.item)
        return class.GunsOfTien_render(self, ...)
    end
end

local function install()
    Events.OnTick.Remove(install)
    wrap(ISToolTipInv)
    wrap(ISToolTipItemSlot)
end

Events.OnGameStart.Add(function()
    Events.OnTick.Add(install)
end)
