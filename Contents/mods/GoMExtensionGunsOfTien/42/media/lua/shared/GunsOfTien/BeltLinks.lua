--[[
    Guns of Tien -- belt links (docs/design.md 4e; user, 2026-10-22): the belt-fed guns' boxes are belts, every round
    held by a disintegrating link. Links are a supply of their own: filling a belt box takes one link with each round,
    unloading a round gives its link back, and a fired round's link goes where its casing goes.
    - Belt boxes: the M249's 200-round box (M27 links) and Guns of Marz's M60 100-round box (M13 links). STANAG
      magazines in the M249 never need links.
    - Filling: Gunworks' magazine loading (ISLoadBulletsInMagazine, its InsertBullet anim event, run where the action
      is authoritative: the server in MP, the game in single player) is wrapped: a round that went in takes a link from
      the main inventory (where the rounds come from too), and the load counts as finished once no link is left, so it
      stops cleanly; with none at all it does not start ("Needs ..." over the head).
    - Unloading rounds from a belt box (ISUnloadBulletsFromMagazine, RemoveBullet) gives each round's link back.
    - Firing (user, 2026-10-22: "follow the realistic rules, treat links like hot brass"; 2026-10-31: "copy the
      behaviour of the casings", under the casing mods and their sandbox options): a fired round's empty link is not
      placed by a rule of ours but rides along with the casing the casing mods place for that shot, where the game
      is authoritative (the server, or single player), on those mods' own per-shot commands:
      - Neither Hot Brass nor Ammo Maker: vanilla has no casing items, so the link is gone.
      - Hot Brass alone: its spawnCasing (one `HBVCEF spawnCasing` command per shot from the shooter's client at
        OnWeaponSwing, or a direct call in single player) places the casing through addCasing (flight, then an item
        only with its Persistent Casings option) or addCasingToVehicle (the seat's container, whatever the option);
        while it runs for a gun with a belt box, the link is placed the same way right after the casing: flying on
        its own launch values (EJECT) with the casing's ignoreDespawn, or into the same seat. Every condition Hot
        Brass puts on a casing (a casing for the round in AMMO_TO_CASING, a chambered unjammed round, a gun that
        neither racks after each shot nor keeps its spent rounds) therefore holds for the link too.
      - Ammo Maker (Hot Brass then throws no casing on firing): the link is Ammo Maker's extra item for the shot, the
        mechanism its ammoData `dropExtraData` uses for other mods' belt links (GoM's API file lists Guns-93's
        M249 / M60 commented out). That table is keyed by the gun's type, which cannot tell a belt box from the M249's
        STANAG magazines, so ammoMakerGetDropExtraDataItemType is wrapped: an `ammomaker returnCasingsOnAttack`
        command (one per shot) notes its gun in our OnClientCommand handler, added from the shared folder and so run
        before Ammo Maker's (server folder), and the wrapper answers that gun's link when it has a belt box. Ammo
        Maker then keeps the link with its casing: the same capacity check (both weights), the same catcher and roll,
        else the same throw (Hot Brass's doSpawnCasing, our launch values swapped in) or floor spot, and its
        clean-up list, which can only remove its own items, so links are listed in server/GunsOfTien/BeltLinks.lua
        instead and removed on its schedule and DroppedCasingsLifetime.
      The links' landing sounds are a "Link" family in Hot Brass's impact sounds (scripts/make_link_sounds.py).
    - Racking a chambered round out of a gun with a belt box fitted: the link goes where the round goes, into the
      inventory (vanilla's removeBullet) or thrown out by Hot Brass (its rackCasing with racking = true).
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
-- Firing and racking out: the link follows its casing (or the racked round)
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

-- Ammo Maker: the gun of the casing command being handled. This handler is added from the shared folder, so it runs
-- before Ammo Maker's own (server folder), which then asks ammoMakerGetDropExtraDataItemType for the shot's extra item.
local amWeapon

local function onClientCommand(module, command, player, args)
    if module ~= "ammomaker" then return end
    amWeapon = command == "returnCasingsOnAttack" and type(args) == "table" and args.weapon or nil
end

local follow                          -- Hot Brass: the link of the casing or round it is placing right now
local wrapped = {}                    -- our wrappers, so a world reload does not wrap them again

local function wrap(fn)
    wrapped[fn] = true
    return fn
end

-- Everything wrapped here is defined in the other mods' server folders (after this file) and looked up at each call.
local function install()
    if isClient() then return end

    -- Ammo Maker: the link is the shot's extra item, so it goes with its casing (same catcher and roll, the same
    -- throw or floor spot, the same clean-up)
    local extraItem = ammoMakerGetDropExtraDataItemType
    if extraItem and not wrapped[extraItem] then
        ammoMakerGetDropExtraDataItemType = wrap(function(dropExtraData, weaponType)
            local own = extraItem(dropExtraData, weaponType)
            if own then return own end
            local gun = amWeapon
            if gun and gun.getFullType and gun:getFullType() == weaponType then
                return BeltLinks.linkForGun(gun)
            end
            return nil
        end)
    end

    -- Ammo Maker's clean-up list matches only its own items, so links get a list of their own
    -- (server/GunsOfTien/BeltLinks.lua)
    local addCleanUp = ammoMakerItemCleanUpAddModData
    if addCleanUp and BeltLinks.noteDropped and not wrapped[addCleanUp] then
        ammoMakerItemCleanUpAddModData = wrap(function(itemType, x, y, z)
            local fullType = type(itemType) == "string" and itemType or (itemType and itemType:getFullType())
            if BeltLinks.EJECT[fullType] then
                BeltLinks.noteDropped(fullType, x, y, z)
                return
            end
            return addCleanUp(itemType, x, y, z)
        end)
    end

    if not HB then return end

    -- Hot Brass alone: each fired casing it places (spawnCasing) and each live round it racks out (rackCasing with
    -- racking = true) brings the link along, placed the same way
    local spawnCasing = HB.spawnCasing
    if spawnCasing and not wrapped[spawnCasing] then
        HB.spawnCasing = wrap(function(player, weapon)
            follow = BeltLinks.linkForGun(weapon)
            spawnCasing(player, weapon)
            follow = nil
        end)
    end
    local rackCasing = HB.rackCasing
    if rackCasing and not wrapped[rackCasing] then
        HB.rackCasing = wrap(function(player, weapon, racking)
            follow = racking == true and BeltLinks.linkForGun(weapon) or nil
            rackCasing(player, weapon, racking)
            follow = nil
        end)
    end
    local addCasing = HB.addCasing
    if addCasing and not wrapped[addCasing] then
        HB.addCasing = wrap(function(params)
            addCasing(params)
            local link = follow
            if link and params then
                follow = nil
                HB.doSpawnCasing(params.player, params.weapon, BeltLinks.EJECT[link], false, link, params.ignoreDespawn)
            end
        end)
    end
    local addCasingToVehicle = HB.addCasingToVehicle
    if addCasingToVehicle and not wrapped[addCasingToVehicle] then
        HB.addCasingToVehicle = wrap(function(vehicle, player, item)
            addCasingToVehicle(vehicle, player, item)
            local link = follow
            if link then
                follow = nil
                addCasingToVehicle(vehicle, player, link)
            end
        end)
    end
    -- a link thrown by Hot Brass for Ammo Maker flies on its own launch values, not the casing's
    local doSpawnCasing = HB.doSpawnCasing
    if doSpawnCasing and not wrapped[doSpawnCasing] then
        HB.doSpawnCasing = wrap(function(player, weapon, params, racking, optionalItem, ignoreDespawn)
            if type(optionalItem) == "string" and BeltLinks.EJECT[optionalItem] then
                params = BeltLinks.EJECT[optionalItem]
            end
            return doSpawnCasing(player, weapon, params, racking, optionalItem, ignoreDespawn)
        end)
    end
end

-------------------------------------------------
-- Racking out into the inventory
-------------------------------------------------
-- Vanilla's removeBullet (Gunworks' wrapper picks the round) is called only when a live round comes out and puts it
-- in the inventory. Hot Brass (no Ammo Maker) replaces rackBullet with nothing and, at every OnInitGlobalModData,
-- removeBullet with one that calls the earlier removeBullet (this one, wrapped at file load) only when the round
-- goes into the inventory: Ammo Maker on, Persistent Casings off, or a gun that keeps its spent rounds. Otherwise it
-- throws the round itself (rackCasing above; with Persistent Casings off it also flies there, for show, beside the
-- round put in the inventory, and so does the link).
require("TimedActions/ISRackFirearm")

if not BeltLinks.removeBulletWrapped then
    BeltLinks.removeBulletWrapped = true

    local removeBullet = ISRackFirearm.removeBullet
    function ISRackFirearm:removeBullet()
        removeBullet(self)
        local link = not isClient() and BeltLinks.linkForGun(self.gun)
        if link then
            BeltLinks.give(self.character, link, 1)
        end
    end
end

if BeltLinks.onClientCommand then Events.OnClientCommand.Remove(BeltLinks.onClientCommand) end
BeltLinks.onClientCommand = onClientCommand
Events.OnClientCommand.Add(onClientCommand)
Events.OnInitGlobalModData.Add(install)
