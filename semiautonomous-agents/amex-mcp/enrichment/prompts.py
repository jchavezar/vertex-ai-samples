"""Prompt templates for Gemini enrichment stages."""

CATEGORIZE_SYSTEM = (
    "You are a financial transaction categorizer. You analyze credit card "
    "transactions and return structured JSON. Be precise with merchant names "
    "and categories. Always return valid JSON arrays. "
    "Some transactions include web-verified merchant info (verified_merchant, "
    "verified_description, verified_category fields). When present, ALWAYS "
    "use these as the primary source of truth — they come from Google Search "
    "and are more accurate than the raw credit card description."
)

CATEGORIZE_PROMPT = """\
Categorize these credit card transactions. For each transaction, determine:
- enriched_category: one of [Dining, Groceries, Transportation, Travel, Shopping, \
Entertainment, Health, Utilities, Subscriptions, Insurance, Education, Personal Care, \
Home, Gifts, Fees, Other]
- subcategory: a more specific label (e.g., "Fast Food", "Streaming", "Gas Station")
- merchant_clean: clean, human-readable merchant name (e.g., "SQ *JOES PIZZA NYC" -> "Joe's Pizza")
- confidence: 0.0 to 1.0 how confident you are in the categorization
- tags: 3-5 lowercase semantic keywords that describe this transaction \
(e.g., ["coffee", "cafe", "beverage", "morning"] or ["rideshare", "uber", "transportation", "commute"])
- merchant_type: one of ["chain", "local", "online", "service", "government", "unknown"]
- purchase_channel: one of ["in_store", "online", "app", "subscription", "phone", "unknown"]
- purpose: one of ["personal", "business", "gift", "travel", "medical", "unknown"]

Transactions:
{transactions_json}

Return a JSON array with one object per transaction, in the same order. Each object:
{{"index": <0-based index>, "enriched_category": "...", "subcategory": "...", \
"merchant_clean": "...", "confidence": 0.95, "tags": ["...", "..."], \
"merchant_type": "...", "purchase_channel": "...", "purpose": "..."}}
"""

SUBSCRIPTION_DETECT_SYSTEM = (
    "You are a financial analyst specializing in recurring charge detection. "
    "Analyze transaction patterns across months to identify subscriptions."
)

SUBSCRIPTION_DETECT_PROMPT = """\
Analyze these transactions across multiple months to identify recurring charges \
(subscriptions, memberships, regular bills).

Candidate recurring merchants and their transaction history:
{candidates_json}

For each confirmed subscription, return:
- merchant: clean merchant name
- amount: typical charge amount
- frequency: "monthly", "annual", or "quarterly"
- category: spending category
- first_seen: earliest date seen (YYYY-MM-DD)
- last_seen: most recent date seen (YYYY-MM-DD)
- status: "active" if seen in last 2 months, else "cancelled"
- annual_cost: estimated yearly cost

Return a JSON array of subscription objects. Only include charges that are clearly \
recurring (not one-time purchases that happen to be at the same merchant).
"""

RECEIPT_QUERY_PROMPT = """\
Generate an optimal Gmail search query to find the email receipt for this transaction:
- Description: {description}
- Amount: ${amount}
- Date: {date}

Return JSON: {{"gmail_query": "...", "expected_merchant": "..."}}

The Gmail query should search for receipts, order confirmations, or purchase \
notifications. Use the merchant name, amount, and date range (within 3 days).
"""

RECEIPT_EXTRACT_PROMPT = """\
Extract receipt details from this email for the transaction:
- Transaction: {description}, ${amount}, {date}

Email body:
{email_body}

Return JSON:
{{"receipt_found": true/false, "merchant_name": "...", \
"items": [{{"name": "...", "amount": 0.00}}], "order_id": "...", "total": 0.00}}

If the email is not a receipt for this transaction, set receipt_found to false.
"""

INSIGHTS_SYSTEM = (
    "You are a personal finance analyst. Generate concise, actionable insights "
    "about spending patterns. Be specific with numbers and percentages."
)

INSIGHTS_PROMPT = """\
Analyze this month's spending and generate insights.

Current month ({period}):
- Total spend: ${total_spend}
- Category breakdown: {category_breakdown_json}
- Top merchants: {top_merchants_json}

Prior month comparison:
{comparison_json}

Generate:
- highlights: 3-5 key observations about this month's spending (specific, with numbers)
- anomalies: any unusual charges or spending spikes (with severity: low/medium/high)
- trends: 2-3 multi-month trends

Return JSON: {{"highlights": ["..."], "anomalies": [{{"description": "...", \
"severity": "..."}}], "trends": ["..."]}}
"""

RECOMMENDATIONS_SYSTEM = (
    "You are a personal finance advisor. Give practical, specific recommendations "
    "based on actual spending data. Focus on actionable savings opportunities."
)

RECOMMENDATIONS_PROMPT = """\
Based on this spending profile, generate financial recommendations.

Monthly spending summaries (last {num_months} months):
{summaries_json}

Active subscriptions:
{subscriptions_json}

Recent anomalies:
{anomalies_json}

Generate:
- recommendations: 3-5 actionable suggestions with estimated savings
- subscription_audit: review each subscription — keep, cancel, or downgrade
- spending_score: 1-100 overall financial health score
- score_explanation: why this score

Return JSON:
{{"recommendations": [{{"title": "...", "description": "...", \
"potential_savings": 0.00, "priority": "high/medium/low"}}], \
"subscription_audit": [{{"merchant": "...", "suggestion": "keep/cancel/downgrade", \
"reason": "..."}}], "spending_score": 75, "score_explanation": "..."}}
"""

SEARCH_SYSTEM = (
    "You interpret natural language transaction searches into structured filters."
)

SEARCH_PROMPT = """\
Convert this natural language search into transaction filters.
Query: "{query}"

Available filter fields:
- description_pattern: regex pattern to match transaction description
- min_amount / max_amount: amount range
- category: category name to match
- date_after / date_before: YYYY-MM-DD date range
- merchant_pattern: regex for merchant name

Return JSON with only the relevant filters:
{{"description_pattern": "...", "min_amount": 0, "max_amount": 0, \
"category": "...", "date_after": "...", "date_before": "...", \
"merchant_pattern": "..."}}

Only include filters that the query implies. Omit unused filters.
"""
