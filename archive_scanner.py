from __future__ import annotations

"""Fetch Grateful Dead show information from the Internet Archive API.

This module implements a small client for the Internet Archive's Advanced
Search API.  It queries for items in the ``GratefulDead`` collection within a
specified year range and returns the show titles and identifiers.  The
functions are written so they can be easily tested by injecting a custom
``request_get`` callable, avoiding a hard dependency on external libraries.
"""

from dataclasses import dataclass
from typing import Callable, List
import json
import urllib.parse
import urllib.request

SEARCH_URL = "https://archive.org/advancedsearch.php"


@dataclass
class ArchiveShow:
    """A single show entry returned by the Internet Archive."""

    title: str
    identifier: str


def _default_get(url: str, params: dict, timeout: float):
    query = urllib.parse.urlencode(params, doseq=True)
    full_url = f"{url}?{query}"
    with urllib.request.urlopen(full_url, timeout=timeout) as resp:
        text = resp.read().decode("utf-8")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return json.loads(text)

    return Response()


def fetch_archive_shows(
    start_year: int,
    end_year: int,
    *,
    request_get: Callable[..., object] = _default_get,
) -> List[ArchiveShow]:
    """Return shows from the Internet Archive within ``start_year`` and ``end_year``.

    Parameters
    ----------
    start_year:
        Starting year of the search range (inclusive).
    end_year:
        Ending year of the search range (inclusive).
    request_get:
        Callable compatible with :func:`requests.get`.  This parameter exists so
        tests can supply a mock implementation without performing network
        requests.
    """

    query = f"collection:GratefulDead AND year:[{start_year} TO {end_year}]"
    params = {
        "q": query,
        "fl[]": ["identifier", "title"],
        "rows": 10000,
        "page": 1,
        "output": "json",
    }
    response = request_get(SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    docs = data.get("response", {}).get("docs", [])
    return [ArchiveShow(title=d["title"], identifier=d["identifier"]) for d in docs]
