"""Domain exports for Viva Real rental research."""

from vivareal_research.domain.criteria import (
    FilterSpecification,
    LocationSpecification,
    RentalSearchCriteria,
)
from vivareal_research.domain.enums import (
    BusinessType,
    LocationCategory,
    PropertyType,
    SortOrder,
)
from vivareal_research.domain.listing import (
    ListingAddress,
    ListingCollection,
    ListingFeatures,
    ListingPricing,
    ListingSummary,
)
from vivareal_research.domain.location import (
    LocationCollection,
    LocationSuggestion,
)
from vivareal_research.domain.property import (
    AdvertiserContact,
    PhotoGallery,
    PropertyAmenities,
    PropertyDetail,
    PropertyDetailContent,
)
from vivareal_research.domain.values import (
    AreaRange,
    LocationCoordinate,
    LocationIdentifier,
    PageRequest,
    PriceRange,
    RoomFilter,
)

__all__ = [
    "AdvertiserContact",
    "AreaRange",
    "BusinessType",
    "FilterSpecification",
    "ListingAddress",
    "ListingCollection",
    "ListingFeatures",
    "ListingPricing",
    "ListingSummary",
    "LocationCategory",
    "LocationCollection",
    "LocationCoordinate",
    "LocationIdentifier",
    "LocationSpecification",
    "LocationSuggestion",
    "PageRequest",
    "PhotoGallery",
    "PriceRange",
    "PropertyAmenities",
    "PropertyDetail",
    "PropertyDetailContent",
    "PropertyType",
    "RentalSearchCriteria",
    "RoomFilter",
    "SortOrder",
]
