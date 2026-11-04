--[[
    Guns of Tien - Post-93 -- the Desert Tech MDRx .223 and .308 (user, 2026-11-04) in Gunworks' and Guns of Marz's
    registries: one bullpup chassis (scripts/post93/build_mdr.py), two rifles Desert Tech sold, both semi-automatic
    only, as GoM's AR-15 and M14 (no rate of fire registered: Gunworks fires a semi-automatic gun without one):
    - MDR223: .223 Wylde, 16" barrel, side ejection, black. GoM's STANAG magazines in its own "STANAG" profile (Desert
      Tech ships the .223 with a 30-round PMAG), drawn at our size; GoM's AR muzzle family.
    - MDR308: 7.62 NATO, 20" barrel, forward ejection, flat dark earth. Magpul's SR-25-pattern PMAG LR/SR 10 / 20 / 25
      and the D-50 drum, a magazine profile of their own like GoM's STANAG (nothing else in GoM takes SR-25 magazines,
      and the SCAR-H's are FN's own); the SCAR-H's mount device and SOCOM762-RC (both 5/8x24; their MountOn in the
      item scripts).
    Both reload with GoM's FAMAS reload ("famas_rifle", its other bullpup, as the AUGs and the PS90). Their charging
    handle does not reciprocate: GoM's Bolt swap moves the carrier seen in the right side's window, the main mod's
    ChargingHandle part the handles, only while racked. GoM's optics on the top rail, its foregrips under the
    handguard, lights left and lasers right on its M-LOK sides: four hidden integral rail parts stand in for M-LOK rail
    sections (the PS90's way), shared by both guns. No GoM bipod: the MDRx takes its own handguard bipod (user,
    2026-11-04), so GoM's bipods are left out of the MountOn, the rail rule and the found-gun parts.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")
local ChargingHandle = require("GunsOfTien/ChargingHandle")
local GoMReloads = require("GunsOfTien/GoMReloads")
local HandMagazines = require("GunsOfTien/HandMagazines")
require("GunsOfTienPost93/Guns")             -- the SCAR-H's suppressor rule and stats first

for _, file in ipairs({ "Magazines", "ReloadsAndAnims/ReloadAnims", "AttachmentCustomStats",
    "AttachmentsRequiredParts", "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local MDR223 = M .. "MDR223"
local MDR308 = M .. "MDR308"
local MDRS = { MDR223, MDR308 }
local PMAGS = { M .. "762x51Magazine20_PMAG", M .. "762x51Magazine10_PMAG", M .. "762x51Magazine25_PMAG",
    M .. "762x51Magazine50_PMAG" }
local STANAGS = {}
for _, n in ipairs({ 20, 25, 30, 50, 60, 75, 100, 150 }) do
    STANAGS[#STANAGS + 1] = "MarzGuns.556x45Magazine" .. n .. "_STANAG"
end
local RAIL_UP = M .. "MDR_Integrated_Rail_Up"
local RAIL_DOWN = M .. "MDR_Integrated_Rail_Down"
local RAIL_LEFT = M .. "MDR_Integrated_Rail_Left"
local RAIL_RIGHT = M .. "MDR_Integrated_Rail_Right"

-------------------------------------------------
-- Magazines
-------------------------------------------------
Magazine.RegisterWeaponWithProfile("STANAG", MDR223)          -- GoM's own profile (M16s, M4A1, FNC...)
Magazine.RegisterMagazineProfile("7.62x51mm SR-25", PMAGS)
Magazine.RegisterWeaponWithProfile("7.62x51mm SR-25", MDR308)

-------------------------------------------------
-- GoM's bolt swap (the carrier in the right side's window), the charging handles back only while racked, GoM's
-- FAMAS reload. The .223 draws GoM's STANAGs at its own size, so a STANAG in the off hand (that node fires
-- attachToHand) is the main mod's scaled _Hand item (HandMagazines.lua, as the SCAR-L's); the PMAGs are ours and
-- carry their own Bip01_Prop2.
-------------------------------------------------
local HAND = HandMagazines.mapOf(STANAGS)
HandMagazines.register(MDR223, HAND)
for _, gun in ipairs(MDRS) do
    Animations.RegisterWeaponWithAnimatedParts(gun, ChargingHandle.ANIMATED_PARTS)
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("famas_rifle",
        gun == MDR223 and { partState = { props = HandMagazines.props(HAND) } } or nil))
end

-------------------------------------------------
-- Rails: the four integral rails as parents of GoM's optics, foregrips, lights and lasers (each side takes
-- one kind, GoM's rule); the SOCOM762-RC already needs the SCAR-H's mount device (Guns.lua)
-------------------------------------------------
local OPTICS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope",
    "MarzGuns.Aimpoint_Sight", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight", "MarzGuns.TR06X_Scope",
    "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}
local FOREGRIPS = { "MarzGuns.Stub_Foregrip", "MarzGuns.MKC_Foregrip", "MarzGuns.MK2_Foregrip" }
local LIGHTS = { "MarzGuns.BrightPoint-5_Light", "MarzGuns.SR7_Light" }
local LASERS = { "MarzGuns.AimRight_Laser", "MarzGuns.LRX-7_Laser" }
local AR_MUZZLE = { "MarzGuns.AR_Muzzle_Mount_Device", "MarzGuns.MKI_Suppressor", "MarzGuns.NDR_Suppressor",
    "MarzGuns.LR2_Compensator", "MarzGuns.LX_Flashhider", "MarzGuns.Trix42_Muzzlebreak" }
RequiredAttachment.RegisterRequired(OPTICS, { RAIL_UP })
RequiredAttachment.RegisterRequired(FOREGRIPS, { RAIL_DOWN })
RequiredAttachment.RegisterRequired(LIGHTS, { RAIL_LEFT })
RequiredAttachment.RegisterRequired(LASERS, { RAIL_RIGHT })

local permanent = { RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT }
for _, mag in ipairs(PMAGS) do permanent[#permanent + 1] = mag end
PreventRemoval.Register(permanent)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the SCARs' accessories at GoM's chances; the
-- .223 GoM's M4A1 magazines (20 / 25 / 30 at 30 / 20 / 50), the .308 Magpul's 20 mostly, the 10 and 25 rarely, the
-- D-50 as rarely as the SCAR-H's drum (2%); no bipod
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local COMMON = {
        "MarzGuns.ReflexS2_Sight:5", "MarzGuns.EXPS3_Sight:5", "MarzGuns.EXPS1_Sight:5", "MarzGuns.Aimpoint_Sight:5",
        "MarzGuns.LR4X_Scope:3", "MarzGuns.TA28_Scope:3", "MarzGuns.ElcanX2_Scope:3",
        "MarzGuns.Stub_Foregrip:5", "MarzGuns.MKC_Foregrip:5", "MarzGuns.MK2_Foregrip:3",
        "MarzGuns.AimRight_Laser:3", "MarzGuns.LRX-7_Laser:3",
        "MarzGuns.BrightPoint-5_Light:5", "MarzGuns.SR7_Light:5",
    }
    local function entry(mags, extra)
        local optionals = {}
        for _, list in ipairs({ mags, COMMON, extra }) do
            for _, e in ipairs(list) do optionals[#optionals + 1] = e end
        end
        return {
            required = { "MarzGuns.Bolt_Lock", ChargingHandle.FORWARD, RAIL_UP, RAIL_DOWN, RAIL_LEFT, RAIL_RIGHT },
            optionals = optionals,
        }
    end
    spawnTable[MDR223] = entry({ "MarzGuns.556x45Magazine20_STANAG:30", "MarzGuns.556x45Magazine25_STANAG:20",
        "MarzGuns.556x45Magazine30_STANAG:50" }, { "MarzGuns.AR_Muzzle_Mount_Device:5" })
    spawnTable[MDR308] = entry({ M .. "762x51Magazine20_PMAG:60", M .. "762x51Magazine10_PMAG:10",
        M .. "762x51Magazine25_PMAG:10", M .. "762x51Magazine50_PMAG:2" },
        { "MarzGuns.TR06X_Scope:1", "MarzGuns.LR10X_Scope:1",
          M .. "SCARH_Muzzle_Mount_Device:5" })
end

-------------------------------------------------
-- MountOn appended (DoParam replaces the list, so it is read and written back whole, as Guns.lua does)
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
    for _, list in ipairs({ OPTICS, FOREGRIPS, LIGHTS, LASERS }) do
        for _, part in ipairs(list) do appendMountOn(part, MDRS) end
    end
    for _, list in ipairs({ STANAGS, AR_MUZZLE }) do
        for _, part in ipairs(list) do appendMountOn(part, { MDR223 }) end
    end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

GunsOfTienPost93_MDR = { MDR223 = MDR223, MDR308 = MDR308 }
