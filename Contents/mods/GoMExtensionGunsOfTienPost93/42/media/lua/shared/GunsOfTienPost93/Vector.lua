--[[
    Guns of Tien - Post-93 -- the KRISS Vector .45 and 9mm (user, 2026-10-30) in Gunworks' and Guns of Marz's
    registries, registered as the UMPs are (Guns.lua):
    - Glock's magazines, which KRISS built the Vector's well around: the .45 takes the main mod's Glock 21 13 (its
      ".45 ACP Glock 21" profile, Glock21.lua) and KRISS's MagEx2 30, the 9mm GoM's Glock 17 17, Glock's 33 and
      KRISS's MagEx2 40 (a "9x19mm Glock" profile of our own, for GoM's Glock 17 too, which has none). Our three fit
      the pistols as well: they join the profiles, and the pistols draw them through ModelWeaponPart lines added here
      (pistol-space copies of the pistols' own magazine meshes, build_vector.py);
    - about 1200 rpm, select fire with KRISS's two-round burst, spreading less than any other SMG here (the Super V
      recoil system);
    - the .45 held as a rifle with GoM's MP5 reload (the well ahead of the trigger, the handle front left, as on the
      MP5); the 9mm held like a pistol (user, 2026-11-01) with its MP5K's ("handgun2"), as the MP7s and the P90; the
      bolt swap in the ejection port and the main mod's charging handle (back only while racked);
    - the side-folding stock with GoM's G36C stock stats (as the UMPs');
    - GoM's optics on the integral top rail, its foregrips on the integral bottom rail, its optional left and right
      Picatinny rails (drawn as KRISS's side rails) for its lights and lasers (the main mod's Rails.Register);
    - at canon the .45 GoM's .45 mount device and P45, the 9mm the main mod's 9x19mm SMG mount device and Mk9.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")
local Rails = require("GunsOfTien/Rails")
local GoMReloads = require("GunsOfTien/GoMReloads")
require("GunsOfTien/Glock21")                -- its profile first: the .45 joins it

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadAnims", "Stocks", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local VECTOR45 = M .. "VECTOR45"
local VECTOR9 = M .. "VECTOR9"
local VECTORS = { VECTOR45, VECTOR9 }
local GLOCK21 = "GunsOfTien.GLOCK21"
local GLOCK17 = "MarzGuns.GLOCK17"
local GLOCK21_13 = "GunsOfTien.45Magazine13_GLOCK21"
local GLOCK17_17 = "MarzGuns.9x19Magazine17_GLOCK"
local MAG45_30 = M .. "45Magazine30_GLOCK21"
local MAG9_33 = M .. "9x19Magazine33_GLOCK"
local MAG9_40 = M .. "9x19Magazine40_GLOCK"
local OWN_MAGS = { MAG45_30, MAG9_33, MAG9_40 }
local STOCK_FOLDED = M .. "VECTOR_Integrated_Stock_Folded"
local STOCK_DEPLOYED = M .. "VECTOR_Integrated_Stock_Deployed"
local RAIL_UP = M .. "VECTOR_Integrated_Rail_Up"
local RAIL_DOWN = M .. "VECTOR_Integrated_Rail_Down"

-------------------------------------------------
-- Magazines: Glock's, shared with the pistols
-------------------------------------------------
Magazine.RegisterMagazineProfile(".45 ACP Glock 21", { MAG45_30 })        -- appended to the main mod's
Magazine.RegisterWeaponWithProfile(".45 ACP Glock 21", VECTOR45)
Magazine.RegisterMagazineProfile("9x19mm Glock", { GLOCK17_17, MAG9_33, MAG9_40 })
Magazine.RegisterWeaponWithProfile("9x19mm Glock", GLOCK17)
Magazine.RegisterWeaponWithProfile("9x19mm Glock", VECTOR9)
Ammo.RegisterMultipleItemsWithFamilies({ [".45 ACP"] = { MAG45_30 }, ["9x19mm"] = { MAG9_33, MAG9_40 } })

-------------------------------------------------
-- Rate of fire: 1200 rpm with KRISS's two-round burst (GoM's MAC-10 1000); the Super V keeps the muzzle down, so
-- both spread less than the UMPs (0.18 / 2.2, 0.11 / 1.6) and the MP7 (0.08 / 1.3)
-------------------------------------------------
RateOfFire.RegisterWeapon(VECTOR45, { rpm = 1200, burstCount = 2, enableSpread = true, sustainedSpread = 0.10,
    maxSpread = 1.3 })
RateOfFire.RegisterWeapon(VECTOR9, { rpm = 1200, burstCount = 2, enableSpread = true, sustainedSpread = 0.08,
    maxSpread = 1.1 })
-- the stock unfolded steadies automatic fire as GoM's G36C stock does (its RPM.lua; the UMPs' too)
RateOfFire.RegisterSpreadPartModifier(STOCK_DEPLOYED, { sustainedSpreadMult = 0.75, maxSpreadMult = 0.85 })

-------------------------------------------------
-- The bolt in the port (GoM's swap) and the charging handle (back only while racked), GoM's reloads: the .45 its
-- MP5's, the pistol-held 9mm its MP5K's
-------------------------------------------------
for _, gun in ipairs(VECTORS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ChargingHandle.Register(gun)
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile(gun == VECTOR9 and "handgun2" or "MP5"))
    FoldingStock.RegisterWeapon(gun, {
        attachments = { partType = "StockIntegrated", folded = STOCK_FOLDED, deployed = STOCK_DEPLOYED },
        initialState = "folded",
    })
end

-- the stock deployed: GoM's G36C stock (another side-folding polymer stock on a short gun, as the UMPs')
CSA.RegisterMultipleParts({
    [STOCK_FOLDED] = {},
    [STOCK_DEPLOYED] = {
        SF.Multiply("HitChance", 1.15),
        SF.Multiply("AimingTime", 0.75),
    },
})

-------------------------------------------------
-- Rails: the integral top and bottom rails as parents of GoM's optics and foregrips; GoM's optional left and right
-- rails (KRISS's bolt-on side rails) for its lights and lasers, GoM's own rule tying them to those sides
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
for _, gun in ipairs(VECTORS) do
    Rails.Register(gun, { sides = { "Left", "Right" }, lights = true, lasers = true })
end

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register({ RAIL_UP, RAIL_DOWN, MAG45_30, MAG9_33, MAG9_40 })

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table), as the UMPs come: the stock folded, the
-- standard magazine at 50 (GoM's one-magazine guns), the long ones rarely; GoM's MP5 accessories at its chances,
-- lights and lasers with their side rail (":PRL" / ":PRR", drawn as KRISS's)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local COMMON = {
        "MarzGuns.EXPS1_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.Aimpoint_Sight:5", "MarzGuns.ReflexS2_Sight:5",
        "MarzGuns.Stub_Foregrip:10", "MarzGuns.MKC_Foregrip:10", "MarzGuns.MK2_Foregrip:5",
        "MarzGuns.AimRight_Laser:5:PRR", "MarzGuns.LRX-7_Laser:5:PRR",
        "MarzGuns.BrightPoint-5_Light:10:PRL", "MarzGuns.SR7_Light:10:PRL",
    }
    local function entry(mags)
        local optionals = {}
        for _, list in ipairs({ mags, COMMON }) do
            for _, e in ipairs(list) do optionals[#optionals + 1] = e end
        end
        return {
            required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD, STOCK_FOLDED, RAIL_UP, RAIL_DOWN },
            optionals = optionals,
        }
    end
    spawnTable[VECTOR45] = entry({ GLOCK21_13 .. ":50", MAG45_30 .. ":5" })
    spawnTable[VECTOR9] = entry({ GLOCK17_17 .. ":50", MAG9_33 .. ":5", MAG9_40 .. ":2" })
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as Guns.lua does), and the
-- pistols' ModelWeaponPart lines for our magazines (DoParam adds one line per call: once per script object, which
-- leaving a game replaces)
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

local PISTOL_PARTS = {
    [GLOCK21] = { M .. "45Magazine30_GLOCK21 " .. M .. "45Magazine30_GLOCK21 magazine magazine" },
    [GLOCK17] = { M .. "9x19Magazine33_GLOCK " .. M .. "9x19Magazine33_GLOCK17 magazine magazine",
        M .. "9x19Magazine40_GLOCK " .. M .. "9x19Magazine40_GLOCK17 magazine magazine" },
}
local partsAddedTo = {}             -- item script -> true

local function appendAll()
    for _, list in ipairs({ OPTICS, FOREGRIPS }) do
        for _, part in ipairs(list) do appendMountOn(part, VECTORS) end
    end
    for _, part in ipairs({ "MarzGuns.45_Muzzle_Mount_Device", "MarzGuns.P45_Suppressor", GLOCK21_13 }) do
        appendMountOn(part, { VECTOR45 })
    end
    for _, part in ipairs({ "GunsOfTien.SMG9_Muzzle_Mount_Device", "GunsOfTien.Mk9_Suppressor", GLOCK17_17 }) do
        appendMountOn(part, { VECTOR9 })
    end
    for pistol, lines in pairs(PISTOL_PARTS) do
        local script = ScriptManager.instance:getItem(pistol)
        if script and not partsAddedTo[script] then
            partsAddedTo[script] = true
            for _, line in ipairs(lines) do script:DoParam("ModelWeaponPart = " .. line) end
        end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_Vector = { VECTOR45 = VECTOR45, VECTOR9 = VECTOR9, MAGS = OWN_MAGS }
