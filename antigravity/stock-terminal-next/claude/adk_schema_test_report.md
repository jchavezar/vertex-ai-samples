# ADK + LLM + Schema Integration Test Report

**Generated:** 2026-01-27 01:37:29

## Test Configuration
- **Schema File:** `mcp_tools_schema.json`
- **LLM:** Gemini 2.0 Flash
- **Test Type:** Natural language query -> LLM interpretation -> MCP tool call

## Summary

| Metric | Value |
|--------|-------|
| Total Queries | 41 |
| OK | 39 (95.1%) |
| NO OK | 2 (4.9%) |
| Correct Tool Selection | 40/41 (97.6%) |
| Avg Latency | 2862ms |

## Results by Tool

| Tool | OK | NO OK | Correct Selection |
|------|-----|-------|-------------------|
| FactSet_Fundamentals | 5 | 0 | 5/5 |
| FactSet_EstimatesConsensus | 5 | 0 | 5/5 |
| FactSet_GlobalPrices | 5 | 0 | 5/5 |
| FactSet_Ownership | 4 | 1 | 5/5 |
| FactSet_MergersAcquisitions | 3 | 1 | 3/4 |
| FactSet_People | 5 | 0 | 5/5 |
| FactSet_CalendarEvents | 3 | 0 | 3/3 |
| FactSet_GeoRev | 3 | 0 | 3/3 |
| FactSet_SupplyChain | 4 | 0 | 4/4 |
| FactSet_Metrics | 2 | 0 | 2/2 |

## Detailed Results

### Query 1

**Query:** How much short-term and long-term debt does GE carry?

**Expected Tool:** `FactSet_Fundamentals`

**Tool Called:** `FactSet_Fundamentals`

**Arguments:**
```json
{
  "ids": [
    "GE-US"
  ],
  "data_type": "fundamentals",
  "metrics": [
    "FF_DEBT_ST",
    "FF_DEBT_LT"
  ]
}
```

**Status:** OK - Success

**Latency:** 3147ms

---

### Query 2

**Query:** Is Netflix's current P/E above or below their 5-year average?

**Expected Tool:** `FactSet_Fundamentals`

**Tool Called:** `FactSet_Fundamentals`

**Arguments:**
```json
{
  "ids": [
    "NFLX-US"
  ],
  "data_type": "fundamentals",
  "metrics": [
    "FF_PE"
  ],
  "periodicity": "ANN"
}
```

**Status:** OK - Success

**Latency:** 1647ms

---

### Query 3

**Query:** How does Tesla's current net margin compare to General Motors and Ford?

**Expected Tool:** `FactSet_Fundamentals`

**Tool Called:** `FactSet_Fundamentals`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US",
    "GM-US",
    "F-US"
  ],
  "data_type": "fundamentals",
  "metrics": [
    "FF_NET_MGN"
  ],
  "periodicity": "LTM"
}
```

**Status:** OK - Success

**Latency:** 2021ms

---

### Query 4

**Query:** Compare the gross margins and ROIC trends for Amazon, Google, and Meta over the past 5 years

**Expected Tool:** `FactSet_Fundamentals`

**Tool Called:** `FactSet_Fundamentals`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US",
    "GOOGL-US",
    "META-US"
  ],
  "data_type": "fundamentals",
  "metrics": [
    "FF_GROSS_MGN",
    "FF_ROIC"
  ],
  "fiscalPeriodStart": "2019-01-01",
  "fiscalPeriodEnd": "2023-12-31",
  "periodicity": "ANN"
}
```

**Status:** OK - Success

**Latency:** 2213ms

---

### Query 5

**Query:** What is AMZN's free cash flow for Q1 2024 and how does it compare to Q1 2023?

**Expected Tool:** `FactSet_Fundamentals`

**Tool Called:** `FactSet_Fundamentals`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US"
  ],
  "data_type": "fundamentals",
  "metrics": [
    "FF_FREE_CF"
  ],
  "periodicity": "QTR",
  "fiscalPeriodStart": "2023-01-01",
  "fiscalPeriodEnd": "2024-03-31"
}
```

**Status:** OK - Success

**Latency:** 1983ms

---

### Query 6

**Query:** How did the 2025 consensus target price for Amazon change between October and December 2024?

**Expected Tool:** `FactSet_EstimatesConsensus`

**Tool Called:** `FactSet_EstimatesConsensus`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US"
  ],
  "estimate_type": "consensus_fixed",
  "metrics": [
    "PRICE_TGT"
  ],
  "fiscalPeriodStart": "2025",
  "fiscalPeriodEnd": "2025",
  "startDate": "2024-10-01",
  "endDate": "2024-12-31",
  "frequency": "AM"
}
```

**Status:** OK - Success

**Latency:** 2229ms

---

### Query 7

**Query:** How have next fiscal year EPS estimates for Apple evolved over the past 12 months?

**Expected Tool:** `FactSet_EstimatesConsensus`

**Tool Called:** `FactSet_EstimatesConsensus`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "estimate_type": "consensus_rolling",
  "metrics": [
    "EPS"
  ],
  "relativeFiscalStart": 1,
  "relativeFiscalEnd": 1,
  "startDate": "2023-11-08",
  "endDate": "2024-11-08",
  "frequency": "AM"
}
```

**Status:** OK - Success

**Latency:** 2057ms

---

### Query 8

**Query:** How consistent are long-term growth estimates (FY2-FY3) for Nvidia's sales?

**Expected Tool:** `FactSet_EstimatesConsensus`

**Tool Called:** `FactSet_EstimatesConsensus`

**Arguments:**
```json
{
  "ids": [
    "NVDA-US"
  ],
  "estimate_type": "consensus_fixed",
  "metrics": [
    "SALES"
  ],
  "fiscalPeriodStart": "2026",
  "fiscalPeriodEnd": "2027",
  "frequency": "AY"
}
```

**Status:** OK - Success

**Latency:** 2038ms

---

### Query 9

**Query:** How often does Tesla beat earnings estimates? Show me their surprise pattern over the last 2 years.

**Expected Tool:** `FactSet_EstimatesConsensus`

**Tool Called:** `FactSet_EstimatesConsensus`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US"
  ],
  "estimate_type": "surprise",
  "metrics": [
    "EPS"
  ],
  "startDate": "2022-06-05",
  "endDate": "2024-06-05",
  "frequency": "AQ"
}
```

**Status:** OK - Success

**Latency:** 1957ms

---

### Query 10

**Query:** What is the current analyst consensus rating for Apple? How many analysts rate it Buy vs Hold vs Sell?

**Expected Tool:** `FactSet_EstimatesConsensus`

**Tool Called:** `FactSet_EstimatesConsensus`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "estimate_type": "ratings"
}
```

**Status:** OK - Success

**Latency:** 1602ms

---

### Query 11

**Query:** Show the week-over-week change in closing prices for Oracle in Q1 2024

**Expected Tool:** `FactSet_GlobalPrices`

**Tool Called:** `FactSet_GlobalPrices`

**Arguments:**
```json
{
  "ids": [
    "ORCL-US"
  ],
  "data_type": "prices",
  "startDate": "2024-01-01",
  "endDate": "2024-03-31",
  "frequency": "W"
}
```

**Status:** OK - Success

**Latency:** 1882ms

---

### Query 12

**Query:** Which days in the past month had the highest trading volume for Amazon?

**Expected Tool:** `FactSet_GlobalPrices`

**Tool Called:** `FactSet_GlobalPrices`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US"
  ],
  "data_type": "prices",
  "startDate": "2024-01-27",
  "endDate": "2024-02-27",
  "frequency": "D"
}
```

**Status:** OK - Success

**Latency:** 1820ms

---

### Query 13

**Query:** Show all gap ups greater than 2% for TSLA stock price in the last quarter

**Expected Tool:** `FactSet_GlobalPrices`

**Tool Called:** `FactSet_GlobalPrices`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US"
  ],
  "data_type": "prices",
  "startDate": "2024-04-01",
  "endDate": "2024-06-30",
  "frequency": "D"
}
```

**Status:** OK - Success

**Latency:** 1840ms

---

### Query 14

**Query:** Compare the dividend payment frequencies between Johnson & Johnson, Procter & Gamble, and Unilever over the past two years

**Expected Tool:** `FactSet_GlobalPrices`

**Tool Called:** `FactSet_GlobalPrices`

**Arguments:**
```json
{
  "ids": [
    "JNJ-US",
    "PG-US",
    "ULVR-GB"
  ],
  "data_type": "annualized_dividends",
  "startDate": "2022-07-26",
  "endDate": "2024-07-26",
  "frequency": "AY"
}
```

**Status:** OK - Success

**Latency:** 1996ms

---

### Query 15

**Query:** Calculate the rolling 12-month return correlation between Netflix and Disney over the past 3 years

**Expected Tool:** `FactSet_GlobalPrices`

**Tool Called:** `FactSet_GlobalPrices`

**Arguments:**
```json
{
  "ids": [
    "NFLX-US",
    "DIS-US"
  ],
  "data_type": "returns",
  "startDate": "2021-05-15",
  "endDate": "2024-05-15",
  "frequency": "M"
}
```

**Status:** OK - Success

**Latency:** 2265ms

---

### Query 16

**Query:** Show me all Apple holdings across the top 5 largest mutual funds

**Expected Tool:** `FactSet_Ownership`

**Tool Called:** `FactSet_Ownership`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "data_type": "security_holders",
  "topn": "5",
  "holderType": "M"
}
```

**Status:** OK - Success

**Latency:** 1611ms

---

### Query 17

**Query:** Who are the top 10 institutional holders of Apple stock?

**Expected Tool:** `FactSet_Ownership`

**Tool Called:** `FactSet_Ownership`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "data_type": "security_holders",
  "topn": "10",
  "holderType": "F"
}
```

**Status:** OK - Success

**Latency:** 1770ms

---

### Query 18

**Query:** Compare insider buying vs selling activity for Tesla over the past year

**Expected Tool:** `FactSet_Ownership`

**Tool Called:** `FactSet_Ownership`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US"
  ],
  "data_type": "insider_transactions",
  "startDate": "2023-08-23",
  "endDate": "2024-08-23",
  "transactionType": "PS"
}
```

**Status:** OK - Success

**Latency:** 2292ms

---

### Query 19

**Query:** Which Netflix executives have made the largest stock purchases in 2024?

**Expected Tool:** `FactSet_Ownership`

**Tool Called:** `FactSet_Ownership`

**Arguments:**
```json
{
  "ids": [
    "NFLX-US"
  ],
  "data_type": "insider_transactions",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "transactionType": "P",
  "topn": "ALL"
}
```

**Status:** OK - Success

**Latency:** 3869ms

---

### Query 20

**Query:** Compare institutional buying patterns between Amazon and Microsoft

**Expected Tool:** `FactSet_Ownership`

**Tool Called:** `FactSet_Ownership`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US",
    "MSFT-US"
  ],
  "data_type": "institutional_transactions",
  "startDate": "2023-01-01",
  "endDate": "2023-12-31"
}
```

**Status:** NO OK - MCP Error: Internal error: Error calling tool 'FactSet_Ownership': API call failed for /factset-ownership/v1/tr

**Latency:** 31787ms

---

### Query 21

**Query:** List all completed acquisitions made by Apple since 2020

**Expected Tool:** `FactSet_MergersAcquisitions`

**Tool Called:** `FactSet_MergersAcquisitions`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "data_type": "deals_by_company",
  "startDate": "2020-01-01",
  "endDate": "2024-01-01",
  "status": "Complete"
}
```

**Status:** OK - Success

**Latency:** 2887ms

---

### Query 22

**Query:** Compare the average deal value of Meta and Google acquisitions over the last 5 years

**Expected Tool:** `FactSet_MergersAcquisitions`

**Tool Called:** `None`

**Arguments:**
```json
null
```

**Status:** NO OK - Error: There is no tool available to directly calculate the average deal value of acquisitions. I can retri

**Latency:** 1446ms

---

### Query 23

**Query:** What deals were announced yesterday where the target is a public company?

**Expected Tool:** `FactSet_MergersAcquisitions`

**Tool Called:** `FactSet_MergersAcquisitions`

**Arguments:**
```json
{
  "data_type": "public_targets",
  "startDate": "2024-01-28",
  "endDate": "2024-01-28"
}
```

**Status:** OK - Success

**Latency:** 1550ms

---

### Query 24

**Query:** Retrieve all M&A deals where Amazon was the acquirer since 2015

**Expected Tool:** `FactSet_MergersAcquisitions`

**Tool Called:** `FactSet_MergersAcquisitions`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US"
  ],
  "data_type": "deals_by_company",
  "startDate": "2015-01-01",
  "endDate": "2024-10-26",
  "status": "All"
}
```

**Status:** OK - Success

**Latency:** 6456ms

---

### Query 25

**Query:** Show me the organizational structure and contact information for Tesla's leadership team

**Expected Tool:** `FactSet_People`

**Tool Called:** `FactSet_People`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US"
  ],
  "data_type": "company_people"
}
```

**Status:** OK - Success

**Latency:** 1616ms

---

### Query 26

**Query:** Show me all the CFOs across the FAANG companies

**Expected Tool:** `FactSet_People`

**Tool Called:** `FactSet_People`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US",
    "META-US",
    "AMZN-US",
    "NFLX-US",
    "GOOGL-US"
  ],
  "data_type": "company_positions",
  "position": "CFO"
}
```

**Status:** OK - Success

**Latency:** 1969ms

---

### Query 27

**Query:** List the founders still active in leadership roles at major tech companies

**Expected Tool:** `FactSet_People`

**Tool Called:** `FactSet_People`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US",
    "MSFT-US",
    "GOOGL-US",
    "AMZN-US",
    "META-US"
  ],
  "data_type": "company_positions",
  "position": "FOU"
}
```

**Status:** OK - Success

**Latency:** 1980ms

---

### Query 28

**Query:** Compare executive compensation packages between Netflix and Disney

**Expected Tool:** `FactSet_People`

**Tool Called:** `FactSet_People`

**Arguments:**
```json
{
  "ids": [
    "NFLX-US",
    "DIS-US"
  ],
  "data_type": "company_compensation"
}
```

**Status:** OK - Success

**Latency:** 1723ms

---

### Query 29

**Query:** Compare gender diversity metrics between Apple, Google, and Meta leadership teams

**Expected Tool:** `FactSet_People`

**Tool Called:** `FactSet_People`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US",
    "GOOGL-US",
    "META-US"
  ],
  "data_type": "company_stats",
  "mbType": "MB"
}
```

**Status:** OK - Success

**Latency:** 1700ms

---

### Query 30

**Query:** When was Microsoft's last earnings call?

**Expected Tool:** `FactSet_CalendarEvents`

**Tool Called:** `FactSet_CalendarEvents`

**Arguments:**
```json
{
  "symbols": [
    "MSFT-US"
  ],
  "universeType": "Tickers",
  "eventTypes": [
    "Earnings",
    "SalesRevenueCall",
    "GuidanceCall"
  ],
  "lastModifiedWithin": "OneMonth"
}
```

**Status:** OK - Success

**Latency:** 2030ms

---

### Query 31

**Query:** Does Nvidia have an earnings call scheduled this quarter?

**Expected Tool:** `FactSet_CalendarEvents`

**Tool Called:** `FactSet_CalendarEvents`

**Arguments:**
```json
{
  "symbols": [
    "NVDA-US"
  ],
  "universeType": "Tickers",
  "eventTypes": [
    "Earnings",
    "SalesRevenueCall",
    "GuidanceCall",
    "AnalystsInvestorsMeeting",
    "ShareholdersMeeting",
    "Conference",
    "ConfirmedEarningsRelease",
    "ProjectedEarningsRelease"
  ],
  "startDateTime": "2024-07-01T00:00:00Z",
  "endDateTime": "2024-09-30T23:59:59Z"
}
```

**Status:** OK - Success

**Latency:** 2297ms

---

### Query 32

**Query:** Compare the number of earnings calls held by JP Morgan and Goldman Sachs in 2024

**Expected Tool:** `FactSet_CalendarEvents`

**Tool Called:** `FactSet_CalendarEvents`

**Arguments:**
```json
{
  "symbols": [
    "JPM-US",
    "GS-US"
  ],
  "universeType": "Tickers",
  "eventTypes": [
    "Earnings",
    "SalesRevenueCall",
    "GuidanceCall"
  ],
  "startDateTime": "2024-01-01T00:00:00Z",
  "endDateTime": "2024-12-31T23:59:59Z"
}
```

**Status:** OK - Success

**Latency:** 1840ms

---

### Query 33

**Query:** Compare Amazon's Americas and Asia/Pacific revenue over the last 3 years

**Expected Tool:** `FactSet_GeoRev`

**Tool Called:** `FactSet_GeoRev`

**Arguments:**
```json
{
  "ids": [
    "AMZN-US"
  ],
  "data_type": "regions",
  "regionIds": [
    "R101",
    "R170"
  ],
  "startDate": "2021-01-01",
  "endDate": "2023-12-31",
  "frequency": "FY"
}
```

**Status:** OK - Success

**Latency:** 2371ms

---

### Query 34

**Query:** What's Coca-Cola's European Union revenue exposure?

**Expected Tool:** `FactSet_GeoRev`

**Tool Called:** `FactSet_GeoRev`

**Arguments:**
```json
{
  "ids": [
    "KO-US"
  ],
  "data_type": "regions",
  "regionIds": [
    "R275"
  ]
}
```

**Status:** OK - Success

**Latency:** 1777ms

---

### Query 35

**Query:** How much revenue does Apple make in China?

**Expected Tool:** `FactSet_GeoRev`

**Tool Called:** `FactSet_GeoRev`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "data_type": "countries",
  "countryIds": [
    "CN"
  ]
}
```

**Status:** OK - Success

**Latency:** 1824ms

---

### Query 36

**Query:** List all direct customers of Taiwan Semiconductor

**Expected Tool:** `FactSet_SupplyChain`

**Tool Called:** `FactSet_SupplyChain`

**Arguments:**
```json
{
  "ids": [
    "2330-TW"
  ],
  "relationshipType": "CUSTOMERS",
  "companyType": "ALL"
}
```

**Status:** OK - Success

**Latency:** 2192ms

---

### Query 37

**Query:** Map the shared supplier ecosystem between Apple and Samsung's supply chains

**Expected Tool:** `FactSet_SupplyChain`

**Tool Called:** `FactSet_SupplyChain`

**Arguments:**
```json
{
  "ids": [
    "AAPL-US"
  ],
  "relationshipType": "SUPPLIERS",
  "companyType": "ALL"
}
```

**Status:** OK - Success

**Latency:** 1789ms

---

### Query 38

**Query:** Starting from Nvidia, map its direct suppliers

**Expected Tool:** `FactSet_SupplyChain`

**Tool Called:** `FactSet_SupplyChain`

**Arguments:**
```json
{
  "ids": [
    "NVDA-US"
  ],
  "relationshipType": "SUPPLIERS"
}
```

**Status:** OK - Success

**Latency:** 1428ms

---

### Query 39

**Query:** Show me Tesla's top competitors

**Expected Tool:** `FactSet_SupplyChain`

**Tool Called:** `FactSet_SupplyChain`

**Arguments:**
```json
{
  "ids": [
    "TSLA-US"
  ],
  "relationshipType": "COMPETITORS",
  "companyType": "PUBLIC_COMPANIES_ONLY"
}
```

**Status:** OK - Success

**Latency:** 1696ms

---

### Query 40

**Query:** Find metric codes for revenue and profitability

**Expected Tool:** `FactSet_Metrics`

**Tool Called:** `FactSet_Metrics`

**Arguments:**
```json
{
  "text": [
    "revenue",
    "profitability"
  ],
  "data_products": [
    "fundamentals"
  ]
}
```

**Status:** OK - Success

**Latency:** 2110ms

---

### Query 41

**Query:** Discover valid metric codes for debt metrics

**Expected Tool:** `FactSet_Metrics`

**Tool Called:** `FactSet_Metrics`

**Arguments:**
```json
{
  "text": [
    "debt",
    "debt to equity",
    "total debt",
    "short term debt",
    "long term debt"
  ],
  "data_products": [
    "fundamentals"
  ]
}
```

**Status:** OK - Success

**Latency:** 2620ms

---

