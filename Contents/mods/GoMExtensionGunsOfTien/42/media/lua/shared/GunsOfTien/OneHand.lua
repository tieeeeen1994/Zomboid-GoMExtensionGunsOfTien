--[[
    Guns of Tien -- the short SMGs held in one hand or in both (user, 2026-10-26: "they can be held in one hand, but
    they can also be held with 2 hands"): the Mini Uzi, Guns of Marz's MP5K and Post-93's MP7A1 / MP7A2.

    - In both hands they play the short SMG stance (CompactStance.lua), in one hand vanilla's pistol clips ("handgun":
      WeaponType.getWeaponType gives "firearm" only to a two-handed gun in both hands). The stance holds its guns in the
      pistol orientation, so one model serves both. (Until 2026-10-28 the stance turned the guns upright with a model
      point and this file drew a gun held in one hand with a second model without it; those models, *_1H, stay in the
      scripts for guns saved with them, and look the same.)
    - The guns are two-handed without RequiresEquippedBothHands, so "Equip Primary" is offered and the hotbar still
      equips both hands; Gunworks' re-equips (reloads, folds, GoM's MP5K on every shot) keep the hand they found.
      The engine treats a two-handed weapon in one hand as any other: half damage
      (CombatManager.applyOneHandedDamagePenalty) and 0.77 combat speed.
    - Reload: in one hand a pistol family, through a Gunworks reload handler with a matches(gun) predicate
      (ReloadAnim.GetHandlerForGun tries those before the full type index, where the stance's reload is): the Mini Uzi
      and the MP7s vanilla's pistol clips ("UziGrip", the Micro Uzi's), the MP5K Guns of Marz's own ("handgun2").
--]]

local OneHand = {}
OneHand.GUNS = {}        -- full type -> true

local function heldInOneHand(gun)
    local container = gun:getContainer()
    local chr = container and container:getCharacter()
    return chr ~= nil and chr:getPrimaryHandItem() == gun and chr:getSecondaryHandItem() ~= gun
end
OneHand.heldInOneHand = heldInOneHand

local okRA, ReloadAnim = pcall(require, "WeaponSystems/ReloadAnim/HandlerFactory")

--- Register a gun held in one hand or in both, with the reload profile it plays in one hand.
---@param fullType string
---@param reload table|nil a Gunworks reload profile (ReloadAnim.RegisterWeapon), without fullType
function OneHand.register(fullType, reload)
    OneHand.GUNS[fullType] = true
    if reload and okRA and type(ReloadAnim) == "table" and ReloadAnim.RegisterWeapon then
        reload.id = fullType .. "@OneHand"
        reload.matches = function(gun)
            return gun:getFullType() == fullType and heldInOneHand(gun)
        end
        ReloadAnim.RegisterWeapon(nil, reload)
    end
end

-------------------------------------------------
-- Kept in one hand. Gunworks re-equips the gun after every magazine insert / eject, fold, part swap and, for guns
-- with an animated bolt (GoM's MP5K), every shot (Animations.CallSyncHandWeaponFields: both hands for any two-handed
-- weapon), which would put a gun held in one hand into both. For our guns held in one hand, what the other hand held
-- is put back.
-------------------------------------------------
local okAn, Animations = pcall(require, "WeaponSystems/Utils/Animations")
if okAn and type(Animations) == "table" and Animations.CallSyncHandWeaponFields then
    local callSyncHandWeaponFields = Animations.CallSyncHandWeaponFields
    Animations.CallSyncHandWeaponFields = function(player, weapon, ...)
        if not (player and weapon and OneHand.GUNS[weapon:getFullType()] and player:getPrimaryHandItem() == weapon
                and player:getSecondaryHandItem() ~= weapon) then
            return callSyncHandWeaponFields(player, weapon, ...)
        end
        local other = player:getSecondaryHandItem()
        local result = callSyncHandWeaponFields(player, weapon, ...)
        player:setSecondaryHandItem(other)
        player:resetEquippedHandsModels()
        return result
    end
end

-------------------------------------------------
-- Guns of Marz's MP5K: its old one-hand model (kept for guns saved with it) takes GoM's live mesh, texture and points
-------------------------------------------------
local function fmt(v)
    return string.format("%.4f %.4f %.4f", v:x(), v:y(), v:z())
end

function OneHand.copyModel(from, to)
    local manager = ScriptManager.instance
    local src, dst = manager:getModelScript(from), manager:getModelScript(to)
    if not (src and dst) then
        print("[GunsOfTien] one hand: model script not found: " .. (src and to or from))
        return
    end
    local name = dst:getName()
    local text = { "model ", name, " { mesh = ", src:getMeshName(), ", texture = ", src:getTextureName(), "," }
    for i = 0, src:getAttachmentCount() - 1 do
        local a = src:getAttachment(i)
        if a:getId() ~= "Bip01_Prop1" then
            local bone = a:getBone()
            text[#text + 1] = " attachment " .. a:getId() .. " { offset = " .. fmt(a:getOffset()) .. ", rotate = "
                .. fmt(a:getRotate()) .. ", scale = " .. string.format("%.4f", a:getScale())
                .. ((bone and bone ~= "") and (", bone = " .. bone) or "") .. ", }"
        end
    end
    text[#text + 1] = " }"
    dst:Load(name, table.concat(text))
end

return OneHand
