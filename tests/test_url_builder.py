"""Unit tests for VivaRealUrlBuilder."""

import urllib.parse
from vivareal_research.domain.criteria import (
    FilterSpecification,
    LocationSpecification,
    RentalSearchCriteria,
)
from vivareal_research.domain.enums import PropertyType, SortOrder
from vivareal_research.domain.values import (
    AreaRange,
    PageRequest,
    PriceRange,
    RoomFilter,
)
from vivareal_research.infrastructure.url_builder import VivaRealUrlBuilder


def test_build_web_search_url_matching_target() -> None:
    """Verify built web URL matches the target prompt canonical navigation."""
    builder = VivaRealUrlBuilder()
    criteria = RentalSearchCriteria.for_timoteo_target_prompt()
    web_url = builder.build_web_search_url(criteria)

    assert "aluguel/minas-gerais/timoteo/" in web_url
    assert "quartos=2%2C3%2C4" in web_url
    assert "onde=" in web_url
    parsed = urllib.parse.urlparse(web_url)
    params = urllib.parse.parse_qs(parsed.query)
    assert params["quartos"] == ["2,3,4"]
    assert "BR>Minas Gerais>NULL>Timoteo" in params["onde"][0]


def test_build_search_api_url() -> None:
    """Verify built Glue API query URL contains expected parameters."""
    builder = VivaRealUrlBuilder()
    loc = LocationSpecification.create_timoteo_default()
    criteria = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            property_type=PropertyType.APARTMENT,
            bedrooms=RoomFilter.from_iterable([2, 3]),
            price_range=PriceRange(minimum_amount=1000, maximum_amount=3000),
            area_range=AreaRange(minimum_area=50, maximum_area=150),
            sort_order=SortOrder.LOWEST_PRICE,
            pagination=PageRequest(page_number=2, page_size=20),
        ),
    )
    api_url = builder.build_search_api_url(criteria)
    assert "/v2/listings" in api_url

    parsed = urllib.parse.urlparse(api_url)
    params = urllib.parse.parse_qs(parsed.query)
    assert params["portal"] == ["VIVAREAL"]
    assert params["business"] == ["RENTAL"]
    assert params["bedrooms"] == ["2,3"]
    assert params["priceMin"] == ["1000"]
    assert params["priceMax"] == ["3000"]
    assert params["usableAreasMin"] == ["50"]
    assert params["usableAreasMax"] == ["150"]
    assert params["sort"] == ["LOWEST_PRICE"]
    assert params["size"] == ["20"]
    assert params["from"] == ["20"]
    assert params["page"] == ["2"]
    assert params["unitTypes"] == ["APARTMENT"]


def test_build_locations_api_url() -> None:
    """Verify built autocomplete locations API URL."""
    builder = VivaRealUrlBuilder()
    loc_url = builder.build_locations_api_url("Timóteo", size=5)
    assert "/v4/locations" in loc_url

    parsed = urllib.parse.urlparse(loc_url)
    params = urllib.parse.parse_qs(parsed.query)
    assert params["portal"] == ["VIVAREAL"]
    assert params["q"] == ["Timóteo"]
    assert params["size"] == ["5"]
    assert params["businessType"] == ["RENTAL"]
