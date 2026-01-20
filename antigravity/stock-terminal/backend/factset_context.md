# FactSet MCP Schema & Context

This document contains the discovered schemas and usage patterns for the FactSet MCP tools. It is intended to help the agent understand how to correctly call these tools.

## Key Learnings & Patterns

### 1. Security Identifiers
-   **Always use the `-US` suffix** for US listings (e.g., `AAPL-US`, `MSFT-US`).
-   Pass identifiers as a **list of strings**, even for a single item (e.g., `ids=['AAPL-US']`).
-   Supported IDs: Tickers, CUSIP, SEDOL, ISIN, FactSet IDs.

### 2. Date Formats
-   **YYYY-MM-DD** is the strict format for `startDate` and `endDate`.
-   **YYYY** or **YYYY/FQ** (e.g., `2024/4F`) for `fiscalPeriodStart`/`End`.
-   **Relative Dates**: Use `relativeFiscalStart` (integer) for rolling periods (1 = next period).

### 3. Enumerations
-   Tools rely heavily on specific `data_type` enums to determine behavior.
-   **Always** specify `data_type`.

---

## Available Tools

### `FactSet_GlobalPrices`
*Retrieves end-of-day pricing, returns, corporate actions, and shares outstanding.*

-   **`data_type`** (Required):
    -   `prices`: OHLCV, VWAP, Turnover.
    -   `returns`: Total/Price/Dividend returns.
    -   `corporate_actions`: Dividends, splits, spinoffs.
    -   `shares_outstanding`: Historical share counts.
-   **`ids`**: List of tickers (e.g., `['AAPL-US']`).
-   **`startDate` / `endDate`**: Required for `prices` and `returns`.
-   **`frequency`**: `D` (Daily), `W` (Weekly), `M` (Monthly), `AQ` (Actual Quarterly), `AY` (Actual Yearly).
    -   *Note: Use `AQ` for quarterly price history requests.*
-   **`adjust`**: `SPLIT` (default), `UNSPLIT`.

### `FactSet_Fundamentals`
*Company-level financial statements and metrics.*

-   **`data_type`**: `fundamentals`.
-   **`ids`**: List of tickers.
-   **`metrics`**: List of FF codes. **CRITICAL**: Use specific codes like `FF_SALES`, `FF_EPS`, `FF_ASSETS`.
-   **`periodicity`**: `ANN` (Annual), `QTR` (Quarterly), `LTM` (Last 12 Months).

### `FactSet_EstimatesConsensus`
*Analyst consensus estimates and surprise data.*

-   **`data_type`**:
    -   `consensus_fixed`: Specific fiscal periods (requires `fiscalPeriodStart`).
    -   `consensus_rolling`: Relative periods (requires `relativeFiscalStart`).
    -   `surprise`: Beat/Miss analysis.
    -   `ratings`: Buy/Hold/Sell.
    -   `guidance`: Company guidance.
-   **`metrics`**: `SALES`, `EPS`, `EBITDA`, `PRICE_TGT`.
-   **`fiscalPeriodStart`**: Year (`2025`) or Quarter (`2025/1F`).

### `FactSet_Ownership`
*Institutional holders, fund holdings, and insider transactions.*

-   **`data_type`**:
    -   `fund_holdings`: What is inside a fund (e.g., `SPY-US` holdings).
    -   `security_holders`: Who owns a stock (e.g., who owns `AAPL-US`).
    -   `insider_transactions`: SEC filings.
-   **`ids`**: Tickers.
-   **`topn`**: Number of results (e.g., `10`, `25`).

### `FactSet_People`
*Professional profiles, jobs, and leadership.*

-   **`data_type`**:
    -   `profiles`: Individual bio (requires Person ID `XXXXXX-E`).
    -   `jobs`: Career history.
    -   `company_people`: Executives at a company.
    -   `company_positions`: Specific roles (e.g., `CEO`).
-   **`ids`**: Company ticker (for company_* types) or Person ID.

### `FactSet_CalendarEvents`
*Upcoming earnings, calls, and conferences.*

-   **`universeType`**: `Tickers`, `Index`.
-   **`eventTypes`**: `['Earnings', 'Conference', 'GuidanceCall']`.
-   **`symbols`**: List of tickers.
-   **`startDateTime` / `endDateTime`**: ISO 8601 timestamps (UTC).

### `FactSet_GeoRev`
*Revenue breakdown by geography.*

-   **`data_type`**:
    -   `countries`: Revenue by specific country.
    -   `regions`: Revenue by super-region/region.
-   **`ids`**: Tickers.
-   **`currency`**: ISO code (`USD`).

---

## Example Tool Calls

### Get Stock Price
```json
{
  "tool": "FactSet_GlobalPrices",
  "args": {
    "ids": ["AAPL-US"],
    "data_type": "prices",
    "startDate": "2024-01-01",
    "endDate": "2024-01-10",
    "frequency": "D"
  }
}
```

### Get Company financials (Sales & EPS)
```json
{
  "tool": "FactSet_Fundamentals",
  "args": {
    "ids": ["MSFT-US"],
    "data_type": "fundamentals",
    "metrics": ["FF_SALES", "FF_EPS"],
    "periodicity": "ANN"
  }
}
```

### Get Institutional Holders
```json
{
  "tool": "FactSet_Ownership",
  "args": {
    "ids": ["TSLA-US"],
    "data_type": "security_holders",
    "topn": "10"
  }
}
```

### Get Analyst Ratings
```json
{
  "tool": "FactSet_EstimatesConsensus",
  "args": {
    "ids": ["GOOGL-US"],
    "data_type": "ratings"
  }
}
```
