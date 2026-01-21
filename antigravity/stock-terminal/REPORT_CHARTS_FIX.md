# Report Generator Charts Fix (2026-01-21)

## Issue
Charts in the **Reports Generator** (e.g., Sales History, Revenue Segments) were failing to render, displaying **"Data Unavailable"** errors.

## Root Cause
The `DataExtractor` agent was designed with **"Interactive Scoping"** rules to prevent fetching too much data for broad queries (e.g., "Analyze GOOGL"). 
When the Report Generator sent a broad prompt like "Analyze GOOGL", the agent interpreted this as a trigger to **ask clarifying questions** (e.g., "Do you want stock performance or news?") instead of fetching the data immediately.
Since the `ReportSynthesizer` expects immediate data output (in `<data_block>` tags), the "conversation" response resulted in missing data.

## Solution
We implemented a **CRITICAL OVERRIDE** in the `DATA_EXTRACTOR_INSTRUCTIONS` within `backend/report_agent.py`.

### Code Reference (`backend/report_agent.py`)

We added Section 0 to the instructions to explicitly disable user interaction for the Report Generator context:

```python
DATA_EXTRACTOR_INSTRUCTIONS = """
### 0. OVERRIDE: NO INTERACTIVE SCOPING (CRITICAL)
You are in "Report Mode" and have been assigned a "Deep Dive" task.
The user has ALREADY authorized "Full Analysis".
*   **IGNORE** any "Interactive Scoping" rules that ask you to clarify broad requests.
*   **EXECUTE** the tool calls below IMMEDIATELY.
*   **DO NOT** ask questions. START FETCHING.

You are a Quantitative Data Analyst.
...
```

## How to Verify
1.  Go to **Reports Generator** in the UI.
2.  Enter a ticker (e.g., `GOOGL`).
3.  Select **Company Primer**.
4.  Click **Generate Report**.
5.  Wait ~60s.
6.  **Success**: Charts ("Sales History", "Revenue Segments") appear visually.

## Update: 'Raw Output' JSON Fix (2026-01-21)

### Issue
Occasionally, the Report Generator would display a large block of **"Raw Output"** text containing the JSON instead of rendering the report components.

### Root Cause
The agents sometimes returned "chatty" responses (e.g., "Here is the report: { ... }"). The backend's `json.loads(clean_text)` would fail on this extra text. Although a regex search for the JSON block existed, the code **ignored the regex match** and attempted to parse the full dirty text again, triggering the fallback.

### Solution (`backend/main.py`)
Updated the JSON extraction logic in `generate_report` to correctly prioritize the **regex match** when direct parsing fails.

```python
# Fixed Logic
if json_match:
    try:
        parsed = json.loads(clean_text)
    except:
        # CORRECTLY use the matched group
        parsed = json.loads(json_match.group(0))
```

### Verification
- **Verified**: 2026-01-21
- **Test**: End-to-end report generation with `MSFT`.
- **Result**: Report rendered correctly with no "Raw Output" fallback.
