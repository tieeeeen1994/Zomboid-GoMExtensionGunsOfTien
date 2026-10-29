--[[
    Guns of Tien -- our guns hang the right way up on modded attachment slots too (user, 2026-10-30), for both mods'
    models.

    An attached item is drawn at the body's point for its location, then turned by the item model's own attachment of
    the **same name** (42.21 `AnimatedModel$AnimatedModelInstanceRenderData.transformToParent`, looked up in the model
    script on every frame through `ModelInstance.getAttachmentById`). Body points expect the model their slot type is
    made for: rifle points an upright rifle, holster points a gun modelled upside down like GoM's pistols. So the
    MP7s and the P90 (held like pistols, modelled upside down, AttachmentType Rifle) carry `rifle_back` /
    `rifle_back_bag` turns, and the sawn-off shotguns (upright, AttachmentType Holster) `holster_right` / `holster_left`
    / `ShoulderHolster` ones. A modded slot names its own points (Plysken Attachments Reborn: `<Bag>_rifle` per
    backpack), which found no attachment and showed the gun upside down.

    Done from the slot table instead of a list of mods: every `ISHotbarAttachDefinition` slot maps an AttachmentType to a
    location, whose body point is `AttachedLocations.getGroup("Human"):getLocation(id):getAttachmentName()`. Points
    reached by one type form a group; a model of ours with an attachment for one point of a group gets a copy of it for
    each point of that group it lacks (never replacing one it has). Models with none need no turn and get none.

    Sandbox option `GunsOfTien.ModdedSlotsUpright` (default on), read when it runs: model scripts are rebuilt when a
    world loads (so turning it off needs nothing removed, and a change applies from the next load), and this runs at
    OnGameStart and once more on the first tick (slots a mod adds in its own OnGameStart). Tien's Attachment Positions copies every model's attachment of a point onto its
    per-player `<point>@<ns>` points when the server first answers, after both. Rendering is client only: nothing runs
    on a dedicated server.
--]]

require("Hotbar/ISHotbarAttachDefinition")

local MODULES = { "GunsOfTien.", "GunsOfTienPost93." }

local function isOurs(script)
    -- a model block re-declared by another mod is reset (ModelScript.reset) and can lack its name
    local ok, fullType = pcall(function() return script:getFullType() end)
    if not ok or type(fullType) ~= "string" then return false end
    for _, prefix in ipairs(MODULES) do
        if fullType:sub(1, #prefix) == prefix then return true end
    end
    return false
end

-- AttachmentType -> body point names reached through it, in slot order, each once
local function pointGroups()
    local group = AttachedLocations.getGroup("Human")
    local groups, seen = {}, {}
    for _, slot in ipairs(ISHotbarAttachDefinition or {}) do
        for attachmentType, locationId in pairs(type(slot) == "table" and type(slot.attachments) == "table"
                and slot.attachments or {}) do
            local location = type(locationId) == "string" and group:getLocation(locationId)
            local point = location and location:getAttachmentName()
            if type(point) == "string" and point ~= "" then
                seen[attachmentType] = seen[attachmentType] or {}
                if not seen[attachmentType][point] then
                    seen[attachmentType][point] = true
                    groups[attachmentType] = groups[attachmentType] or {}
                    table.insert(groups[attachmentType], point)
                end
            end
        end
    end
    return groups
end

local function copyAttachment(script, from, id)
    local copy = ModelAttachment.new(id)
    if from:getBone() then copy:setBone(from:getBone()) end
    local o, r = from:getOffset(), from:getRotate()
    copy:getOffset():set(o:x(), o:y(), o:z())
    copy:getRotate():set(r:x(), r:y(), r:z())
    copy:setScale(from:getScale())
    copy:setZOffset(from:getZOffset())
    script:addAttachment(copy)
end

local function isEnabled()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.ModdedSlotsUpright == true
end

local function turnModels()
    if not isEnabled() then return end
    local all = getScriptManager():getAllModelScripts()
    local groups = pointGroups()
    local added = 0
    for i = 0, all:size() - 1 do
        local script = all:get(i)
        if isOurs(script) then
            for _, points in pairs(groups) do
                local template
                for _, point in ipairs(points) do
                    template = script:getAttachmentById(point)
                    if template then break end
                end
                if template then
                    for _, point in ipairs(points) do
                        if not script:getAttachmentById(point) then
                            copyAttachment(script, template, point)
                            added = added + 1
                        end
                    end
                end
            end
        end
    end
    if added > 0 then
        print("[GunsOfTien] slot turns: " .. added .. " slot points given our guns' turns")
    end
end

local function onFirstTick()
    Events.OnTick.Remove(onFirstTick)
    turnModels()
end

Events.OnGameStart.Add(function()
    turnModels()
    Events.OnTick.Add(onFirstTick)
end)
