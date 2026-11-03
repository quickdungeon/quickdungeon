#!/usr/bin/env python3
"""Stitch in-game world-map art (UiMapArt) from its tiles into PNGs.

Usage: stitch_uimap.py DB2_DIR WOW_DIR PRODUCT OUT_DIR ART_ID [ART_ID ...]
  DB2_DIR holds UiMapArt.csv, UiMapArtTile.csv, UiMapArtStyleLayer.csv for the build
  (e.g. from https://wago.tools/db2/<Table>/csv?build=<version>).
Writes OUT_DIR/art-<id>.png, cropped to the layer size the game displays.
"""
import csv, io, os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from casc_read import Storage  # noqa: E402


def rows(db2, table):
    return list(csv.DictReader(open(os.path.join(db2, table + ".csv"), encoding="utf-8")))


def main():
    db2, wow_dir, product, out_dir = sys.argv[1:5]
    art_ids = sys.argv[5:]
    arts = {r["ID"]: r for r in rows(db2, "UiMapArt")}
    layers = {r["UiMapArtStyleID"]: r for r in rows(db2, "UiMapArtStyleLayer") if r["LayerIndex"] == "0"}
    tiles = rows(db2, "UiMapArtTile")
    st = Storage(wow_dir, product)
    os.makedirs(out_dir, exist_ok=True)
    for art_id in art_ids:
        layer = layers[arts[art_id]["UiMapArtStyleID"]]
        tw, th = int(layer["TileWidth"]), int(layer["TileHeight"])
        mine = [t for t in tiles if t["UiMapArtID"] == art_id and t["LayerIndex"] == "0"]
        cols = 1 + max(int(t["ColIndex"]) for t in mine)
        rws = 1 + max(int(t["RowIndex"]) for t in mine)
        canvas = Image.new("RGB", (cols * tw, rws * th))
        for t in mine:
            tile = Image.open(io.BytesIO(st.read_fdid(int(t["FileDataID"])))).convert("RGB")
            canvas.paste(tile, (int(t["ColIndex"]) * tw, int(t["RowIndex"]) * th))
        w, h = int(layer["LayerWidth"]), int(layer["LayerHeight"])
        canvas = canvas.crop((0, 0, min(w, canvas.width), min(h, canvas.height)))
        path = os.path.join(out_dir, f"art-{art_id}.png")
        canvas.save(path, optimize=True)
        print(f"art {art_id}: {len(mine)} tiles -> {canvas.width}x{canvas.height} {path}")


if __name__ == "__main__":
    main()
