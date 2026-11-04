#!/usr/bin/env python3
"""Build the Quick Dungeon logo from the three tank icons in the WoW Forever client.

Usage: make_logo.py WOW_DIR PRODUCT SITE_DIR
  e.g. make_logo.py "/path/to/World of Warcraft" wowf site

The logo is the classic tanks' signature abilities as round, gold-rimmed medallions (like the
game's role icons) overlapping in a triangle, with the warrior's in front:
  Defensive Stance  interface/icons/ability_warrior_defensivestance.blp  FileDataID 132341
  Righteous Fury    interface/icons/spell_holy_righteousfury.blp         FileDataID 135959
  Bear Form         interface/icons/ability_racial_bearform.blp          FileDataID 132276

Writes (all derived from the game's icon art):
  SITE_DIR/assets/logo/logo.png       512x512 master, transparent; Hugo resizes it for the page
  SITE_DIR/static/favicon.ico         16, 32 and 48 px
  SITE_DIR/static/apple-touch-icon.png  180 px on the site's background colour
Needs Pillow (reads BLP) and tools/casc_read.py.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ICONS = {"warrior": 132341, "paladin": 135959, "druid": 132276}
FRONT, ORDER = "warrior", ["warrior", "paladin", "druid"]
INK = (11, 29, 43, 255)  # --ink in assets/css/main.css
N = 512


def extract(wow_dir, product, out):
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, "-I", os.path.join(here, "casc_read.py"), wow_dir, product, out,
                    *map(str, ICONS.values())], check=True)
    icons = {}
    for name, fdid in ICONS.items():
        im = Image.open(os.path.join(out, str(fdid))).convert("RGBA")
        icons[name] = im.crop((5, 5, 59, 59))  # drop the baked-in icon border, as the game UI does
    return icons


def circle_mask(size, ss=4):
    m = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def gold_ring(size, width, ss=4):
    """Bevelled gold rim, like the game's round role and portrait frames."""
    s, w = size * ss, width * ss
    ring = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.ellipse((0, 0, s - 1, s - 1), fill=(32, 20, 4, 255))                                  # dark outer edge
    d.ellipse((ss * 2, ss * 2, s - 1 - ss * 2, s - 1 - ss * 2), fill=(201, 150, 52, 255))  # gold
    d.ellipse((w * .45, w * .45, s - 1 - w * .45, s - 1 - w * .45), fill=(255, 222, 120, 255))  # highlight
    d.ellipse((w * .7, w * .7, s - 1 - w * .7, s - 1 - w * .7), fill=(150, 104, 30, 255))       # inner shadow
    d.ellipse((w, w, s - 1 - w, s - 1 - w), fill=(0, 0, 0, 0))                                   # hole
    return ring.resize((size, size), Image.LANCZOS)


def medallion(icon, size):
    ring_w = round(size * 22 / 270)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner = size - 2 * ring_w + 6
    art = icon.resize((inner, inner), Image.LANCZOS)
    art.putalpha(ImageChops.multiply(art.getchannel("A"), circle_mask(inner)))
    out.alpha_composite(art, ((size - inner) // 2, (size - inner) // 2))
    out.alpha_composite(gold_ring(size, ring_w))
    return out


def drop_shadow(im, radius=10, alpha=150):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda v: v * alpha // 255))
    return sh.filter(ImageFilter.GaussianBlur(radius))


def logo(icons, back=250, front=290):
    canvas = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    left, right = [k for k in ORDER if k != FRONT]
    for name, size, x, y in ((left, back, 20, 120), (right, back, N - back - 20, 120),
                             (FRONT, front, (N - front) // 2, 222)):
        m = medallion(icons[name], size)
        canvas.alpha_composite(drop_shadow(m), (x, y + 6))
        canvas.alpha_composite(m, (x, y))
    canvas = canvas.crop(canvas.getchannel("A").getbbox())
    side = max(canvas.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(canvas, ((side - canvas.width) // 2, (side - canvas.height) // 2))
    return square.resize((N, N), Image.LANCZOS)


def main():
    wow_dir, product, site = sys.argv[1:4]
    with tempfile.TemporaryDirectory() as tmp:
        icons = extract(wow_dir, product, tmp)
    master = logo(icons)
    os.makedirs(os.path.join(site, "assets", "logo"), exist_ok=True)
    master.save(os.path.join(site, "assets", "logo", "logo.png"), optimize=True)
    master.save(os.path.join(site, "static", "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    touch = Image.new("RGBA", (180, 180), INK)
    touch.alpha_composite(master.resize((148, 148), Image.LANCZOS), (16, 16))
    touch.convert("RGB").save(os.path.join(site, "static", "apple-touch-icon.png"), optimize=True)
    print("wrote assets/logo/logo.png, static/favicon.ico, static/apple-touch-icon.png")


if __name__ == "__main__":
    main()
