#!/usr/bin/env python3
"""An unlit model shader for the lit laser's beam (user, 2026-10-18: always bright, not darkened by the lighting).

    python3 scripts/make_laser_shader.py

Every model shader in 42.21 is lit (basicEffect.frag multiplies the texture by the sum of the scene's lights and its
ambient), so a beam drawn with the default one is as dark as the gun at night. A model script may name its own shader
(`shader = name`), and zombie/core/opengl/ShaderProgram reads `media/shaders/<name>[_static][_instanced].vert` and
`<name>[_instanced].frag` through ZomboidFileSystem.getString, which also finds mod files. This copies vanilla's
basicEffect shaders from the game install into Contents/mods/GoMExtensionGunsOfTien/42/media/shaders/ as
gunsoftien_laser*, the vertex shaders unchanged (all four variants, so the beam draws whichever way the engine
batches it) and one line changed in each fragment shader: the colour is no longer multiplied by `lighting` (unlit;
tint and the model's alpha still apply). A screen-door fade (pixels discarded by texture alpha against noise, since
the engine draws weapon parts opaque) was tried and dropped: it looked dotted at game size, so the beam is solid and
narrows to a point instead (make_laser_beam.py; user's choice, 2026-10-18). Run again after a game update; it stops
if a patched line moved.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media/shaders"))
GAME = next(p for p in (os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/"
                                           "Project Zomboid.app/Contents/Java/media/shaders"),
                        "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/shaders")
            if os.path.isdir(p))
NAME = "gunsoftien_laser"

# fragment shader -> [(vanilla line, replacement)]: unlit
PATCHES = {
    "basicEffect.frag": [
        ("col = vec3(col.x * tintColour.x * lighting.x, col.y * tintColour.y * lighting.y, "
         "col.z * tintColour.z * lighting.z);",
         "col = col * tintColour;    // Guns of Tien laser beam: unlit"),
    ],
    "basicEffect_instanced.frag": [
        ("col = col * inst.TintColour * lighting;",
         "col = col * inst.TintColour;    // Guns of Tien laser beam: unlit"),
    ],
}
COPIES = ["basicEffect.vert", "basicEffect_static.vert", "basicEffect_instanced.vert",
          "basicEffect_static_instanced.vert"]


def main():
    os.makedirs(OUT, exist_ok=True)
    for src in COPIES + list(PATCHES):
        text = open(os.path.join(GAME, src), encoding="utf-8", newline="").read()
        for old, new in PATCHES.get(src, []):
            if text.count(old) != 1:
                sys.exit("%s: %r was not found once; the game's shader changed" % (src, old[:40]))
            text = text.replace(old, new)
        dst = os.path.join(OUT, src.replace("basicEffect", NAME))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("wrote", dst)


if __name__ == "__main__":
    main()
