--[[
    Guns of Tien -- "Information" lines in Guns of Marz's item tooltips for the new rounds and the sawn-off stocks

    GoM draws `tooltipsPergun[fullType]` under an item's tooltip (MarzWeapons/CustomItemTooltips.lua, looked up at
    render time), hard-coded English like its own entries. The round lines match the profiles in
    shared/GunsOfTien/Ammunition.lua, the stock line shared/GunsOfTien/SawnStock.lua (one line per gun type: the gun's
    "Stock (Integrated)" row shows whether this one is sawn off).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun

lines["GunsOfTien.762x39_Bullet_US"] = {
    "Damage to targets decreased by 50%",
    "Sound radius and volume reduced by 50%",
    "Chance to degrade weapon condition halved",
    "Too weak to cycle an AK: rack after every shot",
    "Cycles normally with a PBS-1 suppressor fitted",
    "Stacks with suppressors for maximum effect",
}
lines["GunsOfTien.762x39_Bullet_SP"] = {
    "Damage to targets increased by 20%",
    "Critical damage increased by 15%",
    "Expands: never pierces",
}
lines["GunsOfTien.762x39_Bullet_SteelCore"] = {
    "Damage to targets decreased by 10%",
    "Piercing targets",
    "Able to hit up to 3 targets",
    "Chance to degrade weapon condition increased by 15%",
}
lines["GunsOfTien.9x19_Bullet_Subsonic"] = {
    "Damage to targets decreased by 15%",
    "Sound radius and volume reduced by 30% (no supersonic crack)",
    "Stacks with suppressors for maximum effect",
}
lines["GunsOfTien.9x19_Bullet_HollowPoint"] = {
    "Damage to targets increased by 20%",
    "Critical damage increased by 15%",
}
lines["GunsOfTien.9x19_Bullet_PPP"] = {
    "Damage to targets increased by 20%",
    "Critical damage increased by 10%",
    "Sound radius and volume increased by 10%",
    "Chance to degrade weapon condition increased by 40%",
}
lines["GunsOfTien.45_Bullet_HollowPoint"] = {
    "Damage to targets increased by 20%",
    "Critical damage increased by 15%",
}
lines["GunsOfTien.45_Bullet_P"] = {
    "Damage to targets increased by 15%",
    "Critical damage increased by 10%",
    "Sound radius and volume increased by 10%",
    "Chance to degrade weapon condition increased by 30%",
}
lines["GunsOfTien.9x39_Bullet_SP6"] = {
    "Damage to targets decreased by 10%",
    "Piercing targets",
    "Able to hit up to 3 targets",
}
for _, fullType in ipairs({ "GunsOfTien.3006_Bullet_SP", "GunsOfTien.308_Bullet_SP" }) do
    lines[fullType] = {
        "Damage to targets increased by 20%",
        "Critical damage increased by 15%",
        "Expands: never pierces, hits one target",
    }
end
lines["GunsOfTien.12Gauge_Shell_Birdshot"] = {
    "Many small pellets: weak beyond a few tiles",
    "Wider spread, about half the range of buckshot",
}
lines["SWMG.3030_Bullet"] = {
    "Flat-nosed soft point, safe in tube magazines",
    "Expands: never pierces, hits one target",
}
for _, gun in ipairs({ "MarzGuns.DOUBLEBARREL", "MarzGuns.STEVENS_555", "MarzGuns.TOZ34" }) do
    local list = lines[gun] or {}
    lines[gun] = list
    local line = "Stock can be sawn off (Saw Off Shotgun Stock): Aiming Time reduced by 25%, Hit Chance reduced by 13%, "
        .. "Recoil Delay increased by 30%; with sawn-off barrels too it fits a holster."
    local present = false
    for _, l in ipairs(list) do
        if l == line then present = true end
    end
    if not present then list[#list + 1] = line end
end
lines["SWMG.545x39_Bullet"] = {
    "7N6: steel core",
    "Piercing targets",
    "Able to hit up to 3 targets",
    "Tumbles: critical chance increased by 10%",
}
