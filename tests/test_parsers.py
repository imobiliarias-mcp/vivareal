"""Unit tests for Viva Real response parsers."""

from vivareal_research.domain.enums import LocationCategory
from vivareal_research.parsers.detail_parser import VivaRealDetailParser
from vivareal_research.parsers.location_parser import VivaRealLocationParser
from vivareal_research.parsers.search_parser import VivaRealSearchParser


def test_search_parser_success() -> None:
    """Test parsing a valid Glue API /v2/listings search response."""
    mock_payload = {
        "search": {
            "totalCount": 1,
            "result": {
                "listings": [
                    {
                        "listing": {
                            "id": "2900513774",
                            "externalId": "REF-001",
                            "title": "Casa para alugar em Timóteo",
                            "usableAreas": [211],
                            "bedrooms": [4],
                            "bathrooms": [3],
                            "parkingSpaces": [2],
                            "pricingInfos": [
                                {
                                    "businessType": "RENTAL",
                                    "price": 2800,
                                    "monthlyCondoFee": 0,
                                    "yearlyIptu": 600,
                                    "rentalInfo": {"monthlyRentalTotalPrice": 2800},
                                }
                            ],
                            "address": {
                                "city": "Timóteo",
                                "neighborhood": "Alphaville",
                                "stateAcronym": "MG",
                                "street": "Rua Elis Regina",
                                "point": {"lat": -19.559862, "lon": -42.59119},
                            },
                        },
                        "link": {
                            "name": "Casa com 4 Quartos para alugar, 211m²",
                            "href": "/imovel/casa-4-quartos-alphaville/",
                        },
                        "account": {"name": "Frederico Zulato"},
                        "medias": [{"url": "img1.webp"}, {"url": "img2.webp"}],
                    }
                ]
            },
        }
    }

    parser = VivaRealSearchParser()
    collection = parser.parse(mock_payload)
    assert len(collection) == 1
    assert collection.total_count == 1

    item = collection[0]
    assert item.listing_id == "2900513774"
    assert item.external_id == "REF-001"
    assert item.title == "Casa com 4 Quartos para alugar, 211m²"
    assert item.pricing.monthly_rent == 2800
    assert item.features.bedrooms == 4
    assert item.features.usable_area == 211
    assert item.address.neighborhood == "Alphaville"
    assert item.address.latitude == -19.559862
    assert item.photos_count == 2
    assert item.advertiser_name == "Frederico Zulato"


def test_detail_parser_json_ld() -> None:
    """Test parsing Schema.org Product JSON-LD from HTML markup."""
    mock_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Casas para alugar em Timóteo</title>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Casa de Luxo em Alphaville",
          "description": "Excelente casa com 4 quartos e churrasqueira.",
          "sku": "2900513774",
          "image": [
            "https://resizedimgs.vivareal.com/img1.webp",
            "https://resizedimgs.vivareal.com/img2.webp"
          ],
          "offers": {
            "@type": "Offer",
            "price": 2800,
            "url": "https://www.vivareal.com.br/imovel/casa-4-quartos/"
          }
        }
        </script>
      </head>
      <body>
        <h1>Casa de Luxo em Alphaville</h1>
      </body>
    </html>
    """
    parser = VivaRealDetailParser()
    detail = parser.parse_html(mock_html)
    assert detail.title() == "Casa de Luxo em Alphaville"
    assert detail.summary.listing_id == "2900513774"
    assert detail.summary.pricing.monthly_rent == 2800
    assert len(detail.gallery()) == 2
    assert detail.gallery().first() == "https://resizedimgs.vivareal.com/img1.webp"
    assert "Excelente casa" in detail.description()


def test_location_parser() -> None:
    """Test parsing Glue API /v4/locations suggestions."""
    mock_payload = {
        "result": [
            {
                "category": "city",
                "address": {
                    "city": "Timóteo",
                    "state": "Minas Gerais",
                    "locationId": "BR>Minas Gerais>NULL>Timoteo",
                    "point": {"lat": -19.582378, "lon": -42.644959},
                },
            },
            {
                "category": "neighborhood",
                "address": {
                    "city": "Timóteo",
                    "neighborhood": "Bromélias",
                    "state": "Minas Gerais",
                    "locationId": "BR>Minas Gerais>NULL>Timoteo>Barrios>Bromelias",
                    "point": {"lat": -19.545438, "lon": -42.655699},
                },
            },
        ]
    }
    parser = VivaRealLocationParser()
    locations = parser.parse(mock_payload)
    assert len(locations) == 2

    city_loc = locations[0]
    assert city_loc.category == LocationCategory.CITY
    assert city_loc.label == "Timóteo"
    assert city_loc.location_id.location_id == "BR>Minas Gerais>NULL>Timoteo"
    assert city_loc.coordinate is not None
    assert city_loc.coordinate.latitude == -19.582378

    bairro_loc = locations[1]
    assert bairro_loc.category == LocationCategory.NEIGHBORHOOD
    assert bairro_loc.label == "Bromélias, Timóteo"
