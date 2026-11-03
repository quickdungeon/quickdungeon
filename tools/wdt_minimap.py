#!/usr/bin/env python3
"""Build a top-down overview of a WoW map from its minimap tiles.

Usage: wdt_minimap.py WOW_DIR PRODUCT WDT_FDID OUT.png [--info]
Reads the map's WDT (by FileDataID), finds the minimap texture for every terrain tile
(MAID chunk), extracts them from CASC and stitches them into one image, cropped to the tiles
that exist. --info only prints what the WDT contains.

WDT layout (wowdev.wiki/WDT): chunks of <4-byte reversed magic><u32 size>.
  MPHD  flags (0x1 = the map is a single global WMO, no terrain)
  MAIN  64x64 x (u32 flags, u32 async id); flags & 1 = tile has terrain
  MAID  64x64 x 8 u32 FileDataIDs: root ADT, obj0, obj1, tex0, lod, map texture,
        map normal texture, minimap texture
  MODF  placement of the global WMO, if any
"""
import io, os, struct, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from casc_read import Storage, Encrypted  # noqa: E402


def chunks(blob):
    pos = 0
    while pos + 8 <= len(blob):
        magic = blob[pos:pos + 4][::-1].decode("ascii", "replace")
        size = struct.unpack_from("<I", blob, pos + 4)[0]
        yield magic, blob[pos + 8:pos + 8 + size]
        pos += 8 + size


def parse_wdt(blob):
    info = {"flags": 0, "tiles": {}, "chunks": []}
    main = maid = None
    for magic, data in chunks(blob):
        info["chunks"].append(f"{magic}({len(data)})")
        if magic == "MPHD":
            info["flags"] = struct.unpack_from("<I", data, 0)[0]
        elif magic == "MAIN":
            main = data
        elif magic == "MAID":
            maid = data
        elif magic == "MODF":
            info["modf"] = len(data) // 64
    if main and maid:
        for y in range(64):
            for x in range(64):
                i = y * 64 + x
                if struct.unpack_from("<I", main, i * 8)[0] & 1:
                    fdids = struct.unpack_from("<8I", maid, i * 32)
                    info["tiles"][(x, y)] = {"root": fdids[0], "minimap": fdids[7]}
    return info


def main():
    wow_dir, product, wdt_fdid, out = sys.argv[1:5]
    st = Storage(wow_dir, product)
    info = parse_wdt(st.read_fdid(int(wdt_fdid)))
    tiles = info["tiles"]
    xs = [x for x, _ in tiles] or [0]
    ys = [y for _, y in tiles] or [0]
    print(f"WDT {wdt_fdid}: flags=0x{info['flags']:x} chunks={' '.join(info['chunks'])}")
    print(f"  {len(tiles)} terrain tiles, x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}; "
          f"{sum(1 for t in tiles.values() if t['minimap'])} with a minimap texture; global WMO placements: {info.get('modf', 0)}")
    if "--info" in sys.argv or not tiles:
        return
    images, missing = {}, 0
    for (x, y), t in tiles.items():
        if not t["minimap"]:
            missing += 1
            continue
        try:
            images[(x, y)] = Image.open(io.BytesIO(st.read_fdid(t["minimap"]))).convert("RGB")
        except (KeyError, Encrypted) as e:
            missing += 1
            print(f"  tile {x},{y}: minimap {t['minimap']} unavailable ({type(e).__name__})")
    if not images:
        print("  no minimap tiles could be read")
        return
    size = max(im.width for im in images.values())
    x0, y0 = min(x for x, _ in images), min(y for _, y in images)
    w = (max(x for x, _ in images) - x0 + 1) * size
    h = (max(y for _, y in images) - y0 + 1) * size
    canvas = Image.new("RGB", (w, h), (16, 22, 41))
    for (x, y), im in images.items():
        canvas.paste(im.resize((size, size)) if im.width != size else im, ((x - x0) * size, (y - y0) * size))
    canvas.save(out, optimize=True)
    print(f"  wrote {out}: {canvas.width}x{canvas.height} from {len(images)} tiles ({size}px each), {missing} missing")


if __name__ == "__main__":
    main()
