#!/usr/bin/env python3
# ==============================================================================
# PIPELINE POC: SHAREPOINT INGESTION & AI ENRICHMENT (GEMINI 3.5 FLASH)
# ==============================================================================
# This script runs the full extraction pipeline for a document:
# 1. Ingestion / Loading
# 2. Multimodal Gemini 3.5 Flash extraction (Structure, Explainability, ACLs)
# 3. Dynamic Ontology Mapping
# 4. DLP PII Redaction Check
# 5. Outputting final index metadata JSON.
# ==============================================================================

import json
import os
import sys
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# --- SCHEMAS (Pydantic models for structured output) ---
class EntityProperty(BaseModel):
    name: str = Field(description="Name of the property (e.g. client_name, liability_limit)")
    value: str = Field(description="Extracted value for this property")
    rationale: str = Field(description="Verbatim evidence text from document justifying this value")
    confidence: float = Field(description="Confidence rating from 0.0 to 1.0")

class ExtractedOntology(BaseModel):
    class_name: str = Field(description="The matching ontology class (e.g. EngagementLetter, Blueprint)")
    properties: List[EntityProperty] = Field(description="List of properties identified")
    relationships: List[str] = Field(description="List of relationships (e.g. 'adheresTo PolicyDocument')")

class IngestionPackage(BaseModel):
    filename: str
    doc_type: str
    customer_scope: str
    allowed_groups: List[str] = Field(description="Microsoft Entra ID groups mapped to this file")
    metadata: ExtractedOntology
    pii_redacted: bool

# --- MOCK DOCUMENT GENERATOR ---
MOCK_CONTRACT_CONTENT = """
================================================================================
TAX ADVISORY ENGAGEMENT LETTER
================================================================================
Client Name: ACME Global Corporation
Target Sector: Heavy Manufacturing

1. Scope of Work
ACME Global Corporation hereby engages advisors to perform transfer pricing analysis 
for fiscal year 2026. All work will comply with manufacturing standard guidelines.

2. Liability Limitation Cap
Except in cases of gross negligence, the total liability under this agreement 
is strictly capped at $5,000,000 (Five Million US Dollars).

3. Access Controls (SharePoint Inherited Groups)
- Restricted to Group: group::finance-all (ID: 3f4db3b8-6874-4b5b-8d02-8f92931a293f)
- Read-All: group::employees

Signed:
John Doe, CFO, ACME Global Corporation (Date: June 9, 2026)
SSN: 000-12-3456 (For billing verification purposes)
"""

def mock_dlp_scan(text: str) -> tuple[str, bool]:
    """Simulates Google Cloud DLP PII scanning and redaction."""
    has_pii = False
    if "000-12-3456" in text or "SSN:" in text:
        text = text.replace("000-12-3456", "[REDACTED SSN]")
        has_pii = True
    return text, has_pii

def run_extraction_pipeline():
    print("======================================================================")
    print("STARTING SHAREPOINT INGESTION PIPELINE POC")
    print("Using Model: gemini-3.5-flash | Region: global")
    print("======================================================================")

    # 1. Run local mock DLP Scan first
    print("[1/4] Running Sensitive Data Protection (DLP API) scan...")
    clean_text, pii_found = mock_dlp_scan(MOCK_CONTRACT_CONTENT)
    if pii_found:
        print(" -> WARNING: PII detected. Redacting content before LLM analysis.")
    else:
        print(" -> OK: No PII identified.")

    # 2. Initialize Gemini Client (Vertex AI mode)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "jchavezar-demo")
    
    print(f"[2/4] Initializing Vertex AI Client (project: {project_id}, location: global)...")
    try:
        client = genai.Client(vertexai=True, project=project_id, location="global")
    except Exception as e:
        print(f"Error initializing Client: {e}")
        print("Make sure you have active Google Cloud credentials in your shell environment.")
        sys.exit(1)

    # 3. Call Gemini to perform Structured Ingestion and Ontology extraction
    prompt = f"""
    Analyze the following document content:
    ---
    {clean_text}
    ---

    Perform extraction:
    1. Classify the document class (e.g. EngagementLetter, TechnicalBlueprint).
    2. Extract key properties (client name, liability limit, dates) alongside evidence/rationale from text.
    3. Mappings: Identify relationships with policy documents.
    4. Extract security groups mentioned under Access Controls section.

    Return JSON only, matching the response schema.
    """

    print("[3/4] Submitting to Gemini 3.5 Flash for Multimodal OCR & Schema Ingestion...")
    
    try:
        resp = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedOntology,
                temperature=0.0
            )
        )
        
        extracted_data = json.loads(resp.text)
        print(" -> Success! Structured extraction complete.")
        
    except Exception as e:
        print(f"Gemini API execution failed: {e}")
        print("Using local mock extraction fallback to complete flow.")
        extracted_data = {
            "class_name": "EngagementLetter",
            "properties": [
                {
                    "name": "client_name",
                    "value": "ACME Global Corporation",
                    "rationale": "Client Name: ACME Global Corporation",
                    "confidence": 0.98
                },
                {
                    "name": "liability_limit",
                    "value": "$5,000,000",
                    "rationale": "total liability under this agreement is strictly capped at $5,000,000",
                    "confidence": 0.96
                }
            ],
            "relationships": ["governedBy PolicyDocument"]
        }

    # 4. Assemble Ingestion Package
    print("[4/4] Packing final index metadata & ACL filters...")
    allowed_groups = ["group::3f4db3b8-6874-4b5b-8d02-8f92931a293f", "group::employees"]
    
    package = IngestionPackage(
        filename="ACME_Global_Tax_Engagement_Letter.pdf",
        doc_type=extracted_data.get("class_name", "Unknown"),
        customer_scope="ACME Global Corporation",
        allowed_groups=allowed_groups,
        metadata=ExtractedOntology(**extracted_data),
        pii_redacted=pii_found
    )

    print("\n======================================================================")
    print("FINAL INGESTION METADATA PACKAGE (Ready for Vector Indexing & BigQuery)")
    print("======================================================================")
    print(json.dumps(package.model_dump(), indent=2))
    print("======================================================================")

if __name__ == "__main__":
    run_extraction_pipeline()
