"""Collaborator bundles for Viva Real rental client adhering to Object Calisthenics."""

from vivareal_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpxHttpClient,
)
from vivareal_research.infrastructure.url_builder import VivaRealUrlBuilder
from vivareal_research.parsers.detail_parser import VivaRealDetailParser
from vivareal_research.parsers.location_parser import VivaRealLocationParser
from vivareal_research.parsers.search_parser import VivaRealSearchParser


class VivaRealGateway:
    """Network gateway bundling HTTP client and URL builder."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        url_builder: VivaRealUrlBuilder | None = None,
    ) -> None:
        """Initialize gateway with transport and builder."""
        self._http = http_client or HttpxHttpClient()
        self._builder = url_builder or VivaRealUrlBuilder()

    def http(self) -> HttpClientProtocol:
        """Return HTTP transport."""
        return self._http

    def builder(self) -> VivaRealUrlBuilder:
        """Return URL builder."""
        return self._builder


class VivaRealParserSuite:
    """Parser suite bundling search, detail, and location parsers."""

    def __init__(
        self,
        search_parser: VivaRealSearchParser | None = None,
        detail_parser: VivaRealDetailParser | None = None,
        public_base_url: str | None = None,
    ) -> None:
        """Initialize suite with parsers and the configured public website base."""
        self._search = search_parser or VivaRealSearchParser(public_base_url)
        self._detail = detail_parser or VivaRealDetailParser()
        self._location = VivaRealLocationParser()

    def search(self) -> VivaRealSearchParser:
        """Return search parser."""
        return self._search

    def detail(self) -> VivaRealDetailParser:
        """Return detail parser."""
        return self._detail

    def location(self) -> VivaRealLocationParser:
        """Return location parser."""
        return self._location
