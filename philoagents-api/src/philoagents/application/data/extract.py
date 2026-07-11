import json
from typing import Generator
from urllib.parse import unquote

import requests
from langchain_core.documents import Document
from loguru import logger
from tqdm import tqdm

from philoagents.config import settings
from philoagents.domain.philosopher import Philosopher, PhilosopherExtract
from philoagents.domain.philosopher_factory import PhilosopherFactory


def get_extraction_generator(
    philosophers: list[PhilosopherExtract],
) -> Generator[tuple[Philosopher, list[Document]], None, None]:
    """Extract documents for a list of poets, yielding one at a time.

    Args:
        philosophers: A list of PhilosopherExtract objects containing poet information.

    Yields:
        tuple[Philosopher, list[Document]]: A tuple containing the poet object and a list of
            documents extracted for that poet.
    """

    progress_bar = tqdm(
        philosophers,
        desc="Extracting docs",
        unit="poet",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        ncols=100,
        position=0,
        leave=True,
    )

    poets_factory = PhilosopherFactory()
    for poet_extract in progress_bar:
        poet = poets_factory.get_philosopher(poet_extract.id)
        progress_bar.set_postfix_str(f"Poet: {poet.name}")

        poet_docs = extract(poet, poet_extract.urls)

        yield (poet, poet_docs)


def extract(poet: Philosopher, extract_urls: list[str]) -> list[Document]:
    """Extract documents for a single poet from all sources.

    Args:
        poet: Philosopher object containing poet information.
        extract_urls: List of URLs to extract content from (fa.wikipedia URLs).

    Returns:
        list[Document]: List of documents extracted for the poet.
    """

    docs = []

    docs.extend(extract_wikipedia(poet, extract_urls))
    docs.extend(extract_ganjoor(poet))

    return docs


def extract_wikipedia(
    poet: Philosopher, urls: list[str] | None = None
) -> list[Document]:
    """Extract the poet's Persian Wikipedia article.

    If a fa.wikipedia.org URL is present in `urls`, its exact page title is
    used as the query; otherwise we fall back to searching by the poet's name.

    Args:
        poet: Philosopher object containing poet information.
        urls: Optional list of URLs from the extraction metadata.

    Returns:
        list[Document]: List of documents extracted from Persian Wikipedia.
    """

    title = poet.name
    for url in urls or []:
        if "wikipedia.org/wiki/" in url:
            title = unquote(url.split("/wiki/")[-1]).replace("_", " ")
            break

    # NOTE: we call the MediaWiki API directly with a descriptive User-Agent.
    # The `wikipedia` pip package sends a generic UA that Wikimedia now blocks
    # (it returns an HTML error page, which crashes with a JSONDecodeError).
    try:
        response = requests.get(
            "https://fa.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "explaintext": 1,
                "redirects": 1,
                "format": "json",
                "titles": title,
            },
            headers={
                "User-Agent": (
                    "PersianPoetAgents/1.0 "
                    "(https://github.com/Amin-Tgz/PersianPoetAgents)"
                )
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        logger.error(f"Wikipedia fetch failed for '{title}' ({poet.id}): {e}")
        return []

    pages = (payload.get("query") or {}).get("pages") or {}

    docs = []
    for page in pages.values():
        text = (page.get("extract") or "").strip()
        if not text:
            continue
        page_title = page.get("title") or title
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": "https://fa.wikipedia.org/wiki/"
                    + page_title.replace(" ", "_"),
                    "title": page_title,
                    "philosopher_id": poet.id,
                    "philosopher_name": poet.name,
                },
            )
        )

    if not docs:
        logger.warning(f"No fa.wikipedia article found for '{title}' ({poet.id})")

    return docs


def extract_ganjoor(poet: Philosopher) -> list[Document]:
    """Load the poet's poems previously downloaded from Ganjoor (گنجور).

    Reads data/ganjoor/<poet_id>.json created by `tools.download_ganjoor`.
    Each poem becomes one Document so retrieved chunks stay verse-accurate.

    Args:
        poet: Philosopher object containing poet information.

    Returns:
        list[Document]: One document per poem, empty if no corpus exists yet.
    """

    corpus_file = settings.GANJOOR_DATA_DIR / f"{poet.id}.json"
    if not corpus_file.exists():
        logger.warning(
            f"No Ganjoor corpus at {corpus_file}. "
            f"Run `python -m tools.download_ganjoor` first; skipping poems for {poet.id}."
        )
        return []

    with open(corpus_file, "r", encoding="utf-8") as f:
        poems = json.load(f)

    documents = []
    for poem in poems:
        text = (poem.get("text") or "").strip()
        if not text:
            continue

        title = poem.get("title", "")
        page_content = f"{title}\n\n{text}" if title else text

        documents.append(
            Document(
                page_content=page_content,
                metadata={
                    "source": poem.get("url") or "https://ganjoor.net",
                    "title": title,
                    "philosopher_id": poet.id,
                    "philosopher_name": poet.name,
                },
            )
        )

    logger.info(f"Loaded {len(documents)} Ganjoor poems for {poet.id}")

    return documents
