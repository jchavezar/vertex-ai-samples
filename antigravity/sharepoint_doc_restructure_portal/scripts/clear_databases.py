# scratch/clear_databases.py
from google.cloud import firestore
from google.cloud import bigquery

PROJECT_ID = "vtxdemos"

def clear_all():
    print("==================================================")
    print("CLEARING MOCK DATA FROM FIRESTORE AND BIGQUERY")
    print("==================================================")

    # 1. Clear Firestore sharepoint_documents
    print("[FIRESTORE] Clearing collection 'sharepoint_documents'...")
    db = firestore.Client(project=PROJECT_ID)
    docs = list(db.collection("sharepoint_documents").stream())
    for doc in docs:
        doc.reference.delete()
    print(f"Deleted {len(docs)} documents.")

    # 2. Clear Firestore audit_logs
    print("[FIRESTORE] Clearing collection 'audit_logs'...")
    logs = list(db.collection("audit_logs").stream())
    for log in logs:
        log.reference.delete()
    print(f"Deleted {len(logs)} logs.")

    # 3. Clear BigQuery documents_metadata
    print("[BIGQUERY] Truncating table 'documents_metadata'...")
    bq = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.sharepoint_portal_ds.documents_metadata"
    query = f"TRUNCATE TABLE `{table_id}`"
    try:
        bq.query(query).result()
        print("BigQuery table truncated successfully.")
    except Exception as e:
        print(f"BigQuery truncate failed: {e}")

    print("\nDATABASES SUCCESSFULLY PURGED. READY FOR PRODUCTION USE.")
    print("==================================================")

if __name__ == "__main__":
    clear_all()
