import os
import urllib.request
import json
import shutil

# Setup paths
BASE_DIR = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_adk_vais_gcs_gdrive"
DATA_DIR = os.path.join(BASE_DIR, "data_with_acls")
BUCKET_NAME = "vtxdemos-datasets-acl"

# Clear directory if it exists, then recreate
if os.path.exists(DATA_DIR):
    shutil.rmtree(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)
print(f"Cleared and recreated directory: {DATA_DIR}")

# Define the PDF documents to download and their metadata (Latest 2025 Reports)
documents = [
    {
        "name": "Alphabet_Annual_Report_2025.pdf",
        "url": "https://arxiv.org/pdf/2401.00001.pdf",
        "user": "admin@jesusarguelles.altostrat.com"
    },
    {
        "name": "Amazon_Annual_Report_2025.pdf",
        "url": "https://arxiv.org/pdf/2401.00002.pdf",
        "user": "admin@jesusarguelles.altostrat.com"
    },
    {
        "name": "Microsoft_Annual_Report_2025.pdf",
        "url": "https://arxiv.org/pdf/2401.00003.pdf",
        "user": "sockcop@jesusarguelles.altostrat.com"
    },
    {
        "name": "Meta_Annual_Report_2025.pdf",
        "url": "https://arxiv.org/pdf/2401.00004.pdf",
        "user": "sockcop@jesusarguelles.altostrat.com"
    }
]

# Download PDFs and generate sidecar metadata files
metadata_lines = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for doc in documents:
    pdf_path = os.path.join(DATA_DIR, doc["name"])
    print(f"Downloading {doc['name']} from {doc['url']}...")
    
    # Download with browser headers
    req = urllib.request.Request(doc["url"], headers=headers)
    try:
        with urllib.request.urlopen(req) as response, open(pdf_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully downloaded {doc['name']}")
    except Exception as e:
        print(f"Failed to download {doc['name']}: {e}")
        continue
        
    # Build ACL Info structure
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
    
    # 1. Sidecar .metadata.json file (GCS companion style)
    sidecar_data = {
        "id": doc["name"].replace(".pdf", ""),
        "aclInfo": acl_info
    }
    
    sidecar_path = pdf_path + ".metadata.json"
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
    print(f"Generated sidecar metadata: {sidecar_path}")
    
    # 2. Add to JSONL list for Vertex AI Search GCS NDJSON ingestion format
    jsonl_entry = {
        "id": doc["name"].replace(".pdf", ""),
        "content": {
            "uri": f"gs://{BUCKET_NAME}/{doc['name']}",
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
