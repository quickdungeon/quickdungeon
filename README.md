# Quick Dungeon

A rebuilt version of quickdungeon.com, the World of Warcraft dungeon quick-guide site
(WordPress, ~2014–2024). Each guide gives the tank route as a series of annotated maps, a
one-line tactic for every boss (ready to paste into instance chat with `/i`), and directions
to the entrance.

The guides were recovered from the Internet Archive in November 2026. The guide text and
annotated route maps are the original author's work, and the maps and boss portraits are
built on Blizzard's game art. Get the author's permission before hosting this publicly.

## Run it

You need Docker with Compose.

| What | Command | URL |
|---|---|---|
| Local copy of the site | `docker compose up -d --build` | http://localhost:8080 |
| Live editing (reloads as you edit `site/`) | `docker compose --profile dev up dev` | http://localhost:1313 |
| Public server with automatic HTTPS | `SITE_ADDRESS=quickdungeon.com docker compose -f compose.yaml -f compose.https.yaml up -d --build` | https://quickdungeon.com |

Options (environment variables for `docker compose`):

- `PORT`: host port for the local site (default `8080`).
- `SITE_ADDRESS`: what Caddy serves. The default `:8080` serves plain HTTP. A domain name
  (or several, comma-separated) switches on automatic HTTPS from Let's Encrypt on ports 80
  and 443. For that, DNS must already point at the server. `compose.https.yaml` publishes
  80/443 and keeps certificates in a volume.
- `BASE_URL`: build-time base URL for canonical links, Open Graph and the sitemap
  (default `https://quickdungeon.com/`, set in `site/hugo.toml`). All links inside the site
  are relative, so the site works on any host either way.

Other ways to host it:

- **Behind an existing reverse proxy or a platform that handles TLS** (Traefik, nginx,
  Cloudflare Tunnel, Fly.io, Render, Cloud Run, ...): run the image as-is. It listens on
  8080 over plain HTTP. Health check: `GET :8081/healthz` inside the container.
- **Static hosting only** (GitHub Pages, Cloudflare Pages, Netlify, S3): build with
  `docker build --target build -t qd-build . && docker run --rm qd-build tar -C /src/public -c . | tar -x -C ./public`,
  then upload `public/`. You'll lose Caddy's security and cache headers, but everything else works.

The image is the official Caddy image plus about 25 MB of site, and runs Caddy as an
unprivileged user (uid 10001). It sets a strict
Content-Security-Policy (no third-party requests at all: the font is self-hosted), uses
zstd/gzip compression, and caches fingerprinted assets for a year.

## Layout

```
site/                      Hugo project (Hugo 0.147, built inside Docker; no local install needed)
  hugo.toml
  content/dungeons/<slug>/ one page bundle per guide: index.md (structured YAML) + images/
  data/expansions/         which guides each expansion section lists, and in what order
  layouts/                 templates (home, guide page, 404, partials)
  assets/css/main.css      all styles
  assets/js/site.js        theme toggle, search, route-map stepper, copy-to-chat buttons
  assets/js/theme.js       applies a saved light theme before first paint
  static/                  font (Archivo, OFL licence), favicon
Dockerfile, Caddyfile      build with Hugo, serve with Caddy
compose.yaml               local + dev services
compose.https.yaml         override for a public HTTPS server
classic/                   the raw recovered archive (original HTML + images); not deployed
artist-maps/               unmodified originals of third-party maps (Santiago Reyes); not deployed
game-maps/                 maps extracted from the WoW Forever client (entrance areas, new-dungeon overviews)
tools/                     archive downloader, archive-to-Hugo converter, game-file extraction tools
```

Guide URLs match the old WordPress site (`/shadowfang-keep/`), so old links and search
results keep working if the domain comes back.

## Editing guides

Each guide is `site/content/dungeons/<slug>/index.md`. The page is generated entirely from
its front matter:

```yaml
title: "Shadowfang Keep"
url: "/shadowfang-keep/"
zone: "Silverpine Forest"
continent: "Eastern Kingdoms"
coords:
  x: 44.8
  "y": 67.6           # quote "y" (and "n"): YAML 1.1 reads bare y/n as true/false
entrance:             # ordered blocks: text, image, or note (an editor's note)
  - image: "images/shadowfang-keep-entrance-map1.jpg"
route:                # one entry per route map, shown as steps
  - label: "Map 1"
    blocks:
      - text: "Optional instructions for this map"
      - image: "images/shadowfang-keep-dungeon-map-1.jpg"
bosses:
  - number: 1         # matches the marker drawn on the route map
    name: "Baron Ashbury"
    tag: "optional"   # optional, or "heroic" for heroic-only bosses
    image: "images/baron-ashbury-model.jpg"
    tactics:
      - "Group make sure healed & ready for Asphyxiate..."   # shown and copied as "/i ..."
    heroic: "When finishes Asphyxiate will cast Stay of Execution..."
```

Images go in the guide's `images/` folder. Hugo converts them to WebP and makes the list
thumbnails. If a front-matter path points at a missing image, the dev server prints a
warning and the Docker build fails, naming the file.

## Adding the other expansions

The archive has ~100 more guides (Burning Crusade through The War Within) that haven't been
downloaded yet. To add an expansion:

1. Download it: `python3 -I tools/qd_fetch.py <dir> tools/capture-timestamps.txt <slug> ...`,
   then `python3 -I tools/qd_index.py <dir> <slug> ...` (slugs are the page paths in
   `tools/capture-timestamps.txt`).
2. Convert it: `python3 -I tools/convert_to_hugo.py <dir> site <id> "<Name>"`. This writes
   the page bundles and `site/data/expansions/<id>.yaml`.
3. Rebuild. A guide that's in more than one expansion (Deadmines and Shadowfang Keep are
   listed under both Classic and Cataclysm) only needs one page bundle; list its slug in
   each expansion's data file.

The converter needs Python with `beautifulsoup4` and `lxml`, which nest the WordPress markup
the same way a browser does.

## Third-party maps (credit required)

All four new WoW Forever dungeon pages (City of Dalaran with its city and sewers maps, Ruins
of Lordaeron, The Hall of Thanes, Excavation Site: Wetlands) show maps by **Santiago Reyes**
([Atlas de Azeroth: Forever](https://asguevara433.wixsite.com/srmaps)). His project post gives
everyone permission to use the maps for free, on these conditions: don't alter the watermark
or credits, and don't use the maps to make money. He also asks people to write to him so he
can approve the use (contact page: https://asguevara433.wixsite.com/srmaps/contacto).
Each map shows "Map by Santiago Reyes" with a link to his site underneath it. That comes from
the image block's `credit:` field (its `source:` records where the file came from), so keep
the field if you swap or move an image. The home-page thumbnails use his maps scaled
down (add `thumbnail_fit: "contain"` to a page to fit a differently shaped map without
cropping). The two Dalaran maps had a title banner across the bottom, which is cropped off
for the site; his watermark inside the map is untouched. The unmodified originals are in
`artist-maps/`. The "New in WoW Forever" intro line credits him with a
link, set by `credit:` in `site/data/expansions/forever.yaml`.

## Maps from the game client

`site/data/entrance_maps.yaml` lists in-game maps that appear under a guide's entrance
directions (Blackrock Mountain, Gnomeregan, Uldaman). The images are in
`site/assets/game-maps/`. They're kept out of `content/` so that rerunning the converter
doesn't delete them. `game-maps/README.md` describes every extracted map, including top-down
overviews and boss lists for the five new WoW Forever dungeons, which don't have guides yet.

The extraction tools only read the game files:

- `tools/casc_read.py WOW_DIR PRODUCT OUT_DIR FDID...` extracts files by FileDataID from a
  local CASC install (pure Python, no third-party code).
- `tools/stitch_uimap.py DB2_DIR WOW_DIR PRODUCT OUT_DIR ART_ID...` assembles world-map art
  from its tiles. The UiMapArt* tables come as CSV from `https://wago.tools/db2/<Table>/csv?build=<version>`.
- `tools/wdt_minimap.py WOW_DIR PRODUCT WDT_FDID OUT.png` stitches a map's terrain minimap tiles.

For example (WoW Forever is product `wowf`):
`python3 -I tools/casc_read.py "/path/to/World of Warcraft" wowf out 603971`

## Design notes

- Colour means something, and it's borrowed from the game's UI. Gold is for names (dungeons,
  bosses), like quest and NPC titles. Orange is for text you paste into instance chat (`/i`
  chat is orange in-game). Cyan boss numbers match the cyan annotations on the route maps.
  The dark theme's background is the misty night teal of the WoW Forever key art (with a
  soft glow at the top of the page), body text is the cream of its lettering, and the tan
  rules come from the bronze ring around its emblem, so the parchment maps stand out. The
  light theme is classic quest-log parchment.
- One typeface, Archivo, at three widths: expanded for names, normal for directions,
  condensed for chat lines.
- On wide screens the route map stays pinned while the boss list scrolls, so you can see the
  map and the tactics together on a second monitor. On phones they stack.
- Everything works without JavaScript (all maps are shown in order, and the tactics text can
  be selected). With JS you get search, the map stepper (arrow keys, `#map-3` deep links) and
  copy buttons.
- Dark is the default theme for everyone. The sun/moon button in the top-right corner
  switches to light and remembers it (`localStorage`). `assets/js/theme.js` is a tiny
  blocking script in `<head>` that applies a saved light choice before the first paint.

## Archive notes

- **Blackrock Depths: Upper City**: the two route maps uploaded in Feb 2024 were never
  archived. The guide shows the original 2014 route maps instead, with a note.
- **Stratholme: Main Gate**: Balnazzar's portrait was broken on the 2024 site. The archive
  copy repairs the tag.
- Raw archived pages are in `classic/<slug>/original.html`, and `classic/manifest.json`
  records the source URL for each one.
