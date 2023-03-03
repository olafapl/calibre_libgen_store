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
        doc = """<html><body>
            <tr valign="top" bgcolor="#C6DEFF">
                <td>123456</td>
                <td>
                    <a href="search.php?req=query&amp;column[]=author">
                        Author McAuthor
                    </a>
                </td>
                <td width="500">
                    <a href="book/index.php?md5=md5" title="" id="123456">
                        Some Title
                        <font face="Times" color="green">
                            <i>[1&nbsp;ed.]</i>
                        </font><br>
                        <font face="Times" color="green"><i>ISBN1, ISBN2</i></font>
                    </a>
                </td>
                <td>Publisher</td>
                <td nowrap="">2000</td>
                <td>42</td>
                <td>English</td>
                <td nowrap="">1 Mb</td>
                <td nowrap="">epub</td>
                <td>
                    <a href="http://first.mirror/main/md5" title="this mirror">
                        [1]
                    </a>
                </td>
                <td>
                    <a href="http://second.mirror/ads.php?md5=md5" title="other.mirror">
                        [2]
                    </a>
                </td>
                <td>
                    <a
                        href="http://first.mirror/main/edit/md5"
                        title="Libgen Librarian">
                        [edit]
                    </a>
                </td>
            </tr>
            </body></html>"""
        soup = BeautifulSoup(doc, "html.parser")
        row = soup.select_one("tr")

        result = libgen.parse_result_row(row, base_url="http://base.url")

        assert result.authors == "Author McAuthor"
        assert result.title == "Some Title"
        assert result.publisher == "Publisher"
        assert result.year == "2000"
        assert result.pages == "42"
        assert result.language == "English"
        assert result.size == "1 MB"
        assert result.extension == "epub"
        assert result.mirrors == {
            "http://first.mirror/main/md5",
            "http://second.mirror/ads.php?md5=md5",
        }

    @responses.activate
    def test_get_extra(self):
        with open(DATA_DIR / "details-page.html") as f:
            responses.get("http://details.page", body=f.read())

        with open(DATA_DIR / "download-page.html") as f:
            responses.get("http://first.mirror/main/md5", body=f.read())

        extra = libgen.get_extra("http://details.page")

        assert extra.cover_url == "http://details.page/covers/cover.jpg"
        assert extra.download_url == "http://10.0.0.1/main/728000/md5/Some%20Title.epub"
