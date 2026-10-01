"""Viva Real rental search provider implementation for central MCP."""

from scripts.interfaces.provider import RentalProviderProtocol
from vivareal_research.client import VivaRealRentalClient
from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.domain.listing import ListingCollection
from vivareal_research.domain.location import LocationCollection
from vivareal_research.domain.property import PropertyDetail


class VivaRealRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Viva Real (Grupo OLX)."""

    def __init__(self, client: VivaRealRentalClient | None = None) -> None:
        """Initialize provider with client facade."""
        self._client = client or VivaRealRentalClient()

    @classmethod
    def create_default(cls) -> "VivaRealRentalProvider":
        """Factory method constructing provider with default dependencies."""
        return cls(client=VivaRealRentalClient())

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "vivareal"

    def search_rentals(self, criteria: RentalSearchCriteria) -> ListingCollection:
        """Search rental listings using criteria."""
        return self._client.search_rentals(criteria)

    def get_property_detail(self, property_url: str) -> PropertyDetail:
        """Retrieve full details for a single property by URL."""
        return self._client.get_property_detail(property_url)

    def suggest_locations(self, query: str, size: int = 10) -> LocationCollection:
        """Suggest matching locations for user search."""
        return self._client.suggest_locations(query, size=size)
