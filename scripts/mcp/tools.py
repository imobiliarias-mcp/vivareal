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


class VivaRealMcpAdapter:
    """Adapts Viva Real provider for consumption by MCP servers and tool registries."""

    def __init__(self, provider: VivaRealRentalProvider | None = None) -> None:
        """Initialize adapter with an abstract rental provider."""
        self._provider = provider or VivaRealRentalProvider.create_default()

    @classmethod
    def create_default(cls) -> "VivaRealMcpAdapter":
        """Factory constructor instantiating the default Viva Real provider."""
        default_provider = VivaRealRentalProvider.create_default()
        return cls(provider=default_provider)

    def _resolve_location(self, city: str) -> LocationSpecification:
        """Resolve location specification from city name."""
        locations = self._provider.suggest_locations(city, size=5)
        matched = locations.find_city_match(city) or locations.first()
        loc_id = matched.location_id if matched else LocationIdentifier(f"BR>Minas Gerais>NULL>{city}")
        coord = matched.coordinate if matched else LocationCoordinate(-19.582378, -42.644959)
        return LocationSpecification(location_id=loc_id, city=city, coordinate=coord)

    def _build_filter(self, bedrooms: int, min_price: float, max_price: float, page: int) -> FilterSpecification:
        """Build filter specification from criteria."""
        rooms = [bedrooms] if bedrooms and bedrooms > 0 else []
        min_p = int(min_price) if min_price > 0 else None
        max_p = int(max_price) if max_price > 0 else None
        return FilterSpecification(
            bedrooms=RoomFilter.from_iterable(rooms),
            price_range=PriceRange(minimum_amount=min_p, maximum_amount=max_p),
            pagination=PageRequest(page_number=page, page_size=30),
        )

    def search_rentals(
        self,
        city: str = "Timóteo",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        loc_spec = self._resolve_location(city or "Timóteo")
        filter_spec = self._build_filter(bedrooms, min_price, max_price, page)
        criteria = RentalSearchCriteria(location=loc_spec, filters=filter_spec)
        collection = self._provider.search_rentals(criteria)
        return self._format_collection(collection)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format listing collection into standard dictionary."""
        return {
            "provider": self._provider.provider_name(),
            "total_count": collection.total_count,
            "returned_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        condo_val = float(item.pricing.monthly_condo) if item.pricing.monthly_condo else 0.0
        return {
            "id": item.listing_id,
            "title": item.title,
            "price": item.pricing.monthly_rent,
            "condo": item.pricing.monthly_condo,
            "condo_fee": condo_val,
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

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        url = property_code
        if not property_code.startswith("http"):
            url = f"https://www.vivareal.com.br/imovel/{property_code}/"
        detail = self._provider.get_property_detail(url)
        condo = getattr(detail.summary.pricing, "monthly_condo", None)
        condo_fee = float(condo) if condo else None
        return {
            "title": detail.title(),
            "description": detail.description(),
            "rent_price": detail.summary.pricing.monthly_rent,
            "condo_fee": condo_fee,
            "photos_count": len(detail.gallery()),
            "photos": list(detail.gallery()),
            "url": detail.summary.canonical_url,
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        locations = self._provider.suggest_locations("Timóteo", size=5)
        return {"cities": [{"name": "Timóteo"}, {"name": "Coronel Fabriciano"}, {"name": "Ipatinga"}]}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": self._provider.provider_name(),
            "coverage_region": "Nacional / Vale do Aço (Timóteo, Ipatinga, Coronel Fabriciano)",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }


def vivareal_search_rentals(
    city: str = "Timóteo",
    bedrooms: list[int] | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    page: int = 1,
) -> dict[str, Any]:
    """MCP tool executing rental property search on Viva Real (legacy function wrapper)."""
    adapter = VivaRealMcpAdapter.create_default()
    bed = bedrooms[0] if bedrooms else 0
    return adapter.search_rentals(city=city, min_price=float(min_price or 0), max_price=float(max_price or 0), bedrooms=bed, page=page)


def vivareal_get_property_detail(property_url: str) -> dict[str, Any]:
    """MCP tool retrieving property detail and media gallery (legacy function wrapper)."""
    adapter = VivaRealMcpAdapter.create_default()
    return adapter.get_property_detail(property_url)


def vivareal_suggest_locations(query: str) -> list[dict[str, Any]]:
    """MCP tool discovering location identifiers from autocomplete (legacy function wrapper)."""
    provider = VivaRealRentalProvider.create_default()
    locations = provider.suggest_locations(query)
    return [{"label": loc.label, "city": loc.city, "neighborhood": loc.neighborhood} for loc in locations]
