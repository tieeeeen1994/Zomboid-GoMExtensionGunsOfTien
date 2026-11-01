--[[
    Guns of Tien -- no "Belt Round 1" .. "Belt Round 9" rows in a belt-fed gun's tooltip (reported 2026-11-02)

    The visible rounds of the M249's and GoM's M60's belts are GoM's weapon parts MarzGuns.Bullet_1..9 (PartType
    Animated1..9), fitted and taken off by ammo count (Gunworks' Animations.CheckStates). 42.21 HandWeapon.DoTooltip
    (ObjectTooltip, Layout) adds one row per entry of the gun's attachmentList, labelled "Tooltip_weapon_" ..
    getPartType() with the part's name, and Lua cannot remove a row once added. So they showed as nine rows of
    "Animated1: Bullet" (later "Belt Round 1: Bullet" through our Tooltip.json, which is kept as the fallback).

    getAllWeaponParts() returns that list itself, so for the length of each tooltip call on a HandWeapon the belt
    parts are taken out of it and put back at their places afterwards (also when the call errors). Nothing else changes:
    no detach, so no stats, model or sync. Both Lua entry points are wrapped through HandWeapon's class metatable:
    DoTooltip (vanilla's ISToolTipInv, the crafting slot tooltip, GoM's) and DoTooltipEmbedded (ZomboidFixesB42's GoM
    tooltip fix); the Java calls between them happen inside either.
--]]

local meta = __classmetatables and HandWeapon and __classmetatables[HandWeapon.class]
local index = meta and meta.__index
if not index then
    print("[GunsOfTien] BeltRoundRows: HandWeapon's methods are not reachable, belt rounds stay in gun tooltips")
    return
end

local function isBeltRound(part)
    local partType = part:getPartType()
    return partType ~= nil and string.find(partType, "^Animated%d$") ~= nil
end

--- Take the belt rounds out of the gun's part list; returns the list and { index, part } from the last one down.
local function hideBeltRounds(weapon)
    local parts = weapon:getAllWeaponParts()
    local hidden
    for i = parts:size() - 1, 0, -1 do
        local part = parts:get(i)
        if isBeltRound(part) then
            hidden = hidden or {}
            hidden[#hidden + 1] = { i, part }
        end
    end
    if not hidden then return nil end
    for _, entry in ipairs(hidden) do
        parts:remove(entry[2])
    end
    return parts, hidden
end

local function restore(parts, hidden)
    -- lowest index first, so each goes back where it was
    for k = #hidden, 1, -1 do
        parts:add(hidden[k][1], hidden[k][2])
    end
end

local function wrap(name)
    local key = "GunsOfTien_" .. name
    local original = index[key] or index[name]               -- kept, so a Lua reload does not wrap twice
    if not original then
        print("[GunsOfTien] BeltRoundRows: HandWeapon:" .. name .. " not found")
        return
    end
    index[key] = original
    index[name] = function(weapon, ...)
        local parts, hidden = hideBeltRounds(weapon)
        if not parts then return original(weapon, ...) end
        local ok, err = pcall(original, weapon, ...)
        restore(parts, hidden)
        if not ok then error(err, 0) end
    end
end

wrap("DoTooltip")
wrap("DoTooltipEmbedded")
