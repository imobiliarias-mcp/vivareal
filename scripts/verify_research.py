import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.mcp.tools import (
    vivareal_get_property_detail,
    vivareal_search_rentals,
    vivareal_suggest_locations,
)
from vivareal_research import (
    FilterSpecification,
    LocationSpecification,
    PageRequest,
    RentalSearchCriteria,
    RoomFilter,
    SortOrder,
    VivaRealRentalClient,
)


def verify_target_search() -> str:
    """Verify target prompt search query."""
    print("\n--- 1. Target URL Search Reproduction ---")
    client = VivaRealRentalClient()
    criteria = RentalSearchCriteria.for_timoteo_target_prompt()

    web_url = client.build_canonical_web_url(criteria)
    print(f"Generated Web URL: {web_url}")

    results = client.search_rentals(criteria)
    print(f"Total matching listings: {results.total_count}")
    print(f"Returned on page: {len(results)}")
    assert len(results) > 0, "Expected at least 1 listing for Timóteo prompt"

    first_item = results[0]
    print(f"Sample listing: [{first_item.listing_id}] {first_item.title}")
    print(f"  Rent: R$ {first_item.pricing.monthly_rent} | Total: R$ {first_item.pricing.total_monthly}")
    print(f"  Bedrooms: {first_item.features.bedrooms} | Usable area: {first_item.features.usable_area} m²")
    print(f"  Location: {first_item.address.display_neighborhood()}")
    return first_item.canonical_url


def verify_location_discovery() -> None:
    """Verify location autocomplete."""
    print("\n--- 2. Location Discovery & Autocomplete ---")
    client = VivaRealRentalClient()
    locations = client.suggest_locations("Timóteo")
    print(f"Discovered locations: {len(locations)}")
    assert len(locations) > 0, "Expected at least 1 location for Timóteo"

    city_match = locations.find_city_match("Timóteo")
    assert city_match is not None, "Expected city match for Timóteo"
    print(f"City Match: {city_match.label} -> LocationId: {city_match.location_id.location_id}")
    if city_match.coordinate:
        print(f"Coordinates: {city_match.coordinate.latitude}, {city_match.coordinate.longitude}")


def verify_property_details(property_url: str) -> None:
    """Verify property detail retrieval and photo gallery."""
    print("\n--- 3. Property Detail & Photo Gallery Retrieval ---")
    client = VivaRealRentalClient()
    detail = client.get_property_detail(property_url)

    print(f"Title: {detail.title()}")
    print(f"Rent: R$ {detail.summary.pricing.monthly_rent:,}")
    print(f"Total photos: {len(detail.gallery())}")
    assert len(detail.gallery()) > 0, "Expected photos in gallery"
    print(f"First photo: {detail.gallery().first()}")
    assert len(detail.description()) > 0, "Expected non-empty description"
    print(f"Description preview: {detail.description()[:120].strip()}...")


def verify_pagination() -> None:
    """Verify pagination mechanics and boundaries."""
    print("\n--- 4. Pagination & Boundary Testing ---")
    client = VivaRealRentalClient()
    loc = LocationSpecification.create_timoteo_default()

    # Page 1 (size=1)
    p1 = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=1, page_size=1),
        ),
    )
    res1 = client.search_rentals(p1)
    print(f"Page 1 (size 1): returned {len(res1)} item, id={res1[0].listing_id}")

    # Page 2 (size=1)
    p2 = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=2, page_size=1),
        ),
    )
    res2 = client.search_rentals(p2)
    print(f"Page 2 (size 1): returned {len(res2)} item, id={res2[0].listing_id}")
    assert res1[0].listing_id != res2[0].listing_id, "Page 1 and Page 2 should have distinct listings"

    # Out of bounds page
    p_empty = RentalSearchCriteria(
        location=loc,
        filters=FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            pagination=PageRequest(page_number=10, page_size=1),
        ),
    )
    res_empty = client.search_rentals(p_empty)
    print(f"Page 10 (out of bounds for 2 items): returned {len(res_empty)} items")
    assert len(res_empty) == 0, "Out of bounds page should return empty list"


def verify_sorting() -> None:
    """Verify sort orders."""
    print("\n--- 5. Sorting Orders Verification ---")
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
        print(f"Sort {order.value}: returned {len(res)} items")
        assert len(res) > 0, f"Expected results for sort {order.value}"


def verify_mcp_tools() -> None:
    """Verify MCP tools facade layer."""
    print("\n--- 6. MCP Tools Layer Verification ---")
    search_res = vivareal_search_rentals(city="Timóteo", bedrooms=[2, 3, 4])
    print(f"MCP Search Tool returned: {search_res['returned_count']} items (total: {search_res['total_count']})")
    assert search_res["returned_count"] > 0, "MCP search tool should return items"

    loc_res = vivareal_suggest_locations("Timóteo")
    print(f"MCP Locations Tool returned: {len(loc_res)} locations")
    assert len(loc_res) > 0, "MCP locations tool should return suggestions"


def main() -> None:
    """Execute complete verification."""
    print("=" * 80)
    print("Starting Viva Real Research Verification Suite")
    print("=" * 80)

    try:
        sample_url = verify_target_search()
        verify_location_discovery()
        verify_property_details(sample_url)
        verify_pagination()
        verify_sorting()
        verify_mcp_tools()
        print("\n" + "=" * 80)
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (100%)")
        print("=" * 80)
    except Exception as e:
        print(f"\nVerification FAILED: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
