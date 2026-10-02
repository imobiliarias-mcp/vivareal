# Viva Real API Reference & Developer Recipes

## 1. Quick `curl` Recipes

### 1.1 Reproduce Target Prompt Rental Search (Timóteo, 2-4 Bedrooms)
```bash
curl -s -H "x-domain: .vivareal.com.br" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://glue-api.vivareal.com/v2/listings?portal=VIVAREAL&categoryPage=RESULT&business=RENTAL&addressLocationId=BR%3EMinas+Gerais%3ENULL%3ETimoteo&bedrooms=2,3,4&size=30"
```

### 1.2 Location Autocomplete & Discovery
```bash
curl -s -H "x-domain: .vivareal.com.br" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  "https://glue-api.vivareal.com/v4/locations?portal=VIVAREAL&q=Tim%C3%B3teo&size=10&listingType=USED&businessType=RENTAL&fields=neighborhood,city,street,zone&includeFields=address.neighborhood,address.city,address.state,address.zone,address.locationId,address.point"
```

### 1.3 Property Detail Page Microdata (HTML / JSON-LD)
```bash
curl -s -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  "https://www.vivareal.com.br/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/" | grep -A 30 '"@type": "Product"'
```

---

## 2. Python Code Recipes

### 2.1 Basic Rental Search
```python
from vivareal_research import VivaRealRentalClient, RentalSearchCriteria

client = VivaRealRentalClient()
criteria = RentalSearchCriteria.for_timoteo_target_prompt()

results = client.search_rentals(criteria)
print(f"Total matching: {results.total_count}")

for item in results:
    print(f"[{item.listing_id}] {item.title}")
    print(f"  Rent: R$ {item.pricing.monthly_rent} | Total: R$ {item.pricing.total_monthly}")
    print(f"  Rooms: {item.features.bedrooms} dorms, {item.features.bathrooms} banheiros")
    print(f"  URL: {item.canonical_url}")
```

Search results resolve each Glue API `link.href` against the configured public website base (`web_base`), independently of the API request base (`api_base`). Absolute, relative, and protocol-relative VivaReal property links are accepted only for the configured public host and `/imovel/{slug}/` detail paths; same-host image and search URLs are rejected. Missing or invalid links fail with listing context rather than inventing a route from the internal Glue listing ID. The resolved link remains available under the existing `url` key in MCP output and as `canonical_url` on the Python listing.

### 2.2 Location Autocomplete
```python
from vivareal_research import VivaRealRentalClient

client = VivaRealRentalClient()
locations = client.suggest_locations("Timóteo")

for loc in locations:
    print(f"[{loc.category.value}] {loc.label} -> {loc.location_id.location_id}")
```

### 2.3 Property Detail Retrieval
```python
from vivareal_research import VivaRealRentalClient

client = VivaRealRentalClient()
detail = client.get_property_detail("/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/")

print(f"Title: {detail.title()}")
print(f"Rent: R$ {detail.summary.pricing.monthly_rent}")
print(f"Photos in gallery: {len(detail.gallery())}")
for photo in detail.gallery()[:3]:
    print(f"  Photo: {photo}")
```
