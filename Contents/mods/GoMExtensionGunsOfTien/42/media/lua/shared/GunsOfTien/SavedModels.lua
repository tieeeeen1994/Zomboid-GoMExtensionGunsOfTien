--[[
    Guns of Tien -- models that only guns saved in older versions still name (a HandWeapon keeps its weapon sprite in
    its save when it differs from the script's). Until 2026-10-28 GoM's MP5K was swapped to GunsOfTien.MP5K_1H while
    held in one hand, and until 2026-10-29 to GunsOfTien.MP5K_2H while held in both (our own hold animations, dropped
    for GoM's: GoMReloads.lua). Both now copy GoM's live MP5K model (mesh, texture, points), so such a gun is drawn
    as GoM draws it. The other `_1H` models (Mini Uzi, MP7s) are the guns' own models already (gen_scripts.py,
    gen_post93_guns.py).
--]]

local function fmt(v)
    return string.format("%.4f %.4f %.4f", v:x(), v:y(), v:z())
end

local function copyModel(from, to)
    local manager = ScriptManager.instance
    local src, dst = manager:getModelScript(from), manager:getModelScript(to)
    if not (src and dst) then
        print("[GunsOfTien] saved models: model script not found: " .. (src and to or from))
        return
    end
    local name = dst:getName()
    local text = { "model ", name, " { mesh = ", src:getMeshName(), ", texture = ", src:getTextureName(), "," }
    for i = 0, src:getAttachmentCount() - 1 do
        local a = src:getAttachment(i)
        if a:getId() ~= "Bip01_Prop1" then
            local bone = a:getBone()
            text[#text + 1] = " attachment " .. a:getId() .. " { offset = " .. fmt(a:getOffset()) .. ", rotate = "
                .. fmt(a:getRotate()) .. ", scale = " .. string.format("%.4f", a:getScale())
                .. ((bone and bone ~= "") and (", bone = " .. bone) or "") .. ", }"
        end
    end
    text[#text + 1] = " }"
    dst:Load(name, table.concat(text))
end

local function copyAll()
    copyModel("MarzGuns.MP5K", "GunsOfTien.MP5K_1H")
    copyModel("MarzGuns.MP5K", "GunsOfTien.MP5K_2H")
end
Events.OnGameBoot.Add(copyAll)
Events.OnInitGlobalModData.Add(copyAll)
