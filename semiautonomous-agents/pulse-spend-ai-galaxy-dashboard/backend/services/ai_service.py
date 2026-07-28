import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any, List

class AIService:
    def __init__(self):
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'vtxdemos'
        os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        self.model_name = 'gemini-3.5-flash'
        self.client = genai.Client(location='us-central1')

    def generate_spending_audit_report(self, kpis: Dict[str, Any], categories: List[Dict[str, Any]], cardholders: Dict[str, Any], top_merchants: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"""
You are an elite AI Chief Financial Officer and Personal Wealth Strategist.
Analyze this comprehensive 1-month credit card spending dataset for a household consisting of DINORAH GUERRA and JESUS CHAVEZ.

Key Financial Statistics:
- Total Gross Spent: ${kpis['total_gross']:,.2f}
- Total Refunds/Credits: ${kpis['total_refunds']:,.2f}
- Net Total Spent: ${kpis['total_net']:,.2f}
- Total Transactions: {kpis['total_count']}
- Average Transaction Size: ${kpis['avg_transaction']:,.2f}
- Top Spent Merchant: {kpis['top_merchant']} (${kpis['top_merchant_amount']:,.2f})
- Top Spent Category: {kpis['top_category']} (${kpis['top_category_amount']:,.2f})

Category Spend Breakdown:
{json.dumps(categories, indent=2)}

Cardholder Comparison:
{json.dumps(cardholders, indent=2)}

Top Spent Merchants:
{json.dumps(top_merchants, indent=2)}

Provide a structured AI Spending Audit in JSON format with the following fields:
1. `spending_persona_title`: A creative, accurate title for this household's spending personality (e.g. "The High-End NYC Gourmet & Fashion Duo")
2. `executive_summary`: 2-3 paragraph sharp narrative detailing where money is going.
3. `detected_patterns`: Array of 4-5 specific, insightful patterns detected by AI (e.g., food delivery frequency, travel spend, refund behavior, card member habits). Each item has `title`, `description`, and `severity` ("high", "medium", "info").
4. `top_anomalies`: Array of 2-3 unexpected spending outliers or spikes. Each with `merchant_or_category`, `amount`, and `insight`.
5. `cardholder_insights`: Narrative comparing Dinorah Guerra vs Jesus Chavez spending styles and favorite categories.
6. `actionable_savings_tips`: Array of 4 concrete strategies to reduce spending next month (with estimated monthly savings amount).

Return ONLY valid JSON matching this schema.
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.2
            )
        )
        return json.loads(response.text)

    def answer_spending_query(self, user_query: str, dataset_summary: str) -> str:
        prompt = f"""
You are an expert AI Assistant specializing in personal finance and expense analysis.
You have access to the user's detailed enriched credit card spending dataset summary below:

--- DATASET CONTEXT ---
{dataset_summary}
----------------------

User Question: "{user_query}"

Provide a helpful, precise, friendly, and analytical answer. Use formatting (bullet points, bold text, dollar amounts) where applicable.
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
