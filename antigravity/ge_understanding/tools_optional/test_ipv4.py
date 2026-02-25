import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("Connecting to 127.0.0.1:9222...")
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected!")
            page = await browser.new_page()
            await page.goto("http://localhost:5173/")
            print(f"Page title at 5173: {await page.title()}")
            await browser.close()
            print("Successfully verified frontend.")
        except Exception as e:
            print(f"Error connecting to 127.0.0.1:9222: {e}")

if __name__ == "__main__":
    asyncio.run(run())
