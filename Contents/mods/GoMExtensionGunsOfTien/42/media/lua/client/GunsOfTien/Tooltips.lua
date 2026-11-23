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
    installed at file load or OnGameStart), so the lines are set before any of them reads the table. The guns' and
    magazines' own lines are rebuilt there first (GunLines.lua), once every mod's tooltip file has loaded. Vanilla hands a
    tooltip its item with ISToolTipInv:new(item) as well as setItem, so render is the one sure place.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end
local okStock, SawnStock = pcall(require, "GunsOfTien/SawnStock")
if not okStock or type(SawnStock) ~= "table" then SawnStock = nil end

local lines = tooltips.tooltipsPergun
GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
local STATES = GunsOfTien_TooltipStates

-- the sawn-off stock (SawnStock.HANDLING, flat as GoM's attachments since November 2026)
local SAWN = {
    "Sawn-off stock:",
    "Aiming Time reduced by 10",
    "Hit Chance reduced by 8%",
    "Recoil Delay increased by 9",
}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34", "MOSIN" }) do
    STATES["GunsOfTien." .. gun .. "_Stock_Sawnoff"] = SAWN
end
-- the Mosin's sawn-off barrel (SawnStock.BARREL_HANDLING, BARREL_SIGHTS / OBREZ_SIGHTS against GoM's 20-28)
STATES["GunsOfTien.MOSIN_Barrel_Sawnoff"] = function(item)
    return {
        "Sawn-off barrel:",
        "Min Damage reduced by 0.3 and Max Damage by 0.35",
        "Hit Chance reduced by 10%",
        "Aiming Time reduced by 25",
        "Recoil Delay increased by 4",
        SawnStock and SawnStock.IsSawn(item) and "Sight Range reduced to 2-9 tiles" or "Sight Range reduced to 4-13 tiles",
        "Range reduced by 30 tiles",
        "Sound Radius increased by 75 and Volume by 90",
        "Larger Muzzle Flash",
    }
end
-- the sawn-off barrels, in GoM's attachment style (user, 2026-10-19). GoM's stats on the Double Barrel's,
-- SawnStock.lua's copy on the other two: Aiming Time 30, Hit Chance 70, spread 2.0, range 15 against the guns'
-- 40 / 65 / 0.6 / 20. GoM gives these parts no lines of its own.
local SAWN_BARRELS = {
    "Aiming Time reduced by 10",
    "Hit Chance increased by 5%",
    "Pellet spread increased by 1.4",
    "Range reduced by 5 tiles",
}
for _, gun in ipairs({ "DOUBLEBARREL", "STEVENS_555", "TOZ34" }) do
    for _, side in ipairs({ "Close", "Open" }) do
        lines["MarzGuns." .. gun .. "_Barrel_Sawnoff_" .. side] = SAWN_BARRELS
    end
end
-- Every "Can be mounted on" line below is left empty here: GunLines.lua fills it with the guns the part's MountOn
-- really lists, by name.
-- The 9mm muzzle parts (shared/GunsOfTien/Suppressors.lua) in GoM's own wording: one 9x19mm mount device (GoM's
-- Pistol mount renamed, and the main mod's old one, the same item for worlds that have it) for GoM's pistol cans and
-- AWC's Mk9; the guns that take them get their "Compatible Muzzle Device" line from GunLines.lua
local NINE_MOUNT = {
    "No Direct Stat Changes",
    "Enables 9x19mm Muzzle Attachments",
    "Needs Wrench to install or remove.",
}
lines["MarzGuns.Pistol_Muzzle_Mount_Device"] = NINE_MOUNT
lines["GunsOfTien.SMG9_Muzzle_Mount_Device"] = NINE_MOUNT
-- Effects in GoM's November 2026 wording: flat numbers for the calibre's usual gun (GoM's own lines; the stats stay
-- x0.3 sound, x0.9 damage, so the cut is that size on a gun as loud as the usual one). The Mk9 has the same stats
-- as GoM's 9mm cans (user, 2026-11-23), so it takes their lines.
for _, can in ipairs({ "MarzGuns.M&P_Suppressor", "MarzGuns.Shh9_Suppressor", "GunsOfTien.Mk9_Suppressor" }) do
    lines[can] = {
        "Requires 9x19mm Muzzle Mount",
        "Sound Radius reduced by 70 and Volume by 20",
        "Min Damage reduced by 0.05 and Max Damage by 0.1",
        "Removes Muzzle Flash",
        "Can be mounted on",
    }
end
-- GoM's AK can on the main mod's RPKs and GoM's SKS too (RPK.lua, MuzzleFamilies.lua), and Post-93's Grozas
lines["MarzGuns.PBS-1_Suppressor"] = {
    "Requires AK Muzzle Mount",
    "Sound Radius reduced by 140 and Volume by 28",
    "Min Damage reduced by 0.15 and Max Damage by 0.2",
    "Removes Muzzle Flash",
    "Can be mounted on",
}
-- GoM's .45 can on its Camp Carbine too (MuzzleFamilies.lua) and Post-93's Vector .45 Carbine
lines["MarzGuns.P45_Suppressor"] = {
    "Requires .45 Muzzle Mount",
    "Sound Radius reduced by 80 and Volume by 25",
    "Damage reduced by 0.1",
    "Removes Muzzle Flash",
    "Can be mounted on",
}
-- The real muzzle devices (shared/GunsOfTien/MuzzleFamilies.lua, MuzzleDevicesTable.lua) in the cans' wording, and
-- GoM's three AR devices the same way (it gives them only the effect). Since GoM's November 2026 update a can or
-- device needs no tool once its mount is on (OnCreate/AttachAndDetach.lua: part type Canon has none; CanonMount, the
-- mount devices, keep the wrench), and its effects are flat (GoM's own wording)
-- Each kind's bonus (MuzzleDeviceKinds.lua, user 2026-11-24) follows the sound line, in GoM's order and wording.
local KINDS = require("GunsOfTien/MuzzleDeviceKinds")
local function deviceLines(family, effect, kind)
    local out = { "Requires " .. family .. " Muzzle Mount", effect }
    for _, line in ipairs(KINDS[kind].lines) do out[#out + 1] = line end
    out[#out + 1] = "Removes Muzzle Flash"
    out[#out + 1] = "Can be mounted on"
    return out
end
for device, d in pairs(require("GunsOfTien/MuzzleDevicesTable")) do
    lines[device] = deviceLines(d.family, d.effect, d.kind)
end
for device, effect in pairs({ ["MarzGuns.LR2_Compensator"] = "Sound Radius reduced by 15 and Volume by 4",
    ["MarzGuns.LX_Flashhider"] = "Sound Radius reduced by 10 and Volume by 2",
    ["MarzGuns.Trix42_Muzzlebreak"] = "Sound Radius reduced by 10 and Volume by 2" }) do
    lines[device] = deviceLines("AR", effect, KINDS.gom[device])
end
local FITS_HOLSTER = "Fits a holster"
local NEEDS_BARRELS = "Fits a holster if barrels are sawed off"
local NEEDS_BARREL = "Fits a holster if the barrel is sawed off"

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
    -- every gun's and magazine's own lines, from the live registries (GunLines.lua), before anything reads them
    if GunsOfTien_GunLines and GunsOfTien_GunLines.Build then GunsOfTien_GunLines.Build() end
    dropAllSubjectStops()
    wrap(ISToolTipInv)
    wrap(ISToolTipItemSlot)
end

Events.OnGameStart.Add(function()
    Events.OnTick.Add(install)
end)
