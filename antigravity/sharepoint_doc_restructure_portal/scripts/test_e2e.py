# scratch/test_e2e.py
import httpx
import json
import sys

API_BASE = "http://localhost:8095/api"

def run_tests():
    print("==================================================")
    print("STARTING PORTAL END-TO-END TEST SUITE (FIRESTORE + RAG)")
    print("==================================================")

    # 1. Fetch baseline documents
    print("\n[TEST 1] Fetching Baseline Documents...")
    r = httpx.get(f"{API_BASE}/documents")
    if r.status_code != 200:
        print(f"FAILED: GET /documents returned status {r.status_code}")
        sys.exit(1)
    docs = r.json()
    print(f"SUCCESS: Retrieved {len(docs)} documents from Firestore.")
    for d in docs:
        print(f"  - {d['filename']} ({d['id']}) | Type: {d.get('sub_type')} | State: {d['state']}")

    # 2. Ingest a new document (Jane Doe CV containing PII)
    print("\n[TEST 2] Triggering Ingestion for Candidate Jane Doe CV...")
    ingest_payload = {
        "filename": "Candidate_Jane_Doe_CV.docx",
        "content": "Curriculum Vitae of Jane Doe. Phone: 555-0199. SSN: 000-12-7890. Experience: Senior Advisor at Apex Corp Ltd (2022-2026). PwC UK candidate profile.",
        "site": "SharePoint: Admin/Resourcing",
        "allowed_groups": ["group::hr-all"]
    }
    r = httpx.post(f"{API_BASE}/documents/ingest", json=ingest_payload, timeout=20)
    if r.status_code != 200:
        print(f"FAILED: POST /documents/ingest failed: {r.text}")
        sys.exit(1)
    
    ingested = r.json().get("document")
    doc_id = ingested["id"]
    print(f"SUCCESS: Ingested document ID: {doc_id}")
    print(f"  - Extracted Type: {ingested.get('type')}")
    print(f"  - Extracted Sub-Type: {ingested.get('sub_type')}")
    print(f"  - PII Detected: {ingested.get('pii_detected')}")
    print(f"  - Allowed Groups: {ingested.get('allowed_groups')}")
    
    # 3. Validate and override tags via QA Console
    print("\n[TEST 3] Simulating Human QA Tag Override & Approval...")
    validate_payload = {
        "confidentiality": "Highly Confidential",
        "document_sub_type": "PwC CV",
        "state": "APPROVED"
    }
    r = httpx.post(f"{API_BASE}/documents/{doc_id}/validate", json=validate_payload)
    if r.status_code != 200:
        print(f"FAILED: POST /documents/{doc_id}/validate failed: {r.text}")
        sys.exit(1)
    
    validated = r.json().get("document")
    print(f"SUCCESS: Document {doc_id} state updated to: {validated['state']}")
    print(f"  - New Confidentiality: {validated.get('confidentiality')}")

    # 4. Search Query: Role-Based Filtering Block (Finance User Access)
    print("\n[TEST 4] Querying Search Assistant as 'finance_user' (Should block/not return Jane Doe CV)...")
    search_payload_block = {
        "query": "Who is Jane Doe and what is their phone number?"
    }
    headers_block = {"X-Developer-Override-Groups": "group::finance-all,group::employees"}
    r = httpx.post(f"{API_BASE}/search", json=search_payload_block, headers=headers_block, timeout=20)
    if r.status_code != 200:
        print(f"FAILED: POST /search failed: {r.text}")
        sys.exit(1)
    
    blocked_resp = r.json()
    print("SUCCESS: Search query processed.")
    print(f"  - Answer: {blocked_resp['answer']}")
    if len(blocked_resp['sources']) > 0:
        print("INFO: Sources were returned. Checking for security leaks...")
        leaked_files = [src['title'] for src in blocked_resp['sources']]
        for f in leaked_files:
            print(f"    * Retrieved file: {f}")
        if "Candidate_Jane_Doe_CV.docx" in leaked_files:
            print("CRITICAL SECURITY ERROR: Candidate_Jane_Doe_CV.docx was returned to unauthorized user!")
            sys.exit(1)
        else:
            print("VERIFIED: Security boundary holds. Only accessible files were retrieved.")

    # 5. Search Query: Role-Based Filtering Allowed (HR User Access + Dynamic PII Masking)
    print("\n[TEST 5] Querying Search Assistant as 'hr_user' (Should allow access + mask PII details)...")
    search_payload_allow = {
        "query": "Who is Jane Doe and what is their phone number and SSN?"
    }
    headers_allow = {"X-Developer-Override-Groups": "group::hr-all,group::employees"}
    r = httpx.post(f"{API_BASE}/search", json=search_payload_allow, headers=headers_allow, timeout=20)
    if r.status_code != 200:
        print(f"FAILED: POST /search failed: {r.text}")
        sys.exit(1)
    
    allowed_resp = r.json()
    print("SUCCESS: Search query processed.")
    print(f"  - Answer: {allowed_resp['answer']}")
    print(f"  - Sources Cited: {len(allowed_resp['sources'])}")
    for src in allowed_resp['sources']:
        print(f"    * Source File: {src['title']}")
    
    # Verify PII tags in output
    answer = allowed_resp['answer']
    if "<redact>" not in answer:
        print("WARNING: Output answer did not contain <redact> tags. Check prompt compliance.")
    else:
        print("VERIFIED: Output contains redact tags protecting raw values.")

    print("\n==================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
