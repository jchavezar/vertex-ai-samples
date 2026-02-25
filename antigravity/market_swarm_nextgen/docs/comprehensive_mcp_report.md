# FactSet MCP Comprehensive Query Report

**Generated:** 2026-01-27 01:19:05

## Summary

| Metric | Value |
|--------|-------|
| Total Queries | 41 |
| OK | 40 (97.6%) |
| NO OK | 1 (2.4%) |
| Avg Latency | 2188ms |

## Results by Category

| Category | OK | NO OK | Rate |
|----------|-----|-------|------|
| FactSet_Fundamentals | 5 | 0 | 100% |
| FactSet_EstimatesConsensus | 5 | 0 | 100% |
| FactSet_GlobalPrices | 5 | 0 | 100% |
| FactSet_Ownership | 4 | 1 | 80% |
| FactSet_MergersAcquisitions | 4 | 0 | 100% |
| FactSet_People | 5 | 0 | 100% |
| FactSet_CalendarEvents | 3 | 0 | 100% |
| FactSet_GeoRev | 3 | 0 | 100% |
| FactSet_SupplyChain | 4 | 0 | 100% |
| FactSet_Metrics | 2 | 0 | 100% |

## Detailed Results

### FactSet_Fundamentals

**Query:** How much short-term and long-term debt does GE carry?

**Tool:** `FactSet_Fundamentals`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "GE-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPeriod": null,
      "fiscalYear": null,
      "fiscalPeriodLength": null,
      "fiscalEndDate": "2025-12-31",
      "reportDate": null,
      "epsReportDate": null,
      "updateType": null,
      "currency": "USD",
      "value": null
    }
  ]
}
```

**Latency:** 569ms

---

### FactSet_Fundamentals

**Query:** Is Netflix's current P/E above or below their 5-year average?

**Tool:** `FactSet_Fundamentals`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "NFLX-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPeriod": null,
      "fiscalYear": null,
      "fiscalPeriodLength": null,
      "fiscalEndDate": "2021-12-31",
      "reportDate": null,
      "epsReportDate": null,
      "updateType": null,
      "currency": "USD",
      "value": null
    },
    {
      "requestId": "NFLX-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalP...
```

**Latency:** 288ms

---

### FactSet_Fundamentals

**Query:** How does Tesla's current net margin compare to General Motors and Ford?

**Tool:** `FactSet_Fundamentals`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "TSLA-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPeriod": null,
      "fiscalYear": null,
      "fiscalPeriodLength": null,
      "fiscalEndDate": "2024-12-31",
      "reportDate": null,
      "epsReportDate": null,
      "updateType": null,
      "currency": "USD",
      "value": null
    },
    {
      "requestId": "GM-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPer...
```

**Latency:** 302ms

---

### FactSet_Fundamentals

**Query:** Compare the gross margins and ROIC trends for Amazon, Google, and Meta over the past 5 years

**Tool:** `FactSet_Fundamentals`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "AMZN-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPeriod": null,
      "fiscalYear": null,
      "fiscalPeriodLength": null,
      "fiscalEndDate": "2021-12-31",
      "reportDate": null,
      "epsReportDate": null,
      "updateType": null,
      "currency": "USD",
      "value": null
    },
    {
      "requestId": "AMZN-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalP...
```

**Latency:** 306ms

---

### FactSet_Fundamentals

**Query:** What is AMZN's free cash flow for Q1 2024 and how does it compare to Q1 2023?

**Tool:** `FactSet_Fundamentals`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "AMZN-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalPeriod": null,
      "fiscalYear": null,
      "fiscalPeriodLength": null,
      "fiscalEndDate": "2023-03-31",
      "reportDate": null,
      "epsReportDate": null,
      "updateType": null,
      "currency": "USD",
      "value": null
    },
    {
      "requestId": "AMZN-US",
      "fsymId": null,
      "metric": null,
      "periodicity": null,
      "fiscalP...
```

**Latency:** 238ms

---

### FactSet_EstimatesConsensus

**Query:** How did the 2025 consensus target price for Amazon change between October and December 2024?

**Tool:** `FactSet_EstimatesConsensus`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "AMZN-US",
      "fsymId": "MCNYYL-R",
      "metric": "PRICE_TGT",
      "periodicity": "ANN",
      "fiscalPeriod": 1,
      "fiscalYear": 2024,
      "fiscalEndDate": "2024-12-31",
      "relativePeriod": 1,
      "estimateDate": "2024-10-01",
      "currency": "LOCAL",
      "estimateCurrency": "USD",
      "mean": 221.21563636363638,
      "median": 220.0,
      "standardDeviation": 16.4428877750789,
      "high": 265.0,
      "low": 180.0,
      "esti...
```

**Latency:** 204ms

---

### FactSet_EstimatesConsensus

**Query:** How have next fiscal year EPS estimates for Apple evolved over the past 12 months?

**Tool:** `FactSet_EstimatesConsensus`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "AAPL-US",
      "fsymId": "MH33D6-R",
      "metric": "EPS",
      "periodicity": "ANN",
      "fiscalPeriod": 1,
      "fiscalYear": 2025,
      "fiscalEndDate": "2025-09-30",
      "relativePeriod": 1,
      "estimateDate": "2025-01-27",
      "currency": "LOCAL",
      "estimateCurrency": "USD",
      "mean": 7.34564315915,
      "median": 7.37330876095,
      "standardDeviation": 0.219401724890073,
      "high": 7.85,
      "low": 6.71,
      "estimate...
```

**Latency:** 272ms

---

### FactSet_EstimatesConsensus

**Query:** How consistent are long-term growth estimates (FY2-FY3) for Nvidia's sales?

**Tool:** `FactSet_EstimatesConsensus`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "NVDA-US",
      "fsymId": "K7TPSX-R",
      "metric": "SALES",
      "periodicity": "ANN",
      "fiscalPeriod": 1,
      "fiscalYear": 2026,
      "fiscalEndDate": "2027-01-31",
      "relativePeriod": 2,
      "estimateDate": "2026-01-27",
      "currency": "LOCAL",
      "estimateCurrency": "USD",
      "mean": 329612.5397693138,
      "median": 324596.376,
      "standardDeviation": 27566.8402702195,
      "high": 412529.0,
      "low": 264979.0,
     ...
```

**Latency:** 265ms

---

### FactSet_EstimatesConsensus

**Query:** How often does Tesla beat earnings estimates? Show me their surprise pattern over the last 2 years.

**Tool:** `FactSet_EstimatesConsensus`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": "Q2YN1N-R",
      "date": "2024-01-28",
      "currency": "LOCAL",
      "estimateCurrency": "USD",
      "metric": "EPS",
      "statistic": "MEAN",
      "periodicity": "QTR",
      "fiscalEndDate": "2023-12-31",
      "fiscalYear": 2023,
      "fiscalPeriod": 4,
      "surpriseDate": "2024-01-25",
      "surpriseAmount": -0.031245570986363637,
      "surprisePercent": -4.215279282517082,
      "surpriseBefore": 0.7412455709863637,
      "surpriseAfter": 0.7...
```

**Latency:** 495ms

---

### FactSet_EstimatesConsensus

**Query:** What is the current analyst consensus rating for Apple? How many analysts rate it Buy vs Hold vs Sell?

**Tool:** `FactSet_EstimatesConsensus`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": "MH33D6-R",
      "estimateDate": "2026-01-27",
      "buyCount": 22,
      "overweightCount": 7,
      "holdCount": 18,
      "underweightCount": 1,
      "sellCount": 2,
      "ratingsNestTotal": 50,
      "ratingsNote": 1.54,
      "ratingsNoteText": "OVERWEIGHT",
      "requestId": "AAPL-US"
    }
  ]
}
```

**Latency:** 197ms

---

### FactSet_GlobalPrices

**Query:** Show the week-over-week change in closing prices for Oracle in Q1 2024

**Tool:** `FactSet_GlobalPrices`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "volume": 6133770,
      "date": "2024-01-05",
      "priceLow": 102.29,
      "tradeCount": 59849,
      "requestId": "ORCL-US",
      "price": 102.73,
      "vwap": 102.850421,
      "fsymId": "HQ4DBK-R",
      "currency": "USD",
      "priceOpen": 102.53,
      "priceHigh": 103.72,
      "turnover": 630938.744736
    },
    {
      "volume": 9703848,
      "date": "2024-01-12",
      "priceLow": 104.965,
      "tradeCount": 86084,
      "requestId": "ORCL-US",
      ...
```

**Latency:** 253ms

---

### FactSet_GlobalPrices

**Query:** Which days in the past month had the highest trading volume for Amazon?

**Tool:** `FactSet_GlobalPrices`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "volume": 15994726,
      "date": "2025-12-26",
      "requestId": "AMZN-US",
      "price": 232.52,
      "fsymId": "MCNYYL-R",
      "currency": "USD"
    },
    {
      "volume": 19797909,
      "date": "2025-12-29",
      "requestId": "AMZN-US",
      "price": 232.07,
      "fsymId": "MCNYYL-R",
      "currency": "USD"
    },
    {
      "volume": 21910453,
      "date": "2025-12-30",
      "requestId": "AMZN-US",
      "price": 232.53,
      "fsymId": "MCNYYL-R",
 ...
```

**Latency:** 270ms

---

### FactSet_GlobalPrices

**Query:** Show all gap ups greater than 2% for TSLA stock price in the last quarter

**Tool:** `FactSet_GlobalPrices`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "volume": 67983544,
      "date": "2025-10-29",
      "priceLow": 452.65,
      "tradeCount": 1415330,
      "requestId": "TSLA-US",
      "price": 461.51,
      "vwap": 460.304648,
      "fsymId": "Q2YN1N-R",
      "currency": "USD",
      "priceOpen": 462.5,
      "priceHigh": 465.7,
      "turnover": 31293995.964357
    },
    {
      "volume": 72447938,
      "date": "2025-10-30",
      "priceLow": 439.61,
      "tradeCount": 1551353,
      "requestId": "TSLA-US",
 ...
```

**Latency:** 357ms

---

### FactSet_GlobalPrices

**Query:** Compare the dividend payment frequencies between Johnson & Johnson, Procter & Gamble, and Unilever over the past two years

**Tool:** `FactSet_GlobalPrices`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "amtGrossTradingUnadj": 1.19,
      "adjFactorCombined": null,
      "amtDefTradingUnadj": 1.19,
      "eventTypeDesc": "Dividend",
      "fsymId": "KV0J41-R",
      "rightsIssueCurrency": null,
      "amtNetTradingAdj": null,
      "distNewTerm": null,
      "amtDefDecUnadj": 1.19,
      "rightsIssuePrice": null,
      "dividendFrequencyCode": 4.0,
      "amtNetDecUnadj": null,
      "requestId": "JNJ-US",
      "distOldTerm": null,
      "recordDate": "2024-02-20",
  ...
```

**Latency:** 356ms

---

### FactSet_GlobalPrices

**Query:** Calculate the rolling 12-month return correlation between Netflix and Disney over the past 3 years

**Tool:** `FactSet_GlobalPrices`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": "C4C0BL-R",
      "totalReturn": -29.098333,
      "date": "2022-01-31",
      "currency": "USD",
      "requestId": "NFLX-US"
    },
    {
      "fsymId": "C4C0BL-R",
      "totalReturn": -7.63684,
      "date": "2022-02-28",
      "currency": "USD",
      "requestId": "NFLX-US"
    },
    {
      "fsymId": "C4C0BL-R",
      "totalReturn": -5.051708,
      "date": "2022-03-31",
      "currency": "USD",
      "requestId": "NFLX-US"
    },
    {
      "fsymId":...
```

**Latency:** 427ms

---

### FactSet_Ownership

**Query:** Show me all Apple holdings across the top 5 largest mutual funds

**Tool:** `FactSet_Ownership`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "holderId": "M4004630",
      "fsymId": null,
      "holderEntityId": "04BF4M-E",
      "holderName": "Vanguard Total Stock Market ETF",
      "date": "2025-12-31",
      "currency": "USD",
      "investorType": "Exchange Traded Fund",
      "holderType": "Mutual Fund",
      "adjHolding": 464189894.0,
      "adjMarketValue": 126194664582.84,
      "weightClose": 6.1099,
      "percentOutstanding": 3.1582,
      "source": "US Fund (N-30D)",
      "requestId": "AAPL-US"
...
```

**Latency:** 3824ms

---

### FactSet_Ownership

**Query:** Who are the top 10 institutional holders of Apple stock?

**Tool:** `FactSet_Ownership`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "holderId": "F72998",
      "fsymId": null,
      "holderEntityId": "002FYS-E",
      "holderName": "The Vanguard Group, Inc.",
      "date": "2025-09-30",
      "currency": "USD",
      "investorType": "Mutual Fund Manager",
      "holderType": "Institution",
      "adjHolding": 1256864037.0,
      "adjMarketValue": 341691057098.82,
      "weightClose": 4.5665,
      "percentOutstanding": 8.5513,
      "source": "13F Form",
      "requestId": "AAPL-US"
    },
    {
   ...
```

**Latency:** 27066ms

---

### FactSet_Ownership

**Query:** Compare insider buying vs selling activity for Tesla over the past year

**Tool:** `FactSet_Ownership`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "requestId": "TSLA-US",
      "fsymId": null,
      "currency": null,
      "holderName": "DENHOLM ROBYN M",
      "holderTitle": "Director",
      "holderId": "S155166",
      "shares": 112390.0,
      "price": null,
      "netValueChange": null,
      "filingDate": "2025-02-06",
      "isDerivative": false,
      "isDirect": true,
      "tradeType": "Acquisition",
      "formType": "4         ",
      "transactionDate": "2025-02-03",
      "sharesOwned": 197390.0,
   ...
```

**Latency:** 2622ms

---

### FactSet_Ownership

**Query:** Which Netflix executives have made the largest stock purchases in 2024?

**Tool:** `FactSet_Ownership`

**Status:** OK

**Answer:**
```
Data returned but values are null (may be market closed or no data)
```

**Latency:** 2363ms

---

### FactSet_Ownership

**Query:** Compare institutional buying patterns between Amazon and Microsoft

**Tool:** `FactSet_Ownership`

**Status:** NO OK

**Answer:**
```
ERROR: Internal error: Error calling tool 'FactSet_Ownership': API call failed for /factset-ownership/v1/transactions/institutional:
```

**Latency:** 30138ms

---

### FactSet_MergersAcquisitions

**Query:** List all completed acquisitions made by Apple since 2020

**Tool:** `FactSet_MergersAcquisitions`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "dealId": "4192889MM",
      "target": {
        "fsymId": null,
        "name": "DarwinAI Corp.",
        "industry": "Information Technology Services"
      },
      "buyers": [
        {
          "fsymId": null,
          "name": "Apple, Inc.",
          "industry": null,
          "ultimateParentId": null
        }
      ],
      "sellers": [
        {
          "fsymId": null,
          "name": "iNovia Capital, Inc.",
          "industry": null,
          "ultimat...
```

**Latency:** 715ms

---

### FactSet_MergersAcquisitions

**Query:** Compare the average deal value of Meta and Google acquisitions over the last 5 years

**Tool:** `FactSet_MergersAcquisitions`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "dealId": "4226685MM",
      "target": {
        "fsymId": null,
        "name": "Invenergy LLC /760 Mw Solar Projects/",
        "industry": "Alternative Power Generation"
      },
      "buyers": [
        {
          "fsymId": null,
          "name": "Meta Platforms, Inc.",
          "industry": null,
          "ultimateParentId": null
        }
      ],
      "sellers": [
        {
          "fsymId": null,
          "name": "Invenergy LLC",
          "industry": nu...
```

**Latency:** 675ms

---

### FactSet_MergersAcquisitions

**Query:** What deals were announced yesterday where the target is a public company?

**Tool:** `FactSet_MergersAcquisitions`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "dealId": "4277317MM",
      "target": {
        "fsymId": null,
        "name": "BBD Initiative, Inc.",
        "industry": "Miscellaneous Commercial Services"
      },
      "buyers": [
        {
          "fsymId": null,
          "name": "Headwaters Co. Ltd.",
          "industry": null,
          "ultimateParentId": null
        }
      ],
      "sellers": [
        {
          "fsymId": null,
          "name": "BBD Initiative, Inc.",
          "industry": null,
  ...
```

**Latency:** 1643ms

---

### FactSet_MergersAcquisitions

**Query:** Retrieve all M&A deals where Amazon was the acquirer since 2015 (2024 window)

**Tool:** `FactSet_MergersAcquisitions`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "dealId": "4203038MM",
      "target": {
        "fsymId": null,
        "name": "MX Media & Entertainment Pte Ltd.",
        "industry": "Internet Software/Services"
      },
      "buyers": [
        {
          "fsymId": null,
          "name": "Amazon.com, Inc.",
          "industry": null,
          "ultimateParentId": null
        }
      ],
      "sellers": [
        {
          "fsymId": null,
          "name": "Times Internet Ltd.",
          "industry": null,
...
```

**Latency:** 495ms

---

### FactSet_People

**Query:** Show me the organizational structure and contact information for Tesla's leadership team

**Tool:** `FactSet_People`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": null,
      "email": null,
      "name": "Robyn M. Denholm",
      "jobFunction1": "Chairman",
      "jobFunction2": "Independent Dir/Board Member",
      "jobFunction3": null,
      "jobFunction4": null,
      "mainPhone": "1.512.516.8177",
      "personId": "0056GC-E",
      "phone": null,
      "requestId": "TSLA-US",
      "title": "Chairman"
    },
    {
      "fsymId": null,
      "email": null,
      "name": "Elon Reeve Musk",
      "jobFunction1": "Chi...
```

**Latency:** 323ms

---

### FactSet_People

**Query:** Show me all the CFOs across the FAANG companies

**Tool:** `FactSet_People`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": null,
      "personId": "0JJ1H0-E",
      "name": "Susan J. Li",
      "title": "Chief Financial Officer",
      "yearsAtFirm": 17.82,
      "age": 40,
      "gender": "Female",
      "requestPosition": "CFO",
      "requestId": "META-US"
    },
    {
      "fsymId": null,
      "personId": "1095LQ-E",
      "name": "Kevan Parekh, MBA",
      "title": "Chief Financial Officer & Senior Vice President",
      "yearsAtFirm": 12.65,
      "age": 54,
      "gender"...
```

**Latency:** 296ms

---

### FactSet_People

**Query:** List the founders still active in leadership roles at major tech companies

**Tool:** `FactSet_People`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": null,
      "personId": "07JZCT-E",
      "name": "Chris R. Hughes",
      "title": "Founder",
      "yearsAtFirm": 21.98,
      "age": null,
      "gender": "Male",
      "requestPosition": "FOU",
      "requestId": "META-US"
    },
    {
      "fsymId": null,
      "personId": "09M1YP-E",
      "name": "Lee Charles Linden, MBA",
      "title": "Founder",
      "yearsAtFirm": null,
      "age": 43,
      "gender": "Male",
      "requestPosition": "FOU",
     ...
```

**Latency:** 428ms

---

### FactSet_People

**Query:** Compare executive compensation packages between Netflix and Disney

**Tool:** `FactSet_People`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "name": "Reed Hastings",
      "personId": "001K7R-E",
      "title": "Non-Executive Chairman",
      "salary": 100000,
      "bonus": null,
      "stockAwards": 965039,
      "optionsAwards": 281697,
      "otherCompensation": 2215,
      "totalCompensation": 1748951,
      "nonEquityIncentivePlanComp": 400000,
      "nonQualifiedCompEarnings": null,
      "compensationYear": "2024",
      "requestId": "NFLX-US"
    },
    {
      "name": "Gregory K. Peters",
      "pe...
```

**Latency:** 377ms

---

### FactSet_People

**Query:** Compare gender diversity metrics between Apple, Google, and Meta leadership teams

**Tool:** `FactSet_People`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "fsymId": null,
      "averageMgmtCompensation": 42989440,
      "averageTenure": 17.62,
      "medianTenure": 1.91,
      "averageAge": 61.41,
      "maxAge": 77,
      "minimumAge": 51,
      "medianAge": 61,
      "boardIndependentDirectors": 7,
      "femaleBoardMembers": 4,
      "femaleBoardMembersPercent": 50.0,
      "numberOfMembers": 35,
      "onOtherBoardsAll": 8,
      "onOtherBoardsCorporate": 8,
      "mbType": "MB",
      "requestId": "AAPL-US"
    },
  ...
```

**Latency:** 700ms

---

### FactSet_CalendarEvents

**Query:** When was Microsoft's last earnings call?

**Tool:** `FactSet_CalendarEvents`

**Status:** OK

**Answer:**
```
{
  "error": "VALIDATION ERROR: Date range exceeds maximum 90-day limit.\n\nYour request:\n  - startDateTime: 2025-10-29T00:00:00Z\n  - endDateTime: 2026-01-27T23:59:59Z\n  - Range: 90 days, 23 hours, 59 minutes, 59 seconds\n  - Total: 7,862,399 seconds (max: 7,776,000 seconds)\n\nThe FactSet Events API enforces a STRICT 90-DAY (7,776,000 seconds) MAXIMUM.\nEven adding 1 second over 90 days will cause the API to reject your request.\n\nSolutions:\n1. Use endDateTime at 00:00:00 (midnight) instea
```

**Latency:** 88ms

---

### FactSet_CalendarEvents

**Query:** Does Nvidia have an earnings call scheduled this quarter?

**Tool:** `FactSet_CalendarEvents`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "identifier": "NVDA-US",
      "entityName": "NVIDIA Corp.",
      "description": "Q4 2026 Earnings Release",
      "eventDateTime": "2026-02-25T00:00:00Z",
      "marketTimeCode": "Unspecified",
      "eventType": "ConfirmedEarningsRelease",
      "eventId": "1201329677",
      "webcastLink": "",
      "irLink": "",
      "fiscalYear": "2025",
      "fiscalPeriod": "4",
      "lastModifiedDate": "2025-12-02T14:54:08Z"
    }
  ]
}
```

**Latency:** 779ms

---

### FactSet_CalendarEvents

**Query:** Compare the number of earnings calls held by JP Morgan and Goldman Sachs in 2024

**Tool:** `FactSet_CalendarEvents`

**Status:** OK

**Answer:**
```
{
  "error": "VALIDATION ERROR: Date range exceeds maximum 90-day limit.\n\nYour request:\n  - startDateTime: 2024-10-01T00:00:00Z\n  - endDateTime: 2024-12-31T00:00:00Z\n  - Range: 91 days, 0 hours, 0 minutes, 0 seconds\n  - Total: 7,862,400 seconds (max: 7,776,000 seconds)\n\nThe FactSet Events API enforces a STRICT 90-DAY (7,776,000 seconds) MAXIMUM.\nEven adding 1 second over 90 days will cause the API to reject your request.\n\nSolutions:\n1. Use endDateTime at 00:00:00 (midnight) instead o
```

**Latency:** 109ms

---

### FactSet_GeoRev

**Query:** Compare Amazon's Americas and Asia/Pacific revenue over the last 3 years

**Tool:** `FactSet_GeoRev`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "date": "2021-12-31",
      "fsymId": null,
      "regionId": "R101",
      "requestId": "AMZN-US",
      "regionCertaintyClass": "A",
      "regionCertaintyRank": 79,
      "regionConfidence": 0.998863,
      "regionName": "Americas",
      "regionPercent": 68.394469,
      "regionRevenue": 321332.26214518,
      "currency": "USD",
      "fiscalEndDate": "2021-12-31",
      "reportDate": "2021-12-31"
    },
    {
      "date": "2022-12-31",
      "fsymId": null,
      ...
```

**Latency:** 821ms

---

### FactSet_GeoRev

**Query:** What's Coca-Cola's European Union revenue exposure?

**Tool:** `FactSet_GeoRev`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "date": "2024-12-31",
      "fsymId": null,
      "regionId": "R275",
      "requestId": "KO-US",
      "regionCertaintyClass": "C",
      "regionCertaintyRank": 46,
      "regionConfidence": 0.994512,
      "regionName": "European Union",
      "regionPercent": 12.652438,
      "regionRevenue": 5917.03915508,
      "currency": "USD",
      "fiscalEndDate": "2024-12-31",
      "reportDate": "2024-12-31"
    }
  ]
}
```

**Latency:** 610ms

---

### FactSet_GeoRev

**Query:** How much revenue does Apple make in China?

**Tool:** `FactSet_GeoRev`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "date": "2025-09-30",
      "fsymId": null,
      "countryId": "CN",
      "requestId": "AAPL-US",
      "countryCertaintyClass": "A",
      "countryCertaintyRank": 72,
      "countryConfidence": 0.996513,
      "countryName": "China",
      "countryPercent": 14.540151,
      "countryRevenue": 60510.43780311,
      "currency": "USD",
      "fiscalEndDate": "2025-09-30",
      "reportDate": "2025-09-27"
    }
  ]
}
```

**Latency:** 648ms

---

### FactSet_SupplyChain

**Query:** List all direct customers of Taiwan Semiconductor

**Tool:** `FactSet_SupplyChain`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "entityId": "068XX4-E",
      "companyName": "Global Unichip Corp.",
      "overlappingProductCount": "5 of 10",
      "overlapPercentage": 50,
      "relationshipDirection": "Mutual",
      "requestId": "TSM-US",
      "requestEntityId": "001Y70-E"
    },
    {
      "entityId": "000V67-E",
      "companyName": "QUALCOMM Incorporated",
      "overlappingProductCount": "1 of 24",
      "overlapPercentage": 4,
      "relationshipDirection": "Mutual",
      "requestId": "...
```

**Latency:** 436ms

---

### FactSet_SupplyChain

**Query:** Map the shared supplier ecosystem between Apple and Samsung's supply chains

**Tool:** `FactSet_SupplyChain`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "entityId": "000DS3-E",
      "companyName": "Cirrus Logic, Inc.",
      "overlappingProductCount": "0 of 14",
      "overlapPercentage": 0,
      "relationshipDirection": "Reverse",
      "requestId": "AAPL-US",
      "requestEntityId": "AAPL-US"
    },
    {
      "entityId": "0HBXZ2-E",
      "companyName": "Cherrypick Games SA",
      "overlappingProductCount": "0 of 8",
      "overlapPercentage": 0,
      "relationshipDirection": "Reverse",
      "requestId": "AAPL...
```

**Latency:** 2577ms

---

### FactSet_SupplyChain

**Query:** Starting from Nvidia, map its direct suppliers

**Tool:** `FactSet_SupplyChain`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "entityId": "0638G0-E",
      "companyName": "Fabrinet",
      "overlappingProductCount": "2 of 22",
      "overlapPercentage": 9,
      "relationshipDirection": "Mutual",
      "requestId": "NVDA-US",
      "requestEntityId": "00208X-E"
    },
    {
      "entityId": "05HWW7-E",
      "companyName": "IBIDEN CO., LTD.",
      "overlappingProductCount": "0 of 24",
      "overlapPercentage": 0,
      "relationshipDirection": "Reverse",
      "requestId": "NVDA-US",
      ...
```

**Latency:** 354ms

---

### FactSet_SupplyChain

**Query:** Show me Tesla's top competitors

**Tool:** `FactSet_SupplyChain`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "entityId": "001YFZ-E",
      "companyName": "Volkswagen AG Pref",
      "overlappingProductCount": "6 of 80",
      "overlapPercentage": 8,
      "relationshipDirection": "Reverse",
      "requestId": "TSLA-US",
      "requestEntityId": "006XY7-E"
    },
    {
      "entityId": "0JYCR6-E",
      "companyName": "Turbo Energy, S.A. Sponsored ADR",
      "overlappingProductCount": "4 of 5",
      "overlapPercentage": 80,
      "relationshipDirection": "Reverse",
      "re...
```

**Latency:** 311ms

---

### FactSet_Metrics

**Query:** Find metric codes for revenue and profitability

**Tool:** `FactSet_Metrics`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "query": "revenue",
      "target": "metric",
      "results": [
        {
          "score": 0.9236389,
          "properties": {
            "category": "INDUSTRY_METRICS",
            "description": "Revenue in the Pharmaceutical industry captures the total income generated from the sale of drugs, medical devices, and related products and services. It is a foundational metric for evaluating the financial performance, market share, and growth trajectory of a company. ...
```

**Latency:** 1087ms

---

### FactSet_Metrics

**Query:** Discover valid metric codes for debt metrics

**Tool:** `FactSet_Metrics`

**Status:** OK

**Answer:**
```
{
  "data": [
    {
      "query": "debt",
      "target": "metric",
      "results": [
        {
          "score": 0.9674977,
          "properties": {
            "category": "BALANCE_SHEET",
            "description": "Total Debt represents the sum of all interest-bearing liabilities on a company's balance sheet, including both short-term and long-term borrowings. This metric provides a comprehensive view of a company’s overall indebtedness and is crucial for assessing financial leverage and...
```

**Latency:** 5411ms

---

