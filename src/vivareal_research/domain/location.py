"""Location domain models and suggestion collections."""

from dataclasses import dataclass
from typing import Iterator
from vivareal_research.domain.enums import LocationCategory
from vivareal_research.domain.values import LocationCoordinate, LocationIdentifier


@dataclass(frozen=True)
class LocationSuggestion:
    """Discovered geographical location item from autocomplete."""

    label: str
    category: LocationCategory
    location_id: LocationIdentifier
    city: str
    state: str
    neighborhood: str = ""
    coordinate: LocationCoordinate | None = None

    def display_full(self) -> str:
        """Format full readable location string."""
        if self.neighborhood:
            return f"{self.neighborhood}, {self.city} - {self.state}"
        return f"{self.city} - {self.state}"


@dataclass(frozen=True)
class LocationCollection:
    """First-class collection of location suggestions."""

    items: tuple[LocationSuggestion, ...]

    def __len__(self) -> int:
        """Return suggestion count."""
        return len(self.items)

    def __iter__(self) -> Iterator[LocationSuggestion]:
        """Iterate over location suggestions."""
        return iter(self.items)

    def __getitem__(self, index: int) -> LocationSuggestion:
        """Access suggestion by index."""
        return self.items[index]

    def is_empty(self) -> bool:
        """Return True if collection is empty."""
        return len(self.items) == 0

    def first(self) -> LocationSuggestion | None:
        """Return first suggestion if available."""
        if self.is_empty():
            return None
        return self.items[0]

    def find_city_match(self, city_name: str) -> LocationSuggestion | None:
        """Find first city suggestion matching target name."""
        target = city_name.strip().lower()
        for item in self.items:
            if item.category == LocationCategory.CITY and item.city.strip().lower() == target:
                return item
        return None
