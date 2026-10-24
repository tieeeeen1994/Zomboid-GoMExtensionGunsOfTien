--[[
    Guns of Tien -- Ammo Maker (mod id ammomaker, optional, as it is for Guns of Marz): with it the new rounds can be
    assembled from gunpowder, a casing and a bullet like every other round. Without it they are not made at all
    (none of them is found as loot either, like Guns of Marz's own special loads).

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

    Without Ammo Maker the scripts still load: the placeholders use our copies of its timed actions
    (scripts/GunsOfTien/timedactions_ammomaker.txt; a recipe whose timedAction is missing throws in
    CraftRecipe.OnScriptsLoaded, which stops that pass for every recipe after it), and the soft point recipe gets its
    inputs here, only with Ammo Maker (an itemMapper naming a missing item throws in OutputMapper.OnPostWorldDictionaryInit
    the same way). At OnInitGlobalModData (before PostWorldDictionaryInit resolves inputs) this file hides every recipe
    of ours that needs Ammo Maker the way Ammo Maker hides its unused ones (ammomaker_recipeManager.lua
    updateRecipesInactive: OnAddToMenu = False, which the crafting lists call through callLuaBool and so skip, plus
    NeedToBeLearn), and moves the belt link recipes out of its AmmoMakerParts category into vanilla's Welding.
--]]

local AMMO_MAKER = type(ammoMakerAmmoData) == "table" and type(ammoMakerAmmoParts) == "table"

-- Powder follows Ammo Maker's own 5.56 variants: subsonic x0.7 (556x45SS 35 / 50), overpressured x1.4 (556x45OP
-- 70 / 50) for +P+, and +P a milder x1.2; hollow / soft points, steel core and birdshot keep the standard charge.
-- New type -> { copied from, changes }
local NEW_TYPES = {
    ["762x39SS"] = { "762x39", { grainsAmount = 35 } },
    ["762x39SP"] = { "762x39", { bulletType = "GunsOfTien.BulletRifleSSP" } },
    ["9x19ParaSS"] = { "9x19Para", { grainsAmount = 7 } },
    ["9x19ParaHP"] = { "9x19Para", { bulletType = "ammomaker.ammomaker_BulletHandgunSHP" } },
    ["9x19ParaPPP"] = { "9x19Para", { grainsAmount = 14, bulletType = "ammomaker.ammomaker_BulletHandgunSHP" } },
    ["45ACPHP"] = { "45ACP", { bulletType = "ammomaker.ammomaker_BulletHandgunMHP" } },
    ["45ACPP"] = { "45ACP", { grainsAmount = 19, bulletType = "ammomaker.ammomaker_BulletHandgunMHP" } },
    ["3006SpringSP"] = { "3006Spring", { bulletType = "GunsOfTien.BulletRifleMSP" } },
    ["308WinSP"] = { "308Win", { bulletType = "GunsOfTien.BulletRifleMSP" } },
    ["12Bird"] = { "12Buck00", { bulletType = "GunsOfTien.Birdshot" } },
}

local SOFT_POINT_RECIPE = "GunsOfTien_MakeSoftPointBullet"
local SOFT_POINT = [[
{
    inputs
    {
        item 1 [ammomaker.ammomaker_BulletRifleS;ammomaker.ammomaker_BulletRifleM] mappers[bulletType] mode:destroy,
        item 1 [Base.SmallFileSet] mode:keep,
    }
    outputs
    {
        item 1 mapper:bulletType,
    }
    itemMapper bulletType
    {
        GunsOfTien.BulletRifleSSP = ammomaker.ammomaker_BulletRifleS,
        GunsOfTien.BulletRifleMSP = ammomaker.ammomaker_BulletRifleM,
    }
}
]]

local HIDDEN = "{ OnAddToMenu = False, NeedToBeLearn = True, }"
local LINK_RECIPES = { "GunsOfTien_MakeM27_Links", "GunsOfTien_MakeM13_Links" }

local function hiddenRecipes()
    local names = { SOFT_POINT_RECIPE, "GunsOfTien_MakeBirdshot", "GunsOfTien_ProduceBirdshot" }
    for newType in pairs(NEW_TYPES) do
        names[#names + 1] = "Make" .. newType
        names[#names + 1] = "Produce" .. newType
    end
    return names
end

local function onInitGlobalModData()
    local scripts = ScriptManager.instance
    if AMMO_MAKER then
        -- Ammo Maker's own handler (registered first) hides a part recipe no active round uses; leave it so. The
        -- empty check keeps a second world load in one session from adding the inputs twice.
        local recipe = scripts:getCraftRecipe(SOFT_POINT_RECIPE)
        if recipe and recipe:getInputs():size() == 0 and recipe:getOnAddToMenu() ~= "False" then
            recipe:Load(SOFT_POINT_RECIPE, SOFT_POINT)
        end
        return
    end
    for _, name in ipairs(hiddenRecipes()) do
        local recipe = scripts:getCraftRecipe(name)
        if recipe then
            recipe:getInputs():clear()
            recipe:getOutputs():clear()
            recipe:Load(name, HIDDEN)
        end
    end
    for _, name in ipairs(LINK_RECIPES) do
        local recipe = scripts:getCraftRecipe(name)
        if recipe then recipe:Load(name, "{ category = Welding, }") end
    end
end

Events.OnInitGlobalModData.Add(onInitGlobalModData)

if not AMMO_MAKER then return end

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
