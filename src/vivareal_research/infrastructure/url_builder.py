"""URL builder for Viva Real Glue API and website navigation."""

import urllib.parse

from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.domain.enums import PropertyType


class VivaRealUrlBuilder:
    """Constructs canonical URLs for Glue API and website queries."""

    DEFAULT_API_BASE = "https://glue-api.vivareal.com"
    DEFAULT_WEB_BASE = "https://www.vivareal.com.br"

    def __init__(
        self,
        api_base: str = DEFAULT_API_BASE,
        web_base: str = DEFAULT_WEB_BASE,
    ) -> None:
        """Initialize URL builder with base hosts."""
        self._api_base = api_base.rstrip("/")
        self._web_base = web_base.rstrip("/")

    def public_base_url(self) -> str:
        """Return the configured public website origin, not the Glue API host."""
        return self._web_base

    def build_search_api_url(self, criteria: RentalSearchCriteria) -> str:
        """Build Glue API /v2/listings search query URL."""
        params = self._build_search_query_parameters(criteria)
        query_string = urllib.parse.urlencode(params)
        return f"{self._api_base}/v2/listings?{query_string}"

    def build_locations_api_url(self, query: str, size: int = 10) -> str:
        """Build Glue API /v4/locations autocomplete query URL."""
        params = {
            "portal": "VIVAREAL",
            "q": query.strip(),
            "size": size,
            "listingType": "USED",
            "businessType": "RENTAL",
            "fields": "neighborhood,city,street,zone",
            "includeFields": (
                "address.neighborhood,address.city,address.state,"
                "address.zone,address.locationId,address.point"
            ),
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self._api_base}/v4/locations?{query_string}"

    def build_web_search_url(self, criteria: RentalSearchCriteria) -> str:
        """Build canonical browser search URL matching portal navigation."""
        path_state = self._slugify(criteria.location.state)
        path_city = self._slugify(criteria.location.city)
        onde_value = self._encode_onde_parameter(criteria)
        query_params = {"onde": onde_value}
        self._append_web_filters(query_params, criteria)
        query_string = urllib.parse.urlencode(query_params)
        return f"{self._web_base}/aluguel/{path_state}/{path_city}/?{query_string}"

    def _build_search_query_parameters(self, criteria: RentalSearchCriteria) -> dict[str, str]:
        """Assemble dictionary of Glue API search parameters."""
        params = {
            "portal": "VIVAREAL",
            "categoryPage": "RESULT",
            "business": criteria.filters.business_type.value,
            "addressLocationId": criteria.location.location_id.location_id,
            "addressCity": criteria.location.city,
            "addressState": criteria.location.state,
            "sort": criteria.filters.sort_order.value,
            "size": str(criteria.filters.pagination.page_size),
            "from": str(criteria.filters.pagination.offset()),
            "page": str(criteria.filters.pagination.page_number),
        }
        self._append_api_filters(params, criteria)
        return params

    def _append_api_filters(self, params: dict[str, str], criteria: RentalSearchCriteria) -> None:
        """Append optional room, price, area and unit filters."""
        f = criteria.filters
        if not f.bedrooms.is_empty():
            params["bedrooms"] = f.bedrooms.to_query_string()
        if not f.bathrooms.is_empty():
            params["bathrooms"] = f.bathrooms.to_query_string()
        if not f.parking_spaces.is_empty():
            params["parkingSpaces"] = f.parking_spaces.to_query_string()
        self._append_numerical_filters(params, criteria)
        self._append_unit_type_filters(params, criteria)

    def _append_numerical_filters(
        self, params: dict[str, str], criteria: RentalSearchCriteria
    ) -> None:
        """Append price and area boundary parameters."""
        f = criteria.filters
        if f.price_range.minimum_amount is not None:
            params["priceMin"] = str(f.price_range.minimum_amount)
        if f.price_range.maximum_amount is not None:
            params["priceMax"] = str(f.price_range.maximum_amount)
        if f.area_range.minimum_area is not None:
            params["usableAreasMin"] = str(f.area_range.minimum_area)
        if f.area_range.maximum_area is not None:
            params["usableAreasMax"] = str(f.area_range.maximum_area)

    def _append_unit_type_filters(
        self, params: dict[str, str], criteria: RentalSearchCriteria
    ) -> None:
        """Append 4-tuple unit type filtering if not ALL."""
        pt = criteria.filters.property_type
        if pt == PropertyType.ALL:
            return
        if pt == PropertyType.APARTMENT:
            params["unitTypes"] = "APARTMENT"
            params["unitTypesV3"] = "APARTMENT"
            params["usageTypes"] = "RESIDENTIAL"
            params["unitSubTypes"] = "UnitSubType_NONE,DUPLEX,LOFT,STUDIO,TRIPLEX"
            return
        if pt == PropertyType.HOME:
            params["unitTypes"] = "HOME"
            params["unitTypesV3"] = "HOME"
            params["usageTypes"] = "RESIDENTIAL"
            params["unitSubTypes"] = "UnitSubType_NONE,SINGLE_STOREY_HOUSE,VILLAGE_HOUSE,KITNET"

    def _encode_onde_parameter(self, criteria: RentalSearchCriteria) -> str:
        """Format 12-segment comma-separated onde navigation parameter."""
        loc = criteria.location
        coord = loc.coordinate
        lat_str = str(coord.latitude) if coord else ""
        lon_str = str(coord.longitude) if coord else ""
        segments = [
            "",
            loc.state,
            loc.city,
            "",
            "",
            "",
            "",
            "city",
            loc.location_id.location_id,
            lat_str,
            lon_str,
            "",
        ]
        return ",".join(segments)

    def _append_web_filters(
        self, query_params: dict[str, str], criteria: RentalSearchCriteria
    ) -> None:
        """Append query parameters for website URLs."""
        f = criteria.filters
        if not f.bedrooms.is_empty():
            query_params["quartos"] = f.bedrooms.to_query_string()
        if not f.bathrooms.is_empty():
            query_params["banheiros"] = f.bathrooms.to_query_string()
        if not f.parking_spaces.is_empty():
            query_params["vagas"] = f.parking_spaces.to_query_string()

    def _slugify(self, value: str) -> str:
        """Normalize string to URL slug segment."""
        sanitized = value.strip().lower()
        replacements = [
            ("á", "a"),
            ("ã", "a"),
            ("â", "a"),
            ("é", "e"),
            ("ê", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ô", "o"),
            ("õ", "o"),
            ("ú", "u"),
            ("ç", "c"),
            (" ", "-"),
        ]
        for src, dest in replacements:
            sanitized = sanitized.replace(src, dest)
        return sanitized
