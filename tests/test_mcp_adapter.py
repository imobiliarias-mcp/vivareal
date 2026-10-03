"""Unit tests for VivaRealMcpAdapter."""

from scripts.mcp.tools import VivaRealMcpAdapter, vivareal_search_rentals
from scripts.providers.vivareal import VivaRealRentalProvider


class DummyClient:
    """Dummy client for testing VivaReal adapter without network calls."""

    def search_rentals(self, criteria):
        class DummyCollection(list):
            total_count = 0
        return DummyCollection()

    def get_property_detail(self, property_url):
        class DummyDetail:
            def title(self):
                return "Apto Timóteo"
            def description(self):
                return "Descrição teste"
            def gallery(self):
                return ["https://img.vivareal.com/1.jpg"]
            @property
            def summary(self):
                class DummySummary:
                    canonical_url = "https://www.vivareal.com.br/imovel/123"
                    class pricing:
                        monthly_rent = 1200
                return DummySummary()
        return DummyDetail()

    def suggest_locations(self, query, size=10):
        class DummyLocationCollection(list):
            def find_city_match(self, city):
                return None
            def first(self):
                return None
        return DummyLocationCollection()


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    info = adapter.get_provider_info()
    assert info["provider_name"] == "vivareal"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    result_dict = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(result_dict, dict)
    assert result_dict["provider"] == "vivareal"
    assert "listings" in result_dict


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    detail_dict = adapter.get_property_detail("https://www.vivareal.com.br/imovel/123")
    assert isinstance(detail_dict, dict)
    assert detail_dict["title"] == "Apto Timóteo"
    assert detail_dict["rent_price"] == 1200
