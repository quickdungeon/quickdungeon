#!/usr/bin/env python3
"""Build OUT_DIR/index.html from manifest.json, in the given slug order."""
import html, json, os, sys
out, slugs = sys.argv[1], sys.argv[2:]
man = json.load(open(os.path.join(out, "manifest.json")))
items = []
for s in slugs:
    v = man.get(s, {})
    t = html.escape(v.get("title", s))
    if v.get("status") == "ok":
        note = f' <small>({v["note"]})</small>' if v.get("note") else (
            f' <small>({len(v["missing"])} image(s) missing)</small>' if v.get("missing") else "")
        items.append(f'<li><a href="{s}/index.html">{t}</a>{note}</li>')
    else:
        items.append(f'<li>{t} <small>(not recovered: {v.get("status", "not fetched")})</small></li>')
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quick Dungeon (archive) - Classic dungeons</title>
<link rel="stylesheet" href="style.css">
</head><body>
<h1>Quick Dungeon &mdash; Classic dungeons</h1>
<p><img src="images/wow.jpg" alt="World of Warcraft (Classic)"></p>
<p>Personal offline archive of the Classic dungeon guides from quickdungeon.com,
recovered from the Internet Archive's Wayback Machine (captures from 2024). Order follows the original site's homepage.</p>
<ul class="guides">
{chr(10).join(items)}
</ul>
</body></html>
""")
print("wrote index with", len(items), "entries")
