# Guides to review after matching WoW Forever

In November 2026 the dungeon list and every boss list were brought in line with
[Wowhead's WoW Forever Dungeon Journal](https://www.wowhead.com/forever/dungeon-journal).
Where the journal and the WoW Forever game files (build 1.60.1.70707) disagree, the game files
win:

- **Dungeon names and level ranges** come from the in-game Group Finder listing board
  (`GroupFinderActivity`). WoW Forever has no Dungeon Finder queue.
- **Boss names** use the spelling in the game's encounter table (`DungeonEncounter`, 5-player
  difficulty only, so Season of Discovery raid rows are ignored). Every encounter in that table
  is listed, even where the journal leaves it out.
- **Extra journal entries** that aren't encounters (rares, events, summoned bosses) are
  kept, tagged *Rare* or *Event* where the journal marks them.
- Bosses an old guide already had keep their route-map number, portrait and tactics.
  Bosses with no number aren't marked on the route maps. **Heroic notes were removed**
  (WoW Forever has no heroic dungeons).

Everything removed is still in git history: the last version before this change is commit
`3a6572d`.

## Needs review: written for retail (14 pages)

These pages show a notice under the title until they're checked. The route maps are from
retail's redesigned versions of these dungeons, and the tactics kept from the old guides
describe retail's version of each fight. When a page is done, delete its `review:` line (and
its `bosses_note:` if the default wording fits).

- [ ] **Ragefire Chasm.** All 4 bosses are new (Oggleflint, Taragaman the Hungerer, Jergosh the
      Invoker, Bazzalan). The retail map is a different layout. No tactics.
- [ ] **Deadmines.** 8 bosses. Retail's Glubtok, Helix Gearbreaker, Foe Reaper 5000, Admiral
      Ripsnarl and Vanessa VanCleef are gone. Tactics kept for Cookie (#5, was "'Captain' Cookie").
- [ ] **Shadowfang Keep.** 10 entries. Retail's Baron Ashbury, Lord Walden and Lord Godfrey are
      gone. Tactics kept for Baron Silverlaine (#2) and Commander Springvale (#3); their heroic
      notes were removed.
- [ ] **Blackfathom Deeps.** 8 entries. Retail's Domina, Subjugator Kor'ul, Thruk, Executioner
      Gore, Guardian of the Deep and Twilight Lord Bathiel are gone. Tactics kept for Ghamoo-ra
      (#1) and Aku'mai (#7, was "Aku'mai the Devourer").
- [ ] **Stormwind Stockades** (renamed from Stormwind Stockade). All 6 entries are new; retail's
      Lord Overheat, Randolph Moloch and Hogger are gone. No tactics.
- [ ] **Razorfen Kraul.** 8 entries. Retail's Hunter Bonetusk is gone. Tactics kept for Roogug
      (#2), Overlord Ramtusk (#3, was "Warlord Ramtusk"), Blind Hunter (#4, was "Groyat, the
      Blind Hunter") and Charlga Razorflank (#5).
- [ ] **Razorfen Downs.** 6 entries. Retail's Aarux, Mushlump and Death Speaker Blackthorn are
      gone. Tactics kept for Mordresh Fire Eye (#2) and Amnennar the Coldbringer (#5).
- [ ] **Scholomance.** 15 entries; the old guide was retail's rebuilt Scholomance. Retail's
      Instructor Chillheart and Lilian Voss are gone. Tactics kept for Jandice Barov (#2, heroic
      note removed), Rattlegore (#3) and Darkmaster Gandling (#5).
- [ ] **Sunken Temple** (was The Temple of Atal'Hakkar). 7 entries. Retail's "Wardens of the
      Dream" is split into the journal's two pairs, Weaver & Dreamscythe and Hazzas & Morphaz.
      Both are #3, and the old tactic was divided between them. Tactics kept for Jammal'an the
      Prophet & Ogom the Wretched (#1), Avatar of Hakkar (#2) and Shade of Eranikus (#4).
      Atal'alarion and Atal'ai Defenders are new.
- [ ] **Scarlet Monastery - Graveyard** (new page; `/scarlet-monastery/` redirects here). Map is
      retail's Scarlet Monastery map 1; its "Pile of Corpses" note is a retail mechanic. 5
      entries, no tactics.
- [ ] **Scarlet Monastery - Library** (new page; `/scarlet-halls/` redirects here). Maps are
      retail's Scarlet Halls maps 1 and 2; the Training Grounds shield note is retail. 2 bosses,
      no tactics.
- [ ] **Scarlet Monastery - Armory** (new page). Map is retail's Scarlet Halls map 2. Herod, no
      tactics.
- [ ] **Scarlet Monastery - Cathedral** (new page). Map is retail's Scarlet Monastery map 2.
      Tactics kept for Scarlet Commander Mograine & High Inquisitor Whitemane (#3, from retail's
      Whitemane). High Inquisitor Fairbanks is new.
- [ ] **Upper Blackrock Spire** (new page). The archive only has the later retail version, so
      this page has the boss list and entrance directions (copied from Lower Blackrock Spire)
      and no route or tactics.

Retail bosses removed with the old Scarlet guides: Houndmaster Braun, Armsmaster Harlan,
Flameweaver Koegler, Thalnos the Soulrender, Brother Korloff.

## Updated: route and tactics still fit (9 pages)

These already matched WoW Forever. They gained the journal's extra entries, which have no
tactics or portraits yet and no number on the maps.

- [ ] **Gnomeregan:** + Dark Iron Ambassador (rare).
- [ ] **Zul'Farrak:** + Sergeant Bly, + Zerillis (rare). "Nekrum & Sezz'ziz" renamed to
      "Nekrum Gutchewer & Shadowpriest Sezz'ziz".
- [ ] **Maraudon:** merged from the three wing guides (their URLs redirect here). Each boss is
      labelled with its part, and numbers match that part's maps. + Meshlok the Harvester (rare).
      The Earth Song Falls entrance mentions a "Portal to Inner Maraudon"; check it's there.
- [ ] **Blackrock Depths:** merged from Detention Block and Upper City (their URLs redirect
      here), labelled by part. + The Vault, + Princess Moira Bronzebeard, + Panzor the Invincible
      (rare); Warder Stilgiss is tagged rare, as in the journal. The Upper City's "LFD Map" step was
      removed (no Dungeon Finder; its route map was never archived anyway).
- [ ] **Dire Maul (East):** + Pusillin, + Isalien.
- [ ] **Dire Maul (West):** + Tsu'zee (rare), + Lord Hel'nurath (Warlock quest).
- [ ] **Lower Blackrock Spire:** + Mor Grayhoof, + Spirestone Butcher, Spirestone Battle Lord,
      Bannok Grimaxe, Crystal Fang (all rare).
- [ ] **Stratholme (Main Gate):** + Ezra Grimm, + Postmaster Malown, + Skul (rare),
      + Crimson Hammersmith; Hearthsinger Forresten is tagged rare.
- [ ] **Stratholme (Service Gate):** + Stonespine (rare), + Black Guard Swordsmith.

## Unchanged

Wailing Caverns, Uldaman and Dire Maul (North) already matched.

The four new WoW Forever dungeons keep the game's boss lists, because Wowhead's journal
disagrees with this build:

| Dungeon | Game files | Wowhead journal |
|---|---|---|
| Hall of Thanes | Infurnus | Magmatus instead |
| Ruins of Lordaeron | The Butcher, Lordaeron Captain | neither; has "The Baron" |
| City of Dalaran | Mana Elemental, Mana Wraith | neither; has "Arcanic Enigma" |
| Excavation Site: Wetlands | Highland Horror | missing |

## Where the game files overrode the journal

| Journal | Site (game files) |
|---|---|
| The Deadmines | Deadmines |
| The Stockade | Stormwind Stockades |
| Scarlet Monastery: Graveyard (and the other wings) | Scarlet Monastery - Graveyard |
| The Temple of Atal'Hakkar | Sunken Temple |
| Dire Maul East / West / North | Dire Maul (East) / (West) / (North) |
| Stratholme Live / Undead | Stratholme (Main Gate) / (Service Gate) |
| The Hall of Thanes | Hall of Thanes |
| Level ranges (e.g. Ragefire Chasm 15–25) | Group Finder ranges (Ragefire Chasm 13–18) |
| Sneed's Shredder | Sneed |
| Ghamoo-Ra | Ghamoo-ra |
| Atal'alrion | Atal'alarion |
| Herod, The Scarlet Champion | Herod |
| Kirtonos the Herald | Kirtonos |
| Ras Frostwhisper | Ras Frostwhisperer (the encounter table's spelling; likely a typo in the game data) |
| Ring of the Law | Ring of Law |
| Chest of the Seven | The Seven |
| Bael'gar | Bael'Gar |
| Tzu'see | Tsu'zee |
| Plaguemaw the Rotting Event | Plaguemaw the Rotting |

"Gelihast" (Blackfathom Deeps) follows the journal: the game spells it "Geilhast" in the
5-player row but "Gelihast" in another row of the same table.

Encounters the game lists that the journal leaves out, so they were added: Lorgus Jett
(Blackfathom Deeps), The Vault and Princess Moira Bronzebeard (Blackrock Depths), Lord Valthalak
(Upper Blackrock Spire), Crimson Hammersmith (Stratholme Main Gate), Black Guard Swordsmith
(Stratholme Service Gate).

## Other edits

- **No Dungeon Finder.** Text that mentioned it was reworded or removed:
  - Gnomeregan: "Be aware that often LFD groups skip first boss…" now reads "groups often skip…".
  - Maraudon: "Killing Princess Theradras (boss 2) completes the LFD dungeon but the group should
    stay & jump down into the water to kill Rotgrip (boss 3)." now reads "After Princess Theradras
    (boss 2), jump down into the water to kill Rotgrip (boss 3)."
  - Blackrock Depths: the "LFD Map" route step (see above).
- **Portraits.** 214 of the 229 bosses now use the journal's portrait (saved as
  `images/<journal-boss>-wowhead.png`, 200×200; tall figures cropped to head and shoulders,
  scene shots cropped square). They replace the original site's portraits, which are still in
  `classic/` and git history. Every guide using them credits Wowhead under the boss list.
  - Kept the original portrait (the journal doesn't list them): Ribbly Screwspigot, Plugger
    Spazzring, Cho'Rush the Observer. The journal shows King Gordok and Cho'Rush on one card,
    and its picture is of Gordok alone, so it's used for King Gordok only.
  - No picture anywhere yet: Lorgus Jett, The Vault, Princess Moira Bronzebeard, Lord Valthalak,
    Crimson Hammersmith, Black Guard Swordsmith, Infurnus, The Butcher, Lordaeron Captain,
    Highland Horror, Mana Elemental, Mana Wraith.
  - [ ] Check the two hand-cropped scene shots: Oggleflint (Ragefire Chasm) and Scarlet
    Commander Mograine & High Inquisitor Whitemane (Cathedral).
