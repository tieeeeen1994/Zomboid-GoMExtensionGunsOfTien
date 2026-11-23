--[[
    Guns of Tien - Post-93 -- "Information" lines in Guns of Marz's item tooltips for the MP7A1, the P90 TR, the
    Five-seveN, the UCP, the SCAR-L and SCAR-H, the UMP45 and UMP9, the Steyr AUG A3, Para and HBAR, the KRISS Vector
    .45, 9mm, CRB and SDP, the PS90, the MDRx .223 and .308, the Mk 11, the HK416, the HK416 .22 pistol, the HK417s, the Grozas, their magazines, suppressors and rounds (GoM's tooltipsPergun table, read at render time, hard-coded English like
    GoM's own entries). Every gun's other lines (rails, mounts, built-in parts) and every magazine's "Fits:" line are
    written by the main mod's client/GunsOfTien/GunLines.lua from the registries.
--]]

local ok, tooltips = pcall(require, "MarzWeapons/ItemTooltipsTable")
if not ok or type(tooltips) ~= "table" or type(tooltips.tooltipsPergun) ~= "table" then return end
pcall(require, "GunsOfTien/Tooltips")     -- the main mod's lines first: some below replace them (PBS-1)

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

lines[M .. "UMP45"] = { "Uses .45 rounds" }
lines[M .. "UMP9"] = { "Uses 9x19mm rounds" }
for _, mag in ipairs({ "45Magazine25_UMP", "45Magazine20_UMP", "45Magazine10_UMP" }) do
    lines[M .. mag] = { "Uses .45 rounds." }
end
lines[M .. "9x19Magazine30_UMP"] = { "Uses 9x19mm rounds." }

-- The KRISS Vectors (shared/GunsOfTienPost93/Vector.lua): integral top and bottom rails, GoM's Picatinny Rail upgrades
-- on both sides (KRISS's side rails), the side-folding stock with the UMPs' stats; Glock's magazines, ours fitting
-- the Glock 21 / GoM's Glock 17 too
GunsOfTien_TooltipStates[M .. "VECTOR_Integrated_Stock_Deployed"] = GunsOfTien_TooltipStates[M .. "UMP_Integrated_Stock_Deployed"]
for gun, uses in pairs({ VECTOR45 = "Uses .45 rounds", VECTORCRB = "Uses .45 rounds", VECTOR9 = "Uses 9x19mm rounds",
    VECTORSDP = "Uses 9x19mm rounds" }) do
    lines[M .. gun] = { uses }
end
lines[M .. "45Magazine30_GLOCK21"] = { "Uses .45 rounds" }
for _, mag in ipairs({ "9x19Magazine33_GLOCK", "9x19Magazine40_GLOCK" }) do
    lines[M .. mag] = { "Uses 9x19mm rounds" }
end

-- The Steyr AUGs (shared/GunsOfTienPost93/AUG.lua): the folding grip's state lines are the main mod's (the same
-- parts as its A1); the HBAR's bipod states as the main mod words GoM's bipods'.
for gun, uses in pairs({ AUGA3 = "Uses .223/5.56x45mm NATO rounds", AUGPARA = "Uses 9x19mm rounds",
    AUGHBAR = "Uses 7.62x39mm rounds" }) do
    lines[M .. gun] = { uses }
end
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

lines[M .. "SCARL"] = { "Uses .223/5.56x45mm NATO rounds" }
lines[M .. "SCARH"] = { "Uses .308/7.62x51mm NATO rounds" }
lines[M .. "762x51Magazine20_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }
lines[M .. "MK11"] = { "Uses .308/7.62x51mm NATO rounds" }
lines[M .. "762x51Magazine10_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }
lines[M .. "SV98"] = { "Uses 7.62x54mmR rounds" }
lines[M .. "762x54Magazine10_SV98"] = { "Uses 7.62x54mmR rounds." }
lines[M .. "SV99"] = { "Uses .22 LR rounds" }
lines[M .. "22LRMagazine5_SV99"] = { "Uses .22 LR rounds." }
-- The HK416 (shared/GunsOfTienPost93/HK416.lua): its stock with the SCARs' stats
lines[M .. "HK416"] = { "Uses .223/5.56x45mm NATO rounds" }
GunsOfTien_TooltipStates[M .. "HK416_Integrated_Stock_Deployed"] = {
    "Collapsible stock deployed:",
    "Aiming Time reduced by 15%",
    "Hit Chance increased by 15%",
}
-- The HK417s (shared/GunsOfTienPost93/HK417.lua): the HK416's stock
for _, gun in ipairs({ "HK417", "HK417S" }) do
    lines[M .. gun] = { "Uses .308/7.62x51mm NATO rounds" }
end
for _, n in ipairs({ 10, 20 }) do
    lines[M .. "762x51Magazine" .. n .. "_HK417"] = { "Uses .308/7.62x51mm NATO rounds." }
end
GunsOfTien_TooltipStates[M .. "HK417_Integrated_Stock_Deployed"] = {
    "Collapsible stock deployed:",
    "Aiming Time reduced by 15%",
    "Hit Chance increased by 15%",
}
lines[M .. "HK416QR22"] = { "Uses .22 LR rounds" }
for _, n in ipairs({ 10, 20, 30 }) do
    lines[M .. "22LRMagazine" .. n .. "_HK416"] = { "Uses .22 LR rounds." }
end
-- The Grozas (shared/GunsOfTienPost93/Groza.lua); the GP-25 worded as GoM's M79
for gun, uses in pairs({ GROZA1 = "Uses 7.62x39mm rounds", GROZAGL = "Uses 7.62x39mm rounds",
    GROZAGL_GP25 = "Uses 40mm rounds", GROZA2 = "Uses 5.45x39mm rounds", GROZA4 = "Uses 9x39mm rounds" }) do
    lines[M .. gun] = { uses }
end
lines[M .. "762x51Magazine50_SCARH"] = { "Uses .308/7.62x51mm NATO rounds." }

for gun, uses in pairs({ MP7A1 = "Uses 4.6x30mm rounds", MP7A2 = "Uses 4.6x30mm rounds", P90TR = "Uses 5.7x28mm rounds",
    PS90 = "Uses 5.7x28mm rounds", MDR223 = "Uses .223/5.56x45mm NATO rounds",
    MDR308 = "Uses .308/7.62x51mm NATO rounds" }) do
    lines[M .. gun] = { uses }
end
-- the MDRx .308's ALX bipod handguard: its bipod states worded as the HBAR's, without the automatic fire line
GunsOfTien_TooltipStates[M .. "MDR308_Integrated_Bipod_Deployed"] = {
    "Folding bipod deployed:",
    "Aiming Time increased by 10%",
    "Critical and Hit Chance increased by 15%",
}
for _, mag in ipairs({ "762x51Magazine10_PMAG", "762x51Magazine20_PMAG", "762x51Magazine25_PMAG",
    "762x51Magazine50_PMAG" }) do
    lines[M .. mag] = { "Uses .308/7.62x51mm NATO rounds." }
end

lines["MarzGuns.FIVESEVEN"] = { "Uses 5.7x28mm rounds" }
lines[M .. "57x28Magazine20_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "57x28Magazine30_FIVESEVEN"] = { "Uses 5.7x28mm rounds." }
lines[M .. "UCP"] = { "Uses 4.6x30mm rounds" }
lines[M .. "46x30Magazine20_UCP"] = { "Uses 4.6x30mm rounds." }
lines[M .. "46x30Magazine40_UCP"] = { "Uses 4.6x30mm rounds." }
for _, mag in ipairs({ "46x30Magazine20_MP7", "46x30Magazine30_MP7", "46x30Magazine40_MP7", "46x30Magazine60_MP7" }) do
    lines[M .. mag] = { "Uses 4.6x30mm rounds." }
end
-- the P90's magazine, mount device and SP90 and the SS190 round: the main mod's client/GunsOfTien/P90Tooltips.lua

-- suppressors and mount devices in GoM's own wording (its MKI / PBS-1 / P45 and their mounts): can -> { calibre,
-- the guns it fits } (each MountOn in items_guns.txt)
for part, can in pairs({
    MP7_Suppressor = { "4.6x30mm", "MP7A1, MP7A2 and UCP" },
    P90_Suppressor = { "5.7x28mm", "P90, P90 TR and PS90" },
    FIVESEVEN_Suppressor = { "5.7x28mm", "Five-SeveN" },
    SCARH_Suppressor = { "7.62x51mm", "7.62x51mm rifles" },     -- every one but the M60 (MuzzleFamilies.lua)
}) do
    lines[M .. part] = {
        "Requires " .. can[1] .. " Muzzle Mount",
        "Sound Radius and Volume reduced by 70%",
        "Damage reduced by 10%",
        "Removes Muzzle Flash",
        "Can be mounted on " .. can[2],
        "Needs Wrench to install or remove.",
    }
end
for part, calibre in pairs({ MP7_Muzzle_Mount_Device = "4.6x30mm", P90_Muzzle_Mount_Device = "5.7x28mm",
    SCARH_Muzzle_Mount_Device = "7.62x51mm" }) do
    lines[M .. part] = {
        "No Direct Stat Changes",
        "Enables " .. calibre .. " Muzzle Attachments",
        "Needs Wrench to install or remove.",
    }
end
-- GoM's AK can on Post-93's guns too (Groza.lua, the main mod's MuzzleFamilies.lua): the main mod's PBS-1 line with
-- the Grozas (its P45 line already says carbines, for the Vector .45 Carbine)
lines["MarzGuns.PBS-1_Suppressor"] = {
    "Requires AK Muzzle Mount",
    "Sound Radius and Volume reduced by 70%",
    "Damage reduced by 10%",
    "Removes Muzzle Flash",
    "Can be mounted on AK-47, AK-74, AKS-74U, RPK, RPK-74, SKS, Groza-1 and Groza-2",
    "Needs Wrench to install or remove.",
}

lines[M .. "46x30_Bullet"] = { "DM11 solid copper-plated steel bullet", "Piercing targets", "Able to hit up to 2 targets" }
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
