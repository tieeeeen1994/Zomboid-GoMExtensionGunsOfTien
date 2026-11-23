"""Runs the real server/GunsOfTien/RemovedParts.lua in a real Lua (lupa) against mocks.

- A chunk loads with an M4A1 (bipod and foregrip fitted) in a crate, a G36C with a bipod inside a bag in that crate,
  and an XM177 with a folded bipod lying on the floor: each bipod comes off and lies beside its gun (crate, bag, the
  floor square at the gun's offsets, not transmitted); the foregrip and the M16A2's bipod (still allowed) stay.
- Single player: the local player's inventory is checked once, 10 s after it is first seen, not before; a second
  poll changes nothing.
- On a server: the owner gets syncHandWeaponFields and sendAddItemToContainer; a vehicle's container gets
  sendReplaceItemInContainer and sendAddItemToContainer.
- Sandbox option UpdateSavedParts off: a chunk load and a new player change nothing.
- Replaced parts (the main mod's old 9x19mm SMG mount device -> GoM's 9mm mount): on a chunk load the old mount on a
  Glock 17 in a crate and on an Uzi in a bag is swapped (the Uzi's Mk9 stays), a loose one in the crate and one on
  the floor (same offsets, not transmitted) too, a gun its MountOn does not name is left alone, nothing is sent; on
  a server a player's loose one is removed and its replacement added, and the MP5 carrying one is synced.

Setup once: py -m pip install --target tests/.lupa lupa      Run: py tests/removed_parts_test.py
"""
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parent
sys.path.insert(0, str(here / '.lupa'))
import lupa

SRC = (repo / 'Contents/mods/GoMExtensionGunsOfTien/42/media/lua/server/GunsOfTien/RemovedParts.lua').read_bytes()
SRC = SRC.decode('utf-8').replace('\r\n', '\n')

HARNESS = r'''
local now = 0
function getTimestampMs() return now end
function ADVANCE(ms) now = now + ms end
SERVER = false
SandboxVars = { GunsOfTien = { UpdateSavedParts = true } }
function isClient() return false end
function isServer() return SERVER end
SENT = {}
function syncHandWeaponFields(p, gun) SENT[#SENT + 1] = "sync " .. gun.type end
function sendAddItemToContainer(c, item) SENT[#SENT + 1] = "add " .. item.type .. " to " .. c.name end
function sendReplaceItemInContainer(c, a, b) SENT[#SENT + 1] = "replace " .. a.type .. " in " .. c.name end
function sendRemoveItemFromContainer(c, item) SENT[#SENT + 1] = "remove " .. item.type .. " from " .. c.name end
MOUNTON = {}        -- part type -> the gun types its MountOn names
function instanceItem(type)
    local p = PART(type)
    function p:getMountOn() return MOUNTON[type] and LIST(MOUNTON[type]) or nil end
    return p
end
function instanceof(o, c) return type(o) == "table" and o.class == c end
package.preload["WeaponSystems/Utils/StatsFactory"] = function()
    return { ReapplyAllModifiers = function(gun) gun.reapplied = (gun.reapplied or 0) + 1 end }
end
local handlers = {}
Events = setmetatable({}, { __index = function(_, name)
    handlers[name] = handlers[name] or {}
    return { Add = function(f) table.insert(handlers[name], f) end }
end })
function FIRE(name, ...) for _, f in ipairs(handlers[name] or {}) do f(...) end end

local function list(t)
    local o = { t = t }
    function o:size() return #self.t end
    function o:get(i) return self.t[i + 1] end
    function o:isEmpty() return #self.t == 0 end
    function o:addAll(other) for i = 0, other:size() - 1 do table.insert(self.t, other:get(i)) end end
    return o
end
ArrayList = { new = function() return list({}) end }
LIST = list

local nextId = 1
function PART(type) nextId = nextId + 1 return { class = "WeaponPart", type = type, id = nextId,
    getFullType = function(self) return self.type end, getID = function(self) return self.id end,
    getContainer = function(self) return self.container end } end

function GUN(type, parts)
    nextId = nextId + 1
    local g = { class = "HandWeapon", type = type, parts = parts, id = nextId }
    function g:getFullType() return self.type end
    function g:getID() return self.id end
    function g:getAllWeaponParts() return list({ unpack(self.parts) }) end
    function g:detachWeaponPart(p) for i, q in ipairs(self.parts) do if q == p then table.remove(self.parts, i) return end end end
    function g:attachWeaponPart(p) table.insert(self.parts, p) end
    function g:getWorldItem() return self.worldItem end
    function g:getContainer() return self.container end
    return g
end

function Container(name)
    local c = { name = name, items = {} }
    function c:AddItem(item) table.insert(self.items, item) item.container = self return item end
    function c:DoRemoveItem(item)
        for i, it in ipairs(self.items) do if it == item then table.remove(self.items, i) item.container = nil return end end
    end
    function c:getItems() return list(self.items) end
    function c:getContainingItem() return self.bag end
    function c:getSourceGrid() return self.square end
    function c:getCharacter() return self.character end
    function c:getAllTypeRecurse(t)
        local out = {}
        local function walk(cont)
            for _, it in ipairs(cont.items) do
                if it.type == t then out[#out + 1] = it end
                if it.inventory then walk(it.inventory) end
            end
        end
        walk(self)
        return list(out)
    end
    function c:containsTypeRecurse(t) return self:getAllTypeRecurse(t):size() > 0 end
    return c
end

function BAG(name)
    local bag = { class = "InventoryContainer", type = "Base.Bag_Schoolbag" }
    bag.inventory = Container(name)
    bag.inventory.bag = bag
    function bag:getInventory() return self.inventory end
    function bag:getFullType() return self.type end
    function bag:getContainer() return self.container end
    return bag
end

function SQUARE(x, y, z)
    local s = { x = x, y = y, z = z, objects = {}, worldObjects = {}, bodies = {}, floor = {} }
    function s:getX() return self.x end
    function s:getY() return self.y end
    function s:getZ() return self.z end
    function s:getObjects() return list(self.objects) end
    function s:getWorldObjects() return list(self.worldObjects) end
    function s:getDeadBodys() return list(self.bodies) end
    function s:removeWorldObject(w)
        for i, o in ipairs(self.worldObjects) do if o == w then table.remove(self.worldObjects, i) return end end
    end
    function s:AddWorldInventoryItem(item, ox, oy, oz, transmit)
        table.insert(self.floor, { item = item, ox = ox, oy = oy, oz = oz, transmit = transmit })
        return item
    end
    return s
end

function OBJECT(containers)
    local o = { containers = containers }
    function o:getContainerCount() return #self.containers end
    function o:getContainerByIndex(i) return self.containers[i + 1] end
    return o
end

function WORLDITEM(square, item, ox, oy, oz)
    local w = { item = item, square = square, ox = ox, oy = oy, oz = oz }
    function w:getItem() return self.item end
    function w:getSquare() return self.square end
    function w:getOffX() return self.ox end
    function w:getOffY() return self.oy end
    function w:getOffZ() return self.oz end
    item.worldItem = w
    table.insert(square.worldObjects, w)
    return w
end

function CHUNK(squares)
    local c = { squares = squares }
    function c:getMinLevel() return 0 end
    function c:getMaxLevel() return 0 end
    function c:getGridSquare(x, y, z) return self.squares[x .. "," .. y] end
    return c
end

PLAYERS = {}
function getOnlinePlayers() return list(PLAYERS) end
function getNumActivePlayers() return #PLAYERS end
function getSpecificPlayer(i) return PLAYERS[i + 1] end
VEHICLES = {}
function getCell() return { getVehicles = function() return list(VEHICLES) end } end

local BIPODS = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
GunsOfTien_RemovedParts = { ["MarzGuns.M4A1"] = BIPODS, ["MarzGuns.G36C"] = BIPODS, ["MarzGuns.XM177"] = BIPODS }
'''

failed = 0


def check(name, ok):
    global failed
    print(("ok      " if ok else "FAILED  ") + name)
    if not ok:
        failed += 1


lua = lupa.LuaRuntime(unpack_returned_tuples=True)
lua.execute("unpack = unpack or table.unpack\n" + HARNESS)
lua.execute(SRC)

# --- a chunk loads
lua.execute(r'''
crate = Container("crate")
sq = SQUARE(10, 20, 0)
sq.objects = { OBJECT({ crate }) }
m4 = GUN("MarzGuns.M4A1", { PART("MarzGuns.Bipod_Deployed"), PART("MarzGuns.Stub_Foregrip") })
crate:AddItem(m4)
m16 = GUN("MarzGuns.M16A2", { PART("MarzGuns.Bipod_Deployed") })
crate:AddItem(m16)
bag = BAG("bag")
crate:AddItem(bag)
g36c = GUN("MarzGuns.G36C", { PART("MarzGuns.Bipod_Folded") })
bag.inventory:AddItem(g36c)
xm = GUN("MarzGuns.XM177", { PART("MarzGuns.Bipod_Folded") })
WORLDITEM(sq, xm, 0.3, 0.6, 0.1)
FIRE("LoadChunk", CHUNK({ ["0,0"] = sq }))
''')
check("M4A1: bipod off, foregrip stays", lua.eval('#m4.parts == 1 and m4.parts[1].type == "MarzGuns.Stub_Foregrip"'))
check("M4A1: bipod beside it in the crate", lua.eval('crate.items[#crate.items].type == "MarzGuns.Bipod_Deployed"'))
check("M4A1: stats re-applied", lua.eval('m4.reapplied == 1'))
check("M16A2: bipod stays (still allowed)", lua.eval('#m16.parts == 1'))
check("G36C in a bag: bipod into the bag", lua.eval(
    '#g36c.parts == 0 and bag.inventory.items[#bag.inventory.items].type == "MarzGuns.Bipod_Folded"'))
check("XM177 on the floor: bipod on its square at its offsets, not transmitted", lua.eval(
    '#xm.parts == 0 and #sq.floor == 1 and sq.floor[1].item.type == "MarzGuns.Bipod_Folded" and '
    'sq.floor[1].ox == 0.3 and sq.floor[1].oy == 0.6 and sq.floor[1].oz == 0.1 and sq.floor[1].transmit == false'))
check("chunk load sends nothing", lua.eval('#SENT == 0'))

# --- single player: the local player, 10 s after first seen
lua.execute(r'''
inv = Container("inventory")
player = { getInventory = function() return inv end, getUsername = function() return "p" end }
inv.character = player
PLAYERS = { player }
mine = GUN("MarzGuns.MP5", { PART("MarzGuns.Bipod_Deployed") })
GunsOfTien_RemovedParts["MarzGuns.MP5"] = { "MarzGuns.Bipod_Deployed", "MarzGuns.Bipod_Folded" }
inv:AddItem(mine)
ADVANCE(6000) FIRE("OnTick")
''')
check("player not checked on first sight", lua.eval('#mine.parts == 1'))
lua.execute('ADVANCE(6000) FIRE("OnTick")')
check("player not checked before 10 s", lua.eval('#mine.parts == 1'))
lua.execute('ADVANCE(6000) FIRE("OnTick")')
check("player checked after 10 s", lua.eval('#mine.parts == 0 and inv.items[#inv.items].type == "MarzGuns.Bipod_Deployed"'))
check("single player sends nothing", lua.eval('#SENT == 0'))

# --- server: a new player and a vehicle
lua.execute(r'''
SERVER = true
inv2 = Container("inventory2")
player2 = { getInventory = function() return inv2 end, getUsername = function() return "p2" end }
inv2.character = player2
PLAYERS = { player, player2 }
held = GUN("MarzGuns.MP5", { PART("MarzGuns.Bipod_Folded") })
inv2:AddItem(held)
trunk = Container("trunk")
car = { getPartCount = function() return 1 end,
        getPartByIndex = function() return { getItemContainer = function() return trunk end } end }
VEHICLES = { car }
inTrunk = GUN("MarzGuns.M4A1", { PART("MarzGuns.Bipod_Deployed") })
trunk:AddItem(inTrunk)
ADVANCE(6000) FIRE("OnTick")
ADVANCE(11000) FIRE("OnTick")
''')
check("server: the player's gun synced and its part sent",
      lua.eval('#held.parts == 0') and 'sync MarzGuns.MP5' in list(lua.eval('SENT').values())
      and 'add MarzGuns.Bipod_Folded to inventory2' in list(lua.eval('SENT').values()))
check("server: the vehicle's gun re-sent and its part sent",
      lua.eval('#inTrunk.parts == 0') and 'replace MarzGuns.M4A1 in trunk' in list(lua.eval('SENT').values())
      and 'add MarzGuns.Bipod_Deployed to trunk' in list(lua.eval('SENT').values()))
n = len(list(lua.eval('SENT').values()))
lua.execute('ADVANCE(6000) FIRE("OnTick")')
check("a second poll changes nothing", len(list(lua.eval('SENT').values())) == n)

# --- the option off: nothing is touched
lua.execute(r'''
SandboxVars.GunsOfTien.UpdateSavedParts = false
SENT = {}
crateOff = Container("crateOff")
sqOff = SQUARE(50, 60, 0)
sqOff.objects = { OBJECT({ crateOff }) }
m4Off = GUN("MarzGuns.M4A1", { PART("MarzGuns.Bipod_Deployed") })
crateOff:AddItem(m4Off)
FIRE("LoadChunk", CHUNK({ ["0,0"] = sqOff }))
invOff = Container("inventoryOff")
playerOff = { getInventory = function() return invOff end, getUsername = function() return "off" end }
invOff.character = playerOff
PLAYERS = { player, player2, playerOff }
gunOff = GUN("MarzGuns.MP5", { PART("MarzGuns.Bipod_Folded") })
invOff:AddItem(gunOff)
ADVANCE(6000) FIRE("OnTick")
ADVANCE(11000) FIRE("OnTick")
''')
check("option off: a loading chunk's gun keeps its part", lua.eval('#m4Off.parts == 1 and #crateOff.items == 1'))
check("option off: a player's gun keeps its part, nothing sent", lua.eval('#gunOff.parts == 1 and #SENT == 0'))
lua.execute('SandboxVars.GunsOfTien.UpdateSavedParts = true PLAYERS = { player, player2 }')

# --- replaced parts: the old 9mm mount becomes GoM's
OLD = "GunsOfTien.SMG9_Muzzle_Mount_Device"
NEW = "MarzGuns.Pistol_Muzzle_Mount_Device"
lua.execute(r'''
SERVER = false
SENT = {}
GunsOfTien_ReplacedParts = { ["GunsOfTien.SMG9_Muzzle_Mount_Device"] = "MarzGuns.Pistol_Muzzle_Mount_Device" }
MOUNTON["GunsOfTien.SMG9_Muzzle_Mount_Device"] = { "MarzGuns.GLOCK17", "GunsOfTien.UZI", "MarzGuns.MP5" }
crate2 = Container("crate2")
sq2 = SQUARE(30, 40, 0)
sq2.objects = { OBJECT({ crate2 }) }
glock = GUN("MarzGuns.GLOCK17", { PART("GunsOfTien.SMG9_Muzzle_Mount_Device") })
crate2:AddItem(glock)
looseOld = crate2:AddItem(PART("GunsOfTien.SMG9_Muzzle_Mount_Device"))
other = GUN("MarzGuns.AK47", { PART("GunsOfTien.SMG9_Muzzle_Mount_Device") })    -- not in its MountOn: untouched
crate2:AddItem(other)
bag2 = BAG("bag2")
crate2:AddItem(bag2)
uzi = GUN("GunsOfTien.UZI", { PART("GunsOfTien.SMG9_Muzzle_Mount_Device"), PART("GunsOfTien.Mk9_Suppressor") })
bag2.inventory:AddItem(uzi)
floorOld = PART("GunsOfTien.SMG9_Muzzle_Mount_Device")
WORLDITEM(sq2, floorOld, 0.2, 0.4, 0.0)
FIRE("LoadChunk", CHUNK({ ["0,0"] = sq2 }))
function types(t) local o = {} for _, p in ipairs(t) do o[#o + 1] = p.type end table.sort(o) return table.concat(o, ",") end
''')
check("replaced: the Glock's old mount swapped for GoM's", lua.eval('types(glock.parts)') == NEW)
check("replaced: the Uzi's old mount swapped, its Mk9 stays",
      lua.eval('types(uzi.parts)') == "GunsOfTien.Mk9_Suppressor," + NEW)
check("replaced: guns re-applied", lua.eval('glock.reapplied == 1 and uzi.reapplied == 1'))
check("replaced: a gun its MountOn does not name is left alone", lua.eval('types(other.parts)') == OLD)
check("replaced: the loose one in the crate swapped in the crate",
      lua.eval('looseOld.container == nil') and NEW in lua.eval('types(crate2.items)').split(',')
      and OLD not in lua.eval('types(crate2.items)').split(','))
check("replaced: the one on the floor swapped at its offsets, not transmitted", lua.eval(
    '#sq2.worldObjects == 0 and #sq2.floor == 1 and sq2.floor[1].item.type == "MarzGuns.Pistol_Muzzle_Mount_Device" '
    'and sq2.floor[1].ox == 0.2 and sq2.floor[1].oy == 0.4 and sq2.floor[1].transmit == false'))
check("replaced: chunk load sends nothing", lua.eval('#SENT == 0'))

lua.execute(r'''
SERVER = true
inv3 = Container("inventory3")
player3 = { getInventory = function() return inv3 end, getUsername = function() return "p3" end }
inv3.character = player3
PLAYERS = { player, player2, player3 }
mp5 = GUN("MarzGuns.MP5", { PART("GunsOfTien.SMG9_Muzzle_Mount_Device") })
inv3:AddItem(mp5)
carried = inv3:AddItem(PART("GunsOfTien.SMG9_Muzzle_Mount_Device"))
ADVANCE(6000) FIRE("OnTick")
ADVANCE(11000) FIRE("OnTick")
''')
sent = list(lua.eval('SENT').values())
check("replaced, server: the player's MP5 swapped and synced",
      lua.eval('types(mp5.parts)') == NEW and 'sync MarzGuns.MP5' in sent)
check("replaced, server: the player's loose one removed and its replacement sent",
      lua.eval('carried.container == nil') and 'remove ' + OLD + ' from inventory3' in sent
      and 'add ' + NEW + ' to inventory3' in sent)

print("%d failed" % failed if failed else "all passed")
sys.exit(1 if failed else 0)
