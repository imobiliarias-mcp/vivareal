"""Interfaces package for rental research MCP."""

from scripts.interfaces.provider import (
    RentalDetailCapability,
    RentalLocationsCapability,
    RentalProviderProtocol,
    RentalSearchCapability,
)

__all__ = [
    "RentalDetailCapability",
    "RentalLocationsCapability",
    "RentalProviderProtocol",
    "RentalSearchCapability",
]
