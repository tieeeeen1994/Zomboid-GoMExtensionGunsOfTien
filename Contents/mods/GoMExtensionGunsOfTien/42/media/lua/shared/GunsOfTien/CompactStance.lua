--[[
    Guns of Tien -- the compact SMG stance (user, 2026-10-23; CLAUDE.md "Compact SMG stance"): the full-size Uzi, the
    Mini Uzi and Guns of Marz's MP5K (and Post-93's MP7, registered there) share one idle and aim.

    - Idle: the gun held down across the body, grip high on the right chest, magazine hanging clear of the belly, the
      left hand low on the gun's front. Aim: vanilla's rifle aim, the left hand slid back to the gun's support place.
      Both built from vanilla's rifle clips frame by frame (scripts/anim/compact_build.py), so walking, shooting and
      every aim pitch follow vanilla's motion.
    - The clips play through Gunworks' grip registry (WeaponSystems/Utils/GripAnim.lua): while a registered gun is in
      the primary hand Gunworks sets the animation variable GunworksGripAnim, and our AnimSet nodes
      (AnimSets/player/*/*_GoTCompact<Set>.xml, from scripts/anim/compact_animsets.py) gate on it with priority 100,
      as Heavy Ordnance does for its RPG. One animId per left-hand place: "GunsOfTien_CompactUzi" (under the front of
      the receiver), "GunsOfTien_CompactMP5K" (on its foregrip).
    - Every state the stance does not author falls back to the gun's class, which the game picks from TwoHandWeapon
      alone for guns (WeaponType.getWeaponType: in both hands and two-handed = "firearm"), so the Mini Uzi and the MP5K
      become two-handed (Item.DoParam; isTwoHandWeapon reads the script live) and are turned upright in the hand: they
      are modelled upside down for the pistol clips, and a model's own attachment named after the bone it hangs from
      (Bip01_Prop1) is applied in the hand (ModelInstanceRenderData.testOnBackItem), as vanilla turns its frying pan.
      Holsters, the back slot and the floor use other points, so they are unchanged. They can still be held in one
      hand, on the pistol clips, drawn with a model without the turn (OneHand.lua).
    - The game shoots (tracers, ballistics) from the gun bone and the model's `muzzle` point without that turn
      (BallisticsController.calculateMuzzlePosition), while the muzzle flash hangs on the drawn gun. So the turn is
      about the gun's own bore (the point offset by twice the muzzle's height), which keeps the muzzle where the game
      shoots from, and the turned guns' clips move the gun bone back by as much (scripts/anim/compact_pack.py): the
      gun is drawn where the hands hold it and the bullets leave its muzzle. That needs its own clips for the turned
      guns held like the Uzi ("GunsOfTien_CompactUziT": the Mini Uzi, Post-93's MP7s folded); the full Uzi is
      modelled upright.
--]]

local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")
local OneHand = require "GunsOfTien/OneHand"

local SETS = {
    ["GunsOfTien.UZI"] = "GunsOfTien_CompactUzi",
    ["GunsOfTien.MINIUZI"] = "GunsOfTien_CompactUziT",
    ["MarzGuns.MP5K"] = "GunsOfTien_CompactMP5K",
    -- Not the compact stance: vanilla's rifle hold with the left palm moved back onto the handguard
    -- (scripts/anim/rifle_hand.py, the set made for Post-93's UMPs, shipped here since 2026-10-27). GoM's full-size MP5s
    -- are scaled by 0.833 (build_mp5.py), the set's palm by 0.8375, so the hand lands where vanilla's held GoM's own MP5.
    ["MarzGuns.MP5"] = "GunsOfTien_CompactUMP",
    ["MarzGuns.MP5A2"] = "GunsOfTien_CompactUMP",
    ["MarzGuns.MP5SD"] = "GunsOfTien_CompactUMP",
}
-- modelled upside down for the pistol clips: turned upright in both hands, and made two-handed
local TURNED = { ["GunsOfTien.MINIUZI"] = true, ["MarzGuns.MP5K"] = true }

local CompactStance = {}
CompactStance.SETS = SETS

local function registerGrips()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        print("[GunsOfTien] compact stance: Gunworks.RegisterWeapon not found, stance not registered")
        return
    end
    for fullType, animId in pairs(SETS) do
        Gunworks.RegisterWeapon(fullType, { grip = { animId = animId } })
    end
end
Events.OnGameBoot.Add(registerGrips)

local patched = {}       -- item scripts made two-handed (scripts are new objects after a reload)

--- Turn a gun modelled upside down upright in the hand, about its bore, and make it two-handed (one hand allowed: drawn
--- with its one-hand model there, OneHand.lua). Also used by Post-93 for the MP7.
---@param fullType string
function CompactStance.turnUpright(fullType)
    local manager = ScriptManager.instance
    local model = manager:getModelScript(fullType)
    if model and not model:getAttachmentById("Bip01_Prop1") then
        -- turned 180 degrees about Y, then moved by twice the muzzle's z: the muzzle stays where it was
        local muzzle = model:getAttachmentById("muzzle")
        local z = muzzle and muzzle:getOffset():z() or 0.0
        local point = ModelAttachment.new("Bip01_Prop1")
        point:getOffset():set(0.0, 0.0, 2.0 * z)
        point:getRotate():set(0.0, 180.0, 0.0)
        model:addAttachment(point)
    elseif not model then
        print("[GunsOfTien] compact stance: model script not found: " .. fullType)
    end
    local item = manager:getItem(fullType)
    if item and not patched[item] then
        patched[item] = true
        -- equipped in both hands by default (hotbar, Equip Two Hands); "Equip Primary" still holds it in one hand, as
        -- a handgun (WeaponType: two-handed and in both hands = "firearm"). Not RequiresEquippedBothHands: the guns
        -- are held either way (user, 2026-10-26). Our own Mini Uzi and MP7s have it in their item scripts; GoM's MP5K
        -- needs this.
        item:DoParam("TwoHandWeapon = true")
    end
end

local function patchScripts()
    OneHand.copyModel("MarzGuns.MP5K", "GunsOfTien.MP5K_1H")
    for fullType in pairs(TURNED) do
        CompactStance.turnUpright(fullType)
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)

-- The MP5K's reload on the stance (GoM registers it on its pistol "handgun2" clips, style "none"): our clips
-- (GunsOfTien_CompactMP5K_Reload*, the magazine in the left hand from its release to its seating), Gunworks'
-- attachments style over GoM's MP5 magazines (ModelWeaponPart at its `magazine` point), the part spec pointed at the
-- magazine involved by Uzi.lua's wrapper. A GoM fix: registered after GoM's registry, which it replaces by full type.
local okRA, ReloadAnim = pcall(require, "WeaponSystems/ReloadAnim/HandlerFactory")
if okRA and type(ReloadAnim) == "table" and ReloadAnim.RegisterWeapon then
    pcall(require, "MarzWeapons/Registries/ReloadAnims")
    ReloadAnim.RegisterWeapon("MarzGuns.MP5K", {
        animId = "GunsOfTienCompactMP5K",
        style = "attachments",
        magItem = "MarzGuns.9x19Magazine30_MP5",
        attachments = { magPart = { itemType = "MarzGuns.9x19Magazine30_MP5", partType = "Clip" } },
        durations = { unload = 1.2, load = 1.5, rack = 1.2 },
    })
    ReloadAnim.GunsOfTienPointMag = ReloadAnim.GunsOfTienPointMag or {}
    ReloadAnim.GunsOfTienPointMag.GunsOfTienCompactMP5K = true
end
-- in one hand: GoM's own reload on its pistol clips (its magazineProfile("handgun2"), the clips' lengths)
OneHand.register("MarzGuns.MP5K", "MarzGuns.MP5K", "GunsOfTien.MP5K_1H", {
    animId = "handgun2",
    style = "none",
    durations = { unload = 1.29613, load = 1.29613, rack = 0.999844 },
})

return CompactStance
