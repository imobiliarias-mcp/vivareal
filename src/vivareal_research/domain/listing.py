"""Listing domain models and first-class collections."""

from dataclasses import dataclass
from typing import Iterator, Sequence


@dataclass(frozen=True)
class ListingPricing:
    """Pricing breakdown for a listing."""

    monthly_rent: int
    monthly_condo: int = 0
    yearly_iptu: int = 0
    total_monthly: int = 0

    def calculate_total(self) -> int:
        """Compute estimated total monthly cost if not set."""
        if self.total_monthly > 0:
            return self.total_monthly
        return self.monthly_rent + self.monthly_condo


@dataclass(frozen=True)
class ListingAddress:
    """Standardized address representation for a listing."""

    neighborhood: str
    city: str
    state_acronym: str
    street: str = ""
    street_number: str = ""
    zip_code: str = ""
    latitude: float | None = None
    longitude: float | None = None

    def display_neighborhood(self) -> str:
        """Format neighborhood and city label."""
        return f"{self.neighborhood}, {self.city} - {self.state_acronym}"


@dataclass(frozen=True)
class ListingFeatures:
    """Internal property physical features bundle."""

    usable_area: int
    bedrooms: int
    bathrooms: int
    suites: int = 0
    parking_spaces: int = 0


@dataclass(frozen=True)
class ListingSummary:
    """Core summary card representing a real estate listing."""

    listing_id: str
    external_id: str
    title: str
    address: ListingAddress
    pricing: ListingPricing
    features: ListingFeatures
    photos_count: int
    canonical_url: str
    advertiser_name: str


@dataclass(frozen=True)
class ListingCollection:
    """First-class collection wrapping search results."""

    listings: tuple[ListingSummary, ...]
    total_count: int

    def __len__(self) -> int:
        """Return number of listings on this page."""
        return len(self.listings)

    def __iter__(self) -> Iterator[ListingSummary]:
        """Iterate over listings."""
        return iter(self.listings)

    def __getitem__(self, index: int) -> ListingSummary:
        """Access listing by index."""
        return self.listings[index]

    def is_empty(self) -> bool:
        """Return True if collection has zero items."""
        return len(self.listings) == 0

    def first(self) -> ListingSummary | None:
        """Return first listing if present."""
        if self.is_empty():
            return None
        return self.listings[0]
