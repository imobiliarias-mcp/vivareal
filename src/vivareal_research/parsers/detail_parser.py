"""Parser for property detail page HTML and microdata."""

import json
from typing import Any

from bs4 import BeautifulSoup

from vivareal_research.domain.property import PropertyDetail
from vivareal_research.parsers.detail_mapping import build_property_detail
from vivareal_research.parsers.page_payload_parser import VivaRealPagePayloadParser


class VivaRealDetailParser:
    """Parses property detail HTML and JSON-LD structured data."""

    def parse_html(self, html_content: str, fallback_url: str = "") -> PropertyDetail:
        """Parse property HTML into a detail entity.

        Args:
            html_content: Full page HTML returned by Viva Real.
            fallback_url: URL used when neither page source provides one.

        Returns:
            Parsed summary and descriptive content for the property.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        product_ld = self._extract_product_json_ld(soup)
        page_data_parser = VivaRealPagePayloadParser()
        page_listing = page_data_parser.parse(soup)
        title = self._extract_title(soup, product_ld)
        description = product_ld.get("description", "")
        images = product_ld.get("image", [])
        offers = product_ld.get("offers", {})
        price = int(offers.get("price", 0))
        sku = str(product_ld.get("sku") or page_listing.get("id", ""))
        canonical_url = offers.get("url") or page_listing.get("href") or fallback_url
        return build_property_detail(
            sku, title, description, price, images, canonical_url, page_listing
        )

    def _extract_product_json_ld(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract Schema.org Product dictionary from script tags."""
        script_tags = soup.find_all("script", type="application/ld+json")
        for tag in script_tags:
            content = tag.string or ""
            if '"@type": "Product"' in content or '"@type":"Product"' in content:
                return json.loads(content)
        return {}

    def _extract_title(self, soup: BeautifulSoup, product_ld: dict[str, Any]) -> str:
        """Extract headline title from markup or JSON-LD."""
        ld_name = product_ld.get("name", "")
        if ld_name:
            return str(ld_name).strip()
        h1 = soup.find("h1")
        if h1 and h1.text:
            return h1.text.strip()
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return "Imóvel para Alugar"
