--[[
    Guns of Tien - Post-93 -- Ammo Maker: the 4.6x30mm and 5.7x28mm rounds can be assembled like any other.

    Ammo Maker already has the types 46x30 and 57x28 (rifle S bullet, small bottleneck casing). The subsonic loads
    and the SS197SR get types of their own, copied from those (one recipe per type: two rounds on one type overwrite
    each other's recipe); their Make / Produce placeholders are in scripts/GunsOfTienPost93/recipes_ammomaker.txt.
    How Ammo Maker's API works: the main mod's shared/GunsOfTien/AmmoMaker.lua and CLAUDE.md.

    Ammo Maker is optional, as in the main mod: without it these rounds are not made at all, and the placeholders
    (which use the main mod's copies of its timed actions) are hidden here the way Ammo Maker hides unused recipes.
--]]

-- Subsonic powder x0.7 of the standard charge, as Ammo Maker's own 556x45SS (35 / 50).
local NEW_TYPES = {
    ["46x30SS"] = { "46x30", { grainsAmount = 10 } },
    ["57x28SS"] = { "57x28", { grainsAmount = 8 } },
    ["57x28SR"] = { "57x28", { bulletType = "ammomaker.ammomaker_BulletRifleSHP" } },
}

if type(ammoMakerAmmoData) ~= "table" then
    Events.OnInitGlobalModData.Add(function()
        for newType in pairs(NEW_TYPES) do
            for _, name in ipairs({ "Make" .. newType, "Produce" .. newType }) do
                local recipe = ScriptManager.instance:getCraftRecipe(name)
                if recipe then
                    recipe:getInputs():clear()
                    recipe:getOutputs():clear()
                    recipe:Load(name, "{ OnAddToMenu = False, NeedToBeLearn = True, }")
                end
            end
        end
    end)
    return
end

for newType, def in pairs(NEW_TYPES) do
    local base = ammoMakerAmmoData[def[1]]
    if base and not ammoMakerAmmoData[newType] then
        local copy = {}
        for key, value in pairs(base) do copy[key] = value end
        copy.dropExtraData = {}
        for key, value in pairs(def[2]) do copy[key] = value end
        ammoMakerAmmoData[newType] = copy
    end
end

local MOD = "GoMExtensionGunsOfTienPost93"
local MAP = {
    { modId = MOD, itemType = "GunsOfTienPost93.46x30_Bullet", ammoType = "46x30" },
    { modId = MOD, itemType = "GunsOfTienPost93.46x30_Bullet_Subsonic", ammoType = "46x30SS" },
    { modId = MOD, itemType = "GunsOfTienPost93.57x28_Bullet", ammoType = "57x28" },
    { modId = MOD, itemType = "GunsOfTienPost93.57x28_Bullet_SB193", ammoType = "57x28SS" },
    { modId = MOD, itemType = "GunsOfTienPost93.57x28_Bullet_SS197SR", ammoType = "57x28SR" },
}
MAP.gunsOfTienPost93 = true

-- The first free API slot from the top, or ours again when Lua runs this file a second time.
local slot
for i = 9, 0, -1 do
    local current = _G["ammoMakerAddAmmoTypesMap" .. i]
    if type(current) == "table" and current.gunsOfTienPost93 then
        slot = i
        break
    end
    if current == nil and not slot then slot = i end
end
if slot then
    _G["ammoMakerAddAmmoTypesMap" .. slot] = MAP
else
    print("[GunsOfTienPost93] every Ammo Maker API slot is taken, 4.6x30 and 5.7x28 cannot be crafted with Ammo Maker")
end
