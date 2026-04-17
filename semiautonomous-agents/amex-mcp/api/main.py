"""FastAPI REST backend for Amex Financial Dashboard."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import statements, transactions, categories, trends, subscriptions, insights

app = FastAPI(title="Amex Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(statements.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(insights.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
