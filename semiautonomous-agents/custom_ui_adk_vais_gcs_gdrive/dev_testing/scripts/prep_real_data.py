import os
import shutil
import json

BASE_DIR = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_adk_vais_gcs_gdrive"
DATA_DIR = os.path.join(BASE_DIR, "data_with_acls")
BUCKET_NAME = "vtxdemos-datasets-acl"
DOWNLOADS_DIR = "/Users/jesusarguelles/Downloads"

# Clear data_with_acls directory
if os.path.exists(DATA_DIR):
    shutil.rmtree(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)
print(f"Cleared and recreated directory: {DATA_DIR}")

# Mapping from downloaded file names to clean names and attributes
documents = [
    {
        "source_name": "2026q1-alphabet-earnings-release.pdf",
        "target_name": "Alphabet_Q1_2026_Report.pdf",
        "company": "Alphabet",
        "year": 2026,
        "quarter": "Q1",
        "user": "admin@jesusarguelles.altostrat.com"
    },
    {
        "source_name": "AMZN-Q1-2026-Earnings-Release.pdf",
        "target_name": "Amazon_Q1_2026_Report.pdf",
        "company": "Amazon",
        "year": 2026,
        "quarter": "Q1",
        "user": "admin@jesusarguelles.altostrat.com"
    },
    {
        "source_name": "cdn-dynmedia-1.microsoft.com.pdf",
        "target_name": "Microsoft_Q1_2026_Report.pdf",
        "company": "Microsoft",
        "year": 2026,
        "quarter": "Q1",
        "user": "sockcop@jesusarguelles.altostrat.com"
    },
    {
        "source_name": "Meta-Reports-First-Quarter-2026-Results-2026.pdf",
        "target_name": "Meta_Q1_2026_Report.pdf",
        "company": "Meta",
        "year": 2026,
        "quarter": "Q1",
        "user": "sockcop@jesusarguelles.altostrat.com"
    }
]

metadata_lines = []

for doc in documents:
    src_path = os.path.join(DOWNLOADS_DIR, doc["source_name"])
    dst_path = os.path.join(DATA_DIR, doc["target_name"])
    
    if not os.path.exists(src_path):
        print(f"ERROR: Source file not found in Downloads: {src_path}")
        continue
        
    # Copy file to data_with_acls directory
    shutil.copy2(src_path, dst_path)
    print(f"Copied {doc['source_name']} -> {doc['target_name']}")
    
    # Build ACL structure
    acl_info = {
        "readers": [
            {
                "principals": [
                    {
                        "userId": doc["user"]
                    }
                ]
            }
        ]
    }
    
    # Generate sidecar metadata file (.pdf.metadata.json)
    sidecar_data = {
        "id": doc["target_name"].replace(".pdf", ""),
        "aclInfo": acl_info
    }
    sidecar_path = dst_path + ".metadata.json"
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
    print(f"Generated sidecar metadata: {sidecar_path}")
    
    # Build metadata.jsonl entry (for ingestion into Vertex AI Search)
    jsonl_entry = {
        "id": doc["target_name"].replace(".pdf", ""),
        "structData": {
            "company": doc["company"],
            "year": doc["year"],
            "quarter": doc["quarter"]
        },
        "content": {
            "uri": f"gs://{BUCKET_NAME}/{doc['target_name']}",
            "mimeType": "application/pdf"
        },
        "aclInfo": acl_info
    }
    metadata_lines.append(jsonl_entry)

# Write metadata.jsonl
jsonl_path = os.path.join(DATA_DIR, "metadata.jsonl")
with open(jsonl_path, 'w') as f:
    for entry in metadata_lines:
        f.write(json.dumps(entry) + "\n")
print(f"Generated unified metadata.jsonl: {jsonl_path}")

print("Data preparation complete!")
