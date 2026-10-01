"""Parsers package for Viva Real rental research."""

from vivareal_research.parsers.detail_parser import VivaRealDetailParser
from vivareal_research.parsers.location_parser import VivaRealLocationParser
from vivareal_research.parsers.search_parser import VivaRealSearchParser

__all__ = [
    "VivaRealDetailParser",
    "VivaRealLocationParser",
    "VivaRealSearchParser",
]
