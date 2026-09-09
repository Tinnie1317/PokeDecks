# Pokémon Card Tracker

A simple static webapp for tracking which Pokémon TCG card variants you own.
Open the page, browse cards by set, and check off the ones you've collected.
Your collection is saved in your browser (localStorage) — no account or
server needed.

## Deploying this (one manual step, total)

1. Push this whole repo to GitHub as-is — nothing to move or rename.
2. In the repo, go to **Settings → Pages** → under "Build and deployment",
   set **Source: Deploy from a branch**, **Branch: main**, **Folder: /docs**
   → Save.
3. Wait a minute, then GitHub gives you a live URL (something like
   `https://yourusername.github.io/reponame/`).

That's it — that one setting is the only thing GitHub won't let a file in
the repo do for you (Pages has to be turned on by the repo owner in the UI).
Everything else, including keeping the card data fresh, is automatic from
here on (see below).

## Keeping the data fresh — automatic

`.github/workflows/sync-data.yml` runs every Monday, pulls the latest card
data from the free Pokémon TCG API, and commits any changes straight to
`docs/data`. You don't need to run anything yourself. It also runs:

- Automatically if you ever edit `scripts/sync_data.py`
- On demand — go to the **Actions** tab → "Sync card data" → **Run workflow**

The very first run (whenever you trigger it, or the first scheduled Monday)
is what replaces the small 5-card sample dataset with the full card catalog.
If you don't want to wait for Monday, trigger it manually right after your
first push.

## How it's organized

```
docs/                   <- served directly by GitHub Pages, no build step
  index.html             Title page (links to the 3 sections below)
  current-set.html       Shows only the most recently released set
  all-sets.html          Shows every set, grouped, newest first
  collection.html        Shows only the cards you've checked off
  css/style.css
  js/
    data.js               Fetches manifest.json / set files
    collection.js          Reads/writes your checked cards to localStorage
    grid.js                 Renders the checkbox grid
  data/
    manifest.json          List of every set (id, name, release date)
    sets/
      base1.json            One file per set, listing every card VARIANT
      ...
scripts/
  sync_data.py            Pulls fresh data from the Pokémon TCG API
  requirements.txt
.github/workflows/
  sync-data.yml           Runs sync_data.py weekly and auto-commits results
```

### Why "variants" are separate entries

Each checkbox in the grid represents one **physical printing** of a card,
not just the card itself — e.g. "Charizard (Base Set) — Holofoil" is a
separate entry from "Charizard (Base Set) — Reverse Holofoil" if both
printings exist. Every entry also carries two extra fields:

- `print_variant` — the physical printing (Normal, Holofoil, Reverse
  Holofoil, 1st Edition, 1st Edition Holofoil, Unlimited, Unlimited
  Holofoil). This is what determines whether a card gets one checkbox or
  several.
- `special_variant` — a broader category derived from the card's rarity
  (Full Art, Alt Art, Rainbow Rare, Gold Secret Rare, Radiant, VMAX, GX,
  Trainer Gallery, Promo, etc.), shown as extra detail on each tile.

## Running the sync script yourself (optional)

You never have to — the Actions workflow does it for you — but if you want
to run it locally:

```bash
cd scripts
pip install -r requirements.txt
python sync_data.py
```

Optional: set a `POKEMONTCG_API_KEY` environment variable (free signup at
https://dev.pokemontcg.io) to raise your rate limit from 1,000 to 20,000
requests/day. Not required — a full sync uses well under 1,000 requests.
To use a key in the automated workflow instead, add it as a repo secret
named `POKEMONTCG_API_KEY` and uncomment the two lines near the bottom of
`.github/workflows/sync-data.yml`.

## Notes / things to adjust later

- Currently English-only. The API also has some non-English data under
  different endpoints if you want to expand later.
- `all-sets.html` loads every set's JSON file, which is fine for a
  personal project but will feel slow once the full ~500-set dataset is
  in place. Pagination or lazy-loading per set (only fetch a set's cards
  when its section is scrolled into view) would be the next improvement.
