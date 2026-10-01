import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vivareal_research import VivaRealRentalClient


def main() -> None:
    """Query location autocomplete."""
    query = sys.argv[1] if len(sys.argv) > 1 else "Timóteo"
    client = VivaRealRentalClient()

    print("=" * 80)
    print(f"Viva Real Location Discovery: '{query}'")
    print("=" * 80)

    locations = client.suggest_locations(query, size=10)
    print(f"\nTotal Matching Locations: {len(locations)}\n")

    for i, loc in enumerate(locations, 1):
        coord_str = (
            f"({loc.coordinate.latitude}, {loc.coordinate.longitude})"
            if loc.coordinate
            else "N/A"
        )
        print(f"[{i}] {loc.label} [{loc.category.value.upper()}]")
        print(f"    LocationId: {loc.location_id.location_id}")
        print(f"    Hierarchy: {loc.display_full()}")
        print(f"    Coordinates: {coord_str}")
        print("-" * 80)


if __name__ == "__main__":
    main()
