"""Runs the real server/GunsOfTien/RemovedParts.lua in a real Lua (lupa) against mocks.

- A chunk loads with an M4A1 (bipod and foregrip fitted) in a crate, a G36C with a bipod inside a bag in that crate,
  and an XM177 with a folded bipod lying on the floor: each bipod comes off and lies beside its gun (crate, bag, the
  floor square at the gun's offsets, not transmitted); the foregrip and the M16A2's bipod (still allowed) stay.
- Single player: the local player's inventory is checked once, 10 s after it is first seen, not before; a second
  poll changes nothing.
- On a server: the owner gets syncHandWeaponFields and sendAddItemToContainer; a vehicle's container gets
  sendReplaceItemInContainer and sendAddItemToContainer.

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
function isClient() return false end
function isServer() return SERVER end
SENT = {}
function syncHandWeaponFields(p, gun) SENT[#SENT + 1] = "sync " .. gun.type end
function sendAddItemToContainer(c, item) SENT[#SENT + 1] = "add " .. item.type .. " to " .. c.name end
function sendReplaceItemInContainer(c, a, b) SENT[#SENT + 1] = "replace " .. a.type .. " in " .. c.name end
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

local nextId = 1
function PART(type) nextId = nextId + 1 return { class = "WeaponPart", type = type, id = nextId,
    getFullType = function(self) return self.type end } end

function GUN(type, parts)
    nextId = nextId + 1
    local g = { class = "HandWeapon", type = type, parts = parts, id = nextId }
    function g:getFullType() return self.type end
    function g:getID() return self.id end
    function g:getAllWeaponParts() return list({ unpack(self.parts) }) end
    function g:detachWeaponPart(p) for i, q in ipairs(self.parts) do if q == p then table.remove(self.parts, i) return end end end
    function g:getWorldItem() return self.worldItem end
    function g:getContainer() return self.container end
    return g
end

function Container(name)
    local c = { name = name, items = {} }
    function c:AddItem(item) table.insert(self.items, item) item.container = self return item end
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

print("%d failed" % failed if failed else "all passed")
sys.exit(1 if failed else 0)
