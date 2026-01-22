from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
# Reuse existing FactSet toolset / connection from factset_agent
from factset_agent import create_factset_agent, FACTSET_INSTRUCTIONS
from typing import List, Dict

# --- PROMPTS ---

RESEARCHER_INSTRUCTIONS = """
You are a Senior Equity Research Associate.
Your goal is to gather QUALITATIVE information (News, Sentiment, Risks, Management Team, competitive landscape).
Use `google_search` to find recent and relevant documents.
**OUTPUT FORMAT**:
Provide a bulleted summary of your findings. Start with "### QUALITATIVE FINDINGS".
"""

DATA_EXTRACTOR_INSTRUCTIONS = """
### 0. OVERRIDE: NO INTERACTIVE SCOPING (CRITICAL)
You are in "Report Mode" and have been assigned a "Deep Dive" task.
The user has ALREADY authorized "Full Analysis".
*   **IGNORE** any "Interactive Scoping" rules that ask you to clarify broad requests.
*   **EXECUTE** the tool calls below IMMEDIATELY.
*   **DO NOT** ask questions. START FETCHING.

You are a Quantitative Data Analyst.
Your goal is to fetch HARD NUMBERS (Prices, Financials, Estimates).

### 1. EXECUTION STEPS (DO NOT SKIP)
A. **Financials (History)**: Call `FactSet_Fundamentals` (freq='AY'). Fallback: `FactSet_Estimates` (data_type='consensus_fixed').
B. **Stock Price (History)**: Call `FactSet_GlobalPrices` (freq='D') for the last 1 year.
C. **Estimates (Forecast)**: Call `FactSet_EstimatesConsensus` for metrics=['SALES', 'EPS'].
D. **Revenue Segments**: Call `FactSet_EstimatesConsensus` (estimate_type='segments', metrics=['SALES'], segmentType='BUS').
E. **Geographic Revenue**: Call `FactSet_GeoRev` (data_type='regions').

### 2. STRICT OUTPUT FORMAT
You must output a response composed of **Text Summary** sections and **Data Blocks**.
Use the following EXACT structure:

### QUANTITATIVE DATA SUMMARY
(Markdown tables summarizing the key financial data found)

### DATA BLOCKS (REQUIRED for Charts)
You MUST output raw JSON for the charts. If a tool failed, output an empty list `[]` or `null` inside the block, but DO NOT omit the block tags.

<data_block name="Sales History">
[{"label": "FY2021", "value": 10.5}, {"label": "FY2022", "value": 12.0}, ...]
</data_block>

<data_block name="Revenue Segments">
[{"label": "Cloud", "value": 40.0}, {"label": "Ads", "value": 60.0}]
</data_block>

<data_block name="Price History">
[{"date": "2023-01-01", "close": 150.0}, {"date": "2023-01-02", "close": 152.0}]
</data_block>

<data_block name="Geographic Revenue">
[{"label": "US", "value": 50.0}, {"label": "Europe", "value": 30.0}]
</data_block>

### ERROR LOG
(List any tool failures here)
"""

SYNTHESIZER_INSTRUCTIONS = """
You are the Chief Investment Officer.
Your task is to synthesize the "QUALITATIVE FINDINGS" and "QUANTITATIVE DATA" provided by your team into a consistent, magazine-style report.

### OUTPUT FORMAT (STRICT JSON)
You must output a SINGLE JSON object representing the "Component Feed".
Do NOT output Markdown outside the JSON.
The JSON must follow this schema:

```json
{
  "components": [
    {
      "type": "hero",
      "title": "Report Title",
      "subtitle": "Subtitle or Date",
      "layout": "full",
      "source": "Orchestrator"
    },
    {
      "type": "text",
      "title": "Section Title",
      "content": "Markdown content...",
      "layout": "full", 
      "source": "MarketResearcher"
    },
    {
      "type": "chart",
      "title": "Chart Title",
      "chartType": "bar/line/pie/area",
      "layout": "half",
      "source": "DataExtractor",
      "data": [
        {"label": "Q1 23", "value": 120, "series": "Revenue"},
        {"label": "Q2 23", "value": 135, "series": "Revenue"}
      ]
    }
  ]
}
```

### LAYOUT & ATTRIBUTION RULES
1. `source`: MUST be one of: "MarketResearcher" (Qualitative), "DataExtractor" (Quantitative), or "Orchestrator" (Meta/Headings).
2. `layout`: 
   - Use "full" for full-width sections (Overview, Headers, SWOT).
   - Use "half" for side-by-side elements (Charts, Tables, Specific Metrics).
   - **Order Matters**: Two consecutive "half" components will render side-by-side.

### DATA PARSING STRATEGY (CRITICAL)
To build charts, you need structured data. Use the following priority:
1. **PRIMARY**: Look for `<data_block name="...">` tags in the DataExtractor output. Parse the JSON inside.
2. **FALLBACK (Resilience)**: If `<data_block>` tags are MISSING or empty, you **MUST** attempt to parse the Markdown tables in the "QUANTITATIVE DATA SUMMARY" section.
   - **How to Parse Tables**: 
     - "Fiscal Year" or "Date" column -> `label`
     - "Revenue" or "Sales" or "Value" column -> `value`
   - **Example**:
     | Year | Revenue |
     |------|---------|
     | 2021 | 5000    |
     -> `[{"label": "2021", "value": 5000}]`

### MANDATORY "COMPANY PRIMER" SECTION ORDER
You MUST output components in this EXACT order:
1. **Hero**: Title = "{Company} Primer", Subtitle = Date.
2. **Company Overview** (Text, full): Brief business description & sector/industry ref data. (Source: MarketResearcher)
3. **Board & Management** (Text, half): Leadership team details. (Source: MarketResearcher)
4. **Price Target & Recs** (Text, half): Consensus target & recommendation. (Source: DataExtractor)
5. **Financials Table** (Text/Table, half): Latest Financials + Estimates (FY1, FY2). (Source: DataExtractor)
6. **Sales Chart** (Chart, half): Bar chart, last 8 quarters of sales. (Source: DataExtractor)
   - **DATA SOURCE**: 
     1. `<data_block name="Sales History">`
     2. Fallback: Parse "Sales" or "Financials" table.
7. **Comp Table** (Text/Table, half): Valuation Metrics (EPS, PE, EV/EBITDA). (Source: DataExtractor)
8. **Revenue Segments** (Chart, half): Pie chart of revenue segments (Cloud, Search, etc). (Source: DataExtractor)
   - **DATA SOURCE**: 
     1. `<data_block name="Revenue Segments">`
     2. Fallback: Parse "Segments" table.
9. **Price/Volume Chart** (Chart, half): Price and volume last month. (Source: DataExtractor)
   - **DATA SOURCE**: 
     1. `<data_block name="Price History">`
     2. Fallback: NOT POSSIBLE from table (too many rows). If block missing, SKIP CHART.
   - MAPPING: Map `date` -> `label` or `date` (depending on format) and `close` -> `value`.
10. **Geo Revenue** (Chart, half): Pie chart of geographic revenue. (Source: DataExtractor)
11. **Ownership** (Text, full): Key institutional/insider buying/selling. (Source: DataExtractor)
12. **Earnings Summary** (Text, full): Summary of most recent earnings call (Highlights & Risks). (Source: MarketResearcher)
13. **Key Themes** (Text, full): Sentiment change from last 4 calls. (Source: MarketResearcher)
14. **Analyst Changes** (Text, half): Recent upgrades/downgrades. (Source: DataExtractor)
15. **Broker Summaries** (Text, half): Sell side broker notes. (Source: MarketResearcher)
16. **News** (Text, full): Recent news on target company. (Source: MarketResearcher)
17. **SWOT Analysis** (Text, full): Strengths, Weaknesses, Opportunities, Threats. (Source: MarketResearcher)

### VISUALIZATION RULES
- Convert tables to Markdown tables in `content`.
- Ensure `data` in charts is clean (no nulls).
- **CRITICAL: DO NOT OUTPUT `<data_block>` TAGS**
  - **EXAMPLE OF WHAT TO DO:**
    - **Step 1 (Input)**: You see `<data_block name="Sales">[{"label": "2023", "value": 100}]</data_block>` in the DataExtractor output.
    - **Step 2 (Action)**: You create a `type: "chart"` component.
    - **Step 3 (Output)**: You output `{"type": "chart", "data": [{"label": "2023", "value": 100}], ...}`.
  - **EXAMPLE OF WHAT NOT TO DO:**
    - **NEVER** put the `<data_block>` string inside a "text" component's content.
  - If you see a `<data_block>`, you **MUST** create a `type: "chart"` component (or a Markdown table if a chart isn't requested).

- **MISSING DATA HANDLING**:
  - If the DataExtractor reports "Data unavailable", "Not provided", or "Error" for a specific section AND you cannot parse a table:
    - **DO NOT** output a "chart" component.
    - **MUST** output a "text" component with `layout: "half"` (or "full" if appropriate).
    - Content should be: "> ⚠️ **Data Unavailable**: [Reason/Metric Name]. Resource constraints or provider timeout."
    - This ensures the report layout remains consistent even without the chart.
"""

def create_report_orchestrator(token: str, model_name: str = "gemini-2.5-flash", ticker: str = "Unknown", template_id: str = "company_primer") -> Agent:
    """
    Creates a ParallelAgent workflow for report generation.
    1. Parallel: Researcher (Search) + DataExtractor (FactSet)
    2. Sequential: Synthesizer (JSON Builder)
    """
    
    # 1. Define Workers
    researcher = Agent(
        name="MarketResearcher",
        model=model_name,
        instruction=f"Research qualitative factors for {ticker}. {RESEARCHER_INSTRUCTIONS}",
        tools=[google_search]
    )

    # Use the existing factory for the FactSet agent but override instructions to be a pure data fetcher
    # We strip native tools to keep it focused if preferred, but include_native_tools=True is fine.
    data_extractor = create_factset_agent(
        token=token,
        model_name=model_name,
        instruction_override=f"Fetch financial data for {ticker}. {FACTSET_INSTRUCTIONS}\n\n{DATA_EXTRACTOR_INSTRUCTIONS}\n\nIMPORTANT: When you find data for charts (Price, Sales, Revenue Segments), you MUST also include a structured <data_block> in your output with the raw numbers, to ensure the Synthesizer can build the charts accurately.",
        include_native_tools=True,
        enable_loop_guard=False, # Allow retries for robustness
        use_agent_cache=False,
        force_new_connection=True # FORCE NEW CONNECTION to avoid shared session timeouts/conflicts
    )
    # Rename to avoid confusion in logs
    data_extractor.name = "DataExtractor"

    # 2. Sequential Gathering (Modified from Parallel to reduce load/timeouts)
    # User requested to reduce parallelism to fix timeouts.
    parallel_gatherer = SequentialAgent(
        name="DataGathering_Swarm",
        sub_agents=[data_extractor, researcher]
    )

    # 3. Synthesizer
    synthesizer = Agent(
        name="ReportSynthesizer",
        model=model_name, # Use a smart model for synthesis
        instruction=f"Synthesize the report for {ticker}. {SYNTHESIZER_INSTRUCTIONS.replace('{Company}', ticker)}",
        tools=[] # Pure reasoning
    )

    # 4. Orchestrator
    orchestrator = SequentialAgent(
        name="ReportOrchestrator",
        sub_agents=[parallel_gatherer, synthesizer]
    )

    return orchestrator
