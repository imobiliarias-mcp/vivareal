"""Property detail models and photo galleries."""

from dataclasses import dataclass
from typing import Iterator, Sequence
from vivareal_research.domain.listing import ListingSummary


@dataclass(frozen=True)
class PhotoGallery:
    """First-class collection wrapping property photo URLs."""

    image_urls: tuple[str, ...]

    @classmethod
    def from_iterable(cls, urls: Sequence[str]) -> "PhotoGallery":
        """Factory constructing gallery from url list."""
        return cls(image_urls=tuple(urls))

    def __len__(self) -> int:
        """Return total number of photos."""
        return len(self.image_urls)

    def __iter__(self) -> Iterator[str]:
        """Iterate over photo URLs."""
        return iter(self.image_urls)

    def __getitem__(self, index: int) -> str:
        """Access photo URL by index."""
        return self.image_urls[index]

    def first(self) -> str | None:
        """Return primary photo URL."""
        if len(self.image_urls) == 0:
            return None
        return self.image_urls[0]

    def is_empty(self) -> bool:
        """Return True if gallery has no photos."""
        return len(self.image_urls) == 0


@dataclass(frozen=True)
class PropertyAmenities:
    """First-class collection wrapping property amenity identifiers."""

    amenities: tuple[str, ...]

    def __len__(self) -> int:
        """Return number of amenities."""
        return len(self.amenities)

    def __iter__(self) -> Iterator[str]:
        """Iterate over amenities."""
        return iter(self.amenities)

    def contains(self, amenity: str) -> bool:
        """Check if amenity code is present."""
        return amenity.upper() in (a.upper() for a in self.amenities)


@dataclass(frozen=True)
class AdvertiserContact:
    """Advertiser contact bundle."""

    name: str
    phone: str = ""
    whatsapp: str = ""
    profile_url: str = ""


@dataclass(frozen=True)
class PropertyDetailContent:
    """Bundles descriptive content, amenities and media."""

    description: str
    amenities: PropertyAmenities
    gallery: PhotoGallery
    contact: AdvertiserContact


@dataclass(frozen=True)
class PropertyDetail:
    """Complete detail representation of a property listing."""

    summary: ListingSummary
    content: PropertyDetailContent

    def title(self) -> str:
        """Return property title."""
        return self.summary.title

    def description(self) -> str:
        """Return property description."""
        return self.content.description

    def gallery(self) -> PhotoGallery:
        """Return property photos."""
        return self.content.gallery

    def amenities(self) -> PropertyAmenities:
        """Return property amenities."""
        return self.content.amenities
