# Viva Real — Central Rental Research MCP Provider

Reverse-engineered rental search engine and API client for **Viva Real** (`https://www.vivareal.com.br`), owned by **Grupo OLX**.

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** server following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python, operating alongside sister providers like **Epifânio Imóveis** and **Casa Linhares**.

---

## 📚 Documentation

- **[Documentation Index](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/README.md)** (`docs/README.md`): Overview of all project documentation.
- **[Single Source of Truth (SSoT) API Spec](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/sot/vivareal_glue_api_spec.md)** (`docs/sot/vivareal_glue_api_spec.md`): Complete endpoint contracts, payload schemas, query parameters, and Glue API microservice architecture.
- **[ADR 0001: MCP Architecture & Design](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`): Hexagonal architecture, Object Calisthenics enforcement, and design patterns.
- **[API Reference](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/api_reference.md)** (`docs/api_reference.md`): Ready-to-use cURL recipes and parameter matrices.
- **[Reverse Engineering Analysis](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/api-research.md)** (`docs/api-research.md`): Reverse-engineering investigation notes, Glue API `/v2/listings` and `/v4/locations` specifications.
- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/README.md)** (`scripts/README.md`): Package layout and CLI runner guide.
- **[Architecture Standards](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/ARCHITECTURE.md)** (`scripts/ARCHITECTURE.md`): Calisthenics and SOLID compliance breakdown.
- **[Usage & MCP Integration](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/USAGE.md)** (`scripts/USAGE.md`): How to use the Python modules and integrate into MCP servers.
- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/research-plan.md)** (`scripts/research-plan.md`): Reverse-engineering methodology and probing execution log.

---

## ⚡ Quickstart

### Run Automated Tests (Unit & Live Integration)
```bash
.venv/bin/pytest -v
```

### Run Verification Suite
```bash
.venv/bin/python scripts/verify_research.py
```

### Search Rentals (Target Prompt Query)
```bash
.venv/bin/python scripts/run_search.py
```

### View Listing Details
```bash
.venv/bin/python scripts/run_property_detail.py
```

### Inspect Available Localities & Autocomplete
```bash
.venv/bin/python scripts/run_locations.py "Timóteo"
```

---

## 🏛️ Code Architecture & Standards Compliance

- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and polymorphic handlers.
- **Single Level of Indentation**: All methods adhere to at most 1 indent level.
- **Wrapped Primitives**: Domain concepts (`PriceRange`, `AreaRange`, `RoomFilter`, `PageRequest`, `LocationIdentifier`, `LocationCoordinate`) are immutable Value Objects.
- **First-Class Collections**: `ListingCollection`, `PhotoGallery`, and `LocationCollection` wrap collections without leaking raw mutable lists.
- **Size Limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines.
- **Instance Variables**: All classes hold at most 2 instance variables (composed via collaborator bundles `VivaRealGateway` and `VivaRealParserSuite`).
- **One Dot per Line**: Method chaining is eliminated in favor of explicit intermediate assignments.
- **Tell, Don't Ask**: Exposes domain behaviors and representations, not raw state.
