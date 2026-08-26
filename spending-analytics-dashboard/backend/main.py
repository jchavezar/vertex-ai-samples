import os
import io
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from services.analytics_service import AnalyticsService
from services.enrichment_service import process_csv_dataframe
from services.ai_service import AIService
from services.semantic_search_service import SemanticSearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Amex Spending Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRIMARY_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "enriched_dataset.json")
ENRICHED_DATA_PATH = PRIMARY_DATA_PATH

analytics_service: Optional[AnalyticsService] = AnalyticsService(ENRICHED_DATA_PATH) if os.path.exists(ENRICHED_DATA_PATH) else None
ai_service: Optional[AIService] = None
semantic_search_service: Optional[SemanticSearchService] = None
cached_audit_report: Optional[dict] = None


# Global Receipt Agent instance & cache
receipt_agent: Optional[Any] = None
receipt_cache: Dict[str, Any] = {}

def get_receipt_agent():
    global receipt_agent
    if not receipt_agent:
        from services.adk_receipt_agent import ReceiptAgentOrchestrator
        receipt_agent = ReceiptAgentOrchestrator()
    return receipt_agent

def get_semantic_search():
    global semantic_search_service
    if not semantic_search_service:
        semantic_search_service = SemanticSearchService()
    return semantic_search_service

async def run_parallel_pipeline_async(transactions: List[Dict[str, Any]], concurrency: int = 8):
    agent = get_receipt_agent()
    search_svc = get_semantic_search()
    
    # Run 8x ADK Subagents and Vertex AI Vector Embedding Agent concurrently in the same job
    await asyncio.gather(
        agent.run_parallel_batch_pipeline(transactions, concurrency=concurrency, receipt_cache=receipt_cache),
        asyncio.to_thread(search_svc.rebuild_index)
    )

def run_pipeline_task(transactions: List[Dict[str, Any]], concurrency: int = 8):
    asyncio.run(run_parallel_pipeline_async(transactions, concurrency))

@app.on_event("startup")
def startup_event():
    global analytics_service, ai_service, semantic_search_service
    if os.path.exists(ENRICHED_DATA_PATH):
        analytics_service = AnalyticsService(ENRICHED_DATA_PATH)
        logger.info(f"Loaded {len(analytics_service.records)} records from {ENRICHED_DATA_PATH}")
    else:
        logger.warning(f"Enriched dataset not found at {ENRICHED_DATA_PATH}")

    try:
        ai_service = AIService()
    except Exception as e:
        logger.warning(f"Could not initialize AIService: {e}")

    try:
        semantic_search_service = SemanticSearchService()
        logger.info("Initialized Vertex AI text-embedding-004 Semantic Vector Engine.")
    except Exception as e:
        logger.warning(f"Could not initialize SemanticSearchService: {e}")


@app.get("/api/search/semantic")
def search_semantic(
    q: str = Query(..., description="Natural language semantic search query"),
    top_k: int = Query(50, description="Max results to return"),
    threshold: float = Query(0.35, description="Similarity threshold")
):
    """Contextual semantic search powered by Vertex AI text-embedding-004 and local matrix multiplication."""
    svc = get_semantic_search()
    results = svc.search(q, top_k=top_k, similarity_threshold=threshold)
    return results


@app.post("/api/upload-csv")
@app.post("/api/upload")
async def upload_statements(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    run_pipeline: bool = Form(True)
):
    global analytics_service, cached_audit_report, semantic_search_service
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    dfs = []
    file_names = []

    for f in files:
        contents = await f.read()
        try:
            temp_df = pd.read_csv(io.BytesIO(contents))
            required_cols = ['Date', 'Description', 'Amount']
            for col in required_cols:
                if col not in temp_df.columns:
                    raise HTTPException(status_code=400, detail=f"File {f.filename} is missing required column: {col}")
            dfs.append(temp_df)
            file_names.append(f.filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading {f.filename}: {str(e)}")

    combined_df = pd.concat(dfs, ignore_index=True)
    process_csv_dataframe(combined_df, ENRICHED_DATA_PATH)
    analytics_service = AnalyticsService(ENRICHED_DATA_PATH)
    cached_audit_report = None

    if semantic_search_service:
        background_tasks.add_task(semantic_search_service.rebuild_index)

    agent = get_receipt_agent()
    from services.adk_receipt_agent import add_trace

    if run_pipeline and analytics_service.records:
        background_tasks.add_task(run_pipeline_task, analytics_service.records, 8)
    else:
        add_trace("STORAGE_LOAD", f"⚡ Preserved {len(agent.receipt_cache)} existing agent extractions from persistent disk storage (receipts_cache.json). Instant loading complete with 0 redundant API calls.", "SUCCESS", "STORAGE")

    return {
        "message": f"Successfully merged & enriched {len(combined_df)} raw records ({len(analytics_service.records)} unique deduplicated transactions) from {len(file_names)} statement(s): {', '.join(file_names)}",
        "statement_count": len(file_names),
        "total_records": len(analytics_service.records),
        "persisted_receipts_loaded": len(agent.receipt_cache),
        "kpis": analytics_service.get_summary_kpis()
    }


@app.get("/api/analytics/subscriptions")
def get_subscriptions():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_subscriptions_analysis()


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
    return analytics_service.get_merchant_leaderboard(top_n)


@app.get("/api/analytics/timeline")
def get_timeline(freq: str = 'W'):
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_spend_timeline(freq)


@app.get("/api/analytics/tags")
def get_tags():
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return analytics_service.get_tag_cloud()


@app.get("/api/ai/audit-report")
def get_ai_audit_report(force_refresh: bool = False):
    global cached_audit_report
    if not analytics_service or not ai_service:
        raise HTTPException(status_code=500, detail="AI Service not initialized")

    if cached_audit_report and not force_refresh:
        return cached_audit_report

    kpis = analytics_service.get_summary_kpis()
    categories = analytics_service.get_category_breakdown()
    cardholders = analytics_service.get_cardholder_comparison()
    top_merchants = analytics_service.get_merchant_leaderboard(10)

    try:
        report = ai_service.generate_spending_audit_report(
            kpis=kpis,
            categories=categories,
            cardholders=cardholders,
            top_merchants=top_merchants
        )
        cached_audit_report = report
        return report
    except Exception as e:
        logger.error(f"Error generating AI audit report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI Audit: {str(e)}")


class AskAIRequest(BaseModel):
    question: str
    cardholder: Optional[str] = "ALL"
    history: Optional[List[Dict[str, str]]] = []

@app.post("/api/ai/ask")
def ask_ai(req: AskAIRequest):
    if not analytics_service or not ai_service:
        raise HTTPException(status_code=500, detail="AI Service not initialized")

    txs = analytics_service.records
    if req.cardholder and req.cardholder != 'ALL':
        txs = [t for t in txs if t['card_member'].lower() == req.cardholder.lower()]

    try:
        answer = ai_service.ask_natural_language_question(
            question=req.question,
            transactions=txs,
            kpis=analytics_service.get_summary_kpis(),
            history=req.history
        )
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in ask_ai: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/gmail/status")
def get_gmail_status():
    from services.gmail_service import GmailService
    svc = GmailService()
    return svc.get_status()


class GmailAuthCode(BaseModel):
    code: str

@app.post("/api/auth/gmail/exchange")
def exchange_gmail_code(payload: GmailAuthCode):
    from services.gmail_service import GmailService
    svc = GmailService()
    try:
        res = svc.exchange_code_for_tokens(payload.code)
        return res
    except Exception as e:
        logger.error(f"Failed to exchange Gmail code: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/gmail/disconnect")
def disconnect_gmail():
    from services.gmail_service import GmailService
    svc = GmailService()
    return svc.disconnect()


@app.get("/api/pipeline/traces")
@app.get("/api/agent/traces")
def get_pipeline_traces():
    from services.adk_receipt_agent import get_traces
    return get_traces()


@app.get("/api/agent/pipeline-status")
def get_agent_pipeline_status():
    from services.adk_receipt_agent import get_pipeline_status
    return get_pipeline_status()


@app.post("/api/agent/start-parallel-pipeline")
def start_parallel_pipeline(background_tasks: BackgroundTasks, concurrency: int = 8):
    if analytics_service and analytics_service.records:
        background_tasks.add_task(run_pipeline_task, analytics_service.records, concurrency)
        return {"status": "started", "concurrency": concurrency, "total": len(analytics_service.records)}
    return {"status": "error", "message": "No transactions loaded"}


@app.post("/api/agent/stop-parallel-pipeline")
def stop_parallel_pipeline():
    agent = get_receipt_agent()
    agent.stop_pipeline()
    return {"status": "stopped"}


@app.post("/api/agent/clear-traces")
def clear_agent_traces():
    from services.adk_receipt_agent import clear_traces
    return clear_traces()



@app.get("/api/receipts/deep/{transaction_id}")
def get_deep_receipt_detail(transaction_id: str):
    agent = get_receipt_agent()
    tx = None
    if analytics_service:
        for t in analytics_service.records:
            if t['id'] == transaction_id:
                tx = t
                break
    
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    res = agent.get_or_fetch_receipt_for_tx(tx)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
