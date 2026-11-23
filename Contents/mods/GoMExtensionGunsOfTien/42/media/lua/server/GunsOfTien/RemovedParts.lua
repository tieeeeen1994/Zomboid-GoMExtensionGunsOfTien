--[[
    Guns of Tien -- parts a gun no longer takes come off guns saved with them fitted, and lie beside the gun in the
    same container (user, 2026-11-23: "force existing guns whose attachment slots are taken away to uninstall itself
    from the gun and place it beside the gun in that container").

    Which parts: GunsOfTien_RemovedParts (gun full type -> part full types), filled by the files that take a slot
    away (shared/GunsOfTien/GoMAttachments.lua: GoM's rail bipod off six guns that cannot draw it without it
    overlapping the foregrip). A part taken off goes into the gun's own container (a bag inside a crate stays in that
    bag); a gun lying on the floor gets it on the floor at the same spot. Gunworks' attachment stats are applied again
    (StatsFactory.ReapplyAllModifiers, as its own removal does).

    When, on the server and in single player:
    - every chunk as it loads (LoadChunk, at the end of the chunk's load): its objects' containers, corpses and floor
      items, bags in them included. Nothing is sent: a chunk the server has just loaded is not on any client yet (it
      is served to them from the server's memory afterwards).
    - each player once, 10 s after joining (single player: the local players), and each vehicle once while it is
      loaded (checked every 5 s): those are on clients already, so the gun is synced to its owner
      (syncHandWeaponFields, which updates the client's copy in place, the one in the hands too) or re-sent to the
      players near the vehicle, and the part sent with sendAddItemToContainer.
--]]

if isClient() then return end

local okStats, StatsFactory = pcall(require, "WeaponSystems/Utils/StatsFactory")
if not okStats then StatsFactory = nil end

local function hasAny(t)
    if not t then return false end
    for _ in pairs(t) do return true end
    return false
end

local function removedFor(gunType)
    return GunsOfTien_RemovedParts and GunsOfTien_RemovedParts[gunType]
end

local function where(gun, square)
    if square then return square:getX() .. "," .. square:getY() .. "," .. square:getZ() end
    local container = gun:getContainer()
    while container and container:getContainingItem() and container:getContainingItem():getContainer() do
        container = container:getContainingItem():getContainer()
    end
    local s = container and container:getSourceGrid()
    if s then return s:getX() .. "," .. s:getY() .. "," .. s:getZ() end
    local character = container and container:getCharacter()
    if character then return tostring(character:getUsername()) end
    return "?"
end

--- Takes the parts this gun no longer takes off it, beside it. `sync`: nil (nobody has the gun yet), "owner"
--- (`owner`'s inventory) or "nearby" (a vehicle's container, sent to the players near it).
local function strip(gun, sync, owner)
    local removed = removedFor(gun:getFullType())
    if not removed then return 0 end
    local drop = {}
    for _, part in ipairs(removed) do drop[part] = true end
    local parts = {}
    local fitted = gun:getAllWeaponParts()
    for i = 0, fitted:size() - 1 do
        local part = fitted:get(i)
        if part and drop[part:getFullType()] then parts[#parts + 1] = part end
    end
    if #parts == 0 then return 0 end

    local worldItem = gun:getWorldItem()
    local square = worldItem and worldItem:getSquare()
    local container = not square and gun:getContainer() or nil
    for _, part in ipairs(parts) do
        gun:detachWeaponPart(part)
        if square then
            -- only reached from a chunk being loaded, which no client has yet: not transmitted
            square:AddWorldInventoryItem(part, worldItem:getOffX(), worldItem:getOffY(), worldItem:getOffZ(), false)
        elseif container then
            container:AddItem(part)
        end
        local okWhere, place = pcall(where, gun, square)
        print("[GunsOfTien] removed parts: took " .. part:getFullType() .. " off " .. gun:getFullType() .. " (id "
            .. tostring(gun:getID()) .. ") at " .. (okWhere and place or "?"))
    end
    if StatsFactory and StatsFactory.ReapplyAllModifiers then StatsFactory.ReapplyAllModifiers(gun) end

    if isServer() and container then
        if sync == "owner" and owner then
            syncHandWeaponFields(owner, gun)
        elseif sync == "nearby" then
            sendReplaceItemInContainer(container, gun, gun)
        end
        if sync then
            for _, part in ipairs(parts) do sendAddItemToContainer(container, part) end
        end
    end
    return #parts
end

local function checkContainer(container, sync, owner)
    if not container or not GunsOfTien_RemovedParts then return end
    for gunType in pairs(GunsOfTien_RemovedParts) do
        if container:containsTypeRecurse(gunType) then
            local guns = container:getAllTypeRecurse(gunType)
            for i = 0, guns:size() - 1 do
                local gun = guns:get(i)
                if instanceof(gun, "HandWeapon") then strip(gun, sync, owner) end
            end
        end
    end
end

-------------------------------------------------
-- Chunks as they load
-------------------------------------------------
local function checkSquare(square)
    local objects = square:getObjects()
    for i = 0, objects:size() - 1 do
        local obj = objects:get(i)
        for c = 0, obj:getContainerCount() - 1 do
            checkContainer(obj:getContainerByIndex(c))
        end
    end
    local worldObjects = square:getWorldObjects()
    for i = worldObjects:size() - 1, 0, -1 do
        local item = i < worldObjects:size() and worldObjects:get(i):getItem() or nil
        if item then
            if instanceof(item, "HandWeapon") and removedFor(item:getFullType()) then
                strip(item)
            elseif instanceof(item, "InventoryContainer") then
                checkContainer(item:getInventory())
            end
        end
    end
    local bodies = square:getDeadBodys()
    for i = 0, bodies:size() - 1 do
        checkContainer(bodies:get(i):getContainer())
    end
end

local function onLoadChunk(chunk)
    if not hasAny(GunsOfTien_RemovedParts) then return end
    for z = chunk:getMinLevel(), chunk:getMaxLevel() do
        for x = 0, 7 do
            for y = 0, 7 do
                local square = chunk:getGridSquare(x, y, z)
                if square then checkSquare(square) end
            end
        end
    end
end

Events.LoadChunk.Add(onLoadChunk)

-------------------------------------------------
-- Players once after joining, vehicles once while loaded
-------------------------------------------------
local POLL_MS = 5000
local PLAYER_SETTLE_MS = 10000
local lastPoll = 0
local players = {}       -- player -> time first seen, or true once checked
local vehicles = {}      -- vehicle -> true

local function localPlayers()
    local list = {}
    if isServer() then
        local online = getOnlinePlayers()
        for i = 0, online:size() - 1 do list[#list + 1] = online:get(i) end
    else
        for i = 0, getNumActivePlayers() - 1 do
            local p = getSpecificPlayer(i)
            if p then list[#list + 1] = p end
        end
    end
    return list
end

local function poll()
    local now = getTimestampMs()
    if now - lastPoll < POLL_MS then return end
    lastPoll = now

    local seen = {}
    for _, player in ipairs(localPlayers()) do
        local state = players[player] or now
        if state ~= true and now - state >= PLAYER_SETTLE_MS then
            checkContainer(player:getInventory(), "owner", player)
            state = true
        end
        seen[player] = state
    end
    players = seen

    local seenVehicles = {}
    local loaded = ArrayList.new()
    loaded:addAll(getCell():getVehicles())
    for i = 0, loaded:size() - 1 do
        local vehicle = loaded:get(i)
        if not vehicles[vehicle] then
            for p = 0, vehicle:getPartCount() - 1 do
                local part = vehicle:getPartByIndex(p)
                local container = part and part:getItemContainer()
                if container then checkContainer(container, "nearby") end
            end
        end
        seenVehicles[vehicle] = true
    end
    vehicles = seenVehicles
end

Events.OnTick.Add(function()
    if hasAny(GunsOfTien_RemovedParts) then poll() end
end)
