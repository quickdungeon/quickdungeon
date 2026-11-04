# Quick Dungeon

Quick Dungeon is an open-source reimplementation of quickdungeon.com, the World of Warcraft
dungeon quick-guide site that ran on WordPress from about 2014 to 2024. It's live at
https://quickdungeon.app. Each guide gives the tank route as a series of annotated maps, a
one-line tactic for every boss (ready to paste into instance chat with `/i`), and directions
to the entrance.

The core guides, the original site's 26 Classic dungeon guides, were recovered from the
Internet Archive in November 2026, from snapshots taken between July and November 2024.
They've since been updated to match WoW Forever (`REVIEW.md` lists what changed and what
still needs checking), and the site adds pages for WoW Forever's four new dungeons. The guide
text and annotated route maps are the original Quick Dungeon author's work. The game maps,
icons and boss portraits are built on Blizzard's game art.

## Contributing

Any and all contributions are welcome: new or corrected routes and tactics, fixes for the
guides listed in `REVIEW.md`, missing entrance directions, or changes to the site itself.

Please keep to the spirit of the original site: every route and tactic should be as simple
as possible. They mostly serve as reminders for a group that's already in the dungeon, not
full strategy guides. A tactic is a line or two you could paste into instance chat. A route
is the path on the map, with a short note only where the way isn't obvious.
[Editing guides](#editing-guides) explains how a guide is put together.

## Run it

You need Docker with Compose.

| What | Command | URL |
|---|---|---|
| Local copy of the site | `docker compose up -d --build` | http://localhost:8080 |
| Live editing (reloads as you edit `site/`) | `docker compose --profile dev up dev` | http://localhost:1313 |

Options (environment variables for `docker compose`):

- `PORT`: host port for the local site (default `8080`).
- `BASE_URL`: build-time base URL for canonical links, Open Graph and the sitemap
  (default `https://quickdungeon.app/`, set in `site/hugo.toml`). All links inside the site
  are relative, so the site works on any host either way.

Other ways to host it:

- **Behind an existing reverse proxy or a platform that handles TLS** (Traefik, nginx,
  Cloudflare Tunnel, Fly.io, Render, Cloud Run, ...): run the image as-is. It listens on
  8080 over plain HTTP. Health check: `GET :8081/healthz` inside the container.
- **Cloudflare, free** (how https://quickdungeon.app is hosted): see
  [Host it on Cloudflare](#host-it-on-cloudflare-free) below.
- **Other static hosting** (GitHub Pages, Netlify, S3, ...): export the built site with
  `docker build --target public --output type=local,dest=dist .` and upload `dist/`.
  Netlify reads the security and cache headers from `_headers`. Hosts that don't read
  `_headers` won't send those headers, but everything else works.

The image is the official Caddy image plus about 43 MB of site, and runs Caddy as an
unprivileged user (uid 10001). It sets a strict Content-Security-Policy (the font is
self-hosted, and the only outside requests are Cloudflare Web Analytics), uses zstd/gzip
compression, and caches fingerprinted assets for a year.

## Host it on Cloudflare (free)

The site is only static files, so it runs on Cloudflare's free plan as a Worker with static
assets and no Worker code. Static file requests are free and unlimited, and the site
(about 770 files and 43 MB, largest file 1.8 MB) is far inside the free plan's limits of
20,000 files and 25 MiB per file. To build, preview or deploy it yourself, you need Docker
and Node:

| What | Command |
|---|---|
| Sign in to Cloudflare (once) | `npx wrangler@4 login` |
| Preview it the way Cloudflare serves it | `tools/deploy-cloudflare.sh --preview`, then open http://localhost:8787 |
| Check a deploy without uploading anything | `tools/deploy-cloudflare.sh --dry-run` |
| Deploy | `tools/deploy-cloudflare.sh` |

The script builds the site with the same Docker Hugo step as the image, so warnings still
fail the build (the script prints the build log when that happens). It exports the site to
`dist/` and runs `wrangler deploy` with `wrangler.jsonc`. Deploys upload only the files that
changed.

Caddy isn't used on Cloudflare. Instead:

- `site/static/_headers` sets the same security headers (Content-Security-Policy and the
  rest) and cache rules as the Caddyfile. When you change one, change the other to match.
- `wrangler.jsonc` serves `404.html` for unknown URLs, redirects `/deadmines` to
  `/deadmines/`, and puts the site on quickdungeon.app.
- Cloudflare compresses responses itself.

## Layout

```
site/                      Hugo project (Hugo 0.147, built inside Docker; no local install needed)
  hugo.toml
  content/dungeons/<slug>/ one page bundle per guide: index.md (structured YAML) + images/
  data/expansions/         which guides each expansion section lists (the home page sorts them by level)
  data/levels.yaml         recommended level range for each guide, per expansion section
  layouts/                 templates (home, guide page, 404, partials; Web Analytics in _partials/analytics.html)
  assets/css/main.css      all styles
  assets/js/site.js        theme toggle, search, route-map stepper, copy-to-chat buttons
  assets/js/theme.js       applies a saved light theme before first paint
  assets/logo/logo.png     the logo (built by tools/make_logo.py)
  static/                  font (Archivo, OFL licence), favicon.ico, apple-touch-icon.png,
                           _headers (security and cache headers on Cloudflare)
Dockerfile, Caddyfile      build with Hugo, serve with Caddy
wrangler.jsonc             Cloudflare config (used by tools/deploy-cloudflare.sh)
.github/workflows/         deploy.yml: deploys to Cloudflare on every push to mainline
compose.yaml               local + dev services
classic/                   the raw recovered archive (original HTML + images); not deployed
artist-maps/               unmodified originals of third-party maps (Santiago Reyes); not deployed
game-maps/                 maps extracted from the WoW Forever client (entrance areas, new-dungeon overviews)
tools/                     archive downloader, archive-to-Hugo converter, game-file extraction tools, logo builder,
                           Cloudflare deploy script
REVIEW.md                  guides changed to match WoW Forever that still need checking
LICENSE                    MIT licence for the code (see License below)
```

Guide URLs match the old WordPress site (`/shadowfang-keep/`), so old links and search
results keep working if the domain comes back. Guides that were merged or split to match
WoW Forever list their old URLs under `aliases:`, which Hugo turns into redirect pages (for
example `/maraudon-foulspore-cavern/` goes to `/maraudon/`).

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
review: "..."         # optional: a notice under the title (see REVIEW.md)
source:               # where the guide came from in the archive (a record; not shown on the page)
  url: "https://web.archive.org/web/20241111045715/https://quickdungeon.com/shadowfang-keep/"
  captured: "2024-11-11"
bosses:
  - number: 2         # matches the marker drawn on the route map; leave out if it isn't marked
    name: "Baron Silverlaine"
    part: "Upper City"  # optional: which part of a merged dungeon (Maraudon, Blackrock Depths)
    tag: "rare"       # optional: optional, rare, event, heroic, or any short label ("Warlock quest")
    image: "images/baron-silverlaine-wowhead.png"
    tactics:
      - "Curses his targets with Veil of Shadow..."   # shown and copied as "/i ..."
```

Boss names follow Wowhead's WoW Forever Dungeon Journal, with the spelling from the game
files where the two disagree. REVIEW.md has the details.

Images go in the guide's `images/` folder. Hugo converts them to WebP and makes the list
thumbnails. If a front-matter path points at a missing image, the dev server prints a
warning and the Docker build fails, naming the file.

## Boss portraits (Wowhead)

Most boss portraits come from [Wowhead's WoW Forever Dungeon Journal](https://www.wowhead.com/forever/dungeon-journal)
(saved as `images/<boss>-wowhead.png` in each guide, resized to 200×200). Wowhead hosts them as
guide images, and one (Shade of Eranikus) is Blizzard's own render from
render.worldofwarcraft.com. The site footer credits Wowhead on every page
(`layouts/_partials/site-footer.html`).

## Third-party maps (credit required)

All four new WoW Forever dungeon pages (City of Dalaran with its city and sewers maps, Ruins
of Lordaeron, Hall of Thanes, Excavation Site: Wetlands) show maps by **Santiago Reyes**
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

## Logo

The logo is the three classic tanks' signature abilities, taken from the WoW Forever client's
icons: Defensive Stance (warrior, in front), Righteous Fury (paladin) and Bear Form (druid),
each in a gold-rimmed round frame like the game's role icons. `tools/make_logo.py` extracts
the icons and builds `site/assets/logo/logo.png` (Hugo resizes it for the header and home
page), `site/static/favicon.ico` and `site/static/apple-touch-icon.png`:

`python3 -I tools/make_logo.py "/path/to/World of Warcraft" wowf site`

It needs Pillow, which reads the game's BLP textures.

## Maps from the game client

`site/data/entrance_maps.yaml` lists in-game maps that appear under a guide's entrance
directions (Blackrock Mountain, Gnomeregan, Uldaman). The images are in
`site/assets/game-maps/`. They're kept out of `content/` so that rerunning the converter
doesn't delete them. `game-maps/README.md` describes every extracted map, including
top-down terrain overviews of the new WoW Forever dungeons. The site uses Santiago Reyes's
maps for those, so the overviews are kept for reference only.

The extraction tools only read the game files:

- `tools/casc_read.py WOW_DIR PRODUCT OUT_DIR FDID...` extracts files by FileDataID from a
  local CASC install (pure Python, no third-party code).
- `tools/stitch_uimap.py DB2_DIR WOW_DIR PRODUCT OUT_DIR ART_ID...` assembles world-map art
  from its tiles. The UiMapArt* tables come as CSV from `https://wago.tools/db2/<Table>/csv?build=<version>`.
- `tools/wdt_minimap.py WOW_DIR PRODUCT WDT_FDID OUT.png` stitches a map's terrain minimap tiles.

For example (WoW Forever is product `wowf`):
`python3 -I tools/casc_read.py "/path/to/World of Warcraft" wowf out 603971`

## License

The code (templates, styles, scripts, build and deploy setup, and the tools) is under the
MIT License; see `LICENSE`. That doesn't cover the content, which stays with its owners:

- the guide text and annotated route maps: the original Quick Dungeon author
- game art, maps, icons and boss portraits: Blizzard Entertainment (the portraits are via
  Wowhead's WoW Forever Dungeon Journal)
- the WoW Forever dungeon maps: Santiago Reyes, on the terms in
  [Third-party maps](#third-party-maps-credit-required)
- the Archivo font: the SIL Open Font License (`site/static/fonts/Archivo-OFL.txt`)
