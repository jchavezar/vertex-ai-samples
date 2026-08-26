import os
import json
import logging

os.environ['GOOGLE_CLOUD_PROJECT'] = os.environ.get('GOOGLE_CLOUD_PROJECT', 'vtxdemos')
os.environ['GOOGLE_CLOUD_LOCATION'] = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

from google import genai
from google.genai import types
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.project = os.environ.get('GOOGLE_CLOUD_PROJECT', 'vtxdemos')
        self.location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.model_name = 'gemini-2.5-flash'
        self._init_client()

    def _init_client(self):
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location
            )
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client in AIService: {e}")

    def _call_generate_with_retry(self, prompt: str, is_json: bool = False, max_attempts: int = 3):
        for attempt in range(max_attempts):
            try:
                config = types.GenerateContentConfig(
                    response_mime_type='application/json' if is_json else None,
                    temperature=0.2
                ) if is_json else types.GenerateContentConfig(temperature=0.3)
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                return response
            except Exception as e:
                logger.warning(f"AIService generate_content attempt {attempt+1} failed: {e}. Re-instantiating client...")
                self._init_client()
                if attempt == max_attempts - 1:
                    raise e


    def generate_spending_audit_report(self, kpis: Dict[str, Any], categories: List[Dict[str, Any]], cardholders: Dict[str, Any], top_merchants: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"""
You are an elite AI Chief Financial Officer and Personal Wealth Strategist.
Analyze this comprehensive credit card spending dataset for a household.

Key Financial Statistics:
- Total Gross Spent: ${kpis.get('total_gross', 0):,.2f}
- Total Refunds/Credits: ${kpis.get('total_refunds', 0):,.2f}
- Net Total Spent: ${kpis.get('total_net', 0):,.2f}
- Total Transactions: {kpis.get('total_count', 0)}
- Average Transaction Size: ${kpis.get('avg_transaction', 0):,.2f}
- Top Spent Merchant: {kpis.get('top_merchant', 'N/A')} (${kpis.get('top_merchant_amount', 0):,.2f})
- Top Spent Category: {kpis.get('top_category', 'N/A')} (${kpis.get('top_category_amount', 0):,.2f})

Category Spend Breakdown:
{json.dumps(categories, indent=2)}

Cardholder Comparison:
{json.dumps(cardholders, indent=2)}

Top Spent Merchants:
{json.dumps(top_merchants, indent=2)}

Provide a deep, highly actionable AI Spending Audit and Cost Optimization report in JSON format with the following exact schema:
{{
  "spending_persona_title": "Creative descriptive title for this household (e.g. 'The High-End NYC Gourmet & Fashion Enthusiasts')",
  "executive_summary": "Comprehensive 2-3 paragraph financial breakdown of where household capital is concentrated, recurring leakages, luxury outflows, and discretionary vs essential ratios.",
  "detected_patterns": [
    {{
      "title": "Specific pattern name (e.g. 'High-Frequency Food Delivery Outflow')",
      "description": "Clear explanation of the spending behavior, frequency, and financial impact.",
      "severity": "high"
    }}
  ],
  "top_anomalies": [
    {{
      "merchant_or_category": "Merchant or Category name",
      "amount": 278.48,
      "insight": "Why this represents an anomaly or spike and what caused it."
    }}
  ],
  "cardholder_insights": "Detailed comparison of card members spending habits, individual category priorities, and contribution to total household outflow.",
  "actionable_savings_tips": [
    {{
      "title": "Clear action step (e.g. 'Cap Food Delivery to 2x Weekly')",
      "description": "Concrete steps to execute this reduction without sacrificing lifestyle quality.",
      "monthly_savings": 320,
      "annual_savings": 3840,
      "category": "Food & Dining",
      "difficulty": "Easy"
    }}
  ],
  "cost_optimization_roadmap": [
    {{
      "phase": "Immediate (Days 1-30)",
      "target": "Quick Wins: Cancel redundant subscriptions and audit return credits",
      "potential_cut": "$250 - $450/month"
    }},
    {{
      "phase": "Mid-Term (Months 2-3)",
      "target": "Behavioral Shifts: Batch food delivery & establish luxury apparel monthly budgets",
      "potential_cut": "$600 - $900/month"
    }}
  ]
}}

Return ONLY valid JSON matching this schema.
"""
        response = self._call_generate_with_retry(prompt, is_json=True)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def answer_spending_query(self, user_query: str, dataset_summary: str) -> str:
        prompt = f"""
You are an expert AI Assistant specializing in personal finance, expense optimization, and credit card analytics.
You have access to the user's detailed enriched credit card spending dataset summary below:

--- DATASET CONTEXT ---
{dataset_summary}
----------------------

User Question: "{user_query}"

Provide a helpful, precise, friendly, and analytical answer. Use formatting (bullet points, bold text, dollar amounts, savings tips) where applicable.
"""
        response = self._call_generate_with_retry(prompt, is_json=False)
        return response.text
