--[[
    Guns of Tien -- the turned guns held in one hand or in both (user, 2026-10-26: "they can be held in one hand, but
    they can also be held with 2 hands"): the Mini Uzi, Guns of Marz's MP5K and Post-93's MP7A1 / MP7A2.

    - They are modelled upside down for vanilla's pistol clips. In both hands they play the compact SMG stance, built
      from vanilla's rifle clips, and CompactStance.lua turns them upright there with a Bip01_Prop1 point on the model.
      That point is part of the model script, so it applied in one hand too, where the game plays the pistol clips
      ("handgun": WeaponType.getWeaponType gives "firearm" only to a two-handed gun in both hands) and the gun was
      drawn upside down and reversed.
    - So each has a second model without the turn (GunsOfTien.MINIUZI_1H, GunsOfTien.MP5K_1H,
      GunsOfTienPost93.MP7A1_1H / MP7A2_1H; scripts/gen_scripts.py, gen_post93_guns.py), and every client draws the gun
      held in the primary hand alone with it (HandWeapon:setWeaponSprite + resetEquippedHandsModels, as SawnStock.lua
      does), for its own players and every other player it sees. Each client works it out from the hands, which sync,
      so nothing is sent. The sprite goes back to the two-hand model as soon as the gun leaves that hand, and before a
      save, so items keep their script's model.
    - The guns are two-handed without RequiresEquippedBothHands, so "Equip Primary" is offered and the hotbar still
      equips both hands; Gunworks' re-equips (reloads, folds, GoM's MP5K on every shot) keep the hand they found.
      The engine treats a two-handed weapon in one hand as any other: half damage
      (CombatManager.applyOneHandedDamagePenalty) and 0.77 combat speed.
    - Reload: in one hand the gun's pistol clips, through a Gunworks reload handler with a matches(gun) predicate
      (ReloadAnim.GetHandlerForGun tries those before the full type index, where the stance's reload is): the Mini Uzi
      the Micro Uzi's ("UziGrip"), the MP7s their old pistol clips ("MP7A1"), the MP5K Guns of Marz's own ("handgun2").
--]]

local OneHand = {}
OneHand.GUNS = {}        -- full type -> { two = model in both hands, one = model in one hand }

local function heldInOneHand(gun)
    local container = gun:getContainer()
    local chr = container and container:getCharacter()
    return chr ~= nil and chr:getPrimaryHandItem() == gun and chr:getSecondaryHandItem() ~= gun
end
OneHand.heldInOneHand = heldInOneHand

local okRA, ReloadAnim = pcall(require, "WeaponSystems/ReloadAnim/HandlerFactory")

--- Register a turned gun: its two models and, optionally, the reload profile it plays in one hand.
---@param fullType string
---@param twoHandModel string
---@param oneHandModel string
---@param reload table|nil a Gunworks reload profile (ReloadAnim.RegisterWeapon), without fullType
function OneHand.register(fullType, twoHandModel, oneHandModel, reload)
    OneHand.GUNS[fullType] = { two = twoHandModel, one = oneHandModel }
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
-- Guns of Marz's MP5K: its one-hand model takes GoM's live mesh, texture and points (all but the turn)
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

-------------------------------------------------
-- The model in the hand (clients and single player: a dedicated server draws nothing)
-------------------------------------------------
if not isServer() then
    local oneHanded = {}     -- weapon -> player, while drawn with its one-hand model

    local function setSprite(player, weapon, sprite)
        weapon:setWeaponSprite(sprite)
        player:resetEquippedHandsModels()
    end

    local function check(player)
        local weapon = player:getPrimaryHandItem()
        local entry = weapon and OneHand.GUNS[weapon:getFullType()]
        if not entry then return end
        local sprite = weapon:getWeaponSprite()
        if player:getSecondaryHandItem() == weapon then
            if sprite == entry.one then
                setSprite(player, weapon, entry.two)
                oneHanded[weapon] = nil
            end
        elseif sprite == entry.two then     -- any other model (another mod's) is left alone
            setSprite(player, weapon, entry.one)
            oneHanded[weapon] = player
        end
    end

    local function restore(weapon, player)
        local entry = OneHand.GUNS[weapon:getFullType()]
        if entry and weapon:getWeaponSprite() == entry.one then
            weapon:setWeaponSprite(entry.two)
        end
        oneHanded[weapon] = nil
        if player and player:getPrimaryHandItem() == weapon then
            player:resetEquippedHandsModels()
        end
    end

    Events.OnTick.Add(function()
        local done = nil       -- collected first: the table is not changed while pairs walks it
        for weapon, player in pairs(oneHanded) do
            if player:getPrimaryHandItem() ~= weapon or player:getSecondaryHandItem() == weapon then
                done = done or {}
                done[#done + 1] = weapon
            end
        end
        if done then
            for _, weapon in ipairs(done) do
                restore(weapon, oneHanded[weapon])
            end
        end
        for i = 0, getNumActivePlayers() - 1 do
            local player = getSpecificPlayer(i)
            if player then check(player) end
        end
        if isClient() then
            local players = getOnlinePlayers()
            for i = 0, players:size() - 1 do
                local player = players:get(i)
                if not player:isLocalPlayer() then check(player) end
            end
        end
    end)

    -- saved with the script's model (single player saves on this side); the next tick draws it in one hand again
    Events.OnSave.Add(function()
        for weapon in pairs(oneHanded) do
            local entry = OneHand.GUNS[weapon:getFullType()]
            if entry and weapon:getWeaponSprite() == entry.one then
                weapon:setWeaponSprite(entry.two)
            end
        end
        oneHanded = {}
    end)
end

return OneHand
