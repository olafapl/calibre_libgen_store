from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog
from calibre.customize import StoreBase
from typing import Generator
from . import libgen
from .util import extract_base_url
from .log import logger
from .__version__ import __version__


PLUGIN_AUTHOR = "Olaf Apelseth Liadal"
PLUGIN_NAME = "Library Genesis"
PLUGIN_DESCRIPTION = "Libary Genesis."
PLUGIN_VERSION = tuple(__version__.split("."))


class LibGenStorePlugin(StorePlugin):
    def open(self, parent=None, detail_item: str = None, external=False) -> None:
        if external:
            open_url(detail_item if detail_item else libgen.MIRRORS[0])
        else:
            base_url = (
                extract_base_url(detail_item) if detail_item else libgen.MIRRORS[0]
            )
            dialog = WebStoreDialog(
                self.gui, base_url=base_url, parent=parent, detail_url=detail_item
            )
            dialog.setWindowTitle(self.name)
            dialog.exec()

    def search(
        self, query: str, max_results=10, timeout=60
    ) -> Generator[SearchResult, None, None]:
        logger.info("Searching for %s.", query)
        search_results = libgen.search(query, max_results=max_results)

        for search_result in search_results:
            result = SearchResult()
            result.affiliate = False
            result.author = search_result.authors
            result.detail_item = search_result.details_url
            result.drm = SearchResult.DRM_UNLOCKED
            result.formats = search_result.extension
            result.plugin_author = PLUGIN_AUTHOR
            result.price = "0"
            result.store_name = PLUGIN_NAME
            result.title = search_result.title
            yield result

    def get_details(self, search_result: SearchResult, timeout=60) -> bool:
        try:
            extra = libgen.get_extra(search_result.detail_item)
            search_result.downloads[search_result.formats] = extra.download_url
            search_result.cover_url = extra.cover_url
            return True
        except Exception:
            return False


class LibGenStore(StoreBase):
    name = PLUGIN_NAME
    description = PLUGIN_DESCRIPTION
    author = PLUGIN_AUTHOR
    version = PLUGIN_VERSION
    minimum_calibre_version = (5, 0, 1)
    affiliate = False
    drm_free_only = True

    def load_actual_plugin(self, gui) -> LibGenStorePlugin:
        self.actual_plugin_object = LibGenStorePlugin(gui, self.name)
        return self.actual_plugin_object
