--[[
    Guns of Tien -- a gun's Information lines for the integrated parts fitted on it now (user, 2026-10-19: "only
    display the proper CURRENT stats if they are active")

    GoM draws `tooltipsPergun[fullType]` under an item's tooltip (MarzWeapons/CustomItemTooltips.lua), and so does
    ZomboidFixesB42's GoM tooltip fix, both reading it when the tooltip renders. The table is per gun type, but a
    stock may be deployed or folded, a selector on pump or semi, a Double Barrel's stock or a Mosin's barrel sawn off or
    not. So the lines
    of each integrated part's state are kept in GunsOfTien_TooltipStates (part full type -> lines, in GoM's
    attachment style: a heading, then one effect per line; or a function of the gun returning them):
    HandlingTooltips.lua fills it for GoM's stocks, bipods and selectors, Post-93's Tooltips.lua for the MP7's stock
    and grip, this file for the sawn-off stocks and the Mosin's sawn-off barrel. For each render of a gun its type's
    lines are set to GoM's own plus those of the parts fitted on that gun, and for a sawn-off stock whether the gun
    fits a holster now; a Mosin with its barrel sawn off loses GoM's bayonet line. A state without effects shows
    nothing.

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
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34", "MOSIN" }) do
    STATES["GunsOfTien." .. gun .. "_Stock_Sawnoff"] = SAWN
end
-- the Mosin's sawn-off barrel (SawnStock.BARREL_HANDLING, BARREL_SIGHTS / OBREZ_SIGHTS against GoM's 20-28)
STATES["GunsOfTien.MOSIN_Barrel_Sawnoff"] = function(item)
    return {
        "Sawn-off barrel:",
        "Damage reduced by 15%",
        "Hit Chance reduced by 17%",
        "Aiming Time reduced by 36%",
        "Recoil Delay increased by 20%",
        SawnStock and SawnStock.IsSawn(item) and "Sight Range reduced to 2-9 tiles" or "Sight Range reduced to 4-12 tiles",
        "Range reduced by 50%",
        "Sound Radius and Volume increased by 35%",
        "Larger Muzzle Flash",
    }
end
-- the sawn-off barrels, in GoM's attachment style (user, 2026-10-19). GoM's stats on the Double Barrel's,
-- SawnStock.lua's copy on the other two: Aiming Time 30, Hit Chance 70, spread 2.0, range 15 against the guns'
-- 40 / 65 / 0.6 / 20. GoM gives these parts no lines of its own.
local SAWN_BARRELS = {
    "Aiming Time reduced by 25%",
    "Hit Chance increased by 8%",
    "Pellet spread increased by 233%",
    "Range reduced by 25%",
}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34" }) do
    for _, side in ipairs({ "Close", "Open" }) do
        lines["MarzGuns." .. gun .. "_Barrel_Sawnoff_" .. side] = SAWN_BARRELS
    end
end
-- AWC's Mk9 and its mount device (shared/GunsOfTien/Suppressors.lua), worded as GoM words its 9mm and .45 ones; the
-- guns that take them get GoM's "Compatible Muzzle Device" line (Post-93's Tooltips.lua for the UMP9)
lines["GunsOfTien.Mk9_Suppressor"] = {
    "Requires 9x19mm SMG Muzzle Mount",
    "Sound Radius and Volume reduced by 70%",
    "Damage reduced by 10%",
    "Aiming Time increased by 10%",
    "Removes Muzzle Flash",
    "Can be mounted on 9x19mm SMGs",
    "Needs Wrench to install or remove.",
}
lines["GunsOfTien.SMG9_Muzzle_Mount_Device"] = {
    "No Direct Stat Changes",
    "Enables 9x19mm SMG Muzzle Attachments",
    "Needs Wrench to install or remove.",
}
for _, gun in ipairs({ "MarzGuns.MP5", "MarzGuns.MP5A2" }) do
    if type(lines[gun]) == "table" then
        table.insert(lines[gun], "Compatible Muzzle Device: 9x19mm SMG Muzzle Mount")
    end
end
local FITS_HOLSTER = "Fits a holster."
local NEEDS_BARRELS = "Fits a holster if barrels are sawed off."
local NEEDS_BARREL = "Fits a holster if the barrel is sawed off."

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
            if type(state) == "function" then state = state(item) end
            if state then
                for _, line in ipairs(state) do add[#add + 1] = line end
            end
        end
    end
    local noBayonet = false
    if SawnStock and SawnStock.IsSawn(item) then
        local entry = SawnStock.Entry(item)
        add[#add + 1] = SawnStock.FitsHolster(item) and FITS_HOLSTER or (entry.sawnBarrel and NEEDS_BARREL or NEEDS_BARRELS)
    end
    if SawnStock and SawnStock.Entry(item) and SawnStock.Entry(item).sawnBarrel and SawnStock.IsBarrelSawn(item) then
        noBayonet = true
    end

    local fullType = item:getFullType()
    if #add == 0 and not base[fullType] then return end
    if not base[fullType] then base[fullType] = copy(lines[fullType]) end
    local list = {}
    for _, line in ipairs(base[fullType]) do
        if not (noBayonet and type(line) == "string" and line:lower():find("bayonet")) then list[#list + 1] = line end
    end
    for _, line in ipairs(add) do list[#list + 1] = line end
    lines[fullType] = #list > 0 and list or nil
end

--- "Subject: Detail" lines end without a full stop (user, 2026-10-19), GoM's own included ("Compatible Muzzle
--- Device: AR Muzzle Mount."). A line with a second sentence on either side of the colon is left as it is.
local function dropSubjectStops(list)
    for i, line in ipairs(list) do
        local subject, detail
        if type(line) == "string" then subject, detail = line:match("^([^:]+): (.+)%.$") end
        if subject and not subject:find("%. ") and not detail:find("%. ") and not detail:find(":") then
            list[i] = subject .. ": " .. detail
        end
    end
end

local function dropAllSubjectStops()
    for _, tbl in ipairs({ lines, STATES }) do
        for _, list in pairs(tbl) do
            if type(list) == "table" then dropSubjectStops(list) end
        end
    end
end
-- now for GoM's and this mod's files loaded so far, again on the first tick for every mod loaded after (Post-93)
dropAllSubjectStops()

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
    dropAllSubjectStops()
    wrap(ISToolTipInv)
    wrap(ISToolTipItemSlot)
end

Events.OnGameStart.Add(function()
    Events.OnTick.Add(install)
end)
