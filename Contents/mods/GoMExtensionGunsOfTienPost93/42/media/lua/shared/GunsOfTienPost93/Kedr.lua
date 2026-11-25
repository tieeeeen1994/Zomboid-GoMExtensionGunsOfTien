--[[
    Guns of Tien - Post-93 -- the PP-91 Kedr (docs/post93_design.md "PP-91 Kedr"; user, 2026-11-26: "For makarov
    guns, let's add Skorpion and Kedr") in Gunworks' and Guns of Marz's registries.

    Dragunov's 9x18mm Makarov submachine gun, made at Zlatoust from 1994 for the Russian police, registered as GoM
    registers its MP5K / MAC-10 and as the MP7 and the main mod's TMP and Skorpion: held like a pistol and holstered
    (items_kedr.txt):
    - its own magazine profile, "9x18mm Kedr", with its 20 and 30-round magazines, in the main mod's "9x18mm" family
      (the plain round and this mod's later loads);
    - 1000 rpm (the factory's 800-1000), select fire Auto / Single; no rate reducer, so wilder than the Skorpion
      (850, 0.15 / 1.9): 0.2 / 2.3;
    - the bolt's side in the ejection port on the right and the cocking handle on the left, which is fixed to the
      bolt: one Bolt part on GoM's swap (back on each shot and on an empty gun), no ChargingHandle part;
    - reload: GoM's own animations (the main mod's GoMReloads.lua), its MP5K's ("handgun2");
    - the stock folded over the top or open (Gunworks' FoldingStock, the parts in items_kedr.txt, each state its own
      node drawn in place), with GoM's MAC-10 stock stats, folded on a found gun;
    - no muzzle parts (no muzzle family in 9x18mm; the Kedr-B with its integral can is another gun), no rails.
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
local GoMReloads = require("GunsOfTien/GoMReloads")

for _, file in ipairs({ "Ammunition", "Magazines", "RPM", "ReloadsAndAnims/ReloadAnims", "Stocks", "AttachmentCustomStats",
    "PermanentAttachments", "ReloadsAndAnims/AnimationsFiring" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTienPost93."
local KEDR = M .. "KEDR"
local MAGS = { M .. "9x18Magazine20_KEDR", M .. "9x18Magazine30_KEDR" }
local FOLDED, DEPLOYED = M .. "KEDR_Integrated_Stock_Folded", M .. "KEDR_Integrated_Stock_Deployed"

-------------------------------------------------
-- Magazines: the Kedr's own profile, in the main mod's 9x18mm family
-------------------------------------------------
Magazine.RegisterMagazineProfile("9x18mm Kedr", MAGS)
Magazine.RegisterWeaponWithProfile("9x18mm Kedr", KEDR)
Ammo.RegisterMultipleItemsWithFamilies({ ["9x18mm"] = MAGS })

-------------------------------------------------
-- Rate of fire (required for Gunworks' real auto fire)
-------------------------------------------------
RateOfFire.RegisterWeapon(KEDR, { rpm = 1000, enableSpread = true, sustainedSpread = 0.2, maxSpread = 2.3 })

-------------------------------------------------
-- The bolt in the ejection port with the cocking handle on it (GoM's bolt swap)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(KEDR, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})

-------------------------------------------------
-- Reload animation: GoM's, held like a pistol on its MP5K's
-------------------------------------------------
ReloadAnim.RegisterWeapon(KEDR, GoMReloads.profile("handgun2"))

-------------------------------------------------
-- The folding stock: GoM's MAC-10 stock stats (flat values, as GoM's since its November 2026 update)
-------------------------------------------------
FoldingStock.RegisterWeapon(KEDR, {
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
-- GoM's MP5 rule (the shorter likelier)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    spawnTable[KEDR] = {
        required = { "MarzGuns.Bolt_Lock", FOLDED },
        optionals = { MAGS[1] .. ":30", MAGS[2] .. ":20" },
    }
end

GunsOfTienPost93_Kedr = { GUN = KEDR, MAGS = MAGS }
