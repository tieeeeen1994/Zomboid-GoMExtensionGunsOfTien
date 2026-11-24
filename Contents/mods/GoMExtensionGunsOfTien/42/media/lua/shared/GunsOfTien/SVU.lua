--[[
    Guns of Tien -- the SVU (OTs-03, 1991; user, 2026-11-20; docs/design.md 4p) in Gunworks' and Guns of Marz's
    registries.

    TsKIB SOO's bullpup SVD of 1991, the semi-automatic first model, built on GoM's SVD (scripts/build_svu.py) and
    registered as GoM registers its SVD (items_svu.txt):
    - GoM's SVD 10-round magazine, the SVU's real one (a profile of its own, appended to the magazine's MountOn);
    - the bolt carrier with its handle moves on each shot and holds open when empty (GoM's SVD bolt swap);
    - reload: GoM's FAMAS reload ("famas_rifle", GoMReloads.lua), the bullpup one, as the AUGs (the magazine sits
      behind the grip), GoM's magazine in the off hand at the gun's size (HandMagazines.lua);
    - GoM's AK mount on the SVU's side rail (moved forward onto the handguard's rear, as on the real gun) and every
      optic GoM fits on its SVD, appended to their MountOn;
    - the folding sights: raised with no optic (the gun's own model), folded with any of GoM's optics (`SVU_FD`),
      through Gunworks' ConditionalModel, as Post-93's iron sights (GunsOfTienPost93/IronSights.lua);
    - no rail under the handguard, no bipod, no muzzle parts: the 1991 SVU had none (its brake is fixed);
    - a found gun comes with its magazine at GoM's SVD chance and GoM's SVD optics with the AK mount (":AM") at its
      chances.
--]]

local Magazine = require("WeaponSystems/Utils/Magazine")
local Ammo = require("WeaponSystems/Utils/Ammo")
local Animations = require("WeaponSystems/Utils/Animations")
local ConditionalModel = require("WeaponSystems/Utils/ConditionalModel")
local PreventRemoval = require("WeaponSystems/Utils/PreventRemovals")

for _, file in ipairs({ "Ammunition", "Magazines", "ReloadsAndAnims/AnimationsFiring", "ReloadsAndAnims/ReloadAnims",
    "PermanentAttachments" }) do
    pcall(require, "MarzWeapons/Registries/" .. file)
end

local M = "GunsOfTien."
local SVU = M .. "SVU"
local MAG = "MarzGuns.762x54Magazine10_SVD"
local MAGS = { MAG }

-------------------------------------------------
-- Magazines (GoM's SVD magazine is in GoM's "7.62x54mm" ammunition family already)
-------------------------------------------------
Magazine.RegisterMagazineProfile("7.62x54mm SVU", MAGS)
Magazine.RegisterWeaponWithProfile("7.62x54mm SVU", SVU)
Ammo.RegisterMultipleItemsWithFamilies({ ["7.62x54mm"] = MAGS })

-------------------------------------------------
-- The bolt (GoM's SVD bolt swap) and the reload (GoM's FAMAS reload, the magazine in the off hand at our size)
-------------------------------------------------
Animations.RegisterWeaponWithAnimatedParts(SVU, {
    SingleAttachment = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" },
    cycleTicks = 3,
})
local HandMagazines = require("GunsOfTien/HandMagazines")
local HAND = HandMagazines.mapOf(MAGS)
HandMagazines.register(SVU, HAND)
require("WeaponSystems/ReloadAnim/HandlerFactory").RegisterWeapon(SVU,
    require("GunsOfTien/GoMReloads").profile("famas_rifle", { partState = { props = HandMagazines.props(HAND) } }))

-------------------------------------------------
-- The folding sights follow the optic
-------------------------------------------------
local OPTICS = { "EXPS1_Sight", "EXPS3_Sight", "ElcanX2_Scope", "LR10X_Scope", "Aimpoint_Sight", "TA28_Scope",
    "LR4X_Scope", "OKP3_Sight", "ReflexS2_Sight", "JS14_Sight", "Kobra_Sight", "TR06X_Scope", "PSO1_Scope",
    "LRX12X_Scope" }
local optics = {}
for i, o in ipairs(OPTICS) do optics[i] = "MarzGuns." .. o end
ConditionalModel.Register(SVU, { rules = { { parts = { Scope = optics }, model = SVU .. "_FD" } }, default = SVU })

PreventRemoval.Register(MAGS)

-------------------------------------------------
-- GoM's parts and magazine allowed on it: appended to their MountOn (DoParam replaces the list, so it is read and
-- written back whole, as RPK.lua does)
-------------------------------------------------
local PARTS = { MAG, "MarzGuns.AK_Mount" }
for _, o in ipairs(optics) do PARTS[#PARTS + 1] = o end

local function appendMountOn(partType, gun)
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
    if seen[gun] then return end
    list[#list + 1] = gun
    script:DoParam("MountOn = " .. table.concat(list, ";"))
end

local function appendAll()
    for _, part in ipairs(PARTS) do appendMountOn(part, SVU) end
end

-- Item scripts exist from game boot; re-run at every world load because scripts are reloaded on leaving a game.
Events.OnGameBoot.Add(appendAll)
Events.OnInitGlobalModData.Add(appendAll)
-- and at once (user, 2026-11-25): GoM's guns are in its parts' MountOn from the script files on, and a mod that
-- lists a gun's slots from MountOn when its own Lua loads (before OnGameBoot) missed ours
pcall(appendAll)

-------------------------------------------------
-- A found gun (GoM's MarzGuns_OnCreate.AttachParts reads this table): the bolt, the magazine at GoM's SVD chance,
-- GoM's SVD optics with the AK mount (":AM") at its chances (its PSO-1 rarely, as on its SVD)
-------------------------------------------------
local ok, points = pcall(require, "MarzWeapons/OnCreate/AttachmentPointsTable")
local spawnTable = ok and type(points) == "table" and points.weaponAttachmentTablesAndChances
if spawnTable then
    local optionals = { MAG .. ":50" }
    for _, o in ipairs({ "ReflexS2_Sight", "Kobra_Sight", "OKP3_Sight", "JS14_Sight", "EXPS3_Sight", "EXPS1_Sight",
        "Aimpoint_Sight" }) do optionals[#optionals + 1] = "MarzGuns." .. o .. ":1:AM" end
    for _, o in ipairs({ "LR4X_Scope", "TA28_Scope", "ElcanX2_Scope" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":5:AM"
    end
    for _, o in ipairs({ "TR06X_Scope", "PSO1_Scope", "LR10X_Scope", "LRX12X_Scope" }) do
        optionals[#optionals + 1] = "MarzGuns." .. o .. ":1:AM"
    end
    spawnTable[SVU] = { required = { "MarzGuns.Bolt_Lock" }, optionals = optionals }
end

GunsOfTien_SVU = { GUN = SVU, MAG = MAG }
