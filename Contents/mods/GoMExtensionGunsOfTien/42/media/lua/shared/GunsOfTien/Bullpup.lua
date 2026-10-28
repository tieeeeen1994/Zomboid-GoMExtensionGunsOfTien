--[[
    Guns of Tien -- the bullpup set (docs/design.md 4h; user, 2026-10-27: "we now need a bullpup animation set", for
    the AUG A1 and Guns of Marz's FAMAS, reload included).

    Hold (2026-10-28, scripts/anim/bullpup_stance.py draft B, user: "B looks good. implement B"): a tucked carry, the
    butt pinned behind the right upper arm, the gun along the right forearm 25 degrees down and across to the left,
    built on every vanilla clip played with a gun by scripts/anim/compact_build.py "Bullpup" (as the short SMG stance).
    Aiming keeps the set's earlier aims (scripts/anim/rifle_hand.py: vanilla's rifle aim, the gun pushed forward off
    the face); raising and lowering move the gun on a straight path between the two. The left palm sits 0.72 of
    vanilla's distance ahead of the grip (~0.15: under the FAMAS's handguard and on the AUG's folded grip, which lie
    in the same place; with the AUG's grip unfolded the hand stays there, user's choice). Packed as
    anims_X/Bob/GunsOfTien_CompactBullpup_Pack*.x, nodes AnimSets *_GoTCompactBullpup.xml, played through Gunworks' grip
    registry (animId "GunsOfTien_CompactBullpup") as the UMPs' and the compact stance's are.

    Reload: GoM's way (user: no magazine in the hand; Gunworks' "none" style, the magazine swapped when the action
    ends), one bullpup family for every bullpup (user, 2026-10-28; CLAUDE.md "Animations are generic"): the clips
    built for the AUG (scripts/anim/smg_reload.py `aug`: the magazine behind the grip, the left hand to the handle on
    the left ahead of the scope), so the FAMAS's well sits 2 cm off and its lever under the carry handle is racked
    from the side. Packed with the hold set (GunsOfTien_CompactBullpup_Reload*), nodes
    *GunsOfTienCompactBullpup_GoT.xml, animId "GunsOfTienCompactBullpup". (A FAMAS set of its own shipped until
    2026-10-28.) This replaces GoM's own FAMAS reload registration (this file loads after GoM's).
--]]

local ReloadAnim = require("WeaponSystems/ReloadAnim/HandlerFactory")
pcall(require, "MarzWeapons/Registries/ReloadAnims")

local GUNS = { ["GunsOfTien.AUG"] = true, ["MarzGuns.FAMAS"] = true }

-- smg_reload.py's lengths at 30 fps: unload 36 frames, load 45, rack / aimed rack 36
for gun in pairs(GUNS) do
    ReloadAnim.RegisterWeapon(gun, {
        animId = "GunsOfTienCompactBullpup",
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
