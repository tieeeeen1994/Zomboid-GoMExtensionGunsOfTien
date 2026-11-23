--[[
    Guns of Tien -- parts a gun no longer takes come off guns saved with them fitted, and lie beside the gun in the
    same container (user, 2026-11-23: "force existing guns whose attachment slots are taken away to uninstall itself
    from the gun and place it beside the gun in that container"); parts merged into another item are swapped for it,
    fitted or loose (user, 2026-11-23, the 9mm mount devices merged: "how do we migrate existing worlds into it?").

    Which parts: GunsOfTien_RemovedParts (gun full type -> part full types), filled by the files that take a slot
    away (shared/GunsOfTien/GoMAttachments.lua: GoM's rail bipod off six guns that cannot draw it without it
    overlapping the foregrip). A part taken off goes into the gun's own container (a bag inside a crate stays in that
    bag); a gun lying on the floor gets it on the floor at the same spot. Gunworks' attachment stats are applied again
    (StatsFactory.ReapplyAllModifiers, as its own removal does).
    GunsOfTien_ReplacedParts (old part full type -> new part full type), filled by the file that merged them
    (shared/GunsOfTien/Suppressors.lua: the main mod's 9x19mm SMG mount device -> GoM's 9mm mount): on a gun (any gun
    the old part's MountOn names) the old part is detached and a new one attached in its place; a loose one is taken
    out of its container (or off the floor) and a new one put in the same place. The old item stays defined and works
    as the new one meanwhile, so anything this misses still works.

    Sandbox option UpdateSavedParts ("Update Parts on Saved Guns", on by default; user, 2026-11-23: "let's just add a
    sandbox option that turns it off"), read live: off, nothing is checked (the old mount still works as GoM's).

    When, on the server and in single player:
    - every chunk as it loads (LoadChunk, at the end of the chunk's load): its objects' containers, corpses and floor
      items, bags in them included. Nothing is sent: a chunk the server has just loaded is not on any client yet (it
      is served to them from the server's memory afterwards).
    - each player once, 10 s after joining (single player: the local players), and each vehicle once while it is
      loaded (checked every 5 s): those are on clients already, so the gun is synced to its owner
      (syncHandWeaponFields, which updates the client's copy in place, the one in the hands too) or re-sent to the
      players near the vehicle, and the part sent with sendAddItemToContainer (a swapped loose part: removed with
      sendRemoveItemFromContainer, its replacement added).
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

local function replacedParts()
    return GunsOfTien_ReplacedParts or {}
end

local function isEnabled()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.UpdateSavedParts == true
end

local function anyWork()
    return isEnabled() and (hasAny(GunsOfTien_RemovedParts) or hasAny(GunsOfTien_ReplacedParts))
end

-- old part -> the gun full types its MountOn names (read once per world: scripts are rebuilt on leaving a game, and
-- every MountOn is appended by OnInitGlobalModData, before any chunk loads)
local gunsTakingCache = {}
Events.OnInitGlobalModData.Add(function() gunsTakingCache = {} end)

local function gunsTaking(partType)
    local list = gunsTakingCache[partType]
    if not list then
        list = {}
        local item = instanceItem(partType)
        local mountOn = item and item.getMountOn and item:getMountOn()
        if mountOn then
            for i = 0, mountOn:size() - 1 do list[#list + 1] = tostring(mountOn:get(i)) end
        end
        gunsTakingCache[partType] = list
    end
    return list
end

local function where(item, square)
    if square then return square:getX() .. "," .. square:getY() .. "," .. square:getZ() end
    local container = item:getContainer()
    while container and container:getContainingItem() and container:getContainingItem():getContainer() do
        container = container:getContainingItem():getContainer()
    end
    local s = container and container:getSourceGrid()
    if s then return s:getX() .. "," .. s:getY() .. "," .. s:getZ() end
    local character = container and container:getCharacter()
    if character then return tostring(character:getUsername()) end
    return "?"
end

local function log(text, item, square)
    local okWhere, place = pcall(where, item, square)
    print("[GunsOfTien] removed parts: " .. text .. " at " .. (okWhere and place or "?"))
end

--- Takes the parts this gun no longer takes off it, beside it, and swaps merged parts for their replacement.
--- `sync`: nil (nobody has the gun yet), "owner" (`owner`'s inventory) or "nearby" (a vehicle's container, sent to
--- the players near it).
local function strip(gun, sync, owner)
    local drop = {}
    for _, part in ipairs(removedFor(gun:getFullType()) or {}) do drop[part] = true end
    local replace = replacedParts()
    local parts, swaps = {}, {}
    local fitted = gun:getAllWeaponParts()
    for i = 0, fitted:size() - 1 do
        local part = fitted:get(i)
        local partType = part and part:getFullType()
        if partType and drop[partType] then
            parts[#parts + 1] = part
        elseif partType and replace[partType] then
            swaps[#swaps + 1] = part
        end
    end
    if #parts == 0 and #swaps == 0 then return 0 end

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
        log("took " .. part:getFullType() .. " off " .. gun:getFullType() .. " (id " .. tostring(gun:getID()) .. ")",
            gun, square)
    end
    for _, part in ipairs(swaps) do
        local new = instanceItem(replace[part:getFullType()])
        if new then
            gun:detachWeaponPart(part)
            gun:attachWeaponPart(new)
            log("swapped " .. part:getFullType() .. " for " .. new:getFullType() .. " on " .. gun:getFullType()
                .. " (id " .. tostring(gun:getID()) .. ")", gun, square)
        end
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
    return #parts + #swaps
end

--- A loose merged part in a container: out, its replacement in, in the same container.
local function swapLoose(item, sync)
    local container = item:getContainer()
    local new = container and instanceItem(replacedParts()[item:getFullType()])
    if not new then return end
    log("swapped loose " .. item:getFullType() .. " (id " .. tostring(item:getID()) .. ") for " .. new:getFullType(),
        item)
    container:DoRemoveItem(item)
    container:AddItem(new)
    if isServer() and sync then
        sendRemoveItemFromContainer(container, item)
        sendAddItemToContainer(container, new)
    end
end

local function checkContainer(container, sync, owner)
    if not container then return end
    local gunTypes = {}
    for gunType in pairs(GunsOfTien_RemovedParts or {}) do gunTypes[gunType] = true end
    for partType in pairs(replacedParts()) do
        for _, gunType in ipairs(gunsTaking(partType)) do gunTypes[gunType] = true end
        if container:containsTypeRecurse(partType) then
            local loose = container:getAllTypeRecurse(partType)
            for i = 0, loose:size() - 1 do swapLoose(loose:get(i), sync) end
        end
    end
    for gunType in pairs(gunTypes) do
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
    local replace = replacedParts()
    local worldObjects = square:getWorldObjects()
    for i = worldObjects:size() - 1, 0, -1 do
        local worldItem = i < worldObjects:size() and worldObjects:get(i) or nil
        local item = worldItem and worldItem:getItem()
        if item then
            if instanceof(item, "HandWeapon") then
                strip(item)
            elseif instanceof(item, "InventoryContainer") then
                checkContainer(item:getInventory())
            elseif replace[item:getFullType()] then
                -- only reached from a chunk being loaded, which no client has yet: not transmitted
                local new = instanceItem(replace[item:getFullType()])
                if new then
                    log("swapped " .. item:getFullType() .. " (id " .. tostring(item:getID()) .. ") on the floor for "
                        .. new:getFullType(), item, square)
                    square:removeWorldObject(worldItem)
                    square:AddWorldInventoryItem(new, worldItem:getOffX(), worldItem:getOffY(), worldItem:getOffZ(),
                        false)
                end
            end
        end
    end
    local bodies = square:getDeadBodys()
    for i = 0, bodies:size() - 1 do
        checkContainer(bodies:get(i):getContainer())
    end
end

local function onLoadChunk(chunk)
    if not anyWork() then return end
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
    if anyWork() then poll() end
end)
