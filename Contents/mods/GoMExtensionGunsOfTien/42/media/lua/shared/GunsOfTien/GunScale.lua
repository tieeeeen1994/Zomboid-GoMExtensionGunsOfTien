--[[
    Guns of Tien -- Guns of Marz's guns drawn in the M16A2's proportion to the body (user, 2026-10-25: "the MP5A1 and MP5A2 seem
    a little bit big ... does it follow the size proportion from M16?", then "edit each gun so that they have their own
    scales rather than apply a global scale")

    Guns of Marz draws its guns at 0.53 to 0.73 of their real length (pistols ~0.70), the M16A2 at 0.60, vanilla's body
    and M16 at ~0.55: the MP5A2 is ~20% too big next to the M16. scripts/scale_audit.py measures every gun as drawn
    and scripts/scale_audit_report.py gives each its own scale = the M16A2's ratio / the gun's (TODO.md "Gun scale
    audit"). Guns that mount the same magazine share one scale, their basis gun's (user, 2026-10-26: GoM builds every
    gun of a family on one receiver size, so the shared magazine must stay one size).

    - The scale is the model script's `scale` key, set on GoM's loaded ModelScript with ModelScript:Load (42.21: Load
      on a loaded script sets only the keys it is given and keeps GoM's mesh, texture and points; a model block
      declared again in our scripts would reset them). A model instance copies it when it is made
      (ModelInstance.applyModelScriptScale, at every equip / attach) and floor items read it at every draw.
    - It is applied last, after the gun's own attachment point, so it scales the gun about that point, and parts
      (magazines, sights, suppressors, bayonets, the muzzle flash) follow, drawn from the gun's transform. The gun's
      own points that place it on something else are applied before the scale, though: `world` (the floor pose,
      ItemModelRenderer.init, inverted) and the points named after a body point (back, holsters, Bip01_Prop1; the
      engine pairs the body's point with the gun's point of the same name). Their offsets are scaled too, so the gun
      shrinks or grows about the body point / its floor spot. Body point names are read from FemaleBody and
      MaleBody, so other mods' points count.
    - Not scaled: the `muzzle` point as a bullet origin (BallisticsController reads its raw offset; scaling it would
      move the flash, drawn at it after the scale, into the barrel), Hot Brass ejection offsets (relative to the
      player). See TODO.md.
    - GoM's guns only (user, 2026-10-26: Guns of Tien's own guns are to be remodelled at the right size instead).
      Left out: GoM's MP5K (held in our compact stance, whose clips fit its size) and Stolzer & Son 2-bore (no real
      size). Our sawn-stock bodies of GoM's break-actions are in, at their gun's scale.

    Sandbox option "[BETA] Resize Guns of Marz" (GunsOfTien.RescaleGuns, default off; user, 2026-10-26),
    read once at world load (OnInitGlobalModData: sandbox options are loaded, on clients too, and scripts are fresh).
    Scripts are rebuilt on leaving a game, so this runs again at every world load; values are absolute, and a point
    already scaled is recognised by the offset written to it, so running twice changes nothing. With the option off,
    a model this Lua session scaled and that was not rebuilt goes back to 1 (no GoM or Guns of Tien gun model sets a
    scale of its own).
--]]

local GunScale = {}

-- model script -> scale (the gun's WeaponSprite, and every other model the same gun is drawn with)
GunScale.MODELS = {
    -- AR family on STANAG magazines: one receiver (GoM's `magazine` point is the same on all of them), basis M16A2
    ["MarzGuns.M16A1"] = 1.00, ["MarzGuns.M16A2"] = 1.00, ["MarzGuns.M16A3"] = 1.00,
    ["MarzGuns.M16A2_M203"] = 1.00, ["MarzGuns.M16A2_M203_Underbarrel"] = 1.00,
    ["MarzGuns.AR15"] = 1.00, ["MarzGuns.M4A1"] = 1.00,
    ["MarzGuns.CAR15"] = 1.00, ["MarzGuns.CAR15_M203_Underbarrel"] = 1.00,
    ["MarzGuns.XM177"] = 1.00,
    -- STANAG magazines on receivers of their own: strict, the magazine as in the M16 (open: TODO.md)
    ["MarzGuns.FNC"] = 1.00,
    -- an F1, which never took STANAG magazines (GoM's choice): its own size
    ["MarzGuns.FAMAS"] = 0.88,
    -- MP5 magazines, basis MP5 (not the MP5K: our compact stance holds it at its own size)
    ["MarzGuns.MP5"] = 0.87, ["MarzGuns.MP5A2"] = 0.87, ["MarzGuns.MP5SD"] = 0.87,
    -- AK-74 magazines, basis AK-74
    ["MarzGuns.AK74"] = 0.93, ["MarzGuns.AKS74U"] = 0.93,
    -- G36 magazines, basis G36
    ["MarzGuns.G36"] = 0.98, ["MarzGuns.G36C"] = 0.98,
    -- .45 M1911 magazines, basis M1911
    ["MarzGuns.M1911"] = 0.86, ["MarzGuns.CAMP_CARBINE"] = 0.86,

    -- rifle stance, each its own ('?' in TODO.md: variant guessed from the model)
    ["MarzGuns.W1894"] = 0.90, ["MarzGuns.FAL"] = 0.91, ["MarzGuns.SKS"] = 0.91, ["MarzGuns.SVD"] = 0.91,
    ["MarzGuns.THOMPSON"] = 0.91, ["MarzGuns.MINI_14"] = 0.92, ["MarzGuns.W1873"] = 0.94,
    ["MarzGuns.AK47"] = 0.94, ["MarzGuns.G3"] = 0.94, ["MarzGuns.W1873_CARBINE"] = 0.95, ["MarzGuns.M79"] = 0.95,
    ["MarzGuns.M1903"] = 0.95, ["MarzGuns.ASVAL"] = 0.95, ["MarzGuns.M1895"] = 0.96,
    ["MarzGuns.MOSSBERG_590"] = 0.96, ["MarzGuns.REMINGTON_700"] = 0.97, ["MarzGuns.M24"] = 0.97,
    ["MarzGuns.M60"] = 0.98, ["MarzGuns.M14"] = 0.98, ["MarzGuns.MOSIN"] = 0.99,
    ["MarzGuns.SPAS12"] = 1.00, ["MarzGuns.M1_GARAND"] = 1.00, ["MarzGuns.PSG1"] = 1.00, ["MarzGuns.MODEL_70"] = 1.00,
    ["MarzGuns.TRENCHGUN"] = 1.04, ["MarzGuns.AA12"] = 1.05, ["MarzGuns.BENELLI_M4"] = 1.05, ["MarzGuns.BAR"] = 1.07,
    ["MarzGuns.REMINGTON_870"] = 1.10, ["MarzGuns.W1887"] = 1.14,
    -- break-actions, with our sawn-stock bodies (SawnStock.lua swaps the gun's WeaponSprite to them)
    ["MarzGuns.DOUBLEBARREL"] = 1.01,
    ["GunsOfTien.DOUBLEBARREL_SAWNSTOCK"] = 1.01, ["GunsOfTien.DOUBLEBARREL_SAWNSTOCK_SHORT"] = 1.01,
    ["MarzGuns.STEVENS_555"] = 0.94,
    ["GunsOfTien.STEVENS_555_SAWNSTOCK"] = 0.94, ["GunsOfTien.STEVENS_555_SAWNSTOCK_SHORT"] = 0.94,
    ["MarzGuns.TOZ34"] = 0.98,
    ["GunsOfTien.TOZ34_SAWNSTOCK"] = 0.98, ["GunsOfTien.TOZ34_SAWNSTOCK_SHORT"] = 0.98,

    -- SMGs held as pistols on GoM's clips
    ["MarzGuns.MAC10"] = 0.87, ["MarzGuns.TEC9"] = 0.88,

    -- pistols
    ["MarzGuns.DETECTIVE_38"] = 0.69, ["MarzGuns.MP412"] = 0.75, ["MarzGuns.COLT_SINGLE"] = 0.82,
    ["MarzGuns.RHINO"] = 0.82, ["MarzGuns.HIPOWER"] = 0.83, ["MarzGuns.P226"] = 0.83, ["MarzGuns.GLOCK17"] = 0.84,
    ["MarzGuns.M93R"] = 0.85, ["MarzGuns.PYTHON"] = 0.86, ["MarzGuns.SW629"] = 0.87, ["MarzGuns.M92FS"] = 0.88,
    ["MarzGuns.USP"] = 0.90, ["MarzGuns.DEAGLE"] = 0.94, ["MarzGuns.VP70M"] = 1.01,
}

local written = {}       -- attachment -> { x, y, z } we last set it to
local original = {}      -- attachment -> { x, y, z } as its script had it
local scaled = {}        -- model scripts given a scale this Lua session

local function isEnabled()
    local vars = SandboxVars and SandboxVars.GunsOfTien
    return vars ~= nil and vars.RescaleGuns == true
end

local function selfPointNames(manager)
    local names = { world = true }
    for _, body in ipairs({ "FemaleBody", "MaleBody" }) do
        local script = manager:getModelScript(body)
        if script then
            for i = 0, script:getAttachmentCount() - 1 do
                names[script:getAttachment(i):getId()] = true
            end
        end
    end
    return names
end

local function same(v, w)
    return w and math.abs(v:x() - w[1]) < 1e-6 and math.abs(v:y() - w[2]) < 1e-6 and math.abs(v:z() - w[3]) < 1e-6
end

local function scalePoint(attachment, scale)
    local offset = attachment:getOffset()
    if not same(offset, written[attachment]) then
        -- fresh from its script (a new object, or reloaded into this one)
        original[attachment] = { offset:x(), offset:y(), offset:z() }
    end
    local o = original[attachment]
    offset:set(o[1] * scale, o[2] * scale, o[3] * scale)
    written[attachment] = { offset:x(), offset:y(), offset:z() }
end

local function setScale(script, name, scale, selfNames)
    local short = name:match("[^.]+$")
    script:Load(short, string.format("model %s { scale = %.4f, }", short, scale))
    for i = 0, script:getAttachmentCount() - 1 do
        local attachment = script:getAttachment(i)
        if selfNames[attachment:getId()] then
            scalePoint(attachment, scale)
        end
    end
end

function GunScale.apply()
    local manager = ScriptManager.instance
    local enabled = isEnabled()
    local selfNames = selfPointNames(manager)
    for name, scale in pairs(GunScale.MODELS) do
        local script = manager:getModelScript(name)
        if not script then
            print("[GunsOfTien] gun scale: model script not found: " .. name)
        elseif enabled then
            setScale(script, name, scale, selfNames)
            scaled[script] = true
        elseif scaled[script] then
            setScale(script, name, 1.0, selfNames)
            scaled[script] = nil
        end
    end
end

Events.OnInitGlobalModData.Add(GunScale.apply)

return GunScale
