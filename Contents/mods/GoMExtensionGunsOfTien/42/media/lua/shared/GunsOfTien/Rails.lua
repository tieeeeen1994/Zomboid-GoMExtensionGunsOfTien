--[[
    Guns of Tien -- Guns of Marz's optional Picatinny rails on the main mod's guns (user, 2026-10-30): the AUG A1's
    left and right, the M249's four, the Uzi's and Mini Uzi's top, bottom and left (none on the Micro Uzi, as on GoM's
    MAC-10).

    GoM sells its rails as removable parts, MarzGuns.Picatinny_Rail_Up / _Down / _Left / _Right (a gun takes one when
    it is in that item's MountOn), and makes each kind of accessory need its side (AttachmentsRequiredParts.lua): optics
    the top, foregrips and bipods the bottom, lights the left, lasers the right. Its universal Picatinny_Rail turns into
    whichever side a gun lists for it (Gunworks' UniversalAttachment). Rails.Register does both for one gun and appends
    the gun to the accessories it allows. The rails and the parts on them are drawn by the gun's ModelWeaponPart lines
    (gen_scripts.py rail_parts: our short models on the AUG and the Uzis, GoM's own on the M249), and a found gun's
    accessories come with their rail by GoM's ":PR*" suffixes in its spawn table (each gun's file).
--]]

local UniversalAttachment = require("WeaponSystems/Utils/UniversalAttachment")

for _, file in ipairs({ "AttachmentsRequiredParts", "UniversalAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local Rails = {}

-- GoM's parts by the side they need (gen_scripts.py lists the same). The Uzi takes only the red dots, the seven GoM's
-- MP5 and MP5K spawn with: its magnified scopes (150 mm and longer at our scale) overhang the short top rail. The Mini
-- Uzi only the Reflex S2: every other red dot reaches its cocking knob or front sight from its 45 mm rail. The M249
-- takes three magnified ones too; the four longest reach its carrying handle.
Rails.RED_DOTS = { "MarzGuns.ReflexS2_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.OKP3_Sight", "MarzGuns.JS14_Sight",
    "MarzGuns.EXPS3_Sight", "MarzGuns.EXPS1_Sight", "MarzGuns.Aimpoint_Sight" }
Rails.MINIUZI_OPTICS = { "MarzGuns.ReflexS2_Sight" }
Rails.M249_OPTICS = { "MarzGuns.LR4X_Scope", "MarzGuns.TA28_Scope", "MarzGuns.ElcanX2_Scope" }
for i, optic in ipairs(Rails.RED_DOTS) do table.insert(Rails.M249_OPTICS, i, optic) end
Rails.FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
Rails.LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
Rails.LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }

local registered = {}          -- gun -> every part whose MountOn it joins

--- GoM's rails on one of our guns: `sides` of "Up" / "Down" / "Left" / "Right", and the parts allowed on them
--- (GoM's own rule already ties each part to its side; bipods are never added: none of these guns needs one).
---@param gun string
---@param def table { sides = { string }, optics = { string }?, foregrips = boolean?, lights = boolean?, lasers = boolean? }
function Rails.Register(gun, def)
    local parts, generic = {}, {}
    for _, side in ipairs(def.sides) do
        parts[#parts + 1] = "MarzGuns.Picatinny_Rail_" .. side
        generic[#generic + 1] = "MarzGuns.Picatinny_Rail_" .. side
    end
    local lists = { def.optics or {}, def.foregrips and Rails.FOREGRIPS or {}, def.lights and Rails.LIGHTS or {},
        def.lasers and Rails.LASERS or {} }
    for _, list in ipairs(lists) do
        for _, part in ipairs(list) do parts[#parts + 1] = part end
    end
    registered[gun] = parts
    UniversalAttachment.RegisterWeapon(gun, { ["MarzGuns.Picatinny_Rail"] = generic })
end

-------------------------------------------------
-- MountOn: appended (DoParam replaces the list, so it is read and written back whole; Post-93's Guns.lua and AUG.lua
-- do the same for their guns)
-------------------------------------------------
local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local entry = tostring(current:get(i))
            if not seen[entry] then
                seen[entry] = true
                list[#list + 1] = entry
            end
        end
    end
    local changed = false
    for _, gun in ipairs(guns) do
        if not seen[gun] then
            seen[gun] = true
            list[#list + 1] = gun
            changed = true
        end
    end
    if changed then script:DoParam("MountOn = " .. table.concat(list, ";")) end
end

local function appendAll()
    local byPart, order = {}, {}
    for gun, parts in pairs(registered) do
        for _, part in ipairs(parts) do
            if not byPart[part] then
                byPart[part] = {}
                order[#order + 1] = part
            end
            table.insert(byPart[part], gun)
        end
    end
    table.sort(order)
    for _, part in ipairs(order) do
        table.sort(byPart[part])
        appendMountOn(part, byPart[part])
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

return Rails
