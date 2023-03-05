import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from typing import List, Set
from .util import extract_base_url
from .log import logger


MIRRORS = ["https://libgen.rs", "https://libgen.is", "https://libgen.st"]


@dataclass
class LibGenBook:
    authors: str
    title: str
    details_url: str
    publisher: str
    year: str
    pages: str
    language: str
    size: str
    extension: str
    mirrors: Set[str]


@dataclass
class LibGenBookExtra:
    cover_url: str
    download_url: str


def get_soup(url: str, **kwargs) -> BeautifulSoup:
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def search(query: str, max_results=50, timeout: int = None) -> List[LibGenBook]:
    """Search Library Genesis for books.

    Args:
        query (str): Search query.
        max_results (int, optional): Max number of results. Defaults to 50.
        timeout (int, optional): Timeout in seconds. Defaults to None.

    Returns:
        List[LibGenBook]: Search results.
    """
    for mirror in MIRRORS:
        logger.info("Searching mirror %s.", mirror)
        try:
            response = get_soup(
                f"{mirror}/search.php",
                params={
                    "req": query,
                    "res": next((r for r in (25, 50, 100) if r >= max_results), 100),
                    "view": "simple",
                },
                timeout=timeout,
            )
            return [
                parse_result_row(row, base_url=mirror)
                for row in response.select("table.c tr:not(:first-child)")[:max_results]
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


def parse_result_row(result: Tag, base_url: str) -> LibGenBook:
    cols = result.select("td")
    return LibGenBook(
        authors=cols[1].text.strip(),
        title=cols[2].select_one("a").text.strip().split("\n")[0],
        details_url=f"{base_url}/{cols[2].select_one('a').attrs['href']}",
        publisher=cols[3].text.strip(),
        year=cols[4].text.strip(),
        pages=cols[5].text.strip(),
        language=cols[6].text.strip(),
        size=cols[7].text.strip().upper(),
        extension=cols[8].text.strip(),
        mirrors={c.select_one("a").attrs["href"] for c in (cols[9], cols[10])},
    )


def get_extra(details_url: str, timeout: int = None) -> LibGenBookExtra:
    """Get additional details that are not available in Library Genesis' search
    results.

    Args:
        details_url (str): Search result details URL.
        timeout (int, optional): Timeout in seconds. Defaults to None.

    Returns:
        bool: True if success; else False.
    """

    logger.info("Getting details from %s.", details_url)
    try:
        response = get_soup(details_url)

        base_url = extract_base_url(details_url)
        cover_path = response.select_one("table img").attrs["src"]
        cover_url = f"{base_url}{cover_path}"

        download_page_url = response.select_one("a[title='this mirror']").attrs["href"]
        download_page_response = get_soup(download_page_url)
        download_url = download_page_response.select_one("a", string="GET").attrs[
            "href"
        ]

        return LibGenBookExtra(cover_url=cover_url, download_url=download_url)
    except Exception:
        logger.exception("Failed to get extra from %s.", details_url)
        raise
