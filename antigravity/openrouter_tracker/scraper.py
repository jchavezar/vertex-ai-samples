import asyncio
import json
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_model_providers(page, model_id):
    url = f'https://openrouter.ai/{model_id}'
    print(f"[{model_id}] Navigating to {url}...")
    try:
        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
        try:
            # Wait up to 8s for Async Javascript Hydration to render the Latency indicators
            await page.wait_for_selector('div:has-text("Latency")', timeout=8000)
        except Exception:
            pass
        await page.wait_for_timeout(1000)
        
        # Click "Providers" tab
        try:
            await page.click("text='Providers'", timeout=5000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            # Maybe already on Providers or different view
            pass
            
        # Scroll slightly to trigger full load if lazy
        await page.evaluate("window.scrollBy(0, 500)")
        await page.wait_for_timeout(1000)
        
        # Get content
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        latency_nodes = soup.find_all(string="Latency")
        results = []
        
        for node in latency_nodes:
            # Traverse upwards to parent card/row
            curr = node
            for _ in range(5):
                if curr.parent:
                    curr = curr.parent
                else:
                    break
                    
            text = curr.get_text(separator="|").strip()
            parts = [p.strip() for p in text.split("|") if p.strip()]
            
            if not parts:
                continue
                
            provider = parts[0]
            
            # Extract latency, throughput, uptime
            latency = "--"
            throughput = "--"
            uptime = "--"
            
            for i, part in enumerate(parts):
                if part.lower() == "latency" and i + 1 < len(parts):
                    latency = parts[i+1]
                elif part.lower() == "throughput" and i + 1 < len(parts):
                    throughput = parts[i+1]
                elif part.lower() == "uptime" and i + 1 < len(parts):
                    # Usually looks like "Uptime" followed by "98.5%" or similar
                    if i + 1 < len(parts):
                         uptime = parts[i+1]
                         
            results.append({
                "model_id": model_id,
                "provider": provider,
                "latency": latency,
                "throughput": throughput,
                "uptime": uptime
            })
            
        print(f"[{model_id}] Found {len(results)} providers.")
        return results
        
    except Exception as e:
        print(f"[{model_id}] Error scraping: {e}")
        return []

async def scrape_batch(model_ids, concurrency=3):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Allocate pages based on concurrency
        # To avoid creating 349 pages at once, we use a semaphore
        semaphore = asyncio.Semaphore(concurrency)
        
        all_results = []
        
        async def sem_scrape(model_id):
            async with semaphore:
                # Use a fake context user-agent to bypass bot detection blocking.
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                res = await scrape_model_providers(page, model_id)
                await page.close()
                await context.close()
                all_results.extend(res)
                
        tasks = [sem_scrape(mid) for mid in model_ids]
        await asyncio.gather(*tasks)
        
        await browser.close()
        return all_results

if __name__ == "__main__":
    test_models = ["anthropic/claude-opus-4.6", "google/gemini-2.5-flash"]
    results = asyncio.run(scrape_batch(test_models))
    print("\nScrape Results:")
    print(json.dumps(results, indent=2))
