#!/usr/bin/env python3
"""
Single Unified Tester for SharePoint Federated DataStore Search & AuthN/AuthZ
Demonstrates direct DataStore querying and WIF token validation without a Gemini Enterprise App.
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
DEFAULT_WIF_POOL = "sp-wif-pool-v2"
DEFAULT_WIF_PROVIDER = "entra-provider"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

def get_gcp_token():
    """Obtains valid GCP credentials via Application Default Credentials (ADC)."""
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token

def exchange_entra_jwt(entra_jwt: str, wif_pool: str = DEFAULT_WIF_POOL, wif_provider: str = DEFAULT_WIF_PROVIDER) -> str:
    """Exchanges an Entra ID JWT for a federated GCP token via Google STS."""
    url = "https://sts.googleapis.com/v1/token"
    payload = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{wif_pool}/providers/{wif_provider}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]

def check_connector_token(project_number: str, connector_id: str, gcp_token: str) -> bool:
    """Verifies whether Discovery Engine holds an active SharePoint token for the caller."""
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/{connector_id}/dataConnector:acquireAccessToken"
    headers = {"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json", "X-Goog-User-Project": project_number}
    resp = requests.post(url, headers=headers, json={}, timeout=15)
    return resp.ok and bool(resp.json().get("accessToken"))

def search_datastore(project_number: str, datastore_id: str, query: str, page_size: int = 5, gcp_token: str = None):
    """Executes a direct search against a specific Data Store serving config."""
    token = gcp_token or get_gcp_token()
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/dataStores/{datastore_id}/servingConfigs/default_search:search"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Goog-User-Project": project_number}
    payload = {"query": query, "pageSize": page_size}
    
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if not resp.ok:
        print(f"[-] Error querying {datastore_id} ({resp.status_code}): {resp.text[:200]}")
        return []
    return resp.json().get("results", [])

def main():
    parser = argparse.ArgumentParser(description="SharePoint Federated DataStore Search & Auth Tester")
    parser.add_argument("--query", default="jennifer", help="Search query string")
    parser.add_argument("--entity", default="file", choices=ENTITY_TYPES + ["all"], help="Entity store to query")
    parser.add_argument("--page-size", type=int, default=3, help="Max results per store")
    parser.add_argument("--project-number", default=DEFAULT_PROJECT_NUMBER, help="GCP Project Number")
    parser.add_argument("--connector-id", default=DEFAULT_CONNECTOR_ID, help="Data Connector ID")
    parser.add_argument("--auth-check", action="store_true", help="Perform connector token health check")
    args = parser.parse_args()

    gcp_token = get_gcp_token()

    print("=" * 80)
    print(f"[*] SHAREPOINT FEDERATED DATASTORE DIRECT TEST")
    print(f"[*] Project: {args.project_number} | Connector: {args.connector_id}")
    print("=" * 80)

    if args.auth_check:
        print("\n[*] Validating Connector Token Vault...")
        is_active = check_connector_token(args.project_number, args.connector_id, gcp_token)
        print(f"[+] Connector Token Active: {is_active}")

    entities = ENTITY_TYPES if args.entity == "all" else [args.entity]
    total_results = 0

    for et in entities:
        ds_id = f"{args.connector_id}_{et}"
        print(f"\n--- Searching Data Store: {ds_id} (Query: '{args.query}') ---")
        results = search_datastore(args.project_number, ds_id, args.query, args.page_size, gcp_token)
        total_results += len(results)
        print(f"[+] Found {len(results)} document(s)")

        for idx, item in enumerate(results, 1):
            struct = item.get("document", {}).get("structData", {})
            print(f"  [{idx}] {struct.get('title', 'Untitled')} ({struct.get('file_type', 'file')})")
            print(f"      Author: {struct.get('author', 'Unknown')}")
            print(f"      URL:    {struct.get('url', 'N/A')}")
            desc = struct.get("description", "")
            if desc:
                print(f"      Snippet: {desc[:120]}...")

    print("\n" + "=" * 80)
    print(f"[SUMMARY] Total matching documents retrieved: {total_results}")
    print("=" * 80)

if __name__ == "__main__":
    main()
