# Single Source of Truth (SSoT): Viva Real Glue API Specification

## 1. Service Endpoints & Protocols

### 1.1 Base Hosts
- **Primary Backend API**: `https://glue-api.vivareal.com`
- **Public Portal Web**: `https://www.vivareal.com.br`
- **Image CDN**: `https://resizedimgs.vivareal.com`

### 1.2 Protocol & Headers
```http
Host: glue-api.vivareal.com
x-domain: .vivareal.com.br
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7
```

---

## 2. API Operation Contracts

### 2.1 Operation: `SearchListings`
- **Method**: `GET`
- **Path**: `/v2/listings` (or `/v4/listings`)
- **Query Parameters**:
  - `portal`: Constant `"VIVAREAL"`
  - `categoryPage`: Constant `"RESULT"`
  - `business`: `"RENTAL"` or `"SALE"`
  - `addressLocationId`: Location string (e.g. `"BR>Minas Gerais>NULL>Timoteo"`)
  - `addressCity`: Municipality name (e.g. `"Timóteo"`)
  - `addressState`: State name (e.g. `"Minas Gerais"`)
  - `bedrooms`: Comma-separated integers (e.g. `"2,3,4"`)
  - `bathrooms`: Comma-separated integers
  - `parkingSpaces`: Comma-separated integers
  - `priceMin`: Integer BRL amount
  - `priceMax`: Integer BRL amount
  - `usableAreasMin`: Integer m² area
  - `usableAreasMax`: Integer m² area
  - `unitTypes`: Classification code (e.g. `"APARTMENT"`, `"HOME"`)
  - `unitTypesV3`: V3 classification code (e.g. `"APARTMENT"`, `"HOME"`)
  - `usageTypes`: `"RESIDENTIAL"` or `"COMMERCIAL"`
  - `unitSubTypes`: Comma-separated subtypes (e.g. `"UnitSubType_NONE,DUPLEX,LOFT..."`)
  - `sort`: `"MOST_RELEVANT"`, `"MOST_RECENT"`, `"LOWEST_PRICE"`, `"BIGGEST_PRICE"`, `"BIGGEST_AREA"`
  - `size`: Integer between `1` and `30` (strict maximum is 30)
  - `from`: Integer zero-based offset (`size * (page - 1)`)
  - `page`: Integer 1-indexed page indicator

#### Response Schema (JSON)
```json
{
  "search": {
    "totalCount": 2,
    "result": {
      "listings": [
        {
          "listing": {
            "id": "2900513774",
            "externalId": "0d017d",
            "title": null,
            "usableAreas": [211],
            "bedrooms": [4],
            "bathrooms": [3],
            "parkingSpaces": [2],
            "suites": [2],
            "pricingInfos": [
              {
                "businessType": "RENTAL",
                "price": 2800,
                "monthlyCondoFee": 0,
                "yearlyIptu": 600,
                "rentalInfo": {
                  "period": "MONTHLY",
                  "monthlyRentalTotalPrice": 2800,
                  "warranties": []
                }
              }
            ],
            "address": {
              "city": "Timóteo",
              "neighborhood": "Alphaville",
              "stateAcronym": "MG",
              "street": "Rua Elis Regina",
              "streetNumber": "",
              "zipCode": "35181611",
              "locationId": "BR>Minas Gerais>NULL>Timoteo>Barrios>Alphaville",
              "point": {
                "lat": -19.559862,
                "lon": -42.59119
              }
            },
            "amenities": ["BLINDEX_BOX", "BUILTIN_WARDROBE", "PETS_ALLOWED"]
          },
          "link": {
            "name": "Casa com 4 Quartos para alugar, 211m²",
            "href": "/imovel/casa-4-quartos-alphaville-bairros-timoteo-com-garagem-211m2-aluguel-RS2800-id-2900513774/"
          },
          "account": {
            "name": "Frederico Alves Zulato"
          },
          "medias": [
            {
              "type": "IMAGE",
              "url": "https://resizedimgs.vivareal.com/img/vr-listing/3aa200c10c6b666e3f7f3b02c4f5b764/casa-com-4-quartos-para-alugar-211m-no-alphaville-timoteo.webp?action=fit-in&dimension=614x297"
            }
          ]
        }
      ]
    }
  }
}
```

---

### 2.2 Operation: `SuggestLocations`
- **Method**: `GET`
- **Path**: `/v4/locations`
- **Query Parameters**:
  - `portal`: `"VIVAREAL"`
  - `q`: Search query string (e.g. `"Timóteo"`)
  - `size`: Integer suggestion limit (e.g. `10`)
  - `listingType`: `"USED"`
  - `businessType`: `"RENTAL"`
  - `fields`: `"neighborhood,city,street,zone"`
  - `includeFields`: `"address.neighborhood,address.city,address.state,address.zone,address.locationId,address.point"`

---

## 3. Error Codes & Boundary Matrix

| HTTP Status | Trigger Condition | API Error Payload / Behavior | Client Recovery Strategy |
| :--- | :--- | :--- | :--- |
| `400 Bad Request` | `size > 30` (e.g. `size=36`) | `{"err": "Size is above acceptable limit"}` | Cap `page_size <= 30`. |
| `400 Bad Request` | Repeated query parameters (`bedrooms=2&bedrooms=3`) | `{"err": "Unexpected response"}` | Use comma-separated list (`bedrooms=2,3`). |
| `403 Forbidden` | Missing browser headers or HTTP/2 TLS fingerprinting | Cloudflare Challenge HTML | Force HTTP/1.1 (`http2=False`) and desktop browser `User-Agent`. |
| `404 Not Found` | Requesting out-of-bounds page deep in index (`page=100`) | HTTP 404 status | Treat as end of result pagination stream. |
| `500 Internal Error` | Missing `x-domain` header or using `x-domain: www.vivareal.com.br` | `{"err": "error processing page"}` | Always include `x-domain: .vivareal.com.br` with leading dot. |
