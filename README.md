# Quick Dungeon archive

Personal offline archive of the World of Warcraft dungeon guides that used to live at
quickdungeon.com (a WordPress site, first built ~2014, last seen live in late 2024).
Recovered from the Internet Archive's Wayback Machine in November 2026.

The guide text and annotated route maps are the original author's work, and the maps and
boss portraits are built on Blizzard's game art. This is a private copy, so get the author's
permission before republishing it.

## Contents

- `classic/index.html`: open this in a browser. It covers all 26 guides in the site's
  "Classic" section, in the order the site's homepage listed them.
- `classic/<slug>/index.html`: a cleaned-up local copy of each guide. The route map tabs
  and the "Click for Dungeon Entrance" panels work offline (`classic/widgets.js`).
- `classic/<slug>/original.html`: the raw archived HTML, untouched.
- `classic/<slug>/images/`: every image the guide referenced.
- `classic/manifest.json`: the source Wayback URL, the image list and any gaps for each guide.

## Known gaps and fixes

- **Blackrock Depths: Upper City**: the two route maps uploaded in Feb 2024 (LFD and full)
  were never archived. The page has notes in their place and shows the original 2014 route
  maps from the 2018 version of the page (`images/2014-*.jpg`, raw page in `original-2018.html`).
  This was a manual edit, so rerunning `qd_fetch.py` on that guide will overwrite it.
- **Stratholme: Main Gate**: on the 2024 site, Balnazzar's portrait showed up as stray text
  (WordPress had mangled the `<img>` tag). The local copy repairs the tag so the image shows.
- Several 2014 images only exist in the archive under their original capitalised filenames
  (for example `Maraudon-The-Wicked-Grotto-Dungeon-Map1.jpg`). The downloader finds these
  automatically through the archive's CDX index.

## Re-running / fetching other expansions

```
python3 -I tools/qd_fetch.py <out_dir> tools/capture-timestamps.txt <slug> [<slug> ...]
python3 -I tools/qd_index.py <out_dir> <slug> [<slug> ...]
```

The downloader can resume after an interruption because it skips files that already exist.
The Wayback Machine throttles fast clients (connections get refused), so the script waits
1.5s between requests and backs off on errors. Slugs for the other expansions are the page
paths in `tools/capture-timestamps.txt` (for example `the-stonevault`, `utgarde-keep`).
