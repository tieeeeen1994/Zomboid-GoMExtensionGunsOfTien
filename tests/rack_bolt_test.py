"""Runs the real shared/GunsOfTien/GoMFixes.lua with Gunworks' real Animations.lua in a real Lua (lupa) against mocks.

Racks (owner's client, single player). A rack must not leave Gunworks' bolt flag set by ending between its clip's
rackStart and rackEnd (a trigger pull, sprinting, an early server Done):
- a full rack stopped or performed after rackStart: flag cleared, bolt and handle parts back to closed, synced,
  vanilla's stop / perform still runs;
- an opening stroke of a two-stroke rack (gunworksRackPhase "open") stays open, stopped or performed;
- a closing stroke (GoM's AR-15 bolt catch slap after an empty reload) that performs before its rackEnd is closed
  with its own parts (the bolt; the charging handle is not touched); stopped, it is left as it was;
- a rack that never opened the bolt sends nothing;
- a gun that is no longer in the hands is closed without the redraw (no sync, nothing put in the hands).

Trigger pulls (canShoot, not on a server). A flag no closing stroke could clear is cleared first:
- a gun without reload rules (AUG): closed; left alone while a rack / load / unload is running;
- GoM's AR-15: left open while the chamber is empty (its rules answer a rack with the slap), closed once a round
  is chambered;
- a gun without a chamber, a gun whose rules fail, a gun with no flag: untouched.

Shots on a server (onShoot). A shot that newly sets the flag (GoM's LockOpenWeapons.lua) fits the open bolt part
before vanilla's weapon sync leaves; other shots pass through; the swapped syncHandWeaponFields is always put back.

Hold-open (the real shared/GunsOfTien/HoldOpen.lua). A listed rifle firing its chambered round with none left to feed
gets the flag, on a client and on a server (where the sync then carries the open bolt); with rounds left, or a gun
that is not listed, it does not.

Setup once: py -m pip install --target tests/.lupa lupa      Run: py tests/rack_bolt_test.py
Break (each should print FAILED): noclose, noheal, nofit, nohold."""
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parent
sys.path.insert(0, str(here / '.lupa'))
import lupa

GUNWORKS = Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3722064198/mods/'
                'Gunworks_gang_framework/42.13/media/lua/shared/WeaponSystems/Utils/Animations.lua')
if not GUNWORKS.exists():
    GUNWORKS = Path.home() / ('Library/Application Support/Steam/steamapps/workshop/content/108600/3722064198/mods/'
                              'Gunworks_gang_framework/42.13/media/lua/shared/WeaponSystems/Utils/Animations.lua')


def read(path):
    return path.read_bytes().decode('utf-8').replace('\r\n', '\n')


SHARED = repo / 'Contents/mods/GoMExtensionGunsOfTien/42/media/lua/shared/GunsOfTien'
fixes = read(SHARED / 'GoMFixes.lua')
hold = read(SHARED / 'HoldOpen.lua')
mode = sys.argv[1] if len(sys.argv) > 1 else ''
if mode == 'noclose':
    fixes = fixes.replace('closeBolt(self, true)', '').replace('closeBolt(self)', '')
elif mode == 'noheal':
    assert fixes.count('closeNow(player, weapon)') == 1
    fixes = fixes.replace('closeNow(player, weapon)', '')
elif mode == 'nohold':
    assert hold.count('weapon:getModData().gunworksBoltOpen = true') == 1
    hold = hold.replace('weapon:getModData().gunworksBoltOpen = true', '')
elif mode == 'nofit':
    assert fixes.count('Animations.CallAnimationFunction(weapon, true)') == 1
    fixes = fixes.replace('Animations.CallAnimationFunction(weapon, true)', '')

HARNESS = r'''
SERVER = ...
function isServer() return SERVER end
function instanceof(o, class) return type(o) == "table" and o.class == class end
HANDLERS = {}                   -- event name -> list of handlers
Events = setmetatable({}, { __index = function(t, name)
    local list = {}
    HANDLERS[name] = list
    local e = {
        Add = function(fn) list[#list + 1] = fn end,
        Remove = function(fn)
            for i = #list, 1, -1 do if list[i] == fn then table.remove(list, i) end end
        end,
    }
    rawset(t, name, e)
    return e
end })
function getScriptManager() return nil end
SYNCS, SYNC_BOLT = 0, nil
function syncHandWeaponFields(character, gun)
    SYNCS = SYNCS + 1
    SYNC_BOLT = gun.parts.bolt          -- what the owner would receive
end
REAL_SYNC = syncHandWeaponFields
function instanceItem(type) return type end
ENDED = {}
ISRackFirearm = {
    serverStart = function() end,
    stop = function(self) ENDED[#ENDED + 1] = "stop" end,
    perform = function(self) ENDED[#ENDED + 1] = "perform" end,
}
SHOT = nil                      -- what the mocked GoM + vanilla onShoot does: "lock", "plain", "nosync", "error"
ISReloadWeaponAction = {
    setReloadSpeed = function() end,
    canShoot = function(player, weapon) ENDED[#ENDED + 1] = "canShoot" return "inner" end,
    onShoot = function(player, weapon)
        if SHOT == "error" then error("boom") end
        if SHOT == "lock" or SHOT == "nosync" then weapon:getModData().gunworksBoltOpen = true end
        if SHOT ~= "nosync" then syncHandWeaponFields(player, weapon) end
    end,
}
VANILLA_CAN_SHOOT, VANILLA_ON_SHOOT = ISReloadWeaponAction.canShoot, ISReloadWeaponAction.onShoot
Events.OnWeaponSwingHitPoint.Add(ISReloadWeaponAction.onShoot)

package.preload["WeaponSystems/Hooks/ReloadAnimHooks"] = function() return {} end
package.preload["TimedActions/ISReloadWeaponAction"] = function() return true end
package.preload["GunsOfTien/HoldOpen"] = function() return HOLD_CHUNK() end
package.preload["WeaponSystems/Utils/Animations"] = function() return ANIMATIONS_CHUNK() end
-- Gunworks' rules, as far as the fix asks them: GoM's "boltCatchAfterEmptyInsert" on its AR-15s
RULES = {
    ["MarzGuns.M16A2"] = function(ctx)
        if ctx.boltOpen and not ctx.chambered and not ctx.jammed then return { "close" } end
    end,
    ["Test.Broken"] = function() error("rule failed") end,
}
package.preload["WeaponSystems/Utils/ReloadAnim"] = function()
    return { GetHandlerForGun = function(gun)
        local rule = RULES[gun:getFullType()]
        return rule and { rule = rule }
    end }
end
package.preload["WeaponSystems/ReloadAnim/Rules"] = function()
    return {
        hasRules = function(handler) return handler ~= nil end,
        buildContext = function(character, gun)
            return { boltOpen = gun.data.gunworksBoltOpen == true, chambered = gun.chambered, jammed = false }
        end,
        evaluate = function(handler, moment, step, ctx)
            assert(moment == "instead" and step == "rack")
            return handler.rule(ctx)
        end,
    }
end

function GUN(fullType)
    local g = { class = "HandWeapon", data = {}, parts = {}, type = fullType, chamber = true, chambered = false,
        rounds = 0 }
    function g:isRoundChambered() return self.chambered end
    function g:getCurrentAmmoCount() return self.rounds end
    function g:getFullType() return self.type end
    function g:getModData() return self.data end
    function g:isTwoHandWeapon() return true end
    function g:haveChamber() return self.chamber end
    function g:attachWeaponPart(part) self.parts[part:match("Bolt") and "bolt" or "handle"] = part end
    return g
end
function PLAYER(gun)
    local p = { hand = gun, vars = {} }
    function p:getPrimaryHandItem() return self.hand end
    function p:setPrimaryHandItem(item) self.hand = item end
    function p:setSecondaryHandItem() end
    function p:resetEquippedHandsModels() end
    function p:getVariableBoolean(name) return self.vars[name] == true end
    return p
end
function RACK(player, gun, phase)
    return setmetatable({ character = player, gun = gun, gunworksRackPhase = phase }, { __index = ISRackFirearm })
end
'''

REGISTER = r'''
Animations = require("WeaponSystems/Utils/Animations")
local Bolt = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" }
local AUG = {                                                                  -- ChargingHandle.ANIMATED_PARTS
    SingleAttachment = Bolt,
    reload = { MultipleAttachment = { Bolt = Bolt, ChargingHandle = {
        open = "GunsOfTien.ChargingHandle_Back", locked = "GunsOfTien.ChargingHandle_Forward" } } },
}
for _, gun in ipairs({ "GunsOfTienPost93.AUGHBAR", "Test.Broken", "Test.NoChamber", "GunsOfTien.SR25" }) do
    Animations.RegisterWeaponWithAnimatedParts(gun, AUG)
end
Animations.RegisterWeaponWithAnimatedParts("MarzGuns.M16A2", {                -- GoM's Bolt_AR15
    SingleAttachment = Bolt,
    reload = {
        MultipleAttachment = { Bolt = Bolt, Charging_Handle = {
            open = "MarzGuns.Charging_Handle_Open", locked = "MarzGuns.Charging_Handle_Close" } },
        close = { MultipleAttachment = { Bolt = Bolt } },
    },
})
'''


def runtime(server):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ANIMATIONS_CHUNK = lua.eval('function(src) return load(src, "Animations.lua") end')(read(GUNWORKS))
    lua.globals().HOLD_CHUNK = lua.eval('function(src) return load(src, "HoldOpen.lua") end')(hold)
    lua.eval('function(src) return load(src, "harness") end')(HARNESS)(server)
    lua.eval('function(src) return load(src, "GoMFixes.lua") end')(fixes)()
    lua.execute(REGISTER)
    lua.execute('require("GunsOfTien/HoldOpen").register("GunsOfTien.SR25")')
    return lua


failed = []


def check(name, ok):
    print(('ok      ' if ok else 'FAILED  ') + name)
    if not ok:
        failed.append(name)


AUG, M16, SR25 = 'GunsOfTienPost93.AUGHBAR', 'MarzGuns.M16A2', 'GunsOfTien.SR25'

SHOOT = r'''function(fullType, shot, flagged, chambered, rounds)
    local gun = GUN(fullType)
    local player = PLAYER(gun)
    gun.parts.bolt = "MarzGuns.Bolt_Lock"                   -- the server's copy: never animated
    gun.chambered, gun.rounds = chambered, rounds or 0
    if flagged then gun.data.gunworksBoltOpen = true end
    SHOT, SYNCS, SYNC_BOLT = shot, 0, nil
    local list = HANDLERS.OnWeaponSwingHitPoint
    local ok = pcall(list[1], player, gun)
    return ok, gun.data.gunworksBoltOpen == true, gun.parts.bolt, SYNCS, SYNC_BOLT,
        syncHandWeaponFields == REAL_SYNC, #list == 1 and list[1] == ISReloadWeaponAction.onShoot
            and list[1] ~= VANILLA_ON_SHOOT
end'''
LOCK, FIRED = 'MarzGuns.Bolt_Lock', 'MarzGuns.Bolt_Fired'

# ---------------------------------------------------------------- racks: owner's client / single player
lua = runtime(False)
rack = lua.eval(r'''function(fullType, how, phase, opened, inHand)
    local gun = GUN(fullType)
    local player = PLAYER(gun)
    local action = RACK(player, gun, phase)
    if opened then Animations.rackAction(player, gun, true, phase) end      -- the clip's rackStart
    if not inHand then player.hand = nil end
    SYNCS, ENDED = 0, {}
    action[how](action)
    return gun.data.gunworksBoltOpen == true, gun.parts.bolt, gun.parts.handle, SYNCS, ENDED[1], player.hand == gun
end''')

for how in ('stop', 'perform'):
    is_open, bolt, handle, syncs, ended, held = rack(AUG, how, None, True, True)
    check(f'{how} after rackStart: bolt closed', not is_open and bolt == LOCK
          and handle == 'GunsOfTien.ChargingHandle_Forward' and syncs == 1 and ended == how and held)

for how in ('stop', 'perform'):
    is_open, bolt, handle, syncs, ended, held = rack(AUG, how, 'open', True, True)
    check(f'opening stroke stays open ({how})', is_open and bolt == FIRED and syncs == 0 and ended == how)

is_open, bolt, handle, syncs, ended, held = rack(M16, 'perform', 'close', True, True)
check('closing stroke performed before rackEnd: bolt closed, handle untouched', not is_open and bolt == LOCK
      and handle is None and syncs == 1 and ended == 'perform' and held)
is_open, bolt, handle, syncs, ended, held = rack(M16, 'stop', 'close', True, True)
check('closing stroke stopped: left open', is_open and bolt == FIRED and syncs == 0 and ended == 'stop')
is_open, bolt, handle, syncs, ended, held = rack(M16, 'perform', 'close', False, True)
check('closing stroke that already closed sends nothing', not is_open and syncs == 0 and ended == 'perform')

is_open, bolt, handle, syncs, ended, held = rack(AUG, 'perform', None, False, True)
check('a rack that never opened sends nothing', not is_open and syncs == 0 and bolt is None and ended == 'perform')

is_open, bolt, handle, syncs, ended, held = rack(AUG, 'stop', None, True, False)
check('a gun out of the hands is closed without the redraw', not is_open and bolt == LOCK and syncs == 0
      and not held and ended == 'stop')

# ---------------------------------------------------------------- trigger pulls
pull = lua.eval(r'''function(fullType, flagged, chambered, busy, chamber)
    local gun = GUN(fullType)
    gun.chambered, gun.chamber = chambered, chamber
    local player = PLAYER(gun)
    if flagged then Animations.rackAction(player, gun, true) end
    if busy then player.vars[busy] = true end
    SYNCS, ENDED = 0, {}
    local answer = ISReloadWeaponAction.canShoot(player, gun)
    return gun.data.gunworksBoltOpen == true, gun.parts.bolt, SYNCS, ENDED[1], answer
end''')


def passed_on(ended, answer):
    return ended == 'canShoot' and answer == 'inner'


is_open, bolt, syncs, ended, answer = pull(AUG, True, False, None, True)
check('pull, no rules, empty: stale flag closed', not is_open and bolt == LOCK and syncs == 1
      and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull(AUG, True, True, None, True)
check('pull, no rules, chambered: stale flag closed', not is_open and bolt == LOCK and passed_on(ended, answer))
for busy in ('isRacking', 'isLoading', 'isUnloading'):
    is_open, bolt, syncs, ended, answer = pull(AUG, True, False, busy, True)
    check(f'pull while {busy}: left alone', is_open and bolt == FIRED and syncs == 0 and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull(M16, True, False, None, True)
check('pull, AR-15 held open on an empty chamber: left open', is_open and bolt == FIRED and syncs == 0
      and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull(M16, True, True, None, True)
check('pull, AR-15 flagged with a round chambered: closed', not is_open and bolt == LOCK
      and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull('Test.NoChamber', True, False, None, False)
check('pull, gun without a chamber: left open', is_open and syncs == 0 and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull('Test.Broken', True, True, None, True)
check('pull, rules that fail: left open', is_open and syncs == 0 and passed_on(ended, answer))
is_open, bolt, syncs, ended, answer = pull(AUG, False, True, None, True)
check('pull, no flag: nothing sent', not is_open and bolt is None and syncs == 0 and passed_on(ended, answer))

# ---------------------------------------------------------------- hold-open, owner's client / single player
shoot = lua.eval(SHOOT)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(SR25, 'plain', False, True, 0)
check('client, listed rifle, last round: held open', ok and is_open and syncs == 1 and hooked)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(SR25, 'plain', False, True, 3)
check('client, listed rifle, rounds left: not held', ok and not is_open and syncs == 1)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(SR25, 'plain', False, False, 0)
check('client, listed rifle, nothing chambered: not held', ok and not is_open)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(AUG, 'plain', False, True, 0)
check('client, rifle not listed, last round: not held', ok and not is_open and bolt == LOCK)

# ---------------------------------------------------------------- shots on a server
lua = runtime(True)
shoot = lua.eval(SHOOT)

ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(M16, 'lock', False)
check('server, last round: the sync carries the open bolt', ok and is_open and sync_bolt == FIRED and syncs == 1
      and restored and hooked)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(M16, 'plain', False)
check('server, any other shot: untouched', ok and not is_open and sync_bolt == LOCK and syncs == 1 and restored)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(M16, 'plain', True)
check('server, already held open: passed through', ok and is_open and bolt == LOCK and syncs == 1 and restored)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(M16, 'nosync', False)
check('server, flagged without a sync: bolt part still fitted', ok and is_open and bolt == FIRED and syncs == 0
      and restored)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(M16, 'error', False)
check('server, onShoot fails: the error passes, the sync function is put back', not ok and restored)
check('server: canShoot is not wrapped', lua.eval('ISReloadWeaponAction.canShoot == VANILLA_CAN_SHOOT'))
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(SR25, 'plain', False, True, 0)
check('server, listed rifle, last round: held open and the sync carries the open bolt', ok and is_open
      and sync_bolt == FIRED and syncs == 1 and restored)
ok, is_open, bolt, syncs, sync_bolt, restored, hooked = shoot(SR25, 'plain', False, True, 3)
check('server, listed rifle, rounds left: untouched', ok and not is_open and sync_bolt == LOCK and restored)

print('FAILED' if failed else 'all pass')
sys.exit(1 if failed else 0)
