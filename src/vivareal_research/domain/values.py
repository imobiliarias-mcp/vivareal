"""Domain value objects for Viva Real rental research."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates minimum and maximum monetary amounts."""

    minimum_amount: int | None = None
    maximum_amount: int | None = None

    def __post_init__(self) -> None:
        """Validate price constraints fail-fast."""
        self._validate_non_negative(self.minimum_amount)
        self._validate_non_negative(self.maximum_amount)
        self._validate_range_order()

    def _validate_non_negative(self, amount: int | None) -> None:
        """Validate amount is positive or zero."""
        if amount is None:
            return
        if amount < 0:
            raise ValueError("Price amount cannot be negative")

    def _validate_range_order(self) -> None:
        """Ensure minimum amount does not exceed maximum amount."""
        if self.minimum_amount is None or self.maximum_amount is None:
            return
        if self.minimum_amount > self.maximum_amount:
            raise ValueError("Minimum price cannot exceed maximum price")

    def has_filter(self) -> bool:
        """Check if any price boundary is specified."""
        return self.minimum_amount is not None or self.maximum_amount is not None


@dataclass(frozen=True)
class AreaRange:
    """Encapsulates usable floor area range in square meters."""

    minimum_area: int | None = None
    maximum_area: int | None = None

    def __post_init__(self) -> None:
        """Validate area constraints fail-fast."""
        self._validate_non_negative(self.minimum_area)
        self._validate_non_negative(self.maximum_area)
        self._validate_range_order()

    def _validate_non_negative(self, area: int | None) -> None:
        """Validate area is positive or zero."""
        if area is None:
            return
        if area < 0:
            raise ValueError("Area cannot be negative")

    def _validate_range_order(self) -> None:
        """Ensure minimum area does not exceed maximum area."""
        if self.minimum_area is None or self.maximum_area is None:
            return
        if self.minimum_area > self.maximum_area:
            raise ValueError("Minimum area cannot exceed maximum area")

    def has_filter(self) -> bool:
        """Check if any area boundary is specified."""
        return self.minimum_area is not None or self.maximum_area is not None


@dataclass(frozen=True)
class RoomFilter:
    """Encapsulates discrete room count selections."""

    counts: tuple[int, ...]

    @classmethod
    def from_iterable(cls, values: Sequence[int]) -> "RoomFilter":
        """Factory constructing RoomFilter from integer collection."""
        sanitized = tuple(sorted(set(v for v in values if v >= 0)))
        return cls(counts=sanitized)

    def to_query_string(self) -> str:
        """Format room filter as comma-separated query parameter."""
        return ",".join(str(c) for c in self.counts)

    def is_empty(self) -> bool:
        """Check if filter has no room counts."""
        return len(self.counts) == 0


@dataclass(frozen=True)
class PageRequest:
    """Encapsulates 1-indexed pagination parameters."""

    page_number: int = 1
    page_size: int = 30

    def __post_init__(self) -> None:
        """Validate pagination boundaries."""
        if self.page_number < 1:
            raise ValueError("Page number must be 1 or greater")
        if self.page_size < 1 or self.page_size > 30:
            raise ValueError("Page size must be between 1 and 30")

    def offset(self) -> int:
        """Calculate zero-based offset for API requests."""
        return self.page_size * (self.page_number - 1)


@dataclass(frozen=True)
class LocationCoordinate:
    """Geographical coordinate point."""

    latitude: float
    longitude: float


@dataclass(frozen=True)
class LocationIdentifier:
    """Strongly typed location string representation."""

    location_id: str

    def __post_init__(self) -> None:
        """Validate location identifier is non-empty."""
        if not self.location_id.strip():
            raise ValueError("Location ID cannot be empty")
