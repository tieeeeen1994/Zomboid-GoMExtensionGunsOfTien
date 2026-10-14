"""Make Blender's binary FBX output reproducible (plain Python, also runs inside Blender).

export_scene.fbx stamps the file with the current date and time (CreationTimeStamp, CreationTime) and keys every
object with an id derived from memory addresses, so two identical exports differ. normalize(path) rewrites, in
place and without changing any length: the time stamp to 2026-01-01 00:00:00, and every Document / Geometry /
Model / NodeAttribute id to a number derived from the node's class and name (connections follow, since they
carry the same 8-byte ids). Nothing the game reads (Geometry, Model names, transforms) changes.
"""

import struct
import zlib


def _read(data, off, version):
    if version >= 7500:
        end, nprops, _ = struct.unpack_from("<QQQ", data, off)
        off += 24
    else:
        end, nprops, _ = struct.unpack_from("<III", data, off)
        off += 12
    nlen = data[off]
    name = data[off + 1:off + 1 + nlen].decode("ascii", "replace")
    off += 1 + nlen
    if end == 0:
        return None, off
    props = []
    for _ in range(nprops):
        kind = chr(data[off])
        off += 1
        if kind in "YCIFDL":
            size = {"Y": 2, "C": 1, "I": 4, "F": 4, "D": 8, "L": 8}[kind]
            props.append((kind, off, data[off:off + size]))
            off += size
        elif kind in "fdlbic":
            _, _, length = struct.unpack_from("<III", data, off)
            off += 12 + length
            props.append((kind, off, None))
        elif kind in "SR":
            length = struct.unpack_from("<I", data, off)[0]
            props.append((kind, off + 4, data[off + 4:off + 4 + length]))
            off += 4 + length
        else:
            raise ValueError("FBX property type %r" % kind)
    children = []
    while off < end:
        node, off = _read(data, off, version)
        if node is None:
            break
        children.append(node)
    return {"name": name, "props": props, "children": children}, end


def _walk(nodes):
    for n in nodes:
        yield n
        yield from _walk(n["children"])


def normalize(path):
    with open(path, "rb") as handle:
        data = bytearray(handle.read())
    version = struct.unpack_from("<I", data, 23)[0]
    off, roots = 27, []
    while off < len(data) - 160:
        node, off = _read(bytes(data), off, version)
        if node is None:
            break
        roots.append(node)
    stamp = {"Year": 2026, "Month": 1, "Day": 1, "Hour": 0, "Minute": 0, "Second": 0, "Millisecond": 0}
    remap = {}
    for n in _walk(roots):
        if n["name"] in stamp and n["props"] and n["props"][0][0] == "I":
            struct.pack_into("<i", data, n["props"][0][1], stamp[n["name"]])
        if n["name"] == "P" and n["props"] and n["props"][0][2] == b"CreationTime" and n["props"][-1][0] == "S":
            _, at, old = n["props"][-1]
            new = b"2026-01-01 00:00:00:000"[:len(old)].ljust(len(old), b"0")
            data[at:at + len(old)] = new
        if n["name"] in ("Document", "Geometry", "Model", "NodeAttribute") and n["props"] and n["props"][0][0] == "L":
            old = n["props"][0][2]
            label = n["name"].encode() + b"|" + (n["props"][1][2] or b"")
            remap[old] = struct.pack("<q", 100000000 + zlib.crc32(label) % 900000000)
    for old, new in remap.items():
        data[:] = data.replace(b"L" + old, b"L" + new)
    with open(path, "wb") as handle:
        handle.write(bytes(data))
