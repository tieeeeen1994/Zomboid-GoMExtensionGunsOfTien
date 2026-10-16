--[[
    Guns of Tien - Post-93 -- "Information" lines in Guns of Marz's item tooltips for the MP7A1, the P90 TR, the
    Five-seveN, their magazines, suppressors and rounds (GoM's tooltipsPergun table, read at render time; hard-coded English like
    GoM's own entries).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTienPost93."

lines[M .. "MP7A1"] = {
    "Uses 4.6x30mm rounds.",
    "Integrated Picatinny rails: Up, Left, Right.",
    "Collapsible stock.",
    "Standard rounds pierce: able to hit up to 2 targets.",
}
lines[M .. "P90TR"] = {
    "Uses 5.7x28mm rounds.",
    "Integrated Picatinny rails: Up, Left, Right.",
    "50-round magazine on top; ejects spent cases downward.",
    "Standard rounds pierce: able to hit up to 2 targets.",
}
lines["MarzGuns.FIVESEVEN"] = {
    "Uses 5.7x28mm rounds.",
    "Compatible Mounting Device: Beretta Mount.",
    "Compatible Muzzle Device: 5.7x28mm Muzzle Mount.",
    "Standard rounds pierce: able to hit up to 2 targets.",
}
lines[M .. "57x28Magazine20_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "57x28Magazine30_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "UCP"] = {
    "Uses 4.6x30mm rounds.",
    "H&K prototype, never sold (cancelled 2009).",
    "Compatible Mounting Device: Beretta Mount.",
    "Compatible Muzzle Device: 4.6x30mm Muzzle Mount.",
    "Standard rounds pierce: able to hit up to 2 targets.",
}
lines[M .. "46x30Magazine20_UCP"] = { "Uses 4.6x30mm rounds." }
lines[M .. "46x30Magazine40_UCP"] = { "Uses 4.6x30mm rounds." }
for _, mag in ipairs({ "46x30Magazine20_MP7", "46x30Magazine30_MP7", "46x30Magazine40_MP7", "46x30Magazine60_MP7" }) do
    lines[M .. mag] = { "Uses 4.6x30mm rounds." }
end
lines[M .. "57x28Magazine50_P90"] = { "Uses 5.7x28mm rounds." }

for _, part in ipairs({ "MP7_Suppressor", "P90_Suppressor", "FIVESEVEN_Suppressor" }) do
    lines[M .. part] = {
        "Sound Radius and Volume reduced by 70%",
        "Damage to targets decreased by 10%",
        "Removes Muzzle Flash",
        "Needs its Muzzle Mount Device",
    }
end
for _, part in ipairs({ "MP7_Muzzle_Mount_Device", "P90_Muzzle_Mount_Device" }) do
    lines[M .. part] = {
        "No Direct Stat Changes",
        "Enables its Suppressor",
        "Needs Wrench to install or remove.",
    }
end

lines[M .. "46x30_Bullet"] = { "DM11: solid copper-plated steel bullet", "Piercing targets", "Able to hit up to 2 targets" }
lines[M .. "57x28_Bullet"] = { "SS190: steel and aluminium penetrator", "Piercing targets", "Able to hit up to 2 targets" }
for _, round in ipairs({ "46x30_Bullet_Subsonic", "57x28_Bullet_SB193" }) do
    lines[M .. round] = {
        "Damage to targets decreased by 40%",
        "Sound radius and volume reduced by 50%",
        "Does not pierce",
        "Stacks with suppressors for maximum effect",
    }
end
lines[M .. "57x28_Bullet_SS197SR"] = {
    "Polymer tip, expands",
    "Damage to targets increased by 15%",
    "Critical damage increased by 10%",
    "Does not pierce",
}
