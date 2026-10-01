import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vivareal_research import RentalSearchCriteria, VivaRealRentalClient


def main() -> None:
    """Run rental search and display results."""
    client = VivaRealRentalClient()
    criteria = RentalSearchCriteria.for_timoteo_target_prompt()

    web_url = client.build_canonical_web_url(criteria)
    print("=" * 80)
    print("Viva Real Rental Search Flow")
    print(f"Target URL: {web_url}")
    print("=" * 80)

    results = client.search_rentals(criteria)
    print(f"\nTotal Listings Found: {results.total_count}")
    print(f"Results on Page: {len(results)}\n")

    for i, item in enumerate(results, 1):
        f = item.features
        p = item.pricing
        a = item.address
        print(f"[{i}] Listing ID: {item.listing_id} (Ref: {item.external_id})")
        print(f"    Title: {item.title}")
        print(f"    Rent: R$ {p.monthly_rent:,} | Condo: R$ {p.monthly_condo:,} | Total: R$ {p.total_monthly:,}/mês")
        print(f"    Features: {f.bedrooms} dorms, {f.bathrooms} banheiros, {f.parking_spaces} vagas, {f.usable_area} m²")
        print(f"    Location: {a.street}, {a.neighborhood}, {a.city} - {a.state_acronym}")
        print(f"    Photos: {item.photos_count} images")
        print(f"    URL: {item.canonical_url}")
        print("-" * 80)


if __name__ == "__main__":
    main()
