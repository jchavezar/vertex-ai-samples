# FactSet AI-Ready Data MCP Query Examples

This document lists example natural language queries that can be handled by the FactSet AI-Ready Data MCP tools.

## FactSet_Fundamentals
**Description:** Get most recent and historical data for public company fundamentals and financials, including audit trail.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_Fundamentals tool.
- **Fundamentals:** Pull back income statement items such as sales and net income, balance sheet items such as assets and liabilities, cash flow items, such as depreciation and deferred taxes, and ratios such as total debt to equity and sales per share.

**Sample Prompts:**
- "How much short-term and long-term debt does GE carry?"
- "Is Netflix's current P/E above or below their 5-year average?"
- "How does Tesla's current net margin compare to General Motors and Ford?"
- "Compare the gross margins and ROIC trends for Amazon, Google, and Meta over the past 5 years"
- "What is AMZN's free cash flow for Q1 2024 and how does it compare to Q1 2023?"

## FactSet_EstimatesConsensus
**Description:** Retrieve data for consensus estimates, earnings surprises, analyst ratings, segment projections, and company guidance data.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_EstimatesConsensus tool.
- **Fixed Consensus:** Consensus estimates items aggregated by a statistic such as mean or median for fixed fiscal periods.
- **Rolling Consensus:** Consensus estimates items aggregated by a statistic such as mean or median for rolling fiscal periods.
- **Surprise Analysis:** Surprise (actual vs guidance) data for financial metrics.
- **Analyst Ratings:** Consensus analyst ratings data for buy, hold, and sell.
- **Segments:** Product and geographic segment estimates.
- **Guidance:** Guidance on financial metrics provided by companies.

**Sample Prompts:**
- "How did the 2025 consensus target price for Amazon change between October and December 2024?"
- "How have next fiscal year EPS estimates for Apple evolved over the past 12 months?"
- "How consistent are long-term growth estimates (FY2-FY3) for Nvidia's sales?"
- "How often does Tesla beat earnings estimates? Show me their surprise pattern over the last 2 years."
- "What is the current analyst consensus rating for Apple? How many analysts rate it Buy vs Hold vs Sell?"

## FactSet_GlobalPrices
**Description:** Retrieve data going back to 2006 for public company stock prices, returns, trading volume, corporate actions, latest dividends, and shares outstanding data.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_GlobalPrices tool.
- **Prices:** Get open, high, low, close, and volume.
- **Returns:** Pull returns data for a given date range.
- **Corporate Actions:** Gets historical corporate action data.
- **Annualized Dividends:** Get latest reported annualized dividend.
- **Shares Outstanding:** Get shares outstanding information for securities.

**Sample Prompts:**
- "Show the week-over-week change in closing prices for Oracle in Q1 2024"
- "Which days in the past month had the highest trading volume for Amazon?"
- "Show all gap ups greater than 2% for TSLA stock price in the last quarter"
- "Compare the dividend payment frequencies between Johnson & Johnson, Procter & Gamble, and Unilever over the past two years"
- "Calculate the rolling 12-month return correlation between Netflix and Disney over the past 3 years"

## FactSet_Ownership
**Description:** Get fund holdings, institutional ownership, insider trading activity, and shareholder position changes.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_Ownership tool.
- **Fund Holdings:** Get current and historical fund and etf holdings.
- **Security Holders:** Get current and historical security ownership.
- **Insider Transactions:** Get insider transactions for a given date range.
- **Institutional Transactions:** Get institutional transactions for a given date range.

**Sample Prompts:**
- "Show me all Apple holdings across the top 5 largest mutual funds"
- "Who are the top 10 institutional holders of Apple stock?"
- "Compare insider buying vs selling activity for Tesla over the past year"
- "Which Netflix executives have made the largest stock purchases in 2024?"
- "Compare institutional buying patterns between Amazon and Microsoft"

## FactSet_MergersAcquisitions
**Description:** Get access to key transactions and pricing metrics where the target of the deal is a publicly traded company.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_MergersAcquisitions tool.
- **Deals by Company:** Get a list of deals for companies that were either buyers, sellers, or targets.
- **Public Targets:** Get a list of deals for a given date range in which public companies were the target.
- **Deal Details:** Retrieve details for a specific deal.

**Sample Prompts:**
- "List all completed acquisitions made by Apple since 2020"
- "Compare the average deal value of Meta and Google acquisitions over the last 5 years"
- "List all acquisitions by Microsoft in the gaming sector from 2020-2024. For each, retrieve the target name, announcement date, deal value, and current deal status"
- "What deals were announced yesterday where the target is a public company?"
- "Retrieve all M&A deals where Amazon was the acquirer since 2015. Chart the number of deals per year and average deal value"

## FactSet_People
**Description:** Retrieve executive profiles, leadership rosters, compensation analysis, employment history, and board composition data.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_People tool.
- **Profiles:** Returns information about an individual.
- **Job history:** Returns job history for an individual.
- **Company People:** Returns current executives of companies.
- **Company Positions:** Returns list of people matching a specific position for a list of companies.
- **Company Compensation:** Returns compensation details for top executive listed in annual filings.
- **Company Stats:** Stats such as average age, tenure, compensation for executives of companies.

**Sample Prompts:**
- "Show me the organizational structure and contact information for Tesla's leadership team"
- "Show me all the CFOs across the FAANG companies"
- "List the founders still active in leadership roles at major tech companies"
- "Compare executive compensation packages between Netflix and Disney"
- "Compare gender diversity metrics between Apple, Google, and Meta leadership teams"

## FactSet_CalendarEvents
**Description:** Retrieve company events for a given time period or date range, up to 90 days.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_CalendarEvents tool.
- **Calendar Events:** Retrieve details for company events such as earnings calls, shareholder meetings, and more.

**Sample Prompts:**
- "When was Microsoft's last earnings call?"
- "Does Nvidia have an earnings call scheduled this quarter?"
- "Compare the number of earnings calls held by JP Morgan and Goldman Sachs in 2024"

## FactSet_Metrics
**Description:** Discover valid metric codes for Fundamentals and Estimates APIs before making data requests.

**Details:**
Allows the LLM client to quickly retrieve the correct metrics for Fundamentals and Estimates data.

## FactSet_GeoRev
**Description:** Retrieve geographic revenue exposure data based on region or country breakdowns.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_GeoRev tool.
- **Regions:** Get revenue breakdown by region for a given date range for the requested ids.
- **Countries:** Get revenue breakdown by region for a given date range for the requested ids.

**Sample Prompts:**
- "Compare Amazon's Americas and Asia/Pacific revenue over the last 3 years"
- "What's Coca-Cola's European Union revenue exposure?"
- "How much revenue does Apple make in China?"

## FactSet_SupplyChain
**Description:** Identify both direct (disclosed by a reporting company) and reverse (disclosed by counter parties) relationships for a given company, as currently specified from various sources.

**Details:**
The following section outlines the supported datasets, data coverage, and sample prompts for the FactSet_SupplyChain tool.
- **Relationships:** Understand business relationships between companies from a supplied, competitor, customer, and partner perspective.

**Sample Prompts:**
- "List all direct customers of Taiwan Semiconductor"
- "Map the shared supplier ecosystem between Apple and Samsung's supply chains"
- "Starting from Nvidia, map its direct suppliers. Then retrieve the top 5 suppliers that appear most frequently as direct suppliers to other suppliers within Nvidia's network"
- "Show me the 30-day price volatility for Tesla and compare it to its top 5 competitors"