#!/usr/bin/env python3
"""
Direct Data Store Search Tester for Federated Connectors (SharePoint)
Demonstrates that search and document retrieval work directly on Data Stores
without requiring a Gemini Enterprise App or Engine.
"""

import os
import sys
import json
import argparse
import requests
import google.auth
import google.auth.transport.requests

DEFAULT_PROJECT_NUMBER = "545964020693"
DEFAULT_CONNECTOR_ID = "sharepoint-data-def-connector"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

def get_gcp_token():
    """Obtain a valid GCP access token via Application Default Credentials (ADC)."""
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token

def search_datastore(project_number: str, datastore_id: str, query: str, page_size: int = 5):
    """Execute a direct search against a specific Data Store serving config."""
    token = get_gcp_token()
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/"
        f"locations/global/collections/default_collection/dataStores/{datastore_id}/"
        f"servingConfigs/default_search:search"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_number,
    }
    payload = {
        "query": query,
        "pageSize": page_size
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if not resp.ok:
        print(f"[-] Request failed with status {resp.status_code}: {resp.text}")
        return []

    data = resp.json()
    return data.get("results", [])

def main():
    parser = argparse.ArgumentParser(description="Test direct search on Federated Connector Data Stores")
    parser.add_argument("--project-number", default=DEFAULT_PROJECT_NUMBER, help="GCP Project Number")
    parser.add_argument("--connector-id", default=DEFAULT_CONNECTOR_ID, help="Data Connector ID")
    parser.add_argument("--entity", default="file", choices=ENTITY_TYPES + ["all"], help="Entity type to search")
    parser.add_argument("--query", default="jennifer", help="Search query string")
    parser.add_argument("--page-size", type=int, default=3, help="Number of results to return")
    args = parser.parse_args()

    entities_to_query = ENTITY_TYPES if args.entity == "all" else [args.entity]

    print("=" * 80)
    print(f"[*] DIRECT DATASTORE SEARCH TEST (Query: '{args.query}')")
    print(f"[*] Project Number: {args.project_number}")
    print(f"[*] Connector ID:   {args.connector_id}")
    print("=" * 80)

    total_found = 0
    for et in entities_to_query:
        ds_id = f"{args.connector_id}_{et}"
        print(f"\n--- Searching Data Store: {ds_id} ---")
        results = search_datastore(args.project_number, ds_id, args.query, args.page_size)
        total_found += len(results)
        print(f"[+] Returned {len(results)} document(s)")

        for idx, item in enumerate(results, 1):
            doc = item.get("document", {})
            struct = doc.get("structData", {})
            title = struct.get("title", "Untitled")
            author = struct.get("author", "Unknown")
            url = struct.get("url", "N/A")
            desc = struct.get("description", "")[:100]
            print(f"  Result #{idx}:")
            print(f"    Title:  {title}")
            print(f"    Author: {author}")
            print(f"    URL:    {url}")
            if desc:
                print(f"    Snippet: {desc}...")

    print("\n" + "=" * 80)
    print(f"[SUMMARY] Total matching documents retrieved across queried DataStores: {total_found}")
    print("=" * 80)

if __name__ == "__main__":
    main()
