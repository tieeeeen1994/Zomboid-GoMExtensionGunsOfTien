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
    with the bolt carrier), GoM's default rifle reload (SCAR-L, as the M4A1) and its FAL clips (SCAR-H), the shared
    side-folding stock with GoM's G36 stock stats, four integral rails as parents of GoM's optics, foregrips,
    bipods, lights and lasers, GoM's AR muzzle parts on the SCAR-L and the SCAR-H's own mount device and suppressor.

    The UMP45 and UMP9 (user, 2026-10-22) are registered as GoM's MP5 is: each with its own magazines (in GoM's .45 ACP
    and 9x19mm families, Ammunition.lua), select fire with H&K's two-round burst, GoM's MP5 reload clips, the shared
    side-folding stock with GoM's G36C stock stats, four integral rails as parents of GoM's MP5 accessories (optics,
    foregrips, lights, lasers). The UMP45 takes GoM's .45 mount device and P45 suppressor, as its MAC-10 does, the
    UMP9 the main mod's 9x19mm SMG mount device and AWC Mk9 (GoM's 9mm cans fit its pistols only). No animated
    charging handle (it does not reciprocate, as the MP5's).

    The Five-seveN is MarzGuns.FIVESEVEN (GoM names it but ships nothing else) and is registered like GoM's Glock 17
    and M92FS: magazine profile, the animated slide, permanent magazines, spawn parts, GoM's pistol parts allowed on
    it. Like GoM's pistols it has no reload animation entry (Gunworks' default handgun reload) and no rate of fire
    (semi-automatic only). The UCP Prototype (GunsOfTienPost93.UCP, H&K's 4.6x30mm pistol) is registered the same way
    and takes the MP7's mount device and Rotex-II suppressor.
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
-- No animated bolt: on both the MP7 and the P90 the charging handle does not move when firing (the bolt inside
-- does), so neither is registered with Animations (GoM swaps Bolt_Fired / Bolt_Lock on each shot for guns whose
-- handle reciprocates). The handle model is drawn through the Bolt_Lock part (required at spawn).
-------------------------------------------------

-------------------------------------------------
-- Reload animations. Both guns are held like a pistol. The MP7's magazine goes up into the pistol grip, so it uses
-- vanilla's pistol clips (AnimSets MP7A1_*: Bob_Reload_Handgun_Load, its reverse baked into
-- anims_X/Bob/Bob_GunsOfTien_MP7_Unload, Bob_Reload_Handgun_Rack with GoM's rack events); the P90 its own
-- top-loading clips (AnimSets P90TR_*, clips anims_X/Bob/Bob_GunsOfTien_P90_*). A reload ends on its clip's events
-- (loadFinished...): without the clips the magazine insert waits forever (seen in game, 2026-10-15). Both use
-- Gunworks' "attachments" style so the magazine leaves the gun with the hand: the AnimSets' changeWeaponPart "mag"
-- events detach the magazine part (looks only) as the left hand leaves the gun in the unload, and put it back as the
-- new one is pressed home; the real unload / insert still happen at the clips' ends. Durations = the clips' lengths.
-------------------------------------------------
-- both MP7s: the compact SMG stance's reload (CompactStance.lua; clips GunsOfTien_CompactMP7_Reload* in the stance's
-- packs, from scripts/anim/smg_reload.py's compact_mp7: the magazine carried in the left hand, which is shaped round it,
-- the T handle pulled with the muzzle turned up and right); each gets its own table, as pointMagPart rewrites its spec.
-- Held in one hand (the main mod's OneHand.lua), drawn with their one-hand models (MP7A1_1H / MP7A2_1H, without the
-- stance's turn), they play the old pistol clips: animId "MP7A1", no magazine in the left hand.
local OneHand = require("GunsOfTien/OneHand")
for _, gun in ipairs(MP7S) do
    ReloadAnim.RegisterWeapon(gun, {
        animId = "GunsOfTienCompactMP7",
        style = "attachments",
        magItem = MP7_MAGS[1],
        attachments = { magPart = { itemType = MP7_MAGS[1], partType = "Clip" } },
        durations = { unload = 1.2, load = 1.5, rack = 1.2 },
    })
    OneHand.register(gun, gun, gun .. "_1H", {
        animId = "MP7A1",
        style = "attachments",
        magItem = MP7_MAGS[1],
        attachments = { magPart = { itemType = MP7_MAGS[1], partType = "Clip" } },
        durations = { unload = 1.5, load = 1.5, rack = 1.33 },
    })
end
ReloadAnim.RegisterWeapon(P90, {
    animId = "P90TR",
    style = "attachments",
    magItem = M .. "57x28Magazine50_P90",
    attachments = { magPart = { itemType = M .. "57x28Magazine50_P90", partType = "Clip" } },
    durations = { unload = 1.4, load = 1.8, rack = 1.2 },
})
-- SCAR-H: GoM's FAL clips (its magazineProfile("FAL")); the SCAR-L has no entry, as GoM's M4A1 (Gunworks' default)
ReloadAnim.RegisterWeapon(SCARH, {
    animId = "FAL",
    style = "none",
    durations = { unload = 1.2, load = 1.5, rack = 1.2 },
})
-- the UMPs: their own clips since they were resized (2026-10-26; GoM's MP5 clips, which they used before, reached
-- ~2 cm ahead of the smaller well and handle): scripts/anim/smg_reload.py `ump`, starting and ending in the UMPs' own
-- rifle idle and aim (rifle_hand.py), packed with them (GunsOfTien_CompactUMP_Pack*.x), nodes
-- *GunsOfTienCompactUMP_GoT.xml; Gunworks' "attachments" style, the magazine leaving the gun with the hand as on the
-- compact stance (user, 2026-10-26: "i like what we did for UMP. let's do it"). Each gets its own table, as
-- pointMagPart rewrites its spec.
for gun, mags in pairs({ [UMP45] = UMP45_MAGS, [UMP9] = UMP9_MAGS }) do
    ReloadAnim.RegisterWeapon(gun, {
        animId = "GunsOfTienCompactUMP",
        style = "attachments",
        magItem = mags[1],
        attachments = { magPart = { itemType = mags[1], partType = "Clip" } },
        durations = { unload = 1.2, load = 1.5, rack = 1.2 },
    })
end
-- The UMPs' left hand: vanilla's rifle clips hold the palm ~0.22 ahead of the grip, an M16's handguard, which the
-- UMPs (resized to the M16A2's proportion, 2026-10-26) no longer reach. scripts/anim/rifle_hand.py builds every rifle
-- clip in which the left hand holds the gun with the palm moved back along the gun to the handguard (anims_X/Bob
-- GunsOfTien_CompactUMP_Pack*.x, AnimSets *_GoTCompactUMP.xml), played through Gunworks' grip registry as the compact
-- stance is; the rest of the rifle hold is vanilla's.
local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")
local function registerUmpGrip()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        return
    end
    for _, gun in ipairs(UMPS) do
        Gunworks.RegisterWeapon(gun, { grip = { animId = "GunsOfTien_CompactUMP" } })
    end
end
Events.OnGameBoot.Add(registerUmpGrip)
local NO_HAND_MAGAZINE = { MP7A1 = true, P90TR = true }
-- The magazine only leaves the gun / comes back at those events: no magazine shown in the left hand (user,
-- 2026-10-15). The attachments style shows Gunworks' reload magazine there (the eject's changeWeaponPart and the
-- insert's start, both through ReloadAnim.attachReloadMagazine, looked up on the shared table at call time), so that
-- one call is skipped for our guns; detachReloadMagazine then has nothing to remove.
pcall(require, "WeaponSystems/ReloadAnim/Visuals")
local attachReloadMagazine = ReloadAnim.attachReloadMagazine
if attachReloadMagazine then
    ReloadAnim.attachReloadMagazine = function(action, handler)
        if handler and NO_HAND_MAGAZINE[handler.animId] then
            return
        end
        return attachReloadMagazine(action, handler)
    end
end
-- The magazine part spec names one item type, and Gunworks only detaches a part of that type and attaches that type
-- (Visuals.detachWeaponPartSpec / attachWeaponPartSpec). The MP7 takes four (20 / 30 / 40, the 60 drum), so before
-- each swap the spec is pointed at the magazine involved: ReloadAnim.resolveReloadMagItem = the one being inserted, the one on the gun when the
-- eject started (_actualMagType), or the gun's saved MagazineType.
local resolveReloadMagItem = ReloadAnim.resolveReloadMagItem
local function pointMagPart(action, handler)
    if not (resolveReloadMagItem and action and handler and handler.parts
            and (handler.animId == "MP7A1" or handler.animId == "GunsOfTienCompactMP7"
                or handler.animId == "GunsOfTienCompactUMP")) then
        return
    end
    local spec = handler.parts.mag
    local magType = resolveReloadMagItem(action, handler)
    if spec and magType and magType ~= "" then
        spec.itemType = magType
    end
end
for _, name in ipairs({ "handleWeaponPartAnimEvent", "setWeaponAttachmentState" }) do
    local original = ReloadAnim[name]
    if original then
        ReloadAnim[name] = function(action, handler, ...)
            pointMagPart(action, handler)
            return original(action, handler, ...)
        end
    end
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
