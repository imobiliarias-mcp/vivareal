"""Unit tests for VivaRealRentalClient facade using mocked transport."""

from typing import Any

import pytest

from scripts import run_search
from scripts.mcp import tools as mcp_tools
from vivareal_research.client import VivaRealRentalClient
from vivareal_research.collaborators import VivaRealGateway
from vivareal_research.domain.criteria import RentalSearchCriteria
from vivareal_research.domain.listing import ListingCollection
from vivareal_research.domain.location import LocationCollection
from vivareal_research.infrastructure.http_client import HttpClientProtocol
from vivareal_research.infrastructure.url_builder import VivaRealUrlBuilder
from vivareal_research.parsers.search_parser import VivaRealSearchParser


class MockHttpClient(HttpClientProtocol):
    """Stubbed HTTP transport for testing facade behaviors."""

    def __init__(self, json_data: dict[str, Any] | None = None, text_data: str = "") -> None:
        self.json_data = json_data or {}
        self.text_data = text_data
        self.last_url = ""
        self.call_count = 0

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        self.last_url = url
        self.call_count += 1
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
    builder = VivaRealUrlBuilder(
        api_base="https://glue-api.example",
        web_base="https://public.example",
    )
    gateway = VivaRealGateway(http_client=mock_http, url_builder=builder)
    client = VivaRealRentalClient(gateway=gateway)

    criteria = RentalSearchCriteria.for_timoteo_target_prompt()
    results = client.search_rentals(criteria)

    assert len(results) == 1
    assert results.total_count == 1
    assert results[0].listing_id == "111"
    assert results[0].canonical_url == "https://public.example/imovel/111/"
    assert mock_http.last_url.startswith("https://glue-api.example/v2/listings?")
    assert "categoryPage=RESULT" in mock_http.last_url
    assert "business=RENTAL" in mock_http.last_url
    assert mock_http.call_count == 1


def test_client_suggest_locations_empty_query() -> None:
    """Verify suggest_locations returns empty collection for blank input."""
    client = VivaRealRentalClient()
    locations = client.suggest_locations("   ")
    assert len(locations) == 0
    assert locations.is_empty() is True


def _public_listing_collection() -> ListingCollection:
    """Build a serialized search result with a relative API card link."""
    payload = {
        "search": {
            "totalCount": 1,
            "result": {
                "listings": [
                    {
                        "listing": {"id": "internal-608", "externalId": "REF-608"},
                        "link": {"name": "Casa", "href": "/imovel/casa-608/"},
                    }
                ]
            },
        }
    }
    return VivaRealSearchParser("https://public.example").parse(payload)


def test_mcp_search_serializes_resolved_public_property_url(monkeypatch) -> None:
    """Expose the normalized URL through the existing MCP search output."""
    collection = _public_listing_collection()

    class StubProvider:
        def provider_name(self) -> str:
            return "vivareal"

        def suggest_locations(self, query: str, size: int = 10) -> LocationCollection:
            return LocationCollection(items=())

        def search_rentals(self, criteria: RentalSearchCriteria) -> ListingCollection:
            return collection

    monkeypatch.setattr(
        mcp_tools.VivaRealRentalProvider,
        "create_default",
        classmethod(lambda cls: StubProvider()),
    )

    result = mcp_tools.vivareal_search_rentals(city="Timóteo", bedrooms=[2])

    assert result["listings"][0]["url"] == "https://public.example/imovel/casa-608/"


def test_cli_search_prints_resolved_public_property_url(monkeypatch, capsys) -> None:
    """Keep the public link visible in the existing text-mode CLI."""
    collection = _public_listing_collection()

    class StubClient:
        def build_canonical_web_url(self, criteria: RentalSearchCriteria) -> str:
            return "https://public.example/aluguel/mg/timoteo/"

        def search_rentals(self, criteria: RentalSearchCriteria) -> ListingCollection:
            return collection

    monkeypatch.setattr(run_search, "VivaRealRentalClient", StubClient)
    run_search.main()

    assert "URL: https://public.example/imovel/casa-608/" in capsys.readouterr().out


def test_client_get_property_detail_empty_url_fails() -> None:
    """Verify get_property_detail fails fast on empty URL."""
    client = VivaRealRentalClient()
    with pytest.raises(ValueError, match="Property URL cannot be empty"):
        client.get_property_detail("")
