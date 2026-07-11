"""Download poem corpora for the seven Persian poets from Ganjoor (گنجور).

Ganjoor exposes a public REST API at https://api.ganjoor.net (no key needed).
For each poet we walk the category tree and download up to
GANJOOR_MAX_POEMS_PER_POET poems as plain text, saving them to
data/ganjoor/<poet_id>.json for the extraction pipeline to pick up.

Usage:
    python -m tools.download_ganjoor                 # all poets
    python -m tools.download_ganjoor --poet hafez    # one poet
    python -m tools.download_ganjoor --max-poems 50  # smaller corpus
"""

import json
import time

import click
import requests
from loguru import logger

from philoagents.config import settings

# Ganjoor URL slugs for our poets.
GANJOOR_POET_SLUGS = {
    "saadi": "/saadi",
    "hafez": "/hafez",
    "molavi": "/moulavi",
    "saeb": "/saeb",
    "bidel": "/bedil",
    "iqbal": "/iqbal",
    "rahi": "/rahi",
}

# Fallback: search the full poet list by (partial) Persian name.
GANJOOR_POET_NAMES = {
    "saadi": "سعدی",
    "hafez": "حافظ",
    "molavi": "مولوی",
    "saeb": "صائب",
    "bidel": "بیدل",
    "iqbal": "اقبال",
    "rahi": "رهی معیری",
}

REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.2  # be polite to the free API


def api_get(path: str, params: dict | None = None):
    url = f"{settings.GANJOOR_API_BASE}{path}"
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Ganjoor API error for {url}: {e}")
        return None


def resolve_poet(poet_id: str):
    """Resolve a poet id to its Ganjoor payload (contains 'poet' and 'cat')."""
    slug = GANJOOR_POET_SLUGS.get(poet_id)
    if slug:
        payload = api_get("/api/ganjoor/poet", params={"url": slug})
        if payload and payload.get("cat"):
            return payload

    logger.warning(f"Slug lookup failed for '{poet_id}', searching poet list...")
    name_query = GANJOOR_POET_NAMES.get(poet_id, poet_id)
    poets = api_get("/api/ganjoor/poets") or []
    for poet in poets:
        if name_query in (poet.get("name") or ""):
            payload = api_get(f"/api/ganjoor/poet/{poet['id']}")
            if payload and payload.get("cat"):
                return payload

    return None


def collect_poem_summaries(root_cat: dict, limit: int) -> list[dict]:
    """Depth-first walk of the category tree, collecting poem summaries."""
    poems: list[dict] = []

    def walk(cat_id: int) -> None:
        if len(poems) >= limit:
            return
        payload = api_get(f"/api/ganjoor/cat/{cat_id}", params={"poems": "true"})
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        if not payload:
            return
        cat_data = payload.get("cat") or payload

        for poem in cat_data.get("poems") or []:
            poems.append(poem)
            if len(poems) >= limit:
                return

        for child in cat_data.get("children") or []:
            walk(child["id"])
            if len(poems) >= limit:
                return

    walk(root_cat["id"])
    return poems


def fetch_poem(poem_id: int):
    """Download one poem and normalize it to {title, url, text}."""
    payload = api_get(f"/api/ganjoor/poem/{poem_id}")
    if not payload:
        return None

    text = payload.get("plainText") or ""
    if not text.strip():
        verses = payload.get("verses") or []
        text = "\n".join(v.get("text", "") for v in verses)
    if not text.strip():
        return None

    url = payload.get("fullUrl") or ""
    if url.startswith("/"):
        url = f"https://ganjoor.net{url}"

    return {
        "title": payload.get("fullTitle") or payload.get("title") or "",
        "url": url,
        "text": text.strip(),
    }


@click.command()
@click.option(
    "--poet",
    "poet_ids",
    multiple=True,
    help="Poet id(s) to download (default: all seven).",
)
@click.option(
    "--max-poems",
    default=None,
    type=int,
    help="Max poems per poet (default: settings.GANJOOR_MAX_POEMS_PER_POET).",
)
def main(poet_ids, max_poems) -> None:
    targets = list(poet_ids) or list(GANJOOR_POET_SLUGS)
    limit = max_poems or settings.GANJOOR_MAX_POEMS_PER_POET

    out_dir = settings.GANJOOR_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    for poet_id in targets:
        logger.info(f"=== {poet_id} ===")

        payload = resolve_poet(poet_id)
        if not payload:
            logger.error(f"Could not resolve '{poet_id}' on Ganjoor; skipping.")
            continue

        root_cat = payload["cat"]
        summaries = collect_poem_summaries(root_cat, limit)
        logger.info(f"Found {len(summaries)} poems for {poet_id}, downloading text...")

        poems = []
        for i, summary in enumerate(summaries, start=1):
            poem = fetch_poem(summary["id"])
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            if poem:
                poems.append(poem)
            if i % 25 == 0:
                logger.info(f"  {i}/{len(summaries)} poems downloaded")

        out_file = out_dir / f"{poet_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(poems, f, ensure_ascii=False, indent=1)

        logger.success(f"Saved {len(poems)} poems to {out_file}")


if __name__ == "__main__":
    main()
