"""Parser for property detail page HTML and microdata."""

import json
from typing import Any
from bs4 import BeautifulSoup
from vivareal_research.domain.listing import (
    ListingAddress,
    ListingFeatures,
    ListingPricing,
    ListingSummary,
)
from vivareal_research.domain.property import (
    AdvertiserContact,
    PhotoGallery,
    PropertyAmenities,
    PropertyDetail,
    PropertyDetailContent,
)


class VivaRealDetailParser:
    """Parses property detail HTML and JSON-LD structured data."""

    def parse_html(self, html_content: str, fallback_url: str = "") -> PropertyDetail:
        """Parse HTML string into PropertyDetail entity."""
        soup = BeautifulSoup(html_content, "html.parser")
        product_ld = self._extract_product_json_ld(soup)
        title = self._extract_title(soup, product_ld)
        description = product_ld.get("description", "")
        images = product_ld.get("image", [])
        offers = product_ld.get("offers", {})
        price = int(offers.get("price", 0))
        sku = str(product_ld.get("sku", ""))
        canonical_url = offers.get("url", fallback_url)
        return self._build_property_detail(sku, title, description, price, images, canonical_url)

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

    def _build_property_detail(
        self,
        listing_id: str,
        title: str,
        description: str,
        price: int,
        images: list[str],
        canonical_url: str,
    ) -> PropertyDetail:
        """Construct PropertyDetail from parsed components."""
        summary = ListingSummary(
            listing_id=listing_id,
            external_id="",
            title=title,
            address=ListingAddress(neighborhood="", city="Timóteo", state_acronym="MG"),
            pricing=ListingPricing(monthly_rent=price, total_monthly=price),
            features=ListingFeatures(usable_area=0, bedrooms=0, bathrooms=0),
            photos_count=len(images),
            canonical_url=canonical_url,
            advertiser_name="",
        )
        content = PropertyDetailContent(
            description=description,
            amenities=PropertyAmenities(()),
            gallery=PhotoGallery.from_iterable(images),
            contact=AdvertiserContact(name="", profile_url=canonical_url),
        )
        return PropertyDetail(summary=summary, content=content)
