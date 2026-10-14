--[[
    Guns of Tien -- Ammo Maker (mod id ammomaker, required): the new rounds can be assembled from gunpowder, a
    casing and a bullet like every other round.

    Ammo Maker's API (its server/ammomaker_apiFunctions.lua, OnPreDistributionMerge) reads the global tables
    ammoMakerAddAmmoTypesMap0..9: { modId, itemType (our round), ammoType (an Ammo Maker type) }. At
    OnInitGlobalModData (shared/ammomaker_recipeManager.lua) it fills the craftRecipes "Make<ammoType>" and
    "Produce<ammoType>" from ammoMakerAmmoData[ammoType] (grains of powder, bullet part and count, casing part) with
    `recipe:Load`, so every type needs those two recipes as placeholders in a script
    (scripts/GunsOfTien/recipes_ammomaker.txt). One recipe per type: two rounds on the same type would fight over it.

    Steel Core and SP-6 use Ammo Maker's own armour-piercing types (762x39AP, 9x39AP). The others get new types,
    each a copy of its calibre's base type with its own bullet part and powder: Ammo Maker's hollow-point bullets
    for hollow points, and this mod's parts (scripts/GunsOfTien/items_ammomaker_parts.txt) for soft points (filed
    from Ammo Maker's standard bullets) and birdshot (poured through a strainer into water).

    Parts go in ammoMakerAmmoParts like Ammo Maker's own (its recipe manager reads partClass, makeRecipe,
    recycleRecipe / recycleMaterial / bulkSize for recycling, boxType for its pack / unpack recipes, and its loot code
    partCat; "Shotgun" parts must have a boxType). No moldType: they are not cast in Ammo Maker's molds.
--]]

if type(ammoMakerAmmoData) ~= "table" or type(ammoMakerAmmoParts) ~= "table" then return end

ammoMakerAmmoParts["GunsOfTien.BulletRifleSSP"] = {
    partClass = "Projectile",
    partExtraClass = "SoftPoint",
    makeRecipe = "GunsOfTien_MakeSoftPointBullet",
    recycleRecipe = "RecycleBulletsShots",
    recycleMaterial = "Base.IronScrap",
    bulkSize = 100,
    partCat = "Rifle",
    partSize = "S",
    baseType = "ammomaker.ammomaker_BulletRifleS",
    boxType = "GunsOfTien.BoxBulletsRifleSSP",
}
ammoMakerAmmoParts["GunsOfTien.BulletRifleMSP"] = {
    partClass = "Projectile",
    partExtraClass = "SoftPoint",
    makeRecipe = "GunsOfTien_MakeSoftPointBullet",
    recycleRecipe = "RecycleBulletsShots",
    recycleMaterial = "Base.IronScrap",
    bulkSize = 100,
    partCat = "Rifle",
    partSize = "M",
    baseType = "ammomaker.ammomaker_BulletRifleM",
    boxType = "GunsOfTien.BoxBulletsRifleMSP",
}
ammoMakerAmmoParts["GunsOfTien.Birdshot"] = {
    partClass = "Projectile",
    partExtraClass = "Standard",
    makeRecipe = "GunsOfTien_MakeBirdshot",
    produceRecipe = "GunsOfTien_ProduceBirdshot",
    recycleRecipe = "RecycleBulletsShots",
    recycleMaterial = "Base.IronScrap",
    bulkSize = 300,
    partCat = "Shotgun",
    boxType = "GunsOfTien.BoxBirdshot",
}

-- New type -> { copied from, changes }
local NEW_TYPES = {
    ["762x39SS"] = { "762x39", { grainsAmount = 35 } },
    ["762x39SP"] = { "762x39", { bulletType = "GunsOfTien.BulletRifleSSP" } },
    ["9x19ParaSS"] = { "9x19Para", { grainsAmount = 8 } },
    ["9x19ParaHP"] = { "9x19Para", { bulletType = "ammomaker.ammomaker_BulletHandgunSHP" } },
    ["9x19ParaPPP"] = { "9x19Para", { grainsAmount = 13, bulletType = "ammomaker.ammomaker_BulletHandgunSHP" } },
    ["45ACPHP"] = { "45ACP", { bulletType = "ammomaker.ammomaker_BulletHandgunMHP" } },
    ["45ACPP"] = { "45ACP", { grainsAmount = 19, bulletType = "ammomaker.ammomaker_BulletHandgunMHP" } },
    ["3006SpringSP"] = { "3006Spring", { bulletType = "GunsOfTien.BulletRifleMSP" } },
    ["308WinSP"] = { "308Win", { bulletType = "GunsOfTien.BulletRifleMSP" } },
    ["12Bird"] = { "12Buck00", { bulletType = "GunsOfTien.Birdshot" } },
}

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

local MAP = {
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.762x39_Bullet_US", ammoType = "762x39SS" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.762x39_Bullet_SP", ammoType = "762x39SP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.762x39_Bullet_SteelCore", ammoType = "762x39AP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.9x19_Bullet_Subsonic", ammoType = "9x19ParaSS" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.9x19_Bullet_HollowPoint", ammoType = "9x19ParaHP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.9x19_Bullet_PPP", ammoType = "9x19ParaPPP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.45_Bullet_HollowPoint", ammoType = "45ACPHP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.45_Bullet_P", ammoType = "45ACPP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.9x39_Bullet_SP6", ammoType = "9x39AP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.3006_Bullet_SP", ammoType = "3006SpringSP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.308_Bullet_SP", ammoType = "308WinSP" },
    { modId = "GoMExtensionGunsOfTien", itemType = "GunsOfTien.12Gauge_Shell_Birdshot", ammoType = "12Bird" },
}

MAP.gunsOfTien = true

-- The first free slot from the top (Guns of Marz and Vanilla Weapons Plus both take Map0), or ours again when Lua
-- runs this file a second time.
local slot
for i = 9, 0, -1 do
    local current = _G["ammoMakerAddAmmoTypesMap" .. i]
    if type(current) == "table" and current.gunsOfTien then
        slot = i
        break
    end
    if current == nil and not slot then slot = i end
end
if slot then
    _G["ammoMakerAddAmmoTypesMap" .. slot] = MAP
else
    print("[GunsOfTien] every Ammo Maker API slot is taken, the new rounds cannot be crafted with Ammo Maker")
end
