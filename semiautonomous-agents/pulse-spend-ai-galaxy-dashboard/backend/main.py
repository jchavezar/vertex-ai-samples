import os
import json
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from services.analytics_service import AnalyticsService
from services.ai_service import AIService
from services.enrichment_service import process_csv_dataframe

app = FastAPI(title="PulseSpend AI Analytics API", version="1.0.0")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "data", "enriched_dataset.json")

ENRICHED_DATA_PATH = os.environ.get("ENRICHED_DATA_PATH", DEFAULT_DATA_PATH)

# Services
analytics_service: Optional[AnalyticsService] = None
ai_service: Optional[AIService] = None
cached_audit_report: Optional[Dict[str, Any]] = None

@app.on_event("startup")
def startup_event():
    global analytics_service, ai_service
    if os.path.exists(ENRICHED_DATA_PATH):
        analytics_service = AnalyticsService(ENRICHED_DATA_PATH)
        print(f"Loaded dataset from {ENRICHED_DATA_PATH} with {len(analytics_service.records)} records")
    else:
        print(f"Warning: {ENRICHED_DATA_PATH} not found yet.")
    
    try:
        ai_service = AIService()
    except Exception as e:
        print(f"AI Service initialization error: {e}")

class ChatRequest(BaseModel):
    query: str

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "data_loaded": analytics_service is not None,
        "record_count": len(analytics_service.records) if analytics_service else 0,
        "ai_ready": ai_service is not None
    }

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    global analytics_service, cached_audit_report
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file format: {str(e)}")

    required_cols = ['Date', 'Description', 'Amount']
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required Amex CSV column: {col}")

    # Process & enrich dataset
    process_csv_dataframe(df, ENRICHED_DATA_PATH)
    analytics_service = AnalyticsService(ENRICHED_DATA_PATH)
    cached_audit_report = None  # Reset cached audit report for new data

    return {
        "message": f"Successfully uploaded and enriched {len(df)} transactions from {file.filename}",
        "kpis": analytics_service.get_summary_kpis()
    }

@app.get("/api/transactions")
def get_transactions(
    card_member: Optional[str] = None,
    category: Optional[str] = None,
    expense_type: Optional[str] = None,
    search: Optional[str] = None
):
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    
    txs = analytics_service.records
    if card_member:
        txs = [t for t in txs if t['card_member'].lower() == card_member.lower()]
    if category:
        txs = [t for t in txs if t['primary_category'].lower() == category.lower()]
    if expense_type:
        txs = [t for t in txs if t['expense_type'].lower() == expense_type.lower()]
    if search:
        s = search.lower()
        txs = [t for t in txs if s in t['clean_merchant'].lower() or s in t['raw_description'].lower() or s in t['primary_category'].lower()]
        
    return txs

@app.get("/api/kpis")
def get_kpis():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_summary_kpis()

@app.get("/api/analytics/categories")
def get_categories():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_category_breakdown()

@app.get("/api/analytics/expense-types")
def get_expense_types():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_expense_type_breakdown()

@app.get("/api/analytics/cardholders")
def get_cardholders():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_cardholder_comparison()

@app.get("/api/analytics/merchants")
def get_merchants(top_n: int = 15):
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_merchant_leaderboard(top_n=top_n)

@app.get("/api/analytics/timeline")
def get_timeline():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_daily_timeline()

@app.get("/api/analytics/tags")
def get_tags():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_tags_distribution()

@app.get("/api/ai/audit-report")
def get_audit_report(force_refresh: bool = False):
    global cached_audit_report
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    if not ai_service:
        raise HTTPException(status_code=500, detail="AI service not initialized")

    if cached_audit_report and not force_refresh:
        return cached_audit_report

    kpis = analytics_service.get_summary_kpis()
    categories = analytics_service.get_category_breakdown()
    cardholders = analytics_service.get_cardholder_comparison()
    top_merchants = analytics_service.get_merchant_leaderboard(top_n=10)

    try:
        report = ai_service.generate_spending_audit_report(kpis, categories, cardholders, top_merchants)
        cached_audit_report = report
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI audit report: {str(e)}")

@app.post("/api/ai/chat")
def chat_ai(req: ChatRequest):
    if not analytics_service or not ai_service:
        raise HTTPException(status_code=500, detail="Services not ready")

    kpis = analytics_service.get_summary_kpis()
    categories = analytics_service.get_category_breakdown()
    cardholders = analytics_service.get_cardholder_comparison()
    merchants = analytics_service.get_merchant_leaderboard(10)
    
    summary_context = f"""
KPIs: Total Gross ${kpis['total_gross']}, Net ${kpis['total_net']}, Refunds ${kpis['total_refunds']}, Avg Tx ${kpis['avg_transaction']}.
Cardholders Breakdown: {json.dumps(cardholders)}.
Top Categories: {json.dumps(categories[:5])}
Top Merchants: {json.dumps(merchants[:5])}
Sample dataset transactions: {len(analytics_service.records)} records total.
"""
    try:
        reply = ai_service.answer_spending_query(req.query, summary_context)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
