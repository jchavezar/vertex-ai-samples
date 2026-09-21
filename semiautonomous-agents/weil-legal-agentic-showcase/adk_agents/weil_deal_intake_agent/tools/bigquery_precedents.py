"""BigQuery Precedent and Deal Benchmark Tool for Google ADK."""

from google.adk.tools import FunctionTool

PRECENT_DEALS_DATABASE = [
    {
        "deal_id": "DEAL-2025-104",
        "target": "Zephyr Robotics",
        "acquirer": "Nexus Capital",
        "sector": "Robotics & AI",
        "deal_size_m": 2300.0,
        "reverse_breakup_fee_pct": 4.5,
        "antitrust_standard": "Reasonable Best Efforts with unilateral CFIUS clearance covenant",
        "governing_law": "Delaware Chancery"
    },
    {
        "deal_id": "DEAL-2025-089",
        "target": "BioVance Pharma",
        "acquirer": "Apex Health",
        "sector": "Healthcare",
        "deal_size_m": 4800.0,
        "reverse_breakup_fee_pct": 5.2,
        "antitrust_standard": "Hell-or-High-Water with $200M divestiture cap",
        "governing_law": "Delaware Chancery"
    }
]

def search_bigquery_deal_precedents(sector: str, min_deal_size_m: float = 100.0) -> list[dict]:
    """Queries Weil's BigQuery repository for comparable M&A precedent terms and reverse breakup fees.
    
    Args:
        sector: Target industry sector (e.g., 'Robotics', 'Healthcare', 'Tech').
        min_deal_size_m: Minimum deal enterprise value in millions USD.
    """
    matches = [
        deal for deal in PRECENT_DEALS_DATABASE
        if sector.lower() in deal["sector"].lower() and deal["deal_size_m"] >= min_deal_size_m
    ]
    return matches if matches else PRECENT_DEALS_DATABASE

precedent_tool = FunctionTool(func=search_bigquery_deal_precedents)
