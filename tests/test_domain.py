"""Unit tests for vivareal_research domain value objects and entities."""

import pytest
from vivareal_research.domain.criteria import (
    FilterSpecification,
    LocationSpecification,
    RentalSearchCriteria,
)
from vivareal_research.domain.enums import BusinessType, LocationCategory, PropertyType, SortOrder
from vivareal_research.domain.listing import (
    ListingAddress,
    ListingCollection,
    ListingFeatures,
    ListingPricing,
    ListingSummary,
)
from vivareal_research.domain.location import LocationCollection, LocationSuggestion
from vivareal_research.domain.property import PhotoGallery
from vivareal_research.domain.values import (
    AreaRange,
    LocationCoordinate,
    LocationIdentifier,
    PageRequest,
    PriceRange,
    RoomFilter,
)


def test_price_range_validation() -> None:
    """Test price range boundaries and validations."""
    pr = PriceRange(minimum_amount=1000, maximum_amount=2500)
    assert pr.has_filter() is True

    with pytest.raises(ValueError, match="negative"):
        PriceRange(minimum_amount=-50)

    with pytest.raises(ValueError, match="cannot exceed"):
        PriceRange(minimum_amount=3000, maximum_amount=1000)


def test_area_range_validation() -> None:
    """Test area range boundaries and validations."""
    ar = AreaRange(minimum_area=50, maximum_area=200)
    assert ar.has_filter() is True

    with pytest.raises(ValueError, match="negative"):
        AreaRange(minimum_area=-10)

    with pytest.raises(ValueError, match="cannot exceed"):
        AreaRange(minimum_area=300, maximum_area=100)


def test_room_filter_formatting() -> None:
    """Test room filter sanitization and query string formatting."""
    rf = RoomFilter.from_iterable([4, 2, 3, 2])
    assert rf.to_query_string() == "2,3,4"
    assert rf.is_empty() is False

    empty_rf = RoomFilter(())
    assert empty_rf.is_empty() is True
    assert empty_rf.to_query_string() == ""


def test_page_request_boundaries() -> None:
    """Test pagination validation and offset calculation."""
    p1 = PageRequest(page_number=1, page_size=30)
    assert p1.offset() == 0

    p2 = PageRequest(page_number=3, page_size=20)
    assert p2.offset() == 40

    with pytest.raises(ValueError, match="Page number"):
        PageRequest(page_number=0)

    with pytest.raises(ValueError, match="Page size"):
        PageRequest(page_number=1, page_size=35)


def test_target_criteria_defaults() -> None:
    """Verify target prompt criteria reproduction."""
    criteria = RentalSearchCriteria.for_timoteo_target_prompt()
    assert criteria.location.city == "Timóteo"
    assert criteria.location.state == "Minas Gerais"
    assert criteria.location.location_id.location_id == "BR>Minas Gerais>NULL>Timoteo"
    assert criteria.filters.business_type == BusinessType.RENTAL
    assert criteria.filters.bedrooms.to_query_string() == "2,3,4"


def test_listing_collection_behaviors() -> None:
    """Verify first-class collection behavior for listings."""
    item = ListingSummary(
        listing_id="12345",
        external_id="EXT1",
        title="Apartamento Teste",
        address=ListingAddress(neighborhood="Centro", city="Timóteo", state_acronym="MG"),
        pricing=ListingPricing(monthly_rent=1500, total_monthly=1650),
        features=ListingFeatures(usable_area=75, bedrooms=2, bathrooms=1),
        photos_count=5,
        canonical_url="/imovel/apartamento-12345/",
        advertiser_name="Imobiliaria XYZ",
    )
    collection = ListingCollection(listings=(item,), total_count=1)
    assert len(collection) == 1
    assert collection.is_empty() is False
    assert collection[0].listing_id == "12345"
    assert collection.first() == item


def test_photo_gallery_behaviors() -> None:
    """Verify PhotoGallery first-class collection behavior."""
    urls = [
        "https://resizedimgs.vivareal.com/img1.webp",
        "https://resizedimgs.vivareal.com/img2.webp",
    ]
    gallery = PhotoGallery.from_iterable(urls)
    assert len(gallery) == 2
    assert gallery.first() == urls[0]
    assert gallery[1] == urls[1]
    assert gallery.is_empty() is False


def test_location_collection_matching() -> None:
    """Verify location matching by city name."""
    s1 = LocationSuggestion(
        label="Timóteo",
        category=LocationCategory.CITY,
        location_id=LocationIdentifier("BR>Minas Gerais>NULL>Timoteo"),
        city="Timóteo",
        state="Minas Gerais",
    )
    s2 = LocationSuggestion(
        label="Centro, Timóteo",
        category=LocationCategory.NEIGHBORHOOD,
        location_id=LocationIdentifier("BR>Minas Gerais>NULL>Timoteo>Barrios>Centro"),
        city="Timóteo",
        state="Minas Gerais",
        neighborhood="Centro",
    )
    col = LocationCollection(items=(s1, s2))
    matched = col.find_city_match("timóteo")
    assert matched is not None
    assert matched.category == LocationCategory.CITY
