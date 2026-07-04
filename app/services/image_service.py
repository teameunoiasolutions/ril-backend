"""
Looks up a real, working image URL for a place name or search query using
the Wikimedia Commons search API. No API key required.

Two things added compared to the first version, both aimed at the
"No image available" issue showing up for places that should have photos:

1. A descriptive User-Agent header. Wikimedia's API etiquette
   (https://meta.wikimedia.org/wiki/User-Agent_policy) asks for one, and
   requests without it can get silently throttled rather than erroring
   clearly - which would look exactly like "nothing found" from here.

2. A fallback to a simpler query. Gemini's `image_query` values tend to be
   descriptive ("Tangalle golden hour aerial coastline"), but Commons search
   is fairly literal - a long phrase can return zero hits for a place that
   has photos under a plainer search like just "Tangalle Sri Lanka".

Also logs what actually happened (HTTP error vs genuinely zero results) so
failures are visible in your server console instead of silently becoming
None with no trace.

Requires: pip install httpx
"""

import logging

import httpx

logger = logging.getLogger(__name__)

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    # Replace the contact info with something real before deploying -
    # Wikimedia's etiquette asks for a way to reach you if this app causes
    # unusual traffic.
    "User-Agent": "RoyaleIslesLankaConcierge/1.0 (contact: you@example.com)"
}


async def _search_commons(client: httpx.AsyncClient, query: str) -> str | None:
    search_resp = await client.get(
        COMMONS_API_URL,
        params={
            "action": "query",
            "list": "search",
            "srsearch": f"{query} filetype:bitmap",
            "srnamespace": 6,  # the File: namespace
            "srlimit": 1,
            "format": "json",
        },
        headers=HEADERS,
    )
    search_resp.raise_for_status()
    results = search_resp.json().get("query", {}).get("search", [])

    if not results:
        logger.info("Commons search returned no results for query: %r", query)
        return None

    file_title = results[0]["title"]  # e.g. "File:Some_Beach.jpg"

    info_resp = await client.get(
        COMMONS_API_URL,
        params={
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
        headers=HEADERS,
    )
    info_resp.raise_for_status()
    pages = info_resp.json().get("query", {}).get("pages", {})

    for page in pages.values():
        imageinfo = page.get("imageinfo")
        if imageinfo:
            return imageinfo[0]["url"]

    logger.info("Commons found %r but it had no imageinfo", file_title)
    return None


async def fetch_image_url(query: str, fallback_query: str | None = None) -> str | None:
    if not query and not fallback_query:
        return None

    async with httpx.AsyncClient(timeout=5.0) as client:
        for attempt_query in filter(None, [query, fallback_query]):
            try:
                url = await _search_commons(client, attempt_query)
                if url:
                    return url
            except httpx.HTTPError as exc:
                logger.warning(
                    "Commons request failed for query %r: %s", attempt_query, exc
                )

    return None