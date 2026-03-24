import asyncio
import argparse
import datetime
import json
import os
from scraper import scrape_batch
from get_models import get_model_slugs
import bigquery_sync
# (config loaded strictly for generic hooks if required)
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

async def main():
    parser = argparse.ArgumentParser(description="OpenRouter Stats Tracker (BigQuery Only)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of models to scrape for testing")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrency level for Playwright page scraping")
    args = parser.parse_args()
    
    config = load_config()


    # 3. Get Models List
    if not os.path.exists("models.json"):
        model_ids = get_model_slugs()
    else:
        with open("models.json", 'r') as f:
            model_ids = json.load(f)
            
    if not model_ids:
        print("No models found. Exiting.")
        return
        
    # Create lookup map & simplify slug list variables for concurrency loops backwards compatibility
    models_lookup = {m["id"]: m for m in model_ids}
    slugs_list = [m["id"] for m in model_ids]

        
    if args.limit:
        print(f"Limiting execution to first {args.limit} models for testing...")
        slugs_list = slugs_list[:args.limit]

        
    # 4. Scrape & Append in Chunks
    chunk_size = 20
    print(f"Starting Scrape for {len(slugs_list)} models in chunks of {chunk_size}...")
    
    for i in range(0, len(slugs_list), chunk_size):
        chunk = slugs_list[i:i + chunk_size]
        print(f"\n[Chunk {i//chunk_size + 1}/{(len(slugs_list)-1)//chunk_size + 1}] Processing {len(chunk)} models...")

        
        results = await scrape_batch(chunk, concurrency=args.concurrency)
        if not results:
            continue
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = []
        enriched_results = []
        for item in results:
            meta = models_lookup.get(item["model_id"], {})
            
            # Enrich item dictionary for BigQuery insert loops
            item["name"] = meta.get("name")
            item["context_length"] = meta.get("context_length")
            item["pricing_prompt"] = meta.get("pricing_prompt")
            item["pricing_completion"] = meta.get("pricing_completion")
            item["modality"] = meta.get("modality")
            
            # Capability Matrix
            item["max_completion_tokens"] = meta.get("max_completion_tokens")
            item["supports_vision"] = meta.get("supports_vision")
            item["supports_tools"] = meta.get("supports_tools")
            item["supports_structured_output"] = meta.get("supports_structured_output")
            item["supports_reasoning"] = meta.get("supports_reasoning")
            
            enriched_results.append(item)
            
        # 4b. Sync to BigQuery for historical aggregation

        try:
            bigquery_sync.insert_rows(enriched_results)
        except Exception as e:
            print(f"BigQuery Sync Failed: {e}")



    print("Execution Finished Successfully.")

if __name__ == "__main__":
    asyncio.run(main())
