"""Provider interfaces and capabilities for central rental research MCP."""

from typing import Protocol, runtime_checkable
from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.domain.listing import ListingCollection
from vivareal_research.domain.location import LocationCollection
from vivareal_research.domain.property import PropertyDetail


@runtime_checkable
class RentalSearchCapability(Protocol):
    """Capability protocol for searching rental properties."""

    def search_rentals(self, criteria: RentalSearchCriteria) -> ListingCollection:
        """Search rental listings matching filter criteria."""
        ...


@runtime_checkable
class RentalDetailCapability(Protocol):
    """Capability protocol for retrieving single property details."""

    def get_property_detail(self, property_url: str) -> PropertyDetail:
        """Retrieve full details of a specific property listing."""
        ...


@runtime_checkable
class RentalLocationsCapability(Protocol):
    """Capability protocol for discovering supported locations."""

    def suggest_locations(self, query: str, size: int = 10) -> LocationCollection:
        """Retrieve matching cities, neighborhoods, and location identifiers."""
        ...


@runtime_checkable
class RentalProviderProtocol(
    RentalSearchCapability,
    RentalDetailCapability,
    RentalLocationsCapability,
    Protocol,
):
    """Complete provider interface for Central Rental Research MCP integration."""

    def provider_name(self) -> str:
        """Return unique provider name identifier."""
        ...
