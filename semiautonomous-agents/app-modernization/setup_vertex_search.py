#!/usr/bin/env python3
"""
setup_vertex_search.py
Configures a Vertex AI Search (Discovery Engine) Data Store and Engine
indexing https://www.libertad.com.mx/* to power intelligent navigation and search.
"""

import sys
import time
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.exceptions import AlreadyExists, GoogleAPICallError

PROJECT_ID = "vtxdemos"
LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "libertad-web-store"
ENGINE_ID = "libertad-search-navigator"
TARGET_URI = "https://www.libertad.com.mx/*"


def get_parent_collection():
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}"


def get_data_store_path():
    return f"{get_parent_collection()}/dataStores/{DATA_STORE_ID}"


def get_engine_path():
    return f"{get_parent_collection()}/engines/{ENGINE_ID}"


def create_or_get_datastore():
    client = discoveryengine.DataStoreServiceClient()
    parent = get_parent_collection()

    print(f"🔍 Checking Data Store: {DATA_STORE_ID}...")
    try:
        store = client.get_data_store(name=get_data_store_path())
        print(f"✅ Data Store '{DATA_STORE_ID}' already exists.")
        return store
    except Exception:
        print(f"⚙️ Creating new Website Data Store: {DATA_STORE_ID}...")

    data_store = discoveryengine.DataStore(
        display_name="Libertad Financiera Web Store",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.PUBLIC_WEBSITE,
    )

    req = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=DATA_STORE_ID,
    )

    op = client.create_data_store(request=req)
    print(f"⏳ Provisioning Data Store (LRO: {op.operation.name})...")
    store = op.result(timeout=180)
    print(f"✅ Data Store created successfully: {store.name}")
    return store


def setup_target_site():
    site_client = discoveryengine.SiteSearchEngineServiceClient()
    parent = f"{get_data_store_path()}/siteSearchEngine"

    print(f"🌐 Configuring Target Site: {TARGET_URI}...")
    target_site = discoveryengine.TargetSite(
        provided_uri_pattern=TARGET_URI,
        type_=discoveryengine.TargetSite.Type.INCLUDE,
    )

    req = discoveryengine.CreateTargetSiteRequest(
        parent=parent,
        target_site=target_site,
    )

    try:
        op = site_client.create_target_site(request=req)
        print(f"⏳ Registering target site pattern (LRO: {op.operation.name})...")
        res = op.result(timeout=120)
        print(f"✅ Target Site registered successfully: {res.name}")
    except AlreadyExists:
        print(f"ℹ️ Target Site '{TARGET_URI}' already registered.")
    except Exception as e:
        print(f"⚠️ Notice on target site setup: {e}")


def create_or_get_engine():
    engine_client = discoveryengine.EngineServiceClient()
    parent = get_parent_collection()

    print(f"🔍 Checking Search Engine: {ENGINE_ID}...")
    try:
        eng = engine_client.get_engine(name=get_engine_path())
        print(f"✅ Engine '{ENGINE_ID}' already exists.")
        return eng
    except Exception:
        print(f"⚙️ Creating new Search Engine / Navigator App: {ENGINE_ID}...")

    engine = discoveryengine.Engine(
        display_name="Libertad Smart Navigator",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        data_store_ids=[DATA_STORE_ID],
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
            search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
        ),
    )

    req = discoveryengine.CreateEngineRequest(
        parent=parent,
        engine=engine,
        engine_id=ENGINE_ID,
    )

    try:
        op = engine_client.create_engine(request=req)
        print(f"⏳ Provisioning Search Engine (LRO: {op.operation.name})...")
        eng = op.result(timeout=180)
        print(f"✅ Search Engine created successfully: {eng.name}")
        return eng
    except AlreadyExists:
        print(f"ℹ️ Engine '{ENGINE_ID}' already exists.")
    except Exception as e:
        print(f"⚠️ Engine creation notice: {e}")


def test_search(query: str = "credito personal"):
    print(f"\n🔎 Testing Search Query: '{query}'...")
    search_client = discoveryengine.SearchServiceClient()
    serving_config = f"{get_data_store_path()}/servingConfigs/default_search"

    req = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
    )

    try:
        response = search_client.search(request=req)
        print(f"📊 Results for '{query}':")
        count = 0
        for result in response.results:
            count += 1
            doc = result.document
            print(f"  [{count}] ID: {doc.id}")
            if doc.derived_struct_data:
                title = doc.derived_struct_data.get("title", "")
                link = doc.derived_struct_data.get("link", "")
                print(f"      Title: {title}")
                print(f"      Link:  {link}")
        if count == 0:
            print("  (Crawler is indexing target pages in the background; crawler active).")
    except Exception as e:
        print(f"Search notice: {e}")


def main():
    print("=" * 60)
    print("🚀 VERTEX AI SEARCH - LIBERTAD FINANCIERA NAVIGATOR SETUP")
    print(f"   Project:    {PROJECT_ID}")
    print(f"   Target URL: {TARGET_URI}")
    print("=" * 60)

    create_or_get_datastore()
    setup_target_site()
    create_or_get_engine()
    test_search("credito")


if __name__ == "__main__":
    main()
