--[[
    Guns of Tien - Post-93 -- KBP's 9A-91 and VSK-94 (user, 2026-11-24; docs/post93_design.md "9A-91 and VSK-94") in
    Gunworks' and Guns of Marz's registries.

    The 9A-91 compact assault rifle (made from 1994, MVD police) as current production guns are, and its 1995 sniper
    version VSK-94 on the same receiver (scripts/post93/build_9a91.py; items_a91.txt), both 9x39mm:
    - their own 20-round steel magazine (sources agree it is not the AS VAL's), a profile of its own in GoM's
      "9x39mm" ammunition family, so GoM's SP-5 and the main mod's SP-6 load into it;
    - Auto / Single at 700 rpm (the 9A-91's 600-800, the VSK-94's 700); the 9A-91 lighter and livelier than GoM's AS
      VAL, the VSK-94 steadier on its stock;
    - the bolt carrier with its handle on the right moves on each shot (GoM's AK bolt swap), closing on an empty
      chamber as an AK does (the main mod's RPK.lua wrapper, as the Grozas);
    - reload: GoM's AK reload ("ak_rifle", as its AKS-74U and AS VAL), our magazine in the off hand (its own model
      and Bip01_Prop2, at the guns' size);
    - the 9A-91's stock folds over the receiver (Gunworks' folding stock, GoM's AKS-74U stock stats and spread when
      deployed); the VSK-94's skeleton stock is the body;
    - GoM's AK side mount on the left dovetail rail (both real guns carry their optics there) and every GoM optic on
      it, appended to their MountOn as the SVU does;
    - the detachable can on the threaded barrel (the VSK-94's is not integral, unlike the VSS's), behind the 9x39mm
      mount device, GoM's way: GoM's PBS-1 stats (sound and volume x0.3, damage x0.9, no flash, its shot), worn and
      repaired as GoM's PBS-1 (AttachmentsDurability, fixing_guns.txt);
    - a found gun: the bolt (and the 9A-91's stock folded), its magazine at GoM's AS VAL chance, now and then GoM's
      optics with the AK mount (":AM", the SVU's and GoM's AK chances; the VSK-94 mostly its PSO-1). No can and no
      mount device: GoM's found guns never come with one.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local Animations = require("WeaponSystems/Utils/Animations")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local RequiredAttachment = require("WeaponSystems/Utils/RequiredAttachment")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local GoMReloads = require("GunsOfTien/GoMReloads")
require("GunsOfTien/RPK")                    -- the AK bolt wrapper (GunsOfTien_RPK.CLOSES_ON_EMPTY)

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "Stocks", "ReloadsAndAnims/ReloadAnims",
    "ReloadsAndAnims/AnimationsFiring", "AttachmentCustomStats", "AttachmentsRequiredParts", "PermanentAttachments",
    "AttachmentsDurability" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local A91 = M .. "A91"
local VSK94 = M .. "VSK94"
local GUNS = { A91, VSK94 }
local MAG = M .. "9x39Magazine20_A91"
local CAN = M .. "A91_Suppressor"
local MOUNT = M .. "A91_Muzzle_Mount_Device"
local FOLDED = M .. "A91_Integrated_Stock_Folded"
local DEPLOYED = M .. "A91_Integrated_Stock_Deployed"

-------------------------------------------------
-- Magazine
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x39mm 9A-91", { MAG })
for _, gun in ipairs(GUNS) do Magazine.RegisterWeaponWithProfile("9x39mm 9A-91", gun) end
Ammo.RegisterMultipleItemsWithFamilies({ ["9x39mm"] = { MAG } })

-------------------------------------------------
-- Rate of fire (GoM's AS VAL 900, 0.12 / 3.0; AKS-74U 650, 0.25 / 3.5)
-------------------------------------------------
RateOfFire.RegisterWeapon(A91, { rpm = 700, enableSpread = true, sustainedSpread = 0.18, maxSpread = 3.3 })
RateOfFire.RegisterWeapon(VSK94, { rpm = 700, enableSpread = true, sustainedSpread = 0.12, maxSpread = 2.8 })

-------------------------------------------------
-- The bolt (GoM's AK bolt swap, closing on the empty chamber) and the reload (GoM's AK reload)
-------------------------------------------------
local closes = GunsOfTien_RPK and GunsOfTien_RPK.CLOSES_ON_EMPTY
for _, gun in ipairs(GUNS) do
    if closes then closes[gun] = true end
    Animations.RegisterWeaponWithAnimatedParts(gun, {
        SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
        cycleTicks = 3,
    })
    ReloadAnim.RegisterWeapon(gun, GoMReloads.profile("ak_rifle"))
end

-------------------------------------------------
-- The 9A-91's folding stock (GoM's AKS-74U stock: flat values since GoM's November 2026 update, and its spread)
-------------------------------------------------
FoldingStock.RegisterWeapon(A91, {
    attachments = { partType = "StockIntegrated", folded = FOLDED, deployed = DEPLOYED },
    initialState = "folded",
})
RateOfFire.RegisterSpreadPartModifier(DEPLOYED, { sustainedSpreadMult = 0.75, maxSpreadMult = 0.85 })

-------------------------------------------------
-- Stats: the stock, and the can (GoM's PBS-1, its rifle cans' shot)
-------------------------------------------------
CSA.RegisterMultipleParts({
    [FOLDED] = {},
    [DEPLOYED] = {
        SF.Adjust("HitChance", 8),
        SF.Adjust("AimingTime", -4),
    },
    [CAN] = {
        SF.Multiply("SoundRadius", 0.3),
        SF.Multiply("SoundVolume", 0.3),
        SF.Multiply("MaxDamage", 0.9),
        SF.Multiply("MinDamage", 0.9),
        SF.Set("SwingSound", "CapGunRevolverShoot"),
        SF.Set("MuzzleFlashModelKey", nil),
    },
    [MOUNT] = {},
})
RequiredAttachment.RegisterRequired({ CAN }, { MOUNT })
require("WeaponSystems/Utils/AttachmentsDurability").RegisterAttachment({ CAN })
PreventRemoval.Register({ MAG })

-------------------------------------------------
-- GoM's AK side mount and its optics: appended to their MountOn (DoParam replaces the list, so it is read and
-- written back whole, as SVU.lua does); GoM's own rule puts the optics on the mount
-------------------------------------------------
local OPTICS = { "EXPS1_Sight", "EXPS3_Sight", "ElcanX2_Scope", "LR10X_Scope", "Aimpoint_Sight", "TA28_Scope",
    "LR4X_Scope", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "Kobra_Sight", "TR06X_Scope", "PSO1_Scope",
    "LRX12X_Scope" }
local PARTS = { "MarzGuns.AK_Mount" }
for _, o in ipairs(OPTICS) do PARTS[#PARTS + 1] = "MarzGuns." .. o end

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

local function appendAll()
    for _, part in ipairs(PARTS) do appendMountOn(part, GUNS) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local function optionals(redDot, low, high)
        local out = { MAG .. ":50" }
        for _, o in ipairs({ "Kobra_Sight", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "EXPS3_Sight",
            "EXPS1_Sight", "Aimpoint_Sight" }) do out[#out + 1] = "MarzGuns." .. o .. ":" .. redDot .. ":AM" end
        for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope" }) do
            out[#out + 1] = "MarzGuns." .. o .. ":" .. low .. ":AM"
        end
        for _, o in ipairs({ "TR06X_Scope", "LR10X_Scope", "LRX12X_Scope" }) do
            out[#out + 1] = "MarzGuns." .. o .. ":1:AM"
        end
        return out
    end
    local a91 = optionals(3, 1)
    a91[#a91 + 1] = "MarzGuns.PSO1_Scope:1:AM"
    local vsk = optionals(1, 3)
    vsk[#vsk + 1] = "MarzGuns.PSO1_Scope:15:AM"      -- the VSK-94's own scope
    spawnTable[A91] = { required = { "MarzGuns.Bolt_Lock", FOLDED }, optionals = a91 }
    spawnTable[VSK94] = { required = { "MarzGuns.Bolt_Lock" }, optionals = vsk }
end

GunsOfTienPost93_A91 = { GUNS = GUNS, MAG = MAG, CAN = CAN, MOUNT = MOUNT, FOLDED = FOLDED, DEPLOYED = DEPLOYED }
