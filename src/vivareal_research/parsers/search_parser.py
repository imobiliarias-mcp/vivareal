"""Parsers converting Glue API JSON responses into domain collections."""

from typing import Any
from vivareal_research.domain.listing import (
    ListingAddress,
    ListingCollection,
    ListingFeatures,
    ListingPricing,
    ListingSummary,
)


class VivaRealSearchParser:
    """Parses Glue API /v2/listings search responses into domain models."""

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
        return ListingSummary(
            listing_id=str(listing.get("id", "")),
            external_id=str(listing.get("externalId", "")),
            title=self._extract_title(listing, link),
            address=self._extract_address(listing.get("address", {})),
            pricing=self._extract_pricing(listing.get("pricingInfos", [])),
            features=self._extract_features(listing),
            photos_count=len(medias),
            canonical_url=str(link.get("href", "")),
            advertiser_name=str(account.get("name", "")),
        )

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
