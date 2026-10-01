"""Search criteria and specification bundles for Viva Real rental research."""

from dataclasses import dataclass
from vivareal_research.domain.enums import BusinessType, PropertyType, SortOrder
from vivareal_research.domain.values import (
    AreaRange,
    LocationCoordinate,
    LocationIdentifier,
    PageRequest,
    PriceRange,
    RoomFilter,
)


@dataclass(frozen=True)
class LocationSpecification:
    """Location parameters bundled together."""

    location_id: LocationIdentifier
    city: str
    state: str = "Minas Gerais"
    coordinate: LocationCoordinate | None = None

    @classmethod
    def create_timoteo_default(cls) -> "LocationSpecification":
        """Factory creating canonical Timóteo location specification."""
        coord = LocationCoordinate(latitude=-19.582378, longitude=-42.644959)
        loc_id = LocationIdentifier("BR>Minas Gerais>NULL>Timoteo")
        return cls(location_id=loc_id, city="Timóteo", state="Minas Gerais", coordinate=coord)


@dataclass(frozen=True)
class FilterSpecification:
    """Filter parameters bundled together."""

    property_type: PropertyType = PropertyType.ALL
    bedrooms: RoomFilter = RoomFilter(())
    bathrooms: RoomFilter = RoomFilter(())
    parking_spaces: RoomFilter = RoomFilter(())
    price_range: PriceRange = PriceRange()
    area_range: AreaRange = AreaRange()
    sort_order: SortOrder = SortOrder.MOST_RELEVANT
    pagination: PageRequest = PageRequest()
    business_type: BusinessType = BusinessType.RENTAL


@dataclass(frozen=True)
class RentalSearchCriteria:
    """Unified rental search criteria adhering to 2 instance variables."""

    location: LocationSpecification
    filters: FilterSpecification = FilterSpecification()

    @classmethod
    def for_timoteo_target_prompt(cls) -> "RentalSearchCriteria":
        """Reproduce exact user prompt query: Timoteo rentals with 2, 3, 4 bedrooms."""
        loc = LocationSpecification.create_timoteo_default()
        filt = FilterSpecification(
            bedrooms=RoomFilter.from_iterable([2, 3, 4]),
            business_type=BusinessType.RENTAL,
        )
        return cls(location=loc, filters=filt)
