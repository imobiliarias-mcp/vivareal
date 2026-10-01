"""Domain enumerations for Viva Real rental search."""

from enum import Enum


class BusinessType(str, Enum):
    """Transaction purpose type."""

    RENTAL = "RENTAL"
    SALE = "SALE"


class PropertyType(str, Enum):
    """Property category matching Viva Real unitTypeV3 taxonomy."""

    ALL = "ALL"
    APARTMENT = "APARTMENT"
    HOME = "HOME"
    CONDOMINIUM_HOME = "CONDOMINIUM"
    PENTHOUSE = "PENTHOUSE"
    FLAT = "FLAT"
    KITNET = "KITNET"
    ALLOTMENT_LAND = "RESIDENTIAL_ALLOTMENT_LAND"
    TWO_STORY_HOUSE = "TWO_STORY_HOUSE"
    COMMERCIAL_BUILDING = "COMMERCIAL_BUILDING"
    COMMERCIAL_PROPERTY = "COMMERCIAL_PROPERTY"
    OFFICE = "OFFICE"
    SHED = "SHED_DEPOSIT_WAREHOUSE"


class SortOrder(str, Enum):
    """Listing ordering criteria supported by Glue API."""

    MOST_RELEVANT = "MOST_RELEVANT"
    MOST_RECENT = "MOST_RECENT"
    LOWEST_PRICE = "LOWEST_PRICE"
    BIGGEST_PRICE = "BIGGEST_PRICE"
    BIGGEST_AREA = "BIGGEST_AREA"


class LocationCategory(str, Enum):
    """Category classification of geographical locations."""

    CITY = "city"
    NEIGHBORHOOD = "neighborhood"
    STREET = "street"
    ZONE = "zone"
