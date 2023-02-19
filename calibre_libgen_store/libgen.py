from requests_html import HTMLSession, Element
from requests.exceptions import HTTPError
from dataclasses import dataclass
from typing import List
from calibre_libgen_store.log import logger


MIRRORS = ["https://libgen.rs", "https://libgen.is", "https://libgen.st"]


@dataclass
class SearchResult:
    authors: str
    title: str
    publisher: str
    year: str
    pages: str
    language: str
    size: str
    extension: str
    mirrors: List[str]


def search(query: str, results=50) -> List[SearchResult]:
    session = HTMLSession()
    for mirror in MIRRORS:
        logger.info("Searching mirror %s.", mirror)
        try:
            response = session.get(
                f"{mirror}/search.php",
                params={"req": query, "res": results, "view": "simple"},
            )
            response.raise_for_status()
            return [
                parse_result_row(row)
                for row in response.html.find("table.c tr:not(:first-child)")
            ]
        except HTTPError:
            logger.exception(
                "Search failed for mirror %s.",
                mirror,
            )
        except Exception:
            logger.exception("Search failed for mirror %s.", mirror)
            break
    return []


def parse_result_row(result: Element) -> SearchResult:
    cols = result.find("td")
    return SearchResult(
        authors=cols[1].text,
        title=cols[2].find("a", first=True).text.split("\n")[0],
        publisher=cols[3].text,
        year=cols[4].text,
        pages=cols[5].text,
        language=cols[6].text,
        size=cols[7].text.upper(),
        extension=cols[8].text,
        mirrors=[c.find("a", first=True).attrs["href"] for c in (cols[9], cols[10])],
    )
