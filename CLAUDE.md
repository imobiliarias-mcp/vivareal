# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands & Development Workflows

The project uses Python >=3.11 with virtual environment managed at `.venv/` via `uv`.

### Testing
- Run all tests (unit + integration): `.venv/bin/pytest -v` (or `.venv/bin/python scripts/run_tests.py`)
- Run a single test file: `.venv/bin/pytest tests/test_client.py -v`
- Run a single test function: `.venv/bin/pytest tests/test_client.py -k test_client_search_rentals_with_mock -v`
- Run live integration tests only: `.venv/bin/pytest tests/test_live_integration.py -v`
- Run research verification suite: `.venv/bin/python scripts/verify_research.py`

### CLI Runners
- Rental search execution: `.venv/bin/python scripts/run_search.py`
- Property detail lookup: `.venv/bin/python scripts/run_property_detail.py`
- Location autocomplete discovery: `.venv/bin/python scripts/run_locations.py "Timóteo"`

---

## High-Level Architecture & System Design

The repository implements a reverse-engineered client for the Viva Real (Grupo OLX) portal (`https://www.vivareal.com.br`), structured as an adapter for a Central Rental Research Model Context Protocol (MCP) server alongside sister providers (e.g., Epifânio Imóveis, Casa Linhares).

```
vivareal/
├── src/vivareal_research/            # Core library package
│   ├── domain/                       # Pure domain models (Value Objects, Entities, Collections, Enums)
│   ├── infrastructure/               # HTTP client protocol & implementation, URL builders
│   ├── parsers/                      # Search API, Location API, and JSON-LD Detail parsers
│   ├── collaborators.py              # Gateway & Parser collaborator bundles (Calisthenics <= 2 fields)
│   └── client.py                     # VivaRealRentalClient high-level facade
├── scripts/
│   ├── interfaces/provider.py        # RentalProviderProtocol interface for Central MCP
│   ├── providers/vivareal.py         # VivaRealRentalProvider adapter
│   ├── mcp/tools.py                  # MCP tool declarations (search, detail, locations)
│   └── run_*.py                      # Standalone CLI tools & verify_research.py
└── tests/                            # Unit tests & live integration tests
```

### Core Architecture Layers

1. **Domain Layer (`src/vivareal_research/domain/`)**:
   - **Value Objects**: `PriceRange`, `AreaRange`, `RoomFilter`, `PageRequest`, `LocationIdentifier`, `LocationCoordinate`. All validate at initialization and encapsulate representations.
   - **First-Class Collections**: `ListingCollection`, `PhotoGallery`, `LocationCollection` wrap list primitives and expose domain methods (`first()`, `is_empty()`, `find_city_match()`).
   - **Entities**: `Listing` (with nested `ListingPricing`, `ListingFeatures`, `ListingAddress`), `PropertyDetail`, `LocationSuggestion`.
   - **Criteria**: `RentalSearchCriteria` composed of `LocationSpecification` and `FilterSpecification`.

2. **Infrastructure Layer (`src/vivareal_research/infrastructure/`)**:
   - `HttpClientProtocol`: Abstraction for network transport to enable deterministic mocking.
   - `HttpxHttpClient`: Implements HTTP/1.1 transport (`http2=False` to prevent Cloudflare challenges), sets browser headers, and attaches the mandatory `x-domain: .vivareal.com.br` header.
   - `VivaRealUrlBuilder`: Builds Glue API query strings (`/v2/listings`, `/v4/locations`) and canonical web search URLs (`https://www.vivareal.com.br/aluguel/...`).

3. **Parsers Layer (`src/vivareal_research/parsers/`)**:
   - `VivaRealSearchParser`: Parses Glue API `/v2/listings` JSON into `ListingCollection`.
   - `VivaRealLocationParser`: Parses Glue API `/v4/locations` JSON into `LocationCollection`.
   - `VivaRealDetailParser`: Parses Schema.org `Product` JSON-LD microdata from public property HTML pages into `PropertyDetail`.

4. **Client & Collaborator Bundles (`src/vivareal_research/client.py`, `collaborators.py`)**:
   - `VivaRealGateway`: Groups `HttpClientProtocol` and `VivaRealUrlBuilder`.
   - `VivaRealParserSuite`: Groups `VivaRealSearchParser`, `VivaRealDetailParser`, and `VivaRealLocationParser`.
   - `VivaRealRentalClient`: Exposes `search_rentals()`, `suggest_locations()`, and `get_property_detail()`.

5. **MCP Integration Layer (`scripts/`)**:
   - `RentalProviderProtocol` (`scripts/interfaces/provider.py`): Interface for all rental providers in the ecosystem.
   - `VivaRealRentalProvider` (`scripts/providers/vivareal.py`): Concrete adapter implementing `RentalProviderProtocol`.
   - `scripts/mcp/tools.py`: Tool functions (`vivareal_search_rentals`, `vivareal_get_property_detail`, `vivareal_suggest_locations`) ready for MCP registration.

---

## Critical Glue API Protocol Rules & Quirks

When interacting with or extending Viva Real's reverse-engineered endpoints:

- **Host**: `https://glue-api.vivareal.com`
- **Mandatory Header**: `x-domain: .vivareal.com.br` (leading dot is required; requests fail without it).
- **HTTP Transport**: Force HTTP/1.1 (`http2=False` in `httpx.Client`). HTTP/2 triggers Cloudflare bot challenges.
- **Pagination Boundary**: Maximum page size is **30** (`size <= 30`). Setting `size > 30` returns HTTP 400 Bad Request. Offset is governed by `from={offset}` (`offset = (page - 1) * size`).
- **Room Filter Encoding**: Comma-separated query values (`bedrooms=2,3,4`). Repeating the query parameter (`bedrooms=2&bedrooms=3`) returns HTTP 400 Bad Request.
- **Authentication**: None required. Listing searches and detail page microdata are publicly accessible.

---

## Code Quality & Calisthenics Standards

All code in this repository strictly enforces:
- **No `else` keyword**: Use guard clauses, early returns, or polymorphism.
- **One indentation level per method**: Extract nested control flow into private helper methods.
- **Wrapped primitives**: Wrap domain concepts in immutable Value Objects.
- **First-class collections**: Never leak raw lists or mutate collection state externally.
- **Small entity sizes**: Functions <= 15 lines, Classes <= 100 lines, Modules < 200 lines.
- **Instance variables limit**: Maximum 2 fields per class (use collaborator bundles like `VivaRealGateway`).
- **One dot per line**: Avoid deep method chaining; assign intermediate variables locally.
- **No abbreviations**: Use full descriptive names (`criteria`, `pagination`, `neighborhood`).
- **Tell, don't ask**: Expose domain behavior and representations rather than public getters/setters.

---

## Git Workflow

- **Default Forge**: Gitea. Use `tea` CLI (never `gh`).
- **Default Branch**: `main`.
- **Merge Policy**: Never open PRs. Merge worktrees directly into `main`.
- **Periodic Sync**: Fetch and rebase against `origin/main` before starting tasks, mid-session, and before merging (`git fetch origin && git rebase origin/main`).

---

## Documentation Pointers

- **Documentation Index**: `docs/README.md`
- **Glue API Specification (SSoT)**: `docs/sot/vivareal_glue_api_spec.md`
- **Architecture Decision Record**: `docs/adr/0001-rental-search-mcp-module-design.md`
- **Reverse Engineering Analysis**: `docs/api-research.md`
- **API Reference & cURL Recipes**: `docs/api_reference.md`
- **Package & Scripts Guide**: `scripts/README.md`
- **Calisthenics & Architecture Compliance**: `scripts/ARCHITECTURE.md`
- **Usage & MCP Integration**: `scripts/USAGE.md`
- **Research Plan & Verification Log**: `scripts/research-plan.md`
