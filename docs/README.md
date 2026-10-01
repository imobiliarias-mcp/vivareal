# Viva Real — Rental API Reverse Engineering Documentation

Welcome to the reverse-engineering and architecture documentation for **Viva Real** (`https://www.vivareal.com.br`), part of **Grupo OLX**.

This repository contains the reverse-engineered API specifications, architectural decision records, and clean, modular Python components designed for integration into a **Central Rental Research MCP (Model Context Protocol)** server.

---

## Documentation Structure

- **[Reverse Engineering Analysis](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/api-research.md)** (`docs/api-research.md`):
  Primary research notes, Glue API endpoints, routing mechanics, JSON-LD microdata structure, and parameter encoding conventions.

- **[Single Source of Truth API Specification](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/sot/vivareal_glue_api_spec.md)** (`docs/sot/vivareal_glue_api_spec.md`):
  Comprehensive contract specification for all endpoints, headers, payload schemas, query matrices, and URL rewriting rules.

- **[Architecture Decision Record 0001](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/adr/0001-rental-search-mcp-module-design.md)** (`docs/adr/0001-rental-search-mcp-module-design.md`):
  Detailed rationale on Ports-and-Adapters (Hexagonal) architecture, SOLID principles, Design Patterns, and strict Object Calisthenics enforcement.

- **[API Reference & Quick Recipes](file:///home/samuelcaldas/repos/imobiliarias/vivareal/docs/api_reference.md)** (`docs/api_reference.md`):
  Developer reference featuring ready-to-run `curl` commands, parameter dictionaries, and implementation recipes.

- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/research-plan.md)** (`scripts/research-plan.md`):
  Full executive summary, discovery log, verification results, and central MCP integration guide.

- **[Scripts & MCP Module Guide](file:///home/samuelcaldas/repos/imobiliarias/vivareal/scripts/README.md)** (`scripts/README.md`):
  Developer guide for running the Python modules, CLI utilities, and MCP tool handlers.

---

## Key Technical Discoveries Summary

| Dimension | Discovery |
| :--- | :--- |
| **Underlying Platform** | Next.js App Router (SSR + RSC) backed by Grupo OLX **Glue API** |
| **Backend Services** | `https://glue-api.vivareal.com` (Listings & Locations), `https://resizedimgs.vivareal.com` (Images) |
| **Mandatory Header** | `x-domain: .vivareal.com.br` (Leading dot required) |
| **Transport Protocol** | Force HTTP/1.1 (`http2=False`) with browser User-Agent to bypass Cloudflare challenges |
| **Rental Search Route** | `GET /v2/listings` and `GET /v4/listings` |
| **Room Parameter Encoding** | `bedrooms=2,3,4` (comma-separated; repeated parameters fail with HTTP 400) |
| **Location Discovery** | `GET /v4/locations?portal=VIVAREAL&q={city}&businessType=RENTAL` |
| **Pagination Model** | 1 to 30 listings per page via `size={N}` (maximum **30**; `size > 30` fails with HTTP 400) and `from={offset}` |
| **Property Detail Endpoint** | Direct URL `/imovel/{slug}/` (JSON-LD Product) & embedded payload in search results |
| **Sorting Options** | `MOST_RELEVANT`, `MOST_RECENT`, `LOWEST_PRICE`, `BIGGEST_PRICE`, `BIGGEST_AREA` |
| **Authentication Requirement** | **None** (All listing searches and detail views are publicly accessible) |
