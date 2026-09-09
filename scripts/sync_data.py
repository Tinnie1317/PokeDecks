"""
sync_data.py

Pulls the full English-language Pokemon TCG card catalog from the
pokemontcg.io API and writes it into the per-set JSON files (plus a
manifest) that the web app in /web reads.

This script needs an internet connection to run, so run it locally,
in GitHub Codespaces, or as a GitHub Actions job -- not somewhere with
network access blocked.

Usage:
    pip install -r requirements.txt
    python sync_data.py

Optional:
    Set the POKEMONTCG_API_KEY environment variable to use a registered
    API key. This raises your daily rate limit from 1,000 requests/day
    (no key) to 20,000 requests/day (free registered key). Get a key at
    https://dev.pokemontcg.io -- not required to run this script.

Re-running this script is safe: it overwrites the data files with a
fresh pull, so run it whenever a new set releases to pick up new cards.
"""

import os
import json
import time
import requests

API_BASE = "https://api.pokemontcg.io/v2"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
SETS_DIR = os.path.join(DATA_DIR, "sets")

API_KEY = os.environ.get("POKEMONTCG_API_KEY")
HEADERS = {"X-Api-Key": API_KEY} if API_KEY else {}

# Maps the API's raw "rarity" string to a broader, human-friendly
# "special variant" category. This is kept as a SEPARATE field from
# print_variant (which describes the physical printing -- holo, reverse
# holo, 1st edition, etc.) so the app can show/filter on either one.
# Extend this dictionary as new rarity strings show up in new sets --
# anything not listed here just falls back to using the raw rarity text.
SPECIAL_VARIANT_MAP = {
    "Common": "Standard",
    "Uncommon": "Standard",
    "Rare": "Standard",
    "Rare Holo": "Standard",
    "Promo": "Promo",
    "Rare Holo GX": "GX",
    "Rare Holo EX": "EX",
    "Rare Holo V": "V",
    "Rare Holo VMAX": "VMAX",
    "Rare Holo VSTAR": "VSTAR",
    "Rare BREAK": "BREAK",
    "Rare Prime": "Prime",
    "Rare ACE": "ACE SPEC",
    "Rare Prism Star": "Prism Star",
    "Amazing Rare": "Amazing Rare",
    "Radiant Rare": "Radiant",
    "Rare Rainbow": "Rainbow Rare",
    "Rare Secret": "Secret Rare",
    "Rare Shiny": "Shiny",
    "Rare Shiny GX": "Shiny GX",
    "Rare Shining": "Shining",
    "Rare Holo Star": "Gold Star",
    "Rare Ultra": "Ultra Rare",
    "Rare Full Art": "Full Art",
    "Trainer Gallery Rare Holo": "Trainer Gallery",
    "Special Illustration Rare": "Illustration Rare",
    "Illustration Rare": "Illustration Rare",
    "Hyper Rare": "Hyper Rare",
    "Double Rare": "Double Rare",
    "ACE SPEC Rare": "ACE SPEC",
    "Classic Collection": "Classic Collection",
    "LEGEND": "LEGEND",
}


def special_variant_for(rarity):
    if not rarity:
        return "Other"
    return SPECIAL_VARIANT_MAP.get(rarity, rarity)


def print_variants_for(card):
    """Looks at the tcgplayer price object's keys to see which physical
    printings actually exist for this card (a card only gets a
    'reverseHolofoil' key if a reverse holo printing of it exists, etc).
    Falls back to a single 'Normal' entry if no pricing data is present,
    which happens for some very old or obscure promo cards."""
    prices = (card.get("tcgplayer") or {}).get("prices") or {}
    if not prices:
        return ["Normal"]

    label_map = {
        "normal": "Normal",
        "holofoil": "Holofoil",
        "reverseHolofoil": "Reverse Holofoil",
        "1stEditionNormal": "1st Edition",
        "1stEditionHolofoil": "1st Edition Holofoil",
        "unlimited": "Unlimited",
        "unlimitedHolofoil": "Unlimited Holofoil",
    }
    variants = [label_map[key] for key in prices.keys() if key in label_map]
    return variants or ["Normal"]


def fetch_all_sets():
    resp = requests.get(f"{API_BASE}/sets", params={"orderBy": "releaseDate"}, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["data"]


def fetch_cards_for_set(set_id):
    cards = []
    page = 1
    while True:
        resp = requests.get(
            f"{API_BASE}/cards",
            params={"q": f"set.id:{set_id}", "page": page, "pageSize": 250},
            headers=HEADERS,
        )
        resp.raise_for_status()
        payload = resp.json()
        cards.extend(payload["data"])
        if page * 250 >= payload["totalCount"]:
            break
        page += 1
        time.sleep(0.2)  # be polite to the free tier
    return cards


def build_entries(card):
    """Turns one API card object into one or more 'checkbox entries' --
    one per physical print variant that exists for that card."""
    entries = []
    for pv in print_variants_for(card):
        pv_slug = pv.lower().replace(" ", "-")
        entries.append({
            "id": f"{card['id']}-{pv_slug}",
            "card_id": card["id"],
            "name": card["name"],
            "number": card.get("number"),
            "set_id": card["set"]["id"],
            "set_name": card["set"]["name"],
            "rarity": card.get("rarity"),
            "special_variant": special_variant_for(card.get("rarity")),
            "print_variant": pv,
            "image_small": (card.get("images") or {}).get("small"),
            "image_large": (card.get("images") or {}).get("large"),
        })
    return entries


def main():
    os.makedirs(SETS_DIR, exist_ok=True)
    sets = fetch_all_sets()
    manifest = []

    for s in sets:
        print(f"Fetching {s['name']} ({s['id']})...")
        cards = fetch_cards_for_set(s["id"])
        entries = []
        for card in cards:
            entries.extend(build_entries(card))

        out_path = os.path.join(SETS_DIR, f"{s['id']}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        manifest.append({
            "set_id": s["id"],
            "set_name": s["name"],
            "series": s.get("series"),
            "release_date": s.get("releaseDate"),
            "card_count": len(cards),
            "variant_count": len(entries),
        })

    manifest.sort(key=lambda m: m["release_date"] or "")
    with open(os.path.join(DATA_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(manifest)} sets written to {SETS_DIR}")


if __name__ == "__main__":
    main()
