import google.auth
import google.auth.transport.requests
import requests
import json
import time

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    ds_id = "gcs-fin-acl-v3"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    import_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/{ds_id}/branches/0/documents:import"
    
    import_payload = {
        "gcsSource": {
            "inputUris": [
                "gs://vtxdemos-datasets-acl/metadata.jsonl"
            ],
            "dataSchema": "document"
        },
        "reconciliationMode": "FULL"
    }
    
    print(f"Triggering GCS import in RECONCILE mode for datastore '{ds_id}'...")
    r = requests.post(import_url, headers=headers, json=import_payload)
    print(f"Status Code: {r.status_code}")
    if r.status_code in [200, 202]:
        print("Success! Import operation initiated:")
        response_data = r.json()
        print(json.dumps(response_data, indent=2))
        
        # Save the operation name to scratch/check_import.py for easy tracking
        op_name = response_data.get("name")
        if op_name:
            print(f"Operation Name: {op_name}")
            update_check_script(op_name)
    else:
        print("Failed to trigger import:")
        print(r.text)

def update_check_script(op_name):
    check_script_path = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_adk_vais_gcs_gdrive/scratch/check_import.py"
    try:
        with open(check_script_path, "r") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if "op_name = " in line:
                new_lines.append(f"    op_name = \"{op_name}\"\n")
            else:
                new_lines.append(line)
                
        with open(check_script_path, "w") as f:
            f.writelines(new_lines)
        print(f"Updated check_import.py with active operation ID: {op_name}")
    except Exception as e:
        print(f"Could not update check_import.py: {e}")

if __name__ == "__main__":
    main()
