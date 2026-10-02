"""Parsers converting Glue API JSON responses into domain collections."""

from typing import Any
from urllib.parse import urljoin, urlsplit

from vivareal_research.domain.listing import (
    ListingAddress,
    ListingCollection,
    ListingFeatures,
    ListingPricing,
    ListingSummary,
)
from vivareal_research.infrastructure.url_builder import VivaRealUrlBuilder


class VivaRealSearchParser:
    """Parses Glue API /v2/listings search responses into domain models."""

    def __init__(self, public_base_url: str | None = None) -> None:
        """Initialize with the public website base, separate from the Glue API."""
        builder = VivaRealUrlBuilder()
        active_base_url = public_base_url or builder.public_base_url()
        parsed_base = urlsplit(active_base_url.strip())
        if parsed_base.scheme not in {"http", "https"} or not parsed_base.hostname:
            raise ValueError(f"Invalid VivaReal public base URL: {active_base_url}")
        self._public_base_url = f"{parsed_base.scheme}://{parsed_base.netloc}".rstrip("/")
        self._public_host = self._normalize_host(parsed_base.hostname)

    def parse(self, payload: dict[str, Any]) -> ListingCollection:
        """Parse raw API dictionary into strongly typed ListingCollection."""
        search_data = payload.get("search", {})
        total_count = search_data.get("totalCount", 0)
        raw_listings = search_data.get("result", {}).get("listings", [])
        parsed_items = [self._parse_single_item(item) for item in raw_listings]
        return ListingCollection(listings=tuple(parsed_items), total_count=total_count)

    def _parse_single_item(self, item: dict[str, Any]) -> ListingSummary:
        """Parse single listing card item from result array."""
        listing = item.get("listing", {})
        link = item.get("link", {})
        account = item.get("account", {})
        medias = item.get("medias", [])
        listing_id = str(listing.get("id", ""))
        public_url = self._resolve_public_url(str(link.get("href", "")), listing_id)
        return ListingSummary(
            listing_id=listing_id,
            external_id=str(listing.get("externalId", "")),
            title=self._extract_title(listing, link),
            address=self._extract_address(listing.get("address", {})),
            pricing=self._extract_pricing(listing.get("pricingInfos", [])),
            features=self._extract_features(listing),
            photos_count=len(medias),
            canonical_url=public_url,
            advertiser_name=str(account.get("name", "")),
        )

    def _resolve_public_url(self, href: str, listing_id: str) -> str:
        """Resolve and validate a public property page URL with listing context."""
        if not href.strip():
            raise ValueError(f"VivaReal listing {listing_id} has no public property URL")
        resolved_url = urljoin(f"{self._public_base_url}/", href.strip())
        try:
            parsed_url = urlsplit(resolved_url)
        except ValueError as error:
            raise ValueError(f"Invalid public URL for VivaReal listing {listing_id}: {href}") from error
        same_host = self._normalize_host(parsed_url.hostname) == self._public_host
        has_credentials = parsed_url.username is not None or parsed_url.password is not None
        valid_scheme = parsed_url.scheme in {"http", "https"}
        valid_property_path = self._is_public_property_path(parsed_url.path)
        if (
            not valid_scheme
            or not parsed_url.hostname
            or not same_host
            or has_credentials
            or not valid_property_path
        ):
            raise ValueError(f"Invalid public URL for VivaReal listing {listing_id}: {href}")
        return resolved_url

    def _is_public_property_path(self, path: str) -> bool:
        """Accept property detail routes, not same-host search or media URLs."""
        normalized_path = path.lower()
        property_slug = normalized_path.removeprefix("/imovel/").strip("/")
        image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif")
        is_property_route = normalized_path.startswith("/imovel/") and bool(property_slug)
        is_image = normalized_path.endswith(image_extensions)
        return is_property_route and not is_image

    def _normalize_host(self, hostname: str | None) -> str:
        """Treat www and apex hosts as the same configured public domain."""
        return (hostname or "").removeprefix("www.").lower()

    def _extract_title(self, listing: dict[str, Any], link: dict[str, Any]) -> str:
        """Extract or generate descriptive title for listing."""
        link_name = link.get("name", "")
        if link_name:
            return link_name.strip()
        title = listing.get("title", "")
        if title:
            return title.strip()
        unit_types = listing.get("unitTypes", ["Imóvel"])
        return f"{unit_types[0]} para Alugar"

    def _extract_address(self, addr: dict[str, Any]) -> ListingAddress:
        """Extract address structure with coordinates."""
        point = addr.get("point", {})
        lat = point.get("lat")
        lon = point.get("lon")
        return ListingAddress(
            neighborhood=addr.get("neighborhood", ""),
            city=addr.get("city", ""),
            state_acronym=addr.get("stateAcronym", ""),
            street=addr.get("street", ""),
            street_number=addr.get("streetNumber", ""),
            zip_code=addr.get("zipCode", ""),
            latitude=float(lat) if lat is not None else None,
            longitude=float(lon) if lon is not None else None,
        )

    def _extract_pricing(self, pricing_infos: list[dict[str, Any]]) -> ListingPricing:
        """Extract rental pricing details."""
        if not pricing_infos:
            return ListingPricing(monthly_rent=0)
        rental_info = self._find_rental_pricing(pricing_infos)
        rent = int(rental_info.get("price", 0))
        condo = int(rental_info.get("monthlyCondoFee", 0))
        iptu = int(rental_info.get("yearlyIptu", 0))
        nested_rental = rental_info.get("rentalInfo", {})
        total = int(nested_rental.get("monthlyRentalTotalPrice", 0))
        return ListingPricing(
            monthly_rent=rent,
            monthly_condo=condo,
            yearly_iptu=iptu,
            total_monthly=total or (rent + condo),
        )

    def _find_rental_pricing(self, pricing_infos: list[dict[str, Any]]) -> dict[str, Any]:
        """Find the pricing dictionary corresponding to RENTAL."""
        for info in pricing_infos:
            if info.get("businessType") == "RENTAL":
                return info
        return pricing_infos[0]

    def _extract_features(self, listing: dict[str, Any]) -> ListingFeatures:
        """Extract numerical physical room and area features."""
        areas = listing.get("usableAreas", [0])
        bedrooms = listing.get("bedrooms", [0])
        bathrooms = listing.get("bathrooms", [0])
        suites = listing.get("suites", [0])
        parking = listing.get("parkingSpaces", [0])
        return ListingFeatures(
            usable_area=int(areas[0]) if areas else 0,
            bedrooms=int(bedrooms[0]) if bedrooms else 0,
            bathrooms=int(bathrooms[0]) if bathrooms else 0,
            suites=int(suites[0]) if suites else 0,
            parking_spaces=int(parking[0]) if parking else 0,
        )
