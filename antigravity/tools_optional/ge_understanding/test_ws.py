import asyncio
import requests
from playwright.async_api import async_playwright

async def run():
    try:
        resp = requests.get("http://127.0.0.1:9222/json/version")
        data = resp.json()
        ws_url = data['webSocketDebuggerUrl']
        print(f"WS URL: {ws_url}")
    except Exception as e:
        print(f"Failed to get WS URL via HTTP: {e}")
        return

    async with async_playwright() as p:
        print(f"Connecting to {ws_url}...")
        try:
            browser = await p.chromium.connect_over_cdp(ws_url)
            print("Connected!")
            page = await browser.new_page()
            await page.goto("http://localhost:5173/")
            print(f"Page title at 5173: {await page.title()}")
            await browser.close()
            print("Successfully verified frontend.")
        except Exception as e:
            print(f"Error connecting to WS URL: {e}")

if __name__ == "__main__":
    asyncio.run(run())
