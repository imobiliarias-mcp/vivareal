"""Central rental research client facade for Viva Real."""

from vivareal_research.collaborators import VivaRealGateway, VivaRealParserSuite
from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.domain.listing import ListingCollection
from vivareal_research.domain.location import LocationCollection
from vivareal_research.domain.property import PropertyDetail


class VivaRealRentalClient:
    """Central rental research client facade for Viva Real (Grupo OLX)."""

    def __init__(
        self,
        gateway: VivaRealGateway | None = None,
        parsers: VivaRealParserSuite | None = None,
    ) -> None:
        """Initialize client with collaborators bundle."""
        self._gateway = gateway or VivaRealGateway()
        url_builder = self._gateway.builder()
        public_base_url = url_builder.public_base_url()
        self._parsers = parsers or VivaRealParserSuite(public_base_url=public_base_url)

    def search_rentals(self, criteria: RentalSearchCriteria) -> ListingCollection:
        """Search rental listings using strongly-typed criteria."""
        url = self._gateway.builder().build_search_api_url(criteria)
        payload = self._gateway.http().get_json(url)
        return self._parsers.search().parse(payload)

    def suggest_locations(self, query: str, size: int = 10) -> LocationCollection:
        """Query location autocomplete for matching cities and neighborhoods."""
        if not query.strip():
            return LocationCollection(items=())
        url = self._gateway.builder().build_locations_api_url(query, size=size)
        payload = self._gateway.http().get_json(url)
        return self._parsers.location().parse(payload)

    def get_property_detail(self, property_url: str) -> PropertyDetail:
        """Retrieve full details and media gallery for a specific property listing."""
        if not property_url.strip():
            raise ValueError("Property URL cannot be empty")
        target_url = self._normalize_property_url(property_url)
        html_content = self._gateway.http().get_text(target_url)
        return self._parsers.detail().parse_html(html_content, fallback_url=target_url)

    def build_canonical_web_url(self, criteria: RentalSearchCriteria) -> str:
        """Construct the canonical browser navigation URL matching criteria."""
        return self._gateway.builder().build_web_search_url(criteria)

    def _normalize_property_url(self, url: str) -> str:
        """Ensure property URL is an absolute HTTPS URL."""
        if url.startswith(("http://", "https://")):
            return url
        clean_path = url.lstrip("/")
        return f"https://www.vivareal.com.br/{clean_path}"
