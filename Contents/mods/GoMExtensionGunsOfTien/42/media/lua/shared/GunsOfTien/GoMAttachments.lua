--[[
    Guns of Tien -- Guns of Marz attachments that are offered but drawn nowhere, or not offered where they are meant
    to be (attachment audit, docs/attachments_audit.md; user, 2026-11-23: "we can add the missing model lines. we also
    need to render the picatinny rail... some guns however seem like they shouldn't support bipods... if you find
    yourself needing to overlap from the foregrip, let's drop the bipod support").

    - AA-12: GoM lets its Left and Right Picatinny Rails, its two weapon lights and two lasers on, but the gun has no
      point and no model line for any of them, so they were fitted invisibly. Points are added to GoM's AA12 model
      at the shroud's sides at the bottom rail's distance along the barrel (scripts/gom_points.py: each rail sunk
      1.1 into the shroud as GoM sinks its rails; light and laser at the M16A2's offsets from its rails, clear of the
      shroud), and the model lines to the gun.
    - Bipods: GoM's rail bipod fits on the bottom rail of the G36, G36C, M4A1, XM177, MP5, MP5A2 and MP5SD, and none of
      them draws it. Placed as GoM places it on the M16A2 (the same distance from the rail's front), it clears the
      foregrips on the G36 only; on the M4A1, XM177 and the three MP5s it overlaps them by 15 mm, and the G36C has
      no bottom rail point at all (too short, user). The G36 gets a `bipod` point and its model lines; the other six
      lose the bipods (MountOn), and bipods already on such guns come off beside the gun (server/GunsOfTien/
      RemovedParts.lua, from GunsOfTien_RemovedParts).
    - M16A2: its spawn table fits the AimRight laser on its right rail (2%), but the laser's MountOn leaves it out
      (the LRX-7 has it). Added.
    - CAR-15: the foregrips' MountOn lists it, but its bottom is taken by its integrated M203 and it never gets a
      bottom rail, so they could never be fitted. Taken out of their MountOn (nothing to take off existing guns).
    - PSG-1 and SVD: GoM's spawn tables give them the Stub / MKC / MK2 foregrips on the bottom rail (2%) and their
      items draw them, but the foregrips' MountOn leaves both out (user, 2026-11-23: "add support"). Added; the
      PSG-1 model also gets the `foregrip` point it lacks, at the G3's offset from the bottom rail.

    Model points are set on GoM's loaded ModelScripts (a model block cannot be declared again from another mod: it
    resets the mesh and texture), as MuzzlePoints.lua does. Item scripts get their model lines with Item.DoParam,
    which appends even when the part type is already listed, so each script object is patched once. MountOn lists
    are read from an instance and written back whole (DoParam replaces the list), as Rails.lua does. Scripts are
    rebuilt on leaving a game, so all of it runs again at every world load. This file loads before Lasers.lua, so the
    laser beam lines Lasers.lua adds for every gun on a laser's MountOn include the M16A2's AimRight one.
--]]

local GoMAttachments = {}

local BIPODS = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }

-- gun -> parts it no longer takes. Read by RemovedParts.lua to take them off guns saved with them fitted.
GunsOfTien_RemovedParts = GunsOfTien_RemovedParts or {}
for _, gun in ipairs({ "MarzGuns.G36C", "MarzGuns.M4A1", "MarzGuns.XM177", "MarzGuns.MP5", "MarzGuns.MP5A2",
    "MarzGuns.MP5SD" }) do
    GunsOfTien_RemovedParts[gun] = BIPODS
end
GunsOfTien_RemovedParts["MarzGuns.CAR15"] = FOREGRIPS

-- part -> guns taken out of / added to its MountOn
local MOUNT_REMOVE = {}
for gun, parts in pairs(GunsOfTien_RemovedParts) do
    for _, part in ipairs(parts) do
        MOUNT_REMOVE[part] = MOUNT_REMOVE[part] or {}
        table.insert(MOUNT_REMOVE[part], gun)
    end
end
local MOUNT_ADD = {
    ["MarzGuns.AimRight_Laser"] = { "MarzGuns.M16A2" },
}
for _, grip in ipairs(FOREGRIPS) do
    MOUNT_ADD[grip] = { "MarzGuns.PSG1", "MarzGuns.SVD" }
end

-- gun model -> new points (offset in the model's space, rotation 0 as every GoM rail point), measured by
-- scripts/gom_points.py
local POINTS = {
    ["MarzGuns.AA12"] = {
        rail_left = { 0.0173, 0.2084, 0.0200 },
        rail_right = { -0.0180, 0.2084, 0.0200 },
        light_left = { 0.0241, 0.2237, 0.0195 },
        laser_right = { -0.0235, 0.2211, 0.0195 },
    },
    ["MarzGuns.G36"] = {
        bipod = { 0.0000, 0.2881, -0.0005 },
    },
    -- the G3's foregrip-to-bottom-rail offset (-0.0463, -0.0046) applied to the PSG-1's bottom rail; GoM's PSG1 model
    -- has no foregrip point although its item draws the three foregrips there
    ["MarzGuns.PSG1"] = {
        foregrip = { 0.0000, 0.2282, 0.0053 },
    },
    -- where a three-lug can or flash hider stops on GoM's MP5 and MP5A2 (Suppressors.lua, MuzzleFamilies.lua): the
    -- front face of the front sight housing on the bore axis, measured on GoM's meshes of its November 2026 update
    -- (build_mk9.py's rule; until then our own MP5 models carried it)
    ["MarzGuns.MP5"] = {
        canon = { 0.0000, 0.2178, 0.0301 },
    },
    ["MarzGuns.MP5A2"] = {
        canon = { 0.0000, 0.2190, 0.0325 },
    },
}

-- gun item -> { part, model, point } model lines it is given (GoM's own models, at GoM's point names)
local LINES = {
    ["MarzGuns.AA12"] = {
        { "MarzGuns.Picatinny_Rail_Left", "MarzGuns.Picatinny_Rail_Left", "rail_left" },
        { "MarzGuns.Picatinny_Rail_Right", "MarzGuns.Picatinny_Rail_Right", "rail_right" },
        { "MarzGuns.BrightPoint-5_Light", "MarzGuns.BrightPoint-5_Light", "light_left" },
        { "MarzGuns.SR7_Light", "MarzGuns.SR7_Light", "light_left" },
        { "MarzGuns.AimRight_Laser", "MarzGuns.AimRight_Laser", "laser_right" },
        { "MarzGuns.LRX-7_Laser", "MarzGuns.LRX-7_Laser", "laser_right" },
    },
    ["MarzGuns.G36"] = {
        { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Deployed", "bipod" },
        { "MarzGuns.Bipod_Folded", "MarzGuns.Bipod_Folded", "bipod" },
    },
}

local function mountOnOf(partType)
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list = {}
    if current then
        for i = 0, current:size() - 1 do list[#list + 1] = tostring(current:get(i)) end
    end
    return list
end

local function editMountOn(partType, remove, add)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local drop = {}
    for _, gun in ipairs(remove or {}) do drop[gun] = true end
    local list, seen, changed = {}, {}, false
    for _, gun in ipairs(mountOnOf(partType)) do
        if drop[gun] then
            changed = true
        elseif not seen[gun] then
            seen[gun] = true
            list[#list + 1] = gun
        end
    end
    for _, gun in ipairs(add or {}) do
        if not seen[gun] and ScriptManager.instance:getItem(gun) then
            seen[gun] = true
            list[#list + 1] = gun
            changed = true
        end
    end
    if changed then script:DoParam("MountOn = " .. table.concat(list, ";")) end
end

local function addPoints()
    local manager = ScriptManager.instance
    for modelName, points in pairs(POINTS) do
        local model = manager:getModelScript(modelName)
        if not model then
            if not isServer() then print("[GunsOfTien] GoM attachments: model script not found: " .. modelName) end
        else
            for id, o in pairs(points) do
                local point = model:getAttachmentById(id)
                if not point then
                    point = ModelAttachment.new(id)
                    model:addAttachment(point)
                end
                point:getOffset():set(o[1], o[2], o[3])
                point:getRotate():set(0, 0, 0)
            end
        end
    end
end

local patched = {}       -- gun item scripts given their lines (scripts are new objects after a reload)

local function addLines()
    for gun, lines in pairs(LINES) do
        local script = ScriptManager.instance:getItem(gun)
        if script and not patched[script] then
            patched[script] = true
            for _, line in ipairs(lines) do
                script:DoParam("ModelWeaponPart = " .. line[1] .. " " .. line[2] .. " " .. line[3] .. " " .. line[3])
            end
        end
    end
end

local function apply()
    local parts = {}
    for part in pairs(MOUNT_REMOVE) do parts[part] = true end
    for part in pairs(MOUNT_ADD) do parts[part] = true end
    for part in pairs(parts) do
        editMountOn(part, MOUNT_REMOVE[part], MOUNT_ADD[part])
    end
    addPoints()
    addLines()
end

Events.OnGameBoot.Add(apply)
Events.OnInitGlobalModData.Add(apply)
-- and at once (user, 2026-11-25): GoM's guns are in its parts' MountOn from the script files on, and a mod that
-- lists a gun's slots from MountOn when its own Lua loads (before OnGameBoot) missed ours
pcall(apply)

-- MuzzleFamilies.lua adds its muzzle parts to these three before the events fire
GoMAttachments.POINTS = POINTS
GoMAttachments.LINES = LINES
GoMAttachments.MOUNT_ADD = MOUNT_ADD
return GoMAttachments
