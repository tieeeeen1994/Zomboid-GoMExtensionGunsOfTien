--[[
    Guns of Tien -- belt links (docs/design.md 4e; user, 2026-10-22): the belt-fed guns' boxes are belts, every round
    held by a disintegrating link. Links are a supply of their own: filling a belt box takes one link with each round,
    unloading a round gives its link back, and a fired round's link is thrown out of the gun.
    - Belt boxes: the M249's 200-round box (M27 links) and Guns of Marz's M60 100-round box (M13 links). STANAG
      magazines in the M249 never need links.
    - Filling: Gunworks' magazine loading (ISLoadBulletsInMagazine, its InsertBullet anim event, run where the action
      is authoritative: the server in MP, the game in single player) is wrapped: a round that went in takes a link from
      the main inventory (where the rounds come from too), and the load counts as finished once no link is left, so it
      stops cleanly; with none at all it does not start ("Needs ..." over the head).
    - Unloading rounds from a belt box (ISUnloadBulletsFromMagazine, RemoveBullet) gives each round's link back.
    - Firing (user, 2026-10-22: "follow the realistic rules, treat links like hot brass"): every shot from a fitted
      belt box (OnWeaponSwingHitPoint, which the shooter's game fires for every shot) throws the round's empty link
      out of the gun's right side with Hot Brass's physics (it lands as a real item, never despawned, with our own
      landing sounds: a "Link" family in Hot Brass's impact sounds, scripts/make_link_sounds.py), drops it at the
      shooter's feet without Hot Brass, or puts it in Ammo Maker's brass catcher as Ammo Maker does casings (the
      advanced catcher always, the improvised one half the time). In single player at once; an MP client counts the
      shots and sends the count to the server twice a second (client/GunsOfTien/BeltLinks.lua), which throws them a
      few a tick (server/GunsOfTien/BeltLinks.lua). The server also fires the event, but only for shots that hit
      someone, so it does not count there.
    - Racking a chambered round out of a gun with a belt box fitted throws its link out with it (the round itself is
      vanilla's / Hot Brass's).
    A box fitted to a found gun counts as linked: firing or unloading it gives links.
--]]

GunsOfTien_BeltLinks = GunsOfTien_BeltLinks or {}
local BeltLinks = GunsOfTien_BeltLinks

-- belt box -> its link
BeltLinks.BOXES = {
    ["GunsOfTien.556x45Box200_M249"] = "GunsOfTien.M27_Link",
    ["MarzGuns.762x51Box100_M60"] = "GunsOfTien.M13_Link",
}

--- The link a belt box takes, or nil for any other magazine.
function BeltLinks.linkForBox(box)
    return box and box.getFullType and BeltLinks.BOXES[box:getFullType()] or nil
end

--- The link of the belt box fitted to a gun, or nil (no box, or a STANAG).
function BeltLinks.linkForGun(weapon)
    if not (weapon and weapon.getWeaponPart) then return nil end
    return BeltLinks.linkForBox(weapon:getWeaponPart("Clip"))
end

function BeltLinks.hasLink(character, link)
    return character:getInventory():getFirstType(link) ~= nil
end

--- Put n links in the character's main inventory (on the server, sent to its owner).
function BeltLinks.give(character, link, n)
    local inv = character:getInventory()
    for _ = 1, n do
        local item = inv:AddItem(link)
        if item and isServer() then
            sendAddItemToContainer(inv, item)
        end
    end
end

--- Take one link from the character's main inventory; false if there is none.
function BeltLinks.take(character, link)
    local inv = character:getInventory()
    local item = inv:getFirstType(link)
    if not item then return false end
    inv:Remove(item)
    if isServer() then
        sendRemoveItemFromContainer(inv, item)
    end
    return true
end

local function linkName(link)
    local script = ScriptManager.instance:getItem(link)
    return script and script:getDisplayName() or link
end

-------------------------------------------------
-- Filling a belt box
-------------------------------------------------
require("TimedActions/ISLoadBulletsInMagazine")
require("TimedActions/ISUnloadBulletsFromMagazine")

if not BeltLinks.wrapped then
    BeltLinks.wrapped = true

    local isLoadFinished = ISLoadBulletsInMagazine.isLoadFinished
    function ISLoadBulletsInMagazine:isLoadFinished()
        if isLoadFinished(self) then return true end
        local link = BeltLinks.linkForBox(self.magazine)
        return link ~= nil and not BeltLinks.hasLink(self.character, link)
    end

    local start = ISLoadBulletsInMagazine.start
    function ISLoadBulletsInMagazine:start()
        local link = BeltLinks.linkForBox(self.magazine)
        if link and not BeltLinks.hasLink(self.character, link) then
            if HaloTextHelper and self.character.isLocalPlayer and self.character:isLocalPlayer() then
                HaloTextHelper.addBadText(self.character, getText("IGUI_GunsOfTien_NeedLinks", linkName(link)))
            end
            self:forceStop()
            return
        end
        return start(self)
    end

    local loadEvent = ISLoadBulletsInMagazine.animEvent
    function ISLoadBulletsInMagazine:animEvent(event, parameter)
        local link = not isClient() and BeltLinks.linkForBox(self.magazine)
        local before = link and self.magazine:getCurrentAmmoCount()
        loadEvent(self, event, parameter)
        if link and self.magazine:getCurrentAmmoCount() > before then
            BeltLinks.take(self.character, link)
        end
    end

    local unloadEvent = ISUnloadBulletsFromMagazine.animEvent
    function ISUnloadBulletsFromMagazine:animEvent(event, parameter)
        local link = not isClient() and BeltLinks.linkForBox(self.magazine)
        local before = link and self.magazine:getCurrentAmmoCount()
        unloadEvent(self, event, parameter)
        if link and self.magazine:getCurrentAmmoCount() < before then
            BeltLinks.give(self.character, link, before - self.magazine:getCurrentAmmoCount())
        end
    end
end

-------------------------------------------------
-- Firing: the spent link thrown out of the gun
-------------------------------------------------
local okHB, HB = false, nil
if getActivatedMods():contains("HBVCEFb42") then
    okHB, HB = pcall(require, "SpentCasingPhysics/Init")
    if not okHB or type(HB) ~= "table" then HB = nil end
end

-- Hot Brass launch values per link: out of the receiver's right side (the M249's link port, the M60's right side),
-- lighter and slower than a case, flatter, turning end over end
BeltLinks.EJECT = {
    ["GunsOfTien.M27_Link"] = { forwardOffset = 0.32, sideOffset = 0.12, heightOffset = 0.47, shellForce = 0.45,
        sideSpread = 20, heightSpread = { 20, 45 }, ejectAngle = 95, spinForce = { 60, 120 } },
    ["GunsOfTien.M13_Link"] = { forwardOffset = 0.30, sideOffset = 0.12, heightOffset = 0.48, shellForce = 0.5,
        sideSpread = 20, heightSpread = { 20, 45 }, ejectAngle = 90, spinForce = { 50, 100 } },
}

if HB then
    if type(HB.CasingImpactSoundParams) == "table" then
        local family = {}
        for _, surface in ipairs({ "Concrete", "Dirt", "Grass", "Puddles", "Snow", "Wood" }) do
            family[surface] = { prefix = "GunsOfTien_Link_" .. surface .. "_", variations = 6 }
        end
        HB.CasingImpactSoundParams.Link = family
    end
    if HB.RegisterItemSound then
        HB.RegisterItemSound({ ["GunsOfTien.M27_Link"] = "Link", ["GunsOfTien.M13_Link"] = "Link" })
    end
end

local function catcher(inv, weight)
    if not ammoMakerGetContainerWithSpace then return nil end
    local advanced = ammoMakerGetContainerWithSpace(inv:FindAll("ammomaker_BrassCatcherAdvanced"), weight)
    if advanced then return advanced end
    local improvised = ammoMakerGetContainerWithSpace(inv:FindAll("ammomaker_BrassCatcherImprovised"), weight)
    if improvised and ZombRand(2) == 0 then return improvised end
    return nil
end

--- Throw one spent link out of the gun (where the game is authoritative: single player or the server).
function BeltLinks.eject(character, weapon, link)
    local script = ScriptManager.instance:getItem(link)
    local bag = catcher(character:getInventory(), script and script:getActualWeight() or 0.002)
    if bag then
        local item = instanceItem(link)
        if ammoMakerAddItemToInventory then
            ammoMakerAddItemToInventory(bag, item)
        else
            bag:AddItem(item)
            if isServer() then sendAddItemToContainer(bag, item) end
        end
        return
    end
    if HB and HB.doSpawnCasing and weapon and weapon:getAmmoType() then
        HB.doSpawnCasing(character, weapon, BeltLinks.EJECT[link], false, link, true)
        return
    end
    local square = character:getCurrentSquare()
    if square then
        square:AddWorldInventoryItem(link, ZombRandFloat(0.2, 0.8), ZombRandFloat(0.2, 0.8), 0.0)
    end
end

BeltLinks.pending = BeltLinks.pending or {}        -- MP client: weapon ID -> links not yet reported

local function onShot(character, weapon)
    if not (character and weapon and weapon.isRanged and weapon:isRanged()) then return end
    if isServer() then return end                 -- only shots that hit someone reach the server's event
    if getDebug() and character.isUnlimitedAmmo and character:isUnlimitedAmmo() then return end
    local link = BeltLinks.linkForGun(weapon)
    if not link then return end
    if isClient() then
        if not (character.isLocalPlayer and character:isLocalPlayer()) then return end
        local id = weapon:getID()
        BeltLinks.pending[id] = (BeltLinks.pending[id] or 0) + 1
    else
        BeltLinks.eject(character, weapon, link)
    end
end

-------------------------------------------------
-- Racking: the chambered round leaves the gun with its link
-------------------------------------------------
-- Vanilla's rackBullet (run where the action is authoritative) removes a chambered round that is not jammed
-- (removeBullet: into the inventory, or thrown out by Hot Brass at ejectCasing), so its link goes out with it.
-- rackBullet is wrapped rather than removeBullet, which Hot Brass replaces at OnInitGlobalModData on every world load.
require("TimedActions/ISRackFirearm")

if not BeltLinks.rackWrapped then
    BeltLinks.rackWrapped = true

    local rackBullet = ISRackFirearm.rackBullet
    function ISRackFirearm:rackBullet()
        local gun = self.gun
        local link = not isClient() and gun and gun:haveChamber() and gun:isRoundChambered() and not gun:isJammed()
            and BeltLinks.linkForGun(gun)
        rackBullet(self)
        if link then
            BeltLinks.eject(self.character, gun, link)
        end
    end
end

if BeltLinks.onShot then Events.OnWeaponSwingHitPoint.Remove(BeltLinks.onShot) end
BeltLinks.onShot = onShot
Events.OnWeaponSwingHitPoint.Add(onShot)
