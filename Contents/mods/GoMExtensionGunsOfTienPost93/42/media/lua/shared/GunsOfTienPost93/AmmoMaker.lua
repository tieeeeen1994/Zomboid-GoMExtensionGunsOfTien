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
    -- the main mod's Tokarev (Ammo Maker's 762x25Tok) on Ammo Maker's small handgun hollow point, as its 9x19 HP
    ["762x25TokHP"] = { "762x25Tok", { bulletType = "ammomaker.ammomaker_BulletHandgunSHP" } },
    -- Special rounds audit (2026-11-25): AP rounds copy Ammo Maker's AP types (its own may carry another mod's
    -- round), the soft point is the main mod's filed bullet, PMM x1.3 powder
    ["46x30DM21"] = { "46x30", {} },
    ["9x18MakPMM"] = { "9x18Mak", { grainsAmount = 8 } },
    ["9x18MakRG028"] = { "9x18Mak", { bulletType = "ammomaker.ammomaker_BulletHandgunSAP" } },
    ["762x54RSP"] = { "762x54R", { bulletType = "GunsOfTien.BulletRifleMSP" } },
    ["762x54R7N13"] = { "762x54RAP", {} },
    ["545x39_7N22"] = { "545x39AP", {} },
    ["9x19Para7N21"] = { "9x19ParaAP", { grainsAmount = 12 } },
    ["762x39HP"] = { "762x39", { bulletType = "ammomaker.ammomaker_BulletRifleSHP" } },
    ["3030WinFTX"] = { "3030Win", { bulletType = "ammomaker.ammomaker_BulletRifleMHP" } },
    ["50AEHP"] = { "50AE", { bulletType = "ammomaker.ammomaker_BulletHandgunLHP" } },
    ["12DragonsBreath"] = { "12Dragon", {} },
}

if type(ammoMakerAmmoData) ~= "table" then
    Events.OnInitGlobalModData.Add(function()
        for newType in pairs(NEW_TYPES) do
            for _, name in ipairs({ "Make" .. newType, "Produce" .. newType }) do
                -- the main mod's helper also moves it out of Ammo Maker's category (an empty one showed otherwise)
                GunsOfTien_HideAmmoMakerRecipe(name)
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
    { modId = MOD, itemType = "GunsOfTienPost93.57x28_Bullet_SB193", ammoType = "57x28SS" },
    { modId = MOD, itemType = "GunsOfTienPost93.57x28_Bullet_SS197SR", ammoType = "57x28SR" },
    { modId = MOD, itemType = "GunsOfTienPost93.762x25_Bullet_HollowPoint", ammoType = "762x25TokHP" },
    { modId = MOD, itemType = "GunsOfTienPost93.46x30_Bullet_DM21", ammoType = "46x30DM21" },
    { modId = MOD, itemType = "GunsOfTienPost93.9x18_Bullet_PMM", ammoType = "9x18MakPMM" },
    { modId = MOD, itemType = "GunsOfTienPost93.9x18_Bullet_RG028", ammoType = "9x18MakRG028" },
    { modId = MOD, itemType = "GunsOfTienPost93.762x54_Bullet_SP", ammoType = "762x54RSP" },
    { modId = MOD, itemType = "GunsOfTienPost93.762x54_Bullet_7N13", ammoType = "762x54R7N13" },
    { modId = MOD, itemType = "GunsOfTienPost93.545x39_Bullet_7N22", ammoType = "545x39_7N22" },
    { modId = MOD, itemType = "GunsOfTienPost93.9x19_Bullet_7N21", ammoType = "9x19Para7N21" },
    { modId = MOD, itemType = "GunsOfTienPost93.762x39_Bullet_HollowPoint", ammoType = "762x39HP" },
    { modId = MOD, itemType = "GunsOfTienPost93.3030_Bullet_FTX", ammoType = "3030WinFTX" },
    { modId = MOD, itemType = "GunsOfTienPost93.50_Bullet_HollowPoint", ammoType = "50AEHP" },
    { modId = MOD, itemType = "GunsOfTienPost93.12Gauge_Shell_DragonsBreath", ammoType = "12DragonsBreath" },
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
