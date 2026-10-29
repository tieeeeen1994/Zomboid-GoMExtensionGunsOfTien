--[[
    Guns of Tien - Post-93 -- the MP7A1 and MP7A2, P90 TR, Five-seveN and UCP Prototype in Gunworks' and Guns of
    Marz's registries.

    The MP7A2 (user, 2026-10-18) is the A1 with a rail handguard for the folding front grip: registered exactly like
    the A1 (same magazines, fire rate, reload animations, stock, spawn parts; it uses the A1's integrated rail parts
    for its top and side rails), plus an integrated bottom rail that GoM's three foregrips need.

    Everything a GoM gun goes through, done for ours (CLAUDE.md, "Gun data and registries in GoM"): magazine
    profiles, rate of fire (required for Gunworks' real auto fire), the animated bolt, reload animations, the MP7's
    collapsible stock and the stats of its folding front grip (the fold itself is Foregrip.lua), integrated rails as parents of GoM's optics / lights / lasers, the suppressors and their mount
    devices, parts that cannot be removed, spawn-time parts and magazines, and GoM parts allowed on our guns
    (MountOn appended; DoParam replaces the list, so it is read and written back whole).

    The SCAR-L and SCAR-H (user, 2026-10-20) are registered as GoM's M4A1 and FAL are: the SCAR-L in GoM's STANAG
    magazine profile, the SCAR-H with its own magazines, both at about 600 rpm, the charging handle animated (it rides
    with the bolt carrier), GoM's FNC reload (SCAR-L) and its FAL reload (SCAR-H), the shared side-folding stock with GoM's G36 stock stats, four integral rails as parents of GoM's optics, foregrips,
    bipods, lights and lasers, GoM's AR muzzle parts on the SCAR-L and the SCAR-H's own mount device and suppressor.

    The UMP45 and UMP9 (user, 2026-10-22) are registered as GoM's MP5 is: each with its own magazines (in GoM's .45 ACP
    and 9x19mm families, Ammunition.lua), select fire with H&K's two-round burst, GoM's MP5 reload, the shared
    side-folding stock with GoM's G36C stock stats, four integral rails as parents of GoM's MP5 accessories (optics,
    foregrips, lights, lasers). The UMP45 takes GoM's .45 mount device and P45 suppressor, as its MAC-10 does, the
    UMP9 the main mod's 9x19mm SMG mount device and AWC Mk9 (GoM's 9mm cans fit its pistols only). The charging
    handle animated as GoM animates its MP5's.

    The Five-seveN is MarzGuns.FIVESEVEN (GoM names it but ships nothing else) and is registered like GoM's Glock 17
    and M92FS: magazine profile, the animated slide, permanent magazines, spawn parts, GoM's pistol parts allowed on
    it. Like GoM's pistols it takes GoM's pistol reload and has no rate of fire (semi-automatic only). The UCP
    Prototype (GunsOfTienPost93.UCP, H&K's 4.6x30mm pistol) is registered the same way and takes the MP7's mount
    device and Rotex-II suppressor.

    Every gun reloads with one of GoM's own animations and is held with vanilla's clips (2026-10-29, the main mod's
    GoMReloads.lua): the MP7s and the P90 one-handed, like GoM's MP5K.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")

for _, file in ipairs({ "Magazines", "RPM", "ReloadAnims", "Stocks", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local MP7 = M .. "MP7A1"
local MP7A2 = M .. "MP7A2"
local MP7S = { MP7, MP7A2 }
-- GoM's foregrips (MarzGuns' Picatinny_Rail_Down / G36C rail), on the A2's bottom rail
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local P90 = M .. "P90TR"
local MP7_MAGS = { M .. "46x30Magazine20_MP7", M .. "46x30Magazine30_MP7", M .. "46x30Magazine40_MP7",
    M .. "46x30Magazine60_MP7" }
local P90_MAGS = { M .. "57x28Magazine50_P90" }
local FIVESEVEN = "MarzGuns.FIVESEVEN"
local FIVESEVEN_MAGS = { M .. "57x28Magazine20_FIVESEVEN", M .. "57x28Magazine30_FIVESEVEN" }
local UCP = M .. "UCP"
local UCP_MAGS = { M .. "46x30Magazine20_UCP", M .. "46x30Magazine40_UCP" }
local SCARL = M .. "SCARL"
local SCARH = M .. "SCARH"
local SCARS = { SCARL, SCARH }
local SCARH_MAGS = { M .. "762x51Magazine20_SCARH", M .. "762x51Magazine10_SCARH", M .. "762x51Magazine50_SCARH" }
local UMP45 = M .. "UMP45"
local UMP9 = M .. "UMP9"
local UMPS = { UMP45, UMP9 }
local UMP45_MAGS = { M .. "45Magazine25_UMP", M .. "45Magazine20_UMP", M .. "45Magazine10_UMP" }
local UMP9_MAGS = { M .. "9x19Magazine30_UMP" }
local STANAGS = {}
for _, n in ipairs({ 20, 25, 30, 50, 60, 75, 100, 150 }) do
    STANAGS[#STANAGS + 1] = "MarzGuns.556x45Magazine" .. n .. "_STANAG"
end

-------------------------------------------------
-- Magazines
-------------------------------------------------
Magazine.RegisterMagazineProfile("4.6x30mm MP7", MP7_MAGS)
Magazine.RegisterWeaponWithProfile("4.6x30mm MP7", MP7)
Magazine.RegisterWeaponWithProfile("4.6x30mm MP7", MP7A2)
Magazine.RegisterMagazineProfile("5.7x28mm P90", P90_MAGS)
Magazine.RegisterWeaponWithProfile("5.7x28mm P90", P90)
Magazine.RegisterMagazineProfile("5.7x28mm Five-seveN", FIVESEVEN_MAGS)
Magazine.RegisterWeaponWithProfile("5.7x28mm Five-seveN", FIVESEVEN)
Magazine.RegisterMagazineProfile("4.6x30mm UCP", UCP_MAGS)
Magazine.RegisterWeaponWithProfile("4.6x30mm UCP", UCP)
Magazine.RegisterWeaponWithProfile("STANAG", SCARL)          -- GoM's own profile (M16s, M4A1, FNC...)
Magazine.RegisterMagazineProfile("7.62x51mm SCAR-H", SCARH_MAGS)
Magazine.RegisterWeaponWithProfile("7.62x51mm SCAR-H", SCARH)
Magazine.RegisterMagazineProfile(".45 ACP UMP45", UMP45_MAGS)
Magazine.RegisterWeaponWithProfile(".45 ACP UMP45", UMP45)
Magazine.RegisterMagazineProfile("9x19mm UMP9", UMP9_MAGS)
Magazine.RegisterWeaponWithProfile("9x19mm UMP9", UMP9)

-------------------------------------------------
-- Five-seveN and UCP slides: GoM's pistol slide swap (Slide_Fired / Slide_Lock each shot, AnimationsFiring.lua)
-------------------------------------------------
for _, pistol in ipairs({ FIVESEVEN, UCP }) do
    Animations.RegisterWeaponWithAnimatedParts(pistol, {
        SingleAttachment = { open = "MarzGuns.Slide_Fired", locked = "MarzGuns.Slide_Lock" },
        cycleTicks = 5,
    })
end

-------------------------------------------------
-- Rate of fire: MP7A1 950 rpm, P90 900 rpm. Both are light-recoiling, so they spread less than the MP5.
-------------------------------------------------
for _, gun in ipairs(MP7S) do
    RateOfFire.RegisterWeapon(gun, { rpm = 950, enableSpread = true, sustainedSpread = 0.08, maxSpread = 1.3 })
end
RateOfFire.RegisterWeapon(P90, { rpm = 900, enableSpread = true, sustainedSpread = 0.06, maxSpread = 1.1 })
-- SCAR-L 625 rpm, a soft-shooting piston 5.56 (GoM's M4A1: 800, 0.10 / 2.5); SCAR-H 600 rpm, a 7.62x51 between the
-- M4A1 and GoM's FAL (750, 0.3 / 4.5)
RateOfFire.RegisterWeapon(SCARL, { rpm = 625, enableSpread = true, sustainedSpread = 0.09, maxSpread = 2.2 })
RateOfFire.RegisterWeapon(SCARH, { rpm = 600, enableSpread = true, sustainedSpread = 0.22, maxSpread = 3.5 })
-- UMP45 600 rpm, the .45's heavier recoil in a light gun spreading more than GoM's MP5 (800, 0.1 / 1.5); UMP9 700 rpm,
-- close to the MP5. Both with H&K's two-round burst (Gunworks' burstCount; GoM's M16A2 uses 3).
RateOfFire.RegisterWeapon(UMP45, { rpm = 600, burstCount = 2, enableSpread = true, sustainedSpread = 0.18,
    maxSpread = 2.2 })
RateOfFire.RegisterWeapon(UMP9, { rpm = 700, burstCount = 2, enableSpread = true, sustainedSpread = 0.11,
    maxSpread = 1.6 })
-- the UMP's stock unfolded steadies automatic fire as GoM's G36C stock does (its RPM.lua)
RateOfFire.RegisterSpreadPartModifier(M .. "UMP_Integrated_Stock_Deployed",
    { sustainedSpreadMult = 0.75, maxSpreadMult = 0.85 })
-- The SCARs' charging handle rides with the bolt carrier: GoM's Bolt_Fired / Bolt_Lock swap, as on its rifles.
for _, gun in ipairs(SCARS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
end
-- the MP7's front grip unfolded steadies automatic fire as GoM's Stub Foregrip does
RateOfFire.RegisterSpreadPartModifier(M .. "MP7A1_Integrated_Foregrip_Deployed",
    { sustainedSpreadMult = 0.85, maxSpreadMult = 0.85 })

-------------------------------------------------
-- The MP7s', the P90's and the UMPs' charging handles: GoM's bolt swap, as GoM animates every one of its guns (its
-- MP5s and MAC-10 too; user, 2026-10-29: "I want us to use GoM's way"). The real handles stay put when firing; they
-- flick back on each shot, stay back on an empty gun and move with the rack, drawn at bolt_lock / bolt_fired
-- (the builders' handle travel).
-------------------------------------------------
for _, gun in ipairs({ MP7, MP7A2, P90, UMP45, UMP9 }) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
end

-------------------------------------------------
-- Reload animations: GoM's own (the main mod's GoMReloads.lua). Held like a pistol, the MP7s and the P90 take its
-- MP5K's ("handgun2"), the Five-seveN and the UCP its pistols'; the SCAR-L its FNC's (rifle magazine, side charging
-- handle), the SCAR-H its FAL's, the UMPs its MP5's.
-------------------------------------------------
local GoMReloads = require("GunsOfTien/GoMReloads")
for gun, animId in pairs({
    [MP7] = "handgun2", [MP7A2] = "handgun2", [P90] = "handgun2",
    [FIVESEVEN] = "pistol_reload", [UCP] = "pistol_reload",
    [SCARL] = "fnc_rifle", [SCARH] = "fal_rifle",
    [UMP45] = "MP5", [UMP9] = "MP5",
}) do
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile(animId))
end

-------------------------------------------------
-- MP7A1 collapsible stock (as GoM's MP5)
-------------------------------------------------
for _, gun in ipairs(MP7S) do                       -- the A2 has the A1's stock
    FoldingStock.RegisterWeapon(gun, {
        attachments = {
            partType = "StockIntegrated",
            folded = M .. "MP7A1_Integrated_Stock_Folded",
            deployed = M .. "MP7A1_Integrated_Stock_Deployed",
        },
        initialState = "folded",
    })
end

-- the SCARs' side-folding stock (one part pair for both), and the UMPs' (one pair for both)
for _, gun in ipairs(UMPS) do
    FoldingStock.RegisterWeapon(gun, {
        attachments = {
            partType = "StockIntegrated",
            folded = M .. "UMP_Integrated_Stock_Folded",
            deployed = M .. "UMP_Integrated_Stock_Deployed",
        },
        initialState = "folded",
    })
end
for _, gun in ipairs(SCARS) do
    FoldingStock.RegisterWeapon(gun, {
        attachments = {
            partType = "StockIntegrated",
            folded = M .. "SCAR_Integrated_Stock_Folded",
            deployed = M .. "SCAR_Integrated_Stock_Deployed",
        },
        initialState = "folded",
    })
end

CSA.RegisterMultipleParts({
    [M .. "MP7A1_Integrated_Stock_Folded"] = {},
    [M .. "MP7A1_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.75),
    },
    -- MP7A1 integral front grip (Foregrip.lua swaps the parts): unfolded, GoM's Stub Foregrip stats
    [M .. "MP7A1_Integrated_Foregrip_Folded"] = {},
    [M .. "MP7A1_Integrated_Foregrip_Deployed"] = {
        SF.Multiply("AimingTime", 0.8),
        SF.Multiply("CriticalChance", 1.15),
        SF.Multiply("HitChance", 1.15),
    },
    -- GoM's suppressor stats (its pistol suppressors' sound).
    [M .. "MP7_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
    [M .. "P90_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
    -- SCAR stock deployed: GoM's G36 stock (another side-folding polymer stock)
    [M .. "SCAR_Integrated_Stock_Folded"] = {},
    [M .. "SCAR_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.85),
    },
    -- UMP stock deployed: GoM's G36C stock (another side-folding polymer stock on a short gun)
    [M .. "UMP_Integrated_Stock_Folded"] = {},
    [M .. "UMP_Integrated_Stock_Deployed"] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.75),
    },
    -- GoM's rifle suppressors' stats (MKI / NDR), with their rifle swing sound
    [M .. "SCARH_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRevolverShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
    [M .. "FIVESEVEN_Suppressor"] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRifleShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
})

-------------------------------------------------
-- Integrated rails as mounts for GoM's optics, lights and lasers; suppressors need their mount device
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }

local BIPODS = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
RequiredAttachment.RegisterRequired(OPTICS, { M .. "MP7A1_Integrated_Rail_Up", M .. "P90TR_Integrated_Rail_Up",
    M .. "SCAR_Integrated_Rail_Up" })
RequiredAttachment.RegisterRequired(LIGHTS, { M .. "MP7A1_Integrated_Rail_Left", M .. "P90TR_Integrated_Rail_Left",
    M .. "SCAR_Integrated_Rail_Left" })
RequiredAttachment.RegisterRequired(LASERS, { M .. "MP7A1_Integrated_Rail_Right", M .. "P90TR_Integrated_Rail_Right",
    M .. "SCAR_Integrated_Rail_Right" })
RequiredAttachment.RegisterRequired(FOREGRIPS, { M .. "SCAR_Integrated_Rail_Down" })
RequiredAttachment.RegisterRequired(BIPODS, { M .. "SCAR_Integrated_Rail_Down" })
RequiredAttachment.RegisterRequired(OPTICS, { M .. "UMP_Integrated_Rail_Up" })
RequiredAttachment.RegisterRequired(LIGHTS, { M .. "UMP_Integrated_Rail_Left" })
RequiredAttachment.RegisterRequired(LASERS, { M .. "UMP_Integrated_Rail_Right" })
RequiredAttachment.RegisterRequired(FOREGRIPS, { M .. "UMP_Integrated_Rail_Down" })
RequiredAttachment.RegisterRequired({ M .. "SCARH_Suppressor" }, { M .. "SCARH_Muzzle_Mount_Device" })
RequiredAttachment.RegisterRequired({ M .. "MP7_Suppressor" }, { M .. "MP7_Muzzle_Mount_Device" })
-- appended to GoM's own rule (Picatinny_Rail_Down or the G36C's rail): any one of them will do
RequiredAttachment.RegisterRequired(FOREGRIPS, { M .. "MP7A2_Integrated_Rail_Down" })
RequiredAttachment.RegisterRequired({ M .. "P90_Suppressor" }, { M .. "P90_Muzzle_Mount_Device" })
-- the Five-seveN's own suppressor screws onto the same 5.7x28mm mount device (shared, as GoM's pistols share theirs)
RequiredAttachment.RegisterRequired({ M .. "FIVESEVEN_Suppressor" }, { M .. "P90_Muzzle_Mount_Device" })

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu
-------------------------------------------------
local permanent = {}
for _, list in ipairs({ MP7_MAGS, P90_MAGS, FIVESEVEN_MAGS, UCP_MAGS, SCARH_MAGS, UMP45_MAGS, UMP9_MAGS }) do
    for _, part in ipairs(list) do permanent[#permanent + 1] = part end
end
for _, part in ipairs({ "MP7A1_Integrated_Rail_Up", "MP7A1_Integrated_Rail_Left", "MP7A1_Integrated_Rail_Right",
    "MP7A2_Integrated_Rail_Down",
    "P90TR_Integrated_Rail_Up", "P90TR_Integrated_Rail_Left", "P90TR_Integrated_Rail_Right",
    "SCAR_Integrated_Rail_Up", "SCAR_Integrated_Rail_Down", "SCAR_Integrated_Rail_Left",
    "SCAR_Integrated_Rail_Right",
    "UMP_Integrated_Rail_Up", "UMP_Integrated_Rail_Down", "UMP_Integrated_Rail_Left", "UMP_Integrated_Rail_Right" }) do
    permanent[#permanent + 1] = M .. part
end
PreventRemoval.Register(permanent)

-------------------------------------------------
-- Parts and magazines a found gun comes with (GoM's MarzGuns_OnCreate.AttachParts reads this table)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[MP7] = {
        required = {
            "MarzGuns.Bolt_Lock",
            M .. "MP7A1_Integrated_Stock_Folded",
            M .. "MP7A1_Integrated_Foregrip_Folded",
            M .. "MP7A1_Integrated_Rail_Up",
            M .. "MP7A1_Integrated_Rail_Left",
            M .. "MP7A1_Integrated_Rail_Right",
        },
        optionals = {
            M .. "46x30Magazine20_MP7:30",
            M .. "46x30Magazine30_MP7:20",
            M .. "46x30Magazine40_MP7:5",
            M .. "46x30Magazine60_MP7:2",
            "MarzGuns.EXPS1_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            M .. "MP7_Muzzle_Mount_Device:10",
        },
    }
    -- The A2: the A1's parts and magazines, no folding grip, its bottom rail, GoM's foregrips at GoM's own chances
    -- (its MP5: Stub and MKC 10, MK2 5).
    spawnTable[MP7A2] = {
        required = {
            "MarzGuns.Bolt_Lock",
            M .. "MP7A1_Integrated_Stock_Folded",
            M .. "MP7A1_Integrated_Rail_Up",
            M .. "MP7A1_Integrated_Rail_Left",
            M .. "MP7A1_Integrated_Rail_Right",
            M .. "MP7A2_Integrated_Rail_Down",
        },
        optionals = {
            M .. "46x30Magazine20_MP7:30",
            M .. "46x30Magazine30_MP7:20",
            M .. "46x30Magazine40_MP7:5",
            M .. "46x30Magazine60_MP7:2",
            "MarzGuns.EXPS1_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            "MarzGuns.Stub_Foregrip:10", "MarzGuns.MKC_Foregrip:10", "MarzGuns.MK2_Foregrip:5",
            M .. "MP7_Muzzle_Mount_Device:10",
        },
    }
    spawnTable[P90] = {
        required = {
            "MarzGuns.Bolt_Lock",
            M .. "P90TR_Integrated_Rail_Up",
            M .. "P90TR_Integrated_Rail_Left",
            M .. "P90TR_Integrated_Rail_Right",
        },
        optionals = {
            M .. "57x28Magazine50_P90:60",
            "MarzGuns.EXPS1_Sight:10", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:10",
            "MarzGuns.ReflexS2_Sight:5",
            "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
            "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
            M .. "P90_Muzzle_Mount_Device:10",
        },
    }
    -- The SCARs as GoM's M4A1 / FAL come (their optics, foregrips, lights and lasers at GoM's chances; no ":PR*"
    -- rail suffix: the integral rails are always there), the stock folded as GoM's guns spawn.
    local SCAR_COMMON = {
        "MarzGuns.ReflexS2_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.EXPS1_Sight:5", "MarzGuns.Aimpoint_Sight:5",
        "MarzGuns.LR4X_Scope:3", "MarzGuns.TA28_Scope:3", "MarzGuns.ElcanX2_Scope:3",
        "MarzGuns.Stub_Foregrip:5", "MarzGuns.MKC_Foregrip:5", "MarzGuns.MK2_Foregrip:3",
        "MarzGuns.AimRight_Laser:3", "MarzGuns.LRX-7_Laser:3",
        "MarzGuns.BrightPoint-5_Light:5", "MarzGuns.SR7_Light:5",
    }
    local function scarEntry(mags, extra)
        local optionals = {}
        for _, list in ipairs({ mags, SCAR_COMMON, extra }) do
            for _, e in ipairs(list) do optionals[#optionals + 1] = e end
        end
        return {
            required = {
                "MarzGuns.Bolt_Lock",
                M .. "SCAR_Integrated_Stock_Folded",
                M .. "SCAR_Integrated_Rail_Up",
                M .. "SCAR_Integrated_Rail_Down",
                M .. "SCAR_Integrated_Rail_Left",
                M .. "SCAR_Integrated_Rail_Right",
            },
            optionals = optionals,
        }
    end
    -- GoM's M4A1 magazines (20 / 25 / 30 at 50 / 30 / 30); FN's SCAR-H magazines, the 10 rarely, ProMag's 50-round
    -- drum as rarely as the MP7's 60 (2%); the FAL's bipod
    spawnTable[SCARL] = scarEntry({ "MarzGuns.556x45Magazine20_STANAG:30", "MarzGuns.556x45Magazine25_STANAG:20",
        "MarzGuns.556x45Magazine30_STANAG:50" }, { "MarzGuns.Bipod_Folded:2", "MarzGuns.AR_Muzzle_Mount_Device:5" })
    spawnTable[SCARH] = scarEntry({ M .. "762x51Magazine20_SCARH:60", M .. "762x51Magazine10_SCARH:10",
        M .. "762x51Magazine50_SCARH:2" },
        { "MarzGuns.TR06X_Scope:1", "MarzGuns.LR10X_Scope:1", "MarzGuns.Bipod_Folded:5",
          M .. "SCARH_Muzzle_Mount_Device:5" })
    -- The UMPs as GoM's MP5 comes (its optics, foregrips, lights and lasers at its chances; no ":PR*" rail suffix: the
    -- integral rails are always there), the stock folded. Magazines by GoM's own rule (user, 2026-10-22: "base your
    -- decisions on how GoM handles it"): its MP5 rolls 20 / 25 / 30 at 30 / 20 / 5, the shortest likeliest, and its
    -- one-magazine guns 50 (AS VAL, M14, Glock 17).
    local UMP_COMMON = {
        "MarzGuns.EXPS1_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5", "MarzGuns.ReflexS2_Sight:5",
        "MarzGuns.Stub_Foregrip:10", "MarzGuns.MKC_Foregrip:10", "MarzGuns.MK2_Foregrip:5",
        "MarzGuns.AimRight_Laser:5", "MarzGuns.LRX-7_Laser:5",
        "MarzGuns.BrightPoint-5_Light:10", "MarzGuns.SR7_Light:10",
    }
    local function umpEntry(mags)
        local optionals = {}
        for _, list in ipairs({ mags, UMP_COMMON }) do
            for _, e in ipairs(list) do optionals[#optionals + 1] = e end
        end
        return {
            required = {
                "MarzGuns.Bolt_Lock",
                M .. "UMP_Integrated_Stock_Folded",
                M .. "UMP_Integrated_Rail_Up",
                M .. "UMP_Integrated_Rail_Down",
                M .. "UMP_Integrated_Rail_Left",
                M .. "UMP_Integrated_Rail_Right",
            },
            optionals = optionals,
        }
    end
    spawnTable[UMP45] = umpEntry({ M .. "45Magazine10_UMP:30", M .. "45Magazine20_UMP:20", M .. "45Magazine25_UMP:5" })
    spawnTable[UMP9] = umpEntry({ M .. "9x19Magazine30_UMP:50" })
    -- As GoM's Glock 17 (":BM" fits the Beretta mount the sight needs), plus the extended magazine and the mount device.
    spawnTable[FIVESEVEN] = {
        required = {
            "MarzGuns.Slide_Lock",
        },
        optionals = {
            M .. "57x28Magazine20_FIVESEVEN:50",
            M .. "57x28Magazine30_FIVESEVEN:5",
            "MarzGuns.PL4_Sight:5:BM", "MarzGuns.PM2_Sight:5:BM", "MarzGuns.PS1_Sight:5:BM",
            "MarzGuns.LP_Light:5", "MarzGuns.TL_Light:5",
            M .. "P90_Muzzle_Mount_Device:5",
        },
    }
    -- The same as the Five-seveN's, the drum as its extended magazine.
    spawnTable[UCP] = {
        required = {
            "MarzGuns.Slide_Lock",
        },
        optionals = {
            M .. "46x30Magazine20_UCP:50",
            M .. "46x30Magazine40_UCP:5",
            "MarzGuns.PL4_Sight:5:BM", "MarzGuns.PM2_Sight:5:BM", "MarzGuns.PS1_Sight:5:BM",
            "MarzGuns.LP_Light:5", "MarzGuns.TL_Light:5",
            M .. "MP7_Muzzle_Mount_Device:5",
        },
    }
end

-------------------------------------------------
-- GoM parts allowed on our guns: append to their MountOn
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

-- GoM's pistol parts on the Five-seveN (from the Glock 17's / M92FS's ModelWeaponPart lines; the sights need the
-- Beretta mount, GoM's own RequiredAttachment rule). Under the rail GoM's two pistol lights (LP, a compact weapon
-- light; TL, a flashlight in a clamp, the pre-rail way), no lasers (user, 2026-10-16).
local PISTOL_PARTS = {
    "MarzGuns.Beretta_Mount", "MarzGuns.PL4_Sight", "MarzGuns.PM2_Sight", "MarzGuns.PS1_Sight",
    "MarzGuns.LP_Light", "MarzGuns.TL_Light",
}

local function appendAll()
    for _, part in ipairs(OPTICS) do appendMountOn(part, { MP7, MP7A2, P90 }) end
    for _, part in ipairs(LIGHTS) do appendMountOn(part, { MP7, MP7A2, P90 }) end
    for _, part in ipairs(LASERS) do appendMountOn(part, { MP7, MP7A2, P90 }) end
    for _, part in ipairs(FOREGRIPS) do appendMountOn(part, { MP7A2 }) end
    -- the UMPs: GoM's MP5 accessories (optics, foregrips, lights, lasers); the UMP45 also its MAC-10's .45 mount
    -- device and P45 suppressor, the UMP9 the main mod's 9x19mm SMG mount device and Mk9 (GoM's 9mm cans fit its
    -- pistols only)
    for _, list in ipairs({ OPTICS, LIGHTS, LASERS, FOREGRIPS }) do
        for _, part in ipairs(list) do appendMountOn(part, UMPS) end
    end
    for _, part in ipairs({ "MarzGuns.45_Muzzle_Mount_Device", "MarzGuns.P45_Suppressor" }) do
        appendMountOn(part, { UMP45 })
    end
    for _, part in ipairs({ "GunsOfTien.SMG9_Muzzle_Mount_Device", "GunsOfTien.Mk9_Suppressor" }) do
        appendMountOn(part, { UMP9 })
    end
    for _, part in ipairs(PISTOL_PARTS) do appendMountOn(part, { FIVESEVEN, UCP }) end
    -- the SCARs: every GoM optic, foregrip, bipod, light and laser; the SCAR-L also GoM's STANAG magazines and its AR
    -- muzzle family (mount device, suppressors, compensator, flash hider, muzzle brake)
    for _, list in ipairs({ OPTICS, LIGHTS, LASERS, FOREGRIPS, BIPODS }) do
        for _, part in ipairs(list) do appendMountOn(part, SCARS) end
    end
    for _, part in ipairs(STANAGS) do appendMountOn(part, { SCARL }) end
    for _, part in ipairs({ "MarzGuns.AR_Muzzle_Mount_Device", "MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor",
        "MarzGuns.LR2_Compensator", "MarzGuns.LX_Flashhider", "MarzGuns.Trix42_Muzzlebreak" }) do
        appendMountOn(part, { SCARL })
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_Guns = { MP7 = MP7, MP7A2 = MP7A2, P90 = P90, FIVESEVEN = FIVESEVEN, UCP = UCP, SCARL = SCARL,
    SCARH = SCARH, UMP45 = UMP45, UMP9 = UMP9 }
