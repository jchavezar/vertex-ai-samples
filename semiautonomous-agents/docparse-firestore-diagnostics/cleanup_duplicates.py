import google.auth
import google.auth.transport.requests
import requests

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    # 1. Unlink older datastores from engine docparse_1780161524773
    engine_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/docparse_1780161524773"
    r = requests.get(engine_url, headers=headers)
    if r.status_code == 200:
        orig = r.json()
        new_ids = ["docparse-firestore-mcp-1780165632_mcp_data"]
        patch_body = {
            "name": orig["name"],
            "displayName": orig["displayName"],
            "dataStoreIds": new_ids
        }
        patch_url = f"{engine_url}?updateMask=dataStoreIds"
        print(f"Unlinking older datastores from engine... setting to {new_ids}")
        patch_r = requests.patch(patch_url, headers=headers, json=patch_body)
        print(f"Engine Patch Response ({patch_r.status_code}): {patch_r.text[:500]}")
    else:
        print(f"Error fetching engine: {r.status_code} - {r.text}")

    # 2. Delete the older data connector docparse-firestore-mcp-1780162342
    conn_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/docparse-firestore-mcp-1780162342/dataConnector"
    print("Deleting older data connector docparse-firestore-mcp-1780162342...")
    del_r = requests.delete(conn_url, headers=headers)
    print(f"Delete Connector Response ({del_r.status_code}): {del_r.text[:500]}")

    # 3. Delete the older datastore docparse-firestore-mcp-1780162342_mcp_data
    ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/docparse-firestore-mcp-1780162342_mcp_data"
    print("Deleting older datastore docparse-firestore-mcp-1780162342_mcp_data...")
    del_ds_r = requests.delete(ds_url, headers=headers)
    print(f"Delete Datastore Response ({del_ds_r.status_code}): {del_ds_r.text[:500]}")

    # 4. Delete docparse-firestore-mcp-1780162063 datastore if it exists and is unused
    ds_url2 = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/dataStores/docparse-firestore-mcp-1780162063"
    print("Deleting older datastore docparse-firestore-mcp-1780162063...")
    del_ds2_r = requests.delete(ds_url2, headers=headers)
    print(f"Delete Datastore 2 Response ({del_ds2_r.status_code}): {del_ds2_r.text[:500]}")

if __name__ == "__main__":
    main()
