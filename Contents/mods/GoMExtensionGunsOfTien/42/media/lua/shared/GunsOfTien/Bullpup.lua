--[[
    Guns of Tien -- the bullpup set (docs/design.md 4h; user, 2026-10-27: "we now need a bullpup animation set", for
    the AUG A1 and Guns of Marz's FAMAS, reload included).

    Hold: vanilla's rifle clips put the left palm ~0.22 ahead of the grip, an M16's handguard: on the AUG that is its
    bare barrel near the flash hider, on the FAMAS the tip of its handguard. scripts/anim/rifle_hand.py "Bullpup"
    builds every rifle clip in which the left hand holds the gun with the palm moved back to 0.72 of vanilla's place
    (~0.15 ahead: under the FAMAS's handguard and on the AUG's folded grip, which lie in the same place; with the
    AUG's grip unfolded the hand stays there, user's choice), and the gun moved 0.02 forward along its length, the
    right arm following (user: aiming left the AUG's scope eyepiece against the face). Packed as
    anims_X/Bob/GunsOfTien_CompactBullpup_Pack*.x, nodes AnimSets *_GoTCompactBullpup.xml, played through Gunworks' grip
    registry (animId "GunsOfTien_CompactBullpup") as the UMPs' and the compact stance's are.

    Reload: GoM's way (user: no magazine in the hand; Gunworks' "none" style, the magazine swapped when the action
    ends), clips of our own (scripts/anim/smg_reload.py `aug` / `famas`; GoM's FAMAS clips are glTF from another rig),
    one set of four per gun because their wells sit 2 cm apart in height and their handles differ (user: "famas and
    AUG have different racking positions"): the AUG's left hand to its handle on the left ahead of the scope, the
    FAMAS's to the lever under its carry handle. Packed with the hold set, nodes *GunsOfTienCompactBullpupAUG_GoT.xml /
    *BullpupFAMAS_GoT.xml. This replaces GoM's own FAMAS reload registration (this file loads after GoM's).
--]]

local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
pcall(require, "MarzWeapons/Registries/ReloadAnims")

local GUNS = { ["GunsOfTien.AUG"] = "AUG", ["MarzGuns.FAMAS"] = "FAMAS" }

-- smg_reload.py's lengths at 30 fps: unload 36 frames, load 45, rack / aimed rack 36
for gun, name in pairs(GUNS) do
    ReloadAnim.RegisterWeapon(gun, {
        animId = "GunsOfTienCompactBullpup" .. name,
        style = "none",
        durations = { unload = 1.2, load = 1.5, rack = 1.2, rackAim = 1.2 },
    })
end

local okGW, Gunworks = pcall(require, "WeaponSystems/Gunworks")
local function registerGrip()
    if not okGW or type(Gunworks) ~= "table" or not Gunworks.RegisterWeapon then
        return
    end
    for gun in pairs(GUNS) do
        Gunworks.RegisterWeapon(gun, { grip = { animId = "GunsOfTien_CompactBullpup" } })
    end
end
Events.OnGameBoot.Add(registerGrip)
