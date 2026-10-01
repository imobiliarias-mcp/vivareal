"""Parser for Glue API /v4/locations suggestions."""

from typing import Any
from vivareal_research.domain.enums import LocationCategory
from vivareal_research.domain.location import LocationCollection, LocationSuggestion
from vivareal_research.domain.values import LocationCoordinate, LocationIdentifier


class VivaRealLocationParser:
    """Parses Glue API /v4/locations responses into LocationCollection."""

    def parse(self, payload: dict[str, Any]) -> LocationCollection:
        """Parse raw dictionary into strongly typed LocationCollection."""
        results = payload.get("result", [])
        suggestions = [self._parse_single(item) for item in results]
        valid_items = [s for s in suggestions if s is not None]
        return LocationCollection(items=tuple(valid_items))

    def _parse_single(self, item: dict[str, Any]) -> LocationSuggestion | None:
        """Parse single location suggestion dictionary."""
        category_str = item.get("category", "")
        category = self._match_category(category_str)
        address = item.get("address", {})
        location_id_str = address.get("locationId", "")
        if not location_id_str:
            return None
        city = address.get("city", "")
        state = address.get("state", "")
        neighborhood = address.get("neighborhood", "")
        label = self._build_label(category, city, neighborhood)
        point = address.get("point")
        coord = self._extract_coordinate(point)
        return LocationSuggestion(
            label=label,
            category=category,
            location_id=LocationIdentifier(location_id_str),
            city=city,
            state=state,
            neighborhood=neighborhood,
            coordinate=coord,
        )

    def _match_category(self, cat: str) -> LocationCategory:
        """Map raw category string to LocationCategory enum."""
        mapping = {
            "city": LocationCategory.CITY,
            "neighborhood": LocationCategory.NEIGHBORHOOD,
            "street": LocationCategory.STREET,
            "zone": LocationCategory.ZONE,
        }
        return mapping.get(cat, LocationCategory.CITY)

    def _build_label(self, category: LocationCategory, city: str, neighborhood: str) -> str:
        """Construct readable label for location item."""
        if category == LocationCategory.NEIGHBORHOOD and neighborhood:
            return f"{neighborhood}, {city}"
        return city

    def _extract_coordinate(self, point: dict[str, Any] | None) -> LocationCoordinate | None:
        """Extract coordinate if present in point dictionary."""
        if not point:
            return None
        lat = point.get("lat")
        lon = point.get("lon")
        if lat is None or lon is None:
            return None
        return LocationCoordinate(latitude=float(lat), longitude=float(lon))
