# Architecture & Design Standards Compliance: Viva Real Research

## 1. Prioritization Hierarchy

Development strictly adhered to the priority order specified in user guidance:
1. **Correctness First**: Real HTTP requests, complete parameter encoding, verified pagination bounds, resilient detail extraction, live test validation.
2. **Modularity Second**: Hexagonal Ports & Adapters, decoupled domain models, URL builder, abstract HTTP gateway, specialized parsers, client facade.
3. **Style Principles Third**: SOLID, Clean Code, Object Calisthenics, Design Patterns.

---

## 2. SOLID Principles Enforcement

- **Single Responsibility Principle (SRP)**:
  - `VivaRealUrlBuilder`: Solely responsible for turning domain criteria into HTTP query strings and SEO URLs.
  - `VivaRealSearchParser`: Solely responsible for mapping Glue API `/v2/listings` JSON payloads into domain models.
  - `VivaRealDetailParser`: Solely responsible for parsing Schema.org `Product` JSON-LD microdata from HTML markup.
  - `VivaRealLocationParser`: Solely responsible for parsing Glue API `/v4/locations` payloads into location collections.
- **Open/Closed Principle (OCP)**:
  - Extensible via `HttpClientProtocol` and `RentalProviderProtocol`. Alternative transports (e.g. caching proxies, mock test clients) can be injected without touching client logic.
- **Liskov Substitution Principle (LSP)**:
  - `MockHttpClient` is a drop-in replacement for `HttpxHttpClient` across all tests.
- **Interface Segregation Principle (ISP)**:
  - Segregated capability protocols: `RentalSearchCapability`, `RentalDetailCapability`, `RentalLocationsCapability`.
- **Dependency Inversion Principle (DIP)**:
  - High-level client (`VivaRealRentalClient`) depends on abstractions (`HttpClientProtocol`) injected via collaborator bundles.

---

## 3. Object Calisthenics Compliance

1. **Only One Level of Indentation per Method**:
   Methods use early returns, guard clauses, and helper extractions to ensure flat control flow.
2. **Don't Use the `else` Keyword**:
   No `else` keyword exists anywhere in the codebase.
3. **Wrap All Primitives and Strings**:
   - `PriceRange`, `AreaRange`, `RoomFilter`, `PageRequest`, `LocationIdentifier`, `LocationCoordinate`.
4. **First-Class Collections**:
   - `ListingCollection`, `PhotoGallery`, `LocationCollection` wrap list/tuple primitives and expose domain methods (`first()`, `is_empty()`, `find_city_match()`).
5. **One Dot per Line**:
   No deep chained method calls; intermediate variables are assigned locally.
6. **Don't Abbreviate**:
   Names are expressive and unambiguous (`criteria`, `pagination`, `neighborhood`, `parking_spaces`).
7. **Keep Entities Small**:
   - Functions $\le 15$ lines.
   - Classes $\le 100$ lines.
   - Modules $< 200$ lines.
8. **No Classes with More Than 2 Instance Variables**:
   Collaborator bundles (`VivaRealGateway` and `VivaRealParserSuite`) group dependencies into pairs so classes never exceed 2 fields.
9. **No Public Getters or Setters (Tell, Don't Ask)**:
   Value objects and entities expose behavior and representations, not mutable state.
