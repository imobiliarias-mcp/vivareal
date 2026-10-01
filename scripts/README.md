# Central Rental Research MCP — Viva Real Module

This package implements the **Viva Real** (`https://www.vivareal.com.br`) rental search provider, designed as a modular adapter for the **Central Rental Research MCP (Model Context Protocol)** server.

---

## 1. Architectural Highlights

- **SOLID Principles**: Single responsibility classes, interface segregation, dependency inversion.
- **Strict Object Calisthenics**:
  - One indent level per method.
  - Zero `else` keywords (guard clauses and early returns only).
  - Wrapped primitives (Value Objects for prices, areas, room filters, page requests, coordinates).
  - First-class collections (`ListingCollection`, `PhotoGallery`, `LocationCollection`).
  - One dot per line (intermediate assigned variables).
  - No abbreviations.
  - Entity size limits: functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines.
  - ≤ 2 instance variables per class (collaborator bundles).
  - Tell, Don't Ask encapsulation.
- **Design Patterns**: Adapter, Strategy, Builder, Value Object, First-Class Collection, Factory.
- **Fail Fast**: Immediate boundary validation on inputs, raising descriptive typed domain exceptions.

---

## 2. Directory Layout

```
scripts/
├── README.md               # Package overview and developer instructions
├── ARCHITECTURE.md         # Calisthenics & SOLID design adherence documentation
├── USAGE.md                # Usage examples and MCP integration guide
├── research-plan.md        # Comprehensive reverse-engineering research plan & logs
├── verify_research.py      # Standalone verification runner
├── interfaces/             # Port contracts (MCP Provider Protocols)
│   ├── __init__.py
│   └── provider.py         # RentalProviderProtocol interface
├── providers/              # Adapter layer
│   ├── __init__.py
│   └── vivareal.py         # VivaRealRentalProvider implementation
├── mcp/                    # MCP tool contracts & handlers
│   ├── __init__.py
│   └── tools.py            # Central Rental Research MCP tools
├── run_search.py           # CLI tool to run rental searches
├── run_property_detail.py  # CLI tool to fetch full property details
└── run_locations.py        # CLI tool to discover locations & autocomplete
```

---

## 3. CLI Utilities Execution

```bash
# Run verification suite (all checks: search, autocomplete, detail, pagination, sort, MCP tools)
.venv/bin/python scripts/verify_research.py

# Run rental search matching target prompt
.venv/bin/python scripts/run_search.py

# Run location discovery
.venv/bin/python scripts/run_locations.py "Timóteo"

# Run property detail retrieval
.venv/bin/python scripts/run_property_detail.py
```
