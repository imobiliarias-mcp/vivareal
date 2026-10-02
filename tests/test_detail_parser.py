"""Regression tests for full Viva Real property detail parsing."""

import json

from vivareal_research.parsers.detail_parser import VivaRealDetailParser


def test_detail_parser_reads_ssr_listing_data() -> None:
    """Preserve factual details exposed in Viva Real's server payload."""
    product = {
        "@type": "Product",
        "name": "Imóvel em Bromelias, Timóteo - MG",
        "description": "kitinet mobiliada com ar condicionado e uma vaga de garagem",
        "sku": "2717181340",
        "image": ["https://resizedimgs.vivareal.com/image.webp"],
        "offers": {"price": 1500, "url": "https://www.vivareal.com.br/imovel/flat/"},
    }
    listing = {
        "id": "2717181340",
        "externalId": "1400",
        "address": {
            "city": "Timóteo",
            "stateAcronym": "MG",
            "neighborhood": "Bromelias",
            "street": "Avenida Jovino Augusto da Silva",
            "streetNumber": "25",
            "coordinates": {"latitude": -19.545438, "longitude": -42.655699},
        },
        "prices": {"rental": {"value": 1500, "condominium": 160, "iptu": 90}},
        "amenities": {
            "usableAreas": [53],
            "bedrooms": [1],
            "bathrooms": [1],
            "suites": [1],
            "parkingSpaces": [1],
            "values": ["AIR_CONDITIONING", "FURNISHED"],
        },
        "advertiser": {
            "name": "Valorize Imoveis E Empreendimentos Ltda",
            "phoneNumbers": ["31991074012"],
            "whatsAppNumber": "31991074012",
        },
    }
    rsc_node = ["$", "$L3d", None, {"baseData": {"pageData": {"listing": listing}}}]
    flight_stream = f"3c:{json.dumps(rsc_node)}"
    html_content = (
        f'<script type="application/ld+json">{json.dumps(product)}</script>'
        f"<script>self.__next_f.push([1,{json.dumps(flight_stream)}])</script>"
    )

    detail = VivaRealDetailParser().parse_html(html_content)

    assert detail.summary.address.city == "Timóteo"
    assert detail.summary.address.state_acronym == "MG"
    assert detail.summary.address.neighborhood == "Bromelias"
    assert detail.summary.address.street == "Avenida Jovino Augusto da Silva"
    assert detail.summary.features.usable_area == 53
    assert detail.summary.features.bedrooms == 1
    assert detail.summary.features.bathrooms == 1
    assert detail.summary.features.suites == 1
    assert detail.summary.features.parking_spaces == 1
    assert detail.summary.pricing.monthly_rent == 1500
    assert detail.summary.pricing.monthly_condo == 160
    assert detail.summary.pricing.yearly_iptu == 90
    assert detail.summary.pricing.total_monthly == 1660
    assert detail.summary.advertiser_name == "Valorize Imoveis E Empreendimentos Ltda"
    assert detail.amenities().contains("furnished")
    assert detail.content.contact.phone == "31991074012"
    assert detail.content.contact.whatsapp == "31991074012"
