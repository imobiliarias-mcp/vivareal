"""Parser for listing data embedded in Viva Real's Next.js payload."""

import json
from typing import Any

from bs4 import BeautifulSoup


class VivaRealPagePayloadParser:
    """Extract the property listing serialized in Next.js Flight data."""

    def parse(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Return pageData.listing from the embedded server-component stream."""
        for tag in soup.find_all("script"):
            script_content = tag.string or tag.get_text()
            flight_data = self._decode_flight_data(script_content)
            listing = self._find_listing(flight_data)
            if listing:
                return listing
        return {}

    def _decode_flight_data(self, script_content: str) -> str:
        """Decode a Next.js Flight payload string from a script tag."""
        marker = "self.__next_f.push([1,"
        marker_position = script_content.find(marker)
        if marker_position < 0:
            return ""
        payload_start = marker_position + len(marker)
        try:
            flight_data, _ = json.JSONDecoder().raw_decode(
                script_content[payload_start:]
            )
        except json.JSONDecodeError:
            return ""
        return flight_data if isinstance(flight_data, str) else ""

    def _find_listing(self, flight_data: str) -> dict[str, Any]:
        """Find the page's base listing node in the decoded Flight stream."""
        for chunk in flight_data.splitlines():
            if '"baseData"' not in chunk:
                continue
            listing = self._listing_from_chunk(chunk)
            if listing:
                return listing
        return {}

    def _listing_from_chunk(self, chunk: str) -> dict[str, Any]:
        """Decode one Flight record containing baseData.pageData.listing."""
        try:
            node = json.loads(chunk.partition(":")[2])
            listing = node[3]["baseData"]["pageData"]["listing"]
        except (IndexError, KeyError, TypeError, json.JSONDecodeError):
            return {}
        return listing if isinstance(listing, dict) else {}
