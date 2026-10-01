# Usage Guide & Central MCP Integration

## 1. Quick Python Usage

```python
from vivareal_research import VivaRealRentalClient, RentalSearchCriteria

client = VivaRealRentalClient()

# 1. Search rentals for Timóteo matching prompt (2, 3, 4 bedrooms)
criteria = RentalSearchCriteria.for_timoteo_target_prompt()
results = client.search_rentals(criteria)

print(f"Total found: {results.total_count}")
for item in results:
    print(f"[{item.listing_id}] {item.title} - R$ {item.pricing.monthly_rent}")

# 2. Location autocomplete
locations = client.suggest_locations("Timóteo")
for loc in locations:
    print(f"{loc.label} -> {loc.location_id.location_id}")

# 3. Property detail & gallery
detail = client.get_property_detail("/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/")
print(f"Photos in gallery: {len(detail.gallery())}")
```

---

## 2. Central Rental Research MCP Integration

The `VivaRealRentalProvider` class in `scripts/providers/vivareal.py` implements `RentalProviderProtocol` from `scripts/interfaces/provider.py`.

### Register Provider in Central MCP
```python
from scripts.providers.vivareal import VivaRealRentalProvider

def register_providers(registry):
    provider = VivaRealRentalProvider.create_default()
    registry.register(provider.provider_name(), provider)
```

### Call MCP Tools directly
```python
from scripts.mcp.tools import (
    vivareal_search_rentals,
    vivareal_get_property_detail,
    vivareal_suggest_locations,
)

# Search rentals
search_result = vivareal_search_rentals(city="Timóteo", bedrooms=[2, 3, 4])

# Location suggestions
loc_suggestions = vivareal_suggest_locations("Timóteo")

# Property detail
prop_detail = vivareal_get_property_detail("/imovel/.../")
```
