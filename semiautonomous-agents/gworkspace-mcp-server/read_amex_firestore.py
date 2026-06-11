from google.cloud import firestore
import os

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"

db = firestore.Client()
collection_name = "amex_statements"

print(f"Reading latest document from {collection_name}...")
try:
    docs = (
        db.collection(collection_name)
        .order_by("period", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )

    found = False
    for doc in docs:
        found = True
        data = doc.to_dict()
        
        txns = data.get("transactions", [])
        if txns:
            # Sort by date descending
            txns.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            print("Last 4 transactions:")
            print("| Date | Description | Amount | Card Member |")
            print("|---|---|---|---|")
            for t in txns[:4]:
                print(f"| {t.get('date')} | {t.get('description')} | ${t.get('amount')} | {t.get('card_member')} |")
        else:
            print("No transactions found.")
        break

    if not found:
        print("No statements found.")
except Exception as e:
    print(f"Error: {e}")
