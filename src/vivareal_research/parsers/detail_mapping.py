"""Map exposed Viva Real listing data into property detail entities."""

from typing import Any

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


def build_property_detail(
    listing_id: str,
    title: str,
    description: str,
    price: int,
    images: list[str],
    canonical_url: str,
    page_listing: dict[str, Any],
) -> PropertyDetail:
    """Build detail entities from parsed page fields.

    Args:
        listing_id: Product JSON-LD or page listing identifier.
        title: Property title from the available page source.
        description: Product JSON-LD description.
        price: Product JSON-LD offer price used as a rent fallback.
        images: Product JSON-LD image URLs.
        canonical_url: Canonical URL from the page or caller fallback.
        page_listing: Listing object decoded from the page payload.

    Returns:
        A property detail with summary and descriptive content.
    """
    summary = _build_summary(
        listing_id, title, price, images, canonical_url, page_listing
    )
    content = _build_content(description, images, canonical_url, page_listing)
    return PropertyDetail(summary=summary, content=content)


def _build_summary(
    listing_id: str,
    title: str,
    price: int,
    images: list[str],
    canonical_url: str,
    page_listing: dict[str, Any],
) -> ListingSummary:
    advertiser = _mapping(page_listing.get("advertiser"))
    return ListingSummary(
        listing_id=listing_id,
        external_id=str(page_listing.get("externalId") or ""),
        title=title,
        address=_extract_address(page_listing.get("address")),
        pricing=_extract_pricing(page_listing.get("prices"), price),
        features=_extract_features(page_listing.get("amenities")),
        photos_count=len(images),
        canonical_url=canonical_url,
        advertiser_name=str(advertiser.get("name") or ""),
    )


def _build_content(
    description: str,
    images: list[str],
    canonical_url: str,
    page_listing: dict[str, Any],
) -> PropertyDetailContent:
    return PropertyDetailContent(
        description=description,
        amenities=PropertyAmenities(
            _amenity_values(page_listing.get("amenities"))
        ),
        gallery=PhotoGallery.from_iterable(images),
        contact=_extract_contact(page_listing.get("advertiser"), canonical_url),
    )


def _extract_address(raw_address: Any) -> ListingAddress:
    address = _mapping(raw_address)
    coordinates = _mapping(address.get("coordinates"))
    latitude = _optional_float(coordinates.get("latitude"))
    longitude = _optional_float(coordinates.get("longitude"))
    return ListingAddress(
        neighborhood=str(address.get("neighborhood") or ""),
        city=str(address.get("city") or ""),
        state_acronym=str(address.get("stateAcronym") or ""),
        street=str(address.get("street") or ""),
        street_number=str(address.get("streetNumber") or ""),
        latitude=latitude,
        longitude=longitude,
    )


def _extract_pricing(raw_prices: Any, fallback_price: int) -> ListingPricing:
    prices = _mapping(raw_prices)
    rental = _mapping(prices.get("rental"))
    rent = _optional_int(rental.get("value"))
    if rent is None:
        rent = fallback_price
    condo = _optional_int(rental.get("condominium"))
    iptu = _optional_int(rental.get("iptu"))
    total = _monthly_total(rental.get("monthlyRentalTotalPrice"), rent, condo)
    return ListingPricing(
        monthly_rent=rent,
        monthly_condo=condo,
        yearly_iptu=iptu,
        total_monthly=total,
    )


def _monthly_total(raw_total: Any, rent: int, condo: int | None) -> int | None:
    total = _optional_int(raw_total)
    if total is not None:
        return total
    if condo is None:
        return None
    return rent + condo


def _extract_features(raw_amenities: Any) -> ListingFeatures:
    amenities = _mapping(raw_amenities)
    return ListingFeatures(
        usable_area=_first_integer(amenities.get("usableAreas")),
        bedrooms=_first_integer(amenities.get("bedrooms")),
        bathrooms=_first_integer(amenities.get("bathrooms")),
        suites=_first_integer(amenities.get("suites")),
        parking_spaces=_first_integer(amenities.get("parkingSpaces")),
    )


def _extract_contact(raw_advertiser: Any, canonical_url: str) -> AdvertiserContact:
    advertiser = _mapping(raw_advertiser)
    phone = _first_phone(advertiser.get("phoneNumbers"))
    return AdvertiserContact(
        name=str(advertiser.get("name") or ""),
        phone=phone,
        whatsapp=str(advertiser.get("whatsAppNumber") or ""),
        profile_url=canonical_url,
    )


def _first_phone(phone_numbers: Any) -> str:
    if not isinstance(phone_numbers, list):
        return ""
    if not phone_numbers:
        return ""
    return str(phone_numbers[0])


def _amenity_values(raw_amenities: Any) -> tuple[str, ...]:
    values = _mapping(raw_amenities).get("values", [])
    if not isinstance(values, list):
        return ()
    return tuple(value for value in values if isinstance(value, str))


def _first_integer(values: Any) -> int | None:
    if not isinstance(values, list) or not values:
        return None
    return _optional_int(values[0])


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
