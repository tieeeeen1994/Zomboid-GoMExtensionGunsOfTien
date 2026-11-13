--[[
    Guns of Tien - Post-93 -- the iron sights follow the optic (user, 2026-11-13; CLAUDE.md "Iron sights under
    optics").

    Every gun of both mods that takes an optic was gone through. The ones with flip-up iron sights show them as the
    real gun would under what is in their Scope slot, through Gunworks' ConditionalModel (a StatsFactory layer that
    sets the gun's WeaponSprite on every ReapplyAllModifiers: equip, attach, detach, load; the sprite is saved per
    gun). Each state is a model of its own with the gun's points (gen_post93_guns.py `SIGHT_STATES`, meshes from
    scripts/post93/build_sight_states.py and, for the HK416, build_hk416.py):
    - no optic: both sights up (the gun's own model);
    - a red dot or holographic sight (no magnification), `_RD`: the rear folded, the front seen through the optic;
    - a magnified scope, `_FD`: both folded;
    - `_RDX` / `_FDX`: the same with the rear sight taken off the rail, for the optics whose mount sits on its spot
      (measured: the Elcan and the TR06X on the SCAR-L; the Kobra, the Elcan and the TR06X on the HK416).
    Guns: MP7A1, MP7A2, SCAR-L, SCAR-H, the four Vectors (modelled folded until now), the HK416. Optics from other mods
    leave the sights up. The others keep theirs: fixed sights the optics clear (Uzis, TMP, RPKs, Grozas, M249, UMPs,
    whose long scopes are drawn further forward), the pistols' slide sights, guns with no iron sights (AUG A3 family,
    MDRx, P90 TR, PS90), integral optics (AUG A1, SR-25) and the Mk 11 (its front sight is already folded).
--]]

local ConditionalModel = require("WeaponSystems/Utils/ConditionalModel")

local IronSights = {}

-- GoM's optics: no magnification (the front sight is seen through them), then the magnified ones
IronSights.RED_DOTS = {
    "MarzGuns.EXPS1_Sight", "MarzGuns.EXPS3_Sight", "MarzGuns.Aimpoint_Sight", "MarzGuns.OKP3_Sight",
    "MarzGuns.ReflexS2_Sight", "MarzGuns.JS14_Sight", "MarzGuns.Kobra_Sight",
}
IronSights.SCOPES = {
    "MarzGuns.ElcanX2_Scope", "MarzGuns.LR10X_Scope", "MarzGuns.TA28_Scope", "MarzGuns.LR4X_Scope",
    "MarzGuns.TR06X_Scope", "MarzGuns.PSO1_Scope", "MarzGuns.LRX12X_Scope",
}

local M = "GunsOfTienPost93."

--- gun: the item's full type (also its own model, sights up). removed: optic -> state suffix ("_RDX" / "_FDX") for
--- the optics whose mount sits on the rear sight's spot; checked before the red dot and scope rules.
function IronSights.Register(gun, removed)
    local rules = {}
    for optic, suffix in pairs(removed or {}) do
        rules[#rules + 1] = { parts = { Scope = optic }, model = gun .. suffix }
    end
    rules[#rules + 1] = { parts = { Scope = IronSights.RED_DOTS }, model = gun .. "_RD" }
    rules[#rules + 1] = { parts = { Scope = IronSights.SCOPES }, model = gun .. "_FD" }
    ConditionalModel.Register(gun, { rules = rules, default = gun })
end

for _, gun in ipairs({ "MP7A1", "MP7A2", "SCARH", "VECTOR45", "VECTOR9", "VECTORCRB", "VECTORSDP" }) do
    IronSights.Register(M .. gun)
end
IronSights.Register(M .. "SCARL", { ["MarzGuns.ElcanX2_Scope"] = "_FDX", ["MarzGuns.TR06X_Scope"] = "_FDX" })
IronSights.Register(M .. "HK416", { ["MarzGuns.Kobra_Sight"] = "_RDX", ["MarzGuns.ElcanX2_Scope"] = "_FDX",
    ["MarzGuns.TR06X_Scope"] = "_FDX" })

return IronSights
