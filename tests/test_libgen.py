import responses
from responses import matchers
from unittest import TestCase
from unittest.mock import patch
from bs4 import BeautifulSoup
from pathlib import Path
import logging
import calibre_libgen_store.libgen as libgen

logging.disable(logging.CRITICAL)

DATA_DIR = Path(__file__).parent / Path(__file__).stem


class TestLibGen(TestCase):
    MIRRORS = ["http://first.mirror", "http://second.mirror"]

    @patch("calibre_libgen_store.libgen.MIRRORS", MIRRORS)
    @responses.activate
    def test_search_working_first_mirror(self):
        @patch("calibre_libgen_store.libgen.parse_result_row")
        def parse_result_row(result, base_url):
            return libgen.LibGenBook(
                authors="authors",
                title="title",
                publisher="publisher",
                year="2000",
                pages="100",
                language="language",
                size="1 MB",
                extension="PDF",
                mirrors=["https://mirror.mirror"],
            )

        params = {"req": "query", "res": 50, "view": "simple"}
        first_mirror_response = responses.get(
            f"{TestLibGen.MIRRORS[0]}/search.php",
            body="<html></html>",
            match=[matchers.query_param_matcher(params)],
        )
        second_mirror_response = responses.get(
            f"{TestLibGen.MIRRORS[1]}/search.php",
            body="<html></html>",
            match=[matchers.query_param_matcher(params)],
        )

        libgen.search("query", max_results=42)

        assert first_mirror_response.call_count == 1
        assert second_mirror_response.call_count == 0

    @patch("calibre_libgen_store.libgen.MIRRORS", MIRRORS)
    @responses.activate
    def test_search_broken_first_mirror(self):
        @patch("calibre_libgen_store.libgen.parse_result_row")
        def parse_result_row(result, base_url):
            return libgen.LibGenBook(
                authors="authors",
                title="title",
                publisher="publisher",
                year="2000",
                pages="100",
                language="language",
                size="1 MB",
                extension="PDF",
                mirrors=["https://mirror.mirror"],
            )

        params = {"req": "query", "res": 50, "view": "simple"}
        first_mirror_response = responses.add(
            responses.GET,
            f"{TestLibGen.MIRRORS[0]}/search.php",
            match=[matchers.query_param_matcher(params)],
            status=500,
        )
        second_mirror_response = responses.get(
            f"{TestLibGen.MIRRORS[1]}/search.php",
            body="<html></html>",
            match=[matchers.query_param_matcher(params)],
        )

        libgen.search("query", max_results=42)

        assert first_mirror_response.call_count == 1
        assert second_mirror_response.call_count == 1

    def test_parse_result_row(self):
        with open(DATA_DIR / "search-result-row.html") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        row = soup.select_one("tr")

        result = libgen.parse_result_row(row, base_url="https://libgen.is")

        assert result.authors == "Author McAuthor"
        assert result.title == "Some Title"
        assert result.details_url == "https://libgen.is/book/index.php?md5=md5"
        assert result.publisher == "Publisher"
        assert result.year == "2000"
        assert result.pages == "42"
        assert result.language == "English"
        assert result.size == "1 MB"
        assert result.extension == "epub"
        assert result.mirrors == {
            "http://library.lol/main/md5",
            "http://libgen.lc/ads.php?md5=md5",
        }

    @responses.activate
    def test_get_extra(self):
        with open(DATA_DIR / "details-page.html") as f:
            responses.get("https://libgen.is/book/index.php?md5=md5", body=f.read())

        with open(DATA_DIR / "download-page.html") as f:
            responses.get("http://library.lol/main/md5", body=f.read())

        extra = libgen.get_extra("https://libgen.is/book/index.php?md5=md5")

        assert extra.cover_url == "https://libgen.is/covers/534000/md5-d.jpg"
        assert (
            extra.download_url == "http://10.0.0.1/main/534000/md5/Some%20Title%.epub"
        )
