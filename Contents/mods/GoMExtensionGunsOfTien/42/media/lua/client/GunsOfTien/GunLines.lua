--[[
    Guns of Tien -- every gun's and magazine's Information lines, written from what the game really allows (attachment
    audit, docs/attachments_audit.md; user, 2026-11-23: "I want the mod to be consistent. I don't want it to keep
    inventing new information bloat and formats").

    The lines used to be hand-written per gun (GoM's table, eleven per-gun files here and Post-93's Tooltips.lua),
    each worded like the last one: four formats for rails, nine for built-in parts, magazine lines naming a gun
    ("Compatible Magazines: AK-47"), barrel lengths and case ejection with no game effect, and lines that were wrong
    (GoM's AR-15 and Mini-14 rails, the TMP and M249 optic limits left out). Now each gun's entry in GoM's
    tooltipsPergun is rebuilt once, on the first tick of the game (Tooltips.lua, before its render wrappers), for
    every ranged gun of GoM and both our mods, always in this order, no full stops, sides as Up, Down, Left, Right,
    a line left out when it has nothing to say:

        Uses <calibre> rounds                       the gun's own "Uses" line (GoM's, or our per-gun files')
        Integrated: <parts>                         INTEGRATED below, plus a registered folding bipod (Gunworks
                                                    FoldingBipod), a launcher fitted for good (Underbarrel, in GoM's
                                                    spawn table "required") and an integrated bayonet
        Integrated Picatinny Rails: <sides>         rails in the spawn table's "required" parts
        Integrated M-LOK Slots: <sides>             those of them that stand for an M-LOK handguard (MLOK below)
        Available Picatinny Slots: <sides>          GoM's Picatinny_Rail_<side> whose MountOn lists the gun
        Compatible Optics: <...>                    only when the gun refuses some optics its rail or mount carries
        Compatible Mounting Device: <names>         other optic mounts whose MountOn lists the gun (item names)
        Compatible Muzzle Device: <names>           muzzle mount devices whose MountOn lists the gun (item names)
        Can attach a bayonet                        Gunworks' bayonet registry
        <RULES below>                               rules the game applies that nothing above says

    Each magazine in a Gunworks magazine profile gets "Fits: <guns>" (every gun registered to a profile it is in,
    short names, one line) after its own "Uses" line, in place of the old "Fits the ..." lines. The lines of the
    part states fitted on a gun (stocks, bipods, selectors) are added under the gun's when its tooltip renders
    (Tooltips.lua). Every list is read from the live registries and item scripts, so a line cannot claim what the gun
    cannot do.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local function want(name)
    local okReq, mod = pcall(require, name)
    return okReq and type(mod) == "table" and mod or nil
end
local Magazine = want("WeaponSystems/Utils/Magazine")
local RequiredAttachment = want("WeaponSystems/Utils/RequiredAttachment")
local FoldingBipod = want("WeaponSystems/Utils/FoldingBipod")
local Bayonet = want("WeaponSystems/Utils/Bayonet")
local Underbarrel = want("WeaponSystems/Utils/Underbarrel")
local Points = want("MarzWeapons/OnCreate/AttachmentPointsTable")
local Rails = want("GunsOfTien/Rails")
for _, file in ipairs({ "Magazines", "AttachmentsRequiredParts", "Bayonets", "Bipods", "Underbarrel" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local lines = tooltips.tooltipsPergun

GunsOfTien_GunLines = GunsOfTien_GunLines or {}
local GunLines = GunsOfTien_GunLines

-- built-in parts no registry tells about (sights and suppressors)
GunLines.INTEGRATED = {
    ["GunsOfTien.AUG"] = { "1.5x scope" },
    ["GunsOfTien.P90"] = { "ring sight" },
    ["GunsOfTien.SR25"] = { "3.5-10x scope" },
    ["GunsOfTienPost93.GROZA4"] = { "suppressor" },
    ["GunsOfTienPost93.SV99"] = { "suppressor" },
    ["MarzGuns.ASVAL"] = { "suppressor" },
    ["MarzGuns.MP5SD"] = { "suppressor" },
}

-- integrated rail parts that stand in for an M-LOK handguard (no rail on the model: lights, lasers and foregrips clamp
-- straight onto its slots). Picatinny rail sections bolted onto M-LOK (the MDRx's sides) are GoM's Picatinny Rail
-- upgrades and show as Available Picatinny Slots.
GunLines.MLOK = {
    ["GunsOfTienPost93.PS90_Integrated_Rail_Down"] = true,
    ["GunsOfTienPost93.PS90_Integrated_Rail_Left"] = true,
    ["GunsOfTienPost93.PS90_Integrated_Rail_Right"] = true,
    ["GunsOfTienPost93.MDR_Integrated_Rail_Down"] = true,
}

-- rules the game applies that the lines built here do not say
GunLines.RULES = {
    ["GunsOfTien.M249"] = { "Jam Chance doubled with STANAG magazines" },
    ["GunsOfTien.PPK"] = { "Fits an ankle holster" },
    ["MarzGuns.DETECTIVE_38"] = { "Compatible with 6-round speedloader" },
    ["MarzGuns.PYTHON"] = { "Compatible with 6-round speedloader" },
    ["MarzGuns.RHINO"] = { "Compatible with 6-round speedloader" },
    ["MarzGuns.MOSIN"] = { "Compatible with 5-round stripper clip" },
}

local MODULES = { MarzGuns = true, GunsOfTien = true, GunsOfTienPost93 = true }
local SIDES = { "Up", "Down", "Left", "Right" }
local RED_DOTS = Rails and Rails.RED_DOTS or {}

-------------------------------------------------
-- Item scripts and registries
-------------------------------------------------
local scriptCache = {}
local function scriptOf(fullType)
    if scriptCache[fullType] == nil then
        scriptCache[fullType] = ScriptManager.instance:getItem(fullType) or false
    end
    return scriptCache[fullType] or nil
end

local function nameOf(fullType)
    local script = scriptOf(fullType)
    return script and script:getDisplayName() or fullType
end

local function isGun(fullType)
    local script = scriptOf(fullType)
    return script ~= nil and script:isRanged()
end

local mountCache = {}
--- part -> set of the guns its MountOn lists (an instance's list: the script's, resolved to full types)
local function mountOn(part)
    if not mountCache[part] then
        local set = {}
        local item = scriptOf(part) and instanceItem(part)
        local list = item and item.getMountOn and item:getMountOn()
        if list then
            for i = 0, list:size() - 1 do set[tostring(list:get(i))] = true end
        end
        mountCache[part] = set
    end
    return mountCache[part]
end

local function required(gun)
    local tables = Points and Points.weaponAttachmentTablesAndChances
    local entry = tables and tables[gun]
    local set = {}
    for _, part in ipairs(entry and entry.required or {}) do set[part] = true end
    return set
end

local function keys(t)
    local out = {}
    for k in pairs(t or {}) do out[#out + 1] = k end
    return out
end

--- Can `part` be on `gun`: fitted for good, or in its MountOn with its required parents available in turn.
local function available(gun, part, integrated, depth)
    if integrated[part] then return true end
    if (depth or 0) > 4 or not mountOn(part)[gun] then return false end
    local all = RequiredAttachment and RequiredAttachment.Dependencies[part]
    local any = RequiredAttachment and RequiredAttachment.AnyDependencies[part]
    for parent in pairs(all or {}) do
        if not available(gun, parent, integrated, (depth or 0) + 1) then return false end
    end
    if any then
        for parent in pairs(any) do
            if available(gun, parent, integrated, (depth or 0) + 1) then return true end
        end
        return false
    end
    return true
end

local function parentsOf(part)
    local out = {}
    if not RequiredAttachment then return out end
    for parent in pairs(RequiredAttachment.Dependencies[part] or {}) do out[parent] = true end
    for parent in pairs(RequiredAttachment.AnyDependencies[part] or {}) do out[parent] = true end
    return out
end

local opticsList = nil
--- every optic that needs a rail or mount (part type Scope)
local function optics()
    if not opticsList then
        opticsList = {}
        local seen = {}
        for _, t in ipairs({ RequiredAttachment and RequiredAttachment.AnyDependencies or {},
            RequiredAttachment and RequiredAttachment.Dependencies or {} }) do
            for part in pairs(t) do
                local item = not seen[part] and scriptOf(part) and instanceItem(part)
                seen[part] = true
                if item and instanceof(item, "WeaponPart") and item:getPartType() == "Scope" then
                    opticsList[#opticsList + 1] = part
                end
            end
        end
        table.sort(opticsList)
    end
    return opticsList
end

local function sideOf(part)
    if not part:find("Rail") then return nil end
    for _, side in ipairs(SIDES) do
        if part:sub(-#side - 1) == "_" .. side then return side end
    end
    return nil
end

local function joinNames(list)
    -- each name once: two items can share one (the 9x19mm mount device, GoM's and the main mod's old one)
    local names, seen = {}, {}
    for _, part in ipairs(list) do
        local name = nameOf(part)
        if not seen[name] then
            seen[name] = true
            names[#names + 1] = name
        end
    end
    table.sort(names)
    return table.concat(names, ", ")
end

-------------------------------------------------
-- One gun
-------------------------------------------------
local function usesLine(list)
    for _, line in ipairs(list or {}) do
        if type(line) == "string" and line:find("^Uses ") then return (line:gsub("%.$", "")) end
    end
    return nil
end

local function opticsLine(gun, integrated)
    local mounts = {}
    for _, optic in ipairs(optics()) do
        for parent in pairs(parentsOf(optic)) do
            if available(gun, parent, integrated) then mounts[parent] = true end
        end
    end
    local universe, allowed = {}, {}
    for _, optic in ipairs(optics()) do
        for parent in pairs(parentsOf(optic)) do
            if mounts[parent] then
                universe[#universe + 1] = optic
                if available(gun, optic, integrated) then allowed[#allowed + 1] = optic end
                break
            end
        end
    end
    if #allowed == 0 or #allowed == #universe then return nil, mounts end
    local isDot, dots = {}, 0
    for _, optic in ipairs(RED_DOTS) do isDot[optic] = true end
    local rest = {}
    for _, optic in ipairs(allowed) do
        if isDot[optic] then dots = dots + 1 else rest[#rest + 1] = optic end
    end
    if #RED_DOTS > 0 and dots == #RED_DOTS then
        if #rest == 0 then return "Compatible Optics: Red dots only", mounts end
        return "Compatible Optics: Red dots, " .. joinNames(rest), mounts
    end
    return "Compatible Optics: " .. joinNames(allowed) .. (#allowed == 1 and " only" or ""), mounts
end

local function buildGun(gun)
    local out = {}
    local uses = usesLine(lines[gun])
    if uses then out[#out + 1] = uses end
    local integrated = required(gun)

    local builtIn = {}
    for _, text in ipairs(GunLines.INTEGRATED[gun] or {}) do builtIn[#builtIn + 1] = text end
    if FoldingBipod and FoldingBipod.WeaponsWithFoldableBipod[gun] then builtIn[#builtIn + 1] = "folding bipod" end
    for part in pairs(integrated) do
        local under = Underbarrel and Underbarrel.UnderbarrelAttachments[part]
        if under and under.type then
            builtIn[#builtIn + 1] = (nameOf(under.type):gsub(" Grenade Launcher$", " grenade launcher"))
        end
    end
    local integratedBayonet = Bayonet and Bayonet.IntegratedBayonets[gun]
    if integratedBayonet then builtIn[#builtIn + 1] = "bayonet" end
    if #builtIn > 0 then out[#out + 1] = "Integrated: " .. table.concat(builtIn, ", ") end

    local fixed, mlok, slots = {}, {}, {}
    for _, side in ipairs(SIDES) do
        local kind = nil
        for part in pairs(integrated) do
            if sideOf(part) == side then kind = GunLines.MLOK[part] and "mlok" or "rail" end
        end
        if kind == "rail" then
            fixed[#fixed + 1] = side
        elseif kind == "mlok" then
            mlok[#mlok + 1] = side
        elseif available(gun, "MarzGuns.Picatinny_Rail_" .. side, integrated) then
            slots[#slots + 1] = side
        end
    end
    if #fixed > 0 then out[#out + 1] = "Integrated Picatinny Rails: " .. table.concat(fixed, ", ") end
    if #mlok > 0 then out[#out + 1] = "Integrated M-LOK Slots: " .. table.concat(mlok, ", ") end
    if #slots > 0 then out[#out + 1] = "Available Picatinny Slots: " .. table.concat(slots, ", ") end

    local optic, mounts = opticsLine(gun, integrated)
    if optic then out[#out + 1] = optic end
    local mountDevices = {}
    for part in pairs(mounts) do
        if not part:find("Rail_") and not integrated[part] then mountDevices[#mountDevices + 1] = part end
    end
    if #mountDevices > 0 then out[#out + 1] = "Compatible Mounting Device: " .. joinNames(mountDevices) end

    local muzzle = {}
    for part, set in pairs(mountCache) do
        if part:find("Muzzle_Mount_Device") and set[gun] and not integrated[part] then muzzle[#muzzle + 1] = part end
    end
    if #muzzle > 0 then out[#out + 1] = "Compatible Muzzle Device: " .. joinNames(muzzle) end

    local bayonets = Bayonet and Bayonet.BayonetMountableWeapons[gun]
    if bayonets and #keys(bayonets) > 0 and not integratedBayonet then out[#out + 1] = "Can attach a bayonet" end

    for _, text in ipairs(GunLines.RULES[gun] or {}) do out[#out + 1] = text end
    return out
end

-------------------------------------------------
-- Magazines
-------------------------------------------------
local SUFFIXES = { " Automatic Shotgun", " Assault Rifle", " Civilian Rifle", " Battle Rifle", " Marksman Rifle",
    " Semi%-Automatic Rifle", " Sniper Rifle", " Light Machine Gun", " Submachine Gun", " Machine Pistol",
    " Machine Gun" }

--- a gun's name without its kind ("RPK Light Machine Gun" -> "RPK"), its variant ("... with M203") or stance
local function shortName(gun)
    local name = nameOf(gun):gsub("%s*%b()$", ""):gsub(" with .+$", "")
    for _, suffix in ipairs(SUFFIXES) do
        local cut = name:gsub(suffix .. "$", "")
        if cut ~= name then return cut end
    end
    return name
end

local function buildMagazines()
    if not Magazine then return end
    local gunsOf = {}             -- profile -> guns
    for gun, profile in pairs(Magazine.WeaponMagazineProfile) do
        if isGun(gun) then
            gunsOf[profile] = gunsOf[profile] or {}
            table.insert(gunsOf[profile], gun)
        end
    end
    local fits = {}               -- magazine -> set of short names
    -- a gun with no profile takes its one MagazineType (vanilla's rule; GoM's SVD, FAL, M14...). The item script has
    -- no getter for it, so it is read from an instance, once per such gun.
    for _, gun in ipairs(GunLines.guns or {}) do
        if not Magazine.WeaponMagazineProfile[gun] then
            local item = instanceItem(gun)
            local mag = item and instanceof(item, "HandWeapon") and item:getMagazineType()
            if mag and mag ~= "" and scriptOf(mag) then
                fits[mag] = fits[mag] or {}
                fits[mag][shortName(gun)] = true
            end
        end
    end
    for profile, mags in pairs(Magazine.MagazineProfiles) do
        for _, gun in ipairs(gunsOf[profile] or {}) do
            for _, mag in ipairs(mags) do
                if scriptOf(mag) then
                    fits[mag] = fits[mag] or {}
                    fits[mag][shortName(gun)] = true
                end
            end
        end
    end
    for mag, set in pairs(fits) do
        local list = {}
        for _, line in ipairs(lines[mag] or {}) do
            if type(line) == "string" and not line:find("^Fits") then
                list[#list + 1] = line:find("^Uses ") and (line:gsub("%.$", "")) or line
            end
        end
        local names = keys(set)
        table.sort(names)
        list[#list + 1] = "Fits: " .. table.concat(names, ", ")
        lines[mag] = list
    end
end

-------------------------------------------------
-- Every gun of the three modules
-------------------------------------------------
function GunLines.Build()
    scriptCache, mountCache, opticsList = {}, {}, nil
    -- every part's MountOn, read once (the muzzle device search walks this cache)
    local all = getScriptManager():getAllItems()
    local guns = {}
    for i = 0, all:size() - 1 do
        local script = all:get(i)
        local fullType = script:getFullName()
        if MODULES[fullType:match("^([^%.]+)%.") or ""] then
            if script:isRanged() then
                guns[#guns + 1] = fullType
            elseif fullType:find("Muzzle_Mount_Device") then
                mountOn(fullType)
            end
        end
    end
    GunLines.guns = guns
    for _, gun in ipairs(guns) do
        local built = buildGun(gun)
        if #built > 0 then lines[gun] = built end
    end
    buildMagazines()
end

return GunLines
