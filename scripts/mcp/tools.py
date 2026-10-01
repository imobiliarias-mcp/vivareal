"""MCP tool declarations and execution handlers for Viva Real."""

from typing import Any
from scripts.providers.vivareal import VivaRealRentalProvider
from vivareal_research.domain.criteria import (
    FilterSpecification,
    LocationSpecification,
    RentalSearchCriteria,
)
from vivareal_research.domain.values import (
    LocationCoordinate,
    LocationIdentifier,
    PageRequest,
    PriceRange,
    RoomFilter,
)


def vivareal_search_rentals(
    city: str = "Timóteo",
    bedrooms: list[int] | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    page: int = 1,
) -> dict[str, Any]:
    """MCP tool executing rental property search on Viva Real."""
    provider = VivaRealRentalProvider.create_default()
    locations = provider.suggest_locations(city, size=5)
    matched = locations.find_city_match(city) or locations.first()
    loc_id = matched.location_id if matched else LocationIdentifier("BR>Minas Gerais>NULL>Timoteo")
    coord = matched.coordinate if matched else LocationCoordinate(-19.582378, -42.644959)

    loc_spec = LocationSpecification(location_id=loc_id, city=city, coordinate=coord)
    room_filter = RoomFilter.from_iterable(bedrooms or [2, 3, 4])
    price_range = PriceRange(minimum_amount=min_price, maximum_amount=max_price)
    filter_spec = FilterSpecification(
        bedrooms=room_filter,
        price_range=price_range,
        pagination=PageRequest(page_number=page, page_size=30),
    )
    criteria = RentalSearchCriteria(location=loc_spec, filters=filter_spec)
    collection = provider.search_rentals(criteria)

    return {
        "provider": provider.provider_name(),
        "total_count": collection.total_count,
        "returned_count": len(collection),
        "listings": [
            {
                "id": item.listing_id,
                "title": item.title,
                "price": item.pricing.monthly_rent,
                "condo": item.pricing.monthly_condo,
                "total_monthly": item.pricing.total_monthly,
                "bedrooms": item.features.bedrooms,
                "bathrooms": item.features.bathrooms,
                "parking_spaces": item.features.parking_spaces,
                "usable_area_m2": item.features.usable_area,
                "neighborhood": item.address.neighborhood,
                "city": item.address.city,
                "url": item.canonical_url,
                "advertiser": item.advertiser_name,
            }
            for item in collection
        ],
    }


def vivareal_get_property_detail(property_url: str) -> dict[str, Any]:
    """MCP tool retrieving property detail and media gallery."""
    provider = VivaRealRentalProvider.create_default()
    detail = provider.get_property_detail(property_url)
    return {
        "title": detail.title(),
        "description": detail.description(),
        "rent_price": detail.summary.pricing.monthly_rent,
        "photos_count": len(detail.gallery()),
        "photos": list(detail.gallery()),
        "url": detail.summary.canonical_url,
    }


def vivareal_suggest_locations(query: str) -> list[dict[str, Any]]:
    """MCP tool discovering location identifiers from autocomplete."""
    provider = VivaRealRentalProvider.create_default()
    locations = provider.suggest_locations(query)
    return [
        {
            "label": loc.label,
            "category": loc.category.value,
            "location_id": loc.location_id.location_id,
            "city": loc.city,
            "neighborhood": loc.neighborhood,
        }
        for loc in locations
    ]
