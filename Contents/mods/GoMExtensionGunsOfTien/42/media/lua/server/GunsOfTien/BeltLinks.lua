--[[
    Guns of Tien -- Ammo Maker's clean-up for dropped links (shared/GunsOfTien/BeltLinks.lua).
    Ammo Maker drops a fired link with its casing as the shot's extra item, and puts both on its clean-up list
    (ammoMakerItemCleanUpAddModData: with Hot Brass when Persistent Casings is on, without it always), which every ten
    in-game minutes removes items older than its DroppedCasingsLifetime option (hours, 0 = never). Its removal
    compares "ammomaker." .. getType() with the listed type, so only its own items are ever removed, and an entry on
    a square that holds any other item is kept for good. The shared file sends links here instead; they are removed
    on the same schedule and lifetime (one link of the type on the square), and an entry is dropped once its square is
    loaded and old enough, whether or not the link was still there. Nothing is noted while the lifetime is 0.
--]]

if isClient() then return end

local BeltLinks = GunsOfTien_BeltLinks
local KEY = "GunsOfTien_DroppedLinks"

local function lifetimeHours()
    local vars = SandboxVars.ammomakerOptions
    return vars and tonumber(vars.DroppedCasingsLifetime) or 0
end

function BeltLinks.noteDropped(link, x, y, z)
    if lifetimeHours() <= 0 then return end
    local list = ModData.getOrCreate(KEY)
    list[#list + 1] = { link = link, x = x, y = y, z = z, t = getWorld():getWorldAgeDays() }
end

local function removeOne(square, link)
    local objects = square:getWorldObjects()
    for j = objects:size() - 1, 0, -1 do
        local object = objects:get(j)
        local item = object:getItem()
        if item and item:getFullType() == link then
            -- as Ammo Maker removes its casings
            square:transmitRemoveItemFromSquare(object)
            object:removeFromWorld()
            object:removeFromSquare()
            return
        end
    end
end

local function cleanUp()
    local hours = lifetimeHours()
    if hours <= 0 then return end
    local list = ModData.get(KEY)
    if not list or #list == 0 then return end
    local oldest = getWorld():getWorldAgeDays() - hours / 24
    local cell = getCell()
    local kept = {}
    for _, entry in ipairs(list) do
        local square = entry.t < oldest and cell:getGridSquare(entry.x, entry.y, entry.z)
        if square then
            removeOne(square, entry.link)
        else
            kept[#kept + 1] = entry
        end
    end
    if #kept == #list then return end
    for i = #list, 1, -1 do list[i] = nil end
    for i, entry in ipairs(kept) do list[i] = entry end
end

Events.EveryTenMinutes.Add(cleanUp)
