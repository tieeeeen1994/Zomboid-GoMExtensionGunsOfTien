--[[
    Guns of Tien -- Guns of Marz's muzzle points at the end of the barrel (user, 2026-10-26: "is this item possible?
    ... can you try it then?")

    The engine draws the muzzle flash at the gun model's `muzzle` point and starts the bullet and its tracer there
    (CLAUDE.md "Gun scale"). On 21 of GoM's gun models it sits 1 to 7 cm off the end of the barrel: ahead of it in
    the air (W1887 5.7, AS VAL 5.6, Detective .38 5.5, the AR-15 / M16s 5.4, Model 70 4.0, M14 and M1 2.8, AK-47 2.1,
    P226 1.1, FAMAS 1.0 cm in game units x 100) or inside it (W1894 7.0, FAL 4.9, Remington 870 2.1, PSG1 2.0, 93R
    1.9, MP5 1.4, Rhino 1.2, MP5A2 1.0). Measured by scripts/muzzle_audit.py (the frontmost vertex within 1.2 cm of
    the point's line along the barrel, full-length parts in place; side views from muzzle_audit_sheet.py); every point
    was already within 0.5 cm of the bore's centre line, so only its distance along the barrel changes.
    The AR-15 and M16s' point was at the front of GoM's AR muzzle mount device, which only carries a suppressor (and a
    suppressor turns the flash off, AttachmentCustomStats.lua); with GoM's flash hider, compensator or muzzle brake
    fitted (3.5-4.3 cm long) the flash now starts inside the device instead of 1-2 cm ahead of it. The point is one
    per model, not per gun, so it is placed for the bare barrel. Left alone: guns under 1 cm off, GoM's MP5K (in our
    compact stance, which reads its point), and the M203 launcher models (`*_M203_Underbarrel`, drawn while the
    grenade launcher is selected).
    The offset is set on GoM's loaded ModelScript (a model block cannot be declared again from another mod: it resets
    the mesh and texture); x and z are kept. Scripts are rebuilt on leaving a game, so it runs again at every world
    load; the values are absolute, so running twice changes nothing.
--]]

-- model script -> the `muzzle` point's distance along the barrel (y), the bore's front
local MUZZLE_Y = {
    ["MarzGuns.AK47"] = 0.4130,           -- was 0.4336 (+2.1)
    ["MarzGuns.AR15"] = 0.4426,           -- was 0.4966 (+5.4)
    ["MarzGuns.ASVAL"] = 0.3893,          -- was 0.4455 (+5.6)
    ["MarzGuns.DETECTIVE_38"] = 0.1491,   -- was 0.2038 (+5.5)
    ["MarzGuns.FAL"] = 0.5512,            -- was 0.5023 (-4.9)
    ["MarzGuns.FAMAS"] = 0.3057,          -- was 0.3158 (+1.0)
    ["MarzGuns.M14"] = 0.5387,            -- was 0.5672 (+2.8)
    ["MarzGuns.M16A2"] = 0.4426,          -- was 0.4966 (+5.4)
    ["MarzGuns.M16A2_M203"] = 0.4426,     -- was 0.4966 (+5.4)
    ["MarzGuns.M16A3"] = 0.4426,          -- was 0.4966 (+5.4)
    ["MarzGuns.M1_GARAND"] = 0.5255,      -- was 0.5537 (+2.8)
    ["MarzGuns.M93R"] = 0.1619,           -- was 0.1433 (-1.9)
    ["MarzGuns.MODEL_70"] = 0.4700,       -- was 0.5100 (+4.0)
    ["MarzGuns.MP5"] = 0.3102,            -- was 0.2966 (-1.4)
    ["MarzGuns.MP5A2"] = 0.3067,          -- was 0.2966 (-1.0)
    ["MarzGuns.P226"] = 0.1325,           -- was 0.1433 (+1.1)
    ["MarzGuns.PSG1"] = 0.5344,           -- was 0.5149 (-2.0)
    ["MarzGuns.REMINGTON_870"] = 0.4996,  -- was 0.4785 (-2.1)
    ["MarzGuns.RHINO"] = 0.1861,          -- was 0.1744 (-1.2)
    ["MarzGuns.W1887"] = 0.5015,          -- was 0.5584 (+5.7)
    ["MarzGuns.W1894"] = 0.4815,          -- was 0.4115 (-7.0)
}

local function patchScripts()
    local manager = ScriptManager.instance
    for name, y in pairs(MUZZLE_Y) do
        local model = manager:getModelScript(name)
        local muzzle = model and model:getAttachmentById("muzzle")
        if muzzle then
            local offset = muzzle:getOffset()
            offset:set(offset:x(), y, offset:z())
        else
            print("[GunsOfTien] muzzle points: no muzzle point on " .. name)
        end
    end
end
Events.OnGameBoot.Add(patchScripts)
Events.OnInitGlobalModData.Add(patchScripts)
