--[[
    Guns of Tien - Post-93 -- the Steyr AUG A3, AUG Para and AUG HBAR (docs/post93_design.md; user, 2026-10-28) in
    Gunworks' and Guns of Marz's registries.

    Three guns on the A3 receiver (the A1's cast scope and handle replaced by a Picatinny rail), registered as the main
    mod registers its AUG A1 (shared/GunsOfTien/AUG.lua):
    - magazines: the A3 the A1's own 30 / 42 (the standard stock: the main mod's "5.56x45mm AUG" profile, their MountOn
      appended); the Para Steyr's straight 25 / 32 9mm in GoM's 9x19mm family; the HBAR Steyr's 7.62x39mm 30 and our
      50-round extended box in GoM's 7.62x39mm family;
    - rate of fire by each gun's real one (A3 700, the A1's; Para 685 from 650-720; HBAR 680, the HBAR's), spread
      balanced on it (docs/post93_design.md, "Stats");
    - the charging handle rides with the bolt (GoM's Bolt_Fired / Bolt_Lock swap), as on the A1;
    - held with vanilla's rifle clips and reloaded with GoM's FAMAS reload, as the A1 (the main mod's GoMReloads.lua);
    - the folding grip: the A1's two parts and their stats (the main mod's AUG.lua), folded through the main mod's
      Foregrip.lua (the Para draws them with its own sand model);
    - rails: integral top (GoM's optics) and right (GoM's lasers), hidden parts as on the SCARs and UMPs; no factory
      left rail: GoM's own Picatinny_Rail_Left (and its universal Picatinny Rail on the left side only) as an optional
      upgrade for GoM's lights, drawn on these guns with our short AUG_RAIL_LEFT; no bottom rail (the folding grip);
    - muzzle: the A3 GoM's AR family (as the SCAR-L), the Para the main mod's 9x19mm SMG mount device and Mk9 (as the
      UMP9), the HBAR none;
    - the HBAR's integrated folding bipod (Gunworks' FoldingBipod, as the main mod's M249 and GoM's BAR / M60 / M24)
      with GoM's rail bipod stats.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingBipod = require("WeaponSystems/Utils/FoldingBipod")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local UniversalAttachment = require("WeaponSystems/Utils/UniversalAttachment")
local Foregrip = require("GunsOfTien/Foregrip")
local GoMReloads = require("GunsOfTien/GoMReloads")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadAnims", "Bipods", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments", "UniversalAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local A3 = M .. "AUGA3"
local PARA = M .. "AUGPARA"
local HBAR = M .. "AUGHBAR"
local GUNS = { A3, PARA, HBAR }
local A1_MAGS = { "GunsOfTien.556x45Magazine30_AUG", "GunsOfTien.556x45Magazine42_AUG" }
local PARA_MAGS = { M .. "9x19Magazine25_AUG", M .. "9x19Magazine32_AUG" }
local HBAR_MAGS = { M .. "762x39Magazine30_AUG", M .. "762x39Magazine50_AUG" }
local GRIP_FOLDED = "GunsOfTien.AUG_Integrated_Foregrip_Folded"
local GRIP_DEPLOYED = "GunsOfTien.AUG_Integrated_Foregrip_Deployed"
local RAIL_UP = M .. "AUG_Integrated_Rail_Up"
local RAIL_RIGHT = M .. "AUG_Integrated_Rail_Right"
local BIPOD_FOLDED = M .. "AUGHBAR_Integrated_Bipod_Folded"
local BIPOD_DEPLOYED = M .. "AUGHBAR_Integrated_Bipod_Deployed"

-------------------------------------------------
-- Magazines
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("5.56x45mm AUG", A3)          -- the main mod's profile (the A1's 30 / 42)
Magazine.RegisterMagazineProfile("9x19mm AUG Para", PARA_MAGS)
Magazine.RegisterWeaponWithProfile("9x19mm AUG Para", PARA)
Magazine.RegisterMagazineProfile("7.62x39mm AUG", HBAR_MAGS)
Magazine.RegisterWeaponWithProfile("7.62x39mm AUG", HBAR)
Ammo.RegisterMultipleItemsWithFamilies({ ["9x19mm"] = PARA_MAGS, ["7.62x39mm"] = HBAR_MAGS })

-------------------------------------------------
-- Rate of fire by the real one (the grip unfolded steadies it: the main mod registers that part's modifier)
-------------------------------------------------
RateOfFire.RegisterWeapon(A3, { rpm = 700, enableSpread = true, sustainedSpread = 0.12, maxSpread = 2.5 })
RateOfFire.RegisterWeapon(PARA, { rpm = 685, enableSpread = true, sustainedSpread = 0.09, maxSpread = 1.4 })
RateOfFire.RegisterWeapon(HBAR, { rpm = 680, enableSpread = true, sustainedSpread = 0.2, maxSpread = 2.8 })
-- the HBAR's bipod deployed steadies it as GoM's rail bipod does (its RPM.lua)
RateOfFire.RegisterSpreadPartModifier(BIPOD_DEPLOYED, { sustainedSpreadMult = 0.65, maxSpreadMult = 0.65 })

-------------------------------------------------
-- The charging handle, GoM's FAMAS reload, the folding grip
-------------------------------------------------
for _, gun in ipairs(GUNS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("famas_rifle"))
    Foregrip.Register(gun, {
        folded = GRIP_FOLDED,
        deployed = GRIP_DEPLOYED,
        foldDesc = "IGUI_GunsOfTien_AUGFoldForegripDesc",
        unfoldDesc = "IGUI_GunsOfTien_AUGUnfoldForegripDesc",
    })
end

-------------------------------------------------
-- The HBAR's integrated bipod: GoM's rail bipod stats (a 4.9 kg rifle, not the M60's or M249's weight)
-------------------------------------------------
FoldingBipod.RegisterWeapon(HBAR, {
    attachments = { partType = "BipodIntegrated", folded = BIPOD_FOLDED, deployed = BIPOD_DEPLOYED },
    initialState = "folded",
})
CSA.RegisterMultipleParts({
    [BIPOD_DEPLOYED] = {
        SF.Multiply("AimingTime", 1.1),
        SF.Multiply("CriticalChance", 1.15),
        SF.Multiply("HitChance", 1.15),
    },
    [BIPOD_FOLDED] = {},
    [RAIL_UP] = {},
    [RAIL_RIGHT] = {},
})

-------------------------------------------------
-- Rails: the integral top and right rails as parents of GoM's optics and lasers; GoM's own rule already makes its
-- lights need Picatinny_Rail_Left. The universal Picatinny Rail offers the left side only on these guns.
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })
local universal = {}
for _, gun in ipairs(GUNS) do
    universal[gun] = { ["MarzGuns.Picatinny_Rail"] = { "MarzGuns.Picatinny_Rail_Left" } }
end
UniversalAttachment.RegisterWeapons(universal)

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
local permanent = { RAIL_UP, RAIL_RIGHT }
for _, list in ipairs({ PARA_MAGS, HBAR_MAGS }) do
    for _, part in ipairs(list) do permanent[#permanent + 1] = part end
end
PreventRemoval.Register(permanent)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the handle, the grip folded, the rails, the
-- HBAR's bipod folded; magazines by GoM's rule (the standard one likeliest, the longer one rarely: the A1's 42 at 5);
-- GoM's optics and lasers at its rifles' chances, lights with GoM's left rail (":PRL", drawn as ours)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local COMMON = {
        "MarzGuns.ReflexS2_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.EXPS1_Sight:5", "MarzGuns.Aimpoint_Sight:5",
        "MarzGuns.LR4X_Scope:3", "MarzGuns.TA28_Scope:3", "MarzGuns.ElcanX2_Scope:3",
        "MarzGuns.AimRight_Laser:3", "MarzGuns.LRX-7_Laser:3",
        "MarzGuns.BrightPoint-5_Light:2:PRL", "MarzGuns.SR7_Light:2:PRL",
    }
    local function entry(mags, extra, required)
        local optionals = {}
        for _, list in ipairs({ mags, COMMON, extra }) do
            for _, e in ipairs(list) do optionals[#optionals + 1] = e end
        end
        local req = { "MarzGuns.Bolt_Lock", GRIP_FOLDED, RAIL_UP, RAIL_RIGHT }
        for _, e in ipairs(required or {}) do req[#req + 1] = e end
        return { required = req, optionals = optionals }
    end
    spawnTable[A3] = entry({ A1_MAGS[1] .. ":30", A1_MAGS[2] .. ":5" }, { "MarzGuns.AR_Muzzle_Mount_Device:5" })
    spawnTable[PARA] = entry({ PARA_MAGS[1] .. ":30", PARA_MAGS[2] .. ":20" },
        { "GunsOfTien.SMG9_Muzzle_Mount_Device:5" })
    spawnTable[HBAR] = entry({ HBAR_MAGS[1] .. ":50", HBAR_MAGS[2] .. ":5" }, {}, { BIPOD_FOLDED })
end

-------------------------------------------------
-- Parts allowed on these guns: append to their MountOn (DoParam replaces the list, so it is read and written back)
-------------------------------------------------
local function appendMountOn(partType, guns)
    local script = ScriptManager.instance:getItem(partType)
    if not script then return end
    local item = instanceItem(partType)
    local current = item and item.getMountOn and item:getMountOn()
    local list, seen = {}, {}
    if current then
        for i = 0, current:size() - 1 do
            local e = tostring(current:get(i))
            if not seen[e] then
                seen[e] = true
                list[#list + 1] = e
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

local function appendAll()
    for _, list in ipairs({ OPTICS, LIGHTS, LASERS, { "MarzGuns.Picatinny_Rail_Left" } }) do
        for _, part in ipairs(list) do appendMountOn(part, GUNS) end
    end
    for _, part in ipairs(A1_MAGS) do appendMountOn(part, { A3 }) end
    for _, part in ipairs({ "MarzGuns.AR_Muzzle_Mount_Device", "MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor",
        "MarzGuns.LR2_Compensator", "MarzGuns.LX_Flashhider", "MarzGuns.Trix42_Muzzlebreak" }) do
        appendMountOn(part, { A3 })
    end
    for _, part in ipairs({ "GunsOfTien.SMG9_Muzzle_Mount_Device", "GunsOfTien.Mk9_Suppressor" }) do
        appendMountOn(part, { PARA })
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_AUG = { A3 = A3, PARA = PARA, HBAR = HBAR, PARA_MAGS = PARA_MAGS, HBAR_MAGS = HBAR_MAGS,
    BIPOD_FOLDED = BIPOD_FOLDED, BIPOD_DEPLOYED = BIPOD_DEPLOYED }
