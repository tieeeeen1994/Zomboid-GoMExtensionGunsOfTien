--[[
    Guns of Tien - Post-93 -- "Information" lines in Guns of Marz's item tooltips for the MP7A1, the P90 TR, the
    Five-seveN, the UCP, the SCAR-L and SCAR-H, the UMP45 and UMP9, the Steyr AUG A3, Para and HBAR, their magazines, suppressors and rounds (GoM's tooltipsPergun table, read at render time, hard-coded English like
    GoM's own entries).
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end

local lines = tooltips.tooltipsPergun
local M = "GunsOfTienPost93."

-- The stock's and front grip's lines, shown under an MP7 while that state is fitted (the main mod's
-- client/GunsOfTien/Tooltips.lua; stats in shared/GunsOfTienPost93/Guns.lua). The A2 has the A1's stock.
GunsOfTien_TooltipStates = GunsOfTien_TooltipStates or {}
GunsOfTien_TooltipStates[M .. "MP7A1_Integrated_Stock_Deployed"] = {
    "Collapsible stock deployed:",
    "Aiming Time reduced by 25%",
    "Hit Chance increased by 15%",
}
GunsOfTien_TooltipStates[M .. "MP7A1_Integrated_Foregrip_Deployed"] = {
    "Folding front grip unfolded:",
    "Aiming Time reduced by 20%",
    "Critical and Hit Chance increased by 15%",
    "Automatic fire spread reduced by 15%",
}

-- The SCARs' side-folding stock (GoM's G36 stats, shared/GunsOfTienPost93/Guns.lua)
GunsOfTien_TooltipStates[M .. "SCAR_Integrated_Stock_Deployed"] = {
    "Folding stock deployed:",
    "Aiming Time reduced by 15%",
    "Hit Chance increased by 15%",
}

-- The UMPs' side-folding stock (GoM's G36C stats and spread, shared/GunsOfTienPost93/Guns.lua), worded as the main
-- mod words the G36C's
GunsOfTien_TooltipStates[M .. "UMP_Integrated_Stock_Deployed"] = {
    "Folding stock deployed:",
    "Aiming Time reduced by 25%",
    "Hit Chance increased by 15%",
    "Automatic fire spread reduced by 25%",
}

lines[M .. "UMP45"] = {
    "Uses .45 rounds.",
    "Integrated Picatinny rails: Up, Down, Left, Right",
    "Compatible Muzzle Device: .45 Muzzle Mount",
}
lines[M .. "UMP9"] = {
    "Uses 9x19mm rounds.",
    "Integrated Picatinny rails: Up, Down, Left, Right",
    "Compatible Muzzle Device: 9x19mm SMG Muzzle Mount",
}
for _, mag in ipairs({ "45Magazine25_UMP", "45Magazine20_UMP", "45Magazine10_UMP" }) do
    lines[M .. mag] = { "Uses .45 rounds." }
end
lines[M .. "9x19Magazine30_UMP"] = { "Uses 9x19mm rounds." }

-- The Steyr AUGs (shared/GunsOfTienPost93/AUG.lua): integral top and right rails, GoM's Picatinny Rail upgrade on the
-- left ("Available Picatinny Slots", GoM's wording for its rail upgrades); the folding grip's state lines are the main
-- mod's (the same parts as its A1); the HBAR's bipod states as the main mod words GoM's bipods'.
for gun, first in pairs({ AUGA3 = "Uses .223/5.56x45mm NATO rounds.", AUGPARA = "Uses 9x19mm rounds.",
    AUGHBAR = "Uses 7.62x39mm rounds." }) do
    lines[M .. gun] = {
        first,
        "Integrated Picatinny rails: Up, Right",
        "Available Picatinny Slots: Left",
    }
end
table.insert(lines[M .. "AUGA3"], "Compatible Muzzle Device: AR Muzzle Mount")
table.insert(lines[M .. "AUGPARA"], "Compatible Muzzle Device: 9x19mm SMG Muzzle Mount")
table.insert(lines[M .. "AUGHBAR"], "Heavy barrel with an integrated folding bipod.")
for _, mag in ipairs({ "9x19Magazine25_AUG", "9x19Magazine32_AUG" }) do
    lines[M .. mag] = { "Uses 9x19mm rounds." }
end
for _, mag in ipairs({ "762x39Magazine30_AUG", "762x39Magazine50_AUG" }) do
    lines[M .. mag] = { "Uses 7.62x39mm rounds." }
end
GunsOfTien_TooltipStates[M .. "AUGHBAR_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 10%",
    "Critical and Hit Chance increased by 15%",
    "Automatic fire spread reduced by 35%",
}

lines[M .. "SCARL"] = {
    "Uses .223/5.56x45mm NATO rounds.",
    "Integrated Picatinny rails: Up, Down, Left, Right",
    "Compatible Muzzle Device: AR Muzzle Mount",
}
lines[M .. "SCARH"] = {
    "Uses .308/7.62x51mm NATO rounds.",
    "Integrated Picatinny rails: Up, Down, Left, Right",
    "Compatible Muzzle Device: SCAR-H Muzzle Mount",
}
lines[M .. "762x51Magazine20_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }
lines[M .. "762x51Magazine10_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }
lines[M .. "762x51Magazine50_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }

lines[M .. "MP7A1"] = {
    "Uses 4.6x30mm rounds.",
    "Integrated Picatinny rails: Up, Left, Right",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines[M .. "MP7A2"] = {
    "Uses 4.6x30mm rounds.",
    "Integrated Picatinny rails: Up, Left, Right, Down",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines[M .. "P90TR"] = {
    "Uses 5.7x28mm rounds.",
    "Integrated Picatinny rails: Up, Left, Right",
    "50-round magazine on top. Ejects spent cases downward.",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines["MarzGuns.FIVESEVEN"] = {
    "Uses 5.7x28mm rounds.",
    "Compatible Mounting Device: Beretta Mount",
    "Compatible Muzzle Device: 5.7x28mm Muzzle Mount",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines[M .. "57x28Magazine20_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "57x28Magazine30_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "UCP"] = {
    "Uses 4.6x30mm rounds.",
    "H&K prototype",
    "Compatible Mounting Device: Beretta Mount",
    "Compatible Muzzle Device: 4.6x30mm Muzzle Mount",
    "Standard rounds pierce and can hit up to 2 targets.",
}
lines[M .. "46x30Magazine20_UCP"] = { "Uses 4.6x30mm rounds." }
lines[M .. "46x30Magazine40_UCP"] = { "Uses 4.6x30mm rounds." }
for _, mag in ipairs({ "46x30Magazine20_MP7", "46x30Magazine30_MP7", "46x30Magazine40_MP7", "46x30Magazine60_MP7" }) do
    lines[M .. mag] = { "Uses 4.6x30mm rounds." }
end
lines[M .. "57x28Magazine50_P90"] = { "Uses 5.7x28mm rounds." }

for _, part in ipairs({ "MP7_Suppressor", "P90_Suppressor", "FIVESEVEN_Suppressor", "SCARH_Suppressor" }) do
    lines[M .. part] = {
        "Sound Radius and Volume reduced by 70%",
        "Damage to targets decreased by 10%",
        "Removes Muzzle Flash",
        "Needs its Muzzle Mount Device",
    }
end
for _, part in ipairs({ "MP7_Muzzle_Mount_Device", "P90_Muzzle_Mount_Device", "SCARH_Muzzle_Mount_Device" }) do
    lines[M .. part] = {
        "No Direct Stat Changes",
        "Enables its Suppressor",
        "Needs Wrench to install or remove.",
    }
end

lines[M .. "46x30_Bullet"] = { "DM11 solid copper-plated steel bullet", "Piercing targets", "Able to hit up to 2 targets" }
lines[M .. "57x28_Bullet"] = { "SS190 steel and aluminium penetrator", "Piercing targets", "Able to hit up to 2 targets" }
for round, damage in pairs({ ["46x30_Bullet_Subsonic"] = "40%", ["57x28_Bullet_SB193"] = "30%" }) do
    lines[M .. round] = {
        "Damage to targets decreased by " .. damage,
        "Sound radius and volume reduced by 30%",
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
