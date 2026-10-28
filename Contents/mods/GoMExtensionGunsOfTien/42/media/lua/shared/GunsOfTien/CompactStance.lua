--[[
    Guns of Tien -- the short SMG stance (CLAUDE.md "Animations are generic"; user, 2026-10-28): one stance for every
    short SMG, held by the grip with no stock to the shoulder: the full-size Uzi, the Mini Uzi and Post-93's MP7A1 / A2
    (registered there). It replaced four per-gun sets (Uzi, UziT, MP5K, MP7). Guns of Marz's MP5K left it for the
    UMPs' rifle-hand set, held like the MP5A3 (user, 2026-10-28: liked better, the left hand on its front end).

    - Idle: the gun held down across the body, grip high on the right chest, magazine hanging clear of the belly, the
      left hand low on the gun's front. Aim: vanilla's rifle aim, the left hand slid back to the gun's support place.
      Both built from vanilla's rifle clips frame by frame (scripts/anim/compact_build.py, the "Uzi" build, the Uzi's
      left-hand place for every gun), so walking, shooting and every aim pitch follow vanilla's motion.
    - The clips play through Gunworks' grip registry (WeaponSystems/Utils/GripAnim.lua): while a registered gun is in
      the primary hand Gunworks sets the animation variable GunworksGripAnim, and our AnimSet nodes
      (AnimSets/player/*/*_GoTCompactShortSMG.xml, from scripts/anim/compact_animsets.py) gate on it with priority 100,
      as Heavy Ordnance does for its RPG. animId "GunsOfTien_CompactShortSMG".
    - The stance holds its gun in the pistol orientation (the gun bone turned half a turn about the barrel at the grip,
      scripts/anim/compact_pack.py): the guns are modelled for vanilla's pistol clips (GoM's MP5K / MAC-10 way; the
      full Uzi too since 2026-10-28), so each is drawn upright with its grip in the hand, the muzzle the game shoots
      from (the gun bone and the model's `muzzle` point) is the drawn muzzle, and the same model serves one hand.
    - Every state the stance does not author falls back to the gun's class, which the game picks from TwoHandWeapon
      alone for guns (WeaponType.getWeaponType: in both hands and two-handed = "firearm"), so the Mini Uzi and the MP5K
      are made two-handed (Item.DoParam; isTwoHandWeapon reads the script live). They can still be held in one hand, on
      the pistol clips (OneHand.lua).
    - The MP5K on the rifle-hand set: those nodes do not test the weapon class (the UMPs and MP5A3s are never in one
      hand), so its grip is a Gunworks matcher that holds only while the gun is in both hands, and OneHand.lua draws it
      there with GunsOfTien.MP5K_2H, its body turned upright for the rifle clips (build_mp5.py "two_hand").
    - Reloads by family (magazine change and rack chosen separately, CLAUDE.md "Animations are generic"), clips in the
      stance's packs (GunsOfTien_CompactShortSMG<Family>_Reload*), nodes *GunsOfTienCompactShortSMG<Id>_GoT.xml:
      "GunsOfTienCompactShortSMGPistol" (magazine into the grip, the rack pulled overhand: the Uzi, the Mini Uzi),
      "GunsOfTienCompactShortSMGPistolRearT" (the pistol magazine change and the rear T-handle rack: the MP7s), and
      "GunsOfTienCompactShortSMGHK" (H&K), built for the MP5K and used by no gun since it left the stance (kept for a
      short H&K-type gun). GoM's MP5s, the MP5K in both hands too, take the H&K family on the rifle-hand hold: the UMPs'
      reload ("GunsOfTienCompactUMP").
--]]

local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")
local OneHand = require "GunsOfTien/OneHand"

local SHORT_SMG = "GunsOfTien_CompactShortSMG"
local SETS = {
    ["GunsOfTien.UZI"] = SHORT_SMG,
    ["GunsOfTien.MINIUZI"] = SHORT_SMG,
    -- Not the short SMG stance: vanilla's rifle hold with the left palm moved back onto the handguard
    -- (scripts/anim/rifle_hand.py, the set made for Post-93's UMPs, shipped here since 2026-10-27). GoM's full-size MP5s
    -- are scaled by 0.833 (build_mp5.py), the set's palm by 0.8375, so the hand lands where vanilla's held GoM's own MP5.
    ["MarzGuns.MP5"] = "GunsOfTien_CompactUMP",
    ["MarzGuns.MP5A2"] = "GunsOfTien_CompactUMP",
    ["MarzGuns.MP5SD"] = "GunsOfTien_CompactUMP",
}
-- the same set only while held in both hands (its nodes do not test the weapon class): no full type entry, a matcher
local BOTH_HANDS_SETS = {
    ["MarzGuns.MP5K"] = "GunsOfTien_CompactUMP",
}
-- held in one hand too, so not two-handed in their scripts: made two-handed here
local MADE_TWO_HANDED = { "GunsOfTien.MINIUZI", "MarzGuns.MP5K" }

local CompactStance = {}
CompactStance.SETS = SETS
CompactStance.BOTH_HANDS_SETS = BOTH_HANDS_SETS
CompactStance.SHORT_SMG = SHORT_SMG

local function registerGrips()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        print("[GunsOfTien] short SMG stance: Gunworks.RegisterWeapon not found, stance not registered")
        return
    end
    for fullType, animId in pairs(SETS) do
        Gunworks.RegisterWeapon(fullType, { grip = { animId = animId } })
    end
    local okGA, GripAnim = pcall(require, "WeaponSystems/Utils/GripAnim")
    if not (okGA and type(GripAnim) == "table" and GripAnim.RegisterWeapon) then
        print("[GunsOfTien] rifle-hand set: GripAnim.RegisterWeapon not found, MP5K hold not registered")
        return
    end
    for fullType, animId in pairs(BOTH_HANDS_SETS) do
        GripAnim.RegisterWeapon(nil, {
            id = fullType .. "@BothHands",
            animId = animId,
            matches = function(gun)
                return gun:getFullType() == fullType and OneHand.heldInBothHands(gun)
            end,
        })
    end
end
Events.OnGameBoot.Add(registerGrips)

local patched = {}       -- item scripts made two-handed (scripts are new objects after a reload)

--- Make a gun two-handed for the stance (one hand allowed: OneHand.lua). Also used by Post-93 for the MP7s.
---@param fullType string
function CompactStance.makeTwoHanded(fullType)
    local item = ScriptManager.instance:getItem(fullType)
    if item and not patched[item] then
        patched[item] = true
        -- equipped in both hands by default (hotbar, Equip Two Hands); "Equip Primary" still holds it in one hand, as
        -- a handgun (WeaponType: two-handed and in both hands = "firearm"). Not RequiresEquippedBothHands: the guns
        -- are held either way (user, 2026-10-26).
        item:DoParam("TwoHandWeapon = true")
    end
end

local function patchScripts()
    -- the MP5K's one-hand model, kept for guns saved with it while OneHand.lua swapped models (until 2026-10-28):
    -- GoM's live mesh, texture and points
    OneHand.copyModel("MarzGuns.MP5K", "GunsOfTien.MP5K_1H")
    for _, fullType in ipairs(MADE_TWO_HANDED) do
        CompactStance.makeTwoHanded(fullType)
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)

-- GoM's MP5A3 / MP5A2 / MP5SD, and the MP5K in both hands: the H&K family on their rifle-hand hold, the UMPs' reload
-- (built for the UMP's well and handle by scripts/anim/smg_reload.py's `ump`, clips in GunsOfTien_CompactUMP_Pack3.x,
-- nodes *GunsOfTienCompactUMP_GoT.xml, both in this mod since 2026-10-28) instead of GoM's own (the MP5K's on its pistol
-- "handgun2" clips, style "none"); Gunworks' attachments style over GoM's MP5 magazines (ModelWeaponPart at the
-- `magazine` point), the magazine in the left hand, the part spec pointed at the magazine involved (20 to 100 rounds)
-- by Uzi.lua's wrapper. A GoM fix: registered after GoM's registry, which it replaces by full type. Each gets its own
-- table. The MP5K in one hand keeps GoM's reload through OneHand's matcher, tried first (below).
local okRA, ReloadAnim = pcall(require, "WeaponSystems/ReloadAnim/HandlerFactory")
if okRA and type(ReloadAnim) == "table" and ReloadAnim.RegisterWeapon then
    pcall(require, "MarzWeapons/Registries/ReloadAnims")
    for _, gun in ipairs({ "MarzGuns.MP5", "MarzGuns.MP5A2", "MarzGuns.MP5SD", "MarzGuns.MP5K" }) do
        ReloadAnim.RegisterWeapon(gun, {
            animId = "GunsOfTienCompactUMP",
            style = "attachments",
            magItem = "MarzGuns.9x19Magazine30_MP5",
            attachments = { magPart = { itemType = "MarzGuns.9x19Magazine30_MP5", partType = "Clip" } },
            durations = { unload = 1.2, load = 1.5, rack = 1.2 },
        })
    end
    ReloadAnim.GunsOfTienPointMag = ReloadAnim.GunsOfTienPointMag or {}
    ReloadAnim.GunsOfTienPointMag.GunsOfTienCompactUMP = true
end
-- in one hand: GoM's own reload on its pistol clips (its magazineProfile("handgun2"), the clips' lengths)
OneHand.register("MarzGuns.MP5K", {
    animId = "handgun2",
    style = "none",
    durations = { unload = 1.29613, load = 1.29613, rack = 0.999844 },
})
-- in both hands: drawn upright for the rifle clips (GoM's model, and our old one-hand copy on guns saved with it, are
-- the pistol-clip model)
OneHand.setTwoHandModel("MarzGuns.MP5K", "GunsOfTien.MP5K_2H", "MarzGuns.MP5K", { "GunsOfTien.MP5K_1H" })

return CompactStance
