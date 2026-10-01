"""Live integration tests against Viva Real endpoints."""

import pytest
from vivareal_research import (
    FilterSpecification,
    LocationSpecification,
    PageRequest,
    RentalSearchCriteria,
    RoomFilter,
    SortOrder,
    VivaRealRentalClient,
)


@pytest.mark.integration
def test_live_target_prompt_search() -> None:
    """Verify live search reproducing exact user target prompt."""
    client = VivaRealRentalClient()
    criteria = RentalSearchCriteria.for_timoteo_target_prompt()

    results = client.search_rentals(criteria)
    assert results.total_count >= 2
    assert len(results) >= 2

    # Check listing IDs and attributes
    ids = [item.listing_id for item in results]
    assert "2900513774" in ids or "2622514616" in ids

    # Check that rooms match filter [2, 3, 4]
    for item in results:
        assert item.features.bedrooms in [2, 3, 4]
        assert item.pricing.monthly_rent > 0
        assert item.canonical_url.startswith("/imovel/") or item.canonical_url.startswith("http")


@pytest.mark.integration
def test_live_location_autocomplete() -> None:
    """Verify live location discovery for Timóteo."""
    client = VivaRealRentalClient()
    locations = client.suggest_locations("Timóteo")

    assert len(locations) > 0
    match = locations.find_city_match("Timóteo")
    assert match is not None
    assert match.location_id.location_id == "BR>Minas Gerais>NULL>Timoteo"
    assert match.city == "Timóteo"
    assert match.coordinate is not None
    assert abs(match.coordinate.latitude - (-19.582378)) < 0.01


@pytest.mark.integration
def test_live_property_detail() -> None:
    """Verify live property detail and gallery retrieval."""
    client = VivaRealRentalClient()
    detail = client.get_property_detail(
        "/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/"
    )

    assert "Alphaville" in detail.title() or "Timóteo" in detail.title()
    assert detail.summary.pricing.monthly_rent == 2800
    assert len(detail.gallery()) > 0
    assert "resizedimgs.vivareal.com" in (detail.gallery().first() or "")
    assert len(detail.description()) > 0


@pytest.mark.integration
def test_live_pagination_boundaries() -> None:
    """Verify live pagination and boundary behaviors."""
    client = VivaRealRentalClient()
    loc = LocationSpecification.create_timoteo_default()

    # Request page 1 with size 1
    p1 = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=1, page_size=1),
        ),
    )
    r1 = client.search_rentals(p1)
    assert len(r1) == 1

    # Request page 2 with size 1
    p2 = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=2, page_size=1),
        ),
    )
    r2 = client.search_rentals(p2)
    assert len(r2) == 1
    assert r1[0].listing_id != r2[0].listing_id

    # Request out of bounds page (page 10 for 2 items)
    p_out = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=10, page_size=1),
        ),
    )
    r_out = client.search_rentals(p_out)
    assert len(r_out) == 0


@pytest.mark.integration
def test_live_sort_orders() -> None:
    """Verify live sorting orders."""
    client = VivaRealRentalClient()
    loc = LocationSpecification.create_timoteo_default()

    for order in [SortOrder.MOST_RELEVANT, SortOrder.LOWEST_PRICE, SortOrder.BIGGEST_PRICE]:
        crit = RentalSearchCriteria(
            location=loc,
            filters=FilterSpecification(
                sort_order=order,
                pagination=PageRequest(page_number=1, page_size=5),
            ),
        )
        res = client.search_rentals(crit)
        assert len(res) > 0
