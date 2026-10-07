"""Unit tests for VivaRealMcpAdapter."""

from scripts.mcp.tools import VivaRealMcpAdapter, vivareal_search_rentals
from scripts.providers.vivareal import VivaRealRentalProvider


class DummyClient:
    """Dummy client for testing VivaReal adapter without network calls."""

    def search_rentals(self, criteria):
        class DummyListing:
            listing_id = "1"
            title = "Apto"
            class pricing:
                monthly_rent = 1200
                monthly_condo = 300
                yearly_iptu = 600
                total_monthly = 1500
            class features:
                bedrooms = 2
                bathrooms = 1
                parking_spaces = 1
                usable_area = 60
            class address:
                neighborhood = "Centro"
                city = "Timóteo"
            canonical_url = "https://www.vivareal.com.br/imovel/1"
            advertiser_name = "Imobiliaria"

        class DummyCollection(list):
            total_count = 1
            def __init__(self):
                super().__init__([DummyListing()])
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
                        monthly_condo = 350
                        yearly_iptu = 600
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
    assert len(result_dict["listings"]) == 1
    assert result_dict["listings"][0]["condo_fee"] == 300.0
    assert result_dict["listings"][0]["iptu"] == 50.0


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    detail_dict = adapter.get_property_detail("https://www.vivareal.com.br/imovel/123")
    assert isinstance(detail_dict, dict)
    assert detail_dict["title"] == "Apto Timóteo"
    assert detail_dict["rent_price"] == 1200
    assert detail_dict["condo_fee"] == 350.0
    assert detail_dict["iptu"] == 50.0


def test_unconstrained_search_does_not_force_bedroom_filter():
    """No bedrooms argument must produce an empty RoomFilter (no API constraint)."""
    from vivareal_research.domain.values import RoomFilter

    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    filter_spec = adapter._build_filter(bedrooms=0, min_price=0.0, max_price=0.0, page=1)
    assert filter_spec.bedrooms.is_empty()


def test_zero_bedrooms_does_not_force_bedroom_filter():
    """Explicit bedrooms=0 must also produce an empty RoomFilter."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    filter_spec = adapter._build_filter(bedrooms=0, min_price=0.0, max_price=0.0, page=1)
    assert filter_spec.bedrooms.is_empty()


def test_explicit_bedrooms_preserves_filter():
    """bedrooms=2 must produce RoomFilter with exactly [2]."""
    provider = VivaRealRentalProvider(client=DummyClient())
    adapter = VivaRealMcpAdapter(provider=provider)

    filter_spec = adapter._build_filter(bedrooms=2, min_price=0.0, max_price=0.0, page=1)
    assert not filter_spec.bedrooms.is_empty()
    assert filter_spec.bedrooms.counts == (2,)
