"""Runs the real shared/GunsOfTien/GoMFixes.lua with Gunworks' real Animations.lua in a real Lua (lupa) against mocks.

A full rack that ends between its clip's rackStart and rackEnd (a trigger pull, sprinting, an early server Done)
must not leave Gunworks' bolt flag set:
- stopped after rackStart: flag cleared, bolt and handle parts back to closed, synced, vanilla's stop still runs;
- performed after rackStart (the server's Done before rackEnd): the same;
- an opening stroke of a two-stroke rack (gunworksRackPhase) stays open;
- a rack that never opened the bolt sends nothing;
- a gun that is no longer in the hands is left alone.

Setup once: py -m pip install --target tests/.lupa lupa      Run: py tests/rack_bolt_test.py
Break (should print FAILED): noclose."""
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


fixes = read(repo / 'Contents/mods/GoMExtensionGunsOfTien/42/media/lua/shared/GunsOfTien/GoMFixes.lua')
if len(sys.argv) > 1 and sys.argv[1] == 'noclose':
    fixes = fixes.replace('closeBolt(self)', '')

HARNESS = r'''
Events = setmetatable({}, { __index = function() return { Add = function() end } end })
function getScriptManager() return nil end
SYNCS = 0
function syncHandWeaponFields() SYNCS = SYNCS + 1 end
function instanceItem(type) return type end
ENDED = {}
ISRackFirearm = {
    serverStart = function() end,
    stop = function(self) ENDED[#ENDED + 1] = "stop" end,
    perform = function(self) ENDED[#ENDED + 1] = "perform" end,
}
ISReloadWeaponAction = { setReloadSpeed = function() end }
package.preload["WeaponSystems/Hooks/ReloadAnimHooks"] = function() return {} end
package.preload["WeaponSystems/Utils/Animations"] = function() return ANIMATIONS_CHUNK() end

function GUN()
    local g = { data = {}, parts = {} }
    function g:getFullType() return "GunsOfTienPost93.AUGHBAR" end
    function g:getModData() return self.data end
    function g:isTwoHandWeapon() return true end
    function g:attachWeaponPart(part) self.parts[part:match("Bolt") and "bolt" or "handle"] = part end
    return g
end
function PLAYER(gun)
    local p = { hand = gun }
    function p:getPrimaryHandItem() return self.hand end
    function p:setPrimaryHandItem(item) self.hand = item end
    function p:setSecondaryHandItem() end
    function p:resetEquippedHandsModels() end
    return p
end
function RACK(player, gun, phase)
    return setmetatable({ character = player, gun = gun, gunworksRackPhase = phase }, { __index = ISRackFirearm })
end
'''

lua = lupa.LuaRuntime(unpack_returned_tuples=True)
lua.globals().ANIMATIONS_CHUNK = lua.eval('function(src) return load(src, "Animations.lua") end')(read(GUNWORKS))
lua.execute(HARNESS)
lua.eval('function(src) return load(src, "GoMFixes.lua") end')(fixes)()
lua.execute(r'''
Animations = require("WeaponSystems/Utils/Animations")
local Bolt = { open = "MarzGuns.Bolt_Fired", locked = "MarzGuns.Bolt_Lock" }
Animations.RegisterWeaponWithAnimatedParts("GunsOfTienPost93.AUGHBAR", {      -- ChargingHandle.ANIMATED_PARTS
    SingleAttachment = Bolt,
    reload = { MultipleAttachment = { Bolt = Bolt, ChargingHandle = {
        open = "GunsOfTien.ChargingHandle_Back", locked = "GunsOfTien.ChargingHandle_Forward" } } },
})
''')

failed = []


def check(name, ok):
    print(('ok      ' if ok else 'FAILED  ') + name)
    if not ok:
        failed.append(name)


run = lua.eval(r'''function(how, phase, opened, inHand)
    local gun = GUN()
    local player = PLAYER(gun)
    local action = RACK(player, gun, phase)
    if opened then Animations.rackAction(player, gun, true, phase) end      -- the clip's rackStart
    if not inHand then player.hand = nil end
    SYNCS, ENDED = 0, {}
    action[how](action)
    return gun.data.gunworksBoltOpen == true, gun.parts.bolt, gun.parts.handle, SYNCS, ENDED[1], player.hand == gun
end''')

for how in ('stop', 'perform'):
    is_open, bolt, handle, syncs, ended, held = run(how, None, True, True)
    check(f'{how} after rackStart: bolt closed', not is_open and bolt == 'MarzGuns.Bolt_Lock'
          and handle == 'GunsOfTien.ChargingHandle_Forward' and syncs == 1 and ended == how and held)

is_open, bolt, handle, syncs, ended, held = run('stop', 'open', True, True)
check('opening stroke stays open', is_open and bolt == 'MarzGuns.Bolt_Fired' and syncs == 0 and ended == 'stop')

is_open, bolt, handle, syncs, ended, held = run('perform', None, False, True)
check('a rack that never opened sends nothing', not is_open and syncs == 0 and bolt is None and ended == 'perform')

is_open, bolt, handle, syncs, ended, held = run('stop', None, True, False)
check('a gun out of the hands is left alone', is_open and syncs == 0 and not held and ended == 'stop')

print('FAILED' if failed else 'all pass')
sys.exit(1 if failed else 0)
