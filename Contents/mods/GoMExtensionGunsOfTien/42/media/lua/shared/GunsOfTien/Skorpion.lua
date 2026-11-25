--[[
    Guns of Tien -- the Skorpion vz. 82 (docs/design.md 4s; user, 2026-11-26: "For makarov guns, let's add Skorpion
    and Kedr") in Gunworks' and Guns of Marz's registries.

    The Czechoslovak army's Skorpion in 9x18mm Makarov (Samopal vz. 82, the vz. 61 rebuilt for the Soviet pistol
    round), registered as GoM registers its MP5K / MAC-10 and as the Micro Uzi and the TMP: held like a pistol and
    holstered (items_skorpion.txt):
    - its own magazine profile, "9x18mm Skorpion", with the straight steel magazines of 12, 24 and 30 rounds, in the
      main mod's "9x18mm" family (the plain round; Post-93 adds later loads to the family);
    - about 850 rpm (the rate reducer in the grip holds the little bolt back between shots), select fire Auto /
      Single; steadier than the Uzis and the TMP: 0.15 / 1.9;
    - the bolt lies under the ejection port in the top of the receiver with a cocking knob on each side: all of it
      is the gun's Bolt part on GoM's swap (back on each shot and held open on an empty gun, which the real bolt
      catch does too), no ChargingHandle part, as the PPSh-41;
    - reload: GoM's own animations (GoMReloads.lua), its MP5K's ("handgun2");
    - the wire stock folded over the top or swung open (Gunworks' FoldingStock, the parts in items_skorpion.txt, each
      state its own node drawn in place), with GoM's MAC-10 stock stats as the Mini and Micro Uzi, folded on a found
      gun;
    - no muzzle parts (no muzzle family in 9x18mm; the Czech suppressor was never exported), no rails, no bayonet.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local RateOfFire = require("WeaponSystems/Utils/RateOfFire")
local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
local FoldingStock = require("WeaponSystems/Utils/FoldingStock")
local CSA = require("WeaponSystems/Utils/CustomStatsAttachments")
local SF = require("WeaponSystems/Utils/StatsFactory")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")
local Animations = require("WeaponSystems/Utils/Animations")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims", "Stocks", "AttachmentCustomStats",
    "PermanentAttachments", "ReloadsAndAnims/AnimationsFiring" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local SKORPION = M .. "SKORPION"
local MAGS = { M .. "9x18Magazine12_SKORPION", M .. "9x18Magazine24_SKORPION", M .. "9x18Magazine30_SKORPION" }
local FOLDED, DEPLOYED = M .. "SKORPION_Integrated_Stock_Folded", M .. "SKORPION_Integrated_Stock_Deployed"

-------------------------------------------------
-- Magazines: the Skorpion's own profile, in the main mod's 9x18mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x18mm Skorpion", MAGS)
Magazine.RegisterWeaponWithProfile("9x18mm Skorpion", SKORPION)
Ammo.RegisterMultipleItemsWithFamilies({ ["9x18mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire)
-------------------------------------------------
RateOfFire.RegisterWeapon(SKORPION, { rpm = 850, enableSpread = true, sustainedSpread = 0.15, maxSpread = 1.9 })

-------------------------------------------------
-- The bolt under the top port with its two cocking knobs (GoM's bolt swap, as its Thompson and our PPSh-41)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(SKORPION, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})

-------------------------------------------------
-- Reload animation: GoM's (GoMReloads.lua), held like a pistol on its MP5K's
-------------------------------------------------
ReloadAnim.RegisterWeapon(SKORPION, require("GunsOfTien/GoMReloads").profile("handgun2"))

-------------------------------------------------
-- The wire stock: GoM's MAC-10 stock stats (flat values, as GoM's since its November 2026 update)
-------------------------------------------------
FoldingStock.RegisterWeapon(SKORPION, {
    attachments = { partType = "StockIntegrated", folded = FOLDED, deployed = DEPLOYED },
    initialState = "folded",
})
CSA.RegisterMultipleParts({
    [FOLDED] = {},
    [DEPLOYED] = {
        SF.Adjust("HitChance", 4),
        SF.Adjust("AimingTime", -3),
    },
})

-------------------------------------------------
-- Parts that cannot be taken off through the vanilla upgrade menu (magazines go with the reload)
-------------------------------------------------
PreventRemoval.Register(MAGS)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the stock folded, one magazine by
-- GoM's MP5 rule, the army's 24 likeliest
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[SKORPION] = {
        required = { "MarzGuns.Bolt_Lock", FOLDED },
        optionals = { MAGS[2] .. ":30", MAGS[1] .. ":20", MAGS[3] .. ":5" },
    }
end

GunsOfTien_Skorpion = { GUN = SKORPION, MAGS = MAGS }
