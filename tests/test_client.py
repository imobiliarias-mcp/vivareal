"""Unit tests for VivaRealRentalClient facade using mocked transport."""

from typing import Any
import pytest
from vivareal_research.client import VivaRealRentalClient
from vivareal_research.collaborators import VivaRealGateway, VivaRealParserSuite
from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.infrastructure.http_client import HttpClientProtocol


class MockHttpClient(HttpClientProtocol):
    """Stubbed HTTP transport for testing facade behaviors."""

    def __init__(self, json_data: dict[str, Any] | None = None, text_data: str = "") -> None:
        self.json_data = json_data or {}
        self.text_data = text_data
        self.last_url = ""

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        self.last_url = url
        return self.json_data

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        self.last_url = url
        return self.text_data


def test_client_search_rentals_with_mock() -> None:
    """Verify search_rentals executes query URL and parses collection."""
    mock_payload = {
        "search": {
            "totalCount": 1,
            "result": {
                "listings": [
                    {
                        "listing": {
                            "id": "111",
                            "externalId": "E111",
                            "pricingInfos": [{"businessType": "RENTAL", "price": 1200}],
                            "usableAreas": [60],
                            "bedrooms": [2],
                            "bathrooms": [1],
                            "address": {"city": "Timóteo", "neighborhood": "Centro"},
                        },
                        "link": {"name": "Apartamento Centro", "href": "/imovel/111/"},
                        "account": {"name": "Corretora"},
                        "medias": [],
                    }
                ]
            },
        }
    }
    mock_http = MockHttpClient(json_data=mock_payload)
    gateway = VivaRealGateway(http_client=mock_http)
    client = VivaRealRentalClient(gateway=gateway)

    criteria = RentalSearchCriteria.for_timoteo_target_prompt()
    results = client.search_rentals(criteria)

    assert len(results) == 1
    assert results.total_count == 1
    assert results[0].listing_id == "111"
    assert "categoryPage=RESULT" in mock_http.last_url
    assert "business=RENTAL" in mock_http.last_url


def test_client_suggest_locations_empty_query() -> None:
    """Verify suggest_locations returns empty collection for blank input."""
    client = VivaRealRentalClient()
    locations = client.suggest_locations("   ")
    assert len(locations) == 0
    assert locations.is_empty() is True


def test_client_get_property_detail_empty_url_fails() -> None:
    """Verify get_property_detail fails fast on empty URL."""
    client = VivaRealRentalClient()
    with pytest.raises(ValueError, match="Property URL cannot be empty"):
        client.get_property_detail("")
