# In-game maps extracted from the WoW Forever client

Source: local install, product `wowf`, build 1.60.1.70707. Extracted with
`tools/stitch_uimap.py` (tiles from the CASC archive via `tools/casc_read.py`, tile layout
from the UiMapArt* tables at https://wago.tools/db2/UiMapArtTile/csv?build=1.60.1.70707).

These are "microdungeon" maps (small caves and entrance areas) that are in the client's
tables but not shown in-game. Blizzard's game art.

| File | UiMapArt | Game texture | Used in |
|---|---|---|---|
| blackrock-mountain-main.png | 1225 (= 1221) | microdungeon/burningsteppes/blackrockmountain14 | Lower Blackrock Spire, both Blackrock Depths guides |
| blackrock-mountain-depths.png | 1227 (= 1223) | .../blackrockmountain16 | both Blackrock Depths guides |
| blackrock-mountain-caverns-burning-steppes.png | 1226 | .../burningsteppes/blackrockmountain15 | (Blackrock Caverns, Cataclysm) |
| blackrock-mountain-caverns-searing-gorge.png | 1222 | .../searinggorge/blackrockmountain15 | (slightly different variant of the above) |
| gnomeregan-entrance.png | 1217 | microdungeon/dunmorogh/gnomeregan10 | Gnomeregan |
| uldaman-entrance.png | 1208 | microdungeon/badlands/uldaman18 | Uldaman |
| caverns-of-time-1.png | 1257 | microdungeon/tanaris/cavernsoftime17 | (Caverns of Time dungeons, TBC+) |
| caverns-of-time-2.png | 1258 | microdungeon/tanaris/cavernsoftime18 | (Caverns of Time dungeons, TBC+) |

## New WoW Forever dungeons: minimap overviews (`new-dungeons/`)

The five 5-player dungeons in `wowf` 1.60.1.70707 that aren't in Classic Era 1.15.9.70576.
None of them has world-map art, so these are stitched from the terrain minimap tiles
(512px per 533-yard tile) listed in each map's WDT. `tools/wdt_minimap.py` makes the full
overview, then it's cropped by hand to the dungeon area. These are top-down terrain renders
with no labels, route lines or boss markers.

| Dungeon | Map ID | File | Notes | Encounters (in the game's table order) |
|---|---|---|---|---|
| City of Dalaran | 2959 | city-of-dalaran.png | Dalaran on its hill by Lordamere Lake, inside the purple barrier | Arcane Anomaly, Fel Ancient, Mana Devourer, Mana Elemental, Unstable Sentinel, Shade of the Archmage, Lyn the Ignored, Atrexis the Grave Knight, Mana Wraith |
| Ruins of Lordaeron | 2999 | ruins-of-lordaeron.png | the walled city above Undercity | Witherfang, The Abandoned, The Butcher, Rath'mael, Lordaeron Captain, Viktor the Vile, Bjork |
| The Hall of Thanes | 3065 | the-hall-of-thanes.png | a dwarven hall complex; everything around it is grey placeholder terrain | Faldrim Anvilmar, Infurnus, Plunder, Durgen Dirgehammer |
| Excavation Site: Wetlands | 2998 | excavation-site-wetlands.png | a copy of the whole Wetlands zone, scaled to 50%, with grey placeholder and duplicated tiles; looks unfinished, and the dungeon area isn't identifiable | Saltspine, Shadetooth, Highland Horror, Relic Guardian |
| Manor Mistmantle | 3109 | none | its WDT (FileDataID 7937200) isn't in this build's root manifest, so the map data hasn't shipped yet | none listed |

Ruins of Lordaeron, The Hall of Thanes and Excavation Site: Wetlands now show Santiago Reyes's
hand-drawn maps on the site (with credit; see the main README), and City of Dalaran shows
his city and sewers maps (saved by hand from ArtStation). These terrain overviews aren't used
on the site any more; they're kept here for reference.
