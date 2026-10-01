import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vivareal_research import VivaRealRentalClient


def main() -> None:
    """Fetch and display property details."""
    target_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/"
    )

    client = VivaRealRentalClient()
    print("=" * 80)
    print("Viva Real Property Detail Flow")
    print(f"Target URL: {target_url}")
    print("=" * 80)

    detail = client.get_property_detail(target_url)
    print(f"\nTitle: {detail.title()}")
    print(f"Listing ID (SKU): {detail.summary.listing_id}")
    print(f"Monthly Rent: R$ {detail.summary.pricing.monthly_rent:,}")
    print(f"Total Photos: {len(detail.gallery())}")

    print("\nPhoto Gallery Sample:")
    for i, photo_url in enumerate(detail.gallery()[:5], 1):
        print(f"  [{i}] {photo_url}")

    print("\nDescription:")
    print(detail.description().strip())
    print("=" * 80)


if __name__ == "__main__":
    main()
